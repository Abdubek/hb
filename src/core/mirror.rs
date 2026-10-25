//! Affine mirror planes, bounded face bisection, UV offsets and deform weights.
use super::{
    Scene, Value, f32_value, groups, id,
    math::{self, M4, V3},
    num, vec3,
};
use serde_json::json;
use std::collections::{BTreeMap, BTreeSet};
#[derive(Clone, Copy)]
struct Corner {
    a: usize,
    b: usize,
    t: f64,
}
fn single(a: usize) -> Corner {
    Corner { a, b: a, t: 0. }
}
fn value(data: &[Value], corner: Corner) -> Value {
    if corner.a == corner.b {
        return data[corner.a].clone();
    }
    json!(
        data[corner.a]
            .as_array()
            .unwrap()
            .iter()
            .zip(data[corner.b].as_array().unwrap())
            .map(|(a, b)| (num(a) * (1. - corner.t) + num(b) * corner.t) as f32)
            .collect::<Vec<_>>()
    )
}
fn remap(
    mesh: &Value,
    vertices: Vec<V3>,
    faces: Vec<Vec<usize>>,
    sources: &[usize],
    corners: &[Corner],
    edges: Vec<[usize; 2]>,
) -> Result<Value, String> {
    if vertices.len() > 2_000_000 || faces.len() > 2_000_000 {
        return Err("MIRROR exceeds two million vertices/faces".into());
    }
    let mut out = mesh.clone();
    out["vertices"] = f32_value(&json!(vertices))?;
    out["faces"] = json!(faces);
    let mut seen = BTreeSet::new();
    let mut unique = vec![];
    for [a, b] in edges {
        if a != b && seen.insert((a.min(b), a.max(b))) {
            unique.push([a, b]);
        }
    }
    for face in &faces {
        for i in 0..face.len() {
            let a = face[i];
            let b = face[(i + 1) % face.len()];
            if a != b && seen.insert((a.min(b), a.max(b))) {
                unique.push([a, b]);
            }
        }
    }
    out["edges"] = json!(unique);
    for field in ["material_indices", "smooth"] {
        out[field] = json!(
            sources
                .iter()
                .map(|&i| mesh[field][i].clone())
                .collect::<Vec<_>>()
        );
    }
    for layer in out["uv_layers"].as_array_mut().unwrap() {
        let data = layer["data"].as_array().unwrap();
        layer["data"] = json!(corners.iter().map(|&c| value(data, c)).collect::<Vec<_>>());
    }
    for field in ["loop_normals", "colors"] {
        let data = mesh[field].as_array().unwrap();
        if !data.is_empty() {
            out[field] = json!(corners.iter().map(|&c| value(data, c)).collect::<Vec<_>>());
        }
    }
    Ok(out)
}
struct Cut {
    source: Vec<V3>,
    distance: Vec<f64>,
    source_weights: Vec<Vec<(usize, f32)>>,
    vertices: Vec<V3>,
    weights: Vec<Vec<(usize, f32)>>,
    map: Vec<Option<usize>>,
    edges: BTreeMap<(usize, usize), usize>,
}
impl Cut {
    fn edge(&mut self, a: usize, b: usize) -> (usize, f64) {
        if self.distance[a] == 0. {
            return (self.map[a].unwrap(), 0.);
        }
        if self.distance[b] == 0. {
            return (self.map[b].unwrap(), 1.);
        }
        let t = self.distance[a] / (self.distance[a] - self.distance[b]);
        let key = (a.min(b), a.max(b));
        let index = *self.edges.entry(key).or_insert_with(|| {
            let index = self.vertices.len();
            self.vertices.push(std::array::from_fn(|k| {
                (self.source[a][k] * (1. - t) + self.source[b][k] * t) as f32 as f64
            }));
            self.weights.push(groups::blend(
                &self.source_weights[a],
                &self.source_weights[b],
                t as f32,
            ));
            index
        });
        (index, t)
    }
}
fn bisect(mesh: &Value, q: M4, axis: usize, flip: bool, epsilon: f64) -> Result<Value, String> {
    let row = [q[axis][0], q[axis][1], q[axis][2]];
    let length = math::length(row);
    if length < 1e-20 {
        return Err("MIRROR bisect requires an invertible mirror plane".into());
    }
    let normal = math::mul(row, 1. / length);
    let constant = q[axis][3] / length;
    let mut source: Vec<_> = mesh["vertices"]
        .as_array()
        .unwrap()
        .iter()
        .map(vec3)
        .collect();
    let mut distance = vec![];
    let mut vertices = vec![];
    let mut map = vec![];
    let mut weights = vec![];
    let source_weights = groups::weights(mesh);
    for (i, p) in source.iter_mut().enumerate() {
        let mut d = math::dot(*p, normal) + constant;
        if d.abs() <= epsilon {
            *p = math::sub(*p, math::mul(normal, d)).map(|v| v as f32 as f64);
            d = 0.;
        }
        if flip {
            d = -d;
        }
        distance.push(d);
        if d >= 0. {
            map.push(Some(vertices.len()));
            vertices.push(*p);
            weights.push(source_weights[i].clone());
        } else {
            map.push(None);
        }
    }
    let mut cut = Cut {
        source,
        distance,
        source_weights,
        vertices,
        weights,
        map,
        edges: BTreeMap::new(),
    };
    let mut faces = vec![];
    let mut sources = vec![];
    let mut corners = vec![];
    let mut offset = 0;
    for (fi, face) in mesh["faces"].as_array().unwrap().iter().enumerate() {
        let face: Vec<_> = face
            .as_array()
            .unwrap()
            .iter()
            .map(|v| v.as_u64().unwrap() as usize)
            .collect();
        let crossings = (0..face.len())
            .filter(|&i| cut.distance[face[i]] * cut.distance[face[(i + 1) % face.len()]] < 0.)
            .count();
        if crossings > 2 {
            return Err("MIRROR bisect supports one cut segment per polygon; triangulate multiply-crossing n-gons first".into());
        }
        let mut output = vec![];
        let mut loop_corners = vec![];
        for i in 0..face.len() {
            let previous = (i + face.len() - 1) % face.len();
            let a = face[previous];
            let b = face[i];
            let a_inside = cut.distance[a] >= 0.;
            let b_inside = cut.distance[b] >= 0.;
            if a_inside != b_inside {
                let (v, t) = cut.edge(a, b);
                output.push(v);
                loop_corners.push(Corner {
                    a: offset + previous,
                    b: offset + i,
                    t,
                });
            }
            if b_inside {
                output.push(cut.map[b].unwrap());
                loop_corners.push(single(offset + i));
            }
        }
        let mut dedup = vec![];
        let mut dedup_corners = vec![];
        for (v, c) in output.into_iter().zip(loop_corners) {
            if dedup.last() != Some(&v) {
                dedup.push(v);
                dedup_corners.push(c);
            }
        }
        if dedup.len() > 1 && dedup.first() == dedup.last() {
            dedup.pop();
            dedup_corners.pop();
        }
        if dedup.len() >= 3 {
            faces.push(dedup);
            sources.push(fi);
            corners.extend(dedup_corners);
        }
        offset += face.len();
    }
    let mut edges = vec![];
    for edge in mesh["edges"].as_array().unwrap() {
        let a = edge[0].as_u64().unwrap() as usize;
        let b = edge[1].as_u64().unwrap() as usize;
        match (cut.map[a], cut.map[b]) {
            (Some(a), Some(b)) => edges.push([a, b]),
            (Some(v), None) | (None, Some(v)) => {
                let (p, _) = cut.edge(a, b);
                if p != v {
                    edges.push([v, p]);
                }
            }
            _ => {}
        }
    }
    let mut out = remap(mesh, cut.vertices, faces, &sources, &corners, edges)?;
    groups::store(&mut out, &cut.weights);
    Ok(out)
}
pub fn apply(scene: &Scene, object: &Value, mesh: &Value, m: &Value) -> Result<Value, String> {
    let extended = !m["mirror_object"].is_null()
        || m["use_bisect_axis"]
            .as_array()
            .is_some_and(|a| a.iter().any(|v| v == true))
        || m["use_mirror_u"] == true
        || m["use_mirror_v"] == true
        || ["offset_u", "offset_v", "mirror_offset_u", "mirror_offset_v"]
            .iter()
            .any(|f| num(&m[*f]) != 0.)
        || mesh.get("deform_weights").is_some();
    if !extended {
        return super::topology::mirror(mesh, m);
    }
    let q = if let Some(key) = m["mirror_object"].as_u64() {
        math::matmul(math::inverse(scene.world(key)?)?, scene.world(id(object))?)
    } else {
        math::IDENTITY
    };
    let inverse = math::inverse(q)?;
    let flip_map = groups::flip_map(object);
    let flip_groups = m.get("use_mirror_vertex_groups").is_none_or(|v| v == true);
    let mut out = mesh.clone();
    for axis in 0..3 {
        if m["use_axis"][axis] != true {
            continue;
        }
        if m["use_bisect_axis"][axis] == true {
            out = bisect(
                &out,
                q,
                axis,
                m["use_bisect_flip_axis"][axis] == true,
                m.get("bisect_threshold")
                    .map(num)
                    .unwrap_or(0.001_f32 as f64),
            )?;
        }
        let old = out;
        let mut reflection = math::IDENTITY;
        reflection[axis][axis] = -1.;
        let reflection = math::matmul(inverse, math::matmul(reflection, q));
        let source: Vec<_> = old["vertices"]
            .as_array()
            .unwrap()
            .iter()
            .map(vec3)
            .collect();
        let source_weights = groups::weights(&old);
        if source.len() > 1_000_000 {
            return Err("MIRROR exceeds two million vertices".into());
        }
        let mut vertices = source.clone();
        let mut weights = source_weights.clone();
        let mut map = vec![];
        let tolerance = num(&m["merge_threshold"]);
        for (i, p) in source.iter().enumerate() {
            let reflected = math::point(reflection, *p).map(|v| v as f32 as f64);
            let d = math::sub(*p, reflected);
            let flipped: Vec<_> = source_weights[i]
                .iter()
                .map(|&(group, weight)| {
                    (
                        if flip_groups {
                            flip_map.get(group).copied().unwrap_or(group)
                        } else {
                            group
                        },
                        weight,
                    )
                })
                .collect();
            if m["use_mirror_merge"] == true && math::dot(d, d) < tolerance * tolerance {
                vertices[i] = math::mul(math::add(*p, reflected), 0.5).map(|v| v as f32 as f64);
                weights[i] = groups::blend(&source_weights[i], &flipped, 0.5);
                map.push(i);
            } else {
                map.push(vertices.len());
                vertices.push(reflected);
                weights.push(flipped);
            }
        }
        let old_faces: Vec<Vec<usize>> = old["faces"]
            .as_array()
            .unwrap()
            .iter()
            .map(|f| {
                f.as_array()
                    .unwrap()
                    .iter()
                    .map(|i| i.as_u64().unwrap() as usize)
                    .collect()
            })
            .collect();
        let mut faces = old_faces.clone();
        let mut sources: Vec<_> = (0..faces.len()).collect();
        let count: usize = faces.iter().map(Vec::len).sum();
        let mut corners: Vec<_> = (0..count).map(single).collect();
        let mut offset = 0;
        for (fi, face) in old_faces.iter().enumerate() {
            if !(m["use_mirror_merge"] == true && face.iter().all(|&i| map[i] == i)) {
                let order: Vec<_> = std::iter::once(0).chain((1..face.len()).rev()).collect();
                faces.push(order.iter().map(|&i| map[face[i]]).collect());
                sources.push(fi);
                corners.extend(order.iter().map(|&i| single(offset + i)));
            }
            offset += face.len();
        }
        let mut edges = vec![];
        for edge in old["edges"].as_array().unwrap() {
            let a = edge[0].as_u64().unwrap() as usize;
            let b = edge[1].as_u64().unwrap() as usize;
            edges.push([a, b]);
        }
        edges.extend(edges.clone().into_iter().map(|[a, b]| [map[a], map[b]]));
        out = remap(&old, vertices, faces, &sources, &corners, edges)?;
        for normal in out["loop_normals"]
            .as_array_mut()
            .unwrap()
            .iter_mut()
            .skip(count)
        {
            *normal = f32_value(&json!(math::normal(reflection, vec3(normal))))?;
        }
        for layer in out["uv_layers"].as_array_mut().unwrap() {
            for uv in layer["data"].as_array_mut().unwrap().iter_mut().skip(count) {
                for (index, suffix) in [(0, "u"), (1, "v")] {
                    let mut v = num(&uv[index]) as f32;
                    if m[format!("use_mirror_{suffix}")] == true {
                        v = 1. - v + num(&m[format!("mirror_offset_{suffix}")]) as f32;
                    }
                    uv[index] = json!(v + num(&m[format!("offset_{suffix}")]) as f32);
                }
            }
        }
        groups::store(&mut out, &weights);
    }
    Ok(out)
}
