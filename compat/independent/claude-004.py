"""Compact handheld game console: rounded shell, screen, d-pad and face buttons."""
import bpy
import bmesh
import math
from mathutils import Vector

BODY = (0.220, 0.115, 0.022)
TOP_Z = BODY[2]
DPAD_C = (-0.082, -0.030)
BTN_C = (0.082, -0.030)


def reset_scene():
    for ob in list(bpy.data.objects):
        bpy.data.objects.remove(ob, do_unlink=True)
    for me in list(bpy.data.meshes):
        bpy.data.meshes.remove(me)


def new_material(name, color, roughness=0.5, metallic=0.0, emission=None, strength=0.0):
    mat = bpy.data.materials.new(name)
    mat.use_nodes = True
    bsdf = mat.node_tree.nodes["Principled BSDF"]
    bsdf.inputs["Base Color"].default_value = (color[0], color[1], color[2], 1.0)
    bsdf.inputs["Roughness"].default_value = roughness
    bsdf.inputs["Metallic"].default_value = metallic
    if emission is not None and "Emission Color" in bsdf.inputs:
        bsdf.inputs["Emission Color"].default_value = (emission[0], emission[1], emission[2], 1.0)
        bsdf.inputs["Emission Strength"].default_value = strength
    return mat


def _link(name, bm, location, rotation, mat, parent, bevel, segments):
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
        mod.segments = segments
    return ob


def add_box(name, size, location, mat, parent=None, bevel=0.0015, segments=2,
            rotation=(0.0, 0.0, 0.0)):
    bm = bmesh.new()
    bmesh.ops.create_cube(bm, size=1.0)
    bmesh.ops.scale(bm, vec=Vector(size), verts=bm.verts)
    return _link(name, bm, location, rotation, mat, parent, bevel, segments)


def add_disc(name, radius, depth, location, mat, parent=None, segments=24,
             rotation=(0.0, 0.0, 0.0)):
    bm = bmesh.new()
    bmesh.ops.create_cone(bm, cap_ends=True, cap_tris=False, segments=segments,
                          radius1=radius, radius2=radius, depth=depth)
    return _link(name, bm, location, rotation, mat, parent, 0.0, 0)


def aim_camera(location, target, lens=45.0):
    cam = bpy.data.objects.new("Camera", bpy.data.cameras.new("Camera"))
    cam.data.lens = lens
    cam.location = location
    cam.rotation_euler = (Vector(target) - Vector(location)).to_track_quat('-Z', 'Y').to_euler()
    bpy.context.collection.objects.link(cam)
    bpy.context.scene.camera = cam
    return cam


reset_scene()
SHELL = new_material("Shell_Plastic", (0.32, 0.34, 0.38), 0.42)
TRIM = new_material("Trim_Plastic", (0.09, 0.09, 0.10), 0.35)
SCREEN = new_material("Screen_Glass", (0.02, 0.04, 0.06), 0.08,
                      emission=(0.10, 0.32, 0.55), strength=1.6)
BTN_A = new_material("Button_Red", (0.62, 0.10, 0.12), 0.3)
BTN_B = new_material("Button_Blue", (0.10, 0.22, 0.60), 0.3)
DESK = new_material("Desk_Surface", (0.28, 0.26, 0.24), 0.75)

add_box("Desk", (0.9, 0.9, 0.012), (0.0, 0.0, -0.006), DESK, bevel=0.0)

console = bpy.data.objects.new("Console", None)
console.empty_display_size = 0.05
bpy.context.collection.objects.link(console)

add_box("Shell_Body", BODY, (0.0, 0.0, TOP_Z * 0.5), SHELL, console, bevel=0.008, segments=4)
add_box("Screen_Bezel", (0.115, 0.075, 0.004), (0.0, 0.010, TOP_Z + 0.0005), TRIM, console,
        bevel=0.001)
add_box("Screen_Panel", (0.104, 0.062, 0.002), (0.0, 0.010, TOP_Z + 0.0025), SCREEN, console,
        bevel=0.0)

# directional pad built as a cross of two slabs plus a centre hub
add_box("DPad_Horizontal", (0.032, 0.011, 0.006), (DPAD_C[0], DPAD_C[1], TOP_Z + 0.001),
        TRIM, console, bevel=0.002)
add_box("DPad_Vertical", (0.011, 0.032, 0.006), (DPAD_C[0], DPAD_C[1], TOP_Z + 0.001),
        TRIM, console, bevel=0.002)
add_disc("DPad_Hub", 0.0055, 0.0065, (DPAD_C[0], DPAD_C[1], TOP_Z + 0.001), TRIM, console, 16)

for label, dx, dy, mat in (("A", 0.017, 0.0, BTN_A), ("B", 0.0, -0.017, BTN_A),
                           ("X", 0.0, 0.017, BTN_B), ("Y", -0.017, 0.0, BTN_B)):
    add_disc("Button_" + label, 0.0075, 0.006, (BTN_C[0] + dx, BTN_C[1] + dy, TOP_Z + 0.001),
             mat, console, 20)

for label, dx in (("Select", -0.016), ("Start", 0.016)):
    add_disc("Pill_" + label, 0.005, 0.004, (dx, -0.048, TOP_Z), TRIM, console, 16)

# small speaker grilles either side of the lower shell
for tag, sx in (("L", -1.0), ("R", 1.0)):
    for row in range(2):
        for col in range(3):
            add_disc("Grille_%s_%d%d" % (tag, row, col), 0.0022, 0.004,
                     (sx * (0.076 + col * 0.008), -0.044 + row * 0.009, TOP_Z - 0.001),
                     TRIM, console, 10)

for tag, sx in (("L", -1.0), ("R", 1.0)):
    add_box("Shoulder_Button_%s" % tag, (0.036, 0.018, 0.010),
            (sx * 0.072, 0.052, TOP_Z - 0.006), TRIM, console, bevel=0.003)
add_box("Cartridge_Slot", (0.052, 0.008, 0.006), (0.0, 0.054, TOP_Z - 0.008), TRIM, console,
        bevel=0.001)
add_disc("Power_LED", 0.003, 0.003, (-0.100, 0.036, TOP_Z - 0.004), BTN_A, console, 12,
         (0.0, math.radians(90.0), 0.0))

key = bpy.data.objects.new("KeyLight", bpy.data.lights.new("KeyLight", type='AREA'))
key.data.energy = 60.0
key.data.size = 0.6
key.location = (0.18, -0.20, 0.35)
key.rotation_euler = (math.radians(30.0), 0.0, math.radians(40.0))
bpy.context.collection.objects.link(key)

aim_camera((0.15, -0.24, 0.19), (0.0, -0.005, 0.014), lens=50.0)
