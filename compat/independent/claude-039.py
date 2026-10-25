import bpy
import bmesh
import math
from mathutils import Vector


def reset_scene():
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete(use_global=False)
    for coll in (bpy.data.meshes, bpy.data.materials, bpy.data.cameras, bpy.data.lights):
        for item in list(coll):
            if item.users == 0:
                coll.remove(item)


def make_material(name, color, metallic=0.0, roughness=0.5):
    mat = bpy.data.materials.new(name)
    mat.use_nodes = True
    bsdf = mat.node_tree.nodes["Principled BSDF"]
    bsdf.inputs["Base Color"].default_value = (color[0], color[1], color[2], 1.0)
    bsdf.inputs["Metallic"].default_value = metallic
    bsdf.inputs["Roughness"].default_value = roughness
    return mat


def finish(name, bm, mat, location, rotation=(0, 0, 0), smooth=False):
    mesh = bpy.data.meshes.new(name)
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    bm.to_mesh(mesh)
    bm.free()
    obj = bpy.data.objects.new(name, mesh)
    bpy.context.collection.objects.link(obj)
    obj.location = location
    obj.rotation_euler = rotation
    mesh.materials.append(mat)
    if smooth:
        mesh.shade_smooth()
    return obj


def add_box(name, size, location, mat, bevel=0.0):
    bm = bmesh.new()
    bmesh.ops.create_cube(bm, size=1.0)
    bmesh.ops.scale(bm, vec=Vector(size), verts=bm.verts)
    obj = finish(name, bm, mat, location)
    if bevel > 0.0:
        mod = obj.modifiers.new("Bevel", 'BEVEL')
        mod.width = bevel
        mod.segments = 2
        mod.limit_method = 'ANGLE'
    return obj


def add_cylinder(name, radius, depth, location, mat, rotation=(0, 0, 0), segments=32):
    bm = bmesh.new()
    bmesh.ops.create_cone(bm, cap_ends=True, cap_tris=False, segments=segments,
                          radius1=radius, radius2=radius, depth=depth)
    return finish(name, bm, mat, location, rotation, smooth=True)


def aim_at(obj, target):
    obj.rotation_euler = (Vector(target) - obj.location).to_track_quat('-Z', 'Y').to_euler()


reset_scene()

red = make_material("Red_Enamel", (0.52, 0.045, 0.035), metallic=0.6, roughness=0.32)
carcass = make_material("Dark_Carcass", (0.055, 0.058, 0.062), metallic=0.5, roughness=0.45)
chrome = make_material("Chrome", (0.78, 0.79, 0.80), metallic=1.0, roughness=0.18)
rubber = make_material("Black_Rubber", (0.03, 0.03, 0.032), metallic=0.0, roughness=0.75)
floor_mat = make_material("Shop_Floor", (0.20, 0.20, 0.21), metallic=0.0, roughness=0.65)

W, D = 0.62, 0.36          # cabinet width (x) and depth (y)
BODY_H = 0.60
Z0 = 0.135                 # cabinet underside, sitting on the casters
Z_TOP = Z0 + BODY_H
FRONT_Y = -(D * 0.5) - 0.008

# --- carcass and worktop ---
add_box("Cabinet_Carcass", (W, D, BODY_H), (0.0, 0.0, Z0 + BODY_H * 0.5), carcass, bevel=0.006)
add_box("Worktop_Panel", (W + 0.04, D + 0.04, 0.025), (0.0, 0.0, Z_TOP + 0.0125), red, bevel=0.005)
add_box("Worktop_Liner", (W, D, 0.006), (0.0, 0.0, Z_TOP + 0.028), rubber)
add_box("Kick_Rail", (W - 0.06, 0.02, 0.05), (0.0, FRONT_Y + 0.004, Z0 - 0.005), carcass)


def add_drawer(index, height, center_z):
    """Drawer face plus its chromed pull and two standoffs."""
    tag = "Drawer_%d" % index
    add_box(tag + "_Face", (W - 0.04, 0.016, height), (0.0, FRONT_Y - 0.008, center_z), red, bevel=0.004)
    add_cylinder(tag + "_Pull", 0.009, 0.30, (0.0, FRONT_Y - 0.046, center_z), chrome,
                 rotation=(0.0, math.radians(90.0), 0.0), segments=20)
    for sx in (-0.14, 0.14):
        add_cylinder(tag + "_Standoff", 0.008, 0.032, (sx, FRONT_Y - 0.030, center_z), chrome,
                     rotation=(math.radians(90.0), 0.0, 0.0), segments=16)


heights = [0.14, 0.14, 0.11, 0.11]
cursor = 0.16
for i, h in enumerate(heights, start=1):
    add_drawer(i, h, cursor + h * 0.5)
    cursor += h + 0.012

# --- push handle on the right-hand side ---
for sy in (-0.13, 0.13):
    add_box("Handle_Bracket", (0.03, 0.05, 0.07), (W * 0.5 + 0.008, sy, Z_TOP - 0.045), carcass, bevel=0.003)
    add_cylinder("Handle_Post", 0.012, 0.175, (W * 0.5 + 0.028, sy, Z_TOP + 0.075), chrome, segments=20)
add_cylinder("Handle_Grip", 0.015, 0.30, (W * 0.5 + 0.028, 0.0, Z_TOP + 0.162), chrome,
             rotation=(math.radians(90.0), 0.0, 0.0), segments=24)


def add_caster(sx, sy):
    add_box("Caster_Plate", (0.075, 0.065, 0.035), (sx, sy, Z0 - 0.0175), carcass, bevel=0.003)
    add_cylinder("Caster_Swivel", 0.014, 0.03, (sx, sy, Z0 - 0.035), chrome, segments=16)
    add_cylinder("Caster_Wheel", 0.05, 0.030, (sx, sy, 0.05), rubber,
                 rotation=(math.radians(90.0), 0.0, 0.0), segments=32)
    add_cylinder("Caster_Hub", 0.018, 0.034, (sx, sy, 0.05), chrome,
                 rotation=(math.radians(90.0), 0.0, 0.0), segments=20)


for sx in (-0.24, 0.24):
    for sy in (-0.13, 0.13):
        add_caster(sx, sy)

# --- ground ---
bm = bmesh.new()
bmesh.ops.create_grid(bm, x_segments=1, y_segments=1, size=1.6)
finish("Shop_Floor", bm, floor_mat, (0.0, 0.0, 0.0))

# --- lighting and world ---
key_data = bpy.data.lights.new("Key_Light", 'AREA')
key_data.energy = 600.0
key_data.size = 2.0
key = bpy.data.objects.new("Key_Light", key_data)
bpy.context.collection.objects.link(key)
key.location = (1.3, -1.5, 2.2)
aim_at(key, (0.0, 0.0, 0.42))

fill_data = bpy.data.lights.new("Fill_Light", 'AREA')
fill_data.energy = 180.0
fill_data.size = 2.5
fill = bpy.data.objects.new("Fill_Light", fill_data)
bpy.context.collection.objects.link(fill)
fill.location = (-1.6, -1.0, 1.2)
aim_at(fill, (0.0, 0.0, 0.40))

world = bpy.context.scene.world or bpy.data.worlds.new("Studio")
bpy.context.scene.world = world
world.use_nodes = True
world.node_tree.nodes["Background"].inputs["Color"].default_value = (0.045, 0.05, 0.055, 1.0)

# --- camera ---
cam_data = bpy.data.cameras.new("Camera")
cam_data.lens = 50.0
cam = bpy.data.objects.new("Camera", cam_data)
bpy.context.collection.objects.link(cam)
cam.location = (1.25, -1.55, 1.15)
aim_at(cam, (0.0, 0.0, 0.42))
bpy.context.scene.camera = cam
