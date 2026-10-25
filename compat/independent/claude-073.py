import bpy
import math
from mathutils import Vector

# Regulation-ish tennis court, length along X, width along Y, net at X = 0.
HALF_LEN = 11.885
SINGLES_Y = 4.115
DOUBLES_Y = 5.485
SERVICE_X = 6.40
POST_Y = 6.40
POST_H = 1.07
NET_CENTER_H = 0.914
LINE_W = 0.05
LINE_Z = 0.006


def make_material(name, color, roughness=0.6, metallic=0.0):
    mat = bpy.data.materials.new(name)
    mat.use_nodes = True
    bsdf = mat.node_tree.nodes["Principled BSDF"]
    bsdf.inputs["Base Color"].default_value = (color[0], color[1], color[2], 1.0)
    bsdf.inputs["Roughness"].default_value = roughness
    bsdf.inputs["Metallic"].default_value = metallic
    return mat


def add_box(name, size, location, material):
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=location)
    obj = bpy.context.object
    obj.name = name
    obj.scale = size
    obj.data.materials.append(material)
    return obj


def add_cylinder(name, radius, depth, location, material, verts=16):
    bpy.ops.mesh.primitive_cylinder_add(radius=radius, depth=depth, vertices=verts,
                                        location=location)
    obj = bpy.context.object
    obj.name = name
    obj.data.materials.append(material)
    return obj


def add_line(name, x, y, length_x, length_y, material):
    size = (length_x if length_x else LINE_W, length_y if length_y else LINE_W, 0.012)
    return add_box(name, size, (x, y, LINE_Z), material)


def net_top(y):
    """Height of the net cord at a given lateral position (sags toward the centre)."""
    t = abs(y) / POST_Y
    return NET_CENTER_H + (POST_H - NET_CENTER_H) * (t ** 2)


def build_strip(name, z_lo_fn, z_hi_fn, material, columns=32):
    """Vertical strip at X=0 spanning between two height functions of y."""
    verts = []
    faces = []
    for i in range(columns + 1):
        y = -POST_Y + 2.0 * POST_Y * i / columns
        verts.append((0.0, y, z_lo_fn(y)))
        verts.append((0.0, y, z_hi_fn(y)))
    for i in range(columns):
        a = 2 * i
        faces.append((a, a + 2, a + 3, a + 1))
    mesh = bpy.data.meshes.new(name)
    mesh.from_pydata(verts, [], faces)
    mesh.update()
    mesh.materials.append(material)
    obj = bpy.data.objects.new(name, mesh)
    bpy.context.collection.objects.link(obj)
    return obj


def aim_camera(location, target, lens=35.0):
    cam_data = bpy.data.cameras.new("CourtCam")
    cam_data.lens = lens
    cam = bpy.data.objects.new("CourtCam", cam_data)
    bpy.context.collection.objects.link(cam)
    cam.location = location
    cam.rotation_euler = (Vector(target) - Vector(location)).to_track_quat('-Z', 'Y').to_euler()
    bpy.context.scene.camera = cam
    return cam


# ---------------------------------------------------------------- materials
mat_surround = make_material("SurroundAsphalt", (0.09, 0.24, 0.42), roughness=0.9)
mat_playing = make_material("PlayingSurface", (0.12, 0.42, 0.26), roughness=0.85)
mat_line = make_material("CourtLine", (0.94, 0.94, 0.92), roughness=0.55)
mat_post = make_material("MetalPost", (0.22, 0.23, 0.25), roughness=0.4, metallic=0.8)
mat_net = make_material("NetMesh", (0.05, 0.05, 0.06), roughness=0.9)
mat_tape = make_material("NetTape", (0.93, 0.93, 0.91), roughness=0.6)

# ---------------------------------------------------------------- surfaces
add_box("Surround", (36.0, 18.5, 0.10), (0.0, 0.0, -0.05), mat_surround)
add_box("PlayingSurface", (30.0, 14.0, 0.06), (0.0, 0.0, -0.01), mat_playing)

# ---------------------------------------------------------------- court lines
for sign in (-1, 1):
    tag = "far" if sign > 0 else "near"
    side = "left" if sign > 0 else "right"
    add_line("Baseline_%s" % tag, sign * HALF_LEN, 0.0, 0.0,
             2 * DOUBLES_Y + LINE_W, mat_line)
    add_line("DoublesSideline_%s" % side, 0.0, sign * DOUBLES_Y,
             2 * HALF_LEN, 0.0, mat_line)
    add_line("SinglesSideline_%s" % side, 0.0, sign * SINGLES_Y,
             2 * HALF_LEN, 0.0, mat_line)
    add_line("ServiceLine_%s" % tag, sign * SERVICE_X, 0.0, 0.0,
             2 * SINGLES_Y, mat_line)
    add_line("CenterMark_%s" % tag, sign * (HALF_LEN - 0.10), 0.0, 0.20, 0.0, mat_line)

add_line("CenterServiceLine", 0.0, 0.0, 2 * SERVICE_X, 0.0, mat_line)

# ---------------------------------------------------------------- net assembly
for sign in (-1, 1):
    side = "left" if sign > 0 else "right"
    add_cylinder("NetPost_%s" % side, 0.06, POST_H + 0.30,
                 (0.0, sign * POST_Y, (POST_H - 0.30) * 0.5), mat_post)
    add_cylinder("NetPostCap_%s" % side, 0.07, 0.04,
                 (0.0, sign * POST_Y, POST_H + 0.02), mat_post)

build_strip("NetMesh", lambda y: 0.0, lambda y: net_top(y) - 0.055, mat_net)
build_strip("NetTape", lambda y: net_top(y) - 0.055, net_top, mat_tape)
add_box("CenterStrap", (0.02, 0.05, NET_CENTER_H),
        (0.0, 0.0, NET_CENTER_H * 0.5), mat_tape)

# ---------------------------------------------------------------- perimeter posts
PERIM_X = 16.5
PERIM_Y = 8.5
FENCE_H = 3.0
perimeter = []
for i in range(9):
    x = -PERIM_X + 2 * PERIM_X * i / 8.0
    perimeter.append((x, -PERIM_Y))
    perimeter.append((x, PERIM_Y))
for j in range(1, 4):
    y = -PERIM_Y + 2 * PERIM_Y * j / 4.0
    perimeter.append((-PERIM_X, y))
    perimeter.append((PERIM_X, y))

for idx, (px, py) in enumerate(perimeter):
    add_cylinder("PerimeterPost_%02d" % idx, 0.05, FENCE_H,
                 (px, py, FENCE_H * 0.5 - 0.10), mat_post, verts=12)
    add_box("PostFooting_%02d" % idx, (0.24, 0.24, 0.12), (px, py, 0.02), mat_surround)

# ---------------------------------------------------------------- lighting + camera
sun_data = bpy.data.lights.new("CourtSun", type='SUN')
sun_data.energy = 4.5
sun = bpy.data.objects.new("CourtSun", sun_data)
bpy.context.collection.objects.link(sun)
sun.location = (10.0, -12.0, 20.0)
sun.rotation_euler = (math.radians(48.0), 0.0, math.radians(30.0))

aim_camera((-23.0, -19.0, 13.0), (0.0, 0.0, 1.0))
