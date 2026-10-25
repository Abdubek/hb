import bpy
import math
from mathutils import Vector

bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)

def material(name, color, metallic=0.0):
    mat = bpy.data.materials.new(name)
    mat.diffuse_color = (*color, 1)
    mat.use_nodes = True
    bs = mat.node_tree.nodes.get('Principled BSDF')
    bs.inputs['Base Color'].default_value = (*color, 1)
    bs.inputs['Metallic'].default_value = metallic
    bs.inputs['Roughness'].default_value = 0.4
    return mat

shell = material('Tank pale gray enamel', (0.64, 0.72, 0.74), 0.45)
steel = material('Galvanized fittings', (0.36, 0.42, 0.46), 0.8)
yellow = material('Safety yellow', (0.95, 0.58, 0.045), 0.35)
dark = material('Gasket and tread', (0.07, 0.09, 0.1))
concrete = material('Concrete plinth', (0.29, 0.3, 0.29))

def cylinder(name, a, b, radius, mat, vertices=32):
    a, b = Vector(a), Vector(b)
    axis = b - a
    bpy.ops.mesh.primitive_cylinder_add(vertices=vertices, radius=radius,
                                      depth=axis.length, location=(a + b) / 2)
    obj = bpy.context.object
    obj.name = name
    obj.rotation_euler = axis.to_track_quat('Z', 'Y').to_euler()
    obj.data.materials.append(mat)
    for face in obj.data.polygons:
        face.use_smooth = len(face.vertices) == 4
    return obj

def box(name, position, dimensions, mat):
    bpy.ops.mesh.primitive_cube_add(size=1, location=position)
    obj = bpy.context.object
    obj.name = name
    obj.dimensions = dimensions
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    obj.data.materials.append(mat)
    return obj

def arc(name, radius, z, start, end, thickness, mat):
    data = bpy.data.curves.new(name, 'CURVE')
    data.dimensions = '3D'
    data.bevel_depth = thickness
    data.bevel_resolution = 3
    data.use_fill_caps = True
    spline = data.splines.new('POLY')
    spline.points.add(96)
    for i, point in enumerate(spline.points):
        angle = start + (end - start) * i / 96
        point.co = (radius * math.cos(angle), radius * math.sin(angle), z, 1)
    obj = bpy.data.objects.new(name, data)
    bpy.context.collection.objects.link(obj)
    obj.data.materials.append(mat)
    return obj

cylinder('Circular concrete foundation', (0, 0, 0), (0, 0, 0.25), 2.35, concrete, 96)
cylinder('Tank bottom skirt', (0, 0, 0.25), (0, 0, 0.48), 2.06, steel, 96)
cylinder('Main cylindrical storage vessel', (0, 0, 0.43), (0, 0, 4.4), 2, shell, 96)
cylinder('Flat access roof', (0, 0, 4.39), (0, 0, 4.48), 2.04, steel, 96)
for z in [0.5, 1.8, 3.1, 4.37]:
    arc('Circumferential shell seam', 2.005, z, 0, math.tau, 0.018, steel)

# Guardrails leave a front opening aligned with the access ladder.
start, end = math.radians(-78), math.radians(258)
for z in [5.02, 5.55]:
    arc('Roof perimeter safety rail', 1.88, z, start, end, 0.034, yellow)
arc('Roof toe rail', 1.88, 4.58, start, end, 0.055, yellow)
for i in range(17):
    angle = start + (end - start) * i / 16
    x, y = 1.88 * math.cos(angle), 1.88 * math.sin(angle)
    cylinder('Guardrail upright', (x, y, 4.47), (x, y, 5.55), 0.034, yellow, 16)
    box('Guardrail base plate', (x, y, 4.49), (0.14, 0.14, 0.025), steel)

for x in [-0.38, 0.38]:
    cylinder('Ladder side rail', (x, -2.24, 0.3), (x, -2.24, 5.55), 0.04, yellow, 16)
    cylinder('Ladder landing handrail', (x, -2.24, 5.55), (x, -1.84, 5.55), 0.04, yellow, 16)
    for z in [0.65, 1.85, 3.05, 4.25]:
        cylinder('Ladder wall bracket', (x, -1.94, z), (x, -2.24, z), 0.035, steel, 16)
for i in range(14):
    z = 0.52 + i * 0.29
    cylinder('Ladder anti-slip rung %02d' % (i + 1), (-0.38, -2.24, z), (0.38, -2.24, z), 0.028, steel, 16)
box('Ladder landing plate', (0, -2.05, 4.46), (0.82, 0.58, 0.065), dark)

cylinder('Roof access hatch neck', (0.65, -0.45, 4.47), (0.65, -0.45, 4.66), 0.45, shell, 48)
cylinder('Hatch gasket', (0.65, -0.45, 4.65), (0.65, -0.45, 4.68), 0.49, dark, 48)
cylinder('Bolted hatch lid', (0.65, -0.45, 4.68), (0.65, -0.45, 4.75), 0.49, steel, 48)
for i in range(8):
    angle = math.tau * i / 8
    x, y = 0.65 + 0.42 * math.cos(angle), -0.45 + 0.42 * math.sin(angle)
    cylinder('Hatch hex bolt', (x, y, 4.74), (x, y, 4.79), 0.025, dark, 6)
for x in [0.5, 0.8]:
    cylinder('Hatch handle foot', (x, -0.45, 4.75), (x, -0.45, 4.87), 0.022, yellow, 12)
cylinder('Hatch lifting handle', (0.5, -0.45, 4.87), (0.8, -0.45, 4.87), 0.022, yellow, 12)
cylinder('Roof vent neck', (-0.7, 0.5, 4.45), (-0.7, 0.5, 4.94), 0.12, steel)
cylinder('Vent rain cap', (-0.7, 0.5, 4.93), (-0.7, 0.5, 5.01), 0.25, shell)
cylinder('Low outlet nozzle', (1.86, 0, 0.85), (2.65, 0, 0.85), 0.14, steel)
cylinder('Outlet blind flange', (2.59, 0, 0.85), (2.7, 0, 0.85), 0.24, steel)
box('Ground slab', (0, 0, -0.1), (8, 8, 0.2), concrete)
bpy.ops.object.camera_add(location=(9, -12, 9))
camera = bpy.context.object
camera.name = 'Tank ladder and roof overview'
camera.rotation_euler = (Vector((0, 0, 2.6)) - camera.location).to_track_quat('-Z', 'Y').to_euler()
camera.data.type = 'ORTHO'
camera.data.ortho_scale = 8.5
bpy.context.scene.camera = camera
for position, energy, size in [((1, -6, 10), 1800, 6), ((-5, 3, 8), 1500, 5)]:
    bpy.ops.object.light_add(type='AREA', location=position)
    light = bpy.context.object
    light.data.energy = energy
    light.data.size = size
    light.rotation_euler = (Vector((0, 0, 2.5)) - light.location).to_track_quat('-Z', 'Y').to_euler()
bpy.context.scene.world.color = (0.22, 0.22, 0.22)
