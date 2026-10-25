"""claude-146 - Landscaped amphitheater with concentric terraces and side access stairs.

Builds the scene headlessly from factory startup: stage disc, stepped concrete
terrace rings, curved timber benches, radial stair aisles with handrails,
planted earth berm with trees, lawn, lighting and camera.
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
    bg.inputs[0].default_value = (0.32, 0.45, 0.62, 1.0)
    bg.inputs[1].default_value = 1.3
    return scn


def link(obj):
    bpy.context.scene.collection.objects.link(obj)
    return obj


def new_mat(name, color, rough=0.6, metal=0.0, emit=None, emit_str=0.0):
    mat = bpy.data.materials.new(name)
    mat.use_nodes = True
    bsdf = mat.node_tree.nodes["Principled BSDF"]

    def s(key, value):
        if key in bsdf.inputs:
            bsdf.inputs[key].default_value = value

    s("Base Color", (color[0], color[1], color[2], 1.0))
    s("Roughness", rough)
    s("Metallic", metal)
    if emit is not None:
        s("Emission Color", (emit[0], emit[1], emit[2], 1.0))
        s("Emission Strength", emit_str)
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


def tube_bm(bm, p1, p2, radius, segments=10):
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


def prism_bm(bm, pts, z, height):
    """Extrude a closed 2D outline into a solid prism inside an existing bmesh."""
    verts = [bm.verts.new((p[0], p[1], z)) for p in pts]
    face = bm.faces.new(verts)
    res = bmesh.ops.extrude_face_region(bm, geom=[face])
    new_verts = [e for e in res["geom"] if isinstance(e, bmesh.types.BMVert)]
    bmesh.ops.translate(bm, verts=new_verts, vec=(0.0, 0.0, height))


def arc_pts(radius, a0, a1, segments):
    return [(radius * math.cos(a0 + (a1 - a0) * i / segments),
             radius * math.sin(a0 + (a1 - a0) * i / segments))
            for i in range(segments + 1)]


def ring_sector(inner, outer, a0, a1, segments):
    pts = arc_pts(outer, a0, a1, segments)
    pts += list(reversed(arc_pts(inner, a0, a1, segments)))
    return pts


def add_camera(location, target, lens=35.0):
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
    data.angle = math.radians(1.8)
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
R_STAGE = 8.0
DEPTH = 2.0
RISE = 0.6
N_TERRACE = 9
A0 = math.radians(-115.0)
A1 = math.radians(115.0)
SEGS = 56
R_OUT = R_STAGE + N_TERRACE * DEPTH
BASE_Z = -0.8
AISLES = [math.radians(a) for a in (-95.0, -38.0, 38.0, 95.0)]
HW = math.radians(4.5)


def build():
    reset_scene()

    m_concrete = new_mat("Concrete", (0.68, 0.66, 0.62), rough=0.78)
    m_stone = new_mat("StageStone", (0.55, 0.52, 0.47), rough=0.6)
    m_wood = new_mat("BenchWood", (0.42, 0.26, 0.13), rough=0.55)
    m_steel = new_mat("Handrail", (0.72, 0.74, 0.76), rough=0.35, metal=1.0)
    m_grass = new_mat("Grass", (0.16, 0.32, 0.11), rough=0.95)
    m_hedge = new_mat("Hedge", (0.12, 0.27, 0.09), rough=0.9)
    m_bark = new_mat("Bark", (0.21, 0.15, 0.10), rough=0.85)
    m_leaf = new_mat("Foliage", (0.14, 0.35, 0.12), rough=0.8)
    m_lamp = new_mat("LampGlow", (0.9, 0.85, 0.7), rough=0.3,
                     emit=(1.0, 0.92, 0.75), emit_str=12.0)

    # ---- lawn -------------------------------------------------------------
    bm = bmesh.new()
    box_bm(bm, (0.0, 0.0, BASE_Z - 0.6), (260.0, 260.0, 1.2))
    obj_from_bm("Lawn", bm, m_grass)

    # ---- stage ------------------------------------------------------------
    bm = bmesh.new()
    prism_bm(bm, arc_pts(R_STAGE, 0.0, math.tau, 72)[:-1], BASE_Z, 0.95)
    prism_bm(bm, arc_pts(R_STAGE - 2.6, 0.0, math.tau, 60)[:-1], BASE_Z + 0.95, 0.06)
    obj_from_bm("Stage", bm, m_stone)

    # ---- stepped terrace rings -------------------------------------------
    bm = bmesh.new()
    for i in range(N_TERRACE):
        inner = R_STAGE + i * DEPTH
        outer = inner + DEPTH
        top = (i + 1) * RISE
        prism_bm(bm, ring_sector(inner, outer, A0, A1, SEGS), BASE_Z, top - BASE_Z)
    # bookend walls closing the two radial ends of the bowl
    for end_angle, sign in ((A0, 1.0), (A1, -1.0)):
        a_a = end_angle
        a_b = end_angle + sign * math.radians(2.2)
        lo, hi = (a_a, a_b) if a_b > a_a else (a_b, a_a)
        prism_bm(bm, ring_sector(R_STAGE, R_OUT, lo, hi, 8), BASE_Z,
                 N_TERRACE * RISE + 0.9 - BASE_Z)
    obj_from_bm("Terraces", bm, m_concrete)

    # ---- bench segments between aisles ------------------------------------
    spans = []
    prev = A0 + math.radians(3.0)
    for a in AISLES:
        spans.append((prev, a - HW))
        prev = a + HW
    spans.append((prev, A1 - math.radians(3.0)))

    bm = bmesh.new()
    for i in range(N_TERRACE):
        inner = R_STAGE + i * DEPTH
        top = (i + 1) * RISE
        for (s0, s1) in spans:
            if s1 - s0 < math.radians(4.0):
                continue
            n = max(3, int(math.degrees(s1 - s0) / 4.0))
            # seat plank
            prism_bm(bm, ring_sector(inner + 0.62, inner + 1.28, s0, s1, n), top, 0.06)
            # two supporting sleepers under the plank
            prism_bm(bm, ring_sector(inner + 0.66, inner + 1.24, s0, s0 + math.radians(2.0), 2),
                     top, -0.0)
    obj_from_bm("Benches", bm, m_wood)

    bm = bmesh.new()
    for i in range(N_TERRACE):
        inner = R_STAGE + i * DEPTH
        top = (i + 1) * RISE
        for (s0, s1) in spans:
            if s1 - s0 < math.radians(4.0):
                continue
            step = math.radians(2.4)
            a = s0 + math.radians(1.0)
            while a < s1 - math.radians(1.0):
                prism_bm(bm, ring_sector(inner + 0.70, inner + 1.20, a, a + step, 2),
                         top - 0.34, 0.34)
                a += math.radians(24.0)
    obj_from_bm("BenchSupports", bm, m_concrete)

    # ---- radial access stairs --------------------------------------------
    bm = bmesh.new()
    for a in AISLES:
        for i in range(N_TERRACE):
            inner = R_STAGE + i * DEPTH
            prism_bm(bm, ring_sector(inner, inner + DEPTH * 0.5, a - HW, a + HW, 4),
                     i * RISE, RISE * 0.5 + 0.02)
    obj_from_bm("AisleSteps", bm, m_concrete)

    # handrails flanking every aisle
    bm = bmesh.new()
    for a in AISLES:
        for off in (-HW, HW):
            ang = a + off
            cx, cy = math.cos(ang), math.sin(ang)
            r0, r1 = R_STAGE + 0.2, R_OUT - 0.2
            z0, z1 = 0.95, N_TERRACE * RISE + 0.95
            tube_bm(bm, (r0 * cx, r0 * cy, z0), (r1 * cx, r1 * cy, z1), 0.045, 8)
            for i in range(0, N_TERRACE + 1, 2):
                r = R_STAGE + i * DEPTH + 0.4
                if r > r1:
                    continue
                zt = i * RISE + 0.95
                tube_bm(bm, (r * cx, r * cy, i * RISE), (r * cx, r * cy, zt), 0.035, 6)
    obj_from_bm("Handrails", bm, m_steel)

    # ---- landscaped berm --------------------------------------------------
    berm_top = N_TERRACE * RISE + 1.3
    bm = bmesh.new()
    prism_bm(bm, ring_sector(R_OUT, R_OUT + 7.0, A0 - math.radians(14.0),
                             A1 + math.radians(14.0), SEGS + 12), BASE_Z, berm_top - BASE_Z)
    obj_from_bm("Berm", bm, m_grass)

    bm = bmesh.new()
    for (s0, s1) in spans:
        prism_bm(bm, ring_sector(R_OUT + 0.4, R_OUT + 1.3, s0, s1,
                                 max(3, int(math.degrees(s1 - s0) / 5.0))),
                 berm_top, 1.0)
    obj_from_bm("Hedge", bm, m_hedge)

    # ---- trees ------------------------------------------------------------
    bm_trunk = bmesh.new()
    bm_leaf = bmesh.new()

    def tree(x, y, z, s):
        tube_bm(bm_trunk, (x, y, z), (x, y, z + 2.8 * s), 0.17 * s, 8)
        for dz, r in ((3.1, 1.55), (4.4, 1.15), (2.4, 1.2)):
            bmesh.ops.create_icosphere(bm_leaf, subdivisions=2, radius=r * s,
                                       matrix=Matrix.Translation((x, y, z + dz * s)))

    ring_r = R_OUT + 4.2
    count = 13
    for i in range(count):
        ang = (A0 - math.radians(10.0)) + (A1 - A0 + math.radians(20.0)) * i / (count - 1)
        s = 0.85 + 0.35 * ((i * 7) % 5) / 4.0
        tree(ring_r * math.cos(ang), ring_r * math.sin(ang), berm_top - 0.2, s)
    for ang_deg, rad, s in ((150.0, 20.0, 1.15), (-150.0, 22.0, 0.95),
                            (172.0, 30.0, 1.3), (-168.0, 34.0, 1.05)):
        ang = math.radians(ang_deg)
        tree(rad * math.cos(ang), rad * math.sin(ang), BASE_Z + 0.4, s)
    obj_from_bm("TreeTrunks", bm_trunk, m_bark)
    obj_from_bm("TreeFoliage", bm_leaf, m_leaf, smooth=True)

    # ---- aisle lamp posts -------------------------------------------------
    bm_post = bmesh.new()
    bm_glow = bmesh.new()
    for a in AISLES:
        cx, cy = math.cos(a), math.sin(a)
        for r, zb in ((R_STAGE + 3.0, RISE * 1.5), (R_OUT - 1.0, N_TERRACE * RISE)):
            tube_bm(bm_post, (r * cx, r * cy, zb), (r * cx, r * cy, zb + 3.4), 0.075, 8)
            bmesh.ops.create_icosphere(
                bm_glow, subdivisions=2, radius=0.24,
                matrix=Matrix.Translation((r * cx, r * cy, zb + 3.55)))
    obj_from_bm("LampPosts", bm_post, m_steel)
    obj_from_bm("LampGlobes", bm_glow, m_lamp, smooth=True)

    # ---- lighting & camera -------------------------------------------------
    add_sun((math.radians(52.0), math.radians(6.0), math.radians(38.0)), energy=4.2)
    add_area((-26.0, -26.0, 26.0), 40.0, 9000.0,
             rotation=(math.radians(50.0), 0.0, math.radians(-45.0)),
             color=(0.75, 0.83, 1.0))
    add_camera((-50.0, -30.0, 25.0), (3.0, 0.0, 3.5), lens=35.0)


build()
