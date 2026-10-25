"""claude-045 : A staircase with landing and handrails (Blender 4.5 LTS).

Half-turn (U-shaped) stair: nine risers up to a landing, then nine more back
the other way to an upper floor, with stringers, newels, balusters and a
continuous tubular handrail on both the outer and the well side.
"""

import bpy, bmesh, math
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


def add_cyl(bm, r, depth, matrix=None, seg=16):
    v = bmesh.ops.create_cone(bm, cap_ends=True, cap_tris=False, segments=seg,
                              radius1=r, radius2=r, depth=depth)["verts"]
    if matrix is not None:
        bmesh.ops.transform(bm, matrix=matrix, verts=v)
    return v


def add_sphere(bm, r, matrix=None, u=16, v=10):
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


def add_tube(bm, points, radius, seg=12, caps=True):
    pts = [Vector(p) for p in points]
    n = len(pts)
    rings = []
    for i, p in enumerate(pts):
        if i == 0:
            t = pts[1] - pts[0]
        elif i == n - 1:
            t = pts[-1] - pts[-2]
        else:
            t = pts[i + 1] - pts[i - 1]
        t.normalize()
        up = Vector((0.0, 0.0, 1.0)) if abs(t.z) < 0.92 else Vector((1.0, 0.0, 0.0))
        ax = t.cross(up).normalized()
        ay = t.cross(ax).normalized()
        rings.append([bm.verts.new(p + (ax * math.cos(math.tau * k / seg)
                                        + ay * math.sin(math.tau * k / seg)) * radius)
                      for k in range(seg)])
    for i in range(n - 1):
        for k in range(seg):
            k2 = (k + 1) % seg
            bm.faces.new((rings[i][k], rings[i][k2], rings[i + 1][k2], rings[i + 1][k]))
    if caps:
        bm.faces.new(rings[0][::-1])
        bm.faces.new(rings[-1])


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


def add_camera(loc, target, lens=35.0):
    c = bpy.data.cameras.new("Camera")
    c.lens = lens
    ob = bpy.data.objects.new("Camera", c)
    bpy.context.scene.collection.objects.link(ob)
    ob.location = loc
    ob.rotation_euler = (Vector(target) - Vector(loc)).to_track_quat('-Z', 'Y').to_euler()
    bpy.context.scene.camera = ob
    return ob


def add_area(name, energy, loc, target, size=3.0, color=(1.0, 1.0, 1.0)):
    d = bpy.data.lights.new(name, 'AREA')
    d.energy, d.size, d.color = energy, size, color
    ob = bpy.data.objects.new(name, d)
    bpy.context.scene.collection.objects.link(ob)
    ob.location = loc
    ob.rotation_euler = (Vector(target) - Vector(loc)).to_track_quat('-Z', 'Y').to_euler()
    return ob


def add_sun(name, energy, rot, color=(1.0, 0.95, 0.88), angle=0.02):
    d = bpy.data.lights.new(name, 'SUN')
    d.energy, d.color, d.angle = energy, color, angle
    ob = bpy.data.objects.new(name, d)
    bpy.context.scene.collection.objects.link(ob)
    ob.rotation_euler = rot
    return ob


# ----------------------------------------------------------------- build
def build():
    reset()
    scene = bpy.context.scene
    scene.render.resolution_x, scene.render.resolution_y = 1400, 1200

    world = bpy.data.worlds.new("World")
    scene.world = world
    world.use_nodes = True
    bg = world.node_tree.nodes["Background"]
    bg.inputs[0].default_value = (0.24, 0.26, 0.30, 1.0)
    bg.inputs[1].default_value = 0.7

    m_oak = mat("OakTread", (0.52, 0.36, 0.20), 0.45)
    m_paint = mat("WhitePaint", (0.90, 0.89, 0.86), 0.42)
    m_rail = mat("BronzeRail", (0.28, 0.20, 0.14), 0.30, metal=1.0)
    m_conc = mat("Concrete", (0.60, 0.59, 0.57), 0.86)
    m_floor = mat("FloorBoards", (0.44, 0.31, 0.19), 0.5)
    m_wall = mat("Plaster", (0.80, 0.78, 0.75), 0.85)
    m_glow = mat("Downlight", (1.0, 0.92, 0.80), 0.3, emit=(1.0, 0.90, 0.75), es=12.0)

    RISE, RUN, WID, GAP = 0.18, 0.28, 1.10, 0.10
    NOSE = 0.03
    XA = -(WID + GAP * 0.5)                    # flight A: x from XA to XA+WID
    XB = GAP * 0.5                             # flight B: x from XB to XB+WID
    AC, BC = XA + WID * 0.5, XB + WID * 0.5    # flight centre lines
    LAND_Y0 = 9 * RUN                          # 2.52
    LAND_Y1 = LAND_Y0 + WID                    # 3.62
    LAND_Z = 9 * RISE                          # 1.62
    TOP_Z = 18 * RISE                          # 3.24
    SLOPE = RISE / RUN

    def railz_a(y):
        return SLOPE * y + RISE + 0.90

    def railz_b(y):
        return railz_a(LAND_Y0) + SLOPE * (LAND_Y0 - y)

    RZ_LAND = railz_a(LAND_Y0)                 # 2.70, kept level across the landing

    # ---- ground floor, upper floor, back wall
    bm = bmesh.new()
    add_box(bm, (9.0, 11.0, 0.30), Matrix.Translation((0.0, 1.0, -0.15)))
    finish(bm, "GroundFloor", m_conc)

    bm = bmesh.new()
    add_box(bm, (5.4, 2.8, 0.26), Matrix.Translation((0.0, -1.4, TOP_Z - 0.13)))
    finish(bm, "UpperFloor", m_floor)

    bm = bmesh.new()
    add_box(bm, (6.4, 0.16, 4.8), Matrix.Translation((0.0, LAND_Y1 + 0.30, 2.40)))
    add_box(bm, (0.16, 6.0, 4.8), Matrix.Translation((-3.1, 0.80, 2.40)))
    finish(bm, "Walls", m_wall)

    # ---- landing slab and its posts
    bm = bmesh.new()
    add_box(bm, (WID * 2 + GAP + 0.10, WID, 0.16),
            Matrix.Translation((0.0, (LAND_Y0 + LAND_Y1) * 0.5, LAND_Z - 0.08)))
    for px in (-1.06, 1.06):
        for py in (LAND_Y0 + 0.12, LAND_Y1 - 0.12):
            add_box(bm, (0.10, 0.10, LAND_Z - 0.16), Matrix.Translation((px, py, (LAND_Z - 0.16) * 0.5)))
    finish(bm, "Landing", m_conc)

    # ---- treads and risers
    b_tread, b_riser = bmesh.new(), bmesh.new()
    for i in range(1, 10):                                     # flight A, ascending +Y
        z = i * RISE
        y0 = (i - 1) * RUN
        add_box(b_tread, (WID, RUN + NOSE, 0.05), Matrix.Translation((AC, y0 + (RUN + NOSE) * 0.5 - NOSE, z - 0.025)))
        add_box(b_riser, (WID, 0.03, RISE - 0.05), Matrix.Translation((AC, y0 + RUN, z - RISE + (RISE - 0.05) * 0.5)))
    for i in range(10, 19):                                    # flight B, ascending -Y
        z = i * RISE
        y1 = LAND_Y0 - (i - 10) * RUN
        add_box(b_tread, (WID, RUN + NOSE, 0.05), Matrix.Translation((BC, y1 - (RUN + NOSE) * 0.5 + NOSE, z - 0.025)))
        add_box(b_riser, (WID, 0.03, RISE - 0.05), Matrix.Translation((BC, y1 - RUN, z - RISE + (RISE - 0.05) * 0.5)))
    finish(b_tread, "Treads", m_oak)
    finish(b_riser, "Risers", m_paint)

    # ---- stringers, offset down the slope normal from the nosing line
    th = math.atan2(RISE, RUN)
    off = Vector((0.0, math.sin(th), -math.cos(th))) * 0.17
    bm = bmesh.new()
    for x in (XA + 0.04, XA + WID - 0.04):
        p0 = Vector((x, -0.04, RISE)) + off
        p1 = Vector((x, LAND_Y0 + 0.04, RISE + SLOPE * (LAND_Y0 + 0.04))) + off
        add_strut(bm, p0, p1, 0.06, 0.32)
    for x in (XB + 0.04, XB + WID - 0.04):
        p0 = Vector((x, LAND_Y0 + 0.04, LAND_Z + RISE)) + Vector((0.0, -off.y, off.z))
        p1 = Vector((x, -0.04, TOP_Z + RISE * 0.2)) + Vector((0.0, -off.y, off.z))
        add_strut(bm, p0, p1, 0.06, 0.32)
    finish(bm, "Stringers", m_paint)

    # ---- handrails: one continuous outer rail, one around the stair well
    outer = [(XA + 0.03, -0.30, railz_a(-0.30)),
             (XA + 0.03, LAND_Y0, RZ_LAND),
             (XA + 0.03, LAND_Y1 - 0.06, RZ_LAND),
             (XA + 0.10, LAND_Y1 - 0.02, RZ_LAND),
             (XB + WID - 0.10, LAND_Y1 - 0.02, RZ_LAND),
             (XB + WID - 0.03, LAND_Y1 - 0.06, RZ_LAND),
             (XB + WID - 0.03, LAND_Y0, RZ_LAND),
             (XB + WID - 0.03, 0.0, railz_b(0.0)),
             (XB + WID - 0.03, -0.30, railz_b(0.0))]
    inner = [(XA + WID - 0.03, -0.30, railz_a(-0.30)),
             (XA + WID - 0.03, LAND_Y0 - 0.06, RZ_LAND),
             (XA + WID + 0.02, LAND_Y0 - 0.02, RZ_LAND),
             (XB + 0.03, LAND_Y0 - 0.02, RZ_LAND),
             (XB + 0.03, LAND_Y0 - 0.06, RZ_LAND),
             (XB + 0.03, 0.0, railz_b(0.0)),
             (XB + 0.03, -0.30, railz_b(0.0))]
    upper = [(-2.55, -0.06, TOP_Z + 1.00), (XA + WID - 0.03, -0.06, TOP_Z + 1.00)]

    bm = bmesh.new()
    for path in (outer, inner, upper):
        add_tube(bm, path, 0.028, 14)
    finish(bm, "Handrails", m_rail, smooth=True)

    # ---- balusters and newel posts
    bm = bmesh.new()

    def baluster(x, y, z0, z1):
        if z1 - z0 < 0.05:
            return
        add_box(bm, (0.035, 0.035, z1 - z0), Matrix.Translation((x, y, (z0 + z1) * 0.5)))

    for i in range(1, 10):                                     # flight A
        for frac in (0.28, 0.72):
            y = (i - 1) * RUN + RUN * frac
            baluster(XA + 0.03, y, i * RISE, railz_a(y) - 0.03)
            baluster(XA + WID - 0.03, y, i * RISE, railz_a(y) - 0.03)
    for i in range(10, 19):                                    # flight B
        for frac in (0.28, 0.72):
            y = LAND_Y0 - (i - 10) * RUN - RUN * frac
            baluster(XB + WID - 0.03, y, i * RISE, railz_b(y) - 0.03)
            baluster(XB + 0.03, y, i * RISE, railz_b(y) - 0.03)
    n = 5                                                      # landing sides
    for k in range(1, n):
        y = LAND_Y0 + (LAND_Y1 - LAND_Y0) * k / n
        baluster(XA + 0.03, y, LAND_Z, RZ_LAND - 0.03)
        baluster(XB + WID - 0.03, y, LAND_Z, RZ_LAND - 0.03)
    n = 10                                                     # landing far edge
    for k in range(1, n):
        x = XA + 0.03 + (XB + WID - 0.06 - XA) * k / n
        baluster(x, LAND_Y1 - 0.02, LAND_Z, RZ_LAND - 0.03)
    n = 11                                                     # upper floor guard
    for k in range(1, n):
        x = -2.55 + (XA + WID - 0.03 + 2.55) * k / n
        baluster(x, -0.06, TOP_Z, TOP_Z + 0.97)
    for (nx, ny, nz0, nz1) in ((XA + 0.03, -0.30, 0.0, railz_a(-0.30) + 0.06),
                               (XA + WID - 0.03, -0.30, 0.0, railz_a(-0.30) + 0.06),
                               (XB + WID - 0.03, -0.30, TOP_Z, TOP_Z + 1.06),
                               (XB + 0.03, -0.30, TOP_Z, TOP_Z + 1.06),
                               (-2.55, -0.06, TOP_Z, TOP_Z + 1.06)):
        add_box(bm, (0.09, 0.09, nz1 - nz0), Matrix.Translation((nx, ny, (nz0 + nz1) * 0.5)))
    finish(bm, "Balusters", m_paint)

    bm = bmesh.new()
    for (nx, ny) in ((XA + 0.03, -0.30), (XA + WID - 0.03, -0.30)):
        add_sphere(bm, 0.055, Matrix.Translation((nx, ny, railz_a(-0.30) + 0.10)))
    finish(bm, "NewelCaps", m_rail, smooth=True)

    # ---- ceiling downlights over the stair
    bm = bmesh.new()
    for (lx, ly) in ((-0.9, 1.2), (0.9, 3.0), (-0.9, 3.4)):
        add_cyl(bm, 0.09, 0.03, Matrix.Translation((lx, ly, 4.55)), 20)
    finish(bm, "Downlights", m_glow, smooth=True)

    add_area("Key", 260.0, (-2.2, -2.6, 4.2), (0.0, 1.4, 1.6), 3.5, (1.0, 0.94, 0.86))
    add_area("Fill", 90.0, (3.4, -1.5, 2.4), (0.0, 1.6, 1.8), 3.0, (0.80, 0.86, 1.0))
    add_area("LandingLight", 120.0, (0.0, 2.9, 4.3), (0.0, 2.9, 1.6), 1.6, (1.0, 0.92, 0.80))
    add_sun("Daylight", 1.6, (math.radians(62.0), 0.0, math.radians(-120.0)), (0.85, 0.90, 1.0))
    add_camera((4.6, -4.4, 3.1), (0.0, 1.55, 1.75), lens=32.0)


build()
