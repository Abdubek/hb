"""Validate only provenance-indexed sources, retaining every original byte.

Blender executes in a network-disabled read-only container. hb check and invalid
runtime checks use the exact checkout's binary. Results include command output,
source/binary hashes, invalid error parity and static symbol census limitations.
"""
import argparse
import ast
import collections
import concurrent.futures
import hashlib
import json
import re
from pathlib import Path
import subprocess
import tempfile
import time
import uuid

CORPUS = Path(__file__).resolve().parents[1]
REPO = CORPUS.parents[1]
RUNNER_HASH = hashlib.sha256(Path(__file__).read_bytes().split(b"\ndef census(", 1)[0] + (CORPUS / "tools/blender_reference.py").read_bytes()).hexdigest()


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def run(command, cwd, dest, timeout):
    started = time.monotonic()
    try:
        result = subprocess.run(command, cwd=cwd, capture_output=True, timeout=timeout)
        code, out, err = result.returncode, result.stdout, result.stderr
    except subprocess.TimeoutExpired as error:
        code, out, err = "timeout", error.stdout or b"", error.stderr or b""
    dest.with_suffix(".stdout").write_bytes(out)
    dest.with_suffix(".stderr").write_bytes(err)
    return {"returncode": code, "seconds": time.monotonic() - started,
            "command": command, "stdout": out.decode(errors="replace"), "stderr": err.decode(errors="replace")}


def check_json(process):
    try:
        return json.loads(process["stdout"])
    except ValueError:
        return {"ok": False, "infrastructure_error": True}


def measure(entry, args, engine_hash):
    runner_hash = RUNNER_HASH
    path = CORPUS / entry["file"]
    if not path.exists():
        path = CORPUS / "invalid" / path.name
    assert digest(path) == entry["sha256"], path
    dest = CORPUS / "results" / path.stem
    dest.mkdir(parents=True, exist_ok=True)
    prior = dest / "record.json"
    if prior.exists():
        record = json.loads(prior.read_text())
        if record["source_sha256"] == entry["sha256"] and record["engine_sha256"] == engine_hash and record.get("runner_sha256") == runner_hash and record.get("reference") == (args.blender or args.image) and not record["blender"].get("infrastructure_error"):
            return record
        (dest / f"previous-{time.time_ns()}.json").write_bytes(prior.read_bytes())
    work = Path(tempfile.mkdtemp(prefix="corpus-check-")).resolve()
    record = {"file": str(path.relative_to(CORPUS)), "source_sha256": digest(path), "engine_sha256": engine_hash, "runner_sha256": runner_hash, "reference": args.blender or args.image}
    record["check_process"] = run([args.hb, "check", str(path)], work, dest / "check", args.timeout)
    record["check"] = check_json(record["check_process"])
    container = "corpus-" + uuid.uuid4().hex
    command = ["docker", "run", "--rm", "--name", container, "--platform", "linux/amd64",
               "--network", "none", "--read-only", "--cpus", "2", "--memory", "2g",
               "--pids-limit", "128", "--cap-drop", "ALL", "--security-opt", "no-new-privileges",
               "--tmpfs", "/tmp:rw,size=512m", "-e", "HOME=/tmp", "-w", "/tmp",
               "-v", f"{CORPUS}:/corpus:ro", args.image,
               "/opt/blender/blender", "-b", "--factory-startup", "-t", "1", "--python-exit-code", "1",
               "--python", "/corpus/tools/blender_reference.py", "--", "/corpus/" + str(path.relative_to(CORPUS))]
    if args.blender:
        profile = '(version 1)(allow default)(deny network*)(deny file-write*)(allow file-write* (subpath ' + json.dumps(str(work)) + ') (literal "/dev/null") (literal "/dev/dtracehelper"))'
        command = ["env", "TMPDIR=" + str(work), "sandbox-exec", "-p", profile, args.blender, "-b", "--factory-startup", "-t", "1", "--python-exit-code", "1", "--python", str(CORPUS / "tools/blender_reference.py"), "--", str(path)]
    reference_timeout = max(args.timeout, args.public_timeout) if entry["provider"] == "github-gist" else args.timeout
    record["blender_process"] = run(command, work, dest / "blender", reference_timeout)
    if record["blender_process"]["returncode"] == "timeout" and not args.blender:
        subprocess.run(["docker", "rm", "-f", container], capture_output=True)
    markers = [line[len("CORPUS_RESULT="):] for line in record["blender_process"]["stdout"].splitlines()
               if line.startswith("CORPUS_RESULT=")]
    record["blender"] = json.loads(markers[-1]) if markers else {
        "ok": False, "infrastructure_error": True, "message": "No reference result (timeout/process failure)"}
    if not markers and args.blender and record["blender_process"]["returncode"] in (-4, -6, -7, -8, -11):
        record["blender"] = {"ok": False, "failure_kind": "process_signal", "signal": -record["blender_process"]["returncode"], "message": "Blender process terminated by signal " + str(-record["blender_process"]["returncode"])}
        crash = work / "blender.crash.txt"
        if crash.exists():
            (dest / "blender.crash.txt").write_bytes(crash.read_bytes())
    if record["blender"].get("exception") or record["blender"].get("signal"):
        profile = '(version 1)(allow default)(deny network*)(deny file-write*)(allow file-write* (subpath ' + json.dumps(str(work)) + ') (literal "/dev/null") (literal "/dev/dtracehelper"))'
        record["runtime_process"] = run(["sandbox-exec", "-p", profile, args.hb, "run", str(path), "--scene", str(work / "scene.hb")],
                                         work, dest / "runtime", args.timeout)
        record["runtime"] = check_json(record["runtime_process"])
        error = record["runtime"].get("error", {})
        probe = work / "exception_probe.py"
        probe.write_text("import json\nsource = " + repr(str(path)) + "\n" + '''try:
    with open(source, 'r', encoding='utf-8', newline='') as handle:
        original = handle.read()
    exec(compile(original, source, 'exec'), {'__name__': '__main__', '__file__': source})
except BaseException as error:
    line = getattr(error, 'lineno', None)
    tb = error.__traceback__
    while tb:
        if tb.tb_frame.f_code.co_filename == source:
            line = tb.tb_lineno
        tb = tb.tb_next
    print('CORPUS_HB_EXCEPTION=' + json.dumps({'exception': type(error).__name__, 'message': str(error), 'line': line}))
    raise
''')
        record["runtime_probe_process"] = run(["sandbox-exec", "-p", profile, args.hb, "run", str(probe), "--scene", str(work / "probe.hb")], work, dest / "runtime-probe", args.timeout)
        markers = [line[len("CORPUS_HB_EXCEPTION="):] for line in record["runtime_probe_process"]["stderr"].splitlines() if line.startswith("CORPUS_HB_EXCEPTION=")]
        record["runtime_exception"] = json.loads(markers[-1]) if markers else {}
        exception = record["runtime_exception"]
        consistent_probe = bool(exception) and exception.get("message") == error.get("message") and str(exception.get("line")) == str(error.get("location", "")).rsplit(":", 1)[-1]
        record["error_parity"] = {
            "hb_rejected": record["runtime"].get("ok") is False,
            "same_message": error.get("message") == record["blender"].get("message"),
            "same_line": str(error.get("location", "")).rsplit(":", 1)[-1] == str(record["blender"].get("line")),
            "probe_matches_direct_run": consistent_probe,
            "same_exception_class": exception.get("exception") == record["blender"].get("exception") if consistent_probe else None}
        parity = record["error_parity"]
        parity["status"] = ("same_error" if parity["hb_rejected"] and parity["same_message"] and parity["same_line"] and parity["same_exception_class"] else "different_error") if consistent_probe else "unresolved"
        invalid = CORPUS / "invalid" / path.name
        invalid.parent.mkdir(exist_ok=True)
        if path != invalid:
            path.rename(invalid)
        record["file"] = "invalid/" + path.name
    elif record["blender"].get("ok") and path.parent == CORPUS / "invalid":
        valid_path = CORPUS / path.name
        if valid_path.exists():
            assert digest(valid_path) == entry["sha256"]
        path.rename(valid_path)
        record["file"] = valid_path.name
    assert digest(CORPUS / record["file"]) == entry["sha256"]
    prior.write_text(json.dumps(record, indent=2) + "\n")
    return record


def census(path):
    """Observe resolved AST paths using the checkout's checker without running source."""
    source = (REPO / "pyshim/checker.py").read_text()
    tree = ast.parse(source)
    hook = ast.parse("""
for observed_node in ast.walk(tree):
    if isinstance(observed_node, (ast.Attribute, ast.Name)):
        for observed_path in resolve(observed_node):
            if observed_path.startswith(('bpy.', 'bmesh.', 'mathutils.')):
                OBSERVED.add(observed_path)
""").body
    for node in tree.body:
        if isinstance(node, ast.FunctionDef) and node.name == "_check_tree":
            node.body[-1:-1] = hook
    ast.fix_missing_locations(tree)
    class Unsupported(Exception):
        suggestion = doc = ""
    namespace = {"ast": ast, "MANIFEST": json.loads((REPO / "compat/manifest.json").read_text()),
                 "UnsupportedError": Unsupported, "OBSERVED": set()}
    exec(compile(tree, "<corpus checker instrumentation>", "exec"), namespace)
    namespace["check"](path.read_text(), str(path))
    return namespace["OBSERVED"]


def report(entries, records, args, engine_hash):
    # A successful direct hb run is a resolved mismatch against a Blender error;
    # it correctly has no exception marker. This is evidence classification only.
    for record in records:
        if "error_parity" in record and record.get("runtime", {}).get("ok") is True and record["runtime_process"]["returncode"] == 0:
            record["error_parity"].update(status="different_error", reason="hb succeeded while Blender failed")
            (CORPUS / "results" / Path(record["file"]).stem / "record.json").write_text(json.dumps(record, indent=2) + "\n")
    by_name = {Path(r["file"]).name: r for r in records}
    symbols, unsupported, unresolved = collections.Counter(), collections.Counter(), collections.Counter()
    rows = []
    for entry in entries:
        record = by_name[entry["file"]]
        row = dict(entry, file=record["file"], validation="results/" + Path(record["file"]).stem + "/record.json")
        found = census(CORPUS / row["file"])
        missing = {e["message"].split(":", 1)[0] for e in record["check"].get("errors", [])
                   if e["code"] == "UNSUPPORTED_API"}
        missing = {s for s in missing if s.startswith(("bpy.", "bmesh.", "mathutils."))}
        uncertain = {e["message"].split(":", 1)[0] for e in record["check"].get("errors", []) if e["code"] == "STATIC_UNRESOLVED"}
        symbols.update(sorted(found | missing))
        unsupported.update(sorted(missing))
        unresolved.update(sorted(uncertain))
        row.update(symbols=sorted(found | missing), unsupported=sorted(missing), unresolved=sorted(uncertain))
        rows.append(row)
    n = len(entries)
    composition = collections.Counter(e["provider"] for e in entries)
    passes = sum(r["check"].get("ok") is True and r["check_process"]["returncode"] == 0 for r in records)
    valid = sum(r["blender"].get("ok") is True for r in records)
    invalid = sum(bool(r["blender"].get("exception") or r["blender"].get("signal")) for r in records)
    incomplete = n != 400 or composition["claude"] != 150 or composition["gpt6"] != 150
    result = {"kind": "fresh verbatim model outputs and explicitly licensed public scripts",
              "complete": not incomplete, "target": {"claude": 150, "gpt6": 150, "public": 100},
              "composition": dict(composition), "scripts": rows}
    (CORPUS / "index.json").write_text(json.dumps(result, indent=2) + "\n")
    summary = {"scripts": n, "composition": dict(composition), "hb_check_pass": passes,
               "blender_pass": valid, "blender_invalid": invalid, "blender_unresolved": n - valid - invalid,
               "engine_sha256": engine_hash, "symbol_frequency": dict(symbols.most_common()),
               "unsupported_frequency": dict(unsupported.most_common()), "unresolved_frequency": dict(unresolved.most_common())}
    summary["unique_source_hashes"] = len({e["sha256"] for e in entries})
    summary["public_licenses"] = dict(collections.Counter(e["license"] for e in entries if "license" in e))
    summary["composition_results"] = {}
    for provider in ("claude", "gpt6", "blender-stackexchange", "github-gist"):
        group = [by_name[e["file"]] for e in entries if e["provider"] == provider]
        summary["composition_results"][provider] = {"scripts": len(group), "blender_pass": sum(r["blender"].get("ok") is True for r in group), "hb_check_pass": sum(r["check"].get("ok") is True for r in group)}
    summary["invalid_error_mismatches"] = [r["file"] for r in records if r.get("error_parity", {}).get("status") == "different_error"]
    summary["invalid_same_error"] = [r["file"] for r in records if r.get("error_parity", {}).get("status") == "same_error"]
    summary["blender_crashes"] = [r["file"] for r in records if r["blender"].get("signal")]
    summary["invalid_error_unresolved"] = [r["file"] for r in records if r.get("error_parity", {}).get("status") == "unresolved"]
    summary["census_syntax_error_scripts"] = [r["file"] for r in records if any(e.get("code") == "SYNTAX_ERROR" for e in r["check"].get("errors", []))]
    baseline = json.loads((CORPUS / "acquisition/synthetic-baseline.json").read_text())
    mapping = json.loads((CORPUS / "tools/backlog-map.json").read_text())
    crossings = []
    for symbol, count in unsupported.most_common():
        old_count = baseline["symbol_frequency"].get(symbol, 0)
        if count * 100 >= 2 * n and old_count * 100 < 2 * baseline["scripts"]:
            coverage = next((m["coverage"] for m in mapping if re.search(m["pattern"], symbol)), None)
            crossings.append({"symbol": symbol, "scripts": count, "percent": 100 * count / n,
                              "previous_percent": 100 * old_count / baseline["scripts"], "backlog": coverage})
    summary["threshold_crossings"] = crossings
    summary["threshold_crossings_not_in_backlog"] = [c for c in crossings if c["backlog"] is None]
    summary["backlog_sha256"] = digest(REPO / "docs/COMPATIBILITY-BACKLOG.md")
    (CORPUS / "coverage.json").write_text(json.dumps(summary, indent=2) + "\n")
    text = ["# Real-source corpus coverage", "", "Status: " + ("**Incomplete acquisition; these are provisional measurements.**" if incomplete else "400 scripts acquired."), "",
            "| Origin | Scripts | Blender pass | hb check pass |", "|---|---:|---:|---:|"]
    names = {"claude": "Claude Opus 5", "gpt6": "GPT-6 Astra", "blender-stackexchange": "Blender StackExchange", "github-gist": "GitHub gists"}
    text += [f"| {names[p]} | {r['scripts']} | {r['blender_pass']} | {r['hb_check_pass']} |" for p, r in summary["composition_results"].items()]
    licenses = summary["public_licenses"]
    text += ["", f"Public licenses: {licenses.get('MIT', 0)} MIT gist files, {licenses.get('CC BY-SA 4.0', 0)} CC BY-SA 4.0 answer snippets and {licenses.get('CC BY-SA 3.0', 0)} CC BY-SA 3.0 answer snippets. The original share-alike licenses apply to the explicitly requested StackExchange sources; the permissive-license filter applies to gists. Per-file attribution, license URLs and snapshots are in the index and acquisition records.", "",
            f"`hb check`: **{passes}/{n} ({passes / n:.2%})**. Blender 4.5.9 LTS: {valid} pass, {invalid} invalid ({len(summary['blender_crashes'])} process crashes), {n-valid-invalid} unresolved process outcomes.", "",
            "The denominator is every acquired script, including invalid ones. Frequencies count distinct scripts, once per symbol per script. Exactly 2% belongs to the at-or-above group. These are preflight results, not runtime or geometry equivalence.", "",
            "Symbols use the current checker's static alias/type inference. Dynamic Python and unparsed syntax cannot be exhaustively enumerated. Parameter restrictions remain separate entries. Inferred parent paths appear alongside member paths; their percentages must not be summed. `bpy.types.IDData` is a checker placeholder for object data, not a Blender RNA type; its member paths retain that inference limitation.", "",
            f"{len(summary['census_syntax_error_scripts'])} syntax-error scripts remain in the denominator but have no resolved AST census; see `corpus/coverage.json` for their filenames. Unsupported tables report checker diagnostics, which can include false positives from type inference. In particular, `bpy.types.MeshPolygon.inputs[.default_value]` and `bpy.types.ShaderNode.use_smooth` reflect the checker conflating variables named `p` used for shader nodes and mesh polygons; these reported paths are not real RNA members. They remain visible as checker defects, not API implementation requests.", "",
            "Invalid scripts remain byte-identical under `corpus/invalid/`. Each record contains Blender's exception and a direct hb runtime result. A second hb probe compiles the original unchanged source under its original filename and observes the exception class; its message and line must agree with the direct run before classification. Timeouts and infrastructure failures are unresolved, not script errors.", "",
            f"Invalid error comparisons: {len(summary['invalid_same_error'])} identical class/message/line; {len(summary['invalid_error_mismatches'])} different errors; {len(summary['invalid_error_unresolved'])} unresolved. The requested same-error requirement is unmet wherever the errors differ; fixing hb is outside the permitted paths.", "",
            f"hb SHA-256: `{engine_hash}`. Source hashes, prompts, responses, licenses and complete process logs are under `corpus/`.", "",
            "## Top 20 unsupported symbols", "", "| Symbol / restriction | Scripts | % |", "|---|---:|---:|"]
    text += [f"| `{s}` | {c} | {100*c/n:.2f}% |" for s, c in unsupported.most_common(20)]
    text += ["", "## At or above 2%", "", "| Symbol / restriction | Scripts | % | Unsupported in scripts |", "|---|---:|---:|---:|"]
    text += [f"| `{s}` | {c} | {100*c/n:.2f}% | {unsupported[s]} |" for s, c in symbols.most_common() if c * 100 >= 2 * n]
    text += ["", "## Below 2%", "", "| Symbol / restriction | Scripts | % | Unsupported in scripts |", "|---|---:|---:|---:|"]
    text += [f"| `{s}` | {c} | {100*c/n:.2f}% | {unsupported[s]} |" for s, c in symbols.most_common() if c * 100 < 2 * n]
    text += ["", "## Unresolved static paths", "", "These `STATIC_UNRESOLVED` diagnostics still reject preflight, but are not counted as confirmed unsupported symbols or new API backlog demands.", "", "| Diagnostic path | Scripts | % |", "|---|---:|---:|"]
    text += [f"| `{s}` | {c} | {100*c/n:.2f}% |" for s, c in unresolved.most_common()]
    text += ["", "## Backlog comparison", "",
             "These checker-reported unsupported paths newly reach 2% compared with the historical synthetic baseline, recomputed using the same per-script counting method. This measures a change of corpus, not a compatibility regression. Mapping is to named entries in `docs/COMPATIBILITY-BACKLOG.md`; broad statements that all Blender RNA is unsupported do not count as a specific backlog entry. Static inference may report paths that are not real Blender members; inspect the recorded diagnostics before scheduling implementation.", "",
             "| Newly ≥2% unsupported path | Previous % | New % | Backlog coverage |", "|---|---:|---:|---|"]
    text += [f"| `{c['symbol']}` | {c['previous_percent']:.2f}% | {c['percent']:.2f}% | {c['backlog'] or '**Not listed**'} |" for c in crossings]
    text += ["", "The full symbol tables include supported paths; supported symbols do not require backlog entries. The mapping rules are preserved in `corpus/tools/backlog-map.json`.", ""]
    (REPO / "compat/COVERAGE.md").write_text("\n".join(text))
    return summary


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--hb", required=True)
    parser.add_argument("--image", default="vide-hb-blender-compat:latest")
    parser.add_argument("--blender", help="Optional native Blender 4.x executable; runs under sandbox-exec")
    parser.add_argument("--timeout", type=int, default=120)
    parser.add_argument("--public-timeout", type=int, default=900)
    parser.add_argument("--workers", type=int, default=4)
    parser.add_argument("--models-only", action="store_true")
    parser.add_argument("--public-only", action="store_true")
    parser.add_argument("--no-report", action="store_true")
    parser.add_argument("--file", action="append", help="Measure only this source basename; repeatable")
    args = parser.parse_args()
    args.hb = str(Path(args.hb).resolve())
    engine_hash = digest(Path(args.hb))
    entries = [row for p in sorted((CORPUS / "acquisition").glob("**/manifest.json"))
               for row in json.loads(p.read_text())["scripts"]]
    if args.models_only:
        entries = [e for e in entries if e["provider"] in ("claude", "gpt6")]
    if args.public_only:
        entries = [e for e in entries if e["provider"] not in ("claude", "gpt6")]
    if args.file:
        entries = [e for e in entries if Path(e["file"]).name in args.file]
    assert entries and len({e["file"] for e in entries}) == len(entries)
    records = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=args.workers) as pool:
        futures = [pool.submit(measure, entry, args, engine_hash) for entry in entries]
        for future in concurrent.futures.as_completed(futures):
            record = future.result()
            records.append(record)
            print(json.dumps({"file": record["file"], "blender": record["blender"].get("ok"),
                              "check": record["check"].get("ok")}), flush=True)
    if not args.no_report:
        summary = report(entries, records, args, engine_hash)
        print(json.dumps({k: v for k, v in summary.items() if not k.endswith("frequency")}), flush=True)
