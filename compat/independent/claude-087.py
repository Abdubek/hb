import bpy
import bmesh
import math
from mathutils import Vector

TUBE_R = 0.016
HALF_W = 0.245
SEAT_Z = 0.430


def clear_scene():
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete(use_global=False)
    for coll in (bpy.data.meshes, bpy.data.materials):
        for item in list(coll):
            if item.users == 0:
                coll.remove(item)


def make_material(name, color, roughness=0.5, metallic=0.0):
    mat = bpy.data.materials.new(name)
    mat.use_nodes = True
    bsdf = mat.node_tree.nodes.get("Principled BSDF")
    bsdf.inputs["Base Color"].default_value = (color[0], color[1], color[2], 1.0)
    bsdf.inputs["Roughness"].default_value = roughness
    bsdf.inputs["Metallic"].default_value = metallic
    return mat


def finish(obj, name, mat, parent=None):
    obj.name = name
    obj.data.name = name
    obj.data.materials.append(mat)
    if parent is not None:
        obj.parent = parent
    return obj


def tube(name, p1, p2, mat, parent, radius=TUBE_R, verts=16):
    a, b = Vector(p1), Vector(p2)
    vec = b - a
    bpy.ops.mesh.primitive_cylinder_add(vertices=verts, radius=radius, depth=vec.length,
                                        location=(a + b) * 0.5)
    obj = bpy.context.active_object
    obj.rotation_euler = vec.to_track_quat('Z', 'Y').to_euler()
    return finish(obj, name, mat, parent)


def mirrored_tube(base_name, p1, p2, mat, parent, radius=TUBE_R):
    for sign, tag in ((-1.0, "L"), (1.0, "R")):
        tube("%s_%s" % (base_name, tag),
             (sign * p1[0], p1[1], p1[2]),
             (sign * p2[0], p2[1], p2[2]), mat, parent, radius=radius)


def joint(name, location, mat, parent, radius=TUBE_R * 1.25):
    bpy.ops.mesh.primitive_uv_sphere_add(segments=16, ring_count=8, radius=radius,
                                         location=location)
    return finish(bpy.context.active_object, name, mat, parent)


def fabric_panel(name, centre, half_size, rotation, sag, mat, parent, segs=10):
    """Sagging quad panel: local XY grid pushed down in local -Z toward the middle."""
    mesh = bpy.data.meshes.new(name)
    bm = bmesh.new()
    bmesh.ops.create_grid(bm, x_segments=segs, y_segments=segs, size=1.0)
    for v in bm.verts:
        u, w = v.co.x, v.co.y
        v.co.x *= half_size[0]
        v.co.y *= half_size[1]
        v.co.z -= sag * (1.0 - u * u) * (1.0 - w * w)
    bm.to_mesh(mesh)
    bm.free()
    obj = bpy.data.objects.new(name, mesh)
    bpy.context.collection.objects.link(obj)
    obj.location = centre
    obj.rotation_euler = rotation
    solid = obj.modifiers.new("Thickness", 'SOLIDIFY')
    solid.thickness = 0.006
    solid.offset = 0.0
    return finish(obj, name, mat, parent)


clear_scene()

frame_mat = make_material("MAT_FrameAlu", (0.55, 0.57, 0.60), roughness=0.30, metallic=1.0)
hub_mat = make_material("MAT_HubPlastic", (0.10, 0.10, 0.11), roughness=0.55)
fabric_mat = make_material("MAT_CanvasGreen", (0.09, 0.24, 0.16), roughness=0.85)
strap_mat = make_material("MAT_WebbingTan", (0.42, 0.33, 0.19), roughness=0.80)
ground_mat = make_material("MAT_Ground", (0.36, 0.33, 0.28), roughness=0.95)

bpy.ops.object.empty_add(type='PLAIN_AXES', location=(0.0, 0.0, 0.0))
root = bpy.context.active_object
root.name = "CampingChair"

front_foot = (HALF_W, -0.230, 0.020)
front_top = (HALF_W, 0.115, SEAT_Z)
rear_foot = (HALF_W, 0.235, 0.020)
rear_top = (HALF_W, -0.130, SEAT_Z)
back_top = (HALF_W - 0.010, 0.215, 0.880)

# --- crossed side frames ---
mirrored_tube("Leg_Front", front_foot, front_top, frame_mat, root)
mirrored_tube("Leg_Rear", rear_foot, rear_top, frame_mat, root)
mirrored_tube("Backrest_Upright", front_top, back_top, frame_mat, root)

for sign, tag in ((-1.0, "L"), (1.0, "R")):
    joint("Pivot_%s" % tag, (sign * HALF_W, -0.012, 0.235), hub_mat, root)
    joint("Hinge_Seat_%s" % tag, (sign * HALF_W, front_top[1], SEAT_Z), hub_mat, root)

# --- cross members tying the two side frames together ---
tube("Rail_Seat_Front", (-HALF_W, rear_top[1], SEAT_Z), (HALF_W, rear_top[1], SEAT_Z),
     frame_mat, root, radius=TUBE_R * 0.85)
tube("Rail_Seat_Rear", (-HALF_W, front_top[1], SEAT_Z), (HALF_W, front_top[1], SEAT_Z),
     frame_mat, root, radius=TUBE_R * 0.85)
tube("Rail_Foot_Front", (-HALF_W, front_foot[1], front_foot[2]), (HALF_W, front_foot[1], front_foot[2]),
     frame_mat, root, radius=TUBE_R * 0.8)
tube("Rail_Foot_Rear", (-HALF_W, rear_foot[1], rear_foot[2]), (HALF_W, rear_foot[1], rear_foot[2]),
     frame_mat, root, radius=TUBE_R * 0.8)
tube("Rail_Backrest_Top", (-HALF_W + 0.010, back_top[1], back_top[2]),
     (HALF_W - 0.010, back_top[1], back_top[2]), frame_mat, root, radius=TUBE_R * 0.85)
tube("Rail_Backrest_Lower", (-HALF_W, 0.150, 0.590), (HALF_W, 0.150, 0.590),
     frame_mat, root, radius=TUBE_R * 0.7)

# --- armrests with vertical supports ---
for sign, tag in ((-1.0, "L"), (1.0, "R")):
    tube("Armrest_%s" % tag, (sign * HALF_W, -0.145, 0.660), (sign * (HALF_W - 0.004), 0.170, 0.700),
         frame_mat, root, radius=TUBE_R * 0.8)
    tube("Armrest_Post_%s" % tag, (sign * HALF_W, -0.140, SEAT_Z), (sign * HALF_W, -0.145, 0.660),
         frame_mat, root, radius=TUBE_R * 0.7)

# --- rubber feet ---
for sign in (-1.0, 1.0):
    for point, tag in ((front_foot, "Front"), (rear_foot, "Rear")):
        bpy.ops.mesh.primitive_cylinder_add(vertices=16, radius=TUBE_R * 1.5, depth=0.040,
                                            location=(sign * point[0], point[1], 0.020))
        finish(bpy.context.active_object,
               "Foot_%s_%s" % (tag, "L" if sign < 0 else "R"), hub_mat, root)

# --- fabric seat and backrest ---
fabric_panel("Seat_Canvas", (0.0, -0.008, SEAT_Z - 0.004), (HALF_W - 0.010, 0.128),
             (0.0, 0.0, 0.0), 0.055, fabric_mat, root)
fabric_panel("Backrest_Canvas", (0.0, 0.196, 0.735), (HALF_W - 0.020, 0.150),
             (math.radians(-79.0), 0.0, 0.0), 0.045, fabric_mat, root)

# --- webbing straps under the seat edges ---
for y, tag in ((front_top[1], "Rear"), (rear_top[1], "Front")):
    bpy.ops.mesh.primitive_cube_add(size=2.0, location=(0.0, y, SEAT_Z - 0.012))
    strap = bpy.context.active_object
    strap.scale = (HALF_W - 0.015, 0.022, 0.004)
    finish(strap, "Seat_Webbing_%s" % tag, strap_mat, root)

# --- ground, lights, camera ---
bpy.ops.mesh.primitive_plane_add(size=6.0, location=(0.0, 0.0, 0.0))
finish(bpy.context.active_object, "Ground", ground_mat)

bpy.ops.object.light_add(type='SUN', location=(2.0, -2.0, 3.5))
sun = bpy.context.active_object
sun.name = "Light_Sun"
sun.data.energy = 4.0
sun.rotation_euler = (math.radians(50.0), math.radians(12.0), math.radians(35.0))

bpy.ops.object.light_add(type='AREA', location=(-1.6, -1.2, 1.6))
fill = bpy.context.active_object
fill.name = "Light_Fill"
fill.data.energy = 120.0
fill.data.size = 2.0
fill.rotation_euler = (math.radians(70.0), 0.0, math.radians(-55.0))

target = Vector((0.0, 0.0, 0.480))
bpy.ops.object.camera_add(location=(1.50, -1.85, 1.25))
cam = bpy.context.active_object
cam.name = "Camera_ThreeQuarter"
cam.data.lens = 50.0
cam.rotation_euler = (target - cam.location).to_track_quat('-Z', 'Y').to_euler()
bpy.context.scene.camera = cam
