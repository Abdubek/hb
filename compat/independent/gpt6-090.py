import bpy
import math
from mathutils import Vector

# Open-cab utility tractor; the engine and front axle point along +X.
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)

def material(name, color, metallic=0.0, roughness=0.45):
    m = bpy.data.materials.new(name)
    m.diffuse_color = (*color, 1)
    m.use_nodes = True
    shader = m.node_tree.nodes.get('Principled BSDF')
    shader.inputs['Base Color'].default_value = (*color, 1)
    shader.inputs['Metallic'].default_value = metallic
    shader.inputs['Roughness'].default_value = roughness
    return m

green = material('Farm green enamel', (0.12, 0.34, 0.075), 0.3)
yellow = material('Yellow wheel enamel', (0.91, 0.60, 0.045), 0.35)
rubber = material('Agricultural rubber', (0.023, 0.029, 0.023), 0, 0.9)
steel = material('Dark chassis steel', (0.10, 0.13, 0.12), 0.65)
seatmat = material('Black vinyl seat', (0.045, 0.047, 0.040), 0, 0.65)
silver = material('Grille and hardware', (0.49, 0.54, 0.51), 0.75)
lens = material('Cream headlamp glass', (0.94, 0.92, 0.73), 0.15, 0.2)
ground = material('Neutral ground', (0.29, 0.27, 0.22), 0, 0.9)

def box(name, location, size, mat, bevel=0.035):
    bpy.ops.mesh.primitive_cube_add(size=1, location=location)
    obj = bpy.context.object
    obj.name = name
    obj.dimensions = size
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    obj.data.materials.append(mat)
    if bevel:
        mod = obj.modifiers.new('Rounded edges', 'BEVEL')
        mod.width = bevel
        mod.segments = 2
        obj.modifiers.new('Weighted normals', 'WEIGHTED_NORMAL')
    return obj

def cylinder(name, location, radius, depth, mat, rotation=(0, 0, 0)):
    bpy.ops.mesh.primitive_cylinder_add(vertices=32, radius=radius, depth=depth,
                                      location=location, rotation=rotation)
    obj = bpy.context.object
    obj.name = name
    obj.data.materials.append(mat)
    mod = obj.modifiers.new('Rounded cylinder edges', 'BEVEL')
    mod.width = min(0.04, radius * 0.2)
    mod.segments = 2
    obj.modifiers.new('Weighted normals', 'WEIGHTED_NORMAL')
    return obj

def rod(name, start, end, radius, mat):
    a, b = Vector(start), Vector(end)
    obj = cylinder(name, (a + b) / 2, radius, (b - a).length, mat)
    obj.rotation_euler = (b - a).to_track_quat('Z', 'Y').to_euler()
    return obj

box('Main longitudinal chassis', (0.05, 0, 0.89), (3.65, 0.72, 0.34), steel)
box('Engine block', (0.83, 0, 1.29), (1.85, 0.84, 0.53), steel)
box('Rounded engine hood', (0.85, 0, 1.85), (2.04, 1.02, 0.85), green, 0.12)
box('Front grille surround', (1.897, 0, 1.77), (0.10, 0.96, 0.72), green)
box('Recessed dark radiator', (1.954, 0, 1.77), (0.025, 0.76, 0.53), seatmat)
for i in range(9):
    box('Radiator vertical slat %02d' % i, (1.972, -0.32 + i * 0.08, 1.77), (0.025, 0.023, 0.48), silver, 0.006)
box('Front counterweight', (2.05, 0, 0.92), (0.48, 1.12, 0.34), steel)
for y in [-0.40, 0.40]:
    cylinder('Front round headlight', (1.93, y, 2.12), 0.125, 0.10, lens, (0, math.pi / 2, 0))
for side in [-1, 1]:
    box('Hood side badge', (0.94, side * 0.515, 1.91), (0.73, 0.022, 0.10), yellow, 0.01)
    for x in [0.15, 0.28, 0.41, 0.54]:
        box('Engine side ventilation slot', (x, side * 0.516, 1.69), (0.035, 0.018, 0.23), steel, 0.006)

for x, radius, half_track, width, label in [(-1.18, 1.02, 1.02, 0.51, 'Rear'), (1.48, 0.62, 0.88, 0.34, 'Front')]:
    z = radius + 0.055
    rod(label + ' axle', (x, -half_track, z), (x, half_track, z), 0.13, steel)
    for side in [-1, 1]:
        y = side * half_track
        cylinder(label + ' tire', (x, y, z), radius, width, rubber, (math.pi / 2, 0, 0))
        outer = y + side * (width / 2 + 0.01)
        cylinder(label + ' yellow rim', (x, outer, z), radius * 0.57, 0.055, yellow, (math.pi / 2, 0, 0))
        cylinder(label + ' axle hub', (x, outer + side * 0.045, z), radius * 0.20, 0.10, steel, (math.pi / 2, 0, 0))
        for i in range(18):
            a = i * math.tau / 18
            lug = box(label + ' traction lug %02d' % i,
                      (x + radius * math.sin(a), y, z + radius * math.cos(a)),
                      (radius * 0.23, width * 1.06, 0.10), rubber, 0.018)
            lug.rotation_euler[1] = a

box('Operator platform', (-0.79, 0, 1.25), (1.52, 1.38, 0.12), steel)
for side in [-1, 1]:
    box('Rear wheel fender', (-1.18, side * 0.99, 2.22), (1.73, 0.64, 0.12), green, 0.06)
    box('Inner fender shield', (-1.18, side * 0.66, 1.88), (1.30, 0.07, 0.60), green)
    box('Boarding step', (-0.26, side * 0.91, 0.84), (0.56, 0.38, 0.10), steel)
    rod('Step bracket', (-0.26, side * 0.72, 0.88), (-0.26, side * 0.65, 1.23), 0.045, steel)
    rod('Roll protection upright', (-1.62, side * 0.59, 1.31), (-1.62, side * 0.59, 3.13), 0.065, steel)
rod('Roll protection crossbar', (-1.62, -0.59, 3.13), (-1.62, 0.59, 3.13), 0.065, steel)
box('Sun canopy', (-1.00, 0, 3.24), (1.87, 1.70, 0.13), green, 0.06)
cylinder('Seat pedestal', (-1.06, 0, 1.56), 0.13, 0.51, steel)
box('Seat cushion', (-1.04, 0, 1.83), (0.65, 0.69, 0.16), seatmat, 0.075)
box('Seat backrest', (-1.36, 0, 2.12), (0.15, 0.69, 0.58), seatmat, 0.07)
rod('Steering column', (-0.11, 0, 1.39), (-0.47, 0, 2.08), 0.045, steel)
bpy.ops.mesh.primitive_torus_add(major_segments=32, minor_segments=8, location=(-0.47, 0, 2.08), major_radius=0.235, minor_radius=0.024)
wheel = bpy.context.object
wheel.name = 'Steering wheel'
wheel.data.materials.append(seatmat)
normal = Vector((-0.36, 0, 0.69)).normalized()
wheel.rotation_euler = normal.to_track_quat('Z', 'Y').to_euler()
for a in [0, math.tau / 3, 2 * math.tau / 3]:
    tip = wheel.location + wheel.rotation_euler.to_matrix() @ Vector((0.22 * math.cos(a), 0.22 * math.sin(a), 0))
    rod('Steering spoke', wheel.location, tip, 0.014, steel)
cylinder('Exhaust stack', (0.42, 0.30, 2.76), 0.065, 1.20, steel)
cylinder('Exhaust rain cap', (0.42, 0.30, 3.39), 0.10, 0.035, steel)
box('Rear towing hitch', (-2.05, 0, 0.74), (0.48, 0.24, 0.14), steel)
box('Ground', (0, 0, -0.10), (200, 200, 0.20), ground, 0)
bpy.ops.object.camera_add(location=(7.5, -9, 5.7))
camera = bpy.context.object
camera.name = 'Tractor overview camera'
camera.rotation_euler = (Vector((0, 0, 1.55)) - camera.location).to_track_quat('-Z', 'Y').to_euler()
camera.data.type = 'ORTHO'
camera.data.ortho_scale = 7.3
bpy.context.scene.camera = camera
for pos, energy in [((1, -4, 7), 1400), ((-4, 3, 5), 1000)]:
    bpy.ops.object.light_add(type='AREA', location=pos)
    lamp = bpy.context.object
    lamp.data.energy = energy
    lamp.data.size = 5
    lamp.rotation_euler = (Vector((0, 0, 1.3)) - lamp.location).to_track_quat('-Z', 'Y').to_euler()
bpy.context.scene.world.color = (0.22, 0.22, 0.22)
