import bpy
import bmesh
import math
from mathutils import Vector, Matrix

HINGE = Vector((0.0, 0.115, 0.014))
LID_ANGLE = math.radians(100.0)


def clear_scene():
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete(use_global=False)
    for coll in (bpy.data.meshes, bpy.data.materials, bpy.data.cameras, bpy.data.lights):
        for item in list(coll):
            if item.users == 0:
                coll.remove(item)


def new_material(name, color, roughness=0.45, metallic=0.0, emission=None):
    mat = bpy.data.materials.new(name)
    mat.use_nodes = True
    bsdf = mat.node_tree.nodes["Principled BSDF"]
    bsdf.inputs["Base Color"].default_value = (*color, 1.0)
    bsdf.inputs["Roughness"].default_value = roughness
    bsdf.inputs["Metallic"].default_value = metallic
    if emission is not None:
        bsdf.inputs["Emission Color"].default_value = (*emission[0], 1.0)
        bsdf.inputs["Emission Strength"].default_value = emission[1]
    return mat


def finish(name, bm, location, mat, bevel=0.0, segments=2):
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    mesh = bpy.data.meshes.new(name)
    bm.to_mesh(mesh)
    bm.free()
    mesh.shade_smooth() if False else None
    obj = bpy.data.objects.new(name, mesh)
    bpy.context.collection.objects.link(obj)
    obj.location = location
    obj.data.materials.append(mat)
    if bevel > 0.0:
        mod = obj.modifiers.new("Bevel", 'BEVEL')
        mod.width = bevel
        mod.segments = segments
        mod.limit_method = 'ANGLE'
    return obj


def add_box(name, size, location, mat, bevel=0.0):
    bm = bmesh.new()
    bmesh.ops.create_cube(bm, size=1.0, matrix=Matrix.Diagonal(Vector(size).to_4d()))
    return finish(name, bm, location, mat, bevel)


def add_cylinder(name, radius, depth, location, mat, axis='Z', segments=24):
    bm = bmesh.new()
    mat_rot = Matrix.Rotation(math.radians(90.0), 4, 'Y') if axis == 'X' else Matrix.Identity(4)
    bmesh.ops.create_cone(bm, cap_ends=True, cap_tris=False, segments=segments,
                          radius1=radius, radius2=radius, depth=depth, matrix=mat_rot)
    return finish(name, bm, location, mat)


def add_keys(name, mat):
    bm = bmesh.new()
    rows, cols = 5, 14
    kw, kd, kh, gap = 0.017, 0.017, 0.0045, 0.0026
    deck_y = 0.038
    total_w = cols * (kw + gap) - gap
    total_d = rows * (kd + gap) - gap
    for r in range(rows):
        for c in range(cols):
            x = -total_w / 2 + kw / 2 + c * (kw + gap)
            y = deck_y + total_d / 2 - kd / 2 - r * (kd + gap)
            loc = Matrix.Translation((x, y, kh / 2))
            bmesh.ops.create_cube(bm, size=1.0, matrix=loc @ Matrix.Diagonal(Vector((kw, kd, kh)).to_4d()))
    space_y = deck_y - total_d / 2 - (kd + gap) / 2
    loc = Matrix.Translation((0.0, space_y, kh / 2))
    bmesh.ops.create_cube(bm, size=1.0, matrix=loc @ Matrix.Diagonal(Vector((0.10, kd, kh)).to_4d()))
    return finish(name, bm, (0.0, 0.0, 0.0165), mat, bevel=0.0009)


def rotate_lid(objects):
    piv = Matrix.Translation(HINGE) @ Matrix.Rotation(LID_ANGLE, 4, 'X') @ Matrix.Translation(-HINGE)
    for obj in objects:
        obj.matrix_world = piv @ obj.matrix_world


def add_camera(location, target):
    cam = bpy.data.objects.new("Camera", bpy.data.cameras.new("Camera"))
    bpy.context.collection.objects.link(cam)
    cam.location = location
    cam.data.lens = 50.0
    cam.rotation_euler = (Vector(target) - Vector(location)).to_track_quat('-Z', 'Y').to_euler()
    bpy.context.scene.camera = cam


def add_light(name, location, energy, size):
    light = bpy.data.lights.new(name, 'AREA')
    light.energy = energy
    light.size = size
    obj = bpy.data.objects.new(name, light)
    bpy.context.collection.objects.link(obj)
    obj.location = location
    obj.rotation_euler = (Vector((0.0, 0.05, 0.05)) - Vector(location)).to_track_quat('-Z', 'Y').to_euler()


clear_scene()

alu = new_material("Aluminium", (0.62, 0.63, 0.65), roughness=0.32, metallic=1.0)
dark = new_material("DarkPlastic", (0.05, 0.05, 0.055), roughness=0.55)
keycap = new_material("Keycap", (0.11, 0.11, 0.12), roughness=0.65)
glass = new_material("TrackpadGlass", (0.42, 0.43, 0.45), roughness=0.18)
screen = new_material("ScreenPanel", (0.03, 0.05, 0.09), roughness=0.12,
                      emission=((0.32, 0.46, 0.72), 3.0))
rubber = new_material("FootRubber", (0.03, 0.03, 0.03), roughness=0.85)
desk_mat = new_material("Desk", (0.24, 0.22, 0.20), roughness=0.7)

add_box("Desk", (2.0, 2.0, 0.02), (0.0, 0.0, -0.011), desk_mat)
add_box("BaseBody", (0.34, 0.24, 0.016), (0.0, 0.0, 0.008), alu, bevel=0.0022)
add_box("KeyboardWell", (0.29, 0.125, 0.0016), (0.0, 0.031, 0.0161), dark)
add_keys("Keys", keycap)
add_box("TrackpadGlass", (0.104, 0.068, 0.0014), (0.0, -0.076, 0.0163), glass, bevel=0.0004)

for i, (fx, fy) in enumerate([(-0.145, -0.10), (0.145, -0.10), (-0.145, 0.10), (0.145, 0.10)]):
    add_cylinder("Foot_%d" % i, 0.007, 0.002, (fx, fy, -0.001), rubber)

for i, hx in enumerate((-0.095, 0.095)):
    add_cylinder("Hinge_%d" % i, 0.0062, 0.055, (hx, HINGE.y, HINGE.z), dark, axis='X')

lid_parts = [
    add_box("LidShell", (0.34, 0.23, 0.009), (0.0, HINGE.y + 0.115, HINGE.z), alu, bevel=0.0018),
    add_box("LidBezel", (0.325, 0.215, 0.0022), (0.0, HINGE.y + 0.115, HINGE.z + 0.0051), dark),
    add_box("ScreenPanel", (0.305, 0.192, 0.0012), (0.0, HINGE.y + 0.118, HINGE.z + 0.0064), screen),
]
rotate_lid(lid_parts)

add_light("KeyLight", (0.45, -0.55, 0.75), 220.0, 1.0)
add_light("FillLight", (-0.6, -0.25, 0.45), 70.0, 1.2)
add_camera((0.44, -0.56, 0.33), (0.0, 0.02, 0.10))

bpy.context.scene.world = bpy.context.scene.world or bpy.data.worlds.new("World")
bpy.context.scene.world.use_nodes = True
bpy.context.scene.world.node_tree.nodes["Background"].inputs[0].default_value = (0.05, 0.05, 0.06, 1.0)
