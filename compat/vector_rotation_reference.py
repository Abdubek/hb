"""Capture Vector.rotation_difference results from Blender.

blender --background --factory-startup --python-exit-code 1 \
  --python compat/vector_rotation_reference.py -- /tmp/rotation-reference.json
"""
import json
from pathlib import Path
import random
import sys

import bpy
from mathutils import Vector

pairs = [
    ((1, 0, 0), (0, 1, 0)), ((0, 0, 1), (1, 0, 0)),
    ((0, 0, 1), (1, 2, 3)), ((2, 0, 0), (0, 3, 0)),
    ((0, 0, 0), (1, 2, 3)), ((1, 2, 3), (0, 0, 0)),
    ((0, 0, 0), (0, 0, 0)), ((1e-20, 0, 0), (0, 1, 0)),
    ((1, 2, 3), (0, 1e-20, 0)),
    ((1, 0, 0), (0, 1, 0, 3)), ((1, 0, 0, 2), (0, 1, 0, -4)),
    ((1e6, -1e6, 1e6), (-1e6, 1e6, 1e6)),
]
for a in ((1, 0, 0), (-1, 0, 0), (0, 1, 0), (0, 0, 1),
          (1, 2, 3), (3, 2, 1), (-3, 2, 1), (1, -3, 2), (1, 2, -3),
          (1, 1, 1), (1, 1, 0), (1, 0, 1)):
    pairs.append((a, tuple(-x for x in a)))
for epsilon in (1e-8, 1e-7, 1.19e-7, 1.2e-7, 2e-7, 1e-6, .001, .1):
    for sign in (1, -1):
        pairs.append(((1, 0, 0), (sign, epsilon, 0)))
rng = random.Random(20261105)
for index in range(40):
    a = [rng.uniform(-1, 1)*10**rng.uniform(-5, 5) for _ in range(3 + index % 2)]
    b = [rng.uniform(-1, 1)*10**rng.uniform(-5, 5) for _ in range(3 + (index // 2) % 2)]
    pairs.append((a, b))
for _ in range(16):
    a = [rng.uniform(-10, 10) for _ in range(3)]
    pairs.append((a, [-x for x in a]))
edge_rng = random.Random(918273)
for index in range(32):
    a = Vector([edge_rng.uniform(-1, 1) for _ in range(3)]).normalized()
    epsilon = (1e-8, 1e-7, 1e-6, 1e-4)[index % 4]
    b = a*(1 if index % 8 < 4 else -1) + Vector([edge_rng.uniform(-epsilon, epsilon) for _ in range(3)])
    pairs.append((list(a), list(b)))
records = []
for a, b in pairs:
    source, target = Vector(a), Vector(b)
    before = (list(source), list(target))
    result = source.rotation_difference(target)
    assert before == (list(source), list(target))
    records.append({'a': list(source), 'b': list(target), 'quaternion': list(result),
                    'matrix': [list(row) for row in result.to_matrix()]})
Path(sys.argv[sys.argv.index('--') + 1]).write_text(
    json.dumps({'blender': bpy.app.version_string, 'cases': records}, indent=2) + '\n')
print(f'VECTOR_ROTATION_REFERENCE_OK: {len(records)} cases')
