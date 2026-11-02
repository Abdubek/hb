"""Replay Blender column normalization and apply it to actual mesh coordinates."""
import json
import math
import os
from mathutils import Matrix

with open(os.path.join(os.path.dirname(__file__), '../fixtures/matrix-normalization-reference.json')) as source:
    reference = json.load(source)

def close(actual, expected):
    assert len(actual) == len(expected)
    for a, b in zip(actual, expected):
        assert math.isclose(a, b, rel_tol=2e-6, abs_tol=2e-6), (a, b)

for record in reference['cases']:
    matrix = Matrix(record['input'])
    original = [list(row) for row in matrix]
    result = matrix.normalized()
    assert result is not matrix
    assert [list(row) for row in matrix] == original
    held_row = matrix[0]
    assert matrix.normalize() is None
    for actual, copied, expected in zip(matrix, result, record['normalized']):
        close(actual, expected)
        close(copied, expected)
    close(held_row, record['normalized'][0])
    if len(matrix) == 4:
        assert [row[3] for row in matrix] == [row[3] for row in original]
    result[0][0] += .125
    close(matrix[0], record['normalized'][0])

# Normalization does not orthogonalize a shear or remove a reflection.
shear = Matrix(((3, 1, 0), (4, -2, 0), (0, 2, 0))).normalized()
assert abs(sum(shear[i][0] * shear[i][1] for i in range(3))) > .3
assert Matrix.Diagonal((-2, 3, 4)).normalized().determinant() < 0
for values in (((1, 0), (0, 1)), ((1, 0, 0), (0, 1, 0))):
    matrix = Matrix(values)
    before = [list(row) for row in matrix]
    for operation in (matrix.normalize, matrix.normalized):
        try:
            operation()
        except (ValueError, SystemError):
            pass  # Blender 5.2 raises SystemError for its unsupported 2x2 case.
        else:
            raise AssertionError('Normalization requires a 3x3 or 4x4 matrix')
        assert [list(row) for row in matrix] == before

import bpy
bpy.ops.mesh.primitive_cube_add()
transform = Matrix(((3, 0, 0, 7), (4, -2, 0, -3), (0, 0, 5, 2), (0, 0, 0, 1))).normalized()
for vertex in bpy.context.object.data.vertices:
    x, y, z = vertex.co
    vertex.co = transform @ vertex.co
    close(vertex.co, (.6*x + 7, .8*x - y - 3, z + 2))
