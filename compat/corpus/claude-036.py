# claude-036: A computer monitor on an articulated desk mount
# Blender 4.5 LTS -- builds the scene only (no render, no file output).

import bpy
import bmesh
import math
from mathutils import Vector, Matrix

TAU = math.tau
D2R = math.radians


# ----------------------------------------------------------------------------
# scene bootstrap
# ----------------------------------------------------------------------------

def reset_scene():
    bpy.ops.wm.read_factory_settings(use_empty=True)
    scene = bpy.context.scene
    scene.unit_settings.system = 'METRIC'
    scene.unit_settings.length_unit = 'METERS'
    try:
        scene.render.engine = 'BLENDER_EEVEE_NEXT'
    except TypeError:
        scene.render.engine = 'CYCLES'
    scene.render.resolution_x = 1920
    scene.render.resolution_y = 1200


def new_collection(name):
    col = bpy.data.collections.new(name)
    bpy.context.scene.collection.children.link(col)
    return col


# ----------------------------------------------------------------------------
# material helpers
# ----------------------------------------------------------------------------

def set_input(node, name, value):
    """Tolerant socket setter -- socket names shift between versions."""
    sock = node.inputs.get(name)
    if sock is None:
        return False
    try:
        sock.default_value = value
    except (TypeError, ValueError):
        return False
    return True


def simple_material(name, color, roughness=0.5, metallic=0.0,
                    emission=None, emission_strength=0.0, ior=1.45):
    mat = bpy.data.materials.new(name)
    mat.use_nodes = True
    bsdf = mat.node_tree.nodes.get("Principled BSDF")
    set_input(bsdf, "Base Color", (color[0], color[1], color[2], 1.0))
    set_input(bsdf, "Roughness", roughness)
    set_input(bsdf, "Metallic", metallic)
    set_input(bsdf, "IOR", ior)
    if emission is not None:
        set_input(bsdf, "Emission Color", (emission[0], emission[1], emission[2], 1.0))
        set_input(bsdf, "Emission Strength", emission_strength)
    return mat


def screen_material():
    """Emissive desktop-ish gradient driven by object coordinates."""
    mat = bpy.data.materials.new("Screen_Image")
    mat.use_nodes = True
    nt = mat.node_tree
    nt.nodes.clear()

    out = nt.nodes.new("ShaderNodeOutputMaterial")
    out.location = (620, 0)
    bsdf = nt.nodes.new("ShaderNodeBsdfPrincipled")
    bsdf.location = (330, 0)
    set_input(bsdf, "Base Color", (0.008, 0.008, 0.010, 1.0))
    set_input(bsdf, "Roughness", 0.14)
    set_input(bsdf, "Metallic", 0.0)
    set_input(bsdf, "Emission Strength", 3.2)

    coord = nt.nodes.new("ShaderNodeTexCoord")
    coord.location = (-620, 0)
    mapping = nt.nodes.new("ShaderNodeMapping")
    mapping.location = (-430, 0)
    mapping.inputs["Location"].default_value = (0.5, 0.0, 0.5)
    mapping.inputs["Rotation"].default_value = (0.0, D2R(38.0), 0.0)
    mapping.inputs["Scale"].default_value = (1.0 / 0.62, 1.0, 1.0 / 0.62)

    grad = nt.nodes.new("ShaderNodeTexGradient")
    grad.location = (-240, 0)
    grad.gradient_type = 'LINEAR'

    ramp = nt.nodes.new("ShaderNodeValToRGB")
    ramp.location = (-40, 0)
    el = ramp.color_ramp.elements
    el[0].position = 0.0
    el[0].color = (0.012, 0.035, 0.130, 1.0)
    el[1].position = 1.0
    el[1].color = (0.380, 0.140, 0.520, 1.0)
    mid = ramp.color_ramp.elements.new(0.52)
    mid.color = (0.060, 0.220, 0.520, 1.0)

    nt.links.new(coord.outputs["Object"], mapping.inputs["Vector"])
    nt.links.new(mapping.outputs["Vector"], grad.inputs["Vector"])
    nt.links.new(grad.outputs["Color"], ramp.inputs["Fac"])
    nt.links.new(ramp.outputs["Color"], bsdf.inputs["Emission Color"])
    nt.links.new(bsdf.outputs["BSDF"], out.inputs["Surface"])
    return mat


def wood_material():
    mat = bpy.data.materials.new("Desk_Wood")
    mat.use_nodes = True
    nt = mat.node_tree
    bsdf = nt.nodes.get("Principled BSDF")
    set_input(bsdf, "Roughness", 0.42)

    coord = nt.nodes.new("ShaderNodeTexCoord")
    coord.location = (-800, -150)
    mapping = nt.nodes.new("ShaderNodeMapping")
    mapping.location = (-620, -150)
    mapping.inputs["Scale"].default_value = (1.0, 26.0, 1.0)

    noise = nt.nodes.new("ShaderNodeTexNoise")
    noise.location = (-440, -150)
    set_input(noise, "Scale", 9.0)
    set_input(noise, "Detail", 6.0)
    set_input(noise, "Roughness", 0.55)

    ramp = nt.nodes.new("ShaderNodeValToRGB")
    ramp.location = (-250, -150)
    ramp.color_ramp.elements[0].position = 0.35
    ramp.color_ramp.elements[0].color = (0.150, 0.077, 0.038, 1.0)
    ramp.color_ramp.elements[1].position = 0.68
    ramp.color_ramp.elements[1].color = (0.320, 0.185, 0.098, 1.0)

    bump = nt.nodes.new("ShaderNodeBump")
    bump.location = (-60, -330)
    set_input(bump, "Strength", 0.08)

    nt.links.new(coord.outputs["Object"], mapping.inputs["Vector"])
    nt.links.new(mapping.outputs["Vector"], noise.inputs["Vector"])
    nt.links.new(noise.outputs["Fac"], ramp.inputs["Fac"])
    nt.links.new(ramp.outputs["Color"], bsdf.inputs["Base Color"])
    nt.links.new(noise.outputs["Fac"], bump.inputs["Height"])
    nt.links.new(bump.outputs["Normal"], bsdf.inputs["Normal"])
    return mat


# ----------------------------------------------------------------------------
# mesh helpers
# ----------------------------------------------------------------------------

def _bevel(bm, width, segments):
    if width <= 0.0:
        return
    geom = list(bm.verts) + list(bm.edges) + list(bm.faces)
    bmesh.ops.bevel(bm, geom=geom, offset=width, offset_type='OFFSET',
                    segments=segments, profile=0.5, affect='EDGES',
                    clamp_overlap=True, loop_slide=True)


def _to_object(coll, name, bm, matrix, mat, smooth):
    me = bpy.data.meshes.new(name)
    bm.normal_update()
    bm.to_mesh(me)
    bm.free()
    obj = bpy.data.objects.new(name, me)
    coll.objects.link(obj)
    obj.matrix_world = matrix.copy()
    if mat is not None:
        obj.data.materials.append(mat)
    if smooth:
        for poly in me.polygons:
            poly.use_smooth = True
        es = obj.modifiers.new("Smooth", 'EDGE_SPLIT')
        es.split_angle = D2R(40.0)
    return obj


def add_box(coll, name, size, matrix=None, mat=None, bevel=0.0, segments=2,
            smooth=False):
    bm = bmesh.new()
    scale = Matrix.Diagonal(Vector((size[0], size[1], size[2], 1.0)))
    bmesh.ops.create_cube(bm, size=1.0, matrix=scale)
    _bevel(bm, bevel, segments)
    return _to_object(coll, name, bm, matrix or Matrix.Identity(4), mat,
                      smooth or bevel > 0.0)


def add_cylinder(coll, name, radius, depth, matrix=None, mat=None, verts=32,
                 bevel=0.0, caps=True):
    bm = bmesh.new()
    bmesh.ops.create_cone(bm, cap_ends=caps, cap_tris=False, segments=verts,
                          radius1=radius, radius2=radius, depth=depth,
                          matrix=Matrix.Identity(4))
    _bevel(bm, bevel, 2)
    return _to_object(coll, name, bm, matrix or Matrix.Identity(4), mat, True)


def add_sphere(coll, name, radius, matrix=None, mat=None, u=28, v=14):
    bm = bmesh.new()
    try:
        bmesh.ops.create_uvsphere(bm, u_segments=u, v_segments=v, radius=radius)
    except TypeError:
        bmesh.ops.create_uvsphere(bm, u_segments=u, v_segments=v,
                                  diameter=radius)
    return _to_object(coll, name, bm, matrix or Matrix.Identity(4), mat, True)


def T(x, y, z):
    return Matrix.Translation(Vector((x, y, z)))


def rot_x(a):
    return Matrix.Rotation(a, 4, 'X')


def rot_y(a):
    return Matrix.Rotation(a, 4, 'Y')


def rot_z(a):
    return Matrix.Rotation(a, 4, 'Z')


def segment_matrix(p0, p1):
    """Local +Y runs from p0 to p1 (all motion stays in the YZ plane)."""
    d = p1 - p0
    angle = math.atan2(d.z, d.y)
    return Matrix.Translation((p0 + p1) * 0.5) @ rot_x(angle)


# ----------------------------------------------------------------------------
# materials
# ----------------------------------------------------------------------------

reset_scene()

MAT_SHELL = simple_material("Monitor_Shell", (0.055, 0.056, 0.060), 0.44)
MAT_BEZEL = simple_material("Monitor_Bezel", (0.018, 0.018, 0.020), 0.30)
MAT_SCREEN = screen_material()
MAT_ALU = simple_material("Mount_Aluminium", (0.640, 0.650, 0.665), 0.30,
                          metallic=1.0)
MAT_DARKMET = simple_material("Mount_DarkMetal", (0.070, 0.072, 0.078), 0.38,
                              metallic=0.85)
MAT_PLASTIC = simple_material("Mount_Plastic", (0.030, 0.030, 0.033), 0.55)
MAT_RUBBER = simple_material("Rubber", (0.022, 0.022, 0.024), 0.88)
MAT_CABLE = simple_material("Cable", (0.030, 0.030, 0.032), 0.62)
MAT_LED = simple_material("Power_LED", (0.02, 0.05, 0.03), 0.25,
                          emission=(0.10, 1.0, 0.35), emission_strength=12.0)
MAT_WOOD = wood_material()
MAT_FLOOR = simple_material("Floor", (0.105, 0.100, 0.098), 0.72)
MAT_WALL = simple_material("Wall", (0.360, 0.372, 0.395), 0.92)
MAT_KEYCAP = simple_material("Keycap", (0.048, 0.048, 0.052), 0.60)

COL_ROOM = new_collection("Room")
COL_DESK = new_collection("Desk")
COL_MOUNT = new_collection("Mount")
COL_MONITOR = new_collection("Monitor")
COL_LIGHTS = new_collection("Lighting")


# ----------------------------------------------------------------------------
# room + desk
# ----------------------------------------------------------------------------

DESK_TOP_Z = 0.0
DESK_THICK = 0.030
DESK_W = 1.80
DESK_D = 0.90
FLOOR_Z = -0.735

add_box(COL_ROOM, "Floor", (7.0, 7.0, 0.02), T(0.0, 0.0, FLOOR_Z - 0.01),
        MAT_FLOOR)
add_box(COL_ROOM, "Wall_Back", (7.0, 0.03, 3.0), T(0.0, 0.78, FLOOR_Z + 1.5),
        MAT_WALL)
add_box(COL_ROOM, "Wall_Side", (0.03, 7.0, 3.0), T(-2.4, 0.0, FLOOR_Z + 1.5),
        MAT_WALL)

add_box(COL_DESK, "Desk_Top", (DESK_W, DESK_D, DESK_THICK),
        T(0.0, 0.0, DESK_TOP_Z - DESK_THICK * 0.5), MAT_WOOD, bevel=0.003)

for sx in (-1.0, 1.0):
    add_box(COL_DESK, "Desk_Leg_%s" % ("R" if sx > 0 else "L"),
            (0.035, DESK_D - 0.10, 0.68),
            T(sx * (DESK_W * 0.5 - 0.09), 0.0, FLOOR_Z + 0.34 + 0.008),
            MAT_DARKMET, bevel=0.002)
    add_box(COL_DESK, "Desk_Foot_%s" % ("R" if sx > 0 else "L"),
            (0.055, DESK_D - 0.04, 0.016),
            T(sx * (DESK_W * 0.5 - 0.09), 0.0, FLOOR_Z + 0.008),
            MAT_DARKMET, bevel=0.003)

add_box(COL_DESK, "Desk_Stretcher", (DESK_W - 0.24, 0.05, 0.05),
        T(0.0, 0.10, FLOOR_Z + 0.12), MAT_DARKMET, bevel=0.004)


# ----------------------------------------------------------------------------
# C-clamp at the rear desk edge
# ----------------------------------------------------------------------------

CLAMP_Y = 0.405
DESK_BACK = DESK_D * 0.5

add_box(COL_MOUNT, "Clamp_Spine", (0.086, 0.016, 0.108),
        T(0.0, DESK_BACK + 0.014, -0.030), MAT_DARKMET, bevel=0.004)
add_box(COL_MOUNT, "Clamp_JawTop", (0.090, 0.105, 0.014),
        T(0.0, CLAMP_Y + 0.008, 0.007), MAT_DARKMET, bevel=0.004)
add_box(COL_MOUNT, "Clamp_JawTop_Pad", (0.078, 0.090, 0.002),
        T(0.0, CLAMP_Y + 0.008, -0.001), MAT_RUBBER)
add_box(COL_MOUNT, "Clamp_JawBottom", (0.088, 0.080, 0.014),
        T(0.0, CLAMP_Y + 0.020, -0.084), MAT_DARKMET, bevel=0.004)

add_cylinder(COL_MOUNT, "Clamp_Screw", 0.0075, 0.052,
             T(0.0, CLAMP_Y + 0.010, -0.062), MAT_ALU, verts=20)
add_cylinder(COL_MOUNT, "Clamp_ScrewPad", 0.021, 0.008,
             T(0.0, CLAMP_Y + 0.010, -0.041), MAT_RUBBER, verts=28,
             bevel=0.0015)
add_cylinder(COL_MOUNT, "Clamp_Handle", 0.0055, 0.088,
             T(0.0, CLAMP_Y + 0.010, -0.090) @ rot_y(math.pi * 0.5),
             MAT_ALU, verts=18, bevel=0.0015)
for sx in (-1.0, 1.0):
    add_sphere(COL_MOUNT, "Clamp_HandleKnob", 0.009,
               T(sx * 0.046, CLAMP_Y + 0.010, -0.090), MAT_PLASTIC, u=20, v=10)


# ----------------------------------------------------------------------------
# riser post
# ----------------------------------------------------------------------------

POST_TOP_Z = 0.340

add_cylinder(COL_MOUNT, "Post_Collar", 0.032, 0.020,
             T(0.0, CLAMP_Y, 0.024), MAT_DARKMET, verts=36, bevel=0.002)
add_cylinder(COL_MOUNT, "Post", 0.0215, POST_TOP_Z - 0.014,
             T(0.0, CLAMP_Y, 0.014 + (POST_TOP_Z - 0.014) * 0.5),
             MAT_ALU, verts=40)
add_cylinder(COL_MOUNT, "Post_Cap", 0.024, 0.016,
             T(0.0, CLAMP_Y, POST_TOP_Z - 0.026), MAT_DARKMET, verts=36,
             bevel=0.002)


# ----------------------------------------------------------------------------
# articulated arm (two segments in the YZ plane)
# ----------------------------------------------------------------------------

def polar(origin, angle_deg, length):
    a = D2R(angle_deg)
    return origin + Vector((0.0, -math.cos(a) * length, math.sin(a) * length))


P0 = Vector((0.0, CLAMP_Y, POST_TOP_Z))          # shoulder, on the post
P1 = polar(P0, 22.0, 0.300)                      # elbow
P2 = polar(P1, -30.0, 0.260)                     # wrist

ARM_W = 0.054
ARM_H = 0.046


def build_arm(name, a, b, width, height, mat, shrink=0.030):
    d = (b - a)
    length = d.length
    mtx = segment_matrix(a, b)
    add_box(COL_MOUNT, name, (width, length - shrink, height), mtx, mat,
            bevel=0.006, segments=3)
    # snap-on cable channel cover along the top face
    add_box(COL_MOUNT, name + "_CableCover",
            (width * 0.52, length - shrink - 0.030, 0.010),
            mtx @ T(0.0, 0.0, height * 0.5 + 0.002), MAT_PLASTIC,
            bevel=0.003)
    return mtx


mtx_lower = build_arm("Arm_Lower", P0, P1, ARM_W, ARM_H, MAT_ALU)
mtx_upper = build_arm("Arm_Upper", P1, P2, ARM_W - 0.006, ARM_H - 0.004,
                      MAT_ALU)

# gas-spring tension adjuster on the lower arm
add_cylinder(COL_MOUNT, "Tension_Screw", 0.010, ARM_W + 0.004,
             mtx_lower @ T(0.0, -0.100, 0.006) @ rot_y(math.pi * 0.5),
             MAT_DARKMET, verts=6)

# joint hubs (axes along world X)
for nm, p, r in (("Joint_Shoulder", P0, 0.029),
                 ("Joint_Elbow", P1, 0.029),
                 ("Joint_Wrist", P2, 0.025)):
    add_cylinder(COL_MOUNT, nm, r, ARM_W + 0.008,
                 T(p.x, p.y, p.z) @ rot_y(math.pi * 0.5), MAT_DARKMET,
                 verts=40, bevel=0.002)
    for sx in (-1.0, 1.0):
        add_cylinder(COL_MOUNT, nm + "_Bolt", r * 0.36, 0.007,
                     T(p.x + sx * (ARM_W * 0.5 + 0.007), p.y, p.z)
                     @ rot_y(math.pi * 0.5), MAT_ALU, verts=6)

# little cable clips hugging the arms
for mtx, off in ((mtx_lower, 0.075), (mtx_lower, -0.055), (mtx_upper, 0.040)):
    add_box(COL_MOUNT, "Cable_Clip", (0.014, 0.012, 0.020),
            mtx @ T(ARM_W * 0.5 + 0.005, off, 0.014), MAT_PLASTIC, bevel=0.002)


# ----------------------------------------------------------------------------
# tilt/swivel head + VESA plate
# ----------------------------------------------------------------------------

BALL = P2 + Vector((0.0, -0.024, 0.0))
YAW = D2R(9.0)
TILT = D2R(-6.0)

add_cylinder(COL_MOUNT, "Wrist_Stub", 0.020, 0.030,
             T(P2.x, P2.y - 0.012, P2.z) @ rot_x(math.pi * 0.5), MAT_DARKMET,
             verts=32)

HEAD_YAW = T(BALL.x, BALL.y, BALL.z) @ rot_z(YAW) @ T(-BALL.x, -BALL.y, -BALL.z)
head_objs = []

head_objs.append(add_sphere(COL_MOUNT, "Ball_Joint", 0.0245,
                            T(BALL.x, BALL.y, BALL.z), MAT_ALU, u=32, v=16))

# panel local frame: X = width, Y = depth (front faces -Y), Z = height
PANEL_W = 0.545
PANEL_H = 0.330
SHELL_D = 0.020
BORDER = 0.008
CHIN = 0.024

panel_center = BALL + Vector((0.0, -0.053, 0.0))
PANEL_MTX = (T(BALL.x, BALL.y, BALL.z) @ rot_x(TILT)
             @ T(0.0, panel_center.y - BALL.y, 0.0))


def P(local_mtx):
    return PANEL_MTX @ local_mtx


# VESA plate + quick release
head_objs.append(add_box(COL_MOUNT, "VESA_Plate", (0.108, 0.006, 0.108),
                         P(T(0.0, 0.0370, 0.0)), MAT_DARKMET, bevel=0.003))
head_objs.append(add_box(COL_MOUNT, "VESA_Boss", (0.062, 0.014, 0.062),
                         P(T(0.0, 0.0290, 0.0)), MAT_DARKMET, bevel=0.003))
head_objs.append(add_box(COL_MOUNT, "QR_Lever", (0.014, 0.030, 0.046),
                         P(T(0.058, 0.032, -0.020)), MAT_PLASTIC, bevel=0.003))
for sx in (-1.0, 1.0):
    for sz in (-1.0, 1.0):
        head_objs.append(add_cylinder(
            COL_MOUNT, "VESA_Screw", 0.0045, 0.010,
            P(T(sx * 0.050, 0.036, sz * 0.050) @ rot_x(math.pi * 0.5)),
            MAT_ALU, verts=6))

# monitor body
head_objs.append(add_box(COL_MONITOR, "Panel_Shell",
                         (PANEL_W, SHELL_D, PANEL_H), P(T(0, 0, 0)),
                         MAT_SHELL, bevel=0.004, segments=3))
head_objs.append(add_box(COL_MONITOR, "Panel_RearBulge", (0.340, 0.024, 0.200),
                         P(T(0.0, SHELL_D * 0.5 + 0.012, 0.0)), MAT_SHELL,
                         bevel=0.006, segments=3))
# ventilation ribs on the rear bulge
for i in range(7):
    head_objs.append(add_box(
        COL_MONITOR, "Vent_Rib", (0.300, 0.006, 0.006),
        P(T(0.0, SHELL_D * 0.5 + 0.024, 0.070 - i * 0.014)), MAT_BEZEL))

front_y = -SHELL_D * 0.5
bez_t = 0.0028
bez_y = front_y - bez_t * 0.5
screen_z = ((PANEL_H * 0.5 - BORDER) + (-PANEL_H * 0.5 + CHIN)) * 0.5
screen_w = PANEL_W - 2.0 * BORDER
screen_h = PANEL_H - BORDER - CHIN

head_objs.append(add_box(COL_MONITOR, "Bezel_Top", (PANEL_W, bez_t, BORDER),
                         P(T(0.0, bez_y, PANEL_H * 0.5 - BORDER * 0.5)),
                         MAT_BEZEL))
head_objs.append(add_box(COL_MONITOR, "Bezel_Chin", (PANEL_W, bez_t, CHIN),
                         P(T(0.0, bez_y, -PANEL_H * 0.5 + CHIN * 0.5)),
                         MAT_BEZEL, bevel=0.0008))
for sx in (-1.0, 1.0):
    head_objs.append(add_box(
        COL_MONITOR, "Bezel_Side", (BORDER, bez_t, screen_h),
        P(T(sx * (PANEL_W * 0.5 - BORDER * 0.5), bez_y, screen_z)),
        MAT_BEZEL))

screen = add_box(COL_MONITOR, "Screen", (screen_w, 0.0012, screen_h),
                 P(T(0.0, front_y - 0.0006, screen_z)), MAT_SCREEN)
head_objs.append(screen)

# chin details: brand strip, power LED, joystick button
head_objs.append(add_box(COL_MONITOR, "Brand_Strip", (0.058, 0.0018, 0.006),
                         P(T(0.0, bez_y - bez_t * 0.6,
                             -PANEL_H * 0.5 + CHIN * 0.5)),
                         MAT_ALU))
head_objs.append(add_cylinder(
    COL_MONITOR, "Power_LED", 0.0022, 0.0022,
    P(T(0.215, bez_y - bez_t * 0.5, -PANEL_H * 0.5 + 0.008)
      @ rot_x(math.pi * 0.5)), MAT_LED, verts=14))
head_objs.append(add_cylinder(
    COL_MONITOR, "OSD_Joystick", 0.0055, 0.010,
    P(T(0.170, SHELL_D * 0.5 + 0.004, -PANEL_H * 0.5 + 0.012)
      @ rot_x(math.pi * 0.5)), MAT_PLASTIC, verts=18, bevel=0.001))

# I/O recess under the rear bulge
head_objs.append(add_box(COL_MONITOR, "IO_Block", (0.150, 0.016, 0.030),
                         P(T(0.0, SHELL_D * 0.5 + 0.010, -0.118)), MAT_BEZEL,
                         bevel=0.002))
for i in range(4):
    head_objs.append(add_box(
        COL_MONITOR, "IO_Port", (0.020, 0.006, 0.010),
        P(T(-0.048 + i * 0.032, SHELL_D * 0.5 + 0.020, -0.118)),
        MAT_ALU, bevel=0.0008))

for obj in head_objs:
    obj.matrix_world = HEAD_YAW @ obj.matrix_world


# ----------------------------------------------------------------------------
# power/signal cable routed along the arm
# ----------------------------------------------------------------------------

cable_pts = [
    Vector((0.02, panel_center.y + 0.040, panel_center.z - 0.130)),
    Vector((0.035, BALL.y + 0.010, BALL.z - 0.060)),
    Vector((0.036, (P2.y + P1.y) * 0.5, (P2.z + P1.z) * 0.5 + 0.030)),
    Vector((0.036, P1.y + 0.010, P1.z + 0.034)),
    Vector((0.036, (P1.y + P0.y) * 0.5, (P1.z + P0.z) * 0.5 + 0.030)),
    Vector((0.032, P0.y - 0.010, P0.z - 0.020)),
    Vector((0.036, CLAMP_Y + 0.030, 0.150)),
    Vector((0.030, CLAMP_Y + 0.034, 0.010)),
    Vector((-0.060, CLAMP_Y - 0.010, 0.006)),
    Vector((-0.190, CLAMP_Y + 0.020, 0.006)),
]

curve = bpy.data.curves.new("Cable_Curve", 'CURVE')
curve.dimensions = '3D'
curve.resolution_u = 12
curve.bevel_depth = 0.0042
curve.bevel_resolution = 5
spline = curve.splines.new('BEZIER')
spline.bezier_points.add(len(cable_pts) - 1)
for bp, co in zip(spline.bezier_points, cable_pts):
    bp.co = co
    bp.handle_left_type = 'AUTO'
    bp.handle_right_type = 'AUTO'
cable_obj = bpy.data.objects.new("Cable", curve)
cable_obj.data.materials.append(MAT_CABLE)
COL_MOUNT.objects.link(cable_obj)


# ----------------------------------------------------------------------------
# keyboard, for scale
# ----------------------------------------------------------------------------

KB_LOC = Vector((-0.030, -0.250, 0.0))
kb_mtx = T(KB_LOC.x, KB_LOC.y, KB_LOC.z) @ rot_z(D2R(3.0)) @ rot_x(D2R(-3.0))

add_box(COL_DESK, "Keyboard_Body", (0.372, 0.132, 0.017),
        kb_mtx @ T(0.0, 0.0, 0.0095), MAT_SHELL, bevel=0.0025, segments=3)
add_box(COL_DESK, "Keyboard_Deck", (0.352, 0.112, 0.004),
        kb_mtx @ T(0.0, 0.0, 0.0175), MAT_BEZEL)

bm_keys = bmesh.new()
rows, cols = 5, 15
kw, kh, kt = 0.0192, 0.0192, 0.0055
sx_step, sy_step = 0.0228, 0.0222
for r in range(rows):
    for c in range(cols):
        x = (c - (cols - 1) * 0.5) * sx_step
        y = ((rows - 1) * 0.5 - r) * sy_step
        m = (Matrix.Translation(Vector((x, y, 0.0)))
             @ Matrix.Diagonal(Vector((kw, kh, kt, 1.0))))
        bmesh.ops.create_cube(bm_keys, size=1.0, matrix=m)
bmesh.ops.bevel(bm_keys, geom=list(bm_keys.verts) + list(bm_keys.edges)
                + list(bm_keys.faces), offset=0.0009, offset_type='OFFSET',
                segments=2, profile=0.5, affect='EDGES', clamp_overlap=True)
_to_object(COL_DESK, "Keycaps", bm_keys, kb_mtx @ T(0.0, 0.0, 0.0222),
           MAT_KEYCAP, True)


# ----------------------------------------------------------------------------
# lighting
# ----------------------------------------------------------------------------

world = bpy.data.worlds.new("World")
bpy.context.scene.world = world
world.use_nodes = True
bg = world.node_tree.nodes.get("Background")
set_input(bg, "Color", (0.045, 0.050, 0.062, 1.0))
set_input(bg, "Strength", 0.55)


def add_area_light(name, loc, target, size, energy, color=(1.0, 1.0, 1.0),
                   shape='SQUARE', size_y=None):
    data = bpy.data.lights.new(name, 'AREA')
    data.shape = shape
    data.size = size
    if size_y is not None:
        data.size_y = size_y
    data.energy = energy
    data.color = color
    obj = bpy.data.objects.new(name, data)
    COL_LIGHTS.objects.link(obj)
    obj.location = loc
    direction = Vector(target) - Vector(loc)
    obj.rotation_euler = direction.to_track_quat('-Z', 'Y').to_euler()
    return obj


add_area_light("Key_Light", (1.15, -1.05, 1.55), (0.0, -0.10, 0.32),
               1.10, 320.0, (1.0, 0.96, 0.90))
add_area_light("Fill_Light", (-1.35, -0.95, 0.85), (-0.05, -0.05, 0.28),
               1.40, 90.0, (0.80, 0.86, 1.0))
add_area_light("Rim_Light", (-0.55, 0.72, 1.05), (0.05, -0.05, 0.36),
               0.70, 120.0, (0.72, 0.82, 1.0))
add_area_light("Practical_Strip", (0.0, 0.55, 0.62), (0.0, 0.55, -0.2),
               0.05, 25.0, (1.0, 0.85, 0.65), shape='RECTANGLE', size_y=1.2)


# ----------------------------------------------------------------------------
# camera
# ----------------------------------------------------------------------------

cam_data = bpy.data.cameras.new("Camera")
cam_data.lens = 55.0
cam_data.sensor_width = 36.0
cam_data.clip_start = 0.02
cam_data.clip_end = 100.0
cam_data.dof.use_dof = True
cam_data.dof.focus_object = screen
cam_data.dof.aperture_fstop = 4.0

cam = bpy.data.objects.new("Camera", cam_data)
bpy.context.scene.collection.objects.link(cam)
cam.location = Vector((0.98, -1.18, 0.60))
look_target = Vector((0.0, -0.12, 0.30))
cam.rotation_euler = (look_target - cam.location).to_track_quat('-Z', 'Y').to_euler()
bpy.context.scene.camera = cam

bpy.context.view_layer.update()
print("claude-036: monitor on articulated desk mount -- scene built.")
