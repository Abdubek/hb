"""claude-113 - Procedural brick wall: staggered courses, an interlocking corner return
and a window opening with sill and lintel.

Plan is an L: run A along +X, run B along +Y, meeting at the origin.  Alternate courses
swap which run owns the corner block, producing a proper quoin interlock.  Bricks are
clipped against rectangular voids (window, sill bed, lintel bed) so jambs stay clean.
"""

import bpy
import bmesh
import math
import random
from mathutils import Vector, Matrix, Euler

random.seed(11)

# --------------------------------------------------------------- parameters
BL = 0.215            # brick length
BH = 0.065            # brick height
BT = 0.1025           # brick thickness (wall depth)
J = 0.010             # mortar joint
CH = BH + J           # course height
N_COURSES = 26
LA = 3.20             # length of run A (along X)
LB = 1.70             # length of run B (along Y)
WALL_TOP = N_COURSES * CH

WX0, WX1 = 1.00, 2.00
WZ0, WZ1 = 0.60, 1.50

VOIDS = [
    (WX0, WX1, WZ0, WZ1),                          # window opening
    (WX0 - 0.09, WX1 + 0.09, WZ0 - 0.075, WZ0),    # sill bed
    (WX0 - 0.11, WX1 + 0.11, WZ1, WZ1 + 0.15),     # lintel bed
]


# --------------------------------------------------------------- utilities
def reset_scene():
    bpy.ops.wm.read_factory_settings(use_empty=True)
    bpy.context.scene.unit_settings.system = 'METRIC'


def make_material(name, color, metallic=0.0, rough=0.6, transmission=0.0):
    m = bpy.data.materials.new(name)
    m.use_nodes = True
    p = m.node_tree.nodes["Principled BSDF"]
    p.inputs["Base Color"].default_value = (color[0], color[1], color[2], 1.0)
    p.inputs["Metallic"].default_value = metallic
    p.inputs["Roughness"].default_value = rough
    if transmission > 0.0:
        try:
            p.inputs["Transmission Weight"].default_value = transmission
        except KeyError:
            pass
        m.blend_method = 'BLEND'
    return m


def new_object(name, verts, faces, mats=(), face_mats=None):
    me = bpy.data.meshes.new(name)
    me.from_pydata(verts, [], faces)
    me.validate()
    me.update()
    for m in mats:
        me.materials.append(m)
    if face_mats is not None:
        for poly, idx in zip(me.polygons, face_mats):
            poly.material_index = idx
    ob = bpy.data.objects.new(name, me)
    bpy.context.collection.objects.link(ob)
    return ob


def recalc_normals(ob):
    bm = bmesh.new()
    bm.from_mesh(ob.data)
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    bm.to_mesh(ob.data)
    bm.free()
    ob.data.update()


BOX_FACES = ((0, 1, 3, 2), (4, 6, 7, 5), (0, 4, 5, 1),
             (2, 3, 7, 6), (0, 2, 6, 4), (1, 5, 7, 3))


def add_box(verts, faces, center, size, rot=(0.0, 0.0, 0.0)):
    mtx = Matrix.Translation(Vector(center)) @ Euler(rot, 'XYZ').to_matrix().to_4x4()
    sx, sy, sz = size
    off = len(verts)
    for dx in (-0.5, 0.5):
        for dy in (-0.5, 0.5):
            for dz in (-0.5, 0.5):
                verts.append(tuple(mtx @ Vector((dx * sx, dy * sy, dz * sz))))
    for f in BOX_FACES:
        faces.append(tuple(off + i for i in f))
    return 6


def clip_span(a, b, z0, z1, voids):
    """Clip a horizontal brick span against rectangular voids in the wall plane."""
    spans = [(a, b)]
    for (vx0, vx1, vz0, vz1) in voids:
        if z1 <= vz0 + 1e-6 or z0 >= vz1 - 1e-6:
            continue
        out = []
        for (p, q) in spans:
            if q <= vx0 + 1e-6 or p >= vx1 - 1e-6:
                out.append((p, q))
                continue
            if p < vx0:
                out.append((p, min(q, vx0)))
            if q > vx1:
                out.append((max(p, vx1), q))
        spans = out
    return [(p, q) for (p, q) in spans if q - p > 0.045]


def course_spans(start, end, course):
    """Stretcher bond: half-brick lead-in on odd courses, end bricks cut to fit."""
    out = []
    pos = start
    first = True
    while pos < end - 1e-6:
        length = BL * 0.5 if (first and course % 2 == 1) else BL
        length = min(length, end - pos)
        if length > 0.045:
            out.append((pos, pos + length))
        pos += length + J
        first = False
    return out


# --------------------------------------------------------------- scene
reset_scene()

brick_mats = [
    make_material("Brick A", (0.44, 0.16, 0.11), rough=0.72),
    make_material("Brick B", (0.36, 0.14, 0.10), rough=0.78),
    make_material("Brick C", (0.52, 0.24, 0.15), rough=0.66),
    make_material("Brick D", (0.30, 0.15, 0.13), rough=0.80),
]
mat_mortar = make_material("Mortar", (0.58, 0.56, 0.52), rough=0.90)
mat_stone = make_material("Cast Stone", (0.68, 0.66, 0.60), rough=0.55)
mat_frame = make_material("Window Frame", (0.16, 0.17, 0.18), metallic=0.4, rough=0.42)
mat_glass = make_material("Glazing", (0.55, 0.62, 0.68), rough=0.05, transmission=0.95)
mat_ground = make_material("Ground", (0.22, 0.21, 0.17), rough=0.92)
mat_interior = make_material("Interior", (0.10, 0.10, 0.11), rough=0.85)

verts, faces, face_mats = [], [], []
n_bricks = 0

for c in range(N_COURSES):
    z0 = c * CH
    z1 = z0 + BH
    zc = z0 + BH * 0.5
    even = (c % 2 == 0)

    # run A along +X ; run B along +Y ; the corner block alternates between them
    a_start = 0.0 if even else BT
    b_start = BT if even else 0.0

    for (sa, sb) in course_spans(a_start, LA, c):
        for (p, q) in clip_span(sa, sb, z0, z1, VOIDS):
            jit = (random.uniform(-0.0018, 0.0018), random.uniform(-0.0025, 0.0025),
                   random.uniform(-0.006, 0.006))
            rot = (random.uniform(-0.006, 0.006), random.uniform(-0.008, 0.008),
                   random.uniform(-0.005, 0.005))
            n = add_box(verts, faces,
                        ((p + q) * 0.5 + jit[0], BT * 0.5 + jit[1], zc + jit[2] * 0.4),
                        (q - p, BT, BH), rot)
            face_mats.extend([random.randrange(len(brick_mats))] * n)
            n_bricks += 1

    for (sa, sb) in course_spans(b_start, LB, c):
        jit = (random.uniform(-0.0025, 0.0025), random.uniform(-0.0018, 0.0018),
               random.uniform(-0.006, 0.006))
        rot = (random.uniform(-0.008, 0.008), random.uniform(-0.006, 0.006),
               random.uniform(-0.005, 0.005))
        n = add_box(verts, faces,
                    (BT * 0.5 + jit[0], (sa + sb) * 0.5 + jit[1], zc + jit[2] * 0.4),
                    (BT, sb - sa, BH), rot)
        face_mats.extend([random.randrange(len(brick_mats))] * n)
        n_bricks += 1

# soldier course on end, capping both runs
z_sol = WALL_TOP + BL * 0.5
pos = 0.0
while pos < LA - 1e-6:
    w = min(BH, LA - pos)
    if w > 0.03:
        n = add_box(verts, faces, (pos + w * 0.5, BT * 0.5, z_sol), (w, BT, BL),
                    (0.0, 0.0, random.uniform(-0.004, 0.004)))
        face_mats.extend([random.randrange(len(brick_mats))] * n)
        n_bricks += 1
    pos += w + J
pos = BT + J
while pos < LB - 1e-6:
    w = min(BH, LB - pos)
    if w > 0.03:
        n = add_box(verts, faces, (BT * 0.5, pos + w * 0.5, z_sol), (BT, w, BL),
                    (0.0, 0.0, random.uniform(-0.004, 0.004)))
        face_mats.extend([random.randrange(len(brick_mats))] * n)
        n_bricks += 1
    pos += w + J

bricks = new_object("Brickwork", verts, faces, brick_mats, face_mats)
recalc_normals(bricks)
bev = bricks.modifiers.new("Bevel", 'BEVEL')
bev.width = 0.0035
bev.segments = 2
bev.limit_method = 'ANGLE'
bev.angle_limit = math.radians(35.0)

# --- mortar backing slabs, recessed behind the brick faces ------------------
v, f = [], []
add_box(v, f, (LA * 0.5, BT * 0.5, WALL_TOP * 0.5),
        (LA - 0.02, BT - 0.026, WALL_TOP - 0.01))
add_box(v, f, (BT * 0.5, (BT + LB) * 0.5, WALL_TOP * 0.5),
        (BT - 0.026, LB - BT - 0.02, WALL_TOP - 0.01))
mortar = new_object("Mortar_Core", v, f, [mat_mortar])
recalc_normals(mortar)

# --- sill, lintel and window reveal ---------------------------------------
v, f = [], []
add_box(v, f, ((WX0 + WX1) * 0.5, BT * 0.5 - 0.018, WZ0 - 0.037),
        (WX1 - WX0 + 0.18, BT + 0.055, 0.075), (math.radians(-3.0), 0.0, 0.0))
add_box(v, f, ((WX0 + WX1) * 0.5, BT * 0.5, WZ1 + 0.075),
        (WX1 - WX0 + 0.22, BT, 0.15))
stone = new_object("Sill_Lintel", v, f, [mat_stone])
recalc_normals(stone)
bev = stone.modifiers.new("Bevel", 'BEVEL')
bev.width = 0.006
bev.segments = 2

v, f = [], []
fw, fd = 0.055, 0.07
add_box(v, f, (WX0 + fw * 0.5, fd * 0.6, (WZ0 + WZ1) * 0.5), (fw, fd, WZ1 - WZ0))
add_box(v, f, (WX1 - fw * 0.5, fd * 0.6, (WZ0 + WZ1) * 0.5), (fw, fd, WZ1 - WZ0))
add_box(v, f, ((WX0 + WX1) * 0.5, fd * 0.6, WZ1 - fw * 0.5),
        (WX1 - WX0 - 2.0 * fw, fd, fw))
add_box(v, f, ((WX0 + WX1) * 0.5, fd * 0.6, WZ0 + fw * 0.5),
        (WX1 - WX0 - 2.0 * fw, fd, fw))
add_box(v, f, ((WX0 + WX1) * 0.5, fd * 0.6, (WZ0 + WZ1) * 0.5),
        (0.035, fd * 0.8, WZ1 - WZ0 - 2.0 * fw))          # centre mullion
win = new_object("Window_Frame", v, f, [mat_frame])
recalc_normals(win)

for i, (gx0, gx1) in enumerate((((WX0 + fw), (WX0 + WX1) * 0.5 - 0.018),
                                (((WX0 + WX1) * 0.5 + 0.018), WX1 - fw))):
    y = fd * 0.6
    new_object("Glazing_%d" % i,
               [(gx0, y, WZ0 + fw), (gx1, y, WZ0 + fw),
                (gx1, y, WZ1 - fw), (gx0, y, WZ1 - fw)],
               [(0, 1, 2, 3)], [mat_glass])

# dark interior card seen through the opening
new_object("Interior_Card",
           [(WX0 - 0.3, BT + 0.9, 0.0), (WX1 + 0.3, BT + 0.9, 0.0),
            (WX1 + 0.3, BT + 0.9, WALL_TOP), (WX0 - 0.3, BT + 0.9, WALL_TOP)],
           [(0, 1, 2, 3)], [mat_interior])

# --- footing and ground ---------------------------------------------------
v, f = [], []
add_box(v, f, (LA * 0.5 - 0.05, BT * 0.5, -0.07), (LA + 0.14, BT + 0.10, 0.14))
add_box(v, f, (BT * 0.5, LB * 0.5, -0.07), (BT + 0.10, LB + 0.14, 0.14))
footing = new_object("Footing", v, f, [mat_stone])
recalc_normals(footing)

new_object("Ground", [(-6.0, -6.0, -0.14), (8.0, -6.0, -0.14),
                      (8.0, 8.0, -0.14), (-6.0, 8.0, -0.14)],
           [(0, 1, 2, 3)], [mat_ground])

# --------------------------------------------------------------- lights
sun = bpy.data.lights.new("Sun", 'SUN')
sun.energy = 4.0
sun.angle = math.radians(1.8)
sun.color = (1.0, 0.94, 0.84)
sun_ob = bpy.data.objects.new("Sun", sun)
bpy.context.collection.objects.link(sun_ob)
sun_ob.rotation_euler = (math.radians(56.0), math.radians(6.0), math.radians(-52.0))

sky = bpy.data.lights.new("SkyFill", 'AREA')
sky.size = 8.0
sky.energy = 420.0
sky.color = (0.72, 0.82, 1.0)
sky_ob = bpy.data.objects.new("SkyFill", sky)
bpy.context.collection.objects.link(sky_ob)
sky_ob.location = (1.0, -4.5, 4.5)
sky_ob.rotation_euler = (Vector((1.0, 0.4, 0.9)) - Vector(sky_ob.location)).to_track_quat('-Z', 'Y').to_euler()

world = bpy.data.worlds.new("World")
world.use_nodes = True
bg = world.node_tree.nodes["Background"]
bg.inputs[0].default_value = (0.30, 0.42, 0.60, 1.0)
bg.inputs[1].default_value = 0.7
bpy.context.scene.world = world

# --------------------------------------------------------------- camera
cam_data = bpy.data.cameras.new("Camera")
cam_data.lens = 40.0
cam = bpy.data.objects.new("Camera", cam_data)
bpy.context.collection.objects.link(cam)
cam.location = (-2.5, -3.2, 1.75)
cam.rotation_euler = (Vector((1.15, 0.3, 0.95)) - Vector(cam.location)).to_track_quat('-Z', 'Y').to_euler()
bpy.context.scene.camera = cam

print("claude-113: %d bricks in %d courses" % (n_bricks, N_COURSES))
