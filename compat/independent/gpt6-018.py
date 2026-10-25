import bpy
import math
from mathutils import Vector

# Open aluminum laptop with individually modeled keys and screen graphics.
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)

def material(name, color, metallic=0.0, roughness=0.4, emission=0.0):
    m = bpy.data.materials.new(name)
    m.diffuse_color = (*color, 1)
    m.use_nodes = True
    shader = m.node_tree.nodes.get('Principled BSDF')
    shader.inputs['Base Color'].default_value = (*color, 1)
    shader.inputs['Metallic'].default_value = metallic
    shader.inputs['Roughness'].default_value = roughness
    if emission:
        shader.inputs['Emission Color'].default_value = (*color, 1)
        shader.inputs['Emission Strength'].default_value = emission
    return m

silver = material('Anodized aluminum', (0.47, 0.51, 0.56), 0.78, 0.29)
edge = material('Polished trackpad border', (0.69, 0.73, 0.78), 0.8, 0.23)
black = material('Keyboard and bezel', (0.018, 0.023, 0.030))
keymat = material('Keycaps', (0.045, 0.055, 0.065))
white = material('Key legends', (0.79, 0.83, 0.86))
glass = material('Display background', (0.016, 0.065, 0.13), roughness=0.24, emission=0.25)
cyan = material('Display cyan', (0.05, 0.60, 0.76), emission=0.35)
panel = material('Display window', (0.12, 0.22, 0.32), emission=0.2)
pad = material('Trackpad surface', (0.38, 0.42, 0.47), 0.55)
floor = material('Studio surface', (0.16, 0.19, 0.23))

def box(name, location, size, mat, bevel=0.015, parent=None):
    bpy.ops.mesh.primitive_cube_add(size=1)
    obj = bpy.context.object
    obj.name = name
    obj.dimensions = size
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    obj.data.materials.append(mat)
    if bevel:
        mod = obj.modifiers.new('Rounded edges', 'BEVEL')
        mod.width = bevel
        mod.segments = 3
        obj.modifiers.new('Weighted normals', 'WEIGHTED_NORMAL')
    if parent is not None:
        obj.parent = parent
    obj.location = location
    return obj

def legend(body, location, size=0.041):
    curve = bpy.data.curves.new('Legend ' + body, 'FONT')
    curve.body = body
    curve.align_x = 'CENTER'
    curve.align_y = 'CENTER'
    curve.size = size
    obj = bpy.data.objects.new('Key legend ' + body, curve)
    bpy.context.collection.objects.link(obj)
    obj.location = location
    curve.materials.append(white)

box('Laptop lower shell', (0, 0, 0.13), (3.25, 2.18, 0.20), silver, 0.075)
box('Lower shell seam', (0, 0, 0.061), (3.17, 2.10, 0.012), black, 0.005)
box('Keyboard recessed well', (0, 0.28, 0.234), (2.65, 1.13, 0.018), black, 0.035)
for row, characters in enumerate(('1234567890-=', 'QWERTYUIOP[]', 'ASDFGHJKL;\'', 'ZXCVBNM,./')):
    y = 0.70 - row * 0.205
    offset = (0, 0.035, 0.075, 0.15)[row]
    for col, character in enumerate(characters):
        x = -1.16 + offset + col * 0.208
        box('Key ' + character, (x, y, 0.262), (0.182, 0.174, 0.041), keymat, 0.016)
        legend(character, (x, y, 0.284))
# Bottom modifier row and wide spacebar.
for name, x, width in (('Ctrl', -1.14, 0.23), ('Alt', -0.86, 0.23), ('Space', -0.03, 1.33), ('Alt', 0.82, 0.23), ('Left', 1.06, 0.19), ('Right', 1.28, 0.19)):
    box('Key ' + name, (x, -0.12, 0.262), (width, 0.17, 0.041), keymat, 0.014)
    if name != 'Space':
        legend(name, (x, -0.12, 0.284), 0.028)
box('Trackpad metallic outline', (0, -0.66, 0.238), (1.23, 0.66, 0.015), edge, 0.04)
box('Trackpad', (0, -0.66, 0.247), (1.19, 0.62, 0.012), pad, 0.035)
for side in (-1, 1):
    for i in range(12):
        box('Speaker grille slot', (side * 1.46, -0.04 + i * 0.064, 0.234), (0.10, 0.016, 0.006), black, 0.003)
    box('USB-C port recess', (side * 1.626, 0.50, 0.14), (0.009, 0.19, 0.056), black, 0.012)
    box('USB-C inner tongue', (side * 1.632, 0.50, 0.14), (0.005, 0.12, 0.014), pad, 0.003)
for x in (-1.10, 1.10):
    bpy.ops.mesh.primitive_cylinder_add(vertices=32, radius=0.09, depth=0.49, location=(x, 0.97, 0.25), rotation=(0, math.pi/2, 0))
    bpy.context.object.name = 'Display hinge barrel'
    bpy.context.object.data.materials.append(silver)

hinge = bpy.data.objects.new('Display assembly - 105 degree opening', None)
bpy.context.collection.objects.link(hinge)
hinge.location = (0, 0.97, 0.26)
hinge.rotation_euler.x = math.radians(-15)
box('Display aluminum lid', (0, 0.018, 1.00), (3.25, 0.105, 2.00), silver, 0.06, hinge)
box('Black screen bezel', (0, -0.043, 1.00), (3.13, 0.023, 1.88), black, 0.035, hinge)
box('Active display', (0, -0.059, 1.02), (2.92, 0.012, 1.65), glass, 0.008, hinge)
box('Desktop application window', (0.16, -0.069, 1.09), (2.14, 0.006, 1.21), panel, 0.025, hinge)
box('Application toolbar', (0.16, -0.074, 1.59), (2.04, 0.005, 0.12), cyan, 0.008, hinge)
box('Application sidebar', (-0.62, -0.075, 1.06), (0.42, 0.006, 0.84), glass, 0.008, hinge)
for i, width in enumerate((1.12, 0.93, 1.22, 0.75)):
    box('Screen content line', (0.34, -0.075, 1.34-i*0.13), (width, 0.006, 0.032), white, 0.006, hinge)
for i in range(5):
    box('Dock icon', (-0.44+i*0.22, -0.074, 0.29), (0.14, 0.007, 0.12), cyan if i % 2 else white, 0.02, hinge)
box('Webcam housing', (0, -0.060, 1.921), (0.072, 0.012, 0.035), pad, 0.01, hinge)
box('Webcam lens', (0, -0.068, 1.921), (0.023, 0.006, 0.023), glass, 0.009, hinge)
box('Studio tabletop', (0, 0, -0.055), (12, 12, 0.10), floor, 0.02)

bpy.ops.object.camera_add(location=(4.1, -5.5, 4.0))
camera = bpy.context.object
camera.name = 'Laptop three-quarter camera'
camera.rotation_euler = (Vector((0, 0.25, 0.86)) - camera.location).to_track_quat('-Z', 'Y').to_euler()
camera.data.type = 'ORTHO'
camera.data.ortho_scale = 5.3
bpy.context.scene.camera = camera
for location, power, size in (((-3, -4, 6), 950, 4), ((4, 2, 5), 1100, 3)):
    bpy.ops.object.light_add(type='AREA', location=location)
    light = bpy.context.object
    light.data.energy = power
    light.data.size = size
    light.rotation_euler = (Vector((0, 0, 0.7)) - light.location).to_track_quat('-Z', 'Y').to_euler()
bpy.context.scene.world.color = (0.20, 0.20, 0.20)
bpy.context.scene.render.resolution_x = 1200
bpy.context.scene.render.resolution_y = 1000
bpy.context.scene.render.resolution_percentage = 100
