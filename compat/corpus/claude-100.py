"""claude-100 - A small pedestrian station platform with canopy and benches.

A single concrete platform beside a ballasted track: tactile warning studs and
a painted safety line at the platform edge, a steel column canopy with rafters
and fascia, a glazed windbreak, two slatted timber benches, a name sign, litter
bin and lamps.  Daylight sun plus sky, with a three quarter camera.
"""

import bpy
import bmesh
import math
from mathutils import Vector, Matrix


# --------------------------------------------------------------------------
# generic helpers
# --------------------------------------------------------------------------
def reset_scene():
    bpy.ops.wm.read_factory_settings(use_empty=True)
    bpy.context.scene.unit_settings.system = 'METRIC'


def make_world(color=(0.32, 0.47, 0.68), strength=1.2):
    world = bpy.data.worlds.new("World")
    world.use_nodes = True
    bg = world.node_tree.nodes["Background"]
    bg.inputs[0].default_value = (*color, 1.0)
    bg.inputs[1].default_value = strength
    bpy.context.scene.world = world
    return world


def mat_pbr(name, color, metallic=0.0, roughness=0.5, alpha=1.0,
            emission=None, emit_strength=0.0):
    mat = bpy.data.materials.new(name)
    mat.use_nodes = True
    bsdf = mat.node_tree.nodes["Principled BSDF"]
    bsdf.inputs["Base Color"].default_value = (*color, 1.0)
    bsdf.inputs["Metallic"].default_value = metallic
    bsdf.inputs["Roughness"].default_value = roughness
    if emission is not None and "Emission Color" in bsdf.inputs:
        bsdf.inputs["Emission Color"].default_value = (*emission, 1.0)
        bsdf.inputs["Emission Strength"].default_value = emit_strength
    if alpha < 1.0:
        bsdf.inputs["Alpha"].default_value = alpha
        try:
            mat.blend_method = 'BLEND'
        except Exception:
            pass
    return mat


def assign(obj, mat):
    if mat is not None:
        obj.data.materials.append(mat)
    return obj


def box(name, size, loc, mat=None, rot=(0.0, 0.0, 0.0)):
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=loc, rotation=rot)
    ob = bpy.context.object
    ob.name = name
    ob.scale = size
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    return assign(ob, mat)


def cyl(name, radius, depth, loc, mat=None, rot=(0.0, 0.0, 0.0), verts=24):
    bpy.ops.mesh.primitive_cylinder_add(radius=radius, depth=depth,
                                        vertices=verts, location=loc,
                                        rotation=rot)
    ob = bpy.context.object
    ob.name = name
    return assign(ob, mat)


def torus(name, major, minor, loc, mat=None, rot=(0.0, 0.0, 0.0),
          maj_seg=32, min_seg=8):
    bpy.ops.mesh.primitive_torus_add(major_radius=major, minor_radius=minor,
                                     major_segments=maj_seg,
                                     minor_segments=min_seg,
                                     location=loc, rotation=rot)
    ob = bpy.context.object
    ob.name = name
    return assign(ob, mat)


def bevel_mod(obj, width=0.008, segments=2, angle=40.0):
    m = obj.modifiers.new("Bevel", 'BEVEL')
    m.width = width
    m.segments = segments
    m.limit_method = 'ANGLE'
    m.angle_limit = math.radians(angle)
    return obj


def smooth(obj, angle=40.0):
    try:
        for o in bpy.context.selected_objects:
            o.select_set(False)
        obj.select_set(True)
        bpy.context.view_layer.objects.active = obj
        bpy.ops.object.shade_auto_smooth(angle=math.radians(angle))
    except Exception:
        for p in obj.data.polygons:
            p.use_smooth = True
    return obj


def look_at(obj, target):
    d = Vector(target) - obj.location
    obj.rotation_euler = d.to_track_quat('-Z', 'Y').to_euler()


# --------------------------------------------------------------------------
# layout constants (platform runs along X, track lies to -Y)
# --------------------------------------------------------------------------
P_LEN = 12.0
P_WID = 3.20
P_H = 0.95
EDGE_Y = -P_WID / 2.0          # track side edge
BACK_Y = P_WID / 2.0
TRACK_Y = -3.25


def build_materials():
    return {
        "concrete": mat_pbr("Concrete", (0.56, 0.555, 0.54), 0.0, 0.78),
        "concrete2": mat_pbr("ConcreteEdge", (0.62, 0.615, 0.60), 0.0, 0.70),
        "paving": mat_pbr("Paving", (0.50, 0.495, 0.485), 0.0, 0.82),
        "yellow": mat_pbr("SafetyYellow", (0.86, 0.66, 0.06), 0.0, 0.55),
        "steel": mat_pbr("PaintedSteel", (0.16, 0.30, 0.34), 0.15, 0.42),
        "steel_gal": mat_pbr("Galvanised", (0.62, 0.63, 0.65), 0.9, 0.42),
        "roof": mat_pbr("RoofSheet", (0.42, 0.44, 0.46), 0.8, 0.38),
        "glass": mat_pbr("Windbreak", (0.65, 0.74, 0.76), 0.0, 0.06, alpha=0.28),
        "wood": mat_pbr("BenchTimber", (0.44, 0.28, 0.15), 0.0, 0.62),
        "rail": mat_pbr("RailSteel", (0.36, 0.33, 0.30), 0.9, 0.35),
        "rail_head": mat_pbr("RailHead", (0.70, 0.70, 0.72), 1.0, 0.15),
        "sleeper": mat_pbr("Sleeper", (0.22, 0.18, 0.14), 0.0, 0.85),
        "ballast": mat_pbr("Ballast", (0.31, 0.30, 0.29), 0.0, 0.92),
        "ground": mat_pbr("Ground", (0.26, 0.30, 0.19), 0.0, 0.90),
        "sign_blue": mat_pbr("SignBlue", (0.05, 0.16, 0.42), 0.0, 0.35),
        "sign_white": mat_pbr("SignWhite", (0.90, 0.90, 0.88), 0.0, 0.40),
        "lamp": mat_pbr("LampDiffuser", (0.95, 0.95, 0.90), 0.0, 0.30,
                        emission=(1.0, 0.96, 0.88), emit_strength=4.0),
        "bin": mat_pbr("LitterBin", (0.14, 0.26, 0.30), 0.3, 0.45),
    }


# --------------------------------------------------------------------------
# platform deck
# --------------------------------------------------------------------------
def build_platform(M):
    parts = []
    slab = box("PlatformSlab", (P_LEN, P_WID, P_H), (0.0, 0.0, P_H / 2.0),
               M["concrete"])
    bevel_mod(slab, 0.02, 2)
    parts.append(slab)

    # cast coping units along the track edge
    n = 16
    seg = P_LEN / n
    for i in range(n):
        x = -P_LEN / 2.0 + seg * (i + 0.5)
        c = box("Coping_%02d" % i, (seg - 0.012, 0.42, P_H + 0.012),
                (x, EDGE_Y + 0.21, (P_H + 0.012) / 2.0), M["concrete2"])
        bevel_mod(c, 0.012, 2)
        parts.append(c)

    # paving slab grid on the deck surface
    cols, rows = 20, 5
    sx = P_LEN / cols
    sy = (P_WID - 0.50) / rows
    for i in range(cols):
        for j in range(rows):
            x = -P_LEN / 2.0 + sx * (i + 0.5)
            y = EDGE_Y + 0.50 + sy * (j + 0.5)
            parts.append(box("Paver_%02d_%d" % (i, j),
                             (sx - 0.02, sy - 0.02, 0.02),
                             (x, y, P_H + 0.008), M["paving"]))

    # painted safety line
    parts.append(box("SafetyLine", (P_LEN - 0.10, 0.10, 0.006),
                     (0.0, EDGE_Y + 0.52, P_H + 0.020), M["yellow"]))

    # tactile warning surface: one mesh holding all the studs
    bm = bmesh.new()
    rows_y = [EDGE_Y + 0.12, EDGE_Y + 0.24, EDGE_Y + 0.36, EDGE_Y + 0.48]
    nx = 60
    for j, y in enumerate(rows_y):
        off = 0.05 if j % 2 else 0.0
        for i in range(nx):
            x = -P_LEN / 2.0 + 0.15 + i * (P_LEN - 0.30) / (nx - 1) + off
            mat_loc = Matrix.Translation((x, y, P_H + 0.012))
            bmesh.ops.create_cone(bm, cap_ends=True, cap_tris=False,
                                  segments=8, radius1=0.024, radius2=0.020,
                                  depth=0.014, matrix=mat_loc)
    me = bpy.data.meshes.new("TactileStuds")
    bm.normal_update()
    bm.to_mesh(me)
    bm.free()
    studs = bpy.data.objects.new("TactileStuds", me)
    bpy.context.collection.objects.link(studs)
    assign(studs, M["yellow"])
    parts.append(studs)

    parts.append(box("TactileBase", (P_LEN - 0.20, 0.46, 0.014),
                     (0.0, EDGE_Y + 0.30, P_H + 0.010), M["yellow"]))

    # ramp down at the far end of the platform
    ramp = box("Ramp", (1.60, P_WID - 0.4, 0.10),
               (P_LEN / 2.0 + 0.70, 0.20, P_H - 0.30), M["concrete"],
               rot=(0.0, math.radians(21.0), 0.0))
    parts.append(ramp)
    return parts


# --------------------------------------------------------------------------
# track
# --------------------------------------------------------------------------
def build_track(M):
    parts = []
    bpy.ops.mesh.primitive_plane_add(size=60.0, location=(0.0, -4.0, -0.02))
    ground = bpy.context.object
    ground.name = "Ground"
    assign(ground, M["ground"])
    parts.append(ground)

    ballast = box("Ballast", (18.0, 3.40, 0.40), (0.0, TRACK_Y, 0.16),
                  M["ballast"])
    parts.append(ballast)

    n = 22
    for i in range(n):
        x = -8.4 + i * (16.8 / (n - 1))
        parts.append(box("Sleeper_%02d" % i, (0.26, 2.50, 0.15),
                         (x, TRACK_Y, 0.42), M["sleeper"]))

    for sy in (-1, 1):
        y = TRACK_Y + sy * 0.7175
        web = box("RailWeb_%d" % (sy + 1), (18.0, 0.030, 0.110),
                  (0.0, y, 0.545), M["rail"])
        parts.append(web)
        parts.append(box("RailFoot_%d" % (sy + 1), (18.0, 0.110, 0.024),
                         (0.0, y, 0.502), M["rail"]))
        head = box("RailHead_%d" % (sy + 1), (18.0, 0.070, 0.036),
                   (0.0, y, 0.612), M["rail_head"])
        bevel_mod(head, 0.006, 2)
        parts.append(head)
    return parts


# --------------------------------------------------------------------------
# canopy
# --------------------------------------------------------------------------
COL_Y = 0.95
COL_TOP = 3.05


def build_canopy(M):
    parts = []
    col_x = (-3.9, -1.3, 1.3, 3.9)
    for i, x in enumerate(col_x):
        base = box("ColBase_%d" % i, (0.26, 0.26, 0.05), (x, COL_Y, P_H + 0.045),
                   M["steel_gal"])
        bevel_mod(base, 0.006, 2)
        parts.append(base)
        col = cyl("Column_%d" % i, 0.075, COL_TOP - P_H,
                  (x, COL_Y, P_H + (COL_TOP - P_H) / 2.0), M["steel"], verts=20)
        smooth(col)
        parts.append(col)
        for j in range(4):
            a = 2.0 * math.pi * j / 4.0
            parts.append(cyl("ColBolt_%d_%d" % (i, j), 0.014, 0.030,
                             (x + 0.10 * math.cos(a), COL_Y + 0.10 * math.sin(a),
                              P_H + 0.055), M["steel_gal"], verts=8))
        # bracket flaring out to the rafter
        parts.append(box("Bracket_%d" % i, (0.10, 0.55, 0.10),
                         (x, COL_Y - 0.32, COL_TOP - 0.22), M["steel"],
                         rot=(math.radians(28.0), 0.0, 0.0)))
        parts.append(cyl("ColCap_%d" % i, 0.095, 0.05, (x, COL_Y, COL_TOP),
                         M["steel_gal"], verts=20))

    beam = box("MainBeam", (9.4, 0.17, 0.26), (0.0, COL_Y, COL_TOP + 0.13),
               M["steel"])
    bevel_mod(beam, 0.010, 2)
    parts.append(beam)

    # rafters spanning across the platform, tilted towards the track
    for i in range(9):
        x = -4.0 + i * 1.0
        parts.append(box("Rafter_%02d" % i, (0.09, 3.10, 0.13),
                         (x, 0.80, COL_TOP + 0.33), M["steel"],
                         rot=(math.radians(-4.0), 0.0, 0.0)))

    deck = box("RoofDeck", (9.6, 3.20, 0.055), (0.0, 0.80, COL_TOP + 0.43),
               M["roof"], rot=(math.radians(-4.0), 0.0, 0.0))
    bevel_mod(deck, 0.008, 2)
    parts.append(deck)

    # standing seams on the roof sheet
    for i in range(13):
        x = -4.6 + i * 0.766
        parts.append(box("Seam_%02d" % i, (0.035, 3.16, 0.045),
                         (x, 0.80, COL_TOP + 0.475), M["roof"],
                         rot=(math.radians(-4.0), 0.0, 0.0)))

    fascia = box("Fascia", (9.6, 0.06, 0.22), (0.0, -0.78, COL_TOP + 0.42),
                 M["steel"])
    bevel_mod(fascia, 0.008, 2)
    parts.append(fascia)
    parts.append(box("RearGutter", (9.6, 0.10, 0.12), (0.0, 2.38, COL_TOP + 0.55),
                     M["steel_gal"]))

    # downpipes on the outer columns
    for x in (-3.9, 3.9):
        parts.append(cyl("Downpipe_%d" % int(x), 0.038, COL_TOP - P_H + 0.4,
                         (x + 0.13, COL_Y + 0.12,
                          P_H + (COL_TOP - P_H + 0.4) / 2.0), M["steel_gal"],
                         verts=14))

    # under canopy lights
    for x in (-2.6, 0.0, 2.6):
        parts.append(box("LampBody_%d" % int(x * 10), (1.30, 0.16, 0.09),
                         (x, 0.55, COL_TOP + 0.22), M["steel_gal"]))
        parts.append(box("LampLens_%d" % int(x * 10), (1.20, 0.12, 0.030),
                         (x, 0.55, COL_TOP + 0.166), M["lamp"]))
        ld = bpy.data.lights.new("CanopyLight", 'AREA')
        ld.energy = 60.0
        ld.shape = 'RECTANGLE'
        ld.size = 1.2
        ld.size_y = 0.12
        lo = bpy.data.objects.new("CanopyLight_%d" % int(x * 10), ld)
        lo.location = (x, 0.55, COL_TOP + 0.14)
        lo.rotation_euler = (math.pi, 0.0, 0.0)
        bpy.context.collection.objects.link(lo)
        parts.append(lo)
    return parts


def build_windbreak(M):
    parts = []
    y = 1.42
    for i, cx in enumerate((-2.6, 2.6)):
        for sx in (-1, 1):
            parts.append(box("WbPost_%d_%d" % (i, sx + 1),
                             (0.08, 0.10, 1.90),
                             (cx + sx * 1.20, y, P_H + 0.95), M["steel"]))
        parts.append(box("WbRailTop_%d" % i, (2.48, 0.09, 0.09),
                         (cx, y, P_H + 1.86), M["steel"]))
        parts.append(box("WbRailBot_%d" % i, (2.48, 0.09, 0.09),
                         (cx, y, P_H + 0.14), M["steel"]))
        parts.append(box("WbGlass_%d" % i, (2.32, 0.020, 1.66),
                         (cx, y, P_H + 1.00), M["glass"]))
        parts.append(box("WbMullion_%d" % i, (0.05, 0.04, 1.66),
                         (cx, y, P_H + 1.00), M["steel"]))
    return parts


# --------------------------------------------------------------------------
# furniture
# --------------------------------------------------------------------------
def build_bench(M, bx, by, index):
    parts = []
    z0 = P_H
    seat_z = z0 + 0.45
    half = 0.70
    for sx in (-1, 1):
        x = bx + sx * half
        parts.append(box("BenchLegF_%d_%d" % (index, sx + 1),
                         (0.055, 0.070, 0.45), (x, by - 0.20, z0 + 0.225),
                         M["steel"]))
        parts.append(box("BenchLegB_%d_%d" % (index, sx + 1),
                         (0.055, 0.070, 0.92), (x, by + 0.21, z0 + 0.46),
                         M["steel"]))
        parts.append(box("BenchRail_%d_%d" % (index, sx + 1),
                         (0.055, 0.480, 0.055), (x, by, seat_z), M["steel"]))
        parts.append(box("BenchFoot_%d_%d" % (index, sx + 1),
                         (0.13, 0.16, 0.02), (x, by - 0.20, z0 + 0.012),
                         M["steel_gal"]))
        parts.append(box("BenchFootB_%d_%d" % (index, sx + 1),
                         (0.13, 0.16, 0.02), (x, by + 0.21, z0 + 0.012),
                         M["steel_gal"]))
        # arm rest
        parts.append(box("BenchArm_%d_%d" % (index, sx + 1),
                         (0.05, 0.46, 0.05), (x, by - 0.02, seat_z + 0.24),
                         M["wood"]))
        parts.append(box("BenchArmPost_%d_%d" % (index, sx + 1),
                         (0.045, 0.06, 0.24), (x, by - 0.22, seat_z + 0.12),
                         M["steel"]))

    for i in range(4):
        y = by - 0.175 + i * 0.117
        s = box("BenchSeat_%d_%d" % (index, i), (1.46, 0.088, 0.032),
                (bx, y, seat_z + 0.042), M["wood"])
        bevel_mod(s, 0.006, 2)
        parts.append(s)

    for i in range(3):
        z = seat_z + 0.19 + i * 0.145
        s = box("BenchBack_%d_%d" % (index, i), (1.46, 0.032, 0.105),
                (bx, by + 0.215 + i * 0.022, z), M["wood"],
                rot=(math.radians(-9.0), 0.0, 0.0))
        bevel_mod(s, 0.005, 2)
        parts.append(s)
    return parts


def build_furniture(M):
    parts = []
    parts += build_bench(M, -2.55, 1.00, 0)
    parts += build_bench(M, 2.55, 1.00, 1)

    # litter bin
    bin_x, bin_y = 0.05, 1.05
    body = cyl("BinBody", 0.24, 0.78, (bin_x, bin_y, P_H + 0.39), M["bin"],
               verts=24)
    smooth(body)
    parts.append(body)
    rim = torus("BinRim", 0.245, 0.022, (bin_x, bin_y, P_H + 0.78),
                M["steel_gal"], maj_seg=28, min_seg=8)
    smooth(rim)
    parts.append(rim)
    lid = cyl("BinLid", 0.20, 0.05, (bin_x, bin_y, P_H + 0.815), M["steel_gal"],
              verts=24)
    smooth(lid)
    parts.append(lid)
    parts.append(cyl("BinFoot", 0.20, 0.04, (bin_x, bin_y, P_H + 0.02),
                     M["steel_gal"], verts=20))

    # station name sign on twin posts
    sx, sy = -5.05, 0.75
    for dx in (-0.55, 0.55):
        p = cyl("SignPost_%d" % int(dx * 10), 0.042, 2.30,
                (sx + dx, sy, P_H + 1.15), M["steel_gal"], verts=14)
        smooth(p)
        parts.append(p)
    board = box("SignBoard", (1.55, 0.05, 0.42), (sx, sy, P_H + 1.92),
                M["sign_blue"])
    bevel_mod(board, 0.010, 2)
    parts.append(board)
    parts.append(box("SignInner", (1.44, 0.02, 0.31), (sx, sy - 0.032,
                                                       P_H + 1.92),
                     M["sign_white"]))
    for i in range(7):
        parts.append(box("SignGlyph_%d" % i, (0.10, 0.012, 0.16),
                         (sx - 0.60 + i * 0.20, sy - 0.048, P_H + 1.92),
                         M["sign_blue"]))

    # timetable case against the windbreak
    case = box("TimetableCase", (0.60, 0.06, 0.80), (0.0, 1.50, P_H + 1.20),
               M["steel"])
    bevel_mod(case, 0.008, 2)
    parts.append(case)
    parts.append(box("TimetablePaper", (0.52, 0.02, 0.70),
                     (0.0, 1.462, P_H + 1.20), M["sign_white"]))

    # help point post at the platform end
    hp = cyl("HelpPost", 0.055, 1.60, (4.85, 0.60, P_H + 0.80), M["steel"],
             verts=16)
    smooth(hp)
    parts.append(hp)
    parts.append(box("HelpBox", (0.22, 0.16, 0.34), (4.85, 0.50, P_H + 1.62),
                     M["sign_blue"]))
    parts.append(box("HelpPanel", (0.16, 0.02, 0.22), (4.85, 0.415, P_H + 1.64),
                     M["sign_white"]))

    # edge fence behind the platform
    for i in range(13):
        x = -6.0 + i * 1.0
        parts.append(cyl("FencePost_%02d" % i, 0.035, 1.10,
                         (x, BACK_Y - 0.10, P_H + 0.55), M["steel_gal"],
                         verts=10))
    for z in (P_H + 0.45, P_H + 1.00):
        parts.append(box("FenceRail_%d" % int(z * 100), (12.0, 0.04, 0.06),
                         (0.0, BACK_Y - 0.10, z), M["steel_gal"]))
    return parts


# --------------------------------------------------------------------------
# lighting / camera
# --------------------------------------------------------------------------
def build_lighting():
    sun_data = bpy.data.lights.new("Sun", 'SUN')
    sun_data.energy = 3.4
    sun_data.angle = math.radians(1.8)
    sun_data.color = (1.0, 0.96, 0.89)
    sun = bpy.data.objects.new("Sun", sun_data)
    sun.location = (-8.0, -10.0, 12.0)
    bpy.context.collection.objects.link(sun)
    look_at(sun, (0.0, 0.4, 1.4))

    fill_data = bpy.data.lights.new("SkyFill", 'AREA')
    fill_data.energy = 700.0
    fill_data.size = 12.0
    fill_data.color = (0.72, 0.82, 1.0)
    fill = bpy.data.objects.new("SkyFill", fill_data)
    fill.location = (6.0, -10.0, 8.0)
    bpy.context.collection.objects.link(fill)
    look_at(fill, (0.0, 0.0, 1.5))


def build_camera():
    cam_data = bpy.data.cameras.new("Camera")
    cam_data.lens = 35.0
    cam = bpy.data.objects.new("Camera", cam_data)
    cam.location = (9.6, -9.8, 4.70)
    bpy.context.collection.objects.link(cam)
    look_at(cam, (-0.60, 0.30, 1.70))
    bpy.context.scene.camera = cam
    return cam


def main():
    reset_scene()
    make_world((0.34, 0.49, 0.70), 1.25)
    M = build_materials()

    objs = []
    objs += build_track(M)
    objs += build_platform(M)
    objs += build_canopy(M)
    objs += build_windbreak(M)
    objs += build_furniture(M)

    build_lighting()
    build_camera()

    print("claude-100: station platform built with %d objects" % len(objs))


if __name__ == "__main__":
    main()
