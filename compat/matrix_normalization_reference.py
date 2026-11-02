"""Capture Blender column normalization, including non-affine bottom rows.

blender --background --factory-startup --python-exit-code 1 \
  --python compat/matrix_normalization_reference.py -- /tmp/reference.json
"""
import json
from pathlib import Path
import random
import sys

import bpy
from mathutils import Matrix

cases = {
    'scale': [[3, 0, 0], [4, -2, 0], [0, 0, 5]],
    'shear': [[3, 1, 0], [4, -2, 0], [0, 2, 0]],
    'zero': [[0, 0, 0], [0, 0, 0], [0, 0, 0]],
    'tiny': [[1e-20, 0, 0], [0, 1e-16, 0], [0, 0, 1e-18]],
    'threshold': [[1e-18, 0, 0], [0, 1e-19, 0], [0, 0, 1e-17]],
    'affine': [[3, 0, 0, 7], [4, -2, 0, -3], [0, 0, 5, 2], [0, 0, 0, 1]],
    'perspective': [[3, 0, 0, 11], [4, -2, 0, -7], [0, 0, 0, 5], [.2, .3, .4, 2]],
    'limits': [[1e6, -1e6, 0, 1e6], [1e6, 1e6, 0, -1e6], [1e6, 0, -1e6, 2], [1, 2, 3, 4]],
}
rng = random.Random(20261102)
for size in (3, 4):
    for index in range(16):
        cases[f'random-{size}-{index}'] = [[rng.uniform(-100, 100) for _ in range(size)]
                                         for _ in range(size)]
rows = lambda matrix: [list(row) for row in matrix]
records = []
for name, values in cases.items():
    matrix = Matrix(values)
    before = rows(matrix)
    result = matrix.normalized()
    assert rows(matrix) == before
    assert matrix.normalize() is None
    assert rows(matrix) == rows(result)
    records.append({'name': name, 'input': before, 'normalized': rows(result)})
output = Path(sys.argv[sys.argv.index('--') + 1])
output.write_text(json.dumps({'blender': bpy.app.version_string, 'cases': records}, indent=2) + '\n')
print(f'MATRIX_NORMALIZATION_REFERENCE_OK: {len(records)} cases')
