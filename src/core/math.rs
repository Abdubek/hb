#![allow(clippy::needless_range_loop)] // Fixed-size vector/matrix indexing.
pub type V3 = [f64; 3];
pub type M4 = [[f64; 4]; 4];
pub const IDENTITY: M4 = [
    [1., 0., 0., 0.],
    [0., 1., 0., 0.],
    [0., 0., 1., 0.],
    [0., 0., 0., 1.],
];
pub fn add(a: V3, b: V3) -> V3 {
    std::array::from_fn(|i| a[i] + b[i])
}
pub fn sub(a: V3, b: V3) -> V3 {
    std::array::from_fn(|i| a[i] - b[i])
}
pub fn mul(a: V3, s: f64) -> V3 {
    a.map(|x| x * s)
}
pub fn dot(a: V3, b: V3) -> f64 {
    a.iter().zip(b).map(|(a, b)| a * b).sum()
}
pub fn cross(a: V3, b: V3) -> V3 {
    [
        a[1] * b[2] - a[2] * b[1],
        a[2] * b[0] - a[0] * b[2],
        a[0] * b[1] - a[1] * b[0],
    ]
}
pub fn length(a: V3) -> f64 {
    dot(a, a).sqrt()
}
pub fn normalize(a: V3) -> V3 {
    let n = length(a);
    if n > 1e-30 { mul(a, 1. / n) } else { [0.; 3] }
}
pub fn matmul(a: M4, b: M4) -> M4 {
    std::array::from_fn(|i| std::array::from_fn(|j| (0..4).map(|k| a[i][k] * b[k][j]).sum()))
}
pub fn point(m: M4, v: V3) -> V3 {
    std::array::from_fn(|i| m[i][3] + (0..3).map(|j| m[i][j] * v[j]).sum::<f64>())
}
pub fn direction(m: M4, v: V3) -> V3 {
    std::array::from_fn(|i| (0..3).map(|j| m[i][j] * v[j]).sum::<f64>())
}
pub fn inverse(m: M4) -> Result<M4, String> {
    let mut a: [[f64; 8]; 4] = std::array::from_fn(|i| {
        std::array::from_fn(|j| {
            if j < 4 {
                m[i][j]
            } else {
                if i == j - 4 { 1. } else { 0. }
            }
        })
    });
    for col in 0..4 {
        let pivot = (col..4)
            .max_by(|&i, &j| a[i][col].abs().total_cmp(&a[j][col].abs()))
            .unwrap();
        if a[pivot][col].abs() < 1e-14 {
            return Err("Singular transform cannot be inverted".into());
        }
        a.swap(col, pivot);
        let div = a[col][col];
        for j in 0..8 {
            a[col][j] /= div;
        }
        for i in 0..4 {
            if i != col {
                let k = a[i][col];
                for j in 0..8 {
                    a[i][j] -= k * a[col][j];
                }
            }
        }
    }
    Ok(std::array::from_fn(|i| {
        std::array::from_fn(|j| a[i][j + 4])
    }))
}

/// Blender's glTF exporter decomposes parent-compensated local matrices to TRS.
/// This removes shear while scene evaluation retains the original affine matrix.
pub fn decompose_affine(m: M4) -> (V3, [f64; 4], V3) {
    let mut scale: V3 = std::array::from_fn(|j| length([m[0][j], m[1][j], m[2][j]]));
    if dot(
        cross([m[0][0], m[1][0], m[2][0]], [m[0][1], m[1][1], m[2][1]]),
        [m[0][2], m[1][2], m[2][2]],
    ) < 0.
    {
        scale = scale.map(|s| -s);
    }
    let r: [[f64; 3]; 3] = std::array::from_fn(|i| {
        std::array::from_fn(|j| {
            if scale[j].abs() > 1e-30 {
                m[i][j] / scale[j]
            } else {
                0.
            }
        })
    });
    let mut q = [1., 0., 0., 0.];
    let trace = r[0][0] + r[1][1] + r[2][2];
    if r.iter().flatten().any(|v| *v != 0.) {
        if trace > 0. {
            let s = 2. * (trace + 1.).sqrt();
            q = [
                s / 4.,
                (r[2][1] - r[1][2]) / s,
                (r[0][2] - r[2][0]) / s,
                (r[1][0] - r[0][1]) / s,
            ];
        } else {
            let i = (0..3).max_by(|&a, &b| r[a][a].total_cmp(&r[b][b])).unwrap();
            let j = (i + 1) % 3;
            let k = (i + 2) % 3;
            let s = 2. * (1. + r[i][i] - r[j][j] - r[k][k]).max(0.).sqrt();
            if s != 0. {
                q[0] = (r[k][j] - r[j][k]) / s;
                q[i + 1] = s / 4.;
                q[j + 1] = (r[i][j] + r[j][i]) / s;
                q[k + 1] = (r[i][k] + r[k][i]) / s;
            }
        }
    }
    let norm = q.iter().map(|x| x * x).sum::<f64>().sqrt();
    (
        point(m, [0.; 3]),
        [q[1] / norm, q[2] / norm, q[3] / norm, q[0] / norm],
        scale,
    )
}
pub fn without_shear(m: M4) -> M4 {
    let (translation, rotation, scale) = decompose_affine(m);
    let mut result = quat(rotation);
    for i in 0..3 {
        for j in 0..3 {
            result[i][j] *= scale[j];
        }
        result[i][3] = translation[i];
    }
    result
}
pub fn normal(m: M4, n: V3) -> V3 {
    match inverse(m) {
        Ok(inv) => normalize(std::array::from_fn(|i| {
            (0..3).map(|j| inv[j][i] * n[j]).sum()
        })),
        Err(_) => normalize(direction(m, n)),
    }
}
pub fn trs(t: V3, r: V3, s: V3) -> M4 {
    let (sx, cx) = r[0].sin_cos();
    let (sy, cy) = r[1].sin_cos();
    let (sz, cz) = r[2].sin_cos();
    let mut m = IDENTITY;
    let rot = [
        [cy * cz, cz * sx * sy - cx * sz, sx * sz + cx * cz * sy],
        [cy * sz, cx * cz + sx * sy * sz, cx * sy * sz - cz * sx],
        [-sy, cy * sx, cx * cy],
    ];
    for i in 0..3 {
        for j in 0..3 {
            m[i][j] = rot[i][j] * s[j];
        }
        m[i][3] = t[i];
    }
    m
}
pub fn trs_order(t: V3, r: V3, s: V3, order: &str) -> M4 {
    let axes = match order {
        "XZY" => [0, 2, 1],
        "YXZ" => [1, 0, 2],
        "YZX" => [1, 2, 0],
        "ZXY" => [2, 0, 1],
        "ZYX" => [2, 1, 0],
        _ => return trs(t, r, s),
    };
    let mut m = IDENTITY;
    for axis in axes {
        let a = (axis + 1) % 3;
        let b = (axis + 2) % 3;
        let (sin, cos) = r[axis].sin_cos();
        let mut turn = IDENTITY;
        turn[a][a] = cos;
        turn[b][b] = cos;
        turn[a][b] = -sin;
        turn[b][a] = sin;
        m = matmul(turn, m);
    }
    for i in 0..3 {
        for (j, scale) in s.iter().enumerate() {
            m[i][j] *= scale;
        }
        m[i][3] = t[i];
    }
    m
}
pub fn quat(q: [f64; 4]) -> M4 {
    let [x, y, z, w] = q;
    [
        [
            1. - 2. * (y * y + z * z),
            2. * (x * y - z * w),
            2. * (x * z + y * w),
            0.,
        ],
        [
            2. * (x * y + z * w),
            1. - 2. * (x * x + z * z),
            2. * (y * z - x * w),
            0.,
        ],
        [
            2. * (x * z - y * w),
            2. * (y * z + x * w),
            1. - 2. * (x * x + y * y),
            0.,
        ],
        [0., 0., 0., 1.],
    ]
}
pub const Z_TO_Y: M4 = [
    [1., 0., 0., 0.],
    [0., 0., 1., 0.],
    [0., -1., 0., 0.],
    [0., 0., 0., 1.],
];
pub const Y_TO_Z: M4 = [
    [1., 0., 0., 0.],
    [0., 0., -1., 0.],
    [0., 1., 0., 0.],
    [0., 0., 0., 1.],
];
pub fn look_at(eye: V3, target: V3, up: V3) -> M4 {
    let z = normalize(sub(eye, target));
    let mut x = normalize(cross(up, z));
    if length(x) < 1e-9 {
        x = [1., 0., 0.];
    }
    let y = cross(z, x);
    [
        [x[0], y[0], z[0], eye[0]],
        [x[1], y[1], z[1], eye[1]],
        [x[2], y[2], z[2], eye[2]],
        [0., 0., 0., 1.],
    ]
}
pub fn from_flat(v: &[f64]) -> Result<M4, String> {
    if v.len() != 16 {
        return Err("Matrix must have 16 components".into());
    }
    Ok(std::array::from_fn(|i| {
        std::array::from_fn(|j| v[j * 4 + i])
    }))
}
pub fn flat(m: M4) -> Vec<f64> {
    (0..16).map(|i| m[i % 4][i / 4]).collect()
}
