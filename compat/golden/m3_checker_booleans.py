"""Boolean expressions return operands; not produces a plain Python bool."""
import bpy
from mathutils import Vector

bpy.ops.mesh.primitive_cube_add()
obj = bpy.context.object
world = bpy.data.worlds.get('Fallback') or bpy.data.worlds.new('Fallback')
world.color = (.1, .2, .3)
bpy.context.scene.world = world
assert (bpy.data.worlds.get('Fallback') or bpy.data.worlds.new('Unused')) is world


def choose(primary, fallback):
    return primary or fallback


def enabled(condition, value):
    return condition and value


obj.location = enabled(True, choose(None, Vector((1, 2, 3))))
points = [] or [Vector((2, 2, 2))]
values = {'scale': False or points[0]}
obj.scale = choose(None, values['scale'])


def direction(value=None or Vector((1, 0, 0))):
    return value.normalized()


assert tuple(direction()) == (1, 0, 0)
flag = not obj
assert flag is False and flag.bit_length() == 0
assert tuple((flag or Vector((1, 2, 3))).normalized()) == tuple(Vector((1, 2, 3)).normalized())

calls = []


def make():
    calls.append('made')
    return Vector((1, 0, 0))


assert tuple(Vector((0, 1, 0)) or make()) == (0, 1, 0)
assert calls == []
assert tuple(None or make()) == (1, 0, 0)
assert calls == ['made']
assert tuple(obj.location) == (1, 2, 3)
assert tuple(obj.scale) == (2, 2, 2)
