"""Cylindrical perfume bottle: lathed glass body, metal collar, cap, curved label."""
import bpy, bmesh, math
from mathutils import Vector, Matrix


def reset_scene():
    bpy.ops.wm.read_factory_settings(use_empty=True)
    sc = bpy.context.scene
    try:
        sc.render.engine = 'CYCLES'
        sc.cycles.samples = 160
        sc.cycles.max_bounces = 24
        sc.cycles.transmission_bounces = 24
    except Exception:
        pass
    sc.render.resolution_x, sc.render.resolution_y = 1400, 1750
    return sc


def collection(name):
    c = bpy.data.collections.new(name)
    bpy.context.scene.collection.children.link(c)
    return c


def material(name, color, rough=0.5, metal=0.0, transmission=0.0, ior=1.45,
             emission=None, strength=0.0, coat=0.0):
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
    if "Coat Weight" in i:
        i["Coat Weight"].default_value = coat
    if emission is not None:
        i["Emission Color"].default_value = (*emission, 1.0)
        i["Emission Strength"].default_value = strength
    return m


def mesh_object(name, bm, mats, col, smooth=True):
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


def lathe(profile, segments=96, close=True):
    """Revolve a 2D (r, z) profile around the Z axis."""
    bm = bmesh.new()
    verts = [bm.verts.new((p[0], 0.0, p[1])) for p in profile]
    for a, b in zip(verts, verts[1:]):
        bm.edges.new((a, b))
    if close:
        bm.edges.new((verts[-1], verts[0]))
    geom = bm.verts[:] + bm.edges[:]
    bmesh.ops.spin(bm, geom=geom, cent=(0, 0, 0), axis=(0, 0, 1), dvec=(0, 0, 0),
                   angle=2.0 * math.pi, steps=segments,
                   use_merge=False, use_duplicate=False)
    bmesh.ops.remove_doubles(bm, verts=bm.verts[:], dist=1e-6)
    loose = [e for e in bm.edges if not e.link_faces]
    if loose:
        bmesh.ops.delete(bm, geom=loose, context='EDGES')
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    return bm


def arc(cx, cz, r, a0, a1, n):
    return [(cx + r * math.cos(a0 + (a1 - a0) * i / n),
             cz + r * math.sin(a0 + (a1 - a0) * i / n)) for i in range(n + 1)]


def shoulder(r0, z0, r1, z1, n):
    """Quarter-ellipse blend from the body radius r0 up to the neck radius r1."""
    pts = []
    for i in range(n + 1):
        t = (i / n) * (math.pi / 2.0)
        pts.append((r1 + (r0 - r1) * math.cos(t), z0 + (z1 - z0) * math.sin(t)))
    return pts


def add_box(bm, center, size, mi=0):
    mat = Matrix.Translation(center) @ Matrix.Diagonal(Vector((size[0], size[1], size[2], 1.0)))
    res = bmesh.ops.create_cube(bm, size=1.0, matrix=mat)
    for v in res["verts"]:
        for f in v.link_faces:
            f.material_index = mi


def cyl_patch(bm, radius, a_half, z0, z1, nu=32, nv=8, mi=0):
    """Rectangular patch wrapped on a cylinder of the given radius, facing -Y."""
    grid = []
    for j in range(nv + 1):
        z = z0 + (z1 - z0) * j / nv
        row = []
        for i in range(nu + 1):
            a = -a_half + 2.0 * a_half * i / nu
            row.append(bm.verts.new((radius * math.sin(a), -radius * math.cos(a), z)))
        grid.append(row)
    for j in range(nv):
        for i in range(nu):
            f = bm.faces.new((grid[j][i], grid[j][i + 1], grid[j + 1][i + 1], grid[j + 1][i]))
            f.material_index = mi


def text_on_cylinder(name, body, size, radius, z_center, mat, col,
                     extrude=0.00025, spacing=1.0):
    """Build text as a mesh, then remap its local X into an angle around Z."""
    cu = bpy.data.curves.new(name + "_font", type='FONT')
    cu.body = body
    cu.size = size
    cu.align_x = 'CENTER'
    cu.align_y = 'CENTER'
    cu.extrude = extrude
    cu.space_character = spacing
    tmp = bpy.data.objects.new(name + "_tmp", cu)
    bpy.context.scene.collection.objects.link(tmp)
    dg = bpy.context.evaluated_depsgraph_get()
    me = bpy.data.meshes.new_from_object(tmp.evaluated_get(dg))
    bpy.data.objects.remove(tmp, do_unlink=True)
    bpy.data.curves.remove(cu)
    for v in me.vertices:
        a = v.co.x / radius
        r = radius + v.co.z
        v.co = Vector((r * math.sin(a), -r * math.cos(a), z_center + v.co.y))
    me.materials.append(mat)
    ob = bpy.data.objects.new(name, me)
    col.objects.link(ob)
    return ob


def add_light(name, loc, energy, color=(1, 1, 1), size=0.4, size_y=None, target=(0, 0, 0)):
    l = bpy.data.lights.new(name, 'AREA')
    l.energy = energy
    l.color = color
    l.size = size
    if size_y is not None:
        l.shape = 'RECTANGLE'
        l.size_y = size_y
    ob = bpy.data.objects.new(name, l)
    bpy.context.scene.collection.objects.link(ob)
    ob.location = loc
    ob.rotation_euler = (Vector(target) - Vector(loc)).to_track_quat('-Z', 'Y').to_euler()
    return ob


def add_camera(loc, target, lens=85.0):
    cam = bpy.data.cameras.new("Camera")
    cam.lens = lens
    cam.clip_start, cam.clip_end = 0.001, 50.0
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


# ------------------------------------------------------------- bottle params
R_BODY = 0.0225       # 45 mm diameter
R_WALL = 0.0025
Z_SHOULD = 0.060
Z_NECK_T = 0.0995
R_NECK = 0.0080
FILL_Z = 0.0520


def build():
    reset_scene()
    set_world((0.03, 0.03, 0.035), 1.0)

    col_bottle = collection("Bottle")
    col_set = collection("Set")

    m_glass = material("ClearGlass", (0.92, 0.95, 0.94), rough=0.015,
                       transmission=1.0, ior=1.46)
    m_juice = material("Fragrance", (0.72, 0.36, 0.06), rough=0.02,
                       transmission=0.92, ior=1.38)
    m_gold = material("PolishedGold", (0.80, 0.60, 0.26), rough=0.14, metal=1.0)
    m_cap = material("CapLacquer", (0.07, 0.075, 0.085), rough=0.22, coat=0.6)
    m_label = material("LabelStock", (0.94, 0.91, 0.83), rough=0.62)
    m_ink = material("LabelInk", (0.10, 0.09, 0.08), rough=0.55)
    m_base = material("Pedestal", (0.10, 0.10, 0.11), rough=0.08)
    m_bg = material("Backdrop", (0.16, 0.16, 0.18), rough=0.75)

    # ------------------------------------------------------------- glass body
    prof = [(0.0, 0.0), (0.0180, 0.0)]
    prof += arc(0.0180, 0.0045, 0.0045, -math.pi / 2.0, 0.0, 8)[1:]
    prof += [(R_BODY, Z_SHOULD)]
    prof += shoulder(R_BODY, Z_SHOULD, R_NECK, 0.0885, 16)[1:]
    prof += [(R_NECK, Z_NECK_T), (R_NECK - 0.0022, Z_NECK_T), (R_NECK - 0.0022, 0.0880)]
    prof += [(p[0] - 0.0025, p[1] - 0.0015) for p in
             reversed(shoulder(R_BODY, Z_SHOULD, R_NECK, 0.0880, 14)[1:-1])]
    prof += [(R_BODY - R_WALL, 0.0070), (0.0, 0.0070)]
    mesh_object("BottleGlass", lathe(prof, 96), [m_glass], col_bottle)

    # ---------------------------------------------------------------- liquid
    juice = [(0.0, 0.0072), (R_BODY - R_WALL - 0.0002, 0.0072),
             (R_BODY - R_WALL - 0.0002, FILL_Z), (0.0, FILL_Z)]
    mesh_object("Fragrance", lathe(juice, 96), [m_juice], col_bottle)

    # ----------------------------------------------------- collar and sprayer
    collar = [(0.0078, 0.0870), (0.0100, 0.0875), (0.0100, 0.0985), (0.0078, 0.0990)]
    mesh_object("NeckCollar", lathe(collar, 96), [m_gold], col_bottle)

    stem = [(0.0, 0.0995), (0.0048, 0.0995), (0.0048, 0.1075), (0.0, 0.1075)]
    mesh_object("SprayStem", lathe(stem, 48), [m_gold], col_bottle)

    # ------------------------------------------------------------------- cap
    cap = [(0.0092, 0.0955), (0.0138, 0.0955), (0.0138, 0.1265)]
    cap += arc(0.0098, 0.1265, 0.0040, 0.0, math.pi / 2.0, 8)[1:]
    cap += [(0.0, 0.1305), (0.0, 0.1240), (0.0092, 0.1240)]
    mesh_object("Cap", lathe(cap, 96), [m_cap], col_bottle)

    band = [(0.0139, 0.0960), (0.0146, 0.0965), (0.0146, 0.1035), (0.0139, 0.1040)]
    mesh_object("CapBand", lathe(band, 96), [m_gold], col_bottle)

    # ---------------------------------------------------------- curved label
    bm = bmesh.new()
    cyl_patch(bm, R_BODY + 0.00018, 0.62, 0.0215, 0.0505, nu=40, nv=10, mi=0)
    ob = mesh_object("LabelPanel", bm, [m_label], col_bottle)
    sol = ob.modifiers.new("Solidify", 'SOLIDIFY')
    sol.thickness = 0.00035
    sol.offset = 1.0

    bm = bmesh.new()
    cyl_patch(bm, R_BODY + 0.00062, 0.58, 0.0230, 0.0233, nu=36, nv=1, mi=0)
    cyl_patch(bm, R_BODY + 0.00062, 0.58, 0.0487, 0.0490, nu=36, nv=1, mi=0)
    cyl_patch(bm, R_BODY + 0.00062, 0.22, 0.0296, 0.0299, nu=18, nv=1, mi=0)
    mesh_object("LabelRules", bm, [m_ink], col_bottle)

    text_on_cylinder("Label_Brand", "AURA", 0.0072, R_BODY + 0.00060,
                     0.0393, m_ink, col_bottle, extrude=0.0002, spacing=1.25)
    text_on_cylinder("Label_Sub", "EAU DE PARFUM", 0.0021, R_BODY + 0.00060,
                     0.0262, m_ink, col_bottle, extrude=0.00012)
    text_on_cylinder("Label_Vol", "50 ml", 0.0018, R_BODY + 0.00060,
                     0.0327, m_ink, col_bottle, extrude=0.00012)

    # ------------------------------------------------------------------- set
    ped = [(0.0, 0.0), (0.075, 0.0), (0.075, -0.010), (0.0, -0.010)]
    mesh_object("Pedestal", lathe(ped, 64), [m_base], col_set)

    bm = bmesh.new()
    add_box(bm, (0.0, 0.22, 0.10), (1.4, 0.02, 0.9), 0)
    add_box(bm, (0.0, 0.0, -0.026), (1.4, 1.0, 0.03), 0)
    mesh_object("Backdrop", bm, [m_bg], col_set, smooth=False)

    # ---------------------------------------------------------- studio lights
    add_light("KeySoftbox", (-0.20, -0.24, 0.26), 28.0, color=(1.0, 0.97, 0.93),
              size=0.30, size_y=0.45, target=(0.0, 0.0, 0.06))
    add_light("RimLeft", (-0.26, 0.16, 0.16), 16.0, color=(0.78, 0.86, 1.0),
              size=0.05, size_y=0.34, target=(0.0, 0.0, 0.06))
    add_light("RimRight", (0.26, 0.14, 0.17), 18.0, color=(1.0, 0.86, 0.66),
              size=0.05, size_y=0.34, target=(0.0, 0.0, 0.06))
    add_light("TopKicker", (0.02, -0.05, 0.42), 14.0, size=0.22, target=(0.0, 0.0, 0.11))
    add_light("Bounce", (0.16, -0.20, 0.02), 6.0, color=(1.0, 0.95, 0.9),
              size=0.30, target=(0.0, 0.0, 0.05))

    cam = add_camera((0.052, -0.185, 0.098), (0.0, 0.0, 0.062), lens=90.0)
    cam.data.dof.use_dof = True
    cam.data.dof.focus_distance = 0.20
    cam.data.dof.aperture_fstop = 5.6

    print("Perfume bottle built: %d objects" % len(bpy.data.objects))


build()
