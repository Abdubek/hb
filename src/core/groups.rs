//! Mesh deform weights and the bounded object vertex-group editing API.
use super::{Scene, Value, id, num, text, unique};
use serde_json::json;

pub fn edit(scene: &mut Scene, key: u64, r: &Value) -> Result<Value, String> {
    let object = scene.object(key)?;
    let mesh_key = id(scene
        .mesh(object)
        .ok_or("Vertex groups require a mesh object")?);
    let mut groups = object
        .get("vertex_groups")
        .and_then(Value::as_array)
        .cloned()
        .unwrap_or_default();
    let mut next = object
        .get("vertex_group_next_id")
        .and_then(Value::as_u64)
        .unwrap_or(0);
    let mesh = scene.get("meshes", mesh_key)?;
    let n = mesh["vertices"].as_array().unwrap().len();
    let mut weights = mesh
        .get("deform_weights")
        .and_then(Value::as_array)
        .cloned()
        .unwrap_or_else(|| vec![json!([]); n]);
    if weights.len() != n {
        return Err("Deform weights do not match mesh vertices".into());
    }
    let action = text(&r["action"]);
    let mut result = Value::Null;
    if action == "new" {
        if groups.len() >= 1024 {
            return Err("At most 1024 vertex groups per object".into());
        }
        let name = if text(&r["name"]).is_empty() {
            "Group"
        } else {
            text(&r["name"])
        };
        let name = unique(name, groups.iter().map(|g| text(&g["name"]).into()));
        groups.push(json!({"key":next,"name":name}));
        result = json!(next);
        next += 1;
    } else if action == "clear" {
        groups.clear();
        weights = vec![json!([]); n];
    } else {
        let group = groups
            .iter()
            .position(|g| g["key"] == r["group"])
            .ok_or("Vertex group has been removed")?;
        match action {
            "rename" => {
                let name = if text(&r["name"]).is_empty() {
                    "Group"
                } else {
                    text(&r["name"])
                };
                groups[group]["name"] = json!(unique(
                    name,
                    groups
                        .iter()
                        .enumerate()
                        .filter(|(i, _)| *i != group)
                        .map(|(_, g)| text(&g["name"]).into())
                ));
            }
            "remove" => {
                groups.remove(group);
                for row in &mut weights {
                    let row = row.as_array_mut().unwrap();
                    row.retain(|pair| pair[0].as_u64() != Some(group as u64));
                    for pair in row {
                        let i = pair[0].as_u64().unwrap();
                        if i > group as u64 {
                            pair[0] = json!(i - 1);
                        }
                    }
                }
            }
            "add" | "remove_weights" => {
                let vertices = r["vertices"]
                    .as_array()
                    .ok_or("Vertex indices must be a sequence")?;
                let indices = vertices
                    .iter()
                    .map(|i| {
                        i.as_u64()
                            .filter(|&v| v < n as u64)
                            .map(|v| v as usize)
                            .ok_or("Vertex group index out of range")
                    })
                    .collect::<Result<Vec<_>, _>>()?;
                let mode = text(&r["mode"]);
                if action == "add" && !["REPLACE", "ADD", "SUBTRACT"].contains(&mode) {
                    return Err(
                        "Vertex-group assignment mode must be REPLACE, ADD or SUBTRACT".into(),
                    );
                }
                let value = num(&r["weight"]) as f32;
                if !value.is_finite() {
                    return Err("Vertex group weight must be finite".into());
                }
                let value = value.clamp(0., 1.);
                for i in indices {
                    let row = weights[i].as_array_mut().unwrap();
                    let at = row
                        .iter()
                        .position(|pair| pair[0].as_u64() == Some(group as u64));
                    if action == "remove_weights" {
                        if let Some(at) = at {
                            row.remove(at);
                        }
                        continue;
                    }
                    let old = at.map(|at| num(&row[at][1]) as f32).unwrap_or(0.);
                    let updated = match mode {
                        "ADD" => (old + value).min(1.),
                        "SUBTRACT" => (old - value).max(0.),
                        _ => value,
                    };
                    if let Some(at) = at {
                        if mode == "SUBTRACT" && updated == 0. {
                            row.remove(at);
                        } else {
                            row[at][1] = json!(updated);
                        }
                    } else if mode != "SUBTRACT" {
                        row.push(json!([group, updated]));
                    }
                }
            }
            _ => return Err("Unknown vertex group edit".into()),
        }
    }
    if weights
        .iter()
        .map(|row| row.as_array().unwrap().len())
        .sum::<usize>()
        > 1_000_000
    {
        return Err("At most one million deform-weight memberships per mesh".into());
    }
    let object = scene.get_mut("objects", key)?;
    object["vertex_groups"] = json!(groups);
    object["vertex_group_next_id"] = json!(next);
    let mesh = scene.get_mut("meshes", mesh_key)?;
    if weights
        .iter()
        .any(|row| !row.as_array().unwrap().is_empty())
    {
        mesh["deform_weights"] = json!(weights);
    } else {
        mesh.as_object_mut().unwrap().remove("deform_weights");
    }
    Ok(result)
}

pub fn weights(mesh: &Value) -> Vec<Vec<(usize, f32)>> {
    let n = mesh["vertices"].as_array().unwrap().len();
    mesh.get("deform_weights")
        .and_then(Value::as_array)
        .map(|rows| {
            rows.iter()
                .map(|row| {
                    row.as_array()
                        .unwrap()
                        .iter()
                        .map(|pair| (pair[0].as_u64().unwrap() as usize, num(&pair[1]) as f32))
                        .collect()
                })
                .collect()
        })
        .unwrap_or_else(|| vec![vec![]; n])
}
pub fn store(mesh: &mut Value, weights: &[Vec<(usize, f32)>]) {
    if weights.iter().any(|row| !row.is_empty()) {
        mesh["deform_weights"] = json!(weights);
    } else {
        mesh.as_object_mut().unwrap().remove("deform_weights");
    }
}

pub fn blend(a: &[(usize, f32)], b: &[(usize, f32)], t: f32) -> Vec<(usize, f32)> {
    let mut out: Vec<_> = a
        .iter()
        .map(|&(group, weight)| {
            (
                group,
                weight * (1. - t)
                    + b.iter()
                        .find(|(g, _)| *g == group)
                        .map(|(_, w)| *w)
                        .unwrap_or(0.)
                        * t,
            )
        })
        .collect();
    for &(group, weight) in b {
        if !a.iter().any(|(g, _)| *g == group) {
            out.push((group, weight * t));
        }
    }
    out
}
pub fn flip_map(object: &Value) -> Vec<usize> {
    let names: Vec<_> = object
        .get("vertex_groups")
        .and_then(Value::as_array)
        .map(|groups| groups.iter().map(|g| text(&g["name"])).collect())
        .unwrap_or_default();
    names
        .iter()
        .enumerate()
        .map(|(i, name)| {
            let (base, suffix) = name
                .rsplit_once('.')
                .filter(|(_, s)| !s.is_empty() && s.bytes().all(|b| b.is_ascii_digit()))
                .map(|(a, b)| (a, format!(".{b}")))
                .unwrap_or((name, String::new()));
            let mut flipped = None;
            for (left, right) in [
                (".L", ".R"),
                ("_L", "_R"),
                ("-L", "-R"),
                (".l", ".r"),
                ("_l", "_r"),
                ("-l", "-r"),
                ("Left", "Right"),
                ("left", "right"),
                ("LEFT", "RIGHT"),
            ] {
                for (from, to) in [(left, right), (right, left)] {
                    if base.len() > from.len()
                        && let Some(prefix) = base.strip_suffix(from)
                    {
                        flipped = Some(format!("{prefix}{to}{suffix}"));
                        break;
                    }
                }
                if flipped.is_some() {
                    break;
                }
            }
            if flipped.is_none() {
                for (left, right) in [
                    ("L.", "R."),
                    ("L_", "R_"),
                    ("L-", "R-"),
                    ("l.", "r."),
                    ("l_", "r_"),
                    ("l-", "r-"),
                    ("Left", "Right"),
                    ("left", "right"),
                    ("LEFT", "RIGHT"),
                ] {
                    for (from, to) in [(left, right), (right, left)] {
                        if base.len() > from.len()
                            && let Some(rest) = base.strip_prefix(from)
                        {
                            flipped = Some(format!("{to}{rest}{suffix}"));
                            break;
                        }
                    }
                    if flipped.is_some() {
                        break;
                    }
                }
            }
            flipped
                .and_then(|f| names.iter().position(|n| **n == f))
                .unwrap_or(i)
        })
        .collect()
}
