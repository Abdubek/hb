"""Helper defaults preserve API provenance and defining lexical scope."""
import bpy
from mathutils import Vector


def position(point=Vector((1, 2, 3)), /):
    return point


def offset(required, point=Vector((0, 0, 0)), *, direction=Vector((0, 0, 0))):
    return required + point + direction


def overridden(point=bpy.context.object):
    return point.normalized()


def overridden_keyword(*, point=bpy.context.object):
    return point.normalized()


assert tuple(overridden(Vector((1, 0, 0)))) == (1, 0, 0)
assert tuple(overridden(point=Vector((0, 1, 0)))) == (0, 1, 0)
assert tuple(overridden_keyword(point=Vector((0, 0, 1)))) == (0, 0, 1)
assert tuple(offset(Vector((1, 2, 3)))) == (1, 2, 3)
assert tuple(offset(Vector((1, 2, 3)), point=Vector((1, 0, 0)))) == (2, 2, 3)

# Each default expression uses the defining function's binding, even when the
# parameter has the same name and a global API value has a different type.
value = bpy.context.object


def scale():
    from mathutils import Vector as make
    value = make((2, 2, 2))

    def inner(value=value, /, *, other=make((0, 0, 0))):
        return value + other

    return inner()


points = []


def remember(values=points):
    values.append(position())


remember()
assert tuple(points[0]) == (1, 2, 3)
bpy.ops.mesh.primitive_cube_add(location=points[0])
bpy.context.object.scale = scale()
assert tuple(bpy.context.object.location) == (1, 2, 3)
assert tuple(bpy.context.object.scale) == (2, 2, 2)
