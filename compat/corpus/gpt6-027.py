import bpy, math
from mathutils import Vector
bpy.ops.object.select_all(action='SELECT'); bpy.ops.object.delete(use_global=False)

def mat(name,c,rough=.5,metal=0):
    m=bpy.data.materials.new(name); m.diffuse_color=(*c,1); m.use_nodes=True; p=m.node_tree.nodes.get('Principled BSDF'); p.inputs['Base Color'].default_value=(*c,1); p.inputs['Roughness'].default_value=rough; p.inputs['Metallic'].default_value=metal; return m

def box(name,loc,size,m,bevel=.04):
    bpy.ops.mesh.primitive_cube_add(size=1,location=loc); o=bpy.context.object; o.name=name; o.dimensions=size; bpy.ops.object.transform_apply(location=False,rotation=False,scale=True); o.data.materials.append(m)
    if bevel: b=o.modifiers.new('Rounded edges','BEVEL'); b.width=bevel; b.segments=4; o.modifiers.new('Weighted normals','WEIGHTED_NORMAL')
    return o

def cylinder(name,a,b,r,m,vertices=32,r2=None):
    a=Vector(a); b=Vector(b); v=b-a
    if r2 is None: bpy.ops.mesh.primitive_cylinder_add(vertices=vertices,radius=r,depth=v.length,location=(a+b)/2)
    else: bpy.ops.mesh.primitive_cone_add(vertices=vertices,radius1=r,radius2=r2,depth=v.length,location=(a+b)/2)
    o=bpy.context.object; o.name=name; o.rotation_euler=v.to_track_quat('Z','Y').to_euler(); o.data.materials.append(m)
    bevel=o.modifiers.new('Edge radii','BEVEL'); bevel.width=.006; bevel.segments=3; o.modifiers.new('Normals','WEIGHTED_NORMAL')
    for p in o.data.polygons: p.use_smooth=True
    return o

def pipe(name,points,r,m):
    c=bpy.data.curves.new(name,'CURVE'); c.dimensions='3D'; c.bevel_depth=r; c.bevel_resolution=3; s=c.splines.new('BEZIER'); s.bezier_points.add(len(points)-1)
    for p,co in zip(s.bezier_points,points): p.co=co; p.handle_left_type='AUTO'; p.handle_right_type='AUTO'
    o=bpy.data.objects.new(name,c); bpy.context.collection.objects.link(o); c.materials.append(m); return o

black=mat('Graphite molded nylon',(.035,.045,.055),.43); rubber=mat('Soft caster tread',(.016,.021,.025),.8); chrome=mat('Brushed aluminum',(.52,.58,.63),.26,.85); cloth=mat('Deep teal woven fabric',(.035,.22,.25),.86); seam=mat('Teal piping',(.018,.095,.11),.75)
n=cloth.node_tree.nodes; l=cloth.node_tree.links; noise=n.new('ShaderNodeTexNoise'); noise.inputs['Scale'].default_value=190; bump=n.new('ShaderNodeBump'); bump.inputs['Strength'].default_value=.24; bump.inputs['Distance'].default_value=.008; l.new(noise.outputs['Fac'],bump.inputs['Height']); l.new(bump.outputs['Normal'],n.get('Principled BSDF').inputs['Normal'])
# Five radial spokes with exactly five twin-wheel caster assemblies.
for i in range(5):
    a=2*math.pi*i/5+math.pi/2; radial=Vector((math.cos(a),math.sin(a),0)); tangent=Vector((-math.sin(a),math.cos(a),0))
    inner=radial*.08+Vector((0,0,.32)); end=radial*.60+Vector((0,0,.23))
    spoke=box('Star base spoke %d'%(i+1),(inner+end)/2,(.12,.085,(end-inner).length),chrome,.035); spoke.rotation_euler=(end-inner).to_track_quat('Z','Y').to_euler()
    stem=radial*.60; cylinder('Caster %d swivel stem'%(i+1),stem+Vector((0,0,.16)),stem+Vector((0,0,.255)),.032,chrome)
    center=stem+radial*.035+Vector((0,0,.10))
    fork=box('Caster %d fork housing'%(i+1),center+Vector((0,0,.053)),(.10,.14,.095),black,.028); fork.rotation_euler.z=a
    cylinder('Caster axle',center-tangent*.095,center+tangent*.095,.025,chrome)
    for side in [-1,1]:
        c=center+tangent*side*.065
        cylinder('Caster %d wheel'% (i+1),c-tangent*.025,c+tangent*.025,.10,rubber)
        cylinder('Wheel hub',c+tangent*side*.026,c+tangent*side*.030,.049,black)
cylinder('Central base hub',(0,0,.23),(0,0,.39),.125,black)
cylinder('Gas lift shroud',(0,0,.32),(0,0,.60),.072,black)
cylinder('Gas lift piston',(0,0,.56),(0,0,.82),.043,chrome)
box('Under-seat tilt mechanism',(0,.035,.80),(.33,.36,.095),black,.03)
box('Seat pan',(0,-.055,.885),(.71,.68,.085),black,.075)
box('Upholstered seat cushion',(0,-.08,.968),(.73,.70,.14),cloth,.065)
pipe('Seat perimeter piping',[(-.29,-.415,.99),(.29,-.415,.99),(.354,-.35,.99),(.354,.20,.99),(.29,.26,.99),(-.29,.26,.99),(-.354,.20,.99),(-.354,-.35,.99),(-.29,-.415,.99)],.006,seam)
# Slightly reclined back and its structural support.
pipe('Back support spine',[(0,.23,.81),(0,.36,.93),(0,.39,1.18),(0,.44,1.56)],.041,black)
back=box('Backrest shell',(0,.405,1.46),(.68,.105,.78),black,.05); back.rotation_euler.x=math.radians(9)
back=box('Backrest cushion',(0,.345,1.465),(.625,.14,.72),cloth,.065); back.rotation_euler.x=math.radians(9)
for x in [-.22,.22]: pipe('Back stitched channel',[(x,.295,1.17),(x,.257,1.43),(x,.213,1.72)],.0025,seam)
box('Lumbar pad',(0,.25,1.27),(.48,.075,.145),cloth,.035)
for side in [-1,1]:
    x=side*.43
    pipe('Armrest support',[(side*.29,.13,.86),(x,.15,.95),(x,.10,1.20),(x,.00,1.24)],.031,black)
    cylinder('Arm height collar',(x,.09,1.06),(x,.09,1.16),.042,black)
    box('Padded armrest',(x,-.045,1.265),(.125,.39,.068),black,.032)
# Adjustment controls under the seat.
cylinder('Height lever',(0.16,-.02,.80),(.41,-.11,.79),.012,chrome)
box('Height lever grip',(.425,-.115,.79),(.11,.075,.035),black,.017)
cylinder('Tilt tension knob',(0,-.18,.80),(0,-.18,.71),.057,black)

floor=mat('Studio floor',(.30,.33,.36),.85); box('Floor',(0,0,-.035),(200,200,.06),floor,0)
scene=bpy.context.scene; scene.world.use_nodes=True; scene.world.node_tree.nodes['Background'].inputs[0].default_value=(.5,.57,.65,1); scene.world.node_tree.nodes['Background'].inputs[1].default_value=.35
for loc,energy,size in [((2,-3,5),650,3),((-3,-1,3),400,3),((1,3,4),800,2)]:
    bpy.ops.object.light_add(type='AREA',location=loc); o=bpy.context.object; o.data.energy=energy; o.data.size=size; o.rotation_euler=(Vector((0,0,1))-o.location).to_track_quat('-Z','Y').to_euler()
bpy.ops.object.camera_add(location=(3,-4,2.7)); cam=bpy.context.object; cam.rotation_euler=(Vector((0,0,.95))-cam.location).to_track_quat('-Z','Y').to_euler(); cam.data.type='ORTHO'; cam.data.ortho_scale=2.65; scene.camera=cam
scene.render.engine='CYCLES'; scene.cycles.samples=64; scene.render.resolution_x=1200; scene.render.resolution_y=1400; scene.render.resolution_percentage=100
