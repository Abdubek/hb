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
    bs.inputs['Roughness'].default_value = 0.34
    return m

pipe_mat = material('Petroleum blue enamel', (0.045, 0.25, 0.32), 0.65)
steel = material('Machined steel', (0.43, 0.48, 0.52), 0.8)
red = material('Safety red wheels', (0.65, 0.035, 0.025), 0.45)
dark = material('Graphite supports', (0.075, 0.09, 0.11), 0.5)
floor_mat = material('Concrete', (0.26, 0.28, 0.29))

def cylinder(name, a, b, radius, mat, vertices=32):
    a, b = Vector(a), Vector(b)
    delta = b - a
    bpy.ops.mesh.primitive_cylinder_add(vertices=vertices, radius=radius,
                                      depth=delta.length, location=(a + b) / 2)
    obj = bpy.context.object
    obj.name = name
    obj.rotation_euler = delta.to_track_quat('Z', 'Y').to_euler()
    obj.data.materials.append(mat)
    bevel = obj.modifiers.new('Machined edge', 'BEVEL')
    bevel.width = 0.012
    bevel.segments = 2
    obj.modifiers.new('Weighted normals', 'WEIGHTED_NORMAL')
    return obj

def box(name, location, scale, mat):
    bpy.ops.mesh.primitive_cube_add(size=1, location=location)
    obj = bpy.context.object
    obj.name = name
    obj.dimensions = scale
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    obj.data.materials.append(mat)
    return obj

def elbow(name, cx, cy, start, end):
    curve = bpy.data.curves.new(name, 'CURVE')
    curve.dimensions = '3D'
    curve.bevel_depth = 0.19
    curve.bevel_resolution = 4
    curve.use_fill_caps = True
    spline = curve.splines.new('POLY')
    spline.points.add(24)
    for i, point in enumerate(spline.points):
        angle = start + (end - start) * i / 24
        point.co = (cx + 0.6 * math.cos(angle), cy + 0.6 * math.sin(angle), 1.45, 1)
    obj = bpy.data.objects.new(name, curve)
    bpy.context.collection.objects.link(obj)
    obj.data.materials.append(pipe_mat)

cylinder('Inlet straight pipe', (-4, -1.2, 1.45), (-2, -1.2, 1.45), 0.19, pipe_mat)
elbow('Long radius elbow A', -2, -0.6, -math.pi / 2, 0)
cylinder('Offset connecting spool', (-1.4, -0.6, 1.45), (-1.4, 0.6, 1.45), 0.19, pipe_mat)
elbow('Long radius elbow B', -0.8, 0.6, math.pi, math.pi / 2)
cylinder('Outlet straight pipe', (-0.8, 1.2, 1.45), (4, 1.2, 1.45), 0.19, pipe_mat)

def flange(x, y, name):
    cylinder(name, (x - 0.07, y, 1.45), (x + 0.07, y, 1.45), 0.32, steel)
    for i in range(8):
        angle = i * math.tau / 8
        yy = y + 0.255 * math.cos(angle)
        zz = 1.45 + 0.255 * math.sin(angle)
        cylinder(name + ' hex bolt', (x - 0.095, yy, zz), (x + 0.095, yy, zz), 0.033, dark, 6)

for x, y in [(-3.9, -1.2), (3.9, 1.2)]:
    flange(x, y, 'Terminal flange')

for index, (x, y) in enumerate([(-3, -1.2), (1.4, 1.2)], 1):
    prefix = 'Gate valve %d ' % index
    cylinder(prefix + 'body', (x - 0.33, y, 1.45), (x + 0.33, y, 1.45), 0.28, pipe_mat)
    flange(x - 0.36, y, prefix + 'inlet flange')
    flange(x + 0.36, y, prefix + 'outlet flange')
    cylinder(prefix + 'bonnet', (x, y, 1.45), (x, y, 1.95), 0.16, pipe_mat)
    cylinder(prefix + 'packing collar', (x, y, 1.92), (x, y, 2.03), 0.21, steel)
    cylinder(prefix + 'exposed stem', (x, y, 2.0), (x, y, 2.48), 0.055, steel)
    bpy.ops.mesh.primitive_torus_add(major_segments=48, minor_segments=10,
        location=(x, y, 2.45), major_radius=0.39, minor_radius=0.045)
    wheel = bpy.context.object
    wheel.name = prefix + 'handwheel rim'
    wheel.data.materials.append(red)
    for face in wheel.data.polygons:
        face.use_smooth = True
    cylinder(prefix + 'wheel hub', (x, y, 2.39), (x, y, 2.51), 0.09, red)
    for i in range(5):
        angle = math.tau * i / 5
        cylinder(prefix + 'wheel spoke', (x, y, 2.45),
                 (x + 0.39 * math.cos(angle), y + 0.39 * math.sin(angle), 2.45), 0.026, red, 12)

for x, y in [(-3.65, -1.2), (-0.5, 1.2), (3.25, 1.2)]:
    box('Anchored support foot', (x, y, 0.12), (0.65, 0.65, 0.18), dark)
    cylinder('Pipe support post', (x, y, 0.2), (x, y, 1.19), 0.09, dark)
    box('Pipe saddle', (x, y, 1.2), (0.35, 0.48, 0.12), steel)
box('Concrete equipment pad', (0, 0, -0.12), (9.5, 5.4, 0.24), floor_mat)
bpy.ops.object.camera_add(location=(8, -10, 8))
camera = bpy.context.object
camera.name = 'Assembly overview camera'
camera.rotation_euler = (Vector((0, 0, 1.15)) - camera.location).to_track_quat('-Z', 'Y').to_euler()
camera.data.type = 'ORTHO'
camera.data.ortho_scale = 11
bpy.context.scene.camera = camera
for location, power, size in [((0, -4, 9), 1700, 7), ((3, 5, 7), 1300, 5)]:
    bpy.ops.object.light_add(type='AREA', location=location)
    light = bpy.context.object
    light.data.energy = power
    light.data.shape = 'DISK'
    light.data.size = size
    light.rotation_euler = (Vector((0, 0, 1)) - light.location).to_track_quat('-Z', 'Y').to_euler()
bpy.context.scene.world.color = (0.22, 0.22, 0.22)
