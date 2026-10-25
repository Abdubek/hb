import bpy,json
from pathlib import Path
out={}
for affect in ('EDGES','VERTICES'):
 for segments in (1,2,3,4,8):
  for width in (.1,1.,3.):
   for clamp in (True,False):
    for obj in list(bpy.data.objects):bpy.data.objects.remove(obj,do_unlink=True)
    bpy.ops.mesh.primitive_cube_add();obj=bpy.context.object
    for v in obj.data.vertices:v.co.y*=2;v.co.z*=3
    mod=obj.modifiers.new('Bevel','BEVEL');mod.affect=affect;mod.width=width;mod.segments=segments;mod.use_clamp_overlap=clamp
    bpy.ops.object.modifier_apply(modifier=mod.name);mesh=obj.data
    out[f'{affect}_{segments}_{width}_{clamp}']=dict(vertices=[list(v.co) for v in mesh.vertices],edges=[list(e.vertices) for e in mesh.edges],faces=[list(f.vertices) for f in mesh.polygons],uv=[list(v.uv) for v in mesh.uv_layers[0].data])
Path('/results/reference.json').write_text(json.dumps(out,separators=(',',':'))+'\n')
