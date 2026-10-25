//! Deterministic CPU preview: clipped triangles, perspective interpolation, GGX,
//! shadow maps and depth-based ambient occlusion. No GPU or runtime assets.
use super::{
    Scene, Value,
    geometry::{Bounds, Geometry, Triangle},
    id,
    images::Texture,
    math::{M4, V3, *},
    num, text, vec3,
};
use image::{Rgba, RgbaImage};
use serde_json::json;
use std::collections::BTreeMap;
use std::f64::consts::PI;

pub fn bpy_render(scene: &Scene, write_still: bool) -> Result<Vec<String>, String> {
    let percentage = num(&scene.render["resolution_percentage"]);
    let width = (num(&scene.render["resolution_x"]) * percentage / 100.)
        .floor()
        .max(1.) as usize;
    let height = (num(&scene.render["resolution_y"]) * percentage / 100.)
        .floor()
        .max(1.) as usize;
    if width > 2048 || height > 2048 {
        return Err("Raster render dimensions must be at most 2048 pixels per axis after resolution_percentage".into());
    }
    let aspect = width as f64 / height as f64 * num(&scene.render["pixel_aspect_x"])
        / num(&scene.render["pixel_aspect_y"]);
    let camera = Camera::scene(scene, None, aspect)?;
    let renderer = Renderer::new(scene)?;
    let frame = renderer.frame(&camera, width, height, false);
    if write_still {
        let filename = text(&scene.render["filepath"]);
        let filename = if filename.to_ascii_lowercase().ends_with(".png") {
            filename.to_string()
        } else {
            format!("{filename}.png")
        };
        let mut bytes = std::io::Cursor::new(Vec::new());
        image::DynamicImage::ImageRgba8(frame)
            .write_to(&mut bytes, image::ImageFormat::Png)
            .map_err(|e| e.to_string())?;
        crate::cli::atomic_write(std::path::Path::new(&filename), bytes.get_ref())
            .map_err(|e| format!("{filename}: {e}"))?;
    }
    Ok(vec!["Rendered with hb's CPU raster preview, not Blender pixel parity; the volatile Render Result datablock is not retained. Use write_still=True for PNG output.".into()])
}
#[derive(Clone)]
pub struct Camera {
    pub view: M4,
    pub world: M4,
    pub perspective: bool,
    pub half_x: f64,
    pub half_y: f64,
    pub shift: [f64; 2],
    pub near: f64,
    pub far: f64,
}
impl Camera {
    pub fn scene(s: &Scene, name: Option<&str>, aspect: f64) -> Result<Self, String> {
        let k = match name {
            Some(n) => s
                .objects
                .iter()
                .find(|o| text(&o["name"]) == n)
                .map(id)
                .ok_or(format!("Camera {n} not found"))?,
            None => s.camera.ok_or("Scene has no active camera")?,
        };
        let o = s.object(k)?;
        if s.obj_type(o) != "CAMERA" {
            return Err("Expected camera object".into());
        }
        let d = s.get("cameras", id(&o["data"]))?;
        let world = s.world(k)?;
        let vertical = text(&d["sensor_fit"]) == "VERTICAL"
            || (text(&d["sensor_fit"]) == "AUTO" && aspect < 1.);
        let perspective = d["type"] != "ORTHO";
        let scale = if perspective {
            let sensor = if text(&d["sensor_fit"]) == "VERTICAL" {
                num(&d["sensor_height"])
            } else {
                num(&d["sensor_width"])
            };
            sensor / (2. * num(&d["lens"]))
        } else {
            num(&d["ortho_scale"]) * 0.5
        };
        let (hx, hy) = if vertical {
            (scale * aspect, scale)
        } else {
            (scale, scale / aspect)
        };
        Ok(Self {
            view: inverse(world)?,
            world,
            perspective,
            half_x: hx,
            half_y: hy,
            shift: [
                num(&d["shift_x"]) * scale * 2.,
                num(&d["shift_y"]) * scale * 2.,
            ],
            near: num(&d["clip_start"]),
            far: num(&d["clip_end"]),
        })
    }
    pub fn fit(bounds: Bounds, dir: V3, aspect: f64, perspective: bool) -> Self {
        let bounds = if bounds.min[0].is_finite() {
            bounds
        } else {
            Bounds {
                min: [-1.; 3],
                max: [1.; 3],
            }
        };
        let center = bounds.center();
        let radius = length(bounds.extent()).max(0.1) * 0.5;
        let world = look_at(
            add(center, mul(normalize(dir), radius * 3.5)),
            center,
            [0., 0., 1.],
        );
        let scale = radius * 1.12;
        if perspective {
            Self {
                view: inverse(world).unwrap(),
                world,
                perspective,
                half_x: 0.36 * aspect.min(1.),
                half_y: 0.36 / aspect.max(1.),
                shift: [0.; 2],
                near: radius * 0.01,
                far: radius * 20.,
            }
        } else {
            Self {
                view: inverse(world).unwrap(),
                world,
                perspective,
                half_x: scale * aspect.max(1.),
                half_y: scale / aspect.min(1.),
                shift: [0.; 2],
                near: radius * 0.01,
                far: radius * 20.,
            }
        }
    }
    fn planes(&self, p: V3) -> [f64; 6] {
        let z = -p[2];
        let k = if self.perspective { z } else { 1. };
        [
            z - self.near,
            self.far - z,
            p[0] - (self.shift[0] - self.half_x) * k,
            (self.shift[0] + self.half_x) * k - p[0],
            p[1] - (self.shift[1] - self.half_y) * k,
            (self.shift[1] + self.half_y) * k - p[1],
        ]
    }
    pub fn contains(&self, p: V3) -> bool {
        self.planes(point(self.view, p))
            .into_iter()
            .all(|v| v >= 0.)
    }
    pub fn intersects(&self, t: &Triangle) -> bool {
        !self.clip(t).is_empty()
    }
    fn clip(&self, t: &Triangle) -> Vec<[Vertex; 3]> {
        let mut poly: Vec<_> = (0..3)
            .map(|i| Vertex {
                camera: point(self.view, t.p[i]),
                world: t.p[i],
                normal: t.n[i],
                uv: t.uv[i],
                color: t.colors[i],
            })
            .collect();
        for plane in 0..6 {
            let mut next = vec![];
            for i in 0..poly.len() {
                let a = poly[i];
                let b = poly[(i + 1) % poly.len()];
                let da = self.planes(a.camera)[plane];
                let db = self.planes(b.camera)[plane];
                if da >= 0. {
                    next.push(a);
                }
                if (da >= 0.) != (db >= 0.) {
                    next.push(a.lerp(b, da / (da - db)));
                }
            }
            poly = next;
            if poly.len() < 3 {
                return vec![];
            }
        }
        (1..poly.len() - 1)
            .map(|i| [poly[0], poly[i], poly[i + 1]])
            .collect()
    }
    fn screen(&self, p: V3, w: usize, h: usize) -> [f64; 3] {
        let z = -p[2];
        let k = if self.perspective { z } else { 1. };
        [
            ((p[0] / k - self.shift[0]) / self.half_x * 0.5 + 0.5) * w as f64,
            (0.5 - (p[1] / k - self.shift[1]) / self.half_y * 0.5) * h as f64,
            z,
        ]
    }
    fn unproject(&self, x: usize, y: usize, depth: f64, w: usize, h: usize) -> V3 {
        let k = if self.perspective { depth } else { 1. };
        point(
            self.world,
            [
                (((x as f64 + 0.5) / w as f64 * 2. - 1.) * self.half_x + self.shift[0]) * k,
                ((1. - (y as f64 + 0.5) / h as f64 * 2.) * self.half_y + self.shift[1]) * k,
                -depth,
            ],
        )
    }
    fn ray(&self, x: usize, y: usize, w: usize, h: usize) -> (V3, V3) {
        let px = ((x as f64 + 0.5) / w as f64 * 2. - 1.) * self.half_x + self.shift[0];
        let py = (1. - (y as f64 + 0.5) / h as f64 * 2.) * self.half_y + self.shift[1];
        if self.perspective {
            (
                point(self.world, [0.; 3]),
                normalize(direction(self.world, [px, py, -1.])),
            )
        } else {
            (
                point(self.world, [px, py, 0.]),
                direction(self.world, [0., 0., -1.]),
            )
        }
    }
}
#[derive(Clone, Copy)]
struct Vertex {
    camera: V3,
    world: V3,
    normal: V3,
    uv: [f64; 2],
    color: [f64; 4],
}
impl Vertex {
    fn lerp(self, b: Self, t: f64) -> Self {
        fn mix<const N: usize>(a: [f64; N], b: [f64; N], t: f64) -> [f64; N] {
            std::array::from_fn(|i| a[i] + (b[i] - a[i]) * t)
        }
        Self {
            camera: mix(self.camera, b.camera, t),
            world: mix(self.world, b.world, t),
            normal: mix(self.normal, b.normal, t),
            uv: mix(self.uv, b.uv, t),
            color: mix(self.color, b.color, t),
        }
    }
}
pub use super::material::Material;

struct Shadow {
    camera: Camera,
    size: usize,
    depth: Vec<f64>,
}
struct Light {
    position: V3,
    direction: V3,
    color: V3,
    power: f64,
    kind: String,
    cone: f64,
    blend: f64,
    radius: f64,
    shadows: Vec<Shadow>,
    use_shadow: bool,
}
fn raster<F: FnMut(usize, [f64; 3], f64)>(
    camera: &Camera,
    v: [Vertex; 3],
    w: usize,
    h: usize,
    mut pixel: F,
) {
    let p = v.map(|v| camera.screen(v.camera, w, h));
    let edge = |a: [f64; 3], b: [f64; 3], x: f64, y: f64| {
        (b[0] - a[0]) * (y - a[1]) - (b[1] - a[1]) * (x - a[0])
    };
    let area = edge(p[0], p[1], p[2][0], p[2][1]);
    if area.abs() < 1e-12 {
        return;
    }
    let minx = p
        .iter()
        .map(|p| p[0])
        .fold(f64::INFINITY, f64::min)
        .floor()
        .max(0.) as usize;
    let maxx = p
        .iter()
        .map(|p| p[0])
        .fold(f64::NEG_INFINITY, f64::max)
        .ceil()
        .min(w as f64) as usize;
    let miny = p
        .iter()
        .map(|p| p[1])
        .fold(f64::INFINITY, f64::min)
        .floor()
        .max(0.) as usize;
    let maxy = p
        .iter()
        .map(|p| p[1])
        .fold(f64::NEG_INFINITY, f64::max)
        .ceil()
        .min(h as f64) as usize;
    for y in miny..maxy {
        for x in minx..maxx {
            let mut b = [
                edge(p[1], p[2], x as f64 + 0.5, y as f64 + 0.5) / area,
                edge(p[2], p[0], x as f64 + 0.5, y as f64 + 0.5) / area,
                edge(p[0], p[1], x as f64 + 0.5, y as f64 + 0.5) / area,
            ];
            if b.iter().any(|n| *n < -1e-10) {
                continue;
            }
            let z = if camera.perspective {
                for i in 0..3 {
                    b[i] /= p[i][2];
                }
                let sum = b.iter().sum::<f64>();
                for n in &mut b {
                    *n /= sum;
                }
                1. / sum
            } else {
                (0..3).map(|i| b[i] * p[i][2]).sum()
            };
            pixel(y * w + x, b, z);
        }
    }
}
fn interp<const N: usize>(a: [[f64; N]; 3], b: [f64; 3]) -> [f64; N] {
    std::array::from_fn(|i| (0..3).map(|j| a[j][i] * b[j]).sum())
}
fn make_shadow(
    camera: Camera,
    size: usize,
    g: &Geometry,
    materials: &BTreeMap<u64, Material>,
    textures: &BTreeMap<u64, Texture>,
) -> Shadow {
    let mut depth = vec![f64::INFINITY; size * size];
    let default = Material::default();
    for t in &g.triangles {
        let m = t
            .material
            .and_then(|k| materials.get(&k))
            .unwrap_or(&default);
        for v in camera.clip(t) {
            raster(&camera, v, size, size, |k, b, z| {
                if z < depth[k] {
                    let mut alpha = m.base[3];
                    if let Some(tx) = m.alpha_image.and_then(|k| textures.get(&k)) {
                        alpha *= tx.sample(interp(v.map(|v| v.uv), b), false)[3];
                    }
                    if m.alpha_mode == "OPAQUE" || alpha >= m.cutoff {
                        depth[k] = z;
                    }
                }
            });
        }
    }
    Shadow {
        camera,
        size,
        depth,
    }
}
fn shadow(light: &Light, p: V3, n: V3) -> f64 {
    if light.shadows.is_empty() {
        return 1.;
    }
    let offset = add(p, mul(n, light.radius.max(1.) * 0.0003));
    for s in &light.shadows {
        if !s.camera.contains(offset) {
            continue;
        }
        let q = s
            .camera
            .screen(point(s.camera.view, offset), s.size, s.size);
        let light_dir = if light.kind == "SUN" {
            mul(light.direction, -1.)
        } else {
            normalize(sub(light.position, p))
        };
        let cosine = dot(n, light_dir).abs().max(0.08);
        let texel =
            2. * s.camera.half_x / s.size as f64 * if s.camera.perspective { q[2] } else { 1. };
        let bias = texel * (1. + (1. - cosine * cosine).sqrt() / cosine);
        if s.size >= 512 {
            // Symmetric bilinear PCF in final quality; draft pixels remain stable.
            let x = q[0] - 0.5;
            let y = q[1] - 0.5;
            let fx = x - x.floor();
            let fy = y - y.floor();
            let mut visibility = 0.;
            for dy in -1..=1 {
                for dx in -1..=1 {
                    let mut sample = 0.;
                    for (ox, wx) in [(0, 1. - fx), (1, fx)] {
                        for (oy, wy) in [(0, 1. - fy), (1, fy)] {
                            let ix =
                                (x.floor() as i64 + dx + ox).clamp(0, s.size as i64 - 1) as usize;
                            let iy =
                                (y.floor() as i64 + dy + oy).clamp(0, s.size as i64 - 1) as usize;
                            if q[2] - bias <= s.depth[iy * s.size + ix] {
                                sample += wx * wy;
                            }
                        }
                    }
                    visibility += sample;
                }
            }
            return visibility / 9.;
        }
        let mut count = 0.;
        for (dx, dy) in [(-1, 0), (0, -1), (0, 0), (1, 1)] {
            let x = (q[0] as i64 + dx).clamp(0, s.size as i64 - 1) as usize;
            let y = (q[1] as i64 + dy).clamp(0, s.size as i64 - 1) as usize;
            count += if q[2] - bias <= s.depth[y * s.size + x] {
                1.
            } else {
                0.
            };
        }
        return count * 0.25;
    }
    1.
}
pub struct Renderer {
    pub geometry: Geometry,
    materials: BTreeMap<u64, Material>,
    textures: BTreeMap<u64, Texture>,
    lights: Vec<Light>,
    grid: f64,
    world_color: Option<V3>,
    environment: Option<super::world::DiffuseEnvironment>,
    high_quality: bool,
}
impl Renderer {
    pub fn new(scene: &Scene) -> Result<Self, String> {
        Self::with_quality(scene, false)
    }
    fn with_quality(scene: &Scene, high_quality: bool) -> Result<Self, String> {
        let geometry = Geometry::new(scene, true)?;
        let mut materials = BTreeMap::new();
        let mut textures = BTreeMap::new();
        for v in &scene.materials {
            materials.insert(id(v), Material::from(scene, v)?);
        }
        for v in &scene.images {
            textures.insert(id(v), Texture::new(v)?);
        }
        let radius = if geometry.bounds.min[0].is_finite() {
            length(geometry.bounds.extent()).max(1.)
        } else {
            2.
        };
        let mut lights = vec![];
        for k in scene.linked_ids() {
            let o = scene.object(k)?;
            if scene.obj_type(o) != "LIGHT" || o["hide_render"] == true {
                continue;
            }
            let d = scene.get("lights", id(&o["data"]))?;
            let world = scene.world(k)?;
            let kind = text(&d["type"]);
            let samples = if kind == "AREA" { 4 } else { 1 };
            for sample in 0..samples {
                let local = if samples == 4 {
                    let x = num(&d["size"]);
                    let shape = d["shape"].as_str().unwrap_or("SQUARE");
                    let y = if shape == "RECTANGLE" || shape == "ELLIPSE" {
                        d["size_y"].as_f64().unwrap_or(0.25)
                    } else {
                        x
                    };
                    if shape == "DISK" || shape == "ELLIPSE" {
                        let offset = std::f64::consts::FRAC_1_SQRT_2 * 0.5;
                        match sample {
                            0 => [x * offset, 0., 0.],
                            1 => [-x * offset, 0., 0.],
                            2 => [0., y * offset, 0.],
                            _ => [0., -y * offset, 0.],
                        }
                    } else {
                        [
                            if sample & 1 == 0 { -x * 0.25 } else { x * 0.25 },
                            if sample & 2 == 0 { -y * 0.25 } else { y * 0.25 },
                            0.,
                        ]
                    }
                } else {
                    [0.; 3]
                };
                lights.push(Light {
                    position: point(world, local),
                    direction: normalize(direction(world, [0., 0., -1.])),
                    color: vec3(&d["color"]),
                    power: num(&d["energy"]) / samples as f64,
                    kind: kind.into(),
                    cone: num(&d["spot_size"]) * 0.5,
                    blend: num(&d["spot_blend"]),
                    radius: num(&d["shadow_soft_size"]).max(0.01),
                    shadows: vec![],
                    use_shadow: d["use_shadow"] != false,
                });
            }
        }
        if lights.is_empty() {
            lights.push(Light {
                position: [0.; 3],
                direction: normalize([-3., 4., -5.]),
                color: [1., 0.92, 0.8],
                power: 3.,
                kind: "SUN".into(),
                cone: 0.,
                blend: 0.,
                radius,
                shadows: vec![],
                use_shadow: true,
            });
            lights.push(Light {
                position: [0.; 3],
                direction: normalize([3., -1., -2.]),
                color: [0.65, 0.8, 1.],
                power: 0.8,
                kind: "SUN".into(),
                cone: 0.,
                blend: 0.,
                radius,
                shadows: vec![],
                use_shadow: true,
            });
        }
        for light in &mut lights {
            if !light.use_shadow {
                continue;
            }
            let cameras = if light.kind == "SUN" {
                vec![Camera::fit(
                    geometry.bounds,
                    mul(light.direction, -1.),
                    1.,
                    false,
                )]
            } else {
                let dirs: Vec<_> = if light.kind == "SPOT" || light.kind == "AREA" {
                    vec![light.direction]
                } else {
                    vec![
                        [1., 0., 0.],
                        [-1., 0., 0.],
                        [0., 1., 0.],
                        [0., -1., 0.],
                        [0., 0., 1.],
                        [0., 0., -1.],
                    ]
                };
                dirs.into_iter()
                    .map(|dir| {
                        let world = look_at(
                            light.position,
                            add(light.position, dir),
                            if dir[2].abs() > 0.99 {
                                [0., 1., 0.]
                            } else {
                                [0., 0., 1.]
                            },
                        );
                        let half = if light.kind == "SPOT" {
                            light.cone.tan()
                        } else if light.kind == "AREA" {
                            10.
                        } else {
                            1.
                        };
                        Camera {
                            world,
                            view: inverse(world).unwrap(),
                            perspective: true,
                            half_x: half,
                            half_y: half,
                            shift: [0.; 2],
                            near: radius * 0.0001,
                            far: radius * 100.,
                        }
                    })
                    .collect()
            };
            for camera in cameras {
                let size = if light.kind == "SUN" { 256 } else { 128 };
                let size = if high_quality { size * 4 } else { size };
                light
                    .shadows
                    .push(make_shadow(camera, size, &geometry, &materials, &textures));
            }
        }
        let grid = 10_f64.powf((radius / 8.).log10().floor());
        Ok(Self {
            geometry,
            materials,
            textures,
            lights,
            grid,
            world_color: super::world::preview_color(scene)?,
            high_quality,
            environment: if high_quality {
                super::world::diffuse_environment(scene)?
            } else {
                None
            },
        })
    }
    #[allow(clippy::too_many_arguments)] // One fragment and its material/camera inputs.
    fn shade(
        &self,
        t: &Triangle,
        m: &Material,
        p: V3,
        mut n: V3,
        uv: [f64; 2],
        color: [f64; 4],
        eye: V3,
    ) -> ([f64; 3], f64) {
        let mut base = m.base;
        for i in 0..4 {
            base[i] *= color[i];
        }
        if let Some(tx) = m.color_image.and_then(|k| self.textures.get(&k)) {
            let tex = tx.sample(uv, true);
            for i in 0..3 {
                base[i] *= tex[i];
            }
        }
        if let Some(tx) = m.alpha_image.and_then(|k| self.textures.get(&k)) {
            base[3] *= tx.sample(uv, false)[3];
        }
        if m.alpha_mode == "OPAQUE" {
            base[3] = 1.;
        }
        if m.alpha_mode == "MASK" {
            base[3] = if base[3] >= m.cutoff { 1. } else { 0. };
        }
        let view = normalize(sub(eye, p));
        let facing = if self.high_quality {
            dot(cross(sub(t.p[1], t.p[0]), sub(t.p[2], t.p[0])), view)
        } else {
            dot(n, view)
        };
        if facing < 0. {
            n = mul(n, -1.);
        }
        if let Some(tx) = m.normal_image.and_then(|k| self.textures.get(&k)) {
            let tex = tx.sample(uv, false);
            let e1 = sub(t.p[1], t.p[0]);
            let e2 = sub(t.p[2], t.p[0]);
            let u1 = [t.uv[1][0] - t.uv[0][0], t.uv[1][1] - t.uv[0][1]];
            let u2 = [t.uv[2][0] - t.uv[0][0], t.uv[2][1] - t.uv[0][1]];
            let det = u1[0] * u2[1] - u1[1] * u2[0];
            if det.abs() > 1e-12 {
                let tangent = normalize(mul(sub(mul(e1, u2[1]), mul(e2, u1[1])), 1. / det));
                let tangent = normalize(sub(tangent, mul(n, dot(n, tangent))));
                let bitangent = mul(cross(n, tangent), det.signum());
                n = normalize(add(
                    add(
                        mul(tangent, (tex[0] * 2. - 1.) * m.normal_strength),
                        mul(bitangent, (tex[1] * 2. - 1.) * m.normal_strength),
                    ),
                    mul(n, tex[2] * 2. - 1.),
                ));
            }
        }
        let (mut rough, mut metal) = (m.roughness, m.metallic);
        if let Some(tx) = m.mr_image.and_then(|k| self.textures.get(&k)) {
            let q = tx.sample(uv, false);
            rough *= q[1];
            metal *= q[2];
        }
        rough = rough.clamp(0.045, 1.);
        metal = metal.clamp(0., 1.);
        let ambient = self
            .environment
            .as_ref()
            .map(|e| e.irradiance(n))
            .or(self.world_color);
        let mut out = std::array::from_fn(|i| {
            base[i] * ambient.map_or(0.07, |color| color[i]) * (1. - metal * 0.7) + m.emission[i]
        });
        let nv = dot(n, view).max(0.001);
        let a2 = rough.powi(4);
        let k = (rough + 1.).powi(2) / 8.;
        for light in &self.lights {
            let delta = sub(light.position, p);
            let dist = length(delta);
            let l = if light.kind == "SUN" {
                mul(light.direction, -1.)
            } else {
                normalize(delta)
            };
            let nl = dot(n, l).max(0.);
            if nl <= 0. {
                continue;
            }
            let mut radiance = if light.kind == "SUN" {
                light.power
            } else {
                light.power / (4. * PI * dist.powi(2).max(light.radius.powi(2)))
            };
            if light.kind == "SPOT" {
                let cosine = dot(mul(l, -1.), light.direction);
                let outer = light.cone.cos();
                let inner = (light.cone * (1. - light.blend)).cos();
                radiance *= ((cosine - outer) / (inner - outer).max(1e-8)).clamp(0., 1.);
            }
            if light.kind == "AREA" {
                radiance *= dot(mul(l, -1.), light.direction).max(0.) * 4.;
            }
            if radiance <= 0. {
                continue;
            }
            let visibility = shadow(light, p, n);
            let h = normalize(add(l, view));
            let nh = dot(n, h).max(0.);
            let vh = dot(view, h).max(0.);
            let d = a2 / (PI * (nh * nh * (a2 - 1.) + 1.).powi(2));
            let g = (nv / (nv * (1. - k) + k)) * (nl / (nl * (1. - k) + k));
            for i in 0..3 {
                let f0 = 0.04 * (1. - metal) + base[i] * metal;
                let f = f0 + (1. - f0) * (1. - vh).powi(5);
                let diffuse = (1. - f) * (1. - metal) * base[i] / PI;
                let spec = d * g * f / (4. * nv * nl).max(1e-6);
                out[i] += (diffuse + spec) * radiance * light.color[i] * nl * visibility;
            }
        }
        (out, base[3])
    }
    pub fn frame(&self, camera: &Camera, w: usize, h: usize, wire: bool) -> RgbaImage {
        let count = w * h;
        let mut depth = vec![f64::INFINITY; count];
        let mut colors = vec![[0.; 3]; count];
        let mut alpha = vec![0.; count];
        let mut normals = if self.high_quality {
            vec![[0.; 3]; count]
        } else {
            vec![]
        };
        let mut image = RgbaImage::new(w as u32, h as u32);
        let eye = point(camera.world, [0.; 3]);
        let default = Material::default();
        let mut order: Vec<_> = (0..self.geometry.triangles.len()).collect();
        order.sort_by(|&a, &b| {
            let ta = &self.geometry.triangles[a];
            let tb = &self.geometry.triangles[b];
            let transparent = |t: &Triangle| {
                t.material
                    .and_then(|k| self.materials.get(&k))
                    .is_some_and(|m| m.alpha_mode == "BLEND")
            };
            transparent(ta).cmp(&transparent(tb)).then_with(|| {
                if transparent(ta) {
                    let da = point(camera.view, ta.bounds.center())[2];
                    let db = point(camera.view, tb.bounds.center())[2];
                    da.total_cmp(&db)
                } else {
                    std::cmp::Ordering::Equal
                }
            })
        });
        for ti in order {
            let t = &self.geometry.triangles[ti];
            let m = t
                .material
                .and_then(|k| self.materials.get(&k))
                .unwrap_or(&default);
            for v in camera.clip(t) {
                raster(camera, v, w, h, |index, b, z| {
                    if z >= depth[index] {
                        return;
                    }
                    let p = interp(v.map(|v| v.world), b);
                    let n = normalize(interp(v.map(|v| v.normal), b));
                    let uv = interp(v.map(|v| v.uv), b);
                    let color = interp(v.map(|v| v.color), b);
                    let sample_eye = if self.high_quality && !camera.perspective {
                        add(p, direction(camera.world, [0., 0., 1.]))
                    } else {
                        eye
                    };
                    let (c, a) = self.shade(t, m, p, n, uv, color, sample_eye);
                    if a < 0.001 {
                        return;
                    }
                    if a >= 0.999 {
                        depth[index] = z;
                        colors[index] = c;
                        alpha[index] = 1.;
                        if self.high_quality {
                            let facing = dot(
                                cross(sub(t.p[1], t.p[0]), sub(t.p[2], t.p[0])),
                                sub(sample_eye, p),
                            );
                            normals[index] = if facing < 0. { mul(n, -1.) } else { n };
                        }
                    } else {
                        for i in 0..3 {
                            colors[index][i] = c[i] * a + colors[index][i] * (1. - a);
                        }
                        alpha[index] = a + alpha[index] * (1. - a);
                    }
                });
            }
        }
        for y in 0..h {
            for x in 0..w {
                let index = y * w + x;
                let mut bg = self.world_color.unwrap_or([0.028, 0.039, 0.057]);
                let (origin, dir) = camera.ray(x, y, w, h);
                if self.world_color.is_none() && dir[2].abs() > 1e-8 {
                    let d = -origin[2] / dir[2];
                    if d > 0. {
                        let p = add(origin, mul(dir, d));
                        let line = (p[0] / self.grid - (p[0] / self.grid).round())
                            .abs()
                            .min((p[1] / self.grid - (p[1] / self.grid).round()).abs());
                        let footprint = 2. * camera.half_x / w as f64
                            * if camera.perspective { d } else { 1. }
                            / self.grid
                            / dir[2].abs().max(0.2);
                        let opacity = (1. - line / footprint.max(0.001)).clamp(0., 1.)
                            * (1. - footprint * 3.).clamp(0., 1.);
                        let grid = [0.044, 0.060, 0.079];
                        for i in 0..3 {
                            bg[i] += (grid[i] - bg[i]) * opacity;
                        }
                    }
                }
                let mut ao = 1.;
                if depth[index].is_finite() && self.high_quality {
                    // Reject neighbors below the local surface tangent plane;
                    // depth-only AO incorrectly darkens smooth convex surfaces.
                    let position = camera.unproject(x, y, depth[index], w, h);
                    let radius = 2. * camera.half_x / w as f64
                        * if camera.perspective { depth[index] } else { 1. }
                        * 10.;
                    let mut blocked = 0.;
                    for (dx, dy) in [
                        (-3, -3),
                        (0, -5),
                        (3, -3),
                        (5, 0),
                        (3, 3),
                        (0, 5),
                        (-3, 3),
                        (-5, 0),
                    ] {
                        let xx = x as i64 + dx;
                        let yy = y as i64 + dy;
                        if xx < 0 || yy < 0 || xx >= w as i64 || yy >= h as i64 {
                            continue;
                        }
                        let other = depth[yy as usize * w + xx as usize];
                        if !other.is_finite() {
                            continue;
                        }
                        let delta = sub(
                            camera.unproject(xx as usize, yy as usize, other, w, h),
                            position,
                        );
                        let distance = length(delta);
                        if distance > 1e-12 && distance < radius {
                            let horizon = (dot(normals[index], delta) / distance - 0.05).max(0.);
                            blocked += horizon * (1. - distance / radius);
                        }
                    }
                    ao -= blocked * 0.1;
                } else if depth[index].is_finite() {
                    let mut blocked = 0.;
                    for (dx, dy) in [
                        (-3, -3),
                        (0, -5),
                        (3, -3),
                        (5, 0),
                        (3, 3),
                        (0, 5),
                        (-3, 3),
                        (-5, 0),
                    ] {
                        let xx = x as i64 + dx;
                        let yy = y as i64 + dy;
                        if xx >= 0 && yy >= 0 && xx < w as i64 && yy < h as i64 {
                            let other = depth[yy as usize * w + xx as usize];
                            let delta = depth[index] - other;
                            let range = depth[index] * 0.04;
                            if delta > range * 0.02 && delta < range {
                                blocked += 1. - delta / range;
                            }
                        }
                    }
                    ao -= blocked * 0.055;
                }
                let c: [u8; 4] = std::array::from_fn(|i| {
                    if i == 3 {
                        255
                    } else {
                        let linear = colors[index][i] * ao + bg[i] * (1. - alpha[index]);
                        let mapped = (linear * (2.51 * linear + 0.03)
                            / (linear * (2.43 * linear + 0.59) + 0.14))
                            .clamp(0., 1.);
                        let srgb = if mapped <= 0.0031308 {
                            mapped * 12.92
                        } else {
                            1.055 * mapped.powf(1. / 2.4) - 0.055
                        };
                        (srgb.clamp(0., 1.) * 255. + 0.5) as u8
                    }
                });
                image.put_pixel(x as u32, y as u32, Rgba(c));
            }
        }
        if wire {
            for t in &self.geometry.triangles {
                for v in camera.clip(t) {
                    let p = v.map(|v| camera.screen(v.camera, w, h));
                    for i in 0..3 {
                        let a = p[i];
                        let b = p[(i + 1) % 3];
                        let steps = (a[0] - b[0]).abs().max((a[1] - b[1]).abs()).ceil() as usize;
                        for j in 0..=steps {
                            let u = j as f64 / steps.max(1) as f64;
                            let x = (a[0] + (b[0] - a[0]) * u) as i64;
                            let y = (a[1] + (b[1] - a[1]) * u) as i64;
                            if x < 0 || y < 0 || x >= w as i64 || y >= h as i64 {
                                continue;
                            }
                            let z = if camera.perspective {
                                1. / ((1. - u) / a[2] + u / b[2])
                            } else {
                                a[2] + (b[2] - a[2]) * u
                            };
                            if z <= depth[y as usize * w + x as usize] + z * 0.001 {
                                image.put_pixel(x as u32, y as u32, Rgba([86, 208, 204, 255]));
                            }
                        }
                    }
                }
            }
        }
        image
    }
}
pub fn render(
    scene: &Scene,
    size: usize,
    views: Option<&str>,
    camera_name: Option<&str>,
    wire: bool,
) -> Result<(Vec<u8>, Value), String> {
    render_quality(scene, size, views, camera_name, wire, "draft")
}
pub fn render_quality(
    scene: &Scene,
    size: usize,
    views: Option<&str>,
    camera_name: Option<&str>,
    wire: bool,
    quality: &str,
) -> Result<(Vec<u8>, Value), String> {
    render_focused(scene, size, views, camera_name, wire, quality, None)
}
pub fn render_focused(
    scene: &Scene,
    size: usize,
    views: Option<&str>,
    camera_name: Option<&str>,
    wire: bool,
    quality: &str,
    focus: Option<&[String]>,
) -> Result<(Vec<u8>, Value), String> {
    if !["draft", "final"].contains(&quality) {
        return Err("Render quality must be draft or final".into());
    }
    let factor = if quality == "final" { 2 } else { 1 };
    if size > 2048 / factor {
        return Err("Final quality supports at most 1024 pixels per view (2048 internal); draft supports 2048".into());
    }
    if !(16..=2048).contains(&size) {
        return Err("Preview size must be 16–2048 pixels per view".into());
    }
    let start = std::time::Instant::now();
    let renderer = Renderer::with_quality(scene, quality == "final")?;
    let mut fit_bounds = renderer.geometry.bounds;
    if let Some(names) = focus {
        if names.is_empty() {
            return Err("Focus needs at least one render-visible geometry object".into());
        }
        fit_bounds = Bounds::empty();
        for name in names {
            let object = renderer
                .geometry
                .objects
                .iter()
                .find(|o| o.name == *name)
                .ok_or_else(|| format!("Focus object {name} has no render-visible geometry"))?;
            fit_bounds = fit_bounds.union(object.bounds);
        }
    }

    let views = views.unwrap_or(if camera_name.is_some() {
        "camera"
    } else {
        "front,right,back,top,camera,wire"
    });
    let names: Vec<_> = views.split(',').collect();
    if names.is_empty() || names.len() > 12 {
        return Err("Choose 1–12 named views".into());
    }
    let mut sheet = crate::preview::ContactSheet::new(size, names.len())?;
    let mut warnings = vec![];
    for (i, name) in names.iter().enumerate() {
        let direction = match *name {
            "front" => [0., -1., 0.],
            "back" => [0., 1., 0.],
            "left" => [-1., 0., 0.],
            "right" => [1., 0., 0.],
            "top" => [0., 0., 1.],
            "iso" | "wire" | "camera" => [1., -1.5, 1.],
            _ => {
                return Err(format!(
                    "Unknown view {name}; choose front, back, left, right, top, iso, camera, wire"
                ));
            }
        };
        let camera = if *name == "camera" {
            match Camera::scene(scene, camera_name, 1.) {
                Ok(c) => c,
                Err(e) => {
                    if camera_name.is_some() {
                        return Err(e);
                    }
                    warnings.push("No active camera: camera panel uses a fitted perspective view.");
                    Camera::fit(fit_bounds, direction, 1., true)
                }
            }
        } else {
            Camera::fit(fit_bounds, direction, 1., false)
        };
        let frame = renderer.frame(
            &camera,
            size * factor,
            size * factor,
            wire || *name == "wire",
        );
        let frame = if factor == 1 {
            frame
        } else {
            image::imageops::resize(
                &frame,
                size as u32,
                size as u32,
                image::imageops::FilterType::Lanczos3,
            )
        };
        sheet.panel(
            i,
            &frame,
            &format!("{:02}  {}", i + 1, name),
            &format!("GRID {} M", renderer.grid),
        )?;
    }
    let bytes = sheet.png()?;
    Ok((
        bytes,
        json!({"width":sheet.width(),"height":sheet.height(),"views":names,"quality":quality,"supersampling":factor,"directional_environment":renderer.environment.is_some(),"focus":focus,"triangles":renderer.geometry.triangles.len(),"grid_meters":renderer.grid,"warnings":warnings,"render_ms":start.elapsed().as_secs_f64()*1000.}),
    ))
}
