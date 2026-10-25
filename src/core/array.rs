//! Contextual fixed-count arrays: affine offsets, seam welding and mesh caps.
use super::{
    Scene, Value, f32_value, id,
    math::{self, M4, V3},
    num, text, vec3,
};
use serde_json::json;
use std::{
    borrow::Cow,
    collections::{BTreeSet, HashMap},
    ops::Range,
};
fn multiply(a: M4, b: M4) -> M4 {
    std::array::from_fn(|i| {
        std::array::from_fn(|j| (0..4).map(|k| a[i][k] as f32 * b[k][j] as f32).sum::<f32>() as f64)
    })
}
fn root(map: &[usize], mut i: usize) -> usize {
    while map[i] != i {
        i = map[i];
    }
    i
}
fn merge(
    vertices: &[V3],
    map: &mut [usize],
    source: Range<usize>,
    target: Range<usize>,
    distance: f64,
    checks: &mut usize,
) -> Result<(), String> {
    if source.is_empty() || target.is_empty() {
        return Ok(());
    }
    let cell = |p: V3| -> Result<[i64; 3], String> {
        if distance == 0. {
            return Ok(p.map(|v| {
                if v == 0. {
                    0
                } else {
                    (v as f32).to_bits() as i64
                }
            }));
        }
        let v = p.map(|v| (v / distance).floor());
        if v.iter().any(|v| !v.is_finite() || v.abs() > 9e18) {
            return Err("ARRAY merge threshold is too small for these coordinates".into());
        }
        Ok(v.map(|v| v as i64))
    };
    let mut buckets: HashMap<[i64; 3], Vec<usize>> = HashMap::new();
    for i in target {
        buckets.entry(cell(vertices[i])?).or_default().push(i);
    }
    let radius = if distance == 0. { 0 } else { 1 };
    for i in source {
        let c = cell(vertices[i])?;
        let mut best: Option<(f64, usize)> = None;
        for x in -radius..=radius {
            for y in -radius..=radius {
                for z in -radius..=radius {
                    if let Some(candidates) = buckets.get(&[c[0] + x, c[1] + y, c[2] + z]) {
                        for &j in candidates {
                            *checks += 1;
                            if *checks > 2_000_000 {
                                return Err("ARRAY exceeds 2,000,000 merge proximity checks".into());
                            }
                            let d = math::sub(vertices[i], vertices[j]);
                            let squared = math::dot(d, d);
                            if squared <= distance * distance
                                && best.is_none_or(|b| (squared, j) < b)
                            {
                                best = Some((squared, j));
                            }
                        }
                    }
                }
            }
        }
        if let Some((_, j)) = best {
            let a = root(map, i);
            let b = root(map, j);
            if a != b {
                map[a] = b;
            }
        }
    }
    Ok(())
}
pub fn apply(
    scene: &Scene,
    object: &Value,
    mesh: &Value,
    m: &Value,
    render: bool,
    visited: &mut Vec<u64>,
) -> Result<Value, String> {
    if m["use_object_offset"] != true
        && m["use_merge_vertices"] != true
        && m["start_cap"].is_null()
        && m["end_cap"].is_null()
    {
        return super::modeling::array(mesh, m);
    }
    let count = m["count"].as_u64().unwrap() as usize;
    let source = mesh["vertices"]
        .as_array()
        .ok_or("Invalid ARRAY vertices")?;
    let mut lo = [f64::INFINITY; 3];
    let mut hi = [f64::NEG_INFINITY; 3];
    for p in source {
        let p = vec3(p);
        for k in 0..3 {
            lo[k] = lo[k].min(p[k]);
            hi[k] = hi[k].max(p[k]);
        }
    }
    let step: [f64; 3] = std::array::from_fn(|k| {
        let relative = if m["use_relative_offset"] == true && !source.is_empty() {
            (hi[k] - lo[k]) as f32 * num(&m["relative_offset_displace"][k]) as f32
        } else {
            0.
        };
        (relative
            + if m["use_constant_offset"] == true {
                num(&m["constant_offset_displace"][k]) as f32
            } else {
                0.
            }) as f64
    });
    let mut delta = math::IDENTITY;
    if m["use_object_offset"] == true
        && let Some(key) = m["offset_object"].as_u64()
    {
        delta = multiply(math::inverse(scene.world(id(object))?)?, scene.world(key)?);
    }
    for k in 0..3 {
        delta[k][3] = (delta[k][3] as f32 + step[k] as f32) as f64;
    }
    if source.len().saturating_mul(count) > 2_000_000
        || mesh["faces"]
            .as_array()
            .unwrap()
            .len()
            .saturating_mul(count)
            > 2_000_000
    {
        return Err("Evaluated ARRAY exceeds the 2,000,000 vertex/face resource limit".into());
    }
    let mut parts = vec![];
    let mut transform = math::IDENTITY;
    for _ in 0..count {
        parts.push((Cow::Borrowed(mesh), transform, false));
        transform = multiply(delta, transform);
    }
    for (field, matrix) in [
        ("start_cap", math::inverse(delta)),
        ("end_cap", Ok(transform)),
    ] {
        if let Some(key) = m[field].as_u64() {
            if key == id(object) {
                return Err("ARRAY cap must be a different mesh object".into());
            }
            let cap = super::modeling::evaluate(scene, scene.object(key)?, render, visited)?
                .ok_or("ARRAY cap must be a mesh")?
                .into_owned();
            parts.push((Cow::Owned(cap), matrix?, field == "start_cap"));
        }
    }
    let nvertices: usize = parts
        .iter()
        .map(|(p, _, _)| p["vertices"].as_array().unwrap().len())
        .sum();
    let nfaces: usize = parts
        .iter()
        .map(|(p, _, _)| p["faces"].as_array().unwrap().len())
        .sum();
    if nvertices > 2_000_000 || nfaces > 2_000_000 {
        return Err("Evaluated ARRAY exceeds the 2,000,000 vertex/face resource limit".into());
    }
    let mut vertices = Vec::with_capacity(nvertices);
    let mut deform_weights = vec![];
    let mut edges = vec![];
    let mut faces = vec![];
    let mut materials = vec![];
    let mut smooth = vec![];
    let mut normals = vec![];
    let mut colors = vec![];
    let has_normals = !mesh["loop_normals"].as_array().unwrap().is_empty();
    let has_colors = !mesh["colors"].as_array().unwrap().is_empty();
    let layers = mesh["uv_layers"].as_array().unwrap();
    let mut uv: Vec<Vec<Value>> = vec![vec![]; layers.len()];
    let mut ranges = vec![];
    for (part_index, (part, matrix, _)) in parts.iter().enumerate() {
        let start = vertices.len();
        if part_index >= count && part.get("deform_weights").is_some() {
            return Err("ARRAY cap deform groups are unsupported; apply the array before assigning cap weights".into());
        }
        deform_weights.extend(super::groups::weights(part));
        let vs: Vec<_> = part["vertices"]
            .as_array()
            .unwrap()
            .iter()
            .map(vec3)
            .collect();
        for p in &vs {
            vertices.push(math::point(*matrix, *p).map(|v| v as f32 as f64));
        }
        ranges.push(start..vertices.len());
        for e in part["edges"].as_array().unwrap() {
            edges.push([
                start + e[0].as_u64().unwrap() as usize,
                start + e[1].as_u64().unwrap() as usize,
            ]);
        }
        let mut corner = 0;
        for (face_index, face) in part["faces"].as_array().unwrap().iter().enumerate() {
            let indices: Vec<_> = face
                .as_array()
                .unwrap()
                .iter()
                .map(|i| i.as_u64().unwrap() as usize)
                .collect();
            faces.push(indices.iter().map(|i| start + i).collect::<Vec<_>>());
            let slot = part["material_indices"][face_index].as_u64().unwrap_or(0);
            materials.push(if part_index < count {
                slot
            } else {
                slot.min(
                    mesh["materials"]
                        .as_array()
                        .unwrap()
                        .len()
                        .saturating_sub(1) as u64,
                )
            });
            smooth.push(part["smooth"][face_index].as_bool().unwrap_or(false));
            let geometric =
                super::geometry::face_normal(&indices.iter().map(|&i| vs[i]).collect::<Vec<_>>());
            for _ in &indices {
                if has_normals {
                    let n = part["loop_normals"]
                        .as_array()
                        .unwrap()
                        .get(corner)
                        .map(vec3)
                        .unwrap_or(geometric);
                    normals.push(json!(math::normal(*matrix, n)));
                }
                if has_colors {
                    colors.push(
                        part["colors"]
                            .as_array()
                            .unwrap()
                            .get(corner)
                            .cloned()
                            .unwrap_or(json!([1., 1., 1., 1.])),
                    );
                }
                for (layer, data) in layers.iter().zip(&mut uv) {
                    let value = part["uv_layers"]
                        .as_array()
                        .unwrap()
                        .iter()
                        .find(|l| l["name"] == layer["name"])
                        .and_then(|l| l["data"].get(corner))
                        .cloned()
                        .unwrap_or(json!([0., 0.]));
                    data.push(value);
                }
                corner += 1;
            }
        }
    }
    let mut map: Vec<_> = (0..vertices.len()).collect();
    if m["use_merge_vertices"] == true {
        let distance = m.get("merge_threshold").map(num).unwrap_or(0.01_f32 as f64);
        let mut checks = 0;
        for i in 1..count {
            merge(
                &vertices,
                &mut map,
                ranges[i].clone(),
                ranges[i - 1].clone(),
                distance,
                &mut checks,
            )?;
        }
        if m["use_merge_vertices_cap"] == true && count > 1 {
            merge(
                &vertices,
                &mut map,
                ranges[0].clone(),
                ranges[count - 1].clone(),
                distance,
                &mut checks,
            )?;
        }
        for i in count..parts.len() {
            let target = if parts[i].2 { 0 } else { count - 1 };
            merge(
                &vertices,
                &mut map,
                ranges[i].clone(),
                ranges[target].clone(),
                distance,
                &mut checks,
            )?;
        }
    }
    let mut compact = vec![];
    let mut remap = vec![0; vertices.len()];
    for (i, p) in vertices.iter().enumerate() {
        if map[i] == i {
            remap[i] = compact.len();
            compact.push(*p);
        }
    }
    for i in 0..vertices.len() {
        remap[i] = remap[root(&map, i)];
    }
    let changed = map.iter().enumerate().any(|(i, &v)| i != v);
    let mut output_faces = vec![];
    let mut kept_faces = vec![];
    let mut kept_corners = vec![];
    let mut known = BTreeSet::new();
    let mut corner = 0;
    for (fi, face) in faces.iter().enumerate() {
        if !changed {
            output_faces.push(face.iter().map(|&i| remap[i]).collect());
            kept_faces.push(fi);
            kept_corners.extend(corner..corner + face.len());
            corner += face.len();
            continue;
        }
        let mut mapped = vec![];
        let mut corners = vec![];
        for (ci, &v) in face.iter().enumerate() {
            let v = remap[v];
            if mapped.last() != Some(&v) {
                mapped.push(v);
                corners.push(corner + ci);
            }
        }
        if mapped.len() > 1 && mapped.first() == mapped.last() {
            mapped.pop();
            corners.pop();
        }
        corner += face.len();
        let unique: BTreeSet<_> = mapped.iter().copied().collect();
        if unique.len() < 3 {
            continue;
        }
        if unique.len() != mapped.len() {
            return Err("ARRAY seam merge creates a repeated nonadjacent face corner; reduce merge_threshold".into());
        }
        if known.insert(unique) {
            output_faces.push(mapped);
            kept_faces.push(fi);
            kept_corners.extend(corners);
        }
    }
    let mut output_edges = vec![];
    let mut known = BTreeSet::new();
    for [a, b] in edges {
        let a = remap[a];
        let b = remap[b];
        if a != b && known.insert((a.min(b), a.max(b))) {
            output_edges.push([a, b]);
        }
    }
    let mut out = mesh.clone();
    out["vertices"] = json!(compact);
    out["faces"] = json!(output_faces);
    out["edges"] = json!(output_edges);
    out["material_indices"] = json!(kept_faces.iter().map(|&i| materials[i]).collect::<Vec<_>>());
    out["smooth"] = json!(kept_faces.iter().map(|&i| smooth[i]).collect::<Vec<_>>());
    if has_normals {
        out["loop_normals"] = json!(
            kept_corners
                .iter()
                .map(|&i| normals[i].clone())
                .collect::<Vec<_>>()
        );
    }
    if has_colors {
        out["colors"] = json!(
            kept_corners
                .iter()
                .map(|&i| colors[i].clone())
                .collect::<Vec<_>>()
        );
    }
    out["uv_layers"]=json!(layers.iter().zip(uv).map(|(layer,data)|json!({"name":text(&layer["name"]),"data":kept_corners.iter().map(|&i|data[i].clone()).collect::<Vec<_>>()})).collect::<Vec<_>>());
    let weights: Vec<_> = deform_weights
        .into_iter()
        .enumerate()
        .filter(|(i, _)| map[*i] == *i)
        .map(|(_, w)| w)
        .collect();
    super::groups::store(&mut out, &weights);
    out["vertices"] = f32_value(&out["vertices"])?;
    out["loop_normals"] = f32_value(&out["loop_normals"])?;
    Ok(out)
}
