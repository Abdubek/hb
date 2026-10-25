"""Desktop monitor speaker: ported cabinet with a woofer and a dome tweeter."""
import bpy
import math
from mathutils import Vector

CAB = (0.200, 0.240, 0.340)
FOOT_H = 0.012
CAB_Z = FOOT_H + CAB[2] * 0.5
FRONT_Y = -CAB[1] * 0.5
WOOFER_Z = 0.150
TWEETER_Z = 0.290
FACE = (math.radians(90.0), 0.0, 0.0)


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


def _tidy(name, mat, parent=None, bevel=0.0, segments=2):
    ob = bpy.context.active_object
    ob.name = name
    ob.data.materials.append(mat)
    if parent is not None:
        ob.parent = parent
    if bevel:
        mod = ob.modifiers.new("Bevel", 'BEVEL')
        mod.width = bevel
        mod.segments = segments
    return ob


def cube(name, dims, location, mat, parent=None, bevel=0.0, rotation=(0.0, 0.0, 0.0)):
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=location, rotation=rotation)
    bpy.context.active_object.scale = dims
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    return _tidy(name, mat, parent, bevel)


def cyl(name, radius, depth, location, mat, parent=None, rotation=(0.0, 0.0, 0.0), verts=48):
    bpy.ops.mesh.primitive_cylinder_add(vertices=verts, radius=radius, depth=depth,
                                        location=location, rotation=rotation)
    return _tidy(name, mat, parent)


def cone(name, r1, r2, depth, location, mat, parent=None, rotation=(0.0, 0.0, 0.0), verts=48):
    bpy.ops.mesh.primitive_cone_add(vertices=verts, radius1=r1, radius2=r2, depth=depth,
                                    location=location, rotation=rotation)
    return _tidy(name, mat, parent)


def ball(name, radius, location, mat, parent=None):
    bpy.ops.mesh.primitive_uv_sphere_add(radius=radius, segments=28, ring_count=14,
                                         location=location)
    return _tidy(name, mat, parent)


def aim_camera(location, target, lens=50.0):
    cam = bpy.data.objects.new("Camera", bpy.data.cameras.new("Camera"))
    cam.data.lens = lens
    cam.location = location
    cam.rotation_euler = (Vector(target) - Vector(location)).to_track_quat('-Z', 'Y').to_euler()
    bpy.context.collection.objects.link(cam)
    bpy.context.scene.camera = cam
    return cam


reset_scene()
WALNUT = new_material("Cabinet_Walnut", (0.20, 0.11, 0.06), 0.45)
BAFFLE = new_material("Baffle_Plastic", (0.05, 0.05, 0.055), 0.55)
CONE_PAPER = new_material("Cone_Paper", (0.30, 0.29, 0.27), 0.8)
SURROUND = new_material("Cone_Surround", (0.10, 0.10, 0.11), 0.6)
CHROME = new_material("Trim_Chrome", (0.72, 0.73, 0.75), 0.22, 0.95)
LED = new_material("Power_LED", (0.10, 0.65, 0.30), 0.25)
DESK = new_material("Desk_Top", (0.30, 0.29, 0.28), 0.7)

cube("Desk", (1.4, 1.2, 0.02), (0.0, 0.0, -0.01), DESK)

speaker = bpy.data.objects.new("Speaker", None)
speaker.empty_display_size = 0.08
bpy.context.collection.objects.link(speaker)

cube("Cabinet_Box", CAB, (0.0, 0.0, CAB_Z), WALNUT, speaker, bevel=0.006)
cube("Cabinet_Baffle", (CAB[0] - 0.012, 0.008, CAB[2] - 0.012), (0.0, FRONT_Y - 0.003, CAB_Z),
     BAFFLE, speaker, bevel=0.002)

for tag, sx in (("L", -1.0), ("R", 1.0)):
    for depth_tag, sy in (("F", -1.0), ("B", 1.0)):
        cyl("Foot_%s%s" % (tag, depth_tag), 0.012, FOOT_H,
            (sx * 0.075, sy * 0.090, FOOT_H * 0.5), SURROUND, speaker, verts=20)

# woofer assembly: mounting ring, surround roll, cone and dust cap
cyl("Woofer_Ring", 0.076, 0.010, (0.0, FRONT_Y - 0.012, WOOFER_Z), SURROUND, speaker, FACE)
cyl("Woofer_Surround", 0.066, 0.014, (0.0, FRONT_Y - 0.014, WOOFER_Z), SURROUND, speaker, FACE)
cone("Woofer_Cone", 0.018, 0.060, 0.036, (0.0, FRONT_Y + 0.012, WOOFER_Z), CONE_PAPER,
     speaker, FACE)
ball("Woofer_DustCap", 0.018, (0.0, FRONT_Y - 0.006, WOOFER_Z), CHROME, speaker)
for i in range(4):
    a = math.radians(45.0 + i * 90.0)
    cyl("Woofer_Screw_%02d" % (i + 1), 0.004, 0.006,
        (math.cos(a) * 0.070, FRONT_Y - 0.016, WOOFER_Z + math.sin(a) * 0.070),
        CHROME, speaker, FACE, verts=12)

# tweeter assembly with waveguide plate and metal dome
cyl("Tweeter_Plate", 0.036, 0.008, (0.0, FRONT_Y - 0.011, TWEETER_Z), SURROUND, speaker, FACE)
cone("Tweeter_Waveguide", 0.012, 0.030, 0.016, (0.0, FRONT_Y - 0.004, TWEETER_Z), SURROUND,
     speaker, FACE)
ball("Tweeter_Dome", 0.013, (0.0, FRONT_Y - 0.011, TWEETER_Z), CHROME, speaker)

cyl("Volume_Knob", 0.015, 0.014, (0.062, FRONT_Y - 0.010, 0.052), CHROME, speaker, FACE, verts=32)
cyl("Knob_Indicator", 0.0018, 0.016, (0.062, FRONT_Y - 0.011, 0.062), SURROUND, speaker, FACE,
    verts=10)
cyl("Status_LED", 0.0045, 0.005, (-0.062, FRONT_Y - 0.004, 0.052), LED, speaker, FACE, verts=16)

# rear panel: bass reflex port and speaker binding posts
cyl("Rear_Port", 0.021, 0.030, (0.0, -FRONT_Y - 0.010, 0.100), SURROUND, speaker, FACE, verts=32)
cube("Terminal_Plate", (0.080, 0.006, 0.040), (0.0, -FRONT_Y + 0.002, 0.048), BAFFLE, speaker,
     bevel=0.002)
for tag, sx in (("Pos", -1.0), ("Neg", 1.0)):
    cyl("Binding_Post_%s" % tag, 0.006, 0.020, (sx * 0.022, -FRONT_Y + 0.008, 0.048),
        CHROME, speaker, FACE, verts=16)

key = bpy.data.objects.new("KeyLight", bpy.data.lights.new("KeyLight", type='AREA'))
key.data.energy = 120.0
key.data.size = 1.0
key.location = (0.5, -0.6, 0.8)
key.rotation_euler = (math.radians(35.0), 0.0, math.radians(40.0))
bpy.context.collection.objects.link(key)

fill = bpy.data.objects.new("FillLight", bpy.data.lights.new("FillLight", type='AREA'))
fill.data.energy = 40.0
fill.data.size = 1.2
fill.location = (-0.7, -0.4, 0.4)
fill.rotation_euler = (math.radians(70.0), 0.0, math.radians(-60.0))
bpy.context.collection.objects.link(fill)

aim_camera((0.42, -0.62, 0.36), (0.0, 0.0, 0.18))
