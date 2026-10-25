import bpy
from mathutils import Vector

# Self-contained ticket kiosk, with its front facing negative Y.
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)

def material(name, color, metallic=0.0, roughness=0.45):
    mat = bpy.data.materials.new(name)
    mat.diffuse_color = (*color, 1)
    mat.use_nodes = True
    shader = mat.node_tree.nodes.get('Principled BSDF')
    shader.inputs['Base Color'].default_value = (*color, 1)
    shader.inputs['Metallic'].default_value = metallic
    shader.inputs['Roughness'].default_value = roughness
    return mat

def box(name, location, dimensions, mat, bevel=0.02):
    bpy.ops.mesh.primitive_cube_add(size=1, location=location)
    obj = bpy.context.object
    obj.name = name
    obj.dimensions = dimensions
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    obj.data.materials.append(mat)
    if bevel:
        mod = obj.modifiers.new('Soft manufactured edges', 'BEVEL')
        mod.width = bevel
        mod.segments = 3
        obj.modifiers.new('Weighted corner normals', 'WEIGHTED_NORMAL')
    return obj

def label(name, text, location, size, mat):
    curve = bpy.data.curves.new(name, 'FONT')
    curve.body = text
    curve.align_x = 'CENTER'
    curve.align_y = 'CENTER'
    curve.size = size
    curve.extrude = 0.0006
    obj = bpy.data.objects.new(name, curve)
    bpy.context.collection.objects.link(obj)
    obj.location = location
    obj.rotation_euler = (1.5707963, 0, 0)
    obj.data.materials.append(mat)
    return obj

shell = material('Powder coated silver', (0.52, 0.58, 0.63), 0.65)
blue = material('Transit blue', (0.025, 0.18, 0.36), 0.3)
black = material('Black rubber and recesses', (0.013, 0.022, 0.03))
glass = material('Touchscreen dark glass', (0.025, 0.075, 0.105), 0.25, 0.19)
white = material('White lettering', (0.9, 0.95, 0.98))
cyan = material('Interface cyan', (0.04, 0.62, 0.81), 0.15)
green = material('Payment indicator', (0.16, 0.85, 0.34))
paper = material('Ticket paper', (0.92, 0.88, 0.71))
floor = material('Station floor', (0.23, 0.25, 0.27))

box('Station floor slab', (0, 0, -0.06), (5, 4, 0.12), floor)
box('Anchored plinth', (0, 0, 0.095), (1.0, 0.78, 0.19), black, 0.035)
box('Kiosk main cabinet', (0, 0, 1.15), (0.88, 0.64, 2.1), shell, 0.065)
box('Blue front fascia', (0, -0.335, 1.27), (0.78, 0.065, 1.77), blue, 0.025)
box('Top identity header', (0, -0.378, 1.99), (0.70, 0.025, 0.22), blue)
label('Kiosk title', 'TICKETS', (0, -0.396, 2.015), 0.095, white)
label('Kiosk subtitle', 'CITY TRANSIT', (0, -0.397, 1.945), 0.031, white)
box('Touchscreen bezel', (0, -0.391, 1.59), (0.69, 0.06, 0.55), black, 0.028)
box('Touchscreen glass', (0, -0.425, 1.59), (0.61, 0.012, 0.47), glass, 0.008)
label('Screen heading', 'Where to?', (0, -0.435, 1.755), 0.052, white)
label('Screen instruction', 'SELECT YOUR TICKET', (0, -0.435, 1.687), 0.025, white)
for x, text in [(-0.151, 'SINGLE'), (0.151, 'DAY PASS')]:
    box('Touch button ' + text, (x, -0.438, 1.58), (0.267, 0.006, 0.102), cyan, 0.006)
    label('Button caption ' + text, text, (x, -0.443, 1.58), 0.028, white)
label('Fare status', '1 ADULT     $2.50', (0, -0.435, 1.474), 0.032, white)
box('Continue touch target', (0, -0.438, 1.403), (0.39, 0.006, 0.055), blue, 0.006)
label('Continue caption', 'CONTINUE  >', (0, -0.444, 1.403), 0.027, white)

box('Card reader housing', (0.205, -0.418, 1.10), (0.245, 0.13, 0.31), black, 0.025)
box('Reader display', (0.205, -0.486, 1.18), (0.174, 0.01, 0.074), glass, 0.005)
label('Reader ready', 'TAP / INSERT', (0.205, -0.494, 1.18), 0.019, green)
for row in range(3):
    for col in range(3):
        box('Reader keypad %d %d' % (row, col),
            (0.151 + col * 0.054, -0.491, 1.116 - row * 0.033),
            (0.035, 0.012, 0.022), shell, 0.004)
box('Card insertion rim', (0.205, -0.493, 0.983), (0.186, 0.022, 0.035), shell, 0.005)
box('Card insertion dark slot', (0.205, -0.506, 0.983), (0.158, 0.004, 0.012), black, 0.002)
label('Payment instruction', 'PAY HERE', (-0.18, -0.377, 1.17), 0.04, white)
label('Accepted payment', 'CARD ONLY', (-0.18, -0.377, 1.10), 0.027, white)
box('Ticket outlet surround', (0, -0.39, 0.76), (0.49, 0.055, 0.12), shell, 0.012)
box('Ticket outlet shadow', (0, -0.423, 0.77), (0.41, 0.014, 0.041), black, 0.004)
box('Printed ticket', (-0.06, -0.493, 0.752), (0.235, 0.15, 0.006), paper, 0.001)
box('Ticket catch tray', (0, -0.446, 0.68), (0.5, 0.2, 0.025), black, 0.01)
label('Collection caption', 'COLLECT TICKET', (0, -0.377, 0.88), 0.035, white)
box('Lower service door', (0, -0.337, 0.36), (0.68, 0.025, 0.28), shell, 0.012)
box('Service lock', (0.265, -0.354, 0.40), (0.018, 0.01, 0.028), black, 0.004)

bpy.ops.object.camera_add(location=(3.0, -4.6, 2.85))
camera = bpy.context.object
camera.name = 'Kiosk presentation camera'
camera.rotation_euler = (Vector((0, -0.1, 1.08)) - camera.location).to_track_quat('-Z', 'Y').to_euler()
camera.data.type = 'ORTHO'
camera.data.ortho_scale = 3.25
scene = bpy.context.scene
scene.camera = camera
bpy.ops.object.light_add(type='AREA', location=(1, -3, 5))
bpy.context.object.data.energy = 650
bpy.context.object.data.shape = 'DISK'
bpy.context.object.data.size = 4
scene.world.color = (0.22, 0.22, 0.22)
scene.render.resolution_x = 800
scene.render.resolution_y = 900
scene.render.resolution_percentage = 100
