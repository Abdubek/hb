import bpy
import math
from mathutils import Vector


def clear_scene():
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete(use_global=False)


def make_material(name, color, roughness=0.5, metallic=0.0, emission=0.0):
    mat = bpy.data.materials.new(name)
    mat.use_nodes = True
    bsdf = mat.node_tree.nodes["Principled BSDF"]
    bsdf.inputs["Base Color"].default_value = (color[0], color[1], color[2], 1.0)
    bsdf.inputs["Roughness"].default_value = roughness
    bsdf.inputs["Metallic"].default_value = metallic
    if emission > 0.0:
        bsdf.inputs["Emission Color"].default_value = (color[0], color[1], color[2], 1.0)
        bsdf.inputs["Emission Strength"].default_value = emission
    return mat


def add_box(name, dims, loc, mat, rot=(0.0, 0.0, 0.0)):
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=loc, rotation=rot)
    ob = bpy.context.active_object
    ob.name = name
    ob.scale = dims
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    ob.data.materials.append(mat)
    return ob


def add_cylinder(name, radius, depth, loc, mat, rot=(0.0, 0.0, 0.0), verts=24):
    bpy.ops.mesh.primitive_cylinder_add(vertices=verts, radius=radius, depth=depth,
                                        location=loc, rotation=rot)
    ob = bpy.context.active_object
    ob.name = name
    ob.data.materials.append(mat)
    return ob


def bevel(ob, width=0.008, segments=2):
    mod = ob.modifiers.new("Bevel", 'BEVEL')
    mod.width = width
    mod.segments = segments
    mod.limit_method = 'ANGLE'
    return ob


def look_at(ob, target):
    direction = Vector(target) - ob.location
    ob.rotation_euler = direction.to_track_quat('-Z', 'Y').to_euler()


clear_scene()

m_shell = make_material("KioskShell", (0.78, 0.79, 0.81), roughness=0.35, metallic=0.7)
m_accent = make_material("AccentTeal", (0.05, 0.42, 0.45), roughness=0.45)
m_dark = make_material("DarkPlastic", (0.035, 0.035, 0.04), roughness=0.6)
m_screen = make_material("TouchScreen", (0.20, 0.55, 0.90), roughness=0.1, emission=3.2)
m_sign = make_material("SignLightbox", (0.98, 0.86, 0.35), roughness=0.3, emission=2.2)
m_steel = make_material("BrushedSteel", (0.62, 0.63, 0.65), roughness=0.3, metallic=1.0)
m_led = make_material("ReaderLED", (0.15, 0.95, 0.35), roughness=0.2, emission=6.0)
m_paper = make_material("TicketPaper", (0.94, 0.93, 0.88), roughness=0.85)
m_floor = make_material("FloorTile", (0.30, 0.30, 0.32), roughness=0.6)

bpy.ops.mesh.primitive_plane_add(size=6.0, location=(0.0, 0.0, 0.0))
floor = bpy.context.active_object
floor.name = "Floor"
floor.data.materials.append(m_floor)

add_box("Kiosk_BasePlinth", (0.64, 0.56, 0.06), (0.0, 0.0, 0.03), m_dark)
body = add_box("Kiosk_Body", (0.52, 0.42, 1.02), (0.0, 0.0, 0.57), m_shell)
bevel(body, 0.012, 2)
add_box("Body_AccentStripe", (0.53, 0.43, 0.05), (0.0, 0.0, 0.30), m_accent)

# Tilted head housing carrying the touch screen; screen sits in head local space.
head_rot = (math.radians(28.0), 0.0, 0.0)
head = add_box("Head_Housing", (0.56, 0.46, 0.12), (0.0, -0.055, 1.15), m_shell, head_rot)
bevel(head, 0.01, 2)
H = head.matrix_world.copy()


def on_head(lx, ly, lz):
    return H @ Vector((lx, ly, lz))


add_box("TouchScreen_Glass", (0.46, 0.34, 0.014), on_head(0.0, 0.01, 0.064), m_screen, head_rot)
add_box("Screen_Mask_Top", (0.46, 0.03, 0.016), on_head(0.0, 0.195, 0.063), m_dark, head_rot)
add_cylinder("Head_Camera", 0.012, 0.01, on_head(0.0, 0.195, 0.070), m_dark, head_rot)
add_box("Head_UnderShroud", (0.50, 0.10, 0.06), (0.0, -0.20, 1.05), m_shell)

# Card reader assembly on the right of the front fascia.
reader = add_box("CardReader_Body", (0.14, 0.10, 0.22), (0.155, -0.235, 0.90), m_dark)
bevel(reader, 0.008, 2)
add_box("CardReader_Slot", (0.095, 0.02, 0.012), (0.155, -0.29, 0.965), m_steel)
add_box("CardReader_Keypad", (0.10, 0.02, 0.09), (0.155, -0.288, 0.885), m_shell)
for r in range(3):
    for c in range(3):
        add_box("ReaderKey_%d%d" % (r, c), (0.022, 0.008, 0.018),
                (0.125 + c * 0.03, -0.30, 0.915 - r * 0.026), m_steel)
add_cylinder("CardReader_LED", 0.008, 0.008, (0.155, -0.29, 0.80), m_led,
             (math.radians(90.0), 0.0, 0.0))
add_box("CardReader_TapPad", (0.07, 0.012, 0.05), (0.155, -0.292, 0.735), m_accent)

# Ticket dispensing slot with a printed ticket emerging.
add_box("TicketSlot_Frame", (0.22, 0.03, 0.07), (-0.06, -0.215, 0.62), m_steel)
add_box("TicketSlot_Mouth", (0.18, 0.02, 0.018), (-0.06, -0.232, 0.62), m_dark)
add_box("Ticket_Printed", (0.16, 0.10, 0.003), (-0.06, -0.29, 0.605), m_paper,
        (math.radians(-12.0), 0.0, 0.0))
add_box("CoinReturn_Tray", (0.12, 0.05, 0.03), (0.16, -0.225, 0.62), m_dark)

# Overhead illuminated sign on two posts.
for side, x in (("L", -0.22), ("R", 0.22)):
    add_cylinder("Sign_Post_" + side, 0.018, 0.50, (x, 0.10, 1.42), m_steel, verts=16)
sign = add_box("Sign_Housing", (0.62, 0.08, 0.30), (0.0, 0.10, 1.76), m_shell)
bevel(sign, 0.01, 2)
add_box("Sign_FaceFront", (0.56, 0.02, 0.24), (0.0, 0.055, 1.76), m_sign)
add_box("Sign_FaceBack", (0.56, 0.02, 0.24), (0.0, 0.145, 1.76), m_sign)
add_box("Sign_TopCap", (0.64, 0.10, 0.03), (0.0, 0.10, 1.925), m_accent)

add_box("Body_RearPanel", (0.50, 0.02, 0.90), (0.0, 0.205, 0.58), m_accent)
add_cylinder("Grab_Handle", 0.014, 0.34, (0.0, -0.225, 0.42), m_steel,
             (0.0, math.radians(90.0), 0.0), verts=16)

bpy.ops.object.light_add(type='AREA', location=(1.3, -1.7, 2.8))
key = bpy.context.active_object
key.name = "KeyLight"
key.data.energy = 500.0
key.data.size = 2.5
look_at(key, (0.0, -0.1, 1.1))

bpy.ops.object.light_add(type='AREA', location=(-1.7, -1.1, 1.6))
fill = bpy.context.active_object
fill.name = "FillLight"
fill.data.energy = 140.0
fill.data.size = 2.0
look_at(fill, (0.0, 0.0, 0.9))

bpy.ops.object.camera_add(location=(1.55, -1.95, 1.55))
cam = bpy.context.active_object
cam.name = "SceneCamera"
cam.data.lens = 45.0
look_at(cam, (0.0, -0.08, 1.02))
bpy.context.scene.camera = cam
