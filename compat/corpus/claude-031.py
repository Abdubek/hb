"""claude-031 - Railway signal beside a short section of ballasted track.

Builds the scene from factory startup: ground, ballast bed, sleepers, rails with
fastenings, a three-aspect colour-light signal on a mast with ladder, relay
cabinet and cable trough, plus lighting and a camera.
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


def mat(name, col, rough=0.5, metal=0.0, emis=None, es=4.0, alpha=1.0):
    m = bpy.data.materials.new(name)
    m.use_nodes = True
    b = m.node_tree.nodes["Principled BSDF"]
    b.inputs["Base Color"].default_value = (col[0], col[1], col[2], 1.0)
    b.inputs["Roughness"].default_value = rough
    b.inputs["Metallic"].default_value = metal
    if emis is not None:
        b.inputs["Emission Color"].default_value = (emis[0], emis[1], emis[2], 1.0)
        b.inputs["Emission Strength"].default_value = es
    if alpha < 1.0:
        b.inputs["Alpha"].default_value = alpha
        try:
            m.blend_method = 'BLEND'
        except Exception:
            pass
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


def between(name, p1, p2, r, m=None, seg=12, r2=None):
    p1, p2 = Vector(p1), Vector(p2)
    d = p2 - p1
    return cyl(name, r, d.length, (p1 + p2) / 2.0,
               d.to_track_quat('Z', 'Y').to_euler(), seg=seg, r2=r2, m=m)


def prism(name, prof, length, loc=(0, 0, 0), rot=(0, 0, 0), m=None, tri=True):
    """Extrude a closed (x, z) profile along Y."""
    bm = bmesh.new()
    a, b = [], []
    for (x, z) in prof:
        a.append(bm.verts.new((x, -length / 2.0, z)))
        b.append(bm.verts.new((x, length / 2.0, z)))
    f1 = bm.faces.new(list(reversed(a)))
    f2 = bm.faces.new(b)
    n = len(prof)
    for i in range(n):
        j = (i + 1) % n
        bm.faces.new((a[i], a[j], b[j], b[i]))
    if tri:
        bmesh.ops.triangulate(bm, faces=[f1, f2])
    return finish(name, bm, m, None, loc, rot)


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


# ----------------------------------------------------------------- materials
setup((0.42, 0.55, 0.74), 1.0)

M_GRASS = mat("Grass", (0.13, 0.21, 0.08), 0.95)
M_BALLAST = mat("Ballast", (0.29, 0.27, 0.25), 0.95)
M_SLEEPER = mat("Sleeper", (0.40, 0.38, 0.36), 0.88)
M_RAIL = mat("RailSteel", (0.19, 0.15, 0.13), 0.60, 1.0)
M_HEAD = mat("RailHead", (0.74, 0.75, 0.77), 0.14, 1.0)
M_FIX = mat("Fastening", (0.26, 0.20, 0.16), 0.70, 1.0)
M_MAST = mat("GalvSteel", (0.55, 0.57, 0.59), 0.38, 0.9)
M_BODY = mat("SignalBody", (0.055, 0.06, 0.06), 0.45)
M_CONC = mat("Concrete", (0.52, 0.51, 0.48), 0.9)
M_WHITE = mat("WhitePlate", (0.86, 0.86, 0.84), 0.45)
M_CAB = mat("Cabinet", (0.36, 0.42, 0.38), 0.55, 0.3)
M_TROUGH = mat("CableTrough", (0.44, 0.43, 0.41), 0.9)
M_DARKGLASS = mat("DarkLens", (0.03, 0.03, 0.035), 0.12)
M_RED = mat("LensRed", (0.20, 0.01, 0.01), 0.12, emis=(1.0, 0.05, 0.02), es=0.6)
M_YEL = mat("LensYellow", (0.20, 0.13, 0.01), 0.12, emis=(1.0, 0.55, 0.05), es=0.6)
M_GRN = mat("LensGreen", (0.02, 0.25, 0.10), 0.10, emis=(0.10, 1.0, 0.35), es=26.0)

# ----------------------------------------------------------------- ground
bm = bmesh.new()
bbox(bm, (90.0, 90.0, 0.4), loc=(0.0, 0.0, -0.2))
finish("Ground", bm, M_GRASS)

# ----------------------------------------------------------------- track bed
TRACK_LEN = 16.0
BAL_H = 0.45
prism("Ballast",
      [(-3.35, 0.0), (3.35, 0.0), (2.25, BAL_H), (-2.25, BAL_H)],
      TRACK_LEN, m=M_BALLAST)

# sleepers + baseplates, batched into two meshes
GAUGE = 1.435
RX = GAUGE / 2.0
SLP_TOP = BAL_H + 0.11
bm_s = bmesh.new()
bm_f = bmesh.new()
spacing = 0.62
count = int(TRACK_LEN / spacing)
for i in range(count):
    y = -TRACK_LEN / 2.0 + spacing * (i + 0.5)
    bbox(bm_s, (2.60, 0.26, 0.20), loc=(0.0, y, SLP_TOP - 0.10))
    for sx in (-1.0, 1.0):
        bbox(bm_f, (0.24, 0.22, 0.018), loc=(sx * RX, y, SLP_TOP + 0.009))
        # rail clips either side of the foot
        for cx in (-0.10, 0.10):
            bbox(bm_f, (0.05, 0.09, 0.045),
                 loc=(sx * RX + cx, y, SLP_TOP + 0.040))
finish("Sleepers", bm_s, M_SLEEPER)
finish("Fastenings", bm_f, M_FIX)

# rails: flat-bottom profile extruded along Y
RAIL_BASE = SLP_TOP + 0.018
RAIL_PROFILE = [
    (-0.070, 0.000), (0.070, 0.000), (0.070, 0.018), (0.016, 0.048),
    (0.016, 0.112), (0.036, 0.132), (0.036, 0.156), (0.021, 0.172),
    (-0.021, 0.172), (-0.036, 0.156), (-0.036, 0.132), (-0.016, 0.112),
    (-0.016, 0.048), (-0.070, 0.018),
]
bm_h = bmesh.new()
for sx in (-1.0, 1.0):
    prism("Rail_%s" % ("L" if sx < 0 else "R"), RAIL_PROFILE, TRACK_LEN,
          loc=(sx * RX, 0.0, RAIL_BASE), m=M_RAIL)
    bbox(bm_h, (0.040, TRACK_LEN, 0.004),
         loc=(sx * RX, 0.0, RAIL_BASE + 0.1725))
finish("RailheadPolish", bm_h, M_HEAD)

# fishplated joint on the right rail
bm_j = bmesh.new()
for sy in (-1.0, 1.0):
    bbox(bm_j, (0.016, 0.62, 0.085), loc=(RX + sy * 0.030, 2.4, RAIL_BASE + 0.082))
    for by in (-0.22, -0.08, 0.08, 0.22):
        bcyl(bm_j, 0.014, 0.10, loc=(RX, 2.4 + by, RAIL_BASE + 0.082),
             rot=(0.0, math.pi / 2.0, 0.0), seg=8)
finish("Fishplate", bm_j, M_FIX, smooth=40.0)

# cable trough running alongside the ballast shoulder
bm_t = bmesh.new()
for i in range(13):
    y = -TRACK_LEN / 2.0 + 0.62 + i * 1.25
    bbox(bm_t, (0.36, 1.16, 0.30), loc=(-3.9, y, 0.15))
    bbox(bm_t, (0.40, 1.16, 0.04), loc=(-3.9, y, 0.32))
finish("CableTrough", bm_t, M_TROUGH)

# ----------------------------------------------------------------- signal
SX, SY = 3.05, 1.20
MAST_H = 5.30

box("SignalFoundation", (0.95, 0.95, 0.55), loc=(SX, SY, 0.20), m=M_CONC, bev=0.03)
cyl("MastFlange", 0.26, 0.06, (SX, SY, 0.50), seg=20, m=M_MAST)
cyl("Mast", 0.085, MAST_H, (SX, SY, 0.50 + MAST_H / 2.0), seg=20, r2=0.072, m=M_MAST)
cyl("MastCap", 0.095, 0.05, (SX, SY, 0.50 + MAST_H), seg=20, m=M_BODY)

# ladder up the rear of the mast
bm_l = bmesh.new()
for sx in (-0.20, 0.20):
    bcyl(bm_l, 0.020, 3.70, loc=(sx, 0.30, 2.55), seg=8)
rungs = 12
for i in range(rungs):
    z = 0.85 + i * 0.30
    bcyl(bm_l, 0.013, 0.40, loc=(0.0, 0.30, z), rot=(0.0, math.pi / 2.0, 0.0), seg=8)
for z in (1.5, 3.2, 4.3):
    bbox(bm_l, (0.04, 0.30, 0.04), loc=(0.20, 0.16, z))
    bbox(bm_l, (0.04, 0.30, 0.04), loc=(-0.20, 0.16, z))
ladder = finish("Ladder", bm_l, M_MAST, smooth=40.0, loc=(SX, SY, 0.0))

# backboard + signal head
box("Backboard", (1.10, 0.05, 2.05), loc=(SX, SY - 0.14, 4.55), m=M_BODY, bev=0.015)
box("SignalHead", (0.56, 0.34, 1.72), loc=(SX, SY - 0.32, 4.55), m=M_BODY, bev=0.02)
box("HeadBracket", (0.16, 0.22, 0.30), loc=(SX, SY - 0.06, 3.70), m=M_BODY)


def hood(name, r_in, r_out, depth, loc, material, segs=16):
    """Half-tube visor opening toward -Y."""
    bm = bmesh.new()
    rows = []
    for k in (0, 1):
        r = r_in if k == 0 else r_out
        y = -depth * k
        row = []
        for i in range(segs + 1):
            a = math.pi * i / segs
            row.append(bm.verts.new((math.cos(a) * r, y, math.sin(a) * r * 1.0)))
        rows.append(row)
    for i in range(segs):
        bm.faces.new((rows[0][i], rows[0][i + 1], rows[1][i + 1], rows[1][i]))
    return finish(name, bm, material, 40.0, loc)


lens_face_y = SY - 0.49
for (z, lm, nm) in ((5.10, M_RED, "Red"), (4.55, M_YEL, "Yellow"), (4.00, M_GRN, "Green")):
    cyl("LensRim_" + nm, 0.135, 0.06, (SX, lens_face_y + 0.01, z),
        rot=(math.pi / 2.0, 0.0, 0.0), seg=24, m=M_BODY)
    cyl("Lens_" + nm, 0.115, 0.03, (SX, lens_face_y - 0.025, z),
        rot=(math.pi / 2.0, 0.0, 0.0), seg=24, m=lm)
    hood("Hood_" + nm, 0.145, 0.185, 0.26, (SX, lens_face_y, z), M_BODY)

# identification plate and junction box
box("IdPlate", (0.30, 0.03, 0.42), loc=(SX, SY - 0.51, 3.35), m=M_WHITE, bev=0.008)
box("JunctionBox", (0.34, 0.26, 0.52), loc=(SX, SY - 0.24, 1.55), m=M_BODY, bev=0.015)
between("Conduit", (SX, SY - 0.24, 1.30), (SX, SY - 0.24, 0.55), 0.030, m=M_MAST)
between("ConduitRun", (SX, SY - 0.24, 0.16), (-3.72, SY - 0.24, 0.16), 0.030, m=M_BODY)

# relay cabinet further from the track
box("CabinetBase", (1.30, 0.85, 0.24), loc=(5.4, -2.2, 0.12), m=M_CONC)
box("RelayCabinet", (1.15, 0.70, 1.55), loc=(5.4, -2.2, 1.02), m=M_CAB, bev=0.02)
box("CabinetRoof", (1.28, 0.84, 0.06), loc=(5.4, -2.24, 1.82), m=M_CAB, bev=0.01)
bm_d = bmesh.new()
bcyl(bm_d, 0.022, 0.16, loc=(5.9, -1.84, 1.05), rot=(math.pi / 2.0, 0.0, 0.0), seg=10)
finish("CabinetHandle", bm_d, M_MAST, smooth=40.0)

# ----------------------------------------------------------------- lighting
sun = light('SUN', "Sun", (14.0, -18.0, 20.0), 3.4, (1.0, 0.95, 0.86),
            tgt=(1.0, 0.0, 2.0), angle=0.03)
light('AREA', "SkyFill", (-12.0, -14.0, 12.0), 900.0, (0.62, 0.74, 1.0),
      size=16.0, tgt=(1.5, 0.0, 2.0))
light('POINT', "GreenGlow", (SX, SY - 0.75, 4.00), 45.0, (0.25, 1.0, 0.45), size=0.12)
light('AREA', "RimLight", (-6.0, 12.0, 6.0), 500.0, (1.0, 0.88, 0.72),
      size=8.0, tgt=(2.0, 1.0, 3.0))

# ----------------------------------------------------------------- camera
cam((8.6, -10.4, 3.9), (2.0, 0.4, 2.6), lens=52.0)
