"""claude-049 - A solar panel array on an angled support frame.

A ground mounted PV table: 2 rows x 5 columns of framed modules at 30 degrees
tilt, carried on tilted rafters, torque-tube purlins, front/rear posts with
concrete footings and wind bracing.  Includes junction boxes, DC conduit and a
string inverter cabinet.
"""

import bpy
import bmesh
import math
import random
from mathutils import Vector, Matrix, Euler, noise

random.seed(49)


# --------------------------------------------------------------------------
# helpers
# --------------------------------------------------------------------------
def reset_scene():
    bpy.ops.wm.read_factory_settings(use_empty=True)
    bpy.context.scene.unit_settings.system = 'METRIC'


def link(obj):
    bpy.context.scene.collection.objects.link(obj)
    return obj


def make_mat(name, color, rough=0.5, metal=0.0, emis=None, emis_str=0.0,
             spec=0.5):
    m = bpy.data.materials.new(name)
    m.use_nodes = True
    b = m.node_tree.nodes["Principled BSDF"]
    b.inputs["Base Color"].default_value = (color[0], color[1], color[2], 1.0)
    b.inputs["Roughness"].default_value = rough
    b.inputs["Metallic"].default_value = metal
    if "Specular IOR Level" in b.inputs:
        b.inputs["Specular IOR Level"].default_value = spec
    if emis is not None:
        if "Emission Color" in b.inputs:
            b.inputs["Emission Color"].default_value = (emis[0], emis[1], emis[2], 1.0)
        b.inputs["Emission Strength"].default_value = emis_str
    return m


def tag_new(bm, before, index, smooth=False):
    for f in bm.faces:
        if f not in before:
            f.material_index = index
            if smooth:
                f.smooth = True


def bm_box(bm, center, size, index=0, rot=None):
    m = Matrix.Translation(Vector(center))
    if rot is not None:
        m = m @ Euler(rot).to_matrix().to_4x4()
    m = m @ Matrix.Diagonal(Vector((size[0], size[1], size[2], 1.0)))
    before = set(bm.faces)
    bmesh.ops.create_cube(bm, size=1.0, matrix=m)
    tag_new(bm, before, index)


def bm_cyl(bm, center, radius, depth, index=0, segments=20, rot=None, r2=None):
    m = Matrix.Translation(Vector(center))
    if rot is not None:
        m = m @ Euler(rot).to_matrix().to_4x4()
    before = set(bm.faces)
    bmesh.ops.create_cone(bm, cap_ends=True, cap_tris=False, segments=segments,
                          radius1=radius, radius2=(radius if r2 is None else r2),
                          depth=depth, matrix=m)
    tag_new(bm, before, index, smooth=True)


def bm_tube_between(bm, p1, p2, radius, index=0, segments=12):
    p1, p2 = Vector(p1), Vector(p2)
    d = p2 - p1
    if d.length < 1e-6:
        return
    m = (Matrix.Translation((p1 + p2) * 0.5)
         @ d.to_track_quat('Z', 'Y').to_matrix().to_4x4())
    before = set(bm.faces)
    bmesh.ops.create_cone(bm, cap_ends=True, cap_tris=False, segments=segments,
                          radius1=radius, radius2=radius, depth=d.length, matrix=m)
    tag_new(bm, before, index, smooth=True)


def finish(bm, name, mats, location=(0, 0, 0), rotation=(0, 0, 0)):
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    me = bpy.data.meshes.new(name)
    bm.to_mesh(me)
    bm.free()
    obj = bpy.data.objects.new(name, me)
    obj.location = location
    obj.rotation_euler = rotation
    for m in mats:
        me.materials.append(m)
    return link(obj)


def poly_tube(name, points, radius, material, res=3):
    cu = bpy.data.curves.new(name, 'CURVE')
    cu.dimensions = '3D'
    sp = cu.splines.new('POLY')
    sp.points.add(len(points) - 1)
    for i, p in enumerate(points):
        sp.points[i].co = (p[0], p[1], p[2], 1.0)
    cu.bevel_depth = radius
    cu.bevel_resolution = res
    cu.use_fill_caps = True
    obj = bpy.data.objects.new(name, cu)
    cu.materials.append(material)
    return link(obj)


def look_at(obj, target):
    d = Vector(target) - obj.location
    obj.rotation_euler = d.to_track_quat('-Z', 'Y').to_euler()


# --------------------------------------------------------------------------
reset_scene()

M_GROUND = make_mat("Ground", (0.24, 0.23, 0.17), rough=0.95)
M_GRAVEL = make_mat("Gravel", (0.38, 0.37, 0.34), rough=0.9)
M_CONCRETE = make_mat("Footing", (0.55, 0.54, 0.51), rough=0.85)
M_GALV = make_mat("GalvSteel", (0.60, 0.62, 0.64), rough=0.42, metal=1.0)
M_ALU = make_mat("AluFrame", (0.76, 0.77, 0.79), rough=0.28, metal=1.0)
M_CELL = make_mat("PVCell", (0.015, 0.025, 0.075), rough=0.10, metal=0.35)
M_BUSBAR = make_mat("Busbar", (0.72, 0.73, 0.75), rough=0.25, metal=1.0)
M_BACKSHEET = make_mat("Backsheet", (0.10, 0.11, 0.13), rough=0.55)
M_JBOX = make_mat("JunctionBox", (0.08, 0.08, 0.09), rough=0.6)
M_CABLE = make_mat("DCCable", (0.05, 0.05, 0.06), rough=0.7)
M_INVERTER = make_mat("Inverter", (0.80, 0.81, 0.82), rough=0.45, metal=0.3)
M_LABEL = make_mat("WarningLabel", (0.85, 0.62, 0.05), rough=0.5)

# ------------------------------------------------------------------- terrain
bm = bmesh.new()
N = 40
SPAN = 60.0
grid = []
for iy in range(N + 1):
    row = []
    for ix in range(N + 1):
        x = -SPAN / 2 + SPAN * ix / N
        y = -SPAN / 2 + SPAN * iy / N
        h = noise.noise(Vector((x * 0.035, y * 0.035, 0.0))) * 0.55
        flat = max(0.0, 1.0 - (max(abs(x) / 12.0, abs(y) / 8.0)))
        row.append(bm.verts.new((x, y, h * (1.0 - flat))))
    grid.append(row)
for iy in range(N):
    for ix in range(N):
        f = bm.faces.new((grid[iy][ix], grid[iy][ix + 1],
                          grid[iy + 1][ix + 1], grid[iy + 1][ix]))
        f.material_index = 0
finish(bm, "Terrain", [M_GROUND])

# gravel maintenance pad under the array
bm = bmesh.new()
bm_box(bm, (0, 0, 0.015), (24.0, 9.0, 0.03), 0)
finish(bm, "GravelPad", [M_GRAVEL])


# --------------------------------------------------------------- PV module
def build_module(name, width=1.05, height=1.75, cols=6, rows=10,
                 location=(0, 0, 0), rotation=(0, 0, 0)):
    """Framed module lying in local XY, glass face towards +Z."""
    bm = bmesh.new()
    frame_w, frame_t = 0.035, 0.038
    hw, hh = width / 2, height / 2
    # laminate backsheet
    bm_box(bm, (0, 0, 0.0), (width - 2 * frame_w, height - 2 * frame_w, 0.008), 2)
    # cells
    inner_w = width - 2 * frame_w - 0.024
    inner_h = height - 2 * frame_w - 0.024
    cw = inner_w / cols
    ch = inner_h / rows
    gap = 0.004
    for c in range(cols):
        for r in range(rows):
            cx = -inner_w / 2 + cw * (c + 0.5)
            cy = -inner_h / 2 + ch * (r + 0.5)
            bm_box(bm, (cx, cy, 0.006), (cw - gap, ch - gap, 0.003), 1)
            # three fine busbars per cell
            for b in range(3):
                bm_box(bm, (cx - (cw - gap) * 0.3 + b * (cw - gap) * 0.3, cy, 0.0085),
                       (0.0035, ch - gap, 0.0008), 3)
    # perimeter frame
    bm_box(bm, (0, hh - frame_w / 2, 0.004), (width, frame_w, frame_t), 0)
    bm_box(bm, (0, -hh + frame_w / 2, 0.004), (width, frame_w, frame_t), 0)
    bm_box(bm, (-hw + frame_w / 2, 0, 0.004), (frame_w, height - 2 * frame_w, frame_t), 0)
    bm_box(bm, (hw - frame_w / 2, 0, 0.004), (frame_w, height - 2 * frame_w, frame_t), 0)
    # junction box + short leads on the back
    bm_box(bm, (0, -hh + 0.30, -0.035), (0.16, 0.10, 0.045), 4)
    return finish(bm, name, [M_ALU, M_CELL, M_BACKSHEET, M_BUSBAR, M_JBOX],
                  location=location, rotation=rotation)


# ------------------------------------------------------- array arrangement
TILT = math.radians(30.0)
COLS, ROWS = 5, 2
MOD_W, MOD_H = 1.05, 1.75
GAP_X, GAP_Y = 0.03, 0.04
ARRAY_W = COLS * MOD_W + (COLS - 1) * GAP_X
SLOPE_LEN = ROWS * MOD_H + (ROWS - 1) * GAP_Y
FRONT_H = 0.85                                  # height of the lower rail
BASE_Y = -SLOPE_LEN * math.cos(TILT) / 2        # front edge in plan


def slope_point(u, s, lift=0.0):
    """u across the array (X), s along the slope from the low edge."""
    return Vector((u,
                   BASE_Y + s * math.cos(TILT),
                   FRONT_H + s * math.sin(TILT) + lift))


modules = []
for c in range(COLS):
    for r in range(ROWS):
        u = -ARRAY_W / 2 + MOD_W / 2 + c * (MOD_W + GAP_X)
        s = MOD_H / 2 + r * (MOD_H + GAP_Y)
        p = slope_point(u, s, lift=0.12)
        modules.append(build_module("PVModule_c%d_r%d" % (c, r),
                                    MOD_W, MOD_H,
                                    location=(p.x, p.y, p.z),
                                    rotation=(TILT, 0.0, 0.0)))

# ------------------------------------------------------------ support frame
bm = bmesh.new()
rafter_x = [-ARRAY_W / 2 + 0.55 + i * (ARRAY_W - 1.1) / 3 for i in range(4)]
for rx in rafter_x:
    a = slope_point(rx, -0.25, lift=0.02)
    b = slope_point(rx, SLOPE_LEN + 0.25, lift=0.02)
    d = b - a
    m = (Matrix.Translation((a + b) * 0.5)
         @ Euler((TILT, 0, 0)).to_matrix().to_4x4())
    before = set(bm.faces)
    bmesh.ops.create_cube(bm, size=1.0,
                          matrix=m @ Matrix.Diagonal(Vector((0.09, d.length, 0.16, 1.0))))
    tag_new(bm, before, 0)

    # front and rear posts down to the footings
    front = slope_point(rx, 0.15)
    rear = slope_point(rx, SLOPE_LEN - 0.15)
    bm_box(bm, (front.x, front.y, front.z / 2), (0.10, 0.10, front.z), 0)
    bm_box(bm, (rear.x, rear.y, rear.z / 2), (0.10, 0.10, rear.z), 0)
    # diagonal brace between rear post and front foot
    bm_tube_between(bm, (rx, rear.y, rear.z - 0.35), (rx, front.y, 0.20), 0.032, 0)

# purlins (torque tubes) running across the array under the modules
for s in (MOD_H * 0.28, MOD_H * 0.28 + MOD_H + GAP_Y, SLOPE_LEN - MOD_H * 0.28):
    p = slope_point(0.0, s, lift=-0.02)
    bm_box(bm, (0.0, p.y, p.z), (ARRAY_W + 0.6, 0.13, 0.11), 1, rot=(TILT, 0, 0))

# rear horizontal tie beam and wind bracing in the post plane
rear_top = slope_point(0.0, SLOPE_LEN - 0.15)
front_top = slope_point(0.0, 0.15)
bm_box(bm, (0.0, rear_top.y, rear_top.z - 0.55), (ARRAY_W + 0.4, 0.09, 0.12), 0)
bm_box(bm, (0.0, front_top.y, 0.35), (ARRAY_W + 0.4, 0.08, 0.10), 0)
for i in range(len(rafter_x) - 1):
    x0, x1 = rafter_x[i], rafter_x[i + 1]
    bm_tube_between(bm, (x0, rear_top.y, 0.15), (x1, rear_top.y, rear_top.z - 0.60), 0.022, 1)
    bm_tube_between(bm, (x1, rear_top.y, 0.15), (x0, rear_top.y, rear_top.z - 0.60), 0.022, 1)
finish(bm, "SupportFrame", [M_GALV, M_ALU])

# concrete footings ---------------------------------------------------------
bm = bmesh.new()
for rx in rafter_x:
    for yy in (slope_point(rx, 0.15).y, slope_point(rx, SLOPE_LEN - 0.15).y):
        bm_box(bm, (rx, yy, 0.11), (0.46, 0.46, 0.22), 0)
        bm_box(bm, (rx, yy, 0.23), (0.30, 0.30, 0.04), 0)
finish(bm, "Footings", [M_CONCRETE])

# module clamps -------------------------------------------------------------
bm = bmesh.new()
for c in range(COLS):
    u = -ARRAY_W / 2 + MOD_W / 2 + c * (MOD_W + GAP_X)
    for s in (MOD_H * 0.28, MOD_H * 0.28 + MOD_H + GAP_Y, SLOPE_LEN - MOD_H * 0.28):
        for du in (-MOD_W / 2 - 0.015, MOD_W / 2 + 0.015):
            p = slope_point(u + du, s, lift=0.10)
            bm_box(bm, (p.x, p.y, p.z), (0.05, 0.06, 0.05), 0, rot=(TILT, 0, 0))
finish(bm, "ModuleClamps", [M_ALU])

# ------------------------------------------------------- DC wiring & inverter
cable_pts = []
for c in range(COLS):
    u = -ARRAY_W / 2 + MOD_W / 2 + c * (MOD_W + GAP_X)
    p = slope_point(u, SLOPE_LEN - 0.35, lift=-0.06)
    cable_pts.append((p.x, p.y + 0.05, p.z - 0.04))
cable_pts.append((ARRAY_W / 2 + 0.6, slope_point(0, SLOPE_LEN).y, 1.35))
cable_pts.append((ARRAY_W / 2 + 0.9, slope_point(0, SLOPE_LEN).y, 0.95))
cable_pts.append((ARRAY_W / 2 + 1.1, slope_point(0, SLOPE_LEN).y - 0.6, 0.80))
cable_pts.append((5.4, -0.4, 0.75))
poly_tube("DCTrunk", cable_pts, 0.022, M_CABLE)

# per-module drop leads
for c in range(COLS):
    u = -ARRAY_W / 2 + MOD_W / 2 + c * (MOD_W + GAP_X)
    top = slope_point(u, MOD_H * 0.85, lift=0.02)
    bot = slope_point(u, SLOPE_LEN - 0.35, lift=-0.06)
    poly_tube("DCLead_%d" % c,
              [(top.x, top.y, top.z - 0.03),
               (top.x + 0.06, (top.y + bot.y) / 2, (top.z + bot.z) / 2 - 0.12),
               (bot.x, bot.y + 0.05, bot.z - 0.04)],
              0.014, M_CABLE)

# inverter cabinet on a small plinth
bm = bmesh.new()
bm_box(bm, (0, 0, 0.08), (1.10, 0.75, 0.16), 3)
bm_box(bm, (0, 0, 0.86), (0.80, 0.36, 1.40), 0)
bm_box(bm, (0, -0.19, 1.05), (0.62, 0.02, 0.60), 1)     # louvred front
for k in range(8):
    bm_box(bm, (0, -0.20, 0.82 + k * 0.075), (0.58, 0.012, 0.028), 1)
bm_box(bm, (0, -0.19, 1.52), (0.30, 0.02, 0.12), 2)     # warning label
bm_box(bm, (0, 0, 1.60), (0.86, 0.42, 0.06), 1)         # rain hood
bm_cyl(bm, (0.0, 0.20, 0.30), 0.035, 0.40, 1, segments=12, rot=(math.radians(90), 0, 0))
finish(bm, "Inverter", [M_INVERTER, M_GALV, M_LABEL, M_CONCRETE],
       location=(5.9, -0.4, 0.02), rotation=(0, 0, math.radians(-95)))

# ------------------------------------------------------------------ lighting
sun_data = bpy.data.lights.new("Sun", 'SUN')
sun_data.energy = 5.0
sun_data.angle = math.radians(0.53)
sun_data.color = (1.0, 0.95, 0.87)
sun = bpy.data.objects.new("Sun", sun_data)
# sun roughly normal to the tilted modules, from the south-east
sun.rotation_euler = (math.radians(46), 0.0, math.radians(150))
sun.location = (0, 0, 30)
link(sun)

sky_fill = bpy.data.lights.new("SkyFill", 'AREA')
sky_fill.shape = 'SQUARE'
sky_fill.size = 30.0
sky_fill.energy = 1200.0
sky_fill.color = (0.55, 0.68, 1.0)
sf = bpy.data.objects.new("SkyFill", sky_fill)
sf.location = (0, 0, 16.0)
link(sf)

world = bpy.data.worlds.new("ArrayWorld")
world.use_nodes = True
nt = world.node_tree
bg = nt.nodes["Background"]
bg.inputs["Strength"].default_value = 1.0
try:
    sky = nt.nodes.new("ShaderNodeTexSky")
    sky.sky_type = 'NISHITA'
    sky.sun_elevation = math.radians(46)
    sky.sun_rotation = math.radians(150)
    nt.links.new(sky.outputs["Color"], bg.inputs["Color"])
except Exception:
    bg.inputs["Color"].default_value = (0.32, 0.48, 0.80, 1.0)
bpy.context.scene.world = world

# ------------------------------------------------------------------- camera
cam_data = bpy.data.cameras.new("ArrayCam")
cam_data.lens = 40.0
cam_data.clip_end = 500.0
cam = bpy.data.objects.new("ArrayCam", cam_data)
cam.location = (-7.5, -9.5, 4.2)
link(cam)
look_at(cam, (0.0, 0.0, 1.4))
bpy.context.scene.camera = cam

bpy.context.view_layer.update()
print("claude-049: solar array built with %d modules, %d objects"
      % (len(modules), len(bpy.data.objects)))
