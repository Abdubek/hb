"""Capture Vector.project observations without embedding Blender source code.

blender --background --factory-startup --python-exit-code 1 \\
  --python compat/vector_project_reference.py -- /tmp/vector-project-reference.json
"""
import json
from pathlib import Path
import random
import sys

import bpy
from mathutils import Vector


def axis(kind, values):
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
    a = [3.1, -1.2, 5.3, 2.4][:size]
    b = [1.1, -2.2, 3.3, -4.4][:size]
    for values in (b, [0]*size, a, [-x for x in a]):
        for kind in ('vector', 'tuple', 'list', 'iterator', 'generator'):
            specs.append(dict(a=a, other=values, kind=kind))
    for kind in ('vector', 'tuple', 'list', 'iterator', 'generator'):
        if kind != 'vector' or size < 4:
            specs.append(dict(a=a, other=b+[99], kind=kind))
    for kind, values in (('range', [2, 2*size+1, 2]),
                         ('dict', list(range(1, size+1))), ('bytes', list(range(1, size+1)))):
        specs.append(dict(a=a, other=values, kind=kind))
    for values in ([], [1]*(size-1), None, 3, '1234', [1]*size+['bad'],
                   [1]*(size-1)+['2'], [[1]]*size):
        specs.append(dict(a=a, other=values, kind='list'))
    # Squared axis length underflows: capture the native nonfinite result.
    specs.append(dict(a=a, other=[1e-30]*size, kind='tuple'))
    specs.append(dict(a=[-1]*size, other=[1e-30]*size, kind='tuple'))
    specs.append(dict(a=a, other=[1e-30]+[0]*(size-1), kind='tuple'))
    specs.append(dict(a=[0]*size, other=b, kind='tuple'))

rng = random.Random(20261128)
for index in range(36):
    size = 2+index%3
    scale = (1e-15, .001, 1, 1e5)[index%4]
    specs.append(dict(a=[rng.uniform(-1,1)*scale for _ in range(size)],
                      other=[rng.uniform(-1,1)*scale for _ in range(size)],
                      kind='vector' if index%2 else 'tuple'))
# Cancellation in the projection numerator and non-unit axes.
for size in (2, 3, 4):
    specs.append(dict(a=[1e10, 1, 1e10, 2][:size], other=[1, 1, -1, 2][:size], kind='tuple'))

records = []
for spec in specs:
    vector=Vector(spec['a']);other=axis(spec['kind'],spec['other'])
    before=[x.hex() for x in vector]
    other_before=list(other) if isinstance(other,(Vector,list,tuple)) else None
    try:
        result=vector.project(other)
        assert type(result) is Vector and result is not vector and result is not other
        assert len(result)==len(vector)
        observed={'result':[float(x).hex() for x in result]}
    except (TypeError,ValueError) as error:observed={'error':type(error).__name__}
    assert [x.hex() for x in vector]==before
    if other_before is not None:assert list(other)==other_before
    records.append(dict(**spec,**observed))
Path(sys.argv[sys.argv.index('--')+1]).write_text(
    '{"blender": '+json.dumps(bpy.app.version_string)+', "cases": [\n'+
    ',\n'.join(json.dumps(row) for row in records)+'\n]}\n')
print('VECTOR_PROJECT_REFERENCE_OK: %d cases' % len(records))
