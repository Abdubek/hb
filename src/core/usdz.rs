//! USDZ packages: a USDA default layer and embedded PNG assets, no USD runtime.
use super::{
    Scene, Value, geometry, id, images,
    math::*,
    num,
    render::{Camera, Material},
    text, vec3,
};
use std::{
    collections::{BTreeMap, BTreeSet},
    fmt::Write,
};

fn quoted(value: &str) -> String {
    serde_json::to_string(value).unwrap()
}
fn tuple(values: &[f64]) -> String {
    format!(
        "({})",
        values
            .iter()
            .map(ToString::to_string)
            .collect::<Vec<_>>()
            .join(", ")
    )
}
fn array<T: std::fmt::Display>(values: impl IntoIterator<Item = T>) -> String {
    format!(
        "[{}]",
        values
            .into_iter()
            .map(|v| v.to_string())
            .collect::<Vec<_>>()
            .join(", ")
    )
}
fn identifier(value: &str) -> String {
    let mut value: String = value
        .chars()
        .map(|c| {
            if c.is_ascii_alphanumeric() || c == '_' {
                c
            } else {
                '_'
            }
        })
        .collect();
    if value.is_empty() || value.as_bytes()[0].is_ascii_digit() {
        value.insert(0, '_');
    }
    value
}
fn property(out: &mut String, kind: &str, name: &str, value: impl std::fmt::Display) {
    writeln!(out, "{kind} {name} = {value}").unwrap();
}

pub fn export(scene: &Scene) -> Result<(Vec<u8>, Vec<String>), String> {
    let evaluated = super::modeling::for_export(scene)?;
    let scene = evaluated.as_ref().unwrap_or(scene);
    let linked: BTreeSet<_> = scene.linked_ids().into_iter().collect();
    let mut names = BTreeMap::new();
    let mut used = BTreeSet::from(["Looks".to_owned()]);
    for &key in &linked {
        let base = identifier(text(&scene.object(key)?["name"]));
        let mut name = base.clone();
        let mut suffix = 0;
        while !used.insert(name.clone()) {
            name = format!("{base}_{key}_{suffix}");
            suffix += 1;
        }
        names.insert(key, name);
    }
    let mut out = String::from(
        "#usda 1.0\n( defaultPrim = \"Scene\"\nmetersPerUnit = 1\nupAxis = \"Z\" )\ndef Xform \"Scene\" {\n",
    );
    let mut assets = BTreeMap::new();
    let mut materials = BTreeSet::new();
    let mut warnings = vec![];
    for &key in &linked {
        let object = scene.object(key)?;
        if scene.mesh(object).is_some() {
            let mesh = scene.get("meshes", id(&object["data"]))?;
            for material in mesh["materials"].as_array().unwrap() {
                if let Some(key) = material.as_u64() {
                    materials.insert(key);
                }
            }
        }
    }
    let has_materials = !materials.is_empty();
    if has_materials {
        out.push_str("def Scope \"Looks\" {\n");
    }
    for key in materials {
        let source = scene.get("materials", key)?;
        let material = Material::from(scene, source)?;
        let path = format!("/Scene/Looks/Mat_{key}");
        writeln!(
            out,
            "def Material \"Mat_{key}\" ( displayName = {} ) {{",
            quoted(text(&source["name"]))
        )
        .unwrap();
        property(
            &mut out,
            "token",
            "outputs:surface.connect",
            format!("<{path}/Surface.outputs:surface>"),
        );
        out.push_str("def Shader \"Surface\" {\nuniform token info:id = \"UsdPreviewSurface\"\n");
        property(
            &mut out,
            "color3f",
            "inputs:diffuseColor",
            tuple(&material.base[..3]),
        );
        if material.emission.iter().any(|v| *v != 0.) {
            property(
                &mut out,
                "color3f",
                "inputs:emissiveColor",
                tuple(&material.emission),
            );
        }
        property(&mut out, "float", "inputs:metallic", material.metallic);
        property(&mut out, "float", "inputs:roughness", material.roughness);
        property(
            &mut out,
            "float",
            "inputs:opacity",
            if material.alpha_mode == "OPAQUE" {
                1.
            } else {
                material.base[3]
            },
        );
        if material.alpha_mode == "MASK" {
            property(
                &mut out,
                "float",
                "inputs:opacityThreshold",
                material.cutoff,
            );
        }
        for (input, image, shader, channel, kind) in [
            (
                "diffuseColor",
                material.color_image,
                "Color",
                "rgb",
                "color3f",
            ),
            (
                "opacity",
                material
                    .alpha_image
                    .filter(|_| material.alpha_mode != "OPAQUE"),
                "Alpha",
                "a",
                "float",
            ),
            ("normal", material.normal_image, "Normal", "rgb", "normal3f"),
            ("roughness", material.mr_image, "MR", "g", "float"),
            ("metallic", material.mr_image, "MR", "b", "float"),
        ] {
            if image.is_some() {
                property(
                    &mut out,
                    kind,
                    &format!("inputs:{input}.connect"),
                    format!("<{path}/{shader}.outputs:{channel}>"),
                );
            }
        }
        out.push_str("token outputs:surface\n}\n");
        let mut textured = false;
        for (shader, image, color, scale, bias) in [
            ("Color", material.color_image, true, material.base, [0.; 4]),
            (
                "Alpha",
                material.alpha_image,
                false,
                [1., 1., 1., material.base[3]],
                [0.; 4],
            ),
            (
                "Normal",
                material.normal_image,
                false,
                [
                    2. * material.normal_strength,
                    2. * material.normal_strength,
                    2.,
                    1.,
                ],
                [
                    -material.normal_strength,
                    -material.normal_strength,
                    -1.,
                    0.,
                ],
            ),
            (
                "MR",
                material.mr_image,
                false,
                [1., material.roughness, material.metallic, 1.],
                [0.; 4],
            ),
        ] {
            let Some(image) = image else { continue };
            textured = true;
            let filename = format!(
                "textures/image_{image}_{}.png",
                if color { "color" } else { "data" }
            );
            if !assets.contains_key(&filename) {
                assets.insert(filename.clone(), texture_png(scene.get("images", image)?)?);
            }
            writeln!(
                out,
                "def Shader \"{shader}\" {{\nuniform token info:id = \"UsdUVTexture\""
            )
            .unwrap();
            property(&mut out, "asset", "inputs:file", format!("@{filename}@"));
            property(
                &mut out,
                "token",
                "inputs:sourceColorSpace",
                quoted(
                    if shader == "Normal"
                        || shader == "MR"
                        || scene.get("images", image)?["colorspace"] == "Non-Color"
                    {
                        "raw"
                    } else {
                        "auto"
                    },
                ),
            );
            property(&mut out, "token", "inputs:wrapS", "\"repeat\"");
            property(&mut out, "token", "inputs:wrapT", "\"repeat\"");
            property(
                &mut out,
                "float2",
                "inputs:st.connect",
                format!("<{path}/UV.outputs:result>"),
            );
            property(&mut out, "float4", "inputs:scale", tuple(&scale));
            property(&mut out, "float4", "inputs:bias", tuple(&bias));
            out.push_str("float3 outputs:rgb\nfloat outputs:r\nfloat outputs:g\nfloat outputs:b\nfloat outputs:a\n}\n");
        }
        if textured {
            out.push_str("def Shader \"UV\" {\nuniform token info:id = \"UsdPrimvarReader_float2\"\nstring inputs:varname = \"st\"\nfloat2 outputs:result\n}\n");
        }
        out.push_str("}\n");
    }
    if has_materials {
        out.push_str("}\n");
    }
    let aspect = num(&scene.render["resolution_x"]) * num(&scene.render["pixel_aspect_x"])
        / (num(&scene.render["resolution_y"]) * num(&scene.render["pixel_aspect_y"]));
    let roots: Vec<_> = linked
        .iter()
        .copied()
        .filter(|&key| {
            scene.object(key).unwrap()["parent"]
                .as_u64()
                .is_none_or(|p| !linked.contains(&p))
        })
        .collect();
    let mut pending: Vec<_> = roots.into_iter().rev().map(Some).collect();
    while let Some(next) = pending.pop() {
        let Some(key) = next else {
            out.push_str("}\n");
            continue;
        };
        let object = scene.object(key)?;
        let kind = scene.obj_type(object);
        let data_kind = match kind {
            "MESH" | "CURVE" | "FONT" => "meshes",
            "CAMERA" => "cameras",
            "LIGHT" => "lights",
            _ => "",
        };
        let data = if data_kind.is_empty() {
            None
        } else {
            Some(scene.get(data_kind, id(&object["data"]))?)
        };
        let schema = match kind {
            "MESH" | "CURVE" | "FONT" => "Mesh",
            "CAMERA" => "Camera",
            "LIGHT" => match text(&data.unwrap()["type"]) {
                "SUN" => "DistantLight",
                "AREA" => {
                    if matches!(text(&data.unwrap()["shape"]), "DISK" | "ELLIPSE") {
                        "DiskLight"
                    } else {
                        "RectLight"
                    }
                }
                _ => "SphereLight",
            },
            _ => "Xform",
        };
        writeln!(
            out,
            "def {schema} {} ( displayName = {}",
            quoted(&names[&key]),
            quoted(text(&object["name"]))
        )
        .unwrap();
        if matches!(kind, "MESH" | "CURVE" | "FONT") {
            out.push_str("prepend apiSchemas = [\"MaterialBindingAPI\"]\n");
        }
        if kind == "LIGHT" && data.unwrap()["type"] == "SPOT" {
            out.push_str("prepend apiSchemas = [\"ShapingAPI\"]\n");
        }
        out.push_str(") {\n");
        property(
            &mut out,
            "custom string",
            "hb:originalName",
            quoted(text(&object["name"])),
        );
        let mut transform = if object["parent"]
            .as_u64()
            .is_some_and(|p| linked.contains(&p))
        {
            scene.local(object)
        } else {
            scene.world(key)?
        };
        if kind == "LIGHT" && data.unwrap()["type"] == "AREA" && data.unwrap()["shape"] == "ELLIPSE"
        {
            let d = data.unwrap();
            let size = num(&d["size"]);
            if size <= 0. {
                return Err("USD ellipse light needs positive size".into());
            }
            let mut stretch = IDENTITY;
            stretch[1][1] = num(&d["size_y"]) / size;
            transform = matmul(transform, stretch);
        }
        let matrix = (0..4)
            .map(|i| tuple(&(0..4).map(|j| transform[j][i]).collect::<Vec<_>>()))
            .collect::<Vec<_>>()
            .join(", ");
        property(
            &mut out,
            "matrix4d",
            "xformOp:transform",
            format!("({matrix})"),
        );
        property(
            &mut out,
            "uniform token[]",
            "xformOpOrder",
            "[\"xformOp:transform\"]",
        );
        if matches!(kind, "MESH" | "CURVE" | "FONT") {
            mesh(&mut out, data.unwrap())?;
        }
        if kind == "CAMERA" {
            let d = data.unwrap();
            let camera = Camera::scene(scene, Some(text(&object["name"])), aspect)?;
            if !camera.perspective {
                warnings.push(format!("USDZ orthographic camera {} uses standard tenths-of-scene-unit apertures; Blender 4.5 imports ortho_scale 10x too large. Divide its imported ortho_scale by 10, or use a perspective camera.",text(&object["name"])));
            }
            let factor = if camera.perspective {
                num(&d["lens"]) / 100.
            } else {
                10.
            };
            property(
                &mut out,
                "token",
                "projection",
                quoted(if camera.perspective {
                    "perspective"
                } else {
                    "orthographic"
                }),
            );
            property(&mut out, "float", "focalLength", num(&d["lens"]) / 100.);
            property(
                &mut out,
                "float",
                "horizontalAperture",
                camera.half_x * 2. * factor,
            );
            property(
                &mut out,
                "float",
                "verticalAperture",
                camera.half_y * 2. * factor,
            );
            property(
                &mut out,
                "float",
                "horizontalApertureOffset",
                camera.shift[0] * factor,
            );
            property(
                &mut out,
                "float",
                "verticalApertureOffset",
                camera.shift[1] * factor,
            );
            property(
                &mut out,
                "float2",
                "clippingRange",
                tuple(&[camera.near, camera.far]),
            );
        }
        if kind == "LIGHT" {
            let d = data.unwrap();
            let ty = text(&d["type"]);
            property(
                &mut out,
                "color3f",
                "inputs:color",
                tuple(&vec3(&d["color"])),
            );
            property(
                &mut out,
                "float",
                "inputs:intensity",
                num(&d["energy"])
                    / if ty == "SUN" {
                        4.
                    } else {
                        std::f64::consts::PI
                    },
            );
            property(&mut out, "bool", "inputs:normalize", 1);
            match ty {
                "SUN" => property(&mut out, "float", "inputs:angle", 0.263),
                "AREA" => {
                    if schema == "DiskLight" {
                        property(&mut out, "float", "inputs:radius", num(&d["size"]) * 0.5);
                    } else {
                        property(&mut out, "float", "inputs:width", num(&d["size"]));
                        property(
                            &mut out,
                            "float",
                            "inputs:height",
                            if d["shape"] == "RECTANGLE" {
                                num(&d["size_y"])
                            } else {
                                num(&d["size"])
                            },
                        );
                    }
                }
                _ => {
                    let radius = num(&d["shadow_soft_size"]);
                    property(&mut out, "float", "inputs:radius", radius);
                    property(
                        &mut out,
                        "bool",
                        "treatAsPoint",
                        if radius == 0. { 1 } else { 0 },
                    );
                    if ty == "SPOT" {
                        property(
                            &mut out,
                            "float",
                            "inputs:shaping:cone:angle",
                            num(&d["spot_size"]).to_degrees() * 0.5,
                        );
                        property(
                            &mut out,
                            "float",
                            "inputs:shaping:cone:softness",
                            num(&d["spot_blend"]),
                        );
                    }
                }
            }
        }
        pending.push(None);
        let children: Vec<_> = linked
            .iter()
            .copied()
            .filter(|&child| scene.object(child).unwrap()["parent"].as_u64() == Some(key))
            .collect();
        pending.extend(children.into_iter().rev().map(Some));
    }
    out.push_str("}\n");
    if scene.scene_world.is_some() {
        warnings.push("USDZ exports mesh/material assets and scene cameras/lights; World environment settings are not included.".into());
    }
    let mut files = vec![("scene.usda".to_owned(), out.into_bytes())];
    files.extend(assets);
    Ok((package(&files)?, warnings))
}

fn mesh(out: &mut String, mesh: &Value) -> Result<(), String> {
    let vertices: Vec<_> = mesh["vertices"]
        .as_array()
        .unwrap()
        .iter()
        .map(vec3)
        .collect();
    let faces: Vec<Vec<usize>> = mesh["faces"]
        .as_array()
        .unwrap()
        .iter()
        .map(|f| {
            f.as_array()
                .unwrap()
                .iter()
                .map(|v| v.as_u64().unwrap() as usize)
                .collect()
        })
        .collect();
    property(
        out,
        "point3f[]",
        "points",
        array(vertices.iter().map(|v| tuple(v))),
    );
    property(
        out,
        "int[]",
        "faceVertexCounts",
        array(faces.iter().map(Vec::len)),
    );
    property(
        out,
        "int[]",
        "faceVertexIndices",
        array(faces.iter().flatten()),
    );
    property(out, "uniform token", "subdivisionScheme", "\"none\"");
    property(out, "uniform token", "orientation", "\"rightHanded\"");
    property(out, "uniform bool", "doubleSided", 1);
    let mut vertex_normals = vec![[0.; 3]; vertices.len()];
    let mut face_normals = vec![];
    for face in &faces {
        let normal = geometry::face_normal(&face.iter().map(|&v| vertices[v]).collect::<Vec<_>>());
        for &v in face {
            vertex_normals[v] = add(vertex_normals[v], normal);
        }
        face_normals.push(normal);
    }
    vertex_normals.iter_mut().for_each(|v| *v = normalize(*v));
    let custom = mesh["loop_normals"].as_array().unwrap();
    let mut normals = vec![];
    let mut corner = 0;
    for (i, face) in faces.iter().enumerate() {
        for &v in face {
            normals.push(if !custom.is_empty() {
                normalize(vec3(&custom[corner]))
            } else if mesh["smooth"][i] == true {
                vertex_normals[v]
            } else {
                face_normals[i]
            });
            corner += 1;
        }
    }
    writeln!(
        out,
        "normal3f[] normals = {} ( interpolation = \"faceVarying\" )",
        array(normals.iter().map(|v| tuple(v)))
    )
    .unwrap();
    for (i, layer) in mesh["uv_layers"].as_array().unwrap().iter().enumerate() {
        let name = if i == mesh["active_uv"].as_u64().unwrap_or(0) as usize {
            "st".to_owned()
        } else {
            format!("uv_{i}")
        };
        writeln!(
            out,
            "texCoord2f[] primvars:{name} = {} ( interpolation = \"faceVarying\" )",
            array(
                layer["data"]
                    .as_array()
                    .unwrap()
                    .iter()
                    .map(|v| tuple(&[num(&v[0]), num(&v[1])]))
            )
        )
        .unwrap();
    }
    let colors = mesh["colors"].as_array().unwrap();
    if !colors.is_empty() {
        writeln!(
            out,
            "color3f[] primvars:displayColor = {} ( interpolation = \"faceVarying\" )",
            array(colors.iter().map(|v| tuple(&vec3(v))))
        )
        .unwrap();
        writeln!(
            out,
            "float[] primvars:displayOpacity = {} ( interpolation = \"faceVarying\" )",
            array(colors.iter().map(|v| num(&v[3])))
        )
        .unwrap();
    }
    let mut groups: BTreeMap<u64, Vec<usize>> = BTreeMap::new();
    for i in 0..faces.len() {
        let slot = mesh["material_indices"][i].as_u64().unwrap_or(0) as usize;
        if let Some(key) = mesh["materials"][slot].as_u64() {
            groups.entry(key).or_default().push(i);
        }
    }
    if groups.len() == 1 && groups.values().next().unwrap().len() == faces.len() {
        let key = groups.keys().next().unwrap();
        property(
            out,
            "rel",
            "material:binding",
            format!("</Scene/Looks/Mat_{key}>"),
        );
    } else {
        for (key, indices) in groups {
            writeln!(out,"def GeomSubset \"Material_{key}\" ( prepend apiSchemas = [\"MaterialBindingAPI\"] ) {{\nuniform token elementType = \"face\"\nuniform token familyName = \"materialBind\"").unwrap();
            property(out, "int[]", "indices", array(indices));
            property(
                out,
                "rel",
                "material:binding",
                format!("</Scene/Looks/Mat_{key}>"),
            );
            out.push_str("}\n");
        }
    }
    Ok(())
}

fn package(files: &[(String, Vec<u8>)]) -> Result<Vec<u8>, String> {
    if files.len() > 65535 {
        return Err("USDZ archive has too many entries".into());
    }
    let mut out = vec![];
    let mut central = vec![];
    fn u16le(out: &mut Vec<u8>, value: u16) {
        out.extend(value.to_le_bytes());
    }
    fn u32le(out: &mut Vec<u8>, value: u32) {
        out.extend(value.to_le_bytes());
    }
    for (name, data) in files {
        let size = u32::try_from(data.len()).map_err(|_| "USDZ entry exceeds 4 GiB")?;
        let offset = u32::try_from(out.len()).map_err(|_| "USDZ archive exceeds 4 GiB")?;
        let length = u16::try_from(name.len()).map_err(|_| "USDZ filename is too long")?;
        let mut crc = flate2::Crc::new();
        crc.update(data);
        let crc = crc.sum();
        let padding = (64 - (out.len() + 30 + name.len() + 4) % 64) % 64;
        u32le(&mut out, 0x04034b50);
        for value in [20, 0, 0, 0, 33] {
            u16le(&mut out, value);
        }
        for value in [crc, size, size] {
            u32le(&mut out, value);
        }
        u16le(&mut out, length);
        u16le(&mut out, (padding + 4) as u16);
        out.extend(name.as_bytes());
        u16le(&mut out, 0x1986);
        u16le(&mut out, padding as u16);
        out.resize(out.len() + padding, 0);
        out.extend(data);
        u32le(&mut central, 0x02014b50);
        for value in [20, 20, 0, 0, 0, 33] {
            u16le(&mut central, value);
        }
        for value in [crc, size, size] {
            u32le(&mut central, value);
        }
        for value in [length, 0, 0, 0, 0] {
            u16le(&mut central, value);
        }
        u32le(&mut central, 0);
        u32le(&mut central, offset);
        central.extend(name.as_bytes());
    }
    let offset = u32::try_from(out.len()).map_err(|_| "USDZ archive exceeds 4 GiB")?;
    let size = u32::try_from(central.len()).map_err(|_| "USDZ directory exceeds 4 GiB")?;
    out.extend(central);
    u32le(&mut out, 0x06054b50);
    for value in [0, 0, files.len() as u16, files.len() as u16] {
        u16le(&mut out, value);
    }
    u32le(&mut out, size);
    u32le(&mut out, offset);
    u16le(&mut out, 0);
    Ok(out)
}

fn texture_png(value: &Value) -> Result<Vec<u8>, String> {
    if let Some(encoded) = value["encoded"].as_str() {
        use base64::Engine;
        let bytes = base64::engine::general_purpose::STANDARD
            .decode(encoded)
            .map_err(|e| e.to_string())?;
        if bytes.starts_with(b"\x89PNG\r\n\x1a\n") {
            return Ok(bytes);
        }
    }
    if value["float_buffer"] != true {
        return images::png(value, false);
    }
    let (width, height) = (num(&value["width"]) as u32, num(&value["height"]) as u32);
    if width == 0 || height == 0 || u64::from(width) * u64::from(height) > 16_777_216 {
        return Err("Invalid USDZ image dimensions".into());
    }
    let pixels = value["pixels"].as_array().ok_or("Missing image pixels")?;
    let mut buffer = image::ImageBuffer::<image::Rgba<u16>, Vec<u16>>::new(width, height);
    for y in 0..height {
        for x in 0..width {
            let offset = if value["solid"] == true {
                0
            } else {
                ((height - 1 - y) * width + x) as usize * 4
            };
            if offset + 4 > pixels.len() {
                return Err("Incomplete image pixels".into());
            }
            buffer.put_pixel(
                x,
                y,
                image::Rgba(std::array::from_fn(|i| {
                    (num(&pixels[offset + i]).clamp(0., 1.) * 65535.).round() as u16
                })),
            );
        }
    }
    let mut bytes = std::io::Cursor::new(vec![]);
    buffer
        .write_to(&mut bytes, image::ImageFormat::Png)
        .map_err(|e| e.to_string())?;
    Ok(bytes.into_inner())
}
