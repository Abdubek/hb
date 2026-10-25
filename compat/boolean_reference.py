import bpy,json
from pathlib import Path
out={}
for solver in ('EXACT','FAST','MANIFOLD'):
 for operation in ('DIFFERENCE','UNION','INTERSECT'):
  for reflected in (False,True):
   for obj in list(bpy.data.objects):bpy.data.objects.remove(obj,do_unlink=True)
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
   out[f'{solver}_{operation}_{reflected}']=dict(vertices=[list(v.co) for v in mesh.vertices],faces=[list(p.vertices) for p in mesh.polygons],uv=[list(d.uv) for d in mesh.uv_layers[0].data])
Path('/results/reference.json').write_text(json.dumps(out,indent=2)+'\n')
