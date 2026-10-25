import bpy,json
from pathlib import Path
out={}
for name,points,faces in [
 ('closing',[(0,0,0),(.09,0,0),(1,1,0),(0,.09,0)],[(0,1,2,3)]),
 ('pinched',[(0,0,0),(1,0,0),(1,1,0),(.01,.01,0),(-1,0,0),(-1,-1,0)],[(0,1,2,3,4,5)]),
 ('triple',[(0,0,0),(.01,0,0),(.02,0,0),(1,1,0),(0,1,0)],[(0,1,2,3,4)])]:
 for mode in ('ALL','CONNECTED'):
  for obj in list(bpy.data.objects):bpy.data.objects.remove(obj,do_unlink=True)
  key=name+'_'+mode;m=bpy.data.meshes.new(key);m.from_pydata(points,[],faces)
  u=m.uv_layers.new(name='UVMap')
  for i,d in enumerate(u.data):d.uv=(i*.13,i*.07)
  o=bpy.data.objects.new(key,m);bpy.context.collection.objects.link(o);bpy.context.view_layer.objects.active=o
  w=o.modifiers.new('Weld','WELD');w.mode=mode;w.merge_threshold=.1;bpy.ops.object.modifier_apply(modifier=w.name)
  m=o.data;out[key]=dict(input=points,input_faces=faces,vertices=[list(v.co) for v in m.vertices],faces=[list(p.vertices) for p in m.polygons],edges=[list(e.vertices) for e in m.edges],uv=[list(d.uv) for d in m.uv_layers[0].data])
Path('/results/face-reference.json').write_text(json.dumps(out,indent=2)+'\n')
