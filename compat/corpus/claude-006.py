"""Blender 4.5 LTS - furnished 4 x 5 m room with doorway and window."""
import bpy, bmesh, math, random
from mathutils import Vector


# ----------------------------------------------------------------- helpers
def reset_scene():
    bpy.ops.wm.read_factory_settings(use_empty=True)
    scene = bpy.context.scene
    for engine in ("BLENDER_EEVEE_NEXT", "BLENDER_EEVEE", "CYCLES"):
        try:
            scene.render.engine = engine
            break
        except TypeError:
            continue
    world = bpy.data.worlds.new("World")
    world.use_nodes = True
    scene.world = world
    return scene


def world_color(color, strength=1.0):
    bg = bpy.context.scene.world.node_tree.nodes["Background"]
    bg.inputs[0].default_value = (color[0], color[1], color[2], 1.0)
    bg.inputs[1].default_value = strength


def mkmat(name, color, rough=0.5, metal=0.0, emit=None, emit_power=0.0,
          alpha=1.0, transmission=0.0, ior=1.45):
    mat = bpy.data.materials.new(name)
    mat.use_nodes = True
    b = mat.node_tree.nodes["Principled BSDF"]
    b.inputs["Base Color"].default_value = (color[0], color[1], color[2], 1.0)
    b.inputs["Roughness"].default_value = rough
    b.inputs["Metallic"].default_value = metal
    if "IOR" in b.inputs:
        b.inputs["IOR"].default_value = ior
    if transmission and "Transmission Weight" in b.inputs:
        b.inputs["Transmission Weight"].default_value = transmission
    if emit is not None:
        for key in ("Emission Color", "Emission"):
            if key in b.inputs:
                b.inputs[key].default_value = (emit[0], emit[1], emit[2], 1.0)
                break
        if "Emission Strength" in b.inputs:
            b.inputs["Emission Strength"].default_value = emit_power
    if alpha < 1.0:
        b.inputs["Alpha"].default_value = alpha
        try:
            mat.blend_method = 'BLEND'
        except TypeError:
            mat.blend_method = 'HASHED'
    return mat


def link(ob):
    bpy.context.scene.collection.objects.link(ob)
    return ob


def _finish(name, bm, mat, loc, rot, smooth, parent, scale=(1.0, 1.0, 1.0)):
    if smooth:
        for f in bm.faces:
            f.smooth = True
        for e in bm.edges:
            if e.calc_face_angle(0.0) > 0.62:
                e.smooth = False
    me = bpy.data.meshes.new(name)
    bm.to_mesh(me)
    bm.free()
    if mat is not None:
        me.materials.append(mat)
    ob = bpy.data.objects.new(name, me)
    ob.location = loc
    ob.rotation_euler = rot
    ob.scale = scale
    if parent is not None:
        ob.parent = parent
    return link(ob)


def box(name, size, loc=(0, 0, 0), rot=(0, 0, 0), mat=None, shift=(0, 0, 0), parent=None):
    bm = bmesh.new()
    bmesh.ops.create_cube(bm, size=1.0)
    bmesh.ops.scale(bm, vec=Vector(size), verts=bm.verts)
    if any(shift):
        bmesh.ops.translate(bm, verts=bm.verts, vec=Vector(shift))
    return _finish(name, bm, mat, loc, rot, False, parent)


def cylinder(name, radius, depth, loc=(0, 0, 0), rot=(0, 0, 0), mat=None,
             segments=24, radius_top=None, cap=True, parent=None):
    bm = bmesh.new()
    bmesh.ops.create_cone(bm, cap_ends=cap, cap_tris=False, segments=segments,
                          radius1=radius,
                          radius2=(radius if radius_top is None else radius_top),
                          depth=depth)
    return _finish(name, bm, mat, loc, rot, True, parent)


def sphere(name, radius, loc=(0, 0, 0), mat=None, u=24, v=12,
           scale=(1.0, 1.0, 1.0), parent=None):
    bm = bmesh.new()
    bmesh.ops.create_uvsphere(bm, u_segments=u, v_segments=v, radius=radius)
    return _finish(name, bm, mat, loc, (0, 0, 0), True, parent, scale)


def add_camera(loc, target, lens=35.0):
    cam = bpy.data.cameras.new("Camera")
    cam.lens = lens
    ob = bpy.data.objects.new("Camera", cam)
    ob.location = loc
    ob.rotation_euler = (Vector(target) - Vector(loc)).to_track_quat('-Z', 'Y').to_euler()
    link(ob)
    bpy.context.scene.camera = ob
    return ob


def add_light(name, ltype, loc, energy, color=(1, 1, 1), size=0.25,
              size_y=None, target=None):
    lt = bpy.data.lights.new(name, ltype)
    lt.energy = energy
    lt.color = color
    if ltype == 'AREA':
        lt.size = size
        if size_y is not None:
            lt.shape = 'RECTANGLE'
            lt.size_y = size_y
    elif ltype in ('POINT', 'SPOT'):
        lt.shadow_soft_size = size
    ob = bpy.data.objects.new(name, lt)
    ob.location = loc
    if target is not None:
        ob.rotation_euler = (Vector(target) - Vector(loc)).to_track_quat('-Z', 'Y').to_euler()
    return link(ob)


# ------------------------------------------------------------------- scene
reset_scene()
world_color((0.30, 0.42, 0.60), 0.6)
random.seed(11)

FW, FD, FH, T = 4.0, 5.0, 2.6, 0.12       # interior width, depth, height, wall thickness

m_floor = mkmat("Oak Floor", (0.42, 0.27, 0.15), rough=0.35)
m_wall = mkmat("Wall Paint", (0.83, 0.81, 0.76), rough=0.85)
m_ceil = mkmat("Ceiling", (0.93, 0.93, 0.92), rough=0.9)
m_trim = mkmat("White Trim", (0.94, 0.94, 0.93), rough=0.4)
m_wood = mkmat("Walnut", (0.17, 0.10, 0.06), rough=0.4)
m_wood2 = mkmat("Light Wood", (0.55, 0.38, 0.22), rough=0.45)
m_fabric = mkmat("Sofa Fabric", (0.31, 0.36, 0.40), rough=0.9)
m_cushion = mkmat("Cushion", (0.62, 0.30, 0.24), rough=0.9)
m_rug = mkmat("Rug", (0.55, 0.48, 0.40), rough=0.95)
m_metal = mkmat("Brushed Metal", (0.62, 0.63, 0.65), rough=0.32, metal=1.0)
m_black = mkmat("Dark Plastic", (0.04, 0.04, 0.05), rough=0.45)
m_glass = mkmat("Glass", (0.85, 0.90, 0.92), rough=0.03, transmission=1.0, ior=1.45)
m_screen = mkmat("Screen", (0.02, 0.02, 0.03), rough=0.2, emit=(0.10, 0.14, 0.22), emit_power=1.2)
m_shade = mkmat("Lamp Shade", (0.96, 0.92, 0.82), rough=0.6, emit=(1.0, 0.85, 0.62), emit_power=3.0)
m_leaf = mkmat("Foliage", (0.14, 0.32, 0.12), rough=0.75)
m_pot = mkmat("Terracotta", (0.55, 0.28, 0.18), rough=0.7)
book_mats = [mkmat("Book%d" % i, c, rough=0.7) for i, c in enumerate(
    [(0.55, 0.13, 0.12), (0.13, 0.25, 0.42), (0.20, 0.36, 0.20),
     (0.62, 0.50, 0.20), (0.35, 0.18, 0.38), (0.75, 0.72, 0.64)])]

# ---- shell -------------------------------------------------------------
box("Floor", (FW + 2 * T, FD + 2 * T, 0.10), (0, 0, -0.05), mat=m_floor)
box("Ceiling", (FW + 2 * T, FD + 2 * T, 0.10), (0, 0, FH + 0.05), mat=m_ceil)


def wall(name, along, offset, u0, u1, height, thick, openings, mat):
    """Build a wall out of solid segments, leaving the given openings empty.
    openings: list of (centre, width, sill, top)."""
    def seg(a, b, z0, z1, tag):
        if b - a < 1e-4 or z1 - z0 < 1e-4:
            return
        L, hh = b - a, z1 - z0
        cu, cz = 0.5 * (a + b), 0.5 * (z0 + z1)
        if along == 'x':
            box("%s_%s" % (name, tag), (L, thick, hh), (cu, offset, cz), mat=mat)
        else:
            box("%s_%s" % (name, tag), (thick, L, hh), (offset, cu, cz), mat=mat)
    cur = u0
    for i, (c, w, sill, top) in enumerate(sorted(openings)):
        a, b = c - 0.5 * w, c + 0.5 * w
        seg(cur, a, 0.0, height, "pier%d" % i)
        seg(a, b, 0.0, sill, "sill%d" % i)
        seg(a, b, top, height, "head%d" % i)
        cur = b
    seg(cur, u1, 0.0, height, "end")


DOOR_C, DOOR_W, DOOR_H = -0.70, 0.95, 2.05
WIN_C, WIN_W, WIN_SILL, WIN_TOP = 0.60, 1.50, 0.85, 2.05

wall("WallSouth", 'x', -FD / 2 - T / 2, -FW / 2 - T, FW / 2 + T, FH, T,
     [(DOOR_C, DOOR_W, 0.0, DOOR_H)], m_wall)
wall("WallNorth", 'x', FD / 2 + T / 2, -FW / 2 - T, FW / 2 + T, FH, T, [], m_wall)
wall("WallWest", 'y', -FW / 2 - T / 2, -FD / 2, FD / 2, FH, T, [], m_wall)
wall("WallEast", 'y', FW / 2 + T / 2, -FD / 2, FD / 2, FH, T,
     [(WIN_C, WIN_W, WIN_SILL, WIN_TOP)], m_wall)

# ---- doorway lining, casing and leaf ------------------------------------
DY = -FD / 2 - T / 2
d_l, d_r = DOOR_C - DOOR_W / 2, DOOR_C + DOOR_W / 2
box("DoorJambL", (0.02, T, DOOR_H - 0.02), (d_l + 0.01, DY, (DOOR_H - 0.02) / 2), mat=m_trim)
box("DoorJambR", (0.02, T, DOOR_H - 0.02), (d_r - 0.01, DY, (DOOR_H - 0.02) / 2), mat=m_trim)
box("DoorHead", (DOOR_W, T, 0.02), (DOOR_C, DY, DOOR_H - 0.01), mat=m_trim)
for sx in (d_l - 0.03, d_r + 0.03):
    box("DoorCasing", (0.06, 0.02, DOOR_H + 0.06), (sx, -FD / 2 + 0.01, (DOOR_H + 0.06) / 2), mat=m_trim)
box("DoorCasingTop", (DOOR_W + 0.12, 0.02, 0.06), (DOOR_C, -FD / 2 + 0.01, DOOR_H + 0.03), mat=m_trim)
leaf = box("DoorLeaf", (0.90, 0.045, 2.00), (d_l + 0.02, DY, 0.02),
           rot=(0, 0, math.radians(62)), mat=m_trim, shift=(0.45, 0, 1.0))
box("DoorPanelA", (0.62, 0.012, 0.72), (0, 0, 0), mat=m_trim,
    shift=(0.45, -0.028, 0.52), parent=leaf).rotation_euler = (0, 0, 0)
box("DoorPanelB", (0.62, 0.012, 0.62), (0, 0, 0), mat=m_trim,
    shift=(0.45, -0.028, 1.42), parent=leaf)
cylinder("DoorHandle", 0.018, 0.11, (0, 0, 0), rot=(math.pi / 2, 0, 0), mat=m_metal,
         parent=leaf).location = (0.80, -0.05, 1.02)

# ---- window frame, glass, sill ------------------------------------------
WX = FW / 2 + T / 2
w_a, w_b = WIN_C - WIN_W / 2, WIN_C + WIN_W / 2
box("WinJambL", (T, 0.02, WIN_TOP - WIN_SILL), (WX, w_a + 0.01, (WIN_TOP + WIN_SILL) / 2), mat=m_trim)
box("WinJambR", (T, 0.02, WIN_TOP - WIN_SILL), (WX, w_b - 0.01, (WIN_TOP + WIN_SILL) / 2), mat=m_trim)
box("WinHead", (T, WIN_W, 0.02), (WX, WIN_C, WIN_TOP - 0.01), mat=m_trim)
box("WinBottom", (T, WIN_W, 0.02), (WX, WIN_C, WIN_SILL + 0.01), mat=m_trim)
box("WinFrameBot", (0.06, WIN_W, 0.05), (WX, WIN_C, WIN_SILL + 0.045), mat=m_trim)
box("WinFrameTop", (0.06, WIN_W, 0.05), (WX, WIN_C, WIN_TOP - 0.045), mat=m_trim)
box("WinFrameL", (0.06, 0.05, 1.20), (WX, w_a + 0.045, 1.45), mat=m_trim)
box("WinFrameR", (0.06, 0.05, 1.20), (WX, w_b - 0.045, 1.45), mat=m_trim)
box("WinMullion", (0.05, 0.04, 1.10), (WX, WIN_C, 1.45), mat=m_trim)
for dy in (-0.375, 0.375):
    box("WinGlass", (0.012, 0.70, 1.09), (WX, WIN_C + dy, 1.45), mat=m_glass)
box("WinSillBoard", (0.26, WIN_W + 0.12, 0.04), (FW / 2 - 0.05, WIN_C, WIN_SILL - 0.01), mat=m_trim)

# ---- skirting ------------------------------------------------------------
box("SkirtN", (FW, 0.02, 0.10), (0, FD / 2 - 0.01, 0.05), mat=m_trim)
box("SkirtW", (0.02, FD, 0.10), (-FW / 2 + 0.01, 0, 0.05), mat=m_trim)
box("SkirtE1", (0.02, FD / 2 + w_a, 0.10), (FW / 2 - 0.01, (-FD / 2 + w_a) / 2, 0.05), mat=m_trim)
box("SkirtE2", (0.02, FD / 2 - w_b, 0.10), (FW / 2 - 0.01, (w_b + FD / 2) / 2, 0.05), mat=m_trim)
box("SkirtS1", (FW / 2 + d_l, 0.02, 0.10), ((-FW / 2 + d_l) / 2, -FD / 2 + 0.01, 0.05), mat=m_trim)
box("SkirtS2", (FW / 2 - d_r, 0.02, 0.10), ((d_r + FW / 2) / 2, -FD / 2 + 0.01, 0.05), mat=m_trim)

# ---- rug and sofa --------------------------------------------------------
box("Rug", (2.40, 2.60, 0.016), (-0.45, -0.30, 0.008), mat=m_rug)

SX, SY = -1.30, -0.30
box("SofaBase", (0.90, 2.00, 0.24), (SX, SY, 0.32), mat=m_fabric)
box("SofaBack", (0.22, 2.00, 0.56), (SX - 0.34, SY, 0.62), mat=m_fabric)
for ay in (SY - 0.90, SY + 0.90):
    box("SofaArm", (0.90, 0.20, 0.34), (SX, ay, 0.55), mat=m_fabric)
for cy in (SY - 0.41, SY + 0.41):
    box("SofaSeat", (0.80, 0.76, 0.15), (SX + 0.02, cy, 0.515), mat=m_cushion)
    box("SofaPillow", (0.15, 0.74, 0.42), (SX - 0.19, cy, 0.71),
        rot=(0, math.radians(-8), 0), mat=m_fabric)
for lx in (SX - 0.38, SX + 0.38):
    for ly in (SY - 0.88, SY + 0.88):
        cylinder("SofaLeg", 0.028, 0.20, (lx, ly, 0.10), mat=m_wood, segments=12)

# ---- coffee table --------------------------------------------------------
box("TableTop", (1.00, 0.56, 0.05), (-0.10, -0.30, 0.42), mat=m_wood2)
box("TableShelf", (0.86, 0.44, 0.025), (-0.10, -0.30, 0.16), mat=m_wood2)
for lx in (-0.55, 0.35):
    for ly in (-0.54, -0.06):
        box("TableLeg", (0.05, 0.05, 0.40), (lx, ly, 0.20), mat=m_wood)
box("TableBook", (0.24, 0.18, 0.035), (-0.22, -0.34, 0.462), rot=(0, 0, 0.25), mat=book_mats[1])
cylinder("Mug", 0.042, 0.10, (0.12, -0.20, 0.495), mat=m_trim, segments=16)

# ---- media console and TV (north wall) ----------------------------------
box("Console", (1.70, 0.40, 0.46), (0.30, 2.28, 0.28), mat=m_wood)
box("ConsoleTop", (1.78, 0.44, 0.03), (0.30, 2.28, 0.525), mat=m_wood2)
for dx in (-0.42, 0.42):
    box("ConsoleDoor", (0.78, 0.02, 0.36), (0.30 + dx, 2.075, 0.28), mat=m_wood2)
    cylinder("ConsoleKnob", 0.014, 0.04, (0.30 + dx, 2.05, 0.28),
             rot=(math.pi / 2, 0, 0), mat=m_metal, segments=12)
box("TVStand", (0.34, 0.20, 0.05), (0.30, 2.30, 0.565), mat=m_black)
box("TVBody", (1.16, 0.05, 0.66), (0.30, 2.34, 0.95), mat=m_black)
box("TVScreen", (1.10, 0.01, 0.60), (0.30, 2.31, 0.95), mat=m_screen)

# ---- bookshelf (north wall, left) ---------------------------------------
BX, BY, BH, BW, BD = -1.35, 2.34, 1.86, 0.92, 0.30
box("ShelfSideL", (0.03, BD, BH), (BX - BW / 2, BY, BH / 2), mat=m_wood)
box("ShelfSideR", (0.03, BD, BH), (BX + BW / 2, BY, BH / 2), mat=m_wood)
box("ShelfBack", (BW, 0.02, BH), (BX, BY + BD / 2, BH / 2), mat=m_wood2)
shelf_levels = [0.03, 0.42, 0.81, 1.20, 1.59, 1.84]
for i, sz in enumerate(shelf_levels):
    box("Shelf%d" % i, (BW, BD, 0.03), (BX, BY, sz), mat=m_wood)
for sz in shelf_levels[:-1]:
    x = BX - BW / 2 + 0.05
    while x < BX + BW / 2 - 0.09:
        w = random.uniform(0.028, 0.055)
        h = random.uniform(0.19, 0.28)
        box("Book", (w, 0.17, h), (x + w / 2, BY - 0.04, sz + 0.015 + h / 2),
            mat=random.choice(book_mats))
        x += w + 0.005
        if random.random() < 0.12:
            x += 0.09

# ---- floor lamp ----------------------------------------------------------
LX, LY = -1.72, 0.95
cylinder("LampBase", 0.17, 0.03, (LX, LY, 0.015), mat=m_metal, segments=28)
cylinder("LampPole", 0.018, 1.42, (LX, LY, 0.73), mat=m_metal, segments=14)
cylinder("LampShade", 0.20, 0.26, (LX, LY, 1.58), mat=m_shade, segments=28,
         radius_top=0.14, cap=False)
cylinder("LampDiffuser", 0.19, 0.01, (LX, LY, 1.46), mat=m_shade, segments=28)
add_light("LampLight", 'POINT', (LX, LY, 1.55), 55.0, (1.0, 0.83, 0.60), size=0.09)

# ---- side table + plant --------------------------------------------------
PX, PY = 1.62, 1.75
cylinder("PotBody", 0.19, 0.34, (PX, PY, 0.17), mat=m_pot, segments=24, radius_top=0.23)
cylinder("PotSoil", 0.215, 0.02, (PX, PY, 0.335), mat=m_black, segments=24)
for dx, dy, dz, r in ((0.0, 0.0, 0.62, 0.24), (0.16, 0.08, 0.48, 0.17),
                      (-0.13, -0.10, 0.52, 0.16), (0.04, -0.15, 0.72, 0.14)):
    sphere("Foliage", r, (PX + dx, PY + dy, dz), mat=m_leaf, u=16, v=10,
           scale=(1.0, 1.0, 0.85))
cylinder("Stem", 0.02, 0.5, (PX, PY, 0.45), mat=m_wood, segments=10)

cylinder("SideTableTop", 0.27, 0.035, (1.62, -1.55, 0.545), mat=m_wood2, segments=28)
cylinder("SideTableStem", 0.035, 0.53, (1.62, -1.55, 0.265), mat=m_metal, segments=16)
cylinder("SideTableFoot", 0.20, 0.02, (1.62, -1.55, 0.01), mat=m_metal, segments=24)

# ---- wall picture (west wall) -------------------------------------------
box("PictureFrame", (0.03, 0.80, 0.60), (-FW / 2 + 0.02, -0.30, 1.72), mat=m_wood)
box("PictureCanvas", (0.01, 0.72, 0.52), (-FW / 2 + 0.045, -0.30, 1.72), mat=m_cushion)

# ---- ceiling fixture -----------------------------------------------------
cylinder("CeilingRose", 0.06, 0.04, (0, 0.2, FH - 0.02), mat=m_trim, segments=20)
cylinder("CeilingShade", 0.26, 0.14, (0, 0.2, FH - 0.14), mat=m_shade, segments=32,
         radius_top=0.14, cap=False)
cylinder("CeilingDiffuser", 0.25, 0.01, (0, 0.2, FH - 0.205), mat=m_shade, segments=32)

# ---- lighting ------------------------------------------------------------
sun = add_light("Sun", 'SUN', (7.0, -2.0, 6.0), 2.6, (1.0, 0.95, 0.86))
sun.rotation_euler = (Vector((0, 0.6, 1.2)) - Vector((7.0, -2.0, 6.0))).to_track_quat('-Z', 'Y').to_euler()
add_light("WindowLight", 'AREA', (FW / 2 + 0.55, WIN_C, 1.45), 420.0, (0.90, 0.94, 1.0),
          size=1.5, size_y=1.2, target=(0.0, WIN_C, 1.20))
add_light("CeilingLight", 'AREA', (0.0, 0.20, FH - 0.28), 130.0, (1.0, 0.92, 0.82),
          size=0.5, target=(0.0, 0.20, 0.0))
add_light("Fill", 'AREA', (-0.3, -2.0, 2.2), 45.0, (0.85, 0.88, 1.0),
          size=2.0, target=(-0.5, 0.5, 1.0))

# ---- camera --------------------------------------------------------------
add_camera((-1.55, -2.05, 1.68), (0.75, 1.55, 1.05), lens=22.0)
