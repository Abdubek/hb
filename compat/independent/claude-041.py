import bpy
import bmesh
from mathutils import Vector


def clear_scene():
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete(use_global=False)


def make_material(name, color, rough=0.6, metal=0.0):
    mat = bpy.data.materials.new(name)
    mat.use_nodes = True
    bsdf = mat.node_tree.nodes['Principled BSDF']
    bsdf.inputs['Base Color'].default_value = (*color, 1.0)
    bsdf.inputs['Roughness'].default_value = rough
    bsdf.inputs['Metallic'].default_value = metal
    return mat


def add_box(name, center, size, mat, rot=(0.0, 0.0, 0.0)):
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=center, rotation=rot)
    obj = bpy.context.object
    obj.name = name
    obj.scale = Vector(size) * 0.5
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    obj.data.materials.append(mat)
    return obj


def add_gable_roof(name, half_x, y0, y1, eave_z, ridge_z, mat):
    """Triangular prism: ridge runs along X, slopes fall toward +/-Y."""
    ymid = (y0 + y1) * 0.5
    profile = [(y0, eave_z), (y1, eave_z), (ymid, ridge_z)]
    bm = bmesh.new()
    left = [bm.verts.new((-half_x, y, z)) for y, z in profile]
    right = [bm.verts.new((half_x, y, z)) for y, z in profile]
    bm.faces.new(left)
    bm.faces.new(right[::-1])
    for i in range(3):
        j = (i + 1) % 3
        bm.faces.new((left[i], right[i], right[j], left[j]))
    bm.normal_update()
    me = bpy.data.meshes.new(name)
    bm.to_mesh(me)
    bm.free()
    obj = bpy.data.objects.new(name, me)
    bpy.context.collection.objects.link(obj)
    obj.data.materials.append(mat)
    return obj


def add_window(name, x, z, mat_frame, mat_glass):
    add_box(name + '_Frame', (x, -1.52, z), (0.9, 0.10, 1.0), mat_frame)
    add_box(name + '_Glass', (x, -1.56, z), (0.72, 0.04, 0.82), mat_glass)
    add_box(name + '_Mullion', (x, -1.58, z), (0.05, 0.04, 0.82), mat_frame)
    add_box(name + '_Sill', (x, -1.58, z - 0.55), (1.05, 0.16, 0.08), mat_frame)


def setup_camera(target):
    bpy.ops.object.camera_add(location=(7.5, -9.0, 5.2))
    cam = bpy.context.object
    cam.name = 'SceneCamera'
    cam.rotation_euler = (Vector(target) - cam.location).to_track_quat('-Z', 'Y').to_euler()
    cam.data.lens = 42
    bpy.context.scene.camera = cam
    return cam


clear_scene()

siding = make_material('Siding', (0.86, 0.85, 0.80), rough=0.7)
trim = make_material('Trim', (0.95, 0.95, 0.93), rough=0.5)
shingle = make_material('Shingles', (0.24, 0.26, 0.29), rough=0.85)
deck = make_material('DeckWood', (0.52, 0.36, 0.21), rough=0.75)
brick = make_material('Brick', (0.48, 0.24, 0.19), rough=0.9)
glass = make_material('WindowGlass', (0.35, 0.55, 0.68), rough=0.08, metal=0.2)
doorpaint = make_material('DoorPaint', (0.14, 0.34, 0.26), rough=0.45)
stone = make_material('Foundation', (0.42, 0.41, 0.40), rough=0.95)
lawn = make_material('Lawn', (0.24, 0.36, 0.18), rough=1.0)

add_box('Ground', (0.0, 0.0, -0.05), (24.0, 24.0, 0.1), lawn)
add_box('Foundation', (0.0, 0.0, 0.15), (4.2, 3.2, 0.3), stone)
add_box('Walls', (0.0, 0.0, 1.55), (4.0, 3.0, 2.5), siding)

# Corner trim boards.
for sx in (-1, 1):
    for sy in (-1, 1):
        add_box('CornerTrim_%d%d' % (sx, sy), (sx * 1.97, sy * 1.47, 1.55),
                (0.12, 0.12, 2.5), trim)

add_gable_roof('Roof', 2.35, -1.85, 1.85, 2.8, 4.15, shingle)
add_box('RidgeCap', (0.0, 0.0, 4.16), (4.8, 0.16, 0.10), trim)

# Gable-end trim so the roof reads as an overhanging edge.
for sx in (-1, 1):
    add_box('Fascia_%d' % sx, (sx * 2.38, 0.0, 3.45), (0.08, 3.9, 1.5), trim)

# Chimney rising out of the rear slope.
add_box('ChimneyStack', (1.35, 0.75, 3.05), (0.55, 0.55, 2.6), brick)
add_box('ChimneyCap', (1.35, 0.75, 4.40), (0.72, 0.72, 0.14), stone)

# Front porch: deck, steps, posts, railing and a shed roof.
add_box('PorchDeck', (0.0, -2.35, 0.22), (3.6, 1.9, 0.24), deck)
for i, z in enumerate((0.05, -0.05)):
    add_box('PorchStep_%d' % i, (0.0, -3.35 - i * 0.36, 0.13 - i * 0.11),
            (1.6, 0.36, 0.14 + i * 0.02), deck)

for sx in (-1, 1):
    px = sx * 1.62
    add_box('PorchPost_%d' % sx, (px, -3.15, 1.45), (0.16, 0.16, 2.4), trim)
    add_box('Railing_%d' % sx, (px, -2.35, 1.05), (0.10, 1.5, 0.10), trim)
    for k in range(4):
        add_box('Baluster_%d_%d' % (sx, k), (px, -3.0 + k * 0.45, 0.72),
                (0.06, 0.06, 0.75), trim)

add_box('PorchBeam', (0.0, -3.15, 2.62), (3.6, 0.18, 0.24), trim)
add_box('PorchRoof', (0.0, -2.55, 2.86), (3.9, 2.1, 0.14), shingle,
        rot=(-0.16, 0.0, 0.0))

# Door and windows on the porch-facing wall.
add_box('DoorFrame', (0.0, -1.52, 1.35), (1.05, 0.12, 2.15), trim)
add_box('Door', (0.0, -1.58, 1.30), (0.85, 0.06, 2.0), doorpaint)
add_box('DoorKnob', (0.30, -1.64, 1.30), (0.08, 0.06, 0.08), trim)
add_window('WindowLeft', -1.30, 1.75, trim, glass)
add_window('WindowRight', 1.30, 1.75, trim, glass)

bpy.ops.object.light_add(type='SUN', location=(6.0, -8.0, 10.0))
sun = bpy.context.object
sun.name = 'SunLight'
sun.data.energy = 3.5
sun.rotation_euler = (0.85, 0.05, -0.6)

setup_camera((0.0, -0.6, 1.9))
world = bpy.data.worlds.new('World')
world.use_nodes = True
world.node_tree.nodes['Background'].inputs[0].default_value = (0.50, 0.62, 0.80, 1.0)
bpy.context.scene.world = world
