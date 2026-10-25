import bpy
from math import radians, cos, sin, pi
from mathutils import Vector


def clear_scene():
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete(use_global=False)
    for mesh in list(bpy.data.meshes):
        if mesh.users == 0:
            bpy.data.meshes.remove(mesh)


def make_material(name, color, roughness=0.5, metallic=0.0):
    mat = bpy.data.materials.new(name)
    mat.use_nodes = True
    bsdf = next(n for n in mat.node_tree.nodes if n.type == 'BSDF_PRINCIPLED')
    bsdf.inputs["Base Color"].default_value = (color[0], color[1], color[2], 1.0)
    bsdf.inputs["Roughness"].default_value = roughness
    bsdf.inputs["Metallic"].default_value = metallic
    return mat


def smooth(obj):
    try:
        bpy.ops.object.shade_auto_smooth(angle=radians(35))
    except Exception:
        bpy.ops.object.shade_smooth()
    return obj


def add_tube(name, p0, p1, radius, mat, verts=20):
    """Cylinder spanning two points, oriented with to_track_quat."""
    a, b = Vector(p0), Vector(p1)
    vec = b - a
    bpy.ops.mesh.primitive_cylinder_add(vertices=verts, radius=radius,
                                        depth=vec.length, location=(a + b) * 0.5)
    obj = bpy.context.active_object
    obj.name = name
    obj.rotation_mode = 'QUATERNION'
    obj.rotation_quaternion = vec.to_track_quat('Z', 'Y')
    obj.data.materials.append(mat)
    return smooth(obj)


def add_box(name, size, location, mat, bevel=0.0):
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=location)
    obj = bpy.context.active_object
    obj.name = name
    obj.scale = Vector(size)
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    obj.data.materials.append(mat)
    if bevel > 0.0:
        mod = obj.modifiers.new("Bevel", 'BEVEL')
        mod.width = bevel
        mod.segments = 3
        mod.limit_method = 'ANGLE'
    return obj


def add_sphere(name, radius, location, mat, segments=24, rings=12):
    bpy.ops.mesh.primitive_uv_sphere_add(segments=segments, ring_count=rings,
                                         radius=radius, location=location)
    obj = bpy.context.active_object
    obj.name = name
    obj.data.materials.append(mat)
    return smooth(obj)


clear_scene()

black_mat = make_material("Anodized_Black", (0.03, 0.03, 0.035), roughness=0.4, metallic=0.6)
alu_mat = make_material("Aluminium", (0.68, 0.69, 0.71), roughness=0.28, metallic=1.0)
rubber_mat = make_material("Rubber", (0.02, 0.02, 0.02), roughness=0.88)
red_mat = make_material("Lock_Red", (0.55, 0.06, 0.05), roughness=0.45)

HUB_Z = 1.00
HUB_R = 0.055
FOOT_R = 0.52          # spread radius of the feet
FOOT_Z = 0.028

# --- shoulder / spider --------------------------------------------------
bpy.ops.mesh.primitive_cylinder_add(vertices=6, radius=HUB_R, depth=0.07, location=(0, 0, HUB_Z))
hub = bpy.context.active_object
hub.name = "Spider_Hub"
hub.data.materials.append(black_mat)

# --- three spread legs, each in two telescoping stages ------------------
for i in range(3):
    ang = radians(90.0) + i * 2.0 * pi / 3.0
    top = Vector((HUB_R * 0.85 * cos(ang), HUB_R * 0.85 * sin(ang), HUB_Z + 0.02))
    foot = Vector((FOOT_R * cos(ang), FOOT_R * sin(ang), FOOT_Z))
    vec = foot - top
    mid = top + vec * 0.55

    add_tube("Leg%d_Upper" % i, top, mid, 0.024, black_mat)
    add_tube("Leg%d_Lower" % i, mid - vec * 0.03, foot, 0.016, alu_mat)

    # twist-lock collar at the joint
    collar = add_tube("Leg%d_Lock" % i, mid - vec * 0.06, mid + vec * 0.02, 0.029, red_mat, verts=16)
    collar.name = "Leg%d_Lock" % i

    # rubber foot
    add_tube("Leg%d_Foot" % i, foot, foot + vec.normalized() * 0.035, 0.026, rubber_mat, verts=16)

    # brace from the centre post down to the leg
    brace_end = top + vec * 0.35
    add_tube("Leg%d_Brace" % i, (0, 0, HUB_Z - 0.10), brace_end, 0.008, alu_mat, verts=12)

# lower brace collar on the centre post
bpy.ops.mesh.primitive_cylinder_add(vertices=20, radius=0.032, depth=0.05, location=(0, 0, HUB_Z - 0.10))
brace_ring = bpy.context.active_object
brace_ring.name = "Brace_Collar"
brace_ring.data.materials.append(black_mat)
smooth(brace_ring)

# --- central column ----------------------------------------------------
add_tube("Centre_Column", (0, 0, HUB_Z - 0.16), (0, 0, HUB_Z + 0.30), 0.019, alu_mat)
add_tube("Column_Lock", (0, 0, HUB_Z + 0.02), (0, 0, HUB_Z + 0.08), 0.030, red_mat, verts=16)
add_sphere("Column_Hook", 0.018, (0, 0, HUB_Z - 0.185), black_mat, segments=16, rings=8)

# --- ball head and quick-release plate ---------------------------------
HEAD_Z = HUB_Z + 0.30
add_tube("Head_Base", (0, 0, HEAD_Z), (0, 0, HEAD_Z + 0.055), 0.042, black_mat)
add_sphere("Head_Ball", 0.046, (0, 0, HEAD_Z + 0.095), black_mat)
add_tube("Head_Stem", (0, 0, HEAD_Z + 0.09), (0, 0, HEAD_Z + 0.145), 0.020, alu_mat, verts=16)
add_box("QR_Plate", (0.11, 0.085, 0.016), (0, 0, HEAD_Z + 0.153), black_mat, bevel=0.004)
add_box("QR_Lever", (0.05, 0.018, 0.012), (0.075, 0.0, HEAD_Z + 0.150), red_mat, bevel=0.003)
add_tube("Head_Knob", (-0.045, -0.030, HEAD_Z + 0.055),
         (-0.075, -0.050, HEAD_Z + 0.055), 0.016, red_mat, verts=16)

# pan handle angled off the head
handle_root = Vector((0.04, 0.035, HEAD_Z + 0.05))
handle_tip = handle_root + Vector((0.16, 0.14, -0.10))
add_tube("Pan_Handle", handle_root, handle_tip, 0.010, alu_mat, verts=14)
add_tube("Pan_Grip", handle_root + (handle_tip - handle_root) * 0.6, handle_tip, 0.016, rubber_mat, verts=16)

# --- ground, light, camera --------------------------------------------
floor_mat = make_material("Floor", (0.30, 0.30, 0.31), roughness=0.75)
bpy.ops.mesh.primitive_plane_add(size=8.0, location=(0, 0, 0))
floor = bpy.context.active_object
floor.name = "Floor"
floor.data.materials.append(floor_mat)

bpy.ops.object.light_add(type='AREA', location=(1.8, -2.0, 3.0))
key = bpy.context.active_object
key.name = "Key_Light"
key.data.energy = 600.0
key.data.size = 2.5
key.rotation_euler = (Vector((0, 0, 0.9)) - key.location).to_track_quat('-Z', 'Y').to_euler()

TARGET = Vector((0, 0, 0.80))
bpy.ops.object.camera_add(location=(1.7, -2.1, 1.55))
cam = bpy.context.active_object
cam.name = "Camera"
cam.data.lens = 55.0
cam.rotation_euler = (TARGET - cam.location).to_track_quat('-Z', 'Y').to_euler()
bpy.context.scene.camera = cam
