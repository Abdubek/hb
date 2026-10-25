//! Non-destructive modeling evaluation, shared by queries, raster and export.
use super::{Scene, Value, f32_value, id, num, text, vec3};
use serde_json::json;
use std::borrow::Cow;

pub fn validate(stack: &Value) -> Result<(), String> {
    let stack = stack.as_array().ok_or("Modifier stack must be an array")?;
    if stack.len() > 64 {
        return Err("At most 64 modifiers per object".into());
    }
    let mut names = std::collections::BTreeSet::new();
    let boolean = |m: &Value, key: &str| -> Result<(), String> {
        if m[key].is_boolean() {
            Ok(())
        } else {
            Err(format!("Modifier {key} must be a boolean"))
        }
    };
    let number = |m: &Value, key: &str, min: f64, max: f64| -> Result<(), String> {
        if m[key]
            .as_f64()
            .is_some_and(|v| v.is_finite() && v >= min && v <= max)
        {
            Ok(())
        } else {
            Err(format!("Modifier {key} must be finite in {min}..{max}"))
        }
    };
    for m in stack {
        if !names.insert(text(&m["name"])) {
            return Err("Duplicate modifier name".into());
        }
        for key in ["show_viewport", "show_render"] {
            boolean(m, key)?;
        }
        match text(&m["type"]) {
            "WEIGHTED_NORMAL" => {
                if !["FACE_AREA", "CORNER_ANGLE", "FACE_AREA_WITH_ANGLE"]
                    .contains(&text(&m["mode"]))
                {
                    return Err("Unsupported weighted-normal mode".into());
                }
                if m["weight"].as_i64().is_none_or(|v| !(1..=100).contains(&v)) {
                    return Err("WEIGHTED_NORMAL weight must be an integer in 1..100".into());
                }
                number(m, "thresh", 0., 10.)?;
                for key in ["keep_sharp", "use_face_influence", "invert_vertex_group"] {
                    boolean(m, key)?;
                }
                if m["vertex_group"].as_str().is_none_or(|s| s.len() > 63) {
                    return Err(
                        "WEIGHTED_NORMAL vertex-group name requires at most 63 UTF-8 bytes".into(),
                    );
                }
            }
            "DISPLACE" => {
                if !["NORMAL", "X", "Y", "Z"].contains(&text(&m["direction"]))
                    || m["space"] != "LOCAL"
                    || m["texture_coords"] != "LOCAL"
                    || !(m["texture"].is_null() || m["texture"].as_u64().is_some())
                {
                    return Err("DISPLACE supports local NORMAL/X/Y/Z directions, LOCAL texture coordinates".into());
                }
                boolean(m, "invert_vertex_group")?;
                if m["vertex_group"].as_str().is_none_or(|s| s.len() > 63) {
                    return Err("DISPLACE vertex-group name requires at most 63 UTF-8 bytes".into());
                }
                number(m, "strength", -(f32::MAX as f64), f32::MAX as f64)?;
                number(m, "mid_level", 0., 1.)?;
            }
            "SUBSURF" => {
                if m.get("use_custom_normals").is_some_and(|v| !v.is_boolean()) {
                    return Err("SUBSURF use_custom_normals must be boolean".into());
                }
                if !["CATMULL_CLARK", "SIMPLE"].contains(&text(&m["subdivision_type"]))
                    || !["ALL", "PRESERVE_CORNERS"].contains(&text(&m["boundary_smooth"]))
                    || m["quality"] != 3
                    || m["uv_smooth"] != "PRESERVE_BOUNDARIES"
                {
                    return Err("SUBSURF supports CATMULL_CLARK/SIMPLE, quality 3 and PRESERVE_BOUNDARIES UV smoothing".into());
                }
                for key in ["levels", "render_levels"] {
                    if m[key].as_u64().is_none_or(|v| v > 6) {
                        return Err("SUBSURF supports levels 0..6".into());
                    }
                }
                for key in [
                    "use_limit_surface",
                    "use_creases",
                    "show_only_control_edges",
                ] {
                    boolean(m, key)?;
                }
            }
            "BOOLEAN" => {
                if !["EXACT", "FAST", "MANIFOLD"].contains(&text(&m["solver"]))
                    || !["DIFFERENCE", "UNION", "INTERSECT"].contains(&text(&m["operation"]))
                    || !["OBJECT", "COLLECTION"].contains(&text(&m["operand_type"]))
                    || m["material_mode"] != "INDEX"
                    || m["use_self"] != false
                    || m["use_hole_tolerant"] != false
                    || m["double_threshold"].as_f64() != Some(1e-6_f32 as f64)
                    || !(m["object"].is_null() || m["object"].as_u64().is_some())
                    || !(m["collection"].is_null() || m["collection"].as_u64().is_some())
                {
                    return Err("BOOLEAN supports EXACT/FAST/MANIFOLD closed-solid operands with INDEX material mapping and default advanced options".into());
                }
            }
            "WELD" => {
                if !["ALL", "CONNECTED"].contains(&text(&m["mode"])) {
                    return Err("WELD mode must be ALL or CONNECTED".into());
                }
                boolean(m, "loose_edges")?;
                boolean(m, "invert_vertex_group")?;
                if m["vertex_group"].as_str().is_none_or(|s| s.len() > 63) {
                    return Err("WELD requires a vertex-group name up to 63 UTF-8 bytes".into());
                }
                number(m, "merge_threshold", 0., f32::MAX as f64)?;
            }
            "ARRAY" => {
                if m["fit_type"] != "FIXED_COUNT" {
                    return Err(
                        "ARRAY supports fixed count; other fit modes are outside the manifest contract".into(),
                    );
                }
                if m["count"]
                    .as_u64()
                    .is_none_or(|n| !(1..=10000).contains(&n))
                {
                    return Err("ARRAY count must be 1..10000".into());
                }
                for key in ["relative_offset_displace", "constant_offset_displace"] {
                    let a = m[key].as_array().ok_or("ARRAY offset must be a vector")?;
                    if a.len() != 3 || a.iter().any(|v| v.as_f64().is_none_or(|v| !v.is_finite())) {
                        return Err("ARRAY offset must have three finite coordinates".into());
                    }
                }
                for key in [
                    "use_relative_offset",
                    "use_constant_offset",
                    "use_merge_vertices",
                    "use_object_offset",
                ] {
                    boolean(m, key)?;
                }
                for key in ["offset_object", "start_cap", "end_cap"] {
                    if !(m[key].is_null() || m[key].as_u64().is_some()) {
                        return Err("ARRAY object references must be IDs or null".into());
                    }
                }
                if m.get("use_merge_vertices_cap").is_some() {
                    boolean(m, "use_merge_vertices_cap")?;
                }
                if m.get("merge_threshold").is_some() {
                    number(m, "merge_threshold", 0., 1.)?;
                }
            }
            "MIRROR" => {
                if m["use_axis"]
                    .as_array()
                    .is_none_or(|a| a.len() != 3 || a.iter().any(|v| !v.is_boolean()))
                {
                    return Err("MIRROR use_axis requires three booleans".into());
                }
                for key in ["use_mirror_merge", "use_clip"] {
                    boolean(m, key)?;
                }
                number(m, "merge_threshold", 0., 1.)?;
                for key in ["use_bisect_axis", "use_bisect_flip_axis"] {
                    if let Some(value) = m.get(key)
                        && value
                            .as_array()
                            .is_none_or(|v| v.len() != 3 || v.iter().any(|v| !v.is_boolean()))
                    {
                        return Err("MIRROR axis masks need three booleans".into());
                    }
                }
                for key in ["use_mirror_u", "use_mirror_v", "use_mirror_vertex_groups"] {
                    if m.get(key).is_some() {
                        boolean(m, key)?;
                    }
                }
                if m.get("bisect_threshold").is_some() {
                    number(m, "bisect_threshold", 0., 1.)?;
                }
                for key in ["offset_u", "offset_v", "mirror_offset_u", "mirror_offset_v"] {
                    if m.get(key).is_some() {
                        number(m, key, -1., 1.)?;
                    }
                }
                if !(m["mirror_object"].is_null() || m["mirror_object"].as_u64().is_some()) {
                    return Err("MIRROR mirror_object must be an object ID or null".into());
                }
            }
            "TRIANGULATE" => {
                if ![
                    "BEAUTY",
                    "FIXED",
                    "FIXED_ALTERNATE",
                    "SHORTEST_DIAGONAL",
                    "LONGEST_DIAGONAL",
                ]
                .contains(&text(&m["quad_method"]))
                    || !["BEAUTY", "CLIP"].contains(&text(&m["ngon_method"]))
                {
                    return Err("Unsupported TRIANGULATE quad or ngon method".into());
                }
                boolean(m, "keep_custom_normals")?;
                if m["min_vertices"]
                    .as_u64()
                    .is_none_or(|n| !(4..=i32::MAX as u64).contains(&n))
                {
                    return Err("TRIANGULATE min_vertices must be at least four".into());
                }
            }
            "BEVEL" => {
                if !["EDGES", "VERTICES"].contains(&text(&m["affect"]))
                    || m["offset_type"] != "OFFSET"
                    || !["NONE", "ANGLE"].contains(&text(&m["limit_method"]))
                    || m["profile"].as_f64() != Some(0.5)
                    || m["loop_slide"] != true
                    || m["harden_normals"] != false
                    || m["material"].as_i64() != Some(-1)
                {
                    return Err("BEVEL supports EDGES/VERTICES with OFFSET, circular profile, ANGLE/NONE and default advanced settings".into());
                }
                boolean(m, "use_clamp_overlap")?;
                number(m, "width", 0., 1e6)?;
                number(m, "angle_limit", 0., std::f64::consts::PI + 1e-6)?;
                if m["segments"].as_u64().is_none_or(|n| !(1..=8).contains(&n)) {
                    return Err("BEVEL supports 1..8 segments".into());
                }
            }
            "SOLIDIFY" => {
                if !["EXTRUDE", "NON_MANIFOLD"].contains(&text(&m["solidify_mode"])) {
                    return Err("SOLIDIFY supports EXTRUDE and NON_MANIFOLD".into());
                }
                for key in [
                    "use_rim",
                    "use_rim_only",
                    "use_even_offset",
                    "use_quality_normals",
                ] {
                    boolean(m, key)?;
                }
                number(m, "thickness_clamp", 0., 100.)?;
                if m.get("thickness_vertex_group").is_some() {
                    number(m, "thickness_vertex_group", 0., 1.)?;
                }
                if m.get("invert_vertex_group").is_some() {
                    boolean(m, "invert_vertex_group")?;
                }
                for key in ["vertex_group", "shell_vertex_group", "rim_vertex_group"] {
                    if m.get(key).is_some() && m[key].as_str().is_none_or(|s| s.len() > 63) {
                        return Err(
                            "SOLIDIFY requires vertex-group names up to 63 UTF-8 bytes".into()
                        );
                    }
                }
                number(m, "thickness", -10000., 10000.)?;
                number(m, "offset", -1., 1.)?;
                for key in ["material_offset", "material_offset_rim"] {
                    if m[key]
                        .as_i64()
                        .is_none_or(|v| !(-32768..=32767).contains(&v))
                    {
                        return Err("Invalid SOLIDIFY material offset".into());
                    }
                }
            }
            _ => return Err("Unsupported modifier type".into()),
        }
    }
    Ok(())
}

pub fn apply(mesh: &Value, modifier: &Value) -> Result<Value, String> {
    validate(&json!([modifier]))?;
    match text(&modifier["type"]) {
        "ARRAY" => array(mesh, modifier),
        "WELD" => super::weld::apply(&json!({}), mesh, modifier),
        "SUBSURF" => super::subsurf::apply(mesh, modifier, false),
        "BEVEL" => super::bevel::apply(mesh, modifier),
        "WEIGHTED_NORMAL" => super::weighted_normals::apply(&Value::Null, mesh, modifier),
        "MIRROR" => super::topology::mirror(mesh, modifier),
        "TRIANGULATE" => super::topology::triangulate(mesh, modifier),
        "SOLIDIFY" => super::solidify::apply(&json!({}), mesh, modifier),
        _ => Err("Unsupported modifier".into()),
    }
}

pub fn array(mesh: &Value, modifier: &Value) -> Result<Value, String> {
    validate(&json!([modifier]))?;
    let count = modifier["count"].as_u64().unwrap() as usize;
    let vs = mesh["vertices"].as_array().ok_or("Invalid mesh vertices")?;
    if vs.len().saturating_mul(count) > 2_000_000
        || mesh["faces"]
            .as_array()
            .unwrap()
            .len()
            .saturating_mul(count)
            > 2_000_000
    {
        return Err(
            "Evaluated ARRAY exceeds the 2,000,000 vertex/face resource limit; reduce count".into(),
        );
    }
    let mut lo = [f64::INFINITY; 3];
    let mut hi = [f64::NEG_INFINITY; 3];
    for v in vs {
        let p = vec3(v);
        for axis in 0..3 {
            lo[axis] = lo[axis].min(p[axis]);
            hi[axis] = hi[axis].max(p[axis]);
        }
    }
    let step: [f32; 3] = std::array::from_fn(|axis| {
        let relative = if modifier["use_relative_offset"] == true && !vs.is_empty() {
            ((hi[axis] - lo[axis]) as f32)
                * (num(&modifier["relative_offset_displace"][axis]) as f32)
        } else {
            0.
        };
        relative
            + if modifier["use_constant_offset"] == true {
                num(&modifier["constant_offset_displace"][axis]) as f32
            } else {
                0.
            }
    });
    let mut out = mesh.clone();
    let mut vertices = Vec::with_capacity(vs.len() * count);
    for copy in 0..count {
        for v in vs {
            vertices.push(json!(std::array::from_fn::<_, 3, _>(|axis| (num(&v[axis])
                as f32)
                + (copy as f32) * step[axis])));
        }
    }
    out["vertices"] = f32_value(&json!(vertices))?;
    for key in ["edges", "faces"] {
        let mut values = vec![];
        for copy in 0..count {
            for face in mesh[key].as_array().ok_or("Invalid mesh topology")? {
                values.push(json!(
                    face.as_array()
                        .unwrap()
                        .iter()
                        .map(|i| i.as_u64().unwrap() + (copy * vs.len()) as u64)
                        .collect::<Vec<_>>()
                ));
            }
        }
        out[key] = json!(values);
    }
    for key in ["material_indices", "smooth", "loop_normals", "colors"] {
        let values = mesh[key].as_array().ok_or("Invalid mesh attributes")?;
        out[key] = json!(
            (0..count)
                .flat_map(|_| values.iter().cloned())
                .collect::<Vec<_>>()
        );
    }
    if let Some(weights) = mesh.get("deform_weights").and_then(Value::as_array) {
        out["deform_weights"] = json!(
            (0..count)
                .flat_map(|_| weights.iter().cloned())
                .collect::<Vec<_>>()
        );
    }
    for layer in out["uv_layers"].as_array_mut().ok_or("Invalid UV layers")? {
        let data = layer["data"].as_array().ok_or("Invalid UV data")?;
        layer["data"] = json!(
            (0..count)
                .flat_map(|_| data.iter().cloned())
                .collect::<Vec<_>>()
        );
    }
    Ok(out)
}

pub fn apply_in_scene(
    scene: &Scene,
    object: &Value,
    mesh: &Value,
    modifier: &Value,
    render: bool,
    visited: &mut Vec<u64>,
) -> Result<Value, String> {
    validate(&json!([modifier]))?;
    if mesh
        .get("shape_keys")
        .is_some_and(|v| v.as_array().is_some_and(|a| !a.is_empty()))
    {
        return Err(
            "Modifier evaluation on shape-key meshes is outside the static shape-editing subset"
                .into(),
        );
    }
    if mesh.get("face_strength").is_some()
        && !["WEIGHTED_NORMAL", "DISPLACE"].contains(&text(&modifier["type"]))
    {
        return Err("Face-strength interpolation through geometry modifiers is outside the verified subset; assign strengths after geometry modifiers".into());
    }

    if mesh.get("deform_weights").is_some()
        && ![
            "ARRAY",
            "MIRROR",
            "SOLIDIFY",
            "TRIANGULATE",
            "WELD",
            "DISPLACE",
            "WEIGHTED_NORMAL",
        ]
        .contains(&text(&modifier["type"]))
    {
        return Err(format!(
            "{} on weighted meshes is outside the current contract; apply it before assigning vertex groups",
            text(&modifier["type"])
        ));
    }
    if modifier["type"] == "ARRAY" {
        return super::array::apply(scene, object, mesh, modifier, render, visited);
    }
    if modifier["type"] == "MIRROR" {
        return super::mirror::apply(scene, object, mesh, modifier);
    }
    if modifier["type"] == "WELD" {
        return super::weld::apply(object, mesh, modifier);
    }
    if modifier["type"] == "SOLIDIFY" {
        return super::solidify::apply(object, mesh, modifier);
    }
    if modifier["type"] == "WEIGHTED_NORMAL" {
        return super::weighted_normals::apply(object, mesh, modifier);
    }
    if modifier["type"] == "DISPLACE" {
        return super::displace::apply(scene, object, mesh, modifier);
    }
    if modifier["type"] == "SUBSURF" {
        return super::subsurf::apply(mesh, modifier, render);
    }
    if modifier["type"] != "BOOLEAN" {
        return apply(mesh, modifier);
    }
    let mut operands = vec![];
    if modifier["operand_type"] == "COLLECTION" {
        if let Some(key) = modifier["collection"].as_u64() {
            scene.get("collections", key)?;
            scene.walk_collection(key, &mut std::collections::BTreeSet::new(), &mut operands);
        }
        operands.retain(|&key| {
            key != id(object)
                && scene
                    .object(key)
                    .is_ok_and(|o| o["data"]["kind"] == "meshes")
        });
        if operands.len() > 64 {
            return Err("BOOLEAN collection supports at most 64 mesh operands".into());
        }
        if modifier["solver"] == "FAST" && modifier["operation"] == "INTERSECT" {
            return Err(
                "BOOLEAN FAST collection INTERSECT is unsupported by Blender; use EXACT".into(),
            );
        }
    } else if let Some(key) = modifier["object"].as_u64() {
        operands.push(key);
    }
    let mut output = mesh.clone();
    for key in operands {
        let operand = scene.object(key)?;
        let mut other = evaluate(scene, operand, render, visited)?
            .ok_or("BOOLEAN operand must be a mesh object")?
            .into_owned();
        let transform = super::math::matmul(
            super::math::inverse(scene.world(id(object))?)?,
            scene.world(key)?,
        );
        let determinant = super::math::dot(
            [transform[0][0], transform[1][0], transform[2][0]],
            super::math::cross(
                [transform[0][1], transform[1][1], transform[2][1]],
                [transform[0][2], transform[1][2], transform[2][2]],
            ),
        );
        if determinant < 0. && modifier["solver"] == "MANIFOLD" {
            return Err("BOOLEAN reflected relative transforms require EXACT or FAST; Blender MANIFOLD yields an inconsistent oriented solid".into());
        }
        if determinant.abs() <= 1e-14 {
            return Err("BOOLEAN requires nonsingular operand transforms".into());
        }
        other["vertices"] = f32_value(&json!(
            other["vertices"]
                .as_array()
                .unwrap()
                .iter()
                .map(|v| super::math::point(transform, vec3(v)))
                .collect::<Vec<_>>()
        ))?;
        let inverse = super::math::inverse(transform)?;
        other["loop_normals"] = f32_value(&json!(
            other["loop_normals"]
                .as_array()
                .unwrap()
                .iter()
                .map(|v| {
                    let n = vec3(v);
                    super::math::normalize(std::array::from_fn(|i| {
                        (0..3).map(|j| inverse[j][i] * n[j]).sum()
                    }))
                })
                .collect::<Vec<_>>()
        ))?;
        if determinant < 0. {
            let source = super::topology::faces(&other);
            let starts = super::topology::starts(&source);
            let faces = source
                .iter()
                .enumerate()
                .map(|(i, f)| super::topology::Face {
                    vertices: f.iter().rev().copied().collect(),
                    corners: (starts[i]..starts[i] + f.len()).rev().collect(),
                    source: i,
                    material: None,
                })
                .collect::<Vec<_>>();
            other = super::topology::assemble(
                &other,
                other["vertices"].as_array().unwrap().clone(),
                &faces,
                other["edges"].as_array().unwrap().clone(),
            )?;
        }
        output = super::boolean::kernel_with_solver(
            &output,
            &other,
            text(&modifier["operation"]),
            text(&modifier["solver"]),
        )?;
    }
    Ok(output)
}

pub fn evaluated_mesh<'a>(
    scene: &'a Scene,
    object: &Value,
    render: bool,
) -> Result<Option<Cow<'a, Value>>, String> {
    evaluate(scene, object, render, &mut vec![])
}

pub(crate) fn evaluate<'a>(
    scene: &'a Scene,
    object: &Value,
    render: bool,
    visited: &mut Vec<u64>,
) -> Result<Option<Cow<'a, Value>>, String> {
    if visited.contains(&id(object)) || visited.len() >= 64 {
        return Err("BOOLEAN dependency cycle or depth over 64; use an independent operand without a reference back to this object".into());
    }
    let Some(mesh) = scene.mesh(object) else {
        return Ok(None);
    };
    let Some(stack) = object.get("modifiers") else {
        return Ok(Some(Cow::Borrowed(mesh)));
    };
    validate(stack)?;
    visited.push(id(object));
    let mut output = Cow::Borrowed(mesh);
    for modifier in stack.as_array().unwrap() {
        if modifier[if render {
            "show_render"
        } else {
            "show_viewport"
        }] == false
        {
            continue;
        }
        output = Cow::Owned(apply_in_scene(
            scene, object, &output, modifier, render, visited,
        )?);
    }
    visited.pop();
    Ok(Some(output))
}

pub fn for_export(scene: &Scene) -> Result<Option<Scene>, String> {
    if !scene
        .objects
        .iter()
        .any(|o| o["modifiers"].as_array().is_some_and(|s| !s.is_empty()))
    {
        return Ok(None);
    }
    let mut out = scene.clone();
    for object in &scene.objects {
        if object["modifiers"].as_array().is_none_or(|s| s.is_empty()) {
            continue;
        }
        // Blender's glTF export_apply evaluates the viewport dependency graph.
        if let Some(mesh) = evaluated_mesh(scene, object, false)? {
            let mut mesh = mesh.into_owned();
            let name = text(&mesh["name"]).to_string();
            mesh.as_object_mut().unwrap().remove("id");
            mesh.as_object_mut().unwrap().remove("name");
            let key = out.create("meshes", &name, mesh)?;
            out.get_mut("objects", id(object))?["data"] = json!({"kind":"meshes","id":key});
        }
        out.get_mut("objects", id(object))?
            .as_object_mut()
            .unwrap()
            .remove("modifiers");
    }
    Ok(Some(out))
}

/// References contribute data-block users and must be cleared on deletion.
pub fn object_reference_fields(modifier: &Value) -> &'static [&'static str] {
    match text(&modifier["type"]) {
        "BOOLEAN" => &["object"],
        "ARRAY" => &["offset_object", "start_cap", "end_cap"],
        "MIRROR" => &["mirror_object"],
        _ => &[],
    }
}
