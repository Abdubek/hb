# Real-source compatibility corpus

The corpus contains 400 sources: 150 new Claude Opus 5 scripts, 150 new
GPT-6 Astra scripts, 92 Blender StackExchange snippets and 8 MIT-licensed gist
scripts. `index.json` is the authoritative sample
list; files in `tools/`, prompts, raw responses and historical metadata are not
samples. The historical synthetic fixtures now live separately in
`compat/seed-corpus/`; `scripts/generate_corpus.py` regenerates only that directory.

Each author receives 150 distinct scene/modeling tasks. Neither the implementation,
existing corpus nor compatibility feedback is supplied. The two models receive
the same task list, initially in independent batches of five. Incomplete provider
requests are retried individually; completed script outputs are never retried in
response to compatibility results. Successful prompts, source payloads, event
types and extraction manifests are retained under `acquisition/`. Failed attempts,
duplicate process logs, provider session identifiers and billing telemetry were
removed for public distribution.
JSON decoding is the only transformation of model source. Mistakes, deprecated
APIs and inconsistent Blender assumptions are deliberately preserved.

Public gist files require an explicit license in the same gist or source file.
The manifest records the source URL, pinned raw URL, author, original filename,
license evidence and SHA-256. An unrelated repository or gist license is not
treated as permission. The source request separately names Blender StackExchange
answers, which retain their original CC BY-SA 3.0/4.0 share-alike licenses and
attribution. The permissive-software-license filter applies to gists. The answer
snippets are not labeled MIT or public domain; each has an attribution notice,
license URL, revision-history URL and an answer snapshot. Personal paths in the
published snapshots have been redacted.

Validation uses Blender 4.5.9 LTS, either in a read-only, network-disabled
container with only this corpus mounted read-only, or the checksum-verified
native macOS build under `sandbox-exec`. Scripts run from factory startup, with
their own scene setup intact. Rendering invoked by a public script is not removed
or stubbed out. Each source's original bytes are checked before and after
execution. Original Python exceptions and source-triggered native crashes move a
file to `invalid/`; timeouts and infrastructure failures remain unresolved.
Crash records identify the process signal separately from Python exceptions.

The checker is the binary built from this branch. Invalid-script runtime checks
also use that binary, with writes restricted to a fresh temporary directory and
network disabled. A separate probe compiles the unchanged original source under
its original filename to observe the Python exception class that hb's normal
JSON omits. The probe must agree with the direct run's message and source line
before its class is used. An unsupported API error earlier in the script is a
mismatch, not matching rejection.

The symbol census instruments a copy of the current static checker's AST in
memory, observing its resolved paths without executing the corpus source. It
counts each symbol once per script and includes aliases inferred through helper
functions. It inherits the checker's limitations for classes, closures, dynamic
Python and nonconverging inference; it is not an exhaustive dynamic API trace.
Parameter restrictions are separate entries. The 2% cutoff includes equality,
and its denominator includes invalid scripts. `hb check` acceptance is not a
runtime, mesh or rendering equivalence score.

Reproduction (from repository root, authenticated model CLIs required):

```sh
python3 compat/corpus/tools/acquire_models.py --claude /path/to/claude --codex /path/to/codex
CARGO_TARGET_DIR=/tmp/corpus-real-build HB_PYTHON_SOURCE=/path/to/Python-3.13.7 cargo build --release --offline
python3 compat/corpus/tools/measure.py --hb /tmp/corpus-real-build/release/hb --blender /path/to/Blender --timeout 3600
PYTHONDONTWRITEBYTECODE=1 python3 compat/corpus/tools/audit.py --check
python3 compat/corpus/tools/assert_error_parity.py
```

The measurement command requires Docker and the
`vide-hb-blender-compat:latest` image, or `--blender /path/to/Blender` for the native
reference. macOS `sandbox-exec` isolates native execution. The final validation
uses native Blender, with download URL and hashes in `acquisition/environment.json`.
`results/*/record.json` retains commands, engine and source hashes and process
output with personal home paths replaced by `/workspace` or `/user-home`. The parity gate fails for mismatches; it does not accept an
earlier unsupported API error as equivalent. The previous synthetic corpus's
per-script frequency baseline is historical metadata only, not a source sample.

`compat/coverage.py` and `compat/verify.py --corpus` exercise only the separate
synthetic seed regression suite. Use this directory's measurement tool for the
full indexed real-source sample, including `invalid/`. Its recorded error-parity
gate still fails for 96 of the 102 invalid scripts; the provenance audit does not
claim compatibility. The retained measurement evidence predates the merge.

## Publication redactions

All 300 model-generated scripts retain their source bytes. One public sample,
`invalid/stackexchange-24139-block-2.py`, replaces a personal home path with
`/user-home`. Its `index.json` entry records the published `sha256`, the historical
`original_sha256` and the transformation. The related answer snapshot uses the
same redaction; author, source URL and CC BY-SA attribution are preserved.

Historical validation still refers to the original input hash. The audit verifies
the published source against the redacted snapshot and records consistency with
the historical input hash separately; it does not claim the edited input was
rerun. Per-process output is embedded in each final `record.json`, so duplicate
stdout/stderr files and intermediate `previous-*` records are not distributed.
