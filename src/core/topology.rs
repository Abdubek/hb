//! Topology-changing modifier kernels. Corner attributes follow every remap.
use super::{
    Value, f32_value,
    math::{add, cross, dot, length, mul, normalize, sub},
    num, text, vec3,
};
use serde_json::json;
use std::collections::{BTreeMap, BTreeSet};

pub(super) struct Face {
    pub(super) vertices: Vec<usize>,
    pub(super) corners: Vec<usize>,
    pub(super) source: usize,
    pub(super) material: Option<usize>,
}
pub(super) fn faces(mesh: &Value) -> Vec<Vec<usize>> {
    mesh["faces"]
        .as_array()
        .unwrap()
        .iter()
        .map(|f| {
            f.as_array()
                .unwrap()
                .iter()
                .map(|v| v.as_u64().unwrap() as usize)
                .collect()
        })
        .collect()
}
pub(super) fn starts(faces: &[Vec<usize>]) -> Vec<usize> {
    let mut offset = 0;
    faces
        .iter()
        .map(|f| {
            let n = offset;
            offset += f.len();
            n
        })
        .collect()
}
pub(super) fn assemble(
    mesh: &Value,
    vertices: Vec<Value>,
    faces: &[Face],
    edges: Vec<Value>,
) -> Result<Value, String> {
    if vertices.len() > 2_000_000 || faces.len() > 2_000_000 {
        return Err(
            "Evaluated mesh exceeds 2,000,000 vertices/faces; reduce modeling detail".into(),
        );
    }
    let mut out = mesh.clone();
    out["vertices"] = f32_value(&json!(vertices))?;
    out["faces"] = json!(faces.iter().map(|f| &f.vertices).collect::<Vec<_>>());
    let mut known = BTreeSet::new();
    let mut unique = vec![];
    for e in edges {
        let a = e[0].as_u64().unwrap();
        let b = e[1].as_u64().unwrap();
        if a != b && known.insert((a.min(b), a.max(b))) {
            unique.push(e);
        }
    }
    for f in faces {
        for i in 0..f.vertices.len() {
            let a = f.vertices[i] as u64;
            let b = f.vertices[(i + 1) % f.vertices.len()] as u64;
            if a != b && known.insert((a.min(b), a.max(b))) {
                unique.push(json!([a, b]));
            }
        }
    }
    out["edges"] = json!(unique);
    out["material_indices"] = json!(
        faces
            .iter()
            .map(|f| f
                .material
                .map(|m| json!(m))
                .unwrap_or_else(|| mesh["material_indices"][f.source].clone()))
            .collect::<Vec<_>>()
    );
    out["smooth"] = json!(
        faces
            .iter()
            .map(|f| mesh["smooth"][f.source].clone())
            .collect::<Vec<_>>()
    );
    for layer in out["uv_layers"].as_array_mut().unwrap() {
        let old = layer["data"].as_array().unwrap();
        layer["data"] = json!(
            faces
                .iter()
                .flat_map(|f| f.corners.iter().map(|&c| old[c].clone()))
                .collect::<Vec<_>>()
        );
    }
    for field in ["colors", "loop_normals"] {
        let old = mesh[field].as_array().unwrap();
        if !old.is_empty() {
            out[field] = json!(
                faces
                    .iter()
                    .flat_map(|f| f.corners.iter().map(|&c| old[c].clone()))
                    .collect::<Vec<_>>()
            );
        }
    }
    Ok(out)
}

pub fn mirror(mesh: &Value, modifier: &Value) -> Result<Value, String> {
    let mut out = mesh.clone();
    for axis in 0..3 {
        if modifier["use_axis"][axis] != true {
            continue;
        }
        let old = out.clone();
        let source = faces(&old);
        let starts = starts(&source);
        let vs = old["vertices"].as_array().unwrap();
        if vs.len() > 1_000_000 {
            return Err("MIRROR exceeds 2,000,000 vertex resource limit".into());
        }
        let mut vertices = vs.clone();
        let mut map = vec![];
        let tolerance = num(&modifier["merge_threshold"]);
        for (i, v) in vs.iter().enumerate() {
            let mut p = vec3(v);
            if modifier["use_mirror_merge"] == true && 2. * p[axis].abs() < tolerance {
                p[axis] = 0.;
                vertices[i] = json!(p);
                map.push(i);
            } else {
                p[axis] = -p[axis];
                map.push(vertices.len());
                vertices.push(json!(p));
            }
        }
        let mut output = vec![];
        for (i, f) in source.iter().enumerate() {
            output.push(Face {
                vertices: f.clone(),
                corners: (starts[i]..starts[i] + f.len()).collect(),
                source: i,
                material: None,
            });
        }
        let mut reflected_face_count = 0;
        for (i, f) in source.iter().enumerate() {
            // Blender keeps one copy of a face fully on the merged seam.
            if modifier["use_mirror_merge"] == true && f.iter().all(|&v| map[v] == v) {
                continue;
            }
            let order = std::iter::once(0)
                .chain((1..f.len()).rev())
                .collect::<Vec<_>>();
            output.push(Face {
                vertices: order.iter().map(|&j| map[f[j]]).collect(),
                corners: order.iter().map(|&j| starts[i] + j).collect(),
                source: i,
                material: None,
            });
            reflected_face_count += 1;
        }
        let mut edges = old["edges"].as_array().unwrap().clone();
        edges.extend(old["edges"].as_array().unwrap().iter().map(|e| {
            json!([
                map[e[0].as_u64().unwrap() as usize],
                map[e[1].as_u64().unwrap() as usize]
            ])
        }));
        out = assemble(&old, vertices, &output, edges)?;
        if reflected_face_count > 0 && !old["loop_normals"].as_array().unwrap().is_empty() {
            let start: usize = source.iter().map(Vec::len).sum();
            for v in out["loop_normals"]
                .as_array_mut()
                .unwrap()
                .iter_mut()
                .skip(start)
            {
                v[axis] = json!(-num(&v[axis]));
            }
        }
    }
    Ok(out)
}

pub fn triangulate(mesh: &Value, modifier: &Value) -> Result<Value, String> {
    let has_normals = !mesh["loop_normals"].as_array().unwrap().is_empty();
    let source = faces(mesh);
    let starts = starts(&source);
    let mut retained = vec![];
    let mut appended = vec![];
    let min = modifier["min_vertices"].as_u64().unwrap() as usize;
    for (i, f) in source.iter().enumerate() {
        if has_normals && modifier["keep_custom_normals"] == false && f.len() >= min && f.len() > 3
        {
            if mesh["smooth"][i] == true {
                return Err(
                    "TRIANGULATE smooth custom normals require keep_custom_normals=True".into(),
                );
            }
            let points: Vec<_> = f.iter().map(|&v| vec3(&mesh["vertices"][v])).collect();
            super::triangulation::polygon(&points, "BEAUTY", "EAR_CLIP")?;
        }
        let mut groups: Vec<Vec<usize>> = if f.len() < min || f.len() == 3 {
            vec![(0..f.len()).collect()]
        } else if f.len() == 4 {
            let p: Vec<_> = f.iter().map(|&v| vec3(&mesh["vertices"][v])).collect();
            let a = sub(p[0], p[2]);
            let b = sub(p[1], p[3]);
            let fixed = match text(&modifier["quad_method"]) {
                "FIXED" => true,
                "FIXED_ALTERNATE" => false,
                "SHORTEST_DIAGONAL" => dot(a, a) < dot(b, b),
                "LONGEST_DIAGONAL" => dot(a, a) > dot(b, b),
                "BEAUTY" => super::triangulation::polygon(&p, "BEAUTY", "BEAUTY")?[0] == [0, 2, 3],
                _ => return Err("Unknown TRIANGULATE quad method".into()),
            };
            if fixed {
                vec![vec![0, 2, 3], vec![0, 1, 2]]
            } else {
                vec![vec![1, 3, 0], vec![1, 2, 3]]
            }
        } else {
            let points: Vec<_> = f.iter().map(|&v| vec3(&mesh["vertices"][v])).collect();
            super::triangulation::polygon(
                &points,
                "BEAUTY",
                if modifier["ngon_method"] == "CLIP" {
                    "EAR_CLIP"
                } else {
                    "BEAUTY"
                },
            )?
            .into_iter()
            .map(|t| t.to_vec())
            .collect()
        };
        for (j, g) in groups.drain(..).enumerate() {
            let record = Face {
                vertices: g.iter().map(|&k| f[k]).collect(),
                corners: g.iter().map(|&k| starts[i] + k).collect(),
                source: i,
                material: None,
            };
            if j == 0 {
                retained.push(record);
            } else {
                appended.push(record);
            }
        }
    }
    retained.extend(appended);
    let mut out = assemble(
        mesh,
        mesh["vertices"].as_array().unwrap().clone(),
        &retained,
        mesh["edges"].as_array().unwrap().clone(),
    )?;
    if has_normals && modifier["keep_custom_normals"] == false {
        let mut normals = vec![];
        for face in &retained {
            let original: Vec<_> = source[face.source]
                .iter()
                .map(|&v| vec3(&mesh["vertices"][v]))
                .collect();
            let output: Vec<_> = face
                .vertices
                .iter()
                .map(|&v| vec3(&mesh["vertices"][v]))
                .collect();
            for (j, &corner) in face.corners.iter().enumerate() {
                let custom = vec3(&mesh["loop_normals"][corner]);
                normals.push(json!(if face.vertices.len() == source[face.source].len() {
                    custom
                } else {
                    super::normal_space::remap(
                        &original,
                        corner - starts[face.source],
                        &output,
                        j,
                        custom,
                    )
                }));
            }
        }
        out["loop_normals"] = f32_value(&json!(normals))?;
    }
    Ok(out)
}

pub fn solidify(mesh: &Value, modifier: &Value) -> Result<Value, String> {
    if !mesh["loop_normals"].as_array().unwrap().is_empty() {
        return Err("SOLIDIFY custom split normals are unsupported; remove custom normals before generating a shell".into());
    }
    let source = faces(mesh);
    let starts = starts(&source);
    let vs = mesh["vertices"].as_array().unwrap();
    let n = vs.len();
    if n > 1_000_000 {
        return Err("SOLIDIFY exceeds 2,000,000 vertex resource limit".into());
    }
    let mut normals = vec![[0.; 3]; n];
    // Store oriented face incidence in face/corner order, keeping seam UVs.
    let mut edges: Vec<(usize, usize, usize, usize)> = vec![];
    let mut incidence: BTreeMap<(usize, usize), Vec<usize>> = BTreeMap::new();
    for (fi, f) in source.iter().enumerate() {
        let points: Vec<_> = f.iter().map(|&v| vec3(&vs[v])).collect();
        let mut normal = [0.; 3];
        for i in 0..f.len() {
            normal = add(normal, cross(points[i], points[(i + 1) % f.len()]));
        }
        if length(normal) < 1e-15 {
            return Err("SOLIDIFY requires non-degenerate faces".into());
        }
        normal = normalize(normal);
        for j in 0..f.len() {
            let previous = (j + f.len() - 1) % f.len();
            let next = (j + 1) % f.len();
            let a = normalize(sub(points[previous], points[j]));
            let b = normalize(sub(points[next], points[j]));
            let angle = dot(a, b).clamp(-1., 1.).acos();
            normals[f[j]] = add(normals[f[j]], mul(normal, angle));
            let a = f[previous];
            let b = f[j];
            let key = (a.min(b), a.max(b));
            let entries = incidence.entry(key).or_default();
            if let Some(&index) = entries.first()
                && edges[index].0 == a
            {
                return Err("SOLIDIFY requires consistently oriented manifold faces".into());
            }
            entries.push(edges.len());
            edges.push((a, b, fi, j));
            if entries.len() > 2 {
                return Err(
                    "SOLIDIFY non-manifold edges are unsupported; use a manifold surface".into(),
                );
            }
        }
    }
    for v in &mut normals {
        if length(*v) < 1e-15 {
            return Err("SOLIDIFY requires surface vertices with valid normals; loose or cancelling-normal vertices are unsupported".into());
        }
        *v = normalize(*v);
    }
    let thickness = num(&modifier["thickness"]);
    let center = thickness * num(&modifier["offset"]) * 0.5;
    let distances = [
        center + thickness.abs() * 0.5,
        center - thickness.abs() * 0.5,
    ];
    let only_rim = modifier["use_rim"] == true && modifier["use_rim_only"] == true;
    let boundary: BTreeSet<usize> = edges
        .iter()
        .filter(|(a, b, _, _)| incidence[&((*a).min(*b), (*a).max(*b))].len() == 1)
        .flat_map(|(a, b, _, _)| [*a, *b])
        .collect();
    let mut vertices = vs
        .iter()
        .zip(&normals)
        .map(|(v, normal)| json!(add(vec3(v), mul(*normal, distances[0]))))
        .collect::<Vec<_>>();
    let mut inner = vec![None; n];
    for (i, (v, normal)) in vs.iter().zip(&normals).enumerate() {
        if !only_rim || boundary.contains(&i) {
            inner[i] = Some(vertices.len());
            vertices.push(json!(add(vec3(v), mul(*normal, distances[1]))));
        }
    }
    let slots = mesh["materials"].as_array().unwrap().len();
    let material = |face: usize, field: &str| {
        let base = mesh["material_indices"][face].as_i64().unwrap_or(0);
        let offset = modifier[field].as_i64().unwrap_or(0);
        if slots == 0 {
            base as usize
        } else {
            (base + offset).clamp(0, slots as i64 - 1) as usize
        }
    };
    let mut out = vec![];
    for (i, f) in source.iter().enumerate() {
        out.push(Face {
            vertices: f.clone(),
            corners: (starts[i]..starts[i] + f.len()).collect(),
            source: i,
            material: None,
        });
    }
    if !only_rim {
        for (i, f) in source.iter().enumerate() {
            let order = std::iter::once(0)
                .chain((1..f.len()).rev())
                .collect::<Vec<_>>();
            out.push(Face {
                vertices: order.iter().map(|&j| f[j] + n).collect(),
                corners: order.iter().map(|&j| starts[i] + j).collect(),
                source: i,
                material: Some(material(i, "material_offset")),
            });
        }
    }
    if modifier["use_rim"] == true {
        for (a, b, fi, j) in &edges {
            if incidence[&((*a).min(*b), (*a).max(*b))].len() != 1 {
                continue;
            }
            let previous = (j + source[*fi].len() - 1) % source[*fi].len();
            out.push(Face {
                vertices: vec![*b, *a, inner[*a].unwrap(), inner[*b].unwrap()],
                corners: vec![
                    starts[*fi] + j,
                    starts[*fi] + previous,
                    starts[*fi] + previous,
                    starts[*fi] + j,
                ],
                source: *fi,
                material: Some(material(*fi, "material_offset_rim")),
            });
        }
    }
    // Loose edges are retained on both shells.
    let mut es = mesh["edges"].as_array().unwrap().clone();
    if !only_rim {
        es.extend(mesh["edges"].as_array().unwrap().iter().map(|e| {
            json!([
                e[0].as_u64().unwrap() + n as u64,
                e[1].as_u64().unwrap() + n as u64
            ])
        }));
    }
    assemble(mesh, vertices, &out, es)
}
