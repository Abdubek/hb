"""Editable cube/grid creation contract, authored before implementation."""
HB_SYMBOLS={
'bmesh.ops.create_cube':'Create cube topology in a standalone BMesh; size, calc_uvs=False, no matrix',
'bmesh.ops.create_grid':'Create an XY grid with x/y segment counts; size, calc_uvs=False, no matrix',
}
import bpy,bmesh
for size in (.5,2,3):
    bm=bmesh.new();result=bmesh.ops.create_cube(bm,size=size)
    assert len(result['verts'])==8 and len(bm.verts)==8 and len(bm.faces)==6
    bmesh.ops.translate(bm,verts=result['verts'],vec=(0,0,1))
    mesh=bpy.data.meshes.new('CubeGrid');bm.to_mesh(mesh)
    obj=bpy.data.objects.new('EditableCube',mesh);bpy.context.collection.objects.link(obj);bm.free()
for x,y,size in [(1,1,1),(2,3,1),(4,2,2.5)]:
    bm=bmesh.new();result=bmesh.ops.create_grid(bm,x_segments=x,y_segments=y,size=size,calc_uvs=False)
    assert len(result['verts'])==(x+1)*(y+1) and len(bm.faces)==x*y
    mesh=bpy.data.meshes.new('Grid');bm.to_mesh(mesh)
    obj=bpy.data.objects.new('EditableGrid',mesh);bpy.context.collection.objects.link(obj);bm.free()
# New operators append and return only the newly created vertices.
bm=bmesh.new();existing=bm.verts.new((9,9,9))
result=bmesh.ops.create_cube(bm,size=1,calc_uvs=False)
assert existing not in result['verts'] and len(bm.verts)==9
bm.free()
