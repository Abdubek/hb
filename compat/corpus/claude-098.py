"""claude-098 - A washbasin with faucet, drain and pedestal.

The basin bowl is cut with bmesh (inset + extrude + bevel), the pedestal is a
lathed profile spun about Z, and the spout is a bevelled bezier curve converted
to mesh.  Includes tap handles, a drain grate, tail pipe, a wall with mirror,
lighting and a camera.
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


def make_world(color=(0.05, 0.052, 0.058), strength=1.0):
    world = bpy.data.worlds.new("World")
    world.use_nodes = True
    bg = world.node_tree.nodes["Background"]
    bg.inputs[0].default_value = (*color, 1.0)
    bg.inputs[1].default_value = strength
    bpy.context.scene.world = world
    return world


def mat_pbr(name, color, metallic=0.0, roughness=0.5, alpha=1.0):
    mat = bpy.data.materials.new(name)
    mat.use_nodes = True
    bsdf = mat.node_tree.nodes["Principled BSDF"]
    bsdf.inputs["Base Color"].default_value = (*color, 1.0)
    bsdf.inputs["Metallic"].default_value = metallic
    bsdf.inputs["Roughness"].default_value = roughness
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


def link_mesh(name, bm, mat=None):
    me = bpy.data.meshes.new(name)
    bm.normal_update()
    bm.to_mesh(me)
    bm.free()
    ob = bpy.data.objects.new(name, me)
    bpy.context.collection.objects.link(ob)
    return assign(ob, mat)


def box(name, size, loc, mat=None, rot=(0.0, 0.0, 0.0)):
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=loc, rotation=rot)
    ob = bpy.context.object
    ob.name = name
    ob.scale = size
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    return assign(ob, mat)


def cyl(name, radius, depth, loc, mat=None, rot=(0.0, 0.0, 0.0), verts=32):
    bpy.ops.mesh.primitive_cylinder_add(radius=radius, depth=depth,
                                        vertices=verts, location=loc,
                                        rotation=rot)
    ob = bpy.context.object
    ob.name = name
    return assign(ob, mat)


def torus(name, major, minor, loc, mat=None, rot=(0.0, 0.0, 0.0),
          maj_seg=36, min_seg=12):
    bpy.ops.mesh.primitive_torus_add(major_radius=major, minor_radius=minor,
                                     major_segments=maj_seg,
                                     minor_segments=min_seg,
                                     location=loc, rotation=rot)
    ob = bpy.context.object
    ob.name = name
    return assign(ob, mat)


def bevel_mod(obj, width=0.005, segments=3, angle=40.0):
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
# materials
# --------------------------------------------------------------------------
def build_materials():
    return {
        "porcelain": mat_pbr("Porcelain", (0.945, 0.95, 0.95), 0.0, 0.12),
        "porcelain2": mat_pbr("PorcelainShade", (0.90, 0.905, 0.91), 0.0, 0.16),
        "chrome": mat_pbr("Chrome", (0.90, 0.91, 0.93), 1.0, 0.06),
        "chrome_soft": mat_pbr("ChromeSoft", (0.80, 0.81, 0.83), 1.0, 0.18),
        "dark": mat_pbr("DrainDark", (0.03, 0.03, 0.035), 0.0, 0.35),
        "tile": mat_pbr("WallTile", (0.80, 0.83, 0.83), 0.0, 0.20),
        "grout": mat_pbr("Grout", (0.62, 0.63, 0.62), 0.0, 0.70),
        "floor": mat_pbr("FloorStone", (0.30, 0.29, 0.28), 0.0, 0.42),
        "mirror": mat_pbr("Mirror", (0.92, 0.93, 0.94), 1.0, 0.02),
        "soap": mat_pbr("Soap", (0.85, 0.74, 0.52), 0.0, 0.35),
    }


# --------------------------------------------------------------------------
# basin: box -> inset -> extrude down -> bevel
# --------------------------------------------------------------------------
BASIN_TOP = 0.855
BASIN_H = 0.185
BASIN_W = 0.585
BASIN_D = 0.455
BOWL_DEPTH = 0.145


def build_basin(M):
    bm = bmesh.new()
    bmesh.ops.create_cube(bm, size=1.0)
    for v in bm.verts:
        v.co.x *= BASIN_W
        v.co.y *= BASIN_D
        v.co.z *= BASIN_H
    # slight taper: narrow the underside for a softer profile
    for v in bm.verts:
        if v.co.z < 0.0:
            v.co.x *= 0.80
            v.co.y *= 0.82

    bm.faces.ensure_lookup_table()
    top = max(bm.faces, key=lambda f: f.calc_center_median().z)

    bmesh.ops.inset_region(bm, faces=[top], thickness=0.055, depth=0.0,
                           use_even_offset=True)
    res = bmesh.ops.extrude_face_region(bm, geom=[top])
    new_verts = [e for e in res["geom"] if isinstance(e, bmesh.types.BMVert)]
    bmesh.ops.translate(bm, verts=new_verts, vec=(0.0, 0.0, -BOWL_DEPTH))
    bmesh.ops.delete(bm, geom=[top], context='FACES')

    # narrow the bowl floor so the walls slope inwards to the drain
    for v in new_verts:
        v.co.x *= 0.72
        v.co.y *= 0.70

    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    bmesh.ops.bevel(bm, geom=list(bm.verts) + list(bm.edges), offset=0.020,
                    segments=4, profile=0.5, affect='EDGES',
                    clamp_overlap=True, loop_slide=True)
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)

    basin = link_mesh("Basin", bm, M["porcelain"])
    basin.location = (0.0, 0.0, BASIN_TOP - BASIN_H / 2.0)
    smooth(basin, 45.0)

    parts = [basin]

    # raised rear deck carrying the tap set
    deck = box("BasinDeck", (BASIN_W * 0.98, 0.115, 0.095),
               (0.0, BASIN_D / 2.0 + 0.030, BASIN_TOP + 0.020),
               M["porcelain"])
    bevel_mod(deck, 0.016, 4)
    smooth(deck, 45.0)
    parts.append(deck)

    # small splash lip along the back of the deck
    lip = box("SplashLip", (BASIN_W * 0.98, 0.030, 0.045),
              (0.0, BASIN_D / 2.0 + 0.075, BASIN_TOP + 0.088), M["porcelain"])
    bevel_mod(lip, 0.010, 3)
    smooth(lip, 45.0)
    parts.append(lip)
    return parts


# --------------------------------------------------------------------------
# pedestal: lathed profile
# --------------------------------------------------------------------------
def build_pedestal(M):
    profile = [
        (0.000, 0.000), (0.150, 0.000), (0.168, 0.018), (0.168, 0.055),
        (0.140, 0.100), (0.112, 0.170), (0.098, 0.280), (0.096, 0.400),
        (0.104, 0.510), (0.122, 0.600), (0.145, 0.665), (0.158, 0.700),
        (0.160, 0.726), (0.120, 0.740), (0.000, 0.745),
    ]
    bm = bmesh.new()
    verts = [bm.verts.new((p[0], 0.0, p[1])) for p in profile]
    edges = [bm.edges.new((verts[i], verts[i + 1]))
             for i in range(len(verts) - 1)]
    bmesh.ops.spin(bm, geom=verts + edges, cent=(0.0, 0.0, 0.0),
                   axis=(0.0, 0.0, 1.0), dvec=(0.0, 0.0, 0.0),
                   angle=2.0 * math.pi, steps=48, use_merge=False)
    bmesh.ops.remove_doubles(bm, verts=bm.verts, dist=1e-5)
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    ped = link_mesh("Pedestal", bm, M["porcelain"])
    ped.location = (0.0, 0.045, 0.0)
    smooth(ped, 50.0)

    # the pedestal top disappears under the basin underside
    parts = [ped]
    parts.append(cyl("PedestalCollar", 0.150, 0.030, (0.0, 0.045, 0.745),
                     M["porcelain2"], verts=40))
    smooth(parts[-1])
    return parts


# --------------------------------------------------------------------------
# tap set
# --------------------------------------------------------------------------
DECK_Y = BASIN_D / 2.0 + 0.030
DECK_Z = BASIN_TOP + 0.068


def build_spout(M):
    curve = bpy.data.curves.new("SpoutCurve", 'CURVE')
    curve.dimensions = '3D'
    curve.bevel_depth = 0.017
    curve.bevel_resolution = 6
    curve.resolution_u = 14
    curve.use_fill_caps = True

    pts = [
        (0.0, DECK_Y, DECK_Z - 0.010),
        (0.0, DECK_Y, DECK_Z + 0.120),
        (0.0, DECK_Y - 0.030, DECK_Z + 0.185),
        (0.0, DECK_Y - 0.120, DECK_Z + 0.190),
        (0.0, DECK_Y - 0.165, DECK_Z + 0.150),
    ]
    spline = curve.splines.new('BEZIER')
    spline.bezier_points.add(len(pts) - 1)
    for bp, p in zip(spline.bezier_points, pts):
        bp.co = p
        bp.handle_left_type = 'AUTO'
        bp.handle_right_type = 'AUTO'

    ob = bpy.data.objects.new("Spout", curve)
    bpy.context.collection.objects.link(ob)
    assign(ob, M["chrome"])

    for o in bpy.context.selected_objects:
        o.select_set(False)
    ob.select_set(True)
    bpy.context.view_layer.objects.active = ob
    bpy.ops.object.convert(target='MESH')
    ob = bpy.context.object
    smooth(ob, 50.0)

    parts = [ob]
    # base escutcheon and aerator
    esc = cyl("SpoutBase", 0.032, 0.028, (0.0, DECK_Y, DECK_Z - 0.014),
              M["chrome"], verts=32)
    smooth(esc)
    parts.append(esc)
    aer = cyl("Aerator", 0.020, 0.020,
              (0.0, DECK_Y - 0.175, DECK_Z + 0.140), M["chrome_soft"],
              rot=(math.radians(35.0), 0.0, 0.0), verts=24)
    smooth(aer)
    parts.append(aer)
    return parts


def build_taps(M):
    parts = []
    for sx, tag in ((-1, "Cold"), (1, "Hot")):
        x = sx * 0.175
        base = cyl("TapBase_%s" % tag, 0.030, 0.024, (x, DECK_Y, DECK_Z - 0.012),
                   M["chrome"], verts=28)
        smooth(base)
        parts.append(base)
        stem = cyl("TapStem_%s" % tag, 0.014, 0.065, (x, DECK_Y, DECK_Z + 0.030),
                   M["chrome"], verts=20)
        smooth(stem)
        parts.append(stem)
        hub = cyl("TapHub_%s" % tag, 0.020, 0.018, (x, DECK_Y, DECK_Z + 0.068),
                  M["chrome"], verts=24)
        smooth(hub)
        parts.append(hub)
        # cross head lever
        for a in (0.0, math.pi / 2.0):
            arm = box("TapArm_%s_%d" % (tag, int(a * 10)),
                      (0.098, 0.014, 0.014), (x, DECK_Y, DECK_Z + 0.072),
                      M["chrome"], rot=(0.0, 0.0, a))
            bevel_mod(arm, 0.004, 3)
            smooth(arm)
            parts.append(arm)
        cap = cyl("TapCap_%s" % tag, 0.011, 0.008, (x, DECK_Y, DECK_Z + 0.083),
                  M["dark"], verts=16)
        parts.append(cap)
    return parts


# --------------------------------------------------------------------------
# drain and waste pipe
# --------------------------------------------------------------------------
def build_drain(M):
    bowl_floor = BASIN_TOP - BOWL_DEPTH + 0.010
    parts = []
    flange = cyl("DrainFlange", 0.033, 0.008, (0.0, 0.0, bowl_floor + 0.002),
                 M["chrome"], verts=32)
    smooth(flange)
    parts.append(flange)
    parts.append(cyl("DrainHole", 0.026, 0.010, (0.0, 0.0, bowl_floor - 0.004),
                     M["dark"], verts=32))
    ring = torus("DrainRing", 0.028, 0.004, (0.0, 0.0, bowl_floor + 0.004),
                 M["chrome"], maj_seg=32, min_seg=8)
    smooth(ring)
    parts.append(ring)
    for i in range(3):
        bar = box("DrainBar_%d" % i, (0.056, 0.006, 0.005),
                  (0.0, 0.0, bowl_floor + 0.004), M["chrome"],
                  rot=(0.0, 0.0, math.pi * i / 3.0))
        parts.append(bar)
    parts.append(cyl("DrainBoss", 0.008, 0.008, (0.0, 0.0, bowl_floor + 0.006),
                     M["chrome"], verts=12))

    # overflow slot on the front inner wall of the bowl
    parts.append(box("Overflow", (0.062, 0.012, 0.012),
                     (0.0, -BASIN_D / 2.0 + 0.070, BASIN_TOP - 0.045),
                     M["dark"]))

    # tail pipe dropping behind the pedestal into the wall
    tail = cyl("TailPipe", 0.020, 0.16, (0.0, 0.0, bowl_floor - 0.085),
               M["chrome_soft"], verts=20)
    smooth(tail)
    parts.append(tail)
    nut = cyl("TailNut", 0.026, 0.020, (0.0, 0.0, bowl_floor - 0.020),
              M["chrome_soft"], verts=20)
    smooth(nut)
    parts.append(nut)
    return parts


# --------------------------------------------------------------------------
# room
# --------------------------------------------------------------------------
def build_room(M):
    parts = []
    bpy.ops.mesh.primitive_plane_add(size=8.0, location=(0.0, 0.0, 0.0))
    floor = bpy.context.object
    floor.name = "Floor"
    assign(floor, M["floor"])
    parts.append(floor)

    wall_y = BASIN_D / 2.0 + 0.095
    parts.append(box("Wall", (5.0, 0.10, 2.8), (0.0, wall_y + 0.05, 1.4),
                     M["grout"]))

    # tile courses on the wall face
    tw, th, gap = 0.30, 0.20, 0.006
    for row in range(9):
        z = 0.10 + row * (th + gap)
        offset = (tw + gap) / 2.0 if row % 2 else 0.0
        for col in range(-4, 5):
            x = col * (tw + gap) + offset
            parts.append(box("Tile_%d_%d" % (row, col), (tw, 0.012, th),
                             (x, wall_y - 0.004, z + th / 2.0), M["tile"]))

    # mirror above the basin
    frame = box("MirrorFrame", (0.56, 0.030, 0.72), (0.0, wall_y - 0.006, 1.50),
                M["chrome_soft"])
    bevel_mod(frame, 0.006, 3)
    smooth(frame)
    parts.append(frame)
    parts.append(box("MirrorGlass", (0.52, 0.012, 0.68),
                     (0.0, wall_y - 0.024, 1.50), M["mirror"]))

    # soap bar on the deck corner
    soap = box("Soap", (0.085, 0.055, 0.028), (0.235, DECK_Y - 0.010,
                                               BASIN_TOP + 0.082), M["soap"])
    bevel_mod(soap, 0.012, 4)
    smooth(soap)
    parts.append(soap)
    return parts


def build_lighting():
    key_data = bpy.data.lights.new("Key", 'AREA')
    key_data.energy = 260.0
    key_data.size = 1.6
    key = bpy.data.objects.new("KeyLight", key_data)
    key.location = (-1.4, -1.5, 2.35)
    bpy.context.collection.objects.link(key)
    look_at(key, (0.0, 0.0, 0.85))

    fill_data = bpy.data.lights.new("Fill", 'AREA')
    fill_data.energy = 90.0
    fill_data.size = 1.6
    fill = bpy.data.objects.new("FillLight", fill_data)
    fill.location = (1.6, -1.5, 1.30)
    bpy.context.collection.objects.link(fill)
    look_at(fill, (0.05, 0.0, 0.80))

    van_data = bpy.data.lights.new("Vanity", 'AREA')
    van_data.energy = 70.0
    van_data.shape = 'RECTANGLE'
    van_data.size = 0.6
    van_data.size_y = 0.08
    van = bpy.data.objects.new("VanityLight", van_data)
    van.location = (0.0, 0.15, 2.05)
    bpy.context.collection.objects.link(van)
    look_at(van, (0.0, 0.20, 0.90))


def build_camera():
    cam_data = bpy.data.cameras.new("Camera")
    cam_data.lens = 50.0
    cam = bpy.data.objects.new("Camera", cam_data)
    cam.location = (0.95, -1.35, 1.35)
    bpy.context.collection.objects.link(cam)
    look_at(cam, (0.0, 0.02, 0.78))
    bpy.context.scene.camera = cam
    return cam


def main():
    reset_scene()
    make_world((0.055, 0.058, 0.062), 1.0)
    M = build_materials()

    objs = []
    objs += build_room(M)
    objs += build_pedestal(M)
    objs += build_basin(M)
    objs += build_spout(M)
    objs += build_taps(M)
    objs += build_drain(M)

    build_lighting()
    build_camera()

    print("claude-098: washbasin built with %d objects" % len(objs))


if __name__ == "__main__":
    main()
