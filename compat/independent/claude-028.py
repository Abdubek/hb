import bpy
import math
from mathutils import Vector


def clear_scene():
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete(use_global=False)
    for block in (bpy.data.meshes, bpy.data.curves, bpy.data.materials):
        for item in list(block):
            if item.users == 0:
                block.remove(item)


def material(name, color, roughness=0.45, metallic=0.0, emission=None, strength=0.0):
    mat = bpy.data.materials.new(name)
    mat.use_nodes = True
    bsdf = mat.node_tree.nodes["Principled BSDF"]
    bsdf.inputs["Base Color"].default_value = (*color, 1.0)
    bsdf.inputs["Roughness"].default_value = roughness
    bsdf.inputs["Metallic"].default_value = metallic
    if emission is not None:
        bsdf.inputs["Emission Color"].default_value = (*emission, 1.0)
        bsdf.inputs["Emission Strength"].default_value = strength
    return mat


def finish(obj, name, mat):
    obj.name = name
    obj.data.name = name
    obj.data.materials.append(mat)
    return obj


def cylinder(name, radius, depth, location, mat, verts=32, rotation=(0, 0, 0)):
    bpy.ops.mesh.primitive_cylinder_add(vertices=verts, radius=radius, depth=depth,
                                        location=location, rotation=rotation)
    return finish(bpy.context.object, name, mat)


def sphere(name, radius, location, mat, segments=24):
    bpy.ops.mesh.primitive_uv_sphere_add(radius=radius, segments=segments,
                                         ring_count=segments // 2, location=location)
    obj = bpy.context.object
    bpy.ops.object.shade_smooth()
    return finish(obj, name, mat)


def aim_between(obj, a, b):
    """Point the object's local +Z from a towards b and centre it on the span."""
    d = Vector(b) - Vector(a)
    obj.location = (Vector(a) + Vector(b)) / 2.0
    obj.rotation_euler = d.to_track_quat('Z', 'Y').to_euler()
    return d.length


def tube_between(name, a, b, radius, mat, verts=24):
    length = (Vector(b) - Vector(a)).length
    bpy.ops.mesh.primitive_cylinder_add(vertices=verts, radius=radius, depth=length)
    obj = bpy.context.object
    aim_between(obj, a, b)
    return finish(obj, name, mat)


def cone_between(name, a, b, r_top, r_bottom, mat, verts=48):
    length = (Vector(b) - Vector(a)).length
    bpy.ops.mesh.primitive_cone_add(vertices=verts, radius1=r_top, radius2=r_bottom, depth=length)
    obj = bpy.context.object
    aim_between(obj, a, b)
    bpy.ops.object.shade_smooth()
    return finish(obj, name, mat)


def power_cord(points, mat):
    curve = bpy.data.curves.new("LampCordCurve", 'CURVE')
    curve.dimensions = '3D'
    curve.bevel_depth = 0.009
    curve.resolution_u = 4
    spline = curve.splines.new('BEZIER')
    spline.bezier_points.add(len(points) - 1)
    for bp, co in zip(spline.bezier_points, points):
        bp.co = co
        bp.handle_left_type = bp.handle_right_type = 'AUTO'
    obj = bpy.data.objects.new("LampCord", curve)
    bpy.context.collection.objects.link(obj)
    obj.data.materials.append(mat)
    return obj


def add_camera(location, target, lens=50.0):
    bpy.ops.object.camera_add(location=location)
    cam = bpy.context.object
    cam.name = "SceneCamera"
    cam.data.lens = lens
    cam.rotation_euler = (Vector(target) - Vector(location)).to_track_quat('-Z', 'Y').to_euler()
    bpy.context.scene.camera = cam
    return cam


clear_scene()

mat_metal = material("LampSteel", (0.32, 0.33, 0.35), roughness=0.28, metallic=1.0)
mat_dark = material("LampGraphite", (0.05, 0.05, 0.06), roughness=0.42)
mat_shade = material("ShadeEnamel", (0.82, 0.28, 0.18), roughness=0.35)
mat_bulb = material("BulbGlow", (1.0, 0.95, 0.82), roughness=0.1,
                    emission=(1.0, 0.9, 0.7), strength=12.0)
mat_floor = material("FloorOak", (0.30, 0.21, 0.13), roughness=0.65)

# base stack
cylinder("LampBaseDisc", 0.30, 0.035, (0.0, 0.0, 0.018), mat_dark, verts=48)
cylinder("LampBaseCollar", 0.12, 0.06, (0.0, 0.0, 0.065), mat_metal, verts=32)

# column and the first pivot
POLE_TOP = Vector((0.0, 0.0, 1.34))
cylinder("LampColumn", 0.024, 1.25, (0.0, 0.0, 0.095 + 1.25 / 2), mat_metal)
sphere("ShoulderJoint", 0.048, POLE_TOP, mat_dark)

# adjustable two-segment arm
ELBOW = Vector((0.52, 0.0, 1.72))
WRIST = Vector((0.95, 0.0, 1.50))
tube_between("ArmSegmentLower", POLE_TOP, ELBOW, 0.019, mat_metal)
sphere("ElbowJoint", 0.044, ELBOW, mat_dark)
tube_between("ArmSegmentUpper", ELBOW, WRIST, 0.017, mat_metal)
sphere("WristJoint", 0.038, WRIST, mat_dark)

# tension knobs on the joints
cylinder("ElbowKnob", 0.030, 0.11, ELBOW, mat_dark, rotation=(math.pi / 2, 0, 0))
cylinder("ShoulderKnob", 0.032, 0.12, POLE_TOP, mat_dark, rotation=(math.pi / 2, 0, 0))

# shade hanging off the wrist
SHADE_TOP = WRIST + Vector((0.05, 0.0, -0.10))
SHADE_BOT = WRIST + Vector((0.14, 0.0, -0.40))
tube_between("ShadeStem", WRIST, SHADE_TOP, 0.013, mat_metal)
cone_between("LampShade", SHADE_TOP, SHADE_BOT, 0.085, 0.20, mat_shade)
sphere("LightBulb", 0.058, (SHADE_TOP + SHADE_BOT) / 2, mat_bulb)

# foot switch and cord
cylinder("FootSwitch", 0.045, 0.022, (0.34, -0.30, 0.011), mat_dark, verts=20)
power_cord([(0.0, 0.0, 0.06), (0.20, -0.22, 0.02), (0.34, -0.30, 0.012),
            (0.75, -0.62, 0.010), (1.35, -0.80, 0.010)], mat_dark)

bpy.ops.mesh.primitive_plane_add(size=8.0, location=(0.0, 0.0, 0.0))
finish(bpy.context.object, "Floor", mat_floor)

bpy.ops.object.light_add(type='AREA', location=(-2.2, -2.4, 3.0))
key = bpy.context.object
key.name = "KeyLight"
key.data.energy = 300.0
key.data.size = 2.5
key.rotation_euler = (Vector((0.4, 0, 1.2)) - key.location).to_track_quat('-Z', 'Y').to_euler()

add_camera((2.9, -3.4, 2.15), (0.35, 0.0, 1.15))
