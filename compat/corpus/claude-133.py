# claude-133  —  Small public library interior with reading tables, book stacks and skylights
# Blender 4.5 LTS  •  scene construction only (no render, no file output)

import bpy, bmesh, math, random
from mathutils import Vector, Matrix

RNG = random.Random(20250909)

# ----------------------------------------------------------------------------- helpers
def reset_scene():
    bpy.ops.wm.read_factory_settings(use_empty=True)
    sc = bpy.context.scene
    try:
        sc.render.engine = 'BLENDER_EEVEE_NEXT'
    except TypeError:
        sc.render.engine = 'CYCLES'
    sc.unit_settings.system = 'METRIC'


def make_mat(name, color, rough=0.6, metal=0.0, transmission=0.0,
             emission=None, emission_strength=0.0, ior=1.45):
    mat = bpy.data.materials.new(name)
    mat.use_nodes = True
    bsdf = mat.node_tree.nodes["Principled BSDF"]
    bsdf.inputs["Base Color"].default_value = (*color, 1.0)
    bsdf.inputs["Roughness"].default_value = rough
    bsdf.inputs["Metallic"].default_value = metal
    if "Transmission Weight" in bsdf.inputs:
        bsdf.inputs["Transmission Weight"].default_value = transmission
    if "IOR" in bsdf.inputs:
        bsdf.inputs["IOR"].default_value = ior
    if emission is not None:
        bsdf.inputs["Emission Color"].default_value = (*emission, 1.0)
        bsdf.inputs["Emission Strength"].default_value = emission_strength
    if transmission > 0.0:
        mat.blend_method = 'BLEND'
    return mat


def new_bmesh():
    return bmesh.new()


def finish(bm, name, mats, smooth=False, remove_doubles=True):
    """Turn a bmesh into a linked object carrying the given material slots."""
    if remove_doubles:
        bmesh.ops.remove_doubles(bm, verts=bm.verts, dist=1e-5)
    me = bpy.data.meshes.new(name)
    bm.to_mesh(me)
    bm.free()
    for m in mats:
        me.materials.append(m)
    if smooth:
        for p in me.polygons:
            p.use_smooth = True
    ob = bpy.data.objects.new(name, me)
    bpy.context.scene.collection.objects.link(ob)
    return ob


def add_box(bm, center, size, mat_index=0, xform=None):
    """Axis-aligned box (optionally pushed through an extra 4x4 transform)."""
    m = Matrix.Translation(Vector(center)) @ Matrix.Diagonal(
        Vector((size[0], size[1], size[2], 1.0)))
    if xform is not None:
        m = xform @ m
    res = bmesh.ops.create_cube(bm, size=1.0)
    bmesh.ops.transform(bm, matrix=m, verts=res["verts"])
    faces = set()
    for v in res["verts"]:
        faces.update(v.link_faces)
    for f in faces:
        f.material_index = mat_index
    return faces


def add_cylinder(bm, center, radius, depth, mat_index=0, segments=16,
                 xform=None, r2=None):
    m = Matrix.Translation(Vector(center))
    if xform is not None:
        m = xform @ m
    res = bmesh.ops.create_cone(
        bm, cap_ends=True, cap_tris=False, segments=segments,
        radius1=radius, radius2=(radius if r2 is None else r2),
        depth=depth, matrix=m)
    faces = set()
    for v in res["verts"]:
        faces.update(v.link_faces)
    for f in faces:
        f.material_index = mat_index
    return faces


def add_sphere(bm, center, radius, mat_index=0, subdiv=2, xform=None, squash=1.0):
    m = Matrix.Translation(Vector(center)) @ Matrix.Diagonal(
        Vector((1.0, 1.0, squash, 1.0)))
    if xform is not None:
        m = xform @ m
    res = bmesh.ops.create_icosphere(bm, subdivisions=subdiv, radius=radius, matrix=m)
    faces = set()
    for v in res["verts"]:
        faces.update(v.link_faces)
    for f in faces:
        f.material_index = mat_index
    return faces


def look_at(ob, target):
    d = Vector(target) - ob.location
    ob.rotation_euler = d.to_track_quat('-Z', 'Y').to_euler()


# ----------------------------------------------------------------------------- room metrics
X0, X1 = -7.0, 7.0          # interior extents
Y0, Y1 = -5.0, 5.0
WALL_H = 4.2
WALL_T = 0.22
CELL = 0.5                  # ceiling grid cell

SKYLIGHTS = [(-4.0, -2.5), (-4.0, 1.5), (3.0, -2.5), (3.0, 1.5)]
SKY_HALF = 1.0
SHAFT_TOP = WALL_H + 0.75


reset_scene()

# ----------------------------------------------------------------------------- materials
m_floor   = make_mat("Floor_Oak",      (0.30, 0.19, 0.11), rough=0.42)
m_rug     = make_mat("Rug_Wool",       (0.20, 0.26, 0.30), rough=0.92)
m_wall    = make_mat("Wall_Plaster",   (0.83, 0.81, 0.76), rough=0.85)
m_accent  = make_mat("Wall_Accent",    (0.44, 0.50, 0.47), rough=0.85)
m_ceiling = make_mat("Ceiling_Paint",  (0.90, 0.90, 0.88), rough=0.90)
m_shaft   = make_mat("Shaft_White",    (0.95, 0.95, 0.93), rough=0.75)
m_wood    = make_mat("Shelf_Birch",    (0.56, 0.40, 0.24), rough=0.55)
m_wood_d  = make_mat("Table_Walnut",   (0.24, 0.14, 0.08), rough=0.35)
m_metal   = make_mat("Steel_Brushed",  (0.62, 0.63, 0.65), rough=0.35, metal=1.0)
m_fabric  = make_mat("Chair_Felt",     (0.35, 0.29, 0.45), rough=0.90)
m_glass   = make_mat("Glazing",        (0.86, 0.90, 0.93), rough=0.05,
                     transmission=1.0, ior=1.5)
m_lamp    = make_mat("Lamp_Shade",     (0.10, 0.10, 0.11), rough=0.5)
m_bulb    = make_mat("Lamp_Bulb",      (1.0, 0.93, 0.80), rough=0.4,
                     emission=(1.0, 0.86, 0.66), emission_strength=14.0)
m_sky     = make_mat("Sky_Panel",      (0.72, 0.82, 0.95), rough=0.4,
                     emission=(0.62, 0.74, 0.95), emission_strength=6.0)
m_terra   = make_mat("Pot_Terracotta", (0.55, 0.28, 0.18), rough=0.75)
m_leaf    = make_mat("Foliage",        (0.14, 0.32, 0.13), rough=0.70)
m_paper   = make_mat("Paper",          (0.92, 0.90, 0.85), rough=0.85)

BOOK_MATS = [
    make_mat("Book_Crimson",  (0.42, 0.08, 0.09), rough=0.68),
    make_mat("Book_Navy",     (0.08, 0.13, 0.31), rough=0.68),
    make_mat("Book_Forest",   (0.09, 0.24, 0.15), rough=0.68),
    make_mat("Book_Ochre",    (0.55, 0.38, 0.10), rough=0.68),
    make_mat("Book_Cream",    (0.76, 0.71, 0.58), rough=0.72),
    make_mat("Book_Plum",     (0.27, 0.11, 0.27), rough=0.68),
    make_mat("Book_Slate",    (0.22, 0.25, 0.27), rough=0.68),
    make_mat("Book_Rust",     (0.51, 0.24, 0.11), rough=0.68),
    make_mat("Book_Teal",     (0.08, 0.30, 0.32), rough=0.68),
]

# ----------------------------------------------------------------------------- floor + rugs
bm = new_bmesh()
add_box(bm, ((X0 + X1) / 2, (Y0 + Y1) / 2, -0.08),
        (X1 - X0, Y1 - Y0, 0.16), 0)
finish(bm, "Floor", [m_floor])

bm = new_bmesh()
add_box(bm, (3.9, -1.1, 0.012), (5.2, 4.6, 0.024), 0)
add_box(bm, (-3.8, 3.0, 0.012), (3.0, 2.4, 0.024), 0)
finish(bm, "Rugs", [m_rug])

# ----------------------------------------------------------------------------- walls
bm = new_bmesh()
cx, cy = (X0 + X1) / 2, (Y0 + Y1) / 2
w, d = (X1 - X0), (Y1 - Y0)

# -x wall (accent colour), -y wall, +x wall : solid slabs
add_box(bm, (X0 - WALL_T / 2, cy, WALL_H / 2), (WALL_T, d + 2 * WALL_T, WALL_H), 1)
add_box(bm, (X1 + WALL_T / 2, cy, WALL_H / 2), (WALL_T, d + 2 * WALL_T, WALL_H), 0)
add_box(bm, (cx, Y0 - WALL_T / 2, WALL_H / 2), (w, WALL_T, WALL_H), 0)

# +y wall with a band of clerestory windows (z 2.75 .. 3.75)
WIN_Z0, WIN_Z1 = 2.75, 3.75
win_centres = [-4.6, -2.3, 0.0, 2.3, 4.6]
win_hw = 0.85
add_box(bm, (cx, Y1 + WALL_T / 2, WIN_Z0 / 2), (w, WALL_T, WIN_Z0), 0)
add_box(bm, (cx, Y1 + WALL_T / 2, (WIN_Z1 + WALL_H) / 2),
        (w, WALL_T, WALL_H - WIN_Z1), 0)
edges = [X0] + [c + s * win_hw for c in win_centres for s in (-1, 1)] + [X1]
for i in range(0, len(edges) - 1, 2):
    a, b = edges[i], edges[i + 1]
    if b - a > 1e-4:
        add_box(bm, ((a + b) / 2, Y1 + WALL_T / 2, (WIN_Z0 + WIN_Z1) / 2),
                (b - a, WALL_T, WIN_Z1 - WIN_Z0), 0)

# skirting board around the room
sk_h, sk_t = 0.12, 0.025
add_box(bm, (cx, Y0 + sk_t / 2, sk_h / 2), (w, sk_t, sk_h), 2)
add_box(bm, (cx, Y1 - sk_t / 2, sk_h / 2), (w, sk_t, sk_h), 2)
add_box(bm, (X0 + sk_t / 2, cy, sk_h / 2), (sk_t, d, sk_h), 2)
add_box(bm, (X1 - sk_t / 2, cy, sk_h / 2), (sk_t, d, sk_h), 2)
finish(bm, "Walls", [m_wall, m_accent, m_wood_d])

# window glazing + a bright exterior panel behind it (daylight cue)
bm = new_bmesh()
for c in win_centres:
    add_box(bm, (c, Y1 + 0.02, (WIN_Z0 + WIN_Z1) / 2),
            (2 * win_hw - 0.06, 0.02, WIN_Z1 - WIN_Z0 - 0.06), 0)
finish(bm, "Clerestory_Glass", [m_glass])

bm = new_bmesh()
add_box(bm, (cx, Y1 + WALL_T + 0.35, (WIN_Z0 + WIN_Z1) / 2),
        (w, 0.05, WIN_Z1 - WIN_Z0 + 0.4), 0)
finish(bm, "Exterior_Sky_Panel", [m_sky])

# ----------------------------------------------------------------------------- ceiling with skylight openings
def in_skylight(px, py):
    for sx, sy in SKYLIGHTS:
        if abs(px - sx) < SKY_HALF - 1e-6 and abs(py - sy) < SKY_HALF - 1e-6:
            return True
    return False

bm = new_bmesh()
nx = int(round((X1 - X0) / CELL))
ny = int(round((Y1 - Y0) / CELL))
sheet = []
for i in range(nx):
    for j in range(ny):
        ax, bx = X0 + i * CELL, X0 + (i + 1) * CELL
        ay, by = Y0 + j * CELL, Y0 + (j + 1) * CELL
        if in_skylight((ax + bx) / 2, (ay + by) / 2):
            continue
        vs = [bm.verts.new((ax, ay, WALL_H)),
              bm.verts.new((bx, ay, WALL_H)),
              bm.verts.new((bx, by, WALL_H)),
              bm.verts.new((ax, by, WALL_H))]
        sheet.append(bm.faces.new(vs))          # normal +Z
bmesh.ops.remove_doubles(bm, verts=bm.verts, dist=1e-5)
bmesh.ops.solidify(bm, geom=list(bm.faces), thickness=0.28)
for f in bm.faces:
    f.material_index = 0
finish(bm, "Ceiling", [m_ceiling], remove_doubles=False)

# light shafts + skylight glazing
bm_shaft = new_bmesh()
bm_glass = new_bmesh()
t = 0.10
for sx, sy in SKYLIGHTS:
    h = SHAFT_TOP - WALL_H
    zc = WALL_H + h / 2
    add_box(bm_shaft, (sx, sy - SKY_HALF - t / 2, zc), (2 * SKY_HALF + 2 * t, t, h), 0)
    add_box(bm_shaft, (sx, sy + SKY_HALF + t / 2, zc), (2 * SKY_HALF + 2 * t, t, h), 0)
    add_box(bm_shaft, (sx - SKY_HALF - t / 2, sy, zc), (t, 2 * SKY_HALF, h), 0)
    add_box(bm_shaft, (sx + SKY_HALF + t / 2, sy, zc), (t, 2 * SKY_HALF, h), 0)
    # slim frame + glass at the top of the shaft
    add_box(bm_shaft, (sx, sy, SHAFT_TOP + 0.03), (2 * SKY_HALF + 0.16, 0.09, 0.06), 1)
    add_box(bm_shaft, (sx, sy, SHAFT_TOP + 0.03), (0.09, 2 * SKY_HALF + 0.16, 0.06), 1)
    add_box(bm_glass, (sx, sy, SHAFT_TOP), (2 * SKY_HALF, 2 * SKY_HALF, 0.03), 0)
finish(bm_shaft, "Skylight_Shafts", [m_shaft, m_metal])
finish(bm_glass, "Skylight_Glass", [m_glass])

# ----------------------------------------------------------------------------- book stacks
bm_shelf = new_bmesh()
bm_book = new_bmesh()

def shelf_unit(x, y, rot_z, width=1.70, depth=0.32, height=2.10, n_shelves=5,
               fill=0.92):
    """Single-faced shelf unit; local +Y is the open (book) face."""
    X = Matrix.Translation((x, y, 0.0)) @ Matrix.Rotation(rot_z, 4, 'Z')
    side_t, board_t, back_t = 0.032, 0.030, 0.016

    add_box(bm_shelf, (-width / 2 + side_t / 2, 0, height / 2),
            (side_t, depth, height), 0, X)
    add_box(bm_shelf, (width / 2 - side_t / 2, 0, height / 2),
            (side_t, depth, height), 0, X)
    add_box(bm_shelf, (0, -depth / 2 + back_t / 2, height / 2),
            (width, back_t, height), 1, X)
    add_box(bm_shelf, (0, 0, height - board_t / 2), (width, depth, board_t), 0, X)
    add_box(bm_shelf, (0, 0, 0.055), (width - 0.04, depth - 0.05, 0.11), 1, X)  # plinth

    inner = height - 0.11 - board_t
    gap = inner / n_shelves
    for k in range(n_shelves):
        z = 0.11 + gap * k
        if k > 0:
            add_box(bm_shelf, (0, 0, z + board_t / 2), (width, depth, board_t), 0, X)
        # ---- books on this shelf
        top = z + board_t
        cur = -width / 2 + side_t + 0.02
        limit = width / 2 - side_t - 0.02
        max_h = min(gap - board_t - 0.04, 0.30)
        while cur < limit - 0.05:
            if RNG.random() < 0.05:                       # gap / removed volume
                cur += RNG.uniform(0.04, 0.12)
                continue
            bw = RNG.uniform(0.026, 0.062)
            if cur + bw > limit:
                break
            bh = RNG.uniform(0.62, 1.0) * max_h
            bd = RNG.uniform(0.62, 0.80) * depth
            mi = RNG.randrange(len(BOOK_MATS))
            cy_ = depth / 2 - 0.025 - bd / 2
            if RNG.random() < 0.045:                      # leaning volume
                ang = math.radians(RNG.uniform(9.0, 17.0)) * RNG.choice((-1, 1))
                base = Matrix.Translation((cur + bw / 2, cy_, top)) @ \
                       Matrix.Rotation(ang, 4, 'Y')
                add_box(bm_book, (0, 0, bh / 2), (bw, bd, bh), mi, X @ base)
                cur += bw + abs(math.sin(ang)) * bh * 0.55 + 0.004
            else:
                add_box(bm_book, (cur + bw / 2, cy_, top + bh / 2),
                        (bw, bd, bh), mi, X)
                cur += bw + 0.003
        # occasional flat-stacked pile at the end of a shelf
        if RNG.random() < 0.22 and limit - cur > 0.18:
            zz = top
            for _ in range(RNG.randrange(2, 5)):
                th = RNG.uniform(0.028, 0.05)
                add_box(bm_book, (limit - 0.11, 0.02, zz + th / 2),
                        (0.20, 0.26, th), RNG.randrange(len(BOOK_MATS)), X)
                zz += th

# two back-to-back double rows of free-standing stacks
for row_y in (-3.60, -1.80):
    for ux in (-5.55, -3.80, -2.05):
        shelf_unit(ux, row_y + 0.165, 0.0)          # faces +y
        shelf_unit(ux, row_y - 0.165, math.pi)      # faces -y
    # aisle end-panel signage strip
    add_box(bm_shelf, (-1.13, row_y, 1.55), (0.05, 0.66, 0.44), 1)

# perimeter shelving: left wall and part of the back wall
for uy in (0.95, 2.75):
    shelf_unit(X0 + 0.17, uy, -math.pi / 2)
for ux in (-1.6, 0.2, 2.0):
    shelf_unit(ux, Y1 - 0.17, math.pi)

finish(bm_shelf, "Bookshelves", [m_wood, m_wood_d])
finish(bm_book, "Books", BOOK_MATS)

# ----------------------------------------------------------------------------- tables, chairs, desk
bm_f = new_bmesh()       # furniture: 0 walnut, 1 steel, 2 felt, 3 paper

def chair(x, y, rot_z):
    X = Matrix.Translation((x, y, 0.0)) @ Matrix.Rotation(rot_z, 4, 'Z')
    s, sh = 0.44, 0.44
    for sx in (-1, 1):
        for sy in (-1, 1):
            add_box(bm_f, (sx * (s / 2 - 0.04), sy * (s / 2 - 0.04), sh / 2),
                    (0.035, 0.035, sh), 1, X)
    add_box(bm_f, (0, 0, sh + 0.025), (s, s, 0.05), 2, X)
    add_box(bm_f, (0, -s / 2 + 0.03, sh + 0.30), (s, 0.045, 0.48), 2, X)


def table(x, y, rot_z, w=2.20, d=1.10, h=0.74):
    X = Matrix.Translation((x, y, 0.0)) @ Matrix.Rotation(rot_z, 4, 'Z')
    add_box(bm_f, (0, 0, h - 0.02), (w, d, 0.045), 0, X)
    add_box(bm_f, (0, 0, h - 0.10), (w - 0.30, d - 0.26, 0.06), 0, X)     # apron
    for sx in (-1, 1):
        add_box(bm_f, (sx * (w / 2 - 0.14), 0, (h - 0.05) / 2),
                (0.07, d - 0.30, h - 0.05), 1, X)
        add_box(bm_f, (sx * (w / 2 - 0.14), 0, 0.02), (0.10, d - 0.20, 0.04), 1, X)
    # chairs, two per long side
    for sx in (-0.55, 0.55):
        chair(x + math.cos(rot_z) * sx - math.sin(rot_z) * (-(d / 2 + 0.34)),
              y + math.sin(rot_z) * sx + math.cos(rot_z) * (-(d / 2 + 0.34)),
              rot_z)
        chair(x + math.cos(rot_z) * sx - math.sin(rot_z) * (d / 2 + 0.34),
              y + math.sin(rot_z) * sx + math.cos(rot_z) * (d / 2 + 0.34),
              rot_z + math.pi)
    # a few open books / paper on the tabletop
    for _ in range(RNG.randrange(1, 4)):
        px = RNG.uniform(-w / 2 + 0.35, w / 2 - 0.35)
        py = RNG.uniform(-d / 2 + 0.22, d / 2 - 0.22)
        ang = RNG.uniform(-0.5, 0.5)
        P = X @ Matrix.Translation((px, py, h)) @ Matrix.Rotation(ang, 4, 'Z')
        add_box(bm_f, (0, 0, 0.012), (0.30, 0.21, 0.024), 3, P)

TABLES = [(2.40, -2.85, 0.0), (2.40, 0.75, 0.0),
          (5.40, -2.85, 0.0), (5.40, 0.75, 0.0)]
for tx, ty, tr in TABLES:
    table(tx, ty, tr)

# circulation desk (L-shaped counter) near the entrance corner
add_box(bm_f, (5.35, 3.85, 0.52), (3.00, 0.62, 1.04), 0)
add_box(bm_f, (4.05, 2.95, 0.52), (0.62, 1.20, 1.04), 0)
add_box(bm_f, (5.35, 3.85, 1.07), (3.16, 0.76, 0.06), 0)
add_box(bm_f, (4.05, 2.95, 1.07), (0.76, 1.30, 0.06), 0)
add_box(bm_f, (5.35, 3.52, 0.36), (2.86, 0.03, 0.70), 1)     # front reveal
chair(5.35, 4.45, math.pi)

# low display / returns cart
add_box(bm_f, (0.30, -0.30, 0.42), (1.10, 0.46, 0.05), 0)
add_box(bm_f, (0.30, -0.30, 0.78), (1.10, 0.46, 0.05), 0)
for sx in (-1, 1):
    for sy in (-1, 1):
        add_box(bm_f, (0.30 + sx * 0.50, -0.30 + sy * 0.18, 0.40),
                (0.04, 0.04, 0.80), 1)
finish(bm_f, "Furniture", [m_wood_d, m_metal, m_fabric, m_paper])

# books lying on the cart
bm = new_bmesh()
for lvl in (0.455, 0.815):
    cur = -0.48
    while cur < 0.42:
        bw = RNG.uniform(0.03, 0.055)
        add_box(bm, (0.30 + cur + bw / 2, -0.30, lvl + 0.12),
                (bw, 0.26, 0.24), RNG.randrange(len(BOOK_MATS)))
        cur += bw + 0.004
finish(bm, "Cart_Books", BOOK_MATS)

# ----------------------------------------------------------------------------- planters
bm = new_bmesh()
for px, py, sc in ((6.35, -4.40, 1.0), (-6.40, -4.45, 0.85), (0.80, 4.30, 0.95)):
    add_cylinder(bm, (px, py, 0.22 * sc), 0.26 * sc, 0.44 * sc, 0, segments=20,
                 r2=0.30 * sc)
    add_cylinder(bm, (px, py, 0.44 * sc), 0.31 * sc, 0.05 * sc, 0, segments=20)
    for k in range(5):
        a = k * (2 * math.pi / 5) + RNG.uniform(-0.3, 0.3)
        r = RNG.uniform(0.05, 0.20) * sc
        add_sphere(bm, (px + math.cos(a) * r, py + math.sin(a) * r,
                        (0.72 + RNG.uniform(-0.10, 0.16)) * sc),
                   RNG.uniform(0.20, 0.28) * sc, 1, subdiv=2, squash=0.75)
finish(bm, "Planters", [m_terra, m_leaf], smooth=True)

# ----------------------------------------------------------------------------- pendant lamps over the tables
bm = new_bmesh()
for tx, ty, _ in TABLES:
    for sx in (-0.55, 0.55):
        add_cylinder(bm, (tx + sx, ty, (WALL_H + 2.05) / 2), 0.012,
                     WALL_H - 2.05, 0, segments=8)
        add_cylinder(bm, (tx + sx, ty, 1.98), 0.19, 0.17, 0, segments=20, r2=0.07)
        add_sphere(bm, (tx + sx, ty, 1.90), 0.055, 1, subdiv=2)
finish(bm, "Pendants", [m_lamp, m_bulb], smooth=True)

# ----------------------------------------------------------------------------- lighting
def add_light(name, ltype, loc, energy, color=(1, 1, 1), size=1.0, rot=None):
    data = bpy.data.lights.new(name, ltype)
    data.energy = energy
    data.color = color
    if ltype == 'AREA':
        data.shape = 'SQUARE'
        data.size = size
    elif ltype in {'POINT', 'SPOT'}:
        data.shadow_soft_size = size
    ob = bpy.data.objects.new(name, data)
    ob.location = loc
    if rot:
        ob.rotation_euler = rot
    bpy.context.scene.collection.objects.link(ob)
    return ob

# daylight pouring down each shaft
for i, (sx, sy) in enumerate(SKYLIGHTS):
    add_light(f"Skylight_Area_{i}", 'AREA', (sx, sy, SHAFT_TOP - 0.10),
              320.0, (0.90, 0.94, 1.0), size=1.9)

# soft bounce filling the room from the clerestory band
add_light("Clerestory_Fill", 'AREA', (0.0, Y1 - 0.25, 3.25), 220.0,
          (0.85, 0.90, 1.0), size=6.0,
          rot=(math.radians(90), 0.0, 0.0))

# warm task light from the pendants
for tx, ty, _ in TABLES:
    add_light(f"Pendant_{tx}_{ty}", 'POINT', (tx, ty, 1.90), 32.0,
              (1.0, 0.85, 0.66), size=0.12)

add_light("Desk_Fill", 'POINT', (5.0, 3.4, 2.60), 40.0, (1.0, 0.90, 0.78), size=0.35)
add_light("Stacks_Fill", 'AREA', (-3.8, -2.7, 3.60), 90.0,
          (1.0, 0.94, 0.86), size=3.0)

sun = add_light("Sun", 'SUN', (0.0, 0.0, 9.0), 3.2, (1.0, 0.96, 0.90),
                rot=(math.radians(38), 0.0, math.radians(-42)))
sun.data.angle = math.radians(1.6)

# world: pale overcast sky so the glazing reads correctly
world = bpy.data.worlds.new("LibraryWorld")
world.use_nodes = True
bg = world.node_tree.nodes["Background"]
bg.inputs["Color"].default_value = (0.42, 0.50, 0.62, 1.0)
bg.inputs["Strength"].default_value = 0.6
bpy.context.scene.world = world

# ----------------------------------------------------------------------------- camera
cam_data = bpy.data.cameras.new("Camera")
cam_data.lens = 20.0
cam_data.clip_start = 0.05
cam_data.clip_end = 200.0
cam_data.dof.use_dof = True
cam_data.dof.focus_distance = 6.5
cam_data.dof.aperture_fstop = 4.0
cam = bpy.data.objects.new("Camera", cam_data)
cam.location = Vector((5.85, -4.25, 1.68))
bpy.context.scene.collection.objects.link(cam)
look_at(cam, Vector((-2.20, 0.60, 1.35)))
bpy.context.scene.camera = cam

# a second, higher vantage over the stacks (not active)
cam2_data = bpy.data.cameras.new("Camera_Stacks")
cam2_data.lens = 28.0
cam2 = bpy.data.objects.new("Camera_Stacks", cam2_data)
cam2.location = Vector((-0.40, -4.55, 2.60))
bpy.context.scene.collection.objects.link(cam2)
look_at(cam2, Vector((-4.60, -2.60, 1.10)))

bpy.context.scene.render.resolution_x = 1920
bpy.context.scene.render.resolution_y = 1080
