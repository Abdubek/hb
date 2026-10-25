import bpy, math
from mathutils import Vector

bpy.ops.wm.read_factory_settings(use_empty=True)
scene = bpy.context.scene
scene.render.engine = 'CYCLES'
scene.cycles.samples = 96
scene.render.resolution_x = 1400
scene.render.resolution_y = 1400
scene.render.resolution_percentage = 100
scene.view_settings.view_transform = 'AgX'
scene.world.color = (0.15,0.15,0.15)

def mat(name,color,metal=0,rough=0.4):
    m = bpy.data.materials.new(name)
    m.diffuse_color = (*color,1)
    m.use_nodes = True
    p = m.node_tree.nodes.get('Principled BSDF')
    p.inputs['Base Color'].default_value = (*color,1)
    p.inputs['Metallic'].default_value = metal
    p.inputs['Roughness'].default_value = rough
    return m
terracotta = mat('Terracotta powder coat',(0.42,0.105,0.052),0.22,0.34)
brass = mat('Satin brass hardware',(0.58,0.37,0.14),0.85,0.26)
cream = mat('Warm ivory reflector',(0.85,0.80,0.67),0.15,0.3)
black = mat('Rubber cord and feet',(0.012,0.014,0.016),0,0.62)
wood = mat('Dark walnut tabletop',(0.13,0.065,0.032),0,0.42)
bg = mat('Warm neutral studio',(0.30,0.28,0.25),0,0.8)
opal = mat('Opal LED diffuser',(1,0.87,0.62),0,0.34)
p = opal.node_tree.nodes.get('Principled BSDF')
p.inputs['Emission Color'].default_value = (1,0.72,0.38,1)
p.inputs['Emission Strength'].default_value = 2.5

def assign(o,m):
    o.data.materials.append(m)
    return o

def box(name,loc,dims,m,bevel=0):
    bpy.ops.mesh.primitive_cube_add(size=1,location=loc)
    o = bpy.context.object
    o.name = name
    o.dimensions = dims
    bpy.ops.object.transform_apply(location=False,rotation=False,scale=True)
    assign(o,m)
    if bevel:
        b = o.modifiers.new('Rounded edges','BEVEL')
        b.width = bevel
        b.segments = 4
        o.modifiers.new('Weighted normals','WEIGHTED_NORMAL')
    return o

def cylinder(name,r,depth,loc,m):
    bpy.ops.mesh.primitive_cylinder_add(vertices=96,radius=r,depth=depth,location=loc)
    o = bpy.context.object
    o.name = name
    assign(o,m)
    for p in o.data.polygons:
        p.use_smooth = True
    b = o.modifiers.new('Soft edge','BEVEL')
    b.width = min(0.008,depth*0.2)
    b.segments = 3
    o.modifiers.new('Weighted normals','WEIGHTED_NORMAL')
    return o

def curve(name,points,r,m):
    c = bpy.data.curves.new(name,'CURVE')
    c.dimensions = '3D'
    c.resolution_u = 32
    c.bevel_depth = r
    c.bevel_resolution = 5
    c.use_fill_caps = True
    s = c.splines.new('BEZIER')
    s.bezier_points.add(len(points)-1)
    for p,co in zip(s.bezier_points,points):
        p.co = co
        p.handle_left_type = 'AUTO'
        p.handle_right_type = 'AUTO'
    o = bpy.data.objects.new(name,c)
    scene.collection.objects.link(o)
    assign(o,m)
    return o

box('Walnut desk slab',(0,0,-0.055),(3.8,2.2,0.11),wood,0.035)
box('Studio floor',(0,0,-0.83),(200,200,0.08),bg)
for x in (-1.5,1.5):
    box('Desk pedestal',(x,0,-0.43),(0.10,1.6,0.75),black,0.015)
for x,y in [(-0.15,-0.12),(0.15,-0.12),(0,0.16)]:
    cylinder('Rubber isolation foot',0.035,0.012,(x,y,0.006),black)
cylinder('Weighted circular base',0.265,0.065,(0,0,0.043),terracotta)
cylinder('Base brass reveal',0.238,0.010,(0,0,0.078),brass)
cylinder('Base top plate',0.229,0.012,(0,0,0.089),terracotta)
cylinder('Dimmer dial',0.037,0.019,(0.10,-0.105,0.106),brass)
box('Dial indicator',(0.10,-0.12,0.116),(0.003,0.017,0.0015),black,0.0007)
# A single sweeping S-shaped tube is the central sculptural gesture.
curve('Continuous sculptural gooseneck',[(-0.10,0.035,0.09),(-0.25,0.035,0.32),(-0.30,0.035,0.64),(-0.16,0.035,0.98),(0.10,0.035,1.10),(0.29,0.035,1.01)],0.026,terracotta)
curve('Brass spine accent',[(-0.124,0.035,0.13),(-0.276,0.035,0.33),(-0.326,0.035,0.64),(-0.177,0.035,0.994),(0.10,0.035,1.126)],0.005,brass)
joint = cylinder('Shade pivot',0.045,0.073,(0.29,0.035,1.01),brass)
joint.rotation_euler.x = math.pi/2
screw = cylinder('Pivot screw',0.018,0.004,(0.29,-0.004,1.01),black)
screw.rotation_euler.x = math.pi/2
box('Pivot screw slot',(0.29,-0.0065,1.01),(0.021,0.002,0.003),brass,0.0005)

# Thick shell: outer dome returns through the rim to an ivory inner reflector.
origin = Vector((0.31,0.035,0.90))
rot = Vector((-0.32,0,1)).normalized().to_track_quat('Z','Y')
profile = [(0,0.19),(0.055,0.18),(0.12,0.14),(0.185,0.075),(0.24,-0.015),(0.255,-0.075),(0.252,-0.09),(0.239,-0.09),(0.225,-0.025),(0.174,0.061),(0.109,0.123),(0.046,0.16),(0,0.169)]
N = 128
verts = [tuple(origin + rot @ Vector((r*math.cos(2*math.pi*j/N),r*math.sin(2*math.pi*j/N),z))) for r,z in profile for j in range(N)]
faces = []
for k in range(len(profile)-1):
    for j in range(N):
        a,b = k*N+j,k*N+(j+1)%N
        faces.append((a,b,b+N,a+N))
me = bpy.data.meshes.new('Double-surface domed shade')
me.from_pydata(verts,[],faces)
me.update()
o = bpy.data.objects.new('Tilted sculpted reflector shade',me)
scene.collection.objects.link(o)
me.materials.append(terracotta)
me.materials.append(cream)
me.materials.append(brass)
for p in me.polygons:
    k = p.index//N
    p.material_index = 2 if k == 6 else (1 if k >= 7 else 0)
    p.use_smooth = True
loc = origin + rot @ Vector((0,0,-0.035))
diffuser = cylinder('Inset opal light disc',0.201,0.009,loc,opal)
diffuser.rotation_euler = rot.to_euler()
curve('Power cord',[(-0.16,0.15,0.045),(-0.34,0.31,0.014),(-0.69,0.36,0.012),(-0.86,0.17,0.012),(-1.16,0.30,0.012),(-1.34,0.55,0.012)],0.007,black)
box('Inline cord switch',(-0.78,0.25,0.025),(0.105,0.043,0.028),black,0.012)

def aim(o,target):
    o.rotation_euler = (Vector(target)-o.location).to_track_quat('-Z','Y').to_euler()
def area(name,loc,target,power,size,color=(1,1,1)):
    d = bpy.data.lights.new(name,'AREA')
    d.energy = power
    d.size = size
    d.color = color
    o = bpy.data.objects.new(name,d)
    scene.collection.objects.link(o)
    o.location = loc
    aim(o,target)
    return o
lightpos = origin + rot @ Vector((0,0,-0.047))
area('Warm working lamp output',lightpos,lightpos + rot @ Vector((0,0,-1)),18,0.34,(1,0.73,0.43))
area('Studio key',(-2,-2.8,3.5),(0,0,0.6),450,2.5)
area('Studio fill',(2,-1,2.5),(0,0,0.5),180,2.0,(0.8,0.88,1))
area('Rear edge light',(1,2,3),(0,0,0.7),380,1.5)

def camera(name,loc,target,lens=55,ortho=None):
    d = bpy.data.cameras.new(name)
    o = bpy.data.objects.new(name,d)
    scene.collection.objects.link(o)
    o.location = loc
    aim(o,target)
    if ortho is not None:
        d.type = 'ORTHO'
        d.ortho_scale = ortho
    else:
        d.lens = lens
    d.clip_start = 0.01
    d.clip_end = 300
    return o
hero = camera('CAM 01 - front three-quarter hero',(2.4,-3.4,2.15),(0,0,0.58),58)
camera('CAM 02 - opposite rear detail',(-2.5,2.6,1.85),(0,0,0.62),62)
camera('CAM 03 - orthographic front elevation',(0,-5,0.60),(0,0,0.60),ortho=1.65)
scene.camera = hero
for frame,name in [(1,'CAM 01 - front three-quarter hero'),(60,'CAM 02 - opposite rear detail'),(120,'CAM 03 - orthographic front elevation')]:
    marker = scene.timeline_markers.new(name,frame=frame)
    marker.camera = bpy.data.objects[name]
scene.frame_end = 120
scene.frame_set(1)
