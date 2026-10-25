#![allow(clippy::needless_range_loop)] // Fixed-size vector/matrix indexing.
use super::{
    Scene, Value, id,
    math::{self, V3, add, cross, dot, length, mul, normalize, sub},
    num, text, vec3,
};
use serde_json::json;
use std::collections::BTreeMap;
#[derive(Clone, Copy, Debug)]
pub struct Bounds {
    pub min: V3,
    pub max: V3,
}
impl Bounds {
    pub fn empty() -> Self {
        Self {
            min: [f64::INFINITY; 3],
            max: [f64::NEG_INFINITY; 3],
        }
    }
    pub fn include(&mut self, p: V3) {
        for i in 0..3 {
            self.min[i] = self.min[i].min(p[i]);
            self.max[i] = self.max[i].max(p[i]);
        }
    }
    pub fn union(mut self, b: Self) -> Self {
        self.include(b.min);
        self.include(b.max);
        self
    }
    pub fn center(self) -> V3 {
        mul(add(self.min, self.max), 0.5)
    }
    pub fn extent(self) -> V3 {
        sub(self.max, self.min)
    }
    pub fn distance(self, b: Self) -> f64 {
        (0..3)
            .map(|i| {
                (self.min[i] - b.max[i])
                    .max(b.min[i] - self.max[i])
                    .max(0.)
                    .powi(2)
            })
            .sum::<f64>()
            .sqrt()
    }
    pub fn value(self) -> Value {
        if self.min[0].is_finite() {
            json!({"min":self.min,"max":self.max,"center":self.center(),"dimensions":self.extent()})
        } else {
            Value::Null
        }
    }
}
#[derive(Clone)]
pub struct Triangle {
    pub p: [V3; 3],
    pub vertex_indices: [usize; 3],
    pub loop_indices: [usize; 3],
    pub n: [V3; 3],
    pub uv: [[f64; 2]; 3],
    pub colors: [[f64; 4]; 3],
    pub material: Option<u64>,
    pub material_slot: usize,
    pub bounds: Bounds,
}
#[derive(Clone)]
pub struct ObjectGeometry {
    pub id: u64,
    pub name: String,
    pub bounds: Bounds,
    pub triangles: Vec<usize>,
    pub vertices: Vec<V3>,
}
pub struct Geometry {
    pub triangles: Vec<Triangle>,
    pub objects: Vec<ObjectGeometry>,
    pub bounds: Bounds,
}
pub(crate) fn face_normal(p: &[V3]) -> V3 {
    let mut n = [0.; 3];
    let origin = p.first().copied().unwrap_or([0.; 3]);
    for i in 0..p.len() {
        n = add(
            n,
            cross(sub(p[i], origin), sub(p[(i + 1) % p.len()], origin)),
        );
    }
    normalize(n)
}
/// Ear clipping keeps concave n-gons intact instead of silently drawing a fan.
pub fn triangulate(points: &[V3]) -> Result<Vec<[usize; 3]>, String> {
    if points.len() < 3 {
        return Ok(vec![]);
    }
    if points.len() == 3 {
        return Ok(vec![[0, 1, 2]]);
    }
    let normal = face_normal(points);
    let axis = (0..3)
        .max_by(|&a, &b| normal[a].abs().total_cmp(&normal[b].abs()))
        .unwrap();
    let axes: Vec<_> = (0..3).filter(|i| *i != axis).collect();
    let xy: Vec<[f64; 2]> = points.iter().map(|p| [p[axes[0]], p[axes[1]]]).collect();
    let turn = |a: usize, b: usize, c: usize| {
        (xy[b][0] - xy[a][0]) * (xy[c][1] - xy[a][1])
            - (xy[b][1] - xy[a][1]) * (xy[c][0] - xy[a][0])
    };
    let area: f64 = (0..xy.len())
        .map(|i| xy[i][0] * xy[(i + 1) % xy.len()][1] - xy[(i + 1) % xy.len()][0] * xy[i][1])
        .sum();
    if area.abs() < 1e-20 {
        return Ok((1..points.len() - 1).map(|i| [0, i, i + 1]).collect());
    }
    let sign = area.signum();
    let mut indices: Vec<_> = (0..points.len()).collect();
    let mut out = vec![];
    while indices.len() > 3 {
        let mut found = false;
        for i in 0..indices.len() {
            let a = indices[(i + indices.len() - 1) % indices.len()];
            let b = indices[i];
            let c = indices[(i + 1) % indices.len()];
            if turn(a, b, c) * sign <= 1e-16 {
                continue;
            }
            if indices.iter().any(|&p| {
                p != a
                    && p != b
                    && p != c
                    && turn(a, b, p) * sign >= -1e-14
                    && turn(b, c, p) * sign >= -1e-14
                    && turn(c, a, p) * sign >= -1e-14
            }) {
                continue;
            }
            out.push([a, b, c]);
            indices.remove(i);
            found = true;
            break;
        }
        if !found {
            return Err("Cannot triangulate a self-intersecting or degenerate polygon".into());
        }
    }
    out.push([indices[0], indices[1], indices[2]]);
    Ok(out)
}
impl Geometry {
    pub fn new(scene: &Scene, render_only: bool) -> Result<Self, String> {
        let mut g = Self {
            triangles: vec![],
            objects: vec![],
            bounds: Bounds::empty(),
        };
        for key in scene.linked_ids() {
            let o = scene.object(key)?;
            if render_only && o["hide_render"] == true {
                continue;
            }
            let Some(m) = super::modeling::evaluated_mesh(scene, o, render_only)? else {
                continue;
            };
            let world = scene.world(key)?;
            let vertices: Vec<_> = m["vertices"].as_array().unwrap().iter().map(vec3).collect();
            let faces = m["faces"].as_array().unwrap();
            let uv =
                m["uv_layers"][m["active_uv"].as_u64().unwrap_or(0) as usize]["data"].as_array();
            let custom = m["loop_normals"].as_array().filter(|a| !a.is_empty());
            let colors = m["colors"].as_array().filter(|a| !a.is_empty());
            let mut smooth = vec![[0.; 3]; vertices.len()];
            let mut normals = vec![];
            for face in faces {
                let p: Vec<_> = face
                    .as_array()
                    .unwrap()
                    .iter()
                    .map(|i| vertices[i.as_u64().unwrap() as usize])
                    .collect();
                let n = face_normal(&p);
                for i in face.as_array().unwrap() {
                    let k = i.as_u64().unwrap() as usize;
                    smooth[k] = add(smooth[k], n);
                }
                normals.push(n);
            }
            for n in &mut smooth {
                *n = normalize(*n);
            }
            let world_vertices: Vec<_> = vertices.iter().map(|p| math::point(world, *p)).collect();
            let mut object = ObjectGeometry {
                id: key,
                name: text(&o["name"]).into(),
                bounds: Bounds::empty(),
                triangles: vec![],
                vertices: world_vertices.clone(),
            };
            for p in &world_vertices {
                object.bounds.include(*p);
                g.bounds.include(*p);
            }
            let mut loop_start = 0;
            for (fi, face) in faces.iter().enumerate() {
                let indices: Vec<_> = face
                    .as_array()
                    .unwrap()
                    .iter()
                    .map(|i| i.as_u64().unwrap() as usize)
                    .collect();
                let pts: Vec<_> = indices.iter().map(|&i| vertices[i]).collect();
                let material_slot = m["material_indices"][fi].as_u64().unwrap_or(0) as usize;
                let material = m["materials"][material_slot].as_u64();
                for tri in triangulate(&pts)? {
                    let p = tri.map(|j| world_vertices[indices[j]]);
                    let n = tri.map(|j| {
                        let n = if let Some(ns) = custom {
                            vec3(&ns[loop_start + j])
                        } else if m["smooth"][fi] == true {
                            smooth[indices[j]]
                        } else {
                            normals[fi]
                        };
                        math::normal(world, n)
                    });
                    let uv = tri.map(|j| {
                        uv.and_then(|a| a.get(loop_start + j))
                            .map(|v| [num(&v[0]), num(&v[1])])
                            .unwrap_or([0.; 2])
                    });
                    let colors = tri.map(|j| {
                        colors
                            .and_then(|a| a.get(loop_start + j))
                            .map(super::vec4)
                            .unwrap_or([1.; 4])
                    });
                    let mut bounds = Bounds::empty();
                    for v in p {
                        bounds.include(v);
                    }
                    object.triangles.push(g.triangles.len());
                    g.triangles.push(Triangle {
                        vertex_indices: tri.map(|j| indices[j]),
                        loop_indices: tri.map(|j| loop_start + j),
                        p,
                        n,
                        uv,
                        colors,
                        material,
                        material_slot,
                        bounds,
                    });
                }
                loop_start += indices.len();
            }
            g.objects.push(object);
        }
        Ok(g)
    }
    pub fn object(&self, name: &str) -> Result<&ObjectGeometry, String> {
        self.objects
            .iter()
            .find(|o| o.name == name)
            .ok_or(format!("No linked mesh object named {name}"))
    }
}
pub fn ray_triangle(origin: V3, dir: V3, t: &Triangle) -> Option<f64> {
    let e1 = sub(t.p[1], t.p[0]);
    let e2 = sub(t.p[2], t.p[0]);
    let p = cross(dir, e2);
    let det = dot(e1, p);
    if det.abs() < 1e-12 {
        return None;
    }
    let inv = 1. / det;
    let s = sub(origin, t.p[0]);
    let u = dot(s, p) * inv;
    if !(-1e-9..=1. + 1e-9).contains(&u) {
        return None;
    }
    let q = cross(s, e1);
    let v = dot(dir, q) * inv;
    if v < -1e-9 || u + v > 1. + 1e-9 {
        return None;
    }
    let hit = dot(e2, q) * inv;
    (hit >= -1e-9).then_some(hit)
}
fn point_segment(p: V3, a: V3, b: V3) -> V3 {
    let d = sub(b, a);
    let n = dot(d, d);
    if n == 0. {
        a
    } else {
        add(a, mul(d, (dot(sub(p, a), d) / n).clamp(0., 1.)))
    }
}
pub fn point_triangle(p: V3, t: &Triangle) -> V3 {
    let [a, b, c] = t.p;
    let ab = sub(b, a);
    let ac = sub(c, a);
    let n = cross(ab, ac);
    let nn = dot(n, n);
    if nn > 1e-24 {
        let q = sub(p, mul(n, dot(sub(p, a), n) / nn));
        let v0 = sub(q, a);
        let d00 = dot(ab, ab);
        let d01 = dot(ab, ac);
        let d11 = dot(ac, ac);
        let d20 = dot(v0, ab);
        let d21 = dot(v0, ac);
        let d = d00 * d11 - d01 * d01;
        let u = (d11 * d20 - d01 * d21) / d;
        let v = (d00 * d21 - d01 * d20) / d;
        if u >= 0. && v >= 0. && u + v <= 1. {
            return q;
        }
    }
    [
        point_segment(p, a, b),
        point_segment(p, b, c),
        point_segment(p, c, a),
    ]
    .into_iter()
    .min_by(|a, b| length(sub(*a, p)).total_cmp(&length(sub(*b, p))))
    .unwrap()
}
fn segment_pair(a: V3, b: V3, c: V3, d: V3) -> (V3, V3) {
    let u = sub(b, a);
    let v = sub(d, c);
    let w = sub(a, c);
    let aa = dot(u, u);
    let bb = dot(u, v);
    let cc = dot(v, v);
    let dd = dot(u, w);
    let ee = dot(v, w);
    if aa < 1e-20 {
        return (a, point_segment(a, c, d));
    }
    if cc < 1e-20 {
        return (point_segment(c, a, b), c);
    }
    let den = aa * cc - bb * bb;
    let mut s = if den > 1e-20 {
        ((bb * ee - cc * dd) / den).clamp(0., 1.)
    } else {
        0.
    };
    let mut t = (bb * s + ee) / cc;
    if t < 0. {
        t = 0.;
        s = (-dd / aa).clamp(0., 1.);
    } else if t > 1. {
        t = 1.;
        s = ((bb - dd) / aa).clamp(0., 1.);
    }
    (add(a, mul(u, s)), add(c, mul(v, t)))
}
fn triangle_distance(a: &Triangle, b: &Triangle) -> (f64, V3, V3) {
    for t in [a, b] {
        let other = if std::ptr::eq(t, a) { b } else { a };
        for i in 0..3 {
            let d = sub(t.p[(i + 1) % 3], t.p[i]);
            if let Some(s) = ray_triangle(t.p[i], d, other)
                && s <= 1. + 1e-10
            {
                let p = add(t.p[i], mul(d, s));
                return (0., p, p);
            }
        }
    }
    let mut best = (f64::INFINITY, [0.; 3], [0.; 3]);
    let mut consider = |p: V3, q: V3| {
        let d = length(sub(p, q));
        if d < best.0 {
            best = (d, p, q);
        }
    };
    for p in a.p {
        consider(p, point_triangle(p, b));
    }
    for p in b.p {
        consider(point_triangle(p, a), p);
    }
    for i in 0..3 {
        for j in 0..3 {
            let (p, q) = segment_pair(a.p[i], a.p[(i + 1) % 3], b.p[j], b.p[(j + 1) % 3]);
            consider(p, q);
        }
    }
    best
}
struct Bvh {
    bounds: Bounds,
    left: Option<Box<Bvh>>,
    right: Option<Box<Bvh>>,
    indices: Vec<usize>,
}
impl Bvh {
    fn new(g: &Geometry, mut ids: Vec<usize>) -> Self {
        let bounds = ids
            .iter()
            .fold(Bounds::empty(), |a, &i| a.union(g.triangles[i].bounds));
        if ids.len() <= 8 {
            return Self {
                bounds,
                left: None,
                right: None,
                indices: ids,
            };
        }
        let e = bounds.extent();
        let axis = (0..3).max_by(|&a, &b| e[a].total_cmp(&e[b])).unwrap();
        ids.sort_by(|&a, &b| {
            g.triangles[a].bounds.center()[axis].total_cmp(&g.triangles[b].bounds.center()[axis])
        });
        let right = ids.split_off(ids.len() / 2);
        Self {
            bounds,
            left: Some(Box::new(Self::new(g, ids))),
            right: Some(Box::new(Self::new(g, right))),
            indices: vec![],
        }
    }
    fn pair(&self, other: &Self, g: &Geometry, best: &mut (f64, V3, V3)) {
        if self.bounds.distance(other.bounds) > best.0 {
            return;
        }
        match (&self.left, &other.left) {
            (None, None) => {
                for &a in &self.indices {
                    for &b in &other.indices {
                        if g.triangles[a].bounds.distance(g.triangles[b].bounds) <= best.0 {
                            let d = triangle_distance(&g.triangles[a], &g.triangles[b]);
                            if d.0 < best.0 {
                                *best = d;
                            }
                            if best.0 == 0. {
                                return;
                            }
                        }
                    }
                }
            }
            (Some(a), _) => {
                a.pair(other, g, best);
                self.right.as_ref().unwrap().pair(other, g, best);
            }
            (_, Some(a)) => {
                self.pair(a, g, best);
                self.pair(other.right.as_ref().unwrap(), g, best);
            }
        }
    }
}
pub fn distance(
    g: &Geometry,
    a: &ObjectGeometry,
    b: &ObjectGeometry,
) -> Result<(f64, V3, V3), String> {
    if a.triangles.is_empty() || b.triangles.is_empty() {
        return Err("Distance requires surface geometry on both objects".into());
    }
    let mut best = (f64::INFINITY, [0.; 3], [0.; 3]);
    Bvh::new(g, a.triangles.clone()).pair(&Bvh::new(g, b.triangles.clone()), g, &mut best);
    Ok(best)
}
fn inside_point(g: &Geometry, p: V3, b: &ObjectGeometry) -> bool {
    let dir = normalize([1., 0.371390676, 0.694746591]);
    let mut hits = vec![];
    for &i in &b.triangles {
        let t = &g.triangles[i];
        if length(sub(point_triangle(p, t), p)) < 1e-8 {
            return true;
        }
        if let Some(d) = ray_triangle(p, dir, t)
            && d > 1e-8
        {
            hits.push(d);
        }
    }
    hits.sort_by(f64::total_cmp);
    hits.dedup_by(|a, b| (*a - *b).abs() < 1e-8);
    hits.len() % 2 == 1
}
fn closed(g: &Geometry, b: &ObjectGeometry) -> bool {
    let mut edges = BTreeMap::new();
    for &i in &b.triangles {
        let t = &g.triangles[i];
        for j in 0..3 {
            let a = t.p[j].map(|v| if v == 0. { 0 } else { v.to_bits() });
            let b = t.p[(j + 1) % 3].map(|v| if v == 0. { 0 } else { v.to_bits() });
            *edges
                .entry(if a < b { (a, b) } else { (b, a) })
                .or_insert(0) += 1;
        }
    }
    !edges.is_empty() && edges.values().all(|n| *n == 2)
}
pub fn query(scene: &Scene, args: &[String]) -> Result<Value, String> {
    let op = args.first().map(String::as_str).unwrap_or("stats");
    match op{
"snapshot"=>return Ok(serde_json::to_value(scene).unwrap()),
"stats"=>return Ok(json!({"objects":scene.objects.len(),"linked_objects":scene.linked_ids().len(),"meshes":scene.meshes.len(),"vertices":scene.meshes.iter().map(|m|m["vertices"].as_array().unwrap().len()).sum::<usize>(),"faces":scene.meshes.iter().map(|m|m["faces"].as_array().unwrap().len()).sum::<usize>(),"triangles":scene.meshes.iter().flat_map(|m|m["faces"].as_array().unwrap()).map(|f|f.as_array().unwrap().len().saturating_sub(2)).sum::<usize>(),"materials":scene.materials.len(),"cameras":scene.cameras.len(),"lights":scene.lights.len(),"images":scene.images.len()})),
"tree"=>{fn branch(scene:&Scene,parent:Option<u64>)->Value{json!(scene.objects.iter().filter(|o|o["parent"].as_u64()==parent&&scene.is_linked(id(o))).map(|o|json!({"name":o["name"],"type":scene.obj_type(o),"children":branch(scene,Some(id(o)))})).collect::<Vec<_>>())}return Ok(json!({"objects":branch(scene,None),"collections":scene.collections}));},
"materials"=>return Ok(json!(scene.materials.iter().map(|m|json!({"name":m["name"],"users":scene.users("materials",id(m)),"use_nodes":m["use_nodes"],"diffuse_color":m["diffuse_color"],"metallic":m["metallic"],"roughness":m["roughness"]})).collect::<Vec<_>>())),_=>{}}
    let g = Geometry::new(scene, false)?;
    let arg = |i| {
        args.get(i)
            .map(String::as_str)
            .ok_or("Missing query argument".to_string())
    };
    match op {
        "bbox" => {
            if args.get(1).is_none_or(|s| s == "--all") {
                Ok(
                    json!({"bbox":g.bounds.value(),"objects":g.objects.iter().map(|o|json!({"name":o.name,"bbox":o.bounds.value()})).collect::<Vec<_>>()}),
                )
            } else {
                let o = g.object(arg(1)?)?;
                Ok(json!({"name":o.name,"bbox":o.bounds.value()}))
            }
        }
        "distance" => {
            let a = g.object(arg(1)?)?;
            let b = g.object(arg(2)?)?;
            let (d, p, q) = distance(&g, a, b)?;
            Ok(
                json!({"a":a.name,"b":b.name,"distance":d,"point_a":p,"point_b":q,"units":"meters","method":"triangle surfaces"}),
            )
        }
        "inside" => {
            let a = g.object(arg(1)?)?;
            let b = g.object(arg(2)?)?;
            if !closed(&g, b) {
                return Err("Containment requires a closed two-manifold target mesh".into());
            }
            let center = b.bounds.center();
            let mut planes = vec![];
            for &i in &b.triangles {
                let t = &g.triangles[i];
                let mut n = normalize(cross(sub(t.p[1], t.p[0]), sub(t.p[2], t.p[0])));
                if dot(n, sub(center, t.p[0])) > 0. {
                    n = mul(n, -1.);
                }
                if b.vertices.iter().any(|p| dot(n, sub(*p, t.p[0])) > 1e-7) {
                    return Err("M1 exact containment supports closed convex targets; concave target containment is unsupported".into());
                }
                planes.push((n, t.p[0]));
            }
            Ok(
                json!({"a":a.name,"b":b.name,"inside":!a.vertices.is_empty()&&a.vertices.iter().all(|p|planes.iter().all(|(n,q)|dot(*n,sub(*p,*q))<=1e-7)),"boundary_included":true,"method":"convex halfspaces","tolerance":1e-7}),
            )
        }
        "overlaps" => {
            let mut pairs = vec![];
            for i in 0..g.objects.len() {
                for j in i + 1..g.objects.len() {
                    let a = &g.objects[i];
                    let b = &g.objects[j];
                    if a.bounds.distance(b.bounds) > 1e-7 {
                        continue;
                    }
                    let d = distance(&g, a, b)?.0;
                    let contained = d > 1e-7
                        && ((closed(&g, b) && inside_point(&g, a.vertices[0], b))
                            || (closed(&g, a) && inside_point(&g, b.vertices[0], a)));
                    if d <= 1e-7 || contained {
                        pairs.push(json!({"a":a.name,"b":b.name,"relation":if contained{"containment"}else{"surface_contact_or_intersection"}}));
                    }
                }
            }
            Ok(json!({"pairs":pairs,"tolerance":1e-7}))
        }
        "floating" => {
            let mut floating = vec![];
            for a in &g.objects {
                let mut touching = false;
                for b in &g.objects {
                    if a.id != b.id
                        && a.bounds.distance(b.bounds) <= 1e-5
                        && distance(&g, a, b)?.0 <= 1e-5
                    {
                        touching = true;
                        break;
                    }
                }
                if !touching {
                    floating.push(&a.name);
                }
            }
            Ok(json!({"objects":floating,"contact_tolerance":1e-5}))
        }
        "visible" => {
            let name = if args.get(1).is_some_and(|s| s == "--camera") {
                args.get(2).map(String::as_str)
            } else {
                None
            };
            let camera = super::render::Camera::scene(scene, name, 1.)?;
            Ok(
                json!({"objects":g.objects.iter().filter(|o|o.triangles.iter().any(|&i|camera.intersects(&g.triangles[i]))).map(|o|&o.name).collect::<Vec<_>>(),"method":"clipped triangle frustum intersection","occlusion_tested":false}),
            )
        }
        _ => Err(format!("Unsupported query {op}")),
    }
}
