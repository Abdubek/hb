"""claude-112 - Parametric honeycomb partition wall with a doorway and surrounding frame.

The honeycomb is generated from a hex lattice: cell outlines are collected as a
de-duplicated edge set, and each unique edge becomes a single mitred rib beam, so
shared cell walls are never doubled.  Cells overlapping the doorway are omitted and
the ragged edge is trimmed by a door jamb.
"""

import bpy
import bmesh
import math
import random
from mathutils import Vector, Matrix

random.seed(7)

# --------------------------------------------------------------- parameters
WALL_W = 4.6          # overall width (X)
WALL_H = 3.05         # overall height (Z)
FRAME_W = 0.16        # frame member width
FRAME_D = 0.24        # frame member depth (Y)
PANEL_D = 0.13        # honeycomb rib depth (Y)
CELL_R = 0.255        # hex circumradius
RIB_T = 0.036         # rib thickness
DOOR_W = 1.10
DOOR_H = 2.15
JAMB_T = 0.10
JAMB_D = 0.20
GLASS_FRACTION = 0.14


# --------------------------------------------------------------- utilities
def reset_scene():
    bpy.ops.wm.read_factory_settings(use_empty=True)
    bpy.context.scene.unit_settings.system = 'METRIC'


def make_material(name, color, metallic=0.0, rough=0.5, transmission=0.0,
                  emit=None, strength=0.0):
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
    if emit is not None:
        p.inputs["Emission Color"].default_value = (emit[0], emit[1], emit[2], 1.0)
        p.inputs["Emission Strength"].default_value = strength
    return m


def new_object(name, verts, faces, mats=()):
    me = bpy.data.meshes.new(name)
    me.from_pydata(verts, [], faces)
    me.validate()
    me.update()
    for m in mats:
        me.materials.append(m)
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


def add_box(verts, faces, center, size):
    cx, cy, cz = center
    sx, sy, sz = size
    off = len(verts)
    for dx in (-0.5, 0.5):
        for dy in (-0.5, 0.5):
            for dz in (-0.5, 0.5):
                verts.append((cx + dx * sx, cy + dy * sy, cz + dz * sz))
    for f in BOX_FACES:
        faces.append(tuple(off + i for i in f))


def add_beam(verts, faces, p0, p1, w, h, up=(0.0, 1.0, 0.0)):
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


# --------------------------------------------------------------- scene
reset_scene()

mat_rib = make_material("Honeycomb Brass", (0.62, 0.46, 0.20), metallic=1.0, rough=0.30)
mat_frame = make_material("Frame Steel", (0.10, 0.11, 0.12), metallic=0.9, rough=0.35)
mat_jamb = make_material("Jamb Oak", (0.33, 0.20, 0.10), metallic=0.0, rough=0.48)
mat_glass = make_material("Tinted Infill", (0.15, 0.42, 0.44), metallic=0.0,
                          rough=0.08, transmission=0.9)
mat_floor = make_material("Terrazzo", (0.30, 0.29, 0.27), metallic=0.0, rough=0.35)
mat_back = make_material("Backdrop", (0.55, 0.53, 0.50), metallic=0.0, rough=0.85)
mat_light = make_material("Cove Light", (1.0, 0.95, 0.86), emit=(1.0, 0.95, 0.86),
                          strength=9.0)

# usable honeycomb region (inside the frame)
ix0 = -WALL_W * 0.5 + FRAME_W
ix1 = WALL_W * 0.5 - FRAME_W
iz0 = 0.0
iz1 = WALL_H - FRAME_W

door = (-DOOR_W * 0.5 - JAMB_T, DOOR_W * 0.5 + JAMB_T, -0.1, DOOR_H + JAMB_T)


def inside_panel(x, z):
    return (ix0 - 1e-6) <= x <= (ix1 + 1e-6) and (iz0 - 1e-6) <= z <= (iz1 + 1e-6)


def in_door(x, z):
    return door[0] <= x <= door[1] and door[2] <= z <= door[3]


# ---- hex lattice ----------------------------------------------------------
step_x = math.sqrt(3.0) * CELL_R
step_z = 1.5 * CELL_R
hex_dirs = [(CELL_R * math.cos(math.radians(90.0 + 60.0 * k)),
             CELL_R * math.sin(math.radians(90.0 + 60.0 * k))) for k in range(6)]

n_cols = int(WALL_W / step_x) + 3
n_rows = int(WALL_H / step_z) + 3

edges = {}
cell_centers = []
for row in range(-1, n_rows):
    cz = iz0 + row * step_z
    x_off = (step_x * 0.5) if (row % 2) else 0.0
    for col in range(-n_cols, n_cols + 1):
        cx = col * step_x + x_off
        corners = [(cx + dx, cz + dz) for (dx, dz) in hex_dirs]
        if not all(inside_panel(x, z) for (x, z) in corners):
            continue
        if any(in_door(x, z) for (x, z) in corners):
            continue
        cell_centers.append((cx, cz))
        for k in range(6):
            a = corners[k]
            b = corners[(k + 1) % 6]
            ka = (round(a[0], 4), round(a[1], 4))
            kb = (round(b[0], 4), round(b[1], 4))
            key = (ka, kb) if ka <= kb else (kb, ka)
            edges[key] = (a, b)

# ---- ribs -----------------------------------------------------------------
EXT = 0.289 * RIB_T          # mitre allowance at 120 degree nodes
v, f = [], []
for (a, b) in edges.values():
    p0 = Vector((a[0], 0.0, a[1]))
    p1 = Vector((b[0], 0.0, b[1]))
    d = (p1 - p0).normalized()
    add_beam(v, f, p0 - d * EXT, p1 + d * EXT, RIB_T, PANEL_D, up=(0.0, 1.0, 0.0))
ribs = new_object("Honeycomb_Ribs", v, f, [mat_rib])
recalc_normals(ribs)
bev = ribs.modifiers.new("Bevel", 'BEVEL')
bev.width = 0.004
bev.segments = 2
bev.limit_method = 'ANGLE'

# ---- tinted infill plates in a scattered subset of cells ------------------
v, f = [], []
for (cx, cz) in cell_centers:
    if random.random() > GLASS_FRACTION:
        continue
    off = len(v)
    inset = CELL_R - RIB_T * 1.1
    for k in range(6):
        a = math.radians(90.0 + 60.0 * k)
        v.append((cx + inset * math.cos(a), 0.0, cz + inset * math.sin(a)))
    f.append(tuple(off + k for k in range(6)))
if f:
    glass = new_object("Honeycomb_Infill", v, f, [mat_glass])
    sol = glass.modifiers.new("Solidify", 'SOLIDIFY')
    sol.thickness = 0.012
    sol.offset = 0.0

# ---- surrounding frame ----------------------------------------------------
v, f = [], []
hw = WALL_W * 0.5
add_box(v, f, (-hw + FRAME_W * 0.5, 0.0, WALL_H * 0.5),
        (FRAME_W, FRAME_D, WALL_H))                       # left stile
add_box(v, f, (hw - FRAME_W * 0.5, 0.0, WALL_H * 0.5),
        (FRAME_W, FRAME_D, WALL_H))                       # right stile
add_box(v, f, (0.0, 0.0, WALL_H - FRAME_W * 0.5),
        (WALL_W - 2.0 * FRAME_W, FRAME_D, FRAME_W))       # head
add_box(v, f, (0.0, 0.0, -0.045), (WALL_W, FRAME_D + 0.04, 0.09))  # base channel
for sx in (-1.0, 1.0):
    add_box(v, f, (sx * (hw - FRAME_W * 0.5), 0.0, WALL_H + 0.03),
            (FRAME_W + 0.06, FRAME_D + 0.06, 0.06))       # cap plates
frame = new_object("Wall_Frame", v, f, [mat_frame])
recalc_normals(frame)
bev = frame.modifiers.new("Bevel", 'BEVEL')
bev.width = 0.008
bev.segments = 2

# ---- doorway jamb and header ---------------------------------------------
v, f = [], []
jx = DOOR_W * 0.5 + JAMB_T * 0.5
for sx in (-1.0, 1.0):
    add_box(v, f, (sx * jx, 0.0, (DOOR_H + JAMB_T) * 0.5),
            (JAMB_T, JAMB_D, DOOR_H + JAMB_T))
add_box(v, f, (0.0, 0.0, DOOR_H + JAMB_T * 0.5),
        (DOOR_W + 2.0 * JAMB_T, JAMB_D, JAMB_T))
# reveal linings on both faces of the opening
for sy in (-1.0, 1.0):
    for sx in (-1.0, 1.0):
        add_box(v, f, (sx * (DOOR_W * 0.5 + 0.012), sy * (JAMB_D * 0.5 + 0.008),
                       DOOR_H * 0.5), (0.024, 0.016, DOOR_H))
jamb = new_object("Door_Jamb", v, f, [mat_jamb])
recalc_normals(jamb)
bev = jamb.modifiers.new("Bevel", 'BEVEL')
bev.width = 0.006
bev.segments = 2

# threshold strip
v, f = [], []
add_box(v, f, (0.0, 0.0, 0.006), (DOOR_W + 2.0 * JAMB_T, JAMB_D + 0.05, 0.012))
thresh = new_object("Threshold", v, f, [mat_frame])
recalc_normals(thresh)

# cove light behind the wall head, to graze the honeycomb
v, f = [], []
add_box(v, f, (0.0, 0.42, WALL_H - 0.05), (WALL_W - 0.4, 0.10, 0.03))
cove = new_object("Cove_Strip", v, f, [mat_light])
recalc_normals(cove)

# ---- room shell -----------------------------------------------------------
new_object("Floor", [(-7.0, -6.0, 0.0), (7.0, -6.0, 0.0), (7.0, 6.0, 0.0), (-7.0, 6.0, 0.0)],
           [(0, 1, 2, 3)], [mat_floor])
new_object("Backdrop", [(-7.0, 3.6, 0.0), (7.0, 3.6, 0.0), (7.0, 3.6, 4.2), (-7.0, 3.6, 4.2)],
           [(0, 1, 2, 3)], [mat_back])


# --------------------------------------------------------------- lights
def add_area(name, loc, target, size, energy, color=(1.0, 1.0, 1.0)):
    d = bpy.data.lights.new(name, 'AREA')
    d.size = size
    d.energy = energy
    d.color = color
    ob = bpy.data.objects.new(name, d)
    bpy.context.collection.objects.link(ob)
    ob.location = loc
    ob.rotation_euler = (Vector(target) - Vector(loc)).to_track_quat('-Z', 'Y').to_euler()
    return ob


add_area("Key", (2.8, -3.4, 3.4), (0.2, 0.0, 1.5), 3.2, 900.0)
add_area("Behind", (0.0, 2.6, 1.8), (0.0, 0.0, 1.4), 4.0, 700.0, (0.85, 0.92, 1.0))
add_area("Fill", (-3.6, -2.2, 2.2), (-0.5, 0.0, 1.4), 3.0, 260.0)

world = bpy.data.worlds.new("World")
world.use_nodes = True
bg = world.node_tree.nodes["Background"]
bg.inputs[0].default_value = (0.08, 0.085, 0.095, 1.0)
bg.inputs[1].default_value = 1.0
bpy.context.scene.world = world

# --------------------------------------------------------------- camera
cam_data = bpy.data.cameras.new("Camera")
cam_data.lens = 35.0
cam = bpy.data.objects.new("Camera", cam_data)
bpy.context.collection.objects.link(cam)
cam.location = (3.1, -4.6, 1.85)
cam.rotation_euler = (Vector((-0.15, 0.0, 1.35)) - Vector(cam.location)).to_track_quat('-Z', 'Y').to_euler()
bpy.context.scene.camera = cam

print("claude-112: %d cells, %d unique ribs" % (len(cell_centers), len(edges)))
