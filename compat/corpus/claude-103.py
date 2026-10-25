"""claude-103 - Wristwatch macro composition.

A lathed watch case with dial, applied markers, hands, domed sapphire crystal, crown,
lugs and a segmented leather strap, resting on a tilted display block.  Shot with a
100mm macro at f/2.8 for a very shallow depth of field focused on the dial.
Scene construction only.
"""

import bpy
import bmesh
import math
from mathutils import Vector, Euler


# --------------------------------------------------------------------------- #
# helpers
# --------------------------------------------------------------------------- #
def clean_scene():
    bpy.ops.wm.read_factory_settings(use_empty=True)
    scene = bpy.context.scene
    if scene.world is None:
        scene.world = bpy.data.worlds.new("World")
    return scene


def to_object(name, bm, smooth=True):
    me = bpy.data.meshes.new(name)
    bm.to_mesh(me)
    bm.free()
    if smooth:
        for poly in me.polygons:
            poly.use_smooth = True
    ob = bpy.data.objects.new(name, me)
    bpy.context.scene.collection.objects.link(ob)
    return ob


def lathe(name, profile, segments=96, smooth=True):
    bm = bmesh.new()
    verts = [bm.verts.new((p[0], 0.0, p[1])) for p in profile]
    edges = [bm.edges.new((verts[i], verts[i + 1])) for i in range(len(verts) - 1)]
    bmesh.ops.spin(bm, geom=verts + edges, cent=(0, 0, 0), axis=(0, 0, 1),
                   dvec=(0, 0, 0), angle=2.0 * math.pi, steps=segments,
                   use_merge=False)
    bmesh.ops.remove_doubles(bm, verts=bm.verts, dist=1e-6)
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    return to_object(name, bm, smooth)


def box(name, size, location=(0, 0, 0), rotation=(0, 0, 0), bevel=0.0, segments=2,
        smooth=False):
    bm = bmesh.new()
    bmesh.ops.create_cube(bm, size=1.0)
    bmesh.ops.scale(bm, vec=Vector(size), verts=bm.verts)
    if bevel > 0.0:
        bmesh.ops.bevel(bm, geom=list(bm.verts) + list(bm.edges) + list(bm.faces),
                        offset=bevel, segments=segments, profile=0.5,
                        affect='EDGES', clamp_overlap=True)
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    ob = to_object(name, bm, smooth)
    ob.location = location
    ob.rotation_euler = rotation
    return ob


def cylinder(name, radius, depth, location=(0, 0, 0), rotation=(0, 0, 0),
             segments=32, radius_top=None):
    bm = bmesh.new()
    bmesh.ops.create_cone(bm, cap_ends=True, cap_tris=False, segments=segments,
                          radius1=radius,
                          radius2=radius if radius_top is None else radius_top,
                          depth=depth)
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    ob = to_object(name, bm, smooth=True)
    ob.location = location
    ob.rotation_euler = rotation
    return ob


def pbr(name, base, metallic=0.0, roughness=0.4, extra=None):
    mat = bpy.data.materials.new(name)
    mat.use_nodes = True
    bsdf = mat.node_tree.nodes["Principled BSDF"]
    bsdf.inputs["Base Color"].default_value = base
    bsdf.inputs["Metallic"].default_value = metallic
    bsdf.inputs["Roughness"].default_value = roughness
    for key, value in (extra or {}).items():
        if key in bsdf.inputs:
            bsdf.inputs[key].default_value = value
    return mat


def assign(ob, mat):
    ob.data.materials.clear()
    ob.data.materials.append(mat)


# --------------------------------------------------------------------------- #
# the watch (built flat, dial facing +Z, then parented to a tilt pivot)
# --------------------------------------------------------------------------- #
def build_watch(mats):
    steel, dial_mat, gold, sapphire, hand_mat, second_mat, leather = mats
    parts = []

    case_profile = [
        (0.0000, -0.0040), (0.0090, -0.0048), (0.0150, -0.0030), (0.0182, 0.0000),
        (0.0190, 0.0022), (0.0188, 0.0048), (0.0176, 0.0070), (0.0162, 0.0080),
        (0.0150, 0.0082), (0.0148, 0.0062), (0.0146, 0.0022), (0.0000, 0.0018),
    ]
    case = lathe("Watch_Case", case_profile, segments=96)
    assign(case, steel)
    parts.append(case)

    dial = cylinder("Watch_Dial", 0.0145, 0.0012, (0.0, 0.0, 0.0024), segments=96)
    assign(dial, dial_mat)
    parts.append(dial)

    # applied hour markers, longer batons at the quarters
    for i in range(12):
        ang = math.radians(i * 30.0)
        long_marker = (i % 3 == 0)
        length = 0.0030 if long_marker else 0.0018
        radius = 0.0120 if long_marker else 0.0126
        marker = box("Marker_%02d" % i,
                     (0.0009, length, 0.0006),
                     location=(math.sin(ang) * radius, math.cos(ang) * radius, 0.0034),
                     rotation=(0.0, 0.0, -ang),
                     bevel=0.00015)
        assign(marker, gold)
        marker.name = "Watch_Marker_%02d" % i
        parts.append(marker)

    # date window at 3 o'clock
    date = box("Watch_DateWindow", (0.0038, 0.0028, 0.0006),
               location=(0.0098, 0.0, 0.0033), bevel=0.0002)
    assign(date, pbr("Date Disc", (0.86, 0.86, 0.84, 1.0), 0.0, 0.4))
    parts.append(date)

    hour = box("Watch_HourHand", (0.0012, 0.0080, 0.0005),
               location=(0.0, 0.0028, 0.0040), rotation=(0.0, 0.0, math.radians(-52.0)),
               bevel=0.00012)
    assign(hour, gold)
    parts.append(hour)

    minute = box("Watch_MinuteHand", (0.0009, 0.0118, 0.0005),
                 location=(0.0, 0.0045, 0.0046),
                 rotation=(0.0, 0.0, math.radians(160.0)), bevel=0.0001)
    assign(minute, gold)
    parts.append(minute)

    second = box("Watch_SecondHand", (0.0004, 0.0135, 0.0003),
                 location=(0.0, 0.0040, 0.0051),
                 rotation=(0.0, 0.0, math.radians(28.0)))
    assign(second, second_mat)
    parts.append(second)

    cap = cylinder("Watch_HandCap", 0.0013, 0.0016, (0.0, 0.0, 0.0050), segments=24)
    assign(cap, gold)
    parts.append(cap)

    crystal_profile = [
        (0.0000, 0.0079), (0.0060, 0.0077), (0.0105, 0.0071), (0.0135, 0.0063),
        (0.0148, 0.0056), (0.0148, 0.0052), (0.0110, 0.0056), (0.0000, 0.0060),
    ]
    crystal = lathe("Watch_Crystal", crystal_profile, segments=96)
    assign(crystal, sapphire)
    parts.append(crystal)

    # fluted crown at 3 o'clock
    crown = cylinder("Watch_Crown", 0.0032, 0.0032,
                     (0.0203, 0.0, 0.0022), rotation=(0.0, math.radians(90.0), 0.0),
                     segments=20)
    assign(crown, steel)
    parts.append(crown)
    for i in range(14):
        ang = math.radians(i * (360.0 / 14.0))
        flute = box("Watch_CrownFlute_%02d" % i, (0.0030, 0.0004, 0.0004),
                    location=(0.0203,
                              math.sin(ang) * 0.0031,
                              0.0022 + math.cos(ang) * 0.0031),
                    rotation=(-ang, 0.0, 0.0))
        assign(flute, steel)
        parts.append(flute)

    # lugs
    for sy in (1.0, -1.0):
        for sx in (1.0, -1.0):
            lug = box("Watch_Lug_%d_%d" % (sx, sy), (0.0032, 0.0080, 0.0035),
                      location=(sx * 0.0110, sy * 0.0180, 0.0),
                      rotation=(sy * math.radians(-14.0), 0.0,
                                sx * sy * math.radians(-6.0)),
                      bevel=0.0008, segments=3, smooth=True)
            assign(lug, steel)
            parts.append(lug)

    # segmented leather strap curving away on both sides
    for sy in (1.0, -1.0):
        y = sy * 0.0225
        z = -0.0015
        drop = 0.0
        for i in range(9):
            width = 0.0100 - i * 0.00035
            seg = box("Watch_Strap_%s_%02d" % ("A" if sy > 0 else "B", i),
                      (width, 0.0055, 0.0011),
                      location=(0.0, y, z),
                      rotation=(sy * math.radians(-18.0 - i * 4.0), 0.0, 0.0),
                      bevel=0.0004, segments=3, smooth=True)
            assign(seg, leather)
            parts.append(seg)
            drop += 0.0022 + i * 0.00035
            y += sy * 0.0100
            z = -0.0015 - drop

    root = bpy.data.objects.new("Wristwatch", None)
    root.empty_display_type = 'PLAIN_AXES'
    root.empty_display_size = 0.02
    bpy.context.scene.collection.objects.link(root)
    for part in parts:
        part.parent = root
    return root


# --------------------------------------------------------------------------- #
# main
# --------------------------------------------------------------------------- #
def main():
    scene = clean_scene()
    scene.render.engine = 'CYCLES'
    try:
        scene.cycles.samples = 320
        scene.cycles.use_denoising = True
    except AttributeError:
        pass
    scene.render.resolution_x = 2000
    scene.render.resolution_y = 1333
    scene.view_settings.view_transform = 'AgX'

    scene.world.use_nodes = True
    scene.world.node_tree.nodes["Background"].inputs["Color"].default_value = (
        0.015, 0.016, 0.020, 1.0)

    steel = pbr("Polished Steel", (0.70, 0.71, 0.72, 1.0), 1.0, 0.12)
    dial_mat = pbr("Dial Blue", (0.012, 0.035, 0.110, 1.0), 0.15, 0.20,
                   {"Coat Weight": 1.0, "Coat Roughness": 0.05})
    gold = pbr("Applied Gold", (0.92, 0.74, 0.36, 1.0), 1.0, 0.13)
    sapphire = pbr("Sapphire Crystal", (1.0, 1.0, 1.0, 1.0), 0.0, 0.005,
                   {"Transmission Weight": 1.0, "IOR": 1.77})
    hand_mat = pbr("Hand Steel", (0.85, 0.86, 0.88, 1.0), 1.0, 0.08)
    second_mat = pbr("Second Hand", (0.62, 0.05, 0.03, 1.0), 0.0, 0.28)
    leather = pbr("Strap Leather", (0.075, 0.032, 0.018, 1.0), 0.0, 0.55,
                  {"Sheen Weight": 0.25})
    block_mat = pbr("Display Block", (0.055, 0.056, 0.060, 1.0), 0.0, 0.22,
                    {"Coat Weight": 0.6, "Coat Roughness": 0.12})
    table_mat = pbr("Table Slate", (0.030, 0.031, 0.034, 1.0), 0.0, 0.38)
    backdrop_mat = pbr("Backdrop", (0.10, 0.11, 0.14, 1.0), 0.0, 0.6)

    # ---- set ------------------------------------------------------------- #
    bm = bmesh.new()
    bmesh.ops.create_grid(bm, x_segments=1, y_segments=1, size=2.0)
    table = to_object("Table_Surface", bm, smooth=False)
    assign(table, table_mat)

    backdrop = box("Backdrop", (2.0, 0.01, 1.2), location=(0.0, 0.55, 0.60))
    assign(backdrop, backdrop_mat)

    # ---- tilted display block + watch ------------------------------------ #
    pivot = bpy.data.objects.new("Display_Pivot", None)
    pivot.empty_display_type = 'ARROWS'
    pivot.empty_display_size = 0.04
    scene.collection.objects.link(pivot)
    pivot.location = (0.0, 0.0, 0.030)
    pivot.rotation_euler = Euler((math.radians(-16.0), 0.0, math.radians(24.0)), 'XYZ')

    block = box("Display_Block", (0.115, 0.085, 0.030), location=(0.0, 0.0, -0.015),
                bevel=0.006, segments=4, smooth=True)
    assign(block, block_mat)
    block.parent = pivot

    watch = build_watch((steel, dial_mat, gold, sapphire, hand_mat, second_mat,
                         leather))
    watch.parent = pivot
    watch.location = (0.0, 0.0, 0.0045)
    watch.rotation_euler = (0.0, 0.0, math.radians(-10.0))

    focus_empty = bpy.data.objects.new("Focus_Dial", None)
    focus_empty.empty_display_type = 'SPHERE'
    focus_empty.empty_display_size = 0.006
    scene.collection.objects.link(focus_empty)
    focus_empty.parent = pivot
    focus_empty.location = (0.0, 0.0, 0.0095)

    # ---- lighting: large soft top, long strip for the case, cool accent --- #
    def area(name, loc, target, size, size_y, energy, color=(1, 1, 1),
             shape='RECTANGLE'):
        data = bpy.data.lights.new(name, type='AREA')
        data.shape = shape
        data.size = size
        data.size_y = size_y
        data.energy = energy
        data.color = color
        ob = bpy.data.objects.new(name, data)
        scene.collection.objects.link(ob)
        ob.location = loc
        ob.rotation_euler = (Vector(target) - Vector(loc)).to_track_quat(
            '-Z', 'Y').to_euler()
        return ob

    focus_point = (0.0, 0.0, 0.042)
    area("Key_Diffusion", (-0.28, -0.22, 0.55), focus_point, 0.60, 0.60, 90.0)
    area("Strip_Reflector", (0.30, -0.05, 0.32), focus_point, 0.03, 0.55, 45.0,
         color=(1.0, 0.97, 0.92))
    area("Cool_Accent", (0.22, 0.34, 0.24), focus_point, 0.12, 0.12, 22.0,
         color=(0.70, 0.82, 1.0))
    area("Dial_Kicker", (-0.10, -0.30, 0.10), focus_point, 0.08, 0.08, 8.0)

    # ---- macro camera ------------------------------------------------------ #
    cam_data = bpy.data.cameras.new("MacroCam")
    cam_data.lens = 100.0
    cam_data.clip_start = 0.005
    cam_data.clip_end = 20.0
    cam_data.dof.use_dof = True
    cam_data.dof.focus_object = focus_empty
    cam_data.dof.aperture_fstop = 2.8
    cam_data.dof.aperture_blades = 9
    cam = bpy.data.objects.new("MacroCam", cam_data)
    scene.collection.objects.link(cam)
    cam.location = (0.085, -0.185, 0.125)
    track = cam.constraints.new('TRACK_TO')
    track.target = focus_empty
    track.track_axis = 'TRACK_NEGATIVE_Z'
    track.up_axis = 'UP_Y'
    scene.camera = cam


if __name__ == "__main__":
    main()
