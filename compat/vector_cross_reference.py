"""Capture dimensional cross results and errors without Blender source code.

blender --background --factory-startup --python-exit-code 1 \\
  --python compat/vector_cross_reference.py -- /tmp/vector-cross-reference.json
"""
import json
from pathlib import Path
import random
import sys

import bpy
from mathutils import Vector


def operand(kind, values):
    if kind == 'vector': return Vector(values)
    if kind == 'tuple': return tuple(values)
    if kind == 'iterator': return iter(values)
    if kind == 'generator': return (x for x in values)
    if kind == 'range': return range(*values)
    if kind == 'dict': return {x: None for x in values}
    if kind == 'bytes': return bytes(values)
    return values


specs = []
for size in (2, 3):
    for a, b in (([1, 2, 3], [4, 5, 6]), ([0, 0, 0], [1, 2, 3]),
                 ([1, 2, 3], [2, 4, 6]), ([1.1, -2.2, 3.3], [-4.4, 5.5, -6.6])):
        for kind in ('vector', 'tuple', 'list', 'iterator', 'generator'):
            specs.append(dict(a=a[:size], b=b[:size], kind=kind))
    for kind, b in (('range', [2, 2*size+1, 2]), ('dict', list(range(1,size+1))),
                    ('bytes', list(range(1,size+1)))):
        specs.append(dict(a=list(range(1,size+1)), b=b, kind=kind))
    for b in ([], [1]*(size-1), [1]*(size+1), None, 3, '123'[:size],
              [1]*(size-1)+['2'], [[1]]*size, [1]*size+['bad']):
        specs.append(dict(a=list(range(1,size+1)), b=b, kind='list'))
    for b in ((1,2), (1,2,3), (1,2,3,4)):
        if len(b)!=size:specs.append(dict(a=list(range(1,size+1)), b=b, kind='vector'))
for b in ([1,2], [1,2,3], [1,2,3,4], None):
    specs.append(dict(a=[1,2,3,4], b=b, kind='list'))
rng = random.Random(20261126)
for index in range(32):
    size=2+index%2
    scale=(1e-10,.001,1,1e4)[index%4]
    a=[rng.uniform(-1,1)*scale for _ in range(size)]
    b=[rng.uniform(-1,1)*scale for _ in range(size)]
    specs.append(dict(a=a,b=b,kind='tuple' if index%3 else 'vector'))
# Cancellation cases distinguish float32 products from wider intermediates.
for size in (2,3):
    for epsilon in (0., 1e-7, 1e-6, .001):
        specs.append(dict(a=[1.1,2.2,3.3][:size],
                          b=[2.2+epsilon,4.4-epsilon,6.6+epsilon][:size],kind='tuple'))

records=[]
for spec in specs:
    vector=Vector(spec['a']);other=operand(spec['kind'],spec['b'])
    before=[x.hex() for x in vector]
    other_before=list(other) if isinstance(other,(Vector,list,tuple)) else None
    try:
        result=vector.cross(other)
        observed={'type':type(result).__name__,
                  'result':list(result) if isinstance(result,Vector) else result}
    except (TypeError,ValueError) as error:observed={'error':type(error).__name__}
    assert [x.hex() for x in vector]==before
    if other_before is not None:assert list(other)==other_before
    records.append(dict(**spec,**observed))
Path(sys.argv[sys.argv.index('--')+1]).write_text(
    '{"blender": '+json.dumps(bpy.app.version_string)+', "cases": [\n'+
    ',\n'.join(json.dumps(row) for row in records)+'\n]}\n')
print('VECTOR_CROSS_REFERENCE_OK: %d cases' % len(records))
