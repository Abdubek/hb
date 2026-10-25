import bpy,json,itertools
from pathlib import Path
out={}
for index,(align,explicit,edit) in enumerate(itertools.product(('WORLD','CURSOR','VIEW'),('none','location','rotation','both'),(False,True))):
 if bpy.context.object and bpy.context.object.mode!='OBJECT':bpy.ops.object.mode_set(mode='OBJECT')
 for o in list(bpy.data.objects):bpy.data.objects.remove(o,do_unlink=True)
 for m in list(bpy.data.meshes):bpy.data.meshes.remove(m)
 bpy.context.scene.cursor.location=(2,-3,1);bpy.context.scene.cursor.rotation_euler=(.2,.3,.4)
 kwargs=dict(size=.7,align=align)
 if explicit in ('location','both'):kwargs['location']=(-1,3,2)
 if explicit in ('rotation','both'):kwargs['rotation']=(-.3,.5,.7)
 if edit:
  bpy.ops.mesh.primitive_cube_add(size=.4,location=(1,2,3),rotation=(.2,.3,-.4));bpy.context.object.scale=(.7,1.2,1.5);bpy.ops.object.mode_set(mode='EDIT')
 try:result=sorted(bpy.ops.mesh.primitive_cube_add(**kwargs));error=None
 except Exception as e:result=None;error=str(e)
 if bpy.context.object and bpy.context.object.mode=='EDIT':bpy.ops.object.mode_set(mode='OBJECT')
 o=bpy.context.object
 out[str(index)]=dict(align=align,explicit=explicit,edit=edit,kwargs=kwargs,result=result,error=error,location=list(o.location) if o else None,rotation=list(o.rotation_euler) if o else None,vertices=[list(v.co) for v in o.data.vertices] if o else None)
Path('/results/alignment-reference.json').write_text(json.dumps(out,indent=2)+'\n')
