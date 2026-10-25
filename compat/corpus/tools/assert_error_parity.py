"""Fail unless every Blender-invalid sample has the same hb error.

This gate intentionally stays red for mismatches; it does not weaken the oracle
to accept any rejection or rewrite the source to avoid unsupported APIs.
"""
import hashlib
import json
from pathlib import Path

corpus = Path(__file__).resolve().parents[1]
index = json.loads((corpus / "index.json").read_text())
failures = []
invalid = 0
for entry in index["scripts"]:
    source = corpus / entry["file"]
    if hashlib.sha256(source.read_bytes()).hexdigest() != entry["sha256"]:
        failures.append({"file": entry["file"], "status": "source hash changed"})
        continue
    record = json.loads((corpus / entry["validation"]).read_text())
    if record["blender"].get("infrastructure_error"):
        failures.append({"file": entry["file"], "status": "unresolved Blender execution"})
    if entry["file"].startswith("invalid/"):
        invalid += 1
        status = record.get("error_parity", {}).get("status", "not measured")
        if status != "same_error":
            failures.append({"file": entry["file"], "status": status})
if not index.get("complete"):
    failures.append({"status": "acquisition incomplete"})
print(json.dumps({"ok": not failures, "invalid_scripts": invalid, "failures": failures}, indent=2))
raise SystemExit(bool(failures))
