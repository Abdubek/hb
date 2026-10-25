"""Mountain research outpost - prefabricated modules, stilts and elevated walkways."""

import bpy
import bmesh
import math
import random
from mathutils import Vector, Matrix, Euler, noise

random.seed(20260909)

# ----------------------------------------------------------------------------- setup

def reset_scene():
    bpy.ops.wm.read_factory_settings(use_empty=True)
    scene = bpy.context.scene
    scene.unit_settings.system = 'METRIC'
    try:
        scene.render.engine = 'CYCLES'
        scene.cycles.samples = 128
    except Exception:
        pass


def get_coll(name):
    coll = bpy.data.collections.get(name)
    if coll is None:
        coll = bpy.data.collections.new(name)
        bpy.context.scene.collection.children.link(coll)
    return coll


def set_input(bsdf, name, value):
    if name in bsdf.inputs:
        bsdf.inputs[name].default_value = value


def make_material(name, base, rough=0.6, metal=0.0, emit=None, emit_str=0.0,
                  alpha=1.0, transmission=0.0, ior=1.45, coat=0.0):
    mat = bpy.data.materials.new(name)
    mat.use_nodes = True
    bsdf = mat.node_tree.nodes.get("Principled BSDF")
    set_input(bsdf, "Base Color", (*base, 1.0))
    set_input(bsdf, "Roughness", rough)
    set_input(bsdf, "Metallic", metal)
    set_input(bsdf, "IOR", ior)
    set_input(bsdf, "Alpha", alpha)
    set_input(bsdf, "Transmission Weight", transmission)
    set_input(bsdf, "Coat Weight", coat)
    if emit is not None:
        set_input(bsdf, "Emission Color", (*emit, 1.0))
        set_input(bsdf, "Emission Strength", emit_str)
    if alpha < 1.0 or transmission > 0.0:
        mat.blend_method = 'BLEND'
    return mat


# ------------------------------------------------------------------- bmesh utilities

def _tag_new(bm, start, mi, smooth=False):
    bm.faces.ensure_lookup_table()
    for f in bm.faces[start:]:
        f.material_index = mi
        f.smooth = smooth


def bm_box(bm, size, loc=(0.0, 0.0, 0.0), rot=(0.0, 0.0, 0.0), mi=0, mtx=None):
    base = mtx if mtx is not None else (Matrix.Translation(loc) @ Euler(rot, 'XYZ').to_matrix().to_4x4())
    m = base @ Matrix.Diagonal(Vector((size[0], size[1], size[2], 1.0)))
    n = len(bm.faces)
    bmesh.ops.create_cube(bm, size=1.0, matrix=m, calc_uvs=True)
    _tag_new(bm, n, mi, False)


def bm_cyl(bm, r1, r2, depth, mtx, seg=20, mi=0, smooth=True, caps=True):
    n = len(bm.faces)
    bmesh.ops.create_cone(bm, cap_ends=caps, cap_tris=False, segments=seg,
                          radius1=r1, radius2=r2, depth=depth, matrix=mtx, calc_uvs=True)
    _tag_new(bm, n, mi, smooth)


def bm_rod(bm, p0, p1, r, mi=0, seg=8, smooth=True):
    p0, p1 = Vector(p0), Vector(p1)
    d = p1 - p0
    length = d.length
    if length < 1e-5:
        return
    rot = Vector((0.0, 0.0, 1.0)).rotation_difference(d.normalized()).to_matrix().to_4x4()
    mtx = Matrix.Translation((p0 + p1) * 0.5) @ rot
    bm_cyl(bm, r, r, length, mtx, seg=seg, mi=mi, smooth=smooth)


def bm_sphere(bm, r, loc, mi=0, u=20, v=12, scale=(1.0, 1.0, 1.0), rot_z=0.0):
    mtx = (Matrix.Translation(loc) @ Matrix.Rotation(rot_z, 4, 'Z')
           @ Matrix.Diagonal(Vector((scale[0], scale[1], scale[2], 1.0))))
    n = len(bm.faces)
    bmesh.ops.create_uvsphere(bm, u_segments=u, v_segments=v, radius=r, matrix=mtx, calc_uvs=True)
    _tag_new(bm, n, mi, True)


def bm_ico(bm, r, loc, mi=0, subdiv=2, scale=(1.0, 1.0, 1.0), rot_z=0.0, smooth=True):
    mtx = (Matrix.Translation(loc) @ Matrix.Rotation(rot_z, 4, 'Z')
           @ Matrix.Diagonal(Vector((scale[0], scale[1], scale[2], 1.0))))
    n = len(bm.faces)
    bmesh.ops.create_icosphere(bm, subdivisions=subdiv, radius=r, matrix=mtx, calc_uvs=True)
    _tag_new(bm, n, mi, smooth)


def obj_from_bm(name, bm, mats, coll="Outpost", matrix=None):
    me = bpy.data.meshes.new(name)
    bm.normal_update()
    bm.to_mesh(me)
    bm.free()
    for m in mats:
        me.materials.append(m)
    ob = bpy.data.objects.new(name, me)
    if matrix is not None:
        ob.matrix_world = matrix
    get_coll(coll).objects.link(ob)
    return ob


# --------------------------------------------------------------------------- terrain

def smoothstep(a, b, x):
    if b - a == 0.0:
        return 0.0
    t = min(1.0, max(0.0, (x - a) / (b - a)))
    return t * t * (3.0 - 2.0 * t)


def terrain_h(x, y):
    """Analytic alpine height field with a flat shelf around the outpost."""
    p = Vector((x * 0.021, y * 0.021, 0.0))
    h = noise.fractal(p, 1.0, 2.0, 5) * 13.0
    h += math.sin(x * 0.034) * math.cos(y * 0.027) * 4.2
    h += noise.noise(Vector((x * 0.17, y * 0.17, 3.0))) * 0.55
    r = math.hypot(x, y + 1.0)
    h += max(0.0, r - 42.0) * 0.62          # ridges rising away from the shelf
    shelf = 0.35 * noise.noise(Vector((x * 0.09, y * 0.09, 7.0))) + 0.018 * x - 0.012 * y
    t = smoothstep(19.0, 41.0, r)
    return shelf * (1.0 - t) + h * t


def build_terrain(mat_snow, mat_rock, size=210.0, n=180):
    bm = bmesh.new()
    step = size / n
    half = size * 0.5
    grid = []
    for j in range(n + 1):
        row = []
        y = -half + j * step
        for i in range(n + 1):
            x = -half + i * step
            row.append(bm.verts.new((x, y, terrain_h(x, y))))
        grid.append(row)
    bm.verts.ensure_lookup_table()
    for j in range(n):
        for i in range(n):
            bm.faces.new((grid[j][i], grid[j][i + 1], grid[j + 1][i + 1], grid[j + 1][i]))
    bm.normal_update()
    for f in bm.faces:
        f.smooth = True
        f.material_index = 0 if f.normal.z > 0.74 else 1   # snow on flats, rock on cliffs
    return obj_from_bm("Terrain", bm, [mat_snow, mat_rock], coll="Terrain")


# -------------------------------------------------------------------------- material

reset_scene()

M_SNOW = make_material("Snow", (0.90, 0.93, 0.97), rough=0.42)
M_ROCK = make_material("Rock", (0.16, 0.15, 0.145), rough=0.88)
M_SHELL_A = make_material("Shell_Orange", (0.62, 0.20, 0.05), rough=0.42, coat=0.25)
M_SHELL_B = make_material("Shell_Cream", (0.70, 0.68, 0.62), rough=0.45, coat=0.2)
M_SHELL_C = make_material("Shell_Blue", (0.09, 0.20, 0.33), rough=0.45, coat=0.2)
M_ACCENT = make_material("Accent_White", (0.78, 0.79, 0.80), rough=0.5)
M_METAL = make_material("Galv_Steel", (0.56, 0.57, 0.59), rough=0.36, metal=1.0)
M_DARK = make_material("Dark_Rubber", (0.035, 0.035, 0.04), rough=0.75)
M_GRATE = make_material("Deck_Grating", (0.28, 0.29, 0.30), rough=0.62, metal=0.85)
M_GLASS = make_material("Window_Lit", (0.05, 0.05, 0.06), rough=0.12,
                        emit=(1.0, 0.72, 0.38), emit_str=3.0)
M_SOLAR = make_material("Solar_Cell", (0.015, 0.02, 0.05), rough=0.14, metal=0.35)
M_TANK = make_material("Fuel_Tank", (0.42, 0.44, 0.42), rough=0.5, metal=0.7)

build_terrain(M_SNOW, M_ROCK)

# --------------------------------------------------------------------------- modules

MODULES = [
    dict(name="Hub",     x=0.0,   y=0.0,   rot=math.radians(0.0),  L=9.0,  W=4.4, H=3.0,
         shell=M_SHELL_A, windows=3, roofkit=True),
    dict(name="Lab",     x=-13.0, y=6.5,   rot=math.radians(16.0), L=7.2,  W=3.8, H=2.9,
         shell=M_SHELL_B, windows=2, roofkit=False),
    dict(name="Dorm",    x=12.5,  y=-3.5,  rot=math.radians(-18.0), L=8.0, W=3.8, H=2.9,
         shell=M_SHELL_C, windows=3, roofkit=False),
    dict(name="Power",   x=2.5,   y=-13.0, rot=math.radians(90.0), L=6.4,  W=3.6, H=2.8,
         shell=M_SHELL_B, windows=1, roofkit=True),
    dict(name="Storage", x=-10.0, y=-9.0,  rot=math.radians(28.0), L=6.0,  W=3.4, H=2.7,
         shell=M_SHELL_A, windows=0, roofkit=False),
]

GROUNDS = [terrain_h(m['x'], m['y']) for m in MODULES]
DECK_Z = max(GROUNDS) + 2.7          # single shared floor level for the whole outpost


def port(m, lx, ly):
    """World XY of a local point on a module footprint."""
    v = Matrix.Rotation(m['rot'], 3, 'Z') @ Vector((lx, ly, 0.0))
    return (m['x'] + v.x, m['y'] + v.y)


def build_module(m):
    """Body object (bevelled) + detail object, both in module-local space."""
    L, W, H = m['L'], m['W'], m['H']
    origin = Matrix.Translation((m['x'], m['y'], DECK_Z)) @ Matrix.Rotation(m['rot'], 4, 'Z')

    body = bmesh.new()
    bm_box(body, (L, W, H), loc=(0.0, 0.0, H * 0.5), mi=0)
    ob_body = obj_from_bm(m['name'] + "_Shell", body, [m['shell']], matrix=origin)
    bev = ob_body.modifiers.new("Bevel", 'BEVEL')
    bev.width = 0.09
    bev.segments = 3
    bev.limit_method = 'ANGLE'
    bev.angle_limit = math.radians(45.0)

    # detail slots: 0 accent, 1 glass, 2 metal, 3 dark, 4 snow, 5 shell
    d = bmesh.new()

    # under-floor chassis: skids and cross beams
    for sy in (-1, 1):
        bm_box(d, (L, 0.24, 0.34), loc=(0.0, sy * (W * 0.5 - 0.28), -0.20), mi=2)
    for i in range(5):
        x = -L * 0.5 + 0.5 + i * (L - 1.0) / 4.0
        bm_box(d, (0.18, W - 0.3, 0.24), loc=(x, 0.0, -0.14), mi=2)

    # corrugation ribs on the long walls
    ribs = max(4, int(L / 0.95))
    for i in range(ribs):
        x = -L * 0.5 + (i + 0.5) * (L / ribs)
        bm_box(d, (0.085, W + 0.075, H - 0.34), loc=(x, 0.0, H * 0.5), mi=0)

    # roof pan, drip lip and settled snow
    bm_box(d, (L + 0.24, W + 0.24, 0.12), loc=(0.0, 0.0, H + 0.06), mi=0)
    for sy in (-1, 1):
        bm_box(d, (L + 0.24, 0.10, 0.16), loc=(0.0, sy * (W * 0.5 + 0.07), H + 0.16), mi=2)
    bm_box(d, (L + 0.10, W + 0.10, 0.10), loc=(0.0, 0.0, H + 0.19), mi=4)

    # ISO-style corner castings
    for sx in (-1, 1):
        for sy in (-1, 1):
            for z in (0.14, H - 0.14):
                bm_box(d, (0.36, 0.36, 0.28),
                       loc=(sx * (L * 0.5 - 0.18), sy * (W * 0.5 - 0.18), z), mi=3)

    # lit windows both long sides
    if m['windows']:
        span = L - 2.2
        for i in range(m['windows']):
            x = -span * 0.5 + (span * i / max(1, m['windows'] - 1)) if m['windows'] > 1 else 0.0
            for sy in (-1, 1):
                yw = sy * (W * 0.5)
                bm_box(d, (1.42, 0.12, 1.02), loc=(x, yw, H * 0.60), mi=0)
                bm_box(d, (1.20, 0.07, 0.80), loc=(x, yw + sy * 0.045, H * 0.60), mi=1)
                bm_box(d, (0.06, 0.09, 0.80), loc=(x, yw + sy * 0.05, H * 0.60), mi=2)

    # door on the -X end with a small porch
    bm_box(d, (0.14, 1.12, 2.20), loc=(-L * 0.5 - 0.02, 0.0, 1.12), mi=0)
    bm_box(d, (0.08, 0.92, 2.00), loc=(-L * 0.5 - 0.09, 0.0, 1.10), mi=2)
    bm_box(d, (0.10, 0.16, 0.05), loc=(-L * 0.5 - 0.14, 0.30, 1.05), mi=3)
    bm_box(d, (0.9, 1.5, 0.10), loc=(-L * 0.5 - 0.45, 0.0, -0.06), mi=2)
    bm_box(d, (0.9, 0.14, 0.55), loc=(-L * 0.5 - 0.55, 0.0, 2.55), mi=0)   # door canopy

    # roof furniture
    bm_cyl(d, 0.16, 0.16, 0.7, Matrix.Translation((L * 0.28, 0.9, H + 0.55)), seg=16, mi=2)
    bm_cyl(d, 0.20, 0.20, 0.14, Matrix.Translation((L * 0.28, 0.9, H + 0.94)), seg=16, mi=2)
    bm_box(d, (0.9, 0.7, 0.45), loc=(-L * 0.25, -0.7, H + 0.34), mi=0)     # HVAC box
    bm_cyl(d, 0.24, 0.24, 0.10, Matrix.Translation((-L * 0.25, -0.7, H + 0.60)), seg=16, mi=3)

    if m['roofkit']:
        # whip antenna + small dish on the hub / power module roofs
        bm_cyl(d, 0.045, 0.02, 2.6, Matrix.Translation((L * 0.42, -1.2, H + 1.45)), seg=10, mi=2)
        bm_sphere(d, 0.07, (L * 0.42, -1.2, H + 2.75), mi=3, u=10, v=6)
        bm_cyl(d, 0.07, 0.07, 0.9, Matrix.Translation((-L * 0.40, 1.1, H + 0.62)), seg=10, mi=2)
        n0 = len(d.faces)
        bmesh.ops.create_uvsphere(
            d, u_segments=20, v_segments=10, radius=0.55,
            matrix=(Matrix.Translation((-L * 0.40, 1.1, H + 1.30))
                    @ Matrix.Rotation(math.radians(-42.0), 4, 'X')
                    @ Matrix.Diagonal(Vector((1.0, 1.0, 0.45, 1.0)))), calc_uvs=True)
        d.faces.ensure_lookup_table()
        for f in d.faces[n0:]:
            f.material_index = 0
            f.smooth = True

    obj_from_bm(m['name'] + "_Details", d,
                [M_ACCENT, M_GLASS, M_METAL, M_DARK, M_SNOW, m['shell']], matrix=origin)


for mod in MODULES:
    build_module(mod)


# ------------------------------------------------- structures: legs, walkways, stairs
# slots: 0 grating, 1 metal, 2 accent, 3 dark, 4 snow
S = bmesh.new()
GRATE, MET, ACC, DRK, SNW = 0, 1, 2, 3, 4


def add_leg(wx, wy, top_z, r=0.11, pad=0.72):
    gz = terrain_h(wx, wy)
    bm_rod(S, (wx, wy, gz - 0.35), (wx, wy, top_z), r, mi=MET, seg=12)
    bm_box(S, (pad, pad, 0.20), loc=(wx, wy, gz - 0.02), mi=DRK)
    return gz


def module_legs(m):
    L, W = m['L'], m['W']
    rot = Matrix.Rotation(m['rot'], 3, 'Z')
    xs = (-L * 0.5 + 0.65, 0.0, L * 0.5 - 0.65)
    tops = []
    for lx in xs:
        pair = []
        for sy in (-1, 1):
            v = rot @ Vector((lx, sy * (W * 0.5 - 0.32), 0.0))
            wx, wy = m['x'] + v.x, m['y'] + v.y
            gz = add_leg(wx, wy, DECK_Z - 0.30)
            pair.append((wx, wy, gz))
        tops.append(pair)
        # X-brace across the pair
        (ax, ay, agz), (bx, by, bgz) = pair
        bm_rod(S, (ax, ay, agz + 0.25), (bx, by, DECK_Z - 0.55), 0.045, mi=MET, seg=6)
        bm_rod(S, (bx, by, bgz + 0.25), (ax, ay, DECK_Z - 0.55), 0.045, mi=MET, seg=6)
    # longitudinal braces
    for a, b in zip(tops, tops[1:]):
        for i in (0, 1):
            bm_rod(S, (a[i][0], a[i][1], a[i][2] + 0.4), (b[i][0], b[i][1], DECK_Z - 0.6),
                   0.045, mi=MET, seg=6)


for mod in MODULES:
    module_legs(mod)


def walkway(p0, p1, width=1.65, deck_z=None, railings=True):
    deck_z = DECK_Z if deck_z is None else deck_z
    p0, p1 = Vector(p0), Vector(p1)
    d = p1 - p0
    length = d.length
    if length < 0.2:
        return
    ang = math.atan2(d.y, d.x)
    mid = (p0 + p1) * 0.5
    rz = Matrix.Rotation(ang, 4, 'Z')
    base = Matrix.Translation((mid.x, mid.y, 0.0)) @ rz

    # deck plate + snow skin + side stringers
    bm_box(S, (length, width, 0.10), mtx=base @ Matrix.Translation((0, 0, deck_z - 0.05)), mi=GRATE)
    bm_box(S, (length, width * 0.82, 0.05), mtx=base @ Matrix.Translation((0, 0, deck_z + 0.02)), mi=SNW)
    for sy in (-1, 1):
        bm_box(S, (length, 0.12, 0.34),
               mtx=base @ Matrix.Translation((0, sy * width * 0.5, deck_z - 0.24)), mi=MET)

    ux, uy = math.cos(ang), math.sin(ang)
    nx, ny = -uy, ux

    if railings:
        posts = max(2, int(length / 1.45))
        for i in range(posts + 1):
            t = -length * 0.5 + i * (length / posts)
            for sy in (-1, 1):
                px = mid.x + ux * t + nx * sy * width * 0.5
                py = mid.y + uy * t + ny * sy * width * 0.5
                bm_rod(S, (px, py, deck_z - 0.15), (px, py, deck_z + 1.02), 0.045, mi=ACC, seg=8)
        for sy in (-1, 1):
            for h in (0.52, 1.00):
                a = (p0.x + nx * sy * width * 0.5, p0.y + ny * sy * width * 0.5, deck_z + h)
                b = (p1.x + nx * sy * width * 0.5, p1.y + ny * sy * width * 0.5, deck_z + h)
                bm_rod(S, a, b, 0.038, mi=ACC, seg=8)

    # trestles every few metres
    bays = max(1, int(length / 4.2))
    for i in range(1, bays):
        t = -length * 0.5 + i * (length / bays)
        cx, cy = mid.x + ux * t, mid.y + uy * t
        for sy in (-1, 1):
            lx, ly = cx + nx * sy * (width * 0.42), cy + ny * sy * (width * 0.42)
            add_leg(lx, ly, deck_z - 0.34, r=0.085, pad=0.55)
        ax, ay = cx + nx * width * 0.42, cy + ny * width * 0.42
        bx, by = cx - nx * width * 0.42, cy - ny * width * 0.42
        bm_rod(S, (ax, ay, terrain_h(ax, ay) + 0.3), (bx, by, deck_z - 0.55), 0.04, mi=MET, seg=6)
        bm_rod(S, (bx, by, terrain_h(bx, by) + 0.3), (ax, ay, deck_z - 0.55), 0.04, mi=MET, seg=6)


hub, lab, dorm, power, store = MODULES
walkway(port(hub, -hub['L'] * 0.5 - 0.1, 0.0), port(lab, lab['L'] * 0.5 + 0.1, 0.0))
walkway(port(hub, hub['L'] * 0.5 + 0.1, 0.0), port(dorm, -dorm['L'] * 0.5 - 0.1, 0.0))
walkway(port(hub, 2.6, -hub['W'] * 0.5 - 0.1), port(power, power['L'] * 0.5 + 0.1, 0.0), width=1.45)
walkway(port(hub, -2.8, -hub['W'] * 0.5 - 0.1), port(store, store['L'] * 0.5 + 0.1, 0.0), width=1.45)


def stairs(top_xy, ang, top_z=None, tread_w=1.15):
    top_z = DECK_Z if top_z is None else top_z
    ux, uy = math.cos(ang), math.sin(ang)
    nx, ny = -uy, ux
    bottom = (top_xy[0] + ux * 3.6, top_xy[1] + uy * 3.6)
    gz = terrain_h(*bottom)
    steps = max(4, int((top_z - gz) / 0.21))
    rise = (top_z - gz) / steps
    run = 3.6 / steps
    for i in range(steps):
        t = (i + 0.5) * run
        cx, cy = top_xy[0] + ux * t, top_xy[1] + uy * t
        cz = top_z - rise * (i + 0.5)
        bm_box(S, (run + 0.04, tread_w, 0.05),
               mtx=(Matrix.Translation((cx, cy, cz)) @ Matrix.Rotation(ang, 4, 'Z')), mi=GRATE)
    for sy in (-1, 1):
        a = (top_xy[0] + nx * sy * tread_w * 0.5, top_xy[1] + ny * sy * tread_w * 0.5, top_z - 0.12)
        b = (bottom[0] + nx * sy * tread_w * 0.5, bottom[1] + ny * sy * tread_w * 0.5, gz - 0.05)
        bm_rod(S, a, b, 0.07, mi=MET, seg=8)
        for f in (0.0, 0.34, 0.67, 1.0):
            px = a[0] + (b[0] - a[0]) * f
            py = a[1] + (b[1] - a[1]) * f
            pz = a[2] + (b[2] - a[2]) * f
            bm_rod(S, (px, py, pz), (px, py, pz + 1.05), 0.04, mi=ACC, seg=8)
        bm_rod(S, (a[0], a[1], a[2] + 1.05), (b[0], b[1], b[2] + 1.05), 0.035, mi=ACC, seg=8)
    # landing at the top of the flight
    bm_box(S, (1.4, tread_w + 0.5, 0.10),
           mtx=(Matrix.Translation((top_xy[0] - ux * 0.6, top_xy[1] - uy * 0.6, top_z - 0.05))
                @ Matrix.Rotation(ang, 4, 'Z')), mi=GRATE)


stairs(port(hub, 0.0, hub['W'] * 0.5 + 0.9), math.radians(90.0))

# ------------------------------------------------------------ mast, solar, hardware

MAST_X, MAST_Y = -4.5, 9.5
mast_g = terrain_h(MAST_X, MAST_Y)
MAST_TOP = mast_g + 11.5
bm_box(S, (1.5, 1.5, 0.32), loc=(MAST_X, MAST_Y, mast_g + 0.05), mi=DRK)
bm_cyl(S, 0.20, 0.11, MAST_TOP - mast_g,
       Matrix.Translation((MAST_X, MAST_Y, (mast_g + MAST_TOP) * 0.5)), seg=14, mi=ACC)
for i in range(5):
    z = mast_g + 1.6 + i * 2.0
    r = 0.19 - i * 0.016
    bm_cyl(S, r + 0.07, r + 0.07, 0.10, Matrix.Translation((MAST_X, MAST_Y, z)), seg=14, mi=MET)
for k in range(3):
    a = math.radians(20.0 + k * 120.0)
    ax, ay = MAST_X + math.cos(a) * 7.5, MAST_Y + math.sin(a) * 7.5
    az = terrain_h(ax, ay)
    bm_rod(S, (ax, ay, az + 0.1), (MAST_X, MAST_Y, MAST_TOP - 1.2), 0.032, mi=DRK, seg=6)
    bm_box(S, (0.55, 0.55, 0.4), loc=(ax, ay, az), mi=MET)
for k in range(3):                                   # cross-arm antennas
    a = math.radians(k * 120.0)
    ex, ey = MAST_X + math.cos(a) * 1.25, MAST_Y + math.sin(a) * 1.25
    bm_rod(S, (MAST_X, MAST_Y, MAST_TOP - 2.2), (ex, ey, MAST_TOP - 2.2), 0.045, mi=MET, seg=6)
    bm_rod(S, (ex, ey, MAST_TOP - 2.9), (ex, ey, MAST_TOP - 1.4), 0.035, mi=MET, seg=6)
bm_cyl(S, 0.09, 0.09, 1.4, Matrix.Translation((MAST_X, MAST_Y, MAST_TOP + 0.7)), seg=10, mi=MET)
bm_sphere(S, 0.13, (MAST_X, MAST_Y, MAST_TOP + 1.45), mi=DRK, u=12, v=8)
# anemometer cups
for k in range(3):
    a = math.radians(k * 120.0)
    bm_sphere(S, 0.11, (MAST_X + math.cos(a) * 0.42, MAST_Y + math.sin(a) * 0.42, MAST_TOP + 1.05),
              mi=ACC, u=10, v=6, scale=(1.0, 1.0, 0.8))

# large parabolic dish on its own pedestal
DX, DY = 6.5, 10.5
dg = terrain_h(DX, DY)
bm_box(S, (1.8, 1.8, 0.3), loc=(DX, DY, dg + 0.05), mi=DRK)
bm_cyl(S, 0.22, 0.22, 2.4, Matrix.Translation((DX, DY, dg + 1.25)), seg=16, mi=ACC)
for sx in (-1, 1):
    bm_rod(S, (DX + sx * 0.55, DY, dg + 2.3), (DX + sx * 0.55, DY, dg + 3.4), 0.09, mi=ACC, seg=8)

dish = bmesh.new()
bmesh.ops.create_uvsphere(dish, u_segments=32, v_segments=16, radius=1.9,
                          matrix=Matrix.Identity(4), calc_uvs=True)
bmesh.ops.delete(dish, geom=[v for v in dish.verts if v.co.z > -0.85], context='VERTS')
for v in dish.verts:
    v.co.z = (v.co.z + 1.9) * 0.55 - 0.15
for f in dish.faces:
    f.smooth = True
    f.material_index = 0
bm_cyl(dish, 0.055, 0.055, 1.5, Matrix.Translation((0.0, 0.0, 0.85)), seg=10, mi=1)
bm_box(dish, (0.26, 0.26, 0.3), loc=(0.0, 0.0, 1.6), mi=2)
dish_mtx = (Matrix.Translation((DX, DY, dg + 3.6))
            @ Matrix.Rotation(math.radians(-38.0), 4, 'X')
            @ Matrix.Rotation(math.radians(25.0), 4, 'Z'))
obj_from_bm("Comms_Dish", dish, [M_ACCENT, M_METAL, M_DARK], matrix=dish_mtx)

# solar array field
sol = bmesh.new()
for row in range(2):
    for col in range(3):
        px = 9.0 + col * 3.1
        py = 5.0 - row * 4.0
        gz = terrain_h(px, py)
        tilt = Matrix.Rotation(math.radians(40.0), 4, 'X')
        frame = Matrix.Translation((px, py, gz + 1.25)) @ Matrix.Rotation(math.radians(-8.0), 4, 'Z')
        bm_box(sol, (2.9, 0.06, 1.9), mtx=frame @ tilt, mi=1)
        bm_box(sol, (3.0, 0.10, 2.0), mtx=frame @ tilt @ Matrix.Translation((0, 0.06, 0)), mi=2)
        for sx in (-1, 1):
            fx = px + sx * 1.25
            bm_rod(sol, (fx, py + 0.75, gz - 0.1), (fx, py + 0.55, gz + 0.75), 0.06, mi=2, seg=8)
            bm_rod(sol, (fx, py - 0.75, gz - 0.1), (fx, py - 0.45, gz + 1.85), 0.06, mi=2, seg=8)
            bm_box(sol, (0.45, 0.45, 0.16), loc=(fx, py + 0.75, gz), mi=0)
            bm_box(sol, (0.45, 0.45, 0.16), loc=(fx, py - 0.75, gz), mi=0)
obj_from_bm("Solar_Array", sol, [M_DARK, M_SOLAR, M_METAL])

# fuel tanks, crates and drums beside the power module
gear = bmesh.new()
for i in range(2):
    tx, ty = 6.2, -14.5 - i * 2.6
    gz = terrain_h(tx, ty)
    mtx = (Matrix.Translation((tx, ty, gz + 1.1)) @ Matrix.Rotation(math.radians(12.0), 4, 'Z')
           @ Matrix.Rotation(math.radians(90.0), 4, 'Y'))
    bm_cyl(gear, 0.95, 0.95, 3.6, mtx, seg=28, mi=0)
    for sx in (-1, 1):
        cx = tx + sx * 1.2 * math.cos(math.radians(12.0))
        cy = ty + sx * 1.2 * math.sin(math.radians(12.0))
        bm_box(gear, (0.9, 2.1, 0.7), loc=(cx, cy, gz + 0.35), rot=(0, 0, math.radians(12.0)), mi=2)
for i in range(7):
    a = random.uniform(0.0, math.tau)
    r = random.uniform(2.0, 4.5)
    cx, cy = -13.5 + math.cos(a) * r, -12.0 + math.sin(a) * r
    gz = terrain_h(cx, cy)
    if random.random() < 0.5:
        s = random.uniform(0.7, 1.15)
        rz = random.uniform(0, math.tau)
        bm_box(gear, (1.3 * s, 0.95 * s, 0.85 * s), loc=(cx, cy, gz + 0.42 * s), rot=(0, 0, rz), mi=1)
        bm_box(gear, (1.32 * s, 0.97 * s, 0.06), loc=(cx, cy, gz + 0.86 * s), rot=(0, 0, rz), mi=3)
    else:
        bm_cyl(gear, 0.32, 0.32, 0.9, Matrix.Translation((cx, cy, gz + 0.45)), seg=16, mi=2)
        for zz in (0.25, 0.65):
            bm_cyl(gear, 0.35, 0.35, 0.07, Matrix.Translation((cx, cy, gz + zz)), seg=16, mi=2)
obj_from_bm("Site_Gear", gear, [M_TANK, M_SHELL_B, M_SHELL_A, M_SNOW])

# marker poles along the route down the slope
poles = bmesh.new()
for i in range(14):
    t = i / 13.0
    px = -6.0 + t * 26.0 + math.sin(t * 5.0) * 2.2
    py = 14.0 + t * 16.0 + math.cos(t * 4.0) * 1.8
    gz = terrain_h(px, py)
    bm_rod(poles, (px, py, gz - 0.2), (px, py, gz + 2.0), 0.045, mi=0, seg=6)
    bm_box(poles, (0.09, 0.30, 0.30), loc=(px, py, gz + 1.85), mi=1)
obj_from_bm("Route_Markers", poles, [M_ACCENT, M_SHELL_A])

obj_from_bm("Outpost_Structure", S, [M_GRATE, M_METAL, M_ACCENT, M_DARK, M_SNOW])

# ------------------------------------------------------------------- rocks and snow
rocks = bmesh.new()
for _ in range(90):
    a = random.uniform(0.0, math.tau)
    r = random.uniform(16.0, 62.0)
    px, py = math.cos(a) * r, math.sin(a) * r
    gz = terrain_h(px, py)
    rad = random.uniform(0.5, 2.4)
    v0 = len(rocks.verts)
    bm_ico(rocks, rad, (px, py, gz - rad * 0.35), mi=0, subdiv=1,
           scale=(1.0, random.uniform(0.7, 1.1), random.uniform(0.5, 0.8)),
           rot_z=random.uniform(0, math.tau), smooth=False)
    rocks.verts.ensure_lookup_table()
    for v in rocks.verts[v0:]:
        v.co += Vector((random.uniform(-1, 1), random.uniform(-1, 1),
                        random.uniform(-1, 1))) * rad * 0.18
obj_from_bm("Rocks", rocks, [M_ROCK], coll="Terrain")

drifts = bmesh.new()
for _ in range(70):
    a = random.uniform(0.0, math.tau)
    r = random.uniform(4.0, 34.0)
    px, py = math.cos(a) * r, math.sin(a) * r
    gz = terrain_h(px, py)
    rad = random.uniform(1.0, 3.4)
    bm_ico(drifts, rad, (px, py, gz - rad * 0.62), mi=0, subdiv=2,
           scale=(1.0, random.uniform(0.5, 0.8), random.uniform(0.22, 0.38)),
           rot_z=random.uniform(0, math.tau))
obj_from_bm("Snow_Drifts", drifts, [M_SNOW], coll="Terrain")

# ---------------------------------------------------------------- world and lighting
world = bpy.data.worlds.new("Alpine_Sky")
bpy.context.scene.world = world
world.use_nodes = True
nt = world.node_tree
bg = nt.nodes.get("Background")
bg.inputs["Strength"].default_value = 1.1
try:
    sky = nt.nodes.new("ShaderNodeTexSky")
    sky.sky_type = 'NISHITA'
    sky.sun_elevation = math.radians(14.0)
    sky.sun_rotation = math.radians(200.0)
    sky.altitude = 2800.0
    sky.air_density = 0.6
    sky.dust_density = 0.3
    sky.location = (-320.0, 120.0)
    nt.links.new(sky.outputs["Color"], bg.inputs["Color"])
except Exception:
    bg.inputs["Color"].default_value = (0.35, 0.48, 0.68, 1.0)

sun_data = bpy.data.lights.new("Sun", 'SUN')
sun_data.energy = 4.5
sun_data.angle = math.radians(1.5)
sun_data.color = (1.0, 0.90, 0.78)
sun = bpy.data.objects.new("Sun", sun_data)
sun.rotation_euler = Euler((math.radians(62.0), 0.0, math.radians(38.0)), 'XYZ')
get_coll("Lighting").objects.link(sun)

fill_data = bpy.data.lights.new("SkyFill", 'AREA')
fill_data.energy = 900.0
fill_data.shape = 'RECTANGLE'
fill_data.size = 40.0
fill_data.size_y = 30.0
fill_data.color = (0.62, 0.74, 1.0)
fill = bpy.data.objects.new("SkyFill", fill_data)
fill.location = (-24.0, 26.0, 26.0)
fill.rotation_euler = (Vector((0.0, -2.0, 3.0)) - Vector(fill.location)).to_track_quat('-Z', 'Y').to_euler()
get_coll("Lighting").objects.link(fill)

for m in (hub, dorm):
    px, py = port(m, -m['L'] * 0.5 - 0.7, 0.0)
    ld = bpy.data.lights.new(m['name'] + "_Porch", 'POINT')
    ld.energy = 90.0
    ld.color = (1.0, 0.74, 0.44)
    ld.shadow_soft_size = 0.18
    lo = bpy.data.objects.new(m['name'] + "_Porch", ld)
    lo.location = (px, py, DECK_Z + 2.35)
    get_coll("Lighting").objects.link(lo)

# ---------------------------------------------------------------------------- camera
cam_data = bpy.data.cameras.new("Camera")
cam_data.lens = 42.0
cam_data.clip_end = 800.0
cam = bpy.data.objects.new("Camera", cam_data)
cam.location = (34.0, -33.0, DECK_Z + 14.0)
target = Vector((-1.0, -1.5, DECK_Z + 1.5))
cam.rotation_euler = (target - Vector(cam.location)).to_track_quat('-Z', 'Y').to_euler()
get_coll("Lighting").objects.link(cam)
bpy.context.scene.camera = cam
