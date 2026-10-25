"""Planar manifold region inset, depth, boundary and even-offset variants."""
HB_EQUIVALENT_MESH_PREFIXES=('Inset','InsetHole')
import bpy,bmesh
for index,(x,y,thickness,depth,even,boundary) in enumerate(((1,1,.2,0,True,True),(2,2,.2,.3,True,True),(1,1,.2,0,False,True),(2,1,0,.3,True,True),(2,2,.2,0,True,False))):
    bm=bmesh.new();bmesh.ops.create_grid(bm,x_segments=x,y_segments=y,size=1)
    original=list(bm.faces)
    for i,face in enumerate(original):face.material_index=i%2;face.smooth=bool(i%2)
    result=bmesh.ops.inset_region(bm,faces=original,thickness=thickness,depth=depth,use_even_offset=even,use_boundary=boundary)
    assert all(face.is_valid for face in original)
    assert all(face.is_valid for face in result['faces'])
    assert (len(bm.verts),len(bm.edges),len(bm.faces),len(result['faces']))==((8,12,5,4),(17,28,12,8),(8,12,5,4),(12,19,8,6),(9,12,4,0))[index]
    bmesh.ops.translate(bm,verts=list(bm.verts),vec=(index*4,0,0))
    mesh=bpy.data.meshes.new('Inset');bm.to_mesh(mesh)
    obj=bpy.data.objects.new('Inset',mesh);bpy.context.collection.objects.link(obj);bm.free()
bm=bmesh.new();bmesh.ops.create_grid(bm,x_segments=3,y_segments=3,size=1)
original=list(bm.faces);bm.faces.remove(original[4])
bmesh.ops.inset_region(bm,faces=list(bm.faces),thickness=.1,depth=.2,use_boundary=True,use_even_offset=True)
mesh=bpy.data.meshes.new('InsetHole');bm.to_mesh(mesh)
obj=bpy.data.objects.new('InsetHole',mesh);bpy.context.collection.objects.link(obj);bm.free()
bm=bmesh.new();assert bmesh.ops.inset_region(bm)=={'faces':[]};bm.free()
