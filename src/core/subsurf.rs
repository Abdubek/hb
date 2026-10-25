//! Bounded CPU subdivision with OpenSubdiv, preserving per-face and UV data.
use super::{Value, num, vec3};
use serde_json::json;
use std::{
    collections::{BTreeMap, BTreeSet},
    ffi::{CStr, c_char, c_void},
    ptr,
};
#[repr(C)]
struct Input {
    positions: *const f32,
    face_counts: *const i32,
    face_indices: *const i32,
    uv_values: *const f32,
    uv_indices: *const i32,
    uv_counts: *const i32,
    crease_edges: *const i32,
    crease_weights: *const f32,
    vertex_creases: *const f32,
    colors: *const f32,
    normals: *const f32,
    crease_count: usize,
    use_creases: i32,
    vertex_count: usize,
    face_count: usize,
    corner_count: usize,
    uv_layer_count: usize,
}
#[repr(C)]
struct View {
    positions: *const f32,
    faces: *const i32,
    source_faces: *const i32,
    uv: *const f32,
    colors: *const f32,
    normals: *const f32,
    vertex_creases: *const f32,
    crease_edges: *const i32,
    crease_weights: *const f32,
    original_vertices: *const i32,
    crease_count: usize,
    vertex_count: usize,
    face_count: usize,
    uv_layer_count: usize,
}
unsafe extern "C" {
    fn hb_subdivide(
        input: *const Input,
        level: i32,
        simple: i32,
        limit: i32,
        corners: i32,
        error: *mut c_char,
        error_size: usize,
    ) -> *mut c_void;
    fn hb_subdivide_view(result: *const c_void, view: *mut View);
    fn hb_subdivide_free(result: *mut c_void);
}
struct ResultHandle(*mut c_void);
impl Drop for ResultHandle {
    fn drop(&mut self) {
        unsafe {
            hb_subdivide_free(self.0);
        }
    }
}
unsafe fn copied<T: Copy>(pointer: *const T, len: usize) -> Vec<T> {
    if len == 0 {
        vec![]
    } else {
        unsafe { std::slice::from_raw_parts(pointer, len).to_vec() }
    }
}

fn surface(mesh: &Value, modifier: &Value, render: bool) -> Result<Value, String> {
    let level = modifier[if render { "render_levels" } else { "levels" }]
        .as_u64()
        .ok_or("Invalid SUBSURF level")? as usize;
    if level == 0 {
        return Ok(mesh.clone());
    }
    if level > 6 {
        return Err("SUBSURF supports levels zero through six".into());
    }
    let vertices = mesh["vertices"]
        .as_array()
        .ok_or("Invalid SUBSURF vertices")?;
    let faces = mesh["faces"].as_array().ok_or("Invalid SUBSURF faces")?;
    let layers = mesh["uv_layers"]
        .as_array()
        .ok_or("Invalid SUBSURF UV layers")?;
    if vertices.len() > 2_000_000 || faces.len() > 2_000_000 || layers.len() > 8 {
        return Err("SUBSURF input exceeds two million vertices/faces or eight UV layers".into());
    }
    for (field, count) in [
        ("crease_vert", vertices.len()),
        ("crease_edge", mesh["edges"].as_array().unwrap().len()),
    ] {
        if mesh.get(field).is_some_and(|v| {
            v.as_array().is_none_or(|a| {
                a.len() != count
                    || a.iter().any(|x| {
                        x.as_f64()
                            .is_none_or(|x| !x.is_finite() || !(0. ..=1.).contains(&x))
                    })
            })
        }) {
            return Err("SUBSURF crease attributes do not match topology or 0..1 bounds".into());
        }
    }
    let mut counts = vec![];
    let mut indices = vec![];
    let mut edges = BTreeMap::new();
    let mut used = vec![false; vertices.len()];
    for face in faces {
        let face = face.as_array().ok_or("Invalid SUBSURF face")?;
        let mut unique = BTreeSet::new();
        for (i, index) in face.iter().enumerate() {
            let a = index.as_u64().ok_or("Invalid SUBSURF index")? as usize;
            let b = face[(i + 1) % face.len()]
                .as_u64()
                .ok_or("Invalid SUBSURF index")? as usize;
            if a >= vertices.len() || b >= vertices.len() || !unique.insert(a) {
                return Err("SUBSURF requires valid simple polygon loops".into());
            }
            used[a] = true;
            indices.push(a as i32);
            let value = edges.entry((a.min(b), a.max(b))).or_insert((0, 0));
            value.0 += 1;
            value.1 += if a < b { 1 } else { -1 };
        }
        if face.len() < 3 {
            return Err("SUBSURF faces need at least three distinct vertices".into());
        }
        counts.push(face.len() as i32);
    }
    if edges
        .values()
        .any(|&(count, orientation)| count > 2 || (count == 2 && orientation != 0))
    {
        return Err("SUBSURF requires consistently oriented manifold polygon surfaces; boundaries are allowed".into());
    }
    for edge in mesh["edges"].as_array().unwrap() {
        let a = edge[0].as_u64().unwrap() as usize;
        let b = edge[1].as_u64().unwrap() as usize;
        if !edges.contains_key(&(a.min(b), a.max(b))) {
            return Err("SUBSURF loose edges are unsupported; use a polygon surface".into());
        }
    }
    if faces.is_empty() {
        return Ok(mesh.clone());
    }
    if used.iter().any(|&v| !v) {
        return Err(
            "SUBSURF loose vertices are unsupported; remove unused vertices before refining".into(),
        );
    }
    let (mut predicted_vertices, mut predicted_edges, mut predicted_faces, mut predicted_corners) =
        (vertices.len(), edges.len(), faces.len(), indices.len());
    // Limit patches may refine through quality 3 even at lower display levels.
    let safety_level =
        if modifier["use_limit_surface"] == true && modifier["subdivision_type"] != "SIMPLE" {
            level.max(3)
        } else {
            level
        };
    for _ in 0..safety_level {
        predicted_vertices += predicted_edges + predicted_faces;
        predicted_edges = 2 * predicted_edges + predicted_corners;
        predicted_faces = predicted_corners;
        predicted_corners = 4 * predicted_faces;
        if predicted_vertices > 2_000_000 || predicted_faces > 2_000_000 {
            return Err("SUBSURF evaluated mesh exceeds two million vertices/faces; reduce levels or source topology".into());
        }
    }
    let positions: Vec<f32> = vertices
        .iter()
        .flat_map(|v| vec3(v).map(|v| v as f32))
        .collect();
    let mut uv_values = vec![];
    let mut uv_indices = vec![];
    let mut uv_counts = vec![];
    for layer in layers {
        let data = layer["data"].as_array().ok_or("Invalid SUBSURF UV data")?;
        if data.len() != indices.len() {
            return Err("SUBSURF UV corner count does not match topology".into());
        }
        let mut known = BTreeMap::new();
        for (corner, &vertex) in indices.iter().enumerate() {
            let u = num(&data[corner][0]) as f32;
            let v = num(&data[corner][1]) as f32;
            // FVar indices are shared only across corners on the same geometric
            // vertex with identical UV values; discontinuities remain seams.
            let key = (
                vertex,
                if u == 0. { 0 } else { u.to_bits() },
                if v == 0. { 0 } else { v.to_bits() },
            );
            let next = known.len() as i32;
            let value = *known.entry(key).or_insert_with(|| {
                uv_values.extend([u, v]);
                next
            });
            uv_indices.push(value);
        }
        uv_counts.push(known.len() as i32);
    }
    let vertex_creases: Vec<f32> = (0..vertices.len())
        .map(|i| num(&mesh["crease_vert"][i]) as f32)
        .collect();
    let mut crease_edges = vec![];
    let mut crease_weights = vec![];
    if let Some(values) = mesh["crease_edge"].as_array() {
        for (edge, value) in mesh["edges"].as_array().unwrap().iter().zip(values) {
            if num(value) > 0. {
                crease_edges.extend([
                    edge[0].as_u64().unwrap() as i32,
                    edge[1].as_u64().unwrap() as i32,
                ]);
                crease_weights.push(num(value) as f32);
            }
        }
    }
    let colors: Vec<f32> = mesh["colors"]
        .as_array()
        .unwrap()
        .iter()
        .flat_map(|c| c.as_array().unwrap().iter().map(|v| num(v) as f32))
        .collect();
    let preserve_normals = modifier["use_custom_normals"] == true;
    if preserve_normals
        && !mesh["loop_normals"].as_array().unwrap().is_empty()
        && (level > 2 || mesh["smooth"].as_array().unwrap().iter().any(|v| v == true))
    {
        return Err("SUBSURF custom-normal preservation supports flat input faces at levels 1..2; disable use_custom_normals for higher levels or smooth input".into());
    }

    let mut normals: Vec<f32> = if preserve_normals {
        mesh["loop_normals"]
            .as_array()
            .unwrap()
            .iter()
            .flat_map(|c| vec3(c).map(|x| x as f32))
            .collect()
    } else {
        vec![]
    };
    if !normals.is_empty() {
        let mut start = 0;
        for (i, face) in faces.iter().enumerate() {
            let ids = face.as_array().unwrap();
            if mesh["smooth"][i] != true {
                let points: Vec<[f32; 3]> = ids
                    .iter()
                    .map(|v| vec3(&vertices[v.as_u64().unwrap() as usize]).map(|x| x as f32))
                    .collect();
                for corner in 0..ids.len() {
                    let at = (start + corner) * 3;
                    let normal = super::weighted_normals::quantize_corner(
                        &points,
                        corner,
                        [normals[at], normals[at + 1], normals[at + 2]],
                    );
                    normals[at..at + 3].copy_from_slice(&normal);
                }
            }
            start += ids.len();
        }
    }
    if (!colors.is_empty() && colors.len() != indices.len() * 4)
        || (!normals.is_empty() && normals.len() != indices.len() * 3)
    {
        return Err("SUBSURF corner attributes must match topology".into());
    }
    let input = Input {
        positions: positions.as_ptr(),
        crease_edges: crease_edges.as_ptr(),
        crease_weights: crease_weights.as_ptr(),
        vertex_creases: vertex_creases.as_ptr(),
        colors: if colors.is_empty() {
            ptr::null()
        } else {
            colors.as_ptr()
        },
        normals: if normals.is_empty() {
            ptr::null()
        } else {
            normals.as_ptr()
        },
        crease_count: crease_weights.len(),
        use_creases: i32::from(modifier["use_creases"] == true),
        face_counts: counts.as_ptr(),
        face_indices: indices.as_ptr(),
        uv_values: uv_values.as_ptr(),
        uv_indices: uv_indices.as_ptr(),
        uv_counts: uv_counts.as_ptr(),
        vertex_count: vertices.len(),
        face_count: faces.len(),
        corner_count: indices.len(),
        uv_layer_count: layers.len(),
    };
    let mut error = [0 as c_char; 1024];
    let raw = unsafe {
        hb_subdivide(
            &input,
            level as i32,
            i32::from(modifier["subdivision_type"] == "SIMPLE"),
            i32::from(modifier["use_limit_surface"] == true),
            i32::from(modifier["boundary_smooth"] == "PRESERVE_CORNERS"),
            error.as_mut_ptr(),
            error.len(),
        )
    };
    if raw.is_null() {
        return Err(unsafe { CStr::from_ptr(error.as_ptr()) }
            .to_string_lossy()
            .into_owned());
    }
    let result = ResultHandle(raw);
    let mut view = View {
        positions: ptr::null(),
        colors: ptr::null(),
        normals: ptr::null(),
        vertex_creases: ptr::null(),
        crease_edges: ptr::null(),
        crease_weights: ptr::null(),
        original_vertices: ptr::null(),
        crease_count: 0,
        faces: ptr::null(),
        source_faces: ptr::null(),
        uv: ptr::null(),
        vertex_count: 0,
        face_count: 0,
        uv_layer_count: 0,
    };
    unsafe {
        hb_subdivide_view(result.0, &mut view);
    }
    if view.vertex_count > 2_000_000
        || view.face_count > 2_000_000
        || view.uv_layer_count != layers.len()
    {
        return Err("SUBSURF invalid output bounds".into());
    }
    let (positions, indices, parents, uv) = unsafe {
        (
            copied(view.positions, view.vertex_count * 3),
            copied(view.faces, view.face_count * 4),
            copied(view.source_faces, view.face_count),
            copied(view.uv, view.face_count * 8 * view.uv_layer_count),
        )
    };
    if positions.iter().chain(&uv).any(|v| !v.is_finite())
        || indices
            .iter()
            .any(|&i| i < 0 || i as usize >= view.vertex_count)
        || parents.iter().any(|&i| i < 0 || i as usize >= faces.len())
    {
        return Err("SUBSURF generated invalid geometry".into());
    }
    let mut output = mesh.clone();
    output["vertices"] = json!(positions.as_chunks::<3>().0.iter().collect::<Vec<_>>());
    output["faces"] = json!(indices.as_chunks::<4>().0.iter().collect::<Vec<_>>());
    for field in ["material_indices", "smooth"] {
        output[field] = json!(
            parents
                .iter()
                .map(|&i| mesh[field][i as usize].clone())
                .collect::<Vec<_>>()
        );
    }
    let mut edges = BTreeMap::new();
    for face in indices.as_chunks::<4>().0.iter() {
        for i in 0..4 {
            let a = face[i];
            let b = face[(i + 1) % 4];
            edges.entry((a.min(b), a.max(b))).or_insert([a, b]);
        }
    }
    output["edges"] = json!(edges.into_values().collect::<Vec<_>>());
    for (i, layer) in output["uv_layers"]
        .as_array_mut()
        .unwrap()
        .iter_mut()
        .enumerate()
    {
        let stride = view.face_count * 8;
        layer["data"] = json!(
            uv[i * stride..(i + 1) * stride]
                .as_chunks::<2>()
                .0
                .iter()
                .collect::<Vec<_>>()
        );
    }
    if mesh.get("crease_vert").is_some() {
        output["crease_vert"] = json!(unsafe { copied(view.vertex_creases, view.vertex_count) });
    }
    if mesh.get("crease_edge").is_some() {
        let pairs = unsafe { copied(view.crease_edges, view.crease_count * 2) };
        let weights = unsafe { copied(view.crease_weights, view.crease_count) };
        let values: BTreeMap<_, _> = pairs
            .as_chunks::<2>()
            .0
            .iter()
            .zip(weights)
            .map(|(e, w)| ((e[0].min(e[1]), e[0].max(e[1])), w))
            .collect();
        output["crease_edge"] = json!(
            output["edges"]
                .as_array()
                .unwrap()
                .iter()
                .map(|e| {
                    let a = e[0].as_i64().unwrap() as i32;
                    let b = e[1].as_i64().unwrap() as i32;
                    *values.get(&(a.min(b), a.max(b))).unwrap_or(&0.)
                })
                .collect::<Vec<_>>()
        );
    }
    if !colors.is_empty() {
        output["colors"] = json!(
            unsafe { copied(view.colors, view.face_count * 16) }
                .as_chunks::<4>()
                .0
                .iter()
                .collect::<Vec<_>>()
        );
    }
    if !mesh["loop_normals"].as_array().unwrap().is_empty() {
        if preserve_normals {
            let normals = unsafe { copied(view.normals, view.face_count * 12) };
            let values: Vec<_> = normals
                .as_chunks::<3>()
                .0
                .iter()
                .map(|n| super::math::normalize([n[0] as f64, n[1] as f64, n[2] as f64]))
                .collect();
            let mut values = values;
            for (i, face) in output["faces"].as_array().unwrap().iter().enumerate() {
                if output["smooth"][i] != true {
                    let points: Vec<[f32; 3]> = face
                        .as_array()
                        .unwrap()
                        .iter()
                        .map(|v| {
                            vec3(&output["vertices"][v.as_u64().unwrap() as usize])
                                .map(|x| x as f32)
                        })
                        .collect();
                    for corner in 0..4 {
                        values[i * 4 + corner] = super::weighted_normals::quantize_corner(
                            &points,
                            corner,
                            values[i * 4 + corner].map(|x| x as f32),
                        )
                        .map(|x| x as f64);
                    }
                }
            }
            output["loop_normals"] = super::f32_value(&json!(values))?;
        } else {
            let vs: Vec<_> = output["vertices"]
                .as_array()
                .unwrap()
                .iter()
                .map(vec3)
                .collect();
            let fs = super::topology::faces(&output);
            let normals: Vec<_> = fs
                .iter()
                .map(|f| {
                    super::geometry::face_normal(&f.iter().map(|&v| vs[v]).collect::<Vec<_>>())
                })
                .collect();
            let mut vertex_normals = vec![[0.; 3]; vs.len()];
            for (f, &n) in fs.iter().zip(&normals) {
                for i in 0..f.len() {
                    let p = vs[f[i]];
                    let a = super::math::normalize(super::math::sub(
                        vs[f[(i + f.len() - 1) % f.len()]],
                        p,
                    ));
                    let b = super::math::normalize(super::math::sub(vs[f[(i + 1) % f.len()]], p));
                    let angle = super::math::dot(a, b).clamp(-1., 1.).acos();
                    vertex_normals[f[i]] =
                        super::math::add(vertex_normals[f[i]], super::math::mul(n, angle));
                }
            }
            let mut values = vec![];
            for (i, f) in fs.iter().enumerate() {
                for &v in f {
                    values.push(if output["smooth"][i] == true {
                        super::math::normalize(vertex_normals[v])
                    } else {
                        normals[i]
                    });
                }
            }
            output["loop_normals"] = super::f32_value(&json!(values))?;
        }
    }
    output.as_object_mut().unwrap().remove("deform_weights");
    Ok(output)
}

/// Refine disconnected wire components separately from manifold polygon surfaces.
pub fn apply(mesh: &Value, modifier: &Value, render: bool) -> Result<Value, String> {
    let level = modifier[if render { "render_levels" } else { "levels" }]
        .as_u64()
        .ok_or("Invalid SUBSURF level")? as usize;
    if level == 0 {
        return Ok(mesh.clone());
    }
    if level > 6 {
        return Err("SUBSURF supports levels zero through six".into());
    }
    if mesh["deform_weights"].as_array().is_some_and(|rows| {
        rows.iter()
            .any(|row| row.as_array().is_some_and(|r| !r.is_empty()))
    }) {
        return Err("SUBSURF vertex-group interpolation is outside this subset; subdivide before assigning groups".into());
    }
    let vertices = mesh["vertices"]
        .as_array()
        .ok_or("Invalid SUBSURF vertices")?;
    if vertices.len() > 2_000_000 {
        return Err("SUBSURF input exceeds two million vertices".into());
    }
    for face in mesh["faces"].as_array().ok_or("Invalid SUBSURF faces")? {
        if face.as_array().is_none_or(|f| {
            f.len() < 3
                || f.iter()
                    .any(|v| v.as_u64().is_none_or(|i| i as usize >= vertices.len()))
        }) {
            return Err("Invalid SUBSURF face indices".into());
        }
    }
    for edge in mesh["edges"].as_array().ok_or("Invalid SUBSURF edges")? {
        if edge.as_array().is_none_or(|e| {
            e.len() != 2
                || e.iter()
                    .any(|v| v.as_u64().is_none_or(|i| i as usize >= vertices.len()))
        }) || edge[0] == edge[1]
        {
            return Err("Invalid SUBSURF edge indices".into());
        }
    }
    let faces = super::topology::faces(mesh);
    let mut used = BTreeSet::new();
    let mut surface_edges = BTreeSet::new();
    for face in &faces {
        for i in 0..face.len() {
            used.insert(face[i]);
            let a = face[i];
            let b = face[(i + 1) % face.len()];
            surface_edges.insert((a.min(b), a.max(b)));
        }
    }
    let edges: Vec<[usize; 2]> = mesh["edges"]
        .as_array()
        .unwrap()
        .iter()
        .map(|e| {
            [
                e[0].as_u64().unwrap() as usize,
                e[1].as_u64().unwrap() as usize,
            ]
        })
        .collect();
    let loose: Vec<usize> = edges
        .iter()
        .enumerate()
        .filter_map(|(i, e)| {
            (!surface_edges.contains(&(e[0].min(e[1]), e[0].max(e[1])))).then_some(i)
        })
        .collect();
    if used.len() == vertices.len() && loose.is_empty() {
        return surface(mesh, modifier, render);
    }
    if loose
        .iter()
        .any(|&i| used.contains(&edges[i][0]) || used.contains(&edges[i][1]))
    {
        return Err("SUBSURF loose wires must be disconnected from polygon surfaces".into());
    }
    let segments = 1usize << level;
    if vertices.len() + loose.len() * (segments - 1) > 2_000_000 {
        return Err("SUBSURF loose geometry exceeds two million vertices".into());
    }
    let mut compact = mesh.clone();
    let mut map = vec![usize::MAX; vertices.len()];
    let mut compact_vertices = vec![];
    for &v in &used {
        if v >= vertices.len() {
            return Err("Invalid SUBSURF vertex index".into());
        }
        map[v] = compact_vertices.len();
        compact_vertices.push(vertices[v].clone());
    }
    compact["vertices"] = json!(compact_vertices);
    compact["faces"] = json!(
        faces
            .iter()
            .map(|f| f.iter().map(|&i| map[i]).collect::<Vec<_>>())
            .collect::<Vec<_>>()
    );
    let compact_edge_indices: Vec<_> = edges
        .iter()
        .enumerate()
        .filter_map(|(i, e)| {
            surface_edges
                .contains(&(e[0].min(e[1]), e[0].max(e[1])))
                .then_some(i)
        })
        .collect();
    compact["edges"] = json!(
        compact_edge_indices
            .iter()
            .map(|&i| [map[edges[i][0]], map[edges[i][1]]])
            .collect::<Vec<_>>()
    );
    if mesh.get("crease_vert").is_some() {
        compact["crease_vert"] = json!(
            used.iter()
                .map(|&i| mesh["crease_vert"][i].clone())
                .collect::<Vec<_>>()
        );
    }
    if mesh.get("crease_edge").is_some() {
        compact["crease_edge"] = json!(
            compact_edge_indices
                .iter()
                .map(|&i| mesh["crease_edge"][i].clone())
                .collect::<Vec<_>>()
        );
    }
    compact.as_object_mut().unwrap().remove("deform_weights");
    let mut out = surface(&compact, modifier, render)?;
    let mut vs = out["vertices"].as_array().unwrap().clone();
    let mut es = out["edges"].as_array().unwrap().clone();
    let mut vc = out["crease_vert"].as_array().cloned().unwrap_or_default();
    let mut ec = out["crease_edge"].as_array().cloned().unwrap_or_default();
    for (i, v) in vertices.iter().enumerate() {
        if !used.contains(&i) {
            map[i] = vs.len();
            vs.push(v.clone());
            if mesh.get("crease_vert").is_some() {
                vc.push(mesh["crease_vert"][i].clone());
            }
        }
    }
    let mut neighbors = vec![vec![]; vertices.len()];
    for &i in &loose {
        for &v in &edges[i] {
            neighbors[v].push(i);
        }
    }
    let simple = modifier["subdivision_type"] == "SIMPLE";
    for &i in &loose {
        let [a, b] = edges[i];
        let pa = vec3(&vertices[a]);
        let pb = vec3(&vertices[b]);
        let outer = |v: usize, p: [f64; 3], q: [f64; 3]| -> [f64; 3] {
            if neighbors[v].len() == 2 {
                let e = edges[*neighbors[v].iter().find(|&&e| e != i).unwrap()];
                vec3(&vertices[if e[0] == v { e[1] } else { e[0] }])
            } else {
                super::math::sub(super::math::mul(p, 2.), q)
            }
        };
        let p0 = outer(a, pa, pb);
        let p3 = outer(b, pb, pa);
        let mut previous = map[a];
        for step in 0..=segments {
            let t = step as f64 / segments as f64;
            let v = if step == 0 {
                map[a]
            } else if step == segments {
                map[b]
            } else {
                let n = vs.len();
                vs.push(Value::Null);
                if mesh.get("crease_vert").is_some() {
                    vc.push(json!(
                        num(&mesh["crease_vert"][a]) * (1. - t) + num(&mesh["crease_vert"][b]) * t
                    ));
                }
                n
            };
            let point: [f64; 3] = if simple {
                std::array::from_fn(|k| pa[k] * (1. - t) + pb[k] * t)
            } else {
                let t2 = t * t;
                let t3 = t2 * t;
                let w = [
                    (1. - t).powi(3) / 6.,
                    (3. * t3 - 6. * t2 + 4.) / 6.,
                    (-3. * t3 + 3. * t2 + 3. * t + 1.) / 6.,
                    t3 / 6.,
                ];
                std::array::from_fn(|k| p0[k] * w[0] + pa[k] * w[1] + pb[k] * w[2] + p3[k] * w[3])
            };
            vs[v] = super::f32_value(&json!(point))?;
            if step > 0 {
                es.push(json!([previous, v]));
                if mesh.get("crease_edge").is_some() {
                    ec.push(mesh["crease_edge"][i].clone());
                }
            }
            previous = v;
        }
    }
    if vs.len() > 2_000_000 {
        return Err("SUBSURF evaluated mesh exceeds two million vertices".into());
    }
    out["vertices"] = json!(vs);
    out["edges"] = json!(es);
    if mesh.get("crease_vert").is_some() {
        out["crease_vert"] = json!(vc);
    }
    if mesh.get("crease_edge").is_some() {
        out["crease_edge"] = json!(ec);
    }
    Ok(out)
}
