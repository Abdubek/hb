# hb

Headless 3D modeling with a tested subset of Blender's Python API. Write Python
with `bpy`, build a scene, render a CPU preview, and export a model from one
self-contained executable. The built binary needs no Blender, Python, or GPU.

HB implements its own scene engine in Rust and embeds CPython. It supports part
of `bpy`, `bmesh`, and `mathutils`; it does not run Blender or open `.blend` files.
Use `hb api` for the exact supported API.

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
