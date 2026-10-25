"""claude-018 - Laptop with open screen, keyboard and trackpad.

Builds the scene only: no rendering, no file output, no external assets.
"""

import bpy
import bmesh
import math
from mathutils import Vector


# ----------------------------------------------------------------------------
# generic helpers
# ----------------------------------------------------------------------------

def reset_scene():
    bpy.ops.wm.read_factory_settings(use_empty=True)
    bpy.context.scene.unit_settings.system = 'METRIC'


def new_material(name, base=(0.8, 0.8, 0.8), metallic=0.0, rough=0.5,
                 transmission=0.0, alpha=1.0, ior=1.45,
                 emission=None, emit_strength=0.0, coat=0.0):
    mat = bpy.data.materials.new(name)
    mat.use_nodes = True
    bsdf = mat.node_tree.nodes.get("Principled BSDF")

    def put(key, value):
        if bsdf and key in bsdf.inputs:
            bsdf.inputs[key].default_value = value

    put("Base Color", (base[0], base[1], base[2], 1.0))
    put("Metallic", metallic)
    put("Roughness", rough)
    put("IOR", ior)
    put("Transmission Weight", transmission)
    put("Alpha", alpha)
    put("Coat Weight", coat)
    if emission is not None:
        put("Emission Color", (emission[0], emission[1], emission[2], 1.0))
        put("Emission Strength", emit_strength)
    if alpha < 1.0 or transmission > 0.0:
        try:
            mat.blend_method = 'BLEND'
        except Exception:
            pass
    return mat


def shade_auto(ob, angle=math.radians(32.0)):
    me = ob.data
    for poly in me.polygons:
        poly.use_smooth = True
    bm = bmesh.new()
    bm.from_mesh(me)
    for edge in bm.edges:
        if len(edge.link_faces) == 2:
            edge.smooth = edge.calc_face_angle() < angle
        else:
            edge.smooth = False
    bm.to_mesh(me)
    bm.free()


def _finish(bm, name, loc, rot, mat, smooth, smooth_angle, parent):
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    me = bpy.data.meshes.new(name)
    bm.to_mesh(me)
    bm.free()
    ob = bpy.data.objects.new(name, me)
    bpy.context.collection.objects.link(ob)
    if parent is not None:
        ob.parent = parent
    ob.location = loc
    ob.rotation_euler = rot
    if mat is not None:
        me.materials.append(mat)
    if smooth:
        shade_auto(ob, smooth_angle)
    return ob


def add_box(name, size, loc=(0, 0, 0), rot=(0, 0, 0), mat=None,
            bevel=0.0, seg=3, smooth=True, parent=None):
    bm = bmesh.new()
    bmesh.ops.create_cube(bm, size=1.0)
    bmesh.ops.scale(bm, vec=Vector(size), verts=bm.verts)
    if bevel > 0.0:
        bmesh.ops.bevel(bm, geom=list(bm.verts) + list(bm.edges) + list(bm.faces),
                        offset=bevel, offset_type='OFFSET', segments=seg,
                        profile=0.5, affect='EDGES', clamp_overlap=True)
        return _finish(bm, name, loc, rot, mat, smooth, math.radians(32.0), parent)
    return _finish(bm, name, loc, rot, mat, False, 0.0, parent)


def add_cyl(name, radius, depth, loc=(0, 0, 0), rot=(0, 0, 0), mat=None,
            segments=32, bevel=0.0, parent=None):
    bm = bmesh.new()
    bmesh.ops.create_cone(bm, cap_ends=True, cap_tris=False, segments=segments,
                          radius1=radius, radius2=radius, depth=depth)
    if bevel > 0.0:
        bmesh.ops.bevel(bm, geom=list(bm.verts) + list(bm.edges) + list(bm.faces),
                        offset=bevel, offset_type='OFFSET', segments=2,
                        profile=0.5, affect='EDGES', clamp_overlap=True)
    return _finish(bm, name, loc, rot, mat, True, math.radians(40.0), parent)


def aim(ob, target):
    d = Vector(target) - ob.location
    ob.rotation_euler = d.to_track_quat('-Z', 'Y').to_euler()


def add_light(name, ltype, loc, energy, color=(1.0, 1.0, 1.0), size=1.0,
              target=None):
    data = bpy.data.lights.new(name, ltype)
    data.energy = energy
    data.color = color
    if ltype == 'AREA':
        data.size = size
    elif ltype == 'SUN':
        data.angle = math.radians(3.0)
    else:
        data.shadow_soft_size = size
    ob = bpy.data.objects.new(name, data)
    ob.location = loc
    bpy.context.collection.objects.link(ob)
    if target is not None:
        aim(ob, target)
    return ob


def setup_world(color=(0.04, 0.045, 0.05), strength=1.0):
    world = bpy.data.worlds.new("World")
    bpy.context.scene.world = world
    world.use_nodes = True
    bg = world.node_tree.nodes["Background"]
    bg.inputs[0].default_value = (color[0], color[1], color[2], 1.0)
    bg.inputs[1].default_value = strength


def add_camera(loc, target, lens=55.0, name="Camera"):
    data = bpy.data.cameras.new(name)
    data.lens = lens
    ob = bpy.data.objects.new(name, data)
    ob.location = loc
    bpy.context.collection.objects.link(ob)
    aim(ob, target)
    bpy.context.scene.camera = ob
    return ob


# ----------------------------------------------------------------------------
# materials
# ----------------------------------------------------------------------------

reset_scene()
setup_world((0.035, 0.038, 0.043), 1.0)

DESK = new_material("DeskWood", (0.19, 0.13, 0.09), rough=0.45, coat=0.2)
ALU = new_material("Aluminium", (0.66, 0.67, 0.69), metallic=1.0, rough=0.26)
ALU_DARK = new_material("AluminiumDark", (0.28, 0.29, 0.31), metallic=1.0,
                        rough=0.34)
KEY_PLATE = new_material("KeyPlate", (0.055, 0.055, 0.06), rough=0.55)
KEY_CAP = new_material("KeyCap", (0.085, 0.085, 0.092), rough=0.42)
KEY_MOD = new_material("KeyCapMod", (0.065, 0.065, 0.072), rough=0.46)
TRACKPAD = new_material("Trackpad", (0.13, 0.135, 0.14), rough=0.22, coat=0.5)
BEZEL = new_material("Bezel", (0.02, 0.02, 0.022), rough=0.35)
SCREEN = new_material("ScreenPanel", (0.03, 0.05, 0.09),
                      emission=(0.16, 0.30, 0.52), emit_strength=2.6)
SCREEN_UI = new_material("ScreenUI", (0.8, 0.85, 0.9),
                         emission=(0.82, 0.88, 0.96), emit_strength=3.4)
SCREEN_BAR = new_material("ScreenBar", (0.6, 0.7, 0.85),
                          emission=(0.55, 0.68, 0.9), emit_strength=2.2)
RUBBER = new_material("Rubber", (0.03, 0.03, 0.035), rough=0.75)
GLASSY = new_material("CamGlass", (0.05, 0.06, 0.08), rough=0.08, coat=0.8)


# ----------------------------------------------------------------------------
# desk
# ----------------------------------------------------------------------------

add_box("Desk", (2.4, 1.6, 0.05), (0.0, 0.1, -0.0265), mat=DESK, bevel=0.004)


# ----------------------------------------------------------------------------
# base unit
# ----------------------------------------------------------------------------

BASE_W, BASE_D, BASE_T = 0.335, 0.240, 0.017
FOOT_H = 0.003
BASE_Z0 = FOOT_H
BASE_ZC = BASE_Z0 + BASE_T * 0.5
TOP_Z = BASE_Z0 + BASE_T

add_box("Base", (BASE_W, BASE_D, BASE_T), (0.0, BASE_D * 0.5, BASE_ZC),
        mat=ALU, bevel=0.0035, seg=4)

# recessed keyboard well and palm rest deck
add_box("KeyWell", (0.278, 0.104, 0.004), (0.0, 0.1235, TOP_Z - 0.0015),
        mat=KEY_PLATE, bevel=0.0012)

# rubber feet
for sx in (-1, 1):
    for fy in (0.028, BASE_D - 0.028):
        add_cyl("Foot_%d_%.3f" % (sx, fy), 0.0085, FOOT_H,
                (sx * (BASE_W * 0.5 - 0.030), fy, FOOT_H * 0.5),
                mat=RUBBER, segments=20)

# side ports and a speaker grille strip
for sx in (-1, 1):
    for i, py in enumerate((0.075, 0.105, 0.135)):
        add_box("Port_%d_%d" % (sx, i), (0.006, 0.019, 0.0055),
                (sx * (BASE_W * 0.5 - 0.002), py, BASE_ZC),
                mat=new_material("PortHole_%d_%d" % (sx, i), (0.02, 0.02, 0.02),
                                 rough=0.8))
    add_box("Speaker_%d" % sx, (0.016, 0.098, 0.0025),
            (sx * 0.148, 0.1235, TOP_Z - 0.0005), mat=KEY_PLATE)


# ----------------------------------------------------------------------------
# keyboard: function row plus five full rows
# ----------------------------------------------------------------------------

U = 0.0175          # key pitch
GAP = 0.0022        # gap between key caps
KEY_H = 0.0035      # cap height
X_START = -15.0 * U * 0.5
Y_TOP = 0.175       # back edge of the key field

ROWS = [
    (0.62, [15.0 / 13.0] * 13),
    (1.00, [1.0] * 13 + [2.0]),
    (1.00, [1.5] + [1.0] * 12 + [1.5]),
    (1.00, [1.75] + [1.0] * 11 + [2.25]),
    (1.00, [2.25] + [1.0] * 10 + [2.75]),
    (1.00, [1.25, 1.25, 1.25, 1.25, 6.0, 1.25, 1.25, 0.75, 0.75]),
]

y_cursor = Y_TOP
for ri, (row_h, widths) in enumerate(ROWS):
    h = row_h * U
    yc = y_cursor - h * 0.5
    x = X_START
    for ci, w in enumerate(widths):
        kw = w * U - GAP
        kh = h - GAP
        xc = x + w * U * 0.5
        mat = KEY_MOD if (w > 1.2 or row_h < 0.9) else KEY_CAP
        add_box("Key_%d_%d" % (ri, ci), (kw, kh, KEY_H),
                (xc, yc, TOP_Z + KEY_H * 0.5 - 0.0005),
                mat=mat, bevel=0.0006, seg=2)
        x += w * U
    y_cursor -= h

# arrow cluster: replace the two half keys on the bottom right with a 4-key set
arrow_x = X_START + 13.5 * U
arrow_y = y_cursor + U * 0.5
add_box("KeyArrowUp", (0.75 * U - GAP, 0.5 * U - GAP, KEY_H),
        (arrow_x + 0.375 * U, arrow_y + 0.25 * U, TOP_Z + KEY_H * 0.5 - 0.0005),
        mat=KEY_MOD, bevel=0.0006)
add_box("KeyArrowDown", (0.75 * U - GAP, 0.5 * U - GAP, KEY_H),
        (arrow_x + 0.375 * U, arrow_y - 0.25 * U, TOP_Z + KEY_H * 0.5 - 0.0005),
        mat=KEY_MOD, bevel=0.0006)
add_box("KeyArrowLeft", (0.75 * U - GAP, U - GAP, KEY_H),
        (arrow_x - 0.375 * U, arrow_y, TOP_Z + KEY_H * 0.5 - 0.0005),
        mat=KEY_MOD, bevel=0.0006)
add_box("KeyArrowRight", (0.75 * U - GAP, U - GAP, KEY_H),
        (arrow_x + 1.125 * U, arrow_y, TOP_Z + KEY_H * 0.5 - 0.0005),
        mat=KEY_MOD, bevel=0.0006)


# ----------------------------------------------------------------------------
# trackpad
# ----------------------------------------------------------------------------

TP_W, TP_D = 0.112, 0.068
TP_Y = 0.042
add_box("TrackpadRecess", (TP_W + 0.004, TP_D + 0.004, 0.003),
        (0.0, TP_Y, TOP_Z - 0.0016), mat=KEY_PLATE)
add_box("Trackpad", (TP_W, TP_D, 0.0018), (0.0, TP_Y, TOP_Z + 0.0001),
        mat=TRACKPAD, bevel=0.0004)


# ----------------------------------------------------------------------------
# hinge and lid
# ----------------------------------------------------------------------------

HINGE_Y = BASE_D - 0.008
HINGE_Z = TOP_Z - 0.002
for sx in (-1, 1):
    add_cyl("HingeBarrel_%d" % sx, 0.0062, 0.058,
            (sx * 0.105, HINGE_Y, HINGE_Z), rot=(0, math.radians(90), 0),
            mat=ALU_DARK, segments=24)
add_box("HingeStrip", (0.20, 0.014, 0.007), (0.0, HINGE_Y, HINGE_Z),
        mat=ALU_DARK, bevel=0.0015)

lid = bpy.data.objects.new("LidPivot", None)
lid.empty_display_size = 0.05
bpy.context.collection.objects.link(lid)
lid.location = (0.0, HINGE_Y, HINGE_Z)
lid.rotation_euler = (math.radians(-14.0), 0.0, 0.0)   # ~104 degrees open

LID_W, LID_T, LID_H = 0.335, 0.0105, 0.228

# lid shell: local +Y is the back of the screen, local Z runs up the lid
add_box("LidShell", (LID_W, LID_T, LID_H),
        (0.0, LID_T * 0.5, LID_H * 0.5 + 0.004),
        mat=ALU, bevel=0.0035, seg=4, parent=lid)
add_box("LidBezel", (LID_W - 0.008, 0.0016, LID_H - 0.008),
        (0.0, -0.0006, LID_H * 0.5 + 0.004), mat=BEZEL, parent=lid)

SCR_W, SCR_H = 0.306, 0.194
SCR_ZC = LID_H * 0.5 + 0.006
add_box("ScreenPanel", (SCR_W, 0.0012, SCR_H), (0.0, -0.0018, SCR_ZC),
        mat=SCREEN, parent=lid)

# a little on-screen content so the display reads as "on"
add_box("ScreenMenuBar", (SCR_W - 0.004, 0.0006, 0.009),
        (0.0, -0.0026, SCR_ZC + SCR_H * 0.5 - 0.006), mat=SCREEN_BAR,
        parent=lid)
add_box("ScreenWindow", (0.185, 0.0006, 0.112),
        (-0.022, -0.0026, SCR_ZC + 0.012), mat=SCREEN_UI, parent=lid)
add_box("ScreenWindowBar", (0.185, 0.0007, 0.010),
        (-0.022, -0.0030, SCR_ZC + 0.073), mat=SCREEN_BAR, parent=lid)
add_box("ScreenDock", (0.150, 0.0006, 0.014),
        (0.0, -0.0026, SCR_ZC - SCR_H * 0.5 + 0.012), mat=SCREEN_BAR,
        parent=lid)
for i in range(6):
    add_box("ScreenDockIcon_%d" % i, (0.010, 0.0008, 0.010),
            (-0.062 + i * 0.0248, -0.0031, SCR_ZC - SCR_H * 0.5 + 0.012),
            mat=SCREEN_UI, parent=lid)

# webcam and status dot in the top bezel
add_cyl("Webcam", 0.0022, 0.0012, (0.0, -0.0014, LID_H - 0.0035),
        rot=(math.radians(90), 0, 0), mat=GLASSY, segments=16, parent=lid)
add_cyl("WebcamLed", 0.0009, 0.0010, (0.008, -0.0014, LID_H - 0.0035),
        rot=(math.radians(90), 0, 0),
        mat=new_material("Led", (0.1, 0.02, 0.02), emission=(1.0, 0.25, 0.15),
                         emit_strength=2.0), segments=12, parent=lid)

# logo on the outside of the lid
add_cyl("LidLogo", 0.0135, 0.0008, (0.0, LID_T + 0.0004, LID_H * 0.55),
        rot=(math.radians(90), 0, 0), mat=ALU_DARK, segments=32, parent=lid)
add_cyl("LidLogoRing", 0.0175, 0.0005, (0.0, LID_T + 0.0002, LID_H * 0.55),
        rot=(math.radians(90), 0, 0), mat=ALU, segments=32, parent=lid)


# ----------------------------------------------------------------------------
# lighting and camera
# ----------------------------------------------------------------------------

add_light("Key", 'AREA', (-0.55, -0.55, 0.85), 90.0, (1.0, 0.97, 0.93),
          size=1.1, target=(0.0, 0.10, 0.06))
add_light("Fill", 'AREA', (0.75, -0.35, 0.45), 28.0, (0.80, 0.86, 1.0),
          size=1.2, target=(0.03, 0.12, 0.08))
add_light("Rim", 'AREA', (0.25, 1.05, 0.60), 45.0, (0.85, 0.90, 1.0),
          size=0.8, target=(0.0, 0.18, 0.14))
add_light("Top", 'AREA', (0.0, 0.20, 1.30), 40.0, (1.0, 1.0, 1.0),
          size=1.8, target=(0.0, 0.14, 0.05))

add_camera((0.44, -0.47, 0.315), (0.0, 0.105, 0.085), lens=52.0)

bpy.context.view_layer.update()
