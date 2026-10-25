import bpy
import bmesh
import math
from mathutils import Vector


def clear_scene():
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete(use_global=False)
    for coll in (bpy.data.meshes, bpy.data.materials, bpy.data.cameras, bpy.data.lights):
        for item in list(coll):
            if item.users == 0:
                coll.remove(item)


def make_material(name, color, roughness=0.5, metallic=0.0):
    mat = bpy.data.materials.new(name)
    mat.use_nodes = True
    bsdf = mat.node_tree.nodes["Principled BSDF"]
    bsdf.inputs["Base Color"].default_value = (color[0], color[1], color[2], 1.0)
    bsdf.inputs["Roughness"].default_value = roughness
    bsdf.inputs["Metallic"].default_value = metallic
    return mat


def add_box(name, dims, loc, mat, rot=(0.0, 0.0, 0.0), bevel=0.0):
    mesh = bpy.data.meshes.new(name)
    bm = bmesh.new()
    bmesh.ops.create_cube(bm, size=1.0)
    bmesh.ops.scale(bm, vec=Vector(dims), verts=bm.verts)
    if bevel > 0.0:
        bmesh.ops.bevel(bm, geom=list(bm.verts) + list(bm.edges) + list(bm.faces),
                        offset=bevel, segments=2, affect='EDGES')
    bm.to_mesh(mesh)
    bm.free()
    obj = bpy.data.objects.new(name, mesh)
    obj.location = loc
    obj.rotation_euler = rot
    mesh.materials.append(mat)
    bpy.context.collection.objects.link(obj)
    return obj


def add_cylinder(name, radius, depth, loc, mat, rot=(0.0, 0.0, 0.0), verts=24):
    bpy.ops.mesh.primitive_cylinder_add(radius=radius, depth=depth, vertices=verts,
                                        location=loc, rotation=rot)
    obj = bpy.context.active_object
    obj.name = name
    obj.data.materials.append(mat)
    return obj


def add_wheel(name, radius, width, loc, tire_mat, rim_mat):
    axle_rot = (math.pi / 2.0, 0.0, 0.0)
    tire = add_cylinder(name + "_Tire", radius, width, loc, tire_mat, axle_rot, verts=28)
    rim = add_cylinder(name + "_Rim", radius * 0.5, width * 1.06, loc, rim_mat, axle_rot, verts=20)
    hub = add_cylinder(name + "_Hub", radius * 0.16, width * 1.3, loc, rim_mat, axle_rot, verts=12)
    return [tire, rim, hub]


def aim_camera(location, target, lens=45.0):
    cam_data = bpy.data.cameras.new("TractorCam")
    cam_data.lens = lens
    cam = bpy.data.objects.new("TractorCam", cam_data)
    bpy.context.collection.objects.link(cam)
    cam.location = location
    direction = Vector(target) - Vector(location)
    cam.rotation_euler = direction.to_track_quat('-Z', 'Y').to_euler()
    bpy.context.scene.camera = cam
    return cam


clear_scene()

paint = make_material("Tractor_Paint", (0.05, 0.32, 0.09), roughness=0.35)
metal = make_material("Tractor_Metal", (0.55, 0.56, 0.58), roughness=0.35, metallic=0.9)
rubber = make_material("Tire_Rubber", (0.035, 0.035, 0.04), roughness=0.85)
rim_mat = make_material("Wheel_Rim", (0.72, 0.62, 0.10), roughness=0.4, metallic=0.3)
seat_mat = make_material("Seat_Vinyl", (0.12, 0.11, 0.13), roughness=0.6)
glass = make_material("Lamp_Glass", (0.95, 0.92, 0.70), roughness=0.15)
ground_mat = make_material("Ground_Dirt", (0.30, 0.24, 0.17), roughness=0.95)

REAR_R, FRONT_R = 0.92, 0.46
REAR_X, FRONT_X = -1.05, 1.55
TRACK = 0.95

parts = []
parts.append(add_box("Chassis", (3.9, 0.85, 0.5), (0.15, 0.0, 0.95), paint, bevel=0.05))
parts.append(add_box("EngineHood", (1.9, 0.95, 0.72), (1.35, 0.0, 1.52), paint, bevel=0.08))
parts.append(add_box("HoodNose", (0.18, 0.88, 0.62), (2.38, 0.0, 1.47), metal, bevel=0.03))
parts.append(add_box("Grille", (0.08, 0.72, 0.42), (2.48, 0.0, 1.42), metal))
parts.append(add_box("FuelTank", (0.9, 0.72, 0.42), (0.05, 0.0, 1.42), metal, bevel=0.05))
parts.append(add_box("Footplate", (1.0, 1.5, 0.09), (-0.65, 0.0, 1.24), metal))
parts.append(add_box("SeatPedestal", (0.4, 0.4, 0.34), (-1.05, 0.0, 1.44), metal))
parts.append(add_box("SeatCushion", (0.62, 0.66, 0.14), (-1.05, 0.0, 1.68), seat_mat, bevel=0.04))
parts.append(add_box("SeatBack", (0.16, 0.62, 0.55), (-1.40, 0.0, 1.98), seat_mat,
                     rot=(0.0, math.radians(-12.0), 0.0), bevel=0.04))
parts.append(add_cylinder("SteeringColumn", 0.06, 0.8, (-0.25, 0.0, 1.85), metal,
                          rot=(0.0, math.radians(28.0), 0.0), verts=12))

bpy.ops.mesh.primitive_torus_add(major_radius=0.26, minor_radius=0.035, location=(-0.42, 0.0, 2.18),
                                 rotation=(0.0, math.radians(28.0), 0.0),
                                 major_segments=20, minor_segments=8)
wheel = bpy.context.active_object
wheel.name = "SteeringWheel"
wheel.data.materials.append(seat_mat)
parts.append(wheel)

parts.append(add_cylinder("ExhaustStack", 0.075, 1.1, (2.05, 0.30, 2.32), metal, verts=14))
parts.append(add_cylinder("ExhaustTip", 0.11, 0.14, (2.05, 0.30, 2.92), metal, verts=14))
parts.append(add_cylinder("FrontAxle", 0.09, 2.0, (FRONT_X, 0.0, FRONT_R), metal,
                          rot=(math.pi / 2.0, 0.0, 0.0), verts=12))
parts.append(add_cylinder("RearAxle", 0.12, 2.1, (REAR_X, 0.0, REAR_R), metal,
                          rot=(math.pi / 2.0, 0.0, 0.0), verts=12))

for side, tag in ((1.0, "L"), (-1.0, "R")):
    parts += add_wheel("RearWheel_" + tag, REAR_R, 0.46,
                       (REAR_X, side * TRACK, REAR_R), rubber, rim_mat)
    parts += add_wheel("FrontWheel_" + tag, FRONT_R, 0.26,
                       (FRONT_X, side * 0.82, FRONT_R), rubber, rim_mat)
    parts.append(add_box("RearFender_" + tag, (1.7, 0.5, 0.1),
                         (REAR_X, side * TRACK, REAR_R + 0.95), paint, bevel=0.03))
    parts.append(add_box("FenderSkirt_" + tag, (0.12, 0.48, 0.55),
                         (REAR_X - 0.79, side * TRACK, REAR_R + 0.66), paint))
    parts.append(add_cylinder("Headlight_" + tag, 0.11, 0.1,
                              (2.5, side * 0.28, 1.55), glass,
                              rot=(0.0, math.pi / 2.0, 0.0), verts=14))
    parts.append(add_cylinder("RollBarPost_" + tag, 0.055, 1.5,
                              (-1.55, side * 0.52, 2.15), metal, verts=10))

parts.append(add_box("RollBarTop", (0.11, 1.2, 0.11), (-1.55, 0.0, 2.88), metal))

root = bpy.data.objects.new("Tractor", None)
bpy.context.collection.objects.link(root)
for obj in parts:
    obj.parent = root

bpy.ops.mesh.primitive_plane_add(size=24.0, location=(0.0, 0.0, 0.0))
ground = bpy.context.active_object
ground.name = "Ground"
ground.data.materials.append(ground_mat)

bpy.ops.object.light_add(type='SUN', location=(6.0, -7.0, 10.0))
sun = bpy.context.active_object
sun.name = "SunLight"
sun.data.energy = 4.0
sun.rotation_euler = (math.radians(52.0), math.radians(12.0), math.radians(35.0))

bpy.ops.object.light_add(type='AREA', location=(-5.0, 5.0, 5.0))
fill = bpy.context.active_object
fill.name = "FillLight"
fill.data.energy = 320.0
fill.data.size = 6.0
fill.rotation_euler = (math.radians(60.0), 0.0, math.radians(-135.0))

aim_camera((7.2, -6.4, 4.1), (0.1, 0.0, 1.3))
