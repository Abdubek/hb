"""claude-106 - Isometric cutaway studio apartment with kitchenette and sleeping area."""
import bpy, bmesh, math
from mathutils import Vector, Matrix

R = math.radians

# ------------------------------------------------------------------ helpers
def scene(res=(1800, 1350), bgc=(0.52, 0.58, 0.66), bgs=0.7):
    bpy.ops.wm.read_factory_settings(use_empty=True)
    sc = bpy.context.scene
    sc.render.resolution_x, sc.render.resolution_y = res
    try:
        sc.render.engine = 'CYCLES'
        sc.cycles.samples = 128
    except Exception:
        pass
    w = bpy.data.worlds.new("World")
    sc.world = w
    w.use_nodes = True
    bg = w.node_tree.nodes["Background"]
    bg.inputs[0].default_value = (bgc[0], bgc[1], bgc[2], 1.0)
    bg.inputs[1].default_value = bgs
    return sc


def mat(name, c, rough=0.5, metal=0.0, emit=None, es=0.0, trans=0.0, alpha=1.0):
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
    if alpha < 1.0:
        s(["Alpha"], alpha)
        try:
            m.blend_method = 'BLEND'
        except Exception:
            pass
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


def bev(ob, w, seg=2):
    b = ob.modifiers.new("Bevel", 'BEVEL')
    b.width = w
    b.segments = seg
    b.limit_method = 'ANGLE'
    b.angle_limit = R(50)


def box(name, size, loc, rot=(0, 0, 0), m=None, b=0.0):
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
        bev(ob, b)
    return ob


def cyl(name, r, d, loc, rot=(0, 0, 0), v=24, m=None, sm=True):
    bpy.ops.mesh.primitive_cylinder_add(radius=r, depth=d, vertices=v, location=loc, rotation=rot)
    ob = bpy.context.active_object
    ob.name = name
    put(ob, m)
    if sm:
        smooth(ob)
    return ob


def cone(name, r1, r2, d, loc, rot=(0, 0, 0), v=24, m=None):
    bpy.ops.mesh.primitive_cone_add(radius1=r1, radius2=r2, depth=d, vertices=v,
                                    location=loc, rotation=rot)
    ob = bpy.context.active_object
    ob.name = name
    put(ob, m)
    smooth(ob)
    return ob


def ball(name, r, loc, seg=24, ring=12, m=None):
    bpy.ops.mesh.primitive_uv_sphere_add(radius=r, segments=seg, ring_count=ring, location=loc)
    ob = bpy.context.active_object
    ob.name = name
    put(ob, m)
    smooth(ob, 80)
    return ob


def torus(name, R1, R2, loc, rot=(0, 0, 0), ms=28, mn=10, m=None):
    bpy.ops.mesh.primitive_torus_add(major_radius=R1, minor_radius=R2, major_segments=ms,
                                     minor_segments=mn, location=loc, rotation=rot)
    ob = bpy.context.active_object
    ob.name = name
    put(ob, m)
    smooth(ob, 80)
    return ob


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
        l.angle = R(2.5)
    else:
        l.shadow_soft_size = size
    ob = bpy.data.objects.new(name, l)
    ob.location = loc
    bpy.context.collection.objects.link(ob)
    if target is not None:
        aim(ob, target)
    return ob


# ------------------------------------------------------------------ scene
sc = scene()

M = {
    'floor': mat("Floor", (0.44, 0.29, 0.17), 0.35),
    'wall': mat("Wall", (0.88, 0.86, 0.82), 0.8),
    'accent': mat("WallAccent", (0.55, 0.60, 0.60), 0.85),
    'trim': mat("Trim", (0.95, 0.95, 0.93), 0.5),
    'slab': mat("Slab", (0.58, 0.56, 0.53), 0.85),
    'cab': mat("Cabinet", (0.17, 0.30, 0.32), 0.45),
    'cabup': mat("CabinetUpper", (0.93, 0.91, 0.87), 0.45),
    'stone': mat("Counter", (0.86, 0.85, 0.81), 0.25),
    'tile': mat("Tile", (0.80, 0.84, 0.83), 0.2),
    'steel': mat("Steel", (0.74, 0.75, 0.77), 0.25, 1.0),
    'dark': mat("DarkGlass", (0.035, 0.035, 0.045), 0.12),
    'wood': mat("Wood", (0.56, 0.38, 0.22), 0.4),
    'fabric': mat("Sofa", (0.33, 0.40, 0.50), 0.9),
    'linen': mat("Linen", (0.91, 0.90, 0.86), 0.9),
    'duvet': mat("Duvet", (0.78, 0.74, 0.66), 0.95),
    'rug': mat("Rug", (0.73, 0.56, 0.43), 0.95),
    'glass': mat("Glass", (0.85, 0.9, 0.95), 0.04, trans=1.0),
    'leaf': mat("Leaf", (0.19, 0.42, 0.20), 0.6),
    'pot': mat("Pot", (0.72, 0.45, 0.32), 0.6),
    'shade': mat("LampShade", (1.0, 0.92, 0.78), 0.4, emit=(1.0, 0.84, 0.60), es=7.0),
    'brass': mat("Brass", (0.72, 0.58, 0.32), 0.3, 1.0),
    'paper': mat("Paper", (0.95, 0.94, 0.90), 0.7),
    'book': mat("Book", (0.52, 0.20, 0.18), 0.7),
    'art': mat("Art", (0.86, 0.80, 0.70), 0.6),
}

WH = 2.70          # wall height
T = 0.12           # wall thickness
X0, X1 = -3.0, 3.0
Y0, Y1 = -2.10, 2.10

# floor slab (extends under the two retained walls)
box("FloorSlab", (X1 - X0 + T, Y1 - Y0 + T, 0.18),
    ((X0 + X1 - T) / 2, (Y0 + Y1 + T) / 2, -0.09), m=M['slab'])
box("FloorBoards", (X1 - X0, Y1 - Y0, 0.02), ((X0 + X1) / 2, (Y0 + Y1) / 2, 0.01), m=M['floor'])

# --- back wall (+Y) built as four segments around the window opening
WX0, WX1, WZ0, WZ1 = -0.15, 1.25, 0.95, 2.15
seg = [((X0 - T, WX0), (0.0, WH)),
       ((WX1, X1), (0.0, WH)),
       ((WX0, WX1), (0.0, WZ0)),
       ((WX0, WX1), (WZ1, WH))]
for i, ((ax, bx), (az, bz)) in enumerate(seg):
    box("BackWall%d" % i, (bx - ax, T, bz - az),
        ((ax + bx) / 2, Y1 + T / 2, (az + bz) / 2), m=M['wall'])
# accent paint on interior face of back wall behind the bed
box("AccentPanel", (1.7, 0.01, WH - 0.02), (2.05, Y1 - 0.005, WH / 2), m=M['accent'])

# window frame + glass
box("WinGlass", (WX1 - WX0 - 0.06, 0.012, WZ1 - WZ0 - 0.06),
    ((WX0 + WX1) / 2, Y1 + T / 2, (WZ0 + WZ1) / 2), m=M['glass'])
for (sx, sy, sz, lx, ly, lz) in [
        (WX1 - WX0, T + 0.04, 0.06, (WX0 + WX1) / 2, Y1 + T / 2, WZ0 + 0.03),
        (WX1 - WX0, T + 0.04, 0.06, (WX0 + WX1) / 2, Y1 + T / 2, WZ1 - 0.03),
        (0.06, T + 0.04, WZ1 - WZ0, WX0 + 0.03, Y1 + T / 2, (WZ0 + WZ1) / 2),
        (0.06, T + 0.04, WZ1 - WZ0, WX1 - 0.03, Y1 + T / 2, (WZ0 + WZ1) / 2),
        (0.05, T + 0.04, WZ1 - WZ0, (WX0 + WX1) / 2, Y1 + T / 2, (WZ0 + WZ1) / 2)]:
    box("WinFrame", (sx, sy, sz), (lx, ly, lz), m=M['trim'])
box("WinSill", (WX1 - WX0 + 0.14, 0.22, 0.04), ((WX0 + WX1) / 2, Y1 - 0.05, WZ0 - 0.02), m=M['trim'])

# --- left wall (-X)
box("LeftWall", (T, Y1 - Y0 + T, WH), (X0 - T / 2, (Y0 + Y1 + T) / 2, WH / 2), m=M['wall'])

# baseboards
box("BaseB", (X1 - X0, 0.03, 0.10), ((X0 + X1) / 2, Y1 - 0.015, 0.05), m=M['trim'])
box("BaseL", (0.03, Y1 - Y0, 0.10), (X0 + 0.015, (Y0 + Y1) / 2, 0.05), m=M['trim'])

# ------------------------------------------------------------- kitchenette
KX0, KX1 = -2.90, -1.10
KY = Y1 - 0.30                     # centre line of a 600 deep run
box("Plinth", (KX1 - KX0, 0.52, 0.09), ((KX0 + KX1) / 2, KY + 0.02, 0.045), m=M['dark'])
box("BaseCab", (KX1 - KX0, 0.60, 0.79), ((KX0 + KX1) / 2, KY, 0.485), m=M['cab'])
box("Worktop", (KX1 - KX0 + 0.08, 0.66, 0.04), ((KX0 + KX1) / 2, KY - 0.02, 0.90), m=M['stone'])
box("Backsplash", (KX1 - KX0 + 0.08, 0.02, 0.58), ((KX0 + KX1) / 2, Y1 - 0.012, 1.21), m=M['tile'])

for i in range(3):
    dx = KX0 + 0.31 + i * 0.585
    box("CabDoor%d" % i, (0.55, 0.02, 0.70), (dx, KY - 0.31, 0.49), m=M['cab'], b=0.006)
    cyl("CabPull%d" % i, 0.008, 0.16, (dx, KY - 0.33, 0.79), rot=(0, R(90), 0), v=10, m=M['brass'])

# inset sink + mixer tap
box("SinkRim", (0.56, 0.46, 0.02), (-2.42, KY - 0.02, 0.915), m=M['steel'], b=0.008)
box("SinkBasin", (0.46, 0.36, 0.17), (-2.42, KY - 0.02, 0.845), m=M['steel'])
cyl("TapBody", 0.018, 0.30, (-2.42, KY + 0.24, 1.06), v=16, m=M['steel'])
torus("TapBend", 0.055, 0.018, (-2.42, KY + 0.185, 1.21), rot=(R(90), 0, 0), m=M['steel'])
cyl("TapSpout", 0.014, 0.05, (-2.42, KY + 0.13, 1.19), v=12, m=M['steel'])
cyl("TapLever", 0.010, 0.10, (-2.34, KY + 0.24, 1.20), rot=(0, R(70), 0), v=10, m=M['steel'])

# hob
box("Hob", (0.56, 0.48, 0.014), (-1.52, KY - 0.02, 0.927), m=M['dark'], b=0.004)
for sx, sy, rr in [(-0.13, 0.11, 0.075), (0.13, 0.11, 0.055), (-0.13, -0.11, 0.055), (0.13, -0.11, 0.075)]:
    torus("Burner", rr, 0.005, (-1.52 + sx, KY - 0.02 + sy, 0.936), m=M['steel'], ms=24, mn=8)

# upper cabinets and open shelves
box("UpperCab", (1.10, 0.34, 0.72), (-2.33, Y1 - 0.17, 1.86), m=M['cabup'], b=0.008)
for i in range(2):
    cyl("UpPull%d" % i, 0.007, 0.14, (-2.61 + i * 0.56, Y1 - 0.35, 1.60), rot=(0, R(90), 0), v=10, m=M['brass'])
for i, z in enumerate((1.55, 1.92)):
    box("Shelf%d" % i, (0.78, 0.26, 0.03), (-1.42, Y1 - 0.13, z), m=M['wood'])
    for j in range(3):
        cyl("Jar%d%d" % (i, j), 0.045, 0.13, (-1.70 + j * 0.28, Y1 - 0.13, z + 0.08), v=16,
            m=M['paper'] if j % 2 else M['pot'])

# fridge
box("Fridge", (0.68, 0.66, 1.78), (-0.72, Y1 - 0.33, 0.89), m=M['steel'], b=0.012)
box("FridgeSplit", (0.70, 0.02, 0.012), (-0.72, Y1 - 0.665, 1.20), m=M['dark'])
for z in (0.95, 1.45):
    cyl("FridgeHandle", 0.010, 0.34, (-0.42, Y1 - 0.68, z), rot=(R(90), 0, 0), v=10, m=M['steel'])

# ------------------------------------------------------------- sleeping area
BX, BY = 2.05, 1.05                 # bed centre
box("BedFrame", (1.42, 2.02, 0.26), (BX, BY, 0.13), m=M['wood'], b=0.012)
box("Headboard", (1.46, 0.08, 0.85), (BX, Y1 - 0.05, 0.52), m=M['fabric'], b=0.02)
box("Mattress", (1.36, 1.96, 0.22), (BX, BY, 0.37), m=M['linen'], b=0.05)
d = box("Duvet", (1.44, 1.35, 0.16), (BX, BY - 0.32, 0.53), m=M['duvet'], b=0.06)
d.modifiers.new("Sub", 'SUBSURF').levels = 1
box("DuvetFold", (1.44, 0.24, 0.10), (BX, BY + 0.42, 0.52), m=M['linen'], b=0.04)
for sx in (-0.32, 0.32):
    box("Pillow", (0.60, 0.34, 0.14), (BX + sx, BY + 0.78, 0.53), rot=(0, 0, R(4 if sx > 0 else -4)),
        m=M['linen'], b=0.055)
box("Throw", (1.30, 0.42, 0.05), (BX, BY - 0.76, 0.60), m=M['fabric'], b=0.02)

# nightstand + bedside lamp + book
box("Nightstand", (0.40, 0.36, 0.50), (1.12, Y1 - 0.22, 0.25), m=M['wood'], b=0.01)
box("NsDrawer", (0.34, 0.02, 0.14), (1.12, Y1 - 0.41, 0.36), m=M['cabup'], b=0.005)
cyl("LampBase", 0.055, 0.03, (1.12, Y1 - 0.22, 0.515), v=20, m=M['brass'])
cyl("LampStem", 0.012, 0.20, (1.12, Y1 - 0.22, 0.63), v=10, m=M['brass'])
cone("LampShade", 0.10, 0.065, 0.15, (1.12, Y1 - 0.22, 0.80), v=24, m=M['shade'])
light("BedLampLight", 'POINT', (1.12, Y1 - 0.22, 0.80), 12.0, size=0.06, color=(1.0, 0.82, 0.60))
box("Book", (0.14, 0.20, 0.03), (1.14, Y1 - 0.20, 0.515), rot=(0, 0, R(12)), m=M['book'], b=0.004)

# rug under the bed
box("BedRug", (2.00, 1.40, 0.014), (1.95, -0.30, 0.018), m=M['rug'], b=0.004)

# ------------------------------------------------------------- living corner
box("SofaBase", (1.70, 0.80, 0.30), (-1.55, -1.55, 0.20), m=M['fabric'], b=0.03)
box("SofaBack", (1.70, 0.20, 0.50), (-1.55, -1.85, 0.55), m=M['fabric'], b=0.04)
for sx in (-0.80, 0.80):
    box("SofaArm", (0.16, 0.80, 0.26), (-1.55 + sx, -1.55, 0.48), m=M['fabric'], b=0.05)
for sx in (-0.42, 0.42):
    box("SofaCushion", (0.72, 0.70, 0.16), (-1.55 + sx, -1.52, 0.42), m=M['linen'], b=0.05)
for sx in (-0.55, 0.55):
    box("SofaPillow", (0.34, 0.14, 0.32), (-1.55 + sx, -1.74, 0.62), rot=(R(10), 0, 0), m=M['rug'], b=0.05)
for sx in (-0.75, 0.75):
    for sy in (-0.32, 0.32):
        cyl("SofaLeg", 0.022, 0.10, (-1.55 + sx, -1.55 + sy, 0.05), v=10, m=M['wood'])
box("LivingRug", (2.30, 1.60, 0.012), (-1.45, -0.72, 0.017), m=M['rug'], b=0.004)
cyl("CoffeeTop", 0.34, 0.04, (-1.45, -0.62, 0.40), v=28, m=M['wood'])
cyl("CoffeeCol", 0.05, 0.36, (-1.45, -0.62, 0.20), v=14, m=M['steel'])
cyl("CoffeeFoot", 0.20, 0.02, (-1.45, -0.62, 0.02), v=24, m=M['steel'])
cyl("Mug", 0.04, 0.09, (-1.36, -0.55, 0.465), v=16, m=M['paper'])
torus("MugHandle", 0.028, 0.006, (-1.31, -0.55, 0.465), rot=(R(90), 0, 0), m=M['paper'], ms=20, mn=8)
for i in range(3):
    box("CoffeeBook%d" % i, (0.22, 0.16, 0.025), (-1.56, -0.70, 0.435 + i * 0.026),
        rot=(0, 0, R(-6 + i * 5)), m=[M['book'], M['cab'], M['paper']][i], b=0.004)

# bookshelf against the left wall
box("ShelfCase", (0.32, 1.20, 1.62), (X0 + 0.17, -1.00, 0.81), m=M['wood'], b=0.008)
for i in range(4):
    box("ShelfBoard%d" % i, (0.28, 1.14, 0.026), (X0 + 0.17, -1.00, 0.36 + i * 0.40), m=M['cabup'])
    for j in range(4):
        box("Vol%d%d" % (i, j), (0.16, 0.05 + 0.03 * (j % 2), 0.24),
            (X0 + 0.17, -1.50 + j * 0.14, 0.50 + i * 0.40),
            m=[M['book'], M['cab'], M['fabric'], M['paper']][j], b=0.003)

# framed art on the left wall
for i, (yy, zz, w, h) in enumerate([(-0.05, 1.65, 0.44, 0.58), (0.55, 1.50, 0.34, 0.42)]):
    box("Frame%d" % i, (0.03, w, h), (X0 + 0.015, yy, zz), m=M['wood'])
    box("Canvas%d" % i, (0.01, w - 0.06, h - 0.06), (X0 + 0.036, yy, zz), m=M['art'])

# dining / work table with two chairs
TX, TY = 0.75, -1.25
cyl("TableTop", 0.46, 0.04, (TX, TY, 0.74), v=32, m=M['wood'])
cyl("TableCol", 0.055, 0.72, (TX, TY, 0.37), v=16, m=M['steel'])
cyl("TableFoot", 0.26, 0.025, (TX, TY, 0.013), v=28, m=M['steel'])
for sgn, ang in ((-1, R(8)), (1, R(-14))):
    cx, cy = TX + sgn * 0.62, TY + sgn * 0.16
    box("ChairSeat", (0.40, 0.40, 0.05), (cx, cy, 0.45), rot=(0, 0, ang), m=M['wood'], b=0.01)
    box("ChairBack", (0.38, 0.05, 0.42), (cx + sgn * 0.17, cy, 0.66), rot=(0, 0, ang), m=M['wood'], b=0.01)
    for lx in (-0.16, 0.16):
        for ly in (-0.16, 0.16):
            cyl("ChairLeg", 0.014, 0.43, (cx + lx, cy + ly, 0.215), v=8, m=M['steel'])
box("Laptop", (0.30, 0.21, 0.015), (TX - 0.04, TY - 0.03, 0.768), rot=(0, 0, R(-10)), m=M['steel'], b=0.004)
box("LaptopLid", (0.30, 0.014, 0.20), (TX - 0.06, TY + 0.10, 0.855), rot=(R(-12), 0, R(-10)), m=M['dark'], b=0.004)

# pendant over the table
cyl("PendCord", 0.006, 0.90, (TX, TY, 2.25), v=8, m=M['dark'])
cone("PendShade", 0.20, 0.06, 0.22, (TX, TY, 1.70), v=28, m=M['shade'])
light("PendantLight", 'POINT', (TX, TY, 1.63), 30.0, size=0.10, color=(1.0, 0.86, 0.66))

# plant in the open corner
cyl("PlantPot", 0.20, 0.34, (2.62, -1.72, 0.17), v=24, m=M['pot'])
cyl("PlantSoil", 0.175, 0.02, (2.62, -1.72, 0.335), v=20, m=M['dark'])
cyl("Stem", 0.02, 0.60, (2.62, -1.72, 0.62), v=8, m=M['leaf'])
for i in range(7):
    a = R(i * 51.4)
    lf = ball("Leaf%d" % i, 0.13,
              (2.62 + 0.20 * math.cos(a), -1.72 + 0.20 * math.sin(a), 0.72 + 0.09 * (i % 3)),
              seg=16, ring=8, m=M['leaf'])
    lf.scale = (1.5, 0.7, 0.22)
    lf.rotation_euler = (0, R(22), a)

# ------------------------------------------------------------- lighting
sun = light("Sun", 'SUN', (6.0, -8.0, 9.0), 3.2, color=(1.0, 0.96, 0.88))
sun.rotation_euler = (R(52), R(6), R(214))
light("SkyFill", 'AREA', (0.6, 0.0, 5.2), 420.0, size=6.0, color=(0.85, 0.90, 1.0), target=(0.2, 0.1, 0.9))
light("WindowLight", 'AREA', ((WX0 + WX1) / 2, Y1 + 0.6, 1.55), 180.0, size=1.4,
      color=(0.80, 0.88, 1.0), target=((WX0 + WX1) / 2, 0.4, 1.0))
light("FrontFill", 'AREA', (5.0, -6.0, 3.4), 260.0, size=5.0, color=(1.0, 0.97, 0.92), target=(0.0, 0.0, 1.1))

# ------------------------------------------------------------- isometric camera
cd = bpy.data.cameras.new("IsoCam")
cd.type = 'ORTHO'
cd.ortho_scale = 9.6
cd.clip_end = 200.0
cam = bpy.data.objects.new("IsoCam", cd)
bpy.context.collection.objects.link(cam)
centre = Vector((0.05, -0.05, 1.05))
fwd = Vector((-0.6124, 0.6124, -0.5))          # matches euler (60, 0, 45)
cam.location = centre - fwd * 18.0
cam.rotation_euler = (R(60.0), 0.0, R(45.0))
sc.camera = cam
