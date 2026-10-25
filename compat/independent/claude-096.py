"""Freestanding kitchen range: cooktop with burners, control panel with knobs, oven door."""
import bpy
import math
from mathutils import Vector


def reset_scene():
    for ob in list(bpy.data.objects):
        bpy.data.objects.remove(ob, do_unlink=True)
    for coll in (bpy.data.meshes, bpy.data.materials, bpy.data.lights, bpy.data.cameras):
        for item in list(coll):
            coll.remove(item)


def make_material(name, color, roughness=0.45, metallic=0.0):
    mat = bpy.data.materials.new(name)
    mat.use_nodes = True
    bsdf = next(n for n in mat.node_tree.nodes if n.type == 'BSDF_PRINCIPLED')
    bsdf.inputs["Base Color"].default_value = (color[0], color[1], color[2], 1.0)
    bsdf.inputs["Roughness"].default_value = roughness
    bsdf.inputs["Metallic"].default_value = metallic
    return mat


def box(name, center, size, material):
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=center)
    ob = bpy.context.object
    ob.name = name
    ob.scale = size
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    ob.data.materials.append(material)
    return ob


def cyl(name, center, radius, depth, material, rotation=(0.0, 0.0, 0.0), verts=28):
    bpy.ops.mesh.primitive_cylinder_add(vertices=verts, radius=radius, depth=depth,
                                       location=center, rotation=rotation)
    ob = bpy.context.object
    ob.name = name
    ob.data.materials.append(material)
    bpy.ops.object.shade_smooth()
    return ob


def ring(name, center, major, minor, material):
    bpy.ops.mesh.primitive_torus_add(location=center, major_radius=major, minor_radius=minor,
                                     major_segments=32, minor_segments=10)
    ob = bpy.context.object
    ob.name = name
    ob.data.materials.append(material)
    bpy.ops.object.shade_smooth()
    return ob


def aim(ob, target):
    direction = Vector(target) - ob.location
    ob.rotation_euler = direction.to_track_quat('-Z', 'Y').to_euler()


reset_scene()

STEEL = make_material("MAT_Stainless", (0.62, 0.63, 0.65), 0.28, 0.9)
DARK = make_material("MAT_DarkEnamel", (0.05, 0.05, 0.06), 0.35)
GLASS = make_material("MAT_OvenGlass", (0.02, 0.03, 0.04), 0.12)
CAST = make_material("MAT_CastIron", (0.09, 0.09, 0.10), 0.65)
CHROME = make_material("MAT_Chrome", (0.80, 0.81, 0.83), 0.15, 1.0)
FLOOR = make_material("MAT_Floor", (0.55, 0.50, 0.45), 0.7)

W, D = 0.76, 0.65          # range width / depth
BODY_BOTTOM, TOP = 0.06, 0.90

box("Floor", (0, 0, -0.01), (6, 6, 0.02), FLOOR)
box("Range_Body", (0, 0, (BODY_BOTTOM + TOP) * 0.5), (W, D, TOP - BODY_BOTTOM), STEEL)
box("Cooktop_Plate", (0, 0, TOP + 0.008), (W - 0.01, D - 0.01, 0.016), DARK)

for sx in (-1, 1):
    for sy in (-1, 1):
        cyl("Leg_%d%d" % (sx, sy), (sx * (W / 2 - 0.06), sy * (D / 2 - 0.06), 0.03),
            0.02, 0.06, DARK, verts=12)

# --- cooktop burners -------------------------------------------------------
burners = [(-0.19, 0.16, 0.085), (0.19, 0.16, 0.085), (-0.19, -0.14, 0.070), (0.19, -0.14, 0.070)]
for i, (bx, by, r) in enumerate(burners, start=1):
    z = TOP + 0.02
    ring("Burner_Ring_%d" % i, (bx, by, z), r, 0.012, CAST)
    cyl("Burner_Cap_%d" % i, (bx, by, z + 0.012), r * 0.42, 0.022, CAST, verts=20)
    for a in range(3):
        ang = math.radians(60 * a)
        box("Grate_Bar_%d_%d" % (i, a), (bx, by, z + 0.028),
            (r * 2.3, 0.014, 0.012), CAST).rotation_euler = (0, 0, ang)

# --- back control panel with knobs ----------------------------------------
box("Backguard", (0, D / 2 - 0.04, TOP + 0.14), (W, 0.08, 0.28), STEEL)
box("Control_Panel", (0, D / 2 - 0.085, TOP + 0.14), (W - 0.06, 0.01, 0.20), DARK)
knob_y = D / 2 - 0.10
for i, kx in enumerate((-0.26, -0.09, 0.09, 0.26), start=1):
    cyl("Knob_%d" % i, (kx, knob_y - 0.02, TOP + 0.14), 0.032, 0.045, CHROME,
        rotation=(math.radians(90), 0, 0))
    box("Knob_Marker_%d" % i, (kx, knob_y - 0.043, TOP + 0.155), (0.006, 0.004, 0.026), DARK)

# --- oven door -------------------------------------------------------------
front = -D / 2
box("Oven_Door", (0, front - 0.02, 0.44), (W - 0.02, 0.04, 0.62), STEEL)
box("Oven_Window", (0, front - 0.043, 0.46), (W - 0.20, 0.012, 0.40), GLASS)
cyl("Oven_Handle", (0, front - 0.09, 0.80), 0.016, W - 0.12, CHROME,
    rotation=(0, math.radians(90), 0))
for sx in (-1, 1):
    box("Handle_Post_%d" % sx, (sx * (W / 2 - 0.07), front - 0.06, 0.80), (0.02, 0.09, 0.02), CHROME)
box("Bottom_Drawer", (0, front - 0.015, 0.16), (W - 0.02, 0.03, 0.14), STEEL)

# --- lights and camera -----------------------------------------------------
key = bpy.data.lights.new("KeyLight", 'AREA')
key.energy, key.size = 320.0, 2.2
key_ob = bpy.data.objects.new("Key_Light", key)
key_ob.location = (-1.6, -2.0, 2.6)
bpy.context.collection.objects.link(key_ob)
aim(key_ob, (0, 0, 0.7))

fill = bpy.data.lights.new("FillLight", 'SUN')
fill.energy = 1.6
fill_ob = bpy.data.objects.new("Fill_Light", fill)
fill_ob.location = (2.4, -1.4, 3.0)
bpy.context.collection.objects.link(fill_ob)
aim(fill_ob, (0, 0, 0.5))

cam_data = bpy.data.cameras.new("RangeCam")
cam_data.lens = 50.0
cam = bpy.data.objects.new("Camera", cam_data)
cam.location = (1.35, -1.85, 1.35)
bpy.context.collection.objects.link(cam)
aim(cam, (0, 0, 0.62))
bpy.context.scene.camera = cam
