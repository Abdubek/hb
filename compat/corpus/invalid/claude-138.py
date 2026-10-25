"""
claude-138 - Compact boat cabin interior for Blender 4.5 LTS

Builds, from an empty factory scene:
  * a monocoque cabin shell with flared topsides and a curved (elliptical) deckhead
  * teak-and-holly cabin sole, deckhead ribs and overhead grab rails
  * a long port berth with a stacked upper bunk (lee cloth + brass lee rail)
  * a starboard settee berth with lockers
  * three brass portholes cut through the topsides, plus a glazed deck hatch
  * a fold-down (deployed) saloon table with fiddles and folding legs
  * bulkheads fore and aft, companionway opening and steps
  * practical lamps, daylight through the glazing, and an interior camera

Scene construction only - nothing is rendered or saved.
"""

import bpy
import bmesh
import math
from mathutils import Vector, Matrix, Euler


# ----------------------------------------------------------------- constants
HALF_LEN = 2.10          # cabin half length along +/-Y
SHELL_T = 0.08           # shell thickness
ARCH_A = 1.22            # deckhead ellipse half width
ARCH_B = 0.80            # deckhead ellipse rise
ARCH_Z = 1.15            # height at which the topsides meet the arch
SOLE_Z = 0.025           # top of the cabin sole

# half section of the topsides, from the sole up to the springing of the arch
SIDE = [(1.05, 0.00), (1.12, 0.30), (1.18, 0.62), (1.21, 0.90), (ARCH_A, ARCH_Z)]


# ----------------------------------------------------------------- utilities
def reset_scene():
    bpy.ops.wm.read_factory_settings(use_empty=True)
    scene = bpy.context.scene
    scene.unit_settings.system = 'METRIC'
    try:
        scene.render.engine = 'CYCLES'
        scene.cycles.samples = 160
        scene.cycles.preview_samples = 32
    except Exception:
        scene.render.engine = 'BLENDER_EEVEE_NEXT'
    scene.render.resolution_x = 1920
    scene.render.resolution_y = 1080


def make_collection(name):
    coll = bpy.data.collections.new(name)
    bpy.context.scene.collection.children.link(coll)
    lc = bpy.context.view_layer.layer_collection.children[coll.name]
    bpy.context.view_layer.active_layer_collection = lc
    return coll


def material(name, base, rough=0.5, metal=0.0, emission=None, strength=0.0,
             alpha=1.0, transmission=0.0, ior=1.45):
    mat = bpy.data.materials.new(name)
    mat.use_nodes = True
    bsdf = mat.node_tree.nodes.get("Principled BSDF")
    i = bsdf.inputs
    i["Base Color"].default_value = (base[0], base[1], base[2], 1.0)
    i["Roughness"].default_value = rough
    i["Metallic"].default_value = metal
    if "IOR" in i:
        i["IOR"].default_value = ior
    if "Transmission Weight" in i:
        i["Transmission Weight"].default_value = transmission
    elif "Transmission" in i:
        i["Transmission"].default_value = transmission
    if emission is not None:
        if "Emission Color" in i:
            i["Emission Color"].default_value = (emission[0], emission[1], emission[2], 1.0)
        i["Emission Strength"].default_value = strength
    i["Alpha"].default_value = alpha
    if alpha < 1.0:
        mat.blend_method = 'BLEND'
    return mat


def obj_from_bm(name, bm, mat=None, smooth_quads=False, coll=None):
    if smooth_quads:
        for f in bm.faces:
            f.smooth = (len(f.verts) == 4)
    me = bpy.data.meshes.new(name)
    bm.to_mesh(me)
    bm.free()
    me.validate()
    ob = bpy.data.objects.new(name, me)
    (coll or CABIN).objects.link(ob)
    if mat is not None:
        me.materials.append(mat)
    return ob


def bm_box(bm, center, size, rot=(0.0, 0.0, 0.0)):
    mrot = Euler(rot, 'XYZ').to_matrix().to_4x4()
    mscale = Matrix.Diagonal(Vector((size[0], size[1], size[2], 1.0)))
    mat = Matrix.Translation(Vector(center)) @ mrot @ mscale
    bmesh.ops.create_cube(bm, size=1.0, matrix=mat)


def bm_cyl(bm, center, radius, depth, axis='Z', segments=24, rot=None):
    axis_rot = {
        'Z': Matrix.Identity(4),
        'X': Matrix.Rotation(math.pi * 0.5, 4, 'Y'),
        'Y': Matrix.Rotation(-math.pi * 0.5, 4, 'X'),
    }[axis]
    extra = Euler(rot, 'XYZ').to_matrix().to_4x4() if rot else Matrix.Identity(4)
    mat = Matrix.Translation(Vector(center)) @ extra @ axis_rot
    try:
        bmesh.ops.create_cone(bm, cap_ends=True, cap_tris=False, segments=segments,
                              radius1=radius, radius2=radius, depth=depth, matrix=mat)
    except TypeError:
        bmesh.ops.create_cone(bm, cap_ends=True, cap_tris=False, segments=segments,
                              diameter1=radius, diameter2=radius, depth=depth, matrix=mat)


def bm_sphere(bm, center, radius, u=24, v=12):
    mat = Matrix.Translation(Vector(center))
    try:
        bmesh.ops.create_uvsphere(bm, u_segments=u, v_segments=v, radius=radius, matrix=mat)
    except TypeError:
        bmesh.ops.create_uvsphere(bm, u_segments=u, v_segments=v, diameter=radius, matrix=mat)


def bm_bevel(bm, offset, segments=2):
    geom = list(bm.verts) + list(bm.edges) + list(bm.faces)
    bmesh.ops.bevel(bm, geom=geom, offset=offset, offset_type='OFFSET',
                    segments=segments, profile=0.5, affect='EDGES')


def box(name, center, size, mat, rot=(0.0, 0.0, 0.0), bevel=0.0, segments=2, smooth=False):
    bm = bmesh.new()
    bm_box(bm, center, size, rot)
    if bevel > 0.0:
        bm_bevel(bm, bevel, segments)
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    ob = obj_from_bm(name, bm, mat)
    if smooth:
        for p in ob.data.polygons:
            p.use_smooth = True
    return ob


def cylinder(name, center, radius, depth, mat, axis='Z', segments=24, rot=None):
    bm = bmesh.new()
    bm_cyl(bm, center, radius, depth, axis, segments, rot)
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    return obj_from_bm(name, bm, mat, smooth_quads=True)


def apply_booleans(target, cutters, operation='DIFFERENCE'):
    """Add and immediately apply boolean modifiers, then delete the cutters."""
    for i, c in enumerate(cutters):
        m = target.modifiers.new("bool_%02d" % i, 'BOOLEAN')
        m.operation = operation
        m.solver = 'EXACT'
        m.object = c
    view = bpy.context.view_layer
    for ob in view.objects:
        ob.select_set(False)
    view.objects.active = target
    target.select_set(True)
    for m in list(target.modifiers):
        bpy.ops.object.modifier_apply(modifier=m.name)
    for c in cutters:
        bpy.data.objects.remove(c, do_unlink=True)


# ------------------------------------------------------------- cross section
def arch_points(steps=18):
    """Interior points of the elliptical deckhead, port to starboard."""
    pts = []
    for i in range(1, steps):
        t = math.pi * (1.0 - i / float(steps))
        pts.append((ARCH_A * math.cos(t), ARCH_Z + ARCH_B * math.sin(t)))
    return pts


def section_loop():
    """Closed interior section, CW or CCW is resolved later by signed area."""
    port_up = [(-x, z) for (x, z) in SIDE]
    stbd_down = [(x, z) for (x, z) in reversed(SIDE)]
    return port_up + arch_points() + stbd_down


def signed_area(loop):
    a = 0.0
    n = len(loop)
    for i in range(n):
        x0, z0 = loop[i]
        x1, z1 = loop[(i + 1) % n]
        a += x0 * z1 - x1 * z0
    return 0.5 * a


def outward_normals(loop):
    """Mitred outward normals for the closed section."""
    ccw = signed_area(loop) > 0.0
    n = len(loop)

    def edge_normal(a, b):
        e = Vector(b) - Vector(a)
        if e.length < 1e-9:
            return Vector((0.0, 1.0))
        v = Vector((e.y, -e.x)) if ccw else Vector((-e.y, e.x))
        return v.normalized()

    normals = []
    for i in range(n):
        p0 = loop[i - 1]
        p1 = loop[i]
        p2 = loop[(i + 1) % n]
        n1 = edge_normal(p0, p1)
        n2 = edge_normal(p1, p2)
        v = n1 + n2
        if v.length < 1e-9:
            v = n2.copy()
        v.normalize()
        miter = max(0.45, v.dot(n2))
        normals.append(v / miter)
    return normals


def side_x(z):
    """Interior half-beam at height z (positive/starboard side)."""
    if z <= SIDE[0][1]:
        return SIDE[0][0]
    if z >= ARCH_Z:
        s = min(1.0, (z - ARCH_Z) / ARCH_B)
        return ARCH_A * math.sqrt(max(0.0, 1.0 - s * s))
    for (x0, z0), (x1, z1) in zip(SIDE, SIDE[1:]):
        if z0 <= z <= z1:
            t = (z - z0) / (z1 - z0)
            return x0 + t * (x1 - x0)
    return SIDE[-1][0]


# ------------------------------------------------------------------- scene
reset_scene()
CABIN = make_collection("BoatCabin")

M_PAINT = material("PaintedPanel", (0.88, 0.87, 0.82), rough=0.28)
M_HULL = material("HullOutside", (0.20, 0.24, 0.28), rough=0.45)
M_TEAK = material("Teak", (0.30, 0.16, 0.075), rough=0.36)
M_HOLLY = material("Holly", (0.85, 0.80, 0.68), rough=0.40)
M_WOOD = material("VarnishedMahogany", (0.26, 0.105, 0.055), rough=0.18)
M_WOOD_L = material("VarnishedAsh", (0.52, 0.34, 0.18), rough=0.24)
M_BRASS = material("Brass", (0.72, 0.55, 0.24), rough=0.20, metal=1.0)
M_STEEL = material("Stainless", (0.62, 0.63, 0.65), rough=0.28, metal=1.0)
M_GLASS = material("PortlightGlass", (0.90, 0.93, 0.95), rough=0.03,
                   transmission=1.0, ior=1.5)
M_BLUE = material("CushionBlue", (0.10, 0.17, 0.28), rough=0.88)
M_CREAM = material("CushionCream", (0.74, 0.70, 0.61), rough=0.90)
M_CANVAS = material("Canvas", (0.66, 0.63, 0.55), rough=0.92)
M_LAMP = material("LampGlow", (1.0, 0.90, 0.72), rough=0.35,
                  emission=(1.0, 0.80, 0.52), strength=14.0)
M_PAPER = material("Chart", (0.82, 0.80, 0.72), rough=0.75)
M_CERAMIC = material("Mug", (0.16, 0.35, 0.42), rough=0.25)

LOOP = section_loop()
NRMS = outward_normals(LOOP)
OUTER = [(p[0] + n.x * SHELL_T, p[1] + n.y * SHELL_T) for p, n in zip(LOOP, NRMS)]


# ------------------------------------------------------------- cabin shell
def build_shell():
    y0, y1 = -HALF_LEN - 0.16, HALF_LEN + 0.16
    bm = bmesh.new()
    n = len(LOOP)
    inner0 = [bm.verts.new((p[0], y0, p[1])) for p in LOOP]
    inner1 = [bm.verts.new((p[0], y1, p[1])) for p in LOOP]
    outer0 = [bm.verts.new((p[0], y0, p[1])) for p in OUTER]
    outer1 = [bm.verts.new((p[0], y1, p[1])) for p in OUTER]
    for i in range(n):
        j = (i + 1) % n
        bm.faces.new((inner0[i], inner0[j], inner1[j], inner1[i]))
        bm.faces.new((outer1[i], outer1[j], outer0[j], outer0[i]))
        bm.faces.new((inner0[j], inner0[i], outer0[i], outer0[j]))
        bm.faces.new((inner1[i], inner1[j], outer1[j], outer1[i]))
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    shell = obj_from_bm("CabinShell", bm, M_PAINT)
    shell.data.materials.append(M_HULL)
    return shell


SHELL = build_shell()

# openings: three portholes and one deck hatch
PORTS = [(1.0, -0.90, 1.05), (1.0, 0.80, 1.05), (-1.0, 0.85, 1.05)]
PORT_R = 0.175
HATCH_Y = -1.35

cutters = []
for side, py, pz in PORTS:
    cutters.append(cylinder("cut_port", (side * 1.26, py, pz), PORT_R, 0.70,
                            M_PAINT, axis='X', segments=32))
cutters.append(box("cut_hatch", (0.0, HATCH_Y, 1.95), (0.52, 0.52, 0.80), M_PAINT))
apply_booleans(SHELL, cutters)


# --------------------------------------------------------------- bulkheads
def bulkhead(name, y_face, thickness, forward=True):
    bm = bmesh.new()
    verts = [bm.verts.new((p[0], y_face, p[1])) for p in LOOP]
    bm.faces.new(verts)
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    res = bmesh.ops.extrude_face_region(bm, geom=bm.faces[:])
    moved = [g for g in res['geom'] if isinstance(g, bmesh.types.BMVert)]
    bmesh.ops.translate(bm, verts=moved, vec=(0.0, -thickness if forward else thickness, 0.0))
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    return obj_from_bm(name, bm, M_PAINT)


FWD_BHD = bulkhead("BulkheadForward", -HALF_LEN, 0.06, forward=True)
AFT_BHD = bulkhead("BulkheadAft", HALF_LEN, 0.06, forward=False)

# companionway opening in the aft bulkhead
door_cut = box("cut_door", (0.0, HALF_LEN + 0.03, 1.00), (0.76, 0.30, 1.92), M_PAINT)
apply_booleans(AFT_BHD, [door_cut])

# door trim
for dx in (-0.40, 0.40):
    box("DoorTrimSide", (dx, HALF_LEN - 0.015, 1.00), (0.05, 0.035, 1.98), M_WOOD)
box("DoorTrimHead", (0.0, HALF_LEN - 0.015, 1.985), (0.85, 0.035, 0.07), M_WOOD)

# companionway steps
box("Step01", (0.0, 1.80, 0.115), (0.80, 0.30, 0.18), M_TEAK, bevel=0.008)
box("Step02", (0.0, 2.02, 0.315), (0.80, 0.26, 0.18), M_TEAK, bevel=0.008)
for sy, sz in ((1.80, 0.02), (2.02, 0.22)):
    box("StepRiser", (0.0, sy - 0.155, sz + 0.09), (0.80, 0.02, 0.185), M_WOOD)


# -------------------------------------------------------------- cabin sole
def build_sole():
    bm_t = bmesh.new()
    bm_h = bmesh.new()
    x = -1.02
    plank, seam = 0.115, 0.014
    while x < 1.02:
        w = min(plank, 1.02 - x)
        bm_box(bm_t, (x + w * 0.5, 0.0, SOLE_Z * 0.5), (w * 0.985, 2.0 * HALF_LEN - 0.02, SOLE_Z))
        x += w
        if x < 1.02:
            w2 = min(seam, 1.02 - x)
            bm_box(bm_h, (x + w2 * 0.5, 0.0, SOLE_Z * 0.5),
                   (w2, 2.0 * HALF_LEN - 0.02, SOLE_Z * 1.02))
            x += w2
    obj_from_bm("SoleTeak", bm_t, M_TEAK)
    obj_from_bm("SoleHolly", bm_h, M_HOLLY)
    # flush lifting ring for the bilge access board
    bpy.ops.mesh.primitive_torus_add(location=(0.0, 1.15, SOLE_Z + 0.004),
                                     major_radius=0.045, minor_radius=0.008,
                                     major_segments=32, minor_segments=8)
    ring = bpy.context.object
    ring.name = "SolePullRing"
    ring.data.materials.append(M_BRASS)
    for p in ring.data.polygons:
        p.use_smooth = True


build_sole()


# ------------------------------------------------------- deckhead ribs etc.
def build_ribs():
    idx = [i for i, p in enumerate(LOOP) if p[1] >= 0.95]
    bm = bmesh.new()
    depth = 0.045
    for ry in (-1.85, -0.95, -0.05, 0.85, 1.75):
        if abs(ry - HATCH_Y) < 0.36:
            continue
        y0, y1 = ry - 0.028, ry + 0.028
        rings = []
        for i in idx:
            px, pz = LOOP[i]
            nx, nz = NRMS[i].x, NRMS[i].y
            a = Vector((px - nx * 0.002, 0.0, pz - nz * 0.002))
            b = Vector((px - nx * depth, 0.0, pz - nz * depth))
            rings.append([
                bm.verts.new((a.x, y0, a.z)),
                bm.verts.new((b.x, y0, b.z)),
                bm.verts.new((b.x, y1, b.z)),
                bm.verts.new((a.x, y1, a.z)),
            ])
        for r0, r1 in zip(rings, rings[1:]):
            for k in range(4):
                m = (k + 1) % 4
                bm.faces.new((r0[k], r0[m], r1[m], r1[k]))
        bm.faces.new(rings[0])
        bm.faces.new(list(reversed(rings[-1])))
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    obj_from_bm("DeckheadRibs", bm, M_WOOD_L)


build_ribs()


def build_grabrails():
    bm = bmesh.new()
    for sx in (-0.62, 0.62):
        rz = ARCH_Z + ARCH_B * math.sqrt(max(0.0, 1.0 - (abs(sx) / ARCH_A) ** 2))
        bm_cyl(bm, (sx, 0.0, rz - 0.105), 0.022, 3.5, axis='Y', segments=16)
        for gy in (-1.60, -0.80, 0.0, 0.80, 1.60):
            bm_box(bm, (sx, gy, rz - 0.045), (0.05, 0.06, 0.12))
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    obj_from_bm("GrabRails", bm, M_WOOD, smooth_quads=True)


build_grabrails()


# ------------------------------------------------------------- port berths
def build_port_berths():
    x_in, x_out = -1.17, -0.32
    xc = (x_in + x_out) * 0.5
    xw = abs(x_out - x_in)
    y_lo_c, y_lo_l = -0.25, 3.52          # lower berth, y from -2.01 to 1.51
    y_up_c, y_up_l = -1.08, 1.86          # upper bunk

    # lower berth platform and locker face
    box("BerthLowerBase", (xc, y_lo_c, 0.395), (xw, y_lo_l, 0.05), M_WOOD_L)
    box("BerthLowerFace", (x_out - 0.018, y_lo_c, 0.20), (0.036, y_lo_l, 0.37), M_WOOD)
    for i, dy in enumerate((-1.55, -0.70, 0.15, 1.00)):
        box("BerthLocker%d" % i, (x_out - 0.002, dy, 0.20), (0.022, 0.72, 0.27),
            M_WOOD_L, bevel=0.006)
        cylinder("LockerKnob%d" % i, (x_out + 0.018, dy, 0.20), 0.016, 0.035,
                 M_BRASS, axis='X', segments=14)
    box("BerthLowerMattress", (xc - 0.01, y_lo_c, 0.485), (xw - 0.05, y_lo_l - 0.06, 0.13),
        M_BLUE, bevel=0.045, segments=3)
    box("PillowLower", (xc - 0.02, -1.78, 0.575), (0.56, 0.34, 0.15), M_CREAM,
        rot=(0.0, 0.0, math.radians(5.0)), bevel=0.06, segments=3)
    box("BlanketLower", (xc - 0.02, 0.55, 0.575), (xw - 0.10, 0.80, 0.075), M_CANVAS,
        bevel=0.03, segments=2)

    # upper bunk
    box("BunkUpperBase", (xc, y_up_c, 1.095), (xw, y_up_l, 0.05), M_WOOD_L)
    box("BunkUpperMattress", (xc - 0.01, y_up_c, 1.185), (xw - 0.05, y_up_l - 0.06, 0.13),
        M_BLUE, bevel=0.045, segments=3)
    box("PillowUpper", (xc - 0.02, -1.78, 1.275), (0.56, 0.34, 0.15), M_CREAM,
        rot=(0.0, 0.0, math.radians(-4.0)), bevel=0.06, segments=3)
    box("LeeCloth", (x_out - 0.008, y_up_c, 1.245), (0.018, y_up_l - 0.10, 0.26),
        M_CANVAS)

    bm = bmesh.new()
    bm_cyl(bm, (x_out - 0.01, y_up_c, 1.375), 0.020, y_up_l - 0.02, axis='Y', segments=16)
    for ey in (y_up_c - (y_up_l - 0.02) * 0.5, y_up_c + (y_up_l - 0.02) * 0.5):
        bm_cyl(bm, (x_out - 0.01, ey, 1.245), 0.020, 0.27, axis='Z', segments=16)
    for py in (-1.99, -0.18):
        bm_cyl(bm, (x_out - 0.02, py, 0.77), 0.026, 0.70, axis='Z', segments=16)
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    obj_from_bm("BunkLeeRail", bm, M_BRASS, smooth_quads=True)

    # shelf with fiddle over the aft end of the lower berth
    sx = -(side_x(1.42) - 0.11)
    box("PortShelf", (sx, 0.72, 1.42), (0.22, 1.55, 0.025), M_WOOD_L)
    box("PortShelfFiddle", (sx + 0.10, 0.72, 1.462), (0.018, 1.55, 0.06), M_WOOD)


build_port_berths()


# ------------------------------------------------------ starboard settee
def build_settee():
    y_c, y_l = -0.10, 2.70                # settee from -1.45 to 1.25
    x_in, x_out = 1.18, 0.42
    xc = (x_in + x_out) * 0.5
    xw = x_in - x_out

    box("SetteeBase", (xc, y_c, 0.18 + SOLE_Z * 0.5), (xw, y_l, 0.36), M_WOOD_L)
    box("SetteeFace", (x_out + 0.018, y_c, 0.20), (0.036, y_l, 0.36), M_WOOD)
    for i, dy in enumerate((-1.02, -0.10, 0.82)):
        box("SetteeLocker%d" % i, (x_out - 0.002, dy, 0.20), (0.022, 0.80, 0.26),
            M_WOOD_L, bevel=0.006)
        cylinder("SetteeKnob%d" % i, (x_out - 0.018, dy, 0.20), 0.016, 0.035,
                 M_BRASS, axis='X', segments=14)
    box("SetteeCushion", (xc, y_c, 0.425), (xw - 0.05, y_l - 0.06, 0.115),
        M_BLUE, bevel=0.04, segments=3)
    box("SetteeBack", (side_x(0.59) - 0.06, y_c, 0.59), (0.11, y_l - 0.10, 0.22),
        M_BLUE, rot=(0.0, math.radians(-5.0), 0.0), bevel=0.035, segments=3)
    for cy in (-1.20, 1.00):
        box("ScatterCushion", (0.92, cy, 0.585), (0.34, 0.12, 0.30), M_CREAM,
            rot=(math.radians(8.0), 0.0, 0.0), bevel=0.05, segments=3)

    sx = side_x(1.38) - 0.11
    box("StbdShelf", (sx, -0.10, 1.38), (0.22, 2.45, 0.025), M_WOOD_L)
    box("StbdShelfFiddle", (sx - 0.10, -0.10, 1.422), (0.018, 2.45, 0.06), M_WOOD)
    for i, by in enumerate((-1.00, -0.86, -0.72, -0.58)):
        box("Book%d" % i, (sx + 0.01, by, 1.485), (0.15, 0.035 + 0.01 * i, 0.20),
            M_WOOD if i % 2 else M_PAPER, rot=(math.radians(3.0 * i), 0.0, 0.0))


build_settee()


# ------------------------------------------------------- fold-down table
def build_table():
    wall_x = side_x(0.72)
    top_z = 0.750
    thick = 0.035
    y_c, y_l = -0.15, 1.30
    x_in = wall_x - 0.05                  # hinged edge, just off the topsides
    x_out = 0.50                          # free edge
    xc = (x_in + x_out) * 0.5
    xw = x_in - x_out

    box("TableCleat", (wall_x - 0.028, y_c, 0.700), (0.055, y_l + 0.06, 0.12), M_WOOD)
    box("TableTop", (xc, y_c, top_z - thick * 0.5), (xw, y_l, thick), M_WOOD,
        bevel=0.008, segments=2)
    box("TableFiddleOuter", (x_out + 0.012, y_c, top_z + 0.017), (0.024, y_l, 0.034), M_WOOD)
    for dy in (-1.0, 1.0):
        box("TableFiddleEnd", (xc, y_c + dy * (y_l * 0.5 - 0.012), top_z + 0.017),
            (xw, 0.024, 0.034), M_WOOD)

    bm = bmesh.new()
    for hy in (y_c - 0.48, y_c, y_c + 0.48):          # piano hinge knuckles
        bm_cyl(bm, (x_in + 0.008, hy, top_z - thick * 0.5), 0.018, 0.11,
               axis='Y', segments=14)
    for ly in (y_c - 0.44, y_c + 0.44):               # folding legs
        bm_cyl(bm, (0.60, ly, (top_z - thick + SOLE_Z) * 0.5 + 0.01), 0.022,
               top_z - thick - SOLE_Z, axis='Z', segments=16)
    bm_cyl(bm, (0.60, y_c, 0.16), 0.016, 0.88, axis='Y', segments=14)
    bm_box(bm, (x_in - 0.09, y_c - 0.48, top_z - 0.075), (0.16, 0.02, 0.09),
           rot=(0.0, math.radians(-28.0), 0.0))
    bm_box(bm, (x_in - 0.09, y_c + 0.48, top_z - 0.075), (0.16, 0.02, 0.09),
           rot=(0.0, math.radians(-28.0), 0.0))
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    obj_from_bm("TableHardware", bm, M_BRASS, smooth_quads=True)

    # things on the table
    box("Chart", (0.86, 0.18, top_z + 0.004), (0.44, 0.60, 0.006), M_PAPER,
        rot=(0.0, 0.0, math.radians(9.0)))
    box("Notebook", (0.72, -0.52, top_z + 0.010), (0.22, 0.30, 0.020), M_WOOD_L,
        rot=(0.0, 0.0, math.radians(-14.0)), bevel=0.004)
    cylinder("Mug", (0.66, -0.05, top_z + 0.050), 0.042, 0.100, M_CERAMIC, segments=24)
    bpy.ops.mesh.primitive_torus_add(location=(0.66, -0.108, top_z + 0.055),
                                     rotation=(math.pi * 0.5, 0.0, 0.0),
                                     major_radius=0.030, minor_radius=0.007,
                                     major_segments=24, minor_segments=8)
    handle = bpy.context.object
    handle.name = "MugHandle"
    handle.data.materials.append(M_CERAMIC)
    for p in handle.data.polygons:
        p.use_smooth = True


build_table()


# ----------------------------------------------------------- portholes
def build_portholes():
    for i, (side, py, pz) in enumerate(PORTS):
        wx = side_x(pz)
        inner_x = side * (wx - 0.012)
        outer_x = side * (wx + SHELL_T + 0.012)
        rot = (0.0, math.pi * 0.5, 0.0)

        for tag, tx, major, minor in (("In", inner_x, PORT_R + 0.030, 0.036),
                                      ("Out", outer_x, PORT_R + 0.022, 0.026)):
            bpy.ops.mesh.primitive_torus_add(location=(tx, py, pz), rotation=rot,
                                             major_radius=major, minor_radius=minor,
                                             major_segments=48, minor_segments=12)
            ring = bpy.context.object
            ring.name = "PortholeRing%s_%d" % (tag, i)
            ring.data.materials.append(M_BRASS)
            for p in ring.data.polygons:
                p.use_smooth = True

        spigot = cylinder("PortholeSpigot_%d" % i, (side * (wx + SHELL_T * 0.5), py, pz),
                          PORT_R + 0.012, SHELL_T + 0.02, M_BRASS, axis='X', segments=48)
        spigot.name = "PortholeSpigot_%d" % i
        cylinder("PortholeGlass_%d" % i, (side * (wx + SHELL_T * 0.55), py, pz),
                 PORT_R + 0.006, 0.012, M_GLASS, axis='X', segments=48)

        # dogs (clamping handles) top and bottom of the inner ring
        bm = bmesh.new()
        for ang in (math.radians(35.0), math.radians(215.0)):
            dy = py + math.cos(ang) * (PORT_R + 0.052)
            dz = pz + math.sin(ang) * (PORT_R + 0.052)
            bm_cyl(bm, (inner_x - side * 0.035, dy, dz), 0.017, 0.075, axis='X', segments=14)
            bm_box(bm, (inner_x - side * 0.075, dy, dz), (0.03, 0.11, 0.022),
                   rot=(ang, 0.0, 0.0))
        bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
        obj_from_bm("PortholeDogs_%d" % i, bm, M_BRASS, smooth_quads=True)


build_portholes()


def build_deck_hatch():
    bm = bmesh.new()
    outer, inner, zc, h = 0.66, 0.50, 1.955, 0.20
    t = (outer - inner) * 0.5
    for sx in (-1.0, 1.0):
        bm_box(bm, (sx * (inner + t) * 0.5, HATCH_Y, zc), (t, outer, h))
    for sy in (-1.0, 1.0):
        bm_box(bm, (0.0, HATCH_Y + sy * (inner + t) * 0.5, zc), (inner, t, h))
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    obj_from_bm("HatchFrame", bm, M_WOOD)
    box("HatchGlass", (0.0, HATCH_Y, 2.030), (0.52, 0.52, 0.016), M_GLASS)
    for sy in (-0.20, 0.20):
        cylinder("HatchDog", (0.0, HATCH_Y + sy, 1.905), 0.016, 0.06, M_BRASS,
                 axis='Z', segments=14)


build_deck_hatch()


# --------------------------------------------- forward bulkhead furniture
def build_fwd_bulkhead_details():
    yf = -HALF_LEN + 0.012
    box("FwdLockerDoor", (0.52, yf + 0.012, 0.95), (0.62, 0.026, 0.72), M_WOOD_L,
        bevel=0.008)
    box("FwdLockerFrame", (0.52, yf, 0.95), (0.70, 0.02, 0.80), M_WOOD)
    cylinder("FwdLockerKnob", (0.76, yf + 0.032, 0.95), 0.018, 0.04, M_BRASS,
             axis='Y', segments=14)
    for i, dx in enumerate((0.28, 0.76)):
        cylinder("Instrument%d" % i, (dx, yf + 0.020, 1.62), 0.075, 0.040,
                 M_BRASS, axis='Y', segments=32)
        cylinder("InstrumentFace%d" % i, (dx, yf + 0.042, 1.62), 0.062, 0.006,
                 M_PAPER, axis='Y', segments=32)
    box("FwdTrim", (0.0, yf, 0.02), (2.0, 0.02, 0.06), M_WOOD)


build_fwd_bulkhead_details()


# ------------------------------------------------------------------ lamps
def build_lamps():
    lamp_ys = (-0.60, 1.05)
    for i, ly in enumerate(lamp_ys):
        base_z = ARCH_Z + ARCH_B - 0.01
        cylinder("LampBase%d" % i, (0.0, ly, base_z - 0.020), 0.075, 0.045,
                 M_BRASS, segments=28)
        bm = bmesh.new()
        bm_sphere(bm, (0.0, ly, base_z - 0.055), 0.085, u=28, v=14)
        bmesh.ops.scale(bm, vec=(1.0, 1.0, 0.75),
                        verts=bm.verts, space=Matrix.Translation((0.0, -ly, -(base_z - 0.055))))
        bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
        dome = obj_from_bm("LampDome%d" % i, bm, M_LAMP)
        for p in dome.data.polygons:
            p.use_smooth = True

        ld = bpy.data.lights.new("CabinLamp%d" % i, 'POINT')
        ld.energy = 22.0
        ld.color = (1.0, 0.80, 0.55)
        ld.shadow_soft_size = 0.07
        lo = bpy.data.objects.new("CabinLamp%d" % i, ld)
        lo.location = (0.0, ly, base_z - 0.075)
        CABIN.objects.link(lo)

    # brass reading light over the lower berth
    rx = -(side_x(1.00) - 0.05)
    cylinder("ReadingLampArm", (rx + 0.07, -1.55, 1.00), 0.014, 0.16, M_BRASS,
             axis='X', segments=12)
    bm = bmesh.new()
    bm_cyl(bm, (rx + 0.17, -1.55, 0.985), 0.055, 0.075, axis='Z', segments=20)
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    shade = obj_from_bm("ReadingLampShade", bm, M_BRASS, smooth_quads=True)
    shade.rotation_euler = (math.radians(22.0), 0.0, 0.0)
    rl = bpy.data.lights.new("ReadingLight", 'SPOT')
    rl.energy = 14.0
    rl.color = (1.0, 0.86, 0.66)
    rl.spot_size = math.radians(70.0)
    rl.spot_blend = 0.5
    rl.shadow_soft_size = 0.03
    ro = bpy.data.objects.new("ReadingLight", rl)
    ro.location = (rx + 0.17, -1.55, 0.945)
    ro.rotation_euler = (math.radians(18.0), 0.0, 0.0)
    CABIN.objects.link(ro)


build_lamps()


# ----------------------------------------------------------- daylight rig
def build_daylight():
    for i, (side, py, pz) in enumerate(PORTS):
        ld = bpy.data.lights.new("PortDaylight%d" % i, 'AREA')
        ld.shape = 'DISK'
        ld.size = 0.45
        ld.energy = 90.0
        ld.color = (0.72, 0.84, 1.0)
        lo = bpy.data.objects.new("PortDaylight%d" % i, ld)
        lo.location = (side * 1.75, py, pz)
        lo.rotation_euler = (0.0, side * math.pi * 0.5, 0.0)
        CABIN.objects.link(lo)

    hd = bpy.data.lights.new("HatchDaylight", 'AREA')
    hd.shape = 'RECTANGLE'
    hd.size, hd.size_y = 0.8, 0.8
    hd.energy = 260.0
    hd.color = (0.85, 0.90, 1.0)
    ho = bpy.data.objects.new("HatchDaylight", hd)
    ho.location = (0.0, HATCH_Y, 2.85)
    ho.rotation_euler = (math.radians(8.0), 0.0, 0.0)
    CABIN.objects.link(ho)

    cd = bpy.data.lights.new("CompanionwayDaylight", 'AREA')
    cd.shape = 'RECTANGLE'
    cd.size, cd.size_y = 0.8, 1.6
    cd.energy = 220.0
    cd.color = (0.80, 0.88, 1.0)
    co = bpy.data.objects.new("CompanionwayDaylight", cd)
    co.location = (0.0, HALF_LEN + 0.55, 1.05)
    co.rotation_euler = (math.radians(90.0), 0.0, math.radians(180.0))
    CABIN.objects.link(co)

    fill = bpy.data.lights.new("InteriorFill", 'AREA')
    fill.shape = 'RECTANGLE'
    fill.size, fill.size_y = 1.4, 1.4
    fill.energy = 18.0
    fill.color = (1.0, 0.94, 0.86)
    fo = bpy.data.objects.new("InteriorFill", fill)
    fo.location = (0.0, 1.85, 1.55)
    fo.rotation_euler = (math.radians(105.0), 0.0, 0.0)
    CABIN.objects.link(fo)


build_daylight()

world = bpy.data.worlds.new("CabinWorld")
world.use_nodes = True
bg = world.node_tree.nodes["Background"]
bg.inputs[0].default_value = (0.055, 0.075, 0.095, 1.0)
bg.inputs[1].default_value = 1.0
bpy.context.scene.world = world


# ---------------------------------------------------------------- camera
def build_camera():
    cam_data = bpy.data.cameras.new("CabinCam")
    cam_data.lens = 18.0
    cam_data.sensor_width = 36.0
    cam_data.clip_start = 0.02
    cam_data.clip_end = 100.0
    cam_data.dof.use_dof = True
    cam_data.dof.aperture_fstop = 4.0
    cam = bpy.data.objects.new("CabinCam", cam_data)
    loc = Vector((0.10, 1.86, 1.42))
    target = Vector((-0.05, -1.10, 0.80))
    direction = target - loc
    cam.location = loc
    cam.rotation_euler = direction.to_track_quat('-Z', 'Y').to_euler()
    cam_data.dof.focus_distance = direction.length
    CABIN.objects.link(cam)
    bpy.context.scene.camera = cam
    return cam


build_camera()

for ob in bpy.context.view_layer.objects:
    ob.select_set(False)

print("Boat cabin built: %d objects" % len(CABIN.objects))
