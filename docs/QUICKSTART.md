# Try the hb preview

hb is a standalone headless 3D engine. This preview can build, inspect, render
and export scenes with a tested subset of Blender Python. It is not a drop-in
replacement for Blender. The manifest defines the supported subset.

## Start

Build HB using the [repository instructions](../README.md#build), then
use `target/release/hb`. A packaged executable needs no Blender, Python or GPU
installation. The commands below assume that executable is `./hb`.

```sh
./hb capabilities
./hb api --json
```

## Write a small scene

Save this as `my_scene.py`:

```python
import bpy
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)
bpy.ops.mesh.primitive_cube_add(location=(0, 0, 0.5))
box = bpy.context.object
box.name = 'Blue housing'
box.scale = (1.2, 0.8, 0.5)
material = bpy.data.materials.new('Blue paint')
material.diffuse_color = (0.08, 0.25, 0.65, 1)
box.data.materials.append(material)
```

```sh
./hb check my_scene.py
./hb run my_scene.py --scene my_scene.hb --out my_scene.glb
./hb render --scene my_scene.hb --out my_scene.png
./hb log --scene my_scene.hb
```

Use meters and radians. Camera forward is local −Z and up is +Y. A scene with no
lights uses hb's studio lighting; a missing active camera gets a fitted preview.

## Use an agent

Register a stdio MCP server in your agent client with an **absolute** executable
path and a writable scene working directory:

```json
{
  "mcpServers": {
    "hb": {
      "command": "/absolute/path/to/hb",
      "args": ["serve", "--mcp"]
    }
  }
}
```

A useful first prompt is:

> Read hb_capabilities, then build a small desk with named parts. Consult hb_api
> before using unfamiliar operations. Use hb_run with a scene path, render and
> inspect the contact sheet, check dimensions with hb_query, then export a GLB.

`hb_run` automatically checks scripts before executing. Tool responses include
structured errors and renders include PNG images. Query and revision operations
use the same scene path. Embedded Python executes local scripts. Run untrusted scripts inside an isolated
environment supplied by the calling application.

See [agent workflow tips](AGENT-TIPS.md) for checker workarounds and common
modeling errors observed during evaluation.

## Keep and share your work

Keep `my_scene.hb` and **`my_scene.hb.revisions/` together**. The first is a small
head pointer; the directory holds its revisions. To share only the resulting
model, send the GLB and PNG instead. The preview does not publish artifacts or
send them to anyone automatically.

A failed script leaves the saved head unchanged. `hb undo --scene my_scene.hb`
restores its parent; `hb checkout REVISION --scene my_scene.hb` restores a named
revision from `hb log`. Optional export and head updates are not one cross-file
transaction, so check command results when automating artifact delivery.

## Know the limits

- Read `hb api bpy.types.BevelModifier` (or another dotted prefix) for tested
  parameters. Familiar Blender names do not imply every mode is implemented.
- Import GLB/glTF (including Meshopt), OBJ, STL or PLY; export GLB/glTF, OBJ or
  USDZ. Bounded bpy glTF/OBJ I/O and `render.render` are also available.
- Curves support POLY and BEZIER paths with optional tube end caps; Text supports
  extrusion. Nonempty Text requires an explicit static
  TrueType font and printable ASCII. Inspect the manifest before using either.
- World supports Background inputs; materials support Principled, Image Texture
  and one Mapping/TexCoord chain. Advanced texture assets require glTF export.
- Bevel supports closed convex meshes; concave/open meshes, arbitrary graphs,
  constraints, Draco/KTX2/EXR and full
  method/operator/type/error parity remain excluded.
- `hb check` can miss dynamic API uses and cannot prove geometry eligibility.
  Treat runtime errors as unsupported work to correct, not warnings to ignore.
- CPU renders are deterministic previews, not EEVEE or Cycles output. The fixed
  512²/~50k-triangle budget does not guarantee every scene or contact sheet is
  below 500 ms. Images used by the preview/export are quantized to 8-bit channels;
  it is not an HDR texture rendering pipeline.
- These packages target Linux x86_64 and macOS arm64 only; no Windows binary is
  included. The macOS binary uses system libraries and is not notarized; macOS
  may require local approval before it runs after downloading.

See the detailed [compatibility contract](compatibility.md). Report the failing
script, `hb capabilities` version, command/error JSON and expected behavior when
requesting a compatibility increment. Remove private assets before sharing a
reproduction.
