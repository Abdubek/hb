"""Dictionary get/pop defaults retain API values without changing Python semantics."""
import bpy
from mathutils import Matrix, Vector


def location(config, fallback=Vector((1, 2, 3))):
    return config.get('location', fallback)


def transform(config, fallback):
    return config.pop('matrix', fallback)


config = {}
bpy.ops.mesh.primitive_cube_add()
obj = bpy.context.object
offsets = config.get('offsets', [Vector((1, 0, 0))])
obj.location = location(config) + offsets[0]
matrix = transform(config, Matrix.Diagonal((2, 2, 2)))
for vertex in obj.data.vertices:
    vertex.co = matrix @ vertex.co
world = config.get('world', bpy.data.worlds.new('Fallback'))
world.color = (.1, .2, .3)
bpy.context.scene.world = world
assert config == {}  # Neither missing-key operation inserts the default.
assert tuple(obj.location) == (2, 2, 3)
assert sorted({vertex.co.z for vertex in obj.data.vertices}) == [-2, 2]

stored = Vector((4, 5, 6))
fallback = Vector((7, 8, 9))
values = {'point': stored}
get = values.get
assert get('point', fallback) is stored and values['point'] is stored
assert get('missing', fallback) is fallback and 'missing' not in values
assert get('missing') is None
pop = values.pop
assert pop('point', fallback) is stored and 'point' not in values
assert pop('missing', fallback) is fallback
assert pop('missing', None) is None
try:
    pop('missing')
except KeyError:
    pass
else:
    raise AssertionError('pop without a default must raise for a missing key')

calls = []


def make():
    calls.append('made')
    return Vector((0, 0, 1))


values = {'point': stored}
assert values.get('point', make()) is stored
assert values.pop('point', make()) is stored
assert calls == ['made', 'made']  # Defaults are evaluated even on a hit.
