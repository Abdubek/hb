import bpy, math
from mathutils import Vector
bpy.ops.wm.read_factory_settings(use_empty=True)

def mat(name, rgb, metal=0, glow=0):
    m=bpy.data.materials.new(name)
    m.diffuse_color=(*rgb,1)
    m.use_nodes=True
    p=m.node_tree.nodes.get('Principled BSDF')
    p.inputs['Base Color'].default_value=(*rgb,1)
    p.inputs['Metallic'].default_value=metal
    p.inputs['Roughness'].default_value=0.35
    if glow:
        p.inputs['Emission Color'].default_value=(*rgb,1)
        p.inputs['Emission Strength'].default_value=glow
    return m

def finish(o,name,m,bevel=0.02):
    o.name=name
    o.data.materials.append(m)
    if bevel:
        b=o.modifiers.new('Rounded fabrication edges','BEVEL')
        b.width,b.segments=bevel,2
        o.modifiers.new('Weighted normals','WEIGHTED_NORMAL')
    return o

def box(name,loc,size,m,bevel=0.02):
    bpy.ops.mesh.primitive_cube_add(size=1,location=loc)
    o=bpy.context.object
    o.dimensions=size
    bpy.ops.object.transform_apply(location=False,rotation=False,scale=True)
    return finish(o,name,m,bevel)

def cyl(name,a,b,r,m,verts=24):
    a,b=Vector(a),Vector(b)
    bpy.ops.mesh.primitive_cylinder_add(vertices=verts,radius=r,depth=(b-a).length,location=(a+b)/2)
    o=bpy.context.object
    o.rotation_mode='QUATERNION'
    o.rotation_quaternion=(b-a).to_track_quat('Z','Y')
    finish(o,name,m,0.008)
    for p in o.data.polygons:
        p.use_smooth=len(p.vertices)==4
    return o

def beam(name,a,b,width,depth,m):
    a,b=Vector(a),Vector(b)
    o=box(name,(a+b)/2,(width,depth,(b-a).length),m,0.045)
    o.rotation_mode='QUATERNION'
    o.rotation_quaternion=(b-a).to_track_quat('Z','Y')
    return o

def cable(name,points,r,m):
    c=bpy.data.curves.new(name,'CURVE')
    c.dimensions,c.bevel_depth,c.bevel_resolution='3D',r,3
    s=c.splines.new('BEZIER')
    s.bezier_points.add(len(points)-1)
    for p,co in zip(s.bezier_points,points):
        p.co=co
        p.handle_left_type=p.handle_right_type='AUTO'
    o=bpy.data.objects.new(name,c)
    bpy.context.collection.objects.link(o)
    o.data.materials.append(m)

def text(body,loc,size,m):
    c=bpy.data.curves.new(body,'FONT')
    c.body,c.size,c.align_x=body,size,'CENTER'
    o=bpy.data.objects.new(body,c)
    bpy.context.collection.objects.link(o)
    o.location=loc
    o.rotation_euler.x=math.pi/2
    o.data.materials.append(m)

silver=mat('Roller stainless',(0.53,0.61,0.64),0.85)
frame=mat('Machine frame graphite',(0.075,0.11,0.14),0.7)
orange=mat('Robot orange enamel',(0.95,0.22,0.035),0.45)
yellow=mat('Safety fence yellow',(0.94,0.62,0.035),0.4)
black=mat('Rubber and mesh',(0.012,0.019,0.022),0.35)
white=mat('Equipment ivory',(0.7,0.77,0.76),0.3)
cyan=mat('Sensor lens blue',(0.015,0.47,0.9),0.45,2)
green=mat('Status green',(0.03,0.8,0.19),0.1,4)
red=mat('Emergency red',(0.85,0.018,0.006),0.2)
amber=mat('Status amber',(1,0.36,0.02),0.2,0.5)
floor=mat('Epoxy floor',(0.16,0.19,0.22),0.1)
box('Factory floor',(0,0,-0.15),(200,200,0.25),floor)
box('Inspection cell plinth',(0,0,0.015),(9.6,6.8,0.1),frame,0.1)
for y in (-2.98,2.98):
    box('Cell safety perimeter',(0,y,0.076),(9,0.055,0.012),yellow,0)
for x in (-4.45,4.45):
    box('Cell safety perimeter',(x,0,0.076),(0.055,6,0.012),yellow,0)

# Conveyor runs on X; its open ends pass through guarded portals.
for y in (-0.85,0.85):
    box('Conveyor side channel',(0,y,1.02),(8.6,0.17,0.33),frame)
    box('Upper guide rail',(0,y,1.28),(8.6,0.045,0.1),silver,0.012)
    for x in (-3.65,-1.2,1.2,3.65):
        box('Adjustable conveyor leg',(x,y,0.56),(0.13,0.13,0.88),silver)
        cyl('Threaded leveling stem',(x,y,0.1),(x,y,0.24),0.045,black)
        cyl('Leveling foot',(x,y,0.09),(x,y,0.14),0.13,black)
        cyl('Rail fastener',(x,y-0.1,1.02),(x,y+0.1,1.02),0.036,silver,6)
for x in (-3.65,-1.2,1.2,3.65):
    box('Conveyor cross tie',(x,0,0.48),(0.1,1.7,0.1),frame)
for i in range(37):
    x=-4.14+i*0.23
    cyl('Powered conveyor roller %02d'%i,(x,-0.76,1.1),(x,0.76,1.1),0.103,silver)
    for y in (-0.795,0.795):
        cyl('Roller bearing',(x,y-0.03,1.1),(x,y+0.03,1.1),0.058,black)
box('Conveyor drive cover',(-3.3,1.08,0.96),(0.8,0.43,0.43),orange,0.06)
cyl('Conveyor gearmotor',(-3.3,1.14,0.96),(-3.3,1.75,0.96),0.17,frame)
for x in (-2.8,0.2,2.65):
    box('Inspection pallet',(x,0,1.27),(0.92,1.12,0.12),black)
    box('Cast workpiece',(x,0,1.48),(0.68,0.8,0.3),silver,0.08)
    cyl('Workpiece raised hub',(x,0,1.61),(x,0,1.91),0.2,frame)
    cyl('Hub face',(x,0,1.907),(x,0,1.925),0.12,black)
    for dx in (-0.22,0.22):
        for dy in (-0.27,0.27):
            cyl('Workpiece bolt',(x+dx,dy,1.625),(x+dx,dy,1.66),0.045,frame,6)

for x in (-1.6,1.65):
    for y in (-1.13,1.13):
        box('Sensor arch foot',(x,y,0.16),(0.48,0.46,0.15),frame)
        box('Extruded sensor arch upright',(x,y,1.58),(0.17,0.17,2.82),silver)
        box('Extrusion channel',(x,y-0.09,1.6),(0.038,0.012,2.5),black,0)
        box('Side vision camera',(x,y*0.89,1.83),(0.29,0.28,0.34),frame)
        cyl('Side camera lens',(x,y*0.8,1.83),(x,y*0.68,1.83),0.09,cyan)
    box('Sensor arch crossbar',(x,0,2.96),(0.25,2.45,0.21),silver)
    box('Overhead inspection camera',(x,0,2.71),(0.42,0.4,0.3),frame)
    cyl('Downward camera lens',(x,0,2.57),(x,0,2.43),0.12,cyan)
    for y in (-0.57,0.57):
        box('Inspection light bar',(x,y,2.77),(0.3,0.37,0.07),white)
    box('Arch blue identification plate',(x,-1.231,2.55),(0.42,0.025,0.27),cyan)

# Articulated inspection arm, with each link terminating in a rotary joint.
base=Vector((-0.1,2.02,0.77))
shoulder=Vector((-0.1,2.02,1.28))
elbow=Vector((-0.6,1.88,2.48))
wrist=Vector((0.25,0.69,2.46))
tool=Vector((0.25,0.15,2.15))
box('Robot pedestal',(-0.1,2.02,0.37),(0.88,0.85,0.6),frame)
cyl('Robot slew base',(-0.1,2.02,0.62),base,0.38,orange)
beam('Shoulder column',base,shoulder,0.4,0.4,orange)
beam('Upper robot arm',shoulder,elbow,0.31,0.36,orange)
beam('Robot forearm',elbow,wrist,0.25,0.29,orange)
beam('Wrist adapter',wrist,tool,0.17,0.2,frame)
for p,r in ((shoulder,0.27),(elbow,0.24),(wrist,0.18)):
    cyl('Rotary joint housing',p+Vector((0,-0.22,0)),p+Vector((0,0.22,0)),r,frame)
    cyl('Joint face cap',p+Vector((0,-0.245,0)),p+Vector((0,-0.224,0)),r*0.65,silver)
box('Robot laser measurement head',tool,(0.32,0.3,0.23),white)
cyl('Measurement optical aperture',tool+Vector((0,0,-0.1)),tool+Vector((0,0,-0.19)),0.085,cyan)
cable('Robot flexible service loom',[(-0.1,2.24,0.9),(-0.3,2.24,1.6),(-0.6,2.12,2.62),(0,1.3,2.77),(0.36,0.42,2.37)],0.045,black)

# Welded-wire panels use a single mesh per panel for modest object counts.
def fence(a,b,height=2.15):
    a,b=Vector(a),Vector(b)
    delta=b-a
    width=delta.length
    u=delta.normalized()
    for p in (a,b):
        box('Fence post',(p.x,p.y,height/2+0.08),(0.085,0.085,height),yellow,0.012)
        box('Fence foot',(p.x,p.y,0.11),(0.26,0.26,0.09),frame)
    for z in (0.3,height):
        cyl('Panel frame rail',(a.x,a.y,z),(b.x,b.y,z),0.025,yellow,12)
    verts,faces=[],[]
    def wire(p,q,r=0.009):
        direction=(q-p).normalized()
        t=direction.cross(Vector((0,0,1)))
        if t.length<0.1:
            t=Vector((1,0,0))
        t.normalize()
        v=direction.cross(t)
        start=len(verts)
        for end in (p,q):
            for k in range(4):
                verts.append(tuple(end+r*(t*math.cos(k*math.pi/2)+v*math.sin(k*math.pi/2))))
        for k in range(4):
            faces.append((start+k,start+(k+1)%4,start+4+(k+1)%4,start+4+k))
    for i in range(1,int(width/0.15)):
        p=a+u*(i*0.15)
        wire(Vector((p.x,p.y,0.3)),Vector((p.x,p.y,height)))
    for i in range(1,int((height-0.3)/0.15)):
        z=0.3+i*0.15
        wire(Vector((a.x,a.y,z)),Vector((b.x,b.y,z)))
    mesh=bpy.data.meshes.new('Welded safety mesh')
    mesh.from_pydata(verts,[],faces)
    mesh.update()
    o=bpy.data.objects.new('Welded safety mesh',mesh)
    bpy.context.collection.objects.link(o)
    o.data.materials.append(black)
for y in (-2.75,2.75):
    for x in (-3.3,-1.65,0,1.65):
        fence((x,y,0),(x+1.65,y,0))
for x in (-3.3,3.3):
    fence((x,-2.75,0),(x,-1.12,0))
    fence((x,1.12,0),(x,2.75,0))
    box('Guarded conveyor portal header',(x,0,2.21),(0.12,2.33,0.15),yellow)
    for y in (-1.06,1.06):
        box('Safety light curtain',(x,y,1.77),(0.085,0.09,0.83),black)
        for z in (1.45,1.6,1.75,1.9,2.05):
            cyl('Curtain emitter',(x,y, z),(x,y-math.copysign(0.06,y),z),0.015,red,12)
box('Gate handle',(2.85,-2.83,1.12),(0.25,0.08,0.045),silver)
box('Safety interlock',(3.19,-2.83,1.62),(0.2,0.1,0.16),red)
box('Operator console stand',(-2.28,-3.02,0.7),(0.15,0.15,1.3),silver)
box('Operator panel',(-2.28,-3.05,1.42),(0.8,0.22,0.55),white,0.04)
box('HMI display',(-2.39,-3.172,1.47),(0.42,0.018,0.31),cyan,0.015)
cyl('Emergency stop',(-2.0,-3.18,1.41),(-2.0,-3.25,1.41),0.075,red)
text('VISION CELL 04',(-0.7,-2.82,1.5),0.14,white)
cyl('Tower light mast',(3.3,2.75,2.15),(3.3,2.75,2.69),0.035,silver)
for i,m in enumerate((green,amber,red)):
    cyl('Stack light segment',(3.3,2.75,2.65+i*0.15),(3.3,2.75,2.79+i*0.15),0.085,m)
for name,loc,power,color,size in [('Key',(1,-7,10),2100,(0.82,0.9,1),6),('Fill',(-7,-1,6),1500,(1,0.78,0.55),5),('Rim',(3,6,8),2300,(0.66,0.8,1),5)]:
    d=bpy.data.lights.new(name,'AREA')
    d.energy,d.color,d.size=power,color,size
    o=bpy.data.objects.new(name,d)
    bpy.context.collection.objects.link(o)
    o.location=loc
    o.rotation_euler=(Vector((0,0,1))-o.location).to_track_quat('-Z','Y').to_euler()
bpy.ops.object.camera_add(location=(11,-14,11))
cam=bpy.context.object
cam.rotation_euler=(Vector((0,0,1.0))-cam.location).to_track_quat('-Z','Y').to_euler()
cam.data.type,cam.data.ortho_scale='ORTHO',12.6
scene=bpy.context.scene
scene.camera=cam
scene.world.color=(0.13,0.13,0.13)
scene.render.engine='CYCLES'
scene.render.resolution_x,scene.render.resolution_y=1500,1100
scene.render.resolution_percentage=100
scene.view_settings.view_transform='AgX'
