"""claude-149 - Coastal lookout pavilion with angular roof, viewing deck and wind screens.

Noise-displaced cliff terrain above a sea plane, a hexagonal timber deck on stilts
with a cantilevered prow, six steel columns carrying a folded two-plane roof,
tilted glass wind screens with frames, cable railings, bench, telescope and stair.
"""

import bpy
import bmesh
import math
from mathutils import Vector, Matrix, Euler, noise


# ----------------------------------------------------------------------------
# helpers
# ----------------------------------------------------------------------------
def reset_scene():
    bpy.ops.wm.read_factory_settings(use_empty=True)
    scn = bpy.context.scene
    try:
        scn.render.engine = 'BLENDER_EEVEE_NEXT'
    except Exception:
        pass
    world = bpy.data.worlds.new("World")
    scn.world = world
    world.use_nodes = True
    bg = world.node_tree.nodes["Background"]
    bg.inputs[0].default_value = (0.44, 0.58, 0.76, 1.0)
    bg.inputs[1].default_value = 1.6
    return scn


def link(obj):
    bpy.context.scene.collection.objects.link(obj)
    return obj


def new_mat(name, color, rough=0.6, metal=0.0, alpha=1.0, transmission=0.0):
    mat = bpy.data.materials.new(name)
    mat.use_nodes = True
    bsdf = mat.node_tree.nodes["Principled BSDF"]

    def s(key, value):
        if key in bsdf.inputs:
            bsdf.inputs[key].default_value = value

    s("Base Color", (color[0], color[1], color[2], 1.0))
    s("Roughness", rough)
    s("Metallic", metal)
    s("Alpha", alpha)
    s("Transmission Weight", transmission)
    s("IOR", 1.45)
    if alpha < 1.0:
        try:
            mat.blend_method = 'BLEND'
        except Exception:
            pass
    return mat


def obj_from_bm(name, bm, mat=None, smooth=False):
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    me = bpy.data.meshes.new(name)
    bm.to_mesh(me)
    bm.free()
    if smooth:
        for poly in me.polygons:
            poly.use_smooth = True
    ob = bpy.data.objects.new(name, me)
    if mat is not None:
        ob.data.materials.append(mat)
    return link(ob)


def box_bm(bm, center, size, rot=(0.0, 0.0, 0.0)):
    m = Matrix.Translation(Vector(center))
    m = m @ Euler(rot, 'XYZ').to_matrix().to_4x4()
    m = m @ Matrix.Diagonal(Vector((size[0], size[1], size[2], 1.0)))
    bmesh.ops.create_cube(bm, size=1.0, matrix=m)


def tube_bm(bm, p1, p2, radius, segments=8):
    p1 = Vector(p1)
    p2 = Vector(p2)
    d = p2 - p1
    length = d.length
    if length < 1e-6:
        return
    quat = d.to_track_quat('Z', 'Y')
    m = Matrix.Translation(p1 + d * 0.5) @ quat.to_matrix().to_4x4()
    bmesh.ops.create_cone(bm, cap_ends=True, cap_tris=False, segments=segments,
                          radius1=radius, radius2=radius, depth=length, matrix=m)


def prism_bm(bm, pts, z, height):
    verts = [bm.verts.new((p[0], p[1], z)) for p in pts]
    face = bm.faces.new(verts)
    res = bmesh.ops.extrude_face_region(bm, geom=[face])
    new_verts = [e for e in res["geom"] if isinstance(e, bmesh.types.BMVert)]
    bmesh.ops.translate(bm, verts=new_verts, vec=(0.0, 0.0, height))


def add_camera(location, target, lens=35.0):
    cam_data = bpy.data.cameras.new("Camera")
    cam_data.lens = lens
    cam_data.clip_end = 3000.0
    cam = bpy.data.objects.new("Camera", cam_data)
    link(cam)
    cam.location = location
    cam.rotation_euler = (Vector(target) - Vector(location)).to_track_quat('-Z', 'Y').to_euler()
    bpy.context.scene.camera = cam
    return cam


def add_sun(rotation, energy=4.0, color=(1.0, 0.9, 0.78)):
    data = bpy.data.lights.new("Sun", 'SUN')
    data.energy = energy
    data.angle = math.radians(1.5)
    data.color = color
    ob = bpy.data.objects.new("Sun", data)
    link(ob)
    ob.rotation_euler = rotation
    return ob


def add_area(location, size, energy, rotation=(0.0, 0.0, 0.0), color=(1.0, 1.0, 1.0)):
    data = bpy.data.lights.new("Area", 'AREA')
    data.size = size
    data.energy = energy
    data.color = color
    ob = bpy.data.objects.new("Area", data)
    link(ob)
    ob.location = location
    ob.rotation_euler = rotation
    return ob


# ----------------------------------------------------------------------------
# site
# ----------------------------------------------------------------------------
DECK_Z = 9.8
DECK = [(8.0, 0.0), (3.5, 6.0), (-8.0, 6.0), (-10.5, 0.0), (-8.0, -6.0), (3.5, -6.0)]


def terrain_h(x, y):
    """Cliff plateau on -X dropping to the sea toward +X, with rocky noise."""
    base = 8.0 / (1.0 + math.exp(x * 0.28))
    rough = max(0.0, min(1.0, (8.0 - x) / 16.0))
    n1 = noise.noise(Vector((x * 0.05, y * 0.05, 0.0))) * 2.3
    n2 = noise.noise(Vector((x * 0.17, y * 0.17, 3.1))) * 0.75
    z = base + (n1 + n2) * rough - 1.0
    return max(z, -4.5)


def roof_z(x):
    """Height of the folded roof underside datum above the deck, by X only."""
    if x <= -1.0:
        t = (x + 12.0) / 11.0
        return 3.6 + (5.3 - 3.6) * max(0.0, min(1.0, t))
    t = (x + 1.0) / 11.0
    return 5.3 + (2.8 - 5.3) * max(0.0, min(1.0, t))


def build():
    reset_scene()

    m_rock = new_mat("Rock", (0.34, 0.32, 0.29), rough=0.92)
    m_sea = new_mat("Sea", (0.02, 0.09, 0.16), rough=0.06, metal=0.0)
    m_steel = new_mat("Steel", (0.36, 0.38, 0.40), rough=0.35, metal=1.0)
    m_pale = new_mat("PaintedSteel", (0.86, 0.86, 0.84), rough=0.4, metal=0.6)
    m_wood = new_mat("DeckTimber", (0.47, 0.33, 0.19), rough=0.6)
    m_wood2 = new_mat("BenchTimber", (0.52, 0.38, 0.23), rough=0.55)
    m_concrete = new_mat("Concrete", (0.66, 0.65, 0.62), rough=0.8)
    m_glass = new_mat("ScreenGlass", (0.55, 0.68, 0.72), rough=0.04,
                      alpha=0.28, transmission=0.9)
    m_roof = new_mat("RoofPanel", (0.22, 0.24, 0.26), rough=0.35, metal=0.85)

    # ---- terrain -------------------------------------------------------------
    nx = ny = 70
    size = 80.0
    bm = bmesh.new()
    grid = []
    for i in range(nx + 1):
        row = []
        x = -size * 0.5 + size * i / nx
        for j in range(ny + 1):
            y = -size * 0.5 + size * j / ny
            row.append(bm.verts.new((x, y, terrain_h(x, y))))
        grid.append(row)
    bm.verts.ensure_lookup_table()
    for i in range(nx):
        for j in range(ny):
            bm.faces.new((grid[i][j], grid[i + 1][j], grid[i + 1][j + 1], grid[i][j + 1]))
    obj_from_bm("Headland", bm, m_rock, smooth=True)

    bm = bmesh.new()
    box_bm(bm, (60.0, 0.0, -2.5), (200.0, 400.0, 5.0))
    obj_from_bm("SeaFloor", bm, m_rock)

    bm = bmesh.new()
    box_bm(bm, (80.0, 0.0, -0.15), (400.0, 500.0, 0.3))
    obj_from_bm("Sea", bm, m_sea)

    # ---- deck structure --------------------------------------------------------
    bm = bmesh.new()
    prism_bm(bm, DECK, DECK_Z - 0.45, 0.45)
    obj_from_bm("DeckSlab", bm, m_concrete)

    def half_width(x):
        if x >= 3.5:
            return 6.0 * max(0.0, (8.0 - x) / 4.5)
        if x <= -8.0:
            return 6.0 * max(0.0, (x + 10.5) / 2.5)
        return 6.0

    bm = bmesh.new()
    x = -10.3
    while x < 7.9:
        hw = half_width(x) - 0.12
        if hw > 0.15:
            box_bm(bm, (x + 0.15, 0.0, DECK_Z + 0.03), (0.28, hw * 2.0, 0.07))
        x += 0.33
    obj_from_bm("DeckPlanks", bm, m_wood)

    # stilts down to the rock
    bm = bmesh.new()
    for (px, py) in DECK + [(-2.0, 0.0), (5.0, 3.0), (5.0, -3.0)]:
        gx, gy = px * 0.94, py * 0.94
        ground = terrain_h(gx, gy)
        tube_bm(bm, (gx, gy, min(ground - 1.2, DECK_Z - 1.0)),
                (gx, gy, DECK_Z - 0.45), 0.24, 10)
    # diagonal braces on the seaward stilts
    for (ax, ay, bx, by) in ((8.0, 0.0, 3.5, 6.0), (8.0, 0.0, 3.5, -6.0),
                             (3.5, 6.0, -2.0, 0.0), (3.5, -6.0, -2.0, 0.0)):
        za = terrain_h(ax * 0.94, ay * 0.94)
        tube_bm(bm, (ax * 0.94, ay * 0.94, max(za, 1.5) + 0.5),
                (bx * 0.94, by * 0.94, DECK_Z - 0.7), 0.11, 8)
    obj_from_bm("Stilts", bm, m_steel)

    # ---- columns and folded roof -------------------------------------------------
    col_xy = [(5.5, 0.0), (2.5, 5.0), (2.5, -5.0), (-7.0, 5.0), (-7.0, -5.0), (-9.5, 0.0)]
    bm = bmesh.new()
    for (cx, cy) in col_xy:
        top = DECK_Z + roof_z(cx) - 0.30
        tube_bm(bm, (cx, cy, DECK_Z), (cx, cy, top), 0.13, 10)
        box_bm(bm, (cx, cy, DECK_Z + 0.06), (0.55, 0.55, 0.12))
    obj_from_bm("Columns", bm, m_pale)

    z0 = DECK_Z + 0.10
    rv = [(-12.0, -8.0, z0 + 3.6), (-1.0, -8.8, z0 + 5.3), (10.0, -7.0, z0 + 2.8),
          (-12.0, 8.0, z0 + 3.6), (-1.0, 8.8, z0 + 5.3), (10.0, 7.0, z0 + 2.8)]
    me = bpy.data.meshes.new("RoofPanels")
    me.from_pydata(rv, [], [(0, 1, 4, 3), (1, 2, 5, 4)])
    me.update()
    roof = bpy.data.objects.new("Roof", me)
    roof.data.materials.append(m_roof)
    link(roof)
    mod = roof.modifiers.new("Solidify", 'SOLIDIFY')
    mod.thickness = 0.26
    mod.offset = -1.0

    # purlins under the roof
    bm = bmesh.new()
    for px in (-10.0, -5.5, -1.0, 3.5, 8.0):
        hw = 8.6 if abs(px + 1.0) < 3.0 else 7.6
        zz = DECK_Z + roof_z(px) - 0.32
        tube_bm(bm, (px, -hw, zz), (px, hw, zz), 0.09, 8)
    for py in (-6.5, 0.0, 6.5):
        prev = None
        for px in (-12.0, -6.0, -1.0, 4.0, 10.0):
            p = (px, py, DECK_Z + roof_z(px) - 0.45)
            if prev:
                tube_bm(bm, prev, p, 0.07, 6)
            prev = p
    obj_from_bm("RoofPurlins", bm, m_steel)

    # ---- wind screens ---------------------------------------------------------
    bm_glass = bmesh.new()
    bm_frame = bmesh.new()

    def screen(p1, p2, zb, h, tilt=0.0):
        a = Vector((p1[0], p1[1], 0.0))
        b = Vector((p2[0], p2[1], 0.0))
        d = b - a
        length = d.length
        ang = math.atan2(d.y, d.x)
        c = (a + b) * 0.5
        box_bm(bm_glass, (c.x, c.y, zb + h * 0.5), (length - 0.18, 0.05, h - 0.16),
               (tilt, 0.0, ang))
        for p in (a, b):
            tube_bm(bm_frame, (p.x, p.y, zb), (p.x, p.y, zb + h), 0.055, 8)
        tube_bm(bm_frame, (a.x, a.y, zb + h), (b.x, b.y, zb + h), 0.05, 8)
        tube_bm(bm_frame, (a.x, a.y, zb + 0.06), (b.x, b.y, zb + 0.06), 0.05, 8)
        # intermediate glazing bar
        mid = (a + b) * 0.5
        tube_bm(bm_frame, (mid.x, mid.y, zb), (mid.x, mid.y, zb + h), 0.04, 6)

    # long sides (partial - the prow stays open to the view)
    screen((-8.0, -6.0), (-3.0, -6.0), DECK_Z + 0.05, 2.45)
    screen((-3.0, -6.0), (2.0, -6.0), DECK_Z + 0.05, 2.45)
    screen((-8.0, 6.0), (-3.0, 6.0), DECK_Z + 0.05, 2.45)
    screen((-3.0, 6.0), (2.0, 6.0), DECK_Z + 0.05, 2.45)
    # angled landward corners and back wall
    screen((-8.0, 6.0), (-10.5, 0.0), DECK_Z + 0.05, 2.6)
    screen((-10.5, 0.0), (-8.0, -6.0), DECK_Z + 0.05, 2.6)
    # lower prow screens, slightly raked
    screen((2.0, -6.0), (3.5, -6.0), DECK_Z + 0.05, 1.5, tilt=math.radians(-6.0))
    screen((2.0, 6.0), (3.5, 6.0), DECK_Z + 0.05, 1.5, tilt=math.radians(6.0))
    obj_from_bm("WindScreenGlass", bm_glass, m_glass)
    obj_from_bm("WindScreenFrames", bm_frame, m_pale)

    # ---- railings on the open prow ----------------------------------------------
    bm = bmesh.new()

    def railing(p1, p2, z, height=1.10, spacing=1.5):
        a = Vector(p1)
        b = Vector(p2)
        length = (b - a).length
        n = max(2, int(length / spacing) + 1)
        pts = [a.lerp(b, i / (n - 1)) for i in range(n)]
        for p in pts:
            tube_bm(bm, (p.x, p.y, z), (p.x, p.y, z + height), 0.035, 6)
        for lvl in (height, height * 0.72, height * 0.48, height * 0.24):
            r = 0.032 if lvl == height else 0.014
            tube_bm(bm, (a.x, a.y, z + lvl), (b.x, b.y, z + lvl), r, 6)

    railing((3.5, -6.0), (8.0, 0.0), DECK_Z + 0.05)
    railing((8.0, 0.0), (3.5, 6.0), DECK_Z + 0.05)
    obj_from_bm("Railings", bm, m_steel)

    # ---- bench, telescope, stair --------------------------------------------------
    bm = bmesh.new()
    box_bm(bm, (-8.6, 0.0, DECK_Z + 0.48), (0.55, 7.0, 0.09), (0.0, 0.0, math.radians(90.0)))
    box_bm(bm, (-8.6, 0.0, DECK_Z + 0.48), (0.55, 7.0, 0.09))
    for by in (-2.6, 0.0, 2.6):
        box_bm(bm, (-8.6, by, DECK_Z + 0.24), (0.45, 0.12, 0.45))
    box_bm(bm, (-1.0, -5.6, DECK_Z + 0.5), (7.0, 0.5, 0.09))
    for bx in (-4.0, -1.0, 2.0):
        box_bm(bm, (bx, -5.6, DECK_Z + 0.25), (0.12, 0.42, 0.5))
    obj_from_bm("Benches", bm, m_wood2)

    bm = bmesh.new()
    tube_bm(bm, (6.6, 1.6, DECK_Z), (6.6, 1.6, DECK_Z + 1.25), 0.07, 10)
    tube_bm(bm, (6.6, 1.6, DECK_Z + 1.25), (7.5, 1.6, DECK_Z + 1.05), 0.11, 10)
    obj_from_bm("Telescope", bm, m_steel)

    bm = bmesh.new()
    steps = 17
    for k in range(steps):
        zt = DECK_Z - 0.2 * (k + 1)
        xs = -10.6 - 0.34 * k
        box_bm(bm, (xs, 0.0, zt - 0.10), (0.34, 2.6, 0.20))
    box_bm(bm, (-17.4, 0.0, DECK_Z - 0.2 * steps - 0.3), (2.4, 3.0, 0.5))
    obj_from_bm("Stair", bm, m_concrete)

    bm = bmesh.new()
    for side in (-1.35, 1.35):
        tube_bm(bm, (-10.6, side, DECK_Z + 1.0),
                (-10.6 - 0.34 * steps, side, DECK_Z - 0.2 * steps + 1.0), 0.035, 6)
        for k in range(0, steps, 4):
            xs = -10.6 - 0.34 * k
            zt = DECK_Z - 0.2 * k
            tube_bm(bm, (xs, side, zt), (xs, side, zt + 1.0), 0.03, 6)
    obj_from_bm("StairRail", bm, m_steel)

    # ---- lighting & camera ----------------------------------------------------
    add_sun((math.radians(62.0), math.radians(4.0), math.radians(28.0)),
            energy=4.6, color=(1.0, 0.88, 0.72))
    add_area((30.0, -22.0, 20.0), 30.0, 9000.0,
             rotation=(math.radians(64.0), 0.0, math.radians(52.0)),
             color=(0.7, 0.82, 1.0))
    add_camera((27.0, -21.0, 14.5), (-2.0, 0.0, 11.0), lens=35.0)


build()
