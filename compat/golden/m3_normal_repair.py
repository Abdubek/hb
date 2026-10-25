"""Open manifold and partial-selection winding repair."""
import bpy,bmesh
for mode in ('plane','open_cube','partial_cube'):
    for offset in ((0,0,0),(3,2,1),(-3,-2,-1)):
        bm=bmesh.new()
        if mode=='plane':bmesh.ops.create_grid(bm,x_segments=2,y_segments=2,size=1)
        else:bmesh.ops.create_cube(bm,size=2)
        if mode=='open_cube':bm.faces.remove(list(bm.faces)[-1])
        # Rebuild reversed polygons using the public creation/removal subset.
        for face in list(bm.faces):
            verts=tuple(face.verts);bm.faces.remove(face);bm.faces.new(tuple(reversed(verts)))
        bmesh.ops.translate(bm,verts=list(bm.verts),vec=offset)
        faces=list(bm.faces)
        bmesh.ops.recalc_face_normals(bm,faces=faces[:2] if mode=='partial_cube' else faces)
        mesh=bpy.data.meshes.new(f'Repair {mode} {offset}');bm.to_mesh(mesh)
        obj=bpy.data.objects.new(mesh.name,mesh);bpy.context.collection.objects.link(obj);bm.free()
