//! Material evaluation shared by preview and asset exporters.
use super::{
    Value,
    math::{V3, mul},
    num, text, vec3, vec4,
};

#[derive(Clone)]
pub struct Material {
    pub transmission: f64,
    pub ior: f64,
    pub principled: Value,
    pub base: [f64; 4],
    pub metallic: f64,
    pub roughness: f64,
    pub emission: V3,
    pub emission_image: Option<u64>,
    pub color_image: Option<u64>,
    pub alpha_image: Option<u64>,
    pub normal_image: Option<u64>,
    pub normal_strength: f64,
    pub mr_image: Option<u64>,
    pub alpha_mode: String,
    pub cutoff: f64,
}
impl Default for Material {
    fn default() -> Self {
        Self {
            transmission: 0.,
            ior: 1.5,
            principled: Value::Null,
            base: [0.65, 0.68, 0.72, 1.],
            metallic: 0.,
            roughness: 0.5,
            emission: [0.; 3],
            emission_image: None,
            color_image: None,
            alpha_image: None,
            normal_image: None,
            normal_strength: 1.,
            mr_image: None,
            alpha_mode: "OPAQUE".into(),
            cutoff: 0.5,
        }
    }
}
impl Material {
    pub fn from_asset(v: &Value) -> Result<Self, String> {
        let mut m = Self {
            base: vec4(&v["diffuse_color"]),
            metallic: num(&v["metallic"]),
            roughness: num(&v["roughness"]),
            ..Self::default()
        };
        if v["use_nodes"] == true {
            let ns = v["nodes"].as_array().ok_or("Missing material nodes")?;
            let links = v["links"].as_array().ok_or("Missing material links")?;
            let pi = ns
                .iter()
                .position(|n| n["type"] == "ShaderNodeBsdfPrincipled");
            let oi = ns
                .iter()
                .position(|n| n["type"] == "ShaderNodeOutputMaterial");
            if let (Some(pi), Some(oi)) = (pi, oi) {
                if !links
                    .iter()
                    .any(|l| l["source"] == pi && l["target"] == oi && l["input"] == "Surface")
                {
                    m.base = [0., 0., 0., 1.];
                    return Ok(m);
                }
                let p = &ns[pi]["inputs"];
                m.principled = p.clone();
                m.transmission = num(&p["Transmission Weight"]);
                m.ior = p["IOR"].as_f64().unwrap_or(1.5);
                m.base = vec4(&p["Base Color"]);
                m.base[3] = num(&p["Alpha"]);
                m.metallic = num(&p["Metallic"]);
                m.roughness = num(&p["Roughness"]);
                m.emission = mul(vec3(&p["Emission Color"]), num(&p["Emission Strength"]));
                for l in links {
                    if l["target"] != pi {
                        continue;
                    }
                    let src = &ns[l["source"].as_u64().unwrap_or(0) as usize];
                    if src["type"] == "ShaderNodeTexImage" && src["image"].is_null() {
                        return Err("Linked image texture has no image; assign node.image before preview/export".into());
                    }
                    match text(&l["input"]) {
                        "Base Color" => {
                            m.color_image = src["image"].as_u64();
                            m.base[0] = 1.;
                            m.base[1] = 1.;
                            m.base[2] = 1.;
                        }
                        "Emission Color" => {
                            m.emission_image = src["image"].as_u64();
                            m.emission = [num(&p["Emission Strength"]); 3];
                        }
                        "Alpha" => {
                            m.alpha_image = src["image"].as_u64();
                            m.base[3] = 1.;
                        }
                        "Normal" => {
                            m.normal_strength = num(&src["inputs"]["Strength"]);
                            for n in links {
                                if n["target"] == l["source"] && n["input"] == "Color" {
                                    m.normal_image = ns[n["source"].as_u64().unwrap_or(0) as usize]
                                        ["image"]
                                        .as_u64();
                                }
                            }
                        }
                        _ => {}
                    }
                }
            } else {
                m.base = [0., 0., 0., 1.];
            }
        }
        // Import metadata represents glTF's factors and channels without pretending to be bpy nodes.
        if let Some(g) = v.get("gltf") {
            m.transmission = num(&g["transmission"]);
            m.ior = g["ior"].as_f64().unwrap_or(1.5);
            m.principled = g.get("principled").cloned().unwrap_or(Value::Null);
            m.base = vec4(&g["base"]);
            m.metallic = num(&g["metallic"]);
            m.roughness = num(&g["roughness"]);
            m.emission = vec3(&g["emission"]);
            m.emission_image = g["emission_image"].as_u64();
            m.color_image = g["color_image"].as_u64();
            m.alpha_image = m.color_image;
            m.normal_image = g["normal_image"].as_u64();
            m.normal_strength = g["normal_strength"].as_f64().unwrap_or(1.);
            m.mr_image = g["mr_image"].as_u64();
            m.alpha_mode = g["alpha_mode"].as_str().unwrap_or("OPAQUE").into();
            m.cutoff = g["cutoff"].as_f64().unwrap_or(0.5);
        } else if m.base[3] < 1. || m.alpha_image.is_some() {
            m.alpha_mode = "BLEND".into();
        }
        Ok(m)
    }
}

/// Standard glTF transmission/refraction plus lossless metadata for additional
/// Principled data inputs whose shading is outside the fixed raster preview.
pub fn export_parameters(source: &Value, material: &Material, out: &mut Value) -> Vec<String> {
    use serde_json::json;
    let mut extensions = out["extensions"].as_object().cloned().unwrap_or_default();
    if material.transmission != 0. {
        extensions.insert(
            "KHR_materials_transmission".into(),
            json!({"transmissionFactor":material.transmission}),
        );
    }
    if material.ior != 1.5 {
        extensions.insert("KHR_materials_ior".into(), json!({"ior":material.ior}));
    }
    if !extensions.is_empty() {
        out["extensions"] = Value::Object(extensions);
    }
    let defaults: Value = serde_json::from_str(include_str!("principled_defaults.json")).unwrap();
    let mut extra = serde_json::Map::new();
    if let Some(inputs) = material.principled.as_object() {
        for (key, value) in inputs {
            if [
                "Base Color",
                "Metallic",
                "Roughness",
                "Alpha",
                "Emission Color",
                "Emission Strength",
                "Normal",
                "IOR",
                "Transmission Weight",
            ]
            .contains(&key.as_str())
            {
                continue;
            }
            if value != &defaults[key] {
                extra.insert(key.clone(), value.clone());
            }
        }
    }
    let mut warnings = vec![];
    if material.transmission != 0. {
        warnings.push(format!("Material {}: transmission/IOR are exported as standard glTF parameters; the fixed raster preview does not simulate refraction.",text(&source["name"])));
    }
    if !extra.is_empty() {
        warnings.push(format!("Material {}: additional Principled inputs are preserved in extras.hb_principled; their scattering is outside the fixed preview and standard transmission/IOR export subset.",text(&source["name"])));
        out["extras"] = json!({"hb_principled":extra});
    }
    warnings
}

/// Convert a single Blender UV -> POINT Mapping -> Image Texture chain into
/// the glTF texture transform (which uses the opposite vertical UV convention).
pub fn texture_transform(source: &Value, input: &str) -> Result<Option<Value>, String> {
    use serde_json::json;
    if source["use_nodes"] != true {
        return Ok(None);
    }
    let Some(nodes) = source["nodes"].as_array() else {
        return Ok(None);
    };
    let Some(links) = source["links"].as_array() else {
        return Ok(None);
    };
    let Some(pi) = nodes
        .iter()
        .position(|n| n["type"] == "ShaderNodeBsdfPrincipled")
    else {
        return Ok(None);
    };
    let Some(image_link) = links
        .iter()
        .find(|l| l["target"] == pi && l["input"] == input)
    else {
        return Ok(None);
    };
    let mut image = image_link["source"]
        .as_u64()
        .ok_or("Invalid image node link")? as usize;
    if nodes
        .get(image)
        .is_some_and(|n| n["type"] == "ShaderNodeNormalMap")
    {
        let Some(link) = links
            .iter()
            .find(|l| l["target"] == image && l["input"] == "Color")
        else {
            return Ok(None);
        };
        image = link["source"]
            .as_u64()
            .ok_or("Invalid Normal Map image link")? as usize;
    }
    if nodes
        .get(image)
        .is_none_or(|n| n["type"] != "ShaderNodeTexImage")
    {
        return Ok(None);
    }
    let Some(vector_link) = links
        .iter()
        .find(|l| l["target"] == image && l["input"] == "Vector")
    else {
        return Ok(None);
    };
    let index = vector_link["source"]
        .as_u64()
        .ok_or("Invalid texture coordinate link")? as usize;
    let node = nodes.get(index).ok_or("Missing texture coordinate node")?;
    if node["type"] == "ShaderNodeTexCoord" && vector_link["output"] == "UV" {
        return Ok(None);
    }
    if node["type"] != "ShaderNodeMapping" {
        return Err("Image coordinates require UV or a POINT Mapping node".into());
    }
    let mapping_link = links
        .iter()
        .find(|l| l["target"] == index && l["input"] == "Vector")
        .ok_or("Connect Texture Coordinate UV to Mapping Vector before export")?;
    let coord = nodes
        .get(mapping_link["source"].as_u64().ok_or("Invalid UV link")? as usize)
        .ok_or("Missing UV node")?;
    if coord["type"] != "ShaderNodeTexCoord" || mapping_link["output"] != "UV" {
        return Err("Mapping coordinates must come from Texture Coordinate UV".into());
    }
    let p = &node["inputs"];
    let t = vec3(&p["Location"]);
    let r = vec3(&p["Rotation"]);
    let s = vec3(&p["Scale"]);
    if t == [0.; 3] && r == [0.; 3] && s == [1.; 3] {
        return Ok(None);
    }
    if t[2] != 0. || r[0] != 0. || r[1] != 0. || s[2] != 1. {
        return Err("Use planar UV Mapping: XY location/scale, Z rotation, scale Z=1".into());
    }
    Ok(Some(
        json!({"offset":[t[0]-s[1]*r[2].sin(),1.-t[1]-s[1]*r[2].cos()],"rotation":r[2],"scale":[s[0],s[1]]}),
    ))
}

pub fn validate_import(source: &Value) -> Result<(), String> {
    for (extension, field, minimum, maximum) in [
        ("KHR_materials_transmission", "transmissionFactor", 0., 1.),
        ("KHR_materials_ior", "ior", 1., f64::MAX),
    ] {
        if let Some(value) = source["extensions"][extension].get(field)
            && value
                .as_f64()
                .is_none_or(|v| !v.is_finite() || v < minimum || v > maximum)
        {
            return Err(format!(
                "Invalid {extension}.{field}; use a finite value in {minimum}..{maximum}"
            ));
        }
    }
    let Some(extra) = source["extras"].get("hb_principled") else {
        return Ok(());
    };
    let extra = extra
        .as_object()
        .ok_or("hb_principled must be an object of named numeric inputs")?;
    let defaults: Value = serde_json::from_str(include_str!("principled_defaults.json")).unwrap();
    for (key, value) in extra {
        let default = defaults.get(key).ok_or_else(|| {
            format!("Unsupported Principled input {key}; use the named inputs listed in hb api")
        })?;
        let valid = if let Some(vector) = default.as_array() {
            value.as_array().is_some_and(|a| {
                a.len() == vector.len() && a.iter().all(|x| x.as_f64().is_some_and(f64::is_finite))
            })
        } else {
            value.as_f64().is_some_and(f64::is_finite)
        };
        if !valid {
            return Err(format!(
                "Invalid Principled input {key}; use its documented finite scalar or vector value"
            ));
        }
    }
    Ok(())
}

/// Lossless glTF texture binding, separate from the fixed preview sampler.
pub fn import_binding(doc: &Value, info: &Value) -> Result<Value, String> {
    use serde_json::json;
    if info.is_null() {
        return Ok(Value::Null);
    }
    let tex = info["index"]
        .as_u64()
        .and_then(|i| doc["textures"].get(i as usize))
        .ok_or("Invalid texture index")?;
    let mut sampler = json!({});
    if let Some(index) = tex.get("sampler") {
        sampler = index
            .as_u64()
            .and_then(|i| doc["samplers"].get(i as usize))
            .ok_or("Invalid texture sampler index")?
            .clone();
    }
    for field in ["wrapS", "wrapT"] {
        if sampler
            .get(field)
            .is_some_and(|x| ![Some(10497), Some(33071), Some(33648)].contains(&x.as_u64()))
        {
            return Err("Texture wrapping must be REPEAT, CLAMP_TO_EDGE or MIRRORED_REPEAT".into());
        }
    }
    for (field, allowed) in [
        ("magFilter", &[9728, 9729][..]),
        ("minFilter", &[9728, 9729, 9984, 9985, 9986, 9987][..]),
    ] {
        if sampler
            .get(field)
            .is_some_and(|x| x.as_u64().is_none_or(|v| !allowed.contains(&v)))
        {
            return Err(format!(
                "Invalid texture {field}; use a glTF sampler filter"
            ));
        }
    }
    let mut binding = info.clone();
    binding
        .as_object_mut()
        .ok_or("Texture info must be an object")?
        .remove("index");
    binding["sampler"] = sampler;
    for source in [&binding, &binding["extensions"]["KHR_texture_transform"]] {
        if source
            .get("texCoord")
            .is_some_and(|x| x.as_u64().is_none_or(|i| i > 7))
        {
            return Err("Texture coordinates require TEXCOORD_0 through TEXCOORD_7".into());
        }
    }
    if let Some(exts) = binding.get("extensions") {
        for key in exts
            .as_object()
            .ok_or("Texture extensions must be an object")?
            .keys()
        {
            if key != "KHR_texture_transform" {
                return Err(format!(
                    "Unsupported texture extension {key}; use KHR_texture_transform"
                ));
            }
        }
    }
    if let Some(transform) = binding["extensions"].get("KHR_texture_transform") {
        let values = transform
            .as_object()
            .ok_or("Texture transform must be an object")?;
        for (key, value) in values {
            let valid = match key.as_str() {
                "offset" | "scale" => value.as_array().is_some_and(|a| {
                    a.len() == 2 && a.iter().all(|v| v.as_f64().is_some_and(f64::is_finite))
                }),
                "rotation" => value.as_f64().is_some_and(f64::is_finite),
                "texCoord" => value.as_u64().is_some_and(|v| v <= 7),
                _ => false,
            };
            if !valid {
                return Err(format!(
                    "Invalid texture transform {key}; use finite offset/scale pairs, rotation and optional texCoord 0..7"
                ));
            }
        }
    }
    Ok(binding)
}

fn render_uv(scene: &super::Scene, source: &Value) -> Result<u64, String> {
    let mut channels = std::collections::BTreeSet::new();
    for mesh in &scene.meshes {
        if mesh["materials"]
            .as_array()
            .is_some_and(|a| a.contains(&source["id"]))
        {
            let channel = mesh["render_uv"].as_u64().unwrap_or(0);
            if channel > 7
                || (channel > 0
                    && mesh["uv_layers"]
                        .as_array()
                        .is_none_or(|a| channel as usize >= a.len()))
            {
                return Err("Use an existing render UV layer in channels 0..7".into());
            }
            channels.insert(channel);
        }
    }
    if channels.len() > 1 {
        return Err("Shared textured material uses different active render UV layers; duplicate the material for each UV channel before glTF export".into());
    }
    Ok(channels.first().copied().unwrap_or(0))
}

pub fn texture_binding(scene: &super::Scene, source: &Value, role: &str) -> Result<Value, String> {
    use serde_json::json;
    if let Some(binding) =
        source["gltf"]["bindings"].get(if role == "alpha" { "base_color" } else { role })
    {
        return Ok(binding.clone());
    }
    let input = match role {
        "base_color" => "Base Color",
        "alpha" => "Alpha",
        "normal" => "Normal",
        "emission" => "Emission Color",
        _ => return Ok(json!({})),
    };
    let mut binding = json!({});
    let uv = render_uv(scene, source)?;
    if uv > 0 {
        binding["texCoord"] = json!(uv);
    }
    if let Some(transform) = texture_transform(source, input)? {
        binding["extensions"] = json!({"KHR_texture_transform":transform});
    }
    if let (Some(nodes), Some(links)) = (source["nodes"].as_array(), source["links"].as_array())
        && let Some(pi) = nodes
            .iter()
            .position(|n| n["type"] == "ShaderNodeBsdfPrincipled")
        && let Some(link) = links
            .iter()
            .find(|l| l["target"] == pi && l["input"] == input)
    {
        let mut ni = link["source"].as_u64().ok_or("Invalid texture link")? as usize;
        if nodes
            .get(ni)
            .is_some_and(|n| n["type"] == "ShaderNodeNormalMap")
            && let Some(link) = links
                .iter()
                .find(|l| l["target"] == ni && l["input"] == "Color")
        {
            ni = link["source"].as_u64().ok_or("Invalid normal image link")? as usize;
        }
        let node = nodes.get(ni).ok_or("Invalid texture node")?;
        let wrap = match node["extension"].as_str().unwrap_or("REPEAT") {
            "REPEAT" => 10497,
            "EXTEND" => 33071,
            "MIRROR" => 33648,
            _ => return Err("Use Image Texture REPEAT, EXTEND or MIRROR wrapping".into()),
        };
        if wrap != 10497 {
            binding["sampler"] =
                json!({"wrapS":wrap,"wrapT":wrap,"magFilter":9729,"minFilter":9987});
        }
    }
    Ok(binding)
}

/// Asset bindings that the unchanged rasterizer and other format writers cannot
/// evaluate must fail before producing an image or a silently degraded asset.
impl Material {
    pub fn from(scene: &super::Scene, source: &Value) -> Result<Self, String> {
        let m = Self::from_asset(source)?;
        for (role, image) in [
            ("base_color", m.color_image),
            ("alpha", m.alpha_image),
            ("normal", m.normal_image),
            ("mr", m.mr_image),
            ("emission", m.emission_image),
        ] {
            if image.is_none() {
                continue;
            }
            let b = texture_binding(scene, source, role)?;
            let s = &b["sampler"];
            if role == "emission"
                || b["texCoord"].as_u64().unwrap_or(0) != 0
                || !b["extensions"]["KHR_texture_transform"].is_null()
                || s["wrapS"].as_u64().unwrap_or(10497) != 10497
                || s["wrapT"].as_u64().unwrap_or(10497) != 10497
                || s["magFilter"].as_u64() == Some(9728)
                || [Some(9728), Some(9984), Some(9986)].contains(&s["minFilter"].as_u64())
            {
                return Err("Texture transforms, clamp/mirror, nonzero UV channels and emissive images are glTF asset features; export GLB/glTF to a texture-aware viewer, or use UV0/REPEAT without Mapping or emissive images for the fixed preview/OBJ/USDZ".into());
            }
        }
        Ok(m)
    }
}

/// Add an image/sampler instance without changing the image index map.
pub fn export_texture(
    doc: &mut Value,
    source_index: usize,
    mut binding: Value,
) -> Result<Value, String> {
    use serde_json::json;
    if binding.is_null() {
        binding = json!({});
    }
    let sampler = binding
        .as_object_mut()
        .ok_or("Invalid texture binding")?
        .remove("sampler");
    let mut index = source_index;
    if let Some(sampler) = sampler.filter(|s| s.as_object().is_some_and(|s| !s.is_empty())) {
        if doc["samplers"].is_null() {
            doc["samplers"] = json!([]);
        }
        let samplers = doc["samplers"].as_array_mut().unwrap();
        let si = if let Some(i) = samplers.iter().position(|s| s == &sampler) {
            i
        } else {
            samplers.push(sampler);
            samplers.len() - 1
        };
        let texture = json!({"source":source_index,"sampler":si});
        let textures = doc["textures"].as_array_mut().unwrap();
        index = if let Some(i) = textures.iter().position(|t| t == &texture) {
            i
        } else {
            textures.push(texture);
            textures.len() - 1
        };
    }
    binding["index"] = json!(index);
    if !binding["extensions"]["KHR_texture_transform"].is_null() {
        if doc["extensionsUsed"].is_null() {
            doc["extensionsUsed"] = json!([]);
        }
        let used = doc["extensionsUsed"].as_array_mut().unwrap();
        if !used.contains(&json!("KHR_texture_transform")) {
            used.push(json!("KHR_texture_transform"));
        }
    }
    Ok(binding)
}

pub fn asset_image_users(source: &Value, image: u64) -> usize {
    ["color_image", "normal_image", "mr_image", "emission_image"]
        .into_iter()
        .filter(|field| source["gltf"][field].as_u64() == Some(image))
        .count()
}
pub fn unlink_asset_image(source: &mut Value, image: u64) {
    for field in ["color_image", "normal_image", "mr_image", "emission_image"] {
        if source["gltf"][field].as_u64() == Some(image) {
            source["gltf"][field] = Value::Null;
        }
    }
}
