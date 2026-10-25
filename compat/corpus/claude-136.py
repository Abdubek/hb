"""claude-136 - A loft workshop with workbench, pegboard tools, storage drawers and task lamps."""
import bpy, bmesh, math, random
from mathutils import Vector, Matrix

random.seed(20250909)
TAU = math.tau

# ---------------------------------------------------------------- scene setup
bpy.ops.wm.read_factory_settings(use_empty=True)
scene = bpy.context.scene
try:
    scene.render.engine = 'CYCLES'
    scene.cycles.samples = 160
    scene.cycles.preview_samples = 24
except Exception:
    pass
scene.render.resolution_x, scene.render.resolution_y = 1800, 1200
scene.unit_settings.system = 'METRIC'

COLLS = {}
for _n in ("Structure", "Floor", "Bench", "Pegboard", "Tools",
           "Storage", "Lamps", "Props", "Lights"):
    c = bpy.data.collections.new(_n)
    scene.collection.children.link(c)
    COLLS[_n] = c

# ---------------------------------------------------------------- materials
def make_mat(name, color, rough=0.5, metallic=0.0, emit=None, emit_str=0.0,
             transmission=0.0, ior=1.45, coat=0.0):
    mat = bpy.data.materials.new(name)
    mat.use_nodes = True
    b = mat.node_tree.nodes["Principled BSDF"]
    b.inputs["Base Color"].default_value = (*color, 1.0)
    b.inputs["Roughness"].default_value = rough
    b.inputs["Metallic"].default_value = metallic
    b.inputs["IOR"].default_value = ior
    if "Coat Weight" in b.inputs:
        b.inputs["Coat Weight"].default_value = coat
    if "Transmission Weight" in b.inputs:
        b.inputs["Transmission Weight"].default_value = transmission
    if emit is not None:
        b.inputs["Emission Color"].default_value = (*emit, 1.0)
        b.inputs["Emission Strength"].default_value = emit_str
    return mat


def make_wood(name, c_light, c_dark, scale=2.4, distortion=9.0, rough=0.42,
              bump=0.25, band_dir='X'):
    """Procedural grained wood (wave + noise), no external assets."""
    mat = bpy.data.materials.new(name)
    mat.use_nodes = True
    nt = mat.node_tree
    nodes, links = nt.nodes, nt.links
    nodes.clear()
    out = nodes.new("ShaderNodeOutputMaterial"); out.location = (620, 0)
    bsdf = nodes.new("ShaderNodeBsdfPrincipled"); bsdf.location = (320, 0)
    coord = nodes.new("ShaderNodeTexCoord"); coord.location = (-760, 0)
    mapn = nodes.new("ShaderNodeMapping"); mapn.location = (-580, 0)
    mapn.inputs["Scale"].default_value = (1.0, 1.0, 1.0)
    wave = nodes.new("ShaderNodeTexWave"); wave.location = (-380, 120)
    wave.wave_type = 'BANDS'
    wave.bands_direction = band_dir
    wave.wave_profile = 'SIN'
    wave.inputs["Scale"].default_value = scale
    wave.inputs["Distortion"].default_value = distortion
    wave.inputs["Detail"].default_value = 4.0
    wave.inputs["Detail Scale"].default_value = 1.6
    wave.inputs["Detail Roughness"].default_value = 0.6
    ramp = nodes.new("ShaderNodeValToRGB"); ramp.location = (-170, 120)
    ramp.color_ramp.elements[0].position = 0.30
    ramp.color_ramp.elements[0].color = (*c_dark, 1.0)
    ramp.color_ramp.elements[1].position = 0.78
    ramp.color_ramp.elements[1].color = (*c_light, 1.0)
    noise = nodes.new("ShaderNodeTexNoise"); noise.location = (-380, -220)
    noise.inputs["Scale"].default_value = 28.0
    noise.inputs["Detail"].default_value = 6.0
    rmap = nodes.new("ShaderNodeMapRange"); rmap.location = (-170, -220)
    rmap.inputs["To Min"].default_value = max(0.05, rough - 0.12)
    rmap.inputs["To Max"].default_value = min(1.0, rough + 0.12)
    bmp = nodes.new("ShaderNodeBump"); bmp.location = (90, -160)
    bmp.inputs["Strength"].default_value = bump
    bmp.inputs["Distance"].default_value = 0.02
    links.new(coord.outputs["Object"], mapn.inputs["Vector"])
    links.new(mapn.outputs["Vector"], wave.inputs["Vector"])
    links.new(mapn.outputs["Vector"], noise.inputs["Vector"])
    links.new(wave.outputs["Fac"], ramp.inputs["Fac"])
    links.new(ramp.outputs["Color"], bsdf.inputs["Base Color"])
    links.new(noise.outputs["Fac"], rmap.inputs["Value"])
    links.new(rmap.outputs["Result"], bsdf.inputs["Roughness"])
    links.new(wave.outputs["Fac"], bmp.inputs["Height"])
    links.new(bmp.outputs["Normal"], bsdf.inputs["Normal"])
    links.new(bsdf.outputs["BSDF"], out.inputs["Surface"])
    return mat


M = {
    "beech":     make_wood("W_BenchTop", (0.72, 0.53, 0.31), (0.44, 0.28, 0.14),
                           scale=3.0, distortion=11.0, rough=0.36, bump=0.35),
    "pine":      make_wood("W_Pine", (0.76, 0.61, 0.40), (0.52, 0.37, 0.21),
                           scale=2.2, distortion=8.0, rough=0.5),
    "floor_a":   make_wood("W_FloorA", (0.60, 0.42, 0.25), (0.36, 0.22, 0.11),
                           scale=1.6, distortion=7.0, rough=0.34, band_dir='Y'),
    "floor_b":   make_wood("W_FloorB", (0.53, 0.36, 0.21), (0.30, 0.18, 0.09),
                           scale=2.0, distortion=9.0, rough=0.40, band_dir='Y'),
    "floor_c":   make_wood("W_FloorC", (0.66, 0.48, 0.29), (0.40, 0.25, 0.13),
                           scale=1.3, distortion=6.0, rough=0.30, band_dir='Y'),
    "rafter":    make_wood("W_Rafter", (0.50, 0.37, 0.24), (0.31, 0.21, 0.12),
                           scale=1.4, distortion=6.0, rough=0.62, bump=0.5),
    "wall":      make_mat("Wall_Painted", (0.80, 0.79, 0.74), rough=0.72),
    "wall_edge": make_mat("Wall_Shadowline", (0.55, 0.54, 0.50), rough=0.8),
    "roofboard": make_mat("RoofBoard", (0.68, 0.65, 0.59), rough=0.78),
    "peg":       make_mat("Pegboard_MDF", (0.74, 0.55, 0.34), rough=0.68),
    "hole":      make_mat("Pegboard_Hole", (0.05, 0.04, 0.035), rough=0.9),
    "steel":     make_mat("Steel", (0.62, 0.63, 0.65), rough=0.34, metallic=1.0),
    "steel_dk":  make_mat("Steel_Dark", (0.26, 0.27, 0.29), rough=0.48, metallic=1.0),
    "chrome":    make_mat("Chrome", (0.85, 0.86, 0.88), rough=0.12, metallic=1.0),
    "castiron":  make_mat("CastIron", (0.13, 0.13, 0.14), rough=0.55, metallic=0.9),
    "brass":     make_mat("Brass", (0.76, 0.60, 0.28), rough=0.30, metallic=1.0),
    "rubber":    make_mat("Rubber", (0.09, 0.09, 0.10), rough=0.88),
    "red":       make_mat("Plastic_Red", (0.55, 0.06, 0.05), rough=0.34, coat=0.3),
    "blue":      make_mat("Plastic_Blue", (0.06, 0.16, 0.45), rough=0.34, coat=0.3),
    "yellow":    make_mat("Plastic_Yellow", (0.72, 0.52, 0.04), rough=0.36, coat=0.3),
    "green_en":  make_mat("Enamel_Green", (0.07, 0.22, 0.17), rough=0.24, coat=0.5),
    "cab_paint": make_mat("Cabinet_Teal", (0.10, 0.26, 0.27), rough=0.35, metallic=0.35),
    "cab_dark":  make_mat("Cabinet_Shadow", (0.05, 0.13, 0.14), rough=0.5, metallic=0.3),
    "glass":     make_mat("Glass", (0.92, 0.95, 0.97), rough=0.03, transmission=1.0, ior=1.5),
    "bulb":      make_mat("Bulb_Emissive", (1.0, 0.86, 0.66), rough=0.4,
                          emit=(1.0, 0.80, 0.55), emit_str=28.0),
    "shade_in":  make_mat("Shade_Inner", (1.0, 0.95, 0.88), rough=0.45,
                          emit=(1.0, 0.90, 0.74), emit_str=6.0),
    "concrete":  make_mat("Concrete", (0.30, 0.30, 0.30), rough=0.85),
    "canvas":    make_mat("Canvas", (0.46, 0.42, 0.33), rough=0.85),
    "glassjar":  make_mat("JarGlass", (0.90, 0.93, 0.92), rough=0.10, transmission=1.0, ior=1.5),
    "screws":    make_mat("Screws", (0.44, 0.42, 0.38), rough=0.55, metallic=0.8),
    "paper":     make_mat("Paper", (0.86, 0.84, 0.78), rough=0.8),
}

# ---------------------------------------------------------------- primitives
def obj_from_bm(name, bm, mat=None, loc=(0, 0, 0), rot=(0, 0, 0),
                coll="Props", smooth='NONE'):
    me = bpy.data.meshes.new(name)
    bm.normal_update()
    bm.to_mesh(me)
    bm.free()
    if smooth == 'ALL':
        for p in me.polygons:
            p.use_smooth = True
    elif smooth == 'SIDES':
        for p in me.polygons:
            p.use_smooth = abs(p.normal.z) < 0.9
    ob = bpy.data.objects.new(name, me)
    ob.location = loc
    ob.rotation_euler = rot
    if mat is not None:
        me.materials.append(mat)
    COLLS[coll].objects.link(ob)
    return ob


def add_box(name, size, loc, rot=(0, 0, 0), mat=None, coll="Props", bevel=0.0):
    bm = bmesh.new()
    bmesh.ops.create_cube(bm, size=1.0)
    bmesh.ops.scale(bm, vec=Vector(size), verts=bm.verts)
    if bevel > 0.0:
        off = min(bevel, min(size) * 0.35)
        bmesh.ops.bevel(bm, geom=bm.verts[:] + bm.edges[:] + bm.faces[:],
                        offset=off, segments=2, profile=0.5,
                        affect='EDGES', clamp_overlap=True)
    return obj_from_bm(name, bm, mat, loc, rot, coll)


def add_cyl(name, radius, depth, loc, rot=(0, 0, 0), mat=None, coll="Props",
            segs=20, cap=True, radius2=None):
    bm = bmesh.new()
    bmesh.ops.create_cone(bm, cap_ends=cap, cap_tris=False, segments=segs,
                          radius1=radius,
                          radius2=radius if radius2 is None else radius2,
                          depth=depth)
    return obj_from_bm(name, bm, mat, loc, rot, coll, smooth='SIDES')


def add_sphere(name, radius, loc, mat=None, coll="Props", subd=3):
    bm = bmesh.new()
    bmesh.ops.create_icosphere(bm, subdivisions=subd, radius=radius)
    return obj_from_bm(name, bm, mat, loc, (0, 0, 0), coll, smooth='ALL')


def torus_bmesh(major, minor, mseg=22, nseg=10):
    bm = bmesh.new()
    bmesh.ops.create_circle(bm, cap_ends=False, cap_tris=False,
                            segments=nseg, radius=minor,
                            matrix=Matrix.Translation((major, 0, 0)) @
                            Matrix.Rotation(math.pi / 2, 4, 'X'))
    geom = bm.verts[:] + bm.edges[:]
    bmesh.ops.spin(bm, geom=geom, cent=(0, 0, 0), axis=(0, 0, 1),
                   dvec=(0, 0, 0), angle=TAU, steps=mseg, use_merge=True)
    return bm


def add_torus(name, major, minor, loc, rot=(0, 0, 0), mat=None, coll="Props",
              mseg=22, nseg=10, squash=None):
    bm = torus_bmesh(major, minor, mseg, nseg)
    if squash:
        bmesh.ops.scale(bm, vec=Vector(squash), verts=bm.verts)
    return obj_from_bm(name, bm, mat, loc, rot, coll, smooth='ALL')


def add_prism(name, pts, thickness, loc, rot=(0, 0, 0), mat=None,
              coll="Props", bevel=0.0):
    """Extrude a 2D outline (given in the local XZ plane) along local Y."""
    bm = bmesh.new()
    verts = [bm.verts.new((p[0], -thickness * 0.5, p[1])) for p in pts]
    face = bm.faces.new(verts)
    res = bmesh.ops.extrude_face_region(bm, geom=[face])
    new_verts = [e for e in res["geom"] if isinstance(e, bmesh.types.BMVert)]
    bmesh.ops.translate(bm, verts=new_verts, vec=(0, thickness, 0))
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    if bevel > 0.0:
        bmesh.ops.bevel(bm, geom=bm.verts[:] + bm.edges[:] + bm.faces[:],
                        offset=bevel, segments=2, profile=0.5,
                        affect='EDGES', clamp_overlap=True)
    return obj_from_bm(name, bm, mat, loc, rot, coll)


# ---------------------------------------------------------------- loft shell
HALF_X = 3.5           # eaves at +/- 3.5
EAVE_Z = 1.10          # knee wall height
RIDGE_Z = 3.00         # ridge height at x = 0
ROOM_Y = 3.0           # gable walls at +/- 3.0
SLOPE_LEN = math.hypot(HALF_X, RIDGE_Z - EAVE_Z)
SLOPE_ANG = math.atan2(RIDGE_Z - EAVE_Z, HALF_X)


def roof_profile(x):
    return RIDGE_Z - abs(x) / HALF_X * (RIDGE_Z - EAVE_Z)


# --- floorboards
add_box("FloorSlab", (2 * HALF_X + 0.4, 2 * ROOM_Y + 0.4, 0.12),
        (0, 0, -0.07), mat=M["concrete"], coll="Floor")

plank_w, plank_gap = 0.215, 0.007
n_planks = int((2 * HALF_X) // (plank_w + plank_gap))
floor_mats = [M["floor_a"], M["floor_b"], M["floor_c"]]
x0 = -HALF_X
for i in range(n_planks):
    xc = x0 + plank_w * 0.5 + i * (plank_w + plank_gap)
    add_box("Plank_%02d" % i, (plank_w, 2 * ROOM_Y, 0.032),
            (xc, 0, 0.016), mat=floor_mats[i % 3], coll="Floor")
for j, yj in enumerate((-1.35, 1.9)):
    add_box("PlankJoint_%d" % j, (2 * HALF_X, 0.012, 0.034),
            (0, yj, 0.017), mat=M["wall_edge"], coll="Floor")

# --- knee walls + skirting
for s in (-1, 1):
    add_box("KneeWall_%d" % s, (0.10, 2 * ROOM_Y, EAVE_Z),
            (s * (HALF_X + 0.05), 0, EAVE_Z * 0.5),
            mat=M["wall"], coll="Structure")
    add_box("KneePlate_%d" % s, (0.16, 2 * ROOM_Y, 0.09),
            (s * (HALF_X + 0.02), 0, EAVE_Z + 0.045),
            mat=M["rafter"], coll="Structure")
    add_box("Skirting_%d" % s, (0.03, 2 * ROOM_Y, 0.11),
            (s * (HALF_X - 0.015), 0, 0.055),
            mat=M["wall_edge"], coll="Structure")

# --- sloped roof planes, rafters, ridge beam
for s in (-1, 1):
    ang = -SLOPE_ANG * s
    mid = Vector((s * HALF_X * 0.5, 0.0, (EAVE_Z + RIDGE_Z) * 0.5))
    add_box("RoofDeck_%d" % s, (SLOPE_LEN, 2 * ROOM_Y, 0.07),
            mid, rot=(0, ang, 0), mat=M["roofboard"], coll="Structure")
    nrm = Vector((math.sin(ang), 0.0, math.cos(ang)))
    for k in range(9):
        yk = -2.6 + k * 0.65
        add_box("Rafter_%d_%d" % (s, k), (SLOPE_LEN - 0.05, 0.075, 0.16),
                mid + Vector((0, yk, 0)) - nrm * 0.115,
                rot=(0, ang, 0), mat=M["rafter"], coll="Structure")
add_box("RidgeBeam", (0.15, 2 * ROOM_Y, 0.24), (0, 0, RIDGE_Z - 0.14),
        mat=M["rafter"], coll="Structure")
for k in range(5):
    add_box("Purlin_%d" % k, (0.09, 0.09, 1.0),
            (0, -2.2 + k * 1.1, RIDGE_Z - 0.30), rot=(math.pi / 2, 0, 0),
            mat=M["rafter"], coll="Structure")

# --- far gable wall (behind camera) as a single extruded profile
add_prism("GableWall_Back",
          [(-HALF_X, 0.0), (HALF_X, 0.0), (HALF_X, EAVE_Z),
           (0.0, RIDGE_Z), (-HALF_X, EAVE_Z)],
          0.09, (0, -(ROOM_Y + 0.045), 0), mat=M["wall"], coll="Structure")

# --- working gable wall (behind bench): vertical boarding + window opening
WIN = dict(x0=0.35, x1=1.65, z0=1.00, z1=1.95)
WALL_Y = ROOM_Y - 0.03
slat_w = 0.235
x = -HALF_X
idx = 0
while x < HALF_X - 0.02:
    w = min(slat_w, HALF_X - x)
    top = min(roof_profile(x), roof_profile(x + w)) - 0.012
    xc = x + w * 0.5
    overlaps = (x + w > WIN["x0"]) and (x < WIN["x1"])
    if overlaps:
        add_box("Slat_%02d_lo" % idx, (w, 0.05, WIN["z0"]),
                (xc, WALL_Y, WIN["z0"] * 0.5), mat=M["wall"], coll="Structure")
        if top > WIN["z1"] + 0.03:
            h = top - WIN["z1"]
            add_box("Slat_%02d_hi" % idx, (w, 0.05, h),
                    (xc, WALL_Y, WIN["z1"] + h * 0.5),
                    mat=M["wall"], coll="Structure")
    else:
        add_box("Slat_%02d" % idx, (w, 0.05, top),
                (xc, WALL_Y, top * 0.5), mat=M["wall"], coll="Structure")
    x += w + plank_gap
    idx += 1
add_box("WallPlate", (2 * HALF_X, 0.09, 0.10), (0, ROOM_Y + 0.03, 0.05),
        mat=M["rafter"], coll="Structure")

# --- window in the gable
wx = (WIN["x0"] + WIN["x1"]) * 0.5
wz = (WIN["z0"] + WIN["z1"]) * 0.5
ww = WIN["x1"] - WIN["x0"]
wh = WIN["z1"] - WIN["z0"]
fr = 0.055
add_box("WinGlass", (ww - 0.02, 0.012, wh - 0.02), (wx, WALL_Y + 0.01, wz),
        mat=M["glass"], coll="Structure")
for dz in (-1, 1):
    add_box("WinFrameH_%d" % dz, (ww + 2 * fr, 0.10, fr),
            (wx, WALL_Y, wz + dz * (wh * 0.5 + fr * 0.5)),
            mat=M["wall"], coll="Structure", bevel=0.006)
for dx in (-1, 1):
    add_box("WinFrameV_%d" % dx, (fr, 0.10, wh),
            (wx + dx * (ww * 0.5 + fr * 0.5), WALL_Y, wz),
            mat=M["wall"], coll="Structure", bevel=0.006)
add_box("WinMullionV", (0.032, 0.06, wh), (wx, WALL_Y - 0.01, wz),
        mat=M["wall"], coll="Structure")
add_box("WinMullionH", (ww, 0.06, 0.028), (wx, WALL_Y - 0.01, wz),
        mat=M["wall"], coll="Structure")
add_box("WinSill", (ww + 0.16, 0.20, 0.035), (wx, WALL_Y - 0.055, WIN["z0"] - 0.05),
        mat=M["pine"], coll="Structure", bevel=0.008)

# ---------------------------------------------------------------- workbench
BX0, BX1 = -2.25, 0.35
BENCH_W = BX1 - BX0
BENCH_D = 0.72
BENCH_Y = ROOM_Y - 0.06 - BENCH_D * 0.5
TOP_Z = 0.90
TOP_T = 0.075
bcx = (BX0 + BX1) * 0.5

add_box("BenchTop", (BENCH_W, BENCH_D, TOP_T), (bcx, BENCH_Y, TOP_Z - TOP_T * 0.5),
        mat=M["beech"], coll="Bench", bevel=0.008)
add_box("BenchTopLip", (BENCH_W, 0.03, 0.035),
        (bcx, BENCH_Y - BENCH_D * 0.5 - 0.015, TOP_Z - TOP_T - 0.017),
        mat=M["beech"], coll="Bench")

leg_h = TOP_Z - TOP_T
for sx in (-1, 1):
    for sy in (-1, 1):
        add_box("BenchLeg_%d%d" % (sx, sy), (0.095, 0.095, leg_h),
                (bcx + sx * (BENCH_W * 0.5 - 0.13),
                 BENCH_Y + sy * (BENCH_D * 0.5 - 0.11), leg_h * 0.5),
                mat=M["pine"], coll="Bench", bevel=0.006)
for sy in (-1, 1):
    add_box("BenchRail_%d" % sy, (BENCH_W - 0.26, 0.05, 0.14),
            (bcx, BENCH_Y + sy * (BENCH_D * 0.5 - 0.11), leg_h - 0.10),
            mat=M["pine"], coll="Bench")
for sx in (-1, 1):
    add_box("BenchEndRail_%d" % sx, (0.05, BENCH_D - 0.22, 0.14),
            (bcx + sx * (BENCH_W * 0.5 - 0.13), BENCH_Y, leg_h - 0.10),
            mat=M["pine"], coll="Bench")
    add_box("BenchStretch_%d" % sx, (0.06, BENCH_D - 0.22, 0.08),
            (bcx + sx * (BENCH_W * 0.5 - 0.13), BENCH_Y, 0.22),
            mat=M["pine"], coll="Bench")
add_box("BenchShelf", (BENCH_W - 0.30, BENCH_D - 0.24, 0.028),
        (bcx, BENCH_Y, 0.27), mat=M["pine"], coll="Bench")

for i in range(7):
    add_cyl("DogHole_%d" % i, 0.011, 0.012,
            (BX0 + 0.35 + i * 0.30, BENCH_Y - 0.16, TOP_Z - 0.004),
            mat=M["hole"], coll="Bench", segs=10)

# --- cast iron vise on the front-left corner
vx, vy = BX0 + 0.34, BENCH_Y - BENCH_D * 0.5 - 0.03
add_box("ViseBody", (0.24, 0.16, 0.13), (vx, vy, TOP_Z - 0.10),
        mat=M["castiron"], coll="Bench", bevel=0.01)
add_box("ViseJawFixed", (0.24, 0.045, 0.10), (vx, vy + 0.10, TOP_Z - 0.055),
        mat=M["castiron"], coll="Bench", bevel=0.006)
add_box("ViseJawMove", (0.24, 0.045, 0.10), (vx, vy - 0.03, TOP_Z - 0.055),
        mat=M["castiron"], coll="Bench", bevel=0.006)
for f, yj in (("A", 0.079), ("B", -0.052)):
    add_box("ViseFace_%s" % f, (0.22, 0.018, 0.09), (vx, vy + yj, TOP_Z - 0.055),
            mat=M["beech"], coll="Bench")
add_cyl("ViseScrew", 0.016, 0.30, (vx, vy - 0.10, TOP_Z - 0.095),
        rot=(math.pi / 2, 0, 0), mat=M["steel"], coll="Bench", segs=14)
add_cyl("ViseHandleBar", 0.011, 0.30, (vx, vy - 0.245, TOP_Z - 0.095),
        rot=(0, math.pi / 2, 0), mat=M["steel"], coll="Bench", segs=14)
for sx in (-1, 1):
    add_sphere("ViseKnob_%d" % sx, 0.022,
               (vx + sx * 0.155, vy - 0.245, TOP_Z - 0.095),
               mat=M["steel_dk"], coll="Bench", subd=2)


# --- drawer fronts (shared by every drawer unit)
def drawer_front(name, w, h, loc, coll, face_mat, handle='BAR', depth=0.022):
    add_box(name, (w, depth, h), loc, mat=face_mat, coll=coll, bevel=0.005)
    y = loc[1] - depth * 0.5 - 0.012
    if handle == 'BAR':
        add_cyl(name + "_Handle", 0.010, w * 0.45, (loc[0], y - 0.012, loc[2]),
                rot=(0, math.pi / 2, 0), mat=M["chrome"], coll=coll, segs=12)
        for sx in (-1, 1):
            add_cyl(name + "_Stem%d" % sx, 0.007, 0.026,
                    (loc[0] + sx * w * 0.225, y + 0.001, loc[2]),
                    rot=(math.pi / 2, 0, 0), mat=M["chrome"], coll=coll, segs=10)
    elif handle == 'CUP':
        add_box(name + "_Pull", (w * 0.34, 0.024, 0.030),
                (loc[0], y, loc[2]), mat=M["steel_dk"], coll=coll, bevel=0.004)


dbx0, dbx1 = -0.62, 0.28
dbw = dbx1 - dbx0
dby = BENCH_Y
add_box("BenchDrawerCase", (dbw, BENCH_D - 0.16, leg_h - 0.34),
        ((dbx0 + dbx1) * 0.5, dby, 0.31 + (leg_h - 0.34) * 0.5),
        mat=M["pine"], coll="Storage")
for i in range(3):
    zc = 0.42 + i * 0.155
    drawer_front("BenchDrawer_%d" % i, dbw - 0.03, 0.135,
                 ((dbx0 + dbx1) * 0.5, dby - (BENCH_D - 0.16) * 0.5, zc),
                 "Storage", M["beech"], handle='CUP')

# ---------------------------------------------------------------- pegboard
PB_X0, PB_X1 = -2.05, -0.20
PB_Z0, PB_Z1 = 1.05, 1.80
PB_Y = ROOM_Y - 0.075
PB_FRONT = PB_Y - 0.010
pbw, pbh = PB_X1 - PB_X0, PB_Z1 - PB_Z0
pbcx, pbcz = (PB_X0 + PB_X1) * 0.5, (PB_Z0 + PB_Z1) * 0.5

for sx in (-1, 1):
    add_box("PegBatten_%d" % sx, (0.04, 0.03, pbh),
            (pbcx + sx * (pbw * 0.5 - 0.03), PB_Y + 0.022, pbcz),
            mat=M["pine"], coll="Pegboard")
add_box("Pegboard", (pbw, 0.014, pbh), (pbcx, PB_Y, pbcz),
        mat=M["peg"], coll="Pegboard")
for sz in (-1, 1):
    add_box("PegTrim_%d" % sz, (pbw + 0.05, 0.028, 0.03),
            (pbcx, PB_Y - 0.008, pbcz + sz * (pbh * 0.5 + 0.015)),
            mat=M["pine"], coll="Pegboard", bevel=0.004)

bm_holes = bmesh.new()
step = 0.06
nx = int((pbw - 0.06) / step)
nz = int((pbh - 0.06) / step)
for i in range(nx + 1):
    for k in range(nz + 1):
        hx = PB_X0 + 0.03 + i * step
        hz = PB_Z0 + 0.03 + k * step
        bmesh.ops.create_circle(
            bm_holes, cap_ends=True, cap_tris=False, segments=8, radius=0.0115,
            matrix=Matrix.Translation((hx, PB_FRONT - 0.001, hz)) @
            Matrix.Rotation(-math.pi / 2, 4, 'X'))
obj_from_bm("PegboardHoles", bm_holes, M["hole"], coll="Pegboard")


def add_hook(x, z, name, out=0.045):
    add_cyl(name + "_hook", 0.0045, out, (x, PB_FRONT - out * 0.5, z),
            rot=(math.pi / 2, 0, 0), mat=M["steel"], coll="Tools", segs=8)
    add_cyl(name + "_hooktip", 0.0045, 0.022, (x, PB_FRONT - out, z - 0.011),
            mat=M["steel"], coll="Tools", segs=8)


# ---------------------------------------------------------------- hand tools
TY = PB_FRONT - 0.05


def tool_hammer(x, ztop, name="Hammer", claw=True):
    add_hook(x, ztop + 0.02, name)
    add_cyl(name + "_head", 0.023, 0.115, (x, TY, ztop),
            rot=(0, math.pi / 2, 0), mat=M["steel_dk"], coll="Tools", segs=16)
    add_cyl(name + "_face", 0.024, 0.014, (x + 0.062, TY, ztop),
            rot=(0, math.pi / 2, 0), mat=M["chrome"], coll="Tools", segs=16)
    if claw:
        add_prism(name + "_claw",
                  [(-0.055, 0.018), (-0.115, 0.010), (-0.128, -0.020),
                   (-0.100, -0.014), (-0.055, -0.018)],
                  0.030, (x, TY, ztop), mat=M["steel_dk"], coll="Tools")
    add_cyl(name + "_handle", 0.017, 0.28, (x, TY, ztop - 0.155),
            mat=M["pine"], coll="Tools", segs=14, radius2=0.021)
    add_cyl(name + "_grip", 0.020, 0.10, (x, TY, ztop - 0.245),
            mat=M["rubber"], coll="Tools", segs=14)


def tool_mallet(x, ztop, name="Mallet"):
    add_hook(x, ztop + 0.02, name)
    add_cyl(name + "_head", 0.037, 0.115, (x, TY, ztop),
            rot=(0, math.pi / 2, 0), mat=M["rubber"], coll="Tools", segs=18)
    add_cyl(name + "_handle", 0.015, 0.24, (x, TY, ztop - 0.13),
            mat=M["pine"], coll="Tools", segs=12)


def tool_screwdriver(x, ztop, col, length=0.15, name="Driver"):
    add_hook(x, ztop + 0.015, name)
    add_cyl(name + "_handle", 0.017, 0.095, (x, TY, ztop - 0.048),
            mat=col, coll="Tools", segs=14, radius2=0.013)
    add_cyl(name + "_collar", 0.008, 0.02, (x, TY, ztop - 0.105),
            mat=M["chrome"], coll="Tools", segs=10)
    add_cyl(name + "_shaft", 0.005, length, (x, TY, ztop - 0.115 - length * 0.5),
            mat=M["chrome"], coll="Tools", segs=10)
    add_box(name + "_tip", (0.012, 0.004, 0.02),
            (x, TY, ztop - 0.118 - length), mat=M["steel_dk"], coll="Tools")


def tool_wrench(x, ztop, length=0.24, name="Wrench"):
    add_hook(x, ztop + 0.015, name)
    add_box(name + "_shank", (0.024, 0.008, length),
            (x, TY, ztop - length * 0.5 - 0.02),
            mat=M["chrome"], coll="Tools", bevel=0.004)
    add_torus(name + "_ring", 0.026, 0.008, (x, TY, ztop - length - 0.045),
              rot=(math.pi / 2, 0, 0), mat=M["chrome"], coll="Tools",
              mseg=18, nseg=8, squash=(1.0, 1.0, 0.5))
    for sx in (-1, 1):
        add_box(name + "_jaw%d" % sx, (0.011, 0.009, 0.045),
                (x + sx * 0.019, TY, ztop - 0.012),
                mat=M["chrome"], coll="Tools")
    add_box(name + "_jawback", (0.05, 0.009, 0.014), (x, TY, ztop - 0.038),
            mat=M["chrome"], coll="Tools")


def tool_pliers(x, ztop, name="Pliers"):
    add_hook(x, ztop + 0.015, name)
    for sx in (-1, 1):
        add_box(name + "_handle%d" % sx, (0.016, 0.010, 0.155),
                (x + sx * 0.021, TY, ztop - 0.105),
                rot=(0, math.radians(-7 * sx), 0),
                mat=M["red"], coll="Tools", bevel=0.004)
        add_box(name + "_leg%d" % sx, (0.013, 0.010, 0.070),
                (x + sx * 0.007, TY, ztop - 0.012),
                rot=(0, math.radians(6 * sx), 0),
                mat=M["steel_dk"], coll="Tools")
    add_cyl(name + "_pivot", 0.008, 0.026, (x, TY, ztop - 0.045),
            rot=(math.pi / 2, 0, 0), mat=M["chrome"], coll="Tools", segs=10)
    add_prism(name + "_nose", [(-0.012, 0.0), (0.012, 0.0), (0.004, 0.055),
                               (-0.004, 0.055)],
              0.014, (x, TY, ztop + 0.005), mat=M["steel_dk"], coll="Tools")


def tool_level(xc, zc, length=0.55, name="Level"):
    add_box(name + "_body", (length, 0.030, 0.055), (xc, TY, zc),
            mat=M["yellow"], coll="Tools", bevel=0.006)
    for dx in (-0.13, 0.13):
        add_box(name + "_vial%s" % ("a" if dx < 0 else "b"),
                (0.05, 0.034, 0.026), (xc + dx, TY, zc),
                mat=M["shade_in"], coll="Tools")
    for sx in (-1, 1):
        add_hook(xc + sx * length * 0.4, zc + 0.045, name + "%d" % sx, out=0.05)


def tool_tape(x, z, name="Tape"):
    add_hook(x, z + 0.05, name)
    add_cyl(name + "_body", 0.047, 0.052, (x, TY, z),
            rot=(math.pi / 2, 0, 0), mat=M["yellow"], coll="Tools", segs=22)
    add_cyl(name + "_hub", 0.020, 0.056, (x, TY, z),
            rot=(math.pi / 2, 0, 0), mat=M["steel_dk"], coll="Tools", segs=14)
    add_box(name + "_blade", (0.024, 0.004, 0.05), (x, TY, z + 0.06),
            mat=M["chrome"], coll="Tools")


def tool_saw(x, ztop, name="Saw"):
    add_hook(x, ztop + 0.02, name)
    ang = math.radians(62)
    add_prism(name + "_blade",
              [(0.02, -0.010), (0.56, -0.055), (0.56, -0.115), (0.02, -0.105)],
              0.004, (x, TY, ztop), rot=(0, ang, 0),
              mat=M["chrome"], coll="Tools")
    add_prism(name + "_handle",
              [(-0.10, 0.03), (0.03, 0.02), (0.04, -0.10), (-0.09, -0.12),
               (-0.13, -0.05)],
              0.028, (x, TY, ztop), rot=(0, ang, 0),
              mat=M["pine"], coll="Tools", bevel=0.008)
    add_torus(name + "_grip", 0.032, 0.010, (x - 0.02, TY, ztop - 0.05),
              rot=(math.pi / 2, ang, 0), mat=M["hole"], coll="Tools",
              mseg=16, nseg=8)


def tool_clamp(x, ztop, name="CClamp"):
    add_hook(x, ztop + 0.015, name)
    add_prism(name + "_frame",
              [(-0.012, 0.0), (0.075, 0.0), (0.075, -0.022), (0.012, -0.022),
               (0.012, -0.100), (0.075, -0.100), (0.075, -0.122),
               (-0.012, -0.122)],
              0.022, (x, TY, ztop), mat=M["castiron"], coll="Tools", bevel=0.004)
    add_cyl(name + "_screw", 0.008, 0.09, (x + 0.062, TY, ztop - 0.075),
            mat=M["steel"], coll="Tools", segs=12)
    add_cyl(name + "_bar", 0.006, 0.075, (x + 0.062, TY, ztop - 0.122),
            rot=(0, math.pi / 2, 0), mat=M["steel"], coll="Tools", segs=10)
    add_cyl(name + "_pad", 0.014, 0.010, (x + 0.062, TY, ztop - 0.036),
            mat=M["steel_dk"], coll="Tools", segs=12)


tool_hammer(-1.96, 1.70)
tool_mallet(-1.79, 1.69)
tool_screwdriver(-1.60, 1.72, M["red"], 0.16)
tool_screwdriver(-1.50, 1.72, M["yellow"], 0.13)
tool_screwdriver(-1.40, 1.72, M["blue"], 0.19)
tool_pliers(-1.22, 1.71)
tool_wrench(-1.04, 1.72, 0.23, "WrenchA")
tool_wrench(-0.93, 1.72, 0.18, "WrenchB")
tool_tape(-0.75, 1.60)
tool_saw(-0.47, 1.73)
tool_level(-1.30, 1.16)
tool_clamp(-0.62, 1.20)
add_torus("WireCoil", 0.085, 0.016, (-0.90, TY + 0.015, 1.28),
          rot=(math.pi / 2, 0, 0), mat=M["steel_dk"], coll="Tools",
          mseg=24, nseg=8, squash=(1.0, 1.0, 0.6))
add_hook(-0.90, 1.37, "WireCoil")

# small parts organiser hanging at the right of the board
org_x, org_z = -0.34, 1.42
add_box("Organiser_Case", (0.20, 0.075, 0.26), (org_x, PB_FRONT - 0.042, org_z),
        mat=M["steel_dk"], coll="Storage", bevel=0.004)
for r in range(4):
    for c in range(3):
        drawer_front("OrgDrawer_%d%d" % (r, c), 0.055, 0.052,
                     (org_x - 0.062 + c * 0.062, PB_FRONT - 0.081,
                      org_z + 0.096 - r * 0.064),
                     "Storage", M["shade_in"], handle='CUP', depth=0.014)


# ---------------------------------------------------------------- storage
def drawer_unit(name, loc, w, d, h, n, body_mat, face_mat, plinth=0.06):
    cx, cy, _ = loc
    add_box(name + "_Body", (w, d, h - plinth), (cx, cy, plinth + (h - plinth) * 0.5),
            mat=body_mat, coll="Storage", bevel=0.006)
    add_box(name + "_Plinth", (w - 0.06, d - 0.05, plinth),
            (cx, cy, plinth * 0.5), mat=M["cab_dark"], coll="Storage")
    add_box(name + "_Top", (w + 0.03, d + 0.02, 0.024), (cx, cy, h + 0.012),
            mat=M["beech"], coll="Storage", bevel=0.005)
    usable = h - plinth - 0.05
    dh = usable / n
    for i in range(n):
        zc = plinth + 0.025 + dh * (i + 0.5)
        drawer_front("%s_Drawer%d" % (name, i), w - 0.035, dh - 0.014,
                     (cx, cy - d * 0.5, zc), "Storage", face_mat, handle='BAR')
    return h


CAB_X, CAB_Y = 2.15, ROOM_Y - 0.32
CAB_H = 1.00
drawer_unit("TallCab", (CAB_X, CAB_Y, 0), 0.90, 0.52, CAB_H, 5,
            M["cab_paint"], M["cab_paint"])
drawer_unit("LowCab", (2.55, 0.30, 0), 0.80, 0.50, 0.72, 3,
            M["cab_dark"], M["cab_paint"])

# open shelf with jars, hung on the right knee wall
add_box("KneeShelf", (0.95, 0.24, 0.030), (2.85, 0.30, 0.98),
        mat=M["pine"], coll="Storage", bevel=0.005)
for sx in (-1, 1):
    add_prism("KneeShelfBracket_%d" % sx,
              [(0.0, 0.0), (0.20, 0.0), (0.0, -0.18)], 0.022,
              (3.20, 0.30 + sx * 0.33, 0.965), rot=(0, math.pi / 2, 0),
              mat=M["steel_dk"], coll="Storage")
for i in range(4):
    jx = 2.58 + i * 0.18
    add_cyl("Jar_%d" % i, 0.058, 0.13, (jx, 0.30, 1.06),
            mat=M["glassjar"], coll="Storage", segs=20)
    add_cyl("JarFill_%d" % i, 0.052, 0.07, (jx, 0.30, 1.03),
            mat=M["screws"], coll="Storage", segs=18)
    add_cyl("JarLid_%d" % i, 0.060, 0.022, (jx, 0.30, 1.13),
            mat=M["steel_dk"], coll="Storage", segs=20)


# ---------------------------------------------------------------- task lamps
def task_lamp(name, base, rot_z, a1=math.radians(38), a2=math.radians(118),
              base_kind='CLAMP', shade_mat=None, light_energy=45.0):
    shade_mat = shade_mat or M["green_en"]
    Mw = Matrix.Translation(Vector(base)) @ Matrix.Rotation(rot_z, 4, 'Z')

    def place(ob):
        ob.matrix_world = Mw @ ob.matrix_basis
        return ob

    if base_kind == 'CLAMP':
        place(add_box(name + "_ClampTop", (0.10, 0.13, 0.030), (0, 0, 0.015),
                      mat=M["steel_dk"], coll="Lamps", bevel=0.005))
        place(add_box(name + "_ClampJaw", (0.09, 0.030, 0.075), (0, -0.05, -0.038),
                      mat=M["steel_dk"], coll="Lamps", bevel=0.004))
        place(add_cyl(name + "_ClampScrew", 0.008, 0.06, (0, -0.05, -0.075),
                      mat=M["steel"], coll="Lamps", segs=10))
        post_z0 = 0.03
    else:
        place(add_cyl(name + "_Base", 0.105, 0.028, (0, 0, 0.014),
                      mat=M["steel_dk"], coll="Lamps", segs=26))
        place(add_cyl(name + "_BaseDome", 0.075, 0.030, (0, 0, 0.040),
                      mat=M["steel_dk"], coll="Lamps", segs=22, radius2=0.045))
        post_z0 = 0.055

    p1 = Vector((0.0, 0.0, post_z0 + 0.19))
    place(add_cyl(name + "_Post", 0.013, 0.19, (0, 0, post_z0 + 0.095),
                  mat=shade_mat, coll="Lamps", segs=14))
    place(add_cyl(name + "_Joint1", 0.017, 0.040, p1, rot=(math.pi / 2, 0, 0),
                  mat=M["steel_dk"], coll="Lamps", segs=14))

    d1 = Vector((math.sin(a1), 0.0, math.cos(a1)))
    L1 = 0.34
    place(add_cyl(name + "_Arm1", 0.011, L1, p1 + d1 * (L1 * 0.5),
                  rot=(0, a1, 0), mat=shade_mat, coll="Lamps", segs=12))
    place(add_cyl(name + "_Arm1b", 0.005, L1 * 0.9,
                  p1 + d1 * (L1 * 0.5) + Vector((0, 0.028, 0)),
                  rot=(0, a1, 0), mat=M["steel"], coll="Lamps", segs=8))
    p2 = p1 + d1 * L1
    place(add_cyl(name + "_Joint2", 0.017, 0.040, p2, rot=(math.pi / 2, 0, 0),
                  mat=M["steel_dk"], coll="Lamps", segs=14))
    place(add_torus(name + "_Spring", 0.014, 0.004, p2 - d1 * 0.06,
                    rot=(0, a1, 0), mat=M["steel"], coll="Lamps",
                    mseg=16, nseg=6))

    d2 = Vector((math.sin(a2), 0.0, math.cos(a2)))
    L2 = 0.30
    place(add_cyl(name + "_Arm2", 0.011, L2, p2 + d2 * (L2 * 0.5),
                  rot=(0, a2, 0), mat=shade_mat, coll="Lamps", segs=12))
    p3 = p2 + d2 * L2
    place(add_cyl(name + "_Joint3", 0.015, 0.034, p3, rot=(math.pi / 2, 0, 0),
                  mat=M["steel_dk"], coll="Lamps", segs=12))

    shade_len = 0.16
    place(add_cyl(name + "_Shade", 0.034, shade_len, p3 + d2 * (shade_len * 0.5),
                  rot=(0, a2, 0), mat=shade_mat, coll="Lamps",
                  segs=28, cap=False, radius2=0.115))
    place(add_cyl(name + "_ShadeRim", 0.118, 0.012,
                  p3 + d2 * (shade_len - 0.004), rot=(0, a2, 0),
                  mat=shade_mat, coll="Lamps", segs=28))
    place(add_cyl(name + "_ShadeInner", 0.100, 0.006, p3 + d2 * (shade_len * 0.80),
                  rot=(0, a2, 0), mat=M["shade_in"], coll="Lamps", segs=26))
    place(add_sphere(name + "_Bulb", 0.030, p3 + d2 * (shade_len * 0.55),
                     mat=M["bulb"], coll="Lamps", subd=2))

    lp = bpy.data.lights.new(name + "_Light", 'POINT')
    lp.energy = light_energy
    lp.color = (1.0, 0.86, 0.68)
    lp.shadow_soft_size = 0.05
    lob = bpy.data.objects.new(name + "_Light", lp)
    lob.location = p3 + d2 * (shade_len * 0.62)
    COLLS["Lights"].objects.link(lob)
    place(lob)

    place(add_cyl(name + "_Cable", 0.004, 0.22, (0.0, 0.06, post_z0 - 0.05),
                  rot=(math.radians(70), 0, 0), mat=M["rubber"],
                  coll="Lamps", segs=8))


task_lamp("LampBench", (0.18, ROOM_Y - 0.16, TOP_Z), math.radians(212),
          a1=math.radians(34), a2=math.radians(122), base_kind='CLAMP',
          light_energy=55.0)
task_lamp("LampCab", (CAB_X - 0.10, CAB_Y - 0.04, CAB_H + 0.024),
          math.radians(196), a1=math.radians(44), a2=math.radians(112),
          base_kind='DISC', shade_mat=M["red"], light_energy=38.0)

# ---------------------------------------------------------------- props
add_cyl("Mug", 0.042, 0.10, (-1.62, BENCH_Y + 0.10, TOP_Z + 0.05),
        mat=M["shade_in"], coll="Props", segs=22)
add_cyl("MugHollow", 0.036, 0.09, (-1.62, BENCH_Y + 0.10, TOP_Z + 0.062),
        mat=M["hole"], coll="Props", segs=20)
add_torus("MugHandle", 0.030, 0.007, (-1.575, BENCH_Y + 0.145, TOP_Z + 0.055),
          rot=(0, 0, math.radians(-40)), mat=M["shade_in"], coll="Props",
          mseg=16, nseg=8)

# work-in-progress box being assembled on the bench
wip = (-0.95, BENCH_Y - 0.02, TOP_Z)
add_box("WipBase", (0.34, 0.22, 0.018), (wip[0], wip[1], wip[2] + 0.009),
        mat=M["beech"], coll="Props", bevel=0.003)
for sy in (-1, 1):
    add_box("WipSideY_%d" % sy, (0.34, 0.016, 0.10),
            (wip[0], wip[1] + sy * 0.102, wip[2] + 0.068),
            mat=M["beech"], coll="Props", bevel=0.003)
add_box("WipSideX", (0.016, 0.20, 0.10), (wip[0] - 0.162, wip[1], wip[2] + 0.068),
        mat=M["beech"], coll="Props", bevel=0.003)
add_box("WipLoosePanel", (0.30, 0.18, 0.016),
        (wip[0] + 0.34, wip[1] - 0.06, wip[2] + 0.008),
        rot=(0, 0, math.radians(12)), mat=M["beech"], coll="Props", bevel=0.003)

add_cyl("Pencil", 0.0045, 0.17, (-1.95, BENCH_Y - 0.20, TOP_Z + 0.005),
        rot=(0, math.pi / 2, math.radians(14)), mat=M["yellow"],
        coll="Props", segs=8)
add_box("SteelRule", (0.30, 0.026, 0.002), (-1.72, BENCH_Y - 0.26, TOP_Z + 0.002),
        rot=(0, 0, math.radians(-6)), mat=M["chrome"], coll="Props")
for i in range(3):
    cx = -0.42 + i * 0.055
    add_cyl("ChiselHandle_%d" % i, 0.015, 0.10,
            (cx, BENCH_Y + 0.22, TOP_Z + 0.016),
            rot=(math.pi / 2, 0, 0), mat=M["pine"], coll="Props",
            segs=12, radius2=0.011)
    add_box("ChiselBlade_%d" % i, (0.016, 0.11, 0.005),
            (cx, BENCH_Y + 0.115, TOP_Z + 0.0125),
            mat=M["chrome"], coll="Props")
add_box("Sketch", (0.24, 0.17, 0.001), (-0.30, BENCH_Y + 0.16, TOP_Z + 0.001),
        rot=(0, 0, math.radians(-9)), mat=M["paper"], coll="Props")

for i in range(14):
    add_box("Chip_%02d" % i,
            (random.uniform(0.02, 0.05), random.uniform(0.008, 0.02), 0.003),
            (random.uniform(BX0 + 0.2, BX1 - 0.2),
             random.uniform(BENCH_Y - 0.30, BENCH_Y + 0.28),
             TOP_Z + 0.002),
            rot=(0, 0, random.uniform(0, TAU)), mat=M["pine"], coll="Props")

# three-legged shop stool
st = (-0.55, 1.62)
add_cyl("StoolSeat", 0.17, 0.038, (st[0], st[1], 0.63),
        mat=M["beech"], coll="Props", segs=26)
for i in range(3):
    a = i * TAU / 3 + 0.4
    add_cyl("StoolLeg_%d" % i, 0.019, 0.63,
            (st[0] + math.cos(a) * 0.075, st[1] + math.sin(a) * 0.075, 0.31),
            rot=(math.radians(9) * math.sin(a), -math.radians(9) * math.cos(a), 0),
            mat=M["pine"], coll="Props", segs=10)
add_torus("StoolRing", 0.115, 0.010, (st[0], st[1], 0.24),
          mat=M["pine"], coll="Props", mseg=20, nseg=8)

# steel toolbox on the floor
tb = (1.15, 1.15)
add_box("ToolboxBody", (0.46, 0.22, 0.17), (tb[0], tb[1], 0.085),
        rot=(0, 0, math.radians(-14)), mat=M["red"], coll="Props", bevel=0.008)
add_box("ToolboxLid", (0.47, 0.23, 0.05), (tb[0], tb[1], 0.195),
        rot=(0, 0, math.radians(-14)), mat=M["red"], coll="Props", bevel=0.008)
add_cyl("ToolboxHandle", 0.008, 0.20, (tb[0], tb[1], 0.255),
        rot=(0, math.pi / 2, math.radians(-14)), mat=M["chrome"],
        coll="Props", segs=10)
for sx in (-1, 1):
    add_cyl("ToolboxHStem_%d" % sx, 0.006, 0.05,
            (tb[0] + sx * 0.098 * math.cos(math.radians(-14)),
             tb[1] + sx * 0.098 * math.sin(math.radians(-14)), 0.235),
            mat=M["chrome"], coll="Props", segs=8)

# timber offcuts and a sheet leaning on the left knee wall
for i in range(6):
    lw = random.uniform(0.075, 0.15)
    add_box("Offcut_%d" % i, (0.026, lw, random.uniform(1.0, 1.45)),
            (-3.30 + i * 0.045, -0.55 + i * 0.20, 0.62),
            rot=(0, math.radians(11 + i * 0.9), 0),
            mat=random.choice((M["pine"], M["beech"])), coll="Props")
add_box("SheetGood", (0.032, 1.05, 1.30), (-3.28, 1.35, 0.66),
        rot=(0, math.radians(9), 0), mat=M["pine"], coll="Props")


# sawhorse with a board across it
def sawhorse(name, loc, rot_z):
    Mw = Matrix.Translation(Vector(loc)) @ Matrix.Rotation(rot_z, 4, 'Z')

    def place(ob):
        ob.matrix_world = Mw @ ob.matrix_basis
        return ob
    place(add_box(name + "_Beam", (0.90, 0.075, 0.09), (0, 0, 0.53),
                  mat=M["pine"], coll="Props", bevel=0.005))
    for sx in (-1, 1):
        for sy in (-1, 1):
            place(add_box(name + "_Leg%d%d" % (sx, sy), (0.05, 0.05, 0.55),
                          (sx * 0.34, sy * 0.13, 0.265),
                          rot=(math.radians(13) * sy, 0, 0),
                          mat=M["pine"], coll="Props"))
    for sx in (-1, 1):
        place(add_box(name + "_Brace%d" % sx, (0.05, 0.34, 0.028),
                      (sx * 0.34, 0, 0.22), mat=M["pine"], coll="Props"))


sawhorse("Sawhorse", (-2.05, -0.35, 0), math.radians(-18))
add_box("SawhorseBoard", (1.55, 0.22, 0.036), (-1.85, -0.20, 0.60),
        rot=(0, 0, math.radians(-12)), mat=M["pine"], coll="Props", bevel=0.004)

add_torus("CordCoil", 0.16, 0.014, (0.55, 0.55, 0.016),
          mat=M["rubber"], coll="Props", mseg=28, nseg=8, squash=(1, 1, 0.7))
add_torus("CordCoil2", 0.125, 0.014, (0.55, 0.55, 0.042),
          mat=M["rubber"], coll="Props", mseg=26, nseg=8, squash=(1, 1, 0.7))
add_box("DustSheet", (0.62, 0.42, 0.07), (2.52, 0.30, 0.755),
        rot=(0, 0, math.radians(6)), mat=M["canvas"], coll="Props", bevel=0.02)

# ---------------------------------------------------------------- lighting
world = bpy.data.worlds.new("WorkshopWorld")
world.use_nodes = True
bg = world.node_tree.nodes["Background"]
bg.inputs["Color"].default_value = (0.055, 0.070, 0.095, 1.0)
bg.inputs["Strength"].default_value = 1.0
scene.world = world

sun_data = bpy.data.lights.new("Sun", 'SUN')
sun_data.energy = 3.2
sun_data.angle = math.radians(1.6)
sun_data.color = (1.0, 0.94, 0.82)
sun = bpy.data.objects.new("Sun", sun_data)
sun.location = (2.0, 7.0, 4.5)
sun.rotation_euler = Vector((-0.28, -0.86, -0.43)).normalized() \
    .to_track_quat('-Z', 'Y').to_euler()
COLLS["Lights"].objects.link(sun)

sky_data = bpy.data.lights.new("WindowSky", 'AREA')
sky_data.shape = 'RECTANGLE'
sky_data.size, sky_data.size_y = 2.0, 1.6
sky_data.energy = 260.0
sky_data.color = (0.78, 0.86, 1.0)
sky = bpy.data.objects.new("WindowSky", sky_data)
sky.location = (wx, ROOM_Y + 0.9, wz + 0.1)
sky.rotation_euler = (-math.pi / 2, 0, 0)
COLLS["Lights"].objects.link(sky)

fill_data = bpy.data.lights.new("RidgeFill", 'AREA')
fill_data.shape = 'RECTANGLE'
fill_data.size, fill_data.size_y = 2.2, 4.0
fill_data.energy = 55.0
fill_data.color = (0.95, 0.93, 0.90)
fill = bpy.data.objects.new("RidgeFill", fill_data)
fill.location = (0.0, 0.2, RIDGE_Z - 0.45)
COLLS["Lights"].objects.link(fill)

bounce_data = bpy.data.lights.new("FloorBounce", 'AREA')
bounce_data.shape = 'RECTANGLE'
bounce_data.size, bounce_data.size_y = 3.0, 2.0
bounce_data.energy = 22.0
bounce_data.color = (1.0, 0.88, 0.74)
bounce = bpy.data.objects.new("FloorBounce", bounce_data)
bounce.location = (0.6, -0.6, 0.9)
bounce.rotation_euler = (math.radians(-115), 0, math.radians(20))
COLLS["Lights"].objects.link(bounce)

# ---------------------------------------------------------------- camera
cam_data = bpy.data.cameras.new("WorkshopCam")
cam_data.lens = 24.0
cam_data.sensor_width = 36.0
cam_data.clip_start = 0.02
cam_data.clip_end = 60.0
cam = bpy.data.objects.new("WorkshopCam", cam_data)
cam_loc = Vector((2.20, -2.05, 1.45))
target = Vector((-0.80, 2.45, 1.20))
cam.location = cam_loc
cam.rotation_euler = (target - cam_loc).to_track_quat('-Z', 'Y').to_euler()
scene.collection.objects.link(cam)
scene.camera = cam

cam_data.dof.use_dof = True
cam_data.dof.focus_distance = (target - cam_loc).length
cam_data.dof.aperture_fstop = 4.0

print("Loft workshop built: %d objects" % len(bpy.data.objects))
