import bpy
import math
from mathutils import Vector

# Standalone quadcopter scene; all dimensions are in meters.
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)

def material(name, color, metallic=0.0, roughness=0.4):
    mat = bpy.data.materials.new(name)
    mat.diffuse_color = (*color, 1)
    mat.use_nodes = True
    bsdf = mat.node_tree.nodes.get('Principled BSDF')
    bsdf.inputs['Base Color'].default_value = (*color, 1)
    bsdf.inputs['Metallic'].default_value = metallic
    bsdf.inputs['Roughness'].default_value = roughness
    return mat

shell = material('Pearl white shell', (0.8, 0.84, 0.87), 0.25)
carbon = material('Graphite arms and propellers', (0.035, 0.045, 0.055), 0.25)
metal = material('Brushed motor aluminum', (0.28, 0.32, 0.37), 0.8)
red = material('Front red markings', (0.85, 0.045, 0.025))
green = material('Rear green markings', (0.025, 0.55, 0.18))
glass = material('Camera lens blue glass', (0.015, 0.08, 0.15), 0.65, 0.12)
floor = material('Studio floor', (0.16, 0.19, 0.23))

def finish(obj, name, mat, bevel=0):
    obj.name = name
    obj.data.materials.append(mat)
    if bevel:
        mod = obj.modifiers.new('Soft manufactured edges', 'BEVEL')
        mod.width = bevel
        mod.segments = 3
        obj.modifiers.new('Weighted normals', 'WEIGHTED_NORMAL')
    return obj

def box(name, loc, size, mat, bevel=0.03):
    bpy.ops.mesh.primitive_cube_add(size=1, location=loc)
    obj = bpy.context.object
    obj.dimensions = size
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    return finish(obj, name, mat, bevel)

def cylinder(name, loc, radius, depth, mat, axis=(0, 0, 1)):
    bpy.ops.mesh.primitive_cylinder_add(vertices=32, radius=radius, depth=depth, location=loc)
    obj = bpy.context.object
    obj.rotation_euler = Vector(axis).to_track_quat('Z', 'Y').to_euler()
    return finish(obj, name, mat, 0.012)

def rod(name, a, b, radius, mat):
    a, b = Vector(a), Vector(b)
    return cylinder(name, (a + b) / 2, radius, (b - a).length, mat, b - a)

def propeller(name, center, angle):
    # One closed, swept paddle mesh, duplicated opposite the hub.
    outline = [(0.08, -0.065), (0.36, -0.11), (0.73, -0.07),
               (0.88, 0.015), (0.82, 0.09), (0.43, 0.12), (0.12, 0.065)]
    n = len(outline)
    verts = [(x, y, z) for z in (-0.012, 0.012) for x, y in outline]
    faces = [tuple(reversed(range(n))), tuple(range(n, 2*n))]
    faces += [(i, (i+1) % n, (i+1) % n+n, i+n) for i in range(n)]
    mesh = bpy.data.meshes.new(name + ' paddle mesh')
    mesh.from_pydata(verts, [], faces)
    mesh.update()
    for blade in range(2):
        obj = bpy.data.objects.new(name + ' blade ' + str(blade+1), mesh.copy())
        bpy.context.collection.objects.link(obj)
        obj.location = center
        obj.rotation_euler.z = angle + blade * math.pi
        finish(obj, obj.name, carbon, 0.009)

box('Central electronics chassis', (0, 0, 0.83), (0.93, 1.18, 0.29), carbon, 0.12)
box('Rounded upper flight shell', (0, 0, 1.01), (0.87, 1.10, 0.22), shell, 0.10)
box('Battery compartment', (0, 0.12, 1.15), (0.49, 0.67, 0.11), shell, 0.045)
box('Battery release latch', (0, 0.43, 1.21), (0.17, 0.08, 0.035), carbon, 0.01)
for x in (-1.18, 1.18):
    for y in (-1.18, 1.18):
        tag = ('Left' if x < 0 else 'Right') + (' front' if y < 0 else ' rear')
        rod(tag + ' arm', (x*0.22, y*0.27, 0.83), (x, y, 0.88), 0.105, carbon)
        cylinder(tag + ' motor mount', (x, y, 0.88), 0.20, 0.12, shell)
        cylinder(tag + ' brushless motor', (x, y, 1.02), 0.145, 0.20, metal)
        cylinder(tag + ' indicator band', (x, y, 1.09), 0.149, 0.035, red if y < 0 else green)
        propeller(tag + ' propeller', (x, y, 1.19), math.radians(25 if x*y > 0 else -25))
        cylinder(tag + ' propeller hub', (x, y, 1.20), 0.092, 0.11, carbon)
        cylinder(tag + ' hub bolt', (x, y, 1.26), 0.036, 0.025, metal)
for x in (-0.48, 0.48):
    for y in (-0.40, 0.40):
        rod('Landing strut', (x*0.75, y, 0.76), (x, y, 0.17), 0.035, metal)
    rod('Landing skid', (x, -0.65, 0.13), (x, 0.65, 0.13), 0.055, carbon)
rod('Camera suspension', (0, -0.40, 0.70), (0, -0.40, 0.48), 0.045, metal)
box('Underslung camera body', (0, -0.46, 0.43), (0.32, 0.27, 0.23), carbon)
cylinder('Camera lens bezel', (0, -0.62, 0.43), 0.105, 0.10, metal, (0, 1, 0))
cylinder('Camera front glass', (0, -0.678, 0.43), 0.080, 0.014, glass, (0, 1, 0))
box('Ground', (0, 0, -0.04), (200, 200, 0.10), floor, 0)
bpy.ops.object.camera_add(location=(4.5, -5.7, 5.0))
camera = bpy.context.object
camera.name = 'Quadcopter presentation camera'
camera.rotation_euler = (Vector((0, 0, 0.7)) - camera.location).to_track_quat('-Z', 'Y').to_euler()
camera.data.type = 'ORTHO'
camera.data.ortho_scale = 6.1
bpy.context.scene.camera = camera
for name, loc, power, size in [('Key softbox', (1, -4, 7), 1400, 5), ('Fill softbox', (-4, 2, 5), 1000, 4)]:
    bpy.ops.object.light_add(type='AREA', location=loc)
    light = bpy.context.object
    light.name = name
    light.data.energy = power
    light.data.shape = 'DISK'
    light.data.size = size
    light.rotation_euler = (Vector((0, 0, 0.7)) - light.location).to_track_quat('-Z', 'Y').to_euler()
scene = bpy.context.scene
scene.world = bpy.data.worlds.new('Studio world')
scene.world.use_nodes = True
scene.world.node_tree.nodes['Background'].inputs[0].default_value = (0.20, 0.23, 0.28, 1)
scene.world.node_tree.nodes['Background'].inputs[1].default_value = 0.45
scene.render.resolution_x = 1000
scene.render.resolution_y = 1000
scene.render.resolution_percentage = 100
