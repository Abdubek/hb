"""Edge subdivision grids and return categories, measured in Blender."""
HB_EQUIVALENT_MESH_PREFIXES=('Subdivide',)
import bpy,bmesh
for count in (3,4):
    for cuts in (1,2,3):
        bm=bmesh.new();points=((0,0,0),(2,0,0),(2,2,0),(0,2,0)) if count==4 else ((0,0,0),(2,0,0),(0,2,0))
        vertices=[bm.verts.new(point) for point in points];face=bm.faces.new(vertices);edges=list(bm.edges)
        result=bmesh.ops.subdivide_edges(bm,edges=edges,cuts=cuts,use_grid_fill=True)
        expected={(3,1):(6,9,4,3,3,3,3,6),(3,2):(10,18,9,7,9,8,6,9),(3,3):(15,30,16,12,18,15,9,12),(4,1):(9,12,4,5,4,3,4,8),(4,2):(16,24,9,12,12,8,8,12),(4,3):(25,40,16,21,24,15,12,16)}[count,cuts]
        assert (len(bm.verts),len(bm.edges),len(bm.faces))==expected[:3]
        assert [sum(isinstance(v,cls) for v in result['geom_inner']) for cls in (bmesh.types.BMVert,bmesh.types.BMEdge,bmesh.types.BMFace)]==list(expected[3:6])
        assert [sum(isinstance(v,cls) for v in result['geom_split']) for cls in (bmesh.types.BMVert,bmesh.types.BMEdge)]==list(expected[6:])
        assert len(result['geom'])==expected[3]+expected[1]+expected[2]
        assert face.is_valid and all(e.is_valid for e in edges)
        mesh=bpy.data.meshes.new('Subdivide');bm.to_mesh(mesh)
        obj=bpy.data.objects.new('Subdivide',mesh);bpy.context.collection.objects.link(obj);bm.free()
bm=bmesh.new();a=bm.verts.new((0,0,0));b=bm.verts.new((2,0,0));edge=bm.edges.new((a,b))
result=bmesh.ops.subdivide_edges(bm,edges=[edge],cuts=2)
assert len(bm.verts)==4 and len(bm.edges)==3 and edge.is_valid
assert len(result['geom_inner'])==2 and len(result['geom_split'])==5 and len(result['geom'])==5
assert abs(edge.verts[0].co.x-4/3)<1e-6 and edge.verts[1].co.x==2
bm.free()
for cuts,amount,grid in ((0,4,False),(1,4,False),(2,4,False),(1,1,False),(2,2,False)):
    bm=bmesh.new();vertices=[bm.verts.new(point) for point in ((0,0,0),(2,0,0),(2,2,0),(0,2,0))];face=bm.faces.new(vertices)
    result=bmesh.ops.subdivide_edges(bm,edges=list(face.edges)[:amount],cuts=cuts,use_grid_fill=grid)
    expected={(0,4):(4,4,1,0,0,5),(1,4):(8,8,1,4,12,13),(2,4):(12,12,1,8,20,21),(1,1):(5,5,1,1,3,4),(2,2):(8,10,3,6,10,13)}[cuts,amount]
    assert (len(bm.verts),len(bm.edges),len(bm.faces))==expected[:3]
    assert (len(result['geom_inner']),len(result['geom_split']),len(result['geom']))==expected[3:]
    mesh=bpy.data.meshes.new('Subdivide');bm.to_mesh(mesh)
    obj=bpy.data.objects.new('Subdivide',mesh);bpy.context.collection.objects.link(obj);bm.free()
