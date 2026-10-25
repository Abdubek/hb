import bpy,json
from pathlib import Path
out={}
for direction in ('NORMAL','X','Y','Z'):
 for group in ('','Mask','Missing'):
  for invert in (False,True):
   for custom in (False,True):
    for obj in list(bpy.data.objects):bpy.data.objects.remove(obj,do_unlink=True)
    bpy.ops.mesh.primitive_cube_add();obj=bpy.context.object;mesh=obj.data
    weights=obj.vertex_groups.new(name='Mask')
    for i in range(7):weights.add([i],(i%4)/3,'REPLACE')
    if custom:mesh.normals_split_custom_set([(.2,.3,1)]*24)
    source=dict(vertices=[list(v.co) for v in mesh.vertices],faces=[list(p.vertices) for p in mesh.polygons],normals=[list(n.vector) for n in mesh.corner_normals] if mesh.has_custom_normals else [])
    mod=obj.modifiers.new('Displace','DISPLACE');mod.direction=direction;mod.strength=.4;mod.mid_level=.2;mod.vertex_group=group;mod.invert_vertex_group=invert
    bpy.ops.object.modifier_apply(modifier=mod.name)
    out[f'{direction}_{group}_{invert}_{custom}']=dict(vertices=[list(v.co) for v in mesh.vertices],faces=[list(p.vertices) for p in mesh.polygons],normals=[list(n.vector) for n in mesh.corner_normals] if mesh.has_custom_normals else [],source=source)
Path('/results/reference.json').write_text(json.dumps(out,separators=(',',':'))+'\n')
