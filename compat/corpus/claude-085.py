"""Desk organizer: A4 paper tray, pen cups, clip bin and contents."""
import bpy, bmesh, math, random
from mathutils import Vector, Matrix

random.seed(7)


def reset_scene():
    bpy.ops.wm.read_factory_settings(use_empty=True)
    sc = bpy.context.scene
    try:
        sc.render.engine = 'CYCLES'
        sc.cycles.samples = 128
    except Exception:
        pass
    sc.render.resolution_x, sc.render.resolution_y = 1920, 1280
    return sc


def collection(name):
    c = bpy.data.collections.new(name)
    bpy.context.scene.collection.children.link(c)
    return c


def material(name, color, rough=0.5, metal=0.0, coat=0.0):
    m = bpy.data.materials.new(name)
    m.use_nodes = True
    b = m.node_tree.nodes.get("Principled BSDF")
    i = b.inputs
    i["Base Color"].default_value = (*color, 1.0)
    i["Roughness"].default_value = rough
    i["Metallic"].default_value = metal
    if "Coat Weight" in i:
        i["Coat Weight"].default_value = coat
    return m


def wood_material(name, c1, c2, scale=3.0, rough=0.42):
    m = bpy.data.materials.new(name)
    m.use_nodes = True
    nt = m.node_tree
    bsdf = nt.nodes.get("Principled BSDF")
    coord = nt.nodes.new("ShaderNodeTexCoord")
    coord.location = (-900, 0)
    wave = nt.nodes.new("ShaderNodeTexWave")
    wave.location = (-680, 0)
    wave.wave_type = 'BANDS'
    wave.bands_direction = 'Y'
    wave.inputs["Scale"].default_value = scale
    wave.inputs["Distortion"].default_value = 7.0
    wave.inputs["Detail"].default_value = 6.0
    wave.inputs["Detail Scale"].default_value = 1.4
    ramp = nt.nodes.new("ShaderNodeValToRGB")
    ramp.location = (-440, 0)
    ramp.color_ramp.elements[0].color = (*c1, 1.0)
    ramp.color_ramp.elements[1].color = (*c2, 1.0)
    nt.links.new(coord.outputs["Object"], wave.inputs["Vector"])
    nt.links.new(wave.outputs["Fac"], ramp.inputs["Fac"])
    nt.links.new(ramp.outputs["Color"], bsdf.inputs["Base Color"])
    bsdf.inputs["Roughness"].default_value = rough
    return m


def mesh_object(name, bm, mats, col, smooth=False, bevel=None):
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
    if bevel:
        b = ob.modifiers.new("Bevel", 'BEVEL')
        b.width = bevel
        b.segments = 3
        b.limit_method = 'ANGLE'
        b.angle_limit = math.radians(40.0)
    return ob


def add_box(bm, center, size, mi=0, rot_z=0.0):
    mat = (Matrix.Translation(center) @ Matrix.Rotation(rot_z, 4, 'Z')
           @ Matrix.Diagonal(Vector((size[0], size[1], size[2], 1.0))))
    res = bmesh.ops.create_cube(bm, size=1.0, matrix=mat)
    for v in res["verts"]:
        for f in v.link_faces:
            f.material_index = mi


def add_cyl(bm, p0, p1, r, seg=32, mi=0, r2=None):
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


def add_tube(bm, cx, cy, z0, z1, r_out, r_in, floor_t=0.005, seg=48, mi=0):
    """Open-topped cylindrical cup with a solid floor."""
    zf = z0 + floor_t

    def ring(r, z):
        return [bm.verts.new((cx + r * math.cos(2 * math.pi * i / seg),
                              cy + r * math.sin(2 * math.pi * i / seg), z))
                for i in range(seg)]

    ob_bot, ob_top = ring(r_out, z0), ring(r_out, z1)
    in_top, in_flr = ring(r_in, z1), ring(r_in, zf)
    faces = []
    for i in range(seg):
        j = (i + 1) % seg
        faces.append(bm.faces.new((ob_bot[i], ob_bot[j], ob_top[j], ob_top[i])))
        faces.append(bm.faces.new((in_flr[i], in_top[i], in_top[j], in_flr[j])))
        faces.append(bm.faces.new((ob_top[i], ob_top[j], in_top[j], in_top[i])))
    faces.append(bm.faces.new(ob_bot[::-1]))
    faces.append(bm.faces.new(in_flr))
    for f in faces:
        f.material_index = mi


def add_light(name, kind, loc, energy, color=(1, 1, 1), size=1.0, size_y=None,
              target=(0, 0, 0), angle=None):
    l = bpy.data.lights.new(name, kind)
    l.energy = energy
    l.color = color
    if kind == 'AREA':
        l.size = size
        if size_y is not None:
            l.shape = 'RECTANGLE'
            l.size_y = size_y
    if kind == 'SUN' and angle is not None:
        l.angle = angle
    ob = bpy.data.objects.new(name, l)
    bpy.context.scene.collection.objects.link(ob)
    ob.location = loc
    ob.rotation_euler = (Vector(target) - Vector(loc)).to_track_quat('-Z', 'Y').to_euler()
    return ob


def add_camera(loc, target, lens=55.0):
    cam = bpy.data.cameras.new("Camera")
    cam.lens = lens
    cam.clip_start, cam.clip_end = 0.005, 100.0
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


# ---------------------------------------------------------------- dimensions
T = 0.006             # wall thickness
IN_X = 0.222          # inner width  (A4 short side + clearance)
IN_Y = 0.306          # inner depth  (A4 long side + clearance)
OUT_X = IN_X + 2 * T
Y_FRONT = -IN_Y / 2.0 - T
Y_BACK = IN_Y / 2.0 + T
WALL_H = 0.046
FLOOR_T = 0.006
RISER_Y0 = Y_BACK
RISER_Y1 = Y_BACK + 0.125
CUP_R = 0.033
CUP_H = 0.098


def build():
    reset_scene()
    set_world((0.05, 0.055, 0.065), 1.0)

    col_org = collection("Organizer")
    col_cont = collection("Contents")
    col_set = collection("Desk")

    m_body = wood_material("Walnut", (0.115, 0.055, 0.026), (0.28, 0.15, 0.075),
                           scale=2.4, rough=0.42)
    m_alu = material("BrushedAluminium", (0.60, 0.61, 0.63), rough=0.30, metal=1.0)
    m_dark = material("SoftTouchABS", (0.075, 0.078, 0.085), rough=0.62)
    m_felt = material("Felt", (0.18, 0.22, 0.28), rough=0.95)
    m_paper = material("Paper", (0.93, 0.93, 0.91), rough=0.72)
    m_ink = material("PrintInk", (0.22, 0.24, 0.28), rough=0.6)
    m_barrel = material("PenBarrel", (0.05, 0.06, 0.09), rough=0.25, coat=0.5)
    m_red = material("PenRed", (0.55, 0.07, 0.08), rough=0.28, coat=0.5)
    m_pencil = material("PencilPaint", (0.85, 0.62, 0.10), rough=0.42)
    m_wood2 = material("PencilWood", (0.82, 0.68, 0.45), rough=0.7)
    m_lead = material("Graphite", (0.10, 0.10, 0.11), rough=0.5)
    m_chrome = material("Chrome", (0.85, 0.86, 0.88), rough=0.12, metal=1.0)
    m_desk = wood_material("DeskTop", (0.20, 0.13, 0.08), (0.42, 0.29, 0.17),
                           scale=1.1, rough=0.36)

    # ------------------------------------------------------------ tray carcass
    bm = bmesh.new()
    add_box(bm, (0.0, 0.0, FLOOR_T / 2.0), (OUT_X, IN_Y + 2 * T, FLOOR_T), 0)
    zc = FLOOR_T + (WALL_H - FLOOR_T) / 2.0
    hw = WALL_H - FLOOR_T
    for sx in (-1.0, 1.0):
        add_box(bm, (sx * (IN_X + T) / 2.0, 0.0, zc), (T, IN_Y + 2 * T, hw), 0)
    add_box(bm, (0.0, (IN_Y + T) / 2.0, zc), (IN_X, T, hw), 0)
    # front wall split by a central finger scoop
    for sx in (-1.0, 1.0):
        add_box(bm, (sx * (IN_X / 2.0 - 0.052), Y_FRONT + T / 2.0, zc), (0.104, T, hw), 0)
    add_box(bm, (0.0, Y_FRONT + T / 2.0, FLOOR_T + 0.007), (0.116, T, 0.014), 0)

    # riser plinth carrying the cups
    ry = 0.5 * (RISER_Y0 + RISER_Y1)
    rh = RISER_Y1 - RISER_Y0
    add_box(bm, (0.0, ry, 0.009), (OUT_X, rh, 0.018), 0)
    add_box(bm, (0.0, RISER_Y0 + T / 2.0, 0.030), (OUT_X, T, 0.042), 0)
    mesh_object("OrganizerBody", bm, [m_body], col_org, bevel=0.0018)

    bm = bmesh.new()
    add_box(bm, (0.0, 0.0, FLOOR_T + 0.0006), (IN_X - 0.002, IN_Y - 0.002, 0.0012), 0)
    mesh_object("TrayLining", bm, [m_felt], col_org)

    # --------------------------------------------------------------- pen cups
    bm = bmesh.new()
    cups = [(-0.068, ry + 0.004), (0.002, ry - 0.002)]
    for (cx, cy) in cups:
        add_tube(bm, cx, cy, 0.018, 0.018 + CUP_H, CUP_R, CUP_R - 0.0025,
                 floor_t=0.004, seg=56, mi=0)
    mesh_object("PenCups", bm, [m_alu], col_org, smooth=True, bevel=0.0008)

    bx, by = 0.078, ry
    bm = bmesh.new()
    add_box(bm, (bx, by, 0.018 + 0.016), (0.070, 0.070, 0.032), 0)
    mesh_object("ClipBinShell", bm, [m_dark], col_org, bevel=0.0025)
    bm = bmesh.new()
    add_box(bm, (bx, by, 0.018 + 0.028), (0.058, 0.058, 0.012), 0)
    mesh_object("ClipBinLiner", bm, [m_felt], col_org)

    bm = bmesh.new()
    for sx in (-1.0, 1.0):
        for cy in (Y_FRONT + 0.03, 0.0, RISER_Y1 - 0.03):
            add_cyl(bm, (sx * (IN_X / 2.0 - 0.012), cy, -0.004),
                    (sx * (IN_X / 2.0 - 0.012), cy, 0.0), 0.008, seg=16, mi=0)
    mesh_object("Feet", bm, [m_dark], col_org, smooth=True)

    # ---------------------------------------------------------- paper in tray
    bm = bmesh.new()
    z = FLOOR_T + 0.002
    for i in range(5):
        h = 0.0022
        add_box(bm, (0.0015 * math.sin(i * 1.7), 0.001 * i, z + h / 2.0),
                (0.210, 0.297, h), 0, rot_z=math.radians(0.7 * math.sin(i * 2.1)))
        z += h
    mesh_object("PaperStack", bm, [m_paper], col_cont)

    bm = bmesh.new()
    for i in range(9):
        w = 0.16 - 0.012 * (i % 3)
        add_box(bm, (-0.08 + w / 2.0, 0.09 - i * 0.018, z + 0.0004),
                (w, 0.0022, 0.0004), 0)
    mesh_object("PrintedLines", bm, [m_ink], col_cont)

    # ---------------------------------------------------------- pens, pencils
    def place_stick(bm_body, bm_tip, cx, cy, tilt, azim, length, r, tip_len, seg=16):
        base = Vector((cx, cy, 0.024))
        d = Vector((math.sin(tilt) * math.cos(azim), math.sin(tilt) * math.sin(azim),
                    math.cos(tilt)))
        top = base + d * length
        neck = base + d * (length - tip_len)
        add_cyl(bm_body, base, neck, r, seg=seg, mi=0)
        add_cyl(bm_tip, neck, top, r * 0.95, seg=seg, mi=0, r2=r * 0.12)
        return base, top, d

    bm_pen, bm_tip, bm_clip = bmesh.new(), bmesh.new(), bmesh.new()
    for (cx, cy, tl, az, ln) in [(cups[0][0] - 0.010, cups[0][1] + 0.008, 0.13, 1.9, 0.150),
                                 (cups[0][0] + 0.012, cups[0][1] - 0.006, 0.10, -0.6, 0.142)]:
        base, top, d = place_stick(bm_pen, bm_tip, cx, cy, tl, az, ln, 0.0045, 0.020)
        clip_dir = Vector((math.cos(az + 1.57), math.sin(az + 1.57), 0.0)) * 0.005
        add_box(bm_clip, tuple(base + d * (ln - 0.040) + clip_dir),
                (0.0035, 0.0035, 0.030), 0)
    mesh_object("Pens", bm_pen, [m_barrel], col_cont, smooth=True)
    mesh_object("PenTips", bm_tip, [m_chrome], col_cont, smooth=True)
    mesh_object("PenClips", bm_clip, [m_chrome], col_cont, bevel=0.0006)

    bm_red, bm_redtip = bmesh.new(), bmesh.new()
    place_stick(bm_red, bm_redtip, cups[1][0] + 0.014, cups[1][1] + 0.010,
                0.16, 0.4, 0.146, 0.0048, 0.022)
    mesh_object("RedPen", bm_red, [m_red], col_cont, smooth=True)
    mesh_object("RedPenTip", bm_redtip, [m_chrome], col_cont, smooth=True)

    bm_p, bm_w, bm_l = bmesh.new(), bmesh.new(), bmesh.new()
    for k, (dx, dy, tl, az) in enumerate([(-0.012, 0.004, 0.09, 2.6),
                                          (0.000, -0.012, 0.14, -1.2),
                                          (-0.004, 0.014, 0.05, 0.9)]):
        cx, cy = cups[1][0] + dx, cups[1][1] + dy
        base = Vector((cx, cy, 0.024))
        d = Vector((math.sin(tl) * math.cos(az), math.sin(tl) * math.sin(az), math.cos(tl)))
        ln = 0.168 - 0.012 * k
        neck = base + d * (ln - 0.016)
        cone = base + d * (ln - 0.004)
        add_cyl(bm_p, base, neck, 0.0037, seg=6, mi=0)          # hexagonal barrel
        add_cyl(bm_w, neck, cone, 0.0037, seg=12, mi=0, r2=0.0009)
        add_cyl(bm_l, cone, base + d * ln, 0.0009, seg=8, mi=0, r2=0.0002)
    mesh_object("Pencils", bm_p, [m_pencil], col_cont)
    mesh_object("PencilTips", bm_w, [m_wood2], col_cont, smooth=True)
    mesh_object("PencilLeads", bm_l, [m_lead], col_cont, smooth=True)

    bm = bmesh.new()
    for i in range(14):
        ax = bx + random.uniform(-0.020, 0.020)
        ay = by + random.uniform(-0.020, 0.020)
        az = 0.018 + 0.034 + random.uniform(0.0, 0.004)
        add_box(bm, (ax, ay, az), (0.022, 0.0085, 0.0011), 0,
                rot_z=random.uniform(0.0, math.pi))
    mesh_object("PaperClips", bm, [m_chrome], col_cont, bevel=0.0004)

    bm = bmesh.new()
    add_box(bm, (0.20, -0.05, 0.006), (0.076, 0.076, 0.012), 0, rot_z=math.radians(-8.0))
    mesh_object("StickyPad", bm,
                [material("StickyYellow", (0.94, 0.86, 0.36), 0.75)], col_set, bevel=0.0008)

    # ---------------------------------------------------------------- desktop
    bm = bmesh.new()
    add_box(bm, (0.0, 0.0, -0.011), (2.4, 1.6, 0.022), 0)
    mesh_object("Desk", bm, [m_desk], col_set, bevel=0.002)

    # ------------------------------------------------------------ light & cam
    add_light("KeyWindow", 'AREA', (-0.75, -0.55, 0.95), 220.0, color=(1.0, 0.97, 0.92),
              size=0.8, size_y=1.2, target=(0.0, 0.0, 0.05))
    add_light("Fill", 'AREA', (0.70, -0.45, 0.50), 45.0, color=(0.80, 0.86, 1.0),
              size=0.9, target=(0.0, 0.0, 0.05))
    add_light("Rim", 'AREA', (0.35, 0.85, 0.65), 70.0, color=(1.0, 0.90, 0.78),
              size=0.5, target=(0.0, 0.06, 0.08))
    add_light("TopSoft", 'AREA', (0.0, 0.0, 1.25), 90.0, size=1.6, target=(0.0, 0.0, 0.0))

    cam = add_camera((0.42, -0.52, 0.36), (-0.01, 0.03, 0.055), lens=52.0)
    cam.data.dof.use_dof = True
    cam.data.dof.focus_distance = 0.72
    cam.data.dof.aperture_fstop = 4.0

    print("Desk organizer built: %d objects" % len(bpy.data.objects))


build()
