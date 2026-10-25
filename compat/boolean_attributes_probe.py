import bpy,json

out={}
for kind in ('object','collection','empty_collection'):
 for solver in ('EXACT','FAST','MANIFOLD'):
  for operation in ('DIFFERENCE','UNION','INTERSECT'):
   if kind!='object' and solver=='FAST' and operation=='INTERSECT':continue
   bpy.ops.mesh.primitive_cube_add();owner=bpy.context.object
   owner.data.normals_split_custom_set([(0,.2,1)]*24)
   layer=owner.data.color_attributes.new(name='Color',type='FLOAT_COLOR',domain='CORNER')
   for i,d in enumerate(layer.data):d.color=(i/24,.2,.4,1)
   coll=bpy.data.collections.new('Cutters');bpy.context.scene.collection.children.link(coll)
   for x in (-.6,.6):
    bpy.ops.mesh.primitive_cube_add(size=.6,location=(x,0,0));other=bpy.context.object
    if kind!='empty_collection':coll.objects.link(other)
   bpy.context.view_layer.objects.active=owner
   mod=owner.modifiers.new('Boolean','BOOLEAN');mod.solver=solver;mod.operation=operation
   if kind=='object':mod.object=other
   else:mod.operand_type='COLLECTION';mod.collection=coll
   bpy.ops.object.modifier_apply(modifier=mod.name)
   mesh=owner.data
   owner.name=f'{kind}_{solver}_{operation}'
