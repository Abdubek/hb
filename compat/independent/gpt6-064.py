import bpy
import math
from mathutils import Vector

bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)

def material(name, color, metallic=0.0, emission=0.0):
    m = bpy.data.materials.new(name)
    m.diffuse_color = (*color, 1)
    m.use_nodes = True
    p = m.node_tree.nodes.get('Principled BSDF')
    p.inputs['Base Color'].default_value = (*color, 1)
    p.inputs['Metallic'].default_value = metallic
    p.inputs['Roughness'].default_value = 0.36
    if emission:
        p.inputs['Emission Color'].default_value = (*color, 1)
        p.inputs['Emission Strength'].default_value = emission
    return m

def box(name, loc, size, mat, bevel=0.02):
    bpy.ops.mesh.primitive_cube_add(size=1, location=loc)
    o = bpy.context.object
    o.name = name
    o.dimensions = size
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    o.data.materials.append(mat)
    if bevel:
        b = o.modifiers.new('Soft cabinet edges', 'BEVEL')
        b.width = bevel
        b.segments = 3
        o.modifiers.new('Weighted normals', 'WEIGHTED_NORMAL')
    return o

def cylinder(name, loc, radius, depth, mat):
    bpy.ops.mesh.primitive_cylinder_add(vertices=24, radius=radius, depth=depth, location=loc)
    o = bpy.context.object
    o.name = name
    o.data.materials.append(mat)
    b = o.modifiers.new('Rounded edges', 'BEVEL')
    b.width = 0.008
    b.segments = 3
    o.modifiers.new('Weighted normals', 'WEIGHTED_NORMAL')
    return o

def text(name, body, loc, size, mat):
    bpy.ops.object.text_add(location=loc, rotation=(math.pi / 2, 0, 0))
    o = bpy.context.object
    o.name = name
    o.data.body = body
    o.data.size = size
    o.data.align_x = 'CENTER'
    o.data.align_y = 'CENTER'
    o.data.extrude = 0.001
    o.data.materials.append(mat)
    return o

purple = material('Purple laminate', (0.19, 0.035, 0.34))
black = material('Black plastic and recesses', (0.014, 0.018, 0.028))
cyan = material('Turquoise trim', (0.02, 0.71, 0.82), 0.15)
pink = material('Hot pink controls', (0.92, 0.025, 0.25))
metal = material('Joystick chrome', (0.57, 0.65, 0.72), 0.85)
white = material('Ivory print', (0.92, 0.94, 0.85))
screen = material('Screen blue black', (0.008, 0.025, 0.065), emission=0.3)
pixel = material('Game phosphor', (0.08, 0.91, 0.68), emission=1.5)
ground = material('Floor', (0.14, 0.17, 0.21))

# Extruded side profiles form the classic overhanging arcade silhouette.
profile = [(-0.56, 0.12), (0.53, 0.12), (0.53, 2.65),
           (-0.39, 2.65), (-0.48, 2.33), (-0.27, 2.25),
           (-0.44, 1.55), (-0.72, 1.39), (-0.72, 1.22), (-0.56, 1.15)]
for side, x in [('Left', -0.66), ('Right', 0.66)]:
    verts = [(xx, y, z) for xx in (x - 0.065, x + 0.065) for y, z in profile]
    n = len(profile)
    faces = [tuple(reversed(range(n))), tuple(range(n, n * 2))]
    faces += [(i, (i + 1) % n, (i + 1) % n + n, i + n] for i in range(n)]
    mesh = bpy.data.meshes.new(side + ' profile mesh')
    mesh.from_pydata(verts, [], faces)
    mesh.update()
    o = bpy.data.objects.new(side + ' shaped side panel', mesh)
    bpy.context.collection.objects.link(o)
    o.data.materials.append(purple)
    bevel = o.modifiers.new('Panel edge rounding', 'BEVEL')
    bevel.width = 0.018
    bevel.segments = 3
    o.modifiers.new('Weighted normals', 'WEIGHTED_NORMAL')

box('Rear enclosure', (0, 0.48, 1.37), (1.21, 0.10, 2.50), black)
box('Base plinth', (0, 0, 0.10), (1.40, 1.10, 0.20), black)
box('Lower front cabinet', (0, -0.49, 0.72), (1.19, 0.12, 1.12), purple)
box('Control console', (0, -0.36, 1.32), (1.24, 0.72, 0.16), black)
box('Console front accent', (0, -0.728, 1.32), (1.26, 0.025, 0.08), cyan)
box('Roof', (0, 0.055, 2.61), (1.30, 0.96, 0.10), black)
box('Marquee housing', (0, -0.395, 2.48), (1.25, 0.16, 0.29), black)
box('Marquee face', (0, -0.483, 2.48), (1.15, 0.025, 0.22), pink)
text('Marquee title', 'NEON ORBIT', (0, -0.502, 2.48), 0.145, white)

# Screen and its graphics share a tilted local coordinate system.
angle = math.radians(-13)
center = Vector((0, -0.325, 1.94))
rotation = mathutils_rotation = __import__('mathutils').Matrix.Rotation(angle, 4, 'X')
def screen_part(name, local, size, mat, bevel=0.005):
    position = center + rotation.to_3x3() @ Vector(local)
    o = box(name, position, size, mat, bevel)
    o.rotation_euler.x = angle
    return o
screen_part('Monitor surround', (0, 0, 0), (1.19, 0.12, 0.81), black, 0.035)
screen_part('Monitor silver border', (0, -0.068, 0), (1.04, 0.02, 0.67), metal)
screen_part('Arcade screen', (0, -0.083, 0), (0.99, 0.015, 0.62), screen, 0.015)
for row in range(3):
    for col in range(6):
        screen_part('Alien sprite %d-%d' % (row, col), (-0.36 + col * 0.145, -0.096, 0.19 - row * 0.10), (0.064, 0.008, 0.038), pixel, 0)
screen_part('Player ship', (0.05, -0.10, -0.22), (0.12, 0.008, 0.025), white, 0)
screen_part('Player ship nose', (0.05, -0.10, -0.197), (0.036, 0.008, 0.028), white, 0)
screen_part('Laser shot', (0.05, -0.10, -0.11), (0.012, 0.008, 0.044), pink, 0)

cylinder('Joystick rubber boot', (-0.36, -0.43, 1.417), 0.11, 0.035, black)
cylinder('Joystick shaft', (-0.36, -0.43, 1.52), 0.023, 0.20, metal)
bpy.ops.mesh.primitive_uv_sphere_add(segments=24, ring_count=12, radius=0.085, location=(-0.36, -0.43, 1.64))
bpy.context.object.name = 'Joystick pink ball grip'
bpy.context.object.data.materials.append(pink)
for p in bpy.context.object.data.polygons:
    p.use_smooth = True
for row in range(2):
    for col in range(3):
        x, y = 0.07 + col * 0.17, -0.51 + row * 0.19
        cylinder('Action button collar %d-%d' % (row, col), (x, y, 1.41), 0.070, 0.025, metal)
        cylinder('Action button %d-%d' % (row, col), (x, y, 1.435), 0.055, 0.035, pink if row == 0 else cyan)
box('Coin door', (0, -0.561, 0.76), (0.49, 0.035, 0.56), black)
box('Coin acceptor plate', (0, -0.585, 0.89), (0.18, 0.02, 0.20), metal)
box('Coin slot', (0, -0.600, 0.91), (0.023, 0.012, 0.12), black, 0.003)
text('Coin instruction', 'INSERT COIN', (0, -0.589, 0.61), 0.062, white)
for i in range(6):
    box('Speaker grille slot %d' % i, (-0.20 + i * 0.08, -0.563, 0.30), (0.033, 0.018, 0.10), black, 0.008)
box('Ground', (0, 0, -0.06), (200, 200, 0.1), ground, 0)
bpy.ops.object.camera_add(location=(3.6, -5.4, 3.5))
cam = bpy.context.object
cam.name = 'Arcade showcase camera'
cam.rotation_euler = (Vector((0, -0.05, 1.35)) - cam.location).to_track_quat('-Z', 'Y').to_euler()
cam.data.type = 'ORTHO'
cam.data.ortho_scale = 3.7
bpy.context.scene.camera = cam
bpy.ops.object.light_add(type='AREA', location=(0, -4, 5))
bpy.context.object.data.energy = 900
bpy.context.object.data.size = 4
bpy.context.scene.world.color = (0.23, 0.23, 0.23)
