"""claude-020 - Four-legged robot dog with simple jointed limbs.

Builds the scene only: no rendering, no file output, no external assets.
"""

import bpy
import bmesh
import math
from mathutils import Vector


# ----------------------------------------------------------------------------
# generic helpers
# ----------------------------------------------------------------------------

def reset_scene():
    bpy.ops.wm.read_factory_settings(use_empty=True)
    bpy.context.scene.unit_settings.system = 'METRIC'


def new_material(name, base=(0.8, 0.8, 0.8), metallic=0.0, rough=0.5,
                 transmission=0.0, alpha=1.0, ior=1.45,
                 emission=None, emit_strength=0.0, coat=0.0):
    mat = bpy.data.materials.new(name)
    mat.use_nodes = True
    bsdf = mat.node_tree.nodes.get("Principled BSDF")

    def put(key, value):
        if bsdf and key in bsdf.inputs:
            bsdf.inputs[key].default_value = value

    put("Base Color", (base[0], base[1], base[2], 1.0))
    put("Metallic", metallic)
    put("Roughness", rough)
    put("IOR", ior)
    put("Transmission Weight", transmission)
    put("Alpha", alpha)
    put("Coat Weight", coat)
    if emission is not None:
        put("Emission Color", (emission[0], emission[1], emission[2], 1.0))
        put("Emission Strength", emit_strength)
    if alpha < 1.0 or transmission > 0.0:
        try:
            mat.blend_method = 'BLEND'
        except Exception:
            pass
    return mat


def shade_auto(ob, angle=math.radians(34.0)):
    me = ob.data
    for poly in me.polygons:
        poly.use_smooth = True
    bm = bmesh.new()
    bm.from_mesh(me)
    for edge in bm.edges:
        if len(edge.link_faces) == 2:
            edge.smooth = edge.calc_face_angle() < angle
        else:
            edge.smooth = False
    bm.to_mesh(me)
    bm.free()


def _finish(bm, name, loc, rot, mat, smooth, smooth_angle, parent):
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    me = bpy.data.meshes.new(name)
    bm.to_mesh(me)
    bm.free()
    ob = bpy.data.objects.new(name, me)
    bpy.context.collection.objects.link(ob)
    if parent is not None:
        ob.parent = parent
    ob.location = loc
    if isinstance(rot, Vector) or len(rot) == 3:
        ob.rotation_euler = rot
    if mat is not None:
        me.materials.append(mat)
    if smooth:
        shade_auto(ob, smooth_angle)
    return ob


def add_box(name, size, loc=(0, 0, 0), rot=(0, 0, 0), mat=None,
            bevel=0.0, seg=3, parent=None):
    bm = bmesh.new()
    bmesh.ops.create_cube(bm, size=1.0)
    bmesh.ops.scale(bm, vec=Vector(size), verts=bm.verts)
    if bevel > 0.0:
        bmesh.ops.bevel(bm, geom=list(bm.verts) + list(bm.edges) + list(bm.faces),
                        offset=bevel, offset_type='OFFSET', segments=seg,
                        profile=0.5, affect='EDGES', clamp_overlap=True)
        return _finish(bm, name, loc, rot, mat, True, math.radians(32.0), parent)
    return _finish(bm, name, loc, rot, mat, False, 0.0, parent)


def add_cyl(name, radius, depth, loc=(0, 0, 0), rot=(0, 0, 0), mat=None,
            segments=32, bevel=0.0, parent=None):
    bm = bmesh.new()
    bmesh.ops.create_cone(bm, cap_ends=True, cap_tris=False, segments=segments,
                          radius1=radius, radius2=radius, depth=depth)
    if bevel > 0.0:
        bmesh.ops.bevel(bm, geom=list(bm.verts) + list(bm.edges) + list(bm.faces),
                        offset=bevel, offset_type='OFFSET', segments=2,
                        profile=0.5, affect='EDGES', clamp_overlap=True)
    return _finish(bm, name, loc, rot, mat, True, math.radians(40.0), parent)


def add_sphere(name, radius, loc=(0, 0, 0), mat=None, useg=28, vseg=16,
               scale=(1, 1, 1), parent=None):
    bm = bmesh.new()
    bmesh.ops.create_uvsphere(bm, u_segments=useg, v_segments=vseg, radius=radius)
    bmesh.ops.scale(bm, vec=Vector(scale), verts=bm.verts)
    return _finish(bm, name, loc, (0, 0, 0), mat, True, math.radians(60.0), parent)


def add_link(name, p0, p1, width, depth, mat=None, bevel=0.008, parent=None):
    """A beveled box spanning p0 -> p1, its local +Z aligned with the segment."""
    a, b = Vector(p0), Vector(p1)
    d = b - a
    length = d.length
    rot = d.to_track_quat('Z', 'Y').to_euler()
    return add_box(name, (width, depth, length), (a + d * 0.5), rot,
                   mat=mat, bevel=bevel, parent=parent)


def aim(ob, target):
    d = Vector(target) - ob.location
    ob.rotation_euler = d.to_track_quat('-Z', 'Y').to_euler()


def add_light(name, ltype, loc, energy, color=(1.0, 1.0, 1.0), size=1.0,
              target=None):
    data = bpy.data.lights.new(name, ltype)
    data.energy = energy
    data.color = color
    if ltype == 'AREA':
        data.size = size
    elif ltype == 'SUN':
        data.angle = math.radians(2.5)
    else:
        data.shadow_soft_size = size
    ob = bpy.data.objects.new(name, data)
    ob.location = loc
    bpy.context.collection.objects.link(ob)
    if target is not None:
        aim(ob, target)
    return ob


def setup_world(color=(0.05, 0.055, 0.065), strength=1.0):
    world = bpy.data.worlds.new("World")
    bpy.context.scene.world = world
    world.use_nodes = True
    bg = world.node_tree.nodes["Background"]
    bg.inputs[0].default_value = (color[0], color[1], color[2], 1.0)
    bg.inputs[1].default_value = strength


def add_camera(loc, target, lens=50.0, name="Camera"):
    data = bpy.data.cameras.new(name)
    data.lens = lens
    ob = bpy.data.objects.new(name, data)
    ob.location = loc
    bpy.context.collection.objects.link(ob)
    aim(ob, target)
    bpy.context.scene.camera = ob
    return ob


# ----------------------------------------------------------------------------
# materials
# ----------------------------------------------------------------------------

reset_scene()
setup_world((0.055, 0.06, 0.07), 1.0)

GROUND = new_material("Ground", (0.14, 0.145, 0.15), rough=0.7)
SHELL = new_material("ShellWhite", (0.80, 0.79, 0.75), rough=0.35, coat=0.4)
SHELL_2 = new_material("ShellGrey", (0.36, 0.37, 0.39), rough=0.42)
JOINT = new_material("JointMetal", (0.55, 0.56, 0.58), metallic=1.0, rough=0.3)
DARKMET = new_material("DarkMetal", (0.10, 0.105, 0.115), metallic=0.9,
                       rough=0.4)
RUBBER = new_material("FootRubber", (0.045, 0.045, 0.05), rough=0.8)
ACCENT = new_material("Accent", (0.86, 0.36, 0.05), rough=0.35, coat=0.5)
EYE = new_material("EyeLens", (0.02, 0.06, 0.08),
                   emission=(0.25, 0.85, 1.0), emit_strength=7.0)
LED = new_material("StatusLed", (0.06, 0.02, 0.02),
                   emission=(1.0, 0.35, 0.12), emit_strength=6.0)
GLASSY = new_material("SensorGlass", (0.03, 0.035, 0.045), rough=0.08,
                      coat=0.9)


# ----------------------------------------------------------------------------
# ground
# ----------------------------------------------------------------------------

add_box("Ground", (10.0, 10.0, 0.2), (0.0, 0.0, -0.1), mat=GROUND)
for i in range(-3, 4):
    add_box("GroundLineX_%d" % i, (6.0, 0.008, 0.002), (0.0, i * 0.5, 0.001),
            mat=SHELL_2)
    add_box("GroundLineY_%d" % i, (0.008, 6.0, 0.002), (i * 0.5, 0.0, 0.001),
            mat=SHELL_2)


# ----------------------------------------------------------------------------
# torso
# ----------------------------------------------------------------------------

BODY_Z = 0.360
BODY_L, BODY_W, BODY_H = 0.460, 0.220, 0.160

add_box("Torso", (BODY_W, BODY_L, BODY_H), (0.0, 0.0, BODY_Z), mat=SHELL,
        bevel=0.024, seg=4)
add_box("TorsoUnderTray", (BODY_W - 0.03, BODY_L - 0.06, 0.05),
        (0.0, 0.0, BODY_Z - BODY_H * 0.5 - 0.012), mat=DARKMET, bevel=0.012)
add_box("TorsoTopPlate", (BODY_W - 0.04, 0.30, 0.022), (0.0, -0.02, BODY_Z + 0.088),
        mat=SHELL_2, bevel=0.008)
add_box("TorsoSpine", (0.05, BODY_L - 0.05, 0.028), (0.0, 0.0, BODY_Z + 0.096),
        mat=DARKMET, bevel=0.008)
add_box("HandleBar", (0.026, 0.20, 0.026), (0.0, -0.05, BODY_Z + 0.118),
        mat=JOINT, bevel=0.010)

# side panels with vent slots
for sx in (-1, 1):
    add_box("SidePanel_%d" % sx, (0.008, BODY_L - 0.10, BODY_H - 0.055),
            (sx * (BODY_W * 0.5 + 0.001), 0.0, BODY_Z - 0.008), mat=SHELL_2,
            bevel=0.004)
    for i in range(5):
        add_box("Vent_%d_%d" % (sx, i), (0.006, 0.022, 0.052),
                (sx * (BODY_W * 0.5 + 0.004), -0.10 + i * 0.05, BODY_Z - 0.008),
                mat=DARKMET, bevel=0.002)
    add_box("AccentStripe_%d" % sx, (0.006, 0.16, 0.014),
            (sx * (BODY_W * 0.5 + 0.004), 0.08, BODY_Z + 0.055), mat=ACCENT,
            bevel=0.003)

# battery pack slung under the belly
add_box("BatteryPack", (0.150, 0.200, 0.045), (0.0, -0.03, BODY_Z - BODY_H * 0.5 - 0.038),
        mat=DARKMET, bevel=0.010)
add_cyl("BatteryLed", 0.008, 0.006, (0.0, -0.135, BODY_Z - BODY_H * 0.5 - 0.038),
        rot=(math.radians(90), 0, 0), mat=LED, segments=18)

# sensor turret on the back
add_cyl("TurretBase", 0.038, 0.026, (0.0, 0.115, BODY_Z + 0.112), mat=SHELL_2,
        segments=32, bevel=0.006)
add_cyl("TurretDrum", 0.032, 0.030, (0.0, 0.115, BODY_Z + 0.140), mat=GLASSY,
        segments=32)
add_sphere("TurretDome", 0.032, (0.0, 0.115, BODY_Z + 0.155), mat=SHELL_2,
           useg=28, vseg=14, scale=(1.0, 1.0, 0.55))
add_cyl("AntennaRod", 0.0035, 0.10, (-0.06, -0.16, BODY_Z + 0.14), mat=DARKMET,
        segments=12)
add_sphere("AntennaTip", 0.007, (-0.06, -0.16, BODY_Z + 0.192), mat=ACCENT,
           useg=16, vseg=10)


# ----------------------------------------------------------------------------
# neck and head
# ----------------------------------------------------------------------------

neck_root = Vector((0.0, BODY_L * 0.5 - 0.02, BODY_Z + 0.045))
neck_mid = Vector((0.0, BODY_L * 0.5 + 0.055, BODY_Z + 0.095))
add_sphere("NeckJoint0", 0.036, neck_root, mat=JOINT, useg=24, vseg=14)
add_link("NeckLink", neck_root, neck_mid, 0.085, 0.085, mat=SHELL_2, bevel=0.014)
add_sphere("NeckJoint1", 0.032, neck_mid, mat=JOINT, useg=24, vseg=14)

HEAD_C = Vector((0.0, 0.352, BODY_Z + 0.130))
add_box("Head", (0.130, 0.160, 0.110), HEAD_C, mat=SHELL, bevel=0.022, seg=4)
add_box("Snout", (0.092, 0.080, 0.062), (0.0, HEAD_C.y + 0.098, HEAD_C.z - 0.022),
        mat=SHELL_2, bevel=0.016)
add_box("SnoutVisor", (0.078, 0.010, 0.036),
        (0.0, HEAD_C.y + 0.137, HEAD_C.z - 0.020), mat=GLASSY, bevel=0.006)
add_cyl("Nose", 0.012, 0.010, (0.0, HEAD_C.y + 0.140, HEAD_C.z - 0.048),
        rot=(math.radians(90), 0, 0), mat=DARKMET, segments=20)

# eyes
for sx in (-1, 1):
    add_cyl("EyeHousing_%d" % sx, 0.026, 0.016,
            (sx * 0.038, HEAD_C.y + 0.072, HEAD_C.z + 0.018),
            rot=(math.radians(90), 0, 0), mat=DARKMET, segments=28, bevel=0.004)
    add_cyl("EyeLens_%d" % sx, 0.021, 0.008,
            (sx * 0.038, HEAD_C.y + 0.083, HEAD_C.z + 0.018),
            rot=(math.radians(90), 0, 0), mat=EYE, segments=28)
    # ears
    add_box("Ear_%d" % sx, (0.018, 0.048, 0.072),
            (sx * 0.056, HEAD_C.y - 0.018, HEAD_C.z + 0.086),
            rot=(math.radians(-8), sx * math.radians(16.0), 0),
            mat=SHELL_2, bevel=0.006)
    add_box("EarInner_%d" % sx, (0.008, 0.032, 0.050),
            (sx * 0.048, HEAD_C.y - 0.018, HEAD_C.z + 0.086),
            rot=(math.radians(-8), sx * math.radians(16.0), 0),
            mat=ACCENT, bevel=0.003)

add_box("HeadTopPlate", (0.108, 0.130, 0.014), (0.0, HEAD_C.y - 0.004, HEAD_C.z + 0.058),
        mat=SHELL_2, bevel=0.005)


# ----------------------------------------------------------------------------
# tail
# ----------------------------------------------------------------------------

t0 = Vector((0.0, -BODY_L * 0.5 + 0.01, BODY_Z + 0.030))
t1 = Vector((0.0, -BODY_L * 0.5 - 0.070, BODY_Z + 0.075))
t2 = Vector((0.012, -BODY_L * 0.5 - 0.120, BODY_Z + 0.150))
add_sphere("TailJoint0", 0.028, t0, mat=JOINT, useg=20, vseg=12)
add_link("TailLink0", t0, t1, 0.040, 0.040, mat=SHELL_2, bevel=0.010)
add_sphere("TailJoint1", 0.023, t1, mat=JOINT, useg=20, vseg=12)
add_link("TailLink1", t1, t2, 0.030, 0.030, mat=SHELL_2, bevel=0.008)
add_sphere("TailTip", 0.020, t2, mat=ACCENT, useg=20, vseg=12)


# ----------------------------------------------------------------------------
# legs: hip -> knee -> ankle chain solved in the sagittal plane
# ----------------------------------------------------------------------------

HIP_X = 0.115
HIP_Y = 0.175
HIP_Z = 0.340
THIGH_L = 0.170
SHANK_L = 0.176

LEGS = [
    ("FL", -1, 1, math.radians(-22.0), math.radians(18.0)),
    ("FR", 1, 1, math.radians(-22.0), math.radians(18.0)),
    ("RL", -1, -1, math.radians(22.0), math.radians(-18.0)),
    ("RR", 1, -1, math.radians(22.0), math.radians(-18.0)),
]

for tag, sx, sy, a_thigh, a_shank in LEGS:
    hip = Vector((sx * HIP_X, sy * HIP_Y, HIP_Z))
    knee = hip + Vector((0.0, math.sin(a_thigh), -math.cos(a_thigh))) * THIGH_L
    foot = knee + Vector((0.0, math.sin(a_shank), -math.cos(a_shank))) * SHANK_L

    # hip housing / abduction actuator
    add_cyl("HipHousing_" + tag, 0.047, 0.062,
            (sx * (HIP_X + 0.034), hip.y, hip.z), rot=(0, math.radians(90), 0),
            mat=SHELL, segments=32, bevel=0.008)
    add_cyl("HipPlate_" + tag, 0.030, 0.012,
            (sx * (HIP_X + 0.066), hip.y, hip.z), rot=(0, math.radians(90), 0),
            mat=ACCENT, segments=28, bevel=0.003)
    add_sphere("HipJoint_" + tag, 0.040, hip, mat=JOINT, useg=26, vseg=14)

    # upper link (thigh) with a shell fairing
    add_link("Thigh_" + tag, hip, knee, 0.052, 0.072, mat=SHELL, bevel=0.014,
             seg=3)
    mid_t = (hip + knee) * 0.5
    add_link("ThighTrim_" + tag, hip, knee, 0.058, 0.026, mat=SHELL_2,
             bevel=0.008)

    # knee joint plus a visible actuator barrel
    add_sphere("KneeJoint_" + tag, 0.036, knee, mat=JOINT, useg=26, vseg=14)
    add_cyl("KneeCap_" + tag, 0.030, 0.070, (sx * (HIP_X + 0.006), knee.y, knee.z),
            rot=(0, math.radians(90), 0), mat=DARKMET, segments=26, bevel=0.005)
    act_a = mid_t + Vector((0.0, -sy * 0.030, 0.010))
    act_b = knee + Vector((0.0, -sy * 0.016, 0.030))
    add_link("KneeActuator_" + tag, act_a, act_b, 0.020, 0.020, mat=JOINT,
             bevel=0.005)

    # lower link (shank), tapered by a second thinner segment
    add_link("Shank_" + tag, knee, foot, 0.042, 0.056, mat=SHELL_2, bevel=0.012)
    add_link("ShankRib_" + tag, knee, foot, 0.048, 0.018, mat=SHELL, bevel=0.006)

    # ankle and foot pad
    add_sphere("AnkleJoint_" + tag, 0.026, foot, mat=JOINT, useg=22, vseg=12)
    add_cyl("FootPad_" + tag, 0.036, 0.024, (foot.x, foot.y, 0.012),
            mat=RUBBER, segments=28, bevel=0.008)
    add_cyl("FootSole_" + tag, 0.030, 0.006, (foot.x, foot.y, 0.003),
            mat=DARKMET, segments=24)


# ----------------------------------------------------------------------------
# lighting and camera
# ----------------------------------------------------------------------------

add_light("Key", 'AREA', (-1.7, -1.6, 2.1), 700.0, (1.0, 0.97, 0.92),
          size=2.6, target=(0.0, 0.05, 0.32))
add_light("Fill", 'AREA', (1.9, -1.3, 1.0), 220.0, (0.75, 0.83, 1.0),
          size=3.0, target=(0.0, 0.05, 0.30))
add_light("Rim", 'AREA', (0.6, 2.3, 1.6), 380.0, (0.85, 0.90, 1.0),
          size=2.0, target=(0.0, 0.10, 0.36))
add_light("Bounce", 'AREA', (0.0, 0.0, 0.03), 30.0, (1.0, 0.96, 0.9),
          size=2.5, target=(0.0, 0.0, 0.5))

add_camera((1.55, -1.62, 0.88), (0.0, 0.06, 0.34), lens=50.0)

bpy.context.view_layer.update()
