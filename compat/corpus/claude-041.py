"""claude-041 : A tiny house with porch, pitched roof and chimney (Blender 4.5 LTS)."""

import bpy, bmesh, math, random
from mathutils import Vector, Matrix


# ------------------------------------------------------------------ helpers
def reset():
    bpy.ops.wm.read_factory_settings(use_empty=True)


def mat(name, color, rough=0.6, metal=0.0, trans=0.0, alpha=1.0, ior=1.45, emit=None, es=0.0):
    m = bpy.data.materials.new(name)
    m.use_nodes = True
    b = m.node_tree.nodes["Principled BSDF"]

    def p(k, v):
        s = b.inputs.get(k)
        if s is not None:
            s.default_value = v

    p("Base Color", (*color, 1.0)); p("Roughness", rough); p("Metallic", metal)
    p("IOR", ior); p("Transmission Weight", trans); p("Alpha", alpha)
    if emit is not None:
        p("Emission Color", (*emit, 1.0)); p("Emission Strength", es)
    if trans > 0.0 or alpha < 1.0:
        for a, v in (("surface_render_method", 'BLENDED'), ("blend_method", 'BLEND')):
            try:
                setattr(m, a, v)
            except Exception:
                pass
    return m


def add_box(bm, size, matrix=None):
    v = bmesh.ops.create_cube(bm, size=1.0)["verts"]
    bmesh.ops.scale(bm, vec=Vector(size), verts=v)
    if matrix is not None:
        bmesh.ops.transform(bm, matrix=matrix, verts=v)
    return v


def add_cone(bm, r1, r2, depth, matrix=None, seg=20):
    v = bmesh.ops.create_cone(bm, cap_ends=True, cap_tris=False, segments=seg,
                              radius1=r1, radius2=r2, depth=depth)["verts"]
    if matrix is not None:
        bmesh.ops.transform(bm, matrix=matrix, verts=v)
    return v


def add_cyl(bm, r, depth, matrix=None, seg=20):
    return add_cone(bm, r, r, depth, matrix, seg)


def add_sphere(bm, r, matrix=None, u=16, v=10):
    vs = bmesh.ops.create_uvsphere(bm, u_segments=u, v_segments=v, radius=r)["verts"]
    if matrix is not None:
        bmesh.ops.transform(bm, matrix=matrix, verts=vs)
    return vs


def add_strut(bm, p0, p1, w, t):
    """Box of section w x t running from p0 to p1 (local X along the run)."""
    p0, p1 = Vector(p0), Vector(p1)
    d = p1 - p0
    if d.length < 1e-6:
        return
    q = d.normalized().to_track_quat('X', 'Z')
    add_box(bm, (d.length, w, t), Matrix.Translation((p0 + p1) * 0.5) @ q.to_matrix().to_4x4())


def add_prism(bm, profile, depth, matrix=None):
    """Closed XZ profile extruded along Y."""
    vs = [bm.verts.new((x, -depth * 0.5, z)) for (x, z) in profile]
    f = bm.faces.new(vs)
    res = bmesh.ops.extrude_face_region(bm, geom=[f])
    nv = [e for e in res["geom"] if isinstance(e, bmesh.types.BMVert)]
    bmesh.ops.translate(bm, vec=(0.0, depth, 0.0), verts=nv)
    if matrix is not None:
        bmesh.ops.transform(bm, matrix=matrix, verts=vs + nv)


def finish(bm, name, material=None, smooth=False, loc=(0.0, 0.0, 0.0)):
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    me = bpy.data.meshes.new(name)
    bm.to_mesh(me)
    bm.free()
    me.validate()
    ob = bpy.data.objects.new(name, me)
    bpy.context.scene.collection.objects.link(ob)
    ob.location = loc
    if material is not None:
        me.materials.append(material)
    if smooth:
        for p in me.polygons:
            p.use_smooth = True
    return ob


def add_camera(loc, target, lens=40.0):
    c = bpy.data.cameras.new("Camera")
    c.lens = lens
    ob = bpy.data.objects.new("Camera", c)
    bpy.context.scene.collection.objects.link(ob)
    ob.location = loc
    ob.rotation_euler = (Vector(target) - Vector(loc)).to_track_quat('-Z', 'Y').to_euler()
    bpy.context.scene.camera = ob
    return ob


def add_sun(name, energy, rot, color=(1.0, 0.95, 0.88), angle=0.02):
    d = bpy.data.lights.new(name, 'SUN')
    d.energy, d.color, d.angle = energy, color, angle
    ob = bpy.data.objects.new(name, d)
    bpy.context.scene.collection.objects.link(ob)
    ob.rotation_euler = rot
    return ob


def add_area(name, energy, loc, target, size=5.0, color=(1.0, 1.0, 1.0)):
    d = bpy.data.lights.new(name, 'AREA')
    d.energy, d.size, d.color = energy, size, color
    ob = bpy.data.objects.new(name, d)
    bpy.context.scene.collection.objects.link(ob)
    ob.location = loc
    ob.rotation_euler = (Vector(target) - Vector(loc)).to_track_quat('-Z', 'Y').to_euler()
    return ob


# --------------------------------------------------------------- wall tools
def add_wall(bm, length, height, thick, openings, matrix):
    """Wall along local X, thickness on local Y, exterior facing local -Y."""
    segs, cursor = [], -length * 0.5
    for (c, w, sill, top) in sorted(openings, key=lambda o: o[0]):
        a, b = c - w * 0.5, c + w * 0.5
        if a > cursor:
            segs.append((cursor, a, 0.0, height))
        if sill > 0.001:
            segs.append((a, b, 0.0, sill))
        if top < height - 0.001:
            segs.append((a, b, top, height))
        cursor = b
    if cursor < length * 0.5:
        segs.append((cursor, length * 0.5, 0.0, height))
    for (x0, x1, z0, z1) in segs:
        if x1 - x0 < 1e-4 or z1 - z0 < 1e-4:
            continue
        add_box(bm, (x1 - x0, thick, z1 - z0),
                matrix @ Matrix.Translation(((x0 + x1) * 0.5, 0.0, (z0 + z1) * 0.5)))


def add_casing(bm, matrix, c, w, sill, top, thick, board=0.09, ext=0.05):
    y = -(thick * 0.5 + ext * 0.5)
    for s in (-1, 1):
        add_box(bm, (board, ext, top - sill + 2.0 * board),
                matrix @ Matrix.Translation((c + s * (w * 0.5 + board * 0.5), y, (sill + top) * 0.5)))
    add_box(bm, (w + 2.0 * board, ext, board), matrix @ Matrix.Translation((c, y, top + board * 0.5)))
    if sill > 0.1:
        add_box(bm, (w + 2.0 * board, ext, board),
                matrix @ Matrix.Translation((c, y, sill - board * 0.5)))
        add_box(bm, (w + 0.34, 0.16, 0.05),
                matrix @ Matrix.Translation((c, -thick * 0.5 - 0.05, sill - board - 0.03)))


# ----------------------------------------------------------------- build
def build():
    reset()
    random.seed(41)
    scene = bpy.context.scene
    scene.render.resolution_x, scene.render.resolution_y = 1600, 1000

    world = bpy.data.worlds.new("World")
    scene.world = world
    world.use_nodes = True
    bg = world.node_tree.nodes["Background"]
    bg.inputs[0].default_value = (0.42, 0.58, 0.82, 1.0)
    bg.inputs[1].default_value = 0.85

    m_siding = mat("Siding", (0.78, 0.77, 0.70), 0.72)
    m_trim = mat("Trim", (0.94, 0.94, 0.91), 0.45)
    m_roof = mat("Shingles", (0.075, 0.085, 0.10), 0.85)
    m_stone = mat("Foundation", (0.30, 0.29, 0.28), 0.92)
    m_brick = mat("Brick", (0.40, 0.17, 0.12), 0.88)
    m_wood = mat("PorchWood", (0.42, 0.28, 0.17), 0.72)
    m_door = mat("Door", (0.09, 0.25, 0.29), 0.42)
    m_glass = mat("WindowGlass", (0.82, 0.90, 0.94), 0.06, trans=1.0, alpha=0.28)
    m_metal = mat("Metal", (0.72, 0.71, 0.69), 0.32, metal=1.0)
    m_grass = mat("Grass", (0.19, 0.33, 0.12), 0.95)
    m_path = mat("Path", (0.52, 0.50, 0.46), 0.88)
    m_leaf = mat("Foliage", (0.15, 0.31, 0.11), 0.82)
    m_glow = mat("LampGlow", (1.0, 0.86, 0.58), 0.3, emit=(1.0, 0.82, 0.5), es=8.0)

    W, D, H, T = 4.0, 5.0, 2.5, 0.16       # width(x), depth(y), wall height, thickness
    PITCH = math.radians(34.0)
    tanp, cosp, sinp = math.tan(PITCH), math.cos(PITCH), math.sin(PITCH)
    OVER, FZ = 0.40, 0.50                  # eave overhang, floor level
    RIDGE = FZ + H + (W * 0.5) * tanp

    # ground
    bm = bmesh.new()
    add_box(bm, (70.0, 70.0, 0.4), Matrix.Translation((0.0, 0.0, -0.2)))
    finish(bm, "Ground", m_grass)

    # foundation and porch piers
    bm = bmesh.new()
    add_box(bm, (W + 0.34, D + 0.34, FZ), Matrix.Translation((0.0, 0.0, FZ * 0.5)))
    for px in (-1.78, 1.78):
        for py in (-2.65, -4.25):
            add_box(bm, (0.30, 0.30, FZ - 0.05), Matrix.Translation((px, py, (FZ - 0.05) * 0.5)))
    finish(bm, "Foundation", m_stone)

    # walls (local -Y is always the exterior face)
    walls = [
        (W, Matrix.Translation((0.0, -D * 0.5 + T * 0.5, FZ)),
         [(-0.85, 0.95, 0.0, 2.05), (1.15, 0.95, 0.95, 1.85)]),
        (W, Matrix.Translation((0.0, D * 0.5 - T * 0.5, FZ)) @ Matrix.Rotation(math.pi, 4, 'Z'),
         [(0.0, 1.40, 0.90, 1.90)]),
        (D - 2.0 * T, Matrix.Translation((-W * 0.5 + T * 0.5, 0.0, FZ))
         @ Matrix.Rotation(math.radians(-90.0), 4, 'Z'), [(0.0, 1.10, 0.95, 1.85)]),
        (D - 2.0 * T, Matrix.Translation((W * 0.5 - T * 0.5, 0.0, FZ))
         @ Matrix.Rotation(math.radians(90.0), 4, 'Z'), [(-1.20, 0.90, 0.95, 1.85)]),
    ]

    bm = bmesh.new()
    for (length, mtx, openings) in walls:
        add_wall(bm, length, H, T, openings, mtx)
    gable = [(-W * 0.5, FZ + H), (W * 0.5, FZ + H), (0.0, RIDGE)]
    for sy in (-1, 1):
        add_prism(bm, gable, T, Matrix.Translation((0.0, sy * (D * 0.5 - T * 0.5), 0.0)))
    z = FZ + 0.22                                       # lap-siding shadow lines
    while z < FZ + H - 0.1:
        for sx in (-1, 1):
            add_box(bm, (0.03, D - 0.02, 0.03), Matrix.Translation((sx * (W * 0.5 + 0.005), 0.0, z)))
        z += 0.24
    finish(bm, "Walls", m_siding)

    # trim: casings, corner boards, fascia
    run = W * 0.5 + OVER
    z_eave = RIDGE - run * tanp
    bm = bmesh.new()
    for (length, mtx, openings) in walls:
        for (c, w, sill, top) in openings:
            add_casing(bm, mtx, c, w, sill, top, T)
    for sx in (-1, 1):
        for sy in (-1, 1):
            add_box(bm, (0.13, 0.13, H),
                    Matrix.Translation((sx * (W * 0.5 - 0.02), sy * (D * 0.5 - 0.02), FZ + H * 0.5)))
    for s in (-1, 1):
        add_strut(bm, (s * run, -D * 0.5 - OVER, z_eave - 0.06),
                  (s * run, D * 0.5 + OVER, z_eave - 0.06), 0.06, 0.22)
    finish(bm, "Trim", m_trim)

    # glazing and muntins
    bg_, bmun = bmesh.new(), bmesh.new()
    for (length, mtx, openings) in walls:
        for (c, w, sill, top) in openings:
            if sill < 0.1:
                continue
            h = top - sill
            add_box(bg_, (w - 0.06, 0.02, h - 0.06), mtx @ Matrix.Translation((c, 0.0, (sill + top) * 0.5)))
            add_box(bmun, (0.035, 0.05, h - 0.06), mtx @ Matrix.Translation((c, -0.02, (sill + top) * 0.5)))
            add_box(bmun, (w - 0.06, 0.05, 0.035), mtx @ Matrix.Translation((c, -0.02, (sill + top) * 0.5)))
    finish(bg_, "Glazing", m_glass)
    finish(bmun, "Muntins", m_trim)

    # roof planes and ridge cap
    bm = bmesh.new()
    for s in (-1, 1):
        n = Vector((s * sinp, 0.0, cosp))
        add_strut(bm, Vector((0.0, 0.0, RIDGE)) + n * 0.055,
                  Vector((s * run, 0.0, z_eave)) + n * 0.055, D + 2.0 * OVER, 0.11)
    add_strut(bm, (0.0, -D * 0.5 - OVER, RIDGE + 0.09), (0.0, D * 0.5 + OVER, RIDGE + 0.09), 0.30, 0.10)
    finish(bm, "Roof", m_roof)

    # porch deck, steps, posts and railing
    y0, y1 = -D * 0.5 - 1.90, -D * 0.5
    bm = bmesh.new()
    add_box(bm, (3.90, y1 - y0, 0.14), Matrix.Translation((0.0, (y0 + y1) * 0.5, FZ - 0.11)))
    x = -1.90
    while x < 1.88:
        add_box(bm, (0.26, y1 - y0 - 0.02, 0.045), Matrix.Translation((x + 0.13, (y0 + y1) * 0.5, FZ - 0.02)))
        x += 0.285
    for i in range(2):
        add_box(bm, (1.40, 0.32, 0.10),
                Matrix.Translation((-0.85, y0 - 0.16 - i * 0.32, FZ - 0.06 - (i + 1) * 0.16)))
    for (px, py) in ((-1.78, y1 - 0.14), (1.78, y1 - 0.14), (-1.78, y0 + 0.14), (1.78, y0 + 0.14)):
        add_box(bm, (0.13, 0.13, 2.25), Matrix.Translation((px, py, FZ + 1.12)))
    for (a, b) in (((-1.78, y0 + 0.14), (-1.78, y1 - 0.14)),
                   ((1.78, y0 + 0.14), (1.78, y1 - 0.14)),
                   ((-1.78, y0 + 0.14), (-1.55, y0 + 0.14)),
                   ((1.78, y0 + 0.14), (-0.15, y0 + 0.14))):
        for zz, sec in ((FZ + 0.92, (0.09, 0.05)), (FZ + 0.18, (0.07, 0.05))):
            add_strut(bm, (a[0], a[1], zz), (b[0], b[1], zz), sec[0], sec[1])
        seg = Vector((b[0] - a[0], b[1] - a[1], 0.0))
        n = max(1, int(seg.length / 0.17))
        for i in range(1, n):
            p = Vector((a[0], a[1], 0.0)) + seg * (i / n)
            add_box(bm, (0.04, 0.04, 0.70), Matrix.Translation((p.x, p.y, FZ + 0.55)))
    finish(bm, "Porch", m_wood)

    bm = bmesh.new()
    add_strut(bm, (0.0, y1 + 0.06, FZ + 2.42), (0.0, y0 - 0.22, FZ + 2.02), 4.10, 0.09)
    add_strut(bm, (-2.05, y0 + 0.14, FZ + 2.06), (2.05, y0 + 0.14, FZ + 2.06), 0.10, 0.20)
    finish(bm, "PorchRoof", m_roof)

    # front door, hardware, porch lamp
    dy = -D * 0.5 + T * 0.5
    bm = bmesh.new()
    add_box(bm, (0.92, 0.06, 2.02), Matrix.Translation((-0.85, dy - 0.03, FZ + 1.01)))
    for zc in (FZ + 0.55, FZ + 1.50):
        add_box(bm, (0.60, 0.03, 0.62), Matrix.Translation((-0.85, dy - 0.07, zc)))
    finish(bm, "Door", m_door)

    bm = bmesh.new()
    add_sphere(bm, 0.045, Matrix.Translation((-0.45, dy - 0.10, FZ + 0.98)))
    add_cyl(bm, 0.018, 0.06, Matrix.Translation((-0.45, dy - 0.06, FZ + 0.98))
            @ Matrix.Rotation(math.radians(90.0), 4, 'X'), 12)
    add_box(bm, (0.05, 0.05, 0.14), Matrix.Translation((-0.20, dy - 0.11, FZ + 1.95)))
    finish(bm, "Hardware", m_metal, smooth=True)

    bm = bmesh.new()
    add_box(bm, (0.16, 0.16, 0.22), Matrix.Translation((-0.20, dy - 0.11, FZ + 1.80)))
    finish(bm, "LampGlass", m_glow)

    # chimney on the +X wall
    cx, cy = W * 0.5 + 0.22, 1.15
    bm = bmesh.new()
    add_box(bm, (0.62, 0.92, RIDGE + 0.55), Matrix.Translation((cx, cy, (RIDGE + 0.55) * 0.5)))
    add_box(bm, (0.74, 1.04, 0.13), Matrix.Translation((cx, cy, RIDGE + 0.61)))
    finish(bm, "Chimney", m_brick)
    bm = bmesh.new()
    for oy in (-0.22, 0.22):
        add_cyl(bm, 0.095, 0.34, Matrix.Translation((cx, cy + oy, RIDGE + 0.83)), 16)
    finish(bm, "FluePots", m_stone, smooth=True)

    # path and shrubs
    bm = bmesh.new()
    for i in range(7):
        add_box(bm, (1.30, 0.62, 0.06),
                Matrix.Translation((-0.85 + math.sin(i * 0.7) * 0.18, y0 - 0.95 - i * 0.72, 0.03)))
    finish(bm, "Path", m_path)

    bm = bmesh.new()
    for (bx, by, br) in ((-2.55, -2.10, 0.42), (2.45, -1.60, 0.36), (2.75, 0.95, 0.30), (-2.70, 0.40, 0.34)):
        for k in range(3):
            r = br * (0.75 + 0.25 * random.random())
            add_sphere(bm, r, Matrix.Translation((bx + random.uniform(-0.2, 0.2),
                                                  by + random.uniform(-0.2, 0.2),
                                                  r * 0.85 + k * 0.12)), 14, 9)
    finish(bm, "Shrubs", m_leaf, smooth=True)

    add_sun("KeySun", 4.2, (math.radians(52.0), 0.0, math.radians(38.0)), (1.0, 0.94, 0.84), 0.02)
    add_area("Fill", 220.0, (-7.0, -8.0, 4.5), (0.0, -1.0, 1.6), 8.0, (0.72, 0.82, 1.0))
    add_area("PorchFill", 45.0, (-0.9, -4.4, 1.9), (-0.85, -2.4, 1.2), 1.6, (1.0, 0.86, 0.62))
    add_camera((8.6, -9.6, 5.0), (0.0, -1.2, 1.75), lens=42.0)


build()
