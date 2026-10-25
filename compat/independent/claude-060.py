import bpy
import math
from mathutils import Vector


def clear_scene():
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete(use_global=False)
    for coll in (bpy.data.meshes, bpy.data.materials, bpy.data.cameras, bpy.data.lights):
        for item in list(coll):
            if item.users == 0:
                coll.remove(item)


def make_material(name, color, roughness=0.5, metallic=0.0, emission=0.0):
    mat = bpy.data.materials.new(name)
    mat.use_nodes = True
    bsdf = mat.node_tree.nodes["Principled BSDF"]
    bsdf.inputs["Base Color"].default_value = (*color, 1.0)
    bsdf.inputs["Roughness"].default_value = roughness
    bsdf.inputs["Metallic"].default_value = metallic
    if emission > 0.0:
        bsdf.inputs["Emission Color"].default_value = (*color, 1.0)
        bsdf.inputs["Emission Strength"].default_value = emission
    return mat


def add_box(name, location, dims, material, rotation=(0.0, 0.0, 0.0)):
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=location, rotation=rotation)
    ob = bpy.context.active_object
    ob.name = name
    ob.scale = dims
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    ob.data.materials.append(material)
    return ob


def add_cylinder(name, location, radius, depth, material, rotation=(0.0, 0.0, 0.0), verts=24):
    bpy.ops.mesh.primitive_cylinder_add(vertices=verts, radius=radius, depth=depth,
                                        location=location, rotation=rotation)
    ob = bpy.context.active_object
    ob.name = name
    ob.data.materials.append(material)
    return ob


def build_lounge_chair(prefix, x, y, facing, fabric, frame):
    """Boxy armchair on four slim legs, parented to an empty so it can face the desk."""
    parts = [add_box(prefix + "_Seat", (x, y, 0.40), (0.72, 0.70, 0.16), fabric),
             add_box(prefix + "_Back", (x, y + 0.30, 0.62), (0.72, 0.12, 0.60), fabric)]
    for side, sx in (("L", -0.36), ("R", 0.36)):
        parts.append(add_box(prefix + "_Arm" + side, (x + sx, y, 0.52), (0.10, 0.68, 0.40), fabric))
    for lx in (-0.29, 0.29):
        for ly in (-0.27, 0.27):
            parts.append(add_cylinder(prefix + "_Leg", (x + lx, y + ly, 0.16), 0.026, 0.32, frame, verts=12))
    pivot = bpy.data.objects.new(prefix, None)
    bpy.context.collection.objects.link(pivot)
    pivot.location = (x, y, 0.0)
    for p in parts:
        p.parent = pivot
        p.matrix_parent_inverse = pivot.matrix_world.inverted()
    pivot.rotation_euler = (0.0, 0.0, facing)
    return pivot


def add_camera(location, target, lens=35.0):
    cam_data = bpy.data.cameras.new("ReceptionCamera")
    cam_data.lens = lens
    cam = bpy.data.objects.new("ReceptionCamera", cam_data)
    bpy.context.collection.objects.link(cam)
    cam.location = location
    direction = Vector(target) - Vector(location)
    cam.rotation_euler = direction.to_track_quat('-Z', 'Y').to_euler()
    bpy.context.scene.camera = cam
    return cam


clear_scene()

floor_mat = make_material("Mat_PolishedFloor", (0.17, 0.16, 0.15), roughness=0.18)
wall_mat = make_material("Mat_Wall", (0.86, 0.83, 0.78), roughness=0.85)
panel_mat = make_material("Mat_WalnutPanel", (0.21, 0.11, 0.06), roughness=0.42)
stone_mat = make_material("Mat_StoneTop", (0.90, 0.88, 0.84), roughness=0.25)
brass_mat = make_material("Mat_Brass", (0.72, 0.55, 0.20), roughness=0.28, metallic=1.0)
fabric_mat = make_material("Mat_Upholstery", (0.16, 0.27, 0.31), roughness=0.80)
glow_mat = make_material("Mat_SignGlow", (1.0, 0.92, 0.72), roughness=0.4, emission=4.0)
plant_mat = make_material("Mat_Foliage", (0.10, 0.26, 0.12), roughness=0.75)
screen_mat = make_material("Mat_Screen", (0.05, 0.06, 0.08), roughness=0.15)

# --- lobby shell -------------------------------------------------------
add_box("Floor", (0.0, -1.5, -0.05), (11.0, 10.0, 0.1), floor_mat)
add_box("BackWall", (0.0, 1.60, 1.70), (11.0, 0.2, 3.4), wall_mat)
add_box("WallPanel", (0.0, 1.47, 1.55), (6.4, 0.06, 2.6), panel_mat)

# --- reception desk ----------------------------------------------------
add_box("Desk_Body", (-0.30, 0.75, 0.53), (3.60, 0.75, 1.06), panel_mat)
add_box("Desk_Top", (-0.30, 0.73, 1.09), (3.76, 0.86, 0.06), stone_mat)
add_box("Desk_Kick", (-0.30, 0.80, 0.05), (3.40, 0.60, 0.10), stone_mat)
add_box("Desk_Return", (1.62, -0.05, 0.53), (0.75, 0.85, 1.06), panel_mat)
add_box("Desk_ReturnTop", (1.62, -0.05, 1.09), (0.86, 0.95, 0.06), stone_mat)
add_box("Desk_BrassReveal", (-0.30, 0.36, 0.86), (3.60, 0.02, 0.05), brass_mat)
add_box("Desk_LowerCounter", (-1.90, 0.60, 0.38), (0.90, 0.55, 0.76), panel_mat)
add_box("Desk_LowerTop", (-1.90, 0.60, 0.78), (1.00, 0.65, 0.05), stone_mat)

# --- counter props -----------------------------------------------------
add_box("Monitor_Screen", (0.55, 0.95, 1.38), (0.44, 0.03, 0.28), screen_mat)
add_cylinder("Monitor_Stand", (0.55, 0.95, 1.18), 0.05, 0.12, brass_mat, verts=16)
add_box("GuestBook", (-1.10, 0.55, 1.14), (0.30, 0.22, 0.04),
        make_material("Mat_Book", (0.38, 0.09, 0.11), roughness=0.6))
add_cylinder("BellBase", (-1.90, 0.55, 0.82), 0.07, 0.03, brass_mat, verts=20)
bpy.ops.mesh.primitive_uv_sphere_add(radius=0.055, location=(-1.90, 0.55, 0.86),
                                     segments=20, ring_count=10)
bell = bpy.context.active_object
bell.name = "ServiceBell"
bell.scale = (1.0, 1.0, 0.7)
bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
bell.data.materials.append(brass_mat)

# --- wall sign: dark backer with brass block letters -------------------
add_box("Sign_Backer", (-0.30, 1.42, 2.35), (2.60, 0.05, 0.62),
        make_material("Mat_SignBacker", (0.09, 0.09, 0.10), roughness=0.55))
letters = (("H", 0.26), ("O", 0.26), ("T", 0.24), ("E", 0.22), ("L", 0.22))
cursor = -1.24
for letter, width in letters:
    add_box("SignLetter_" + letter, (cursor + width * 0.5, 1.33, 2.35),
            (width, 0.06, 0.34), brass_mat)
    cursor += width + 0.13
add_box("Sign_GlowStrip", (-0.30, 1.38, 2.06), (2.50, 0.04, 0.03), glow_mat)

# --- waiting area ------------------------------------------------------
build_lounge_chair("Chair_A", -1.55, -2.30, math.radians(155.0), fabric_mat, brass_mat)
build_lounge_chair("Chair_B", -0.05, -2.65, math.radians(180.0), fabric_mat, brass_mat)
add_cylinder("CoffeeTable_Top", (-0.85, -1.85, 0.42), 0.42, 0.05, stone_mat, verts=32)
add_cylinder("CoffeeTable_Column", (-0.85, -1.85, 0.20), 0.07, 0.40, brass_mat, verts=16)
add_cylinder("CoffeeTable_Base", (-0.85, -1.85, 0.02), 0.26, 0.04, brass_mat, verts=32)

add_cylinder("Planter_Pot", (2.55, -1.10, 0.28), 0.28, 0.56, stone_mat, verts=28)
bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=2, radius=0.42, location=(2.55, -1.10, 0.85))
bush = bpy.context.active_object
bush.name = "Planter_Foliage"
bush.scale = (1.0, 1.0, 1.25)
bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
bush.data.materials.append(plant_mat)

# --- pendant lamps over the desk ---------------------------------------
for i, px in enumerate((-1.60, -0.30, 1.00)):
    add_cylinder("Pendant_Cord_%d" % i, (px, 0.10, 2.72), 0.012, 0.80, brass_mat, verts=10)
    bpy.ops.mesh.primitive_cone_add(vertices=24, radius1=0.16, radius2=0.05, depth=0.22,
                                    location=(px, 0.10, 2.25))
    shade = bpy.context.active_object
    shade.name = "Pendant_Shade_%d" % i
    shade.data.materials.append(brass_mat)
    add_cylinder("Pendant_Bulb_%d" % i, (px, 0.10, 2.15), 0.045, 0.05, glow_mat, verts=12)

# --- lighting and camera ----------------------------------------------
sun_data = bpy.data.lights.new("KeySun", type='SUN')
sun_data.energy = 2.2
sun = bpy.data.objects.new("KeySun", sun_data)
bpy.context.collection.objects.link(sun)
sun.location = (4.0, -5.0, 6.0)
sun.rotation_euler = (math.radians(52.0), 0.0, math.radians(35.0))

fill_data = bpy.data.lights.new("LobbyFill", type='AREA')
fill_data.energy = 320.0
fill_data.size = 4.0
fill = bpy.data.objects.new("LobbyFill", fill_data)
bpy.context.collection.objects.link(fill)
fill.location = (-1.0, -3.5, 3.0)
fill.rotation_euler = (math.radians(35.0), 0.0, 0.0)

add_camera((4.6, -5.6, 2.35), (-0.35, -0.30, 1.15), lens=34.0)
world = bpy.data.worlds.new("ReceptionWorld")
world.use_nodes = True
world.node_tree.nodes["Background"].inputs["Color"].default_value = (0.05, 0.05, 0.06, 1.0)
bpy.context.scene.world = world
