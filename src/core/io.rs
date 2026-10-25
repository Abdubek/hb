//! glTF 2.0/GLB and OBJ+MTL assembly I/O. Unsupported extensions fail explicitly.
use super::{
    Scene, Value,
    geometry::Geometry,
    id, images,
    math::{M4, *},
    num,
    render::Material,
    text, vec3, vec4,
};
use base64::{Engine, engine::general_purpose::STANDARD};
use serde_json::json;
use std::{
    collections::{BTreeMap, BTreeSet},
    fs,
    path::Path,
};
fn read(path: &Path) -> Result<Vec<u8>, String> {
    fs::read(path).map_err(|e| format!("{}: {e}", path.display()))
}
fn array<'a>(v: &'a Value, key: &str) -> &'a [Value] {
    v[key].as_array().map(Vec::as_slice).unwrap_or(&[])
}
fn index(v: &Value) -> Result<usize, String> {
    v.as_u64()
        .and_then(|n| usize::try_from(n).ok())
        .ok_or("Expected nonnegative index".into())
}
fn uri(base: &Path, s: &str) -> Result<Vec<u8>, String> {
    if s.starts_with("data:") {
        let (header, data) = s.split_once(',').ok_or("Invalid data URI")?;
        if !header.ends_with(";base64") {
            return Err("Only base64 data URIs are supported".into());
        }
        return STANDARD.decode(data).map_err(|e| e.to_string());
    }
    if s.contains("://") {
        return Err("Remote asset URLs are unsupported; download the asset pack first".into());
    }
    let mut decoded = vec![];
    let bytes = s.as_bytes();
    let mut i = 0;
    while i < bytes.len() {
        if bytes[i] == b'%' && i + 2 < bytes.len() {
            decoded
                .push(u8::from_str_radix(&s[i + 1..i + 3], 16).map_err(|_| "Invalid URI escape")?);
            i += 3;
        } else {
            decoded.push(bytes[i]);
            i += 1;
        }
    }
    let path = String::from_utf8(decoded).map_err(|_| "Invalid URI UTF-8")?;
    read(&base.join(path))
}
struct Gltf {
    doc: Value,
    buffers: Vec<Vec<u8>>,
    decoded: BTreeMap<usize, Vec<u8>>,
}
impl Gltf {
    fn load(path: &Path) -> Result<Self, String> {
        let bytes = read(path)?;
        let (mut doc, mut bin) = (None, None);
        if bytes.starts_with(b"glTF") {
            if bytes.len() < 20
                || u32::from_le_bytes(bytes[4..8].try_into().unwrap()) != 2
                || u32::from_le_bytes(bytes[8..12].try_into().unwrap()) as usize != bytes.len()
            {
                return Err("Invalid GLB header/length".into());
            }
            let mut at = 12;
            while at + 8 <= bytes.len() {
                let len = u32::from_le_bytes(bytes[at..at + 4].try_into().unwrap()) as usize;
                let kind = &bytes[at + 4..at + 8];
                at += 8;
                let data = bytes.get(at..at + len).ok_or("Truncated GLB chunk")?;
                if kind == b"JSON" {
                    doc = Some(serde_json::from_slice(data).map_err(|e| e.to_string())?);
                } else if kind == b"BIN\0" {
                    bin = Some(data.to_vec());
                }
                at += len;
            }
            if at != bytes.len() {
                return Err("Invalid GLB alignment".into());
            }
        } else {
            doc = Some(serde_json::from_slice(&bytes).map_err(|e| e.to_string())?);
        }
        let doc: Value = doc.ok_or("Missing glTF JSON")?;
        if doc["asset"]["version"] != "2.0" {
            return Err("Only glTF 2.0 is supported".into());
        }
        let supported = [
            "KHR_lights_punctual",
            "KHR_materials_emissive_strength",
            "KHR_materials_transmission",
            "KHR_materials_ior",
            "KHR_texture_transform",
            "KHR_mesh_quantization",
            "EXT_meshopt_compression",
        ];
        for e in array(&doc, "extensionsRequired") {
            if !supported.contains(&text(e)) {
                return Err(format!("Unsupported required glTF extension {}", text(e)));
            }
        }
        if !array(&doc, "animations").is_empty() || !array(&doc, "skins").is_empty() {
            return Err("Animated/skinned glTF is outside the M1 static assembly subset; export a static mesh".into());
        }
        for field in [
            "nodes",
            "meshes",
            "materials",
            "cameras",
            "images",
            "textures",
            "samplers",
            "scenes",
            "buffers",
            "bufferViews",
            "accessors",
        ] {
            if doc.get(field).is_some_and(|v| !v.is_array()) {
                return Err(format!("glTF {field} must be an array"));
            }
        }
        for n in array(&doc, "nodes") {
            if !n.is_object() {
                return Err("glTF node must be an object".into());
            }
            let components = ["mesh", "camera"]
                .iter()
                .filter(|k| !n[**k].is_null())
                .count()
                + usize::from(!n["extensions"]["KHR_lights_punctual"].is_null());
            if components > 1 {
                return Err(
                    "M1 requires separate nodes for mesh, camera and light components".into(),
                );
            }
            for (field, len) in [
                ("translation", 3),
                ("scale", 3),
                ("rotation", 4),
                ("matrix", 16),
            ] {
                if let Some(v) = n.get(field)
                    && v.as_array().is_none_or(|a| {
                        a.len() != len
                            || a.iter().any(|n| n.as_f64().is_none_or(|n| !n.is_finite()))
                    })
                {
                    return Err(format!("Invalid node {field}"));
                }
            }
        }
        let base = path.parent().unwrap_or(Path::new("."));
        let mut buffers = vec![];
        let meshopt_required = array(&doc, "extensionsRequired")
            .iter()
            .any(|v| v == "EXT_meshopt_compression");
        for (i, b) in array(&doc, "buffers").iter().enumerate() {
            let marker = &b["extensions"]["EXT_meshopt_compression"]["fallback"];
            if !marker.is_null() && marker != true {
                return Err("Meshopt fallback marker must be true".into());
            }
            let no_source = b["uri"].is_null() && !(i == 0 && bin.is_some());
            let fallback = marker == true || (meshopt_required && no_source);
            if fallback {
                if no_source && !meshopt_required {
                    return Err("URI-less Meshopt fallback requires extensionsRequired".into());
                }
                for view in array(&doc, "bufferViews") {
                    let extension = &view["extensions"]["EXT_meshopt_compression"];
                    if (view["buffer"].as_u64() == Some(i as u64) && !extension.is_object())
                        || extension["buffer"].as_u64() == Some(i as u64)
                    {
                        return Err("Meshopt fallback buffers may only be referenced by compressed parent views".into());
                    }
                }
                index(&b["byteLength"])?;
                buffers.push(Vec::new());
                continue;
            }
            let data = if let Some(s) = b["uri"].as_str() {
                uri(base, s)?
            } else if i == 0 && bin.is_some() {
                bin.take().unwrap()
            } else {
                return Err("Missing buffer URI".into());
            };
            if data.len() < index(&b["byteLength"])? {
                return Err("Truncated glTF buffer".into());
            }
            buffers.push(data);
        }
        let decoded = super::meshopt::views(&doc, &buffers)?;
        Ok(Self {
            doc,
            buffers,
            decoded,
        })
    }
    fn view(&self, k: usize) -> Result<&[u8], String> {
        if let Some(data) = self.decoded.get(&k) {
            return Ok(data);
        }
        let v = self.doc["bufferViews"]
            .get(k)
            .ok_or("Invalid buffer view")?;
        let buffer = self
            .buffers
            .get(index(&v["buffer"])?)
            .ok_or("Invalid buffer index")?;
        let start = v["byteOffset"].as_u64().unwrap_or(0) as usize;
        let len = index(&v["byteLength"])?;
        buffer
            .get(start..start.checked_add(len).ok_or("Buffer size overflow")?)
            .ok_or("Buffer view exceeds buffer".into())
    }
    fn accessor(&self, k: usize) -> Result<Vec<Vec<f64>>, String> {
        let a = self.doc["accessors"].get(k).ok_or("Invalid accessor")?;
        let count = index(&a["count"])?;
        if count > 20_000_000 {
            return Err("Accessor exceeds 20 million elements".into());
        }
        let n = match text(&a["type"]) {
            "SCALAR" => 1,
            "VEC2" => 2,
            "VEC3" => 3,
            "VEC4" => 4,
            _ => return Err("Only scalar/vector mesh accessors are supported".into()),
        };
        let ct = index(&a["componentType"])?;
        let width = match ct {
            5120 | 5121 => 1,
            5122 | 5123 => 2,
            5125 | 5126 => 4,
            _ => return Err("Unsupported accessor component type".into()),
        };
        let norm = a["normalized"] == true;
        let decode = |b: &[u8]| -> f64 {
            match ct {
                5120 => {
                    let v = b[0] as i8 as f64;
                    if norm { (v / 127.).max(-1.) } else { v }
                }
                5121 => b[0] as f64 / if norm { 255. } else { 1. },
                5122 => {
                    let v = i16::from_le_bytes(b.try_into().unwrap()) as f64;
                    if norm { (v / 32767.).max(-1.) } else { v }
                }
                5123 => {
                    u16::from_le_bytes(b.try_into().unwrap()) as f64
                        / if norm { 65535. } else { 1. }
                }
                5125 => u32::from_le_bytes(b.try_into().unwrap()) as f64,
                5126 => f32::from_le_bytes(b.try_into().unwrap()) as f64,
                _ => unreachable!(),
            }
        };
        let mut out = vec![vec![0.; n]; count];
        if let Some(view) = a["bufferView"].as_u64() {
            let data = self.view(view as usize)?;
            let stride = self.doc["bufferViews"][view as usize]["byteStride"]
                .as_u64()
                .unwrap_or((n * width) as u64) as usize;
            if stride < n * width {
                return Err("Accessor byte stride too small".into());
            }
            let offset = a["byteOffset"].as_u64().unwrap_or(0) as usize;
            for (i, row) in out.iter_mut().enumerate() {
                for (j, v) in row.iter_mut().enumerate() {
                    let at = offset
                        .checked_add(i.checked_mul(stride).ok_or("Accessor overflow")?)
                        .and_then(|x| x.checked_add(j * width))
                        .ok_or("Accessor overflow")?;
                    *v = decode(
                        data.get(at..at + width)
                            .ok_or("Accessor exceeds buffer view")?,
                    );
                }
            }
        }
        if let Some(s) = a.get("sparse") {
            let nc = index(&s["count"])?;
            if nc > count {
                return Err("Sparse count exceeds accessor".into());
            }
            let ids = self.view(index(&s["indices"]["bufferView"])?)?;
            let vals = self.view(index(&s["values"]["bufferView"])?)?;
            let it = index(&s["indices"]["componentType"])?;
            let iw = match it {
                5121 => 1,
                5123 => 2,
                5125 => 4,
                _ => return Err("Invalid sparse index type".into()),
            };
            let io = s["indices"]["byteOffset"].as_u64().unwrap_or(0) as usize;
            let vo = s["values"]["byteOffset"].as_u64().unwrap_or(0) as usize;
            for i in 0..nc {
                let b = ids
                    .get(io + i * iw..io + (i + 1) * iw)
                    .ok_or("Truncated sparse indices")?;
                let k = match iw {
                    1 => b[0] as usize,
                    2 => u16::from_le_bytes(b.try_into().unwrap()) as usize,
                    _ => u32::from_le_bytes(b.try_into().unwrap()) as usize,
                };
                let row = out.get_mut(k).ok_or("Sparse index out of bounds")?;
                for (j, v) in row.iter_mut().enumerate() {
                    let at = vo + (i * n + j) * width;
                    *v = decode(vals.get(at..at + width).ok_or("Truncated sparse values")?);
                }
            }
        }
        if out.iter().flatten().any(|x| !x.is_finite()) {
            return Err("Nonfinite glTF attribute".into());
        }
        Ok(out)
    }
}
fn transform_record(m: M4) -> Value {
    let t = point(m, [0.; 3]);
    let mut s: [f64; 3] = std::array::from_fn(|j| length([m[0][j], m[1][j], m[2][j]]));
    if dot(
        cross([m[0][0], m[1][0], m[2][0]], [m[0][1], m[1][1], m[2][1]]),
        [m[0][2], m[1][2], m[2][2]],
    ) < 0.
    {
        s[0] = -s[0];
    }
    let r: [[f64; 3]; 3] = std::array::from_fn(|i| {
        std::array::from_fn(|j| {
            if s[j].abs() > 1e-15 {
                m[i][j] / s[j]
            } else {
                if i == j { 1. } else { 0. }
            }
        })
    });
    let y = (-r[2][0]).clamp(-1., 1.).asin();
    let (x, z) = if y.cos().abs() > 1e-6 {
        (r[2][1].atan2(r[2][2]), r[1][0].atan2(r[0][0]))
    } else {
        ((-r[1][2]).atan2(r[1][1]), 0.)
    };
    json!({"matrix":flat(m),"location":t.map(|v|v as f32),"rotation_euler":[x as f32,y as f32,z as f32],"scale":s.map(|v|v as f32)})
}
pub fn import(scene: &mut Scene, path: &Path) -> Result<Vec<String>, String> {
    match path
        .extension()
        .and_then(|s| s.to_str())
        .unwrap_or("")
        .to_ascii_lowercase()
        .as_str()
    {
        "glb" | "gltf" => import_gltf(scene, path, false),
        "obj" => import_obj(scene, path, false),
        "stl" => super::stl::import(scene, path),
        "ply" => super::ply::import(scene, path),
        _ => Err("Import supports .glb, .gltf, .obj, .stl and .ply".into()),
    }
}
pub fn bpy_import_gltf(scene: &mut Scene, path: &Path) -> Result<Vec<String>, String> {
    let mut candidate = scene.clone();
    let warnings = import_gltf(&mut candidate, path, true)?;
    *scene = candidate;
    Ok(warnings)
}
pub fn bpy_export_gltf(scene: &Scene, options: &Value) -> Result<Vec<String>, String> {
    let mut output = scene.clone();
    let mut retained = BTreeSet::new();
    for key in scene.linked_ids() {
        let object = scene.object(key)?;
        if (options["selection"] != true || object["selected"] == true)
            && (options["cameras"] == true || scene.obj_type(object) != "CAMERA")
            && (options["lights"] == true || scene.obj_type(object) != "LIGHT")
        {
            retained.insert(key);
        }
    }
    // Evaluate before filtering so modifier operands remain available.
    if options["apply"] == true {
        if let Some(evaluated) = super::modeling::for_export(&output)? {
            output = evaluated;
        }
    } else {
        for object in &mut output.objects {
            object["modifiers"] = json!([]);
        }
    }
    for object in &mut output.objects {
        if object["parent"]
            .as_u64()
            .is_some_and(|p| !retained.contains(&p))
        {
            let world = scene.world(id(object))?;
            object["parent"] = Value::Null;
            object["matrix"] = json!(flat(world));
            object
                .as_object_mut()
                .unwrap()
                .remove("matrix_parent_inverse");
        }
    }
    output.objects.retain(|o| retained.contains(&id(o)));
    for collection in &mut output.collections {
        collection["objects"]
            .as_array_mut()
            .unwrap()
            .retain(|o| o.as_u64().is_some_and(|k| retained.contains(&k)));
    }
    let path = Path::new(text(&options["path"]));
    let binary = options["format"] == "GLB";
    let extension = if binary { "glb" } else { "gltf" };
    let path = if path
        .extension()
        .is_some_and(|e| e.eq_ignore_ascii_case(extension))
    {
        path.to_path_buf()
    } else {
        std::path::PathBuf::from(format!("{}.{}", path.display(), extension))
    };
    let write = |path: &Path, bytes: &[u8]| {
        crate::cli::atomic_write(path, bytes).map_err(|e| format!("{}: {e}", path.display()))
    };
    if binary {
        let (bytes, warnings) = glb(&output)?;
        write(&path, &bytes)?;
        Ok(warnings)
    } else {
        let (mut doc, bytes, warnings) = gltf(&output)?;
        if !bytes.is_empty() {
            let buffer = path.with_extension("bin");
            doc["buffers"][0]["uri"] = json!(
                buffer
                    .file_name()
                    .ok_or("Expected export filename")?
                    .to_string_lossy()
            );
            write(&buffer, &bytes)?;
        }
        write(&path, &serde_json::to_vec(&doc).map_err(|e| e.to_string())?)?;
        Ok(warnings)
    }
}
fn import_gltf(scene: &mut Scene, path: &Path, operator: bool) -> Result<Vec<String>, String> {
    let g = Gltf::load(path)?;
    let doc = &g.doc;
    let base = path.parent().unwrap_or(Path::new("."));
    let mut warnings = vec![];
    for e in array(doc, "extensionsUsed") {
        if ![
            "KHR_lights_punctual",
            "KHR_materials_emissive_strength",
            "KHR_materials_transmission",
            "KHR_materials_ior",
            "KHR_texture_transform",
            "KHR_mesh_quantization",
            "EXT_meshopt_compression",
        ]
        .contains(&text(e))
        {
            return Err(format!(
                "glTF extension {} is unsupported; re-export without it",
                text(e)
            ));
        }
    }
    let mut images = vec![];
    for (i, v) in array(doc, "images").iter().enumerate() {
        let bytes = if let Some(s) = v["uri"].as_str() {
            uri(base, s)?
        } else {
            g.view(index(&v["bufferView"])?)?.to_vec()
        };
        let k = scene.create(
            "images",
            v["name"].as_str().unwrap_or(&format!("Image{i}")),
            images::encoded(&bytes)?,
        )?;
        images.push(k);
    }
    let texture = |info: &Value| -> Result<Option<u64>, String> {
        if info.is_null() {
            return Ok(None);
        }
        super::material::import_binding(doc, info)?;
        let t = doc["textures"]
            .get(index(&info["index"])?)
            .ok_or("Invalid texture index")?;
        Ok(Some(
            *images
                .get(index(&t["source"])?)
                .ok_or("Invalid texture source")?,
        ))
    };
    let mut materials = vec![];
    for (i, v) in array(doc, "materials").iter().enumerate() {
        super::material::validate_import(v)?;
        let p = &v["pbrMetallicRoughness"];
        let base = p
            .get("baseColorFactor")
            .cloned()
            .unwrap_or(json!([1., 1., 1., 1.]));
        let metallic = p["metallicFactor"].as_f64().unwrap_or(1.);
        let roughness = p["roughnessFactor"].as_f64().unwrap_or(1.);
        let emission = mul(
            vec3(&v["emissiveFactor"]),
            v["extensions"]["KHR_materials_emissive_strength"]["emissiveStrength"]
                .as_f64()
                .unwrap_or(1.),
        );
        if !v["occlusionTexture"].is_null() {
            return Err("Occlusion textures are outside the permitted Principled chain; remove occlusionTexture before import".into());
        }
        let k=scene.create("materials",v["name"].as_str().unwrap_or(&format!("Material{i}")),json!({"diffuse_color":base,"metallic":metallic,"roughness":roughness,"gltf":{"base":base,"metallic":metallic,"roughness":roughness,"emission":emission,"emission_image":texture(&v["emissiveTexture"])?,"bindings":{"base_color":super::material::import_binding(doc,&p["baseColorTexture"])?,"normal":super::material::import_binding(doc,&v["normalTexture"])?,"mr":super::material::import_binding(doc,&p["metallicRoughnessTexture"])?,"emission":super::material::import_binding(doc,&v["emissiveTexture"])?},"color_image":texture(&p["baseColorTexture"])?,"mr_image":texture(&p["metallicRoughnessTexture"])?,"normal_image":texture(&v["normalTexture"])?,"normal_strength":v["normalTexture"]["scale"].as_f64().unwrap_or(1.),"alpha_mode":v["alphaMode"].as_str().unwrap_or("OPAQUE"),"cutoff":v["alphaCutoff"].as_f64().unwrap_or(0.5),"transmission":v["extensions"]["KHR_materials_transmission"]["transmissionFactor"].as_f64().unwrap_or(0.),"ior":v["extensions"]["KHR_materials_ior"]["ior"].as_f64().unwrap_or(1.5),"principled":v["extras"]["hb_principled"].clone()}}))?;
        if operator {
            let emitted = emission.iter().any(|x| *x != 0.);
            let color = if emitted {
                vec3(&v["emissiveFactor"])
            } else {
                [1.; 3]
            };
            let strength = if emitted {
                v["extensions"]["KHR_materials_emissive_strength"]["emissiveStrength"]
                    .as_f64()
                    .unwrap_or(1.)
            } else {
                0.
            };
            let mut nodes = json!([
                {"name":"Principled BSDF","type":"ShaderNodeBsdfPrincipled","image":null,"inputs":{
                    "Base Color":base,"Metallic":metallic,"Roughness":roughness,"Alpha":base[3],
                    "Emission Color":[color[0],color[1],color[2],1.],"Emission Strength":strength,"Normal":[0.,0.,0.]}},
                {"name":"Material Output","type":"ShaderNodeOutputMaterial","image":null,"inputs":{"Surface":null}}
            ]);
            if let Some(extra) = v["extras"]["hb_principled"].as_object() {
                for (key, value) in extra {
                    nodes[0]["inputs"][key] = value.clone();
                }
            }
            if !v["extensions"]["KHR_materials_transmission"].is_null() {
                nodes[0]["inputs"]["Transmission Weight"] =
                    v["extensions"]["KHR_materials_transmission"]["transmissionFactor"].clone();
            }
            if !v["extensions"]["KHR_materials_ior"].is_null() {
                nodes[0]["inputs"]["IOR"] = v["extensions"]["KHR_materials_ior"]["ior"].clone();
            }
            for node in nodes.as_array_mut().unwrap() {
                for value in node["inputs"].as_object_mut().unwrap().values_mut() {
                    if !value.is_null() {
                        *value = super::f32_value(value)?;
                    }
                }
            }
            let material = scene.get_mut("materials", k)?;
            material["nodes"] = nodes;
            material["links"] = json!([{"source":0,"output":"BSDF","target":1,"input":"Surface"}]);
            material["use_nodes"] = json!(true);
            material["metallic"] = json!(0.);
            material["roughness"] = json!(0.4f32);
        }
        materials.push(k);
    }
    let mut meshes = vec![];
    for (mi, m) in array(doc, "meshes").iter().enumerate() {
        let mut vertices = vec![];
        let mut faces: Vec<Vec<usize>> = vec![];
        let mut norms = vec![];
        let mut uv_count = 1;
        for prim in array(m, "primitives") {
            for key in prim["attributes"]
                .as_object()
                .ok_or("Missing mesh attributes")?
                .keys()
            {
                if let Some(index) = key
                    .strip_prefix("TEXCOORD_")
                    .and_then(|s| s.parse::<usize>().ok())
                {
                    if index >= 8 {
                        return Err("glTF import supports TEXCOORD_0 through TEXCOORD_7".into());
                    }
                    uv_count = uv_count.max(index + 1);
                }
            }
        }
        let mut uvs = vec![vec![]; uv_count];
        let mut colors = vec![];
        let mut slots = vec![];
        let mut matindices = vec![];
        for primitive in array(m, "primitives") {
            if !primitive["targets"].is_null() {
                return Err("Morph targets are outside static M1 assembly".into());
            }
            let a = &primitive["attributes"];
            for key in a.as_object().ok_or("Missing mesh attributes")?.keys() {
                if !["POSITION", "NORMAL", "COLOR_0"].contains(&key.as_str())
                    && !(0..8).any(|i| key == &format!("TEXCOORD_{i}"))
                {
                    return Err(format!("Unsupported mesh attribute {key}"));
                }
            }
            if let Some(material) = primitive["material"]
                .as_u64()
                .and_then(|i| doc["materials"].get(i as usize))
            {
                for info in [
                    &material["pbrMetallicRoughness"]["baseColorTexture"],
                    &material["pbrMetallicRoughness"]["metallicRoughnessTexture"],
                    &material["normalTexture"],
                    &material["emissiveTexture"],
                ] {
                    let uv = info["extensions"]["KHR_texture_transform"]["texCoord"]
                        .as_u64()
                        .or(info["texCoord"].as_u64())
                        .unwrap_or(0);
                    if uv > 0 && a[format!("TEXCOORD_{uv}")].is_null() {
                        return Err(format!(
                            "Texture needs missing TEXCOORD_{uv}; include that UV channel before import"
                        ));
                    }
                }
            }
            let pos = g.accessor(index(&a["POSITION"])?)?;
            if pos.iter().any(|p| p.len() != 3) {
                return Err("POSITION needs VEC3".into());
            }
            let normal = if a["NORMAL"].is_null() {
                None
            } else {
                Some(g.accessor(index(&a["NORMAL"])?)?)
            };
            let uv: Vec<_> = (0..uv_count)
                .map(|i| {
                    let key = format!("TEXCOORD_{i}");
                    if a[&key].is_null() {
                        Ok(None)
                    } else {
                        g.accessor(index(&a[&key])?).map(Some)
                    }
                })
                .collect::<Result<_, String>>()?;
            let color = if a["COLOR_0"].is_null() {
                None
            } else {
                Some(g.accessor(index(&a["COLOR_0"])?)?)
            };
            if normal
                .as_ref()
                .is_some_and(|v| v.len() != pos.len() || v.iter().any(|x| x.len() != 3))
                || uv
                    .iter()
                    .flatten()
                    .any(|v| v.len() != pos.len() || v.iter().any(|x| x.len() != 2))
                || color.as_ref().is_some_and(|v| {
                    v.len() != pos.len() || v.iter().any(|x| x.len() != 3 && x.len() != 4)
                })
            {
                return Err("Attribute dimensions/counts differ".into());
            }
            let ids: Vec<usize> = if primitive["indices"].is_null() {
                (0..pos.len()).collect()
            } else {
                g.accessor(index(&primitive["indices"])?)?
                    .into_iter()
                    .map(|v| v[0] as usize)
                    .collect()
            };
            if ids.iter().any(|&i| i >= pos.len()) {
                return Err("Triangle index exceeds vertex count".into());
            }
            let mode = primitive["mode"].as_u64().unwrap_or(4);
            let triangles: Vec<[usize; 3]> = match mode {
                4 => {
                    if !ids.len().is_multiple_of(3) {
                        return Err("Triangle index count is not divisible by three".into());
                    }
                    ids.chunks(3).map(|v| [v[0], v[1], v[2]]).collect()
                }
                5 => (2..ids.len())
                    .map(|i| {
                        if i % 2 == 0 {
                            [ids[i - 2], ids[i - 1], ids[i]]
                        } else {
                            [ids[i - 1], ids[i - 2], ids[i]]
                        }
                    })
                    .collect(),
                6 => (2..ids.len())
                    .map(|i| [ids[0], ids[i - 1], ids[i]])
                    .collect(),
                _ => {
                    return Err("Only glTF triangle, strip and fan primitives are supported".into());
                }
            };
            let offset = vertices.len();
            vertices.extend(pos.iter().map(|v| point(Y_TO_Z, [v[0], v[1], v[2]])));
            let material = if primitive["material"].is_null() {
                Value::Null
            } else {
                json!(
                    *materials
                        .get(index(&primitive["material"])?)
                        .ok_or("Invalid primitive material")?
                )
            };
            let slot = slots
                .iter()
                .position(|v| v == &material)
                .unwrap_or_else(|| {
                    slots.push(material);
                    slots.len() - 1
                });
            for t in triangles {
                if t[0] == t[1] || t[0] == t[2] || t[1] == t[2] {
                    continue;
                }
                let p = t.map(|i| vertices[offset + i]);
                let face_n = normalize(cross(sub(p[1], p[0]), sub(p[2], p[0])));
                faces.push(t.map(|i| offset + i).to_vec());
                matindices.push(slot);
                for i in t {
                    norms.push(
                        normal
                            .as_ref()
                            .map(|v| normalize(direction(Y_TO_Z, [v[i][0], v[i][1], v[i][2]])))
                            .unwrap_or(face_n),
                    );
                    for (values, source) in uvs.iter_mut().zip(&uv) {
                        values.push(
                            source
                                .as_ref()
                                .map(|v| [v[i][0], 1. - v[i][1]])
                                .unwrap_or([0.; 2]),
                        );
                    }
                    colors.push(
                        color
                            .as_ref()
                            .map(|v| {
                                [
                                    v[i][0],
                                    v[i][1],
                                    v[i][2],
                                    v[i].get(3).copied().unwrap_or(1.),
                                ]
                            })
                            .unwrap_or([1.; 4]),
                    );
                }
            }
        }
        let k = scene.create(
            "meshes",
            m["name"].as_str().unwrap_or(&format!("Mesh{mi}")),
            json!({}),
        )?;
        scene.mesh_from(k, json!(vertices), json!([]), json!(faces), false)?;
        let m = scene.get_mut("meshes", k)?;
        m["materials"] = json!(slots);
        m["material_indices"] = json!(matindices);
        m["loop_normals"] = json!(norms);
        m["uv_layers"] = json!(uvs.into_iter().enumerate().map(|(i,data)| json!({"name":if i==0 { "UVMap".to_string() } else { format!("UVMap.{i:03}") },"data":data})).collect::<Vec<_>>());
        m["colors"] = json!(colors);
        meshes.push(k);
    }
    let nodes = array(doc, "nodes");
    let mut parent = BTreeMap::new();
    for (i, n) in nodes.iter().enumerate() {
        for c in array(n, "children") {
            let c = index(c)?;
            if c >= nodes.len() || parent.insert(c, i).is_some() {
                return Err("Invalid or multiply-parented glTF node".into());
            }
        }
    }
    fn world(
        i: usize,
        nodes: &[Value],
        parent: &BTreeMap<usize, usize>,
        seen: &mut BTreeSet<usize>,
    ) -> Result<M4, String> {
        if !seen.insert(i) {
            return Err("Cyclic node hierarchy".into());
        }
        let n = &nodes[i];
        let m = if let Some(v) = n["matrix"].as_array() {
            from_flat(&v.iter().map(num).collect::<Vec<_>>())?
        } else {
            let t = vec3(&n["translation"]);
            let s = n.get("scale").map(vec3).unwrap_or([1.; 3]);
            let q = n.get("rotation").map(vec4).unwrap_or([0., 0., 0., 1.]);
            let mut m = quat(q);
            for j in 0..3 {
                for row in m.iter_mut().take(3) {
                    row[j] *= s[j];
                }
            }
            for j in 0..3 {
                m[j][3] = t[j];
            }
            m
        };
        Ok(if let Some(p) = parent.get(&i) {
            matmul(world(*p, nodes, parent, seen)?, m)
        } else {
            m
        })
    }
    let si = doc["scene"].as_u64().unwrap_or(0) as usize;
    let roots = doc["scenes"]
        .get(si)
        .map(|v| array(v, "nodes").to_vec())
        .unwrap_or_else(|| {
            (0..nodes.len())
                .filter(|i| !parent.contains_key(i))
                .map(|i| json!(i))
                .collect()
        });
    let mut reachable = BTreeSet::new();
    let first_root = roots.first().and_then(Value::as_u64).map(|v| v as usize);
    let mut todo = roots;
    while let Some(k) = todo.pop() {
        let k = index(&k)?;
        if !reachable.insert(k) {
            return Err("Repeated/cyclic glTF scene node".into());
        }
        let n = nodes.get(k).ok_or("Invalid scene root")?;
        todo.extend_from_slice(array(n, "children"));
    }
    let mut objects = BTreeMap::new();
    let mut worlds = BTreeMap::new();
    for &i in &reachable {
        let n = &nodes[i];
        let name = n["name"].as_str().unwrap_or("Object");
        let special = !n["camera"].is_null()
            || !n["extensions"]["KHR_lights_punctual"].is_null()
            || !n["extras"]["hb_area_light"].is_null();
        let w = world(i, nodes, &parent, &mut BTreeSet::new())?;
        worlds.insert(
            i,
            if special {
                matmul(Y_TO_Z, w)
            } else {
                matmul(matmul(Y_TO_Z, w), Z_TO_Y)
            },
        );
        let data = if let Some(mi) = n["mesh"].as_u64() {
            json!({"kind":"meshes","id":*meshes.get(mi as usize).ok_or("Invalid mesh index")?})
        } else if let Some(ci) = n["camera"].as_u64() {
            let c = doc["cameras"]
                .get(ci as usize)
                .ok_or("Invalid camera index")?;
            let t = text(&c["type"]);
            let p = &c[t];
            let extra = if let Some(extra) = c["extras"].get("hb_camera") {
                extra.clone()
            } else if t == "perspective" {
                let aspect = p["aspectRatio"].as_f64().unwrap_or(1.);
                json!({"type":"PERSP","sensor_fit":"VERTICAL","sensor_height":24.,"lens":12./(num(&p["yfov"])*0.5).tan(),"clip_start":p["znear"],"clip_end":p["zfar"].as_f64().unwrap_or(1e8),"import_aspect":aspect})
            } else if t == "orthographic" {
                json!({"type":"ORTHO","ortho_scale":num(&p["ymag"])*2.,"sensor_fit":"VERTICAL","clip_start":p["znear"],"clip_end":p["zfar"],"import_aspect":num(&p["xmag"])/num(&p["ymag"])})
            } else {
                return Err("Unsupported camera type".into());
            };
            let data_name = if operator {
                c["name"].as_str().unwrap_or("Camera")
            } else {
                name
            };
            json!({"kind":"cameras","id":scene.create("cameras",data_name,extra)?})
        } else if let Some(li) = n["extensions"]["KHR_lights_punctual"]["light"].as_u64() {
            let l = doc["extensions"]["KHR_lights_punctual"]["lights"]
                .get(li as usize)
                .ok_or("Invalid light index")?;
            let kind = match text(&l["type"]) {
                "directional" => "SUN",
                "point" => "POINT",
                "spot" => "SPOT",
                _ => return Err("Unsupported punctual light".into()),
            };
            let energy = l["intensity"].as_f64().unwrap_or(1.) / 683.
                * if kind == "SUN" {
                    1.
                } else {
                    4. * std::f64::consts::PI
                };
            let outer = l["spot"]["outerConeAngle"]
                .as_f64()
                .unwrap_or(std::f64::consts::FRAC_PI_4);
            let inner = l["spot"]["innerConeAngle"].as_f64().unwrap_or(0.);
            let data_name = if operator {
                l["name"].as_str().unwrap_or("Light")
            } else {
                name
            };
            json!({"kind":"lights","id":scene.create("lights",data_name,json!({"type":kind,"energy":energy,"color":l.get("color").cloned().unwrap_or(json!([1.,1.,1.])),"spot_size":outer*2.,"spot_blend":1.-inner/outer.max(1e-8)}))?})
        } else if let Some(light) = n["extras"].get("hb_area_light") {
            json!({"kind":"lights","id":scene.create("lights",name,light.clone())?})
        } else {
            Value::Null
        };
        let k = scene.create("objects", name, json!({"data":data}))?;
        scene.link(scene.active_collection, k, false, false)?;
        if !operator
            && special
            && scene.obj_type(scene.object(k)?) == "CAMERA"
            && scene.camera.is_none()
        {
            scene.camera = Some(k);
        }
        objects.insert(i, k);
    }
    for (&i, &k) in &objects {
        let p = parent.get(&i).and_then(|p| objects.get(p));
        let local = if let Some(pi) = parent.get(&i).filter(|p| objects.contains_key(p)) {
            matmul(inverse(worlds[pi])?, worlds[&i])
        } else {
            worlds[&i]
        };
        let record = transform_record(local);
        let o = scene.get_mut("objects", k)?;
        for (key, val) in record.as_object().unwrap() {
            o[key] = val.clone();
        }
        if operator {
            let (location, q, scale) = decompose_affine(local);
            o["matrix"] = Value::Null;
            o["location"] = json!(location.map(|x| x as f32));
            o["scale"] = json!(scale.map(|x| x as f32));
            o["rotation_euler"] = json!([0., 0., 0.]);
            o["rotation_mode"] = json!("QUATERNION");
            o["rotation_quaternion"] = json!([q[3] as f32, q[0] as f32, q[1] as f32, q[2] as f32]);
        }
        o["parent"] = json!(p);
    }
    if operator {
        let imported: BTreeSet<_> = objects.values().copied().collect();
        for object in &mut scene.objects {
            object["selected"] = json!(imported.contains(&id(object)));
        }
        scene.active = first_root
            .and_then(|i| objects.get(&i).copied())
            .or_else(|| objects.values().next().copied());
    }
    warnings.push(if operator {
        "glTF imported with editable scalar Principled inputs and native texture bindings; arbitrary generated shader graphs are not reconstructed.".into()
    } else {
        "glTF Y-up coordinates converted to Blender Z-up; imported material factors are editable through the material data fields.".into()
    });
    scene.validate()?;
    Ok(warnings)
}
fn obj_index(s: &str, n: usize) -> Result<usize, String> {
    let i = s.parse::<i64>().map_err(|_| "Invalid OBJ index")?;
    let i = if i < 0 { n as i64 + i } else { i - 1 };
    if i < 0 || i >= n as i64 {
        return Err("OBJ index out of bounds".into());
    }
    Ok(i as usize)
}
pub fn bpy_import_obj(scene: &mut Scene, options: &Value) -> Result<Vec<String>, String> {
    let mut candidate = scene.clone();
    let existing: BTreeSet<_> = scene.objects.iter().map(id).collect();
    let old_materials: BTreeSet<_> = scene.materials.iter().map(id).collect();
    import_obj(&mut candidate, Path::new(text(&options["path"])), true)?;
    let matrix = from_flat(&array(options, "matrix").iter().map(num).collect::<Vec<_>>())?;
    let transform = transform_record(matrix);
    for object in &mut candidate.objects {
        object["selected"] = json!(!existing.contains(&id(object)));
        if !existing.contains(&id(object)) {
            for (field, value) in transform.as_object().unwrap() {
                object[field] = value.clone();
            }
        }
    }
    for material in &mut candidate.materials {
        if old_materials.contains(&id(material)) {
            continue;
        }
        let mut base = material["diffuse_color"].clone();
        base[3] = json!(1.);
        let roughness = material
            .as_object_mut()
            .unwrap()
            .remove("obj_roughness")
            .unwrap_or_else(|| material["roughness"].clone());
        let mut nodes = json!([
            {"name":"Principled BSDF","type":"ShaderNodeBsdfPrincipled","image":null,"inputs":{
                "Base Color":base,"Metallic":material["metallic"],"Roughness":roughness,"Alpha":material["diffuse_color"][3],
                "Emission Color":[0.,0.,0.,1.],"Emission Strength":1.,"Normal":[0.,0.,0.]}},
            {"name":"Material Output","type":"ShaderNodeOutputMaterial","image":null,"inputs":{"Surface":null}}
        ]);
        for node in nodes.as_array_mut().unwrap() {
            for value in node["inputs"].as_object_mut().unwrap().values_mut() {
                if !value.is_null() {
                    *value = super::f32_value(value)?;
                }
            }
        }
        material["nodes"] = nodes;
        material["links"] = json!([{"source":0,"output":"BSDF","target":1,"input":"Surface"}]);
        material["use_nodes"] = json!(true);
    }
    candidate.validate()?;
    *scene = candidate;
    Ok(vec!["Legacy OBJ import uses the declared forward/up axes and Blender 3.6 scalar MTL conversion; arbitrary generated shader graphs are not reconstructed.".into()])
}
fn import_obj(scene: &mut Scene, path: &Path, operator: bool) -> Result<Vec<String>, String> {
    let source = String::from_utf8(read(path)?).map_err(|_| "OBJ is not UTF-8")?;
    let base = path.parent().unwrap_or(Path::new("."));
    let (mut positions, mut texcoords, mut normals) = (vec![], vec![], vec![]);
    let mut materials = BTreeMap::new();
    let mut name = path
        .file_stem()
        .and_then(|s| s.to_str())
        .unwrap_or("Object")
        .to_string();
    let mut groups: Vec<(String, Vec<Value>)> = vec![];
    let mut faces = vec![];
    let mut material = None;
    let mut smooth = false;
    for (line_no, line) in source.lines().enumerate() {
        let line = line.split('#').next().unwrap_or("").trim();
        let mut words = line.split_whitespace();
        let Some(op) = words.next() else {
            continue;
        };
        let fields: Vec<_> = words.collect();
        let numbers = || {
            fields
                .iter()
                .map(|s| {
                    s.parse::<f64>()
                        .map_err(|_| format!("OBJ line {}: invalid number", line_no + 1))
                })
                .collect::<Result<Vec<_>, _>>()
        };
        match op {
            "v" => {
                let v = numbers()?;
                if v.len() != 3 {
                    return Err("OBJ vertices require XYZ (vertex colors and homogeneous weights unsupported)".into());
                }
                positions.push([v[0], v[1], v[2]]);
            }
            "vt" => {
                let v = numbers()?;
                if v.len() < 2 || v.len() > 3 {
                    return Err("Invalid OBJ texture coordinate".into());
                }
                texcoords.push([v[0], v[1]]);
            }
            "vn" => {
                let v = numbers()?;
                if v.len() != 3 {
                    return Err("Invalid OBJ normal".into());
                }
                normals.push([v[0], v[1], v[2]]);
            }
            "o" | "g" => {
                if operator && op == "g" {
                    continue;
                }
                if !faces.is_empty() {
                    groups.push((name, faces));
                    faces = vec![];
                }
                name = fields.join(" ");
            }
            "usemtl" => {
                let n = fields.join(" ");
                material = Some(
                    *materials
                        .get(&n)
                        .ok_or(format!("OBJ material {n} has not been defined in an MTL"))?,
                );
            }
            "s" => smooth = fields.first().is_some_and(|s| *s != "off" && *s != "0"),
            "mtllib" => {
                for filename in fields {
                    let mtl = String::from_utf8(read(&base.join(filename))?)
                        .map_err(|_| "MTL is not UTF-8")?;
                    let mut current = None;
                    for l in mtl.lines() {
                        let l = l.split('#').next().unwrap_or("").trim();
                        let Some((op, rest)) = l.split_once(char::is_whitespace) else {
                            continue;
                        };
                        let rest = rest.trim();
                        if op == "newmtl" {
                            let k = scene.create(
                                "materials",
                                rest,
                                if operator {
                                    json!({"roughness":1.})
                                } else {
                                    json!({})
                                },
                            )?;
                            materials.insert(rest.to_string(), k);
                            current = Some(k);
                            continue;
                        }
                        let Some(k) = current else {
                            continue;
                        };
                        match op {
                            "Kd" | "Ke" => {
                                let v: Vec<f64> = rest
                                    .split_whitespace()
                                    .map(|s| s.parse().map_err(|_| "Invalid MTL color"))
                                    .collect::<Result<_, _>>()?;
                                if v.len() != 3 {
                                    return Err("MTL color requires RGB".into());
                                }
                                if op == "Kd" {
                                    scene.get_mut("materials", k)?["diffuse_color"] =
                                        json!([v[0], v[1], v[2], 1.]);
                                } else if v.iter().any(|x| *x != 0.) {
                                    return Err(
                                        "MTL emission is unsupported; use glTF emissiveFactor"
                                            .into(),
                                    );
                                }
                            }
                            "d" | "Tr" => {
                                let a = rest.parse::<f64>().map_err(|_| "Invalid MTL opacity")?;
                                scene.get_mut("materials", k)?["diffuse_color"][3] =
                                    json!(if op == "Tr" { 1. - a } else { a });
                            }
                            "Pr" | "Pm" | "Ns" => {
                                let n = rest.parse::<f64>().map_err(|_| "Invalid MTL factor")?;
                                let field = if op == "Pm" { "metallic" } else { "roughness" };
                                scene.get_mut("materials", k)?[field] = json!(if op == "Ns" {
                                    if operator {
                                        1. - (n.clamp(0., 1000.) / 1000.).sqrt()
                                    } else {
                                        (2. / (n + 2.)).sqrt().clamp(0., 1.)
                                    }
                                } else {
                                    n
                                });
                            }
                            "map_Kd" => {
                                if rest.starts_with('-') {
                                    return Err(
                                        "MTL texture options unsupported; use a plain map_Kd path"
                                            .into(),
                                    );
                                }
                                let image = scene.create(
                                    "images",
                                    rest,
                                    images::encoded(&read(
                                        &base.join(filename).parent().unwrap_or(base).join(rest),
                                    )?)?,
                                )?;
                                scene.get_mut("materials", k)?["obj_color_image"] = json!(image);
                            }
                            "Ka" | "Ks" | "Ni" | "illum" => {}
                            _ => return Err(format!("Unsupported MTL property {op}")),
                        }
                    }
                }
            }
            "f" => {
                if fields.len() < 3 {
                    return Err("OBJ faces require at least three vertices".into());
                }
                let mut vs = vec![];
                let mut uv = vec![];
                let mut ns = vec![];
                for f in fields {
                    let parts: Vec<_> = f.split('/').collect();
                    vs.push(obj_index(parts[0], positions.len())?);
                    uv.push(if parts.get(1).is_some_and(|s| !s.is_empty()) {
                        Some(texcoords[obj_index(parts[1], texcoords.len())?])
                    } else {
                        None
                    });
                    ns.push(if parts.get(2).is_some_and(|s| !s.is_empty()) {
                        Some(normals[obj_index(parts[2], normals.len())?])
                    } else {
                        None
                    });
                }
                faces.push(
                    json!({"vertices":vs,"uv":uv,"normals":ns,"material":material,"smooth":smooth}),
                );
            }
            _ => {
                return Err(format!(
                    "Unsupported OBJ statement {op} at line {}",
                    line_no + 1
                ));
            }
        }
    }
    if !faces.is_empty() {
        groups.push((name, faces));
    }
    for k in materials.values() {
        let m = scene.get_mut("materials", *k)?;
        if let Some(image) = m["obj_color_image"].as_u64() {
            m["gltf"] = json!({"base":m["diffuse_color"],"metallic":m["metallic"],"roughness":m["roughness"],"emission":[0.,0.,0.],"color_image":image,"alpha_mode":if num(&m["diffuse_color"][3])<1.{"BLEND"}else{"OPAQUE"}});
        }
    }
    if operator
        && groups
            .iter()
            .any(|(_, faces)| faces.iter().any(|f| f["material"].is_null()))
    {
        let default = scene.create("materials", "Default OBJ", json!({"obj_roughness":0.5}))?;
        for (_, faces) in &mut groups {
            for face in faces {
                if face["material"].is_null() {
                    face["material"] = json!(default);
                }
            }
        }
    }
    for (name, fs) in groups {
        let has_uv = fs
            .iter()
            .any(|f| array(f, "uv").iter().any(|v| !v.is_null()));
        let has_normals = fs
            .iter()
            .any(|f| array(f, "normals").iter().any(|v| !v.is_null()));
        let mut remap = BTreeMap::new();
        let mut vertices = vec![];
        let mut faces = vec![];
        let mut uvs = vec![];
        let mut ns = vec![];
        let mut slots = vec![];
        let mut indices = vec![];
        let mut smoothing = vec![];
        for f in fs {
            let mut face = vec![];
            for i in array(&f, "vertices") {
                let vi = index(i)?;
                let local = *remap.entry(vi).or_insert_with(|| {
                    vertices.push(positions[vi]);
                    vertices.len() - 1
                });
                face.push(local);
            }
            let p: Vec<_> = face.iter().map(|&i| vertices[i]).collect();
            let normal = normalize(cross(sub(p[1], p[0]), sub(p[2], p[0])));
            for n in array(&f, "normals") {
                ns.push(if n.is_null() { normal } else { vec3(n) });
            }
            for uv in array(&f, "uv") {
                uvs.push(if uv.is_null() {
                    [0.; 2]
                } else {
                    [num(&uv[0]), num(&uv[1])]
                });
            }
            let slot = slots
                .iter()
                .position(|v| v == &f["material"])
                .unwrap_or_else(|| {
                    slots.push(f["material"].clone());
                    slots.len() - 1
                });
            indices.push(slot);
            smoothing.push(f["smooth"].clone());
            faces.push(face);
        }
        let k = scene.create("meshes", &name, json!({}))?;
        scene.mesh_from(k, json!(vertices), json!([]), json!(faces), false)?;
        let m = scene.get_mut("meshes", k)?;
        m["materials"] = json!(slots);
        m["material_indices"] = json!(indices);
        m["smooth"] = json!(smoothing);
        m["loop_normals"] = json!(ns);
        m["uv_layers"] = json!([{"name":"UVMap","data":uvs}]);
        if operator && !has_uv {
            m["uv_layers"] = json!([]);
        }
        if operator && !has_normals {
            m["loop_normals"] = json!([]);
        }
        let o = scene.create("objects", &name, json!({"data":{"kind":"meshes","id":k}}))?;
        scene.link(scene.active_collection, o, false, false)?;
    }
    scene.validate()?;
    Ok(vec!["OBJ coordinates interpreted as Z-up meters (OBJ does not declare axis or units). Legacy MTL specular terms map to the metallic/roughness preview model.".into()])
}
struct Writer {
    doc: Value,
    bin: Vec<u8>,
}
impl Writer {
    fn new() -> Self {
        Self {
            doc: json!({"asset":{"version":"2.0","generator":"hb M1"},"scene":0,"scenes":[{"nodes":[]}],"nodes":[],"meshes":[],"materials":[],"accessors":[],"bufferViews":[],"buffers":[],"images":[],"textures":[],"cameras":[]}),
            bin: vec![],
        }
    }
    fn view(&mut self, data: &[u8]) -> usize {
        while !self.bin.len().is_multiple_of(4) {
            self.bin.push(0);
        }
        let at = self.bin.len();
        self.bin.extend_from_slice(data);
        let views = self.doc["bufferViews"].as_array_mut().unwrap();
        let k = views.len();
        views.push(json!({"buffer":0,"byteOffset":at,"byteLength":data.len()}));
        k
    }
    fn attr(&mut self, values: &[Vec<f64>], typ: &str) -> usize {
        let bytes: Vec<u8> = values
            .iter()
            .flatten()
            .flat_map(|n| (*n as f32).to_le_bytes())
            .collect();
        let view = self.view(&bytes);
        let mut a = json!({"bufferView":view,"componentType":5126,"count":values.len(),"type":typ});
        if typ == "VEC3" && !values.is_empty() {
            a["min"] = json!(
                (0..3)
                    .map(|i| values
                        .iter()
                        .map(|v| v[i] as f32)
                        .fold(f32::INFINITY, f32::min))
                    .collect::<Vec<_>>()
            );
            a["max"] = json!(
                (0..3)
                    .map(|i| values
                        .iter()
                        .map(|v| v[i] as f32)
                        .fold(f32::NEG_INFINITY, f32::max))
                    .collect::<Vec<_>>()
            );
        }
        let access = self.doc["accessors"].as_array_mut().unwrap();
        let k = access.len();
        access.push(a);
        k
    }
}
pub fn gltf(scene: &Scene) -> Result<(Value, Vec<u8>, Vec<String>), String> {
    if let Some(evaluated) = super::modeling::for_export(scene)? {
        return gltf(&evaluated);
    }
    let mut w = Writer::new();
    let mut warnings = vec![];
    let mut textures = BTreeMap::new();
    for v in &scene.images {
        let mut color = false;
        let mut data = false;
        for material in &scene.materials {
            let m = Material::from_asset(material)?;
            color |= m.color_image == Some(id(v)) || m.emission_image == Some(id(v));
            data |= m.normal_image == Some(id(v)) || m.mr_image == Some(id(v));
        }
        if color && data && text(&v["colorspace"]) == "Linear Rec.709" {
            return Err("A linear image used for both color and data needs separate image datablocks before export".into());
        }
        let bytes = images::png(v, color)?;
        let view = w.view(&bytes);
        let k = textures.len();
        w.doc["images"]
            .as_array_mut()
            .unwrap()
            .push(json!({"name":v["name"],"bufferView":view,"mimeType":"image/png"}));
        w.doc["textures"]
            .as_array_mut()
            .unwrap()
            .push(json!({"source":k}));
        textures.insert(id(v), k);
    }
    let mut materials = BTreeMap::new();
    for v in &scene.materials {
        let m = Material::from_asset(v)?;
        let mut p = json!({"baseColorFactor":m.base,"metallicFactor":m.metallic,"roughnessFactor":m.roughness});
        if let Some(k) = m.color_image {
            p["baseColorTexture"] = super::material::export_texture(
                &mut w.doc,
                *textures.get(&k).ok_or("Missing color image")?,
                super::material::texture_binding(scene, v, "base_color")?,
            )?;
        }
        if let Some(k) = m.mr_image {
            p["metallicRoughnessTexture"] = super::material::export_texture(
                &mut w.doc,
                *textures.get(&k).ok_or("Missing metallic/roughness image")?,
                super::material::texture_binding(scene, v, "mr")?,
            )?;
        }
        let strength = m.emission.into_iter().fold(1., f64::max);
        let mut out = json!({"name":v["name"],"pbrMetallicRoughness":p,"emissiveFactor":m.emission.map(|x|x/strength),"doubleSided":true,"alphaMode":m.alpha_mode});
        if m.alpha_mode == "MASK" {
            out["alphaCutoff"] = json!(m.cutoff);
        }
        if strength > 1. {
            out["extensions"] =
                json!({"KHR_materials_emissive_strength":{"emissiveStrength":strength}});
        }
        if let Some(k) = m.normal_image {
            out["normalTexture"] = super::material::export_texture(
                &mut w.doc,
                *textures.get(&k).ok_or("Missing normal image")?,
                super::material::texture_binding(scene, v, "normal")?,
            )?;
            out["normalTexture"]["scale"] = json!(m.normal_strength);
        }
        if m.alpha_image.is_some() && m.alpha_image != m.color_image {
            return Err("glTF requires base color and alpha in the same texture; combine the images before export".into());
        }
        if v.get("gltf").is_none()
            && m.alpha_image.is_some()
            && super::material::texture_binding(scene, v, "alpha")?
                != super::material::texture_binding(scene, v, "base_color")?
        {
            return Err("glTF requires matching base-color and alpha texture coordinates/samplers; use the same Image Texture node".into());
        }
        warnings.extend(super::material::export_parameters(v, &m, &mut out));
        if let Some(k) = m.emission_image {
            out["emissiveTexture"] = super::material::export_texture(
                &mut w.doc,
                *textures.get(&k).ok_or("Missing emissive image")?,
                super::material::texture_binding(scene, v, "emission")?,
            )?;
        }
        let mut used = w.doc["extensionsUsed"]
            .as_array()
            .cloned()
            .unwrap_or_default();
        for key in out["extensions"]
            .as_object()
            .into_iter()
            .flat_map(|m| m.keys())
        {
            if !used.contains(&json!(key)) {
                used.push(json!(key));
            }
        }
        if !out["pbrMetallicRoughness"]["baseColorTexture"]["extensions"]["KHR_texture_transform"]
            .is_null()
            && !used.contains(&json!("KHR_texture_transform"))
        {
            used.push(json!("KHR_texture_transform"));
        }
        if !used.is_empty() {
            w.doc["extensionsUsed"] = json!(used);
        }
        materials.insert(id(v), w.doc["materials"].as_array().unwrap().len());
        w.doc["materials"].as_array_mut().unwrap().push(out);
    }
    let mut meshmap = BTreeMap::new();
    for m in &scene.meshes {
        if !scene.objects.iter().any(|o| {
            o["data"]["kind"] == "meshes" && id(&o["data"]) == id(m) && scene.is_linked(id(o))
        }) {
            continue;
        }
        let mut temp = Scene::default();
        temp.meshes.push(m.clone());
        temp.next_id = scene.next_id;
        let k = temp.create(
            "objects",
            "Mesh",
            json!({"data":{"kind":"meshes","id":id(m)}}),
        )?;
        temp.link(1, k, false, false)?;
        let g = Geometry::new(&temp, false)?;
        if g.triangles.is_empty() {
            continue;
        }
        // Group by face material slot even when slots reference the same data or are empty.
        let mut groups: BTreeMap<(usize, Option<u64>), Vec<_>> = BTreeMap::new();
        for t in g.triangles {
            groups
                .entry((t.material_slot, t.material))
                .or_default()
                .push(t);
        }
        let mut primitives = vec![];
        for ((_, material), ts) in groups {
            let mut positions = vec![];
            let mut vertex_ids = vec![];
            let mut normals = vec![];
            let layers = array(m, "uv_layers");
            let mut uv = vec![vec![]; layers.len()];
            let mut colors = vec![];
            for t in ts {
                for i in 0..3 {
                    positions.push(point(Z_TO_Y, t.p[i]).to_vec());
                    vertex_ids.push(t.vertex_indices[i] as u32);
                    // Blender glTF rounds normals to four decimal places before
                    // normalization and vertex deduplication.
                    let normal = direction(Z_TO_Y, t.n[i])
                        .map(|v| ((v as f32) * 10000.).round_ties_even() / 10000.);
                    let length = normal.iter().map(|v| v * v).sum::<f32>().sqrt();
                    normals.push(
                        normal
                            .map(|v| if length > 0. { (v / length) as f64 } else { 0. })
                            .to_vec(),
                    );
                    for (j, layer) in layers.iter().enumerate() {
                        let value = &layer["data"][t.loop_indices[i]];
                        uv[j].push(vec![num(&value[0]), 1. - num(&value[1])]);
                    }
                    colors.push(t.colors[i].to_vec());
                }
            }
            let mut unique = BTreeMap::new();
            let mut ps = vec![];
            let mut ns = vec![];
            let mut us = vec![vec![]; layers.len()];
            let mut cs = vec![];
            let mut ids = vec![];
            for i in 0..positions.len() {
                let mut key: Vec<u32> = positions[i]
                    .iter()
                    .chain(normals[i].iter())
                    .map(|v| if *v == 0. { 0 } else { (*v as f32).to_bits() })
                    .collect();
                key.push(vertex_ids[i]);
                for layer in &uv {
                    key.extend(layer[i].iter().map(|v| (*v as f32).to_bits()));
                }
                if !array(m, "colors").is_empty() {
                    key.extend(colors[i].iter().map(|v| (*v as f32).to_bits()));
                }
                let k = *unique.entry(key).or_insert_with(|| {
                    ps.push(positions[i].clone());
                    ns.push(normals[i].clone());
                    for (layer, values) in us.iter_mut().zip(&uv) {
                        layer.push(values[i].clone());
                    }
                    cs.push(colors[i].clone());
                    ps.len() - 1
                });
                ids.push(k as u32);
            }
            let mut attrs = json!({"POSITION":w.attr(&ps,"VEC3"),"NORMAL":w.attr(&ns,"VEC3")});
            for (i, values) in us.iter().enumerate() {
                attrs[format!("TEXCOORD_{i}")] = json!(w.attr(values, "VEC2"));
            }
            if !array(m, "colors").is_empty() {
                attrs["COLOR_0"] = json!(w.attr(&cs, "VEC4"));
            }
            let bytes: Vec<u8> = ids.iter().flat_map(|i| i.to_le_bytes()).collect();
            let view = w.view(&bytes);
            let accessor = w.doc["accessors"].as_array().unwrap().len();
            w.doc["accessors"].as_array_mut().unwrap().push(
                json!({"bufferView":view,"componentType":5125,"count":ids.len(),"type":"SCALAR"}),
            );
            let mut primitive = json!({"attributes":attrs,"indices":accessor,"mode":4});
            if let Some(k) = material {
                primitive["material"] = json!(materials.get(&k).ok_or("Missing material")?);
            }
            primitives.push(primitive);
        }
        meshmap.insert(id(m), w.doc["meshes"].as_array().unwrap().len());
        w.doc["meshes"]
            .as_array_mut()
            .unwrap()
            .push(json!({"name":m["name"],"primitives":primitives}));
    }
    let mut linked: BTreeSet<_> = scene.linked_ids().into_iter().collect();
    for k in linked.clone() {
        let mut p = scene.object(k)?["parent"].as_u64();
        while let Some(k) = p {
            linked.insert(k);
            p = scene.object(k)?["parent"].as_u64();
        }
    }
    let mut nodemap = BTreeMap::new();
    let mut worlds = BTreeMap::new();
    for k in &linked {
        let o = scene.object(*k)?;
        let special = ["CAMERA", "LIGHT"].contains(&scene.obj_type(o));
        let world = scene.world(*k)?;
        worlds.insert(
            *k,
            if special {
                matmul(Z_TO_Y, world)
            } else {
                matmul(matmul(Z_TO_Y, world), Y_TO_Z)
            },
        );
        nodemap.insert(*k, nodemap.len());
    }
    let aspect = num(&scene.render["resolution_x"]) * num(&scene.render["pixel_aspect_x"])
        / (num(&scene.render["resolution_y"]) * num(&scene.render["pixel_aspect_y"]));
    let mut lights = vec![];
    for k in &linked {
        let o = scene.object(*k)?;
        let parent = o["parent"].as_u64().filter(|k| linked.contains(k));
        let local = if let Some(p) = parent {
            matmul(inverse(worlds[&p])?, worlds[k])
        } else {
            worlds[k]
        };
        let local = if o.get("matrix_parent_inverse").is_some() {
            let decomposed = without_shear(local);
            if local
                .iter()
                .flatten()
                .zip(decomposed.iter().flatten())
                .any(|(a, b)| (a - b).abs() > 1e-6)
            {
                warnings.push(format!("Parent compensation on {} contains shear; glTF removes it to match Blender's TRS export. The scene retains the full transform.", text(&o["name"])));
            }
            decomposed
        } else {
            local
        };
        let mut node = json!({"name":o["name"],"matrix":flat(local)});
        let children: Vec<_> = linked
            .iter()
            .filter(|c| scene.object(**c).unwrap()["parent"].as_u64() == Some(*k))
            .map(|k| nodemap[k])
            .collect();
        if !children.is_empty() {
            node["children"] = json!(children);
        }
        if let Some(m) = meshmap.get(&id(&o["data"])) {
            node["mesh"] = json!(m);
        }
        if scene.obj_type(o) == "CAMERA" {
            let c = scene.get("cameras", id(&o["data"]))?;
            let camera = super::render::Camera::scene(scene, Some(text(&o["name"])), aspect)?;
            if camera.shift.iter().any(|x| x.abs() > 1e-12) {
                warnings.push(format!(
                    "Camera {}: glTF has no lens shift; shift stored in extras.hb_camera",
                    text(&o["name"])
                ));
            }
            let mut out = if camera.perspective {
                json!({"name":c["name"],"type":"perspective","perspective":{"yfov":2.*camera.half_y.atan(),"aspectRatio":aspect,"znear":camera.near,"zfar":camera.far}})
            } else {
                json!({"name":c["name"],"type":"orthographic","orthographic":{"xmag":camera.half_x,"ymag":camera.half_y,"znear":camera.near,"zfar":camera.far}})
            };
            out["extras"] = json!({"hb_camera":c});
            node["camera"] = json!(w.doc["cameras"].as_array().unwrap().len());
            w.doc["cameras"].as_array_mut().unwrap().push(out);
        }
        if scene.obj_type(o) == "LIGHT" {
            let l = scene.get("lights", id(&o["data"]))?;
            let kind = text(&l["type"]);
            if kind == "AREA" {
                node["extras"] = json!({"hb_area_light":l});
                warnings.push(format!("Area light {} stored in extras.hb_area_light; standard glTF supports punctual lights only",text(&o["name"])));
            } else {
                let mut light = json!({"name":l["name"],"type":if kind=="SUN"{"directional"}else if kind=="SPOT"{"spot"}else{"point"},"color":l["color"],"intensity":num(&l["energy"])*683./if kind=="SUN"{1.}else{4.*std::f64::consts::PI}});
                if kind == "SPOT" {
                    let outer = num(&l["spot_size"]) * 0.5;
                    light["spot"] = json!({"outerConeAngle":outer,"innerConeAngle":outer*(1.-num(&l["spot_blend"]))});
                }
                node["extensions"] = json!({"KHR_lights_punctual":{"light":lights.len()}});
                lights.push(light);
            }
        }
        if parent.is_none() {
            w.doc["scenes"][0]["nodes"]
                .as_array_mut()
                .unwrap()
                .push(json!(nodemap[k]));
        }
        w.doc["nodes"].as_array_mut().unwrap().push(node);
    }
    if !lights.is_empty() {
        w.doc["extensions"] = json!({"KHR_lights_punctual":{"lights":lights}});
        if w.doc["extensionsUsed"].is_null() {
            w.doc["extensionsUsed"] = json!([]);
        }
        w.doc["extensionsUsed"]
            .as_array_mut()
            .unwrap()
            .push(json!("KHR_lights_punctual"));
    }
    if w.bin.is_empty() {
        w.doc.as_object_mut().unwrap().remove("buffers");
    } else {
        w.doc["buffers"] = json!([{"byteLength":w.bin.len()}]);
    }
    for field in [
        "meshes",
        "materials",
        "accessors",
        "bufferViews",
        "images",
        "textures",
        "cameras",
    ] {
        if array(&w.doc, field).is_empty() {
            w.doc.as_object_mut().unwrap().remove(field);
        }
    }
    Ok((w.doc, w.bin, warnings))
}
pub fn glb(scene: &Scene) -> Result<(Vec<u8>, Vec<String>), String> {
    let (doc, mut bin, warnings) = gltf(scene)?;
    let mut js = serde_json::to_vec(&doc).map_err(|e| e.to_string())?;
    while js.len() % 4 != 0 {
        js.push(b' ');
    }
    while bin.len() % 4 != 0 {
        bin.push(0);
    }
    let mut out = b"glTF".to_vec();
    out.extend(2u32.to_le_bytes());
    out.extend(
        ((12 + 8 + js.len() + if bin.is_empty() { 0 } else { 8 + bin.len() }) as u32).to_le_bytes(),
    );
    out.extend((js.len() as u32).to_le_bytes());
    out.extend(b"JSON");
    out.extend(js);
    if !bin.is_empty() {
        out.extend((bin.len() as u32).to_le_bytes());
        out.extend(b"BIN\0");
        out.extend(bin);
    }
    Ok((out, warnings))
}
