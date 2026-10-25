"""Compact handheld game console with buttons and a lit screen.

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
    scn.render.resolution_x = 1600
    scn.render.resolution_y = 1100


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
                 segments=28, material=None, radius_top=None):
    bm = bmesh.new()
    bmesh.ops.create_cone(
        bm, cap_ends=True, cap_tris=False, segments=segments,
        radius1=radius, radius2=(radius if radius_top is None else radius_top),
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


def setup_world(color=(0.03, 0.035, 0.045), strength=1.0):
    world = bpy.data.worlds.new("World")
    bpy.context.scene.world = world
    world.use_nodes = True
    bg = world.node_tree.nodes["Background"]
    bg.inputs[0].default_value = (color[0], color[1], color[2], 1.0)
    bg.inputs[1].default_value = strength


# ------------------------------------------------------------------ setup
reset_scene()
setup_world()

shell = make_material("Shell Plastic", (0.10, 0.115, 0.145),
                      roughness=0.36, clearcoat=0.5)
shell_light = make_material("Shell Grey", (0.30, 0.32, 0.36), roughness=0.45)
bezel = make_material("Bezel", (0.02, 0.02, 0.024), roughness=0.25)
glass = make_material("Screen Glass", (0.02, 0.03, 0.04), roughness=0.05)
screen = make_material("Screen Image", (0.10, 0.35, 0.55), roughness=0.12,
                       emission=(0.25, 0.62, 0.95), emission_strength=3.0)
btn_red = make_material("Button Red", (0.62, 0.10, 0.12), roughness=0.32)
btn_blue = make_material("Button Blue", (0.12, 0.26, 0.68), roughness=0.32)
btn_grey = make_material("Button Grey", (0.16, 0.17, 0.19), roughness=0.40)
chrome = make_material("Trim", (0.72, 0.73, 0.76), roughness=0.22,
                       metallic=1.0)
led = make_material("Power LED", (0.1, 0.9, 0.3), roughness=0.2,
                    emission=(0.2, 1.0, 0.35), emission_strength=8.0)
desk_mat = make_material("Desk", (0.09, 0.09, 0.10), roughness=0.35)


# ------------------------------------------------------------------ body
BW, BD, BT = 0.176, 0.098, 0.024      # width (X), depth (Y), thickness (Z)
TOP = BT * 0.5

body = add_box("Console Shell", (BW, BD, BT), (0.0, 0.0, 0.0),
               material=shell, bevel=0.009, segments=5)

# lighter faceplate inset just below the top surface
add_box("Faceplate", (BW - 0.014, BD - 0.014, 0.004),
        (0.0, 0.0, TOP - 0.0015),
        material=shell_light, bevel=0.003, segments=3)

# grip bulges at each end
for sx in (-1.0, 1.0):
    grip = add_cylinder("Grip", 0.030, BT * 0.98,
                        (sx * (BW * 0.5 - 0.018), -0.018, 0.0),
                        material=shell, segments=32)
    grip.scale = (1.0, 0.85, 1.0)
    smooth_shade(grip, 50.0)


# ------------------------------------------------------------------ screen
SCREEN_Y = 0.014
add_box("Screen Bezel", (0.098, 0.062, 0.005), (0.0, SCREEN_Y, TOP + 0.0005),
        material=bezel, bevel=0.002, segments=2)
add_box("Screen Panel", (0.086, 0.050, 0.002), (0.0, SCREEN_Y, TOP + 0.0026),
        material=screen)
add_box("Screen Glass", (0.090, 0.054, 0.0012), (0.0, SCREEN_Y, TOP + 0.0040),
        material=glass)

# brand strip under the screen
add_box("Brand Strip", (0.040, 0.006, 0.0015), (0.0, -0.020, TOP + 0.0012),
        material=chrome)


# ------------------------------------------------------------------ d-pad
DPAD = (-0.061, -0.034)
add_box("D-Pad Well", (0.042, 0.042, 0.003), (DPAD[0], DPAD[1], TOP + 0.0005),
        material=bezel, bevel=0.004, segments=3)
add_box("D-Pad H", (0.034, 0.012, 0.006), (DPAD[0], DPAD[1], TOP + 0.0035),
        material=btn_grey, bevel=0.002, segments=3)
add_box("D-Pad V", (0.012, 0.034, 0.006), (DPAD[0], DPAD[1], TOP + 0.0035),
        material=btn_grey, bevel=0.002, segments=3)
hub = add_cylinder("D-Pad Hub", 0.0055, 0.0065,
                   (DPAD[0], DPAD[1], TOP + 0.0038),
                   segments=20, material=btn_grey)
smooth_shade(hub)


# ------------------------------------------------------------- face buttons
FACE = (0.061, -0.032)
button_layout = (
    ("A", (0.0145, 0.0), btn_red),
    ("B", (0.0, -0.0145), btn_blue),
    ("X", (0.0, 0.0145), btn_blue),
    ("Y", (-0.0145, 0.0), btn_red),
)
for label, (dx, dy), mat in button_layout:
    ring = add_cylinder("Button Well %s" % label, 0.0085, 0.003,
                        (FACE[0] + dx, FACE[1] + dy, TOP + 0.0005),
                        segments=20, material=bezel)
    smooth_shade(ring)
    btn = add_cylinder("Button %s" % label, 0.0068, 0.005,
                       (FACE[0] + dx, FACE[1] + dy, TOP + 0.0032),
                       segments=24, material=mat)
    smooth_shade(btn)


# ------------------------------------------------- start / select / analog
for i, sx in enumerate((-1.0, 1.0)):
    pill = add_cylinder("System Button %d" % i, 0.0045, 0.0035,
                        (sx * 0.016, -0.040, TOP + 0.0025),
                        (0.0, 0.0, 0.0), segments=18, material=btn_grey)
    pill.scale = (2.1, 1.0, 1.0)
    smooth_shade(pill)

# small analog nub between screen and buttons
nub_base = add_cylinder("Stick Base", 0.010, 0.003, (0.0, -0.0025, TOP + 0.0),
                        segments=24, material=bezel)
smooth_shade(nub_base)


# ---------------------------------------------------------- speaker grille
for sx in (-1.0, 1.0):
    for row in range(2):
        for col in range(4):
            hx = sx * (0.070 - col * 0.0075)
            hy = -0.045 + row * 0.0075
            hole = add_cylinder("Grille Hole", 0.0022, 0.002,
                                (hx, hy, TOP - 0.0004),
                                segments=10, material=bezel)
            smooth_shade(hole)

# power LED
led_ob = add_cylinder("LED", 0.0022, 0.0025, (-0.078, 0.036, TOP + 0.0005),
                      segments=12, material=led)
smooth_shade(led_ob)


# -------------------------------------------------------- shoulder buttons
for sx in (-1.0, 1.0):
    add_box("Shoulder Button", (0.032, 0.014, 0.011),
            (sx * 0.058, BD * 0.5 - 0.002, 0.004),
            material=shell_light, bevel=0.004, segments=3)

# cartridge slot on the back edge
add_box("Cartridge Slot", (0.052, 0.008, 0.006),
        (0.0, BD * 0.5 - 0.003, -0.004),
        material=bezel, bevel=0.002)

# headphone jack and charge port on the bottom edge
jack = add_cylinder("Headphone Jack", 0.0045, 0.006,
                    (-0.040, -BD * 0.5 + 0.002, -0.003),
                    (math.radians(90.0), 0.0, 0.0),
                    segments=18, material=bezel)
smooth_shade(jack)
add_box("Charge Port", (0.011, 0.006, 0.004),
        (0.030, -BD * 0.5 + 0.002, -0.003), material=bezel, bevel=0.0015)


# ------------------------------------------------------------------ stage
desk = add_box("Desk", (2.0, 2.0, 0.04), (0.0, 0.0, -BT * 0.5 - 0.02),
               material=desk_mat)


# ------------------------------------------------------------------ lights
key_data = bpy.data.lights.new("Key", 'AREA')
key_data.energy = 60.0
key_data.size = 0.6
key_data.color = (1.0, 0.96, 0.92)
key = bpy.data.objects.new("Key", key_data)
bpy.context.collection.objects.link(key)
key.location = (-0.22, -0.26, 0.42)
look_at(key, (0.0, 0.0, 0.0))

fill_data = bpy.data.lights.new("Fill", 'AREA')
fill_data.energy = 22.0
fill_data.size = 0.9
fill_data.color = (0.62, 0.75, 1.0)
fill = bpy.data.objects.new("Fill", fill_data)
bpy.context.collection.objects.link(fill)
fill.location = (0.34, -0.24, 0.24)
look_at(fill, (0.0, 0.0, 0.0))

rim_data = bpy.data.lights.new("Rim", 'AREA')
rim_data.energy = 40.0
rim_data.size = 0.4
rim_data.color = (0.85, 0.90, 1.0)
rim = bpy.data.objects.new("Rim", rim_data)
bpy.context.collection.objects.link(rim)
rim.location = (0.10, 0.40, 0.26)
look_at(rim, (0.0, 0.0, 0.01))


# ------------------------------------------------------------------ camera
cam_data = bpy.data.cameras.new("Camera")
cam_data.lens = 85.0
cam = bpy.data.objects.new("Camera", cam_data)
bpy.context.collection.objects.link(cam)
cam.location = (0.14, -0.30, 0.26)
look_at(cam, (0.0, -0.004, 0.006))
bpy.context.scene.camera = cam

print("Handheld console built: %d objects" % len(bpy.context.scene.objects))
