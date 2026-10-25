# Independent model-authored corpus

These scripts are original outputs from Claude Opus 5 and GPT-6 Astra, generated
from varied hard-surface, product, architecture and scene-assembly prompts.
The original collection records retain each prompt, raw provider response,
requested/observed model identity, usage and script SHA-256 in `traces/`.
The authors receive no hb manifest, capabilities, implementation or checker
results. Generated source files are retained unchanged; execution validity and
compatibility must be measured separately. A successful generation is not a
Blender pass, hb pass or agent-assessment success.

This collection is distinct from the 200-script synthetic seed in `compat/corpus`.
The held-out 30-task MCP agent assessment remains separate and has not run yet.

The initial 15 scripts all fail preflight against the preserved v0.12.0 binary.
Frequent gaps include Vector.to_track_quat/Quaternion conversion, object
size/dimensions, textured BEVEL, camera/light creation operators, world color and
WEIGHTED_NORMAL. Several of these conflict with the original strict whitelist;
the user approved expanding the tested whitelist based on this evidence,
while preserving the major non-goals. Do not silently omit failing scripts or rewrite them to inflate scores.
