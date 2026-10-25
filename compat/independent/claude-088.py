import bpy
import bmesh
import math
from mathutils import Vector


def clear_scene():
    for ob in list(bpy.data.objects):
        bpy.data.objects.remove(ob, do_unlink=True)


def make_material(name, color, roughness=0.5, metallic=0.0):
    mat = bpy.data.materials.new(name)
    mat.use_nodes = True
    bsdf = mat.node_tree.nodes["Principled BSDF"]
    bsdf.inputs["Base Color"].default_value = (color[0], color[1], color[2], 1.0)
    bsdf.inputs["Roughness"].default_value = roughness
    bsdf.inputs["Metallic"].default_value = metallic
    return mat


def add_box(name, size, location, mat, rotation=(0.0, 0.0, 0.0)):
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=location, rotation=rotation)
    ob = bpy.context.object
    ob.name = name
    ob.scale = size
    ob.data.materials.append(mat)
    return ob


def add_cylinder(name, radius, depth, location, mat, rotation=(0.0, 0.0, 0.0), verts=24):
    bpy.ops.mesh.primitive_cylinder_add(radius=radius, depth=depth, vertices=verts,
                                        location=location, rotation=rotation)
    ob = bpy.context.object
    ob.name = name
    ob.data.materials.append(mat)
    return ob


def add_beam(name, p1, p2, width, height, mat):
    """Box spanning two points in the XY plane (tongue members)."""
    a, b = Vector(p1), Vector(p2)
    d = b - a
    ang = math.atan2(d.y, d.x) - math.pi * 0.5
    return add_box(name, (width, d.length, height), (a + b) * 0.5, mat, (0.0, 0.0, ang))


def add_fender(name, center, radius, width, thickness, mat, segs=12):
    """Half-round arch swept over the wheel (axis along X)."""
    bm = bmesh.new()
    rings = []
    for i in range(segs + 1):
        ang = math.pi * i / segs
        cy, cz = math.cos(ang), math.sin(ang)
        ring = []
        for x, r in ((-width * 0.5, radius), (width * 0.5, radius),
                     (width * 0.5, radius + thickness), (-width * 0.5, radius + thickness)):
            ring.append(bm.verts.new((x, cy * r, cz * r)))
        rings.append(ring)
    for i in range(segs):
        lo, hi = rings[i], rings[i + 1]
        for k in range(4):
            n = (k + 1) % 4
            bm.faces.new((lo[k], lo[n], hi[n], hi[k]))
    bm.faces.new(rings[0][::-1])
    bm.faces.new(rings[-1])
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    me = bpy.data.meshes.new(name)
    bm.to_mesh(me)
    bm.free()
    ob = bpy.data.objects.new(name, me)
    bpy.context.collection.objects.link(ob)
    ob.location = center
    ob.data.materials.append(mat)
    return ob


def add_wheel(side, x, y, z, rubber, hub_mat):
    rot = (0.0, math.pi * 0.5, 0.0)
    add_cylinder("Tire_" + side, 0.32, 0.22, (x, y, z), rubber, rot, verts=28)
    add_cylinder("Rim_" + side, 0.18, 0.235, (x, y, z), hub_mat, rot, verts=20)
    add_cylinder("Hub_" + side, 0.07, 0.27, (x, y, z), hub_mat, rot, verts=12)


clear_scene()

steel = make_material("SteelFrame", (0.10, 0.11, 0.13), 0.45, 0.85)
galv = make_material("GalvanizedSteel", (0.62, 0.64, 0.66), 0.35, 0.9)
wood = make_material("DeckPlank", (0.52, 0.38, 0.22), 0.85, 0.0)
rubber = make_material("TireRubber", (0.035, 0.035, 0.04), 0.9, 0.0)
lens = make_material("LampLens", (0.6, 0.03, 0.03), 0.25, 0.0)
ground_mat = make_material("Ground", (0.30, 0.31, 0.30), 0.95, 0.0)

AXLE_Y, WHEEL_Z, TRACK = 0.10, 0.32, 0.92

add_box("Ground", (16.0, 16.0, 0.05), (0.0, 0.0, -0.025), ground_mat)

# --- frame and deck -------------------------------------------------------
add_box("FrameRail_L", (0.09, 2.60, 0.14), (-0.70, 0.0, 0.43), steel)
add_box("FrameRail_R", (0.09, 2.60, 0.14), (0.70, 0.0, 0.43), steel)
for i, y in enumerate((-1.15, -0.55, 0.10, 0.70, 1.25)):
    add_box("CrossMember_%d" % i, (1.50, 0.08, 0.10), (0.0, y, 0.43), steel)
for i in range(6):
    x = -0.625 + i * 0.25
    add_box("DeckPlank_%d" % i, (0.235, 2.55, 0.05), (x, 0.0, 0.525), wood)

# --- stake pockets and side rails ----------------------------------------
for side, sx in (("L", -0.73), ("R", 0.73)):
    add_box("TopRail_" + side, (0.06, 2.55, 0.06), (sx, 0.0, 0.93), galv)
    for i, y in enumerate((-1.15, -0.40, 0.40, 1.15)):
        add_box("StakePost_%s%d" % (side, i), (0.06, 0.06, 0.35),
                (sx, y, 0.755), galv)
add_box("FrontRail", (1.52, 0.06, 0.06), (0.0, -1.28, 0.93), galv)
add_box("FrontPanel", (1.46, 0.04, 0.32), (0.0, -1.28, 0.74), galv)

# --- tongue, coupler and jack --------------------------------------------
add_beam("TongueBeam_L", (-0.62, -1.20, 0.44), (0.0, -2.05, 0.44), 0.09, 0.13, steel)
add_beam("TongueBeam_R", (0.62, -1.20, 0.44), (0.0, -2.05, 0.44), 0.09, 0.13, steel)
add_box("HitchTube", (0.10, 0.45, 0.12), (0.0, -2.18, 0.44), steel)
add_box("CouplerBody", (0.16, 0.24, 0.16), (0.0, -2.36, 0.42), galv)
add_cylinder("CouplerLatch", 0.035, 0.14, (0.0, -2.36, 0.53), galv, (math.pi * 0.5, 0, 0), 12)
add_cylinder("JackPost", 0.045, 0.50, (0.26, -1.85, 0.30), galv, verts=14)
add_cylinder("JackFoot", 0.11, 0.05, (0.26, -1.85, 0.05), galv, verts=16)
add_cylinder("JackCrank", 0.02, 0.24, (0.40, -1.85, 0.52), galv, (0, math.pi * 0.5, 0), 10)

# --- suspension, axle, wheels, fenders -----------------------------------
add_cylinder("Axle", 0.05, 1.90, (0.0, AXLE_Y, WHEEL_Z), steel, (0, math.pi * 0.5, 0), 16)
for side, sx in (("L", -1.0), ("R", 1.0)):
    add_box("LeafSpring_" + side, (0.08, 0.80, 0.04), (sx * 0.70, AXLE_Y, 0.36), steel)
    add_box("SpringHanger_%s_F" % side, (0.07, 0.06, 0.14), (sx * 0.70, AXLE_Y - 0.38, 0.44), steel)
    add_box("SpringHanger_%s_R" % side, (0.07, 0.06, 0.14), (sx * 0.70, AXLE_Y + 0.38, 0.44), steel)
    add_wheel(side, sx * TRACK, AXLE_Y, WHEEL_Z, rubber, galv)
    add_fender("Fender_" + side, (sx * TRACK, AXLE_Y, WHEEL_Z), 0.40, 0.28, 0.03, galv)

# --- tailgate ramp and lights --------------------------------------------
add_box("RampGate", (1.48, 0.90, 0.05), (0.0, 1.55, 0.94), galv, (math.radians(-62.0), 0, 0))
add_box("TailLight_L", (0.14, 0.07, 0.10), (-0.70, 1.32, 0.62), lens)
add_box("TailLight_R", (0.14, 0.07, 0.10), (0.70, 1.32, 0.62), lens)
add_box("LicensePlate", (0.28, 0.02, 0.15), (0.0, 1.33, 0.60), galv)

# --- lighting and camera --------------------------------------------------
sun_data = bpy.data.lights.new("Sun", type='SUN')
sun_data.energy = 4.0
sun = bpy.data.objects.new("Sun", sun_data)
bpy.context.collection.objects.link(sun)
sun.location = (4.0, -5.0, 7.0)
sun.rotation_euler = (math.radians(52.0), 0.0, math.radians(38.0))

fill_data = bpy.data.lights.new("Fill", type='AREA')
fill_data.energy = 220.0
fill_data.size = 5.0
fill = bpy.data.objects.new("Fill", fill_data)
bpy.context.collection.objects.link(fill)
fill.location = (-4.5, 3.0, 4.0)
fill.rotation_euler = (math.radians(58.0), 0.0, math.radians(-135.0))

cam_data = bpy.data.cameras.new("Camera")
cam_data.lens = 50.0
cam = bpy.data.objects.new("Camera", cam_data)
bpy.context.collection.objects.link(cam)
cam.location = (4.4, -4.8, 2.6)
target = Vector((0.0, -0.25, 0.60))
cam.rotation_euler = (target - cam.location).to_track_quat('-Z', 'Y').to_euler()
bpy.context.scene.camera = cam
