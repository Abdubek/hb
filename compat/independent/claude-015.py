import bpy
import bmesh
from mathutils import Vector


def clear_scene():
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete(use_global=False)
    for coll in (bpy.data.meshes, bpy.data.materials, bpy.data.cameras, bpy.data.lights):
        for item in list(coll):
            if item.users == 0:
                coll.remove(item)


def make_material(name, color, roughness=0.6, metallic=0.0, alpha=1.0):
    mat = bpy.data.materials.new(name)
    mat.use_nodes = True
    bsdf = mat.node_tree.nodes.get("Principled BSDF")
    if bsdf is None:
        bsdf = next(n for n in mat.node_tree.nodes if n.type == 'BSDF_PRINCIPLED')
    bsdf.inputs["Base Color"].default_value = (color[0], color[1], color[2], 1.0)
    bsdf.inputs["Roughness"].default_value = roughness
    bsdf.inputs["Metallic"].default_value = metallic
    bsdf.inputs["Alpha"].default_value = alpha
    if alpha < 1.0:
        mat.blend_method = 'BLEND'
    return mat


def add_box(name, size, center, mat=None, parent=None):
    mesh = bpy.data.meshes.new(name)
    bm = bmesh.new()
    bmesh.ops.create_cube(bm, size=1.0)
    bmesh.ops.scale(bm, vec=Vector(size), verts=bm.verts)
    bm.to_mesh(mesh)
    bm.free()
    obj = bpy.data.objects.new(name, mesh)
    obj.location = center
    bpy.context.collection.objects.link(obj)
    if mat is not None:
        obj.data.materials.append(mat)
    if parent is not None:
        obj.parent = parent
    return obj


def add_cylinder(name, radius, height, center, mat=None, parent=None, verts=10):
    mesh = bpy.data.meshes.new(name)
    bm = bmesh.new()
    bmesh.ops.create_cone(bm, cap_ends=True, cap_tris=False, segments=verts,
                          radius1=radius, radius2=radius, depth=height)
    bm.to_mesh(mesh)
    bm.free()
    obj = bpy.data.objects.new(name, mesh)
    obj.location = center
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

WALL = make_material("MAT_Stucco", (0.78, 0.74, 0.66), 0.85)
TRIM = make_material("MAT_Trim", (0.90, 0.89, 0.86), 0.6)
GLASS = make_material("MAT_Glass", (0.35, 0.48, 0.55), 0.12, 0.0, alpha=0.45)
METAL = make_material("MAT_Railing", (0.15, 0.16, 0.18), 0.35, 0.85)
STONE = make_material("MAT_Stone", (0.52, 0.50, 0.47), 0.8)
DOOR = make_material("MAT_Door", (0.28, 0.15, 0.09), 0.45)

BUILDING_W = 10.0
WALL_D = 0.45
FLOOR_H = 3.2
STORIES = 3
BAY_X = [-3.6, -1.2, 1.2, 3.6]
WIN_W, WIN_H = 1.25, 1.80

facade = bpy.data.objects.new("Facade", None)
bpy.context.collection.objects.link(facade)


def add_window(name, x, z_sill, parent):
    """Recessed opening approximated by a frame ring plus glass pane."""
    zc = z_sill + WIN_H * 0.5
    y_face = -WALL_D * 0.5
    t = 0.09
    add_box(name + "_Glass", (WIN_W, 0.03, WIN_H), (x, y_face + 0.13, zc), GLASS, parent)
    add_box(name + "_Mullion", (0.05, 0.05, WIN_H), (x, y_face + 0.12, zc), TRIM, parent)
    add_box(name + "_FrameL", (t, 0.14, WIN_H + t * 2), (x - WIN_W * 0.5 - t * 0.5, y_face + 0.07, zc), TRIM, parent)
    add_box(name + "_FrameR", (t, 0.14, WIN_H + t * 2), (x + WIN_W * 0.5 + t * 0.5, y_face + 0.07, zc), TRIM, parent)
    add_box(name + "_Lintel", (WIN_W + t * 4, 0.18, 0.14), (x, y_face + 0.05, zc + WIN_H * 0.5 + t), TRIM, parent)
    add_box(name + "_Sill", (WIN_W + t * 4, 0.26, 0.09), (x, y_face + 0.02, z_sill - 0.05), STONE, parent)


def add_balcony(name, x, z, width, parent):
    depth = 1.05
    slab_y = -WALL_D * 0.5 - depth * 0.5
    add_box(name + "_Slab", (width, depth, 0.14), (x, slab_y, z - 0.07), STONE, parent)
    rail_h = 0.95
    fy = -WALL_D * 0.5 - depth
    add_box(name + "_TopRail", (width, 0.06, 0.06), (x, fy + 0.05, z + rail_h), METAL, parent)
    add_box(name + "_MidRail", (width, 0.04, 0.04), (x, fy + 0.05, z + rail_h * 0.5), METAL, parent)
    n = int(width / 0.22)
    for i in range(n + 1):
        px = x - width * 0.5 + width * (i / float(n))
        add_cylinder("%s_Baluster_%02d" % (name, i), 0.022, rail_h,
                     (px, fy + 0.05, z + rail_h * 0.5), METAL, parent, verts=8)
    for sign, side in ((-1.0, "L"), (1.0, "R")):
        sx = x + sign * width * 0.5
        add_box("%s_Side_%s" % (name, side), (0.05, depth, 0.06), (sx, slab_y, z + rail_h), METAL, parent)
        add_cylinder("%s_SidePost_%s" % (name, side), 0.03, rail_h,
                     (sx, -WALL_D * 0.5 - 0.06, z + rail_h * 0.5), METAL, parent, verts=8)


total_h = FLOOR_H * STORIES
add_box("Wall_Main", (BUILDING_W, WALL_D, total_h), (0.0, 0.0, total_h * 0.5), WALL, facade)
add_box("Wall_Return", (BUILDING_W - 0.6, 5.0, total_h - 0.2),
        (0.0, 2.7, (total_h - 0.2) * 0.5), WALL, facade)
add_box("Base_Plinth", (BUILDING_W + 0.3, WALL_D + 0.25, 0.75),
        (0.0, 0.05, 0.375), STONE, facade)

for story in range(STORIES):
    z0 = story * FLOOR_H
    add_box("Band_Floor_%d" % story, (BUILDING_W + 0.2, WALL_D + 0.14, 0.16),
            (0.0, 0.0, z0 + 0.08), TRIM, facade)
    sill = z0 + 0.95
    for b, x in enumerate(BAY_X):
        if story == 0 and b == 1:
            add_box("Entry_Door", (1.30, 0.10, 2.35), (x, -WALL_D * 0.5 + 0.06, 1.175), DOOR, facade)
            add_box("Entry_Frame", (1.55, 0.20, 2.60), (x, -WALL_D * 0.5 + 0.01, 1.30), TRIM, facade)
            add_box("Entry_Canopy", (2.0, 0.9, 0.12), (x, -WALL_D * 0.5 - 0.45, 2.80), STONE, facade)
            add_box("Entry_Step", (2.0, 0.7, 0.16), (x, -WALL_D * 0.5 - 0.35, 0.08), STONE, facade)
            continue
        add_window("Win_%d_%d" % (story, b), x, sill, facade)
    if story > 0:
        add_balcony("Balcony_%d_A" % story, -2.4, z0 + 0.16, 3.4, facade)
        add_balcony("Balcony_%d_B" % story, 2.4, z0 + 0.16, 3.4, facade)

add_box("Cornice_Lower", (BUILDING_W + 0.35, WALL_D + 0.35, 0.18),
        (0.0, 0.0, total_h + 0.09), TRIM, facade)
add_box("Cornice_Cap", (BUILDING_W + 0.6, WALL_D + 0.6, 0.16),
        (0.0, 0.0, total_h + 0.26), STONE, facade)
add_box("Parapet", (BUILDING_W, WALL_D + 0.1, 0.55),
        (0.0, 0.0, total_h + 0.61), WALL, facade)
add_box("Ground", (26.0, 22.0, 0.2), (0.0, -4.0, -0.1), STONE)

sun_data = bpy.data.lights.new("Sun", type='SUN')
sun_data.energy = 4.0
sun = bpy.data.objects.new("Sun", sun_data)
sun.location = (-8.0, -12.0, 16.0)
bpy.context.collection.objects.link(sun)
look_at(sun, (0.0, 0.0, 4.0))

cam_data = bpy.data.cameras.new("Camera")
cam_data.lens = 35.0
cam = bpy.data.objects.new("Camera", cam_data)
cam.location = (10.0, -16.0, 7.5)
bpy.context.collection.objects.link(cam)
look_at(cam, (0.0, 0.0, 4.6))
bpy.context.scene.camera = cam
