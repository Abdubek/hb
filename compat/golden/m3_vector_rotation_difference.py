"""Blender rotation differences, full roll, operand views and real mesh edits."""
import json
import os
from mathutils import Vector, Quaternion

with open(os.path.join(os.path.dirname(__file__), '../fixtures/vector-rotation-reference.json')) as source:
    reference = json.load(source)
for record in reference['cases']:
    a, b = Vector(record['a']), Vector(record['b'])
    before = (tuple(a), tuple(b))
    result = a.rotation_difference(b)
    assert isinstance(result, Quaternion)
    error = min(max(abs(x-y) for x, y in zip(result, record['quaternion'])),
                max(abs(x+y) for x, y in zip(result, record['quaternion'])))
    assert error <= 2e-6, (record, list(result))
    assert max(abs(x-y) for ar, br in zip(result.to_matrix(), record['matrix'])
               for x, y in zip(ar, br)) <= 2e-6
    assert (tuple(a), tuple(b)) == before
    assert abs(result.magnitude-1) <= 2e-6

for other in ((0, 1, 0), [0, 1, 0, 7], Vector((0, 1, 0))):
    rotated = Vector((1, 0, 0)).rotation_difference(other) @ Vector((1, 0, 0))
    assert (rotated-Vector((0, 1, 0))).length < 2e-6
for a, b in ((Vector((1, 0)), Vector((0, 1, 0))),
             (Vector((1, 0, 0)), Vector((0, 1)))):
    try:
        a.rotation_difference(b)
    except ValueError:
        pass
    else:
        raise AssertionError('2D rotation_difference accepted')

import bpy
bpy.ops.mesh.primitive_cube_add()
obj = bpy.context.object
obj.location = (1, 0, 0)
view_rotation = obj.location.rotation_difference(Vector((0, 1, 0)))
assert ((view_rotation @ Vector((1, 0, 0)))-Vector((0, 1, 0))).length < 2e-6
assert tuple(obj.location) == (1, 0, 0)
obj.location = (0, 0, 0)
rotation = Vector((0, 0, 1)).rotation_difference(Vector((1, 0, 0)))
for vertex in obj.data.vertices:
    x, y, z = vertex.co
    vertex.co = rotation @ Vector((x, y, z))
    assert max(abs(a-b) for a, b in zip(vertex.co, (z, y, -x))) < 2e-6
