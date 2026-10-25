import bpy
import math
import random
from mathutils import Vector

random.seed(7)


def clear_scene():
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete(use_global=False)
    for coll in (bpy.data.meshes, bpy.data.materials, bpy.data.cameras, bpy.data.lights):
        for item in list(coll):
            if item.users == 0:
                coll.remove(item)


def make_material(name, color, roughness=0.6, metallic=0.0, emission=0.0):
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


def add_cylinder(name, location, radius, depth, material, rotation=(0.0, 0.0, 0.0), verts=20):
    bpy.ops.mesh.primitive_cylinder_add(vertices=verts, radius=radius, depth=depth,
                                        location=location, rotation=rotation)
    ob = bpy.context.active_object
    ob.name = name
    ob.data.materials.append(material)
    return ob


def add_log(name, location, radius, length, material, tilt=0.0):
    """Log lying with its axis along X, yawed slightly for a loose stack."""
    return add_cylinder(name, location, radius, length, material,
                        rotation=(0.0, math.radians(90.0), tilt), verts=12)


def build_stone_course(prefix, y, z, x_start, x_end, height, depth, material):
    """One row of irregular blocks for the chimney facing."""
    x = x_start
    idx = 0
    while x < x_end - 0.05:
        w = min(random.uniform(0.22, 0.40), x_end - x)
        add_box("%s_Stone_%02d" % (prefix, idx), (x + w * 0.5, y, z),
                (w * 0.96, depth, height * 0.94), material)
        x += w
        idx += 1


def add_camera(location, target, lens=40.0):
    cam_data = bpy.data.cameras.new("FireplaceCamera")
    cam_data.lens = lens
    cam = bpy.data.objects.new("FireplaceCamera", cam_data)
    bpy.context.collection.objects.link(cam)
    cam.location = location
    direction = Vector(target) - Vector(location)
    cam.rotation_euler = direction.to_track_quat('-Z', 'Y').to_euler()
    bpy.context.scene.camera = cam
    return cam


clear_scene()

plaster_mat = make_material("Mat_Plaster", (0.82, 0.79, 0.73), roughness=0.9)
floor_mat = make_material("Mat_OakFloor", (0.32, 0.19, 0.09), roughness=0.45)
stone_mat = make_material("Mat_Limestone", (0.60, 0.57, 0.51), roughness=0.78)
hearth_mat = make_material("Mat_HearthSlab", (0.30, 0.29, 0.28), roughness=0.55)
firebrick_mat = make_material("Mat_Firebrick", (0.14, 0.10, 0.08), roughness=0.92)
mantel_mat = make_material("Mat_MantelOak", (0.24, 0.13, 0.06), roughness=0.40)
iron_mat = make_material("Mat_CastIron", (0.06, 0.06, 0.07), roughness=0.45, metallic=0.9)
bark_mat = make_material("Mat_Bark", (0.23, 0.15, 0.09), roughness=0.88)
split_mat = make_material("Mat_SplitWood", (0.60, 0.44, 0.26), roughness=0.80)
ember_mat = make_material("Mat_Embers", (1.0, 0.34, 0.06), roughness=0.9, emission=9.0)
flame_mat = make_material("Mat_Flame", (1.0, 0.60, 0.18), roughness=0.9, emission=14.0)
candle_mat = make_material("Mat_Candle", (0.93, 0.90, 0.80), roughness=0.5)

# --- room shell --------------------------------------------------------
add_box("Floor", (0.0, -1.60, -0.04), (6.0, 5.0, 0.08), floor_mat)
add_box("BackWall", (0.0, 0.55, 1.60), (6.0, 0.20, 3.20), plaster_mat)

# --- hearth ------------------------------------------------------------
add_box("Hearth_Slab", (0.0, -0.28, 0.05), (2.60, 1.30, 0.10), hearth_mat)
add_box("Hearth_Nosing", (0.0, -0.90, 0.04), (2.60, 0.06, 0.12), hearth_mat)

# --- surround: piers, lintel, firebox ---------------------------------
add_box("Pier_Left", (-0.92, 0.20, 0.68), (0.44, 0.50, 1.36), stone_mat)
add_box("Pier_Right", (0.92, 0.20, 0.68), (0.44, 0.50, 1.36), stone_mat)
add_box("Lintel", (0.0, 0.20, 1.44), (2.28, 0.50, 0.20), stone_mat)

add_box("Firebox_Back", (0.0, 0.42, 0.72), (1.40, 0.08, 1.34), firebrick_mat)
add_box("Firebox_SideLeft", (-0.68, 0.20, 0.72), (0.06, 0.46, 1.34), firebrick_mat)
add_box("Firebox_SideRight", (0.68, 0.20, 0.72), (0.06, 0.46, 1.34), firebrick_mat)
add_box("Firebox_Floor", (0.0, 0.20, 0.12), (1.36, 0.46, 0.06), firebrick_mat)
add_box("Firebox_Throat", (0.0, 0.20, 1.34), (1.36, 0.46, 0.06), firebrick_mat)

# --- mantel shelf and corbels -----------------------------------------
add_box("Mantel_Shelf", (0.0, 0.02, 1.62), (2.70, 0.42, 0.12), mantel_mat)
add_box("Mantel_Frieze", (0.0, 0.14, 1.50), (2.40, 0.16, 0.14), mantel_mat)
for side, cx in (("Left", -1.08), ("Right", 1.08)):
    add_box("Corbel_" + side, (cx, 0.10, 1.44), (0.16, 0.26, 0.24), mantel_mat)

# --- chimney breast above the mantel ----------------------------------
add_box("ChimneyBreast", (0.0, 0.32, 2.35), (1.90, 0.30, 1.35), stone_mat)
for i, cz in enumerate((1.82, 2.10, 2.38, 2.66, 2.94)):
    build_stone_course("Breast_C%d" % i, 0.15, cz, -0.92, 0.92, 0.28, 0.06, stone_mat)

# --- grate and andirons ------------------------------------------------
for side, ax in (("Left", -0.48), ("Right", 0.48)):
    add_box("Andiron_" + side, (ax, 0.20, 0.24), (0.06, 0.40, 0.06), iron_mat)
    add_box("Andiron_%s_Post" % side, (ax, 0.02, 0.30), (0.06, 0.06, 0.30), iron_mat)
for i in range(5):
    add_cylinder("Grate_Bar_%d" % i, (0.0, 0.05 + i * 0.09, 0.28), 0.018, 1.00, iron_mat,
                 rotation=(0.0, math.radians(90.0), 0.0), verts=8)

# --- stacked logs on the grate ----------------------------------------
log_rows = [
    (0.33, [(-0.34, 10.0), (0.02, 20.0), (0.36, 12.0)]),
    (0.46, [(-0.18, 16.0), (0.20, 6.0)]),
    (0.58, [(0.02, 14.0)]),
]
for r, (z, entries) in enumerate(log_rows):
    for c, (y_off, tilt_deg) in enumerate(entries):
        radius = random.uniform(0.055, 0.075)
        length = random.uniform(0.80, 0.95)
        mat = split_mat if (r + c) % 2 == 0 else bark_mat
        add_log("Log_R%dC%d" % (r, c), (0.0, 0.20 + y_off, z + radius),
                radius, length, mat, tilt=math.radians(tilt_deg))

# kindling, ember bed and a flame cone
for i in range(4):
    add_cylinder("Kindling_%d" % i,
                 (random.uniform(-0.35, 0.35), 0.20 + random.uniform(-0.12, 0.12), 0.22),
                 0.016, random.uniform(0.35, 0.55), split_mat,
                 rotation=(0.0, math.radians(90.0), random.uniform(-0.8, 0.8)), verts=6)
add_box("EmberBed", (0.0, 0.20, 0.17), (0.90, 0.34, 0.04), ember_mat)
bpy.ops.mesh.primitive_cone_add(vertices=16, radius1=0.22, radius2=0.02, depth=0.55,
                                location=(0.0, 0.20, 0.62))
flame = bpy.context.active_object
flame.name = "FlameCone"
flame.data.materials.append(flame_mat)

# --- mantel decor ------------------------------------------------------
for i, cx in enumerate((-1.00, -0.80, 0.95)):
    h = 0.20 + 0.06 * (i % 2)
    add_cylinder("Candle_Base_%d" % i, (cx, 0.02, 1.70), 0.05, 0.03, iron_mat, verts=16)
    add_cylinder("Candle_%d" % i, (cx, 0.02, 1.72 + h * 0.5), 0.028, h, candle_mat, verts=14)
add_box("Mantel_PictureFrame", (0.35, 0.28, 2.05), (0.60, 0.04, 0.46), mantel_mat)
add_box("Mantel_PictureCanvas", (0.35, 0.25, 2.05), (0.50, 0.02, 0.36), plaster_mat)

# --- spare firewood beside the hearth ---------------------------------
for i in range(6):
    row, col = divmod(i, 3)
    add_log("Woodpile_%d" % i, (1.72, -0.55 + col * 0.17, 0.10 + row * 0.15),
            0.07, 0.62, bark_mat if i % 2 else split_mat, tilt=math.radians(6.0 * i))

# --- lighting and camera ----------------------------------------------
fire_data = bpy.data.lights.new("FireLight", type='POINT')
fire_data.energy = 260.0
fire_data.color = (1.0, 0.52, 0.20)
fire_data.shadow_soft_size = 0.25
fire = bpy.data.objects.new("FireLight", fire_data)
bpy.context.collection.objects.link(fire)
fire.location = (0.0, 0.18, 0.45)

room_data = bpy.data.lights.new("RoomFill", type='AREA')
room_data.energy = 120.0
room_data.size = 3.0
room = bpy.data.objects.new("RoomFill", room_data)
bpy.context.collection.objects.link(room)
room.location = (-2.0, -3.0, 2.6)
room.rotation_euler = (math.radians(55.0), 0.0, math.radians(-30.0))

add_camera((2.2, -3.9, 1.75), (0.0, 0.15, 1.20), lens=42.0)
world = bpy.data.worlds.new("FireplaceWorld")
world.use_nodes = True
world.node_tree.nodes["Background"].inputs["Color"].default_value = (0.03, 0.03, 0.04, 1.0)
bpy.context.scene.world = world
