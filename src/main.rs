mod cli;
mod core;
mod manifest;
mod preview;
mod random;
use core::Scene;

use serde_json::{Value, json};
use std::{
    ffi::{CStr, CString, c_char},
    fs,
    io::Write,
    path::{Path, PathBuf},
    sync::{Mutex, OnceLock},
    time::Instant,
};
static SCENE: OnceLock<Mutex<Scene>> = OnceLock::new();
static RESULT: OnceLock<Mutex<Value>> = OnceLock::new();
fn scene() -> &'static Mutex<Scene> {
    SCENE.get_or_init(|| Mutex::new(Scene::default()))
}
fn result() -> &'static Mutex<Value> {
    RESULT.get_or_init(|| Mutex::new(Value::Null))
}
#[unsafe(no_mangle)]
/// # Safety
/// `words` must point to writable storage for 624 u32 values owned by the C bridge.
pub unsafe extern "C" fn hb_seed_state(seed: u64, words: *mut u32) {
    let rng = random::SeededRng::new(seed);
    unsafe { std::ptr::copy_nonoverlapping(rng.state().0.as_ptr(), words, 624) };
}
#[unsafe(no_mangle)]
/// # Safety
/// `input` must be a live, NUL-terminated UTF-8 string supplied by the C bridge.
pub unsafe extern "C" fn hb_core_request(input: *const c_char) -> *mut c_char {
    let r = (|| -> Result<Value, String> {
        let input = unsafe { CStr::from_ptr(input) }
            .to_str()
            .map_err(|e| e.to_string())?;
        let r: Value = serde_json::from_str(input).map_err(|e| e.to_string())?;
        if r["op"] == "manifest_accepts" {
            let alternatives: Vec<String> =
                serde_json::from_value(r["alternatives"].clone()).map_err(|e| e.to_string())?;
            return Ok(json!(manifest().accepts(&alternatives)));
        }
        if r["op"] == "execution_result" {
            *result().lock().unwrap() = r["value"].clone();
            return Ok(Value::Null);
        }
        scene().lock().unwrap().request(r)
    })();
    let output = match r {
        Ok(v) => json!({"result":v}),
        Err(e) => json!({"error":e}),
    };
    CString::new(output.to_string()).unwrap().into_raw()
}
#[unsafe(no_mangle)]
/// # Safety
/// `ptr` must be null or an unreleased pointer returned by `hb_core_request`.
pub unsafe extern "C" fn hb_core_free(ptr: *mut c_char) {
    if !ptr.is_null() {
        drop(unsafe { CString::from_raw(ptr) });
    }
}
unsafe extern "C" {
    fn hb_python_init() -> i32;
    fn hb_python_exec(source: *const c_char) -> i32;
    fn hb_python_finish() -> i32;
}
fn py(code: &str) -> Result<(), Value> {
    let c = CString::new(code).map_err(|_| err("SCRIPT_ERROR", "NUL byte in source"))?;
    if unsafe { hb_python_exec(c.as_ptr()) } != 0 {
        Err(err("PYTHON_ERROR", "Embedded Python failed"))
    } else {
        Ok(())
    }
}
const MANIFEST: &str = include_str!("../compat/manifest.json");
fn manifest() -> &'static crate::manifest::Manifest {
    static MANIFEST_INDEX: OnceLock<crate::manifest::Manifest> = OnceLock::new();
    MANIFEST_INDEX.get_or_init(|| {
        crate::manifest::Manifest::new(serde_json::from_str(MANIFEST).unwrap()).unwrap()
    })
}
struct Python;
impl Python {
    fn start(seed: u64) -> Result<Self, Value> {
        if unsafe { hb_python_init() } != 0 {
            return Err(err("PYTHON_INIT", "Could not initialize embedded CPython"));
        }
        let p = Python;
        py(&format!(
            "SEED = {seed}\nimport json, _hb\nfrom _hb_runtime import check, execute"
        ))?;
        Ok(p)
    }
}
impl Drop for Python {
    fn drop(&mut self) {
        unsafe {
            hb_python_finish();
        }
    }
}
fn err(code: &str, message: &str) -> Value {
    json!({
        "code": code,
        "message": message,
        "location": null,
        "suggestion": "Run hb capabilities or hb api --json for the tested API contract.",
        "doc": "docs/compatibility.md"
    })
}
fn ioerr(e: std::io::Error) -> Value {
    err("IO_ERROR", &e.to_string())
}

mod guidance;
mod quality;
mod recipes;
mod server;
mod store;
use store::{Lock, Revision, atomic_write, load, save};
fn changes(before: &Scene, after: &Scene) -> Value {
    let mut out = json!({});
    for kind in [
        "objects",
        "meshes",
        "materials",
        "cameras",
        "lights",
        "collections",
        "images",
        "textures",
        "worlds",
    ] {
        let a = before.db(kind).unwrap();
        let b = after.db(kind).unwrap();
        let created: Vec<_> = b
            .iter()
            .filter(|v| !a.iter().any(|x| core::id(x) == core::id(v)))
            .map(|v| v["name"].clone())
            .collect();
        let deleted: Vec<_> = a
            .iter()
            .filter(|v| !b.iter().any(|x| core::id(x) == core::id(v)))
            .map(|v| v["name"].clone())
            .collect();
        let modified:Vec<_>=b.iter().filter_map(|v|a.iter().find(|x|core::id(x)==core::id(v)).filter(|x|*x!=v).map(|x|{let fields:Vec<_>=v.as_object().unwrap().keys().filter(|k|x[*k]!=v[*k]).cloned().collect();let mut delta=json!({"name":v["name"],"before_name":x["name"],"fields":fields});if kind=="meshes"{delta["vertices"]=json!({"before":x["vertices"].as_array().unwrap().len(),"after":v["vertices"].as_array().unwrap().len()});delta["faces"]=json!({"before":x["faces"].as_array().unwrap().len(),"after":v["faces"].as_array().unwrap().len()});}for f in ["location","rotation_euler","scale","parent","data","diffuse_color","metallic","roughness"]{if x[f]!=v[f]{delta[f]=json!({"before":x[f],"after":v[f]});}}delta})).collect();
        out[kind] = json!({"created":created,"deleted":deleted,"modified":modified});
    }
    if before.scene_world != after.scene_world {
        let name = |scene: &Scene| {
            scene
                .scene_world
                .and_then(|key| scene.get("worlds", key).ok())
                .map(|world| world["name"].clone())
        };
        out["scene"] = json!({"world":{"before":name(before),"after":name(after)}});
    }
    out
}
fn warnings(s: &Scene) -> Vec<Value> {
    let mut out = vec![];
    for o in &s.objects {
        if core::vec3(&o["rotation_euler"])
            .iter()
            .any(|x| x.abs() > std::f64::consts::TAU)
        {
            out.push(err(
                "ROTATION_UNITS",
                &format!(
                    "{} has an Euler channel above 2π; verify radians",
                    core::text(&o["name"])
                ),
            ));
        }
    }
    if let Ok(g) = core::geometry::Geometry::new(s, false) {
        if g.bounds.min[0].is_finite() {
            let size = core::math::length(g.bounds.extent());
            if !(0.01..=10000.).contains(&size) {
                out.push(err(
                    "SCENE_UNITS",
                    "Scene bounds are below 1 cm or above 10 km; verify meters",
                ));
            }
        }
        let degenerate = g
            .triangles
            .iter()
            .filter(|t| {
                core::math::length(core::math::cross(
                    core::math::sub(t.p[1], t.p[0]),
                    core::math::sub(t.p[2], t.p[0]),
                )) < 1e-12
            })
            .count();
        if degenerate > 0 {
            out.push(err(
                "ZERO_AREA_FACES",
                &format!("{degenerate} evaluated triangles have zero area"),
            ));
        }
        if let Ok(camera) = core::render::Camera::scene(s, None, 1.) {
            for o in &g.objects {
                if !o
                    .triangles
                    .iter()
                    .any(|&i| camera.intersects(&g.triangles[i]))
                {
                    out.push(err(
                        "OUTSIDE_CAMERA",
                        &format!("{} is outside the active camera frustum", o.name),
                    ));
                }
            }
        }
    }
    for m in &s.materials {
        if s.users("materials", core::id(m)) == 0 {
            out.push(err(
                "UNUSED_MATERIAL",
                &format!("{} is assigned to no mesh slots", core::text(&m["name"])),
            ));
        }
    }
    out
}
fn take_option(args: &mut Vec<String>, flag: &str) -> Result<Option<String>, Value> {
    crate::cli::take_option(args, flag, err)
}
use crate::cli::take_flag;
fn required(path: &Path) -> Result<Revision, Value> {
    load(path)?.ok_or_else(|| {
        err(
            "SCENE_NOT_FOUND",
            "Run or import a scene first; pass --scene path.hb",
        )
    })
}
fn export(s: &Scene, out: &Path) -> Result<Vec<String>, Value> {
    match out.extension().and_then(|x| x.to_str()) {
        Some("glb") => {
            let (bytes, warnings) = core::io::glb(s).map_err(|e| err("EXPORT_ERROR", &e))?;
            atomic_write(out, &bytes)?;
            Ok(warnings)
        }
        Some("usdz") => {
            let (bytes, warnings) = core::usdz::export(s).map_err(|e| err("EXPORT_ERROR", &e))?;
            atomic_write(out, &bytes)?;
            Ok(warnings)
        }
        Some("obj") => core::obj_export::export(
            s,
            out,
            &json!({"apply":true,"matrix":core::math::flat(core::math::IDENTITY)}),
        )
        .map_err(|e| err("EXPORT_ERROR", &e)),
        Some("gltf") => {
            let (mut doc, bin, warnings) =
                core::io::gltf(s).map_err(|e| err("EXPORT_ERROR", &e))?;
            if !bin.is_empty() {
                doc["buffers"][0]["uri"] = json!(format!(
                    "data:application/octet-stream;base64,{}",
                    base64::Engine::encode(&base64::engine::general_purpose::STANDARD, &bin)
                ));
            }
            atomic_write(out, &serde_json::to_vec(&doc).unwrap())?;
            Ok(warnings)
        }
        _ => Err(err(
            "UNSUPPORTED_FORMAT",
            "Export supports .glb, self-contained .gltf, .obj with companion MTL, or .usdz.",
        )),
    }
}
fn dispatch(mut args: Vec<String>) -> Result<Value, Value> {
    let start = Instant::now();
    if args.is_empty() {
        args.push("capabilities".into());
    }
    let command = args.remove(0);
    let path = PathBuf::from(take_option(&mut args, "--scene")?.unwrap_or("scene.hb".into()));
    match command.as_str() {
        "capabilities" | "--help" | "-h" => {
            take_flag(&mut args, "--json");
            let task = take_option(&mut args, "--task")?;
            if !args.is_empty() {
                return Err(err("USAGE", "hb capabilities [--json] [--task TEXT]"));
            }
            Ok(guidance::capabilities(task.as_deref()))
        }
        "recipe" => recipes::command(args),
        "inspect" | "review" | "deliver" => quality::command(&command, args, &path),
        "licenses" => Ok(
            json!({"engine":"MIT","python":"PSF-2.0","third_party":include_str!("../docs/THIRD-PARTY-NOTICES.txt"),"python_license":include_str!("../docs/CPYTHON-LICENSE.txt")}),
        ),
        "api" => {
            take_flag(&mut args, "--json");
            let m: Value = serde_json::from_str(MANIFEST).unwrap();
            if args.len() > 1 {
                return Err(err("USAGE", "hb api [--json] [dotted.path]"));
            }
            if let Some(prefix) = args.first() {
                Ok(manifest().filter(prefix))
            } else {
                Ok(m)
            }
        }
        "check" | "run" => {
            let seed = take_option(&mut args, "--seed")?
                .unwrap_or("0".into())
                .parse::<u64>()
                .map_err(|_| err("USAGE", "Seed must be an unsigned integer"))?;
            let out = take_option(&mut args, "--out")?;
            if args.len() != 1 {
                return Err(err(
                    "USAGE",
                    "hb run/check script.py [--scene scene.hb] [--seed 0]",
                ));
            }
            let filename = &args[0];
            let source = fs::read_to_string(filename).map_err(ioerr)?;
            let _lock = if command == "run" {
                Some(Lock::acquire(&path)?)
            } else {
                None
            };
            let previous = if command == "run" { load(&path)? } else { None };
            let before = previous
                .as_ref()
                .map(|r| r.state.scene.clone())
                .unwrap_or_default();
            *scene().lock().unwrap() = before.clone();
            *result().lock().unwrap() = Value::Null;
            let init = Instant::now();
            let _python = Python::start(seed)?;
            let python_ms = init.elapsed().as_secs_f64() * 1000.;
            if command == "check" {
                py(&format!(
                    "_hb.request(json.dumps({{'op':'execution_result','value':{{'errors':check({}, {})}}}}))",
                    json!(source),
                    json!(filename)
                ))?;
                let errors = result().lock().unwrap()["errors"].clone();
                return Ok(
                    json!({"ok":errors.as_array().unwrap().is_empty(),"errors":errors,"file":filename,"timing":{"python_init_ms":python_ms,"total_ms":start.elapsed().as_secs_f64()*1000.}}),
                );
            }
            py(&format!("execute({}, {})", json!(source), json!(filename)))?;
            let outcome = result().lock().unwrap().clone();
            if outcome["ok"] != true {
                return Ok(outcome);
            }
            let after = scene().lock().unwrap().clone();
            after.validate().map_err(|e| err("INVALID_SCENE", &e))?;
            let mut ws = warnings(&after);
            if let Some(operation_warnings) = outcome["warnings"].as_array() {
                ws.extend(operation_warnings.iter().cloned());
            }
            if let Some(out) = &out {
                if Path::new(out) == path {
                    return Err(err(
                        "USAGE",
                        "Export output cannot overwrite the scene head",
                    ));
                }
                ws.extend(
                    export(&after, Path::new(out))?
                        .into_iter()
                        .map(Value::String),
                );
            }
            let parent = previous.map(|r| r.id);
            let id = after.revision(&source, parent.as_deref(), seed);
            let diff = changes(&before, &after);
            let report = json!({"ok":true,"revision":id,"scene":path,"objects":{"created":diff["objects"]["created"],"deleted":diff["objects"]["deleted"],"modified":diff["objects"]["modified"].as_array().unwrap().iter().map(|v|v["name"].clone()).collect::<Vec<_>>()},"changes":diff,"next":{"tool":"hb_review","args":["--scene",path,"--out","review.json"],"reason":"Inspect the current revision before final delivery"},"warnings":ws,"timing":{"python_init_ms":python_ms,"total_ms":start.elapsed().as_secs_f64()*1000.},"export":out});
            save(
                &path,
                &Revision {
                    format: "hb-m1-v1".into(),
                    id,
                    parent,
                    script: source,
                    seed,
                    state: store::State { scene: after },
                },
            )?;
            Ok(report)
        }
        "import" => {
            if args.len() != 1 {
                return Err(err(
                    "USAGE",
                    "hb import asset.glb/.gltf/.obj/.stl/.ply [--scene scene.hb]",
                ));
            }
            let _lock = Lock::acquire(&path)?;
            let previous = load(&path)?;
            let before = previous
                .as_ref()
                .map(|r| r.state.scene.clone())
                .unwrap_or_default();
            let mut after = before.clone();
            let ws = core::io::import(&mut after, Path::new(&args[0]))
                .map_err(|e| err("IMPORT_ERROR", &e))?;
            let source = format!("# hb import {}", args[0]);
            let parent = previous.map(|r| r.id);
            let id = after.revision(&source, parent.as_deref(), 0);
            let changes = changes(&before, &after);
            save(
                &path,
                &Revision {
                    format: "hb-m1-v1".into(),
                    id: id.clone(),
                    parent,
                    script: source,
                    seed: 0,
                    state: store::State { scene: after },
                },
            )?;
            Ok(json!({"ok":true,"revision":id,"changes":changes,"warnings":ws}))
        }
        "export" => {
            if args.len() != 1 {
                return Err(err(
                    "USAGE",
                    "hb export output.glb/.gltf/.obj/.usdz [--scene scene.hb]",
                ));
            }
            if Path::new(&args[0]) == path {
                return Err(err("USAGE", "Export cannot overwrite scene head"));
            }
            let r = required(&path)?;
            let ws = export(&r.state.scene, Path::new(&args[0]))?;
            Ok(json!({"ok":true,"output":args[0],"revision":r.id,"warnings":ws}))
        }
        "query" => {
            let r = required(&path)?;
            let data =
                core::geometry::query(&r.state.scene, &args).map_err(|e| err("QUERY_ERROR", &e))?;
            Ok(
                json!({"ok":true,"revision":r.id,"result":data,"query_ms":start.elapsed().as_secs_f64()*1000.}),
            )
        }
        "render" => {
            let size = take_option(&mut args, "--size")?
                .unwrap_or("512".into())
                .parse::<usize>()
                .map_err(|_| err("USAGE", "Invalid preview size"))?;
            let views = take_option(&mut args, "--views")?;
            let camera = take_option(&mut args, "--camera")?;
            let out = take_option(&mut args, "--out")?.unwrap_or("sheet.png".into());
            let wire = take_flag(&mut args, "--wire");
            let quality = take_option(&mut args, "--quality")?.unwrap_or("draft".into());
            if !args.is_empty() {
                return Err(err("USAGE", "Unknown render argument"));
            }
            if Path::new(&out) == path {
                return Err(err("USAGE", "Render cannot overwrite scene head"));
            }
            let r = required(&path)?;
            let (bytes, info) = if quality == "draft" {
                core::render::render(
                    &r.state.scene,
                    size,
                    views.as_deref(),
                    camera.as_deref(),
                    wire,
                )
            } else {
                core::render::render_quality(
                    &r.state.scene,
                    size,
                    views.as_deref(),
                    camera.as_deref(),
                    wire,
                    &quality,
                )
            }
            .map_err(|e| err("RENDER_ERROR", &e))?;
            atomic_write(Path::new(&out), &bytes)?;
            Ok(
                json!({"ok":true,"output":out,"revision":r.id,"render":info,"total_ms":start.elapsed().as_secs_f64()*1000.}),
            )
        }
        "log" | "undo" | "checkout" | "diff" => {
            // Preserve validation-before-lock ordering and legacy writer messages.
            if (command == "undo" && !args.is_empty()) || (command == "checkout" && args.len() != 1)
            {
                return Err(err(
                    "USAGE",
                    "hb undo / hb checkout revision [--scene scene.hb]",
                ));
            }
            let _lock = if command == "undo" || command == "checkout" {
                Some(Lock::acquire(&path)?)
            } else {
                None
            };
            store::revision_command(&command, &args, &path)
        }
        _ => Err(err(
            "UNSUPPORTED_COMMAND",
            &format!("Unknown command '{command}'"),
        )),
    }
}
fn main() {
    let args: Vec<String> = std::env::args().skip(1).collect();
    if args.first().is_some_and(|x| x == "serve")
        && args.len() == 2
        && (args[1] == "--mcp" || args[1] == "--jsonrpc")
    {
        if let Err(e) = server::serve(args[1] == "--mcp") {
            eprintln!("{e}");
            std::process::exit(1);
        }
        return;
    }
    let json_mode = std::env::args().any(|a| a == "--json");
    let code = cli::emit(dispatch(args), json_mode, human);
    if code != 0 {
        std::process::exit(code);
    }
}
fn human(body: &Value) -> bool {
    if body["name"] == "hb" {
        println!(
            "hb {} — headless 3D modeling\n\n{}\n",
            env!("CARGO_PKG_VERSION"),
            body["summary"].as_str().unwrap()
        );
        for line in body["workflow"].as_array().unwrap() {
            println!("• {}", line.as_str().unwrap());
        }
        println!("\n{}", body["compatibility"].as_str().unwrap());
        for field in ["not_implemented", "non_goals", "commands"] {
            let values = body[field]
                .as_array()
                .unwrap()
                .iter()
                .filter_map(Value::as_str)
                .collect::<Vec<_>>()
                .join("; ");
            println!("\n{}: {}", field.replace('_', " "), values);
        }
        println!(
            "\nBudget targets: 60 MB binary; 200 ms first Python; 80 MB empty RSS; 500 ms single-view 512²/~50k triangles.\nDocs: {}",
            body["docs"].as_str().unwrap()
        );

        true
    } else {
        false
    }
}
