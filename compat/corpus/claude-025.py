"""claude-025 - Circular gazebo with posts and roof.

Eight turned posts stand on a round deck inside an octagonal ring beam.
Seven bays carry balustrades, the eighth opens onto steps and a stone path.
The roof is an eight sided solid of revolution with hip caps and a finial.
"""

import bpy
import bmesh
import math
import random
from mathutils import Vector


# --------------------------------------------------------------- utilities
def reset_scene():
    bpy.ops.wm.read_factory_settings(use_empty=True)


def make_material(name, color, rough=0.6, metal=0.0, emission=None,
                  emission_strength=0.0):
    mat = bpy.data.materials.new(name)
    mat.use_nodes = True
    bsdf = mat.node_tree.nodes["Principled BSDF"]

    def setv(key, val):
        if key in bsdf.inputs:
            bsdf.inputs[key].default_value = val

    setv("Base Color", (color[0], color[1], color[2], 1.0))
    setv("Roughness", rough)
    setv("Metallic", metal)
    if emission is not None:
        setv("Emission Color", (emission[0], emission[1], emission[2], 1.0))
        setv("Emission Strength", emission_strength)
    return mat


def assign(obj, mat):
    obj.data.materials.append(mat)
    return obj


def smooth(obj, angle=35.0):
    for poly in obj.data.polygons:
        poly.use_smooth = True
    try:
        bpy.ops.object.select_all(action='DESELECT')
        obj.select_set(True)
        bpy.context.view_layer.objects.active = obj
        bpy.ops.object.shade_auto_smooth(angle=math.radians(angle))
    except Exception:
        pass
    return obj


def lathe(name, profile, segments=48, mat=None, rot_z=0.0):
    bm = bmesh.new()
    verts = [bm.verts.new((p[0], 0.0, p[1])) for p in profile]
    edges = [bm.edges.new((verts[i], verts[i + 1])) for i in range(len(verts) - 1)]
    bmesh.ops.spin(bm, geom=verts + edges, cent=(0.0, 0.0, 0.0),
                   axis=(0.0, 0.0, 1.0), dvec=(0.0, 0.0, 0.0),
                   angle=math.tau, steps=segments, use_merge=True)
    bmesh.ops.remove_doubles(bm, verts=bm.verts, dist=1e-5)
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    me = bpy.data.meshes.new(name)
    bm.to_mesh(me)
    bm.free()
    obj = bpy.data.objects.new(name, me)
    obj.rotation_euler = (0.0, 0.0, rot_z)
    bpy.context.scene.collection.objects.link(obj)
    if mat:
        assign(obj, mat)
    return obj


def box(name, size, location, rotation=(0.0, 0.0, 0.0), mat=None, bev=0.0):
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=location, rotation=rotation)
    obj = bpy.context.active_object
    obj.name = name
    obj.scale = size
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    if mat:
        assign(obj, mat)
    if bev > 0.0:
        m = obj.modifiers.new("Bevel", 'BEVEL')
        m.width = bev
        m.segments = 2
        m.limit_method = 'ANGLE'
        m.angle_limit = math.radians(35.0)
    return obj


def bar(name, p1, p2, width, height, mat=None, bev=0.0):
    a, b = Vector(p1), Vector(p2)
    d = b - a
    if d.length < 1e-6:
        return None
    rot = d.to_track_quat('Z', 'Y').to_euler()
    return box(name, (width, height, d.length), (a + b) * 0.5, rot, mat, bev)


def strut(name, p1, p2, radius, mat=None, verts=10):
    a, b = Vector(p1), Vector(p2)
    d = b - a
    if d.length < 1e-6:
        return None
    bpy.ops.mesh.primitive_cylinder_add(vertices=verts, radius=radius,
                                        depth=d.length, location=(a + b) * 0.5)
    obj = bpy.context.active_object
    obj.name = name
    obj.rotation_euler = d.to_track_quat('Z', 'Y').to_euler()
    if mat:
        assign(obj, mat)
    smooth(obj)
    return obj


def look_at(obj, target):
    d = Vector(target) - obj.location
    obj.rotation_euler = d.to_track_quat('-Z', 'Y').to_euler()


# ------------------------------------------------------------------- scene
reset_scene()
random.seed(5)

world = bpy.data.worlds.new("World")
world.use_nodes = True
wbg = world.node_tree.nodes["Background"]
wbg.inputs[0].default_value = (0.33, 0.46, 0.68, 1.0)
wbg.inputs[1].default_value = 1.0
bpy.context.scene.world = world

WOOD = make_material("PaintedWood", (0.86, 0.85, 0.80), rough=0.45)
WOOD_W = make_material("DeckWood", (0.50, 0.34, 0.20), rough=0.72)
WOOD_D = make_material("TrimWood", (0.34, 0.22, 0.13), rough=0.68)
SHINGLE = make_material("Shingle", (0.24, 0.22, 0.24), rough=0.82)
STONE = make_material("Stone", (0.60, 0.58, 0.54), rough=0.90)
GRASS = make_material("Grass", (0.15, 0.31, 0.10), rough=0.95)
BRASS = make_material("Brass", (0.70, 0.53, 0.20), rough=0.30, metal=1.0)
GLOW = make_material("LampGlass", (1.0, 0.92, 0.72), rough=0.2,
                     emission=(1.0, 0.86, 0.60), emission_strength=12.0)

# ---- geometry constants
N = 8
R_POST = 2.55
R_DECK = 2.98
DECK_TOP = 0.45
POST_TOP = 2.88
EAVE_R = 3.40
EAVE_Z = 2.98
APEX_Z = 4.55
ANG = [math.radians(-67.5 + 45.0 * k) for k in range(N)]


def ring_pt(radius, angle, z):
    return Vector((radius * math.cos(angle), radius * math.sin(angle), z))


# ---- ground and approach path
bpy.ops.mesh.primitive_plane_add(size=40.0, location=(0.0, 0.0, 0.0))
g = bpy.context.active_object
g.name = "Lawn"
assign(g, GRASS)

for i in range(6):
    y = -3.9 - i * 0.78
    bpy.ops.mesh.primitive_cylinder_add(vertices=6, radius=0.62, depth=0.06,
                                        location=(random.uniform(-0.1, 0.1), y, 0.03),
                                        rotation=(0.0, 0.0, random.uniform(0.0, 1.0)))
    flag = bpy.context.active_object
    flag.name = "PathStone_%d" % i
    flag.scale = (1.0, 0.82, 1.0)
    assign(flag, STONE)

# ---- foundation piers and deck
for k in range(N):
    p = ring_pt(R_POST, ANG[k], 0.0)
    bpy.ops.mesh.primitive_cylinder_add(vertices=16, radius=0.28, depth=0.34,
                                        location=(p.x, p.y, 0.17))
    pier = bpy.context.active_object
    pier.name = "Pier_%d" % k
    assign(pier, STONE)
    smooth(pier)

deck = lathe("Deck", [
    (0.000, DECK_TOP), (R_DECK - 0.10, DECK_TOP), (R_DECK, DECK_TOP - 0.05),
    (R_DECK, DECK_TOP - 0.20), (R_DECK - 0.12, DECK_TOP - 0.26),
    (0.000, DECK_TOP - 0.26)], segments=64, mat=WOOD_W)
smooth(deck, 20.0)

# radial deck boards suggested by shallow inlay strips
for k in range(24):
    a = math.tau * k / 24.0
    bar("DeckJoint_%d" % k, ring_pt(0.35, a, DECK_TOP + 0.006),
        ring_pt(R_DECK - 0.08, a, DECK_TOP + 0.006), 0.02, 0.012, WOOD_D)

bpy.ops.mesh.primitive_cylinder_add(vertices=48, radius=0.36, depth=0.02,
                                    location=(0.0, 0.0, DECK_TOP + 0.006))
medal = bpy.context.active_object
medal.name = "DeckMedallion"
assign(medal, WOOD_D)
smooth(medal)

# fascia band
fascia = lathe("Fascia", [(R_DECK + 0.01, DECK_TOP - 0.06),
                          (R_DECK + 0.01, DECK_TOP - 0.20)],
               segments=64, mat=WOOD_D)
fs = fascia.modifiers.new("Solidify", 'SOLIDIFY')
fs.thickness = 0.03

# ---- entry steps at the -Y gap
for i, (h, y, w) in enumerate(((0.30, -3.10, 1.55), (0.15, -3.42, 1.70))):
    box("Step_%d" % i, (w, 0.34, h), (0.0, y, h * 0.5), mat=STONE, bev=0.012)
for sx in (-1.0, 1.0):
    box("StepCheek_%d" % int(sx), (0.14, 0.75, 0.46),
        (sx * 0.86, -3.26, 0.23), mat=STONE, bev=0.01)

# ---- posts
for k in range(N):
    a = ANG[k]
    p = ring_pt(R_POST, a, 0.0)
    box("Post_%d" % k, (0.14, 0.14, POST_TOP - DECK_TOP),
        (p.x, p.y, (POST_TOP + DECK_TOP) * 0.5), (0.0, 0.0, a),
        mat=WOOD, bev=0.008)
    box("PostBase_%d" % k, (0.22, 0.22, 0.10),
        (p.x, p.y, DECK_TOP + 0.05), (0.0, 0.0, a), mat=WOOD, bev=0.008)
    box("PostCap_%d" % k, (0.22, 0.22, 0.08),
        (p.x, p.y, POST_TOP - 0.04), (0.0, 0.0, a), mat=WOOD, bev=0.008)

# ---- octagonal ring beam and its brackets
for k in range(N):
    a1, a2 = ANG[k], ANG[(k + 1) % N]
    p1 = ring_pt(R_POST, a1, POST_TOP + 0.13)
    p2 = ring_pt(R_POST, a2, POST_TOP + 0.13)
    bar("RingBeam_%d" % k, p1, p2, 0.13, 0.26, WOOD, bev=0.008)
    # decorative corner brackets each side of every post
    mid_dir = (p2 - p1).normalized()
    for end, sgn in ((p1, 1.0), (p2, -1.0)):
        b1 = end + mid_dir * (0.10 * sgn) + Vector((0.0, 0.0, -0.55))
        b2 = end + mid_dir * (0.55 * sgn) + Vector((0.0, 0.0, -0.10))
        bar("Bracket", b1, b2, 0.06, 0.10, WOOD, bev=0.005)

# ---- balustrades: every bay except the front opening (post 7 -> post 0)
for k in range(N):
    nxt = (k + 1) % N
    if k == N - 1:
        continue                      # entry gap faces -Y
    a1, a2 = ANG[k], ANG[nxt]
    for rz, w, h in ((DECK_TOP + 0.18, 0.09, 0.09),
                     (DECK_TOP + 0.92, 0.14, 0.09)):
        bar("Rail_%d" % k, ring_pt(R_POST, a1, rz), ring_pt(R_POST, a2, rz),
            w, h, WOOD, bev=0.006)
    p1 = ring_pt(R_POST, a1, 0.0)
    p2 = ring_pt(R_POST, a2, 0.0)
    n_bal = 6
    for j in range(1, n_bal + 1):
        t = j / (n_bal + 1.0)
        bp = p1.lerp(p2, t)
        box("Baluster_%d_%d" % (k, j), (0.055, 0.055, 0.66),
            (bp.x, bp.y, DECK_TOP + 0.55), (0.0, 0.0, a1), mat=WOOD, bev=0.004)

# ---- benches in three of the rear bays
for k in (2, 3, 4):
    a1, a2 = ANG[k], ANG[(k + 1) % N]
    r_seat = R_POST - 0.42
    s1 = ring_pt(r_seat, a1, 0.0)
    s2 = ring_pt(r_seat, a2, 0.0)
    seat_z = DECK_TOP + 0.44
    bar("BenchSeat_%d" % k, Vector((s1.x, s1.y, seat_z)),
        Vector((s2.x, s2.y, seat_z)), 0.46, 0.06, WOOD_W, bev=0.006)
    for t in (0.22, 0.78):
        lp = s1.lerp(s2, t)
        box("BenchLeg", (0.40, 0.07, 0.44),
            (lp.x, lp.y, DECK_TOP + 0.21),
            (0.0, 0.0, a1 + (a2 - a1) * t), mat=WOOD_W, bev=0.005)

# ---- roof: eight sided lathe, rotated so the corners land over the posts
roof_profile = [
    (EAVE_R, EAVE_Z - 0.06), (EAVE_R, EAVE_Z + 0.02), (3.10, EAVE_Z + 0.22),
    (2.30, 3.42), (1.45, 3.90), (0.72, 4.28), (0.24, 4.48), (0.000, APEX_Z),
]
roof = lathe("Roof", roof_profile, segments=8, mat=SHINGLE,
             rot_z=math.radians(22.5))
rsol = roof.modifiers.new("Solidify", 'SOLIDIFY')
rsol.thickness = 0.07
rsol.offset = 1.0

# soffit / eave board following the same octagon
for k in range(N):
    a1, a2 = ANG[k], ANG[(k + 1) % N]
    bar("EaveBoard_%d" % k, ring_pt(EAVE_R, a1, EAVE_Z - 0.14),
        ring_pt(EAVE_R, a2, EAVE_Z - 0.14), 0.06, 0.20, WOOD, bev=0.005)

# hip rafter caps from each eave corner to the apex
for k in range(N):
    corner = ring_pt(EAVE_R - 0.02, ANG[k], EAVE_Z + 0.03)
    strut("HipCap_%d" % k, corner, (0.0, 0.0, APEX_Z + 0.02), 0.055,
          WOOD_D, verts=6)

# ---- finial
bpy.ops.mesh.primitive_uv_sphere_add(segments=24, ring_count=14, radius=0.17,
                                     location=(0.0, 0.0, APEX_Z + 0.16))
ball = bpy.context.active_object
ball.name = "FinialBall"
assign(ball, BRASS)
smooth(ball)
spire = lathe("FinialSpire", [
    (0.000, APEX_Z + 0.28), (0.075, APEX_Z + 0.34), (0.05, APEX_Z + 0.55),
    (0.000, APEX_Z + 0.78)], segments=20, mat=BRASS)
smooth(spire)

# weather vane arrow
strut("VaneShaft", (0.0, 0.0, APEX_Z + 0.78), (0.0, 0.0, APEX_Z + 0.98),
      0.02, BRASS, verts=8)
bar("VaneArrow", (-0.34, 0.0, APEX_Z + 0.94), (0.34, 0.0, APEX_Z + 0.94),
    0.02, 0.05, BRASS)

# ---- hanging lamp under the roof
strut("LampCord", (0.0, 0.0, 3.90), (0.0, 0.0, 3.32), 0.012, WOOD_D, verts=6)
lamp_body = lathe("LampShade", [
    (0.000, 3.36), (0.20, 3.30), (0.22, 3.20), (0.000, 3.18)],
    segments=24, mat=BRASS)
smooth(lamp_body)
bpy.ops.mesh.primitive_uv_sphere_add(segments=20, ring_count=12, radius=0.11,
                                     location=(0.0, 0.0, 3.10))
bulb = bpy.context.active_object
bulb.name = "LampGlobe"
assign(bulb, GLOW)
smooth(bulb)

# ---- a couple of shrubs framing the entry
for sx in (-1.0, 1.0):
    for j in range(5):
        bpy.ops.mesh.primitive_ico_sphere_add(
            subdivisions=2, radius=random.uniform(0.22, 0.36),
            location=(sx * (1.9 + random.uniform(-0.2, 0.2)),
                      -3.0 + random.uniform(-0.3, 0.3),
                      0.30 + random.uniform(0.0, 0.30)))
        sh = bpy.context.active_object
        sh.name = "Shrub"
        assign(sh, GRASS)
        smooth(sh)

# --------------------------------------------------------------- lighting
bpy.ops.object.light_add(type='SUN', location=(8.0, -9.0, 14.0))
sun = bpy.context.active_object
sun.name = "Sun"
sun.data.energy = 3.6
sun.data.angle = math.radians(2.0)
sun.data.color = (1.0, 0.95, 0.87)
look_at(sun, (0.0, 0.0, 1.5))

bpy.ops.object.light_add(type='POINT', location=(0.0, 0.0, 3.08))
inner = bpy.context.active_object
inner.name = "LampLight"
inner.data.energy = 90.0
inner.data.shadow_soft_size = 0.15
inner.data.color = (1.0, 0.82, 0.58)

bpy.ops.object.light_add(type='AREA', location=(-7.0, 6.0, 6.0))
fill = bpy.context.active_object
fill.name = "Fill"
fill.data.energy = 500.0
fill.data.size = 8.0
fill.data.color = (0.70, 0.80, 1.0)
look_at(fill, (0.0, 0.0, 1.8))

# ----------------------------------------------------------------- camera
cam_data = bpy.data.cameras.new("Camera")
cam_data.lens = 40.0
cam = bpy.data.objects.new("Camera", cam_data)
cam.location = (7.4, -8.2, 4.3)
bpy.context.scene.collection.objects.link(cam)
look_at(cam, (0.0, -0.2, 1.85))
bpy.context.scene.camera = cam

print("claude-025 gazebo built: %d objects" % len(bpy.data.objects))
