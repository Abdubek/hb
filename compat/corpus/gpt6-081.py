import bpy, math
from mathutils import Vector

bpy.ops.wm.read_factory_settings(use_empty=True)

def mat(name, color, metallic=0.0, roughness=0.45):
    m = bpy.data.materials.new(name)
    m.diffuse_color = (*color, 1)
    m.use_nodes = True
    p = m.node_tree.nodes.get('Principled BSDF')
    p.inputs['Base Color'].default_value = (*color, 1)
    p.inputs['Metallic'].default_value = metallic
    p.inputs['Roughness'].default_value = roughness
    return m

def box(name, loc, size, material, bevel=0):
    bpy.ops.mesh.primitive_cube_add(size=1, location=loc)
    o = bpy.context.object
    o.name = name
    o.dimensions = size
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    o.data.materials.append(material)
    if bevel:
        b = o.modifiers.new('Soft edges', 'BEVEL')
        b.width = bevel
        b.segments = 3
        o.modifiers.new('Weighted normals', 'WEIGHTED_NORMAL')
    return o

def rod(name, a, b, radius, material, vertices=12):
    a, b = Vector(a), Vector(b)
    bpy.ops.mesh.primitive_cylinder_add(vertices=vertices, radius=radius, depth=(b-a).length, location=(a+b)/2)
    o = bpy.context.object
    o.name = name
    o.rotation_euler = (b-a).to_track_quat('Z', 'Y').to_euler()
    o.data.materials.append(material)
    for p in o.data.polygons:
        p.use_smooth = True
    return o

def cable(name, coords, radius, material):
    c = bpy.data.curves.new(name, 'CURVE')
    c.dimensions = '3D'
    c.bevel_depth = radius
    c.bevel_resolution = 3
    s = c.splines.new('POLY')
    s.points.add(len(coords)-1)
    for p, co in zip(s.points, coords):
        p.co = (*co, 1)
    o = bpy.data.objects.new(name, c)
    bpy.context.collection.objects.link(o)
    o.data.materials.append(material)
    return o

ivory = mat('Warm concrete', (0.56, 0.54, 0.47))
red = mat('Vermilion painted steel', (0.39, 0.07, 0.038), 0.6, 0.3)
steel = mat('Galvanized cable', (0.3, 0.36, 0.38), 0.8, 0.26)
asphalt = mat('Road surface', (0.055, 0.07, 0.08), 0, 0.8)
white = mat('Lane marking', (0.89, 0.85, 0.68))
water = mat('Deep teal water', (0.026, 0.16, 0.18), 0.35, 0.24)
land = mat('River banks', (0.24, 0.3, 0.23), 0, 0.95)
carpaint = mat('Ochre car paint', (0.83, 0.39, 0.065), 0.45, 0.3)
glass = mat('Dark glazing', (0.055, 0.13, 0.17), 0.4, 0.18)

box('Water study plinth', (0, 0, -0.42), (43, 20, 0.75), water, 0.3)
for x in (-19, 19):
    box('Raised riverbank', (x, 0, 0.2), (6, 20, 1.2), land, 0.3)
    box('Abutment', (x/19*16.4, 0, 1.75), (1.5, 5.7, 3), ivory, 0.12)
box('Structural deck', (0, 0, 3.15), (39, 4.7, 0.5), red, 0.06)
box('Road wearing course', (0, 0, 3.435), (39, 3.35, 0.08), asphalt, 0.018)
for y in (-2, 2):
    box('Pedestrian walkway', (0, y, 3.48), (39, 0.55, 0.16), ivory, 0.025)
for x in range(-19, 20, 2):
    box('Center dashed line', (x, 0, 3.483), (0.95, 0.07, 0.012), white)
for y in (-1.54, 1.54):
    box('Road edge line', (0, y, 3.483), (39, 0.055, 0.012), white)
for x in (-8, 8):
    for y in (-2.75, 2.75):
        box('Pier foundation', (x, y, 0.42), (2.1, 2.0, 1.0), ivory, 0.15)
        box('Tower leg', (x, y, 6.7), (0.8, 0.78, 12.2), red, 0.055)
        box('Tower cap', (x, y, 12.87), (0.98, 0.96, 0.22), red, 0.04)
        box('Cable saddle', (x, y, 12.0), (0.75, 0.5, 0.35), steel, 0.09)
    for z in (4.1, 10.65, 12.45):
        box('Portal crossbeam', (x, 0, z), (0.72, 6.2, 0.55), red, 0.045)
    rod('Portal diagonal', (x, -2.35, 10.9), (x, 2.35, 12.2), 0.095, red)
    rod('Portal diagonal', (x, 2.35, 10.9), (x, -2.35, 12.2), 0.095, red)

def cable_z(x):
    if abs(x) <= 8:
        return 5.1 + 6.9*(x/8)**2
    t = (abs(x)-8)/9
    return 12.0 - 9.8*t + 0.85*t*(t-1)

for y in (-2.75, 2.75):
    coords = [(x, y, cable_z(x)) for x in [-17+i*34/240 for i in range(241)]]
    cable('Continuous suspension main cable', coords, 0.105, steel)
    for i in range(-29, 30):
        x = i*0.5
        z = cable_z(x)
        if z > 3.45:
            rod('Vertical hanger', (x, y, 3.22), (x, y, z), 0.025, steel, 8)
            rod('Deck outrigger', (x, y, 3.22), (x, y/abs(y)*2.25, 3.22), 0.055, red)
    for x in (-17, 17):
        box('Cable anchor block', (x, y, 1.5), (1.8, 1.45, 1.45), ivory, 0.12)
for y in (-2.29, 2.29):
    for z in (3.9, 4.23):
        rod('Continuous railing', (-19.5, y, z), (19.5, y, z), 0.035, steel)
    for i in range(79):
        x = -19.5 + i*0.5
        rod('Railing post', (x, y, 3.55), (x, y, 4.23), 0.025, steel, 8)
for x in range(-19, 20):
    box('Deck transverse stiffener', (x, 0, 2.91), (0.12, 4.6, 0.25), red, 0.015)
for x, y in [(-4, -0.8), (5, 0.8), (13, -0.8)]:
    box('Scale car body', (x, y, 3.7), (1.2, 0.57, 0.34), carpaint, 0.12)
    box('Scale car cabin', (x-0.05, y, 3.96), (0.65, 0.48, 0.26), glass, 0.1)

world = bpy.data.worlds.new('Bridge atmosphere')
bpy.context.scene.world = world
world.use_nodes = True
world.node_tree.nodes['Background'].inputs[0].default_value = (0.65, 0.76, 0.85, 1)
world.node_tree.nodes['Background'].inputs[1].default_value = 0.45
bpy.ops.object.light_add(type='SUN', location=(0, 0, 20))
bpy.context.object.rotation_euler = (0.45, -0.5, -0.45)
bpy.context.object.data.energy = 2.4
bpy.context.object.data.angle = 0.15
bpy.ops.object.light_add(type='AREA', location=(1, -9, 20))
bpy.context.object.data.energy = 2200
bpy.context.object.data.shape = 'DISK'
bpy.context.object.data.size = 16
bpy.ops.object.camera_add(location=(31, -38, 26))
camera = bpy.context.object
camera.rotation_euler = (Vector((0, 0, 5))-camera.location).to_track_quat('-Z', 'Y').to_euler()
camera.data.type = 'ORTHO'
camera.data.ortho_scale = 48
scene = bpy.context.scene
scene.camera = camera
scene.render.engine = 'CYCLES'
scene.cycles.samples = 64
scene.render.resolution_x = 1600
scene.render.resolution_y = 1000
scene.render.resolution_percentage = 100
scene.view_settings.view_transform = 'AgX'
