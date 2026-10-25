"""claude-116 : A solar farm following a gently sloping ground surface with service paths.

Builds, from factory startup:
  * an undulating, gently sloping terrain mesh
  * gravel service corridors + a perimeter ring road that hug the terrain
  * ~90 tracker tables (torque tube + posts + 2x5 PV modules) that follow the ground
  * inverter skids, a perimeter fence, sun + sky, and a survey camera
"""

import bpy
import bmesh
import math
import random
from mathutils import Vector, Matrix, Euler

random.seed(11)
bpy.ops.wm.read_factory_settings(use_empty=True)
scn = bpy.context.scene
scn.unit_settings.system = 'METRIC'


# ----------------------------------------------------------------------------
# helpers
# ----------------------------------------------------------------------------
def make_material(name, colour, rough=0.6, metal=0.0):
    mat = bpy.data.materials.new(name)
    mat.use_nodes = True
    bsdf = mat.node_tree.nodes["Principled BSDF"]
    bsdf.inputs["Base Color"].default_value = (colour[0], colour[1], colour[2], 1.0)
    bsdf.inputs["Roughness"].default_value = rough
    bsdf.inputs["Metallic"].default_value = metal
    return mat


def object_from_bmesh(name, bm, materials):
    me = bpy.data.meshes.new(name)
    bm.to_mesh(me)
    bm.free()
    for m in materials:
        me.materials.append(m)
    me.validate()
    ob = bpy.data.objects.new(name, me)
    scn.collection.objects.link(ob)
    return ob


def add_box(bm, loc, size, rot=None):
    """Axis aligned (or rotated) box centred on *loc*."""
    basis = rot if rot is not None else Matrix.Identity(4)
    mtx = (Matrix.Translation(Vector(loc)) @ basis @
           Matrix.Diagonal(Vector((size[0], size[1], size[2], 1.0))))
    bmesh.ops.create_cube(bm, size=1.0, matrix=mtx)


def add_tube(bm, p0, p1, radius, segments=10):
    """Capped cylinder spanning p0 -> p1."""
    p0 = Vector(p0)
    p1 = Vector(p1)
    d = p1 - p0
    length = d.length
    if length < 1e-6:
        return
    rot = d.to_track_quat('Z', 'Y').to_matrix().to_4x4()
    mtx = Matrix.Translation((p0 + p1) * 0.5) @ rot
    bmesh.ops.create_cone(bm, cap_ends=True, cap_tris=False, segments=segments,
                          radius1=radius, radius2=radius, depth=length, matrix=mtx)


def look_at(ob, target):
    d = Vector(target) - ob.location
    ob.rotation_euler = d.to_track_quat('-Z', 'Y').to_euler()


# ----------------------------------------------------------------------------
# materials
# ----------------------------------------------------------------------------
MAT_GROUND = make_material("Ground_Grass", (0.16, 0.20, 0.09), 0.95)
MAT_PATH = make_material("Service_Gravel", (0.40, 0.38, 0.35), 0.88)
MAT_GLASS = make_material("PV_Module", (0.014, 0.024, 0.060), 0.17, 0.20)
MAT_FRAME = make_material("Module_Frame", (0.63, 0.64, 0.66), 0.34, 1.0)
MAT_STEEL = make_material("Galvanised_Steel", (0.50, 0.52, 0.54), 0.44, 1.0)
MAT_CABINET = make_material("Inverter_Skid", (0.74, 0.74, 0.71), 0.52, 0.15)


# ----------------------------------------------------------------------------
# terrain
# ----------------------------------------------------------------------------
X0, X1 = -46.0, 46.0
Y0, Y1 = -36.0, 36.0


def ground_z(x, y):
    """Gentle ~4% slope to the south-east with soft rolling relief."""
    return (0.045 * x - 0.020 * y
            + 0.90 * math.sin(x / 26.0) * math.cos(y / 19.0)
            + 0.34 * math.sin(y / 11.0 + 1.2)
            + 0.18 * math.cos(x / 8.5 + 0.4))


def build_terrain():
    bm = bmesh.new()
    nx, ny = 92, 72
    grid = []
    for i in range(nx + 1):
        col = []
        x = X0 + (X1 - X0) * i / nx
        for j in range(ny + 1):
            y = Y0 + (Y1 - Y0) * j / ny
            col.append(bm.verts.new((x, y, ground_z(x, y))))
        grid.append(col)
    for i in range(nx):
        for j in range(ny):
            bm.faces.new((grid[i][j], grid[i + 1][j], grid[i + 1][j + 1], grid[i][j + 1]))
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces[:])
    ob = object_from_bmesh("Terrain", bm, [MAT_GROUND])
    return ob


build_terrain()


# ----------------------------------------------------------------------------
# service paths - gravel strips draped on the terrain
# ----------------------------------------------------------------------------
CORRIDORS_X = ((-16.5, -12.5), (12.5, 16.5))   # north-south service lanes
CORRIDOR_Y = (-3.2, 3.2)                        # east-west spine road


def add_path_strip(bm, xa, xb, ya, yb, step=2.0, lift=0.07):
    nx = max(1, int(round((xb - xa) / step)))
    ny = max(1, int(round((yb - ya) / step)))
    grid = []
    for i in range(nx + 1):
        x = xa + (xb - xa) * i / nx
        col = []
        for j in range(ny + 1):
            y = ya + (yb - ya) * j / ny
            col.append(bm.verts.new((x, y, ground_z(x, y) + lift)))
        grid.append(col)
    for i in range(nx):
        for j in range(ny):
            bm.faces.new((grid[i][j], grid[i + 1][j], grid[i + 1][j + 1], grid[i][j + 1]))


path_bm = bmesh.new()
for (xa, xb) in CORRIDORS_X:
    add_path_strip(path_bm, xa, xb, -34.5, 34.5)
add_path_strip(path_bm, -44.5, 44.5, CORRIDOR_Y[0], CORRIDOR_Y[1])
# perimeter ring road
add_path_strip(path_bm, -44.5, 44.5, -34.5, -31.0)
add_path_strip(path_bm, -44.5, 44.5, 31.0, 34.5)
add_path_strip(path_bm, -44.5, -41.0, -31.0, 31.0)
add_path_strip(path_bm, 41.0, 44.5, -31.0, 31.0)
bmesh.ops.recalc_face_normals(path_bm, faces=path_bm.faces[:])
object_from_bmesh("ServicePaths", path_bm, [MAT_PATH])


# ----------------------------------------------------------------------------
# PV tables
# ----------------------------------------------------------------------------
TILT = math.radians(27.0)
TABLE_LEN = 6.4          # along +X (row direction)
MODULE_W = 1.20          # along the torque tube
MODULE_H = 1.00          # up the slope of the table
MOUNT_H = 1.60           # torque tube height above grade

glass_bm = bmesh.new()
frame_bm = bmesh.new()
steel_bm = bmesh.new()


def add_table(cx, cy):
    zg = ground_z(cx, cy)
    hub = Vector((cx, cy, zg + MOUNT_H))
    tilt = Euler((TILT, 0.0, 0.0), 'XYZ').to_matrix().to_4x4()

    # torque tube along X, running through the hub
    axis = tilt @ Vector((1.0, 0.0, 0.0))
    add_tube(steel_bm, hub - axis * (TABLE_LEN * 0.5), hub + axis * (TABLE_LEN * 0.5),
             0.075, segments=12)

    # foundation posts
    for u in (-2.15, 2.15):
        top = hub + axis * u
        base = Vector((top.x, cy, ground_z(top.x, cy) - 0.9))
        add_tube(steel_bm, base, top, 0.062, segments=8)

    # modules: 5 across the tube, 2 up the tilt
    for i in range(5):
        u = (i - 2) * (MODULE_W + 0.03)
        for j in (0, 1):
            v = (j - 0.5) * (MODULE_H + 0.03)
            centre = hub + tilt @ Vector((u, v, 0.075))
            add_box(glass_bm, centre, (MODULE_W, MODULE_H, 0.032), tilt)
            add_box(frame_bm, centre + tilt @ Vector((0.0, 0.0, -0.006)),
                    (MODULE_W + 0.026, MODULE_H + 0.026, 0.044), tilt)


def blocked(cx):
    half = TABLE_LEN * 0.5 + 0.4
    for (xa, xb) in CORRIDORS_X:
        if cx + half > xa and cx - half < xb:
            return True
    return False


row_y = [y for y in range(-28, 29, 7)]
for cy in row_y:
    if CORRIDOR_Y[0] - 2.0 < cy < CORRIDOR_Y[1] + 2.0:
        continue
    cx = -38.0
    while cx <= 38.0:
        if not blocked(cx):
            add_table(cx, float(cy))
        cx += TABLE_LEN + 0.35

object_from_bmesh("PV_Modules", glass_bm, [MAT_GLASS])
object_from_bmesh("Module_Frames", frame_bm, [MAT_FRAME])
object_from_bmesh("Tracker_Steel", steel_bm, [MAT_STEEL])


# ----------------------------------------------------------------------------
# inverter skids beside the corridors
# ----------------------------------------------------------------------------
cab_bm = bmesh.new()
pad_bm = bmesh.new()
for (sx, sy) in ((-19.5, 10.0), (-19.5, -12.0), (19.5, 10.0), (19.5, -12.0)):
    z = ground_z(sx, sy)
    add_box(pad_bm, (sx, sy, z + 0.10), (4.2, 3.0, 0.24))
    add_box(cab_bm, (sx, sy, z + 1.20), (3.0, 1.5, 2.0))
    add_box(cab_bm, (sx, sy, z + 2.28), (3.2, 1.7, 0.14))
    add_box(cab_bm, (sx - 1.9, sy, z + 1.10), (0.9, 0.9, 1.6))
object_from_bmesh("Inverter_Skids", cab_bm, [MAT_CABINET])
object_from_bmesh("Skid_Pads", pad_bm, [MAT_PATH])


# ----------------------------------------------------------------------------
# perimeter fence
# ----------------------------------------------------------------------------
fence_bm = bmesh.new()
FX, FY = 45.0, 35.0
loop = []
for x in [FX - i * 5.0 for i in range(int(2 * FX / 5.0) + 1)]:
    loop.append((x, -FY))
for y in [-FY + i * 5.0 for i in range(int(2 * FY / 5.0) + 1)]:
    loop.append((-FX, y))
for x in [-FX + i * 5.0 for i in range(int(2 * FX / 5.0) + 1)]:
    loop.append((x, FY))
for y in [FY - i * 5.0 for i in range(int(2 * FY / 5.0) + 1)]:
    loop.append((FX, y))

for (x, y) in loop:
    z = ground_z(x, y)
    add_tube(fence_bm, (x, y, z - 0.5), (x, y, z + 2.2), 0.045, segments=6)
for idx in range(len(loop)):
    ax, ay = loop[idx]
    bx, by = loop[(idx + 1) % len(loop)]
    for h in (0.55, 1.30, 2.05):
        add_tube(fence_bm, (ax, ay, ground_z(ax, ay) + h),
                 (bx, by, ground_z(bx, by) + h), 0.014, segments=5)
object_from_bmesh("Perimeter_Fence", fence_bm, [MAT_STEEL])


# ----------------------------------------------------------------------------
# sky, sun and camera
# ----------------------------------------------------------------------------
world = bpy.data.worlds.new("SolarWorld")
world.use_nodes = True
bg = world.node_tree.nodes["Background"]
bg.inputs["Color"].default_value = (0.32, 0.46, 0.72, 1.0)
bg.inputs["Strength"].default_value = 1.15
scn.world = world

sun_data = bpy.data.lights.new("Sun", 'SUN')
sun_data.energy = 4.2
sun_data.angle = math.radians(1.2)
sun_data.color = (1.0, 0.95, 0.86)
sun = bpy.data.objects.new("Sun", sun_data)
sun.location = (-30.0, -50.0, 60.0)
sun.rotation_euler = Euler((math.radians(52.0), 0.0, math.radians(-38.0)), 'XYZ')
scn.collection.objects.link(sun)

fill_data = bpy.data.lights.new("SkyFill", 'AREA')
fill_data.energy = 8000.0
fill_data.size = 60.0
fill_data.color = (0.6, 0.72, 1.0)
fill = bpy.data.objects.new("SkyFill", fill_data)
fill.location = (20.0, 40.0, 45.0)
look_at(fill, (0.0, 0.0, 0.0))
scn.collection.objects.link(fill)

cam_data = bpy.data.cameras.new("Camera")
cam_data.lens = 42.0
cam_data.clip_end = 500.0
cam = bpy.data.objects.new("Camera", cam_data)
cam.location = (-58.0, -72.0, 34.0)
scn.collection.objects.link(cam)
look_at(cam, (2.0, 2.0, 1.5))
scn.camera = cam

print("claude-116: solar farm scene built with", len(bpy.data.objects), "objects")
