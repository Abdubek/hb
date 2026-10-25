"""claude-060 : A hotel reception desk with wall sign and seating."""
import bpy, bmesh, math, random
from mathutils import Vector, Matrix

random.seed(60)


# ------------------------------------------------------------------ helpers
def reset_scene():
    bpy.ops.wm.read_factory_settings(use_empty=True)
    scn = bpy.context.scene
    try:
        scn.render.engine = 'BLENDER_EEVEE_NEXT'
    except Exception:
        pass
    scn.render.resolution_x, scn.render.resolution_y = 1800, 1000


def mat(name, color, rough=0.5, metal=0.0, emis=None, estr=0.0, alpha=1.0):
    m = bpy.data.materials.new(name)
    m.use_nodes = True
    i = m.node_tree.nodes["Principled BSDF"].inputs
    i["Base Color"].default_value = (*color, 1.0)
    i["Roughness"].default_value = rough
    i["Metallic"].default_value = metal
    if emis is not None:
        if "Emission Color" in i:
            i["Emission Color"].default_value = (*emis, 1.0)
        i["Emission Strength"].default_value = estr
    if alpha < 1.0:
        i["Alpha"].default_value = alpha
        try:
            m.blend_method = 'BLEND'
        except Exception:
            pass
        if hasattr(m, "surface_render_method"):
            m.surface_render_method = 'BLENDED'
    return m


def shade_smooth(ob):
    bpy.ops.object.select_all(action='DESELECT')
    ob.select_set(True)
    bpy.context.view_layer.objects.active = ob
    try:
        bpy.ops.object.shade_auto_smooth(angle=math.radians(35))
    except Exception:
        bpy.ops.object.shade_smooth()


def finish(ob, material=None, bevel=0.0, seg=2, smooth=False):
    if material:
        ob.data.materials.append(material)
    if bevel > 0.0:
        b = ob.modifiers.new("Bevel", 'BEVEL')
        b.width, b.segments = bevel, seg
        b.limit_method = 'ANGLE'
        b.angle_limit = math.radians(50)
    if smooth:
        shade_smooth(ob)
    return ob


def add_box(name, size, loc=(0, 0, 0), rot=(0, 0, 0), material=None, bevel=0.0, seg=2):
    bpy.ops.mesh.primitive_cube_add(size=1.0)
    ob = bpy.context.object
    ob.name = name
    ob.data.transform(Matrix.Diagonal(Vector((size[0], size[1], size[2], 1.0))))
    ob.location, ob.rotation_euler = loc, rot
    return finish(ob, material, bevel, seg)


def add_cyl(name, r, d, loc=(0, 0, 0), rot=(0, 0, 0), verts=24, material=None,
            r2=None):
    if r2 is None:
        bpy.ops.mesh.primitive_cylinder_add(vertices=verts, radius=r, depth=d)
    else:
        bpy.ops.mesh.primitive_cone_add(vertices=verts, radius1=r, radius2=r2, depth=d)
    ob = bpy.context.object
    ob.name = name
    ob.location, ob.rotation_euler = loc, rot
    return finish(ob, material, smooth=True)


def add_ico(name, r, loc, material=None, subd=3):
    bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=subd, radius=r, location=loc)
    ob = bpy.context.object
    ob.name = name
    return finish(ob, material, smooth=True)


def look_at(ob, target):
    d = Vector(target) - ob.location
    ob.rotation_euler = d.to_track_quat('-Z', 'Y').to_euler()


# ------------------------------------------------------------------ materials
reset_scene()

M_FLOOR = mat("PolishedStone", (0.20, 0.19, 0.18), 0.12)
M_WALL = mat("Plaster", (0.66, 0.63, 0.58), 0.75)
M_SLAT = mat("WalnutSlat", (0.24, 0.14, 0.08), 0.36)
M_SLAT_G = mat("SlatGap", (0.06, 0.05, 0.045), 0.85)
M_DESK = mat("DeskFront", (0.19, 0.20, 0.23), 0.35)
M_DESK_T = mat("DeskStone", (0.87, 0.86, 0.83), 0.14)
M_BRASS = mat("Brass", (0.76, 0.58, 0.26), 0.22, 1.0)
M_BLACK = mat("SoftBlack", (0.05, 0.05, 0.055), 0.5)
M_SCREEN = mat("Screen", (0.10, 0.14, 0.20), 0.25, emis=(0.25, 0.45, 0.70), estr=2.0)
M_LEDCOVE = mat("LEDCove", (1.0, 0.90, 0.75), 0.4, emis=(1.0, 0.88, 0.70), estr=7.0)
M_SIGN = mat("SignBrass", (0.83, 0.68, 0.34), 0.18, 1.0,
             emis=(1.0, 0.86, 0.55), estr=1.6)
M_UPH = mat("Upholstery", (0.32, 0.38, 0.42), 0.72)
M_UPH2 = mat("UpholsteryAccent", (0.52, 0.32, 0.22), 0.72)
M_CUSHION = mat("Cushion", (0.70, 0.64, 0.52), 0.80)
M_WOODLEG = mat("OakLeg", (0.42, 0.28, 0.15), 0.42)
M_RUG = mat("Rug", (0.28, 0.26, 0.24), 0.90)
M_GLASSTOP = mat("GlassTop", (0.85, 0.92, 0.94), 0.05, 0.0, alpha=0.25)
M_LEAF = mat("Foliage", (0.16, 0.32, 0.16), 0.60)
M_POT = mat("Planter", (0.30, 0.31, 0.30), 0.45)
M_PAPER = mat("Paper", (0.90, 0.89, 0.86), 0.85)
M_BULB = mat("PendantGlow", (1.0, 0.88, 0.68), 0.3, emis=(1.0, 0.85, 0.62), estr=12.0)

# ------------------------------------------------------------------ room shell
add_box("Floor", (14.0, 12.0, 0.20), (0, 0, -0.10), material=M_FLOOR)
add_box("BackWall", (14.0, 0.25, 3.60), (0, 2.60, 1.80), material=M_WALL)
add_box("SideWallL", (0.25, 12.0, 3.60), (-5.60, -3.0, 1.80), material=M_WALL)
add_box("Ceiling", (14.0, 12.0, 0.20), (0, -1.0, 3.70), material=M_WALL)

# walnut slat feature wall behind the desk
SLAT_X0, SLAT_X1 = -3.30, 3.30
add_box("SlatBacking", (SLAT_X1 - SLAT_X0 + 0.10, 0.05, 3.00), (0, 2.45, 1.55),
        material=M_SLAT_G)
nslat = 46
for k in range(nslat):
    x = SLAT_X0 + (SLAT_X1 - SLAT_X0) * (k + 0.5) / nslat
    add_box("Slat%02d" % k, (0.075, 0.06, 2.96), (x, 2.40, 1.55), material=M_SLAT,
            bevel=0.006)
add_box("SlatCapTop", (SLAT_X1 - SLAT_X0 + 0.12, 0.10, 0.06), (0, 2.40, 3.06),
        material=M_SLAT, bevel=0.008)
# concealed cove wash at the top of the slat wall
add_box("CoveStrip", (SLAT_X1 - SLAT_X0, 0.05, 0.04), (0, 2.30, 3.02),
        material=M_LEDCOVE)

# ------------------------------------------------------------------ wall sign
bpy.ops.object.text_add(location=(0.0, 2.30, 2.28), rotation=(math.pi / 2, 0, 0))
sign = bpy.context.object
sign.name = "WallSign"
sign.data.body = "GRAND MERIDIAN"
sign.data.size = 0.34
sign.data.extrude = 0.022
sign.data.bevel_depth = 0.0025
sign.data.align_x = 'CENTER'
sign.data.align_y = 'CENTER'
sign.data.space_character = 1.15
sign.data.materials.append(M_SIGN)

bpy.ops.object.text_add(location=(0.0, 2.30, 1.94), rotation=(math.pi / 2, 0, 0))
sub = bpy.context.object
sub.name = "WallSignSub"
sub.data.body = "H O T E L   &   S P A"
sub.data.size = 0.105
sub.data.extrude = 0.010
sub.data.align_x = 'CENTER'
sub.data.align_y = 'CENTER'
sub.data.materials.append(M_BRASS)

# soft halo panel behind the lettering
add_box("SignHalo", (3.60, 0.02, 0.98), (0, 2.355, 2.16),
        material=mat("Halo", (0.9, 0.8, 0.6), 0.6, emis=(1.0, 0.86, 0.62), estr=1.4))

# ------------------------------------------------------------------ reception desk
DW, DD = 4.20, 0.80        # main counter width / depth
DX, DY = -0.40, 1.15       # desk centre
BASE_H, LEDGE_Z = 0.96, 1.10

add_box("DeskBody", (DW, DD, BASE_H), (DX, DY, BASE_H / 2), material=M_DESK,
        bevel=0.012)
add_box("DeskReveal", (DW - 0.10, DD + 0.02, 0.05), (DX, DY, 0.10),
        material=M_LEDCOVE)
add_box("DeskToe", (DW - 0.16, DD - 0.06, 0.10), (DX, DY, 0.05), material=M_BLACK)
# fluted brass reveal running along the front face
for k in range(24):
    x = DX - DW / 2 + 0.14 + k * (DW - 0.28) / 23.0
    add_box("Flute%02d" % k, (0.030, 0.03, 0.62), (x, DY - DD / 2 - 0.012, 0.56),
            material=M_BRASS, bevel=0.004)
# transaction ledge overhanging the front
add_box("DeskLedge", (DW + 0.18, DD + 0.34, 0.06), (DX, DY - 0.12, LEDGE_Z + 0.03),
        material=M_DESK_T, bevel=0.008)
add_box("DeskLedgeShadowGap", (DW + 0.02, DD + 0.10, 0.04), (DX, DY - 0.04, LEDGE_Z - 0.02),
        material=M_BLACK)
# lower working top behind
add_box("WorkTop", (DW - 0.20, 0.50, 0.05), (DX, DY + 0.62, 0.90), material=M_DESK_T,
        bevel=0.006)
# side return
add_box("DeskReturn", (0.75, 1.10, BASE_H), (DX + DW / 2 + 0.375, DY + 0.20, BASE_H / 2),
        material=M_DESK, bevel=0.012)
add_box("DeskReturnTop", (0.85, 1.20, 0.05), (DX + DW / 2 + 0.375, DY + 0.20, BASE_H + 0.025),
        material=M_DESK_T, bevel=0.006)

# back credenza against the slat wall
add_box("Credenza", (5.20, 0.45, 0.78), (0, 2.10, 0.39), material=M_SLAT, bevel=0.01)
add_box("CredenzaTop", (5.30, 0.50, 0.04), (0, 2.10, 0.80), material=M_DESK_T,
        bevel=0.006)
for k in range(4):
    add_box("CredPull%d" % k, (0.36, 0.025, 0.02), (-1.95 + k * 1.30, 1.86, 0.52),
            material=M_BRASS, bevel=0.005)

# ------------------------------------------------------------------ desk-top props
TOPZ = BASE_H + 0.05
# monitor on the staff side, facing away from the lobby
add_cyl("MonBase", 0.11, 0.02, (DX - 1.30, DY + 0.55, TOPZ + 0.01), verts=24,
        material=M_BLACK)
add_box("MonStem", (0.05, 0.03, 0.26), (DX - 1.30, DY + 0.55, TOPZ + 0.14),
        material=M_BLACK, bevel=0.006)
screen = add_box("Monitor", (0.56, 0.03, 0.34), (DX - 1.30, DY + 0.56, TOPZ + 0.36),
                 rot=(math.radians(-8), 0, 0), material=M_BLACK, bevel=0.006)
add_box("MonitorFace", (0.52, 0.008, 0.30), (DX - 1.30, DY + 0.538, TOPZ + 0.362),
        rot=(math.radians(-8), 0, 0), material=M_SCREEN)
add_box("Keyboard", (0.42, 0.15, 0.018), (DX - 1.30, DY + 0.25, TOPZ + 0.009),
        material=M_BLACK, bevel=0.004)

# service bell on the ledge
add_cyl("BellBase", 0.055, 0.014, (DX + 1.35, DY - 0.34, LEDGE_Z + 0.067), verts=24,
        material=M_BRASS)
bell = add_ico("BellDome", 0.052, (DX + 1.35, DY - 0.34, LEDGE_Z + 0.078),
               material=M_BRASS, subd=3)
bell.scale = (1.0, 1.0, 0.62)
add_cyl("BellPin", 0.008, 0.026, (DX + 1.35, DY - 0.34, LEDGE_Z + 0.115), verts=12,
        material=M_BRASS)

# card holder, pen cup and registration cards
add_box("CardHolder", (0.14, 0.09, 0.05), (DX + 0.85, DY - 0.32, LEDGE_Z + 0.085),
        rot=(math.radians(-12), 0, 0), material=M_BRASS, bevel=0.008)
add_cyl("PenCup", 0.038, 0.10, (DX + 0.55, DY - 0.30, LEDGE_Z + 0.11), verts=20,
        material=M_BLACK)
for k in range(3):
    add_cyl("Pen%d" % k, 0.005, 0.15,
            (DX + 0.55 + 0.012 * (k - 1), DY - 0.30 + 0.010 * k, LEDGE_Z + 0.18),
            rot=(math.radians(6 * (k - 1)), math.radians(5 * k), 0), verts=8,
            material=M_BRASS if k == 1 else M_BLACK)
add_box("CardStack", (0.22, 0.15, 0.012), (DX - 0.25, DY - 0.30, LEDGE_Z + 0.066),
        rot=(0, 0, math.radians(-6)), material=M_PAPER)

# flower vase on the desk return
add_cyl("Vase", 0.075, 0.26, (DX + DW / 2 + 0.375, DY + 0.20, TOPZ + 0.13), verts=26,
        material=M_DESK_T, r2=0.055)
for k in range(7):
    a = 2 * math.pi * k / 7
    tip = Vector((DX + DW / 2 + 0.375 + 0.16 * math.cos(a),
                  DY + 0.20 + 0.16 * math.sin(a), TOPZ + 0.50))
    base = Vector((DX + DW / 2 + 0.375, DY + 0.20, TOPZ + 0.24))
    d = tip - base
    st = add_cyl("Stem%d" % k, 0.005, d.length, tuple((tip + base) * 0.5), verts=6,
                 material=M_LEAF)
    st.rotation_euler = d.to_track_quat('Z', 'Y').to_euler()
    add_ico("Bloom%d" % k, 0.045, tuple(tip), material=M_CUSHION, subd=2)


# ------------------------------------------------------------------ seating
def armchair(name, loc, rot_z=0.0, fabric=None):
    fabric = fabric or M_UPH
    parts = []
    add_box(name + "_Base", (0.74, 0.72, 0.16), (0, 0, 0.34), material=fabric,
            bevel=0.035, seg=3)
    add_box(name + "_Seat", (0.66, 0.64, 0.14), (0, 0.02, 0.47), material=M_CUSHION,
            bevel=0.045, seg=3)
    add_box(name + "_Back", (0.72, 0.14, 0.60), (0, -0.30, 0.72),
            rot=(math.radians(-8), 0, 0), material=fabric, bevel=0.045, seg=3)
    add_box(name + "_BackCushion", (0.62, 0.10, 0.48), (0, -0.22, 0.72),
            rot=(math.radians(-9), 0, 0), material=M_CUSHION, bevel=0.04, seg=3)
    for sgn in (-1, 1):
        add_box(name + "_Arm%d" % (sgn > 0), (0.12, 0.62, 0.20),
                (sgn * 0.31, 0.0, 0.58), material=fabric, bevel=0.045, seg=3)
    for sx in (-1, 1):
        for sy in (-1, 1):
            add_cyl(name + "_Leg%d%d" % (sx > 0, sy > 0), 0.022, 0.26,
                    (sx * 0.28, sy * 0.27, 0.13),
                    rot=(math.radians(sy * 5), math.radians(-sx * 5), 0), verts=12,
                    material=M_WOODLEG, r2=0.016)
    # gather the freshly created objects and group them under an empty
    grp = bpy.data.objects.new(name, None)
    grp.empty_display_size = 0.2
    bpy.context.collection.objects.link(grp)
    grp.location = loc
    grp.rotation_euler = (0, 0, rot_z)
    for ob in bpy.data.objects:
        if ob.name.startswith(name + "_") and ob.parent is None:
            ob.parent = grp
            ob.matrix_parent_inverse = grp.matrix_world.inverted()
    return grp


def sofa(name, loc, rot_z=0.0, width=1.90, fabric=None):
    fabric = fabric or M_UPH
    add_box(name + "_Base", (width, 0.80, 0.18), (0, 0, 0.33), material=fabric,
            bevel=0.04, seg=3)
    add_box(name + "_Back", (width, 0.16, 0.58), (0, -0.32, 0.71),
            rot=(math.radians(-7), 0, 0), material=fabric, bevel=0.04, seg=3)
    for sgn in (-1, 1):
        add_box(name + "_Arm%d" % (sgn > 0), (0.14, 0.78, 0.24),
                (sgn * (width / 2 - 0.07), 0.0, 0.55), material=fabric,
                bevel=0.045, seg=3)
    ncush = 3
    for k in range(ncush):
        x = -width / 2 + (k + 0.5) * width / ncush
        add_box(name + "_Seat%d" % k, (width / ncush - 0.06, 0.68, 0.15),
                (x, 0.03, 0.49), material=M_CUSHION, bevel=0.05, seg=3)
        add_box(name + "_BackC%d" % k, (width / ncush - 0.08, 0.12, 0.44),
                (x, -0.24, 0.72), rot=(math.radians(-8), 0, 0), material=M_CUSHION,
                bevel=0.045, seg=3)
    for k, sx in enumerate((-1, 1)):
        add_box(name + "_Pillow%d" % k, (0.34, 0.14, 0.34),
                (sx * (width / 2 - 0.34), -0.16, 0.62),
                rot=(math.radians(-14), 0, math.radians(sx * 8)), material=M_UPH2,
                bevel=0.05, seg=3)
    for sx in (-1, 1):
        for sy in (-1, 1):
            add_cyl(name + "_Leg%d%d" % (sx > 0, sy > 0), 0.024, 0.26,
                    (sx * (width / 2 - 0.14), sy * 0.31, 0.13), verts=12,
                    material=M_WOODLEG, r2=0.018)
    grp = bpy.data.objects.new(name, None)
    grp.empty_display_size = 0.25
    bpy.context.collection.objects.link(grp)
    grp.location = loc
    grp.rotation_euler = (0, 0, rot_z)
    for ob in bpy.data.objects:
        if ob.name.startswith(name + "_") and ob.parent is None:
            ob.parent = grp
            ob.matrix_parent_inverse = grp.matrix_world.inverted()
    return grp


# lounge grouping in front of and to the side of the desk
add_box("Rug", (3.40, 2.60, 0.02), (1.10, -1.85, 0.01), material=M_RUG)
add_box("RugBorder", (3.56, 2.76, 0.012), (1.10, -1.85, 0.006), material=M_UPH2)

sofa("Sofa", (1.10, -0.72, 0.0), rot_z=math.radians(180))
armchair("ChairA", (0.05, -2.75, 0.0), rot_z=math.radians(28), fabric=M_UPH2)
armchair("ChairB", (2.15, -2.75, 0.0), rot_z=math.radians(-28))

# coffee table with glass top and a tray of magazines
add_box("TableFrame", (1.00, 0.60, 0.06), (1.10, -1.85, 0.40), material=M_WOODLEG,
        bevel=0.012)
for sx in (-1, 1):
    for sy in (-1, 1):
        add_cyl("TableLeg%d%d" % (sx > 0, sy > 0), 0.025, 0.40,
                (1.10 + sx * 0.42, -1.85 + sy * 0.22, 0.20), verts=12,
                material=M_WOODLEG)
add_box("TableGlass", (1.14, 0.72, 0.018), (1.10, -1.85, 0.452),
        material=M_GLASSTOP, bevel=0.005)
for k in range(3):
    add_box("Magazine%d" % k, (0.26, 0.19, 0.010),
            (0.85, -1.82, 0.468 + k * 0.012), rot=(0, 0, math.radians(-8 + 7 * k)),
            material=M_PAPER if k % 2 == 0 else M_UPH2)
add_cyl("TableBowl", 0.10, 0.06, (1.42, -1.88, 0.492), verts=26, material=M_BRASS,
        r2=0.13)

# bench seating along the side wall
add_box("BenchTop", (0.55, 2.20, 0.14), (-4.10, -1.20, 0.46), material=M_UPH,
        bevel=0.05, seg=3)
add_box("BenchBase", (0.45, 2.05, 0.34), (-4.10, -1.20, 0.22), material=M_SLAT,
        bevel=0.012)
for k in range(3):
    add_box("BenchPillow%d" % k, (0.14, 0.34, 0.34), (-4.28, -2.05 + k * 0.85, 0.68),
            rot=(0, math.radians(-14), 0), material=M_UPH2, bevel=0.05, seg=3)

# ------------------------------------------------------------------ planters
def planter(name, x, y, h=0.55, r=0.28):
    add_cyl(name + "_Pot", r * 0.8, h, (x, y, h / 2), verts=28, material=M_POT, r2=r)
    add_cyl(name + "_Soil", r * 0.94, 0.03, (x, y, h - 0.01), verts=28,
            material=M_BLACK)
    for k in range(16):
        a = 2 * math.pi * k / 16 + random.uniform(-0.2, 0.2)
        rr = r * random.uniform(0.25, 0.95)
        tip_h = h + random.uniform(0.55, 1.15)
        base = Vector((x, y, h))
        tip = Vector((x + rr * math.cos(a) * 1.5, y + rr * math.sin(a) * 1.5, tip_h))
        d = tip - base
        st = add_cyl(name + "_Stem%d" % k, 0.010, d.length, tuple((base + tip) * 0.5),
                     verts=6, material=M_LEAF)
        st.rotation_euler = d.to_track_quat('Z', 'Y').to_euler()
        leaf = add_ico(name + "_Leaf%d" % k, 0.14, tuple(tip), material=M_LEAF, subd=2)
        leaf.scale = (0.45, 1.25, 0.28)
        leaf.rotation_euler = (random.uniform(-0.3, 0.3), random.uniform(-0.4, 0.4), a)


planter("PlantL", -3.10, 1.85)
planter("PlantR", 3.05, 1.85)
planter("PlantLobby", 3.60, -2.60, h=0.65, r=0.34)

# luggage trolley hint: a brass stanchion pair with rope near the desk
for k, sx in enumerate((-3.00, -2.20)):
    add_cyl("Stanchion%d" % k, 0.035, 0.95, (sx, 0.10, 0.475), verts=18,
            material=M_BRASS)
    add_cyl("StanchionFoot%d" % k, 0.16, 0.03, (sx, 0.10, 0.015), verts=24,
            material=M_BRASS)
    add_ico("StanchionCap%d" % k, 0.045, (sx, 0.10, 0.97), material=M_BRASS, subd=2)
rope_pts = [Vector((-3.00, 0.10, 0.86)), Vector((-2.60, 0.10, 0.72)),
            Vector((-2.20, 0.10, 0.86))]
for k in range(len(rope_pts) - 1):
    p0, p1 = rope_pts[k], rope_pts[k + 1]
    d = p1 - p0
    rp = add_cyl("Rope%d" % k, 0.016, d.length, tuple((p0 + p1) * 0.5), verts=10,
                 material=M_UPH2)
    rp.rotation_euler = d.to_track_quat('Z', 'Y').to_euler()

# ------------------------------------------------------------------ pendants + light
for k, px in enumerate((-1.60, -0.40, 0.80)):
    add_cyl("PendantRod%d" % k, 0.008, 1.10, (px, DY - 0.30, 3.05), verts=8,
            material=M_BLACK)
    add_cyl("PendantShade%d" % k, 0.13, 0.20, (px, DY - 0.30, 2.42), verts=28,
            material=M_BRASS, r2=0.05)
    add_ico("PendantBulb%d" % k, 0.05, (px, DY - 0.30, 2.34), material=M_BULB, subd=3)
    pd = bpy.data.lights.new("PendantLight%d" % k, 'POINT')
    pd.energy, pd.shadow_soft_size = 45.0, 0.08
    pd.color = (1.0, 0.86, 0.68)
    po = bpy.data.objects.new("PendantLight%d" % k, pd)
    bpy.context.collection.objects.link(po)
    po.location = (px, DY - 0.30, 2.32)

# recessed ceiling wash over the lounge
for k, (lx, ly) in enumerate(((1.10, -1.90), (-3.20, -1.60), (3.40, -0.20))):
    add_cyl("Downlight%d" % k, 0.09, 0.03, (lx, ly, 3.585), verts=20,
            material=M_LEDCOVE)
    ld = bpy.data.lights.new("Down%d" % k, 'SPOT')
    ld.energy, ld.spot_size, ld.spot_blend = 300.0, math.radians(85), 0.6
    ld.shadow_soft_size = 0.12
    ld.color = (1.0, 0.95, 0.90)
    lo = bpy.data.objects.new("Down%d" % k, ld)
    bpy.context.collection.objects.link(lo)
    lo.location = (lx, ly, 3.55)
    lo.rotation_euler = (0, 0, 0)

# key / fill / cove area lights
kd = bpy.data.lights.new("Key", 'AREA')
kd.shape, kd.size, kd.size_y = 'RECTANGLE', 4.0, 2.0
kd.energy = 500.0
kd.color = (1.0, 0.94, 0.88)
key = bpy.data.objects.new("Key", kd)
bpy.context.collection.objects.link(key)
key.location = (-0.6, -2.4, 3.30)
look_at(key, (-0.3, 0.9, 1.1))

fd = bpy.data.lights.new("WallWash", 'AREA')
fd.shape, fd.size, fd.size_y = 'RECTANGLE', 6.0, 0.4
fd.energy = 220.0
fd.color = (1.0, 0.88, 0.72)
fw = bpy.data.objects.new("WallWash", fd)
bpy.context.collection.objects.link(fw)
fw.location = (0.0, 1.95, 3.05)
look_at(fw, (0.0, 2.40, 1.90))

sd = bpy.data.lights.new("LoungeFill", 'AREA')
sd.size, sd.energy = 3.0, 130.0
sd.color = (0.80, 0.86, 1.0)
sf = bpy.data.objects.new("LoungeFill", sd)
bpy.context.collection.objects.link(sf)
sf.location = (5.0, -4.5, 2.6)
look_at(sf, (1.0, -1.5, 0.8))

world = bpy.data.worlds.new("World")
bpy.context.scene.world = world
world.use_nodes = True
wbg = world.node_tree.nodes["Background"]
wbg.inputs["Color"].default_value = (0.055, 0.058, 0.070, 1.0)
wbg.inputs["Strength"].default_value = 1.0

# ------------------------------------------------------------------ camera
cam_data = bpy.data.cameras.new("Camera")
cam_data.lens = 32
cam = bpy.data.objects.new("Camera", cam_data)
bpy.context.collection.objects.link(cam)
cam.location = (4.30, -5.60, 1.95)
look_at(cam, (-0.35, 0.55, 1.25))
bpy.context.scene.camera = cam

print("claude-060 hotel reception built: %d objects" % len(bpy.data.objects))
