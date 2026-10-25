import bpy
import math
from mathutils import Vector

# Compact counterbalanced forklift; front and forks point toward negative X.
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)

def material(name, color, metallic=0.0, roughness=0.45):
    mat = bpy.data.materials.new(name)
    mat.diffuse_color = (*color, 1)
    mat.use_nodes = True
    bsdf = mat.node_tree.nodes.get('Principled BSDF')
    bsdf.inputs['Base Color'].default_value = (*color, 1)
    bsdf.inputs['Metallic'].default_value = metallic
    bsdf.inputs['Roughness'].default_value = roughness
    return mat

yellow = material('Safety yellow paint', (0.95, 0.55, 0.025), 0.35)
steel = material('Charcoal structural steel', (0.075, 0.09, 0.11), 0.7)
chrome = material('Hydraulic polished steel', (0.62, 0.68, 0.72), 0.85, 0.22)
rubber = material('Solid rubber tires', (0.023, 0.027, 0.032), 0, 0.8)
seat_mat = material('Black vinyl upholstery', (0.045, 0.052, 0.06), 0, 0.65)
hub_mat = material('Wheel hub paint', (0.47, 0.49, 0.5), 0.6)
white = material('Headlamp lenses', (0.86, 0.94, 1.0), 0.15)
red = material('Rear red lenses', (0.65, 0.025, 0.015))
amber = material('Amber beacon lens', (1.0, 0.27, 0.01))
floor_mat = material('Concrete display floor', (0.3, 0.32, 0.34))

def box(name, location, size, mat, bevel=0.025):
    bpy.ops.mesh.primitive_cube_add(size=1, location=location)
    obj = bpy.context.object
    obj.name = name
    obj.dimensions = size
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    obj.data.materials.append(mat)
    if bevel:
        mod = obj.modifiers.new('Rounded manufactured edges', 'BEVEL')
        mod.width = bevel
        mod.segments = 3
        obj.modifiers.new('Weighted normals', 'WEIGHTED_NORMAL')
    return obj

def cylinder(name, location, radius, depth, mat, rotation=(0, 0, 0)):
    bpy.ops.mesh.primitive_cylinder_add(vertices=32, radius=radius, depth=depth, location=location, rotation=rotation)
    obj = bpy.context.object
    obj.name = name
    obj.data.materials.append(mat)
    mod = obj.modifiers.new('Edge radius', 'BEVEL')
    mod.width = 0.015
    mod.segments = 2
    obj.modifiers.new('Weighted normals', 'WEIGHTED_NORMAL')
    return obj

def rod(name, a, b, radius, mat):
    a, b = Vector(a), Vector(b)
    obj = cylinder(name, (a + b) / 2, radius, (b - a).length, mat)
    obj.rotation_euler = (b - a).to_track_quat('Z', 'Y').to_euler()
    return obj

box('Concrete ground', (-0.6, 0, -0.09), (7.5, 5.5, 0.18), floor_mat)
box('Lower chassis', (0, 0, 0.51), (2.18, 1.05, 0.27), steel, 0.08)
box('Rear rounded counterweight', (0.86, 0, 0.94), (0.8, 1.22, 0.94), yellow, 0.17)
box('Rear bumper', (1.29, 0, 0.52), (0.16, 1.23, 0.2), steel, 0.06)
box('Operator floor plate', (-0.24, 0, 0.72), (1.24, 1.07, 0.11), steel)
box('Seat pedestal battery enclosure', (0.34, 0, 0.94), (0.77, 0.89, 0.45), yellow, 0.07)
for side in (-1, 1):
    y = side * 0.66
    for x, radius, z in ((-0.72, 0.43, 0.43), (0.83, 0.32, 0.32)):
        cylinder('Solid tire', (x, y, z), radius, 0.27, rubber, (math.pi / 2, 0, 0))
        cylinder('Recessed wheel hub', (x, y + side * 0.146, z), radius * 0.53, 0.035, hub_mat, (math.pi / 2, 0, 0))
        cylinder('Axle cap', (x, y + side * 0.17, z), radius * 0.19, 0.055, steel, (math.pi / 2, 0, 0))
    box('Front wheel fender', (-0.72, side * 0.58, 0.91), (0.97, 0.35, 0.11), yellow, 0.045)
    box('Operator access step', (-0.08, side * 0.66, 0.48), (0.5, 0.29, 0.08), steel)
    for x in (-0.64, 0.83):
        box('Overhead guard upright', (x, side * 0.51, 1.72), (0.065, 0.065, 1.8), steel, 0.012)
    box('Overhead guard side rail', (0.09, side * 0.53, 2.64), (1.64, 0.10, 0.11), yellow)
    box('Rear tail light', (1.267, side * 0.39, 1.11), (0.025, 0.19, 0.12), red, 0.012)
for x in (-0.69, -0.29, 0.11, 0.51, 0.9):
    box('Overhead protective crossbar', (x, 0, 2.64), (0.075, 1.08, 0.075), steel, 0.012)
box('Seat cushion', (0.19, 0, 1.22), (0.62, 0.66, 0.16), seat_mat, 0.07)
back = box('Seat backrest', (0.49, 0, 1.54), (0.14, 0.66, 0.61), seat_mat, 0.07)
back.rotation_euler.y = -0.12
rod('Steering column', (-0.49, 0, 0.8), (-0.38, 0, 1.53), 0.035, steel)
bpy.ops.mesh.primitive_torus_add(major_radius=0.19, minor_radius=0.025, major_segments=32, minor_segments=8, location=(-0.38, 0, 1.53))
bpy.context.object.name = 'Steering wheel rim'
bpy.context.object.data.materials.append(rubber)
for angle in (0, 2.094, 4.189):
    rod('Steering wheel spoke', (-0.38, 0, 1.53), (-0.38 + 0.18 * math.cos(angle), 0.18 * math.sin(angle), 1.53), 0.012, steel)
box('Instrument console', (-0.65, 0, 1.21), (0.17, 0.63, 0.3), steel)
for y in (0.28, 0.39):
    rod('Lift control lever', (-0.25, y, 0.88), (-0.32, y, 1.32), 0.016, chrome)
    cylinder('Control knob', (-0.32, y, 1.33), 0.038, 0.065, rubber)
for y in (-0.43, 0.43):
    box('Outer mast rail', (-1.13, y, 1.6), (0.16, 0.14, 2.62), steel)
    box('Inner sliding mast rail', (-1.24, y * 0.77, 1.57), (0.10, 0.085, 2.38), chrome, 0.012)
for z in (0.36, 2.87):
    box('Mast cross tie', (-1.13, 0, z), (0.18, 0.99, 0.14), steel)
rod('Lift cylinder barrel', (-1.08, 0, 0.42), (-1.08, 0, 1.5), 0.075, steel)
rod('Lift piston', (-1.08, 0, 1.5), (-1.08, 0, 2.69), 0.039, chrome)
for z in (0.52, 0.88):
    box('Fork carriage crossbar', (-1.37, 0, z), (0.15, 1.09, 0.14), steel)
for y in (-0.34, 0.34):
    box('Fork vertical heel', (-1.49, y, 0.63), (0.10, 0.15, 0.83), steel, 0.012)
    box('Long lifting fork', (-2.1, y, 0.255), (1.32, 0.15, 0.09), steel, 0.018)
for y in (-0.49, 0.49):
    box('Headlamp housing', (-0.71, y, 2.32), (0.13, 0.18, 0.15), steel)
    box('Headlamp lens', (-0.78, y, 2.32), (0.015, 0.14, 0.11), white, 0.01)
cylinder('Beacon base', (0.65, 0.35, 2.73), 0.105, 0.08, steel)
cylinder('Amber safety beacon', (0.65, 0.35, 2.84), 0.085, 0.17, amber)

scene = bpy.context.scene
scene.world = scene.world or bpy.data.worlds.new('Studio world')
scene.world.use_nodes = True
scene.world.node_tree.nodes['Background'].inputs[1].default_value = 0.45
bpy.ops.object.light_add(type='AREA', location=(-3, -4, 7))
bpy.context.object.name = 'Large softbox'
bpy.context.object.data.energy = 1300
bpy.context.object.data.size = 5
bpy.ops.object.camera_add(location=(-6.2, -7, 4.6))
camera = bpy.context.object
camera.name = 'Forklift three-quarter camera'
camera.rotation_euler = (Vector((-0.6, 0, 1.25)) - camera.location).to_track_quat('-Z', 'Y').to_euler()
camera.data.type = 'ORTHO'
camera.data.ortho_scale = 5.5
scene.camera = camera
scene.render.resolution_x = 1400
scene.render.resolution_y = 1100
scene.render.resolution_percentage = 100
