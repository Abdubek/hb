# Preview MCP workflow benchmark

This is a **constrained assembly/workflow benchmark**, not a measurement of
unrestricted Blender compatibility or the original visual-modeling success gate.
Thirty tasks are defined in `tasks.json`. Each requires named meshes, two assigned
materials, an active camera, geometry queries, a GLB and a 512px preview. Models
receive these acceptance criteria and can read hb capabilities and the manifest.
The first three families were used for a development pilot; the set is not fully
held out. Do not label its structural success rate as the original M3 80% score.

`run.py` uses authenticated local Claude and GPT-6 CLIs, installed under
`.build/eval-tools`. These are evaluation instruments, not implementation agents.
It does not install tools or expose the source checkout to the model's engine.
`proxy.py` forwards the real MCP protocol to a networkless, read-only-root Docker
container, with only the task's artifact directory writable. It records requests,
responses and image hashes, and limits each session to 15 run attempts and 100
MCP calls. Model-side non-MCP tool use must be checked in the retained traces.

Provide a Docker image containing the HB executable as its entrypoint, tagged
`hb:local`, before running this optional benchmark.

```sh
python3 compat/agent_eval/run.py --image hb:local \
  --out .build/my-agent-eval --limit 30 --workers 4
python3 compat/agent_eval/score.py --out .build/my-agent-eval \
  --hb target/release/hb
```

The runner resolves the image tag to an immutable image ID and records input
hashes. Each provider session has a 15-minute deadline; Claude also has a $3 cap.
Raw traces, failures and incomplete attempts are retained. An incomplete attempt
must use another output directory to retry; do not silently overwrite it. A
provider timeout/failure remains in the score. Do not rerun failed tasks to replace
first-attempt outcomes. Score only after the intended number of tasks completes.

`score.py` inspects saved geometry and exported GLB, checks materials and active
camera and required parts intersecting its frustum (not occlusion), queries
evaluated finite bounds, validates selected dimension/placement
requirements and verifies PNG dimensions. It requires successful MCP query,
render and export calls and does not trust the model's final success statement.
It reports first-run execution separately from full-task structural success;
an executable first scene is not necessarily a completed task. Total run attempts
include failed preflight and later corrections. Visual recognition, arrangements
not covered by the few geometric predicates, aesthetics and pixel parity need
separate human review. Scene names alone cannot establish those properties.

A camera-frustum audit was added while the main run was underway to enforce the
already-published aimed-camera requirement. Earlier provisional scores are
preserved separately; final scores use the recorded scorer hash.
