"""claude-046 - Modular exhibition booth with walls and display plinths.

Builds a 8 x 6 m island booth: extruded aluminium wall system with modular
infill panels, header fascia, lighting truss, reception counter and a row of
display plinths carrying products.  Scene only - nothing is rendered or saved.
"""

import bpy
import bmesh
import math
from mathutils import Vector, Matrix, Euler


# --------------------------------------------------------------------------
# helpers
# --------------------------------------------------------------------------
def reset_scene():
    bpy.ops.wm.read_factory_settings(use_empty=True)
    scene = bpy.context.scene
    scene.unit_settings.system = 'METRIC'
    return scene


def link(obj):
    bpy.context.scene.collection.objects.link(obj)
    return obj


def make_mat(name, color, rough=0.5, metal=0.0, emis=None, emis_str=0.0,
             alpha=1.0, transmission=0.0):
    m = bpy.data.materials.new(name)
    m.use_nodes = True
    b = m.node_tree.nodes["Principled BSDF"]
    b.inputs["Base Color"].default_value = (color[0], color[1], color[2], 1.0)
    b.inputs["Roughness"].default_value = rough
    b.inputs["Metallic"].default_value = metal
    if "Transmission Weight" in b.inputs:
        b.inputs["Transmission Weight"].default_value = transmission
    if emis is not None:
        if "Emission Color" in b.inputs:
            b.inputs["Emission Color"].default_value = (emis[0], emis[1], emis[2], 1.0)
        b.inputs["Emission Strength"].default_value = emis_str
    if alpha < 1.0:
        b.inputs["Alpha"].default_value = alpha
        try:
            m.blend_method = 'BLEND'
        except Exception:
            pass
    return m


def tag_new(bm, before, index):
    for f in bm.faces:
        if f not in before:
            f.material_index = index


def bm_box(bm, center, size, index=0, rot=None):
    m = Matrix.Translation(Vector(center))
    if rot is not None:
        m = m @ Euler(rot).to_matrix().to_4x4()
    m = m @ Matrix.Diagonal(Vector((size[0], size[1], size[2], 1.0)))
    before = set(bm.faces)
    bmesh.ops.create_cube(bm, size=1.0, matrix=m)
    tag_new(bm, before, index)


def bm_cyl(bm, center, radius, depth, index=0, segments=24, rot=None, r2=None):
    m = Matrix.Translation(Vector(center))
    if rot is not None:
        m = m @ Euler(rot).to_matrix().to_4x4()
    before = set(bm.faces)
    bmesh.ops.create_cone(bm, cap_ends=True, cap_tris=False, segments=segments,
                          radius1=radius, radius2=(radius if r2 is None else r2),
                          depth=depth, matrix=m)
    tag_new(bm, before, index)


def bm_tube_between(bm, p1, p2, radius, index=0, segments=10):
    p1, p2 = Vector(p1), Vector(p2)
    d = p2 - p1
    if d.length < 1e-6:
        return
    m = Matrix.Translation((p1 + p2) * 0.5) @ d.to_track_quat('Z', 'Y').to_matrix().to_4x4()
    before = set(bm.faces)
    bmesh.ops.create_cone(bm, cap_ends=True, cap_tris=False, segments=segments,
                          radius1=radius, radius2=radius, depth=d.length, matrix=m)
    tag_new(bm, before, index)


def finish(bm, name, mats, location=(0, 0, 0), rotation=(0, 0, 0), smooth_round=False):
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    if smooth_round:
        for f in bm.faces:
            if abs(f.normal.z) < 0.85:
                f.smooth = True
    me = bpy.data.meshes.new(name)
    bm.to_mesh(me)
    bm.free()
    obj = bpy.data.objects.new(name, me)
    obj.location = location
    obj.rotation_euler = rotation
    for m in mats:
        me.materials.append(m)
    return link(obj)


def look_at(obj, target):
    d = Vector(target) - obj.location
    obj.rotation_euler = d.to_track_quat('-Z', 'Y').to_euler()


# --------------------------------------------------------------------------
# scene
# --------------------------------------------------------------------------
reset_scene()

M_CARPET = make_mat("Carpet", (0.06, 0.07, 0.09), rough=0.95)
M_DECK = make_mat("DeckEdge", (0.10, 0.10, 0.11), rough=0.6)
M_ALU = make_mat("AluExtrusion", (0.72, 0.73, 0.75), rough=0.30, metal=1.0)
M_PANEL = make_mat("PanelWhite", (0.86, 0.87, 0.88), rough=0.55)
M_ACCENT = make_mat("PanelAccent", (0.05, 0.35, 0.62), rough=0.45)
M_LIGHTBOX = make_mat("Lightbox", (0.9, 0.95, 1.0), rough=0.4,
                      emis=(0.85, 0.93, 1.0), emis_str=3.0)
M_LOGO = make_mat("LogoGlow", (0.9, 0.5, 0.15), rough=0.4,
                  emis=(1.0, 0.55, 0.15), emis_str=6.0)
M_PLINTH = make_mat("PlinthWhite", (0.90, 0.90, 0.91), rough=0.35)
M_PLINTH_DK = make_mat("PlinthDark", (0.09, 0.10, 0.12), rough=0.35)
M_STEEL = make_mat("Steel", (0.55, 0.56, 0.58), rough=0.42, metal=1.0)
M_BLACK = make_mat("MatteBlack", (0.03, 0.03, 0.035), rough=0.7)
M_GLASS = make_mat("Acrylic", (0.95, 0.97, 1.0), rough=0.05, transmission=1.0, alpha=0.25)
M_GOLD = make_mat("BrassProduct", (0.80, 0.60, 0.25), rough=0.25, metal=1.0)
M_RED = make_mat("ProductRed", (0.65, 0.10, 0.09), rough=0.35)
M_WOOD = make_mat("CounterWood", (0.36, 0.22, 0.12), rough=0.45)

BW, BD = 8.0, 6.0          # booth width / depth
HALF_W, HALF_D = BW / 2, BD / 2
WALL_H = 3.0
PANEL_W = 1.0
POST = 0.10                # extrusion post section

# ---------------------------------------------------------------- floor deck
bm = bmesh.new()
bm_box(bm, (0, 0, 0.05), (BW, BD, 0.10), 0)
bm_box(bm, (0, -HALF_D - 0.03, 0.05), (BW + 0.06, 0.06, 0.11), 1)
bm_box(bm, (-HALF_W - 0.03, 0, 0.05), (0.06, BD + 0.06, 0.11), 1)
bm_box(bm, (HALF_W + 0.03, 0, 0.05), (0.06, BD + 0.06, 0.11), 1)
finish(bm, "BoothDeck", [M_CARPET, M_DECK])


# ------------------------------------------------------- modular wall system
def wall_run(bm, start, end, height, base_z, accents=()):
    """Build a run of 1 m modular frame bays between two ground points."""
    start, end = Vector(start), Vector(end)
    span = (end - start)
    length = span.length
    direction = span.normalized()
    normal = Vector((-direction.y, direction.x, 0.0))
    bays = max(1, int(round(length / PANEL_W)))
    bay_w = length / bays
    yaw = math.atan2(direction.y, direction.x)

    # vertical posts (one per bay joint)
    for i in range(bays + 1):
        p = start + direction * (bay_w * i)
        bm_box(bm, (p.x, p.y, base_z + height / 2), (POST, POST, height), 0, rot=(0, 0, yaw))
    # top and bottom rails
    mid = (start + end) * 0.5
    for z in (base_z + 0.05, base_z + height - 0.05):
        bm_box(bm, (mid.x, mid.y, z), (length, POST * 0.8, 0.10), 0, rot=(0, 0, yaw))
    # infill panels, slightly recessed from the frame face
    for i in range(bays):
        c = start + direction * (bay_w * (i + 0.5))
        idx = 2 if i in accents else 1
        bm_box(bm, (c.x, c.y, base_z + height / 2),
               (bay_w - 0.04, 0.05, height - 0.16), idx, rot=(0, 0, yaw))
        # horizontal reveal line at 1.1 m
        bm_box(bm, (c.x + normal.x * 0.03, c.y + normal.y * 0.03, base_z + 1.10),
               (bay_w - 0.04, 0.02, 0.02), 0, rot=(0, 0, yaw))


bm = bmesh.new()
wall_run(bm, (-HALF_W, HALF_D), (HALF_W, HALF_D), WALL_H, 0.10, accents=(2, 5))
wall_run(bm, (-HALF_W, -HALF_D + 1.2), (-HALF_W, HALF_D), WALL_H, 0.10, accents=(1,))
wall_run(bm, (HALF_W, -HALF_D + 1.2), (HALF_W, HALF_D), WALL_H, 0.10, accents=(3,))
# corner posts, slightly taller
for sx in (-1, 1):
    bm_box(bm, (sx * HALF_W, HALF_D, 0.10 + 1.65), (0.14, 0.14, 3.30), 0)
    bm_box(bm, (sx * HALF_W, -HALF_D + 1.2, 0.10 + 1.65), (0.14, 0.14, 3.30), 0)
finish(bm, "WallSystem", [M_ALU, M_PANEL, M_ACCENT])

# ------------------------------------------------------------- header fascia
bm = bmesh.new()
fascia_z = 0.10 + WALL_H + 0.30
bm_box(bm, (0, HALF_D, fascia_z), (BW + 0.2, 0.16, 0.60), 0)
for sx in (-1, 1):
    bm_box(bm, (sx * (HALF_W + 0.02), (HALF_D - 2.4) / 2 + 0.6, fascia_z),
           (0.16, BD - 1.2, 0.60), 0)
# illuminated logo band + logo blocks on the back fascia
bm_box(bm, (0, HALF_D - 0.10, fascia_z), (BW - 1.2, 0.05, 0.34), 1)
for i, w in enumerate((0.55, 0.30, 0.30, 0.75)):
    x = -1.6 + i * 1.05
    bm_box(bm, (x, HALF_D - 0.14, fascia_z), (w, 0.04, 0.18), 2)
finish(bm, "HeaderFascia", [M_BLACK, M_LIGHTBOX, M_LOGO])

# ------------------------------------------------------------- back lightbox
bm = bmesh.new()
bm_box(bm, (0, HALF_D - 0.10, 0.10 + 1.75), (5.4, 0.06, 2.0), 0)
bm_box(bm, (0, HALF_D - 0.14, 0.10 + 1.75), (5.6, 0.05, 2.12), 1)
finish(bm, "BackGraphic", [M_LIGHTBOX, M_ALU])


# ------------------------------------------------------------------ plinths
def build_plinth(name, x, y, height, top_size, dark=False):
    bm = bmesh.new()
    base = 0.10
    body_i = 1 if dark else 0
    # recessed shadow-gap base
    bm_box(bm, (0, 0, base + 0.03), (top_size - 0.10, top_size - 0.10, 0.06), 2)
    bm_box(bm, (0, 0, base + 0.06 + (height - 0.06) / 2),
           (top_size, top_size, height - 0.06), body_i)
    # top capping plate
    bm_box(bm, (0, 0, base + height + 0.012), (top_size + 0.03, top_size + 0.03, 0.024), 2)
    obj = finish(bm, name, [M_PLINTH, M_PLINTH_DK, M_STEEL], location=(x, y, 0))
    mod = obj.modifiers.new("Bevel", 'BEVEL')
    mod.width = 0.006
    mod.segments = 2
    mod.limit_method = 'ANGLE'
    return base + height + 0.024


def display_sphere(x, y, z, r, material):
    bm = bmesh.new()
    bmesh.ops.create_icosphere(bm, subdivisions=3, radius=r)
    for f in bm.faces:
        f.smooth = True
    return finish(bm, "DisplaySphere", [material], location=(x, y, z + r))


def display_torus(x, y, z, R, r, material):
    bm = bmesh.new()
    major, minor = 48, 20
    rings = []
    for i in range(major):
        a = 2 * math.pi * i / major
        ca, sa = math.cos(a), math.sin(a)
        ring = []
        for j in range(minor):
            b = 2 * math.pi * j / minor
            rr = R + r * math.cos(b)
            ring.append(bm.verts.new((rr * ca, rr * sa, r * math.sin(b))))
        rings.append(ring)
    for i in range(major):
        a, bset = rings[i], rings[(i + 1) % major]
        for j in range(minor):
            k = (j + 1) % minor
            bm.faces.new((a[j], a[k], bset[k], bset[j]))
    for f in bm.faces:
        f.smooth = True
    return finish(bm, "DisplayTorus", [material], location=(x, y, z + R + r),
                  rotation=(math.radians(90), 0, math.radians(20)))


def display_stack(x, y, z, material):
    bm = bmesh.new()
    bm_cyl(bm, (0, 0, 0.09), 0.16, 0.18, 0, segments=32)
    bm_cyl(bm, (0, 0, 0.26), 0.12, 0.16, 0, segments=32)
    bm_cyl(bm, (0, 0, 0.42), 0.14, 0.16, 0, segments=32, r2=0.02)
    return finish(bm, "DisplayStack", [material], location=(x, y, z), smooth_round=True)


def display_product_box(x, y, z, material, glass):
    bm = bmesh.new()
    bm_box(bm, (0, 0, 0.14), (0.30, 0.22, 0.28), 0)
    bm_box(bm, (0, 0, 0.30), (0.34, 0.26, 0.02), 1)
    obj = finish(bm, "DisplayProduct", [material, glass], location=(x, y, z),
                 rotation=(0, 0, math.radians(-25)))
    mod = obj.modifiers.new("Bevel", 'BEVEL')
    mod.width = 0.012
    mod.segments = 3
    mod.limit_method = 'ANGLE'
    return obj


plinth_specs = [
    ("PlinthA", -2.70, 1.30, 1.05, 0.55, False),
    ("PlinthB", -1.00, -0.30, 0.90, 0.62, True),
    ("PlinthC", 1.00, -0.30, 1.10, 0.50, False),
    ("PlinthD", 2.70, 1.30, 0.95, 0.60, True),
]
tops = []
for name, px, py, h, s, dark in plinth_specs:
    tops.append((px, py, build_plinth(name, px, py, h, s, dark)))

display_sphere(tops[0][0], tops[0][1], tops[0][2], 0.17, M_GOLD)
display_torus(tops[1][0], tops[1][1], tops[1][2], 0.17, 0.055, M_RED)
display_stack(tops[2][0], tops[2][1], tops[2][2], M_GLASS)
display_product_box(tops[3][0], tops[3][1], tops[3][2], M_ACCENT, M_GOLD)

# --------------------------------------------------------- reception counter
bm = bmesh.new()
bm_box(bm, (0, 0, 0.55), (2.40, 0.70, 0.90), 0)
bm_box(bm, (0, 0, 1.02), (2.55, 0.85, 0.06), 1)
bm_box(bm, (0, -0.36, 0.60), (2.20, 0.03, 0.30), 2)   # glowing front strip
bm_box(bm, (0, 0.30, 0.30), (2.10, 0.40, 0.50), 3)    # storage box behind
finish(bm, "ReceptionCounter", [M_PLINTH, M_WOOD, M_LIGHTBOX, M_PLINTH_DK],
       location=(2.6, -2.05, 0.10), rotation=(0, 0, math.radians(-28)))

# ------------------------------------------------------------ lighting truss
def build_truss(name, p_start, p_end, z, size=0.30):
    bm = bmesh.new()
    a, b = Vector(p_start), Vector(p_end)
    direction = (b - a).normalized()
    length = (b - a).length
    side = Vector((-direction.y, direction.x, 0.0))
    h = size / 2
    offsets = [(-h, -h), (h, -h), (-h, h), (h, h)]
    for so, zo in offsets:
        off = side * so
        bm_tube_between(bm, (a.x + off.x, a.y + off.y, z + zo),
                        (b.x + off.x, b.y + off.y, z + zo), 0.028, 0)
    n = max(2, int(length / 0.5))
    for i in range(n):
        t0, t1 = i / n, (i + 1) / n
        p0 = a + (b - a) * t0
        p1 = a + (b - a) * t1
        up = 1 if i % 2 == 0 else -1
        for so in (-h, h):
            off = side * so
            bm_tube_between(bm, (p0.x + off.x, p0.y + off.y, z - h * up),
                            (p1.x + off.x, p1.y + off.y, z + h * up), 0.014, 0, segments=8)
        bm_tube_between(bm, (p0.x - side.x * h, p0.y - side.y * h, z + h * up),
                        (p0.x + side.x * h, p0.y + side.y * h, z - h * up), 0.014, 0, segments=8)
    return finish(bm, name, [M_STEEL], smooth_round=True)


TRUSS_Z = 3.75
build_truss("TrussFront", (-HALF_W + 0.2, -1.4), (HALF_W - 0.2, -1.4), TRUSS_Z)
build_truss("TrussBack", (-HALF_W + 0.2, 2.2), (HALF_W - 0.2, 2.2), TRUSS_Z)
bm = bmesh.new()
for sx in (-1, 1):
    for y in (-1.4, 2.2):
        bm_tube_between(bm, (sx * (HALF_W - 0.2), y, 0.10), (sx * (HALF_W - 0.2), y, TRUSS_Z - 0.15), 0.05, 0)
finish(bm, "TrussLegs", [M_STEEL], smooth_round=True)


# ------------------------------------------------------------------ fixtures
def spot_fixture(name, pos, target, energy=350.0, angle_deg=32.0, color=(1.0, 0.96, 0.9)):
    bm = bmesh.new()
    bm_cyl(bm, (0, 0, -0.02), 0.05, 0.06, 0, segments=16)      # yoke block
    bm_cyl(bm, (0, 0, -0.16), 0.075, 0.22, 0, segments=20, r2=0.095)
    body = finish(bm, name + "_Body", [M_BLACK], location=pos, smooth_round=True)
    look_at(body, target)

    ld = bpy.data.lights.new(name + "_Light", 'SPOT')
    ld.energy = energy
    ld.color = color
    ld.spot_size = math.radians(angle_deg)
    ld.spot_blend = 0.35
    ld.shadow_soft_size = 0.06
    lo = bpy.data.objects.new(name + "_Light", ld)
    lo.location = pos
    link(lo)
    look_at(lo, target)
    return body


for i, (px, py, pz) in enumerate(tops):
    src_y = -1.4 if py < 0.8 else 2.2
    spot_fixture("SpotPlinth%d" % i, (px * 0.75, src_y, TRUSS_Z - 0.22), (px, py, pz + 0.15),
                 energy=260.0, angle_deg=26.0)

spot_fixture("SpotGraphic", (-1.4, 2.2, TRUSS_Z - 0.22), (-1.4, HALF_D - 0.2, 2.0),
             energy=200.0, angle_deg=45.0)
spot_fixture("SpotCounter", (2.3, -1.4, TRUSS_Z - 0.22), (2.6, -2.05, 1.15),
             energy=220.0, angle_deg=38.0)

# soft fill above the booth and a broad hall light
fill = bpy.data.lights.new("BoothFill", 'AREA')
fill.shape = 'RECTANGLE'
fill.size, fill.size_y = 7.0, 5.0
fill.energy = 420.0
fill.color = (0.95, 0.96, 1.0)
fo = bpy.data.objects.new("BoothFill", fill)
fo.location = (0, 0.2, 5.2)
link(fo)

key = bpy.data.lights.new("HallKey", 'AREA')
key.shape = 'RECTANGLE'
key.size, key.size_y = 10.0, 6.0
key.energy = 700.0
ko = bpy.data.objects.new("HallKey", key)
ko.location = (-6.0, -8.0, 6.5)
link(ko)
look_at(ko, (0, 0, 1.5))

# ------------------------------------------------------------- hall backdrop
bm = bmesh.new()
bm_box(bm, (0, 0, -0.01), (60, 60, 0.02), 0)
finish(bm, "HallFloor", [make_mat("HallFloor", (0.20, 0.20, 0.22), rough=0.35)])

world = bpy.data.worlds.new("BoothWorld")
world.use_nodes = True
bg = world.node_tree.nodes["Background"]
bg.inputs["Color"].default_value = (0.045, 0.05, 0.06, 1.0)
bg.inputs["Strength"].default_value = 1.0
bpy.context.scene.world = world

# ------------------------------------------------------------------- camera
cam_data = bpy.data.cameras.new("BoothCam")
cam_data.lens = 32.0
cam_data.clip_end = 500.0
cam = bpy.data.objects.new("BoothCam", cam_data)
cam.location = (8.4, -9.6, 4.6)
link(cam)
look_at(cam, (0.0, 0.4, 1.45))
bpy.context.scene.camera = cam

bpy.context.view_layer.update()
print("claude-046: exhibition booth built with %d objects" % len(bpy.data.objects))
