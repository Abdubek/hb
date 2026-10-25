import bpy,json,itertools
from pathlib import Path
specs={
 'cube':dict(size=1), 'plane':dict(size=1),
 'circle':dict(vertices=8,radius=.7,fill_type='NGON'),
 'cylinder':dict(vertices=8,radius=.7,depth=1.2),
 'cone':dict(vertices=8,radius1=.7,radius2=.2,depth=1.2),
 'uv_sphere':dict(segments=8,ring_count=4,radius=.7),
 'ico_sphere':dict(subdivisions=1,radius=.7),
 'torus':dict(major_segments=8,minor_segments=4,major_radius=1,minor_radius=.3)}
out={}
for index,(kind,scale,edit,zero) in enumerate(itertools.product(('cylinder','cone'),((-.5,1.3,2),),(False,True),(False,True))):
 if kind=='torus' and scale!=(0,0,0):continue
 if bpy.context.object and bpy.context.object.mode!='OBJECT':bpy.ops.object.mode_set(mode='OBJECT')
 for o in list(bpy.data.objects):bpy.data.objects.remove(o,do_unlink=True)
 for m in list(bpy.data.meshes):bpy.data.meshes.remove(m)
 kwargs=specs[kind].copy();kwargs['calc_uvs']=False
 if kind!='torus':kwargs['scale']=scale
 if zero:
  for k in ('size','radius','radius1','radius2','depth','minor_radius'):
   if k in kwargs:kwargs[k]=0
 if edit:
  bpy.ops.mesh.primitive_cube_add(size=.4,location=(1,2,3),rotation=(.2,.3,-.4));bpy.context.object.scale=(.7,1.2,1.5);bpy.ops.object.mode_set(mode='EDIT')
 kwargs.update(location=(2,-1,3),rotation=(.3,-.2,.4))
 try:result=sorted(getattr(bpy.ops.mesh,'primitive_'+kind+'_add')(**kwargs));error=None
 except Exception as e:result=None;error=str(e)
 mode=bpy.context.object.mode if bpy.context.object else None
 if mode=='EDIT':bpy.ops.object.mode_set(mode='OBJECT')
 o=bpy.context.object;m=o.data if o else None
 out[str(index)]=dict(kind=kind,kwargs=kwargs,edit=edit,zero=zero,result=result,error=error,mode=mode,location=list(o.location) if o else None,rotation=list(o.rotation_euler) if o else None,scale=list(o.scale) if o else None,mesh=dict(vertices=[list(v.co) for v in m.vertices],edges=[list(e.vertices) for e in m.edges],faces=[list(p.vertices) for p in m.polygons],uv=[list(v.uv) for v in m.uv_layers.active.data] if m.uv_layers else []) if m else None)
Path('/results/untextured-reference.json').write_text(json.dumps(out,indent=2)+'\n')
