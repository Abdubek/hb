//! Greedy distance welding and edge-connected cluster collapse.
use super::{Value, groups, num, topology, vec3};
use serde_json::json;
use std::collections::{BTreeMap, BTreeSet};

fn root(parents: &mut [usize], mut i: usize) -> usize {
    while parents[i] != i {
        parents[i] = parents[parents[i]];
        i = parents[i];
    }
    i
}
fn squared(a: [f32; 3], b: [f32; 3]) -> f32 {
    let d: [f32; 3] = std::array::from_fn(|k| a[k] - b[k]);
    (d[0] * d[0] + d[1] * d[1]) + d[2] * d[2]
}
// Same spatial partition as the independently implemented BMesh merge kernel,
// with original-index seed order for the modifier's deterministic representatives.
fn balance(order: &mut [usize], points: &[[f32; 3]], axes: &mut [usize], axis: usize) {
    if order.len() < 2 {
        return;
    }
    let middle = order.len() / 2;
    let (mut low, mut high) = (0, order.len() - 1);
    while low < high {
        let pivot = points[order[high]][axis];
        let (mut a, mut b) = (low, high - 1);
        loop {
            while points[order[a]][axis] < pivot {
                a += 1;
            }
            while b > low && points[order[b]][axis] > pivot {
                b -= 1;
            }
            if a >= b {
                break;
            }
            order.swap(a, b);
            a += 1;
            b -= 1;
        }
        order.swap(a, high);
        if a >= middle {
            if a == 0 {
                break;
            }
            high = a - 1;
        }
        if a <= middle {
            low = a + 1;
        }
    }
    axes[middle] = axis;
    balance(
        &mut order[..middle],
        points,
        &mut axes[..middle],
        (axis + 1) % 3,
    );
    balance(
        &mut order[middle + 1..],
        points,
        &mut axes[middle + 1..],
        (axis + 1) % 3,
    );
}
fn all_targets(
    points: &[[f32; 3]],
    selected: &[bool],
    distance: f32,
) -> Result<Vec<usize>, String> {
    let mut order: Vec<_> = (0..points.len()).filter(|&i| selected[i]).collect();
    let mut axes = vec![0; order.len()];
    balance(&mut order, points, &mut axes, 0);
    let mut targets: Vec<_> = (0..points.len()).collect();
    let mut claimed = vec![false; points.len()];
    let mut checks = 0;
    for seed in 0..points.len() {
        if !selected[seed] || targets[seed] != seed {
            continue;
        }
        let mut stack = vec![(0, order.len())];
        let mut found = false;
        while let Some((start, stop)) = stack.pop() {
            if start == stop {
                continue;
            }
            checks += 1;
            if checks > 2_000_000 {
                return Err("WELD exceeds 2,000,000 proximity checks; split dense geometry".into());
            }
            let middle = (start + stop) / 2;
            let index = order[middle];
            let axis = axes[middle];
            if points[seed][axis] + distance <= points[index][axis] {
                stack.push((start, middle));
                continue;
            }
            if points[seed][axis] - distance >= points[index][axis] {
                stack.push((middle + 1, stop));
                continue;
            }
            if index != seed
                && !claimed[index]
                && squared(points[seed], points[index]) <= distance * distance
            {
                targets[index] = seed;
                claimed[index] = true;
                found = true;
            }
            stack.push((middle + 1, stop));
            stack.push((start, middle));
        }
        if found {
            claimed[seed] = true;
        }
    }
    Ok(targets)
}
fn pair(a: usize, b: usize) -> (usize, usize) {
    (a.min(b), a.max(b))
}

pub fn apply(object: &Value, mesh: &Value, modifier: &Value) -> Result<Value, String> {
    let input = mesh["vertices"].as_array().ok_or("Invalid mesh vertices")?;
    let source = topology::faces(mesh);
    if input.len() > 2_000_000
        || source.len() > 2_000_000
        || source.iter().map(Vec::len).sum::<usize>() > 4_000_000
    {
        return Err("WELD exceeds 2,000,000 vertices/faces or 4,000,000 corners".into());
    }
    let distance = num(&modifier["merge_threshold"]) as f32;
    if !(distance * distance).is_finite() {
        return Err("WELD threshold is too large for finite float32 distance testing".into());
    }
    let connected = modifier["mode"] == "CONNECTED";
    if input.is_empty() || !connected && distance == 0. {
        return Ok(mesh.clone());
    }
    let positions: Vec<[f32; 3]> = input.iter().map(|v| vec3(v).map(|x| x as f32)).collect();
    let weights = groups::weights(mesh);
    let group = object
        .get("vertex_groups")
        .and_then(Value::as_array)
        .and_then(|gs| {
            gs.iter()
                .position(|g| g["name"] == modifier["vertex_group"])
        });
    let selected: Vec<_> = (0..input.len())
        .map(|i| {
            group.is_none_or(|g| {
                let value = weights[i]
                    .iter()
                    .find(|(k, _)| *k == g)
                    .map(|(_, w)| *w)
                    .unwrap_or(0.);
                if modifier["invert_vertex_group"] == true {
                    value <= 0.
                } else {
                    value > 0.
                }
            })
        })
        .collect();
    let mut targets = if connected {
        (0..input.len()).collect()
    } else {
        all_targets(&positions, &selected, distance)?
    };
    if connected {
        let mut boundary = BTreeSet::new();
        for f in &source {
            for i in 0..f.len() {
                boundary.insert(pair(f[i], f[(i + 1) % f.len()]));
            }
        }
        let mut edge_order = vec![];
        let mut visited = BTreeSet::new();
        // Preserve loose-wire order; surface edges use closing-corner-first
        // allocation, matching from_pydata's face construction order.
        for edge in mesh["edges"].as_array().unwrap() {
            let e = pair(
                edge[0].as_u64().unwrap() as usize,
                edge[1].as_u64().unwrap() as usize,
            );
            if !boundary.contains(&e) && visited.insert(e) {
                edge_order.push(e);
            }
        }
        if modifier["loose_edges"] != true {
            for f in &source {
                for i in 0..f.len() {
                    let e = pair(f[(i + f.len() - 1) % f.len()], f[i]);
                    if visited.insert(e) {
                        edge_order.push(e);
                    }
                }
            }
        }
        let mut centers = positions.clone();
        let mut sizes = vec![1usize; input.len()];
        for (a, b) in edge_order {
            let (a, b) = pair(root(&mut targets, a), root(&mut targets, b));
            if a == b || !selected[a] || !selected[b] {
                continue;
            }
            if squared(centers[a], centers[b]) <= distance * distance {
                let influence = sizes[b] as f32 / (sizes[a] + sizes[b]) as f32;
                let other = centers[b];
                for (value, other) in centers[a].iter_mut().zip(other) {
                    *value += (other - *value) * influence;
                }
                sizes[a] += sizes[b];
                targets[b] = a;
            }
        }
        for i in 0..targets.len() {
            targets[i] = root(&mut targets, i);
        }
    }
    if targets.iter().enumerate().all(|(i, &t)| i == t) {
        return Ok(mesh.clone());
    }
    if !mesh["loop_normals"].as_array().unwrap().is_empty()
        || !mesh["colors"].as_array().unwrap().is_empty()
    {
        return Err("WELD custom corner normals/colors are outside the named welding subset; use ordinary normals and UV layers".into());
    }
    let mut members = vec![vec![]; input.len()];
    for (i, &target) in targets.iter().enumerate() {
        members[target].push(i);
    }
    let mut remap = vec![0; input.len()];
    let mut vertices = vec![];
    let mut merged_weights = vec![];
    for list in members.iter().filter(|m| !m.is_empty()) {
        if list.len() > 65536 {
            return Err("WELD exceeds 65,536 vertices in one cluster".into());
        }
        let factor = 1. / list.len() as f32;
        let mut p = [0f32; 3];
        let mut row: Vec<(usize, f32)> = vec![];
        for &i in list {
            remap[i] = vertices.len();
            for k in 0..3 {
                p[k] += positions[i][k] * factor;
            }
            for &(g, w) in &weights[i] {
                if let Some((_, v)) = row.iter_mut().find(|(k, _)| *k == g) {
                    *v += w * factor;
                } else {
                    row.push((g, w * factor));
                }
            }
        }
        if list.len() > 1 {
            row.retain(|(_, w)| *w > 0.);
        }
        vertices.push(json!(p));
        merged_weights.push(row);
    }
    // Collapse consecutive corners, interpolate their UVs, and split pinched
    // polygons into simple cycles without inventing edges or reversing winding.
    let starts = topology::starts(&source);
    let mut faces = vec![];
    let mut corner_groups = vec![];
    let mut extra_faces = vec![];
    let mut extra_corners = vec![];
    let mut known = BTreeSet::new();
    for (fi, face) in source.iter().enumerate() {
        let mut runs: Vec<(usize, Vec<usize>)> = vec![];
        for (j, &v) in face.iter().enumerate() {
            let v = remap[v];
            if let Some((last, corners)) = runs.last_mut()
                && *last == v
            {
                corners.push(starts[fi] + j);
                continue;
            }
            runs.push((v, vec![starts[fi] + j]));
        }
        if runs.len() > 1 && runs[0].0 == runs.last().unwrap().0 {
            let last = runs.pop().unwrap();
            runs[0].1.extend(last.1);
        }
        let mut path: Vec<(usize, Vec<usize>)> = vec![];
        let mut seen = BTreeMap::new();
        let mut cycles = vec![];
        if !runs.is_empty() {
            runs.push(runs[0].clone());
        }
        for entry in runs {
            if let Some(&at) = seen.get(&entry.0) {
                let cycle = path[at..].to_vec();
                if cycle.len() >= 3 {
                    cycles.push(cycle);
                }
                path.truncate(at + 1);
                seen = path.iter().enumerate().map(|(i, e)| (e.0, i)).collect();
            } else {
                seen.insert(entry.0, path.len());
                path.push(entry);
            }
        }
        let mut merged_corners: BTreeMap<usize, Vec<usize>> = BTreeMap::new();
        for (j, &v) in face.iter().enumerate() {
            merged_corners
                .entry(remap[v])
                .or_default()
                .push(starts[fi] + j);
        }
        if !cycles.is_empty() {
            cycles.rotate_right(1);
        }
        for (cycle_index, cycle) in cycles.into_iter().enumerate() {
            let set: BTreeSet<_> = cycle.iter().map(|e| e.0).collect();
            if !known.insert(set) {
                continue;
            }
            let record = topology::Face {
                vertices: cycle.iter().map(|e| e.0).collect(),
                corners: cycle.iter().map(|e| e.1[0]).collect(),
                source: fi,
                material: None,
            };
            let corners = cycle.into_iter().map(|e| merged_corners[&e.0].clone());
            if cycle_index == 0 {
                faces.push(record);
                corner_groups.extend(corners);
            } else {
                extra_faces.push(record);
                extra_corners.extend(corners);
            }
        }
    }
    faces.extend(extra_faces);
    corner_groups.extend(extra_corners);
    let edges = mesh["edges"]
        .as_array()
        .unwrap()
        .iter()
        .map(|e| {
            json!([
                remap[e[0].as_u64().unwrap() as usize],
                remap[e[1].as_u64().unwrap() as usize]
            ])
        })
        .collect();
    let mut out = topology::assemble(mesh, vertices, &faces, edges)?;
    for (index, layer) in out["uv_layers"]
        .as_array_mut()
        .unwrap()
        .iter_mut()
        .enumerate()
    {
        let old = &mesh["uv_layers"][index]["data"];
        layer["data"] = json!(
            corner_groups
                .iter()
                .map(|corners| {
                    let mut uv = [0f32; 2];
                    let factor = 1. / corners.len() as f32;
                    for &i in corners {
                        for (k, v) in uv.iter_mut().enumerate() {
                            *v += num(&old[i][k]) as f32 * factor;
                        }
                    }
                    uv
                })
                .collect::<Vec<_>>()
        );
    }
    groups::store(&mut out, &merged_weights);
    Ok(out)
}
