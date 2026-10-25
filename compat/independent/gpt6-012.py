import bpy
import math
from mathutils import Vector

bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)

def material(name, color, metallic=0.0, roughness=0.4):
    m = bpy.data.materials.new(name)
    m.diffuse_color = (*color, 1)
    m.use_nodes = True
    p = m.node_tree.nodes.get('Principled BSDF')
    p.inputs['Base Color'].default_value = (*color, 1)
    p.inputs['Metallic'].default_value = metallic
    p.inputs['Roughness'].default_value = roughness
    return m

def finish(obj, name, mat, bevel=0.0):
    obj.name = name
    obj.data.materials.append(mat)
    if bevel:
        mod = obj.modifiers.new('Manufactured edge bevel', 'BEVEL')
        mod.width, mod.segments = bevel, 2
        obj.modifiers.new('Weighted normals', 'WEIGHTED_NORMAL')
    return obj

def box(name, location, dimensions, mat, bevel=0.03):
    bpy.ops.mesh.primitive_cube_add(size=1, location=location)
    obj = bpy.context.object
    obj.dimensions = dimensions
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    return finish(obj, name, mat, bevel)

def cylinder(name, location, radius, depth, mat, front=False, vertices=48):
    bpy.ops.mesh.primitive_cylinder_add(vertices=vertices, radius=radius, depth=depth, location=location)
    obj = bpy.context.object
    if front:
        obj.rotation_euler[0] = math.pi / 2
    return finish(obj, name, mat, 0.008)

def ring(name, y, radius, thickness, mat):
    bpy.ops.mesh.primitive_torus_add(major_segments=48, minor_segments=8, location=(-0.22, y, 1.02), major_radius=radius, minor_radius=thickness, rotation=(math.pi / 2, 0, 0))
    return finish(bpy.context.object, name, mat)

black = material('Black anodized metal', (0.027, 0.033, 0.04), 0.65, 0.3)
rubber = material('Textured grip rubber', (0.043, 0.048, 0.052), 0.0, 0.78)
silver = material('Satin silver top plate', (0.56, 0.6, 0.63), 0.8, 0.26)
dark = material('Optical interior black', (0.005, 0.008, 0.012), 0.0, 0.32)
glass = material('Blue coated lens glass', (0.025, 0.11, 0.19), 0.65, 0.1)
white = material('Ivory control markings', (0.86, 0.86, 0.79))
red = material('Record button red', (0.7, 0.025, 0.017), 0.15)
screen = material('Rear screen glass', (0.025, 0.065, 0.078), 0.3, 0.16)
floor = material('Studio surface', (0.22, 0.25, 0.28))

box('Main camera chassis', (0, 0, 1.0), (2.95, 0.91, 1.75), black, 0.12)
box('Front leatherette panel', (0, -0.466, 0.99), (2.77, 0.05, 1.34), rubber, 0.07)
box('Silver upper deck', (0, 0, 1.84), (2.91, 0.94, 0.19), silver, 0.055)
box('Bottom plate', (0, 0, 0.15), (2.85, 0.88, 0.16), black)
box('Deep right hand grip', (1.11, -0.39, 0.96), (0.6, 0.65, 1.48), rubber, 0.16)
for z in (0.5, 0.69, 0.88, 1.07, 1.26):
    box('Grip traction ridge', (1.18, -0.719, z), (0.28, 0.025, 0.028), black, 0.01)
box('Viewfinder housing', (-0.22, 0.04, 2.0), (0.82, 0.72, 0.36), black, 0.07)
box('Viewfinder rear eyecup', (-0.22, 0.47, 1.98), (0.57, 0.19, 0.3), rubber)
box('Viewfinder glass', (-0.22, 0.57, 1.98), (0.35, 0.015, 0.16), glass, 0.01)
box('Hot shoe base', (-0.22, 0.08, 2.2), (0.4, 0.39, 0.035), dark, 0.008)
for x in (-0.43, -0.01):
    box('Hot shoe rail', (x, 0.08, 2.23), (0.055, 0.4, 0.055), silver, 0.009)

# Stepped lens barrel projects toward negative Y.
cylinder('Lens bayonet mount', (-0.22, -0.52, 1.02), 0.69, 0.13, silver, True)
cylinder('Lens rear barrel', (-0.22, -0.72, 1.02), 0.63, 0.32, black, True)
cylinder('Zoom grip', (-0.22, -1.01, 1.02), 0.66, 0.3, rubber, True)
cylinder('Forward lens barrel', (-0.22, -1.29, 1.02), 0.59, 0.29, black, True)
cylinder('Focus grip', (-0.22, -1.46, 1.02), 0.61, 0.14, rubber, True)
cylinder('Recessed lens interior', (-0.22, -1.546, 1.02), 0.56, 0.04, dark, True)
cylinder('Front optical element', (-0.22, -1.573, 1.02), 0.45, 0.012, glass, True)
ring('Front protective rim', -1.59, 0.57, 0.032, black)
ring('Optical retaining ring', -1.586, 0.472, 0.014, silver)
ring('Lens accent band', -0.84, 0.635, 0.012, silver)
for j in range(40):
    a = 2 * math.pi * j / 40
    for y, radius, length in ((-1.01, 0.661, 0.25), (-1.46, 0.611, 0.105)):
        obj = box('Lens grip knurl', (-0.22 + radius * math.cos(a), y, 1.02 + radius * math.sin(a)), (0.023, length, 0.018), black, 0.004)
        obj.rotation_euler[1] = math.pi / 2 - a

for name, x, y, radius in [('Mode dial', -1.0, 0.03, 0.26), ('Exposure dial', 0.63, 0.15, 0.23)]:
    cylinder(name, (x, y, 2.0), radius, 0.15, black, vertices=32)
    for j in range(12):
        a = j * math.tau / 12
        mark = box(name + ' index', (x + radius * 0.76 * math.cos(a), y + radius * 0.76 * math.sin(a), 2.079), (0.047, 0.015, 0.008), white, 0)
        mark.rotation_euler[2] = a
cylinder('Shutter button bezel', (1.14, -0.23, 1.99), 0.15, 0.12, black)
cylinder('Shutter release', (1.14, -0.23, 2.067), 0.107, 0.045, silver)
cylinder('Record button', (1.2, 0.22, 1.957), 0.075, 0.045, red, vertices=24)
cylinder('Lens release button', (0.59, -0.514, 0.66), 0.085, 0.05, silver, True, 24)
box('Front badge', (-1.03, -0.503, 1.52), (0.39, 0.025, 0.13), silver, 0.012)
box('Rear LCD frame', (-0.28, 0.479, 0.98), (1.83, 0.09, 1.15), rubber, 0.06)
box('Rear LCD glass', (-0.28, 0.53, 0.98), (1.62, 0.018, 0.94), screen, 0.03)
cylinder('Rear control wheel', (1.04, 0.49, 0.96), 0.21, 0.1, black, True, 24)
for z in (1.42, 0.53):
    cylinder('Rear function button', (1.04, 0.49, z), 0.075, 0.08, silver, True, 20)
for x in (-1.51, 1.51):
    bpy.ops.mesh.primitive_torus_add(major_segments=16, minor_segments=6, major_radius=0.1, minor_radius=0.027, location=(x, 0.02, 1.63), rotation=(math.pi / 2, 0, 0))
    finish(bpy.context.object, 'Strap attachment loop', silver)
box('Studio floor', (0, 0, -0.035), (200, 200, 0.1), floor, 0)

bpy.ops.object.camera_add(location=(4.2, -6.6, 4.1))
cam = bpy.context.object
cam.name = 'Camera product three quarter view'
cam.rotation_euler = (Vector((0, -0.4, 1.1)) - cam.location).to_track_quat('-Z', 'Y').to_euler()
cam.data.type, cam.data.ortho_scale = 'ORTHO', 4.7
bpy.context.scene.camera = cam
for name, loc, energy, size in [('Large key', (1, -4, 6), 1000, 4), ('Left fill', (-4, -2, 3), 650, 3), ('Rear rim', (1, 4, 5), 900, 3)]:
    bpy.ops.object.light_add(type='AREA', location=loc)
    obj = bpy.context.object
    obj.name = name
    obj.data.energy, obj.data.size = energy, size
    obj.rotation_euler = (Vector((0, -0.3, 1)) - obj.location).to_track_quat('-Z', 'Y').to_euler()
scene = bpy.context.scene
scene.world = bpy.data.worlds.new('Camera studio world')
scene.world.use_nodes = True
scene.world.node_tree.nodes['Background'].inputs[0].default_value = (0.25, 0.25, 0.25, 1)
scene.render.resolution_x, scene.render.resolution_y = 1000, 800
