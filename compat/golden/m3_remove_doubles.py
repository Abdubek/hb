"""Vertex merge selection, proximity chains and topology cleanup."""
HB_EQUIVALENT_MESH_PREFIXES=('RemoveDoubles',)
import bpy,bmesh
bm=bmesh.new()
vertices=[bm.verts.new(co) for co in ((0,0,0),(1,0,0),(1,1,0),(0,0,0),(1,1,0),(0,1,0))]
bm.faces.new(vertices[:3]);bm.faces.new(vertices[3:])
assert bmesh.ops.remove_doubles(bm,verts=vertices,dist=.001) is None
assert len(bm.verts)==4 and len(bm.faces)==2 and len(bm.edges)==5
mesh=bpy.data.meshes.new('RemoveDoubles');bm.to_mesh(mesh)
obj=bpy.data.objects.new('RemoveDoubles',mesh);bpy.context.collection.objects.link(obj);bm.free()
for coords in ((0,.09,.18,.27,.36),(0,0,0),(0,.1,.2)):
    bm=bmesh.new();vertices=[bm.verts.new((x,0,0)) for x in coords]
    bmesh.ops.remove_doubles(bm,verts=vertices,dist=.1)
    expected=(.09,.36) if len(coords)==5 else ((0,) if coords==(0,0,0) else coords)
    assert len(bm.verts)==len(expected)
    assert all(abs(v.co.x-x)<1e-6 for v,x in zip(bm.verts,expected))
    if coords==(0,0,0):assert [v.is_valid for v in vertices]==[False,True,False]
    bm.free()
for distance in (0,.1):
    bm=bmesh.new();vertices=[bm.verts.new((0,y,0)) for y in (0,.1,.2)]
    bmesh.ops.remove_doubles(bm,verts=vertices,dist=distance)
    assert len(bm.verts)==(3 if distance==0 else 1)
    bm.free()
bm=bmesh.new();vertices=[bm.verts.new(co) for co in ((0,0,0),(.01,0,0),(0,1,0))]
face=bm.faces.new(vertices);bmesh.ops.remove_doubles(bm,verts=vertices,dist=.1)
assert (len(bm.verts),len(bm.edges),len(bm.faces))==(2,1,0)
assert not face.is_valid;bm.free()
bm=bmesh.new();vertices=[bm.verts.new((x,y,0)) for x,y in ((-.01,0),(-1,1),(-2,0),(-1,-1),(.01,0),(1,-1),(2,0),(1,1))]
bm.faces.new(vertices);bmesh.ops.remove_doubles(bm,verts=vertices,dist=.05)
assert len(bm.verts)==7 and len(bm.faces)==2 and len(bm.edges)==8
mesh=bpy.data.meshes.new('RemoveDoubles');bm.to_mesh(mesh)
obj=bpy.data.objects.new('RemoveDoubles',mesh);bpy.context.collection.objects.link(obj);bm.free()
bm=bmesh.new();vertices=[bm.verts.new((0,0,0)) for _ in range(3)]
bmesh.ops.remove_doubles(bm,verts=vertices[:2],dist=.1)
assert [v.is_valid for v in vertices]==[False,True,True];bm.free()
