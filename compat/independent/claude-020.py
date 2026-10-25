import bpy
from mathutils import Vector


def clear_scene():
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete(use_global=False)


def make_material(name, color, metallic=0.0, roughness=0.5):
    mat = bpy.data.materials.new(name)
    mat.use_nodes = True
    bsdf = mat.node_tree.nodes["Principled BSDF"]
    bsdf.inputs["Base Color"].default_value = (color[0], color[1], color[2], 1.0)
    bsdf.inputs["Metallic"].default_value = metallic
    bsdf.inputs["Roughness"].default_value = roughness
    return mat


def add_box(name, size, location, mat, rotation=(0.0, 0.0, 0.0)):
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=location, rotation=rotation)
    obj = bpy.context.object
    obj.name = name
    obj.scale = size
    obj.data.materials.append(mat)
    return obj


def add_ball(name, radius, location, mat):
    bpy.ops.mesh.primitive_uv_sphere_add(radius=radius, segments=20, ring_count=12, location=location)
    obj = bpy.context.object
    obj.name = name
    obj.data.materials.append(mat)
    bpy.ops.object.shade_smooth()
    return obj


def add_strut(name, p0, p1, radius, mat, verts=14):
    """Cylinder spanning two points - used for limb segments."""
    a, b = Vector(p0), Vector(p1)
    d = b - a
    bpy.ops.mesh.primitive_cylinder_add(vertices=verts, radius=radius, depth=d.length,
                                        location=(a + b) * 0.5)
    obj = bpy.context.object
    obj.name = name
    obj.rotation_euler = d.to_track_quat('Z', 'Y').to_euler()
    obj.data.materials.append(mat)
    return obj


def build_leg(tag, hip, forward, mats):
    """Jointed leg: hip pivot -> thigh -> knee pivot -> shin -> ankle -> foot."""
    hip = Vector(hip)
    knee = hip + Vector((0.17 * forward, 0.0, -0.30))
    ankle = knee + Vector((-0.07 * forward, 0.0, -0.30))
    add_ball("Hip_%s" % tag, 0.075, hip, mats['joint'])
    add_strut("Thigh_%s" % tag, hip, knee, 0.052, mats['shell'])
    add_ball("Knee_%s" % tag, 0.06, knee, mats['joint'])
    add_strut("Shin_%s" % tag, knee, ankle, 0.038, mats['dark'])
    add_ball("Ankle_%s" % tag, 0.045, ankle, mats['joint'])
    add_box("Foot_%s" % tag, (0.20, 0.11, 0.07), (ankle.x + 0.02 * forward, ankle.y, 0.035),
            mats['rubber'])


clear_scene()

mats = {
    'shell': make_material("RobotShell", (0.82, 0.83, 0.86), metallic=0.75, roughness=0.32),
    'dark': make_material("RobotDark", (0.13, 0.14, 0.16), metallic=0.6, roughness=0.45),
    'joint': make_material("JointMetal", (0.45, 0.47, 0.52), metallic=0.95, roughness=0.22),
    'rubber': make_material("FootRubber", (0.06, 0.06, 0.07), metallic=0.0, roughness=0.85),
    'accent': make_material("AccentOrange", (0.90, 0.35, 0.05), metallic=0.1, roughness=0.4),
    'lens': make_material("SensorLens", (0.05, 0.35, 0.65), metallic=0.2, roughness=0.1),
    'ground': make_material("Ground", (0.28, 0.29, 0.30), metallic=0.0, roughness=0.9),
}

bpy.ops.mesh.primitive_plane_add(size=8.0, location=(0.0, 0.0, 0.0))
bpy.context.object.name = "GroundPlane"
bpy.context.object.data.materials.append(mats['ground'])

# torso
add_box("TorsoChassis", (1.16, 0.48, 0.32), (0.0, 0.0, 0.80), mats['shell'])
add_box("TorsoSpine", (0.90, 0.30, 0.10), (0.0, 0.0, 0.99), mats['dark'])
add_box("BatteryPack", (0.44, 0.40, 0.16), (-0.18, 0.0, 0.62), mats['dark'])
add_box("ShoulderYokeF", (0.14, 0.62, 0.22), (0.42, 0.0, 0.72), mats['dark'])
add_box("ShoulderYokeR", (0.14, 0.62, 0.22), (-0.42, 0.0, 0.72), mats['dark'])
add_box("StatusStripe", (0.34, 0.02, 0.06), (0.10, 0.245, 0.86), mats['accent'])

# neck and head
add_strut("Neck", (0.55, 0.0, 0.90), (0.76, 0.0, 1.06), 0.055, mats['joint'])
add_box("Head", (0.30, 0.26, 0.22), (0.86, 0.0, 1.10), mats['shell'])
add_box("Muzzle", (0.12, 0.18, 0.12), (1.02, 0.0, 1.06), mats['dark'])
add_ball("SensorEye_L", 0.045, (0.99, 0.08, 1.16), mats['lens'])
add_ball("SensorEye_R", 0.045, (0.99, -0.08, 1.16), mats['lens'])
add_strut("Antenna", (0.78, 0.0, 1.21), (0.70, 0.0, 1.46), 0.012, mats['dark'])
add_ball("AntennaTip", 0.03, (0.70, 0.0, 1.47), mats['accent'])
add_box("LidarDeck", (0.16, 0.20, 0.05), (0.84, 0.0, 1.23), mats['dark'])

# four jointed legs
for px, forward, side_tag in ((0.42, 1.0, "Front"), (-0.42, -1.0, "Rear")):
    for py, lr in ((0.27, "L"), (-0.27, "R")):
        build_leg("%s%s" % (side_tag, lr), (px, py, 0.72), forward, mats)

# tail
add_strut("TailBase", (-0.58, 0.0, 0.86), (-0.80, 0.0, 1.00), 0.035, mats['dark'])
add_strut("TailTip", (-0.80, 0.0, 1.00), (-0.95, 0.0, 1.16), 0.022, mats['accent'])

# lighting
bpy.ops.object.light_add(type='SUN', location=(3.0, -3.0, 6.0))
key = bpy.context.object
key.name = "KeyLight"
key.data.energy = 4.0
key.rotation_euler = Vector((-3.0, 3.0, -6.0)).to_track_quat('-Z', 'Y').to_euler()

bpy.ops.object.light_add(type='AREA', location=(-3.0, 2.5, 3.0))
fill = bpy.context.object
fill.name = "FillLight"
fill.data.energy = 200.0
fill.data.size = 3.0
fill.rotation_euler = Vector((3.0, -2.5, -2.2)).to_track_quat('-Z', 'Y').to_euler()

# camera
cam_loc = Vector((3.1, -3.4, 1.9))
target = Vector((0.05, 0.0, 0.78))
cam_data = bpy.data.cameras.new("DogCam")
cam_data.lens = 50.0
cam = bpy.data.objects.new("Camera", cam_data)
bpy.context.collection.objects.link(cam)
cam.location = cam_loc
cam.rotation_euler = (target - cam_loc).to_track_quat('-Z', 'Y').to_euler()
bpy.context.scene.camera = cam
