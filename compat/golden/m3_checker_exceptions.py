"""Exception target bindings stay local to their Python function."""
import bpy
import bpy as engine
from mathutils import Vector

bpy.ops.mesh.primitive_cube_add(location=(1, 2, 3))
obj = bpy.context.object
vector = Vector((1, 2, 3))


def size():
    try:
        raise ValueError(4)
    except ValueError as obj:
        def captured():
            return obj.args[0]
        return captured()


def nested_handlers():
    try:
        raise ValueError(5)
    except ValueError as obj:
        try:
            raise TypeError(6)
        except (ValueError, TypeError) as vector:
            return obj.args[0] + vector.args[0]


def alias_and_cleanup():
    try:
        raise ValueError(7)
    except ValueError as engine:
        value = engine.args[0]
    try:
        engine
    except UnboundLocalError:
        return value
    raise AssertionError('Exception target was not cleared')


def group_value():
    values = []
    try:
        raise ExceptionGroup('group', [ValueError(2)])
    except* ValueError as obj:
        values.append(obj.exceptions[0].args[0])
    return values[0]


assert size() == 4
assert nested_handlers() == 11
assert alias_and_cleanup() == 7
assert group_value() == 2
assert tuple(vector) == (1, 2, 3)
assert engine.context.object.name == obj.name
assert tuple(obj.location) == (1, 2, 3)
obj.scale = (size(), size(), size())
