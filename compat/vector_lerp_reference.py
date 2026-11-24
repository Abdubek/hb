"""Capture Vector.lerp input/result observations without Blender source code.

blender --background --factory-startup --python-exit-code 1 \\
  --python compat/vector_lerp_reference.py -- /tmp/vector-lerp-reference.json
"""
import json
from pathlib import Path
import random
import sys

import bpy
from mathutils import Vector


def endpoint(kind, values):
    if kind == 'vector': return Vector(values)
    if kind == 'tuple': return tuple(values)
    if kind == 'iterator': return iter(values)
    if kind == 'generator': return (x for x in values)
    if kind == 'range': return range(*values)
    if kind == 'dict': return {x: None for x in values}
    if kind == 'bytes': return bytes(values)
    return values


specs = []
for size in (2, 3, 4):
    a = [1.1, -2.25, 3.125, -4.5][:size]
    b = [-3.75, 4.2, -5.5, 6.25][:size]
    for kind in ('vector', 'tuple', 'list', 'iterator', 'generator'):
        for factor in (-.5, 0., .25, 1., 1.5):
            specs.append(dict(a=a, other=b, kind=kind, factor=factor))
        if size < 4 or kind != 'vector':
            specs.append(dict(a=a, other=b+[99.], kind=kind, factor=.25))
    for kind, values in (('range', [2, 2*size+1, 2]),
                         ('dict', list(range(1, size+1))), ('bytes', list(range(1, size+1)))):
        specs.append(dict(a=a, other=values, kind=kind, factor=.5))
    for other in ([], [1]*(size-1), None, 3, '1234', [1]*size+['bad'],
                  [1]*(size-1)+['2'], [[1]]*size):
        specs.append(dict(a=a, other=other, kind='list', factor=.5))
    for factor in (None, '0.5', []):
        specs.append(dict(a=a, other=b, kind='vector', factor=factor))

rng = random.Random(20261124)
for index in range(24):
    size = 2+index%3
    scale = (1e-20, .001, 1, 1e5)[index%4]
    specs.append(dict(a=[rng.uniform(-1,1)*scale for _ in range(size)],
                      other=[rng.uniform(-1,1)*scale for _ in range(size)],
                      kind='vector' if index%2 else 'tuple', factor=rng.uniform(-1,2)))
specs.append(dict(a=[0., -0., 1e-30, -1e-30], other=[-0., 0., -1e-30, 1e-30],
                  kind='tuple', factor=.5))
records = []
for spec in specs:
    vector = Vector(spec['a'])
    other = endpoint(spec['kind'], spec['other'])
    before = [x.hex() for x in vector]
    other_before = list(other) if isinstance(other, (Vector, list, tuple)) else None
    try:
        result = vector.lerp(other, spec['factor'])
        assert type(result) is Vector and result is not vector
        observed = {'result': list(result)}
    except (TypeError, ValueError) as error:
        observed = {'error': type(error).__name__}
    assert [x.hex() for x in vector] == before
    if other_before is not None: assert list(other) == other_before
    records.append(dict(**spec, **observed))
Path(sys.argv[sys.argv.index('--')+1]).write_text(
    '{"blender": '+json.dumps(bpy.app.version_string)+', "cases": [\n'+
    ',\n'.join(json.dumps(row) for row in records)+'\n]}\n')
print('VECTOR_LERP_REFERENCE_OK: %d cases' % len(records))
