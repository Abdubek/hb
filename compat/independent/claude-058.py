import bpy
import math
from mathutils import Vector


def make_material(name, color, metallic=0.0, roughness=0.5):
    mat = bpy.data.materials.get(name)
    if mat is None:
        mat = bpy.data.materials.new(name)
    mat.use_nodes = True
    bsdf = mat.node_tree.nodes["Principled BSDF"]
    bsdf.inputs["Base Color"].default_value = (color[0], color[1], color[2], 1.0)
    bsdf.inputs["Metallic"].default_value = metallic
    bsdf.inputs["Roughness"].default_value = roughness
    return mat


def add_box(name, dims, loc, mat, rot=(0.0, 0.0, 0.0)):
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=loc, rotation=rot)
    ob = bpy.context.object
    ob.name = name
    ob.scale = dims
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    ob.data.materials.append(mat)
    return ob


def add_cyl(name, radius, height, loc, mat, rot=(0.0, 0.0, 0.0), verts=24):
    bpy.ops.mesh.primitive_cylinder_add(radius=radius, depth=height, vertices=verts,
                                        location=loc, rotation=rot)
    ob = bpy.context.object
    ob.name = name
    for poly in ob.data.polygons:
        poly.use_smooth = True
    ob.data.materials.append(mat)
    return ob


def aim(ob, target):
    direction = Vector(target) - ob.location
    ob.rotation_euler = direction.to_track_quat('-Z', 'Y').to_euler()


# --- materials -------------------------------------------------------------
wood = make_material("CartWood", (0.32, 0.18, 0.09), 0.0, 0.55)
steel = make_material("BrushedSteel", (0.68, 0.69, 0.71), 1.0, 0.28)
chrome = make_material("Chrome", (0.85, 0.86, 0.88), 1.0, 0.08)
black = make_material("MattBlack", (0.05, 0.05, 0.055), 0.2, 0.6)
rubber = make_material("TireRubber", (0.03, 0.03, 0.035), 0.0, 0.85)
porcelain = make_material("Porcelain", (0.94, 0.93, 0.90), 0.0, 0.3)
brass = make_material("Brass", (0.72, 0.53, 0.20), 1.0, 0.25)


# --- rolling base ----------------------------------------------------------
def build_caster(tag, x, y):
    add_box("CasterFork_" + tag, (0.10, 0.05, 0.16), (x, y, 0.20), steel)
    add_cyl("Wheel_" + tag, 0.11, 0.05, (x, y, 0.11), rubber,
            rot=(math.radians(90), 0, 0), verts=28)
    add_cyl("WheelHub_" + tag, 0.035, 0.056, (x, y, 0.11), chrome,
            rot=(math.radians(90), 0, 0), verts=16)


for tag, x, y in (("FL", -0.36, -0.21), ("FR", 0.36, -0.21),
                  ("BL", -0.36, 0.21), ("BR", 0.36, 0.21)):
    build_caster(tag, x, y)

add_box("BaseFrame", (0.92, 0.58, 0.06), (0.0, 0.0, 0.31), steel)
add_box("CabinetBody", (0.90, 0.56, 0.60), (0.0, 0.0, 0.64), wood)
add_box("CabinetDoorL", (0.42, 0.02, 0.50), (-0.23, -0.29, 0.64), black)
add_box("CabinetDoorR", (0.42, 0.02, 0.50), (0.23, -0.29, 0.64), black)
add_cyl("DoorHandleL", 0.010, 0.16, (-0.06, -0.305, 0.64), chrome,
        rot=(math.radians(90), 0, 0), verts=12)
add_cyl("DoorHandleR", 0.010, 0.16, (0.06, -0.305, 0.64), chrome,
        rot=(math.radians(90), 0, 0), verts=12)
add_box("Countertop", (1.02, 0.64, 0.05), (0.0, 0.0, 0.965), steel)
add_box("CounterEdge", (1.02, 0.02, 0.03), (0.0, -0.31, 0.925), chrome)

# push handle at the back
for tag, x in (("L", -0.40), ("R", 0.40)):
    add_cyl("HandlePost_" + tag, 0.016, 0.22, (x, 0.30, 1.09), chrome, verts=12)
add_cyl("HandleBar", 0.018, 0.82, (0.0, 0.30, 1.19), chrome,
        rot=(0, math.radians(90), 0), verts=14)


# --- espresso machine ------------------------------------------------------
machine_z = 0.99
add_box("MachineBase", (0.52, 0.38, 0.04), (-0.14, 0.03, machine_z + 0.02), black)
add_box("MachineBody", (0.50, 0.36, 0.30), (-0.14, 0.03, machine_z + 0.19), steel)
add_box("MachineHood", (0.52, 0.38, 0.06), (-0.14, 0.03, machine_z + 0.37), black)
add_box("DripTray", (0.34, 0.16, 0.03), (-0.14, -0.14, machine_z + 0.055), chrome)

for tag, gx in (("L", -0.26), ("R", -0.02)):
    add_cyl("GroupHead_" + tag, 0.045, 0.09, (gx, -0.10, machine_z + 0.14), chrome, verts=18)
    add_cyl("PortafilterCup_" + tag, 0.048, 0.05, (gx, -0.10, machine_z + 0.085), chrome, verts=18)
    add_cyl("PortafilterHandle_" + tag, 0.014, 0.14, (gx, -0.18, machine_z + 0.085), black,
            rot=(math.radians(90), 0, 0), verts=12)
    add_cyl("Gauge_" + tag, 0.035, 0.02, (gx, -0.145, machine_z + 0.27), chrome,
            rot=(math.radians(90), 0, 0), verts=20)

add_cyl("SteamWand", 0.009, 0.24, (0.10, -0.09, machine_z + 0.14), chrome,
        rot=(math.radians(28), 0, 0), verts=10)
add_cyl("SteamKnob", 0.026, 0.03, (0.10, -0.14, machine_z + 0.28), black,
        rot=(math.radians(90), 0, 0), verts=16)

# cup warmer rail and cups
add_box("CupRail", (0.50, 0.34, 0.012), (-0.14, 0.03, machine_z + 0.41), chrome)
for i in range(3):
    add_cyl("WarmCup_%d" % i, 0.035, 0.06, (-0.30 + i * 0.15, 0.05, machine_z + 0.445),
            porcelain, verts=18)

# grinder, pitcher and cup stacks on the free counter side
add_box("GrinderBody", (0.14, 0.16, 0.26), (0.33, 0.10, machine_z + 0.155), black)
add_cyl("GrinderHopper", 0.06, 0.16, (0.33, 0.10, machine_z + 0.36), brass, verts=20)
add_cyl("MilkPitcher", 0.05, 0.13, (0.34, -0.16, machine_z + 0.09), chrome, verts=20)
for i in range(2):
    add_cyl("CupStack_%d" % i, 0.038, 0.16, (0.13 + i * 0.10, 0.24, machine_z + 0.105),
            porcelain, verts=18)


# --- ground, light, camera -------------------------------------------------
bpy.ops.mesh.primitive_plane_add(size=8.0, location=(0, 0, 0))
floor = bpy.context.object
floor.name = "Floor"
floor.data.materials.append(make_material("FloorConcrete", (0.42, 0.41, 0.39), 0.0, 0.8))

bpy.ops.object.light_add(type='AREA', location=(1.6, -1.8, 3.0))
key = bpy.context.object
key.name = "KeyLight"
key.data.energy = 400.0
key.data.size = 2.5
aim(key, (0.0, 0.0, 1.0))

bpy.ops.object.light_add(type='SUN', location=(-2.5, 2.5, 4.0))
sun = bpy.context.object
sun.name = "FillSun"
sun.data.energy = 1.5
aim(sun, (0.0, 0.0, 0.8))

bpy.ops.object.camera_add(location=(2.1, -2.5, 1.85))
cam = bpy.context.object
cam.name = "SceneCamera"
cam.data.lens = 45.0
aim(cam, (0.0, 0.0, 1.0))
bpy.context.scene.camera = cam
