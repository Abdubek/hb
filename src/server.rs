use super::*;
fn schema() -> Value {
    json!({"type":"object","properties":{"args":{"type":"array","items":{"type":"string"},"description":"Arguments exactly as for hb <operation>, including flags. Do not include the command itself."},"scene":{"type":"string","description":"Scene file path; defaults to scene.hb"},"code":{"type":"string","description":"Python source for run/check, instead of a file argument"}},"additionalProperties":false})
}
fn operation(command: &str, params: &Value) -> Result<Value, Value> {
    if !guidance::COMMANDS
        .iter()
        .any(|(name, _, _)| *name == command)
    {
        return Err(err("UNSUPPORTED_COMMAND", command));
    }
    if !params.is_object() && !params.is_null() {
        return Err(err("INVALID_PARAMS", "Expected an object"));
    }
    if let Some(fields) = params.as_object() {
        if fields
            .keys()
            .any(|k| !["args", "scene", "code"].contains(&k.as_str()))
        {
            return Err(err(
                "INVALID_PARAMS",
                "Only args, scene and code are accepted",
            ));
        }
        for key in ["scene", "code"] {
            if fields.get(key).is_some_and(|v| !v.is_string()) {
                return Err(err("INVALID_PARAMS", &format!("{key} must be a string")));
            }
        }
    }
    let mut args = match params.get("args") {
        None => vec![],
        Some(v) => v
            .as_array()
            .ok_or_else(|| err("INVALID_PARAMS", "args must be strings"))?
            .iter()
            .map(|v| {
                v.as_str()
                    .map(str::to_owned)
                    .ok_or_else(|| err("INVALID_PARAMS", "args must be strings"))
            })
            .collect::<Result<Vec<_>, _>>()?,
    };
    if let Some(scene) = params["scene"].as_str() {
        args.extend(["--scene".into(), scene.into()]);
    }
    let mut script = None;
    if let Some(code) = params["code"].as_str() {
        if !["run", "check"].contains(&command) {
            return Err(err("INVALID_PARAMS", "code is only valid for run/check"));
        }
        let path = std::env::temp_dir().join(format!("hb-rpc-{}.py", std::process::id()));
        atomic_write(&path, code.as_bytes())?;
        args.insert(0, path.to_string_lossy().into_owned());
        script = Some(path);
    }
    let result = {
        let mut all = vec![command.into()];
        all.extend(args);
        dispatch(all)
    };
    if let Some(path) = script {
        let _ = fs::remove_file(path);
    }
    result
}

use std::io::{BufRead, BufReader, Read};

const MAX_REQUEST_BYTES: u64 = 16 * 1024 * 1024;

#[derive(Debug, PartialEq)]
enum RequestLine {
    Json(Vec<u8>),
    TooLarge,
}

fn read_request(reader: &mut impl BufRead, limit: u64) -> std::io::Result<Option<RequestLine>> {
    let mut line = Vec::new();
    // Limit allocation before reading, including when no newline has arrived yet.
    (&mut *reader).take(limit).read_until(b'\n', &mut line)?;
    if line.is_empty() {
        return Ok(None);
    }
    if line.len() as u64 == limit && line.last() != Some(&b'\n') && !reader.fill_buf()?.is_empty() {
        // Discard without retaining the tail; the next request starts after its newline.
        reader.skip_until(b'\n')?;
        return Ok(Some(RequestLine::TooLarge));
    }
    Ok(Some(RequestLine::Json(line)))
}

fn has_command(name: &str) -> bool {
    guidance::COMMANDS
        .iter()
        .any(|(command, _, _)| *command == name)
}
fn tools() -> Value {
    json!({"tools":guidance::COMMANDS.iter().map(|(name, description, read_only)| json!({
        "name":format!("hb_{name}"),"description":description,
        "inputSchema":schema(),"annotations":{"readOnlyHint":read_only,"openWorldHint":false}
    })).collect::<Vec<_>>()})
}

fn content(command: &str, value: &Value) -> Vec<Value> {
    let mut content = vec![json!({"type":"text","text":value.to_string()})];
    if (command == "render" || command == "review")
        && value["ok"] == true
        && let Some(path) = value[if command == "review" {
            "image"
        } else {
            "output"
        }]
        .as_str()
        && let Ok(bytes) = fs::read(path)
    {
        content.push(json!({"type":"image","mimeType":"image/png","data":base64::Engine::encode(&base64::engine::general_purpose::STANDARD,bytes)}));
    }
    content
}
fn error(id: Value, code: i32, message: &str, data: Option<Value>) -> Value {
    let mut e = json!({"code":code,"message":message});
    if let Some(d) = data {
        e["data"] = d;
    }
    json!({"jsonrpc":"2.0","id":id,"error":e})
}
struct Server {
    mcp: bool,
    initialized: bool,
    ready: bool,
}
impl Server {
    fn operation(&mut self, command: &str, params: &Value, precheck: bool) -> Result<Value, Value> {
        if command == "run" && precheck {
            let value = operation("check", params)?;
            if value["ok"] != true {
                return Ok(value);
            }
        }
        operation(command, params)
    }

    fn message(&mut self, r: Value) -> Option<Value> {
        if !r.is_object()
            || r["jsonrpc"] != "2.0"
            || !r["method"].is_string()
            || r.get("id")
                .is_some_and(|v| !v.is_null() && !v.is_string() && !v.is_number())
        {
            return Some(error(Value::Null, -32600, "Invalid Request", None));
        }
        let id = r.get("id").cloned();
        let method = r["method"].as_str().unwrap();
        let p = &r["params"];
        if id.is_none() {
            if self.mcp && method == "notifications/initialized" && self.initialized {
                self.ready = true;
            }
            if !self.mcp && has_command(method) {
                let _ = self.operation(method, p, false);
            }
            return None;
        }
        let id = id.unwrap();
        let response = if self.mcp {
            match method {
                "initialize" => {
                    if self.initialized {
                        return Some(error(id, -32600, "Already initialized", None));
                    }
                    if !p["protocolVersion"].is_string()
                        || !p["clientInfo"].is_object()
                        || !p["capabilities"].is_object()
                    {
                        return Some(error(id, -32602, "Invalid initialize parameters", None));
                    }
                    self.initialized = true;
                    Ok(
                        json!({"protocolVersion":"2025-11-25","capabilities":{"tools":{"listChanged":false}},"serverInfo":{"name":"hb","version":env!("CARGO_PKG_VERSION")},"instructions":include_str!("workflow.md")}),
                    )
                }
                "ping" => Ok(json!({})),
                _ if !self.ready => {
                    return Some(error(
                        id,
                        -32000,
                        "Initialize and send notifications/initialized first",
                        None,
                    ));
                }
                "tools/list" => Ok(tools()),
                "tools/call" => {
                    let name = p["name"].as_str().unwrap_or("");
                    let Some(command) = name.strip_prefix("hb_").filter(|c| has_command(c)) else {
                        return Some(error(id, -32602, "Unknown tool name", None));
                    };
                    let value = match self.operation(command, &p["arguments"], true) {
                        Ok(v) => v,
                        Err(e) => json!({"ok":false,"error":e}),
                    };
                    let content = content(command, &value);
                    Ok(
                        json!({"content":content,"structuredContent":value,"isError":value["ok"]==false}),
                    )
                }
                _ => return Some(error(id, -32601, "Method not found", None)),
            }
        } else {
            if !has_command(method) {
                return Some(error(id, -32601, "Method not found", None));
            }
            self.operation(method, p, false)
        };
        Some(match response {
            Ok(result) => json!({"jsonrpc":"2.0","id":id,"result":result}),
            Err(e) => error(id, -32000, "Operation failed", Some(e)),
        })
    }
}
pub fn serve(mcp: bool) -> Result<(), String> {
    let stdin = std::io::stdin();
    let mut reader = BufReader::new(stdin.lock());
    let stdout = std::io::stdout();
    let mut out = stdout.lock();
    let mut server = Server {
        mcp,
        initialized: false,
        ready: false,
    };
    while let Some(line) =
        read_request(&mut reader, MAX_REQUEST_BYTES).map_err(|e| e.to_string())?
    {
        let response = match line {
            RequestLine::TooLarge => {
                Some(error(Value::Null, -32600, "Request exceeds 16 MB", None))
            }
            RequestLine::Json(line) => {
                if line.iter().all(u8::is_ascii_whitespace) {
                    continue;
                }
                match serde_json::from_slice::<Value>(&line) {
                    Err(_) => Some(error(Value::Null, -32700, "Parse error", None)),
                    Ok(Value::Array(batch)) => {
                        if mcp || batch.is_empty() {
                            Some(error(
                                Value::Null,
                                -32600,
                                "Batch unsupported in MCP; JSON-RPC batches must not be empty",
                                None,
                            ))
                        } else {
                            let responses: Vec<_> = batch
                                .into_iter()
                                .filter_map(|r| server.message(r))
                                .collect();
                            if responses.is_empty() {
                                None
                            } else {
                                Some(json!(responses))
                            }
                        }
                    }
                    Ok(v) => server.message(v),
                }
            }
        };
        if let Some(response) = response {
            writeln!(out, "{response}").map_err(|e| e.to_string())?;
            out.flush().map_err(|e| e.to_string())?;
        }
    }
    Ok(())
}

#[cfg(test)]
mod tests {
    use super::*;
    use std::io::Cursor;

    #[test]
    fn request_limit_includes_newline_and_accepts_eof() {
        for input in [b"{} \n".as_slice(), b"null", b"{}", b"\n"] {
            let mut reader = Cursor::new(input);
            assert_eq!(
                read_request(&mut reader, 4).unwrap(),
                Some(RequestLine::Json(input.to_vec()))
            );
            assert_eq!(read_request(&mut reader, 4).unwrap(), None);
        }
    }

    #[test]
    fn oversized_request_is_drained_before_next_line() {
        // A one-byte input buffer also exercises delimiters at buffer boundaries.
        let mut reader = BufReader::with_capacity(1, Cursor::new(b"null\n123456789\n{}\n"));
        for _ in 0..2 {
            assert_eq!(
                read_request(&mut reader, 4).unwrap(),
                Some(RequestLine::TooLarge)
            );
        }
        assert_eq!(
            read_request(&mut reader, 4).unwrap(),
            Some(RequestLine::Json(b"{}\n".to_vec()))
        );
        assert_eq!(read_request(&mut reader, 4).unwrap(), None);
    }

    #[test]
    fn oversized_request_without_newline_is_drained_to_eof() {
        let mut reader = Cursor::new(b"123456789");
        assert_eq!(
            read_request(&mut reader, 4).unwrap(),
            Some(RequestLine::TooLarge)
        );
        assert_eq!(read_request(&mut reader, 4).unwrap(), None);
    }
}
