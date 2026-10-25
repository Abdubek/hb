import bpy
import math
from mathutils import Vector

bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)

def material(name, color, metallic=0.0, roughness=0.45):
    m = bpy.data.materials.new(name)
    m.diffuse_color = (*color, 1)
    m.use_nodes = True
    bs = m.node_tree.nodes.get('Principled BSDF')
    bs.inputs['Base Color'].default_value = (*color, 1)
    bs.inputs['Metallic'].default_value = metallic
    bs.inputs['Roughness'].default_value = roughness
    return m

shell = material('Graphite polymer', (0.055, 0.065, 0.085), 0.25)
leather = material('Soft charcoal cushions', (0.016, 0.019, 0.026), 0, 0.8)
metal = material('Brushed aluminum', (0.42, 0.49, 0.56), 0.8, 0.3)
accent = material('Copper details', (0.65, 0.25, 0.09), 0.65)
stand_mat = material('Stand satin black', (0.025, 0.033, 0.041), 0.5)
floor_mat = material('Warm studio floor', (0.25, 0.28, 0.3))

def finish(obj, name, mat, bevel=0):
    obj.name = name
    obj.data.materials.append(mat)
    if bevel:
        mod = obj.modifiers.new('Soft manufactured edges', 'BEVEL')
        mod.width = bevel
        mod.segments = 3
        obj.modifiers.new('Weighted normals', 'WEIGHTED_NORMAL')
    return obj

def box(name, loc, scale, mat, bevel=0.05):
    bpy.ops.mesh.primitive_cube_add(size=1, location=loc)
    obj = bpy.context.object
    obj.dimensions = scale
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    return finish(obj, name, mat, bevel)

def cylinder(name, loc, radius, depth, mat, along_x=False):
    bpy.ops.mesh.primitive_cylinder_add(vertices=48, radius=radius, depth=depth, location=loc)
    obj = bpy.context.object
    if along_x:
        obj.rotation_euler[1] = math.pi / 2
    finish(obj, name, mat, 0.025)
    for p in obj.data.polygons:
        p.use_smooth = len(p.vertices) == 4
    return obj

def arc_band(name, radius, thickness, width, mat):
    verts, faces = [], []
    count = 48
    for i in range(count + 1):
        angle = math.pi * i / count
        for r, y in [(radius-thickness/2, -width/2),
                     (radius-thickness/2, width/2),
                     (radius+thickness/2, width/2),
                     (radius+thickness/2, -width/2)]:
            verts.append((r * math.cos(angle), y, 2.55 + r * math.sin(angle)))
    for i in range(count):
        for j in range(4):
            a, b = 4*i+j, 4*i+(j+1)%4
            faces.append((a, b, b+4, a+4))
    faces.extend([(3, 2, 1, 0), tuple(4*count+j for j in range(4))])
    mesh = bpy.data.meshes.new(name)
    mesh.from_pydata(verts, [], faces)
    mesh.update()
    obj = bpy.data.objects.new(name, mesh)
    bpy.context.collection.objects.link(obj)
    return finish(obj, name, mat, 0.025)

box('Stand weighted base', (0, 0.18, 0.14), (1.85, 1.3, 0.28), stand_mat, 0.12)
box('Base aluminum inset', (0, 0.18, 0.295), (1.45, 0.94, 0.035), metal, 0.015)
box('Stand upright', (0, 0.22, 1.91), (0.17, 0.22, 3.22), metal)
box('Headband support saddle', (0, 0, 3.55), (0.68, 0.6, 0.22), leather, 0.09)
arc_band('Continuous outer headband', 1.2, 0.12, 0.42, shell)
arc_band('Headband inner comfort padding', 1.105, 0.10, 0.36, leather)
for side, label in [(-1, 'Left'), (1, 'Right')]:
    x = side * 1.2
    box(label + ' adjustable slider', (x, 0, 2.51), (0.10, 0.24, 0.55), metal, 0.025)
    for y in [-0.39, 0.39]:
        box(label + ' fork arm', (x, y, 2.23), (0.13, 0.10, 0.63), shell, 0.04)
    box(label + ' fork bridge', (x, 0, 2.52), (0.13, 0.86, 0.12), shell)
    housing = cylinder(label + ' earcup housing', (x, 0, 1.96), 0.50, 0.31, shell, True)
    housing.scale.x = 1.18
    cylinder(label + ' outer trim', (x + side*0.17, 0, 1.96), 0.42, 0.035, accent, True)
    cylinder(label + ' outer face', (x + side*0.20, 0, 1.96), 0.38, 0.04, metal, True)
    cylinder(label + ' inset speaker fabric', (x-side*0.18, 0, 1.96), 0.34, 0.025, leather, True)
    bpy.ops.mesh.primitive_torus_add(major_segments=48, minor_segments=12,
        location=(x-side*0.23, 0, 1.96), rotation=(0, math.pi/2, 0),
        major_radius=0.35, minor_radius=0.115)
    pad = finish(bpy.context.object, label + ' oval ear cushion', leather)
    pad.scale.x = 1.22
    for p in pad.data.polygons:
        p.use_smooth = True
    cylinder(label + ' hinge cap', (x+side*0.085, 0, 2.50), 0.085, 0.045, accent, True)
box('Right earcup power button', (1.37, -0.40, 1.77), (0.09, 0.06, 0.17), accent, 0.02)
box('Display floor', (0, 0, -0.075), (200, 200, 0.1), floor_mat, 0)
bpy.ops.object.camera_add(location=(6.4, -8.2, 5.0))
cam = bpy.context.object
cam.name = 'Headphones presentation camera'
cam.rotation_euler = (Vector((0, 0, 1.95)) - cam.location).to_track_quat('-Z', 'Y').to_euler()
cam.data.type = 'ORTHO'
cam.data.ortho_scale = 5.1
bpy.context.scene.camera = cam
bpy.ops.object.light_add(type='AREA', location=(1, -4, 7))
bpy.context.object.data.energy = 1000
bpy.context.object.data.shape = 'DISK'
bpy.context.object.data.size = 5
bpy.context.scene.world.color = (0.3, 0.3, 0.3)
