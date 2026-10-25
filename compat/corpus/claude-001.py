"""Two-seat park bench with slatted back and seat.

Blender 4.5 LTS - builds the scene headlessly from factory startup.
"""

import bpy
import bmesh
import math
from mathutils import Vector, Matrix


# ------------------------------------------------------------------ helpers
def reset_scene():
    bpy.ops.wm.read_factory_settings(use_empty=True)
    scn = bpy.context.scene
    scn.render.engine = 'CYCLES'
    if hasattr(scn, "cycles"):
        scn.cycles.samples = 96
    scn.render.resolution_x = 1600
    scn.render.resolution_y = 1000
    scn.render.film_transparent = False


def set_input(node, name, value):
    if name in node.inputs:
        node.inputs[name].default_value = value


def make_material(name, base, roughness=0.5, metallic=0.0):
    mat = bpy.data.materials.new(name)
    mat.use_nodes = True
    bsdf = mat.node_tree.nodes.get("Principled BSDF")
    set_input(bsdf, "Base Color", (base[0], base[1], base[2], 1.0))
    set_input(bsdf, "Roughness", roughness)
    set_input(bsdf, "Metallic", metallic)
    return mat


def new_mesh_object(name, bm, material=None):
    me = bpy.data.meshes.new(name)
    bm.to_mesh(me)
    bm.free()
    ob = bpy.data.objects.new(name, me)
    bpy.context.collection.objects.link(ob)
    if material is not None:
        me.materials.append(material)
    return ob


def add_box(name, size, location=(0, 0, 0), rotation=(0, 0, 0),
            material=None, bevel=0.0, segments=2):
    bm = bmesh.new()
    bmesh.ops.create_cube(
        bm, size=1.0,
        matrix=Matrix.Diagonal(Vector((size[0], size[1], size[2], 1.0))))
    if bevel > 0.0:
        bmesh.ops.bevel(bm, geom=list(bm.verts) + list(bm.edges),
                        offset=bevel, offset_type='OFFSET',
                        segments=segments, profile=0.5,
                        affect='EDGES', clamp_overlap=True)
    ob = new_mesh_object(name, bm, material)
    ob.location = location
    ob.rotation_euler = rotation
    return ob


def add_cylinder(name, radius, depth, location=(0, 0, 0), rotation=(0, 0, 0),
                 segments=24, material=None):
    bm = bmesh.new()
    bmesh.ops.create_cone(bm, cap_ends=True, cap_tris=False,
                          segments=segments, radius1=radius, radius2=radius,
                          depth=depth)
    ob = new_mesh_object(name, bm, material)
    ob.location = location
    ob.rotation_euler = rotation
    return ob


def smooth_shade(ob, angle=40.0):
    for poly in ob.data.polygons:
        poly.use_smooth = True
    mod = ob.modifiers.new("Sharp Edges", 'EDGE_SPLIT')
    mod.split_angle = math.radians(angle)


def look_at(ob, target):
    direction = Vector(target) - ob.location
    ob.rotation_euler = direction.to_track_quat('-Z', 'Y').to_euler()


def setup_world(color=(0.30, 0.40, 0.52), strength=1.2):
    world = bpy.data.worlds.new("World")
    bpy.context.scene.world = world
    world.use_nodes = True
    bg = world.node_tree.nodes["Background"]
    bg.inputs[0].default_value = (color[0], color[1], color[2], 1.0)
    bg.inputs[1].default_value = strength


# ------------------------------------------------------------------ build
reset_scene()
setup_world()

wood = make_material("Bench Wood", (0.34, 0.17, 0.075), roughness=0.52)
steel = make_material("Cast Iron", (0.035, 0.038, 0.042),
                      roughness=0.42, metallic=0.9)
ground_mat = make_material("Path", (0.30, 0.30, 0.29), roughness=0.92)

# bench dimensions
SEAT_W = 1.24            # along X (two seats)
SEAT_Z = 0.44            # top of seat slats
FRAME_X = 0.56           # side frames
LEAN = -0.21             # back rake, radians about X

sin_l = math.sin(LEAN)
cos_l = math.cos(LEAN)
up = Vector((0.0, -sin_l, cos_l))          # direction along the rear post

# ---- ground
ground = add_box("Ground", (14.0, 14.0, 0.2), (0.0, 0.0, -0.1),
                 material=ground_mat)

frame_parts = []
for side in (-1.0, 1.0):
    x = side * FRAME_X

    # front leg
    frame_parts.append(add_box(
        "Front Leg", (0.055, 0.07, 0.42), (x, -0.20, 0.21),
        material=steel, bevel=0.008))

    # rear leg, continues upward as the back post
    post_base = Vector((x, 0.081, 0.0))
    post_len = 0.93
    post_c = post_base + up * (post_len * 0.5)
    frame_parts.append(add_box(
        "Rear Post", (0.05, 0.065, post_len), post_c, (LEAN, 0.0, 0.0),
        material=steel, bevel=0.008))

    # seat bearer connecting the two legs
    frame_parts.append(add_box(
        "Seat Bearer", (0.05, 0.50, 0.055), (x, -0.02, 0.40),
        material=steel, bevel=0.008))

    # lower stretcher
    frame_parts.append(add_box(
        "Stretcher", (0.035, 0.44, 0.035), (x, -0.01, 0.13),
        material=steel, bevel=0.006))

    # armrest and its front support
    frame_parts.append(add_box(
        "Armrest", (0.05, 0.46, 0.038), (x, -0.02, 0.665),
        material=wood, bevel=0.012, segments=3))
    frame_parts.append(add_box(
        "Arm Support", (0.04, 0.045, 0.27), (x, -0.20, 0.545),
        material=steel, bevel=0.006))

    # decorative scroll under the armrest
    scroll = add_cylinder("Arm Scroll", 0.05, 0.035,
                          (x, -0.20, 0.645), (0.0, math.pi * 0.5, 0.0),
                          segments=24, material=steel)
    smooth_shade(scroll)
    frame_parts.append(scroll)

# ---- seat slats (4, running the full width)
for i, y in enumerate((-0.235, -0.115, 0.005, 0.125)):
    add_box("Seat Slat %d" % (i + 1), (SEAT_W, 0.105, 0.028),
            (0.0, y, SEAT_Z), material=wood, bevel=0.008, segments=3)

# ---- back slats, following the rake of the rear posts
for i, t in enumerate((0.51, 0.645, 0.78, 0.905)):
    p = Vector((0.0, 0.081, 0.0)) + up * t
    # push each slat slightly forward so it sits in front of the posts
    p += Vector((0.0, -0.037 * cos_l, -0.037 * -sin_l))
    add_box("Back Slat %d" % (i + 1), (SEAT_W, 0.024, 0.10),
            (p.x, p.y, p.z), (LEAN, 0.0, 0.0),
            material=wood, bevel=0.007, segments=3)

# ---- centre support frame (bench is two-seat, so it gets a middle leg)
add_box("Centre Bearer", (0.04, 0.50, 0.05), (0.0, -0.02, 0.40),
        material=steel, bevel=0.006)
add_box("Centre Leg", (0.04, 0.055, 0.40), (0.0, -0.18, 0.20),
        material=steel, bevel=0.006)

# ---- ground fixings
for side in (-1.0, 1.0):
    for y in (-0.20, 0.081):
        pad = add_cylinder("Foot Pad", 0.055, 0.018,
                           (side * FRAME_X, y, 0.009),
                           segments=20, material=steel)
        smooth_shade(pad)


# ------------------------------------------------------------------ lights
sun_data = bpy.data.lights.new("Sun", 'SUN')
sun_data.energy = 3.6
sun_data.angle = math.radians(2.0)
sun_data.color = (1.0, 0.95, 0.86)
sun = bpy.data.objects.new("Sun", sun_data)
bpy.context.collection.objects.link(sun)
sun.location = (3.0, -3.5, 5.0)
look_at(sun, (0.0, 0.1, 0.4))

fill_data = bpy.data.lights.new("Fill", 'AREA')
fill_data.energy = 120.0
fill_data.size = 3.0
fill_data.color = (0.72, 0.82, 1.0)
fill = bpy.data.objects.new("Fill", fill_data)
bpy.context.collection.objects.link(fill)
fill.location = (-2.6, -1.8, 2.0)
look_at(fill, (0.0, 0.0, 0.45))

rim_data = bpy.data.lights.new("Rim", 'AREA')
rim_data.energy = 90.0
rim_data.size = 2.0
rim = bpy.data.objects.new("Rim", rim_data)
bpy.context.collection.objects.link(rim)
rim.location = (-1.2, 3.0, 1.8)
look_at(rim, (0.0, 0.15, 0.6))


# ------------------------------------------------------------------ camera
cam_data = bpy.data.cameras.new("Camera")
cam_data.lens = 52.0
cam = bpy.data.objects.new("Camera", cam_data)
bpy.context.collection.objects.link(cam)
cam.location = (2.05, -2.45, 1.40)
look_at(cam, (0.0, 0.0, 0.48))
bpy.context.scene.camera = cam

print("Park bench built: %d objects" % len(bpy.context.scene.objects))
