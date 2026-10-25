pub mod array;
pub mod assembly;
pub mod bevel;
mod bevel_mesh;
pub mod boolean;
pub mod displace;
pub mod geometry;
pub mod groups;
pub mod images;
pub mod io;
#[allow(dead_code)]
pub mod legacy;
pub mod material;
pub mod math;
pub mod meshopt;
pub mod mirror;
pub mod modeling;
mod normal_space;
pub mod obj_export;
pub mod ply;
pub mod render;
pub mod solidify;
pub mod stl;
pub mod subsurf;
pub mod text;
pub mod topology;
pub mod triangulation;
pub mod usdz;
pub mod weighted_normals;
pub mod weld;
pub mod world;
use math::{M4, V3};
use serde::{Deserialize, Serialize};
use serde_json::{Value, json};
use sha2::{Digest, Sha256};
use std::collections::BTreeSet;

#[derive(Clone, Serialize, Deserialize)]
#[serde(deny_unknown_fields)]
pub struct Scene {
    pub objects: Vec<Value>,
    pub meshes: Vec<Value>,
    pub materials: Vec<Value>,
    pub cameras: Vec<Value>,
    pub lights: Vec<Value>,
    pub collections: Vec<Value>,
    pub images: Vec<Value>,
    #[serde(default, skip_serializing_if = "Vec::is_empty")]
    pub textures: Vec<Value>,
    #[serde(default, skip_serializing_if = "Vec::is_empty")]
    pub fonts: Vec<Value>,
    #[serde(default, skip_serializing_if = "Vec::is_empty")]
    pub worlds: Vec<Value>,
    #[serde(default, skip_serializing_if = "Option::is_none")]
    pub scene_world: Option<u64>,
    pub active: Option<u64>,
    pub camera: Option<u64>,
    pub active_collection: u64,
    pub next_id: u64,
    pub render: Value,
}
impl Default for Scene {
    fn default() -> Self {
        Self {
            objects: vec![],
            meshes: vec![],
            materials: vec![],
            cameras: vec![],
            lights: vec![],
            images: vec![],
            textures: vec![],
            fonts: vec![],
            worlds: vec![
                json!({"id":2,"name":"World","color":[0.05087608844041824,0.05087608844041824,0.05087608844041824],"use_nodes":true}),
            ],
            scene_world: Some(2),
            collections: vec![
                json!({"id":0,"name":"Scene Collection","objects":[],"children":[1]}),
                json!({"id":1,"name":"Collection","objects":[],"children":[]}),
            ],
            active: None,
            camera: None,
            active_collection: 1,
            next_id: 3,
            render: json!({"resolution_x":1920,"resolution_y":1080,"resolution_percentage":100,"pixel_aspect_x":1.0,"pixel_aspect_y":1.0,"filepath":"/tmp/","film_transparent":false}),
        }
    }
}
pub fn id(v: &Value) -> u64 {
    v["id"].as_u64().unwrap_or(u64::MAX)
}
pub fn num(v: &Value) -> f64 {
    v.as_f64().unwrap_or(0.)
}
pub fn vec3(v: &Value) -> V3 {
    [num(&v[0]), num(&v[1]), num(&v[2])]
}
pub fn vec4(v: &Value) -> [f64; 4] {
    [num(&v[0]), num(&v[1]), num(&v[2]), num(&v[3])]
}
pub fn text(v: &Value) -> &str {
    v.as_str().unwrap_or("")
}
pub fn f32_value(v: &Value) -> Result<Value, String> {
    match v {
        Value::Number(_) => {
            let n = num(v) as f32;
            if !n.is_finite() {
                return Err("Value must be finite".into());
            }
            Ok(json!(n))
        }
        Value::Array(a) => Ok(Value::Array(
            a.iter().map(f32_value).collect::<Result<_, _>>()?,
        )),
        _ => Err("Expected finite numeric values".into()),
    }
}
pub fn unique(name: &str, names: impl Iterator<Item = String>) -> String {
    let names: BTreeSet<_> = names.collect();
    let mut name = if name.is_empty() { "Object" } else { name }
        .split('\0')
        .next()
        .unwrap_or("")
        .to_string();
    while name.len() > 63 {
        name.pop();
    }
    if !names.contains(&name) {
        return name;
    }
    let base = name
        .rsplit_once('.')
        .filter(|(_, s)| s.len() >= 3 && s.bytes().all(|c| c.is_ascii_digit()))
        .map(|(s, _)| s)
        .unwrap_or(&name);
    for i in 1.. {
        let suffix = format!(".{i:03}");
        let mut base = base.to_string();
        while base.len() + suffix.len() > 63 {
            base.pop();
        }
        let n = base + &suffix;
        if !names.contains(&n) {
            return n;
        }
    }
    unreachable!()
}
impl Scene {
    pub fn db(&self, kind: &str) -> Result<&Vec<Value>, String> {
        match kind {
            "objects" => Ok(&self.objects),
            "meshes" => Ok(&self.meshes),
            "materials" => Ok(&self.materials),
            "cameras" => Ok(&self.cameras),
            "lights" => Ok(&self.lights),
            "collections" => Ok(&self.collections),
            "images" => Ok(&self.images),
            "textures" => Ok(&self.textures),
            "fonts" => Ok(&self.fonts),
            "worlds" => Ok(&self.worlds),
            _ => Err(format!("Unsupported database: {kind}")),
        }
    }
    pub fn db_mut(&mut self, kind: &str) -> Result<&mut Vec<Value>, String> {
        match kind {
            "objects" => Ok(&mut self.objects),
            "meshes" => Ok(&mut self.meshes),
            "materials" => Ok(&mut self.materials),
            "cameras" => Ok(&mut self.cameras),
            "lights" => Ok(&mut self.lights),
            "collections" => Ok(&mut self.collections),
            "images" => Ok(&mut self.images),
            "textures" => Ok(&mut self.textures),
            "fonts" => Ok(&mut self.fonts),
            "worlds" => Ok(&mut self.worlds),
            _ => Err(format!("Unsupported database: {kind}")),
        }
    }
    pub fn get(&self, kind: &str, key: u64) -> Result<&Value, String> {
        self.db(kind)?
            .iter()
            .find(|v| id(v) == key)
            .ok_or(format!("Removed or missing {kind} data block {key}"))
    }
    pub fn get_mut(&mut self, kind: &str, key: u64) -> Result<&mut Value, String> {
        self.db_mut(kind)?
            .iter_mut()
            .find(|v| id(v) == key)
            .ok_or(format!("Removed or missing {kind} data block {key}"))
    }
    pub fn object(&self, key: u64) -> Result<&Value, String> {
        self.get("objects", key)
    }
    pub fn mesh(&self, o: &Value) -> Option<&Value> {
        if o["data"]["kind"] == "meshes" {
            self.get("meshes", id(&o["data"])).ok()
        } else {
            None
        }
    }
    pub fn obj_type(&self, o: &Value) -> &str {
        match text(&o["data"]["kind"]) {
            "meshes" => match self.mesh(o).and_then(|m| m.get("curve")) {
                Some(c) if c["type"] == "FONT" => "FONT",
                Some(_) => "CURVE",
                None => "MESH",
            },
            "cameras" => "CAMERA",
            "lights" => "LIGHT",
            _ => "EMPTY",
        }
    }
    pub fn create(&mut self, kind: &str, name: &str, extra: Value) -> Result<u64, String> {
        let name = unique(
            name,
            self.db(kind)?
                .iter()
                .filter(|v| {
                    kind != "meshes" || v.get("curve").is_some() == extra.get("curve").is_some()
                })
                .map(|v| text(&v["name"]).to_string()),
        );
        let key = self.next_id;
        self.next_id += 1;
        let mut v = match kind {
            "objects" => {
                json!({"data":null,"parent":null,"location":[0.,0.,0.],"rotation_euler":[0.,0.,0.],"scale":[1.,1.,1.],"selected":false,"hide_render":false,"matrix":null,"empty_display_size":1.0,"empty_display_type":"PLAIN_AXES"})
            }
            "meshes" => {
                json!({"vertices":[],"edges":[],"faces":[],"material_indices":[],"smooth":[],"materials":[],"uv_layers":[],"active_uv":0,"loop_normals":[],"colors":[]})
            }
            "materials" => {
                json!({"diffuse_color":[0.8,0.8,0.8,1.],"metallic":0.,"roughness":0.4,"use_nodes":false,"nodes":null,"links":[]})
            }
            "cameras" => {
                json!({"type":"PERSP","lens":50.,"sensor_width":36.,"sensor_height":24.,"sensor_fit":"AUTO","clip_start":0.1,"clip_end":1000.,"ortho_scale":6.,"shift_x":0.,"shift_y":0.})
            }
            "lights" => {
                let t = extra["type"].as_str().unwrap_or("POINT");
                if !["POINT", "SUN", "SPOT", "AREA"].contains(&t) {
                    return Err(format!("Unsupported light type {t}"));
                }
                json!({"type":t,"energy":10.,"color":[1.,1.,1.],"shadow_soft_size":0.0,"size":0.25,"size_y":0.25,"shape":"SQUARE","use_shadow":true,"spot_size":std::f64::consts::FRAC_PI_4,"spot_blend":0.15})
            }
            "collections" => json!({"objects":[],"children":[]}),
            "worlds" => {
                json!({"color":[0.05f32,0.05f32,0.05f32],"use_nodes":false,"nodes":null,"links":[]})
            }
            "textures" => {
                json!({"type":"CLOUDS","noise_basis":"BLENDER_ORIGINAL","noise_scale":0.25,"noise_depth":2,"noise_type":"SOFT_NOISE","cloud_type":"GRAYSCALE","intensity":1.0,"contrast":1.0})
            }
            "fonts" => json!({}),
            "images" => {
                json!({"width":1,"height":1,"pixels":[0.,0.,0.,1.],"float_buffer":false,"filepath":"","colorspace":"sRGB"})
            }
            _ => return Err(format!("Unsupported data type {kind}")),
        };
        if let Some(fields) = extra.as_object() {
            for (k, val) in fields {
                v[k] = val.clone();
            }
        }
        v["id"] = json!(key);
        v["name"] = json!(name);
        self.db_mut(kind)?.push(v);
        Ok(key)
    }
    pub fn linked_ids(&self) -> Vec<u64> {
        let mut out = vec![];
        let mut visited = BTreeSet::new();
        self.walk_collection(0, &mut visited, &mut out);
        out
    }
    fn walk_collection(&self, key: u64, visited: &mut BTreeSet<u64>, out: &mut Vec<u64>) {
        if !visited.insert(key) {
            return;
        }
        if let Ok(c) = self.get("collections", key) {
            for o in c["objects"]
                .as_array()
                .into_iter()
                .flatten()
                .filter_map(Value::as_u64)
            {
                if !out.contains(&o) {
                    out.push(o);
                }
            }
            for child in c["children"]
                .as_array()
                .into_iter()
                .flatten()
                .filter_map(Value::as_u64)
            {
                self.walk_collection(child, visited, out);
            }
        }
    }
    pub fn is_linked(&self, key: u64) -> bool {
        self.linked_ids().contains(&key)
    }
    pub fn local(&self, o: &Value) -> M4 {
        let basis = if let Some(a) = o["matrix"].as_array() {
            math::from_flat(&a.iter().map(num).collect::<Vec<_>>()).unwrap_or(math::IDENTITY)
        } else if o["rotation_mode"] == "QUATERNION" {
            let q = vec4(&o["rotation_quaternion"]);
            let length = q.iter().map(|x| x * x).sum::<f64>().sqrt();
            let mut m = if length > 0. {
                math::quat([q[1] / length, q[2] / length, q[3] / length, q[0] / length])
            } else {
                math::IDENTITY
            };
            for i in 0..3 {
                for j in 0..3 {
                    m[i][j] *= num(&o["scale"][j]);
                }
                m[i][3] = num(&o["location"][i]);
            }
            m
        } else {
            math::trs_order(
                vec3(&o["location"]),
                vec3(&o["rotation_euler"]),
                vec3(&o["scale"]),
                text(&o["rotation_mode"]),
            )
        };
        if !o["parent"].is_null()
            && let Some(a) = o["matrix_parent_inverse"].as_array()
        {
            let inverse =
                math::from_flat(&a.iter().map(num).collect::<Vec<_>>()).unwrap_or(math::IDENTITY);
            math::matmul(inverse, basis)
        } else {
            basis
        }
    }
    pub fn world(&self, key: u64) -> Result<M4, String> {
        let mut chain = vec![];
        let mut cursor = Some(key);
        let mut visited = BTreeSet::new();
        while let Some(k) = cursor {
            if !visited.insert(k) {
                return Err("Cyclic object parent hierarchy".into());
            }
            let o = self.object(k)?;
            chain.push(self.local(o));
            cursor = o["parent"].as_u64();
        }
        Ok(chain.into_iter().rev().fold(math::IDENTITY, math::matmul))
    }
    pub fn users(&self, kind: &str, key: u64) -> usize {
        match kind {
            "fonts" => self
                .meshes
                .iter()
                .filter(|m| m["curve"]["font"].as_u64() == Some(key))
                .count(),
            "objects" => {
                self.collections
                    .iter()
                    .filter(|c| {
                        c["objects"]
                            .as_array()
                            .is_some_and(|a| a.contains(&json!(key)))
                    })
                    .count()
                    + self
                        .objects
                        .iter()
                        .flat_map(|o| o["modifiers"].as_array().into_iter().flatten())
                        .flat_map(|m| {
                            modeling::object_reference_fields(m)
                                .iter()
                                .map(move |field| &m[*field])
                        })
                        .filter(|v| v.as_u64() == Some(key))
                        .count()
            }
            "collections" => {
                self.collections
                    .iter()
                    .filter(|c| {
                        c["children"]
                            .as_array()
                            .is_some_and(|a| a.contains(&json!(key)))
                    })
                    .count()
                    + self
                        .objects
                        .iter()
                        .flat_map(|o| o["modifiers"].as_array().into_iter().flatten())
                        .filter(|m| m["type"] == "BOOLEAN" && m["collection"].as_u64() == Some(key))
                        .count()
            }
            "meshes" | "cameras" | "lights" => self
                .objects
                .iter()
                .filter(|o| o["data"]["kind"] == kind && id(&o["data"]) == key)
                .count(),
            "materials" => self
                .meshes
                .iter()
                .flat_map(|m| m["materials"].as_array().into_iter().flatten())
                .filter(|v| v.as_u64() == Some(key))
                .count(),
            "worlds" => usize::from(self.scene_world == Some(key)),
            "textures" => self
                .objects
                .iter()
                .flat_map(|o| o["modifiers"].as_array().into_iter().flatten())
                .filter(|m| m["type"] == "DISPLACE" && m["texture"].as_u64() == Some(key))
                .count(),
            "images" => {
                self.materials
                    .iter()
                    .chain(self.worlds.iter())
                    .flat_map(|m| m["nodes"].as_array().into_iter().flatten())
                    .filter(|v| v["image"].as_u64() == Some(key))
                    .count()
                    + self
                        .materials
                        .iter()
                        .map(|m| material::asset_image_users(m, key))
                        .sum::<usize>()
            }
            _ => 0,
        }
    }
    pub fn link(
        &mut self,
        collection: u64,
        key: u64,
        children: bool,
        unlink: bool,
    ) -> Result<(), String> {
        let kind = if children { "collections" } else { "objects" };
        self.get(kind, key)?;
        if children && !unlink {
            let mut seen = BTreeSet::new();
            let mut dummy = vec![];
            self.walk_collection(key, &mut seen, &mut dummy);
            if seen.contains(&collection) {
                return Err("Collection cycle is not allowed".into());
            }
        }
        let values = self.get_mut("collections", collection)?
            [if children { "children" } else { "objects" }]
        .as_array_mut()
        .ok_or("Invalid collection")?;
        let pos = values.iter().position(|v| v.as_u64() == Some(key));
        if unlink {
            let p = pos.ok_or("Data block not linked to collection")?;
            values.remove(p);
        } else {
            if pos.is_some() {
                return Err("Data block is already in the collection".into());
            }
            values.push(json!(key));
        }
        Ok(())
    }
    pub fn remove(&mut self, kind: &str, key: u64, do_unlink: bool) -> Result<(), String> {
        self.get(kind, key)?;
        if kind == "collections" && key == 0 {
            return Err("Cannot remove the scene master collection".into());
        }
        if !do_unlink
            && ((kind == "objects"
                && self
                    .collections
                    .iter()
                    .any(|c| c["objects"].as_array().unwrap().contains(&json!(key))))
                || self.users(kind, key) > 0)
        {
            return Err("Data block has users; use do_unlink=True".into());
        }
        match kind {
            "objects" => {
                for c in &mut self.collections {
                    c["objects"]
                        .as_array_mut()
                        .unwrap()
                        .retain(|v| v.as_u64() != Some(key));
                }
                for o in &mut self.objects {
                    if let Some(stack) = o.get_mut("modifiers").and_then(Value::as_array_mut) {
                        for m in stack {
                            for field in modeling::object_reference_fields(m) {
                                if m[*field].as_u64() == Some(key) {
                                    m[*field] = Value::Null;
                                }
                            }
                        }
                    }
                    if o["parent"].as_u64() == Some(key) {
                        o["parent"] = Value::Null;
                    }
                }
                if self.active == Some(key) {
                    self.active = None;
                }
                if self.camera == Some(key) {
                    self.camera = None;
                }
            }
            "collections" => {
                for o in &mut self.objects {
                    if let Some(stack) = o.get_mut("modifiers").and_then(Value::as_array_mut) {
                        for m in stack {
                            if m["type"] == "BOOLEAN" && m["collection"].as_u64() == Some(key) {
                                m["collection"] = Value::Null;
                            }
                        }
                    }
                }
                for c in &mut self.collections {
                    c["children"]
                        .as_array_mut()
                        .unwrap()
                        .retain(|v| v.as_u64() != Some(key));
                }
                if self.active_collection == key {
                    self.active_collection = 0;
                }
            }
            "materials" => {
                for m in &mut self.meshes {
                    for v in m["materials"].as_array_mut().unwrap() {
                        if v.as_u64() == Some(key) {
                            *v = Value::Null;
                        }
                    }
                }
            }
            "worlds" => {
                if self.scene_world == Some(key) {
                    self.scene_world = None;
                }
            }
            "textures" => {
                for o in &mut self.objects {
                    if let Some(stack) = o.get_mut("modifiers").and_then(Value::as_array_mut) {
                        for m in stack {
                            if m["type"] == "DISPLACE" && m["texture"].as_u64() == Some(key) {
                                m["texture"] = Value::Null;
                            }
                        }
                    }
                }
            }
            "images" => {
                for m in self.materials.iter_mut().chain(self.worlds.iter_mut()) {
                    material::unlink_asset_image(m, key);
                    if let Some(nodes) = m["nodes"].as_array_mut() {
                        for n in nodes {
                            if n["image"].as_u64() == Some(key) {
                                n["image"] = Value::Null;
                            }
                        }
                    }
                }
            }
            _ => {
                for o in &mut self.objects {
                    if o["data"]["kind"] == kind && id(&o["data"]) == key {
                        o["data"] = Value::Null;
                    }
                }
            }
        }
        self.db_mut(kind)?.retain(|v| id(v) != key);
        Ok(())
    }
    pub fn mesh_from(
        &mut self,
        key: u64,
        vertices: Value,
        edges: Value,
        faces: Value,
        smooth: bool,
    ) -> Result<(), String> {
        let vertices = f32_value(&vertices)?;
        let vs = vertices.as_array().ok_or("Vertices must be a sequence")?;
        if vs.iter().any(|v| v.as_array().is_none_or(|a| a.len() != 3)) {
            return Err("Each vertex needs three coordinates".into());
        }
        let fs = faces.as_array().ok_or("Faces must be a sequence")?;
        let mut es = edges.as_array().ok_or("Edges must be a sequence")?.clone();
        let mut known = BTreeSet::new();
        for edge in &es {
            let a = edge.as_array().ok_or("Invalid edge")?;
            if a.len() != 2
                || a.iter()
                    .any(|v| v.as_u64().is_none_or(|i| i as usize >= vs.len()))
            {
                return Err("Invalid edge index".into());
            }
            let x = a[0].as_u64().unwrap();
            let y = a[1].as_u64().unwrap();
            known.insert((x.min(y), x.max(y)));
        }
        for face in fs {
            let f = face.as_array().ok_or("Invalid face")?;
            if f.len() < 3
                || f.iter()
                    .any(|v| v.as_u64().is_none_or(|i| i as usize >= vs.len()))
            {
                return Err("Faces need at least three valid vertex indices".into());
            }
            for i in 0..f.len() {
                let a = f[i].as_u64().unwrap();
                let b = f[(i + 1) % f.len()].as_u64().unwrap();
                if known.insert((a.min(b), a.max(b))) {
                    es.push(json!([a, b]));
                }
            }
        }
        let n = fs.len();
        let m = self.get_mut("meshes", key)?;
        m["vertices"] = vertices;
        m["edges"] = json!(es);
        m["faces"] = faces;
        m["material_indices"] = json!(vec![0; n]);
        m["smooth"] = json!(vec![smooth; n]);
        m["uv_layers"] = json!([]);
        m["loop_normals"] = json!([]);
        m["colors"] = json!([]);
        m.as_object_mut().unwrap().remove("deform_weights");
        m.as_object_mut().unwrap().remove("crease_edge");
        m.as_object_mut().unwrap().remove("crease_vert");
        m.as_object_mut().unwrap().remove("face_strength");
        Ok(())
    }
    pub fn cube(&mut self, r: &Value) -> Result<u64, String> {
        let s = (num(&r["size"]) as f32).clamp(0., 1e12) / 2.;
        let scale = vec3(&r["scale"]);
        let vs = [
            [-s, -s, -s],
            [-s, -s, s],
            [-s, s, -s],
            [-s, s, s],
            [s, -s, -s],
            [s, -s, s],
            [s, s, -s],
            [s, s, s],
        ]
        .map(|v| std::array::from_fn::<_, 3, _>(|i| v[i] * (scale[i] as f32)));
        let mesh = self.create("meshes", "Cube", json!({}))?;
        self.mesh_from(
            mesh,
            json!(vs),
            json!([]),
            json!([
                [0, 1, 3, 2],
                [2, 3, 7, 6],
                [6, 7, 5, 4],
                [4, 5, 1, 0],
                [2, 6, 4, 0],
                [7, 3, 1, 5]
            ]),
            false,
        )?;
        if r["calc_uvs"].as_bool().unwrap_or(true) {
            self.get_mut("meshes", mesh)?["uv_layers"] = json!([{"name":"UVMap","data":cube_uv()}]);
        }
        let obj=self.create("objects","Cube",json!({"data":{"kind":"meshes","id":mesh},"location":f32_value(&r["location"])?,"rotation_euler":f32_value(&r["rotation"])?}))?;
        let linked = self.linked_ids();
        for o in &mut self.objects {
            if linked.contains(&id(o)) {
                o["selected"] = json!(false);
            }
        }
        self.link(self.active_collection, obj, false, false)?;
        self.get_mut("objects", obj)?["selected"] = json!(true);
        self.active = Some(obj);
        Ok(obj)
    }
    pub fn request(&mut self, r: Value) -> Result<Value, String> {
        let op = text(&r["op"]);
        let kind = r["kind"].as_str().unwrap_or("objects");
        let key = r["id"].as_u64().unwrap_or(0);
        match op {
            "dimensions" | "set_dimensions" => {
                let object = self.object(key)?;
                let mesh = modeling::evaluated_mesh(self, object, false)?;
                let mut minimum = [f32::INFINITY; 3];
                let mut maximum = [f32::NEG_INFINITY; 3];
                if let Some(mesh) = mesh.as_ref() {
                    for vertex in mesh["vertices"].as_array().ok_or("Invalid mesh vertices")? {
                        for axis in 0..3 {
                            let coordinate = num(&vertex[axis]) as f32;
                            minimum[axis] = minimum[axis].min(coordinate);
                            maximum[axis] = maximum[axis].max(coordinate);
                        }
                    }
                }
                let extent: [f32; 3] = std::array::from_fn(|i| {
                    if minimum[i].is_finite() {
                        maximum[i] - minimum[i]
                    } else {
                        0.
                    }
                });
                if op == "dimensions" {
                    let world = self.world(key)?;
                    let dimensions: [f32; 3] = std::array::from_fn(|axis| {
                        let scale = (0..3)
                            .map(|row| (world[row][axis] as f32).powi(2))
                            .sum::<f32>()
                            .sqrt();
                        extent[axis] * scale
                    });
                    Ok(json!(dimensions))
                } else {
                    let values = r["value"]
                        .as_array()
                        .filter(|v| v.len() == 3)
                        .ok_or("Expected three dimensions")?;
                    let mut scale = vec3(&object["scale"]);
                    for axis in 0..3 {
                        let value =
                            values[axis].as_f64().ok_or("Expected finite dimensions")? as f32;
                        if !value.is_finite() {
                            return Err("Expected finite dimensions".into());
                        }
                        if extent[axis] > 0. {
                            scale[axis] = (value.abs() / extent[axis]) as f64
                                * if scale[axis] < 0. { -1. } else { 1. };
                        }
                    }
                    let object = self.get_mut("objects", key)?;
                    object["scale"] = json!(scale);
                    object["matrix"] = Value::Null;
                    Ok(Value::Null)
                }
            }
            "read" | "length" => {
                if kind == "lights"
                    && op == "read"
                    && r["path"].as_array().is_some_and(|a| a.len() == 1)
                {
                    let field = text(&r["path"][0]);
                    let fallback = match field {
                        "shape" => Some(json!("SQUARE")),
                        "size_y" => Some(json!(0.25)),
                        "use_shadow" => Some(json!(true)),
                        _ => None,
                    };
                    if let Some(fallback) = fallback {
                        return Ok(self.get(kind, key)?.get(field).cloned().unwrap_or(fallback));
                    }
                }
                if kind == "objects" && op == "read" {
                    if r["path"] == json!(["empty_display_size"]) {
                        return Ok(self
                            .object(key)?
                            .get("empty_display_size")
                            .cloned()
                            .unwrap_or(json!(1.0)));
                    }
                    if r["path"] == json!(["empty_display_type"]) {
                        return Ok(self
                            .object(key)?
                            .get("empty_display_type")
                            .cloned()
                            .unwrap_or(json!("PLAIN_AXES")));
                    }
                }
                let mut v = self.get(kind, key)?;
                for step in r["path"].as_array().ok_or("Missing data path")? {
                    v = if let Some(k) = step.as_str() {
                        v.get(k)
                    } else {
                        step.as_u64().and_then(|i| v.get(i as usize))
                    }
                    .ok_or("Invalid data path")?;
                }
                if op == "length" {
                    Ok(json!(v.as_array().ok_or("Not a sequence")?.len()))
                } else {
                    Ok(v.clone())
                }
            }
            "write" => {
                let mut v = self.get_mut(kind, key)?;
                for step in r["path"].as_array().ok_or("Missing data path")? {
                    v = if let Some(k) = step.as_str() {
                        v.get_mut(k)
                    } else {
                        step.as_u64().and_then(|i| v.get_mut(i as usize))
                    }
                    .ok_or("Invalid data path")?;
                }
                *v = r["value"].clone();
                Ok(Value::Null)
            }
            "mesh_update" => {
                self.validate()?;
                Ok(Value::Null)
            }
            "image_new" => {
                let w = r["width"].as_u64().ok_or("Invalid image width")?;
                let h = r["height"].as_u64().ok_or("Invalid image height")?;
                if w == 0 || h == 0 || w * h > 16777216 {
                    return Err("Images require 1–16,777,216 pixels".into());
                }
                let alpha = 1.;
                Ok(json!(self.create("images",text(&r["name"]),json!({"width":w,"height":h,"pixels":[0.,0.,0.,alpha],"solid":true,"float_buffer":r["float_buffer"],"colorspace":if r["is_data"]==true{"Non-Color"}else if r["float_buffer"]==true{"Linear Rec.709"}else{"sRGB"}}))?))
            }
            "texture_evaluate" => Ok(json!([
                0.,
                0.,
                0.,
                displace::texture(
                    self.get("textures", key)?,
                    vec3(&r["position"]).map(|x| x as f32)
                )?
            ])),
            "image_pixels" => Ok(json!(images::pixels(self.get("images", key)?)?)),
            "image_set_pixels" => {
                let v = self.get_mut("images", key)?;
                let mut pixels = r["pixels"]
                    .as_array()
                    .ok_or("Invalid pixel sequence")?
                    .clone();
                if pixels.len() != (num(&v["width"]) * num(&v["height"]) * 4.) as usize {
                    return Err("Wrong pixel count".into());
                }
                if v["float_buffer"] != true {
                    for p in &mut pixels {
                        *p = json!((num(p).clamp(0., 1.) * 255.).round() / 255.);
                    }
                }
                v["pixels"] = json!(pixels);
                v["solid"] = json!(false);
                v["encoded"] = Value::Null;
                Ok(Value::Null)
            }
            "snapshot" => Ok(serde_json::to_value(&self).unwrap()),
            "get" => {
                let mut v = self.get(kind, key)?.clone();
                v["users"] = json!(self.users(kind, key));
                if kind == "objects" {
                    v["type"] = json!(self.obj_type(&v));
                    v["linked"] = json!(self.is_linked(key));
                    v["children"] = json!(
                        self.objects
                            .iter()
                            .filter(|o| o["parent"].as_u64() == Some(key))
                            .map(id)
                            .collect::<Vec<_>>()
                    );
                    v["users_collection"] = json!(
                        self.collections
                            .iter()
                            .filter(|c| c["objects"].as_array().unwrap().contains(&json!(key)))
                            .map(id)
                            .collect::<Vec<_>>()
                    );
                }
                Ok(v)
            }
            "list" => {
                let mut records: Vec<_> = self
                    .db(kind)?
                    .iter()
                    .filter(|v| kind != "collections" || id(v) != 0)
                    .collect();
                records.sort_by_key(|v| text(&v["name"]).to_ascii_lowercase());
                Ok(json!(records.into_iter().map(id).collect::<Vec<_>>()))
            }
            "linked" => Ok(json!(self.linked_ids())),
            "active" => Ok(json!(self.active)),
            "settings" => Ok(
                json!({"camera":self.camera,"world":self.scene_world,"active_collection":self.active_collection,"render":self.render}),
            ),
            "set_active" => {
                let id = r["value"].as_u64();
                if let Some(k) = id
                    && !self.is_linked(k)
                {
                    return Err("Active object must belong to the view layer".into());
                }
                self.active = id;
                Ok(Value::Null)
            }
            "set_camera" => {
                let id = r["value"].as_u64();
                if let Some(k) = id
                    && self.obj_type(self.object(k)?) != "CAMERA"
                {
                    return Err("Scene camera must be a camera object".into());
                }
                self.camera = id;
                Ok(Value::Null)
            }
            "set_world" => {
                let key = r["value"].as_u64();
                if let Some(key) = key {
                    self.get("worlds", key)?;
                }
                self.scene_world = key;
                Ok(Value::Null)
            }
            "set_render" => {
                let field = text(&r["field"]);
                if self.render.get(field).is_none() {
                    return Err(format!("Unsupported render setting {field}"));
                }
                self.render[field] = r["value"].clone();
                Ok(Value::Null)
            }
            "new" => Ok(json!(self.create(
                kind,
                text(&r["name"]),
                r.get("extra").cloned().unwrap_or(json!({}))
            )?)),
            "modifier_stack" => {
                modeling::validate(&r["value"])?;
                if self.obj_type(self.object(key)?) != "MESH" {
                    return Err("Modifiers require a mesh object".into());
                }
                for m in r["value"].as_array().unwrap() {
                    if m["type"] == "BOOLEAN"
                        && let Some(collection) = m["collection"].as_u64()
                    {
                        self.get("collections", collection)?;
                    }
                    if m["type"] == "ARRAY" {
                        for field in modeling::object_reference_fields(m) {
                            if let Some(reference) = m[*field].as_u64() {
                                let referenced = self.object(reference)?;
                                if *field != "offset_object"
                                    && (reference == key || self.obj_type(referenced) != "MESH")
                                {
                                    return Err("ARRAY caps require a different mesh object".into());
                                }
                            }
                        }
                    }
                    if m["type"] == "BOOLEAN"
                        && let Some(operand) = m["object"].as_u64()
                        && (operand == key || self.obj_type(self.object(operand)?) != "MESH")
                    {
                        return Err("BOOLEAN requires a different mesh object operand".into());
                    }
                }
                let o = self.get_mut("objects", key)?;
                o["modifiers"] = r["value"].clone();
                if let Some(next) = r.get("next_id") {
                    o["modifier_next_id"] = next.clone();
                }
                Ok(Value::Null)
            }
            "group_edit" => groups::edit(self, key, &r),
            "join" => Ok(json!(assembly::join(self, key)?)),
            "transform_apply" => {
                let o = self.object(key)?.clone();
                let mesh = self
                    .mesh(&o)
                    .ok_or("Transform application requires a mesh")?;
                if mesh.get("shape_keys").is_some() {
                    return Err("Apply transforms before creating shape keys".into());
                }
                let old = self.local(&o);
                let mut updated = o.clone();
                for (flag, field, default) in [
                    ("location", "location", json!([0., 0., 0.])),
                    ("rotation", "rotation_euler", json!([0., 0., 0.])),
                    ("scale", "scale", json!([1., 1., 1.])),
                ] {
                    if r[flag] == true {
                        updated[field] = default;
                    }
                }
                if r["rotation"] == true {
                    updated["rotation_quaternion"] = json!([1., 0., 0., 0.]);
                }
                let remaining = self.local(&updated);
                let matrix = math::matmul(math::inverse(remaining)?, old);
                let mesh_key = id(mesh);
                let mut transformed = mesh.clone();
                transformed["vertices"] = f32_value(&json!(
                    mesh["vertices"]
                        .as_array()
                        .unwrap()
                        .iter()
                        .map(|p| math::point(matrix, vec3(p)))
                        .collect::<Vec<_>>()
                ))?;
                transformed["loop_normals"] = f32_value(&json!(
                    mesh["loop_normals"]
                        .as_array()
                        .unwrap()
                        .iter()
                        .map(|p| math::normal(matrix, vec3(p)))
                        .collect::<Vec<_>>()
                ))?;
                *self.get_mut("meshes", mesh_key)? = transformed;
                *self.get_mut("objects", key)? = updated;
                Ok(Value::Null)
            }
            "modifier_apply" => {
                let o = self.object(key)?;
                let stack = o["modifiers"].as_array().ok_or("Missing modifier")?;
                let modifier = stack.first().ok_or("Empty modifier stack")?;
                if modifier["type"] == "BEVEL" && num(&modifier["width"]) == 0. {
                    return Err("Error: Modifier is disabled, skipping apply".into());
                }
                let mesh = self.mesh(o).ok_or("Modifier requires a mesh")?;
                if self.users("meshes", id(mesh)) != 1 {
                    return Err("Cannot apply modifier to shared mesh data".into());
                }
                if modifier["type"] == "SUBSURF" && modifier["levels"] == 0 {
                    return Err("Error: Modifier is disabled, skipping apply".into());
                }
                if modifier["type"] == "BOOLEAN"
                    && modifier[if modifier["operand_type"] == "COLLECTION" {
                        "collection"
                    } else {
                        "object"
                    }]
                    .is_null()
                {
                    return Err("Error: Modifier is disabled, skipping apply".into());
                }
                let updated =
                    modeling::apply_in_scene(self, o, mesh, modifier, false, &mut vec![key])?;
                let mesh_key = id(mesh);
                *self.get_mut("meshes", mesh_key)? = updated;
                self.get_mut("objects", key)?["modifiers"]
                    .as_array_mut()
                    .unwrap()
                    .remove(0);
                Ok(Value::Null)
            }
            "cube" => Ok(json!(self.cube(&r)?)),
            "text_triangulate" => text::triangulate(&r["contours"]),
            "bmesh_publish" => {
                let mut candidate = self.clone();
                let data = &r["mesh"];
                candidate.mesh_from(
                    key,
                    data["vertices"].clone(),
                    data["edges"].clone(),
                    data["faces"].clone(),
                    false,
                )?;
                let mesh = candidate.get_mut("meshes", key)?;
                for field in [
                    "material_indices",
                    "smooth",
                    "uv_layers",
                    "active_uv",
                    "loop_normals",
                    "colors",
                ] {
                    mesh[field] = data[field].clone();
                }
                for field in ["color_attribute_name", "shape_keys"] {
                    if let Some(value) = data.get(field) {
                        mesh[field] = value.clone();
                    } else {
                        mesh.as_object_mut().unwrap().remove(field);
                    }
                }
                if !mesh["loop_normals"]
                    .as_array()
                    .ok_or("Invalid corner normals")?
                    .is_empty()
                {
                    if mesh["smooth"].as_array().unwrap().iter().any(|v| v == true) {
                        return Err("BMesh packed-normal round trips require flat faces".into());
                    }
                    let custom = mesh["loop_normals"].as_array().unwrap();
                    let mut output = vec![];
                    let mut start = 0;
                    for face in topology::faces(mesh) {
                        let points: Vec<_> = face
                            .iter()
                            .map(|&i| vec3(&mesh["vertices"][i]).map(|v| v as f32))
                            .collect();
                        for corner in 0..face.len() {
                            output.push(weighted_normals::quantize_corner(
                                &points,
                                corner,
                                vec3(&custom[start + corner]).map(|v| v as f32),
                            ));
                        }
                        start += face.len();
                    }
                    mesh["loop_normals"] = json!(output);
                }
                candidate.validate()?;
                *self = candidate;
                Ok(Value::Null)
            }
            "bmesh_triangulate" => {
                let polygons = r["polygons"].as_array().ok_or("Expected polygon arrays")?;
                let mut result = vec![];
                for polygon in polygons {
                    let points: Vec<_> = polygon
                        .as_array()
                        .ok_or("Expected polygon coordinates")?
                        .iter()
                        .map(vec3)
                        .collect();
                    result.push(triangulation::polygon(
                        &points,
                        text(&r["quad_method"]),
                        text(&r["ngon_method"]),
                    )?);
                }
                Ok(json!(result))
            }
            "bmesh_bevel" => {
                let width = r["width"]
                    .as_f64()
                    .filter(|v| v.is_finite() && *v > 0.)
                    .ok_or("Expected positive bevel width")?;
                let segments = r["segments"]
                    .as_u64()
                    .filter(|n| (1..=8).contains(n))
                    .ok_or("Bevel segments must be 1..8")?;
                let mut candidate = Scene::default();
                let key = candidate.create("meshes", "BMesh", json!({}))?;
                candidate.mesh_from(
                    key,
                    r["mesh"]["vertices"].clone(),
                    json!([]),
                    r["mesh"]["faces"].clone(),
                    false,
                )?;
                let mesh = candidate.get_mut("meshes", key)?;
                mesh["material_indices"] = r["mesh"]["material_indices"].clone();
                mesh["smooth"] = r["mesh"]["smooth"].clone();
                candidate.validate()?;
                bevel::apply(
                    candidate.get("meshes", key)?,
                    &json!({"width":width,"segments":segments,"limit_method":"NONE"}),
                )
            }
            "copy" => {
                let mut v = self.get(kind, key)?.clone();
                let name = text(&v["name"]).to_string();
                v.as_object_mut().unwrap().remove("id");
                v.as_object_mut().unwrap().remove("name");
                Ok(json!(self.create(kind, &name, v)?))
            }
            "remove" => {
                self.remove(kind, key, r["do_unlink"].as_bool().unwrap_or(true))?;
                Ok(Value::Null)
            }
            "set" => {
                let field = text(&r["field"]);
                let mut value = r["value"].clone();
                if field == "name" {
                    value = json!(unique(
                        text(&value),
                        self.db(kind)?
                            .iter()
                            .filter(|v| id(v) != key
                                && (kind != "meshes"
                                    || v.get("curve").is_some()
                                        == self.get(kind, key).unwrap().get("curve").is_some()))
                            .map(|v| text(&v["name"]).to_string())
                    ));
                }
                if ["location", "rotation_euler", "scale"].contains(&field) {
                    value = f32_value(&value)?;
                    if value.as_array().is_none_or(|v| v.len() != 3) {
                        return Err("Expected three transform components".into());
                    }
                    self.get_mut(kind, key)?["matrix"] = Value::Null;
                }
                if kind == "objects" && field == "rotation_quaternion" {
                    value = f32_value(&value)?;
                    if value.as_array().is_none_or(|v| v.len() != 4) {
                        return Err("Expected four quaternion components".into());
                    }
                    self.get_mut(kind, key)?["matrix"] = Value::Null;
                }
                if kind == "objects" && field == "rotation_mode" {
                    if !["XYZ", "XZY", "YXZ", "YZX", "ZXY", "ZYX", "QUATERNION"]
                        .contains(&text(&value))
                    {
                        return Err("Unsupported rotation mode".into());
                    }
                    self.get_mut(kind, key)?["matrix"] = Value::Null;
                }
                if kind == "objects" && field == "parent" {
                    let mut cursor = value.as_u64();
                    while let Some(k) = cursor {
                        if k == key {
                            return Err("Cyclic parent relation".into());
                        }
                        cursor = self.object(k)?["parent"].as_u64();
                    }
                }
                if kind == "meshes" && ["crease_edge", "crease_vert"].contains(&field) {
                    let values = f32_value(&r["value"])?;
                    let mesh = self.get(kind, key)?;
                    let count = mesh[if field == "crease_edge" {
                        "edges"
                    } else {
                        "vertices"
                    }]
                    .as_array()
                    .unwrap()
                    .len();
                    if values.as_array().is_none_or(|a| {
                        a.len() != count
                            || a.iter()
                                .any(|v| v.as_f64().is_none_or(|x| !(0. ..=1.).contains(&x)))
                    }) {
                        return Err(
                            "Crease attributes need one finite value in 0..1 per element".into(),
                        );
                    }
                    self.get_mut(kind, key)?[field] = values;
                    return Ok(Value::Null);
                }
                if kind == "meshes" && field == "shape_keys" {
                    let mut candidate = self.clone();
                    candidate.get_mut(kind, key)?[field] = value;
                    candidate.validate()?;
                    *self = candidate;
                    return Ok(Value::Null);
                }
                if kind == "meshes" && field == "face_strength" {
                    let count = self.get(kind, key)?["faces"].as_array().unwrap().len();
                    if value.as_array().is_none_or(|a| {
                        a.len() != count
                            || a.iter()
                                .any(|v| v.as_i64().is_none_or(|v| !(0..=2).contains(&v)))
                    }) {
                        return Err("Face strength needs one integer in 0..2 per face".into());
                    }
                    self.get_mut(kind, key)?[field] = value;
                    return Ok(Value::Null);
                }
                if kind == "meshes" && field == "color_attribute_name" {
                    let value = r["value"]
                        .as_str()
                        .filter(|s| !s.is_empty() && s.len() <= 63)
                        .ok_or("Color attribute name requires 1..63 UTF-8 bytes")?;
                    self.get_mut(kind, key)?[field] = json!(value);
                    return Ok(Value::Null);
                }
                if kind == "objects" && field == "matrix_parent_inverse" {
                    value = f32_value(&value)?;
                    if value.as_array().is_none_or(|v| v.len() != 16) {
                        return Err("Expected a 4x4 parent inverse matrix".into());
                    }
                }
                if kind == "objects" && field == "data" && !value.is_null() {
                    self.get(text(&value["kind"]), id(&value))?;
                }
                if kind == "objects" && field == "selected" && !self.is_linked(key) {
                    return Err("Object is not in the view layer".into());
                }
                if self.get(kind, key)?.get(field).is_none()
                    && !(kind == "objects"
                        && [
                            "empty_display_size",
                            "empty_display_type",
                            "matrix_parent_inverse",
                            "rotation_mode",
                            "rotation_quaternion",
                        ]
                        .contains(&field))
                    && !(kind == "lights" && ["shape", "size_y", "use_shadow"].contains(&field))
                    && !(kind == "worlds" && ["nodes", "links"].contains(&field))
                    && !(kind == "meshes" && field == "render_uv")
                {
                    return Err(format!("Unsupported property {kind}.{field}"));
                }
                if kind == "images" && field == "colorspace" {
                    let v = self.get_mut(kind, key)?;
                    if v["encoded"].is_null() {
                        v["pixels"] = json!([0., 0., 0., 1.]);
                        v["solid"] = json!(true);
                    }
                }
                if kind == "materials" {
                    let v = self.get_mut(kind, key)?;
                    if v.get("gltf").is_some() {
                        match field {
                            "diffuse_color" if v["use_nodes"] != true => {
                                v["gltf"]["base"] = value.clone()
                            }
                            "metallic" | "roughness" if v["use_nodes"] != true => {
                                v["gltf"][field] = value.clone()
                            }
                            "nodes" if v["use_nodes"] == true => {
                                if let Some(node) = value.as_array().and_then(|nodes| {
                                    nodes
                                        .iter()
                                        .find(|n| n["type"] == "ShaderNodeBsdfPrincipled")
                                }) {
                                    let inputs = &node["inputs"];
                                    let mut base = inputs["Base Color"].clone();
                                    base[3] = inputs["Alpha"].clone();
                                    if base[3] != v["gltf"]["base"][3] {
                                        v["gltf"]["alpha_mode"] = json!(if num(&base[3]) < 1. {
                                            "BLEND"
                                        } else {
                                            "OPAQUE"
                                        });
                                    }
                                    v["gltf"]["base"] = base;
                                    v["gltf"]["metallic"] = inputs["Metallic"].clone();
                                    v["gltf"]["roughness"] = inputs["Roughness"].clone();
                                    v["gltf"]["transmission"] =
                                        json!(inputs["Transmission Weight"].as_f64().unwrap_or(0.));
                                    v["gltf"]["ior"] = json!(inputs["IOR"].as_f64().unwrap_or(1.5));
                                    v["gltf"]["principled"] = inputs.clone();
                                    v["gltf"]["emission"] = json!(math::mul(
                                        vec3(&inputs["Emission Color"]),
                                        num(&inputs["Emission Strength"])
                                    ));
                                } else {
                                    v.as_object_mut().unwrap().remove("gltf");
                                }
                            }
                            "use_nodes" if value == true && v["use_nodes"] != true => {
                                v.as_object_mut().unwrap().remove("gltf");
                            }
                            _ => {}
                        }
                    }
                }
                self.get_mut(kind, key)?[field] = value;
                Ok(Value::Null)
            }
            "link" => {
                self.link(
                    key,
                    r["target"].as_u64().ok_or("Missing target")?,
                    r["children"].as_bool().unwrap_or(false),
                    r["unlink"].as_bool().unwrap_or(false),
                )?;
                Ok(Value::Null)
            }
            "mesh_from" => {
                self.mesh_from(
                    key,
                    r["vertices"].clone(),
                    r["edges"].clone(),
                    r["faces"].clone(),
                    r["smooth"].as_bool().unwrap_or(false),
                )?;
                Ok(Value::Null)
            }
            "image_load" => {
                let path = text(&r["path"]);
                if r["check_existing"] == true
                    && let Some(v) = self.images.iter().find(|v| text(&v["filepath"]) == path)
                {
                    return Ok(json!(id(v)));
                }
                let bytes = std::fs::read(path).map_err(|e| e.to_string())?;
                let mut extra = images::encoded(&bytes)?;
                extra["filepath"] = json!(path);
                Ok(json!(
                    self.create(
                        "images",
                        std::path::Path::new(path)
                            .file_name()
                            .and_then(|n| n.to_str())
                            .unwrap_or("Image"),
                        extra
                    )?
                ))
            }
            "import_gltf" => Ok(json!(io::bpy_import_gltf(
                self,
                std::path::Path::new(text(&r["path"]))
            )?)),
            "export_gltf" => Ok(json!(io::bpy_export_gltf(self, &r)?)),
            "import_obj" => Ok(json!(io::bpy_import_obj(self, &r)?)),
            "render_operator" => Ok(json!(render::bpy_render(self, r["write_still"] == true)?)),
            "export_obj" => Ok(json!(obj_export::export(
                self,
                std::path::Path::new(text(&r["path"])),
                &r
            )?)),
            "update" => {
                self.validate()?;
                Ok(Value::Null)
            }
            "object_basis" => {
                let rotation_field = text(&r["rotation_field"]);
                if !["rotation_euler", "rotation_quaternion"].contains(&rotation_field) {
                    return Err("Invalid rotation field".into());
                }
                let mut candidate = self.clone();
                let obj = candidate.get_mut("objects", key)?;
                for (field, value, count) in [
                    ("location", &r["location"], 3),
                    ("scale", &r["scale"], 3),
                    (
                        rotation_field,
                        &r["rotation"],
                        if rotation_field == "rotation_euler" {
                            3
                        } else {
                            4
                        },
                    ),
                ] {
                    let value = f32_value(value)?;
                    if value.as_array().is_none_or(|values| values.len() != count) {
                        return Err("Invalid object basis component count".into());
                    }
                    obj[field] = value;
                }
                obj["matrix"] = Value::Null;
                candidate.validate()?;
                *self = candidate;
                Ok(Value::Null)
            }
            "world" => Ok(json!(self.world(key)?)),
            _ => Err(format!("Unknown core operation {op}")),
        }
    }
    pub fn validate(&self) -> Result<(), String> {
        let mut ids = BTreeSet::new();
        for kind in [
            "objects",
            "meshes",
            "materials",
            "cameras",
            "lights",
            "collections",
            "images",
            "textures",
            "fonts",
            "worlds",
        ] {
            let mut names = BTreeSet::new();
            for v in self.db(kind)? {
                if !ids.insert(id(v))
                    || id(v) >= self.next_id
                    || !names.insert((
                        text(&v["name"]),
                        kind == "meshes" && v.get("curve").is_some(),
                    ))
                {
                    return Err("Duplicate or invalid data-block identifier/name".into());
                }
            }
        }
        if let Some(key) = self.scene_world {
            self.get("worlds", key)?;
        }
        for world in &self.worlds {
            if world["color"].as_array().is_none_or(|v| {
                v.len() != 3
                    || v.iter()
                        .any(|c| c.as_f64().is_none_or(|n| !n.is_finite() || n < 0.))
            }) {
                return Err("Invalid world color".into());
            }
        }
        for font in &self.fonts {
            text::validate_font(font)?;
        }
        for t in &self.textures {
            displace::validate_texture(t)?;
        }
        for o in &self.objects {
            if let Some(groups) = o.get("vertex_groups") {
                let groups = groups.as_array().ok_or("Invalid vertex groups")?;
                let mut names = BTreeSet::new();
                let mut keys = BTreeSet::new();
                if groups.len() > 1024 {
                    return Err("Vertex group limit exceeded".into());
                }
                for group in groups {
                    if group["name"].as_str().is_none()
                        || !names.insert(text(&group["name"]))
                        || group["key"].as_u64().is_none()
                        || !keys.insert(group["key"].as_u64().unwrap())
                    {
                        return Err("Invalid vertex group name/key".into());
                    }
                }
            }
            if o["rotation_mode"] == "QUATERNION"
                && o["rotation_quaternion"].as_array().is_none_or(|v| {
                    v.len() != 4 || v.iter().any(|x| x.as_f64().is_none_or(|n| !n.is_finite()))
                })
            {
                return Err("Invalid object quaternion".into());
            }
            if let Some(matrix) = o.get("matrix_parent_inverse")
                && matrix.as_array().is_none_or(|v| {
                    v.len() != 16 || v.iter().any(|x| x.as_f64().is_none_or(|n| !n.is_finite()))
                })
            {
                return Err("Invalid parent inverse matrix".into());
            }
            if let Some(stack) = o.get("modifiers") {
                modeling::validate(stack)?;
                for modifier in stack.as_array().unwrap() {
                    if modifier["type"] == "BOOLEAN"
                        && let Some(collection) = modifier["collection"].as_u64()
                    {
                        self.get("collections", collection)?;
                    }
                    for field in modeling::object_reference_fields(modifier) {
                        if let Some(reference) = modifier[*field].as_u64() {
                            self.object(reference)?;
                        }
                    }
                    if modifier["type"] == "DISPLACE"
                        && let Some(key) = modifier["texture"].as_u64()
                    {
                        self.get("textures", key)?;
                    }
                }
            }
            if !o["data"].is_null() {
                self.get(text(&o["data"]["kind"]), id(&o["data"]))?;
            }
            self.world(id(o))?;
            for field in ["location", "rotation_euler", "scale"] {
                let a = o[field].as_array().ok_or("Invalid transform")?;
                if a.len() != 3 || a.iter().any(|v| v.as_f64().is_none_or(|n| !n.is_finite())) {
                    return Err("Invalid/nonfinite transform".into());
                }
            }
        }
        for m in &self.meshes {
            if let Some(curve) = m.get("curve") {
                if curve["type"] == "FONT" {
                    if let Some(font) = curve["font"].as_u64() {
                        self.get("fonts", font)?;
                    }
                    if curve["body"].as_str().is_none_or(|s| {
                        s.len() > 256 || !s.bytes().all(|c| c == b'\n' || (32..=126).contains(&c))
                    }) || curve["size"]
                        .as_f64()
                        .is_none_or(|n| !n.is_finite() || !(0.0001f32 as f64..=100.).contains(&n))
                        || curve["space_line"]
                            .as_f64()
                            .is_none_or(|n| !n.is_finite() || !(0. ..=10.).contains(&n))
                        || !["LEFT", "CENTER", "RIGHT"].contains(&text(&curve["align_x"]))
                        || curve.get("extrude").is_some_and(|v| {
                            v.as_f64()
                                .is_none_or(|n| !n.is_finite() || !(0. ..=100.).contains(&n))
                        })
                    {
                        return Err("Invalid bounded text settings".into());
                    }
                }
                if !["CURVE", "FONT"].contains(&text(&curve["type"]))
                    || !["2D", "3D"].contains(&text(&curve["dimensions"]))
                    || curve["fill_mode"] != "FULL"
                    || curve["twist_mode"] != "MINIMUM"
                    || curve["bevel_mode"] != "ROUND"
                    || curve["bevel_resolution"].as_u64().is_none_or(|n| n > 8)
                    || curve["bevel_depth"]
                        .as_f64()
                        .is_none_or(|v| !v.is_finite() || !(0. ..=100.).contains(&v))
                    || curve["resolution_u"]
                        .as_u64()
                        .is_none_or(|n| !(1..=1024).contains(&n))
                    || curve.get("use_fill_caps").is_some_and(|v| !v.is_boolean())
                {
                    return Err("Invalid bounded curve settings".into());
                }
                let splines = curve["splines"]
                    .as_array()
                    .filter(|a| a.len() <= 64)
                    .ok_or("Invalid curve splines")?;
                for spline in splines {
                    if spline
                        .get("type")
                        .is_some_and(|v| v != "POLY" && v != "BEZIER")
                        || spline["use_cyclic_u"].as_bool().is_none()
                        || spline["use_smooth"].as_bool().is_none()
                        || spline["material_index"].as_u64().is_none_or(|n| n > 32767)
                    {
                        return Err("Invalid curve spline settings".into());
                    }
                    let points = spline["points"]
                        .as_array()
                        .filter(|a| !a.is_empty() && a.len() <= 4096)
                        .ok_or("Invalid curve points")?;
                    for point in points {
                        if spline["type"] == "BEZIER" {
                            for side in ["left", "right"] {
                                if point[format!("handle_{side}")].as_array().is_none_or(|a| {
                                    a.len() != 3
                                        || a.iter().any(|v| {
                                            v.as_f64()
                                                .is_none_or(|n| !n.is_finite() || n.abs() > 10000.)
                                        })
                                }) || !["FREE", "VECTOR", "AUTO", "ALIGNED"]
                                    .contains(&text(&point[format!("handle_{side}_type")]))
                                {
                                    return Err("Invalid Bezier handle".into());
                                }
                            }
                        }
                        if point["co"].as_array().is_none_or(|a| {
                            a.len() != 4
                                || a.iter().any(|v| {
                                    v.as_f64()
                                        .is_none_or(|x| !x.is_finite() || x.abs() > 10000.)
                                })
                        }) || point["radius"]
                            .as_f64()
                            .is_none_or(|x| !x.is_finite() || !(0. ..=100.).contains(&x))
                            || point["tilt"]
                                .as_f64()
                                .is_none_or(|x| !x.is_finite() || x.abs() > 100.)
                        {
                            return Err("Invalid curve point values".into());
                        }
                    }
                }
            }
            let n = m["vertices"].as_array().ok_or("Invalid vertices")?.len();
            for (field, count) in [
                ("crease_vert", n),
                (
                    "crease_edge",
                    m["edges"].as_array().ok_or("Invalid edges")?.len(),
                ),
            ] {
                if m.get(field).is_some_and(|v| {
                    v.as_array().is_none_or(|a| {
                        a.len() != count
                            || a.iter().any(|v| {
                                v.as_f64()
                                    .is_none_or(|x| !x.is_finite() || !(0. ..=1.).contains(&x))
                            })
                    })
                }) {
                    return Err("Crease attributes must match topology with values in 0..1".into());
                }
            }
            if m.get("face_strength").is_some_and(|v| {
                v.as_array().is_none_or(|a| {
                    a.len() != m["faces"].as_array().map_or(0, Vec::len)
                        || a.iter()
                            .any(|v| v.as_i64().is_none_or(|v| !(0..=2).contains(&v)))
                })
            }) {
                return Err("Face strengths must match faces with integer values in 0..2".into());
            }
            if let Some(keys) = m.get("shape_keys") {
                let keys = keys.as_array().ok_or("Shape keys must be an array")?;
                if keys.len() > 64 {
                    return Err("At most 64 shape keys".into());
                }
                let mut names = BTreeSet::new();
                for key in keys {
                    let name = key["name"]
                        .as_str()
                        .filter(|s| !s.is_empty() && s.len() <= 63)
                        .ok_or("Invalid shape-key name")?;
                    if !names.insert(name) {
                        return Err("Duplicate shape-key name".into());
                    }
                    if key["points"].as_array().is_none_or(|a| {
                        a.len() != n
                            || a.iter().any(|v| {
                                v.as_array().is_none_or(|a| {
                                    a.len() != 3
                                        || a.iter()
                                            .any(|v| v.as_f64().is_none_or(|x| !x.is_finite()))
                                })
                            })
                    }) {
                        return Err("Shape keys require one finite 3D point per vertex".into());
                    }
                }
            }
            if let Some(weights) = m.get("deform_weights") {
                let weights = weights.as_array().ok_or("Invalid deform weights")?;
                if weights
                    .iter()
                    .filter_map(Value::as_array)
                    .map(Vec::len)
                    .sum::<usize>()
                    > 1_000_000
                {
                    return Err("Deform membership limit exceeded".into());
                }
                if weights.len() != n {
                    return Err("Deform weights must match mesh vertices".into());
                }
                for row in weights {
                    let row = row.as_array().ok_or("Invalid deform weight row")?;
                    let mut seen = BTreeSet::new();
                    for pair in row {
                        if pair.as_array().is_none_or(|p| p.len() != 2)
                            || pair[0]
                                .as_u64()
                                .is_none_or(|g| g >= 1024 || !seen.insert(g))
                            || pair[1]
                                .as_f64()
                                .is_none_or(|v| !v.is_finite() || !(0. ..=1.).contains(&v))
                        {
                            return Err("Invalid deform group index/weight".into());
                        }
                    }
                }
            }
            for v in m["vertices"].as_array().unwrap() {
                if v.as_array().is_none_or(|a| {
                    a.len() != 3 || a.iter().any(|v| v.as_f64().is_none_or(|n| !n.is_finite()))
                }) {
                    return Err("Invalid mesh coordinate".into());
                }
            }
            for f in m["faces"].as_array().ok_or("Invalid faces")? {
                if f.as_array().is_none_or(|a| {
                    a.len() < 3 || a.iter().any(|v| v.as_u64().is_none_or(|i| i as usize >= n))
                }) {
                    return Err("Invalid mesh face".into());
                }
            }
        }
        for c in &self.collections {
            for v in c["objects"].as_array().ok_or("Invalid collection")? {
                self.object(v.as_u64().ok_or("Invalid object id")?)?;
            }
            for v in c["children"]
                .as_array()
                .ok_or("Invalid collection children")?
            {
                self.get("collections", v.as_u64().ok_or("Invalid collection id")?)?;
            }
        }
        if let Some(k) = self.camera {
            self.object(k)?;
        }
        for object in &self.objects {
            if object["modifiers"].as_array().is_some_and(|s| {
                s.iter().any(|m| {
                    (m["type"] == "ARRAY"
                        && (m["use_merge_vertices"] == true
                            || m["use_object_offset"] == true
                            || !m["start_cap"].is_null()
                            || !m["end_cap"].is_null()))
                        || m["type"] == "BEVEL"
                        || m["type"] == "BOOLEAN"
                        || m["type"] == "SUBSURF"
                        || m["type"] == "DISPLACE"
                })
            }) {
                modeling::evaluated_mesh(self, object, false)?;
                modeling::evaluated_mesh(self, object, true)?;
            }
        }
        Ok(())
    }
    pub fn revision(&self, source: &str, parent: Option<&str>, seed: u64) -> String {
        let mut h = Sha256::new();
        h.update(b"hb-m1-v1\0");
        h.update(seed.to_le_bytes());
        h.update(serde_json::to_vec(self).unwrap());
        h.update(b"\0");
        h.update(source);
        h.update(b"\0");
        h.update(parent.unwrap_or(""));
        format!("{:x}", h.finalize())
    }
    pub fn migrate(old: legacy::Scene) -> Result<Self, String> {
        let mut s = Self::default();
        let mut ids = std::collections::BTreeMap::new();
        for o in old.objects {
            let data = if let Some(m) = o.mesh {
                let k = s.create("meshes", &m.name, json!({}))?;
                s.mesh_from(k, json!(m.vertices), json!([]), json!(m.faces), false)?;
                if !m.uv.is_empty() {
                    s.get_mut("meshes", k)?["uv_layers"] = json!([{"name":"UVMap","data":m.uv}]);
                }
                json!({"kind":"meshes","id":k})
            } else {
                Value::Null
            };
            let k=s.create("objects",&o.name,json!({"data":data,"location":o.location,"rotation_euler":o.rotation_euler,"scale":o.scale,"selected":o.selected}))?;
            ids.insert(o.id, k);
            if o.linked {
                s.link(1, k, false, false)?;
            }
        }
        s.active = old.active.and_then(|k| ids.get(&k).copied());
        Ok(s)
    }
}
fn cube_uv() -> Vec<[f32; 2]> {
    vec![
        [0.375, 0.],
        [0.625, 0.],
        [0.625, 0.25],
        [0.375, 0.25],
        [0.375, 0.25],
        [0.625, 0.25],
        [0.625, 0.5],
        [0.375, 0.5],
        [0.375, 0.5],
        [0.625, 0.5],
        [0.625, 0.75],
        [0.375, 0.75],
        [0.375, 0.75],
        [0.625, 0.75],
        [0.625, 1.],
        [0.375, 1.],
        [0.125, 0.5],
        [0.375, 0.5],
        [0.375, 0.75],
        [0.125, 0.75],
        [0.625, 0.5],
        [0.875, 0.5],
        [0.875, 0.75],
        [0.625, 0.75],
    ]
}
#[cfg(test)]
mod tests;
