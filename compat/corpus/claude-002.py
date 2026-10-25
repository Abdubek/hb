"""Dining table with four matching chairs.

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


def setup_world(color=(0.05, 0.055, 0.065), strength=1.0):
    world = bpy.data.worlds.new("World")
    bpy.context.scene.world = world
    world.use_nodes = True
    bg = world.node_tree.nodes["Background"]
    bg.inputs[0].default_value = (color[0], color[1], color[2], 1.0)
    bg.inputs[1].default_value = strength


# ------------------------------------------------------------------ setup
reset_scene()
setup_world()

oak = make_material("Oak", (0.42, 0.26, 0.13), roughness=0.42)
oak_dark = make_material("Oak Dark", (0.30, 0.17, 0.085), roughness=0.48)
fabric = make_material("Seat Fabric", (0.35, 0.36, 0.40), roughness=0.85)
floor_mat = make_material("Floor", (0.22, 0.19, 0.17), roughness=0.55)
wall_mat = make_material("Wall", (0.62, 0.60, 0.57), roughness=0.9)


# ------------------------------------------------------------------ table
TABLE_H = 0.755
TOP_X, TOP_Y, TOP_T = 1.60, 0.90, 0.045

top = add_box("Table Top", (TOP_X, TOP_Y, TOP_T),
              (0.0, 0.0, TABLE_H - TOP_T * 0.5),
              material=oak, bevel=0.008, segments=3)

# a thin lip under the top edge reads as a solid slab
add_box("Top Lip", (TOP_X - 0.06, TOP_Y - 0.06, 0.022),
        (0.0, 0.0, TABLE_H - TOP_T - 0.010),
        material=oak_dark, bevel=0.005)

# apron rails
APRON_Z = TABLE_H - TOP_T - 0.075
add_box("Apron Long -Y", (1.36, 0.055, 0.10), (0.0, -0.375, APRON_Z),
        material=oak_dark, bevel=0.006)
add_box("Apron Long +Y", (1.36, 0.055, 0.10), (0.0, 0.375, APRON_Z),
        material=oak_dark, bevel=0.006)
add_box("Apron Short -X", (0.055, 0.70, 0.10), (-0.705, 0.0, APRON_Z),
        material=oak_dark, bevel=0.006)
add_box("Apron Short +X", (0.055, 0.70, 0.10), (0.705, 0.0, APRON_Z),
        material=oak_dark, bevel=0.006)

# legs, gently tapered by using two stacked sections
LEG_H = TABLE_H - TOP_T
for sx in (-1.0, 1.0):
    for sy in (-1.0, 1.0):
        x, y = sx * 0.705, sy * 0.375
        add_box("Table Leg", (0.075, 0.075, LEG_H * 0.55),
                (x, y, LEG_H * 0.725),
                material=oak, bevel=0.006)
        add_box("Table Leg Taper", (0.055, 0.055, LEG_H * 0.47),
                (x, y, LEG_H * 0.235),
                material=oak, bevel=0.005)


# ------------------------------------------------------------------ chair
def build_chair(name, location, rot_z):
    """Chair built at the origin facing +Y, then parented to an empty."""
    parts = []

    SEAT_Z = 0.445
    SEAT = (0.44, 0.44, 0.045)
    LEG = 0.038
    LEAN = 0.13                     # back posts rake toward -Y
    up = Vector((0.0, -math.sin(LEAN), math.cos(LEAN)))
    back_base_y = -0.185

    # seat pad
    parts.append(add_box("Chair Seat", SEAT, (0.0, 0.0, SEAT_Z),
                         material=oak, bevel=0.010, segments=3))
    parts.append(add_box("Chair Cushion", (0.40, 0.40, 0.030),
                         (0.0, 0.0, SEAT_Z + 0.036),
                         material=fabric, bevel=0.012, segments=3))

    # front legs
    for sx in (-1.0, 1.0):
        parts.append(add_box("Chair Front Leg", (LEG, LEG, SEAT_Z),
                             (sx * 0.185, 0.185, SEAT_Z * 0.5),
                             material=oak, bevel=0.005))

    # rear legs continue upward as the back posts
    POST_LEN = 0.96
    for sx in (-1.0, 1.0):
        base = Vector((sx * 0.185, back_base_y, 0.0))
        centre = base + up * (POST_LEN * 0.5)
        parts.append(add_box("Chair Back Post", (LEG, 0.042, POST_LEN),
                             (centre.x, centre.y, centre.z),
                             (LEAN, 0.0, 0.0),
                             material=oak, bevel=0.005))

    # stretchers
    parts.append(add_box("Stretcher Front", (0.335, 0.028, 0.028),
                         (0.0, 0.185, 0.175), material=oak, bevel=0.004))
    parts.append(add_box("Stretcher Back", (0.335, 0.028, 0.028),
                         (0.0, -0.208, 0.175), material=oak, bevel=0.004))
    for sx in (-1.0, 1.0):
        parts.append(add_box("Stretcher Side", (0.028, 0.375, 0.028),
                             (sx * 0.185, -0.012, 0.205),
                             material=oak, bevel=0.004))

    # backrest slats
    for i, t in enumerate((0.56, 0.685, 0.81)):
        p = Vector((0.0, back_base_y, 0.0)) + up * t
        p += Vector((0.0, 0.030 * math.cos(LEAN), 0.030 * math.sin(LEAN)))
        parts.append(add_box("Back Slat %d" % (i + 1), (0.335, 0.022, 0.070),
                             (p.x, p.y, p.z), (LEAN, 0.0, 0.0),
                             material=oak, bevel=0.006, segments=3))

    # crest rail
    crest = Vector((0.0, back_base_y, 0.0)) + up * 0.925
    parts.append(add_box("Crest Rail", (0.395, 0.034, 0.075),
                         (crest.x, crest.y, crest.z), (LEAN, 0.0, 0.0),
                         material=oak, bevel=0.010, segments=3))

    # felt glides
    for sx in (-1.0, 1.0):
        for py in (0.185, back_base_y):
            glide = add_cylinder("Glide", 0.020, 0.006,
                                 (sx * 0.185, py, 0.003),
                                 segments=16, material=oak_dark)
            smooth_shade(glide)
            parts.append(glide)

    root = bpy.data.objects.new(name, None)
    bpy.context.collection.objects.link(root)
    root.empty_display_size = 0.25
    root.location = location
    root.rotation_euler = (0.0, 0.0, rot_z)
    for p in parts:
        p.parent = root
    return root


# four chairs, two per long side, slightly staggered so it reads naturally
build_chair("Chair A", (-0.42, -0.86, 0.0), math.radians(4.0))
build_chair("Chair B", (0.44, -0.90, 0.0), math.radians(-7.0))
build_chair("Chair C", (-0.44, 0.88, 0.0), math.radians(180.0 - 5.0))
build_chair("Chair D", (0.42, 0.86, 0.0), math.radians(180.0 + 6.0))


# ------------------------------------------------------------------ room
add_box("Floor", (10.0, 10.0, 0.1), (0.0, 0.0, -0.05), material=floor_mat)
add_box("Back Wall", (10.0, 0.12, 3.0), (0.0, 3.0, 1.5), material=wall_mat)
add_box("Side Wall", (0.12, 10.0, 3.0), (-3.4, 0.0, 1.5), material=wall_mat)


# ------------------------------------------------------------------ lights
key_data = bpy.data.lights.new("Key", 'AREA')
key_data.energy = 420.0
key_data.size = 1.6
key_data.color = (1.0, 0.93, 0.84)
key = bpy.data.objects.new("Key", key_data)
bpy.context.collection.objects.link(key)
key.location = (0.0, -0.2, 2.35)
look_at(key, (0.0, 0.0, 0.75))

fill_data = bpy.data.lights.new("Fill", 'AREA')
fill_data.energy = 150.0
fill_data.size = 2.5
fill_data.color = (0.75, 0.84, 1.0)
fill = bpy.data.objects.new("Fill", fill_data)
bpy.context.collection.objects.link(fill)
fill.location = (-2.6, -2.4, 1.9)
look_at(fill, (0.0, 0.0, 0.7))

rim_data = bpy.data.lights.new("Rim", 'AREA')
rim_data.energy = 200.0
rim_data.size = 1.2
rim = bpy.data.objects.new("Rim", rim_data)
bpy.context.collection.objects.link(rim)
rim.location = (2.4, 2.2, 2.1)
look_at(rim, (0.0, 0.2, 0.8))


# ------------------------------------------------------------------ camera
cam_data = bpy.data.cameras.new("Camera")
cam_data.lens = 40.0
cam = bpy.data.objects.new("Camera", cam_data)
bpy.context.collection.objects.link(cam)
cam.location = (2.7, -3.1, 1.95)
look_at(cam, (0.0, 0.0, 0.62))
bpy.context.scene.camera = cam

print("Dining set built: %d objects" % len(bpy.context.scene.objects))
