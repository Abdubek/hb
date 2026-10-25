import bpy,json,itertools
from pathlib import Path
out={}
def state():
 bpy.context.view_layer.update()
 return dict(objects={o.name:dict(data=o.data.name if o.data else None,parent=o.parent.name if o.parent else None,location=list(o.location),rotation_euler=list(o.rotation_euler),scale=list(o.scale),world=[list(r) for r in o.matrix_world],parent_inverse=[list(r) for r in o.matrix_parent_inverse]) for o in bpy.data.objects},meshes={m.name:dict(vertices=[list(v.co) for v in m.vertices],faces=[list(f.vertices) for f in m.polygons],users=m.users) for m in bpy.data.meshes})
for index,(kind,negative,flags,isolate) in enumerate(itertools.product(('shared','shared_selected'),(False,True),tuple(itertools.product((False,True),repeat=3)),(False,True))):
 for o in list(bpy.data.objects):bpy.data.objects.remove(o,do_unlink=True)
 for m in list(bpy.data.meshes):bpy.data.meshes.remove(m)
 bpy.ops.mesh.primitive_cube_add(calc_uvs=False);o=bpy.context.object;o.name='Target';o.location=(1,2,3);o.rotation_euler=(.3,-.4,.7);o.scale=(-.5 if negative else .5,1.2,2)
 if kind in ('parent','both'):
  p=bpy.data.objects.new('Parent',None);bpy.context.collection.objects.link(p);p.location=(2,-3,1);p.rotation_euler=(-.2,.3,.5);p.scale=(1.2,.8,2);o.parent=p
 if kind in ('child','both'):
  c=bpy.data.objects.new('Child',None);bpy.context.collection.objects.link(c);c.location=(2,-1,3);c.rotation_euler=(-.3,.4,-.1);c.parent=o
 if kind.startswith('shared'):
  c=bpy.data.objects.new('Shared',o.data);bpy.context.collection.objects.link(c);c.location=(-3,2,1);c.rotation_euler=(.2,.4,-.7);c.scale=(.8,1.3,1.7)
  if kind=='shared_selected':c.select_set(True)
 before=state()
 try:result=sorted(bpy.ops.object.transform_apply(location=flags[0],rotation=flags[1],scale=flags[2],isolate_users=isolate));error=None
 except Exception as e:result=None;error=str(e)
 out[str(index)]=dict(kind=kind,negative=negative,flags=flags,isolate=isolate,before=before,result=result,error=error,after=state())
Path('/results/apply-transformed-shared-reference.json').write_text(json.dumps(out,indent=2)+'\n')
