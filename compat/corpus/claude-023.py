"""claude-023 - Water tower with tank, legs and ladder.

Elevated steel water tower: lathed tank with hopper bottom and conical
roof, four splayed legs with ring girts and X-bracing, a catwalk with
railing, a caged access ladder and a riser downpipe.
"""

import bpy
import bmesh
import math
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


def lathe(name, profile, segments=48, mat=None):
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
    bpy.context.scene.collection.objects.link(obj)
    if mat:
        assign(obj, mat)
    smooth(obj)
    return obj


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

world = bpy.data.worlds.new("World")
world.use_nodes = True
wbg = world.node_tree.nodes["Background"]
wbg.inputs[0].default_value = (0.34, 0.48, 0.70, 1.0)
wbg.inputs[1].default_value = 1.2
bpy.context.scene.world = world

TANK = make_material("TankPaint", (0.78, 0.80, 0.82), rough=0.42, metal=0.35)
ROOF = make_material("RoofPaint", (0.30, 0.42, 0.52), rough=0.48, metal=0.30)
STEEL = make_material("Steelwork", (0.44, 0.45, 0.47), rough=0.55, metal=0.85)
DKSTEEL = make_material("DarkSteel", (0.24, 0.25, 0.27), rough=0.62, metal=0.80)
CONC = make_material("Concrete", (0.66, 0.65, 0.62), rough=0.92)
GROUND = make_material("Ground", (0.24, 0.30, 0.16), rough=0.95)
GRAVEL = make_material("Gravel", (0.44, 0.42, 0.39), rough=0.95)

# ---- geometry constants
LEG_N = 4
R_FOOT = 4.5
R_TOP = 2.55
Z_TOP = 11.90
Z_TANK_BOT = 11.80
Z_TANK_TOP = 16.20
R_TANK = 3.00
LEVELS = (0.0, 3.60, 7.20, 10.80)
ANGLES = [math.radians(45.0 + 90.0 * i) for i in range(LEG_N)]


def leg_point(angle, z):
    t = max(0.0, min(1.0, z / Z_TOP))
    r = R_FOOT + (R_TOP - R_FOOT) * t
    return Vector((r * math.cos(angle), r * math.sin(angle), z))


# ---- ground
bpy.ops.mesh.primitive_plane_add(size=80.0, location=(0.0, 0.0, 0.0))
g = bpy.context.active_object
g.name = "Ground"
assign(g, GROUND)

bpy.ops.mesh.primitive_cylinder_add(vertices=48, radius=7.5, depth=0.10,
                                    location=(0.0, 0.0, 0.05))
pad = bpy.context.active_object
pad.name = "GravelPad"
assign(pad, GRAVEL)

# ---- tank: hopper bottom + barrel + conical roof, one solid of revolution
tank_profile = [
    (0.000, 10.30), (0.36, 10.48), (1.60, 11.10), (2.86, 11.72),
    (2.98, 11.86), (3.000, 12.10), (3.000, 15.90), (2.96, 16.14),
    (2.80, 16.34), (1.70, 16.95), (0.62, 17.42), (0.22, 17.56),
    (0.000, 17.60),
]
tank = lathe("Tank", tank_profile, segments=64, mat=TANK)

# barrel banding
for z in (12.60, 13.80, 15.00):
    bpy.ops.mesh.primitive_torus_add(major_radius=3.02, minor_radius=0.055,
                                     major_segments=64, minor_segments=8,
                                     location=(0.0, 0.0, z))
    b = bpy.context.active_object
    b.name = "TankBand"
    assign(b, STEEL)
    smooth(b)

# eave ring where the roof springs from the barrel
bpy.ops.mesh.primitive_torus_add(major_radius=2.98, minor_radius=0.09,
                                 major_segments=64, minor_segments=8,
                                 location=(0.0, 0.0, 16.16))
assign(bpy.context.active_object, STEEL)
bpy.context.active_object.name = "EaveRing"
smooth(bpy.context.active_object)

# roof colour overlay: a thin lathed cap sitting on the cone
roof_cap = lathe("RoofSkin", [
    (2.86, 16.32), (1.70, 16.93), (0.62, 17.40), (0.22, 17.54)],
    segments=64, mat=ROOF)
rs = roof_cap.modifiers.new("Solidify", 'SOLIDIFY')
rs.thickness = 0.05
rs.offset = 1.0

# roof hatch and vent
vent = lathe("RoofVent", [
    (0.000, 17.58), (0.34, 17.60), (0.36, 17.86), (0.52, 17.92),
    (0.50, 18.02), (0.000, 18.06)], segments=32, mat=STEEL)
box("RoofHatch", (0.80, 0.80, 0.14), (1.35, 0.0, 17.14),
    (0.0, math.radians(-24.0), 0.0), mat=DKSTEEL)

# ---- legs, feet and pier pads
for i, a in enumerate(ANGLES):
    p0 = leg_point(a, 0.0)
    p1 = leg_point(a, Z_TOP)
    strut("Leg_%d" % i, p0, p1, 0.165, STEEL, verts=12)
    bpy.ops.mesh.primitive_cylinder_add(vertices=24, radius=0.62, depth=0.45,
                                        location=(p0.x, p0.y, 0.16))
    pier = bpy.context.active_object
    pier.name = "Pier_%d" % i
    assign(pier, CONC)
    smooth(pier)
    box("BasePlate_%d" % i, (0.55, 0.55, 0.05), (p0.x, p0.y, 0.40), mat=DKSTEEL)

# ---- ring girts and X bracing between the legs
for li, z in enumerate(LEVELS):
    if z <= 0.01:
        continue
    for i in range(LEG_N):
        a1 = ANGLES[i]
        a2 = ANGLES[(i + 1) % LEG_N]
        strut("Girt_%d_%d" % (li, i), leg_point(a1, z), leg_point(a2, z),
              0.075, STEEL, verts=8)

for li in range(len(LEVELS) - 1):
    zl, zu = LEVELS[li], LEVELS[li + 1]
    for i in range(LEG_N):
        a1 = ANGLES[i]
        a2 = ANGLES[(i + 1) % LEG_N]
        strut("BraceA_%d_%d" % (li, i), leg_point(a1, zl), leg_point(a2, zu),
              0.05, DKSTEEL, verts=8)
        strut("BraceB_%d_%d" % (li, i), leg_point(a2, zl), leg_point(a1, zu),
              0.05, DKSTEEL, verts=8)

# ---- catwalk deck around the tank base
deck = lathe("Catwalk", [
    (2.92, 11.78), (3.95, 11.78), (3.95, 11.86), (2.92, 11.86), (2.92, 11.78)],
    segments=64, mat=DKSTEEL)

# outer toe board
toe = lathe("ToeBoard", [(3.93, 11.86), (3.93, 12.02)], segments=64, mat=DKSTEEL)
ts = toe.modifiers.new("Solidify", 'SOLIDIFY')
ts.thickness = 0.03

# catwalk support brackets down to the legs
for i, a in enumerate(ANGLES):
    for off in (-0.30, 0.30):
        aa = a + off
        strut("DeckBracket_%d" % i,
              (2.60 * math.cos(aa), 2.60 * math.sin(aa), 10.90),
              (3.90 * math.cos(aa), 3.90 * math.sin(aa), 11.78),
              0.05, STEEL, verts=8)

# railing: 16 posts and two rails
for i in range(16):
    a = math.tau * i / 16.0
    strut("RailPost_%02d" % i,
          (3.82 * math.cos(a), 3.82 * math.sin(a), 11.86),
          (3.82 * math.cos(a), 3.82 * math.sin(a), 12.94),
          0.035, DKSTEEL, verts=8)
for z in (12.36, 12.90):
    bpy.ops.mesh.primitive_torus_add(major_radius=3.82, minor_radius=0.035,
                                     major_segments=64, minor_segments=8,
                                     location=(0.0, 0.0, z))
    r = bpy.context.active_object
    r.name = "CatwalkRail"
    assign(r, DKSTEEL)
    smooth(r)

# ---- access ladder on the -Y side with a safety cage
LAD_Y = -4.15
LAD_HW = 0.26
LAD_TOP = 12.90
for sx in (-1.0, 1.0):
    strut("LadderStringer_%d" % int(sx),
          (sx * LAD_HW, LAD_Y, 0.10), (sx * LAD_HW, LAD_Y, LAD_TOP),
          0.045, DKSTEEL, verts=8)

n_rungs = int((LAD_TOP - 0.55) / 0.32)
for i in range(n_rungs):
    z = 0.55 + i * 0.32
    strut("Rung_%02d" % i, (-LAD_HW, LAD_Y, z), (LAD_HW, LAD_Y, z),
          0.022, DKSTEEL, verts=8)

# cage hoops and their longitudinal bars
hoop_zs = [2.60 + 0.90 * i for i in range(11)]
for i, z in enumerate(hoop_zs):
    if z > LAD_TOP - 0.2:
        break
    bpy.ops.mesh.primitive_torus_add(major_radius=0.42, minor_radius=0.022,
                                     major_segments=32, minor_segments=6,
                                     location=(0.0, LAD_Y - 0.16, z))
    h = bpy.context.active_object
    h.name = "CageHoop_%02d" % i
    assign(h, DKSTEEL)
    smooth(h)

for a_deg in (-60.0, -20.0, 20.0, 60.0, 180.0):
    a = math.radians(a_deg)
    px = 0.42 * math.sin(a)
    py = LAD_Y - 0.16 - 0.42 * math.cos(a)
    strut("CageBar", (px, py, 2.60), (px, py, min(LAD_TOP - 0.2, hoop_zs[-1])),
          0.018, DKSTEEL, verts=6)

# ladder standoff brackets tied back to the nearest bracing
for z in (3.60, 7.20, 10.80):
    strut("LadderStay", (0.0, LAD_Y, z),
          (0.0, LAD_Y + 0.9, z), 0.03, DKSTEEL, verts=6)

# ---- riser pipe and valve gear
strut("Riser", (0.0, 0.0, 0.0), (0.0, 0.0, 10.45), 0.24, STEEL, verts=20)
bpy.ops.mesh.primitive_torus_add(major_radius=0.30, minor_radius=0.06,
                                 major_segments=32, minor_segments=8,
                                 location=(0.0, 0.0, 1.60))
assign(bpy.context.active_object, DKSTEEL)
bpy.context.active_object.name = "RiserFlange"
smooth(bpy.context.active_object)

strut("OutletElbow", (0.0, 0.0, 0.90), (1.30, 0.0, 0.90), 0.18, STEEL, verts=16)
box("ValveBox", (0.9, 0.9, 0.8), (1.85, 0.0, 0.40), mat=CONC)

# overflow pipe hugging one leg
strut("Overflow", (0.0, 3.0, 11.60), (0.0, 3.6, 6.0), 0.07, STEEL, verts=8)
strut("Overflow2", (0.0, 3.6, 6.0), (0.0, 4.1, 0.4), 0.07, STEEL, verts=8)

# --------------------------------------------------------------- lighting
bpy.ops.object.light_add(type='SUN', location=(14.0, -18.0, 30.0))
sun = bpy.context.active_object
sun.name = "Sun"
sun.data.energy = 4.0
sun.data.angle = math.radians(2.0)
sun.data.color = (1.0, 0.96, 0.90)
look_at(sun, (0.0, 0.0, 9.0))

bpy.ops.object.light_add(type='AREA', location=(-20.0, 14.0, 16.0))
fill = bpy.context.active_object
fill.name = "Fill"
fill.data.energy = 6000.0
fill.data.size = 16.0
fill.data.color = (0.70, 0.80, 1.0)
look_at(fill, (0.0, 0.0, 10.0))

# ----------------------------------------------------------------- camera
cam_data = bpy.data.cameras.new("Camera")
cam_data.lens = 45.0
cam_data.clip_end = 500.0
cam = bpy.data.objects.new("Camera", cam_data)
cam.location = (19.0, -24.0, 11.5)
bpy.context.scene.collection.objects.link(cam)
look_at(cam, (0.0, 0.0, 9.5))
bpy.context.scene.camera = cam

print("claude-023 water tower built: %d objects" % len(bpy.data.objects))
