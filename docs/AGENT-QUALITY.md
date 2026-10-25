# Agent quality workflow

hb now exposes a compact, shared CLI/MCP capability catalog, four parameterized
modeling recipes, geometry observations, a visual-review receipt and checked
final delivery. The optional final renderer improves edge sampling, shadows and
diffuse environment lighting. Existing direct run/render/export commands remain
available and retain their default draft rendering behavior.

## Discover and construct

```sh
hb capabilities --task 'product housing cable'
hb recipe list
hb recipe housing --params '{"name":"Housing","dimensions":[2,1.2,0.45]}' --out housing.py
hb check housing.py
hb run housing.py --scene product.hb
hb recipe studio --params '{"target":[0,0,0.225],"span":2.5}' --out studio.py
hb run studio.py --scene product.hb
```

CLI command metadata and MCP descriptions share `src/guidance.rs`. The MCP
initialization response supplies the full workflow from `src/workflow.md`. Feature
entries are included only when their API prefixes exist in the test-generated
manifest; exact parameter limits remain available through `hb api PREFIX`.
Recommendations match task keywords, including a small Russian vocabulary; they
are deterministic hints, not language-model task understanding. `capabilities`
returns a compact recipe index; `recipe list` returns parameter schemas/defaults.

Recipes return Python source without executing it. Parameters are validated
before source generation and encoded as JSON, never interpolated as Python code.
An existing object name causes an atomic run failure rather than duplication.
Recipes are composable; give repeated components distinct names. Changes to a
recipe's original parameters do not automatically update existing objects.

| Recipe | Behavior | Main limits |
| --- | --- | --- |
| housing | Baked dimensions, solid rounded block, material, weighted normals | Convex solid blank; no hollow shell or automatic openings |
| cable | AUTO Bezier path, circular profile, caps, rubber material | Distinct non-reversing points; no self-intersection solver |
| label | Centered extruded text and material | Explicit static TrueType path; printable ASCII; no text bevel |
| studio | Orthographic camera and key/fill/rim sun lights | Set target and span; existing lights are retained |

Use features appropriate to the brief. Deliberate low-poly facets, open sheets,
flat lettering and sharp edges are legitimate choices. More modifiers or polygons
do not by themselves establish higher quality.

## Inspect, view, correct, deliver

```sh
hb inspect --scene product.hb --profile product --size 512
hb review --scene product.hb --profile product --size 512 --out review.json
# Read review.review.png, correct defects, and repeat review after any changes.
# Fill review.assessment_template with actual image observations.
hb deliver --scene product.hb --review review.json --assessment assessment.json --out product.glb
```

For an MCP-only agent, `hb_deliver` also accepts `--assessment-json` followed by
the assessment JSON string, so no shell/file-writing tool is required. Exactly
one assessment input is required. `hb_review` returns the PNG image content as
well as structured data, just like `hb_render`.

Inspection evaluates render-visible geometry and checks empty scenes, degenerate
triangles, edge incidence/orientation, negative closed volume, implicit default
materials, camera-frustum exclusion/cropping and projected text size. Profiles
are `product`, `assembly` and `stylized`; the latter suppresses default-material
warnings. Currently product and assembly use the same checks. Thresholds and
counts are returned with each observation. Text size below 12 pixels is a heuristic,
not OCR. Open/non-manifold/inward surfaces and crop/default-material findings are
warnings because some scenes intentionally contain them. Degenerate triangles
and an empty surface are errors. Self-intersection and occlusion are not tested.
Contact, overlap and distance queries remain separately available.

Review writes a five-view camera/front/right/top/wire contact sheet and a JSON
receipt binding the image SHA-256, scene path, revision, executable hash and API
manifest hash. Fitted technical views automatically frame objects with nonzero extent on all
three world axes, falling back to all geometry when none qualify. This prevents
a large flat backdrop from shrinking the product. All geometry remains rendered;
the active camera is unchanged. `review --focus Housing,Cable` explicitly selects
the fitting bounds instead; names containing commas are not supported by this
option. The heuristic can omit intentionally flat artwork, so use explicit focus
for those cases. The receipt records the selected names.

The receipt includes diagnostics and an assessment template with
brief, silhouette, materials, composition and detail checks. Each passing check
needs a written observation. Every remaining warning needs an explicit reason.

Delivery re-evaluates diagnostics, verifies freshness and rejects unresolved
geometry errors, changed images, stale assessments or unexplained warnings before
export. It writes a `.delivery.json` alongside the export with its hash,
assessment, diagnostics and export warnings. Source scene/history and review
inputs are protected from accidental output overwrites. Review and delivery hold
the scene writer lock while consuming their snapshot.

These checks enforce an explicit current-revision workflow. They cannot prove
that a model looked at an image, understood it, or wrote an honest assessment.
Receipts are local workflow records, not cryptographically authenticated evidence.
The host should accept `deliver` as the final-artifact path, retain the receipt,
and budget the build/review/correct loop (for example, its existing 15 run attempts).
Standard `export` remains usable for intermediate assets and bypasses this gate.

## Final raster quality and curves

`hb render --quality draft` is the unchanged default fast path. `--quality final`
renders each view at twice its requested linear resolution and downsamples using
Lanczos3. Shadow maps use four times the draft linear resolution, with symmetric
bilinear 3x3 PCF. Final shading uses the correct constant viewing direction for
orthographic cameras and geometric face orientation for two-sided shading. Its
normal-aware screen-space ambient occlusion ignores neighbors below the local
tangent plane, reducing false dark bands on convex surfaces. Final views are limited to 1024 pixels (2048 internally), draft
to 2048. The higher quality costs more time and memory; draft budget targets do
not apply to final contact sheets. Bpy's existing render operator stays draft.

Final mode additionally approximates directional diffuse environment light using
low-order spherical harmonics, following the mathematical approach described by
[Ramamoorthi and Hanrahan](https://graphics.stanford.edu/papers/envmap/).
A fixed 64x32 integration grid gives a bounded prefiltering cost; very small bright
features may be missed. The constant environment mean is preserved, including
linear values above 1 in supported generated images. Longitude uses +X at U=0.5,
+Y at U=0.75, and +Z at V=1. This is unoccluded diffuse light: no environment
specular reflections, environment shadow rays, background image or path tracing.
The existing approximate metallic ambient response remains. No numeric error
bound or Cycles equivalence is claimed.

Spatial cyclic POLY/BEZIER tubes now parallel-transport frames and distribute the
remaining loop rotation by arc length. Existing XY-planar reference behavior is
preserved; spatial tessellation is not claimed identical to Blender. Radius and
tilt remain user controls; the method does not repair self-intersecting paths.

The static checker also preserves heterogeneous tuple element positions through
helper returns, aliases, unpacking and constant indexing. It excludes nested
helper returns from the enclosing function's return type. This fixes the native
Bezier handle probe's previous false rejection without executing code or ignoring
unsupported API accesses.

## Evidence and remaining scope

See `tests/test_agent_quality.py`, the environment unit tests and
`compat/quality_eval/README.md`. The latter supplies six development
briefs and a blind pairwise gallery with rating export/scoring. Artistic scores
require real independent judgments. Renderer comparisons are not agent evaluation.

General concave bevel/corner handling, rounded text outlines, Unicode/font shaping,
full environment reflection and path tracing remain separate substantial tasks.
No unrestricted Blender compatibility or superiority benchmark is claimed.
