//! Bounded ASCII/binary STL import; coordinates are Z-up meters.
use super::Scene;
use serde_json::json;
use std::{
    collections::{BTreeMap, BTreeSet},
    path::Path,
};
const LIMIT: usize = 100_000;

type Triangle = [[f32; 3]; 3];

fn ascii(bytes: &[u8]) -> Result<Vec<Triangle>, String> {
    let source = std::str::from_utf8(bytes)
        .map_err(|_| "STL is neither exact-length binary nor UTF-8 ASCII")?;
    let mut lines = source
        .lines()
        .map(str::trim)
        .filter(|line| !line.is_empty());
    let first = lines.next().ok_or("ASCII STL requires solid/endsolid")?;
    if first.split_whitespace().next() != Some("solid") {
        return Err("ASCII STL must start with solid".into());
    }
    let mut triangles = Vec::new();
    let mut ended = false;
    while let Some(line) = lines.next() {
        let fields: Vec<_> = line.split_whitespace().collect();
        if fields.first() == Some(&"endsolid") {
            ended = true;
            break;
        }
        if fields.len() != 5 || fields[..2] != ["facet", "normal"] {
            return Err("ASCII STL expects facet normal nx ny nz".into());
        }
        for value in &fields[2..] {
            value
                .parse::<f32>()
                .map_err(|_| "Invalid STL facet normal")?;
        }
        if lines
            .next()
            .map(|line| line.split_whitespace().collect::<Vec<_>>())
            != Some(vec!["outer", "loop"])
        {
            return Err("ASCII STL expects outer loop".into());
        }
        let mut triangle = [[0.; 3]; 3];
        for vertex in &mut triangle {
            let fields: Vec<_> = lines
                .next()
                .ok_or("Truncated ASCII STL vertex")?
                .split_whitespace()
                .collect();
            if fields.len() != 4 || fields[0] != "vertex" {
                return Err("ASCII STL triangles require exactly three XYZ vertices".into());
            }
            for (coordinate, value) in vertex.iter_mut().zip(&fields[1..]) {
                *coordinate = value.parse().map_err(|_| "Invalid STL coordinate")?;
            }
        }
        if lines.next() != Some("endloop") || lines.next() != Some("endfacet") {
            return Err("ASCII STL expects endloop/endfacet".into());
        }
        triangles.push(triangle);
        if triangles.len() > LIMIT {
            return Err("STL limit is 100,000 input triangles".into());
        }
    }
    if !ended || lines.next().is_some() {
        return Err("ASCII STL requires one complete solid; trailing data is unsupported".into());
    }
    Ok(triangles)
}

pub fn import(scene: &mut Scene, path: &Path) -> Result<Vec<String>, String> {
    let file = std::fs::File::open(path).map_err(|e| format!("{}: {e}", path.display()))?;
    use std::io::Read;
    let mut bytes = Vec::new();
    file.take(32 * 1024 * 1024 + 1)
        .read_to_end(&mut bytes)
        .map_err(|e| e.to_string())?;
    if bytes.len() > 32 * 1024 * 1024 {
        return Err("STL input limit is 32 MiB".into());
    }
    let mut attributes = false;
    let triangles = if bytes.len() >= 84
        && 84_u64 + 50 * u64::from(u32::from_le_bytes(bytes[80..84].try_into().unwrap()))
            == bytes.len() as u64
    {
        let count = (bytes.len() - 84) / 50;
        if count > LIMIT {
            return Err("STL limit is 100,000 input triangles".into());
        }
        bytes[84..]
            .as_chunks::<50>()
            .0
            .iter()
            .map(|facet| {
                attributes |= facet[48] != 0 || facet[49] != 0;
                std::array::from_fn(|i| {
                    std::array::from_fn(|j| {
                        let offset = 12 + i * 12 + j * 4;
                        f32::from_le_bytes(facet[offset..offset + 4].try_into().unwrap())
                    })
                })
            })
            .collect()
    } else {
        ascii(&bytes)?
    };
    let mut vertices = Vec::new();
    let mut vertex_map = BTreeMap::new();
    let mut faces = Vec::new();
    let mut known = BTreeSet::new();
    let mut duplicates = 0;
    let mut degenerates = 0;
    for triangle in triangles {
        let mut face = [0; 3];
        for (index, vertex) in triangle.into_iter().enumerate() {
            if vertex.iter().any(|v| !v.is_finite()) {
                return Err("STL vertex coordinates must be finite float32 values".into());
            }
            let vertex = vertex.map(|v| if v == 0. { 0. } else { v });
            let bits = vertex.map(f32::to_bits);
            face[index] = *vertex_map.entry(bits).or_insert_with(|| {
                vertices.push(vertex);
                vertices.len() - 1
            });
        }
        if vertices.len() > LIMIT {
            return Err("STL limit is 100,000 unique vertices".into());
        }
        let mut key = face;
        key.sort();
        if key[0] == key[1] || key[1] == key[2] {
            degenerates += 1;
        } else if !known.insert(key) {
            duplicates += 1;
        } else {
            faces.push(face);
        }
    }
    let mut candidate = scene.clone();
    let name = path.file_stem().and_then(|s| s.to_str()).unwrap_or("STL");
    let mesh = candidate.create("meshes", name, json!({}))?;
    candidate.mesh_from(mesh, json!(vertices), json!([]), json!(faces), false)?;
    let normals: Vec<_> = faces
        .iter()
        .flat_map(|face| {
            let p = face.map(|i| vertices[i].map(f64::from));
            let mut normal = super::geometry::face_normal(&p);
            if normal == [0.; 3] {
                normal = [0., 0., 1.];
            }
            [normal.map(|v| v as f32); 3]
        })
        .collect();
    candidate.get_mut("meshes", mesh)?["loop_normals"] = json!(normals);
    let object = candidate.create("objects", name, json!({"data":{"kind":"meshes","id":mesh}}))?;
    candidate.link(candidate.active_collection, object, false, false)?;
    candidate.validate()?;
    *scene = candidate;
    let mut warnings = vec!["STL coordinates interpreted as Z-up meters; units are not declared. Normals are derived from geometry.".into()];
    if duplicates != 0 || degenerates != 0 {
        warnings.push(format!(
            "STL removed {duplicates} duplicate and {degenerates} repeated-vertex triangles."
        ));
    }
    if attributes {
        warnings.push("STL nonstandard binary facet color/attribute bytes ignored.".into());
    }
    Ok(warnings)
}
