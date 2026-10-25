import bpy,json,itertools
from pathlib import Path
out={}
def state():
 bpy.context.view_layer.update()
 return dict(objects={o.name:dict(data=o.data.name if o.data else None,parent=o.parent.name if o.parent else None,location=list(o.location),rotation_euler=list(o.rotation_euler),scale=list(o.scale),world=[list(r) for r in o.matrix_world],parent_inverse=[list(r) for r in o.matrix_parent_inverse]) for o in bpy.data.objects},meshes={m.name:dict(vertices=[list(v.co) for v in m.vertices],faces=[list(f.vertices) for f in m.polygons],users=m.users) for m in bpy.data.meshes})
for index,(kind,negative) in enumerate(itertools.product(('plain','parent_active','parent_source','child_active','child_source','source_parent_active','active_parent_source','shared_active','shared_source','shared_selected'),('none','active','source','both'))):
 for o in list(bpy.data.objects):bpy.data.objects.remove(o,do_unlink=True)
 for m in list(bpy.data.meshes):bpy.data.meshes.remove(m)
 bpy.ops.mesh.primitive_cube_add(calc_uvs=False);a=bpy.context.object;a.name='Active';a.location=(1,2,3);a.rotation_euler=(.3,-.4,.7);a.scale=(-.5 if negative in ('active','both') else .5,1.2,2)
 bpy.ops.mesh.primitive_cube_add(calc_uvs=False);b=bpy.context.object;b.name='Source';b.location=(-2,1,-1);b.rotation_euler=(-.2,.5,-.3);b.scale=(-.8 if negative in ('source','both') else .8,.7,1.4)
 if kind.startswith('parent_'):
  p=bpy.data.objects.new('Parent',None);bpy.context.collection.objects.link(p);p.location=(2,-3,1);p.rotation_euler=(-.2,.3,.5);p.scale=(1.2,.8,2)
  (a if kind=='parent_active' else b).parent=p
 if kind.startswith('child_'):
  c=bpy.data.objects.new('Child',None);bpy.context.collection.objects.link(c);c.location=(2,-1,3);c.rotation_euler=(-.3,.4,-.1);c.parent=a if kind=='child_active' else b
 if kind=='source_parent_active':a.parent=b
 if kind=='active_parent_source':b.parent=a
 if kind.startswith('shared_'):
  c=bpy.data.objects.new('Shared',a.data if kind=='shared_active' else b.data);bpy.context.collection.objects.link(c);c.location=(-3,2,1)
  if kind=='shared_selected':c.select_set(True)
 a.select_set(True);b.select_set(True);bpy.context.view_layer.objects.active=a
 before=state()
 try:result=sorted(bpy.ops.object.join());error=None
 except Exception as e:result=None;error=str(e)
 out[str(index)]=dict(kind=kind,negative=negative,before=before,result=result,error=error,after=state())
Path('/results/join-reference.json').write_text(json.dumps(out,indent=2)+'\n')
