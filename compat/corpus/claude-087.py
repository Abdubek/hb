"""claude-087 : Folding camping chair with a tubular frame and sagging fabric.
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
    s.render.resolution_x, s.render.resolution_y = 1600, 1200
    return s


def mat(name, base, metallic=0.0, rough=0.5, sheen=0.0):
    m = bpy.data.materials.new(name)
    m.use_nodes = True
    i = m.node_tree.nodes["Principled BSDF"].inputs
    i["Base Color"].default_value = (base[0], base[1], base[2], 1.0)
    i["Metallic"].default_value = metallic
    i["Roughness"].default_value = rough
    if sheen:
        for k in ("Sheen Weight", "Sheen"):
            if k in i:
                i[k].default_value = sheen
                break
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


def bm_cyl(bm, r, depth, matrix=None, segs=24, r2=None, cap=True, bevel=0.0, bsegs=2):
    res = bmesh.ops.create_cone(bm, cap_ends=cap, cap_tris=False, segments=segs,
                                radius1=r, radius2=(r if r2 is None else r2),
                                depth=depth, matrix=(matrix or Matrix.Identity(4)))
    if bevel > 0.0:
        _bevel(bm, res, bevel, bsegs)
    return res


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


def round_corners(pts, radius, segs=6):
    """Insert quadratic fillets at every interior corner of a polyline."""
    out = [Vector(pts[0])]
    for i in range(1, len(pts) - 1):
        p0, p1, p2 = Vector(pts[i - 1]), Vector(pts[i]), Vector(pts[i + 1])
        d0, d2 = p0 - p1, p2 - p1
        l0, l2 = d0.length, d2.length
        if l0 < 1e-9 or l2 < 1e-9:
            continue
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


def tube(name, pts, radius, material, parent=None, bevel_res=4, fillet=0.0, caps=True):
    if fillet > 0.0:
        pts = round_corners(pts, fillet)
    cu = bpy.data.curves.new(name, 'CURVE')
    cu.dimensions = '3D'
    cu.resolution_u = 3
    cu.bevel_depth = radius
    cu.bevel_resolution = bevel_res
    cu.use_fill_caps = caps
    sp = cu.splines.new('POLY')
    sp.points.add(len(pts) - 1)
    for i, p in enumerate(pts):
        sp.points[i].co = (p[0], p[1], p[2], 1.0)
    sp.use_smooth = True
    ob = bpy.data.objects.new(name, cu)
    link(ob, parent)
    cu.materials.append(material)
    return ob


def surface(name, nu, nv, fn, material, parent=None, thickness=0.0):
    bm = bmesh.new()
    grid = [[bm.verts.new(fn(i / (nu - 1.0), j / (nv - 1.0))) for j in range(nv)]
            for i in range(nu)]
    for i in range(nu - 1):
        for j in range(nv - 1):
            bm.faces.new((grid[i][j], grid[i + 1][j], grid[i + 1][j + 1], grid[i][j + 1]))
    ob = bm_finish(bm, name, material, parent, math.radians(80))
    if thickness > 0.0:
        md = ob.modifiers.new("Solidify", 'SOLIDIFY')
        md.thickness = thickness
        md.offset = 0.0
    return ob


def add_light(name, ltype, energy, loc, target=None, size=1.0, color=(1, 1, 1)):
    d = bpy.data.lights.new(name, ltype)
    d.energy = energy
    d.color = color
    if ltype == 'AREA':
        d.size = size
    elif ltype == 'SUN':
        d.angle = math.radians(2.5)
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
bg.inputs[0].default_value = (0.34, 0.42, 0.55, 1.0)
bg.inputs[1].default_value = 1.1
scene.world = w

M_TUBE = mat("PowderTube", (0.13, 0.14, 0.16), metallic=0.85, rough=0.36)
M_TUBE2 = mat("BrightTube", (0.55, 0.57, 0.60), metallic=0.95, rough=0.25)
M_FABRIC = mat("Fabric", (0.10, 0.24, 0.42), rough=0.92, sheen=0.35)
M_FABRIC2 = mat("FabricTrim", (0.55, 0.16, 0.10), rough=0.92, sheen=0.3)
M_PLASTIC = mat("Plastic", (0.045, 0.045, 0.05), rough=0.55)
M_MESH = mat("CupMesh", (0.08, 0.08, 0.09), rough=0.7)
M_GROUND = mat("Ground", (0.20, 0.21, 0.17), rough=0.95)

root = bpy.data.objects.new("CampingChair", None)
link(root)

W = 0.245          # half width of the frame
RT = 0.0115        # tube radius
ZS = 0.445         # seat rail height

# --- frame A : front feet -> seat rear rail -> back posts -> top bar ---------
path_a = [(-W, -0.26, 0.02), (-W, 0.16, ZS), (-W, 0.235, 0.95),
          (W, 0.235, 0.95), (W, 0.16, ZS), (W, -0.26, 0.02)]
tube("FrameBack", path_a, RT, M_TUBE, root, fillet=0.075)

# --- frame B : rear feet -> seat front rail -> armrest (mirrored pair) ------
for sx in (1, -1):
    x = sx * W
    path_b = [(x, 0.28, 0.02), (x, -0.16, ZS), (x, -0.205, 0.63),
              (x, -0.185, 0.685), (x, 0.203, 0.705)]
    tube("FrameArm.%s" % ("R" if sx > 0 else "L"), path_b, RT, M_TUBE, root, fillet=0.055)

# --- cross bars --------------------------------------------------------------
for (y, z, nm) in ((-0.26, 0.02, "FrontFoot"), (0.28, 0.02, "RearFoot"),
                   (-0.16, ZS, "SeatFront"), (0.16, ZS, "SeatRear"),
                   (0.222, 0.86, "BackBrace")):
    tube("Cross_" + nm, [(-W, y, z), (W, y, z)], RT * 0.85, M_TUBE2, root)

# --- pivot hardware at the X crossing and at the joints ----------------------
bm = bmesh.new()
for sx in (1, -1):
    for (y, z) in ((0.004, 0.284), (-0.16, ZS), (0.16, ZS), (0.200, 0.703)):
        bm_cyl(bm, 0.016, 0.016, tf((sx * (W + 0.010), y, z), (0, math.radians(90), 0)),
               segs=16, bevel=0.002)
        bm_cyl(bm, 0.0055, 0.030, tf((sx * (W + 0.010), y, z), (0, math.radians(90), 0)), segs=12)
bm_finish(bm, "Pivots", M_TUBE2, root, math.radians(30))

# --- plastic feet ------------------------------------------------------------
bm = bmesh.new()
for sx in (1, -1):
    for y in (-0.26, 0.28):
        bm_cyl(bm, 0.026, 0.055, tf((sx * W, y, 0.024)), segs=20, r2=0.030, bevel=0.006, bsegs=3)
bm_finish(bm, "Feet", M_PLASTIC, root, math.radians(35))


# --- seat fabric (sags between the two seat rails) ---------------------------
def seat_fn(u, v):
    x = -W * 1.02 + u * 2.0 * W * 1.02
    y = -0.205 + v * 0.41
    edge = math.sin(math.pi * min(max(v, 0.0), 1.0))
    z = ZS + 0.012 - 0.075 * edge ** 0.85 - 0.030 * math.sin(math.pi * u) * edge
    return (x, y, z)


surface("SeatFabric", 22, 22, seat_fn, M_FABRIC, root, thickness=0.007)


# --- back fabric (follows the back posts, bulges rearwards) ------------------
def back_fn(u, v):
    z = 0.475 + v * 0.455
    x = (-W * 0.99 + u * 2.0 * W * 0.99) * (1.0 - 0.03 * math.sin(math.pi * v))
    y_post = 0.16 + (z - ZS) / 0.51 * 0.075
    y = y_post + 0.014 + 0.045 * math.sin(math.pi * u) * math.sin(math.pi * v) ** 0.6
    return (x, y, z)


surface("BackFabric", 20, 20, back_fn, M_FABRIC, root, thickness=0.007)

# --- fabric trim strips ------------------------------------------------------
bm = bmesh.new()
bm_box(bm, (2.0 * W * 1.03, 0.055, 0.014), tf((0, -0.198, ZS + 0.006)), bevel=0.005, segments=2)
bm_box(bm, (2.0 * W * 1.03, 0.055, 0.014), tf((0, 0.198, ZS + 0.006)), bevel=0.005, segments=2)
bm_box(bm, (2.0 * W * 1.00, 0.035, 0.014), tf((0, 0.245, 0.925), (math.radians(-8), 0, 0)),
       bevel=0.005, segments=2)
bm_finish(bm, "FabricTrim", M_FABRIC2, root, math.radians(40))

# --- armrest pads ------------------------------------------------------------
bm = bmesh.new()
for sx in (1, -1):
    bm_box(bm, (0.062, 0.375, 0.024),
           tf((sx * W, 0.010, 0.706), (0.0515, 0, 0)), bevel=0.010, segments=4)
bm_finish(bm, "ArmrestPads", M_PLASTIC, root, math.radians(35))

# --- cup holder on the right armrest ----------------------------------------
cup_c = (W + 0.085, 0.075, 0.660)
bm = bmesh.new()
bm_cyl(bm, 0.046, 0.105, tf(cup_c), segs=24, cap=False)
bm_cyl(bm, 0.046, 0.006, tf((cup_c[0], cup_c[1], cup_c[2] - 0.049)), segs=24)
for k in range(3):
    bm_cyl(bm, 0.047, 0.0055, tf((cup_c[0], cup_c[1], cup_c[2] - 0.03 + k * 0.032)),
           segs=24, cap=False)
cup = bm_finish(bm, "CupHolder", M_MESH, root, math.radians(40))
md = cup.modifiers.new("Solidify", 'SOLIDIFY')
md.thickness = 0.0035
tube("CupBracket", [(W + 0.010, 0.075, 0.700), (W + 0.050, 0.075, 0.695),
                    (W + 0.050, 0.075, 0.640)], 0.008, M_TUBE, root, fillet=0.02)

# --- storage pouch on the left arm ------------------------------------------
bm = bmesh.new()
bm_box(bm, (0.020, 0.185, 0.150), tf((-W - 0.020, 0.060, 0.605), (0, math.radians(4), 0)),
       bevel=0.012, segments=3)
bm_finish(bm, "SidePouch", M_FABRIC2, root, math.radians(40))

# --- ground ------------------------------------------------------------------
bm = bmesh.new()
bm_box(bm, (12.0, 12.0, 0.08), tf((0, 0, -0.04)))
bm_finish(bm, "Ground", M_GROUND)

root.rotation_euler = (0, 0, math.radians(18))

# --- lighting and camera -----------------------------------------------------
add_light("Sun", 'SUN', 3.6, (3.0, -4.0, 6.0), (0, 0, 0.5))
add_light("Key", 'AREA', 320.0, (2.2, -2.4, 2.6), (0, 0, 0.55), size=2.2)
add_light("Fill", 'AREA', 90.0, (-2.8, -1.6, 1.8), (0, 0, 0.5), size=3.0)

cd = bpy.data.cameras.new("Camera")
cd.lens = 52.0
cd.clip_start = 0.05
cd.clip_end = 200.0
cam = bpy.data.objects.new("Camera", cd)
link(cam)
cam.location = (1.75, -2.15, 1.25)
cam.rotation_euler = (Vector((0, 0.02, 0.52)) - cam.location).to_track_quat('-Z', 'Y').to_euler()
scene.camera = cam
