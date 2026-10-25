import bpy
import math
from mathutils import Vector

bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)

def material(name, color, metallic=0.0):
    m = bpy.data.materials.new(name)
    m.diffuse_color = (*color, 1)
    m.use_nodes = True
    bs = m.node_tree.nodes.get('Principled BSDF')
    bs.inputs['Base Color'].default_value = (*color, 1)
    bs.inputs['Metallic'].default_value = metallic
    bs.inputs['Roughness'].default_value = 0.38
    return m

yellow = material('Safety yellow paint', (0.96, 0.57, 0.035), 0.45)
dark = material('Dark machinery steel', (0.055, 0.075, 0.09), 0.65)
steel = material('Machined steel', (0.43, 0.49, 0.54), 0.85)
rope = material('Steel wire rope', (0.12, 0.14, 0.16), 0.8)
concrete = material('Workshop concrete', (0.28, 0.30, 0.32))

def box(name, loc, size, mat, bevel=0.025):
    bpy.ops.mesh.primitive_cube_add(size=1, location=loc)
    o = bpy.context.object
    o.name = name
    o.dimensions = size
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    o.data.materials.append(mat)
    if bevel:
        mod = o.modifiers.new('Edge radii', 'BEVEL')
        mod.width = bevel
        mod.segments = 2
    return o

def beam(name, a, b, width, depth, mat):
    v = Vector(b)-Vector(a)
    o = box(name, (Vector(a)+Vector(b))/2, (width, depth, v.length), mat)
    o.rotation_euler = v.to_track_quat('Z', 'Y').to_euler()
    return o

def cylinder(name, loc, radius, length, mat, axis='Z'):
    bpy.ops.mesh.primitive_cylinder_add(vertices=24, radius=radius, depth=length, location=loc)
    o = bpy.context.object
    o.name = name
    o.data.materials.append(mat)
    if axis == 'X':
        o.rotation_euler[1] = math.pi/2
    elif axis == 'Y':
        o.rotation_euler[0] = math.pi/2
    mod = o.modifiers.new('Rim chamfer', 'BEVEL')
    mod.width = 0.018
    mod.segments = 2
    return o

box('Factory floor', (0, 0, -0.12), (13, 11, 0.24), concrete)
# Two floor rails carry the four crane bogies along the Y direction.
for x in [-4.2, 4.2]:
    box('Rail base plate', (x, 0, 0.035), (0.32, 9, 0.07), dark)
    box('Floor rail head', (x, 0, 0.10), (0.12, 9, 0.09), steel)
    box('Long traveling end carriage', (x, 0, 0.65), (0.53, 3.9, 0.38), yellow)
    for y in [-1.55, 1.55]:
        cylinder('Crane travel wheel', (x, y, 0.40), 0.27, 0.25, dark, 'X')
        cylinder('Wheel outer flange', (x+0.14, y, 0.40), 0.30, 0.045, steel, 'X')
        box('Axle bearing housing', (x-0.20, y, 0.48), (0.17, 0.32, 0.30), dark)
        beam('Splayed gantry leg', (x, y, 0.83), (x, math.copysign(0.70, y), 6.12), 0.32, 0.34, yellow)
    box('End frame cross tie', (x, 0, 3.55), (0.25, 2.30, 0.23), yellow)
    beam('End frame diagonal brace', (x, -1.44, 1.25), (x, 0.80, 5.60), 0.13, 0.13, dark)
    box('Travel drive motor', (x+0.38, -1.25, 0.72), (0.38, 0.57, 0.35), dark)
    box('Top end crosshead', (x, 0, 6.13), (0.63, 2.0, 0.32), yellow)
    inward = x-math.copysign(1.25, x)
    beam('Span knee brace', (x, -0.72, 4.95), (inward, -0.72, 6.07), 0.18, 0.18, yellow)

# Twin built-up bridge girders leave room for the hoist ropes.
for y in [-0.70, 0.70]:
    box('Bridge girder web', (0, y, 6.36), (9.15, 0.18, 0.64), yellow)
    for z in [6.04, 6.68]:
        box('Bridge girder flange', (0, y, z), (9.3, 0.43, 0.10), yellow)
    box('Trolley running rail', (0, y, 6.77), (8.9, 0.075, 0.09), steel)
    for x in [-4.35, 4.35]:
        box('Trolley end stop', (x, y, 6.90), (0.13, 0.30, 0.27), dark)
    for x in [-3, -1.5, 0, 1.5, 3]:
        box('Girder stiffener', (x, y-0.12, 6.36), (0.06, 0.13, 0.54), yellow)

cx = 0.85
for x in [cx-0.56, cx+0.56]:
    for y in [-0.70, 0.70]:
        cylinder('Trolley rail wheel', (x, y, 6.94), 0.15, 0.15, steel, 'Y')
box('Trolley chassis', (cx, 0, 7.12), (1.62, 1.88, 0.21), dark)
cylinder('Hoist winding drum', (cx, 0, 7.42), 0.25, 1.05, steel, 'Y')
for y in [-0.56, 0.56]:
    cylinder('Drum flange', (cx, y, 7.42), 0.31, 0.07, yellow, 'Y')
box('Hoist gearbox', (cx, 0.76, 7.42), (0.57, 0.33, 0.55), yellow)
cylinder('Hoist electric motor', (cx+0.48, 0.72, 7.44), 0.19, 0.51, dark, 'X')
# Four falls run through the open space between the girders.
for dx in [-0.20, 0.20]:
    for y in [-0.28, 0.28]:
        cylinder('Suspension wire rope', (cx+dx, y, 5.0), 0.017, 3.90, rope)
cylinder('Lower sheave', (cx, 0, 3.05), 0.25, 0.61, steel, 'Y')
for y in [-0.36, 0.36]:
    box('Hook block cheek plate', (cx, y, 3.05), (0.67, 0.10, 0.59), yellow)
    cylinder('Sheave axle cap', (cx, y*1.17, 3.05), 0.10, 0.055, dark, 'Y')
cylinder('Hook swivel shank', (cx, 0, 2.62), 0.085, 0.37, steel)

# A tapered open J-hook, modeled as a beveled curve in the XZ plane.
curve = bpy.data.curves.new('Forged hook path', 'CURVE')
curve.dimensions = '3D'
curve.bevel_depth = 0.10
curve.bevel_resolution = 3
curve.resolution_u = 16
curve.use_fill_caps = True
spline = curve.splines.new('BEZIER')
points = [(0, 2.58), (-0.06, 2.37), (-0.22, 2.17), (-0.23, 1.94), (-0.08, 1.77), (0.17, 1.76), (0.35, 1.92), (0.34, 2.12)]
spline.bezier_points.add(len(points)-1)
for i, (x, z) in enumerate(points):
    p = spline.bezier_points[i]
    p.co = (cx+x, 0, z)
    p.handle_left_type = 'AUTO'
    p.handle_right_type = 'AUTO'
    p.radius = 0.30 if i == len(points)-1 else 1.0
hook = bpy.data.objects.new('Forged lifting hook', curve)
bpy.context.collection.objects.link(hook)
hook.data.materials.append(steel)
beam('Hook safety latch', (cx-0.015, 0, 2.34), (cx+0.34, 0, 2.12), 0.045, 0.06, dark)
box('Crane electrical cabinet', (-4.47, -1.05, 1.72), (0.38, 0.50, 0.80), dark)

bpy.ops.object.camera_add(location=(12, -15, 10))
cam = bpy.context.object
cam.name = 'Gantry overview camera'
cam.rotation_euler = (Vector((0, 0, 3.5))-cam.location).to_track_quat('-Z', 'Y').to_euler()
cam.data.type = 'ORTHO'
cam.data.ortho_scale = 13.5
bpy.context.scene.camera = cam
bpy.ops.object.light_add(type='AREA', location=(1, -5, 12))
bpy.context.object.data.energy = 2400
bpy.context.object.data.size = 8
bpy.context.scene.world.color = (0.3, 0.3, 0.3)
bpy.context.scene.render.resolution_x = 1100
bpy.context.scene.render.resolution_y = 1000
bpy.context.scene.render.resolution_percentage = 100
