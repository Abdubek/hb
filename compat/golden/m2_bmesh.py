"""Editable mesh contract, written before the bmesh implementation."""
HB_SYMBOLS = {
'bmesh.new':'Create a standalone editable mesh, use_operators=True/False',
'bmesh.types.BMesh.verts':'Mutable vertex sequence', 'bmesh.types.BMesh.edges':'Mutable edge sequence', 'bmesh.types.BMesh.faces':'Mutable face sequence',
'bmesh.types.BMesh.verts.new':'Add a vertex with a 3D coordinate', 'bmesh.types.BMesh.edges.new':'Add an edge between distinct vertices', 'bmesh.types.BMesh.faces.new':'Add a face using distinct vertices',
'bmesh.types.BMesh.verts.ensure_lookup_table':'Enable indexed vertex access', 'bmesh.types.BMesh.edges.ensure_lookup_table':'Enable indexed edge access', 'bmesh.types.BMesh.faces.ensure_lookup_table':'Enable indexed face access',
'bmesh.types.BMesh.verts.index_update':'Update vertex indices', 'bmesh.types.BMesh.edges.index_update':'Update edge indices', 'bmesh.types.BMesh.faces.index_update':'Update face indices',
'bmesh.types.BMesh.verts.remove':'Remove vertex and incident geometry', 'bmesh.types.BMesh.edges.remove':'Remove edge and incident faces', 'bmesh.types.BMesh.faces.remove':'Remove face, retaining edges and vertices',
'bmesh.types.BMesh.free':'Invalidate the editable mesh and its elements',
'bmesh.types.BMesh.normal_update':'Recalculate vertex and face normals',
'bmesh.types.BMVert.co':'Writable Vector coordinate', 'bmesh.types.BMVert.index':'Mutable index, -1 before index_update', 'bmesh.types.BMVert.is_valid':'Element validity',
'bmesh.types.BMEdge.verts':'The two edge vertices', 'bmesh.types.BMEdge.index':'Mutable index',
'bmesh.types.BMFace.verts':'Ordered face vertices', 'bmesh.types.BMFace.edges':'Ordered boundary edges', 'bmesh.types.BMFace.normal':'Face normal after normal_update',
'bmesh.types.BMFace.material_index':'Material slot index', 'bmesh.types.BMFace.smooth':'Smooth shading flag',
'bmesh.ops.translate':'Translate vertices by a Vector', 'bmesh.ops.scale':'Scale vertex components',
'bmesh.ops.delete':'Delete selected VERTS, EDGES, FACES_ONLY geometry',
}
import bpy,bmesh
from mathutils import Vector
bm=bmesh.new()
a=bm.verts.new((0,0,0));b=bm.verts.new((1,0,0));c=bm.verts.new((1,1,0));d=bm.verts.new((0,1,0))
assert a.index==-1
f=bm.faces.new((a,b,c,d));assert len(bm.edges)==4
bm.verts.ensure_lookup_table();bm.edges.ensure_lookup_table();bm.faces.ensure_lookup_table()
bm.verts.index_update();bm.edges.index_update();bm.faces.index_update()
assert bm.verts[2] is c and c.index==2 and bm.faces[0] is f
assert len(f.edges)==4 and tuple(f.verts)==(a,b,c,d) and len(bm.edges[0].verts)==2
bmesh.ops.translate(bm,verts=bm.verts,vec=Vector((1,2,3)))
bmesh.ops.scale(bm,verts=bm.verts,vec=(2,1,1))
a.co.z=4;assert tuple(a.co)==(2,2,4)
a.co.z=3
bm.normal_update();assert (f.normal-Vector((0,0,1))).length<1e-6
f.smooth=True;f.material_index=2
mesh=bpy.data.meshes.new('Editable');bm.to_mesh(mesh)
obj=bpy.data.objects.new('Editable',mesh);bpy.context.collection.objects.link(obj)
assert mesh.polygons[0].use_smooth and mesh.polygons[0].material_index==2
bm.free();assert not a.is_valid
other=bmesh.new(use_operators=False);other.from_mesh(mesh)
other.verts.ensure_lookup_table();assert tuple(other.verts[0].co)==(2,2,3)
other.faces.ensure_lookup_table();other.faces.remove(other.faces[0]);assert len(other.edges)==4
other.edges.ensure_lookup_table();other.edges.remove(other.edges[0]);assert len(other.edges)==3
other.verts.ensure_lookup_table();other.verts.remove(other.verts[0]);assert len(other.verts)==3
other.free()
bm=bmesh.new();a=bm.verts.new((0,0,0));b=bm.verts.new((1,0,0));edge=bm.edges.new((a,b));assert len(bm.edges)==1
bmesh.ops.delete(bm,geom=[a],context='VERTS');assert not a.is_valid and len(bm.edges)==0
bm.free()

bm=bmesh.new();a=bm.verts.new((0,0,0));b=bm.verts.new((1,0,0));edge=bm.edges.new((a,b))
bmesh.ops.delete(bm,geom=[edge],context='EDGES');assert len(bm.edges)==0 and len(bm.verts)==0
bm.free()
