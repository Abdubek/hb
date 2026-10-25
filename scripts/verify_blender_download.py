import hashlib
import sys
from pathlib import Path
name=sys.argv[1] if len(sys.argv)>1 else 'blender-4.5.9-linux-x64.tar.xz'
lines=Path('.build/blender.sha256').read_text().splitlines()
expected=next(line.split()[0] for line in lines if line.split()[-1].lstrip('*')==name)
actual=hashlib.sha256(Path('.build/blender.tar.xz').read_bytes()).hexdigest()
if actual!=expected:raise SystemExit('Blender archive checksum mismatch')
