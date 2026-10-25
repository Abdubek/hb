"""
Laboratory workstation with cabinets and instruments.
Blender 4.5 LTS - scene construction only (no render, no file output).
"""

import bpy
import bmesh
from math import pi, radians, sin, cos, sqrt
from mathutils import Vector, Matrix

# ---------------------------------------------------------------- scene setup
bpy.ops.wm.read_factory_settings(use_empty=True)
scene = bpy.context.scene
scene.unit_settings.system = 'METRIC'

LAB = bpy.data.collections.new("Lab_Workstation")
scene.collection.children.link(LAB)

world = bpy.data.worlds.new("LabWorld")
world.use_nodes = True
_bg = world.node_tree.nodes["Background"]
_bg.inputs[0].default_value = (0.055, 0.06, 0.065, 1.0)
_bg.inputs[1].default_value = 0.7
scene.world = world


# ---------------------------------------------------------------- materials
def make_mat(name, base=(0.8, 0.8, 0.8), rough=0.5, metal=0.0,
             transmission=0.0, ior=1.45, emit=None, emit_str=0.0, alpha=1.0):
    m = bpy.data.materials.new(name)
    m.use_nodes = True
    b = m.node_tree.nodes["Principled BSDF"]

    def setv(key, val):
        if key in b.inputs:
            b.inputs[key].default_value = val

    setv("Base Color", (base[0], base[1], base[2], 1.0))
    setv("Roughness", rough)
    setv("Metallic", metal)
    setv("IOR", ior)
    setv("Transmission Weight", transmission)
    setv("Alpha", alpha)
    if emit is not None:
        setv("Emission Color", (emit[0], emit[1], emit[2], 1.0))
        setv("Emission Strength", emit_str)
    if transmission > 0.0 or alpha < 1.0:
        try:
            m.blend_method = 'BLEND'
        except Exception:
            pass
        if hasattr(m, "surface_render_method"):
            m.surface_render_method = 'BLENDED'
        m.use_backface_culling = False
    return m


M = {
    "floor":      make_mat("Floor_Vinyl", (0.30, 0.31, 0.33), 0.42),
    "wall":       make_mat("Wall_Paint", (0.74, 0.75, 0.73), 0.72),
    "cab":        make_mat("Cabinet_Laminate", (0.62, 0.66, 0.70), 0.38),
    "cab_dark":   make_mat("Cabinet_Carcass", (0.40, 0.43, 0.46), 0.50),
    "top":        make_mat("Worktop_Epoxy", (0.045, 0.048, 0.05), 0.28),
    "steel":      make_mat("Stainless", (0.72, 0.73, 0.75), 0.22, 1.0),
    "steel_br":   make_mat("Stainless_Brushed", (0.66, 0.67, 0.69), 0.38, 1.0),
    "chrome":     make_mat("Chrome", (0.86, 0.87, 0.89), 0.08, 1.0),
    "alu":        make_mat("Anodized_Alu", (0.55, 0.56, 0.58), 0.32, 0.9),
    "plastic_w":  make_mat("Plastic_White", (0.86, 0.87, 0.87), 0.36),
    "plastic_d":  make_mat("Plastic_Dark", (0.10, 0.105, 0.115), 0.42),
    "plastic_g":  make_mat("Plastic_Grey", (0.34, 0.35, 0.37), 0.44),
    "rubber":     make_mat("Rubber", (0.045, 0.045, 0.05), 0.72),
    "glass":      make_mat("Lab_Glass", (0.97, 0.98, 1.0), 0.03, 0.0, 1.0, 1.47),
    "glass_win":  make_mat("Sash_Glass", (0.86, 0.92, 0.94), 0.02, 0.0, 0.95, 1.5),
    "liq_blue":   make_mat("Liquid_Blue", (0.06, 0.30, 0.62), 0.05, 0.0, 1.0, 1.33),
    "liq_amber":  make_mat("Liquid_Amber", (0.62, 0.32, 0.05), 0.05, 0.0, 1.0, 1.35),
    "liq_green":  make_mat("Liquid_Green", (0.10, 0.45, 0.18), 0.05, 0.0, 1.0, 1.34),
    "liq_clear":  make_mat("Liquid_Clear", (0.9, 0.94, 0.95), 0.03, 0.0, 1.0, 1.33),
    "liq_red":    make_mat("Liquid_Red", (0.55, 0.06, 0.10), 0.05, 0.0, 1.0, 1.34),
    "label":      make_mat("Label_Paper", (0.90, 0.89, 0.85), 0.66),
    "label_y":    make_mat("Label_Hazard", (0.86, 0.72, 0.12), 0.60),
    "cap_blue":   make_mat("Cap_Blue", (0.09, 0.20, 0.52), 0.42),
    "cap_red":    make_mat("Cap_Red", (0.48, 0.08, 0.09), 0.42),
    "cap_white":  make_mat("Cap_White", (0.82, 0.83, 0.83), 0.42),
    "screen":     make_mat("Screen_LCD", (0.02, 0.03, 0.05), 0.16,
                           emit=(0.42, 0.60, 0.80), emit_str=2.4),
    "readout":    make_mat("Readout", (0.02, 0.04, 0.03), 0.20,
                           emit=(0.25, 0.85, 0.45), emit_str=3.0),
    "lamp":       make_mat("Hood_Lamp", (0.95, 0.96, 0.98), 0.30,
                           emit=(1.0, 0.97, 0.92), emit_str=9.0),
    "led_red":    make_mat("LED_Red", (0.3, 0.02, 0.02), 0.25,
                           emit=(1.0, 0.10, 0.05), emit_str=4.0),
    "seat":       make_mat("Stool_Seat", (0.10, 0.12, 0.16), 0.58),
}


# ---------------------------------------------------------------- helpers
def _finish(name, bm, mat, loc, rot, parent, smooth_mode=None):
    me = bpy.data.meshes.new(name)
    bm.to_mesh(me)
    bm.free()
    ob = bpy.data.objects.new(name, me)
    LAB.objects.link(ob)
    ob.location = loc
    ob.rotation_euler = rot
    if mat is not None:
        me.materials.append(mat)
    if smooth_mode == 'Z':
        for p in me.polygons:
            p.use_smooth = abs(p.normal.z) < 0.85
    elif smooth_mode == 'ALL':
        for p in me.polygons:
            p.use_smooth = True
    if parent is not None:
        ob.parent = parent
    return ob


def group(name, loc=(0, 0, 0), rot=(0, 0, 0), parent=None):
    e = bpy.data.objects.new(name, None)
    e.empty_display_type = 'PLAIN_AXES'
    e.empty_display_size = 0.08
    LAB.objects.link(e)
    e.location = loc
    e.rotation_euler = rot
    if parent is not None:
        e.parent = parent
    return e


def box(name, size, loc=(0, 0, 0), mat=None, bevel=0.0, rot=(0, 0, 0), parent=None):
    bm = bmesh.new()
    bmesh.ops.create_cube(bm, size=1.0)
    bmesh.ops.scale(bm, vec=Vector(size), verts=bm.verts)
    if bevel > 0.0:
        geom = list(bm.verts) + list(bm.edges) + list(bm.faces)
        bmesh.ops.bevel(bm, geom=geom, offset=bevel, segments=2, profile=0.5,
                        affect='EDGES', clamp_overlap=True)
    return _finish(name, bm, mat, loc, rot, parent)


def cyl(name, r, h, loc=(0, 0, 0), mat=None, seg=32, rot=(0, 0, 0),
        parent=None, r2=None, caps=True):
    bm = bmesh.new()
    bmesh.ops.create_cone(bm, cap_ends=caps, cap_tris=False, segments=seg,
                          radius1=r, radius2=(r if r2 is None else r2), depth=h)
    return _finish(name, bm, mat, loc, rot, parent, 'Z')


def ball(name, r, loc=(0, 0, 0), mat=None, subd=3, parent=None, scale=(1, 1, 1)):
    bm = bmesh.new()
    bmesh.ops.create_icosphere(bm, subdivisions=subd, radius=r)
    if scale != (1, 1, 1):
        bmesh.ops.scale(bm, vec=Vector(scale), verts=bm.verts)
    return _finish(name, bm, mat, loc, (0, 0, 0), parent, 'ALL')


def lathe(name, profile, loc=(0, 0, 0), mat=None, seg=48, rot=(0, 0, 0), parent=None):
    """Surface of revolution around Z from a list of (radius, height) points."""
    bm = bmesh.new()
    vs = [bm.verts.new((p[0], 0.0, p[1])) for p in profile]
    es = [bm.edges.new((vs[i], vs[i + 1])) for i in range(len(vs) - 1)]
    bmesh.ops.spin(bm, geom=vs + es, cent=(0, 0, 0), axis=(0, 0, 1),
                   dvec=(0, 0, 0), angle=2.0 * pi, steps=seg, use_merge=True)
    bmesh.ops.remove_doubles(bm, verts=bm.verts, dist=1e-5)
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    return _finish(name, bm, mat, loc, rot, parent, 'Z')


def tube(name, pts, r, mat=None, seg=12, joints=True, loc=(0, 0, 0), parent=None):
    """Sweep a round tube through a polyline of local-space points."""
    bm = bmesh.new()
    up = Vector((0, 0, 1))
    for i in range(len(pts) - 1):
        a, b = Vector(pts[i]), Vector(pts[i + 1])
        d = b - a
        L = d.length
        if L < 1e-6:
            continue
        rotm = up.rotation_difference(d.normalized()).to_matrix().to_4x4()
        mx = Matrix.Translation((a + b) * 0.5) @ rotm
        bmesh.ops.create_cone(bm, cap_ends=True, cap_tris=False, segments=seg,
                              radius1=r, radius2=r, depth=L, matrix=mx)
    if joints:
        for p in pts:
            bmesh.ops.create_icosphere(bm, subdivisions=2, radius=r * 0.999,
                                       matrix=Matrix.Translation(Vector(p)))
    return _finish(name, bm, mat, loc, (0, 0, 0), parent, 'ALL')


def ring_pts(radius, z=0.0, cx=0.0, cy=0.0, n=28):
    pts = []
    for i in range(n + 1):
        t = 2.0 * pi * i / n
        pts.append((cx + radius * cos(t), cy + radius * sin(t), z))
    return pts


def look_at(ob, target):
    d = Vector(target) - ob.location
    ob.rotation_euler = d.to_track_quat('-Z', 'Y').to_euler()


# ---------------------------------------------------------------- room shell
box("Floor", (8.4, 7.4, 0.06), (0.0, -2.6, -0.03), M["floor"])
box("Wall_Back", (8.4, 0.10, 3.0), (0.0, 0.47, 1.5), M["wall"])
box("Wall_Left", (0.10, 7.4, 3.0), (-3.15, -2.6, 1.5), M["wall"])
box("Skirting", (8.4, 0.02, 0.09), (0.0, 0.41, 0.045), M["plastic_g"])

# ---------------------------------------------------------------- base cabinets
BENCH_TOP = 0.90
bench = group("Bench_Run")

box("Cabinet_Carcass", (4.80, 0.715, 0.760), (0.0, 0.0175, 0.480),
    M["cab_dark"], parent=bench)
box("Toe_Kick", (4.80, 0.655, 0.100), (0.0, 0.0475, 0.050),
    M["plastic_d"], parent=bench)

# vertical reveals between the five modules
for i in range(4):
    x = -2.40 + 0.96 * (i + 1)
    box("Cab_Divider_%d" % i, (0.014, 0.02, 0.755), (x, -0.348, 0.4825),
        M["cab_dark"], parent=bench)


def bar_handle(name, cx, cz, length, vertical=False, parent=None):
    rot = (0, 0, 0) if vertical else (0, pi * 0.5, 0)
    cyl(name, 0.008, length, (cx, -0.392, cz), M["chrome"], 20, rot, parent)
    off = length * 0.5 - 0.022
    for s in (-1, 1):
        if vertical:
            p = (cx, -0.3725, cz + s * off)
        else:
            p = (cx + s * off, -0.3725, cz)
        cyl(name + "_Post_%d" % s, 0.006, 0.030, p, M["chrome"], 12,
            (pi * 0.5, 0, 0), parent)


# module 0 : drawer bank
DRW_X = -1.92
for i in range(3):
    z = 0.229 + i * 0.246
    box("Drawer_Front_%d" % i, (0.905, 0.020, 0.238), (DRW_X, -0.350, z),
        M["cab"], bevel=0.004, parent=bench)
    bar_handle("Drawer_Handle_%d" % i, DRW_X, z, 0.30, False, bench)

# modules 1-4 : hinged double doors
for mi, cx in enumerate((-0.96, 0.0, 0.96, 1.92)):
    for s in (-1, 1):
        dx = cx + s * 0.2425
        box("Door_%d_%d" % (mi, s), (0.465, 0.020, 0.720), (dx, -0.350, 0.480),
            M["cab"], bevel=0.004, parent=bench)
        bar_handle("Door_Handle_%d_%d" % (mi, s), cx + s * 0.048, 0.480,
                   0.150, True, bench)

# ---------------------------------------------------------------- worktop + sink
SINK_X0, SINK_X1 = 1.35, 1.90
SINK_Y0, SINK_Y1 = -0.24, 0.24
SINK_CX = (SINK_X0 + SINK_X1) * 0.5
SINK_D = 0.28

box("Worktop_Main", (3.80, 0.84, 0.040), (-0.55, 0.0, 0.880), M["top"],
    bevel=0.004, parent=bench)
box("Worktop_Right", (0.55, 0.84, 0.040), (2.175, 0.0, 0.880), M["top"],
    bevel=0.004, parent=bench)
box("Worktop_SinkBack", (0.55, 0.18, 0.040), (SINK_CX, 0.33, 0.880), M["top"],
    parent=bench)
box("Worktop_SinkFront", (0.55, 0.18, 0.040), (SINK_CX, -0.33, 0.880), M["top"],
    parent=bench)
box("Backsplash", (4.90, 0.024, 0.140), (0.0, 0.408, 0.970), M["top"], parent=bench)

sink = group("Sink", (SINK_CX, 0.0, 0.0), parent=bench)
box("Sink_Bottom", (0.526, 0.456, 0.012), (0.0, 0.0, BENCH_TOP - SINK_D + 0.006),
    M["steel"], parent=sink)
for s in (-1, 1):
    box("Sink_WallX_%d" % s, (0.012, 0.480, SINK_D),
        (s * 0.269, 0.0, BENCH_TOP - SINK_D * 0.5), M["steel"], parent=sink)
    box("Sink_WallY_%d" % s, (0.550, 0.012, SINK_D),
        (0.0, s * 0.234, BENCH_TOP - SINK_D * 0.5), M["steel"], parent=sink)
for s in (-1, 1):
    box("Sink_RimX_%d" % s, (0.030, 0.520, 0.008), (s * 0.290, 0.0, BENCH_TOP + 0.002),
        M["steel"], parent=sink)
    box("Sink_RimY_%d" % s, (0.610, 0.030, 0.008), (0.0, s * 0.255, BENCH_TOP + 0.002),
        M["steel"], parent=sink)
cyl("Sink_Drain", 0.032, 0.010, (0.0, 0.0, BENCH_TOP - SINK_D + 0.014),
    M["steel_br"], 24, parent=sink)
cyl("Sink_Drain_Hole", 0.020, 0.006, (0.0, 0.0, BENCH_TOP - SINK_D + 0.018),
    M["plastic_d"], 20, parent=sink)

# gooseneck faucet
faucet = group("Faucet", (SINK_CX, 0.32, BENCH_TOP), parent=bench)
cyl("Faucet_Base", 0.032, 0.016, (0, 0, 0.008), M["chrome"], 24, parent=faucet)
cyl("Faucet_Column", 0.020, 0.150, (0, 0, 0.083), M["chrome"], 24, parent=faucet)
arc = []
for i in range(13):
    t = pi * i / 12.0
    arc.append((0.0, 0.15 * cos(t) - 0.0 + 0.0, 0.158 + 0.15 * sin(t)))
# shift the arc so it starts on the column axis and sweeps forward
arc = [(0.0, y - 0.15, z) for (x, y, z) in arc]
arc.append((0.0, -0.30, 0.120))
tube("Faucet_Neck", arc, 0.019, M["chrome"], 20, True, (0, 0, 0), faucet)
cyl("Faucet_Aerator", 0.023, 0.026, (0.0, -0.30, 0.112), M["chrome"], 20,
    parent=faucet)
for s in (-1, 1):
    cyl("Faucet_Handle_%d" % s, 0.014, 0.070, (s * 0.085, 0.0, 0.030),
        M["chrome"], 16, (0, radians(s * 55), 0), faucet)
# eyewash unit at the sink edge
cyl("Eyewash_Post", 0.014, 0.120, (-0.30, 0.05, 0.060), M["chrome"], 16, parent=faucet)
for s in (-1, 1):
    cyl("Eyewash_Cup_%d" % s, 0.030, 0.024, (-0.30 + s * 0.045, 0.05, 0.128),
        M["led_red"], 20, r2=0.020, parent=faucet)

# ---------------------------------------------------------------- fume hood
hood = group("Fume_Hood", (-1.80, 0.0, 0.0), parent=bench)
HW, HD = 1.20, 0.82
for s in (-1, 1):
    box("Hood_Side_%d" % s, (0.030, HD, 1.200), (s * 0.585, 0.010, 1.500),
        M["cab"], parent=hood)
box("Hood_Back", (1.140, 0.030, 1.200), (0.0, 0.395, 1.500), M["plastic_w"], parent=hood)
box("Hood_Top", (HW, HD, 0.045), (0.0, 0.010, 2.078), M["cab"], parent=hood)
box("Hood_Liner", (1.140, 0.790, 0.012), (0.0, 0.010, 0.906), M["plastic_w"], parent=hood)
box("Hood_Fascia", (1.140, 0.032, 0.280), (0.0, -0.385, 1.960), M["cab"], parent=hood)
box("Hood_Sash_Glass", (1.100, 0.014, 0.600), (0.0, -0.386, 1.500),
    M["glass_win"], parent=hood)
box("Hood_Sash_Rail", (1.130, 0.040, 0.050), (0.0, -0.386, 1.185), M["alu"], parent=hood)
box("Hood_Sash_RailTop", (1.130, 0.036, 0.036), (0.0, -0.386, 1.808), M["alu"], parent=hood)
cyl("Hood_Sash_Grip", 0.010, 0.400, (0.0, -0.412, 1.170), M["chrome"], 16,
    (0, pi * 0.5, 0), hood)
box("Hood_Lamp", (1.000, 0.070, 0.020), (0.0, -0.150, 2.046), M["lamp"], parent=hood)
# hood control panel
box("Hood_Panel", (0.230, 0.026, 0.150), (0.470, -0.400, 1.960), M["plastic_d"], parent=hood)
box("Hood_Panel_Screen", (0.130, 0.008, 0.055), (0.470, -0.416, 1.985),
    M["readout"], parent=hood)
for i in range(3):
    cyl("Hood_Btn_%d" % i, 0.012, 0.010, (0.420 + i * 0.050, -0.416, 1.920),
        M["plastic_w"], 16, (pi * 0.5, 0, 0), hood)
# service fittings on the hood back wall
for i, (dx, cm) in enumerate(((-0.42, M["cap_blue"]), (-0.30, M["cap_red"]))):
    cyl("Hood_Tap_Body_%d" % i, 0.016, 0.070, (dx, 0.360, 1.060), M["chrome"], 16,
        (pi * 0.5, 0, 0), hood)
    cyl("Hood_Tap_Nozzle_%d" % i, 0.008, 0.090, (dx, 0.318, 1.020), M["chrome"], 12,
        parent=hood)
    cyl("Hood_Tap_Handle_%d" % i, 0.024, 0.014, (dx, 0.360, 1.105), cm, 16, parent=hood)

# ring stand with round-bottom flask inside the hood
stand = group("Ring_Stand", (-1.90, 0.16, 0.912), parent=bench)
box("Stand_Base", (0.190, 0.260, 0.020), (0.0, 0.0, 0.010), M["plastic_d"],
    bevel=0.004, parent=stand)
cyl("Stand_Rod", 0.008, 0.560, (0.0, 0.085, 0.300), M["chrome"], 16, parent=stand)
box("Stand_Clamp", (0.026, 0.070, 0.016), (0.0, 0.048, 0.300), M["alu"], parent=stand)
tube("Stand_Ring", ring_pts(0.055, 0.300, 0.0, -0.010), 0.005, M["chrome"], 10,
     False, (0, 0, 0), stand)
ball("RBF_Body", 0.056, (0.0, -0.010, 0.318), M["glass"], 3, stand)
ball("RBF_Liquid", 0.049, (0.0, -0.010, 0.310), M["liq_amber"], 3, stand,
     scale=(1.0, 1.0, 0.82))
cyl("RBF_Neck", 0.016, 0.090, (0.0, -0.010, 0.412), M["glass"], 24, parent=stand)
cyl("RBF_Rim", 0.019, 0.010, (0.0, -0.010, 0.455), M["glass"], 24, parent=stand)


# ---------------------------------------------------------------- glassware kit
def beaker(name, loc, r=0.045, h=0.090, fill=0.055, liq=None, parent=None):
    prof = [(0.0, 0.002), (r - 0.006, 0.002), (r, 0.010), (r, h), (r + 0.002, h + 0.003)]
    lathe(name, prof, loc, M["glass"], 40, parent=parent)
    cyl(name + "_Grad", r * 1.002, 0.030, (loc[0], loc[1], loc[2] + h * 0.55),
        M["label"], 40, parent=parent)
    if liq is not None and fill > 0.0:
        lathe(name + "_Liquid",
              [(0.0, 0.004), (r - 0.003, 0.004), (r - 0.003, fill), (0.0, fill)],
              loc, liq, 40, parent=parent)


def flask(name, loc, parent=None, liq=None, fill=0.045):
    prof = [(0.0, 0.002), (0.048, 0.004), (0.052, 0.014), (0.0135, 0.105),
            (0.0135, 0.140), (0.017, 0.144)]
    lathe(name, prof, loc, M["glass"], 40, parent=parent)
    if liq is not None:
        rr = 0.050 - (0.050 - 0.013) * (fill / 0.105)
        lathe(name + "_Liquid",
              [(0.0, 0.006), (0.046, 0.008), (rr, fill), (0.0, fill)],
              loc, liq, 40, parent=parent)


def reagent_bottle(name, loc, cap, liq=None, fill=0.070, hazard=False, parent=None):
    prof = [(0.0, 0.0), (0.031, 0.0), (0.034, 0.005), (0.034, 0.098),
            (0.028, 0.112), (0.0145, 0.122), (0.0145, 0.140)]
    lathe(name, prof, loc, M["glass"], 36, parent=parent)
    cyl(name + "_Cap", 0.018, 0.026, (loc[0], loc[1], loc[2] + 0.150), cap, 24,
        parent=parent)
    cyl(name + "_Label", 0.0345, 0.052, (loc[0], loc[1], loc[2] + 0.055),
        M["label_y"] if hazard else M["label"], 36, parent=parent)
    if liq is not None:
        lathe(name + "_Liquid",
              [(0.0, 0.004), (0.031, 0.004), (0.031, fill), (0.0, fill)],
              loc, liq, 36, parent=parent)


def test_tube(name, loc, liq=None, fill=0.040, parent=None):
    r = 0.0075
    prof = []
    for i in range(5):
        a = -pi * 0.5 + i * (pi * 0.5) / 4.0
        prof.append((r * cos(a), r + r * sin(a)))
    prof += [(r, 0.070), (r + 0.001, 0.073)]
    lathe(name, prof, loc, M["glass"], 24, parent=parent)
    if liq is not None:
        lp = [(p[0] * 0.86, p[1]) for p in prof[:5]] + [(r * 0.86, fill), (0.0, fill)]
        lathe(name + "_Liquid", lp, loc, liq, 24, parent=parent)


# glassware inside the hood
beaker("Hood_Beaker", (-1.42, 0.10, 0.918), 0.048, 0.095, 0.050,
       M["liq_clear"], bench)
reagent_bottle("Hood_Bottle", (-2.18, 0.28, 0.918), M["cap_red"], M["liq_amber"],
               0.062, True, bench)

# ---------------------------------------------------------------- microscope
mic = group("Microscope", (-0.95, 0.06, BENCH_TOP), (0, 0, radians(18)), bench)
box("Mic_Base", (0.190, 0.240, 0.032), (0, 0, 0.016), M["plastic_w"], 0.008, parent=mic)
box("Mic_Base_Foot", (0.170, 0.220, 0.006), (0, 0, 0.002), M["rubber"], parent=mic)
cyl("Mic_Illum", 0.030, 0.020, (0, -0.020, 0.042), M["alu"], 24, parent=mic)
cyl("Mic_Illum_Lens", 0.020, 0.006, (0, -0.020, 0.055), M["lamp"], 20, parent=mic)
box("Mic_Arm_Post", (0.056, 0.060, 0.230), (0, 0.086, 0.145), M["plastic_w"],
    0.008, parent=mic)
box("Mic_Arm_Neck", (0.050, 0.110, 0.062), (0, 0.032, 0.234), M["plastic_w"],
    0.008, parent=mic)
cyl("Mic_Focus_Coarse", 0.032, 0.022, (0.052, 0.086, 0.100), M["plastic_g"], 24,
    (0, pi * 0.5, 0), mic)
cyl("Mic_Focus_Fine", 0.020, 0.016, (-0.048, 0.086, 0.100), M["plastic_g"], 20,
    (0, pi * 0.5, 0), mic)
box("Mic_Stage", (0.140, 0.130, 0.012), (0, -0.012, 0.108), M["plastic_d"], parent=mic)
box("Mic_Stage_Clip", (0.050, 0.014, 0.005), (0.026, -0.048, 0.116), M["chrome"], parent=mic)
box("Mic_Slide", (0.026, 0.062, 0.002), (-0.006, -0.014, 0.115), M["glass"], parent=mic)
cyl("Mic_Stage_Knob", 0.016, 0.014, (0.078, -0.030, 0.100), M["plastic_g"], 18,
    (0, pi * 0.5, 0), mic)
cyl("Mic_Turret", 0.038, 0.026, (0, -0.020, 0.196), M["plastic_d"], 28, parent=mic)
for i in range(4):
    a = radians(-55 + i * 36)
    ox, oy = 0.024 * sin(a), -0.020 - 0.024 * cos(a)
    L = 0.042 + 0.008 * (i % 2)
    cyl("Mic_Objective_%d" % i, 0.009, L, (ox, oy, 0.182 - L * 0.5),
        M["chrome"], 16, r2=0.006, parent=mic)
box("Mic_Head", (0.070, 0.100, 0.056), (0, -0.010, 0.235), M["plastic_w"],
    0.008, parent=mic)
eye = group("Mic_Eyepiece_Grp", (0, -0.040, 0.252), (radians(-38), 0, 0), mic)
cyl("Mic_Eye_Tube", 0.020, 0.090, (0, 0, 0.045), M["plastic_d"], 24, parent=eye)
cyl("Mic_Eye_Lens", 0.024, 0.020, (0, 0, 0.098), M["chrome"], 24, parent=eye)

# ---------------------------------------------------------------- centrifuge
cen = group("Centrifuge", (-0.50, 0.08, BENCH_TOP), (0, 0, radians(-8)), bench)
lathe("Cen_Body", [(0.0, 0.0), (0.165, 0.0), (0.170, 0.012), (0.170, 0.150),
                   (0.164, 0.168), (0.150, 0.176), (0.0, 0.176)],
      (0, 0, 0), M["plastic_w"], 48, parent=cen)
lathe("Cen_Lid", [(0.0, 0.176), (0.140, 0.176), (0.152, 0.182), (0.152, 0.196),
                  (0.130, 0.212), (0.0, 0.216)],
      (0, 0, 0), M["plastic_g"], 48, parent=cen)
cyl("Cen_Lid_Window", 0.070, 0.006, (0, 0, 0.216), M["glass_win"], 36, parent=cen)
box("Cen_Latch", (0.070, 0.030, 0.024), (0.0, -0.156, 0.186), M["plastic_g"],
    0.004, parent=cen)
panel = group("Cen_Panel_Grp", (0.0, -0.140, 0.115), (radians(58), 0, 0), cen)
box("Cen_Panel", (0.200, 0.100, 0.010), (0, 0, 0), M["plastic_d"], 0.003, parent=panel)
box("Cen_Display", (0.100, 0.038, 0.004), (0.0, 0.022, 0.008), M["readout"], parent=panel)
for i in range(4):
    cyl("Cen_Btn_%d" % i, 0.011, 0.008, (-0.066 + i * 0.044, -0.026, 0.008),
        M["plastic_g"] if i else M["led_red"], 16, parent=panel)
cyl("Cen_Dial", 0.020, 0.012, (0.072, 0.020, 0.008), M["plastic_g"], 20, parent=panel)
for s in (-1, 1):
    for t in (-1, 1):
        cyl("Cen_Foot_%d_%d" % (s, t), 0.020, 0.008,
            (s * 0.105, t * 0.105, 0.004), M["rubber"], 16, parent=cen)

# ---------------------------------------------------------------- analytical balance
bal = group("Balance", (-0.02, 0.10, BENCH_TOP), (0, 0, radians(4)), bench)
box("Bal_Base", (0.230, 0.310, 0.055), (0, 0.0, 0.028), M["plastic_w"], 0.006, parent=bal)
box("Bal_Base_Front", (0.230, 0.090, 0.030), (0, -0.150, 0.048), M["plastic_g"],
    0.005, parent=bal)
box("Bal_Display", (0.120, 0.052, 0.004), (0, -0.152, 0.064), M["readout"],
    rot=(radians(-14), 0, 0), parent=bal)
for i in range(3):
    cyl("Bal_Key_%d" % i, 0.010, 0.006, (-0.078 + i * 0.078, -0.118, 0.064),
        M["plastic_g"], 16, parent=bal)
cyl("Bal_Pan", 0.046, 0.004, (0, 0.030, 0.060), M["steel_br"], 32, parent=bal)
cyl("Bal_Pan_Post", 0.008, 0.012, (0, 0.030, 0.052), M["chrome"], 12, parent=bal)
# draft shield
sh = group("Bal_Shield", (0, 0.048, 0.055), parent=bal)
for s in (-1, 1):
    box("Bal_Shield_Side_%d" % s, (0.006, 0.190, 0.170), (s * 0.100, 0, 0.085),
        M["glass"], parent=sh)
box("Bal_Shield_Back", (0.200, 0.006, 0.170), (0, 0.095, 0.085), M["glass"], parent=sh)
box("Bal_Shield_Front", (0.200, 0.006, 0.170), (0, -0.095, 0.085), M["glass"], parent=sh)
box("Bal_Shield_Top", (0.206, 0.196, 0.006), (0, 0, 0.173), M["glass"], parent=sh)
for s in (-1, 1):
    box("Bal_Shield_PostF_%d" % s, (0.010, 0.010, 0.176), (s * 0.100, -0.095, 0.088),
        M["alu"], parent=sh)
    box("Bal_Shield_PostB_%d" % s, (0.010, 0.010, 0.176), (s * 0.100, 0.095, 0.088),
        M["alu"], parent=sh)
cyl("Bal_Shield_Grip", 0.008, 0.050, (0.100, -0.055, 0.150), M["plastic_d"], 14,
    (pi * 0.5, 0, 0), sh)
cyl("Bal_Weight", 0.014, 0.026, (0, 0.030, 0.077), M["chrome"], 20, parent=bal)

# ---------------------------------------------------------------- hot plate stirrer
hp = group("Hotplate_Stirrer", (1.02, 0.10, BENCH_TOP), (0, 0, radians(-6)), bench)
box("HP_Body", (0.190, 0.220, 0.058), (0, 0, 0.029), M["steel_br"], 0.006, parent=hp)
box("HP_Front", (0.190, 0.020, 0.040), (0, -0.110, 0.030), M["plastic_d"], parent=hp)
cyl("HP_Plate", 0.074, 0.010, (0, 0.020, 0.062), M["plastic_w"], 36, parent=hp)
cyl("HP_Plate_Ring", 0.078, 0.005, (0, 0.020, 0.058), M["alu"], 36, parent=hp)
for i, cm in enumerate((M["plastic_g"], M["plastic_g"])):
    cyl("HP_Knob_%d" % i, 0.021, 0.014, (-0.052 + i * 0.104, -0.112, 0.038), cm, 24,
        (pi * 0.5, 0, 0), hp)
    box("HP_Knob_Mark_%d" % i, (0.004, 0.006, 0.016), (-0.052 + i * 0.104, -0.121, 0.046),
        M["plastic_w"], parent=hp)
box("HP_LED", (0.020, 0.006, 0.008), (0.0, -0.121, 0.050), M["led_red"], parent=hp)
beaker("HP_Beaker", (0.0, 0.020, 0.068), 0.050, 0.100, 0.062, M["liq_blue"], hp)
cyl("HP_Stir_Bar", 0.005, 0.026, (0.0, 0.020, 0.076), M["plastic_w"], 12,
    (0, pi * 0.5, 0), hp)

# ---------------------------------------------------------------- computer
comp = group("Computer", (0.50, 0.0, BENCH_TOP), parent=bench)
box("Mon_Base", (0.250, 0.170, 0.016), (0, 0.230, 0.008), M["plastic_d"], 0.004, parent=comp)
box("Mon_Post", (0.052, 0.030, 0.210), (0, 0.240, 0.118), M["plastic_d"], 0.004, parent=comp)
head = group("Mon_Head", (0, 0.238, 0.370), (radians(-9), 0, 0), comp)
box("Mon_Panel", (0.540, 0.022, 0.330), (0, 0, 0), M["plastic_d"], 0.004, parent=head)
box("Mon_Screen", (0.508, 0.006, 0.296), (0, -0.015, 0.006), M["screen"], parent=head)
box("Keyboard", (0.440, 0.150, 0.018), (0, -0.230, 0.009), M["plastic_d"],
    0.004, rot=(radians(-2.5), 0, 0), parent=comp)
box("Keyboard_Keys", (0.404, 0.116, 0.006), (0, -0.232, 0.019), M["plastic_g"],
    rot=(radians(-2.5), 0, 0), parent=comp)
ball("Mouse", 0.042, (0.310, -0.245, 0.014), M["plastic_d"], 3, comp,
     scale=(0.72, 1.30, 0.42))

# ---------------------------------------------------------------- tube rack + glassware
rack = group("Tube_Rack", (2.18, -0.14, BENCH_TOP), (0, 0, radians(12)), bench)
box("Rack_Base", (0.230, 0.075, 0.014), (0, 0, 0.007), M["plastic_g"], 0.003, parent=rack)
for s in (-1, 1):
    box("Rack_End_%d" % s, (0.014, 0.075, 0.070), (s * 0.108, 0, 0.042),
        M["plastic_g"], 0.003, parent=rack)
for s in (-1, 1):
    box("Rack_Rail_%d" % s, (0.230, 0.010, 0.012), (0, s * 0.014, 0.070),
        M["plastic_g"], parent=rack)
liqs = [M["liq_red"], M["liq_clear"], M["liq_amber"], None, M["liq_green"], M["liq_red"]]
for i in range(6):
    x = -0.085 + i * 0.034
    test_tube("Tube_%d" % i, (x, 0.0, 0.012), liqs[i], 0.030 + 0.006 * (i % 3), rack)

flask("Erlenmeyer_A", (2.14, 0.20, BENCH_TOP), bench, M["liq_green"], 0.055)
beaker("Beaker_Small", (1.90, 0.30, BENCH_TOP), 0.036, 0.070, 0.038,
       M["liq_clear"], bench)
lathe("Graduated_Cylinder",
      [(0.0, 0.0), (0.036, 0.0), (0.036, 0.012), (0.019, 0.030), (0.019, 0.250),
       (0.022, 0.256)],
      (2.34, 0.24, BENCH_TOP), M["glass"], 36, parent=bench)
lathe("Graduated_Liquid",
      [(0.0, 0.032), (0.0165, 0.032), (0.0165, 0.170), (0.0, 0.170)],
      (2.34, 0.24, BENCH_TOP), M["liq_blue"], 36, parent=bench)

# pipette stand
pst = group("Pipette_Stand", (-0.74, 0.30, BENCH_TOP), parent=bench)
box("Pip_Base", (0.120, 0.090, 0.014), (0, 0, 0.007), M["plastic_d"], 0.003, parent=pst)
cyl("Pip_Post", 0.009, 0.230, (0, 0.020, 0.125), M["chrome"], 16, parent=pst)
box("Pip_Arm", (0.110, 0.016, 0.012), (0, 0.010, 0.232), M["plastic_d"], parent=pst)
for i, cm in enumerate((M["cap_blue"], M["cap_red"], M["cap_white"])):
    x = -0.040 + i * 0.040
    cyl("Pipette_Body_%d" % i, 0.011, 0.130, (x, 0.002, 0.165), cm, 18, parent=pst)
    cyl("Pipette_Tip_%d" % i, 0.005, 0.070, (x, 0.002, 0.070), M["plastic_w"], 12,
        r2=0.002, parent=pst)
    cyl("Pipette_Plunger_%d" % i, 0.007, 0.024, (x, 0.002, 0.240), M["plastic_g"],
        12, parent=pst)

# glove box on the bench
box("Glove_Box", (0.130, 0.075, 0.130), (-1.12, 0.34, BENCH_TOP + 0.065),
    M["cap_blue"], 0.004, parent=bench)
box("Glove_Box_Slot", (0.080, 0.010, 0.040), (-1.12, 0.302, BENCH_TOP + 0.100),
    M["plastic_w"], parent=bench)

# ---------------------------------------------------------------- wall shelf
shelf = group("Wall_Shelf", (-0.48, 0.29, 1.50))
box("Shelf_Board", (1.350, 0.260, 0.026), (0, 0, 0), M["cab"], 0.004, parent=shelf)
for s in (-1, 1):
    box("Shelf_Bracket_%d" % s, (0.018, 0.170, 0.100), (s * 0.560, 0.040, -0.062),
        M["alu"], parent=shelf)
    box("Shelf_Bracket_Up_%d" % s, (0.018, 0.020, 0.150), (s * 0.560, 0.118, -0.088),
        M["alu"], parent=shelf)
bottle_specs = [(-0.52, M["cap_blue"], M["liq_clear"], 0.080, False),
                (-0.42, M["cap_white"], M["liq_blue"], 0.070, False),
                (-0.30, M["cap_red"], M["liq_amber"], 0.086, True),
                (-0.18, M["cap_white"], M["liq_green"], 0.062, False),
                (0.36, M["cap_blue"], M["liq_red"], 0.074, True),
                (0.48, M["cap_white"], M["liq_clear"], 0.090, False)]
for i, (x, cap, liq, fill, hz) in enumerate(bottle_specs):
    reagent_bottle("Shelf_Bottle_%d" % i, (x, -0.010, 0.013), cap, liq, fill, hz, shelf)
beaker("Shelf_Beaker", (0.16, -0.010, 0.013), 0.046, 0.092, 0.0, None, shelf)
flask("Shelf_Flask", (0.04, 0.000, 0.013), shelf, None, 0.0)

# ---------------------------------------------------------------- upper cabinet
up = group("Upper_Cabinet", (1.475, 0.26, 1.85))
for s in (-1, 1):
    box("Up_Side_%d" % s, (0.018, 0.320, 0.600), (s * 0.866, 0, 0), M["cab"], parent=up)
box("Up_Top", (1.750, 0.320, 0.020), (0, 0, 0.290), M["cab"], parent=up)
box("Up_Bottom", (1.750, 0.320, 0.020), (0, 0, -0.290), M["cab"], parent=up)
box("Up_Back", (1.714, 0.016, 0.600), (0, 0.152, 0), M["plastic_w"], parent=up)
box("Up_Shelf", (1.714, 0.300, 0.016), (0, 0, -0.010), M["cab"], parent=up)
for s in (-1, 1):
    box("Up_Door_%d" % s, (0.855, 0.018, 0.556), (s * 0.437, -0.152, 0),
        M["glass_win"], parent=up)
    box("Up_Door_FrameV_%d" % s, (0.022, 0.024, 0.556), (s * 0.855, -0.152, 0),
        M["alu"], parent=up)
    box("Up_Door_FrameH_%d" % s, (0.876, 0.024, 0.022), (s * 0.437, -0.152, s * 0.267),
        M["alu"], parent=up)
    box("Up_Door_FrameH2_%d" % s, (0.876, 0.024, 0.022), (s * 0.437, -0.152, -s * 0.267),
        M["alu"], parent=up)
    cyl("Up_Handle_%d" % s, 0.008, 0.170, (s * 0.030, -0.178, 0.0), M["chrome"], 16,
        parent=up)
# contents visible through the glass doors
for i in range(5):
    reagent_bottle("Up_Bottle_%d" % i, (-0.62 + i * 0.16, 0.02, 0.004),
                   M["cap_white"] if i % 2 else M["cap_blue"],
                   M["liq_clear"], 0.060 + 0.008 * i, i == 2, up)
for i in range(4):
    beaker("Up_Beaker_%d" % i, (0.30 + i * 0.13, 0.02, -0.280), 0.042, 0.084,
           0.0, None, up)

# ---------------------------------------------------------------- stool
stool = group("Lab_Stool", (0.30, -1.02, 0.0), (0, 0, radians(-24)))
lathe("Stool_Seat", [(0.0, 0.640), (0.150, 0.640), (0.172, 0.652), (0.172, 0.686),
                     (0.150, 0.700), (0.0, 0.700)],
      (0, 0, 0), M["seat"], 40, parent=stool)
cyl("Stool_Seat_Plate", 0.100, 0.014, (0, 0, 0.632), M["plastic_d"], 32, parent=stool)
cyl("Stool_Gas_Upper", 0.026, 0.300, (0, 0, 0.478), M["chrome"], 24, parent=stool)
cyl("Stool_Gas_Lower", 0.038, 0.240, (0, 0, 0.230), M["plastic_d"], 24, parent=stool)
cyl("Stool_Hub", 0.052, 0.060, (0, 0, 0.090), M["plastic_d"], 24, parent=stool)
cyl("Stool_Lever", 0.008, 0.140, (0.100, 0.0, 0.330), M["chrome"], 12,
    (0, pi * 0.5, 0), stool)
for i in range(5):
    a = 2.0 * pi * i / 5.0
    box("Stool_Leg_%d" % i, (0.240, 0.036, 0.026),
        (0.135 * cos(a), 0.135 * sin(a), 0.072), M["plastic_d"], 0.005,
        (0, radians(6), a), stool)
    ball("Stool_Caster_%d" % i, 0.030, (0.250 * cos(a), 0.250 * sin(a), 0.032),
         M["rubber"], 2, stool, scale=(1.0, 0.55, 1.0))
# foot ring
tube("Stool_Foot_Ring", ring_pts(0.190, 0.230), 0.010, M["chrome"], 10, False,
     (0, 0, 0), stool)
for i in range(3):
    a = 2.0 * pi * i / 3.0
    box("Stool_Ring_Arm_%d" % i, (0.160, 0.014, 0.010),
        (0.098 * cos(a), 0.098 * sin(a), 0.230), M["chrome"], rot=(0, 0, a), parent=stool)

# ---------------------------------------------------------------- waste bin
bin_g = group("Waste_Bin", (2.72, -0.62, 0.0), (0, 0, radians(14)))
lathe("Bin_Body", [(0.150, 0.0), (0.150, 0.012), (0.185, 0.430), (0.190, 0.445)],
      (0, 0, 0), M["plastic_g"], 40, parent=bin_g)
lathe("Bin_Lid", [(0.0, 0.470), (0.150, 0.462), (0.192, 0.448), (0.196, 0.442)],
      (0, 0, 0), M["cap_red"], 40, parent=bin_g)
cyl("Bin_Pedal", 0.030, 0.010, (0.150, -0.130, 0.020), M["plastic_d"], 20, parent=bin_g)
box("Bin_Label", (0.110, 0.006, 0.080), (0.0, -0.176, 0.300), M["label_y"], parent=bin_g)

# ---------------------------------------------------------------- lighting
def area_light(name, loc, size, sizey, energy, target=None, rot=(0, 0, 0)):
    d = bpy.data.lights.new(name, 'AREA')
    d.shape = 'RECTANGLE'
    d.size = size
    d.size_y = sizey
    d.energy = energy
    ob = bpy.data.objects.new(name, d)
    LAB.objects.link(ob)
    ob.location = loc
    ob.rotation_euler = rot
    if target is not None:
        look_at(ob, target)
    return ob


area_light("Ceiling_Fixture_L", (-1.20, -0.70, 2.85), 1.80, 0.60, 260.0)
area_light("Ceiling_Fixture_R", (1.30, -0.70, 2.85), 1.80, 0.60, 260.0)
area_light("Fill_Front", (2.60, -3.20, 2.10), 3.00, 2.00, 120.0,
           target=(0.10, 0.0, 1.10))
area_light("Rim_Left", (-2.90, -2.40, 2.30), 1.60, 1.60, 70.0,
           target=(-1.60, 0.10, 1.40))

# visible ceiling fixture housings
for i, x in enumerate((-1.20, 1.30)):
    box("Ceiling_Housing_%d" % i, (1.90, 0.70, 0.09), (x, -0.70, 2.925), M["plastic_w"])
    box("Ceiling_Diffuser_%d" % i, (1.80, 0.60, 0.02), (x, -0.70, 2.872), M["lamp"])

# ---------------------------------------------------------------- camera
cam_data = bpy.data.cameras.new("LabCam")
cam_data.lens = 35.0
cam_data.sensor_width = 36.0
cam_data.clip_start = 0.05
cam_data.clip_end = 200.0
cam = bpy.data.objects.new("LabCam", cam_data)
LAB.objects.link(cam)
cam.location = (2.95, -3.55, 1.98)
TARGET = Vector((0.15, -0.05, 1.15))
look_at(cam, TARGET)
cam_data.dof.use_dof = True
cam_data.dof.focus_distance = (TARGET - cam.location).length
cam_data.dof.aperture_fstop = 5.6
scene.camera = cam

scene.render.resolution_x = 1920
scene.render.resolution_y = 1080

bpy.context.view_layer.update()
