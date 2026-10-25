"""claude-043 : A public drinking fountain with two basins (Blender 4.5 LTS)."""

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


def paving_material(name, c1, c2, mortar, scale=1.1, rough=0.85):
    m = bpy.data.materials.new(name)
    m.use_nodes = True
    nt = m.node_tree
    bsdf = nt.nodes["Principled BSDF"]
    coord = nt.nodes.new("ShaderNodeTexCoord")
    brick = nt.nodes.new("ShaderNodeTexBrick")
    brick.offset = 0.5
    brick.squash = 1.0
    brick.inputs["Color1"].default_value = (*c1, 1.0)
    brick.inputs["Color2"].default_value = (*c2, 1.0)
    brick.inputs["Mortar"].default_value = (*mortar, 1.0)
    brick.inputs["Scale"].default_value = scale
    brick.inputs["Mortar Size"].default_value = 0.015
    brick.inputs["Brick Width"].default_value = 0.5
    brick.inputs["Row Height"].default_value = 0.25
    bump = nt.nodes.new("ShaderNodeBump")
    bump.inputs["Strength"].default_value = 0.25
    nt.links.new(coord.outputs["Object"], brick.inputs["Vector"])
    nt.links.new(brick.outputs["Color"], bsdf.inputs["Base Color"])
    nt.links.new(brick.outputs["Fac"], bump.inputs["Height"])
    nt.links.new(bump.outputs["Normal"], bsdf.inputs["Normal"])
    bsdf.inputs["Roughness"].default_value = rough
    return m


def add_box(bm, size, matrix=None):
    v = bmesh.ops.create_cube(bm, size=1.0)["verts"]
    bmesh.ops.scale(bm, vec=Vector(size), verts=v)
    if matrix is not None:
        bmesh.ops.transform(bm, matrix=matrix, verts=v)
    return v


def add_cone(bm, r1, r2, depth, matrix=None, seg=24):
    v = bmesh.ops.create_cone(bm, cap_ends=True, cap_tris=False, segments=seg,
                              radius1=r1, radius2=r2, depth=depth)["verts"]
    if matrix is not None:
        bmesh.ops.transform(bm, matrix=matrix, verts=v)
    return v


def add_cyl(bm, r, depth, matrix=None, seg=24):
    return add_cone(bm, r, r, depth, matrix, seg)


def add_sphere(bm, r, matrix=None, u=16, v=10):
    vs = bmesh.ops.create_uvsphere(bm, u_segments=u, v_segments=v, radius=r)["verts"]
    if matrix is not None:
        bmesh.ops.transform(bm, matrix=matrix, verts=vs)
    return vs


def add_tube(bm, points, radius, seg=10, caps=True):
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


def lathe(name, profile, material, seg=48, loc=(0.0, 0.0, 0.0), solidify=0.0, smooth=True):
    bm = bmesh.new()
    verts = [bm.verts.new((r, 0.0, z)) for (r, z) in profile]
    for a, b in zip(verts[:-1], verts[1:]):
        bm.edges.new((a, b))
    geom = list(verts) + list(bm.edges)
    bmesh.ops.spin(bm, geom=geom, cent=(0.0, 0.0, 0.0), axis=(0.0, 0.0, 1.0),
                   dvec=(0.0, 0.0, 0.0), angle=math.tau, steps=seg, use_merge=False)
    bmesh.ops.remove_doubles(bm, verts=list(bm.verts), dist=1e-5)
    ob = finish(bm, name, material, smooth=smooth, loc=loc)
    if solidify > 0.0:
        md = ob.modifiers.new("Solidify", 'SOLIDIFY')
        md.thickness = solidify
        md.offset = 0.0
    return ob


def add_camera(loc, target, lens=55.0):
    c = bpy.data.cameras.new("Camera")
    c.lens = lens
    ob = bpy.data.objects.new("Camera", c)
    bpy.context.scene.collection.objects.link(ob)
    ob.location = loc
    ob.rotation_euler = (Vector(target) - Vector(loc)).to_track_quat('-Z', 'Y').to_euler()
    bpy.context.scene.camera = ob
    return ob


def add_sun(name, energy, rot, color=(1.0, 0.95, 0.87), angle=0.015):
    d = bpy.data.lights.new(name, 'SUN')
    d.energy, d.color, d.angle = energy, color, angle
    ob = bpy.data.objects.new(name, d)
    bpy.context.scene.collection.objects.link(ob)
    ob.rotation_euler = rot
    return ob


def add_area(name, energy, loc, target, size=4.0, color=(1.0, 1.0, 1.0)):
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
    random.seed(43)
    scene = bpy.context.scene
    scene.render.resolution_x, scene.render.resolution_y = 1400, 1400

    world = bpy.data.worlds.new("World")
    scene.world = world
    world.use_nodes = True
    bg = world.node_tree.nodes["Background"]
    bg.inputs[0].default_value = (0.50, 0.63, 0.82, 1.0)
    bg.inputs[1].default_value = 1.0

    m_pave = paving_material("Paving", (0.56, 0.54, 0.50), (0.49, 0.47, 0.44), (0.36, 0.35, 0.33))
    m_conc = mat("CastStone", (0.55, 0.54, 0.51), 0.85)
    m_conc_d = mat("CastStoneDark", (0.42, 0.41, 0.39), 0.88)
    m_steel = mat("Stainless", (0.80, 0.81, 0.82), 0.22, metal=1.0)
    m_steel_d = mat("StainlessDark", (0.42, 0.43, 0.45), 0.35, metal=1.0)
    m_water = mat("Water", (0.62, 0.83, 0.90), 0.03, trans=1.0, alpha=0.35, ior=1.33)
    m_wet = mat("WetPool", (0.30, 0.48, 0.55), 0.08)
    m_sign = mat("SignText", (0.10, 0.28, 0.45), 0.4)
    m_plate = mat("SignPlate", (0.90, 0.90, 0.88), 0.35)
    m_soil = mat("Soil", (0.15, 0.11, 0.08), 0.95)
    m_leaf = mat("Shrub", (0.16, 0.33, 0.12), 0.8)
    m_curb = mat("Curb", (0.62, 0.60, 0.57), 0.9)

    # plaza and kerb
    bm = bmesh.new()
    add_box(bm, (30.0, 30.0, 0.30), Matrix.Translation((0.0, 0.0, -0.15)))
    finish(bm, "Plaza", m_pave)
    bm = bmesh.new()
    add_box(bm, (10.0, 0.28, 0.30), Matrix.Translation((0.0, 3.1, 0.02)))
    finish(bm, "Kerb", m_curb)

    PW, PD = 0.92, 0.34
    PH_HIGH, PH_LOW = 1.06, 0.78            # adult and child basin rim heights

    # pedestal
    bm = bmesh.new()
    add_box(bm, (PW + 0.16, PD + 0.16, 0.10), Matrix.Translation((0.0, 0.0, 0.05)))
    add_box(bm, (PW, PD, PH_HIGH - 0.10), Matrix.Translation((0.0, 0.0, (PH_HIGH - 0.10) * 0.5 + 0.10)))
    add_box(bm, (PW - 0.06, PD + 0.03, 0.03), Matrix.Translation((0.0, 0.0, 0.16)))
    finish(bm, "Pedestal", m_conc)

    bm = bmesh.new()
    add_box(bm, (PW + 0.05, PD + 0.05, 0.05), Matrix.Translation((0.0, 0.0, PH_HIGH - 0.015)))
    add_box(bm, (PW * 0.62, PD + 0.06, 0.05), Matrix.Translation((0.24, 0.0, PH_LOW - 0.015)))
    finish(bm, "PedestalCap", m_conc_d)

    # the two basins, lathed and solidified
    bowl = [(0.020, -0.130), (0.055, -0.126), (0.100, -0.110), (0.145, -0.083),
            (0.185, -0.048), (0.215, -0.018), (0.232, 0.000), (0.238, -0.010),
            (0.234, -0.040), (0.222, -0.062)]
    basins = [(-0.245, PH_HIGH, 1.00), (0.265, PH_LOW, 0.86)]
    for i, (bx, bz, s) in enumerate(basins):
        ob = lathe("Basin_%d" % i, [(r * s, z * s) for (r, z) in bowl], m_steel,
                   seg=56, loc=(bx, -0.20, bz), solidify=0.012)
        ob.scale = (1.0, 1.15, 1.0)

    bm = bmesh.new()
    for (bx, bz, s) in basins:
        add_box(bm, (0.10, 0.24, 0.055), Matrix.Translation((bx, -0.10, bz - 0.10)))
        add_box(bm, (0.20, 0.05, 0.12), Matrix.Translation((bx, 0.0, bz - 0.10)))
    finish(bm, "BasinArms", m_steel_d)

    # bubblers, guards, push pads, drains
    b_b, b_d, b_p = bmesh.new(), bmesh.new(), bmesh.new()
    for (bx, bz, s) in basins:
        by = -0.20 + 0.135 * s * 1.15
        add_cyl(b_b, 0.020, 0.075, Matrix.Translation((bx, by, bz + 0.020)), 18)
        add_cone(b_b, 0.030, 0.020, 0.030, Matrix.Translation((bx, by, bz + 0.070)), 18)
        add_cyl(b_b, 0.008, 0.030, Matrix.Translation((bx, by - 0.006, bz + 0.090))
                @ Matrix.Rotation(math.radians(-32.0), 4, 'X'), 10)
        add_tube(b_b, [(bx - 0.045, by + 0.010, bz + 0.030), (bx - 0.042, by - 0.006, bz + 0.086),
                       (bx, by - 0.020, bz + 0.104), (bx + 0.042, by - 0.006, bz + 0.086),
                       (bx + 0.045, by + 0.010, bz + 0.030)], 0.006, 8)
        add_cyl(b_d, 0.035 * s, 0.010, Matrix.Translation((bx, -0.20, bz - 0.128 * s)), 18)
        add_box(b_p, (0.075, 0.03, 0.045), Matrix.Translation((bx + 0.19, -PD * 0.5 - 0.012, bz - 0.055)))
    finish(b_b, "Bubblers", m_steel, smooth=True)
    finish(b_d, "Drains", m_steel_d, smooth=True)
    finish(b_p, "PushPads", m_steel_d)

    # water arcs and standing water
    bm = bmesh.new()
    for (bx, bz, s) in basins:
        by = -0.20 + 0.135 * s * 1.15
        pts = []
        for k in range(13):
            t = k / 12.0
            pts.append((bx, by - 0.185 * s * t, bz + 0.105 * s + 0.085 * t - 0.30 * t * t))
        add_tube(bm, pts, 0.0075, 8)
    finish(bm, "WaterJets", m_water, smooth=True)

    bm = bmesh.new()
    for (bx, bz, s) in basins:
        add_cyl(bm, 0.085 * s, 0.006, Matrix.Translation((bx, -0.20, bz - 0.118 * s)), 24)
    finish(bm, "StandingWater", m_wet, smooth=True)

    # sign plate and ground drain
    bm = bmesh.new()
    add_box(bm, (0.30, 0.012, 0.20), Matrix.Translation((-0.245, PD * 0.5 + 0.008, 0.86)))
    finish(bm, "SignPlate", m_plate)
    bm = bmesh.new()
    add_box(bm, (0.26, 0.008, 0.055), Matrix.Translation((-0.245, PD * 0.5 + 0.016, 0.905)))
    add_box(bm, (0.22, 0.008, 0.035), Matrix.Translation((-0.245, PD * 0.5 + 0.016, 0.828)))
    finish(bm, "SignText", m_sign)

    bm = bmesh.new()
    add_box(bm, (0.46, 0.26, 0.04), Matrix.Translation((0.0, -0.60, -0.015)))
    for i in range(7):
        add_box(bm, (0.40, 0.012, 0.05), Matrix.Translation((0.0, -0.72 + i * 0.036, 0.005)))
    finish(bm, "GroundDrain", m_steel_d)

    # bollards
    bm = bmesh.new()
    for bxp in (-1.85, 1.85):
        add_cyl(bm, 0.075, 0.92, Matrix.Translation((bxp, -0.05, 0.46)), 24)
        add_cone(bm, 0.085, 0.045, 0.08, Matrix.Translation((bxp, -0.05, 0.94)), 24)
        add_cyl(bm, 0.105, 0.06, Matrix.Translation((bxp, -0.05, 0.03)), 24)
    finish(bm, "Bollards", m_steel_d, smooth=True)

    # planter behind the fountain
    bm = bmesh.new()
    for (sx, sy, w, d) in ((0.0, 1.86, 2.60, 0.10), (0.0, 2.66, 2.60, 0.10),
                          (-1.25, 2.26, 0.10, 0.90), (1.25, 2.26, 0.10, 0.90)):
        add_box(bm, (w, d, 0.46), Matrix.Translation((sx, sy, 0.23)))
    finish(bm, "Planter", m_curb)
    bm = bmesh.new()
    add_box(bm, (2.40, 0.70, 0.34), Matrix.Translation((0.0, 2.26, 0.20)))
    finish(bm, "PlanterSoil", m_soil)
    bm = bmesh.new()
    for i in range(11):
        px = -1.05 + i * 0.21
        for k in range(3):
            r = random.uniform(0.10, 0.17)
            add_sphere(bm, r, Matrix.Translation((px + random.uniform(-0.06, 0.06),
                                                  2.26 + random.uniform(-0.18, 0.18),
                                                  0.40 + r * 0.7 + k * 0.06)), 14, 9)
    finish(bm, "Shrubs", m_leaf, smooth=True)

    add_sun("Sun", 4.0, (math.radians(55.0), 0.0, math.radians(28.0)))
    add_area("SkyFill", 300.0, (-2.5, -4.0, 4.0), (0.0, 0.0, 0.9), 6.0, (0.72, 0.82, 1.0))
    add_area("Rim", 120.0, (3.0, 2.6, 2.4), (0.0, 0.0, 0.9), 3.0, (1.0, 0.93, 0.82))
    add_camera((1.55, -2.35, 1.55), (0.0, -0.10, 0.86), lens=55.0)


build()
