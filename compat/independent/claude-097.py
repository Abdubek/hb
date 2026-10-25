"""Two-door refrigerator with an open fresh-food door, shelves, drawers and door bins."""
import bpy
import math
from mathutils import Vector


def reset_scene():
    for ob in list(bpy.data.objects):
        bpy.data.objects.remove(ob, do_unlink=True)
    for coll in (bpy.data.meshes, bpy.data.materials, bpy.data.lights, bpy.data.cameras):
        for item in list(coll):
            coll.remove(item)


def make_material(name, color, roughness=0.45, metallic=0.0, alpha=1.0):
    mat = bpy.data.materials.new(name)
    mat.use_nodes = True
    bsdf = next(n for n in mat.node_tree.nodes if n.type == 'BSDF_PRINCIPLED')
    bsdf.inputs["Base Color"].default_value = (color[0], color[1], color[2], 1.0)
    bsdf.inputs["Roughness"].default_value = roughness
    bsdf.inputs["Metallic"].default_value = metallic
    bsdf.inputs["Alpha"].default_value = alpha
    if alpha < 1.0:
        mat.blend_method = 'BLEND'
    return mat


def box(name, center, size, material):
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=center)
    ob = bpy.context.object
    ob.name = name
    ob.scale = size
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    ob.data.materials.append(material)
    return ob


def cyl(name, center, radius, depth, material, rotation=(0.0, 0.0, 0.0)):
    bpy.ops.mesh.primitive_cylinder_add(vertices=24, radius=radius, depth=depth,
                                        location=center, rotation=rotation)
    ob = bpy.context.object
    ob.name = name
    ob.data.materials.append(material)
    bpy.ops.object.shade_smooth()
    return ob


def aim(ob, target):
    direction = Vector(target) - ob.location
    ob.rotation_euler = direction.to_track_quat('-Z', 'Y').to_euler()


reset_scene()

STEEL = make_material("MAT_BrushedSteel", (0.60, 0.62, 0.64), 0.30, 0.9)
LINER = make_material("MAT_WhiteLiner", (0.90, 0.91, 0.90), 0.55)
GLASS = make_material("MAT_ShelfGlass", (0.72, 0.82, 0.85), 0.10, 0.0, 0.35)
PLASTIC = make_material("MAT_ClearPlastic", (0.78, 0.84, 0.86), 0.25, 0.0, 0.55)
TRIM = make_material("MAT_DarkTrim", (0.08, 0.08, 0.09), 0.4)
FLOOR = make_material("MAT_Floor", (0.48, 0.46, 0.44), 0.75)

HW, HD, H = 0.45, 0.35, 1.90        # half width, half depth, height
T = 0.05                             # wall thickness
SPLIT_LO, SPLIT_HI = 1.20, 1.25      # freezer / fridge divider

box("Floor", (0, 0, -0.01), (6, 6, 0.02), FLOOR)

# --- cabinet shell (open at the front) ------------------------------------
box("Cabinet_Back", (0, HD - T / 2, H / 2), (HW * 2, T, H), STEEL)
box("Cabinet_Side_L", (-HW + T / 2, 0, H / 2), (T, HD * 2, H), STEEL)
box("Cabinet_Side_R", (HW - T / 2, 0, H / 2), (T, HD * 2, H), STEEL)
box("Cabinet_Top", (0, 0, H - T / 2), (HW * 2, HD * 2, T), STEEL)
box("Cabinet_Base", (0, 0, T / 2), (HW * 2, HD * 2, T), TRIM)
box("Divider_Shelf", (0, 0, (SPLIT_LO + SPLIT_HI) / 2), (HW * 2 - 2 * T, HD * 2 - T, SPLIT_HI - SPLIT_LO), LINER)

# interior liner surfaces so the open cavity reads as white plastic
box("Liner_Back", (0, HD - T - 0.006, (T + SPLIT_LO) / 2), (HW * 2 - 2 * T, 0.012, SPLIT_LO - T), LINER)
for sx in (-1, 1):
    box("Liner_Side_%d" % sx, (sx * (HW - T - 0.006), 0.02, (T + SPLIT_LO) / 2),
        (0.012, HD * 2 - T, SPLIT_LO - T), LINER)
box("Liner_Floor", (0, 0.02, T + 0.006), (HW * 2 - 2 * T, HD * 2 - T, 0.012), LINER)

# --- shelves and crisper drawers ------------------------------------------
for i, z in enumerate((0.42, 0.66, 0.90, 1.10), start=1):
    box("Shelf_%d" % i, (0, 0.02, z), (HW * 2 - 2 * T - 0.02, HD * 2 - T - 0.03, 0.014), GLASS)
    box("Shelf_Rail_%d" % i, (0, -HD + 0.06, z + 0.01), (HW * 2 - 2 * T - 0.02, 0.012, 0.03), TRIM)

for i, dx in enumerate((-0.19, 0.19), start=1):
    box("Crisper_Drawer_%d" % i, (dx, 0.03, 0.20), (0.34, HD * 2 - T - 0.06, 0.24), PLASTIC)
    box("Crisper_Handle_%d" % i, (dx, -HD + 0.06, 0.29), (0.20, 0.02, 0.02), TRIM)

# --- freezer door (closed) -------------------------------------------------
box("Freezer_Door", (0, -HD - 0.02, (SPLIT_HI + H) / 2), (HW * 2, 0.04, H - SPLIT_HI), STEEL)
cyl("Freezer_Handle", (0, -HD - 0.10, H - 0.14), 0.016, HW * 1.5, STEEL,
    rotation=(0, math.radians(90), 0))
for sx in (-1, 1):
    box("Freezer_Handle_Post_%d" % sx, (sx * HW * 0.72, -HD - 0.065, H - 0.14), (0.02, 0.09, 0.02), STEEL)

# --- fresh-food door, swung open on a hinge empty --------------------------
hinge = bpy.data.objects.new("Door_Hinge", None)
hinge.empty_display_size = 0.12
hinge.location = (HW, -HD, 0.0)
bpy.context.collection.objects.link(hinge)

door_parts = []
door_parts.append(box("Fridge_Door_Panel", (0, -HD - 0.02, (T + SPLIT_LO) / 2),
                      (HW * 2, 0.04, SPLIT_LO - T), STEEL))
door_parts.append(box("Fridge_Door_Liner", (0, -HD + 0.005, (T + SPLIT_LO) / 2),
                      (HW * 2 - 0.04, 0.012, SPLIT_LO - T - 0.03), LINER))
for i, z in enumerate((0.32, 0.62, 0.92), start=1):
    door_parts.append(box("Door_Bin_%d" % i, (0, -HD + 0.06, z), (HW * 1.8, 0.10, 0.14), PLASTIC))
    door_parts.append(box("Door_Bin_Lip_%d" % i, (0, -HD + 0.11, z + 0.06), (HW * 1.8, 0.012, 0.03), PLASTIC))
door_parts.append(cyl("Fridge_Handle", (-HW * 0.72, -HD - 0.10, 0.70), 0.016, 0.70, STEEL,
                      rotation=(math.radians(90), 0, 0)))
for dz in (0.36, 1.04):
    door_parts.append(box("Fridge_Handle_Post_%d" % int(dz * 100),
                          (-HW * 0.72, -HD - 0.065, dz), (0.02, 0.09, 0.02), STEEL))

for part in door_parts:
    part.parent = hinge
    part.matrix_parent_inverse = hinge.matrix_world.inverted()
hinge.rotation_euler = (0, 0, math.radians(112))

# --- lights and camera -----------------------------------------------------
key = bpy.data.lights.new("KeyLight", 'AREA')
key.energy, key.size = 500.0, 2.5
key_ob = bpy.data.objects.new("Key_Light", key)
key_ob.location = (-2.2, -2.4, 3.0)
bpy.context.collection.objects.link(key_ob)
aim(key_ob, (0, 0, 1.0))

inner = bpy.data.lights.new("CabinetLight", 'POINT')
inner.energy, inner.shadow_soft_size = 45.0, 0.08
inner_ob = bpy.data.objects.new("Cabinet_Light", inner)
inner_ob.location = (0, 0.1, 1.12)
bpy.context.collection.objects.link(inner_ob)

sun = bpy.data.lights.new("SunFill", 'SUN')
sun.energy = 1.4
sun_ob = bpy.data.objects.new("Fill_Light", sun)
sun_ob.location = (2.5, -2.0, 3.5)
bpy.context.collection.objects.link(sun_ob)
aim(sun_ob, (0, 0, 0.9))

cam_data = bpy.data.cameras.new("FridgeCam")
cam_data.lens = 42.0
cam = bpy.data.objects.new("Camera", cam_data)
cam.location = (-1.9, -2.5, 2.05)
bpy.context.collection.objects.link(cam)
aim(cam, (0.0, -0.05, 1.00))
bpy.context.scene.camera = cam
