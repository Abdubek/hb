"""
claude-052 : Round storage tank with access ladder and safety rail
Blender 4.5 LTS - build only, no render, no file output.
"""

import bpy
import bmesh
from math import sin, cos, asin, sqrt, radians, pi
from mathutils import Vector

# ----------------------------------------------------------------------------
# scene reset
# ----------------------------------------------------------------------------
bpy.ops.wm.read_factory_settings(use_empty=True)
scene = bpy.context.scene
scene.unit_settings.system = 'METRIC'
scene.render.resolution_x = 1600
scene.render.resolution_y = 1100

C = bpy.context.collection


# ----------------------------------------------------------------------------
# helpers
# ----------------------------------------------------------------------------
def make_material(name, color, metallic=0.0, roughness=0.5):
    m = bpy.data.materials.new(name)
    m.use_nodes = True
    bsdf = m.node_tree.nodes["Principled BSDF"]
    bsdf.inputs["Base Color"].default_value = (*color, 1.0)
    bsdf.inputs["Metallic"].default_value = metallic
    bsdf.inputs["Roughness"].default_value = roughness
    return m


def new_obj(name, mesh, mat=None):
    ob = bpy.data.objects.new(name, mesh)
    C.objects.link(ob)
    if mat:
        ob.data.materials.append(mat)
    return ob


def mesh_from_pydata(name, verts, faces, smooth=False):
    me = bpy.data.meshes.new(name)
    me.from_pydata(verts, [], faces)
    me.validate()
    me.update()
    if smooth:
        for p in me.polygons:
            p.use_smooth = True
    return me


def prim_cyl(name, radius, depth, location, rotation=(0, 0, 0), verts=32, mat=None):
    bpy.ops.mesh.primitive_cylinder_add(vertices=verts, radius=radius, depth=depth,
                                        location=location, rotation=rotation)
    ob = bpy.context.object
    ob.name = name
    bpy.ops.object.shade_smooth()
    for p in ob.data.polygons:            # keep the flat caps flat
        if abs(p.normal.z) > 0.7:
            p.use_smooth = False
    if mat:
        ob.data.materials.append(mat)
    return ob


def prim_box(name, size, location, rotation=(0, 0, 0), mat=None):
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=location, rotation=rotation)
    ob = bpy.context.object
    ob.name = name
    ob.scale = size
    if mat:
        ob.data.materials.append(mat)
    return ob


def tube(name, points, radius, cyclic=False, mat=None, res=3):
    """A swept round profile along a polyline - used for all rails and cages."""
    cu = bpy.data.curves.new(name, 'CURVE')
    cu.dimensions = '3D'
    cu.resolution_u = 2
    cu.bevel_depth = radius
    cu.bevel_resolution = res
    cu.use_fill_caps = True
    sp = cu.splines.new('POLY')
    sp.points.add(len(points) - 1)
    for i, p in enumerate(points):
        sp.points[i].co = (p[0], p[1], p[2], 1.0)
    sp.use_cyclic_u = cyclic
    ob = bpy.data.objects.new(name, cu)
    C.objects.link(ob)
    if mat:
        ob.data.materials.append(mat)
    return ob


def arc_points(cx, cy, z, radius, a0, a1, steps):
    return [(cx + radius * cos(a0 + (a1 - a0) * i / steps),
             cy + radius * sin(a0 + (a1 - a0) * i / steps),
             z) for i in range(steps + 1)]


# ----------------------------------------------------------------------------
# materials
# ----------------------------------------------------------------------------
mat_shell = make_material("TankPaint", (0.72, 0.74, 0.71), 0.15, 0.42)
mat_roof = make_material("RoofPaint", (0.55, 0.58, 0.58), 0.20, 0.50)
mat_steel = make_material("GalvSteel", (0.62, 0.64, 0.66), 1.00, 0.38)
mat_dark = make_material("DarkSteel", (0.18, 0.19, 0.20), 0.90, 0.45)
mat_safety = make_material("SafetyYellow", (0.86, 0.62, 0.05), 0.10, 0.40)
mat_concrete = make_material("Concrete", (0.55, 0.54, 0.51), 0.0, 0.85)
mat_ground = make_material("Ground", (0.26, 0.27, 0.24), 0.0, 0.95)

# ----------------------------------------------------------------------------
# main dimensions
# ----------------------------------------------------------------------------
R = 3.20           # tank radius
H = 7.00           # shell height (top of shell / eave)
RISE = 0.95        # roof dome rise
SEG = 64           # circumferential segments

Rs = (R * R + RISE * RISE) / (2.0 * RISE)     # dome sphere radius
CZ = H + RISE - Rs                            # dome sphere centre z


def dome_z(r):
    return CZ + sqrt(max(Rs * Rs - r * r, 0.0))


# ----------------------------------------------------------------------------
# ground and foundation
# ----------------------------------------------------------------------------
bpy.ops.mesh.primitive_plane_add(size=60.0, location=(0, 0, -0.32))
ground = bpy.context.object
ground.name = "Ground"
ground.data.materials.append(mat_ground)

prim_cyl("Foundation", R + 0.95, 0.34, (0, 0, -0.15), verts=64, mat=mat_concrete)

# ----------------------------------------------------------------------------
# tank shell (open topped cylinder, thickened by a solidify modifier)
# ----------------------------------------------------------------------------
verts, faces = [], []
for i in range(SEG):
    a = 2.0 * pi * i / SEG
    verts.append((R * cos(a), R * sin(a), 0.0))
for i in range(SEG):
    a = 2.0 * pi * i / SEG
    verts.append((R * cos(a), R * sin(a), H))
for i in range(SEG):
    j = (i + 1) % SEG
    faces.append((i, j, j + SEG, i + SEG))
faces.append(tuple(range(SEG - 1, -1, -1)))          # bottom plate

shell = new_obj("TankShell", mesh_from_pydata("TankShell", verts, faces, smooth=True), mat_shell)
for p in shell.data.polygons:
    if len(p.vertices) > 4:
        p.use_smooth = False
sol = shell.modifiers.new("Shell", 'SOLIDIFY')
sol.thickness = 0.05
sol.offset = -1.0

# ----------------------------------------------------------------------------
# domed roof
# ----------------------------------------------------------------------------
RINGS = 10
theta_max = asin(min(R / Rs, 1.0))
dverts = [(0.0, 0.0, H + RISE)]
dfaces = []
for ring in range(1, RINGS + 1):
    th = theta_max * ring / RINGS
    rr, zz = Rs * sin(th), CZ + Rs * cos(th)
    for i in range(SEG):
        a = 2.0 * pi * i / SEG
        dverts.append((rr * cos(a), rr * sin(a), zz))
for i in range(SEG):
    dfaces.append((0, 1 + i, 1 + (i + 1) % SEG))
for ring in range(RINGS - 1):
    b0 = 1 + ring * SEG
    b1 = b0 + SEG
    for i in range(SEG):
        j = (i + 1) % SEG
        dfaces.append((b0 + i, b0 + j, b1 + j, b1 + i))

roof = new_obj("RoofDome", mesh_from_pydata("RoofDome", dverts, dfaces, smooth=True), mat_roof)
rsol = roof.modifiers.new("Plate", 'SOLIDIFY')
rsol.thickness = 0.04
rsol.offset = -1.0

# eave angle / curb ring
bpy.ops.mesh.primitive_torus_add(location=(0, 0, H), major_radius=R + 0.02,
                                 minor_radius=0.07, major_segments=SEG, minor_segments=10)
eave = bpy.context.object
eave.name = "EaveAngle"
eave.data.materials.append(mat_shell)
bpy.ops.object.shade_smooth()

# shell stiffener rings
for z in (2.45, 4.90):
    bpy.ops.mesh.primitive_torus_add(location=(0, 0, z), major_radius=R + 0.03,
                                     minor_radius=0.055, major_segments=SEG, minor_segments=8)
    ob = bpy.context.object
    ob.name = "StiffenerRing"
    ob.data.materials.append(mat_shell)
    bpy.ops.object.shade_smooth()

# anchor chairs around the base
for i in range(12):
    a = 2.0 * pi * i / 12 + radians(15)
    prim_box("AnchorChair", (0.10, 0.34, 0.55),
             ((R + 0.06) * cos(a), (R + 0.06) * sin(a), 0.28),
             rotation=(0, 0, a), mat=mat_shell)

# ----------------------------------------------------------------------------
# nozzles, manway, roof fittings
# ----------------------------------------------------------------------------
def flanged_nozzle(loc, rot, length, radius):
    prim_cyl("Nozzle", radius, length, loc, rot, verts=20, mat=mat_dark)
    d = Vector((0, 0, 1))
    d.rotate(bpy.context.object.rotation_euler)
    prim_cyl("Flange", radius * 1.6, 0.06,
             (Vector(loc) + d * (length * 0.5 - 0.03)), rot, verts=20, mat=mat_dark)


# shell manway (facing -Y) with cover plate
mw_a = radians(-90)
prim_cyl("Manway", 0.32, 0.40, ((R + 0.10) * cos(mw_a), (R + 0.10) * sin(mw_a), 1.35),
         rotation=(radians(90), 0, -mw_a), verts=28, mat=mat_dark)
prim_cyl("ManwayCover", 0.42, 0.07, ((R + 0.30) * cos(mw_a), (R + 0.30) * sin(mw_a), 1.35),
         rotation=(radians(90), 0, -mw_a), verts=28, mat=mat_dark)

# outlet and inlet nozzles
for ang, z, ln, rd in ((radians(200), 0.85, 0.55, 0.13), (radians(150), 5.60, 0.45, 0.10)):
    flanged_nozzle(((R + 0.22) * cos(ang), (R + 0.22) * sin(ang), z),
                   (radians(90), 0, radians(90) + ang), ln, rd)

# roof vent and gauge hatch
prim_cyl("RoofVent", 0.26, 0.55, (0, 0, H + RISE + 0.20), verts=24, mat=mat_dark)
prim_cyl("VentCap", 0.36, 0.06, (0, 0, H + RISE + 0.50), verts=24, mat=mat_dark)
hx, hy = 1.30, -0.60
prim_cyl("Hatch", 0.30, 0.22, (hx, hy, dome_z(sqrt(hx * hx + hy * hy)) + 0.10),
         verts=24, mat=mat_safety)

# ----------------------------------------------------------------------------
# access ladder (on the +X side)
# ----------------------------------------------------------------------------
LX = R + 0.30          # stile plane, standing off the shell
LW = 0.24              # half rung width
Z_BOT = 0.38
Z_TOP = H + 1.10       # grab-rail extension above the roof deck

for s in (-1, 1):
    tube("LadderStile", [(LX, s * LW, Z_BOT), (LX, s * LW, Z_TOP)], 0.038, mat=mat_steel)

n_rung = int((H - 0.10 - Z_BOT) / 0.30)
for i in range(n_rung + 1):
    z = Z_BOT + 0.30 * i
    prim_cyl("Rung", 0.020, LW * 2.0, (LX, 0.0, z),
             rotation=(radians(90), 0, 0), verts=12, mat=mat_steel)

# stand-off brackets tying the ladder back to the shell
for z in (1.10, 3.10, 5.10, 6.90):
    for s in (-1, 1):
        tube("LadderBracket", [(R - 0.02, s * LW, z), (LX, s * LW, z)], 0.030, mat=mat_steel)

# ----------------------------------------------------------------------------
# ladder safety cage
# ----------------------------------------------------------------------------
CAGE_R = 0.40
CX = LX + 0.10                       # hoop centre, pushed outboard of the stiles
CAGE_BOT, CAGE_TOP = 2.40, H + 0.85
hoop_z = []
z = CAGE_BOT
while z <= CAGE_TOP + 1e-6:
    hoop_z.append(z)
    z += 0.75
hoop_z.append(CAGE_TOP)

a_open = radians(107)                # C-hoop, opening faces the ladder / tank
for z in hoop_z:
    tube("CageHoop", arc_points(CX, 0.0, z, CAGE_R, -a_open, a_open, 26), 0.028, mat=mat_steel)
    for s in (-1, 1):
        p = (CX + CAGE_R * cos(a_open), s * CAGE_R * sin(a_open), z)
        tube("CageTie", [p, (LX, s * LW, z)], 0.024, mat=mat_steel)

for a in (radians(-95), radians(-48), 0.0, radians(48), radians(95)):
    tube("CageBar",
         [(CX + CAGE_R * cos(a), CAGE_R * sin(a), hoop_z[0]),
          (CX + CAGE_R * cos(a), CAGE_R * sin(a), hoop_z[-1])], 0.022, mat=mat_steel)

# flared cage entry hoop at the bottom
tube("CageFlare", arc_points(CX, 0.0, CAGE_BOT - 0.55, CAGE_R + 0.14, -a_open, a_open, 26),
     0.026, mat=mat_steel)
for a in (radians(-95), 0.0, radians(95)):
    tube("CageFlareBar",
         [(CX + (CAGE_R + 0.14) * cos(a), (CAGE_R + 0.14) * sin(a), CAGE_BOT - 0.55),
          (CX + CAGE_R * cos(a), CAGE_R * sin(a), CAGE_BOT)], 0.022, mat=mat_steel)

# ----------------------------------------------------------------------------
# roof safety rail (guardrail with top rail, mid rail, toe board and posts)
# ----------------------------------------------------------------------------
RAIL_R = R - 0.30
DECK_Z = dome_z(RAIL_R)
TOP_Z = DECK_Z + 1.10
MID_Z = DECK_Z + 0.55
TOE_Z = DECK_Z + 0.09

GAP = radians(15)                    # ladder access opening at angle 0
a0, a1 = GAP, 2.0 * pi - GAP

tube("RailTop", arc_points(0, 0, TOP_Z, RAIL_R, a0, a1, 96), 0.032, mat=mat_safety)
tube("RailMid", arc_points(0, 0, MID_Z, RAIL_R, a0, a1, 96), 0.028, mat=mat_safety)
tube("RailToe", arc_points(0, 0, TOE_Z, RAIL_R, a0, a1, 96), 0.045, mat=mat_safety)

n_post = 16
for i in range(n_post + 1):
    a = a0 + (a1 - a0) * i / n_post
    x, y = RAIL_R * cos(a), RAIL_R * sin(a)
    tube("RailPost", [(x, y, dome_z(RAIL_R) - 0.05), (x, y, TOP_Z)], 0.034, mat=mat_safety)
    prim_box("PostBase", (0.20, 0.20, 0.04), (x, y, dome_z(RAIL_R) + 0.01),
             rotation=(0, 0, a), mat=mat_safety)

# rail returns running out to the ladder head, closing the access opening
for s in (-1, 1):
    a = s * GAP
    x, y = RAIL_R * cos(a), RAIL_R * sin(a)
    for zz, rr in ((TOP_Z, 0.032), (MID_Z, 0.028)):
        tube("RailReturn", [(x, y, zz), (LX + 0.02, s * LW, zz)], rr, mat=mat_safety)
    tube("ReturnPost", [(LX + 0.02, s * LW, DECK_Z - 0.30),
                        (LX + 0.02, s * LW, TOP_Z)], 0.034, mat=mat_safety)

# small grating landing at the ladder head
prim_box("Landing", (0.55, 0.75, 0.05), (LX - 0.05, 0.0, DECK_Z + 0.03), mat=mat_steel)

# ----------------------------------------------------------------------------
# lighting
# ----------------------------------------------------------------------------
world = bpy.data.worlds.new("World")
scene.world = world
world.use_nodes = True
world.node_tree.nodes["Background"].inputs["Color"].default_value = (0.13, 0.17, 0.24, 1.0)
world.node_tree.nodes["Background"].inputs["Strength"].default_value = 1.0

sun_data = bpy.data.lights.new("Sun", 'SUN')
sun_data.energy = 4.0
sun_data.angle = radians(2.5)
sun_data.color = (1.0, 0.95, 0.87)
sun = bpy.data.objects.new("Sun", sun_data)
sun.rotation_euler = (radians(52), 0.0, radians(38))
sun.location = (0, 0, 20)
C.objects.link(sun)

fill_data = bpy.data.lights.new("Fill", 'AREA')
fill_data.energy = 2500.0
fill_data.size = 12.0
fill_data.color = (0.75, 0.83, 1.0)
fill = bpy.data.objects.new("Fill", fill_data)
fill.location = (-12.0, 10.0, 11.0)
fill.rotation_euler = (radians(55), 0.0, radians(-130))
C.objects.link(fill)

# ----------------------------------------------------------------------------
# camera
# ----------------------------------------------------------------------------
cam_data = bpy.data.cameras.new("Camera")
cam_data.lens = 42.0
cam = bpy.data.objects.new("Camera", cam_data)
cam.location = (11.5, -13.0, 8.2)
C.objects.link(cam)
target = Vector((0.9, 0.0, 3.9))
cam.rotation_euler = (target - cam.location).to_track_quat('-Z', 'Y').to_euler()
scene.camera = cam
