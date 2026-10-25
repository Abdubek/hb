"""Catmull-Clark/SIMPLE refinement through level three, authored for Blender first."""
HB_EQUIVALENT_MESH_PREFIXES=('Subdivision cube','Subdivision plane','Subdivision patch','Subdivision triangle')
HB_SYMBOLS={
'bpy.types.SubsurfModifier.name':'Modifier name',
'bpy.types.SubsurfModifier.type':'SUBSURF',
'bpy.types.SubsurfModifier.subdivision_type':'CATMULL_CLARK or SIMPLE',
'bpy.types.SubsurfModifier.quality':'Default quality 3',
'bpy.types.SubsurfModifier.uv_smooth':'PRESERVE_BOUNDARIES',
'bpy.types.SubsurfModifier.boundary_smooth':'ALL or PRESERVE_CORNERS',
'bpy.types.SubsurfModifier.use_limit_surface':'Evaluate the limit surface or finite refinement',
'bpy.types.SubsurfModifier.show_only_control_edges':'Control edge display flag; does not change exported surface',
'bpy.types.SubsurfModifier.show_viewport':'Viewport and glTF evaluation flag',
'bpy.types.SubsurfModifier.show_render':'Preview evaluation flag',
}
import bpy

def subdivide(obj,method,level,limit=True,boundary='ALL',apply=True):
    bpy.context.view_layer.objects.active=obj
    m=obj.modifiers.new('Smooth','SUBSURF')
    assert m.type=='SUBSURF' and m.subdivision_type=='CATMULL_CLARK'
    assert m.levels==1 and m.render_levels==2 and m.quality==3 and m.uv_smooth=='PRESERVE_BOUNDARIES'
    assert m.boundary_smooth=='ALL' and m.use_limit_surface and m.use_creases and m.show_only_control_edges
    m.subdivision_type=method;m.levels=level;m.render_levels=3;m.use_limit_surface=limit;m.boundary_smooth=boundary
    m.quality=3;m.uv_smooth='PRESERVE_BOUNDARIES';m.use_creases=False;m.use_creases=True
    m.show_only_control_edges=False;m.show_only_control_edges=True;m.name='Refine'
    m.show_viewport=False;m.show_viewport=True;m.show_render=False;m.show_render=True
    if apply:bpy.ops.object.modifier_apply(modifier=m.name)
    return m
for method in ('CATMULL_CLARK','SIMPLE'):
    for level in (1,2,3):
        for limit in (False,True):
            bpy.ops.mesh.primitive_cube_add();o=bpy.context.object;o.data.name='Subdivision cube'
            subdivide(o,method,level,limit)
        for boundary in ('ALL','PRESERVE_CORNERS'):
            bpy.ops.mesh.primitive_plane_add();o=bpy.context.object;o.data.name='Subdivision plane'
            subdivide(o,method,level,boundary=boundary)
vertices=[(x,y,.2*x*y) for y in range(3) for x in range(3)]
faces=[(y*3+x,y*3+x+1,(y+1)*3+x+1,(y+1)*3+x) for y in range(2) for x in range(2)]
for level in (1,2,3):
    for limit in (False,True):
        mesh=bpy.data.meshes.new('Subdivision patch');mesh.from_pydata(vertices,[],faces)
        o=bpy.data.objects.new('Patch',mesh);bpy.context.collection.objects.link(o)
        for i in range(2):
            mat=bpy.data.materials.new('Patch material');mat.diffuse_color=(.2+.3*i,.4,.6,1);mesh.materials.append(mat)
        for i,p in enumerate(mesh.polygons):p.material_index=i%2;p.use_smooth=bool(i%2)
        for name in ('UV','Detail'):
            uv=mesh.uv_layers.new(name=name);corner=0
            for face in faces:
                for index in face:
                    x,y,z=vertices[index];uv.data[corner].uv=(x/2+.1*y*y,y/2+.05*x*y);corner+=1
        subdivide(o,'CATMULL_CLARK',level,limit)
# Extraordinary topology: triangle fan from a filled disc.
bpy.ops.mesh.primitive_circle_add(vertices=5,fill_type='TRIFAN');o=bpy.context.object;o.data.name='Subdivision triangle'
subdivide(o,'CATMULL_CLARK',2)
# Descriptor persistence and separate viewport/render levels.
bpy.ops.mesh.primitive_cube_add();o=bpy.context.object;o.data.name='Subdivision cube';subdivide(o,'CATMULL_CLARK',1,apply=False)
bpy.ops.mesh.primitive_plane_add();o=bpy.context.object;o.data.name='Subdivision plane';m=subdivide(o,'CATMULL_CLARK',0,apply=False)
m.show_render=False
