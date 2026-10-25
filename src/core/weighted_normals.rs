//! Area/angle normals and a float32 corner-normal codec.
//! Newell sums deliberately use original float32 coordinates: translating the
//! calculation to a local origin changes Blender's packed-normal boundaries.
use super::{Value, num, text};
use serde_json::json;
use std::collections::BTreeMap;

type V = [f32; 3];
fn add(a: V, b: V) -> V {
    std::array::from_fn(|i| a[i] + b[i])
}
fn sub(a: V, b: V) -> V {
    std::array::from_fn(|i| a[i] - b[i])
}
fn mul(a: V, s: f32) -> V {
    a.map(|v| v * s)
}
fn dot(a: V, b: V) -> f32 {
    (a[0] * b[0] + a[1] * b[1]) + a[2] * b[2]
}
fn cross(a: V, b: V) -> V {
    [
        a[1] * b[2] - a[2] * b[1],
        a[2] * b[0] - a[0] * b[2],
        a[0] * b[1] - a[1] * b[0],
    ]
}
fn unit(a: V) -> V {
    let squared = dot(a, a);
    if squared > 1e-35_f32 {
        let length = squared.sqrt();
        a.map(|v| v / length)
    } else {
        [0.; 3]
    }
}
fn unit_reciprocal(a: V) -> V {
    let length = dot(a, a).sqrt();
    if length > 0. {
        mul(a, 1. / length)
    } else {
        [0.; 3]
    }
}
fn weighted_unit(a: V) -> Result<V, String> {
    let squared = dot(a, a);
    if !squared.is_finite() {
        return Err("WEIGHTED_NORMAL weighted sum exceeds finite float32 arithmetic".into());
    }
    Ok(if squared < 1e-12 {
        [0.; 3]
    } else {
        unit_reciprocal(a)
    })
}
fn acos(x: f32) -> f32 {
    // Polynomial coefficients describe the reference's numeric approximation;
    // they are mathematical data, not bundled Blender implementation code.
    let x_abs = x.abs();
    let t = if x_abs < 1. { 1. - (1. - x_abs) } else { 1. };
    let angle = (1. - t).sqrt()
        * (std::f32::consts::FRAC_PI_2
            + t * (-0.213_300_99 + t * (0.077_980_48 + t * -0.021_640_95)));
    if x < 0. {
        std::f32::consts::PI - angle
    } else {
        angle
    }
}
fn root(parents: &mut [usize], mut i: usize) -> usize {
    while parents[i] != i {
        parents[i] = parents[parents[i]];
        i = parents[i];
    }
    i
}

struct Frame {
    normal: V,
    reference: V,
    tangent: V,
    alpha: f32,
    beta: f32,
}
impl Frame {
    fn new(normal: V, reference: V, other: V, edges: &[V]) -> Self {
        let mut frame = Self {
            normal,
            reference: [0.; 3],
            tangent: [0.; 3],
            alpha: 0.,
            beta: 0.,
        };
        if normal == [0.; 3]
            || dot(normal, reference).abs() >= 0.9999
            || dot(normal, other).abs() >= 0.9999
        {
            return frame;
        }
        let mut alpha = 0.;
        for &edge in edges {
            alpha += acos(dot(normal, edge));
        }
        frame.alpha = alpha / edges.len() as f32;
        frame.reference = unit(sub(reference, mul(normal, dot(normal, reference))));
        frame.tangent = unit(cross(normal, frame.reference));
        let other = unit(sub(other, mul(normal, dot(normal, other))));
        frame.beta = if dot(frame.reference, other) >= 0.9999 {
            std::f32::consts::TAU
        } else {
            let angle = acos(dot(frame.reference, other));
            if dot(frame.tangent, other) < 0. {
                std::f32::consts::TAU - angle
            } else {
                angle
            }
        };
        frame
    }
    fn encode_decode(&self, target: V) -> V {
        self.remap_to(target, self)
    }
    fn remap_to(&self, target: V, destination: &Self) -> V {
        if self.alpha == 0.
            || self.beta == 0.
            || target == [0.; 3]
            || (0..3).all(|i| (target[i] - self.normal[i]).abs() < 1e-4)
        {
            return destination.normal;
        }
        let cosine = dot(target, self.normal);
        let alpha = acos(cosine);
        let projection = unit(sub(target, mul(self.normal, cosine)));
        let beta = if dot(projection, self.reference) >= 0.9999 {
            0.
        } else {
            let angle = acos(dot(projection, self.reference));
            if dot(projection, self.tangent) < 0. {
                std::f32::consts::TAU - angle
            } else {
                angle
            }
        };
        let snap = |angle: f32, bound: f32, new_bound: f32| {
            let ratio = if angle <= bound {
                angle / bound
            } else {
                -(std::f32::consts::TAU - angle) / (std::f32::consts::TAU - bound)
            };
            let code = (ratio * 32767. + 0.5).floor();
            code / 32767.
                * if code > 0. {
                    new_bound
                } else {
                    std::f32::consts::TAU - new_bound
                }
        };
        let alpha = snap(alpha, self.alpha, destination.alpha);
        let beta = snap(beta, self.beta, destination.beta);
        let base = mul(destination.normal, alpha.cos());
        let first = mul(destination.reference, alpha.sin() * beta.cos());
        let second = mul(destination.tangent, alpha.sin() * beta.sin());
        add(add(base, first), second)
    }
}

/// Reuse the float32 normal codec for flat polygon corners produced by SUBSURF.
pub(crate) fn quantize_corner(points: &[[f32; 3]], corner: usize, target: [f32; 3]) -> [f32; 3] {
    corner_frame(points, corner).encode_decode(target)
}
pub(crate) fn remap_corner(
    original: &[[f32; 3]],
    points: &[[f32; 3]],
    corner: usize,
    target: [f32; 3],
) -> [f32; 3] {
    corner_frame(original, corner).remap_to(target, &corner_frame(points, corner))
}
fn corner_frame(points: &[[f32; 3]], corner: usize) -> Frame {
    let mut normal = [0.; 3];
    for i in 0..points.len() {
        let a = points[(i + points.len() - 1) % points.len()];
        let b = points[i];
        for k in 0..3 {
            normal[k] += (a[(k + 1) % 3] - b[(k + 1) % 3]) * (a[(k + 2) % 3] + b[(k + 2) % 3]);
        }
    }
    let normal = unit_reciprocal(normal);
    let p = points[corner];
    let forward = unit(sub(points[(corner + 1) % points.len()], p));
    let backward = unit(sub(points[(corner + points.len() - 1) % points.len()], p));
    Frame::new(normal, forward, backward, &[forward, backward])
}

pub fn apply(object: &Value, mesh: &Value, modifier: &Value) -> Result<Value, String> {
    let vertices: Vec<V> = mesh["vertices"]
        .as_array()
        .unwrap()
        .iter()
        .map(|v| std::array::from_fn(|i| num(&v[i]) as f32))
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
    let count: usize = faces.iter().map(Vec::len).sum();
    if vertices.len() > 1_000_000 || count > 2_000_000 {
        return Err(
            "WEIGHTED_NORMAL is limited to one million vertices and two million corners".into(),
        );
    }
    if count == 0 {
        return Ok(mesh.clone());
    }
    let mut normals = Vec::with_capacity(faces.len());
    let mut areas = Vec::with_capacity(faces.len());
    let mut owner = Vec::with_capacity(count);
    let mut vertex = Vec::with_capacity(count);
    let mut next = Vec::with_capacity(count);
    let mut prev = Vec::with_capacity(count);
    let mut angles = Vec::with_capacity(count);
    let mut weight_angles = Vec::with_capacity(count);
    for (fi, face) in faces.iter().enumerate() {
        let mut normal = [0.; 3];
        for i in 0..face.len() {
            let a = vertices[face[(i + face.len() - 1) % face.len()]];
            let b = vertices[face[i]];
            for axis in 0..3 {
                normal[axis] += (a[(axis + 1) % 3] - b[(axis + 1) % 3])
                    * (a[(axis + 2) % 3] + b[(axis + 2) % 3]);
            }
        }
        let area_vector = if face.len() == 3 {
            cross(
                sub(vertices[face[1]], vertices[face[0]]),
                sub(vertices[face[2]], vertices[face[0]]),
            )
        } else {
            normal
        };
        let area = dot(area_vector, area_vector).sqrt() * 0.5;
        normal = unit_reciprocal(normal);
        if normal == [0.; 3] {
            normal = [0., 0., 1.];
        }
        if !area.is_finite() || normal.iter().any(|v| !v.is_finite()) {
            return Err("WEIGHTED_NORMAL geometry exceeds finite float32 normal arithmetic".into());
        }
        normals.push(normal);
        areas.push(area);
        let start = vertex.len();
        for (i, &vi) in face.iter().enumerate() {
            owner.push(fi);
            vertex.push(vi);
            next.push(start + (i + 1) % face.len());
            prev.push(start + (i + face.len() - 1) % face.len());
            let u = unit(sub(vertices[face[(i + 1) % face.len()]], vertices[vi]));
            let w = unit(sub(
                vertices[face[(i + face.len() - 1) % face.len()]],
                vertices[vi],
            ));
            angles.push(acos(dot(u, w)));
            let incoming = unit_reciprocal(sub(
                vertices[face[(i + face.len() - 1) % face.len()]],
                vertices[vi],
            ));
            let outgoing = unit_reciprocal(sub(vertices[vi], vertices[face[(i + 1) % face.len()]]));
            // Chord length avoids the loss of precision of acos near parallel
            // edges. Weighting uses the interior supplement of the turn angle.
            let opposite = dot(incoming, outgoing) < 0.;
            let chord = if opposite {
                add(incoming, outgoing)
            } else {
                sub(incoming, outgoing)
            };
            let half = (0.5 * dot(chord, chord).sqrt()).min(1.);
            let acute = 2. * half.asin();
            let turn = if opposite {
                std::f32::consts::PI - acute
            } else {
                acute
            };
            weight_angles.push(std::f32::consts::PI - turn);
        }
    }
    let mut edges = BTreeMap::<(usize, usize), Vec<usize>>::new();
    for corner in 0..count {
        let (a, b) = (vertex[corner], vertex[next[corner]]);
        edges.entry((a.min(b), a.max(b))).or_default().push(corner);
    }
    let mut parents: Vec<_> = (0..count).collect();
    let mut next_neighbor = vec![None; count];
    let mut prev_neighbor = vec![None; count];
    for adjacent in edges.values() {
        if adjacent.len() != 2 {
            continue;
        }
        let (a, b) = (adjacent[0], adjacent[1]);
        if mesh["smooth"][owner[a]] != true
            || mesh["smooth"][owner[b]] != true
            || vertex[a] != vertex[next[b]]
            || vertex[b] != vertex[next[a]]
        {
            continue;
        }
        for (left, right) in [(a, next[b]), (b, next[a])] {
            next_neighbor[left] = Some(right);
            prev_neighbor[right] = Some(left);
            let l = root(&mut parents, left);
            let r = root(&mut parents, right);
            parents[l] = r;
        }
    }
    let mut fans = BTreeMap::<usize, Vec<usize>>::new();
    for corner in 0..count {
        fans.entry(root(&mut parents, corner))
            .or_default()
            .push(corner);
    }
    let weights: Vec<_> = (0..count)
        .map(|c| match text(&modifier["mode"]) {
            "CORNER_ANGLE" => weight_angles[c],
            "FACE_AREA_WITH_ANGLE" => areas[owner[c]] * weight_angles[c],
            _ => areas[owner[c]],
        })
        .collect();
    if weights.iter().any(|v| !v.is_finite()) {
        return Err("WEIGHTED_NORMAL weights exceed finite float32 arithmetic".into());
    }
    let group = object["vertex_groups"]
        .as_array()
        .and_then(|g| g.iter().position(|g| g["name"] == modifier["vertex_group"]));
    let memberships = super::groups::weights(mesh);
    let masked = group.is_some() && mesh.get("deform_weights").is_some();
    let selected = |vi: usize| {
        !masked
            || (memberships[vi].iter().any(|(g, _)| Some(*g) == group)
                != (modifier["invert_vertex_group"] == true))
    };
    let value = num(&modifier["weight"]) as f32;
    let mut bias = value / 50.;
    if value == 100. {
        bias = 32767.;
    } else if value == 1. {
        bias = 1. / 32767.;
    } else if (bias - 1.) * 25. > 1. {
        bias = (bias - 1.) * 25.;
    }
    let threshold = num(&modifier["thresh"]) as f32;
    let strength = mesh["face_strength"]
        .as_array()
        .filter(|_| modifier["use_face_influence"] == true);
    let aggregate = |corners: &[usize]| -> Result<V, String> {
        let max_strength = strength.map(|values| {
            corners
                .iter()
                .map(|&c| values[owner[c]].as_i64().unwrap())
                .max()
                .unwrap_or(0)
        });
        let mut sorted = corners.to_vec();
        sorted.sort_by(|&a, &b| weights[b].total_cmp(&weights[a]));
        let mut previous = 0.;
        let mut rank = 0;
        let mut sum = [0.; 3];
        for c in sorted {
            if !selected(vertex[c])
                || strength.is_some_and(|v| v[owner[c]].as_i64() != max_strength)
            {
                continue;
            }
            let weight = weights[c];
            if previous == 0. {
                previous = weight;
            }
            if (previous - weight).abs() > threshold {
                rank += 1;
                previous = weight;
            }
            let inverse = 1. / bias.powf(rank as f32);
            sum = add(sum, mul(normals[owner[c]], weight * inverse));
        }
        weighted_unit(sum)
    };
    let mut per_vertex = vec![vec![]; vertices.len()];
    for c in 0..count {
        per_vertex[vertex[c]].push(c);
    }
    let targets: Vec<_> = per_vertex
        .iter()
        .map(|corners| aggregate(corners))
        .collect::<Result<_, _>>()?;
    let mut output = vec![[0.; 3]; count];
    for fan in fans.values() {
        let start = fan
            .iter()
            .copied()
            .find(|&c| next_neighbor[c].is_none())
            .unwrap_or(fan[0]);
        let vi = vertex[start];
        let custom = mesh["loop_normals"].as_array().unwrap();
        if !custom.is_empty()
            && fan.iter().any(|&c| {
                (0..3).any(|i| (num(&custom[c][i]) - num(&custom[start][i])).abs() > 1e-5)
            })
        {
            return Err(
                "WEIGHTED_NORMAL custom normals require consistent values within each smooth fan"
                    .into(),
            );
        }

        let reference = unit(sub(vertices[vertex[next[start]]], vertices[vi]));
        let mut boundary = vec![reference];
        let mut other;
        let mut automatic = [0.; 3];
        let mut c = start;
        let mut visited = Vec::with_capacity(fan.len());
        loop {
            visited.push(c);
            automatic = add(automatic, mul(normals[owner[c]], angles[c]));
            other = unit(sub(vertices[vertex[prev[c]]], vertices[vi]));
            if prev_neighbor[c] != Some(start) {
                boundary.push(other);
            }
            match prev_neighbor[c] {
                Some(neighbor) if neighbor != start && visited.len() < fan.len() => c = neighbor,
                _ => break,
            }
        }
        if visited.len() != fan.len() {
            return Err("WEIGHTED_NORMAL encountered an ambiguous smoothing fan".into());
        }
        automatic = if fan.len() == 1 {
            normals[owner[start]]
        } else {
            unit(automatic)
        };
        let frame = Frame::new(automatic, reference, other, &boundary);
        let mut target = if modifier["keep_sharp"] == true {
            aggregate(fan)?
        } else {
            targets[vi]
        };
        if target == [0.; 3] {
            let custom = mesh["loop_normals"].as_array().unwrap();
            target = if !custom.is_empty() && (masked || modifier["keep_sharp"] == true) {
                let first: V = std::array::from_fn(|i| num(&custom[start][i]) as f32);
                if fan
                    .iter()
                    .any(|&c| (0..3).any(|i| (num(&custom[c][i]) as f32 - first[i]).abs() > 1e-5))
                {
                    return Err("WEIGHTED_NORMAL retained custom normals require consistent values within each smooth fan".into());
                }
                frame.encode_decode(first)
            } else if !masked && modifier["keep_sharp"] != true {
                let mut sum = [0.; 3];
                for &c in &per_vertex[vi] {
                    sum = add(sum, mul(normals[owner[c]], angles[c]));
                }
                let normal = unit(sum);
                if normal == [0.; 3] { automatic } else { normal }
            } else {
                automatic
            };
        }
        // The custom-normal representation averages repeated corner inputs in
        // float32 even when every corner starts with the same vertex normal.
        let target = if fan.len() > 1 {
            let mut sum = [0.; 3];
            for _ in fan {
                sum = add(sum, target);
            }
            mul(sum, 1. / fan.len() as f32)
        } else {
            target
        };
        let normal = frame.encode_decode(target);
        if normal.iter().any(|v| !v.is_finite()) {
            return Err("WEIGHTED_NORMAL normal-space arithmetic is not finite".into());
        }
        for &corner in fan {
            output[corner] = normal;
        }
    }
    let mut result = mesh.clone();
    result["loop_normals"] = json!(output);
    Ok(result)
}
