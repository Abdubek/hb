"""claude-148 - Compact airport control tower with glazed cab and service platforms.

Base operations block, tapered ribbed shaft, two exterior service platforms with
guardrails and a caged access ladder, an outward-leaning glazed cab with mullions,
roof with antenna mast, radar and obstruction lights, apron with markings.
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
    bg.inputs[0].default_value = (0.26, 0.38, 0.56, 1.0)
    bg.inputs[1].default_value = 1.1
    return scn


def link(obj):
    bpy.context.scene.collection.objects.link(obj)
    return obj


def new_mat(name, color, rough=0.6, metal=0.0, alpha=1.0, transmission=0.0,
            emit=None, emit_str=0.0):
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
    s("Transmission Weight", transmission)
    s("IOR", 1.45)
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


def prism_bm(bm, pts, z, height):
    verts = [bm.verts.new((p[0], p[1], z)) for p in pts]
    face = bm.faces.new(verts)
    res = bmesh.ops.extrude_face_region(bm, geom=[face])
    new_verts = [e for e in res["geom"] if isinstance(e, bmesh.types.BMVert)]
    bmesh.ops.translate(bm, verts=new_verts, vec=(0.0, 0.0, height))


def circle_pts(radius, segments, phase=0.0):
    return [(radius * math.cos(phase + math.tau * i / segments),
             radius * math.sin(phase + math.tau * i / segments))
            for i in range(segments)]


def annulus_pts(inner, outer, segments):
    outer_pts = circle_pts(outer, segments)
    inner_pts = list(reversed(circle_pts(inner, segments)))
    # single closed outline: outer loop, bridge, inner loop, bridge back
    return outer_pts + [outer_pts[0]] + [inner_pts[-1]] + inner_pts + [inner_pts[-1]]


def ring_bm(bm, inner, outer, z, height, segments=48):
    """Solid annular ring built as a quad band (robust, fully manifold)."""
    zt = z + height
    ring = []
    for i in range(segments):
        a = math.tau * i / segments
        ca, sa = math.cos(a), math.sin(a)
        ring.append((bm.verts.new((inner * ca, inner * sa, z)),
                     bm.verts.new((outer * ca, outer * sa, z)),
                     bm.verts.new((outer * ca, outer * sa, zt)),
                     bm.verts.new((inner * ca, inner * sa, zt))))
    for i in range(segments):
        a = ring[i]
        b = ring[(i + 1) % segments]
        bm.faces.new((a[0], b[0], b[1], a[1]))   # bottom
        bm.faces.new((a[1], b[1], b[2], a[2]))   # outer wall
        bm.faces.new((a[2], b[2], b[3], a[3]))   # top
        bm.faces.new((a[3], b[3], b[0], a[0]))   # inner wall


def add_camera(location, target, lens=45.0):
    cam_data = bpy.data.cameras.new("Camera")
    cam_data.lens = lens
    cam_data.clip_end = 2000.0
    cam = bpy.data.objects.new("Camera", cam_data)
    link(cam)
    cam.location = location
    cam.rotation_euler = (Vector(target) - Vector(location)).to_track_quat('-Z', 'Y').to_euler()
    bpy.context.scene.camera = cam
    return cam


def add_sun(rotation, energy=4.0, color=(1.0, 0.94, 0.84)):
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
BASE_H = 5.0
SHAFT_TOP = 26.0
R_BOT = 3.4
R_TOP = 2.4
PLAT1_Z = 13.0
CAT_Z = 26.4          # catwalk under the cab
CAB_FLOOR = 26.9
CAB_TOP = 31.2
CAB_R_BOT = 4.2
CAB_R_TOP = 5.4
ROOF_R = 6.0


def shaft_radius(z):
    t = max(0.0, min(1.0, z / SHAFT_TOP))
    return R_BOT + (R_TOP - R_BOT) * t


def build():
    reset_scene()

    m_concrete = new_mat("TowerConcrete", (0.74, 0.73, 0.70), rough=0.7)
    m_accent = new_mat("AccentPanel", (0.30, 0.36, 0.44), rough=0.45, metal=0.3)
    m_steel = new_mat("Steel", (0.78, 0.79, 0.81), rough=0.3, metal=1.0)
    m_dark = new_mat("DarkMetal", (0.16, 0.17, 0.19), rough=0.45, metal=0.8)
    m_glass = new_mat("CabGlass", (0.42, 0.55, 0.62), rough=0.05, metal=0.0,
                      alpha=0.30, transmission=0.85)
    m_grate = new_mat("Grating", (0.42, 0.44, 0.46), rough=0.6, metal=0.7)
    m_apron = new_mat("Apron", (0.29, 0.29, 0.30), rough=0.92)
    m_paint = new_mat("Marking", (0.86, 0.74, 0.16), rough=0.7)
    m_interior = new_mat("CabLight", (0.95, 0.95, 0.9), rough=0.5,
                         emit=(1.0, 0.96, 0.86), emit_str=4.0)
    m_red = new_mat("ObstructionLight", (0.6, 0.03, 0.03), rough=0.4,
                    emit=(1.0, 0.05, 0.05), emit_str=25.0)

    # ---- apron -------------------------------------------------------------
    bm = bmesh.new()
    box_bm(bm, (0.0, 0.0, -0.3), (400.0, 400.0, 0.6))
    obj_from_bm("Apron", bm, m_apron)

    bm = bmesh.new()
    for i in range(-10, 11):
        box_bm(bm, (i * 8.0, -34.0, 0.02), (5.0, 0.30, 0.04))
    box_bm(bm, (0.0, -46.0, 0.02), (160.0, 0.35, 0.04))
    obj_from_bm("ApronMarkings", bm, m_paint)

    # ---- base operations building -------------------------------------------
    bm = bmesh.new()
    box_bm(bm, (0.0, 0.0, BASE_H * 0.5), (18.0, 13.0, BASE_H))
    box_bm(bm, (0.0, 0.0, BASE_H + 0.25), (18.8, 13.8, 0.5))
    box_bm(bm, (-7.0, -7.6, 1.6), (4.2, 2.6, 3.2))          # entry canopy block
    obj_from_bm("BaseBuilding", bm, m_concrete)

    bm = bmesh.new()
    for y in (-6.56, 6.56):
        box_bm(bm, (0.0, y, 3.1), (16.4, 0.12, 1.7))
    for x in (-9.06, 9.06):
        box_bm(bm, (x, 0.0, 3.1), (0.12, 11.4, 1.7))
    obj_from_bm("BaseGlazing", bm, m_glass)

    bm = bmesh.new()
    box_bm(bm, (-7.0, -8.9, 2.9), (4.6, 0.25, 0.35))
    box_bm(bm, (-7.0, -8.0, 1.05), (2.2, 0.12, 2.1))
    obj_from_bm("BaseTrim", bm, m_accent)

    # ---- tapered shaft -------------------------------------------------------
    bm = bmesh.new()
    bmesh.ops.create_cone(bm, cap_ends=True, cap_tris=False, segments=40,
                          radius1=R_BOT, radius2=R_TOP, depth=SHAFT_TOP,
                          matrix=Matrix.Translation((0.0, 0.0, SHAFT_TOP * 0.5)))
    obj_from_bm("Shaft", bm, m_concrete, smooth=True)

    # vertical ribs and narrow stair-light slots
    bm = bmesh.new()
    for i in range(10):
        a = math.tau * i / 10.0
        ca, sa = math.cos(a), math.sin(a)
        z0, z1 = BASE_H - 0.4, SHAFT_TOP - 0.2
        r0 = shaft_radius(z0) + 0.06
        r1 = shaft_radius(z1) + 0.06
        tube_bm(bm, (r0 * ca, r0 * sa, z0), (r1 * ca, r1 * sa, z1), 0.16, 6)
    obj_from_bm("ShaftRibs", bm, m_accent)

    bm = bmesh.new()
    for k in range(9):
        z = BASE_H + 1.4 + k * 2.2
        r = shaft_radius(z) + 0.02
        a = math.radians(35.0)
        box_bm(bm, (r * math.cos(a), r * math.sin(a), z), (0.12, 0.55, 1.0),
               (0.0, 0.0, a))
    obj_from_bm("ShaftSlots", bm, m_glass)

    # ---- service platforms ---------------------------------------------------
    bm_deck = bmesh.new()
    ring_bm(bm_deck, shaft_radius(PLAT1_Z) - 0.05, 4.9, PLAT1_Z, 0.22, segments=44)
    ring_bm(bm_deck, shaft_radius(CAT_Z) - 0.05, 6.1, CAT_Z, 0.24, segments=48)
    obj_from_bm("ServicePlatforms", bm_deck, m_grate)

    bm_rail = bmesh.new()

    def guardrail(radius, z, posts=24, height=1.10):
        pts = [(radius * math.cos(math.tau * i / posts),
                radius * math.sin(math.tau * i / posts)) for i in range(posts)]
        for (px, py) in pts:
            tube_bm(bm_rail, (px, py, z), (px, py, z + height), 0.035, 6)
        for lvl in (height, height * 0.55):
            for i in range(posts):
                a = pts[i]
                b = pts[(i + 1) % posts]
                tube_bm(bm_rail, (a[0], a[1], z + lvl), (b[0], b[1], z + lvl), 0.028, 6)

    guardrail(4.78, PLAT1_Z + 0.22)
    guardrail(5.98, CAT_Z + 0.24, posts=28)
    # platform support brackets
    for z, r_out in ((PLAT1_Z, 4.9), (CAT_Z, 6.1)):
        for i in range(12):
            a = math.tau * i / 12.0
            ca, sa = math.cos(a), math.sin(a)
            r_in = shaft_radius(z - 1.6)
            tube_bm(bm_rail, (r_in * ca, r_in * sa, z - 1.6),
                    ((r_out - 0.2) * ca, (r_out - 0.2) * sa, z), 0.07, 6)
    obj_from_bm("PlatformRails", bm_rail, m_steel)

    # ---- caged access ladder -------------------------------------------------
    bm = bmesh.new()
    a = math.pi
    ca, sa = math.cos(a), math.sin(a)
    z = BASE_H + 0.4
    while z < CAT_Z - 0.4:
        r = shaft_radius(z) + 0.30
        tube_bm(bm, ((r) * ca - 0.25 * sa, (r) * sa + 0.25 * ca, z),
                ((r) * ca + 0.25 * sa, (r) * sa - 0.25 * ca, z), 0.022, 6)
        z += 0.34
    for off in (-0.25, 0.25):
        pts = []
        zz = BASE_H + 0.3
        while zz <= CAT_Z:
            r = shaft_radius(zz) + 0.30
            pts.append((r * ca - off * sa, r * sa + off * ca, zz))
            zz += 1.0
        for i in range(len(pts) - 1):
            tube_bm(bm, pts[i], pts[i + 1], 0.035, 6)
    # cage hoops
    zz = BASE_H + 1.2
    while zz < CAT_Z - 0.6:
        r = shaft_radius(zz) + 0.30
        cx, cy = r * ca, r * sa
        prev = None
        for i in range(11):
            ang = math.radians(-100.0 + 200.0 * i / 10.0) + a
            p = (cx + 0.75 * math.cos(ang), cy + 0.75 * math.sin(ang), zz)
            if prev:
                tube_bm(bm, prev, p, 0.022, 5)
            prev = p
        zz += 1.6
    obj_from_bm("AccessLadder", bm, m_steel)

    # ---- cab -----------------------------------------------------------------
    bm = bmesh.new()
    prism_bm(bm, circle_pts(4.55, 44), CAB_FLOOR - 0.35, 0.35)
    obj_from_bm("CabFloor", bm, m_concrete)

    bm = bmesh.new()
    ring_bm(bm, 4.05, 4.62, CAB_FLOOR - 0.02, 0.32, segments=44)
    ring_bm(bm, CAB_R_TOP - 0.55, CAB_R_TOP + 0.12, CAB_TOP - 0.34, 0.34, segments=44)
    obj_from_bm("CabRingBeams", bm, m_accent)

    # leaning glazing shell
    bm = bmesh.new()
    bmesh.ops.create_cone(bm, cap_ends=False, cap_tris=False, segments=44,
                          radius1=CAB_R_BOT, radius2=CAB_R_TOP,
                          depth=CAB_TOP - CAB_FLOOR,
                          matrix=Matrix.Translation((0.0, 0.0,
                                                     (CAB_FLOOR + CAB_TOP) * 0.5)))
    obj_from_bm("CabGlazing", bm, m_glass, smooth=True)

    bm = bmesh.new()
    n_mull = 22
    for i in range(n_mull):
        ang = math.tau * i / n_mull
        ca2, sa2 = math.cos(ang), math.sin(ang)
        tube_bm(bm, (CAB_R_BOT * ca2, CAB_R_BOT * sa2, CAB_FLOOR + 0.05),
                (CAB_R_TOP * ca2, CAB_R_TOP * sa2, CAB_TOP - 0.05), 0.055, 6)
    obj_from_bm("CabMullions", bm, m_dark)

    # interior floor, console ring and ceiling light plane
    bm = bmesh.new()
    prism_bm(bm, circle_pts(4.2, 40), CAB_FLOOR, 0.06)
    obj_from_bm("CabInteriorFloor", bm, m_dark)

    bm = bmesh.new()
    ring_bm(bm, 2.7, 3.7, CAB_FLOOR + 0.06, 0.95, segments=36)
    obj_from_bm("Consoles", bm, m_dark)

    bm = bmesh.new()
    prism_bm(bm, circle_pts(4.1, 40), CAB_TOP - 0.42, 0.06)
    obj_from_bm("CabCeilingLight", bm, m_interior)

    # ---- roof ----------------------------------------------------------------
    bm = bmesh.new()
    prism_bm(bm, circle_pts(ROOF_R, 48), CAB_TOP, 0.5)
    prism_bm(bm, circle_pts(ROOF_R + 0.32, 48), CAB_TOP + 0.12, 0.18)
    obj_from_bm("Roof", bm, m_concrete)

    bm = bmesh.new()
    ring_bm(bm, ROOF_R - 0.55, ROOF_R - 0.35, CAB_TOP + 0.5, 0.55, segments=44)
    obj_from_bm("RoofParapet", bm, m_accent)

    bm = bmesh.new()
    # antenna mast with cross elements
    z_base = CAB_TOP + 0.5
    tube_bm(bm, (0.0, 0.0, z_base), (0.0, 0.0, z_base + 6.2), 0.09, 8)
    for k in range(4):
        zz = z_base + 2.0 + k * 1.0
        tube_bm(bm, (-0.8, 0.0, zz), (0.8, 0.0, zz), 0.035, 6)
        tube_bm(bm, (0.0, -0.8, zz + 0.5), (0.0, 0.8, zz + 0.5), 0.035, 6)
    # radar assembly
    tube_bm(bm, (2.6, 0.0, z_base), (2.6, 0.0, z_base + 0.9), 0.28, 12)
    box_bm(bm, (2.6, 0.0, z_base + 1.35), (2.9, 0.16, 0.85), (0.0, 0.0, math.radians(25.0)))
    # small comms dishes
    for ang_deg in (120.0, 240.0):
        ang = math.radians(ang_deg)
        px, py = 4.6 * math.cos(ang), 4.6 * math.sin(ang)
        tube_bm(bm, (px, py, z_base), (px, py, z_base + 1.4), 0.07, 8)
        bmesh.ops.create_icosphere(bm, subdivisions=2, radius=0.42,
                                   matrix=Matrix.Translation((px, py, z_base + 1.65)))
    obj_from_bm("RoofEquipment", bm, m_steel, smooth=False)

    bm = bmesh.new()
    for i in range(4):
        ang = math.tau * i / 4.0 + math.radians(45.0)
        bmesh.ops.create_icosphere(
            bm, subdivisions=2, radius=0.16,
            matrix=Matrix.Translation((5.6 * math.cos(ang), 5.6 * math.sin(ang),
                                       CAB_TOP + 0.75)))
    bmesh.ops.create_icosphere(bm, subdivisions=2, radius=0.14,
                               matrix=Matrix.Translation((0.0, 0.0, z_base + 6.35)))
    obj_from_bm("ObstructionLights", bm, m_red, smooth=True)

    # ---- lighting & camera -----------------------------------------------------
    add_sun((math.radians(48.0), math.radians(8.0), math.radians(-40.0)), energy=4.0)
    add_area((-24.0, -30.0, 28.0), 36.0, 12000.0,
             rotation=(math.radians(56.0), 0.0, math.radians(-38.0)),
             color=(0.72, 0.82, 1.0))
    add_camera((36.0, -34.0, 21.0), (0.0, 0.0, 19.0), lens=42.0)


build()
