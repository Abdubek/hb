import bpy
import math
from mathutils import Vector

ROAD_W = 8.0      # half-width of each carriageway
BLOCK = 26.0      # half-size of the ground tile


def clear_scene():
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete(use_global=False)
    for coll in (bpy.data.meshes, bpy.data.materials, bpy.data.cameras, bpy.data.lights):
        for item in list(coll):
            if item.users == 0:
                coll.remove(item)


def material(name, color, rough=0.7, metallic=0.0, emit=None):
    mat = bpy.data.materials.new(name)
    mat.use_nodes = True
    bsdf = mat.node_tree.nodes["Principled BSDF"]
    bsdf.inputs["Base Color"].default_value = (*color, 1.0)
    bsdf.inputs["Roughness"].default_value = rough
    bsdf.inputs["Metallic"].default_value = metallic
    if emit is not None:
        bsdf.inputs["Emission Color"].default_value = (*emit, 1.0)
        bsdf.inputs["Emission Strength"].default_value = 5.0
    return mat


def box(name, size, loc, mat, rot=(0, 0, 0)):
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=loc, rotation=rot)
    ob = bpy.context.active_object
    ob.name = name
    ob.scale = size
    ob.data.materials.append(mat)
    return ob


def cyl(name, radius, depth, loc, mat, rot=(0, 0, 0), verts=16):
    bpy.ops.mesh.primitive_cylinder_add(vertices=verts, radius=radius, depth=depth,
                                        location=loc, rotation=rot)
    ob = bpy.context.active_object
    ob.name = name
    ob.data.materials.append(mat)
    return ob


def stripe_row(prefix, mat, axis):
    """Dashed centre line running along the given axis, skipping the junction."""
    for i in range(1, 8):
        d = ROAD_W + 1.0 + (i - 1) * 3.0
        for sign in (1, -1):
            pos = (sign * d, 0.0, 0.02) if axis == 'X' else (0.0, sign * d, 0.02)
            size = (1.8, 0.18, 0.02) if axis == 'X' else (0.18, 1.8, 0.02)
            box("%s_%s%d" % (prefix, '+' if sign > 0 else '-', i), size, pos, mat)


def crosswalk(prefix, mat, offset, axis):
    for i in range(7):
        t = -ROAD_W * 0.5 + 0.4 + i * 1.15
        if axis == 'X':
            loc, size = (offset, t, 0.02), (1.6, 0.34, 0.02)
        else:
            loc, size = (t, offset, 0.02), (0.34, 1.6, 0.02)
        box("%s_%d" % (prefix, i), size, loc, mat)


def signal(name, corner_x, corner_y, arm_dir, phase):
    """Mast-arm signal: vertical pole, horizontal arm, 3-lamp head over the road."""
    base = (corner_x, corner_y, 0.15)
    cyl(name + "_Base", 0.35, 0.3, base, MAT_CONCRETE)
    cyl(name + "_Pole", 0.14, 6.4, (corner_x, corner_y, 3.35), MAT_STEEL)
    ax, ay = arm_dir
    arm_len = 5.2
    mid = (corner_x + ax * arm_len * 0.5, corner_y + ay * arm_len * 0.5, 6.3)
    rot = (math.pi / 2, 0, 0) if ay else (0, math.pi / 2, 0)
    cyl(name + "_Arm", 0.09, arm_len, mid, MAT_STEEL, rot=rot)
    hx = corner_x + ax * arm_len * 0.92
    hy = corner_y + ay * arm_len * 0.92
    head_rot = (0, 0, math.atan2(ay, ax))
    box(name + "_Head", (0.42, 0.5, 1.5), (hx, hy, 5.6), MAT_SIGNAL_BODY, rot=head_rot)
    lamps = ((MAT_RED, 0.5), (MAT_AMBER, 0.0), (MAT_GREEN, -0.5))
    for i, (lamp_mat, dz) in enumerate(lamps):
        lit = lamp_mat if i == phase else MAT_LAMP_OFF
        lx = hx + ax * 0.24
        ly = hy + ay * 0.24
        cyl("%s_Lamp%d" % (name, i), 0.16, 0.1, (lx, ly, 5.6 + dz), lit,
            rot=(0, math.pi / 2, 0) if ax else (math.pi / 2, 0, 0), verts=12)


def bollard(name, x, y):
    cyl(name, 0.12, 1.0, (x, y, 0.5), MAT_BOLLARD, verts=12)
    cyl(name + "_Band", 0.13, 0.12, (x, y, 0.82), MAT_AMBER, verts=12)
    cyl(name + "_Cap", 0.12, 0.06, (x, y, 1.02), MAT_STEEL, verts=12)


def add_camera(loc, target, lens=40):
    cam = bpy.data.objects.new("Camera", bpy.data.cameras.new("CameraData"))
    cam.data.lens = lens
    cam.location = loc
    cam.rotation_euler = (Vector(target) - Vector(loc)).to_track_quat('-Z', 'Y').to_euler()
    bpy.context.collection.objects.link(cam)
    bpy.context.scene.camera = cam


clear_scene()

MAT_ASPHALT = material("Asphalt", (0.055, 0.055, 0.06), rough=0.85)
MAT_CONCRETE = material("Concrete", (0.62, 0.61, 0.58), rough=0.8)
MAT_GRASS = material("Verge", (0.16, 0.28, 0.12), rough=0.9)
MAT_PAINT = material("RoadPaint", (0.9, 0.89, 0.85), rough=0.55)
MAT_STEEL = material("GalvSteel", (0.55, 0.56, 0.58), rough=0.35, metallic=1.0)
MAT_SIGNAL_BODY = material("SignalHousing", (0.06, 0.09, 0.07), rough=0.5)
MAT_BOLLARD = material("BollardBody", (0.08, 0.08, 0.09), rough=0.45, metallic=0.6)
MAT_RED = material("LampRed", (0.5, 0.02, 0.02), emit=(1.0, 0.05, 0.03))
MAT_AMBER = material("LampAmber", (0.6, 0.3, 0.02), emit=(1.0, 0.45, 0.05))
MAT_GREEN = material("LampGreen", (0.03, 0.5, 0.12), emit=(0.1, 1.0, 0.25))
MAT_LAMP_OFF = material("LampOff", (0.03, 0.03, 0.03), rough=0.3)

box("Ground_Verge", (BLOCK * 2, BLOCK * 2, 0.1), (0, 0, -0.06), MAT_GRASS)
box("Road_EW", (BLOCK * 2, ROAD_W, 0.1), (0, 0, 0.0), MAT_ASPHALT)
box("Road_NS", (ROAD_W, BLOCK * 2, 0.1), (0, 0, 0.0), MAT_ASPHALT)

for sx in (1, -1):
    for sy in (1, -1):
        cx = sx * (ROAD_W * 0.5 + 6.0)
        cy = sy * (ROAD_W * 0.5 + 6.0)
        box("Sidewalk_%s%s" % ('E' if sx > 0 else 'W', 'N' if sy > 0 else 'S'),
            (12.0, 12.0, 0.22), (cx, cy, 0.11), MAT_CONCRETE)

stripe_row("Lane_EW", MAT_PAINT, 'X')
stripe_row("Lane_NS", MAT_PAINT, 'Y')
for sign in (1, -1):
    crosswalk("Crosswalk_EW%d" % sign, MAT_PAINT, sign * (ROAD_W * 0.5 + 1.2), 'X')
    crosswalk("Crosswalk_NS%d" % sign, MAT_PAINT, sign * (ROAD_W * 0.5 + 1.2), 'Y')
    box("StopBar_EW%d" % sign, (0.4, ROAD_W * 0.5, 0.02),
        (sign * (ROAD_W * 0.5 + 2.6), sign * ROAD_W * 0.25, 0.02), MAT_PAINT)
    box("StopBar_NS%d" % sign, (ROAD_W * 0.5, 0.4, 0.02),
        (-sign * ROAD_W * 0.25, sign * (ROAD_W * 0.5 + 2.6), 0.02), MAT_PAINT)

c = ROAD_W * 0.5 + 1.1
signal("Signal_NE", c, c, (-1, 0), 0)
signal("Signal_SW", -c, -c, (1, 0), 0)
signal("Signal_NW", -c, c, (0, -1), 2)
signal("Signal_SE", c, -c, (0, 1), 2)

n = 0
for sx in (1, -1):
    for sy in (1, -1):
        for i in range(5):
            t = ROAD_W * 0.5 + 2.6 + i * 2.4
            bollard("Bollard_%02d" % n, sx * t, sy * (ROAD_W * 0.5 + 0.9))
            n += 1
            bollard("Bollard_%02d" % n, sx * (ROAD_W * 0.5 + 0.9), sy * t)
            n += 1

sun = bpy.data.objects.new("Sun", bpy.data.lights.new("SunData", type='SUN'))
sun.data.energy = 4.0
sun.location = (14, -18, 26)
sun.rotation_euler = (math.radians(48), 0, math.radians(38))
bpy.context.collection.objects.link(sun)

add_camera((26.0, -30.0, 20.0), (0.0, 0.0, 2.5), lens=45)
