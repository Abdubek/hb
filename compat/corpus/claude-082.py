"""Modern pavilion: doubly curved shell roof on slim steel columns."""
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


def material(name, color, rough=0.5, metal=0.0, transmission=0.0, ior=1.45, alpha=1.0):
    m = bpy.data.materials.new(name)
    m.use_nodes = True
    b = m.node_tree.nodes.get("Principled BSDF")
    i = b.inputs
    i["Base Color"].default_value = (*color, 1.0)
    i["Roughness"].default_value = rough
    i["Metallic"].default_value = metal
    if "IOR" in i:
        i["IOR"].default_value = ior
    if "Transmission Weight" in i:
        i["Transmission Weight"].default_value = transmission
    i["Alpha"].default_value = alpha
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


def add_cyl(bm, p0, p1, r, seg=20, mi=0, r2=None):
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


def add_camera(loc, target, lens=35.0):
    cam = bpy.data.cameras.new("Camera")
    cam.lens = lens
    cam.clip_start, cam.clip_end = 0.05, 500.0
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


# ----------------------------------------------------------------- geometry
LX, LY = 9.0, 6.0     # roof half extents (includes overhang)
CX, CY = 7.0, 4.6     # column grid half extents


def roof_z(x, y):
    """Gentle barrel vault across Y, falling away towards the long ends."""
    return 4.15 + 1.55 * math.cos(math.pi * y / (2.0 * LY)) - 0.62 * (x / LX) ** 2


def build_roof_shell(mat, col):
    nx, ny = 56, 36
    bm = bmesh.new()
    grid = []
    for iy in range(ny + 1):
        y = -LY + 2.0 * LY * iy / ny
        row = []
        for ix in range(nx + 1):
            x = -LX + 2.0 * LX * ix / nx
            row.append(bm.verts.new((x, y, roof_z(x, y))))
        grid.append(row)
    for iy in range(ny):
        for ix in range(nx):
            bm.faces.new((grid[iy][ix], grid[iy][ix + 1],
                          grid[iy + 1][ix + 1], grid[iy + 1][ix]))
    ob = mesh_object("RoofShell", bm, [mat], col, smooth=True)
    sol = ob.modifiers.new("Solidify", 'SOLIDIFY')
    sol.thickness = 0.24
    sol.offset = -1.0
    sol.use_even_offset = True
    bev = ob.modifiers.new("Bevel", 'BEVEL')
    bev.width = 0.03
    bev.segments = 2
    bev.limit_method = 'ANGLE'
    return ob


def build():
    reset_scene()
    set_world((0.52, 0.64, 0.82), 1.6)

    col_arch = collection("Pavilion")
    col_site = collection("Site")

    m_roof = material("RoofPanel", (0.88, 0.88, 0.86), rough=0.34, metal=0.55)
    m_soffit = material("Soffit", (0.80, 0.68, 0.50), rough=0.6)
    m_steel = material("SlimSteel", (0.20, 0.21, 0.22), rough=0.28, metal=1.0)
    m_slab = material("Terrazzo", (0.78, 0.77, 0.74), rough=0.42)
    m_glass = material("Glazing", (0.72, 0.82, 0.84), rough=0.03,
                       transmission=1.0, ior=1.5)
    m_wood = material("BenchWood", (0.42, 0.26, 0.14), rough=0.55)
    m_grass = material("Ground", (0.19, 0.27, 0.13), rough=0.95)
    m_water = material("ReflectPool", (0.02, 0.06, 0.08), rough=0.06)
    m_plant = material("Hedge", (0.13, 0.30, 0.12), rough=0.85)

    build_roof_shell(m_roof, col_arch)

    # soffit lining just under the shell, gives the underside a warm tone
    bm = bmesh.new()
    nx, ny = 40, 26
    grid = []
    for iy in range(ny + 1):
        y = -(LY - 0.25) + 2.0 * (LY - 0.25) * iy / ny
        row = []
        for ix in range(nx + 1):
            x = -(LX - 0.25) + 2.0 * (LX - 0.25) * ix / nx
            row.append(bm.verts.new((x, y, roof_z(x, y) - 0.28)))
        grid.append(row)
    for iy in range(ny):
        for ix in range(nx):
            bm.faces.new((grid[iy][ix + 1], grid[iy][ix],
                          grid[iy + 1][ix], grid[iy + 1][ix + 1]))
    mesh_object("Soffit", bm, [m_soffit], col_arch, smooth=True)

    # --------------------------------------------------------------- columns
    bm = bmesh.new()
    for x in (-CX, -CX * 0.5, 0.0, CX * 0.5, CX):
        for sy in (-1.0, 1.0):
            y = sy * CY
            top_z = roof_z(x, y) - 0.30
            lean = 0.0 if abs(x) < CX - 1e-6 else -0.18 * (1.0 if x > 0 else -1.0)
            add_cyl(bm, (x, y, 0.06), (x + lean, y - sy * 0.10, top_z), 0.085, seg=20, mi=0)
            add_cyl(bm, (x, y, 0.06), (x, y, 0.16), 0.16, seg=20, mi=0)
    for x in (-3.0, 3.0):
        add_cyl(bm, (x, 0.0, 0.06), (x, 0.0, roof_z(x, 0.0) - 0.30), 0.075, seg=20, mi=0)
    mesh_object("Columns", bm, [m_steel], col_arch, smooth=True)

    # -------------------------------------------------------------- platform
    bm = bmesh.new()
    add_box(bm, (0.0, 0.0, -0.14), (2 * LX + 1.6, 2 * LY + 1.4, 0.40), 0)
    add_box(bm, (0.0, 0.0, -0.42), (2 * LX + 0.8, 2 * LY + 0.6, 0.24), 0)
    for depth, z in ((0.36, -0.30), (0.60, -0.48)):
        add_box(bm, (0.0, -(LY + 0.7) - depth, z), (9.0, 2 * depth, 0.22), 0)
    ob = mesh_object("Platform", bm, [m_slab], col_arch)
    bev = ob.modifiers.new("Bevel", 'BEVEL')
    bev.width = 0.015
    bev.segments = 2

    # --------------------------------------------------------- glazed screen
    bm_g = bmesh.new()
    bm_m = bmesh.new()
    x0, x1 = -CX - 0.4, 0.6
    panels = 6
    for i in range(panels):
        xa = x0 + (x1 - x0) * i / panels
        xb = x0 + (x1 - x0) * (i + 1) / panels
        xm = 0.5 * (xa + xb)
        h = roof_z(xm, CY) - 0.34
        add_box(bm_g, (xm, CY, h * 0.5 + 0.07), (xb - xa - 0.06, 0.024, h - 0.14), 0)
        add_box(bm_m, (xa, CY, h * 0.5 + 0.07), (0.05, 0.09, h - 0.06), 0)
    add_box(bm_m, (x1, CY, 2.4), (0.05, 0.09, 4.6), 0)
    add_box(bm_m, (0.5 * (x0 + x1), CY, 0.10), (x1 - x0, 0.10, 0.08), 0)
    mesh_object("Glazing", bm_g, [m_glass], col_arch)
    mesh_object("Mullions", bm_m, [m_steel], col_arch)

    # --------------------------------------------------------------- benches
    bm = bmesh.new()
    for bx in (-4.6, 1.4):
        for i in range(6):
            y = -1.9 + i * 0.28
            add_box(bm, (bx, y, 0.52), (2.6, 0.22, 0.05), 0)
        for sx in (-1.0, 1.0):
            add_box(bm, (bx + sx * 1.1, 0.0, 0.28), (0.10, 1.9, 0.44), 0)
    mesh_object("Benches", bm, [m_wood], col_arch)

    bm_p = bmesh.new()
    bm_h = bmesh.new()
    for sx in (-1.0, 1.0):
        for i in range(3):
            y = -3.2 + i * 3.2
            cx = sx * (LX + 2.4)
            add_box(bm_p, (cx, y, 0.05), (1.5, 2.4, 0.9), 0)
            add_box(bm_h, (cx, y, 0.62), (1.3, 2.2, 0.55), 0)
    mesh_object("Planters", bm_p, [m_slab], col_site)
    ob = mesh_object("Hedges", bm_h, [m_plant], col_site)
    b = ob.modifiers.new("Bevel", 'BEVEL')
    b.width = 0.08
    b.segments = 3

    # ------------------------------------------------------------- landscape
    bm = bmesh.new()
    add_box(bm, (0.0, 0.0, -0.80), (140.0, 140.0, 1.0), 0)
    mesh_object("Ground", bm, [m_grass], col_site)

    bm = bmesh.new()
    add_box(bm, (0.0, -14.0, -0.34), (26.0, 8.0, 0.10), 0)
    mesh_object("ReflectingPool", bm, [m_water], col_site)

    # ------------------------------------------------------------ light/cam
    add_light("Sun", 'SUN', (-16.0, -22.0, 24.0), 4.5,
              color=(1.0, 0.95, 0.86), target=(0.0, 0.0, 3.0), angle=math.radians(0.9))
    add_light("SkyDome", 'AREA', (8.0, 20.0, 22.0), 9000.0,
              color=(0.6, 0.72, 1.0), size=40.0, target=(0.0, 0.0, 3.0))
    add_light("UnderRoofFill", 'AREA', (0.0, -12.0, 2.4), 2200.0,
              color=(1.0, 0.92, 0.82), size=14.0, target=(0.0, 1.0, 3.6))

    add_camera((17.5, -19.0, 6.4), (-0.5, 0.3, 3.0), lens=35.0)

    print("Pavilion built: %d objects" % len(bpy.data.objects))


build()
