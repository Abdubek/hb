import bpy

def curve(name,coords):
    c=bpy.data.curves.new(name,'CURVE');c.dimensions='3D'
    s=c.splines.new('BEZIER');s.bezier_points.add(len(coords)-1)
    for p,co in zip(s.bezier_points,coords):p.co=co
    o=bpy.data.objects.new(name,c);bpy.context.collection.objects.link(o)
    return c,s

for name,coords in [('auto-corner',[(0,0,0),(1,0,0),(1,1,0)]),('auto-uneven',[(0,0,0),(.1,0,0),(.1,10,0)])]:
    c,s=curve(name,coords)
    for p in s.bezier_points:p.handle_left_type='AUTO';p.handle_right_type='AUTO'
    bpy.context.view_layer.update()
    p=s.bezier_points[1]
    print('REVIEW', (name,list(p.co),list(p.handle_left),list(p.handle_right),(p.handle_left-p.co).length,(p.handle_right-p.co).length))

for name,left,right in [('aligned-free','ALIGNED','FREE'),('aligned-aligned','ALIGNED','ALIGNED')]:
    c,s=curve(name,[(0,0,0),(1,0,0),(2,0,0)])
    p=s.bezier_points[1];p.handle_left_type=left;p.handle_right_type=right
    p.handle_left=(.5,0,0);p.handle_right=(1,.5,0)
    bpy.context.view_layer.update()
    print('REVIEW',(name,list(p.co),list(p.handle_left),list(p.handle_right)))
