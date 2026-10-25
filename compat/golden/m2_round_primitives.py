"""Round primitive contracts, authored before implementation against Blender."""
HB_SYMBOLS={
'bpy.ops.mesh.primitive_uv_sphere_add':'WORLD/CURSOR UV sphere in object or single-mesh EDIT construction; segments/rings/radius, explicit scale including zero; zero radius requires calc_uvs=False and keeps an unmerged quad grid; construction limit 100000 vertices',
'bpy.ops.mesh.primitive_cone_add':'WORLD/CURSOR cone/frustum in object or single-mesh EDIT construction; vertices/radii/depth and caps, finite degenerate wire geometry; explicit positive/zero scale and optional UVs; negative scale requires calc_uvs=False',
}
HB_EQUIVALENT_MESH_PREFIXES=('Sphere',)
import bpy
for segments,rings in ((3,3),(4,4),(5,3),(6,5),(7,7),(8,6),(16,8),(24,12),(32,16),(64,32)):
    bpy.ops.mesh.primitive_uv_sphere_add(segments=segments,ring_count=rings,radius=.7,location=(segments,rings,1),rotation=(.2,.3,.4),scale=(2,.5,1))
    obj=bpy.context.object
    assert len(obj.data.vertices)==segments*(rings-1)+2
    assert len(obj.data.polygons)==segments*rings
    assert tuple(obj.scale)==(1,1,1)
for n in (3,4,5,8,16):
    for r1,r2 in ((1,0),(0,1),(1,.4)):
        for fill in ('NGON','TRIFAN','NOTHING'):
            bpy.ops.mesh.primitive_cone_add(vertices=n,radius1=r1,radius2=r2,depth=1.3,end_fill_type=fill,location=(n,r1,r2))
            obj=bpy.context.object
            assert obj.type=='MESH' and len(obj.data.uv_layers)==1
bpy.ops.mesh.primitive_uv_sphere_add(calc_uvs=False)
assert len(bpy.context.object.data.uv_layers)==0
bpy.ops.mesh.primitive_cone_add(calc_uvs=False)
assert len(bpy.context.object.data.uv_layers)==0

bpy.ops.mesh.primitive_cone_add(vertices=7,radius1=.8,radius2=.3,depth=2,scale=(-2,.5,1.5),rotation=(.3,.1,.2),calc_uvs=False)
assert tuple(bpy.context.object.scale)==(1,1,1)
bpy.ops.mesh.primitive_uv_sphere_add(segments=1,ring_count=1,radius=.3)
assert len(bpy.context.object.data.vertices)==8
