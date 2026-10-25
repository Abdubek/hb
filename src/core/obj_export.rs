//! Wavefront OBJ/MTL export from evaluated scene geometry.
use super::{
    Scene, Value,
    geometry::{self, Geometry},
    id, images,
    math::*,
    num,
    render::Material,
    text, vec3,
};
use std::{
    collections::BTreeMap,
    fmt::Write,
    path::{Path, PathBuf},
};

fn name(value: &str) -> String {
    value
        .chars()
        .map(|c| {
            if c.is_whitespace() || matches!(c, '/' | '\\' | '#') {
                '_'
            } else {
                c
            }
        })
        .collect()
}

pub fn export(source: &Scene, path: &Path, options: &Value) -> Result<Vec<String>, String> {
    let mut scene = source.clone();
    if options["apply"] == true {
        if let Some(evaluated) = super::modeling::for_export(&scene)? {
            scene = evaluated;
        }
    } else {
        for object in &mut scene.objects {
            object["modifiers"] = serde_json::json!([]);
        }
    }
    let matrix = from_flat(
        &options["matrix"]
            .as_array()
            .ok_or("Expected axis matrix")?
            .iter()
            .map(num)
            .collect::<Vec<_>>(),
    )?;
    let geometry = Geometry::new(&scene, false)?;
    let mut normals = BTreeMap::new();
    for object in &geometry.objects {
        for &triangle in &object.triangles {
            let t = &geometry.triangles[triangle];
            for i in 0..3 {
                normals.insert((object.id, t.loop_indices[i]), normal(matrix, t.n[i]));
            }
        }
    }
    let uv_enabled = options["uvs"] != false;
    let normals_enabled = options["normals"] != false;
    let materials_enabled = options["materials"] != false;
    let path = if path
        .extension()
        .is_some_and(|e| e.eq_ignore_ascii_case("obj"))
    {
        path.to_path_buf()
    } else {
        PathBuf::from(format!("{}.obj", path.display()))
    };
    let mtl_path = path.with_extension("mtl");
    let mut obj = String::from("# hb Wavefront OBJ\n");
    let mut used = BTreeMap::new();
    if materials_enabled {
        writeln!(
            obj,
            "mtllib {}",
            mtl_path
                .file_name()
                .ok_or("Expected export filename")?
                .to_string_lossy()
        )
        .unwrap();
    }
    let (mut vertex_offset, mut uv_offset, mut normal_offset) = (1, 1, 1);
    for key in scene.linked_ids() {
        let object = scene.object(key)?;
        if scene.mesh(object).is_none()
            || (options["selection"] == true && object["selected"] != true)
        {
            continue;
        }
        let mesh = scene.get("meshes", id(&object["data"]))?;
        let vertices: Vec<_> = mesh["vertices"]
            .as_array()
            .unwrap()
            .iter()
            .map(vec3)
            .collect();
        let world = scene.world(key)?;
        let transform = matmul(matrix, world);
        let reflected = dot(
            cross(
                [world[0][0], world[1][0], world[2][0]],
                [world[0][1], world[1][1], world[2][1]],
            ),
            [world[0][2], world[1][2], world[2][2]],
        ) < 0.;
        let original_mesh_name =
            text(&source.get("meshes", id(&source.object(key)?["data"]))?["name"]);
        let object_name = if text(&object["name"]) == original_mesh_name {
            name(text(&object["name"]))
        } else {
            format!(
                "{}_{}",
                name(text(&object["name"])),
                name(original_mesh_name)
            )
        };
        writeln!(obj, "o {object_name}").unwrap();
        for vertex in &vertices {
            let [x, y, z] = point(transform, *vertex);
            writeln!(obj, "v {x:.6} {y:.6} {z:.6}").unwrap();
        }
        let uv = mesh["uv_layers"][mesh["active_uv"].as_u64().unwrap_or(0) as usize]["data"]
            .as_array()
            .filter(|_| uv_enabled);
        if let Some(uv) = uv {
            for value in uv {
                writeln!(obj, "vt {:.6} {:.6}", num(&value[0]), num(&value[1])).unwrap();
            }
        }
        let loop_count: usize = mesh["faces"]
            .as_array()
            .unwrap()
            .iter()
            .map(|f| f.as_array().unwrap().len())
            .sum();
        if normals_enabled {
            for index in 0..loop_count {
                let [x, y, z] = normals.get(&(key, index)).copied().unwrap_or([0.; 3]);
                writeln!(obj, "vn {x:.4} {y:.4} {z:.4}").unwrap();
            }
        }
        let mut loop_start = 0;
        for (fi, face) in mesh["faces"].as_array().unwrap().iter().enumerate() {
            let indices: Vec<_> = face
                .as_array()
                .unwrap()
                .iter()
                .map(|v| v.as_u64().unwrap() as usize)
                .collect();
            let polygons: Vec<Vec<usize>> = if options["triangles"] == true {
                geometry::triangulate(&indices.iter().map(|&i| vertices[i]).collect::<Vec<_>>())?
                    .into_iter()
                    .map(|t| t.to_vec())
                    .collect()
            } else {
                vec![(0..indices.len()).collect()]
            };
            let slot = mesh["material_indices"][fi].as_u64().unwrap_or(0) as usize;
            if materials_enabled {
                let material = mesh["materials"][slot].as_u64();
                let material_name = if let Some(k) = material {
                    format!("{}_{}", name(text(&scene.get("materials", k)?["name"])), k)
                } else {
                    "None".into()
                };
                used.insert(material, material_name.clone());
                writeln!(obj, "usemtl {material_name}").unwrap();
            }
            writeln!(
                obj,
                "s {}",
                if mesh["smooth"][fi] == true {
                    "1"
                } else {
                    "off"
                }
            )
            .unwrap();
            for mut polygon in polygons {
                if reflected {
                    polygon.reverse();
                }
                obj.push('f');
                for corner in polygon {
                    let vertex = vertex_offset + indices[corner];
                    let uv_index = uv_offset + loop_start + corner;
                    let normal_index = normal_offset + loop_start + corner;
                    match (uv.is_some(), normals_enabled) {
                        (true, true) => write!(obj, " {vertex}/{uv_index}/{normal_index}"),
                        (true, false) => write!(obj, " {vertex}/{uv_index}"),
                        (false, true) => write!(obj, " {vertex}//{normal_index}"),
                        (false, false) => write!(obj, " {vertex}"),
                    }
                    .unwrap();
                }
                obj.push('\n');
            }
            loop_start += indices.len();
        }
        vertex_offset += vertices.len();
        uv_offset += uv.map_or(0, Vec::len);
        normal_offset += if normals_enabled { loop_count } else { 0 };
    }
    let mut outputs = vec![];
    let mut warnings = vec![];
    if materials_enabled {
        let mut mtl = String::from("# hb scalar Principled to legacy MTL\n");
        for (key, material_name) in used {
            let m = if let Some(key) = key {
                Material::from(&scene, scene.get("materials", key)?)?
            } else {
                Material::default()
            };
            let ambient = if m.metallic > 0. { m.metallic } else { 1. };
            let illumination = match (m.metallic > 0., m.base[3] < 1.) {
                (true, true) => 6,
                (true, false) => 3,
                (false, true) => 9,
                (false, false) => 2,
            };
            writeln!(mtl,"\nnewmtl {material_name}\nNs {:.6}\nKa {ambient:.6} {ambient:.6} {ambient:.6}\nKd {:.6} {:.6} {:.6}\nKs 0.500000 0.500000 0.500000\nKe {:.6} {:.6} {:.6}\nNi 1.450000\nd {:.6}\nillum {illumination}",(1.-m.roughness).powi(2)*1000.,m.base[0],m.base[1],m.base[2],m.emission[0],m.emission[1],m.emission[2],m.base[3]).unwrap();
            for (kind, image, color) in [
                ("map_Kd", m.color_image, true),
                ("map_d", m.alpha_image, false),
                ("map_Bump", m.normal_image, false),
            ] {
                if let Some(image) = image {
                    let file = format!("{material_name}_{kind}.png");
                    outputs.push((
                        path.with_file_name(&file),
                        images::png(scene.get("images", image)?, color)?,
                    ));
                    writeln!(mtl, "{kind} {file}").unwrap();
                }
            }
            if m.mr_image.is_some() {
                warnings.push(format!("Material {material_name}: packed metallic/roughness texture cannot be represented by a single MTL map; scalar factors were exported."));
            }
        }
        outputs.push((mtl_path, mtl.into_bytes()));
    }
    outputs.push((path, obj.into_bytes()));
    for (path, bytes) in outputs {
        crate::cli::atomic_write(&path, &bytes).map_err(|e| format!("{}: {e}", path.display()))?;
    }
    Ok(warnings)
}
