use super::*;
fn number(default: f64, min: f64, max: f64) -> Value {
    json!({"type":"number","default":default,"min":min,"max":max})
}
fn integer(default: u64, min: u64, max: u64) -> Value {
    json!({"type":"integer","default":default,"min":min,"max":max})
}
fn vector(default: [f64; 3], min: f64, max: f64) -> Value {
    json!({"type":"vector3","default":default,"min":min,"max":max})
}
fn string(default: &str) -> Value {
    json!({"type":"string","default":default,"max_length":256})
}
fn catalog() -> Vec<Value> {
    vec![
        json!({"name":"housing","description":"Solid rounded enclosure blank, baked dimensions, material and weighted normals. Add openings separately; this is not a hollow shell.","tags":["housing","product","device","box","button","корпус","устройство","кнопка"],"api":["bpy.types.BevelModifier","bpy.types.WeightedNormalModifier"],"parameters":{"name":string("Housing"),"dimensions":vector([2.,1.2,0.45],0.001,100.),"location":vector([0.,0.,0.225],-100.,100.),"bevel":number(0.05,0.,10.),"segments":integer(4,1,8),"color":vector([0.035,0.22,0.38],0.,1.),"metallic":number(0.45,0.,1.),"roughness":number(0.3,0.04,1.)}}),
        json!({"name":"cable","description":"Capped AUTO Bezier cable. Avoid coincident or reversing control points; radius must fit the intended bends.","tags":["cable","wire","hose","curve","кабель","провод","шланг"],"api":["bpy.types.BezierSplinePoint","bpy.types.Curve.use_fill_caps"],"parameters":{"name":string("Cable"),"radius":number(0.04,0.001,1.),"resolution":integer(16,2,64),"profile_resolution":integer(4,0,8),"color":vector([0.06,0.065,0.075],0.,1.),"points":{"type":"points","default":[[-1.,0.,0.2],[-0.4,0.5,0.35],[0.5,-0.4,0.3],[1.,0.,0.2]],"min":-100.,"max":100.,"min_items":2,"max_items":64}}}),
        json!({"name":"label","description":"Centered extruded printable-ASCII label. An explicit static TrueType font path is required. Size and extrusion are independent; thickness is twice extrusion.","tags":["label","text","letter","logo","надпись","текст","буквы"],"api":["bpy.types.TextCurve.extrude","bpy.data.fonts.load"],"parameters":{"name":string("Label"),"text":string("HB"),"font":{"type":"string","required":true,"max_length":4096},"size":number(0.3,0.01,10.),"extrude":number(0.01,0.,1.),"location":vector([0.,0.,0.5],-100.,100.),"rotation":vector([0.,0.,0.],-100.,100.),"color":vector([0.8,0.85,0.9],0.,1.)}}),
        json!({"name":"studio","description":"Orthographic product camera plus warm key, cool fill and rim. Set target to object center and span to its largest dimension; review framing. Adds lights, does not remove existing lights.","tags":["studio","light","camera","render","product","свет","камера","рендер"],"api":["bpy.types.Camera.ortho_scale","bpy.types.Light.use_shadow"],"parameters":{"name":string("Studio"),"target":vector([0.,0.,0.25],-100.,100.),"span":number(2.5,0.01,100.),"shadows":{"type":"boolean","default":true}}}),
    ]
}
pub fn recommend(task: Option<&str>) -> Value {
    let query = task.unwrap_or("").to_lowercase();
    let mut rows = catalog();
    for row in &mut rows {
        let score = row["tags"]
            .as_array()
            .unwrap()
            .iter()
            .filter(|tag| query.contains(tag.as_str().unwrap()))
            .count();
        row["relevance"] = json!(score);
        row["available"] = json!(
            row["api"]
                .as_array()
                .unwrap()
                .iter()
                .all(|p| manifest().accepts(&[p.as_str().unwrap().into()]))
        );
    }
    rows.sort_by_key(|row| std::cmp::Reverse(row["relevance"].as_u64().unwrap()));
    json!(rows)
}
fn valid(value: &Value, rule: &Value) -> bool {
    let scalar = |v: &Value| {
        v.as_f64().is_some_and(|n| {
            n.is_finite()
                && n >= rule["min"].as_f64().unwrap()
                && n <= rule["max"].as_f64().unwrap()
        })
    };
    let vec3 = |v: &Value| {
        v.as_array()
            .is_some_and(|a| a.len() == 3 && a.iter().all(scalar))
    };
    match rule["type"].as_str().unwrap() {
        "number" => scalar(value),
        "integer" => value.as_u64().is_some() && scalar(value),
        "vector3" => vec3(value),
        "boolean" => value.is_boolean(),
        "string" => value.as_str().is_some_and(|s| {
            !s.is_empty()
                && !s.contains('\0')
                && s.chars().count() <= rule["max_length"].as_u64().unwrap() as usize
        }),
        "points" => value.as_array().is_some_and(|a| {
            a.len() >= rule["min_items"].as_u64().unwrap() as usize
                && a.len() <= rule["max_items"].as_u64().unwrap() as usize
                && a.iter().all(vec3)
        }),
        _ => false,
    }
}
pub fn command(mut args: Vec<String>) -> Result<Value, Value> {
    let supplied = take_option(&mut args, "--params")?.unwrap_or("{}".into());
    let out = take_option(&mut args, "--out")?;
    if args.is_empty() || args == ["list"] {
        if supplied != "{}" || out.is_some() {
            return Err(err("USAGE", "recipe list takes no params/output"));
        }
        return Ok(json!({"ok":true,"recipes":recommend(None)}));
    }
    if args.len() != 1 {
        return Err(err(
            "USAGE",
            "hb recipe NAME [--params JSON] [--out script.py]",
        ));
    }
    let spec = catalog()
        .into_iter()
        .find(|r| r["name"] == args[0])
        .ok_or_else(|| err("USAGE", "Unknown recipe; use hb recipe list"))?;
    let supplied: Value = serde_json::from_str(&supplied)
        .map_err(|_| err("USAGE", "Recipe params must be a JSON object"))?;
    let supplied = supplied
        .as_object()
        .ok_or_else(|| err("USAGE", "Recipe params must be a JSON object"))?;
    let rules = spec["parameters"].as_object().unwrap();
    if supplied.keys().any(|k| !rules.contains_key(k)) {
        return Err(err(
            "USAGE",
            "Unknown recipe parameter; inspect recipe list",
        ));
    }
    let mut params = json!({});
    for (name, rule) in rules {
        let value = supplied.get(name).unwrap_or(&rule["default"]);
        if !valid(value, rule) {
            return Err(err(
                "USAGE",
                &format!("Invalid or missing recipe parameter {name}: {rule}"),
            ));
        }
        params[name] = value.clone();
    }
    if args[0] == "label"
        && !params["text"]
            .as_str()
            .unwrap()
            .chars()
            .all(|c| c == '\n' || (' '..='~').contains(&c))
    {
        return Err(err(
            "USAGE",
            "Label supports printable ASCII and newlines only",
        ));
    }
    if args[0] == "housing"
        && params["dimensions"]
            .as_array()
            .unwrap()
            .iter()
            .any(|d| params["bevel"].as_f64().unwrap() >= d.as_f64().unwrap() * 0.5)
    {
        return Err(err(
            "USAGE",
            "Housing bevel must be smaller than half every dimension",
        ));
    }
    let source = match args[0].as_str() {
        "housing" => include_str!("../recipes/housing.py"),
        "cable" => include_str!("../recipes/cable.py"),
        "label" => include_str!("../recipes/label.py"),
        "studio" => include_str!("../recipes/studio.py"),
        _ => unreachable!(),
    };
    let code = format!(
        "# hb recipe: {}\nimport json\n_cfg = json.loads({})\n{}",
        args[0],
        json!(params.to_string()),
        source
    );
    if let Some(out) = &out {
        atomic_write(Path::new(out), code.as_bytes())?;
    }
    Ok(
        json!({"ok":true,"recipe":args[0],"parameters":params,"code":code,"output":out,"next":"Check and run this code, then review the scene. Reusing an existing recipe object name fails instead of duplicating it."}),
    )
}

pub fn summary(task: Option<&str>) -> Value {
    json!(
        recommend(task)
            .as_array()
            .unwrap()
            .iter()
            .map(
                |r| json!({"name":r["name"],"relevance":r["relevance"],"available":r["available"]})
            )
            .collect::<Vec<_>>()
    )
}
