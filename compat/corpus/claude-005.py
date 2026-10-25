"""Desktop speaker with two circular drivers (woofer and tweeter).

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
        scn.cycles.samples = 128
    scn.render.resolution_x = 1400
    scn.render.resolution_y = 1600


def set_input(node, name, value):
    if name in node.inputs:
        node.inputs[name].default_value = value


def make_material(name, base, roughness=0.5, metallic=0.0,
                  emission=None, emission_strength=0.0, clearcoat=0.0):
    mat = bpy.data.materials.new(name)
    mat.use_nodes = True
    bsdf = mat.node_tree.nodes.get("Principled BSDF")
    set_input(bsdf, "Base Color", (base[0], base[1], base[2], 1.0))
    set_input(bsdf, "Roughness", roughness)
    set_input(bsdf, "Metallic", metallic)
    if clearcoat > 0.0:
        set_input(bsdf, "Coat Weight", clearcoat)
    if emission is not None:
        set_input(bsdf, "Emission Color",
                  (emission[0], emission[1], emission[2], 1.0))
        set_input(bsdf, "Emission Strength", emission_strength)
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
            material=None, bevel=0.0, segments=3):
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
                 segments=48, material=None, radius_top=None):
    bm = bmesh.new()
    bmesh.ops.create_cone(
        bm, cap_ends=True, cap_tris=False, segments=segments,
        radius1=radius, radius2=(radius if radius_top is None else radius_top),
        depth=depth)
    ob = new_mesh_object(name, bm, material)
    ob.location = location
    ob.rotation_euler = rotation
    return ob


def add_sphere(name, radius, location=(0, 0, 0), material=None,
               u=32, v=16, scale=(1.0, 1.0, 1.0)):
    bm = bmesh.new()
    bmesh.ops.create_uvsphere(bm, u_segments=u, v_segments=v, radius=radius)
    ob = new_mesh_object(name, bm, material)
    ob.location = location
    ob.scale = scale
    return ob


def add_torus(name, major, minor, location, rotation, material,
              major_segments=64, minor_segments=14):
    bpy.ops.mesh.primitive_torus_add(
        major_radius=major, minor_radius=minor,
        major_segments=major_segments, minor_segments=minor_segments,
        location=location, rotation=rotation)
    ob = bpy.context.object
    ob.name = name
    ob.data.name = name
    ob.data.materials.append(material)
    smooth_shade(ob, 60.0)
    return ob


def smooth_shade(ob, angle=40.0):
    for poly in ob.data.polygons:
        poly.use_smooth = True
    mod = ob.modifiers.new("Sharp Edges", 'EDGE_SPLIT')
    mod.split_angle = math.radians(angle)


def look_at(ob, target):
    direction = Vector(target) - ob.location
    ob.rotation_euler = direction.to_track_quat('-Z', 'Y').to_euler()


def setup_world(color=(0.03, 0.032, 0.038), strength=1.0):
    world = bpy.data.worlds.new("World")
    bpy.context.scene.world = world
    world.use_nodes = True
    bg = world.node_tree.nodes["Background"]
    bg.inputs[0].default_value = (color[0], color[1], color[2], 1.0)
    bg.inputs[1].default_value = strength


# ------------------------------------------------------------------ setup
reset_scene()
setup_world()

cabinet_mat = make_material("Cabinet Walnut", (0.14, 0.075, 0.042),
                            roughness=0.34, clearcoat=0.4)
baffle_mat = make_material("Baffle", (0.045, 0.046, 0.05), roughness=0.55)
cone_mat = make_material("Driver Cone", (0.16, 0.155, 0.15), roughness=0.62)
surround_mat = make_material("Rubber Surround", (0.035, 0.035, 0.038),
                             roughness=0.72)
metal_mat = make_material("Cast Basket", (0.55, 0.56, 0.58),
                          roughness=0.28, metallic=1.0)
dome_mat = make_material("Silk Dome", (0.80, 0.72, 0.55),
                         roughness=0.42, metallic=0.35)
foot_mat = make_material("Rubber Foot", (0.03, 0.03, 0.032), roughness=0.85)
knob_mat = make_material("Knob", (0.68, 0.69, 0.71), roughness=0.25,
                         metallic=1.0)
led_mat = make_material("Standby LED", (0.9, 0.35, 0.1), roughness=0.2,
                        emission=(1.0, 0.35, 0.08), emission_strength=9.0)
desk_mat = make_material("Desk Surface", (0.11, 0.11, 0.12), roughness=0.4)


# ------------------------------------------------------------------ cabinet
W, D, H = 0.165, 0.190, 0.300         # X width, Y depth, Z height
FRONT = -D * 0.5                       # the baffle faces -Y
BASE_Z = 0.012                         # standing on rubber feet

cabinet = add_box("Cabinet", (W, D, H), (0.0, 0.0, BASE_Z + H * 0.5),
                  material=cabinet_mat, bevel=0.006, segments=4)

# recessed front baffle
BAFFLE_Y = FRONT + 0.004
baffle = add_box("Baffle", (W - 0.010, 0.008, H - 0.010),
                 (0.0, BAFFLE_Y, BASE_Z + H * 0.5),
                 material=baffle_mat, bevel=0.003, segments=3)

FACE_Y = BAFFLE_Y - 0.004              # front plane of the baffle
ROT_FRONT = (math.radians(90.0), 0.0, 0.0)   # local +Z -> -Y


# ------------------------------------------------------- woofer (lower driver)
WOOF_Z = BASE_Z + 0.095
WOOF_R = 0.056

# mounting flange
flange = add_cylinder("Woofer Flange", WOOF_R + 0.010, 0.006,
                      (0.0, FACE_Y - 0.001, WOOF_Z), ROT_FRONT,
                      material=metal_mat)
smooth_shade(flange)

# basket ring behind the flange
basket = add_cylinder("Woofer Basket", WOOF_R + 0.004, 0.040,
                      (0.0, FACE_Y + 0.022, WOOF_Z), ROT_FRONT,
                      material=metal_mat, radius_top=0.024)
smooth_shade(basket, 55.0)

# rubber surround
add_torus("Woofer Surround", WOOF_R - 0.007, 0.0075,
          (0.0, FACE_Y - 0.004, WOOF_Z), ROT_FRONT, surround_mat)

# cone: wide end forward (local +Z maps to -Y)
cone = add_cylinder("Woofer Cone", 0.014, 0.030,
                    (0.0, FACE_Y + 0.011, WOOF_Z), ROT_FRONT,
                    material=cone_mat, radius_top=WOOF_R - 0.011)
smooth_shade(cone, 55.0)

# dust cap
dust = add_sphere("Dust Cap", 0.016, (0.0, FACE_Y - 0.003, WOOF_Z),
                  material=dome_mat, u=32, v=16)
dust.rotation_euler = ROT_FRONT
dust.scale = (1.0, 1.0, 0.65)
smooth_shade(dust, 60.0)

# screw bosses around the flange
for i in range(6):
    th = math.tau * i / 6.0 + math.radians(30.0)
    sx = math.cos(th) * (WOOF_R + 0.004)
    sz = math.sin(th) * (WOOF_R + 0.004)
    screw = add_cylinder("Woofer Screw", 0.0035, 0.004,
                         (sx, FACE_Y - 0.003, WOOF_Z + sz), ROT_FRONT,
                         segments=14, material=metal_mat)
    smooth_shade(screw)


# ------------------------------------------------------ tweeter (upper driver)
TWEET_Z = BASE_Z + 0.228
TWEET_R = 0.030

face_plate = add_cylinder("Tweeter Faceplate", TWEET_R + 0.008, 0.005,
                          (0.0, FACE_Y - 0.001, TWEET_Z), ROT_FRONT,
                          material=metal_mat)
smooth_shade(face_plate)

waveguide = add_cylinder("Waveguide", 0.014, 0.016,
                         (0.0, FACE_Y + 0.006, TWEET_Z), ROT_FRONT,
                         material=baffle_mat, radius_top=TWEET_R)
smooth_shade(waveguide, 55.0)

add_torus("Tweeter Surround", TWEET_R - 0.014, 0.0035,
          (0.0, FACE_Y - 0.003, TWEET_Z), ROT_FRONT, surround_mat)

dome = add_sphere("Tweeter Dome", 0.014, (0.0, FACE_Y - 0.002, TWEET_Z),
                  material=dome_mat, u=32, v=16)
dome.rotation_euler = ROT_FRONT
dome.scale = (1.0, 1.0, 0.7)
smooth_shade(dome, 60.0)

for i in range(4):
    th = math.tau * i / 4.0 + math.radians(45.0)
    sx = math.cos(th) * (TWEET_R + 0.003)
    sz = math.sin(th) * (TWEET_R + 0.003)
    screw = add_cylinder("Tweeter Screw", 0.003, 0.004,
                         (sx, FACE_Y - 0.003, TWEET_Z + sz), ROT_FRONT,
                         segments=12, material=metal_mat)
    smooth_shade(screw)


# ------------------------------------------------------------- bass port
port_ring = add_cylinder("Port Ring", 0.020, 0.004,
                         (0.0, FACE_Y - 0.001, BASE_Z + 0.028), ROT_FRONT,
                         material=baffle_mat)
smooth_shade(port_ring)
port_tube = add_cylinder("Port Tube", 0.017, 0.055,
                         (0.0, FACE_Y + 0.028, BASE_Z + 0.028), ROT_FRONT,
                         material=baffle_mat)
smooth_shade(port_tube)


# ------------------------------------------------- front controls & branding
knob = add_cylinder("Volume Knob", 0.012, 0.010,
                    (0.055, FACE_Y - 0.004, BASE_Z + 0.163), ROT_FRONT,
                    segments=32, material=knob_mat)
smooth_shade(knob)
add_box("Knob Indicator", (0.0018, 0.011, 0.010),
        (0.055, FACE_Y - 0.008, BASE_Z + 0.168), material=baffle_mat)

led = add_cylinder("Standby LED", 0.0026, 0.003,
                   (-0.055, FACE_Y - 0.002, BASE_Z + 0.163), ROT_FRONT,
                   segments=14, material=led_mat)
smooth_shade(led)

add_box("Logo Badge", (0.030, 0.0018, 0.006),
        (0.0, FACE_Y - 0.001, BASE_Z + 0.163),
        material=metal_mat, bevel=0.0006, segments=2)


# ------------------------------------------------------------- rear panel
add_box("Rear Panel", (0.090, 0.006, 0.070),
        (0.0, D * 0.5 - 0.002, BASE_Z + 0.070),
        material=baffle_mat, bevel=0.002)
for sx in (-1.0, 1.0):
    post = add_cylinder("Binding Post", 0.006, 0.014,
                        (sx * 0.024, D * 0.5 + 0.004, BASE_Z + 0.055),
                        (math.radians(90.0), 0.0, 0.0),
                        segments=20, material=metal_mat)
    smooth_shade(post)
jack = add_cylinder("Input Jack", 0.008, 0.010,
                    (0.0, D * 0.5 + 0.002, BASE_Z + 0.092),
                    (math.radians(90.0), 0.0, 0.0),
                    segments=20, material=baffle_mat)
smooth_shade(jack)

# heat sink fins on the rear (powered monitor)
for i in range(6):
    add_box("Heat Fin", (0.070, 0.010, 0.004),
            (0.0, D * 0.5 + 0.006, BASE_Z + 0.150 + i * 0.012),
            material=metal_mat, bevel=0.001, segments=2)


# ------------------------------------------------------------------- feet
for sx in (-1.0, 1.0):
    for sy in (-1.0, 1.0):
        foot = add_cylinder("Foot", 0.013, 0.012,
                            (sx * (W * 0.5 - 0.022),
                             sy * (D * 0.5 - 0.024), 0.006),
                            segments=24, material=foot_mat)
        smooth_shade(foot)


# ------------------------------------------------------------------ stage
desk = add_box("Desk", (2.0, 2.0, 0.04), (0.0, 0.0, -0.02),
               material=desk_mat)
backdrop = add_box("Backdrop", (2.0, 0.04, 1.4), (0.0, 0.62, 0.70),
                   material=desk_mat)


# ------------------------------------------------------------------ lights
key_data = bpy.data.lights.new("Key", 'AREA')
key_data.energy = 160.0
key_data.size = 1.0
key_data.color = (1.0, 0.97, 0.93)
key = bpy.data.objects.new("Key", key_data)
bpy.context.collection.objects.link(key)
key.location = (-0.55, -0.75, 0.85)
look_at(key, (0.0, 0.0, 0.17))

fill_data = bpy.data.lights.new("Fill", 'AREA')
fill_data.energy = 45.0
fill_data.size = 1.4
fill_data.color = (0.62, 0.74, 1.0)
fill = bpy.data.objects.new("Fill", fill_data)
bpy.context.collection.objects.link(fill)
fill.location = (0.85, -0.55, 0.45)
look_at(fill, (0.0, 0.0, 0.16))

rim_data = bpy.data.lights.new("Rim", 'AREA')
rim_data.energy = 90.0
rim_data.size = 0.5
rim_data.color = (0.88, 0.92, 1.0)
rim = bpy.data.objects.new("Rim", rim_data)
bpy.context.collection.objects.link(rim)
rim.location = (0.45, 0.55, 0.75)
look_at(rim, (0.0, 0.03, 0.22))


# ------------------------------------------------------------------ camera
cam_data = bpy.data.cameras.new("Camera")
cam_data.lens = 80.0
cam = bpy.data.objects.new("Camera", cam_data)
bpy.context.collection.objects.link(cam)
cam.location = (0.42, -0.78, 0.34)
look_at(cam, (0.0, 0.0, 0.16))
bpy.context.scene.camera = cam

print("Desktop speaker built: %d objects" % len(bpy.context.scene.objects))
