"""Differential check against the embedding CPython's unmodified codec sources."""
import ast
import json
import marshal
from pathlib import Path
import sys
from frozen_codec_maps import compact_codec_maps

stdlib = Path(sys.argv[1])
checks = 0
saved = 0
modules = []

def outcome(fn, value, errors):
    try:
        return ('ok', fn(value, errors))
    except UnicodeError as e:
        return (type(e).__name__, str(e), e.start, e.end, e.reason)

for path in sorted((stdlib / 'encodings').glob('*.py')):
    original = compile(path.read_bytes(), '<codec>', 'exec', optimize=2)
    tree, changed = compact_codec_maps(ast.parse(path.read_bytes()))
    if not changed:
        continue
    compiled = compile(tree, '<codec>', 'exec', optimize=2)
    a, b = {}, {}
    exec(original, a)
    exec(compiled, b)
    for name in ('encoding_map', 'decoding_map', 'decoding_table'):
        assert a.get(name) == b.get(name), (path.name, name)
        if isinstance(a.get(name), dict):
            assert list(a[name].items()) == list(b[name].items()), (path.name, name, 'order')
    values = [chr(i) for i in range(256)] + list(a['decoding_table']) + ['\uffff', '\U0010ffff']
    for errors in ('strict', 'ignore', 'replace'):
        for value in [bytes([i]) for i in range(256)] + [bytes(range(256))]:
            assert outcome(a['Codec']().decode, value, errors) == outcome(b['Codec']().decode, value, errors), (path.name, value, errors)
            checks += 1
        for value in values + [''.join(values)]:
            assert outcome(a['Codec']().encode, value, errors) == outcome(b['Codec']().encode, value, errors), (path.name, value, errors)
            checks += 1
    saved += len(marshal.dumps(original)) - len(marshal.dumps(compiled))
    modules.append(path.stem)
assert modules, 'No codec layouts recognized; inspect the new CPython generator.'
print(json.dumps(dict(modules=modules, modules_changed=len(modules), codec_checks=checks, marshal_bytes_saved=saved, dictionary_values_and_order='identical'), indent=2))
