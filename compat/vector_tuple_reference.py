"""Capture Vector.to_tuple observations without Blender implementation code.

blender --background --factory-startup --python-exit-code 1 \\
  --python compat/vector_tuple_reference.py -- /tmp/vector-tuple-reference.json
"""
import json
from pathlib import Path
import sys

import bpy
from mathutils import Vector

vectors = [
    (2.5, -2.5, 3.5, -3.5),
    (1.25, -1.25, .125, -.125),
    (1.234567, -2.345678, .0005),
    (0., -0., 1e-40, -1e-40),
    (1e38, -1e38),
    (float('inf'), float('-inf'), float('nan')),
    (3.4028234663852886e38, 1.401298464324817e-45, .99999994),
]
records = []
for values in vectors:
    vector = Vector(values)
    before = [x.hex() for x in vector]
    # Omitted precision and explicit -1 are both captured. Blender 5.2.3 also
    # accepts 22, although the API documentation gives a maximum of 21.
    for args in [[], *[[precision] for precision in range(-1, 23)]]:
        result = vector.to_tuple(*args)
        assert type(result) is tuple and all(type(x) is float for x in result)
        assert [x.hex() for x in vector] == before
        records.append({'values': [float(x).hex() for x in values], 'args': args,
                        'result': [x.hex() for x in result]})
output = {'blender': bpy.app.version_string, 'cases': records}
# One observation per line keeps reviewable fixture diffs compact.
Path(sys.argv[sys.argv.index('--') + 1]).write_text(
    '{"blender": ' + json.dumps(output['blender']) + ', "cases": [\n' +
    ',\n'.join(json.dumps(row) for row in records) + '\n]}\n')
print('VECTOR_TUPLE_REFERENCE_OK: %d cases' % len(records))
