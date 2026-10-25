"""claude-047 - A courtyard with a fountain and surrounding planters.

A 20 x 20 m enclosed courtyard: radial paved apron around a three tier lathed
fountain with arcing water jets, rectangular planters with shrubs, corner tree
planters, benches, lamp posts and a colonnade along the perimeter walls.
"""

import bpy
import bmesh
import math
import random
from mathutils import Vector, Matrix, Euler

random.seed(47)


# --------------------------------------------------------------------------
# helpers
# --------------------------------------------------------------------------
def reset_scene():
    bpy.ops.wm.read_factory_settings(use_empty=True)
    bpy.context.scene.unit_settings.system = 'METRIC'


def link(obj):
    bpy.context.scene.collection.objects.link(obj)
    return obj


def make_mat(name, color, rough=0.5, metal=0.0, emis=None, emis_str=0.0,
             alpha=1.0, transmission=0.0, ior=1.45):
    m = bpy.data.materials.new(name)
    m.use_nodes = True
    b = m.node_tree.nodes["Principled BSDF"]
    b.inputs["Base Color"].default_value = (color[0], color[1], color[2], 1.0)
    b.inputs["Roughness"].default_value = rough
    b.inputs["Metallic"].default_value = metal
    if "IOR" in b.inputs:
        b.inputs["IOR"].default_value = ior
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


def bm_cyl(bm, center, radius, depth, index=0, segments=24, r2=None, rot=None):
    m = Matrix.Translation(Vector(center))
    if rot is not None:
        m = m @ Euler(rot).to_matrix().to_4x4()
    before = set(bm.faces)
    bmesh.ops.create_cone(bm, cap_ends=True, cap_tris=False, segments=segments,
                          radius1=radius, radius2=(radius if r2 is None else r2),
                          depth=depth, matrix=m)
    tag_new(bm, before, index)


def bm_sphere(bm, center, radius, index=0, subdiv=2, scale=(1, 1, 1)):
    m = Matrix.Translation(Vector(center)) @ Matrix.Diagonal(
        Vector((scale[0], scale[1], scale[2], 1.0)))
    before = set(bm.faces)
    bmesh.ops.create_icosphere(bm, subdivisions=subdiv, radius=radius, matrix=m)
    for f in bm.faces:
        if f not in before:
            f.material_index = index
            f.smooth = True


def finish(bm, name, mats, location=(0, 0, 0), rotation=(0, 0, 0), smooth_round=False):
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    if smooth_round:
        for f in bm.faces:
            if abs(f.normal.z) < 0.8:
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


def lathe(name, profile, mats, segments=48, location=(0, 0, 0), smooth=True):
    """Revolve a (radius, z) profile polyline about the Z axis."""
    bm = bmesh.new()
    verts = [bm.verts.new((p[0], 0.0, p[1])) for p in profile]
    edges = [bm.edges.new((verts[i], verts[i + 1])) for i in range(len(verts) - 1)]
    bmesh.ops.spin(bm, geom=verts + edges, cent=(0, 0, 0), axis=(0, 0, 1),
                   dvec=(0, 0, 0), angle=2 * math.pi, steps=segments, use_merge=False)
    bmesh.ops.remove_doubles(bm, verts=bm.verts, dist=1e-4)
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    if smooth:
        for f in bm.faces:
            f.smooth = True
    me = bpy.data.meshes.new(name)
    bm.to_mesh(me)
    bm.free()
    obj = bpy.data.objects.new(name, me)
    obj.location = location
    for m in mats:
        me.materials.append(m)
    return link(obj)


def poly_tube(name, points, radius, material, res=4):
    cu = bpy.data.curves.new(name, 'CURVE')
    cu.dimensions = '3D'
    sp = cu.splines.new('POLY')
    sp.points.add(len(points) - 1)
    for i, p in enumerate(points):
        sp.points[i].co = (p[0], p[1], p[2], 1.0)
    cu.bevel_depth = radius
    cu.bevel_resolution = res
    cu.use_fill_caps = True
    obj = bpy.data.objects.new(name, cu)
    cu.materials.append(material)
    return link(obj)


def look_at(obj, target):
    d = Vector(target) - obj.location
    obj.rotation_euler = d.to_track_quat('-Z', 'Y').to_euler()


# --------------------------------------------------------------------------
reset_scene()

M_SLAB = make_mat("CourtyardSlab", (0.52, 0.49, 0.44), rough=0.85)
M_PAVE_A = make_mat("PavingLight", (0.62, 0.58, 0.52), rough=0.8)
M_PAVE_B = make_mat("PavingDark", (0.42, 0.39, 0.36), rough=0.85)
M_GROUT = make_mat("Grout", (0.24, 0.23, 0.22), rough=0.95)
M_STONE = make_mat("Limestone", (0.74, 0.71, 0.63), rough=0.62)
M_STONE_DK = make_mat("StoneWeathered", (0.55, 0.53, 0.47), rough=0.75)
M_WATER = make_mat("Water", (0.14, 0.32, 0.36), rough=0.03,
                   transmission=0.9, alpha=0.5, ior=1.333)
M_JET = make_mat("WaterJet", (0.80, 0.90, 0.95), rough=0.08,
                 transmission=0.7, alpha=0.55, ior=1.333)
M_SOIL = make_mat("Soil", (0.15, 0.10, 0.07), rough=0.95)
M_LEAF_A = make_mat("FoliageA", (0.10, 0.28, 0.09), rough=0.75)
M_LEAF_B = make_mat("FoliageB", (0.16, 0.36, 0.12), rough=0.75)
M_FLOWER = make_mat("Flowers", (0.72, 0.24, 0.34), rough=0.6)
M_BARK = make_mat("Bark", (0.22, 0.16, 0.11), rough=0.9)
M_WOOD = make_mat("BenchWood", (0.38, 0.24, 0.13), rough=0.55)
M_IRON = make_mat("CastIron", (0.10, 0.10, 0.11), rough=0.45, metal=0.8)
M_BRONZE = make_mat("Bronze", (0.42, 0.31, 0.16), rough=0.35, metal=1.0)
M_LAMP = make_mat("LampGlass", (1.0, 0.93, 0.78), rough=0.25,
                  emis=(1.0, 0.88, 0.62), emis_str=14.0)
M_PLASTER = make_mat("WallPlaster", (0.80, 0.74, 0.64), rough=0.8)
M_ROOF = make_mat("RoofTile", (0.45, 0.22, 0.14), rough=0.8)

HALF = 10.0

# ------------------------------------------------------------------ ground
bm = bmesh.new()
bm_box(bm, (0, 0, -0.06), (2 * HALF, 2 * HALF, 0.12), 0)
finish(bm, "CourtyardSlab", [M_SLAB])

# radial paving apron around the fountain -----------------------------------
bm = bmesh.new()
rings = [2.6, 3.4, 4.3, 5.3, 6.4, 7.6]
SEG = 36
gap = 0.035
for ri in range(len(rings) - 1):
    r0, r1 = rings[ri], rings[ri + 1]
    for si in range(SEG):
        a0 = 2 * math.pi * si / SEG
        a1 = 2 * math.pi * (si + 1) / SEG
        am = (a0 + a1) * 0.5
        rm = (r0 + r1) * 0.5
        cx, cy = rm * math.cos(am), rm * math.sin(am)
        idx = (ri + si) % 2
        corners = [(r0, a0), (r1, a0), (r1, a1), (r0, a1)]
        vs = []
        for r, a in corners:
            x, y = r * math.cos(a), r * math.sin(a)
            d = Vector((x - cx, y - cy))
            if d.length > gap:
                d = d - d.normalized() * gap
            vs.append(bm.verts.new((cx + d.x, cy + d.y, 0.015)))
        f = bm.faces.new(vs)
        f.material_index = idx
# square field paving beyond the apron
for gx in range(-9, 9):
    for gy in range(-9, 9):
        cx, cy = gx + 0.5, gy + 0.5
        if math.hypot(cx, cy) < 8.1:
            continue
        s = 0.5 - gap
        idx = (gx + gy) % 2
        vs = [bm.verts.new((cx - s, cy - s, 0.015)),
              bm.verts.new((cx + s, cy - s, 0.015)),
              bm.verts.new((cx + s, cy + s, 0.015)),
              bm.verts.new((cx - s, cy + s, 0.015))]
        bm.faces.new(vs).material_index = idx
finish(bm, "Paving", [M_PAVE_A, M_PAVE_B])

# ------------------------------------------------------------------ fountain
# lower basin ring (revolved profile)
basin_profile = [
    (0.00, 0.00), (2.35, 0.00), (2.35, 0.12), (2.42, 0.20), (2.44, 0.52),
    (2.36, 0.60), (2.16, 0.62), (2.10, 0.52), (2.10, 0.16), (0.55, 0.16),
    (0.50, 0.30), (0.42, 0.30),
]
lathe("FountainBasin", basin_profile, [M_STONE], segments=64)

# pedestal, bowls and finial
stem_profile = [
    (0.42, 0.30), (0.46, 0.36), (0.34, 0.48), (0.30, 0.95), (0.44, 1.05),
    (0.40, 1.12), (1.30, 1.30), (1.34, 1.42), (1.22, 1.46), (1.18, 1.36),
    (0.30, 1.22), (0.26, 1.26), (0.22, 1.85), (0.34, 1.95), (0.30, 2.00),
    (0.82, 2.14), (0.84, 2.24), (0.74, 2.27), (0.72, 2.19), (0.20, 2.08),
    (0.16, 2.12), (0.14, 2.55), (0.22, 2.62), (0.10, 2.78), (0.05, 2.95),
    (0.00, 3.00),
]
lathe("FountainStem", stem_profile, [M_STONE_DK], segments=64)

# water surfaces (rippled discs)
def water_disc(name, radius, z, ripple=0.012, rings_n=8, seg=48):
    bm = bmesh.new()
    center = bm.verts.new((0, 0, z))
    prev = None
    for ri in range(1, rings_n + 1):
        r = radius * ri / rings_n
        ring = []
        for si in range(seg):
            a = 2 * math.pi * si / seg
            zz = z + ripple * math.sin(r * 9.0 + a * 3.0)
            ring.append(bm.verts.new((r * math.cos(a), r * math.sin(a), zz)))
        if prev is None:
            for si in range(seg):
                bm.faces.new((center, ring[si], ring[(si + 1) % seg]))
        else:
            for si in range(seg):
                sj = (si + 1) % seg
                bm.faces.new((prev[si], prev[sj], ring[sj], ring[si]))
        prev = ring
    for f in bm.faces:
        f.smooth = True
    return finish(bm, name, [M_WATER])


water_disc("WaterLower", 2.08, 0.46)
water_disc("WaterMid", 1.16, 1.40, ripple=0.006, rings_n=5, seg=36)
water_disc("WaterUpper", 0.72, 2.22, ripple=0.004, rings_n=4, seg=32)

# arcing jets from the finial into the lower basin
for i in range(8):
    a = 2 * math.pi * i / 8 + math.pi / 8
    pts = []
    v0 = 2.4
    for k in range(19):
        t = k / 18.0 * 1.05
        r = 0.06 + v0 * 0.55 * t
        z = 3.02 + (1.9 * t - 4.9 * t * t)
        if z < 0.5:
            break
        pts.append((r * math.cos(a), r * math.sin(a), z))
    if len(pts) > 2:
        poly_tube("Jet_%d" % i, pts, 0.022, M_JET)

# small central plume + splash droplets
poly_tube("JetCenter", [(0, 0, 3.0), (0, 0, 3.35), (0, 0, 3.6)], 0.028, M_JET)
bm = bmesh.new()
for i in range(26):
    a = random.uniform(0, 2 * math.pi)
    r = random.uniform(0.4, 1.9)
    bm_sphere(bm, (r * math.cos(a), r * math.sin(a), 0.5 + random.uniform(0.0, 0.35)),
              random.uniform(0.015, 0.045), 0, subdiv=1)
finish(bm, "SplashDroplets", [M_JET])


# ------------------------------------------------------------------ greenery
def add_shrub(bm, x, y, z, size, leaf_index, flower_index=None):
    blobs = random.randint(3, 5)
    for i in range(blobs):
        ox = random.uniform(-size * 0.45, size * 0.45)
        oy = random.uniform(-size * 0.45, size * 0.45)
        oz = random.uniform(0.0, size * 0.35)
        r = size * random.uniform(0.42, 0.62)
        bm_sphere(bm, (x + ox, y + oy, z + r * 0.75 + oz), r, leaf_index,
                  subdiv=2, scale=(1.0, 1.0, 0.82))
    if flower_index is not None:
        for i in range(6):
            a = random.uniform(0, 2 * math.pi)
            rr = random.uniform(0.1, size * 0.55)
            bm_sphere(bm, (x + rr * math.cos(a), y + rr * math.sin(a),
                           z + size * random.uniform(0.7, 1.1)),
                      size * 0.09, flower_index, subdiv=1)


planter_positions = []
for sx in (-1, 1):
    for oy in (-3.2, 0.0, 3.2):
        planter_positions.append((sx * 8.2, oy, math.radians(90)))
for sy in (-1, 1):
    for ox in (-3.2, 0.0, 3.2):
        planter_positions.append((ox, sy * 8.2, 0.0))

bm_planter = bmesh.new()
bm_plants = bmesh.new()
for px, py, yaw in planter_positions:
    c, s = math.cos(yaw), math.sin(yaw)
    W, D, H = 2.4, 0.95, 0.55
    # walls of the planter box
    bm_box(bm_planter, (px, py, H / 2), (W, D, H), 0, rot=(0, 0, yaw))
    bm_box(bm_planter, (px, py, H + 0.03), (W + 0.10, D + 0.10, 0.06), 1, rot=(0, 0, yaw))
    bm_box(bm_planter, (px, py, H - 0.02), (W - 0.22, D - 0.22, 0.10), 2, rot=(0, 0, yaw))
    for t in (-0.62, 0.0, 0.62):
        lx = px + c * t * W * 0.5 * 1.0
        ly = py + s * t * W * 0.5 * 1.0
        add_shrub(bm_plants, lx, ly, H + 0.02, random.uniform(0.42, 0.58), 0,
                  1 if random.random() < 0.5 else None)
finish(bm_planter, "Planters", [M_STONE, M_STONE_DK, M_SOIL])
finish(bm_plants, "PlanterShrubs", [M_LEAF_A, M_FLOWER])

# corner tree planters ------------------------------------------------------
bm = bmesh.new()
bm_tree = bmesh.new()
for sx in (-1, 1):
    for sy in (-1, 1):
        px, py = sx * 7.4, sy * 7.4
        bm_cyl(bm, (px, py, 0.30), 1.15, 0.60, 0, segments=24)
        bm_cyl(bm, (px, py, 0.62), 1.24, 0.08, 1, segments=24)
        bm_cyl(bm, (px, py, 0.56), 0.98, 0.10, 2, segments=24)
        # trunk
        bm_cyl(bm_tree, (px, py, 0.60 + 0.85), 0.13, 1.70, 0, segments=12, r2=0.09)
        for i in range(4):
            a = 2 * math.pi * i / 4 + 0.4
            tip = (px + 0.55 * math.cos(a), py + 0.55 * math.sin(a), 2.85)
            base = (px, py, 2.10)
            d = Vector(tip) - Vector(base)
            m = (Matrix.Translation((Vector(base) + Vector(tip)) * 0.5)
                 @ d.to_track_quat('Z', 'Y').to_matrix().to_4x4())
            before = set(bm_tree.faces)
            bmesh.ops.create_cone(bm_tree, cap_ends=True, cap_tris=False, segments=8,
                                  radius1=0.06, radius2=0.03, depth=d.length, matrix=m)
            for f in bm_tree.faces:
                if f not in before:
                    f.material_index = 0
        # canopy
        for i in range(7):
            ox = random.uniform(-0.7, 0.7)
            oy = random.uniform(-0.7, 0.7)
            oz = random.uniform(-0.25, 0.45)
            bm_sphere(bm_tree, (px + ox, py + oy, 3.25 + oz),
                      random.uniform(0.62, 0.95), 1, subdiv=2, scale=(1.0, 1.0, 0.85))
finish(bm, "TreePlanters", [M_STONE, M_STONE_DK, M_SOIL])
finish(bm_tree, "Trees", [M_BARK, M_LEAF_B])


# ------------------------------------------------------------------ benches
def build_bench(name, x, y, yaw):
    bm = bmesh.new()
    for sx in (-0.72, 0.72):
        bm_box(bm, (sx, 0.0, 0.21), (0.08, 0.52, 0.42), 1)
        bm_box(bm, (sx, 0.0, 0.03), (0.14, 0.60, 0.06), 1)
        bm_box(bm, (sx, 0.22, 0.66), (0.06, 0.06, 0.50), 1)
    for i, oy in enumerate((-0.20, -0.02, 0.16)):
        bm_box(bm, (0, oy, 0.45), (1.70, 0.14, 0.05), 0)
    for i, oz in enumerate((0.62, 0.76, 0.90)):
        bm_box(bm, (0, 0.24, oz), (1.70, 0.05, 0.11), 0)
    return finish(bm, name, [M_WOOD, M_IRON], location=(x, y, 0.02),
                  rotation=(0, 0, yaw))


build_bench("BenchN", 0.0, 5.9, math.radians(180))
build_bench("BenchS", 0.0, -5.9, 0.0)
build_bench("BenchE", 5.9, 0.0, math.radians(-90))
build_bench("BenchW", -5.9, 0.0, math.radians(90))

# ---------------------------------------------------------------- lamp posts
lamp_positions = [(6.6, 6.6), (-6.6, 6.6), (6.6, -6.6), (-6.6, -6.6)]
for i, (lx, ly) in enumerate(lamp_positions):
    lathe("LampBase_%d" % i,
          [(0.0, 0.0), (0.24, 0.0), (0.24, 0.10), (0.16, 0.20), (0.09, 0.30),
           (0.07, 2.60), (0.11, 2.68), (0.09, 2.74), (0.0, 2.74)],
          [M_IRON], segments=20, location=(lx, ly, 0.02))
    bm = bmesh.new()
    bm_sphere(bm, (0, 0, 2.98), 0.24, 0, subdiv=3)
    bm_cyl(bm, (0, 0, 3.26), 0.05, 0.12, 1, segments=10, r2=0.02)
    finish(bm, "LampGlobe_%d" % i, [M_LAMP, M_IRON], location=(lx, ly, 0.02))

    ld = bpy.data.lights.new("LampLight_%d" % i, 'POINT')
    ld.energy = 900.0
    ld.color = (1.0, 0.85, 0.62)
    ld.shadow_soft_size = 0.24
    lo = bpy.data.objects.new("LampLight_%d" % i, ld)
    lo.location = (lx, ly, 3.0)
    link(lo)

# -------------------------------------------------- perimeter wall + arcade
bm = bmesh.new()
WALL_H = 4.2
for sx in (-1, 1):
    bm_box(bm, (sx * (HALF + 0.25), 0, WALL_H / 2), (0.50, 2 * HALF + 1.0, WALL_H), 0)
for sy in (-1, 1):
    bm_box(bm, (0, sy * (HALF + 0.25), WALL_H / 2), (2 * HALF + 1.0, 0.50, WALL_H), 0)
# coping and pitched tile cap
for sx in (-1, 1):
    bm_box(bm, (sx * (HALF + 0.25), 0, WALL_H + 0.09), (0.72, 2 * HALF + 1.2, 0.18), 1)
for sy in (-1, 1):
    bm_box(bm, (0, sy * (HALF + 0.25), WALL_H + 0.09), (2 * HALF + 1.2, 0.72, 0.18), 1)
finish(bm, "CourtyardWalls", [M_PLASTER, M_ROOF])

# colonnade: columns + architrave in front of the walls
for axis in ('x', 'y'):
    for side in (-1, 1):
        bm_beam = bmesh.new()
        for k in range(-3, 4):
            t = k * 2.6
            if axis == 'x':
                cx, cy = side * 8.9, t
            else:
                cx, cy = t, side * 8.9
            lathe("Column_%s%d_%d" % (axis, side, k),
                  [(0.0, 0.0), (0.30, 0.0), (0.30, 0.16), (0.24, 0.24), (0.21, 0.34),
                   (0.205, 1.60), (0.19, 2.85), (0.235, 2.95), (0.22, 3.02),
                   (0.30, 3.12), (0.30, 3.26), (0.0, 3.26)],
                  [M_STONE], segments=24, location=(cx, cy, 0.02))
        if axis == 'x':
            bm_box(bm_beam, (side * 8.9, 0, 3.46), (0.60, 18.0, 0.36), 0)
        else:
            bm_box(bm_beam, (0, side * 8.9, 3.46), (18.0, 0.60, 0.36), 0)
        finish(bm_beam, "Architrave_%s%d" % (axis, side), [M_STONE_DK], location=(0, 0, 0.02))

# ------------------------------------------------------------------ lighting
sun_data = bpy.data.lights.new("Sun", 'SUN')
sun_data.energy = 4.0
sun_data.angle = math.radians(1.5)
sun_data.color = (1.0, 0.94, 0.84)
sun = bpy.data.objects.new("Sun", sun_data)
sun.rotation_euler = (math.radians(52), 0.0, math.radians(38))
sun.location = (0, 0, 20)
link(sun)

bounce = bpy.data.lights.new("SkyFill", 'AREA')
bounce.shape = 'SQUARE'
bounce.size = 18.0
bounce.energy = 900.0
bounce.color = (0.62, 0.74, 1.0)
bo = bpy.data.objects.new("SkyFill", bounce)
bo.location = (0, 0, 14.0)
link(bo)

world = bpy.data.worlds.new("CourtyardWorld")
world.use_nodes = True
nt = world.node_tree
bg = nt.nodes["Background"]
bg.inputs["Strength"].default_value = 1.0
try:
    sky = nt.nodes.new("ShaderNodeTexSky")
    sky.sky_type = 'NISHITA'
    sky.sun_elevation = math.radians(52)
    sky.sun_rotation = math.radians(38)
    nt.links.new(sky.outputs["Color"], bg.inputs["Color"])
except Exception:
    bg.inputs["Color"].default_value = (0.35, 0.52, 0.85, 1.0)
bpy.context.scene.world = world

# ------------------------------------------------------------------- camera
cam_data = bpy.data.cameras.new("CourtyardCam")
cam_data.lens = 28.0
cam_data.clip_end = 500.0
cam = bpy.data.objects.new("CourtyardCam", cam_data)
cam.location = (11.5, -12.5, 6.6)
link(cam)
look_at(cam, (0.0, 0.0, 1.6))
bpy.context.scene.camera = cam

bpy.context.view_layer.update()
print("claude-047: courtyard built with %d objects" % len(bpy.data.objects))
