# hb

Headless 3D modeling with a tested subset of Blender's Python API. Write Python
with `bpy`, build a scene, render a CPU preview, and export a model from one
self-contained executable. The built binary needs no Blender, Python, or GPU.

HB implements its own scene engine in Rust and embeds CPython. It supports part
of `bpy`, `bmesh`, and `mathutils`; it does not run Blender or open `.blend` files.
Use `hb api` for the exact supported API.

## Why HB

- **Small deployment:** an **8.7 MB executable** in the measured macOS arm64
  release build, including embedded Python. Copy the binary and run it; no
  Blender installation, Python environment, GPU, or model-provider account is
  required at runtime.
- **Quick iteration:** about **33 ms to start and execute `import bpy`**, and
  **32 ms to build and export a cube**, in the local benchmark below. This keeps
  short modeling steps inexpensive when an agent repeatedly edits a scene.
- **Discoverable API:** `capabilities` explains the workflow and `api PREFIX`
  returns only the relevant tested API entries and parameter limits. Agents can
  look up an operation without loading the full Blender API into context.
- **Structured feedback:** CLI, JSON-RPC, and MCP expose the same operations.
  Errors include codes, source locations, and suggestions; MCP renders return
  PNG image content alongside structured results.
- **Recoverable edits:** seeded runs, revision IDs, history, diffs, undo, and
  checkout. Failed scripts leave the saved scene head unchanged.
- **Inspect before delivery:** query dimensions, hierarchy, distances, overlaps,
  and camera framing. `review` produces a contact sheet and diagnostics;
  `deliver` requires a current review and an explicit assessment before export.
  Parameterized recipes cover housings, cables, labels, and studio lighting.

These features support a discover → model → inspect → render → correct loop.
They give an agent concrete tools and feedback; model success rates and artistic
quality still depend on the task and the agent's decisions.

## What it can build

| Area | Supported features |
| --- | --- |
| Modeling | Mesh primitives, editable meshes, extrusion, inset, joins, welding, triangulation; bounded bevel, boolean, subdivision, array, mirror, solidify, displace, and weighted normals |
| Assembly | Named objects, collections, parenting, transforms, cameras, and lights |
| Curves and text | POLY/Bezier paths and tubes; extruded printable-ASCII text with an explicit static TrueType font |
| Materials | Color, metallic, roughness, emission, transparency, and a limited set of image/normal-map and environment nodes |
| Preview | CPU rasterization, multiple views, contact sheets, wireframe, and supersampled final previews |
| Import | GLB/glTF, including Meshopt, OBJ, STL, and PLY |
| Export | GLB, self-contained glTF, OBJ with MTL, and USDZ |

Each feature has bounds on parameters, topology, or node graphs. Read
[`hb api` and the compatibility contract](docs/compatibility.md) for those limits.

## Size and speed

Measured on **Apple M2 Pro, 16 GiB RAM, macOS arm64**, using HB 0.18.0 and
Blender 5.2.3 LTS on 26 October 2026:

| Measurement | HB | Background Blender |
| --- | ---: | ---: |
| Executable size | **8.68 MB** | 182.93 MB, plus required libraries and data |
| Fresh process + `import bpy` | **33 ms** | 706 ms |
| Fresh process + one cube → GLB | **32 ms** | 690 ms |
| Peak resident memory, cube → GLB | **17.2 MB** | 250.4 MB |

For this small workload, HB took roughly **1/22 of the time** and **1/15 of the
resident memory**. A single-view 512×512 HB draft preview of the cube took
**88 ms**, including process startup. These timings measure launch overhead and
one simple asset; complex modeling has a different cost profile. HB previews
use its own rasterizer and do not promise Cycles or EEVEE image parity.

Times and peak memory are medians of 10 fresh processes after one warmup, with
warm filesystem caches; Blender uses one thread. Both export runs clear the
scene and build the same cube; HB additionally saves its scene revision. MB
means 1,000,000 bytes. Build options and platform change the executable size.
[Raw measurements and methodology](docs/benchmarks/macos-arm64.json) are retained.

Reproduce on your own machine:

```sh
python3 scripts/benchmark.py --hb target/release/hb \
  --blender /absolute/path/to/blender --runs 10 --out outputs/benchmark.json
```

Omit `--blender` to measure HB alone.

## Blender compatibility

The manifest currently declares **645 tested API entries** across `bpy`,
`bmesh`, and `mathutils`, with **81 executable Rust contract tests**. Entries
include operators, types, properties, and methods; this count is not a percentage
of Blender's API. The subset covers the modeling workflow above. The retained
[Blender reference report](compat/golden-report.json) records 236/236 passing
comparisons for an earlier, selected regression suite against Blender 4.5.9 LTS.

**Existing Blender scripts often need adaptation.** A fresh static-only check
with HB 0.18.0 accepted **11 of 400 unchanged external/model-authored scripts
(2.75%)** in the [retained corpus](compat/corpus/README.md).
[Per-script results](docs/benchmarks/corpus-preflight.json) include every source,
including scripts previously found invalid in Blender. This is checker
acceptance, not execution, geometry, rendering, or error-equivalence coverage.
It is separate from the selected regression suite above.

For agents, the intended workflow is to read `hb capabilities`, consult the
needed `hb api PREFIX` entries, and author within that contract. `hb check`
finds unsupported uses before execution, while runtime validation enforces
geometry and parameter limits. Static analysis can still miss dynamic uses or
reject valid patterns.

HB does not support `.blend` files, the Blender GUI, Cycles/EEVEE, arbitrary
addons or node graphs, Geometry Nodes, rigging, animation, simulation, sculpting,
or full Blender lifecycle and exception parity. See the detailed
[compatibility contract](docs/compatibility.md).

Recheck the corpus without executing its scripts:

```sh
python3 scripts/benchmark.py --corpus-preflight --out outputs/corpus-preflight.json
```

## Build

Requires stable Rust, a C/C++ compiler, `make`, `curl`, and Python 3.11+ for
development scripts. On macOS, install Xcode Command Line Tools. Supported build
platforms are macOS arm64 and Linux x86_64.

```sh
git clone https://github.com/Abdubek/hb.git
cd hb
./scripts/build.sh
./target/release/hb capabilities
```

The first build downloads and compiles pinned CPython 3.13.7. Subsequent builds
reuse it. Set `HB_BUILD_JOBS` to control CPython build parallelism, or
`HB_PYTHON_SOURCE` to use an existing compatible static CPython build.

## Use

```sh
./target/release/hb check examples/cube.py
./target/release/hb run examples/cube.py --scene cube.hb --out cube.glb
./target/release/hb render --scene cube.hb --out cube.png
./target/release/hb query stats --scene cube.hb
./target/release/hb api bpy.types.BevelModifier
```

Keep `cube.hb` and `cube.hb.revisions/` together: the head file points to snapshots
in that directory. Runs edit the existing scene; `undo`, `checkout`, `log`, and
`diff` provide revision history.

The explicit output paths of `render`, `export`, and `run --out` cannot target
the scene head or anything inside its revision directory, including through
absolute paths, `..`, or symlink aliases. OBJ's companion MTL path is checked too.
A conflicting destination returns `USAGE` before those outputs are written.

Import GLB/glTF, OBJ, STL, or PLY; export GLB/glTF, OBJ, or USDZ. Renders are CPU
previews. See the [quickstart](docs/QUICKSTART.md) and
[compatibility contract](docs/compatibility.md) for supported features and limits.

## Agents

HB also works as a stdio MCP or JSON-RPC server:

```sh
./target/release/hb serve --mcp
./target/release/hb serve --jsonrpc
```

Point your client at the absolute executable path with arguments
`["serve", "--mcp"]` and a writable working directory. Start with `hb_capabilities`
and `hb_api`. See the [modeling workflow](docs/AGENT-QUALITY.md) and
[workflow tips](docs/AGENT-TIPS.md). Embedded Python executes local scripts; isolate
untrusted scripts in the calling application.

Both stdio servers accept one JSON message per line, up to 16 MiB including the
newline. HB bounds the input buffer while reading and discards oversized lines
without executing them. It returns JSON-RPC error `-32600` with a null ID, then
continues with the next line. This limits request buffering, not script memory
or execution time.

## Development

```sh
cargo fmt --check
cargo test --locked --release
python3 -m unittest discover -s tests
python3 scripts/generate_manifest.py --check
```

One Cargo package builds one binary. `src/` holds the CLI, server, and scene
engine; `pyshim/` implements the Python API; `recipes/` contains modeling recipes.
`tests/` and `compat/` hold regression tests, Blender reference tools, and fixtures.
`third_party/` contains the native geometry dependencies.

## License

[MIT](LICENSE). Third-party code and compatibility samples retain their own
licenses; see [THIRD_PARTY.md](THIRD_PARTY.md).
