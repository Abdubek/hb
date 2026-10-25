import bpy
from mathutils import Vector
from math import radians

# Independent picnic table scene; dimensions are in metres.
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

cedar = material('Warm cedar', (0.43, 0.21, 0.085))
lightwood = material('Alternate cedar boards', (0.57, 0.31, 0.13))
framewood = material('Structural cedar', (0.32, 0.145, 0.055))
steel = material('Galvanized fasteners', (0.48, 0.53, 0.57), 0.8, 0.3)
ground = material('Muted stone paving', (0.25, 0.29, 0.27))

def box(name, location, dimensions, mat, bevel=0.008):
    bpy.ops.mesh.primitive_cube_add(size=1, location=location)
    obj = bpy.context.object
    obj.name = name
    obj.dimensions = dimensions
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    obj.data.materials.append(mat)
    if bevel:
        mod = obj.modifiers.new('Soft timber edges', 'BEVEL')
        mod.width = bevel
        mod.segments = 2
        obj.modifiers.new('Weighted corner normals', 'WEIGHTED_NORMAL')
    return obj

def beam(name, start, end, width, depth, mat):
    delta = Vector(end) - Vector(start)
    obj = box(name, (Vector(start) + Vector(end)) / 2,
              (width, depth, delta.length), mat)
    obj.rotation_mode = 'QUATERNION'
    obj.rotation_quaternion = delta.to_track_quat('Z', 'Y')
    return obj

def bolt(name, location, axis):
    bpy.ops.mesh.primitive_cylinder_add(vertices=6, radius=0.014,
                                       depth=0.009, location=location)
    obj = bpy.context.object
    obj.name = name
    obj.rotation_mode = 'QUATERNION'
    obj.rotation_quaternion = Vector(axis).to_track_quat('Z', 'Y')
    obj.data.materials.append(steel)

# Five full-length top planks with visible drainage gaps.
for i in range(5):
    y = (i - 2) * 0.172
    box('Tabletop plank %02d' % (i + 1), (0, y, 0.79),
        (2.4, 0.162, 0.055), cedar if i % 2 else lightwood)
    for x in (-0.84, 0.84):
        bolt('Top carriage bolt', (x, y, 0.821), (0, 0, 1))

# Each bench is fixed to the same transverse frame as the tabletop.
for side in (-1, 1):
    for i in range(2):
        y = side * 0.79 + (i - 0.5) * 0.174
        box('Bench %s plank %d' % (side, i + 1), (0, y, 0.445),
            (2.4, 0.164, 0.05), lightwood if i else cedar)
        for x in (-0.84, 0.84):
            bolt('Bench fixing bolt', (x, y, 0.474), (0, 0, 1))

for x in (-0.84, 0.84):
    box('Upper transverse bearer', (x, 0, 0.717), (0.11, 0.91, 0.09), framewood)
    box('Shared bench support', (x, 0, 0.365), (0.12, 1.94, 0.11), framewood)
    for side in (-1, 1):
        beam('Splayed A-frame leg', (x, side * 0.61, 0.055),
             (x, side * 0.28, 0.728), 0.105, 0.105, framewood)
        bolt('Leg joint bolt', (x + 0.065, side * 0.46, 0.365), (1, 0, 0))

box('Longitudinal lower stretcher', (0, 0, 0.365), (1.79, 0.095, 0.105), framewood)
for side in (-1, 1):
    beam('Under-table diagonal brace', (side * 0.78, 0, 0.405),
         (side * 0.24, 0, 0.715), 0.065, 0.065, framewood)
box('Paving slab', (0, 0, -0.055), (3.8, 3.3, 0.11), ground, 0.025)

world = bpy.data.worlds.new('Picnic table world')
bpy.context.scene.world = world
world.use_nodes = True
world.node_tree.nodes['Background'].inputs[0].default_value = (0.65, 0.73, 0.85, 1)
world.node_tree.nodes['Background'].inputs[1].default_value = 0.5
bpy.ops.object.light_add(type='AREA', location=(1.5, -2.5, 4.5))
bpy.context.object.name = 'Large soft key light'
bpy.context.object.data.energy = 550
bpy.context.object.data.shape = 'DISK'
bpy.context.object.data.size = 4
bpy.ops.object.camera_add(location=(3.5, -3.8, 2.6))
camera = bpy.context.object
camera.name = 'Picnic table overview'
camera.rotation_euler = (Vector((0, 0, 0.42)) - camera.location).to_track_quat('-Z', 'Y').to_euler()
camera.data.type = 'ORTHO'
camera.data.ortho_scale = 4.5
bpy.context.scene.camera = camera
bpy.context.scene.render.resolution_x = 1200
bpy.context.scene.render.resolution_y = 900
bpy.context.scene.render.resolution_percentage = 100
