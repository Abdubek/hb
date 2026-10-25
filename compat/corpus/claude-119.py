"""claude-119 : A perforated metal speaker grille over a rounded rectangular enclosure.

The grille is generated directly as geometry (no booleans): a hexagonal lattice
of ring cells, each a hexagonal Voronoi cell with a circular hole, welded into a
single sheet, clipped to a rounded-rectangle outline, gently domed, then
solidified. Behind it sit a recessed baffle with woofer and tweeter.
"""

import bpy
import bmesh
import math
from mathutils import Vector, Matrix, Euler

bpy.ops.wm.read_factory_settings(use_empty=True)
scn = bpy.context.scene
scn.unit_settings.system = 'METRIC'

# --- cabinet dimensions (metres) -------------------------------------------
W, D, H = 0.30, 0.26, 0.46
FRONT_Y = -D * 0.5

# --- grille outline ---------------------------------------------------------
GA, GB = 0.130, 0.205        # half width / half height of the grille
GRAD = 0.035                 # outline corner radius
PITCH = 0.0160               # hole centre spacing
HOLE_R = 0.0052
DOME = 0.0060                # forward bulge at the centre
GRILLE_Y = FRONT_Y - 0.008


# ----------------------------------------------------------------------------
# helpers
# ----------------------------------------------------------------------------
def make_material(name, colour, rough=0.5, metal=0.0):
    mat = bpy.data.materials.new(name)
    mat.use_nodes = True
    bsdf = mat.node_tree.nodes["Principled BSDF"]
    bsdf.inputs["Base Color"].default_value = (colour[0], colour[1], colour[2], 1.0)
    bsdf.inputs["Roughness"].default_value = rough
    bsdf.inputs["Metallic"].default_value = metal
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


def add_box(bm, loc, size, rot=None):
    basis = rot if rot is not None else Matrix.Identity(4)
    mtx = (Matrix.Translation(Vector(loc)) @ basis @
           Matrix.Diagonal(Vector((size[0], size[1], size[2], 1.0))))
    bmesh.ops.create_cube(bm, size=1.0, matrix=mtx)


def add_cone_y(bm, loc, r1, r2, depth, segments=32):
    """Cone whose axis lies along -Y (pointing out of the baffle)."""
    mtx = (Matrix.Translation(Vector(loc)) @
           Matrix.Rotation(math.radians(90.0), 4, 'X'))
    bmesh.ops.create_cone(bm, cap_ends=True, cap_tris=False, segments=segments,
                          radius1=r1, radius2=r2, depth=depth, matrix=mtx)


def look_at(ob, target):
    d = Vector(target) - ob.location
    ob.rotation_euler = d.to_track_quat('-Z', 'Y').to_euler()


def rounded_rect_inside(x, z, a, b, rad):
    dx = abs(x) - (a - rad)
    dz = abs(z) - (b - rad)
    if dx <= 0.0 or dz <= 0.0:
        return abs(x) <= a and abs(z) <= b
    return math.hypot(dx, dz) <= rad


def rounded_rect_points(a, b, rad, per_corner=9):
    pts = []
    corners = ((a - rad, b - rad, 0.0),
               (-(a - rad), b - rad, math.pi * 0.5),
               (-(a - rad), -(b - rad), math.pi),
               (a - rad, -(b - rad), math.pi * 1.5))
    for cx, cz, a0 in corners:
        for i in range(per_corner + 1):
            t = a0 + (math.pi * 0.5) * i / per_corner
            pts.append((cx + rad * math.cos(t), cz + rad * math.sin(t)))
    return pts


# ----------------------------------------------------------------------------
# materials
# ----------------------------------------------------------------------------
MAT_GRILLE = make_material("Perf_Metal", (0.26, 0.27, 0.29), 0.34, 1.0)
MAT_BEZEL = make_material("Bezel_Alu", (0.72, 0.73, 0.75), 0.28, 1.0)
MAT_CAB = make_material("Cabinet_Satin", (0.10, 0.105, 0.115), 0.42, 0.05)
MAT_BAFFLE = make_material("Baffle_Felt", (0.035, 0.035, 0.038), 0.92)
MAT_CONE = make_material("Driver_Cone", (0.16, 0.14, 0.12), 0.68)
MAT_SURROUND = make_material("Rubber_Surround", (0.045, 0.045, 0.05), 0.55)
MAT_DOME = make_material("Tweeter_Dome", (0.80, 0.78, 0.70), 0.22, 0.9)
MAT_FOOT = make_material("Foot_Rubber", (0.05, 0.05, 0.055), 0.75)
MAT_FLOOR = make_material("Studio_Floor", (0.30, 0.30, 0.32), 0.60)


# ----------------------------------------------------------------------------
# enclosure
# ----------------------------------------------------------------------------
cab_bm = bmesh.new()
add_box(cab_bm, (0.0, 0.0, H * 0.5), (W, D, H))
cab = object_from_bmesh("Enclosure", cab_bm, [MAT_CAB])

bev = cab.modifiers.new("Round", 'BEVEL')
bev.width = 0.026
bev.segments = 6
bev.limit_method = 'ANGLE'
bev.angle_limit = math.radians(30.0)
bev.harden_normals = False

bpy.context.view_layer.objects.active = cab
cab.select_set(True)
try:
    bpy.ops.object.shade_auto_smooth(angle=math.radians(35.0))
except Exception:
    for p in cab.data.polygons:
        p.use_smooth = True
cab.select_set(False)


# ----------------------------------------------------------------------------
# perforated grille sheet
# ----------------------------------------------------------------------------
def dome_offset(x, z):
    fx = max(0.0, 1.0 - (x / GA) ** 2)
    fz = max(0.0, 1.0 - (z / GB) ** 2)
    return -DOME * fx * fz


RING_N = 24
HEX_R = PITCH / math.sqrt(3.0)
HEX_V = [(HEX_R * math.cos(math.radians(30.0) + k * math.pi / 3.0),
          HEX_R * math.sin(math.radians(30.0) + k * math.pi / 3.0)) for k in range(6)]

grille_bm = bmesh.new()


def add_hex_cell(bm, cx, cz):
    outer = []
    inner = []
    for k in range(RING_N):
        e = k // 4
        t = (k % 4) / 4.0
        v0 = HEX_V[e]
        v1 = HEX_V[(e + 1) % 6]
        ox = cx + v0[0] + (v1[0] - v0[0]) * t
        oz = cz + v0[1] + (v1[1] - v0[1]) * t
        ang = math.radians(30.0) + k * (2.0 * math.pi / RING_N)
        ix = cx + HOLE_R * math.cos(ang)
        iz = cz + HOLE_R * math.sin(ang)
        outer.append(bm.verts.new((ox, GRILLE_Y + dome_offset(ox, oz), oz)))
        inner.append(bm.verts.new((ix, GRILLE_Y + dome_offset(ix, iz), iz)))
    for k in range(RING_N):
        k2 = (k + 1) % RING_N
        bm.faces.new((outer[k], outer[k2], inner[k2], inner[k]))


row_h = PITCH * math.sqrt(3.0) * 0.5
n_rows = int(math.ceil(GB / row_h)) + 1
n_cols = int(math.ceil(GA / PITCH)) + 1
cell_count = 0
for j in range(-n_rows, n_rows + 1):
    cz = j * row_h
    xoff = (PITCH * 0.5) if (j % 2) else 0.0
    for i in range(-n_cols, n_cols + 1):
        cx = i * PITCH + xoff
        if not rounded_rect_inside(cx, cz, GA - PITCH * 0.55, GB - PITCH * 0.55, GRAD):
            continue
        add_hex_cell(grille_bm, cx, cz)
        cell_count += 1

bmesh.ops.remove_doubles(grille_bm, verts=grille_bm.verts[:], dist=PITCH * 1e-3)
bmesh.ops.recalc_face_normals(grille_bm, faces=grille_bm.faces[:])
grille = object_from_bmesh("Perforated_Grille", grille_bm, [MAT_GRILLE])

sol = grille.modifiers.new("Sheet", 'SOLIDIFY')
sol.thickness = 0.0013
sol.offset = 0.0


# ----------------------------------------------------------------------------
# grille bezel frame (rounded rectangle sweep)
# ----------------------------------------------------------------------------
bez_pts = rounded_rect_points(GA, GB, GRAD, per_corner=10)
cu = bpy.data.curves.new("Bezel", 'CURVE')
cu.dimensions = '3D'
cu.bevel_depth = 0.0055
cu.bevel_resolution = 3
cu.fill_mode = 'FULL'
sp = cu.splines.new('POLY')
sp.points.add(len(bez_pts) - 1)
for i, (px, pz) in enumerate(bez_pts):
    sp.points[i].co = (px, GRILLE_Y + 0.0005, pz, 1.0)
sp.use_cyclic_u = True
cu.materials.append(MAT_BEZEL)
bezel = bpy.data.objects.new("Grille_Bezel", cu)
scn.collection.objects.link(bezel)


# ----------------------------------------------------------------------------
# recessed baffle and drivers behind the grille
# ----------------------------------------------------------------------------
baffle_bm = bmesh.new()
add_box(baffle_bm, (0.0, FRONT_Y + 0.012, H * 0.5), (W - 0.030, 0.010, H - 0.030))
object_from_bmesh("Baffle", baffle_bm, [MAT_BAFFLE])

WOOF_Z = H * 0.5 - 0.085
TWEET_Z = H * 0.5 + 0.115
BY = FRONT_Y + 0.008

cone_bm = bmesh.new()
add_cone_y(cone_bm, (0.0, BY + 0.030, WOOF_Z), 0.020, 0.082, 0.052, segments=36)
add_cone_y(cone_bm, (0.0, BY - 0.001, WOOF_Z), 0.024, 0.020, 0.012, segments=28)  # dust cap
object_from_bmesh("Woofer_Cone", cone_bm, [MAT_CONE], smooth=True)

sur_bm = bmesh.new()
# rubber surround: half torus ring around the woofer
RMAJ, RMIN = 0.089, 0.008
rings = []
for i in range(40):
    a = 2.0 * math.pi * i / 40.0
    ring = []
    for j in range(10):
        b = 2.0 * math.pi * j / 10.0
        rr = RMAJ + RMIN * math.cos(b)
        ring.append(sur_bm.verts.new((rr * math.cos(a), BY - RMIN * math.sin(b),
                                      WOOF_Z + rr * math.sin(a) - 0.0)))
    rings.append(ring)
# rebuild properly as a torus in the XZ plane
sur_bm.free()
sur_bm = bmesh.new()
for i in range(40):
    a = 2.0 * math.pi * i / 40.0
    ring = []
    for j in range(10):
        b = 2.0 * math.pi * j / 10.0
        rr = RMAJ + RMIN * math.cos(b)
        ring.append(sur_bm.verts.new((rr * math.cos(a), BY + 0.004 - RMIN * math.sin(b),
                                      WOOF_Z + rr * math.sin(a))))
    rings.append(ring)
rings = rings[-40:]
for i in range(40):
    a_ring = rings[i]
    b_ring = rings[(i + 1) % 40]
    for j in range(10):
        j2 = (j + 1) % 10
        sur_bm.faces.new((a_ring[j], a_ring[j2], b_ring[j2], b_ring[j]))
bmesh.ops.recalc_face_normals(sur_bm, faces=sur_bm.faces[:])
object_from_bmesh("Woofer_Surround", sur_bm, [MAT_SURROUND], smooth=True)

basket_bm = bmesh.new()
add_cone_y(basket_bm, (0.0, BY + 0.012, WOOF_Z), 0.098, 0.098, 0.012, segments=36)
object_from_bmesh("Woofer_Basket", basket_bm, [MAT_BAFFLE], smooth=True)

tw_bm = bmesh.new()
add_cone_y(tw_bm, (0.0, BY + 0.010, TWEET_Z), 0.034, 0.034, 0.010, segments=28)
add_cone_y(tw_bm, (0.0, BY + 0.006, TWEET_Z), 0.030, 0.016, 0.010, segments=28)
object_from_bmesh("Tweeter_Faceplate", tw_bm, [MAT_BAFFLE], smooth=True)

dome_bm = bmesh.new()
bmesh.ops.create_uvsphere(dome_bm, u_segments=24, v_segments=12, radius=0.0145,
                          matrix=(Matrix.Translation((0.0, BY + 0.004, TWEET_Z)) @
                                  Matrix.Diagonal(Vector((1.0, 0.55, 1.0, 1.0)))))
object_from_bmesh("Tweeter_Dome", dome_bm, [MAT_DOME], smooth=True)


# ----------------------------------------------------------------------------
# feet, rear terminal plate, floor
# ----------------------------------------------------------------------------
feet_bm = bmesh.new()
for sx in (-1, 1):
    for sy in (-1, 1):
        loc = (sx * (W * 0.5 - 0.035), sy * (D * 0.5 - 0.035), -0.008)
        bmesh.ops.create_cone(feet_bm, cap_ends=True, cap_tris=False, segments=16,
                              radius1=0.014, radius2=0.012, depth=0.016,
                              matrix=Matrix.Translation(loc))
object_from_bmesh("Feet", feet_bm, [MAT_FOOT], smooth=True)

term_bm = bmesh.new()
add_box(term_bm, (0.0, D * 0.5 - 0.004, 0.075), (0.085, 0.012, 0.055))
for sx in (-0.022, 0.022):
    bmesh.ops.create_cone(term_bm, cap_ends=True, cap_tris=False, segments=14,
                          radius1=0.008, radius2=0.008, depth=0.016,
                          matrix=(Matrix.Translation((sx, D * 0.5 + 0.006, 0.075)) @
                                  Matrix.Rotation(math.radians(90.0), 4, 'X')))
object_from_bmesh("Terminals", term_bm, [MAT_BEZEL], smooth=True)

floor_bm = bmesh.new()
bmesh.ops.create_grid(floor_bm, x_segments=1, y_segments=1, size=3.0,
                      matrix=Matrix.Translation((0.0, 0.0, -0.016)))
object_from_bmesh("Floor", floor_bm, [MAT_FLOOR])

back_bm = bmesh.new()
bmesh.ops.create_grid(back_bm, x_segments=1, y_segments=1, size=3.0,
                      matrix=(Matrix.Translation((0.0, 1.6, 1.4)) @
                              Matrix.Rotation(math.radians(90.0), 4, 'X')))
object_from_bmesh("Backdrop", back_bm, [MAT_FLOOR])


# ----------------------------------------------------------------------------
# lighting and camera
# ----------------------------------------------------------------------------
world = bpy.data.worlds.new("StudioWorld")
world.use_nodes = True
bg = world.node_tree.nodes["Background"]
bg.inputs["Color"].default_value = (0.045, 0.048, 0.055, 1.0)
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


add_area("Key", (-0.75, -0.95, 0.85), (0.0, 0.0, 0.26), 120.0, 0.9)
add_area("Fill", (0.85, -0.70, 0.40), (0.0, 0.0, 0.22), 35.0, 1.2, (0.85, 0.90, 1.0))
add_area("Rim", (0.55, 0.85, 1.00), (0.0, 0.0, 0.30), 90.0, 0.6, (0.9, 0.95, 1.0))

cam_data = bpy.data.cameras.new("Camera")
cam_data.lens = 85.0
cam_data.dof.use_dof = True
cam_data.dof.focus_distance = 1.05
cam_data.dof.aperture_fstop = 5.6
cam = bpy.data.objects.new("Camera", cam_data)
cam.location = (0.48, -0.92, 0.42)
scn.collection.objects.link(cam)
look_at(cam, (0.0, 0.0, 0.26))
scn.camera = cam

print("claude-119: grille built from %d hexagonal perforation cells" % cell_count)
