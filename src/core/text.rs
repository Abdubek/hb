//! Bounded contour tessellation for static text outlines.
use super::Value;
use serde_json::json;
use std::ffi::{CStr, c_char};
unsafe extern "C" {
    fn hb_text_triangulate(
        xy: *const f64,
        lengths: *const u32,
        count: usize,
        triangles: *mut u32,
        capacity: usize,
        error: *mut c_char,
        error_size: usize,
    ) -> usize;
}
pub fn triangulate(contours: &Value) -> Result<Value, String> {
    let contours = contours
        .as_array()
        .filter(|a| a.len() <= 128)
        .ok_or("At most 128 glyph contours")?;
    let mut lengths = Vec::new();
    let mut xy = Vec::new();
    for contour in contours {
        let points = contour
            .as_array()
            .filter(|a| a.len() >= 3 && a.len() <= 32768)
            .ok_or("Invalid glyph contour")?;
        lengths.push(points.len() as u32);
        for point in points {
            let point = point
                .as_array()
                .filter(|a| a.len() == 2)
                .ok_or("Expected 2D glyph point")?;
            for value in point {
                xy.push(
                    value
                        .as_f64()
                        .filter(|v| v.is_finite() && v.abs() <= 100.)
                        .ok_or("Invalid glyph coordinate")?,
                );
            }
        }
    }
    if xy.len() > 200000 {
        return Err("Glyph point limit exceeded".into());
    }
    let capacity = xy.len() + 256;
    let mut triangles = vec![0; capacity * 3];
    let mut error = [0 as c_char; 256];
    // All buffers live through the call. C++ catches exceptions and checks output capacity.
    let count = unsafe {
        hb_text_triangulate(
            xy.as_ptr(),
            lengths.as_ptr(),
            lengths.len(),
            triangles.as_mut_ptr(),
            capacity,
            error.as_mut_ptr(),
            error.len(),
        )
    };
    if count == usize::MAX {
        return Err(unsafe { CStr::from_ptr(error.as_ptr()) }
            .to_string_lossy()
            .into_owned());
    }
    triangles.truncate(count * 3);
    if triangles.iter().any(|&i| i as usize >= xy.len() / 2) {
        return Err("Invalid tessellation index".into());
    }
    Ok(json!(triangles.chunks(3).collect::<Vec<_>>()))
}

pub fn validate_font(font: &Value) -> Result<(), String> {
    if font["scale"]
        .as_f64()
        .is_none_or(|v| !v.is_finite() || v <= 0. || v > 1.)
    {
        return Err("Invalid font scale".into());
    }
    let glyphs = font["glyphs"]
        .as_object()
        .filter(|g| g.len() == 95)
        .ok_or("Expected printable ASCII font map")?;
    for (character, glyph) in glyphs {
        if character.len() != 1 || !(32..=126).contains(&character.as_bytes()[0]) {
            return Err("Invalid font character".into());
        }
        if glyph.is_null() {
            continue;
        }
        if glyph["advance"]
            .as_f64()
            .is_none_or(|v| !v.is_finite() || !(0. ..=100.).contains(&v))
        {
            return Err("Invalid font advance".into());
        }
        let contours = glyph["contours"]
            .as_array()
            .filter(|a| a.len() <= 128)
            .ok_or("Invalid font contours")?;
        let mut count = 0;
        for contour in contours {
            let points = contour.as_array().ok_or("Invalid font contour")?;
            count += points.len();
            for point in points {
                if point.as_array().is_none_or(|p| {
                    p.len() != 3
                        || p[2].as_bool().is_none()
                        || p[..2].iter().any(|v| {
                            v.as_f64()
                                .is_none_or(|v| !v.is_finite() || v.abs() > 65536.)
                        })
                }) {
                    return Err("Invalid font point".into());
                }
            }
        }
        if count > 8192 {
            return Err("Font glyph point limit exceeded".into());
        }
    }
    Ok(())
}
