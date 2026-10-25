"""Blender 4.5 LTS - kitchen island with bar stools and overhead pendant lights."""
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


def mkmat(name, color, rough=0.5, metal=0.0, emit=None, emit_power=0.0, alpha=1.0):
    mat = bpy.data.materials.new(name)
    mat.use_nodes = True
    b = mat.node_tree.nodes["Principled BSDF"]
    b.inputs["Base Color"].default_value = (color[0], color[1], color[2], 1.0)
    b.inputs["Roughness"].default_value = rough
    b.inputs["Metallic"].default_value = metal
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


def bevel_box(name, size, loc=(0, 0, 0), rot=(0, 0, 0), mat=None, amount=0.008, parent=None):
    bm = bmesh.new()
    bmesh.ops.create_cube(bm, size=1.0)
    bmesh.ops.scale(bm, vec=Vector(size), verts=bm.verts)
    bmesh.ops.bevel(bm, geom=list(bm.verts) + list(bm.edges) + list(bm.faces),
                    offset=amount, segments=2, affect='EDGES', profile=0.5,
                    clamp_overlap=True)
    return _finish(name, bm, mat, loc, rot, False, parent)


def cylinder(name, radius, depth, loc=(0, 0, 0), rot=(0, 0, 0), mat=None,
             segments=32, radius_top=None, cap=True, parent=None):
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


def tube(name, points, radius, mat=None, cyclic=False, res=4, parent=None, caps=True):
    cu = bpy.data.curves.new(name, 'CURVE')
    cu.dimensions = '3D'
    sp = cu.splines.new('POLY')
    sp.points.add(len(points) - 1)
    for i, p in enumerate(points):
        sp.points[i].co = (p[0], p[1], p[2], 1.0)
    sp.use_cyclic_u = cyclic
    sp.use_smooth = True
    cu.bevel_depth = radius
    cu.bevel_resolution = res
    cu.fill_caps = caps
    if mat is not None:
        cu.materials.append(mat)
    ob = bpy.data.objects.new(name, cu)
    if parent is not None:
        ob.parent = parent
    return link(ob)


def circle_points(center, radius, n=28, plane='XY'):
    pts = []
    for i in range(n):
        a = 2.0 * math.pi * i / n
        c, s = math.cos(a), math.sin(a)
        if plane == 'XY':
            pts.append((center[0] + radius * c, center[1] + radius * s, center[2]))
        else:
            pts.append((center[0] + radius * c, center[1], center[2] + radius * s))
    return pts


def empty(name, loc=(0, 0, 0), rot=(0, 0, 0)):
    ob = bpy.data.objects.new(name, None)
    ob.empty_display_size = 0.2
    ob.location = loc
    ob.rotation_euler = rot
    return link(ob)


def add_camera(loc, target, lens=35.0):
    cam = bpy.data.cameras.new("Camera")
    cam.lens = lens
    ob = bpy.data.objects.new("Camera", cam)
    ob.location = loc
    ob.rotation_euler = (Vector(target) - Vector(loc)).to_track_quat('-Z', 'Y').to_euler()
    link(ob)
    bpy.context.scene.camera = ob
    return ob


def add_light(name, ltype, loc, energy, color=(1, 1, 1), size=0.5, size_y=None, target=None):
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
world_color((0.16, 0.18, 0.22), 0.5)
random.seed(9)

CEIL = 2.80
COUNTER = 0.92

m_floor = mkmat("Oak Floor", (0.46, 0.32, 0.19), rough=0.35)
m_wall = mkmat("Wall", (0.86, 0.85, 0.82), rough=0.9)
m_ceil = mkmat("Ceiling", (0.94, 0.94, 0.93), rough=0.95)
m_stone = mkmat("Quartz Top", (0.88, 0.87, 0.84), rough=0.18)
m_cab = mkmat("Navy Cabinet", (0.055, 0.085, 0.135), rough=0.42)
m_cab2 = mkmat("Oak Cabinet", (0.52, 0.36, 0.20), rough=0.5)
m_kick = mkmat("Toe Kick", (0.03, 0.035, 0.045), rough=0.6)
m_brass = mkmat("Brass", (0.72, 0.55, 0.24), rough=0.22, metal=1.0)
m_steel = mkmat("Steel", (0.70, 0.71, 0.73), rough=0.25, metal=1.0)
m_black = mkmat("Matt Black", (0.035, 0.035, 0.04), rough=0.45)
m_leather = mkmat("Leather Seat", (0.30, 0.17, 0.10), rough=0.55)
m_shade_out = mkmat("Pendant Shell", (0.06, 0.06, 0.07), rough=0.35)
m_shade_in = mkmat("Pendant Inner", (1.0, 0.94, 0.84), rough=0.4,
                   emit=(1.0, 0.86, 0.66), emit_power=9.0)
m_wood_board = mkmat("Chopping Board", (0.60, 0.44, 0.26), rough=0.55)
m_ceramic = mkmat("Ceramic", (0.92, 0.91, 0.88), rough=0.25)
m_fruit_a = mkmat("Apple", (0.55, 0.10, 0.09), rough=0.4)
m_fruit_b = mkmat("Lemon", (0.78, 0.68, 0.12), rough=0.45)
m_plant = mkmat("Herb", (0.16, 0.34, 0.15), rough=0.75)

# ---- room shell ----------------------------------------------------------
box("Floor", (9.0, 9.0, 0.10), (0, 0, -0.05), mat=m_floor)
box("Ceiling", (9.0, 9.0, 0.10), (0, 0, CEIL + 0.05), mat=m_ceil)
box("WallBack", (9.0, 0.12, CEIL), (0, 3.0, CEIL / 2), mat=m_wall)
box("WallLeft", (0.12, 9.0, CEIL), (-4.0, 0, CEIL / 2), mat=m_wall)
box("WallRight", (0.12, 9.0, CEIL), (4.0, 0, CEIL / 2), mat=m_wall)

# ---- island --------------------------------------------------------------
TOP_X, TOP_Y, TOP_T = 2.40, 1.25, 0.045
CAB_X, CAB_Y, CAB_H = 2.10, 0.90, COUNTER - TOP_T - 0.10
CAB_CY = 0.15                    # cabinet pushed back to leave a knee overhang

bevel_box("CounterTop", (TOP_X, TOP_Y, TOP_T), (0, 0, COUNTER - TOP_T / 2),
          mat=m_stone, amount=0.006)
box("IslandBody", (CAB_X, CAB_Y, CAB_H), (0, CAB_CY, 0.10 + CAB_H / 2), mat=m_cab)
box("ToeKick", (CAB_X - 0.10, CAB_Y - 0.10, 0.10), (0, CAB_CY, 0.05), mat=m_kick)
box("IslandEndPanelL", (0.02, CAB_Y, CAB_H), (-CAB_X / 2 - 0.011, CAB_CY, 0.10 + CAB_H / 2), mat=m_cab)
box("IslandEndPanelR", (0.02, CAB_Y, CAB_H), (CAB_X / 2 + 0.011, CAB_CY, 0.10 + CAB_H / 2), mat=m_cab)

# drawer bank + doors on the working (+Y) face
FACE_Y = CAB_CY + CAB_Y / 2
for i, dz in enumerate((0.72, 0.50, 0.28)):
    box("Drawer%d" % i, (0.66, 0.02, 0.19), (-0.66, FACE_Y + 0.011, dz), mat=m_cab)
    tube("DrawerHandle%d" % i, [(-0.90, FACE_Y + 0.045, dz), (-0.42, FACE_Y + 0.045, dz)],
         0.008, m_brass, res=3)
    for hx in (-0.90, -0.42):
        tube("HandleStem", [(hx, FACE_Y + 0.02, dz), (hx, FACE_Y + 0.045, dz)],
             0.007, m_brass, res=3)
for i, dx in enumerate((0.14, 0.72)):
    box("Door%d" % i, (0.54, 0.02, 0.70), (dx, FACE_Y + 0.011, 0.50), mat=m_cab)
    tube("DoorHandle%d" % i, [(dx - 0.20, FACE_Y + 0.045, 0.30), (dx - 0.20, FACE_Y + 0.045, 0.70)],
         0.008, m_brass, res=3)
    for hz in (0.30, 0.70):
        tube("DoorHandleStem", [(dx - 0.20, FACE_Y + 0.02, hz), (dx - 0.20, FACE_Y + 0.045, hz)],
             0.007, m_brass, res=3)
# open display shelf on the seating side end
box("ShelfBoard", (0.34, 0.60, 0.02), (-CAB_X / 2 + 0.20, CAB_CY, 0.48), mat=m_cab2)

# ---- bar stools ----------------------------------------------------------
def make_stool(name, x, y, rot_z=0.0):
    root = empty(name, (x, y, 0.0), (0, 0, rot_z))
    SEAT_Z = COUNTER - 0.28
    cylinder("%s_Seat" % name, 0.175, 0.05, (0, 0, SEAT_Z), mat=m_leather,
             segments=32, parent=root)
    cylinder("%s_SeatRim" % name, 0.178, 0.018, (0, 0, SEAT_Z - 0.032), mat=m_black,
             segments=32, parent=root)
    for sx, sy in ((-1, -1), (-1, 1), (1, -1), (1, 1)):
        tube("%s_Leg" % name,
             [(sx * 0.125, sy * 0.125, SEAT_Z - 0.03), (sx * 0.205, sy * 0.205, 0.0)],
             0.017, m_black, res=4, parent=root)
    tube("%s_Footrest" % name, circle_points((0, 0, 0.20), 0.175, 24), 0.012,
         m_steel, cyclic=True, res=4, parent=root)
    for sx, sy in ((-1, -1), (-1, 1), (1, -1), (1, 1)):
        tube("%s_Brace" % name,
             [(sx * 0.115, sy * 0.115, 0.32), (sx * 0.155, sy * 0.155, 0.30)],
             0.010, m_black, res=3, parent=root)
    # low curved backrest
    tube("%s_Back" % name,
         [(0.13, -0.10, SEAT_Z + 0.02), (0.17, 0.0, SEAT_Z + 0.22), (0.13, 0.10, SEAT_Z + 0.02)],
         0.014, m_black, res=4, parent=root)
    return root


for i, sx in enumerate((-0.72, 0.0, 0.72)):
    make_stool("Stool%d" % i, sx, -0.92, rot_z=math.radians(-90) + random.uniform(-0.1, 0.1))

# ---- pendant lights ------------------------------------------------------
for i, px in enumerate((-0.75, 0.0, 0.75)):
    box("PendantPlate%d" % i, (0.09, 0.09, 0.012), (px, 0.0, CEIL - 0.006), mat=m_shade_out)
    tube("PendantCord%d" % i, [(px, 0.0, CEIL - 0.01), (px, 0.0, 1.80)], 0.005,
         m_black, res=3)
    cylinder("PendantShade%d" % i, 0.185, 0.24, (px, 0.0, 1.66), mat=m_shade_out,
             segments=36, radius_top=0.05, cap=False)
    cylinder("PendantInner%d" % i, 0.178, 0.22, (px, 0.0, 1.665), mat=m_shade_in,
             segments=36, radius_top=0.048, cap=False)
    cylinder("PendantDisc%d" % i, 0.175, 0.008, (px, 0.0, 1.552), mat=m_shade_in, segments=36)
    sphere("PendantBulb%d" % i, 0.035, (px, 0.0, 1.60), mat=m_shade_in, u=16, v=8)
    add_light("Pendant%d" % i, 'POINT', (px, 0.0, 1.60), 42.0, (1.0, 0.86, 0.68), size=0.10)

# ---- countertop accessories ---------------------------------------------
box("ChoppingBoard", (0.42, 0.30, 0.022), (0.72, 0.22, COUNTER + 0.011),
    rot=(0, 0, 0.22), mat=m_wood_board)
cylinder("BowlBody", 0.085, 0.10, (-0.62, 0.18, COUNTER + 0.05), mat=m_ceramic,
         segments=32, radius_top=0.155, cap=False)
cylinder("BowlBase", 0.085, 0.012, (-0.62, 0.18, COUNTER + 0.006), mat=m_ceramic, segments=32)
for (fx, fy, fr, fm) in ((-0.66, 0.14, 0.042, m_fruit_a), (-0.58, 0.21, 0.040, m_fruit_a),
                         (-0.62, 0.24, 0.036, m_fruit_b), (-0.68, 0.22, 0.034, m_fruit_b)):
    sphere("Fruit", fr, (fx, fy, COUNTER + 0.055), mat=fm, u=16, v=10)
for i, mx in enumerate((0.30, 0.44)):
    cylinder("Mug%d" % i, 0.042, 0.095, (mx, -0.28, COUNTER + 0.048), mat=m_ceramic, segments=20)
    tube("MugHandle%d" % i,
         [(mx + 0.042, -0.28, COUNTER + 0.03), (mx + 0.075, -0.28, COUNTER + 0.055),
          (mx + 0.042, -0.28, COUNTER + 0.08)], 0.006, m_ceramic, res=3)
cylinder("HerbPot", 0.065, 0.12, (-1.02, -0.10, COUNTER + 0.06), mat=m_ceramic,
         segments=24, radius_top=0.078)
for i in range(6):
    a = 2.0 * math.pi * i / 6.0
    sphere("Herb", 0.055, (-1.02 + 0.045 * math.cos(a), -0.10 + 0.045 * math.sin(a),
                           COUNTER + 0.15), mat=m_plant, u=12, v=8, scale=(1.0, 1.0, 0.8))

# ---- background run of cabinets ------------------------------------------
box("BackBase", (3.40, 0.62, 0.78), (0.30, 2.62, 0.49), mat=m_cab2)
box("BackKick", (3.30, 0.52, 0.10), (0.30, 2.62, 0.05), mat=m_kick)
bevel_box("BackTop", (3.50, 0.66, 0.04), (0.30, 2.60, 0.90), mat=m_stone, amount=0.005)
for i in range(4):
    dx = -1.02 + i * 0.68
    box("BackDoor%d" % i, (0.62, 0.02, 0.68), (0.30 + dx, 2.30, 0.50), mat=m_cab2)
    tube("BackHandle%d" % i, [(0.30 + dx, 2.27, 0.78), (0.30 + dx + 0.30, 2.27, 0.78)],
         0.007, m_brass, res=3)
box("Backsplash", (3.50, 0.02, 0.55), (0.30, 2.92, 1.19), mat=m_stone)
box("UpperCabinets", (2.20, 0.36, 0.72), (0.60, 2.76, 1.92), mat=m_cab2)
for i in range(3):
    box("UpperDoor%d" % i, (0.68, 0.02, 0.66), (0.60 - 0.72 + i * 0.72, 2.575, 1.92), mat=m_cab2)
cylinder("SinkTap", 0.018, 0.34, (-0.90, 2.70, 1.07), mat=m_steel, segments=20)
tube("TapSpout", [(-0.90, 2.70, 1.22), (-0.90, 2.62, 1.28), (-0.90, 2.50, 1.20)],
     0.017, m_steel, res=5)
box("SinkBasin", (0.56, 0.40, 0.02), (-0.90, 2.60, 0.885), mat=m_steel)

# ---- lighting ------------------------------------------------------------
add_light("CeilingWash", 'AREA', (0.0, 0.60, CEIL - 0.08), 160.0, (1.0, 0.95, 0.88),
          size=3.0, target=(0, 0.4, 0.0))
add_light("WindowLight", 'AREA', (-3.60, -0.40, 1.75), 320.0, (0.80, 0.87, 1.0),
          size=2.2, size_y=1.6, target=(0.0, 0.10, 1.00))
add_light("UnderCabinet", 'AREA', (0.30, 2.55, 1.42), 45.0, (1.0, 0.92, 0.80),
          size=2.0, size_y=0.25, target=(0.30, 2.55, 0.9))
add_light("Rim", 'AREA', (2.60, -2.20, 2.30), 70.0, (0.95, 0.93, 1.0),
          size=1.5, target=(0.2, -0.3, 1.0))

# ---- camera --------------------------------------------------------------
add_camera((2.55, -2.85, 1.72), (-0.05, 0.30, 1.02), lens=35.0)
