"""Manifold object booleans: reference contract authored before bpy exposure."""
HB_EQUIVALENT_MESH_PREFIXES=('Boolean DIFFERENCE','Boolean UNION','Boolean INTERSECT','Boolean transformed')
HB_SYMBOLS={
'bpy.types.BooleanModifier.name':'Modifier name', 'bpy.types.BooleanModifier.type':'BOOLEAN',
'bpy.types.BooleanModifier.operation':'DIFFERENCE, UNION or INTERSECT of closed manifold meshes',
'bpy.types.BooleanModifier.object':'Mesh object operand or None; evaluated in owner local coordinates',
'bpy.types.BooleanModifier.material_mode':'INDEX only',
'bpy.types.BooleanModifier.use_self':'False only',
'bpy.types.BooleanModifier.use_hole_tolerant':'False only',
'bpy.types.BooleanModifier.double_threshold':'Default 1e-6 only; unused by MANIFOLD',
'bpy.types.BooleanModifier.show_viewport':'Viewport and glTF evaluation flag',
'bpy.types.BooleanModifier.show_render':'Preview evaluation flag',
}
import bpy

def box(name,location):
    bpy.ops.mesh.primitive_cube_add(size=2,location=location)
    o=bpy.context.object;o.name=name;o.data.name=name
    for i in range(2):
        mat=bpy.data.materials.new(name+str(i));mat.diffuse_color=(.2+.4*i,.3,.5,1);o.data.materials.append(mat)
    for i,p in enumerate(o.data.polygons):p.material_index=i%2;p.use_smooth=bool(i%2)
    layer=o.data.uv_layers.new(name='Detail')
    for i,loop in enumerate(layer.data):loop.uv=(i*.125,(i%3)*.25)
    return o

for operation in ('DIFFERENCE','UNION','INTERSECT'):
    for location in ((1,0,0),(.7,.4,.3),(4,0,0),(0,0,0)):
        a=box('Boolean '+operation,(0,0,0));b=box('Operand',location)
        bpy.context.view_layer.objects.active=a
        mod=a.modifiers.new('Boolean','BOOLEAN')
        assert mod.solver=='EXACT' and mod.operation=='DIFFERENCE' and mod.operand_type=='OBJECT'
        assert mod.object is None and mod.material_mode=='INDEX'
        assert not mod.use_self and not mod.use_hole_tolerant and abs(mod.double_threshold-1e-6)<1e-12
        mod.solver='MANIFOLD';mod.operation=operation;mod.object=b
        assert mod.object==b
        mod.operand_type='OBJECT';mod.material_mode='INDEX';mod.use_self=False;mod.use_hole_tolerant=False;mod.double_threshold=1e-6
        mod.name='Cut';mod.show_render=False;mod.show_render=True;mod.show_viewport=False;mod.show_viewport=True
        bpy.ops.object.modifier_apply(modifier=mod.name)

# Dependency graph, object transforms and retained descriptors.
a=box('Boolean transformed',(10,2,0));a.scale=(2,1,1)
b=box('Operand transformed',(11,2,0));b.scale=(2,1,1)
mod=a.modifiers.new('Cut','BOOLEAN');mod.solver='MANIFOLD';mod.object=b
bpy.context.view_layer.objects.active=a;bpy.ops.object.modifier_apply(modifier=mod.name)
a=box('Boolean stack',(0,0,0));b=box('Operand stack',(1,0,0))
array=b.modifiers.new('Repeat','ARRAY');array.count=2;array.relative_offset_displace=(0,2,0)
mod=a.modifiers.new('Cut','BOOLEAN');mod.solver='MANIFOLD';mod.object=b
# No operand preserves the input, also with the default solver.
a=box('Boolean no operand',(0,0,0));mod=a.modifiers.new('Disabled','BOOLEAN')
a=box('Boolean hidden viewport',(0,0,0));mod=a.modifiers.new('Cut','BOOLEAN');mod.solver='MANIFOLD';mod.object=b;mod.show_viewport=False
a=box('Boolean hidden render',(0,0,0));mod=a.modifiers.new('Cut','BOOLEAN');mod.solver='MANIFOLD';mod.object=b;mod.show_render=False
