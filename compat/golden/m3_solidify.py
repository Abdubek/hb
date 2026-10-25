import bpy
HB_EQUIVALENT_MESH_PREFIXES=('Radial','RadialGroups','Junction','RadialZero')

def make(name,vertices,faces,**settings):
    data=bpy.data.meshes.new(name);data.from_pydata(vertices,[],faces)
    obj=bpy.data.objects.new(name,data);bpy.context.collection.objects.link(obj)
    if settings.pop('groups',False):
        group=obj.vertex_groups.new(name='Thickness');group.add([0],.25,'REPLACE');group.add([1],.75,'REPLACE')
        obj.vertex_groups.new(name='Shell');obj.vertex_groups.new(name='Rim')
    if settings.pop('uv',False):
        layer=data.uv_layers.new(name='UVMap')
        for corner in range(len(layer.data)):layer.data[corner].uv=(corner*.13,corner*.07)
    mod=obj.modifiers.new('Solidify','SOLIDIFY');mod.thickness=.2;mod.offset=0
    mod.solidify_mode=settings.get('solidify_mode','EXTRUDE')
    mod.thickness=settings.get('thickness',.2);mod.offset=settings.get('offset',0.)
    mod.use_even_offset=settings.get('use_even_offset',False);mod.use_quality_normals=settings.get('use_quality_normals',False)
    mod.thickness_clamp=settings.get('thickness_clamp',0.)
    mod.vertex_group=settings.get('vertex_group','');mod.thickness_vertex_group=settings.get('thickness_vertex_group',0.)
    mod.invert_vertex_group=settings.get('invert_vertex_group',False)
    mod.shell_vertex_group=settings.get('shell_vertex_group','');mod.rim_vertex_group=settings.get('rim_vertex_group','')
    bpy.context.view_layer.objects.active=obj;obj.select_set(True);bpy.ops.object.modifier_apply(modifier=mod.name)
    return obj
flat=[(0,0,0),(1,0,0),(1,1,0),(0,1,0)];ff=[(0,1,2,3)]
fold=flat+[(1,0,1),(1,1,1)];faces=ff+[(2,1,4,5)]
make('Even',fold,faces,use_even_offset=True,uv=True)
make('Quality',[(0,0,0),(3,0,0),(2,1,0),(0,1,0),(3,0,2),(2,1,2)],faces,use_quality_normals=True)
make('Clamped',fold,faces,thickness=4,thickness_clamp=1,use_even_offset=True)
make('Groups',flat,ff,groups=True,vertex_group='Thickness',thickness_vertex_group=.1,shell_vertex_group='Shell',rim_vertex_group='Rim')
make('InverseGroups',flat,ff,groups=True,vertex_group='Thickness',thickness_vertex_group=.1,invert_vertex_group=True)
make('Radial',fold,faces,solidify_mode='NON_MANIFOLD',uv=True)
make('RadialGroups',flat,ff,solidify_mode='NON_MANIFOLD',groups=True,vertex_group='Thickness',thickness_vertex_group=.1,shell_vertex_group='Shell',rim_vertex_group='Rim')
make('Junction',[(0,0,0),(1,0,0),(0,1,0),(0,-1,0),(0,0,1)],[(0,1,2),(1,0,3),(0,1,4)],solidify_mode='NON_MANIFOLD')
make('RadialZero',flat,ff,solidify_mode='NON_MANIFOLD',thickness=0)
