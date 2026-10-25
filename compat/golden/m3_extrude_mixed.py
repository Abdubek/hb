"""Mixed region extrusion, preserving oriented topology under index equivalence."""
HB_EQUIVALENT_MESH_PREFIXES=('Mixed region False', 'Mixed region True', 'Mixed edges False', 'Mixed edges True', 'Mixed verts False', 'Mixed verts True', 'Mixed cube False', 'Mixed cube True')
import bpy,bmesh
for mode in ('region','edges','verts','cube'):
    for keep in (False,True):
        bm=bmesh.new()
        if mode=='cube':bmesh.ops.create_cube(bm,size=2)
        else:bmesh.ops.create_grid(bm,x_segments=1,y_segments=1,size=1)
        for i,face in enumerate(bm.faces):face.material_index=i%2;face.smooth=(i%2==0) and not (mode=='cube' and keep)
        first=list(bm.faces)[0]
        if mode=='cube':geom=[first]+list(first.edges)
        elif mode=='region':geom=list(bm.verts)+list(bm.edges)+list(bm.faces)
        elif mode=='edges':geom=list(bm.edges)
        else:geom=list(bm.verts)
        result=bmesh.ops.extrude_face_region(bm,geom=geom,use_keep_orig=keep)
        bmesh.ops.translate(bm,verts=[v for v in result['geom'] if isinstance(v,bmesh.types.BMVert)],vec=(-1,0,0) if mode=='cube' else (0,0,1))
        mesh=bpy.data.meshes.new(f'Mixed {mode} {keep}');bm.to_mesh(mesh)
        obj=bpy.data.objects.new(mesh.name,mesh);bpy.context.collection.objects.link(obj);bm.free()
