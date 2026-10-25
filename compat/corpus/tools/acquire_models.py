"""Acquire fresh, unedited model outputs using authenticated local CLIs.

Run outside the repository in an empty temporary directory. Prompts and provider
responses are retained; JSON string decoding is the only source transformation.
No existing corpus, implementation, capability list or checker feedback is sent.
"""
import argparse
import concurrent.futures
import hashlib
import json
import os
from pathlib import Path
import subprocess
import tempfile
import time
import uuid

ROOT = Path(__file__).resolve().parents[1]
SCHEMA = {"type": "object", "properties": {"scripts": {"type": "array", "items": {
    "type": "object", "properties": {"id": {"type": "string"}, "source": {"type": "string"}},
    "required": ["id", "source"], "additionalProperties": False}}},
    "required": ["scripts"], "additionalProperties": False}
PROMPT = """Write independent complete Python scripts for Blender 4.5 LTS for the following tasks.
Use normal Blender bpy, bmesh and mathutils idioms as appropriate. Each script must
construct its scene headlessly from Blender's factory startup, using no external
assets or addons. Include materials, lighting and cameras appropriate to the task.
Model the requested forms with useful detail and sensible geometry counts.
Only construct the scene: do not render images or save files. Return one complete
self-contained source string per task id in the requested JSON. Do not use tools,
read files, execute or test your code. Return your first solution as text.

"""


def acquire(provider, indices, tasks, args):
    ids = [f"{provider}-{i + 1:03}" for i in indices]
    dest = ROOT / "acquisition" / provider / ids[0]
    if (dest / "manifest.json").exists():
        existing = json.loads((dest / "manifest.json").read_text())
        if existing.get("scripts"):
            return {"batch": ids[0], "cached": True}
        if args.reserve and existing.get("reservation") != args.run_id:
            return {"batch": ids[0], "reserved_by_other_run": True}
    if any((ROOT / (id + ".py")).exists() or (ROOT / "invalid" / (id + ".py")).exists() for id in ids):
        return {"batch": ids[0], "error": "Refusing to overwrite an existing source from another acquisition batch"}
    dest.mkdir(parents=True, exist_ok=True)
    attempt = dest / str(time.time_ns())
    attempt.mkdir()
    prompt = PROMPT + "\n".join(f"{id}: {tasks[i]}" for id, i in zip(ids, indices))
    (attempt / "prompt.txt").write_text(prompt)
    work = tempfile.mkdtemp(prefix="blender-author-")
    schema = Path(work) / "response.schema.json"
    schema.write_text(json.dumps(SCHEMA))
    response_file = attempt / "response.json"
    if provider == "claude":
        command = [args.claude, "-p", "--model", args.claude_model, "--effort", "medium",
                   "--tools", "", "--strict-mcp-config", "--setting-sources", "",
                   "--no-session-persistence", "--output-format", "json",
                   "--json-schema", json.dumps(SCHEMA), prompt]
    else:
        command = [args.codex, "exec", "--ignore-user-config", "--ephemeral",
                   "--skip-git-repo-check", "--sandbox", "read-only", "--json",
                   "--model", "gpt-6-astra", "-c", 'model_reasoning_effort="medium"',
                   "--output-schema", str(schema), "-o", str(response_file), prompt]
    started = time.time()
    with (attempt / "stdout.jsonl").open("w") as out, (attempt / "stderr.txt").open("w") as err:
        try:
            result = subprocess.run(command, cwd=work, stdin=subprocess.DEVNULL,
                                    stdout=out, stderr=err, timeout=1200)
        except subprocess.TimeoutExpired:
            return {"batch": ids[0], "error": "provider timeout", "attempt": str(attempt)}
    if result.returncode:
        return {"batch": ids[0], "error": f"provider exit {result.returncode}", "attempt": str(attempt)}
    try:
        if provider == "claude":
            raw = json.loads((attempt / "stdout.jsonl").read_text())
            if raw.get("is_error"):
                raise ValueError("provider reported an error")
            data = raw.get("structured_output") or json.loads(raw["result"])
            models = list(raw.get("modelUsage", {}))
        else:
            data = json.loads(response_file.read_text())
            models = ["gpt-6-astra"]
        sources = data["scripts"]
        assert len(sources) == len(ids) and {s["id"] for s in sources} == set(ids)
        rows = []
        for source in sources:
            assert isinstance(source["source"], str) and source["source"]
            path = ROOT / (source["id"] + ".py")
            content = source["source"].encode("utf-8")
            path.write_bytes(content)
            index = int(source["id"].rsplit("-", 1)[1]) - 1
            rows.append({"file": path.name, "task": tasks[index], "provider": provider,
                         "models": models, "sha256": hashlib.sha256(content).hexdigest(),
                         "requested_model": args.claude_model if provider == "claude" else "gpt-6-astra",
                         "response": str(attempt.relative_to(ROOT)), "source_transform": "JSON decode only"})
        record = {"scripts": rows, "elapsed_seconds": time.time() - started}
        (dest / "manifest.json").write_text(json.dumps(record, indent=2) + "\n")
        return {"batch": ids[0], "count": len(rows), "seconds": round(time.time() - started)}
    except (ValueError, KeyError, AssertionError, OSError) as error:
        return {"batch": ids[0], "error": str(error), "attempt": str(attempt)}


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--claude", default="claude")
    parser.add_argument("--codex", default="codex")
    parser.add_argument("--claude-model", default="claude-opus-5")
    parser.add_argument("--batch-size", type=int, default=5)
    parser.add_argument("--workers", type=int, default=2)
    parser.add_argument("--limit", type=int, default=150)
    parser.add_argument("--start", type=int, default=0)
    parser.add_argument("--reserve", action="store_true", help="Reserve a disjoint range before another acquisition worker reaches it")
    parser.add_argument("--provider", choices=["claude", "gpt6"], action="append")
    parser.add_argument("--task-ids", help="Comma-separated one-based task ids for targeted single-task recovery")
    args = parser.parse_args()
    args.run_id = uuid.uuid4().hex
    providers = args.provider or ("claude", "gpt6")
    starts = list(range(args.start, args.limit, args.batch_size))
    if args.task_ids:
        assert args.batch_size == 1
        starts = [int(id) - 1 for id in args.task_ids.split(",")]
        assert len(set(starts)) == len(starts) and all(0 <= i < 150 for i in starts)
    tasks = (ROOT / "acquisition/tasks.txt").read_text().splitlines()
    tasks += (ROOT / "acquisition/additional-tasks.txt").read_text().splitlines()
    assert len(tasks) == 150 and len(set(tasks)) == 150
    if args.reserve:
        for start in starts:
            for provider in providers:
                dest = ROOT / "acquisition" / provider / f"{provider}-{start+1:03}"
                dest.mkdir(parents=True, exist_ok=True)
                try:
                    with (dest / "manifest.json").open("x") as handle:
                        json.dump({"state": "reserved; not yet acquired", "reservation": args.run_id, "scripts": []}, handle)
                except FileExistsError:
                    pass
    with concurrent.futures.ThreadPoolExecutor(max_workers=args.workers) as pool:
        futures = [pool.submit(acquire, provider, list(range(start, min(start + args.batch_size, args.limit))), tasks, args)
                   for start in starts for provider in providers]
        failures = 0
        for future in concurrent.futures.as_completed(futures):
            result = future.result()
            print(json.dumps(result), flush=True)
            if result.get("error"):
                failures += 1
                for pending in futures:
                    pending.cancel()
                break
    raise SystemExit(bool(failures))
