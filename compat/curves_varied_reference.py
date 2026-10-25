import bpy,json,sys,random,math
from pathlib import Path
random.seed(384)
cases=[]
for i in range(80):
 points=[(0.,0.,0.)]
 for j in range(1,2+i%5):points.append(tuple(points[-1][k]+random.uniform(-1,2) for k in range(3)))
 c=bpy.data.curves.new('C','CURVE');c.dimensions='3D';c.bevel_depth=(.03,.1,.4)[i%3];c.bevel_resolution=(0,1,3,8)[i%4]
 sp=c.splines.new('POLY');sp.points.add(len(points)-1)
 radius=[];tilt=[]
 for j,(p,co) in enumerate(zip(sp.points,points)):
  p.co=(*co,1);p.radius=random.uniform(.2,2);p.tilt=random.uniform(-2,2);radius.append(p.radius);tilt.append(p.tilt)
 sp.use_smooth=i%2==0
 o=bpy.data.objects.new('C',c);bpy.context.collection.objects.link(o);bpy.context.view_layer.update()
 m=o.evaluated_get(bpy.context.evaluated_depsgraph_get()).to_mesh()
 cases.append(dict(points=points,res=c.bevel_resolution,depth=c.bevel_depth,radius=radius,tilt=tilt,cyclic=False,use_smooth=sp.use_smooth,vertices=[list(v.co) for v in m.vertices],faces=[list(f.vertices) for f in m.polygons],edges=[list(e.vertices) for e in m.edges],smooth=[f.use_smooth for f in m.polygons],uv=[list(u.uv) for u in m.uv_layers.active.data]))
 bpy.data.objects.remove(o,do_unlink=True);bpy.data.curves.remove(c)
Path(sys.argv[-1]).write_text(json.dumps(cases))
