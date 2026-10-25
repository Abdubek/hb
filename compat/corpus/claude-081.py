"""Suspension bridge study: towers, main cables, hangers, deck, approaches."""
import bpy, bmesh, math
from mathutils import Vector, Matrix


def reset_scene():
    bpy.ops.wm.read_factory_settings(use_empty=True)
    sc = bpy.context.scene
    try:
        sc.render.engine = 'CYCLES'
        sc.cycles.samples = 96
    except Exception:
        pass
    sc.render.resolution_x, sc.render.resolution_y = 1920, 1080
    return sc


def collection(name):
    c = bpy.data.collections.new(name)
    bpy.context.scene.collection.children.link(c)
    return c


def material(name, color, rough=0.5, metal=0.0, emission=None, strength=0.0):
    m = bpy.data.materials.new(name)
    m.use_nodes = True
    b = m.node_tree.nodes.get("Principled BSDF")
    i = b.inputs
    i["Base Color"].default_value = (*color, 1.0)
    i["Roughness"].default_value = rough
    i["Metallic"].default_value = metal
    if emission is not None:
        i["Emission Color"].default_value = (*emission, 1.0)
        i["Emission Strength"].default_value = strength
    return m


def mesh_object(name, bm, mats, col, smooth=False):
    me = bpy.data.meshes.new(name)
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    bm.to_mesh(me)
    bm.free()
    for m in mats:
        me.materials.append(m)
    if smooth:
        for p in me.polygons:
            p.use_smooth = True
    ob = bpy.data.objects.new(name, me)
    col.objects.link(ob)
    return ob


def add_box(bm, center, size, mi=0):
    mat = Matrix.Translation(center) @ Matrix.Diagonal(Vector((size[0], size[1], size[2], 1.0)))
    res = bmesh.ops.create_cube(bm, size=1.0, matrix=mat)
    for v in res["verts"]:
        for f in v.link_faces:
            f.material_index = mi


def add_cyl(bm, p0, p1, r, seg=16, mi=0, r2=None):
    p0, p1 = Vector(p0), Vector(p1)
    d = p1 - p0
    h = d.length
    if h < 1e-9:
        return
    m = Matrix.Translation(p0 + d * 0.5) @ d.to_track_quat('Z', 'Y').to_matrix().to_4x4()
    res = bmesh.ops.create_cone(bm, cap_ends=True, cap_tris=False, segments=seg,
                                radius1=r, radius2=(r if r2 is None else r2), depth=h, matrix=m)
    for v in res["verts"]:
        for f in v.link_faces:
            f.material_index = mi


def add_prism(bm, x, y0, y1, z0, z1, hx0, hy0, hx1, hy1, mi=0):
    """Tapered rectangular prism, bottom footprint centred at y0, top at y1."""
    b = [(x - hx0, y0 - hy0, z0), (x + hx0, y0 - hy0, z0),
         (x + hx0, y0 + hy0, z0), (x - hx0, y0 + hy0, z0)]
    t = [(x - hx1, y1 - hy1, z1), (x + hx1, y1 - hy1, z1),
         (x + hx1, y1 + hy1, z1), (x - hx1, y1 + hy1, z1)]
    vb = [bm.verts.new(p) for p in b]
    vt = [bm.verts.new(p) for p in t]
    faces = [bm.faces.new(vb[::-1]), bm.faces.new(vt)]
    for i in range(4):
        j = (i + 1) % 4
        faces.append(bm.faces.new((vb[i], vb[j], vt[j], vt[i])))
    for f in faces:
        f.material_index = mi


def poly_curve(name, pts, depth, mat, col):
    cu = bpy.data.curves.new(name, 'CURVE')
    cu.dimensions = '3D'
    sp = cu.splines.new('POLY')
    sp.points.add(len(pts) - 1)
    for i, p in enumerate(pts):
        sp.points[i].co = (p[0], p[1], p[2], 1.0)
    cu.bevel_depth = depth
    cu.bevel_resolution = 3
    cu.use_fill_caps = True
    cu.materials.append(mat)
    ob = bpy.data.objects.new(name, cu)
    col.objects.link(ob)
    return ob


def add_light(name, kind, loc, energy, color=(1, 1, 1), size=1.0, target=(0, 0, 0), angle=None):
    l = bpy.data.lights.new(name, kind)
    l.energy = energy
    l.color = color
    if kind == 'AREA':
        l.size = size
    if kind == 'SUN' and angle is not None:
        l.angle = angle
    ob = bpy.data.objects.new(name, l)
    bpy.context.scene.collection.objects.link(ob)
    ob.location = loc
    ob.rotation_euler = (Vector(target) - Vector(loc)).to_track_quat('-Z', 'Y').to_euler()
    return ob


def add_camera(loc, target, lens=50.0, clip_start=0.1, clip_end=2000.0):
    cam = bpy.data.cameras.new("Camera")
    cam.lens = lens
    cam.clip_start, cam.clip_end = clip_start, clip_end
    ob = bpy.data.objects.new("Camera", cam)
    bpy.context.scene.collection.objects.link(ob)
    ob.location = loc
    ob.rotation_euler = (Vector(target) - Vector(loc)).to_track_quat('-Z', 'Y').to_euler()
    bpy.context.scene.camera = ob
    return ob


def set_world(color, strength):
    w = bpy.data.worlds.new("World")
    w.use_nodes = True
    bg = w.node_tree.nodes["Background"]
    bg.inputs[0].default_value = (*color, 1.0)
    bg.inputs[1].default_value = strength
    bpy.context.scene.world = w
    return w


# ------------------------------------------------------------- bridge params
TOWER_X = 60.0      # tower centreline
TOWER_TOP = 46.0    # saddle height
ANCHOR_X = 124.0    # cable anchorage
DECK_Z = 9.4        # roadway surface
DECK_HW = 7.0       # half width of deck
CABLE_Y = 6.4       # cable plane offset
MID_Z = 16.8        # cable low point at midspan
K = 0.030           # catenary constant
DECK_END = 165.0


def main_cable_z(x):
    return MID_Z + (TOWER_TOP - MID_Z) * (math.cosh(K * x) - 1.0) / (math.cosh(K * TOWER_X) - 1.0)


def side_cable_z(x):
    t = (abs(x) - TOWER_X) / (ANCHOR_X - TOWER_X)
    return TOWER_TOP + (7.6 - TOWER_TOP) * t - 4.0 * 2.4 * t * (1.0 - t)


def cable_z(x):
    return main_cable_z(x) if abs(x) <= TOWER_X else side_cable_z(x)


def tower_leg_y(z):
    """Legs lean inward with height until they meet the cable plane."""
    t = max(0.0, min(1.0, (z - 3.0) / (TOWER_TOP - 3.0)))
    return 8.6 + (CABLE_Y - 8.6) * t


def build():
    reset_scene()
    set_world((0.45, 0.58, 0.75), 1.2)

    col_struct = collection("Structure")
    col_cables = collection("Cables")
    col_deck = collection("Deck")
    col_site = collection("Site")

    m_concrete = material("Concrete", (0.62, 0.61, 0.58), rough=0.75)
    m_steel = material("SteelCable", (0.34, 0.35, 0.37), rough=0.38, metal=1.0)
    m_paint = material("DeckSteel", (0.42, 0.20, 0.17), rough=0.55, metal=0.4)
    m_asphalt = material("Asphalt", (0.055, 0.055, 0.06), rough=0.9)
    m_line = material("RoadLine", (0.86, 0.84, 0.72), rough=0.65)
    m_rail = material("Railing", (0.72, 0.73, 0.74), rough=0.35, metal=0.9)
    m_water = material("Water", (0.02, 0.06, 0.10), rough=0.12)
    m_land = material("Land", (0.18, 0.22, 0.12), rough=0.95)
    m_lamp = material("LampGlow", (1.0, 0.86, 0.62), rough=0.3,
                      emission=(1.0, 0.83, 0.55), strength=28.0)

    # ------------------------------------------------------- towers & piers
    bm = bmesh.new()
    for sx in (-1.0, 1.0):
        x = sx * TOWER_X
        add_box(bm, (x, 0.0, -1.5), (17.0, 27.0, 9.0), 0)
        add_box(bm, (x, 0.0, 3.6), (14.0, 23.0, 1.6), 0)
        for sy in (-1.0, 1.0):
            y0 = sy * tower_leg_y(4.4)
            y1 = sy * tower_leg_y(TOWER_TOP)
            add_prism(bm, x, y0, y1, 4.4, TOWER_TOP, 2.1, 2.6, 1.15, 1.5, 0)
            add_box(bm, (x, sy * CABLE_Y, TOWER_TOP + 0.7), (3.0, 3.4, 1.4), 0)
        for z, hz in ((13.5, 1.3), (27.0, 1.2), (41.5, 1.4)):
            hy = tower_leg_y(z)
            add_box(bm, (x, 0.0, z), (2.6, 2.0 * hy, 2.0 * hz), 0)
    mesh_object("Towers", bm, [m_concrete], col_struct)

    # ------------------------------------------------------- anchor blocks
    bm = bmesh.new()
    for sx in (-1.0, 1.0):
        add_box(bm, (sx * ANCHOR_X, 0.0, 3.4), (20.0, 30.0, 12.0), 0)
        add_box(bm, (sx * (ANCHOR_X - 11.0), 0.0, 8.0), (6.0, 22.0, 3.2), 0)
    mesh_object("Anchorages", bm, [m_concrete], col_struct)

    # ---------------------------------------------------------- main cables
    xs = [-ANCHOR_X + i * (2.0 * ANCHOR_X / 240.0) for i in range(241)]
    for sy in (-1.0, 1.0):
        pts = [(x, sy * CABLE_Y, cable_z(x)) for x in xs]
        poly_curve("MainCable_%s" % ("L" if sy < 0 else "R"), pts, 0.42, m_steel, col_cables)

    # --------------------------------------------------------------- hangers
    bm = bmesh.new()
    for i in range(-9, 10):
        x = i * 6.0
        ztop = main_cable_z(x)
        if ztop < DECK_Z + 2.2:
            continue
        for sy in (-1.0, 1.0):
            y = sy * CABLE_Y
            add_cyl(bm, (x, y, DECK_Z - 0.4), (x, y, ztop), 0.11, seg=8, mi=0)
            add_box(bm, (x, y, DECK_Z + 0.15), (0.9, 0.9, 0.9), 0)
    mesh_object("Hangers", bm, [m_steel], col_cables)

    # -------------------------------------------------------------- deck box
    bm = bmesh.new()
    L = 2.0 * DECK_END
    add_box(bm, (0.0, 0.0, DECK_Z - 0.25), (L, 2.0 * DECK_HW, 0.5), 0)
    for sy in (-1.0, 1.0):
        add_box(bm, (0.0, sy * (DECK_HW - 0.5), DECK_Z - 1.25), (L, 1.0, 2.0), 0)
        add_box(bm, (0.0, sy * (DECK_HW - 0.12), DECK_Z + 0.05), (L, 0.24, 0.30), 0)
    n_cross = int((2 * ANCHOR_X) // 6)
    for i in range(n_cross + 1):
        x = -ANCHOR_X + i * 6.0
        add_box(bm, (x, 0.0, DECK_Z - 1.25), (0.55, 2.0 * DECK_HW - 0.4, 1.4), 0)
    add_box(bm, (0.0, 0.0, DECK_Z - 1.35), (2.0 * ANCHOR_X, 1.2, 1.2), 0)
    mesh_object("DeckStructure", bm, [m_paint], col_deck)

    bm = bmesh.new()
    add_box(bm, (0.0, 0.0, DECK_Z + 0.005), (L, 2.0 * (DECK_HW - 0.9), 0.06), 0)
    mesh_object("Roadway", bm, [m_asphalt], col_deck)

    bm = bmesh.new()
    seg = 4.0
    n = int(L // (2 * seg))
    for i in range(-n, n + 1):
        add_box(bm, (i * 2 * seg, 0.0, DECK_Z + 0.045), (seg, 0.22, 0.03), 0)
    for sy in (-1.0, 1.0):
        add_box(bm, (0.0, sy * (DECK_HW - 1.1), DECK_Z + 0.045), (L, 0.20, 0.03), 0)
        for i in range(-n, n + 1):
            add_box(bm, (i * 2 * seg, sy * 3.2, DECK_Z + 0.045), (seg, 0.18, 0.03), 0)
    mesh_object("RoadMarkings", bm, [m_line], col_deck)

    # -------------------------------------------------------------- railings
    bm = bmesh.new()
    posts = int(L // 3.0)
    for i in range(posts + 1):
        x = -DECK_END + i * 3.0
        for sy in (-1.0, 1.0):
            y = sy * (DECK_HW - 0.12)
            add_cyl(bm, (x, y, DECK_Z + 0.18), (x, y, DECK_Z + 1.35), 0.055, seg=8, mi=0)
    for sy in (-1.0, 1.0):
        y = sy * (DECK_HW - 0.12)
        for z in (DECK_Z + 1.30, DECK_Z + 0.85, DECK_Z + 0.45):
            add_cyl(bm, (-DECK_END, y, z), (DECK_END, y, z), 0.05, seg=8, mi=0)
    mesh_object("Railings", bm, [m_rail], col_deck)

    # ------------------------------------------------------------ lamp posts
    bm_pole = bmesh.new()
    bm_head = bmesh.new()
    for i in range(-6, 7):
        x = i * 24.0
        for sy in (-1.0, 1.0):
            y = sy * (DECK_HW - 0.55)
            base = (x, y, DECK_Z + 0.05)
            top = (x, y, DECK_Z + 7.2)
            add_cyl(bm_pole, base, top, 0.13, seg=10, mi=0, r2=0.09)
            arm_end = (x, y - sy * 1.5, DECK_Z + 7.4)
            add_cyl(bm_pole, top, arm_end, 0.08, seg=8, mi=0)
            add_box(bm_head, (arm_end[0], arm_end[1], arm_end[2] - 0.15), (1.0, 0.45, 0.22), 0)
    mesh_object("LampPosts", bm_pole, [m_rail], col_deck)
    mesh_object("LampHeads", bm_head, [m_lamp], col_deck)

    bm = bmesh.new()
    for sx in (-1.0, 1.0):
        for sy in (-1.0, 1.0):
            add_cyl(bm, (sx * TOWER_X, sy * CABLE_Y, TOWER_TOP + 1.4),
                    (sx * TOWER_X, sy * CABLE_Y, TOWER_TOP + 1.9), 0.35, seg=10, mi=0)
    mesh_object("WarningLights", bm,
                [material("RedBeacon", (0.9, 0.08, 0.06), 0.4,
                          emission=(1.0, 0.1, 0.06), strength=40.0)], col_struct)

    # ------------------------------------------------------------------ site
    bm = bmesh.new()
    add_box(bm, (0.0, 0.0, -1.0), (900.0, 700.0, 2.0), 0)
    mesh_object("Water", bm, [m_water], col_site)

    bm = bmesh.new()
    for sx in (-1.0, 1.0):
        add_box(bm, (sx * 200.0, 0.0, 4.0), (200.0, 420.0, 8.6), 0)
        add_box(bm, (sx * 118.0, 0.0, 3.0), (40.0, 120.0, 6.6), 0)
    mesh_object("Shoreline", bm, [m_land], col_site)

    bm = bmesh.new()
    for sx in (-1.0, 1.0):
        for d in (140.0, 152.0):
            add_box(bm, (sx * d, 0.0, DECK_Z / 2.0 - 1.0), (3.0, 12.0, DECK_Z - 1.0), 0)
    mesh_object("ApproachPiers", bm, [m_concrete], col_site)

    # ------------------------------------------------------------ light/cam
    add_light("Sun", 'SUN', (-140.0, -180.0, 160.0), 4.0,
              color=(1.0, 0.94, 0.84), target=(0.0, 0.0, 20.0), angle=math.radians(1.2))
    add_light("SkyFill", 'AREA', (120.0, 160.0, 130.0), 900000.0,
              color=(0.62, 0.74, 1.0), size=180.0, target=(0.0, 0.0, 18.0))
    add_light("Bounce", 'AREA', (0.0, -90.0, 6.0), 250000.0,
              color=(0.55, 0.65, 0.8), size=140.0, target=(0.0, 0.0, 24.0))

    add_camera((-118.0, -152.0, 58.0), (6.0, 0.0, 20.0), lens=45.0,
               clip_start=0.5, clip_end=3000.0)

    print("Suspension bridge built: %d objects" % len(bpy.data.objects))


build()
