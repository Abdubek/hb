"""claude-107 - Telephoto architectural view: office tower with facade fins and plaza."""
import bpy, bmesh, math
from mathutils import Vector, Matrix

R = math.radians

# ------------------------------------------------------------------ helpers
def scene(res=(1200, 1800)):
    bpy.ops.wm.read_factory_settings(use_empty=True)
    sc = bpy.context.scene
    sc.render.resolution_x, sc.render.resolution_y = res
    try:
        sc.render.engine = 'CYCLES'
        sc.cycles.samples = 160
    except Exception:
        pass
    w = bpy.data.worlds.new("World")
    sc.world = w
    w.use_nodes = True
    nt = w.node_tree
    bg = nt.nodes["Background"]
    bg.inputs[1].default_value = 1.0
    sky = nt.nodes.new("ShaderNodeTexSky")
    try:
        sky.sky_type = 'NISHITA'
        sky.sun_elevation = R(34)
        sky.sun_rotation = R(205)
        sky.turbidity = 2.4
        sky.altitude = 60.0
    except Exception:
        pass
    nt.links.new(sky.outputs[0], bg.inputs[0])
    return sc


def mat(name, c, rough=0.5, metal=0.0, trans=0.0, emit=None, es=0.0):
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
    if trans:
        s(["Transmission Weight", "Transmission"], trans)
    if emit is not None:
        s(["Emission Color", "Emission"], (emit[0], emit[1], emit[2], 1.0))
        s(["Emission Strength"], es)
    return m


def put(ob, m):
    if m is not None:
        ob.data.materials.clear()
        ob.data.materials.append(m)
    return ob


def smooth(ob, ang=35):
    for p in ob.data.polygons:
        p.use_smooth = True
    md = ob.modifiers.new("ES", 'EDGE_SPLIT')
    md.split_angle = R(ang)
    md.use_edge_sharp = False


def box(name, size, loc, rot=(0, 0, 0), m=None):
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
    return put(ob, m)


def cyl(name, r, d, loc, rot=(0, 0, 0), v=20, m=None):
    bpy.ops.mesh.primitive_cylinder_add(radius=r, depth=d, vertices=v, location=loc, rotation=rot)
    ob = bpy.context.active_object
    ob.name = name
    put(ob, m)
    smooth(ob)
    return ob


def ico(name, r, loc, sub=2, m=None):
    bpy.ops.mesh.primitive_ico_sphere_add(radius=r, subdivisions=sub, location=loc)
    ob = bpy.context.active_object
    ob.name = name
    put(ob, m)
    smooth(ob, 80)
    return ob


def bm_box(bm, centre, size, rz=0.0):
    mtx = (Matrix.Translation(Vector(centre)) @ Matrix.Rotation(rz, 4, 'Z')
           @ Matrix.Diagonal(Vector((size[0], size[1], size[2], 1.0))))
    bmesh.ops.create_cube(bm, size=1.0, matrix=mtx)


def batch(name, builder, m=None):
    """Build many boxes into a single mesh to keep the object count sane."""
    me = bpy.data.meshes.new(name)
    bm = bmesh.new()
    builder(bm)
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces[:])
    bm.to_mesh(me)
    bm.free()
    ob = bpy.data.objects.new(name, me)
    bpy.context.collection.objects.link(ob)
    return put(ob, m)


def aim(ob, t):
    d = Vector(t) - ob.location
    ob.rotation_euler = d.to_track_quat('-Z', 'Y').to_euler()


def light(name, kind, loc, energy, size=1.0, color=(1, 1, 1), target=None):
    l = bpy.data.lights.new(name, kind)
    l.energy = energy
    l.color = color
    if kind == 'AREA':
        l.size = size
    elif kind == 'SUN':
        l.angle = R(0.6)
    ob = bpy.data.objects.new(name, l)
    ob.location = loc
    bpy.context.collection.objects.link(ob)
    if target is not None:
        aim(ob, target)
    return ob


# ------------------------------------------------------------------ scene
sc = scene()

M = {
    'glass': mat("CurtainWall", (0.10, 0.16, 0.20), 0.06, 0.35),
    'glass2': mat("PodiumGlass", (0.09, 0.14, 0.18), 0.05, 0.25),
    'alu': mat("Aluminium", (0.72, 0.73, 0.75), 0.28, 1.0),
    'alu2': mat("AnodBand", (0.55, 0.56, 0.58), 0.35, 1.0),
    'stone': mat("Stone", (0.68, 0.66, 0.62), 0.55),
    'conc': mat("Concrete", (0.60, 0.59, 0.57), 0.75),
    'paving': mat("Paving", (0.52, 0.51, 0.49), 0.70),
    'paving2': mat("PavingLight", (0.70, 0.69, 0.66), 0.65),
    'dark': mat("DarkMetal", (0.06, 0.06, 0.07), 0.35, 0.8),
    'water': mat("Water", (0.02, 0.05, 0.07), 0.03, 0.0, trans=0.6),
    'bark': mat("Bark", (0.24, 0.19, 0.15), 0.85),
    'leaf': mat("Foliage", (0.16, 0.34, 0.14), 0.70),
    'hedge': mat("Hedge", (0.14, 0.30, 0.13), 0.80),
    'wood': mat("Bench", (0.42, 0.29, 0.17), 0.60),
    'lamp': mat("LampHead", (0.9, 0.9, 0.85), 0.3, emit=(1.0, 0.93, 0.80), es=4.0),
    'ctx': mat("Context", (0.34, 0.35, 0.37), 0.45, 0.2),
}

FH = 3.90                    # typical floor to floor
POD_F = 3
POD_H = POD_F * 4.70         # 14.1 m podium
FLOORS = 32
TOP = POD_H + FLOORS * FH    # ~138.9 m parapet
TX, TY = 15.0, 11.0          # tower half plan (30 x 22)
PX, PY = 21.0, 16.0          # podium half plan

# ---------------------------------------------------------------- tower shell
box("TowerGlass", (TX * 2, TY * 2, TOP - 0.4), (0, 0, (TOP + 0.4) / 2 - 0.2), m=M['glass'])
box("TowerCoreCap", (TX * 2 + 0.5, TY * 2 + 0.5, 1.2), (0, 0, TOP + 0.6), m=M['stone'])

# spandrel bands, one per floor, batched
def bands(bm):
    z = POD_H
    while z < TOP - 1.0:
        bm_box(bm, (0, 0, z), (TX * 2 + 0.55, TY * 2 + 0.55, 0.55))
        z += FH


batch("FloorBands", bands, M['alu2'])

# full height vertical sun-shading fins, batched
FIN_D, FIN_W = 0.62, 0.10
fin_z0, fin_z1 = POD_H + 0.6, TOP - 0.8


def fins(bm):
    h = fin_z1 - fin_z0
    zc = (fin_z0 + fin_z1) / 2
    n = int((TX * 2) // 1.5)
    for i in range(n + 1):
        x = -TX + 0.5 + i * ((TX * 2 - 1.0) / n)
        for sy in (-1, 1):
            bm_box(bm, (x, sy * (TY + FIN_D / 2), zc), (FIN_W, FIN_D, h))
    n = int((TY * 2) // 1.5)
    for i in range(n + 1):
        y = -TY + 0.5 + i * ((TY * 2 - 1.0) / n)
        for sx in (-1, 1):
            bm_box(bm, (sx * (TX + FIN_D / 2), y, zc), (FIN_D, FIN_W, h))
    # fin tip flanges give the facade a finer scale under the telephoto
    for sy in (-1, 1):
        bm_box(bm, (0, sy * (TY + FIN_D), zc), (TX * 2 - 0.6, 0.06, h))
    for sx in (-1, 1):
        bm_box(bm, (sx * (TX + FIN_D), 0, zc), (0.06, TY * 2 - 0.6, h))


batch("FacadeFins", fins, M['alu'])

# corner mullion pilasters
for sx in (-1, 1):
    for sy in (-1, 1):
        box("Corner", (0.5, 0.5, TOP - POD_H),
            (sx * (TX + 0.1), sy * (TY + 0.1), POD_H + (TOP - POD_H) / 2), m=M['alu'])

# ---------------------------------------------------------------- crown
for sx, sy, w, d in ((0, 1, TX * 2 + 1.4, 0.5), (0, -1, TX * 2 + 1.4, 0.5),
                     (1, 0, 0.5, TY * 2 + 1.4), (-1, 0, 0.5, TY * 2 + 1.4)):
    box("Parapet", (w, d, 2.6), (sx * (TX + 0.45), sy * (TY + 0.45), TOP + 2.5), m=M['alu2'])
box("Mech", (17.0, 12.0, 6.4), (1.5, 0, TOP + 4.4), m=M['conc'])
box("MechLouvre", (17.4, 12.4, 0.4), (1.5, 0, TOP + 7.4), m=M['alu'])
for i, (x, y, h, r) in enumerate(((6.0, 3.0, 16.0, 0.22), (7.4, -2.0, 11.0, 0.16))):
    cyl("Mast%d" % i, r, h, (x, y, TOP + 7.6 + h / 2), v=10, m=M['dark'])
for i in range(3):
    box("BMU", (5.0, 1.2, 0.8), (-8.0 + i * 0.0, 0, TOP + 2.2), m=M['dark'])

# ---------------------------------------------------------------- podium
box("Podium", (PX * 2, PY * 2, POD_H), (0, 0, POD_H / 2), m=M['stone'])
box("PodiumGlazing", (PX * 2 - 1.6, PY * 2 - 1.6, 7.6), (0, 0, 4.1), m=M['glass2'])


def pod_bands(bm):
    for i in range(1, POD_F + 1):
        bm_box(bm, (0, 0, i * 4.70), (PX * 2 + 0.4, PY * 2 + 0.4, 0.7))


batch("PodiumBands", pod_bands, M['alu2'])

# colonnade around the podium base
for i in range(9):
    x = -PX + 0.8 + i * ((PX * 2 - 1.6) / 8)
    for sy in (-1, 1):
        cyl("Col", 0.55, 8.0, (x, sy * (PY - 0.4), 4.0), v=14, m=M['stone'])
for i in range(7):
    y = -PY + 0.8 + i * ((PY * 2 - 1.6) / 6)
    for sx in (-1, 1):
        cyl("Col", 0.55, 8.0, (sx * (PX - 0.4), y, 4.0), v=14, m=M['stone'])
box("Canopy", (PX * 2 + 8.0, PY * 2 + 6.0, 0.7), (0, 0, 8.6), m=M['alu2'])
box("CanopyEdge", (PX * 2 + 8.4, PY * 2 + 6.4, 0.18), (0, 0, 8.2), m=M['alu'])
box("Entrance", (11.0, 1.2, 6.6), (0, -PY - 0.6, 3.4), m=M['glass2'])
box("EntrancePortal", (12.4, 1.8, 0.7), (0, -PY - 0.7, 7.1), m=M['alu'])

# ---------------------------------------------------------------- plaza
box("Ground", (600, 600, 0.4), (0, 0, -0.2), m=M['conc'])
box("Plaza", (150.0, 120.0, 0.30), (0, -46.0, 0.15), m=M['paving'])


def paving_grid(bm):
    for i in range(9):
        bm_box(bm, (-64.0 + i * 16.0, -46.0, 0.32), (1.2, 118.0, 0.10))
    for j in range(7):
        bm_box(bm, (0.0, -104.0 + j * 19.0, 0.32), (148.0, 1.2, 0.10))


batch("PavingJoints", paving_grid, M['paving2'])

# entrance steps
for i in range(4):
    box("Step%d" % i, (34.0 - i * 1.5, 3.0, 0.42 + i * 0.02),
        (0, -PY - 3.0 - i * 3.0, 1.55 - i * 0.42), m=M['paving2'])

# reflecting pool
box("PoolWall", (34.0, 14.0, 0.9), (-40.0, -52.0, 0.45), m=M['stone'])
box("PoolWater", (32.6, 12.6, 0.5), (-40.0, -52.0, 0.62), m=M['water'])

# planters with hedges
for i in range(4):
    x = 20.0 + i * 15.0
    box("Planter%d" % i, (11.0, 4.4, 1.0), (x, -44.0, 0.55), m=M['stone'])
    box("Hedge%d" % i, (10.2, 3.6, 1.1), (x, -44.0, 1.35), m=M['hedge'])

# street trees
for i, (x, y) in enumerate([(-58, -30), (-58, -62), (-58, -94), (52, -78), (30, -84),
                            (8, -92), (-14, -92), (-36, -92), (66, -40), (66, -12)]):
    cyl("Trunk%d" % i, 0.22, 5.4, (x, y, 2.7), v=10, m=M['bark'])
    for k, (dz, rr) in enumerate(((5.6, 2.9), (7.2, 2.4), (8.4, 1.5))):
        c = ico("Canopy%d_%d" % (i, k), rr, (x + 0.3 * k, y - 0.2 * k, dz), sub=2, m=M['leaf'])
        c.scale = (1.25, 1.15, 0.85)

# benches, bollards, lamp posts
for i in range(6):
    x = -30.0 + i * 12.0
    box("Bench%d" % i, (4.4, 1.0, 0.14), (x, -70.0, 0.78), m=M['wood'])
    box("BenchBack%d" % i, (4.4, 0.14, 0.5), (x, -70.5, 1.05), m=M['wood'])
    for sx in (-1.7, 1.7):
        box("BenchLeg", (0.2, 0.9, 0.66), (x + sx, -70.0, 0.44), m=M['dark'])
for i in range(14):
    cyl("Bollard%d" % i, 0.13, 1.0, (-58.0 + i * 9.0, -26.0, 0.5), v=10, m=M['dark'])
for i in range(6):
    x = -55.0 + i * 22.0
    cyl("Pole%d" % i, 0.11, 7.0, (x, -60.0, 3.5), v=10, m=M['dark'])
    box("Head%d" % i, (0.9, 0.35, 0.16), (x, -60.0, 7.1), m=M['lamp'])

# background context blocks for the compressed telephoto layering
for i, (x, y, w, d, h) in enumerate([(-96, 58, 40, 34, 62), (86, 46, 46, 38, 48),
                                     (-20, 96, 60, 40, 84), (120, -40, 34, 30, 30)]):
    box("Ctx%d" % i, (w, d, h), (x, y, h / 2), m=M['ctx'])
    box("CtxCap%d" % i, (w + 1.0, d + 1.0, 1.4), (x, y, h + 0.4), m=M['conc'])

# ---------------------------------------------------------------- lighting
sun = light("Sun", 'SUN', (200, -160, 220), 4.2, color=(1.0, 0.95, 0.86))
sun.rotation_euler = (R(52), R(2), R(208))
light("SkyFill", 'AREA', (-140, -220, 160), 90000.0, size=180.0,
      color=(0.72, 0.80, 1.0), target=(0, 0, 70))

# ---------------------------------------------------------------- camera
cd = bpy.data.cameras.new("TeleCam")
cd.lens = 135.0
cd.sensor_fit = 'AUTO'
cd.clip_start = 1.0
cd.clip_end = 6000.0
cd.shift_y = 0.02
cam = bpy.data.objects.new("TeleCam", cd)
cam.location = (330.0, -505.0, 96.0)
bpy.context.collection.objects.link(cam)
aim(cam, (0.0, -8.0, 74.0))
sc.camera = cam
