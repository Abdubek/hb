"""claude-022 - Camping lantern with handle and protective frame.

A kerosene style storm lantern: lathed fuel font, burner gallery, glass
globe, vented hood, four-bar protective cage with rings, a swept wire bail
handle and a lit flame.  Sits on a plank table in a dark scene.
"""

import bpy
import bmesh
import math
from mathutils import Vector


# --------------------------------------------------------------- utilities
def reset_scene():
    bpy.ops.wm.read_factory_settings(use_empty=True)


def make_material(name, color, rough=0.5, metal=0.0, transmission=0.0,
                  emission=None, emission_strength=0.0, ior=1.45):
    mat = bpy.data.materials.new(name)
    mat.use_nodes = True
    bsdf = mat.node_tree.nodes["Principled BSDF"]

    def setv(key, val):
        if key in bsdf.inputs:
            bsdf.inputs[key].default_value = val

    setv("Base Color", (color[0], color[1], color[2], 1.0))
    setv("Roughness", rough)
    setv("Metallic", metal)
    setv("IOR", ior)
    if transmission:
        setv("Transmission Weight", transmission)
    if emission is not None:
        setv("Emission Color", (emission[0], emission[1], emission[2], 1.0))
        setv("Emission Strength", emission_strength)
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


def lathe(name, profile, segments=48, mat=None, location=(0.0, 0.0, 0.0)):
    """Solid/shell of revolution from a list of (radius, z) profile points."""
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
    obj.location = location
    bpy.context.scene.collection.objects.link(obj)
    if mat:
        assign(obj, mat)
    smooth(obj)
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


def box(name, size, location, rotation=(0.0, 0.0, 0.0), mat=None):
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=location, rotation=rotation)
    obj = bpy.context.active_object
    obj.name = name
    obj.scale = size
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    if mat:
        assign(obj, mat)
    return obj


def look_at(obj, target):
    d = Vector(target) - obj.location
    obj.rotation_euler = d.to_track_quat('-Z', 'Y').to_euler()


# ------------------------------------------------------------------- scene
reset_scene()
scene = bpy.context.scene
try:
    scene.render.engine = 'CYCLES'
    scene.cycles.samples = 128
except Exception:
    pass

world = bpy.data.worlds.new("World")
world.use_nodes = True
wbg = world.node_tree.nodes["Background"]
wbg.inputs[0].default_value = (0.02, 0.025, 0.04, 1.0)
wbg.inputs[1].default_value = 0.35
scene.world = world

STEEL = make_material("GalvSteel", (0.62, 0.63, 0.65), rough=0.34, metal=1.0)
BRASS = make_material("Brass", (0.72, 0.55, 0.22), rough=0.28, metal=1.0)
PAINT = make_material("RedEnamel", (0.44, 0.06, 0.05), rough=0.35, metal=0.15)
GLASS = make_material("LanternGlass", (0.94, 0.93, 0.88), rough=0.05,
                      transmission=1.0, ior=1.47)
FLAME = make_material("Flame", (0.02, 0.01, 0.0), rough=0.9,
                      emission=(1.0, 0.55, 0.16), emission_strength=28.0)
WICKM = make_material("Wick", (0.10, 0.09, 0.08), rough=0.95)
TABLE = make_material("TablePlank", (0.26, 0.16, 0.09), rough=0.75)
GROUND = make_material("Ground", (0.09, 0.09, 0.10), rough=0.95)

# ---- table the lantern rests on
bpy.ops.mesh.primitive_plane_add(size=12.0, location=(0.0, 0.0, -0.42))
assign(bpy.context.active_object, GROUND)
bpy.context.active_object.name = "Ground"

for i in range(6):
    y = -0.55 + i * 0.22
    plank = box("Plank_%d" % i, (1.6, 0.205, 0.035), (0.0, y, -0.0175), mat=TABLE)
    m = plank.modifiers.new("Bevel", 'BEVEL')
    m.width = 0.004
    m.segments = 2
for sx in (-1.0, 1.0):
    box("TableLeg_%d" % int(sx), (0.07, 0.07, 0.40),
        (sx * 0.62, -0.05, -0.235), mat=TABLE)

# ---- fuel font (lathed)
font_profile = [
    (0.000, 0.000), (0.070, 0.000), (0.088, 0.012), (0.094, 0.032),
    (0.094, 0.072), (0.086, 0.096), (0.066, 0.112), (0.058, 0.122),
    (0.058, 0.132), (0.000, 0.132),
]
font = lathe("FuelFont", font_profile, segments=48, mat=PAINT)

# fuel filler cap on the shoulder
bpy.ops.mesh.primitive_cylinder_add(vertices=20, radius=0.020, depth=0.016,
                                    location=(0.060, 0.038, 0.104))
cap = bpy.context.active_object
cap.name = "FillerCap"
cap.rotation_euler = (math.radians(18.0), 0.0, 0.0)
assign(cap, BRASS)
smooth(cap)

# ---- burner gallery and wick knob
gallery = lathe("BurnerGallery", [
    (0.000, 0.130), (0.056, 0.130), (0.058, 0.140), (0.052, 0.152),
    (0.052, 0.164), (0.000, 0.164)], segments=40, mat=BRASS)

for i in range(16):
    a = math.tau * i / 16.0
    box("GalleryFlute_%d" % i, (0.006, 0.006, 0.026),
        (0.055 * math.cos(a), 0.055 * math.sin(a), 0.145),
        (0.0, 0.0, a), mat=BRASS)

strut("KnobShaft", (0.05, 0.0, 0.146), (0.098, 0.0, 0.146), 0.005, BRASS)
bpy.ops.mesh.primitive_cylinder_add(vertices=16, radius=0.020, depth=0.008,
                                    location=(0.104, 0.0, 0.146),
                                    rotation=(0.0, math.radians(90.0), 0.0))
knob = bpy.context.active_object
knob.name = "WickKnob"
assign(knob, BRASS)
smooth(knob)

# ---- glass globe: an open lathed shell given thickness by solidify
globe_profile = [
    (0.050, 0.164), (0.062, 0.180), (0.074, 0.212), (0.076, 0.246),
    (0.068, 0.282), (0.054, 0.312), (0.050, 0.330),
]
globe = lathe("Globe", globe_profile, segments=56, mat=GLASS)
sol = globe.modifiers.new("Solidify", 'SOLIDIFY')
sol.thickness = 0.0035
sol.offset = 0.0

# ---- vented hood / top cap
hood = lathe("Hood", [
    (0.000, 0.330), (0.092, 0.336), (0.094, 0.348), (0.080, 0.362),
    (0.048, 0.386), (0.026, 0.398), (0.024, 0.412), (0.000, 0.416)],
    segments=48, mat=STEEL)

# louvre slots around the hood skirt
for i in range(12):
    a = math.tau * i / 12.0
    box("Louvre_%d" % i, (0.020, 0.004, 0.012),
        (0.086 * math.cos(a), 0.086 * math.sin(a), 0.352),
        (0.0, 0.0, a), mat=PAINT)

# chimney crown
crown = lathe("Crown", [
    (0.000, 0.416), (0.028, 0.418), (0.030, 0.430), (0.018, 0.438),
    (0.000, 0.440)], segments=32, mat=STEEL)

# ---- protective cage: four uprights plus two rings
for i in range(4):
    a = math.tau * i / 4.0 + math.radians(45.0)
    r0, r1 = 0.088, 0.090
    strut("CageBar_%d" % i,
          (r0 * math.cos(a), r0 * math.sin(a), 0.030),
          (r1 * math.cos(a), r1 * math.sin(a), 0.344),
          0.0055, STEEL, verts=10)

for z, rr in ((0.196, 0.089), (0.288, 0.086)):
    bpy.ops.mesh.primitive_torus_add(major_radius=rr, minor_radius=0.0048,
                                     major_segments=48, minor_segments=8,
                                     location=(0.0, 0.0, z))
    ring = bpy.context.active_object
    ring.name = "CageRing"
    assign(ring, STEEL)
    smooth(ring)

# base ring skirt tying the cage to the font
bpy.ops.mesh.primitive_torus_add(major_radius=0.090, minor_radius=0.006,
                                 major_segments=48, minor_segments=8,
                                 location=(0.0, 0.0, 0.030))
assign(bpy.context.active_object, STEEL)
bpy.context.active_object.name = "BaseRing"
smooth(bpy.context.active_object)

# ---- bail handle: swept wire arc between two ears on the hood
for sx in (-1.0, 1.0):
    ear = box("HandleEar_%d" % int(sx), (0.010, 0.026, 0.030),
              (sx * 0.086, 0.0, 0.352), mat=STEEL)
    smooth(ear)

curve_data = bpy.data.curves.new("HandleCurve", 'CURVE')
curve_data.dimensions = '3D'
curve_data.bevel_depth = 0.0055
curve_data.bevel_resolution = 4
curve_data.resolution_u = 12
spline = curve_data.splines.new('NURBS')
HN = 17
spline.points.add(HN - 1)
for i in range(HN):
    t = i / (HN - 1.0)
    ang = math.pi * t
    x = -0.086 * math.cos(ang)
    z = 0.352 + math.sin(ang) * 0.145
    spline.points[i].co = (x, 0.0, z, 1.0)
spline.use_endpoint_u = True
spline.order_u = 3
handle = bpy.data.objects.new("BailHandle", curve_data)
bpy.context.scene.collection.objects.link(handle)
assign(handle, STEEL)

# grip sleeve on the handle apex
bpy.ops.mesh.primitive_cylinder_add(vertices=16, radius=0.011, depth=0.055,
                                    location=(0.0, 0.0, 0.494),
                                    rotation=(0.0, math.radians(90.0), 0.0))
grip = bpy.context.active_object
grip.name = "HandleGrip"
assign(grip, WICKM)
smooth(grip)

# ---- wick and flame
bpy.ops.mesh.primitive_cylinder_add(vertices=12, radius=0.010, depth=0.020,
                                    location=(0.0, 0.0, 0.170))
wick = bpy.context.active_object
wick.name = "Wick"
wick.scale = (1.6, 0.35, 1.0)
assign(wick, WICKM)

bpy.ops.mesh.primitive_uv_sphere_add(segments=20, ring_count=12, radius=0.030,
                                     location=(0.0, 0.0, 0.204))
flame = bpy.context.active_object
flame.name = "Flame"
flame.scale = (0.55, 0.30, 1.35)
bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
assign(flame, FLAME)
smooth(flame)

# --------------------------------------------------------------- lighting
bpy.ops.object.light_add(type='POINT', location=(0.0, 0.0, 0.205))
lamp = bpy.context.active_object
lamp.name = "FlameLight"
lamp.data.energy = 14.0
lamp.data.shadow_soft_size = 0.02
lamp.data.color = (1.0, 0.68, 0.36)

bpy.ops.object.light_add(type='AREA', location=(-0.9, -0.7, 0.9))
key = bpy.context.active_object
key.name = "KeyLight"
key.data.energy = 18.0
key.data.size = 0.7
key.data.color = (0.62, 0.72, 1.0)
look_at(key, (0.0, 0.0, 0.22))

bpy.ops.object.light_add(type='AREA', location=(1.1, 0.9, 0.6))
rim = bpy.context.active_object
rim.name = "RimLight"
rim.data.energy = 10.0
rim.data.size = 0.6
rim.data.color = (0.75, 0.82, 1.0)
look_at(rim, (0.0, 0.0, 0.25))

# ----------------------------------------------------------------- camera
cam_data = bpy.data.cameras.new("Camera")
cam_data.lens = 60.0
cam = bpy.data.objects.new("Camera", cam_data)
cam.location = (0.62, -0.78, 0.46)
bpy.context.scene.collection.objects.link(cam)
look_at(cam, (0.0, 0.0, 0.235))
bpy.context.scene.camera = cam

print("claude-022 lantern built: %d objects" % len(bpy.data.objects))
