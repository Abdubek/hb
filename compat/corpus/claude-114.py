"""claude-114 - Circular auditorium: tiered seating bowl, radial aisles with handrails,
and a central presentation platform.

The bowl is a single revolved staircase profile; seats are linked duplicates of one seat
mesh, placed on each tier and rotated to face the centre, skipping the aisle sectors.
"""

import bpy
import bmesh
import math
from mathutils import Vector, Matrix

# --------------------------------------------------------------- parameters
R0 = 3.30            # inner radius of the first tier
TREAD = 1.05
RISE = 0.42
N_TIERS = 8
R_MAX = R0 + N_TIERS * TREAD
Z_TOP = N_TIERS * RISE
WALL_H = 3.6
N_AISLES = 4
AISLE_HALF_W = 0.80         # metres, converted to an angle at each radius
SEAT_PITCH = 0.66


# --------------------------------------------------------------- utilities
def reset_scene():
    bpy.ops.wm.read_factory_settings(use_empty=True)
    bpy.context.scene.unit_settings.system = 'METRIC'


def make_material(name, color, metallic=0.0, rough=0.6, emit=None, strength=0.0):
    m = bpy.data.materials.new(name)
    m.use_nodes = True
    p = m.node_tree.nodes["Principled BSDF"]
    p.inputs["Base Color"].default_value = (color[0], color[1], color[2], 1.0)
    p.inputs["Metallic"].default_value = metallic
    p.inputs["Roughness"].default_value = rough
    if emit is not None:
        p.inputs["Emission Color"].default_value = (emit[0], emit[1], emit[2], 1.0)
        p.inputs["Emission Strength"].default_value = strength
    return m


def new_object(name, verts, faces, mats=(), smooth=False):
    me = bpy.data.meshes.new(name)
    me.from_pydata(verts, [], faces)
    me.validate()
    me.update()
    for m in mats:
        me.materials.append(m)
    if smooth:
        for poly in me.polygons:
            poly.use_smooth = True
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


def add_box(verts, faces, center, size, rot_z=0.0):
    mtx = Matrix.Translation(Vector(center)) @ Matrix.Rotation(rot_z, 4, 'Z')
    sx, sy, sz = size
    off = len(verts)
    for dx in (-0.5, 0.5):
        for dy in (-0.5, 0.5):
            for dz in (-0.5, 0.5):
                verts.append(tuple(mtx @ Vector((dx * sx, dy * sy, dz * sz))))
    for f in BOX_FACES:
        faces.append(tuple(off + i for i in f))


def add_beam(verts, faces, p0, p1, w, h, up=(0.0, 0.0, 1.0)):
    p0 = Vector(p0)
    p1 = Vector(p1)
    d = p1 - p0
    if d.length < 1e-9:
        return
    d.normalize()
    side = d.cross(Vector(up))
    if side.length < 1e-6:
        side = d.cross(Vector((1.0, 0.0, 0.0)))
    side.normalize()
    upv = side.cross(d).normalized()
    off = len(verts)
    for base in (p0, p1):
        for s, u in ((-1, -1), (-1, 1), (1, 1), (1, -1)):
            verts.append(tuple(base + side * (s * w * 0.5) + upv * (u * h * 0.5)))
    faces.append((off + 3, off + 2, off + 1, off + 0))
    faces.append((off + 4, off + 5, off + 6, off + 7))
    for i in range(4):
        j = (i + 1) % 4
        faces.append((off + i, off + 4 + i, off + 4 + j, off + j))


def lathe(verts, faces, profile, segments=128):
    off = len(verts)
    n = len(profile)
    for s in range(segments):
        a = 2.0 * math.pi * s / segments
        ca, sa = math.cos(a), math.sin(a)
        for (r, z) in profile:
            verts.append((r * ca, r * sa, z))
    for s in range(segments):
        s2 = (s + 1) % segments
        for i in range(n):
            i2 = (i + 1) % n
            faces.append((off + s * n + i, off + s * n + i2,
                          off + s2 * n + i2, off + s2 * n + i))


def add_cylinder(verts, faces, center, radius, height, segments=32):
    off = len(verts)
    cx, cy, cz = center
    for h in (-0.5, 0.5):
        for s in range(segments):
            a = 2.0 * math.pi * s / segments
            verts.append((cx + radius * math.cos(a), cy + radius * math.sin(a),
                          cz + h * height))
    for s in range(segments):
        s2 = (s + 1) % segments
        faces.append((off + s, off + s2, off + segments + s2, off + segments + s))
    faces.append(tuple(off + segments - 1 - s for s in range(segments)))
    faces.append(tuple(off + segments + s for s in range(segments)))


def add_annulus(verts, faces, r_in, r_out, z, segments=96):
    off = len(verts)
    for s in range(segments):
        a = 2.0 * math.pi * s / segments
        ca, sa = math.cos(a), math.sin(a)
        verts.append((r_in * ca, r_in * sa, z))
        verts.append((r_out * ca, r_out * sa, z))
    for s in range(segments):
        s2 = (s + 1) % segments
        faces.append((off + 2 * s, off + 2 * s + 1, off + 2 * s2 + 1, off + 2 * s2))


# --------------------------------------------------------------- scene
reset_scene()

mat_concrete = make_material("Bowl Concrete", (0.30, 0.29, 0.28), rough=0.72)
mat_carpet = make_material("Aisle Carpet", (0.14, 0.10, 0.12), rough=0.92)
mat_seat = make_material("Seat Fabric", (0.44, 0.08, 0.10), rough=0.85)
mat_seat_frame = make_material("Seat Frame", (0.10, 0.10, 0.11), metallic=0.8, rough=0.36)
mat_rail = make_material("Handrail", (0.68, 0.69, 0.72), metallic=1.0, rough=0.24)
mat_wood = make_material("Platform Oak", (0.42, 0.27, 0.13), rough=0.42)
mat_plaster = make_material("Wall Plaster", (0.52, 0.50, 0.47), rough=0.80)
mat_nose = make_material("Step Nosing", (0.95, 0.85, 0.35), emit=(1.0, 0.86, 0.30),
                         strength=3.0, rough=0.4)
mat_cove = make_material("Cove Light", (1.0, 0.94, 0.85), emit=(1.0, 0.94, 0.85),
                         strength=7.0)
mat_metal = make_material("Rig Steel", (0.20, 0.20, 0.22), metallic=1.0, rough=0.40)
mat_lens = make_material("Lens", (1.0, 0.96, 0.88), emit=(1.0, 0.96, 0.88), strength=18.0)

aisle_angles = [2.0 * math.pi * i / N_AISLES + math.pi / N_AISLES for i in range(N_AISLES)]


def in_aisle(theta, r):
    half = min(AISLE_HALF_W / max(r, 0.5), 0.5)
    for a in aisle_angles:
        d = (theta - a + math.pi) % (2.0 * math.pi) - math.pi
        if abs(d) < half:
            return True
    return False


# --- bowl: revolved staircase profile --------------------------------------
profile = [(0.05, 0.0), (R0, 0.0)]
for i in range(N_TIERS):
    z = i * RISE
    r = R0 + i * TREAD
    profile.append((r, z))
    profile.append((r + TREAD, z))
profile.append((R_MAX, Z_TOP))
profile.append((R_MAX, Z_TOP + WALL_H))
profile.append((R_MAX + 0.45, Z_TOP + WALL_H))
profile.append((R_MAX + 0.45, -0.5))
profile.append((0.05, -0.5))

v, f = [], []
lathe(v, f, profile, segments=144)
bowl = new_object("Seating_Bowl", v, f, [mat_concrete], smooth=True)
recalc_normals(bowl)

# --- aisle carpet strips and step nosings ---------------------------------
v_c, f_c = [], []
v_n, f_n = [], []
for a in aisle_angles:
    for i in range(N_TIERS):
        r0 = R0 + i * TREAD
        r1 = r0 + TREAD
        z = i * RISE
        half = AISLE_HALF_W / ((r0 + r1) * 0.5)
        segs = 6
        off = len(v_c)
        for s in range(segs + 1):
            t = a - half + 2.0 * half * s / segs
            ca, sa = math.cos(t), math.sin(t)
            v_c.append((r0 * ca, r0 * sa, z + 0.004))
            v_c.append((r1 * ca, r1 * sa, z + 0.004))
        for s in range(segs):
            f_c.append((off + 2 * s, off + 2 * s + 1, off + 2 * s + 3, off + 2 * s + 2))
        # nosing bar along the leading edge of each aisle tread
        p0 = Vector((r0 * math.cos(a - half), r0 * math.sin(a - half), z + 0.012))
        p1 = Vector((r0 * math.cos(a + half), r0 * math.sin(a + half), z + 0.012))
        add_beam(v_n, f_n, p0, p1, 0.06, 0.02, up=(0.0, 0.0, 1.0))
carpet = new_object("Aisle_Carpet", v_c, f_c, [mat_carpet])
nosings = new_object("Step_Nosings", v_n, f_n, [mat_nose])
recalc_normals(nosings)

# --- handrails along both sides of every aisle ----------------------------
v, f = [], []
for a in aisle_angles:
    for sgn in (-1.0, 1.0):
        pts = []
        for i in range(N_TIERS + 1):
            r = R0 + i * TREAD
            z = min(i, N_TIERS - 1) * RISE if i < N_TIERS else Z_TOP
            half = (AISLE_HALF_W + 0.06) / max(r, 0.5)
            t = a + sgn * half
            pts.append(Vector((r * math.cos(t), r * math.sin(t), z + 0.98)))
        for i in range(len(pts) - 1):
            add_beam(v, f, pts[i], pts[i + 1], 0.045, 0.045, up=(0.0, 0.0, 1.0))
        for i in range(0, len(pts), 2):
            p = pts[i]
            base = Vector((p.x, p.y, p.z - 0.98))
            add_beam(v, f, base, p, 0.04, 0.04, up=(1.0, 0.0, 0.0))
rails = new_object("Aisle_Handrails", v, f, [mat_rail])
recalc_normals(rails)

# --- one seat, then linked duplicates -------------------------------------
v, f, fm = [], [], []


def seat_part(center, size, mat_idx):
    add_box(v, f, center, size)
    fm.extend([mat_idx] * 6)


seat_part((0.0, 0.02, 0.44), (0.52, 0.48, 0.07), 0)                     # pan
seat_part((0.0, 0.24, 0.70), (0.52, 0.07, 0.52), 0)                     # back
seat_part((0.0, 0.235, 0.98), (0.52, 0.09, 0.05), 1)                    # back cap
for sx in (-0.27, 0.27):
    seat_part((sx, 0.05, 0.60), (0.035, 0.42, 0.36), 1)                 # side frames
    seat_part((sx, -0.06, 0.62), (0.05, 0.30, 0.045), 1)                # armrests
seat_part((0.0, 0.18, 0.20), (0.10, 0.10, 0.40), 1)                     # pedestal
seat_part((0.0, 0.18, 0.02), (0.34, 0.30, 0.04), 1)                     # foot plate
seat_proto = new_object("Seat", v, f, [mat_seat, mat_seat_frame])
for poly, idx in zip(seat_proto.data.polygons, fm):
    poly.material_index = idx
recalc_normals(seat_proto)
seat_mesh = seat_proto.data
bpy.context.collection.objects.unlink(seat_proto)

n_seats = 0
for i in range(N_TIERS):
    r_seat = R0 + i * TREAD + TREAD * 0.62
    z = i * RISE
    count = max(12, int(2.0 * math.pi * r_seat / SEAT_PITCH))
    for k in range(count):
        theta = 2.0 * math.pi * k / count
        if in_aisle(theta, r_seat):
            continue
        ob = bpy.data.objects.new("Seat_%02d_%03d" % (i, k), seat_mesh)
        bpy.context.collection.objects.link(ob)
        ob.matrix_world = (Matrix.Translation(Vector((r_seat * math.cos(theta),
                                                      r_seat * math.sin(theta), z)))
                           @ Matrix.Rotation(theta - math.pi * 0.5, 4, 'Z'))
        n_seats += 1

# --- central presentation platform ----------------------------------------
v, f = [], []
add_cylinder(v, f, (0.0, 0.0, 0.22), 2.55, 0.44, segments=72)
add_cylinder(v, f, (0.0, 0.0, 0.455), 2.62, 0.03, segments=72)
plat = new_object("Platform", v, f, [mat_wood], smooth=True)
recalc_normals(plat)

# two curved approach steps in each aisle direction
v, f = [], []
for a in aisle_angles:
    for s in range(2):
        rz = 2.75 + s * 0.32
        zc = 0.30 - s * 0.15
        segs = 8
        half = 0.42
        off = len(v)
        for k in range(segs + 1):
            t = a - half + 2.0 * half * k / segs
            ca, sa = math.cos(t), math.sin(t)
            v.append((rz * ca, rz * sa, zc))
            v.append(((rz + 0.32) * ca, (rz + 0.32) * sa, zc))
            v.append((rz * ca, rz * sa, zc - 0.15))
            v.append(((rz + 0.32) * ca, (rz + 0.32) * sa, zc - 0.15))
        for k in range(segs):
            b0 = off + 4 * k
            b1 = off + 4 * (k + 1)
            f.extend([(b0, b0 + 1, b1 + 1, b1), (b0 + 2, b1 + 2, b1 + 3, b0 + 3),
                      (b0, b1, b1 + 2, b0 + 2), (b0 + 1, b0 + 3, b1 + 3, b1 + 1)])
steps = new_object("Platform_Steps", v, f, [mat_wood])
recalc_normals(steps)

v, f = [], []
add_box(v, f, (0.0, -0.9, 0.99), (0.66, 0.44, 1.10))
add_box(v, f, (0.0, -0.9, 1.565), (0.78, 0.56, 0.05))
add_box(v, f, (0.9, 0.6, 0.86), (0.9, 0.5, 0.84))
podium = new_object("Podium", v, f, [mat_wood])
recalc_normals(podium)

# --- outer wall detailing, cove light and lighting rig --------------------
v, f = [], []
for k in range(24):
    a = 2.0 * math.pi * k / 24
    add_box(v, f, ((R_MAX - 0.09) * math.cos(a), (R_MAX - 0.09) * math.sin(a),
                   Z_TOP + WALL_H * 0.5),
            (0.18, 0.5, WALL_H - 0.4), rot_z=a)
pilasters = new_object("Wall_Pilasters", v, f, [mat_plaster])
recalc_normals(pilasters)

v, f = [], []
add_annulus(v, f, R_MAX - 0.55, R_MAX - 0.25, Z_TOP + WALL_H - 0.25, segments=120)
cove = new_object("Cove_Ring", v, f, [mat_cove])

v, f = [], []
r_rig = 6.0
z_rig = Z_TOP + WALL_H - 0.9
segs = 96
off = len(v)
for s in range(segs):
    a = 2.0 * math.pi * s / segs
    for (rr, zz) in ((r_rig - 0.09, z_rig - 0.09), (r_rig + 0.09, z_rig - 0.09),
                     (r_rig + 0.09, z_rig + 0.09), (r_rig - 0.09, z_rig + 0.09)):
        v.append((rr * math.cos(a), rr * math.sin(a), zz))
for s in range(segs):
    s2 = (s + 1) % segs
    for i in range(4):
        i2 = (i + 1) % 4
        f.append((off + 4 * s + i, off + 4 * s + i2, off + 4 * s2 + i2, off + 4 * s2 + i))
for k in range(16):
    a = 2.0 * math.pi * k / 16
    add_box(v, f, (r_rig * math.cos(a), r_rig * math.sin(a), z_rig - 0.35),
            (0.24, 0.24, 0.40), rot_z=a)
rig = new_object("Lighting_Rig", v, f, [mat_metal], smooth=True)
recalc_normals(rig)

v, f = [], []
for k in range(16):
    a = 2.0 * math.pi * k / 16
    add_cylinder(v, f, (r_rig * math.cos(a), r_rig * math.sin(a), z_rig - 0.56),
                 0.10, 0.02, segments=16)
new_object("Rig_Lenses", v, f, [mat_lens])


# --------------------------------------------------------------- lights
def add_spot(name, loc, target, energy, spot_deg, color=(1.0, 1.0, 1.0)):
    d = bpy.data.lights.new(name, 'SPOT')
    d.energy = energy
    d.spot_size = math.radians(spot_deg)
    d.spot_blend = 0.35
    d.color = color
    d.shadow_soft_size = 0.25
    ob = bpy.data.objects.new(name, d)
    bpy.context.collection.objects.link(ob)
    ob.location = loc
    ob.rotation_euler = (Vector(target) - Vector(loc)).to_track_quat('-Z', 'Y').to_euler()
    return ob


for k in range(6):
    a = 2.0 * math.pi * k / 6
    add_spot("Stage_Spot_%d" % k,
             (5.6 * math.cos(a), 5.6 * math.sin(a), z_rig - 0.7),
             (0.0, 0.0, 0.9), 3000.0, 46.0, (1.0, 0.95, 0.88))

for k in range(4):
    a = 2.0 * math.pi * k / 4 + 0.4
    add_spot("House_%d" % k,
             (8.0 * math.cos(a), 8.0 * math.sin(a), z_rig),
             (5.0 * math.cos(a), 5.0 * math.sin(a), 1.0), 1400.0, 90.0, (0.80, 0.84, 1.0))

ambient = bpy.data.lights.new("Ambient", 'AREA')
ambient.size = 20.0
ambient.energy = 900.0
ambient.color = (0.75, 0.80, 0.95)
amb_ob = bpy.data.objects.new("Ambient", ambient)
bpy.context.collection.objects.link(amb_ob)
amb_ob.location = (0.0, 0.0, Z_TOP + WALL_H + 1.5)
amb_ob.rotation_euler = (math.pi, 0.0, 0.0)

world = bpy.data.worlds.new("World")
world.use_nodes = True
bg = world.node_tree.nodes["Background"]
bg.inputs[0].default_value = (0.02, 0.02, 0.03, 1.0)
bg.inputs[1].default_value = 1.0
bpy.context.scene.world = world

# --------------------------------------------------------------- camera
cam_data = bpy.data.cameras.new("Camera")
cam_data.lens = 24.0
cam = bpy.data.objects.new("Camera", cam_data)
bpy.context.collection.objects.link(cam)
cam.location = (10.5, -11.5, 8.4)
cam.rotation_euler = (Vector((0.0, 0.0, 0.8)) - Vector(cam.location)).to_track_quat('-Z', 'Y').to_euler()
bpy.context.scene.camera = cam

print("claude-114: %d seats on %d tiers, %d aisles" % (n_seats, N_TIERS, N_AISLES))
