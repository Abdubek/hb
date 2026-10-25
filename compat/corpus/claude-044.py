"""claude-044 : A tiled swimming pool with ladder and surrounding deck (Blender 4.5 LTS)."""

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


def tile_material(name, c1, c2, mortar, scale=9.0, row=0.5, width=0.5, offset=0.0,
                  rough=0.16, mortar_size=0.03, bump=0.35):
    """Procedural square-tile material driven by a Brick texture in object space."""
    m = bpy.data.materials.new(name)
    m.use_nodes = True
    nt = m.node_tree
    bsdf = nt.nodes["Principled BSDF"]
    coord = nt.nodes.new("ShaderNodeTexCoord")
    brick = nt.nodes.new("ShaderNodeTexBrick")
    brick.offset = offset
    brick.squash = 1.0
    brick.inputs["Color1"].default_value = (*c1, 1.0)
    brick.inputs["Color2"].default_value = (*c2, 1.0)
    brick.inputs["Mortar"].default_value = (*mortar, 1.0)
    brick.inputs["Scale"].default_value = scale
    brick.inputs["Mortar Size"].default_value = mortar_size
    brick.inputs["Brick Width"].default_value = width
    brick.inputs["Row Height"].default_value = row
    bmp = nt.nodes.new("ShaderNodeBump")
    bmp.inputs["Strength"].default_value = bump
    nt.links.new(coord.outputs["Object"], brick.inputs["Vector"])
    nt.links.new(brick.outputs["Color"], bsdf.inputs["Base Color"])
    nt.links.new(brick.outputs["Fac"], bmp.inputs["Height"])
    nt.links.new(bmp.outputs["Normal"], bsdf.inputs["Normal"])
    bsdf.inputs["Roughness"].default_value = rough
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


def add_prism(bm, profile, depth, matrix=None):
    vs = [bm.verts.new((x, -depth * 0.5, z)) for (x, z) in profile]
    f = bm.faces.new(vs)
    res = bmesh.ops.extrude_face_region(bm, geom=[f])
    nv = [e for e in res["geom"] if isinstance(e, bmesh.types.BMVert)]
    bmesh.ops.translate(bm, vec=(0.0, depth, 0.0), verts=nv)
    if matrix is not None:
        bmesh.ops.transform(bm, matrix=matrix, verts=vs + nv)


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


def add_camera(loc, target, lens=38.0):
    c = bpy.data.cameras.new("Camera")
    c.lens = lens
    ob = bpy.data.objects.new("Camera", c)
    bpy.context.scene.collection.objects.link(ob)
    ob.location = loc
    ob.rotation_euler = (Vector(target) - Vector(loc)).to_track_quat('-Z', 'Y').to_euler()
    bpy.context.scene.camera = ob
    return ob


def add_sun(name, energy, rot, color=(1.0, 0.95, 0.86), angle=0.012):
    d = bpy.data.lights.new(name, 'SUN')
    d.energy, d.color, d.angle = energy, color, angle
    ob = bpy.data.objects.new(name, d)
    bpy.context.scene.collection.objects.link(ob)
    ob.rotation_euler = rot
    return ob


def add_area(name, energy, loc, target, size=6.0, color=(1.0, 1.0, 1.0)):
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
    random.seed(44)
    scene = bpy.context.scene
    scene.render.resolution_x, scene.render.resolution_y = 1600, 1000

    world = bpy.data.worlds.new("World")
    scene.world = world
    world.use_nodes = True
    bg = world.node_tree.nodes["Background"]
    bg.inputs[0].default_value = (0.38, 0.55, 0.84, 1.0)
    bg.inputs[1].default_value = 1.2

    m_tile = tile_material("PoolTile", (0.30, 0.66, 0.76), (0.24, 0.58, 0.70), (0.86, 0.90, 0.90), 9.0)
    m_band = tile_material("WaterlineTile", (0.05, 0.24, 0.42), (0.07, 0.30, 0.50), (0.80, 0.86, 0.88), 14.0)
    m_deck = tile_material("DeckPaving", (0.74, 0.71, 0.65), (0.70, 0.67, 0.61), (0.56, 0.54, 0.50),
                           0.9, rough=0.7, bump=0.2)
    m_coping = mat("Coping", (0.86, 0.84, 0.79), 0.55)
    m_water = mat("PoolWater", (0.22, 0.60, 0.72), 0.02, trans=1.0, alpha=0.42, ior=1.333)
    m_steel = mat("Stainless", (0.82, 0.83, 0.84), 0.20, metal=1.0)
    m_wood = mat("Teak", (0.55, 0.38, 0.22), 0.65)
    m_fabric = mat("Cushion", (0.90, 0.89, 0.85), 0.85)
    m_canvas = mat("Canvas", (0.88, 0.44, 0.31), 0.9)
    m_grass = mat("Lawn", (0.22, 0.38, 0.15), 0.95)
    m_leaf = mat("Shrub", (0.14, 0.32, 0.12), 0.75)
    m_pot = mat("Planter", (0.72, 0.70, 0.66), 0.8)
    m_lamp = mat("PoolLamp", (0.85, 0.95, 1.0), 0.2, emit=(0.65, 0.90, 1.0), es=4.0)

    PX, PY, WT = 4.00, 2.00, 0.25          # inner half extents, wall thickness
    D_SH, D_DP = 1.05, 2.10                # shallow / deep depths
    SA, SB = -1.0, 3.0                     # slope run
    OX, OY = PX + WT, PY + WT
    DX, DY = 7.4, 5.2                      # deck half extents

    bm = bmesh.new()
    add_box(bm, (60.0, 60.0, 0.6), Matrix.Translation((0.0, 0.0, -0.55)))
    finish(bm, "Lawn", m_grass)

    # deck slab as a frame around the pool opening
    bm = bmesh.new()
    for (cx, cy, sx, sy) in ((0.0, (OY + DY) * 0.5, OX * 2, DY - OY),
                             (0.0, -(OY + DY) * 0.5, OX * 2, DY - OY),
                             ((OX + DX) * 0.5, 0.0, DX - OX, DY * 2),
                             (-(OX + DX) * 0.5, 0.0, DX - OX, DY * 2)):
        add_box(bm, (sx, sy, 0.30), Matrix.Translation((cx, cy, -0.15)))
    finish(bm, "Deck", m_deck)

    # tiled shell: walls, sloping floor, entry steps
    bm = bmesh.new()
    for sy in (-1, 1):
        add_box(bm, (OX * 2, WT, 2.55), Matrix.Translation((0.0, sy * (PY + WT * 0.5), -1.275)))
    for sx in (-1, 1):
        add_box(bm, (WT, PY * 2, 2.55), Matrix.Translation((sx * (PX + WT * 0.5), 0.0, -1.275)))
    add_prism(bm, [(-OX, -D_SH - 0.30), (OX, -D_DP - 0.30), (OX, -D_DP),
                   (SB, -D_DP), (SA, -D_SH), (-OX, -D_SH)], OY * 2)
    for i in range(3):
        add_box(bm, (0.42, PY * 2 - 0.9, 0.30),
                Matrix.Translation((-PX + 0.21 + i * 0.42, 0.0, -0.15 - i * 0.30)))
    finish(bm, "PoolShell", m_tile)

    # waterline tile band
    bm = bmesh.new()
    for sy in (-1, 1):
        add_box(bm, (PX * 2, 0.02, 0.22), Matrix.Translation((0.0, sy * (PY - 0.012), -0.19)))
    for sx in (-1, 1):
        add_box(bm, (0.02, PY * 2, 0.22), Matrix.Translation((sx * (PX - 0.012), 0.0, -0.19)))
    finish(bm, "WaterlineBand", m_band)

    # coping ring
    bm = bmesh.new()
    CW = 0.42
    for sy in (-1, 1):
        add_box(bm, (PX * 2 + CW * 2, CW, 0.07), Matrix.Translation((0.0, sy * (PY + CW * 0.5 - 0.04), 0.025)))
    for sx in (-1, 1):
        add_box(bm, (CW, PY * 2, 0.07), Matrix.Translation((sx * (PX + CW * 0.5 - 0.04), 0.0, 0.025)))
    finish(bm, "Coping", m_coping)

    # water surface
    bm = bmesh.new()
    add_box(bm, (PX * 2 - 0.02, PY * 2 - 0.02, 0.02), Matrix.Translation((0.0, 0.0, -0.13)))
    finish(bm, "WaterSurface", m_water)

    # ladder with hooked rails and rungs
    LX0, LX1 = 2.62, 3.26
    path = [(2.62, -0.32), (2.62, 0.44), (2.60, 0.74), (2.50, 0.94), (2.32, 1.02),
            (2.12, 0.96), (2.00, 0.78), (1.96, 0.42), (1.96, -0.10), (1.94, -0.62), (1.94, -1.22)]
    bm = bmesh.new()
    for lx in (LX0, LX1):
        add_tube(bm, [(lx, y, z) for (y, z) in path], 0.023, 12)
    for rz in (-0.16, -0.58, -1.00):
        add_cyl(bm, 0.020, LX1 - LX0, Matrix.Translation(((LX0 + LX1) * 0.5, 1.945, rz))
                @ Matrix.Rotation(math.radians(90.0), 4, 'Y'), 14)
    for lx in (LX0, LX1):
        add_cyl(bm, 0.055, 0.02, Matrix.Translation((lx, 2.62, 0.075)), 18)
    finish(bm, "Ladder", m_steel, smooth=True)

    # skimmer and main drain
    bm = bmesh.new()
    add_box(bm, (0.34, 0.03, 0.16), Matrix.Translation((-1.6, PY - 0.02, -0.16)))
    add_cyl(bm, 0.14, 0.02, Matrix.Translation((3.2, 0.0, -D_DP + 0.01)), 20)
    finish(bm, "Fittings", m_steel, smooth=True)

    bm = bmesh.new()
    for ly in (-1.0, 1.0):
        add_cyl(bm, 0.11, 0.03, Matrix.Translation((PX - 0.02, ly, -0.75))
                @ Matrix.Rotation(math.radians(90.0), 4, 'Y'), 20)
    finish(bm, "PoolLights", m_lamp, smooth=True)

    # loungers and side table
    bw, bf = bmesh.new(), bmesh.new()
    for (cx, cy, rz) in ((-2.2, -3.65, math.radians(4.0)), (0.6, -3.65, math.radians(-3.0))):
        base = Matrix.Translation((cx, cy, 0.0)) @ Matrix.Rotation(rz, 4, 'Z')
        for (lx, ly) in ((-0.30, -0.86), (0.30, -0.86), (-0.30, 0.72), (0.30, 0.72)):
            add_box(bw, (0.05, 0.05, 0.34), base @ Matrix.Translation((lx, ly, 0.17)))
        for lx in (-0.30, 0.30):
            add_box(bw, (0.055, 1.75, 0.055), base @ Matrix.Translation((lx, 0.0, 0.36)))
        for i in range(9):
            add_box(bw, (0.66, 0.10, 0.025), base @ Matrix.Translation((0.0, -0.80 + i * 0.17, 0.395)))
        back = base @ Matrix.Translation((0.0, 0.72, 0.40)) @ Matrix.Rotation(math.radians(-38.0), 4, 'X')
        for i in range(5):
            add_box(bw, (0.66, 0.10, 0.025), back @ Matrix.Translation((0.0, 0.10 + i * 0.155, 0.02)))
        add_box(bf, (0.62, 1.55, 0.055), base @ Matrix.Translation((0.0, -0.10, 0.435)))
        add_box(bf, (0.62, 0.72, 0.055), back @ Matrix.Translation((0.0, 0.38, 0.055)))
    add_box(bw, (0.42, 0.42, 0.04), Matrix.Translation((-0.85, -3.62, 0.42)))
    for (lx, ly) in ((-0.16, -0.16), (0.16, -0.16), (-0.16, 0.16), (0.16, 0.16)):
        add_box(bw, (0.04, 0.04, 0.40), Matrix.Translation((-0.85 + lx, -3.62 + ly, 0.20)))
    finish(bw, "LoungerFrames", m_wood)
    finish(bf, "LoungerCushions", m_fabric)

    # parasol
    bm = bmesh.new()
    add_cyl(bm, 0.032, 2.30, Matrix.Translation((2.0, -3.7, 1.15)), 16)
    finish(bm, "ParasolPole", m_steel, smooth=True)
    bm = bmesh.new()
    add_cone(bm, 1.30, 0.06, 0.42, Matrix.Translation((2.0, -3.7, 2.28)), 12)
    finish(bm, "ParasolCanopy", m_canvas)
    bm = bmesh.new()
    add_cyl(bm, 0.30, 0.10, Matrix.Translation((2.0, -3.7, 0.05)), 24)
    finish(bm, "ParasolBase", m_coping, smooth=True)

    # planters along the far deck edge
    bp, bl = bmesh.new(), bmesh.new()
    for px in (-5.6, -2.8, 2.8, 5.6):
        add_box(bp, (0.80, 0.80, 0.60), Matrix.Translation((px, 4.2, 0.30)))
        for k in range(6):
            r = random.uniform(0.16, 0.28)
            add_sphere(bl, r, Matrix.Translation((px + random.uniform(-0.25, 0.25),
                                                  4.2 + random.uniform(-0.25, 0.25),
                                                  0.62 + r * 0.7 + random.uniform(0.0, 0.28))), 14, 9)
    finish(bp, "Planters", m_pot)
    finish(bl, "PlanterShrubs", m_leaf, smooth=True)

    add_sun("Sun", 5.5, (math.radians(58.0), 0.0, math.radians(-42.0)))
    add_area("SkyFill", 700.0, (0.0, 0.0, 12.0), (0.0, 0.0, 0.0), 18.0, (0.68, 0.80, 1.0))
    add_area("Bounce", 150.0, (-8.0, -6.0, 3.0), (0.0, 0.0, -0.4), 8.0, (0.85, 0.93, 1.0))
    add_camera((10.5, -10.5, 6.4), (-0.3, 0.0, -0.5), lens=38.0)


build()
