"""Dining set: rectangular table with an apron plus four matching side chairs."""
import bpy
import math
from mathutils import Vector

TABLE_TOP_Z = 0.74
SEAT_Z = 0.44
CHAIR_SPOTS = ((-0.45, 0.70, 0.0), (0.45, 0.70, 0.0),
               (-0.45, -0.70, math.pi), (0.45, -0.70, math.pi))


def reset_scene():
    for ob in list(bpy.data.objects):
        bpy.data.objects.remove(ob, do_unlink=True)
    for me in list(bpy.data.meshes):
        bpy.data.meshes.remove(me)


def new_material(name, color, roughness=0.5, metallic=0.0):
    mat = bpy.data.materials.new(name)
    mat.use_nodes = True
    bsdf = mat.node_tree.nodes["Principled BSDF"]
    bsdf.inputs["Base Color"].default_value = (color[0], color[1], color[2], 1.0)
    bsdf.inputs["Roughness"].default_value = roughness
    bsdf.inputs["Metallic"].default_value = metallic
    return mat


def part(name, dims, location, mat, rotation=(0.0, 0.0, 0.0), parent=None):
    """Unit cube scaled to dims, scale baked down so sizes stay readable."""
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=location, rotation=rotation)
    ob = bpy.context.active_object
    ob.name = name
    ob.scale = dims
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    ob.data.materials.append(mat)
    if parent is not None:
        ob.parent = parent
    return ob


def build_table(name, oak, walnut):
    root = bpy.data.objects.new(name, None)
    root.empty_display_size = 0.2
    bpy.context.collection.objects.link(root)
    part(name + "_Top", (1.60, 0.95, 0.05), (0.0, 0.0, TABLE_TOP_Z - 0.025), oak, parent=root)
    for sy in (-1.0, 1.0):
        tag = "Front" if sy < 0 else "Back"
        part("%s_Apron_%s" % (name, tag), (1.46, 0.06, 0.10),
             (0.0, sy * 0.40, TABLE_TOP_Z - 0.11), walnut, parent=root)
    for sx in (-1.0, 1.0):
        tag = "Left" if sx < 0 else "Right"
        part("%s_Apron_%s" % (name, tag), (0.06, 0.81, 0.10),
             (sx * 0.72, 0.0, TABLE_TOP_Z - 0.11), walnut, parent=root)
    for sx, sy, tag in ((-1, -1, "FL"), (1, -1, "FR"), (-1, 1, "RL"), (1, 1, "RR")):
        part("%s_Leg_%s" % (name, tag), (0.08, 0.08, TABLE_TOP_Z - 0.05),
             (sx * 0.70, sy * 0.40, (TABLE_TOP_Z - 0.05) * 0.5), walnut, parent=root)
    return root


def build_chair(name, location, rot_z, walnut, fabric, oak):
    """Chair is assembled around the origin, then placed by its empty."""
    root = bpy.data.objects.new(name, None)
    root.empty_display_size = 0.12
    bpy.context.collection.objects.link(root)
    leg_h = SEAT_Z - 0.02
    for sx, sy, tag in ((-1, -1, "FL"), (1, -1, "FR"), (-1, 1, "RL"), (1, 1, "RR")):
        part("%s_Leg_%s" % (name, tag), (0.045, 0.045, leg_h),
             (sx * 0.19, sy * 0.19, leg_h * 0.5), walnut, parent=root)
    for sy in (-1.0, 1.0):
        part("%s_Rail_Y%d" % (name, int(sy)), (0.38, 0.04, 0.05),
             (0.0, sy * 0.185, 0.30), walnut, parent=root)
    for sx in (-1.0, 1.0):
        part("%s_Rail_X%d" % (name, int(sx)), (0.04, 0.38, 0.05),
             (sx * 0.185, 0.0, 0.30), walnut, parent=root)
    part(name + "_Seat", (0.44, 0.44, 0.05), (0.0, 0.0, SEAT_Z), fabric, parent=root)
    for sx in (-1.0, 1.0):
        part("%s_BackPost_%d" % (name, int(sx)), (0.045, 0.045, 0.50),
             (sx * 0.19, 0.19, SEAT_Z + 0.25), walnut, parent=root)
    for i in range(2):
        part("%s_BackSlat_%02d" % (name, i + 1), (0.38, 0.03, 0.10),
             (0.0, 0.19, 0.60 + i * 0.16), oak, parent=root)
    part(name + "_TopRail", (0.44, 0.05, 0.055), (0.0, 0.19, 0.915), walnut, parent=root)
    root.location = (location[0], location[1], 0.0)
    root.rotation_euler = (0.0, 0.0, rot_z)
    return root


def aim_camera(location, target, lens=45.0):
    cam = bpy.data.objects.new("Camera", bpy.data.cameras.new("Camera"))
    cam.data.lens = lens
    cam.location = location
    cam.rotation_euler = (Vector(target) - Vector(location)).to_track_quat('-Z', 'Y').to_euler()
    bpy.context.collection.objects.link(cam)
    bpy.context.scene.camera = cam
    return cam


reset_scene()
OAK = new_material("Oak_Light", (0.62, 0.44, 0.24), 0.45)
WALNUT = new_material("Walnut_Dark", (0.24, 0.13, 0.07), 0.4)
FABRIC = new_material("Seat_Fabric", (0.30, 0.35, 0.42), 0.85)
FLOOR = new_material("Floor_Boards", (0.45, 0.36, 0.28), 0.6)

part("Floor", (7.0, 7.0, 0.06), (0.0, 0.0, -0.03), FLOOR)
build_table("Table", OAK, WALNUT)
for i, (x, y, rz) in enumerate(CHAIR_SPOTS):
    build_chair("Chair_%02d" % (i + 1), (x, y), rz, WALNUT, FABRIC, OAK)

key = bpy.data.objects.new("KeyLight", bpy.data.lights.new("KeyLight", type='AREA'))
key.data.energy = 400.0
key.data.size = 2.5
key.location = (1.5, -1.5, 3.2)
key.rotation_euler = (math.radians(25.0), 0.0, math.radians(30.0))
bpy.context.collection.objects.link(key)

aim_camera((2.8, -3.2, 2.2), (0.0, 0.0, 0.55))
