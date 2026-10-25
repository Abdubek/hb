import bpy
import math
from mathutils import Vector

# Straight architectural stair: ten risers, upper landing, and continuous rails.
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

concrete = material('Warm architectural concrete', (0.48, 0.47, 0.43))
wood = material('Oak tread caps', (0.42, 0.23, 0.10))
steel = material('Charcoal powder coated steel', (0.055, 0.07, 0.08), 0.65)
floor_mat = material('Pale stone floor', (0.72, 0.75, 0.76))

def box(name, location, dimensions, mat, bevel=0.015):
    bpy.ops.mesh.primitive_cube_add(size=1, location=location)
    obj = bpy.context.object
    obj.name = name
    obj.dimensions = dimensions
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    obj.data.materials.append(mat)
    if bevel:
        mod = obj.modifiers.new('Soft manufactured edges', 'BEVEL')
        mod.width = bevel
        mod.segments = 2
        obj.modifiers.new('Weighted corner normals', 'WEIGHTED_NORMAL')
    return obj

def rod(name, start, end, radius=0.025, mat=steel):
    direction = Vector(end) - Vector(start)
    bpy.ops.mesh.primitive_cylinder_add(vertices=16, radius=radius,
        depth=direction.length, location=(Vector(start) + Vector(end)) / 2)
    obj = bpy.context.object
    obj.name = name
    obj.rotation_euler = direction.to_track_quat('Z', 'Y').to_euler()
    obj.data.materials.append(mat)
    for face in obj.data.polygons:
        face.use_smooth = len(face.vertices) == 4
    return obj

width, run, rise, count = 1.8, 0.32, 0.18, 10
landing_start = count * run
landing_depth = 1.55
landing_end = landing_start + landing_depth
height = count * rise
box('Ground slab', (0, 2.1, -0.10), (4.8, 7.3, 0.20), floor_mat)
for i in range(count):
    top = (i + 1) * rise
    y = (i + 0.5) * run
    box('Concrete step %02d' % (i + 1), (0, y, (top - 0.035) / 2),
        (width, run, top - 0.035), concrete, 0.008)
    box('Oak tread %02d' % (i + 1), (0, y - 0.008, top - 0.0175),
        (width + 0.06, run + 0.025, 0.035), wood, 0.006)

box('Upper landing slab', (0, (landing_start + landing_end) / 2, height - 0.14),
    (width, landing_depth, 0.28), concrete)
box('Landing oak surface', (0, (landing_start + landing_end) / 2, height + 0.0175),
    (width + 0.06, landing_depth, 0.035), wood, 0.006)
for x in (-0.72, 0.72):
    for y in (landing_start + 0.22, landing_end - 0.20):
        box('Landing support column', (x, y, (height - 0.28) / 2),
            (0.14, 0.14, height - 0.28), steel)
        box('Column foot plate', (x, y, 0.025), (0.26, 0.26, 0.05), steel)

rail_height = 0.96
for side, x in [('Left', -0.83), ('Right', 0.83)]:
    for i in range(count):
        y, z = (i + 0.5) * run, (i + 1) * rise
        box(side + ' stair post base %02d' % i, (x, y, z + 0.015),
            (0.11, 0.11, 0.03), steel, 0.004)
        rod(side + ' stair baluster %02d' % i, (x, y, z), (x, y, z + rail_height), 0.018)
    first_y, last_y = run / 2, (count - 0.5) * run
    for offset, radius, label in [(rail_height, 0.035, 'Handrail'), (0.48, 0.018, 'Midrail')]:
        rod(side + ' sloping ' + label, (x, first_y, rise + offset),
            (x, last_y, height + offset), radius)
        rod(side + ' landing ' + label, (x, last_y, height + offset),
            (x, landing_end - 0.08, height + offset), radius)
    for j in range(5):
        y = landing_start + 0.12 + j * (landing_depth - 0.20) / 4
        rod(side + ' landing baluster %02d' % j, (x, y, height),
            (x, y, height + rail_height), 0.018)

# Guard the back edge while leaving the lower stair entry open.
back_y = landing_end - 0.08
for j in range(7):
    x = -0.83 + j * 1.66 / 6
    rod('Rear guard baluster %02d' % j, (x, back_y, height),
        (x, back_y, height + rail_height), 0.018)
for offset in (0.48, rail_height):
    rod('Rear landing cross rail', (-0.83, back_y, height + offset),
        (0.83, back_y, height + offset), 0.03)

scene = bpy.context.scene
scene.world.color = (0.22, 0.22, 0.22)
bpy.ops.object.light_add(type='AREA', location=(1, -2, 8))
bpy.context.object.name = 'Large overhead softbox'
bpy.context.object.data.energy = 1700
bpy.context.object.data.shape = 'DISK'
bpy.context.object.data.size = 6
bpy.ops.object.camera_add(location=(7, -7, 5.7))
camera = bpy.context.object
camera.name = 'Staircase overview camera'
camera.rotation_euler = (Vector((0, 2.3, 1.25)) - camera.location).to_track_quat('-Z', 'Y').to_euler()
camera.data.type = 'ORTHO'
camera.data.ortho_scale = 8.4
scene.camera = camera
scene.render.resolution_x = 1200
scene.render.resolution_y = 1000
scene.render.resolution_percentage = 100
