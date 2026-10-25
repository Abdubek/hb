import bpy
import math
from mathutils import Vector

# A small retail counter with stocked wall shelving.
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)

def material(name, color, metallic=0.0, roughness=0.45):
    m = bpy.data.materials.new(name)
    m.diffuse_color = (*color, 1)
    m.use_nodes = True
    bsdf = m.node_tree.nodes.get('Principled BSDF')
    bsdf.inputs['Base Color'].default_value = (*color, 1)
    bsdf.inputs['Metallic'].default_value = metallic
    bsdf.inputs['Roughness'].default_value = roughness
    return m

wood = material('Warm oak', (0.47, 0.24, 0.10))
cream = material('Ivory painted cabinetry', (0.84, 0.79, 0.66))
stone = material('Dark stone countertop', (0.065, 0.085, 0.085))
metal = material('Brushed brass', (0.56, 0.35, 0.12), 0.7)
black = material('Register casing', (0.025, 0.032, 0.035))
blue = material('Blue packaging', (0.055, 0.30, 0.43))
red = material('Terracotta packaging', (0.62, 0.16, 0.085))
green = material('Sage packaging', (0.25, 0.43, 0.25))
label = material('Paper labels', (0.94, 0.89, 0.74))
screen = material('Register display', (0.09, 0.52, 0.57))
floor = material('Floor', (0.27, 0.30, 0.30))

def box(name, location, size, mat, bevel=0.02):
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
        obj.modifiers.new('Weighted normals', 'WEIGHTED_NORMAL')
    return obj

def cylinder(name, location, radius, depth, mat):
    bpy.ops.mesh.primitive_cylinder_add(vertices=24, radius=radius, depth=depth, location=location)
    obj = bpy.context.object
    obj.name = name
    obj.data.materials.append(mat)
    mod = obj.modifiers.new('Rim bevel', 'BEVEL')
    mod.width = 0.009
    mod.segments = 2
    obj.modifiers.new('Weighted normals', 'WEIGHTED_NORMAL')
    return obj

def text(name, body, location, size, mat):
    curve = bpy.data.curves.new(name, 'FONT')
    curve.body = body
    curve.align_x = 'CENTER'
    curve.align_y = 'CENTER'
    curve.size = size
    curve.extrude = 0.001
    obj = bpy.data.objects.new(name, curve)
    bpy.context.collection.objects.link(obj)
    obj.location = location
    obj.rotation_euler = (math.pi / 2, 0, 0)
    curve.materials.append(mat)
    return obj

box('Shop floor platform', (0, 0.3, -0.10), (6.6, 4.8, 0.2), floor)
box('Rear feature wall', (0, 2.05, 1.75), (6.6, 0.16, 3.5), cream)
box('Counter plinth', (0, -0.75, 0.10), (4.25, 1.0, 0.2), black)
box('Counter cabinet', (0, -0.75, 0.67), (4.5, 1.15, 1.1), wood)
box('Countertop', (0, -0.75, 1.29), (4.8, 1.4, 0.14), stone)
for x in (-1.48, 0, 1.48):
    box('Recessed front panel', (x, -1.334, 0.69), (1.35, 0.035, 0.86), cream)
box('Counter brass accent', (0, -1.365, 0.25), (4.32, 0.018, 0.035), metal, 0.005)
text('Counter wordmark', 'THE DAILY GOODS', (0, -1.362, 0.77), 0.18, stone)

box('Shelf backing', (0, 1.88, 1.87), (4.9, 0.10, 2.68), wood)
for x in (-2.43, 0, 2.43):
    box('Shelf upright', (x, 1.57, 1.86), (0.09, 0.68, 2.72), wood)
for level, z in enumerate((0.53, 1.28, 2.03, 2.78)):
    box('Display shelf %d' % level, (0, 1.55, z), (4.95, 0.76, 0.09), wood)
    box('Shelf price rail %d' % level, (0, 1.156, z), (4.85, 0.026, 0.065), metal, 0.006)
    if level == 3:
        continue
    for i, x in enumerate((-2.04, -1.60, -1.16, -0.72, 0.48, 0.96, 1.44, 1.92)):
        base = z + 0.045
        mat = (blue, red, green)[(level + i) % 3]
        if i < 4:
            h = 0.40 + 0.04 * (i % 2)
            box('Packaged goods %d-%d' % (level, i), (x, 1.51, base + h/2), (0.31, 0.29, h), mat, 0.012)
            box('Carton label', (x, 1.358, base + h*0.55), (0.23, 0.012, 0.16), label, 0.003)
        else:
            cylinder('Product jar %d-%d' % (level, i), (x, 1.50, base + 0.18), 0.155, 0.36, mat)
            cylinder('Jar paper band', (x, 1.50, base + 0.18), 0.158, 0.12, label)
            cylinder('Jar lid', (x, 1.50, base + 0.38), 0.164, 0.055, metal)
text('Wall sign', 'PANTRY / HOME / EVERYDAY', (0, 1.947, 3.21), 0.20, stone)
box('Register foot', (1.55, -0.61, 1.405), (0.60, 0.43, 0.09), black)
box('Register stem', (1.55, -0.49, 1.60), (0.09, 0.10, 0.34), metal)
box('Register monitor', (1.55, -0.49, 1.86), (0.68, 0.09, 0.43), black)
box('Register screen', (1.55, -0.541, 1.86), (0.60, 0.012, 0.34), screen, 0.008)
box('Counter display tray', (-1.40, -0.72, 1.40), (0.95, 0.64, 0.08), wood)
for x in (-1.68, -1.40, -1.12):
    box('Counter impulse product', (x, -0.72, 1.56), (0.22, 0.36, 0.24), red)

bpy.ops.object.camera_add(location=(7.0, -9.5, 6.5))
camera = bpy.context.object
camera.name = 'Shop overview camera'
camera.rotation_euler = (Vector((0, 0.35, 1.45)) - camera.location).to_track_quat('-Z', 'Y').to_euler()
camera.data.type = 'ORTHO'
camera.data.ortho_scale = 8.9
bpy.context.scene.camera = camera
for location, power, size in (((1, -4, 7), 1300, 5), ((-4, 0, 5), 900, 4)):
    bpy.ops.object.light_add(type='AREA', location=location)
    lamp = bpy.context.object
    lamp.data.energy = power
    lamp.data.shape = 'DISK'
    lamp.data.size = size
    lamp.rotation_euler = (Vector((0, 0, 1)) - lamp.location).to_track_quat('-Z', 'Y').to_euler()
bpy.context.scene.world.color = (0.22, 0.22, 0.22)
bpy.context.scene.render.resolution_x = 1200
bpy.context.scene.render.resolution_y = 1000
bpy.context.scene.render.resolution_percentage = 100
