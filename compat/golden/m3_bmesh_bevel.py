"""BMesh bevel of complete cuboids, measured before implementation."""
HB_EQUIVALENT_MESH_PREFIXES=('BMeshBevel',)
import bpy,bmesh
for index,segments in enumerate((1,2,3,8)):
    bm=bmesh.new();bmesh.ops.create_cube(bm,size=2)
    original_faces=list(bm.faces);original_edges=list(bm.edges);original_verts=list(bm.verts)
    result=bmesh.ops.bevel(bm,geom=original_edges,offset=.2,segments=segments,profile=.5,affect='EDGES')
    counts=((24,48,26,20),(56,108,54,48),(96,192,98,92),(488,972,486,480))[index]
    assert (len(bm.verts),len(bm.edges),len(bm.faces),len(result['faces']))==counts
    assert len(result['edges'])==counts[1] and len(result['verts'])==counts[0]
    assert all(not v.is_valid for group in (original_faces,original_edges,original_verts) for v in group)
    bmesh.ops.translate(bm,verts=list(bm.verts),vec=(index*4,0,0))
    mesh=bpy.data.meshes.new('BMeshBevel');bm.to_mesh(mesh)
    obj=bpy.data.objects.new('BMeshBevel',mesh);bpy.context.collection.objects.link(obj);bm.free()
bm=bmesh.new();bmesh.ops.create_cube(bm,size=2)
vertices=list(bm.verts)
assert bmesh.ops.bevel(bm)=={'faces':[],'edges':[],'verts':[]}
assert bmesh.ops.bevel(bm,geom=list(bm.edges),offset=0)=={'faces':[],'edges':[],'verts':[]}
assert all(v.is_valid for v in vertices);bm.free()
