//! Shared CLI/MCP guidance, tied to the tested symbol manifest.
use super::*;
pub const COMMANDS: &[(&str, &str, bool)] = &[
    (
        "run",
        "Execute Python after MCP preflight; edits the existing scene and commits only on success. Clear objects explicitly when rebuilding. Follow with review before delivery.",
        false,
    ),
    (
        "check",
        "Check supported API use without execution; acceptance does not prove arbitrary Python or geometry validity.",
        true,
    ),
    (
        "render",
        "Render a PNG contact sheet and return its image. args: [--out, preview.png, --size, 512, --quality, final]; views include iso or camera. draft preserves the fast preview; final supersamples edges.",
        false,
    ),
    (
        "query",
        "Inspect geometry: stats, tree, bbox --all, distance A B, overlaps, floating, inside A B, visible --camera Camera. Contact and bounding tests do not prove artistic quality.",
        true,
    ),
    (
        "import",
        "Import GLB/glTF (including Meshopt), OBJ, STL or PLY. args: [asset.glb]. Commits a revision.",
        false,
    ),
    (
        "export",
        "Export GLB, self-contained glTF, OBJ with MTL, or USDZ. args: [output.glb]. For reviewed final artifacts use deliver.",
        false,
    ),
    (
        "api",
        "Read exact tested API and limits. args: [bpy.types.BevelModifier] for one prefix; [] for the full manifest.",
        true,
    ),
    (
        "capabilities",
        "Read workflow and manifest-backed features. args: [--task, product housing cable] ranks relevant recipes; inspect recipe parameters before use.",
        true,
    ),
    (
        "recipe",
        "Get a tested, parameterized bpy recipe without executing it. args: [list] or [housing, --params, JSON]. Returns code, defaults, limits and required APIs; --out writes a Python file.",
        false,
    ),
    (
        "inspect",
        "Diagnose evaluated geometry and square-camera framing. args: [--profile, product, --size, 512, --camera, Camera]. Profiles: product, assembly, stylized. Warnings are observations, not automatic edits.",
        true,
    ),
    (
        "review",
        "Create a revision-bound contact sheet and diagnostics. args: [--out, review.json, --profile, product, --size, 512]. Inspect the returned image; fix issues and repeat if needed. Receipt records hashes; it does not prove image comprehension.",
        false,
    ),
    (
        "deliver",
        "Export after a current review and explicit visual assessment. args: [--review, review.json, --assessment-json, JSON, --out, result.glb]. Rejects stale revisions, changed images, geometry errors and unacknowledged warnings. See review.assessment_template.",
        false,
    ),
    (
        "diff",
        "Compare two saved revisions. args: [revisionA, revisionB].",
        true,
    ),
    ("undo", "Restore the parent revision. args: [].", false),
    (
        "checkout",
        "Restore a saved revision. args: [revision].",
        false,
    ),
    ("log", "List scene revision history. args: [].", true),
    (
        "licenses",
        "Read bundled engine and dependency license notices.",
        true,
    ),
];
pub fn capabilities(task: Option<&str>) -> Value {
    let mut commands: Vec<_> = COMMANDS.iter().map(|(n, _, _)| *n).collect();
    commands.extend(["serve --jsonrpc", "serve --mcp"]);
    let mut features = vec![];
    for (name, prefix, use_for) in [
        (
            "bevel",
            "bpy.types.BevelModifier",
            "Round closed convex solid edges; inspect width, angle and attribute limits. Concave/open general bevel remains unsupported.",
        ),
        (
            "bezier",
            "bpy.types.BezierSplinePoint",
            "Smooth cables and paths with FREE/VECTOR/AUTO/ALIGNED handles.",
        ),
        (
            "solid_text",
            "bpy.types.TextCurve.extrude",
            "Solid printable-ASCII labels from an explicit static TrueType font; no text bevel or default Bfont.",
        ),
        (
            "weighted_normals",
            "bpy.types.WeightedNormalModifier",
            "Keep broad hard-surface faces visually flat after compatible modeling operations.",
        ),
        (
            "materials",
            "bpy.types.Material",
            "Set surface color, roughness and metallic response; preview has bounded lighting and scattering.",
        ),
        (
            "boolean",
            "bpy.types.BooleanModifier",
            "Cut or combine eligible closed solids; inspect topology and attributes afterward.",
        ),
        (
            "subdivision",
            "bpy.types.SubsurfModifier",
            "Smooth supported cage geometry; inspect silhouette and dimensions afterward.",
        ),
    ] {
        let contract = manifest().filter(prefix);
        if !contract["symbols"].as_object().unwrap().is_empty() {
            features.push(json!({"name":name,"api":prefix,"use_for":use_for,"contract":contract}));
        }
    }
    // Keep the initial response small; exact limits remain retrievable by prefix.
    for feature in &mut features {
        feature.as_object_mut().unwrap().remove("contract");
    }
    json!({
        "name":"hb","version":env!("CARGO_PKG_VERSION"),
        "milestone":"Reviewed modeling workflow; manifest defines the supported subset",
        "summary":"Native 3D modeling, parameterized recipes, visual review and revision-bound delivery with a tested bpy subset.",
        "commands":commands,"features":features,"recipes":recipes::summary(task),
        "workflow":[
            "Read task-relevant capabilities and recipe parameters. Look up exact API limits with hb api PREFIX.",
            "Choose useful features for the requested style; every object does not need bevel, subdivision or maximum detail.",
            "Build named parts in meters/radians. Recipes return code and never execute implicitly. Runs edit the existing scene.",
            "Use materials and a deliberate camera/light rig. Camera forward is local -Z, up +Y.",
            "Run review to inspect topology and obtain camera/front/right/top/wire images of the current revision.",
            "Read the image and judge brief, silhouette, materials, composition and detail. Correct concrete defects; repeat within the host's time/call budget.",
            "Use deliver with the current receipt and a written assessment. Keep unresolved limitations explicit; do not claim Blender/Cycles parity.",
            "Keep scene.hb and scene.hb.revisions together; undo/checkout recover saved revisions."
        ],
        "compatibility":"Partial compatibility with Blender. Static checks do not prove arbitrary Python or valid geometry. Review diagnostics cannot determine aesthetics or prove that an agent viewed an image.",
        "not_implemented":["NURBS and default Bfont rendering","concave/open general mesh bevel; rounded text outlines","constraints/depsgraph, full Blender lifecycle","arbitrary shaders and path tracing","Draco/KTX2/EXR"],
        "non_goals":["GUI or .blend files","sculpting, rigging, animation, simulation","Geometry Nodes, addons or arbitrary compositor"],
        "budget_targets":{"binary_bytes":60000000,"first_python_ms":200,"empty_rss_bytes":80000000,"preview_ms":500},
        "budget_scope":"Draft 512px single view, approximately 50k triangles; final supersampling and review take more work. Measurements are separate from targets.",
        "docs":"docs/AGENT-QUALITY.md; docs/compatibility.md"
    })
}
