"""claude-147 - Multilevel car park facade with ramps, columns and horizontal barriers.

Five parking decks on a column grid, alternating internal ramps with kerb walls,
perimeter upstands and horizontal precast safety bands on every facade,
plus a stair / lift core and a few parked cars for scale.
"""

import bpy
import bmesh
import math
from mathutils import Vector, Matrix, Euler


# ----------------------------------------------------------------------------
# helpers
# ----------------------------------------------------------------------------
def reset_scene():
    bpy.ops.wm.read_factory_settings(use_empty=True)
    scn = bpy.context.scene
    try:
        scn.render.engine = 'BLENDER_EEVEE_NEXT'
    except Exception:
        pass
    world = bpy.data.worlds.new("World")
    scn.world = world
    world.use_nodes = True
    bg = world.node_tree.nodes["Background"]
    bg.inputs[0].default_value = (0.30, 0.40, 0.55, 1.0)
    bg.inputs[1].default_value = 1.2
    return scn


def link(obj):
    bpy.context.scene.collection.objects.link(obj)
    return obj


def new_mat(name, color, rough=0.6, metal=0.0, alpha=1.0, emit=None, emit_str=0.0):
    mat = bpy.data.materials.new(name)
    mat.use_nodes = True
    bsdf = mat.node_tree.nodes["Principled BSDF"]

    def s(key, value):
        if key in bsdf.inputs:
            bsdf.inputs[key].default_value = value

    s("Base Color", (color[0], color[1], color[2], 1.0))
    s("Roughness", rough)
    s("Metallic", metal)
    s("Alpha", alpha)
    if emit is not None:
        s("Emission Color", (emit[0], emit[1], emit[2], 1.0))
        s("Emission Strength", emit_str)
    if alpha < 1.0:
        try:
            mat.blend_method = 'BLEND'
        except Exception:
            pass
    return mat


def obj_from_bm(name, bm, mat=None, smooth=False):
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    me = bpy.data.meshes.new(name)
    bm.to_mesh(me)
    bm.free()
    if smooth:
        for poly in me.polygons:
            poly.use_smooth = True
    ob = bpy.data.objects.new(name, me)
    if mat is not None:
        ob.data.materials.append(mat)
    return link(ob)


def box_bm(bm, center, size, rot=(0.0, 0.0, 0.0)):
    m = Matrix.Translation(Vector(center))
    m = m @ Euler(rot, 'XYZ').to_matrix().to_4x4()
    m = m @ Matrix.Diagonal(Vector((size[0], size[1], size[2], 1.0)))
    bmesh.ops.create_cube(bm, size=1.0, matrix=m)


def cyl_bm(bm, center, radius, depth, axis='Z', segments=12):
    rot = {'Z': Matrix.Identity(4),
           'X': Matrix.Rotation(math.radians(90.0), 4, 'Y'),
           'Y': Matrix.Rotation(math.radians(90.0), 4, 'X')}[axis]
    m = Matrix.Translation(Vector(center)) @ rot
    bmesh.ops.create_cone(bm, cap_ends=True, cap_tris=False, segments=segments,
                          radius1=radius, radius2=radius, depth=depth, matrix=m)


def add_camera(location, target, lens=38.0):
    cam_data = bpy.data.cameras.new("Camera")
    cam_data.lens = lens
    cam_data.clip_end = 2000.0
    cam = bpy.data.objects.new("Camera", cam_data)
    link(cam)
    cam.location = location
    cam.rotation_euler = (Vector(target) - Vector(location)).to_track_quat('-Z', 'Y').to_euler()
    bpy.context.scene.camera = cam
    return cam


def add_sun(rotation, energy=4.0, color=(1.0, 0.96, 0.9)):
    data = bpy.data.lights.new("Sun", 'SUN')
    data.energy = energy
    data.angle = math.radians(2.0)
    data.color = color
    ob = bpy.data.objects.new("Sun", data)
    link(ob)
    ob.rotation_euler = rotation
    return ob


def add_area(location, size, energy, rotation=(0.0, 0.0, 0.0), color=(1.0, 1.0, 1.0)):
    data = bpy.data.lights.new("Area", 'AREA')
    data.size = size
    data.energy = energy
    data.color = color
    ob = bpy.data.objects.new("Area", data)
    link(ob)
    ob.location = location
    ob.rotation_euler = rotation
    return ob


# ----------------------------------------------------------------------------
# parameters
# ----------------------------------------------------------------------------
W = 44.0            # building width  (X)
D = 32.0            # building depth  (Y)
FH = 3.2            # floor to floor
LEVELS = 5          # parking decks (ground + 4) plus roof deck
SLAB_T = 0.30
COL = 0.5
RAMP_Y = 11.0
RAMP_W = 6.0
RAMP_HALF = 11.0    # ramp runs from -11 to +11 in X


def build():
    reset_scene()

    m_concrete = new_mat("Concrete", (0.70, 0.69, 0.66), rough=0.75)
    m_deck = new_mat("DeckConcrete", (0.60, 0.59, 0.57), rough=0.85)
    m_barrier = new_mat("BarrierSteel", (0.80, 0.81, 0.83), rough=0.35, metal=0.9)
    m_core = new_mat("CoreConcrete", (0.55, 0.54, 0.53), rough=0.8)
    m_glass = new_mat("Glazing", (0.35, 0.5, 0.6), rough=0.08, metal=0.0, alpha=0.35)
    m_asphalt = new_mat("Asphalt", (0.09, 0.09, 0.10), rough=0.95)
    m_paint = new_mat("LineMarking", (0.85, 0.82, 0.30), rough=0.6)
    m_rubber = new_mat("Tyre", (0.05, 0.05, 0.06), rough=0.9)
    car_mats = [new_mat("CarPaintA", (0.65, 0.08, 0.08), rough=0.25, metal=0.5),
                new_mat("CarPaintB", (0.09, 0.16, 0.42), rough=0.25, metal=0.5),
                new_mat("CarPaintC", (0.82, 0.82, 0.84), rough=0.3, metal=0.5)]

    # ---- ground -----------------------------------------------------------
    bm = bmesh.new()
    box_bm(bm, (0.0, 0.0, -0.4), (300.0, 300.0, 0.8))
    obj_from_bm("Ground", bm, m_asphalt)

    bm = bmesh.new()
    for i in range(-8, 9):
        box_bm(bm, (i * 4.0, -D / 2 - 9.0, 0.015), (2.4, 0.18, 0.04))
    obj_from_bm("RoadMarkings", bm, m_paint)

    # ---- slabs ------------------------------------------------------------
    bm = bmesh.new()
    for lvl in range(LEVELS + 1):
        z = lvl * FH
        box_bm(bm, (0.0, 0.0, z - SLAB_T * 0.5), (W, D, SLAB_T))
    obj_from_bm("Slabs", bm, m_deck)

    # ---- columns ----------------------------------------------------------
    xs = [-18.0 + i * 6.0 for i in range(7)]
    ys = [-12.0, -4.0, 4.0, 12.0]
    bm = bmesh.new()
    for lvl in range(LEVELS):
        z0 = lvl * FH
        h = FH - SLAB_T
        for x in xs:
            for y in ys:
                if y > 7.0 and abs(x) < RAMP_HALF + 1.0:
                    continue  # ramp bay kept clear
                box_bm(bm, (x, y, z0 + h * 0.5), (COL, COL, h))
        # edge beams along the long facades
        for y in (-D / 2 + 0.25, D / 2 - 0.25):
            box_bm(bm, (0.0, y, z0 + FH - SLAB_T - 0.3), (W - 1.0, 0.35, 0.6))
    obj_from_bm("Columns", bm, m_concrete)

    # ---- ramps ------------------------------------------------------------
    run = RAMP_HALF * 2.0
    ang = math.atan2(FH, run)
    length = math.hypot(run, FH)
    bm = bmesh.new()
    bm_kerb = bmesh.new()
    for lvl in range(LEVELS):
        sign = 1.0 if lvl % 2 == 0 else -1.0
        cz = lvl * FH + FH * 0.5
        rot = (0.0, -sign * ang, 0.0)
        box_bm(bm, (0.0, RAMP_Y, cz), (length, RAMP_W, 0.28), rot)
        for dy in (-RAMP_W * 0.5 - 0.12, RAMP_W * 0.5 + 0.12):
            box_bm(bm_kerb, (0.0, RAMP_Y + dy, cz + 0.5), (length, 0.24, 0.85), rot)
        # landing slabs at both ends of each flight
        box_bm(bm, (sign * (RAMP_HALF + 3.0), RAMP_Y, (lvl + 1) * FH - 0.14),
               (6.0, RAMP_W, 0.28))
    obj_from_bm("Ramps", bm, m_deck)
    obj_from_bm("RampKerbs", bm_kerb, m_concrete)

    # ---- perimeter upstands + horizontal safety barriers -------------------
    facades = [
        ((0.0, -D / 2 + 0.12, 0.0), W - 0.4, 0.0),
        ((0.0, D / 2 - 0.12, 0.0), W - 0.4, 0.0),
        ((-W / 2 + 0.12, 0.0, 0.0), D - 0.4, math.pi / 2.0),
        ((W / 2 - 0.12, 0.0, 0.0), D - 0.4, math.pi / 2.0),
    ]

    bm_up = bmesh.new()
    bm_band = bmesh.new()
    band_heights = (0.62, 1.20, 1.78, 2.36)
    for lvl in range(LEVELS):
        z0 = lvl * FH
        for (cx, cy, _), span, rz in facades:
            box_bm(bm_up, (cx, cy, z0 + 0.26), (span, 0.30, 0.52), (0.0, 0.0, rz))
            for bh in band_heights:
                box_bm(bm_band, (cx, cy, z0 + bh), (span - 0.3, 0.16, 0.26),
                       (0.0, 0.0, rz))
            # vertical barrier posts tying the bands back to the structure
            n = 12 if abs(rz) < 0.01 else 9
            for i in range(n):
                t = -0.5 + (i + 0.5) / n
                px = cx + (span * t if abs(rz) < 0.01 else 0.0)
                py = cy + (0.0 if abs(rz) < 0.01 else span * t)
                box_bm(bm_band, (px, py, z0 + 1.55), (0.10, 0.10, 2.0),
                       (0.0, 0.0, rz))
    # roof deck parapet
    for (cx, cy, _), span, rz in facades:
        box_bm(bm_up, (cx, cy, LEVELS * FH + 0.55), (span, 0.30, 1.10), (0.0, 0.0, rz))
    obj_from_bm("Upstands", bm_up, m_concrete)
    obj_from_bm("SafetyBarriers", bm_band, m_barrier)

    # ---- stair / lift core -------------------------------------------------
    core_h = LEVELS * FH + 3.2
    cx = W / 2.0 + 4.0
    bm = bmesh.new()
    box_bm(bm, (cx, -9.0, core_h * 0.5), (8.0, 10.0, core_h))
    box_bm(bm, (cx, -9.0, core_h + 0.25), (8.8, 10.8, 0.5))
    obj_from_bm("Core", bm, m_core)

    bm = bmesh.new()
    for lvl in range(LEVELS + 1):
        box_bm(bm, (cx - 4.05, -9.0, lvl * FH + 1.6), (0.12, 7.0, 1.6))
        box_bm(bm, (cx, -14.05, lvl * FH + 1.6), (5.0, 0.12, 1.6))
    obj_from_bm("CoreGlazing", bm, m_glass)

    # link bridges from core to each deck
    bm = bmesh.new()
    for lvl in range(LEVELS + 1):
        box_bm(bm, (W / 2.0 + 1.0, -9.0, lvl * FH - 0.15), (4.0, 4.0, 0.3))
    obj_from_bm("CoreLinks", bm, m_deck)

    # ---- parked cars -------------------------------------------------------
    placements = [(-14.0, -12.0, 0, 0), (-8.0, -12.0, 1, 0), (-2.0, -12.0, 2, 0),
                  (10.0, 4.0, 1, math.pi), (16.0, 4.0, 0, math.pi),
                  (-14.0, -12.0 + FH * 2, 2, 0), (2.0, 4.0, 0, math.pi)]
    bm_wheels = bmesh.new()
    for idx, (x, y, ci, rz) in enumerate(placements):
        z = 0.0 if idx < 5 else FH * 2.0
        if idx == 5:
            x, y, z = -14.0, -12.0, FH * 2.0
        bmc = bmesh.new()
        box_bm(bmc, (x, y, z + 0.72), (4.5, 1.86, 0.66), (0.0, 0.0, rz))
        box_bm(bmc, (x - 0.25 * math.cos(rz), y, z + 1.32), (2.5, 1.70, 0.56),
               (0.0, 0.0, rz))
        obj_from_bm("Car_%02d" % idx, bmc, car_mats[ci])
        for dx in (-1.55, 1.55):
            for dy in (-0.95, 0.95):
                wx = x + dx * math.cos(rz) - dy * math.sin(rz)
                wy = y + dx * math.sin(rz) + dy * math.cos(rz)
                cyl_bm(bm_wheels, (wx, wy, z + 0.34), 0.34, 0.24,
                       axis='Y' if abs(rz) < 0.01 else 'Y', segments=12)
    obj_from_bm("CarWheels", bm_wheels, m_rubber)

    # ---- deck bay markings -------------------------------------------------
    bm = bmesh.new()
    for lvl in range(LEVELS + 1):
        z = lvl * FH + 0.01
        for y in (-12.0, 4.0):
            for i in range(15):
                box_bm(bm, (-19.0 + i * 2.7, y, z), (0.10, 4.8, 0.02))
    obj_from_bm("BayMarkings", bm, m_paint)

    # ---- lighting & camera -------------------------------------------------
    add_sun((math.radians(56.0), math.radians(4.0), math.radians(-52.0)), energy=4.5)
    add_area((40.0, -46.0, 34.0), 45.0, 16000.0,
             rotation=(math.radians(52.0), 0.0, math.radians(40.0)),
             color=(0.78, 0.85, 1.0))
    add_camera((58.0, -54.0, 27.0), (0.0, 0.0, 7.5), lens=38.0)


build()
