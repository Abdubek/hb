import bpy,json,random
from pathlib import Path
out={};random.seed(19)
for case in range(40):
 vertices=[(random.randrange(10)*.04,random.randrange(5)*.04,0) for i in range(20)]
 edges=[(i,i+1) for i in range(19)]
 for mode in ('ALL','CONNECTED'):
  for invert in (False,True):
   for obj in list(bpy.data.objects):bpy.data.objects.remove(obj,do_unlink=True)
   name=f'random_{case}_{mode}_{invert}'
   mesh=bpy.data.meshes.new(name);mesh.from_pydata(vertices,edges,[])
   obj=bpy.data.objects.new(name,mesh);bpy.context.collection.objects.link(obj);bpy.context.view_layer.objects.active=obj
   group=obj.vertex_groups.new(name='Mask')
   for i in range(len(vertices)):group.add([i],[0,.2,1][i%3],'REPLACE')
   mod=obj.modifiers.new('Weld','WELD');mod.mode=mode;mod.merge_threshold=.105;mod.vertex_group='Mask';mod.invert_vertex_group=invert
   bpy.ops.object.modifier_apply(modifier=mod.name)
   mesh=obj.data
   out[name]=dict(input=vertices,vertices=[list(v.co) for v in mesh.vertices],edges=[list(e.vertices) for e in mesh.edges],weights=[[(g.group,g.weight) for g in v.groups] for v in mesh.vertices])
Path('/results/extra-reference.json').write_text(json.dumps(out,indent=2)+'\n')
