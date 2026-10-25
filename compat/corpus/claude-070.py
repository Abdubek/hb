import bpy
import bmesh
import random
from math import radians, cos, sin
from mathutils import Vector

bpy.ops.wm.read_factory_settings(use_empty=True)
scene = bpy.context.scene
try:
    scene.render.engine = 'BLENDER_EEVEE_NEXT'
except TypeError:
    pass
C = bpy.context
random.seed(7)


def mat(name, color, rough=0.5, metal=0.0):
    m = bpy.data.materials.new(name)
    m.use_nodes = True
    b = m.node_tree.nodes["Principled BSDF"]
    b.inputs["Base Color"].default_value = (*color, 1.0)
    b.inputs["Roughness"].default_value = rough
    b.inputs["Metallic"].default_value = metal
    return m


def smooth(ob, angle=40.0):
    for p in ob.data.polygons:
        p.use_smooth = True
    m = ob.modifiers.new("EdgeSplit", 'EDGE_SPLIT')
    m.split_angle = radians(angle)
    return ob


def bevel(ob, width=0.004, segments=3, angle=40.0):
    m = ob.modifiers.new("Bevel", 'BEVEL')
    m.width = width
    m.segments = segments
    m.limit_method = 'ANGLE'
    m.angle_limit = radians(angle)
    return ob


def box(name, size, loc, material=None, rot=(0, 0, 0)):
    bpy.ops.mesh.primitive_cube_add(size=1, location=loc, rotation=rot)
    ob = C.object
    ob.name = name
    ob.scale = size
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    if material:
        ob.data.materials.append(material)
    return ob


def cyl(name, r, h, loc, material=None, rot=(0, 0, 0), verts=24):
    bpy.ops.mesh.primitive_cylinder_add(vertices=verts, radius=r, depth=h,
                                        location=loc, rotation=rot)
    ob = C.object
    ob.name = name
    if material:
        ob.data.materials.append(material)
    return ob


def cone(name, r1, r2, h, loc, material=None, rot=(0, 0, 0), verts=24):
    bpy.ops.mesh.primitive_cone_add(vertices=verts, radius1=r1, radius2=r2, depth=h,
                                    location=loc, rotation=rot)
    ob = C.object
    ob.name = name
    if material:
        ob.data.materials.append(material)
    return ob


def sphere(name, r, loc, material=None, segs=20, rings=12):
    bpy.ops.mesh.primitive_uv_sphere_add(segments=segs, ring_count=rings, radius=r,
                                         location=loc)
    ob = C.object
    ob.name = name
    if material:
        ob.data.materials.append(material)
    return ob


def join(objs, name):
    for o in C.selected_objects:
        o.select_set(False)
    for o in objs:
        o.select_set(True)
    C.view_layer.objects.active = objs[0]
    bpy.ops.object.join()
    ob = C.object
    ob.name = name
    return ob


# ---------------------------------------------------------------- materials
M_FLOOR = mat("Floor", (0.20, 0.15, 0.11), rough=0.62)
M_RUG = mat("Rug", (0.22, 0.12, 0.12), rough=0.88)
M_WOOD_F = mat("FrameWood", (0.16, 0.085, 0.048), rough=0.32)
M_WOOD_D = mat("WalnutDark", (0.085, 0.045, 0.026), rough=0.36)
M_SQ_L = mat("SquareLight", (0.72, 0.58, 0.38), rough=0.22)
M_SQ_D = mat("SquareDark", (0.10, 0.055, 0.032), rough=0.22)
M_WHITE = mat("PieceWhite", (0.80, 0.74, 0.62), rough=0.30)
M_BLACK = mat("PieceBlack", (0.045, 0.040, 0.038), rough=0.28)
M_FELT = mat("Felt", (0.10, 0.12, 0.16), rough=0.95)
M_BRASS = mat("Brass", (0.62, 0.47, 0.18), rough=0.30, metal=1.0)

# ---------------------------------------------------------------- room
box("Floor", (8.0, 8.0, 0.08), (0, 0, -0.04), M_FLOOR)
rug = box("Rug", (2.6, 2.2, 0.016), (0, 0, 0.008), M_RUG)
bevel(rug, 0.004, 2)

# ---------------------------------------------------------------- table
TOP_Z = 0.745          # height of the playing surface
TOP_T = 0.055
TOP_S = 0.66

top = box("TableTop", (TOP_S, TOP_S, TOP_T), (0, 0, TOP_Z - TOP_T * 0.5), M_WOOD_F)
bevel(top, 0.012, 4, angle=50)
smooth(top, 45)

# apron below the top
for s in (-1, 1):
    a = box("ApronX%d" % s, (TOP_S - 0.12, 0.028, 0.075),
            (0, s * (TOP_S * 0.5 - 0.055), TOP_Z - TOP_T - 0.045), M_WOOD_F)
    bevel(a, 0.005, 2)
    b = box("ApronY%d" % s, (0.028, TOP_S - 0.12, 0.075),
            (s * (TOP_S * 0.5 - 0.055), 0, TOP_Z - TOP_T - 0.045), M_WOOD_F)
    bevel(b, 0.005, 2)

# four tapered legs with turned collars and brass feet
LEG_OFF = TOP_S * 0.5 - 0.055
LEG_H = TOP_Z - TOP_T - 0.02
for sx in (-1, 1):
    for sy in (-1, 1):
        x, y = sx * LEG_OFF, sy * LEG_OFF
        smooth(cone("Leg%d%d" % (sx, sy), 0.030, 0.017, LEG_H,
                    (x, y, LEG_H * 0.5 + 0.010), M_WOOD_F, verts=20))
        smooth(cyl("LegCollar%d%d" % (sx, sy), 0.034, 0.030,
                   (x, y, TOP_Z - TOP_T - 0.030), M_WOOD_F, verts=20))
        smooth(cyl("LegFoot%d%d" % (sx, sy), 0.022, 0.016, (x, y, 0.012), M_BRASS,
                   verts=18))

# stretchers tying the legs together
for sy in (-1, 1):
    smooth(cyl("StretchX%d" % sy, 0.011, LEG_OFF * 2, (0, sy * LEG_OFF, 0.20),
               M_WOOD_F, rot=(0, radians(90), 0), verts=16))
for sx in (-1, 1):
    smooth(cyl("StretchY%d" % sx, 0.011, LEG_OFF * 2, (sx * LEG_OFF, 0, 0.20),
               M_WOOD_F, rot=(radians(90), 0, 0), verts=16))
smooth(cyl("StretchHub", 0.020, 0.028, (0, 0, 0.20), M_WOOD_F, verts=18))

# ---------------------------------------------------------------- inlaid board
SQ = 0.055
BOARD = SQ * 8
BOARD_Z = TOP_Z + 0.002

frame = box("BoardFrame", (BOARD + 0.07, BOARD + 0.07, 0.010), (0, 0, TOP_Z - 0.003),
            M_WOOD_D)
bevel(frame, 0.004, 3)

me = bpy.data.meshes.new("BoardSquares")
bm = bmesh.new()
for i in range(8):
    for j in range(8):
        x0 = -BOARD * 0.5 + i * SQ
        y0 = -BOARD * 0.5 + j * SQ
        vs = [bm.verts.new((x0, y0, 0.0)),
              bm.verts.new((x0 + SQ, y0, 0.0)),
              bm.verts.new((x0 + SQ, y0 + SQ, 0.0)),
              bm.verts.new((x0, y0 + SQ, 0.0))]
        f = bm.faces.new(vs)
        f.material_index = (i + j) % 2
bm.normal_update()
bm.to_mesh(me)
bm.free()
squares = bpy.data.objects.new("BoardSquares", me)
scene.collection.objects.link(squares)
squares.data.materials.append(M_SQ_D)
squares.data.materials.append(M_SQ_L)
squares.location = (0, 0, BOARD_Z)


# ---------------------------------------------------------------- chess pieces
def build_piece(kind, m, prefix):
    r = 0.019
    p = [cone(prefix + "_Base", r, r * 0.78, 0.011, (0, 0, 0.0055), m, verts=24),
         cyl(prefix + "_Collar", r * 0.72, 0.006, (0, 0, 0.014), m, verts=24)]

    if kind == 'pawn':
        p.append(cone(prefix + "_Stem", 0.0115, 0.0075, 0.022, (0, 0, 0.028), m,
                      verts=20))
        p.append(cyl(prefix + "_Ring", 0.0105, 0.004, (0, 0, 0.041), m, verts=20))
        p.append(sphere(prefix + "_Head", 0.0105, (0, 0, 0.052), m))
    elif kind == 'rook':
        p.append(cone(prefix + "_Body", 0.0140, 0.0125, 0.030, (0, 0, 0.032), m,
                      verts=22))
        p.append(cyl(prefix + "_Rim", 0.0160, 0.009, (0, 0, 0.051), m, verts=22))
        for k in range(4):
            a = radians(45 + 90 * k)
            p.append(box(prefix + "_Crenel%d" % k, (0.009, 0.009, 0.011),
                         (0.0105 * cos(a), 0.0105 * sin(a), 0.060), m, rot=(0, 0, a)))
    elif kind == 'knight':
        p.append(cone(prefix + "_Body", 0.0135, 0.0110, 0.024, (0, 0, 0.029), m,
                      verts=22))
        head = box(prefix + "_Head", (0.011, 0.024, 0.034), (0, 0.002, 0.055), m,
                   rot=(radians(-16), 0, 0))
        bevel(head, 0.005, 3)
        p.append(head)
        snout = box(prefix + "_Snout", (0.010, 0.020, 0.012), (0, 0.016, 0.062), m,
                    rot=(radians(-32), 0, 0))
        bevel(snout, 0.004, 2)
        p.append(snout)
        p.append(box(prefix + "_Ear", (0.006, 0.006, 0.010), (0, -0.008, 0.073), m,
                     rot=(radians(10), 0, 0)))
    elif kind == 'bishop':
        p.append(cone(prefix + "_Body", 0.0140, 0.0055, 0.038, (0, 0, 0.036), m,
                      verts=22))
        p.append(cyl(prefix + "_Band", 0.0090, 0.004, (0, 0, 0.049), m, verts=20))
        p.append(sphere(prefix + "_Head", 0.0085, (0, 0, 0.062), m))
        p.append(sphere(prefix + "_Tip", 0.0042, (0, 0, 0.072), m))
    elif kind == 'queen':
        p.append(cone(prefix + "_Body", 0.0150, 0.0085, 0.042, (0, 0, 0.038), m,
                      verts=24))
        p.append(cyl(prefix + "_Band", 0.0110, 0.005, (0, 0, 0.060), m, verts=22))
        p.append(cone(prefix + "_Crown", 0.0125, 0.0075, 0.014, (0, 0, 0.070), m,
                      verts=22))
        p.append(sphere(prefix + "_Orb", 0.0075, (0, 0, 0.083), m))
    elif kind == 'king':
        p.append(cone(prefix + "_Body", 0.0155, 0.0095, 0.046, (0, 0, 0.040), m,
                      verts=24))
        p.append(cyl(prefix + "_Band", 0.0115, 0.005, (0, 0, 0.064), m, verts=22))
        p.append(cone(prefix + "_Crown", 0.0130, 0.0090, 0.014, (0, 0, 0.074), m,
                      verts=22))
        p.append(box(prefix + "_CrossV", (0.005, 0.005, 0.020), (0, 0, 0.091), m))
        p.append(box(prefix + "_CrossH", (0.016, 0.005, 0.005), (0, 0, 0.093), m))

    for o in p:
        smooth(o, 45)
    ob = join(p, prefix)
    bpy.ops.object.origin_set(type='ORIGIN_CURSOR')   # cursor sits at the world origin
    return ob


PROTOS = {}
for colname, m in (("W", M_WHITE), ("B", M_BLACK)):
    for kind in ("pawn", "rook", "knight", "bishop", "queen", "king"):
        PROTOS[(colname, kind)] = build_piece(kind, m, "Proto_%s_%s" % (colname, kind))


def square_pos(file_i, rank_i):
    return (-BOARD * 0.5 + (file_i + 0.5) * SQ,
            -BOARD * 0.5 + (rank_i + 0.5) * SQ,
            BOARD_Z)


def place(colname, kind, file_i, rank_i):
    proto = PROTOS[(colname, kind)]
    ob = proto.copy()                      # linked duplicate: shares the mesh data
    scene.collection.objects.link(ob)
    ob.name = "%s_%s_%d%d" % (colname, kind, file_i, rank_i)
    ob.location = square_pos(file_i, rank_i)
    z = radians(random.uniform(-9, 9))
    if kind == 'knight' and colname == "B":
        z += radians(180)                  # knights face the opponent
    ob.rotation_euler = (0, 0, z)
    return ob


BACK = ["rook", "knight", "bishop", "queen", "king", "bishop", "knight", "rook"]
for f in range(8):
    place("W", BACK[f], f, 0)
    place("B", BACK[f], f, 7)
    if f != 4:                             # the e-pawns are advanced below
        place("W", "pawn", f, 1)
        place("B", "pawn", f, 6)

# an opening already under way: 1. e4 e5
place("W", "pawn", 4, 3)
place("B", "pawn", 4, 4)

for proto in PROTOS.values():
    bpy.data.objects.remove(proto, do_unlink=True)

# ---------------------------------------------------------------- table dressing
tray = box("Tray", (0.12, 0.20, 0.014), (BOARD * 0.5 + 0.10, -0.10, TOP_Z + 0.007),
           M_WOOD_D, rot=(0, 0, radians(-6)))
bevel(tray, 0.004, 2)
box("TrayFelt", (0.10, 0.18, 0.004), (BOARD * 0.5 + 0.10, -0.10, TOP_Z + 0.015),
    M_FELT, rot=(0, 0, radians(-6)))

for sx in (-1, 1):
    for sy in (-1, 1):
        smooth(cyl("Dot%d%d" % (sx, sy), 0.005, 0.006,
                   (sx * (BOARD * 0.5 + 0.024), sy * (BOARD * 0.5 + 0.024), TOP_Z),
                   M_BRASS, verts=14))

# ---------------------------------------------------------------- lighting
world = bpy.data.worlds.new("World")
scene.world = world
world.use_nodes = True
world.node_tree.nodes["Background"].inputs[0].default_value = (0.16, 0.17, 0.20, 1.0)
world.node_tree.nodes["Background"].inputs[1].default_value = 0.5

lamp = bpy.data.lights.new("Overhead", 'AREA')
lamp.energy = 120.0
lamp.size = 0.7
lamp.color = (1.0, 0.90, 0.76)
lo = bpy.data.objects.new("Overhead", lamp)
scene.collection.objects.link(lo)
lo.location = (0.10, -0.05, 1.55)

key = bpy.data.lights.new("Key", 'AREA')
key.energy = 90.0
key.size = 1.0
ko = bpy.data.objects.new("Key", key)
scene.collection.objects.link(ko)
ko.location = (0.9, -1.0, 1.35)
ko.rotation_euler = (radians(48), 0, radians(42))

fill = bpy.data.lights.new("Fill", 'AREA')
fill.energy = 35.0
fill.size = 1.6
fo = bpy.data.objects.new("Fill", fill)
scene.collection.objects.link(fo)
fo.location = (-1.2, -0.8, 1.1)
fo.rotation_euler = (radians(66), 0, radians(-56))

# ---------------------------------------------------------------- camera
cam_data = bpy.data.cameras.new("Camera")
cam_data.lens = 60.0
cam = bpy.data.objects.new("Camera", cam_data)
scene.collection.objects.link(cam)
cam.location = (0.62, -0.86, 1.16)
target = Vector((0.0, -0.02, 0.78))
cam.rotation_euler = (target - cam.location).to_track_quat('-Z', 'Y').to_euler()
cam_data.dof.use_dof = True
cam_data.dof.focus_distance = (target - cam.location).length
cam_data.dof.aperture_fstop = 3.5
scene.camera = cam
