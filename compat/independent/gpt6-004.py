import bpy
from mathutils import Vector
from math import pi

bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)

def material(name, rgb, metal=0, rough=0.4, emission=0):
    m = bpy.data.materials.new(name)
    m.diffuse_color = (*rgb, 1)
    m.use_nodes = True
    bs = m.node_tree.nodes.get('Principled BSDF')
    bs.inputs['Base Color'].default_value = (*rgb, 1)
    bs.inputs['Metallic'].default_value = metal
    bs.inputs['Roughness'].default_value = rough
    if emission:
        bs.inputs['Emission Color'].default_value = (*rgb, 1)
        bs.inputs['Emission Strength'].default_value = emission
    return m

def box(name, pos, size, mat, bevel=0.02):
    bpy.ops.mesh.primitive_cube_add(size=1, location=pos)
    ob = bpy.context.object
    ob.name = name
    ob.dimensions = size
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    ob.data.materials.append(mat)
    if bevel:
        mod = ob.modifiers.new('Molded radii', 'BEVEL')
        mod.width = bevel
        mod.segments = 5
        ob.modifiers.new('Weighted normals', 'WEIGHTED_NORMAL')
    return ob

def button(name, x, y, z, radius, depth, mat):
    bpy.ops.mesh.primitive_cylinder_add(vertices=32, radius=radius, depth=depth, location=(x, y, z))
    ob = bpy.context.object
    ob.name = name
    ob.data.materials.append(mat)
    mod = ob.modifiers.new('Button edge radius', 'BEVEL')
    mod.width = 0.008
    mod.segments = 3
    ob.modifiers.new('Weighted normals', 'WEIGHTED_NORMAL')
    return ob

shell = material('Indigo polymer', (0.15, 0.19, 0.38))
back = material('Lower shell', (0.085, 0.10, 0.20))
black = material('Soft black controls', (0.018, 0.023, 0.035), rough=0.6)
bezel = material('Screen bezel', (0.035, 0.045, 0.07), rough=0.25)
screen = material('Display deep teal', (0.018, 0.12, 0.16), rough=0.18, emission=0.25)
cyan = material('Display cyan', (0.15, 0.78, 0.75), emission=0.8)
pink = material('Coral action buttons', (0.86, 0.20, 0.27))
white = material('Control legends', (0.78, 0.84, 0.86))
floor = material('Studio surface', (0.28, 0.31, 0.37), rough=0.8)

# Console lies face-up; dimensions are in a convenient product display scale.
box('Rear enclosure', (0, 0, 0.125), (2.30, 1.03, 0.20), back, 0.095)
box('Perimeter assembly seam', (0, 0, 0.213), (2.285, 1.015, 0.035), black, 0.017)
box('Front enclosure', (0, 0, 0.29), (2.30, 1.03, 0.15), shell, 0.073)
box('Raised screen surround', (0, 0.035, 0.369), (1.27, 0.82, 0.045), bezel, 0.022)
box('Display glass', (0, 0.035, 0.395), (1.13, 0.68, 0.012), screen, 0.005)

# A simple geometric game image made entirely from shallow meshes.
box('Game horizon', (0, -0.115, 0.404), (1.02, 0.015, 0.004), cyan, 0)
for i in range(5):
    box('Game platform '+str(i), (-0.43+i*0.205, -0.24, 0.404), (0.14, 0.035, 0.004), cyan, 0)
box('Player sprite body', (-0.24, -0.04, 0.405), (0.07, 0.10, 0.005), pink, 0)
box('Player sprite head', (-0.24, 0.027, 0.405), (0.05, 0.035, 0.005), white, 0)
for i in range(3):
    box('Life indicator '+str(i), (-0.45+i*0.075, 0.30, 0.405), (0.045, 0.023, 0.005), pink, 0)
box('Battery outline', (0.43, 0.30, 0.405), (0.13, 0.032, 0.005), white, 0.002)
box('Battery charge', (0.417, 0.30, 0.409), (0.09, 0.018, 0.004), cyan, 0)

button('D-pad socket', -0.86, 0.10, 0.374, 0.185, 0.025, bezel)
box('D-pad horizontal', (-0.86, 0.10, 0.405), (0.31, 0.105, 0.07), black, 0.02)
box('D-pad vertical', (-0.86, 0.10, 0.406), (0.105, 0.31, 0.072), black, 0.02)
for label, x, y in [('A', 0.99, 0.10), ('B', 0.84, -0.045), ('X', 0.84, 0.245), ('Y', 0.69, 0.10)]:
    button(label+' socket', x, y, 0.375, 0.08, 0.025, bezel)
    button(label+' action button', x, y, 0.405, 0.062, 0.065, pink)
    bpy.ops.object.text_add(location=(x, y, 0.441))
    text = bpy.context.object
    text.name = label+' legend'
    text.data.body = label
    text.data.align_x = 'CENTER'
    text.data.align_y = 'CENTER'
    text.data.size = 0.053
    text.data.materials.append(white)
for x in (-0.30, 0.30):
    box('Menu button', (x, -0.434, 0.378), (0.12, 0.043, 0.032), black, 0.015)
for x in (-0.87, 0.87):
    for i in range(4):
        box('Speaker grille slot', (x+(i-1.5)*0.045, -0.32, 0.366), (0.018, 0.11, 0.008), black, 0.004)
    box('Shoulder bumper', (x, 0.495, 0.285), (0.33, 0.11, 0.12), black, 0.035)
box('USB port surround', (0, -0.519, 0.15), (0.19, 0.014, 0.067), bezel, 0.006)
box('USB port interior', (0, -0.528, 0.15), (0.135, 0.01, 0.035), black, 0.004)
box('Display surface', (0, 0, -0.035), (5, 4, 0.1), floor)
bpy.ops.object.camera_add(location=(1.9, -2.6, 4.4))
cam = bpy.context.object
cam.name = 'Console product camera'
cam.rotation_euler = (Vector((0, 0, 0.18))-cam.location).to_track_quat('-Z', 'Y').to_euler()
cam.data.type = 'ORTHO'
cam.data.ortho_scale = 2.95
bpy.context.scene.camera = cam
bpy.ops.object.light_add(type='AREA', location=(-2, -1, 4))
bpy.context.object.data.energy = 500
bpy.context.object.data.size = 3
bpy.context.scene.world.color = (0.25, 0.25, 0.25)
