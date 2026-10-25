"""Ico-sphere topology, seam UVs and construction transforms measured in Blender."""
HB_EQUIVALENT_MESH_PREFIXES=('Icosphere',)
import bpy
for subdivisions in (1,2,3,4):
    bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=subdivisions,radius=.7,location=(subdivisions,2,3),rotation=(.2,.3,.4))
    obj=bpy.context.object
    assert len(obj.data.vertices)==10*4**(subdivisions-1)+2
    assert len(obj.data.polygons)==20*4**(subdivisions-1)
    assert all(len(f.vertices)==3 for f in obj.data.polygons)
    assert len(obj.data.uv_layers)==1
    assert tuple(obj.scale)==(1,1,1)
bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=2,radius=1.3,scale=(2,.5,1.5),calc_uvs=False)
assert len(bpy.context.object.data.uv_layers)==0
assert tuple(bpy.context.object.scale)==(1,1,1)
bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=1,radius=.4,scale=(-1,2,.5))
assert len(bpy.context.object.data.uv_layers)==1
