# Agent workflow tips from the preview evaluation

These workarounds keep scripts inside the current tested subset. They do not
remove the underlying compatibility gaps or make the checker sound.

- **Read before modeling:** call `hb_capabilities`, then query a focused
  `hb_api` prefix for unfamiliar constructors, modifier parameters or material
  inputs. Full-manifest output is available but often unnecessary.
- **Choose between rebuild and edit:** a successful run persists changes. Clear
  objects explicitly before rebuilding; otherwise new primitives accumulate.
  Use short follow-up scripts to adjust named objects when possible.
- **Use distinct variable names for distinct datablock types:** the checker joins
  assignments conservatively. Reusing `data` for a camera and later a light can
  produce false errors such as `Light.ortho_scale` or `Camera.energy`. Prefer
  `camera_data` and `light_data`.
- **Name lookup is more reliable than string filtering in preflight:**
  `bpy.data.objects['Camera']` is tested. Chained string calls such as
  `obj.name.startswith(...)` can be misclassified as API paths. Use explicit
  known names for preview edits. This is a checker limitation, not a claim that
  Blender strings lack `startswith`.
- **Bevel width is limited by thickness:** a very thin screen or panel may have
  a shortest edge far smaller than its visible width. Keep bevel width strictly
  below half that shortest local edge, or use the tested overlap clamp on a
  canonical cuboid. Inspect segment/UV limits. Apply dimensions first when
  a physical bevel width is needed.
- **Aim a camera with tested math:** create a camera datablock/object, link it,
  assign `scene.camera`, then use `(target - camera.location).to_track_quat('-Z',
  'Y').to_euler()` for XYZ orientation. `scene.camera.name` now passes preflight;
  the pilot's false rejection was fixed before the main evaluation.
- **Inspect the result:** use both the image and `hb_query` bounds/distance/stats.
  A successful render alone does not establish correct dimensions or part count.
  Dim lighting, floating parts and occluded controls can remain in valid scenes.
- **Finish with explicit files:** `hb_export` takes the output path in `args`;
  `hb_render` takes `--out`. Use the same scene path throughout the session.
  Share GLB/PNG outputs, or keep the `.hb` head and revision sidecar together.

The benchmark's structural score only covers its declared checks. General visual
quality, every requested arrangement and unmodified real-world bpy scripts are
separate evaluation questions.
