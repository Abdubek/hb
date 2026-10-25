"""claude-019 - A pair of over-ear headphones resting on a stand.

Builds the scene only: no rendering, no file output, no external assets.
"""

import bpy
import bmesh
import math
from mathutils import Vector


# ----------------------------------------------------------------------------
# generic helpers
# ----------------------------------------------------------------------------

def reset_scene():
    bpy.ops.wm.read_factory_settings(use_empty=True)
    bpy.context.scene.unit_settings.system = 'METRIC'


def new_material(name, base=(0.8, 0.8, 0.8), metallic=0.0, rough=0.5,
                 transmission=0.0, alpha=1.0, ior=1.45,
                 emission=None, emit_strength=0.0, coat=0.0):
    mat = bpy.data.materials.new(name)
    mat.use_nodes = True
    bsdf = mat.node_tree.nodes.get("Principled BSDF")

    def put(key, value):
        if bsdf and key in bsdf.inputs:
            bsdf.inputs[key].default_value = value

    put("Base Color", (base[0], base[1], base[2], 1.0))
    put("Metallic", metallic)
    put("Roughness", rough)
    put("IOR", ior)
    put("Transmission Weight", transmission)
    put("Alpha", alpha)
    put("Coat Weight", coat)
    if emission is not None:
        put("Emission Color", (emission[0], emission[1], emission[2], 1.0))
        put("Emission Strength", emit_strength)
    if alpha < 1.0 or transmission > 0.0:
        try:
            mat.blend_method = 'BLEND'
        except Exception:
            pass
    return mat


def shade_auto(ob, angle=math.radians(35.0)):
    me = ob.data
    for poly in me.polygons:
        poly.use_smooth = True
    bm = bmesh.new()
    bm.from_mesh(me)
    for edge in bm.edges:
        if len(edge.link_faces) == 2:
            edge.smooth = edge.calc_face_angle() < angle
        else:
            edge.smooth = False
    bm.to_mesh(me)
    bm.free()


def _finish(bm, name, loc, rot, mat, smooth, smooth_angle):
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    me = bpy.data.meshes.new(name)
    bm.to_mesh(me)
    bm.free()
    ob = bpy.data.objects.new(name, me)
    ob.location = loc
    ob.rotation_euler = rot
    bpy.context.collection.objects.link(ob)
    if mat is not None:
        me.materials.append(mat)
    if smooth:
        shade_auto(ob, smooth_angle)
    return ob


def add_box(name, size, loc=(0, 0, 0), rot=(0, 0, 0), mat=None,
            bevel=0.0, seg=3, smooth=True):
    bm = bmesh.new()
    bmesh.ops.create_cube(bm, size=1.0)
    bmesh.ops.scale(bm, vec=Vector(size), verts=bm.verts)
    if bevel > 0.0:
        bmesh.ops.bevel(bm, geom=list(bm.verts) + list(bm.edges) + list(bm.faces),
                        offset=bevel, offset_type='OFFSET', segments=seg,
                        profile=0.5, affect='EDGES', clamp_overlap=True)
        return _finish(bm, name, loc, rot, mat, smooth, math.radians(32.0))
    return _finish(bm, name, loc, rot, mat, False, 0.0)


def add_cyl(name, radius, depth, loc=(0, 0, 0), rot=(0, 0, 0), mat=None,
            segments=32, bevel=0.0):
    bm = bmesh.new()
    bmesh.ops.create_cone(bm, cap_ends=True, cap_tris=False, segments=segments,
                          radius1=radius, radius2=radius, depth=depth)
    if bevel > 0.0:
        bmesh.ops.bevel(bm, geom=list(bm.verts) + list(bm.edges) + list(bm.faces),
                        offset=bevel, offset_type='OFFSET', segments=3,
                        profile=0.5, affect='EDGES', clamp_overlap=True)
    return _finish(bm, name, loc, rot, mat, True, math.radians(40.0))


def add_cone(name, r1, r2, depth, loc=(0, 0, 0), rot=(0, 0, 0), mat=None,
             segments=32):
    bm = bmesh.new()
    bmesh.ops.create_cone(bm, cap_ends=True, cap_tris=False, segments=segments,
                          radius1=r1, radius2=r2, depth=depth)
    return _finish(bm, name, loc, rot, mat, True, math.radians(45.0))


def add_sphere(name, radius, loc=(0, 0, 0), mat=None, useg=32, vseg=18,
               scale=(1, 1, 1), rot=(0, 0, 0)):
    bm = bmesh.new()
    bmesh.ops.create_uvsphere(bm, u_segments=useg, v_segments=vseg, radius=radius)
    bmesh.ops.scale(bm, vec=Vector(scale), verts=bm.verts)
    return _finish(bm, name, loc, rot, mat, True, math.radians(60.0))


def add_torus(name, major, minor, loc=(0, 0, 0), rot=(0, 0, 0), mat=None,
              mseg=48, nseg=18):
    bpy.ops.mesh.primitive_torus_add(align='WORLD', location=loc, rotation=rot,
                                     major_radius=major, minor_radius=minor,
                                     major_segments=mseg, minor_segments=nseg)
    ob = bpy.context.active_object
    ob.name = name
    if mat is not None:
        ob.data.materials.append(mat)
    shade_auto(ob, math.radians(70.0))
    return ob


def add_arc_band(name, center, radius, width, thickness, a_start, a_end,
                 steps=48, mat=None):
    """Revolve a rectangular section about the Y axis to make a curved band."""
    bm = bmesh.new()
    verts = []
    for dr, dy in ((-thickness * 0.5, -width * 0.5),
                   (thickness * 0.5, -width * 0.5),
                   (thickness * 0.5, width * 0.5),
                   (-thickness * 0.5, width * 0.5)):
        r = radius + dr
        verts.append(bm.verts.new((math.sin(a_start) * r, dy,
                                   math.cos(a_start) * r)))
    bm.faces.new(verts)
    bm.normal_update()
    bmesh.ops.spin(bm, geom=list(bm.verts) + list(bm.edges) + list(bm.faces),
                   cent=(0.0, 0.0, 0.0), axis=(0.0, 1.0, 0.0),
                   dvec=(0.0, 0.0, 0.0), angle=(a_end - a_start), steps=steps,
                   use_merge=False)
    bmesh.ops.bevel(bm, geom=list(bm.verts) + list(bm.edges) + list(bm.faces),
                    offset=thickness * 0.25, offset_type='OFFSET', segments=2,
                    profile=0.5, affect='EDGES', clamp_overlap=True)
    return _finish(bm, name, center, (0, 0, 0), mat, True, math.radians(38.0))


def add_curve(name, points, depth, mat=None, resolution=14):
    cu = bpy.data.curves.new(name, 'CURVE')
    cu.dimensions = '3D'
    cu.bevel_depth = depth
    cu.bevel_resolution = 4
    cu.resolution_u = resolution
    spline = cu.splines.new('BEZIER')
    spline.bezier_points.add(len(points) - 1)
    for bp, co in zip(spline.bezier_points, points):
        bp.co = co
        bp.handle_left_type = 'AUTO'
        bp.handle_right_type = 'AUTO'
    ob = bpy.data.objects.new(name, cu)
    bpy.context.collection.objects.link(ob)
    if mat is not None:
        cu.materials.append(mat)
    return ob


def aim(ob, target):
    d = Vector(target) - ob.location
    ob.rotation_euler = d.to_track_quat('-Z', 'Y').to_euler()


def add_light(name, ltype, loc, energy, color=(1.0, 1.0, 1.0), size=1.0,
              target=None):
    data = bpy.data.lights.new(name, ltype)
    data.energy = energy
    data.color = color
    if ltype == 'AREA':
        data.size = size
    elif ltype == 'SUN':
        data.angle = math.radians(3.0)
    else:
        data.shadow_soft_size = size
    ob = bpy.data.objects.new(name, data)
    ob.location = loc
    bpy.context.collection.objects.link(ob)
    if target is not None:
        aim(ob, target)
    return ob


def setup_world(color=(0.03, 0.033, 0.038), strength=1.0):
    world = bpy.data.worlds.new("World")
    bpy.context.scene.world = world
    world.use_nodes = True
    bg = world.node_tree.nodes["Background"]
    bg.inputs[0].default_value = (color[0], color[1], color[2], 1.0)
    bg.inputs[1].default_value = strength


def add_camera(loc, target, lens=60.0, name="Camera"):
    data = bpy.data.cameras.new(name)
    data.lens = lens
    ob = bpy.data.objects.new(name, data)
    ob.location = loc
    bpy.context.collection.objects.link(ob)
    aim(ob, target)
    bpy.context.scene.camera = ob
    return ob


# ----------------------------------------------------------------------------
# materials
# ----------------------------------------------------------------------------

reset_scene()
setup_world((0.03, 0.033, 0.038), 1.0)

TABLE = new_material("TableTop", (0.16, 0.12, 0.10), rough=0.42, coat=0.25)
BACKDROP = new_material("Backdrop", (0.10, 0.11, 0.13), rough=0.85)
SHELL = new_material("CupShell", (0.055, 0.058, 0.065), rough=0.30, coat=0.45)
SHELL_PLATE = new_material("CupPlate", (0.62, 0.63, 0.66), metallic=1.0,
                           rough=0.24)
FOAM = new_material("Leatherette", (0.035, 0.035, 0.04), rough=0.62)
HEADBAND = new_material("HeadbandShell", (0.075, 0.078, 0.085), rough=0.34,
                        coat=0.4)
METAL = new_material("Aluminium", (0.70, 0.71, 0.74), metallic=1.0, rough=0.22)
DARKMET = new_material("DarkMetal", (0.12, 0.125, 0.13), metallic=0.95,
                       rough=0.38)
MESH = new_material("DriverMesh", (0.09, 0.09, 0.10), rough=0.7)
CABLE = new_material("Cable", (0.045, 0.045, 0.05), rough=0.55)
ACCENT = new_material("Accent", (0.72, 0.30, 0.06), metallic=0.6, rough=0.3)
LED = new_material("Led", (0.05, 0.1, 0.1), emission=(0.2, 0.85, 0.95),
                   emit_strength=6.0)
WOOD_BASE = new_material("StandBase", (0.20, 0.13, 0.08), rough=0.38, coat=0.35)


# ----------------------------------------------------------------------------
# table and backdrop
# ----------------------------------------------------------------------------

add_box("Table", (1.6, 1.2, 0.04), (0.0, 0.05, -0.02), mat=TABLE, bevel=0.004)
add_box("Backdrop", (2.0, 0.04, 1.2), (0.0, 0.62, 0.58), mat=BACKDROP)


# ----------------------------------------------------------------------------
# stand
# ----------------------------------------------------------------------------

add_cyl("StandBase", 0.086, 0.016, (0.0, 0.0, 0.008), mat=WOOD_BASE,
        segments=64, bevel=0.004)
add_cyl("StandCollar", 0.048, 0.010, (0.0, 0.0, 0.021), mat=METAL,
        segments=48, bevel=0.003)
add_cyl("StandPost", 0.0125, 0.284, (0.0, 0.0, 0.166), mat=METAL, segments=32)
add_cyl("StandPostTaper", 0.016, 0.02, (0.0, 0.0, 0.036), mat=METAL,
        segments=32, bevel=0.004)

# horizontal padded bar the headband rests on
BAR_Z = 0.308
add_cyl("StandBar", 0.012, 0.104, (0.0, 0.0, BAR_Z), rot=(0, math.radians(90), 0),
        mat=METAL, segments=32)
add_cyl("StandBarPad", 0.0145, 0.070, (0.0, 0.0, BAR_Z),
        rot=(0, math.radians(90), 0), mat=FOAM, segments=32, bevel=0.004)
for sx in (-1, 1):
    add_sphere("StandBarCap_%d" % sx, 0.012, (sx * 0.052, 0.0, BAR_Z),
               mat=METAL, useg=24, vseg=14)
add_cyl("StandBarJoint", 0.018, 0.026, (0.0, 0.0, BAR_Z - 0.006), mat=DARKMET,
        segments=32, bevel=0.005)


# ----------------------------------------------------------------------------
# headband
# ----------------------------------------------------------------------------

ARC_C = Vector((0.0, 0.0, 0.222))
R_BAND = 0.105
BAND_T = 0.013
BAND_W = 0.027
A_END = math.radians(78.0)

add_arc_band("HeadbandShell", ARC_C, R_BAND, BAND_W, BAND_T,
             -A_END, A_END, steps=56, mat=HEADBAND)
# metal reinforcing strip on the outside of the band
add_arc_band("HeadbandStrip", ARC_C, R_BAND + BAND_T * 0.5 + 0.0015,
             BAND_W * 0.45, 0.003, -A_END * 0.96, A_END * 0.96, steps=56,
             mat=METAL)
# padded crown on the inside
add_arc_band("HeadbandCushion", ARC_C, R_BAND - BAND_T * 0.5 - 0.006,
             BAND_W * 0.92, 0.014, math.radians(-44.0), math.radians(44.0),
             steps=40, mat=FOAM)


def band_point(angle, radius):
    return Vector((math.sin(angle) * radius, 0.0,
                   ARC_C.z + math.cos(angle) * radius))


# ----------------------------------------------------------------------------
# yokes and ear cups
# ----------------------------------------------------------------------------

CUP_X = 0.082
CUP_Z = 0.190
CUP_R = 0.046

for sx in (-1, 1):
    end = band_point(sx * A_END, R_BAND)
    end.x = sx * abs(end.x)

    # slider that extends out of the headband end
    add_box("Slider_%d" % sx, (0.016, 0.020, 0.036),
            (sx * 0.1035, 0.0, end.z - 0.016),
            rot=(0, sx * math.radians(10.0), 0), mat=METAL, bevel=0.003)

    # yoke fork: two arms straddling the cup
    for sy in (-1, 1):
        add_box("YokeArm_%d_%d" % (sx, sy), (0.010, 0.011, 0.062),
                (sx * 0.102, sy * 0.031, end.z - 0.046),
                rot=(0, sx * math.radians(6.0), 0), mat=DARKMET, bevel=0.003)
    add_box("YokeBridge_%d" % sx, (0.012, 0.072, 0.014),
            (sx * 0.1015, 0.0, end.z - 0.020), mat=DARKMET, bevel=0.004)

    # gimbal pivot into the cup
    add_cyl("Pivot_%d" % sx, 0.008, 0.030, (sx * 0.100, 0.0, CUP_Z + 0.012),
            rot=(0, math.radians(90), 0), mat=METAL, segments=24)

    # cup body
    add_cyl("CupShell_%d" % sx, CUP_R, 0.026, (sx * CUP_X, 0.0, CUP_Z),
            rot=(0, math.radians(90), 0), mat=SHELL, segments=56, bevel=0.006)
    add_cyl("CupOuterPlate_%d" % sx, CUP_R - 0.004, 0.007,
            (sx * (CUP_X + 0.016), 0.0, CUP_Z), rot=(0, math.radians(90), 0),
            mat=SHELL_PLATE, segments=56, bevel=0.002)
    add_sphere("CupDome_%d" % sx, CUP_R - 0.006,
               (sx * (CUP_X + 0.019), 0.0, CUP_Z), mat=SHELL,
               useg=40, vseg=20, scale=(0.28, 1.0, 1.0))
    add_cyl("CupRing_%d" % sx, CUP_R + 0.001, 0.004, (sx * CUP_X, 0.0, CUP_Z),
            rot=(0, math.radians(90), 0), mat=ACCENT, segments=56)

    # ear cushion and driver grille on the inner face
    add_torus("Cushion_%d" % sx, CUP_R - 0.010, 0.014,
              (sx * (CUP_X - 0.020), 0.0, CUP_Z), (0.0, math.radians(90), 0.0),
              mat=FOAM, mseg=56, nseg=20)
    add_cyl("Grille_%d" % sx, CUP_R - 0.017, 0.004,
            (sx * (CUP_X - 0.024), 0.0, CUP_Z), rot=(0, math.radians(90), 0),
            mat=MESH, segments=48)

    # controls on the shell edge
    add_cyl("Dial_%d" % sx, 0.008, 0.008, (sx * CUP_X, -0.040, CUP_Z - 0.020),
            rot=(math.radians(90), 0, 0), mat=DARKMET, segments=20, bevel=0.002)

add_cyl("StatusLed", 0.0032, 0.003, (-(CUP_X + 0.010), -0.030, CUP_Z - 0.034),
        rot=(math.radians(90), 0, 0), mat=LED, segments=16)
add_cyl("CableSocket", 0.005, 0.008, (-(CUP_X - 0.004), 0.0, CUP_Z - CUP_R + 0.006),
        mat=DARKMET, segments=20)


# ----------------------------------------------------------------------------
# cable draped down to the table
# ----------------------------------------------------------------------------

add_curve("Cable", [
    (-(CUP_X - 0.004), 0.0, CUP_Z - CUP_R + 0.002),
    (-0.098, 0.020, 0.120),
    (-0.105, 0.050, 0.030),
    (-0.060, 0.075, 0.0035),
    (0.010, 0.055, 0.0035),
    (0.055, 0.010, 0.0035),
    (0.040, -0.045, 0.0035),
    (-0.020, -0.060, 0.0035),
], depth=0.0024, mat=CABLE)
add_cyl("CablePlugBody", 0.006, 0.030, (-0.048, -0.070, 0.0035),
        rot=(math.radians(90), 0, math.radians(30)), mat=DARKMET, segments=20)
add_cyl("CablePlugTip", 0.0022, 0.020, (-0.070, -0.082, 0.0035),
        rot=(0, math.radians(90), math.radians(30)), mat=METAL, segments=16)


# ----------------------------------------------------------------------------
# lighting and camera
# ----------------------------------------------------------------------------

add_light("Key", 'AREA', (-0.42, -0.40, 0.62), 70.0, (1.0, 0.97, 0.94),
          size=0.7, target=(0.0, 0.0, 0.21))
add_light("Fill", 'AREA', (0.50, -0.28, 0.32), 22.0, (0.78, 0.85, 1.0),
          size=0.8, target=(0.02, 0.0, 0.20))
add_light("Rim", 'AREA', (0.16, 0.52, 0.52), 55.0, (0.86, 0.90, 1.0),
          size=0.5, target=(0.0, 0.0, 0.24))
add_light("Bounce", 'AREA', (0.0, -0.10, 0.02), 6.0, (1.0, 0.95, 0.9),
          size=0.6, target=(0.0, 0.0, 0.3))

add_camera((0.40, -0.50, 0.335), (0.0, 0.0, 0.205), lens=62.0)

bpy.context.view_layer.update()
