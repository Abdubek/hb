import bpy
import math
import random
from mathutils import Vector


def clear_scene():
    for ob in list(bpy.data.objects):
        bpy.data.objects.remove(ob, do_unlink=True)
    for coll in (bpy.data.meshes, bpy.data.materials, bpy.data.cameras, bpy.data.lights):
        for item in list(coll):
            if item.users == 0:
                coll.remove(item)


def make_material(name, color, roughness=0.5, metallic=0.0, alpha=1.0, emission=0.0):
    mat = bpy.data.materials.new(name)
    mat.use_nodes = True
    bsdf = mat.node_tree.nodes["Principled BSDF"]
    bsdf.inputs["Base Color"].default_value = (*color, 1.0)
    bsdf.inputs["Roughness"].default_value = roughness
    bsdf.inputs["Metallic"].default_value = metallic
    if alpha < 1.0:
        bsdf.inputs["Alpha"].default_value = alpha
        mat.blend_method = 'BLEND'
    if emission > 0.0:
        bsdf.inputs["Emission Color"].default_value = (*color, 1.0)
        bsdf.inputs["Emission Strength"].default_value = emission
    return mat


def add_box(name, size, location, material, rotation=(0.0, 0.0, 0.0)):
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=location, rotation=rotation)
    ob = bpy.context.active_object
    ob.name = name
    ob.scale = size
    ob.data.materials.append(material)
    return ob


def add_cylinder(name, radius, depth, location, material, rotation=(0.0, 0.0, 0.0), verts=20):
    bpy.ops.mesh.primitive_cylinder_add(radius=radius, depth=depth, vertices=verts,
                                        location=location, rotation=rotation)
    ob = bpy.context.active_object
    ob.name = name
    ob.data.materials.append(material)
    return ob


def aim(ob, target):
    ob.rotation_euler = (Vector(target) - ob.location).to_track_quat('-Z', 'Y').to_euler()


clear_scene()
random.seed(7)

body_mat = make_material("MachineRed", (0.45, 0.04, 0.05), roughness=0.35)
dark_mat = make_material("DarkPlastic", (0.03, 0.03, 0.035), roughness=0.40)
steel_mat = make_material("Steel", (0.60, 0.61, 0.64), roughness=0.28, metallic=1.0)
glass_mat = make_material("Glass", (0.75, 0.85, 0.90), roughness=0.05, alpha=0.18)
sign_mat = make_material("SignPanel", (0.95, 0.85, 0.30), roughness=0.25, emission=2.0)
shelf_mat = make_material("ShelfMetal", (0.45, 0.46, 0.48), roughness=0.45, metallic=0.8)
floor_mat = make_material("FloorTile", (0.30, 0.30, 0.31), roughness=0.80)
key_mat = make_material("KeypadButton", (0.80, 0.80, 0.82), roughness=0.50)
snack_mats = [make_material("Snack_%d" % i, c, roughness=0.35) for i, c in enumerate(
    [(0.85, 0.55, 0.10), (0.15, 0.45, 0.80), (0.20, 0.65, 0.30),
     (0.80, 0.20, 0.25), (0.60, 0.25, 0.70)])]

W, D, H = 1.05, 0.80, 1.95   # cabinet outer dimensions
T = 0.05                     # panel thickness

add_box("Floor", (7.0, 7.0, 0.04), (0.0, 0.0, -0.02), floor_mat)

# --- Cabinet shell -----------------------------------------------------------
add_box("Cabinet_Back", (W, T, H), (0.0, D / 2 - T / 2, H / 2), body_mat)
add_box("Cabinet_Top", (W, D, T), (0.0, 0.0, H - T / 2), body_mat)
add_box("Cabinet_Bottom", (W, D, T), (0.0, 0.0, T / 2), dark_mat)
for sx in (-1, 1):
    add_box("Cabinet_Side_%s" % ("L" if sx < 0 else "R"),
            (T, D, H), (sx * (W / 2 - T / 2), 0.0, H / 2), body_mat)
for sx in (-1, 1):
    add_cylinder("Foot_%s" % ("L" if sx < 0 else "R"), 0.03, 0.06,
                 (sx * (W / 2 - 0.10), 0.0, 0.03), steel_mat)

# --- Front: illuminated sign, glass window, control column -------------------
front_y = -D / 2 + T / 2
add_box("Sign_Header", (W - 2 * T, T, 0.26), (0.0, front_y, H - 0.20), sign_mat)
add_box("Sign_Frame", (W - 2 * T, 0.02, 0.03), (0.0, front_y - 0.03, H - 0.34), dark_mat)

COL_W = 0.30                      # right-hand control column width
win_w = W - 2 * T - COL_W
win_cx = -(W / 2 - T) + win_w / 2
win_bottom, win_top = 0.42, H - 0.36
add_box("Display_Glass", (win_w, 0.015, win_top - win_bottom),
        (win_cx, front_y, (win_top + win_bottom) / 2), glass_mat)
for sx in (-1, 1):
    add_box("Window_Mullion_%d" % sx, (0.025, 0.03, win_top - win_bottom),
            (win_cx + sx * win_w / 2, front_y, (win_top + win_bottom) / 2), dark_mat)

# --- Product shelves and goods ----------------------------------------------
SHELVES = 4
for s in range(SHELVES):
    z = win_bottom + 0.10 + s * ((win_top - win_bottom - 0.14) / SHELVES)
    add_box("Shelf_%d" % s, (win_w - 0.06, D - 0.16, 0.015), (win_cx, 0.04, z), shelf_mat)
    add_box("Shelf_Rail_%d" % s, (win_w - 0.06, 0.012, 0.04),
            (win_cx, 0.04 - (D - 0.16) / 2, z + 0.028), dark_mat)
    for col in range(5):
        x = win_cx - (win_w - 0.14) / 2 + col * ((win_w - 0.14) / 4)
        mat = snack_mats[(s + col) % len(snack_mats)]
        if (s + col) % 3 == 0:
            add_cylinder("Can_%d_%d" % (s, col), 0.032, 0.12, (x, 0.02, z + 0.068), mat)
        else:
            h = 0.14 + 0.02 * ((col + s) % 3)
            add_box("Pack_%d_%d" % (s, col), (0.085, 0.05, h),
                    (x, 0.02, z + 0.008 + h / 2), mat,
                    rotation=(0.0, 0.0, random.uniform(-0.06, 0.06)))

# --- Keypad, coin slot, card reader -----------------------------------------
col_cx = W / 2 - T - COL_W / 2
add_box("Control_Panel", (COL_W, 0.03, win_top - win_bottom),
        (col_cx, front_y - 0.01, (win_top + win_bottom) / 2), dark_mat)
add_box("Keypad_Plate", (0.22, 0.02, 0.30), (col_cx, front_y - 0.03, 1.28), steel_mat)
for row in range(4):
    for col in range(3):
        add_cylinder("Key_%d%d" % (row, col), 0.019, 0.016,
                     (col_cx - 0.06 + col * 0.06, front_y - 0.045, 1.39 - row * 0.062),
                     key_mat, rotation=(math.pi / 2, 0.0, 0.0), verts=16)
add_box("Price_Display", (0.20, 0.02, 0.07), (col_cx, front_y - 0.035, 1.52),
        make_material("LEDDisplay", (0.10, 0.90, 0.35), roughness=0.2, emission=3.0))
add_box("Card_Reader", (0.10, 0.05, 0.16), (col_cx, front_y - 0.045, 1.03), steel_mat)
add_cylinder("Coin_Slot", 0.016, 0.03, (col_cx + 0.06, front_y - 0.045, 0.86),
             steel_mat, rotation=(math.pi / 2, 0.0, 0.0))
add_box("Coin_Return", (0.09, 0.04, 0.05), (col_cx - 0.05, front_y - 0.04, 0.72), steel_mat)

# --- Dispensing tray ---------------------------------------------------------
add_box("Tray_Recess", (W - 2 * T, 0.10, 0.26), (0.0, front_y + 0.06, 0.26), dark_mat)
add_box("Tray_Flap", (W - 0.20, 0.02, 0.18), (0.0, front_y - 0.02, 0.28), dark_mat,
        rotation=(math.radians(-14.0), 0.0, 0.0))
add_box("Tray_Lip", (W - 0.20, 0.06, 0.02), (0.0, front_y + 0.01, 0.155), steel_mat)

# --- Lighting and camera -----------------------------------------------------
for name, loc, energy, size in (("KeyLight", (2.0, -2.4, 3.0), 500.0, 3.0),
                                ("FillLight", (-2.4, -1.8, 2.0), 160.0, 2.5)):
    data = bpy.data.lights.new(name, type='AREA')
    data.energy = energy
    data.size = size
    lamp = bpy.data.objects.new(name, data)
    bpy.context.collection.objects.link(lamp)
    lamp.location = loc
    aim(lamp, (0.0, 0.0, 1.1))

cam_data = bpy.data.cameras.new("VendingCam")
cam_data.lens = 42.0
cam = bpy.data.objects.new("Camera", cam_data)
bpy.context.collection.objects.link(cam)
cam.location = Vector((1.9, -2.9, 1.85))
aim(cam, (0.0, 0.0, 1.05))
bpy.context.scene.camera = cam
