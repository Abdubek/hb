//! Corner-space remapping for flat TRIANGULATE faces without normal preservation.
use super::{
    geometry,
    math::{V3, add, cross, dot, mul, normalize, sub},
};
use std::f64::consts::{FRAC_PI_2, TAU};
struct Space {
    normal: V3,
    reference: V3,
    tangent: V3,
    beta: f64,
}
fn space(points: &[V3], corner: usize) -> Space {
    let normal = geometry::face_normal(points);
    let reference = normalize(sub(points[(corner + 1) % points.len()], points[corner]));
    let other = normalize(sub(
        points[(corner + points.len() - 1) % points.len()],
        points[corner],
    ));
    let tangent = normalize(cross(normal, reference));
    let beta = dot(tangent, other)
        .atan2(dot(reference, other))
        .rem_euclid(TAU);
    Space {
        normal,
        reference,
        tangent,
        beta: if beta < 1e-8 { TAU } else { beta },
    }
}
fn encode(angle: f64, reference: f64) -> f64 {
    let factor = if angle <= reference {
        angle / reference
    } else {
        -(TAU - angle) / (TAU - reference)
    };
    (factor * 32767. + 0.5).floor() / 32767.
}
fn decode(factor: f64, reference: f64) -> f64 {
    factor
        * if factor > 0. {
            reference
        } else {
            TAU - reference
        }
}
pub fn remap(
    original: &[V3],
    original_corner: usize,
    triangle: &[V3],
    corner: usize,
    custom: V3,
) -> V3 {
    let old = space(original, original_corner);
    let new = space(triangle, corner);
    if custom
        .iter()
        .zip(old.normal)
        .all(|(a, b)| (*a - b).abs() < 1e-4)
    {
        return new.normal;
    }
    let alpha = dot(old.normal, custom).clamp(-1., 1.).acos();
    let beta = dot(old.tangent, custom)
        .atan2(dot(old.reference, custom))
        .rem_euclid(TAU);
    let alpha = decode(encode(alpha, FRAC_PI_2), FRAC_PI_2);
    let beta = decode(encode(beta, old.beta), new.beta);
    normalize(add(
        mul(new.normal, alpha.cos()),
        mul(
            add(mul(new.reference, beta.cos()), mul(new.tangent, beta.sin())),
            alpha.sin(),
        ),
    ))
}
