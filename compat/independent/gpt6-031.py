import bpy
import math
from mathutils import Vector

# Railway signal beside a short ballasted track.
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)

def material(name, color, metallic=0.0, roughness=0.55, emission=0.0):
    m = bpy.data.materials.new(name)
    m.diffuse_color = (*color, 1)
    m.use_nodes = True
    bs = m.node_tree.nodes.get('Principled BSDF')
    bs.inputs['Base Color'].default_value = (*color, 1)
    bs.inputs['Metallic'].default_value = metallic
    bs.inputs['Roughness'].default_value = roughness
    if emission:
        bs.inputs['Emission Color'].default_value = (*color, 1)
        bs.inputs['Emission Strength'].default_value = emission
    return m

def box(name, loc, scale, mat, bevel=0.0):
    bpy.ops.mesh.primitive_cube_add(size=1, location=loc)
    obj = bpy.context.object
    obj.name = name
    obj.dimensions = scale
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    obj.data.materials.append(mat)
    if bevel:
        mod = obj.modifiers.new('Soft manufactured edges', 'BEVEL')
        mod.width, mod.segments = bevel, 2
        obj.modifiers.new('Weighted normals', 'WEIGHTED_NORMAL')
    return obj

def rod(name, a, b, radius, mat, vertices=16):
    direction = Vector(b) - Vector(a)
    bpy.ops.mesh.primitive_cylinder_add(vertices=vertices, radius=radius,
        depth=direction.length, location=(Vector(a) + Vector(b)) / 2)
    obj = bpy.context.object
    obj.name = name
    obj.rotation_euler = direction.to_track_quat('Z', 'Y').to_euler()
    obj.data.materials.append(mat)
    return obj

steel = material('Rail steel', (0.34, 0.38, 0.42), 0.85, 0.27)
rust = material('Oxidized rail webs', (0.24, 0.13, 0.07), 0.5)
wood = material('Dark timber sleepers', (0.16, 0.10, 0.065))
ballast = material('Gray ballast bed', (0.29, 0.31, 0.32))
ground = material('Earth', (0.23, 0.28, 0.19))
black = material('Signal black enamel', (0.022, 0.028, 0.032), 0.3)
silver = material('Galvanized mast', (0.57, 0.61, 0.62), 0.65)
concrete = material('Concrete foundation', (0.49, 0.49, 0.45))
white = material('Identification plate', (0.88, 0.89, 0.82))
red = material('Unlit red lens', (0.20, 0.008, 0.005), roughness=0.22)
amber = material('Unlit amber lens', (0.25, 0.085, 0.003), roughness=0.22)
green = material('Active green lens', (0.025, 0.85, 0.13), roughness=0.2, emission=2.5)
box('Ground display slab', (0, 0, -0.16), (7, 12, 0.3), ground, 0.12)
box('Raised ballast bed', (0, 0, 0.05), (3.3, 11, 0.25), ballast, 0.12)
for i in range(17):
    y = -4.8 + i * 0.6
    box('Timber sleeper %02d' % i, (0, y, 0.23), (2.6, 0.24, 0.19), wood, 0.025)
    for x in (-0.75, 0.75):
        box('Rail fastening plate', (x, y, 0.35), (0.30, 0.30, 0.05), rust)
        for dx in (-0.115, 0.115):
            rod('Fastening bolt', (x + dx, y, 0.375), (x + dx, y, 0.415), 0.028, steel, 8)
for x in (-0.75, 0.75):
    box('Rail foot', (x, 0, 0.39), (0.19, 10.8, 0.055), rust)
    box('Rail upright web', (x, 0, 0.48), (0.065, 10.8, 0.16), rust)
    box('Polished running rail head', (x, 0, 0.58), (0.12, 10.8, 0.075), steel, 0.017)

sx, sy = 2.15, 1.1
box('Mast concrete footing', (sx, sy, 0.15), (0.75, 0.75, 0.4), concrete, 0.045)
box('Mast base flange', (sx, sy, 0.38), (0.43, 0.43, 0.07), steel, 0.02)
rod('Signal mast', (sx, sy, 0.4), (sx, sy, 4.15), 0.085, silver)
box('Signal rear enclosure', (sx, sy, 3.95), (0.65, 0.34, 1.72), black, 0.1)
box('Signal face surround', (sx, sy - 0.2, 3.95), (0.84, 0.09, 1.95), black, 0.16)
for label, z, mat in [('Red', 4.53, red), ('Amber', 3.95, amber), ('Green', 3.37, green)]:
    rod(label + ' bezel', (sx, sy - 0.24, z), (sx, sy - 0.31, z), 0.215, silver, 32)
    rod(label + ' lens', (sx, sy - 0.31, z), (sx, sy - 0.34, z), 0.177, mat, 32)
    box(label + ' projecting rain visor', (sx, sy - 0.43, z + 0.235), (0.48, 0.47, 0.055), black, 0.02)
box('Signal number plate', (sx, sy - 0.13, 2.65), (0.46, 0.05, 0.27), white, 0.015)
bpy.ops.object.text_add(location=(sx, sy - 0.161, 2.65), rotation=(math.pi / 2, 0, 0))
text = bpy.context.object
text.name = 'Signal identification S12'
text.data.body, text.data.align_x, text.data.align_y, text.data.size = 'S12', 'CENTER', 'CENTER', 0.18
text.data.materials.append(black)
for dx in (-0.25, 0.25):
    rod('Access ladder upright', (sx + dx, sy + 0.36, 0.35), (sx + dx, sy + 0.36, 4.4), 0.025, silver)
for i in range(13):
    z = 0.6 + i * 0.29
    rod('Ladder rung', (sx - 0.25, sy + 0.36, z), (sx + 0.25, sy + 0.36, z), 0.021, silver)
box('Trackside electrical cabinet', (2.5, 3, 0.65), (0.72, 0.48, 1.1), silver, 0.045)
box('Cabinet door', (2.5, 2.748, 0.65), (0.62, 0.03, 0.94), concrete, 0.02)
box('Cabinet handle', (2.72, 2.71, 0.65), (0.025, 0.035, 0.15), black)

scene = bpy.context.scene
scene.world.color = (0.23, 0.23, 0.23)
bpy.ops.object.light_add(type='AREA', location=(2, -4, 10))
bpy.context.object.data.energy, bpy.context.object.data.shape, bpy.context.object.data.size = 1800, 'DISK', 8
bpy.ops.object.camera_add(location=(10, -15, 10))
camera = bpy.context.object
camera.rotation_euler = (Vector((0.3, 0, 1.3)) - camera.location).to_track_quat('-Z', 'Y').to_euler()
camera.data.type, camera.data.ortho_scale = 'ORTHO', 15
scene.camera = camera
scene.render.resolution_x, scene.render.resolution_y, scene.render.resolution_percentage = 1100, 900, 100
