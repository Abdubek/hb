"""claude-050 - A wind turbine with a tapered tower and three blades.

Horizontal-axis turbine: 85 m tapered tubular tower on a concrete foundation,
yaw ring, lofted nacelle with cooler and anemometer mast, spinner hub and three
lofted blades built from twisted, tapering airfoil sections.
"""

import bpy
import bmesh
import math
from mathutils import Vector, Matrix, Euler, noise


# --------------------------------------------------------------------------
# helpers
# --------------------------------------------------------------------------
def reset_scene():
    bpy.ops.wm.read_factory_settings(use_empty=True)
    bpy.context.scene.unit_settings.system = 'METRIC'


def link(obj):
    bpy.context.scene.collection.objects.link(obj)
    return obj


def make_mat(name, color, rough=0.5, metal=0.0, emis=None, emis_str=0.0):
    m = bpy.data.materials.new(name)
    m.use_nodes = True
    b = m.node_tree.nodes["Principled BSDF"]
    b.inputs["Base Color"].default_value = (color[0], color[1], color[2], 1.0)
    b.inputs["Roughness"].default_value = rough
    b.inputs["Metallic"].default_value = metal
    if emis is not None:
        if "Emission Color" in b.inputs:
            b.inputs["Emission Color"].default_value = (emis[0], emis[1], emis[2], 1.0)
        b.inputs["Emission Strength"].default_value = emis_str
    return m


def tag_new(bm, before, index, smooth=False):
    for f in bm.faces:
        if f not in before:
            f.material_index = index
            if smooth:
                f.smooth = True


def bm_box(bm, center, size, index=0, rot=None):
    m = Matrix.Translation(Vector(center))
    if rot is not None:
        m = m @ Euler(rot).to_matrix().to_4x4()
    m = m @ Matrix.Diagonal(Vector((size[0], size[1], size[2], 1.0)))
    before = set(bm.faces)
    bmesh.ops.create_cube(bm, size=1.0, matrix=m)
    tag_new(bm, before, index)


def bm_cyl(bm, center, radius, depth, index=0, segments=24, rot=None, r2=None):
    m = Matrix.Translation(Vector(center))
    if rot is not None:
        m = m @ Euler(rot).to_matrix().to_4x4()
    before = set(bm.faces)
    bmesh.ops.create_cone(bm, cap_ends=True, cap_tris=False, segments=segments,
                          radius1=radius, radius2=(radius if r2 is None else r2),
                          depth=depth, matrix=m)
    tag_new(bm, before, index, smooth=True)


def finish(bm, name, mats, location=(0, 0, 0), rotation=(0, 0, 0), parent=None):
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    me = bpy.data.meshes.new(name)
    bm.to_mesh(me)
    bm.free()
    obj = bpy.data.objects.new(name, me)
    obj.location = location
    obj.rotation_euler = rotation
    for m in mats:
        me.materials.append(m)
    link(obj)
    if parent is not None:
        obj.parent = parent
    return obj


def loft(name, rings, mats, closed=True, cap_start=True, cap_end=True,
         smooth=True, location=(0, 0, 0), rotation=(0, 0, 0), parent=None,
         material_index=0):
    """Skin a list of equal-length vertex rings."""
    bm = bmesh.new()
    ring_verts = [[bm.verts.new(p) for p in ring] for ring in rings]
    n = len(rings[0])
    for a, b in zip(ring_verts, ring_verts[1:]):
        span = range(n) if closed else range(n - 1)
        for i in span:
            j = (i + 1) % n
            try:
                bm.faces.new((a[i], a[j], b[j], b[i]))
            except ValueError:
                pass
    if cap_start:
        try:
            bm.faces.new(list(reversed(ring_verts[0])))
        except ValueError:
            pass
    if cap_end:
        try:
            bm.faces.new(ring_verts[-1])
        except ValueError:
            pass
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    for f in bm.faces:
        f.material_index = material_index
        f.smooth = smooth
    return finish(bm, name, mats, location=location, rotation=rotation, parent=parent)


def look_at(obj, target):
    d = Vector(target) - obj.location
    obj.rotation_euler = d.to_track_quat('-Z', 'Y').to_euler()


# --------------------------------------------------------------------------
reset_scene()

M_TERRAIN = make_mat("Terrain", (0.19, 0.26, 0.12), rough=0.95)
M_TRACK = make_mat("AccessTrack", (0.42, 0.39, 0.33), rough=0.92)
M_CONCRETE = make_mat("Foundation", (0.58, 0.57, 0.54), rough=0.85)
M_TOWER = make_mat("TowerPaint", (0.90, 0.91, 0.92), rough=0.42)
M_TOWER_LO = make_mat("TowerBase", (0.78, 0.79, 0.80), rough=0.5)
M_STEEL = make_mat("Steel", (0.55, 0.56, 0.58), rough=0.38, metal=1.0)
M_DARK = make_mat("DarkTrim", (0.11, 0.12, 0.13), rough=0.5)
M_BLADE = make_mat("BladeGelcoat", (0.93, 0.94, 0.95), rough=0.30)
M_TIP = make_mat("BladeTip", (0.80, 0.15, 0.10), rough=0.35)
M_BEACON = make_mat("Beacon", (1.0, 0.15, 0.1), rough=0.3,
                    emis=(1.0, 0.12, 0.08), emis_str=25.0)
M_GLASS = make_mat("HatchGlass", (0.12, 0.16, 0.2), rough=0.15, metal=0.4)

HUB_Z = 88.0
BLADE_LEN = 45.0
TOWER_TOP = HUB_Z - 1.9

# ------------------------------------------------------------------- terrain
bm = bmesh.new()
N = 48
SPAN = 520.0
grid = []
for iy in range(N + 1):
    row = []
    for ix in range(N + 1):
        x = -SPAN / 2 + SPAN * ix / N
        y = -SPAN / 2 + SPAN * iy / N
        h = (noise.noise(Vector((x * 0.004, y * 0.004, 0.0))) * 9.0
             + noise.noise(Vector((x * 0.016, y * 0.016, 4.0))) * 2.2)
        d = math.hypot(x, y)
        h *= min(1.0, max(0.0, (d - 26.0) / 55.0))
        row.append(bm.verts.new((x, y, h)))
    grid.append(row)
for iy in range(N):
    for ix in range(N):
        bm.faces.new((grid[iy][ix], grid[iy][ix + 1],
                      grid[iy + 1][ix + 1], grid[iy + 1][ix])).material_index = 0
for f in bm.faces:
    f.smooth = True
finish(bm, "Terrain", [M_TERRAIN])

# hardstanding and access track
bm = bmesh.new()
bm_cyl(bm, (0, 0, 0.06), 22.0, 0.12, 0, segments=48)
bm_box(bm, (0, -60.0, 0.05), (7.0, 96.0, 0.10), 0)
finish(bm, "Hardstanding", [M_TRACK])

# ---------------------------------------------------------------- foundation
bm = bmesh.new()
bm_cyl(bm, (0, 0, 0.30), 9.5, 0.60, 0, segments=48, r2=8.2)
bm_cyl(bm, (0, 0, 0.90), 4.6, 0.70, 0, segments=48, r2=3.6)
bm_cyl(bm, (0, 0, 1.32), 3.0, 0.20, 1, segments=48)
finish(bm, "Foundation", [M_CONCRETE, M_STEEL])

# --------------------------------------------------------------------- tower
SEG = 48
BASE_R, TOP_R = 2.30, 1.15
rings = []
STEPS = 26
for k in range(STEPS + 1):
    t = k / STEPS
    z = 1.40 + (TOWER_TOP - 1.40) * t
    r = TOP_R + (BASE_R - TOP_R) * (1.0 - t) ** 1.25
    rings.append([(r * math.cos(2 * math.pi * i / SEG),
                   r * math.sin(2 * math.pi * i / SEG), z) for i in range(SEG)])
tower = loft("Tower", rings, [M_TOWER], cap_start=True, cap_end=True)

# tower details: flange bands, door, service platform, beacon
bm = bmesh.new()
for z, r in ((1.55, BASE_R + 0.06), (22.0, 2.02), (44.0, 1.72), (66.0, 1.42)):
    bm_cyl(bm, (0, 0, z), r, 0.22, 0, segments=SEG)
# access door
bm_box(bm, (BASE_R - 0.05, 0.0, 3.10), (0.28, 1.10, 2.10), 1)
bm_box(bm, (BASE_R + 0.06, 0.0, 3.10), (0.05, 0.95, 1.95), 2)
bm_box(bm, (BASE_R + 0.20, 0.0, 1.70), (0.90, 1.40, 0.14), 0)   # entry step
# top service platform with railing
bm_cyl(bm, (0, 0, TOWER_TOP - 1.2), 2.35, 0.10, 0, segments=32)
for k in range(3):
    bm_cyl(bm, (0, 0, TOWER_TOP - 0.75 + k * 0.35), 2.32, 0.045, 0, segments=32, r2=2.32)
for i in range(12):
    a = 2 * math.pi * i / 12
    bm_cyl(bm, (2.25 * math.cos(a), 2.25 * math.sin(a), TOWER_TOP - 0.6),
           0.035, 1.10, 0, segments=8)
finish(bm, "TowerDetails", [M_STEEL, M_DARK, M_GLASS])


# -------------------------------------------------------------------- nacelle
def rounded_rect_ring(hw, hh, z, corner=0.35, n=32):
    """Superellipse-ish ring in the local XZ->section plane, returned in 3D."""
    pts = []
    for i in range(n):
        a = 2 * math.pi * i / n
        ca, sa = math.cos(a), math.sin(a)
        p = 2.0 / max(corner, 1e-3) * 0.35 + 2.0
        x = hw * math.copysign(abs(ca) ** (2.0 / p), ca)
        y = hh * math.copysign(abs(sa) ** (2.0 / p), sa)
        pts.append((x, y, z))
    return pts


# nacelle built along local +Y (pointing downwind/aft), skinned from sections
nac_sections = [
    (-2.10, 1.10, 0.95),
    (-1.20, 1.60, 1.45),
    (0.60, 1.75, 1.60),
    (3.60, 1.75, 1.60),
    (5.60, 1.62, 1.44),
    (6.60, 1.20, 1.05),
    (7.00, 0.70, 0.60),
]
nac_rings = []
for y, hw, hh in nac_sections:
    ring = rounded_rect_ring(hw, hh, 0.0, corner=0.45, n=32)
    nac_rings.append([(p[0], y, p[1]) for p in ring])
nacelle = loft("Nacelle", nac_rings, [M_TOWER], smooth=True)
nacelle.location = (0.0, 0.0, HUB_Z)

# nacelle add-ons: cooler, anemometer mast, hatch, beacon, yaw ring
bm = bmesh.new()
bm_box(bm, (0.0, 4.6, 1.70), (2.10, 1.60, 0.34), 0)                  # top cooler
for k in range(7):
    bm_box(bm, (0.0, 3.95 + k * 0.22, 1.92), (2.00, 0.08, 0.10), 1)  # cooler fins
bm_box(bm, (0.0, 6.35, 1.55), (0.50, 0.50, 0.10), 1)                 # met platform
bm_cyl(bm, (0.35, 6.35, 2.10), 0.05, 1.10, 1, segments=10)
bm_cyl(bm, (-0.35, 6.35, 1.95), 0.05, 0.80, 1, segments=10)
bm_cyl(bm, (0.35, 6.35, 2.72), 0.16, 0.06, 1, segments=12)           # anemometer cups
for i in range(3):
    a = 2 * math.pi * i / 3
    bm_cyl(bm, (0.35 + 0.22 * math.cos(a), 6.35 + 0.22 * math.sin(a), 2.78),
           0.07, 0.05, 1, segments=10)
bm_box(bm, (-0.30, 6.35, 2.40), (0.60, 0.10, 0.32), 1)               # wind vane
bm_box(bm, (0.0, 2.20, 1.62), (1.10, 1.40, 0.06), 1)                 # roof hatch
bm_cyl(bm, (0.0, 6.85, 1.30), 0.16, 0.20, 2, segments=14)            # aviation beacon
bm_box(bm, (0.0, 1.20, -1.62), (2.20, 3.20, 0.20), 1)                # yaw deck
bm_cyl(bm, (0.0, 1.20, -1.85), 1.35, 0.34, 1, segments=40)           # yaw bearing
finish(bm, "NacelleDetails", [M_TOWER, M_STEEL, M_BEACON],
       location=(0.0, 0.0, HUB_Z), parent=nacelle)

# beacon light
beacon = bpy.data.lights.new("BeaconLight", 'POINT')
beacon.energy = 3000.0
beacon.color = (1.0, 0.15, 0.1)
beacon.shadow_soft_size = 0.2
bo = bpy.data.objects.new("BeaconLight", beacon)
bo.location = (0.0, 6.85, HUB_Z + 1.4)
link(bo)
bo.parent = nacelle
bo.matrix_parent_inverse = nacelle.matrix_world.inverted()

# ----------------------------------------------------------------- rotor hub
rotor = bpy.data.objects.new("RotorRoot", None)
rotor.empty_display_type = 'PLAIN_AXES'
rotor.empty_display_size = 2.0
rotor.location = (0.0, -2.6, HUB_Z)
rotor.rotation_euler = (math.radians(-5.0), 0.0, 0.0)   # rotor tilt
link(rotor)
rotor.parent = nacelle
rotor.matrix_parent_inverse = nacelle.matrix_world.inverted()

# spinner: revolved nose cone built as a loft of circles about the -Y axis
spin_rings = []
spin_sections = [(1.15, 0.35), (0.55, 1.45), (0.00, 1.70), (-0.70, 1.72),
                 (-1.40, 1.55), (-1.85, 1.15)]
for y, r in spin_sections:
    ring = []
    for i in range(28):
        a = 2 * math.pi * i / 28
        ring.append((r * math.cos(a), -y, r * math.sin(a)))
    spin_rings.append(ring)
spinner = loft("Spinner", spin_rings, [M_TOWER], smooth=True)
spinner.parent = rotor
spinner.matrix_parent_inverse = rotor.matrix_world.inverted()
spinner.location = rotor.location

bm = bmesh.new()
bm_cyl(bm, (0, 0, 0), 1.30, 1.10, 0, segments=32, rot=(math.radians(90), 0, 0))
finish(bm, "HubBarrel", [M_STEEL], location=rotor.location)
hub_barrel = bpy.data.objects["HubBarrel"]
hub_barrel.parent = rotor
hub_barrel.matrix_parent_inverse = rotor.matrix_world.inverted()


# -------------------------------------------------------------------- blades
def airfoil_points(n_half=18, thickness=0.16, camber=0.035):
    """Closed airfoil loop, chord from 0..1 in x, thickness in y."""
    upper, lower = [], []
    for i in range(n_half + 1):
        beta = math.pi * i / n_half
        x = 0.5 * (1.0 - math.cos(beta))
        yt = 5.0 * thickness * (0.2969 * math.sqrt(max(x, 0.0)) - 0.1260 * x
                                - 0.3516 * x * x + 0.2843 * x ** 3 - 0.1015 * x ** 4)
        yc = camber * 4.0 * x * (1.0 - x)
        upper.append((x, yc + yt))
        lower.append((x, yc - yt))
    loop = list(reversed(upper)) + lower[1:-1]
    return loop


AF = airfoil_points()
NPTS = len(AF)


def blade_ring(t):
    """One blade section at span fraction t (0 root .. 1 tip), local Z = span."""
    span = t * BLADE_LEN
    # chord distribution: cylindrical root -> max chord -> taper to tip
    if t < 0.16:
        u = t / 0.16
        chord = 1.9 + (3.55 - 1.9) * u
        blend = u ** 1.4
    else:
        u = (t - 0.16) / 0.84
        chord = 3.55 * (1.0 - 0.86 * u ** 0.85)
        blend = 1.0
    twist = math.radians(16.0) * (1.0 - t) ** 1.6 - math.radians(2.0) * t
    rel_thick = 0.42 - 0.24 * min(1.0, t / 0.45)
    prebend = 2.2 * t ** 2.6            # gentle out-of-plane prebend
    sweep = -0.35 * t ** 2.2
    root_r = 0.95

    ring = []
    for i in range(NPTS):
        # airfoil coordinates, scaled by chord, thickness modulated along span
        ax, ay = AF[i]
        ax = (ax - 0.32) * chord
        ay = ay * chord * (rel_thick / 0.16)
        # circular root section with matching point ordering
        ang = 2 * math.pi * i / NPTS
        cx = math.cos(ang) * root_r
        cy = math.sin(ang) * root_r
        x = cx + (ax - cx) * blend
        y = cy + (ay - cy) * blend
        # twist about the span axis
        ct, st = math.cos(twist), math.sin(twist)
        xr = x * ct - y * st
        yr = x * st + y * ct
        ring.append((xr + sweep, yr + prebend, span))
    return ring


blade_rings = []
STEPS = 34
for k in range(STEPS + 1):
    t = (k / STEPS) ** 0.92
    blade_rings.append(blade_ring(min(t, 0.999)))
# closing tip ring, pinched
tip = blade_ring(0.999)
cx = sum(p[0] for p in tip) / len(tip)
cy = sum(p[1] for p in tip) / len(tip)
blade_rings.append([(cx + (p[0] - cx) * 0.18, cy + (p[1] - cy) * 0.18, BLADE_LEN)
                    for p in tip])

for b in range(3):
    ang = 2 * math.pi * b / 3
    blade = loft("Blade_%d" % b, blade_rings, [M_BLADE, M_TIP], smooth=True,
                 cap_start=True, cap_end=True)
    # colour the outer tip faces
    for poly in blade.data.polygons:
        if poly.center.z > BLADE_LEN - 3.2:
            poly.material_index = 1
    blade.location = rotor.location
    blade.rotation_euler = Euler((math.radians(90), 0.0, 0.0)).to_matrix().to_4x4() \
        .to_euler()
    # orient: span outwards from hub, rotated around the rotor axis (local -Y)
    m = (Matrix.Rotation(-ang, 4, 'Y')
         @ Matrix.Rotation(math.radians(90), 4, 'X'))
    blade.rotation_euler = m.to_euler()
    blade.parent = rotor
    blade.matrix_parent_inverse = rotor.matrix_world.inverted()

    # blade root ring / pitch bearing
    bmr = bmesh.new()
    bm_cyl(bmr, (0, 0, 0), 1.10, 0.55, 0, segments=28)
    bm_cyl(bmr, (0, 0, 0.30), 1.18, 0.12, 0, segments=28)
    root = finish(bmr, "BladeRoot_%d" % b, [M_STEEL], location=rotor.location)
    root.rotation_euler = m.to_euler()
    root.parent = rotor
    root.matrix_parent_inverse = rotor.matrix_world.inverted()

# put the rotor in a pleasing pose
rotor.rotation_euler = (math.radians(-5.0), math.radians(24.0), 0.0)
# yaw the whole nacelle slightly for a three-quarter view
nacelle.rotation_euler = (0.0, 0.0, math.radians(28.0))

# ------------------------------------------------------------------ lighting
sun_data = bpy.data.lights.new("Sun", 'SUN')
sun_data.energy = 3.2
sun_data.angle = math.radians(1.0)
sun_data.color = (1.0, 0.92, 0.80)
sun = bpy.data.objects.new("Sun", sun_data)
sun.rotation_euler = (math.radians(58), 0.0, math.radians(-40))
sun.location = (0, 0, 140)
link(sun)

fill = bpy.data.lights.new("SkyFill", 'AREA')
fill.shape = 'SQUARE'
fill.size = 200.0
fill.energy = 60000.0
fill.color = (0.55, 0.68, 1.0)
fo = bpy.data.objects.new("SkyFill", fill)
fo.location = (-60, -60, 150)
link(fo)
look_at(fo, (0, 0, 60))

world = bpy.data.worlds.new("TurbineWorld")
world.use_nodes = True
nt = world.node_tree
bg = nt.nodes["Background"]
bg.inputs["Strength"].default_value = 1.0
try:
    sky = nt.nodes.new("ShaderNodeTexSky")
    sky.sky_type = 'NISHITA'
    sky.sun_elevation = math.radians(32)
    sky.sun_rotation = math.radians(-40)
    nt.links.new(sky.outputs["Color"], bg.inputs["Color"])
except Exception:
    bg.inputs["Color"].default_value = (0.30, 0.48, 0.85, 1.0)
bpy.context.scene.world = world

# ------------------------------------------------------------------- camera
cam_data = bpy.data.cameras.new("TurbineCam")
cam_data.lens = 45.0
cam_data.clip_start = 0.5
cam_data.clip_end = 3000.0
cam = bpy.data.objects.new("TurbineCam", cam_data)
cam.location = (135.0, -195.0, 62.0)
link(cam)
look_at(cam, (0.0, 0.0, 62.0))
bpy.context.scene.camera = cam

bpy.context.view_layer.update()
print("claude-050: wind turbine built, hub height %.1f m, rotor diameter %.1f m"
      % (HUB_Z, 2 * BLADE_LEN + 3.4))
