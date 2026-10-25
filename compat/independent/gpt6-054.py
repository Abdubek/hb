import bpy
import math
from mathutils import Vector

bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)

def material(name, color, metal=0.0, roughness=0.4):
    m = bpy.data.materials.new(name)
    m.diffuse_color = (*color, 1)
    m.use_nodes = True
    bs = m.node_tree.nodes.get('Principled BSDF')
    bs.inputs['Base Color'].default_value = (*color, 1)
    bs.inputs['Metallic'].default_value = metal
    bs.inputs['Roughness'].default_value = roughness
    return m

gold = material('Gold thermal blanket', (0.66, 0.39, 0.075), 0.72, 0.32)
silver = material('Aluminum structure', (0.57, 0.64, 0.72), 0.8, 0.28)
blue = material('Photovoltaic blue', (0.015, 0.055, 0.23), 0.5, 0.24)
blue2 = material('Alternate photovoltaic blue', (0.025, 0.095, 0.32), 0.5, 0.24)
dark = material('Graphite hardware', (0.04, 0.05, 0.065), 0.45)
white = material('Antenna ceramic coating', (0.8, 0.84, 0.88), 0.35)

 def_placeholder = None

def box(name, loc, dims, mat, bevel=0.025):
    bpy.ops.mesh.primitive_cube_add(size=1, location=loc)
    o = bpy.context.object
    o.name = name
    o.dimensions = dims
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    o.data.materials.append(mat)
    if bevel:
        mod = o.modifiers.new('Edge bevel', 'BEVEL')
        mod.width = bevel
        mod.segments = 2
        o.modifiers.new('Weighted normals', 'WEIGHTED_NORMAL')
    return o

def cylinder(name, loc, radius, depth, mat):
    bpy.ops.mesh.primitive_cylinder_add(vertices=32, radius=radius, depth=depth, location=loc)
    o = bpy.context.object
    o.name = name
    o.data.materials.append(mat)
    mod = o.modifiers.new('Machined edge', 'BEVEL')
    mod.width = 0.015
    mod.segments = 2
    o.modifiers.new('Weighted normals', 'WEIGHTED_NORMAL')
    return o

def rod(name, a, b, radius, mat):
    d = Vector(b) - Vector(a)
    o = cylinder(name, (Vector(a) + Vector(b)) / 2, radius, d.length, mat)
    o.rotation_euler = d.to_track_quat('Z', 'Y').to_euler()
    return o

box('Satellite insulated bus', (0, 0, 0), (1.9, 1.65, 2.05), gold, 0.08)
for z in (-1.05, 1.05):
    box('Structural end deck', (0, 0, z), (2.05, 1.8, 0.12), silver)
for x in (-0.96, 0.96):
    for y in (-0.83, 0.83):
        box('Corner rail', (x, y, 0), (0.08, 0.08, 2.03), silver, 0.012)
box('Front equipment panel', (0, -0.845, 0.12), (1.42, 0.065, 1.3), dark)
for x in (-0.43, 0.43):
    box('Avionics enclosure', (x, -0.94, 0.2), (0.58, 0.18, 0.73), silver)
    for z in (-0.02, 0.12, 0.26, 0.4):
        box('Avionics cooling rib', (x, -1.043, z), (0.5, 0.04, 0.035), dark, 0.005)
# Two articulated solar wings, each divided into two framed modules.
for side in (-1, 1):
    label = 'Port' if side < 0 else 'Starboard'
    rod(label + ' deployment boom', (side * 0.96, 0, 0.3), (side * 1.78, 0, 0.3), 0.075, silver)
    cylinder(label + ' root hinge', (side * 1.48, 0, 0.3), 0.16, 0.36, dark)
    for module in range(2):
        x = side * (2.7 + module * 1.94)
        box(label + ' solar module backing', (x, 0, 0.3), (1.86, 2.8, 0.09), dark, 0.01)
        for dx in (-0.94, 0.94):
            box(label + ' longitudinal frame', (x + dx, 0, 0.34), (0.055, 2.87, 0.11), silver, 0.009)
        for y in (-1.42, 1.42):
            box(label + ' end frame', (x, y, 0.34), (1.93, 0.055, 0.11), silver, 0.009)
        for col in range(4):
            for row in range(8):
                cx = x - 0.675 + col * 0.45
                cy = -1.2075 + row * 0.345
                box(label + ' solar cell %d-%d-%d' % (module, col, row), (cx, cy, 0.357), (0.425, 0.32, 0.012), blue if (col + row) % 2 else blue2, 0)
                box('Cell silver busbar', (cx, cy, 0.365), (0.012, 0.3, 0.004), silver, 0)
    rod(label + ' interpanel hinge', (side * 3.67, -0.55, 0.29), (side * 3.67, 0.55, 0.29), 0.055, silver)
# Parabolic dish opens toward its local +Z axis.
mount = Vector((0, 0, 1.58))
axis = Vector((0, -0.48, 0.88)).normalized()
q = Vector((0, 0, 1)).rotation_difference(axis)
def dish_point(p):
    return mount + q @ Vector(p)
rod('Dish pedestal', (0, 0, 1.1), mount, 0.16, silver)
verts = [(0, 0, 0)]
faces = []
segments, rings, radius = 64, 12, 1.08
for ring in range(1, rings + 1):
    r = radius * ring / rings
    for j in range(segments):
        a = j * math.tau / segments
        verts.append((r * math.cos(a), r * math.sin(a), 0.36 * (r / radius) ** 2))
for j in range(segments):
    faces.append((0, 1 + j, 1 + (j + 1) % segments))
for ring in range(rings - 1):
    a = 1 + ring * segments
    b = a + segments
    for j in range(segments):
        k = (j + 1) % segments
        faces.append((a + j, b + j, b + k, a + k))
mesh = bpy.data.meshes.new('Parabolic reflector mesh')
mesh.from_pydata(verts, [], faces)
mesh.update()
dish = bpy.data.objects.new('High gain parabolic antenna', mesh)
bpy.context.collection.objects.link(dish)
dish.location = mount
dish.rotation_mode = 'QUATERNION'
dish.rotation_quaternion = q
dish.data.materials.append(white)
for poly in mesh.polygons:
    poly.use_smooth = True
solid = dish.modifiers.new('Reflector shell thickness', 'SOLIDIFY')
solid.thickness = 0.025
bpy.ops.mesh.primitive_torus_add(major_segments=64, minor_segments=8, major_radius=radius, minor_radius=0.025, location=dish_point((0, 0, 0.36)))
rim = bpy.context.object
rim.name = 'Reflector reinforced rim'
rim.rotation_mode = 'QUATERNION'
rim.rotation_quaternion = q
rim.data.materials.append(silver)
for i in range(3):
    a = i * math.tau / 3
    rod('Feed support strut', dish_point((radius * math.cos(a), radius * math.sin(a), 0.36)), dish_point((0, 0, 0.88)), 0.018, silver)
rod('Antenna feed horn', dish_point((0, 0, 0.72)), dish_point((0, 0, 0.95)), 0.08, gold)
rod('Telemetry whip mast', (0.75, 0.64, 1.1), (0.75, 0.64, 2.62), 0.018, silver)
cylinder('Whip mounting socket', (0.75, 0.64, 1.18), 0.09, 0.15, dark)
cylinder('Propulsion mounting ring', (0, 0, -1.19), 0.45, 0.2, silver)
bpy.ops.mesh.primitive_cone_add(vertices=32, radius1=0.4, radius2=0.19, depth=0.46, end_fill_type='NOTHING', location=(0, 0, -1.5))
nozzle = bpy.context.object
nozzle.name = 'Open main engine nozzle'
nozzle.data.materials.append(dark)
nozzle.modifiers.new('Nozzle wall', 'SOLIDIFY').thickness = 0.025

scene = bpy.context.scene
scene.world = bpy.data.worlds.new('Deep space studio')
scene.world.use_nodes = True
scene.world.node_tree.nodes['Background'].inputs[0].default_value = (0.025, 0.035, 0.065, 1)
scene.world.node_tree.nodes['Background'].inputs[1].default_value = 0.35
for name, loc, power, size in [('Sunward softbox', (1, -5, 8), 1900, 6), ('Earth fill', (-5, 1, 4), 1400, 5), ('Rim light', (3, 5, 5), 1700, 4)]:
    bpy.ops.object.light_add(type='AREA', location=loc)
    lamp = bpy.context.object
    lamp.name = name
    lamp.data.energy = power
    lamp.data.size = size
    lamp.rotation_euler = (Vector((0, 0, 0.4)) - lamp.location).to_track_quat('-Z', 'Y').to_euler()
bpy.ops.object.camera_add(location=(8, -13, 10))
cam = bpy.context.object
cam.name = 'Satellite overview camera'
cam.rotation_euler = (Vector((0, 0, 0.5)) - cam.location).to_track_quat('-Z', 'Y').to_euler()
cam.data.type = 'ORTHO'
cam.data.ortho_scale = 13
scene.camera = cam
scene.render.resolution_x = 1500
scene.render.resolution_y = 1000
scene.render.resolution_percentage = 100
