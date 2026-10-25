//! Manifold FFI and conversion between indexed polygon meshes and property triangles.
use super::{Value, geometry, math, vec3};
use serde_json::json;
use std::{
    collections::BTreeMap,
    ffi::{CStr, c_char, c_void},
    ptr,
};

#[repr(C)]
struct MeshView {
    properties: *const f64,
    triangles: *const u64,
    merge_from: *const u64,
    merge_to: *const u64,
    face_ids: *const u64,
    vertex_count: usize,
    triangle_count: usize,
    merge_count: usize,
    property_count: usize,
}
unsafe extern "C" {
    fn hb_manifold_boolean(
        a: *const MeshView,
        b: *const MeshView,
        operation: i32,
        error: *mut c_char,
        error_size: usize,
    ) -> *mut c_void;
    fn hb_manifold_view(result: *const c_void, view: *mut MeshView);
    fn hb_manifold_free(result: *mut c_void);
}
struct ResultHandle(*mut c_void);
impl Drop for ResultHandle {
    fn drop(&mut self) {
        unsafe {
            hb_manifold_free(self.0);
        }
    }
}

struct Input {
    properties: Vec<f64>,
    triangles: Vec<u64>,
    merge_from: Vec<u64>,
    merge_to: Vec<u64>,
    face_ids: Vec<u64>,
    property_count: usize,
}
impl Input {
    fn view(&self) -> MeshView {
        MeshView {
            properties: self.properties.as_ptr(),
            triangles: self.triangles.as_ptr(),
            merge_from: self.merge_from.as_ptr(),
            merge_to: self.merge_to.as_ptr(),
            face_ids: self.face_ids.as_ptr(),
            vertex_count: self.properties.len() / self.property_count,
            triangle_count: self.face_ids.len(),
            merge_count: self.merge_from.len(),
            property_count: self.property_count,
        }
    }
    fn new(mesh: &Value, _uv_names: &[String], face_offset: usize) -> Result<Self, String> {
        let vertices = mesh["vertices"].as_array().ok_or("Invalid BOOLEAN mesh")?;
        let faces = mesh["faces"].as_array().unwrap();
        if vertices.len() > 1_000_000 || faces.len() > 1_000_000 {
            return Err("BOOLEAN inputs are limited to 1,000,000 vertices/faces".into());
        }
        let mut out = Self {
            properties: vertices.iter().flat_map(vec3).collect(),
            triangles: vec![],
            merge_from: vec![],
            merge_to: vec![],
            face_ids: vec![],
            property_count: 3,
        };
        for (fi, face) in faces.iter().enumerate() {
            let indices: Vec<_> = face
                .as_array()
                .unwrap()
                .iter()
                .map(|v| v.as_u64().unwrap() as usize)
                .collect();
            let points: Vec<_> = indices.iter().map(|&i| vec3(&vertices[i])).collect();
            let triangles = if points.len() == 4 {
                let n = geometry::face_normal(&points);
                if math::dot(
                    math::cross(
                        math::sub(points[1], points[0]),
                        math::sub(points[2], points[0]),
                    ),
                    n,
                ) > 0.
                    && math::dot(
                        math::cross(
                            math::sub(points[2], points[0]),
                            math::sub(points[3], points[0]),
                        ),
                        n,
                    ) > 0.
                {
                    vec![[0, 1, 2], [0, 2, 3]]
                } else {
                    geometry::triangulate(&points)?
                }
            } else {
                geometry::triangulate(&points)?
            };
            for triangle in triangles {
                if out.face_ids.len() >= 2_000_000 {
                    return Err("BOOLEAN input triangulation exceeds 2,000,000 triangles".into());
                }
                for corner in triangle {
                    out.triangles.push(indices[corner] as u64);
                }
                out.face_ids.push((fi + face_offset) as u64);
            }
        }
        Ok(out)
    }
}

// Empty vectors may have null data pointers in C++; never form a Rust slice from them.
unsafe fn copy_array<T: Copy>(pointer: *const T, length: usize) -> Vec<T> {
    if length == 0 {
        vec![]
    } else {
        unsafe { std::slice::from_raw_parts(pointer, length).to_vec() }
    }
}

#[cfg(test)]
pub fn kernel(a: &Value, b: &Value, operation: &str) -> Result<Value, String> {
    kernel_with_solver(a, b, operation, "MANIFOLD")
}
pub fn kernel_with_solver(
    a: &Value,
    b: &Value,
    operation: &str,
    solver: &str,
) -> Result<Value, String> {
    let uv_names: Vec<_> = a["uv_layers"]
        .as_array()
        .unwrap()
        .iter()
        .map(|l| l["name"].as_str().unwrap().to_string())
        .collect();
    let input_a = Input::new(a, &uv_names, 0)?;
    let offset = a["faces"].as_array().unwrap().len();
    let input_b = Input::new(b, &uv_names, offset)?;
    let operation = match operation {
        "UNION" => 0,
        "DIFFERENCE" => 1,
        "INTERSECT" => 2,
        _ => return Err("Unknown BOOLEAN operation".into()),
    };
    let source_faces: Vec<_> = if operation == 0 {
        a["faces"]
            .as_array()
            .unwrap()
            .iter()
            .map(|face| {
                let points: Vec<_> = face
                    .as_array()
                    .unwrap()
                    .iter()
                    .map(|i| vec3(&a["vertices"][i.as_u64().unwrap() as usize]))
                    .collect();
                let mut bounds = geometry::Bounds::empty();
                for &p in &points {
                    bounds.include(p);
                }
                Ok(SourceFace {
                    normal: geometry::face_normal(&points),
                    triangles: geometry::triangulate(&points)?,
                    points,
                    bounds,
                })
            })
            .collect::<Result<_, String>>()?
    } else {
        vec![]
    };
    let index = FaceIndex::new(&source_faces, (0..source_faces.len()).collect());
    let swap_union = operation == 0
        && b["faces"].as_array().unwrap().iter().any(|face| {
            let points: Vec<_> = face
                .as_array()
                .unwrap()
                .iter()
                .map(|i| vec3(&b["vertices"][i.as_u64().unwrap() as usize]))
                .collect();
            let mut bounds = geometry::Bounds::empty();
            for &p in &points {
                bounds.include(p);
            }
            index.has_coplanar(
                &source_faces,
                &points,
                geometry::face_normal(&points),
                bounds,
            )
        });
    let mut error = [0 as c_char; 1024];
    let view_a = input_a.view();
    let view_b = input_b.view();
    let raw = unsafe {
        hb_manifold_boolean(
            if swap_union { &view_b } else { &view_a },
            if swap_union { &view_a } else { &view_b },
            operation,
            error.as_mut_ptr(),
            error.len(),
        )
    };
    if raw.is_null() {
        return Err(unsafe { CStr::from_ptr(error.as_ptr()) }
            .to_string_lossy()
            .into_owned());
    }
    let handle = ResultHandle(raw);
    let mut view = MeshView {
        properties: ptr::null(),
        triangles: ptr::null(),
        merge_from: ptr::null(),
        merge_to: ptr::null(),
        face_ids: ptr::null(),
        vertex_count: 0,
        triangle_count: 0,
        merge_count: 0,
        property_count: 0,
    };
    unsafe {
        hb_manifold_view(handle.0, &mut view);
    }
    let (properties, triangles, from, to, ids) = unsafe {
        (
            copy_array(view.properties, view.vertex_count * view.property_count),
            copy_array(view.triangles, 3 * view.triangle_count),
            copy_array(view.merge_from, view.merge_count),
            copy_array(view.merge_to, view.merge_count),
            copy_array(view.face_ids, view.triangle_count),
        )
    };
    let mut parents: Vec<_> = (0..view.vertex_count).collect();
    fn root(parents: &mut [usize], mut i: usize) -> usize {
        while parents[i] != i {
            parents[i] = parents[parents[i]];
            i = parents[i];
        }
        i
    }
    for (a, b) in from.into_iter().zip(to) {
        let x = root(&mut parents, a as usize);
        let y = root(&mut parents, b as usize);
        parents[x.max(y)] = x.min(y);
    }
    let mut vertices = vec![];
    let mut remap = vec![0; view.vertex_count];
    for i in 0..view.vertex_count {
        let r = root(&mut parents, i);
        if r == i {
            remap[i] = vertices.len();
            vertices.push(json!(
                &properties[i * view.property_count..i * view.property_count + 3]
            ));
        } else {
            remap[i] = remap[r];
        }
    }
    let mut visits = 0;
    // Remove triangle-internal edges per original polygon. Indices on
    // boundary edges identify output corners; UVs are interpolated per source polygon.
    let mut face_normals: BTreeMap<usize, [f64; 3]> = BTreeMap::new();
    let mut face_triangles: BTreeMap<usize, Vec<[usize; 3]>> = BTreeMap::new();
    let mut boundaries: BTreeMap<usize, BTreeMap<(usize, usize), usize>> = BTreeMap::new();
    for (triangle, &id) in triangles.as_chunks::<3>().0.iter().zip(&ids) {
        let p: Vec<_> = triangle
            .iter()
            .map(|&i| vec3(&vertices[remap[i as usize]]))
            .collect();
        let normal = math::cross(math::sub(p[1], p[0]), math::sub(p[2], p[0]));
        let id = if operation == 0 {
            index
                .find(&source_faces, &p, math::normalize(normal), &mut visits)?
                .unwrap_or(id as usize)
        } else {
            id as usize
        };
        face_triangles.entry(id).or_default().push([
            triangle[0] as usize,
            triangle[1] as usize,
            triangle[2] as usize,
        ]);
        let accumulated = face_normals.entry(id).or_insert([0.; 3]);
        *accumulated = math::add(*accumulated, normal);
        let edges = boundaries.entry(id).or_default();
        for k in 0..3 {
            let x = remap[triangle[k] as usize];
            let y = remap[triangle[(k + 1) % 3] as usize];
            if edges.remove(&(y, x)).is_none()
                && edges.insert((x, y), triangle[k] as usize).is_some()
            {
                return Err("BOOLEAN produced overlapping polygon boundaries".into());
            }
        }
    }
    let mut partitions = vec![];
    for (id, edges) in boundaries {
        let loops = boundary_loops(&edges)?;
        let has_hole = loops.iter().any(|loop_| {
            let normal = loop_.iter().fold([0.; 3], |n, &(x, y, _)| {
                math::add(n, math::cross(vec3(&vertices[x]), vec3(&vertices[y])))
            });
            math::dot(normal, face_normals[&id]) < 0.
        });
        if has_hole {
            for part in decompose(&face_triangles[&id], &remap)? {
                partitions.push((id, part));
            }
        } else {
            partitions.push((id, edges));
        }
    }
    let mut neighbors = vec![std::collections::BTreeSet::new(); vertices.len()];
    for (_, edges) in &partitions {
        for &(a, b) in edges.keys() {
            neighbors[a].insert(b);
            neighbors[b].insert(a);
        }
    }
    let redundant: Vec<_> = neighbors
        .iter()
        .enumerate()
        .map(|(i, ns)| {
            if ns.len() != 2 {
                return false;
            }
            let ns: Vec<_> = ns.iter().copied().collect();
            let a = math::sub(vec3(&vertices[ns[0]]), vec3(&vertices[i]));
            let b = math::sub(vec3(&vertices[ns[1]]), vec3(&vertices[i]));
            math::dot(a, b) < 0.
                && math::length(math::cross(a, b)) <= 1e-6 * math::length(a) * math::length(b)
        })
        .collect();
    let starts = |mesh: &Value| {
        let mut at = 0;
        mesh["faces"]
            .as_array()
            .unwrap()
            .iter()
            .map(|f| {
                let start = at;
                at += f.as_array().unwrap().len();
                start
            })
            .collect::<Vec<_>>()
    };
    let starts_a = starts(a);
    let starts_b = starts(b);
    let mut interpolation_work = 0_usize;
    let mut output = a.clone();
    let mut faces = vec![];
    let mut materials = vec![];
    let mut smooth = vec![];
    let mut uv = vec![vec![]; uv_names.len()];
    let custom_normals = [a, b]
        .iter()
        .any(|m| !m["loop_normals"].as_array().unwrap().is_empty());
    let custom_colors = [a, b]
        .iter()
        .any(|m| !m["colors"].as_array().unwrap().is_empty());
    let mut normals = vec![];
    let mut colors = vec![];
    for (id, mut edges) in partitions {
        let (source, face) = if id < offset {
            (a, id)
        } else {
            (b, id - offset)
        };
        if source["faces"].get(face).is_none() {
            return Err("BOOLEAN lost source face provenance".into());
        }
        let loop_start = if id < offset {
            starts_a[face]
        } else {
            starts_b[face]
        };
        while let Some((&(start, _), _)) = edges.first_key_value() {
            let mut current = start;
            let mut polygon = vec![];
            let mut corners = vec![];
            loop {
                let choices: Vec<_> = edges
                    .range((current, 0)..=(current, usize::MAX))
                    .map(|(&key, &value)| (key, value))
                    .collect();
                if choices.len() != 1 {
                    return Err("BOOLEAN polygon boundary is not a simple loop".into());
                }
                let ((x, y), corner) = choices[0];
                edges.remove(&(x, y));
                if !redundant[x] {
                    polygon.push(x);
                    corners.push(corner);
                }
                current = y;
                if current == start {
                    break;
                }
                if polygon.len() > view.triangle_count * 3 {
                    return Err("BOOLEAN polygon boundary did not close".into());
                }
            }
            if polygon.len() < 3 {
                return Err("BOOLEAN produced a degenerate polygon".into());
            }
            let mut normal = [0.; 3];
            for k in 0..polygon.len() {
                normal = math::add(
                    normal,
                    math::cross(
                        vec3(&vertices[polygon[k]]),
                        vec3(&vertices[polygon[(k + 1) % polygon.len()]]),
                    ),
                );
            }
            if math::dot(normal, face_normals[&id]) <= 0. {
                return Err("BOOLEAN polygon reconstruction produced an invalid orientation; split the source face".into());
            }
            faces.push(json!(polygon));
            let material = source["material_indices"][face].as_u64().unwrap() as usize;
            materials
                .push(material.min(a["materials"].as_array().unwrap().len().saturating_sub(1)));
            smooth.push(source["smooth"][face].clone());
            for &corner in &corners {
                interpolation_work += source["faces"][face].as_array().unwrap().len()
                    * (usize::from(custom_normals) + usize::from(custom_colors));
                if interpolation_work > 20_000_000 {
                    return Err("BOOLEAN corner interpolation exceeds its work limit".into());
                }
                let point = vec3(&vertices[remap[corner]]);
                if custom_normals {
                    let normal = math::normalize(normal);
                    let value = if source["loop_normals"].as_array().unwrap().is_empty() {
                        normal
                    } else {
                        let n = interpolate_attribute::<3>(
                            source,
                            face,
                            loop_start,
                            &source["loop_normals"],
                            point,
                        )?;
                        let points: Vec<_> = source["faces"][face]
                            .as_array()
                            .unwrap()
                            .iter()
                            .map(|i| vec3(&source["vertices"][i.as_u64().unwrap() as usize]))
                            .collect();
                        math::mul(
                            math::normalize(n),
                            if math::dot(normal, geometry::face_normal(&points)) < 0. {
                                -1.
                            } else {
                                1.
                            },
                        )
                    };
                    normals.push(value);
                }
                if custom_colors {
                    colors.push(if source["colors"].as_array().unwrap().is_empty() {
                        if solver == "MANIFOLD" {
                            [0.; 4]
                        } else {
                            [1.; 4]
                        }
                    } else {
                        interpolate_attribute::<4>(
                            source,
                            face,
                            loop_start,
                            &source["colors"],
                            point,
                        )?
                    });
                }
            }
            for (layer, values) in uv.iter_mut().enumerate() {
                for &corner in &corners {
                    let point = vec3(&vertices[remap[corner]]);
                    interpolation_work += source["faces"][face].as_array().unwrap().len();
                    if interpolation_work > 20_000_000 {
                        return Err("BOOLEAN UV interpolation exceeds its work limit; split large source polygons".into());
                    }
                    values.push(json!(interpolate_uv(
                        source,
                        face,
                        loop_start,
                        &uv_names[layer],
                        point
                    )?));
                }
            }
        }
    }
    let mut used = vec![false; vertices.len()];
    for face in &faces {
        for v in face.as_array().unwrap() {
            used[v.as_u64().unwrap() as usize] = true;
        }
    }
    let mut compact = vec![];
    let mut map = vec![0; vertices.len()];
    for (i, v) in vertices.into_iter().enumerate() {
        if used[i] {
            map[i] = compact.len();
            compact.push(v);
        }
    }
    let vertices = compact;
    for face in &mut faces {
        for v in face.as_array_mut().unwrap() {
            *v = json!(map[v.as_u64().unwrap() as usize]);
        }
    }
    let mut edges = BTreeMap::new();
    for face in &faces {
        let vs = face.as_array().unwrap();
        for i in 0..vs.len() {
            let a = vs[i].as_u64().unwrap();
            let b = vs[(i + 1) % vs.len()].as_u64().unwrap();
            edges.entry((a.min(b), a.max(b))).or_insert(json!([a, b]));
        }
    }
    let mut slots = a["materials"].as_array().unwrap().clone();
    if slots.is_empty() {
        slots.push(Value::Null);
    }
    let operand_slots = b["materials"].as_array().unwrap();
    if operand_slots.is_empty() && !slots.contains(&Value::Null) {
        slots.push(Value::Null);
    }
    for slot in operand_slots {
        if !slots.contains(slot) {
            slots.push(slot.clone());
        }
    }
    if solver != "MANIFOLD"
        && a["materials"].as_array().unwrap().is_empty()
        && b["materials"].as_array().unwrap().is_empty()
    {
        slots.clear();
    }
    output["materials"] = json!(slots);
    output["vertices"] = super::f32_value(&json!(vertices))?;
    output["faces"] = json!(faces);
    output["edges"] = json!(edges.into_values().collect::<Vec<_>>());
    output["material_indices"] = json!(materials);
    output["smooth"] = json!(smooth);
    output["loop_normals"] = super::f32_value(&json!(normals))?;
    output["colors"] = super::f32_value(&json!(colors))?;
    if faces.is_empty() {
        output["uv_layers"] = json!([]);
        output["active_uv"] = json!(0);
    } else {
        for (i, layer) in output["uv_layers"]
            .as_array_mut()
            .unwrap()
            .iter_mut()
            .enumerate()
        {
            layer["data"] = super::f32_value(&json!(uv[i]))?;
        }
    }
    Ok(output)
}

type Boundary = BTreeMap<(usize, usize), usize>;
type BoundaryLoop = Vec<(usize, usize, usize)>;
fn boundary_loops(edges: &Boundary) -> Result<Vec<BoundaryLoop>, String> {
    let mut remaining = edges.clone();
    let mut loops = vec![];
    while let Some((&(start, _), _)) = remaining.first_key_value() {
        let mut current = start;
        let mut cycle = vec![];
        loop {
            let mut choices = remaining.range((current, 0)..=(current, usize::MAX));
            let Some((&(x, y), &corner)) = choices.next() else {
                return Err("BOOLEAN open polygon boundary".into());
            };
            if choices.next().is_some() {
                return Err("BOOLEAN pinched polygon boundary; split the source face".into());
            }
            remaining.remove(&(x, y));
            cycle.push((x, y, corner));
            current = y;
            if current == start {
                break;
            }
        }
        loops.push(cycle);
    }
    Ok(loops)
}
// Dissolve internal triangle edges while retaining simple polygon boundaries.
// A region with holes stops at several polygons instead of filling the hole.
fn decompose(triangles: &[[usize; 3]], remap: &[usize]) -> Result<Vec<Boundary>, String> {
    let mut groups: Vec<_> = triangles
        .iter()
        .map(|t| {
            (0..3)
                .map(|k| ((remap[t[k]], remap[t[(k + 1) % 3]]), t[k]))
                .collect::<Boundary>()
        })
        .collect();
    let mut work = 0;
    loop {
        let mut merged = false;
        'outer: for i in 0..groups.len() {
            for j in i + 1..groups.len() {
                work += 1;
                if work > 2_000_000 {
                    return Err("BOOLEAN hole decomposition exceeds its work limit; split large source faces".into());
                }
                if !groups[i]
                    .keys()
                    .any(|&(a, b)| groups[j].contains_key(&(b, a)))
                {
                    continue;
                }
                let mut joined = groups[i].clone();
                let mut valid = true;
                for (&(a, b), &corner) in &groups[j] {
                    if joined.remove(&(b, a)).is_none() && joined.insert((a, b), corner).is_some() {
                        valid = false;
                        break;
                    }
                }
                if valid
                    && boundary_loops(&joined).is_ok_and(|ls| ls.len() == 1 && ls[0].len() >= 3)
                {
                    groups[i] = joined;
                    groups.remove(j);
                    merged = true;
                    break 'outer;
                }
            }
        }
        if !merged {
            break;
        }
    }
    Ok(groups)
}

struct SourceFace {
    points: Vec<math::V3>,
    triangles: Vec<[usize; 3]>,
    normal: math::V3,
    bounds: geometry::Bounds,
}
struct FaceIndex {
    bounds: geometry::Bounds,
    children: Option<Box<[FaceIndex; 2]>>,
    faces: Vec<usize>,
}
impl FaceIndex {
    fn new(faces: &[SourceFace], mut ids: Vec<usize>) -> Self {
        let bounds = ids
            .iter()
            .fold(geometry::Bounds::empty(), |b, &i| b.union(faces[i].bounds));
        if ids.len() <= 8 {
            return Self {
                bounds,
                children: None,
                faces: ids,
            };
        }
        let ext = bounds.extent();
        let axis = (0..3).max_by(|&a, &b| ext[a].total_cmp(&ext[b])).unwrap();
        ids.sort_unstable_by(|&a, &b| {
            faces[a].bounds.center()[axis].total_cmp(&faces[b].bounds.center()[axis])
        });
        let right = ids.split_off(ids.len() / 2);
        Self {
            bounds,
            children: Some(Box::new([Self::new(faces, ids), Self::new(faces, right)])),
            faces: vec![],
        }
    }
    fn has_coplanar(
        &self,
        faces: &[SourceFace],
        points: &[math::V3],
        normal: math::V3,
        bounds: geometry::Bounds,
    ) -> bool {
        if self.bounds.distance(bounds) > 1e-7 {
            return false;
        }
        if let Some(children) = &self.children {
            return children
                .iter()
                .any(|child| child.has_coplanar(faces, points, normal, bounds));
        }
        self.faces.iter().any(|&i| {
            let f = &faces[i];
            f.bounds.distance(bounds) < 1e-7
                && math::dot(f.normal, normal) > 1. - 1e-8
                && points
                    .iter()
                    .all(|&p| math::dot(math::sub(p, f.points[0]), f.normal).abs() < 1e-7)
        })
    }
    fn find(
        &self,
        faces: &[SourceFace],
        points: &[math::V3],
        normal: math::V3,
        visits: &mut usize,
    ) -> Result<Option<usize>, String> {
        *visits += 1;
        if *visits > 10_000_000 {
            return Err(
                "BOOLEAN coplanar attribute matching exceeds its work limit; simplify operands"
                    .into(),
            );
        }
        let contains = |b: geometry::Bounds| {
            points
                .iter()
                .all(|p| (0..3).all(|k| p[k] >= b.min[k] - 1e-7 && p[k] <= b.max[k] + 1e-7))
        };
        if !contains(self.bounds) {
            return Ok(None);
        }
        if let Some(children) = &self.children {
            let a = children[0].find(faces, points, normal, visits)?;
            let b = children[1].find(faces, points, normal, visits)?;
            return Ok(a.into_iter().chain(b).min());
        }
        Ok(self
            .faces
            .iter()
            .copied()
            .filter(|&i| {
                let f = &faces[i];
                contains(f.bounds)
                    && math::dot(normal, f.normal) > 1. - 1e-8
                    && points.iter().all(|&p| {
                        math::dot(math::sub(p, f.points[0]), f.normal).abs() < 1e-7
                            && f.triangles.iter().any(|t| {
                                (0..3).all(|k| {
                                    let a = f.points[t[k]];
                                    let b = f.points[t[(k + 1) % 3]];
                                    math::dot(
                                        math::cross(math::sub(b, a), math::sub(p, a)),
                                        f.normal,
                                    ) >= -1e-8
                                })
                            })
                    })
            })
            .min())
    }
}

// Mean-value coordinates interpolate a polygon's corner attributes without
// introducing triangulation-dependent seams. Exact vertices/edges use limits.
fn interpolate_uv(
    mesh: &Value,
    face: usize,
    start: usize,
    name: &str,
    point: [f64; 3],
) -> Result<[f64; 2], String> {
    let Some(layer) = mesh["uv_layers"]
        .as_array()
        .unwrap()
        .iter()
        .find(|l| l["name"] == name)
    else {
        return Ok([0.; 2]);
    };
    interpolate_attribute::<2>(mesh, face, start, &layer["data"], point)
}
fn interpolate_attribute<const N: usize>(
    mesh: &Value,
    face: usize,
    start: usize,
    values: &Value,
    point: [f64; 3],
) -> Result<[f64; N], String> {
    let indices = mesh["faces"][face].as_array().unwrap();
    let positions: Vec<_> = indices
        .iter()
        .map(|i| vec3(&mesh["vertices"][i.as_u64().unwrap() as usize]))
        .collect();
    let offsets: Vec<_> = positions.iter().map(|&v| math::sub(v, point)).collect();
    let distances: Vec<_> = offsets.iter().map(|&v| math::length(v)).collect();
    let value = |i: usize| std::array::from_fn::<_, N, _>(|k| super::num(&values[start + i][k]));
    let normal = geometry::face_normal(&positions);
    let mut half = vec![0.; indices.len()];
    for i in 0..indices.len() {
        if distances[i] < 1e-9 {
            return Ok(value(i));
        }
        let j = (i + 1) % indices.len();
        let cross = math::dot(math::cross(offsets[i], offsets[j]), normal);
        let dot = math::dot(offsets[i], offsets[j]);
        if cross.abs() < 1e-12 && dot <= 0. {
            let t = distances[i] / (distances[i] + distances[j]);
            return Ok(std::array::from_fn(|k| {
                value(i)[k] * (1. - t) + value(j)[k] * t
            }));
        }
        half[i] = cross / (distances[i] * distances[j] + dot);
    }
    let weights: Vec<_> = (0..indices.len())
        .map(|i| (half[(i + indices.len() - 1) % indices.len()] + half[i]) / distances[i])
        .collect();
    let sum: f64 = weights.iter().sum();
    if !sum.is_finite() || sum.abs() < 1e-20 {
        return Err("BOOLEAN cannot interpolate this degenerate UV polygon".into());
    }
    Ok(std::array::from_fn(|k| {
        weights
            .iter()
            .enumerate()
            .map(|(i, w)| w * value(i)[k])
            .sum::<f64>()
            / sum
    }))
}

#[cfg(test)]
mod tests {
    use super::*;
    #[test]
    fn manifold_box_cut() {
        let make = |x: f64| json!({"vertices":[[-1.+x,-1.,-1.],[-1.+x,-1.,1.],[-1.+x,1.,-1.],[-1.+x,1.,1.],[1.+x,-1.,-1.],[1.+x,-1.,1.],[1.+x,1.,-1.],[1.+x,1.,1.]],"faces":[[0,1,3,2],[2,3,7,6],[6,7,5,4],[4,5,1,0],[2,6,4,0],[7,3,1,5]],"edges":[],"materials":[],"material_indices":[0,0,0,0,0,0],"smooth":[false,false,false,false,false,false],"uv_layers":[],"active_uv":0,"loop_normals":[],"colors":[]});
        let output = kernel(&make(0.), &make(1.), "DIFFERENCE").unwrap();
        assert_eq!(output["vertices"].as_array().unwrap().len(), 8);
        assert_eq!(output["faces"].as_array().unwrap().len(), 6);
        assert!(
            output["vertices"]
                .as_array()
                .unwrap()
                .iter()
                .all(|p| p[0].as_f64().unwrap() <= 0.)
        );
    }
}
