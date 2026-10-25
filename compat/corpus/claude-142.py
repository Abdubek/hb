"""
claude-142 - Courtyard housing block with balconies, external stairs and a shared garden.

Builds, from an empty factory startup:
  * a three-storey perimeter block (42 x 34 m) wrapped around a 24 x 16 m courtyard,
    with punched-window facades (sills, lintels, floor bands, plinth) inside and out
    and a vaulted entrance passage through the south wing,
  * continuous access galleries on levels 1 and 2 facing the courtyard, carried on
    slender columns, with open balustrades and projecting private balconies clad in
    coloured panels,
  * two external dog-leg stair cores in opposite courtyard corners (treads, sloping
    soffits, half landings, support posts, sloped handrails),
  * a flat roof with parapets, gravel finish and a PV array over the north wing,
  * a shared garden in the courtyard: paving, raised lawns with kerbs, clipped hedges,
    trees, planters, benches, lamp standards and a central water basin,
  * sun + sky lighting, warm lamp fills, and a three-quarter aerial camera.

Nothing is rendered and nothing is written to disk.
"""

import bpy
import bmesh
import math
import random
from collections import defaultdict
from mathutils import Vector, Matrix

random.seed(4142)

# ----------------------------------------------------------------- scene reset
bpy.ops.wm.read_factory_settings(use_empty=True)
scene = bpy.context.scene

for engine in ('BLENDER_EEVEE_NEXT', 'BLENDER_EEVEE'):
    try:
        scene.render.engine = engine
        break
    except TypeError:
        continue

scene.unit_settings.system = 'METRIC'
scene.render.resolution_x = 1920
scene.render.resolution_y = 1080


def new_collection(name):
    col = bpy.data.collections.new(name)
    scene.collection.children.link(col)
    return col


COL_BUILD = new_collection("Building")
COL_ACCESS = new_collection("Access")
COL_GARDEN = new_collection("Garden")
COL_SITE = new_collection("Site")
COL_LIGHT = new_collection("Lighting")

# -------------------------------------------------------------------- geometry
OX, OY = 21.0, 17.0          # outer half dimensions of the block
IX, IY = 12.0, 8.0           # courtyard half dimensions
GAL = 1.7                    # access gallery depth
GX, GY = IX - GAL, IY - GAL  # gallery edge (open courtyard half dims)
FLOOR_H = 3.2
LEVELS = 3
ROOF_Z = LEVELS * FLOOR_H
WALL_T = 0.32
SILL = 0.95
HEAD = 2.55
WIN_W = 1.55
DOOR_W = 1.2
SLAB_T = 0.32
DECK_T = 0.22
RAIL_H = 1.05

# ring of wing footprints  (x0, x1, y0, y1)
RING = [
    (-OX, OX, -OY, -IY),
    (-OX, OX, IY, OY),
    (-OX, -IX, -IY, IY),
    (IX, OX, -IY, IY),
]


# ------------------------------------------------------------------- utilities
def make_mat(name, color, rough=0.7, metal=0.0, emit=None, emit_str=0.0,
             transmission=0.0, ior=1.45):
    mat = bpy.data.materials.new(name)
    mat.use_nodes = True
    bsdf = mat.node_tree.nodes.get("Principled BSDF")

    def put(key, value):
        if bsdf is not None and key in bsdf.inputs:
            bsdf.inputs[key].default_value = value

    put("Base Color", (color[0], color[1], color[2], 1.0))
    put("Roughness", rough)
    put("Metallic", metal)
    put("IOR", ior)
    if transmission:
        put("Transmission Weight", transmission)
    if emit is not None:
        put("Emission Color", (emit[0], emit[1], emit[2], 1.0))
        put("Emission Strength", emit_str)
    return mat


def box_matrix(center, size, rot=None):
    m = Matrix.Translation(Vector(center))
    if rot is not None:
        m = m @ rot
    return m @ Matrix.Diagonal(Vector((size[0], size[1], size[2], 1.0)))


def add_box(bm, center, size, rot=None):
    bmesh.ops.create_cube(bm, size=1.0, matrix=box_matrix(center, size, rot))


def add_box_local(bm, M, center, size):
    bmesh.ops.create_cube(bm, size=1.0, matrix=M @ box_matrix(center, size))


def add_ico(bm, radius, center, subdiv=2, scale=(1.0, 1.0, 1.0)):
    m = Matrix.Translation(Vector(center)) @ Matrix.Diagonal(
        Vector((scale[0], scale[1], scale[2], 1.0)))
    try:
        bmesh.ops.create_icosphere(bm, subdivisions=subdiv, radius=radius, matrix=m)
    except TypeError:
        bmesh.ops.create_icosphere(bm, subdivisions=subdiv, diameter=radius, matrix=m)


def add_cyl(bm, r_bottom, r_top, depth, center, segments=14, rot=None):
    m = Matrix.Translation(Vector(center))
    if rot is not None:
        m = m @ rot
    try:
        bmesh.ops.create_cone(bm, cap_ends=True, cap_tris=False, segments=segments,
                              radius1=r_bottom, radius2=r_top, depth=depth, matrix=m)
    except TypeError:
        bmesh.ops.create_cone(bm, cap_ends=True, cap_tris=False, segments=segments,
                              diameter1=r_bottom * 2.0, diameter2=r_top * 2.0,
                              depth=depth, matrix=m)


def solid_segments(length, gaps):
    """Return the solid stretches of [0, length] left over after removing gaps."""
    out = []
    cursor = 0.0
    for g0, g1 in sorted(gaps):
        g0 = max(0.0, g0)
        g1 = min(length, g1)
        if g1 <= g0:
            continue
        if g0 - cursor > 1e-4:
            out.append((cursor, g0))
        cursor = max(cursor, g1)
    if length - cursor > 1e-4:
        out.append((cursor, length))
    return out


def dir_rot(direction, local_axis=Vector((0.0, 1.0, 0.0))):
    """Rotation matrix taking local_axis onto direction."""
    d = Vector(direction)
    if d.length < 1e-9:
        return Matrix.Identity(4)
    return local_axis.rotation_difference(d.normalized()).to_matrix().to_4x4()


def add_railing(bm, a, b, height=RAIL_H, post_gap=1.15, bal_gap=0.30):
    """Open balustrade following the 3D line a -> b (works for sloping runs)."""
    a = Vector(a)
    b = Vector(b)
    v = b - a
    L = v.length
    if L < 0.15:
        return
    d = v.normalized()
    rot = dir_rot(d, Vector((1.0, 0.0, 0.0)))
    mid = (a + b) * 0.5
    add_box(bm, mid + Vector((0, 0, height)), (L, 0.07, 0.07), rot)
    add_box(bm, mid + Vector((0, 0, height * 0.55)), (L, 0.05, 0.05), rot)
    nb = max(1, int(L / bal_gap))
    for i in range(1, nb):
        p = a + v * (i / nb)
        add_box(bm, p + Vector((0, 0, height * 0.5)), (0.025, 0.025, height))
    npost = max(1, int(L / post_gap))
    for i in range(npost + 1):
        p = a + v * (i / npost)
        add_box(bm, p + Vector((0, 0, height * 0.5)), (0.07, 0.07, height + 0.06))


def railing_with_gaps(bm, a, b, gaps, height=RAIL_H):
    a = Vector(a)
    b = Vector(b)
    L = (b - a).length
    d = (b - a).normalized()
    for s, e in solid_segments(L, gaps):
        add_railing(bm, a + d * s, a + d * e, height)


def add_ramp(bm, a, b, width, thick=0.24):
    """Sloping slab (stair soffit) between two 3D points."""
    a = Vector(a)
    b = Vector(b)
    v = b - a
    L = v.length
    rot = dir_rot(v)
    perp = (rot @ Vector((0.0, 0.0, 1.0))).normalized()
    center = (a + b) * 0.5 - perp * (thick * 0.5 + 0.05)
    add_box(bm, center, (width, L + 0.1, thick), rot)


def add_flight(bm_solid, bm_metal, p_bottom, p_top, width, steps, rails=(-1, 1)):
    """Straight flight: treads, sloping soffit and handrails."""
    a = Vector(p_bottom)
    b = Vector(p_top)
    horiz = Vector((b.x - a.x, b.y - a.y, 0.0))
    run = horiz.length
    rise = b.z - a.z
    hdir = horiz.normalized()
    going = run / steps
    riser = rise / steps
    rot = dir_rot(hdir)
    across = (rot @ Vector((1.0, 0.0, 0.0))).normalized()
    for i in range(1, steps + 1):
        c = a + hdir * (going * (i - 0.5)) + Vector((0, 0, i * riser - 0.075))
        add_box(bm_solid, c, (width, going, 0.15), rot)
    add_ramp(bm_solid, a, b, width + 0.12, 0.26)
    for s in rails:
        off = across * (s * (width * 0.5 - 0.06))
        add_railing(bm_metal, a + off + Vector((0, 0, riser)), b + off, 1.02)


# ------------------------------------------------------------------- materials
MAT = {
    'wall':    make_mat("Facade_Render", (0.780, 0.745, 0.685), 0.82),
    'trim':    make_mat("Precast_Trim", (0.870, 0.860, 0.830), 0.65),
    'struct':  make_mat("Concrete_Structure", (0.560, 0.552, 0.535), 0.86),
    'glass':   make_mat("Window_Glass", (0.045, 0.062, 0.078), 0.08, metal=0.15),
    'lit':     make_mat("Window_Lit", (0.90, 0.72, 0.45), 0.35,
                        emit=(1.0, 0.78, 0.50), emit_str=3.0),
    'door':    make_mat("Timber_Door", (0.230, 0.130, 0.070), 0.55),
    'metal':   make_mat("Dark_Metalwork", (0.085, 0.088, 0.092), 0.42, metal=0.85),
    'stair':   make_mat("Stair_Concrete", (0.620, 0.610, 0.595), 0.80),
    'accent1': make_mat("Panel_Terracotta", (0.620, 0.245, 0.135), 0.55),
    'accent2': make_mat("Panel_Teal", (0.110, 0.360, 0.375), 0.55),
    'accent3': make_mat("Panel_Ochre", (0.760, 0.545, 0.150), 0.55),
    'roofpv':  make_mat("PV_Panel", (0.030, 0.045, 0.090), 0.20, metal=0.45),
    'gravel':  make_mat("Roof_Gravel", (0.400, 0.385, 0.360), 0.95),
    'paving':  make_mat("Courtyard_Paving", (0.545, 0.520, 0.485), 0.88),
    'walk':    make_mat("Sidewalk", (0.480, 0.470, 0.455), 0.92),
    'street':  make_mat("Asphalt", (0.105, 0.105, 0.110), 0.95),
    'lawn':    make_mat("Lawn", (0.115, 0.320, 0.085), 0.94),
    'kerb':    make_mat("Kerb_Stone", (0.640, 0.620, 0.585), 0.85),
    'hedge':   make_mat("Clipped_Hedge", (0.085, 0.245, 0.075), 0.92),
    'trunk':   make_mat("Tree_Bark", (0.180, 0.135, 0.098), 0.90),
    'leaf':    make_mat("Tree_Foliage", (0.135, 0.300, 0.100), 0.88),
    'wood':    make_mat("Bench_Timber", (0.400, 0.245, 0.125), 0.62),
    'water':   make_mat("Water", (0.045, 0.140, 0.165), 0.06, transmission=0.85, ior=1.33),
    'soil':    make_mat("Soil", (0.130, 0.095, 0.070), 0.96),
    'pot':     make_mat("Planter_Concrete", (0.660, 0.640, 0.610), 0.80),
    'glow':    make_mat("Lamp_Globe", (1.0, 0.90, 0.72), 0.3,
                        emit=(1.0, 0.86, 0.62), emit_str=8.0),
}

BM = defaultdict(bmesh.new)


# ------------------------------------------------------- facade wall generator
def build_wall(p0, p1, doors_ground=False, voids=(), plinth=False, lit_prob=0.26):
    a = Vector((p0[0], p0[1], 0.0))
    b = Vector((p1[0], p1[1], 0.0))
    v = b - a
    L = v.length
    d = v.normalized()
    M = Matrix.Translation(a) @ Matrix.Rotation(math.atan2(d.y, d.x), 4, 'Z')
    t = WALL_T

    void_iv = []
    for vx, vy, vw in voids:
        lx = (Vector((vx, vy, 0.0)) - a).dot(d)
        void_iv.append((lx - vw * 0.5, lx + vw * 0.5))

    bays = max(2, int(round(L / 3.25)))
    step = L / bays
    centers = [step * (i + 0.5) for i in range(bays)]

    for lvl in range(LEVELS):
        z0 = lvl * FLOOR_H
        gaps_full = list(void_iv) if lvl == 0 else []

        cols = []
        for i, c in enumerate(centers):
            if any(g0 - 1.0 < c < g1 + 1.0 for g0, g1 in gaps_full):
                continue
            is_door = doors_ground and lvl == 0 and (i % 3 == 1)
            cols.append((c, DOOR_W if is_door else WIN_W, is_door))

        open_iv = [(c - w * 0.5, c + w * 0.5) for c, w, _ in cols]
        door_iv = [(c - w * 0.5, c + w * 0.5) for c, w, dr in cols if dr]

        for x0, x1 in solid_segments(L, door_iv + gaps_full):
            add_box_local(BM['wall'], M, ((x0 + x1) * 0.5, 0.0, z0 + SILL * 0.5),
                          (x1 - x0, t, SILL))
        for x0, x1 in solid_segments(L, open_iv + gaps_full):
            add_box_local(BM['wall'], M, ((x0 + x1) * 0.5, 0.0, z0 + (SILL + HEAD) * 0.5),
                          (x1 - x0, t, HEAD - SILL))
        for x0, x1 in solid_segments(L, gaps_full):
            add_box_local(BM['wall'], M, ((x0 + x1) * 0.5, 0.0, z0 + (HEAD + FLOOR_H) * 0.5),
                          (x1 - x0, t, FLOOR_H - HEAD))

        if plinth and lvl == 0:
            for x0, x1 in solid_segments(L, gaps_full):
                add_box_local(BM['trim'], M, ((x0 + x1) * 0.5, 0.0, 0.38),
                              (x1 - x0, t + 0.22, 0.76))
        if lvl > 0:
            add_box_local(BM['trim'], M, (L * 0.5, 0.0, z0), (L, t + 0.24, 0.30))

        for c, w, is_door in cols:
            if is_door:
                add_box_local(BM['door'], M, (c, 0.0, z0 + HEAD * 0.5),
                              (w - 0.10, 0.12, HEAD - 0.05))
                add_box_local(BM['trim'], M, (c, 0.0, z0 + HEAD + 0.06),
                              (w + 0.36, t + 0.30, 0.12))
            else:
                pane = BM['lit'] if random.random() < lit_prob else BM['glass']
                add_box_local(pane, M, (c, 0.0, z0 + (SILL + HEAD) * 0.5),
                              (w - 0.13, 0.07, HEAD - SILL - 0.11))
                add_box_local(BM['trim'], M, (c, 0.0, z0 + (SILL + HEAD) * 0.5),
                              (0.07, 0.11, HEAD - SILL - 0.10))
                add_box_local(BM['trim'], M, (c, 0.0, z0 + SILL - 0.04),
                              (w + 0.34, t + 0.20, 0.10))
                add_box_local(BM['trim'], M, (c, 0.0, z0 + HEAD + 0.05),
                              (w + 0.34, t + 0.16, 0.11))

    add_box_local(BM['trim'], M, (L * 0.5, 0.0, ROOF_Z + 0.06), (L, t + 0.34, 0.36))


# ------------------------------------------------------------ structural shell
def add_ring(bm, z_top, thick, shrink=0.0):
    for x0, x1, y0, y1 in RING:
        add_box(bm, ((x0 + x1) * 0.5, (y0 + y1) * 0.5, z_top - thick * 0.5),
                (x1 - x0 - 2 * shrink, y1 - y0 - 2 * shrink, thick))


# floor slabs and roof deck
for lvl in range(LEVELS + 1):
    add_ring(BM['struct'], lvl * FLOOR_H, SLAB_T)
add_ring(BM['gravel'], ROOF_Z + 0.10, 0.10, shrink=0.30)

# outer envelope
build_wall((-OX, -OY), (OX, -OY), plinth=True, voids=[(0.0, -OY, 4.2)], lit_prob=0.22)
build_wall((OX, -OY), (OX, OY), plinth=True, lit_prob=0.22)
build_wall((OX, OY), (-OX, OY), plinth=True, lit_prob=0.22)
build_wall((-OX, OY), (-OX, -OY), plinth=True, lit_prob=0.22)

# courtyard envelope (front doors on the ground floor)
build_wall((-IX, -IY), (IX, -IY), doors_ground=True, voids=[(0.0, -IY, 4.2)], lit_prob=0.34)
build_wall((IX, -IY), (IX, IY), doors_ground=True, lit_prob=0.34)
build_wall((IX, IY), (-IX, IY), doors_ground=True, lit_prob=0.34)
build_wall((-IX, IY), (-IX, -IY), doors_ground=True, lit_prob=0.34)

# entrance passage lining and paving under the gate
for sx in (-2.35, 2.35):
    add_box(BM['trim'], (sx, -(IY + OY) * 0.5, 1.6), (0.30, OY - IY, 3.2))
add_box(BM['paving'], (0.0, -(IY + OY) * 0.5, 0.02), (4.6, OY - IY, 0.10))

# roof parapets, outer and courtyard side
PAR_H = 1.05
for cx, cy, sx, sy in ((0.0, -OY, 2 * OX, WALL_T + 0.1),
                       (0.0, OY, 2 * OX, WALL_T + 0.1),
                       (-OX, 0.0, WALL_T + 0.1, 2 * OY),
                       (OX, 0.0, WALL_T + 0.1, 2 * OY)):
    add_box(BM['wall'], (cx, cy, ROOF_Z + PAR_H * 0.5 + 0.2), (sx, sy, PAR_H))
    add_box(BM['trim'], (cx, cy, ROOF_Z + PAR_H + 0.24), (sx + 0.22, sy + 0.22, 0.12))
for cx, cy, sx, sy in ((0.0, -IY, 2 * IX, WALL_T + 0.1),
                       (0.0, IY, 2 * IX, WALL_T + 0.1),
                       (-IX, 0.0, WALL_T + 0.1, 2 * IY),
                       (IX, 0.0, WALL_T + 0.1, 2 * IY)):
    add_box(BM['wall'], (cx, cy, ROOF_Z + 0.62), (sx, sy, 0.85))
    add_box(BM['trim'], (cx, cy, ROOF_Z + 1.09), (sx + 0.2, sy + 0.2, 0.10))

# rooftop plant enclosures and PV array over the north wing
for px in (-13.0, 4.0):
    add_box(BM['struct'], (px, 13.0, ROOF_Z + 0.85), (3.2, 2.4, 1.7))
    add_box(BM['metal'], (px, 13.0, ROOF_Z + 1.80), (3.4, 2.6, 0.20))
for row_y in (10.2, 12.6, 15.0):
    for px in [-18.0 + 2.15 * i for i in range(18)]:
        rot = Matrix.Rotation(math.radians(28.0), 4, 'X')
        add_box(BM['roofpv'], (px, row_y, ROOF_Z + 0.62), (2.0, 1.15, 0.06), rot)
        for sx in (-0.85, 0.85):
            add_box(BM['metal'], (px + sx, row_y + 0.42, ROOF_Z + 0.35), (0.06, 0.06, 0.5))


# --------------------------------------------------- galleries and balconies
GALLERY_LEVELS = (1, 2)
STAIR_SW = Vector((-8.9, -GY, 0.0))
STAIR_NE = Vector((8.9, GY, 0.0))
STAIR_HALF_W = 1.45  # half of the two-flight stair well width

BALCONY = {
    'south': [-4.0, 0.0, 4.0, 7.6],
    'north': [-7.6, -4.0, 0.0, 4.0],
    'west': [0.0, 4.0],
    'east': [-4.0, 0.0],
}
BAL_W = 2.8
BAL_D = 1.5

for li, lvl in enumerate(GALLERY_LEVELS):
    z = lvl * FLOOR_H
    # deck ring
    add_box(BM['struct'], (0.0, -(IY + GY) * 0.5, z - DECK_T * 0.5), (2 * IX, GAL, DECK_T))
    add_box(BM['struct'], (0.0, (IY + GY) * 0.5, z - DECK_T * 0.5), (2 * IX, GAL, DECK_T))
    add_box(BM['struct'], (-(IX + GX) * 0.5, 0.0, z - DECK_T * 0.5), (GAL, 2 * IY, DECK_T))
    add_box(BM['struct'], ((IX + GX) * 0.5, 0.0, z - DECK_T * 0.5), (GAL, 2 * IY, DECK_T))
    # fascia band on the courtyard edge
    for cx, cy, sx, sy in ((0.0, -GY, 2 * GX, 0.12), (0.0, GY, 2 * GX, 0.12),
                           (-GX, 0.0, 0.12, 2 * GY), (GX, 0.0, 0.12, 2 * GY)):
        add_box(BM['trim'], (cx, cy, z - DECK_T * 0.5), (sx, sy, DECK_T + 0.06))

    # projecting balconies with solid coloured parapets
    idx = 0
    for edge, values in BALCONY.items():
        for val in values:
            acc = ('accent1', 'accent2', 'accent3')[(idx + li) % 3]
            idx += 1
            if edge in ('south', 'north'):
                sgn = -1.0 if edge == 'south' else 1.0
                cx = val
                cy = sgn * (GY + BAL_D * 0.5)
                add_box(BM['struct'], (cx, cy, z - DECK_T * 0.5), (BAL_W, BAL_D, DECK_T))
                add_box(BM[acc], (cx, sgn * (GY + BAL_D), z + 0.52), (BAL_W, 0.10, 1.04))
                for s in (-1.0, 1.0):
                    add_box(BM[acc], (cx + s * BAL_W * 0.5, cy, z + 0.52),
                            (0.10, BAL_D, 1.04))
                add_box(BM['metal'], (cx, sgn * (GY + BAL_D), z + 1.07), (BAL_W + 0.1, 0.16, 0.07))
            else:
                sgn = -1.0 if edge == 'west' else 1.0
                cy = val
                cx = sgn * (GX + BAL_D * 0.5)
                add_box(BM['struct'], (cx, cy, z - DECK_T * 0.5), (BAL_D, BAL_W, DECK_T))
                add_box(BM[acc], (sgn * (GX + BAL_D), cy, z + 0.52), (0.10, BAL_W, 1.04))
                for s in (-1.0, 1.0):
                    add_box(BM[acc], (cx, cy + s * BAL_W * 0.5, z + 0.52),
                            (BAL_D, 0.10, 1.04))
                add_box(BM['metal'], (sgn * (GX + BAL_D), cy, z + 1.07), (0.16, BAL_W + 0.1, 0.07))

    # gallery balustrades, opened at balconies and stair arrivals
    sw_gaps = [(STAIR_SW.x - STAIR_HALF_W + GX, STAIR_SW.x - 0.05 + GX),
               (STAIR_SW.x + 0.05 + GX, STAIR_SW.x + STAIR_HALF_W + GX)]
    ne_gaps = [(STAIR_NE.x - STAIR_HALF_W + GX, STAIR_NE.x - 0.05 + GX),
               (STAIR_NE.x + 0.05 + GX, STAIR_NE.x + STAIR_HALF_W + GX)]

    s_gaps = [(x + GX - BAL_W * 0.5, x + GX + BAL_W * 0.5) for x in BALCONY['south']] + sw_gaps
    n_gaps = [(x + GX - BAL_W * 0.5, x + GX + BAL_W * 0.5) for x in BALCONY['north']] + ne_gaps
    w_gaps = [(y + GY - BAL_W * 0.5, y + GY + BAL_W * 0.5) for y in BALCONY['west']]
    e_gaps = [(y + GY - BAL_W * 0.5, y + GY + BAL_W * 0.5) for y in BALCONY['east']]

    railing_with_gaps(BM['metal'], (-GX, -GY, z), (GX, -GY, z), s_gaps)
    railing_with_gaps(BM['metal'], (-GX, GY, z), (GX, GY, z), n_gaps)
    railing_with_gaps(BM['metal'], (-GX, -GY, z), (-GX, GY, z), w_gaps)
    railing_with_gaps(BM['metal'], (GX, -GY, z), (GX, GY, z), e_gaps)

# columns carrying the galleries at ground level
def stair_zone(x, y):
    for base, sgn in ((STAIR_SW, 1.0), (STAIR_NE, -1.0)):
        lx = (x - base.x) * (1.0 if sgn > 0 else -1.0)
        ly = (y - base.y) * sgn
        if abs(lx) < 1.8 and -0.4 < ly < 4.2:
            return True
    return False


col_h = FLOOR_H - DECK_T
for gx in [-GX + 0.2 + 3.35 * i for i in range(int((2 * GX - 0.4) / 3.35) + 1)]:
    for gy in (-GY + 0.18, GY - 0.18):
        if stair_zone(gx, gy):
            continue
        add_box(BM['struct'], (gx, gy, col_h * 0.5), (0.26, 0.26, col_h))
for gy in [-GY + 0.2 + 3.15 * i for i in range(int((2 * GY - 0.4) / 3.15) + 1)]:
    for gx in (-GX + 0.18, GX - 0.18):
        if stair_zone(gx, gy):
            continue
        add_box(BM['struct'], (gx, gy, col_h * 0.5), (0.26, 0.26, col_h))


# --------------------------------------------------------- external stair core
def build_stair(M):
    """Dog-leg external stair; local +Y points into the courtyard, y=0 is the gallery edge."""
    def P(x, y, z):
        return M @ Vector((x, y, z))

    width = 1.30
    xa, xb = -0.75, 0.75

    # ground -> level 1 (single straight run), level 1 -> half landing -> level 2
    add_flight(BM['stair'], BM['metal'], P(xa, 4.8, 0.0), P(xa, 0.0, FLOOR_H), width, 16)
    add_flight(BM['stair'], BM['metal'], P(xb, 0.0, FLOOR_H), P(xb, 2.4, FLOOR_H + 1.6), width, 8)
    add_flight(BM['stair'], BM['metal'], P(xa, 2.4, FLOOR_H + 1.6), P(xa, 0.0, 2 * FLOOR_H), width, 8)

    # half landing and its supports
    add_box(BM['stair'], P(0.0, 3.0, FLOOR_H + 1.6 - 0.13), (2.9, 1.25, 0.26),
            M.to_3x3().to_4x4())
    for sx in (-1.25, 1.25):
        add_box(BM['stair'], P(sx, 3.45, (FLOOR_H + 1.6) * 0.5),
                (0.26, 0.26, FLOOR_H + 1.6), M.to_3x3().to_4x4())

    # landing balustrade (three open sides)
    add_railing(BM['metal'], P(-1.45, 3.62, FLOOR_H + 1.6), P(1.45, 3.62, FLOOR_H + 1.6), 1.02)
    add_railing(BM['metal'], P(-1.45, 2.38, FLOOR_H + 1.6), P(-1.45, 3.62, FLOOR_H + 1.6), 1.02)
    add_railing(BM['metal'], P(1.45, 2.38, FLOOR_H + 1.6), P(1.45, 3.62, FLOOR_H + 1.6), 1.02)

    # arrival apron at the foot of the stair
    add_box(BM['paving'], P(0.0, 5.25, 0.03), (3.1, 1.2, 0.10), M.to_3x3().to_4x4())


build_stair(Matrix.Translation(STAIR_SW))
build_stair(Matrix.Translation(STAIR_NE) @ Matrix.Rotation(math.pi, 4, 'Z'))


# --------------------------------------------------------------- shared garden
# site, street and sidewalk
add_box(BM['street'], (0.0, 0.0, -0.30), (200.0, 200.0, 0.6))
add_box(BM['walk'], (0.0, 0.0, 0.02), (2 * OX + 9.0, 2 * OY + 9.0, 0.12))

# courtyard paving
add_box(BM['paving'], (0.0, 0.0, 0.01), (2 * IX, 2 * IY, 0.12))

# raised lawns with stone kerbs
LAWNS = [(-7.2, -1.8, -4.4, 4.4), (1.8, 7.2, -4.4, 4.4)]
for x0, x1, y0, y1 in LAWNS:
    cx, cy = (x0 + x1) * 0.5, (y0 + y1) * 0.5
    add_box(BM['kerb'], (cx, cy, 0.13), (x1 - x0 + 0.24, y1 - y0 + 0.24, 0.26))
    add_box(BM['lawn'], (cx, cy, 0.19), (x1 - x0, y1 - y0, 0.20))

# clipped hedges flanking the central walk
for sx in (-1.98, 1.98):
    for y0, y1 in ((-4.3, -2.4), (2.4, 4.3)):
        add_box(BM['hedge'], (sx, (y0 + y1) * 0.5, 0.55), (0.55, y1 - y0, 0.72))
bmesh.ops.bevel(BM['hedge'], geom=list(BM['hedge'].verts) + list(BM['hedge'].edges) +
                list(BM['hedge'].faces), offset=0.09, segments=2, affect='EDGES')

# central water basin
add_cyl(BM['kerb'], 1.70, 1.70, 0.62, (0.0, 0.0, 0.30), segments=28)
add_cyl(BM['water'], 1.52, 1.52, 0.36, (0.0, 0.0, 0.40), segments=28)


def add_tree(pos, height=5.6, spread=2.1, seed=0):
    rnd = random.Random(seed)
    x, y = pos
    add_cyl(BM['trunk'], 0.26, 0.15, height * 0.6, (x, y, height * 0.30), segments=10)
    for k in range(3):
        ang = rnd.uniform(0, math.tau)
        tilt = Matrix.Rotation(rnd.uniform(0.5, 0.9), 4, 'Y') @ Matrix.Rotation(0, 4, 'X')
        rot = Matrix.Rotation(ang, 4, 'Z') @ tilt
        add_cyl(BM['trunk'], 0.10, 0.05, 1.5,
                (x + math.cos(ang) * 0.35, y + math.sin(ang) * 0.35, height * 0.62),
                segments=8, rot=rot)
    for k in range(5):
        off = Vector((rnd.uniform(-spread * 0.5, spread * 0.5),
                      rnd.uniform(-spread * 0.5, spread * 0.5),
                      height * 0.66 + rnd.uniform(-0.25, 1.0)))
        r = spread * rnd.uniform(0.58, 0.88)
        add_ico(BM['leaf'], 1.0, (x + off.x, y + off.y, off.z), subdiv=2,
                scale=(r, r, r * 0.85))


for i, (tx, ty) in enumerate([(-4.6, -2.6), (-4.6, 2.6), (4.6, -2.6), (4.6, 2.6)]):
    add_tree((tx, ty), height=5.2 + 0.5 * (i % 2), spread=2.0 + 0.25 * (i % 3), seed=10 + i)
for i, (tx, ty) in enumerate([(-14.0, -21.0), (0.0, -21.0), (14.0, -21.0),
                              (-14.0, 21.0), (0.0, 21.0), (14.0, 21.0)]):
    add_tree((tx, ty), height=6.4, spread=2.5, seed=40 + i)


def add_bench(pos, angle):
    R = Matrix.Rotation(angle, 4, 'Z')
    o = Vector((pos[0], pos[1], 0.0))
    for i in range(4):
        add_box(BM['wood'], o + R @ Vector((0.0, -0.27 + i * 0.18, 0.46)),
                (1.80, 0.15, 0.06), R)
    for i in range(3):
        add_box(BM['wood'], o + R @ Vector((0.0, 0.32, 0.66 + i * 0.17)),
                (1.80, 0.06, 0.13), R)
    for sx in (-0.78, 0.78):
        add_box(BM['metal'], o + R @ Vector((sx, -0.22, 0.22)), (0.07, 0.07, 0.44), R)
        add_box(BM['metal'], o + R @ Vector((sx, 0.30, 0.22)), (0.07, 0.07, 0.44), R)
        add_box(BM['metal'], o + R @ Vector((sx, 0.34, 0.68)), (0.07, 0.07, 0.56), R)


for pos, ang in [((-1.35, -3.0), math.radians(90)), ((1.35, -3.0), math.radians(-90)),
                 ((-1.35, 3.0), math.radians(90)), ((1.35, 3.0), math.radians(-90)),
                 ((0.0, -5.4), math.radians(180)), ((0.0, 5.4), 0.0)]:
    add_bench(pos, ang)

# planters with shrubs along the gallery edge
for i, (px, py) in enumerate([(-9.4, 4.6), (-9.4, 1.4), (9.4, -4.6), (9.4, -1.4),
                              (-3.2, -5.6), (3.2, 5.6)]):
    add_box(BM['pot'], (px, py, 0.28), (1.30, 0.85, 0.56))
    add_box(BM['soil'], (px, py, 0.55), (1.14, 0.70, 0.06))
    rnd = random.Random(70 + i)
    for k in range(3):
        r = rnd.uniform(0.26, 0.36)
        add_ico(BM['hedge'], 1.0,
                (px + rnd.uniform(-0.4, 0.4), py + rnd.uniform(-0.22, 0.22), 0.62 + r * 0.6),
                subdiv=2, scale=(r, r, r * 0.9))

# lamp standards (geometry + matching point lights)
LAMPS = [(0.0, -5.9), (0.0, 5.9), (-5.2, 0.0), (5.2, 0.0)]
for i, (lx, ly) in enumerate(LAMPS):
    add_cyl(BM['metal'], 0.22, 0.18, 0.14, (lx, ly, 0.10), segments=12)
    add_cyl(BM['metal'], 0.075, 0.055, 3.6, (lx, ly, 1.85), segments=10)
    add_ico(BM['glow'], 0.26, (lx, ly, 3.78), subdiv=2)


# ------------------------------------------------------------- build the objects
OBJECT_SPEC = [
    ('wall', "Facades", 'wall', COL_BUILD, False),
    ('trim', "Facade_Trim", 'trim', COL_BUILD, False),
    ('struct', "Structure_Slabs", 'struct', COL_BUILD, False),
    ('glass', "Windows_Glass", 'glass', COL_BUILD, False),
    ('lit', "Windows_Lit", 'lit', COL_BUILD, False),
    ('door', "Entrance_Doors", 'door', COL_BUILD, False),
    ('accent1', "Balcony_Panels_A", 'accent1', COL_BUILD, False),
    ('accent2', "Balcony_Panels_B", 'accent2', COL_BUILD, False),
    ('accent3', "Balcony_Panels_C", 'accent3', COL_BUILD, False),
    ('roofpv', "Roof_PV_Array", 'roofpv', COL_BUILD, False),
    ('gravel', "Roof_Finish", 'gravel', COL_BUILD, False),
    ('stair', "External_Stairs", 'stair', COL_ACCESS, False),
    ('metal', "Metalwork", 'metal', COL_ACCESS, False),
    ('paving', "Courtyard_Paving", 'paving', COL_GARDEN, False),
    ('kerb', "Kerbs_and_Basin", 'kerb', COL_GARDEN, False),
    ('lawn', "Lawns", 'lawn', COL_GARDEN, False),
    ('hedge', "Hedges_and_Shrubs", 'hedge', COL_GARDEN, True),
    ('trunk', "Tree_Trunks", 'trunk', COL_GARDEN, True),
    ('leaf', "Tree_Foliage", 'leaf', COL_GARDEN, True),
    ('wood', "Benches_Timber", 'wood', COL_GARDEN, False),
    ('pot', "Planters", 'pot', COL_GARDEN, False),
    ('soil', "Planter_Soil", 'soil', COL_GARDEN, False),
    ('water', "Basin_Water", 'water', COL_GARDEN, False),
    ('glow', "Lamp_Globes", 'glow', COL_GARDEN, True),
    ('walk', "Sidewalk", 'walk', COL_SITE, False),
    ('street', "Ground_Plane", 'street', COL_SITE, False),
]

created = []
for key, obj_name, mat_key, coll, smooth in OBJECT_SPEC:
    if key not in BM:
        continue
    bm = BM[key]
    bmesh.ops.remove_doubles(bm, verts=bm.verts, dist=1e-4)
    me = bpy.data.meshes.new(obj_name)
    bm.to_mesh(me)
    bm.free()
    if smooth:
        for poly in me.polygons:
            poly.use_smooth = True
    me.materials.append(MAT[mat_key])
    ob = bpy.data.objects.new(obj_name, me)
    coll.objects.link(ob)
    created.append(ob)


# -------------------------------------------------------------------- lighting
world = bpy.data.worlds.new("CourtyardWorld")
scene.world = world
world.use_nodes = True
wnt = world.node_tree
bg = wnt.nodes.get("Background")
bg.inputs["Strength"].default_value = 1.0
bg.inputs["Color"].default_value = (0.240, 0.400, 0.680, 1.0)
try:
    sky = wnt.nodes.new("ShaderNodeTexSky")
    sky.location = (-320, 0)
    sky.sun_elevation = math.radians(46.0)
    sky.sun_rotation = math.radians(-125.0)
    wnt.links.new(sky.outputs[0], bg.inputs[0])
except Exception:
    pass

sun_data = bpy.data.lights.new("Sun", 'SUN')
sun_data.energy = 4.2
sun_data.angle = math.radians(1.6)
sun_data.color = (1.0, 0.955, 0.885)
sun = bpy.data.objects.new("Sun", sun_data)
sun.rotation_euler = Vector((-0.55, -0.35, -1.05)).to_track_quat('-Z', 'Y').to_euler()
sun.location = (28.0, -30.0, 45.0)
COL_LIGHT.objects.link(sun)

fill_data = bpy.data.lights.new("Courtyard_Fill", 'AREA')
fill_data.shape = 'RECTANGLE'
fill_data.size = 22.0
fill_data.size_y = 14.0
fill_data.energy = 900.0
fill_data.color = (0.80, 0.87, 1.0)
fill = bpy.data.objects.new("Courtyard_Fill", fill_data)
fill.location = (0.0, 0.0, 20.0)
COL_LIGHT.objects.link(fill)

for i, (lx, ly) in enumerate(LAMPS):
    ld = bpy.data.lights.new("Lamp_%d" % i, 'POINT')
    ld.energy = 90.0
    ld.color = (1.0, 0.84, 0.62)
    ld.shadow_soft_size = 0.28
    lo = bpy.data.objects.new("Lamp_%d" % i, ld)
    lo.location = (lx, ly, 3.78)
    COL_LIGHT.objects.link(lo)


# ---------------------------------------------------------------------- camera
cam_data = bpy.data.cameras.new("Camera")
cam_data.lens = 32.0
cam_data.clip_start = 0.1
cam_data.clip_end = 500.0
cam = bpy.data.objects.new("Camera", cam_data)
cam_loc = Vector((40.0, -50.0, 34.0))
cam.location = cam_loc
cam.rotation_euler = (Vector((0.0, 0.0, 4.5)) - cam_loc).to_track_quat('-Z', 'Y').to_euler()
COL_LIGHT.objects.link(cam)
scene.camera = cam

total_verts = sum(len(o.data.vertices) for o in created)
total_faces = sum(len(o.data.polygons) for o in created)
print("Courtyard housing block built: %d objects, %d verts, %d faces"
      % (len(created), total_verts, total_faces))
