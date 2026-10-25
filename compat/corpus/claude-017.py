"""claude-017 - Shop counter with display shelves and products.

Builds the scene only: no rendering, no file output, no external assets.
"""

import bpy
import bmesh
import math
import random
from mathutils import Vector

random.seed(20170)


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


def shade_auto(ob, angle=math.radians(35.0)):
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


def _finish(bm, name, loc, rot, mat, smooth, smooth_angle):
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    me = bpy.data.meshes.new(name)
    bm.to_mesh(me)
    bm.free()
    ob = bpy.data.objects.new(name, me)
    ob.location = loc
    ob.rotation_euler = rot
    bpy.context.collection.objects.link(ob)
    if mat is not None:
        me.materials.append(mat)
    if smooth:
        shade_auto(ob, smooth_angle)
    return ob


def add_box(name, size, loc=(0, 0, 0), rot=(0, 0, 0), mat=None,
            bevel=0.0, seg=2, smooth=False):
    bm = bmesh.new()
    bmesh.ops.create_cube(bm, size=1.0)
    bmesh.ops.scale(bm, vec=Vector(size), verts=bm.verts)
    if bevel > 0.0:
        bmesh.ops.bevel(bm, geom=list(bm.verts) + list(bm.edges) + list(bm.faces),
                        offset=bevel, offset_type='OFFSET', segments=seg,
                        profile=0.5, affect='EDGES', clamp_overlap=True)
    return _finish(bm, name, loc, rot, mat, smooth, math.radians(35.0))


def add_cyl(name, radius, depth, loc=(0, 0, 0), rot=(0, 0, 0), mat=None,
            segments=32, bevel=0.0):
    bm = bmesh.new()
    bmesh.ops.create_cone(bm, cap_ends=True, cap_tris=False, segments=segments,
                          radius1=radius, radius2=radius, depth=depth)
    if bevel > 0.0:
        bmesh.ops.bevel(bm, geom=list(bm.verts) + list(bm.edges) + list(bm.faces),
                        offset=bevel, offset_type='OFFSET', segments=2,
                        profile=0.5, affect='EDGES', clamp_overlap=True)
    return _finish(bm, name, loc, rot, mat, True, math.radians(40.0))


def add_cone(name, r1, r2, depth, loc=(0, 0, 0), rot=(0, 0, 0), mat=None,
             segments=24):
    bm = bmesh.new()
    bmesh.ops.create_cone(bm, cap_ends=True, cap_tris=False, segments=segments,
                          radius1=r1, radius2=r2, depth=depth)
    return _finish(bm, name, loc, rot, mat, True, math.radians(45.0))


def add_sphere(name, radius, loc=(0, 0, 0), mat=None, useg=24, vseg=14,
               scale=(1, 1, 1)):
    bm = bmesh.new()
    bmesh.ops.create_uvsphere(bm, u_segments=useg, v_segments=vseg, radius=radius)
    bmesh.ops.scale(bm, vec=Vector(scale), verts=bm.verts)
    return _finish(bm, name, loc, (0, 0, 0), mat, True, math.radians(60.0))


def aim(ob, target):
    d = Vector(target) - ob.location
    ob.rotation_euler = d.to_track_quat('-Z', 'Y').to_euler()


def add_light(name, ltype, loc, energy, color=(1.0, 1.0, 1.0), size=1.0,
              target=None, spot_size=math.radians(50.0)):
    data = bpy.data.lights.new(name, ltype)
    data.energy = energy
    data.color = color
    if ltype == 'AREA':
        data.size = size
    elif ltype == 'SPOT':
        data.spot_size = spot_size
        data.spot_blend = 0.35
        data.shadow_soft_size = size
    elif ltype == 'SUN':
        data.angle = math.radians(3.0)
    else:
        data.shadow_soft_size = size
    ob = bpy.data.objects.new(name, data)
    ob.location = loc
    bpy.context.collection.objects.link(ob)
    if target is not None:
        aim(ob, target)
    return ob


def setup_world(color=(0.05, 0.05, 0.06), strength=1.0):
    world = bpy.data.worlds.new("World")
    bpy.context.scene.world = world
    world.use_nodes = True
    bg = world.node_tree.nodes["Background"]
    bg.inputs[0].default_value = (color[0], color[1], color[2], 1.0)
    bg.inputs[1].default_value = strength


def add_camera(loc, target, lens=45.0, name="Camera"):
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
setup_world((0.05, 0.05, 0.055), 1.0)

FLOOR = new_material("FloorTile", (0.24, 0.22, 0.20), rough=0.42, coat=0.25)
WALL = new_material("Wall", (0.82, 0.79, 0.72), rough=0.75)
CAB = new_material("CabinetPaint", (0.10, 0.19, 0.20), rough=0.38, coat=0.4)
CAB_TRIM = new_material("CabinetTrim", (0.72, 0.55, 0.28), metallic=1.0, rough=0.3)
STONE = new_material("CounterTop", (0.09, 0.09, 0.10), rough=0.18, coat=0.6)
SHELF_W = new_material("ShelfWood", (0.44, 0.28, 0.15), rough=0.5)
METAL = new_material("Metal", (0.66, 0.67, 0.70), metallic=1.0, rough=0.28)
DARK = new_material("DarkPlastic", (0.06, 0.06, 0.07), rough=0.4)
GLASS = new_material("Glass", (0.86, 0.92, 0.9), rough=0.02, transmission=1.0,
                     alpha=0.13, ior=1.5)
STRIP = new_material("ShelfStrip", (1.0, 0.97, 0.9),
                     emission=(1.0, 0.94, 0.82), emit_strength=7.0)
SCREEN = new_material("Screen", (0.02, 0.03, 0.05),
                      emission=(0.35, 0.62, 0.9), emit_strength=3.0)
PASTRY = new_material("Pastry", (0.70, 0.44, 0.18), rough=0.55)
ICING = new_material("Icing", (0.92, 0.86, 0.78), rough=0.35)
PAPER = new_material("KraftPaper", (0.66, 0.50, 0.33), rough=0.8)
FRUIT_A = new_material("FruitRed", (0.72, 0.10, 0.10), rough=0.32, coat=0.5)
FRUIT_B = new_material("FruitGreen", (0.42, 0.62, 0.16), rough=0.34, coat=0.5)

PALETTE = [(0.74, 0.14, 0.11), (0.92, 0.60, 0.09), (0.13, 0.34, 0.66),
           (0.17, 0.53, 0.26), (0.86, 0.83, 0.30), (0.55, 0.22, 0.48),
           (0.90, 0.90, 0.87), (0.22, 0.20, 0.19), (0.05, 0.55, 0.55)]
PROD_MATS = [new_material("Product_%02d" % i, c, rough=0.32, coat=0.35)
             for i, c in enumerate(PALETTE)]
LABEL_MATS = [new_material("Label_%02d" % i, c, rough=0.55)
              for i, c in enumerate(PALETTE)]


def pick(seq):
    return seq[random.randrange(len(seq))]


# ----------------------------------------------------------------------------
# room
# ----------------------------------------------------------------------------

add_box("Floor", (9.0, 9.0, 0.12), (0.0, 0.6, -0.06), mat=FLOOR)
add_box("BackWall", (9.0, 0.14, 3.30), (0.0, 2.42, 1.65), mat=WALL)
add_box("SideWallL", (0.14, 5.0, 3.30), (-3.4, 0.0, 1.65), mat=WALL)
add_box("Skirting", (9.0, 0.05, 0.12), (0.0, 2.32, 0.06), mat=SHELF_W)
add_box("Ceiling", (9.0, 9.0, 0.14), (0.0, 0.6, 3.32), mat=WALL)


# ----------------------------------------------------------------------------
# counter
# ----------------------------------------------------------------------------

CW, CD, CH = 2.60, 0.72, 0.94   # cabinet body
TOP_Z = CH + 0.05               # top surface height (0.99 + half thickness)

add_box("CounterBody", (CW, CD, CH), (0.0, 0.0, CH * 0.5 + 0.06),
        mat=CAB, bevel=0.01)
add_box("CounterPlinth", (CW - 0.10, CD - 0.10, 0.06), (0.0, 0.0, 0.03),
        mat=DARK)
top = add_box("CounterTop", (CW + 0.14, CD + 0.13, 0.055),
              (0.0, -0.03, CH + 0.06 + 0.028), mat=STONE, bevel=0.008)
TOP_Z = CH + 0.06 + 0.055       # working surface height

# front panelling: three recessed panels with brass trim
for i in range(3):
    px = -CW * 0.5 + CW / 6.0 + i * CW / 3.0
    add_box("FrontPanel_%d" % i, (CW / 3.0 - 0.10, 0.02, CH - 0.22),
            (px, -CD * 0.5 - 0.005, CH * 0.5 + 0.06),
            mat=new_material("PanelInset_%d" % i, (0.08, 0.15, 0.16), rough=0.45))
    add_box("FrontTrim_%d" % i, (CW / 3.0 - 0.06, 0.012, 0.012),
            (px, -CD * 0.5 - 0.012, CH * 0.5 + 0.06 + (CH - 0.22) * 0.5),
            mat=CAB_TRIM)

# storage side: two shelves and a drawer visible from behind
add_box("CounterShelf", (CW - 0.12, CD - 0.16, 0.025), (0.0, 0.02, 0.52),
        mat=SHELF_W)
add_box("CounterDrawer", (0.62, 0.03, 0.16), (-0.85, -CD * 0.5 - 0.02, 0.80),
        mat=CAB_TRIM, bevel=0.006)
add_cyl("DrawerPull", 0.012, 0.24, (-0.85, -CD * 0.5 - 0.05, 0.80),
        rot=(0, math.radians(90), 0), mat=CAB_TRIM, segments=16)


# ----------------------------------------------------------------------------
# glazed display case on the counter
# ----------------------------------------------------------------------------

CASE_X, CASE_Y = 0.62, 0.0
CW2, CD2, CH2 = 0.98, 0.46, 0.40
base_z = TOP_Z

add_box("CaseBase", (CW2, CD2, 0.03), (CASE_X, CASE_Y, base_z + 0.015),
        mat=METAL, bevel=0.004)
add_box("CaseGlassFront", (CW2 - 0.04, 0.008, CH2 - 0.05),
        (CASE_X, CASE_Y - CD2 * 0.5 + 0.02, base_z + 0.03 + (CH2 - 0.05) * 0.5),
        mat=GLASS)
add_box("CaseGlassBack", (CW2 - 0.04, 0.008, CH2 - 0.05),
        (CASE_X, CASE_Y + CD2 * 0.5 - 0.02, base_z + 0.03 + (CH2 - 0.05) * 0.5),
        mat=GLASS)
for sx in (-1, 1):
    add_box("CaseGlassSide_%d" % sx, (0.008, CD2 - 0.05, CH2 - 0.05),
            (CASE_X + sx * (CW2 * 0.5 - 0.02), CASE_Y,
             base_z + 0.03 + (CH2 - 0.05) * 0.5), mat=GLASS)
    for sy in (-1, 1):
        add_box("CaseCorner_%d_%d" % (sx, sy), (0.018, 0.018, CH2),
                (CASE_X + sx * (CW2 * 0.5 - 0.012),
                 CASE_Y + sy * (CD2 * 0.5 - 0.012), base_z + CH2 * 0.5),
                mat=METAL, bevel=0.002)
add_box("CaseTop", (CW2, CD2, 0.012), (CASE_X, CASE_Y, base_z + CH2 + 0.006),
        mat=GLASS)
add_box("CaseLight", (CW2 - 0.10, 0.05, 0.012),
        (CASE_X, CASE_Y + 0.16, base_z + CH2 - 0.02), mat=STRIP)

# two glass shelves with pastries
for level, sz in enumerate((0.055, 0.20)):
    add_box("CaseShelf_%d" % level, (CW2 - 0.07, CD2 - 0.09, 0.008),
            (CASE_X, CASE_Y, base_z + sz), mat=GLASS)
    for i in range(5):
        px = CASE_X - 0.36 + i * 0.18
        py = CASE_Y + random.uniform(-0.05, 0.05)
        pz = base_z + sz + 0.008
        kind = random.random()
        if kind < 0.4:
            add_cyl("Pastry_%d_%d" % (level, i), 0.045, 0.045,
                    (px, py, pz + 0.023), mat=PASTRY, segments=20, bevel=0.012)
            add_cyl("PastryTop_%d_%d" % (level, i), 0.040, 0.010,
                    (px, py, pz + 0.050), mat=ICING, segments=20, bevel=0.004)
        elif kind < 0.75:
            add_box("Cake_%d_%d" % (level, i), (0.085, 0.085, 0.055),
                    (px, py, pz + 0.028), rot=(0, 0, random.uniform(-0.3, 0.3)),
                    mat=PASTRY, bevel=0.008)
            add_sphere("Berry_%d_%d" % (level, i), 0.012,
                       (px, py, pz + 0.062), mat=FRUIT_A, useg=16, vseg=10)
        else:
            add_sphere("Bun_%d_%d" % (level, i), 0.040, (px, py, pz + 0.030),
                       mat=PASTRY, useg=20, vseg=12, scale=(1.0, 1.0, 0.72))


# ----------------------------------------------------------------------------
# till, card reader and counter-top goods
# ----------------------------------------------------------------------------

TILL_X = -0.78
add_box("TillBody", (0.30, 0.34, 0.10), (TILL_X, 0.02, TOP_Z + 0.05),
        mat=DARK, bevel=0.008)
add_box("TillKeys", (0.24, 0.20, 0.012), (TILL_X, -0.07, TOP_Z + 0.104),
        mat=new_material("KeyPad", (0.14, 0.14, 0.15), rough=0.6), bevel=0.003)
for r in range(3):
    for c in range(4):
        add_box("TillKey_%d_%d" % (r, c), (0.036, 0.030, 0.008),
                (TILL_X - 0.075 + c * 0.05, -0.125 + r * 0.045, TOP_Z + 0.113),
                mat=new_material("Key_%d_%d" % (r, c), (0.55, 0.55, 0.56),
                                 rough=0.5), bevel=0.002)
add_box("TillScreenBody", (0.28, 0.02, 0.20), (TILL_X, 0.12, TOP_Z + 0.20),
        rot=(math.radians(-16), 0, 0), mat=DARK, bevel=0.006)
add_box("TillScreen", (0.245, 0.006, 0.165), (TILL_X, 0.104, TOP_Z + 0.202),
        rot=(math.radians(-16), 0, 0), mat=SCREEN)

add_box("CardReader", (0.09, 0.14, 0.03), (-0.20, -0.16, TOP_Z + 0.015),
        mat=DARK, bevel=0.006)
add_box("CardReaderFace", (0.075, 0.115, 0.008), (-0.20, -0.16, TOP_Z + 0.032),
        rot=(math.radians(-12), 0, 0), mat=SCREEN)

# stack of paper bags and a bowl of fruit
for i in range(4):
    add_box("Bag_%d" % i, (0.20, 0.26, 0.012),
            (-1.06, -0.20, TOP_Z + 0.007 + i * 0.013),
            rot=(0, 0, math.radians(random.uniform(-4, 4))), mat=PAPER)

add_cyl("Bowl", 0.13, 0.06, (0.0, 0.20, TOP_Z + 0.03), mat=SHELF_W,
        segments=32, bevel=0.014)
for i in range(6):
    ang = i * math.tau / 6.0
    add_sphere("Fruit_%d" % i, 0.032,
               (0.0 + math.cos(ang) * 0.055, 0.20 + math.sin(ang) * 0.055,
                TOP_Z + 0.075),
               mat=FRUIT_A if i % 2 == 0 else FRUIT_B, useg=20, vseg=12)
add_sphere("FruitTop", 0.032, (0.0, 0.20, TOP_Z + 0.115), mat=FRUIT_B,
           useg=20, vseg=12)

# a tall glass jar of sweets
add_cyl("Jar", 0.085, 0.26, (1.36, 0.14, TOP_Z + 0.13), mat=GLASS, segments=32)
add_cyl("JarLid", 0.088, 0.03, (1.36, 0.14, TOP_Z + 0.275), mat=METAL,
        segments=32, bevel=0.006)
for i in range(16):
    add_sphere("Sweet_%d" % i, 0.018,
               (1.36 + random.uniform(-0.05, 0.05),
                0.14 + random.uniform(-0.05, 0.05),
                TOP_Z + 0.03 + random.uniform(0.0, 0.13)),
               mat=pick(PROD_MATS), useg=14, vseg=8)


# ----------------------------------------------------------------------------
# back display shelving unit, procedurally stocked
# ----------------------------------------------------------------------------

SH_W, SH_D, SH_H = 2.90, 0.36, 2.15
SH_Y = 2.10
add_box("ShelfBack", (SH_W, 0.02, SH_H), (0.0, SH_Y + SH_D * 0.5, SH_H * 0.5),
        mat=new_material("ShelfBackBoard", (0.30, 0.19, 0.11), rough=0.62))
for sx in (-1, 1):
    add_box("ShelfUpright_%d" % sx, (0.05, SH_D, SH_H),
            (sx * (SH_W * 0.5 - 0.025), SH_Y, SH_H * 0.5), mat=SHELF_W,
            bevel=0.006)
add_box("ShelfCornice", (SH_W + 0.10, SH_D + 0.06, 0.09),
        (0.0, SH_Y - 0.02, SH_H + 0.045), mat=SHELF_W, bevel=0.01)

SHELF_LEVELS = [0.30, 0.72, 1.14, 1.56, 1.94]
PROD_SPECS = [
    ('can', 0.036, 0.115),
    ('can', 0.030, 0.095),
    ('carton', 0.085, 0.175),
    ('carton', 0.070, 0.130),
    ('bottle', 0.036, 0.235),
    ('jar', 0.044, 0.100),
]

for li, sz in enumerate(SHELF_LEVELS):
    add_box("ShelfBoard_%d" % li, (SH_W - 0.06, SH_D, 0.03), (0.0, SH_Y, sz),
            mat=SHELF_W, bevel=0.005)
    add_box("ShelfLip_%d" % li, (SH_W - 0.06, 0.015, 0.035),
            (0.0, SH_Y - SH_D * 0.5 + 0.008, sz + 0.03), mat=CAB_TRIM)
    add_box("ShelfStrip_%d" % li, (SH_W - 0.30, 0.04, 0.012),
            (0.0, SH_Y - 0.10, sz - 0.03), mat=STRIP)

    top_z = sz + 0.015
    x = -SH_W * 0.5 + 0.09
    idx = 0
    while x < SH_W * 0.5 - 0.14:
        kind, rad, hgt = pick(PROD_SPECS)
        body = pick(PROD_MATS)
        label = pick(LABEL_MATS)
        rows = 1 if random.random() < 0.5 else 2
        for row in range(rows):
            py = SH_Y - 0.06 + row * 0.13
            tag = "%d_%d_%d" % (li, idx, row)
            if kind == 'can':
                add_cyl("Can_" + tag, rad, hgt, (x + rad, py, top_z + hgt * 0.5),
                        mat=body, segments=20, bevel=0.004)
                add_cyl("CanLabel_" + tag, rad * 1.02, hgt * 0.55,
                        (x + rad, py, top_z + hgt * 0.5), mat=label, segments=20)
            elif kind == 'carton':
                add_box("Carton_" + tag, (rad, 0.062, hgt),
                        (x + rad * 0.5, py, top_z + hgt * 0.5),
                        rot=(0, 0, math.radians(random.uniform(-3, 3))),
                        mat=body, bevel=0.004)
                add_box("CartonLabel_" + tag, (rad * 0.7, 0.004, hgt * 0.45),
                        (x + rad * 0.5, py - 0.033, top_z + hgt * 0.55),
                        mat=label)
            elif kind == 'bottle':
                add_cyl("BottleBody_" + tag, rad, hgt * 0.62,
                        (x + rad, py, top_z + hgt * 0.31), mat=body,
                        segments=24, bevel=0.005)
                add_cone("BottleShoulder_" + tag, rad, rad * 0.36, hgt * 0.20,
                         (x + rad, py, top_z + hgt * 0.72), mat=body,
                         segments=24)
                add_cyl("BottleNeck_" + tag, rad * 0.36, hgt * 0.18,
                        (x + rad, py, top_z + hgt * 0.91), mat=body, segments=18)
                add_cyl("BottleCap_" + tag, rad * 0.40, hgt * 0.06,
                        (x + rad, py, top_z + hgt * 1.01), mat=label,
                        segments=18, bevel=0.002)
            else:  # jar
                add_cyl("JarBody_" + tag, rad, hgt,
                        (x + rad, py, top_z + hgt * 0.5), mat=GLASS,
                        segments=24)
                add_cyl("JarFill_" + tag, rad * 0.9, hgt * 0.75,
                        (x + rad, py, top_z + hgt * 0.42), mat=body, segments=24)
                add_cyl("JarTop_" + tag, rad * 1.05, hgt * 0.12,
                        (x + rad, py, top_z + hgt * 0.97), mat=label,
                        segments=24, bevel=0.003)
        step = (rad * 2.0 if kind != 'carton' else rad) + 0.022
        x += step
        idx += 1

# a chalkboard price sign on the wall
add_box("SignFrame", (0.72, 0.04, 0.50), (-2.05, 2.30, 1.55), mat=SHELF_W,
        bevel=0.008)
add_box("SignBoard", (0.64, 0.02, 0.42), (-2.05, 2.27, 1.55),
        mat=new_material("Chalkboard", (0.05, 0.06, 0.06), rough=0.85))


# ----------------------------------------------------------------------------
# lighting and camera
# ----------------------------------------------------------------------------

add_light("CeilingKey", 'AREA', (0.0, -0.6, 2.95), 320.0, (1.0, 0.94, 0.86),
          size=2.4, target=(0.0, 0.05, 1.0))
add_light("CeilingBack", 'AREA', (0.0, 1.55, 2.95), 220.0, (1.0, 0.95, 0.88),
          size=2.6, target=(0.0, 2.0, 1.2))
add_light("Fill", 'AREA', (-2.6, -2.8, 2.2), 140.0, (0.75, 0.82, 1.0),
          size=3.0, target=(-0.4, 0.3, 1.0))
add_light("CaseSpot", 'SPOT', (1.0, -1.5, 2.7), 180.0, (1.0, 0.92, 0.8),
          size=0.1, target=(0.62, 0.0, 1.15), spot_size=math.radians(42.0))

add_camera((2.85, -3.35, 1.82), (0.05, 0.45, 1.05), lens=40.0)

bpy.context.view_layer.update()
