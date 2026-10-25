//! Parametric cuboid bevels. Reference-derived geometry stencils contain no code.
//! Canonical cuboid topology is validated before evaluating width in its frame.
use super::{
    Value,
    math::{add, cross, dot, length, mul, sub},
    num, vec3,
};
use serde_json::json;
use std::sync::OnceLock;
const CUBE_FACES: [[usize; 4]; 6] = [
    [0, 1, 3, 2],
    [2, 3, 7, 6],
    [6, 7, 5, 4],
    [4, 5, 1, 0],
    [2, 6, 4, 0],
    [7, 3, 1, 5],
];
static STENCILS: OnceLock<Value> = OnceLock::new();
static UV_STENCILS: OnceLock<Value> = OnceLock::new();
static VERTEX_STENCILS: OnceLock<Value> = OnceLock::new();
static VERTEX_UV_STENCILS: OnceLock<Value> = OnceLock::new();
fn coefficients(bytes: &[u8]) -> Value {
    serde_json::from_reader(flate2::read::ZlibDecoder::new(bytes))
        .expect("validated compressed bevel coefficients")
}

fn uv_mode(layer: &Value) -> Result<&'static str, String> {
    let data = layer["data"].as_array().ok_or("Invalid BEVEL UV layer")?;
    if data.len() != 24 {
        return Err("BEVEL requires one UV per cuboid corner".into());
    }
    let uv = |i: usize| [num(&data[i][0]), num(&data[i][1])];
    for f in 0..6 {
        let [a, b, c, d] = std::array::from_fn(|i| uv(f * 4 + i));
        if (0..2).any(|i| (a[i] + c[i] - b[i] - d[i]).abs() > 1e-6) {
            return Err(
                "BEVEL UVs require affine quad maps; non-affine corner maps are unsupported".into(),
            );
        }
    }
    let reference = super::cube_uv();
    let mut default = true;
    let mut islands = true;
    for a in 0..24 {
        for b in a + 1..24 {
            if CUBE_FACES[a / 4][a % 4] != CUBE_FACES[b / 4][b % 4] {
                continue;
            }
            let same = uv(a) == uv(b);
            // Near, unequal seams depend on Blender's UV connectivity tolerance.
            // Do not silently turn such seams into either joined or split corners.
            if !same && (0..2).all(|i| (uv(a)[i] - uv(b)[i]).abs() < 1e-4) {
                return Err(
                    "BEVEL requires exact joined UV corners or clearly separated islands".into(),
                );
            }
            default &= same == (reference[a] == reference[b]);
            islands &= !same;
        }
    }
    if default {
        Ok("default")
    } else if islands {
        Ok("islands")
    } else {
        Err(
            "BEVEL supports the cube primitive UV seam layout or six separate affine face islands"
                .into(),
        )
    }
}

fn interpolate_uvs(
    mesh: &Value,
    result: &mut Value,
    stencil: &Value,
    lengths: [f64; 3],
    axes: [[f64; 3]; 3],
    options: (f64, usize, bool),
) -> Result<(), String> {
    let (width, segments, vertex_only) = options;
    let layers = mesh["uv_layers"].as_array().unwrap();
    if layers.is_empty() {
        return Ok(());
    }
    if vertex_only && segments > 1 && segments % 2 == 1 {
        return Err("Textured vertex BEVEL supports one or even segments; use calc_uvs=False for odd segments 3/5/7".into());
    }
    let modes = layers.iter().map(uv_mode).collect::<Result<Vec<_>, _>>()?;
    if modes.iter().any(|m| m != &modes[0]) {
        return Err("BEVEL requires the same seam layout in every UV layer".into());
    }
    if segments % 2 == 1
        && (0..3).any(|i| (0..3).any(|j| (axes[i][j] - f64::from(i == j)).abs() > 1e-6))
    {
        return Err("Textured BEVEL with odd segments requires a cuboid aligned with its local axes; leave object rotation unapplied or use even segments".into());
    }
    let table = if vertex_only {
        VERTEX_UV_STENCILS.get_or_init(|| {
            coefficients(include_bytes!(concat!(
                env!("OUT_DIR"),
                "/bevel_vertex_uv_stencils.json.zlib"
            )))
        })
    } else {
        UV_STENCILS.get_or_init(|| {
            coefficients(include_bytes!(concat!(
                env!("OUT_DIR"),
                "/bevel_uv_stencils.json.zlib"
            )))
        })
    };
    let key = format!(
        "{}{}",
        modes[0],
        if width * width * 0.5 < 1e-4 {
            "_narrow"
        } else {
            ""
        }
    );
    let map = &table["tables"][&key][segments - 1];
    let faces = result["faces"].as_array().unwrap();
    let vertices = result["vertices"].as_array().unwrap();
    let corner = |i: usize| {
        std::array::from_fn::<_, 3, _>(|axis| lengths[axis] * ((i >> (2 - axis)) & 1) as f64)
    };
    let mut output = Vec::new();
    for layer in layers {
        let input = layer["data"].as_array().unwrap();
        let uv = |i: usize| [num(&input[i][0]), num(&input[i][1])];
        let mut positions = Vec::<[f64; 2]>::new();
        let mut groups = std::collections::BTreeMap::<(usize, [u64; 2]), Vec<(usize, f64)>>::new();
        for (fi, face) in faces.iter().enumerate() {
            let face = face.as_array().unwrap();
            let first = vec3(&vertices[face[0].as_u64().unwrap() as usize]);
            let mut normal = [0.; 3];
            for i in 1..face.len() - 1 {
                normal = add(
                    normal,
                    cross(
                        sub(vec3(&vertices[face[i].as_u64().unwrap() as usize]), first),
                        sub(
                            vec3(&vertices[face[i + 1].as_u64().unwrap() as usize]),
                            first,
                        ),
                    ),
                );
            }
            let weight = length(normal) * 0.5;
            for vertex in face {
                let vi = vertex.as_u64().unwrap() as usize;
                let v = &stencil["vertices"][vi];
                let original = ((v[0].as_u64().unwrap() << 2)
                    | (v[1].as_u64().unwrap() << 1)
                    | v[2].as_u64().unwrap()) as usize;
                let index = positions.len();
                let mut code = map["loops"][index].as_u64().unwrap() as usize;
                let source = code % 6;
                code /= 6;
                let mut p = [0.; 3];
                for axis in 0..3 {
                    let inset = width
                        * match code % 3 {
                            0 => 0.,
                            1 => 1.,
                            _ => num(&v[axis + 3]),
                        };
                    code /= 3;
                    p[axis] = if v[axis] == 1 {
                        lengths[axis] - inset
                    } else {
                        inset
                    };
                }
                let source_face = CUBE_FACES[source];
                let a = corner(source_face[0]);
                let u = sub(corner(source_face[1]), a);
                let w = sub(corner(source_face[3]), a);
                let delta = sub(p, a);
                let x = dot(delta, u) / dot(u, u);
                let y = dot(delta, w) / dot(w, w);
                let [a, b, d] = [uv(source * 4), uv(source * 4 + 1), uv(source * 4 + 3)];
                positions.push(std::array::from_fn(|i| {
                    a[i] + x * (b[i] - a[i]) + y * (d[i] - a[i])
                }));
                let owner = map["owners"][fi].as_u64().unwrap() as usize;
                let at = CUBE_FACES[owner]
                    .iter()
                    .position(|&v| v == original)
                    .unwrap();
                let key = uv(owner * 4 + at).map(|v| if v == 0. { 0 } else { v.to_bits() });
                groups.entry((vi, key)).or_default().push((index, weight));
            }
        }
        for group in groups.values() {
            let total = group.iter().map(|(_, w)| w).sum::<f64>();
            if total <= 0. {
                return Err("BEVEL UV interpolation encountered a degenerate face group".into());
            }
            let mean = std::array::from_fn(|axis| {
                (group
                    .iter()
                    .map(|&(i, w)| positions[i][axis] * w)
                    .sum::<f64>()
                    / total) as f32 as f64
            });
            for &(i, _) in group {
                positions[i] = mean;
            }
        }
        let mut layer = layer.clone();
        layer["data"] = json!(positions);
        output.push(layer);
    }
    result["uv_layers"] = json!(output);
    Ok(())
}
pub fn apply(mesh: &Value, modifier: &Value) -> Result<Value, String> {
    let requested_width = num(&modifier["width"]);
    let mut width = requested_width;
    let vertex_only = modifier["affect"] == "VERTICES";
    if width == 0. {
        return Ok(mesh.clone());
    }
    let vs = mesh["vertices"].as_array().ok_or("BEVEL needs a mesh")?;
    if vs.len() != 8 || mesh["faces"] != json!(CUBE_FACES) {
        return super::bevel_mesh::apply(mesh, modifier);
    }
    let origin = vec3(&vs[0]);
    let sides = [
        sub(vec3(&vs[4]), origin),
        sub(vec3(&vs[2]), origin),
        sub(vec3(&vs[1]), origin),
    ];
    let lengths = sides.map(length);
    if lengths.iter().any(|&v| v < 1e-8) {
        return Err("BEVEL requires a non-degenerate cuboid".into());
    }
    let axes = std::array::from_fn::<_, 3, _>(|i| mul(sides[i], 1. / lengths[i]));
    if dot(cross(axes[0], axes[1]), axes[2]) < 1. - 1e-6
        || (0..3).any(|i| ((i + 1)..3).any(|j| dot(axes[i], axes[j]).abs() > 1e-6))
    {
        return Err("BEVEL requires orthogonal, outward-oriented cuboid axes".into());
    }
    for (i, v) in vs.iter().enumerate() {
        let p = add(
            origin,
            add(
                mul(sides[0], ((i >> 2) & 1) as f64),
                add(
                    mul(sides[1], ((i >> 1) & 1) as f64),
                    mul(sides[2], (i & 1) as f64),
                ),
            ),
        );
        if length(sub(p, vec3(v))) > lengths.iter().copied().fold(0., f64::max) * 1e-6 {
            return Err(
                "BEVEL requires a rectangular cuboid; this mesh has deformed corners".into(),
            );
        }
    }
    if modifier["limit_method"] == "ANGLE"
        && num(&modifier["angle_limit"]) > std::f64::consts::FRAC_PI_2
    {
        return Ok(mesh.clone());
    }
    let limit = lengths.iter().copied().fold(f64::INFINITY, f64::min) * 0.5;
    if width >= limit {
        if modifier["use_clamp_overlap"] != true {
            return Err("BEVEL overlapping geometry requires use_clamp_overlap=True".into());
        }
        // Preserve a sub-tolerance positive gap at collapsed-face boundaries so
        // preview/export triangulation does not inherit zero-area limit faces.
        width = limit - (limit * 1e-6).min(1e-6);
    }
    for field in ["loop_normals", "colors"] {
        if !mesh[field].as_array().unwrap().is_empty() {
            return Err(format!(
                "BEVEL requires a cuboid without {field}; custom corner normals and colors are unsupported"
            ));
        }
    }
    for field in ["material_indices", "smooth"] {
        let values = mesh[field].as_array().unwrap();
        if values.iter().any(|v| v != &values[0]) {
            return Err(
                "BEVEL currently requires uniform face material and smooth settings".into(),
            );
        }
    }
    let n = modifier["segments"].as_u64().unwrap() as usize;
    let table = if vertex_only {
        VERTEX_STENCILS.get_or_init(|| {
            coefficients(include_bytes!(concat!(
                env!("OUT_DIR"),
                "/bevel_vertex_stencils.json.zlib"
            )))
        })
    } else {
        STENCILS.get_or_init(|| {
            coefficients(include_bytes!(concat!(
                env!("OUT_DIR"),
                "/bevel_stencils.json.zlib"
            )))
        })
    };
    let stencil = &table["stencils"][n - 1];
    let vertices = stencil["vertices"]
        .as_array()
        .unwrap()
        .iter()
        .map(|v| {
            let mut p = origin;
            for i in 0..3 {
                let inset = width * num(&v[i + 3]);
                let distance = if v[i] == 1 { lengths[i] - inset } else { inset };
                p = add(p, mul(axes[i], distance));
            }
            json!(p.map(|v| v as f32))
        })
        .collect::<Vec<_>>();
    let faces = stencil["faces"].as_array().unwrap();
    // Validate the evaluated f32 geometry, at the same relative area threshold
    // as review, before committing a modifier. A positive analytic clamp gap
    // can still collapse at the export precision of a thin/translated cuboid.
    let area_epsilon = lengths.iter().map(|v| v * v).sum::<f64>() * 1e-12;
    for face in faces {
        let points: Vec<_> = face
            .as_array()
            .unwrap()
            .iter()
            .map(|i| vec3(&vertices[i.as_u64().unwrap() as usize]))
            .collect();
        let triangles = super::geometry::triangulate(&points).map_err(|_| format!("BEVEL width {requested_width} (evaluated {width}) cannot triangulate this cuboid at f32 precision; half-thickness limit {limit}. Reduce width below {limit}, reduce segments or increase thickness"))?;
        if triangles.iter().any(|t| {
            length(cross(
                sub(points[t[1]], points[t[0]]),
                sub(points[t[2]], points[t[0]]),
            )) <= area_epsilon
        }) {
            return Err(format!(
                "BEVEL width {requested_width} (evaluated {width}) creates numerically degenerate faces at f32 precision; half-thickness limit {limit}, segments {n}. Reduce width below {limit}, reduce segments or increase thickness; clamp_overlap cannot guarantee representable faces"
            ));
        }
    }
    let mut edges = std::collections::BTreeSet::new();
    for f in faces {
        let f = f.as_array().unwrap();
        for i in 0..f.len() {
            let a = f[i].as_u64().unwrap();
            let b = f[(i + 1) % f.len()].as_u64().unwrap();
            edges.insert((a.min(b), a.max(b)));
        }
    }
    let mut result = mesh.clone();
    result["vertices"] = json!(vertices);
    result["faces"] = json!(faces);
    result["edges"] = json!(edges.into_iter().map(|(a, b)| [a, b]).collect::<Vec<_>>());
    result["material_indices"] = json!(vec![mesh["material_indices"][0].clone(); faces.len()]);
    result["smooth"] = json!(vec![mesh["smooth"][0].clone(); faces.len()]);
    interpolate_uvs(
        mesh,
        &mut result,
        stencil,
        lengths,
        axes,
        (width, n, vertex_only),
    )?;
    Ok(result)
}
