import bpy
import math
from mathutils import Vector

bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)

def material(name, color, metallic=0.0, roughness=0.4):
    m = bpy.data.materials.new(name)
    m.diffuse_color = (*color, 1)
    m.use_nodes = True
    bs = m.node_tree.nodes.get('Principled BSDF')
    bs.inputs['Base Color'].default_value = (*color, 1)
    bs.inputs['Metallic'].default_value = metallic
    bs.inputs['Roughness'].default_value = roughness
    return m

ivory = material('Warm enamel', (0.77, 0.82, 0.8))
teal = material('Cabinet teal', (0.06, 0.28, 0.32))
steel = material('Brushed steel', (0.48, 0.55, 0.58), 0.75)
black = material('Graphite rubber', (0.035, 0.045, 0.055))
stone = material('Epoxy work surface', (0.14, 0.18, 0.2))
blue = material('Display blue', (0.035, 0.42, 0.65), 0.15)
amber = material('Amber reagent bottles', (0.48, 0.2, 0.045))
white = material('Ceramic white', (0.92, 0.94, 0.9))
floor = material('Floor', (0.3, 0.34, 0.38))

def box(name, loc, dims, mat, bevel=0.025):
    bpy.ops.mesh.primitive_cube_add(size=1, location=loc)
    o = bpy.context.object
    o.name = name
    o.dimensions = dims
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    o.data.materials.append(mat)
    if bevel:
        mod = o.modifiers.new('Soft manufactured edges', 'BEVEL')
        mod.width = bevel
        mod.segments = 2
        o.modifiers.new('Weighted normals', 'WEIGHTED_NORMAL')
    return o

def cylinder(name, loc, radius, depth, mat, rotation=(0, 0, 0)):
    bpy.ops.mesh.primitive_cylinder_add(vertices=32, radius=radius, depth=depth, location=loc, rotation=rotation)
    o = bpy.context.object
    o.name = name
    o.data.materials.append(mat)
    mod = o.modifiers.new('Rim bevel', 'BEVEL')
    mod.width = 0.012
    mod.segments = 2
    o.modifiers.new('Weighted normals', 'WEIGHTED_NORMAL')
    return o

def rod(name, a, b, radius, mat):
    d = Vector(b) - Vector(a)
    o = cylinder(name, (Vector(a) + Vector(b)) / 2, radius, d.length, mat)
    o.rotation_euler = d.to_track_quat('Z', 'Y').to_euler()
    return o

box('Room floor', (0, 0, -0.09), (8, 6, 0.18), floor)
box('Service wall', (0, 1.15, 2), (6.4, 0.16, 4), ivory)
for x in (-1.95, 1.95):
    box('Recessed cabinet plinth', (x, 0, 0.14), (1.42, 1.14, 0.28), black)
    box('Base cabinet carcass', (x, 0, 0.94), (1.5, 1.32, 1.6), ivory)
    for z in (0.48, 1.02, 1.56):
        box('Drawer front', (x, -0.697, z), (1.42, 0.075, 0.48), teal)
        rod('Drawer steel pull', (x - 0.23, -0.79, z + 0.1), (x + 0.23, -0.79, z + 0.1), 0.025, steel)
box('Continuous laboratory countertop', (0, 0, 1.84), (5.8, 1.55, 0.16), stone)
box('Rear splashback', (0, 0.72, 2.04), (5.8, 0.09, 0.3), stone)
for x in (-1.95, 0, 1.95):
    box('Wall mounted storage cabinet', (x, 0.86, 3.18), (1.75, 0.5, 1.02), ivory)
    for dx in (-0.43, 0.43):
        box('Upper cabinet door', (x + dx, 0.577, 3.18), (0.84, 0.06, 0.95), teal)
        rod('Upper door handle', (x + dx * 0.35, 0.5, 3.03), (x + dx * 0.35, 0.5, 3.32), 0.018, steel)
box('Under cabinet task light', (0, 0.61, 2.65), (5.35, 0.12, 0.045), white)
# Benchtop analyzer with a sloped control face.
box('Analyzer housing', (-1.98, 0.06, 2.27), (1.1, 0.94, 0.7), ivory)
box('Analyzer dark fascia', (-1.98, -0.422, 2.29), (0.98, 0.04, 0.48), black)
box('Analyzer screen', (-2.17, -0.451, 2.34), (0.46, 0.015, 0.27), blue)
for z in (2.2, 2.35):
    cylinder('Analyzer control knob', (-1.65, -0.47, z), 0.055, 0.05, steel, (math.pi / 2, 0, 0))
for i in range(5):
    box('Analyzer ventilation slot', (-2.3 + i * 0.15, 0.06, 2.627), (0.075, 0.46, 0.015), black, 0.005)
# Microscope assembled from distinct mechanical parts.
box('Microscope foot', (-0.32, -0.08, 1.98), (0.63, 0.65, 0.12), ivory)
rod('Microscope upright', (-0.1, 0.18, 2.02), (-0.1, 0.18, 2.7), 0.085, ivory)
box('Specimen stage', (-0.32, -0.08, 2.3), (0.53, 0.48, 0.055), black)
box('Glass specimen slide', (-0.36, -0.1, 2.334), (0.24, 0.1, 0.012), blue, 0.002)
rod('Microscope head arm', (-0.1, 0.18, 2.68), (-0.35, -0.1, 2.72), 0.09, ivory)
cylinder('Objective barrel', (-0.35, -0.1, 2.54), 0.065, 0.2, steel)
rod('Angled eyepiece', (-0.35, -0.1, 2.72), (-0.35, -0.29, 2.96), 0.065, black)
cylinder('Focus adjustment wheel', (0.01, 0.18, 2.46), 0.12, 0.1, black, (0, math.pi / 2, 0))
box('Digital balance body', (0.77, -0.1, 2.01), (0.62, 0.64, 0.18), ivory)
cylinder('Balance weighing pan', (0.77, -0.04, 2.13), 0.23, 0.055, steel)
box('Balance readout', (0.77, -0.429, 2.03), (0.31, 0.012, 0.065), blue, 0.005)
box('Reagent tray', (1.91, 0.25, 1.955), (1.05, 0.6, 0.07), steel)
for i in range(3):
    x = 1.58 + i * 0.33
    cylinder('Reagent bottle', (x, 0.25, 2.17), 0.115, 0.36, amber)
    cylinder('Bottle screw cap', (x, 0.25, 2.385), 0.083, 0.07, black)
    box('Bottle label', (x, 0.134, 2.17), (0.14, 0.015, 0.14), white, 0.003)
cylinder('Stool seat', (0, -1.32, 1.03), 0.39, 0.13, black)
cylinder('Stool pedestal', (0, -1.32, 0.57), 0.065, 0.83, steel)
for i in range(5):
    a = i * math.tau / 5
    rod('Stool radial foot', (0, -1.32, 0.17), (0.47 * math.cos(a), -1.32 + 0.47 * math.sin(a), 0.1), 0.035, steel)

world = bpy.context.scene.world or bpy.data.worlds.new('Laboratory world')
bpy.context.scene.world = world
world.use_nodes = True
world.node_tree.nodes['Background'].inputs[0].default_value = (0.7, 0.78, 0.85, 1)
world.node_tree.nodes['Background'].inputs[1].default_value = 0.45
for name, loc, power, size in [('Key light', (1, -4, 7), 1500, 5), ('Fill light', (-4, -1, 5), 900, 4)]:
    bpy.ops.object.light_add(type='AREA', location=loc)
    o = bpy.context.object
    o.name = name
    o.data.energy = power
    o.data.shape = 'DISK'
    o.data.size = size
    o.rotation_euler = (Vector((0, 0, 1.7)) - o.location).to_track_quat('-Z', 'Y').to_euler()
bpy.ops.object.camera_add(location=(7.3, -10, 6.6))
cam = bpy.context.object
cam.name = 'Workstation overview'
cam.rotation_euler = (Vector((0, 0, 1.85)) - cam.location).to_track_quat('-Z', 'Y').to_euler()
cam.data.type = 'ORTHO'
cam.data.ortho_scale = 8.7
bpy.context.scene.camera = cam
bpy.context.scene.render.resolution_x = 1400
bpy.context.scene.render.resolution_y = 1000
bpy.context.scene.render.resolution_percentage = 100
