"""Run with the SAME CPython used for embedding. No extracted runtime files."""
import ast
import marshal
from frozen_codec_maps import compact_codec_maps
import sys
from pathlib import Path
stdlib, output = map(Path, sys.argv[1:])
names = ['encodings', 'json', 'collections', 're', 'importlib', 'ast', '__future__',
         'types', 'enum', 'functools', 'operator', 'keyword', 'reprlib', 'copy',
         'copyreg', 'weakref', '_weakrefset', 'contextlib', 'warnings', 'traceback',
         'linecache', 'tokenize', 'token', 'textwrap', 'string', 'io', 'abc',
         'stat', 'genericpath', 'posixpath', 'os', '_collections_abc', 'random',
         'bisect', 'itertools', 'heapq', 'struct']
modules = {}
for name in names:
    path = stdlib / name
    if path.is_dir():
        for file in sorted(path.rglob('*.py')):
            if '__pycache__' in file.parts: continue
            rel = file.relative_to(stdlib).with_suffix('')
            parts = list(rel.parts)
            package = parts[-1] == '__init__'
            if package: parts.pop()
            modules['.'.join(parts)] = (file, package)
    elif path.with_suffix('.py').is_file():
        modules[name] = (path.with_suffix('.py'), False)
root = Path(__file__).resolve().parents[1]
# Build-time bytecode for the whole compatibility namespace. Nothing is unpacked
# to disk at runtime and no host Python is needed by the resulting executable.
# Manifest membership is owned by HB in Rust; no Python copy.
shim = 'from __main__ import SEED\n'
shim += '\n'.join((root/'pyshim'/name).read_text() for name in ('runtime.py','vectors.py','transforms.py','colors.py','primitives.py','bmesh_data.py','bmesh.py','groups.py','modifiers.py','object_ops.py','primitive_context.py','curves.py','text.py','io_ops.py','checker.py'))
modules['_hb_runtime'] = (None, False)
lines = ['#include <Python.h>']
entries = []
for i, (name, (file, package)) in enumerate(sorted(modules.items())):
    source = shim if file is None else file.read_bytes()
    if name.startswith('encodings.'):
        source, _ = compact_codec_maps(ast.parse(source))
    blob = marshal.dumps(compile(source, '<hb>/' + name if file is None else '<stdlib>/' + name, 'exec', optimize=2))
    lines.append('static const unsigned char m%d[] = {%s};' % (i, ','.join(map(str, blob))))
    entries.append('{"%s", m%d, %d, %d},' % (name, i, len(blob), int(package)))
lines += ['static const struct _frozen hb_frozen[] = {', *entries, '{NULL, NULL, 0, 0}};',
          'void hb_set_frozen(void) { PyImport_FrozenModules = hb_frozen; }']
output.write_text('\n'.join(lines))
