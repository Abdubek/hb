"""Standalone round construction, authored before implementation."""
HB_SYMBOLS={
'bmesh.ops.create_uvsphere':'Append UV sphere; u_segments/v_segments/radius; stable indices (documented deviation), no matrix or editable UVs',
'bmesh.ops.create_cone':'Append cone/frustum with segments/radius1/radius2/depth/cap_ends/cap_tris; no matrix or editable UVs',
'bmesh.ops.create_circle':'Append circle with segments/radius/cap_ends/cap_tris; no matrix or editable UVs',
}
HB_EQUIVALENT_MESH_PREFIXES=('EditableSphere',)
import bpy,bmesh
for n,rings in ((3,3),(5,4),(8,6)):
    bm=bmesh.new();sentinel=bm.verts.new((9,9,9))
    result=bmesh.ops.create_uvsphere(bm,u_segments=n,v_segments=rings,radius=.8)
    assert len(result['verts'])==n*(rings-1)+2 and sentinel not in result['verts']
    mesh=bpy.data.meshes.new('EditableSphere');bm.to_mesh(mesh);bm.free()
    obj=bpy.data.objects.new('Sphere',mesh);bpy.context.collection.objects.link(obj)
for n in (3,4,7):
    for caps,tris in ((False,False),(True,False),(True,True)):
        for radii in ((1,0),(0,1),(1,.4)):
            bm=bmesh.new()
            result=bmesh.ops.create_cone(bm,segments=n,radius1=radii[0],radius2=radii[1],depth=1.5,cap_ends=caps,cap_tris=tris)
            assert len(result['verts'])==len(bm.verts)
            mesh=bpy.data.meshes.new('EditableCone');bm.to_mesh(mesh);bm.free()
            obj=bpy.data.objects.new('Cone',mesh);bpy.context.collection.objects.link(obj)
        bm=bmesh.new();result=bmesh.ops.create_circle(bm,segments=n,radius=.7,cap_ends=caps,cap_tris=tris)
        assert len(result['verts'])==len(bm.verts)
        mesh=bpy.data.meshes.new('EditableCircle');bm.to_mesh(mesh);bm.free()
        obj=bpy.data.objects.new('Circle',mesh);bpy.context.collection.objects.link(obj)
