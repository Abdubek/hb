"""Verify the vendored release files against the recorded upstream inventory."""
import hashlib,json
from pathlib import Path
root=Path(__file__).resolve().parents[1]/'third_party/opensubdiv'
record=json.loads((root/'SOURCE.json').read_text())
for name,expected in record['files_sha256'].items():
    actual=hashlib.sha256((root/name).read_bytes()).hexdigest()
    if actual!=expected:raise SystemExit(f'OpenSubdiv source mismatch: {name}')
print(f"OpenSubdiv {record['version']}: {len(record['files_sha256'])} files verified")
