"""
claude-126 : Portable generator with tubular cage, motor housing, fuel tank
             and control panel.

Built headlessly from Blender's factory startup.  Scene construction only:
no rendering, no file output, no external assets or addons.

Axis convention
    +X  front of the machine (control panel side)
    -X  rear (finned cylinder head, wheel kit)
    -Y  left flank (recoil starter, muffler)
    +Z  up, ground plane at z = 0
"""

import math

import bpy
import bmesh
from mathutils import Vector, Matrix

rad = math.radians

COLL = None      # collection everything is linked into
PARTS = []       # generator parts, parented to a root empty at the end


# ---------------------------------------------------------------------------
# scene / material helpers
# ---------------------------------------------------------------------------
def reset_scene():
    global COLL
    bpy.ops.wm.read_factory_settings(use_empty=True)

    scene = bpy.context.scene
    scene.unit_settings.system = 'METRIC'
    scene.unit_settings.length_unit = 'METERS'
    try:
        scene.render.engine = 'BLENDER_EEVEE_NEXT'
    except TypeError:
        pass
    scene.render.resolution_x = 1800
    scene.render.resolution_y = 1200

    COLL = bpy.data.collections.new("Generator")
    scene.collection.children.link(COLL)


def make_mat(name, color, metallic=0.0, roughness=0.5,
             emission=None, emission_strength=0.0, coat=0.0):
    mat = bpy.data.materials.new(name)
    mat.use_nodes = True
    bsdf = mat.node_tree.nodes.get("Principled BSDF")

    def put(key, value):
        if bsdf is not None and key in bsdf.inputs:
            bsdf.inputs[key].default_value = value

    put("Base Color", (color[0], color[1], color[2], 1.0))
    put("Metallic", metallic)
    put("Roughness", roughness)
    put("Coat Weight", coat)
    put("Coat Roughness", 0.06)
    if emission is not None:
        put("Emission Color", (emission[0], emission[1], emission[2], 1.0))
        put("Emission Strength", emission_strength)

    mat.diffuse_color = (color[0], color[1], color[2], 1.0)
    mat.roughness = roughness
    mat.metallic = metallic
    return mat


# ---------------------------------------------------------------------------
# geometry helpers
# ---------------------------------------------------------------------------
def finish(name, bm, mat=None, loc=(0.0, 0.0, 0.0), rot=(0.0, 0.0, 0.0),
           smooth=False, smooth_test=None):
    """Turn a bmesh into a linked object.  smooth_test(face) -> bool wins."""
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces[:])

    if smooth_test is not None:
        for f in bm.faces:
            f.smooth = bool(smooth_test(f))
    elif smooth:
        for f in bm.faces:
            f.smooth = True

    me = bpy.data.meshes.new(name)
    bm.to_mesh(me)
    bm.free()

    obj = bpy.data.objects.new(name, me)
    obj.location = loc
    obj.rotation_euler = rot
    if mat is not None:
        me.materials.append(mat)

    COLL.objects.link(obj)
    PARTS.append(obj)
    return obj


def _round_test(f):
    """Smooth only faces that are not axis aligned (bevel rounds of a box)."""
    n = f.normal
    return max(abs(n.x), abs(n.y), abs(n.z)) < 0.995


def _side_test(f):
    """Smooth only the barrel of a Z-aligned cylinder, never the caps."""
    return abs(f.normal.z) < 0.86


def add_box(name, size, loc, rot=(0.0, 0.0, 0.0), mat=None,
            bevel=0.0, bseg=2, smooth=False):
    bm = bmesh.new()
    bmesh.ops.create_cube(bm, size=1.0)
    for v in bm.verts:
        v.co.x *= size[0]
        v.co.y *= size[1]
        v.co.z *= size[2]
    if bevel > 0.0:
        bmesh.ops.bevel(bm, geom=list(bm.verts) + list(bm.edges),
                        offset=bevel, segments=bseg, affect='EDGES',
                        profile=0.5, clamp_overlap=True)
    test = _round_test if (smooth and bevel > 0.0) else None
    return finish(name, bm, mat=mat, loc=loc, rot=rot, smooth_test=test)


def add_cylinder(name, radius, depth, loc, rot=(0.0, 0.0, 0.0), verts=32,
                 mat=None, bevel=0.0, bseg=2, caps=True, smooth=True):
    bm = bmesh.new()
    bmesh.ops.create_cone(bm, cap_ends=caps, cap_tris=False, segments=verts,
                          radius1=radius, radius2=radius, depth=depth)
    if bevel > 0.0:
        bmesh.ops.bevel(bm, geom=list(bm.verts) + list(bm.edges),
                        offset=bevel, segments=bseg, affect='EDGES',
                        profile=0.5, clamp_overlap=True)
    return finish(name, bm, mat=mat, loc=loc, rot=rot,
                  smooth_test=_side_test if smooth else None)


def add_cone(name, r1, r2, depth, loc, rot=(0.0, 0.0, 0.0), verts=24, mat=None):
    bm = bmesh.new()
    bmesh.ops.create_cone(bm, cap_ends=True, cap_tris=False, segments=verts,
                          radius1=r1, radius2=r2, depth=depth)
    return finish(name, bm, mat=mat, loc=loc, rot=rot, smooth_test=_side_test)


def add_sphere(name, radius, loc, mat=None, useg=24, vseg=12, scale=(1, 1, 1)):
    bm = bmesh.new()
    bmesh.ops.create_uvsphere(bm, u_segments=useg, v_segments=vseg,
                              radius=radius)
    for v in bm.verts:
        v.co.x *= scale[0]
        v.co.y *= scale[1]
        v.co.z *= scale[2]
    return finish(name, bm, mat=mat, loc=loc, smooth=True)


def add_torus(name, major_r, minor_r, loc, rot=(0.0, 0.0, 0.0),
              major_seg=32, minor_seg=10, mat=None):
    bm = bmesh.new()
    rings = []
    for i in range(major_seg):
        a = 2.0 * math.pi * i / major_seg
        ca, sa = math.cos(a), math.sin(a)
        ring = []
        for j in range(minor_seg):
            b = 2.0 * math.pi * j / minor_seg
            r = major_r + minor_r * math.cos(b)
            ring.append(bm.verts.new((r * ca, r * sa, minor_r * math.sin(b))))
        rings.append(ring)
    for i in range(major_seg):
        r1 = rings[i]
        r2 = rings[(i + 1) % major_seg]
        for j in range(minor_seg):
            k = (j + 1) % minor_seg
            bm.faces.new((r1[j], r1[k], r2[k], r2[j]))
    return finish(name, bm, mat=mat, loc=loc, rot=rot, smooth=True)


def add_arc_shell(name, radius, thickness, length, a0, a1, segs=20,
                  loc=(0.0, 0.0, 0.0), rot=(0.0, 0.0, 0.0), mat=None):
    """Curved sheet-metal shell.  Axis along local Z, profile swept in XY."""
    bm = bmesh.new()
    hz = length * 0.5
    ib, ob, it, ot = [], [], [], []
    for i in range(segs + 1):
        a = a0 + (a1 - a0) * i / segs
        ca, sa = math.cos(a), math.sin(a)
        ri, ro = radius, radius + thickness
        ib.append(bm.verts.new((ri * ca, ri * sa, -hz)))
        ob.append(bm.verts.new((ro * ca, ro * sa, -hz)))
        it.append(bm.verts.new((ri * ca, ri * sa, hz)))
        ot.append(bm.verts.new((ro * ca, ro * sa, hz)))

    for i in range(segs):
        bm.faces.new((ib[i], ib[i + 1], it[i + 1], it[i]))          # inner
        bm.faces.new((ob[i + 1], ob[i], ot[i], ot[i + 1]))          # outer
        bm.faces.new((ib[i], ob[i], ob[i + 1], ib[i + 1]))          # -Z rim
        bm.faces.new((it[i + 1], ot[i + 1], ot[i], it[i]))          # +Z rim
    bm.faces.new((ib[0], it[0], ot[0], ob[0]))                      # end caps
    bm.faces.new((ob[segs], ot[segs], it[segs], ib[segs]))

    def test(f):
        return abs(f.normal.z) < 0.86

    return finish(name, bm, mat=mat, loc=loc, rot=rot, smooth_test=test)


def add_tube_between(name, p1, p2, radius, mat=None, verts=16, pad=0.0):
    """Capped cylinder spanning two points (pad extends both ends)."""
    a, b = Vector(p1), Vector(p2)
    d = b - a
    length = d.length + 2.0 * pad
    if length < 1e-6:
        return None
    quat = d.to_track_quat('Z', 'Y')
    return add_cylinder(name, radius, length, tuple((a + b) * 0.5),
                        rot=tuple(quat.to_euler()), verts=verts, mat=mat)


# ---------------------------------------------------------------------------
# polyline filleting + curve based tubing (used for the roll cage)
# ---------------------------------------------------------------------------
def fillet_polyline(points, radius, segments=6, closed=False):
    """Replace sharp corners of a 3D polyline with tangent circular arcs."""
    pts = [Vector(p) for p in points]
    n = len(pts)
    out = []

    if closed:
        indices = range(n)
    else:
        indices = range(1, n - 1)
        out.append(pts[0].copy())

    for i in indices:
        p = pts[i]
        a = pts[(i - 1) % n]
        b = pts[(i + 1) % n]
        v1, v2 = a - p, b - p
        l1, l2 = v1.length, v2.length
        if l1 < 1e-7 or l2 < 1e-7:
            out.append(p.copy())
            continue

        d1, d2 = v1 / l1, v2 / l2
        theta = d1.angle(d2)
        if theta < 1e-4 or abs(theta - math.pi) < 1e-4:
            out.append(p.copy())
            continue

        half = theta * 0.5
        t = min(radius / math.tan(half), l1 * 0.48, l2 * 0.48)
        r_eff = t * math.tan(half)
        bis = (d1 + d2)
        if bis.length < 1e-7:
            out.append(p.copy())
            continue
        bis.normalize()

        center = p + bis * (r_eff / math.sin(half))
        v1c = (p + d1 * t) - center
        v2c = (p + d2 * t) - center
        axis = v1c.cross(v2c)
        if axis.length < 1e-9:
            out.append(p.copy())
            continue
        axis.normalize()
        total = v1c.angle(v2c)

        for k in range(segments + 1):
            rot = Matrix.Rotation(total * k / segments, 3, axis)
            out.append(center + (rot @ v1c))

    if not closed:
        out.append(pts[-1].copy())
    return out


def add_tube_curve(name, points, radius, mat=None, closed=False,
                   fillet=0.0, fillet_segs=6, bevel_res=6):
    pts = points
    if fillet > 0.0:
        pts = fillet_polyline(points, fillet, segments=fillet_segs,
                              closed=closed)

    cu = bpy.data.curves.new(name, 'CURVE')
    cu.dimensions = '3D'
    cu.resolution_u = 1
    cu.bevel_depth = radius
    cu.bevel_resolution = bevel_res
    cu.use_fill_caps = True

    sp = cu.splines.new('POLY')
    sp.points.add(len(pts) - 1)
    for i, p in enumerate(pts):
        sp.points[i].co = (p[0], p[1], p[2], 1.0)
    sp.use_cyclic_u = closed

    if mat is not None:
        cu.materials.append(mat)

    obj = bpy.data.objects.new(name, cu)
    COLL.objects.link(obj)
    PARTS.append(obj)
    return obj


# ---------------------------------------------------------------------------
# materials
# ---------------------------------------------------------------------------
class M:
    pass


def build_materials():
    M.frame = make_mat("Frame_Steel", (0.055, 0.058, 0.062),
                       metallic=0.85, roughness=0.38, coat=0.15)
    M.paint = make_mat("Tank_Paint_Red", (0.52, 0.045, 0.035),
                       metallic=0.25, roughness=0.22, coat=0.4)
    M.paint_dark = make_mat("Housing_Paint", (0.09, 0.10, 0.11),
                            metallic=0.3, roughness=0.33, coat=0.25)
    M.alu = make_mat("Cast_Aluminium", (0.60, 0.61, 0.63),
                     metallic=0.9, roughness=0.47)
    M.alu_dark = make_mat("Cast_Aluminium_Dark", (0.40, 0.41, 0.43),
                          metallic=0.85, roughness=0.58)
    M.steel = make_mat("Muffler_Steel", (0.30, 0.29, 0.28),
                       metallic=0.8, roughness=0.55)
    M.chrome = make_mat("Chrome", (0.88, 0.89, 0.91),
                        metallic=1.0, roughness=0.12)
    M.plastic = make_mat("Black_Plastic", (0.030, 0.031, 0.033),
                         metallic=0.0, roughness=0.40, coat=0.2)
    M.rubber = make_mat("Rubber", (0.017, 0.017, 0.018),
                        metallic=0.0, roughness=0.82)
    M.panel = make_mat("Panel_Face", (0.115, 0.120, 0.128),
                       metallic=0.35, roughness=0.42)
    M.socket = make_mat("Socket_Body", (0.045, 0.046, 0.048),
                        metallic=0.0, roughness=0.34, coat=0.3)
    M.slot = make_mat("Socket_Slot", (0.006, 0.006, 0.007),
                      metallic=0.0, roughness=0.9)
    M.brass = make_mat("Brass", (0.62, 0.45, 0.16),
                       metallic=1.0, roughness=0.30)
    M.red = make_mat("Warn_Red", (0.58, 0.045, 0.030),
                     metallic=0.0, roughness=0.35, coat=0.3)
    M.green = make_mat("Ground_Green", (0.06, 0.30, 0.09),
                       metallic=0.0, roughness=0.40)
    M.yellow = make_mat("Oil_Yellow", (0.66, 0.48, 0.03),
                        metallic=0.0, roughness=0.38, coat=0.2)
    M.glass = make_mat("Gauge_Glass", (0.02, 0.02, 0.025),
                       metallic=0.0, roughness=0.08, coat=0.6)
    M.display = make_mat("LCD", (0.02, 0.05, 0.06), metallic=0.0,
                         roughness=0.25, emission=(0.15, 0.75, 0.65),
                         emission_strength=2.2)
    M.ground = make_mat("Studio_Floor", (0.19, 0.19, 0.20),
                        metallic=0.0, roughness=0.62)
    M.label = make_mat("Label_Plate", (0.72, 0.72, 0.70),
                       metallic=0.2, roughness=0.5)


# ---------------------------------------------------------------------------
# tubular cage + base
# ---------------------------------------------------------------------------
CAGE_X = 0.52          # half length of the cage
CAGE_Y = 0.30          # half width
CAGE_Z0 = 0.045        # bottom rail height
CAGE_Z1 = 0.775        # top rail height
TUBE_R = 0.019


def build_cage():
    # two closed side loops in the XZ plane, corners filleted
    for side, y in (("L", -CAGE_Y), ("R", CAGE_Y)):
        loop = [(-CAGE_X, y, CAGE_Z0),
                (CAGE_X, y, CAGE_Z0),
                (CAGE_X, y, CAGE_Z1),
                (-CAGE_X, y, CAGE_Z1)]
        add_tube_curve("Cage_SideLoop_" + side, loop, TUBE_R, mat=M.frame,
                       closed=True, fillet=0.105, fillet_segs=7)

    # cross members top and bottom
    for x in (-0.42, 0.0, 0.42):
        add_tube_between("Cage_CrossTop_%+0.2f" % x,
                         (x, -CAGE_Y, CAGE_Z1), (x, CAGE_Y, CAGE_Z1),
                         TUBE_R, mat=M.frame)
        add_tube_between("Cage_CrossBottom_%+0.2f" % x,
                         (x, -CAGE_Y, CAGE_Z0), (x, CAGE_Y, CAGE_Z0),
                         TUBE_R, mat=M.frame)

    # vertical side struts
    for y in (-CAGE_Y, CAGE_Y):
        for x in (-0.19, 0.19):
            add_tube_between("Cage_Strut",
                             (x, y, CAGE_Z0), (x, y, CAGE_Z1),
                             0.0155, mat=M.frame)

    # diagonal rear braces
    for y in (-CAGE_Y, CAGE_Y):
        add_tube_between("Cage_Brace",
                         (-0.42, y, CAGE_Z0 + 0.02), (-0.19, y, 0.32),
                         0.014, mat=M.frame)

    # moulded carry grips on the top side rails
    for y in (-CAGE_Y, CAGE_Y):
        add_cylinder("Cage_Grip", 0.031, 0.30, (0.0, y, CAGE_Z1),
                     rot=(0.0, rad(90.0), 0.0), verts=20, mat=M.rubber,
                     bevel=0.008, bseg=2)
        for gx in (-0.13, -0.065, 0.0, 0.065, 0.13):
            add_torus("Cage_GripRib", 0.032, 0.004, (gx, y, CAGE_Z1),
                      rot=(0.0, rad(90.0), 0.0), major_seg=18, minor_seg=6,
                      mat=M.rubber)

    # base pan the engine sits on
    add_box("Base_Pan", (0.88, 0.52, 0.030), (-0.01, 0.0, 0.075),
            mat=M.paint_dark, bevel=0.010, bseg=2, smooth=True)
    for x in (-0.36, 0.30):
        add_box("Base_Rib", (0.06, 0.50, 0.024), (x, 0.0, 0.052),
                mat=M.paint_dark, bevel=0.006, smooth=True)

    # rubber anti-vibration feet
    for x in (0.42, -0.14):
        for y in (-CAGE_Y, CAGE_Y):
            add_cylinder("Foot", 0.046, 0.048, (x, y, 0.024), verts=20,
                         mat=M.rubber, bevel=0.010, bseg=2)
            add_cylinder("Foot_Bolt", 0.011, 0.030, (x, y, 0.052), verts=12,
                         mat=M.chrome)

    # engine mounting blocks
    for x in (-0.16, 0.06):
        for y in (-0.15, 0.15):
            add_cylinder("Engine_Mount", 0.026, 0.028, (x, y, 0.104),
                         verts=14, mat=M.rubber, bevel=0.005)


# ---------------------------------------------------------------------------
# engine / motor housing
# ---------------------------------------------------------------------------
def build_engine():
    # crankcase
    add_box("Crankcase", (0.34, 0.36, 0.26), (-0.06, 0.0, 0.245),
            mat=M.alu, bevel=0.030, bseg=3, smooth=True)
    add_box("Crankcase_Sump", (0.30, 0.32, 0.05), (-0.06, 0.0, 0.135),
            mat=M.alu_dark, bevel=0.014, bseg=2, smooth=True)

    # finned cylinder head pointing rearwards
    for i in range(7):
        x = -0.250 - i * 0.028
        w = 0.275 - i * 0.006
        h = 0.235 - i * 0.008
        add_box("Head_Fin_%d" % i, (0.014, w, h), (x, 0.0, 0.290),
                mat=M.alu_dark, bevel=0.004, smooth=True)
    add_box("Head_Barrel", (0.20, 0.20, 0.17), (-0.32, 0.0, 0.290),
            mat=M.alu, bevel=0.020, bseg=2, smooth=True)
    add_box("Head_Cover", (0.05, 0.21, 0.19), (-0.445, 0.0, 0.290),
            mat=M.alu, bevel=0.016, bseg=2, smooth=True)
    for y in (-0.075, 0.075):
        for z in (0.215, 0.365):
            add_cylinder("Head_Bolt", 0.010, 0.016, (-0.470, y, z),
                         rot=(0.0, rad(90.0), 0.0), verts=6, mat=M.chrome)

    # spark plug on top of the head, with lead running back to the coil
    add_cylinder("Plug_Base", 0.021, 0.030, (-0.395, 0.0, 0.390), verts=16,
                 mat=M.alu_dark)
    add_cylinder("Plug_Hex", 0.019, 0.020, (-0.395, 0.0, 0.412), verts=6,
                 mat=M.chrome)
    add_cylinder("Plug_Cap", 0.026, 0.055, (-0.395, 0.0, 0.450), verts=18,
                 mat=M.plastic, bevel=0.007, bseg=2)
    add_tube_curve("Plug_Lead",
                   [(-0.395, 0.0, 0.476), (-0.350, 0.03, 0.470),
                    (-0.290, 0.07, 0.430), (-0.230, 0.10, 0.400),
                    (-0.180, 0.115, 0.370)],
                   0.0075, mat=M.plastic, fillet=0.03, bevel_res=4)

    # recoil starter on the left flank
    add_cylinder("Recoil_Housing", 0.115, 0.050, (0.0, -0.205, 0.245),
                 rot=(rad(90.0), 0.0, 0.0), verts=32, mat=M.plastic,
                 bevel=0.010, bseg=2)
    add_torus("Recoil_Rim", 0.108, 0.010, (0.0, -0.228, 0.245),
              rot=(rad(90.0), 0.0, 0.0), major_seg=32, minor_seg=8,
              mat=M.plastic)
    add_cylinder("Recoil_Hub", 0.030, 0.020, (0.0, -0.238, 0.245),
                 rot=(rad(90.0), 0.0, 0.0), verts=18, mat=M.alu_dark)
    add_cylinder("Recoil_Rope", 0.0055, 0.075, (0.0, -0.272, 0.245),
                 rot=(rad(90.0), 0.0, 0.0), verts=8, mat=M.label)
    add_cylinder("Recoil_Handle", 0.019, 0.115, (0.0, -0.317, 0.245),
                 rot=(0.0, rad(90.0), 0.0), verts=18, mat=M.plastic,
                 bevel=0.007, bseg=2)
    for hx in (-0.045, 0.045):
        add_sphere("Recoil_HandleEnd", 0.020, (hx, -0.317, 0.245),
                   mat=M.plastic, useg=16, vseg=8)

    # air cleaner + carburettor on the right flank
    add_box("AirBox", (0.20, 0.15, 0.15), (-0.255, 0.225, 0.430),
            mat=M.plastic, bevel=0.018, bseg=2, smooth=True)
    add_cylinder("AirBox_Nut", 0.020, 0.030, (-0.255, 0.305, 0.430),
                 rot=(rad(90.0), 0.0, 0.0), verts=16, mat=M.plastic,
                 bevel=0.006)
    add_box("AirBox_Snorkel", (0.055, 0.05, 0.05), (-0.170, 0.225, 0.470),
            mat=M.plastic, bevel=0.010, smooth=True)
    add_box("Carburettor", (0.085, 0.09, 0.085), (-0.215, 0.185, 0.328),
            mat=M.alu, bevel=0.012, bseg=2, smooth=True)
    add_cylinder("Carb_Bowl", 0.032, 0.030, (-0.215, 0.185, 0.278),
                 verts=18, mat=M.alu_dark, bevel=0.008)
    add_box("Choke_Lever", (0.045, 0.012, 0.018), (-0.160, 0.185, 0.360),
            rot=(0.0, 0.0, rad(-12.0)), mat=M.red, bevel=0.004, smooth=True)

    # fuel line from the tank down to the carburettor, with an inline filter
    add_tube_curve("Fuel_Line",
                   [(-0.300, 0.140, 0.505), (-0.290, 0.160, 0.470),
                    (-0.265, 0.175, 0.430), (-0.240, 0.183, 0.395),
                    (-0.228, 0.185, 0.362)],
                   0.0065, mat=M.plastic, fillet=0.02, bevel_res=4)
    add_cylinder("Fuel_Filter", 0.014, 0.045, (-0.281, 0.166, 0.452),
                 rot=(rad(-32.0), rad(18.0), 0.0), verts=14, mat=M.glass,
                 bevel=0.005)

    # oil filler / dipstick
    add_cylinder("Oil_Filler", 0.026, 0.036, (0.055, 0.186, 0.165),
                 rot=(rad(90.0), 0.0, 0.0), verts=16, mat=M.yellow,
                 bevel=0.007)

    # muffler with heat shield and exhaust tip
    add_cylinder("Muffler", 0.075, 0.30, (-0.130, -0.215, 0.445),
                 rot=(0.0, rad(90.0), 0.0), verts=28, mat=M.steel,
                 bevel=0.018, bseg=3)
    add_arc_shell("Muffler_HeatShield", 0.086, 0.006, 0.265,
                  rad(98.0), rad(262.0), segs=22,
                  loc=(-0.130, -0.215, 0.445), rot=(0.0, rad(90.0), 0.0),
                  mat=M.steel)
    for sx in (-0.235, -0.025):
        add_cylinder("Shield_Standoff", 0.008, 0.030, (sx, -0.215, 0.531),
                     verts=8, mat=M.steel)
    add_cylinder("Exhaust_Pipe", 0.030, 0.075, (-0.312, -0.215, 0.415),
                 rot=(0.0, rad(90.0), 0.0), verts=18, mat=M.steel)
    add_cylinder("Exhaust_Screen", 0.026, 0.006, (-0.348, -0.215, 0.415),
                 rot=(0.0, rad(90.0), 0.0), verts=18, mat=M.slot)
    add_tube_between("Exhaust_Header", (-0.400, -0.100, 0.330),
                     (-0.240, -0.200, 0.400), 0.020, mat=M.steel, verts=14)

    # alternator housing with cooling louvres, between engine and panel
    add_cylinder("Alternator_Housing", 0.150, 0.225, (0.220, 0.0, 0.260),
                 rot=(0.0, rad(90.0), 0.0), verts=32, mat=M.paint_dark,
                 bevel=0.014, bseg=2)
    add_torus("Alternator_Flange", 0.150, 0.012, (0.110, 0.0, 0.260),
              rot=(0.0, rad(90.0), 0.0), major_seg=32, minor_seg=8,
              mat=M.paint_dark)
    for i in range(14):
        a = 2.0 * math.pi * i / 14.0
        add_box("Alternator_Louvre_%d" % i, (0.145, 0.007, 0.030),
                (0.220, 0.153 * math.cos(a), 0.260 + 0.153 * math.sin(a)),
                rot=(a, 0.0, 0.0), mat=M.paint_dark)
    add_box("Alternator_Foot", (0.14, 0.24, 0.055), (0.220, 0.0, 0.128),
            mat=M.paint_dark, bevel=0.010, smooth=True)

    # data plate on the housing flank
    add_box("Data_Plate", (0.10, 0.006, 0.055), (0.215, 0.152, 0.300),
            rot=(rad(0.0), 0.0, 0.0), mat=M.label)


# ---------------------------------------------------------------------------
# fuel tank
# ---------------------------------------------------------------------------
def build_tank():
    add_box("Fuel_Tank", (0.87, 0.51, 0.20), (-0.010, 0.0, 0.600),
            mat=M.paint, bevel=0.055, bseg=4, smooth=True)

    # seam flange around the tank shell
    add_box("Tank_Seam", (0.875, 0.515, 0.010), (-0.010, 0.0, 0.598),
            mat=M.paint, bevel=0.004, smooth=True)

    # support pads between tank and frame
    for x in (-0.36, 0.30):
        for y in (-0.20, 0.20):
            add_box("Tank_Pad", (0.07, 0.07, 0.045), (x, y, 0.484),
                    mat=M.rubber, bevel=0.008, smooth=True)

    # filler neck and cap
    add_cylinder("Filler_Neck", 0.060, 0.028, (-0.150, 0.0, 0.700),
                 verts=28, mat=M.alu_dark, bevel=0.006)
    add_cylinder("Fuel_Cap", 0.056, 0.048, (-0.150, 0.0, 0.730), verts=28,
                 mat=M.plastic, bevel=0.010, bseg=2)
    for i in range(10):
        a = 2.0 * math.pi * i / 10.0
        add_box("Cap_Rib_%d" % i, (0.012, 0.006, 0.040),
                (-0.150 + 0.053 * math.cos(a), 0.053 * math.sin(a), 0.730),
                rot=(0.0, 0.0, a), mat=M.plastic)
    add_cylinder("Cap_Vent", 0.009, 0.012, (-0.150, 0.0, 0.757), verts=10,
                 mat=M.chrome)

    # fuel gauge
    add_cylinder("Gauge_Bezel", 0.042, 0.014, (0.140, 0.0, 0.702),
                 verts=26, mat=M.chrome, bevel=0.004)
    add_cylinder("Gauge_Face", 0.035, 0.008, (0.140, 0.0, 0.708),
                 verts=26, mat=M.label)
    add_cylinder("Gauge_Glass", 0.036, 0.004, (0.140, 0.0, 0.713),
                 verts=26, mat=M.glass)
    add_box("Gauge_Needle", (0.028, 0.004, 0.003), (0.152, 0.010, 0.714),
            rot=(0.0, 0.0, rad(28.0)), mat=M.red)

    # fuel shutoff valve on the tank underside, reachable from the front
    add_cylinder("Fuel_Valve", 0.024, 0.030, (0.130, 0.230, 0.520),
                 rot=(rad(90.0), 0.0, 0.0), verts=16, mat=M.plastic,
                 bevel=0.006)
    add_box("Fuel_Valve_Lever", (0.014, 0.020, 0.055), (0.130, 0.248, 0.520),
            rot=(rad(20.0), 0.0, 0.0), mat=M.plastic, bevel=0.004,
            smooth=True)


# ---------------------------------------------------------------------------
# control panel
# ---------------------------------------------------------------------------
PX = 0.400        # panel plate centre in X
FX = PX + 0.014   # panel face plane


def duplex_outlet(cy, cz, tag):
    add_box("Outlet_Plate_" + tag, (0.014, 0.095, 0.140), (FX + 0.006, cy, cz),
            mat=M.socket, bevel=0.008, bseg=2, smooth=True)
    for dz in (-0.034, 0.034):
        z = cz + dz
        add_cylinder("Outlet_Recess_" + tag, 0.029, 0.012,
                     (FX + 0.014, cy, z), rot=(0.0, rad(90.0), 0.0),
                     verts=22, mat=M.slot)
        for dy in (-0.013, 0.013):
            add_box("Outlet_Slot_" + tag, (0.016, 0.005, 0.017),
                    (FX + 0.017, cy + dy, z + 0.005), mat=M.slot)
        add_cylinder("Outlet_Gnd_" + tag, 0.006, 0.016,
                     (FX + 0.017, cy, z - 0.016), rot=(0.0, rad(90.0), 0.0),
                     verts=10, mat=M.slot)
    add_cylinder("Outlet_Screw_" + tag, 0.007, 0.014, (FX + 0.014, cy, cz),
                 rot=(0.0, rad(90.0), 0.0), verts=8, mat=M.chrome)


def twistlock_outlet(cy, cz):
    add_cylinder("Twist_Body", 0.050, 0.018, (FX + 0.008, cy, cz),
                 rot=(0.0, rad(90.0), 0.0), verts=28, mat=M.socket,
                 bevel=0.005)
    add_torus("Twist_Ring", 0.048, 0.006, (FX + 0.017, cy, cz),
              rot=(0.0, rad(90.0), 0.0), major_seg=28, minor_seg=8,
              mat=M.chrome)
    add_cylinder("Twist_Face", 0.042, 0.008, (FX + 0.019, cy, cz),
                 rot=(0.0, rad(90.0), 0.0), verts=28, mat=M.slot)
    for i in range(4):
        a = rad(45.0 + i * 90.0)
        add_box("Twist_Slot_%d" % i, (0.012, 0.007, 0.020),
                (FX + 0.022, cy + 0.024 * math.cos(a),
                 cz + 0.024 * math.sin(a)),
                rot=(a, 0.0, 0.0), mat=M.slot)
    add_box("Twist_Cover_Hinge", (0.010, 0.040, 0.014),
            (FX + 0.020, cy, cz + 0.058), mat=M.socket, bevel=0.004,
            smooth=True)


def breaker(cy, cz, tag):
    add_box("Breaker_Body_" + tag, (0.014, 0.048, 0.070),
            (FX + 0.006, cy, cz), mat=M.socket, bevel=0.005, smooth=True)
    add_box("Breaker_Lever_" + tag, (0.020, 0.024, 0.030),
            (FX + 0.020, cy, cz + 0.014), rot=(rad(-14.0), 0.0, 0.0),
            mat=M.red, bevel=0.004, smooth=True)


def build_panel():
    # recessed panel box and face plate
    add_box("Panel_Box", (0.030, 0.460, 0.320), (PX - 0.020, 0.0, 0.340),
            mat=M.paint_dark, bevel=0.012, bseg=2, smooth=True)
    add_box("Panel_Face", (0.026, 0.430, 0.295), (PX, 0.0, 0.340),
            mat=M.panel, bevel=0.008, bseg=2, smooth=True)
    for y in (-0.198, 0.198):
        for z in (0.212, 0.468):
            add_cylinder("Panel_Screw", 0.008, 0.014, (FX + 0.002, y, z),
                         rot=(0.0, rad(90.0), 0.0), verts=10, mat=M.chrome)

    # panel mounting struts back to the alternator housing
    for y in (-0.170, 0.170):
        add_box("Panel_Strut", (0.075, 0.030, 0.030), (PX - 0.075, y, 0.190),
                mat=M.paint_dark, bevel=0.006, smooth=True)

    # top row: two 120 V duplex outlets and a 240 V twist-lock
    duplex_outlet(-0.140, 0.375, "A")
    duplex_outlet(-0.005, 0.375, "B")
    twistlock_outlet(0.140, 0.370)

    # bottom row: breakers, hour meter, engine switch, ground lug
    breaker(-0.168, 0.248, "A")
    breaker(-0.098, 0.248, "B")

    add_box("Meter_Bezel", (0.014, 0.120, 0.055), (FX + 0.006, 0.010, 0.248),
            mat=M.socket, bevel=0.006, smooth=True)
    add_box("Meter_LCD", (0.006, 0.096, 0.034), (FX + 0.015, 0.010, 0.248),
            mat=M.display)

    add_cylinder("Switch_Base", 0.034, 0.016, (FX + 0.007, 0.150, 0.245),
                 rot=(0.0, rad(90.0), 0.0), verts=22, mat=M.socket,
                 bevel=0.005)
    add_cylinder("Switch_Knob", 0.026, 0.020, (FX + 0.020, 0.150, 0.245),
                 rot=(0.0, rad(90.0), 0.0), verts=18, mat=M.plastic,
                 bevel=0.005)
    add_box("Switch_Lever", (0.022, 0.014, 0.046), (FX + 0.030, 0.150, 0.253),
            rot=(rad(18.0), 0.0, 0.0), mat=M.plastic, bevel=0.004,
            smooth=True)

    add_cylinder("Ground_Stud", 0.010, 0.038, (FX + 0.016, -0.190, 0.205),
                 rot=(0.0, rad(90.0), 0.0), verts=12, mat=M.brass)
    add_cylinder("Ground_Nut", 0.017, 0.014, (FX + 0.026, -0.190, 0.205),
                 rot=(0.0, rad(90.0), 0.0), verts=6, mat=M.green)
    add_torus("Ground_Washer", 0.020, 0.004, (FX + 0.006, -0.190, 0.205),
              rot=(0.0, rad(90.0), 0.0), major_seg=18, minor_seg=6,
              mat=M.chrome)

    # small identification / rating plates
    add_box("Rating_Plate", (0.005, 0.150, 0.030), (FX + 0.004, 0.020, 0.455),
            mat=M.label)
    add_box("Warning_Plate", (0.005, 0.080, 0.022), (FX + 0.004, -0.150, 0.455),
            mat=M.red)


# ---------------------------------------------------------------------------
# rear wheel kit
# ---------------------------------------------------------------------------
def build_wheels():
    axle_x, axle_z = -0.600, 0.120
    add_cylinder("Wheel_Axle", 0.014, 0.760, (axle_x, 0.0, axle_z),
                 rot=(rad(90.0), 0.0, 0.0), verts=14, mat=M.steel)

    for y in (-0.360, 0.360):
        add_cylinder("Tyre", 0.100, 0.062, (axle_x, y, axle_z),
                     rot=(rad(90.0), 0.0, 0.0), verts=32, mat=M.rubber,
                     bevel=0.016, bseg=3)
        add_torus("Tyre_Tread", 0.093, 0.014, (axle_x, y, axle_z),
                  rot=(rad(90.0), 0.0, 0.0), major_seg=32, minor_seg=8,
                  mat=M.rubber)
        add_cylinder("Wheel_Hub", 0.046, 0.058, (axle_x, y, axle_z),
                     rot=(rad(90.0), 0.0, 0.0), verts=24, mat=M.paint_dark,
                     bevel=0.008)
        add_cylinder("Wheel_Cap", 0.020, 0.024,
                     (axle_x, y + (0.040 if y > 0 else -0.040), axle_z),
                     rot=(rad(90.0), 0.0, 0.0), verts=14, mat=M.chrome)

        # bracket tying the axle back to the bottom cage rail
        sgn = 1.0 if y > 0 else -1.0
        add_box("Wheel_Bracket", (0.140, 0.028, 0.055),
                (-0.560, 0.320 * sgn, 0.098), rot=(0.0, rad(14.0), 0.0),
                mat=M.paint_dark, bevel=0.008, smooth=True)
        add_tube_between("Wheel_Stay",
                         (-0.520, 0.300 * sgn, 0.070),
                         (axle_x, 0.320 * sgn, axle_z),
                         0.013, mat=M.frame, verts=12)


# ---------------------------------------------------------------------------
# environment: floor, lights, camera
# ---------------------------------------------------------------------------
def build_world_and_floor():
    world = bpy.data.worlds.new("GenWorld")
    world.use_nodes = True
    bg = world.node_tree.nodes.get("Background")
    if bg is not None:
        bg.inputs["Color"].default_value = (0.045, 0.050, 0.058, 1.0)
        bg.inputs["Strength"].default_value = 1.0
    bpy.context.scene.world = world

    bm = bmesh.new()
    bmesh.ops.create_grid(bm, x_segments=1, y_segments=1, size=6.0)
    me = bpy.data.meshes.new("Floor")
    bm.to_mesh(me)
    bm.free()
    floor = bpy.data.objects.new("Floor", me)
    me.materials.append(M.ground)
    COLL.objects.link(floor)


def add_area_light(name, loc, target, energy, size, size_y=None):
    light = bpy.data.lights.new(name, 'AREA')
    light.energy = energy
    if size_y is None:
        light.shape = 'SQUARE'
        light.size = size
    else:
        light.shape = 'RECTANGLE'
        light.size = size
        light.size_y = size_y
    light.use_shadow = True

    obj = bpy.data.objects.new(name, light)
    obj.location = loc
    d = Vector(target) - Vector(loc)
    obj.rotation_euler = d.to_track_quat('-Z', 'Y').to_euler()
    COLL.objects.link(obj)
    return obj


def build_lights():
    aim = (0.0, 0.0, 0.40)
    add_area_light("Key_Light", (1.9, -2.3, 2.6), aim, 900.0, 2.2)
    add_area_light("Fill_Light", (-2.6, -1.5, 1.5), aim, 260.0, 3.0)
    add_area_light("Rim_Light", (-1.1, 2.5, 2.0), aim, 520.0, 1.6, size_y=2.6)
    add_area_light("Panel_Kicker", (1.6, 0.4, 0.9), (0.42, 0.0, 0.35),
                   60.0, 0.6)


def build_camera():
    cam_data = bpy.data.cameras.new("Camera")
    cam_data.lens = 58.0
    cam_data.clip_start = 0.02
    cam_data.clip_end = 100.0

    loc = Vector((1.85, -1.95, 1.10))
    target = Vector((0.0, 0.0, 0.42))
    cam_data.dof.use_dof = True
    cam_data.dof.focus_distance = (target - loc).length
    cam_data.dof.aperture_fstop = 4.5

    cam = bpy.data.objects.new("Camera", cam_data)
    cam.location = loc
    cam.rotation_euler = (target - loc).to_track_quat('-Z', 'Y').to_euler()
    COLL.objects.link(cam)
    bpy.context.scene.camera = cam
    return cam


# ---------------------------------------------------------------------------
# main
# ---------------------------------------------------------------------------
def main():
    reset_scene()
    build_materials()

    build_cage()
    build_engine()
    build_tank()
    build_panel()
    build_wheels()

    build_world_and_floor()
    build_lights()
    build_camera()

    # tidy hierarchy: one root empty for the whole machine
    root = bpy.data.objects.new("Generator_Root", None)
    root.empty_display_type = 'PLAIN_AXES'
    root.empty_display_size = 0.25
    COLL.objects.link(root)
    for obj in PARTS:
        obj.parent = root
        obj.matrix_parent_inverse = Matrix.Identity(4)

    print("portable generator built: %d parts" % len(PARTS))


if __name__ == "__main__":
    main()
