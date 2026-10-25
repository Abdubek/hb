"""claude-042 : A greenhouse with frame, roof and planting tables (Blender 4.5 LTS)."""

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


def add_cone(bm, r1, r2, depth, matrix=None, seg=16):
    v = bmesh.ops.create_cone(bm, cap_ends=True, cap_tris=False, segments=seg,
                              radius1=r1, radius2=r2, depth=depth)["verts"]
    if matrix is not None:
        bmesh.ops.transform(bm, matrix=matrix, verts=v)
    return v


def add_cyl(bm, r, depth, matrix=None, seg=18):
    return add_cone(bm, r, r, depth, matrix, seg)


def add_sphere(bm, r, matrix=None, u=14, v=9):
    vs = bmesh.ops.create_uvsphere(bm, u_segments=u, v_segments=v, radius=r)["verts"]
    if matrix is not None:
        bmesh.ops.transform(bm, matrix=matrix, verts=vs)
    return vs


def add_strut(bm, p0, p1, w, t):
    p0, p1 = Vector(p0), Vector(p1)
    d = p1 - p0
    if d.length < 1e-6:
        return
    q = d.normalized().to_track_quat('X', 'Z')
    add_box(bm, (d.length, w, t), Matrix.Translation((p0 + p1) * 0.5) @ q.to_matrix().to_4x4())


def add_prism(bm, profile, depth, matrix=None):
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


def add_camera(loc, target, lens=36.0):
    c = bpy.data.cameras.new("Camera")
    c.lens = lens
    ob = bpy.data.objects.new("Camera", c)
    bpy.context.scene.collection.objects.link(ob)
    ob.location = loc
    ob.rotation_euler = (Vector(target) - Vector(loc)).to_track_quat('-Z', 'Y').to_euler()
    bpy.context.scene.camera = ob
    return ob


def add_sun(name, energy, rot, color=(1.0, 0.96, 0.9), angle=0.015):
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


# ----------------------------------------------------------------- build
def build():
    reset()
    random.seed(42)
    scene = bpy.context.scene
    scene.render.resolution_x, scene.render.resolution_y = 1600, 1000

    world = bpy.data.worlds.new("World")
    scene.world = world
    world.use_nodes = True
    bg = world.node_tree.nodes["Background"]
    bg.inputs[0].default_value = (0.52, 0.66, 0.86, 1.0)
    bg.inputs[1].default_value = 1.1

    m_frame = mat("Aluminium", (0.74, 0.75, 0.76), 0.34, metal=1.0)
    m_glass = mat("Glazing", (0.83, 0.92, 0.90), 0.05, trans=1.0, alpha=0.22)
    m_brick = mat("Kneewall", (0.44, 0.24, 0.19), 0.9)
    m_conc = mat("Concrete", (0.60, 0.59, 0.56), 0.92)
    m_gravel = mat("Gravel", (0.50, 0.48, 0.44), 0.95)
    m_wood = mat("BenchWood", (0.50, 0.36, 0.22), 0.75)
    m_soil = mat("Soil", (0.14, 0.10, 0.07), 0.95)
    m_pot = mat("Terracotta", (0.62, 0.31, 0.19), 0.85)
    m_tray = mat("Tray", (0.13, 0.14, 0.15), 0.7)
    m_leaf = mat("Foliage", (0.18, 0.42, 0.13), 0.72)
    m_leaf2 = mat("FoliageDark", (0.11, 0.29, 0.10), 0.75)
    m_grass = mat("Grass", (0.21, 0.36, 0.14), 0.95)
    m_metal = mat("GalvSteel", (0.66, 0.67, 0.68), 0.42, metal=1.0)

    GW, GL = 3.60, 6.00                 # width (x), length (y)
    KNEE, EAVE, RIDGE = 0.50, 2.05, 3.05
    bays = [-3.0, -2.0, -1.0, 0.0, 1.0, 2.0, 3.0]
    hx = GW * 0.5
    S = 0.055                            # frame member section

    bm = bmesh.new()
    add_box(bm, (60.0, 60.0, 0.4), Matrix.Translation((0.0, 0.0, -0.21)))
    finish(bm, "Ground", m_grass)

    bm = bmesh.new()
    add_box(bm, (GW + 0.5, GL + 0.5, 0.16), Matrix.Translation((0.0, 0.0, -0.06)))
    finish(bm, "Slab", m_conc)

    # brick kneewall, open at the doorway
    bm = bmesh.new()
    for sx in (-1, 1):
        add_box(bm, (0.14, GL, KNEE), Matrix.Translation((sx * hx, 0.0, KNEE * 0.5)))
    add_box(bm, (GW, 0.14, KNEE), Matrix.Translation((0.0, GL * 0.5, KNEE * 0.5)))
    for sx in (-1, 1):
        add_box(bm, (GW * 0.5 - 0.55, 0.14, KNEE),
                Matrix.Translation((sx * (GW * 0.25 + 0.275), -GL * 0.5, KNEE * 0.5)))
    finish(bm, "Kneewall", m_brick)

    # aluminium frame
    bm = bmesh.new()
    for sx in (-1, 1):
        add_strut(bm, (sx * hx, -GL * 0.5, EAVE), (sx * hx, GL * 0.5, EAVE), S, S)
        add_strut(bm, (sx * hx, -GL * 0.5, KNEE + S * 0.5), (sx * hx, GL * 0.5, KNEE + S * 0.5), S, S)
        add_strut(bm, (sx * (hx + 0.10), -GL * 0.5 - 0.1, EAVE - 0.07),
                  (sx * (hx + 0.10), GL * 0.5 + 0.1, EAVE - 0.07), 0.09, 0.10)
        px, pz = sx * hx * 0.5, (EAVE + RIDGE) * 0.5
        add_strut(bm, (px, -GL * 0.5, pz), (px, GL * 0.5, pz), 0.045, 0.045)
    add_strut(bm, (0.0, -GL * 0.5 - 0.14, RIDGE), (0.0, GL * 0.5 + 0.14, RIDGE), 0.07, 0.09)
    for y in bays:
        for sx in (-1, 1):
            add_strut(bm, (sx * hx, y, KNEE), (sx * hx, y, EAVE), S, S)
            eave_pt = Vector((sx * hx, y, EAVE))
            over = eave_pt + Vector((sx, 0.0, -(RIDGE - EAVE) / hx)).normalized() * 0.18
            add_strut(bm, over, (0.0, y, RIDGE), S, 0.075)
    for sy in (-1, 1):
        y = sy * GL * 0.5
        for x in (-0.9, 0.9):
            zt = EAVE + (RIDGE - EAVE) * (1.0 - abs(x) / hx)
            add_strut(bm, (x, y, KNEE), (x, y, zt), S, S)
        add_strut(bm, (-hx, y, EAVE), (0.0, y, RIDGE), S, S)
        add_strut(bm, (hx, y, EAVE), (0.0, y, RIDGE), S, S)
        add_strut(bm, (-hx, y, EAVE), (hx, y, EAVE), S, S)
    for x in (-0.55, 0.55):
        add_strut(bm, (x, -GL * 0.5, 0.0), (x, -GL * 0.5, 2.02), 0.07, 0.07)
    add_strut(bm, (-0.55, -GL * 0.5, 2.02), (0.55, -GL * 0.5, 2.02), 0.07, 0.07)
    finish(bm, "Frame", m_frame)

    # glazing panels
    bg_ = bmesh.new()
    for i in range(len(bays) - 1):
        y0, y1 = bays[i], bays[i + 1]
        yc, yl = (y0 + y1) * 0.5, (y1 - y0) - 0.05
        for sx in (-1, 1):
            add_box(bg_, (0.016, yl, EAVE - KNEE - 0.09),
                    Matrix.Translation((sx * hx, yc, (EAVE + KNEE) * 0.5)))
            a = Vector((sx * hx, yc, EAVE))
            b = Vector((0.0, yc, RIDGE))
            q = (b - a).normalized().to_track_quat('X', 'Z')
            add_box(bg_, ((b - a).length - 0.04, yl, 0.016),
                    Matrix.Translation((a + b) * 0.5 + Vector((0.0, 0.0, 0.035))) @ q.to_matrix().to_4x4())
    for sy in (-1, 1):
        y = sy * GL * 0.5
        for (x0, x1) in ((-hx, -0.9), (0.9, hx)):
            add_box(bg_, (x1 - x0 - 0.06, 0.016, EAVE - KNEE - 0.09),
                    Matrix.Translation(((x0 + x1) * 0.5, y, (EAVE + KNEE) * 0.5)))
        add_prism(bg_, [(-hx + 0.05, EAVE + 0.03), (hx - 0.05, EAVE + 0.03), (0.0, RIDGE - 0.05)],
                  0.016, Matrix.Translation((0.0, y, 0.0)))
        if sy > 0:
            add_box(bg_, (1.72, 0.016, EAVE - KNEE - 0.09),
                    Matrix.Translation((0.0, y, (EAVE + KNEE) * 0.5)))
    finish(bg_, "Glazing", m_glass)

    # door leaf, hinged open
    hinge = Matrix.Translation((-0.53, -GL * 0.5, 0.0)) @ Matrix.Rotation(math.radians(-28.0), 4, 'Z')
    bm = bmesh.new()
    add_box(bm, (1.06, 0.05, 0.07), hinge @ Matrix.Translation((0.53, 0.0, 0.09)))
    add_box(bm, (1.06, 0.05, 0.07), hinge @ Matrix.Translation((0.53, 0.0, 1.95)))
    for ox in (0.035, 0.53, 1.025):
        add_box(bm, (0.07, 0.05, 1.86), hinge @ Matrix.Translation((ox, 0.0, 1.02)))
    add_cyl(bm, 0.018, 0.10, hinge @ Matrix.Translation((0.98, -0.06, 1.02))
            @ Matrix.Rotation(math.radians(90.0), 4, 'X'), 10)
    finish(bm, "DoorLeaf", m_frame, smooth=False)
    bm = bmesh.new()
    add_box(bm, (0.90, 0.014, 1.74), hinge @ Matrix.Translation((0.53, 0.0, 1.02)))
    finish(bm, "DoorGlass", m_glass)

    # roof vent propped open on the +X slope
    slope_ang = math.atan2(RIDGE - EAVE, hx)
    vm = (Matrix.Translation((hx * 0.52, 1.45, EAVE + (RIDGE - EAVE) * 0.48 + 0.16))
          @ Matrix.Rotation(-slope_ang - math.radians(16.0), 4, 'Y'))
    bm = bmesh.new()
    add_box(bm, (0.95, 0.90, 0.02), vm)
    for oy in (-0.45, 0.45):
        add_box(bm, (0.95, 0.05, 0.05), vm @ Matrix.Translation((0.0, oy, 0.03)))
    add_cyl(bm, 0.012, 0.34, Matrix.Translation((hx * 0.62, 1.45, EAVE + 0.30))
            @ Matrix.Rotation(math.radians(20.0), 4, 'Y'), 10)
    finish(bm, "RoofVent", m_frame)

    # gravel path
    bm = bmesh.new()
    add_box(bm, (1.10, GL - 0.3, 0.05), Matrix.Translation((0.0, 0.0, 0.045)))
    finish(bm, "Path", m_gravel)

    # planting tables
    TOP_Z, TW, TL = 0.82, 0.66, 4.80
    bw, bmt = bmesh.new(), bmesh.new()
    table_x = []
    for sx in (-1, 1):
        tx = sx * (hx - 0.10 - TW * 0.5)
        table_x.append(tx)
        for ly in (-TL * 0.5 + 0.18, -0.9, 0.9, TL * 0.5 - 0.18):
            for lx in (-TW * 0.5 + 0.06, TW * 0.5 - 0.06):
                add_box(bmt, (0.045, 0.045, TOP_Z), Matrix.Translation((tx + lx, ly, TOP_Z * 0.5)))
        for lx in (-TW * 0.5 + 0.06, TW * 0.5 - 0.06):
            add_box(bmt, (0.05, TL, 0.05), Matrix.Translation((tx + lx, 0.0, TOP_Z - 0.09)))
            add_box(bmt, (0.04, TL, 0.04), Matrix.Translation((tx + lx, 0.0, 0.28)))
        n = 8
        for i in range(n):
            sxp = -TW * 0.5 + 0.04 + (TW - 0.08) * (i + 0.5) / n
            add_box(bw, (TW / n - 0.022, TL, 0.028), Matrix.Translation((tx + sxp, 0.0, TOP_Z - 0.014)))
        for i in range(3):
            add_box(bw, (0.19, TL - 0.2, 0.024), Matrix.Translation((tx - TW * 0.5 + 0.10 + i * 0.22, 0.0, 0.30)))
        add_box(bw, (0.03, TL, 0.09), Matrix.Translation((tx + sx * (TW * 0.5 - 0.01), 0.0, TOP_Z + 0.03)))
    finish(bw, "TableTops", m_wood)
    finish(bmt, "TableFrames", m_metal)

    # pots, trays, soil and plants
    b_pot, b_soil, b_leaf, b_leaf2, b_tray = (bmesh.new() for _ in range(5))
    for tx in table_x:
        y = -TL * 0.5 + 0.35
        while y < TL * 0.5 - 0.25:
            ox = random.uniform(-0.13, 0.13)
            if random.random() < 0.55:
                r = random.uniform(0.065, 0.095)
                h = r * 1.7
                add_cone(b_pot, r, r * 0.72, h, Matrix.Translation((tx + ox, y, TOP_Z + h * 0.5)), 18)
                add_cyl(b_soil, r * 0.94, 0.02, Matrix.Translation((tx + ox, y, TOP_Z + h - 0.02)), 18)
                for k in range(random.randint(3, 5)):
                    a = random.uniform(0.0, math.tau)
                    rr = random.uniform(0.02, r * 0.9)
                    tgt = b_leaf if random.random() < 0.6 else b_leaf2
                    add_sphere(tgt, random.uniform(0.035, 0.065),
                               Matrix.Translation((tx + ox + math.cos(a) * rr, y + math.sin(a) * rr,
                                                   TOP_Z + h + random.uniform(0.05, 0.16))), 12, 8)
                    add_cyl(b_leaf2, 0.006, 0.14,
                            Matrix.Translation((tx + ox + math.cos(a) * rr * 0.5,
                                                y + math.sin(a) * rr * 0.5, TOP_Z + h + 0.06)), 8)
                y += r * 2.4 + 0.06
            else:
                add_box(b_tray, (0.40, 0.28, 0.07), Matrix.Translation((tx + ox, y, TOP_Z + 0.035)))
                add_box(b_soil, (0.37, 0.25, 0.05), Matrix.Translation((tx + ox, y, TOP_Z + 0.045)))
                for gx in range(4):
                    for gy in range(3):
                        add_cone(b_leaf, 0.018, 0.0, 0.075,
                                 Matrix.Translation((tx + ox - 0.15 + gx * 0.10, y - 0.09 + gy * 0.09,
                                                     TOP_Z + 0.10)), 8)
                y += 0.40
        for i in range(4):
            add_cone(b_pot, 0.10, 0.075, 0.17,
                     Matrix.Translation((tx + random.uniform(-0.1, 0.1), -1.6 + i * 1.05, 0.40)), 16)
    finish(b_pot, "Pots", m_pot, smooth=True)
    finish(b_soil, "Soil", m_soil)
    finish(b_tray, "Trays", m_tray)
    finish(b_leaf, "Foliage", m_leaf, smooth=True)
    finish(b_leaf2, "FoliageDark", m_leaf2, smooth=True)

    # watering can
    bm = bmesh.new()
    add_cyl(bm, 0.10, 0.20, Matrix.Translation((0.30, -2.05, 0.15)), 20)
    add_cone(bm, 0.022, 0.035, 0.34, Matrix.Translation((0.44, -2.28, 0.24))
             @ Matrix.Rotation(math.radians(62.0), 4, 'X') @ Matrix.Rotation(math.radians(20.0), 4, 'Y'), 12)
    add_cyl(bm, 0.012, 0.20, Matrix.Translation((0.30, -1.92, 0.30))
            @ Matrix.Rotation(math.radians(90.0), 4, 'Y'), 10)
    finish(bm, "WateringCan", m_metal, smooth=True)

    # staked climbing plants
    bs, bp = bmesh.new(), bmesh.new()
    for (px, py) in ((-0.62, 2.10), (0.62, 2.35), (-0.62, 1.20)):
        add_cyl(bs, 0.016, 1.30, Matrix.Translation((px, py, 0.70)), 10)
        for k in range(6):
            a = k * 1.9
            add_sphere(bp, 0.10 - k * 0.008,
                       Matrix.Translation((px + math.cos(a) * 0.10, py + math.sin(a) * 0.10,
                                           0.22 + k * 0.19)), 12, 8)
    finish(bs, "Stakes", m_wood)
    finish(bp, "StakedPlants", m_leaf2, smooth=True)

    add_sun("Sun", 5.0, (math.radians(50.0), 0.0, math.radians(-35.0)), (1.0, 0.95, 0.86))
    add_area("SkyFill", 400.0, (0.0, 0.0, 8.0), (0.0, 0.0, 1.0), 10.0, (0.75, 0.85, 1.0))
    add_area("InteriorFill", 90.0, (0.0, -4.0, 1.6), (0.0, 0.5, 1.0), 3.0, (0.95, 1.0, 0.92))
    add_camera((6.4, -7.6, 3.7), (0.0, -0.3, 1.30), lens=36.0)


build()
