"""Six-wheel planetary rover: chassis, rocker suspension, sensor mast and dish."""
import bpy
import bmesh
import math
from mathutils import Vector

WHEEL_R = 0.17
WHEEL_W = 0.14
WHEEL_X = (-0.40, 0.0, 0.40)
Y_AXIS = (math.radians(90.0), 0.0, 0.0)
X_AXIS = (0.0, math.radians(90.0), 0.0)


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


def _finish(name, bm, location, rotation, mat, parent, bevel):
    me = bpy.data.meshes.new(name)
    bm.to_mesh(me)
    bm.free()
    ob = bpy.data.objects.new(name, me)
    ob.location = location
    ob.rotation_euler = rotation
    ob.data.materials.append(mat)
    bpy.context.collection.objects.link(ob)
    if parent is not None:
        ob.parent = parent
    if bevel:
        mod = ob.modifiers.new("Bevel", 'BEVEL')
        mod.width = bevel
        mod.segments = 2
    return ob


def add_box(name, size, location, mat, rotation=(0.0, 0.0, 0.0), parent=None, bevel=0.008):
    bm = bmesh.new()
    bmesh.ops.create_cube(bm, size=1.0)
    bmesh.ops.scale(bm, vec=Vector(size), verts=bm.verts)
    return _finish(name, bm, location, rotation, mat, parent, bevel)


def add_tube(name, r1, r2, depth, location, mat, rotation=(0.0, 0.0, 0.0), segments=28, parent=None):
    """Cylinder when r1 == r2, truncated cone otherwise."""
    bm = bmesh.new()
    bmesh.ops.create_cone(bm, cap_ends=True, cap_tris=False, segments=segments,
                          radius1=r1, radius2=r2, depth=depth)
    return _finish(name, bm, location, rotation, mat, parent, 0.0)


def add_ball(name, radius, location, mat, parent=None):
    bm = bmesh.new()
    bmesh.ops.create_icosphere(bm, subdivisions=2, radius=radius)
    return _finish(name, bm, location, (0.0, 0.0, 0.0), mat, parent, 0.0)


def aim_camera(location, target, lens=45.0):
    cam = bpy.data.objects.new("Camera", bpy.data.cameras.new("Camera"))
    cam.data.lens = lens
    cam.location = location
    cam.rotation_euler = (Vector(target) - Vector(location)).to_track_quat('-Z', 'Y').to_euler()
    bpy.context.collection.objects.link(cam)
    bpy.context.scene.camera = cam
    return cam


reset_scene()
SHELL = new_material("Rover_Shell", (0.78, 0.78, 0.76), 0.35, 0.25)
ALLOY = new_material("Rover_Alloy", (0.55, 0.56, 0.58), 0.3, 0.9)
RUBBER = new_material("Wheel_Rubber", (0.06, 0.06, 0.07), 0.75)
PANEL = new_material("Solar_Panel", (0.05, 0.08, 0.22), 0.2, 0.6)
LENS = new_material("Camera_Lens", (0.02, 0.05, 0.07), 0.1, 0.4)
REGOLITH = new_material("Regolith", (0.42, 0.26, 0.18), 0.95)

add_box("Regolith_Ground", (10.0, 10.0, 0.1), (0.0, 0.0, -0.05), REGOLITH, bevel=0.0)

rover = bpy.data.objects.new("Rover", None)
rover.empty_display_size = 0.3
bpy.context.collection.objects.link(rover)

add_box("Chassis_Body", (1.10, 0.62, 0.26), (0.0, 0.0, 0.44), SHELL, parent=rover, bevel=0.03)
add_box("Chassis_Deck", (1.02, 0.56, 0.03), (0.0, 0.0, 0.585), PANEL, parent=rover, bevel=0.004)
add_box("Front_Bumper", (0.06, 0.50, 0.09), (0.57, 0.0, 0.40), ALLOY, parent=rover, bevel=0.01)
add_box("Rear_Electronics_Box", (0.18, 0.34, 0.12), (-0.58, 0.0, 0.44), SHELL, parent=rover, bevel=0.012)

for tag, sy in (("L", -1.0), ("R", 1.0)):
    add_box("Rocker_Beam_%s" % tag, (1.00, 0.05, 0.07), (0.0, sy * 0.33, 0.30), ALLOY,
            parent=rover, bevel=0.006)
    for i, x in enumerate(WHEEL_X):
        suffix = "%s%d" % (tag, i + 1)
        add_tube("Wheel_" + suffix, WHEEL_R, WHEEL_R, WHEEL_W, (x, sy * 0.42, WHEEL_R),
                 RUBBER, Y_AXIS, 20, rover)
        add_tube("Wheel_Hub_" + suffix, 0.07, 0.07, WHEEL_W + 0.015, (x, sy * 0.42, WHEEL_R),
                 ALLOY, Y_AXIS, 20, rover)
        add_tube("Axle_" + suffix, 0.028, 0.028, 0.10, (x, sy * 0.375, WHEEL_R),
                 ALLOY, Y_AXIS, 16, rover)
        add_box("Strut_" + suffix, (0.07, 0.05, 0.18), (x, sy * 0.33, 0.24), ALLOY,
                parent=rover, bevel=0.005)

# sensor mast rising from the rear deck
add_tube("Mast_Base", 0.055, 0.055, 0.06, (-0.36, 0.0, 0.62), ALLOY, parent=rover)
add_tube("Mast_Pole", 0.03, 0.03, 0.55, (-0.36, 0.0, 0.90), ALLOY, parent=rover)
add_box("Mast_Head", (0.20, 0.11, 0.13), (-0.34, 0.0, 1.22), SHELL, parent=rover, bevel=0.012)
for tag, sy in (("L", -1.0), ("R", 1.0)):
    add_tube("NavCam_%s" % tag, 0.032, 0.032, 0.05, (-0.225, sy * 0.055, 1.235),
             LENS, X_AXIS, 20, rover)
add_tube("Mast_Antenna", 0.008, 0.008, 0.30, (-0.42, 0.0, 1.42), ALLOY, parent=rover, segments=12)
add_ball("Antenna_Tip", 0.02, (-0.42, 0.0, 1.58), ALLOY, rover)

# high-gain dish on the forward deck
add_tube("Dish_Post", 0.028, 0.028, 0.12, (0.36, 0.0, 0.655), ALLOY, parent=rover)
add_tube("Dish_Reflector", 0.13, 0.03, 0.06, (0.36, 0.02, 0.75), SHELL,
         (math.radians(-30.0), 0.0, 0.0), 24, rover)

sun = bpy.data.objects.new("Sun", bpy.data.lights.new("Sun", type='SUN'))
sun.data.energy = 4.0
sun.location = (2.0, -3.0, 4.0)
sun.rotation_euler = (math.radians(55.0), 0.0, math.radians(40.0))
bpy.context.collection.objects.link(sun)

aim_camera((2.1, -2.5, 1.55), (0.0, 0.0, 0.6))
