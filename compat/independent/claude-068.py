import bpy
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


def finish(obj, mat, bevel=0.0, segments=3, smooth=False):
    obj.data.materials.append(mat)
    if bevel > 0.0:
        mod = obj.modifiers.new("Bevel", 'BEVEL')
        mod.width = bevel
        mod.segments = segments
        mod.limit_method = 'ANGLE'
    if smooth:
        try:
            bpy.ops.object.shade_auto_smooth(angle=0.6)
        except Exception:
            bpy.ops.object.shade_smooth()
    return obj


def add_box(name, size, location, mat, bevel=0.0, segments=3):
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=location)
    obj = bpy.context.active_object
    obj.name = name
    obj.scale = Vector(size)
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    return finish(obj, mat, bevel, segments)


def add_cyl(name, radius, depth, location, rotation, mat, verts=24):
    bpy.ops.mesh.primitive_cylinder_add(vertices=verts, radius=radius, depth=depth,
                                        location=location, rotation=rotation)
    obj = bpy.context.active_object
    obj.name = name
    return finish(obj, mat, smooth=True)


clear_scene()

shell_mat = make_material("Shell_ABS", (0.09, 0.13, 0.20), roughness=0.35)
trim_mat = make_material("Trim_Plastic", (0.02, 0.02, 0.02), roughness=0.55)
rubber_mat = make_material("Rubber", (0.03, 0.03, 0.03), roughness=0.85)
metal_mat = make_material("Handle_Alu", (0.72, 0.73, 0.75), roughness=0.25, metallic=1.0)

# --- main shell ---------------------------------------------------------
HX, HY, HZ = 0.225, 0.115, 0.325
BODY_Z = 0.395
add_box("Suitcase_Shell", (HX * 2, HY * 2, HZ * 2), (0, 0, BODY_Z),
        shell_mat, bevel=0.05, segments=4)

# split line between the two shell halves plus the zipper-side rim
add_box("Shell_Seam", (HX * 2 + 0.006, 0.012, HZ * 2 - 0.02), (0, 0, BODY_Z), trim_mat, bevel=0.004)

# ribbed front detail
for i, x in enumerate((-0.11, 0.0, 0.11)):
    add_box("Rib_%d" % i, (0.05, 0.012, HZ * 1.5), (x, -HY - 0.002, BODY_Z), trim_mat, bevel=0.005)

# --- corner bumpers ----------------------------------------------------
for ix, sx in enumerate((-1, 1)):
    for iy, sy in enumerate((-1, 1)):
        for iz, sz in enumerate((-1, 1)):
            loc = (sx * (HX - 0.015), sy * (HY - 0.015), BODY_Z + sz * (HZ - 0.015))
            add_box("Bumper_%d%d%d" % (ix, iy, iz), (0.085, 0.085, 0.085), loc,
                    rubber_mat, bevel=0.028, segments=3)

# --- wheels ------------------------------------------------------------
for ix, sx in enumerate((-1, 1)):
    for iy, sy in enumerate((-1, 1)):
        x, y = sx * 0.165, sy * 0.075
        add_box("WheelHousing_%d%d" % (ix, iy), (0.075, 0.05, 0.05), (x, y, 0.085),
                trim_mat, bevel=0.012)
        add_cyl("Wheel_%d%d" % (ix, iy), 0.038, 0.028, (x, y, 0.04),
                (0, 1.5708, 0), rubber_mat)
        add_cyl("Hubcap_%d%d" % (ix, iy), 0.015, 0.032, (x, y, 0.04),
                (0, 1.5708, 0), trim_mat, verts=16)

# --- telescoping handle ------------------------------------------------
for ix, sx in enumerate((-1, 1)):
    x = sx * 0.13
    add_cyl("HandleTube_%d" % ix, 0.013, 0.42, (x, 0.082, 0.78), (0, 0, 0), metal_mat, verts=16)
    add_box("HandleGuide_%d" % ix, (0.045, 0.045, 0.03), (x, 0.082, 0.712), trim_mat, bevel=0.008)

add_box("HandleGrip", (0.30, 0.045, 0.038), (0, 0.082, 0.985), trim_mat, bevel=0.016, segments=4)
add_box("GripButton", (0.07, 0.03, 0.014), (0, 0.06, 1.002), rubber_mat, bevel=0.005)

# --- side carry handle and feet ---------------------------------------
add_box("SideHandle", (0.03, 0.10, 0.045), (HX + 0.012, 0.0, BODY_Z), rubber_mat, bevel=0.014)
for ix, sx in enumerate((-1, 1)):
    add_box("Foot_%d" % ix, (0.07, 0.05, 0.03), (sx * 0.16, -0.075, 0.06), rubber_mat, bevel=0.01)

# --- ground, light, camera --------------------------------------------
ground_mat = make_material("Ground", (0.35, 0.34, 0.33), roughness=0.8)
bpy.ops.mesh.primitive_plane_add(size=6.0, location=(0, 0, 0))
ground = bpy.context.active_object
ground.name = "Ground"
ground.data.materials.append(ground_mat)

bpy.ops.object.light_add(type='AREA', location=(1.6, -1.8, 2.6))
key = bpy.context.active_object
key.name = "Key_Light"
key.data.energy = 400.0
key.data.size = 2.0
key.rotation_euler = (Vector((0, 0, 0.6)) - key.location).to_track_quat('-Z', 'Y').to_euler()

bpy.ops.object.camera_add(location=(1.35, -1.55, 1.20))
cam = bpy.context.active_object
cam.name = "Camera"
cam.data.lens = 50.0
cam.rotation_euler = (Vector((0, 0, 0.52)) - cam.location).to_track_quat('-Z', 'Y').to_euler()
bpy.context.scene.camera = cam
