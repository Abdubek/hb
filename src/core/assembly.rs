//! Object-mode joining. The active mesh is first; other meshes follow scene order.
use super::{Scene, Value, f32_value, id, math, vec3};
use serde_json::json;

pub fn join(scene: &mut Scene, active: u64) -> Result<bool, String> {
    let selected: Vec<_> = scene
        .linked_ids()
        .into_iter()
        .filter(|key| scene.object(*key).is_ok_and(|o| o["selected"] == true))
        .collect();
    if !selected.contains(&active) {
        return Err("Join requires a selected active mesh".into());
    }
    let mut ordered = vec![active];
    ordered.extend(selected.into_iter().filter(|key| *key != active));
    let mut meshes = vec![];
    let inverse = math::inverse(scene.world(active)?)?;
    let mut vertex_count = 0;
    let mut face_count = 0;
    for key in &ordered {
        let obj = scene.object(*key)?;
        let mesh = scene.mesh(obj).ok_or("Join requires mesh objects")?;
        if obj["modifiers"].as_array().is_some_and(|m| !m.is_empty()) {
            return Err("Apply modifiers before joining meshes".into());
        }
        for field in ["shape_keys", "crease_edge", "crease_vert", "face_strength"] {
            if mesh.get(field).is_some() {
                return Err("Join supports ordinary mesh attributes and UV layers only".into());
            }
        }
        if mesh.get("deform_weights").is_some() {
            return Err("Join on weighted meshes is outside the contract; join geometry before assigning vertex groups".into());
        }
        if !mesh["loop_normals"].as_array().unwrap().is_empty()
            || !mesh["colors"].as_array().unwrap().is_empty()
        {
            return Err("Join does not support custom normals or corner colors".into());
        }
        let material_count = mesh["materials"].as_array().unwrap().len();
        if material_count > 0
            && mesh["material_indices"]
                .as_array()
                .unwrap()
                .iter()
                .any(|i| i.as_u64().unwrap() as usize >= material_count)
        {
            return Err("Join requires valid material slot indices".into());
        }
        vertex_count += mesh["vertices"].as_array().unwrap().len();
        face_count += mesh["faces"].as_array().unwrap().len();
        if vertex_count > 2_000_000 || face_count > 2_000_000 {
            return Err("Join exceeds the 2,000,000 vertex/face resource limit".into());
        }
        let matrix = if *key == active {
            math::IDENTITY
        } else {
            math::matmul(inverse, scene.world(*key)?)
        };
        meshes.push((mesh.clone(), matrix));
    }
    if vertex_count == meshes[0].0["vertices"].as_array().unwrap().len() {
        return Ok(false);
    }
    let mut joined = meshes[0].0.clone();
    let mut vertices = vec![];
    let mut edges = vec![];
    let mut faces = vec![];
    let mut smooth = vec![];
    let mut material_indices = vec![];
    let mut materials = joined["materials"].as_array().unwrap().clone();
    let has_materials = meshes
        .iter()
        .any(|(m, _)| !m["materials"].as_array().unwrap().is_empty());
    let mut uv_names = vec![];
    for (mesh, _) in &meshes {
        for layer in mesh["uv_layers"].as_array().unwrap() {
            let name = layer["name"].clone();
            if !uv_names.contains(&name) {
                uv_names.push(name);
            }
        }
    }
    if joined["uv_layers"].as_array().unwrap().is_empty()
        && let Some((source, _)) = meshes
            .iter()
            .find(|(m, _)| !m["uv_layers"].as_array().unwrap().is_empty())
    {
        let name = &source["uv_layers"][source["active_uv"].as_u64().unwrap() as usize]["name"];
        joined["active_uv"] = json!(uv_names.iter().position(|n| n == name).unwrap());
    }
    let mut uv_data: Vec<Vec<Value>> = vec![vec![]; uv_names.len()];
    for (mesh_index, (mesh, matrix)) in meshes.iter().enumerate() {
        let offset = vertices.len();
        for p in mesh["vertices"].as_array().unwrap() {
            vertices.push(if mesh_index == 0 {
                p.clone()
            } else {
                f32_value(&json!(math::point(*matrix, vec3(p))))?
            });
        }
        for edge in mesh["edges"].as_array().unwrap() {
            edges.push(json!(
                edge.as_array()
                    .unwrap()
                    .iter()
                    .map(|v| v.as_u64().unwrap() as usize + offset)
                    .collect::<Vec<_>>()
            ));
        }
        let source_materials = mesh["materials"].as_array().unwrap();
        let mut slots = vec![];
        for mat in source_materials {
            let index = materials.iter().position(|m| m == mat).unwrap_or_else(|| {
                materials.push(mat.clone());
                materials.len() - 1
            });
            slots.push(index);
        }
        for (i, face) in mesh["faces"].as_array().unwrap().iter().enumerate() {
            faces.push(json!(
                face.as_array()
                    .unwrap()
                    .iter()
                    .map(|v| v.as_u64().unwrap() as usize + offset)
                    .collect::<Vec<_>>()
            ));
            smooth.push(mesh["smooth"][i].clone());
            let source_index = mesh["material_indices"][i].as_u64().unwrap() as usize;
            let mapped = if !has_materials {
                0
            } else if let Some(index) = slots.get(source_index) {
                *index
            } else {
                materials
                    .iter()
                    .position(Value::is_null)
                    .unwrap_or_else(|| {
                        materials.push(Value::Null);
                        materials.len() - 1
                    })
            };
            material_indices.push(mapped);
        }
        let loops: usize = mesh["faces"]
            .as_array()
            .unwrap()
            .iter()
            .map(|f| f.as_array().unwrap().len())
            .sum();
        for (i, name) in uv_names.iter().enumerate() {
            if let Some(layer) = mesh["uv_layers"]
                .as_array()
                .unwrap()
                .iter()
                .find(|l| &l["name"] == name)
            {
                uv_data[i].extend(layer["data"].as_array().unwrap().iter().cloned());
            } else {
                uv_data[i].extend(std::iter::repeat_n(json!([0., 0.]), loops));
            }
        }
    }
    joined["vertices"] = json!(vertices);
    joined["edges"] = json!(edges);
    joined["faces"] = json!(faces);
    joined["smooth"] = json!(smooth);
    joined["material_indices"] = json!(material_indices);
    joined["materials"] = json!(materials);
    joined["uv_layers"] = json!(
        uv_names
            .into_iter()
            .zip(uv_data)
            .map(|(name, data)| json!({"name":name,"data":data}))
            .collect::<Vec<_>>()
    );
    let mesh_key = id(&joined);
    *scene.get_mut("meshes", mesh_key)? = joined;
    for key in ordered.into_iter().skip(1) {
        scene.remove("objects", key, true)?;
    }
    Ok(true)
}
