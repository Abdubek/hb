import bpy
import bmesh
import random
from mathutils import Vector

random.seed(11)


def clear_scene():
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete(use_global=False)
    for coll in (bpy.data.meshes, bpy.data.materials, bpy.data.cameras, bpy.data.lights):
        for item in list(coll):
            if item.users == 0:
                coll.remove(item)


def make_material(name, color, roughness=0.55, metallic=0.0):
    mat = bpy.data.materials.new(name)
    mat.use_nodes = True
    bsdf = mat.node_tree.nodes.get("Principled BSDF")
    if bsdf is None:
        bsdf = next(n for n in mat.node_tree.nodes if n.type == 'BSDF_PRINCIPLED')
    bsdf.inputs["Base Color"].default_value = (color[0], color[1], color[2], 1.0)
    bsdf.inputs["Roughness"].default_value = roughness
    bsdf.inputs["Metallic"].default_value = metallic
    return mat


def add_box(name, size, center, mat=None, parent=None, rot=(0.0, 0.0, 0.0)):
    mesh = bpy.data.meshes.new(name)
    bm = bmesh.new()
    bmesh.ops.create_cube(bm, size=1.0)
    bmesh.ops.scale(bm, vec=Vector(size), verts=bm.verts)
    bm.to_mesh(mesh)
    bm.free()
    obj = bpy.data.objects.new(name, mesh)
    obj.location = center
    obj.rotation_euler = rot
    bpy.context.collection.objects.link(obj)
    if mat is not None:
        obj.data.materials.append(mat)
    if parent is not None:
        obj.parent = parent
    return obj


def look_at(obj, target):
    direction = obj.location - Vector(target)
    obj.rotation_euler = direction.to_track_quat('Z', 'Y').to_euler()


clear_scene()

OAK = make_material("MAT_Oak", (0.42, 0.26, 0.13), 0.5)
BACK = make_material("MAT_BackPanel", (0.24, 0.15, 0.08), 0.7)
FLOOR = make_material("MAT_Floor", (0.55, 0.53, 0.50), 0.85)
BOOK_COLORS = [(0.65, 0.14, 0.12), (0.12, 0.28, 0.52), (0.16, 0.42, 0.22),
               (0.72, 0.58, 0.18), (0.38, 0.16, 0.45), (0.82, 0.78, 0.68),
               (0.20, 0.20, 0.24), (0.78, 0.40, 0.14)]
BOOK_MATS = [make_material("MAT_Book_%02d" % i, c, 0.72) for i, c in enumerate(BOOK_COLORS)]

root = bpy.data.objects.new("Bookshelf", None)
bpy.context.collection.objects.link(root)

DEPTH = 0.30
PANEL = 0.04
SHELF_T = 0.045

# (x_center, width, height, z_base, shelf_count) -- staggered module heights and bases
MODULES = [
    (-1.30, 0.90, 1.90, 0.00, 5),
    (-0.36, 0.86, 1.45, 0.34, 4),
    (0.58, 0.90, 2.10, 0.00, 6),
    (1.52, 0.86, 1.25, 0.60, 3),
]


def fill_books(shelf_name, x_left, x_right, z_top, depth, parent):
    """Line books up from the left edge of an opening, leaving a random gap."""
    x = x_left + 0.02
    limit = x_right - random.uniform(0.05, 0.30)
    idx = 0
    while x < limit:
        w = random.uniform(0.025, 0.055)
        if x + w > limit:
            break
        h = random.uniform(0.20, 0.30)
        d = depth * random.uniform(0.72, 0.90)
        mat = random.choice(BOOK_MATS)
        lean = random.random() < 0.08
        if lean:
            add_box("%s_Book_%02d" % (shelf_name, idx), (w, d, h),
                    (x + w * 0.5 + 0.02, 0.0, z_top + h * 0.5 - 0.01),
                    mat, parent, rot=(0.0, 0.22, 0.0))
            x += w + 0.045
        else:
            add_box("%s_Book_%02d" % (shelf_name, idx), (w, d, h),
                    (x + w * 0.5, 0.0, z_top + h * 0.5), mat, parent)
            x += w + 0.004
        idx += 1


for m, (cx, width, height, z_base, shelves) in enumerate(MODULES):
    mod = bpy.data.objects.new("Module_%d" % m, None)
    mod.location = (cx, 0.0, 0.0)
    mod.parent = root
    bpy.context.collection.objects.link(mod)

    half = width * 0.5
    for sign, side in ((-1.0, "L"), (1.0, "R")):
        add_box("Module_%d_Side_%s" % (m, side), (PANEL, DEPTH, height),
                (sign * (half - PANEL * 0.5), 0.0, z_base + height * 0.5), OAK, mod)
    add_box("Module_%d_Back" % m, (width - PANEL * 2.0, 0.015, height),
            (0.0, DEPTH * 0.5 - 0.01, z_base + height * 0.5), BACK, mod)

    inner = width - PANEL * 2.0
    span = height - SHELF_T
    for s in range(shelves + 1):
        z = z_base + SHELF_T * 0.5 + span * (s / float(shelves))
        add_box("Module_%d_Shelf_%d" % (m, s), (inner, DEPTH, SHELF_T),
                (0.0, 0.0, z), OAK, mod)
        if s < shelves:
            fill_books("Module_%d_S%d" % (m, s), -inner * 0.5, inner * 0.5,
                       z + SHELF_T * 0.5, DEPTH, mod)

    add_box("Module_%d_Plinth" % m, (width, DEPTH * 0.8, 0.06),
            (0.0, 0.0, z_base - 0.03), BACK, mod)

add_box("Ground", (7.0, 5.0, 0.08), (0.0, 0.0, -0.10), FLOOR)

light_data = bpy.data.lights.new("KeyLight", type='AREA')
light_data.energy = 320.0
light_data.size = 3.0
key = bpy.data.objects.new("KeyLight", light_data)
key.location = (2.2, -3.0, 3.6)
bpy.context.collection.objects.link(key)
look_at(key, (0.0, 0.0, 1.0))

cam_data = bpy.data.cameras.new("Camera")
cam_data.lens = 45.0
cam = bpy.data.objects.new("Camera", cam_data)
cam.location = (2.6, -4.2, 2.1)
bpy.context.collection.objects.link(cam)
look_at(cam, (0.05, 0.0, 1.05))
bpy.context.scene.camera = cam
