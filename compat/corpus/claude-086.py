"""claude-086 : Wristwatch with round case, hands and a segmented metal bracelet.
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
        s.cycles.samples = 160
    except Exception:
        pass
    s.render.resolution_x, s.render.resolution_y = 1600, 1200
    return s


def mat(name, base, metallic=0.0, rough=0.5, trans=0.0, emis=None, es=0.0, ior=1.45):
    m = bpy.data.materials.new(name)
    m.use_nodes = True
    i = m.node_tree.nodes["Principled BSDF"].inputs
    i["Base Color"].default_value = (base[0], base[1], base[2], 1.0)
    i["Metallic"].default_value = metallic
    i["Roughness"].default_value = rough
    if "IOR" in i:
        i["IOR"].default_value = ior
    if trans:
        for k in ("Transmission Weight", "Transmission"):
            if k in i:
                i[k].default_value = trans
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


def bm_cyl(bm, r, depth, matrix=None, segs=32, r2=None, cap=True, bevel=0.0, bsegs=2):
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


def frame_matrix(loc, ydir, up=Vector((0, 0, 1))):
    y = Vector(ydir).normalized()
    x = y.cross(up)
    if x.length < 1e-9:
        x = Vector((1, 0, 0))
    x.normalize()
    z = x.cross(y).normalized()
    M = Matrix((x, y, z)).transposed().to_4x4()
    M.translation = Vector(loc)
    return M


def add_light(name, ltype, energy, loc, target=None, size=1.0, color=(1, 1, 1)):
    d = bpy.data.lights.new(name, ltype)
    d.energy = energy
    d.color = color
    if ltype == 'AREA':
        d.size = size
        d.shape = 'SQUARE'
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
bg.inputs[0].default_value = (0.05, 0.055, 0.065, 1.0)
bg.inputs[1].default_value = 1.0
scene.world = w

M_STEEL = mat("Steel", (0.72, 0.73, 0.75), metallic=1.0, rough=0.16)
M_STEEL_B = mat("SteelBrushed", (0.68, 0.69, 0.71), metallic=1.0, rough=0.34)
M_DIAL = mat("Dial", (0.035, 0.045, 0.075), metallic=0.35, rough=0.28)
M_GLASS = mat("Crystal", (1.0, 1.0, 1.0), rough=0.02, trans=1.0, ior=1.52)
M_HAND = mat("Hands", (0.86, 0.87, 0.89), metallic=1.0, rough=0.08)
M_LUME = mat("Lume", (0.80, 0.93, 0.82), rough=0.4, emis=(0.55, 0.95, 0.70), es=1.2)
M_RED = mat("SecondHand", (0.62, 0.06, 0.05), metallic=0.2, rough=0.35)
M_WHITE = mat("DateDisc", (0.90, 0.90, 0.88), rough=0.45)
M_GROUND = mat("Ground", (0.10, 0.105, 0.115), rough=0.55)

root = bpy.data.objects.new("Wristwatch", None)
link(root)

R_CASE = 0.0200
H_CASE = 0.0105

# --- case, caseback, bezel ---------------------------------------------------
bm = bmesh.new()
bm_cyl(bm, R_CASE, H_CASE, tf((0, 0, H_CASE * 0.5)), segs=72, bevel=0.0009, bsegs=3)
bm_cyl(bm, R_CASE * 0.86, 0.0022, tf((0, 0, -0.0004)), segs=64, bevel=0.0006, bsegs=2)
bm_cyl(bm, R_CASE * 0.55, 0.0010, tf((0, 0, -0.0012)), segs=48, bevel=0.0003)
bm_finish(bm, "Case", M_STEEL_B, root, math.radians(30))

bm = bmesh.new()
# bezel ring built as a lofted square-ish torus profile
rings = []
for k in range(73):
    a = 2 * math.pi * k / 72.0
    ca, sa = math.cos(a), math.sin(a)
    ring = []
    for (rr, zz) in ((0.0168, 0.0088), (0.0204, 0.0098), (0.0204, 0.0118), (0.0176, 0.0128)):
        ring.append((rr * ca, rr * sa, zz))
    rings.append(ring)
vr = [[bm.verts.new(p) for p in r] for r in rings[:-1]]
for i in range(len(vr)):
    a = vr[i]
    b = vr[(i + 1) % len(vr)]
    for j in range(len(a) - 1):
        bm.faces.new((a[j], a[j + 1], b[j + 1], b[j]))
# knurled bezel edge
for k in range(72):
    a = 2 * math.pi * k / 72.0
    bm_box(bm, (0.0012, 0.0022, 0.0026),
           tf((0.0203 * math.cos(a), 0.0203 * math.sin(a), 0.0108), (0, 0, a)))
bm_finish(bm, "Bezel", M_STEEL, root, math.radians(28))

# --- crystal -----------------------------------------------------------------
bm = bmesh.new()
bm_cyl(bm, 0.0170, 0.0016, tf((0, 0, 0.0118)), segs=64, bevel=0.0004, bsegs=2)
bm_finish(bm, "Crystal", M_GLASS, root, math.radians(30))

# --- dial, markers, date window ---------------------------------------------
bm = bmesh.new()
bm_cyl(bm, 0.0163, 0.0009, tf((0, 0, 0.00755)), segs=64)
bm_cyl(bm, 0.0163, 0.0004, tf((0, 0, 0.00775)), segs=64, r2=0.0152, cap=False)
bm_finish(bm, "Dial", M_DIAL, root, math.radians(40))

bm = bmesh.new()
for h in range(12):
    if h == 3:
        continue
    a = math.radians(h * 30.0)
    r = 0.0134
    long_marker = (h % 3 == 0)
    ln = 0.0034 if long_marker else 0.0024
    wd = 0.0016 if long_marker else 0.0011
    M = tf((r * math.sin(a), r * math.cos(a), 0.0083), (0, 0, -a))
    bm_box(bm, (wd, ln, 0.0006), M, bevel=0.00015, segments=1)
for k in range(60):
    a = 2 * math.pi * k / 60.0
    if k % 5 == 0:
        continue
    bm_box(bm, (0.00035, 0.0010, 0.00025),
           tf((0.0157 * math.sin(a), 0.0157 * math.cos(a), 0.0081), (0, 0, -a)))
bm_finish(bm, "Markers", M_STEEL, root, math.radians(30))

bm = bmesh.new()
for h in range(12):
    if h == 3:
        continue
    a = math.radians(h * 30.0)
    r = 0.0134
    ln = 0.0026 if h % 3 == 0 else 0.0018
    bm_box(bm, (0.0009, ln, 0.00035),
           tf((r * math.sin(a), r * math.cos(a), 0.00875), (0, 0, -a)))
bm_finish(bm, "MarkerLume", M_LUME, root)

bm = bmesh.new()
bm_box(bm, (0.0056, 0.0040, 0.0008), tf((0.0112, 0.0, 0.0082)), bevel=0.0002, segments=1)
bm_finish(bm, "DateWindow", M_STEEL, root, math.radians(30))
bm = bmesh.new()
bm_box(bm, (0.0048, 0.0033, 0.0004), tf((0.0112, 0.0, 0.00845)))
bm_finish(bm, "DateDisc", M_WHITE, root)


# --- hands -------------------------------------------------------------------
def hand_mesh(name, length, tail, halfw, thick, z, angle_deg, material, lume=False):
    bm = bmesh.new()
    outline = [(-halfw, -tail), (halfw, -tail), (halfw * 0.95, 0.0),
               (halfw * 0.5, length * 0.86), (0.0, length),
               (-halfw * 0.5, length * 0.86), (-halfw * 0.95, 0.0)]
    rings = []
    for zz in (-thick * 0.5, thick * 0.5):
        rings.append([(x, y, zz) for (x, y) in outline])
    bm_loft(bm, rings)
    ob = bm_finish(bm, name, material, root, math.radians(50))
    ob.location = (0.0, 0.0, z)
    ob.rotation_euler = (0.0, 0.0, math.radians(-angle_deg))
    if lume:
        bl = bmesh.new()
        bm_box(bl, (halfw * 0.9, length * 0.5, thick * 0.55),
               tf((0, length * 0.42, thick * 0.35)))
        lo = bm_finish(bl, name + "Lume", M_LUME, ob)
        lo.location = (0, 0, 0)
        lo.matrix_parent_inverse = Matrix.Identity(4)
    return ob


HOUR, MINUTE, SECOND = 10, 10, 33
hand_mesh("HourHand", 0.0086, 0.0022, 0.00115, 0.00065, 0.0090,
          (HOUR % 12) * 30.0 + MINUTE * 0.5, M_HAND, lume=True)
hand_mesh("MinuteHand", 0.0128, 0.0026, 0.00090, 0.00060, 0.0096,
          MINUTE * 6.0 + SECOND * 0.1, M_HAND, lume=True)

bm = bmesh.new()
bm_box(bm, (0.00040, 0.0192, 0.00030), tf((0, 0.0154 * 0.5 - 0.0019, 0)))
bm_cyl(bm, 0.0016, 0.00040, tf((0, -0.0034, 0)), segs=20)
sec = bm_finish(bm, "SecondHand", M_RED, root, math.radians(35))
sec.location = (0, 0, 0.0101)
sec.rotation_euler = (0, 0, math.radians(-SECOND * 6.0))

bm = bmesh.new()
bm_cyl(bm, 0.00110, 0.0011, tf((0, 0, 0.0104)), segs=24, bevel=0.0002)
bm_finish(bm, "HandCap", M_HAND, root, math.radians(30))

# --- crown and lugs ----------------------------------------------------------
bm = bmesh.new()
Mc = tf((0.0212, 0, 0.0052), (0, math.radians(90), 0))
bm_cyl(bm, 0.0036, 0.0032, Mc, segs=28, bevel=0.0005, bsegs=2)
bm_cyl(bm, 0.0022, 0.0028, tf((0.0198, 0, 0.0052), (0, math.radians(90), 0)), segs=20)
for k in range(20):
    a = 2 * math.pi * k / 20.0
    bm_box(bm, (0.0034, 0.0007, 0.0007),
           tf((0.0212, 0.0035 * math.cos(a), 0.0052 + 0.0035 * math.sin(a)),
              (a, math.radians(90), 0)))
bm_finish(bm, "Crown", M_STEEL, root, math.radians(30))

bm = bmesh.new()
for sy in (1, -1):
    for sx in (1, -1):
        bm_box(bm, (0.0052, 0.0092, 0.0058),
               tf((sx * 0.0118, sy * 0.0178, 0.0040), (math.radians(sy * -6), 0, 0)),
               bevel=0.0011, segments=3)
    bm_cyl(bm, 0.00085, 0.0250, tf((0, sy * 0.0208, 0.0034), (0, math.radians(90), 0)), segs=16)
bm_finish(bm, "Lugs", M_STEEL_B, root, math.radians(32))

# --- segmented bracelet ------------------------------------------------------
PITCH = 0.0058
N_LINKS = 13
ends = {}
bm = bmesh.new()
for sign in (1, -1):
    p = Vector((0.0, sign * 0.0212, 0.0026))
    d = Vector((0.0, float(sign), 0.0))
    for i in range(N_LINKS):
        ramp = min(1.0, i / 2.0)
        turn = math.radians(11.5) * ramp
        d = (Matrix.Rotation(-sign * turn, 3, 'X') @ d).normalized()
        a = p.copy()
        b = p + d * PITCH
        mid = (a + b) * 0.5
        F = frame_matrix(mid, d * sign)
        t = i / float(N_LINKS - 1)
        wtot = 0.0192 - 0.0048 * t
        wc = wtot * 0.44
        ws = wtot * 0.26
        bm_box(bm, (wc, PITCH * 0.86, 0.0034), F, bevel=0.00075, segments=3)
        for sx in (1, -1):
            off = sx * (wc * 0.5 + ws * 0.5 + 0.00025)
            bm_box(bm, (ws, PITCH * 0.86, 0.0029),
                   F @ Matrix.Translation((off, PITCH * 0.5, -0.00015)),
                   bevel=0.00060, segments=3)
        bm_cyl(bm, 0.00075, wtot + 0.0004,
               frame_matrix(a, d * sign) @ tf((0, 0, 0), (0, math.radians(90), 0)), segs=12)
        p = b
    ends[sign] = (p.copy(), d.copy())
bm_finish(bm, "Bracelet", M_STEEL_B, root, math.radians(30))

# --- folding clasp bridging the two bracelet ends ----------------------------
e1 = ends[1][0]
e2 = ends[-1][0]
gap = e2 - e1
L = gap.length
F = frame_matrix((e1 + e2) * 0.5, gap)
bm = bmesh.new()
bm_box(bm, (0.0142, L * 0.98, 0.0022), F, bevel=0.0007, segments=3)
bm_box(bm, (0.0152, L * 0.72, 0.0020), F @ Matrix.Translation((0, 0, -0.0026)),
       bevel=0.0007, segments=3)
bm_box(bm, (0.0126, L * 0.40, 0.0014), F @ Matrix.Translation((0, 0, 0.0021)),
       bevel=0.0005, segments=2)
for sx in (1, -1):
    bm_box(bm, (0.0022, 0.0042, 0.0016),
           F @ Matrix.Translation((sx * 0.0078, L * 0.30, -0.0026)), bevel=0.0004, segments=2)
bm_finish(bm, "Clasp", M_STEEL, root, math.radians(30))

# --- presentation surface ----------------------------------------------------
bm = bmesh.new()
bm_box(bm, (0.9, 0.9, 0.02), tf((0, 0, -0.0790)))
bm_finish(bm, "Ground", M_GROUND, None)

root.rotation_euler = (0.0, 0.0, math.radians(-14))

# --- lighting and camera -----------------------------------------------------
add_light("KeyLight", 'AREA', 55.0, (0.16, -0.14, 0.26), (0, 0, 0.01), size=0.30)
add_light("FillLight", 'AREA', 18.0, (-0.22, -0.10, 0.10), (0, 0, 0.005), size=0.40)
add_light("RimLight", 'AREA', 30.0, (-0.05, 0.24, 0.18), (0, 0, 0.005), size=0.25)

cd = bpy.data.cameras.new("Camera")
cd.lens = 80.0
cd.clip_start = 0.005
cd.clip_end = 50.0
cd.dof.use_dof = True
cam = bpy.data.objects.new("Camera", cd)
link(cam)
cam.location = (0.085, -0.115, 0.082)
cam.rotation_euler = (Vector((0, 0, 0.004)) - cam.location).to_track_quat('-Z', 'Y').to_euler()
cd.dof.focus_distance = (Vector((0, 0, 0.004)) - cam.location).length
cd.dof.aperture_fstop = 4.0
scene.camera = cam
