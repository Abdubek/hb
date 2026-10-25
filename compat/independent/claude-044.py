"""Tiled swimming pool with ladder and surrounding deck (Blender 4.5 LTS)."""
import bpy
import bmesh
from mathutils import Vector, Matrix

POOL_X, POOL_Y, DEPTH = 3.0, 2.0, 1.6
DECK_X, DECK_Y, DECK_T = 5.0, 4.0, 0.3


def clear_scene():
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete(use_global=False)
    for coll in (bpy.data.meshes, bpy.data.materials, bpy.data.cameras, bpy.data.lights):
        for item in list(coll):
            if item.users == 0:
                coll.remove(item)


def make_material(name, color, roughness=0.5, metallic=0.0, alpha=1.0):
    mat = bpy.data.materials.new(name)
    mat.use_nodes = True
    bsdf = mat.node_tree.nodes["Principled BSDF"]
    bsdf.inputs["Base Color"].default_value = (color[0], color[1], color[2], 1.0)
    bsdf.inputs["Roughness"].default_value = roughness
    bsdf.inputs["Metallic"].default_value = metallic
    if alpha < 1.0:
        bsdf.inputs["Alpha"].default_value = alpha
        if hasattr(mat, "surface_render_method"):
            mat.surface_render_method = 'BLENDED'
        elif hasattr(mat, "blend_method"):
            mat.blend_method = 'BLEND'
    return mat


def add_box(name, size, center, mat):
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=center)
    ob = bpy.context.object
    ob.name = name
    ob.scale = size
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    ob.data.materials.append(mat)
    return ob


def add_cylinder(name, p0, p1, radius, mat, verts=16):
    p0, p1 = Vector(p0), Vector(p1)
    d = p1 - p0
    bpy.ops.mesh.primitive_cylinder_add(vertices=verts, radius=radius, depth=d.length,
                                        location=(p0 + p1) * 0.5)
    ob = bpy.context.object
    ob.name = name
    ob.rotation_euler = d.to_track_quat('Z', 'Y').to_euler()
    ob.data.materials.append(mat)
    return ob


def build_tile_field(name, x0, x1, y0, y1, z_top, mat, tile=0.5, gap=0.04, thick=0.05):
    """A grid of individual ceramic tiles baked into one mesh."""
    bm = bmesh.new()
    nx = max(1, int(round((x1 - x0) / tile)))
    ny = max(1, int(round((y1 - y0) / tile)))
    for i in range(nx):
        for j in range(ny):
            cx = x0 + (i + 0.5) * (x1 - x0) / nx
            cy = y0 + (j + 0.5) * (y1 - y0) / ny
            mat_loc = Matrix.Translation((cx, cy, z_top - thick * 0.5))
            scale = Matrix.Diagonal(Vector((tile - gap, tile - gap, thick, 1.0)))
            bmesh.ops.create_cube(bm, size=1.0, matrix=mat_loc @ scale)
    me = bpy.data.meshes.new(name)
    bm.to_mesh(me)
    bm.free()
    ob = bpy.data.objects.new(name, me)
    bpy.context.collection.objects.link(ob)
    ob.data.materials.append(mat)
    return ob


def add_camera(location, target):
    cam = bpy.data.objects.new("Camera", bpy.data.cameras.new("Camera"))
    bpy.context.collection.objects.link(cam)
    cam.location = location
    cam.rotation_euler = (Vector(target) - Vector(location)).to_track_quat('-Z', 'Y').to_euler()
    cam.data.lens = 35
    bpy.context.scene.camera = cam


def main():
    clear_scene()
    deck_mat = make_material("DeckStone", (0.78, 0.74, 0.66), roughness=0.8)
    coping_mat = make_material("CopingStone", (0.88, 0.86, 0.80), roughness=0.7)
    tile_mat = make_material("PoolTileBlue", (0.18, 0.55, 0.72), roughness=0.15)
    band_mat = make_material("WaterlineTileDark", (0.06, 0.24, 0.38), roughness=0.15)
    water_mat = make_material("Water", (0.10, 0.45, 0.60), roughness=0.05, alpha=0.35)
    steel_mat = make_material("StainlessSteel", (0.75, 0.76, 0.78), roughness=0.25, metallic=1.0)

    # Deck slabs surrounding the pool opening
    zc = -DECK_T * 0.5
    add_box("Deck_West", ((DECK_X - POOL_X), 2 * DECK_Y, DECK_T),
            (-(POOL_X + DECK_X) * 0.5, 0, zc), deck_mat)
    add_box("Deck_East", ((DECK_X - POOL_X), 2 * DECK_Y, DECK_T),
            ((POOL_X + DECK_X) * 0.5, 0, zc), deck_mat)
    add_box("Deck_South", (2 * POOL_X, (DECK_Y - POOL_Y), DECK_T),
            (0, -(POOL_Y + DECK_Y) * 0.5, zc), deck_mat)
    add_box("Deck_North", (2 * POOL_X, (DECK_Y - POOL_Y), DECK_T),
            (0, (POOL_Y + DECK_Y) * 0.5, zc), deck_mat)

    # Basin shell: floor slab and four walls
    add_box("Basin_Floor", (2 * POOL_X + 0.4, 2 * POOL_Y + 0.4, 0.25),
            (0, 0, -DEPTH - 0.125), deck_mat)
    for nm, sz, ctr in (
        ("Basin_Wall_West", (0.2, 2 * POOL_Y, DEPTH), (-POOL_X - 0.1, 0, -DEPTH * 0.5)),
        ("Basin_Wall_East", (0.2, 2 * POOL_Y, DEPTH), (POOL_X + 0.1, 0, -DEPTH * 0.5)),
        ("Basin_Wall_South", (2 * POOL_X + 0.4, 0.2, DEPTH), (0, -POOL_Y - 0.1, -DEPTH * 0.5)),
        ("Basin_Wall_North", (2 * POOL_X + 0.4, 0.2, DEPTH), (0, POOL_Y + 0.1, -DEPTH * 0.5)),
    ):
        add_box(nm, sz, ctr, tile_mat)

    # Coping ring around the lip
    for nm, sz, ctr in (
        ("Coping_West", (0.32, 2 * POOL_Y + 0.64, 0.1), (-POOL_X - 0.16, 0, 0.05)),
        ("Coping_East", (0.32, 2 * POOL_Y + 0.64, 0.1), (POOL_X + 0.16, 0, 0.05)),
        ("Coping_South", (2 * POOL_X, 0.32, 0.1), (0, -POOL_Y - 0.16, 0.05)),
        ("Coping_North", (2 * POOL_X, 0.32, 0.1), (0, POOL_Y + 0.16, 0.05)),
    ):
        add_box(nm, sz, ctr, coping_mat)

    build_tile_field("PoolFloorTiles", -POOL_X, POOL_X, -POOL_Y, POOL_Y, -DEPTH + 0.06, tile_mat)
    build_tile_field("DeckTiles", -DECK_X, DECK_X, -DECK_Y, DECK_Y, 0.02, deck_mat, tile=1.0, gap=0.05)

    # Dark waterline band of tiles just under the coping
    for nm, sz, ctr in (
        ("Waterline_West", (0.06, 2 * POOL_Y, 0.16), (-POOL_X + 0.03, 0, -0.16)),
        ("Waterline_East", (0.06, 2 * POOL_Y, 0.16), (POOL_X - 0.03, 0, -0.16)),
        ("Waterline_South", (2 * POOL_X, 0.06, 0.16), (0, -POOL_Y + 0.03, -0.16)),
        ("Waterline_North", (2 * POOL_X, 0.06, 0.16), (0, POOL_Y - 0.03, -0.16)),
    ):
        add_box(nm, sz, ctr, band_mat)

    water = add_box("WaterSurface", (2 * POOL_X - 0.04, 2 * POOL_Y - 0.04, 1.2),
                    (0, 0, -0.25 - 0.6), water_mat)
    water.name = "WaterVolume"

    # Stainless ladder at the north end
    for side, rx in (("L", 1.35), ("R", 1.95)):
        add_cylinder("Ladder_Rail_%s" % side, (rx, POOL_Y - 0.18, -DEPTH + 0.25),
                     (rx, POOL_Y - 0.18, 0.55), 0.035, steel_mat)
        add_cylinder("Ladder_Grab_%s" % side, (rx, POOL_Y - 0.18, 0.55),
                     (rx, POOL_Y + 0.30, 0.95), 0.035, steel_mat)
        add_cylinder("Ladder_Post_%s" % side, (rx, POOL_Y + 0.30, 0.95),
                     (rx, POOL_Y + 0.30, 0.05), 0.035, steel_mat)
    for k, z in enumerate((-1.05, -0.60, -0.15)):
        add_cylinder("Ladder_Step_%d" % (k + 1), (1.35, POOL_Y - 0.18, z),
                     (1.95, POOL_Y - 0.18, z), 0.028, steel_mat)

    # Deck furniture for scale
    add_box("DivingBoard", (0.5, 1.6, 0.07), (-1.8, POOL_Y + 0.5, 0.35), coping_mat)
    add_box("DivingBoard_Support", (0.4, 0.3, 0.35), (-1.8, POOL_Y + 1.1, 0.17), steel_mat)

    sun = bpy.data.objects.new("Sun", bpy.data.lights.new("Sun", 'SUN'))
    bpy.context.collection.objects.link(sun)
    sun.data.energy = 4.0
    sun.location = (6, -6, 10)
    sun.rotation_euler = (0.9, 0.1, 0.7)

    add_camera((9.0, -9.5, 6.5), (0, 0, -0.4))


main()
