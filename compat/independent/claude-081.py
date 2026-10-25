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


def _finish(ob, mat, parent):
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
    return _finish(ob, mat, parent)


def add_cyl(name, radius, depth, loc, mat, rot=(0, 0, 0), seg=16, parent=None):
    me = bpy.data.meshes.new(name)
    bm = bmesh.new()
    bmesh.ops.create_cone(bm, cap_ends=True, cap_tris=False, segments=seg,
                          radius1=radius, radius2=radius, depth=depth)
    bm.to_mesh(me)
    bm.free()
    ob = bpy.data.objects.new(name, me)
    ob.location = loc
    ob.rotation_euler = rot
    return _finish(ob, mat, parent)


def add_cable(name, pts, radius, mat, parent=None):
    cu = bpy.data.curves.new(name, 'CURVE')
    cu.dimensions = '3D'
    cu.bevel_depth = radius
    cu.bevel_resolution = 2
    cu.use_fill_caps = True
    sp = cu.splines.new('POLY')
    sp.points.add(len(pts) - 1)
    for i, p in enumerate(pts):
        sp.points[i].co = (p[0], p[1], p[2], 1.0)
    ob = bpy.data.objects.new(name, cu)
    return _finish(ob, mat, parent)


# ---------------------------------------------------------------- parameters
clear_scene()

MAIN = 22.0        # half main span; towers at x = +/- MAIN
ANCHOR = 40.0      # anchorage position in x
DECK_Z = 3.0       # top of the deck surface
DECK_HW = 4.6      # deck half width
TOWER_TOP = 21.0
CABLE_Y = 4.2      # main cable offset from the centreline
MID_SAG = DECK_Z + 3.4
ANCH_Z = 5.0

STEEL = make_mat("BridgeSteel", (0.62, 0.18, 0.14), 0.5, 0.45)
CABLE = make_mat("CableSteel", (0.42, 0.43, 0.45), 0.9, 0.35)
DECKM = make_mat("Asphalt", (0.13, 0.13, 0.14), 0.0, 0.85)
CONC = make_mat("Concrete", (0.66, 0.65, 0.62), 0.0, 0.8)
PAINT = make_mat("LaneMarking", (0.86, 0.78, 0.18), 0.0, 0.6)
WATER = make_mat("Water", (0.05, 0.11, 0.18), 0.0, 0.12)

root = bpy.data.objects.new("SuspensionBridge", None)
bpy.context.collection.objects.link(root)


# ---------------------------------------------------------------- cable geometry
def main_span_z(x):
    """Parabolic main cable strung between the two tower saddles."""
    t = x / MAIN
    return MID_SAG + (TOWER_TOP - MID_SAG) * t * t


def side_span_z(x):
    """Back-stay running from the anchorage (u=0) up to the saddle (u=1)."""
    u = (abs(x) - ANCHOR) / (MAIN - ANCHOR)
    return ANCH_Z + (TOWER_TOP - ANCH_Z) * (u ** 1.6)


def cable_points(sy):
    pts = []
    for i in range(13):                                  # west back-stay
        x = -ANCHOR + (ANCHOR - MAIN) * i / 12.0
        pts.append((x, sy * CABLE_Y, side_span_z(x)))
    for i in range(1, 40):                               # main span
        x = -MAIN + 2.0 * MAIN * i / 40.0
        pts.append((x, sy * CABLE_Y, main_span_z(x)))
    for i in range(13):                                  # east back-stay
        x = MAIN + (ANCHOR - MAIN) * i / 12.0
        pts.append((x, sy * CABLE_Y, side_span_z(x)))
    return pts


# ---------------------------------------------------------------- water, piers, towers
add_box("Water", (150, 90, 0.2), (0, 0, -0.1), WATER)

for sx in (-1, 1):
    side = "E" if sx > 0 else "W"
    tx = sx * MAIN
    add_box("Pier_" + side, (9.0, 13.0, 3.0), (tx, 0, 1.0), CONC, parent=root)
    for sy in (-1, 1):
        tag = "%s%s" % (side, "N" if sy > 0 else "S")
        add_box("TowerLeg_" + tag, (2.4, 2.4, TOWER_TOP - 2.0),
                (tx, sy * CABLE_Y, (TOWER_TOP + 2.0) * 0.5), STEEL, parent=root)
        add_cyl("Saddle_" + tag, 1.0, 2.6, (tx, sy * CABLE_Y, TOWER_TOP + 0.2),
                CABLE, rot=(0, math.pi / 2, 0), parent=root)
    for bz in (DECK_Z - 1.6, DECK_Z + 4.5, TOWER_TOP - 1.2):
        add_box("TowerStrut_%s_%d" % (side, int(bz)), (1.8, 2 * CABLE_Y, 1.4),
                (tx, 0, bz), STEEL, parent=root)

# ---------------------------------------------------------------- anchorages and abutments
for sx in (-1, 1):
    side = "E" if sx > 0 else "W"
    add_box("Anchorage_" + side, (10.0, 14.0, 10.0), (sx * ANCHOR, 0, ANCH_Z - 5.0),
            CONC, parent=root)
    add_box("Abutment_" + side, (5.0, 12.0, DECK_Z + 1.2),
            (sx * (ANCHOR + 6.5), 0, (DECK_Z - 1.0) * 0.5), CONC, parent=root)

# ---------------------------------------------------------------- deck structure
DECK_LEN = 2 * ANCHOR + 4.0
add_box("DeckSlab", (DECK_LEN, 2 * DECK_HW, 0.35), (0, 0, DECK_Z - 0.18), DECKM, parent=root)
add_box("StiffeningGirder", (DECK_LEN, 2 * DECK_HW - 1.2, 1.5),
        (0, 0, DECK_Z - 1.1), STEEL, parent=root)
for sy in (-1, 1):
    add_box("EdgeBeam_%d" % sy, (DECK_LEN, 0.5, 1.0),
            (0, sy * (DECK_HW - 0.25), DECK_Z - 0.5), STEEL, parent=root)
    add_box("Parapet_%d" % sy, (DECK_LEN, 0.2, 1.1),
            (0, sy * (DECK_HW - 0.1), DECK_Z + 0.55), STEEL, parent=root)

n_beams = int(DECK_LEN // 4.0)
for i in range(n_beams + 1):
    x = -DECK_LEN * 0.5 + i * 4.0
    add_box("FloorBeam_%02d" % i, (0.5, 2 * CABLE_Y + 0.6, 0.7),
            (x, 0, DECK_Z - 2.1), STEEL, parent=root)

for i in range(-19, 20):
    add_box("LaneMark_%02d" % (i + 19), (2.4, 0.22, 0.06),
            (i * 2.0, 0, DECK_Z + 0.03), PAINT, parent=root)

# ---------------------------------------------------------------- main cables + hangers
for sy in (-1, 1):
    tag = "N" if sy > 0 else "S"
    add_cable("MainCable_" + tag, cable_points(sy), 0.28, CABLE, parent=root)

    n_h = 19
    for i in range(1, n_h):
        x = -MAIN + 2.0 * MAIN * i / float(n_h)
        top, bot = main_span_z(x), DECK_Z + 0.4
        add_cyl("Hanger_%s_%02d" % (tag, i), 0.07, top - bot,
                (x, sy * CABLE_Y, (top + bot) * 0.5), CABLE, seg=8, parent=root)

    for i in range(1, 5):                       # side-span hangers
        for sx in (-1, 1):
            x = sx * (MAIN + (ANCHOR - MAIN) * i / 5.0)
            top, bot = side_span_z(x), DECK_Z + 0.4
            if top - bot < 0.6:
                continue
            add_cyl("SideHanger_%s%d_%d" % (tag, i, sx), 0.06, top - bot,
                    (x, sy * CABLE_Y, (top + bot) * 0.5), CABLE, seg=8, parent=root)

# lamp posts along the parapets
for i in range(-4, 5):
    for sy in (-1, 1):
        x = i * 9.0
        add_cyl("LampPost_%d_%d" % (i + 4, sy), 0.12, 3.4,
                (x, sy * (DECK_HW - 0.5), DECK_Z + 1.7), STEEL, seg=10, parent=root)
        add_box("LampHead_%d_%d" % (i + 4, sy), (0.7, 0.3, 0.16),
                (x, sy * (DECK_HW - 0.9), DECK_Z + 3.4), CABLE, parent=root)


# ---------------------------------------------------------------- camera, light, world
def add_camera(loc, target, lens=40):
    cd = bpy.data.cameras.new("Camera")
    cd.lens = lens
    cam = bpy.data.objects.new("Camera", cd)
    cam.location = loc
    cam.rotation_euler = (Vector(target) - Vector(loc)).to_track_quat('-Z', 'Y').to_euler()
    bpy.context.collection.objects.link(cam)
    bpy.context.scene.camera = cam
    return cam


add_camera((46.0, -62.0, 26.0), (0.0, 0.0, 9.0))

sun_data = bpy.data.lights.new("Sun", 'SUN')
sun_data.energy = 4.5
sun = bpy.data.objects.new("Sun", sun_data)
sun.location = (30, -40, 55)
sun.rotation_euler = (math.radians(48), math.radians(-14), math.radians(28))
bpy.context.collection.objects.link(sun)

if bpy.context.scene.world is None:
    bpy.context.scene.world = bpy.data.worlds.new("World")
bpy.context.scene.world.use_nodes = True
bg = bpy.context.scene.world.node_tree.nodes["Background"]
bg.inputs[0].default_value = (0.38, 0.50, 0.68, 1.0)
bg.inputs[1].default_value = 1.0
