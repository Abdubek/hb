"""Measure fresh-process HB tasks, optionally alongside background Blender."""
import argparse
from concurrent.futures import ThreadPoolExecutor
import hashlib
import json
import os
from pathlib import Path
import platform
import statistics
import subprocess
import tempfile
import time


def measure(command, directory):
    with tempfile.TemporaryFile() as log:
        start = time.perf_counter()
        process = subprocess.Popen(command, cwd=directory, stdout=log, stderr=log)
        _, status, usage = os.wait4(process.pid, 0)
        elapsed = (time.perf_counter() - start) * 1000
        process.returncode = os.waitstatus_to_exitcode(status)
        if process.returncode:
            log.seek(0)
            raise RuntimeError(log.read().decode(errors="replace"))
    rss = usage.ru_maxrss * (1 if platform.system() == "Darwin" else 1024)
    return {"wall_ms": round(elapsed, 3), "peak_rss_bytes": rss}


def summary(samples):
    return {
        "median_ms": round(statistics.median(s["wall_ms"] for s in samples), 3),
        "median_peak_rss_bytes": statistics.median(s["peak_rss_bytes"] for s in samples),
        "samples": samples,
    }


def measure_corpus(hb, root):
    corpus = root / "compat/corpus"
    index = json.loads((corpus / "index.json").read_text())

    def check(entry):
        path = corpus / entry["file"]
        if hashlib.sha256(path.read_bytes()).hexdigest() != entry["sha256"]:
            raise ValueError(f"Corpus source changed: {entry['file']}")
        process = subprocess.run([str(hb), "check", str(path)], capture_output=True,
                                 text=True, timeout=30)
        value = json.loads(process.stdout)
        return {"file": entry["file"], "origin": entry["provider"],
                "accepted": process.returncode == 0 and value.get("ok") is True,
                "errors": len(value.get("errors", []))}

    with ThreadPoolExecutor(max_workers=4) as pool:
        rows = list(pool.map(check, index["scripts"]))
    origins = {}
    for origin in sorted({row["origin"] for row in rows}):
        group = [row for row in rows if row["origin"] == origin]
        origins[origin] = {"scripts": len(group),
                           "preflight_accepted": sum(row["accepted"] for row in group)}
    return {
        "kind": "Static checker acceptance only; no runtime, geometry, render or Blender error-parity claim",
        "measured_at_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "hb_version": json.loads(subprocess.check_output([str(hb), "capabilities"]))["version"],
        "binary_sha256": hashlib.sha256(hb.read_bytes()).hexdigest(),
        "corpus_index_sha256": hashlib.sha256((corpus / "index.json").read_bytes()).hexdigest(),
        "scripts": len(rows), "preflight_accepted": sum(row["accepted"] for row in rows),
        "by_origin": origins, "results": rows,
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--hb", type=Path, default=Path("target/release/hb"))
    parser.add_argument("--blender", type=Path)
    parser.add_argument("--runs", type=int, default=10)
    parser.add_argument("--corpus-preflight", action="store_true",
                        help="Only measure checker acceptance of the 400-script corpus")
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    if args.runs < 1:
        parser.error("--runs must be positive")
    hb = args.hb.resolve()
    blender = args.blender.resolve() if args.blender else None
    root = Path(__file__).resolve().parents[1]
    if args.corpus_preflight:
        report = measure_corpus(hb, root)
        args.out.parent.mkdir(parents=True, exist_ok=True)
        args.out.write_text(json.dumps(report, indent=2) + "\n")
        print(json.dumps({key: value for key, value in report.items() if key != "results"}, indent=2))
        return
    report = {
        "kind": "Local process microbenchmark; no agent success or render parity score",
        "measured_at_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "system": {"os": platform.system(), "release": platform.release(),
                   "architecture": platform.machine()},
        "runs": args.runs,
        "warmups_per_task_and_engine": 1,
        "hb": {"version": json.loads(subprocess.check_output([str(hb), "capabilities"]))["version"],
               "binary_bytes": hb.stat().st_size,
               "binary_sha256": hashlib.sha256(hb.read_bytes()).hexdigest()},
        "tasks": {},
    }
    if platform.system() == "Darwin":
        for key, setting in (("cpu", "machdep.cpu.brand_string"), ("memory_bytes", "hw.memsize")):
            try:
                value = subprocess.check_output(["sysctl", "-n", setting], stderr=subprocess.DEVNULL, text=True).strip()
                report["system"][key] = int(value) if key == "memory_bytes" else value
            except (OSError, subprocess.CalledProcessError):
                pass
    if blender:
        version = subprocess.check_output([str(blender), "--version"], stderr=subprocess.DEVNULL, text=True)
        report["blender"] = {"version": next(line for line in version.splitlines()
                                               if line.startswith("Blender ")),
                             "executable_bytes": blender.stat().st_size}
    with tempfile.TemporaryDirectory(prefix="hb-benchmark-") as directory:
        work = Path(directory)
        empty = work / "empty.py"
        empty.write_text("import bpy\n")
        cube = work / "cube.py"
        cube.write_text("import bpy\nbpy.ops.object.select_all(action='SELECT')\n"
                        "bpy.ops.object.delete(use_global=False)\n"
                        + (root / "examples/cube.py").read_text())
        blender_cube = work / "blender_cube.py"
        blender_cube.write_text(cube.read_text() + "\n"
            "bpy.ops.export_scene.gltf(filepath='blender.glb', export_format='GLB', export_apply=True)\n")
        blender_base = [str(blender), "--background", "--factory-startup", "--threads", "1",
                        "--python-exit-code", "1", "--python"] if blender else []
        commands = {
            "import_bpy": {"hb": [str(hb), "run", str(empty)]},
            "cube_to_glb": {"hb": [str(hb), "run", str(cube), "--out", "hb.glb"]},
        }
        if blender:
            commands["import_bpy"]["blender"] = blender_base + [str(empty)]
            commands["cube_to_glb"]["blender"] = blender_base + [str(blender_cube)]
        for name, engines in commands.items():
            samples = {engine: [] for engine in engines}
            for iteration in range(args.runs + 1):
                for engine, command in engines.items():
                    # HB runs persist a snapshot; use a fresh scene on every run.
                    invocation = command + ["--scene", f"{name}-{iteration}.hb"] if engine == "hb" else command
                    sample = measure(invocation, work)
                    if iteration:
                        samples[engine].append(sample)
            report["tasks"][name] = {engine: summary(values) for engine, values in samples.items()}
        for name in ("hb.glb", "blender.glb") if blender else ("hb.glb",):
            assert (work / name).read_bytes()[:4] == b"glTF", f"Missing GLB export: {name}"
        scene = work / f"cube_to_glb-{args.runs}.hb"
        render = [str(hb), "render", "--scene", str(scene), "--views", "iso",
                  "--size", "512", "--out", "preview.png"]
        measure(render, work)
        report["tasks"]["hb_cube_preview_512"] = {"hb": summary([
            measure(render, work) for _ in range(args.runs)])}
        assert (work / "preview.png").read_bytes().startswith(b"\x89PNG\r\n\x1a\n")
    report["method"] = (
        "Sequential fresh processes, one warmup then recorded samples; filesystem caches are warm. "
        "Wall time includes process startup and shutdown. HB run also saves a scene revision. "
        "Both exports clear the default scene and build the same cube; Blender uses one thread. "
        "Peak RSS is wait4 ru_maxrss for the child process. Blender executable size excludes its "
        "required libraries/data; HB size is its complete executable. No Blender rendering comparison."
    )
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(report, indent=2) + "\n")
    print(json.dumps({"tasks": {name: {engine: {key: value for key, value in result.items()
                        if key != "samples"} for engine, result in engines.items()}
                        for name, engines in report["tasks"].items()}}, indent=2))


if __name__ == "__main__":
    main()
