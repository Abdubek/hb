import bpy
import math
import random
from mathutils import Vector

random.seed(11)


def clear_scene():
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete(use_global=False)
    for block in (bpy.data.meshes, bpy.data.materials):
        for item in list(block):
            if item.users == 0:
                block.remove(item)


def material(name, color, roughness=0.6, metallic=0.0):
    mat = bpy.data.materials.new(name)
    mat.use_nodes = True
    bsdf = mat.node_tree.nodes["Principled BSDF"]
    bsdf.inputs["Base Color"].default_value = (*color, 1.0)
    bsdf.inputs["Roughness"].default_value = roughness
    bsdf.inputs["Metallic"].default_value = metallic
    return mat


def finish(obj, name, mat):
    obj.name = name
    obj.data.name = name
    obj.data.materials.append(mat)
    return obj


def box(name, size, location, mat, rotation=(0, 0, 0)):
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=location, rotation=rotation)
    obj = bpy.context.object
    obj.scale = size
    return finish(obj, name, mat)


def cylinder(name, radius, depth, location, mat, verts=32, rotation=(0, 0, 0)):
    bpy.ops.mesh.primitive_cylinder_add(vertices=verts, radius=radius, depth=depth,
                                        location=location, rotation=rotation)
    return finish(bpy.context.object, name, mat)


def brace_between(name, a, b, radius, mat):
    a, b = Vector(a), Vector(b)
    d = b - a
    bpy.ops.mesh.primitive_cylinder_add(vertices=12, radius=radius, depth=d.length,
                                        location=(a + b) / 2)
    obj = bpy.context.object
    obj.rotation_euler = d.to_track_quat('Z', 'Y').to_euler()
    return finish(obj, name, mat)


def add_camera(location, target, lens=42.0):
    bpy.ops.object.camera_add(location=location)
    cam = bpy.context.object
    cam.name = "SceneCamera"
    cam.data.lens = lens
    cam.rotation_euler = (Vector(target) - Vector(location)).to_track_quat('-Z', 'Y').to_euler()
    bpy.context.scene.camera = cam
    return cam


def build_barrel(name, location, mat_body, mat_rim):
    x, y, z = location
    cylinder(name, 0.27, 0.86, (x, y, z + 0.43), mat_body, verts=32)
    for dz in (0.24, 0.62):
        cylinder(name + "Rib", 0.29, 0.05, (x, y, z + dz), mat_rim, verts=32)
    cylinder(name + "Lid", 0.28, 0.04, (x, y, z + 0.87), mat_rim, verts=32)


clear_scene()

mat_upright = material("RackUprightOrange", (0.62, 0.24, 0.05), roughness=0.5, metallic=0.4)
mat_beam = material("RackBeamBlue", (0.08, 0.20, 0.45), roughness=0.45, metallic=0.4)
mat_deck = material("DeckPlywood", (0.55, 0.42, 0.26), roughness=0.8)
mat_carton = material("CartonBrown", (0.58, 0.42, 0.25), roughness=0.85)
mat_carton2 = material("CartonPale", (0.72, 0.62, 0.46), roughness=0.85)
mat_drum = material("DrumBlue", (0.10, 0.30, 0.58), roughness=0.4)
mat_steel = material("GalvSteel", (0.55, 0.56, 0.58), roughness=0.35, metallic=1.0)
mat_floor = material("ConcreteFloor", (0.42, 0.42, 0.43), roughness=0.9)

BAY_X = 2.6          # half length of the rack along X
DEPTH = 0.55         # half depth along Y
HEIGHT = 3.1
LEVELS = [0.12, 1.25, 2.30]

# uprights at the four corners
for i, sx in enumerate((-1, 1)):
    for j, sy in enumerate((-1, 1)):
        x, y = sx * BAY_X, sy * DEPTH
        box("RackUpright_%d%d" % (i, j), (0.10, 0.07, HEIGHT), (x, y, HEIGHT / 2), mat_upright)
        box("RackFootPlate_%d%d" % (i, j), (0.20, 0.18, 0.03), (x, y, 0.015), mat_steel)

# horizontal load beams and decking at every level
for lvl, z in enumerate(LEVELS):
    for sy in (-1, 1):
        box("RackBeam_L%d_%s" % (lvl, "F" if sy < 0 else "B"),
            (2 * BAY_X, 0.06, 0.13), (0.0, sy * DEPTH, z), mat_beam)
    box("RackDeck_L%d" % lvl, (2 * BAY_X - 0.06, 2 * DEPTH, 0.035),
        (0.0, 0.0, z + 0.08), mat_deck)

# diagonal side bracing between the uprights
for sx in (-1, 1):
    for lvl in range(len(LEVELS) - 1):
        z0, z1 = LEVELS[lvl] + 0.1, LEVELS[lvl + 1] - 0.05
        brace_between("RackBrace_%s_%d" % ("L" if sx < 0 else "R", lvl),
                      (sx * BAY_X, -DEPTH, z0), (sx * BAY_X, DEPTH, z1), 0.022, mat_upright)

# barrels on the bottom deck
base_z = LEVELS[0] + 0.10
for n, x in enumerate((-2.05, -1.45, -0.85)):
    build_barrel("Barrel_%d" % n, (x, 0.0, base_z), mat_drum, mat_steel)

# pallet of cartons sharing the bottom level
box("Pallet", (1.15, 0.95, 0.11), (1.30, 0.0, base_z + 0.055), mat_deck)
for n, (dx, dy) in enumerate(((-0.28, -0.22), (0.28, -0.22), (-0.28, 0.24), (0.28, 0.24))):
    box("PalletCarton_%d" % n, (0.52, 0.42, 0.44),
        (1.30 + dx, dy, base_z + 0.11 + 0.22), mat_carton,
        rotation=(0, 0, random.uniform(-0.05, 0.05)))

# mixed cartons on the upper levels
carton_plan = [
    (1, -2.10, 0.0, (0.72, 0.62, 0.55), mat_carton),
    (1, -1.28, -0.10, (0.62, 0.55, 0.48), mat_carton2),
    (1, -0.50, 0.08, (0.66, 0.60, 0.62), mat_carton),
    (1, 0.60, 0.0, (0.90, 0.75, 0.40), mat_carton2),
    (1, 1.70, -0.05, (0.85, 0.70, 0.66), mat_carton),
    (2, -1.90, 0.05, (0.80, 0.68, 0.50), mat_carton2),
    (2, -0.95, -0.06, (0.70, 0.62, 0.58), mat_carton),
    (2, 0.35, 0.02, (1.00, 0.80, 0.45), mat_carton),
    (2, 1.60, 0.0, (0.75, 0.66, 0.62), mat_carton2),
]
for n, (lvl, x, y, size, mat) in enumerate(carton_plan):
    z = LEVELS[lvl] + 0.10 + size[2] / 2
    box("Carton_L%d_%d" % (lvl, n), size, (x, y, z), mat,
        rotation=(0, 0, random.uniform(-0.06, 0.06)))

# a couple of drums parked on the floor beside the rack
for n, x in enumerate((-2.3, -1.75)):
    build_barrel("FloorBarrel_%d" % n, (x, 1.55, 0.0), mat_drum, mat_steel)

bpy.ops.mesh.primitive_plane_add(size=20.0, location=(0.0, 0.0, 0.0))
finish(bpy.context.object, "WarehouseFloor", mat_floor)

bpy.ops.object.light_add(type='AREA', location=(-2.0, -4.0, 6.0))
key = bpy.context.object
key.name = "KeyLight"
key.data.energy = 2500.0
key.data.size = 5.0
key.rotation_euler = (Vector((0, 0, 1.5)) - key.location).to_track_quat('-Z', 'Y').to_euler()

bpy.ops.object.light_add(type='SUN', location=(4.0, 3.0, 8.0))
sun = bpy.context.object
sun.name = "FillSun"
sun.data.energy = 1.5
sun.rotation_euler = (math.radians(50), 0.0, math.radians(35))

add_camera((5.4, -6.6, 3.6), (0.0, 0.0, 1.45))
