import bpy
import bmesh
import math
from mathutils import Vector, Matrix

# Classic A-frame picnic table: long axis along +Y, benches offset along X.
LENGTH = 1.80
TOP_Z = 0.75
SEAT_Z = 0.45
FRAME_Y = 0.62      # leg frames sit this far from centre
PLANK_T = 0.035


def clear_scene():
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete(use_global=False)
    for coll in (bpy.data.meshes, bpy.data.materials):
        for block in list(coll):
            if block.users == 0:
                coll.remove(block)


def make_material(name, color, roughness=0.7, metallic=0.0):
    mat = bpy.data.materials.new(name)
    mat.use_nodes = True
    bsdf = mat.node_tree.nodes["Principled BSDF"]
    bsdf.inputs["Base Color"].default_value = (*color, 1.0)
    bsdf.inputs["Roughness"].default_value = roughness
    bsdf.inputs["Metallic"].default_value = metallic
    return mat


def box_mesh(bm, size, matrix):
    bmesh.ops.create_cube(bm, size=1.0,
                          matrix=matrix @ Matrix.Diagonal(Vector((*size, 1.0))))


def finish(bm, name, mat):
    me = bpy.data.meshes.new(name)
    bm.to_mesh(me)
    bm.free()
    ob = bpy.data.objects.new(name, me)
    ob.data.materials.append(mat)
    bpy.context.collection.objects.link(ob)
    return ob


def board(bm, size, loc):
    """Axis-aligned board added to an existing bmesh."""
    box_mesh(bm, size, Matrix.Translation(loc))


def strut(bm, p0, p1, width, thick, extend=0.0):
    """Board spanning p0..p1, `width` in the tilt plane, `thick` across it."""
    a, b = Vector(p0), Vector(p1)
    direction = b - a
    length = direction.length + extend
    quat = direction.to_track_quat('Z', 'Y')
    mat = Matrix.Translation((a + b) * 0.5) @ quat.to_matrix().to_4x4()
    box_mesh(bm, (width, thick, length), mat)


def plank_row(bm, count, plank_w, gap, centre_x, size_y, z):
    span = count * plank_w + (count - 1) * gap
    start = centre_x - span * 0.5 + plank_w * 0.5
    for i in range(count):
        board(bm, (plank_w, size_y, PLANK_T),
              (start + i * (plank_w + gap), 0.0, z))
    return span


clear_scene()

mat_top = make_material("Mat_PlankWood", (0.52, 0.34, 0.18), 0.72)
mat_frame = make_material("Mat_FrameWood", (0.38, 0.24, 0.13), 0.78)
mat_bolt = make_material("Mat_Hardware", (0.55, 0.56, 0.58), 0.35, metallic=1.0)
mat_ground = make_material("Mat_Ground", (0.28, 0.34, 0.22), 0.95)

# --- ground ---
bm = bmesh.new()
board(bm, (6.0, 6.0, 0.05), (0.0, 0.0, -0.025))
finish(bm, "Ground", mat_ground)

# --- table top planks ---
bm = bmesh.new()
top_span = plank_row(bm, 5, 0.13, 0.015, 0.0, LENGTH, TOP_Z - PLANK_T * 0.5)
finish(bm, "Tabletop_Planks", mat_top)

# --- bench planks (two per side) ---
bm = bmesh.new()
for side in (-1, 1):
    plank_row(bm, 2, 0.13, 0.015, side * 0.60, LENGTH, SEAT_Z - PLANK_T * 0.5)
finish(bm, "Bench_Planks", mat_top)

# --- A-frame legs, seat beams, top cleats ---
leg_foot_x = 0.80
leg_top_x = 0.24
bm = bmesh.new()
for sy in (-1, 1):
    y = sy * FRAME_Y
    for sx in (-1, 1):
        strut(bm,
              (sx * leg_foot_x, y, 0.0),
              (sx * leg_top_x, y, TOP_Z - PLANK_T),
              0.10, 0.038, extend=0.06)
    # seat beam the legs are notched against
    board(bm, (2 * leg_foot_x - 0.08, 0.045, 0.09), (0.0, y, SEAT_Z - PLANK_T - 0.045))
    # cleat under the tabletop
    board(bm, (top_span - 0.02, 0.045, 0.06), (0.0, y, TOP_Z - PLANK_T - 0.03))
finish(bm, "Leg_Frames", mat_frame)

# --- diagonal braces from tabletop centre down to the seat beams ---
bm = bmesh.new()
for sx in (-1, 1):
    for sy in (-1, 1):
        strut(bm,
              (sx * 0.06, sy * 0.10, TOP_Z - PLANK_T - 0.06),
              (sx * 0.55, sy * (FRAME_Y - 0.05), SEAT_Z - PLANK_T - 0.05),
              0.075, 0.030)
finish(bm, "Diagonal_Braces", mat_frame)

# --- bolt heads where the legs meet the frame members ---
bm = bmesh.new()
for sy in (-1, 1):
    for sx in (-1, 1):
        for z in (SEAT_Z - PLANK_T - 0.045, TOP_Z - PLANK_T - 0.09):
            t = z / (TOP_Z - PLANK_T)
            x = sx * (leg_foot_x - (leg_foot_x - leg_top_x) * t)
            m = Matrix.Translation((x, sy * (FRAME_Y - 0.028), z)) @ \
                Matrix.Rotation(math.radians(90.0), 4, 'X')
            bmesh.ops.create_cone(bm, cap_ends=True, cap_tris=False, segments=12,
                                  radius1=0.011, radius2=0.011, depth=0.014, matrix=m)
finish(bm, "Bolt_Heads", mat_bolt)

# --- lighting ---
sun_data = bpy.data.lights.new("Sun", type='SUN')
sun_data.energy = 3.5
sun = bpy.data.objects.new("Sun_Light", sun_data)
sun.rotation_euler = (math.radians(48.0), math.radians(12.0), math.radians(35.0))
bpy.context.collection.objects.link(sun)

fill_data = bpy.data.lights.new("Fill", type='AREA')
fill_data.energy = 180.0
fill_data.size = 3.0
fill = bpy.data.objects.new("Fill_Light", fill_data)
fill.location = (-2.5, 2.0, 2.6)
fill.rotation_euler = (math.radians(55.0), 0.0, math.radians(-125.0))
bpy.context.collection.objects.link(fill)

# --- camera ---
cam_data = bpy.data.cameras.new("Camera")
cam_data.lens = 40.0
cam = bpy.data.objects.new("Camera", cam_data)
cam.location = (2.6, -2.9, 1.95)
target = Vector((0.0, 0.0, 0.55))
cam.rotation_euler = (target - cam.location).to_track_quat('-Z', 'Y').to_euler()
bpy.context.collection.objects.link(cam)
bpy.context.scene.camera = cam
