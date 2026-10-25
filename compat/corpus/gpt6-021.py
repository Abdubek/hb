import bpy, math, random
from mathutils import Vector

bpy.ops.wm.read_factory_settings(use_empty=True)
random.seed(21)

def material(name, color, roughness=0.5, metallic=0.0):
    m = bpy.data.materials.new(name)
    m.diffuse_color = (*color, 1)
    m.use_nodes = True
    p = m.node_tree.nodes.get('Principled BSDF')
    p.inputs['Base Color'].default_value = (*color, 1)
    p.inputs['Roughness'].default_value = roughness
    p.inputs['Metallic'].default_value = metallic
    return m

cedar = material('Warm cedar', (0.38, 0.17, 0.065))
lightwood = material('Fresh cut slats', (0.56, 0.29, 0.12))
stone = material('Pale limestone', (0.56, 0.55, 0.46), 0.85)
iron = material('Blackened steel hardware', (0.045, 0.052, 0.045), 0.3, 0.8)
grass = material('Garden grass', (0.16, 0.25, 0.08), 0.95)
soil = material('Planter soil', (0.065, 0.035, 0.018), 1)
leaf = material('Leaves', (0.095, 0.27, 0.055), 0.8)
clay = material('Terracotta', (0.49, 0.19, 0.095), 0.85)

def box(name, loc, scale, mat, bevel=0.025):
    bpy.ops.mesh.primitive_cube_add(size=1, location=loc)
    o = bpy.context.object
    o.name = name
    o.dimensions = scale
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    o.data.materials.append(mat)
    if bevel:
        b = o.modifiers.new('Soft worked edges', 'BEVEL')
        b.width = bevel
        b.segments = 2
        o.modifiers.new('Weighted corner normals', 'WEIGHTED_NORMAL')
    return o

def beam(name, a, b, width, depth, mat):
    a, b = Vector(a), Vector(b)
    o = box(name, (a+b)/2, (width, depth, (b-a).length), mat)
    o.rotation_euler = (b-a).to_track_quat('Z', 'Y').to_euler()
    return o

def cylinder(name, loc, radius, depth, mat, vertices=24):
    bpy.ops.mesh.primitive_cylinder_add(vertices=vertices, radius=radius, depth=depth, location=loc)
    o = bpy.context.object
    o.name = name
    o.data.materials.append(mat)
    return o

def tube(name, points, radius, mat):
    c = bpy.data.curves.new(name, 'CURVE')
    c.dimensions = '3D'
    c.bevel_depth = radius
    c.bevel_resolution = 2
    s = c.splines.new('POLY')
    s.points.add(len(points)-1)
    for p, co in zip(s.points, points):
        p.co = (*co, 1)
    o = bpy.data.objects.new(name, c)
    bpy.context.collection.objects.link(o)
    o.data.materials.append(mat)
    return o

box('Lawn', (0, 0, -0.13), (200, 200, 0.2), grass, 0)
box('Raised patio foundation', (0, 0, 0.015), (6.5, 5.2, 0.14), stone)
for i in range(10):
    for j in range(8):
        box('Individual paving stone', (-2.88+i*0.64, -2.24+j*0.64, 0.105), (0.625, 0.625, 0.07), stone, 0.012)

for x in (-2.35, 2.35):
    for y in (-1.85, 1.85):
        box('Stone post footing', (x, y, 0.23), (0.58, 0.58, 0.22), stone)
        box('Steel post shoe', (x, y, 0.39), (0.325, 0.325, 0.25), iron, 0.01)
        box('Square cedar post', (x, y, 1.89), (0.29, 0.29, 3.0), cedar)
        box('Post capital', (x, y, 3.30), (0.42, 0.42, 0.13), cedar)
        sx, sy = -math.copysign(1, x), -math.copysign(1, y)
        beam('Longitudinal knee brace', (x, y, 2.48), (x+sx*0.72, y, 3.22), 0.14, 0.18, cedar)
        beam('Transverse knee brace', (x, y, 2.48), (x, y+sy*0.67, 3.22), 0.14, 0.18, cedar)
        for z in (2.62, 3.12):
            bolt = cylinder('Visible carriage bolt', (x, y-0.165, z), 0.035, 0.022, iron, 12)
            bolt.rotation_euler[0] = math.pi/2

for y in (-1.85, 1.85):
    box('Primary spanning beam', (0, y, 3.39), (5.85, 0.22, 0.32), cedar)
    for x in (-2.98, 2.98):
        box('Beam end cap', (x, y, 3.40), (0.15, 0.26, 0.36), lightwood)
for i in range(11):
    x = -2.75 + i*0.55
    box('Open overhead rafter', (x, 0, 3.65), (0.14, 4.85, 0.25), lightwood, 0.018)
for j in range(9):
    y = -2.30 + j*0.575
    box('Crosswise shade slat', (0, y, 3.83), (5.8, 0.07, 0.10), cedar, 0.012)

# Simple seating beneath the open lattice.
for x in (-1.45, 1.45):
    box('Bench trestle', (x, 1.03, 0.40), (0.13, 0.55, 0.52), cedar)
for j in range(4):
    box('Bench seat plank', (0, 0.80+j*0.16, 0.68), (3.4, 0.145, 0.10), lightwood)
beam('Bench stretcher', (-1.45, 1.03, 0.30), (1.45, 1.03, 0.30), 0.10, 0.12, cedar)

for x, y in [(-2.85, 1.85), (2.85, -1.85)]:
    bpy.ops.mesh.primitive_cone_add(vertices=32, radius1=0.30, radius2=0.43, depth=0.60, location=(x, y, 0.43))
    bpy.context.object.name = 'Tapered terracotta planter'
    bpy.context.object.data.materials.append(clay)
    bpy.ops.mesh.primitive_torus_add(major_radius=0.412, minor_radius=0.045, major_segments=40, minor_segments=10, location=(x, y, 0.73))
    bpy.context.object.data.materials.append(clay)
    cylinder('Soil surface', (x, y, 0.71), 0.38, 0.025, soil)
    px = math.copysign(2.35, x)
    points = [(x+(px-x)*min(t/10, 1)+0.16*math.sin(t*0.65), y+0.20*math.cos(t*0.65), 0.73+t*0.085) for t in range(37)]
    tube('Climbing vine', points, 0.023, leaf)
    for k, p in enumerate(points[2:]):
        if k % 2 == 0:
            bpy.ops.mesh.primitive_uv_sphere_add(segments=10, ring_count=6, radius=1, location=(p[0]+0.09*math.sin(k), p[1]+0.08*math.cos(k), p[2]))
            o = bpy.context.object
            o.name = 'Vine leaf'
            o.scale = (0.16, 0.065, 0.045)
            o.rotation_euler = (0.4, k*0.6, k*1.2)
            o.data.materials.append(leaf)

world = bpy.data.worlds.new('Garden sky')
world.use_nodes = True
world.node_tree.nodes['Background'].inputs[0].default_value = (0.65, 0.77, 0.95, 1)
world.node_tree.nodes['Background'].inputs[1].default_value = 0.35
bpy.context.scene.world = world
bpy.ops.object.light_add(type='SUN', location=(4, -6, 10))
bpy.context.object.rotation_euler = (0.45, -0.4, -0.45)
bpy.context.object.data.energy = 2.2
bpy.context.object.data.angle = 0.10
bpy.ops.object.light_add(type='AREA', location=(-4, -4, 7))
bpy.context.object.data.energy = 700
bpy.context.object.data.shape = 'DISK'
bpy.context.object.data.size = 5
bpy.context.object.rotation_euler = (Vector((0, 0, 1.5))-bpy.context.object.location).to_track_quat('-Z', 'Y').to_euler()
bpy.ops.object.camera_add(location=(8.6, -10.2, 7.1))
camera = bpy.context.object
camera.rotation_euler = (Vector((0, 0, 1.65))-camera.location).to_track_quat('-Z', 'Y').to_euler()
camera.data.type = 'ORTHO'
camera.data.ortho_scale = 9.4
scene = bpy.context.scene
scene.camera = camera
scene.render.engine = 'CYCLES'
scene.render.resolution_x = 1400
scene.render.resolution_y = 1100
scene.render.resolution_percentage = 100
