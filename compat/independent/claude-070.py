import bpy
import bmesh
import math
from mathutils import Vector, Matrix

SQ = 0.06          # chess square size
TOP_Z = 0.75       # table top surface height
BOARD_T = 0.008    # board square thickness


def clear_scene():
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete(use_global=False)
    for coll in (bpy.data.meshes, bpy.data.materials):
        for block in list(coll):
            if block.users == 0:
                coll.remove(block)


def make_material(name, color, roughness=0.5, metallic=0.0):
    mat = bpy.data.materials.new(name)
    mat.use_nodes = True
    bsdf = mat.node_tree.nodes["Principled BSDF"]
    bsdf.inputs["Base Color"].default_value = (*color, 1.0)
    bsdf.inputs["Roughness"].default_value = roughness
    bsdf.inputs["Metallic"].default_value = metallic
    return mat


def obj_from_bmesh(bm, name, mat, smooth=False):
    me = bpy.data.meshes.new(name)
    bm.to_mesh(me)
    bm.free()
    if smooth:
        for poly in me.polygons:
            poly.use_smooth = True
    ob = bpy.data.objects.new(name, me)
    ob.data.materials.append(mat)
    bpy.context.collection.objects.link(ob)
    return ob


def add_box(bm, sx, sy, sz, loc):
    m = Matrix.Translation(loc) @ Matrix.Diagonal(Vector((sx, sy, sz, 1.0)))
    bmesh.ops.create_cube(bm, size=1.0, matrix=m)


def add_cone(bm, r1, r2, depth, z, segments=20):
    bmesh.ops.create_cone(bm, cap_ends=True, cap_tris=False, segments=segments,
                          radius1=r1, radius2=r2, depth=depth,
                          matrix=Matrix.Translation((0.0, 0.0, z + depth * 0.5)))


def add_ball(bm, r, z, segments=16):
    bmesh.ops.create_uvsphere(bm, u_segments=segments, v_segments=segments // 2,
                              radius=r, matrix=Matrix.Translation((0.0, 0.0, z)))


def build_piece_mesh(kind):
    """Stack simple primitives into one chess piece, base sitting at z = 0."""
    bm = bmesh.new()
    add_cone(bm, 0.023, 0.019, 0.010, 0.0)          # foot disc
    if kind == 'pawn':
        add_cone(bm, 0.014, 0.008, 0.022, 0.010)
        add_ball(bm, 0.011, 0.043)
    elif kind == 'rook':
        add_cone(bm, 0.015, 0.013, 0.030, 0.010)
        add_cone(bm, 0.018, 0.018, 0.014, 0.040)
    elif kind == 'bishop':
        add_cone(bm, 0.015, 0.007, 0.040, 0.010)
        add_ball(bm, 0.009, 0.052)
    elif kind == 'knight':
        add_cone(bm, 0.015, 0.012, 0.022, 0.010)
        head = Matrix.Translation((0.004, 0.0, 0.044)) @ \
            Matrix.Rotation(math.radians(22.0), 4, 'Y') @ \
            Matrix.Diagonal(Vector((0.030, 0.018, 0.030, 1.0)))
        bmesh.ops.create_cube(bm, size=1.0, matrix=head)
    elif kind == 'queen':
        add_cone(bm, 0.016, 0.010, 0.048, 0.010)
        add_cone(bm, 0.018, 0.014, 0.008, 0.058)
        add_ball(bm, 0.010, 0.072)
    else:  # king
        add_cone(bm, 0.016, 0.010, 0.054, 0.010)
        add_cone(bm, 0.018, 0.014, 0.008, 0.064)
        add_box(bm, 0.007, 0.007, 0.024, (0.0, 0.0, 0.084))
        add_box(bm, 0.018, 0.007, 0.007, (0.0, 0.0, 0.088))
    return bm


def square_center(file_i, rank_j):
    return ((file_i - 3.5) * SQ, (rank_j - 3.5) * SQ)


clear_scene()

mat_wood = make_material("Mat_TableWood", (0.19, 0.10, 0.05), 0.45)
mat_light = make_material("Mat_SquareLight", (0.82, 0.72, 0.55), 0.35)
mat_dark = make_material("Mat_SquareDark", (0.13, 0.08, 0.05), 0.35)
mat_white = make_material("Mat_PieceWhite", (0.88, 0.85, 0.78), 0.30)
mat_black = make_material("Mat_PieceBlack", (0.05, 0.05, 0.06), 0.30)
mat_floor = make_material("Mat_Floor", (0.35, 0.35, 0.37), 0.80)

# --- floor ---
bm = bmesh.new()
add_box(bm, 4.0, 4.0, 0.04, (0.0, 0.0, -0.02))
obj_from_bmesh(bm, "Floor", mat_floor)

# --- table top and apron ---
bm = bmesh.new()
add_box(bm, 0.62, 0.62, 0.04, (0.0, 0.0, TOP_Z - 0.02))
obj_from_bmesh(bm, "Table_Top", mat_wood)

bm = bmesh.new()
for sign in (-1, 1):
    add_box(bm, 0.56, 0.04, 0.07, (0.0, sign * 0.26, TOP_Z - 0.075))
    add_box(bm, 0.04, 0.56, 0.07, (sign * 0.26, 0.0, TOP_Z - 0.075))
obj_from_bmesh(bm, "Table_Apron", mat_wood)

bm = bmesh.new()
for sx in (-1, 1):
    for sy in (-1, 1):
        add_box(bm, 0.055, 0.055, TOP_Z - 0.04,
                (sx * 0.255, sy * 0.255, (TOP_Z - 0.04) * 0.5))
obj_from_bmesh(bm, "Table_Legs", mat_wood)

# --- board: two joined meshes, one per square colour ---
bm_light, bm_dark = bmesh.new(), bmesh.new()
for i in range(8):
    for j in range(8):
        x, y = square_center(i, j)
        target = bm_light if (i + j) % 2 else bm_dark
        add_box(target, SQ, SQ, BOARD_T, (x, y, TOP_Z + BOARD_T * 0.5))
obj_from_bmesh(bm_light, "Board_Squares_Light", mat_light)
obj_from_bmesh(bm_dark, "Board_Squares_Dark", mat_dark)

bm = bmesh.new()
for sign in (-1, 1):
    add_box(bm, 0.54, 0.03, BOARD_T, (0.0, sign * 0.255, TOP_Z + BOARD_T * 0.5))
    add_box(bm, 0.03, 0.54, BOARD_T, (sign * 0.255, 0.0, TOP_Z + BOARD_T * 0.5))
obj_from_bmesh(bm, "Board_Frame", mat_wood)

# --- pieces ---
BACK_RANK = ['rook', 'knight', 'bishop', 'queen', 'king', 'bishop', 'knight', 'rook']
piece_z = TOP_Z + BOARD_T

for side, rank_back, rank_pawn, mat, tag in (
        (1, 0, 1, mat_white, "White"),
        (-1, 7, 6, mat_black, "Black")):
    for i in range(8):
        kind = BACK_RANK[i]
        x, y = square_center(i, rank_back)
        ob = obj_from_bmesh(build_piece_mesh(kind),
                            "%s_%s_%d" % (tag, kind.capitalize(), i),
                            mat, smooth=(kind != 'knight'))
        ob.location = (x, y, piece_z)
        if side < 0:
            ob.rotation_euler = (0.0, 0.0, math.pi)
        x, y = square_center(i, rank_pawn)
        pawn = obj_from_bmesh(build_piece_mesh('pawn'), "%s_Pawn_%d" % (tag, i),
                              mat, smooth=True)
        pawn.location = (x, y, piece_z)

# --- lighting and camera ---
key_data = bpy.data.lights.new("Key", type='AREA')
key_data.energy = 220.0
key_data.size = 1.6
key = bpy.data.objects.new("Key_Light", key_data)
key.location = (0.9, -1.0, 2.2)
key.rotation_euler = (math.radians(38.0), 0.0, math.radians(40.0))
bpy.context.collection.objects.link(key)

fill_data = bpy.data.lights.new("Fill", type='POINT')
fill_data.energy = 60.0
fill = bpy.data.objects.new("Fill_Light", fill_data)
fill.location = (-1.4, 0.8, 1.5)
bpy.context.collection.objects.link(fill)

cam_data = bpy.data.cameras.new("Camera")
cam_data.lens = 50.0
cam = bpy.data.objects.new("Camera", cam_data)
cam.location = (0.95, -1.15, 1.35)
target = Vector((0.0, 0.0, TOP_Z + 0.02))
cam.rotation_euler = (target - cam.location).to_track_quat('-Z', 'Y').to_euler()
bpy.context.collection.objects.link(cam)
bpy.context.scene.camera = cam
