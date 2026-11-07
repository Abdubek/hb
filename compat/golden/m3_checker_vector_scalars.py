"""Vector scalar properties remain numbers through coordinate helper calls."""
import bpy
from mathutils import Vector


def coordinates(value):
    value = Vector(value)
    assert value.length > 0
    return value


def distance(start, end):
    start, end = Vector(start), Vector(end)
    delta = end - start
    return delta.length


v = Vector((1, 2, 2, 4))
for values in ((v.x, v.y, v.z), (v.w, 0, 0),
               (v.length, v.length_squared, 0),
               (getattr(v, 'x'), getattr(v, 'y'), getattr(v, 'z'))):
    assert tuple(coordinates(values)) == values

for offset in (0, 5):
    size = distance((v.x, v.y, v.z), (v.x+3, v.y+4, v.z))
    assert size == 5
    bpy.ops.mesh.primitive_cube_add(size=size, location=(offset, 0, 0))
