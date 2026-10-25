import bpy
bpy.ops.mesh.primitive_uv_sphere_add(segments=3,ring_count=3,radius=0,calc_uvs=False)
o=bpy.context.object;o.name='0'
assert len(o.data.vertices)==16
assert len(o.data.polygons)==9
bpy.ops.mesh.primitive_uv_sphere_add(segments=3,ring_count=4,radius=0,calc_uvs=False)
o=bpy.context.object;o.name='1'
assert len(o.data.vertices)==20
assert len(o.data.polygons)==12
bpy.ops.mesh.primitive_uv_sphere_add(segments=3,ring_count=6,radius=0,calc_uvs=False)
o=bpy.context.object;o.name='2'
assert len(o.data.vertices)==28
assert len(o.data.polygons)==18
bpy.ops.mesh.primitive_uv_sphere_add(segments=8,ring_count=3,radius=0,calc_uvs=False)
o=bpy.context.object;o.name='3'
assert len(o.data.vertices)==36
assert len(o.data.polygons)==24
bpy.ops.mesh.primitive_uv_sphere_add(segments=8,ring_count=4,radius=0,calc_uvs=False)
o=bpy.context.object;o.name='4'
assert len(o.data.vertices)==45
assert len(o.data.polygons)==32
bpy.ops.mesh.primitive_uv_sphere_add(segments=8,ring_count=6,radius=0,calc_uvs=False)
o=bpy.context.object;o.name='5'
assert len(o.data.vertices)==63
assert len(o.data.polygons)==48
bpy.ops.mesh.primitive_uv_sphere_add(segments=12,ring_count=3,radius=0,calc_uvs=False)
o=bpy.context.object;o.name='6'
assert len(o.data.vertices)==52
assert len(o.data.polygons)==36
bpy.ops.mesh.primitive_uv_sphere_add(segments=12,ring_count=4,radius=0,calc_uvs=False)
o=bpy.context.object;o.name='7'
assert len(o.data.vertices)==65
assert len(o.data.polygons)==48
bpy.ops.mesh.primitive_uv_sphere_add(segments=12,ring_count=6,radius=0,calc_uvs=False)
o=bpy.context.object;o.name='8'
assert len(o.data.vertices)==91
assert len(o.data.polygons)==72
