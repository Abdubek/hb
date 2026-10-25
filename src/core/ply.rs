//! PLY 1.0 mesh import with explicit scalar types and bounded element lists.
use super::{Scene, images, math};
use serde_json::json;
use std::{collections::BTreeSet, io::Read, path::Path};
const LIMIT: usize = 100_000;
#[derive(Clone, Copy)]
enum Scalar {
    I8,
    U8,
    I16,
    U16,
    I32,
    U32,
    F32,
    F64,
}
impl Scalar {
    fn parse(s: &str) -> Result<Self, String> {
        Ok(match s {
            "char" | "int8" => Self::I8,
            "uchar" | "uint8" => Self::U8,
            "short" | "int16" => Self::I16,
            "ushort" | "uint16" => Self::U16,
            "int" | "int32" => Self::I32,
            "uint" | "uint32" => Self::U32,
            "float" | "float32" => Self::F32,
            "double" | "float64" => Self::F64,
            _ => return Err(format!("Unsupported PLY scalar type {s}")),
        })
    }
    fn integer(self) -> bool {
        !matches!(self, Self::F32 | Self::F64)
    }
    fn validate(self, v: f64) -> Result<f64, String> {
        if !v.is_finite() {
            return Err("PLY values must be finite".into());
        }
        let (min, max) = match self {
            Self::I8 => (-128., 127.),
            Self::U8 => (0., 255.),
            Self::I16 => (-32768., 32767.),
            Self::U16 => (0., 65535.),
            Self::I32 => (i32::MIN as f64, i32::MAX as f64),
            Self::U32 => (0., u32::MAX as f64),
            Self::F32 => {
                let v = v as f32;
                return if v.is_finite() {
                    Ok(f64::from(v))
                } else {
                    Err("PLY float32 overflow".into())
                };
            }
            Self::F64 => return Ok(v),
        };
        if v < min || v > max || v.fract() != 0. {
            Err("PLY integer is outside its declared scalar type".into())
        } else {
            Ok(v)
        }
    }
}
struct Property {
    name: String,
    scalar: Scalar,
    count: Option<Scalar>,
}
struct Element {
    name: String,
    count: usize,
    properties: Vec<Property>,
}
enum Body<'a> {
    Ascii(std::str::SplitWhitespace<'a>),
    Binary {
        bytes: &'a [u8],
        offset: usize,
        big: bool,
    },
}
impl Body<'_> {
    fn scalar(&mut self, scalar: Scalar) -> Result<f64, String> {
        let value = match self {
            Self::Ascii(words) => words
                .next()
                .ok_or("Truncated ASCII PLY")?
                .parse::<f64>()
                .map_err(|_| "Invalid PLY number")?,
            Self::Binary { bytes, offset, big } => {
                macro_rules! read {
                    ($type:ty) => {{
                        const N: usize = std::mem::size_of::<$type>();
                        let data: [u8; N] = bytes
                            .get(*offset..*offset + N)
                            .ok_or("Truncated binary PLY")?
                            .try_into()
                            .unwrap();
                        *offset += N;
                        (if *big {
                            <$type>::from_be_bytes(data)
                        } else {
                            <$type>::from_le_bytes(data)
                        }) as f64
                    }};
                }
                match scalar {
                    Scalar::I8 => read!(i8),
                    Scalar::U8 => read!(u8),
                    Scalar::I16 => read!(i16),
                    Scalar::U16 => read!(u16),
                    Scalar::I32 => read!(i32),
                    Scalar::U32 => read!(u32),
                    Scalar::F32 => read!(f32),
                    Scalar::F64 => read!(f64),
                }
            }
        };
        scalar.validate(value)
    }
    fn finished(&mut self) -> bool {
        match self {
            Self::Ascii(words) => words.next().is_none(),
            Self::Binary { bytes, offset, .. } => *offset == bytes.len(),
        }
    }
}
fn header(bytes: &[u8]) -> Result<(Vec<Element>, Body<'_>), String> {
    let mut offset = 0;
    let mut format = None;
    let mut elements: Vec<Element> = vec![];
    let mut names = BTreeSet::new();
    loop {
        if offset > 65536 {
            return Err("PLY header limit is 64 KiB".into());
        }
        let end = bytes[offset..]
            .iter()
            .position(|&b| b == b'\n')
            .ok_or("PLY requires a complete newline-terminated header")?
            + offset;
        let line = std::str::from_utf8(&bytes[offset..end])
            .map_err(|_| "PLY header must be UTF-8")?
            .trim();
        if offset == 0 && line != "ply" {
            return Err("PLY must begin with ply".into());
        }
        offset = end + 1;
        let fields: Vec<_> = line.split_whitespace().collect();
        match fields.as_slice() {
            ["ply"] if offset == 4 || offset == 5 => {}
            ["comment", ..] | ["obj_info", ..] => {}
            ["format", kind, "1.0"] if format.is_none() && elements.is_empty() => {
                if !["ascii", "binary_little_endian", "binary_big_endian"].contains(kind) {
                    return Err("Unsupported PLY encoding".into());
                }
                format = Some(*kind);
            }
            ["element", name, count] if format.is_some() => {
                let count = count
                    .parse::<usize>()
                    .map_err(|_| "Invalid PLY element count")?;
                if count > LIMIT || elements.len() >= 32 {
                    return Err(
                        "PLY limits are 100,000 rows per element and 32 element types".into(),
                    );
                }
                if !names.insert(*name) {
                    return Err("Duplicate PLY element declaration".into());
                }
                elements.push(Element {
                    name: (*name).into(),
                    count,
                    properties: vec![],
                });
            }
            ["property", rest @ ..] => {
                let property = match rest {
                    [scalar, name] => Property {
                        name: (*name).into(),
                        scalar: Scalar::parse(scalar)?,
                        count: None,
                    },
                    ["list", count, scalar, name] => {
                        let count = Scalar::parse(count)?;
                        if !count.integer() {
                            return Err("PLY list counts must have integer types".into());
                        }
                        Property {
                            name: (*name).into(),
                            scalar: Scalar::parse(scalar)?,
                            count: Some(count),
                        }
                    }
                    _ => return Err("Malformed PLY property".into()),
                };
                let element = elements
                    .last_mut()
                    .ok_or("PLY property requires an element")?;
                if element.properties.len() >= 64
                    || element.properties.iter().any(|p| p.name == property.name)
                {
                    return Err("PLY allows up to 64 distinct properties per element".into());
                }
                element.properties.push(property);
            }
            ["end_header"] => break,
            _ => return Err(format!("Unsupported PLY header line: {line}")),
        }
    }
    if !names.contains("vertex") {
        return Err("PLY requires a vertex element".into());
    }
    let body = match format.ok_or("PLY requires format 1.0")? {
        "ascii" => Body::Ascii(
            std::str::from_utf8(&bytes[offset..])
                .map_err(|_| "ASCII PLY is not UTF-8")?
                .split_whitespace(),
        ),
        kind => Body::Binary {
            bytes: &bytes[offset..],
            offset: 0,
            big: kind == "binary_big_endian",
        },
    };
    Ok((elements, body))
}
fn index(v: f64) -> Result<usize, String> {
    if v < 0. || v.fract() != 0. || v >= LIMIT as f64 {
        Err("PLY vertex index must be an integer below 100,000".into())
    } else {
        Ok(v as usize)
    }
}
pub fn import(scene: &mut Scene, path: &Path) -> Result<Vec<String>, String> {
    let file = std::fs::File::open(path).map_err(|e| format!("{}: {e}", path.display()))?;
    let mut bytes = vec![];
    file.take(32 * 1024 * 1024 + 1)
        .read_to_end(&mut bytes)
        .map_err(|e| e.to_string())?;
    if bytes.len() > 32 * 1024 * 1024 {
        return Err("PLY input limit is 32 MiB".into());
    }
    let (elements, mut body) = header(&bytes)?;
    let mut vertices = vec![];
    let mut normals = vec![];
    let mut uvs = vec![];
    let mut colors = vec![];
    let mut input_faces: Vec<Vec<usize>> = vec![];
    let mut edges: BTreeSet<[usize; 2]> = BTreeSet::new();
    let mut ignored = BTreeSet::new();
    let mut budget = 4_000_000usize;
    for element in elements {
        let properties = &element.properties;
        let prop = |name: &str| properties.iter().position(|p| p.name == name);
        let has_normals = ["nx", "ny", "nz"].iter().all(|n| prop(n).is_some());
        let has_uv = prop("s").is_some() && prop("t").is_some();
        let has_color = ["red", "green", "blue"].iter().all(|n| prop(n).is_some());
        let recognized: &[&str] = match element.name.as_str() {
            "vertex" => &[
                "x", "y", "z", "nx", "ny", "nz", "s", "t", "red", "green", "blue", "alpha",
            ],
            "face" => &["vertex_indices", "vertex_index"],
            "edge" => &["vertex1", "vertex2"],
            _ => &[],
        };
        for p in properties {
            if !recognized.contains(&p.name.as_str()) {
                ignored.insert(format!("{}.{}", element.name, p.name));
            }
        }
        if element.name == "vertex" {
            for name in ["x", "y", "z"] {
                if prop(name).is_none() {
                    return Err("PLY vertices require x, y and z".into());
                }
            }
            for group in [
                &["nx", "ny", "nz"][..],
                &["s", "t"][..],
                &["red", "green", "blue"][..],
            ] {
                let count = group.iter().filter(|n| prop(n).is_some()).count();
                if count != 0 && count != group.len() {
                    return Err("PLY normal, UV and RGB property groups must be complete".into());
                }
            }
        }
        for _ in 0..element.count {
            let mut values = Vec::with_capacity(properties.len());
            for p in properties {
                let count = if let Some(count) = p.count {
                    let n = body.scalar(count)?;
                    if !(0. ..=100_000.).contains(&n) {
                        return Err("Invalid PLY list length".into());
                    }
                    n as usize
                } else {
                    1
                };
                budget = budget
                    .checked_sub(count)
                    .ok_or("PLY limit is four million scalar values")?;
                values.push(
                    (0..count)
                        .map(|_| body.scalar(p.scalar))
                        .collect::<Result<Vec<_>, _>>()?,
                );
            }
            let value = |name: &str| -> Result<f64, String> {
                let i = prop(name).ok_or_else(|| format!("Missing PLY {}.{name}", element.name))?;
                if properties[i].count.is_some() {
                    return Err(format!("PLY {name} must be scalar"));
                }
                Ok(values[i][0])
            };
            let vector = |names: [&str; 3]| -> Result<[f64; 3], String> {
                Ok([value(names[0])?, value(names[1])?, value(names[2])?])
            };
            match element.name.as_str() {
                "vertex" => {
                    let p = vector(["x", "y", "z"])?.map(|v| v as f32);
                    if p.iter().any(|v| !v.is_finite()) {
                        return Err("PLY positions must fit finite float32 coordinates".into());
                    }
                    vertices.push(p);
                    if has_normals {
                        let normal = math::normalize(vector(["nx", "ny", "nz"])?);
                        if normal == [0.; 3] {
                            return Err("PLY custom normals must be nonzero; omit nx/ny/nz to calculate geometry normals".into());
                        }
                        normals.push(normal);
                    }
                    if has_uv {
                        let uv = [value("s")? as f32, value("t")? as f32];
                        if uv.iter().any(|v| !v.is_finite()) {
                            return Err("PLY UV coordinates must fit finite float32".into());
                        }
                        uvs.push(uv);
                    }
                    if has_color {
                        let mut color = [1.; 4];
                        for (axis, name) in ["red", "green", "blue", "alpha"].iter().enumerate() {
                            if let Some(i) = prop(name) {
                                let v = value(name)?;
                                let normalized =
                                    match properties[i].scalar {
                                        Scalar::U8 => v / 255.,
                                        Scalar::F32 | Scalar::F64 => v,
                                        _ => return Err(
                                            "PLY colors require uchar or float/double properties"
                                                .into(),
                                        ),
                                    };
                                color[axis] = (if axis < 3 {
                                    images::srgb(normalized.max(0.))
                                } else {
                                    normalized
                                }) as f32;
                                if !color[axis].is_finite() {
                                    return Err("Decoded PLY colors must fit finite float32".into());
                                }
                            }
                        }
                        colors.push(color);
                    }
                }
                "face" => {
                    let i = prop("vertex_indices")
                        .or_else(|| prop("vertex_index"))
                        .ok_or("PLY face requires vertex_indices list")?;
                    if properties[i].count.is_none() || !properties[i].scalar.integer() {
                        return Err("PLY face indices must be an integer list".into());
                    }
                    if values[i].len() > 2048 {
                        return Err("PLY faces support at most 2048 corners".into());
                    }
                    input_faces.push(
                        values[i]
                            .iter()
                            .map(|&v| index(v))
                            .collect::<Result<Vec<_>, _>>()?,
                    );
                }
                "edge" => {
                    let mut e = [index(value("vertex1")?)?, index(value("vertex2")?)?];
                    e.sort();
                    if e[0] != e[1] {
                        edges.insert(e);
                    }
                }
                _ => {}
            }
        }
    }
    if !body.finished() {
        return Err("Unexpected trailing PLY data".into());
    }
    let mut faces = vec![];
    let mut seen = BTreeSet::new();
    let mut removed = 0;
    for face in input_faces {
        if face.iter().any(|&i| i >= vertices.len()) {
            return Err("PLY face vertex index out of range".into());
        }
        for i in 0..face.len() {
            let mut e = [face[i], face[(i + 1) % face.len()]];
            e.sort();
            if e[0] != e[1] {
                edges.insert(e);
            }
        }
        let mut key = face.clone();
        key.sort();
        key.dedup();
        if face.len() < 3 || key.len() != face.len() || !seen.insert(key) {
            removed += 1;
        } else {
            faces.push(face);
        }
    }
    if edges.iter().flatten().any(|&i| i >= vertices.len()) {
        return Err("PLY edge vertex index out of range".into());
    }
    if edges.len() > 300_000 {
        return Err("PLY edge limit is 300,000".into());
    }
    let mut candidate = scene.clone();
    let name = path.file_stem().and_then(|s| s.to_str()).unwrap_or("PLY");
    let mesh = candidate.create("meshes", name, json!({}))?;
    candidate.mesh_from(
        mesh,
        json!(vertices),
        json!(edges),
        json!(faces),
        !normals.is_empty(),
    )?;
    let m = candidate.get_mut("meshes", mesh)?;
    let corners: Vec<_> = faces.iter().flatten().copied().collect();
    if !normals.is_empty() {
        m["loop_normals"] = json!(
            corners
                .iter()
                .map(|&i| normals[i].map(|v| v as f32))
                .collect::<Vec<_>>()
        );
    }
    if !uvs.is_empty() {
        m["uv_layers"] =
            json!([{"name":"UVMap","data":corners.iter().map(|&i|uvs[i]).collect::<Vec<_>>() }]);
    }
    if !colors.is_empty() {
        m["colors"] = json!(corners.iter().map(|&i| colors[i]).collect::<Vec<_>>());
    }
    let object = candidate.create("objects", name, json!({"data":{"kind":"meshes","id":mesh}}))?;
    candidate.link(candidate.active_collection, object, false, false)?;
    candidate.validate()?;
    *scene = candidate;
    let mut warnings=vec!["PLY coordinates interpreted as Z-up meters; units are not declared. Vertex RGB is converted from sRGB to linear.".into()];
    if removed != 0 {
        warnings.push(format!(
            "PLY removed {removed} duplicate/invalid faces; retained valid boundary edges."
        ));
    }
    if !ignored.is_empty() {
        warnings.push(format!(
            "PLY ignored unsupported properties: {}",
            ignored.into_iter().collect::<Vec<_>>().join(", ")
        ));
    }
    if !colors.is_empty()
        && corners.iter().copied().collect::<BTreeSet<_>>().len() != vertices.len()
    {
        warnings.push(
            "PLY colors on loose vertices are not retained by the corner-color mesh contract."
                .into(),
        );
    }
    Ok(warnings)
}
