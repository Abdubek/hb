# Visual modeling evaluation

The older assembly benchmark measures structural acceptance, not image quality.
This pack adds six development briefs, a visual rubric and blind pairwise review.
These briefs were written during feature development and are **not a held-out test set**.

For an agent comparison, run the same model, task, assets, seed where applicable,
output resolution and time/tool budget in both environments. Preserve every first
attempt and failure. Record engine/binary/model versions, source scripts, calls,
errors, elapsed time and reported cost. Make exported geometry and camera views
available alongside the hero image. A timeout remains a failure, not a omitted pair.
Use an independent holdout set before claiming a general improvement.

For hb with the new workflow, instruct the host to read capabilities for the task,
inspect recipe parameters, model, review the returned image, correct concrete
issues within its existing run budget, and deliver with an assessment. The host
must retain the delivery JSON. The assessment is the agent's judgment, not an
independent evaluator. Standard export remains available for intermediate assets.

A useful three-way experiment is the previous agent instructions, the new workflow
on hb, and the same model using Blender. The gallery accepts arbitrary pairs from
real artifacts, including those experiments. It does not run external model CLIs
or assume credentials, quotas, installed Blender, or a model version.

```sh
python3 compat/quality_eval/gallery.py build pairs.json --out blind-review
python3 compat/quality_eval/gallery.py score \
  --key blind-review/key.json --ratings ratings.json > preference-report.json
```

`pairs.json` contains `pairs`, each with `id`, `brief`, optional `rubric`, and `a` /
`b` records containing `label`, `image` (relative PNG path), optional measured
`seconds` and any retained provenance. `index.html` embeds images, randomizes side
assignment, saves rating drafts in browser storage, and downloads ratings. Keep
`key.json` away from raters until scoring. Use multiple independent raters for
stronger evidence; report ties/neither and failures. Do not interpret a few
preferences as statistical proof or replace unfavorable first attempts.

Renderer-only draft/final comparisons demonstrate raster differences, not better
agent modeling and not superiority to Blender. No model or human preference
results are fabricated by this tooling.

For a reproducible authored renderer demo (no external model calls):

```sh
python3 scripts/demo_agent_quality.py --out outputs/agent-quality-demo
```

This retains source, CLI responses, a GLB, a review receipt, measured draft/final
frames and a blind gallery. It stops before delivery because a real viewer must
supply an assessment; it never fills visual judgments automatically.
