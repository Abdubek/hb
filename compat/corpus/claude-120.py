"""claude-120 : A woven basket modelled from crossing strips with a reinforced rim
and two handles.

Vertical stakes rise along a flared profile; horizontal weaver strips undulate
in and out past each stake (phase flipping row to row) to produce a real over/
under weave. The rim is doubled inside and out, lashed at every stake, and two
arched handles are lashed on at opposite sides.
"""

import bpy
import bmesh
import math
import random
from mathutils import Vector, Matrix, Euler

random.seed(5)
bpy.ops.wm.read_factory_settings(use_empty=True)
scn = bpy.context.scene
scn.unit_settings.system = 'METRIC'

# --- basket parameters (metres) --------------------------------------------
N_STAKES = 24
HEIGHT = 0.300
R_BASE = 0.160
R_RIM = 0.258

STAKE_W = 0.018          # tangential width
STAKE_T = 0.0055         # radial thickness
WEAVE_H = 0.0145         # vertical width of a weaver
WEAVE_T = 0.0050         # radial thickness of a weaver
WEAVE_AMP = 0.0058       # in/out excursion past the stakes
ROW_STEP = 0.0180
THETA_SEG = 192


# ----------------------------------------------------------------------------
# helpers
# ----------------------------------------------------------------------------
def make_material(name, colour, rough=0.7, metal=0.0, sheen=0.0):
    mat = bpy.data.materials.new(name)
    mat.use_nodes = True
    bsdf = mat.node_tree.nodes["Principled BSDF"]
    bsdf.inputs["Base Color"].default_value = (colour[0], colour[1], colour[2], 1.0)
    bsdf.inputs["Roughness"].default_value = rough
    bsdf.inputs["Metallic"].default_value = metal
    if "Sheen Weight" in bsdf.inputs:
        bsdf.inputs["Sheen Weight"].default_value = sheen
    return mat


def object_from_bmesh(name, bm, materials, smooth=False):
    me = bpy.data.meshes.new(name)
    bm.to_mesh(me)
    bm.free()
    for m in materials:
        me.materials.append(m)
    if smooth:
        for p in me.polygons:
            p.use_smooth = True
    me.validate()
    ob = bpy.data.objects.new(name, me)
    scn.collection.objects.link(ob)
    return ob


def ribbon(bm, sections, closed=False, cap=True):
    """sections: list of 4-tuples of Vectors, ordered around the cross-section."""
    rings = [[bm.verts.new(p) for p in sec] for sec in sections]
    n = len(rings)
    span = range(n) if closed else range(n - 1)
    for i in span:
        a = rings[i]
        b = rings[(i + 1) % n]
        for k in range(4):
            k2 = (k + 1) % 4
            bm.faces.new((a[k], a[k2], b[k2], b[k]))
    if cap and not closed:
        bm.faces.new(tuple(reversed(rings[0])))
        bm.faces.new(tuple(rings[-1]))


def add_torus(bm, mtx, major_r, minor_r, nu=28, nv=10):
    rings = []
    for i in range(nu):
        a = 2.0 * math.pi * i / nu
        ring = []
        for j in range(nv):
            b = 2.0 * math.pi * j / nv
            rr = major_r + minor_r * math.cos(b)
            p = Vector((rr * math.cos(a), rr * math.sin(a), minor_r * math.sin(b)))
            ring.append(bm.verts.new(mtx @ p))
        rings.append(ring)
    for i in range(nu):
        a = rings[i]
        b = rings[(i + 1) % nu]
        for j in range(nv):
            j2 = (j + 1) % nv
            bm.faces.new((a[j], a[j2], b[j2], b[j]))


def poly_curve(name, pts, depth, material, resolution=3):
    cu = bpy.data.curves.new(name, 'CURVE')
    cu.dimensions = '3D'
    cu.bevel_depth = depth
    cu.bevel_resolution = resolution
    cu.fill_mode = 'FULL'
    sp = cu.splines.new('POLY')
    sp.points.add(len(pts) - 1)
    for i, p in enumerate(pts):
        sp.points[i].co = (p[0], p[1], p[2], 1.0)
    cu.materials.append(material)
    ob = bpy.data.objects.new(name, cu)
    scn.collection.objects.link(ob)
    return ob


def look_at(ob, target):
    d = Vector(target) - ob.location
    ob.rotation_euler = d.to_track_quat('-Z', 'Y').to_euler()


# ----------------------------------------------------------------------------
# materials
# ----------------------------------------------------------------------------
MAT_STAKE = make_material("Willow_Stake", (0.44, 0.29, 0.14), 0.72, 0.0, 0.3)
MAT_WEAVE = make_material("Willow_Weaver", (0.58, 0.40, 0.20), 0.68, 0.0, 0.35)
MAT_RIM = make_material("Rim_Rod", (0.36, 0.22, 0.10), 0.65, 0.0, 0.25)
MAT_LASH = make_material("Lashing", (0.66, 0.50, 0.26), 0.60, 0.0, 0.4)
MAT_HANDLE = make_material("Handle_Bow", (0.33, 0.20, 0.09), 0.62, 0.0, 0.25)
MAT_BASE = make_material("Base_Weave", (0.50, 0.34, 0.17), 0.75, 0.0, 0.3)
MAT_TABLE = make_material("Table_Oak", (0.30, 0.20, 0.12), 0.55)


# ----------------------------------------------------------------------------
# profile
# ----------------------------------------------------------------------------
def profile_r(z):
    """Flared wall with a slight belly."""
    t = max(0.0, min(1.0, z / HEIGHT))
    return (R_BASE + (R_RIM - R_BASE) * (t ** 0.82)
            + 0.010 * math.sin(math.pi * t))


# ----------------------------------------------------------------------------
# stakes (vertical crossing strips)
# ----------------------------------------------------------------------------
stake_bm = bmesh.new()
N_Z = 34
for s in range(N_STAKES):
    th = 2.0 * math.pi * s / N_STAKES
    er = Vector((math.cos(th), math.sin(th), 0.0))
    et = Vector((-math.sin(th), math.cos(th), 0.0))
    sections = []
    for k in range(N_Z + 1):
        z = -0.004 + (HEIGHT + 0.020 + 0.004) * k / N_Z
        r = profile_r(max(0.0, z))
        c = er * r + Vector((0.0, 0.0, z))
        hw = et * (STAKE_W * 0.5)
        ht = er * (STAKE_T * 0.5)
        sections.append((c + ht + hw, c + ht - hw, c - ht - hw, c - ht + hw))
    ribbon(stake_bm, sections, closed=False, cap=True)
bmesh.ops.recalc_face_normals(stake_bm, faces=stake_bm.faces[:])
object_from_bmesh("Stakes", stake_bm, [MAT_STAKE])


# ----------------------------------------------------------------------------
# weavers (horizontal strips crossing the stakes over/under)
# ----------------------------------------------------------------------------
weave_bm = bmesh.new()
row = 0
z = 0.012
while z <= HEIGHT - 0.014:
    phase = math.pi * (row % 2)
    jitter = 0.0008 * math.sin(row * 2.1)
    r0 = profile_r(z)
    sections = []
    for i in range(THETA_SEG):
        th = 2.0 * math.pi * i / THETA_SEG
        er = Vector((math.cos(th), math.sin(th), 0.0))
        offset = WEAVE_AMP * math.cos(N_STAKES * th + phase)
        r = r0 + offset + jitter
        zz = z + 0.0012 * math.sin(N_STAKES * th + phase)
        c = er * r + Vector((0.0, 0.0, zz))
        ht = er * (WEAVE_T * 0.5)
        hz = Vector((0.0, 0.0, WEAVE_H * 0.5))
        sections.append((c + ht + hz, c + ht - hz, c - ht - hz, c - ht + hz))
    ribbon(weave_bm, sections, closed=True, cap=False)
    row += 1
    z += ROW_STEP
bmesh.ops.recalc_face_normals(weave_bm, faces=weave_bm.faces[:])
object_from_bmesh("Weavers", weave_bm, [MAT_WEAVE])


# ----------------------------------------------------------------------------
# woven base: two crossing layers of flat slats plus a foot ring
# ----------------------------------------------------------------------------
base_bm = bmesh.new()
SLAT_W = 0.020
SLAT_T = 0.0045
n_slat = int((R_BASE * 2.0 - 0.01) / (SLAT_W + 0.004))
for layer, ang in enumerate((0.0, math.pi * 0.5)):
    zc = -0.004 - layer * (SLAT_T + 0.0008)
    ca, sa = math.cos(ang), math.sin(ang)
    for i in range(n_slat):
        off = (i - (n_slat - 1) * 0.5) * (SLAT_W + 0.004)
        half = math.sqrt(max(0.0, (R_BASE - 0.004) ** 2 - off * off))
        if half < 0.01:
            continue
        wob = 0.0012 if (i % 2 == layer % 2) else -0.0012
        u = Vector((ca, sa, 0.0))
        v = Vector((-sa, ca, 0.0))
        sections = []
        steps = 10
        for k in range(steps + 1):
            t = -half + 2.0 * half * k / steps
            c = u * t + v * off + Vector((0.0, 0.0, zc + wob * math.sin(t * 40.0)))
            hw = v * (SLAT_W * 0.5)
            hz = Vector((0.0, 0.0, SLAT_T * 0.5))
            sections.append((c + hz + hw, c + hz - hw, c - hz - hw, c - hz + hw))
        ribbon(base_bm, sections, closed=False, cap=True)
add_torus(base_bm, Matrix.Translation((0.0, 0.0, -0.012)), R_BASE - 0.006, 0.0075,
          nu=48, nv=10)
bmesh.ops.recalc_face_normals(base_bm, faces=base_bm.faces[:])
object_from_bmesh("Base_Weave", base_bm, [MAT_BASE], smooth=True)


# ----------------------------------------------------------------------------
# reinforced rim: inner + outer rods, lashed at every stake
# ----------------------------------------------------------------------------
rim_bm = bmesh.new()
Z_RIM = HEIGHT + 0.006
R_WALL = profile_r(HEIGHT)
RIM_ROD = 0.0075
add_torus(rim_bm, Matrix.Translation((0.0, 0.0, Z_RIM)),
          R_WALL + STAKE_T * 0.5 + RIM_ROD, RIM_ROD, nu=72, nv=12)
add_torus(rim_bm, Matrix.Translation((0.0, 0.0, Z_RIM)),
          R_WALL - STAKE_T * 0.5 - RIM_ROD, RIM_ROD, nu=72, nv=12)
add_torus(rim_bm, Matrix.Translation((0.0, 0.0, Z_RIM + 0.012)),
          R_WALL + 0.002, RIM_ROD * 0.8, nu=72, nv=12)
bmesh.ops.recalc_face_normals(rim_bm, faces=rim_bm.faces[:])
object_from_bmesh("Rim_Rods", rim_bm, [MAT_RIM], smooth=True)

lash_bm = bmesh.new()
for s in range(N_STAKES):
    th = 2.0 * math.pi * (s + 0.5) / N_STAKES
    er = Vector((math.cos(th), math.sin(th), 0.0))
    centre = er * R_WALL + Vector((0.0, 0.0, Z_RIM + 0.004))
    # a wrap encircling the rim bundle: torus whose axis is tangential
    basis = (Matrix.Translation(centre) @
             Matrix.Rotation(th, 4, 'Z') @
             Matrix.Rotation(math.radians(90.0), 4, 'X'))
    add_torus(lash_bm, basis, 0.0185, 0.0028, nu=20, nv=8)
    basis2 = (Matrix.Translation(centre + Vector((0.0, 0.0, 0.010))) @
              Matrix.Rotation(th, 4, 'Z') @
              Matrix.Rotation(math.radians(78.0), 4, 'X'))
    add_torus(lash_bm, basis2, 0.0175, 0.0025, nu=20, nv=8)
bmesh.ops.recalc_face_normals(lash_bm, faces=lash_bm.faces[:])
object_from_bmesh("Rim_Lashings", lash_bm, [MAT_LASH], smooth=True)


# ----------------------------------------------------------------------------
# two arched handles
# ----------------------------------------------------------------------------
handle_lash_bm = bmesh.new()
SPREAD = 0.42          # half angular spread of a handle at the rim
for hi, th0 in enumerate((0.0, math.pi)):
    a0 = th0 - SPREAD
    a1 = th0 + SPREAD
    p0 = Vector((R_WALL * math.cos(a0), R_WALL * math.sin(a0), Z_RIM - 0.030))
    p1 = Vector((R_WALL * math.cos(a1), R_WALL * math.sin(a1), Z_RIM - 0.030))
    mid_dir = Vector((math.cos(th0), math.sin(th0), 0.0))
    ctrl = (p0 + p1) * 0.5 + mid_dir * 0.045 + Vector((0.0, 0.0, 0.330))
    pts = []
    steps = 40
    for k in range(steps + 1):
        t = k / steps
        p = (p0 * (1.0 - t) ** 2 + ctrl * 2.0 * t * (1.0 - t) + p1 * t * t)
        pts.append((p.x, p.y, p.z))
    poly_curve("Handle_%d" % hi, pts, 0.0090, MAT_HANDLE, resolution=3)

    # a slimmer twisted binding running alongside the bow
    pts2 = []
    for k in range(steps + 1):
        t = k / steps
        p = (p0 * (1.0 - t) ** 2 + ctrl * 2.0 * t * (1.0 - t) + p1 * t * t)
        n = Vector((-math.sin(th0), math.cos(th0), 0.0))
        p = p + n * 0.011 * math.sin(t * math.pi * 9.0) \
              + Vector((0.0, 0.0, 0.011 * math.cos(t * math.pi * 9.0)))
        pts2.append((p.x, p.y, p.z))
    poly_curve("Handle_Wrap_%d" % hi, pts2, 0.0035, MAT_LASH, resolution=2)

    # lashings tying each handle end into the rim
    for (pe, ae) in ((p0, a0), (p1, a1)):
        for dz in (0.006, 0.022, 0.038):
            centre = Vector((R_WALL * math.cos(ae), R_WALL * math.sin(ae), pe.z + dz))
            basis = (Matrix.Translation(centre) @
                     Matrix.Rotation(ae, 4, 'Z') @
                     Matrix.Rotation(math.radians(90.0), 4, 'X'))
            add_torus(handle_lash_bm, basis, 0.0165, 0.0030, nu=20, nv=8)
bmesh.ops.recalc_face_normals(handle_lash_bm, faces=handle_lash_bm.faces[:])
object_from_bmesh("Handle_Lashings", handle_lash_bm, [MAT_LASH], smooth=True)


# ----------------------------------------------------------------------------
# table surface
# ----------------------------------------------------------------------------
table_bm = bmesh.new()
bmesh.ops.create_grid(table_bm, x_segments=1, y_segments=1, size=1.5,
                      matrix=Matrix.Translation((0.0, 0.0, -0.020)))
object_from_bmesh("Table", table_bm, [MAT_TABLE])


# ----------------------------------------------------------------------------
# lighting and camera
# ----------------------------------------------------------------------------
world = bpy.data.worlds.new("BasketWorld")
world.use_nodes = True
bg = world.node_tree.nodes["Background"]
bg.inputs["Color"].default_value = (0.13, 0.13, 0.14, 1.0)
bg.inputs["Strength"].default_value = 1.0
scn.world = world


def add_area(name, loc, target, energy, size, colour=(1.0, 1.0, 1.0)):
    ld = bpy.data.lights.new(name, 'AREA')
    ld.energy = energy
    ld.size = size
    ld.color = colour
    ob = bpy.data.objects.new(name, ld)
    ob.location = loc
    scn.collection.objects.link(ob)
    look_at(ob, target)
    return ob


add_area("Key", (-0.85, -0.75, 1.05), (0.0, 0.0, 0.18), 180.0, 1.0, (1.0, 0.96, 0.90))
add_area("Fill", (0.95, -0.55, 0.45), (0.0, 0.0, 0.16), 45.0, 1.4, (0.86, 0.90, 1.0))
add_area("Rim", (0.35, 1.05, 0.85), (0.0, 0.0, 0.22), 110.0, 0.7, (1.0, 0.93, 0.82))

cam_data = bpy.data.cameras.new("Camera")
cam_data.lens = 65.0
cam_data.dof.use_dof = True
cam_data.dof.focus_distance = 1.10
cam_data.dof.aperture_fstop = 4.0
cam = bpy.data.objects.new("Camera", cam_data)
cam.location = (0.72, -0.82, 0.52)
scn.collection.objects.link(cam)
look_at(cam, (0.0, 0.0, 0.17))
scn.camera = cam

print("claude-120: woven basket built with %d stakes and %d weaver rows" % (N_STAKES, row))
