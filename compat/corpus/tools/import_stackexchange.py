"""Import the requested StackExchange answer snippets with original attribution.

CC BY-SA is retained explicitly, not relabeled as a permissive software license.
The source request names StackExchange answers separately from permissive gists.
"""
import argparse
import hashlib
import json
from pathlib import Path
import shutil

ROOT = Path(__file__).resolve().parents[1]
parser = argparse.ArgumentParser()
parser.add_argument("--staging", required=True)
args = parser.parse_args()
staging = Path(args.staging)
rows = json.loads((staging / "candidates.json").read_text())
for row in rows:
    assert row["license"] in ("CC BY-SA 3.0", "CC BY-SA 4.0"), row
    source = (staging / row["file"]).read_bytes()
    assert hashlib.sha256(source).hexdigest() == row["sha256"]
    dest = ROOT / "acquisition/public" / Path(row["file"]).stem
    dest.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(staging / (row["file"] + ".answer.json"), dest / "answer.json")
    row["license_url"] = "https://creativecommons.org/licenses/by-sa/" + row["license"].rsplit(" ", 1)[1] + "/"
    row["revision_url"] = f"https://blender.stackexchange.com/posts/{row['answer_id']}/revisions"
    row["source_snapshot"] = str((dest / "answer.json").relative_to(ROOT))
    row["license_scope"] = "This source and its answer snapshot retain the original CC BY-SA license; no MIT relicensing."
    attribution = f"{row['file']}\n\nAuthor: {row['author']}\nAnswer: {row['source_url']}\nRevision history: {row['revision_url']}\nLicense: {row['license']} ({row['license_url']})\n\nOne original code block, HTML-decoded. No repairs, added imports, or combined blocks.\nThe licensed answer snapshot is retained in answer.json.\n"
    (dest / "ATTRIBUTION.txt").write_text(attribution)
    (ROOT / row["file"]).write_bytes(source)
    (dest / "manifest.json").write_text(json.dumps({"scripts": [row]}, indent=2) + "\n")
inventory = ROOT / "acquisition/stackexchange-candidates.json"
inventory.write_text(json.dumps({"status": "imported under original CC BY-SA licenses as explicitly requested StackExchange sources", "scripts_counted_in_corpus": len(rows), "candidates": rows}, indent=2) + "\n")
print(f"Imported {len(rows)} unchanged StackExchange code blocks with original licenses")
