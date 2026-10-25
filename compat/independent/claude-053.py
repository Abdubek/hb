import bpy
import math
from mathutils import Vector

# ---------------------------------------------------------------- utilities

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
    bsdf = mat.node_tree.nodes.get("Principled BSDF")
    if bsdf:
        bsdf.inputs["Base Color"].default_value = (color[0], color[1], color[2], 1.0)
        bsdf.inputs["Roughness"].default_value = roughness
        bsdf.inputs["Metallic"].default_value = metallic
    return mat


def finish(obj, name, material, parent=None, smooth=False):
    obj.name = name
    obj.data.name = name + "_mesh"
    obj.data.materials.append(material)
    if smooth:
        for poly in obj.data.polygons:
            poly.use_smooth = True
    if parent is not None:
        obj.parent = parent
    return obj


def add_box(name, size, location, material, rotation=(0, 0, 0), parent=None):
    """size is the full x/y/z extent."""
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=location, rotation=rotation)
    obj = bpy.context.active_object
    obj.scale = size
    return finish(obj, name, material, parent)


def add_cyl(name, radius, depth, location, material, rotation=(0, 0, 0), verts=32,
            parent=None):
    bpy.ops.mesh.primitive_cylinder_add(vertices=verts, radius=radius, depth=depth,
                                        location=location, rotation=rotation)
    return finish(bpy.context.active_object, name, material, parent, smooth=True)


def new_group(name, parent=None):
    empty = bpy.data.objects.new(name, None)
    bpy.context.collection.objects.link(empty)
    empty.parent = parent
    return empty


# ---------------------------------------------------------------- setup

clear_scene()

floor_mat = make_material("MAT_Floor", (0.55, 0.56, 0.54), roughness=0.75)
wall_mat = make_material("MAT_Wall", (0.86, 0.87, 0.85), roughness=0.85)
cab_mat = make_material("MAT_CabinetWhite", (0.82, 0.83, 0.84), roughness=0.45)
door_mat = make_material("MAT_DoorGrey", (0.62, 0.65, 0.68), roughness=0.4)
top_mat = make_material("MAT_BlackEpoxyTop", (0.09, 0.09, 0.10), roughness=0.35)
steel_mat = make_material("MAT_Steel", (0.75, 0.77, 0.79), roughness=0.28, metallic=0.9)
glass_mat = make_material("MAT_ReagentGlass", (0.70, 0.85, 0.80), roughness=0.15)
screen_mat = make_material("MAT_Screen", (0.05, 0.09, 0.14), roughness=0.18)
accent_mat = make_material("MAT_Accent", (0.18, 0.42, 0.62), roughness=0.5)

BENCH_W, BENCH_D = 3.20, 0.72
TOP_Z = 0.90

root = new_group("LabWorkstation")

bpy.ops.mesh.primitive_plane_add(size=12.0, location=(0, 0, 0))
finish(bpy.context.active_object, "Floor", floor_mat)
add_box("BackWall", (8.0, 0.10, 3.0), (0, 0.55, 1.5), wall_mat)

# ---------------------------------------------------------------- bench + cabinets

bench = new_group("BenchUnit", root)
add_box("BenchTop", (BENCH_W, BENCH_D, 0.06), (0, 0.16, TOP_Z), top_mat, parent=bench)
add_box("BenchBacksplash", (BENCH_W, 0.05, 0.16), (0, 0.50, TOP_Z + 0.08), top_mat,
        parent=bench)
add_box("CabinetCarcass", (BENCH_W - 0.06, BENCH_D - 0.10, TOP_Z - 0.15),
        (0, 0.16, (TOP_Z - 0.15) / 2 + 0.12), cab_mat, parent=bench)
add_box("BenchToeKick", (BENCH_W - 0.20, BENCH_D - 0.22, 0.12), (0, 0.20, 0.06),
        door_mat, parent=bench)


def add_handle(name, location, parent):
    add_cyl(name, 0.012, 0.20, location, steel_mat, rotation=(0, math.pi / 2, 0),
            verts=10, parent=parent)


# left module: two hinged doors
for i, x in enumerate((-1.28, -0.68)):
    add_box("CabinetDoor_%02d" % (i + 1), (0.56, 0.03, 0.66), (x, -0.20, 0.48),
            door_mat, parent=bench)
    add_handle("DoorHandle_%02d" % (i + 1), (x + (0.22 if i == 0 else -0.22), -0.23, 0.48),
               bench)

# centre module: drawer stack
for i in range(3):
    z = 0.24 + i * 0.24
    add_box("DrawerFront_%02d" % (i + 1), (0.62, 0.03, 0.21), (-0.05, -0.20, z),
            door_mat, parent=bench)
    add_handle("DrawerHandle_%02d" % (i + 1), (-0.05, -0.23, z), bench)

# right module: open shelf bay with a stored tray
add_box("ShelfBaySide_L", (0.03, BENCH_D - 0.12, 0.66), (0.34, 0.16, 0.48), cab_mat,
        parent=bench)
add_box("ShelfBayBoard", (1.16, BENCH_D - 0.14, 0.03), (0.94, 0.16, 0.46), cab_mat,
        parent=bench)
add_box("StorageTray", (0.44, 0.32, 0.10), (0.80, 0.14, 0.52), accent_mat, parent=bench)

# ---------------------------------------------------------------- sink + faucet

sink = new_group("SinkStation", root)
add_box("SinkRim", (0.46, 0.40, 0.03), (1.22, 0.16, TOP_Z + 0.02), steel_mat, parent=sink)
add_box("SinkBasin", (0.40, 0.34, 0.16), (1.22, 0.16, TOP_Z - 0.06), steel_mat, parent=sink)
add_cyl("FaucetColumn", 0.018, 0.34, (1.22, 0.42, TOP_Z + 0.20), steel_mat, verts=14,
        parent=sink)
add_cyl("FaucetSpout", 0.015, 0.26, (1.22, 0.30, TOP_Z + 0.35), steel_mat,
        rotation=(math.pi / 2, 0, 0), verts=14, parent=sink)
add_cyl("FaucetValve", 0.030, 0.06, (1.05, 0.42, TOP_Z + 0.10), accent_mat,
        rotation=(math.pi / 2, 0, 0), verts=12, parent=sink)

# ---------------------------------------------------------------- instruments

instr = new_group("Instruments", root)

# compound microscope
micro = new_group("Microscope", instr)
MX, MY = -1.10, 0.10
add_box("MicroscopeBase", (0.26, 0.34, 0.07), (MX, MY, TOP_Z + 0.07), door_mat, parent=micro)
add_box("MicroscopeArm", (0.09, 0.10, 0.34), (MX, MY + 0.11, TOP_Z + 0.27), door_mat,
        parent=micro)
add_box("MicroscopeStage", (0.22, 0.20, 0.02), (MX, MY - 0.02, TOP_Z + 0.21), steel_mat,
        parent=micro)
add_cyl("ObjectiveTurret", 0.045, 0.05, (MX, MY - 0.01, TOP_Z + 0.29), steel_mat, verts=16,
        parent=micro)
add_cyl("MicroscopeTube", 0.032, 0.24, (MX, MY + 0.02, TOP_Z + 0.46), steel_mat,
        rotation=(math.radians(-22), 0, 0), verts=16, parent=micro)
add_cyl("Eyepiece", 0.024, 0.08, (MX, MY - 0.06, TOP_Z + 0.58), door_mat,
        rotation=(math.radians(-22), 0, 0), verts=14, parent=micro)
add_cyl("FocusKnob", 0.030, 0.06, (MX + 0.08, MY + 0.11, TOP_Z + 0.20), accent_mat,
        rotation=(0, math.pi / 2, 0), verts=14, parent=micro)

# benchtop centrifuge
cent = new_group("Centrifuge", instr)
add_cyl("CentrifugeBody", 0.17, 0.20, (-0.45, 0.18, TOP_Z + 0.13), cab_mat, parent=cent)
add_cyl("CentrifugeLid", 0.17, 0.04, (-0.45, 0.18, TOP_Z + 0.25), accent_mat, parent=cent)
add_box("CentrifugePanel", (0.10, 0.02, 0.05), (-0.45, 0.02, TOP_Z + 0.16), screen_mat,
        parent=cent)

# analytical balance
bal = new_group("AnalyticalBalance", instr)
add_box("BalanceBody", (0.28, 0.26, 0.09), (0.10, 0.22, TOP_Z + 0.08), cab_mat, parent=bal)
add_cyl("BalancePan", 0.075, 0.01, (0.10, 0.18, TOP_Z + 0.13), steel_mat, parent=bal)
add_box("BalanceDisplay", (0.14, 0.02, 0.05), (0.10, 0.08, TOP_Z + 0.10), screen_mat,
        parent=bal)

# data monitor on a small stand
mon = new_group("DataMonitor", instr)
add_cyl("MonitorFoot", 0.10, 0.02, (0.62, 0.40, TOP_Z + 0.04), door_mat, parent=mon)
add_cyl("MonitorNeck", 0.022, 0.22, (0.62, 0.40, TOP_Z + 0.14), door_mat, verts=14,
        parent=mon)
add_box("MonitorShell", (0.52, 0.03, 0.32), (0.62, 0.40, TOP_Z + 0.40), door_mat,
        rotation=(math.radians(-8), 0, 0), parent=mon)
add_box("MonitorScreen", (0.48, 0.01, 0.28), (0.62, 0.375, TOP_Z + 0.40), screen_mat,
        rotation=(math.radians(-8), 0, 0), parent=mon)

# glassware set
glass = new_group("Glassware", instr)
for i, (x, r, h) in enumerate(((-0.85, 0.05, 0.16), (-0.74, 0.04, 0.12),
                               (-0.65, 0.035, 0.20))):
    add_cyl("Beaker_%02d" % (i + 1), r, h, (x, -0.05, TOP_Z + 0.03 + h / 2), glass_mat,
            verts=20, parent=glass)

# ---------------------------------------------------------------- wall shelf

shelf = new_group("WallShelf", root)
add_box("ShelfBoard", (2.40, 0.30, 0.04), (-0.20, 0.36, 1.72), cab_mat, parent=shelf)
for i, x in enumerate((-1.25, 0.85)):
    add_box("ShelfBracket_%02d" % (i + 1), (0.04, 0.24, 0.16), (x, 0.40, 1.62), door_mat,
            parent=shelf)
for i in range(6):
    x = -1.05 + i * 0.32
    h = 0.16 + (i % 3) * 0.05
    add_cyl("ReagentBottle_%02d" % (i + 1), 0.048, h, (x, 0.36, 1.74 + h / 2), glass_mat,
            verts=18, parent=shelf)
    add_cyl("BottleCap_%02d" % (i + 1), 0.026, 0.03, (x, 0.36, 1.74 + h + 0.015),
            accent_mat, verts=12, parent=shelf)

# ---------------------------------------------------------------- lab stool

stool = new_group("LabStool", root)
add_cyl("StoolBase", 0.24, 0.03, (0.05, -0.85, 0.02), door_mat, parent=stool)
add_cyl("StoolColumn", 0.032, 0.58, (0.05, -0.85, 0.31), steel_mat, verts=16, parent=stool)
add_cyl("StoolSeat", 0.19, 0.07, (0.05, -0.85, 0.63), accent_mat, parent=stool)

# ---------------------------------------------------------------- camera + lights

bpy.ops.object.camera_add(location=(2.9, -3.4, 2.05))
cam = bpy.context.active_object
cam.name = "SceneCamera"
cam.data.lens = 40.0
target = Vector((-0.05, 0.10, 1.05))
cam.rotation_euler = (target - cam.location).to_track_quat('-Z', 'Y').to_euler()
bpy.context.scene.camera = cam

bpy.ops.object.light_add(type='AREA', location=(0.4, -1.4, 2.85))
key = bpy.context.active_object
key.name = "KeyLight"
key.data.energy = 320.0
key.data.size = 2.4
key.rotation_euler = (Vector((0, 0.1, 1.0)) - key.location).to_track_quat('-Z', 'Y').to_euler()

bpy.ops.object.light_add(type='AREA', location=(-2.6, -2.2, 1.9))
fill = bpy.context.active_object
fill.name = "FillLight"
fill.data.energy = 90.0
fill.data.size = 2.0
fill.rotation_euler = (Vector((0, 0.1, 1.0)) - fill.location).to_track_quat('-Z', 'Y').to_euler()

print("Laboratory workstation built: %d objects" % len(bpy.context.scene.objects))
