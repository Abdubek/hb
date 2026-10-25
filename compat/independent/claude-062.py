import bpy
import math
from mathutils import Vector


def clear_scene():
    for ob in list(bpy.data.objects):
        bpy.data.objects.remove(ob, do_unlink=True)
    for block in (bpy.data.meshes, bpy.data.materials, bpy.data.cameras, bpy.data.lights):
        for item in list(block):
            if item.users == 0:
                block.remove(item)


def make_material(name, color, roughness=0.5, metallic=0.0, emission_strength=0.0):
    mat = bpy.data.materials.new(name)
    mat.use_nodes = True
    bsdf = mat.node_tree.nodes["Principled BSDF"]
    bsdf.inputs["Base Color"].default_value = (*color, 1.0)
    bsdf.inputs["Roughness"].default_value = roughness
    bsdf.inputs["Metallic"].default_value = metallic
    if emission_strength > 0.0:
        bsdf.inputs["Emission Color"].default_value = (*color, 1.0)
        bsdf.inputs["Emission Strength"].default_value = emission_strength
    return mat


def add_box(name, size, location, material, rotation=(0.0, 0.0, 0.0)):
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=location, rotation=rotation)
    ob = bpy.context.active_object
    ob.name = name
    ob.scale = size
    ob.data.materials.append(material)
    return ob


def add_cylinder(name, radius, depth, location, material, rotation=(0.0, 0.0, 0.0)):
    bpy.ops.mesh.primitive_cylinder_add(radius=radius, depth=depth, vertices=24,
                                       location=location, rotation=rotation)
    ob = bpy.context.active_object
    ob.name = name
    ob.data.materials.append(material)
    return ob


def add_camera(location, target, lens=45.0):
    cam_data = bpy.data.cameras.new("ConsoleCam")
    cam_data.lens = lens
    cam = bpy.data.objects.new("Camera", cam_data)
    bpy.context.collection.objects.link(cam)
    cam.location = location
    direction = Vector(target) - Vector(location)
    cam.rotation_euler = direction.to_track_quat('-Z', 'Y').to_euler()
    bpy.context.scene.camera = cam
    return cam


def add_light(name, location, energy, size=3.0):
    data = bpy.data.lights.new(name, type='AREA')
    data.energy = energy
    data.size = size
    ob = bpy.data.objects.new(name, data)
    bpy.context.collection.objects.link(ob)
    ob.location = location
    ob.rotation_euler = (Vector((0.0, 0.0, 0.6)) - Vector(location)).to_track_quat('-Z', 'Y').to_euler()
    return ob


clear_scene()

wood = make_material("WalnutWood", (0.20, 0.11, 0.06), roughness=0.45)
wood_light = make_material("OakFront", (0.42, 0.28, 0.16), roughness=0.40)
metal = make_material("BrushedMetal", (0.62, 0.63, 0.66), roughness=0.30, metallic=1.0)
plastic = make_material("BlackPlastic", (0.02, 0.02, 0.025), roughness=0.35)
screen = make_material("ScreenGlow", (0.05, 0.20, 0.45), roughness=0.10, emission_strength=1.6)
floor_mat = make_material("FloorConcrete", (0.35, 0.34, 0.32), roughness=0.85)

add_box("Floor", (7.0, 5.0, 0.05), (0.0, 0.0, -0.025), floor_mat)

# --- Console carcass ---------------------------------------------------------
W, D, H = 1.90, 0.46, 0.52
LEG = 0.14
base_z = LEG

add_box("Console_Top", (W, D, 0.04), (0.0, 0.0, base_z + H - 0.02), wood)
add_box("Console_Bottom", (W, D, 0.03), (0.0, 0.0, base_z + 0.015), wood)
add_box("Console_Back", (W, 0.02, H), (0.0, D / 2 - 0.01, base_z + H / 2), wood)
for sx in (-1, 1):
    add_box("Console_Side_%s" % ("L" if sx < 0 else "R"),
            (0.03, D, H), (sx * (W / 2 - 0.015), 0.0, base_z + H / 2), wood)

for ix, sx in enumerate((-1, 1)):
    for iy, sy in enumerate((-1, 1)):
        add_cylinder("Console_Leg_%d%d" % (ix, iy), 0.022, LEG,
                     (sx * (W / 2 - 0.09), sy * (D / 2 - 0.07), LEG / 2), metal)

# --- Drawers -----------------------------------------------------------------
DRAWERS = 3
cell_w = (W - 0.06) / DRAWERS
for i in range(DRAWERS):
    x = -W / 2 + 0.03 + cell_w * (i + 0.5)
    front_z = base_z + H / 2 - 0.02
    add_box("Drawer_Front_%d" % i, (cell_w - 0.02, 0.02, H - 0.10),
            (x, -D / 2 + 0.01, front_z), wood_light)
    add_cylinder("Drawer_Handle_%d" % i, 0.012, cell_w * 0.5,
                 (x, -D / 2 - 0.02, front_z), metal, rotation=(0.0, math.pi / 2, 0.0))
    if i < DRAWERS - 1:
        add_box("Console_Divider_%d" % i, (0.02, D - 0.04, H - 0.08),
                (-W / 2 + 0.03 + cell_w * (i + 1), 0.0, base_z + H / 2), wood)

# --- Television --------------------------------------------------------------
top_z = base_z + H
add_box("TV_BasePlate", (0.42, 0.24, 0.02), (0.0, 0.02, top_z + 0.01), plastic)
add_box("TV_Neck", (0.10, 0.06, 0.16), (0.0, 0.03, top_z + 0.10), plastic)

panel_z = top_z + 0.18 + 0.35
add_box("TV_Panel", (1.16, 0.045, 0.70), (0.0, 0.05, panel_z), plastic)
add_box("TV_Screen", (1.10, 0.01, 0.63), (0.0, 0.022, panel_z + 0.015), screen)
add_box("TV_Bezel_Bottom", (1.16, 0.02, 0.05), (0.0, 0.022, panel_z - 0.325), plastic)

# --- Small props on the top --------------------------------------------------
add_box("SoundBar", (0.55, 0.09, 0.07), (-0.58, -0.05, top_z + 0.035), plastic)
add_cylinder("Vase", 0.055, 0.20, (0.72, 0.02, top_z + 0.10), wood_light)

add_light("KeyLight", (2.2, -2.6, 3.0), 400.0, size=3.5)
add_light("FillLight", (-2.6, -2.0, 1.8), 120.0, size=2.5)
add_camera((2.6, -3.2, 1.85), (0.0, 0.0, 0.85), lens=45.0)
