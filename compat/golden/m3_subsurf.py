"""Bounded higher-level subdivision and crease attributes; Blender oracle first."""
HB_EQUIVALENT_MESH_PREFIXES=('Subdivision extended',)
import bpy
for case in ('edge','vertex','level4','simple','colors'):
    bpy.ops.mesh.primitive_cube_add()
    obj=bpy.context.object;obj.name='Subdivision extended';obj.data.name='Subdivision extended'
    if case in ('edge','vertex'):
        attr=obj.data.attributes.new(name='crease_edge' if case=='edge' else 'crease_vert',type='FLOAT',domain='EDGE' if case=='edge' else 'POINT')
        assert attr.data_type=='FLOAT'
        for value in attr.data:value.value=.35
        assert obj.data.attributes.get(attr.name).domain==attr.domain
    if case=='colors':
        color=obj.data.color_attributes.new(name='Color',type='FLOAT_COLOR',domain='CORNER')
        for i,color_value in enumerate(color.data):color_value.color=(i/24,.2,.4,1)
    modifier=obj.modifiers.new('Refine','SUBSURF')
    assert not modifier.use_custom_normals
    modifier.levels=4 if case=='level4' else 2
    if case=='simple':modifier.subdivision_type='SIMPLE'
    bpy.ops.object.modifier_apply(modifier=modifier.name)
