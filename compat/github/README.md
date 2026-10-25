# Supplemental public GitHub cohort

These **19 unchanged full scripts** supplement the original 200 model-generated
scripts; they never enter its denominator or the 2% family-frequency calculation.
Selection was frozen before either engine ran the sources:

- All nine standalone `scripts/*.py` examples from
  [njanakiev/blender-scripting](https://github.com/njanakiev/blender-scripting/tree/477ba73c8578901066cc69be4e0d52fb31cf6530)
  (823 stars at retrieval).
- The lexicographically first ten completed `*_done.py` examples from
  [CGArtPython/blender_plus_python](https://github.com/CGArtPython/blender_plus_python/tree/8082843fa03ebed24f97bd806ae8f05f773e49e9)
  (146 stars at retrieval). `*_done_bpybb.py` is outside that filename rule.

`provenance.json` records commits, source hashes, retrieval time and selection.
Each repository's full MIT license is preserved beside its sources; the first
repository's `utils` module is an unscored dependency. No compatibility edits,
API ports or cuts around unsupported operations are applied. Legacy Blender API
failures, unavailable dependencies, GUI/addon/animation requirements and timeouts
remain measured failures. Popularity is repository-level evidence, not a claim
that every selected script is individually popular or representative of all bpy.

Run `compat/assess_github.py` in the same isolated Blender image as the
independent corpus, with the repository read-only, networking disabled, bounded
CPU/RAM and only its results directory writable. Each process has a 60-second
cap. Blender starts from factory state and can import the preserved sibling
utility; hb uses its documented empty scene and restricted import set. These
execution-context differences are part of the compatibility assessment. The
existing GLB structural scorer is reused when both executions succeed; no visual
or full-topology equivalence claim is made.
