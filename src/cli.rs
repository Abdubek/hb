//! Command-line arguments, JSON output and atomic file writes.
use serde_json::{Value, json};
use std::io::{IsTerminal, Write};

type ErrorRenderer = fn(&str, &str) -> Value;

pub fn emit(
    answer: Result<Value, Value>,
    json_mode: bool,
    human: impl FnOnce(&Value) -> bool,
) -> i32 {
    let body = match answer {
        Ok(value) => value,
        Err(error) => json!({"ok": false, "error": error}),
    };
    if std::io::stdout().is_terminal() && !json_mode {
        if !human(&body) {
            println!("{}", serde_json::to_string_pretty(&body).unwrap());
        }
    } else if let Err(error) = writeln!(std::io::stdout().lock(), "{body}") {
        if error.kind() == std::io::ErrorKind::BrokenPipe {
            return 0;
        }
        eprintln!("Could not write response: {error}");
        return 1;
    }
    i32::from(body["ok"] == false)
}

pub fn take_option(
    args: &mut Vec<String>,
    flag: &str,
    error: ErrorRenderer,
) -> Result<Option<String>, Value> {
    if let Some(i) = args.iter().position(|x| x == flag) {
        args.remove(i);
        if i >= args.len() {
            return Err(error("USAGE", &format!("{flag} requires a value")));
        }
        Ok(Some(args.remove(i)))
    } else {
        Ok(None)
    }
}

pub fn take_flag(args: &mut Vec<String>, flag: &str) -> bool {
    if let Some(i) = args.iter().position(|x| x == flag) {
        args.remove(i);
        true
    } else {
        false
    }
}

pub fn atomic_write(path: &std::path::Path, data: &[u8]) -> std::io::Result<()> {
    let parent = path
        .parent()
        .filter(|p| !p.as_os_str().is_empty())
        .unwrap_or(std::path::Path::new("."));
    let name = path
        .file_name()
        .ok_or_else(|| std::io::Error::other("Expected a file path"))?
        .to_string_lossy();
    let temp = parent.join(format!(".{name}.{}.tmp", std::process::id()));
    let mut file = std::fs::OpenOptions::new()
        .write(true)
        .create_new(true)
        .open(&temp)?;
    let result = (|| {
        file.write_all(data)?;
        file.sync_all()?;
        std::fs::rename(&temp, path)
    })();
    if result.is_err() {
        let _ = std::fs::remove_file(temp);
    }
    result
}
