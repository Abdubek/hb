import bpy
from math import radians, cos, sin
from mathutils import Vector

bpy.ops.wm.read_factory_settings(use_empty=True)
scene = bpy.context.scene
try:
    scene.render.engine = 'BLENDER_EEVEE_NEXT'
except TypeError:
    pass
C = bpy.context


def mat(name, color, rough=0.5, metal=0.0):
    m = bpy.data.materials.new(name)
    m.use_nodes = True
    b = m.node_tree.nodes["Principled BSDF"]
    b.inputs["Base Color"].default_value = (*color, 1.0)
    b.inputs["Roughness"].default_value = rough
    b.inputs["Metallic"].default_value = metal
    return m


def box(name, size, loc, material=None, rot=(0, 0, 0)):
    bpy.ops.mesh.primitive_cube_add(size=1, location=loc, rotation=rot)
    ob = C.object
    ob.name = name
    ob.scale = size
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    if material:
        ob.data.materials.append(material)
    return ob


def cyl(name, r, h, loc, material=None, rot=(0, 0, 0), verts=24):
    bpy.ops.mesh.primitive_cylinder_add(vertices=verts, radius=r, depth=h,
                                        location=loc, rotation=rot)
    ob = C.object
    ob.name = name
    if material:
        ob.data.materials.append(material)
    return ob


def sphere(name, r, loc, material=None, segs=20, rings=12):
    bpy.ops.mesh.primitive_uv_sphere_add(segments=segs, ring_count=rings,
                                         radius=r, location=loc)
    ob = C.object
    ob.name = name
    if material:
        ob.data.materials.append(material)
    return ob


def smooth(ob, angle=40.0):
    for p in ob.data.polygons:
        p.use_smooth = True
    m = ob.modifiers.new("EdgeSplit", 'EDGE_SPLIT')
    m.split_angle = radians(angle)
    return ob


def bevel(ob, width=0.006, segments=3, angle=40.0):
    m = ob.modifiers.new("Bevel", 'BEVEL')
    m.width = width
    m.segments = segments
    m.limit_method = 'ANGLE'
    m.angle_limit = radians(angle)
    return ob


def cyl_between(name, p1, p2, r, material=None, verts=20):
    p1, p2 = Vector(p1), Vector(p2)
    d = p2 - p1
    ob = cyl(name, r, d.length, (p1 + p2) * 0.5, material, verts=verts)
    ob.rotation_mode = 'QUATERNION'
    ob.rotation_quaternion = d.to_track_quat('Z', 'Y')
    bpy.ops.object.transform_apply(location=False, rotation=True, scale=False)
    smooth(ob)
    return ob


def tube(name, points, r, material, joints=True):
    for i in range(len(points) - 1):
        cyl_between("%s_seg%d" % (name, i), points[i], points[i + 1], r, material)
    if joints:
        for i, p in enumerate(points[1:-1], 1):
            smooth(sphere("%s_j%d" % (name, i), r, p, material))


# ---------------------------------------------------------------- materials
M_FLOOR = mat("Floor", (0.42, 0.41, 0.40), rough=0.35)
M_CHROME = mat("Chrome", (0.78, 0.79, 0.80), rough=0.16, metal=1.0)
M_STEEL = mat("Steel", (0.40, 0.41, 0.43), rough=0.36, metal=1.0)
M_RUBBER = mat("Rubber", (0.035, 0.035, 0.038), rough=0.85)
M_GRIP = mat("Grip", (0.09, 0.10, 0.12), rough=0.72)
M_DECK = mat("Deck", (0.16, 0.17, 0.19), rough=0.62)
M_PLACARD = mat("Placard", (0.75, 0.15, 0.09), rough=0.55)

M_CASE_A = mat("CaseNavy", (0.055, 0.075, 0.155), rough=0.44)
M_CASE_B = mat("CaseOlive", (0.19, 0.20, 0.13), rough=0.62)
M_CASE_C = mat("CaseRed", (0.36, 0.055, 0.055), rough=0.40)
M_CASE_D = mat("CaseTan", (0.40, 0.29, 0.17), rough=0.66)
M_TRIM = mat("CaseTrim", (0.06, 0.06, 0.065), rough=0.55)
M_ZIP = mat("Zipper", (0.55, 0.52, 0.40), rough=0.34, metal=0.9)
M_TAG = mat("Tag", (0.88, 0.86, 0.80), rough=0.70)

# ---------------------------------------------------------------- floor
box("Floor", (14.0, 14.0, 0.06), (0, 0, -0.03), M_FLOOR)
for i in range(-4, 5):
    box("TileX%d" % i, (0.012, 14.0, 0.004), (i * 1.2, 0, 0.002), M_DECK)
    box("TileY%d" % i, (14.0, 0.012, 0.004), (0, i * 1.2, 0.002), M_DECK)

# ---------------------------------------------------------------- cart frame
DECK_Z = 0.315
LEN, WID = 0.92, 0.56

deck = box("Deck", (LEN, WID, 0.028), (0, 0, DECK_Z), M_DECK)
bevel(deck, 0.010, 3)
for i in range(7):
    box("DeckRib%d" % i, (0.055, WID - 0.05, 0.008),
        (-LEN / 2 + 0.08 + i * 0.13, 0, DECK_Z + 0.018), M_STEEL)

rail_pts = [(-LEN / 2, -WID / 2, DECK_Z - 0.02), (LEN / 2, -WID / 2, DECK_Z - 0.02),
            (LEN / 2, WID / 2, DECK_Z - 0.02), (-LEN / 2, WID / 2, DECK_Z - 0.02),
            (-LEN / 2, -WID / 2, DECK_Z - 0.02)]
tube("DeckRail", rail_pts, 0.014, M_CHROME)

# four swivel casters
for sx in (-1, 1):
    for sy in (-1, 1):
        px, py = sx * (LEN / 2 - 0.10), sy * (WID / 2 - 0.07)
        smooth(cyl("CasterStem_%d%d" % (sx, sy), 0.018, 0.10,
                   (px, py, DECK_Z - 0.085), M_CHROME))
        fork = box("CasterFork_%d%d" % (sx, sy), (0.05, 0.075, 0.075),
                   (px, py, DECK_Z - 0.145), M_STEEL)
        bevel(fork, 0.008, 2)
        w = cyl("Wheel_%d%d" % (sx, sy), 0.072, 0.042, (px - 0.02, py, 0.072),
                M_RUBBER, rot=(radians(90), 0, 0), verts=28)
        smooth(w)
        bevel(w, 0.008, 2)
        smooth(cyl("Hub_%d%d" % (sx, sy), 0.024, 0.046, (px - 0.02, py, 0.072),
                   M_CHROME, rot=(radians(90), 0, 0), verts=16))

# rear uprights bending back into the push handle
HB_Z = 1.02
hb_y = WID / 2 - 0.035
for sy in (-1, 1):
    y = sy * hb_y
    pts = [(-LEN / 2 + 0.03, y, DECK_Z - 0.03),
           (-LEN / 2 + 0.03, y, 0.86),
           (-LEN / 2 - 0.01, y, 0.955),
           (-LEN / 2 - 0.07, y, HB_Z)]
    tube("Upright%d" % sy, pts, 0.017, M_CHROME)

cyl_between("HandleBar", (-LEN / 2 - 0.07, -hb_y, HB_Z),
            (-LEN / 2 - 0.07, hb_y, HB_Z), 0.017, M_CHROME)
for sy in (-1, 1):
    g = cyl("Grip%d" % sy, 0.024, 0.16, (-LEN / 2 - 0.07, sy * (hb_y - 0.09), HB_Z),
            M_GRIP, rot=(radians(90), 0, 0), verts=24)
    smooth(g)
    bevel(g, 0.006, 2)
cyl_between("BrakeLever", (-LEN / 2 - 0.055, -hb_y + 0.03, HB_Z - 0.075),
            (-LEN / 2 - 0.055, hb_y - 0.03, HB_Z - 0.075), 0.010, M_STEEL)

# rear retaining frame
for i, z in enumerate((0.50, 0.63, 0.76)):
    cyl_between("BackBar%d" % i, (-LEN / 2 + 0.03, -hb_y, z),
                (-LEN / 2 + 0.03, hb_y, z), 0.011, M_CHROME)

# front bumper lip that keeps the load on the deck
front_pts = [(LEN / 2 - 0.02, -hb_y, DECK_Z + 0.01),
             (LEN / 2 + 0.02, -hb_y, 0.44),
             (LEN / 2 + 0.02, hb_y, 0.44),
             (LEN / 2 - 0.02, hb_y, DECK_Z + 0.01)]
tube("FrontLip", front_pts, 0.015, M_CHROME)

plc = box("Placard", (0.012, 0.22, 0.13), (-LEN / 2 - 0.075, 0.0, HB_Z - 0.16),
          M_PLACARD, rot=(0, radians(-10), 0))
bevel(plc, 0.006, 2)


# ---------------------------------------------------------------- suitcases
def make_suitcase(name, dims, loc, rot_z, shell, hard=True, handle_up=False,
                  wheels=True, tag=False):
    w, d, h = dims
    body = box(name, (w, d, h), loc, shell, rot=(0, 0, rot_z))
    bevel(body, min(0.045, min(dims) * 0.28), 4, angle=55)
    smooth(body, 50)

    cx, cy, cz = loc
    cr, sr = cos(rot_z), sin(rot_z)

    def place(lx, ly, lz):
        return (cx + lx * cr - ly * sr, cy + lx * sr + ly * cr, cz + lz)

    band = box(name + "_Band", (w + 0.006, d + 0.006, 0.016), place(0, 0, h * 0.10),
               M_ZIP, rot=(0, 0, rot_z))
    bevel(band, 0.005, 2)

    # corner bumpers
    for sx in (-1, 1):
        for sy in (-1, 1):
            for sz in (-1, 1):
                bmp = box(name + "_Bmp%d%d%d" % (sx, sy, sz), (0.055, 0.055, 0.055),
                          place(sx * (w / 2 - 0.012), sy * (d / 2 - 0.012),
                                sz * (h / 2 - 0.012)), M_TRIM, rot=(0, 0, rot_z))
                bevel(bmp, 0.022, 4, angle=60)
                smooth(bmp, 55)

    gh = box(name + "_Handle", (0.15, 0.030, 0.026), place(0, 0, h / 2 + 0.022),
             M_TRIM, rot=(0, 0, rot_z))
    bevel(gh, 0.010, 3)
    for sx in (-1, 1):
        box(name + "_HMount%d" % sx, (0.030, 0.036, 0.030),
            place(sx * 0.062, 0, h / 2 + 0.004), M_TRIM, rot=(0, 0, rot_z))

    if hard:
        for i in range(-2, 3):
            box(name + "_Rib%d" % i, (0.014, d - 0.05, h - 0.09),
                place(i * (w * 0.19), d / 2 - 0.004, 0.0), M_TRIM, rot=(0, 0, rot_z))

    if handle_up:
        for sx in (-1, 1):
            t = cyl(name + "_Tele%d" % sx, 0.011, 0.30,
                    place(sx * 0.09, d / 2 - 0.05, h / 2 + 0.15), M_CHROME,
                    rot=(0, 0, rot_z), verts=16)
            smooth(t)
        tb = box(name + "_TeleGrip", (0.24, 0.034, 0.032),
                 place(0, d / 2 - 0.05, h / 2 + 0.31), M_GRIP, rot=(0, 0, rot_z))
        bevel(tb, 0.012, 3)
    else:
        box(name + "_TeleCap", (0.24, 0.05, 0.016), place(0, d / 2 - 0.05, h / 2 + 0.006),
            M_TRIM, rot=(0, 0, rot_z))

    if wheels:
        for sx in (-1, 1):
            for sy in (-1, 1):
                wh = cyl(name + "_W%d%d" % (sx, sy), 0.030, 0.020,
                         place(sx * (w / 2 - 0.055), sy * (d / 2 - 0.045),
                               -h / 2 - 0.022), M_RUBBER,
                         rot=(radians(90), 0, rot_z), verts=18)
                smooth(wh)
                box(name + "_WH%d%d" % (sx, sy), (0.05, 0.05, 0.03),
                    place(sx * (w / 2 - 0.055), sy * (d / 2 - 0.045), -h / 2 + 0.006),
                    M_TRIM, rot=(0, 0, rot_z))

    if tag:
        smooth(cyl(name + "_TagLoop", 0.004, 0.10, place(0.05, 0, h / 2 - 0.03),
                   M_TRIM, rot=(0, 0, rot_z), verts=10))
        t = box(name + "_Tag", (0.055, 0.006, 0.035), place(0.05, 0, h / 2 - 0.08),
                M_TAG, rot=(0, 0, rot_z))
        bevel(t, 0.004, 2)


TOP = DECK_Z + 0.014

# bottom of the stack: large hardside case lying flat
make_suitcase("CaseBig", (0.74, 0.48, 0.24), (0.02, 0.0, TOP + 0.12),
              radians(2), M_CASE_A, hard=True, wheels=False, tag=True)
# mid: softside case, cross-stacked
make_suitcase("CaseMid", (0.62, 0.40, 0.20), (-0.02, 0.02, TOP + 0.34),
              radians(-8), M_CASE_D, hard=False, wheels=False)
# top: small cabin bag standing upright with its handle out
make_suitcase("CaseSmall", (0.36, 0.22, 0.46), (0.06, -0.02, TOP + 0.67),
              radians(14), M_CASE_C, hard=True, handle_up=True, wheels=True, tag=True)
# a fourth case standing on the deck against the rear frame
make_suitcase("CaseRear", (0.34, 0.20, 0.50), (-0.30, 0.0, TOP + 0.26),
              radians(90), M_CASE_B, hard=True, wheels=True)
# a soft bag on the floor beside the cart
make_suitcase("CaseFloor", (0.46, 0.28, 0.28), (0.75, -0.62, 0.145),
              radians(-24), M_CASE_D, hard=False, wheels=False, tag=True)

# ---------------------------------------------------------------- lighting
world = bpy.data.worlds.new("World")
scene.world = world
world.use_nodes = True
world.node_tree.nodes["Background"].inputs[0].default_value = (0.42, 0.45, 0.50, 1.0)
world.node_tree.nodes["Background"].inputs[1].default_value = 0.7

key = bpy.data.lights.new("Key", 'AREA')
key.energy = 700.0
key.size = 3.0
ko = bpy.data.objects.new("Key", key)
scene.collection.objects.link(ko)
ko.location = (2.2, -2.4, 3.4)
ko.rotation_euler = (radians(38), 0, radians(42))

fill = bpy.data.lights.new("Fill", 'AREA')
fill.energy = 220.0
fill.size = 4.0
fo = bpy.data.objects.new("Fill", fill)
scene.collection.objects.link(fo)
fo.location = (-2.8, -1.6, 2.6)
fo.rotation_euler = (radians(58), 0, radians(-52))

rim = bpy.data.lights.new("Rim", 'AREA')
rim.energy = 300.0
rim.size = 2.0
ro = bpy.data.objects.new("Rim", rim)
scene.collection.objects.link(ro)
ro.location = (-1.0, 3.0, 2.4)
ro.rotation_euler = (radians(65), 0, radians(190))

# ---------------------------------------------------------------- camera
cam_data = bpy.data.cameras.new("Camera")
cam_data.lens = 55.0
cam = bpy.data.objects.new("Camera", cam_data)
scene.collection.objects.link(cam)
cam.location = (2.05, -2.15, 1.55)
target = Vector((-0.05, 0.0, 0.72))
cam.rotation_euler = (target - cam.location).to_track_quat('-Z', 'Y').to_euler()
cam_data.dof.use_dof = True
cam_data.dof.focus_distance = (target - cam.location).length
cam_data.dof.aperture_fstop = 4.5
scene.camera = cam
