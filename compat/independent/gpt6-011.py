import bpy
import math
from mathutils import Vector

# Clear the scene.
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
        mod = obj.modifiers.new('Soft molded edges', 'BEVEL')
        mod.width = bevel
        mod.segments = 2
        obj.modifiers.new('Weighted corner normals', 'WEIGHTED_NORMAL')
    return obj

def box(name, location, scale, mat, bevel=0.04):
    bpy.ops.mesh.primitive_cube_add(size=1, location=location)
    obj = bpy.context.object
    obj.dimensions = scale
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    return finish(obj, name, mat, bevel)

def cylinder(name, location, radius, depth, mat, vertices=32):
    bpy.ops.mesh.primitive_cylinder_add(vertices=vertices, radius=radius, depth=depth, location=location)
    return finish(bpy.context.object, name, mat, 0.012)

def tube(name, points, radius, mat):
    curve = bpy.data.curves.new(name, 'CURVE')
    curve.dimensions = '3D'
    curve.bevel_depth = radius
    curve.bevel_resolution = 2
    spline = curve.splines.new('POLY')
    spline.points.add(len(points) - 1)
    for p, co in zip(spline.points, points):
        p.co = (*co, 1)
    obj = bpy.data.objects.new(name, curve)
    bpy.context.collection.objects.link(obj)
    obj.data.materials.append(mat)
    return obj

charcoal = material('Charcoal molded housing', (0.045, 0.055, 0.064))
steel = material('Brushed stainless steel', (0.48, 0.53, 0.56), 0.8, 0.28)
black = material('Black rubber and plastic', (0.014, 0.019, 0.023))
glass = material('Smoky carafe glass', (0.36, 0.53, 0.57), 0.0, 0.12)
glass.node_tree.nodes.get('Principled BSDF').inputs['Transmission Weight'].default_value = 0.8
coffee = material('Fresh dark coffee', (0.085, 0.025, 0.009), 0.0, 0.22)
green = material('Green power indicator', (0.12, 0.7, 0.25))
ground = material('Warm countertop', (0.37, 0.33, 0.28))

box('Wide appliance base', (0, 0, 0.18), (2.15, 1.95, 0.28), charcoal, 0.1)
for x in (-0.77, 0.77):
    for y in (-0.67, 0.67):
        cylinder('Rubber foot', (x, y, 0.055), 0.13, 0.1, black)
box('Rear water reservoir', (0, 0.55, 1.48), (1.76, 0.75, 2.5), charcoal, 0.12)
box('Reservoir lid', (0, 0.54, 2.78), (1.83, 0.81, 0.13), black)
box('Water level window', (0.89, 0.5, 1.66), (0.022, 0.27, 1.24), glass, 0.01)
for z in (1.15, 1.4, 1.65, 1.9, 2.15):
    box('Water level graduation', (0.91, 0.5, z), (0.018, 0.16, 0.018), steel, 0)
box('Overhanging brew head', (0, -0.17, 2.43), (1.94, 1.53, 0.52), charcoal, 0.09)
box('Stainless control fascia', (0, -0.945, 2.46), (1.76, 0.035, 0.34), steel, 0.025)
box('Status display', (-0.4, -0.973, 2.47), (0.55, 0.024, 0.19), black, 0.012)
for x in (-0.57, -0.44, -0.31):
    box('Display indicator', (x, -0.99, 2.47), (0.065, 0.012, 0.045), green, 0.004)
for x, mat in ((0.25, black), (0.6, green)):
    button = cylinder('Front push button', (x, -0.99, 2.46), 0.1, 0.055, mat, 20)
    button.rotation_euler[0] = math.pi / 2
cylinder('Filter basket', (0, -0.42, 2.11), 0.56, 0.2, black)
cylinder('Drip nozzle', (0, -0.42, 1.98), 0.08, 0.12, steel, 16)
cylinder('Hot plate surround', (0, -0.43, 0.35), 0.77, 0.08, black)
cylinder('Metal hot plate', (0, -0.43, 0.4), 0.66, 0.035, steel)

# Revolved, open-topped carafe shell with a small pouring lip at the front.
profile = [(0.49, 0.44), (0.62, 0.53), (0.67, 0.8), (0.63, 1.23), (0.47, 1.57), (0.46, 1.7)]
verts, faces = [], []
n = 32
for ring, (radius, z) in enumerate(profile):
    for j in range(n):
        a = 2 * math.pi * j / n
        lip = 0.16 if ring == len(profile) - 1 and j in (23, 24, 25) else 0
        verts.append(((radius + lip) * math.cos(a), -0.43 + (radius + lip) * math.sin(a), z))
for k in range(len(profile) - 1):
    for j in range(n):
        a, b = k * n + j, k * n + (j + 1) % n
        faces.append((a, b, b + n, a + n))
faces.append(tuple(reversed(range(n))))
mesh = bpy.data.meshes.new('Carafe shell mesh')
mesh.from_pydata(verts, [], faces)
mesh.update()
obj = bpy.data.objects.new('Glass carafe with pouring lip', mesh)
bpy.context.collection.objects.link(obj)
finish(obj, obj.name, glass)
obj.modifiers.new('Glass wall thickness', 'SOLIDIFY').thickness = 0.025
cylinder('Coffee inside carafe', (0, -0.43, 0.8), 0.58, 0.57, coffee)
cylinder('Carafe lid', (0, -0.43, 1.7), 0.46, 0.09, black)
cylinder('Lid thumb grip', (0, -0.43, 1.78), 0.15, 0.08, black, 16)
tube('Carafe handle', [(0.44, -0.43, 1.61), (0.84, -0.43, 1.59), (1.02, -0.43, 1.43), (1.02, -0.43, 0.76), (0.85, -0.43, 0.62), (0.61, -0.43, 0.65)], 0.085, black)
box('Countertop', (0, 0, -0.09), (200, 200, 0.12), ground, 0)

bpy.ops.object.camera_add(location=(4.5, -6.2, 3.8))
camera = bpy.context.object
camera.name = 'Coffee maker product camera'
camera.rotation_euler = (Vector((0, -0.1, 1.35)) - camera.location).to_track_quat('-Z', 'Y').to_euler()
camera.data.type = 'ORTHO'
camera.data.ortho_scale = 4.4
bpy.context.scene.camera = camera
for name, location, energy, size in [('Key softbox', (2, -4, 6), 850, 4), ('Fill softbox', (-3, -1, 4), 550, 3)]:
    bpy.ops.object.light_add(type='AREA', location=location)
    light = bpy.context.object
    light.name = name
    light.data.energy, light.data.shape, light.data.size = energy, 'DISK', size
    light.rotation_euler = (Vector((0, 0, 1.3)) - light.location).to_track_quat('-Z', 'Y').to_euler()
scene = bpy.context.scene
scene.world = bpy.data.worlds.new('Coffee maker studio world')
scene.world.use_nodes = True
scene.world.node_tree.nodes['Background'].inputs[0].default_value = (0.3, 0.3, 0.3, 1)
scene.render.resolution_x, scene.render.resolution_y = 900, 900
