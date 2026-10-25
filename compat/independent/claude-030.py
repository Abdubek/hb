import bpy
import math
from mathutils import Vector


def clear_scene():
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete(use_global=False)
    for coll in (bpy.data.meshes, bpy.data.materials):
        for block in list(coll):
            if block.users == 0:
                coll.remove(block)


def make_material(name, color, roughness=0.5, metallic=0.0):
    mat = bpy.data.materials.new(name)
    mat.use_nodes = True
    bsdf = mat.node_tree.nodes["Principled BSDF"]
    bsdf.inputs["Base Color"].default_value = (color[0], color[1], color[2], 1.0)
    bsdf.inputs["Roughness"].default_value = roughness
    bsdf.inputs["Metallic"].default_value = metallic
    return mat


def add_box(name, size, location, material, rotation=(0.0, 0.0, 0.0)):
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=location, rotation=rotation)
    obj = bpy.context.object
    obj.name = name
    obj.scale = size
    obj.data.materials.append(material)
    return obj


def add_cylinder(name, radius, depth, location, material, rotation=(0.0, 0.0, 0.0), verts=24):
    bpy.ops.mesh.primitive_cylinder_add(radius=radius, depth=depth, vertices=verts,
                                        location=location, rotation=rotation)
    obj = bpy.context.object
    obj.name = name
    obj.data.materials.append(material)
    return obj


def add_wheel(name, radius, width, location, tyre, hub):
    add_cylinder(name, radius, width, location, tyre, rotation=(math.pi / 2.0, 0.0, 0.0), verts=28)
    add_cylinder(name + "_Hub", radius * 0.45, width * 1.05, location, hub,
                 rotation=(math.pi / 2.0, 0.0, 0.0), verts=20)


def aim(obj, target):
    direction = Vector(target) - obj.location
    obj.rotation_euler = direction.to_track_quat('-Z', 'Y').to_euler()


clear_scene()

yellow = make_material("MAT_Yellow_Body", (0.85, 0.55, 0.03), roughness=0.35)
dark = make_material("MAT_Dark_Steel", (0.06, 0.06, 0.07), roughness=0.55, metallic=0.8)
steel = make_material("MAT_Bare_Steel", (0.55, 0.56, 0.58), roughness=0.3, metallic=1.0)
rubber = make_material("MAT_Rubber", (0.03, 0.03, 0.035), roughness=0.9)
fabric = make_material("MAT_Seat", (0.12, 0.13, 0.16), roughness=0.85)
floor_mat = make_material("MAT_Floor", (0.42, 0.42, 0.44), roughness=0.9)

add_box("Ground", (16.0, 16.0, 0.1), (0.0, 0.0, -0.05), floor_mat)

# --- chassis and bodywork -------------------------------------------------
add_box("Chassis", (1.9, 1.2, 0.55), (-0.15, 0.0, 0.75), yellow)
add_box("Counterweight", (0.55, 1.15, 0.65), (-1.05, 0.0, 0.82), dark)
add_box("EngineCover", (0.72, 1.05, 0.4), (-0.78, 0.0, 1.22), yellow)
add_box("StepPlate", (0.3, 0.1, 0.05), (0.1, -0.66, 0.55), steel)

# --- operator station -----------------------------------------------------
add_box("SeatBase", (0.46, 0.52, 0.12), (-0.3, 0.0, 1.09), fabric)
add_box("SeatBack", (0.12, 0.52, 0.48), (-0.52, 0.0, 1.37), fabric)
add_cylinder("SteeringColumn", 0.045, 0.5, (0.2, 0.0, 1.27), dark,
             rotation=(math.radians(25.0), 0.0, 0.0))
bpy.ops.mesh.primitive_torus_add(major_radius=0.15, minor_radius=0.02,
                                 location=(0.29, 0.1, 1.48),
                                 rotation=(math.radians(-25.0), 0.0, 0.0),
                                 major_segments=24, minor_segments=10)
bpy.context.object.name = "SteeringWheel"
bpy.context.object.data.materials.append(dark)

# --- overhead guard -------------------------------------------------------
for sx, x in (("F", 0.3), ("R", -0.85)):
    for sy, y in (("L", 0.5), ("R", -0.5)):
        add_box("GuardPost_%s%s" % (sx, sy), (0.07, 0.07, 1.2), (x, y, 1.62), dark)
add_box("GuardRoof", (1.5, 1.2, 0.07), (-0.27, 0.0, 2.25), yellow)

# --- mast, carriage and forks --------------------------------------------
for sy, y in (("L", 0.45), ("R", -0.45)):
    add_box("MastRail_Outer_%s" % sy, (0.13, 0.14, 2.3), (1.02, y, 1.35), dark)
    add_box("MastRail_Inner_%s" % sy, (0.09, 0.1, 1.9), (1.14, y * 0.72, 1.5), steel)
add_box("MastCrossbar", (0.14, 1.06, 0.14), (1.02, 0.0, 2.55), dark)
add_box("MastFoot", (0.35, 1.06, 0.18), (0.95, 0.0, 0.28), dark)
add_cylinder("LiftCylinder", 0.075, 1.7, (1.02, 0.0, 1.2), steel)
add_cylinder("TiltCylinder", 0.055, 0.7, (0.6, 0.52, 0.95), steel,
             rotation=(0.0, math.radians(65.0), 0.0))

add_box("Carriage", (0.1, 1.0, 0.62), (1.24, 0.0, 0.72), dark)
add_box("LoadBackrest", (0.06, 0.95, 0.55), (1.24, 0.0, 1.28), steel)
for sy, y in (("L", 0.34), ("R", -0.34)):
    add_box("Fork_Shank_%s" % sy, (0.08, 0.16, 0.58), (1.33, y, 0.5), steel)
    add_box("Fork_Tine_%s" % sy, (1.05, 0.16, 0.06), (1.85, y, 0.24), steel)

# --- running gear ---------------------------------------------------------
for sy, y in (("L", 0.62), ("R", -0.62)):
    add_wheel("Wheel_Front_%s" % sy, 0.38, 0.3, (0.62, y, 0.38), rubber, steel)
for sy, y in (("L", 0.5), ("R", -0.5)):
    add_wheel("Wheel_Rear_%s" % sy, 0.28, 0.24, (-0.9, y, 0.28), rubber, steel)
add_cylinder("RearAxle", 0.05, 1.0, (-0.9, 0.0, 0.28), dark, rotation=(math.pi / 2.0, 0.0, 0.0))

# --- lighting and camera --------------------------------------------------
bpy.ops.object.light_add(type='SUN', location=(5.0, -6.0, 9.0))
sun = bpy.context.object
sun.name = "KeySun"
sun.data.energy = 3.5
sun.rotation_euler = (math.radians(52.0), 0.0, math.radians(35.0))

bpy.ops.object.light_add(type='AREA', location=(-5.0, 4.0, 5.0))
fill = bpy.context.object
fill.name = "FillArea"
fill.data.energy = 320.0
fill.data.size = 5.0
aim(fill, (0.0, 0.0, 1.0))

bpy.ops.object.camera_add(location=(5.6, -5.4, 3.6))
cam = bpy.context.object
cam.name = "SceneCamera"
cam.data.lens = 50.0
aim(cam, (0.15, 0.0, 1.25))
bpy.context.scene.camera = cam
