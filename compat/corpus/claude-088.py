"""claude-088 : Single axle utility trailer with plank bed, mesh sides, axle and hitch.
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
    s.render.resolution_x, s.render.resolution_y = 1600, 1100
    return s


def mat(name, base, metallic=0.0, rough=0.5, emis=None, es=0.0):
    m = bpy.data.materials.new(name)
    m.use_nodes = True
    i = m.node_tree.nodes["Principled BSDF"].inputs
    i["Base Color"].default_value = (base[0], base[1], base[2], 1.0)
    i["Metallic"].default_value = metallic
    i["Roughness"].default_value = rough
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
bg.inputs[0].default_value = (0.33, 0.40, 0.52, 1.0)
bg.inputs[1].default_value = 1.0
scene.world = w

M_FRAME = mat("FrameSteel", (0.055, 0.058, 0.065), metallic=0.85, rough=0.42)
M_GALV = mat("Galvanised", (0.62, 0.64, 0.66), metallic=1.0, rough=0.38)
M_WOOD = mat("DeckWood", (0.44, 0.31, 0.18), rough=0.78)
M_RUBBER = mat("Rubber", (0.035, 0.035, 0.04), rough=0.85)
M_RIM = mat("Rim", (0.78, 0.79, 0.80), metallic=1.0, rough=0.28)
M_RED = mat("TailLight", (0.45, 0.02, 0.02), rough=0.25, emis=(0.9, 0.05, 0.05), es=2.5)
M_AMBER = mat("Reflector", (0.55, 0.24, 0.02), rough=0.25, emis=(1.0, 0.45, 0.03), es=1.2)
M_PLATE = mat("Plate", (0.85, 0.85, 0.82), rough=0.4)
M_GROUND = mat("Ground", (0.20, 0.20, 0.19), rough=0.95)

root = bpy.data.objects.new("UtilityTrailer", None)
link(root)

HX = 0.76        # half deck width
Y0, Y1 = -1.22, 1.22   # deck extents (front is -Y)
DECK = 0.60      # deck surface height
RAIL_TOP = DECK - 0.04

# --- main frame --------------------------------------------------------------
bm = bmesh.new()
for sx in (1, -1):
    bm_box(bm, (0.07, Y1 - Y0, 0.11), tf((sx * (HX - 0.035), 0.0, RAIL_TOP - 0.055)),
           bevel=0.008, segments=2)
for y in (Y0 + 0.03, -0.62, -0.10, 0.42, Y1 - 0.03):
    bm_box(bm, (2 * HX, 0.06, 0.09), tf((0, y, RAIL_TOP - 0.05)), bevel=0.006, segments=2)
bm_box(bm, (2 * HX, 0.07, 0.13), tf((0, 0.0, RAIL_TOP - 0.06)), bevel=0.006, segments=2)
bm_finish(bm, "Frame", M_FRAME, root, math.radians(35))

# --- plank deck --------------------------------------------------------------
bm = bmesh.new()
NP = 11
pw = (2 * HX - 0.02) / NP
for k in range(NP):
    x = -HX + 0.01 + pw * (k + 0.5)
    bm_box(bm, (pw - 0.006, Y1 - Y0 - 0.01, 0.042), tf((x, 0.0, DECK - 0.021)),
           bevel=0.004, segments=2)
bm_finish(bm, "Deck", M_WOOD, root, math.radians(40))

# --- mesh sides and front headboard -----------------------------------------
bm = bmesh.new()
SH = 0.36
for sx in (1, -1):
    x = sx * (HX - 0.03)
    bm_box(bm, (0.05, Y1 - Y0, 0.05), tf((x, 0.0, DECK + SH)), bevel=0.006, segments=2)
    for y in (Y0 + 0.05, -0.55, 0.0, 0.55, Y1 - 0.05):
        bm_box(bm, (0.05, 0.05, SH), tf((x, y, DECK + SH * 0.5)), bevel=0.006, segments=2)
    for k in range(16):
        y = Y0 + 0.08 + k * ((Y1 - Y0 - 0.16) / 15.0)
        bm_box(bm, (0.022, 0.022, SH - 0.03), tf((x, y, DECK + SH * 0.5)))
    for zz in (DECK + SH * 0.35, DECK + SH * 0.7):
        bm_box(bm, (0.020, Y1 - Y0 - 0.10, 0.020), tf((x, 0.0, zz)))
# front headboard, taller
FH = 0.58
bm_box(bm, (2 * HX, 0.05, 0.05), tf((0, Y0 + 0.03, DECK + FH)), bevel=0.006, segments=2)
for sx in (1, -1):
    bm_box(bm, (0.05, 0.05, FH), tf((sx * (HX - 0.03), Y0 + 0.03, DECK + FH * 0.5)),
           bevel=0.006, segments=2)
for k in range(11):
    x = -HX + 0.09 + k * ((2 * HX - 0.18) / 10.0)
    bm_box(bm, (0.022, 0.022, FH - 0.03), tf((x, Y0 + 0.03, DECK + FH * 0.5)))
for zz in (DECK + FH * 0.33, DECK + FH * 0.66):
    bm_box(bm, (2 * HX - 0.10, 0.020, 0.020), tf((0, Y0 + 0.03, zz)))
bm_finish(bm, "Sides", M_FRAME, root, math.radians(35))

# --- rear tailgate, dropped open ---------------------------------------------
bm = bmesh.new()
GL = 0.70
gm = tf((0.0, Y1 + 0.03 + GL * 0.5 * math.cos(math.radians(72)),
         RAIL_TOP - GL * 0.5 * math.sin(math.radians(72))), (math.radians(-72), 0, 0))
bm_box(bm, (2 * HX, GL, 0.05), gm, bevel=0.006, segments=2)
for k in range(9):
    u = -0.5 + k / 8.0
    bm_box(bm, (0.03, GL - 0.06, 0.03), gm @ Matrix.Translation((u * (2 * HX - 0.12), 0, 0.015)))
bm_finish(bm, "Tailgate", M_FRAME, root, math.radians(35))

# --- A-frame tongue and coupler ---------------------------------------------
bm = bmesh.new()
for sx in (1, -1):
    a = Vector((sx * (HX - 0.06), Y0 + 0.10, RAIL_TOP - 0.05))
    b = Vector((sx * 0.035, Y0 - 0.78, RAIL_TOP - 0.05))
    d = b - a
    ang = math.atan2(d.x, -d.y)
    bm_box(bm, (0.06, d.length, 0.10), tf(tuple((a + b) * 0.5), (0, 0, ang)),
           bevel=0.006, segments=2)
bm_box(bm, (0.14, 0.34, 0.10), tf((0, Y0 - 0.90, RAIL_TOP - 0.05)), bevel=0.008, segments=2)
bm_finish(bm, "Tongue", M_FRAME, root, math.radians(35))

bm = bmesh.new()
cy = Y0 - 1.03
bm_box(bm, (0.115, 0.24, 0.115), tf((0, cy, RAIL_TOP - 0.05)), bevel=0.012, segments=3)
bm_cyl(bm, 0.055, 0.075, tf((0, cy - 0.07, RAIL_TOP - 0.115)), segs=24, bevel=0.008)
bm_box(bm, (0.05, 0.13, 0.028), tf((0, cy + 0.02, RAIL_TOP + 0.035),
                                   (math.radians(-14), 0, 0)), bevel=0.006, segments=2)
bm_cyl(bm, 0.010, 0.09, tf((0, cy + 0.08, RAIL_TOP + 0.05), (0, math.radians(90), 0)), segs=12)
bm_finish(bm, "Coupler", M_GALV, root, math.radians(35))

# --- jack --------------------------------------------------------------------
bm = bmesh.new()
jx, jy = 0.19, Y0 - 0.66
bm_box(bm, (0.075, 0.075, 0.30), tf((jx, jy, RAIL_TOP + 0.02)), bevel=0.008, segments=2)
bm_cyl(bm, 0.026, 0.42, tf((jx, jy, RAIL_TOP - 0.28)), segs=16)
bm_cyl(bm, 0.010, 0.16, tf((jx, jy, RAIL_TOP + 0.19)), segs=12)
bm_cyl(bm, 0.010, 0.13, tf((jx + 0.065, jy, RAIL_TOP + 0.24), (0, math.radians(90), 0)), segs=12)
bm_cyl(bm, 0.014, 0.07, tf((jx + 0.13, jy, RAIL_TOP + 0.24)), segs=12)
bm_cyl(bm, 0.075, 0.055, tf((jx, jy, RAIL_TOP - 0.50), (0, math.radians(90), 0)), segs=20,
       bevel=0.008)
bm_finish(bm, "Jack", M_GALV, root, math.radians(35))

# --- safety chains -----------------------------------------------------------
for sx in (1, -1):
    for k in range(7):
        t = k / 6.0
        y = Y0 - 0.30 - t * 0.62
        z = RAIL_TOP - 0.10 - 0.20 * math.sin(math.pi * t)
        bpy.ops.mesh.primitive_torus_add(major_radius=0.026, minor_radius=0.006,
                                         major_segments=18, minor_segments=8,
                                         location=(sx * 0.10 + t * -sx * 0.05, y, z),
                                         rotation=(math.radians(90),
                                                   math.radians(90 * (k % 2)), 0))
        ob = bpy.context.active_object
        ob.name = "ChainLink"
        ob.data.materials.append(M_GALV)
        ob.parent = root
        smooth(ob, math.radians(50))

# --- axle, springs, hubs -----------------------------------------------------
WHEEL_R = 0.305
WHEEL_X = 0.985
bm = bmesh.new()
bm_cyl(bm, 0.036, 1.86, tf((0, 0, 0.335), (0, math.radians(90), 0)), segs=20)
for sx in (1, -1):
    for k in range(3):
        bm_box(bm, (0.055, 0.62 - k * 0.13, 0.012),
               tf((sx * 0.70, 0.0, 0.395 + k * 0.014)), bevel=0.004, segments=1)
    bm_box(bm, (0.075, 0.10, 0.09), tf((sx * 0.70, 0.0, 0.365)), bevel=0.008, segments=2)
    for sy in (1, -1):
        bm_box(bm, (0.05, 0.05, 0.16), tf((sx * 0.70, sy * 0.30, RAIL_TOP - 0.14)),
               bevel=0.005, segments=2)
bm_finish(bm, "Axle", M_FRAME, root, math.radians(35))


# --- wheels ------------------------------------------------------------------
def make_wheel(name, x):
    bm = bmesh.new()
    Mx = tf((x, 0.0, WHEEL_R), (0, math.radians(90), 0))
    bm_cyl(bm, WHEEL_R, 0.185, Mx, segs=48, bevel=0.05, bsegs=4)
    for k in range(40):
        a = 2 * math.pi * k / 40.0
        bm_box(bm, (0.028, 0.150, 0.030),
               tf((x, (WHEEL_R - 0.012) * math.cos(a), WHEEL_R + (WHEEL_R - 0.012) * math.sin(a)),
                  (a + math.radians(18), 0, 0)))
    tire = bm_finish(bm, name + "Tire", M_RUBBER, root, math.radians(38))
    bm = bmesh.new()
    sgn = 1.0 if x > 0 else -1.0
    bm_cyl(bm, WHEEL_R * 0.62, 0.155, Mx, segs=32, bevel=0.012, bsegs=2)
    bm_cyl(bm, WHEEL_R * 0.50, 0.030, tf((x + sgn * 0.075, 0.0, WHEEL_R),
                                         (0, math.radians(90), 0)), segs=32, bevel=0.008)
    bm_cyl(bm, 0.062, 0.055, tf((x + sgn * 0.095, 0.0, WHEEL_R),
                                (0, math.radians(90), 0)), segs=20, bevel=0.008)
    for k in range(5):
        a = 2 * math.pi * k / 5.0
        bm_cyl(bm, 0.014, 0.030,
               tf((x + sgn * 0.100, 0.10 * math.cos(a), WHEEL_R + 0.10 * math.sin(a)),
                  (0, math.radians(90), 0)), segs=6)
        bm_cyl(bm, 0.052, 0.020,
               tf((x + sgn * 0.070, 0.155 * math.cos(a + 0.6),
                   WHEEL_R + 0.155 * math.sin(a + 0.6)),
                  (0, math.radians(90), 0)), segs=16)
    bm_finish(bm, name + "Rim", M_RIM, root, math.radians(35))
    return tire


for sx in (1, -1):
    make_wheel("Wheel.%s" % ("R" if sx > 0 else "L"), sx * WHEEL_X)


# --- fenders -----------------------------------------------------------------
def fender_fn(sx):
    def fn(u, v):
        a = math.radians(-12 + u * 204.0)
        r = 0.40
        return (sx * WHEEL_X + (v - 0.5) * 0.30, r * math.cos(a), WHEEL_R + r * math.sin(a))
    return fn


for sx in (1, -1):
    surface("Fender.%s" % ("R" if sx > 0 else "L"), 20, 4, fender_fn(sx),
            M_FRAME, root, thickness=0.012)
    bm = bmesh.new()
    bm_box(bm, (0.16, 0.06, 0.055), tf((sx * WHEEL_X, 0.0, WHEEL_R + 0.415)),
           bevel=0.008, segments=2)
    bm_box(bm, (0.05, 0.06, 0.28), tf((sx * (HX - 0.02), 0.30, DECK + 0.05)),
           bevel=0.006, segments=2)
    bm_finish(bm, "FenderMount.%d" % sx, M_FRAME, root, math.radians(35))

# --- lights, plate, reflectors ----------------------------------------------
bm = bmesh.new()
for sx in (1, -1):
    bm_box(bm, (0.11, 0.05, 0.19), tf((sx * (HX - 0.06), Y1 + 0.055, DECK + 0.10)),
           bevel=0.010, segments=3)
bm_finish(bm, "TailLights", M_RED, root, math.radians(35))

bm = bmesh.new()
bm_box(bm, (0.28, 0.012, 0.15), tf((0.0, Y1 + 0.05, DECK + 0.06)), bevel=0.004, segments=2)
bm_finish(bm, "LicensePlate", M_PLATE, root, math.radians(35))

bm = bmesh.new()
for sx in (1, -1):
    for y in (-0.55, 0.55):
        bm_box(bm, (0.012, 0.10, 0.045), tf((sx * (HX + 0.005), y, DECK + 0.16)),
               bevel=0.004, segments=2)
bm_finish(bm, "Reflectors", M_AMBER, root, math.radians(35))

# --- ground ------------------------------------------------------------------
bm = bmesh.new()
bm_box(bm, (30.0, 30.0, 0.2), tf((0, 0, -0.1)))
bm_finish(bm, "Ground", M_GROUND)

root.rotation_euler = (0, 0, math.radians(20))

# --- lighting and camera -----------------------------------------------------
add_light("Sun", 'SUN', 4.0, (6.0, -7.0, 9.0), (0, 0, 0.5))
add_light("Key", 'AREA', 900.0, (4.0, -4.5, 4.0), (0, 0, 0.6), size=4.0)
add_light("Fill", 'AREA', 250.0, (-5.0, -3.0, 2.5), (0, 0, 0.6), size=6.0)

cd = bpy.data.cameras.new("Camera")
cd.lens = 50.0
cd.clip_start = 0.05
cd.clip_end = 500.0
cam = bpy.data.objects.new("Camera", cd)
link(cam)
cam.location = (3.6, -4.4, 2.05)
cam.rotation_euler = (Vector((0, -0.15, 0.55)) - cam.location).to_track_quat('-Z', 'Y').to_euler()
scene.camera = cam
