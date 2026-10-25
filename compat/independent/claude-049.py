import bpy
import math
from mathutils import Vector, Matrix


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
    bsdf = mat.node_tree.nodes["Principled BSDF"]
    bsdf.inputs["Base Color"].default_value = (*color, 1.0)
    bsdf.inputs["Roughness"].default_value = roughness
    bsdf.inputs["Metallic"].default_value = metallic
    return mat


def add_box(name, size, location, material, rotation=(0, 0, 0)):
    bpy.ops.mesh.primitive_cube_add(size=2, location=location, rotation=rotation)
    obj = bpy.context.object
    obj.name = name
    obj.scale = (size[0] / 2.0, size[1] / 2.0, size[2] / 2.0)
    obj.data.materials.append(material)
    return obj


clear_scene()

TILT = math.radians(32.0)
ROT = Matrix.Rotation(TILT, 3, 'X')
ARRAY_ORIGIN = Vector((0.0, 0.0, 1.15))

ground_mat = make_material("Ground", (0.34, 0.36, 0.28), 0.95)
glass_mat = make_material("PVGlass", (0.03, 0.05, 0.16), 0.12)
cell_mat = make_material("PVCell", (0.05, 0.09, 0.26), 0.25)
frame_mat = make_material("AnodizedAluminium", (0.74, 0.75, 0.78), 0.32, metallic=1.0)
steel_mat = make_material("GalvSteel", (0.55, 0.56, 0.58), 0.45, metallic=1.0)
concrete_mat = make_material("Footing", (0.66, 0.65, 0.62), 0.88)
box_mat = make_material("Enclosure", (0.82, 0.82, 0.80), 0.50)


def tilted(name, size, local_loc, material):
    """Place a box inside the tilted plane of the array."""
    world = ARRAY_ORIGIN + ROT @ Vector(local_loc)
    return add_box(name, size, world, material, rotation=(TILT, 0, 0))


add_box("GroundPlane", (18.0, 18.0, 0.3), (0, 0, -0.15), ground_mat)

# Panel grid: columns across X, rows running up the slope in local Y
PANEL_W, PANEL_H, PANEL_T = 1.62, 0.99, 0.035
GAP = 0.04
COLS, ROWS = 4, 2

for c in range(COLS):
    lx = (c - (COLS - 1) / 2.0) * (PANEL_W + GAP)
    for r in range(ROWS):
        ly = (r - (ROWS - 1) / 2.0) * (PANEL_H + GAP)
        tag = "%d_%d" % (c, r)
        tilted("PanelFrame_" + tag, (PANEL_W, PANEL_H, PANEL_T), (lx, ly, 0.0), frame_mat)
        tilted("PanelGlass_" + tag, (PANEL_W - 0.06, PANEL_H - 0.06, 0.012),
               (lx, ly, PANEL_T / 2.0), glass_mat)
        for s in range(3):
            oy = (s - 1) * (PANEL_H - 0.14) / 3.0
            tilted("PanelCells_%s_%d" % (tag, s),
                   (PANEL_W - 0.12, (PANEL_H - 0.20) / 3.4, 0.008),
                   (lx, ly + oy, PANEL_T / 2.0 - 0.002), cell_mat)
        tilted("JunctionBox_" + tag, (0.22, 0.14, 0.06),
               (lx, ly, -PANEL_T / 2.0 - 0.03), box_mat)

array_w = COLS * PANEL_W + (COLS - 1) * GAP
array_h = ROWS * PANEL_H + (ROWS - 1) * GAP

# Mounting rails across the back of the array
for i, ly in enumerate((-array_h * 0.28, array_h * 0.28)):
    tilted("MountRail_%d" % i, (array_w + 0.25, 0.09, 0.09),
           (0.0, ly, -PANEL_T / 2.0 - 0.055), frame_mat)

# Purlins running up the slope, tying the rails together
for i in range(3):
    lx = (i - 1) * array_w / 2.6
    tilted("Purlin_%d" % i, (0.07, array_h + 0.1, 0.07),
           (lx, 0.0, -PANEL_T / 2.0 - 0.14), steel_mat)

# Legs, footings and diagonal bracing
low_edge = ARRAY_ORIGIN + ROT @ Vector((0.0, -array_h / 2.0, 0.0))
high_edge = ARRAY_ORIGIN + ROT @ Vector((0.0, array_h / 2.0, 0.0))
leg_xs = (-array_w / 2.0 + 0.35, array_w / 2.0 - 0.35)

for i, lx in enumerate(leg_xs):
    for tag, edge in (("Front", low_edge), ("Rear", high_edge)):
        height = max(edge.z - 0.20, 0.3)
        add_box("Leg%s_%d" % (tag, i), (0.13, 0.13, height),
                (lx, edge.y, height / 2.0), steel_mat)
        add_box("Footing%s_%d" % (tag, i), (0.50, 0.50, 0.24),
                (lx, edge.y, 0.12), concrete_mat)
    span = Vector((0.0, high_edge.y - low_edge.y, (high_edge.z - 0.5) - 0.30))
    mid = Vector((lx, (low_edge.y + high_edge.y) / 2.0,
                  (0.30 + high_edge.z - 0.5) / 2.0))
    add_box("Brace_%d" % i, (0.08, span.length, 0.08), mid, steel_mat,
            rotation=(math.atan2(span.z, span.y), 0, 0))

add_box("CrossTie", (array_w - 0.5, 0.09, 0.09),
        (0.0, high_edge.y, high_edge.z * 0.45), steel_mat)

# Inverter cabinet beside the array
inv_x = array_w / 2.0 + 1.6
add_box("InverterPad", (1.2, 0.9, 0.12), (inv_x, 0.0, 0.06), concrete_mat)
add_box("InverterCabinet", (0.85, 0.45, 1.25), (inv_x, 0.0, 0.74), box_mat)
add_box("InverterVent", (0.60, 0.04, 0.35), (inv_x, -0.24, 0.95), steel_mat)
add_box("InverterConduit", (0.10, 0.10, 0.55), (inv_x, 0.24, 0.30), steel_mat)

# Sun and sky
sun_data = bpy.data.lights.new("Sun", type='SUN')
sun_data.energy = 5.0
sun = bpy.data.objects.new("Sun", sun_data)
sun.location = (6, -8, 10)
sun.rotation_euler = (math.radians(48), 0, math.radians(25))
bpy.context.collection.objects.link(sun)

world = bpy.context.scene.world
if world is None:
    world = bpy.data.worlds.new("World")
    bpy.context.scene.world = world
world.use_nodes = True
world.node_tree.nodes["Background"].inputs[0].default_value = (0.35, 0.5, 0.75, 1.0)

# Camera
cam_data = bpy.data.cameras.new("Camera")
cam_data.lens = 42
cam = bpy.data.objects.new("Camera", cam_data)
cam.location = (6.5, -8.5, 4.6)
target = Vector((0.0, 0.0, 1.3))
cam.rotation_euler = (target - cam.location).to_track_quat('-Z', 'Y').to_euler()
bpy.context.collection.objects.link(cam)
bpy.context.scene.camera = cam
