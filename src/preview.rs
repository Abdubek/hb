// SPDX-License-Identifier: MIT
//! Labeled image grids; callers provide rendered pixels and scale captions.
use image::{ImageFormat, Rgba, RgbaImage};
fn glyph(c: char) -> [u8; 7] {
    match c {
        'A' => [14, 17, 17, 31, 17, 17, 17],
        'B' => [30, 17, 17, 30, 17, 17, 30],
        'C' => [14, 17, 16, 16, 16, 17, 14],
        'D' => [30, 17, 17, 17, 17, 17, 30],
        'E' => [31, 16, 16, 30, 16, 16, 31],
        'F' => [31, 16, 16, 30, 16, 16, 16],
        'G' => [14, 17, 16, 23, 17, 17, 15],
        'H' => [17, 17, 17, 31, 17, 17, 17],
        'I' => [14, 4, 4, 4, 4, 4, 14],
        'J' => [7, 2, 2, 2, 18, 18, 12],
        'K' => [17, 18, 20, 24, 20, 18, 17],
        'L' => [16, 16, 16, 16, 16, 16, 31],
        'M' => [17, 27, 21, 21, 17, 17, 17],
        'N' => [17, 25, 21, 19, 17, 17, 17],
        'O' => [14, 17, 17, 17, 17, 17, 14],
        'P' => [30, 17, 17, 30, 16, 16, 16],
        'Q' => [14, 17, 17, 17, 21, 18, 13],
        'R' => [30, 17, 17, 30, 20, 18, 17],
        'S' => [15, 16, 16, 14, 1, 1, 30],
        'T' => [31, 4, 4, 4, 4, 4, 4],
        'U' => [17, 17, 17, 17, 17, 17, 14],
        'V' => [17, 17, 17, 17, 17, 10, 4],
        'W' => [17, 17, 17, 21, 21, 21, 10],
        'X' => [17, 17, 10, 4, 10, 17, 17],
        'Y' => [17, 17, 10, 4, 4, 4, 4],
        'Z' => [31, 1, 2, 4, 8, 16, 31],
        '0' => [14, 17, 19, 21, 25, 17, 14],
        '1' => [4, 12, 4, 4, 4, 4, 14],
        '2' => [14, 17, 1, 2, 4, 8, 31],
        '3' => [30, 1, 1, 14, 1, 1, 30],
        '4' => [2, 6, 10, 18, 31, 2, 2],
        '5' => [31, 16, 16, 30, 1, 1, 30],
        '6' => [14, 16, 16, 30, 17, 17, 14],
        '7' => [31, 1, 2, 4, 8, 8, 8],
        '8' => [14, 17, 17, 14, 17, 17, 14],
        '9' => [14, 17, 17, 15, 1, 1, 14],
        '.' => [0, 0, 0, 0, 0, 6, 6],
        '-' => [0, 0, 0, 31, 0, 0, 0],
        '/' => [1, 1, 2, 4, 8, 16, 16],
        ':' => [0, 6, 6, 0, 6, 6, 0],
        _ => [0; 7],
    }
}
fn label(im: &mut RgbaImage, x: u32, y: u32, s: &str, color: [u8; 4]) {
    for (i, c) in s.to_uppercase().chars().enumerate() {
        for (row, bits) in glyph(c).iter().enumerate() {
            for col in 0..5 {
                if bits & (1 << (4 - col)) != 0 {
                    let px = x + i as u32 * 6 + col;
                    let py = y + row as u32;
                    if px < im.width() && py < im.height() {
                        im.put_pixel(px, py, Rgba(color));
                    }
                }
            }
        }
    }
}

pub struct ContactSheet {
    image: RgbaImage,
    panel_width: usize,
    panel_height: usize,
    columns: usize,
    count: usize,
    header: usize,
}
impl ContactSheet {
    pub fn new(size: usize, count: usize) -> Result<Self, String> {
        if !(16..=2048).contains(&size) {
            return Err("Expected 16–2048 pixels".into());
        }
        Self::rectangular(size, size, count)
    }
    pub fn rectangular(width: usize, height: usize, count: usize) -> Result<Self, String> {
        if !(16..=4096).contains(&width)
            || !(16..=4096).contains(&height)
            || !(1..=12).contains(&count)
        {
            return Err("Expected 1–12 panels of 16–2048 pixels".into());
        }
        let columns = count.min(3);
        let rows = count.div_ceil(columns);
        let header = if count > 1 { 32 } else { 0 };
        Ok(Self {
            image: RgbaImage::from_pixel(
                (width * columns) as u32,
                ((height + header) * rows) as u32,
                Rgba([19, 26, 37, 255]),
            ),
            panel_width: width,
            panel_height: height,
            columns,
            count,
            header,
        })
    }
    pub fn panel(
        &mut self,
        index: usize,
        image: &RgbaImage,
        title: &str,
        scale: &str,
    ) -> Result<(), String> {
        if index >= self.count
            || image.width() as usize != self.panel_width
            || image.height() as usize != self.panel_height
        {
            return Err("Panel index or dimensions do not match the sheet".into());
        }
        let x = (index % self.columns * self.panel_width) as u32;
        let y = (index / self.columns * (self.panel_height + self.header)) as u32;
        image::imageops::overlay(
            &mut self.image,
            image,
            x as i64,
            (y + self.header as u32) as i64,
        );
        if self.header > 0 {
            label(&mut self.image, x + 12, y + 8, title, [217, 232, 242, 255]);
            label(&mut self.image, x + 12, y + 20, scale, [113, 150, 169, 255]);
        }
        Ok(())
    }
    pub fn width(&self) -> u32 {
        self.image.width()
    }
    pub fn height(&self) -> u32 {
        self.image.height()
    }
    pub fn png(&self) -> Result<Vec<u8>, String> {
        let mut bytes = std::io::Cursor::new(vec![]);
        self.image
            .write_to(&mut bytes, ImageFormat::Png)
            .map_err(|e| e.to_string())?;
        Ok(bytes.into_inner())
    }
}
