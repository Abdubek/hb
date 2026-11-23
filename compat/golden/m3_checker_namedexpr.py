"""Assignment expressions preserve identity, scope and normal modeling results."""
import bpy
from mathutils import Matrix, Vector

bpy.ops.mesh.primitive_cube_add()
obj = bpy.context.object
if (world := bpy.data.worlds.get('World')) is not None:
    world.use_nodes = False
    world.color = (.1, .2, .3)
    bpy.context.scene.world = world

obj.location = (point := Vector((1, 2, 3)))
assert tuple(point) == (1, 2, 3)
offsets = [(offset := Vector((x, 0, 0))) for x in (0, 1)]
assert offset is offsets[-1]
obj.location += offset


def configured_scale():
    # Comprehension walrus targets belong to the containing function, unlike
    # their iteration targets. Reusing "point" must not affect the global Vector.
    values = [(point := Matrix.Diagonal((2, 2, 2))) for _ in range(1)]
    assert point is values[0]
    return point @ Vector((1, 1, 1))


obj.scale = configured_scale()
assert tuple(point.normalized()) == tuple(Vector((1, 2, 3)).normalized())

queue = [Vector((0, 0, 0))]
while (last := queue.pop() if queue else None) is not None:
    assert tuple(last) == (0, 0, 0)
assert last is None


def capture():
    current = None

    def update():
        nonlocal current
        return (current := Vector((2, 2, 2)))

    assert update() is current
    return current


assert tuple(capture()) == tuple(obj.scale)
global_point = None


def update_global():
    global global_point
    return (global_point := Vector((2, 2, 3)))


assert update_global() is global_point
assert tuple(global_point) == tuple(obj.location)
calls = []


def make():
    calls.append('made')
    return Vector((1, 0, 0))


values = {'point': (bound := make())}
assert values['point'] is bound and calls == ['made']
assert tuple(obj.location) == (2, 2, 3)
assert tuple(obj.scale) == (2, 2, 2)
