"""Blender 4.5 LTS - bicycle parking rack for five bicycles, on a concrete pad."""
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


def cylinder(name, radius, depth, loc=(0, 0, 0), rot=(0, 0, 0), mat=None,
             segments=20, radius_top=None, cap=True, parent=None):
    bm = bmesh.new()
    bmesh.ops.create_cone(bm, cap_ends=cap, cap_tris=False, segments=segments,
                          radius1=radius,
                          radius2=(radius if radius_top is None else radius_top),
                          depth=depth)
    return _finish(name, bm, mat, loc, rot, True, parent)


def sphere(name, radius, loc=(0, 0, 0), mat=None, u=16, v=8,
           scale=(1.0, 1.0, 1.0), parent=None):
    bm = bmesh.new()
    bmesh.ops.create_uvsphere(bm, u_segments=u, v_segments=v, radius=radius)
    return _finish(name, bm, mat, loc, (0, 0, 0), True, parent, scale)


def tube(name, points, radius, mat=None, cyclic=False, res=4, parent=None, caps=True):
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


def empty(name, loc=(0, 0, 0), rot=(0, 0, 0)):
    ob = bpy.data.objects.new(name, None)
    ob.empty_display_size = 0.3
    ob.location = loc
    ob.rotation_euler = rot
    return link(ob)


def add_camera(loc, target, lens=35.0):
    cam = bpy.data.cameras.new("Camera")
    cam.lens = lens
    ob = bpy.data.objects.new("Camera", cam)
    ob.location = loc
    ob.rotation_euler = (Vector(target) - Vector(loc)).to_track_quat('-Z', 'Y').to_euler()
    link(ob)
    bpy.context.scene.camera = ob
    return ob


def add_light(name, ltype, loc, energy, color=(1, 1, 1), size=0.5, target=None):
    lt = bpy.data.lights.new(name, ltype)
    lt.energy = energy
    lt.color = color
    if ltype == 'AREA':
        lt.size = size
    elif ltype in ('POINT', 'SPOT'):
        lt.shadow_soft_size = size
    ob = bpy.data.objects.new(name, lt)
    ob.location = loc
    if target is not None:
        ob.rotation_euler = (Vector(target) - Vector(loc)).to_track_quat('-Z', 'Y').to_euler()
    return link(ob)


# ------------------------------------------------------------------- scene
reset_scene()
world_color((0.42, 0.55, 0.72), 1.0)
random.seed(4)

m_ground = mkmat("Asphalt", (0.10, 0.10, 0.11), rough=0.92)
m_pad = mkmat("Concrete", (0.62, 0.61, 0.58), rough=0.85)
m_steel = mkmat("Galv Steel", (0.70, 0.71, 0.73), rough=0.28, metal=1.0)
m_dark = mkmat("Dark Steel", (0.13, 0.13, 0.14), rough=0.4, metal=0.8)
m_rubber = mkmat("Tyre Rubber", (0.035, 0.035, 0.04), rough=0.85)
m_chrome = mkmat("Chrome", (0.85, 0.86, 0.88), rough=0.12, metal=1.0)
m_paint_a = mkmat("Frame Teal", (0.05, 0.35, 0.38), rough=0.25)
m_paint_b = mkmat("Frame Red", (0.48, 0.06, 0.07), rough=0.25)
m_saddle = mkmat("Saddle", (0.06, 0.06, 0.07), rough=0.6)
m_grip = mkmat("Grip", (0.12, 0.10, 0.09), rough=0.8)
m_sign = mkmat("Sign Blue", (0.05, 0.20, 0.55), rough=0.35)
m_white = mkmat("Sign White", (0.93, 0.93, 0.92), rough=0.4)

# ---- ground and pad ------------------------------------------------------
box("Ground", (24.0, 24.0, 0.40), (0, 0, -0.32), mat=m_ground)
box("ConcretePad", (3.60, 1.80, 0.12), (0, 0, -0.06), mat=m_pad)
for i in range(5):                                   # expansion joints
    box("PadJoint", (0.012, 1.80, 0.02), (-1.50 + i * 0.75, 0, 0.0), mat=m_dark)

# ---- rack ----------------------------------------------------------------
SLOTS = 5
PITCH = 0.50
DIV_Y = 0.30            # half depth of each wheel divider
RAIL_Y = 0.26
RAIL_Z = 0.06
xs = [(-(SLOTS) * PITCH / 2.0) + i * PITCH for i in range(SLOTS + 1)]

for i, x in enumerate(xs):
    pts = [(x, -DIV_Y, RAIL_Z - 0.02)]
    pts += arc_points((x, 0.0, 0.42), DIV_Y, math.pi, 0.0, 14, plane='YZ')
    pts += [(x, DIV_Y, RAIL_Z - 0.02)]
    tube("Divider%d" % i, pts, 0.022, m_steel, res=4)

for sy in (-RAIL_Y, RAIL_Y):
    tube("BaseRail", [(xs[0] - 0.18, sy, RAIL_Z), (xs[-1] + 0.18, sy, RAIL_Z)],
         0.026, m_steel, res=4)
    for ex in (xs[0] - 0.16, xs[-1] + 0.16):
        box("FootPlate", (0.14, 0.14, 0.02), (ex, sy, 0.01), mat=m_dark)
        cylinder("FootPost", 0.022, 0.06, (ex, sy, 0.035), mat=m_steel, segments=12)
        for bx in (-0.045, 0.045):
            cylinder("Anchor", 0.008, 0.03, (ex + bx, sy, 0.022), mat=m_dark, segments=8)

# stiffening rail joining the divider tops
tube("TopBrace", [(xs[0], 0.0, 0.72), (xs[-1], 0.0, 0.72)], 0.018, m_steel, res=4)


# ---- simplified bicycle --------------------------------------------------
def make_bicycle(name, x_slot, frame_mat, tilt=0.0):
    """Bicycle standing with its front wheel in a rack slot; local +X is forward."""
    root = empty(name, (x_slot, -0.53, 0.0), (0, 0, math.radians(90)))
    root.rotation_euler = (tilt, 0.0, math.radians(90))
    R_TYRE, R_PATH, HUBZ = 0.030, 0.315, 0.345
    hubs = {'rear': -0.53, 'front': 0.53}
    for key, hx in hubs.items():
        tube("%s_Tyre_%s" % (name, key),
             arc_points((hx, 0, HUBZ), R_PATH, 0.0, 2.0 * math.pi, 26, 'XZ')[:-1],
             R_TYRE, m_rubber, cyclic=True, res=3, parent=root)
        tube("%s_Rim_%s" % (name, key),
             arc_points((hx, 0, HUBZ), 0.295, 0.0, 2.0 * math.pi, 26, 'XZ')[:-1],
             0.012, m_chrome, cyclic=True, res=3, parent=root)
        cylinder("%s_Hub_%s" % (name, key), 0.028, 0.09, (hx, 0, HUBZ),
                 rot=(math.pi / 2, 0, 0), mat=m_chrome, segments=12, parent=root)
        for k in range(10):
            a = 2.0 * math.pi * k / 10.0
            cylinder("%s_Spoke" % name, 0.0035, 0.29,
                     (hx + 0.152 * math.cos(a), 0.0, HUBZ + 0.152 * math.sin(a)),
                     rot=(0, math.pi / 2 - a, 0), mat=m_chrome, segments=6, parent=root)
    rear = (-0.53, 0.0, HUBZ)
    bb = (0.02, 0.0, 0.28)
    seat_top = (-0.15, 0.0, 0.88)
    head_top = (0.37, 0.0, 1.00)
    head_bot = (0.45, 0.0, 0.70)
    front = (0.53, 0.0, HUBZ)
    for a, b, tag in ((bb, seat_top, "SeatTube"), (seat_top, head_top, "TopTube"),
                      (bb, head_bot, "DownTube"), (rear, bb, "ChainStay"),
                      (rear, seat_top, "SeatStay"), (head_top, head_bot, "HeadTube"),
                      (head_bot, front, "Fork")):
        tube("%s_%s" % (name, tag), [a, b], 0.021, frame_mat, res=3, parent=root)
    tube("%s_SeatPost" % name, [seat_top, (-0.19, 0.0, 0.98)], 0.014, m_chrome,
         res=3, parent=root)
    box("%s_Saddle" % name, (0.26, 0.10, 0.045), (-0.20, 0.0, 1.00),
        rot=(0, math.radians(-6), 0), mat=m_saddle, parent=root)
    tube("%s_Stem" % name, [head_top, (0.34, 0.0, 1.06)], 0.016, m_chrome, res=3, parent=root)
    tube("%s_Bar" % name, [(0.34, -0.22, 1.06), (0.34, 0.22, 1.06)], 0.014,
         m_chrome, res=3, parent=root)
    for gy in (-0.185, 0.185):
        cylinder("%s_Grip" % name, 0.017, 0.10, (0.34, gy, 1.06),
                 rot=(math.pi / 2, 0, 0), mat=m_grip, segments=10, parent=root)
    cylinder("%s_Crank" % name, 0.018, 0.13, bb, rot=(math.pi / 2, 0, 0),
             mat=m_chrome, segments=12, parent=root)
    for sgn in (1, -1):
        box("%s_CrankArm" % name, (0.17, 0.02, 0.03),
            (bb[0] + sgn * 0.07, sgn * 0.075, bb[2] + sgn * 0.02),
            rot=(0, math.radians(20 * sgn), 0), mat=m_dark, parent=root)
        box("%s_Pedal" % name, (0.09, 0.06, 0.012),
            (bb[0] + sgn * 0.14, sgn * 0.105, bb[2] + sgn * 0.05), mat=m_dark, parent=root)
    tube("%s_Chain" % name, [(rear[0], 0.075, rear[2] - 0.012), (bb[0], 0.075, bb[2] - 0.05)],
         0.007, m_dark, res=2, parent=root)
    tube("%s_ChainTop" % name, [(rear[0], 0.075, rear[2] + 0.012), (bb[0], 0.075, bb[2] + 0.05)],
         0.007, m_dark, res=2, parent=root)
    sphere("%s_Bell" % name, 0.022, (0.34, 0.13, 1.085), mat=m_chrome, parent=root,
           scale=(1.0, 1.0, 0.7))
    return root


make_bicycle("BikeA", (xs[0] + xs[1]) / 2.0, m_paint_a, tilt=math.radians(2.0))
make_bicycle("BikeB", (xs[2] + xs[3]) / 2.0, m_paint_b, tilt=math.radians(-2.5))
make_bicycle("BikeC", (xs[4] + xs[5]) / 2.0, m_dark, tilt=math.radians(1.5))

# ---- information sign ----------------------------------------------------
cylinder("SignPost", 0.032, 2.30, (2.05, 0.60, 1.15), mat=m_steel, segments=16)
box("SignBoard", (0.50, 0.03, 0.50), (2.05, 0.62, 2.05), mat=m_sign)
box("SignBorder", (0.44, 0.01, 0.44), (2.05, 0.598, 2.05), mat=m_white)
box("SignFace", (0.40, 0.01, 0.40), (2.05, 0.594, 2.05), mat=m_sign)
for gx in (-0.11, 0.11):
    tube("SignWheel", arc_points((2.05 + gx, 0.585, 1.99), 0.075, 0.0, 2.0 * math.pi, 20)[:-1],
         0.010, m_white, cyclic=True, res=3)
tube("SignFrame", [(1.94, 0.585, 1.99), (2.02, 0.585, 2.09), (2.16, 0.585, 1.99)],
     0.010, m_white, res=3)
tube("SignBar", [(2.02, 0.585, 2.09), (2.09, 0.585, 2.10)], 0.009, m_white, res=3)

# ---- kerb detail ---------------------------------------------------------
for sy in (-0.96, 0.96):
    box("Kerb", (3.80, 0.12, 0.16), (0, sy, 0.0), mat=m_pad)

# ---- lighting and camera -------------------------------------------------
sun = add_light("Sun", 'SUN', (6.0, -6.0, 8.0), 3.4, (1.0, 0.96, 0.90))
sun.rotation_euler = (Vector((0, 0, 0.4)) - Vector((6.0, -6.0, 8.0))).to_track_quat('-Z', 'Y').to_euler()
sun.data.angle = math.radians(2.5)
add_light("SkyFill", 'AREA', (-3.0, 3.0, 4.0), 300.0, (0.72, 0.82, 1.0),
          size=6.0, target=(0, 0, 0.4))
add_camera((3.30, -3.90, 1.95), (-0.10, -0.55, 0.55), lens=42.0)
