import bpy
import bmesh
import random
from mathutils import Vector

random.seed(7)

# ---------------------------------------------------------------- helpers

def clear_scene():
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete(use_global=False)


def make_material(name, color, roughness=0.5, metallic=0.0, alpha=1.0):
    mat = bpy.data.materials.new(name)
    mat.use_nodes = True
    bsdf = mat.node_tree.nodes["Principled BSDF"]
    bsdf.inputs["Base Color"].default_value = (*color, alpha)
    bsdf.inputs["Roughness"].default_value = roughness
    bsdf.inputs["Metallic"].default_value = metallic
    bsdf.inputs["Alpha"].default_value = alpha
    if alpha < 1.0:
        bsdf.inputs["Transmission Weight"].default_value = 0.85
        if hasattr(mat, "surface_render_method"):
            mat.surface_render_method = 'BLENDED'
        if hasattr(mat, "blend_method"):
            mat.blend_method = 'BLEND'
    return mat


def new_object(name, mesh, location, material, rotation=(0.0, 0.0, 0.0)):
    obj = bpy.data.objects.new(name, mesh)
    obj.location = location
    obj.rotation_euler = rotation
    obj.data.materials.append(material)
    bpy.context.collection.objects.link(obj)
    return obj


def add_box(name, size, location, material, rotation=(0.0, 0.0, 0.0), bevel=0.0):
    mesh = bpy.data.meshes.new(name)
    bm = bmesh.new()
    bmesh.ops.create_cube(bm, size=1.0)
    bmesh.ops.scale(bm, vec=Vector(size), verts=bm.verts)
    if bevel > 0.0:
        bmesh.ops.bevel(bm, geom=list(bm.verts) + list(bm.edges) + list(bm.faces),
                        offset=bevel, segments=2, affect='EDGES')
    bm.to_mesh(mesh)
    bm.free()
    return new_object(name, mesh, location, material, rotation)


def add_cylinder(name, radius, height, location, material, segments=20, top_radius=None):
    mesh = bpy.data.meshes.new(name)
    bm = bmesh.new()
    bmesh.ops.create_cone(bm, cap_ends=True, cap_tris=False, segments=segments,
                          radius1=radius,
                          radius2=radius if top_radius is None else top_radius,
                          depth=height)
    bm.to_mesh(mesh)
    bm.free()
    return new_object(name, mesh, location, material)


def aim(obj, target):
    obj.rotation_euler = (Vector(target) - obj.location).to_track_quat('-Z', 'Y').to_euler()


# ---------------------------------------------------------------- materials

clear_scene()

mat_floor = make_material("MAT_Floor_Tile", (0.62, 0.60, 0.57), roughness=0.35)
mat_wall = make_material("MAT_Wall", (0.86, 0.84, 0.79), roughness=0.85)
mat_body = make_material("MAT_Counter_Body", (0.20, 0.24, 0.30), roughness=0.55)
mat_top = make_material("MAT_Counter_Top", (0.90, 0.88, 0.84), roughness=0.20)
mat_wood = make_material("MAT_Shelf_Wood", (0.46, 0.30, 0.16), roughness=0.6)
mat_metal = make_material("MAT_Metal_Trim", (0.75, 0.76, 0.78), roughness=0.3, metallic=1.0)
mat_glass = make_material("MAT_Display_Glass", (0.80, 0.88, 0.90), roughness=0.05, alpha=0.16)
mat_screen = make_material("MAT_Register_Screen", (0.06, 0.07, 0.09), roughness=0.25)

product_mats = [make_material("MAT_Product_%d" % i, col, roughness=r) for i, (col, r) in enumerate([
    ((0.72, 0.14, 0.12), 0.45),
    ((0.15, 0.45, 0.72), 0.40),
    ((0.90, 0.72, 0.18), 0.50),
    ((0.20, 0.55, 0.28), 0.45),
    ((0.85, 0.85, 0.88), 0.30),
    ((0.48, 0.22, 0.55), 0.50),
])]

# ---------------------------------------------------------------- room shell

add_box("Floor", (7.0, 5.0, 0.10), (0.0, 0.0, -0.05), mat_floor)
add_box("Back_Wall", (7.0, 0.12, 3.0), (0.0, 2.0, 1.5), mat_wall)
add_box("Side_Wall", (0.12, 5.0, 3.0), (-3.5, 0.0, 1.5), mat_wall)

# ---------------------------------------------------------------- counter

CW, CD, CH = 3.4, 0.75, 1.05
add_box("Counter_Body", (CW, CD, CH - 0.12), (0.0, -0.6, (CH - 0.12) / 2 + 0.12), mat_body)
add_box("Counter_Kickplate", (CW - 0.1, CD - 0.12, 0.12), (0.0, -0.6, 0.06), mat_metal)
add_box("Counter_Top", (CW + 0.12, CD + 0.14, 0.06), (0.0, -0.62, CH + 0.03), mat_top, bevel=0.015)

# customer-side glass display front with two product tiers inside
add_box("Counter_Glass_Front", (CW - 0.2, 0.02, 0.62),
        (0.0, -0.6 - CD / 2 + 0.01, 0.68), mat_glass)
for i in range(2):
    z = 0.45 + i * 0.30
    add_box("Counter_Display_Shelf_%d" % i, (CW - 0.3, CD - 0.22, 0.03), (0.0, -0.62, z), mat_top)
    for j in range(6):
        x = -CW / 2 + 0.35 + j * (CW - 0.7) / 5.0
        mat = product_mats[(i * 3 + j) % len(product_mats)]
        if j % 2 == 0:
            add_box("Case_Item_%d_%d" % (i, j), (0.16, 0.20, 0.10),
                    (x, -0.62, z + 0.065), mat, rotation=(0.0, 0.0, random.uniform(-0.3, 0.3)))
        else:
            add_cylinder("Case_Jar_%d_%d" % (i, j), 0.07, 0.16, (x, -0.62, z + 0.095), mat, segments=16)

# ---------------------------------------------------------------- till area

add_box("Register_Base", (0.42, 0.34, 0.14), (1.05, -0.62, CH + 0.13), mat_screen, bevel=0.01)
add_box("Register_Screen", (0.40, 0.03, 0.26), (1.05, -0.48, CH + 0.33), mat_screen,
        rotation=(-0.22, 0.0, 0.0))
add_box("Card_Terminal", (0.12, 0.18, 0.05), (0.55, -0.85, CH + 0.09), mat_metal,
        rotation=(-0.15, 0.0, 0.2))
add_cylinder("Counter_Bowl", 0.13, 0.09, (-1.15, -0.80, CH + 0.10), mat_metal, top_radius=0.16)
for i in range(4):
    add_cylinder("Impulse_Can_%d" % i, 0.045, 0.13,
                 (-0.75 + i * 0.13, -0.45, CH + 0.115), product_mats[i % len(product_mats)], segments=14)

# ---------------------------------------------------------------- back shelving

SW, SD = 4.2, 0.40
SHELF_Z = [0.35, 0.80, 1.25, 1.70, 2.15]
add_box("Shelf_Backboard", (SW, 0.04, 2.35), (0.0, 1.90, 1.20), mat_wood)
for i, x in enumerate((-SW / 2, -SW / 6, SW / 6, SW / 2)):
    add_box("Shelf_Upright_%d" % i, (0.05, SD, 2.35), (x, 1.90 - SD / 2 - 0.02, 1.20), mat_wood)
for i, z in enumerate(SHELF_Z):
    add_box("Shelf_Board_%d" % i, (SW, SD, 0.04), (0.0, 1.90 - SD / 2 - 0.02, z), mat_wood)
    add_box("Shelf_Lip_%d" % i, (SW, 0.02, 0.05), (0.0, 1.90 - SD - 0.02, z + 0.045), mat_metal)

    # stock the shelf: alternating boxed goods, bottles and canned rows
    kind = i % 3
    count = 11 if kind else 9
    for j in range(count):
        x = -SW / 2 + 0.28 + j * (SW - 0.56) / (count - 1)
        y = 1.90 - SD / 2 - 0.02
        mat = product_mats[(i * 2 + j) % len(product_mats)]
        if kind == 0:
            add_box("Stock_Box_%d_%d" % (i, j), (0.20, 0.22, 0.28), (x, y, z + 0.16), mat,
                    rotation=(0.0, 0.0, random.uniform(-0.12, 0.12)))
        elif kind == 1:
            add_cylinder("Stock_Bottle_%d_%d" % (i, j), 0.055, 0.26, (x, y, z + 0.15), mat, segments=14)
            add_cylinder("Stock_Bottle_Neck_%d_%d" % (i, j), 0.022, 0.08, (x, y, z + 0.32),
                         mat_metal, segments=10)
        else:
            add_cylinder("Stock_Can_%d_%d" % (i, j), 0.05, 0.14, (x, y, z + 0.09), mat, segments=14)
            add_cylinder("Stock_Can_Top_%d_%d" % (i, j), 0.05, 0.14, (x, y - 0.14, z + 0.09),
                         mat, segments=14)

add_box("Shelf_Header_Sign", (2.2, 0.06, 0.34), (0.0, 1.84, 2.55), mat_body, bevel=0.02)

# ---------------------------------------------------------------- lighting

for i, x in enumerate((-1.6, 1.6)):
    strip = bpy.data.lights.new("Strip_%d" % i, type='AREA')
    strip.energy = 320.0
    strip.shape = 'RECTANGLE'
    strip.size, strip.size_y = 2.6, 0.25
    obj = bpy.data.objects.new("Ceiling_Strip_%d" % i, strip)
    obj.location = (x, 0.3, 2.85)
    bpy.context.collection.objects.link(obj)
    aim(obj, (x, 0.3, 0.0))

key = bpy.data.lights.new("Key", type='AREA')
key.energy = 250.0
key.size = 3.0
key_obj = bpy.data.objects.new("Key_Area", key)
key_obj.location = (2.4, -4.2, 2.6)
bpy.context.collection.objects.link(key_obj)
aim(key_obj, (0.0, 0.2, 1.1))

# ---------------------------------------------------------------- camera

cam_data = bpy.data.cameras.new("ShopCam")
cam_data.lens = 32.0
cam = bpy.data.objects.new("Camera", cam_data)
cam.location = (3.8, -4.6, 2.3)
bpy.context.collection.objects.link(cam)
aim(cam, (-0.15, 0.45, 1.15))
bpy.context.scene.camera = cam
