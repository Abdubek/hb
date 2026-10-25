"""Audit the complete corpus against retained provider/source evidence."""
import argparse
import collections
import hashlib
from html.parser import HTMLParser
import importlib.util
import json
from pathlib import Path
import re

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument("--check", action="store_true", help="Verify without rewriting the historical audit report")
args = parser.parse_args()

corpus = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("measurement", corpus / "tools/measure.py")
measurement = importlib.util.module_from_spec(spec)
spec.loader.exec_module(measurement)
index = json.loads((corpus / "index.json").read_text())
assert index["complete"] and len(index["scripts"]) == 400
entries = index["scripts"]
assert collections.Counter(e["provider"] for e in entries) == {"claude": 150, "gpt6": 150, "blender-stackexchange": 92, "github-gist": 8}
assert len({e["sha256"] for e in entries}) == 400, "Duplicate complete sources"
assert {str(p.relative_to(corpus)) for folder in (corpus, corpus / "invalid") for p in folder.glob("*.py")} == {e["file"] for e in entries}, "Unindexed source files or synthetic leftovers"


class Blocks(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.pre = self.code = False
        self.blocks = []
    def handle_starttag(self, tag, attrs):
        if tag == "pre":
            self.pre = True
        if tag == "code" and self.pre:
            self.code = True
            self.blocks.append("")
    def handle_endtag(self, tag):
        if tag == "pre":
            self.pre = False
        if tag == "code":
            self.code = False
    def handle_data(self, data):
        if self.pre and self.code:
            self.blocks[-1] += data


engines, references, class_matches, mismatches = set(), set(), [], []
for entry in entries:
    source = (corpus / entry["file"]).read_bytes()
    assert hashlib.sha256(source).hexdigest() == entry["sha256"], entry["file"]
    provider = entry["provider"]
    if provider in ("claude", "gpt6"):
        attempt = corpus / entry["response"]
        prompt = (attempt / "prompt.txt").read_text()
        assert entry["task"] in prompt
        assert not re.search(r"\bhb\b|videsh", prompt, re.I), "Compatibility knowledge in author prompt"
        if provider == "claude":
            raw = json.loads((attempt / "stdout.jsonl").read_text())
            response = raw.get("structured_output") or json.loads(raw["result"])
        else:
            response = json.loads((attempt / "response.json").read_text())
            events = [json.loads(line) for line in (attempt / "stdout.jsonl").read_text().splitlines()]
            assert not any(e.get("item", {}).get("type") in ("command_execution", "mcp_tool_call", "file_change", "web_search") for e in events), "Author used external tools"
        id = Path(entry["file"]).stem
        original = next(s["source"] for s in response["scripts"] if s["id"] == id)
        assert original.encode("utf-8") == source, entry["file"]
    elif provider == "blender-stackexchange":
        answer = json.loads((corpus / entry["source_snapshot"]).read_text())
        parser = Blocks()
        parser.feed(answer["body"])
        assert parser.blocks[entry["code_block"] - 1].encode("utf-8") == source
        assert answer["content_license"] == entry["license"]
        assert entry["source_url"] and entry["license_url"] and entry["author"]
    else:
        assert entry["license"] == "MIT" and entry["raw_url"] and entry["source_url"]
        license_text = (corpus / entry["license_evidence"]).read_text()
        assert "Permission is hereby granted, free of charge" in license_text and "MERCHANTABILITY" in license_text
    result = json.loads((corpus / entry["validation"]).read_text())
    # Publication may redact a personal path in a source. Keep the historical
    # input hash distinct from the published source hash; do not claim a new run.
    assert result["source_sha256"] == entry.get("original_sha256", entry["sha256"])
    assert result["runner_sha256"] == measurement.RUNNER_HASH, "Stale execution evidence"
    assert not result["blender"].get("infrastructure_error"), entry["file"]
    assert result["check_process"]["returncode"] in (0, 1), "Incomplete checker process"
    engines.add(result["engine_sha256"])
    references.add(result["reference"])
    invalid = bool(result["blender"].get("exception") or result["blender"].get("signal"))
    assert entry["file"].startswith("invalid/") == invalid
    if invalid:
        status = result["error_parity"]["status"]
        assert status in ("same_error", "different_error"), "Unresolved error comparison"
        (class_matches if status == "same_error" else mismatches).append(entry["file"])
assert len(engines) == len(references) == 1
for provider in ("claude", "gpt6"):
    group = [e for e in entries if e["provider"] == provider]
    assert {Path(e["file"]).stem for e in group} == {f"{provider}-{i:03}" for i in range(1, 151)}
    assert len({e["task"] for e in group}) == 150
report = {"integrity_pass": True, "scripts": 400, "unique_sources": 400,
          "model_sources_match_raw_responses": 300, "public_sources_with_license_records": 100,
          "all_blender_outcomes_resolved": True, "same_runner_and_reference": True,
          "invalid_same_error": len(class_matches), "invalid_different_error": len(mismatches),
          "error_parity_pass": not mismatches,
          "runner_sha256": measurement.RUNNER_HASH, "engine_sha256": next(iter(engines))}
if not args.check:
    (corpus / "audit.json").write_text(json.dumps(report, indent=2) + "\n")
print(json.dumps(report, indent=2))
