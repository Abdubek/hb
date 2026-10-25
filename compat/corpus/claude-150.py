"""claude-150 - Modular pedestrian bridge with triangular trusses and covered entry portals.

Six 8 m modules of triangular Warren truss (paired bottom chords, single top chord,
diagonals, cross beams and bottom bracing), a deck with parapet infill and handrails,
two river/road piers, and covered slatted entry portals with stairs at both ends.
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
    bg.inputs[0].default_value = (0.33, 0.45, 0.62, 1.0)
    bg.inputs[1].default_value = 1.3
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


def tube_bm(bm, p1, p2, radius, segments=8):
    p1 = Vector(p1)
    p2 = Vector(p2)
    d = p2 - p1
    length = d.length
    if length < 1e-6:
        return
    quat = d.to_track_quat('Z', 'Y')
    m = Matrix.Translation(p1 + d * 0.5) @ quat.to_matrix().to_4x4()
    bmesh.ops.create_cone(bm, cap_ends=True, cap_tris=False, segments=segments,
                          radius1=radius, radius2=radius, depth=length, matrix=m)


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


def add_sun(rotation, energy=4.0, color=(1.0, 0.95, 0.87)):
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
MODULE = 8.0
N_MOD = 6
HALF = MODULE * N_MOD * 0.5      # 24 m each side of centre
DECK_Z = 5.6                     # top of bottom chords
CHORD_Y = 1.75
TRUSS_H = 3.4
TOP_Z = DECK_Z + TRUSS_H
PORTAL_IN = HALF + 0.5
PORTAL_OUT = HALF + 5.0
STAIR_STEPS = 28
STEP_RISE = 0.2
STEP_RUN = 0.36


def build():
    reset_scene()

    m_steel = new_mat("TrussSteel", (0.72, 0.30, 0.22), rough=0.4, metal=0.85)
    m_grey = new_mat("GreySteel", (0.55, 0.57, 0.59), rough=0.4, metal=0.9)
    m_mesh = new_mat("ParapetMesh", (0.45, 0.47, 0.49), rough=0.55, metal=0.7, alpha=0.55)
    m_deck = new_mat("DeckSurface", (0.30, 0.30, 0.31), rough=0.85)
    m_concrete = new_mat("Concrete", (0.68, 0.67, 0.64), rough=0.8)
    m_timber = new_mat("PortalTimber", (0.46, 0.31, 0.17), rough=0.6)
    m_roof = new_mat("PortalRoof", (0.20, 0.22, 0.24), rough=0.35, metal=0.8)
    m_grass = new_mat("Grass", (0.17, 0.31, 0.12), rough=0.95)
    m_asphalt = new_mat("Asphalt", (0.08, 0.08, 0.09), rough=0.93)
    m_paint = new_mat("RoadPaint", (0.88, 0.87, 0.82), rough=0.7)
    m_light = new_mat("Luminaire", (0.95, 0.95, 0.9), rough=0.4,
                      emit=(1.0, 0.95, 0.85), emit_str=9.0)

    # ---- ground, road ---------------------------------------------------------
    bm = bmesh.new()
    box_bm(bm, (0.0, 0.0, -0.5), (300.0, 300.0, 1.0))
    obj_from_bm("Ground", bm, m_grass)

    bm = bmesh.new()
    box_bm(bm, (0.0, 0.0, 0.03), (14.0, 220.0, 0.12))
    obj_from_bm("Road", bm, m_asphalt)

    bm = bmesh.new()
    for i in range(-24, 25):
        box_bm(bm, (0.0, i * 4.5, 0.10), (0.18, 2.4, 0.04))
    for x in (-6.6, 6.6):
        box_bm(bm, (x, 0.0, 0.10), (0.16, 220.0, 0.04))
    obj_from_bm("RoadMarkings", bm, m_paint)

    # ---- truss ---------------------------------------------------------------
    bottom_x = [-HALF + i * MODULE for i in range(N_MOD + 1)]
    top_x = [-HALF + MODULE * 0.5 + i * MODULE for i in range(N_MOD)]

    bm = bmesh.new()
    # bottom chords
    for y in (-CHORD_Y, CHORD_Y):
        for i in range(N_MOD):
            tube_bm(bm, (bottom_x[i], y, DECK_Z), (bottom_x[i + 1], y, DECK_Z), 0.15, 10)
    # top chord (with end rakes down to the abutment nodes)
    for i in range(len(top_x) - 1):
        tube_bm(bm, (top_x[i], 0.0, TOP_Z), (top_x[i + 1], 0.0, TOP_Z), 0.17, 10)
    # diagonals - warren pattern on both inclined faces
    for tx in top_x:
        for y in (-CHORD_Y, CHORD_Y):
            tube_bm(bm, (tx - MODULE * 0.5, y, DECK_Z), (tx, 0.0, TOP_Z), 0.09, 8)
            tube_bm(bm, (tx + MODULE * 0.5, y, DECK_Z), (tx, 0.0, TOP_Z), 0.09, 8)
    # end rakes
    for y in (-CHORD_Y, CHORD_Y):
        tube_bm(bm, (-HALF, y, DECK_Z), (top_x[0], 0.0, TOP_Z), 0.11, 8)
        tube_bm(bm, (HALF, y, DECK_Z), (top_x[-1], 0.0, TOP_Z), 0.11, 8)
    # cross beams at every bottom node
    for bx in bottom_x:
        tube_bm(bm, (bx, -CHORD_Y, DECK_Z), (bx, CHORD_Y, DECK_Z), 0.12, 8)
    # intermediate deck beams (module midpoints)
    for tx in top_x:
        tube_bm(bm, (tx, -CHORD_Y, DECK_Z), (tx, CHORD_Y, DECK_Z), 0.09, 8)
    # bottom lateral X bracing
    zb = DECK_Z - 0.16
    for i in range(N_MOD):
        a, b = bottom_x[i], bottom_x[i + 1]
        tube_bm(bm, (a, -CHORD_Y, zb), (b, CHORD_Y, zb), 0.06, 6)
        tube_bm(bm, (a, CHORD_Y, zb), (b, -CHORD_Y, zb), 0.06, 6)
    obj_from_bm("Truss", bm, m_steel)

    # ---- deck and parapet -----------------------------------------------------
    bm = bmesh.new()
    box_bm(bm, (0.0, 0.0, DECK_Z + 0.19), (HALF * 2.0 + 1.0, 3.4, 0.18))
    for y in (-1.68, 1.68):
        box_bm(bm, (0.0, y, DECK_Z + 0.36), (HALF * 2.0 + 1.0, 0.16, 0.16))
    obj_from_bm("Deck", bm, m_deck)

    bm = bmesh.new()
    for i in range(N_MOD):
        cx = (bottom_x[i] + bottom_x[i + 1]) * 0.5
        for y in (-CHORD_Y, CHORD_Y):
            box_bm(bm, (cx, y, DECK_Z + 0.85), (MODULE - 0.5, 0.03, 0.95))
    obj_from_bm("ParapetInfill", bm, m_mesh)

    bm = bmesh.new()
    for y in (-CHORD_Y, CHORD_Y):
        tube_bm(bm, (-HALF - 0.4, y, DECK_Z + 1.15), (HALF + 0.4, y, DECK_Z + 1.15),
                0.045, 8)
        for bx in bottom_x:
            tube_bm(bm, (bx, y, DECK_Z + 0.30), (bx, y, DECK_Z + 1.15), 0.04, 6)
    obj_from_bm("Handrails", bm, m_grey)

    bm = bmesh.new()
    for tx in top_x:
        box_bm(bm, (tx, 0.0, TOP_Z - 0.30), (0.9, 0.22, 0.10))
    obj_from_bm("DeckLighting", bm, m_light)

    # ---- piers -----------------------------------------------------------------
    bm = bmesh.new()
    for px in (-11.0, 11.0):
        box_bm(bm, (px, 0.0, (DECK_Z - 0.75) * 0.5), (2.6, 3.4, DECK_Z - 0.75))
        box_bm(bm, (px, 0.0, DECK_Z - 0.55), (4.6, 4.4, 0.7))
        box_bm(bm, (px, 0.0, 0.25), (3.6, 4.4, 0.5))
    obj_from_bm("Piers", bm, m_concrete)

    bm = bmesh.new()
    for px in (-11.0, 11.0):
        for y in (-CHORD_Y, CHORD_Y):
            box_bm(bm, (px, y, DECK_Z - 0.12), (0.7, 0.7, 0.26))
    obj_from_bm("Bearings", bm, m_grey)

    # ---- abutments, portals, stairs ---------------------------------------------
    bm_conc = bmesh.new()
    bm_col = bmesh.new()
    bm_slat = bmesh.new()
    bm_roof = bmesh.new()
    bm_rail = bmesh.new()

    for s in (1.0, -1.0):
        x_in = s * PORTAL_IN
        x_out = s * PORTAL_OUT
        cx = (x_in + x_out) * 0.5

        # abutment block and portal floor
        box_bm(bm_conc, (cx, 0.0, (DECK_Z - 0.2) * 0.5), (5.4, 5.2, DECK_Z - 0.2))
        box_bm(bm_conc, (cx, 0.0, DECK_Z + 0.12), (5.6, 6.0, 0.36))

        # four corner columns
        for dx in (x_in, x_out):
            for dy in (-2.8, 2.8):
                box_bm(bm_col, (dx, dy, DECK_Z + 2.35), (0.35, 0.35, 4.2))
        # header beams
        for dy in (-2.8, 2.8):
            box_bm(bm_col, (cx, dy, DECK_Z + 4.28), (5.0, 0.30, 0.45))
        box_bm(bm_col, (x_out, 0.0, DECK_Z + 4.28), (0.30, 6.0, 0.45))
        box_bm(bm_col, (x_in, 0.0, DECK_Z + 4.28), (0.30, 6.0, 0.45))

        # slatted side screens
        n = 13
        for i in range(n):
            t = (i + 0.5) / n
            sx = x_in + (x_out - x_in) * t
            for dy in (-2.86, 2.86):
                box_bm(bm_slat, (sx, dy, DECK_Z + 2.4), (0.16, 0.06, 3.6))
        # outer end wall with a central opening
        for i in range(8):
            oy = -2.7 + i * 0.72
            if abs(oy) < 1.25:
                continue
            box_bm(bm_slat, (x_out + s * 0.10, oy, DECK_Z + 2.4), (0.06, 0.30, 3.6))
        box_bm(bm_slat, (x_out + s * 0.10, 0.0, DECK_Z + 4.05), (0.06, 2.6, 0.35))

        # pitched roof slab with overhang
        box_bm(bm_roof, (cx, 0.0, DECK_Z + 4.75), (7.0, 7.2, 0.30),
               (0.0, -s * math.radians(5.0), 0.0))
        box_bm(bm_roof, (cx, 0.0, DECK_Z + 4.52), (6.6, 6.8, 0.14),
               (0.0, -s * math.radians(5.0), 0.0))

        # stairs down to grade
        for k in range(STAIR_STEPS):
            zt = DECK_Z - STEP_RISE * (k + 1)
            sx = x_out + s * (0.4 + STEP_RUN * k)
            box_bm(bm_conc, (sx, 0.0, zt - STEP_RISE * 0.5), (STEP_RUN, 2.8, STEP_RISE))
            box_bm(bm_conc, (sx, 0.0, zt * 0.5 - 0.1), (STEP_RUN, 2.8, max(0.1, zt - 0.2)))
        landing_x = x_out + s * (0.4 + STEP_RUN * STAIR_STEPS + 1.6)
        box_bm(bm_conc, (landing_x, 0.0, 0.08), (3.6, 3.4, 0.3))

        # stair railings
        for side in (-1.5, 1.5):
            p1 = (x_out + s * 0.4, side, DECK_Z + 1.0)
            p2 = (x_out + s * (0.4 + STEP_RUN * STAIR_STEPS), side,
                  DECK_Z - STEP_RISE * STAIR_STEPS + 1.0)
            tube_bm(bm_rail, p1, p2, 0.045, 8)
            tube_bm(bm_rail, (p1[0], side, p1[2] - 0.45), (p2[0], side, p2[2] - 0.45),
                    0.03, 6)
            for k in range(0, STAIR_STEPS + 1, 4):
                px = x_out + s * (0.4 + STEP_RUN * k)
                pz = DECK_Z - STEP_RISE * k
                tube_bm(bm_rail, (px, side, pz), (px, side, pz + 1.0), 0.035, 6)

        # portal handrails continuing the bridge line
        for y in (-CHORD_Y, CHORD_Y):
            tube_bm(bm_rail, (x_in, y, DECK_Z + 1.15), (x_out, y, DECK_Z + 1.15),
                    0.045, 8)

    obj_from_bm("AbutmentsAndStairs", bm_conc, m_concrete)
    obj_from_bm("PortalFrames", bm_col, m_grey)
    obj_from_bm("PortalSlats", bm_slat, m_timber)
    obj_from_bm("PortalRoofs", bm_roof, m_roof)
    obj_from_bm("StairRailings", bm_rail, m_grey)

    # ---- lighting & camera -------------------------------------------------------
    add_sun((math.radians(54.0), math.radians(6.0), math.radians(-46.0)), energy=4.4)
    add_area((26.0, -40.0, 30.0), 40.0, 14000.0,
             rotation=(math.radians(55.0), 0.0, math.radians(34.0)),
             color=(0.76, 0.84, 1.0))
    add_camera((36.0, -38.0, 14.0), (0.0, 0.0, 6.5), lens=38.0)


build()
