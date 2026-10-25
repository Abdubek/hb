//! Bounded geometry observations and revision-bound visual delivery.
use super::*;
use crate::core::{
    geometry::Geometry,
    math::{cross, dot, length, point, sub},
    render::Camera,
};
use sha2::{Digest, Sha256};
use std::collections::BTreeMap;
const CHECKS: &[&str] = &["brief", "silhouette", "materials", "composition", "detail"];
fn hash(bytes: &[u8]) -> String {
    format!("{:x}", Sha256::digest(bytes))
}
fn engine_hash() -> Result<String, Value> {
    Ok(hash(
        &fs::read(std::env::current_exe().map_err(ioerr)?).map_err(ioerr)?,
    ))
}
fn issue(
    rows: &mut Vec<Value>,
    code: &str,
    severity: &str,
    object: Option<&core::geometry::ObjectGeometry>,
    message: &str,
    action: &str,
    evidence: Value,
) {
    rows.push(json!({"id":format!("{}/{}",code,object.map(|o|o.id.to_string()).unwrap_or("scene".into())),"code":code,"severity":severity,"object":object.map(|o|&o.name),"message":message,"suggestion":action,"evidence":evidence}));
}
pub fn inspect(
    scene: &Scene,
    profile: &str,
    camera_name: Option<&str>,
    size: usize,
) -> Result<Value, Value> {
    if !["product", "assembly", "stylized"].contains(&profile) || !(16..=2048).contains(&size) {
        return Err(err(
            "USAGE",
            "Use profile product/assembly/stylized and size 16..2048",
        ));
    }
    let g = Geometry::new(scene, true).map_err(|e| err("GEOMETRY_ERROR", &e))?;
    let mut issues = vec![];
    if g.triangles.is_empty() {
        issue(
            &mut issues,
            "EMPTY_SURFACE",
            "error",
            None,
            "No renderable triangles.",
            "Create or unhide surface geometry.",
            json!({}),
        );
    }
    let camera = match Camera::scene(scene, camera_name, 1.) {
        Ok(c) => Some(c),
        Err(e) => {
            if camera_name.is_some() {
                return Err(err("CAMERA_ERROR", &e));
            }
            issue(
                &mut issues,
                "NO_CAMERA",
                "warning",
                None,
                "No active camera; review uses a fitted camera panel.",
                "Use the studio recipe or set an active camera; an intentional fitted overview can be acknowledged.",
                json!({}),
            );
            None
        }
    };
    let mut objects = vec![];
    for o in &g.objects {
        let mut edges: BTreeMap<(usize, usize), Vec<bool>> = BTreeMap::new();
        let mut degenerate = 0;
        let mut volume = 0.;
        let mut missing_material = 0;
        let center = o.bounds.center();
        let area_epsilon = length(o.bounds.extent()).powi(2) * 1e-12;
        for &index in &o.triangles {
            let t = &g.triangles[index];
            if length(cross(sub(t.p[1], t.p[0]), sub(t.p[2], t.p[0]))) <= area_epsilon {
                degenerate += 1;
            }
            volume += dot(
                sub(t.p[0], center),
                cross(sub(t.p[1], center), sub(t.p[2], center)),
            ) / 6.;
            if t.material.is_none() {
                missing_material += 1;
            }
            for i in 0..3 {
                let a = t.vertex_indices[i];
                let b = t.vertex_indices[(i + 1) % 3];
                edges.entry((a.min(b), a.max(b))).or_default().push(a < b);
            }
        }
        let boundary = edges.values().filter(|v| v.len() == 1).count();
        let nonmanifold = edges.values().filter(|v| v.len() > 2).count();
        let winding = edges
            .values()
            .filter(|v| v.len() == 2 && v[0] == v[1])
            .count();
        if degenerate > 0 {
            issue(
                &mut issues,
                "DEGENERATE_TRIANGLES",
                "error",
                Some(o),
                "Zero or numerically tiny area triangles.",
                "Remove collapsed faces or adjust the operation that created them.",
                json!({"count":degenerate,"twice_area_threshold":area_epsilon}),
            );
        }
        if boundary > 0 {
            issue(
                &mut issues,
                "OPEN_SURFACE",
                "warning",
                Some(o),
                "Surface has boundary edges; sheets and uncapped tubes may intentionally be open.",
                "Cap solid parts, add thickness, or acknowledge an intentional open surface.",
                json!({"boundary_edges":boundary}),
            );
        }
        if nonmanifold > 0 || winding > 0 {
            issue(
                &mut issues,
                "TOPOLOGY_JUNCTION",
                "warning",
                Some(o),
                "Some edges have more than two faces or inconsistent orientation.",
                "Inspect wireframe; repair the junction or explain the intended topology.",
                json!({"nonmanifold_edges":nonmanifold,"inconsistent_edges":winding}),
            );
        }
        if boundary == 0 && nonmanifold == 0 && winding == 0 && volume < 0. {
            issue(
                &mut issues,
                "INWARD_SURFACE",
                "warning",
                Some(o),
                "Closed surface has negative signed volume.",
                "Inspect face orientation; repair normals unless the inward shell is intentional.",
                json!({"signed_volume":volume}),
            );
        }
        if missing_material > 0 && profile != "stylized" {
            issue(
                &mut issues,
                "DEFAULT_MATERIAL",
                "warning",
                Some(o),
                "Part uses the implicit default surface.",
                "Assign an intentional material or acknowledge the desired default appearance.",
                json!({"triangles":missing_material}),
            );
        }
        let mut framing = Value::Null;
        if let Some(c) = &camera {
            let visible = o.triangles.iter().any(|&i| c.intersects(&g.triangles[i]));
            let outside = o.vertices.iter().filter(|p| !c.contains(**p)).count();
            let mut min = [f64::INFINITY; 2];
            let mut max = [f64::NEG_INFINITY; 2];
            for &p in &o.vertices {
                let p = point(c.view, p);
                let k = if c.perspective { -p[2] } else { 1. };
                if -p[2] < c.near {
                    continue;
                }
                let xy = [
                    ((p[0] / k - c.shift[0]) / c.half_x * 0.5 + 0.5) * size as f64,
                    (0.5 - (p[1] / k - c.shift[1]) / c.half_y * 0.5) * size as f64,
                ];
                for i in 0..2 {
                    min[i] = min[i].min(xy[i]);
                    max[i] = max[i].max(xy[i]);
                }
            }
            let pixels = if min[0].is_finite() {
                [
                    (max[0].min(size as f64) - min[0].max(0.)).max(0.),
                    (max[1].min(size as f64) - min[1].max(0.)).max(0.),
                ]
            } else {
                [0.; 2]
            };
            framing = json!({"intersects_frustum":visible,"vertices_outside":outside,"projected_bbox_pixels":pixels,"occlusion_tested":false});
            if !visible {
                issue(
                    &mut issues,
                    "OUTSIDE_CAMERA",
                    "warning",
                    Some(o),
                    "Part does not intersect the camera frustum.",
                    "Adjust camera/placement or acknowledge a deliberately off-camera part.",
                    framing.clone(),
                );
            } else if outside > 0 {
                issue(
                    &mut issues,
                    "CAMERA_CROP",
                    "warning",
                    Some(o),
                    "Some vertices lie outside the camera frustum.",
                    "Reframe important parts; deliberate floor/background cropping may be acknowledged.",
                    framing.clone(),
                );
            }
            let source = scene.object(o.id).map_err(|e| err("GEOMETRY_ERROR", &e))?;
            let is_text = source["data"]
                .as_u64()
                .and_then(|id| scene.get("meshes", id).ok())
                .is_some_and(|m| m["curve"]["type"] == "FONT");
            if visible && is_text && pixels[0].min(pixels[1]) < 12. {
                issue(
                    &mut issues,
                    "SMALL_TEXT",
                    "warning",
                    Some(o),
                    "Text occupies fewer than 12 pixels on one projected axis.",
                    "Inspect readability at delivery size; enlarge or reorient the label if needed. This is a size heuristic, not OCR.",
                    framing.clone(),
                );
            }
        }
        objects.push(json!({"name":o.name,"triangles":o.triangles.len(),"bounds":o.bounds.value(),"boundary_edges":boundary,"nonmanifold_edges":nonmanifold,"signed_volume":volume,"framing":framing}));
    }
    let errors = issues.iter().filter(|i| i["severity"] == "error").count();
    Ok(
        json!({"profile":profile,"size":size,"camera":camera_name,"errors":errors,"warnings":issues.len()-errors,"geometry_ready":errors==0,"issues":issues,"objects":objects,"scope":"Evaluated render-visible surfaces and square-camera framing. No self-intersection, occlusion, material taste, text recognition or artistic-quality proof. Overlap/contact queries remain separately available."}),
    )
}
fn resolved(path: &Path) -> Result<PathBuf, Value> {
    if path.exists() {
        return fs::canonicalize(path).map_err(ioerr);
    }
    let parent = path
        .parent()
        .filter(|p| !p.as_os_str().is_empty())
        .unwrap_or(Path::new("."));
    Ok(fs::canonicalize(parent).map_err(ioerr)?.join(
        path.file_name()
            .ok_or_else(|| err("USAGE", "Expected output filename"))?,
    ))
}
fn protect(output: &Path, scene: &Path, other: &[&Path]) -> Result<(), Value> {
    let output = resolved(output)?;
    if output == resolved(scene)?
        || output.starts_with(resolved(&store::history(scene))?)
        || other.iter().any(|p| resolved(p).is_ok_and(|p| p == output))
    {
        return Err(err(
            "USAGE",
            "Output must not overwrite the scene, revision history or review inputs",
        ));
    }
    Ok(())
}
fn options(args: &mut Vec<String>) -> Result<(String, Option<String>, usize), Value> {
    let profile = take_option(args, "--profile")?.unwrap_or("product".into());
    let camera = take_option(args, "--camera")?;
    let size = take_option(args, "--size")?
        .unwrap_or("512".into())
        .parse()
        .map_err(|_| err("USAGE", "Invalid review size"))?;
    Ok((profile, camera, size))
}
pub fn command(command: &str, mut args: Vec<String>, path: &Path) -> Result<Value, Value> {
    // Hold the scene writer lock through snapshot inspection and export.
    let _lock = if command == "deliver" || command == "review" {
        Some(Lock::acquire(path)?)
    } else {
        None
    };
    let r = required(path)?;
    if command == "inspect" || command == "review" {
        let (profile, camera, size) = options(&mut args)?;
        let out = if command == "review" {
            Some(PathBuf::from(
                take_option(&mut args, "--out")?.unwrap_or("review.json".into()),
            ))
        } else {
            None
        };
        let focus = if command == "review" {
            take_option(&mut args, "--focus")?
        } else {
            None
        };
        if !args.is_empty() {
            return Err(err("USAGE", "Unknown inspection/review argument"));
        }
        let diagnostics = inspect(&r.state.scene, &profile, camera.as_deref(), size)?;
        if let Some(out) = out {
            let image = out.with_extension("review.png");
            protect(&out, path, &[&image])?;
            protect(&image, path, &[&out])?;
            // A large flat backdrop should not shrink all diagnostic views.
            // This only changes fitted cameras; all objects still render.
            let focus: Vec<String> = if let Some(names) = focus {
                names.split(',').map(|n| n.trim().to_string()).collect()
            } else {
                diagnostics["objects"]
                    .as_array()
                    .unwrap()
                    .iter()
                    .filter(|o| {
                        o["bounds"]["dimensions"].as_array().is_some_and(|d| {
                            let largest = d.iter().filter_map(Value::as_f64).fold(0., f64::max);
                            d.iter().all(|x| x.as_f64().unwrap_or(0.) > largest * 1e-6)
                        })
                    })
                    .filter_map(|o| o["name"].as_str().map(str::to_string))
                    .collect()
            };
            let (bytes, render) = core::render::render_focused(
                &r.state.scene,
                size,
                Some("camera,front,right,top,wire"),
                camera.as_deref(),
                false,
                "final",
                if focus.is_empty() { None } else { Some(&focus) },
            )
            .map_err(|e| err("RENDER_ERROR", &e))?;
            let image_hash = hash(&bytes);
            atomic_write(&image, &bytes)?;
            let image = fs::canonicalize(image).map_err(ioerr)?;
            let mut checks = json!({});
            for key in CHECKS {
                checks[*key] = json!({"pass":false,"notes":""});
            }
            let assessment = json!({"revision":r.id,"image_sha256":image_hash,"checks":checks,"acknowledged_warnings":{}});
            let receipt = json!({"format":"hb-review-v1","revision":r.id,"scene":fs::canonicalize(path).map_err(ioerr)?,"manifest_sha256":hash(MANIFEST.as_bytes()),"engine_sha256":engine_hash()?,"image":image,"image_sha256":image_hash,"diagnostics":diagnostics,"render":render,"assessment_template":assessment});
            atomic_write(
                &out,
                serde_json::to_string_pretty(&receipt).unwrap().as_bytes(),
            )?;
            return Ok(
                json!({"ok":true,"revision":r.id,"output":out,"image":image,"review":receipt,"next":"Read the image. Fix defects and review again, or fill the assessment template with observations and reasons for each accepted warning. deliver checks freshness, not visual comprehension."}),
            );
        }
        return Ok(json!({"ok":true,"revision":r.id,"diagnostics":diagnostics}));
    }
    let review = PathBuf::from(
        take_option(&mut args, "--review")?
            .ok_or_else(|| err("USAGE", "deliver requires --review"))?,
    );
    let assessment = take_option(&mut args, "--assessment")?.map(PathBuf::from);
    let inline = take_option(&mut args, "--assessment-json")?;
    if assessment.is_some() == inline.is_some() {
        return Err(err(
            "USAGE",
            "Supply exactly one of --assessment FILE or --assessment-json JSON",
        ));
    }
    let out = PathBuf::from(
        take_option(&mut args, "--out")?.ok_or_else(|| err("USAGE", "deliver requires --out"))?,
    );
    if !args.is_empty() {
        return Err(err("USAGE", "Unknown delivery argument"));
    }
    let read_json = |p: &Path| -> Result<Value, Value> {
        serde_json::from_slice(&fs::read(p).map_err(ioerr)?)
            .map_err(|_| err("INVALID_REVIEW", "Expected a JSON review/assessment"))
    };
    let receipt = read_json(&review)?;
    let assessment_value = match (&assessment, &inline) {
        (Some(path), _) => read_json(path)?,
        (_, Some(value)) => serde_json::from_str(value)
            .map_err(|_| err("INVALID_REVIEW", "Invalid assessment JSON"))?,
        _ => unreachable!(),
    };
    if receipt["format"] != "hb-review-v1"
        || receipt["revision"] != r.id
        || receipt["manifest_sha256"] != hash(MANIFEST.as_bytes())
        || receipt["engine_sha256"] != engine_hash()?
        || receipt["scene"] != json!(fs::canonicalize(path).map_err(ioerr)?)
    {
        return Err(err(
            "STALE_REVIEW",
            "Review must refer to this scene's current revision, engine and API contract",
        ));
    }
    let image = PathBuf::from(
        receipt["image"]
            .as_str()
            .ok_or_else(|| err("INVALID_REVIEW", "Missing image"))?,
    );
    if receipt["image_sha256"] != hash(&fs::read(&image).map_err(ioerr)?) {
        return Err(err(
            "STALE_REVIEW",
            "Review image changed; render and inspect again",
        ));
    }
    let d = &receipt["diagnostics"];
    let diagnostics = inspect(
        &r.state.scene,
        d["profile"].as_str().unwrap_or(""),
        d["camera"].as_str(),
        d["size"].as_u64().unwrap_or(0) as usize,
    )?;
    if diagnostics != *d {
        return Err(err(
            "STALE_REVIEW",
            "Review diagnostics differ; create a fresh review",
        ));
    }
    if diagnostics["geometry_ready"] != true {
        return Err(err(
            "QUALITY_FAILED",
            "Resolve geometry errors before delivery",
        ));
    }
    if assessment_value["revision"] != r.id
        || assessment_value["image_sha256"] != receipt["image_sha256"]
    {
        return Err(err(
            "STALE_ASSESSMENT",
            "Assessment must identify the reviewed revision and image hash",
        ));
    }
    for key in CHECKS {
        let check = &assessment_value["checks"][*key];
        if check["pass"] != true || check["notes"].as_str().is_none_or(|s| s.trim().is_empty()) {
            return Err(err(
                "ASSESSMENT_REQUIRED",
                &format!(
                    "Provide a passing visual assessment and concrete notes for {key}; otherwise revise the scene"
                ),
            ));
        }
    }
    for issue in diagnostics["issues"].as_array().unwrap() {
        if assessment_value["acknowledged_warnings"][issue["id"].as_str().unwrap()]
            .as_str()
            .is_none_or(|s| s.trim().is_empty())
        {
            return Err(err(
                "UNREVIEWED_WARNING",
                &format!("Resolve or explain {}", issue["id"]),
            ));
        }
    }
    let report = out.with_extension("delivery.json");
    let mut protected = vec![review.as_path(), image.as_path()];
    if let Some(assessment) = &assessment {
        protected.push(assessment);
    }
    protect(&out, path, &protected)?;
    protect(&report, path, &protected)?;
    protect(&out, path, &[&report])?;
    if out
        .extension()
        .is_some_and(|e| e.eq_ignore_ascii_case("obj"))
    {
        protect(&out.with_extension("mtl"), path, &protected)?;
    }
    let ws = export(&r.state.scene, &out)?;
    let delivery = json!({"ok":true,"revision":r.id,"output":out,"output_sha256":hash(&fs::read(&out).map_err(ioerr)?),"review":review,"image":image,"assessment":assessment_value,"diagnostics":diagnostics,"warnings":ws,"scope":"Review freshness and explicit agent assessment verified; artistic quality is not mechanically proven."});
    atomic_write(
        &report,
        serde_json::to_string_pretty(&delivery).unwrap().as_bytes(),
    )?;
    Ok(delivery)
}
