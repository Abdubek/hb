"""claude-118 : A spiral parking ramp with guard rails and central support columns.

Helical two-and-a-half turn ramp deck with cross-fall, solidified into a slab,
wrapped by inner/outer guard rails (posts + twin tube rails), carried on a ring
of cast columns and a central circulation core, all on a ground slab.
"""

import bpy
import bmesh
import math
from mathutils import Vector, Matrix, Euler

bpy.ops.wm.read_factory_settings(use_empty=True)
scn = bpy.context.scene
scn.unit_settings.system = 'METRIC'

# --- ramp parameters --------------------------------------------------------
R_IN = 9.0
R_OUT = 16.0
TURNS = 2.5
RISE = 3.4                      # vertical rise per full turn
SEG_PER_TURN = 56
N_STEP = int(TURNS * SEG_PER_TURN)
N_RAD = 6
THETA_MAX = TURNS * 2.0 * math.pi
DECK_T = 0.38


# ----------------------------------------------------------------------------
# helpers
# ----------------------------------------------------------------------------
def make_material(name, colour, rough=0.6, metal=0.0):
    mat = bpy.data.materials.new(name)
    mat.use_nodes = True
    bsdf = mat.node_tree.nodes["Principled BSDF"]
    bsdf.inputs["Base Color"].default_value = (colour[0], colour[1], colour[2], 1.0)
    bsdf.inputs["Roughness"].default_value = rough
    bsdf.inputs["Metallic"].default_value = metal
    return mat


def object_from_bmesh(name, bm, materials):
    me = bpy.data.meshes.new(name)
    bm.to_mesh(me)
    bm.free()
    for m in materials:
        me.materials.append(m)
    me.validate()
    ob = bpy.data.objects.new(name, me)
    scn.collection.objects.link(ob)
    return ob


def add_tube(bm, p0, p1, radius, segments=12):
    p0 = Vector(p0)
    p1 = Vector(p1)
    d = p1 - p0
    length = d.length
    if length < 1e-6:
        return
    rot = d.to_track_quat('Z', 'Y').to_matrix().to_4x4()
    mtx = Matrix.Translation((p0 + p1) * 0.5) @ rot
    bmesh.ops.create_cone(bm, cap_ends=True, cap_tris=False, segments=segments,
                          radius1=radius, radius2=radius, depth=length, matrix=mtx)


def add_box(bm, loc, size, rot_z=0.0):
    mtx = (Matrix.Translation(Vector(loc)) @
           Matrix.Rotation(rot_z, 4, 'Z') @
           Matrix.Diagonal(Vector((size[0], size[1], size[2], 1.0))))
    bmesh.ops.create_cube(bm, size=1.0, matrix=mtx)


def poly_curve(name, pts, depth, material, resolution=3, closed=False):
    cu = bpy.data.curves.new(name, 'CURVE')
    cu.dimensions = '3D'
    cu.resolution_u = 2
    cu.bevel_depth = depth
    cu.bevel_resolution = resolution
    cu.fill_mode = 'FULL'
    sp = cu.splines.new('POLY')
    sp.points.add(len(pts) - 1)
    for i, p in enumerate(pts):
        sp.points[i].co = (p[0], p[1], p[2], 1.0)
    sp.use_cyclic_u = closed
    ob = bpy.data.objects.new(name, cu)
    cu.materials.append(material)
    scn.collection.objects.link(ob)
    return ob


def look_at(ob, target):
    d = Vector(target) - ob.location
    ob.rotation_euler = d.to_track_quat('-Z', 'Y').to_euler()


# ----------------------------------------------------------------------------
# materials
# ----------------------------------------------------------------------------
MAT_DECK = make_material("Deck_Concrete", (0.60, 0.59, 0.57), 0.80)
MAT_COL = make_material("Column_Concrete", (0.66, 0.65, 0.62), 0.75)
MAT_RAIL = make_material("Guard_Rail", (0.72, 0.74, 0.76), 0.32, 1.0)
MAT_POST = make_material("Rail_Post", (0.32, 0.34, 0.36), 0.45, 0.9)
MAT_KERB = make_material("Kerb_Paint", (0.82, 0.72, 0.14), 0.65)
MAT_GROUND = make_material("Site_Asphalt", (0.13, 0.13, 0.14), 0.90)


# ----------------------------------------------------------------------------
# deck geometry
# ----------------------------------------------------------------------------
def deck_z(theta, radius):
    """Helical rise plus a constant cross-fall draining to the outside."""
    t = (radius - R_IN) / (R_OUT - R_IN)
    return RISE * theta / (2.0 * math.pi) + 0.10 - 0.17 * t


deck_bm = bmesh.new()
grid = []
for i in range(N_STEP + 1):
    th = THETA_MAX * i / N_STEP
    ring = []
    for j in range(N_RAD + 1):
        r = R_IN + (R_OUT - R_IN) * j / N_RAD
        ring.append(deck_bm.verts.new((r * math.cos(th), r * math.sin(th), deck_z(th, r))))
    grid.append(ring)
for i in range(N_STEP):
    for j in range(N_RAD):
        deck_bm.faces.new((grid[i][j], grid[i][j + 1], grid[i + 1][j + 1], grid[i + 1][j]))
bmesh.ops.recalc_face_normals(deck_bm, faces=deck_bm.faces[:])
deck = object_from_bmesh("Ramp_Deck", deck_bm, [MAT_DECK])

solid = deck.modifiers.new("Slab", 'SOLIDIFY')
solid.thickness = DECK_T
solid.offset = -1.0
solid.use_even_offset = True

# ground level entry apron
apron_bm = bmesh.new()
add_box(apron_bm, (12.5, -1.0, deck_z(0.0, 12.5) - DECK_T * 0.5),
        (7.0, 8.0, DECK_T), rot_z=math.radians(-6.0))
bmesh.ops.recalc_face_normals(apron_bm, faces=apron_bm.faces[:])
object_from_bmesh("Entry_Apron", apron_bm, [MAT_DECK])


# ----------------------------------------------------------------------------
# guard rails: posts + twin tube rails, inner and outer
# ----------------------------------------------------------------------------
post_bm = bmesh.new()
kerb_bm = bmesh.new()

RAIL_H1, RAIL_H2 = 0.52, 1.02
POST_H = 1.10
EDGES = ((R_IN + 0.28, "Inner"), (R_OUT - 0.28, "Outer"))

for (r_edge, tag) in EDGES:
    # posts spaced roughly every 2.8 m of arc
    arc_len = r_edge * THETA_MAX
    n_post = max(6, int(arc_len / 2.8))
    for k in range(n_post + 1):
        th = THETA_MAX * k / n_post
        z0 = deck_z(th, r_edge)
        p = Vector((r_edge * math.cos(th), r_edge * math.sin(th), z0))
        add_tube(post_bm, p, p + Vector((0.0, 0.0, POST_H)), 0.038, segments=8)
        # base plate
        add_box(post_bm, (p.x, p.y, z0 + 0.012), (0.16, 0.16, 0.024), rot_z=th)

    # rail tubes
    for h in (RAIL_H1, RAIL_H2):
        pts = []
        for k in range(N_STEP + 1):
            th = THETA_MAX * k / N_STEP
            pts.append((r_edge * math.cos(th), r_edge * math.sin(th), deck_z(th, r_edge) + h))
        poly_curve("Rail_%s_%0.2f" % (tag, h), pts, 0.045, MAT_RAIL)

    # painted kerb along the deck edge
    kerb_r = r_edge + (-0.28 if tag == "Inner" else 0.28)
    ring_prev = None
    for k in range(N_STEP + 1):
        th = THETA_MAX * k / N_STEP
        z0 = deck_z(th, kerb_r)
        c = Vector((kerb_r * math.cos(th), kerb_r * math.sin(th), z0 + 0.075))
        if ring_prev is not None:
            add_tube(kerb_bm, ring_prev, c, 0.075, segments=6)
        ring_prev = c

object_from_bmesh("Rail_Posts", post_bm, [MAT_POST])
object_from_bmesh("Edge_Kerbs", kerb_bm, [MAT_KERB])


# ----------------------------------------------------------------------------
# columns and central core
# ----------------------------------------------------------------------------
col_bm = bmesh.new()
N_COL = 8
for k in range(N_COL):
    ang = 2.0 * math.pi * k / N_COL
    # tallest deck pass over this angle
    passes = [ang + 2.0 * math.pi * n for n in range(0, int(TURNS) + 2)
              if 0.25 < ang + 2.0 * math.pi * n <= THETA_MAX]
    if not passes:
        continue
    th_top = max(passes)
    for r_col in (R_IN + 0.85, R_OUT - 0.85):
        z_top = deck_z(th_top, r_col) - DECK_T
        base = Vector((r_col * math.cos(ang), r_col * math.sin(ang), -0.30))
        top = Vector((base.x, base.y, z_top))
        if top.z - base.z < 0.5:
            continue
        add_tube(col_bm, base, top, 0.34, segments=16)
        # flared capital and footing
        bmesh.ops.create_cone(col_bm, cap_ends=True, cap_tris=False, segments=16,
                              radius1=0.34, radius2=0.58, depth=0.55,
                              matrix=Matrix.Translation(top - Vector((0, 0, 0.28))))
        add_box(col_bm, (base.x, base.y, -0.18), (1.25, 1.25, 0.42), rot_z=ang)

# central circulation core
core_top = RISE * TURNS + 2.4
bmesh.ops.create_cone(col_bm, cap_ends=True, cap_tris=False, segments=32,
                      radius1=4.6, radius2=4.6, depth=core_top + 0.4,
                      matrix=Matrix.Translation((0.0, 0.0, (core_top - 0.4) * 0.5)))
bmesh.ops.create_cone(col_bm, cap_ends=True, cap_tris=False, segments=32,
                      radius1=5.0, radius2=5.0, depth=0.45,
                      matrix=Matrix.Translation((0.0, 0.0, core_top + 0.2)))
# core parapet ring
for k in range(24):
    a0 = 2.0 * math.pi * k / 24.0
    a1 = 2.0 * math.pi * (k + 1) / 24.0
    add_tube(col_bm,
             (4.9 * math.cos(a0), 4.9 * math.sin(a0), core_top + 1.0),
             (4.9 * math.cos(a1), 4.9 * math.sin(a1), core_top + 1.0),
             0.09, segments=8)
object_from_bmesh("Columns_and_Core", col_bm, [MAT_COL])


# ----------------------------------------------------------------------------
# ground slab
# ----------------------------------------------------------------------------
ground_bm = bmesh.new()
bmesh.ops.create_cone(ground_bm, cap_ends=True, cap_tris=False, segments=48,
                      radius1=R_OUT + 12.0, radius2=R_OUT + 12.0, depth=0.5,
                      matrix=Matrix.Translation((0.0, 0.0, -0.75)))
object_from_bmesh("Ground_Slab", ground_bm, [MAT_GROUND])


# ----------------------------------------------------------------------------
# lighting and camera
# ----------------------------------------------------------------------------
world = bpy.data.worlds.new("RampWorld")
world.use_nodes = True
bg = world.node_tree.nodes["Background"]
bg.inputs["Color"].default_value = (0.30, 0.36, 0.46, 1.0)
bg.inputs["Strength"].default_value = 1.0
scn.world = world

sun_data = bpy.data.lights.new("Sun", 'SUN')
sun_data.energy = 3.4
sun_data.angle = math.radians(2.0)
sun = bpy.data.objects.new("Sun", sun_data)
sun.rotation_euler = Euler((math.radians(48.0), 0.0, math.radians(-55.0)), 'XYZ')
sun.location = (20.0, -25.0, 40.0)
scn.collection.objects.link(sun)

fill_data = bpy.data.lights.new("Fill", 'AREA')
fill_data.energy = 9000.0
fill_data.size = 30.0
fill_data.color = (0.75, 0.82, 1.0)
fill = bpy.data.objects.new("Fill", fill_data)
fill.location = (-28.0, 22.0, 24.0)
look_at(fill, (0.0, 0.0, 4.0))
scn.collection.objects.link(fill)

cam_data = bpy.data.cameras.new("Camera")
cam_data.lens = 40.0
cam_data.clip_end = 400.0
cam = bpy.data.objects.new("Camera", cam_data)
cam.location = (36.0, -40.0, 24.0)
scn.collection.objects.link(cam)
look_at(cam, (0.0, 0.0, 4.5))
scn.camera = cam

print("claude-118: spiral ramp built (%.1f turns, %.1f m total rise)" % (TURNS, RISE * TURNS))
