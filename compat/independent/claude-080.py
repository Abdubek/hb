import bpy, bmesh, math
from mathutils import Vector

# ---------------------------------------------------------------- utilities

def clear_scene():
    for ob in list(bpy.data.objects):
        bpy.data.objects.remove(ob, do_unlink=True)


def make_mat(name, rgb, metallic=0.0, roughness=0.5):
    mat = bpy.data.materials.new(name)
    mat.use_nodes = True
    bsdf = next(n for n in mat.node_tree.nodes if n.type == 'BSDF_PRINCIPLED')
    bsdf.inputs["Base Color"].default_value = (rgb[0], rgb[1], rgb[2], 1.0)
    bsdf.inputs["Metallic"].default_value = metallic
    bsdf.inputs["Roughness"].default_value = roughness
    return mat


def link(ob, mat, parent):
    ob.data.materials.append(mat)
    bpy.context.collection.objects.link(ob)
    if parent:
        ob.parent = parent
    return ob


def add_box(name, size, loc, mat, rot=(0, 0, 0), parent=None):
    me = bpy.data.meshes.new(name)
    bm = bmesh.new()
    bmesh.ops.create_cube(bm, size=1.0)
    bmesh.ops.scale(bm, vec=Vector(size), verts=bm.verts)
    bm.to_mesh(me)
    bm.free()
    ob = bpy.data.objects.new(name, me)
    ob.location = loc
    ob.rotation_euler = rot
    return link(ob, mat, parent)


def add_cyl(name, radius, depth, loc, mat, rot=(0, 0, 0), seg=20, parent=None):
    me = bpy.data.meshes.new(name)
    bm = bmesh.new()
    bmesh.ops.create_cone(bm, cap_ends=True, cap_tris=False, segments=seg,
                          radius1=radius, radius2=radius, depth=depth)
    bm.to_mesh(me)
    bm.free()
    ob = bpy.data.objects.new(name, me)
    ob.location = loc
    ob.rotation_euler = rot
    return link(ob, mat, parent)


def add_tube(name, pts, radius, mat, parent=None):
    cu = bpy.data.curves.new(name, 'CURVE')
    cu.dimensions = '3D'
    cu.bevel_depth = radius
    cu.bevel_resolution = 3
    cu.use_fill_caps = True
    sp = cu.splines.new('POLY')
    sp.points.add(len(pts) - 1)
    for i, p in enumerate(pts):
        sp.points[i].co = (p[0], p[1], p[2], 1.0)
    ob = bpy.data.objects.new(name, cu)
    return link(ob, mat, parent)


# ---------------------------------------------------------------- materials
clear_scene()
STEEL = make_mat("CraneSteel", (0.85, 0.45, 0.06), 0.4, 0.45)
GREY = make_mat("MachineGrey", (0.28, 0.30, 0.33), 0.6, 0.4)
DARK = make_mat("DarkSteel", (0.09, 0.09, 0.10), 0.8, 0.35)
RAIL = make_mat("RailSteel", (0.55, 0.56, 0.58), 0.9, 0.3)
CONC = make_mat("Concrete", (0.62, 0.61, 0.58), 0.0, 0.85)

root = bpy.data.objects.new("GantryCrane", None)
bpy.context.collection.objects.link(root)

SPAN = 7.0      # half span; portal legs sit at x = +/- SPAN
GY = 2.2        # main girder / leg offset in Y
TOP = 10.0      # underside of the main girders

# ---------------------------------------------------------------- ground + travel rails
add_box("Yard", (44, 34, 0.3), (0, 0, -0.15), CONC)
for sx in (-1, 1):
    side = "E" if sx > 0 else "W"
    add_box("RailBed_" + side, (1.6, 30, 0.24), (sx * SPAN, 0, 0.12), CONC)
    add_box("Rail_" + side, (0.3, 30, 0.22), (sx * SPAN, 0, 0.35), RAIL)

# ---------------------------------------------------------------- portal legs and bogies
for sx in (-1, 1):
    side = "E" if sx > 0 else "W"
    x = sx * SPAN
    for sy in (-1, 1):
        tag = "%s%s" % (side, "N" if sy > 0 else "S")
        add_box("Column_" + tag, (0.75, 0.75, 8.6), (x, sy * GY, 5.2), STEEL, parent=root)
        add_box("Bogie_" + tag, (1.0, 2.6, 0.7), (x, sy * GY, 1.15), GREY, parent=root)
        for wy in (-0.9, 0.9):
            add_cyl("Wheel_%s_%d" % (tag, int(wy * 10)), 0.45, 0.34,
                    (x, sy * GY + wy, 0.62), DARK, rot=(0, math.pi / 2, 0), parent=root)
    add_box("PortalBeam_" + side, (0.7, 2 * GY + 0.7, 0.6), (x, 0, 8.2), STEEL, parent=root)
    for sy in (-1, 1):
        ang = math.atan2(4.4, GY) * sy
        add_box("LegBrace_%s%d" % (side, sy), (0.35, 0.35, 5.0),
                (x, sy * GY * 0.5, 5.9), STEEL, rot=(ang, 0, 0), parent=root)

# ---------------------------------------------------------------- main girders + walkways
for sy in (-1, 1):
    tag = "N" if sy > 0 else "S"
    add_box("MainGirder_" + tag, (2 * SPAN + 1.6, 0.8, 1.3), (0, sy * GY, TOP + 0.65),
            STEEL, parent=root)
    add_box("Runway_" + tag, (2 * SPAN + 1.6, 0.26, 0.18), (0, sy * GY, TOP + 1.39),
            RAIL, parent=root)
    add_box("Walkway_" + tag, (2 * SPAN + 1.0, 0.9, 0.1), (0, sy * (GY + 0.85), TOP + 1.35),
            GREY, parent=root)
    for gx in range(-6, 7, 3):
        add_cyl("Stanchion_%s%d" % (tag, gx), 0.05, 1.0,
                (float(gx), sy * (GY + 1.25), TOP + 1.9), RAIL, seg=8, parent=root)
    add_cyl("Handrail_" + tag, 0.06, 12.5, (0, sy * (GY + 1.25), TOP + 2.4),
            RAIL, rot=(0, math.pi / 2, 0), seg=8, parent=root)

for bx in (-5.0, -1.7, 1.7, 5.0):
    add_box("GirderTie_%d" % int(bx * 10), (0.4, 2 * GY, 0.4), (bx, 0, TOP + 0.3),
            STEEL, parent=root)

# ---------------------------------------------------------------- trolley and hoist machinery
TX = 2.6
add_box("TrolleyFrame", (3.0, 2 * GY + 1.2, 0.5), (TX, 0, TOP + 1.72), GREY, parent=root)
for sy in (-1, 1):
    for wx in (-1.15, 1.15):
        add_cyl("TrolleyWheel_%d_%d" % (sy, int(wx * 10)), 0.28, 0.26,
                (TX + wx, sy * GY, TOP + 1.62), DARK, rot=(math.pi / 2, 0, 0),
                seg=14, parent=root)
add_box("MachineHouse", (1.5, 2.4, 1.2), (TX + 0.7, 0, TOP + 2.55), STEEL, parent=root)
add_cyl("HoistDrum", 0.5, 2.0, (TX - 0.85, 0, TOP + 2.3), DARK,
        rot=(math.pi / 2, 0, 0), parent=root)
add_box("OperatorCab", (1.6, 1.8, 1.9), (TX - 2.6, GY + 1.4, TOP - 0.4), STEEL, parent=root)
add_box("CabGlass", (1.4, 0.08, 1.0), (TX - 2.6, GY + 0.52, TOP + 0.15), DARK, parent=root)

# ---------------------------------------------------------------- rope reeving, hook block, hook
BLOCK_Z = 4.3
ROPE_TOP = TOP + 2.0
ROPE_BOT = BLOCK_Z + 0.45
for rx in (-0.42, 0.42):
    for ry in (-0.42, 0.42):
        add_cyl("Rope_%d_%d" % (int(rx * 100), int(ry * 100)), 0.035, ROPE_TOP - ROPE_BOT,
                (TX + rx, ry, (ROPE_TOP + ROPE_BOT) * 0.5), DARK, seg=8, parent=root)

add_box("HookBlock", (1.3, 1.1, 0.9), (TX, 0, BLOCK_Z), GREY, parent=root)
for sy in (-1, 1):
    add_cyl("Sheave_%d" % sy, 0.34, 0.16, (TX, sy * 0.3, BLOCK_Z + 0.3), DARK,
            rot=(math.pi / 2, 0, 0), seg=16, parent=root)
add_cyl("HookShank", 0.16, 0.6, (TX, 0, BLOCK_Z - 0.65), DARK, seg=14, parent=root)

# hook body: short straight shank continuing into a swept J profile
hook_pts = [(TX, 0.0, BLOCK_Z - 0.9), (TX, 0.0, BLOCK_Z - 1.25)]
HC, HR = BLOCK_Z - 1.70, 0.45
for i in range(19):
    a = math.radians(i * 250.0 / 18.0)
    hook_pts.append((TX + HR * math.sin(a), 0.0, HC + HR * math.cos(a)))
add_tube("Hook", hook_pts, 0.11, DARK, parent=root)

# a crate on the ground for scale
add_box("CargoCrate", (2.6, 2.0, 1.6), (-3.2, 3.0, 0.8),
        make_mat("Crate", (0.35, 0.24, 0.14), 0.0, 0.8))


# ---------------------------------------------------------------- camera, light, world
def add_camera(loc, target, lens=42):
    cd = bpy.data.cameras.new("Camera")
    cd.lens = lens
    cam = bpy.data.objects.new("Camera", cd)
    cam.location = loc
    cam.rotation_euler = (Vector(target) - Vector(loc)).to_track_quat('-Z', 'Y').to_euler()
    bpy.context.collection.objects.link(cam)
    bpy.context.scene.camera = cam
    return cam


add_camera((19.0, -23.0, 13.0), (0.5, 0.0, 6.0))

sun_data = bpy.data.lights.new("Sun", 'SUN')
sun_data.energy = 4.0
sun = bpy.data.objects.new("Sun", sun_data)
sun.location = (12, -14, 24)
sun.rotation_euler = (math.radians(52), math.radians(12), math.radians(35))
bpy.context.collection.objects.link(sun)

if bpy.context.scene.world is None:
    bpy.context.scene.world = bpy.data.worlds.new("World")
bpy.context.scene.world.use_nodes = True
bg = bpy.context.scene.world.node_tree.nodes["Background"]
bg.inputs[0].default_value = (0.42, 0.52, 0.66, 1.0)
bg.inputs[1].default_value = 1.0
