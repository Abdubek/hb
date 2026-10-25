import bpy
import math
from mathutils import Vector

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

wood = material('Warm walnut', (0.23, 0.095, 0.043), roughness=0.42)
edge = material('Dark walnut edges', (0.095, 0.037, 0.018))
metal = material('Brushed aluminum', (0.43, 0.48, 0.53), 0.8, 0.28)
black = material('Microphone graphite', (0.018, 0.023, 0.028), 0.35, 0.4)
matte = material('Reading surface charcoal', (0.035, 0.045, 0.05), roughness=0.9)
paper = material('Warm white paper', (0.88, 0.86, 0.77), roughness=0.95)
floor = material('Stone floor', (0.26, 0.29, 0.32), roughness=0.8)

def box(name, location, size, mat, bevel=0.015):
    bpy.ops.mesh.primitive_cube_add(size=1, location=location)
    obj = bpy.context.object
    obj.name = name
    obj.dimensions = size
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    obj.data.materials.append(mat)
    if bevel:
        mod = obj.modifiers.new('Edge rounding', 'BEVEL')
        mod.width = bevel
        mod.segments = 3
        obj.modifiers.new('Weighted normals', 'WEIGHTED_NORMAL')
    return obj

def rod(name, start, end, radius, mat):
    delta = Vector(end) - Vector(start)
    bpy.ops.mesh.primitive_cylinder_add(vertices=24, radius=radius, depth=delta.length, location=(Vector(start) + Vector(end)) / 2)
    obj = bpy.context.object
    obj.name = name
    obj.rotation_euler = delta.to_track_quat('Z', 'Y').to_euler()
    obj.data.materials.append(mat)
    for face in obj.data.polygons:
        face.use_smooth = True
    return obj

box('Display floor', (0, 0, -0.065), (4.5, 4, 0.12), floor)
box('Weighted podium plinth', (0, 0, 0.055), (1.05, 0.8, 0.11), black, 0.035)
box('Plinth aluminum reveal', (0, 0, 0.123), (0.96, 0.71, 0.028), metal, 0.01)
# Audience is on negative Y; the speaker stands on positive Y.
box('Audience front panel', (0, -0.245, 0.665), (0.78, 0.09, 1.07), wood)
for x in (-0.345, 0.345):
    box('Side cheek left' if x < 0 else 'Side cheek right', (x, 0.035, 0.665), (0.09, 0.55, 1.07), wood)
box('Interior lower shelf', (0, 0.025, 0.39), (0.62, 0.48, 0.045), edge)
box('Interior upper shelf', (0, 0.025, 0.85), (0.62, 0.48, 0.045), edge)
for x in (-0.30, 0.30):
    box('Front vertical metal inlay', (x, -0.294, 0.69), (0.014, 0.008, 0.91), metal, 0.002)
box('Front emblem plate', (0, -0.299, 0.92), (0.32, 0.015, 0.15), metal, 0.012)

# Local deck coordinates keep every accessory seated on the tilted top.
slope = math.radians(-13)
deck_center = Vector((0, 0, 1.22))
rotation = __import__('mathutils').Matrix.Rotation(slope, 4, 'X')
def deck_point(x, y, z):
    return deck_center + rotation.to_3x3() @ Vector((x, y, z))

def deck_box(name, local_center, size, mat, bevel=0.01):
    obj = box(name, deck_point(*local_center), size, mat, bevel)
    obj.rotation_euler.x = slope
    return obj

deck_box('Sloping walnut reading desk', (0, 0, 0), (1.05, 0.76, 0.07), wood, 0.025)
deck_box('Inset reading pad', (0, 0.015, 0.04), (0.83, 0.58, 0.012), matte)
deck_box('Raised speaker edge paper stop', (0, 0.335, 0.078), (0.95, 0.035, 0.075), edge)
deck_box('Paper stop metal cap', (0, 0.335, 0.12), (0.91, 0.04, 0.012), metal, 0.004)
deck_box('Lecture notes', (0.04, 0.075, 0.050), (0.30, 0.39, 0.006), paper, 0.002)
for i in range(8):
    deck_box('Printed note line %02d' % i, (0.035, -0.065 + i * 0.031, 0.054), (0.21 if i else 0.24, 0.003, 0.001), matte, 0)

mount = deck_point(-0.39, -0.23, 0.055)
normal = rotation.to_3x3() @ Vector((0, 0, 1))
rod('Microphone socket', mount - normal * 0.014, mount + normal * 0.035, 0.043, metal)
points = [mount + normal * 0.03, mount + Vector((0, 0, 0.17)), mount + Vector((0.02, 0.06, 0.31)), mount + Vector((0.13, 0.21, 0.36))]
curve = bpy.data.curves.new('Flexible microphone stem curve', 'CURVE')
curve.dimensions = '3D'
curve.resolution_u = 16
curve.bevel_depth = 0.012
curve.bevel_resolution = 3
spline = curve.splines.new('BEZIER')
spline.bezier_points.add(len(points) - 1)
for point, coordinate in zip(spline.bezier_points, points):
    point.co = coordinate
    point.handle_left_type = 'AUTO'
    point.handle_right_type = 'AUTO'
stem = bpy.data.objects.new('Gooseneck microphone stem', curve)
bpy.context.collection.objects.link(stem)
stem.data.materials.append(black)
direction = (points[-1] - points[-2]).normalized()
rod('Microphone capsule', points[-1], points[-1] + direction * 0.10, 0.028, black)
rod('Microphone grille', points[-1] + direction * 0.075, points[-1] + direction * 0.13, 0.032, metal)

bpy.ops.object.camera_add(location=(2.6, -3.2, 2.65))
camera = bpy.context.object
camera.name = 'Podium presentation camera'
camera.rotation_euler = (Vector((0, 0, 0.85)) - camera.location).to_track_quat('-Z', 'Y').to_euler()
camera.data.type = 'ORTHO'
camera.data.ortho_scale = 2.6
bpy.context.scene.camera = camera
bpy.ops.object.light_add(type='AREA', location=(1.5, -2, 4))
bpy.context.object.name = 'Large studio light'
bpy.context.object.data.energy = 500
bpy.context.object.data.size = 3
bpy.context.scene.world.color = (0.25, 0.25, 0.25)
bpy.context.scene.render.resolution_x = 1000
bpy.context.scene.render.resolution_y = 1000
