"""Components of supported Vector views remain numeric through helpers."""
import bpy, bmesh
from mathutils import Matrix, Vector


def coordinates(value):
    value = Vector(value)
    return value.copy()


def direction(value):
    value = Vector(value)
    return value.normalized()


bpy.ops.mesh.primitive_cube_add(location=(1, 2, 2))
obj = bpy.context.object
assert tuple(coordinates((obj.scale.x, obj.scale.y, obj.scale.z))) == tuple(obj.scale)
assert tuple(coordinates((obj.dimensions.x, obj.dimensions.y, obj.dimensions.z))) == tuple(obj.dimensions)
obj.location = direction((obj.location.x, obj.location.y, obj.location.z))*3
assert tuple(obj.location) == (1, 2, 2)

translation = Matrix.Translation((2, 2, 2)).translation
obj.scale = coordinates((translation.x, translation.y, translation.z))
for mesh_vertex in obj.data.vertices:
    assert tuple(coordinates((mesh_vertex.co.x, mesh_vertex.co.y, mesh_vertex.co.z))) == tuple(mesh_vertex.co)
uv = obj.data.uv_layers.active.data[0].uv
assert tuple(coordinates((uv.x, uv.y))) == tuple(uv)
values = {'uv': (getattr(uv, 'x'), getattr(uv, 'y'))}
assert tuple(coordinates(values['uv'])) == tuple(uv)
assert tuple(coordinates((obj.location.length, obj.location.length_squared))) == (3, 9)

bm = bmesh.new()
bm_vertex = bm.verts.new((1, 2, 2))
assert tuple(coordinates((bm_vertex.co.x, bm_vertex.co.y, bm_vertex.co.z))) == (1, 2, 2)
assert tuple(direction((bm_vertex.co.x, bm_vertex.co.y, bm_vertex.co.z))*3) == (1, 2, 2)
face = bm.faces.new((bm_vertex, bm.verts.new((2, 2, 2)), bm.verts.new((1, 3, 2))))
bm.normal_update()
assert tuple(coordinates((face.normal.x, face.normal.y, face.normal.z))) == (0, 0, 1)
bm.free()
assert tuple(obj.scale) == (2, 2, 2)
