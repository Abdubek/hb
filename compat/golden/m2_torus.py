"""Torus contract, authored and run in Blender before implementation."""
HB_SYMBOLS={
'bpy.ops.mesh.primitive_torus_add':'WORLD/CURSOR torus in object or existing single-mesh EDIT context; segments 3..256, MAJOR_MINOR or EXT_INT, 0 <= minor <= major including zero, optional UVs; self-intersecting radii excluded',
}
import bpy
for n,m in ((3,3),(3,4),(4,3),(5,7),(7,5),(8,8),(13,9),(48,12),(256,3),(3,256)):
    result=bpy.ops.mesh.primitive_torus_add(major_segments=n,minor_segments=m,major_radius=1.2,minor_radius=.3,location=(n/10,m/10,0),rotation=(.2,.3,.4))
    assert result=={'FINISHED'}
    o=bpy.context.object
    assert o.name[:5]=='Torus' and len(o.data.vertices)==n*m
    assert len(o.data.polygons)==n*m and len(o.data.uv_layers)==1
    assert all(abs(v-1)<1e-6 for v in o.scale) and o.select_get()
bpy.ops.mesh.primitive_torus_add()
assert len(bpy.context.object.data.vertices)==576
bpy.ops.mesh.primitive_torus_add(major_segments=0,minor_segments=999,generate_uvs=False)
assert len(bpy.context.object.data.vertices)==3*256
assert len(bpy.context.object.data.uv_layers)==0
for outer,inner in ((2,1),(.1,.02),(8,3)):
    bpy.ops.mesh.primitive_torus_add(mode='EXT_INT',abso_major_rad=outer,abso_minor_rad=inner,major_segments=9,minor_segments=5)
bpy.ops.mesh.primitive_torus_add(major_segments=7,minor_segments=5,major_radius=100,minor_radius=20,generate_uvs=False)
