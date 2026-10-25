"""claude-134 - Shoe shop interior.

Builds a retail shoe store from Blender's factory startup: room shell with a
glass storefront, full-height wall shelving stocked with shoes, a large fitting
mirror with seating, display islands and an L-shaped checkout desk.

Scene construction only - nothing is rendered or saved.
"""

import math
import random

import bmesh
import bpy
from mathutils import Euler, Matrix, Vector

random.seed(20240134)

TAU = math.tau
RAD = math.radians

# Room shell (interior volume).
RX = 4.0          # half width  -> x in [-4, 4]
RY = 5.0          # half depth  -> y in [-5, 5]
RZ = 3.30         # ceiling height
WALL_T = 0.16


# ---------------------------------------------------------------------------
# generic helpers
# ---------------------------------------------------------------------------

def reset_scene():
    bpy.ops.wm.read_factory_settings(use_empty=True)
    scene = bpy.context.scene
    scene.unit_settings.system = 'METRIC'
    scene.render.engine = 'CYCLES'
    scene.cycles.samples = 160
    scene.render.resolution_x = 1920
    scene.render.resolution_y = 1080
    scene.render.film_transparent = False
    scene.view_settings.look = 'AgX - Medium High Contrast'

    world = bpy.data.worlds.new("ShopWorld")
    world.use_nodes = True
    scene.world = world
    bg = world.node_tree.nodes["Background"]
    bg.inputs["Color"].default_value = (0.34, 0.40, 0.50, 1.0)  # daylight outside
    bg.inputs["Strength"].default_value = 0.9


def get_collection(name):
    coll = bpy.data.collections.get(name)
    if coll is None:
        coll = bpy.data.collections.new(name)
        bpy.context.scene.collection.children.link(coll)
    return coll


def set_input(node, names, value):
    """Assign the first socket that exists (input names moved around in 4.x)."""
    for n in names:
        sock = node.inputs.get(n)
        if sock is not None:
            sock.default_value = value
            return True
    return False


def M(loc=(0.0, 0.0, 0.0), scale=(1.0, 1.0, 1.0), rot=(0.0, 0.0, 0.0)):
    """Translation @ rotation @ non-uniform scale, as a 4x4 matrix."""
    return (Matrix.Translation(Vector(loc))
            @ Euler(rot, 'XYZ').to_matrix().to_4x4()
            @ Matrix.Diagonal(Vector(scale).to_4d()))


def add_prim(bm, kind, matrix, mat_index=0, smooth=False, bevel=0.0,
             bevel_segs=2, **kw):
    """Append a unit primitive (edge length / diameter == 1) shaped by *matrix*."""
    before = set(bm.faces)

    if kind == 'cube':
        bmesh.ops.create_cube(bm, size=1.0, matrix=matrix)
    elif kind == 'sphere':
        bmesh.ops.create_uvsphere(bm,
                                  u_segments=kw.get('u', 16),
                                  v_segments=kw.get('v', 10),
                                  radius=0.5, matrix=matrix)
    elif kind == 'cyl':
        bmesh.ops.create_cone(bm, cap_ends=True, cap_tris=False,
                              segments=kw.get('seg', 24),
                              radius1=kw.get('r1', 0.5),
                              radius2=kw.get('r2', 0.5),
                              depth=1.0, matrix=matrix)
    elif kind == 'ico':
        bmesh.ops.create_icosphere(bm, subdivisions=kw.get('sub', 2),
                                   radius=0.5, matrix=matrix)
    else:
        raise ValueError(kind)

    if bevel > 0.0:
        fresh = [f for f in bm.faces if f not in before]
        geom = set()
        for f in fresh:
            geom.add(f)
            geom.update(f.verts)
            geom.update(f.edges)
        bmesh.ops.bevel(bm, geom=list(geom), offset=bevel, segments=bevel_segs,
                        affect='EDGES', profile=0.5, clamp_overlap=True)

    faces = [f for f in bm.faces if f not in before]
    for f in faces:
        f.material_index = mat_index
        f.smooth = smooth
    return faces


def faces_verts(faces):
    vs = set()
    for f in faces:
        vs.update(f.verts)
    return list(vs)


def bm_to_mesh(bm, name, materials=()):
    me = bpy.data.meshes.new(name)
    bm.to_mesh(me)
    bm.free()
    for mat in materials:
        me.materials.append(mat)
    return me


def new_object(name, mesh, coll, matrix=None, loc=None, rot=(0, 0, 0)):
    obj = bpy.data.objects.new(name, mesh)
    coll.objects.link(obj)
    if matrix is not None:
        obj.matrix_world = matrix
    else:
        obj.location = loc or (0.0, 0.0, 0.0)
        obj.rotation_euler = rot
    return obj


def bm_object(name, bm, coll, materials=(), matrix=None, loc=None, rot=(0, 0, 0)):
    return new_object(name, bm_to_mesh(bm, name + "Mesh", materials), coll,
                      matrix=matrix, loc=loc, rot=rot)


# ---------------------------------------------------------------------------
# materials
# ---------------------------------------------------------------------------

def simple_mat(name, color, rough=0.5, metallic=0.0, emission=None,
               emit_strength=1.0, transmission=0.0, ior=1.45):
    mat = bpy.data.materials.new(name)
    mat.use_nodes = True
    bsdf = mat.node_tree.nodes["Principled BSDF"]
    bsdf.inputs["Base Color"].default_value = (*color, 1.0)
    bsdf.inputs["Roughness"].default_value = rough
    bsdf.inputs["Metallic"].default_value = metallic
    set_input(bsdf, ["IOR"], ior)
    if transmission:
        set_input(bsdf, ["Transmission Weight", "Transmission"], transmission)
    if emission is not None:
        set_input(bsdf, ["Emission Color", "Emission"], (*emission, 1.0))
        set_input(bsdf, ["Emission Strength"], emit_strength)
    return mat


def wood_floor_mat():
    mat = bpy.data.materials.new("OakFloor")
    mat.use_nodes = True
    nt = mat.node_tree
    bsdf = nt.nodes["Principled BSDF"]

    coord = nt.nodes.new("ShaderNodeTexCoord")
    coord.location = (-1000, 0)
    mapping = nt.nodes.new("ShaderNodeMapping")
    mapping.location = (-800, 0)
    mapping.inputs["Scale"].default_value = (1.0, 0.06, 1.0)  # stretched planks

    grain = nt.nodes.new("ShaderNodeTexNoise")
    grain.location = (-600, 60)
    grain.inputs["Scale"].default_value = 7.0
    grain.inputs["Detail"].default_value = 9.0
    grain.inputs["Roughness"].default_value = 0.62

    ramp = nt.nodes.new("ShaderNodeValToRGB")
    ramp.location = (-380, 60)
    ramp.color_ramp.elements[0].position = 0.32
    ramp.color_ramp.elements[0].color = (0.213, 0.130, 0.068, 1.0)
    ramp.color_ramp.elements[1].position = 0.72
    ramp.color_ramp.elements[1].color = (0.430, 0.286, 0.156, 1.0)

    rough = nt.nodes.new("ShaderNodeTexNoise")
    rough.location = (-600, -240)
    rough.inputs["Scale"].default_value = 40.0
    rough_ramp = nt.nodes.new("ShaderNodeValToRGB")
    rough_ramp.location = (-380, -240)
    rough_ramp.color_ramp.elements[0].color = (0.22, 0.22, 0.22, 1.0)
    rough_ramp.color_ramp.elements[1].color = (0.42, 0.42, 0.42, 1.0)

    nt.links.new(coord.outputs["Object"], mapping.inputs["Vector"])
    nt.links.new(mapping.outputs["Vector"], grain.inputs["Vector"])
    nt.links.new(grain.outputs["Fac"], ramp.inputs["Fac"])
    nt.links.new(ramp.outputs["Color"], bsdf.inputs["Base Color"])
    nt.links.new(coord.outputs["Object"], rough.inputs["Vector"])
    nt.links.new(rough.outputs["Fac"], rough_ramp.inputs["Fac"])
    nt.links.new(rough_ramp.outputs["Color"], bsdf.inputs["Roughness"])
    return mat


def build_materials():
    m = {}
    m['floor'] = wood_floor_mat()
    m['wall'] = simple_mat("WallPlaster", (0.855, 0.840, 0.815), rough=0.88)
    m['wall_accent'] = simple_mat("WallAccent", (0.150, 0.175, 0.180), rough=0.80)
    m['ceiling'] = simple_mat("Ceiling", (0.900, 0.900, 0.895), rough=0.92)
    m['skirting'] = simple_mat("Skirting", (0.780, 0.770, 0.750), rough=0.55)

    m['oak'] = simple_mat("ShelfOak", (0.560, 0.410, 0.245), rough=0.44)
    m['oak_dark'] = simple_mat("WalnutPanel", (0.180, 0.110, 0.062), rough=0.40)
    m['steel'] = simple_mat("BrushedSteel", (0.720, 0.730, 0.740),
                            rough=0.30, metallic=1.0)
    m['black_metal'] = simple_mat("BlackMetal", (0.035, 0.035, 0.038),
                                  rough=0.40, metallic=1.0)
    m['brass'] = simple_mat("Brass", (0.760, 0.580, 0.250), rough=0.24, metallic=1.0)
    m['mirror'] = simple_mat("MirrorGlass", (0.930, 0.935, 0.940),
                             rough=0.015, metallic=1.0)
    m['glass'] = simple_mat("Storefront", (0.930, 0.960, 0.960),
                            rough=0.02, transmission=1.0, ior=1.45)
    m['stone'] = simple_mat("CounterStone", (0.085, 0.088, 0.092), rough=0.18)
    m['rug'] = simple_mat("Rug", (0.300, 0.255, 0.230), rough=0.95)
    m['fabric_a'] = simple_mat("FabricTeal", (0.055, 0.190, 0.195), rough=0.85)
    m['fabric_b'] = simple_mat("FabricOchre", (0.470, 0.290, 0.075), rough=0.85)
    m['screen'] = simple_mat("POSScreen", (0.02, 0.02, 0.03), rough=0.25,
                             emission=(0.20, 0.35, 0.55), emit_strength=2.2)
    m['led'] = simple_mat("LEDStrip", (1.0, 0.94, 0.86), rough=0.4,
                          emission=(1.0, 0.90, 0.78), emit_strength=14.0)
    m['panel'] = simple_mat("CeilingPanel", (1.0, 0.97, 0.93), rough=0.4,
                            emission=(1.0, 0.95, 0.88), emit_strength=7.0)
    m['sign'] = simple_mat("SignLetters", (0.92, 0.90, 0.86), rough=0.35,
                           emission=(1.0, 0.86, 0.62), emit_strength=3.0)
    m['carton'] = simple_mat("ShoeBoxCarton", (0.560, 0.430, 0.290), rough=0.90)
    m['carton_lid'] = simple_mat("ShoeBoxLid", (0.120, 0.135, 0.170), rough=0.85)
    m['pot'] = simple_mat("PlanterPot", (0.400, 0.380, 0.355), rough=0.70)
    m['leaf'] = simple_mat("Foliage", (0.075, 0.190, 0.070), rough=0.62)
    m['acrylic'] = simple_mat("AcrylicRiser", (0.90, 0.92, 0.94), rough=0.06,
                              transmission=0.92)

    # shoe leathers / textiles
    m['uppers'] = [
        simple_mat("UpperWhite", (0.850, 0.845, 0.830), rough=0.42),
        simple_mat("UpperBlack", (0.030, 0.030, 0.033), rough=0.34),
        simple_mat("UpperTan", (0.360, 0.190, 0.085), rough=0.46),
        simple_mat("UpperNavy", (0.030, 0.055, 0.145), rough=0.50),
        simple_mat("UpperRed", (0.400, 0.045, 0.045), rough=0.38),
        simple_mat("UpperOlive", (0.140, 0.150, 0.075), rough=0.60),
        simple_mat("UpperCream", (0.700, 0.640, 0.520), rough=0.58),
        simple_mat("UpperGrey", (0.230, 0.235, 0.245), rough=0.62),
        simple_mat("UpperBlush", (0.560, 0.330, 0.320), rough=0.48),
        simple_mat("UpperCobalt", (0.055, 0.150, 0.400), rough=0.44),
    ]
    m['soles'] = [
        simple_mat("SoleWhite", (0.780, 0.775, 0.760), rough=0.55),
        simple_mat("SoleGum", (0.430, 0.260, 0.120), rough=0.62),
        simple_mat("SoleBlack", (0.045, 0.045, 0.048), rough=0.58),
        simple_mat("SoleCream", (0.640, 0.590, 0.480), rough=0.60),
    ]
    return m


# ---------------------------------------------------------------------------
# shoe prototypes (shared mesh data, per-object material overrides)
# ---------------------------------------------------------------------------

UPPER, SOLE = 0, 1
PROTOS = {}


def _taper_heel(faces, factor=0.80, pivot=-0.02):
    """Narrow the rear part of a sole slab so it reads as a footprint."""
    for v in faces_verts(faces):
        if v.co.x < pivot:
            v.co.y *= factor
            v.co.x *= 1.02


def build_shoe_mesh(style):
    bm = bmesh.new()

    if style == 'sneaker':
        sole = add_prim(bm, 'cube', M((0.0, 0.0, 0.017), (0.272, 0.100, 0.034)),
                        SOLE, bevel=0.013, bevel_segs=2)
        _taper_heel(sole, 0.82)
        add_prim(bm, 'cube', M((-0.004, 0.0, 0.062), (0.240, 0.092, 0.062)),
                 UPPER, smooth=True, bevel=0.030, bevel_segs=4)
        add_prim(bm, 'sphere', M((0.086, 0.0, 0.050), (0.088, 0.086, 0.070)),
                 UPPER, smooth=True, u=14, v=9)
        add_prim(bm, 'sphere', M((-0.092, 0.0, 0.082), (0.078, 0.088, 0.086)),
                 UPPER, smooth=True, u=14, v=9)
        # tongue / lace panel
        add_prim(bm, 'cube', M((0.010, 0.0, 0.098), (0.110, 0.052, 0.020),
                               (0.0, RAD(-9.0), 0.0)),
                 UPPER, bevel=0.008, bevel_segs=2)

    elif style == 'loafer':
        sole = add_prim(bm, 'cube', M((0.0, 0.0, 0.012), (0.262, 0.096, 0.024)),
                        SOLE, bevel=0.009, bevel_segs=2)
        _taper_heel(sole, 0.78)
        add_prim(bm, 'sphere', M((0.000, 0.0, 0.046), (0.250, 0.094, 0.084)),
                 UPPER, smooth=True, u=18, v=11)
        add_prim(bm, 'sphere', M((0.082, 0.0, 0.038), (0.130, 0.088, 0.062)),
                 UPPER, smooth=True, u=14, v=9)
        add_prim(bm, 'sphere', M((-0.092, 0.0, 0.052), (0.086, 0.090, 0.090)),
                 UPPER, smooth=True, u=14, v=9)
        add_prim(bm, 'cube', M((0.020, 0.0, 0.078), (0.060, 0.070, 0.010)),
                 SOLE, bevel=0.004)

    elif style == 'heel':
        sole = add_prim(bm, 'cube',
                        M((0.0, 0.0, 0.052), (0.250, 0.086, 0.014),
                          (0.0, RAD(-11.0), 0.0)),
                        SOLE, bevel=0.006, bevel_segs=2)
        _taper_heel(sole, 0.76)
        add_prim(bm, 'cyl', M((-0.100, 0.0, 0.038), (0.040, 0.040, 0.078)),
                 SOLE, smooth=True, seg=14, r1=0.5, r2=0.28)
        add_prim(bm, 'cube', M((-0.100, 0.0, 0.001), (0.036, 0.030, 0.006)),
                 SOLE)
        add_prim(bm, 'sphere', M((0.078, 0.0, 0.082), (0.110, 0.084, 0.058)),
                 UPPER, smooth=True, u=14, v=9)
        add_prim(bm, 'sphere', M((-0.070, 0.0, 0.108), (0.090, 0.086, 0.096)),
                 UPPER, smooth=True, u=14, v=9)
        add_prim(bm, 'cube', M((0.012, 0.0, 0.086), (0.070, 0.070, 0.012),
                               (0.0, RAD(-11.0), 0.0)),
                 UPPER, bevel=0.004)

    elif style == 'boot':
        sole = add_prim(bm, 'cube', M((0.0, 0.0, 0.018), (0.268, 0.102, 0.036)),
                        SOLE, bevel=0.012, bevel_segs=2)
        _taper_heel(sole, 0.82)
        add_prim(bm, 'cube', M((0.0, 0.0, 0.072), (0.244, 0.096, 0.070)),
                 UPPER, smooth=True, bevel=0.032, bevel_segs=4)
        add_prim(bm, 'sphere', M((0.088, 0.0, 0.058), (0.090, 0.088, 0.072)),
                 UPPER, smooth=True, u=14, v=9)
        add_prim(bm, 'cyl', M((-0.058, 0.0, 0.200), (0.124, 0.112, 0.230)),
                 UPPER, smooth=True, seg=18)
        add_prim(bm, 'cyl', M((-0.058, 0.0, 0.312), (0.132, 0.120, 0.020)),
                 SOLE, smooth=True, seg=18)

    else:
        raise ValueError(style)

    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    return bm_to_mesh(bm, "Shoe_" + style)


def build_shoe_protos(mats):
    for style in ('sneaker', 'loafer', 'heel', 'boot'):
        me = build_shoe_mesh(style)
        me.materials.append(mats['uppers'][0])   # slot 0 default
        me.materials.append(mats['soles'][0])    # slot 1 default
        PROTOS[style] = me


def place_shoe(name, style, loc, rot_z, upper, sole, coll, scale=1.0,
               tilt=(0.0, 0.0)):
    obj = bpy.data.objects.new(name, PROTOS[style])
    coll.objects.link(obj)
    obj.location = loc
    obj.rotation_euler = (tilt[0], tilt[1], rot_z)
    obj.scale = (scale, scale, scale)
    for idx, mat in ((0, upper), (1, sole)):
        slot = obj.material_slots[idx]
        slot.link = 'OBJECT'
        slot.material = mat
    return obj


def place_pair(name, style, center, facing, mats, coll, spread=0.135,
               splay=13.0, scale=1.0, upper=None, sole=None):
    """Two shoes side by side, slightly splayed like a retail display."""
    upper = upper or random.choice(mats['uppers'])
    sole = sole or random.choice(mats['soles'])
    right = Vector((math.cos(facing - math.pi / 2.0),
                    math.sin(facing - math.pi / 2.0), 0.0))
    out = []
    for i, side in enumerate((-0.5, 0.5)):
        pos = Vector(center) + right * (side * spread)
        jitter = RAD(random.uniform(-4.0, 4.0))
        rot = facing + RAD(splay) * (1 if side > 0 else -1) + jitter
        out.append(place_shoe("%s_%d" % (name, i), style, pos, rot,
                              upper, sole, coll, scale=scale))
    return out


# ---------------------------------------------------------------------------
# architecture
# ---------------------------------------------------------------------------

def build_shell(mats):
    coll = get_collection("Shell")

    bm = bmesh.new()
    add_prim(bm, 'cube', M((0.0, 0.0, -0.06), (2 * RX + 2 * WALL_T,
                                               2 * RY + 2 * WALL_T, 0.12)), 0)
    bm_object("Floor", bm, coll, (mats['floor'],))

    bm = bmesh.new()
    add_prim(bm, 'cube', M((0.0, 0.0, RZ + 0.06), (2 * RX + 2 * WALL_T,
                                                   2 * RY + 2 * WALL_T, 0.12)), 0)
    bm_object("Ceiling", bm, coll, (mats['ceiling'],))

    # side + back walls (slot 0 plaster, slot 1 accent on the back wall)
    bm = bmesh.new()
    add_prim(bm, 'cube', M((-RX - WALL_T / 2, 0.0, RZ / 2),
                           (WALL_T, 2 * RY + 2 * WALL_T, RZ)), 0)
    add_prim(bm, 'cube', M((RX + WALL_T / 2, 0.0, RZ / 2),
                           (WALL_T, 2 * RY + 2 * WALL_T, RZ)), 0)
    add_prim(bm, 'cube', M((0.0, RY + WALL_T / 2, RZ / 2),
                           (2 * RX, WALL_T, RZ)), 1)
    bm_object("Walls", bm, coll, (mats['wall'], mats['wall_accent']))

    # skirting along the three solid walls
    bm = bmesh.new()
    add_prim(bm, 'cube', M((-RX + 0.01, 0.0, 0.055), (0.022, 2 * RY, 0.11)), 0)
    add_prim(bm, 'cube', M((RX - 0.01, 0.0, 0.055), (0.022, 2 * RY, 0.11)), 0)
    add_prim(bm, 'cube', M((0.0, RY - 0.01, 0.055), (2 * RX, 0.022, 0.11)), 0)
    bm_object("Skirting", bm, coll, (mats['skirting'],))

    # storefront: mullion grid at y = -RY, glazing between
    frame = bmesh.new()
    glass = bmesh.new()
    y = -RY + 0.06
    add_prim(frame, 'cube', M((0.0, y, 0.06), (2 * RX, 0.14, 0.12)), 0)
    add_prim(frame, 'cube', M((0.0, y, RZ - 0.09), (2 * RX, 0.14, 0.18)), 0)
    for mx in (-RX + 0.06, -1.55, -0.05, 1.45, RX - 0.06):
        add_prim(frame, 'cube', M((mx, y, RZ / 2), (0.11, 0.14, RZ)), 0)
    # door leaf frame in the -0.05 .. 1.45 bay
    add_prim(frame, 'cube', M((0.70, y - 0.02, 1.10), (1.30, 0.07, 0.05)), 0)
    add_prim(frame, 'cube', M((0.02, y - 0.06, 1.05), (0.04, 0.04, 0.90)), 0)
    for cx, w in ((-2.80, 2.36), (-0.80, 1.36), (0.70, 1.36), (2.80, 2.36)):
        add_prim(glass, 'cube', M((cx, y, 1.68), (w, 0.02, 3.0)), 0)
    bm_object("StorefrontFrame", frame, coll, (mats['black_metal'],))
    bm_object("StorefrontGlass", glass, coll, (mats['glass'],))

    # recessed ceiling light panels + lighting tracks
    bm = bmesh.new()
    for py in (-3.2, -0.6, 2.0, 4.0):
        add_prim(bm, 'cube', M((0.0, py, RZ - 0.035), (2.6, 0.42, 0.07)), 0)
    bm_object("CeilingPanels", bm, coll, (mats['panel'],))

    bm = bmesh.new()
    for tx in (-3.30, 3.30):
        add_prim(bm, 'cube', M((tx, 0.4, RZ - 0.06), (0.06, 7.6, 0.09)), 0)
        for ty in (-2.6, -0.6, 1.4, 3.4):
            add_prim(bm, 'cyl', M((tx, ty, RZ - 0.17), (0.07, 0.07, 0.15)),
                     0, smooth=True, seg=12)
            add_prim(bm, 'cyl', M((tx, ty, RZ - 0.30),
                                  (0.10, 0.10, 0.15),
                                  (0.0, RAD(28.0) * (1 if tx < 0 else -1), 0.0)),
                     0, smooth=True, seg=14)
    bm_object("LightTrack", bm, coll, (mats['black_metal'],))


# ---------------------------------------------------------------------------
# wall shelving
# ---------------------------------------------------------------------------

def build_shelf_unit(name, mw, length, depth, height, levels, bays, mats,
                     coll, base_z=0.22, top_gap=0.30):
    """Wall shelving built in local space (+X = length, +Y = into the room).

    Returns a list of world-space (location, facing, level_z) display slots.
    """
    t = 0.036
    bm = bmesh.new()
    led = bmesh.new()

    add_prim(bm, 'cube', M((0.0, 0.018, height / 2), (length, 0.036, height)), 0)
    add_prim(bm, 'cube', M((0.0, depth / 2 - 0.03, 0.055),
                           (length, depth - 0.06, 0.11)), 0)          # toe kick

    xs = [-length / 2 + t / 2 + i * (length - t) / bays for i in range(bays + 1)]
    for px in xs:
        add_prim(bm, 'cube', M((px, depth / 2, height / 2), (t, depth, height)), 0)

    usable = height - base_z - top_gap
    step = usable / max(levels - 1, 1)
    shelf_z = [base_z + i * step for i in range(levels)]
    shelf_z.append(height - t / 2)

    for z in shelf_z:
        add_prim(bm, 'cube', M((0.0, depth / 2, z), (length - 0.02, depth, t)), 0)
        add_prim(led, 'cube', M((0.0, depth - 0.055, z - t / 2 - 0.011),
                                (length - 0.10, 0.026, 0.016)), 0)

    obj = bm_object(name, bm, coll, (mats['oak'],), matrix=mw)
    bm_object(name + "_LED", led, coll, (mats['led'],), matrix=mw)

    facing = mw.to_euler().z + math.pi / 2.0   # local +Y, shoes point into room
    pitch = 0.44
    count = max(int((length - 0.30) // pitch), 1)
    slots = []
    for z in shelf_z[:-1]:
        for i in range(count):
            lx = -((count - 1) * pitch) / 2.0 + i * pitch
            local = Vector((lx, depth * 0.55, z + t / 2))
            slots.append((mw @ local, facing, z))
    return obj, slots


def stock_shelves(slots, mats, coll, tag, box_levels=()):
    """Fill display slots with shoe pairs; some rows get stacked boxes."""
    styles = ('sneaker', 'loafer', 'heel', 'boot', 'sneaker', 'loafer')
    for i, (pos, facing, z) in enumerate(slots):
        if z in box_levels:
            build_box_stack("%s_Box%03d" % (tag, i), Vector(pos), facing,
                            random.randint(2, 3), mats, coll)
            continue
        if random.random() < 0.07:
            continue                                    # a few empty gaps
        style = styles[(i + random.randint(0, 1)) % len(styles)]
        if style == 'boot' and random.random() < 0.5:
            style = 'sneaker'
        place_pair("%s_Pair%03d" % (tag, i), style, pos,
                   facing + RAD(random.uniform(-6.0, 6.0)), mats, coll,
                   spread=random.uniform(0.125, 0.150),
                   splay=random.uniform(6.0, 18.0),
                   scale=random.uniform(0.94, 1.06))


# ---------------------------------------------------------------------------
# props
# ---------------------------------------------------------------------------

def build_box_stack(name, loc, rot_z, count, mats, coll):
    bm = bmesh.new()
    z = 0.0
    for _ in range(count):
        h = 0.125
        add_prim(bm, 'cube', M((random.uniform(-0.012, 0.012),
                                random.uniform(-0.012, 0.012), z + h / 2),
                               (0.335, 0.225, h),
                               (0.0, 0.0, RAD(random.uniform(-4.0, 4.0)))),
                 0, bevel=0.006)
        add_prim(bm, 'cube', M((0.0, 0.0, z + h - 0.014), (0.345, 0.235, 0.030)),
                 1, bevel=0.005)
        z += h + 0.006
    return bm_object(name, bm, coll, (mats['carton'], mats['carton_lid']),
                     loc=loc, rot=(0.0, 0.0, rot_z))


def build_mirror(mats, coll):
    bm = bmesh.new()
    glass = bmesh.new()
    x = RX - 0.02
    add_prim(bm, 'cube', M((x - 0.03, 0.9, 1.30), (0.10, 1.62, 2.26)),
             0, bevel=0.012)
    add_prim(glass, 'cube', M((x - 0.075, 0.9, 1.30), (0.02, 1.46, 2.10)), 0)
    bm_object("MirrorFrame", bm, coll, (mats['oak_dark'],))
    bm_object("MirrorGlassPane", glass, coll, (mats['mirror'],))

    # low tilted shoe mirror by the seating
    bm = bmesh.new()
    glass = bmesh.new()
    add_prim(bm, 'cube', M((2.35, -0.85, 0.24), (0.62, 0.09, 0.46),
                           (RAD(-24.0), 0.0, RAD(-12.0))), 0, bevel=0.01)
    add_prim(glass, 'cube', M((2.35, -0.885, 0.245), (0.54, 0.02, 0.38),
                              (RAD(-24.0), 0.0, RAD(-12.0))), 0)
    add_prim(bm, 'cyl', M((2.35, -0.72, 0.06), (0.24, 0.24, 0.03)),
             0, smooth=True, seg=18)
    bm_object("FloorMirrorFrame", bm, coll, (mats['black_metal'],))
    bm_object("FloorMirrorGlass", glass, coll, (mats['mirror'],))


def build_ottoman(name, loc, rot_z, mat_fabric, mats, coll):
    bm = bmesh.new()
    add_prim(bm, 'cube', M((0.0, 0.0, 0.375), (1.05, 0.50, 0.20)),
             0, smooth=True, bevel=0.075, bevel_segs=4)
    add_prim(bm, 'cube', M((0.0, 0.0, 0.255), (0.98, 0.44, 0.10)), 0, bevel=0.02)
    for sx in (-0.42, 0.42):
        for sy in (-0.17, 0.17):
            add_prim(bm, 'cyl', M((sx, sy, 0.105), (0.05, 0.05, 0.21),
                                  (RAD(5.0) * (1 if sy > 0 else -1), 0.0, 0.0)),
                     1, smooth=True, seg=10, r1=0.5, r2=0.36)
    return bm_object(name, bm, coll, (mat_fabric, mats['black_metal']),
                     loc=loc, rot=(0.0, 0.0, rot_z))


def build_island_round(name, loc, radius, height, mats, coll):
    bm = bmesh.new()
    add_prim(bm, 'cyl', M((0.0, 0.0, height / 2), (radius * 2, radius * 2, height)),
             0, smooth=True, seg=40)
    add_prim(bm, 'cyl', M((0.0, 0.0, height + 0.018),
                          (radius * 2 + 0.06, radius * 2 + 0.06, 0.036)),
             1, smooth=True, seg=40)
    add_prim(bm, 'cyl', M((0.0, 0.0, 0.02), (radius * 2 - 0.10,
                                             radius * 2 - 0.10, 0.04)),
             1, smooth=True, seg=40)
    return bm_object(name, bm, coll, (mats['oak'], mats['oak_dark']),
                     loc=loc, rot=(0.0, 0.0, 0.0))


def build_island_table(name, loc, rot_z, size, height, mats, coll):
    sx, sy = size
    bm = bmesh.new()
    add_prim(bm, 'cube', M((0.0, 0.0, height - 0.025), (sx, sy, 0.05)),
             0, bevel=0.008)
    add_prim(bm, 'cube', M((0.0, 0.0, height - 0.14), (sx - 0.14, sy - 0.14, 0.18)),
             1, bevel=0.006)
    for ex in (-1, 1):
        for ey in (-1, 1):
            add_prim(bm, 'cyl', M((ex * (sx / 2 - 0.09), ey * (sy / 2 - 0.09),
                                   (height - 0.06) / 2),
                                  (0.045, 0.045, height - 0.06)),
                     1, smooth=True, seg=10)
    add_prim(bm, 'cube', M((0.0, 0.0, 0.32), (sx - 0.20, sy - 0.20, 0.04)),
             1, bevel=0.005)
    return bm_object(name, bm, coll, (mats['oak'], mats['black_metal']),
                     loc=loc, rot=(0.0, 0.0, rot_z))


def build_riser(name, loc, rot_z, size, mats, coll):
    bm = bmesh.new()
    add_prim(bm, 'cube', M((0.0, 0.0, size[2] / 2), size), 0, bevel=0.006)
    return bm_object(name, bm, coll, (mats['acrylic'],),
                     loc=loc, rot=(0.0, 0.0, rot_z))


def build_checkout(mats, coll):
    """L-shaped counter in the right-front corner plus a back console."""
    mw = (Matrix.Translation(Vector((2.35, -2.90, 0.0)))
          @ Matrix.Rotation(RAD(-14.0), 4, 'Z'))
    body = bmesh.new()
    h = 1.02

    # main run (local X) and short return (local Y)
    add_prim(body, 'cube', M((0.0, 0.0, h / 2 - 0.05), (2.30, 0.66, h - 0.10)),
             0, bevel=0.012)
    add_prim(body, 'cube', M((-0.82, 0.78, h / 2 - 0.05), (0.66, 0.90, h - 0.10)),
             0, bevel=0.012)
    # recessed plinth
    add_prim(body, 'cube', M((0.0, 0.0, 0.05), (2.20, 0.56, 0.10)), 1)
    add_prim(body, 'cube', M((-0.82, 0.78, 0.05), (0.56, 0.80, 0.10)), 1)
    # stone top with overhang
    add_prim(body, 'cube', M((0.0, -0.015, h + 0.02), (2.42, 0.74, 0.06)),
             2, bevel=0.008)
    add_prim(body, 'cube', M((-0.82, 0.80, h + 0.02), (0.78, 0.96, 0.06)),
             2, bevel=0.008)
    # drawer lines on the customer face
    for i in range(3):
        add_prim(body, 'cube', M((-0.62 + i * 0.62, -0.335, 0.72),
                                 (0.54, 0.02, 0.03)), 1)
    bm_object("CheckoutCounter", body, coll,
              (mats['oak_dark'], mats['black_metal'], mats['stone']), matrix=mw)

    top = mw @ Matrix.Translation(Vector((0.0, 0.0, h + 0.05)))

    # POS terminal
    pos = bmesh.new()
    add_prim(pos, 'cyl', M((0.55, 0.06, 0.015), (0.24, 0.24, 0.03)),
             0, smooth=True, seg=20)
    add_prim(pos, 'cyl', M((0.55, 0.06, 0.12), (0.05, 0.05, 0.19)),
             0, smooth=True, seg=12)
    add_prim(pos, 'cube', M((0.55, 0.10, 0.32), (0.40, 0.03, 0.27),
                            (RAD(-16.0), 0.0, 0.0)), 0, bevel=0.008)
    add_prim(pos, 'cube', M((0.55, 0.086, 0.322), (0.36, 0.02, 0.235),
                            (RAD(-16.0), 0.0, 0.0)), 1)
    add_prim(pos, 'cube', M((-0.15, -0.02, 0.035), (0.26, 0.18, 0.07),
                            (0.0, RAD(-12.0), RAD(20.0))), 0, bevel=0.006)
    pos_obj = bm_object("POSTerminal", pos, coll,
                        (mats['black_metal'], mats['screen']), matrix=top)

    # paper bags + tissue on the counter
    bags = bmesh.new()
    for bx, by, bh in ((-0.95, 0.02, 0.30), (-0.72, -0.06, 0.26)):
        add_prim(bags, 'cube', M((bx, by, bh / 2), (0.26, 0.14, bh),
                                 (0.0, 0.0, RAD(random.uniform(-12, 12)))),
                 0, bevel=0.006)
        add_prim(bags, 'cyl', M((bx, by, bh + 0.02), (0.12, 0.12, 0.04),
                                (RAD(90.0), 0.0, 0.0)), 0, smooth=True, seg=12)
    bm_object("CounterBags", bags, coll, (mats['carton_lid'],), matrix=top)

    # back console against the right wall
    back = bmesh.new()
    add_prim(back, 'cube', M((RX - 0.30, -3.95, 0.44), (0.58, 1.70, 0.88)),
             0, bevel=0.010)
    add_prim(back, 'cube', M((RX - 0.30, -3.95, 0.90), (0.64, 1.78, 0.05)),
             1, bevel=0.006)
    for sz in (1.35, 1.75, 2.15):
        add_prim(back, 'cube', M((RX - 0.22, -3.95, sz), (0.42, 1.70, 0.035)), 0)
    bm_object("BackConsole", back, coll, (mats['oak_dark'], mats['stone']))

    # stock boxes stored on the console shelves
    for i, sz in enumerate((1.37, 1.77)):
        for j in range(2):
            build_box_stack("ConsoleBox%d_%d" % (i, j),
                            Vector((RX - 0.26, -4.40 + j * 0.90, sz)),
                            RAD(90.0 + random.uniform(-8, 8)),
                            random.randint(1, 2), mats, coll)
    return pos_obj


def build_plant(name, loc, mats, coll):
    bm = bmesh.new()
    add_prim(bm, 'cyl', M((0.0, 0.0, 0.20), (0.34, 0.34, 0.40)),
             0, smooth=True, seg=24, r1=0.5, r2=0.42)
    add_prim(bm, 'cyl', M((0.0, 0.0, 0.40), (0.38, 0.38, 0.05)),
             0, smooth=True, seg=24)
    add_prim(bm, 'cyl', M((0.0, 0.0, 0.60), (0.05, 0.05, 0.40)),
             1, smooth=True, seg=8)
    for i in range(9):
        a = i * TAU / 9.0 + random.uniform(-0.2, 0.2)
        r = random.uniform(0.14, 0.34)
        add_prim(bm, 'ico',
                 M((math.cos(a) * r, math.sin(a) * r,
                    0.80 + random.uniform(0.0, 0.42)),
                   (random.uniform(0.26, 0.44),) * 3),
                 1, smooth=True, sub=2)
    return bm_object(name, bm, coll, (mats['pot'], mats['leaf']),
                     loc=loc, rot=(0.0, 0.0, random.uniform(0.0, TAU)))


def build_rug(mats, coll):
    bm = bmesh.new()
    add_prim(bm, 'cube', M((2.45, 0.75, 0.006), (2.60, 2.90, 0.012)),
             0, bevel=0.004)
    return bm_object("Rug", bm, coll, (mats['rug'],))


def build_signage(mats, coll):
    cu = bpy.data.curves.new("SignCurve", type='FONT')
    cu.body = "SOLE & CO."
    cu.align_x = 'CENTER'
    cu.align_y = 'CENTER'
    cu.size = 0.34
    cu.extrude = 0.014
    cu.space_character = 0.9
    obj = bpy.data.objects.new("WallSign", cu)
    coll.objects.link(obj)
    obj.location = (0.0, RY - 0.06, 2.62)
    obj.rotation_euler = (RAD(90.0), 0.0, 0.0)
    obj.data.materials.append(mats['sign'])

    cu2 = bpy.data.curves.new("PayCurve", type='FONT')
    cu2.body = "PAY HERE"
    cu2.align_x = 'CENTER'
    cu2.align_y = 'CENTER'
    cu2.size = 0.13
    cu2.extrude = 0.006
    obj2 = bpy.data.objects.new("CheckoutSign", cu2)
    coll.objects.link(obj2)
    obj2.location = (RX - 0.075, -3.95, 2.50)
    obj2.rotation_euler = (RAD(90.0), 0.0, RAD(-90.0))
    obj2.data.materials.append(mats['sign'])
    return obj, obj2


# ---------------------------------------------------------------------------
# lighting & camera
# ---------------------------------------------------------------------------

def add_area(name, loc, size, power, color, coll, rot=(0, 0, 0), size_y=None):
    data = bpy.data.lights.new(name, 'AREA')
    data.shape = 'RECTANGLE'
    data.size = size
    data.size_y = size_y if size_y is not None else size
    data.energy = power
    data.color = color
    obj = bpy.data.objects.new(name, data)
    coll.objects.link(obj)
    obj.location = loc
    obj.rotation_euler = rot
    return obj


def add_spot(name, loc, target, power, color, coll, spot_size=55.0, blend=0.35,
             radius=0.05):
    data = bpy.data.lights.new(name, 'SPOT')
    data.energy = power
    data.color = color
    data.spot_size = RAD(spot_size)
    data.spot_blend = blend
    data.shadow_soft_size = radius
    obj = bpy.data.objects.new(name, data)
    coll.objects.link(obj)
    obj.location = loc
    direction = Vector(target) - Vector(loc)
    obj.rotation_euler = direction.to_track_quat('-Z', 'Y').to_euler()
    return obj


def build_lighting():
    coll = get_collection("Lighting")
    warm = (1.0, 0.90, 0.79)
    neutral = (1.0, 0.96, 0.92)

    for py in (-3.2, -0.6, 2.0, 4.0):
        add_area("CeilingArea_%s" % py, (0.0, py, RZ - 0.10), 2.5, 140.0,
                 neutral, coll, size_y=0.45)

    # accent spots washing the two shelving walls
    for ty in (-2.6, -0.6, 1.4, 3.4):
        add_spot("SpotL_%s" % ty, (-3.30, ty, RZ - 0.30),
                 (-3.95, ty + 0.25, 1.45), 90.0, warm, coll, spot_size=52.0)
        add_spot("SpotR_%s" % ty, (3.30, ty, RZ - 0.30),
                 (3.95, ty + 0.25, 1.45), 70.0, warm, coll, spot_size=52.0)

    add_spot("SpotBackWall", (0.0, 3.6, RZ - 0.25), (0.0, 4.85, 1.60),
             120.0, warm, coll, spot_size=70.0)
    add_spot("SpotIslandA", (-1.0, 0.6, RZ - 0.28), (-1.0, 0.6, 0.55),
             80.0, warm, coll, spot_size=45.0)
    add_spot("SpotIslandB", (1.15, -0.9, RZ - 0.28), (1.15, -0.9, 0.80),
             80.0, warm, coll, spot_size=45.0)
    add_spot("SpotCheckout", (2.35, -2.60, RZ - 0.28), (2.35, -2.95, 1.05),
             90.0, neutral, coll, spot_size=60.0)

    # daylight spilling in through the storefront
    add_area("DaylightFill", (0.0, -RY - 0.6, 1.70), 6.0, 320.0,
             (0.80, 0.87, 1.0), coll, rot=(RAD(90.0), 0.0, 0.0), size_y=2.6)


def build_camera():
    coll = get_collection("Camera")
    data = bpy.data.cameras.new("ShopCam")
    data.lens = 22.0
    data.sensor_width = 36.0
    data.clip_start = 0.05
    data.clip_end = 120.0
    data.dof.use_dof = True
    data.dof.focus_distance = 6.2
    data.dof.aperture_fstop = 4.5

    cam = bpy.data.objects.new("ShopCam", data)
    coll.objects.link(cam)
    cam.location = (-2.85, -4.30, 1.62)
    target = Vector((0.55, 1.70, 1.05))
    cam.rotation_euler = (target - cam.location).to_track_quat('-Z', 'Y').to_euler()
    bpy.context.scene.camera = cam
    return cam


# ---------------------------------------------------------------------------
# assembly
# ---------------------------------------------------------------------------

def build_shop():
    reset_scene()
    mats = build_materials()
    build_shoe_protos(mats)

    build_shell(mats)

    fixtures = get_collection("Fixtures")
    stock = get_collection("Stock")
    props = get_collection("Props")

    # --- left wall shelving (x = -4), 7.4 m long -----------------------------
    mw_left = (Matrix.Translation(Vector((-RX + 0.02, 0.55, 0.0)))
               @ Matrix.Rotation(RAD(-90.0), 4, 'Z'))
    _, left_slots = build_shelf_unit("ShelvingLeft", mw_left, length=7.40,
                                     depth=0.36, height=2.55, levels=6, bays=6,
                                     mats=mats, coll=fixtures)
    stock_shelves(left_slots, mats, stock, "L")

    # --- back wall shelving (y = +5) ----------------------------------------
    mw_back = (Matrix.Translation(Vector((0.0, RY - 0.02, 0.0)))
               @ Matrix.Rotation(RAD(180.0), 4, 'Z'))
    _, back_slots = build_shelf_unit("ShelvingBack", mw_back, length=5.60,
                                     depth=0.36, height=2.30, levels=5, bays=4,
                                     mats=mats, coll=fixtures)
    box_row = sorted({z for _, _, z in back_slots})[0]
    stock_shelves(back_slots, mats, stock, "B", box_levels=(box_row,))

    # --- right wall: short shelving run above the seating -------------------
    mw_right = (Matrix.Translation(Vector((RX - 0.02, 2.90, 0.0)))
                @ Matrix.Rotation(RAD(90.0), 4, 'Z'))
    _, right_slots = build_shelf_unit("ShelvingRight", mw_right, length=3.40,
                                      depth=0.34, height=2.35, levels=5, bays=3,
                                      mats=mats, coll=fixtures)
    stock_shelves(right_slots, mats, stock, "R")

    # --- mirror + seating ----------------------------------------------------
    build_mirror(mats, fixtures)
    build_rug(mats, props)
    build_ottoman("OttomanA", (2.30, 1.55, 0.0), RAD(-96.0), mats['fabric_a'],
                  mats, props)
    build_ottoman("OttomanB", (2.55, 0.05, 0.0), RAD(-82.0), mats['fabric_b'],
                  mats, props)

    # a pair being tried on, left in front of the mirror
    place_shoe("TryOnA", 'sneaker', (2.95, 0.95, 0.0), RAD(150.0),
               mats['uppers'][4], mats['soles'][0], stock)
    place_shoe("TryOnB", 'sneaker', (3.05, 0.72, 0.0), RAD(-160.0),
               mats['uppers'][4], mats['soles'][0], stock)
    build_box_stack("TryOnBox", Vector((2.55, 1.05, 0.42)), RAD(-95.0), 1,
                    mats, props)

    # --- display islands -----------------------------------------------------
    build_island_round("IslandRoundA", (-1.05, 0.60, 0.0), 0.62, 0.46,
                       mats, fixtures)
    build_riser("RiserA1", (-1.05, 0.72, 0.50), RAD(18.0), (0.36, 0.26, 0.13),
                mats, fixtures)
    place_pair("IslandA_Hero", 'heel', (-1.05, 0.72, 0.63), RAD(-58.0),
               mats, stock, spread=0.16, splay=22.0,
               upper=mats['uppers'][8], sole=mats['soles'][2])
    place_pair("IslandA_P2", 'loafer', (-1.42, 0.28, 0.50), RAD(-125.0),
               mats, stock, splay=16.0)
    place_pair("IslandA_P3", 'sneaker', (-0.68, 0.30, 0.50), RAD(-45.0),
               mats, stock, splay=12.0)

    build_island_table("IslandTable", (1.15, -0.95, 0.0), RAD(-8.0),
                       (1.70, 0.95), 0.78, mats, fixtures)
    build_riser("RiserB1", (0.75, -0.75, 0.78), RAD(-8.0), (0.42, 0.30, 0.16),
                mats, fixtures)
    place_pair("IslandT_P1", 'sneaker', (0.75, -0.75, 0.94), RAD(-100.0),
               mats, stock, splay=15.0, upper=mats['uppers'][0],
               sole=mats['soles'][1])
    place_pair("IslandT_P2", 'boot', (1.55, -0.72, 0.80), RAD(-115.0),
               mats, stock, spread=0.17, splay=10.0,
               upper=mats['uppers'][2], sole=mats['soles'][2])
    place_pair("IslandT_P3", 'loafer', (1.20, -1.22, 0.80), RAD(-75.0),
               mats, stock, splay=18.0)
    place_pair("IslandT_P4", 'heel', (0.62, -1.22, 0.80), RAD(-62.0),
               mats, stock, splay=20.0)
    build_box_stack("IslandT_Boxes", Vector((1.15, -0.95, 0.34)), RAD(-8.0), 2,
                    mats, props)

    build_island_round("IslandRoundB", (-1.55, 2.75, 0.0), 0.50, 0.68,
                       mats, fixtures)
    place_pair("IslandB_P1", 'boot', (-1.55, 2.75, 0.72), RAD(-150.0),
               mats, stock, spread=0.18, splay=14.0,
               upper=mats['uppers'][5], sole=mats['soles'][2])

    # --- checkout ------------------------------------------------------------
    build_checkout(mats, fixtures)
    build_box_stack("FloorBoxes1", Vector((3.35, -2.05, 0.0)), RAD(24.0), 4,
                    mats, props)
    build_box_stack("FloorBoxes2", Vector((3.05, -1.72, 0.0)), RAD(-12.0), 3,
                    mats, props)

    # --- greenery & signage --------------------------------------------------
    build_plant("PlantEntry", (-3.10, -4.05, 0.0), mats, props)
    build_plant("PlantCorner", (-3.25, 4.35, 0.0), mats, props)
    build_signage(mats, props)

    build_lighting()
    build_camera()

    bpy.context.view_layer.update()


if __name__ == "__main__":
    build_shop()
