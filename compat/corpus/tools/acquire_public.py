"""Import unedited gist files with an explicit MIT license in the gist.

Input is GitHub's public /users/{owner}/gists listing. Unlicensed snippets,
licenses on unrelated gists, and a profile's repository license do not qualify.
Downloads not qualifying for redistribution stay outside the repository.
"""
import argparse
import concurrent.futures
import hashlib
import json
from pathlib import Path
import re
import subprocess
import tempfile

ROOT = Path(__file__).resolve().parents[1]


def fetch(url):
    result = subprocess.run(["curl", "-fsSL", "--retry", "2", "--max-time", "45", url],
                            capture_output=True, check=True)
    return result.stdout


def inspect(gist):
    files = gist["files"]
    python = [f for f in files.values() if f["filename"].endswith(".py")]
    if not python:
        return []
    license_files = [f for f in files.values() if f["filename"].lower() in ("license", "license.txt", "license.md")]
    license_evidence = None
    for entry in license_files:
        content = fetch(entry["raw_url"])
        if b"Permission is hereby granted, free of charge" in content and b"MERCHANTABILITY" in content:
            license_evidence = (entry, content)
    rows = []
    for entry in python:
        source = fetch(entry["raw_url"])
        if b"bpy" not in source:
            continue
        evidence = license_evidence
        if b"Permission is hereby granted, free of charge" in source and b"MERCHANTABILITY" in source:
            evidence = (entry, source)
        if evidence is None:
            continue
        id = f"gist-{gist['id']}-{entry['filename']}"
        assert "/" not in id and "\\" not in id
        dest = ROOT / "acquisition" / "public" / id.removesuffix(".py")
        dest.mkdir(parents=True, exist_ok=True)
        (dest / "metadata.json").write_text(json.dumps(gist, indent=2) + "\n")
        (dest / "LICENSE").write_bytes(evidence[1])
        (ROOT / id).write_bytes(source)
        row = {"file": id, "provider": "github-gist", "source_url": gist["html_url"],
               "raw_url": entry["raw_url"], "original_filename": entry["filename"],
               "author": gist["owner"]["login"], "license": "MIT",
               "license_url": evidence[0]["raw_url"], "license_evidence": str((dest / "LICENSE").relative_to(ROOT)),
               "sha256": hashlib.sha256(source).hexdigest(), "source_transform": "none; exact downloaded bytes"}
        (dest / "manifest.json").write_text(json.dumps({"scripts": [row]}, indent=2) + "\n")
        rows.append(row)
    return rows


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("listings", nargs="+")
    args = parser.parse_args()
    gists = {}
    for listing in args.listings:
        for gist in json.loads(Path(listing).read_text()):
            gists[gist["id"]] = gist
    with concurrent.futures.ThreadPoolExecutor(max_workers=4) as pool:
        futures = {pool.submit(inspect, g): id for id, g in gists.items()}
        for future in concurrent.futures.as_completed(futures):
            try:
                rows = future.result()
                for row in rows:
                    print(json.dumps({"file": row["file"], "license": row["license"]}), flush=True)
            except (OSError, ValueError, subprocess.SubprocessError) as error:
                print(json.dumps({"gist": futures[future], "error": str(error)}), flush=True)
