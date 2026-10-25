import bpy
import bmesh
import math
from mathutils import Vector, Matrix

POST_TOP = 0.34
HOOK_R = 0.055
BAND_R = 0.105
BAND_TUBE = 0.014
BAND_CZ = POST_TOP + HOOK_R - (BAND_R - BAND_TUBE)


def clear_scene():
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete(use_global=False)
    for coll in (bpy.data.meshes, bpy.data.materials, bpy.data.cameras, bpy.data.lights):
        for item in list(coll):
            if item.users == 0:
                coll.remove(item)


def new_material(name, color, roughness=0.5, metallic=0.0):
    mat = bpy.data.materials.new(name)
    mat.use_nodes = True
    bsdf = mat.node_tree.nodes["Principled BSDF"]
    bsdf.inputs["Base Color"].default_value = (*color, 1.0)
    bsdf.inputs["Roughness"].default_value = roughness
    bsdf.inputs["Metallic"].default_value = metallic
    return mat


def finish(name, bm, location, mat, smooth=False, bevel=0.0):
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    mesh = bpy.data.meshes.new(name)
    bm.to_mesh(mesh)
    bm.free()
    if smooth:
        for poly in mesh.polygons:
            poly.use_smooth = True
    obj = bpy.data.objects.new(name, mesh)
    bpy.context.collection.objects.link(obj)
    obj.location = location
    obj.data.materials.append(mat)
    if bevel > 0.0:
        mod = obj.modifiers.new("Bevel", 'BEVEL')
        mod.width = bevel
        mod.segments = 2
        mod.limit_method = 'ANGLE'
    return obj


def add_cylinder(name, radius, depth, location, mat, axis='Z', segments=32, smooth=True):
    bm = bmesh.new()
    rot = Matrix.Rotation(math.radians(90.0), 4, 'Y') if axis == 'X' else Matrix.Identity(4)
    bmesh.ops.create_cone(bm, cap_ends=True, cap_tris=False, segments=segments,
                          radius1=radius, radius2=radius, depth=depth, matrix=rot)
    return finish(name, bm, location, mat, smooth=smooth)


def add_box(name, size, location, mat, rotation=None, bevel=0.0):
    bm = bmesh.new()
    bmesh.ops.create_cube(bm, size=1.0, matrix=Matrix.Diagonal(Vector(size).to_4d()))
    obj = finish(name, bm, location, mat, bevel=bevel)
    if rotation is not None:
        obj.rotation_euler = rotation
    return obj


def add_arc_tube(name, center, radius, tube, a0, a1, mat, arc_segs=40, ring_segs=14):
    """Tube swept along a circular arc lying in the XZ plane."""
    bm = bmesh.new()
    up = Vector((0.0, 1.0, 0.0))
    rings = []
    for i in range(arc_segs + 1):
        a = a0 + (a1 - a0) * i / arc_segs
        c = Vector((radius * math.cos(a), 0.0, radius * math.sin(a)))
        tangent = Vector((-math.sin(a), 0.0, math.cos(a)))
        side = tangent.cross(up).normalized()
        ring = []
        for j in range(ring_segs):
            th = 2.0 * math.pi * j / ring_segs
            ring.append(bm.verts.new(c + side * (tube * math.cos(th)) + up * (tube * math.sin(th))))
        rings.append(ring)
    for i in range(arc_segs):
        for j in range(ring_segs):
            k = (j + 1) % ring_segs
            bm.faces.new((rings[i][j], rings[i][k], rings[i + 1][k], rings[i + 1][j]))
    bm.faces.new(rings[0])
    bm.faces.new(rings[-1])
    return finish(name, bm, center, mat, smooth=True)


def add_camera(location, target):
    cam = bpy.data.objects.new("Camera", bpy.data.cameras.new("Camera"))
    bpy.context.collection.objects.link(cam)
    cam.location = location
    cam.data.lens = 55.0
    cam.rotation_euler = (Vector(target) - Vector(location)).to_track_quat('-Z', 'Y').to_euler()
    bpy.context.scene.camera = cam


def add_light(name, location, energy, size, target):
    light = bpy.data.lights.new(name, 'AREA')
    light.energy = energy
    light.size = size
    obj = bpy.data.objects.new(name, light)
    bpy.context.collection.objects.link(obj)
    obj.location = location
    obj.rotation_euler = (Vector(target) - Vector(location)).to_track_quat('-Z', 'Y').to_euler()


clear_scene()

steel = new_material("BrushedSteel", (0.55, 0.56, 0.58), roughness=0.3, metallic=1.0)
wood = new_material("WalnutBase", (0.20, 0.11, 0.06), roughness=0.45)
shell = new_material("CupShell", (0.07, 0.07, 0.08), roughness=0.4)
leather = new_material("PadLeather", (0.03, 0.03, 0.035), roughness=0.75)
band_mat = new_material("HeadbandPad", (0.09, 0.09, 0.10), roughness=0.6)
accent = new_material("Accent", (0.72, 0.42, 0.10), roughness=0.35, metallic=0.6)
floor_mat = new_material("Tabletop", (0.26, 0.25, 0.24), roughness=0.7)

add_box("Tabletop", (1.6, 1.6, 0.02), (0.0, 0.0, -0.011), floor_mat)
add_cylinder("StandBase", 0.095, 0.022, (0.0, 0.0, 0.011), wood)
add_cylinder("StandBaseTrim", 0.055, 0.008, (0.0, 0.0, 0.026), steel)
add_cylinder("StandPost", 0.013, POST_TOP - 0.02, (0.0, 0.0, 0.02 + (POST_TOP - 0.02) / 2.0), steel)
add_arc_tube("StandHook", (0.0, 0.0, POST_TOP), HOOK_R, 0.013,
             math.radians(0.0), math.radians(180.0), steel)

add_arc_tube("HeadbandFrame", (0.0, 0.0, BAND_CZ), BAND_R, BAND_TUBE,
             math.radians(-8.0), math.radians(188.0), shell)
add_arc_tube("HeadbandPad", (0.0, 0.0, BAND_CZ), BAND_R - BAND_TUBE * 0.55, 0.011,
             math.radians(25.0), math.radians(155.0), band_mat)

for sign, side in ((-1.0, "L"), (1.0, "R")):
    end_a = math.radians(188.0) if sign < 0 else math.radians(-8.0)
    ex = BAND_R * math.cos(end_a) * (1.0 if sign > 0 else 1.0)
    ex = abs(BAND_R * math.cos(end_a)) * sign
    ez = BAND_CZ + BAND_R * math.sin(end_a)
    cup_z = ez - 0.055
    cup_x = sign * 0.096
    add_box("Slider_" + side, (0.012, 0.022, 0.05), (ex, 0.0, ez - 0.018), steel, bevel=0.002)
    add_box("Yoke_" + side, (0.010, 0.052, 0.026), (cup_x + sign * 0.012, 0.0, cup_z + 0.03), shell,
            bevel=0.003)
    add_cylinder("CupShell_" + side, 0.046, 0.030, (cup_x, 0.0, cup_z), shell, axis='X')
    add_cylinder("CupPlate_" + side, 0.030, 0.006, (cup_x + sign * 0.017, 0.0, cup_z), accent, axis='X')
    add_cylinder("EarPad_" + side, 0.048, 0.024, (cup_x - sign * 0.026, 0.0, cup_z), leather, axis='X')
    add_cylinder("PadInner_" + side, 0.028, 0.026, (cup_x - sign * 0.030, 0.0, cup_z), shell, axis='X')

add_light("KeyLight", (0.6, -0.7, 0.85), 260.0, 1.1, (0.0, 0.0, 0.28))
add_light("RimLight", (-0.7, 0.5, 0.6), 120.0, 1.0, (0.0, 0.0, 0.30))
add_camera((0.46, -0.62, 0.46), (0.0, 0.0, 0.26))

bpy.context.scene.world = bpy.context.scene.world or bpy.data.worlds.new("World")
bpy.context.scene.world.use_nodes = True
bpy.context.scene.world.node_tree.nodes["Background"].inputs[0].default_value = (0.04, 0.045, 0.05, 1.0)
