import bpy, math
from mathutils import Vector
bpy.ops.object.select_all(action='SELECT'); bpy.ops.object.delete(use_global=False)

def mat(name,c,metal=0,rough=0.4):
    m=bpy.data.materials.new(name); m.diffuse_color=(*c,1); m.use_nodes=True; p=m.node_tree.nodes.get('Principled BSDF'); p.inputs['Base Color'].default_value=(*c,1); p.inputs['Metallic'].default_value=metal; p.inputs['Roughness'].default_value=rough; return m
paint=mat('Delivery teal enamel',(0.025,0.36,0.40),0.48,0.27)
white=mat('Warm white roof',(0.84,0.87,0.85),0.3,0.3)
black=mat('Rubber and trim',(0.025,0.033,0.04),0,0.72)
glass=mat('Smoked blue glazing',(0.055,0.13,0.18),0.5,0.16)
chrome=mat('Wheel alloy',(0.55,0.61,0.64),0.85,0.25)
seam=mat('Panel gaps',(0.012,0.09,0.105),0.1,0.5)
head=mat('Headlamp lenses',(0.83,0.94,1),0.25,0.16)
red=mat('Tail lamps',(0.7,0.018,0.01),0.15,0.2)
amber=mat('Indicators',(1,0.32,0.02),0.1,0.25)
floor=mat('Studio floor',(0.22,0.26,0.30),0,0.8)

def box(name,loc,dim,m,b=0.025):
    bpy.ops.mesh.primitive_cube_add(size=1,location=loc); o=bpy.context.object; o.name=name; o.dimensions=dim; bpy.ops.object.transform_apply(location=False,rotation=False,scale=True); o.data.materials.append(m)
    if b:
        q=o.modifiers.new('Rounded body edges','BEVEL'); q.width=b; q.segments=3; o.modifiers.new('Weighted normals','WEIGHTED_NORMAL')
    return o

def mesh(name,vs,fs,m):
    me=bpy.data.meshes.new(name); me.from_pydata(vs,[],fs); me.update(); o=bpy.data.objects.new(name,me); bpy.context.collection.objects.link(o); o.data.materials.append(m); return o

def panel(name,vs,m):
    o=mesh(name,vs,[tuple(range(len(vs)))],m); q=o.modifiers.new('Panel thickness','SOLIDIFY'); q.thickness=0.012; q=o.modifiers.new('Panel edge rounding','BEVEL'); q.width=0.018; q.segments=3; return o

def rod(name,a,b,r,m,n=32):
    a,b=Vector(a),Vector(b); bpy.ops.mesh.primitive_cylinder_add(vertices=n,radius=r,depth=(b-a).length,location=(a+b)/2); o=bpy.context.object; o.name=name; o.rotation_euler=(b-a).to_track_quat('Z','Y').to_euler(); o.data.materials.append(m)
    for p in o.data.polygons: p.use_smooth=len(p.vertices)==4
    return o

def line(name,pts,r,m):
    cu=bpy.data.curves.new(name,'CURVE'); cu.dimensions='3D'; cu.bevel_depth=r; cu.bevel_resolution=2; sp=cu.splines.new('POLY'); sp.points.add(len(pts)-1)
    for p,v in zip(sp.points,pts): p.co=(*v,1)
    o=bpy.data.objects.new(name,cu); bpy.context.collection.objects.link(o); o.data.materials.append(m); return o

# Front faces positive X. A single closed body shell gets real wheel openings.
profile=[(-2.08,0.48),(2.02,0.48),(2.08,1.21),(1.82,1.43),(1.02,1.51),(0.57,2.30),(-1.92,2.30),(-2.08,2.16)]
vs=[(x,y,z) for y in [-0.87,0.87] for x,z in profile]; n=len(profile)
fs=[tuple(reversed(range(n))),tuple(range(n,2*n))]+[(i,(i+1)%n,(i+1)%n+n,i+n) for i in range(n)]
body=mesh('Continuous van body',vs,fs,paint)
for x in [-1.27,1.28]:
    bpy.ops.mesh.primitive_cylinder_add(vertices=64,radius=0.535,depth=2.25,location=(x,0,0.49),rotation=(math.pi/2,0,0)); cutter=bpy.context.object
    bpy.context.view_layer.objects.active=body; body.select_set(True); cutter.select_set(False)
    mod=body.modifiers.new('Wheel arch opening','BOOLEAN'); mod.operation='DIFFERENCE'; mod.solver='EXACT'; mod.object=cutter; bpy.ops.object.modifier_apply(modifier=mod.name); bpy.data.objects.remove(cutter,do_unlink=True)
b=body.modifiers.new('Body corner radii','BEVEL'); b.width=0.065; b.segments=3; body.modifiers.new('Weighted body normals','WEIGHTED_NORMAL')
box('Floating white roof',(-0.69,0,2.305),(2.56,1.74,0.09),white,0.065)
box('Underbody',(0,0,0.45),(3.48,1.42,0.18),black,0.045)
for sy in [-1,1]:
    y=sy*0.879
    # Glazing is inset inside an explicit black gasket polygon.
    panel('Front side window gasket',[(0.02,y,1.48),(0.94,y,1.48),(0.53,y,2.22),(0.02,y,2.22)],black)
    panel('Front side glass',[(0.085,y+sy*0.014,1.55),(0.84,y+sy*0.014,1.55),(0.485,y+sy*0.014,2.155),(0.085,y+sy*0.014,2.155)],glass)
    line('Front door perimeter',[(0.00,y,2.23),(0.00,y,0.65),(0.69,y,0.65),(0.78,y,1.05),(1.04,y,1.43),(0.57,y,2.23),(0.00,y,2.23)],0.009,seam)
    line('Sliding cargo door seam',[(-1.84,y,2.16),(-0.13,y,2.16),(-0.13,y,0.63),(-0.69,y,0.63)],0.009,seam)
    line('Sliding door rear seam',[(-1.84,y,2.16),(-1.84,y,0.75)],0.009,seam)
    box('Sliding door runner',(-0.95,y+sy*0.025,1.02),(1.73,0.045,0.055),chrome,0.012)
    box('Sliding door handle recess',(-0.31,y+sy*0.015,1.40),(0.27,0.025,0.092),seam)
    box('Sliding door pull',(-0.31,y+sy*0.045,1.41),(0.19,0.042,0.037),black,0.015)
    box('Front door handle',(0.23,y+sy*0.039,1.38),(0.22,0.055,0.055),black,0.018)
    box('Side rubbing strip',(-0.25,y+sy*0.025,1.11),(3.17,0.04,0.07),black,0.016)
    rod('Mirror arm',(0.90,y,1.53),(1.0,sy*1.06,1.62),0.025,black)
    box('Door mirror',(0.99,sy*1.12,1.65),(0.25,0.16,0.21),black,0.05)
    box('Mirror glass',(0.852,sy*1.12,1.66),(0.012,0.125,0.16),chrome,0.02)
    box('Side indicator',(1.50,y+sy*0.014,1.23),(0.12,0.022,0.055),amber,0.016)
    for x in [-1.27,1.28]:
        pts=[(x+0.54*math.cos(a),sy*0.89,0.49+0.54*math.sin(a)) for a in [i*math.pi/40 for i in range(41)]]
        line('Wheel arch rubber trim',pts,0.026,black)
# Windshield follows the sloping cabin face.
def frontx(z): return 1.02-(z-1.51)*0.45/0.79+0.016
panel('Windshield gasket',[(frontx(1.56),-0.80,1.56),(frontx(1.56),0.80,1.56),(frontx(2.22),0.80,2.22),(frontx(2.22),-0.80,2.22)],black)
panel('Wide windshield',[(frontx(1.61)+0.012,-0.745,1.61),(frontx(1.61)+0.012,0.745,1.61),(frontx(2.17)+0.012,0.745,2.17),(frontx(2.17)+0.012,-0.745,2.17)],glass)
for y in [-0.40,0.36]:
    line('Windshield wiper',[(frontx(1.60)+0.025,y-0.16,1.60),(frontx(1.70)+0.025,y+0.04,1.70),(frontx(1.72)+0.025,y+0.30,1.72)],0.014,black)
box('Front bumper',(2.075,0,0.61),(0.18,1.82,0.22),black,0.07)
box('Rear bumper',(-2.115,0,0.59),(0.18,1.82,0.19),black,0.045)
box('Front grille surround',(2.08,0,0.98),(0.045,0.86,0.27),black,0.035)
for z in [0.89,0.95,1.01,1.07]: box('Grille slat',(2.11,0,z),(0.026,0.75,0.018),chrome,0.005)
for sy in [-1,1]:
    box('Headlight gasket',(2.075,sy*0.625,1.125),(0.06,0.35,0.25),black,0.045)
    box('Headlight lens',(2.112,sy*0.625,1.14),(0.025,0.29,0.185),head,0.04)
    box('Front turn signal',(2.123,sy*0.755,1.14),(0.027,0.045,0.15),amber,0.012)
    box('Rear vertical lamp',(-2.109,sy*0.76,1.25),(0.035,0.12,0.47),red,0.022)
    box('Reverse lens',(-2.131,sy*0.76,1.18),(0.009,0.105,0.085),head,0.006)
    panel('Rear window gasket',[(-2.096,sy*0.09,1.52),(-2.096,sy*0.65,1.52),(-2.096,sy*0.65,2.08),(-2.096,sy*0.09,2.08)],black)
    panel('Rear window',[(-2.110,sy*0.14,1.57),(-2.110,sy*0.60,1.57),(-2.110,sy*0.60,2.03),(-2.110,sy*0.14,2.03)],glass)
    for z in [0.97,1.90]: box('Rear door hinge',(-2.12,sy*0.69,z),(0.065,0.11,0.065),chrome,0.012)
line('Split rear doors',[(-2.12,0,0.73),(-2.12,0,2.17)],0.011,seam)
box('Rear door handle',(-2.14,-0.13,1.32),(0.06,0.055,0.20),black)
for x in [-1.27,1.28]:
    rod('Axle',(x,-0.95,0.49),(x,0.95,0.49),0.055,black)
    for sy in [-1,1]:
        y=sy*0.87
        bpy.ops.mesh.primitive_torus_add(major_segments=64,minor_segments=20,major_radius=0.345,minor_radius=0.125,location=(x,y,0.49),rotation=(math.pi/2,0,0)); o=bpy.context.object; o.name='Road tire'; o.data.materials.append(black)
        for p in o.data.polygons: p.use_smooth=True
        rod('Wheel barrel',(x,y-0.10,0.49),(x,y+0.10,0.49),0.27,chrome,48)
        yy=y+sy*0.116; rod('Inset wheel face',(x,yy-sy*0.022,0.49),(x,yy,0.49),0.218,seam,48)
        rod('Hub',(x,yy,0.49),(x,yy+sy*0.03,0.49),0.085,chrome)
        for i in range(6):
            a=i*math.tau/6
            rod('Alloy spoke',(x+0.065*math.sin(a),yy,0.49+0.065*math.cos(a)),(x+0.235*math.sin(a+0.13),yy,0.49+0.235*math.cos(a+0.13)),0.026,chrome,16)
            rod('Wheel bolt',(x+0.063*math.sin(a),yy,0.49+0.063*math.cos(a)),(x+0.063*math.sin(a),yy+sy*0.036,0.49+0.063*math.cos(a)),0.012,black,6)
# Raised, readable side graphics.
for sy in [-1,1]:
    cu=bpy.data.curves.new('Delivery lettering','FONT'); cu.body='PARCEL'; cu.align_x='CENTER'; cu.align_y='CENTER'; cu.size=0.26; cu.extrude=0.001
    o=bpy.data.objects.new('PARCEL side logo',cu); bpy.context.collection.objects.link(o); o.location=(-0.98,sy*0.902,1.80); o.rotation_euler=(math.pi/2,0,0 if sy==-1 else math.pi); o.data.materials.append(white)
for x in [-2.22,2.18]: box('License plate',(x,0,0.65),(0.015,0.43,0.115),white,0.012)
box('Floor',(0,0,-0.04),(200,200,0.05),floor)
scene=bpy.context.scene; scene.world.use_nodes=True; scene.world.node_tree.nodes['Background'].inputs[1].default_value=0.5
for loc,power,size in [((4,-5,7),1400,5),((-4,-1,5),1000,4),((1,5,6),1500,4)]:
    bpy.ops.object.light_add(type='AREA',location=loc); o=bpy.context.object; o.data.energy=power; o.data.size=size; o.rotation_euler=(Vector((0,0,1))-o.location).to_track_quat('-Z','Y').to_euler()
bpy.ops.object.camera_add(location=(6.5,-7,4.4)); cam=bpy.context.object; cam.rotation_euler=(Vector((0,0,1.10))-cam.location).to_track_quat('-Z','Y').to_euler(); cam.data.type='ORTHO'; cam.data.ortho_scale=5.7; scene.camera=cam
scene.render.engine='CYCLES'; scene.render.resolution_x=1400; scene.render.resolution_y=1000; scene.render.resolution_percentage=100
