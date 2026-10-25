import bpy
import bmesh
import math
import random
from mathutils import Vector, Matrix

random.seed(7)


def clear_scene():
    for obj in list(bpy.data.objects):
        bpy.data.objects.remove(obj, do_unlink=True)
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


def add_box(name, center, size, material, rotation=(0.0, 0.0, 0.0)):
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=center, rotation=rotation)
    obj = bpy.context.active_object
    obj.name = name
    obj.scale = size
    obj.data.materials.append(material)
    return obj


def add_cylinder(name, center, radius, height, material, rotation=(0.0, 0.0, 0.0)):
    bpy.ops.mesh.primitive_cylinder_add(vertices=16, radius=radius, depth=height,
                                        location=center, rotation=rotation)
    obj = bpy.context.active_object
    obj.name = name
    obj.data.materials.append(material)
    return obj


def build_crate(name, location, material, size=(0.62, 0.44, 0.26), slat=0.028):
    """Open-topped slatted crate: floor plus four thin walls in a single mesh."""
    sx, sy, sz = size
    bm = bmesh.new()

    def slab(cx, cy, cz, dx, dy, dz):
        m = Matrix.Translation((cx, cy, cz)) @ Matrix.Diagonal((dx, dy, dz, 1.0))
        bmesh.ops.create_cube(bm, size=1.0, matrix=m)

    slab(0.0, 0.0, slat * 0.5, sx, sy, slat)
    for sign in (-1, 1):
        slab(0.0, sign * (sy - slat) * 0.5, sz * 0.5, sx, slat, sz)
        slab(sign * (sx - slat) * 0.5, 0.0, sz * 0.5, slat, sy, sz)
    for sign in (-1, 1):                                  # corner uprights
        for sgn2 in (-1, 1):
            slab(sign * (sx - slat) * 0.5, sgn2 * (sy - slat) * 0.5,
                 sz * 0.5, slat * 2.0, slat * 2.0, sz * 1.06)
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)

    me = bpy.data.meshes.new(name)
    bm.to_mesh(me)
    bm.free()
    obj = bpy.data.objects.new(name, me)
    bpy.context.collection.objects.link(obj)
    obj.location = location
    obj.data.materials.append(material)
    return obj


def fill_produce(prefix, crate_loc, material, radius=0.055, size=(0.62, 0.44, 0.26)):
    sx, sy, _ = size
    cols, rows = 4, 3
    for iy in range(rows):
        for ix in range(cols):
            x = crate_loc[0] + (ix - (cols - 1) * 0.5) * (sx - 0.1) / (cols - 1)
            y = crate_loc[1] + (iy - (rows - 1) * 0.5) * (sy - 0.1) / (rows - 1)
            z = crate_loc[2] + size[2] - radius * 0.6 + random.uniform(-0.01, 0.02)
            bpy.ops.mesh.primitive_ico_sphere_add(
                subdivisions=2, radius=radius * random.uniform(0.85, 1.1),
                location=(x + random.uniform(-0.015, 0.015),
                          y + random.uniform(-0.015, 0.015), z))
            fruit = bpy.context.active_object
            fruit.name = "%s_%d_%d" % (prefix, iy + 1, ix + 1)
            fruit.data.materials.append(material)


def add_camera(location, target, lens=42.0):
    cam = bpy.data.objects.new("Camera", bpy.data.cameras.new("Camera"))
    bpy.context.collection.objects.link(cam)
    cam.location = location
    cam.data.lens = lens
    cam.rotation_euler = (Vector(target) - Vector(location)).to_track_quat('-Z', 'Y').to_euler()
    bpy.context.scene.camera = cam
    return cam


clear_scene()

m_ground = make_material("Ground_Cobble", (0.28, 0.27, 0.25), roughness=0.85)
m_wood = make_material("Wood_Pine", (0.58, 0.40, 0.22), roughness=0.65)
m_wood_dark = make_material("Wood_Weathered", (0.35, 0.25, 0.16), roughness=0.75)
m_metal = make_material("Steel_Pole", (0.55, 0.56, 0.58), roughness=0.4, metallic=0.85)
m_stripe_a = make_material("Canvas_Red", (0.62, 0.10, 0.10), roughness=0.75)
m_stripe_b = make_material("Canvas_Cream", (0.92, 0.89, 0.80), roughness=0.75)
m_sign = make_material("Sign_Board", (0.14, 0.16, 0.14), roughness=0.7)
m_apple = make_material("Produce_Apple", (0.68, 0.09, 0.08), roughness=0.35)
m_orange = make_material("Produce_Orange", (0.85, 0.42, 0.05), roughness=0.45)
m_cabbage = make_material("Produce_Cabbage", (0.34, 0.56, 0.20), roughness=0.55)
m_plum = make_material("Produce_Plum", (0.28, 0.12, 0.34), roughness=0.4)

STALL_X, STALL_Y = 3.0, 1.8
POST_H = 2.35
EAVE_Z, RIDGE_Z = 2.15, 2.6

add_box("Ground", (0.0, 0.0, -0.03), (16.0, 16.0, 0.06), m_ground)

for i, (sx, sy) in enumerate(((-1, -1), (1, -1), (-1, 1), (1, 1))):
    add_cylinder("Stall_Post_%d" % (i + 1),
                 (sx * STALL_X * 0.5, sy * STALL_Y * 0.5, POST_H * 0.5),
                 0.045, POST_H, m_metal)

for i, sy in enumerate((-1, 1)):
    add_box("Stall_Beam_Side_%d" % (i + 1),
            (0.0, sy * STALL_Y * 0.5, EAVE_Z), (STALL_X + 0.1, 0.06, 0.06), m_metal)
add_box("Stall_Ridge_Bar", (0.0, 0.0, RIDGE_Z), (STALL_X + 0.3, 0.07, 0.07), m_metal)
for i, sx in enumerate((-1, 1)):
    add_box("Canopy_Gable_%d" % (i + 1), (sx * STALL_X * 0.5, 0.0, RIDGE_Z - 0.06),
            (0.05, 0.09, 0.09), m_metal)

# Striped gable canopy: each slope is a run of alternating strips.
STRIPS = 12
strip_w = (STALL_X + 0.34) / STRIPS
for side_i, sy in enumerate((-1, 1)):
    dy = sy * (STALL_Y * 0.5 + 0.22)
    dz = EAVE_Z - RIDGE_Z
    slope_len = math.hypot(dy, dz)
    angle = math.atan2(dz, dy)
    mid = (0.0, dy * 0.5, RIDGE_Z + dz * 0.5)
    for i in range(STRIPS):
        cx = -(STALL_X + 0.34) * 0.5 + strip_w * (i + 0.5)
        strip = add_box("Canopy_Strip_%d_%d" % (side_i + 1, i + 1),
                        (cx, mid[1], mid[2]),
                        (strip_w * 0.98, slope_len, 0.02),
                        m_stripe_a if i % 2 == 0 else m_stripe_b,
                        rotation=(angle, 0.0, 0.0))
        strip.rotation_euler = (angle, 0.0, 0.0)
    add_box("Canopy_Valance_%d" % (side_i + 1),
            (0.0, dy, EAVE_Z - 0.13), (STALL_X + 0.34, 0.02, 0.26),
            m_stripe_a if side_i == 0 else m_stripe_b)

COUNTER_Z = 0.92
add_box("Counter_Top", (0.0, -STALL_Y * 0.5 + 0.42, COUNTER_Z),
        (STALL_X - 0.2, 0.78, 0.05), m_wood)
add_box("Counter_Front_Panel", (0.0, -STALL_Y * 0.5 + 0.04, COUNTER_Z * 0.5),
        (STALL_X - 0.2, 0.04, COUNTER_Z - 0.05), m_wood_dark)
for i, sx in enumerate((-1, 1)):
    add_box("Counter_Leg_%d" % (i + 1),
            (sx * (STALL_X * 0.5 - 0.2), -STALL_Y * 0.5 + 0.72, COUNTER_Z * 0.5),
            (0.07, 0.07, COUNTER_Z), m_wood_dark)
add_box("Counter_Shelf", (0.0, -STALL_Y * 0.5 + 0.55, 0.34),
        (STALL_X - 0.4, 0.6, 0.04), m_wood_dark)

CRATE = (0.62, 0.44, 0.26)
produce = ((m_apple, "Apple"), (m_orange, "Orange"), (m_cabbage, "Cabbage"), (m_plum, "Plum"))
for i in range(4):
    loc = (-0.99 + i * 0.66, -STALL_Y * 0.5 + 0.42, COUNTER_Z + 0.03)
    tilt = math.radians(-9.0)
    crate = build_crate("Crate_Counter_%d" % (i + 1), loc, m_wood, size=CRATE)
    crate.rotation_euler = (tilt, 0.0, 0.0)
    mat_p, tag = produce[i]
    fill_produce("Produce_%s" % tag, (loc[0], loc[1] + 0.02, loc[2] + 0.02), mat_p, size=CRATE)

for i in range(3):
    z = 0.13 + i * 0.27
    loc = (STALL_X * 0.5 - 0.55, 0.42 + i * 0.03, z)
    stack = build_crate("Crate_Stack_%d" % (i + 1), loc, m_wood_dark, size=CRATE)
    stack.rotation_euler = (0.0, 0.0, math.radians(6.0 * i))
fill_produce("Produce_Stack_Apple", (STALL_X * 0.5 - 0.55, 0.48, 0.13 + 2 * 0.27 + 0.02),
             m_apple, size=CRATE)

spare = build_crate("Crate_Spare", (-STALL_X * 0.5 + 0.45, 0.5, 0.13), m_wood, size=CRATE)
spare.rotation_euler = (0.0, 0.0, math.radians(-22.0))
fill_produce("Produce_Cabbage_Spare", (-STALL_X * 0.5 + 0.45, 0.5, 0.15), m_cabbage, size=CRATE)

add_box("Sign_Board", (0.0, -STALL_Y * 0.5 - 0.24, 1.72), (1.5, 0.04, 0.34), m_sign)
for i, sx in enumerate((-1, 1)):
    add_cylinder("Sign_Hanger_%d" % (i + 1),
                 (sx * 0.6, -STALL_Y * 0.5 - 0.13, 1.95), 0.012, 0.42, m_metal,
                 rotation=(math.radians(-28.0), 0.0, 0.0))
add_cylinder("Hanging_Scale_Hook", (STALL_X * 0.5 - 0.35, -0.2, 1.85), 0.014, 0.55, m_metal)
add_cylinder("Hanging_Scale_Pan", (STALL_X * 0.5 - 0.35, -0.2, 1.55), 0.18, 0.05, m_metal)

sun = bpy.data.objects.new("Sun", bpy.data.lights.new("Sun", 'SUN'))
bpy.context.collection.objects.link(sun)
sun.data.energy = 3.5
sun.location = (4.0, -6.0, 8.0)
sun.rotation_euler = (math.radians(48.0), 0.0, math.radians(-30.0))

fill = bpy.data.objects.new("Fill_Light", bpy.data.lights.new("Fill_Light", 'AREA'))
bpy.context.collection.objects.link(fill)
fill.data.energy = 180.0
fill.data.size = 3.0
fill.location = (-2.5, -4.0, 2.6)
fill.rotation_euler = (math.radians(65.0), 0.0, math.radians(-35.0))

add_camera((4.4, -5.6, 2.5), (0.0, -0.3, 1.35))
