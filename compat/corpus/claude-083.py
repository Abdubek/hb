"""Spiral display stand with staggered circular shelves around a central mast."""
import bpy, bmesh, math
from mathutils import Vector, Matrix


def reset_scene():
    bpy.ops.wm.read_factory_settings(use_empty=True)
    sc = bpy.context.scene
    try:
        sc.render.engine = 'CYCLES'
        sc.cycles.samples = 128
    except Exception:
        pass
    sc.render.resolution_x, sc.render.resolution_y = 1440, 1800
    return sc


def collection(name):
    c = bpy.data.collections.new(name)
    bpy.context.scene.collection.children.link(c)
    return c


def material(name, color, rough=0.5, metal=0.0, transmission=0.0, ior=1.45,
             emission=None, strength=0.0):
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


def add_sphere(bm, center, r, mi=0, seg=24):
    res = bmesh.ops.create_uvsphere(bm, u_segments=seg, v_segments=max(4, seg // 2),
                                    radius=r, matrix=Matrix.Translation(center))
    for v in res["verts"]:
        for f in v.link_faces:
            f.material_index = mi


def add_light(name, kind, loc, energy, color=(1, 1, 1), size=1.0, size_y=None,
              target=(0, 0, 0)):
    l = bpy.data.lights.new(name, kind)
    l.energy = energy
    l.color = color
    if kind == 'AREA':
        l.size = size
        if size_y is not None:
            l.shape = 'RECTANGLE'
            l.size_y = size_y
    ob = bpy.data.objects.new(name, l)
    bpy.context.scene.collection.objects.link(ob)
    ob.location = loc
    ob.rotation_euler = (Vector(target) - Vector(loc)).to_track_quat('-Z', 'Y').to_euler()
    return ob


def add_camera(loc, target, lens=70.0):
    cam = bpy.data.cameras.new("Camera")
    cam.lens = lens
    cam.clip_start, cam.clip_end = 0.01, 100.0
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


# -------------------------------------------------------------- stand params
N_SHELF = 10
Z0 = 0.185
DZ = 0.138
OFFSET = 0.115                    # shelf centre offset from the mast axis
DTHETA = math.radians(40.0)       # spiral increment between shelves
MAST_H = 1.62


def shelf_radius(i):
    return 0.185 if i % 2 == 0 else 0.155


def build():
    reset_scene()
    set_world((0.05, 0.05, 0.055), 1.0)

    col_stand = collection("Stand")
    col_prod = collection("Products")
    col_set = collection("Set")

    m_mast = material("BrushedSteel", (0.55, 0.56, 0.58), rough=0.26, metal=1.0)
    m_brass = material("Brass", (0.72, 0.55, 0.24), rough=0.22, metal=1.0)
    m_shelf = material("WhiteAcrylic", (0.90, 0.90, 0.89), rough=0.30)
    m_edge = material("ShelfEdge", (0.13, 0.13, 0.14), rough=0.45)
    m_glass = material("ProductGlass", (0.85, 0.88, 0.90), rough=0.04,
                       transmission=1.0, ior=1.48)
    m_amber = material("Amber", (0.55, 0.24, 0.05), rough=0.15, transmission=0.85, ior=1.4)
    m_navy = material("Navy", (0.05, 0.09, 0.22), rough=0.35)
    m_cream = material("Cream", (0.92, 0.88, 0.78), rough=0.55)
    m_floor = material("Cyclorama", (0.34, 0.34, 0.36), rough=0.55)
    m_glow = material("ShelfGlow", (1.0, 0.95, 0.85), rough=0.4,
                      emission=(1.0, 0.94, 0.82), strength=6.0)

    # ------------------------------------------------------------ base + mast
    bm = bmesh.new()
    add_cyl(bm, (0, 0, 0.0), (0, 0, 0.028), 0.265, seg=64, mi=0)
    add_cyl(bm, (0, 0, 0.028), (0, 0, 0.048), 0.245, seg=64, mi=0, r2=0.215)
    ob = mesh_object("Base", bm, [m_brass], col_stand, smooth=True)
    b = ob.modifiers.new("Bevel", 'BEVEL')
    b.width = 0.004
    b.segments = 3
    b.limit_method = 'ANGLE'

    bm = bmesh.new()
    add_cyl(bm, (0, 0, 0.040), (0, 0, MAST_H), 0.042, seg=48, mi=0, r2=0.030)
    add_cyl(bm, (0, 0, MAST_H), (0, 0, MAST_H + 0.02), 0.036, seg=48, mi=0)
    mesh_object("Mast", bm, [m_mast], col_stand, smooth=True)

    bm = bmesh.new()
    add_sphere(bm, (0.0, 0.0, MAST_H + 0.055), 0.042, mi=0, seg=32)
    mesh_object("Finial", bm, [m_brass], col_stand, smooth=True)

    # ---------------------------------------------------------------- shelves
    bm_shelf = bmesh.new()
    bm_edge = bmesh.new()
    bm_arm = bmesh.new()
    bm_glow = bmesh.new()
    shelf_data = []
    for i in range(N_SHELF):
        th = i * DTHETA
        z = Z0 + i * DZ
        cx, cy = OFFSET * math.cos(th), OFFSET * math.sin(th)
        r = shelf_radius(i)
        shelf_data.append((cx, cy, z, r, th))

        add_cyl(bm_shelf, (cx, cy, z), (cx, cy, z + 0.016), r, seg=64, mi=0)
        add_cyl(bm_edge, (cx, cy, z + 0.016), (cx, cy, z + 0.0215), r * 0.995,
                seg=64, mi=0, r2=r * 0.96)
        add_box(bm_arm, (cx * 0.5, cy * 0.5, z - 0.012),
                (OFFSET + 0.02, 0.052, 0.030), 0, rot_z=th)
        add_cyl(bm_arm, (cx, cy, z - 0.030), (cx, cy, z + 0.001), 0.030, seg=24, mi=0)
        add_cyl(bm_glow, (cx, cy, z - 0.004), (cx, cy, z - 0.001), r * 0.93, seg=48, mi=0)

    ob = mesh_object("Shelves", bm_shelf, [m_shelf], col_stand, smooth=True)
    b = ob.modifiers.new("Bevel", 'BEVEL')
    b.width = 0.0022
    b.segments = 3
    b.limit_method = 'ANGLE'
    mesh_object("ShelfEdges", bm_edge, [m_edge], col_stand, smooth=True)
    ob = mesh_object("ShelfArms", bm_arm, [m_mast], col_stand, smooth=True)
    b = ob.modifiers.new("Bevel", 'BEVEL')
    b.width = 0.003
    b.segments = 2
    b.limit_method = 'ANGLE'
    mesh_object("ShelfLighting", bm_glow, [m_glow], col_stand)

    # --------------------------------------------------------------- products
    bm_g, bm_a, bm_n, bm_c = bmesh.new(), bmesh.new(), bmesh.new(), bmesh.new()
    for i, (cx, cy, z, r, th) in enumerate(shelf_data):
        top = z + 0.0215
        kind = i % 4
        if kind == 0:                                   # tall glass flacon
            add_cyl(bm_g, (cx, cy, top), (cx, cy, top + 0.10), 0.032, seg=40, mi=0, r2=0.028)
            add_cyl(bm_a, (cx, cy, top + 0.004), (cx, cy, top + 0.062), 0.027, seg=40, mi=0)
            add_cyl(bm_n, (cx, cy, top + 0.10), (cx, cy, top + 0.126), 0.017, seg=32, mi=0)
        elif kind == 1:                                 # low round jar with lid
            add_cyl(bm_c, (cx, cy, top), (cx, cy, top + 0.048), 0.040, seg=40, mi=0)
            add_cyl(bm_n, (cx, cy, top + 0.048), (cx, cy, top + 0.062), 0.041, seg=40, mi=0)
        elif kind == 2:                                 # boxed set, tilted
            add_box(bm_n, (cx + 0.02, cy - 0.015, top + 0.052),
                    (0.062, 0.062, 0.104), 0, rot_z=th + 0.5)
            add_box(bm_c, (cx - 0.055, cy + 0.03, top + 0.018),
                    (0.05, 0.05, 0.036), 0, rot_z=th - 0.4)
        else:                                           # sphere plus small vial
            add_sphere(bm_g, (cx, cy, top + 0.038), 0.038, mi=0, seg=32)
            add_cyl(bm_a, (cx + 0.07, cy + 0.02, top), (cx + 0.07, cy + 0.02, top + 0.055),
                    0.016, seg=28, mi=0)
    mesh_object("ProductGlass", bm_g, [m_glass], col_prod, smooth=True)
    mesh_object("ProductLiquid", bm_a, [m_amber], col_prod, smooth=True)
    ob = mesh_object("ProductBoxes", bm_n, [m_navy], col_prod)
    b = ob.modifiers.new("Bevel", 'BEVEL')
    b.width = 0.0015
    b.segments = 2
    b.limit_method = 'ANGLE'
    ob = mesh_object("ProductCartons", bm_c, [m_cream], col_prod)
    b = ob.modifiers.new("Bevel", 'BEVEL')
    b.width = 0.0015
    b.segments = 2
    b.limit_method = 'ANGLE'

    # -------------------------------------------------------------- cyclorama
    bm = bmesh.new()
    prof = [(-2.2, 0.0), (0.55, 0.0)]
    for k in range(1, 15):                       # cove arc, centre (0.55, 0.85) r=0.85
        a = -math.pi / 2.0 + (math.pi / 2.0) * k / 14
        prof.append((0.55 + 0.85 * math.cos(a), 0.85 + 0.85 * math.sin(a)))
    prof.append((1.40, 3.2))
    rows = []
    for x in (-3.0, 3.0):
        rows.append([bm.verts.new((x, y, z)) for (y, z) in prof])
    for i in range(len(prof) - 1):
        bm.faces.new((rows[0][i], rows[0][i + 1], rows[1][i + 1], rows[1][i]))
    mesh_object("Cyclorama", bm, [m_floor], col_set, smooth=True)

    # ----------------------------------------------------------- lights & cam
    add_light("Key", 'AREA', (-1.35, -1.45, 2.30), 480.0, color=(1.0, 0.96, 0.90),
              size=1.5, size_y=2.2, target=(0.0, 0.0, 0.9))
    add_light("Fill", 'AREA', (1.65, -1.10, 1.20), 160.0, color=(0.82, 0.88, 1.0),
              size=1.8, target=(0.0, 0.0, 0.8))
    add_light("Rim", 'AREA', (0.9, 1.5, 2.0), 320.0, color=(1.0, 0.88, 0.72),
              size=1.0, target=(0.0, 0.0, 1.0))
    add_light("BackdropWash", 'AREA', (0.0, -0.4, 2.9), 120.0, color=(0.75, 0.8, 1.0),
              size=2.5, target=(0.0, 1.2, 1.6))

    add_camera((1.35, -2.30, 1.15), (0.0, 0.0, 0.86), lens=72.0)

    print("Spiral display stand built: %d shelves, %d objects"
          % (N_SHELF, len(bpy.data.objects)))


build()
