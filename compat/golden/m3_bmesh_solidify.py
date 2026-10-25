"""BMesh shells, folds, empty and wire selections."""
HB_EQUIVALENT_MESH_PREFIXES=('BMeshSolidify',)
import bpy,bmesh
for shape in ('plane','fold','cube'):
    for thickness in (.2,-.2):
        bm=bmesh.new()
        if shape=='cube':bmesh.ops.create_cube(bm,size=2,calc_uvs=False)
        else:
            vertices=[bm.verts.new(p) for p in ((0,0,0),(2,0,0),(2,2,0),(0,2,0))]
            bm.faces.new(vertices)
            if shape=='fold':
                a=bm.verts.new((2,0,2));b=bm.verts.new((2,2,2));bm.faces.new((vertices[1],a,b,vertices[2]))
        bm.normal_update();vertices=list(bm.verts);edges=list(bm.edges);faces=list(bm.faces)
        result=bmesh.ops.solidify(bm,geom=faces,thickness=thickness)
        expected={'plane':(8,12,6,9),'fold':(12,20,10,15),'cube':(16,24,12,26)}[shape]
        assert (len(bm.verts),len(bm.edges),len(bm.faces),len(result['geom']))==expected
        assert all(x.is_valid for group in (vertices,edges,faces) for x in group)
        if shape=='plane':assert all(abs(new_vertex.co.z+thickness)<1e-6 for new_vertex in result['geom'] if isinstance(new_vertex,bmesh.types.BMVert))
        mesh=bpy.data.meshes.new('BMeshSolidify');bm.to_mesh(mesh)
        obj=bpy.data.objects.new('BMeshSolidify',mesh);bpy.context.collection.objects.link(obj);bm.free()
bm=bmesh.new();vertices=[bm.verts.new(p) for p in ((.3,.5,1),(-1,-1,0),(2,-1,.3),(1,2,0),(-1,1,-.2))]
for i in range(4):bm.faces.new((vertices[0],vertices[i+1],vertices[(i+1)%4+1]))
bm.normal_update();result=bmesh.ops.solidify(bm,geom=list(bm.faces),thickness=.17)
assert (len(bm.verts),len(bm.edges),len(bm.faces),len(result['geom']))==(10,20,12,17)
mesh=bpy.data.meshes.new('BMeshSolidify');bm.to_mesh(mesh)
obj=bpy.data.objects.new('BMeshSolidify',mesh);bpy.context.collection.objects.link(obj);bm.free()
for kind in ('edge','vert','empty'):
    bm=bmesh.new();vertices=[bm.verts.new((x,0,0)) for x in (0,1)];edge=bm.edges.new(vertices)
    result=bmesh.ops.solidify(bm,geom={'edge':[edge],'vert':vertices,'empty':[]}[kind],thickness=.2)
    assert (len(bm.verts),len(bm.edges),len(bm.faces),len(result['geom']))=={'edge':(4,4,1,3),'vert':(4,3,0,2),'empty':(2,1,0,0)}[kind]
    bm.free()
bm=bmesh.new();vertices=[bm.verts.new(p) for p in ((0,0,0),(2,0,0),(2,2,0),(0,2,0))];face=bm.faces.new(vertices)
result=bmesh.ops.solidify(bm,geom=[face],thickness=0)
assert (len(bm.verts),len(bm.edges),len(bm.faces),len(result['geom']))==(8,12,6,9)
bm.free()
