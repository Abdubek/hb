"""claude-034 - Refractor telescope on a tripod with adjustment knobs.

Three-section tripod with accessory tray, equatorial head with latitude wedge,
counterweight, slow-motion knobs, tube rings with locking knobs, focuser with
coarse/fine knobs, star diagonal, eyepiece and finderscope.
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


def bsph(bm, r, loc=(0, 0, 0), u=16, v=8):
    bmesh.ops.create_uvsphere(bm, u_segments=u, v_segments=v, radius=r,
                              matrix=MX(loc))


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


def between(name, p1, p2, r, m=None, seg=14, r2=None, parent=None):
    p1, p2 = Vector(p1), Vector(p2)
    d = p2 - p1
    return cyl(name, r, d.length, (p1 + p2) / 2.0,
               d.to_track_quat('Z', 'Y').to_euler(), seg=seg, r2=r2, m=m,
               parent=parent)


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
    e.empty_display_size = 0.08
    if parent:
        e.parent = parent
    return e


def knurled_knob(name, r, h, m, teeth=14, loc=(0, 0, 0), rot=(0, 0, 0),
                 parent=None, cap=True):
    """Cylindrical knob with a knurled rim, axis along local Z."""
    bm = bmesh.new()
    n = teeth * 2
    bot, top = [], []
    for i in range(n):
        a = 2.0 * math.pi * i / n
        rr = r if i % 2 == 0 else r * 0.86
        bot.append(bm.verts.new((math.cos(a) * rr, math.sin(a) * rr, -h / 2.0)))
        top.append(bm.verts.new((math.cos(a) * rr, math.sin(a) * rr, h / 2.0)))
    bm.faces.new(list(reversed(bot)))
    bm.faces.new(top)
    for i in range(n):
        j = (i + 1) % n
        bm.faces.new((bot[i], bot[j], top[j], top[i]))
    if cap:
        bcyl(bm, r * 0.55, h * 0.5, loc=(0.0, 0.0, h * 0.7), seg=16)
    return finish(name, bm, m, None, loc, rot, parent)


# ----------------------------------------------------------------- materials
setup((0.045, 0.052, 0.070), 1.0)

M_FLOOR = mat("Floor", (0.075, 0.078, 0.085), 0.80)
M_ALU = mat("Aluminium", (0.68, 0.69, 0.71), 0.28, 1.0)
M_ALU_DARK = mat("AnodisedGrey", (0.30, 0.31, 0.33), 0.35, 0.9)
M_WHITE = mat("TubeWhite", (0.86, 0.87, 0.88), 0.30)
M_BLACK = mat("BlackAnodised", (0.045, 0.046, 0.050), 0.38, 0.5)
M_PLASTIC = mat("Plastic", (0.085, 0.088, 0.095), 0.55)
M_BRASS = mat("Brass", (0.72, 0.55, 0.20), 0.28, 1.0)
M_RUBBER = mat("Rubber", (0.055, 0.055, 0.058), 0.85)
M_GLASS = mat("Objective", (0.06, 0.13, 0.22), 0.06, 0.2)
M_CHROME = mat("Chrome", (0.85, 0.86, 0.88), 0.10, 1.0)
M_RED = mat("RedAccent", (0.55, 0.05, 0.04), 0.35, 0.4)
M_COUNTER = mat("Counterweight", (0.16, 0.16, 0.17), 0.42, 0.85)

# ----------------------------------------------------------------- floor
bm = bmesh.new()
bbox(bm, (14.0, 14.0, 0.3), loc=(0.0, 0.0, -0.15))
finish("Floor", bm, M_FLOOR)

# ----------------------------------------------------------------- tripod
HEAD_Z = 1.02
SPREAD = 0.60
TRAY_Z = 0.36

cyl("TripodHead", 0.085, 0.030, (0.0, 0.0, HEAD_Z), seg=24, m=M_ALU_DARK)
cyl("TripodHeadTop", 0.070, 0.022, (0.0, 0.0, HEAD_Z + 0.026), seg=24, m=M_ALU_DARK)

for i in range(3):
    a = math.radians(90.0) + i * 2.0 * math.pi / 3.0
    ux, uy = math.cos(a), math.sin(a)
    hub = (ux * 0.075, uy * 0.075, HEAD_Z - 0.02)
    knee = (ux * (SPREAD * 0.55), uy * (SPREAD * 0.55), 0.44)
    foot = (ux * SPREAD, uy * SPREAD, 0.035)
    # upper channel section (square tube) and lower round tube
    d = Vector(knee) - Vector(hub)
    rot = d.to_track_quat('Z', 'Y').to_euler()
    box("LegUpper_%d" % i, (0.048, 0.030, d.length),
        loc=tuple((Vector(hub) + Vector(knee)) / 2.0), rot=rot, m=M_ALU, bev=0.004)
    d2 = Vector(foot) - Vector(knee)
    rot2 = d2.to_track_quat('Z', 'Y').to_euler()
    cyl("LegLower_%d" % i, 0.014, d2.length + 0.10,
        tuple((Vector(knee) + Vector(foot)) / 2.0 - d2.normalized() * 0.05),
        rot2, seg=16, m=M_ALU_DARK)
    # leg-lock clamp and knob at the joint
    box("LegClamp_%d" % i, (0.050, 0.038, 0.045), loc=knee, rot=rot,
        m=M_BLACK, bev=0.004)
    knurled_knob("LegKnob_%d" % i, 0.020, 0.016, M_BLACK, teeth=12,
                 loc=(knee[0] - uy * 0.035, knee[1] + ux * 0.035, knee[2]),
                 rot=(math.pi / 2.0, 0.0, a))
    # hinge at the head
    cyl("LegHinge_%d" % i, 0.017, 0.055, (ux * 0.072, uy * 0.072, HEAD_Z - 0.012),
        rot=(math.pi / 2.0, 0.0, a), seg=14, m=M_ALU_DARK)
    # rubber foot
    cyl("Foot_%d" % i, 0.024, 0.036, (foot[0], foot[1], 0.018), seg=16,
        r2=0.020, m=M_RUBBER)
    # brace from the accessory tray out to the leg
    tray_pt = (ux * 0.105, uy * 0.105, TRAY_Z)
    leg_pt = (ux * (SPREAD * 0.66), uy * (SPREAD * 0.66), TRAY_Z - 0.075)
    between("TrayBrace_%d" % i, tray_pt, leg_pt, 0.008, m=M_ALU_DARK, seg=10)

# accessory tray (hexagonal plate with eyepiece holes suggested by rings)
cyl("AccessoryTray", 0.135, 0.012, (0.0, 0.0, TRAY_Z), seg=6, m=M_BLACK)
bm = bmesh.new()
for i in range(3):
    a = i * 2.0 * math.pi / 3.0 + math.radians(60.0)
    bcyl(bm, 0.020, 0.014, loc=(math.cos(a) * 0.075, math.sin(a) * 0.075, TRAY_Z + 0.008),
         seg=16, r2=0.018)
finish("TrayHolders", bm, M_PLASTIC, smooth=40.0)
cyl("TrayBolt", 0.014, 0.030, (0.0, 0.0, TRAY_Z + 0.014), seg=14, m=M_ALU)

# ----------------------------------------------------------------- mount head
base = empty("MountBase", loc=(0.0, 0.0, HEAD_Z + 0.037), rot=(0.0, 0.0, math.radians(-25.0)))
cyl("AzBase", 0.062, 0.040, (0.0, 0.0, 0.020), seg=24, m=M_ALU_DARK, parent=base)
cyl("AzCollar", 0.052, 0.030, (0.0, 0.0, 0.052), seg=24, m=M_ALU, parent=base)
# azimuth adjusters
for sx in (-1.0, 1.0):
    knurled_knob("AzKnob_%s" % ("L" if sx < 0 else "R"), 0.016, 0.014, M_BLACK,
                 teeth=12, loc=(sx * 0.058, -0.030, 0.020),
                 rot=(math.pi / 2.0, 0.0, 0.0), parent=base)

LAT = math.radians(48.0)
wedge = empty("LatitudeWedge", loc=(0.0, 0.0, 0.070), rot=(LAT, 0.0, 0.0), parent=base)
box("WedgeBody", (0.090, 0.075, 0.075), loc=(0.0, 0.0, 0.020), m=M_ALU_DARK,
    bev=0.006, parent=base)
# latitude adjustment bolt with knob
knurled_knob("LatKnob", 0.020, 0.018, M_BLACK, teeth=14,
             loc=(0.0, -0.075, 0.030), rot=(math.pi / 2.0, 0.0, 0.0), parent=base)
cyl("LatBolt", 0.007, 0.060, (0.0, -0.048, 0.030), rot=(math.pi / 2.0, 0.0, 0.0),
    seg=12, m=M_CHROME, parent=base)

# right-ascension axis housing (along wedge local Z)
cyl("RaHousing", 0.042, 0.170, (0.0, 0.0, 0.075), seg=24, m=M_ALU_DARK, parent=wedge)
cyl("RaSetCircle", 0.052, 0.014, (0.0, 0.0, 0.148), seg=32, m=M_ALU, parent=wedge)
knurled_knob("RaLockKnob", 0.017, 0.015, M_BLACK, teeth=12,
             loc=(0.048, 0.0, 0.045), rot=(0.0, math.pi / 2.0, 0.0), parent=wedge)
# RA slow-motion cable knob
cyl("RaSlowShaft", 0.006, 0.130, (0.0, -0.050, 0.010),
    rot=(math.radians(72.0), 0.0, 0.0), seg=10, m=M_CHROME, parent=wedge)
knurled_knob("RaSlowKnob", 0.019, 0.040, M_BLACK, teeth=16,
             loc=(0.0, -0.104, -0.007), rot=(math.radians(72.0), 0.0, 0.0),
             parent=wedge, cap=False)

# counterweight shaft below the RA axis
cyl("CwShaft", 0.010, 0.320, (0.0, 0.0, -0.150), seg=16, m=M_CHROME, parent=wedge)
cyl("CwStop", 0.016, 0.016, (0.0, 0.0, -0.305), seg=16, m=M_BLACK, parent=wedge)
cyl("Counterweight", 0.058, 0.055, (0.0, 0.0, -0.205), seg=28, m=M_COUNTER, parent=wedge)
knurled_knob("CwLockKnob", 0.015, 0.014, M_BLACK, teeth=12,
             loc=(0.058, 0.0, -0.205), rot=(0.0, math.pi / 2.0, 0.0), parent=wedge)

# declination axis on top of the RA axis
dec = empty("DecAxis", loc=(0.0, 0.0, 0.175), rot=(0.0, math.radians(-58.0), 0.0),
            parent=wedge)
cyl("DecHousing", 0.040, 0.150, (0.0, 0.0, 0.0), rot=(math.pi / 2.0, 0.0, 0.0),
    seg=24, m=M_ALU_DARK, parent=dec)
cyl("DecSetCircle", 0.050, 0.012, (0.0, -0.078, 0.0), rot=(math.pi / 2.0, 0.0, 0.0),
    seg=32, m=M_ALU, parent=dec)
knurled_knob("DecLockKnob", 0.017, 0.015, M_BLACK, teeth=12,
             loc=(0.046, 0.030, 0.0), rot=(0.0, math.pi / 2.0, 0.0), parent=dec)
cyl("DecSlowShaft", 0.006, 0.110, (0.0, 0.055, -0.055),
    rot=(math.radians(-40.0), 0.0, 0.0), seg=10, m=M_CHROME, parent=dec)
knurled_knob("DecSlowKnob", 0.019, 0.038, M_BLACK, teeth=16,
             loc=(0.0, 0.090, -0.098), rot=(math.radians(-40.0), 0.0, 0.0),
             parent=dec, cap=False)

# ----------------------------------------------------------------- optical tube
ota = empty("OTA", loc=(0.0, 0.0, 0.048), rot=(0.0, 0.0, 0.0), parent=dec)
box("DovetailBar", (0.044, 0.340, 0.012), loc=(0.0, 0.0, -0.006), m=M_ALU,
    bev=0.002, parent=ota)

TUBE_R = 0.058
TUBE_Z = TUBE_R + 0.052
cyl("Tube", TUBE_R, 0.640, (0.0, 0.010, TUBE_Z), rot=(math.pi / 2.0, 0.0, 0.0),
    seg=32, m=M_WHITE, parent=ota)
cyl("DewShield", TUBE_R + 0.008, 0.130, (0.0, 0.375, TUBE_Z),
    rot=(math.pi / 2.0, 0.0, 0.0), seg=32, m=M_WHITE, parent=ota)
cyl("ObjectiveCell", TUBE_R + 0.004, 0.045, (0.0, 0.320, TUBE_Z),
    rot=(math.pi / 2.0, 0.0, 0.0), seg=32, m=M_BLACK, parent=ota)
cyl("ObjectiveLens", TUBE_R - 0.010, 0.010, (0.0, 0.318, TUBE_Z),
    rot=(math.pi / 2.0, 0.0, 0.0), seg=32, m=M_GLASS, parent=ota)
cyl("RearCell", TUBE_R + 0.006, 0.045, (0.0, -0.318, TUBE_Z),
    rot=(math.pi / 2.0, 0.0, 0.0), seg=32, m=M_BLACK, parent=ota)
bm = bmesh.new()
for y in (0.24, -0.24):
    bcyl(bm, TUBE_R + 0.003, 0.016, loc=(0.0, y, TUBE_Z), rot=(math.pi / 2.0, 0.0, 0.0),
         seg=32)
finish("TubeBands", bm, M_RED, smooth=40.0, parent=ota)

# tube rings with hinge and locking knobs
for i, y in enumerate((-0.105, 0.115)):
    bm = bmesh.new()
    bcyl(bm, TUBE_R + 0.014, 0.022, loc=(0.0, y, TUBE_Z), rot=(math.pi / 2.0, 0.0, 0.0),
         seg=32)
    bbox(bm, (0.030, 0.022, 0.048), loc=(0.0, y, TUBE_Z - TUBE_R - 0.030))
    finish("TubeRing_%d" % i, bm, M_BLACK, smooth=40.0, parent=ota)
    knurled_knob("RingKnob_%d" % i, 0.017, 0.014, M_BLACK, teeth=12,
                 loc=(TUBE_R + 0.030, y, TUBE_Z - 0.010),
                 rot=(0.0, math.pi / 2.0, 0.0), parent=ota)

# focuser assembly at the rear, drawtube going -Y
box("FocuserBody", (0.070, 0.085, 0.062), loc=(0.0, -0.372, TUBE_Z), m=M_BLACK,
    bev=0.005, parent=ota)
cyl("DrawTube", 0.021, 0.075, (0.0, -0.440, TUBE_Z), rot=(math.pi / 2.0, 0.0, 0.0),
    seg=24, m=M_CHROME, parent=ota)
for sx, r, nm in ((1.0, 0.024, "Coarse"), (-1.0, 0.024, "CoarseL")):
    cyl("FocusShaft_" + nm, 0.006, 0.030, (sx * 0.042, -0.372, TUBE_Z),
        rot=(0.0, math.pi / 2.0, 0.0), seg=10, m=M_CHROME, parent=ota)
    knurled_knob("FocusKnob_" + nm, r, 0.020, M_BLACK, teeth=18,
                 loc=(sx * 0.062, -0.372, TUBE_Z), rot=(0.0, math.pi / 2.0, 0.0),
                 parent=ota, cap=False)
knurled_knob("FineFocusKnob", 0.013, 0.016, M_ALU, teeth=14,
             loc=(0.079, -0.372, TUBE_Z), rot=(0.0, math.pi / 2.0, 0.0), parent=ota)
knurled_knob("FocusTensionKnob", 0.012, 0.012, M_BLACK, teeth=10,
             loc=(0.0, -0.372, TUBE_Z + 0.040), parent=ota)

# star diagonal + eyepiece
diag = empty("Diagonal", loc=(0.0, -0.480, TUBE_Z), parent=ota)
box("DiagonalBody", (0.048, 0.055, 0.055), loc=(0.0, -0.014, 0.010), m=M_BLACK,
    bev=0.006, parent=diag)
cyl("DiagonalNose", 0.019, 0.030, (0.0, 0.014, 0.0), rot=(math.pi / 2.0, 0.0, 0.0),
    seg=20, m=M_CHROME, parent=diag)
knurled_knob("DiagonalLock", 0.011, 0.012, M_BLACK, teeth=10,
             loc=(0.030, 0.012, 0.0), rot=(0.0, math.pi / 2.0, 0.0), parent=diag)
cyl("EyepieceBarrel", 0.018, 0.035, (0.0, -0.014, 0.048), seg=20, m=M_CHROME,
    parent=diag)
cyl("EyepieceBody", 0.023, 0.055, (0.0, -0.014, 0.090), seg=24, r2=0.026,
    m=M_BLACK, parent=diag)
cyl("EyeCup", 0.028, 0.016, (0.0, -0.014, 0.124), seg=24, r2=0.024, m=M_RUBBER,
    parent=diag)
knurled_knob("EyepieceLock", 0.010, 0.011, M_BLACK, teeth=10,
             loc=(0.030, -0.014, 0.050), rot=(0.0, math.pi / 2.0, 0.0), parent=diag)

# finderscope on its bracket with adjustment screws
fx = -(TUBE_R + 0.055)
bm = bmesh.new()
for y in (-0.185, -0.095):
    bbox(bm, (0.030, 0.016, 0.052), loc=(-0.030, y, TUBE_Z + 0.040))
    bcyl(bm, 0.026, 0.014, loc=(fx, y, TUBE_Z + 0.062), rot=(math.pi / 2.0, 0.0, 0.0),
         seg=20)
finish("FinderBracket", bm, M_BLACK, smooth=40.0, parent=ota)
cyl("FinderTube", 0.017, 0.180, (fx, -0.140, TUBE_Z + 0.062),
    rot=(math.pi / 2.0, 0.0, 0.0), seg=24, m=M_BLACK, parent=ota)
cyl("FinderObjective", 0.020, 0.020, (fx, -0.052, TUBE_Z + 0.062),
    rot=(math.pi / 2.0, 0.0, 0.0), seg=24, m=M_BLACK, parent=ota)
cyl("FinderLens", 0.014, 0.006, (fx, -0.046, TUBE_Z + 0.062),
    rot=(math.pi / 2.0, 0.0, 0.0), seg=20, m=M_GLASS, parent=ota)
cyl("FinderEyepiece", 0.012, 0.030, (fx, -0.242, TUBE_Z + 0.062),
    rot=(math.pi / 2.0, 0.0, 0.0), seg=20, m=M_BLACK, parent=ota)
for i, y in enumerate((-0.185, -0.095)):
    for k in range(3):
        a = math.radians(30.0) + k * 2.0 * math.pi / 3.0
        knurled_knob("FinderAdj_%d_%d" % (i, k), 0.008, 0.010, M_ALU, teeth=8,
                     loc=(fx + math.cos(a) * 0.032, y,
                          TUBE_Z + 0.062 + math.sin(a) * 0.032),
                     rot=(0.0, math.pi / 2.0 + a, 0.0), parent=ota, cap=False)

# ----------------------------------------------------------------- lighting
light('AREA', "Key", (1.6, -1.7, 2.4), 700.0, (1.0, 0.96, 0.90), size=2.2,
      tgt=(0.0, 0.0, 1.2))
light('AREA', "Fill", (-2.1, -1.2, 1.1), 180.0, (0.60, 0.72, 1.0), size=3.0,
      tgt=(0.0, 0.0, 1.1))
light('AREA', "Rim", (-0.9, 2.2, 2.0), 400.0, (0.80, 0.88, 1.0), size=1.6,
      tgt=(0.0, 0.0, 1.3))
light('SUN', "Ambient", (0.0, 0.0, 6.0), 0.5, (0.75, 0.82, 1.0),
      tgt=(0.0, 0.0, 0.0), angle=0.5)

# ----------------------------------------------------------------- camera
cam((1.45, -1.95, 1.45), (0.0, -0.05, 1.05), lens=55.0)
