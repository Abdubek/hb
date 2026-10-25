"""claude-021 - Garden pergola with overhead slats.

Builds a free-standing timber pergola: stone footings, six posts, doubled
side beams, cross rafters, a run of overhead slats, knee braces, a paved
floor slab and a pair of planters.  Scene only - nothing is rendered.
"""

import bpy
import bmesh
import math
import random
from mathutils import Vector


# --------------------------------------------------------------- utilities
def reset_scene():
    bpy.ops.wm.read_factory_settings(use_empty=True)


def make_material(name, color, rough=0.6, metal=0.0):
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


def bevel(obj, width=0.008, segments=2):
    mod = obj.modifiers.new("Bevel", 'BEVEL')
    mod.width = width
    mod.segments = segments
    mod.limit_method = 'ANGLE'
    mod.angle_limit = math.radians(35.0)
    return obj


def box(name, size, location, rotation=(0.0, 0.0, 0.0), mat=None):
    """Axis aligned cube with real world dimensions (scale is applied)."""
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=location, rotation=rotation)
    obj = bpy.context.active_object
    obj.name = name
    obj.scale = size
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    if mat:
        assign(obj, mat)
    return obj


def bar(name, p1, p2, width, height, mat=None):
    """Rectangular timber running from p1 to p2.

    `width` is horizontal, `height` vertical for non-vertical members.
    """
    a, b = Vector(p1), Vector(p2)
    d = b - a
    length = d.length
    if length < 1e-6:
        return None
    rot = d.to_track_quat('Z', 'Y').to_euler()
    return box(name, (width, height, length), (a + b) * 0.5, rot, mat)


def smooth(obj, angle=32.0):
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


def look_at(obj, target):
    direction = Vector(target) - obj.location
    obj.rotation_euler = direction.to_track_quat('-Z', 'Y').to_euler()


def setup_world(color=(0.32, 0.46, 0.68), strength=1.1):
    world = bpy.data.worlds.new("World")
    world.use_nodes = True
    bg = world.node_tree.nodes["Background"]
    bg.inputs[0].default_value = (color[0], color[1], color[2], 1.0)
    bg.inputs[1].default_value = strength
    bpy.context.scene.world = world
    return world


# ------------------------------------------------------------------- scene
reset_scene()
setup_world()
random.seed(7)

WOOD = make_material("WoodCedar", (0.42, 0.24, 0.12), rough=0.68)
WOOD_DK = make_material("WoodPost", (0.33, 0.18, 0.09), rough=0.72)
STONE = make_material("Stone", (0.62, 0.60, 0.56), rough=0.85)
PAVING = make_material("Paving", (0.70, 0.68, 0.63), rough=0.88)
GRASS = make_material("Grass", (0.16, 0.32, 0.10), rough=0.95)
TERRA = make_material("Terracotta", (0.55, 0.26, 0.16), rough=0.75)
LEAF = make_material("Foliage", (0.14, 0.34, 0.12), rough=0.85)
SOIL = make_material("Soil", (0.14, 0.10, 0.07), rough=0.95)

# ---- ground and paving
bpy.ops.mesh.primitive_plane_add(size=26.0, location=(0.0, 0.0, 0.0))
ground = bpy.context.active_object
ground.name = "Ground"
assign(ground, GRASS)

slab = box("PavingSlab", (5.4, 4.2, 0.08), (0.0, 0.0, 0.04), mat=PAVING)
bevel(slab, 0.012)

# joint lines in the paving, four rows of large flags
for gx in (-1.8, 0.0, 1.8):
    box("PaveJointX", (0.03, 4.2, 0.02), (gx, 0.0, 0.085), mat=STONE)
for gy in (-1.4, 0.0, 1.4):
    box("PaveJointY", (5.4, 0.03, 0.02), (0.0, gy, 0.085), mat=STONE)

# ---- posts
POST = 0.16
POST_H = 2.50
POST_X = (-2.4, 0.0, 2.4)
POST_Y = (-1.8, 1.8)

for ix, px in enumerate(POST_X):
    for iy, py in enumerate(POST_Y):
        footing = box("Footing_%d_%d" % (ix, iy), (0.34, 0.34, 0.16),
                      (px, py, 0.08), mat=STONE)
        bevel(footing, 0.02)
        post = box("Post_%d_%d" % (ix, iy), (POST, POST, POST_H),
                   (px, py, 0.16 + POST_H * 0.5), mat=WOOD_DK)
        bevel(post, 0.012)
        # small cap moulding just under the beams
        box("PostCap_%d_%d" % (ix, iy), (0.24, 0.24, 0.05),
            (px, py, 0.16 + POST_H - 0.02), mat=WOOD_DK)

TOP = 0.16 + POST_H          # 2.66 - underside of the beams

# ---- doubled side beams sandwiching the posts
BEAM_H = 0.30
for iy, py in enumerate(POST_Y):
    for k, dy in enumerate((-0.135, 0.135)):
        beam = box("Beam_%d_%d" % (iy, k), (5.6, 0.07, BEAM_H),
                   (0.0, py + dy, TOP + BEAM_H * 0.5), mat=WOOD)
        bevel(beam, 0.008)
        # shaped beam ends: chamfer blocks at each tip
        for sx in (-1.0, 1.0):
            box("BeamTip_%d_%d" % (iy, k), (0.16, 0.07, 0.16),
                (sx * 2.80, py + dy, TOP + 0.08),
                (0.0, math.radians(45.0), 0.0), mat=WOOD)

BEAM_TOP = TOP + BEAM_H

# ---- rafters running across the short axis
RAF_H = 0.22
n_raf = 13
for i in range(n_raf):
    x = -2.7 + 5.4 * i / (n_raf - 1.0)
    rafter = box("Rafter_%02d" % i, (0.075, 4.35, RAF_H),
                 (x, 0.0, BEAM_TOP + RAF_H * 0.5), mat=WOOD)
    bevel(rafter, 0.007)
    for sy in (-1.0, 1.0):
        box("RafterTip_%02d" % i, (0.075, 0.12, 0.12),
            (x, sy * 2.175, BEAM_TOP + 0.06),
            (math.radians(45.0), 0.0, 0.0), mat=WOOD)

RAF_TOP = BEAM_TOP + RAF_H

# ---- overhead slats
n_slat = 21
for i in range(n_slat):
    y = -2.05 + 4.10 * i / (n_slat - 1.0)
    slat = box("Slat_%02d" % i, (5.85, 0.045, 0.09),
               (0.0, y, RAF_TOP + 0.045), mat=WOOD)
    bevel(slat, 0.005)

# ---- knee braces
for px in POST_X:
    for s in (-1.0, 1.0):
        if abs(px) > 1.0 and px * s > 0.0:
            continue                      # would overhang the beam ends
    # rebuilt below with explicit skip logic
for px in POST_X:
    for s in (-1.0, 1.0):
        if abs(px) > 1.0 and (px * s) > 0.0:
            continue
        for py in POST_Y:
            p1 = (px + s * 0.07, py, TOP - 0.52)
            p2 = (px + s * 0.50, py, TOP + 0.04)
            brace = bar("Brace", p1, p2, 0.07, 0.14, WOOD_DK)
            if brace:
                bevel(brace, 0.006)

# ---- planters with shrubs
for sx in (-1.0, 1.0):
    cx, cy = sx * 3.05, -2.25
    pot = box("Planter_%d" % int(sx), (0.62, 0.62, 0.52),
              (cx, cy, 0.26), mat=TERRA)
    bevel(pot, 0.02)
    box("PlanterRim_%d" % int(sx), (0.70, 0.70, 0.07), (cx, cy, 0.50), mat=TERRA)
    box("Soil_%d" % int(sx), (0.56, 0.56, 0.04), (cx, cy, 0.515), mat=SOIL)
    for b in range(9):
        r = random.uniform(0.0, 0.24)
        a = random.uniform(0.0, math.tau)
        h = 0.58 + random.uniform(0.0, 0.55)
        bpy.ops.mesh.primitive_ico_sphere_add(
            subdivisions=2, radius=random.uniform(0.13, 0.22),
            location=(cx + r * math.cos(a), cy + r * math.sin(a), h))
        blob = bpy.context.active_object
        blob.name = "Foliage"
        blob.scale = (1.0, 1.0, random.uniform(0.7, 1.1))
        assign(blob, LEAF)
        smooth(blob)

# ---- climbing stems threaded over two of the slats
for sx in (-1.0, 1.0):
    px = sx * 2.4
    stem = bar("Vine", (px + sx * 0.11, 1.8, 0.2), (px + sx * 0.11, 1.8, TOP + 0.6),
               0.035, 0.035, LEAF)
    smooth(stem)

# --------------------------------------------------------------- lighting
bpy.ops.object.light_add(type='SUN', location=(6.0, -7.0, 12.0))
sun = bpy.context.active_object
sun.name = "Sun"
sun.data.energy = 4.2
sun.data.angle = math.radians(1.8)
sun.data.color = (1.0, 0.95, 0.86)
look_at(sun, (0.0, 0.0, 1.0))

bpy.ops.object.light_add(type='AREA', location=(-6.0, 5.0, 6.0))
fill = bpy.context.active_object
fill.name = "Fill"
fill.data.energy = 300.0
fill.data.size = 6.0
fill.data.color = (0.72, 0.82, 1.0)
look_at(fill, (0.0, 0.0, 1.6))

# ----------------------------------------------------------------- camera
cam_data = bpy.data.cameras.new("Camera")
cam_data.lens = 40.0
cam = bpy.data.objects.new("Camera", cam_data)
cam.location = (7.6, -8.2, 4.4)
bpy.context.scene.collection.objects.link(cam)
look_at(cam, (0.0, 0.0, 1.55))
bpy.context.scene.camera = cam

print("claude-021 pergola built: %d objects" % len(bpy.data.objects))
