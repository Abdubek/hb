"""Two-seat park bench: cast iron frame with slatted wooden seat and back."""
import bpy
import bmesh
import math
from mathutils import Vector

SEAT_Z = 0.44
SLAT_LEN = 1.66
SIDES = (("L", -0.78), ("R", 0.78))


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


def add_box(name, size, location, mat, parent=None, bevel=0.005):
    """Axis aligned box built from bmesh, optionally softened with a bevel."""
    me = bpy.data.meshes.new(name)
    bm = bmesh.new()
    bmesh.ops.create_cube(bm, size=1.0)
    bmesh.ops.scale(bm, vec=Vector(size), verts=bm.verts)
    bm.to_mesh(me)
    bm.free()
    ob = bpy.data.objects.new(name, me)
    ob.location = location
    ob.data.materials.append(mat)
    bpy.context.collection.objects.link(ob)
    if parent is not None:
        ob.parent = parent
    if bevel:
        mod = ob.modifiers.new("Bevel", 'BEVEL')
        mod.width = bevel
        mod.segments = 2
    return ob


def add_empty(name, location, rotation=(0.0, 0.0, 0.0)):
    ob = bpy.data.objects.new(name, None)
    ob.location = location
    ob.rotation_euler = rotation
    ob.empty_display_size = 0.15
    bpy.context.collection.objects.link(ob)
    return ob


def aim_camera(location, target, lens=50.0):
    cam = bpy.data.objects.new("Camera", bpy.data.cameras.new("Camera"))
    cam.data.lens = lens
    cam.location = location
    direction = Vector(target) - Vector(location)
    cam.rotation_euler = direction.to_track_quat('-Z', 'Y').to_euler()
    bpy.context.collection.objects.link(cam)
    bpy.context.scene.camera = cam
    return cam


reset_scene()
WOOD = new_material("Bench_Wood", (0.36, 0.18, 0.08), 0.55)
IRON = new_material("Bench_Iron", (0.045, 0.05, 0.055), 0.35, 0.85)
PAVING = new_material("Paving_Concrete", (0.36, 0.35, 0.33), 0.9)

add_box("Paving", (6.0, 6.0, 0.08), (0.0, 0.0, -0.04), PAVING, bevel=0.0)

frame = add_empty("Bench_Frame", (0.0, 0.0, 0.0))
for tag, x in SIDES:
    add_box("Leg_Front_%s" % tag, (0.05, 0.05, SEAT_Z), (x, -0.22, SEAT_Z * 0.5), IRON, frame)
    add_box("Leg_Rear_%s" % tag, (0.05, 0.05, SEAT_Z), (x, 0.22, SEAT_Z * 0.5), IRON, frame)
    add_box("Side_Rail_%s" % tag, (0.05, 0.55, 0.06), (x, 0.0, SEAT_Z - 0.06), IRON, frame)
    add_box("Foot_%s" % tag, (0.07, 0.60, 0.03), (x, 0.0, 0.015), IRON, frame)
add_box("Stretcher_Front", (1.56, 0.05, 0.05), (0.0, -0.22, 0.14), IRON, frame)
add_box("Stretcher_Rear", (1.56, 0.05, 0.05), (0.0, 0.22, 0.14), IRON, frame)

for i in range(5):
    y = -0.235 + i * 0.118
    add_box("Seat_Slat_%02d" % (i + 1), (SLAT_LEN, 0.09, 0.032), (0.0, y, SEAT_Z + 0.016), WOOD, frame)

# the backrest leans back ten degrees, so it gets its own tilted parent
back = add_empty("Bench_BackFrame", (0.0, 0.245, SEAT_Z), (-math.radians(10.0), 0.0, 0.0))
back.parent = frame
for tag, x in SIDES:
    add_box("Back_Post_%s" % tag, (0.05, 0.05, 0.56), (x, 0.0, 0.26), IRON, back)
for i in range(3):
    add_box("Back_Slat_%02d" % (i + 1), (SLAT_LEN, 0.032, 0.10), (0.0, 0.0, 0.12 + i * 0.15), WOOD, back)
add_box("Back_Cap_Rail", (SLAT_LEN, 0.05, 0.05), (0.0, 0.0, 0.545), IRON, back)

for tag, x in SIDES:
    add_box("Arm_Support_%s" % tag, (0.045, 0.045, 0.22), (x, -0.18, SEAT_Z + 0.13), IRON, frame)
    add_box("Armrest_%s" % tag, (0.07, 0.56, 0.04), (x, 0.0, SEAT_Z + 0.26), WOOD, frame)

sun = bpy.data.objects.new("Sun", bpy.data.lights.new("Sun", type='SUN'))
sun.data.energy = 3.0
sun.location = (3.0, -4.0, 5.0)
sun.rotation_euler = (math.radians(50.0), 0.0, math.radians(35.0))
bpy.context.collection.objects.link(sun)

aim_camera((2.6, -2.9, 1.7), (0.0, 0.0, 0.55))
