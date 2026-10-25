import bpy
import math
from mathutils import Vector

bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)

def material(name, color, metallic=0.0, roughness=0.4):
    m = bpy.data.materials.new(name)
    m.diffuse_color = (*color, 1)
    m.use_nodes = True
    p = m.node_tree.nodes.get('Principled BSDF')
    p.inputs['Base Color'].default_value = (*color, 1)
    p.inputs['Metallic'].default_value = metallic
    p.inputs['Roughness'].default_value = roughness
    return m

def box(name, loc, scale, mat, bevel=0.025):
    bpy.ops.mesh.primitive_cube_add(size=1, location=loc)
    o = bpy.context.object
    o.name = name
    o.dimensions = scale
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    o.data.materials.append(mat)
    if bevel:
        mod = o.modifiers.new('Rounded manufactured edges', 'BEVEL')
        mod.width = bevel
        mod.segments = 3
        o.modifiers.new('Weighted corner normals', 'WEIGHTED_NORMAL')
    return o

def cylinder(name, loc, radius, depth, mat):
    bpy.ops.mesh.primitive_cylinder_add(vertices=24, radius=radius, depth=depth, location=loc)
    o = bpy.context.object
    o.name = name
    o.data.materials.append(mat)
    mod = o.modifiers.new('Rolled rim edges', 'BEVEL')
    mod.width = 0.008
    mod.segments = 2
    o.modifiers.new('Weighted normals', 'WEIGHTED_NORMAL')
    return o

def label(name, body, loc, size, mat):
    bpy.ops.object.text_add(location=loc, rotation=(math.pi / 2, 0, 0))
    o = bpy.context.object
    o.name = name
    o.data.body = body
    o.data.align_x = 'CENTER'
    o.data.align_y = 'CENTER'
    o.data.size = size
    o.data.extrude = 0.001
    o.data.materials.append(mat)
    return o

blue = material('Enamel midnight blue', (0.025, 0.10, 0.21), 0.35)
dark = material('Charcoal recesses', (0.016, 0.022, 0.030))
metal = material('Brushed aluminum', (0.48, 0.54, 0.59), 0.8)
white = material('Warm white lettering', (0.88, 0.93, 0.93))
cyan = material('Display cyan', (0.10, 0.85, 0.72))
red = material('Cherry cans', (0.75, 0.045, 0.055), 0.25)
yellow = material('Citrus cans', (0.95, 0.62, 0.055), 0.25)
green = material('Lime cans', (0.10, 0.48, 0.22), 0.25)
floor = material('Studio floor', (0.20, 0.23, 0.27))

# Front is negative Y. The open display recess keeps every product visible.
box('Rear body shell', (0, 0.36, 1.65), (2.1, 0.70, 3.1), blue)
box('Dark product bay back', (-0.28, -0.005, 1.89), (1.40, 0.04, 2.05), dark)
box('Left cabinet pillar', (-0.99, -0.28, 1.65), (0.16, 0.65, 3.1), blue)
box('Right cabinet pillar', (0.99, -0.28, 1.65), (0.16, 0.65, 3.1), blue)
box('Top illuminated sign housing', (0, -0.30, 3.02), (1.91, 0.62, 0.34), blue)
label('Brand', 'REFRESH', (0, -0.622, 3.03), 0.22, white)
box('Control column', (0.69, -0.30, 1.80), (0.46, 0.62, 2.10), dark)
box('Display left trim', (-0.89, -0.58, 1.86), (0.045, 0.045, 2.00), metal)
box('Display right trim', (0.425, -0.58, 1.86), (0.045, 0.045, 2.00), metal)

for row in range(3):
    z = 1.04 + row * 0.59
    box('Shelf %d' % (row + 1), (-0.24, -0.29, z), (1.28, 0.54, 0.055), metal)
    box('Shelf price rail %d' % row, (-0.24, -0.57, z + 0.005), (1.28, 0.045, 0.09), blue)
    for col in range(4):
        x = -0.72 + col * 0.32
        mat = [red, yellow, green][row]
        cylinder('Product can %d-%d' % (row, col), (x, -0.30, z + 0.235), 0.105, 0.40, mat)
        cylinder('Can lid %d-%d' % (row, col), (x, -0.30, z + 0.442), 0.102, 0.013, metal)
        box('Can label %d-%d' % (row, col), (x, -0.400, z + 0.23), (0.12, 0.012, 0.14), white, 0.008)
        label('Selection code %d-%d' % (row, col), '%s%d' % ('ABC'[row], col + 1), (x, -0.601, z), 0.052, white)

box('LCD bezel', (0.69, -0.626, 2.52), (0.37, 0.045, 0.24), metal)
box('LCD face', (0.69, -0.654, 2.52), (0.32, 0.015, 0.18), dark)
label('LCD message', '$ 1.50', (0.69, -0.668, 2.52), 0.079, cyan)
for row in range(4):
    for col in range(3):
        x, z = 0.57 + col * 0.12, 2.19 - row * 0.14
        box('Keypad key %d-%d' % (row, col), (x, -0.641, z), (0.093, 0.05, 0.10), metal, 0.012)
        label('Key legend %d-%d' % (row, col), '123456789*0#'[row * 3 + col], (x, -0.671, z), 0.064, dark)
box('Coin slot surround', (0.69, -0.63, 1.48), (0.30, 0.045, 0.15), metal)
box('Coin insertion slot', (0.69, -0.658, 1.48), (0.19, 0.01, 0.025), dark, 0.005)
box('Lower front panel', (0, -0.30, 0.57), (1.90, 0.62, 0.82), blue)
box('Pickup opening trim', (-0.22, -0.633, 0.56), (1.36, 0.055, 0.46), metal)
box('Pickup dark flap', (-0.22, -0.669, 0.56), (1.23, 0.035, 0.34), dark)
label('Pickup instruction', 'PUSH TO COLLECT', (-0.22, -0.692, 0.56), 0.088, white)
for x in (-0.78, 0.78):
    for y in (-0.36, 0.42):
        box('Leveling foot', (x, y, 0.10), (0.20, 0.22, 0.20), dark)
box('Ground', (0, 0, -0.055), (200, 200, 0.1), floor, 0)
bpy.ops.object.camera_add(location=(4.2, -6.5, 3.8))
camera = bpy.context.object
camera.name = 'Vending machine camera'
camera.rotation_euler = (Vector((0, 0, 1.6)) - camera.location).to_track_quat('-Z', 'Y').to_euler()
camera.data.type = 'ORTHO'
camera.data.ortho_scale = 4.5
bpy.context.scene.camera = camera
bpy.ops.object.light_add(type='AREA', location=(1, -4, 6))
bpy.context.object.data.energy = 1000
bpy.context.object.data.shape = 'DISK'
bpy.context.object.data.size = 5
bpy.context.scene.world.color = (0.25, 0.25, 0.25)
