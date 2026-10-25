import bpy, math
from mathutils import Vector

bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)

def mat(name, color, metal=0, rough=0.45):
    m = bpy.data.materials.new(name)
    m.diffuse_color = (*color, 1)
    m.use_nodes = True
    p = m.node_tree.nodes.get('Principled BSDF')
    p.inputs['Base Color'].default_value = (*color, 1)
    p.inputs['Metallic'].default_value = metal
    p.inputs['Roughness'].default_value = rough
    return m

def finish(o, name, m, bevel=0):
    o.name = name
    o.data.materials.append(m)
    if bevel:
        mod = o.modifiers.new('Rounded edges', 'BEVEL')
        mod.width = bevel
        mod.segments = 3
        o.modifiers.new('Weighted normals', 'WEIGHTED_NORMAL')
    return o

def box(name, loc, dim, m, bevel=0.02):
    bpy.ops.mesh.primitive_cube_add(size=1, location=loc)
    o = bpy.context.object
    o.dimensions = dim
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    return finish(o, name, m, bevel)

def rod(name, a, b, r, m):
    a, b = Vector(a), Vector(b)
    bpy.ops.mesh.primitive_cylinder_add(vertices=32, radius=r, depth=(b-a).length, location=(a+b)/2)
    o = bpy.context.object
    o.rotation_euler = (b-a).to_track_quat('Z', 'Y').to_euler()
    for p in o.data.polygons:
        p.use_smooth = len(p.vertices) == 4
    return finish(o, name, m, 0.006)

def tube(name, points, r, m):
    c = bpy.data.curves.new(name, 'CURVE')
    c.dimensions = '3D'
    c.resolution_u = 1
    c.bevel_depth = r
    c.bevel_resolution = 4
    s = c.splines.new('POLY')
    s.points.add(len(points)-1)
    for p, co in zip(s.points, points):
        p.co = (*co, 1)
    o = bpy.data.objects.new(name, c)
    bpy.context.collection.objects.link(o)
    c.materials.append(m)
    return o

brass = mat('Satin brass frame', (0.65, 0.40, 0.12), 0.8, 0.25)
chrome = mat('Polished wheel hardware', (0.52, 0.58, 0.62), 0.85, 0.25)
rubber = mat('Dark rubber', (0.026, 0.032, 0.037), 0, 0.72)
carpet = mat('Burgundy platform carpet', (0.19, 0.018, 0.035), 0, 0.95)
navy = mat('Navy suitcase', (0.025, 0.075, 0.13), 0.06, 0.48)
tan = mat('Cognac suitcase', (0.45, 0.19, 0.065), 0, 0.55)
cream = mat('Ivory suitcase', (0.73, 0.66, 0.50), 0, 0.58)
strap = mat('Chocolate leather straps', (0.10, 0.045, 0.022), 0, 0.62)
tagmat = mat('Luggage tag paper', (0.91, 0.83, 0.61), 0, 0.8)
floor = mat('Warm stone floor', (0.30, 0.32, 0.33), 0, 0.7)
box('Studio floor', (0, 0, -0.07), (200, 200, 0.1), floor, 0)
box('Platform brass tray', (0, 0, 0.44), (1.72, 1.06, 0.17), brass, 0.085)
box('Thick perimeter bumper', (0, 0, 0.415), (1.78, 1.12, 0.09), rubber, 0.045)
box('Carpet deck', (0, 0, 0.539), (1.59, 0.93, 0.04), carpet, 0.04)
# Four complete swiveling caster assemblies.
for x in [-0.66, 0.66]:
    for y in [-0.36, 0.36]:
        rod('Caster swivel stem', (x, y, 0.30), (x, y, 0.38), 0.058, chrome)
        rod('Caster swivel bearing', (x, y, 0.31), (x, y, 0.355), 0.09, chrome)
        wx = x+0.035
        for side in [-1, 1]:
            box('Caster fork cheek', (wx, y+side*0.075, 0.225), (0.11, 0.028, 0.19), chrome, 0.025)
        rod('Rubber caster wheel', (wx, y-0.063, 0.155), (wx, y+0.063, 0.155), 0.15, rubber)
        rod('Wheel axle', (wx, y-0.104, 0.155), (wx, y+0.104, 0.155), 0.033, chrome)
        for side in [-1, 1]:
            rod('Wheel hub disc', (wx, y+side*0.065, 0.155), (wx, y+side*0.081, 0.155), 0.074, brass)
# Two tall, rounded inverted-U frames form the cart's handle cage.
for y in [-0.40, 0.40]:
    points = [(-0.76, y, 0.51), (-0.76, y, 2.11)]
    for i in range(13):
        t = math.pi - (math.pi/2)*i/12
        points.append((-0.49+0.27*math.cos(t), y, 2.11+0.27*math.sin(t)))
    points.append((0.49, y, 2.38))
    for i in range(1, 13):
        t = math.pi/2-(math.pi/2)*i/12
        points.append((0.49+0.27*math.cos(t), y, 2.11+0.27*math.sin(t)))
    points.append((0.76, y, 0.51))
    tube('Rounded upper cart frame', points, 0.041, brass)
    for x in [-0.76, 0.76]:
        rod('Post mounting socket', (x, y, 0.49), (x, y, 0.65), 0.058, brass)
for x in [-0.76, 0.76]:
    rod('Push handle', (x, -0.40, 1.30), (x, 0.40, 1.30), 0.038, brass)
    rod('Leather handle grip', (x, -0.22, 1.30), (x, 0.22, 1.30), 0.045, strap)
rod('Overhead hanger bar', (0, -0.40, 2.38), (0, 0.40, 2.38), 0.028, brass)

# Horizontal travel cases, built locally and then rotated as complete assemblies.
def suitcase(name, center, size, color, angle):
    before = set(bpy.data.objects)
    w, d, h = size
    box(name+' lower shell', (0, 0, -h*0.16), (w, d, h*0.66), color, 0.055)
    box(name+' lid', (0, 0, h*0.34), (w, d, h*0.32), color, 0.048)
    box(name+' zipper seam', (0, 0, h*0.17), (w+0.007, d+0.007, 0.021), rubber, 0.035)
    for x in [-w*0.32, w*0.32]:
        box('Leather strap across lid', (x, 0, h/2+0.004), (0.060, d-0.025, 0.017), strap, 0.008)
        for y in [-d/2-0.005, d/2+0.005]:
            box('Leather strap on side', (x, y, 0), (0.060, 0.017, h-0.03), strap, 0.008)
        box('Brass strap buckle', (x, -d/2-0.019, h*0.09), (0.084, 0.022, 0.080), brass, 0.01)
        box('Buckle leather inset', (x, -d/2-0.032, h*0.09), (0.046, 0.007, 0.047), strap, 0.004)
    for x in [-w/2+0.055, w/2-0.055]:
        for y in [-d/2+0.045, d/2-0.045]:
            for z in [-h/2+0.035, h/2-0.035]:
                box('Reinforced case corner', (x, y, z), (0.12, 0.10, 0.085), strap, 0.028)
    for x in [-0.13, 0.13]:
        box('Handle mount', (x, -d/2-0.018, -0.035), (0.053, 0.035, 0.071), brass, 0.011)
    tube('Front carry handle', [(-0.13, -d/2-0.04, -0.035), (-0.105, -d/2-0.10, 0.028), (0.105, -d/2-0.10, 0.028), (0.13, -d/2-0.04, -0.035)], 0.025, strap)
    for x in [-w*0.17, w*0.17]:
        box('Lid clasp', (x, -d/2-0.014, h*0.17), (0.045, 0.027, 0.075), brass, 0.008)
    root = bpy.data.objects.new(name+' assembly', None)
    bpy.context.collection.objects.link(root)
    for o in set(bpy.data.objects)-before:
        if o != root:
            o.parent = root
    root.location = center
    root.rotation_euler.z = angle

suitcase('Large navy trunk', (0, 0.01, 0.79), (1.35, 0.79, 0.46), navy, math.radians(-3))
suitcase('Cognac middle case', (0.04, 0, 1.215), (1.16, 0.68, 0.39), tan, math.radians(5))
suitcase('Small ivory case', (-0.08, 0.025, 1.575), (0.93, 0.56, 0.33), cream, math.radians(-7))
tube('Tag leather loop', [(0.0, -0.425, 1.20), (0.06, -0.44, 1.14), (0.09, -0.43, 1.10)], 0.006, strap)
tag = box('Hanging luggage tag', (0.095, -0.455, 1.065), (0.115, 0.012, 0.17), tagmat, 0.012)
tag.rotation_euler.y = -0.16
for z in [1.04, 1.065, 1.09]:
    box('Tag address line', (0.095, -0.463, z), (0.067, 0.002, 0.004), strap, 0)

scene = bpy.context.scene
scene.world = scene.world or bpy.data.worlds.new('World')
scene.world.use_nodes = True
scene.world.node_tree.nodes['Background'].inputs[0].default_value = (0.28, 0.32, 0.40, 1)
scene.world.node_tree.nodes['Background'].inputs[1].default_value = 0.4
for name, loc, energy, size in [('Key', (3, -4, 5), 1000, 4), ('Fill', (-4, -1, 3), 650, 3), ('Rim', (1, 4, 5), 1100, 3)]:
    bpy.ops.object.light_add(type='AREA', location=loc)
    o = bpy.context.object
    o.name = name
    o.data.energy = energy
    o.data.size = size
    o.rotation_euler = (Vector((0, 0, 1.2))-o.location).to_track_quat('-Z', 'Y').to_euler()
bpy.ops.object.camera_add(location=(4, -6, 3.7))
cam = bpy.context.object
cam.rotation_euler = (Vector((0, 0, 1.22))-cam.location).to_track_quat('-Z', 'Y').to_euler()
cam.data.type = 'ORTHO'
cam.data.ortho_scale = 3.65
scene.camera = cam
scene.render.resolution_x = 1200
scene.render.resolution_y = 1200
scene.render.resolution_percentage = 100
