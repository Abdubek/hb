//! Deterministic procedural displacement; texture evaluation uses float32 arithmetic.
use super::{Scene, Value, num, text, vec3};
use serde_json::json;

pub fn validate_texture(t: &Value) -> Result<(), String> {
    if t["type"] != "CLOUDS"
        || t["cloud_type"] != "GRAYSCALE"
        || !["BLENDER_ORIGINAL", "CELL_NOISE"].contains(&text(&t["noise_basis"]))
        || !["SOFT_NOISE", "HARD_NOISE"].contains(&text(&t["noise_type"]))
    {
        return Err("Procedural textures support grayscale CLOUDS with CELL_NOISE; the default BLENDER_ORIGINAL basis is readable but cannot be evaluated".into());
    }
    for (key, min, max) in [
        ("noise_scale", 0.0001_f32 as f64, f32::MAX as f64),
        ("intensity", 0., 2.),
        ("contrast", 0., 5.),
    ] {
        if t[key]
            .as_f64()
            .is_none_or(|v| !v.is_finite() || v < min || v > max)
        {
            return Err(format!("Texture {key} must be finite in {min}..{max}"));
        }
    }
    if t["noise_depth"].as_u64().is_none_or(|v| v > 30) {
        return Err("Texture noise_depth must be in 0..30".into());
    }
    Ok(())
}
fn cell_noise(position: [f32; 3]) -> Result<f32, String> {
    let mut cell = [0u32; 3];
    for (i, v) in position.into_iter().enumerate() {
        // Blender's cell boundaries have a small positive offset and dilation.
        let c = ((v + 0.000001) * 1.00001).floor();
        if !c.is_finite() || c.abs() > 2_147_480_000. {
            return Err("CELL_NOISE lattice coordinate exceeds the signed 32-bit range; reduce noise_depth, increase noise_scale or move geometry nearer its origin".into());
        }
        cell[i] = (c as i32) as u32;
    }
    // Integer polynomial hash. Wrapping is intentional for negative cells too.
    let mut n = cell[0]
        .wrapping_add(cell[1].wrapping_mul(1301))
        .wrapping_add(cell[2].wrapping_mul(314159));
    n ^= n.wrapping_shl(13);
    let h = n
        .wrapping_mul(n.wrapping_mul(n).wrapping_mul(15731).wrapping_add(789221))
        .wrapping_add(1376312589);
    Ok(h as f32 / 4294967296.)
}
struct CellTexture {
    scale: f32,
    depth: u64,
    hard: bool,
    intensity: f32,
    contrast: f32,
}
impl CellTexture {
    fn new(t: &Value) -> Result<Self, String> {
        validate_texture(t)?;
        if t["noise_basis"] != "CELL_NOISE" {
            return Err("CLOUDS evaluation requires noise_basis='CELL_NOISE'; BLENDER_ORIGINAL is not implemented".into());
        }
        Ok(Self {
            scale: 1. / num(&t["noise_scale"]) as f32,
            depth: t["noise_depth"].as_u64().unwrap(),
            hard: t["noise_type"] == "HARD_NOISE",
            intensity: num(&t["intensity"]) as f32,
            contrast: num(&t["contrast"]) as f32,
        })
    }
    fn evaluate(&self, position: [f32; 3]) -> Result<f32, String> {
        let mut position = position.map(|v| v * self.scale);
        let mut amplitude = 1.;
        let mut total = 0.;
        let mut weight = 0.;
        for _ in 0..=self.depth {
            let mut value = cell_noise(position)?;
            if self.hard {
                value = (2. * value - 1.).abs();
            }
            total += amplitude * value;
            weight += amplitude;
            amplitude *= 0.5;
            position = position.map(|v| v * 2.);
        }
        let value = total * (1. / weight);
        Ok((value - 0.5) * self.contrast + self.intensity - 0.5)
    }
}
pub fn texture(t: &Value, position: [f32; 3]) -> Result<f32, String> {
    CellTexture::new(t)?.evaluate(position)
}

fn normal(v: [f32; 3]) -> [f32; 3] {
    let length = v.iter().map(|x| x * x).sum::<f32>().sqrt();
    if length > 0. {
        v.map(|x| x / length)
    } else {
        [0.; 3]
    }
}
fn normals(mesh: &Value, vertices: &[[f32; 3]]) -> Vec<[f32; 3]> {
    let mut result = vec![[0.; 3]; vertices.len()];
    for face in mesh["faces"].as_array().unwrap() {
        let face: Vec<usize> = face
            .as_array()
            .unwrap()
            .iter()
            .map(|v| v.as_u64().unwrap() as usize)
            .collect();
        let mut n = [0.; 3];
        for i in 0..face.len() {
            let a = vertices[face[i]];
            let b = vertices[face[(i + 1) % face.len()]];
            for k in 0..3 {
                n[k] += (a[(k + 1) % 3] - b[(k + 1) % 3]) * (a[(k + 2) % 3] + b[(k + 2) % 3]);
            }
        }
        let n = normal(n);
        for i in 0..face.len() {
            let point = vertices[face[i]];
            let a = normal(std::array::from_fn(|k| {
                vertices[face[(i + face.len() - 1) % face.len()]][k] - point[k]
            }));
            let b = normal(std::array::from_fn(|k| {
                vertices[face[(i + 1) % face.len()]][k] - point[k]
            }));
            let angle = a
                .iter()
                .zip(b)
                .map(|(x, y)| x * y)
                .sum::<f32>()
                .clamp(-1., 1.)
                .acos();
            for k in 0..3 {
                result[face[i]][k] += angle * n[k];
            }
        }
    }
    for (v, point) in result.iter_mut().zip(vertices) {
        *v = normal(*v);
        if *v == [0.; 3] {
            *v = normal(*point);
        }
    }
    result
}
pub fn apply(
    scene: &Scene,
    object: &Value,
    mesh: &Value,
    modifier: &Value,
) -> Result<Value, String> {
    let strength = num(&modifier["strength"]) as f32;
    if strength == 0. {
        return Ok(mesh.clone());
    }
    let custom = mesh["loop_normals"].as_array().unwrap();
    if !custom.is_empty() && mesh["smooth"].as_array().unwrap().iter().any(|v| v == true) {
        return Err("DISPLACE custom-normal remapping currently requires flat input faces".into());
    }
    let vertices: Vec<[f32; 3]> = mesh["vertices"]
        .as_array()
        .unwrap()
        .iter()
        .map(|v| vec3(v).map(|x| x as f32))
        .collect();
    let directions = if modifier["direction"] == "NORMAL" {
        normals(mesh, &vertices)
    } else {
        let axis = match text(&modifier["direction"]) {
            "X" => 0,
            "Y" => 1,
            _ => 2,
        };
        let mut v = [0.; 3];
        v[axis] = 1.;
        vec![v; vertices.len()]
    };
    let tex = modifier["texture"]
        .as_u64()
        .map(|key| CellTexture::new(scene.get("textures", key)?))
        .transpose()?;
    if tex
        .as_ref()
        .is_some_and(|t| vertices.len() as u64 * (t.depth + 1) > 10_000_000)
    {
        return Err("DISPLACE exceeds ten million vertex-octave evaluations; reduce topology or noise_depth".into());
    }
    let group = object["vertex_groups"]
        .as_array()
        .and_then(|g| g.iter().position(|g| g["name"] == modifier["vertex_group"]));
    let weights = super::groups::weights(mesh);
    let mut output = Vec::with_capacity(vertices.len());
    for (index, (position, direction)) in vertices.iter().copied().zip(directions).enumerate() {
        let intensity = if let Some(t) = &tex {
            t.evaluate(position)?
        } else {
            1.
        };
        let factor = group.map_or(1., |group| {
            let weight = weights[index]
                .iter()
                .find(|(g, _)| *g == group)
                .map(|(_, w)| *w)
                .unwrap_or(0.);
            if modifier["invert_vertex_group"] == true {
                1. - weight
            } else {
                weight
            }
        });
        let offset = strength * (intensity - num(&modifier["mid_level"]) as f32) * factor;
        let point: [f32; 3] = std::array::from_fn(|i| position[i] + offset * direction[i]);
        if point.iter().any(|v| !v.is_finite()) {
            return Err("DISPLACE produced nonfinite coordinates; reduce strength".into());
        }
        output.push(point);
    }
    let mut out = mesh.clone();
    if !custom.is_empty() {
        let mut normals = vec![];
        let mut start = 0;
        for face in super::topology::faces(mesh) {
            let original: Vec<_> = face.iter().map(|&v| vertices[v]).collect();
            let points: Vec<_> = face.iter().map(|&v| output[v]).collect();
            for corner in 0..face.len() {
                normals.push(super::weighted_normals::remap_corner(
                    &original,
                    &points,
                    corner,
                    vec3(&custom[start + corner]).map(|x| x as f32),
                ));
            }
            start += face.len();
        }
        out["loop_normals"] = json!(normals);
    }
    out["vertices"] = json!(output);
    Ok(out)
}
