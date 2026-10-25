"""Non-destructive ARRAY contract, authored before implementation."""
HB_SYMBOLS = {
'bpy.types.Object.modifiers':'Ordered non-destructive stack; ARRAY/MIRROR/SOLIDIFY/TRIANGULATE and UV-free cuboid BEVEL subsets',
'bpy.types.Object.modifiers.new':'new(name, type): ARRAY, MIRROR, SOLIDIFY, TRIANGULATE, restricted WELD or restricted BEVEL',
'bpy.types.Object.modifiers.remove':'Remove a modifier from this object',
'bpy.types.Object.modifiers.clear':'Remove all modifiers',
'bpy.types.ArrayModifier.name':'Unique modifier name',
'bpy.types.ArrayModifier.type':'ARRAY',
'bpy.types.ArrayModifier.count':'Fixed count, clamped to 1..10000',
'bpy.types.ArrayModifier.fit_type':'FIXED_COUNT only',
'bpy.types.ArrayModifier.use_relative_offset':'Enable offset relative to evaluated mesh bounding box',
'bpy.types.ArrayModifier.relative_offset_displace':'XYZ relative displacement',
'bpy.types.ArrayModifier.use_constant_offset':'Enable fixed local displacement',
'bpy.types.ArrayModifier.constant_offset_displace':'XYZ constant displacement in meters',
'bpy.types.ArrayModifier.use_merge_vertices':'False only in the initial ARRAY subset',
'bpy.types.ArrayModifier.use_object_offset':'False only in the initial ARRAY subset',
'bpy.types.ArrayModifier.show_viewport':'Enable modifier for viewport queries',
'bpy.types.ArrayModifier.show_render':'Enable modifier for CPU preview',
'bpy.ops.object.modifier_apply':'Apply the first supported modifier to an active single-user mesh',
}
import bpy
bpy.ops.mesh.primitive_cube_add(size=1)
o=bpy.context.object;o.name='Grid'
a=o.modifiers.new('Columns','ARRAY');assert a.type=='ARRAY' and a.count==2
assert a.fit_type=='FIXED_COUNT' and a.use_relative_offset and not a.use_constant_offset
assert not a.use_merge_vertices and not a.use_object_offset
assert tuple(a.relative_offset_displace)==(1,0,0)
assert tuple(a.constant_offset_displace)==(1,0,0)
a.count=3;a.relative_offset_displace=(1.5,0,0)
b=o.modifiers.new('Rows','ARRAY');b.count=2;b.use_relative_offset=False;b.use_constant_offset=True;b.constant_offset_displace=(0,2,0)
assert len(o.data.vertices)==8
assert tuple(m.name for m in o.modifiers)==('Columns','Rows')
assert o.modifiers['Columns'].count==3
a.show_viewport=False;assert not a.show_viewport;a.show_viewport=True
a.show_render=False;assert not a.show_render;a.show_render=True
# Keep a non-destructive object to compare evaluated GLB output.
p=o.copy();p.data=o.data.copy();p.name='Applied';p.location=(0,0,2)
bpy.context.collection.objects.link(p);bpy.context.view_layer.objects.active=p
assert p.modifiers[0].name=='Columns'
bpy.ops.object.modifier_apply(modifier='Columns')
assert len(p.data.vertices)==24 and len(p.modifiers)==1
bpy.ops.object.modifier_apply(modifier='Rows')
assert len(p.data.vertices)==48 and len(p.modifiers)==0
unused=p.modifiers.new('Unused','ARRAY');unused.name='Temporary'
p.modifiers.remove(unused)
p.modifiers.new('Clear','ARRAY');p.modifiers.clear();assert len(p.modifiers)==0
