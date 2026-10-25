import bpy
import bmesh
import math
from mathutils import Vector

U = 0.019          # one key unit
GAP = 0.0026       # gap between keycaps
KEY_H = 0.0105     # keycap body height
CASE_H = 0.022     # case height
MARGIN = 0.009     # case border around the key field
UNITS_X = 15.0     # 60% layout width in units
ROWS_Y = 5.0

# (widths in units, extra lift, row tilt) from number row down to spacebar row
LAYOUT = [
    ([1] * 13 + [2], 0.0038, math.radians(-7)),
    ([1.5] + [1] * 12 + [1.5], 0.0024, math.radians(-4)),
    ([1.75] + [1] * 11 + [2.25], 0.0012, math.radians(0)),
    ([2.25] + [1] * 10 + [2.75], 0.0022, math.radians(4)),
    ([1.25, 1.25, 1.25, 6.25, 1.25, 1.25, 1.25, 1.25], 0.0034, math.radians(7)),
]


def purge_scene():
    for obj in list(bpy.data.objects):
        bpy.data.objects.remove(obj, do_unlink=True)
    for mesh in list(bpy.data.meshes):
        bpy.data.meshes.remove(mesh)


def material(name, color, metallic=0.0, roughness=0.5):
    mat = bpy.data.materials.new(name)
    mat.use_nodes = True
    bsdf = mat.node_tree.nodes["Principled BSDF"]
    bsdf.inputs["Base Color"].default_value = (color[0], color[1], color[2], 1.0)
    bsdf.inputs["Metallic"].default_value = metallic
    bsdf.inputs["Roughness"].default_value = roughness
    return mat


def link_bmesh(bm, name, mat, location, rotation=(0, 0, 0), parent=None):
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    mesh = bpy.data.meshes.new(name)
    bm.to_mesh(mesh)
    bm.free()
    obj = bpy.data.objects.new(name, mesh)
    obj.location = location
    obj.rotation_euler = rotation
    obj.data.materials.append(mat)
    obj.parent = parent
    bpy.context.collection.objects.link(obj)
    return obj


def beveled_box(name, dims, location, mat, bevel=0.0008, rotation=(0, 0, 0), parent=None):
    bm = bmesh.new()
    bmesh.ops.create_cube(bm, size=1.0)
    for v in bm.verts:
        v.co.x *= dims[0]
        v.co.y *= dims[1]
        v.co.z *= dims[2]
    bmesh.ops.bevel(bm, geom=bm.verts[:] + bm.edges[:], offset=bevel,
                    segments=2, affect='EDGES')
    return link_bmesh(bm, name, mat, location, rotation, parent)


def keycap(name, width_u, location, mat, tilt, parent):
    """Tapered, slightly dished-looking keycap."""
    w = width_u * U - GAP
    d = U - GAP
    bm = bmesh.new()
    bmesh.ops.create_cube(bm, size=1.0)
    for v in bm.verts:
        v.co.x *= w
        v.co.y *= d
        v.co.z = v.co.z * KEY_H
    for v in bm.verts:
        if v.co.z > 0.0:
            v.co.x *= 0.87
            v.co.y *= 0.78
            v.co.z -= 0.0008
    bmesh.ops.bevel(bm, geom=bm.verts[:] + bm.edges[:], offset=0.0007,
                    segments=2, affect='EDGES')
    return link_bmesh(bm, name, mat, location, (tilt, 0, 0), parent)


def cylinder(name, radius, depth, location, mat, parent, rotation=(0, 0, 0), verts=16):
    bpy.ops.mesh.primitive_cylinder_add(vertices=verts, radius=radius, depth=depth,
                                        location=location, rotation=rotation)
    obj = bpy.context.active_object
    obj.name = name
    obj.data.name = name
    obj.data.materials.append(mat)
    obj.parent = parent
    return obj


purge_scene()

case_mat = material("CaseAluminium", (0.20, 0.21, 0.23), 0.85, 0.35)
plate_mat = material("SwitchPlate", (0.05, 0.05, 0.06), 0.6, 0.5)
alpha_mat = material("KeycapAlpha", (0.84, 0.82, 0.77), 0.0, 0.45)
mod_mat = material("KeycapModifier", (0.22, 0.27, 0.33), 0.0, 0.45)
accent_mat = material("KeycapAccent", (0.86, 0.34, 0.12), 0.0, 0.42)
space_mat = material("KeycapSpace", (0.74, 0.72, 0.68), 0.0, 0.45)
rubber_mat = material("FootRubber", (0.03, 0.03, 0.03), 0.0, 0.75)
led_mat = material("IndicatorLED", (0.25, 0.95, 0.45), 0.0, 0.2)
led_mat.node_tree.nodes["Principled BSDF"].inputs["Emission Strength"].default_value = 4.0
led_mat.node_tree.nodes["Principled BSDF"].inputs["Emission Color"].default_value = (0.25, 0.95, 0.45, 1.0)

root = bpy.data.objects.new("MechanicalKeyboard", None)
bpy.context.collection.objects.link(root)

case_w = UNITS_X * U + 2 * MARGIN
case_d = ROWS_Y * U + 2 * MARGIN
beveled_box("Case", (case_w, case_d, CASE_H), (0, 0, CASE_H * 0.5), case_mat,
            bevel=0.0022, parent=root)
beveled_box("SwitchPlate", (UNITS_X * U + 0.002, ROWS_Y * U + 0.002, 0.004),
            (0, 0, CASE_H - 0.0015), plate_mat, bevel=0.0005, parent=root)
beveled_box("USBPort", (0.011, 0.008, 0.005),
            (0, case_d * 0.5 - 0.002, CASE_H - 0.008), plate_mat,
            bevel=0.0006, parent=root)

for sx in (-1, 1):
    for sy in (-1, 1):
        cylinder("Foot_%d_%d" % (sx, sy), 0.007, 0.004,
                 (sx * (case_w * 0.5 - 0.018), sy * (case_d * 0.5 - 0.014), -0.002),
                 rubber_mat, root)

for i in range(3):
    cylinder("LED_%d" % i, 0.0016, 0.002,
             (case_w * 0.5 - 0.012 - i * 0.007, case_d * 0.5 - 0.005, CASE_H - 0.0005),
             led_mat, root, verts=10)

# ---- keycaps -----------------------------------------------------------
key_top = CASE_H + 0.0015
for r, (widths, lift, tilt) in enumerate(LAYOUT):
    y = (2.0 - r) * U
    x = -UNITS_X * U * 0.5
    for i, w in enumerate(widths):
        cx = x + w * U * 0.5
        if w >= 6.0:
            mat = space_mat
        elif r == 0 and i == 0:
            mat = accent_mat
        elif r == 2 and i == len(widths) - 1:
            mat = accent_mat
        elif w != 1:
            mat = mod_mat
        else:
            mat = alpha_mat
        keycap("Key_R%d_%02d" % (r, i), w, (cx, y, key_top + lift + KEY_H * 0.5),
               mat, tilt, root)
        x += w * U

# ---- lighting and camera ----------------------------------------------
key_data = bpy.data.lights.new("KeyLight", 'AREA')
key_data.energy = 90.0
key_data.size = 0.6
key_light = bpy.data.objects.new("KeyLight", key_data)
key_light.location = (0.16, -0.20, 0.40)
key_light.rotation_euler = (math.radians(32), math.radians(16), 0)
bpy.context.collection.objects.link(key_light)

rim_data = bpy.data.lights.new("RimLight", 'AREA')
rim_data.energy = 35.0
rim_data.size = 0.8
rim = bpy.data.objects.new("RimLight", rim_data)
rim.location = (-0.25, 0.24, 0.22)
rim.rotation_euler = (math.radians(65), 0, math.radians(-140))
bpy.context.collection.objects.link(rim)

cam_data = bpy.data.cameras.new("Camera")
cam_data.lens = 45
cam = bpy.data.objects.new("Camera", cam_data)
cam.location = (0.17, -0.27, 0.21)
target = Vector((0.0, -0.005, CASE_H))
cam.rotation_euler = (target - cam.location).to_track_quat('-Z', 'Y').to_euler()
bpy.context.collection.objects.link(cam)
bpy.context.scene.camera = cam
