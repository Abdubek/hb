"""Six-wheel planetary rover: chassis, rocker-bogie wheels and sensor mast.

Blender 4.5 LTS - builds the scene headlessly from factory startup.
"""

import bpy
import bmesh
import math
import random
from mathutils import Vector, Matrix


# ------------------------------------------------------------------ helpers
def reset_scene():
    bpy.ops.wm.read_factory_settings(use_empty=True)
    scn = bpy.context.scene
    scn.render.engine = 'CYCLES'
    if hasattr(scn, "cycles"):
        scn.cycles.samples = 128
    scn.render.resolution_x = 1600
    scn.render.resolution_y = 1000


def set_input(node, name, value):
    if name in node.inputs:
        node.inputs[name].default_value = value


def make_material(name, base, roughness=0.5, metallic=0.0,
                  emission=None, emission_strength=0.0):
    mat = bpy.data.materials.new(name)
    mat.use_nodes = True
    bsdf = mat.node_tree.nodes.get("Principled BSDF")
    set_input(bsdf, "Base Color", (base[0], base[1], base[2], 1.0))
    set_input(bsdf, "Roughness", roughness)
    set_input(bsdf, "Metallic", metallic)
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


def add_sphere(name, radius, location=(0, 0, 0), material=None,
               u=24, v=12, scale=(1.0, 1.0, 1.0)):
    bm = bmesh.new()
    bmesh.ops.create_uvsphere(bm, u_segments=u, v_segments=v, radius=radius)
    ob = new_mesh_object(name, bm, material)
    ob.location = location
    ob.scale = scale
    return ob


def add_strut(name, p1, p2, radius, material, segments=14):
    """Cylinder spanning two points."""
    a, b = Vector(p1), Vector(p2)
    d = b - a
    ob = add_cylinder(name, radius, max(d.length, 1e-4),
                      segments=segments, material=material)
    ob.location = (a + b) * 0.5
    ob.rotation_euler = d.to_track_quat('Z', 'Y').to_euler()
    smooth_shade(ob)
    return ob


def smooth_shade(ob, angle=40.0):
    for poly in ob.data.polygons:
        poly.use_smooth = True
    mod = ob.modifiers.new("Sharp Edges", 'EDGE_SPLIT')
    mod.split_angle = math.radians(angle)


def look_at(ob, target):
    direction = Vector(target) - ob.location
    ob.rotation_euler = direction.to_track_quat('-Z', 'Y').to_euler()


def setup_world(color=(0.16, 0.10, 0.07), strength=0.8):
    world = bpy.data.worlds.new("World")
    bpy.context.scene.world = world
    world.use_nodes = True
    bg = world.node_tree.nodes["Background"]
    bg.inputs[0].default_value = (color[0], color[1], color[2], 1.0)
    bg.inputs[1].default_value = strength


# ------------------------------------------------------------------ setup
reset_scene()
setup_world()
random.seed(7)

body_mat = make_material("Rover Body", (0.78, 0.76, 0.72),
                         roughness=0.35, metallic=0.55)
gold_foil = make_material("Thermal Foil", (0.86, 0.62, 0.16),
                          roughness=0.28, metallic=0.9)
metal = make_material("Structure", (0.42, 0.43, 0.45),
                      roughness=0.32, metallic=0.95)
dark = make_material("Dark Composite", (0.055, 0.055, 0.06), roughness=0.55)
tire = make_material("Wheel Alloy", (0.62, 0.62, 0.64),
                     roughness=0.45, metallic=0.85)
solar = make_material("Solar Cell", (0.025, 0.045, 0.13),
                      roughness=0.15, metallic=0.35)
lens = make_material("Lens", (0.02, 0.05, 0.08), roughness=0.08,
                     emission=(0.15, 0.45, 0.75), emission_strength=0.7)
regolith = make_material("Regolith", (0.40, 0.22, 0.13), roughness=0.95)
rock_mat = make_material("Rock", (0.26, 0.17, 0.12), roughness=0.9)


# ------------------------------------------------------------------ chassis
CHASSIS_Z = 0.47
chassis = add_box("Chassis", (0.92, 0.56, 0.26), (0.0, 0.0, CHASSIS_Z),
                  material=body_mat, bevel=0.025, segments=3)

# thermal blanket band around the lower body
add_box("Thermal Blanket", (0.94, 0.58, 0.075), (0.0, 0.0, 0.385),
        material=gold_foil, bevel=0.012)

# upper deck
add_box("Deck", (0.86, 0.52, 0.024), (0.0, 0.0, 0.615),
        material=body_mat, bevel=0.008)

# solar panel with cell divisions
add_box("Solar Panel", (1.12, 0.80, 0.014), (-0.02, 0.0, 0.645),
        material=solar, bevel=0.004)
for i in range(5):
    x = -0.48 + i * 0.24
    add_box("Cell Divider", (0.006, 0.80, 0.017), (x - 0.02, 0.0, 0.646),
            material=metal)
for j in range(3):
    y = -0.26 + j * 0.26
    add_box("Cell Divider Y", (1.12, 0.006, 0.017), (-0.02, y, 0.646),
            material=metal)

# instrument boxes on the deck
add_box("Electronics Box", (0.20, 0.16, 0.09), (-0.28, 0.14, 0.672),
        material=body_mat, bevel=0.010)
add_box("RTG Housing", (0.14, 0.14, 0.11), (-0.30, -0.15, 0.682),
        material=dark, bevel=0.010)
for i in range(5):
    add_box("RTG Fin", (0.17, 0.010, 0.10), (-0.30, -0.15 + (i - 2) * 0.030,
                                             0.682),
            material=metal)


# ------------------------------------------------------------------ wheels
WHEEL_R = 0.19
WHEEL_W = 0.15
WHEEL_Y = 0.375
WHEEL_X = (0.42, 0.0, -0.42)


def build_wheel(name, location):
    """Wheel with grousers, axis along X."""
    rot_y = Matrix.Rotation(math.radians(90.0), 4, 'Y')
    bm = bmesh.new()

    # rim
    bmesh.ops.create_cone(bm, cap_ends=True, cap_tris=False, segments=32,
                          radius1=WHEEL_R, radius2=WHEEL_R, depth=WHEEL_W,
                          matrix=rot_y)
    # grousers around the tread
    n = 16
    for i in range(n):
        th = (2.0 * math.pi * i) / n
        m = (Matrix.Rotation(th, 4, 'X')
             @ Matrix.Translation((0.0, WHEEL_R + 0.008, 0.0))
             @ Matrix.Diagonal(Vector((WHEEL_W * 0.92, 0.022, 0.030, 1.0))))
        bmesh.ops.create_cube(bm, size=1.0, matrix=m)

    ob = new_mesh_object(name, bm, tire)
    ob.location = location
    smooth_shade(ob, 35.0)

    # hub and spokes as a separate object
    hb = bmesh.new()
    bmesh.ops.create_cone(hb, cap_ends=True, cap_tris=False, segments=24,
                          radius1=0.055, radius2=0.055, depth=WHEEL_W + 0.03,
                          matrix=rot_y)
    for i in range(6):
        th = (2.0 * math.pi * i) / 6.0
        m = (Matrix.Rotation(th, 4, 'X')
             @ Matrix.Translation((0.0, WHEEL_R * 0.5, 0.0))
             @ Matrix.Diagonal(Vector((0.022, WHEEL_R, 0.014, 1.0))))
        bmesh.ops.create_cube(hb, size=1.0, matrix=m)
    hub = new_mesh_object(name + " Hub", hb, metal)
    hub.location = location
    smooth_shade(hub, 35.0)
    return ob


for sy in (-1.0, 1.0):
    for i, wx in enumerate(WHEEL_X):
        build_wheel("Wheel %d%s" % (i, "L" if sy < 0 else "R"),
                    (wx, sy * WHEEL_Y, WHEEL_R))


# ------------------------------------------------------------- rocker bogie
for sy in (-1.0, 1.0):
    y_arm = sy * 0.30
    y_hub = sy * (WHEEL_Y - WHEEL_W * 0.5 - 0.01)

    pivot = Vector((0.0, y_arm, 0.50))
    front_hub = Vector((WHEEL_X[0], y_arm, WHEEL_R))
    bogie_pivot = Vector((-0.20, y_arm, 0.43))
    mid_hub = Vector((WHEEL_X[1], y_arm, WHEEL_R))
    rear_hub = Vector((WHEEL_X[2], y_arm, WHEEL_R))

    add_strut("Rocker Front", pivot, front_hub, 0.024, metal)
    add_strut("Rocker Rear", pivot, bogie_pivot, 0.024, metal)
    add_strut("Bogie Fore", bogie_pivot, mid_hub, 0.020, metal)
    add_strut("Bogie Aft", bogie_pivot, rear_hub, 0.020, metal)

    # differential pivot bearing on the chassis flank
    bearing = add_cylinder("Pivot Bearing", 0.045, 0.06,
                           (0.0, sy * 0.30, 0.50),
                           (math.radians(90.0), 0.0, 0.0),
                           material=metal)
    smooth_shade(bearing)

    bogie_bear = add_cylinder("Bogie Bearing", 0.032, 0.05,
                              (-0.20, sy * 0.30, 0.43),
                              (math.radians(90.0), 0.0, 0.0),
                              material=metal)
    smooth_shade(bogie_bear)

    # axle stubs / drive motors
    for wx in WHEEL_X:
        motor = add_cylinder("Drive Motor", 0.045, 0.10,
                             (wx, (y_arm + y_hub) * 0.5, WHEEL_R),
                             (0.0, math.radians(90.0), 0.0),
                             material=dark)
        motor.rotation_euler = (math.radians(90.0), 0.0, 0.0)
        smooth_shade(motor)


# ------------------------------------------------------------- sensor mast
MAST_X = 0.32
mast_base = add_cylinder("Mast Base", 0.070, 0.06, (MAST_X, 0.0, 0.648),
                         material=body_mat)
smooth_shade(mast_base)

azimuth = add_cylinder("Azimuth Ring", 0.052, 0.035, (MAST_X, 0.0, 0.692),
                       material=metal)
smooth_shade(azimuth)

mast = add_cylinder("Mast", 0.030, 0.50, (MAST_X, 0.0, 0.955),
                    material=body_mat)
smooth_shade(mast)

elevation = add_cylinder("Elevation Joint", 0.042, 0.09,
                         (MAST_X, 0.0, 1.215),
                         (math.radians(90.0), 0.0, 0.0), material=metal)
smooth_shade(elevation)

head = add_box("Camera Head", (0.11, 0.30, 0.10), (MAST_X, 0.0, 1.275),
               material=body_mat, bevel=0.012, segments=3)

for sy in (-1.0, 1.0):
    barrel = add_cylinder("Cam Barrel", 0.028, 0.06,
                          (MAST_X + 0.075, sy * 0.085, 1.275),
                          (0.0, math.radians(90.0), 0.0), material=dark)
    smooth_shade(barrel)
    glass = add_cylinder("Cam Lens", 0.022, 0.006,
                         (MAST_X + 0.107, sy * 0.085, 1.275),
                         (0.0, math.radians(90.0), 0.0), material=lens)
    smooth_shade(glass)

# mast-top laser / spectrometer aperture
laser = add_cylinder("Spectrometer", 0.022, 0.05, (MAST_X + 0.07, 0.0, 1.340),
                     (0.0, math.radians(90.0), 0.0), material=dark)
smooth_shade(laser)
add_box("Head Sunshade", (0.13, 0.32, 0.010), (MAST_X + 0.01, 0.0, 1.335),
        material=metal, bevel=0.004)

# whip antenna
add_strut("UHF Antenna", (-0.38, 0.20, 0.63), (-0.42, 0.24, 1.05),
          0.008, metal)

# high gain dish
dish_post = add_cylinder("Dish Post", 0.022, 0.16, (-0.34, -0.16, 0.71),
                         material=metal)
smooth_shade(dish_post)
dish = add_cylinder("HGA Dish", 0.030, 0.055, (-0.34, -0.16, 0.83),
                    (math.radians(-35.0), 0.0, 0.0),
                    segments=32, material=body_mat, radius_top=0.155)
smooth_shade(dish, 50.0)


# ------------------------------------------------------------- front tools
add_box("Front Bumper", (0.05, 0.50, 0.07), (0.475, 0.0, 0.39),
        material=metal, bevel=0.008)
for sy in (-1.0, 1.0):
    haz = add_cylinder("Hazcam", 0.020, 0.030,
                       (0.50, sy * 0.14, 0.42),
                       (0.0, math.radians(90.0), 0.0), material=lens)
    smooth_shade(haz)


# ------------------------------------------------------------------ terrain
ground_mesh = bpy.data.meshes.new("Terrain")
gbm = bmesh.new()
bmesh.ops.create_grid(gbm, x_segments=48, y_segments=48, size=8.0)
for v in gbm.verts:
    d = v.co.length
    if d > 1.3:
        v.co.z += (math.sin(v.co.x * 1.7) * math.cos(v.co.y * 1.3)) * 0.06
ground_mesh_obj = new_mesh_object("Terrain", gbm, regolith)
ground_mesh_obj.location = (0.0, 0.0, 0.0)

# procedural bump on the ground material
nt = regolith.node_tree
bsdf = nt.nodes.get("Principled BSDF")
noise = nt.nodes.new("ShaderNodeTexNoise")
noise.location = (-600, -100)
noise.inputs["Scale"].default_value = 24.0
noise.inputs["Detail"].default_value = 8.0
bump = nt.nodes.new("ShaderNodeBump")
bump.location = (-350, -100)
bump.inputs["Strength"].default_value = 0.35
nt.links.new(noise.outputs["Fac"], bump.inputs["Height"])
nt.links.new(bump.outputs["Normal"], bsdf.inputs["Normal"])

# scattered rocks
for i in range(14):
    ang = random.uniform(0.0, math.tau)
    dist = random.uniform(1.1, 4.5)
    r = random.uniform(0.04, 0.16)
    rock = add_sphere("Rock %d" % i, r,
                      (math.cos(ang) * dist, math.sin(ang) * dist, r * 0.45),
                      material=rock_mat, u=10, v=6,
                      scale=(1.0, random.uniform(0.7, 1.3),
                             random.uniform(0.4, 0.8)))
    rock.rotation_euler = (0.0, 0.0, random.uniform(0.0, math.tau))


# ------------------------------------------------------------------ lights
sun_data = bpy.data.lights.new("Sun", 'SUN')
sun_data.energy = 5.0
sun_data.angle = math.radians(0.6)
sun_data.color = (1.0, 0.94, 0.84)
sun = bpy.data.objects.new("Sun", sun_data)
bpy.context.collection.objects.link(sun)
sun.location = (4.0, -3.0, 6.0)
look_at(sun, (0.0, 0.0, 0.5))

bounce_data = bpy.data.lights.new("Bounce", 'AREA')
bounce_data.energy = 180.0
bounce_data.size = 4.0
bounce_data.color = (1.0, 0.62, 0.42)
bounce = bpy.data.objects.new("Bounce", bounce_data)
bpy.context.collection.objects.link(bounce)
bounce.location = (-2.5, -2.0, 1.0)
look_at(bounce, (0.0, 0.0, 0.5))

rim_data = bpy.data.lights.new("Rim", 'AREA')
rim_data.energy = 260.0
rim_data.size = 2.0
rim_data.color = (0.7, 0.8, 1.0)
rim = bpy.data.objects.new("Rim", rim_data)
bpy.context.collection.objects.link(rim)
rim.location = (-1.8, 3.0, 2.2)
look_at(rim, (0.0, 0.0, 0.7))


# ------------------------------------------------------------------ camera
cam_data = bpy.data.cameras.new("Camera")
cam_data.lens = 55.0
cam = bpy.data.objects.new("Camera", cam_data)
bpy.context.collection.objects.link(cam)
cam.location = (2.35, -2.05, 1.35)
look_at(cam, (0.02, 0.0, 0.62))
bpy.context.scene.camera = cam

print("Rover built: %d objects" % len(bpy.context.scene.objects))
