import bpy
for index,case in enumerate(cases):
 c=bpy.data.curves.new('Curve_%03d'%index,'CURVE');c.dimensions='3D';c.bevel_depth=case['depth'];c.bevel_resolution=case['res']
 s=c.splines.new('POLY');s.points.add(len(case['points'])-1)
 for p,co in zip(s.points,case['points']):p.co=(*co,1)
 s.use_cyclic_u=case['cyclic']
 s.use_smooth=case.get('use_smooth',True)
 if 'radius' in case:
  for p,r,t in zip(s.points,case['radius'],case['tilt']):p.radius=r;p.tilt=t
 o=bpy.data.objects.new(c.name,c);bpy.context.collection.objects.link(o)
 assert o.type=='CURVE' and o.data==c and c.users==1
assert len(bpy.data.meshes)==0
bpy.context.view_layer.update()
