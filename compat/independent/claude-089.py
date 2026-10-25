import bpy
import math
from mathutils import Vector


def clear_scene():
    for ob in list(bpy.data.objects):
        bpy.data.objects.remove(ob, do_unlink=True)


def make_material(name, color, roughness=0.5, metallic=0.0):
    mat = bpy.data.materials.new(name)
    mat.use_nodes = True
    bsdf = mat.node_tree.nodes["Principled BSDF"]
    bsdf.inputs["Base Color"].default_value = (color[0], color[1], color[2], 1.0)
    bsdf.inputs["Roughness"].default_value = roughness
    bsdf.inputs["Metallic"].default_value = metallic
    return mat


def add_box(name, size, location, mat, rotation=(0.0, 0.0, 0.0)):
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=location, rotation=rotation)
    ob = bpy.context.object
    ob.name = name
    ob.scale = size
    ob.data.materials.append(mat)
    return ob


def add_cylinder(name, radius, depth, location, mat, rotation=(0.0, 0.0, 0.0), verts=24):
    bpy.ops.mesh.primitive_cylinder_add(radius=radius, depth=depth, vertices=verts,
                                        location=location, rotation=rotation)
    ob = bpy.context.object
    ob.name = name
    ob.data.materials.append(mat)
    return ob


def add_panel(name, p_low, p_high, width, thickness, mat):
    """Flat slab spanning two points in the YZ plane (windshield, ramps)."""
    a, b = Vector(p_low), Vector(p_high)
    d = b - a
    return add_box(name, (width, d.length, thickness), (a + b) * 0.5, mat,
                   (math.atan2(d.z, d.y), 0.0, 0.0))


def add_wheel(name, x, y, rubber, rim_mat, radius=0.36):
    rot = (0.0, math.pi * 0.5, 0.0)
    add_cylinder("Tire_" + name, radius, 0.24, (x, y, radius), rubber, rot, verts=28)
    add_cylinder("Rim_" + name, radius * 0.58, 0.255, (x, y, radius), rim_mat, rot, verts=20)
    add_cylinder("Hub_" + name, radius * 0.20, 0.29, (x, y, radius), rim_mat, rot, verts=12)


clear_scene()

body = make_material("BodyPaint", (0.86, 0.87, 0.89), 0.28, 0.15)
accent = make_material("AccentPaint", (0.10, 0.28, 0.55), 0.30, 0.15)
glass = make_material("WindowGlass", (0.05, 0.09, 0.11), 0.08, 0.0)
trim = make_material("DarkTrim", (0.06, 0.06, 0.07), 0.6, 0.1)
chrome = make_material("Chrome", (0.72, 0.73, 0.75), 0.18, 1.0)
rubber = make_material("TireRubber", (0.035, 0.035, 0.04), 0.9, 0.0)
headlamp = make_material("HeadlampLens", (0.92, 0.90, 0.75), 0.12, 0.0)
taillamp = make_material("TailLampLens", (0.62, 0.04, 0.04), 0.15, 0.0)
ground_mat = make_material("Ground", (0.29, 0.30, 0.31), 0.95, 0.0)

HALF_W = 0.95
FLOOR = 0.75

add_box("Ground", (20.0, 20.0, 0.05), (0.0, 0.0, -0.025), ground_mat)

# --- main volumes ---------------------------------------------------------
add_box("CargoBody", (2 * HALF_W, 3.00, 1.80), (0.0, 0.90, 1.65), body)
add_box("CargoRoof", (1.94, 3.04, 0.06), (0.0, 0.90, 2.58), body)
add_box("CabBody", (2 * HALF_W, 0.85, 1.35), (0.0, -1.02, 1.425), body)
add_box("CabRoof", (1.92, 0.92, 0.06), (0.0, -1.05, 2.13), body)
add_box("Cowl", (1.86, 0.32, 0.65), (0.0, -1.60, 1.075), body)
add_box("Hood", (1.82, 0.60, 0.62), (0.0, -2.06, 1.09), body)
add_box("UnderTray", (1.80, 4.60, 0.22), (0.0, 0.0, 0.66), trim)

# --- glazing --------------------------------------------------------------
add_panel("Windshield", (0.0, -1.78, 1.40), (0.0, -1.44, 2.10), 1.70, 0.05, glass)
for side, sx in (("L", -1.0), ("R", 1.0)):
    add_box("DoorWindow_" + side, (0.04, 0.58, 0.44),
            (sx * (HALF_W + 0.01), -1.05, 1.83), glass)
    add_box("CabDoor_" + side, (0.05, 0.84, 1.28),
            (sx * (HALF_W + 0.02), -1.02, 1.42), accent)
    add_box("DoorWindowRepeat_" + side, (0.04, 0.58, 0.44),
            (sx * (HALF_W + 0.05), -1.05, 1.83), glass)
    add_box("DoorHandle_" + side, (0.05, 0.18, 0.05),
            (sx * (HALF_W + 0.06), -0.72, 1.50), chrome)
    add_box("MirrorArm_" + side, (0.16, 0.05, 0.05),
            (sx * (HALF_W + 0.09), -1.42, 1.92), trim)
    add_box("Mirror_" + side, (0.05, 0.10, 0.26),
            (sx * (HALF_W + 0.19), -1.42, 1.90), trim)
    add_box("RockerSkirt_" + side, (0.06, 2.60, 0.20),
            (sx * (HALF_W - 0.01), 0.0, 0.66), trim)
    add_box("BodyStripe_" + side, (0.03, 3.00, 0.14),
            (sx * (HALF_W + 0.01), 0.90, 1.28), accent)

# --- sliding side door and rear doors ------------------------------------
add_box("SlidingDoor", (0.05, 1.15, 1.45), (-(HALF_W + 0.02), 0.35, 1.58), body)
add_box("SlidingDoorWindow", (0.04, 0.95, 0.42), (-(HALF_W + 0.05), 0.35, 2.06), glass)
add_box("SlidingDoorHandle", (0.05, 0.20, 0.05), (-(HALF_W + 0.06), 0.88, 1.45), chrome)
add_box("SlidingRail", (0.04, 1.40, 0.05), (-(HALF_W + 0.02), 0.55, 0.92), trim)
for side, sx in (("L", -1.0), ("R", 1.0)):
    add_box("RearDoor_" + side, (0.90, 0.06, 1.62), (sx * 0.47, 2.43, 1.62), body)
    add_box("RearDoorWindow_" + side, (0.62, 0.04, 0.36), (sx * 0.47, 2.47, 2.10), glass)
    add_box("RearHandle_" + side, (0.05, 0.07, 0.22), (sx * 0.07, 2.48, 1.55), chrome)

# --- front and rear details ----------------------------------------------
add_box("Grille", (1.30, 0.06, 0.26), (0.0, -2.38, 1.22), trim)
add_box("FrontBumper", (1.88, 0.18, 0.28), (0.0, -2.44, 0.88), trim)
add_box("RearBumper", (1.88, 0.16, 0.24), (0.0, 2.52, 0.78), trim)
add_box("RearStep", (0.80, 0.22, 0.06), (0.0, 2.55, 0.66), chrome)
for side, sx in (("L", -1.0), ("R", 1.0)):
    add_box("Headlight_" + side, (0.30, 0.06, 0.17), (sx * 0.66, -2.38, 1.24), headlamp)
    add_box("FogLight_" + side, (0.14, 0.06, 0.10), (sx * 0.62, -2.50, 0.88), headlamp)
    add_box("TailLight_" + side, (0.16, 0.06, 0.42), (sx * 0.84, 2.47, 1.35), taillamp)
    add_box("MarkerLight_" + side, (0.12, 0.06, 0.07), (sx * 0.55, -2.38, 1.44), headlamp)
add_box("LicensePlate", (0.34, 0.03, 0.17), (0.0, 2.50, 1.00), chrome)

# --- wheels ---------------------------------------------------------------
add_wheel("FL", -0.86, -1.55, rubber, chrome)
add_wheel("FR", 0.86, -1.55, rubber, chrome)
add_wheel("RL", -0.86, 1.45, rubber, chrome)
add_wheel("RR", 0.86, 1.45, rubber, chrome)

# --- lighting and camera --------------------------------------------------
sun_data = bpy.data.lights.new("Sun", type='SUN')
sun_data.energy = 4.2
sun = bpy.data.objects.new("Sun", sun_data)
bpy.context.collection.objects.link(sun)
sun.location = (5.0, -6.0, 9.0)
sun.rotation_euler = (math.radians(50.0), 0.0, math.radians(35.0))

fill_data = bpy.data.lights.new("Fill", type='AREA')
fill_data.energy = 400.0
fill_data.size = 7.0
fill = bpy.data.objects.new("Fill", fill_data)
bpy.context.collection.objects.link(fill)
fill.location = (-6.0, 4.0, 5.0)
fill.rotation_euler = (math.radians(60.0), 0.0, math.radians(-130.0))

cam_data = bpy.data.cameras.new("Camera")
cam_data.lens = 50.0
cam = bpy.data.objects.new("Camera", cam_data)
bpy.context.collection.objects.link(cam)
cam.location = (6.0, -7.2, 3.4)
target = Vector((0.0, -0.20, 1.30))
cam.rotation_euler = (target - cam.location).to_track_quat('-Z', 'Y').to_euler()
bpy.context.scene.camera = cam
