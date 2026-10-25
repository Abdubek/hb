"""Blender 4.5 LTS - modern LED streetlight standing on a square paved base."""
import bpy, bmesh, math, random
from mathutils import Vector


# ----------------------------------------------------------------- helpers
def reset_scene():
    bpy.ops.wm.read_factory_settings(use_empty=True)
    scene = bpy.context.scene
    for engine in ("BLENDER_EEVEE_NEXT", "BLENDER_EEVEE", "CYCLES"):
        try:
            scene.render.engine = engine
            break
        except TypeError:
            continue
    world = bpy.data.worlds.new("World")
    world.use_nodes = True
    scene.world = world
    return scene


def world_color(color, strength=1.0):
    bg = bpy.context.scene.world.node_tree.nodes["Background"]
    bg.inputs[0].default_value = (color[0], color[1], color[2], 1.0)
    bg.inputs[1].default_value = strength


def mkmat(name, color, rough=0.5, metal=0.0, emit=None, emit_power=0.0, alpha=1.0):
    mat = bpy.data.materials.new(name)
    mat.use_nodes = True
    b = mat.node_tree.nodes["Principled BSDF"]
    b.inputs["Base Color"].default_value = (color[0], color[1], color[2], 1.0)
    b.inputs["Roughness"].default_value = rough
    b.inputs["Metallic"].default_value = metal
    if emit is not None:
        for key in ("Emission Color", "Emission"):
            if key in b.inputs:
                b.inputs[key].default_value = (emit[0], emit[1], emit[2], 1.0)
                break
        if "Emission Strength" in b.inputs:
            b.inputs["Emission Strength"].default_value = emit_power
    if alpha < 1.0:
        b.inputs["Alpha"].default_value = alpha
        try:
            mat.blend_method = 'BLEND'
        except TypeError:
            mat.blend_method = 'HASHED'
    return mat


def link(ob):
    bpy.context.scene.collection.objects.link(ob)
    return ob


def _finish(name, bm, mat, loc, rot, smooth, parent, scale=(1.0, 1.0, 1.0)):
    if smooth:
        for f in bm.faces:
            f.smooth = True
        for e in bm.edges:
            if e.calc_face_angle(0.0) > 0.62:
                e.smooth = False
    me = bpy.data.meshes.new(name)
    bm.to_mesh(me)
    bm.free()
    if mat is not None:
        me.materials.append(mat)
    ob = bpy.data.objects.new(name, me)
    ob.location = loc
    ob.rotation_euler = rot
    ob.scale = scale
    if parent is not None:
        ob.parent = parent
    return link(ob)


def box(name, size, loc=(0, 0, 0), rot=(0, 0, 0), mat=None, shift=(0, 0, 0), parent=None):
    bm = bmesh.new()
    bmesh.ops.create_cube(bm, size=1.0)
    bmesh.ops.scale(bm, vec=Vector(size), verts=bm.verts)
    if any(shift):
        bmesh.ops.translate(bm, verts=bm.verts, vec=Vector(shift))
    return _finish(name, bm, mat, loc, rot, False, parent)


def bevel_box(name, size, loc=(0, 0, 0), rot=(0, 0, 0), mat=None, amount=0.01, parent=None):
    bm = bmesh.new()
    bmesh.ops.create_cube(bm, size=1.0)
    bmesh.ops.scale(bm, vec=Vector(size), verts=bm.verts)
    bmesh.ops.bevel(bm, geom=list(bm.verts) + list(bm.edges) + list(bm.faces),
                    offset=amount, segments=2, affect='EDGES', profile=0.5,
                    clamp_overlap=True)
    return _finish(name, bm, mat, loc, rot, False, parent)


def cylinder(name, radius, depth, loc=(0, 0, 0), rot=(0, 0, 0), mat=None,
             segments=24, radius_top=None, cap=True, parent=None):
    bm = bmesh.new()
    bmesh.ops.create_cone(bm, cap_ends=cap, cap_tris=False, segments=segments,
                          radius1=radius,
                          radius2=(radius if radius_top is None else radius_top),
                          depth=depth)
    return _finish(name, bm, mat, loc, rot, True, parent)


def tube(name, points, radius, mat=None, cyclic=False, res=6, parent=None, caps=True):
    cu = bpy.data.curves.new(name, 'CURVE')
    cu.dimensions = '3D'
    sp = cu.splines.new('POLY')
    sp.points.add(len(points) - 1)
    for i, p in enumerate(points):
        sp.points[i].co = (p[0], p[1], p[2], 1.0)
    sp.use_cyclic_u = cyclic
    sp.use_smooth = True
    cu.bevel_depth = radius
    cu.bevel_resolution = res
    cu.fill_caps = caps
    if mat is not None:
        cu.materials.append(mat)
    ob = bpy.data.objects.new(name, cu)
    if parent is not None:
        ob.parent = parent
    return link(ob)


def arc_points(center, radius, a0, a1, n, plane='XZ'):
    pts = []
    for i in range(n + 1):
        a = a0 + (a1 - a0) * i / float(n)
        c, s = math.cos(a), math.sin(a)
        if plane == 'XZ':
            pts.append((center[0] + radius * c, center[1], center[2] + radius * s))
        elif plane == 'YZ':
            pts.append((center[0], center[1] + radius * c, center[2] + radius * s))
        else:
            pts.append((center[0] + radius * c, center[1] + radius * s, center[2]))
    return pts


def add_camera(loc, target, lens=35.0):
    cam = bpy.data.cameras.new("Camera")
    cam.lens = lens
    ob = bpy.data.objects.new("Camera", cam)
    ob.location = loc
    ob.rotation_euler = (Vector(target) - Vector(loc)).to_track_quat('-Z', 'Y').to_euler()
    link(ob)
    bpy.context.scene.camera = ob
    return ob


def add_light(name, ltype, loc, energy, color=(1, 1, 1), size=0.5, size_y=None,
              target=None, spot_size=1.2, spot_blend=0.35):
    lt = bpy.data.lights.new(name, ltype)
    lt.energy = energy
    lt.color = color
    if ltype == 'AREA':
        lt.size = size
        if size_y is not None:
            lt.shape = 'RECTANGLE'
            lt.size_y = size_y
    elif ltype in ('POINT', 'SPOT'):
        lt.shadow_soft_size = size
    if ltype == 'SPOT':
        lt.spot_size = spot_size
        lt.spot_blend = spot_blend
    ob = bpy.data.objects.new(name, lt)
    ob.location = loc
    if target is not None:
        ob.rotation_euler = (Vector(target) - Vector(loc)).to_track_quat('-Z', 'Y').to_euler()
    return link(ob)


# ------------------------------------------------------------------- scene
reset_scene()
world_color((0.020, 0.028, 0.055), 1.0)      # dusk sky
random.seed(3)

m_road = mkmat("Asphalt", (0.055, 0.055, 0.062), rough=0.88)
m_paver_a = mkmat("Paver Light", (0.56, 0.55, 0.52), rough=0.82)
m_paver_b = mkmat("Paver Dark", (0.44, 0.43, 0.41), rough=0.85)
m_kerb = mkmat("Kerb Stone", (0.50, 0.49, 0.47), rough=0.8)
m_pole = mkmat("Anthracite Pole", (0.075, 0.078, 0.085), rough=0.34, metal=0.55)
m_alu = mkmat("Anodised Alu", (0.42, 0.43, 0.45), rough=0.30, metal=0.9)
m_bolt = mkmat("Bolt Steel", (0.55, 0.55, 0.57), rough=0.35, metal=1.0)
m_lens = mkmat("LED Lens", (0.92, 0.94, 1.0), rough=0.12,
               emit=(1.0, 0.90, 0.74), emit_power=26.0)
m_glow = mkmat("LED Cell", (1.0, 0.95, 0.85), rough=0.1,
               emit=(1.0, 0.93, 0.80), emit_power=48.0)

# ---- ground, paved square, kerb -----------------------------------------
box("Ground", (40.0, 40.0, 0.40), (0, 0, -0.20), mat=m_road)
box("SubBase", (3.30, 3.30, 0.10), (0, 0, 0.05), mat=m_kerb)

PAV, N = 3.0, 6                    # 3 m square of 6 x 6 pavers
CELL = PAV / N
for i in range(N):
    for j in range(N):
        cx = -PAV / 2 + CELL * (i + 0.5)
        cy = -PAV / 2 + CELL * (j + 0.5)
        mat = m_paver_a if (i + j) % 2 == 0 else m_paver_b
        h = 0.10 + random.uniform(-0.002, 0.002)
        bevel_box("Paver_%d_%d" % (i, j), (CELL - 0.02, CELL - 0.02, h),
                  (cx, cy, 0.10 + h / 2 - 0.05), mat=mat, amount=0.006)

for sx, sy, sizex, sizey in ((0, PAV / 2 + 0.13, PAV + 0.52, 0.16),
                             (0, -PAV / 2 - 0.13, PAV + 0.52, 0.16),
                             (PAV / 2 + 0.13, 0, 0.16, PAV + 0.52),
                             (-PAV / 2 - 0.13, 0, 0.16, PAV + 0.52)):
    bevel_box("Kerb", (sizex, sizey, 0.24), (sx, sy, 0.06), mat=m_kerb, amount=0.012)

TOP = 0.15                          # finished pavement level

# ---- foundation and pole -------------------------------------------------
bevel_box("BasePlate", (0.42, 0.42, 0.045), (0, 0, TOP + 0.022), mat=m_pole, amount=0.006)
for bx in (-0.15, 0.15):
    for by in (-0.15, 0.15):
        cylinder("AnchorBolt", 0.013, 0.055, (bx, by, TOP + 0.06), mat=m_bolt, segments=10)
        cylinder("AnchorNut", 0.019, 0.018, (bx, by, TOP + 0.055), mat=m_bolt, segments=6)
cylinder("BaseShroud", 0.155, 0.32, (0, 0, TOP + 0.205), mat=m_pole, segments=32,
         radius_top=0.108)

POLE_BOT = TOP + 0.30
POLE_H = 5.95
POLE_TOP = POLE_BOT + POLE_H
cylinder("Pole", 0.098, POLE_H, (0, 0, POLE_BOT + POLE_H / 2), mat=m_pole,
         segments=32, radius_top=0.058)
box("AccessHatch", (0.014, 0.13, 0.36), (0.092, 0.0, TOP + 0.95), mat=m_alu)
cylinder("HatchScrew", 0.008, 0.012, (0.098, 0.0, TOP + 1.12),
         rot=(0, math.pi / 2, 0), mat=m_bolt, segments=8)

# ---- curved outreach arm -------------------------------------------------
bend = arc_points((0.70, 0.0, POLE_TOP - 0.10), 0.70, math.pi, math.pi / 2, 16, 'XZ')
arm_pts = [(0.0, 0.0, POLE_TOP - 0.60)] + bend + [(1.95, 0.0, POLE_TOP + 0.60)]
tube("Arm", arm_pts, 0.055, m_pole, res=6)
cylinder("ArmCollar", 0.075, 0.10, (0, 0, POLE_TOP - 0.55), mat=m_alu, segments=24)

LUM_X = 2.30
LUM_Z = POLE_TOP + 0.60

# ---- luminaire head ------------------------------------------------------
bevel_box("LuminaireBody", (0.80, 0.32, 0.085), (LUM_X, 0.0, LUM_Z),
          rot=(0, math.radians(3.0), 0), mat=m_alu, amount=0.012)
bevel_box("LuminaireCap", (0.62, 0.26, 0.035), (LUM_X, 0.0, LUM_Z + 0.055),
          rot=(0, math.radians(3.0), 0), mat=m_pole, amount=0.008)
for i in range(6):                                        # cooling fins
    box("Fin", (0.012, 0.26, 0.035), (LUM_X - 0.22 + i * 0.09, 0.0, LUM_Z + 0.085),
        rot=(0, math.radians(3.0), 0), mat=m_alu)
box("ArmClamp", (0.18, 0.16, 0.10), (LUM_X - 0.44, 0.0, LUM_Z - 0.01), mat=m_pole)
box("LensPlate", (0.72, 0.26, 0.012), (LUM_X, 0.0, LUM_Z - 0.048),
    rot=(0, math.radians(3.0), 0), mat=m_lens)
for i in range(4):
    for j in range(2):
        box("LedCell", (0.09, 0.09, 0.008),
            (LUM_X - 0.255 + i * 0.17, -0.06 + j * 0.12, LUM_Z - 0.056),
            rot=(0, math.radians(3.0), 0), mat=m_glow)

# small pole-top finial
cylinder("PoleCap", 0.062, 0.05, (0, 0, POLE_TOP + 0.02), mat=m_alu, segments=24,
         radius_top=0.045)

# ---- lighting ------------------------------------------------------------
add_light("StreetLamp", 'AREA', (LUM_X, 0.0, LUM_Z - 0.07), 2600.0, (1.0, 0.90, 0.74),
          size=0.70, size_y=0.24, target=(LUM_X + 0.4, 0.0, 0.0))
add_light("LampSpill", 'SPOT', (LUM_X, 0.0, LUM_Z - 0.10), 900.0, (1.0, 0.92, 0.80),
          size=0.15, target=(LUM_X - 0.6, 0.0, 0.0), spot_size=math.radians(120),
          spot_blend=0.55)
moon = add_light("Moon", 'SUN', (-8.0, -10.0, 12.0), 0.22, (0.55, 0.68, 1.0))
moon.rotation_euler = (Vector((0, 0, 0)) - Vector((-8.0, -10.0, 12.0))).to_track_quat('-Z', 'Y').to_euler()
add_light("SkyFill", 'AREA', (0.0, 6.0, 8.0), 60.0, (0.35, 0.48, 0.85),
          size=12.0, target=(0, 0, 1.0))

# ---- camera --------------------------------------------------------------
add_camera((5.20, -5.00, 1.75), (0.55, 0.0, 4.20), lens=26.0)
