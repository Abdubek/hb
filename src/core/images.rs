use super::{Value, num, text};
use base64::{Engine, engine::general_purpose::STANDARD};
use image::{ImageFormat, Rgba, RgbaImage};
use serde_json::json;
pub fn encoded(bytes: &[u8]) -> Result<Value, String> {
    let im = image::load_from_memory(bytes).map_err(|e| format!("PNG/JPEG image: {e}"))?;
    if im.width() as u64 * im.height() as u64 > 16777216 {
        return Err("Image exceeds 16 megapixels".into());
    }
    Ok(
        json!({"width":im.width(),"height":im.height(),"encoded":STANDARD.encode(bytes),"pixels":[],"solid":false}),
    )
}
pub fn decode(v: &Value) -> Result<RgbaImage, String> {
    decode_output(v, false)
}
fn decode_output(v: &Value, encode_linear: bool) -> Result<RgbaImage, String> {
    if let Some(s) = v["encoded"].as_str() {
        return Ok(
            image::load_from_memory(&STANDARD.decode(s).map_err(|e| e.to_string())?)
                .map_err(|e| e.to_string())?
                .to_rgba8(),
        );
    }
    let (w, h) = (num(&v["width"]) as u32, num(&v["height"]) as u32);
    if w == 0 || h == 0 || w as u64 * h as u64 > 16777216 {
        return Err("Invalid image dimensions".into());
    }
    let p = v["pixels"].as_array().ok_or("Missing image pixels")?;
    let solid = v["solid"] == true;
    let mut out = RgbaImage::new(w, h);
    for y in 0..h {
        for x in 0..w {
            let k = if solid {
                0
            } else {
                ((h - 1 - y) * w + x) as usize * 4
            };
            if k + 4 > p.len() {
                return Err("Incomplete image pixels".into());
            }
            out.put_pixel(
                x,
                y,
                Rgba(std::array::from_fn(|i| {
                    let mut value = num(&p[k + i]).clamp(0., 1.);
                    if encode_linear && i < 3 {
                        value = if value <= 0.0031308 {
                            value * 12.92
                        } else {
                            1.055 * value.powf(1. / 2.4) - 0.055
                        };
                    }
                    (value * 255.).round() as u8
                })),
            );
        }
    }
    Ok(out)
}
pub fn pixels(v: &Value) -> Result<Vec<f32>, String> {
    if v["encoded"].is_null() {
        let p = v["pixels"].as_array().ok_or("Missing pixels")?;
        let p: Vec<_> = p.iter().map(|v| num(v) as f32).collect();
        if v["solid"] == true {
            return Ok(p.repeat((num(&v["width"]) * num(&v["height"])) as usize));
        }
        return Ok(p);
    }
    let im = decode(v)?;
    let mut out = Vec::with_capacity(im.width() as usize * im.height() as usize * 4);
    for y in (0..im.height()).rev() {
        for x in 0..im.width() {
            out.extend(im.get_pixel(x, y).0.map(|x| x as f32 / 255.));
        }
    }
    Ok(out)
}
pub fn png(v: &Value, color: bool) -> Result<Vec<u8>, String> {
    let mut data = std::io::Cursor::new(vec![]);
    decode_output(v, color && text(&v["colorspace"]) == "Linear Rec.709")?
        .write_to(&mut data, ImageFormat::Png)
        .map_err(|e| e.to_string())?;
    Ok(data.into_inner())
}
pub fn srgb(x: f64) -> f64 {
    if x <= 0.04045 {
        x / 12.92
    } else {
        ((x + 0.055) / 1.055).powf(2.4)
    }
}
pub struct Texture {
    pub image: RgbaImage,
    pub linear: bool,
}
impl Texture {
    pub fn new(v: &Value) -> Result<Self, String> {
        Ok(Self {
            image: decode(v)?,
            linear: matches!(text(&v["colorspace"]), "Non-Color" | "Linear Rec.709"),
        })
    }
    pub fn sample(&self, uv: [f64; 2], color: bool) -> [f64; 4] {
        let w = self.image.width() as i64;
        let h = self.image.height() as i64;
        let x = uv[0] * w as f64 - 0.5;
        let y = (1. - uv[1]) * h as f64 - 0.5;
        let ix = x.floor() as i64;
        let iy = y.floor() as i64;
        let fx = x - x.floor();
        let fy = y - y.floor();
        let mut out = [0.; 4];
        for (dy, wy) in [(0, 1. - fy), (1, fy)] {
            for (dx, wx) in [(0, 1. - fx), (1, fx)] {
                let p = self.image.get_pixel(
                    (ix + dx).rem_euclid(w) as u32,
                    (iy + dy).rem_euclid(h) as u32,
                );
                for i in 0..4 {
                    let mut v = p[i] as f64 / 255.;
                    if i < 3 && color && !self.linear {
                        v = srgb(v);
                    }
                    out[i] += v * wx * wy;
                }
            }
        }
        out
    }
}
