"""Generate the bpy API manifest from doc attributes on real Rust tests."""
import argparse
import json
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1]


def generate():
    document = json.loads((ROOT / "compat/manifest-metadata.json").read_text())
    symbols = {}
    attributes = []
    is_test = False
    for line in (ROOT / "tests/contracts.rs").read_text().splitlines():
        line = line.strip()
        doc = re.fullmatch(r'#[\[]doc = ("(?:[^"\\]|\\.)*")[\]]', line)
        if doc:
            attributes.append(json.loads(doc[1]))
        elif line == "#[test]":
            is_test = True
        elif line.startswith("fn "):
            declarations = [text for text in attributes if text.startswith("hb:symbol=")]
            if declarations:
                if not is_test:
                    raise ValueError("API declarations must annotate a test")
                fixtures = [text.removeprefix("hb:test=") for text in attributes
                            if text.startswith("hb:test=")]
                if len(fixtures) != 1 or not (ROOT / fixtures[0]).is_file():
                    raise ValueError(f"Missing test fixture for {line}")
                for index, text in enumerate(attributes):
                    if not text.startswith("hb:symbol="):
                        continue
                    symbol = text.removeprefix("hb:symbol=")
                    if symbol in symbols:
                        raise ValueError(f"Duplicate API symbol: {symbol}")
                    if index + 1 == len(attributes) or attributes[index + 1].startswith("hb:"):
                        raise ValueError(f"Missing description: {symbol}")
                    symbols[symbol] = {"description": attributes[index + 1], "test": fixtures[0]}
            attributes = []
            is_test = False
    if not symbols:
        raise ValueError("No API declarations found")
    document["symbols"] = symbols
    return json.dumps(document, indent=2, sort_keys=True, ensure_ascii=False) + "\n"


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", help="Fail if the manifest is stale")
    args = parser.parse_args()
    output = ROOT / "compat/manifest.json"
    generated = generate()
    if args.check:
        if output.read_text() != generated:
            raise SystemExit("Manifest is stale; run python3 scripts/generate_manifest.py")
        print("API manifest matches contract tests")
    else:
        output.write_text(generated)
