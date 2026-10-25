import bpy
import bmesh
import math
from mathutils import Vector

WIDTH, DEPTH, RISE = 9.0, 6.0, 1.6
SEG = 26
COL_R, COL_CLEAR = 0.075, 3.2
ARC_R = (WIDTH * WIDTH / 4.0 + RISE * RISE) / (2.0 * RISE)


def reset_scene():
    if bpy.context.scene.objects:
        bpy.ops.object.select_all(action='SELECT')
        bpy.ops.object.delete(use_global=False)
    for coll in (bpy.data.meshes, bpy.data.materials, bpy.data.cameras, bpy.data.lights):
        for block in list(coll):
            coll.remove(block)


def make_material(name, color, roughness=0.5, metallic=0.0, alpha=1.0):
    mat = bpy.data.materials.new(name)
    mat.use_nodes = True
    bsdf = mat.node_tree.nodes["Principled BSDF"]
    bsdf.inputs["Base Color"].default_value = (color[0], color[1], color[2], 1.0)
    bsdf.inputs["Roughness"].default_value = roughness
    bsdf.inputs["Metallic"].default_value = metallic
    if alpha < 1.0:
        bsdf.inputs["Alpha"].default_value = alpha
        mat.blend_method = 'BLEND'
    return mat


def roof_z(x):
    """Underside height of the circular-arc roof at cross-section position x."""
    return math.sqrt(max(ARC_R * ARC_R - x * x, 0.0)) - (ARC_R - RISE) + COL_CLEAR


def add_box(name, size, location, material, rotation=(0, 0, 0)):
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=location, rotation=rotation)
    ob = bpy.context.active_object
    ob.name = name
    ob.scale = size
    ob.data.materials.append(material)
    return ob


def add_column(name, location, height, material):
    bpy.ops.mesh.primitive_cylinder_add(vertices=16, radius=COL_R, depth=height,
                                        location=(location[0], location[1], height / 2.0))
    ob = bpy.context.active_object
    ob.name = name
    ob.data.materials.append(material)
    return ob


def build_roof(material):
    bm = bmesh.new()
    rows = []
    for y in (-DEPTH / 2.0, DEPTH / 2.0):
        row = []
        for i in range(SEG + 1):
            x = -WIDTH / 2.0 + WIDTH * i / SEG
            row.append(bm.verts.new((x, y, roof_z(x))))
        rows.append(row)
    for i in range(SEG):
        bm.faces.new((rows[0][i], rows[0][i + 1], rows[1][i + 1], rows[1][i]))
    bm.normal_update()
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    me = bpy.data.meshes.new("PavilionRoof")
    bm.to_mesh(me)
    bm.free()
    ob = bpy.data.objects.new("PavilionRoof", me)
    bpy.context.collection.objects.link(ob)
    ob.data.materials.append(material)
    solid = ob.modifiers.new("Shell", 'SOLIDIFY')
    solid.thickness = 0.18
    solid.offset = 1.0
    return ob


def add_camera(location, target, lens=42.0):
    cam_data = bpy.data.cameras.new("Camera")
    cam_data.lens = lens
    cam = bpy.data.objects.new("Camera", cam_data)
    bpy.context.collection.objects.link(cam)
    cam.location = location
    cam.rotation_euler = (Vector(target) - Vector(location)).to_track_quat('-Z', 'Y').to_euler()
    bpy.context.scene.camera = cam
    return cam


reset_scene()

m_deck = make_material("DeckStone", (0.72, 0.70, 0.66), roughness=0.7)
m_metal = make_material("BrushedSteel", (0.78, 0.79, 0.81), roughness=0.32, metallic=1.0)
m_roof = make_material("RoofPanel", (0.88, 0.88, 0.86), roughness=0.45, metallic=0.2)
m_glass = make_material("GlassPanel", (0.58, 0.72, 0.75), roughness=0.08, alpha=0.28)
m_wood = make_material("BenchOak", (0.55, 0.36, 0.19), roughness=0.6)
m_ground = make_material("Ground", (0.36, 0.42, 0.32), roughness=0.9)

bpy.ops.mesh.primitive_plane_add(size=40.0, location=(0, 0, -0.001))
ground = bpy.context.active_object
ground.name = "Ground"
ground.data.materials.append(m_ground)

add_box("Deck", (WIDTH + 1.4, DEPTH + 1.4, 0.24), (0, 0, 0.12), m_deck)
add_box("Step", (WIDTH + 2.6, 1.0, 0.12), (0, -(DEPTH / 2.0 + 1.2), 0.06), m_deck)

col_x = WIDTH / 2.0 - 0.55
for row, x in enumerate((-col_x, col_x)):
    for col in range(4):
        y = -DEPTH / 2.0 + 0.7 + col * (DEPTH - 1.4) / 3.0
        add_column("Column_%d_%d" % (row, col), (x, y), roof_z(x), m_metal)
    add_box("EdgeBeam_%d" % row, (0.16, DEPTH, 0.22),
            (x, 0.0, roof_z(x) - 0.15), m_metal)

build_roof(m_roof)

add_box("BackGlass", (WIDTH - 1.4, 0.05, 2.4),
        (0.0, DEPTH / 2.0 - 0.55, 0.24 + 1.2), m_glass)
for side in (-1, 1):
    add_box("Bench_%d" % (side + 1), (2.6, 0.5, 0.1),
            (side * 2.0, -1.4, 0.24 + 0.44), m_wood)
    add_box("BenchLeg_%d" % (side + 1), (0.1, 0.44, 0.4),
            (side * 2.0, -1.4, 0.24 + 0.2), m_metal)

sun_data = bpy.data.lights.new("Sun", type='SUN')
sun_data.energy = 4.0
sun = bpy.data.objects.new("Sun", sun_data)
bpy.context.collection.objects.link(sun)
sun.location = (6.0, -8.0, 12.0)
sun.rotation_euler = (math.radians(52), 0.0, math.radians(38))

add_camera((13.0, -13.5, 7.2), (0.0, 0.0, 2.2))
