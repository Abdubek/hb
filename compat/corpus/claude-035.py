"""claude-035 - Mechanical keyboard (tenkeyless) with rows of coloured keycaps.

Sculpted-profile keycaps generated per row, switch housings visible in the
gaps, aluminium case with plate and feet, USB-C cable, and studio lighting.
"""

import bpy
import bmesh
import math
from mathutils import Vector, Matrix, Euler


# ----------------------------------------------------------------- utilities
def setup(bg=(0.05, 0.06, 0.08), s=1.0):
    bpy.ops.wm.read_factory_settings(use_empty=True)
    sc = bpy.context.scene
    try:
        sc.render.engine = 'BLENDER_EEVEE_NEXT'
    except Exception:
        pass
    sc.render.resolution_x, sc.render.resolution_y = 1920, 1080
    w = bpy.data.worlds.new("World")
    sc.world = w
    w.use_nodes = True
    n = w.node_tree.nodes["Background"]
    n.inputs[0].default_value = (bg[0], bg[1], bg[2], 1.0)
    n.inputs[1].default_value = s
    return sc


def mat(name, col, rough=0.5, metal=0.0, emis=None, es=4.0):
    m = bpy.data.materials.new(name)
    m.use_nodes = True
    b = m.node_tree.nodes["Principled BSDF"]
    b.inputs["Base Color"].default_value = (col[0], col[1], col[2], 1.0)
    b.inputs["Roughness"].default_value = rough
    b.inputs["Metallic"].default_value = metal
    if emis is not None:
        b.inputs["Emission Color"].default_value = (emis[0], emis[1], emis[2], 1.0)
        b.inputs["Emission Strength"].default_value = es
    return m


def MX(loc=(0, 0, 0), rot=(0, 0, 0), scl=(1, 1, 1)):
    return (Matrix.Translation(loc)
            @ Euler(rot, 'XYZ').to_matrix().to_4x4()
            @ Matrix.Diagonal(Vector((scl[0], scl[1], scl[2], 1.0))))


def bbox(bm, size, loc=(0, 0, 0), rot=(0, 0, 0)):
    bmesh.ops.create_cube(bm, size=1.0, matrix=MX(loc, rot, size))


def bcyl(bm, r, d, loc=(0, 0, 0), rot=(0, 0, 0), seg=16, r2=None, cap=True):
    bmesh.ops.create_cone(bm, cap_ends=cap, cap_tris=False, segments=seg,
                          radius1=r, radius2=(r if r2 is None else r2),
                          depth=d, matrix=MX(loc, rot))


def shade(ob, angle=35.0):
    for p in ob.data.polygons:
        p.use_smooth = True
    try:
        bpy.context.view_layer.objects.active = ob
        ob.select_set(True)
        bpy.ops.object.shade_smooth_by_angle(angle=math.radians(angle))
        ob.select_set(False)
    except Exception:
        pass


def finish(name, bm, m=None, smooth=None, loc=(0, 0, 0), rot=(0, 0, 0), parent=None):
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    me = bpy.data.meshes.new(name)
    bm.to_mesh(me)
    bm.free()
    me.validate()
    ob = bpy.data.objects.new(name, me)
    bpy.context.scene.collection.objects.link(ob)
    ob.location = loc
    ob.rotation_euler = rot
    if m:
        me.materials.append(m)
    if smooth:
        shade(ob, smooth)
    if parent:
        ob.parent = parent
    return ob


def cyl(name, r, d, loc=(0, 0, 0), rot=(0, 0, 0), seg=24, r2=None, m=None,
        smooth=35.0, cap=True, parent=None):
    bm = bmesh.new()
    bcyl(bm, r, d, seg=seg, r2=r2, cap=cap)
    return finish(name, bm, m, smooth, loc, rot, parent)


def box(name, size, loc=(0, 0, 0), rot=(0, 0, 0), m=None, bev=0.0, seg=2, parent=None):
    bm = bmesh.new()
    bbox(bm, size)
    if bev > 0.0:
        bmesh.ops.bevel(bm, geom=list(bm.verts) + list(bm.edges) + list(bm.faces),
                        offset=bev, segments=seg, profile=0.5, affect='EDGES',
                        clamp_overlap=True)
    return finish(name, bm, m, None, loc, rot, parent)


def cam(loc, tgt, lens=50.0):
    c = bpy.data.cameras.new("Camera")
    c.lens = lens
    ob = bpy.data.objects.new("Camera", c)
    bpy.context.scene.collection.objects.link(ob)
    ob.location = loc
    ob.rotation_euler = (Vector(tgt) - Vector(loc)).to_track_quat('-Z', 'Y').to_euler()
    bpy.context.scene.camera = ob
    return ob


def light(kind, name, loc, energy, col=(1, 1, 1), size=1.0, tgt=None, angle=0.05):
    l = bpy.data.lights.new(name, kind)
    l.energy = energy
    l.color = col
    if kind == 'AREA':
        l.size = size
    elif kind == 'SUN':
        l.angle = angle
    elif kind == 'POINT':
        l.shadow_soft_size = size
    ob = bpy.data.objects.new(name, l)
    bpy.context.scene.collection.objects.link(ob)
    ob.location = loc
    if tgt is not None:
        ob.rotation_euler = (Vector(tgt) - Vector(loc)).to_track_quat('-Z', 'Y').to_euler()
    return ob


def empty(name, loc=(0, 0, 0), rot=(0, 0, 0), parent=None):
    e = bpy.data.objects.new(name, None)
    bpy.context.scene.collection.objects.link(e)
    e.location = loc
    e.rotation_euler = rot
    e.empty_display_size = 0.05
    if parent:
        e.parent = parent
    return e


# ----------------------------------------------------------------- materials
setup((0.030, 0.033, 0.040), 1.0)

M_DESK = mat("Desk", (0.115, 0.085, 0.060), 0.62)
M_CASE = mat("CaseAlu", (0.115, 0.120, 0.130), 0.35, 0.85)
M_PLATE = mat("Plate", (0.030, 0.031, 0.034), 0.55, 0.4)
M_SWITCH = mat("SwitchHousing", (0.040, 0.042, 0.050), 0.60)
M_STEM = mat("SwitchStem", (0.45, 0.05, 0.06), 0.55)
M_FOOT = mat("RubberFoot", (0.030, 0.030, 0.032), 0.85)
M_CABLE = mat("Cable", (0.075, 0.078, 0.085), 0.60)
M_CONN = mat("Connector", (0.55, 0.56, 0.58), 0.30, 0.9)
M_GLOW = mat("Underglow", (0.10, 0.35, 0.55), 0.4, emis=(0.15, 0.55, 1.0), es=9.0)

KEY_MATS = {
    'alpha': mat("CapAlpha", (0.865, 0.860, 0.840), 0.42),
    'mod': mat("CapMod", (0.240, 0.255, 0.275), 0.44),
    'accent': mat("CapAccent", (0.855, 0.290, 0.120), 0.42),
    'nav': mat("CapNav", (0.090, 0.470, 0.480), 0.42),
    'fn': mat("CapFn", (0.175, 0.190, 0.210), 0.44),
    'space': mat("CapSpace", (0.800, 0.795, 0.775), 0.42),
    'arrow': mat("CapArrow", (0.930, 0.700, 0.160), 0.42),
}

# ----------------------------------------------------------------- layout data
U = 0.01905
GAP = 0.0010

# row -> (cap height, tilt degrees)
ROW_PROFILE = {
    0: (0.0088, -2.0),
    1: (0.0112, -7.0),
    2: (0.0104, -4.0),
    3: (0.0100, 0.0),
    4: (0.0104, 4.0),
    5: (0.0112, 7.0),
}

keys = []   # (x_units_left_edge, row_index, y_units_from_top, width_u, group)


def add_row(y_u, row_idx, spec):
    x = 0.0
    for item in spec:
        if isinstance(item, tuple):
            w, grp = item
            keys.append((x, row_idx, y_u, w, grp))
            x += w
        else:
            x += item     # bare number = gap in units


# function row
add_row(0.0, 0, [(1.0, 'accent'), 1.0,
                 (1.0, 'fn'), (1.0, 'fn'), (1.0, 'fn'), (1.0, 'fn'), 0.5,
                 (1.0, 'fn'), (1.0, 'fn'), (1.0, 'fn'), (1.0, 'fn'), 0.5,
                 (1.0, 'fn'), (1.0, 'fn'), (1.0, 'fn'), (1.0, 'fn')])
# number row
add_row(1.5, 1, [(1.0, 'mod')] + [(1.0, 'alpha')] * 12 + [(2.0, 'mod')])
# qwerty row
add_row(2.5, 2, [(1.5, 'mod')] + [(1.0, 'alpha')] * 12 + [(1.5, 'mod')])
# home row
add_row(3.5, 3, [(1.75, 'mod')] + [(1.0, 'alpha')] * 11 + [(2.25, 'mod')])
# shift row
add_row(4.5, 4, [(2.25, 'mod')] + [(1.0, 'alpha')] * 10 + [(2.75, 'mod')])
# bottom row
add_row(5.5, 5, [(1.25, 'mod'), (1.25, 'mod'), (1.25, 'mod'), (6.25, 'space'),
                 (1.25, 'mod'), (1.25, 'mod'), (1.25, 'mod'), (1.25, 'mod')])

# navigation cluster
NAVX = 15.25
for i in range(3):
    keys.append((NAVX + i, 0, 0.0, 1.0, 'fn'))
for i in range(3):
    keys.append((NAVX + i, 1, 1.5, 1.0, 'nav'))
    keys.append((NAVX + i, 2, 2.5, 1.0, 'nav'))
keys.append((NAVX + 1, 4, 4.5, 1.0, 'arrow'))
for i in range(3):
    keys.append((NAVX + i, 5, 5.5, 1.0, 'arrow'))

BOARD_W_U = NAVX + 3.0            # 18.25 u
BOARD_D_U = 6.5                   # 6.5 u including the function-row gap
KEYS_W = BOARD_W_U * U
KEYS_D = BOARD_D_U * U


# ----------------------------------------------------------------- keycap mesh
def keycap(name, wu, du, row, material, parent, x, y, z):
    h, tilt = ROW_PROFILE[row]
    w = wu * U - GAP
    d = du * U - GAP
    hw, hd = w / 2.0, d / 2.0
    tw, td = hw - 0.0019, hd - 0.0019
    dish = 0.00075
    perim = [(1, 1), (0, 1), (-1, 1), (-1, 0), (-1, -1), (0, -1), (1, -1), (1, 0)]

    bm = bmesh.new()
    bot, top = [], []
    for (sx, sy) in perim:
        bot.append(bm.verts.new((sx * hw, sy * hd, 0.0)))
        top.append(bm.verts.new((sx * tw, sy * td, h - dish * (1.0 - sy * sy))))
    centre = bm.verts.new((0.0, 0.0, h - dish))
    n = len(perim)
    for i in range(n):
        j = (i + 1) % n
        bm.faces.new((bot[i], bot[j], top[j], top[i]))
        bm.faces.new((top[i], top[j], centre))
    bm.faces.new(list(reversed(bot)))
    bmesh.ops.bevel(bm, geom=list(bm.verts) + list(bm.edges) + list(bm.faces),
                    offset=0.00055, segments=2, profile=0.5, affect='EDGES',
                    clamp_overlap=True)
    return finish(name, bm, material, 34.0, (x, y, z),
                  (math.radians(tilt), 0.0, 0.0), parent)


# ----------------------------------------------------------------- assembly
root = empty("Keyboard", loc=(0.0, 0.0, 0.0265), rot=(math.radians(6.0), 0.0, 0.0))

# case, plate, bezel
CASE_W = KEYS_W + 0.014
CASE_D = KEYS_D + 0.014
box("Case", (CASE_W, CASE_D, 0.028), loc=(0.0, 0.0, -0.0125), m=M_CASE,
    bev=0.0022, seg=3, parent=root)
box("Plate", (KEYS_W + 0.004, KEYS_D + 0.004, 0.0018), loc=(0.0, 0.0, -0.0009),
    m=M_PLATE, parent=root)
box("Underglow", (CASE_W - 0.006, CASE_D - 0.006, 0.0022),
    loc=(0.0, 0.0, -0.0262), m=M_GLOW, parent=root)

# rubber feet and USB-C port
bm = bmesh.new()
for sx in (-1.0, 1.0):
    for sy in (-1.0, 1.0):
        bcyl(bm, 0.0055, 0.0030, loc=(sx * (CASE_W / 2.0 - 0.020),
                                      sy * (CASE_D / 2.0 - 0.016), -0.0265), seg=14)
finish("Feet", bm, M_FOOT, smooth=40.0, parent=root)
box("UsbPort", (0.0110, 0.0060, 0.0038), loc=(0.0, CASE_D / 2.0 - 0.0015, -0.0135),
    m=M_PLATE, parent=root)

# switches (single batched mesh) + keycaps
bm_sw = bmesh.new()
bm_st = bmesh.new()
for (xu, row, yu, wu, grp) in keys:
    x = (xu + wu / 2.0) * U - KEYS_W / 2.0
    y = KEYS_D / 2.0 - (yu + 0.5) * U
    bbox(bm_sw, (0.0152, 0.0152, 0.0090), loc=(x, y, -0.0047))
    bbox(bm_sw, (0.0139, 0.0139, 0.0016), loc=(x, y, 0.0006))
    bbox(bm_st, (0.0042, 0.0042, 0.0034), loc=(x, y, 0.0022))
    bbox(bm_st, (0.0012, 0.0110, 0.0034), loc=(x, y, 0.0022))
    bbox(bm_st, (0.0110, 0.0012, 0.0034), loc=(x, y, 0.0022))
    keycap("Key_%s_%.2f_%d" % (grp, xu, row), wu, 1.0, row,
           KEY_MATS[grp], root, x, y, 0.0016)
    # stabiliser stems on wide keys
    if wu >= 2.0:
        off = (wu / 2.0 - 0.62) * U
        for sx in (-1.0, 1.0):
            bbox(bm_sw, (0.0100, 0.0110, 0.0060), loc=(x + sx * off, y, -0.0032))
finish("Switches", bm_sw, M_SWITCH, parent=root)
finish("SwitchStems", bm_st, M_STEM, parent=root)

# ----------------------------------------------------------------- cable
curve = bpy.data.curves.new("CableCurve", 'CURVE')
curve.dimensions = '3D'
curve.bevel_depth = 0.0024
curve.bevel_resolution = 4
curve.resolution_u = 12
sp = curve.splines.new('BEZIER')
pts = [(0.0, CASE_D / 2.0 + 0.004, -0.013),
       (0.0, CASE_D / 2.0 + 0.055, -0.005),
       (-0.055, CASE_D / 2.0 + 0.130, -0.020),
       (-0.160, CASE_D / 2.0 + 0.190, -0.024),
       (-0.300, CASE_D / 2.0 + 0.150, -0.024)]
sp.bezier_points.add(len(pts) - 1)
for bp, p in zip(sp.bezier_points, pts):
    bp.co = p
    bp.handle_left_type = 'AUTO'
    bp.handle_right_type = 'AUTO'
cable = bpy.data.objects.new("Cable", curve)
bpy.context.scene.collection.objects.link(cable)
cable.data.materials.append(M_CABLE)
cable.parent = root

box("CableStrain", (0.0090, 0.0140, 0.0075),
    loc=(0.0, CASE_D / 2.0 + 0.010, -0.0130), m=M_CABLE, bev=0.001, parent=root)
cyl("CableConnector", 0.0038, 0.0100, (0.0, CASE_D / 2.0 + 0.0005, -0.0130),
    rot=(math.pi / 2.0, 0.0, 0.0), seg=14, m=M_CONN, parent=root)

# ----------------------------------------------------------------- desk
bm = bmesh.new()
bbox(bm, (3.0, 2.2, 0.05), loc=(0.0, 0.0, -0.025))
finish("Desk", bm, M_DESK)

# ----------------------------------------------------------------- lighting
light('AREA', "Key", (0.30, -0.34, 0.46), 90.0, (1.0, 0.96, 0.91), size=0.55,
      tgt=(0.0, -0.01, 0.02))
light('AREA', "Fill", (-0.42, -0.22, 0.24), 28.0, (0.62, 0.74, 1.0), size=0.80,
      tgt=(0.0, 0.0, 0.02))
light('AREA', "Rim", (-0.18, 0.40, 0.30), 45.0, (0.85, 0.92, 1.0), size=0.45,
      tgt=(0.0, 0.02, 0.03))
light('AREA', "Top", (0.0, 0.02, 0.70), 40.0, (1.0, 1.0, 1.0), size=1.2,
      tgt=(0.0, 0.0, 0.0))

# ----------------------------------------------------------------- camera
cam((0.235, -0.295, 0.215), (-0.005, -0.010, 0.014), lens=50.0)
