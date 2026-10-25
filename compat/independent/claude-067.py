import bpy
import math
from mathutils import Vector, Matrix


def clear_scene():
    if bpy.context.object and bpy.context.object.mode != 'OBJECT':
        bpy.ops.object.mode_set(mode='OBJECT')
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete(use_global=False)


def new_material(name, color, roughness=0.5, metallic=0.0):
    mat = bpy.data.materials.new(name)
    mat.use_nodes = True
    bsdf = mat.node_tree.nodes["Principled BSDF"]
    bsdf.inputs["Base Color"].default_value = (color[0], color[1], color[2], 1.0)
    bsdf.inputs["Roughness"].default_value = roughness
    bsdf.inputs["Metallic"].default_value = metallic
    return mat


def add_box(name, dims, loc, mat=None, rot=(0.0, 0.0, 0.0)):
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=loc, rotation=rot)
    ob = bpy.context.object
    ob.name = name
    ob.scale = dims
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    if mat:
        ob.data.materials.append(mat)
    return ob


def add_cylinder(name, radius, depth, loc, mat=None, rot=(0.0, 0.0, 0.0), verts=24):
    bpy.ops.mesh.primitive_cylinder_add(radius=radius, depth=depth, vertices=verts,
                                        location=loc, rotation=rot)
    ob = bpy.context.object
    ob.name = name
    if mat:
        ob.data.materials.append(mat)
    return ob


def bevel(ob, width, segments=3):
    mod = ob.modifiers.new("Bevel", 'BEVEL')
    mod.width = width
    mod.segments = segments
    mod.limit_method = 'ANGLE'
    mod.angle_limit = math.radians(40.0)
    return mod


def yaw_offset(rot_z, offset):
    """Rotate a local offset into world space around Z."""
    return Matrix.Rotation(rot_z, 3, 'Z') @ Vector(offset)


def add_caster(tag, x, y, wheel_mat, metal_mat):
    add_cylinder("Caster_Wheel_" + tag, 0.085, 0.055, (x, y, 0.085), wheel_mat,
                 rot=(math.pi / 2.0, 0.0, 0.0), verts=20)
    add_cylinder("Caster_Hub_" + tag, 0.028, 0.062, (x, y, 0.085), metal_mat,
                 rot=(math.pi / 2.0, 0.0, 0.0), verts=12)
    fork = add_box("Caster_Fork_" + tag, (0.10, 0.10, 0.11), (x, y, 0.175), metal_mat)
    bevel(fork, 0.012, 2)
    add_cylinder("Caster_Stem_" + tag, 0.026, 0.10, (x, y, 0.27), metal_mat, verts=14)


def add_suitcase(name, dims, z, rot_z, shell_mat, trim_mat, handle_mat):
    body = add_box(name + "_Shell", dims, (0.0, 0.0, z), shell_mat, rot=(0.0, 0.0, rot_z))
    bevel(body, min(dims) * 0.16, 3)
    add_box(name + "_Stripe", (dims[0] * 1.004, dims[1] * 1.004, dims[2] * 0.16),
            (0.0, 0.0, z + dims[2] * 0.12), trim_mat, rot=(0.0, 0.0, rot_z))
    add_box(name + "_Seam", (dims[0] * 1.01, dims[1] * 1.01, 0.012),
            (0.0, 0.0, z - dims[2] * 0.18), trim_mat, rot=(0.0, 0.0, rot_z))
    top = z + dims[2] * 0.5
    bar_len = dims[0] * 0.30
    add_box(name + "_HandleBar", (bar_len, 0.038, 0.032), (0.0, 0.0, top + 0.062),
            handle_mat, rot=(0.0, 0.0, rot_z))
    for sign, tag in ((-1.0, "L"), (1.0, "R")):
        post = yaw_offset(rot_z, (sign * bar_len * 0.5, 0.0, 0.0))
        add_box(name + "_HandlePost_" + tag, (0.032, 0.038, 0.07),
                (post.x, post.y, top + 0.028), handle_mat, rot=(0.0, 0.0, rot_z))
    for sign, tag in ((-1.0, "L"), (1.0, "R")):
        foot = yaw_offset(rot_z, (sign * dims[0] * 0.36, 0.0, 0.0))
        add_box(name + "_Corner_" + tag, (0.07, dims[1] * 0.9, 0.03),
                (foot.x, foot.y, z - dims[2] * 0.5 + 0.012), handle_mat, rot=(0.0, 0.0, rot_z))
    return body


clear_scene()

floor_mat = new_material("Terminal_Floor", (0.52, 0.51, 0.49), roughness=0.35)
chrome = new_material("Cart_Chrome", (0.74, 0.75, 0.77), roughness=0.22, metallic=1.0)
dark_metal = new_material("Cart_DarkMetal", (0.11, 0.12, 0.13), roughness=0.45, metallic=0.7)
rubber = new_material("Rubber_Black", (0.045, 0.045, 0.05), roughness=0.85)
grip_red = new_material("Grip_Red", (0.42, 0.06, 0.06), roughness=0.7)
case_navy = new_material("Case_Navy", (0.06, 0.10, 0.24), roughness=0.42)
case_olive = new_material("Case_Olive", (0.20, 0.24, 0.13), roughness=0.55)
case_red = new_material("Case_Red", (0.44, 0.09, 0.10), roughness=0.40)
trim_tan = new_material("Trim_Tan", (0.46, 0.36, 0.22), roughness=0.6)
trim_grey = new_material("Trim_Grey", (0.30, 0.31, 0.32), roughness=0.5)

add_box("Terminal_Floor", (9.0, 9.0, 0.12), (0.0, 0.0, -0.06), floor_mat)

# --- cart deck and rails ----------------------------------------------------
DECK_TOP = 0.375
deck = add_box("Cart_Deck", (1.50, 0.86, 0.07), (0.0, 0.0, DECK_TOP - 0.035), dark_metal)
bevel(deck, 0.014, 2)
add_box("Deck_Mat", (1.44, 0.80, 0.012), (0.0, 0.0, DECK_TOP + 0.006), rubber)
for sign, tag in ((-1.0, "L"), (1.0, "R")):
    add_cylinder("Deck_Rail_" + tag, 0.020, 1.50, (0.0, sign * 0.43, DECK_TOP + 0.03),
                 chrome, rot=(0.0, math.pi / 2.0, 0.0), verts=14)
add_cylinder("Deck_Rail_Front", 0.020, 0.86, (0.75, 0.0, DECK_TOP + 0.03), chrome,
             rot=(math.pi / 2.0, 0.0, 0.0), verts=14)

for x, y, tag in ((-0.60, -0.32, "RL"), (-0.60, 0.32, "RR"),
                  (0.60, -0.32, "FL"), (0.60, 0.32, "FR")):
    add_caster(tag, x, y, rubber, dark_metal)

# --- rear frame, handlebar, front guard -------------------------------------
for sign, tag in ((-1.0, "L"), (1.0, "R")):
    add_cylinder("Frame_Post_" + tag, 0.030, 0.69, (-0.72, sign * 0.34, DECK_TOP + 0.345),
                 chrome, rot=(0.0, 0.0, 0.0), verts=16)
add_cylinder("Frame_CrossBrace", 0.022, 0.68, (-0.72, 0.0, 0.72), chrome,
             rot=(math.pi / 2.0, 0.0, 0.0), verts=14)
add_cylinder("Handle_Bar", 0.032, 0.80, (-0.72, 0.0, 1.065), chrome,
             rot=(math.pi / 2.0, 0.0, 0.0), verts=20)
for sign, tag in ((-1.0, "L"), (1.0, "R")):
    add_cylinder("Handle_Grip_" + tag, 0.043, 0.15, (-0.72, sign * 0.30, 1.065), grip_red,
                 rot=(math.pi / 2.0, 0.0, 0.0), verts=18)
add_box("Handle_Info_Plate", (0.012, 0.34, 0.14), (-0.735, 0.0, 0.90), trim_grey)
for sign, tag in ((-1.0, "L"), (1.0, "R")):
    add_cylinder("Front_Guard_Post_" + tag, 0.022, 0.24, (0.71, sign * 0.34, DECK_TOP + 0.12),
                 chrome, verts=12)
add_cylinder("Front_Guard_Bar", 0.020, 0.68, (0.71, 0.0, DECK_TOP + 0.235), chrome,
             rot=(math.pi / 2.0, 0.0, 0.0), verts=14)

# --- stacked luggage --------------------------------------------------------
add_suitcase("Suitcase_Large", (1.00, 0.62, 0.30), DECK_TOP + 0.162,
             math.radians(3.0), case_navy, trim_tan, dark_metal)
add_suitcase("Suitcase_Medium", (0.82, 0.52, 0.26), DECK_TOP + 0.312 + 0.13,
             math.radians(-7.0), case_olive, trim_grey, dark_metal)
add_suitcase("Suitcase_Small", (0.54, 0.38, 0.22), DECK_TOP + 0.572 + 0.11,
             math.radians(11.0), case_red, trim_tan, dark_metal)
add_box("Garment_Bag", (0.60, 0.16, 0.34), (0.36, -0.30, DECK_TOP + 0.18),
        trim_grey, rot=(0.0, 0.0, math.radians(-14.0)))

# --- lighting, world, camera ------------------------------------------------
key_data = bpy.data.lights.new("Key", type='AREA')
key_data.energy = 420.0
key_data.size = 3.2
key = bpy.data.objects.new("Key_Light", key_data)
bpy.context.collection.objects.link(key)
key.location = (2.4, -2.6, 3.6)
key.rotation_euler = (Vector((0.0, 0.0, 0.0)) - Vector(key.location)).to_track_quat('-Z', 'Y').to_euler()

rim_data = bpy.data.lights.new("Rim", type='AREA')
rim_data.energy = 160.0
rim_data.size = 2.4
rim = bpy.data.objects.new("Rim_Light", rim_data)
bpy.context.collection.objects.link(rim)
rim.location = (-2.8, 2.2, 2.4)
rim.rotation_euler = (Vector((0.0, 0.0, 0.7)) - Vector(rim.location)).to_track_quat('-Z', 'Y').to_euler()

world = bpy.data.worlds.new("CartWorld")
world.use_nodes = True
world.node_tree.nodes["Background"].inputs["Color"].default_value = (0.30, 0.32, 0.36, 1.0)
world.node_tree.nodes["Background"].inputs["Strength"].default_value = 0.6
bpy.context.scene.world = world

cam_data = bpy.data.cameras.new("CartCam")
cam_data.lens = 55.0
cam = bpy.data.objects.new("Camera", cam_data)
bpy.context.collection.objects.link(cam)
cam.location = (2.55, -2.75, 1.85)
cam.rotation_euler = (Vector((-0.05, 0.0, 0.72)) - Vector(cam.location)).to_track_quat('-Z', 'Y').to_euler()
bpy.context.scene.camera = cam
