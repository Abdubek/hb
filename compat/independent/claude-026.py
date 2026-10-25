import bpy
import bmesh
from math import pi
from mathutils import Vector


def clear_scene():
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete(use_global=False)
    for block in (bpy.data.meshes, bpy.data.curves, bpy.data.materials):
        for item in list(block):
            if item.users == 0:
                block.remove(item)


def make_material(name, color, roughness=0.6, metallic=0.0):
    mat = bpy.data.materials.new(name)
    mat.use_nodes = True
    bsdf = mat.node_tree.nodes["Principled BSDF"]
    bsdf.inputs["Base Color"].default_value = (color[0], color[1], color[2], 1.0)
    bsdf.inputs["Roughness"].default_value = roughness
    bsdf.inputs["Metallic"].default_value = metallic
    return mat


def add_box(name, size, loc, mat, rot=(0.0, 0.0, 0.0)):
    mesh = bpy.data.meshes.new(name)
    bm = bmesh.new()
    bmesh.ops.create_cube(bm, size=1.0)
    bmesh.ops.scale(bm, vec=Vector(size), verts=bm.verts)
    bm.to_mesh(mesh)
    bm.free()
    obj = bpy.data.objects.new(name, mesh)
    obj.location = loc
    obj.rotation_euler = rot
    obj.data.materials.append(mat)
    bpy.context.collection.objects.link(obj)
    return obj


def add_text(name, body, loc, rot, mat, size=0.075):
    curve = bpy.data.curves.new(name, 'FONT')
    curve.body = body
    curve.size = size
    curve.align_x = 'CENTER'
    curve.align_y = 'CENTER'
    curve.extrude = 0.0005
    obj = bpy.data.objects.new(name, curve)
    obj.location = loc
    obj.rotation_euler = rot
    obj.data.materials.append(mat)
    bpy.context.collection.objects.link(obj)
    return obj


def build_pallet(deck_mat, block_mat):
    # Euro-style pallet: 1.20 x 0.80 x 0.122 m, origin at floor level.
    for i, y in enumerate((-0.3275, -0.16375, 0.0, 0.16375, 0.3275)):
        add_box("Pallet_TopBoard_%d" % (i + 1), (1.20, 0.145, 0.022),
                (0.0, y, 0.111), deck_mat)
    for i, y in enumerate((-0.35, 0.0, 0.35)):
        add_box("Pallet_BottomBoard_%d" % (i + 1), (1.20, 0.14, 0.022),
                (0.0, y, 0.011), deck_mat)
    n = 0
    for x in (-0.55, 0.0, 0.55):
        for y in (-0.35, 0.0, 0.35):
            n += 1
            add_box("Pallet_Block_%d" % n, (0.10, 0.10, 0.078),
                    (x, y, 0.061), block_mat)


def build_crate(index, x, y, crate_mat, lid_mat, label_mat, ink_mat):
    deck_top = 0.122
    w, d, h = 0.36, 0.34, 0.28
    cz = deck_top + h * 0.5
    add_box("Crate_%02d_Body" % index, (w, d, h), (x, y, cz), crate_mat)
    add_box("Crate_%02d_Lid" % index, (w + 0.02, d + 0.02, 0.022),
            (x, y, deck_top + h + 0.011), lid_mat)
    for sx in (-1.0, 1.0):
        add_box("Crate_%02d_Batten_%s" % (index, "L" if sx < 0 else "R"),
                (0.03, d + 0.012, h * 0.94),
                (x + sx * (w * 0.5 - 0.015), y, cz), lid_mat)

    # Labels always face away from the pallet centre line in Y.
    outward = 1.0 if y > 0.0 else -1.0
    face_y = y + outward * (d * 0.5)
    add_box("Crate_%02d_Label" % index, (0.19, 0.004, 0.115),
            (x, face_y + outward * 0.002, cz + 0.02), label_mat)
    yaw = 0.0 if outward < 0.0 else pi
    add_text("Crate_%02d_LabelText" % index, "CRATE %02d" % index,
             (x, face_y + outward * 0.006, cz + 0.045),
             (pi * 0.5, 0.0, yaw), ink_mat, size=0.042)
    add_text("Crate_%02d_LabelCode" % index, "NO.%d / 25KG" % index,
             (x, face_y + outward * 0.006, cz - 0.002),
             (pi * 0.5, 0.0, yaw), ink_mat, size=0.026)


def add_camera(loc, target):
    cam = bpy.data.objects.new("Camera", bpy.data.cameras.new("Camera"))
    cam.location = loc
    cam.data.lens = 50.0
    cam.rotation_euler = (Vector(target) - Vector(loc)).to_track_quat('-Z', 'Y').to_euler()
    bpy.context.collection.objects.link(cam)
    bpy.context.scene.camera = cam


def add_light(loc, energy=5.0):
    data = bpy.data.lights.new("Sun", 'SUN')
    data.energy = energy
    obj = bpy.data.objects.new("Sun", data)
    obj.location = loc
    obj.rotation_euler = (0.6, 0.25, -0.9)
    bpy.context.collection.objects.link(obj)


clear_scene()

deck = make_material("Wood_Deck", (0.62, 0.44, 0.24), roughness=0.72)
block = make_material("Wood_Block", (0.44, 0.30, 0.17), roughness=0.85)
crate = make_material("Wood_Crate", (0.74, 0.58, 0.36), roughness=0.68)
lid = make_material("Wood_Crate_Trim", (0.56, 0.40, 0.23), roughness=0.75)
paper = make_material("Label_Paper", (0.93, 0.92, 0.87), roughness=0.55)
ink = make_material("Label_Ink", (0.06, 0.06, 0.07), roughness=0.5)
floor = make_material("Floor_Concrete", (0.35, 0.35, 0.36), roughness=0.9)

add_box("Floor", (6.0, 6.0, 0.08), (0.0, 0.0, -0.04), floor)
build_pallet(deck, block)

index = 0
for x in (-0.4, 0.0, 0.4):
    for y in (-0.185, 0.185):
        index += 1
        build_crate(index, x, y, crate, lid, paper, ink)

add_light((2.5, -3.0, 4.0))
add_camera((1.85, -2.05, 1.35), (0.0, 0.0, 0.28))
