import bpy
from mathutils import Vector

# Independent scene: a timber garden pergola with an open slatted roof.
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)

def material(name, color, roughness=0.5, metallic=0.0):
    mat = bpy.data.materials.new(name)
    mat.diffuse_color = (*color, 1)
    mat.use_nodes = True
    shader = mat.node_tree.nodes.get('Principled BSDF')
    shader.inputs['Base Color'].default_value = (*color, 1)
    shader.inputs['Roughness'].default_value = roughness
    shader.inputs['Metallic'].default_value = metallic
    return mat

wood = material('Warm cedar timber', (0.38, 0.17, 0.065))
endwood = material('Cedar post caps', (0.49, 0.25, 0.10))
steel = material('Black galvanized brackets', (0.045, 0.055, 0.06), 0.35, 0.75)
stone = material('Warm limestone paving', (0.52, 0.49, 0.42), 0.85)
grass = material('Garden green', (0.16, 0.24, 0.105), 0.95)
soil = material('Dark planting soil', (0.095, 0.065, 0.035), 1.0)
leaves = material('Clipped evergreen foliage', (0.075, 0.19, 0.07), 0.9)

def box(name, location, dimensions, mat, bevel=0.025):
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
    direction = Vector(end) - Vector(start)
    obj = box(name, (Vector(start) + Vector(end)) / 2,
              (width, depth, direction.length), mat, 0.012)
    obj.rotation_euler = direction.to_track_quat('Z', 'Y').to_euler()
    return obj

box('Garden ground', (0, 0, -0.13), (9, 8, 0.22), grass, 0.05)
box('Patio foundation', (0, 0, 0.005), (5.9, 4.9, 0.16), stone)
for i in range(7):
    for j in range(6):
        box('Patio paver %02d %02d' % (i, j),
            ((i - 3) * 0.82, (j - 2.5) * 0.79, 0.105),
            (0.80, 0.77, 0.06), stone, 0.009)

for x in (-2.15, 2.15):
    for y in (-1.65, 1.65):
        tag = '%s %s' % ('West' if x < 0 else 'East', 'South' if y < 0 else 'North')
        box(tag + ' footing plate', (x, y, 0.16), (0.40, 0.40, 0.05), steel, 0.008)
        box(tag + ' post shoe', (x, y, 0.26), (0.29, 0.29, 0.18), steel, 0.01)
        box(tag + ' cedar post', (x, y, 1.59), (0.24, 0.24, 2.72), wood)
        box(tag + ' post cap', (x, y, 2.99), (0.29, 0.29, 0.09), endwood)
        sx = -1 if x > 0 else 1
        sy = -1 if y > 0 else 1
        beam(tag + ' longitudinal knee brace', (x, y, 2.21),
             (x + sx * 0.66, y, 2.85), 0.13, 0.13, wood)
        beam(tag + ' transverse knee brace', (x, y, 2.19),
             (x, y + sy * 0.59, 2.86), 0.13, 0.13, wood)

for y in (-1.65, 1.65):
    box('Long perimeter beam %.2f' % y, (0, y, 2.91), (5.25, 0.20, 0.30), wood)
for x in (-2.15, 2.15):
    box('Cross perimeter beam %.2f' % x, (x, 0, 2.91), (0.20, 4.25, 0.30), wood)
for i in range(15):
    x = (i - 7) * 0.35
    box('Overhead cedar slat %02d' % (i + 1), (x, 0, 3.16),
        (0.115, 4.50, 0.20), endwood, 0.012)

for x in (-2.78, 2.78):
    box('Garden planter', (x, 2.50, 0.34), (0.80, 0.80, 0.55), wood)
    box('Planter soil', (x, 2.50, 0.625), (0.70, 0.70, 0.03), soil, 0.005)
    bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=2, radius=0.48, location=(x, 2.50, 0.97))
    bush = bpy.context.object
    bush.name = 'Evergreen planter shrub'
    bush.scale = (0.82, 0.82, 1.0)
    bush.data.materials.append(leaves)

scene = bpy.context.scene
scene.world.color = (0.22, 0.22, 0.22)
bpy.ops.object.light_add(type='AREA', location=(1, -3, 8))
bpy.context.object.name = 'Large daylight softbox'
bpy.context.object.data.energy = 1800
bpy.context.object.data.shape = 'DISK'
bpy.context.object.data.size = 6
bpy.ops.object.camera_add(location=(8, -10, 7))
camera = bpy.context.object
camera.name = 'Pergola overview camera'
camera.rotation_euler = (Vector((0, 0, 1.35)) - camera.location).to_track_quat('-Z', 'Y').to_euler()
camera.data.type = 'ORTHO'
camera.data.ortho_scale = 10.3
scene.camera = camera
scene.render.resolution_x = 1200
scene.render.resolution_y = 1000
scene.render.resolution_percentage = 100
