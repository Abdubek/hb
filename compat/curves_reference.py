import bpy,json,sys,itertools
from pathlib import Path
cases=[]
paths=[[(0,0,0),(0,0,2)],[(0,0,0),(2,0,0)],[(0,0,0),(0,2,0)],[(0,0,0),(1,2,3)],[(0,0,0),(1,0,0),(1,2,0)],[(0,0,0),(1,0,0),(1,1,0),(0,1,0)],[(0,0,0),(1,2,3),(2,1,4)]]
for pi,points in enumerate(paths):
 for res,cyclic,caps,depth in itertools.product((0,1,3),(False,True),(False,True),(0,.2)):
  if len(points)==2 and cyclic:continue
  c=bpy.data.curves.new('C','CURVE');c.dimensions='3D';c.bevel_depth=depth;c.bevel_resolution=res;c.use_fill_caps=caps
  sp=c.splines.new('POLY');sp.points.add(len(points)-1)
  for p,co in zip(sp.points,points):p.co=(*co,1)
  sp.use_cyclic_u=cyclic
  o=bpy.data.objects.new('C',c);bpy.context.collection.objects.link(o);bpy.context.view_layer.update()
  m=o.evaluated_get(bpy.context.evaluated_depsgraph_get()).to_mesh()
  cases.append(dict(path=pi,points=points,res=res,cyclic=cyclic,caps=caps,depth=depth,vertices=[list(v.co) for v in m.vertices],faces=[list(f.vertices) for f in m.polygons],edges=[list(e.vertices) for e in m.edges],smooth=[p.use_smooth for p in m.polygons],uv=[list(x.uv) for x in m.uv_layers.active.data] if m.uv_layers else [],defaults=dict(fill_mode=c.fill_mode,twist_mode=c.twist_mode,resolution_u=c.resolution_u,point_radius=sp.points[0].radius,tilt=sp.points[0].tilt,use_smooth=sp.use_smooth)))
  o.to_mesh_clear();bpy.data.objects.remove(o,do_unlink=True);bpy.data.curves.remove(c)
Path(sys.argv[-1]).write_text(json.dumps(cases))
