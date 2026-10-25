"""claude-024 - Playground slide with ladder and platform.

The chute is a swept U-section built vertex by vertex along a smoothstep
descent and thickened with a solidify modifier.  A guarded platform on four
posts, a gable sunshade and an angled ladder complete the unit.
"""

import bpy
import bmesh
import math
import random
from mathutils import Vector


# --------------------------------------------------------------- utilities
def reset_scene():
    bpy.ops.wm.read_factory_settings(use_empty=True)


def make_material(name, color, rough=0.5, metal=0.0):
    mat = bpy.data.materials.new(name)
    mat.use_nodes = True
    bsdf = mat.node_tree.nodes["Principled BSDF"]

    def setv(key, val):
        if key in bsdf.inputs:
            bsdf.inputs[key].default_value = val

    setv("Base Color", (color[0], color[1], color[2], 1.0))
    setv("Roughness", rough)
    setv("Metallic", metal)
    return mat


def assign(obj, mat):
    obj.data.materials.append(mat)
    return obj


def smooth(obj, angle=40.0):
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


def strut(name, p1, p2, radius, mat=None, verts=12):
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
random.seed(11)

world = bpy.data.worlds.new("World")
world.use_nodes = True
wbg = world.node_tree.nodes["Background"]
wbg.inputs[0].default_value = (0.38, 0.52, 0.74, 1.0)
wbg.inputs[1].default_value = 1.3
bpy.context.scene.world = world

YELLOW = make_material("ChutePlastic", (0.88, 0.62, 0.06), rough=0.28)
BLUE = make_material("BluePlastic", (0.08, 0.26, 0.62), rough=0.35)
RED = make_material("RedPlastic", (0.62, 0.10, 0.10), rough=0.35)
GREEN = make_material("GreenSteel", (0.10, 0.36, 0.20), rough=0.42, metal=0.35)
STEEL = make_material("Galv", (0.66, 0.67, 0.70), rough=0.30, metal=1.0)
DECKM = make_material("DeckPanel", (0.16, 0.18, 0.22), rough=0.65)
SAND = make_material("SafetySand", (0.76, 0.66, 0.48), rough=0.96)
GRASSM = make_material("Grass", (0.18, 0.34, 0.12), rough=0.95)
RUBBER = make_material("RubberMat", (0.35, 0.13, 0.12), rough=0.9)

# ---- ground: grass with a soft-fall sand bay
bpy.ops.mesh.primitive_plane_add(size=40.0, location=(0.0, 0.0, -0.02))
g = bpy.context.active_object
g.name = "Grass"
assign(g, GRASSM)

bpy.ops.mesh.primitive_cylinder_add(vertices=48, radius=4.6, depth=0.06,
                                    location=(0.9, 0.0, 0.01))
bay = bpy.context.active_object
bay.name = "SandBay"
bay.scale = (1.35, 1.0, 1.0)
bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
assign(bay, SAND)
smooth(bay)

# ---- platform
DECK_Z = 1.90
DECK_HX, DECK_HY = 0.62, 0.56
POST = 0.09
POST_TOP = 2.42

deck = box("Deck", (DECK_HX * 2.0, DECK_HY * 2.0, 0.08),
           (0.0, 0.0, DECK_Z - 0.04), mat=DECKM, bev=0.008)
for i in range(7):
    y = -DECK_HY + 0.08 + i * 0.16
    box("DeckRib_%d" % i, (DECK_HX * 1.9, 0.05, 0.012),
        (0.0, y, DECK_Z + 0.006), mat=BLUE)

posts = []
for sx in (-1.0, 1.0):
    for sy in (-1.0, 1.0):
        px, py = sx * (DECK_HX - 0.05), sy * (DECK_HY - 0.05)
        posts.append((px, py))
        box("Post_%d_%d" % (int(sx), int(sy)), (POST, POST, POST_TOP),
            (px, py, POST_TOP * 0.5), mat=GREEN, bev=0.006)
        # ground anchor
        box("Anchor", (0.20, 0.20, 0.10), (px, py, 0.05), mat=DECKM)

# under-deck bearers
for sy in (-1.0, 1.0):
    box("Bearer", (DECK_HX * 2.0, 0.07, 0.14),
        (0.0, sy * (DECK_HY - 0.05), DECK_Z - 0.15), mat=GREEN, bev=0.006)

# ---- guard rails on the two open sides
for sy in (-1.0, 1.0):
    py = sy * (DECK_HY - 0.05)
    for rz in (DECK_Z + 0.50, DECK_Z + 0.92):
        box("Rail", (DECK_HX * 2.0 - 0.09, 0.055, 0.075),
            (0.0, py, rz), mat=RED, bev=0.006)
    for i in range(5):
        bx = -0.44 + i * 0.22
        box("Baluster", (0.035, 0.035, 0.42),
            (bx, py, DECK_Z + 0.71), mat=STEEL)

# waist bar across the slide entry so the mouth is guarded at the sides
for sy in (-1.0, 1.0):
    strut("EntryGuard",
          (DECK_HX - 0.05, sy * (DECK_HY - 0.05), DECK_Z + 0.92),
          (DECK_HX + 0.20, sy * (DECK_HY - 0.05), DECK_Z + 0.55),
          0.028, STEEL)

# ---- gable sunshade over the platform
ROOF_EAVE = POST_TOP
ROOF_APEX = POST_TOP + 0.42
for sy in (-1.0, 1.0):
    ang = math.atan2(ROOF_APEX - ROOF_EAVE, DECK_HY + 0.18)
    length = math.hypot(ROOF_APEX - ROOF_EAVE, DECK_HY + 0.18)
    box("RoofPanel_%d" % int(sy),
        (DECK_HX * 2.0 + 0.30, length, 0.035),
        (0.0, sy * (DECK_HY + 0.18) * 0.5, (ROOF_EAVE + ROOF_APEX) * 0.5),
        (sy * ang, 0.0, 0.0), mat=RED, bev=0.006)
box("RoofRidge", (DECK_HX * 2.0 + 0.34, 0.07, 0.06),
    (0.0, 0.0, ROOF_APEX + 0.02), mat=BLUE, bev=0.006)

# ---- the chute: swept U profile along a smoothstep descent
CHUTE_X0, CHUTE_X1 = 0.58, 3.95
CHUTE_Z0, CHUTE_Z1 = DECK_Z - 0.04, 0.20


def chute_path(t):
    s = t * t * (3.0 - 2.0 * t)          # smoothstep: flat top, flat run-out
    return Vector((CHUTE_X0 + (CHUTE_X1 - CHUTE_X0) * t,
                   0.0,
                   CHUTE_Z0 + (CHUTE_Z1 - CHUTE_Z0) * s))


PROFILE = [
    (-0.360, 0.300), (-0.352, 0.180), (-0.344, 0.075), (-0.326, 0.022),
    (-0.288, 0.000), (0.288, 0.000), (0.326, 0.022), (0.344, 0.075),
    (0.352, 0.180), (0.360, 0.300),
]
STEPS = 52

bm = bmesh.new()
rows = []
for i in range(STEPS):
    t = i / (STEPS - 1.0)
    p = chute_path(t)
    e = 1.0e-3
    tangent = chute_path(min(1.0, t + e)) - chute_path(max(0.0, t - e))
    tangent.normalize()
    normal = Vector((-tangent.z, 0.0, tangent.x))   # in-plane, pointing up
    side = Vector((0.0, 1.0, 0.0))
    rows.append([bm.verts.new(p + side * u + normal * v) for u, v in PROFILE])

for i in range(STEPS - 1):
    for j in range(len(PROFILE) - 1):
        bm.faces.new((rows[i][j], rows[i][j + 1],
                      rows[i + 1][j + 1], rows[i + 1][j]))

bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
chute_mesh = bpy.data.meshes.new("ChuteMesh")
bm.to_mesh(chute_mesh)
bm.free()
chute = bpy.data.objects.new("Chute", chute_mesh)
bpy.context.scene.collection.objects.link(chute)
assign(chute, YELLOW)
sol = chute.modifiers.new("Solidify", 'SOLIDIFY')
sol.thickness = 0.028
sol.offset = -1.0
sol.use_rim = True
smooth(chute, 45.0)

# chute entry hood joining the deck lip
box("ChuteLip", (0.30, 0.78, 0.05), (0.60, 0.0, DECK_Z - 0.02),
    (0.0, 0.0, 0.0), mat=YELLOW, bev=0.008)

# run-out end kerb
box("RunOutKerb", (0.12, 0.74, 0.10), (3.98, 0.0, 0.24), mat=BLUE, bev=0.01)

# ---- chute supports
mid = chute_path(0.52)
for sy in (-1.0, 1.0):
    strut("ChuteLeg", (mid.x, sy * 0.30, 0.0), (mid.x, sy * 0.30, mid.z),
          0.042, GREEN)
strut("ChuteLegTie", (mid.x, -0.30, 0.32), (mid.x, 0.30, 0.32), 0.03, GREEN)

end = chute_path(0.94)
for sy in (-1.0, 1.0):
    strut("ChuteEndLeg", (end.x, sy * 0.30, 0.0), (end.x, sy * 0.30, end.z),
          0.038, GREEN)

# ---- ladder on the -X side
LAD_BOT = Vector((-1.42, 0.0, 0.0))
LAD_TOP = Vector((-0.12, 0.0, DECK_Z - 0.02))
for sy in (-1.0, 1.0):
    y = sy * 0.40
    strut("Stringer_%d" % int(sy),
          (LAD_BOT.x, y, LAD_BOT.z), (LAD_TOP.x, y, LAD_TOP.z), 0.045, GREEN)

N_RUNGS = 6
for i in range(N_RUNGS):
    t = (i + 0.6) / (N_RUNGS + 0.2)
    px = LAD_BOT.x + (LAD_TOP.x - LAD_BOT.x) * t
    pz = LAD_BOT.z + (LAD_TOP.z - LAD_BOT.z) * t
    rung = box("Rung_%d" % i, (0.16, 0.80, 0.035), (px, 0.0, pz),
               mat=STEEL, bev=0.006)
    smooth(rung)

# handrails following the ladder pitch
for sy in (-1.0, 1.0):
    y = sy * 0.42
    strut("Handrail_%d" % int(sy),
          (LAD_BOT.x - 0.05, y, 0.86), (LAD_TOP.x, y, DECK_Z + 0.86), 0.028, RED)
    strut("HandrailStand_%d" % int(sy), (LAD_BOT.x - 0.05, y, 0.0),
          (LAD_BOT.x - 0.05, y, 0.86), 0.028, RED)
    strut("HandrailPost_%d" % int(sy), (LAD_TOP.x, y, DECK_Z - 0.02),
          (LAD_TOP.x, y, DECK_Z + 0.86), 0.028, RED)

# rubber landing mat at the foot of the ladder
bpy.ops.mesh.primitive_cylinder_add(vertices=32, radius=0.85, depth=0.04,
                                    location=(-1.65, 0.0, 0.03))
mat_pad = bpy.context.active_object
mat_pad.name = "LadderMat"
assign(mat_pad, RUBBER)
smooth(mat_pad)

# scattered pebbles for a little ground interest
for i in range(14):
    a = random.uniform(0.0, math.tau)
    r = random.uniform(4.2, 6.5)
    bpy.ops.mesh.primitive_ico_sphere_add(
        subdivisions=1, radius=random.uniform(0.05, 0.12),
        location=(0.9 + r * math.cos(a) * 1.2, r * math.sin(a), 0.03))
    st = bpy.context.active_object
    st.name = "Pebble"
    st.scale = (1.0, 1.0, 0.55)
    assign(st, DECKM)

# --------------------------------------------------------------- lighting
bpy.ops.object.light_add(type='SUN', location=(5.0, -6.0, 10.0))
sun = bpy.context.active_object
sun.name = "Sun"
sun.data.energy = 4.5
sun.data.angle = math.radians(2.5)
sun.data.color = (1.0, 0.96, 0.88)
look_at(sun, (0.5, 0.0, 1.0))

bpy.ops.object.light_add(type='AREA', location=(-5.0, 5.0, 5.0))
fill = bpy.context.active_object
fill.name = "Fill"
fill.data.energy = 350.0
fill.data.size = 6.0
fill.data.color = (0.72, 0.82, 1.0)
look_at(fill, (0.5, 0.0, 1.2))

# ----------------------------------------------------------------- camera
cam_data = bpy.data.cameras.new("Camera")
cam_data.lens = 42.0
cam = bpy.data.objects.new("Camera", cam_data)
cam.location = (5.6, -6.4, 3.3)
bpy.context.scene.collection.objects.link(cam)
look_at(cam, (0.7, 0.0, 1.25))
bpy.context.scene.camera = cam

print("claude-024 slide built: %d objects" % len(bpy.data.objects))
