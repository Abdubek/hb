import bpy
import bmesh
import math
from mathutils import Vector

# ---------------------------------------------------------------- utilities

def clear_scene():
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete(use_global=False)
    for coll in (bpy.data.meshes, bpy.data.materials, bpy.data.cameras, bpy.data.lights):
        for item in coll:
            if item.users == 0:
                coll.remove(item)


def make_material(name, color, roughness=0.6, metallic=0.0):
    mat = bpy.data.materials.new(name)
    mat.use_nodes = True
    bsdf = mat.node_tree.nodes["Principled BSDF"]
    bsdf.inputs["Base Color"].default_value = (*color, 1.0)
    bsdf.inputs["Roughness"].default_value = roughness
    bsdf.inputs["Metallic"].default_value = metallic
    return mat


def new_object(name, mat, parent):
    mesh = bpy.data.meshes.new(name)
    obj = bpy.data.objects.new(name, mesh)
    obj.data.materials.append(mat)
    bpy.context.collection.objects.link(obj)
    obj.parent = parent
    return obj


def beam(name, mat, parent, size, location, rotation=(0.0, 0.0, 0.0)):
    """Box built in local space, then placed with an object-level rotation."""
    obj = new_object(name, mat, parent)
    bm = bmesh.new()
    bmesh.ops.create_cube(bm, size=1.0)
    bmesh.ops.scale(bm, vec=Vector(size), verts=bm.verts)
    bm.normal_update()
    bm.to_mesh(obj.data)
    bm.free()
    obj.location = location
    obj.rotation_euler = rotation
    return obj


def post(name, mat, parent, radius, height, location, segments=12):
    """Slightly tapered upright whose origin sits at its foot."""
    obj = new_object(name, mat, parent)
    bm = bmesh.new()
    bmesh.ops.create_cone(bm, cap_ends=True, cap_tris=False, segments=segments,
                          radius1=radius, radius2=radius * 0.92, depth=height)
    bmesh.ops.translate(bm, vec=Vector((0.0, 0.0, height * 0.5)), verts=bm.verts)
    bm.normal_update()
    bm.to_mesh(obj.data)
    bm.free()
    obj.location = location
    return obj

# ---------------------------------------------------------------- build

clear_scene()

mat_deck = make_material("MAT_Deck_Plank", (0.46, 0.30, 0.17), roughness=0.75)
mat_frame = make_material("MAT_Frame_Timber", (0.33, 0.21, 0.12), roughness=0.8)
mat_rail = make_material("MAT_Rail_Timber", (0.55, 0.38, 0.22), roughness=0.7)
mat_metal = make_material("MAT_Bracket_Steel", (0.25, 0.26, 0.28), roughness=0.4, metallic=0.9)
mat_stone = make_material("MAT_Abutment_Stone", (0.55, 0.54, 0.50), roughness=0.9)
mat_water = make_material("MAT_Water", (0.10, 0.24, 0.30), roughness=0.12)

root = bpy.data.objects.new("FOOTBRIDGE_ROOT", None)
bpy.context.collection.objects.link(root)

SPAN = 8.0          # along X
WIDTH = 1.8         # along Y
DECK_Z = 1.05       # top surface of the planks
PLANK_T = 0.06

# --- Stringers (two main longitudinal beams) and cross joists ---
for side, sy in (("L", -1.0), ("R", 1.0)):
    beam("Stringer_%s" % side, mat_frame, root,
         (SPAN, 0.14, 0.30), (0.0, sy * (WIDTH * 0.5 - 0.14), DECK_Z - PLANK_T - 0.15))

N_JOIST = 7
for i in range(N_JOIST):
    x = (-SPAN * 0.5 + SPAN * (i / (N_JOIST - 1.0))) * 0.94
    beam("Joist_%02d" % i, mat_frame, root,
         (0.10, WIDTH - 0.10, 0.14), (x, 0.0, DECK_Z - PLANK_T - 0.22))

# --- Deck planks laid across the span with small expansion gaps ---
N_PLANK = 34
pitch = SPAN / N_PLANK
for i in range(N_PLANK):
    x = -SPAN * 0.5 + pitch * (i + 0.5)
    beam("Deck_Plank_%02d" % i, mat_deck, root,
         (pitch - 0.015, WIDTH, PLANK_T), (x, 0.0, DECK_Z - PLANK_T * 0.5))

# --- Railings: posts, top rail, mid rail, kick rail, diagonal braces ---
POST_H = 1.05
N_POST = 6
post_xs = [-SPAN * 0.5 + (SPAN * 0.92) * (i / (N_POST - 1.0)) for i in range(N_POST)]
rail_y = WIDTH * 0.5 - 0.08

for side, sy in (("L", -1.0), ("R", 1.0)):
    for i, x in enumerate(post_xs):
        post("Rail_Post_%s_%02d" % (side, i), mat_rail, root,
             0.055, POST_H, (x, sy * rail_y, DECK_Z - 0.02))
        beam("Post_Bracket_%s_%02d" % (side, i), mat_metal, root,
             (0.14, 0.05, 0.10), (x, sy * (rail_y + 0.05), DECK_Z + 0.06))

    beam("Top_Rail_%s" % side, mat_rail, root,
         (SPAN * 0.96, 0.10, 0.08), (0.0, sy * rail_y, DECK_Z + POST_H))
    beam("Mid_Rail_%s" % side, mat_rail, root,
         (SPAN * 0.94, 0.07, 0.06), (0.0, sy * rail_y, DECK_Z + POST_H * 0.55))
    beam("Kick_Rail_%s" % side, mat_rail, root,
         (SPAN * 0.94, 0.07, 0.09), (0.0, sy * rail_y, DECK_Z + 0.10))

    # Alternating diagonal braces between post bays for lateral stiffness
    for i in range(N_POST - 1):
        x0, x1 = post_xs[i], post_xs[i + 1]
        bay = x1 - x0
        rise = POST_H * 0.45
        length = math.hypot(bay, rise)
        angle = math.atan2(rise, bay)
        sign = 1.0 if i % 2 == 0 else -1.0
        beam("Brace_%s_%02d" % (side, i), mat_rail, root,
             (length, 0.045, 0.045),
             ((x0 + x1) * 0.5, sy * (rail_y - 0.06), DECK_Z + POST_H * 0.32),
             rotation=(0.0, -sign * angle, 0.0))

# --- Stone abutments at both ends plus banks and stream ---
for side, sx in (("West", -1.0), ("East", 1.0)):
    beam("Abutment_%s" % side, mat_stone, root,
         (1.2, WIDTH + 0.6, 1.0), (sx * (SPAN * 0.5 + 0.35), 0.0, 0.35))
    beam("Approach_Slab_%s" % side, mat_stone, root,
         (1.6, WIDTH + 0.2, 0.12), (sx * (SPAN * 0.5 + 1.6), 0.0, 0.83))

beam("Bank_West", mat_stone, root, (4.0, 6.0, 0.7), (-6.2, 0.0, 0.15))
beam("Bank_East", mat_stone, root, (4.0, 6.0, 0.7), (6.2, 0.0, 0.15))
beam("Stream_Surface", mat_water, root, (9.0, 6.0, 0.04), (0.0, 0.0, -0.20))

# --- Lighting and camera ---
sun_data = bpy.data.lights.new("KEY_Sun", type='SUN')
sun_data.energy = 3.5
sun = bpy.data.objects.new("KEY_Sun", sun_data)
sun.rotation_euler = (0.72, 0.18, -0.95)
bpy.context.collection.objects.link(sun)

fill_data = bpy.data.lights.new("FILL_Area", type='AREA')
fill_data.energy = 400.0
fill_data.size = 8.0
fill = bpy.data.objects.new("FILL_Area", fill_data)
fill.location = (-7.0, -8.0, 6.0)
fill.rotation_euler = (0.95, -0.35, -0.6)
bpy.context.collection.objects.link(fill)

cam_data = bpy.data.cameras.new("SceneCamera")
cam_data.lens = 42.0
cam = bpy.data.objects.new("SceneCamera", cam_data)
cam.location = (9.0, -11.0, 5.5)
bpy.context.collection.objects.link(cam)
bpy.context.scene.camera = cam

target = bpy.data.objects.new("CameraTarget", None)
target.location = (0.0, 0.0, 1.3)
bpy.context.collection.objects.link(target)
track = cam.constraints.new(type='TRACK_TO')
track.target = target
track.track_axis = 'TRACK_NEGATIVE_Z'
track.up_axis = 'UP_Y'

bpy.context.view_layer.update()
print("Footbridge scene built: %d objects" % len(bpy.context.collection.objects))
