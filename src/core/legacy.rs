use serde::{Deserialize, Serialize};
use serde_json::{Value, json};
use sha2::{Digest, Sha256};
use std::collections::{BTreeMap, BTreeSet};

#[derive(Clone, Default, Serialize, Deserialize)]
#[serde(deny_unknown_fields)]
pub struct Scene {
    pub objects: Vec<Object>,
    pub active: Option<u64>,
    pub next_id: u64,
}
#[derive(Clone, Serialize, Deserialize)]
#[serde(deny_unknown_fields)]
pub struct Object {
    pub id: u64,
    pub name: String,
    pub location: [f32; 3],
    pub rotation_euler: [f32; 3],
    pub scale: [f32; 3],
    pub selected: bool,
    pub linked: bool,
    pub mesh: Option<Mesh>,
}
#[derive(Clone, Serialize, Deserialize)]
#[serde(deny_unknown_fields)]
pub struct Mesh {
    pub name: String,
    pub vertices: Vec<[f32; 3]>,
    pub faces: Vec<Vec<u32>>,
    pub uv: Vec<[f32; 2]>,
}
fn unique(name: &str, existing: BTreeSet<String>) -> String {
    let name = if name.is_empty() { "Object" } else { name };
    let mut name = name.to_string();
    while name.len() > 63 {
        name.pop();
    }
    if !existing.contains(&name) {
        return name;
    }
    let base = name
        .rsplit_once('.')
        .filter(|(_, s)| s.len() >= 3 && s.chars().all(|c| c.is_ascii_digit()))
        .map(|(a, _)| a)
        .unwrap_or(&name);
    for n in 1.. {
        let suffix = format!(".{n:03}");
        let mut base = base.to_string();
        while base.len() + suffix.len() > 63 {
            base.pop();
        }
        let candidate = format!("{base}{suffix}");
        if !existing.contains(&candidate) {
            return candidate;
        }
    }
    unreachable!()
}
fn vector(v: &Value) -> Result<[f32; 3], String> {
    let a = v.as_array().ok_or("Expected three numbers")?;
    if a.len() != 3 {
        return Err("Expected three numbers".into());
    }
    let mut out = [0.; 3];
    for i in 0..3 {
        out[i] = a[i].as_f64().ok_or("Expected a number")? as f32;
        if !out[i].is_finite() {
            return Err("Transform must be finite".into());
        }
    }
    Ok(out)
}
impl Scene {
    pub fn object(&self, id: u64) -> Result<&Object, String> {
        self.objects
            .iter()
            .find(|o| o.id == id)
            .ok_or("Object no longer exists".into())
    }
    pub fn request(&mut self, r: Value) -> Result<Value, String> {
        let op = r["op"].as_str().ok_or("Missing op")?;
        match op {
            "snapshot" => Ok(serde_json::to_value(&self).unwrap()),
            "list" => {
                let mut os: Vec<_> = self
                    .objects
                    .iter()
                    .filter(|o| !r["linked"].as_bool().unwrap_or(false) || o.linked)
                    .collect();
                if !r["linked"].as_bool().unwrap_or(false) {
                    os.sort_by(|a, b| {
                        a.name
                            .to_ascii_lowercase()
                            .cmp(&b.name.to_ascii_lowercase())
                    });
                }
                Ok(json!(os.iter().map(|o| o.id).collect::<Vec<_>>()))
            }
            "active" => Ok(json!(self.active)),
            "set_active" => {
                let id = r["id"].as_u64();
                if let Some(id) = id
                    && !self.object(id)?.linked
                {
                    return Err("Active object must belong to the view layer".into());
                }
                self.active = id;
                Ok(Value::Null)
            }
            "get" => {
                let o = self.object(r["id"].as_u64().ok_or("Missing id")?)?;
                Ok(
                    json!({"id":o.id,"name":o.name,"type":if o.mesh.is_some(){"MESH"}else{"EMPTY"},"location":o.location,"rotation_euler":o.rotation_euler,"scale":o.scale,"selected":o.selected,"linked":o.linked}),
                )
            }
            "new" | "cube" => {
                let name =
                    r["name"]
                        .as_str()
                        .unwrap_or(if op == "cube" { "Cube" } else { "Object" });
                let name = unique(name, self.objects.iter().map(|o| o.name.clone()).collect());
                let mut mesh = None;
                let mut location = [0.; 3];
                let mut rotation_euler = [0.; 3];
                let mut scale = [1.; 3];
                if op == "cube" {
                    location = vector(&r["location"])?;
                    rotation_euler = vector(&r["rotation"])?;
                    scale = vector(&r["scale"])?;
                    let size = r["size"].as_f64().ok_or("Invalid cube size")? as f32;
                    if !size.is_finite() {
                        return Err("Cube size must be finite".into());
                    }
                    let s = size.clamp(0., 1e12) / 2.;
                    let mesh_name = unique(
                        "Cube",
                        self.objects
                            .iter()
                            .filter_map(|o| o.mesh.as_ref().map(|m| m.name.clone()))
                            .collect(),
                    );
                    // Blender's cube vertex/loop order, checked against the reference fixture.
                    let mut vertices = vec![
                        [-s, -s, -s],
                        [-s, -s, s],
                        [-s, s, -s],
                        [-s, s, s],
                        [s, -s, -s],
                        [s, -s, s],
                        [s, s, -s],
                        [s, s, s],
                    ];
                    for v in &mut vertices {
                        for i in 0..3 {
                            v[i] *= scale[i];
                        }
                    }
                    scale = [1.; 3];
                    let faces = vec![
                        vec![0, 1, 3, 2],
                        vec![2, 3, 7, 6],
                        vec![6, 7, 5, 4],
                        vec![4, 5, 1, 0],
                        vec![2, 6, 4, 0],
                        vec![7, 3, 1, 5],
                    ];
                    let uv = if r["calc_uvs"].as_bool().unwrap_or(true) {
                        cube_uv()
                    } else {
                        vec![]
                    };
                    mesh = Some(Mesh {
                        name: mesh_name,
                        vertices,
                        faces,
                        uv,
                    });
                    for obj in &mut self.objects {
                        obj.selected = false;
                    }
                }
                let id = self.next_id;
                self.next_id += 1;
                self.objects.push(Object {
                    id,
                    name,
                    mesh,
                    location,
                    rotation_euler,
                    scale,
                    selected: op == "cube",
                    linked: op == "cube",
                });
                if op == "cube" {
                    self.active = Some(id);
                }
                Ok(json!(id))
            }
            "set" => {
                let id = r["id"].as_u64().ok_or("Missing id")?;
                self.object(id)?;
                let field = r["field"].as_str().ok_or("Missing field")?;
                let name = if field == "name" {
                    Some(unique(
                        r["value"].as_str().ok_or("Name must be str")?,
                        self.objects
                            .iter()
                            .filter(|o| o.id != id)
                            .map(|o| o.name.clone())
                            .collect(),
                    ))
                } else {
                    None
                };
                let o = self.objects.iter_mut().find(|o| o.id == id).unwrap();
                match field {
                    "name" => o.name = name.unwrap(),
                    "location" => o.location = vector(&r["value"])?,
                    "rotation_euler" => o.rotation_euler = vector(&r["value"])?,
                    "scale" => o.scale = vector(&r["value"])?,
                    "selected" => {
                        o.selected = r["value"].as_bool().ok_or("Selection must be bool")?
                    }
                    "linked" => {
                        if o.linked {
                            return Err("Object already in collection".into());
                        }
                        o.linked = true;
                    }
                    _ => return Err(format!("Unsupported object field: {field}")),
                }
                Ok(Value::Null)
            }
            _ => Err(format!("Unknown core operation: {op}")),
        }
    }
    pub fn validate(&self) -> Result<(), String> {
        let mut ids = BTreeSet::new();
        let mut names = BTreeSet::new();
        for o in &self.objects {
            if !ids.insert(o.id) || !names.insert(&o.name) || o.id >= self.next_id {
                return Err("Invalid scene identifiers".into());
            }
            if o.location
                .iter()
                .chain(&o.scale)
                .chain(&o.rotation_euler)
                .any(|n| !n.is_finite())
            {
                return Err("Non-finite transform".into());
            }
            if let Some(m) = &o.mesh {
                if m.vertices.is_empty()
                    || m.faces.is_empty()
                    || m.vertices
                        .iter()
                        .flatten()
                        .chain(m.uv.iter().flatten())
                        .any(|v| !v.is_finite())
                {
                    return Err("Mesh must contain finite geometry".into());
                }
                if !m.uv.is_empty() && m.uv.len() != m.faces.iter().map(Vec::len).sum::<usize>() {
                    return Err("UV loop count does not match mesh".into());
                }
                for f in &m.faces {
                    if f.len() < 3 || f.iter().any(|i| *i as usize >= m.vertices.len()) {
                        return Err("Invalid mesh face".into());
                    }
                }
            }
        }
        if let Some(id) = self.active {
            self.object(id)?;
        }
        Ok(())
    }
    pub fn revision(&self, script: &str, parent: Option<&str>, seed: u64) -> String {
        let mut h = Sha256::new();
        h.update(b"hb-m0-v1\0");
        h.update(seed.to_le_bytes());
        h.update(serde_json::to_vec(self).unwrap());
        h.update(b"\0");
        h.update(script);
        h.update(b"\0");
        h.update(parent.unwrap_or(""));
        format!("{:x}", h.finalize())
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

pub fn glb(scene: &Scene) -> Result<Vec<u8>, String> {
    scene.validate()?;
    let mut bin = Vec::new();
    let mut views = Vec::new();
    let mut accessors = Vec::new();
    let mut meshes = Vec::new();
    let mut nodes = Vec::new();
    let mut objects: Vec<_> = scene.objects.iter().filter(|o| o.linked).collect();
    objects.sort_by(|a, b| a.name.cmp(&b.name));
    for o in objects {
        let [x, y, z] = o.rotation_euler.map(|n| n as f64 / 2.);
        let (sx, cx) = x.sin_cos();
        let (sy, cy) = y.sin_cos();
        let (sz, cz) = z.sin_cos();
        let mut node = json!({"name":o.name,"translation":[o.location[0],o.location[2],-o.location[1]],"scale":[o.scale[0],o.scale[2],o.scale[1]],"rotation":[sx*cy*cz-cx*sy*sz,cx*cy*sz-sx*sy*cz,-(cx*sy*cz+sx*cy*sz),cx*cy*cz+sx*sy*sz]});
        if let Some(m) = &o.mesh {
            let mut positions = Vec::<[f32; 3]>::new();
            let mut normals = Vec::<[f32; 3]>::new();
            let mut uvs = Vec::<[f32; 2]>::new();
            let mut indices = Vec::<u32>::new();
            let mut loop_id = 0;
            let mut vertex_map = BTreeMap::new();
            for f in &m.faces {
                let a = m.vertices[f[0] as usize];
                let b = m.vertices[f[1] as usize];
                let c = m.vertices[f[2] as usize];
                let u = [b[0] - a[0], b[1] - a[1], b[2] - a[2]];
                let v = [c[0] - a[0], c[1] - a[1], c[2] - a[2]];
                let mut n = [
                    u[1] * v[2] - u[2] * v[1],
                    u[2] * v[0] - u[0] * v[2],
                    u[0] * v[1] - u[1] * v[0],
                ];
                let length = n.iter().map(|x| x * x).sum::<f32>().sqrt();
                if length > 0. {
                    n = n.map(|x| x / length);
                }
                let mut polygon = Vec::new();
                for i in f {
                    let v = m.vertices[*i as usize];
                    let normal = [n[0], n[2], -n[1]].map(|x| if x == 0. { 0. } else { x });
                    let uv = m.uv.get(loop_id).map(|uv| [uv[0], 1. - uv[1]]);
                    let key = (
                        *i,
                        normal.map(f32::to_bits),
                        uv.map(|v| v.map(f32::to_bits)),
                    );
                    let index = *vertex_map.entry(key).or_insert_with(|| {
                        let index = positions.len() as u32;
                        positions.push([v[0], v[2], -v[1]]);
                        normals.push(normal);
                        if let Some(uv) = uv {
                            uvs.push(uv);
                        }
                        index
                    });
                    polygon.push(index);
                    loop_id += 1;
                }
                for i in 1..polygon.len() - 1 {
                    indices.extend_from_slice(&[polygon[0], polygon[i], polygon[i + 1]]);
                }
            }
            let p = accessors.len();
            let offset = bin.len();
            for v in &positions {
                for n in v {
                    bin.extend(n.to_le_bytes());
                }
            }
            views.push(json!({"buffer":0,"byteOffset":offset,"byteLength":bin.len()-offset,"target":34962}));
            let min: [f32; 3] = std::array::from_fn(|i| {
                positions.iter().map(|v| v[i]).fold(f32::INFINITY, f32::min)
            });
            let max: [f32; 3] = std::array::from_fn(|i| {
                positions
                    .iter()
                    .map(|v| v[i])
                    .fold(f32::NEG_INFINITY, f32::max)
            });
            accessors.push(json!({"bufferView":views.len()-1,"componentType":5126,"count":positions.len(),"type":"VEC3","min":min,"max":max}));
            let normal = accessors.len();
            let offset = bin.len();
            for v in &normals {
                for n in v {
                    bin.extend(n.to_le_bytes());
                }
            }
            views.push(json!({"buffer":0,"byteOffset":offset,"byteLength":bin.len()-offset,"target":34962}));
            accessors.push(json!({"bufferView":views.len()-1,"componentType":5126,"count":normals.len(),"type":"VEC3"}));
            let mut attributes = json!({"POSITION":p,"NORMAL":normal});
            if !uvs.is_empty() {
                let tex = accessors.len();
                let offset = bin.len();
                for v in &uvs {
                    for n in v {
                        bin.extend(n.to_le_bytes());
                    }
                }
                views.push(json!({"buffer":0,"byteOffset":offset,"byteLength":bin.len()-offset,"target":34962}));
                accessors.push(json!({"bufferView":views.len()-1,"componentType":5126,"count":uvs.len(),"type":"VEC2"}));
                attributes["TEXCOORD_0"] = json!(tex);
            }
            let idx = accessors.len();
            let offset = bin.len();
            for n in &indices {
                bin.extend(n.to_le_bytes());
            }
            views.push(json!({"buffer":0,"byteOffset":offset,"byteLength":bin.len()-offset,"target":34963}));
            accessors.push(json!({"bufferView":views.len()-1,"componentType":5125,"count":indices.len(),"type":"SCALAR"}));
            node["mesh"] = json!(meshes.len());
            meshes.push(json!({"name":m.name,"primitives":[{"attributes":attributes,"indices":idx,"mode":4}]}));
        }
        nodes.push(node);
    }
    let mut doc = json!({"asset":{"version":"2.0","generator":"hb M0"},"scene":0,"scenes":[{"nodes":(0..nodes.len()).collect::<Vec<_>>() }],"nodes":nodes});
    if !meshes.is_empty() {
        doc["meshes"] = json!(meshes);
        doc["buffers"] = json!([{"byteLength":bin.len()}]);
        doc["bufferViews"] = json!(views);
        doc["accessors"] = json!(accessors);
    }
    let mut js = serde_json::to_vec(&doc).unwrap();
    while !js.len().is_multiple_of(4) {
        js.push(b' ');
    }
    while !bin.len().is_multiple_of(4) {
        bin.push(0);
    }
    let total = 12 + 8 + js.len() + if bin.is_empty() { 0 } else { 8 + bin.len() };
    let mut out = b"glTF".to_vec();
    out.extend(2u32.to_le_bytes());
    out.extend((total as u32).to_le_bytes());
    out.extend((js.len() as u32).to_le_bytes());
    out.extend(0x4e4f534au32.to_le_bytes());
    out.extend(js);
    if !bin.is_empty() {
        out.extend((bin.len() as u32).to_le_bytes());
        out.extend(0x004e4942u32.to_le_bytes());
        out.extend(bin);
    }
    Ok(out)
}
#[cfg(test)]
mod tests {
    use super::*;
    #[test]
    fn names() {
        assert_eq!(
            unique("Cube", ["Cube".into(), "Cube.001".into()].into()),
            "Cube.002"
        );
    }
    #[test]
    fn cube_export() {
        let mut s = Scene::default();
        s.request(
            json!({"op":"cube","location":[0,0,0],"rotation":[0,0,0],"scale":[1,1,1],"size":2}),
        )
        .unwrap();
        let a = glb(&s).unwrap();
        assert_eq!(&a[..4], b"glTF");
        assert_eq!(
            u32::from_le_bytes(a[8..12].try_into().unwrap()) as usize,
            a.len()
        );
        assert_eq!(a, glb(&s).unwrap());
    }
}
