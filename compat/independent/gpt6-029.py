import bpy
import math
from mathutils import Vector

# Warehouse storage bay, with three accessible shelf levels.
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)

def material(name, color, metallic=0.0):
    mat = bpy.data.materials.new(name)
    mat.diffuse_color = (*color, 1)
    mat.use_nodes = True
    bsdf = mat.node_tree.nodes.get('Principled BSDF')
    bsdf.inputs['Base Color'].default_value = (*color, 1)
    bsdf.inputs['Metallic'].default_value = metallic
    bsdf.inputs['Roughness'].default_value = 0.48
    return mat

blue = material('Blue powder-coated uprights', (0.045, 0.16, 0.32), 0.55)
orange = material('Orange load beams', (0.95, 0.25, 0.045), 0.4)
steel = material('Galvanized shelf steel', (0.38, 0.43, 0.47), 0.65)
cardboard = material('Kraft cardboard', (0.55, 0.33, 0.15))
tape = material('Packing tape', (0.78, 0.60, 0.32))
label = material('Ivory shipping labels', (0.91, 0.91, 0.82))
drum_blue = material('Blue drum enamel', (0.04, 0.28, 0.43), 0.45)
drum_red = material('Red drum enamel', (0.55, 0.075, 0.04), 0.45)
dark = material('Dark drum rims', (0.11, 0.13, 0.14), 0.7)
concrete = material('Concrete floor', (0.28, 0.30, 0.31))

def box(name, location, size, mat, bevel=0.025):
    bpy.ops.mesh.primitive_cube_add(size=1, location=location)
    obj = bpy.context.object
    obj.name = name
    obj.dimensions = size
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    obj.data.materials.append(mat)
    if bevel:
        mod = obj.modifiers.new('Soft manufactured edges', 'BEVEL')
        mod.width = bevel
        mod.segments = 2
        obj.modifiers.new('Weighted corner normals', 'WEIGHTED_NORMAL')
    return obj

def cylinder(name, location, radius, depth, mat):
    bpy.ops.mesh.primitive_cylinder_add(vertices=32, radius=radius, depth=depth, location=location)
    obj = bpy.context.object
    obj.name = name
    obj.data.materials.append(mat)
    bevel = obj.modifiers.new('Rolled edges', 'BEVEL')
    bevel.width = 0.012
    bevel.segments = 2
    obj.modifiers.new('Weighted normals', 'WEIGHTED_NORMAL')
    return obj

def strut(name, a, b, width, mat):
    a, b = Vector(a), Vector(b)
    obj = box(name, (a + b) / 2, (width, width, (b - a).length), mat, 0.008)
    obj.rotation_euler = (b - a).to_track_quat('Z', 'Y').to_euler()

def carton(name, x, y, base, w, d, h):
    box(name, (x, y, base + h / 2), (w, d, h), cardboard)
    box(name + ' top tape', (x, y, base + h + 0.004), (0.105, d - 0.02, 0.008), tape, 0.002)
    box(name + ' front tape', (x, y - d / 2 - 0.004, base + h / 2), (0.105, 0.008, h), tape, 0.002)
    box(name + ' shipping label', (x + w * 0.24, y - d / 2 - 0.01, base + h * 0.58), (w * 0.27, 0.01, h * 0.27), label, 0.002)

def barrel(name, x, y, base, mat):
    radius, height = 0.34, 0.89
    cylinder(name + ' shell', (x, y, base + height / 2), radius, height, mat)
    for i, z in enumerate((0.025, 0.23, 0.66, 0.865)):
        cylinder(name + ' reinforcing hoop ' + str(i), (x, y, base + z), radius + 0.018, 0.035, dark)
    cylinder(name + ' lid', (x, y, base + height + 0.003), radius - 0.025, 0.016, mat)
    cylinder(name + ' fill bung', (x + 0.17, y, base + height + 0.021), 0.044, 0.022, dark)

box('Warehouse concrete slab', (0, 0, -0.10), (8.5, 6.5, 0.2), concrete)
for x in (-2.5, 2.5):
    for y in (-0.72, 0.72):
        box('Rack upright', (x, y, 1.95), (0.13, 0.13, 3.9), blue)
        box('Anchored foot plate', (x, y, 0.035), (0.32, 0.30, 0.07), steel)
        for z in (0.65, 1.0, 1.35, 1.7, 2.05, 2.4, 2.75, 3.1, 3.45):
            box('Upright adjustment slot', (x, y - 0.066, z), (0.038, 0.006, 0.075), dark, 0.004)
    strut('Side diagonal brace A', (x, -0.69, 0.3), (x, 0.69, 2.0), 0.055, steel)
    strut('Side diagonal brace B', (x, 0.69, 2.0), (x, -0.69, 3.75), 0.055, steel)
for level, z in enumerate((0.27, 1.57, 2.87)):
    for y in (-0.72, 0.72):
        box('Level %d orange beam' % level, (0, y, z), (5.0, 0.12, 0.17), orange)
    box('Level %d steel deck' % level, (0, 0, z + 0.09), (4.87, 1.39, 0.045), steel, 0.01)
    box('Level %d capacity label' % level, (0, -0.786, z), (0.36, 0.01, 0.10), label, 0.003)
barrel('Lower blue drum', -1.85, 0, 0.383, drum_blue)
barrel('Lower red drum', -1.0, 0, 0.383, drum_red)
carton('Lower wide carton', 0.35, 0, 0.383, 1.35, 1.05, 0.82)
carton('Lower narrow carton', 1.65, 0, 0.383, 0.9, 0.95, 0.65)
for i, x in enumerate((-1.8, -0.6, 0.65, 1.85)):
    carton('Middle carton %d' % i, x, 0, 1.683, 1.02, 1.05, 0.78 if i % 2 else 0.95)
carton('Top long carton', -1.35, 0, 2.983, 1.9, 1.05, 0.66)
carton('Top small carton', 0.23, 0, 2.983, 0.95, 0.9, 0.8)
barrel('Top blue drum', 1.55, 0, 2.983, drum_blue)

world = bpy.context.scene.world or bpy.data.worlds.new('Warehouse world')
bpy.context.scene.world = world
world.use_nodes = True
world.node_tree.nodes['Background'].inputs[0].default_value = (0.55, 0.62, 0.72, 1)
world.node_tree.nodes['Background'].inputs[1].default_value = 0.45
bpy.ops.object.light_add(type='AREA', location=(1, -4, 7))
bpy.context.object.name = 'Large overhead warehouse light'
bpy.context.object.data.energy = 1600
bpy.context.object.data.shape = 'DISK'
bpy.context.object.data.size = 6
bpy.ops.object.camera_add(location=(7.5, -10, 6.4))
camera = bpy.context.object
camera.name = 'Rack overview camera'
camera.rotation_euler = (Vector((0, 0, 1.9)) - camera.location).to_track_quat('-Z', 'Y').to_euler()
camera.data.type = 'ORTHO'
camera.data.ortho_scale = 7.7
bpy.context.scene.camera = camera
bpy.context.scene.render.resolution_x = 1400
bpy.context.scene.render.resolution_y = 1100
bpy.context.scene.render.resolution_percentage = 100
