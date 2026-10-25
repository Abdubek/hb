"""claude-090 : Farm tractor with large lugged rear wheels and a simple engine hood.
Builds the whole scene from an empty factory startup (no render, no file output).
"""
import bpy, bmesh, math
from mathutils import Vector, Matrix, Euler


# ----------------------------------------------------------------- helpers --
def reset():
    bpy.ops.wm.read_factory_settings(use_empty=True)
    s = bpy.context.scene
    try:
        s.render.engine = 'CYCLES'
        s.cycles.samples = 128
    except Exception:
        pass
    s.render.resolution_x, s.render.resolution_y = 1700, 1200
    return s


def mat(name, base, metallic=0.0, rough=0.5, trans=0.0, emis=None, es=0.0, coat=0.0):
    m = bpy.data.materials.new(name)
    m.use_nodes = True
    i = m.node_tree.nodes["Principled BSDF"].inputs
    i["Base Color"].default_value = (base[0], base[1], base[2], 1.0)
    i["Metallic"].default_value = metallic
    i["Roughness"].default_value = rough
    if trans:
        for k in ("Transmission Weight", "Transmission"):
            if k in i:
                i[k].default_value = trans
                break
    if coat:
        for k in ("Coat Weight", "Clearcoat"):
            if k in i:
                i[k].default_value = coat
                break
    if emis:
        for k in ("Emission Color", "Emission"):
            if k in i:
                i[k].default_value = (emis[0], emis[1], emis[2], 1.0)
                break
        if "Emission Strength" in i:
            i["Emission Strength"].default_value = es
    return m


def link(ob, parent=None):
    bpy.context.scene.collection.objects.link(ob)
    if parent:
        ob.parent = parent
    return ob


def smooth(ob, angle=math.radians(35)):
    for p in ob.data.polygons:
        p.use_smooth = True
    md = ob.modifiers.new("Smooth", 'EDGE_SPLIT')
    md.split_angle = angle
    return ob


def tf(loc=(0, 0, 0), rot=(0, 0, 0)):
    return Matrix.Translation(loc) @ Euler(rot, 'XYZ').to_matrix().to_4x4()


def _bevel(bm, res, offset, segments):
    vs = res['verts']
    es, fs = set(), set()
    for v in vs:
        es.update(v.link_edges)
        fs.update(v.link_faces)
    bmesh.ops.bevel(bm, geom=list(vs) + list(es) + list(fs), offset=offset,
                    segments=segments, profile=0.5, affect='EDGES', clamp_overlap=True)


def bm_box(bm, size, matrix=None, bevel=0.0, segments=2):
    M = (matrix or Matrix.Identity(4)) @ Matrix.Diagonal(
        Vector((size[0], size[1], size[2], 1.0)))
    res = bmesh.ops.create_cube(bm, size=1.0, matrix=M)
    if bevel > 0.0:
        _bevel(bm, res, bevel, segments)
    return res


def bm_cyl(bm, r, depth, matrix=None, segs=28, r2=None, cap=True, bevel=0.0, bsegs=2):
    res = bmesh.ops.create_cone(bm, cap_ends=cap, cap_tris=False, segments=segs,
                                radius1=r, radius2=(r if r2 is None else r2),
                                depth=depth, matrix=(matrix or Matrix.Identity(4)))
    if bevel > 0.0:
        _bevel(bm, res, bevel, bsegs)
    return res


def bm_loft(bm, rings, caps=True):
    vr = [[bm.verts.new(p) for p in ring] for ring in rings]
    for a, b in zip(vr, vr[1:]):
        n = len(a)
        for i in range(n):
            j = (i + 1) % n
            bm.faces.new((a[i], a[j], b[j], b[i]))
    if caps:
        bm.faces.new(list(reversed(vr[0])))
        bm.faces.new(vr[-1])
    return vr


def bm_finish(bm, name, material=None, parent=None, smooth_angle=None):
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces[:])
    me = bpy.data.meshes.new(name)
    bm.to_mesh(me)
    bm.free()
    ob = bpy.data.objects.new(name, me)
    link(ob, parent)
    if material:
        me.materials.append(material)
    if smooth_angle is not None:
        smooth(ob, smooth_angle)
    return ob


def surface(name, nu, nv, fn, material, parent=None, thickness=0.0):
    bm = bmesh.new()
    g = [[bm.verts.new(fn(i / (nu - 1.0), j / (nv - 1.0))) for j in range(nv)]
         for i in range(nu)]
    for i in range(nu - 1):
        for j in range(nv - 1):
            bm.faces.new((g[i][j], g[i + 1][j], g[i + 1][j + 1], g[i][j + 1]))
    ob = bm_finish(bm, name, material, parent, math.radians(60))
    if thickness > 0.0:
        md = ob.modifiers.new("Solidify", 'SOLIDIFY')
        md.thickness = thickness
        md.offset = 0.0
    return ob


def round_corners(pts, radius, segs=6):
    out = [Vector(pts[0])]
    for i in range(1, len(pts) - 1):
        p0, p1, p2 = Vector(pts[i - 1]), Vector(pts[i]), Vector(pts[i + 1])
        d0, d2 = p0 - p1, p2 - p1
        l0, l2 = d0.length, d2.length
        d0.normalize()
        d2.normalize()
        ang = d0.angle(d2)
        if ang < 1e-3 or abs(ang - math.pi) < 1e-3:
            out.append(p1)
            continue
        t = min(radius / math.tan(ang * 0.5), l0 * 0.45, l2 * 0.45)
        a, b = p1 + d0 * t, p1 + d2 * t
        for s in range(segs + 1):
            u = s / float(segs)
            out.append((1 - u) ** 2 * a + 2 * (1 - u) * u * p1 + u * u * b)
    out.append(Vector(pts[-1]))
    return out


def tube(name, pts, radius, material, parent=None, fillet=0.0, res=4):
    if fillet > 0.0:
        pts = round_corners(pts, fillet)
    cu = bpy.data.curves.new(name, 'CURVE')
    cu.dimensions = '3D'
    cu.resolution_u = 3
    cu.bevel_depth = radius
    cu.bevel_resolution = res
    cu.use_fill_caps = True
    sp = cu.splines.new('POLY')
    sp.points.add(len(pts) - 1)
    for i, p in enumerate(pts):
        sp.points[i].co = (p[0], p[1], p[2], 1.0)
    ob = bpy.data.objects.new(name, cu)
    link(ob, parent)
    cu.materials.append(material)
    return ob


def add_light(name, ltype, energy, loc, target=None, size=1.0):
    d = bpy.data.lights.new(name, ltype)
    d.energy = energy
    if ltype == 'AREA':
        d.size = size
    elif ltype == 'SUN':
        d.angle = math.radians(2.0)
    ob = bpy.data.objects.new(name, d)
    link(ob)
    ob.location = loc
    if target:
        ob.rotation_euler = (Vector(target) - ob.location).to_track_quat('-Z', 'Y').to_euler()
    return ob


# ------------------------------------------------------------------- scene --
scene = reset()
w = bpy.data.worlds.new("World")
w.use_nodes = True
bg = w.node_tree.nodes["Background"]
bg.inputs[0].default_value = (0.36, 0.44, 0.56, 1.0)
bg.inputs[1].default_value = 1.1
scene.world = w

M_PAINT = mat("TractorGreen", (0.035, 0.24, 0.09), metallic=0.3, rough=0.30, coat=0.5)
M_YELLOW = mat("WheelYellow", (0.72, 0.58, 0.06), metallic=0.3, rough=0.35, coat=0.3)
M_RUBBER = mat("Rubber", (0.032, 0.032, 0.036), rough=0.88)
M_STEEL = mat("Steel", (0.42, 0.43, 0.45), metallic=1.0, rough=0.38)
M_CHROME = mat("Chrome", (0.82, 0.83, 0.85), metallic=1.0, rough=0.15)
M_BLACK = mat("BlackPlastic", (0.035, 0.035, 0.04), rough=0.55)
M_SEAT = mat("Seat", (0.10, 0.11, 0.13), rough=0.7)
M_GLASS = mat("Lens", (0.9, 0.9, 0.85), rough=0.08, emis=(1.0, 0.95, 0.8), es=3.0)
M_AMBER = mat("Beacon", (0.7, 0.32, 0.02), rough=0.2, trans=0.4, emis=(1.0, 0.4, 0.02), es=4.0)
M_GROUND = mat("Field", (0.26, 0.23, 0.16), rough=0.95)

root = bpy.data.objects.new("Tractor", None)
link(root)

RR, RW, RX, RY = 0.82, 0.44, 0.86, -0.55       # rear wheel radius/width/x/y
FR, FW, FX, FY = 0.42, 0.21, 0.62, 1.35        # front wheel

# --- chassis / transmission --------------------------------------------------
bm = bmesh.new()
bm_box(bm, (0.74, 1.55, 0.42), tf((0, -0.20, 0.80)), bevel=0.035, segments=3)
bm_box(bm, (0.58, 0.60, 0.34), tf((0, -0.86, 0.86)), bevel=0.035, segments=3)
bm_box(bm, (0.50, 1.20, 0.34), tf((0, 1.05, 0.70)), bevel=0.030, segments=3)
for sx in (1, -1):
    bm_cyl(bm, 0.13, 0.62, tf((sx * 0.55, RY, 0.86), (0, math.radians(90), 0)),
           segs=24, r2=0.10, bevel=0.02)
    bm_cyl(bm, 0.09, 0.22, tf((sx * 0.82, RY, 0.86), (0, math.radians(90), 0)), segs=20)
bm_finish(bm, "Chassis", M_PAINT, root, math.radians(35))

# --- engine hood (lofted, rounded top) --------------------------------------
def hood_ring(y, hw, zb, zt):
    return [(-hw, y, zb), (-hw, y, zt - 0.10), (-hw * 0.62, y, zt),
            (hw * 0.62, y, zt), (hw, y, zt - 0.10), (hw, y, zb)]


bm = bmesh.new()
bm_loft(bm, [hood_ring(0.55, 0.40, 0.96, 1.44),
             hood_ring(1.20, 0.385, 0.94, 1.42),
             hood_ring(1.62, 0.335, 0.92, 1.30),
             hood_ring(1.78, 0.315, 0.92, 1.24)])
bmesh.ops.recalc_face_normals(bm, faces=bm.faces[:])
bmesh.ops.bevel(bm, geom=list(bm.verts) + list(bm.edges) + list(bm.faces),
                offset=0.022, segments=2, profile=0.5, affect='EDGES', clamp_overlap=True)
bm_finish(bm, "Hood", M_PAINT, root, math.radians(32))

# hood side louvres and seam
bm = bmesh.new()
for sx in (1, -1):
    for k in range(7):
        bm_box(bm, (0.016, 0.05, 0.20),
               tf((sx * 0.398, 0.80 + k * 0.085, 1.16)), bevel=0.005, segments=1)
bm_box(bm, (0.10, 1.26, 0.030), tf((0, 1.16, 1.442)), bevel=0.010, segments=2)
bm_finish(bm, "Louvres", M_BLACK, root, math.radians(35))

# --- grille, headlights, front weights --------------------------------------
bm = bmesh.new()
bm_box(bm, (0.64, 0.10, 0.32), tf((0, 1.83, 1.07)), bevel=0.020, segments=2)
for k in range(7):
    bm_box(bm, (0.030, 0.06, 0.30), tf((-0.27 + k * 0.09, 1.87, 1.07)))
bm_box(bm, (0.66, 0.08, 0.05), tf((0, 1.85, 1.245)), bevel=0.014, segments=2)
bm_finish(bm, "Grille", M_BLACK, root, math.radians(35))

bm = bmesh.new()
for sx in (1, -1):
    bm_cyl(bm, 0.085, 0.10, tf((sx * 0.245, 1.84, 1.30), (math.radians(90), 0, 0)),
           segs=20, bevel=0.012)
bm_finish(bm, "HeadlightHousings", M_STEEL, root, math.radians(35))
bm = bmesh.new()
for sx in (1, -1):
    bm_cyl(bm, 0.072, 0.03, tf((sx * 0.245, 1.895, 1.30), (math.radians(90), 0, 0)), segs=20)
bm_finish(bm, "HeadlightLenses", M_GLASS, root, math.radians(35))

bm = bmesh.new()
bm_box(bm, (0.80, 0.16, 0.10), tf((0, 2.02, 0.78)), bevel=0.014, segments=2)
for k in range(8):
    bm_box(bm, (0.085, 0.20, 0.30), tf((-0.36 + k * 0.103, 2.06, 0.95)),
           bevel=0.012, segments=2)
bm_finish(bm, "FrontWeights", M_STEEL, root, math.radians(35))

# --- exhaust stack and pre-cleaner ------------------------------------------
bm = bmesh.new()
bm_cyl(bm, 0.048, 0.95, tf((0.30, 1.28, 1.82)), segs=20)
bm_cyl(bm, 0.062, 0.10, tf((0.30, 1.28, 1.36)), segs=20, bevel=0.012)
bm_cyl(bm, 0.055, 0.08, tf((0.30, 1.28, 2.32)), segs=20, r2=0.048)
bm_box(bm, (0.11, 0.11, 0.020), tf((0.30, 1.315, 2.375), (math.radians(18), 0, 0)),
       bevel=0.006, segments=2)
bm_finish(bm, "Exhaust", M_CHROME, root, math.radians(32))

bm = bmesh.new()
bm_cyl(bm, 0.035, 0.55, tf((-0.30, 1.30, 1.62)), segs=16)
bm_cyl(bm, 0.085, 0.14, tf((-0.30, 1.30, 1.94)), segs=20, bevel=0.02)
bm_cyl(bm, 0.055, 0.05, tf((-0.30, 1.30, 2.03)), segs=16, r2=0.075)
bm_finish(bm, "PreCleaner", M_BLACK, root, math.radians(32))

# --- platform, steps, fenders -----------------------------------------------
bm = bmesh.new()
for sx in (1, -1):
    bm_box(bm, (0.36, 0.86, 0.045), tf((sx * 0.52, 0.16, 0.99)), bevel=0.010, segments=2)
    bm_box(bm, (0.30, 0.06, 0.035), tf((sx * 0.56, -0.10, 0.72)), bevel=0.008, segments=2)
    bm_box(bm, (0.30, 0.06, 0.035), tf((sx * 0.58, -0.10, 0.45)), bevel=0.008, segments=2)
    bm_box(bm, (0.05, 0.05, 0.55), tf((sx * 0.60, 0.12, 0.72)), bevel=0.008, segments=2)
bm_finish(bm, "Platform", M_STEEL, root, math.radians(35))


def fender_fn(sx):
    def fn(u, v):
        a = math.radians(18 + u * 150.0)
        r = 0.96
        return (sx * (RX + (v - 0.5) * 0.52), RY + r * math.cos(a), 0.82 + r * math.sin(a))
    return fn


for sx in (1, -1):
    surface("Fender.%d" % sx, 22, 5, fender_fn(sx), M_PAINT, root, thickness=0.018)
    bm = bmesh.new()
    bm_box(bm, (0.06, 0.55, 0.06), tf((sx * 0.60, RY + 0.10, 1.72)), bevel=0.012, segments=2)
    bm_box(bm, (0.34, 0.06, 0.10), tf((sx * (RX - 0.10), RY - 0.90, 1.15)),
           bevel=0.012, segments=2)
    bm_finish(bm, "FenderBrace.%d" % sx, M_STEEL, root, math.radians(35))

# --- seat, steering, controls -----------------------------------------------
bm = bmesh.new()
bm_box(bm, (0.24, 0.22, 0.24), tf((0, -0.66, 1.10)), bevel=0.020, segments=2)
bm_finish(bm, "SeatPedestal", M_STEEL, root, math.radians(35))

bm = bmesh.new()
bm_box(bm, (0.48, 0.44, 0.12), tf((0, -0.62, 1.28)), bevel=0.045, segments=4)
bm_box(bm, (0.48, 0.14, 0.46), tf((0, -0.84, 1.52), (math.radians(-12), 0, 0)),
       bevel=0.045, segments=4)
bm_finish(bm, "Seat", M_SEAT, root, math.radians(38))

bm = bmesh.new()
bm_box(bm, (0.56, 0.26, 0.34), tf((0, 0.40, 1.30), (math.radians(10), 0, 0)),
       bevel=0.025, segments=3)
bm_cyl(bm, 0.040, 0.52, tf((0, 0.36, 1.55), (math.radians(-28), 0, 0)), segs=16)
bm_finish(bm, "Dash", M_PAINT, root, math.radians(35))

SW = tf((0, 0.22, 1.79), (math.radians(-28), 0, 0))
bpy.ops.mesh.primitive_torus_add(major_radius=0.175, minor_radius=0.020,
                                 major_segments=32, minor_segments=12)
sw = bpy.context.active_object
sw.name = "SteeringWheel"
sw.matrix_world = SW
sw.data.materials.append(M_BLACK)
sw.parent = root
smooth(sw, math.radians(45))

bm = bmesh.new()
for k in range(3):
    a = 2 * math.pi * k / 3.0 + math.radians(90)
    bm_box(bm, (0.16, 0.024, 0.016),
           SW @ tf((0.085 * math.cos(a), 0.085 * math.sin(a), 0), (0, 0, a)))
bm_cyl(bm, 0.055, 0.05, SW, segs=20, bevel=0.01)
bm_finish(bm, "SteeringSpokes", M_BLACK, root, math.radians(40))

bm = bmesh.new()
for (x, y, h) in ((0.34, -0.15, 0.36), (0.42, -0.22, 0.30), (-0.34, -0.15, 0.34)):
    bm_cyl(bm, 0.016, h, tf((x, y, 1.10 + h * 0.5), (math.radians(-10), 0, 0)), segs=10)
    bm_cyl(bm, 0.032, 0.055, tf((x, y - 0.03, 1.12 + h), (math.radians(-10), 0, 0)), segs=12)
bm_finish(bm, "Levers", M_BLACK, root, math.radians(35))

# --- ROPS roll bar and beacon ------------------------------------------------
tube("ROPS", [(-0.44, -0.92, 1.00), (-0.44, -0.92, 2.28), (-0.30, -0.92, 2.40),
              (0.30, -0.92, 2.40), (0.44, -0.92, 2.28), (0.44, -0.92, 1.00)],
     0.045, M_PAINT, root, fillet=0.12)
tube("ROPSBrace", [(-0.44, -0.92, 1.75), (0.44, -0.92, 1.75)], 0.035, M_PAINT, root)
bm = bmesh.new()
for sx in (1, -1):
    bm_box(bm, (0.14, 0.14, 0.16), tf((sx * 0.44, -0.92, 1.02)), bevel=0.014, segments=2)
    bm_cyl(bm, 0.055, 0.14, tf((sx * 0.30, -0.86, 2.30), (math.radians(-70), 0, 0)),
           segs=16, bevel=0.012)
bm_finish(bm, "ROPSMounts", M_STEEL, root, math.radians(35))

bm = bmesh.new()
bm_cyl(bm, 0.055, 0.10, tf((0, -0.92, 2.46)), segs=20, r2=0.045)
bm_finish(bm, "BeaconBase", M_BLACK, root, math.radians(35))
bm = bmesh.new()
bm_cyl(bm, 0.052, 0.09, tf((0, -0.92, 2.55)), segs=20, r2=0.038, bevel=0.012)
bm_finish(bm, "Beacon", M_AMBER, root, math.radians(35))

# --- rear hitch, drawbar, PTO ------------------------------------------------
bm = bmesh.new()
for sx in (1, -1):
    a = Vector((sx * 0.26, -1.10, 0.78))
    b = Vector((sx * 0.40, -1.62, 0.40))
    d = b - a
    bm_box(bm, (0.09, d.length, 0.09),
           tf(tuple((a + b) * 0.5), (math.atan2(-d.z, -d.y) + math.pi, 0,
                                     math.atan2(-d.x, -d.y) * 0.0)), bevel=0.012, segments=2)
    bm_cyl(bm, 0.055, 0.10, tf(tuple(b), (0, math.radians(90), 0)), segs=14, bevel=0.01)
    bm_cyl(bm, 0.030, 0.44, tf((sx * 0.30, -1.20, 1.06), (math.radians(-40), 0, 0)), segs=12)
bm_box(bm, (0.08, 0.60, 0.08), tf((0, -1.35, 0.96), (math.radians(14), 0, 0)),
       bevel=0.012, segments=2)
bm_box(bm, (0.10, 0.46, 0.06), tf((0, -1.40, 0.50)), bevel=0.010, segments=2)
bm_cyl(bm, 0.038, 0.24, tf((0, -1.20, 0.62), (math.radians(90), 0, 0)), segs=14)
bm_finish(bm, "Hitch", M_STEEL, root, math.radians(35))

bm = bmesh.new()
for sx in (1, -1):
    bm_box(bm, (0.10, 0.05, 0.16), tf((sx * 0.62, -1.12, 1.62)), bevel=0.014, segments=2)
bm_finish(bm, "RearLights", M_GLASS, root, math.radians(35))

# --- front axle --------------------------------------------------------------
bm = bmesh.new()
bm_box(bm, (1.16, 0.18, 0.16), tf((0, FY, 0.62)), bevel=0.020, segments=2)
bm_box(bm, (0.22, 0.50, 0.16), tf((0, FY - 0.30, 0.64)), bevel=0.020, segments=2)
bm_cyl(bm, 0.05, 0.16, tf((0, FY, 0.70)), segs=14)
for sx in (1, -1):
    bm_cyl(bm, 0.055, 0.26, tf((sx * 0.58, FY, 0.56)), segs=14)
    bm_cyl(bm, 0.05, 0.14, tf((sx * FX, FY, FR), (0, math.radians(90), 0)), segs=14)
    bm_box(bm, (0.05, 0.42, 0.05), tf((sx * 0.50, FY - 0.16, 0.58)), bevel=0.008, segments=1)
bm_finish(bm, "FrontAxle", M_STEEL, root, math.radians(35))


# --- wheels ------------------------------------------------------------------
def rear_wheel(sx):
    x = sx * RX
    sgn = float(sx)
    Mx = tf((x, RY, RR), (0, math.radians(90), 0))
    bm = bmesh.new()
    bm_cyl(bm, RR - 0.075, RW, Mx, segs=48, bevel=0.05, bsegs=3)
    nlug = 22
    for k in range(nlug):
        a = 2 * math.pi * k / nlug
        side = 1 if (k % 2 == 0) else -1
        base = tf((x, RY, RR)) @ Matrix.Rotation(a, 4, 'X')
        M = (base @ Matrix.Translation((side * RW * 0.235, 0.0, RR - 0.085))
             @ Matrix.Rotation(side * 0.44, 4, 'Z'))
        bm_box(bm, (RW * 0.50, 0.105, 0.17), M, bevel=0.018, segments=2)
    bm_finish(bm, "RearTire.%d" % sx, M_RUBBER, root, math.radians(40))

    bm = bmesh.new()
    bm_cyl(bm, RR * 0.56, RW * 0.80, Mx, segs=36, bevel=0.015)
    bm_cyl(bm, RR * 0.50, 0.045, tf((x + sgn * RW * 0.10, RY, RR),
                                    (0, math.radians(90), 0)), segs=36, bevel=0.010)
    bm_cyl(bm, 0.135, 0.10, tf((x + sgn * RW * 0.16, RY, RR),
                               (0, math.radians(90), 0)), segs=24, bevel=0.015)
    for k in range(8):
        a = 2 * math.pi * k / 8.0
        bm_cyl(bm, 0.024, 0.045,
               tf((x + sgn * RW * 0.20, RY + 0.095 * math.cos(a), RR + 0.095 * math.sin(a)),
                  (0, math.radians(90), 0)), segs=6)
    for k in range(6):
        a = 2 * math.pi * k / 6.0 + 0.4
        bm_box(bm, (0.05, 0.10, 0.30),
               tf((x + sgn * RW * 0.06, RY + 0.26 * math.cos(a), RR + 0.26 * math.sin(a)),
                  (a + math.radians(90), 0, 0)), bevel=0.012, segments=2)
    bm_finish(bm, "RearRim.%d" % sx, M_YELLOW, root, math.radians(35))


def front_wheel(sx):
    x = sx * FX
    sgn = float(sx)
    Mx = tf((x, FY, FR), (0, math.radians(90), 0))
    bm = bmesh.new()
    bm_cyl(bm, FR, FW, Mx, segs=40, bevel=0.045, bsegs=3)
    for k in range(5):
        bm_cyl(bm, FR + 0.012, 0.022,
               tf((x - FW * 0.4 + k * (FW * 0.2), FY, FR), (0, math.radians(90), 0)),
               segs=40, bevel=0.006)
    bm_finish(bm, "FrontTire.%d" % sx, M_RUBBER, root, math.radians(40))

    bm = bmesh.new()
    bm_cyl(bm, FR * 0.58, FW * 0.8, Mx, segs=28, bevel=0.010)
    bm_cyl(bm, FR * 0.52, 0.030, tf((x + sgn * FW * 0.12, FY, FR),
                                    (0, math.radians(90), 0)), segs=28, bevel=0.008)
    bm_cyl(bm, 0.070, 0.06, tf((x + sgn * FW * 0.20, FY, FR),
                               (0, math.radians(90), 0)), segs=18, bevel=0.010)
    for k in range(6):
        a = 2 * math.pi * k / 6.0
        bm_cyl(bm, 0.030, 0.035,
               tf((x + sgn * FW * 0.16, FY + 0.135 * math.cos(a), FR + 0.135 * math.sin(a)),
                  (0, math.radians(90), 0)), segs=12)
    bm_finish(bm, "FrontRim.%d" % sx, M_YELLOW, root, math.radians(35))


for sx in (1, -1):
    rear_wheel(sx)
    front_wheel(sx)

# --- ground ------------------------------------------------------------------
bm = bmesh.new()
bm_box(bm, (60.0, 60.0, 0.2), tf((0, 0, -0.1)))
bm_finish(bm, "Ground", M_GROUND)

root.rotation_euler = (0, 0, math.radians(26))

# --- lighting and camera -----------------------------------------------------
add_light("Sun", 'SUN', 4.5, (5.0, -8.0, 10.0), (0, 0, 1.0))
add_light("Key", 'AREA', 1800.0, (5.0, -5.5, 5.0), (0, 0, 1.2), size=4.5)
add_light("Fill", 'AREA', 500.0, (-6.0, -3.5, 3.0), (0, 0, 1.2), size=7.0)
add_light("Rim", 'AREA', 800.0, (-2.5, 6.0, 4.0), (0, 0, 1.4), size=4.0)

cd = bpy.data.cameras.new("Camera")
cd.lens = 55.0
cd.clip_start = 0.05
cd.clip_end = 500.0
cam = bpy.data.objects.new("Camera", cd)
link(cam)
cam.location = (4.6, -5.6, 2.55)
cam.rotation_euler = (Vector((0, 0.1, 1.15)) - cam.location).to_track_quat('-Z', 'Y').to_euler()
scene.camera = cam
