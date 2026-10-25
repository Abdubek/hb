import bpy
import math
from mathutils import Vector

TILT = math.radians(38.0)   # optical tube elevation
HUB_Z = 0.95                # tripod hub height


def purge_scene():
    for obj in list(bpy.data.objects):
        bpy.data.objects.remove(obj, do_unlink=True)
    for mesh in list(bpy.data.meshes):
        bpy.data.meshes.remove(mesh)


def material(name, color, metallic=0.0, roughness=0.45):
    mat = bpy.data.materials.new(name)
    mat.use_nodes = True
    bsdf = mat.node_tree.nodes["Principled BSDF"]
    bsdf.inputs["Base Color"].default_value = (color[0], color[1], color[2], 1.0)
    bsdf.inputs["Metallic"].default_value = metallic
    bsdf.inputs["Roughness"].default_value = roughness
    return mat


def finish(obj, name, mat, parent):
    obj.name = name
    obj.data.name = name
    obj.data.materials.append(mat)
    obj.parent = parent
    return obj


def cylinder(name, radius, depth, location, mat, parent, rotation=(0, 0, 0), verts=24):
    bpy.ops.mesh.primitive_cylinder_add(vertices=verts, radius=radius, depth=depth,
                                        location=location, rotation=rotation)
    return finish(bpy.context.active_object, name, mat, parent)


def ring(name, major, minor, location, mat, parent, rotation=(0, 0, 0)):
    bpy.ops.mesh.primitive_torus_add(major_radius=major, minor_radius=minor,
                                     major_segments=24, minor_segments=8,
                                     location=location, rotation=rotation)
    return finish(bpy.context.active_object, name, mat, parent)


def box(name, size, location, mat, parent, rotation=(0, 0, 0)):
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=location, rotation=rotation)
    obj = bpy.context.active_object
    obj.scale = size
    return finish(obj, name, mat, parent)


def strut(name, p1, p2, radius, mat, parent, verts=12):
    a, b = Vector(p1), Vector(p2)
    d = b - a
    rot = d.to_track_quat('Z', 'Y').to_euler()
    return cylinder(name, radius, d.length, a + d * 0.5, mat, parent, rot, verts)


def knob(name, center, axis_len, radius, mat, grip_mat, parent):
    """Knurled adjustment knob on the +Y axis."""
    rot = (math.pi / 2, 0, 0)
    cylinder(name, radius, axis_len, center, mat, parent, rot, 20)
    ring(name + "_Grip", radius * 0.98, axis_len * 0.28, center, grip_mat, parent, rot)


purge_scene()

white = material("TubeWhite", (0.88, 0.88, 0.86), 0.05, 0.35)
black = material("MattBlack", (0.04, 0.04, 0.05), 0.1, 0.6)
chrome = material("Chrome", (0.72, 0.73, 0.75), 1.0, 0.22)
brass = material("BrassKnob", (0.68, 0.52, 0.18), 1.0, 0.3)
wood = material("TripodWood", (0.42, 0.27, 0.14), 0.0, 0.55)
glass = material("ObjectiveGlass", (0.55, 0.72, 0.85), 0.2, 0.05)

root = bpy.data.objects.new("Telescope", None)
bpy.context.collection.objects.link(root)

# ---- tripod ------------------------------------------------------------
for i in range(3):
    a = math.radians(90 + i * 120)
    top = (0.07 * math.cos(a), 0.07 * math.sin(a), HUB_Z)
    foot = (0.50 * math.cos(a), 0.50 * math.sin(a), 0.022)
    strut("Leg_%d" % i, top, foot, 0.022, wood, root)
    cylinder("Foot_%d" % i, 0.036, 0.022, (foot[0], foot[1], 0.011), black, root)
    mid = (0.324 * math.cos(a), 0.324 * math.sin(a), 0.40)
    strut("TrayBrace_%d" % i, (0.19 * math.cos(a), 0.19 * math.sin(a), 0.40), mid,
          0.010, chrome, root)

cylinder("AccessoryTray", 0.20, 0.016, (0, 0, 0.40), black, root, verts=32)
cylinder("TripodHub", 0.085, 0.062, (0, 0, HUB_Z), black, root, verts=32)
cylinder("CenterColumn", 0.045, 0.14, (0, 0, HUB_Z + 0.07), chrome, root, verts=24)

# ---- alt-azimuth mount head -------------------------------------------
box("MountHead", (0.16, 0.13, 0.085), (0, 0, 1.125), black, root)
P = Vector((0.0, 0.0, 1.165))               # altitude pivot
u = Vector((math.sin(TILT), 0.0, math.cos(TILT)))   # tube axis
p = Vector((math.cos(TILT), 0.0, -math.sin(TILT)))  # tube "down" direction

box("Saddle", (0.13, 0.12, 0.045), P - p * 0.03, chrome, root, (0, TILT, 0))
knob("AltitudeKnob", P + Vector((0, 0.105, 0)), 0.032, 0.040, brass, black, root)
knob("AzimuthKnob", Vector((0, 0.095, HUB_Z + 0.015)), 0.030, 0.036, brass, black, root)

# slow-motion flexible control hanging off the altitude axis
rod_end = P + Vector((0.09, 0.10, -0.34))
strut("SlowMotionRod", P + Vector((0.02, 0.10, -0.02)), rod_end, 0.008, chrome, root)
cylinder("SlowMotionKnob", 0.028, 0.05, rod_end, brass, root,
         (rod_end - P).to_track_quat('Z', 'Y').to_euler(), 16)

# ---- optical tube assembly --------------------------------------------
center = P - p * 0.105
tube_rot = (0, TILT, 0)
cylinder("OpticalTube", 0.075, 0.85, center, white, root, tube_rot, 32)
cylinder("DewShield", 0.086, 0.10, center + u * 0.44, white, root, tube_rot, 32)
cylinder("Objective", 0.070, 0.008, center + u * 0.398, glass, root, tube_rot, 32)
for s in (-1, 1):
    ring("TubeRing_%s" % ("Rear" if s < 0 else "Front"), 0.079, 0.010,
         center + u * (0.07 * s), black, root, tube_rot)

focuser = center - u * 0.465
cylinder("FocuserBody", 0.046, 0.10, focuser, black, root, tube_rot, 24)
cylinder("DrawTube", 0.028, 0.08, center - u * 0.545, chrome, root, tube_rot, 20)
cylinder("Eyepiece", 0.031, 0.07, center - u * 0.615, black, root, tube_rot, 20)
cylinder("EyeCup", 0.037, 0.014, center - u * 0.652, black, root, tube_rot, 20)
for s in (-1, 1):
    tag = "L" if s < 0 else "R"
    knob("FocusKnob_" + tag, focuser + Vector((0, 0.058 * s, 0)), 0.020, 0.029,
         brass, black, root)

finder_c = center - u * 0.10 - p * 0.095 + Vector((0, 0.085, 0))
cylinder("FinderScope", 0.023, 0.24, finder_c, black, root, tube_rot, 16)
for s in (-1, 1):
    strut("FinderBracket_%d" % (s + 1), finder_c + u * (0.09 * s),
          center + u * (0.09 * s) - p * 0.055 + Vector((0, 0.045, 0)),
          0.008, chrome, root)

# ---- lighting and camera ----------------------------------------------
sun_data = bpy.data.lights.new("KeyLight", 'SUN')
sun_data.energy = 3.5
sun = bpy.data.objects.new("KeyLight", sun_data)
sun.location = (2.5, -2.0, 4.0)
sun.rotation_euler = (math.radians(52), math.radians(12), math.radians(38))
bpy.context.collection.objects.link(sun)

fill_data = bpy.data.lights.new("FillLight", 'AREA')
fill_data.energy = 120.0
fill_data.size = 2.5
fill = bpy.data.objects.new("FillLight", fill_data)
fill.location = (-2.2, -1.6, 1.8)
fill.rotation_euler = (math.radians(70), 0, math.radians(-55))
bpy.context.collection.objects.link(fill)

cam_data = bpy.data.cameras.new("Camera")
cam_data.lens = 50
cam = bpy.data.objects.new("Camera", cam_data)
cam.location = (1.95, -2.35, 1.75)
target = Vector((0.0, 0.0, 1.10))
cam.rotation_euler = (target - cam.location).to_track_quat('-Z', 'Y').to_euler()
bpy.context.collection.objects.link(cam)
bpy.context.scene.camera = cam
