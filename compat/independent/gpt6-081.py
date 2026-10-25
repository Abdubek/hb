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

concrete = material('Warm concrete', (0.57, 0.59, 0.57))
steel = material('Blue gray structural steel', (0.13, 0.23, 0.29), 0.7)
cable_mat = material('Galvanized cables', (0.55, 0.61, 0.64), 0.8)
asphalt = material('Road asphalt', (0.07, 0.085, 0.095))
paint = material('Lane marking ivory', (0.95, 0.87, 0.57))
water = material('Still blue water', (0.055, 0.24, 0.32), 0.25, 0.23)
land = material('Stone banks', (0.29, 0.34, 0.28))

def box(name, loc, size, mat, bevel=0.0):
    bpy.ops.mesh.primitive_cube_add(size=1, location=loc)
    obj = bpy.context.object
    obj.name = name
    obj.dimensions = size
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    obj.data.materials.append(mat)
    if bevel:
        mod = obj.modifiers.new('Soft construction edges', 'BEVEL')
        mod.width = bevel
        mod.segments = 2
        obj.modifiers.new('Weighted corner normals', 'WEIGHTED_NORMAL')
    return obj

def rod(name, a, b, radius, mat, vertices=10):
    delta = Vector(b) - Vector(a)
    bpy.ops.mesh.primitive_cylinder_add(vertices=vertices, radius=radius,
                                      depth=delta.length, location=(Vector(a) + Vector(b)) / 2)
    obj = bpy.context.object
    obj.name = name
    obj.rotation_euler = delta.to_track_quat('Z', 'Y').to_euler()
    obj.data.materials.append(mat)
    return obj

def cable(name, points, radius):
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
    obj.data.materials.append(cable_mat)

box('Water surface', (0, 0, -0.16), (49, 24, 0.3), water)
for x in (-21, 21):
    box('River bank', (x, 0, 0.05), (7, 24, 0.65), land, 0.18)
    box('Approach abutment', (x, 0, 1.85), (4.5, 5.8, 3.5), concrete, 0.12)
box('Continuous structural deck', (0, 0, 3.62), (45, 5, 0.65), steel, 0.08)
box('Road surface', (0, 0, 3.985), (45, 3.5, 0.08), asphalt)
for y in (-2.05, 2.05):
    box('Raised pedestrian walkway', (0, y, 4.04), (45, 0.6, 0.18), concrete, 0.03)
    box('Longitudinal stiffening girder', (0, y, 3.22), (45, 0.22, 0.55), steel)
    for z in (4.55, 4.95):
        rod('Continuous guardrail', (-22.5, y, z), (22.5, y, z), 0.035, cable_mat)
    for i in range(46):
        rod('Guardrail upright', (-22.5+i, y, 4.13), (-22.5+i, y, 4.97), 0.028, steel)
for i in range(-21, 22, 3):
    box('Dashed center line', (i, 0, 4.034), (1.5, 0.075, 0.012), paint)
for y in (-1.62, 1.62):
    box('Road edge line', (0, y, 4.034), (45, 0.065, 0.012), paint)
for x in (-10, 10):
    box('Tower foundation', (x, 0, 0.48), (3.1, 7.2, 1.1), concrete, 0.14)
    for y in (-2.85, 2.85):
        box('Tower vertical pier', (x, y, 7.35), (1.05, 0.95, 13.5), concrete, 0.08)
        box('Cable saddle', (x, y, 14.16), (1.4, 0.9, 0.25), steel, 0.06)
    for z in (5.8, 12.8):
        box('Tower portal crossbeam', (x, 0, z), (1.05, 6.1, 0.65), concrete, 0.06)

def cable_height(x):
    if abs(x) <= 10:
        return 6.25 + 7.95 * (x / 10) ** 2
    t = (abs(x) - 10) / 12
    return 14.2 * (1-t) + 4.35*t - 1.15*math.sin(math.pi*t)

for y in (-2.85, 2.85):
    cable('Main suspension cable', [(x/4, y, cable_height(x/4)) for x in range(-88, 89)], 0.095)
    for x in range(-21, 22):
        if x in (-10, 10):
            continue
        rod('Vertical suspender', (x, y, 3.85), (x, y, cable_height(x)), 0.035, cable_mat)
        rod('Deck outrigger', (x, y, 3.65), (x, y*0.77, 3.65), 0.075, steel)
    for x in (-22, 22):
        box('Cable anchorage block', (x, y, 3.75), (2, 1.3, 1.6), concrete, 0.1)

world = bpy.data.worlds.new('Bridge daylight')
bpy.context.scene.world = world
world.use_nodes = True
world.node_tree.nodes['Background'].inputs[0].default_value = (0.65, 0.76, 0.88, 1)
world.node_tree.nodes['Background'].inputs[1].default_value = 0.65
bpy.ops.object.light_add(type='AREA', location=(0, -8, 25))
bpy.context.object.data.energy = 3500
bpy.context.object.data.shape = 'DISK'
bpy.context.object.data.size = 20
bpy.ops.object.light_add(type='SUN', location=(0, 0, 20))
bpy.context.object.rotation_euler = (0.4, -0.5, -0.3)
bpy.context.object.data.energy = 2
bpy.ops.object.camera_add(location=(36, -43, 29))
cam = bpy.context.object
cam.name = 'Bridge overview camera'
cam.rotation_euler = (Vector((0, 0, 5.4)) - cam.location).to_track_quat('-Z', 'Y').to_euler()
cam.data.type = 'ORTHO'
cam.data.ortho_scale = 55
bpy.context.scene.camera = cam
bpy.context.scene.render.resolution_x = 1600
bpy.context.scene.render.resolution_y = 1000
bpy.context.scene.render.resolution_percentage = 100
