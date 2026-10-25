"""Plane splits, side clearing, selections, and retained handles."""
HB_EQUIVALENT_MESH_PREFIXES=('Bisect',)
import bpy,bmesh
for inner,outer in ((False,False),(True,False),(False,True),(True,True)):
    bm=bmesh.new();vertices=[bm.verts.new(p) for p in ((-1,-1,0),(1,-1,0),(1,1,0),(-1,1,0))];face=bm.faces.new(vertices)
    result=bmesh.ops.bisect_plane(bm,geom=list(bm.verts)+list(bm.edges)+list(bm.faces),plane_co=(0,0,0),plane_no=(1,0,0),clear_inner=inner,clear_outer=outer,dist=.0001)
    expected=(2,1,0) if inner and outer else ((4,4,1) if inner or outer else (6,7,2))
    assert (len(bm.verts),len(bm.edges),len(bm.faces))==expected
    assert len(result['geom_cut'])==3 and len(result['geom'])==sum(expected)
    assert face.is_valid==(not outer)
    assert [v.is_valid for v in vertices]==[not inner,not outer,not outer,not inner]
    mesh=bpy.data.meshes.new('Bisect');bm.to_mesh(mesh)
    obj=bpy.data.objects.new('Bisect',mesh);bpy.context.collection.objects.link(obj);bm.free()
for kind in ('face','edge','vert','empty'):
    bm=bmesh.new();vertices=[bm.verts.new(p) for p in ((-1,-1,0),(1,-1,0),(1,1,0),(-1,1,0))];face=bm.faces.new(vertices)
    geom={'face':[face],'edge':list(bm.edges),'vert':list(bm.verts),'empty':[]}[kind]
    result=bmesh.ops.bisect_plane(bm,geom=geom,plane_co=(0,0,0),plane_no=(1,0,0))
    assert (len(bm.verts),len(bm.edges),len(bm.faces))==((6,6,1) if kind=='edge' else (4,4,1))
    assert len(result['geom_cut'])==(2 if kind=='edge' else 0)
    assert len(result['geom'])=={'face':1,'edge':8,'vert':4,'empty':0}[kind]
    mesh=bpy.data.meshes.new('Bisect');bm.to_mesh(mesh)
    obj=bpy.data.objects.new('Bisect',mesh);bpy.context.collection.objects.link(obj);bm.free()
for plane in ((1,1,0),(1,0,1)):
    bm=bmesh.new();bmesh.ops.create_cube(bm,size=2,calc_uvs=False)
    result=bmesh.ops.bisect_plane(bm,geom=list(bm.verts)+list(bm.edges)+list(bm.faces),plane_co=(.2,0,0),plane_no=plane,clear_inner=True)
    assert all(sum(v.co[i]*plane[i] for i in range(3))>=.19999 for v in bm.verts)
    mesh=bpy.data.meshes.new('Bisect');bm.to_mesh(mesh)
    obj=bpy.data.objects.new('Bisect',mesh);bpy.context.collection.objects.link(obj);bm.free()
for snap in (False,True):
    bm=bmesh.new();vertices=[bm.verts.new((x,0,0)) for x in (-1,.005,1)];bm.edges.new(vertices[:2]);bm.edges.new(vertices[1:])
    result=bmesh.ops.bisect_plane(bm,geom=list(bm.verts)+list(bm.edges),plane_co=(0,0,0),plane_no=(1,0,0),dist=.01,use_snap_center=snap)
    assert len(result['geom_cut'])==1 and len(result['geom'])==5
    assert abs(vertices[1].co.x-(0 if snap else .005))<1e-7
    bm.free()

bm=bmesh.new();vertices=[bm.verts.new(p) for p in ((-1,-1,0),(1,-1,0),(1,1,0),(-1,1,0))];face=bm.faces.new(vertices)
bmesh.ops.bisect_plane(bm,geom=list(bm.verts)+list(bm.edges)+[face],plane_no=(-1,0,0))
assert face.is_valid and all(v.co.x>=0 for v in face.verts)
bm.free()
