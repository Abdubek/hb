import bpy,json

out={}
for solver in ('EXACT','FAST','MANIFOLD'):
 for operation in ('DIFFERENCE','UNION','INTERSECT'):
  for reflected in (False,True):
   if solver=='MANIFOLD' and reflected:continue
   bpy.ops.mesh.primitive_cube_add();owner=bpy.context.object
   bpy.ops.mesh.primitive_cube_add(size=1.3,location=(.6,.1,.2));other=bpy.context.object
   if reflected:other.scale.x=-1
   bpy.context.view_layer.objects.active=owner
   mod=owner.modifiers.new('Boolean','BOOLEAN')
   try:mod.solver=solver
   except Exception as error:out[solver]=str(error);continue
   mod.operation=operation;mod.object=other
   bpy.ops.object.modifier_apply(modifier=mod.name)
   mesh=owner.data
   owner.name=f'{solver}_{operation}_{reflected}'
