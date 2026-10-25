"""claude-117 : A spherical arrangement of small satellites linked by thin struts.

A Fibonacci-distributed shell of 44 identical CubeSat-like satellites (body, two
solar wings, dish and mast), each oriented radially, tied together by a thin
truss of struts running between near neighbours on the shell.
"""

import bpy
import bmesh
import math
from mathutils import Vector, Matrix, Euler

bpy.ops.wm.read_factory_settings(use_empty=True)
scn = bpy.context.scene

SHELL_R = 6.0
N_SATS = 44
STRUT_R = 0.035


# ----------------------------------------------------------------------------
# helpers
# ----------------------------------------------------------------------------
def make_material(name, colour, rough=0.5, metal=0.0, emit=None, emit_strength=0.0):
    mat = bpy.data.materials.new(name)
    mat.use_nodes = True
    bsdf = mat.node_tree.nodes["Principled BSDF"]
    bsdf.inputs["Base Color"].default_value = (colour[0], colour[1], colour[2], 1.0)
    bsdf.inputs["Roughness"].default_value = rough
    bsdf.inputs["Metallic"].default_value = metal
    if emit is not None:
        bsdf.inputs["Emission Color"].default_value = (emit[0], emit[1], emit[2], 1.0)
        bsdf.inputs["Emission Strength"].default_value = emit_strength
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


def add_box(bm, basis, offset, size):
    mtx = (basis @ Matrix.Translation(Vector(offset)) @
           Matrix.Diagonal(Vector((size[0], size[1], size[2], 1.0))))
    bmesh.ops.create_cube(bm, size=1.0, matrix=mtx)


def add_cone(bm, basis, offset, r1, r2, depth, segments=16, rot=None):
    mtx = basis @ Matrix.Translation(Vector(offset))
    if rot is not None:
        mtx = mtx @ rot
    bmesh.ops.create_cone(bm, cap_ends=True, cap_tris=False, segments=segments,
                          radius1=r1, radius2=r2, depth=depth, matrix=mtx)


def add_tube(bm, p0, p1, radius, segments=8):
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
MAT_BODY = make_material("Sat_Body", (0.80, 0.80, 0.82), 0.30, 0.85)
MAT_FOIL = make_material("Thermal_Foil", (0.86, 0.66, 0.18), 0.22, 1.0)
MAT_PANEL = make_material("Solar_Cells", (0.03, 0.05, 0.14), 0.20, 0.35)
MAT_STRUT = make_material("Truss_Strut", (0.55, 0.57, 0.60), 0.38, 1.0)
MAT_DISH = make_material("Antenna", (0.90, 0.90, 0.88), 0.25, 0.6)
MAT_LED = make_material("Beacon", (0.9, 0.15, 0.1), 0.4, 0.0, (1.0, 0.2, 0.1), 12.0)


# ----------------------------------------------------------------------------
# node placement: Fibonacci sphere
# ----------------------------------------------------------------------------
def fibonacci_sphere(n, radius):
    pts = []
    ga = math.pi * (3.0 - math.sqrt(5.0))
    for i in range(n):
        z = 1.0 - 2.0 * (i + 0.5) / n
        r = math.sqrt(max(0.0, 1.0 - z * z))
        a = ga * i
        pts.append(Vector((math.cos(a) * r, math.sin(a) * r, z)) * radius)
    return pts


nodes = fibonacci_sphere(N_SATS, SHELL_R)


def local_basis(pos):
    """Frame with +Z radially outward, +X tangential."""
    zax = pos.normalized()
    ref = Vector((0.0, 0.0, 1.0))
    if abs(zax.dot(ref)) > 0.95:
        ref = Vector((1.0, 0.0, 0.0))
    xax = ref.cross(zax).normalized()
    yax = zax.cross(xax).normalized()
    m = Matrix((
        (xax.x, yax.x, zax.x, pos.x),
        (xax.y, yax.y, zax.y, pos.y),
        (xax.z, yax.z, zax.z, pos.z),
        (0.0, 0.0, 0.0, 1.0),
    ))
    return m


# ----------------------------------------------------------------------------
# satellites
# ----------------------------------------------------------------------------
body_bm = bmesh.new()
foil_bm = bmesh.new()
panel_bm = bmesh.new()
dish_bm = bmesh.new()
led_bm = bmesh.new()

WING_ROT = Matrix.Rotation(math.radians(6.0), 4, 'X')

for pos in nodes:
    B = local_basis(pos)

    # main bus: 3U-ish body with a foil-wrapped mid band
    add_box(body_bm, B, (0.0, 0.0, 0.0), (0.46, 0.42, 0.62))
    add_box(foil_bm, B, (0.0, 0.0, 0.0), (0.48, 0.44, 0.22))
    add_box(body_bm, B, (0.0, 0.0, -0.34), (0.30, 0.30, 0.08))

    # two deployed solar wings, tangential, slightly cocked
    for s in (-1.0, 1.0):
        wing_root = Vector((s * 0.30, 0.0, 0.0))
        add_box(body_bm, B, wing_root, (0.14, 0.06, 0.06))
        mtx = (B @ Matrix.Translation(Vector((s * 1.02, 0.0, 0.0))) @ WING_ROT @
               Matrix.Diagonal(Vector((1.28, 0.52, 0.022, 1.0))))
        bmesh.ops.create_cube(panel_bm, size=1.0, matrix=mtx)
        # wing spine
        mtx2 = (B @ Matrix.Translation(Vector((s * 1.02, 0.0, -0.022))) @ WING_ROT @
                Matrix.Diagonal(Vector((1.32, 0.06, 0.03, 1.0))))
        bmesh.ops.create_cube(body_bm, size=1.0, matrix=mtx2)

    # outward facing dish + feed mast
    add_cone(dish_bm, B, (0.0, 0.0, 0.40), 0.21, 0.07, 0.13, segments=20)
    add_cone(dish_bm, B, (0.0, 0.0, 0.52), 0.018, 0.018, 0.16, segments=8)
    add_cone(dish_bm, B, (0.0, 0.0, 0.61), 0.05, 0.02, 0.05, segments=10)

    # inward facing thruster nozzle and beacon
    add_cone(body_bm, B, (0.0, 0.0, -0.44), 0.06, 0.11, 0.12, segments=12)
    add_box(led_bm, B, (0.16, 0.22, 0.20), (0.05, 0.03, 0.05))

object_from_bmesh("Satellite_Bodies", body_bm, [MAT_BODY])
object_from_bmesh("Satellite_Foil", foil_bm, [MAT_FOIL])
object_from_bmesh("Solar_Wings", panel_bm, [MAT_PANEL])
object_from_bmesh("Antennas", dish_bm, [MAT_DISH])
object_from_bmesh("Beacons", led_bm, [MAT_LED])


# ----------------------------------------------------------------------------
# strut network between near neighbours
# ----------------------------------------------------------------------------
nearest = []
for i, a in enumerate(nodes):
    d = min((a - b).length for j, b in enumerate(nodes) if j != i)
    nearest.append(d)
mean_nn = sum(nearest) / len(nearest)
threshold = mean_nn * 1.32

pairs = set()
for i, a in enumerate(nodes):
    order = sorted(range(len(nodes)), key=lambda j: (nodes[j] - a).length)
    for j in order[1:7]:
        if (nodes[j] - a).length <= threshold:
            pairs.add((min(i, j), max(i, j)))

# guarantee every node keeps at least its three closest links
for i, a in enumerate(nodes):
    order = sorted(range(len(nodes)), key=lambda j: (nodes[j] - a).length)
    for j in order[1:4]:
        pairs.add((min(i, j), max(i, j)))

strut_bm = bmesh.new()
node_bm = bmesh.new()
for (i, j) in sorted(pairs):
    a = nodes[i]
    b = nodes[j]
    da = (b - a).normalized()
    add_tube(strut_bm, a + da * 0.30, b - da * 0.30, STRUT_R, segments=8)

# small hub collars where struts meet the bus
for pos in nodes:
    B = local_basis(pos)
    add_cone(node_bm, B, (0.0, 0.0, 0.0), 0.27, 0.27, 0.30, segments=12,
             rot=Matrix.Rotation(math.radians(90.0), 4, 'X'))

object_from_bmesh("Struts", strut_bm, [MAT_STRUT])
object_from_bmesh("Strut_Collars", node_bm, [MAT_STRUT])


# ----------------------------------------------------------------------------
# lighting, world and camera
# ----------------------------------------------------------------------------
world = bpy.data.worlds.new("SpaceWorld")
world.use_nodes = True
bg = world.node_tree.nodes["Background"]
bg.inputs["Color"].default_value = (0.012, 0.016, 0.030, 1.0)
bg.inputs["Strength"].default_value = 1.0
scn.world = world

sun_data = bpy.data.lights.new("KeySun", 'SUN')
sun_data.energy = 6.0
sun_data.angle = math.radians(0.6)
sun_data.color = (1.0, 0.97, 0.92)
sun = bpy.data.objects.new("KeySun", sun_data)
sun.location = (18.0, -18.0, 16.0)
sun.rotation_euler = Euler((math.radians(58.0), 0.0, math.radians(42.0)), 'XYZ')
scn.collection.objects.link(sun)

rim_data = bpy.data.lights.new("RimArea", 'AREA')
rim_data.energy = 4000.0
rim_data.size = 14.0
rim_data.color = (0.45, 0.62, 1.0)
rim = bpy.data.objects.new("RimArea", rim_data)
rim.location = (-16.0, 20.0, -10.0)
look_at(rim, (0.0, 0.0, 0.0))
scn.collection.objects.link(rim)

fill_data = bpy.data.lights.new("FillArea", 'AREA')
fill_data.energy = 1200.0
fill_data.size = 20.0
fill = bpy.data.objects.new("FillArea", fill_data)
fill.location = (-14.0, -22.0, 8.0)
look_at(fill, (0.0, 0.0, 0.0))
scn.collection.objects.link(fill)

cam_data = bpy.data.cameras.new("Camera")
cam_data.lens = 55.0
cam_data.clip_end = 300.0
cam = bpy.data.objects.new("Camera", cam_data)
cam.location = (16.0, -19.0, 11.0)
scn.collection.objects.link(cam)
look_at(cam, (0.0, 0.0, 0.0))
scn.camera = cam

print("claude-117: %d satellites, %d struts" % (len(nodes), len(pairs)))
