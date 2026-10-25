import bpy
import bmesh
from math import pi, sin, cos
from mathutils import Vector

TAU = 2.0 * pi


def clear_scene():
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete(use_global=False)
    for block in (bpy.data.meshes, bpy.data.materials):
        for item in list(block):
            if item.users == 0:
                block.remove(item)


def make_material(name, color, roughness=0.5, metallic=0.0):
    mat = bpy.data.materials.new(name)
    mat.use_nodes = True
    bsdf = mat.node_tree.nodes["Principled BSDF"]
    bsdf.inputs["Base Color"].default_value = (color[0], color[1], color[2], 1.0)
    bsdf.inputs["Roughness"].default_value = roughness
    bsdf.inputs["Metallic"].default_value = metallic
    return mat


def link(name, mesh, loc, rot, mat):
    obj = bpy.data.objects.new(name, mesh)
    obj.location = loc
    obj.rotation_euler = rot
    obj.data.materials.append(mat)
    bpy.context.collection.objects.link(obj)
    return obj


def add_box(name, size, loc, mat, rot=(0.0, 0.0, 0.0), bevel=0.0):
    mesh = bpy.data.meshes.new(name)
    bm = bmesh.new()
    bmesh.ops.create_cube(bm, size=1.0)
    bmesh.ops.scale(bm, vec=Vector(size), verts=bm.verts)
    bm.to_mesh(mesh)
    bm.free()
    obj = link(name, mesh, loc, rot, mat)
    if bevel > 0.0:
        mod = obj.modifiers.new("Bevel", 'BEVEL')
        mod.width = bevel
        mod.segments = 3
        mod.limit_method = 'ANGLE'
    return obj


def add_cylinder(name, radius, depth, loc, mat, rot=(0.0, 0.0, 0.0),
                 segments=28, radius_top=None):
    mesh = bpy.data.meshes.new(name)
    bm = bmesh.new()
    bmesh.ops.create_cone(bm, cap_ends=True, cap_tris=False, segments=segments,
                          radius1=radius,
                          radius2=radius if radius_top is None else radius_top,
                          depth=depth)
    bm.to_mesh(mesh)
    bm.free()
    return link(name, mesh, loc, rot, mat)


def build_base(plastic, chrome, rubber):
    add_cylinder("Base_Hub", 0.075, 0.08, (0.0, 0.0, 0.075), plastic)
    for i in range(5):
        ang = i * TAU / 5.0
        d = Vector((cos(ang), sin(ang), 0.0))
        leg_mid = d * 0.175
        add_box("Base_Leg_%d" % (i + 1), (0.30, 0.055, 0.045),
                (leg_mid.x, leg_mid.y, 0.062), plastic,
                rot=(0.0, 0.0, ang), bevel=0.012)
        pos = d * 0.305
        add_box("Caster_Yoke_%d" % (i + 1), (0.048, 0.055, 0.055),
                (pos.x, pos.y, 0.072), plastic, rot=(0.0, 0.0, ang))
        add_cylinder("Caster_Stem_%d" % (i + 1), 0.010, 0.03,
                     (pos.x, pos.y, 0.055), chrome, segments=12)
        add_cylinder("Caster_Wheel_%d" % (i + 1), 0.033, 0.024,
                     (pos.x, pos.y, 0.033), rubber,
                     rot=(pi * 0.5, 0.0, ang), segments=24)


def build_column(chrome, plastic):
    add_cylinder("Column_Sleeve", 0.046, 0.20, (0.0, 0.0, 0.20), plastic)
    add_cylinder("Column_Piston", 0.027, 0.16, (0.0, 0.0, 0.37), chrome)
    add_cylinder("Column_Collar", 0.052, 0.02, (0.0, 0.0, 0.305), chrome, segments=20)


def build_seat(plastic, fabric, chrome):
    add_box("Seat_Mechanism", (0.20, 0.24, 0.055), (0.0, 0.0, 0.452), plastic)
    add_box("Seat_Pan", (0.46, 0.44, 0.022), (0.0, -0.01, 0.492), plastic, bevel=0.02)
    add_box("Seat_Cushion", (0.48, 0.46, 0.085), (0.0, -0.01, 0.545), fabric, bevel=0.03)
    add_cylinder("Seat_TiltLever", 0.011, 0.17, (0.20, -0.16, 0.452), chrome,
                 rot=(0.0, pi * 0.5, 0.0), segments=14)
    add_cylinder("Seat_TiltKnob", 0.020, 0.03, (0.29, -0.16, 0.452), plastic,
                 rot=(0.0, pi * 0.5, 0.0), segments=16)


def build_back(plastic, fabric):
    add_box("Back_Support_Arm", (0.07, 0.10, 0.30), (0.0, 0.20, 0.66), plastic,
            rot=(-0.22, 0.0, 0.0), bevel=0.015)
    add_box("Backrest_Frame", (0.44, 0.055, 0.44), (0.0, 0.285, 0.90), plastic,
            rot=(-0.20, 0.0, 0.0), bevel=0.02)
    add_box("Backrest_Mesh", (0.40, 0.03, 0.40), (0.0, 0.256, 0.90), fabric,
            rot=(-0.20, 0.0, 0.0), bevel=0.012)
    add_box("Backrest_Lumbar", (0.34, 0.05, 0.08), (0.0, 0.235, 0.72), fabric,
            rot=(-0.20, 0.0, 0.0), bevel=0.018)
    add_box("Headrest", (0.28, 0.06, 0.12), (0.0, 0.345, 1.17), fabric,
            rot=(-0.20, 0.0, 0.0), bevel=0.025)


def build_armrests(plastic, fabric):
    for side, tag in ((-1.0, "L"), (1.0, "R")):
        add_box("Armrest_Post_%s" % tag, (0.045, 0.065, 0.20),
                (side * 0.265, 0.055, 0.60), plastic, bevel=0.012)
        add_box("Armrest_Pad_%s" % tag, (0.075, 0.26, 0.035),
                (side * 0.265, -0.005, 0.715), fabric, bevel=0.015)


def add_camera(loc, target):
    cam = bpy.data.objects.new("Camera", bpy.data.cameras.new("Camera"))
    cam.location = loc
    cam.data.lens = 55.0
    cam.rotation_euler = (Vector(target) - Vector(loc)).to_track_quat('-Z', 'Y').to_euler()
    bpy.context.collection.objects.link(cam)
    bpy.context.scene.camera = cam


def add_light(loc, energy=4.5):
    data = bpy.data.lights.new("Sun", 'SUN')
    data.energy = energy
    obj = bpy.data.objects.new("Sun", data)
    obj.location = loc
    obj.rotation_euler = (0.55, 0.2, -0.8)
    bpy.context.collection.objects.link(obj)


clear_scene()

plastic = make_material("Plastic_Black", (0.045, 0.045, 0.05), roughness=0.45)
chrome = make_material("Metal_Chrome", (0.72, 0.73, 0.75), roughness=0.18, metallic=1.0)
rubber = make_material("Rubber_Caster", (0.10, 0.10, 0.11), roughness=0.8)
fabric = make_material("Upholstery_Grey", (0.24, 0.26, 0.30), roughness=0.85)
floorm = make_material("Floor_Wood", (0.42, 0.33, 0.24), roughness=0.6)

add_box("Floor", (5.0, 5.0, 0.06), (0.0, 0.0, -0.03), floorm)
build_base(plastic, chrome, rubber)
build_column(chrome, plastic)
build_seat(plastic, fabric, chrome)
build_back(plastic, fabric)
build_armrests(plastic, fabric)

add_light((2.0, -2.5, 4.0))
add_camera((1.55, -1.95, 1.35), (0.0, 0.05, 0.62))
