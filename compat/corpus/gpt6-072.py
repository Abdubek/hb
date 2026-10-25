import bpy, math
from mathutils import Vector
bpy.ops.wm.read_factory_settings(use_empty=True)

def mat(name, color, metallic=0, roughness=0.45):
    m = bpy.data.materials.new(name)
    m.diffuse_color = (*color,1)
    m.use_nodes = True
    p = m.node_tree.nodes.get('Principled BSDF')
    p.inputs['Base Color'].default_value = (*color,1)
    p.inputs['Metallic'].default_value = metallic
    p.inputs['Roughness'].default_value = roughness
    return m

def box(name, loc, size, material, bevel=0.015):
    bpy.ops.mesh.primitive_cube_add(size=1, location=loc)
    o = bpy.context.object
    o.name = name
    o.dimensions = size
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    o.data.materials.append(material)
    if bevel:
        m = o.modifiers.new('Rounded edges','BEVEL')
        m.width = bevel
        m.segments = 3
        o.modifiers.new('Weighted normals','WEIGHTED_NORMAL')
    return o

def beam(name, a, b, width, depth, material):
    a,b = Vector(a),Vector(b)
    o = box(name,(a+b)/2,(width,depth,(b-a).length),material)
    o.rotation_euler = (b-a).to_track_quat('Z','Y').to_euler()
    return o

def tube(name, points, radius, material, cyclic=False):
    c = bpy.data.curves.new(name,'CURVE')
    c.dimensions = '3D'
    c.resolution_u = 1
    c.bevel_depth = radius
    c.bevel_resolution = 3
    s = c.splines.new('POLY')
    s.points.add(len(points)-1)
    for p,co in zip(s.points,points):
        p.co = (*co,1)
    s.use_cyclic_u = cyclic
    o = bpy.data.objects.new(name,c)
    bpy.context.collection.objects.link(o)
    c.materials.append(material)
    return o

def cyl(name, loc, radius, depth, material, vertices=32, axis=(0,0,1)):
    bpy.ops.mesh.primitive_cylinder_add(vertices=vertices,radius=radius,depth=depth,location=loc)
    o = bpy.context.object
    o.name = name
    o.rotation_euler = Vector(axis).to_track_quat('Z','Y').to_euler()
    o.data.materials.append(material)
    return o

pole = mat('Powder coated midnight steel',(0.045,0.065,0.085),0.65)
board = mat('White fiberglass backboard',(0.86,0.88,0.85),roughness=0.34)
orange = mat('Safety orange rim',(0.94,0.19,0.025),0.5,0.28)
black = mat('Black backboard graphics',(0.012,0.02,0.025),roughness=0.65)
rope = mat('Ivory woven nylon',(0.87,0.86,0.73),roughness=0.85)
metal = mat('Stainless mounting hardware',(0.5,0.55,0.59),0.85,0.24)
pad = mat('Blue pole safety padding',(0.055,0.16,0.29),roughness=0.8)
asphalt = mat('Blue gray outdoor court',(0.11,0.16,0.18),roughness=0.95)
white = mat('Court line paint',(0.9,0.88,0.79),roughness=0.8)
concrete = mat('Concrete foundation',(0.41,0.42,0.40),roughness=0.9)

box('Court surface',(0,-2,-0.065),(14,15,0.12),asphalt,0)
box('Concrete footing',(0,1.25,0.025),(0.85,0.85,0.06),concrete)
box('Steel base plate',(0,1.25,0.09),(0.50,0.50,0.06),pole)
box('Square structural pole',(0,1.25,1.86),(0.18,0.18,3.50),pole)
box('Pole cap',(0,1.25,3.63),(0.205,0.205,0.04),pole)
for x in (-0.18,0.18):
    for y in (1.07,1.43):
        cyl('Anchor washer',(x,y,0.128),0.034,0.01,metal)
        cyl('Anchor hex nut',(x,y,0.147),0.023,0.03,metal,6)
box('Pole impact pad',(0,1.215,0.94),(0.31,0.32,1.48),pad,0.055)
for z in (0.40,1.43):
    box('Padding strap',(0,1.215,z),(0.325,0.335,0.038),black,0.01)
for x in (-0.28,0.28):
    beam('Upper backboard support',(0,1.25,3.56),(x,0.09,3.62),0.08,0.09,pole)
    beam('Diagonal backboard brace',(0,1.25,2.73),(x,0.09,3.27),0.07,0.075,pole)
box('Rear mounting crossbar',(0,0.09,3.45),(1.28,0.10,0.10),pole)
# Board faces the negative Y half-court; rim top is approximately 3.05 m.
box('Fiberglass backboard',(0,0,3.50),(1.80,0.075,1.05),board,0.022)
for x in (-0.888,0.888):
    box('Vertical protective frame',(x,0,3.50),(0.035,0.105,1.06),pole,0.01)
for z in (2.985,4.015):
    box('Horizontal protective frame',(0,0,z),(1.80,0.105,0.035),pole,0.01)
for x in (-0.80,0.80):
    box('Backboard painted border',(x,-0.040,3.50),(0.025,0.003,0.87),black,0)
for z in (3.0775,3.9225):
    box('Backboard painted border',(0,-0.040,z),(1.625,0.003,0.025),black,0)
for x in (-0.295,0.295):
    box('Target rectangle side',(x,-0.043,3.29),(0.04,0.003,0.45),black,0)
for z in (3.085,3.495):
    box('Target rectangle rail',(0,-0.043,z),(0.63,0.003,0.04),black,0)
box('Breakaway rim mounting plate',(0,-0.072,3.055),(0.19,0.065,0.20),orange,0.008)
box('Rim mounting neck',(0,-0.142,3.032),(0.13,0.14,0.048),orange,0.008)
for x in (-0.065,0.065):
    for z in (2.995,3.12):
        cyl('Backboard mounting bolt',(x,-0.111,z),0.012,0.012,metal,6,(0,1,0))
center_y = -0.437
rim_z = 3.038
radius = 0.241
circle = [(radius*math.cos(t*math.tau/96),center_y+radius*math.sin(t*math.tau/96),rim_z) for t in range(96)]
tube('Orange regulation diameter rim',circle,0.0095,orange,True)
# Two crossing families form an open diamond net, with a tapered throat.
levels = 9
rings = []
for k in range(levels):
    f = k/(levels-1)
    r = 0.231 - 0.080*math.sin(f*math.pi*0.74)
    rings.append((r,3.023-0.435*f))
for family in (-1,1):
    for i in range(12):
        points = []
        for k,(r,z) in enumerate(rings):
            angle = math.tau*i/12 + family*k*math.pi/12
            points.append((r*math.cos(angle),center_y+r*math.sin(angle),z))
        tube('Interlaced nylon net strand',points,0.0024,rope)
for k in (0,levels-1):
    r,z = rings[k]
    tube('Net binding',[(r*math.cos(i*math.tau/72),center_y+r*math.sin(i*math.tau/72),z) for i in range(72)],0.003,rope,True)
for i in range(12):
    a = i*math.tau/12
    x,y = radius*math.cos(a),center_y+radius*math.sin(a)
    tube('Rim net hook',[(x,y,3.034),(x,y,3.014),(x*0.96,center_y+(y-center_y)*0.96,3.009)],0.003,orange)
# A portion of the key grounds the equipment in a basketball court.
for x in (-2.45,2.45):
    box('Key sideline',(x,-2.75,0.001),(0.05,5.50,0.006),white,0)
for y in (0,-5.5):
    box('Key end line',(0,y,0.001),(4.95,0.05,0.006),white,0)
tube('Free throw semicircle',[(1.8*math.cos(i*math.pi/64),-5.5-1.8*math.sin(i*math.pi/64),0.006) for i in range(65)],0.025,white)

world = bpy.data.worlds.new('Outdoor sky')
world.use_nodes = True
world.node_tree.nodes['Background'].inputs[0].default_value = (0.62,0.74,0.9,1)
world.node_tree.nodes['Background'].inputs[1].default_value = 0.5
bpy.context.scene.world = world
bpy.ops.object.light_add(type='AREA',location=(2,-4,7))
bpy.context.object.data.energy = 1200
bpy.context.object.data.size = 5
bpy.ops.object.light_add(type='SUN',location=(0,0,8))
bpy.context.object.rotation_euler = (0.4,-0.6,-0.35)
bpy.context.object.data.energy = 1.7
bpy.context.object.data.angle = 0.12
bpy.ops.object.camera_add(location=(5.8,-8.5,5.0))
cam = bpy.context.object
cam.rotation_euler = (Vector((0,-0.1,2.05))-cam.location).to_track_quat('-Z','Y').to_euler()
cam.data.type = 'ORTHO'
cam.data.ortho_scale = 5.9
scene = bpy.context.scene
scene.camera = cam
scene.render.engine = 'CYCLES'
scene.render.resolution_x = 1100
scene.render.resolution_y = 1400
scene.render.resolution_percentage = 100
scene.view_settings.view_transform = 'AgX'
