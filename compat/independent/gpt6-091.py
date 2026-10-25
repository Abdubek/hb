import bpy
import math
from mathutils import Vector

# Cinema seating on three broad tiers; seats face negative Y.
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)

def material(name, color, metallic=0.0, roughness=0.5):
    mat = bpy.data.materials.new(name)
    mat.diffuse_color = (*color, 1)
    mat.use_nodes = True
    bsdf = mat.node_tree.nodes.get('Principled BSDF')
    bsdf.inputs['Base Color'].default_value = (*color, 1)
    bsdf.inputs['Metallic'].default_value = metallic
    bsdf.inputs['Roughness'].default_value = roughness
    return mat

velvet = material('Burgundy upholstery', (0.29, 0.018, 0.035), roughness=0.82)
shell = material('Charcoal seat shells', (0.025, 0.032, 0.04))
steel = material('Satin black steel', (0.045, 0.052, 0.06), 0.7, 0.32)
carpet = material('Graphite carpet', (0.085, 0.095, 0.12), roughness=0.95)
trim = material('Brass step nosing', (0.55, 0.36, 0.12), 0.65, 0.32)
floor_mat = material('Room floor', (0.18, 0.2, 0.23), roughness=0.8)

def box(name, location, size, mat, bevel=0.03):
    bpy.ops.mesh.primitive_cube_add(size=1, location=location)
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
    return obj

def cylinder(name, location, radius, depth, mat):
    bpy.ops.mesh.primitive_cylinder_add(vertices=24, radius=radius, depth=depth, location=location)
    obj = bpy.context.object
    obj.name = name
    obj.data.materials.append(mat)
    mod = obj.modifiers.new('Soft rim', 'BEVEL')
    mod.width = 0.012
    mod.segments = 2
    obj.modifiers.new('Weighted normals', 'WEIGHTED_NORMAL')
    return obj

box('Floor', (0, 0.2, -0.10), (8.5, 6.1, 0.2), floor_mat)
# Contiguous stepped slabs, each individually supported down to floor.
for index, (y, height) in enumerate([(-1.6, 0.18), (0, 0.36), (1.6, 0.54)]):
    box('Platform tier %d' % (index + 1), (0, y, height / 2), (7.3, 1.6, height), carpet, 0.015)
    box('Tier %d front nosing' % (index + 1), (0, y - 0.776, height + 0.007), (7.25, 0.045, 0.014), trim, 0.004)

# A single row on the rear tier; the lower tiers form the approach.
base_z = 0.54
seat_y = 1.48
for i in range(5):
    x = (i - 2) * 1.18
    prefix = 'Seat %02d ' % (i + 1)
    box(prefix + 'anchor plate', (x, seat_y, base_z + 0.045), (0.59, 0.64, 0.09), steel)
    box(prefix + 'pedestal', (x, seat_y + 0.03, base_z + 0.29), (0.21, 0.32, 0.49), steel)
    box(prefix + 'seat pan', (x, seat_y - 0.07, base_z + 0.52), (0.91, 0.83, 0.13), shell, 0.055)
    box(prefix + 'seat cushion', (x, seat_y - 0.09, base_z + 0.63), (0.85, 0.77, 0.18), velvet, 0.075)
    back = box(prefix + 'back shell', (x, seat_y + 0.38, base_z + 1.13), (0.96, 0.19, 1.25), shell, 0.085)
    back.rotation_euler.x = math.radians(-8)
    pad = box(prefix + 'back cushion', (x, seat_y + 0.265, base_z + 1.16), (0.85, 0.19, 1.11), velvet, 0.085)
    pad.rotation_euler.x = math.radians(-8)
    head = box(prefix + 'headrest', (x, seat_y + 0.19, base_z + 1.51), (0.67, 0.14, 0.27), velvet, 0.06)
    head.rotation_euler.x = math.radians(-8)
    # Small seat number on the front face of the pedestal.
    bpy.ops.object.text_add(location=(x, seat_y - 0.137, base_z + 0.25), rotation=(math.pi / 2, 0, 0))
    label = bpy.context.object
    label.name = prefix + 'number'
    label.data.body = str(i + 1)
    label.data.align_x = 'CENTER'
    label.data.size = 0.11
    label.data.extrude = 0.001
    label.data.materials.append(trim)

# Shared armrests between neighboring seats, plus both outer arms.
for i in range(6):
    x = -2.95 + i * 1.18
    box('Arm support %02d' % i, (x, seat_y + 0.14, base_z + 0.61), (0.075, 0.20, 0.67), steel)
    box('Armrest %02d' % i, (x, seat_y - 0.05, base_z + 0.91), (0.20, 0.86, 0.14), shell, 0.065)
    cylinder('Cup recess %02d' % i, (x, seat_y - 0.30, base_z + 0.987), 0.065, 0.009, steel)
    bpy.ops.mesh.primitive_torus_add(major_segments=24, minor_segments=8, location=(x, seat_y - 0.30, base_z + 0.998), major_radius=0.071, minor_radius=0.012)
    bpy.context.object.name = 'Cup holder rim %02d' % i
    bpy.context.object.data.materials.append(steel)

bpy.ops.object.camera_add(location=(8.8, -10, 7.4))
camera = bpy.context.object
camera.name = 'Cinema overview camera'
camera.rotation_euler = (Vector((0, 0.5, 0.8)) - camera.location).to_track_quat('-Z', 'Y').to_euler()
camera.data.type = 'ORTHO'
camera.data.ortho_scale = 10.8
bpy.context.scene.camera = camera
bpy.ops.object.light_add(type='AREA', location=(1, -3, 8))
bpy.context.object.name = 'Ceiling softbox'
bpy.context.object.data.energy = 1600
bpy.context.object.data.shape = 'DISK'
bpy.context.object.data.size = 7
bpy.context.scene.world.color = (0.22, 0.22, 0.22)
bpy.context.scene.render.resolution_x = 1200
bpy.context.scene.render.resolution_y = 900
