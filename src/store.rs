use super::*;
use flate2::{Compression, read::ZlibDecoder, write::ZlibEncoder};
use serde::{Deserialize, Serialize};
use std::io::Read;
#[derive(Clone, Serialize, Deserialize)]
#[serde(deny_unknown_fields)]
pub struct State {
    pub scene: Scene,
}
#[derive(Clone, Serialize, Deserialize)]
pub struct Revision {
    pub format: String,
    pub id: String,
    pub parent: Option<String>,
    pub script: String,
    pub seed: u64,
    #[serde(flatten)]
    pub state: State,
}
// Preserve the original strict decoder's field names and diagnostic wording.
mod wire {
    use super::{Deserialize, Scene};
    #[derive(Deserialize)]
    #[serde(deny_unknown_fields)]
    pub(super) struct Revision {
        pub(super) format: String,
        pub(super) id: String,
        pub(super) parent: Option<String>,
        pub(super) script: String,
        pub(super) seed: u64,
        pub(super) scene: Scene,
    }
}
pub fn history(path: &Path) -> PathBuf {
    PathBuf::from(format!("{}.revisions", path.display()))
}
fn decode(bytes: &[u8]) -> Result<Revision, Value> {
    let bytes = if bytes.starts_with(b"HBR1") {
        let mut b = vec![];
        ZlibDecoder::new(&bytes[4..])
            .take(256 * 1024 * 1024 + 1)
            .read_to_end(&mut b)
            .map_err(ioerr)?;
        if b.len() > 256 * 1024 * 1024 {
            return Err(err(
                "INVALID_SCENE",
                "Snapshot exceeds 256 MB decoded limit",
            ));
        }
        b
    } else {
        bytes.to_vec()
    };
    let v: Value =
        serde_json::from_slice(&bytes).map_err(|e| err("INVALID_SCENE", &e.to_string()))?;
    if v["format"] == "hb-m0-v1" {
        let old: core::legacy::Scene = serde_json::from_value(v["scene"].clone())
            .map_err(|e| err("INVALID_SCENE", &e.to_string()))?;
        old.validate().map_err(|e| err("INVALID_SCENE", &e))?;
        let parent = v["parent"].as_str().map(str::to_string);
        let script = v["script"]
            .as_str()
            .ok_or_else(|| err("INVALID_SCENE", "Missing source"))?
            .to_string();
        let seed = v["seed"]
            .as_u64()
            .ok_or_else(|| err("INVALID_SCENE", "Missing seed"))?;
        let id = old.revision(&script, parent.as_deref(), seed);
        if v["id"] != id {
            return Err(err("INVALID_SCENE", "M0 hash mismatch"));
        }
        return Ok(Revision {
            format: "hb-m0-v1".into(),
            id,
            parent,
            script,
            seed,
            state: State {
                scene: Scene::migrate(old).map_err(|e| err("INVALID_SCENE", &e))?,
            },
        });
    }
    let wire: wire::Revision =
        serde_json::from_value(v).map_err(|e| err("INVALID_SCENE", &e.to_string()))?;
    let r = Revision {
        format: wire.format,
        id: wire.id,
        parent: wire.parent,
        script: wire.script,
        seed: wire.seed,
        state: State { scene: wire.scene },
    };
    r.state
        .scene
        .validate()
        .map_err(|e| err("INVALID_SCENE", &e))?;
    if r.format != "hb-m1-v1"
        || r.id
            != r.state
                .scene
                .revision(&r.script, r.parent.as_deref(), r.seed)
    {
        return Err(err("INVALID_SCENE", "Revision hash or format mismatch"));
    }
    Ok(r)
}
pub fn revision(path: &Path, id: &str) -> Result<Revision, Value> {
    if id.len() != 64 || !id.bytes().all(|c| c.is_ascii_hexdigit()) {
        return Err(err(
            "INVALID_REVISION",
            "Expected a complete 64-character revision id",
        ));
    }
    for ext in ["hbr", "json"] {
        let p = history(path).join(format!("{id}.{ext}"));
        if p.exists() {
            let r = decode(&fs::read(p).map_err(ioerr)?)?;
            if r.id != id {
                return Err(err("INVALID_SCENE", "Snapshot name/hash mismatch"));
            }
            return Ok(r);
        }
    }
    Err(err("REVISION_NOT_FOUND", id))
}
pub fn load(path: &Path) -> Result<Option<Revision>, Value> {
    if !path.exists() {
        return Ok(None);
    }
    let b = fs::read(path).map_err(ioerr)?;
    let v: Value = serde_json::from_slice(&b).map_err(|e| err("INVALID_SCENE", &e.to_string()))?;
    if v["format"] == "hb-head-v1" {
        Ok(Some(revision(
            path,
            v["revision"]
                .as_str()
                .ok_or_else(|| err("INVALID_SCENE", "Missing head revision"))?,
        )?))
    } else {
        Ok(Some(decode(&b)?))
    }
}
pub fn atomic_write(path: &Path, data: &[u8]) -> Result<(), Value> {
    crate::cli::atomic_write(path, data).map_err(ioerr)
}
pub fn point_head(path: &Path, id: &str) -> Result<(), Value> {
    atomic_write(
        path,
        &serde_json::to_vec(&json!({"format":"hb-head-v1","revision":id})).unwrap(),
    )
}
pub fn save(path: &Path, r: &Revision) -> Result<(), Value> {
    fs::create_dir_all(history(path)).map_err(ioerr)?;
    if path.exists() {
        let bytes = fs::read(path).map_err(ioerr)?;
        if let Ok(v) = serde_json::from_slice::<Value>(&bytes)
            && v["format"] == "hb-m0-v1"
        {
            let old = decode(&bytes)?;
            let entry = history(path).join(format!("{}.json", old.id));
            if !entry.exists() {
                atomic_write(&entry, &bytes)?;
            }
        }
    }
    let entry = history(path).join(format!("{}.hbr", r.id));
    if !entry.exists() {
        let mut z = ZlibEncoder::new(vec![], Compression::fast());
        serde_json::to_writer(&mut z, r).map_err(|e| err("IO_ERROR", &e.to_string()))?;
        let mut bytes = b"HBR1".to_vec();
        bytes.extend(z.finish().map_err(ioerr)?);
        atomic_write(&entry, &bytes)?;
    } else {
        revision(path, &r.id)?;
    }
    point_head(path, &r.id)
}
pub struct Lock {
    path: PathBuf,
}
impl Lock {
    pub fn acquire(scene: &Path) -> Result<Self, Value> {
        let path = PathBuf::from(format!("{}.lock", scene.display()));
        let mut f=fs::OpenOptions::new().write(true).create_new(true).open(&path).map_err(|e|if e.kind()==std::io::ErrorKind::AlreadyExists{err("SCENE_BUSY","Scene has a writer lock; retry after it completes. Remove a stale .lock only after confirming its recorded PID is no longer running.")}else{ioerr(e)})?;
        f.write_all(std::process::id().to_string().as_bytes())
            .map_err(ioerr)?;
        Ok(Self { path })
    }
}
impl Drop for Lock {
    fn drop(&mut self) {
        let _ = fs::remove_file(&self.path);
    }
}

pub fn revision_command(command: &str, args: &[String], path: &Path) -> Result<Value, Value> {
    match command {
        "log" => {
            if !args.is_empty() {
                return Err(err("USAGE", "hb log [--scene scene.hb]"));
            }
            let mut current = required(path)?;
            let mut revisions = Vec::new();
            loop {
                let parent = current.parent.clone();
                revisions.push(json!({"revision":current.id,"parent":parent,"script":current.script,"seed":current.seed}));
                match parent {
                    Some(id) => current = revision(path, &id)?,
                    None => break,
                }
            }
            Ok(json!({"ok":true,"revisions":revisions}))
        }
        "undo" | "checkout" => {
            let current = required(path)?;
            let id = if command == "undo" {
                current
                    .parent
                    .ok_or_else(|| err("NO_PARENT", "Already at the first revision"))?
            } else {
                args[0].clone()
            };
            let value = revision(path, &id)?;
            point_head(path, &value.id)?;
            Ok(json!({"ok":true,"revision":value.id}))
        }
        "diff" => {
            if args.len() != 2 {
                return Err(err(
                    "USAGE",
                    "hb diff revision_a revision_b [--scene scene.hb]",
                ));
            }
            let before = revision(path, &args[0])?;
            let after = revision(path, &args[1])?;
            Ok(
                json!({"ok":true,"from":before.id,"to":after.id,"changes":changes(&before.state.scene,&after.state.scene)}),
            )
        }
        _ => unreachable!(),
    }
}
