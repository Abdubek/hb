import bpy
for i,(points,cyclic) in enumerate((([(0,0,0),(1,2,3),(2,1,4)],False),([(0,0,0),(1,0,0),(1,1,0),(0,1,0)],True))):
 curve=bpy.data.curves.new('Curve_%d'%i,'CURVE');curve.dimensions='3D';curve.bevel_depth=.1;curve.bevel_resolution=3
 spline=curve.splines.new('POLY');spline.points.add(len(points)-1)
 for point,co in zip(spline.points,points):point.co=(*co,1)
 spline.use_cyclic_u=cyclic
 obj=bpy.data.objects.new('Pipe_%d'%i,curve);bpy.context.collection.objects.link(obj);obj.location=(i*4,0,0)
 material=bpy.data.materials.new('Pipe material %d'%i);material.diffuse_color=(.2,.4,.8,1);curve.materials.append(material)
 assert obj.type=='CURVE' and len(curve.splines)==1 and curve.users==1
bpy.context.view_layer.update()
assert len(bpy.data.curves)==2 and len(bpy.data.meshes)==0
