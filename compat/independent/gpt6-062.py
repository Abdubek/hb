import bpy
from mathutils import Vector

# Standalone scene: drawer fronts and television face negative Y.
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)

def material(name, color, roughness=0.5, metallic=0.0):
    m = bpy.data.materials.new(name)
    m.diffuse_color = (*color, 1)
    m.use_nodes = True
    bs = m.node_tree.nodes.get('Principled BSDF')
    bs.inputs['Base Color'].default_value = (*color, 1)
    bs.inputs['Roughness'].default_value = roughness
    bs.inputs['Metallic'].default_value = metallic
    return m

def box(name, loc, size, mat, bevel=0.0):
    bpy.ops.mesh.primitive_cube_add(size=1, location=loc)
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

def beam(name, start, end, width, depth, mat):
    a, b = Vector(start), Vector(end)
    obj = box(name, (a+b)/2, (width, depth, (b-a).length), mat, 0.012)
    obj.rotation_euler = (b-a).to_track_quat('Z', 'Y').to_euler()
    return obj

walnut = material('Walnut cabinet', (0.23, 0.105, 0.046))
frontwood = material('Warm walnut drawer fronts', (0.34, 0.175, 0.083))
inside = material('Dark cabinet interior', (0.095, 0.053, 0.027))
black = material('Satin black television housing', (0.016, 0.02, 0.024), 0.33)
metal = material('Brushed graphite hardware', (0.08, 0.09, 0.105), 0.3, 0.75)
glass = material('Dark blue screen glass', (0.014, 0.036, 0.06), 0.13, 0.25)
floor = material('Soft gray floor', (0.39, 0.41, 0.42))
plaster = material('Warm white wall', (0.76, 0.75, 0.71))
ceramic = material('Ivory ceramic', (0.72, 0.68, 0.56), 0.3)
bookmat = material('Muted teal book cover', (0.06, 0.21, 0.22))
paper = material('Book page edges', (0.72, 0.69, 0.6))
led = material('Power indicator', (0.1, 0.6, 0.78), 0.3)
bs = led.node_tree.nodes.get('Principled BSDF')
bs.inputs['Emission Color'].default_value = (0.1, 0.6, 0.78, 1)
bs.inputs['Emission Strength'].default_value = 1.5

box('Room floor', (0, 0, -0.075), (10, 8, 0.15), floor)
box('Backdrop wall', (0, 1.5, 2.5), (10, 0.15, 5), plaster)
box('Wall baseboard', (0, 1.39, 0.09), (10, 0.07, 0.18), ceramic, 0.008)
for x in [-1.7, 1.7]:
    for y in [-0.35, 0.35]:
        beam('Splayed console leg', (x*1.04, y*1.14, 0.05), (x, y, 0.31), 0.085, 0.085, metal)
box('Cabinet bottom panel', (0, 0, 0.32), (3.9, 1.02, 0.12), walnut, 0.018)
box('Overhanging console top', (0, 0, 1.23), (4.04, 1.1, 0.14), walnut, 0.025)
box('Cabinet back panel', (0, 0.47, 0.77), (3.78, 0.07, 0.78), inside, 0.006)
for x, label in [(-1.89, 'Left'), (1.89, 'Right')]:
    box(label+' cabinet side', (x, 0, 0.77), (0.12, 1.02, 0.78), walnut, 0.012)
for x in [-0.63, 0.63]:
    box('Internal vertical divider', (x, 0, 0.77), (0.06, 0.93, 0.78), walnut, 0.006)
box('Central horizontal divider', (0, 0, 0.77), (3.78, 0.93, 0.055), walnut, 0.005)
# Six separate drawer assemblies; narrow gaps reveal the cabinet structure.
for col, x in enumerate([-1.25, 0, 1.25]):
    for row, z in enumerate([0.56, 0.98]):
        label = f'Drawer {row+1}-{col+1}'
        box(label+' box', (x, -0.015, z-0.025), (1.12, 0.82, 0.28), inside, 0.008)
        box(label+' front', (x, -0.536, z), (1.215, 0.075, 0.382), frontwood, 0.012)
        for dx in [-0.21, 0.21]:
            box(label+' pull mount', (x+dx, -0.6, z+0.04), (0.045, 0.07, 0.035), metal, 0.008)
        box(label+' bar pull', (x, -0.639, z+0.04), (0.48, 0.035, 0.038), metal, 0.01)

# Broad 16:9 panel with a thin bezel, deeper rear housing and two V feet.
box('Television outer bezel', (0, 0.095, 2.43), (3.18, 0.105, 1.84), black, 0.027)
box('Television rear electronics housing', (0, 0.175, 2.3), (2.35, 0.1, 1.16), black, 0.045)
box('Television glass display', (0, 0.036, 2.45), (3.055, 0.016, 1.719), glass, 0.012)
box('Television lower chin', (0, 0.027, 1.55), (3.08, 0.024, 0.045), black, 0.007)
box('Tiny television status light', (1.35, 0.011, 1.55), (0.025, 0.006, 0.009), led, 0.003)
for sign in [-1, 1]:
    x = sign*1.05
    beam('TV forward angled foot', (x, 0.09, 1.59), (x+sign*0.14, -0.29, 1.327), 0.045, 0.045, metal)
    beam('TV rear angled foot', (x, 0.09, 1.59), (x+sign*0.14, 0.36, 1.327), 0.045, 0.045, metal)
    box('TV front foot pad', (x+sign*0.14, -0.28, 1.316), (0.17, 0.13, 0.032), black, 0.012)
    box('TV rear foot pad', (x+sign*0.14, 0.35, 1.316), (0.14, 0.12, 0.032), black, 0.012)
# Small tabletop objects establish scale without obscuring the television.
box('Remote control', (0.38, -0.37, 1.327), (0.14, 0.31, 0.045), black, 0.025)
for row in range(4):
    for col in range(2):
        box('Remote button', (0.351+col*0.058, -0.44+row*0.048, 1.354), (0.024, 0.022, 0.009), metal, 0.005)
for z in [1.31, 1.385]:
    box('Book cover', (-1.73, -0.07, z), (0.34, 0.48, 0.014), bookmat, 0.004)
box('Book pages', (-1.73, -0.07, 1.348), (0.32, 0.45, 0.06), paper, 0.003)

scene = bpy.context.scene
scene.world.color = (0.25, 0.25, 0.25)
bpy.ops.object.light_add(type='AREA', location=(-3, -4, 6))
light = bpy.context.object
light.name = 'Large studio softbox'
light.data.energy = 1200
light.data.size = 5
light.rotation_euler = (Vector((0, 0, 1.5))-light.location).to_track_quat('-Z', 'Y').to_euler()
bpy.ops.object.camera_add(location=(5, -8, 4.6))
cam = bpy.context.object
cam.name = 'TV console camera'
cam.rotation_euler = (Vector((0, 0, 1.7))-cam.location).to_track_quat('-Z', 'Y').to_euler()
cam.data.type = 'ORTHO'
cam.data.ortho_scale = 5.9
scene.camera = cam
scene.render.resolution_x = 1200
scene.render.resolution_y = 1000
scene.render.resolution_percentage = 100
