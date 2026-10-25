import bpy
import math
from mathutils import Vector

# Compact delivery van; the front points along +X.
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)

def material(name, color, metallic=0.0, roughness=0.45):
    m = bpy.data.materials.new(name)
    m.diffuse_color = (*color, 1)
    m.use_nodes = True
    bs = m.node_tree.nodes.get('Principled BSDF')
    bs.inputs['Base Color'].default_value = (*color, 1)
    bs.inputs['Metallic'].default_value = metallic
    bs.inputs['Roughness'].default_value = roughness
    return m

paint = material('Delivery blue enamel', (0.035, 0.30, 0.58), 0.35)
glass = material('Smoked blue glazing', (0.025, 0.075, 0.115), 0.35, 0.18)
rubber = material('Tire rubber', (0.022, 0.026, 0.030), 0, 0.8)
trim = material('Dark plastic trim', (0.055, 0.065, 0.075))
metal = material('Alloy wheels', (0.55, 0.60, 0.64), 0.75, 0.25)
white = material('Headlamp lenses and signage', (0.90, 0.95, 0.96), 0.15, 0.22)
red = material('Tail lamp lenses', (0.66, 0.025, 0.025), 0.1, 0.22)
ground = material('Warm concrete', (0.30, 0.32, 0.34), 0, 0.9)

def box(name, location, size, mat, bevel=0.04):
    bpy.ops.mesh.primitive_cube_add(size=1, location=location)
    obj = bpy.context.object
    obj.name = name
    obj.dimensions = size
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    obj.data.materials.append(mat)
    if bevel:
        mod = obj.modifiers.new('Soft manufactured edges', 'BEVEL')
        mod.width = bevel
        mod.segments = 3
        obj.modifiers.new('Weighted corner normals', 'WEIGHTED_NORMAL')
    return obj

def cylinder(name, location, radius, depth, mat):
    bpy.ops.mesh.primitive_cylinder_add(vertices=32, radius=radius, depth=depth,
                                      location=location, rotation=(math.pi / 2, 0, 0))
    obj = bpy.context.object
    obj.name = name
    obj.data.materials.append(mat)
    bevel = obj.modifiers.new('Rounded rim', 'BEVEL')
    bevel.width = 0.045
    bevel.segments = 3
    obj.modifiers.new('Weighted normals', 'WEIGHTED_NORMAL')
    return obj

box('Underbody chassis', (0, 0, 0.73), (4.8, 1.64, 0.24), trim)
box('Cargo body', (-0.78, 0, 1.89), (3.28, 1.90, 2.02), paint, 0.14)
box('Cab lower shell', (1.53, 0, 1.19), (1.50, 1.90, 0.69), paint, 0.10)
box('Cab upper shell', (1.36, 0, 2.07), (1.18, 1.88, 1.38), paint, 0.10)
box('Short engine bonnet', (2.06, 0, 1.56), (0.65, 1.87, 0.34), paint, 0.08)
box('Cab roof cap', (1.34, 0, 2.80), (1.35, 1.98, 0.14), paint, 0.07)
box('Front windshield gasket', (1.963, 0, 2.23), (0.025, 1.71, 0.88), trim)
box('Front windshield', (1.980, 0, 2.24), (0.020, 1.58, 0.74), glass)
for side, label in [(-1, 'Driver'), (1, 'Passenger')]:
    y = side * 0.962
    box(label + ' door seam', (1.32, y, 1.85), (1.12, 0.025, 1.63), trim, 0.035)
    box(label + ' door panel', (1.32, y + side * 0.018, 1.45), (1.05, 0.025, 0.77), paint)
    box(label + ' side window', (1.32, y + side * 0.022, 2.25), (0.94, 0.025, 0.70), glass)
    box(label + ' door handle', (0.95, side * 1.014, 1.83), (0.22, 0.06, 0.065), trim, 0.02)
    box(label + ' mirror stalk', (1.77, side * 1.08, 2.04), (0.09, 0.24, 0.065), trim)
    box(label + ' mirror housing', (1.79, side * 1.23, 2.11), (0.24, 0.14, 0.29), trim)
    box(label + ' cargo rub strip', (-0.83, side * 0.965, 1.25), (3.00, 0.045, 0.12), trim)
    box(label + ' sliding door rail', (-0.82, side * 0.966, 2.00), (2.78, 0.03, 0.035), metal, 0.008)
    box(label + ' sliding door seam', (-0.10, side * 0.959, 2.13), (0.022, 0.025, 1.35), trim, 0.004)
    box(label + ' delivery sign', (-1.04, side * 0.971, 2.38), (1.72, 0.025, 0.38), white)
    for x, axle in [(-1.62, 'Rear'), (1.57, 'Front')]:
        cylinder(label + ' ' + axle + ' tire', (x, side * 0.94, 0.61), 0.60, 0.36, rubber)
        cylinder(label + ' ' + axle + ' alloy rim', (x, side * 1.132, 0.61), 0.35, 0.045, metal)
        cylinder(label + ' ' + axle + ' hub', (x, side * 1.163, 0.61), 0.15, 0.055, trim)
box('Front bumper', (2.43, 0, 1.02), (0.19, 2.00, 0.27), trim)
box('Radiator grille', (2.405, 0, 1.39), (0.035, 0.90, 0.29), trim)
for y in [-0.69, 0.69]:
    box('Front headlamp', (2.409, y, 1.43), (0.035, 0.37, 0.23), white)
box('Rear bumper', (-2.47, 0, 0.97), (0.18, 2.00, 0.22), trim)
for y in [-0.45, 0.45]:
    box('Rear split cargo door', (-2.428, y, 1.96), (0.035, 0.86, 1.73), paint)
    box('Rear door glass', (-2.451, y, 2.38), (0.022, 0.70, 0.54), glass)
    box('Rear door handle', (-2.463, y * 0.33, 1.82), (0.06, 0.08, 0.23), trim)
for y in [-0.82, 0.82]:
    box('Vertical tail lamp', (-2.456, y, 1.46), (0.04, 0.15, 0.48), red)
box('Display ground', (0, 0, -0.08), (200, 200, 0.16), ground, 0)
bpy.ops.object.camera_add(location=(8, -9, 5.8))
camera = bpy.context.object
camera.name = 'Van three quarter camera'
camera.rotation_euler = (Vector((0, 0, 1.4)) - camera.location).to_track_quat('-Z', 'Y').to_euler()
camera.data.type = 'ORTHO'
camera.data.ortho_scale = 7.8
bpy.context.scene.camera = camera
for name, pos, power, size in [('Key softbox', (2, -4, 8), 1500, 5), ('Rear fill', (-4, 3, 6), 1000, 4)]:
    bpy.ops.object.light_add(type='AREA', location=pos)
    lamp = bpy.context.object
    lamp.name = name
    lamp.data.energy = power
    lamp.data.shape = 'DISK'
    lamp.data.size = size
    lamp.rotation_euler = (Vector((0, 0, 1)) - lamp.location).to_track_quat('-Z', 'Y').to_euler()
bpy.context.scene.world.color = (0.22, 0.22, 0.22)
