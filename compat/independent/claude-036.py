import bpy
import math
from mathutils import Vector, Euler

# ---------------------------------------------------------------- utilities

def reset_scene():
    for obj in list(bpy.data.objects):
        bpy.data.objects.remove(obj, do_unlink=True)
    for coll in (bpy.data.meshes, bpy.data.materials, bpy.data.cameras, bpy.data.lights):
        for item in list(coll):
            if item.users == 0:
                coll.remove(item)


def make_material(name, color, roughness=0.5, metallic=0.0):
    mat = bpy.data.materials.new(name)
    mat.use_nodes = True
    bsdf = mat.node_tree.nodes["Principled BSDF"]
    bsdf.inputs["Base Color"].default_value = (*color, 1.0)
    bsdf.inputs["Roughness"].default_value = roughness
    bsdf.inputs["Metallic"].default_value = metallic
    return mat


def _finish(obj, name, material, bevel=0.0):
    obj.name = name
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    if material is not None:
        obj.data.materials.append(material)
    if bevel > 0.0:
        mod = obj.modifiers.new("Bevel", 'BEVEL')
        mod.width = bevel
        mod.segments = 3
        mod.limit_method = 'ANGLE'
    return obj


def box(name, dims, location, rotation=(0.0, 0.0, 0.0), material=None, bevel=0.0):
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=location)
    obj = bpy.context.object
    obj.rotation_euler = Euler(rotation)
    obj.scale = dims
    return _finish(obj, name, material, bevel)


def cylinder(name, radius, depth, location, rotation=(0.0, 0.0, 0.0), material=None, verts=24):
    bpy.ops.mesh.primitive_cylinder_add(radius=radius, depth=depth, vertices=verts,
                                        location=location, rotation=rotation)
    return _finish(bpy.context.object, name, material)


def link_arm(name, p0, p1, width, height, material, bevel=0.008):
    """A box segment spanning two pivot points (an arm link)."""
    p0, p1 = Vector(p0), Vector(p1)
    direction = p1 - p0
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(p0 + p1) * 0.5)
    obj = bpy.context.object
    obj.rotation_euler = direction.to_track_quat('Z', 'Y').to_euler()
    obj.scale = (width, height, direction.length)
    return _finish(obj, name, material, bevel)


def add_camera(location, target, lens=50.0):
    cam_data = bpy.data.cameras.new("MonitorCam")
    cam_data.lens = lens
    cam = bpy.data.objects.new("Camera", cam_data)
    bpy.context.collection.objects.link(cam)
    cam.location = location
    cam.rotation_euler = (Vector(location) - Vector(target)).to_track_quat('Z', 'Y').to_euler()
    bpy.context.scene.camera = cam
    return cam


# ---------------------------------------------------------------- materials

reset_scene()

MAT_DESK = make_material("Desk.Wood", (0.35, 0.22, 0.13), roughness=0.55)
MAT_ARM = make_material("Mount.Aluminium", (0.62, 0.63, 0.65), roughness=0.35, metallic=0.9)
MAT_JOINT = make_material("Mount.Joint", (0.08, 0.08, 0.09), roughness=0.45)
MAT_SHELL = make_material("Monitor.Shell", (0.12, 0.12, 0.13), roughness=0.5)
MAT_BEZEL = make_material("Monitor.Bezel", (0.04, 0.04, 0.05), roughness=0.4)
MAT_SCREEN = make_material("Monitor.Screen", (0.05, 0.09, 0.16), roughness=0.12)

# ---------------------------------------------------------------- desk + clamp

box("Desk.Top", (1.60, 0.80, 0.04), (0.0, 0.0, -0.02), material=MAT_DESK, bevel=0.006)

box("Clamp.UpperPad", (0.11, 0.11, 0.022), (0.0, 0.345, 0.011), material=MAT_JOINT, bevel=0.004)
box("Clamp.BackPlate", (0.11, 0.024, 0.19), (0.0, 0.412, -0.055), material=MAT_JOINT, bevel=0.004)
box("Clamp.LowerJaw", (0.11, 0.10, 0.022), (0.0, 0.350, -0.139), material=MAT_JOINT, bevel=0.004)
cylinder("Clamp.Screw", 0.011, 0.10, (0.0, 0.345, -0.090), material=MAT_ARM)
cylinder("Clamp.ScrewKnob", 0.026, 0.016, (0.0, 0.345, -0.148), material=MAT_JOINT, verts=16)

# ---------------------------------------------------------------- articulated arm

POST_TOP = Vector((0.0, 0.400, 0.450))
ELBOW = Vector((0.0, 0.160, 0.790))
WRIST = Vector((0.0, -0.060, 0.705))

cylinder("Mount.Post", 0.026, 0.45, (0.0, 0.400, 0.225), material=MAT_ARM, verts=20)
cylinder("Mount.PostCollar", 0.034, 0.030, (0.0, 0.400, 0.030), material=MAT_JOINT, verts=20)

link_arm("Mount.LowerArm", POST_TOP, ELBOW, 0.048, 0.036, MAT_ARM)
link_arm("Mount.UpperArm", ELBOW, WRIST, 0.042, 0.032, MAT_ARM)

X_AXIS = (0.0, math.radians(90.0), 0.0)
cylinder("Joint.Shoulder", 0.030, 0.058, POST_TOP, rotation=X_AXIS, material=MAT_JOINT, verts=20)
cylinder("Joint.Elbow", 0.028, 0.054, ELBOW, rotation=X_AXIS, material=MAT_JOINT, verts=20)
cylinder("Joint.Wrist", 0.024, 0.048, WRIST, rotation=X_AXIS, material=MAT_JOINT, verts=20)

# ---------------------------------------------------------------- monitor head

pivot = bpy.data.objects.new("Monitor.Pivot", None)
pivot.empty_display_size = 0.06
bpy.context.collection.objects.link(pivot)
pivot.location = WRIST

head_parts = [
    box("Mount.VesaPlate", (0.11, 0.016, 0.11), (0.0, -0.076, 0.705), material=MAT_JOINT, bevel=0.004),
    box("Monitor.Shell", (0.62, 0.036, 0.37), (0.0, -0.102, 0.705), material=MAT_SHELL, bevel=0.010),
    box("Monitor.Bezel", (0.62, 0.012, 0.37), (0.0, -0.126, 0.705), material=MAT_BEZEL, bevel=0.005),
    box("Monitor.Screen", (0.586, 0.004, 0.336), (0.0, -0.134, 0.709), material=MAT_SCREEN),
    box("Monitor.ChinBar", (0.62, 0.020, 0.030), (0.0, -0.124, 0.534), material=MAT_SHELL, bevel=0.004),
]

for part in head_parts:
    part.parent = pivot
    part.matrix_parent_inverse = pivot.matrix_world.inverted()

pivot.rotation_euler = Euler((math.radians(-7.0), 0.0, 0.0))

# ---------------------------------------------------------------- lighting + camera

key = bpy.data.lights.new("Key", 'AREA')
key.energy = 220.0
key.size = 1.2
key_obj = bpy.data.objects.new("Light.Key", key)
bpy.context.collection.objects.link(key_obj)
key_obj.location = (1.1, -1.2, 1.9)
key_obj.rotation_euler = (Vector(key_obj.location) - Vector((0.0, 0.0, 0.7))).to_track_quat('Z', 'Y').to_euler()

fill = bpy.data.lights.new("Fill", 'SUN')
fill.energy = 1.8
fill_obj = bpy.data.objects.new("Light.Fill", fill)
bpy.context.collection.objects.link(fill_obj)
fill_obj.rotation_euler = (math.radians(58.0), 0.0, math.radians(-125.0))

add_camera((0.95, -1.35, 1.10), (0.0, -0.06, 0.72), lens=52.0)
