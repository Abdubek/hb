import bpy,json,itertools
from pathlib import Path
out={}
for index,(kind,fill,zero_depth,uv) in enumerate(itertools.product(('cylinder','cone'),('NOTHING','NGON','TRIFAN'),(False,True),(False,True))):
 for o in list(bpy.data.objects):bpy.data.objects.remove(o,do_unlink=True)
 for m in list(bpy.data.meshes):bpy.data.meshes.remove(m)
 kwargs=dict(vertices=8,depth=0 if zero_depth else 1.2,end_fill_type=fill,calc_uvs=uv)
 kwargs.update(dict(radius=.7 if zero_depth else 0) if kind=='cylinder' else dict(radius1=.7 if zero_depth else 0,radius2=.2 if zero_depth else 0))
 getattr(bpy.ops.mesh,'primitive_'+kind+'_add')(**kwargs);m=bpy.context.object.data
 out[str(index)]=dict(kind=kind,kwargs=kwargs,vertices=[list(v.co) for v in m.vertices],edges=[list(e.vertices) for e in m.edges],faces=[list(f.vertices) for f in m.polygons],uv=[list(v.uv) for v in m.uv_layers.active.data] if m.uv_layers else [])
for fill in ('NOTHING','NGON','TRIFAN'):
 for o in list(bpy.data.objects):bpy.data.objects.remove(o,do_unlink=True)
 for m in list(bpy.data.meshes):bpy.data.meshes.remove(m)
 kwargs=dict(vertices=8,radius=0,fill_type=fill,calc_uvs=False)
 bpy.ops.mesh.primitive_circle_add(**kwargs);m=bpy.context.object.data
 out['circle_'+fill]=dict(kind='circle',kwargs=kwargs,vertices=[list(v.co) for v in m.vertices],edges=[list(e.vertices) for e in m.edges],faces=[list(f.vertices) for f in m.polygons],uv=[])
Path('/results/degenerate-reference.json').write_text(json.dumps(out,indent=2)+'\n')
