"""BMesh triangulation methods, face maps, and retained face identity."""
HB_FACE_ORDER_MESH_PREFIXES=('BMeshTriangulate',)
import bpy,bmesh
for method in ('BEAUTY','FIXED','ALTERNATE','SHORT_EDGE','LONG_EDGE'):
    bm=bmesh.new();vertices=[bm.verts.new(p) for p in ((0,0,0),(3,0,0),(2,1,0),(0,2,0))];face=bm.faces.new(vertices);bm.normal_update()
    result=bmesh.ops.triangulate(bm,faces=[face],quad_method=method)
    assert face.is_valid and len(result['edges'])==1 and len(result['faces'])==2
    assert len(result['face_map'])==2 and len(result['face_map_double'])==0
    assert all(result['face_map'][newface] is face for newface in result['faces'])
    expected=(0,2,3) if method in ('BEAUTY','FIXED','SHORT_EDGE') else (1,3,0)
    assert list(face.verts)==[vertices[i] for i in expected]
    mesh=bpy.data.meshes.new('BMeshTriangulate');bm.to_mesh(mesh)
    obj=bpy.data.objects.new('BMeshTriangulate',mesh);bpy.context.collection.objects.link(obj);bm.free()
for method in ('BEAUTY','EAR_CLIP'):
    for points in (((0,0,0),(2,0,0),(3,1,0),(1,3,0),(-1,1,0)),((0,0,0),(3,0,0),(3,3,0),(1,1,0),(0,3,0))):
        bm=bmesh.new();vertices=[bm.verts.new(p) for p in points];face=bm.faces.new(vertices);face.material_index=2;face.smooth=True;bm.normal_update()
        result=bmesh.ops.triangulate(bm,faces=[face],ngon_method=method)
        assert face.is_valid and len(result['edges'])==2 and len(result['faces'])==3
        assert len(result['face_map'])==3 and len(result['face_map_double'])==0
        assert all(newface.material_index==2 and newface.smooth for newface in result['faces'])
        mesh=bpy.data.meshes.new('BMeshTriangulate');bm.to_mesh(mesh)
        obj=bpy.data.objects.new('BMeshTriangulate',mesh);bpy.context.collection.objects.link(obj);bm.free()
bm=bmesh.new();vertices=[bm.verts.new(p) for p in ((0,0,0),(1,0,0),(0,1,0))];face=bm.faces.new(vertices)
result=bmesh.ops.triangulate(bm,faces=[face]);assert result['faces']==[face] and len(result['face_map'])==0 and len(result['edges'])==0
bm.free()
bm=bmesh.new();vertices=[bm.verts.new(p) for p in ((0,0,0),(1,0,0),(1,1,0),(0,1,0))];face=bm.faces.new(vertices);triangle=bm.faces.new(vertices[:3]);bm.normal_update()
result=bmesh.ops.triangulate(bm,faces=[face],quad_method='FIXED')
assert len(bm.faces)==3 and face.is_valid and triangle.is_valid
assert len(result['edges'])==0 and len(result['face_map_double'])==1
assert len(result['face_map'])==2 and len(result['faces'])==2
bm.free()
bm=bmesh.new();vertices=[bm.verts.new(p) for p in ((0,0,0),(1,0,0),(1,1,0),(0,1,0))];face=bm.faces.new(vertices);bm.normal_update()
bmesh.ops.triangulate(bm,faces=[face])
assert list(face.verts)==[vertices[i] for i in (1,3,0)]
bm.free()
