import bpy, math
from mathutils import Vector

bpy.ops.wm.read_factory_settings(use_empty=True)

def mat(name,color,metallic=0.0,roughness=0.4):
    m=bpy.data.materials.new(name)
    m.diffuse_color=(*color,1)
    m.use_nodes=True
    p=m.node_tree.nodes.get('Principled BSDF')
    p.inputs['Base Color'].default_value=(*color,1)
    p.inputs['Metallic'].default_value=metallic
    p.inputs['Roughness'].default_value=roughness
    return m

def box(name,loc,size,material,bevel=0.0):
    bpy.ops.mesh.primitive_cube_add(size=1,location=loc)
    o=bpy.context.object
    o.name=name
    o.dimensions=size
    bpy.ops.object.transform_apply(location=False,rotation=False,scale=True)
    o.data.materials.append(material)
    if bevel:
        b=o.modifiers.new('Armor edge bevel','BEVEL')
        b.width=bevel
        b.segments=3
        o.modifiers.new('Weighted normals','WEIGHTED_NORMAL')
    return o

def rod(name,a,b,radius,material,vertices=32):
    a,b=Vector(a),Vector(b)
    bpy.ops.mesh.primitive_cylinder_add(vertices=vertices,radius=radius,depth=(b-a).length,location=(a+b)/2)
    o=bpy.context.object
    o.name=name
    o.rotation_euler=(b-a).to_track_quat('Z','Y').to_euler()
    o.data.materials.append(material)
    for p in o.data.polygons:
        p.use_smooth=True
    m=o.modifiers.new('Cylinder edge bevel','BEVEL')
    m.width=0.014
    m.segments=3
    o.modifiers.new('Weighted normals','WEIGHTED_NORMAL')
    return o

def beam(name,a,b,width,depth,material):
    a,b=Vector(a),Vector(b)
    o=box(name,(a+b)/2,(width,depth,(b-a).length),material,min(width,depth)*0.21)
    o.rotation_euler=(b-a).to_track_quat('Z','Y').to_euler()
    return o

def sphere(name,loc,scale,material):
    bpy.ops.mesh.primitive_uv_sphere_add(segments=32,ring_count=16,location=loc)
    o=bpy.context.object
    o.name=name
    o.scale=scale
    o.data.materials.append(material)
    for p in o.data.polygons:
        p.use_smooth=True
    return o

def cable(name,points,material,radius=0.026):
    data=bpy.data.curves.new(name,'CURVE')
    data.dimensions='3D'
    data.resolution_u=16
    data.bevel_depth=radius
    data.bevel_resolution=3
    s=data.splines.new('BEZIER')
    s.bezier_points.add(len(points)-1)
    for p,co in zip(s.bezier_points,points):
        p.co=co
        p.handle_left_type='AUTO'
        p.handle_right_type='AUTO'
    o=bpy.data.objects.new(name,data)
    bpy.context.collection.objects.link(o)
    o.data.materials.append(material)
    return o

def joint(name,p,side,radius):
    x,y,z=p
    rod(name+' motor housing',(x,y-0.13,z),(x,y+0.13,z),radius,dark)
    outer=y+side*0.15
    rod(name+' orange end cap',(x,outer-side*0.025,z),(x,outer+side*0.025,z),radius*0.82,orange)
    rod(name+' hub',(x,outer+side*0.027,z),(x,outer+side*0.048,z),radius*0.38,metal)
    for a in [0,math.pi/2,math.pi,3*math.pi/2]:
        xx=x+radius*0.60*math.cos(a)
        zz=z+radius*0.60*math.sin(a)
        rod(name+' cap bolt',(xx,outer+side*0.025,zz),(xx,outer+side*0.039,zz),0.023,metal,16)

def area(loc,power,size,target):
    bpy.ops.object.light_add(type='AREA',location=loc)
    o=bpy.context.object
    o.data.energy=power
    o.data.size=size
    o.rotation_euler=(Vector(target)-o.location).to_track_quat('-Z','Y').to_euler()

orange=mat('Safety orange armor',(0.86,0.245,0.045),0.28,0.32)
dark=mat('Graphite mechanical frame',(0.035,0.055,0.069),0.72,0.31)
metal=mat('Brushed alloy',(0.47,0.57,0.64),0.85,0.24)
rubber=mat('Rubber feet and cable jackets',(0.018,0.025,0.03),0,0.79)
white=mat('Ceramic markings',(0.80,0.87,0.88),0.1,0.38)
lens=mat('Optical lens glass',(0.025,0.105,0.17),0.6,0.11)
cyan=mat('Cyan status lights',(0.035,0.63,0.83),0.2,0.23)
p=cyan.node_tree.nodes.get('Principled BSDF')
p.inputs['Emission Color'].default_value=(0.02,0.55,0.95,1)
p.inputs['Emission Strength'].default_value=3
floor=mat('Studio ground',(0.22,0.27,0.31),0,0.76)

box('Ground',(0,0,-0.10),(200,200,0.2),floor)
box('Central structural chassis',(0,0,1.69),(2.32,0.95,0.57),dark,0.16)
box('Orange upper body armor',(0,0,1.98),(2.30,1.02,0.28),orange,0.115)
box('Underside battery pack',(-0.12,0,1.40),(1.55,0.76,0.20),metal,0.06)
box('Spine service panel',(-0.14,0,2.132),(1.37,0.60,0.045),dark,0.06)
for x in [-0.70,0.40]:
    for y in [-0.23,0.23]:
        rod('Service panel screw',(x,y,2.154),(x,y,2.17),0.029,metal,16)
for x in [-0.66,-0.48,-0.30,-0.12,0.06,0.24]:
    box('Top cooling slot',(x,0,2.157),(0.07,0.36,0.015),rubber,0.015)
for side in [-1,1]:
    box('Body side panel',(0,side*0.493,1.74),(1.33,0.055,0.35),orange,0.05)
    for i in range(6):
        box('Side cooling grille',(-0.47+i*0.115,side*0.525,1.74),(0.045,0.014,0.19),dark,0.012)
    box('Side identification stripe',(0.45,side*0.526,1.77),(0.20,0.016,0.065),white,0.008)
    for x in [-0.54,0.54]:
        rod('Carry handle mount',(x,side*0.38,2.09),(x,side*0.38,2.26),0.035,metal)
    rod('Carry handle grip',(-0.54,side*0.38,2.26),(0.54,side*0.38,2.26),0.048,rubber)

# Four distinct three-joint legs. Front knees bend rearward; rear knees forward.
for front in [True,False]:
    for side in [-1,1]:
        tag=('Front' if front else 'Rear')+(' left' if side>0 else ' right')
        hx=0.85 if front else -0.85
        hip=Vector((hx,side*0.66,1.73))
        knee=Vector((hx+(-0.34 if front else 0.34),side*0.84,0.91))
        ankle=Vector((hx+(0.19 if front else -0.19),side*0.90,0.22))
        rod(tag+' shoulder axle',(hx,side*0.37,1.73),(hx,side*0.72,1.73),0.16,metal)
        joint(tag+' hip',hip,side,0.235)
        beam(tag+' upper structural link',hip,knee,0.23,0.20,dark)
        start=hip.lerp(knee,0.20)
        end=hip.lerp(knee,0.79)
        start.y+=side*0.105
        end.y+=side*0.105
        beam(tag+' upper armor',start,end,0.22,0.075,orange)
        joint(tag+' knee',knee,side,0.175)
        beam(tag+' lower leg',knee,ankle,0.145,0.15,metal)
        a=knee.lerp(ankle,0.19)
        b=knee.lerp(ankle,0.79)
        a.y+=side*0.081
        b.y+=side*0.081
        beam(tag+' shin cover',a,b,0.17,0.065,dark)
        # Exposed linear actuator beside each lower link.
        actuator_a=knee+Vector((0.10,side*0.12,-0.08))
        actuator_b=ankle+Vector((0.03,side*0.12,0.10))
        mid=actuator_a.lerp(actuator_b,0.56)
        rod(tag+' actuator barrel',actuator_a,mid,0.055,dark)
        rod(tag+' actuator piston',mid,actuator_b,0.026,metal)
        joint(tag+' ankle',ankle,side,0.105)
        box(tag+' foot chassis',(ankle.x+0.045,ankle.y,0.135),(0.40,0.32,0.16),dark,0.055)
        box(tag+' rubber contact pad',(ankle.x+0.045,ankle.y,0.045),(0.43,0.35,0.09),rubber,0.04)
        for offset in [-0.13,0,0.13]:
            box(tag+' tread block',(ankle.x+0.045+offset,ankle.y,0.025),(0.072,0.37,0.05),rubber,0.014)
        cable(tag+' joint wiring',[hip+Vector((-0.13,-side*0.09,-0.08)),hip.lerp(knee,0.50)+Vector((-0.20,-side*0.11,0)),knee+Vector((-0.12,-side*0.09,0.10))],rubber)

# Forward sensor head with a short articulated neck, two cameras and rangefinder.
rod('Neck pivot axle',(1.10,-0.25,1.92),(1.10,0.25,1.92),0.18,dark)
beam('Neck support',(1.08,0,1.92),(1.42,0,2.16),0.32,0.38,metal)
box('Sensor head housing',(1.56,0,2.19),(0.66,0.79,0.49),orange,0.10)
box('Black sensor face',(1.901,0,2.19),(0.055,0.66,0.35),dark,0.065)
for y in [-0.205,0.205]:
    rod('Camera bezel',(1.925,y,2.23),(1.972,y,2.23),0.107,metal)
    rod('Camera optic',(1.974,y,2.23),(1.987,y,2.23),0.082,lens)
    rod('Camera inner lens',(1.988,y,2.23),(1.994,y,2.23),0.043,cyan)
box('Front range sensor',(1.939,0,2.08),(0.024,0.24,0.047),rubber,0.012)
box('Head status light',(1.58,-0.401,2.23),(0.19,0.012,0.038),cyan,0.012)
for y in [-0.31,0.31]:
    ear=box('Short antenna fin',(1.43,y,2.51),(0.13,0.105,0.30),dark,0.035)
    ear.rotation_euler.y=math.radians(-12)
rod('Top lidar pedestal',(-0.69,0,2.14),(-0.69,0,2.28),0.15,metal)
rod('Lidar sensor drum',(-0.69,0,2.28),(-0.69,0,2.44),0.22,dark)
rod('Lidar optical band',(-0.69,0,2.33),(-0.69,0,2.385),0.225,lens)
rod('Lidar cap',(-0.69,0,2.44),(-0.69,0,2.48),0.225,orange)
beam('Short rear antenna tail',(-1.14,0,1.89),(-1.60,0,2.20),0.085,0.085,dark)
sphere('Tail status tip',(-1.60,0,2.20),(0.074,0.074,0.074),cyan)

area((2,-5,7),1350,5,(0,0,1.2))
area((-4,3,5),1600,4,(0,0,1.2))
area((4,3,4),850,3,(0.8,0,1.8))
bpy.ops.object.camera_add(location=(6.4,-7.7,4.6))
cam=bpy.context.object
cam.rotation_euler=(Vector((0.15,0,1.25))-cam.location).to_track_quat('-Z','Y').to_euler()
cam.data.type='ORTHO'
cam.data.ortho_scale=5.5
scene=bpy.context.scene
scene.camera=cam
scene.render.engine='CYCLES'
scene.cycles.samples=64
scene.world.color=(0.22,0.22,0.22)
scene.render.resolution_x=1500
scene.render.resolution_y=1150
scene.render.resolution_percentage=100
scene.view_settings.view_transform='AgX'
