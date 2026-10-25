//! Edge fillets for closed, consistently wound convex polyhedral surfaces.
//! Independent geometric construction; the legacy cuboid path retains its exact stencils.
use super::{Value, math::*, num, vec3};
use serde_json::json;
use std::collections::{BTreeMap, BTreeSet};

type EdgeUse = (usize, usize);

fn key(a: usize, b: usize) -> (usize, usize) {
    (a.min(b), a.max(b))
}

pub fn apply(mesh: &Value, modifier: &Value) -> Result<Value, String> {
    if modifier["affect"] == "VERTICES" {
        return Err(
            "General BEVEL supports affect=EDGES; vertex-only bevel requires a canonical cuboid"
                .into(),
        );
    }
    for field in [
        "loop_normals",
        "colors",
        "crease_vert",
        "crease_edge",
        "deform_weights",
        "shape_keys",
    ] {
        if mesh[field].as_array().is_some_and(|a| !a.is_empty()) {
            return Err(format!(
                "General BEVEL does not interpolate {field}; remove that attribute before beveling"
            ));
        }
    }
    let source: Vec<V3> = mesh["vertices"]
        .as_array()
        .ok_or("BEVEL needs vertices")?
        .iter()
        .map(vec3)
        .collect();
    let faces: Vec<Vec<usize>> = mesh["faces"]
        .as_array()
        .ok_or("BEVEL needs faces")?
        .iter()
        .map(|f| {
            f.as_array()
                .unwrap()
                .iter()
                .map(|v| v.as_u64().unwrap() as usize)
                .collect()
        })
        .collect();
    if faces.is_empty() {
        return Ok(mesh.clone());
    }
    let scale = source.iter().fold(
        ([f64::INFINITY; 3], [f64::NEG_INFINITY; 3]),
        |(mut lo, mut hi), p| {
            for i in 0..3 {
                lo[i] = lo[i].min(p[i]);
                hi[i] = hi[i].max(p[i]);
            }
            (lo, hi)
        },
    );
    let tolerance = length(sub(scale.1, scale.0)).max(1e-6) * 1e-7;
    let mut uses: BTreeMap<(usize, usize), Vec<EdgeUse>> = BTreeMap::new();
    let mut normals = Vec::new();
    let mut directions = Vec::new();
    let mut inward = Vec::new();
    let mut vertex_owner = vec![None; source.len()];
    for (fi, f) in faces.iter().enumerate() {
        for &v in f {
            vertex_owner[v].get_or_insert(fi);
        }
        let mut normal = [0.; 3];
        for i in 0..f.len() {
            normal = add(
                normal,
                cross(
                    sub(source[f[i]], source[f[0]]),
                    sub(source[f[(i + 1) % f.len()]], source[f[0]]),
                ),
            );
        }
        if length(normal) < tolerance * tolerance {
            return Err("General BEVEL requires non-degenerate faces".into());
        }
        normal = normalize(normal);
        if f.iter()
            .any(|&v| dot(sub(source[v], source[f[0]]), normal).abs() > tolerance)
        {
            return Err(
                "General BEVEL requires planar faces; triangulate non-planar polygons first".into(),
            );
        }
        let mut dirs = Vec::new();
        let mut ins = Vec::new();
        for i in 0..f.len() {
            let a = f[i];
            let b = f[(i + 1) % f.len()];
            let d = sub(source[b], source[a]);
            if length(d) < tolerance {
                return Err("General BEVEL requires nonzero edges".into());
            }
            let d = normalize(d);
            let n = cross(normal, d);
            if f.iter()
                .any(|&v| dot(sub(source[v], source[a]), n) < -tolerance)
            {
                return Err("General BEVEL requires convex face polygons; triangulate concave polygons first".into());
            }
            uses.entry(key(a, b)).or_default().push((fi, i));
            dirs.push(d);
            ins.push(n);
        }
        normals.push(normal);
        directions.push(dirs);
        inward.push(ins);
    }
    let mut selected = BTreeSet::new();
    for (&edge, pair) in &uses {
        if pair.len() != 2 {
            return Err(
                "General BEVEL requires a closed manifold surface (two faces per edge)".into(),
            );
        }
        let [(a, i), (b, j)] = [pair[0], pair[1]];
        if faces[a][i] != faces[b][(j + 1) % faces[b].len()] {
            return Err("General BEVEL requires consistent outward face winding".into());
        }
        let cosine = dot(normals[a], normals[b]).clamp(-1., 1.);
        if cosine < -0.999999 {
            return Err("General BEVEL rejects folded or zero-thickness edges".into());
        }
        if dot(normals[b], inward[a][i]) > 1e-6 {
            return Err("General BEVEL currently requires convex solids; concave edge junctions are unsupported".into());
        }
        if cosine < 1. - 1e-10
            && (modifier["limit_method"] != "ANGLE"
                || cosine.acos() + 1e-8 >= num(&modifier["angle_limit"]))
        {
            selected.insert(edge);
        }
    }
    if selected.is_empty() {
        return Ok(mesh.clone());
    }
    let mut selected_degree = vec![0; source.len()];
    for &(a, b) in &selected {
        selected_degree[a] += 1;
        selected_degree[b] += 1;
    }
    if mesh["edges"].as_array().into_iter().flatten().any(|edge| {
        !uses.contains_key(&key(
            edge[0].as_u64().unwrap() as usize,
            edge[1].as_u64().unwrap() as usize,
        ))
    }) {
        return Err("General BEVEL does not support loose edges".into());
    }
    if vertex_owner.iter().any(Option::is_none) {
        return Err("General BEVEL does not support loose vertices".into());
    }
    let segments = modifier["segments"].as_u64().unwrap_or(1) as usize;
    if faces.iter().map(Vec::len).sum::<usize>() * (segments + 2) > 200_000 {
        return Err("General BEVEL output budget exceeded; reduce segments or mesh density".into());
    }
    let mut offsets = Vec::new();
    let mut max_width = f64::INFINITY;
    for (fi, f) in faces.iter().enumerate() {
        let mut row = Vec::new();
        for i in 0..f.len() {
            let prev = (i + f.len() - 1) % f.len();
            let a = inward[fi][prev];
            let b = inward[fi][i];
            let c = dot(a, b);
            let det = 1. - c * c;
            let x = f64::from(selected.contains(&key(f[prev], f[i])));
            let y = f64::from(selected.contains(&key(f[i], f[(i + 1) % f.len()])));
            let offset = if det < 1e-12 {
                if c > 0. && x == y {
                    mul(a, x)
                } else {
                    return Err("General BEVEL cannot inset a reversing or inconsistently selected collinear corner".into());
                }
            } else {
                add(mul(a, (x - c * y) / det), mul(b, (y - c * x) / det))
            };
            row.push(offset);
            // Keep each inset corner inside all non-incident edge half-planes.
            for e in 0..f.len() {
                if e == i || e == prev {
                    continue;
                }
                let dist = dot(sub(source[f[i]], source[f[e]]), inward[fi][e]);
                let rate = dot(offset, inward[fi][e])
                    - f64::from(selected.contains(&key(f[e], f[(e + 1) % f.len()])));
                if rate < -1e-10 {
                    max_width = max_width.min(dist / -rate);
                }
            }
        }
        for i in 0..f.len() {
            let j = (i + 1) % f.len();
            let rate = dot(sub(row[j], row[i]), directions[fi][i]);
            if rate < -1e-10 {
                max_width = max_width.min(length(sub(source[f[j]], source[f[i]])) / -rate);
            }
        }
        offsets.push(row);
    }
    let mut width = num(&modifier["width"]);
    if width >= max_width * (1. - 1e-5) {
        if modifier["use_clamp_overlap"] != true {
            return Err(
                "General BEVEL overlaps faces; reduce width or set use_clamp_overlap=True".into(),
            );
        }
        width = max_width * 0.95;
    }
    if width <= tolerance {
        return Err("General BEVEL width is below this mesh's numerical tolerance".into());
    }
    let mut vertices = Vec::new();
    let mut corners = Vec::new();
    for (fi, f) in faces.iter().enumerate() {
        let mut row = Vec::new();
        for (i, &v) in f.iter().enumerate() {
            row.push(vertices.len());
            vertices.push(add(source[v], mul(offsets[fi][i], width)));
        }
        corners.push(row);
    }
    // Every polygon keeps a source-face owner for material and per-loop UV interpolation.
    let mut polygons: Vec<(Vec<usize>, usize, bool)> = corners
        .iter()
        .enumerate()
        .map(|(i, f)| (f.clone(), i, mesh["smooth"][i] == true))
        .collect();
    let mut boundaries: Vec<Vec<(usize, usize)>> = vec![Vec::new(); source.len()];
    for (&edge, pair) in &uses {
        let (fa, ia) = pair[0];
        let (fb, ib) = pair[1];
        let na = faces[fa].len();
        let nb = faces[fb].len();
        let a = faces[fa][ia];
        let b = faces[fa][(ia + 1) % na];
        let ends = [
            [corners[fa][ia], corners[fb][(ib + 1) % nb]],
            [corners[fa][(ia + 1) % na], corners[fb][ib]],
        ];
        let count = if selected.contains(&edge) {
            segments
        } else {
            1
        };
        let mut arcs = [Vec::new(), Vec::new()];
        let weight = ((1. + dot(normals[fa], normals[fb])) * 0.5).max(0.).sqrt();
        for endpoint in 0..2 {
            let [start, end] = ends[endpoint];
            let p = vertices[start];
            let q = vertices[end];
            let original = if endpoint == 0 { a } else { b };
            let origin = source[original];
            let d = directions[fa][ia];
            // A two-edge chain shares one corner profile across its unselected
            // seam (e.g. a cylinder rim). Projecting separately onto each edge
            // creates tiny wedges and highlight discontinuities at every seam.
            let control = if selected_degree[original] == 2 {
                origin
            } else {
                add(
                    origin,
                    mul(d, 0.5 * dot(sub(add(p, q), mul(origin, 2.)), d)),
                )
            };
            arcs[endpoint].push(start);
            for step in 1..count {
                let t = step as f64 / count as f64;
                let x = (1. - t) * (1. - t);
                let y = 2. * weight * t * (1. - t);
                let z = t * t;
                arcs[endpoint].push(vertices.len());
                vertices.push(mul(
                    add(add(mul(p, x), mul(control, y)), mul(q, z)),
                    1. / (x + y + z),
                ));
            }
            arcs[endpoint].push(end);
        }
        for i in 0..count {
            polygons.push((
                vec![arcs[1][i], arcs[0][i], arcs[0][i + 1], arcs[1][i + 1]],
                fa,
                true,
            ));
            boundaries[a].push((arcs[0][i + 1], arcs[0][i]));
            boundaries[b].push((arcs[1][i], arcs[1][i + 1]));
        }
    }
    // Weld only coincident corners belonging to the same original vertex. This preserves
    // disconnected touching components and does not merge distinct narrow bevel rings.
    let mut remap: Vec<usize> = (0..vertices.len()).collect();
    for boundary in &boundaries {
        let mut unique = Vec::<usize>::new();
        for &(a, b) in boundary {
            for v in [a, b] {
                if let Some(&same) = unique
                    .iter()
                    .find(|&&other| length(sub(vertices[v], vertices[other])) < tolerance)
                {
                    remap[v] = same;
                } else {
                    unique.push(v);
                }
            }
        }
    }
    for (original, boundary) in boundaries.iter().enumerate() {
        let mut open_edges = BTreeSet::new();
        for &(a, b) in boundary {
            let (a, b) = (remap[a], remap[b]);
            if a != b && !open_edges.remove(&(b, a)) {
                open_edges.insert((a, b));
            }
        }
        let links: BTreeMap<usize, usize> = open_edges.iter().copied().collect();
        if links.len() != open_edges.len() {
            return Err("General BEVEL encountered a branching corner junction".into());
        }
        if links.is_empty() {
            continue;
        }
        let first = *links.keys().next().unwrap();
        let mut ring = vec![first];
        let mut next = *links.get(&first).unwrap();
        while next != first && ring.len() <= links.len() {
            ring.push(next);
            next = *links
                .get(&next)
                .ok_or("General BEVEL encountered an open corner junction")?;
        }
        if ring.len() != links.len() {
            return Err("General BEVEL requires one connected face fan per vertex".into());
        }
        if ring.len() < 3 {
            continue;
        }
        let owner = vertex_owner[original].unwrap();
        if ring.len() == 3 {
            polygons.push((ring, owner, true));
        } else {
            let center = mul(
                ring.iter().fold([0.; 3], |s, &v| add(s, vertices[v])),
                1. / ring.len() as f64,
            );
            let ci = vertices.len();
            vertices.push(center);
            remap.push(ci);
            for i in 0..ring.len() {
                polygons.push((vec![ring[i], ring[(i + 1) % ring.len()], ci], owner, true));
            }
        }
    }
    let mut out_faces = Vec::new();
    let mut owners = Vec::new();
    let mut smooth = Vec::new();
    for (polygon, owner, shade) in polygons {
        let mut f = Vec::new();
        for v in polygon {
            let v = remap[v];
            if f.last() != Some(&v) {
                f.push(v);
            }
        }
        if f.first() == f.last() {
            f.pop();
        }
        if f.len() < 3 {
            continue;
        }
        if f.iter().copied().collect::<BTreeSet<_>>().len() != f.len() {
            return Err("General BEVEL produced a collapsed corner; reduce width".into());
        }
        out_faces.push(f);
        owners.push(owner);
        smooth.push(shade);
    }
    let used: BTreeSet<usize> = out_faces.iter().flatten().copied().collect();
    let compact: BTreeMap<usize, usize> = used.iter().enumerate().map(|(i, &v)| (v, i)).collect();
    let output_vertices: Vec<V3> = used
        .iter()
        .map(|&v| vertices[v].map(|x| x as f32 as f64))
        .collect();
    for f in &mut out_faces {
        for v in f {
            *v = compact[v];
        }
    }
    let mut edge_counts = BTreeMap::<(usize, usize), i32>::new();
    let mut edge_uses = BTreeMap::<(usize, usize), usize>::new();
    for f in &out_faces {
        for i in 0..f.len() {
            let a = f[i];
            let b = f[(i + 1) % f.len()];
            *edge_counts.entry(key(a, b)).or_default() += if a < b { 1 } else { -1 };
            *edge_uses.entry(key(a, b)).or_default() += 1;
        }
    }
    if edge_counts.values().any(|&n| n != 0) || edge_uses.values().any(|&n| n != 2) {
        return Err("General BEVEL output failed closed-manifold validation".into());
    }
    let mut result = mesh.clone();
    result["vertices"] = json!(output_vertices);
    result["faces"] = json!(out_faces);
    result["edges"] = json!(edge_uses.keys().map(|&(a, b)| [a, b]).collect::<Vec<_>>());
    result["material_indices"] = json!(
        owners
            .iter()
            .map(|&i| mesh["material_indices"][i].clone())
            .collect::<Vec<_>>()
    );
    result["smooth"] = json!(smooth);
    // Project each new corner onto the owning original convex face and interpolate
    // its original fan triangles. UV seams remain separate per face, never averaged.
    let starts: Vec<usize> = faces
        .iter()
        .scan(0, |n, f| {
            let s = *n;
            *n += f.len();
            Some(s)
        })
        .collect();
    let mut layers = Vec::new();
    for layer in mesh["uv_layers"].as_array().into_iter().flatten() {
        let mut data = Vec::new();
        for (fi, f) in out_faces.iter().enumerate() {
            let owner = owners[fi];
            let original = &faces[owner];
            for &v in f {
                let p = output_vertices[v];
                let a = source[original[0]];
                let mut best = (f64::NEG_INFINITY, [0.; 2]);
                for i in 1..original.len() - 1 {
                    let u = sub(source[original[i]], a);
                    let w = sub(source[original[i + 1]], a);
                    let d = sub(p, a);
                    let uu = dot(u, u);
                    let ww = dot(w, w);
                    let uw = dot(u, w);
                    let den = uu * ww - uw * uw;
                    if den <= 1e-24 {
                        continue;
                    }
                    let b = (dot(d, u) * ww - dot(d, w) * uw) / den;
                    let c = (dot(d, w) * uu - dot(d, u) * uw) / den;
                    let weights = [1. - b - c, b, c];
                    let score = weights.iter().copied().fold(f64::INFINITY, f64::min);
                    if score > best.0 {
                        let at = [0, i, i + 1];
                        let uv = std::array::from_fn(|axis| {
                            (0..3)
                                .map(|j| {
                                    weights[j] * num(&layer["data"][starts[owner] + at[j]][axis])
                                })
                                .sum()
                        });
                        best = (score, uv);
                    }
                }
                data.push(best.1);
            }
        }
        let mut layer = layer.clone();
        layer["data"] = json!(data);
        layers.push(layer);
    }
    result["uv_layers"] = json!(layers);
    for field in ["face_strength", "sharp_edges"] {
        result.as_object_mut().unwrap().remove(field);
    }
    Ok(result)
}
