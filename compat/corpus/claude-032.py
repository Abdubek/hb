"""claude-032 - Four-way traffic intersection with mast-arm signals and bollards.

Roads, curbs, sidewalks, lane and crosswalk markings, four signal assemblies
(vehicle heads on mast arms, pedestrian heads, push buttons) and rows of
bollards along the corner sidewalks.
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
    e.empty_display_size = 0.5
    if parent:
        e.parent = parent
    return e


def rz(x, y, a):
    ca, sa = math.cos(a), math.sin(a)
    return (x * ca - y * sa, x * sa + y * ca)


# ----------------------------------------------------------------- materials
setup((0.44, 0.56, 0.74), 1.0)

M_GRASS = mat("Grass", (0.14, 0.23, 0.09), 0.95)
M_ASPHALT = mat("Asphalt", (0.055, 0.056, 0.060), 0.88)
M_WALK = mat("Sidewalk", (0.52, 0.51, 0.49), 0.92)
M_CURB = mat("Curb", (0.62, 0.61, 0.58), 0.85)
M_WHITE = mat("PaintWhite", (0.86, 0.86, 0.84), 0.60)
M_YELLOW = mat("PaintYellow", (0.78, 0.60, 0.06), 0.60)
M_POLE = mat("PoleGrey", (0.36, 0.38, 0.39), 0.42, 0.85)
M_HOUSING = mat("SignalHousing", (0.06, 0.16, 0.09), 0.45)
M_BLACK = mat("MattBlack", (0.035, 0.035, 0.04), 0.55)
M_BOLLARD = mat("Bollard", (0.10, 0.11, 0.12), 0.40, 0.6)
M_REFLECT = mat("Reflector", (0.85, 0.85, 0.85), 0.25, emis=(0.9, 0.9, 0.85), es=1.2)
M_SIGN = mat("SignGreen", (0.03, 0.22, 0.11), 0.45)
M_DARKLENS = mat("LensOff", (0.03, 0.03, 0.035), 0.15)
M_RED = mat("LensRed", (0.25, 0.01, 0.01), 0.12, emis=(1.0, 0.06, 0.03), es=18.0)
M_AMBER = mat("LensAmber", (0.22, 0.12, 0.01), 0.12, emis=(1.0, 0.5, 0.05), es=1.0)
M_GREEN = mat("LensGreen", (0.02, 0.24, 0.10), 0.12, emis=(0.1, 1.0, 0.35), es=18.0)
M_PEDRED = mat("PedRed", (0.25, 0.03, 0.02), 0.2, emis=(1.0, 0.2, 0.1), es=10.0)
M_LUM = mat("Luminaire", (0.75, 0.76, 0.78), 0.35, 0.8)

# ----------------------------------------------------------------- roadway
RW = 6.0          # half width of carriageway
SW = 5.0          # sidewalk width
EXT = 42.0        # road extent from centre
CURB = 0.16

bm = bmesh.new()
bbox(bm, (2 * EXT, 2 * EXT, 0.4), loc=(0.0, 0.0, -0.2))
finish("Ground", bm, M_GRASS)

bm = bmesh.new()
bbox(bm, (2 * RW, 2 * EXT, 0.12), loc=(0.0, 0.0, 0.06))
bbox(bm, (2 * EXT, 2 * RW, 0.12), loc=(0.0, 0.0, 0.06))
finish("Roadway", bm, M_ASPHALT)

# sidewalks: eight strips forming the four corner L shapes
bm = bmesh.new()
bm_c = bmesh.new()
for sx in (-1.0, 1.0):
    for sy in (-1.0, 1.0):
        ylen = EXT - RW
        bbox(bm, (SW, ylen, CURB),
             loc=(sx * (RW + SW / 2.0), sy * (RW + ylen / 2.0), CURB / 2.0))
        bbox(bm, (ylen, SW, CURB),
             loc=(sx * (RW + ylen / 2.0), sy * (RW + SW / 2.0), CURB / 2.0))
        # curb faces along the carriageway edges
        bbox(bm_c, (0.16, ylen, CURB + 0.04),
             loc=(sx * (RW + 0.08), sy * (RW + ylen / 2.0), (CURB + 0.04) / 2.0))
        bbox(bm_c, (ylen, 0.16, CURB + 0.04),
             loc=(sx * (RW + ylen / 2.0), sy * (RW + 0.08), (CURB + 0.04) / 2.0))
        # rounded corner return
        for k in range(6):
            a = math.pi * 0.5 * k / 5.0
            bbox(bm_c, (0.16, 0.16, CURB + 0.04),
                 loc=(sx * (RW + 0.08) * math.cos(a) + sx * 0.0,
                      sy * (RW + 0.08) * math.sin(a), (CURB + 0.04) / 2.0))
finish("Sidewalks", bm, M_WALK)
finish("Curbs", bm_c, M_CURB)

# ----------------------------------------------------------------- markings
Z_MARK = 0.125
bm_w = bmesh.new()
bm_y = bmesh.new()
for k in range(4):
    a = k * math.pi / 2.0
    # double yellow centre line on each approach
    for ox in (-0.30, 0.30):
        ln = EXT - (RW + 3.0)
        cx, cy = rz(ox, RW + 3.0 + ln / 2.0, a)
        bbox(bm_y, (0.14, ln, 0.02), loc=(cx, cy, Z_MARK), rot=(0, 0, a))
    # dashed lane divider
    for i in range(4):
        y0 = RW + 5.0 + i * 9.0
        for ox in (-3.1, 3.1):
            cx, cy = rz(ox, y0 + 2.25, a)
            bbox(bm_w, (0.13, 4.5, 0.02), loc=(cx, cy, Z_MARK), rot=(0, 0, a))
    # stop bar on the near half of the approach
    cx, cy = rz(-RW / 2.0, RW + 4.4, a)
    bbox(bm_w, (RW - 0.4, 0.55, 0.02), loc=(cx, cy, Z_MARK), rot=(0, 0, a))
    # zebra crossing
    nstripes = 11
    for i in range(nstripes):
        x = -RW + 0.55 + i * ((2 * RW - 1.1) / (nstripes - 1))
        cx, cy = rz(x, RW + 2.5, a)
        bbox(bm_w, (0.55, 2.9, 0.02), loc=(cx, cy, Z_MARK), rot=(0, 0, a))
finish("MarkingsWhite", bm_w, M_WHITE)
finish("MarkingsYellow", bm_y, M_YELLOW)

# drainage inlets at the corners
bm = bmesh.new()
for sx in (-1.0, 1.0):
    for sy in (-1.0, 1.0):
        bbox(bm, (0.75, 0.45, 0.03), loc=(sx * (RW - 0.5), sy * (RW - 0.35), 0.125))
finish("Drains", bm, M_BLACK)


# ----------------------------------------------------------------- signals
def signal_head(name, parent, loc, lit, backplate=True):
    """Three-aspect vehicle head; lenses face -X in the local frame."""
    if backplate:
        box(name + "_Backplate", (0.05, 0.95, 1.55), loc=(loc[0] + 0.16, loc[1], loc[2]),
            m=M_BLACK, bev=0.01, parent=parent)
    box(name + "_Body", (0.30, 0.42, 1.32), loc=loc, m=M_HOUSING, bev=0.02, parent=parent)
    aspects = ((0.44, M_RED if lit == 'RED' else M_DARKLENS),
               (0.0, M_AMBER if lit == 'AMBER' else M_DARKLENS),
               (-0.44, M_GREEN if lit == 'GREEN' else M_DARKLENS))
    for i, (dz, lm) in enumerate(aspects):
        p = (loc[0] - 0.16, loc[1], loc[2] + dz)
        cyl(name + "_Rim%d" % i, 0.135, 0.05, p, rot=(0.0, math.pi / 2.0, 0.0),
            seg=20, m=M_HOUSING, parent=parent)
        cyl(name + "_Lens%d" % i, 0.115, 0.035, (p[0] - 0.03, p[1], p[2]),
            rot=(0.0, math.pi / 2.0, 0.0), seg=20, m=lm, parent=parent)
        # visor
        cyl(name + "_Visor%d" % i, 0.150, 0.20, (p[0] - 0.11, p[1], p[2] + 0.03),
            rot=(0.0, math.pi / 2.0, 0.0), seg=18, r2=0.170, m=M_HOUSING,
            cap=False, parent=parent)


def signal_assembly(index, corner, zrot, lit):
    root = empty("SignalRoot_%d" % index, loc=(corner[0], corner[1], 0.0),
                 rot=(0.0, 0.0, zrot))
    # foundation and pole (arm reaches out along local -X, over the road)
    cyl("Base_%d" % index, 0.42, 0.30, (0.0, 0.0, 0.20), seg=20, m=M_WALK, parent=root)
    cyl("Pole_%d" % index, 0.115, 6.4, (0.0, 0.0, 3.4), seg=20, r2=0.095,
        m=M_POLE, parent=root)
    cyl("ArmBase_%d" % index, 0.13, 0.5, (-0.20, 0.0, 6.45),
        rot=(0.0, math.pi / 2.0, 0.0), seg=18, m=M_POLE, parent=root)
    cyl("Arm_%d" % index, 0.095, 6.4, (-3.4, 0.0, 6.5),
        rot=(0.0, math.pi / 2.0, 0.0), seg=18, r2=0.070, m=M_POLE, parent=root)
    # diagonal brace back to the pole
    p1, p2 = Vector((-0.10, 0.0, 4.9)), Vector((-2.9, 0.0, 6.45))
    d = p2 - p1
    cyl("Brace_%d" % index, 0.045, d.length, (p1 + p2) / 2.0,
        d.to_track_quat('Z', 'Y').to_euler(), seg=12, m=M_POLE, parent=root)
    # two vehicle heads hanging from the arm
    for j, ax in enumerate((-2.6, -5.3)):
        cyl("Hanger_%d_%d" % (index, j), 0.05, 0.55, (ax, 0.0, 6.2), seg=12,
            m=M_POLE, parent=root)
        signal_head("Head_%d_%d" % (index, j), root, (ax, 0.0, 5.20), lit)
    # pole-mounted head facing the same way
    signal_head("PoleHead_%d" % index, root, (-0.36, 0.0, 3.55), lit, backplate=False)
    # pedestrian head + push button facing across the local -Y sidewalk
    box("PedBody_%d" % index, (0.34, 0.30, 0.46), loc=(0.0, -0.32, 2.55),
        m=M_HOUSING, bev=0.02, parent=root)
    box("PedFace_%d" % index, (0.26, 0.03, 0.36), loc=(0.0, -0.48, 2.55),
        m=M_PEDRED, parent=root)
    box("PushBox_%d" % index, (0.14, 0.10, 0.22), loc=(0.0, -0.20, 1.15),
        m=M_POLE, bev=0.01, parent=root)
    cyl("PushBtn_%d" % index, 0.032, 0.04, (0.0, -0.26, 1.19),
        rot=(math.pi / 2.0, 0.0, 0.0), seg=14, m=M_RED, parent=root)
    # street name blade
    box("StreetSign_%d" % index, (1.70, 0.03, 0.30), loc=(-0.95, 0.0, 6.95),
        m=M_SIGN, bev=0.01, parent=root)
    # luminaire on two of the poles
    if index % 2 == 0:
        cyl("LampArm_%d" % index, 0.055, 2.2, (-1.1, 0.0, 7.5),
            rot=(0.0, math.pi / 2.0, 0.0), seg=12, m=M_POLE, parent=root)
        box("Luminaire_%d" % index, (0.85, 0.42, 0.14), loc=(-2.15, 0.0, 7.42),
            m=M_LUM, bev=0.03, parent=root)
    return root


corners = ((RW + 1.6, RW + 1.6, math.pi, 'GREEN'),
           (-(RW + 1.6), RW + 1.6, -math.pi / 2.0, 'RED'),
           (-(RW + 1.6), -(RW + 1.6), 0.0, 'GREEN'),
           (RW + 1.6, -(RW + 1.6), math.pi / 2.0, 'RED'))
for i, (cx, cy, rot, lit) in enumerate(corners):
    signal_assembly(i, (cx, cy), rot, lit)

# ----------------------------------------------------------------- bollards
bm_b = bmesh.new()
bm_r = bmesh.new()


def bollard(x, y):
    h = 0.95
    bcyl(bm_b, 0.13, 0.05, loc=(x, y, CURB + 0.025), seg=18)
    bcyl(bm_b, 0.095, h, loc=(x, y, CURB + h / 2.0), seg=18, r2=0.085)
    bsph(bm_b, 0.085, loc=(x, y, CURB + h), u=18, v=8)
    for dz in (0.72, 0.80):
        bcyl(bm_r, 0.089, 0.055, loc=(x, y, CURB + dz), seg=18)


for sx in (-1.0, 1.0):
    for sy in (-1.0, 1.0):
        for i in range(6):
            d = RW + 1.0 + i * 1.7
            bollard(sx * (RW + 0.9), sy * d)
            bollard(sx * d, sy * (RW + 0.9))
finish("Bollards", bm_b, M_BOLLARD, smooth=45.0)
finish("BollardBands", bm_r, M_REFLECT, smooth=45.0)

# ----------------------------------------------------------------- lighting
light('SUN', "Sun", (30.0, -34.0, 40.0), 3.6, (1.0, 0.95, 0.87),
      tgt=(0.0, 0.0, 2.0), angle=0.02)
light('AREA', "SkyFill", (-25.0, -20.0, 30.0), 9000.0, (0.60, 0.72, 1.0),
      size=40.0, tgt=(0.0, 0.0, 3.0))
light('AREA', "Bounce", (10.0, 18.0, 8.0), 3000.0, (1.0, 0.9, 0.8),
      size=25.0, tgt=(0.0, 0.0, 4.0))

# ----------------------------------------------------------------- camera
cam((26.0, -30.0, 17.0), (-0.5, 0.5, 2.2), lens=45.0)
