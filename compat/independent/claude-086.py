import bpy
import math
from mathutils import Vector

CASE_R = 0.021
CASE_H = 0.011
WRIST_R = 0.030


def clear_scene():
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete(use_global=False)
    for coll in (bpy.data.meshes, bpy.data.materials):
        for item in list(coll):
            if item.users == 0:
                coll.remove(item)


def make_material(name, color, **sockets):
    mat = bpy.data.materials.new(name)
    mat.use_nodes = True
    bsdf = mat.node_tree.nodes.get("Principled BSDF")
    bsdf.inputs["Base Color"].default_value = (color[0], color[1], color[2], 1.0)
    for key, value in sockets.items():
        socket = bsdf.inputs.get(key.replace("_", " "))
        if socket is not None:
            socket.default_value = value
    return mat


def finish(obj, name, mat, parent=None):
    obj.name = name
    obj.data.name = name
    obj.data.materials.append(mat)
    if parent is not None:
        obj.parent = parent
    return obj


def disc(name, radius, depth, z, mat, parent, verts=64):
    bpy.ops.mesh.primitive_cylinder_add(vertices=verts, radius=radius, depth=depth,
                                        location=(0.0, 0.0, z))
    return finish(bpy.context.active_object, name, mat, parent)


def box(name, half, location, rotation, mat, parent):
    bpy.ops.mesh.primitive_cube_add(size=2.0, location=location, rotation=rotation)
    obj = bpy.context.active_object
    obj.scale = half
    return finish(obj, name, mat, parent)


def hand(name, length, width, thickness, angle_deg, z, mat, parent):
    """Angle measured clockwise from the 12 o'clock direction (+Y)."""
    a = math.radians(angle_deg)
    direction = Vector((math.sin(a), math.cos(a), 0.0))
    centre = direction * (length * 0.5 - length * 0.12)
    return box(name, (width, length * 0.5, thickness),
               (centre.x, centre.y, z), (0.0, 0.0, -a), mat, parent)


clear_scene()

steel = make_material("MAT_Steel", (0.72, 0.73, 0.75), Metallic=1.0, Roughness=0.24)
dark_steel = make_material("MAT_SteelDark", (0.34, 0.35, 0.37), Metallic=1.0, Roughness=0.42)
dial_mat = make_material("MAT_DialNavy", (0.05, 0.08, 0.18), Roughness=0.32)
lume = make_material("MAT_Lume", (0.88, 0.92, 0.80), Roughness=0.35)
accent = make_material("MAT_HandOrange", (0.85, 0.28, 0.05), Roughness=0.40)
glass = make_material("MAT_Crystal", (1.0, 1.0, 1.0), Roughness=0.03, Transmission_Weight=1.0, IOR=1.52)
leather = make_material("MAT_StrapLeather", (0.16, 0.10, 0.07), Roughness=0.62)
bench = make_material("MAT_Bench", (0.30, 0.29, 0.27), Roughness=0.85)

bpy.ops.object.empty_add(type='PLAIN_AXES', location=(0.0, 0.0, 0.0))
root = bpy.context.active_object
root.name = "Wristwatch"

# --- case, bezel, dial ---
disc("Case_Body", CASE_R, CASE_H, 0.0, steel, root)
disc("Case_Back", CASE_R * 0.78, 0.003, -CASE_H * 0.5 - 0.0012, dark_steel, root)
bpy.ops.mesh.primitive_torus_add(major_radius=CASE_R - 0.0022, minor_radius=0.0024,
                                 major_segments=64, minor_segments=14,
                                 location=(0.0, 0.0, CASE_H * 0.5))
finish(bpy.context.active_object, "Bezel", dark_steel, root)
dial_z = CASE_H * 0.5 - 0.0028
disc("Dial", CASE_R - 0.0035, 0.0012, dial_z, dial_mat, root)
disc("Crystal", CASE_R - 0.0030, 0.0014, CASE_H * 0.5 - 0.0002, glass, root)

# --- hour markers ---
for i in range(12):
    a = math.radians(i * 30.0)
    r = CASE_R - 0.0062
    box("Marker_%02d" % (i + 1), (0.0009, 0.0022, 0.0004),
        (math.sin(a) * r, math.cos(a) * r, dial_z + 0.0008),
        (0.0, 0.0, -a), lume, root)

# --- hands and crown ---
hand("Hand_Hour", 0.0105, 0.0012, 0.0004, 305.0, dial_z + 0.0016, lume, root)
hand("Hand_Minute", 0.0155, 0.0009, 0.0004, 62.0, dial_z + 0.0022, lume, root)
hand("Hand_Second", 0.0170, 0.0004, 0.0003, 200.0, dial_z + 0.0027, accent, root)
disc("Hand_Cap", 0.0016, 0.0012, dial_z + 0.0032, dark_steel, root, verts=20)

bpy.ops.mesh.primitive_cylinder_add(vertices=18, radius=0.0032, depth=0.0038,
                                    location=(CASE_R + 0.0016, 0.0, 0.0),
                                    rotation=(0.0, math.radians(90.0), 0.0))
finish(bpy.context.active_object, "Crown", steel, root)

# --- lugs ---
for side, tag in ((1.0, "Top"), (-1.0, "Bottom")):
    for x in (-1.0, 1.0):
        box("Lug_%s_%s" % (tag, "L" if x < 0 else "R"), (0.0022, 0.0040, 0.0018),
            (x * 0.0125, side * (CASE_R - 0.0015), -0.0012), (0.0, 0.0, 0.0), steel, root)

# --- segmented strap wrapping around a wrist-sized arc ---
centre = Vector((0.0, 0.0, -WRIST_R - CASE_H * 0.5))
for side in (1.0, -1.0):
    for i in range(10):
        theta = math.radians(18.0 + i * 14.0) * side
        pos = centre + Vector((0.0, math.sin(theta), math.cos(theta))) * (WRIST_R + 0.0018)
        tag = "T" if side > 0 else "B"
        box("Strap_%s_%02d" % (tag, i + 1), (0.0092, 0.0044, 0.0017),
            pos, (-theta, 0.0, 0.0), leather, root)

buckle_theta = math.radians(18.0 + 10 * 14.0)
buckle_pos = centre + Vector((0.0, math.sin(buckle_theta), math.cos(buckle_theta))) * (WRIST_R + 0.0022)
box("Buckle", (0.0100, 0.0060, 0.0011), buckle_pos, (-buckle_theta, 0.0, 0.0), steel, root)

# --- display surface, lights, camera ---
bpy.ops.mesh.primitive_plane_add(size=0.6, location=(0.0, 0.0, -WRIST_R - 0.030))
finish(bpy.context.active_object, "Display_Bench", bench)

bpy.ops.object.light_add(type='AREA', location=(0.10, -0.10, 0.16))
key = bpy.context.active_object
key.name = "Light_Key"
key.data.energy = 60.0
key.data.size = 0.25
key.rotation_euler = (math.radians(45.0), 0.0, math.radians(40.0))

bpy.ops.object.light_add(type='AREA', location=(-0.14, 0.06, 0.10))
fill = bpy.context.active_object
fill.name = "Light_Fill"
fill.data.energy = 18.0
fill.data.size = 0.3
fill.rotation_euler = (math.radians(60.0), 0.0, math.radians(-120.0))

bpy.ops.object.camera_add(location=(0.075, -0.095, 0.070))
cam = bpy.context.active_object
cam.name = "Camera_Product"
cam.data.lens = 70.0
cam.rotation_euler = (Vector((0.0, 0.0, 0.0)) - cam.location).to_track_quat('-Z', 'Y').to_euler()
bpy.context.scene.camera = cam
