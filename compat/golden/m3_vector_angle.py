"""Captured Vector.angle semantics and an angle-driven mesh edit."""
import json
import math
import os
from mathutils import Vector

with open(os.path.join(os.path.dirname(__file__), '../fixtures/vector-angle-reference.json')) as source:
    reference = json.load(source)
for row in reference['cases']:
    a, b = Vector(row['a']), Vector(row['b'])
    before = (tuple(a), tuple(b))
    for other in (b, tuple(b), list(b)):
        if 'error' in row:
            try:
                a.angle(other)
            except ValueError:
                pass
            else:
                raise AssertionError('Zero direction accepted')
            token = object()
            assert a.angle(other, token) is token
            assert a.angle(other, None) is None
        else:
            angle = a.angle(other)
            assert abs(angle-row['angle']) <= 5e-7, (row, angle)
    assert (tuple(a), tuple(b)) == before

# W never contributes, including nonfinite values. Active nonfinite axes yield NaN.
for value in (float('nan'), float('inf'), -float('inf')):
    assert abs(Vector((1, 0, 0, value)).angle((0, 1, 0, 2))-math.pi/2) < 5e-7
    assert math.isnan(Vector((value, 0, 0)).angle((0, 1, 0)))
for other, exception in ((None, TypeError), (3, TypeError), ('bad', TypeError),
                         ((1,), ValueError), ((1, 2, 3, 4, 5), ValueError),
                         (['bad', 0, 0], TypeError), ((1, 2), ValueError)):
    try:
        Vector((1, 0, 0)).angle(other)
    except exception:
        pass
    else:
        raise AssertionError('Invalid argument accepted')

import bpy
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete()
bpy.ops.mesh.primitive_cube_add()
obj = bpy.context.object
obj.name = 'Angles'
obj.location = (1, 0, 0)
view = obj.location
assert abs(view.angle((0, 1, 0))-math.pi/2) < 5e-7
assert tuple(view) == (1, 0, 0)
assert Vector().angle((1, 0, 0), obj) is obj
obj.location = (0, 0, 0)
angle = Vector((1, 0, 0, 1)).angle((0, 1, 0, 1))
assert angle > 1
for vertex in obj.data.vertices:
    vertex.co.z += 2
