//! World evaluation shared by scene consumers; no rasterization policy lives here.
use super::{
    Scene, Value, images,
    math::{V3, mul},
    num, vec3,
};

/// The existing preview accepts constant illumination. Environment inputs are
/// reduced to their solid-angle weighted mean, without changing that pipeline.
pub fn preview_color(scene: &Scene) -> Result<Option<V3>, String> {
    let Some(key) = scene.scene_world else {
        return Ok(Some([0.; 3]));
    };
    let world = scene.get("worlds", key)?;
    if world["use_nodes"] == false {
        return Ok(Some(vec3(&world["color"])));
    }
    // Preserve the legacy untouched factory-world preview and old revisions.
    let Some(nodes) = world["nodes"].as_array() else {
        return Ok(None);
    };
    let links = world["links"]
        .as_array()
        .ok_or("World links must be an array")?;
    let output = nodes
        .iter()
        .position(|n| n["type"] == "ShaderNodeOutputWorld");
    let Some(link) = links
        .iter()
        .find(|l| l["target"].as_u64().map(|i| i as usize) == output && l["input"] == "Surface")
    else {
        return Ok(Some([0.; 3]));
    };
    let bi = link["source"].as_u64().ok_or("Invalid World link source")? as usize;
    let bg = nodes.get(bi).ok_or("Missing World Background node")?;
    if bg["type"] != "ShaderNodeBackground" {
        return Err(
            "World Surface requires a Background; use the documented World node chain".into(),
        );
    }
    let mut color = vec3(&bg["inputs"]["Color"]);
    if let Some(link) = links
        .iter()
        .find(|l| l["target"] == bi && l["input"] == "Color")
    {
        let env = nodes
            .get(link["source"].as_u64().ok_or("Invalid environment link")? as usize)
            .ok_or("Missing Environment Texture node")?;
        let key = env["image"]
            .as_u64()
            .ok_or("Environment Texture has no image; assign node.image before preview")?;
        color = environment_mean(scene.get("images", key)?)?;
    }
    Ok(Some(mul(color, num(&bg["inputs"]["Strength"]).max(0.))))
}

fn environment_mean(image: &Value) -> Result<V3, String> {
    let (w, h) = (
        num(&image["width"]) as usize,
        num(&image["height"]) as usize,
    );
    if w == 0 || h == 0 {
        return Err("Environment image must have positive dimensions".into());
    }
    let encoded = !image["encoded"].is_null();
    let decoded = if encoded {
        Some(images::decode(image)?)
    } else {
        None
    };
    let linear = image["colorspace"] == "Non-Color" || image["colorspace"] == "Linear Rec.709";
    let mut sum = [0.; 3];
    let mut weight = 0.;
    for y in 0..h {
        let solid_angle = (std::f64::consts::PI * (y as f64 + 0.5) / h as f64).sin();
        for x in 0..w {
            let i = if image["solid"] == true {
                0
            } else {
                (y * w + x) * 4
            };
            for (c, total) in sum.iter_mut().enumerate() {
                let value = if let Some(ref pixels) = decoded {
                    pixels.get_pixel(x as u32, (h - 1 - y) as u32)[c] as f64 / 255.
                } else {
                    num(&image["pixels"][i + c])
                };
                *total += if linear { value } else { images::srgb(value) } * solid_angle;
            }
            weight += solid_angle;
        }
    }
    Ok(sum.map(|v| v / weight))
}

#[cfg(test)]
mod tests {
    use super::*;
    use serde_json::json;
    #[test]
    fn world_color_strength_and_environment() {
        let mut scene = Scene::default();
        assert_eq!(preview_color(&scene).unwrap(), None);
        scene.worlds[0]["nodes"] = json!([
            {"type":"ShaderNodeBackground","inputs":{"Color":[0.1,0.2,0.3,1.0],"Strength":2.0}},
            {"type":"ShaderNodeOutputWorld"},
            {"type":"ShaderNodeTexEnvironment","image":3}
        ]);
        scene.worlds[0]["links"] = json!([{"source":0,"target":1,"input":"Surface"}]);
        assert_eq!(preview_color(&scene).unwrap(), Some([0.2, 0.4, 0.6]));
        scene.images.push(json!({"id":3,"width":2,"height":1,"pixels":[0.25,0.5,0.75,1.0],"solid":true,"colorspace":"Linear Rec.709"}));
        scene.worlds[0]["links"]
            .as_array_mut()
            .unwrap()
            .push(json!({"source":2,"target":0,"input":"Color"}));
        assert_eq!(preview_color(&scene).unwrap(), Some([0.5, 1.0, 1.5]));
        scene.worlds[0]["nodes"][0]["inputs"]["Strength"] = json!(-2.0);
        assert_eq!(preview_color(&scene).unwrap(), Some([0.; 3]));
        scene.worlds[0]["nodes"][2]["image"] = Value::Null;
        assert!(
            preview_color(&scene)
                .unwrap_err()
                .contains("assign node.image")
        );
    }
}

/// Low-frequency directional environment light for the optional final preview.
/// Nine real spherical harmonics approximate unoccluded diffuse irradiance / pi.
/// No specular environment reflections, ray visibility or indirect bounces.
pub struct DiffuseEnvironment {
    mean: V3,
    coefficients: [V3; 9],
}
fn basis(n: V3) -> [f64; 9] {
    let [x, y, z] = n;
    [
        0.2820947918,
        0.4886025119 * y,
        0.4886025119 * z,
        0.4886025119 * x,
        1.0925484306 * x * y,
        1.0925484306 * y * z,
        0.3153915653 * (3. * z * z - 1.),
        1.0925484306 * x * z,
        0.5462742153 * (x * x - y * y),
    ]
}
impl DiffuseEnvironment {
    pub fn irradiance(&self, normal: V3) -> V3 {
        let b = basis(normal);
        std::array::from_fn(|c| {
            (self.mean[c]
                + (1..9)
                    .map(|i| self.coefficients[i][c] * b[i] * if i < 4 { 2. / 3. } else { 0.25 })
                    .sum::<f64>())
            .max(0.)
        })
    }
    fn from_image(image: &Value, strength: f64) -> Result<Self, String> {
        let mean = environment_mean(image)?;
        let width = num(&image["width"]) as usize;
        let height = num(&image["height"]) as usize;
        let pixels = images::pixels(image)?;
        let linear = image["colorspace"] == "Non-Color" || image["colorspace"] == "Linear Rec.709";
        let mut coefficients = [[0.; 3]; 9];
        let mut weight_sum = 0.;
        // Fixed integration budget, independent of source environment resolution.
        for y in 0..32 {
            let v = (y as f64 + 0.5) / 32.;
            let latitude = std::f64::consts::PI * (v - 0.5);
            let weight = latitude.cos();
            for x in 0..64 {
                let u = (x as f64 + 0.5) / 64.;
                let longitude = std::f64::consts::TAU * (u - 0.5);
                let n = [
                    latitude.cos() * longitude.cos(),
                    latitude.cos() * longitude.sin(),
                    latitude.sin(),
                ];
                let index = (((v * height as f64) as usize).min(height - 1) * width
                    + ((u * width as f64) as usize).min(width - 1))
                    * 4;
                let color: V3 = std::array::from_fn(|c| {
                    let value = pixels[index + c] as f64;
                    if linear { value } else { images::srgb(value) }
                });
                let b = basis(n);
                for i in 1..9 {
                    for c in 0..3 {
                        coefficients[i][c] += (color[c] - mean[c]) * b[i] * weight;
                    }
                }
                weight_sum += weight;
            }
        }
        for row in &mut coefficients {
            for c in row {
                *c *= 4. * std::f64::consts::PI / weight_sum * strength;
            }
        }
        Ok(Self {
            mean: mul(mean, strength),
            coefficients,
        })
    }
}
pub fn diffuse_environment(scene: &Scene) -> Result<Option<DiffuseEnvironment>, String> {
    let Some(key) = scene.scene_world else {
        return Ok(None);
    };
    let world = scene.get("worlds", key)?;
    if world["use_nodes"] == false {
        return Ok(None);
    }
    let (Some(nodes), Some(links)) = (world["nodes"].as_array(), world["links"].as_array()) else {
        return Ok(None);
    };
    let Some(output) = nodes
        .iter()
        .position(|n| n["type"] == "ShaderNodeOutputWorld")
    else {
        return Ok(None);
    };
    let Some(bg_link) = links
        .iter()
        .find(|l| l["target"] == output && l["input"] == "Surface")
    else {
        return Ok(None);
    };
    let Some(bg_index) = bg_link["source"].as_u64() else {
        return Ok(None);
    };
    let Some(bg) = nodes.get(bg_index as usize) else {
        return Ok(None);
    };
    let Some(env_link) = links
        .iter()
        .find(|l| l["target"] == bg_index && l["input"] == "Color")
    else {
        return Ok(None);
    };
    let env = nodes
        .get(
            env_link["source"]
                .as_u64()
                .ok_or("Missing environment source")? as usize,
        )
        .ok_or("Missing environment node")?;
    let image = scene.get(
        "images",
        env["image"]
            .as_u64()
            .ok_or("Environment Texture has no image")?,
    )?;
    DiffuseEnvironment::from_image(image, num(&bg["inputs"]["Strength"]).max(0.)).map(Some)
}

#[cfg(test)]
mod environment_tests {
    use super::*;
    use serde_json::json;
    #[test]
    fn constant_environment_remains_constant_and_preserves_hdr() {
        let image = json!({"width":2,"height":1,"pixels":[4.,0.5,0.25,1.],"solid":true,"colorspace":"Linear Rec.709"});
        let environment = DiffuseEnvironment::from_image(&image, 2.).unwrap();
        for n in [[1., 0., 0.], [0., 1., 0.], [0., 0., 1.], [-1., 0., 0.]] {
            let value = environment.irradiance(n);
            for (a, b) in value.into_iter().zip([8., 1., 0.5]) {
                assert!((a - b).abs() < 1e-8);
            }
        }
    }
    #[test]
    fn bright_north_illuminates_upward_normals_more() {
        let image = json!({"width":4,"height":2,"pixels":[0.,0.,0.,1.,0.,0.,0.,1.,0.,0.,0.,1.,0.,0.,0.,1.,1.,0.,0.,1.,1.,0.,0.,1.,1.,0.,0.,1.,1.,0.,0.,1.],"solid":false,"colorspace":"Linear Rec.709"});
        let environment = DiffuseEnvironment::from_image(&image, 1.).unwrap();
        assert!(environment.irradiance([0., 0., 1.])[0] > 0.9);
        assert!(environment.irradiance([0., 0., -1.])[0] < 0.1);
        assert!((environment.irradiance([1., 0., 0.])[0] - 0.5).abs() < 0.02);
    }
}
