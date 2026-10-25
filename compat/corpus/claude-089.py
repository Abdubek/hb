"""claude-089 : Small delivery van with windows, doors and wheels.
Builds the whole scene from an empty factory startup (no render, no file output).
"""
import bpy, bmesh, math
from mathutils import Vector, Matrix, Euler


# ----------------------------------------------------------------- helpers --
def reset():
    bpy.ops.wm.read_factory_settings(use_empty=True)
    s = bpy.context.scene
    try:
        s.render.engine = 'CYCLES'
        s.cycles.samples = 128
    except Exception:
        pass
    s.render.resolution_x, s.render.resolution_y = 1800, 1100
    return s


def mat(name, base, metallic=0.0, rough=0.5, trans=0.0, emis=None, es=0.0, coat=0.0):
    m = bpy.data.materials.new(name)
    m.use_nodes = True
    i = m.node_tree.nodes["Principled BSDF"].inputs
    i["Base Color"].default_value = (base[0], base[1], base[2], 1.0)
    i["Metallic"].default_value = metallic
    i["Roughness"].default_value = rough
    if trans:
        for k in ("Transmission Weight", "Transmission"):
            if k in i:
                i[k].default_value = trans
                break
    if coat:
        for k in ("Coat Weight", "Clearcoat"):
            if k in i:
                i[k].default_value = coat
                break
    if emis:
        for k in ("Emission Color", "Emission"):
            if k in i:
                i[k].default_value = (emis[0], emis[1], emis[2], 1.0)
                break
        if "Emission Strength" in i:
            i["Emission Strength"].default_value = es
    return m


def link(ob, parent=None):
    bpy.context.scene.collection.objects.link(ob)
    if parent:
        ob.parent = parent
    return ob


def smooth(ob, angle=math.radians(35)):
    for p in ob.data.polygons:
        p.use_smooth = True
    md = ob.modifiers.new("Smooth", 'EDGE_SPLIT')
    md.split_angle = angle
    return ob


def tf(loc=(0, 0, 0), rot=(0, 0, 0)):
    return Matrix.Translation(loc) @ Euler(rot, 'XYZ').to_matrix().to_4x4()


def _bevel(bm, res, offset, segments):
    vs = res['verts']
    es, fs = set(), set()
    for v in vs:
        es.update(v.link_edges)
        fs.update(v.link_faces)
    bmesh.ops.bevel(bm, geom=list(vs) + list(es) + list(fs), offset=offset,
                    segments=segments, profile=0.5, affect='EDGES', clamp_overlap=True)


def bm_box(bm, size, matrix=None, bevel=0.0, segments=2):
    M = (matrix or Matrix.Identity(4)) @ Matrix.Diagonal(
        Vector((size[0], size[1], size[2], 1.0)))
    res = bmesh.ops.create_cube(bm, size=1.0, matrix=M)
    if bevel > 0.0:
        _bevel(bm, res, bevel, segments)
    return res


def bm_cyl(bm, r, depth, matrix=None, segs=28, r2=None, cap=True, bevel=0.0, bsegs=2):
    res = bmesh.ops.create_cone(bm, cap_ends=cap, cap_tris=False, segments=segs,
                                radius1=r, radius2=(r if r2 is None else r2),
                                depth=depth, matrix=(matrix or Matrix.Identity(4)))
    if bevel > 0.0:
        _bevel(bm, res, bevel, bsegs)
    return res


def bm_loft(bm, rings, caps=True):
    vr = [[bm.verts.new(p) for p in ring] for ring in rings]
    for a, b in zip(vr, vr[1:]):
        n = len(a)
        for i in range(n):
            j = (i + 1) % n
            bm.faces.new((a[i], a[j], b[j], b[i]))
    if caps:
        bm.faces.new(list(reversed(vr[0])))
        bm.faces.new(vr[-1])
    return vr


def bm_finish(bm, name, material=None, parent=None, smooth_angle=None):
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces[:])
    me = bpy.data.meshes.new(name)
    bm.to_mesh(me)
    bm.free()
    ob = bpy.data.objects.new(name, me)
    link(ob, parent)
    if material:
        me.materials.append(material)
    if smooth_angle is not None:
        smooth(ob, smooth_angle)
    return ob


def quad(name, corners, material, parent=None, thickness=0.0):
    bm = bmesh.new()
    vs = [bm.verts.new(c) for c in corners]
    bm.faces.new(vs)
    ob = bm_finish(bm, name, material, parent)
    if thickness > 0.0:
        md = ob.modifiers.new("Solidify", 'SOLIDIFY')
        md.thickness = thickness
        md.offset = 0.0
    return ob


def boolean_cut(target, cutter):
    md = target.modifiers.new("Bool", 'BOOLEAN')
    md.operation = 'DIFFERENCE'
    md.solver = 'EXACT'
    md.object = cutter
    bpy.context.view_layer.objects.active = target
    bpy.ops.object.modifier_apply(modifier=md.name)
    bpy.data.objects.remove(cutter, do_unlink=True)


def add_light(name, ltype, energy, loc, target=None, size=1.0):
    d = bpy.data.lights.new(name, ltype)
    d.energy = energy
    if ltype == 'AREA':
        d.size = size
    elif ltype == 'SUN':
        d.angle = math.radians(2.0)
    ob = bpy.data.objects.new(name, d)
    link(ob)
    ob.location = loc
    if target:
        ob.rotation_euler = (Vector(target) - ob.location).to_track_quat('-Z', 'Y').to_euler()
    return ob


# ------------------------------------------------------------------- scene --
scene = reset()
w = bpy.data.worlds.new("World")
w.use_nodes = True
bg = w.node_tree.nodes["Background"]
bg.inputs[0].default_value = (0.32, 0.38, 0.48, 1.0)
bg.inputs[1].default_value = 1.1
scene.world = w

M_BODY = mat("BodyPaint", (0.86, 0.87, 0.89), metallic=0.35, rough=0.24, coat=0.6)
M_ACCENT = mat("Accent", (0.05, 0.24, 0.52), metallic=0.3, rough=0.30, coat=0.4)
M_TRIM = mat("DarkTrim", (0.035, 0.035, 0.04), rough=0.55)
M_GLASS = mat("Glass", (0.55, 0.62, 0.66), rough=0.05, trans=0.92)
M_CHROME = mat("Chrome", (0.80, 0.81, 0.83), metallic=1.0, rough=0.12)
M_RUBBER = mat("Rubber", (0.035, 0.035, 0.04), rough=0.88)
M_RIM = mat("Rim", (0.74, 0.75, 0.77), metallic=1.0, rough=0.24)
M_HEAD = mat("Headlight", (0.9, 0.9, 0.88), rough=0.08, emis=(1.0, 0.96, 0.85), es=3.0)
M_TAIL = mat("Taillight", (0.45, 0.02, 0.02), rough=0.2, emis=(0.9, 0.05, 0.04), es=2.0)
M_PLATE = mat("Plate", (0.88, 0.88, 0.85), rough=0.4)
M_ROAD = mat("Road", (0.16, 0.165, 0.17), rough=0.9)

root = bpy.data.objects.new("DeliveryVan", None)
link(root)

HW = 0.95            # body half width
WHEEL_R = 0.365
AX_F, AX_R = 1.52, -1.34

# --- body shell : side silhouette lofted across the width -------------------
profile = [(-2.30, 0.34), (2.26, 0.34), (2.42, 0.52), (2.44, 0.88), (2.38, 1.08),
           (2.08, 1.15), (1.84, 1.19), (1.30, 2.02), (1.16, 2.15), (0.40, 2.21),
           (-2.00, 2.22), (-2.22, 2.08), (-2.30, 1.70), (-2.32, 0.58)]
bm = bmesh.new()
bm_loft(bm, [[(-HW, y, z) for (y, z) in profile], [(HW, y, z) for (y, z) in profile]])
bmesh.ops.recalc_face_normals(bm, faces=bm.faces[:])
bmesh.ops.bevel(bm, geom=list(bm.verts) + list(bm.edges) + list(bm.faces),
                offset=0.055, segments=3, profile=0.5, affect='EDGES', clamp_overlap=True)
body = bm_finish(bm, "BodyShell", M_BODY, root)

# wheel arch openings, cut only through the outer walls
for (ay, ) in ((AX_F, ), (AX_R, )):
    for sx in (1, -1):
        bc = bmesh.new()
        bm_cyl(bc, 0.505, 0.58, tf((sx * 0.72, ay, WHEEL_R + 0.045),
                                   (0, math.radians(90), 0)), segs=32)
        cutter = bm_finish(bc, "ArchCut", None, None)
        boolean_cut(body, cutter)
smooth(body, math.radians(32))

# --- wheel arch lips ---------------------------------------------------------
for ay in (AX_F, AX_R):
    for sx in (1, -1):
        cu = bpy.data.curves.new("ArchLip", 'CURVE')
        cu.dimensions = '3D'
        cu.bevel_depth = 0.030
        cu.bevel_resolution = 3
        cu.resolution_u = 3
        sp = cu.splines.new('POLY')
        pts = []
        for k in range(17):
            a = math.radians(4 + k * (172.0 / 16.0))
            pts.append((sx * (HW - 0.01), ay + 0.505 * math.cos(a),
                        WHEEL_R + 0.045 + 0.505 * math.sin(a)))
        sp.points.add(len(pts) - 1)
        for i, p in enumerate(pts):
            sp.points[i].co = (p[0], p[1], p[2], 1.0)
        ob = bpy.data.objects.new("ArchLip", cu)
        link(ob, root)
        cu.materials.append(M_TRIM)

# --- glazing -----------------------------------------------------------------
# windscreen sits just proud of the sloped cowl facet
wn = Vector((0.0, 2.02 - 1.19, 1.30 - 1.84)).normalized()
wn = Vector((0.0, -wn.y, -wn.x)) if False else Vector((0.0, 0.838, 0.545))
off = wn * 0.012
quad("Windscreen",
     [(-HW + 0.10, 1.845 + off.y, 1.205 + off.z), (HW - 0.10, 1.845 + off.y, 1.205 + off.z),
      (HW - 0.16, 1.315 + off.y, 2.005 + off.z), (-HW + 0.16, 1.315 + off.y, 2.005 + off.z)],
     M_GLASS, root, thickness=0.014)

for sx in (1, -1):
    x = sx * (HW + 0.004)
    quad("DoorGlass.%d" % sx,
         [(x, 1.55, 1.36), (x, 0.62, 1.36), (x, 0.62, 1.90), (x, 1.30, 1.94)],
         M_GLASS, root, thickness=0.012)
    quad("RearDoorGlass.%d" % sx,
         [(x * 0.0 + sx * 0.44, -2.325, 1.42), (sx * 0.10, -2.325, 1.42),
          (sx * 0.10, -2.325, 1.86), (sx * 0.44, -2.325, 1.86)],
         M_GLASS, root, thickness=0.012)

# window rubbers / blackout frames
bm = bmesh.new()
for sx in (1, -1):
    x = sx * (HW + 0.001)
    bm_box(bm, (0.012, 0.98, 0.62), tf((x, 1.085, 1.645), (0, 0, 0)))
    bm_box(bm, (0.012, 0.10, 0.62), tf((x, 1.60, 1.63)))
    bm_box(bm, (0.012, 0.36, 0.48), tf((sx * 0.27, -2.322, 1.64), (0, 0, math.radians(90))))
bm_box(bm, (2 * HW - 0.16, 0.05, 0.06), tf((0, 1.30, 2.03), (math.radians(-33), 0, 0)))
bm_finish(bm, "WindowFrames", M_TRIM, root, math.radians(35))

# --- door shut lines and handles --------------------------------------------
bm = bmesh.new()
for sx in (1, -1):
    x = sx * (HW + 0.003)
    # cab door outline
    bm_box(bm, (0.010, 0.020, 1.10), tf((x, 1.62, 1.30)))
    bm_box(bm, (0.010, 0.020, 1.10), tf((x, 0.52, 1.30)))
    bm_box(bm, (0.010, 1.12, 0.020), tf((x, 1.07, 0.77)))
    # sliding cargo door
    bm_box(bm, (0.010, 0.020, 1.35), tf((x, 0.42, 1.32)))
    bm_box(bm, (0.010, 0.020, 1.35), tf((x, -0.98, 1.32)))
    bm_box(bm, (0.010, 1.42, 0.020), tf((x, -0.28, 0.66)))
    bm_box(bm, (0.014, 1.42, 0.030), tf((x, -0.28, 1.30)))     # slider track
    bm_box(bm, (0.010, 1.42, 0.020), tf((x, -0.28, 1.99)))
for sx in (1, -1):
    bm_box(bm, (0.010, 0.020, 1.72), tf((sx * 0.008, -2.327, 1.24)))
bm_box(bm, (0.90, 0.010, 0.020), tf((0, -2.327, 0.40)))
bm_finish(bm, "PanelLines", M_TRIM, root, math.radians(35))

bm = bmesh.new()
for sx in (1, -1):
    bm_box(bm, (0.030, 0.17, 0.045), tf((sx * (HW + 0.020), 0.70, 1.24)),
           bevel=0.010, segments=3)
    bm_box(bm, (0.030, 0.17, 0.045), tf((sx * (HW + 0.020), -0.86, 1.16)),
           bevel=0.010, segments=3)
bm_box(bm, (0.16, 0.035, 0.045), tf((0.30, -2.35, 1.10)), bevel=0.010, segments=3)
bm_finish(bm, "Handles", M_CHROME, root, math.radians(35))

# --- bumpers, grille, lamps --------------------------------------------------
bm = bmesh.new()
bm_box(bm, (2 * HW + 0.04, 0.22, 0.30), tf((0, 2.40, 0.56)), bevel=0.045, segments=3)
bm_box(bm, (2 * HW + 0.02, 0.20, 0.28), tf((0, -2.38, 0.54)), bevel=0.045, segments=3)
bm_box(bm, (2 * HW - 0.10, 0.10, 0.030), tf((0, -2.44, 0.42)), bevel=0.010, segments=2)
bm_finish(bm, "Bumpers", M_TRIM, root, math.radians(35))

bm = bmesh.new()
bm_box(bm, (1.30, 0.10, 0.30), tf((0, 2.40, 0.95)), bevel=0.025, segments=2)
for k in range(4):
    bm_box(bm, (1.24, 0.06, 0.035), tf((0, 2.45, 0.85 + k * 0.075)), bevel=0.010, segments=2)
bm_finish(bm, "Grille", M_TRIM, root, math.radians(35))

bm = bmesh.new()
for sx in (1, -1):
    bm_box(bm, (0.46, 0.10, 0.26), tf((sx * 0.60, 2.415, 0.98), (0, 0, math.radians(-sx * 3))),
           bevel=0.030, segments=3)
bm_finish(bm, "Headlights", M_HEAD, root, math.radians(35))

bm = bmesh.new()
for sx in (1, -1):
    bm_box(bm, (0.16, 0.09, 0.62), tf((sx * (HW - 0.13), -2.37, 1.00)), bevel=0.028, segments=3)
bm_finish(bm, "Taillights", M_TAIL, root, math.radians(35))

bm = bmesh.new()
bm_box(bm, (0.34, 0.014, 0.16), tf((-0.34, -2.395, 0.72)), bevel=0.006, segments=2)
bm_box(bm, (0.34, 0.014, 0.16), tf((0, 2.51, 0.60)), bevel=0.006, segments=2)
bm_finish(bm, "Plates", M_PLATE, root, math.radians(35))

# --- mirrors, wipers, roof detail -------------------------------------------
bm = bmesh.new()
for sx in (1, -1):
    bm_box(bm, (0.16, 0.05, 0.05), tf((sx * (HW + 0.09), 1.60, 1.74)), bevel=0.012, segments=2)
    bm_box(bm, (0.06, 0.10, 0.30), tf((sx * (HW + 0.20), 1.62, 1.66)), bevel=0.022, segments=3)
    bm_box(bm, (0.030, 0.55, 0.020), tf((sx * 0.42, 1.82, 1.24), (0, 0, math.radians(sx * 8))))
bm_finish(bm, "MirrorsWipers", M_TRIM, root, math.radians(35))

bm = bmesh.new()
for sx in (1, -1):
    bm_box(bm, (0.06, 3.10, 0.07), tf((sx * (HW - 0.16), -0.45, 2.25)), bevel=0.018, segments=2)
bm_box(bm, (0.42, 0.42, 0.10), tf((0, -1.30, 2.26)), bevel=0.025, segments=3)
bm_finish(bm, "RoofRails", M_TRIM, root, math.radians(35))

# --- side livery panel -------------------------------------------------------
bm = bmesh.new()
for sx in (1, -1):
    bm_box(bm, (0.012, 3.00, 0.34), tf((sx * (HW + 0.006), -0.55, 0.86)))
bm_box(bm, (2 * HW - 0.06, 0.012, 0.34), tf((0, -2.336, 0.80)))
bm_finish(bm, "Livery", M_ACCENT, root, math.radians(35))


# --- wheels ------------------------------------------------------------------
def make_wheel(name, x, y):
    sgn = 1.0 if x > 0 else -1.0
    Mx = tf((x, y, WHEEL_R), (0, math.radians(90), 0))
    bm = bmesh.new()
    bm_cyl(bm, WHEEL_R, 0.235, Mx, segs=48, bevel=0.055, bsegs=4)
    for k in range(44):
        a = 2 * math.pi * k / 44.0
        bm_box(bm, (0.030, 0.19, 0.030),
               tf((x, y + (WHEEL_R - 0.010) * math.cos(a),
                   WHEEL_R + (WHEEL_R - 0.010) * math.sin(a)),
                  (a + math.radians(15), 0, 0)))
    bm_finish(bm, name + ".Tire", M_RUBBER, root, math.radians(38))

    bm = bmesh.new()
    bm_cyl(bm, WHEEL_R * 0.66, 0.20, Mx, segs=32, bevel=0.012)
    bm_cyl(bm, WHEEL_R * 0.60, 0.035, tf((x + sgn * 0.098, y, WHEEL_R),
                                         (0, math.radians(90), 0)), segs=32, bevel=0.010)
    bm_cyl(bm, 0.075, 0.05, tf((x + sgn * 0.118, y, WHEEL_R),
                               (0, math.radians(90), 0)), segs=20, bevel=0.010)
    for k in range(5):
        a = 2 * math.pi * k / 5.0 + 0.3
        bm_box(bm, (0.030, 0.075, 0.20),
               tf((x + sgn * 0.100, y + 0.135 * math.cos(a), WHEEL_R + 0.135 * math.sin(a)),
                  (a + math.radians(90), 0, 0)), bevel=0.012, segments=2)
        bm_cyl(bm, 0.016, 0.030,
               tf((x + sgn * 0.135, y + 0.070 * math.cos(a), WHEEL_R + 0.070 * math.sin(a)),
                  (0, math.radians(90), 0)), segs=6)
    bm_finish(bm, name + ".Rim", M_RIM, root, math.radians(35))


for sx in (1, -1):
    make_wheel("WheelF.%d" % sx, sx * 0.815, AX_F)
    make_wheel("WheelR.%d" % sx, sx * 0.815, AX_R)

# --- underbody ---------------------------------------------------------------
bm = bmesh.new()
bm_box(bm, (1.20, 4.30, 0.14), tf((0, -0.05, 0.30)), bevel=0.02, segments=2)
bm_cyl(bm, 0.055, 1.55, tf((0, AX_R, WHEEL_R), (0, math.radians(90), 0)), segs=16)
bm_cyl(bm, 0.185, 0.34, tf((0, AX_R, WHEEL_R), (0, math.radians(90), 0)), segs=24, bevel=0.02)
bm_cyl(bm, 0.045, 2.30, tf((0.30, 0.40, 0.30), (math.radians(90), 0, 0)), segs=16)
bm_cyl(bm, 0.055, 0.22, tf((0.30, -2.24, 0.34), (math.radians(70), 0, 0)), segs=16)
bm_finish(bm, "Underbody", M_TRIM, root, math.radians(35))

# --- road --------------------------------------------------------------------
bm = bmesh.new()
bm_box(bm, (60.0, 60.0, 0.2), tf((0, 0, -0.1)))
bm_finish(bm, "Road", M_ROAD)

root.rotation_euler = (0, 0, math.radians(24))

# --- lighting and camera -----------------------------------------------------
add_light("Sun", 'SUN', 4.2, (7.0, -9.0, 11.0), (0, 0, 1.0))
add_light("Key", 'AREA', 2200.0, (6.0, -6.5, 5.5), (0, 0, 1.1), size=5.0)
add_light("Fill", 'AREA', 600.0, (-7.0, -4.0, 3.4), (0, 0, 1.1), size=8.0)
add_light("Rim", 'AREA', 900.0, (-3.0, 7.0, 4.0), (0, 0, 1.4), size=4.0)

cd = bpy.data.cameras.new("Camera")
cd.lens = 55.0
cd.clip_start = 0.05
cd.clip_end = 800.0
cam = bpy.data.objects.new("Camera", cd)
link(cam)
cam.location = (6.4, -7.6, 3.05)
cam.rotation_euler = (Vector((0, 0.1, 1.05)) - cam.location).to_track_quat('-Z', 'Y').to_euler()
scene.camera = cam
