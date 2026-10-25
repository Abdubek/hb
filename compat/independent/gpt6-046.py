import bpy
import math
from mathutils import Vector

# Open-front exhibition booth assembled from repeated wall modules.
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

white = material('Warm white wall panels', (0.86, 0.85, 0.81))
teal = material('Brand deep teal', (0.025, 0.23, 0.26))
metal = material('Brushed aluminum frames', (0.52, 0.58, 0.61), 0.75)
oak = material('Oak platform and countertops', (0.52, 0.34, 0.18))
dark = material('Graphite product finish', (0.045, 0.055, 0.065), 0.45)
orange = material('Terracotta product finish', (0.78, 0.25, 0.10))
ground = material('Exhibition hall floor', (0.29, 0.32, 0.35))


def box(name, location, dimensions, mat, bevel=0.012):
    bpy.ops.mesh.primitive_cube_add(size=1, location=location)
    obj = bpy.context.object
    obj.name = name
    obj.dimensions = dimensions
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    obj.data.materials.append(mat)
    if bevel:
        mod = obj.modifiers.new('Edge rounding', 'BEVEL')
        mod.width = bevel
        mod.segments = 2
        obj.modifiers.new('Weighted normals', 'WEIGHTED_NORMAL')
    return obj

def cylinder(name, location, radius, depth, mat):
    bpy.ops.mesh.primitive_cylinder_add(vertices=32, radius=radius, depth=depth, location=location)
    obj = bpy.context.object
    obj.name = name
    obj.data.materials.append(mat)
    bevel = obj.modifiers.new('Machined rim', 'BEVEL')
    bevel.width = 0.012
    bevel.segments = 2
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

box('Hall ground', (0, 0, -0.065), (10, 9, 0.12), ground)
box('Raised booth platform', (0, 0, 0.08), (6.2, 4.5, 0.16), oak, 0.025)
box('Front aluminum platform trim', (0, -2.255, 0.08), (6.2, 0.025, 0.12), metal, 0.003)
# Six individually framed back-wall panels, each one meter wide.
for i in range(6):
    x = -2.5 + i
    box('Back wall module %02d' % (i + 1), (x, 2.10, 1.57),
        (0.955, 0.11, 2.80), teal if i in (2, 3) else white)
for i in range(7):
    box('Back frame upright %02d' % i, (-3 + i, 2.10, 1.59), (0.045, 0.16, 2.86), metal, 0.003)
for z in (0.19, 2.99):
    box('Back horizontal frame', (0, 2.10, z), (6.05, 0.16, 0.045), metal, 0.003)
# Three left return modules establish an L-shaped booth with two open sides.
for i in range(3):
    box('Left return panel %02d' % i, (-3, 1.60 - i, 1.57), (0.11, 0.955, 2.80), white)
for i in range(4):
    box('Left return upright %02d' % i, (-3, 2.10 - i, 1.59), (0.16, 0.045, 2.86), metal, 0.003)
for z in (0.19, 2.99):
    box('Left horizontal frame', (-3, 0.60, z), (0.16, 3.05, 0.045), metal, 0.003)

box('Brand header fascia', (0, 1.96, 2.68), (5.80, 0.16, 0.48), teal)
text('Primary booth identity', 'FORM / STUDIO', (0, 1.868, 2.69), 0.32, white)
text('Brand subtitle', 'OBJECTS FOR EVERYDAY SPACES', (0, 2.025, 2.18), 0.115, white)
for i, x in enumerate((-2, 2)):
    box('Graphic panel backing %d' % i, (x, 2.027, 1.70), (0.76, 0.025, 1.12), teal)
    for j in range(3):
        box('Graphic accent %d %d' % (i, j), (x - 0.22 + j * 0.22, 2.006, 1.66),
            (0.10, 0.015, 0.34 + j * 0.18), white, 0.002)

for i, (x, y, h) in enumerate([(-1.55, 0.55, 0.85), (0, 0.85, 1.05), (1.55, 0.55, 0.72)]):
    box('Display plinth %02d' % (i + 1), (x, y, 0.16 + h / 2), (0.85, 0.75, h), white, 0.018)
    box('Plinth recessed toe %02d' % i, (x, y, 0.19), (0.75, 0.65, 0.06), dark)
    box('Plinth oak cap %02d' % i, (x, y, 0.16 + h + 0.02), (0.89, 0.79, 0.04), oak)
    top = 0.20 + h
    cylinder('Product base %02d' % i, (x, y, top + 0.025), 0.23, 0.05, metal)
    box('Product enclosure %02d' % i, (x, y, top + 0.26), (0.32, 0.28, 0.42), orange if i == 1 else dark, 0.035)
    box('Product front inset %02d' % i, (x, y - 0.146, top + 0.28), (0.23, 0.015, 0.23), teal, 0.008)
    text('Plinth number %02d' % i, '0%d' % (i + 1), (x, y - 0.383, top - 0.16), 0.11, teal)

box('Welcome counter', (-1.90, -1.40, 0.68), (1.60, 0.65, 1.04), teal, 0.025)
box('Welcome counter oak top', (-1.90, -1.40, 1.225), (1.68, 0.73, 0.05), oak)
text('Welcome counter lettering', 'WELCOME', (-1.90, -1.732, 0.78), 0.16, white)
box('Information tablet', (-1.70, -1.40, 1.30), (0.36, 0.25, 0.09), dark)
scene = bpy.context.scene
scene.world.color = (0.24, 0.24, 0.24)
bpy.ops.object.light_add(type='AREA', location=(0, -1, 7))
bpy.context.object.name = 'Exhibition overhead lighting'
bpy.context.object.data.energy = 2200
bpy.context.object.data.size = 6
bpy.ops.object.camera_add(location=(8, -10, 7))
camera = bpy.context.object
camera.name = 'Booth presentation camera'
camera.rotation_euler = (Vector((0, 0.2, 1.25)) - camera.location).to_track_quat('-Z', 'Y').to_euler()
camera.data.type = 'ORTHO'
camera.data.ortho_scale = 9.2
scene.camera = camera
scene.render.resolution_x = 1200
scene.render.resolution_y = 1000
scene.render.resolution_percentage = 100
