import bpy

curve=bpy.data.curves.new('Cable','CURVE')
curve.dimensions='3D';curve.bevel_depth=.06;curve.bevel_resolution=4
curve.resolution_u=16;curve.use_fill_caps=True
spline=curve.splines.new('BEZIER');spline.bezier_points.add(2)
for point,co in zip(spline.bezier_points,[(0,0,0),(1,.5,1),(2,0,.3)]):
    point.co=co;point.handle_left_type='AUTO';point.handle_right_type='AUTO'
    point.radius=1.;point.tilt=0.
obj=bpy.data.objects.new('Cable',curve);bpy.context.collection.objects.link(obj)
assert spline.type=='BEZIER' and len(spline.bezier_points)==3
bpy.context.view_layer.update()
assert obj.dimensions.x>1.9 and obj.dimensions.z>.7

manual=bpy.data.curves.new('Manual','CURVE');manual.dimensions='3D';manual.bevel_depth=.03;manual.use_fill_caps=True
s=manual.splines.new('BEZIER');s.bezier_points.add(1)
a=s.bezier_points[0];b=s.bezier_points[1]
a.co=(0,2,0);b.co=(2,2,0)
a.handle_right=(0,2,1);b.handle_left=(2,2,1)
o=bpy.data.objects.new('Manual',manual);bpy.context.collection.objects.link(o)
assert tuple(a.handle_right)==(0.,2.,1.)
bpy.context.view_layer.update()
