"""Blender 4.5 LTS - small arched timber footbridge with deck, posts and railings."""
import bpy, bmesh, math, random
from mathutils import Vector


# ----------------------------------------------------------------- helpers
def reset_scene():
    bpy.ops.wm.read_factory_settings(use_empty=True)
    scene = bpy.context.scene
    for engine in ("BLENDER_EEVEE_NEXT", "BLENDER_EEVEE", "CYCLES"):
        try:
            scene.render.engine = engine
            break
        except TypeError:
            continue
    world = bpy.data.worlds.new("World")
    world.use_nodes = True
    scene.world = world
    return scene


def world_color(color, strength=1.0):
    bg = bpy.context.scene.world.node_tree.nodes["Background"]
    bg.inputs[0].default_value = (color[0], color[1], color[2], 1.0)
    bg.inputs[1].default_value = strength


def mkmat(name, color, rough=0.5, metal=0.0, transmission=0.0, ior=1.33, alpha=1.0):
    mat = bpy.data.materials.new(name)
    mat.use_nodes = True
    b = mat.node_tree.nodes["Principled BSDF"]
    b.inputs["Base Color"].default_value = (color[0], color[1], color[2], 1.0)
    b.inputs["Roughness"].default_value = rough
    b.inputs["Metallic"].default_value = metal
    if "IOR" in b.inputs:
        b.inputs["IOR"].default_value = ior
    if transmission and "Transmission Weight" in b.inputs:
        b.inputs["Transmission Weight"].default_value = transmission
    if alpha < 1.0:
        b.inputs["Alpha"].default_value = alpha
        try:
            mat.blend_method = 'BLEND'
        except TypeError:
            mat.blend_method = 'HASHED'
    return mat


def link(ob):
    bpy.context.scene.collection.objects.link(ob)
    return ob


def _finish(name, bm, mat, loc, rot, smooth, parent, scale=(1.0, 1.0, 1.0)):
    if smooth:
        for f in bm.faces:
            f.smooth = True
        for e in bm.edges:
            if e.calc_face_angle(0.0) > 0.62:
                e.smooth = False
    me = bpy.data.meshes.new(name)
    bm.to_mesh(me)
    bm.free()
    if mat is not None:
        me.materials.append(mat)
    ob = bpy.data.objects.new(name, me)
    ob.location = loc
    ob.rotation_euler = rot
    ob.scale = scale
    if parent is not None:
        ob.parent = parent
    return link(ob)


def box(name, size, loc=(0, 0, 0), rot=(0, 0, 0), mat=None, shift=(0, 0, 0), parent=None):
    bm = bmesh.new()
    bmesh.ops.create_cube(bm, size=1.0)
    bmesh.ops.scale(bm, vec=Vector(size), verts=bm.verts)
    if any(shift):
        bmesh.ops.translate(bm, verts=bm.verts, vec=Vector(shift))
    return _finish(name, bm, mat, loc, rot, False, parent)


def cylinder(name, radius, depth, loc=(0, 0, 0), rot=(0, 0, 0), mat=None,
             segments=16, radius_top=None, parent=None):
    bm = bmesh.new()
    bmesh.ops.create_cone(bm, cap_ends=True, cap_tris=False, segments=segments,
                          radius1=radius,
                          radius2=(radius if radius_top is None else radius_top),
                          depth=depth)
    return _finish(name, bm, mat, loc, rot, True, parent)


def rock(name, radius, loc, mat, seed=0, scale=(1.0, 1.0, 1.0), rot=(0, 0, 0)):
    rnd = random.Random(seed)
    bm = bmesh.new()
    bmesh.ops.create_icosphere(bm, subdivisions=2, radius=radius)
    for v in bm.verts:
        v.co *= 1.0 + rnd.uniform(-0.22, 0.22)
    return _finish(name, bm, mat, loc, rot, False, None, scale)


def add_camera(loc, target, lens=35.0):
    cam = bpy.data.cameras.new("Camera")
    cam.lens = lens
    ob = bpy.data.objects.new("Camera", cam)
    ob.location = loc
    ob.rotation_euler = (Vector(target) - Vector(loc)).to_track_quat('-Z', 'Y').to_euler()
    link(ob)
    bpy.context.scene.camera = ob
    return ob


def add_light(name, ltype, loc, energy, color=(1, 1, 1), size=1.0, target=None):
    lt = bpy.data.lights.new(name, ltype)
    lt.energy = energy
    lt.color = color
    if ltype == 'AREA':
        lt.size = size
    elif ltype in ('POINT', 'SPOT'):
        lt.shadow_soft_size = size
    ob = bpy.data.objects.new(name, lt)
    ob.location = loc
    if target is not None:
        ob.rotation_euler = (Vector(target) - Vector(loc)).to_track_quat('-Z', 'Y').to_euler()
    return link(ob)


# ------------------------------------------------------------------- scene
reset_scene()
world_color((0.45, 0.58, 0.78), 1.0)
random.seed(21)

m_deck = mkmat("Deck Timber", (0.44, 0.31, 0.19), rough=0.78)
m_beam = mkmat("Beam Timber", (0.30, 0.20, 0.12), rough=0.82)
m_rail = mkmat("Rail Timber", (0.51, 0.37, 0.23), rough=0.72)
m_post = mkmat("Post Timber", (0.36, 0.25, 0.15), rough=0.8)
m_bolt = mkmat("Bolt", (0.42, 0.43, 0.45), rough=0.4, metal=1.0)
m_stone = mkmat("Stone", (0.46, 0.45, 0.42), rough=0.88)
m_grass = mkmat("Grass Bank", (0.20, 0.31, 0.13), rough=0.95)
m_soil = mkmat("Soil", (0.21, 0.16, 0.11), rough=0.95)
m_water = mkmat("Stream Water", (0.09, 0.20, 0.24), rough=0.06, transmission=0.9, ior=1.33)
m_gravel = mkmat("Gravel Path", (0.55, 0.52, 0.47), rough=0.9)

# ---- bridge geometry parameters -----------------------------------------
SPAN = 6.0                 # along X, from -3 to +3
WIDTH = 1.60               # along Y
CAMBER = 0.30
END_H = 0.12               # deck surface height at the abutments


def deck_z(x):
    return END_H + CAMBER * math.cos(math.pi * x / SPAN)


def deck_slope(x):
    return -CAMBER * (math.pi / SPAN) * math.sin(math.pi * x / SPAN)


# ---- banks, stream bed, water -------------------------------------------
box("BankLeft", (9.0, 12.0, 2.0), (-7.2, 0, -1.0), mat=m_grass)
box("BankRight", (9.0, 12.0, 2.0), (7.2, 0, -1.0), mat=m_grass)
box("StreamBed", (5.6, 12.0, 1.4), (0, 0, -1.62), mat=m_soil)
for sgn in (-1, 1):
    box("BankSlope", (1.5, 12.0, 0.9), (sgn * 2.55, 0, -0.52),
        rot=(0, math.radians(-30 * sgn), 0), mat=m_soil)
    box("BankEdge", (1.2, 12.0, 0.30), (sgn * 3.55, 0, -0.15), mat=m_grass)
box("Water", (5.4, 12.0, 0.04), (0, 0, -0.72), mat=m_water)

# gravel approach paths
for sgn in (-1, 1):
    box("Path", (3.4, 1.5, 0.06), (sgn * 5.0, 0, 0.02), mat=m_gravel)

# ---- abutments -----------------------------------------------------------
for sgn in (-1, 1):
    box("Abutment", (0.90, 2.10, 1.30), (sgn * 3.15, 0, -0.60), mat=m_stone)
    box("AbutmentCap", (1.00, 2.20, 0.10), (sgn * 3.15, 0, 0.00), mat=m_stone)
    for i in range(3):
        rock("AbutStone", 0.28, (sgn * 3.6, -0.8 + i * 0.8, -0.55), m_stone,
             seed=i + sgn * 10, scale=(1.2, 1.0, 0.8))

# ---- stringers (two curved beams under the deck) ------------------------
NSEG = 24
BEAM_H = 0.24
for sy in (-0.62, 0.62):
    for i in range(NSEG):
        x0 = -SPAN / 2 + SPAN * i / NSEG
        x1 = -SPAN / 2 + SPAN * (i + 1) / NSEG
        xm = 0.5 * (x0 + x1)
        s = deck_slope(xm)
        seg_len = (x1 - x0) * math.sqrt(1.0 + s * s) * 1.04
        box("Stringer", (seg_len, 0.11, BEAM_H),
            (xm, sy, deck_z(xm) - 0.055 - BEAM_H / 2),
            rot=(0, -math.atan(s), 0), mat=m_beam)

# cross bracing under the deck
for bx in (-2.0, -0.7, 0.7, 2.0):
    box("CrossBrace", (0.10, 1.30, 0.10), (bx, 0.0, deck_z(bx) - 0.10 - BEAM_H),
        rot=(0, -math.atan(deck_slope(bx)), 0), mat=m_beam)

# ---- deck planks ---------------------------------------------------------
NPLANK = 30
PLANK_T = 0.05
for i in range(NPLANK):
    xm = -SPAN / 2 + SPAN * (i + 0.5) / NPLANK
    s = deck_slope(xm)
    plank_len = (SPAN / NPLANK) * math.sqrt(1.0 + s * s) - 0.006
    box("Plank%02d" % i, (plank_len, WIDTH, PLANK_T),
        (xm, 0.0, deck_z(xm) - PLANK_T / 2),
        rot=(0, -math.atan(s), 0), mat=m_deck)

# ---- posts, rails and balusters -----------------------------------------
POST_X = [-2.72, -1.63, -0.54, 0.54, 1.63, 2.72]
POST_H = 1.00
RAIL_TOP = 0.96
RAIL_MID = 0.50
for sy in (-(WIDTH / 2 - 0.06), (WIDTH / 2 - 0.06)):
    for px in POST_X:
        z0 = deck_z(px)
        box("Post", (0.09, 0.09, POST_H + 0.16), (px, sy, z0 - 0.16 + (POST_H + 0.16) / 2),
            mat=m_post)
        box("PostCap", (0.13, 0.13, 0.03), (px, sy, z0 + POST_H + 0.015), mat=m_rail)
        for bz in (0.28, 0.62):
            cylinder("PostBolt", 0.011, 0.13, (px, sy, z0 + bz),
                     rot=(math.pi / 2, 0, 0), mat=m_bolt, segments=8)
    # continuous curved handrail and mid rail
    for i in range(NSEG):
        x0 = -SPAN / 2 + SPAN * i / NSEG
        x1 = -SPAN / 2 + SPAN * (i + 1) / NSEG
        xm = 0.5 * (x0 + x1)
        s = deck_slope(xm)
        seg_len = (x1 - x0) * math.sqrt(1.0 + s * s) * 1.03
        rot = (0, -math.atan(s), 0)
        box("HandRail", (seg_len, 0.12, 0.06), (xm, sy, deck_z(xm) + RAIL_TOP), rot=rot, mat=m_rail)
        box("MidRail", (seg_len, 0.07, 0.05), (xm, sy, deck_z(xm) + RAIL_MID), rot=rot, mat=m_rail)
    # balusters
    nbal = 25
    for i in range(nbal):
        bx = -SPAN / 2 + 0.14 + (SPAN - 0.28) * i / (nbal - 1.0)
        if min(abs(bx - px) for px in POST_X) < 0.10:
            continue
        z0 = deck_z(bx)
        box("Baluster", (0.035, 0.035, RAIL_TOP - 0.03),
            (bx, sy, z0 + (RAIL_TOP - 0.03) / 2), mat=m_rail)

# ---- kerb rails along the deck edges ------------------------------------
for sy in (-(WIDTH / 2 - 0.02), (WIDTH / 2 - 0.02)):
    for i in range(NSEG):
        x0 = -SPAN / 2 + SPAN * i / NSEG
        x1 = -SPAN / 2 + SPAN * (i + 1) / NSEG
        xm = 0.5 * (x0 + x1)
        s = deck_slope(xm)
        box("Kerb", ((x1 - x0) * math.sqrt(1 + s * s) * 1.03, 0.05, 0.09),
            (xm, sy, deck_z(xm) + 0.02), rot=(0, -math.atan(s), 0), mat=m_beam)

# ---- stream rocks and bank detail ---------------------------------------
for i in range(10):
    rx = random.uniform(-2.2, 2.2)
    ry = random.uniform(-4.0, 4.0)
    if abs(ry) < 1.4 and abs(rx) < 1.0:
        continue
    r = random.uniform(0.10, 0.26)
    rock("StreamRock%d" % i, r, (rx, ry, -0.80 + r * 0.4), m_stone, seed=i,
         scale=(1.3, 1.0, 0.7), rot=(0, 0, random.uniform(0, 6.28)))
for i in range(6):
    rock("BankRock%d" % i, random.uniform(0.14, 0.3),
         (random.choice([-4.0, 4.0]) + random.uniform(-0.5, 0.5),
          random.uniform(-3.5, 3.5), 0.05), m_stone, seed=30 + i,
         scale=(1.2, 1.1, 0.6))

# ---- lighting and camera -------------------------------------------------
sun = add_light("Sun", 'SUN', (6.0, -8.0, 9.0), 3.6, (1.0, 0.95, 0.86))
sun.rotation_euler = (Vector((0, 0, 0.3)) - Vector((6.0, -8.0, 9.0))).to_track_quat('-Z', 'Y').to_euler()
sun.data.angle = math.radians(1.5)
add_light("SkyFill", 'AREA', (-5.0, 6.0, 6.0), 500.0, (0.62, 0.76, 1.0),
          size=10.0, target=(0, 0, 0.3))
add_camera((5.60, -6.20, 2.40), (-0.20, 0.10, 0.35), lens=40.0)
