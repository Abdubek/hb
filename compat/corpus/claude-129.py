# claude-129 : Construction excavator - articulated boom, bucket, tracks, operator cab
# Blender 4.5 LTS - scene construction only (no render, no file output)

import bpy, bmesh, math
from mathutils import Vector, Matrix, Euler

TAU = math.tau
R = math.radians

# ----------------------------------------------------------------------------- setup
bpy.ops.wm.read_factory_settings(use_empty=True)

scene = bpy.context.scene

COLL = bpy.data.collections.new("Excavator")
scene.collection.children.link(COLL)


# ----------------------------------------------------------------------------- materials
def make_mat(name, color, rough=0.5, metal=0.0, transmission=0.0, ior=1.45):
    mat = bpy.data.materials.new(name)
    mat.use_nodes = True
    bsdf = mat.node_tree.nodes.get("Principled BSDF")
    if bsdf:
        i = bsdf.inputs
        i["Base Color"].default_value = (*color, 1.0)
        i["Roughness"].default_value = rough
        i["Metallic"].default_value = metal
        if "IOR" in i:
            i["IOR"].default_value = ior
        if transmission > 0.0:
            if "Transmission Weight" in i:
                i["Transmission Weight"].default_value = transmission
            i["Alpha"].default_value = 0.35
            for attr, val in (("blend_method", 'BLEND'),
                              ("surface_render_method", 'BLENDED')):
                if hasattr(mat, attr):
                    try:
                        setattr(mat, attr, val)
                    except (TypeError, ValueError):
                        pass
    return mat


M_YELLOW = make_mat("PaintYellow", (0.72, 0.44, 0.02), rough=0.38, metal=0.15)
M_DARK   = make_mat("SteelDark",   (0.055, 0.058, 0.062), rough=0.55, metal=0.85)
M_GREY   = make_mat("SteelGrey",   (0.16, 0.17, 0.18), rough=0.45, metal=0.9)
M_CHROME = make_mat("RodChrome",   (0.78, 0.79, 0.81), rough=0.12, metal=1.0)
M_RUBBER = make_mat("TrackRubber", (0.035, 0.035, 0.038), rough=0.82, metal=0.25)
M_GLASS  = make_mat("CabGlass",    (0.55, 0.66, 0.72), rough=0.04, metal=0.0,
                    transmission=1.0, ior=1.52)
M_BLACK  = make_mat("PlasticBlack", (0.02, 0.02, 0.02), rough=0.65)
M_ORANGE = make_mat("LampAmber",   (0.85, 0.32, 0.02), rough=0.25)
M_GROUND = make_mat("Ground",      (0.21, 0.17, 0.13), rough=0.95)


# ----------------------------------------------------------------------------- helpers
def finish(name, bm, mat=None, parent=None, world_space=False):
    """Turn a bmesh into a linked object, optionally parented."""
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    me = bpy.data.meshes.new(name)
    bm.to_mesh(me)
    bm.free()
    ob = bpy.data.objects.new(name, me)
    COLL.objects.link(ob)
    if mat:
        ob.data.materials.append(mat)
    if parent:
        ob.parent = parent
        if world_space:
            ob.matrix_parent_inverse = parent.matrix_world.inverted()
    return ob


def add_empty(name, loc=(0, 0, 0), rot=(0, 0, 0), parent=None):
    e = bpy.data.objects.new(name, None)
    e.empty_display_type = 'PLAIN_AXES'
    e.empty_display_size = 0.4
    e.location = loc
    e.rotation_euler = rot
    COLL.objects.link(e)
    if parent:
        e.parent = parent
    return e


def box(name, size, loc=(0, 0, 0), rot=(0, 0, 0), mat=None, parent=None, bevel=0.0, segs=2):
    bm = bmesh.new()
    M = (Matrix.Translation(loc)
         @ Euler(rot, 'XYZ').to_matrix().to_4x4()
         @ Matrix.Diagonal(Vector(size)).to_4x4())
    bmesh.ops.create_cube(bm, size=1.0, matrix=M)
    if bevel > 0.0:
        bmesh.ops.bevel(bm, geom=bm.edges[:] + bm.verts[:], offset=bevel, segments=segs,
                        profile=0.5, affect='EDGES', clamp_overlap=True)
    return finish(name, bm, mat, parent)


def cyl(name, r, h, loc=(0, 0, 0), rot=(0, 0, 0), mat=None, parent=None, seg=20, r2=None):
    bm = bmesh.new()
    M = Matrix.Translation(loc) @ Euler(rot, 'XYZ').to_matrix().to_4x4()
    bmesh.ops.create_cone(bm, cap_ends=True, cap_tris=False, segments=seg,
                          radius1=r, radius2=(r if r2 is None else r2), depth=h, matrix=M)
    return finish(name, bm, mat, parent)


def rod_between(name, p, q, r, mat, parent=None, seg=14, taper=None):
    """Cylinder spanning two world-space points."""
    p, q = Vector(p), Vector(q)
    d = q - p
    L = max(d.length, 1e-5)
    M = Matrix.Translation((p + q) * 0.5) @ d.to_track_quat('Z', 'Y').to_matrix().to_4x4()
    bm = bmesh.new()
    bmesh.ops.create_cone(bm, cap_ends=True, cap_tris=False, segments=seg,
                          radius1=r, radius2=(r if taper is None else taper),
                          depth=L, matrix=M)
    return finish(name, bm, mat, parent, world_space=True)


def pin_ball(name, p, r, mat, parent=None):
    bm = bmesh.new()
    bmesh.ops.create_icosphere(bm, subdivisions=2, radius=r,
                               matrix=Matrix.Translation(Vector(p)))
    return finish(name, bm, mat, parent, world_space=True)


def hydraulic(name, p, q, rb=0.115, rr=0.062, parent_a=None, parent_b=None):
    """Two-piece hydraulic ram: barrel anchored at p, rod reaching q."""
    p, q = Vector(p), Vector(q)
    d = q - p
    L = d.length
    n = d.normalized()
    rod_start = p + n * (L * 0.42)
    barrel_end = p + n * (L * 0.60)
    rod_between(name + "_Barrel", p, barrel_end, rb, M_GREY, parent_a)
    rod_between(name + "_Gland", barrel_end - n * 0.06, barrel_end + n * 0.05,
                rb * 1.18, M_DARK, parent_a)
    rod_between(name + "_Rod", rod_start, q, rr, M_CHROME, parent_b)
    pin_ball(name + "_PinA", p, rb * 1.15, M_DARK, parent_a)
    pin_ball(name + "_PinB", q, rr * 1.7, M_DARK, parent_b)


def wp(ob, v):
    """Local point of ob -> world."""
    return ob.matrix_world @ Vector(v)


def beam(name, secs, mat, parent=None, bevel=0.025):
    """Lofted box-section beam. secs = [(x, z, half_height, half_width), ...] in XZ plane."""
    bm = bmesh.new()
    rings = []
    n = len(secs)
    for i, (x, z, hh, hw) in enumerate(secs):
        if i == 0:
            d = Vector((secs[1][0] - x, secs[1][1] - z))
        elif i == n - 1:
            d = Vector((x - secs[i - 1][0], z - secs[i - 1][1]))
        else:
            d = Vector((secs[i + 1][0] - secs[i - 1][0], secs[i + 1][1] - secs[i - 1][1]))
        d.normalize()
        u = Vector((-d.y, d.x))
        ring = [bm.verts.new((x + u.x * hh, -hw, z + u.y * hh)),
                bm.verts.new((x + u.x * hh, +hw, z + u.y * hh)),
                bm.verts.new((x - u.x * hh, +hw, z - u.y * hh)),
                bm.verts.new((x - u.x * hh, -hw, z - u.y * hh))]
        rings.append(ring)
    for a, b in zip(rings[:-1], rings[1:]):
        for k in range(4):
            k2 = (k + 1) % 4
            bm.faces.new((a[k], a[k2], b[k2], b[k]))
    bm.faces.new(tuple(reversed(rings[0])))
    bm.faces.new(tuple(rings[-1]))
    if bevel > 0.0:
        bmesh.ops.bevel(bm, geom=bm.edges[:] + bm.verts[:], offset=bevel, segments=2,
                        profile=0.5, affect='EDGES', clamp_overlap=True)
    return finish(name, bm, mat, parent)


def poly_solid(name, pts, y0, y1, mat, parent=None, bevel=0.0):
    """Closed XZ polygon extruded along Y."""
    bm = bmesh.new()
    vs = [bm.verts.new((x, y0, z)) for x, z in pts]
    f = bm.faces.new(vs)
    res = bmesh.ops.extrude_face_region(bm, geom=[f])
    moved = [e for e in res["geom"] if isinstance(e, bmesh.types.BMVert)]
    bmesh.ops.translate(bm, verts=moved, vec=(0.0, y1 - y0, 0.0))
    if bevel > 0.0:
        bmesh.ops.bevel(bm, geom=bm.edges[:] + bm.verts[:], offset=bevel, segments=2,
                        profile=0.5, affect='EDGES', clamp_overlap=True)
    return finish(name, bm, mat, parent)


def offset_path(pts, t):
    """Offset a 2D polyline outward (right-hand side of travel) by t."""
    out = []
    n = len(pts)
    for i, p in enumerate(pts):
        if i == 0:
            d = Vector(pts[1]) - Vector(pts[0])
        elif i == n - 1:
            d = Vector(pts[-1]) - Vector(pts[-2])
        else:
            d = Vector(pts[i + 1]) - Vector(pts[i - 1])
        d.normalize()
        nrm = Vector((d.y, -d.x))
        out.append((p[0] + nrm.x * t, p[1] + nrm.y * t))
    return out


# ----------------------------------------------------------------------------- rig roots
ROOT = add_empty("EX_Root", loc=(0, 0, 0))
SWING = add_empty("EX_Swing", loc=(0, 0, 1.28), rot=(0, 0, R(20)), parent=ROOT)
BOOM = add_empty("EX_BoomPivot", loc=(0.95, 0.0, 0.57), rot=(0, R(-30), 0), parent=SWING)
ARM = add_empty("EX_ArmPivot", loc=(5.0, 0.0, 0.60), rot=(0, R(76), 0), parent=BOOM)
BKT = add_empty("EX_BucketPivot", loc=(2.95, 0.0, 0.0), rot=(0, R(50), 0), parent=ARM)


# ============================================================================= UNDERCARRIAGE
FX, RX, WR = 1.78, -1.78, 0.62          # sprocket / idler centre x, pitch radius
BAND_T, HALF_W = 0.105, 0.36            # shoe thickness, half track width


def track_centreline(steps_arc=14, steps_str=10):
    pts = []
    for i in range(steps_arc):                      # front arc  -90 -> +90
        a = R(-90) + TAU * 0.5 * i / steps_arc
        nrm = Vector((math.cos(a), math.sin(a)))
        pts.append((Vector((FX, WR)) + nrm * WR, nrm))
    for i in range(steps_str):                      # top run
        f = i / steps_str
        pts.append((Vector((FX + (RX - FX) * f, WR * 2.0)), Vector((0, 1))))
    for i in range(steps_arc):                      # rear arc  +90 -> +270
        a = R(90) + TAU * 0.5 * i / steps_arc
        nrm = Vector((math.cos(a), math.sin(a)))
        pts.append((Vector((RX, WR)) + nrm * WR, nrm))
    for i in range(steps_str):                      # bottom run
        f = i / steps_str
        pts.append((Vector((RX + (FX - RX) * f, 0.0)), Vector((0, -1))))
    return pts


def build_track(name, y, parent):
    holder = add_empty(name + "_Grp", loc=(0, y, 0), parent=parent)
    path = track_centreline()
    bm = bmesh.new()
    rings = []
    for p, nrm in path:
        inner = p
        outer = p + nrm * BAND_T
        rings.append([bm.verts.new((inner.x, -HALF_W, inner.y)),
                      bm.verts.new((inner.x, +HALF_W, inner.y)),
                      bm.verts.new((outer.x, +HALF_W, outer.y)),
                      bm.verts.new((outer.x, -HALF_W, outer.y))])
    for i in range(len(rings)):
        a, b = rings[i], rings[(i + 1) % len(rings)]
        for k in range(4):
            k2 = (k + 1) % 4
            bm.faces.new((a[k], a[k2], b[k2], b[k]))
    # grousers
    for i in range(0, len(path), 2):
        p, nrm = path[i]
        centre = Vector((p.x, 0.0, p.y)) + Vector((nrm.x, 0.0, nrm.y)) * (BAND_T + 0.028)
        rotm = Vector((nrm.x, 0.0, nrm.y)).to_track_quat('Z', 'Y').to_matrix().to_4x4()
        M = (Matrix.Translation(centre) @ rotm
             @ Matrix.Diagonal(Vector((0.11, HALF_W * 1.94, 0.056))).to_4x4())
        bmesh.ops.create_cube(bm, size=1.0, matrix=M)
    finish(name + "_Band", bm, M_RUBBER, holder)

    # sprocket, idler, rollers
    cyl(name + "_Sprocket", 0.50, 0.44, (FX, 0, WR), (R(90), 0, 0), M_GREY, holder, seg=24)
    for i in range(10):
        a = TAU * i / 10.0
        box(name + f"_Tooth{i}", (0.16, 0.42, 0.12),
            (FX + math.cos(a) * 0.55, 0, WR + math.sin(a) * 0.55),
            (0, -a, 0), M_GREY, holder)
    cyl(name + "_Idler", 0.47, 0.42, (RX, 0, WR), (R(90), 0, 0), M_GREY, holder, seg=24)
    cyl(name + "_IdlerHub", 0.20, 0.50, (RX, 0, WR), (R(90), 0, 0), M_DARK, holder, seg=16)
    cyl(name + "_SprHub", 0.22, 0.52, (FX, 0, WR), (R(90), 0, 0), M_DARK, holder, seg=16)
    for i, x in enumerate((-1.20, -0.42, 0.42, 1.20)):
        cyl(name + f"_Roller{i}", 0.21, 0.40, (x, 0, 0.21), (R(90), 0, 0), M_DARK, holder, seg=16)
    for i, x in enumerate((-0.75, 0.75)):
        cyl(name + f"_Carrier{i}", 0.15, 0.28, (x, 0, 1.03), (R(90), 0, 0), M_DARK, holder, seg=14)
    # side frame + guard
    box(name + "_Frame", (3.05, 0.42, 0.52), (0.0, 0.0, WR), mat=M_YELLOW,
        parent=holder, bevel=0.05)
    box(name + "_Guard", (2.20, 0.30, 0.20), (0.0, 0.0, 1.28), mat=M_YELLOW,
        parent=holder, bevel=0.03)


build_track("TrackL", 1.28, ROOT)
build_track("TrackR", -1.28, ROOT)

# car body / H-frame
box("CarBody", (1.70, 2.70, 0.60), (0.0, 0.0, 0.80), mat=M_YELLOW, parent=ROOT, bevel=0.07)
box("CarBodyBeamF", (0.55, 2.90, 0.34), (0.75, 0.0, 0.72), mat=M_YELLOW, parent=ROOT, bevel=0.05)
box("CarBodyBeamR", (0.55, 2.90, 0.34), (-0.75, 0.0, 0.72), mat=M_YELLOW, parent=ROOT, bevel=0.05)
box("DozerArm", (0.9, 2.30, 0.25), (2.30, 0.0, 0.55), (0, R(-8), 0), M_YELLOW, ROOT, bevel=0.04)
box("DozerBlade", (0.22, 2.55, 0.62), (2.80, 0.0, 0.42), (0, R(6), 0), M_GREY, ROOT, bevel=0.04)
cyl("SlewRing", 0.98, 0.26, (0.0, 0.0, 1.16), mat=M_GREY, parent=ROOT, seg=32)
cyl("SlewTeeth", 1.05, 0.10, (0.0, 0.0, 1.10), mat=M_DARK, parent=ROOT, seg=48)


# ============================================================================= UPPERSTRUCTURE
# deck
box("Deck", (5.20, 2.80, 0.24), (-0.50, 0.0, 0.12), mat=M_YELLOW, parent=SWING, bevel=0.05)
box("DeckSkirtL", (5.10, 0.10, 0.22), (-0.50, 1.36, -0.02), mat=M_DARK, parent=SWING)
box("DeckSkirtR", (5.10, 0.10, 0.22), (-0.50, -1.36, -0.02), mat=M_DARK, parent=SWING)
cyl("SwingHub", 0.85, 0.30, (0.0, 0.0, -0.10), mat=M_DARK, parent=SWING, seg=28)

# counterweight
box("Counterweight", (1.25, 2.72, 1.32), (-2.42, 0.0, 0.88), mat=M_YELLOW,
    parent=SWING, bevel=0.16, segs=3)
box("CWPlate", (0.10, 1.60, 0.55), (-3.06, 0.0, 0.95), mat=M_DARK, parent=SWING, bevel=0.03)

# engine housing / hood
box("EngineHood", (1.85, 2.62, 0.86), (-1.00, 0.0, 0.67), mat=M_YELLOW,
    parent=SWING, bevel=0.09, segs=2)
box("HoodTop", (1.55, 2.30, 0.10), (-1.00, 0.0, 1.14), mat=M_YELLOW, parent=SWING, bevel=0.04)
for i in range(7):
    box(f"Louver{i}", (0.06, 0.90, 0.055), (-1.72, -0.75, 0.45 + i * 0.10),
        mat=M_DARK, parent=SWING)
for i in range(5):
    box(f"HoodVent{i}", (0.55, 0.05, 0.05), (-1.00, 0.55 + i * 0.11, 1.20),
        mat=M_DARK, parent=SWING)
cyl("Exhaust", 0.085, 0.55, (-0.45, -0.85, 1.35), mat=M_DARK, parent=SWING, seg=14)
cyl("ExhaustCap", 0.11, 0.09, (-0.45, -0.85, 1.64), mat=M_DARK, parent=SWING, seg=14)

# hydraulic / fuel tanks on the right side
box("HydTank", (1.15, 0.80, 0.85), (0.42, -0.85, 0.66), mat=M_YELLOW, parent=SWING, bevel=0.08)
box("FuelTank", (0.85, 0.78, 0.78), (1.45, -0.85, 0.62), mat=M_YELLOW, parent=SWING, bevel=0.08)
box("ToolBox", (0.60, 0.62, 0.45), (-1.95, -0.95, 1.42), mat=M_GREY, parent=SWING, bevel=0.04)

# walkway handrails
for side, sy in (("L", 1.30), ("R", -1.30)):
    for i, x in enumerate((-2.10, -1.10, -0.10)):
        cyl(f"RailPost{side}{i}", 0.035, 0.70, (x, sy, 0.58), mat=M_ORANGE, parent=SWING, seg=10)
    rod_between(f"RailTop{side}", wp(SWING, (-2.10, sy, 0.93)), wp(SWING, (-0.10, sy, 0.93)),
                0.035, M_ORANGE, SWING)

# ------------------------------------------------------------------ operator cab
CX0, CX1 = 0.20, 2.00
CY0, CY1 = 0.32, 1.62
CZ0, CZ1 = 0.24, 1.82
P = 0.075                                    # post section


def cab_post(name, p, q):
    rod_between(name, wp(SWING, p), wp(SWING, q), P, M_DARK, SWING)


box("CabFloor", (CX1 - CX0, CY1 - CY0, 0.10), ((CX0 + CX1) / 2, (CY0 + CY1) / 2, CZ0 + 0.05),
    mat=M_DARK, parent=SWING)
box("CabRoof", (CX1 - CX0 + 0.14, CY1 - CY0 + 0.14, 0.11),
    ((CX0 + CX1) / 2, (CY0 + CY1) / 2, CZ1 - 0.05), mat=M_YELLOW, parent=SWING, bevel=0.05)
for xx in (CX0, CX1):
    for yy in (CY0, CY1):
        cab_post(f"CabPost_{xx}_{yy}", (xx, yy, CZ0), (xx, yy, CZ1))
for (a, b) in (((CX0, CY0, CZ1 - 0.06), (CX0, CY1, CZ1 - 0.06)),
               ((CX1, CY0, CZ1 - 0.06), (CX1, CY1, CZ1 - 0.06)),
               ((CX0, CY0, CZ1 - 0.06), (CX1, CY0, CZ1 - 0.06)),
               ((CX0, CY1, CZ1 - 0.06), (CX1, CY1, CZ1 - 0.06))):
    rod_between("CabBeam", wp(SWING, a), wp(SWING, b), P * 0.85, M_DARK, SWING)

# lower panels
box("CabPanelRear", (0.08, CY1 - CY0, 0.95), (CX0, (CY0 + CY1) / 2, CZ0 + 0.5),
    mat=M_YELLOW, parent=SWING, bevel=0.02)
box("CabPanelFrontLow", (0.07, CY1 - CY0, 0.42), (CX1, (CY0 + CY1) / 2, CZ0 + 0.24),
    mat=M_YELLOW, parent=SWING, bevel=0.02)
box("CabPanelDoorLow", (CX1 - CX0, 0.07, 0.45), ((CX0 + CX1) / 2, CY1, CZ0 + 0.25),
    mat=M_YELLOW, parent=SWING, bevel=0.02)
box("CabPanelInnerLow", (CX1 - CX0, 0.07, 0.62), ((CX0 + CX1) / 2, CY0, CZ0 + 0.33),
    mat=M_YELLOW, parent=SWING, bevel=0.02)

# glazing
box("GlassWindshield", (0.05, CY1 - CY0 - 0.10, 1.05), (CX1 - 0.01, (CY0 + CY1) / 2, CZ0 + 1.02),
    mat=M_GLASS, parent=SWING)
box("GlassDoorUpper", (CX1 - CX0 - 0.14, 0.045, 0.90), ((CX0 + CX1) / 2, CY1 - 0.01, CZ0 + 1.13),
    mat=M_GLASS, parent=SWING)
box("GlassInner", (CX1 - CX0 - 0.14, 0.045, 0.72), ((CX0 + CX1) / 2, CY0 + 0.01, CZ0 + 1.22),
    mat=M_GLASS, parent=SWING)
box("GlassRear", (0.045, CY1 - CY0 - 0.16, 0.42), (CX0 + 0.02, (CY0 + CY1) / 2, CZ0 + 1.38),
    mat=M_GLASS, parent=SWING)
box("GlassRoof", (0.60, CY1 - CY0 - 0.22, 0.04), (CX0 + 0.75, (CY0 + CY1) / 2, CZ1 - 0.12),
    mat=M_GLASS, parent=SWING)

# cab interior: seat + consoles + joysticks
box("Seat", (0.52, 0.52, 0.14), (0.85, 0.97, CZ0 + 0.58), mat=M_BLACK, parent=SWING, bevel=0.04)
box("SeatBack", (0.14, 0.52, 0.62), (0.60, 0.97, CZ0 + 0.92), (0, R(-8), 0),
    M_BLACK, SWING, bevel=0.04)
for i, yy in ((0, 0.62), (1, 1.32)):
    box(f"Console{i}", (0.42, 0.20, 0.16), (1.05, yy, CZ0 + 0.66), mat=M_BLACK,
        parent=SWING, bevel=0.03)
    cyl(f"Joystick{i}", 0.026, 0.26, (1.05, yy, CZ0 + 0.86), mat=M_BLACK, parent=SWING, seg=10)
    cyl(f"JoystickKnob{i}", 0.055, 0.10, (1.05, yy, CZ0 + 1.00), mat=M_ORANGE, parent=SWING, seg=12)
box("Pedals", (0.28, 0.55, 0.05), (1.72, 0.97, CZ0 + 0.14), (0, R(-14), 0), M_DARK, SWING)

# roof work lights and beacon
for i, yy in enumerate((CY0 + 0.22, CY1 - 0.22)):
    box(f"WorkLamp{i}", (0.16, 0.20, 0.16), (CX1 - 0.02, yy, CZ1 + 0.02), (0, R(18), 0),
        M_DARK, SWING, bevel=0.03)
cyl("BeaconBase", 0.06, 0.08, (CX0 + 0.28, CY0 + 0.25, CZ1 + 0.04), mat=M_DARK,
    parent=SWING, seg=12)
cyl("Beacon", 0.065, 0.14, (CX0 + 0.28, CY0 + 0.25, CZ1 + 0.14), mat=M_ORANGE,
    parent=SWING, seg=12)

# boom foot mount plates
for i, yy in enumerate((0.46, -0.46)):
    box(f"BoomMount{i}", (0.70, 0.14, 1.00), (0.95, yy, 0.42), mat=M_YELLOW,
        parent=SWING, bevel=0.04)
cyl("BoomFootPin", 0.13, 1.18, (0.95, 0.0, 0.57), (R(90), 0, 0), M_DARK, SWING, seg=18)


# ============================================================================= BOOM
BOOM_SECS = [(-0.28, 0.02, 0.44, 0.30),
             (0.60, 0.28, 0.46, 0.30),
             (1.70, 0.78, 0.44, 0.28),
             (2.70, 1.12, 0.42, 0.26),
             (3.70, 0.98, 0.34, 0.24),
             (4.60, 0.72, 0.28, 0.22),
             (5.05, 0.60, 0.24, 0.22)]
beam("Boom", BOOM_SECS, M_YELLOW, BOOM, bevel=0.04)
cyl("BoomTipPin", 0.10, 0.62, (5.0, 0.0, 0.60), (R(90), 0, 0), M_DARK, BOOM, seg=16)
cyl("BoomFootBoss", 0.20, 0.66, (0.0, 0.0, 0.0), (R(90), 0, 0), M_DARK, BOOM, seg=18)
# boom cylinder ears (for the arm ram) and hose runs
for i, yy in enumerate((0.30, -0.30)):
    box(f"BoomEar{i}", (0.55, 0.09, 0.30), (1.85, yy, 1.10), (0, R(-14), 0),
        M_GREY, BOOM, bevel=0.03)
    box(f"BoomRamEar{i}", (0.46, 0.09, 0.26), (2.35, yy, 0.55), (0, R(-16), 0),
        M_GREY, BOOM, bevel=0.03)
rod_between("BoomHoseA", wp(BOOM, (0.2, 0.16, 0.48)), wp(BOOM, (4.7, 0.16, 0.85)),
            0.035, M_BLACK, BOOM)
rod_between("BoomHoseB", wp(BOOM, (0.2, 0.04, 0.50)), wp(BOOM, (4.7, 0.04, 0.87)),
            0.035, M_BLACK, BOOM)


# ============================================================================= ARM (STICK)
ARM_SECS = [(-0.30, 0.10, 0.40, 0.24),
            (0.35, 0.06, 0.42, 0.24),
            (1.20, 0.00, 0.36, 0.22),
            (2.10, -0.02, 0.28, 0.20),
            (2.95, 0.00, 0.20, 0.19)]
beam("Arm", ARM_SECS, M_YELLOW, ARM, bevel=0.035)
cyl("ArmFootBoss", 0.17, 0.56, (0.0, 0.0, 0.0), (R(90), 0, 0), M_DARK, ARM, seg=18)
cyl("ArmTipPin", 0.095, 0.52, (2.95, 0.0, 0.0), (R(90), 0, 0), M_DARK, ARM, seg=16)
for i, yy in enumerate((0.26, -0.26)):
    box(f"ArmRamEar{i}", (0.34, 0.08, 0.44), (0.30, yy, 0.48), mat=M_GREY, parent=ARM, bevel=0.03)
    box(f"ArmLinkEar{i}", (0.34, 0.08, 0.34), (2.42, yy, 0.32), mat=M_GREY, parent=ARM, bevel=0.03)
rod_between("ArmHose", wp(ARM, (0.1, 0.0, 0.45)), wp(ARM, (2.4, 0.0, 0.30)),
            0.036, M_BLACK, ARM)


# ============================================================================= BUCKET
BW = 0.58                                     # half width
INNER = [(0.02, -0.06), (0.05, -0.46), (0.14, -0.86), (0.34, -1.14),
         (0.68, -1.30), (1.02, -1.32), (1.24, -1.28)]
OUTER = offset_path(INNER, 0.075)
poly_solid("BucketShell", INNER + list(reversed(OUTER)), -BW, BW, M_GREY, BKT, bevel=0.012)

# side cutting plates
for i, (ya, yb) in enumerate(((BW, BW + 0.05), (-BW - 0.05, -BW))):
    poly_solid(f"BucketSide{i}", INNER + [(1.10, -0.55), (0.55, -0.10)], ya, yb, M_GREY, BKT)

# back ribs and mounting ears
for i, yy in enumerate((0.22, -0.22)):
    box(f"BucketEar{i}", (0.14, 0.10, 0.52), (-0.05, yy, -0.26), (0, R(10), 0),
        M_GREY, BKT, bevel=0.02)
cyl("BucketPin", 0.095, 0.62, (0.0, 0.0, 0.0), (R(90), 0, 0), M_DARK, BKT, seg=16)
cyl("BucketLinkPin", 0.075, 0.50, (-0.16, 0.0, -0.48), (R(90), 0, 0), M_DARK, BKT, seg=14)

# teeth along the lip
lip = Vector(INNER[-1])
tdir = (Vector(INNER[-1]) - Vector(INNER[-2])).normalized()
for i in range(5):
    y = -BW + 0.13 + i * ((2 * BW - 0.26) / 4.0)
    base = Vector((lip.x, y, lip.y - 0.03))
    d3 = Vector((tdir.x, 0.0, tdir.y))
    box(f"ToothAdapter{i}", (0.16, 0.17, 0.10), tuple(base + d3 * 0.04),
        (0, -math.atan2(tdir.y, tdir.x), 0), M_DARK, BKT)
    bm = bmesh.new()
    M = (Matrix.Translation(base + d3 * 0.20)
         @ d3.to_track_quat('Z', 'Y').to_matrix().to_4x4())
    bmesh.ops.create_cone(bm, cap_ends=True, cap_tris=False, segments=4,
                          radius1=0.085, radius2=0.022, depth=0.30, matrix=M)
    finish(f"Tooth{i}", bm, M_DARK, BKT)


# ============================================================================= HYDRAULICS
bpy.context.view_layer.update()

# boom rams: deck -> boom underside
for i, yy in enumerate((0.62, -0.62)):
    hydraulic(f"BoomRam{i}",
              wp(SWING, (0.55, yy, 0.18)),
              wp(BOOM, (2.35, yy * 0.48, 0.55)),
              rb=0.135, rr=0.072, parent_a=SWING, parent_b=BOOM)

# arm ram: boom top -> arm ear
hydraulic("ArmRam",
          wp(BOOM, (1.85, 0.0, 1.18)),
          wp(ARM, (0.30, 0.0, 0.52)),
          rb=0.145, rr=0.078, parent_a=BOOM, parent_b=ARM)

# bucket ram + H-link
A = wp(ARM, (2.42, 0.0, 0.36))               # arm-side link anchor
E = wp(BKT, (-0.16, 0.0, -0.48))             # bucket-side link anchor
mid = (A + E) * 0.5
axis = (E - A).normalized()
yaxis = (wp(ARM, (0, 1, 0)) - wp(ARM, (0, 0, 0))).normalized()
up = axis.cross(yaxis).normalized()
L = mid + up * 0.34                           # floating knuckle of the H-link
hydraulic("BucketRam", wp(ARM, (0.42, 0.0, 0.52)), L,
          rb=0.125, rr=0.066, parent_a=ARM, parent_b=ARM)
side = yaxis * 0.15
for i, s in enumerate((side, -side)):
    rod_between(f"HLink{i}", A + s, L + s, 0.055, M_GREY, ARM)
    rod_between(f"BucketLink{i}", L + s, E + s, 0.05, M_GREY, ARM)
pin_ball("HLinkPin", L, 0.085, M_DARK, ARM)


# ============================================================================= ENVIRONMENT
gbm = bmesh.new()
bmesh.ops.create_grid(gbm, x_segments=24, y_segments=24, size=22.0)
finish("Ground", gbm, M_GROUND)

# a small spoil pile beside the machine, for scale
pbm = bmesh.new()
bmesh.ops.create_icosphere(pbm, subdivisions=2, radius=1.5,
                           matrix=Matrix.Translation((6.4, 2.6, -0.55))
                           @ Matrix.Diagonal(Vector((1.0, 0.8, 0.5, 1.0))))
finish("SpoilPile", pbm, M_GROUND)

# lighting
sun_data = bpy.data.lights.new("Sun", 'SUN')
sun_data.energy = 4.0
sun_data.angle = R(2.5)
sun_data.color = (1.0, 0.95, 0.85)
sun = bpy.data.objects.new("Sun", sun_data)
sun.location = (8.0, -10.0, 14.0)
sun.rotation_euler = (R(52), 0.0, R(38))
COLL.objects.link(sun)

fill_data = bpy.data.lights.new("Fill", 'AREA')
fill_data.energy = 900.0
fill_data.size = 9.0
fill_data.color = (0.72, 0.80, 1.0)
fill = bpy.data.objects.new("Fill", fill_data)
fill.location = (-11.0, 9.0, 8.0)
fill.rotation_euler = (R(58), 0.0, R(-135))
COLL.objects.link(fill)

rim_data = bpy.data.lights.new("Rim", 'AREA')
rim_data.energy = 500.0
rim_data.size = 5.0
rim = bpy.data.objects.new("Rim", rim_data)
rim.location = (-6.0, -9.0, 6.0)
rim.rotation_euler = (R(65), 0.0, R(-30))
COLL.objects.link(rim)

world = bpy.data.worlds.new("World")
world.use_nodes = True
bg = world.node_tree.nodes.get("Background")
if bg:
    bg.inputs[0].default_value = (0.32, 0.40, 0.50, 1.0)
    bg.inputs[1].default_value = 1.0
scene.world = world

# camera
cam_data = bpy.data.cameras.new("Camera")
cam_data.lens = 48.0
cam_data.clip_end = 300.0
cam = bpy.data.objects.new("Camera", cam_data)
cam.location = (13.5, -12.0, 7.4)
target = Vector((2.0, 1.0, 2.4))
cam.rotation_euler = (target - cam.location).to_track_quat('-Z', 'Y').to_euler()
COLL.objects.link(cam)
scene.camera = cam

# shade the round bits smoothly
for ob in COLL.objects:
    if ob.type == 'MESH' and any(k in ob.name for k in
                                 ("Sprocket", "Idler", "Roller", "Ram", "Rod", "Pin",
                                  "Slew", "Hose", "Link", "Exhaust", "Beacon", "Spoil")):
        for p in ob.data.polygons:
            p.use_smooth = True
