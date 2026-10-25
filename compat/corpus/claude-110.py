"""claude-110 - Turntable display scene for a pair of sneakers built from simple modeled forms."""
import bpy, bmesh, math
from mathutils import Vector, Matrix

R = math.radians

# ------------------------------------------------------------------ helpers
def scene(res=(1500, 1500)):
    bpy.ops.wm.read_factory_settings(use_empty=True)
    sc = bpy.context.scene
    sc.render.resolution_x, sc.render.resolution_y = res
    sc.frame_start, sc.frame_end = 1, 120
    try:
        sc.render.engine = 'CYCLES'
        sc.cycles.samples = 160
    except Exception:
        pass
    w = bpy.data.worlds.new("World")
    sc.world = w
    w.use_nodes = True
    bg = w.node_tree.nodes["Background"]
    bg.inputs[0].default_value = (0.05, 0.055, 0.065, 1.0)
    bg.inputs[1].default_value = 0.35
    return sc


def mat(name, c, rough=0.5, metal=0.0, emit=None, es=0.0):
    m = bpy.data.materials.new(name)
    m.use_nodes = True
    b = m.node_tree.nodes["Principled BSDF"]

    def s(keys, v):
        for k in keys:
            if k in b.inputs:
                b.inputs[k].default_value = v
                return
    s(["Base Color"], (c[0], c[1], c[2], 1.0))
    s(["Roughness"], rough)
    s(["Metallic"], metal)
    if emit is not None:
        s(["Emission Color", "Emission"], (emit[0], emit[1], emit[2], 1.0))
        s(["Emission Strength"], es)
    return m


def put(ob, m):
    if m is not None:
        ob.data.materials.clear()
        ob.data.materials.append(m)
    return ob


def smooth(ob, ang=40):
    for p in ob.data.polygons:
        p.use_smooth = True
    md = ob.modifiers.new("ES", 'EDGE_SPLIT')
    md.split_angle = R(ang)
    md.use_edge_sharp = False


def bev(ob, w, seg=2):
    b = ob.modifiers.new("Bevel", 'BEVEL')
    b.width = w
    b.segments = seg
    b.limit_method = 'ANGLE'
    b.angle_limit = R(45)
    return b


def box(name, size, loc, rot=(0, 0, 0), m=None, b=0.0, seg=2):
    me = bpy.data.meshes.new(name)
    bm = bmesh.new()
    bmesh.ops.create_cube(bm, size=1.0)
    bmesh.ops.scale(bm, vec=Vector(size), verts=bm.verts)
    bm.to_mesh(me)
    bm.free()
    ob = bpy.data.objects.new(name, me)
    ob.location = loc
    ob.rotation_euler = rot
    bpy.context.collection.objects.link(ob)
    put(ob, m)
    if b > 0:
        bev(ob, b, seg)
    return ob


def cyl(name, r, d, loc, rot=(0, 0, 0), v=32, m=None):
    bpy.ops.mesh.primitive_cylinder_add(radius=r, depth=d, vertices=v, location=loc, rotation=rot)
    ob = bpy.context.active_object
    ob.name = name
    put(ob, m)
    smooth(ob)
    return ob


def torus(name, R1, R2, loc, rot=(0, 0, 0), ms=40, mn=12, m=None):
    bpy.ops.mesh.primitive_torus_add(major_radius=R1, minor_radius=R2, major_segments=ms,
                                     minor_segments=mn, location=loc, rotation=rot)
    ob = bpy.context.active_object
    ob.name = name
    put(ob, m)
    smooth(ob, 80)
    return ob


def empty(name, loc=(0, 0, 0), rot=(0, 0, 0)):
    ob = bpy.data.objects.new(name, None)
    ob.location = loc
    ob.rotation_euler = rot
    ob.empty_display_size = 0.06
    bpy.context.collection.objects.link(ob)
    return ob


def aim(ob, t):
    d = Vector(t) - ob.location
    ob.rotation_euler = d.to_track_quat('-Z', 'Y').to_euler()


def light(name, kind, loc, energy, size=1.0, color=(1, 1, 1), target=None, shape=None, sy=None):
    l = bpy.data.lights.new(name, kind)
    l.energy = energy
    l.color = color
    if kind == 'AREA':
        l.size = size
        if shape:
            l.shape = shape
            l.size_y = sy or size
    ob = bpy.data.objects.new(name, l)
    ob.location = loc
    bpy.context.collection.objects.link(ob)
    if target is not None:
        aim(ob, target)
    return ob


def loft(name, rings, m=None, caps=True, hole=None, thick=0.0, b=0.0):
    me = bpy.data.meshes.new(name)
    bm = bmesh.new()
    vr = [[bm.verts.new(p) for p in r] for r in rings]
    n = len(rings[0])
    for i in range(len(rings) - 1):
        a, c = vr[i], vr[i + 1]
        for j in range(n):
            k = (j + 1) % n
            bm.faces.new((a[j], a[k], c[k], c[j]))
    if caps:
        bm.faces.new(list(reversed(vr[0])))
        bm.faces.new(vr[-1])
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces[:])
    if hole is not None:
        dead = [f for f in bm.faces if hole(f.calc_center_median())]
        if dead:
            bmesh.ops.delete(bm, geom=dead, context='FACES')
    bm.to_mesh(me)
    bm.free()
    ob = bpy.data.objects.new(name, me)
    bpy.context.collection.objects.link(ob)
    put(ob, m)
    if thick > 0:
        s = ob.modifiers.new("Solid", 'SOLIDIFY')
        s.thickness = thick
        s.offset = 0.0
    if b > 0:
        bev(ob, b)
    smooth(ob, 46)
    return ob


# ------------------------------------------------------------------ scene
sc = scene()

M = {
    'canvas': mat("Canvas", (0.90, 0.89, 0.85), 0.72),
    'panel': mat("SidePanel", (0.13, 0.28, 0.52), 0.62),
    'mid': mat("Midsole", (0.96, 0.95, 0.92), 0.48),
    'gum': mat("GumOutsole", (0.62, 0.40, 0.19), 0.55),
    'rubber': mat("ToeRubber", (0.94, 0.93, 0.90), 0.42),
    'lace': mat("Lace", (0.97, 0.96, 0.93), 0.85),
    'eyelet': mat("Eyelet", (0.78, 0.79, 0.81), 0.28, 1.0),
    'collar': mat("CollarFoam", (0.86, 0.85, 0.81), 0.80),
    'tongue': mat("Tongue", (0.88, 0.87, 0.83), 0.78),
    'heeltab': mat("HeelTab", (0.13, 0.28, 0.52), 0.60),
    'plate': mat("Turntable", (0.045, 0.048, 0.055), 0.18),
    'base': mat("BaseRing", (0.55, 0.56, 0.58), 0.30, 1.0),
    'cyc': mat("Cyclorama", (0.19, 0.20, 0.23), 0.85),
}

# ------------------------------------------------------------- shoe profiles
OUT = [(0.000, 0.020), (0.010, 0.028), (0.025, 0.036), (0.045, 0.041), (0.075, 0.041),
       (0.110, 0.039), (0.145, 0.041), (0.180, 0.045), (0.210, 0.046), (0.240, 0.044),
       (0.265, 0.040), (0.285, 0.032), (0.300, 0.017)]
TOP = [(0.020, 0.100), (0.045, 0.112), (0.075, 0.108), (0.105, 0.100), (0.140, 0.092),
       (0.180, 0.088), (0.220, 0.083), (0.252, 0.075), (0.282, 0.062)]


def interp(tab, x):
    if x <= tab[0][0]:
        return tab[0][1]
    if x >= tab[-1][0]:
        return tab[-1][1]
    for i in range(len(tab) - 1):
        x0, y0 = tab[i]
        x1, y1 = tab[i + 1]
        if x0 <= x <= x1:
            return y0 + (y1 - y0) * (x - x0) / (x1 - x0)
    return tab[-1][1]


def hw(x):
    return interp(OUT, x)


def topz(x):
    return interp(TOP, x)


def spring(x):
    """Toe spring and a touch of heel rocker."""
    return 0.013 * max(0.0, (x - 0.235) / 0.065) ** 2 + 0.007 * max(0.0, (0.030 - x) / 0.030) ** 2


def sole_ring(scale, z):
    pts = [(x, w * scale, z + spring(x)) for x, w in OUT]
    pts += [(x, -w * scale, z + spring(x)) for x, w in reversed(OUT[1:-1])]
    return pts


def upper_ring(x, n=24, e=2.55):
    zt = topz(x)
    zb = 0.032
    zc = (zt + zb) / 2.0
    hz = (zt - zb) / 2.0
    wy = hw(x) * 0.965
    if x < 0.035:
        wy *= 0.80
    if x > 0.265:
        wy *= 0.78
    p = 2.0 / e
    ring = []
    for j in range(n):
        a = 2.0 * math.pi * j / n
        ca, sa = math.cos(a), math.sin(a)
        y = wy * math.copysign(abs(ca) ** p, ca)
        z = zc + hz * math.copysign(abs(sa) ** p, sa)
        ring.append((x, y, z + spring(x) * 0.6))
    return ring


def rod(name, p1, p2, r, m=None, v=10):
    p1, p2 = Vector(p1), Vector(p2)
    d = p2 - p1
    ob = cyl(name, r, d.length, (p1 + p2) / 2.0, v=v, m=m)
    ob.rotation_euler = d.to_track_quat('Z', 'Y').to_euler()
    return ob


def stripe(name, yv, m):
    top, bot = [], []
    for i in range(10):
        t = i / 9.0
        x = 0.092 + 0.140 * t
        zc = 0.050 + 0.030 * t * t
        ht = 0.013 - 0.007 * t
        top.append((x, yv, zc + ht))
        bot.append((x, yv, zc - ht))
    me = bpy.data.meshes.new(name)
    bm = bmesh.new()
    vs = [bm.verts.new(p) for p in top + list(reversed(bot))]
    bm.faces.new(vs)
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces[:])
    bm.to_mesh(me)
    bm.free()
    ob = bpy.data.objects.new(name, me)
    bpy.context.collection.objects.link(ob)
    put(ob, m)
    s = ob.modifiers.new("Solid", 'SOLIDIFY')
    s.thickness = 0.004
    s.offset = 0.0
    return ob


def make_sneaker():
    """Returns the list of objects forming one (right) shoe, origin at heel centre."""
    parts = []

    # outsole and midsole, lofted from the footprint outline
    parts.append(loft("Outsole", [sole_ring(1.0, 0.000), sole_ring(1.005, 0.009),
                                  sole_ring(0.995, 0.017)], m=M['gum'], b=0.004))
    parts.append(loft("Midsole", [sole_ring(0.995, 0.015), sole_ring(1.012, 0.030),
                                  sole_ring(0.985, 0.044), sole_ring(0.945, 0.053)],
                      m=M['mid'], b=0.005))
    parts.append(loft("Foxing", [sole_ring(1.010, 0.019), sole_ring(1.016, 0.026),
                                 sole_ring(1.008, 0.033)], m=M['rubber'], b=0.003))

    # tread ribs, kept inside the outline
    for i in range(11):
        x = 0.030 + i * 0.024
        w = hw(x) * 1.62
        parts.append(box("Tread%d" % i, (0.011, w, 0.006), (x, 0, 0.0 + spring(x) * 0.9),
                         m=M['gum'], b=0.002))
    parts.append(cyl("HeelPad", 0.026, 0.007, (0.030, 0, 0.001), v=24, m=M['gum']))

    # lofted upper with the throat opening cut out and solidified
    xs = [0.020, 0.032, 0.048, 0.068, 0.090, 0.112, 0.135, 0.158, 0.182, 0.205,
          0.228, 0.248, 0.266, 0.280]
    rings = [upper_ring(x) for x in xs]

    def hole(c):
        return (0.032 < c.x < 0.203) and abs(c.y) < 0.027 and c.z > topz(c.x) - 0.021

    parts.append(loft("Upper", rings, m=M['canvas'], hole=hole, thick=0.005))

    # collar foam ring around the opening
    col = torus("Collar", 0.052, 0.0085, (0.117, 0, 0.100), rot=(0, R(-7), 0), m=M['collar'])
    col.scale = (1.68, 0.60, 0.95)
    parts.append(col)

    # tongue under the lacing
    parts.append(box("Tongue", (0.082, 0.050, 0.009), (0.180, 0, 0.089), rot=(0, R(-16), 0),
                     m=M['tongue'], b=0.004))
    parts.append(box("TongueTip", (0.020, 0.044, 0.008), (0.140, 0, 0.098), rot=(0, R(-4), 0),
                     m=M['tongue'], b=0.003))

    # eyelets and crossed laces
    ex = [0.150, 0.170, 0.190, 0.208]
    pts = {}
    for i, x in enumerate(ex):
        z = topz(x) - 0.005
        for sy in (-1, 1):
            p = (x, sy * 0.028, z)
            pts[(i, sy)] = p
            parts.append(torus("Eyelet%d%d" % (i, sy), 0.0038, 0.0012, p, m=M['eyelet'],
                               ms=16, mn=8))
    for i in range(len(ex) - 1):
        parts.append(rod("Lace%dA" % i, pts[(i, -1)], pts[(i + 1, 1)], 0.0026, m=M['lace']))
        parts.append(rod("Lace%dB" % i, pts[(i, 1)], pts[(i + 1, -1)], 0.0026, m=M['lace']))
    parts.append(rod("LaceEndL", pts[(0, -1)], (0.126, -0.020, 0.086), 0.0026, m=M['lace']))
    parts.append(rod("LaceEndR", pts[(0, 1)], (0.126, 0.020, 0.086), 0.0026, m=M['lace']))
    parts.append(rod("LaceToe", pts[(3, -1)], pts[(3, 1)], 0.0026, m=M['lace']))

    # side panels, toe bumper, heel counter and pull tab
    for sy in (-1, 1):
        parts.append(stripe("Stripe%d" % sy, sy * 0.0425, M['panel']))
    parts.append(box("ToeBumper", (0.046, 0.074, 0.030), (0.260, 0, 0.055), rot=(0, R(-8), 0),
                     m=M['rubber'], b=0.013, seg=3))
    parts.append(box("HeelCounter", (0.030, 0.070, 0.048), (0.033, 0, 0.070), m=M['panel'],
                     b=0.014, seg=3))
    parts.append(box("HeelTab", (0.011, 0.028, 0.020), (0.021, 0, 0.104), m=M['heeltab'], b=0.005))
    parts.append(box("Logo", (0.026, 0.006, 0.010), (0.150, 0.0435, 0.070), m=M['panel'], b=0.002))
    return parts


# ------------------------------------------------------------- turntable rig
TABLE_H = 0.052
spin = empty("TurntableSpin", (0, 0, 0))

plate = cyl("Platform", 0.46, TABLE_H, (0, 0, TABLE_H / 2), v=64, m=M['plate'])
bev(plate, 0.008, 3)
plate.parent = spin
ring = torus("PlatformRing", 0.455, 0.006, (0, 0, TABLE_H), ms=64, mn=10, m=M['base'])
ring.parent = spin
base = cyl("PlatformBase", 0.50, 0.014, (0, 0, 0.007), v=64, m=M['base'])
base.parent = spin

# right shoe
parts = make_sneaker()
shoe_r = empty("Sneaker_R", (-0.10, -0.075, TABLE_H), (0, 0, R(-14)))
for ob in parts:
    ob.parent = shoe_r
    ob.matrix_parent_inverse = Matrix.Identity(4)
shoe_r.parent = spin

# left shoe: same mesh data, mirrored through a negatively scaled parent
shoe_l = empty("Sneaker_L", (-0.05, 0.085, TABLE_H), (0, 0, R(24)))
shoe_l.scale = (1.0, -1.0, 1.0)
for ob in parts:
    c = ob.copy()
    c.name = ob.name + "_L"
    bpy.context.collection.objects.link(c)
    c.parent = shoe_l
    c.matrix_parent_inverse = Matrix.Identity(4)
shoe_l.parent = spin

# turntable animation: one full revolution over the shot
spin.rotation_euler = (0, 0, 0)
spin.keyframe_insert("rotation_euler", frame=1)
spin.rotation_euler = (0, 0, 2.0 * math.pi)
spin.keyframe_insert("rotation_euler", frame=120)
try:
    for fc in spin.animation_data.action.fcurves:
        fc.extrapolation = 'LINEAR'
        for kp in fc.keyframe_points:
            kp.interpolation = 'LINEAR'
except Exception:
    pass

# ------------------------------------------------------------- cyclorama backdrop
prof = [(-1.60, 0.0), (0.30, 0.0), (0.68, 0.03), (0.94, 0.20), (1.08, 0.52),
        (1.15, 1.00), (1.18, 1.90)]
me = bpy.data.meshes.new("Cyclorama")
bm = bmesh.new()
rowa = [bm.verts.new((-2.60, y, z)) for y, z in prof]
rowb = [bm.verts.new((2.60, y, z)) for y, z in prof]
for i in range(len(prof) - 1):
    bm.faces.new((rowa[i], rowa[i + 1], rowb[i + 1], rowb[i]))
bmesh.ops.recalc_face_normals(bm, faces=bm.faces[:])
bm.to_mesh(me)
bm.free()
cyc = bpy.data.objects.new("Cyclorama", me)
bpy.context.collection.objects.link(cyc)
put(cyc, M['cyc'])
smooth(cyc, 60)

# ------------------------------------------------------------- studio lighting
light("Key", 'AREA', (-0.95, -0.85, 1.25), 320.0, size=1.20, color=(1.0, 0.99, 0.97),
      target=(0.0, 0.0, 0.10))
light("Fill", 'AREA', (1.05, -0.70, 0.55), 70.0, size=0.90, color=(0.90, 0.94, 1.0),
      target=(0.0, 0.0, 0.08))
light("RimL", 'AREA', (-0.55, 0.95, 0.85), 140.0, size=0.35, color=(0.78, 0.86, 1.0),
      target=(0.0, 0.0, 0.09), shape='RECTANGLE', sy=0.90)
light("RimR", 'AREA', (0.70, 0.90, 0.80), 120.0, size=0.30, color=(1.0, 0.90, 0.78),
      target=(0.0, 0.0, 0.09), shape='RECTANGLE', sy=0.80)
light("TopSoft", 'AREA', (0.0, 0.05, 1.60), 180.0, size=1.60, color=(1.0, 1.0, 1.0),
      target=(0.0, 0.0, 0.06))

# ------------------------------------------------------------- camera
cd = bpy.data.cameras.new("TurntableCam")
cd.lens = 85.0
cd.clip_start = 0.05
cd.clip_end = 50.0
cd.dof.use_dof = True
cd.dof.aperture_fstop = 4.5
cd.dof.focus_distance = 1.20
cam = bpy.data.objects.new("TurntableCam", cd)
cam.location = (0.10, -1.18, 0.42)
bpy.context.collection.objects.link(cam)
aim(cam, (0.0, 0.0, 0.115))
sc.camera = cam
sc.frame_set(1)
