import bpy
import math
from mathutils import Vector


def clear_scene():
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete(use_global=False)
    for block in (bpy.data.meshes, bpy.data.materials, bpy.data.curves):
        for item in list(block):
            if item.users == 0:
                block.remove(item)


def make_material(name, color, roughness=0.5, metallic=0.0, emission=0.0):
    mat = bpy.data.materials.new(name)
    mat.use_nodes = True
    bsdf = mat.node_tree.nodes["Principled BSDF"]
    bsdf.inputs["Base Color"].default_value = (*color, 1.0)
    bsdf.inputs["Roughness"].default_value = roughness
    bsdf.inputs["Metallic"].default_value = metallic
    if emission:
        bsdf.inputs["Emission Color"].default_value = (*color, 1.0)
        bsdf.inputs["Emission Strength"].default_value = emission
    return mat


def add_box(name, size, location, material, rotation=(0, 0, 0)):
    bpy.ops.mesh.primitive_cube_add(size=2, location=location, rotation=rotation)
    obj = bpy.context.object
    obj.name = name
    obj.scale = (size[0] / 2.0, size[1] / 2.0, size[2] / 2.0)
    obj.data.materials.append(material)
    return obj


def add_cylinder(name, radius, depth, location, material, rotation=(0, 0, 0), verts=24):
    bpy.ops.mesh.primitive_cylinder_add(vertices=verts, radius=radius, depth=depth,
                                        location=location, rotation=rotation)
    obj = bpy.context.object
    obj.name = name
    obj.data.materials.append(material)
    return obj


def add_cable(name, points, radius, material):
    curve = bpy.data.curves.new(name + "Curve", type='CURVE')
    curve.dimensions = '3D'
    curve.bevel_depth = radius
    curve.bevel_resolution = 3
    curve.resolution_u = 6
    spline = curve.splines.new('BEZIER')
    spline.bezier_points.add(len(points) - 1)
    for bp, co in zip(spline.bezier_points, points):
        bp.co = Vector(co)
        bp.handle_left_type = 'AUTO'
        bp.handle_right_type = 'AUTO'
    obj = bpy.data.objects.new(name, curve)
    obj.data.materials.append(material)
    bpy.context.collection.objects.link(obj)
    return obj


clear_scene()

asphalt = make_material("Asphalt", (0.06, 0.06, 0.07), 0.95)
concrete = make_material("Concrete", (0.62, 0.61, 0.58), 0.85)
shell = make_material("ChargerShell", (0.05, 0.32, 0.24), 0.35)
trim = make_material("BrushedSteel", (0.72, 0.73, 0.75), 0.30, metallic=1.0)
rubber = make_material("CableRubber", (0.04, 0.04, 0.05), 0.70)
screen = make_material("Screen", (0.15, 0.55, 0.90), 0.15, emission=2.5)
signal = make_material("StatusGreen", (0.15, 0.95, 0.35), 0.20, emission=4.0)
hazard = make_material("HazardYellow", (0.92, 0.72, 0.08), 0.50)

# Ground, island and painted bay markings
add_box("GroundPad", (14.0, 14.0, 0.2), (0, 0, -0.1), asphalt)
add_box("ConcreteIsland", (3.0, 1.6, 0.16), (0, 0, 0.06), concrete)
for i, y in enumerate((-2.6, 2.6)):
    add_box("BayStripe_%d" % i, (5.0, 0.14, 0.02), (2.6, y, 0.01), concrete)

# Charger pedestal
add_box("ChargerBase", (1.10, 0.70, 0.18), (0, 0, 0.23), trim)
add_box("ChargerBody", (0.95, 0.55, 1.75), (0, 0, 1.20), shell)
add_box("ChargerHead", (1.00, 0.60, 0.22), (0, 0, 2.16), trim)
add_box("DisplayBezel", (0.62, 0.06, 0.52), (0, -0.29, 1.55), trim)
add_box("DisplayScreen", (0.52, 0.03, 0.42), (0, -0.33, 1.55), screen)
add_box("CardReader", (0.22, 0.06, 0.12), (0, -0.30, 1.12), trim)
add_box("VentPanel", (0.70, 0.04, 0.30), (0, 0.28, 0.80), trim)
add_box("BrandStripe", (0.97, 0.57, 0.05), (0, 0, 1.98), hazard)
add_cylinder("StatusLamp", 0.05, 0.06, (0, -0.30, 1.95), signal,
             rotation=(math.pi / 2, 0, 0), verts=16)

# Connector holsters on both flanks
for i, sx in enumerate((-1, 1)):
    add_cylinder("Holster_%d" % i, 0.09, 0.26, (sx * 0.52, -0.10, 1.30), rubber,
                 rotation=(0, math.pi / 2, 0), verts=16)
    add_box("Connector_%d" % i, (0.20, 0.13, 0.13), (sx * 0.62, -0.10, 1.30), trim)

add_cable("CableLeft", [(-0.62, -0.10, 1.30), (-1.25, -0.35, 0.85),
                        (-1.45, -0.20, 1.45), (-0.50, 0.28, 1.70)], 0.035, rubber)
add_cable("CableRight", [(0.62, -0.10, 1.30), (1.20, -0.40, 0.80),
                         (1.40, -0.10, 1.40), (0.50, 0.28, 1.70)], 0.035, rubber)

# Protective bollards
for i, (bx, by) in enumerate(((-1.35, -0.6), (1.35, -0.6), (-1.35, 0.6), (1.35, 0.6))):
    add_cylinder("Bollard_%d" % i, 0.11, 1.0, (bx, by, 0.50), hazard, verts=16)
    add_cylinder("BollardCap_%d" % i, 0.11, 0.08, (bx, by, 1.02), trim, verts=16)

# Signage post
add_cylinder("SignPost", 0.05, 2.6, (2.0, 0.9, 1.30), trim, verts=12)
add_box("SignPlate", (0.55, 0.05, 0.55), (2.0, 0.9, 2.45), signal)

# Lighting
sun_data = bpy.data.lights.new("KeySun", type='SUN')
sun_data.energy = 4.0
sun = bpy.data.objects.new("KeySun", sun_data)
sun.location = (5, -6, 9)
sun.rotation_euler = (math.radians(52), 0, math.radians(38))
bpy.context.collection.objects.link(sun)

fill_data = bpy.data.lights.new("FillArea", type='AREA')
fill_data.energy = 220.0
fill_data.size = 5.0
fill = bpy.data.objects.new("FillArea", fill_data)
fill.location = (-4, -4, 4)
fill.rotation_euler = (math.radians(55), 0, math.radians(-45))
bpy.context.collection.objects.link(fill)

# Camera aimed at the charger
cam_data = bpy.data.cameras.new("Camera")
cam_data.lens = 45
cam = bpy.data.objects.new("Camera", cam_data)
cam.location = (4.6, -5.2, 3.4)
target = Vector((0.0, 0.0, 1.25))
cam.rotation_euler = (target - cam.location).to_track_quat('-Z', 'Y').to_euler()
bpy.context.collection.objects.link(cam)
bpy.context.scene.camera = cam
