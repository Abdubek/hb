//! Bounded shell construction: weighted extrusion and radial non-manifold fans.
use super::topology::{Face, assemble, faces, starts};
use super::{
    Value, groups,
    math::{add, cross, dot, length, mul, normalize, sub},
    num, text, vec3,
};
use serde_json::json;
use std::collections::{BTreeMap, BTreeSet};
type Edge = (usize, usize);
type Incidence = (usize, usize, usize);
fn group(object: &Value, name: &Value) -> Option<usize> {
    let name = name.as_str().unwrap_or("");
    if name.is_empty() {
        return None;
    }
    object
        .get("vertex_groups")?
        .as_array()?
        .iter()
        .position(|g| g["name"] == name)
}
fn weight(row: &[(usize, f32)], index: usize) -> f64 {
    row.iter()
        .find(|(i, _)| *i == index)
        .map_or(0., |(_, w)| *w as f64)
}
fn assign(row: &mut Vec<(usize, f32)>, index: Option<usize>) {
    if let Some(index) = index {
        if let Some((_, w)) = row.iter_mut().find(|(i, _)| *i == index) {
            *w = 1.;
        } else {
            row.push((index, 1.));
        }
    }
}
struct Surface {
    positions: Vec<[f64; 3]>,
    faces: Vec<Vec<usize>>,
    normals: Vec<[f64; 3]>,
    angles: Vec<Vec<f64>>,
    edges: BTreeMap<Edge, Vec<Incidence>>,
    shortest: Vec<f64>,
}
impl Surface {
    fn new(mesh: &Value) -> Result<Self, String> {
        let positions: Vec<_> = mesh["vertices"]
            .as_array()
            .unwrap()
            .iter()
            .map(vec3)
            .collect();
        let faces = faces(mesh);
        let mut normals = vec![];
        let mut angles = vec![];
        let mut edges: BTreeMap<Edge, Vec<Incidence>> = BTreeMap::new();
        let mut shortest = vec![f64::INFINITY; positions.len()];
        for (fi, f) in faces.iter().enumerate() {
            let mut normal = [0.; 3];
            let mut fa = vec![];
            for j in 0..f.len() {
                normal = add(
                    normal,
                    cross(positions[f[j]], positions[f[(j + 1) % f.len()]]),
                );
            }
            if length(normal) < 1e-12 {
                return Err("SOLIDIFY requires non-degenerate planar faces".into());
            }
            normal = normalize(normal);
            for j in 0..f.len() {
                let a = f[j];
                let b = f[(j + 1) % f.len()];
                let previous = f[(j + f.len() - 1) % f.len()];
                let len = length(sub(positions[b], positions[a]));
                if len < 1e-12 {
                    return Err("SOLIDIFY requires nonzero face edges".into());
                }
                if dot(normal, sub(positions[a], positions[f[0]])).abs() > 1e-5 {
                    return Err(
                        "SOLIDIFY extensions require planar faces; triangulate the input".into(),
                    );
                }
                shortest[a] = shortest[a].min(len);
                shortest[b] = shortest[b].min(len);
                fa.push(
                    dot(
                        normalize(sub(positions[previous], positions[a])),
                        normalize(sub(positions[b], positions[a])),
                    )
                    .clamp(-1., 1.)
                    .acos(),
                );
                edges
                    .entry((a.min(b), a.max(b)))
                    .or_default()
                    .push((fi, a, b));
            }
            normals.push(normal);
            angles.push(fa);
        }
        Ok(Self {
            positions,
            faces,
            normals,
            angles,
            edges,
            shortest,
        })
    }
}
fn factors(surface: &Surface, object: &Value, mesh: &Value, modifier: &Value) -> Vec<f64> {
    let rows = groups::weights(mesh);
    let index = group(object, &modifier["vertex_group"]);
    let minimum = modifier["thickness_vertex_group"].as_f64().unwrap_or(0.) as f32;
    let clamp = num(&modifier["thickness"]).abs() * num(&modifier["thickness_clamp"]);
    (0..surface.positions.len())
        .map(|i| {
            let w = index.map_or(1., |index| {
                let w = weight(&rows[i], index) as f32;
                let w = if modifier["invert_vertex_group"] == true {
                    1. - w
                } else {
                    w
                };
                (minimum + w * (1. - minimum)) as f64
            });
            w * if clamp > f32::EPSILON as f64 {
                (surface.shortest[i] / clamp).min(1.)
            } else {
                1.
            }
        })
        .collect()
}
pub fn apply(object: &Value, mesh: &Value, modifier: &Value) -> Result<Value, String> {
    let extra = modifier["solidify_mode"] == "NON_MANIFOLD"
        || modifier["use_even_offset"] == true
        || modifier["use_quality_normals"] == true
        || num(&modifier["thickness_clamp"]) != 0.
        || mesh.get("deform_weights").is_some()
        || ["vertex_group", "shell_vertex_group", "rim_vertex_group"]
            .iter()
            .any(|k| !text(&modifier[*k]).is_empty());
    if !extra {
        return super::topology::solidify(mesh, modifier);
    }
    if !mesh["loop_normals"].as_array().unwrap().is_empty() {
        return Err("SOLIDIFY custom split normals are outside the shell contract; clear them before applying".into());
    }
    let surface = Surface::new(mesh)?;
    if surface.positions.len() > 1_000_000 {
        return Err("SOLIDIFY exceeds the two-million vertex limit".into());
    }
    if surface.shortest.iter().any(|v| !v.is_finite())
        || mesh["edges"].as_array().unwrap().iter().any(|e| {
            let a = e[0].as_u64().unwrap() as usize;
            let b = e[1].as_u64().unwrap() as usize;
            !surface.edges.contains_key(&(a.min(b), a.max(b)))
        })
    {
        return Err(
            "SOLIDIFY extensions require surface geometry; remove loose vertices and edges".into(),
        );
    }
    let scales = factors(&surface, object, mesh, modifier);
    if modifier["solidify_mode"] == "NON_MANIFOLD" {
        return nonmanifold(&surface, object, mesh, modifier, &scales);
    }
    let mut output = super::topology::solidify(mesh, modifier)?;
    let mut normals = vec![[0.; 3]; surface.positions.len()];
    if modifier["use_quality_normals"] == true {
        for entries in surface.edges.values() {
            let (fi, a, b) = entries[0];
            let normal = if entries.len() == 2 {
                let other = surface.normals[entries[1].0];
                let angle = dot(surface.normals[fi], other).clamp(-1., 1.).acos();
                mul(
                    normalize(add(surface.normals[fi], other)),
                    angle * std::f64::consts::FRAC_2_PI,
                )
            } else {
                surface.normals[fi]
            };
            normals[a] = add(normals[a], normal);
            normals[b] = add(normals[b], normal);
        }
    } else {
        for (fi, f) in surface.faces.iter().enumerate() {
            for (j, &v) in f.iter().enumerate() {
                normals[v] = add(normals[v], mul(surface.normals[fi], surface.angles[fi][j]));
            }
        }
    }
    // Coplanar interior edges have zero angle weight; use ordinary normals
    // when the quality accumulator is zero, as Blender does.
    let needs_fallback: Vec<_> = normals.iter().map(|n| length(*n) < 1e-12).collect();
    for (fi, f) in surface.faces.iter().enumerate() {
        for (j, &v) in f.iter().enumerate() {
            if needs_fallback[v] {
                normals[v] = add(normals[v], mul(surface.normals[fi], surface.angles[fi][j]));
            }
        }
    }
    for n in &mut normals {
        *n = normalize(*n);
    }
    let mut even = vec![1.; normals.len()];
    if modifier["use_even_offset"] == true {
        let mut sum = vec![0.; normals.len()];
        let mut total = vec![0.; normals.len()];
        for (fi, f) in surface.faces.iter().enumerate() {
            for (j, &v) in f.iter().enumerate() {
                let cosine = dot(normals[v], surface.normals[fi]).abs();
                if cosine < 1e-6 {
                    return Err("SOLIDIFY even offset has cancelling face normals".into());
                }
                // Blender weights shell compensation by the exterior corner angle.
                let angle = (std::f64::consts::PI - surface.angles[fi][j]).max(f32::EPSILON as f64);
                sum[v] += angle / cosine;
                total[v] += angle;
            }
        }
        for i in 0..even.len() {
            if total[i] > 0. {
                even[i] = sum[i] / total[i];
            }
        }
    }
    let boundary: BTreeSet<_> = surface
        .edges
        .values()
        .filter(|e| e.len() == 1)
        .flat_map(|e| [e[0].1, e[0].2])
        .collect();
    let n = surface.positions.len();
    let only_rim = modifier["use_rim"] == true && modifier["use_rim_only"] == true;
    let t = num(&modifier["thickness"]);
    let center = t * num(&modifier["offset"]) * 0.5;
    let distances = [center + t.abs() * 0.5, center - t.abs() * 0.5];
    let source_weights = groups::weights(mesh);
    let mut weights = vec![];
    let mut vertices = vec![];
    for (side, distance) in distances.into_iter().enumerate() {
        for i in 0..n {
            if side == 1 && only_rim && !boundary.contains(&i) {
                continue;
            }
            vertices.push(json!(add(
                surface.positions[i],
                mul(normals[i], distance * scales[i] * even[i])
            )));
            let mut row = source_weights[i].clone();
            if modifier["use_rim"] == true && boundary.contains(&i) {
                assign(&mut row, group(object, &modifier["rim_vertex_group"]));
            }
            if side == 1 {
                assign(&mut row, group(object, &modifier["shell_vertex_group"]));
            }
            weights.push(row);
        }
    }
    output["vertices"] = super::f32_value(&json!(vertices))?;
    groups::store(&mut output, &weights);
    Ok(output)
}
fn root(parent: &mut [usize], mut i: usize) -> usize {
    while parent[i] != i {
        parent[i] = parent[parent[i]];
        i = parent[i];
    }
    i
}
fn union(parent: &mut [usize], a: usize, b: usize) {
    let a = root(parent, a);
    let b = root(parent, b);
    parent[b] = a;
}
fn nonmanifold(
    surface: &Surface,
    object: &Value,
    mesh: &Value,
    modifier: &Value,
    scales: &[f64],
) -> Result<Value, String> {
    let starts = starts(&surface.faces);
    let corners: usize = surface.faces.iter().map(Vec::len).sum();
    if corners > 1_000_000 {
        return Err("NON_MANIFOLD SOLIDIFY is bounded to one million input corners".into());
    }
    let mut parent: Vec<_> = (0..corners * 2).collect();
    let node = |fi: usize, side: usize, v: usize| -> usize {
        2 * (starts[fi] + surface.faces[fi].iter().position(|&i| i == v).unwrap()) + side
    };
    for (&(a, b), entries) in &surface.edges {
        if entries.len() < 2 {
            continue;
        }
        if entries.len() > 64 {
            return Err("NON_MANIFOLD SOLIDIFY supports at most 64 faces per edge".into());
        }
        let axis = normalize(sub(surface.positions[b], surface.positions[a]));
        let mut ordered = vec![];
        let mut basis = None;
        for &(fi, x, _) in entries {
            let side = usize::from(x != a);
            let sign = if side == 0 { 1. } else { -1. };
            let radial = mul(cross(surface.normals[fi], axis), sign);
            let base = *basis.get_or_insert(radial);
            let angle = dot(axis, cross(base, radial)).atan2(dot(base, radial));
            ordered.push((angle, fi, side));
        }
        ordered.sort_by(|a, b| a.0.total_cmp(&b.0));
        for j in 0..ordered.len() {
            let (_, fi, side) = ordered[j];
            let (_, fj, other) = ordered[(j + 1) % ordered.len()];
            for v in [a, b] {
                union(&mut parent, node(fi, side, v), node(fj, 1 - other, v));
            }
        }
    }
    let mut components: BTreeMap<usize, Vec<(usize, usize, usize)>> = BTreeMap::new();
    for (fi, f) in surface.faces.iter().enumerate() {
        for &v in f {
            for side in 0..2 {
                components
                    .entry(root(&mut parent, node(fi, side, v)))
                    .or_default()
                    .push((fi, side, v));
            }
        }
    }
    let only_rim = modifier["use_rim"] == true && modifier["use_rim_only"] == true;
    let t = num(&modifier["thickness"]);
    let center = t * num(&modifier["offset"]) * 0.5;
    let mut vertices = vec![];
    let mut weights = vec![];
    let source_weights = groups::weights(mesh);
    let mut mapped = BTreeMap::new();
    let mut origins = vec![];
    let boundary: BTreeSet<_> = surface
        .edges
        .values()
        .filter(|e| e.len() == 1)
        .flat_map(|e| [e[0].1, e[0].2])
        .collect();
    for (r, keys) in &components {
        let v = keys[0].2;
        let mut basis: Vec<[f64; 3]> = vec![];
        let mut displacement = [0.; 3];
        for &(fi, side, _) in keys {
            let sign = if side == 0 { 1. } else { -1. };
            let normal = mul(surface.normals[fi], sign);
            let distance = (t.abs() * 0.5 + sign * center).max(1e-5) * scales[v];
            let mut orthogonal = normal;
            for &b in &basis {
                orthogonal = sub(orthogonal, mul(b, dot(orthogonal, b)));
            }
            let squared = dot(orthogonal, orthogonal);
            if squared > 1e-10 {
                displacement = add(
                    displacement,
                    mul(orthogonal, (distance - dot(normal, displacement)) / squared),
                );
                basis.push(normalize(orthogonal));
            } else if (dot(normal, displacement) - distance).abs() > 1e-5 {
                return Err("NON_MANIFOLD SOLIDIFY has inconsistent thickness constraints; split the junction or reduce thickness".into());
            }
        }
        if length(displacement) > 1e6 {
            return Err("NON_MANIFOLD SOLIDIFY thickness exceeds the finite offset limit".into());
        }
        mapped.insert(*r, vertices.len());
        origins.push(v);
        vertices.push(json!(add(surface.positions[v], displacement)));
        let mut row = source_weights[v].clone();
        if modifier["use_rim"] == true && boundary.contains(&v) {
            assign(&mut row, group(object, &modifier["rim_vertex_group"]));
        }
        if !only_rim && keys.iter().any(|(_, s, _)| *s == usize::from(t != 0.)) {
            assign(&mut row, group(object, &modifier["shell_vertex_group"]));
        }
        weights.push(row);
    }
    let mut lookup = vec![0; corners * 2];
    for (i, value) in lookup.iter_mut().enumerate() {
        *value = mapped[&root(&mut parent, i)];
    }
    let get = |fi, side, v| lookup[node(fi, side, v)];
    let slots = mesh["materials"].as_array().unwrap().len();
    let material = |fi: usize, key: &str| {
        let base = mesh["material_indices"][fi].as_i64().unwrap_or(0);
        if slots == 0 {
            base as usize
        } else {
            (base + modifier[key].as_i64().unwrap_or(0)).clamp(0, slots as i64 - 1) as usize
        }
    };
    let mut output_faces = vec![];
    if !only_rim {
        for (fi, f) in surface.faces.iter().enumerate() {
            for side in 0..2 {
                let order: Vec<_> = if side == 0 {
                    (0..f.len()).collect()
                } else {
                    (0..f.len()).rev().collect()
                };
                output_faces.push(Face {
                    vertices: order.iter().map(|&j| get(fi, side, f[j])).collect(),
                    corners: order.iter().map(|&j| starts[fi] + j).collect(),
                    source: fi,
                    material: if side == usize::from(t != 0.) {
                        Some(material(fi, "material_offset"))
                    } else {
                        None
                    },
                });
            }
        }
    }
    if modifier["use_rim"] == true {
        for entries in surface.edges.values() {
            if entries.len() == 1 {
                let (fi, a, b) = entries[0];
                let ca = starts[fi] + surface.faces[fi].iter().position(|&v| v == a).unwrap();
                let cb = starts[fi] + surface.faces[fi].iter().position(|&v| v == b).unwrap();
                output_faces.push(Face {
                    vertices: vec![get(fi, 0, b), get(fi, 0, a), get(fi, 1, a), get(fi, 1, b)],
                    corners: vec![cb, ca, ca, cb],
                    source: fi,
                    material: Some(material(fi, "material_offset_rim")),
                });
            }
        }
        if !only_rim {
            let mut incidence: BTreeMap<Edge, Vec<(usize, usize, usize, usize)>> = BTreeMap::new();
            for (fi, f) in output_faces.iter().enumerate() {
                for j in 0..f.vertices.len() {
                    let a = f.vertices[j];
                    let b = f.vertices[(j + 1) % f.vertices.len()];
                    incidence
                        .entry((a.min(b), a.max(b)))
                        .or_default()
                        .push((a, b, fi, j));
                }
            }
            let mut gaps = BTreeMap::new();
            for edges in incidence.values().filter(|e| e.len() == 1) {
                let (a, b, fi, j) = edges[0];
                if origins[a] != origins[b] {
                    return Err("NON_MANIFOLD SOLIDIFY could not close a radial junction".into());
                }
                if gaps.insert(b, (a, fi, j)).is_some() {
                    return Err("NON_MANIFOLD SOLIDIFY has an ambiguous boundary junction".into());
                }
            }
            while let Some((&first, _)) = gaps.first_key_value() {
                let mut current = first;
                let mut face_vertices = vec![];
                let mut face_corners = vec![];
                let source = loop {
                    let (next, fi, j) = gaps
                        .remove(&current)
                        .ok_or("NON_MANIFOLD SOLIDIFY has an open junction")?;
                    face_vertices.push(current);
                    let face = &output_faces[fi];
                    face_corners.push(face.corners[(j + 1) % face.corners.len()]);
                    current = next;
                    if current == first {
                        break face.source;
                    }
                    if face_vertices.len() > 2048 {
                        return Err("NON_MANIFOLD SOLIDIFY junction exceeds 2048 corners".into());
                    }
                };
                output_faces.push(Face {
                    vertices: face_vertices,
                    corners: face_corners,
                    source,
                    material: Some(material(source, "material_offset_rim")),
                });
            }
        }
    }
    if only_rim {
        let used: BTreeSet<_> = output_faces
            .iter()
            .flat_map(|f| f.vertices.iter().copied())
            .collect();
        let mut remap = vec![0; vertices.len()];
        let mut compact = vec![];
        let mut compact_weights = vec![];
        for i in used {
            remap[i] = compact.len();
            compact.push(vertices[i].clone());
            compact_weights.push(weights[i].clone());
        }
        for face in &mut output_faces {
            for v in &mut face.vertices {
                *v = remap[*v];
            }
        }
        vertices = compact;
        weights = compact_weights;
    }
    if t == 0. {
        for face in &mut output_faces {
            face.vertices.reverse();
            face.corners.reverse();
        }
    }
    let mut output = assemble(mesh, vertices, &output_faces, vec![])?;
    groups::store(&mut output, &weights);
    Ok(output)
}
