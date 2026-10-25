//! Deterministic polygon triangulation for editable topology and modifiers.
use super::math::{V3, cross, dot, length, normalize, sub};
use std::collections::BTreeMap;

pub fn polygon(points: &[V3], quad: &str, ngon: &str) -> Result<Vec<[usize; 3]>, String> {
    if !(3..=2048).contains(&points.len()) || points.iter().flatten().any(|x| !x.is_finite()) {
        return Err("Triangulation requires 3..2048 finite polygon vertices".into());
    }
    if !["BEAUTY", "FIXED", "ALTERNATE", "SHORT_EDGE", "LONG_EDGE"].contains(&quad)
        || !["BEAUTY", "EAR_CLIP"].contains(&ngon)
    {
        return Err("Unknown triangulation method".into());
    }
    if points.len() == 3 {
        return Ok(vec![[0, 1, 2]]);
    }
    let normal = super::geometry::face_normal(points);
    let extent = points
        .iter()
        .map(|p| length(sub(*p, points[0])))
        .fold(0., f64::max);
    if length(normal) < 0.5
        || points
            .iter()
            .any(|p| dot(sub(*p, points[0]), normal).abs() > extent.max(1.) * 1e-6)
    {
        return Err("Triangulation requires nondegenerate planar polygons".into());
    }
    let u = normalize(sub(points[1], points[0]));
    let v = cross(normal, u);
    let xy: Vec<_> = points
        .iter()
        .map(|p| {
            let d = sub(*p, points[0]);
            [dot(d, u), dot(d, v)]
        })
        .collect();
    let turn = |a: usize, b: usize, c: usize| {
        (xy[b][0] - xy[a][0]) * (xy[c][1] - xy[a][1])
            - (xy[b][1] - xy[a][1]) * (xy[c][0] - xy[a][0])
    };
    let epsilon = extent * extent * 1e-12;
    for i in 0..points.len() {
        let j = (i + 1) % points.len();
        if length(sub(points[i], points[j])) < extent * 1e-12 {
            return Err("Triangulation has a zero-length boundary edge".into());
        }
        for k in i + 1..points.len() {
            let l = (k + 1) % points.len();
            if i == l || j == k {
                continue;
            }
            if turn(i, j, k) * turn(i, j, l) < 0. && turn(k, l, i) * turn(k, l, j) < 0. {
                return Err("Triangulation requires a simple polygon boundary".into());
            }
        }
    }
    let score = |tri: [usize; 3]| {
        let area = turn(tri[0], tri[1], tri[2]);
        if area <= epsilon {
            return f64::NEG_INFINITY;
        }
        let perimeter = (0..3)
            .map(|i| length(sub(points[tri[i]], points[tri[(i + 1) % 3]])))
            .sum::<f64>();
        area / perimeter
    };
    if points.len() == 4 {
        let primary = [[0, 2, 3], [0, 1, 2]];
        let alternate = [[1, 3, 0], [1, 2, 3]];
        let fixed = match quad {
            "FIXED" => true,
            "ALTERNATE" => false,
            "SHORT_EDGE" => length(sub(points[0], points[2])) < length(sub(points[1], points[3])),
            "LONG_EDGE" => length(sub(points[0], points[2])) > length(sub(points[1], points[3])),
            _ => {
                primary.iter().map(|t| score(*t)).sum::<f64>()
                    > alternate.iter().map(|t| score(*t)).sum::<f64>()
            }
        };
        return Ok(if fixed {
            primary.to_vec()
        } else {
            alternate.to_vec()
        });
    }
    let mut ring: Vec<_> = (0..points.len()).collect();
    let mut triangles = vec![];
    let mut cursor = 0;
    let mut reverse = false;
    while ring.len() > 3 {
        let convex = |position: usize, ring: &[usize]| {
            turn(
                ring[(position + ring.len() - 1) % ring.len()],
                ring[position],
                ring[(position + 1) % ring.len()],
            ) > epsilon
        };
        let count = ring.len();
        let position = (0..count)
            .map(|step| {
                if reverse {
                    (cursor + count - step) % count
                } else {
                    (cursor + step) % count
                }
            })
            .find(|&i| {
                let a = ring[(i + count - 1) % count];
                let b = ring[i];
                let c = ring[(i + 1) % count];
                convex(i, &ring)
                    && !ring.iter().any(|&p| {
                        p != a
                            && p != b
                            && p != c
                            && turn(a, b, p) >= -epsilon
                            && turn(b, c, p) >= -epsilon
                            && turn(c, a, p) >= -epsilon
                    })
            })
            .ok_or("Cannot triangulate a degenerate polygon")?;
        triangles.push([
            ring[(position + count - 1) % count],
            ring[position],
            ring[(position + 1) % count],
        ]);
        ring.remove(position);
        let count = ring.len();
        cursor = if reverse {
            (position + count - 2) % count
        } else {
            (position + 1) % count
        };
        if !convex(cursor, &ring) {
            cursor = if reverse {
                (cursor + count - 1) % count
            } else {
                (cursor + 1) % count
            };
            reverse = !reverse;
        }
    }
    triangles.push([ring[0], ring[1], ring[2]]);
    if ngon == "BEAUTY" {
        // Flip the best improving diagonal until the triangulation is locally stable.
        for _ in 0..points.len() * points.len() {
            let mut edges: BTreeMap<_, Vec<_>> = BTreeMap::new();
            for (i, t) in triangles.iter().enumerate() {
                for j in 0..3 {
                    let a = t[j];
                    let b = t[(j + 1) % 3];
                    edges
                        .entry((a.min(b), a.max(b)))
                        .or_default()
                        .push((i, a, b, t[(j + 2) % 3]));
                }
            }
            let mut best = None;
            let mut gain_best = 0.;
            for uses in edges.values().filter(|u| u.len() == 2) {
                let (i, a, b, c) = uses[0];
                let (j, bb, aa, d) = uses[1];
                if a != aa || b != bb || c == d {
                    continue;
                }
                let t1 = [c, a, d];
                let t2 = [c, d, b];
                let gain = score(t1) + score(t2) - score(triangles[i]) - score(triangles[j]);
                let area = (turn(c, a, b).abs() + turn(d, b, a).abs()) * 0.5;
                if gain > 1e-6 * area.max(1.) && gain > gain_best {
                    best = Some((i, j, t1, t2));
                    gain_best = gain;
                }
            }
            if let Some((i, j, a, b)) = best {
                triangles[i] = a;
                triangles[j] = b;
            } else {
                break;
            }
        }
    }
    // Blender keeps the final triangle in the original face slot.
    triangles.rotate_right(1);
    Ok(triangles)
}
