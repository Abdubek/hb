import bpy, bmesh, math
from mathutils import Vector, Euler

# ----------------------------------------------------------------------------- setup
bpy.ops.wm.read_factory_settings(use_empty=True)
scene = bpy.context.scene
scene.unit_settings.system = 'METRIC'

TAU = math.tau
R_DOME = 6.2          # dome radius
Z_DOME = 7.3          # dome equator height
SLIT_W = math.radians(10.0)   # slit half-angle
AZ = math.radians(-40.0)      # slit azimuth (faces the camera)

def new_mat(name, base, rough=0.5, metal=0.0, ior=1.45,
            alpha=1.0, transmission=0.0, emit=None, emit_str=0.0, coat=0.0):
    mat = bpy.data.materials.new(name)
    mat.use_nodes = True
    b = mat.node_tree.nodes["Principled BSDF"]
    b.inputs["Base Color"].default_value = (*base, 1.0)
    b.inputs["Roughness"].default_value = rough
    b.inputs["Metallic"].default_value = metal
    b.inputs["IOR"].default_value = ior
    b.inputs["Alpha"].default_value = alpha
    b.inputs["Transmission Weight"].default_value = transmission
    b.inputs["Coat Weight"].default_value = coat
    if emit:
        b.inputs["Emission Color"].default_value = (*emit, 1.0)
        b.inputs["Emission Strength"].default_value = emit_str
    if alpha < 1.0 or transmission > 0.0:
        mat.blend_method = 'BLEND'
    return mat

M_DOME   = new_mat("DomeShell",   (0.88, 0.89, 0.90), 0.32, 0.10, coat=0.2)
M_SHUT   = new_mat("Shutter",     (0.74, 0.76, 0.78), 0.30, 0.85)
M_RAIL   = new_mat("RailSteel",   (0.22, 0.23, 0.25), 0.35, 0.90)
M_COLLAR = new_mat("Collar",      (0.30, 0.31, 0.33), 0.40, 0.80)
M_WALL   = new_mat("Concrete",    (0.72, 0.70, 0.67), 0.85)
M_PLINTH = new_mat("PlinthStone", (0.55, 0.54, 0.52), 0.90)
M_GLASS  = new_mat("Glazing",     (0.62, 0.72, 0.78), 0.05, 0.0, 1.45, 1.0, 1.0)
M_DARK   = new_mat("DarkMetal",   (0.10, 0.10, 0.11), 0.35, 0.90)
M_SCOPE  = new_mat("ScopeBody",   (0.93, 0.93, 0.94), 0.28, 0.20)
M_FLOOR  = new_mat("DeckFloor",   (0.16, 0.16, 0.17), 0.70)
M_GROUND = new_mat("Terrain",     (0.19, 0.20, 0.17), 0.95)
M_PLAZA  = new_mat("Plaza",       (0.48, 0.47, 0.45), 0.88)
M_LAMP   = new_mat("LampGlow",    (0.05, 0.05, 0.05), 0.4, 0.0,
                   emit=(1.0, 0.86, 0.62), emit_str=14.0)

def link(obj):
    scene.collection.objects.link(obj)
    return obj

def finish(obj, mat, smooth=False, split=math.radians(35.0)):
    obj.data.materials.append(mat)
    if smooth:
        for p in obj.data.polygons:
            p.use_smooth = True
        es = obj.modifiers.new("EdgeSplit", 'EDGE_SPLIT')
        es.split_angle = split
    return obj

def mesh_from_bmesh(name, bm):
    me = bpy.data.meshes.new(name)
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    bm.to_mesh(me)
    bm.free()
    return link(bpy.data.objects.new(name, me))

def cyl(name, r, h, z, mat, verts=64, caps='NGON', loc=(0.0, 0.0)):
    bpy.ops.mesh.primitive_cylinder_add(vertices=verts, radius=r, depth=h,
                                        end_fill_type=caps,
                                        location=(loc[0], loc[1], z + h * 0.5))
    o = bpy.context.object
    o.name = name
    return finish(o, mat, smooth=True)

def box(name, size, loc, mat, rot=(0.0, 0.0, 0.0)):
    bpy.ops.mesh.primitive_cube_add(size=2.0, location=loc, rotation=rot)
    o = bpy.context.object
    o.name = name
    o.scale = (size[0] * 0.5, size[1] * 0.5, size[2] * 0.5)
    return finish(o, mat)

# ----------------------------------------------------------------------------- dome shell
# Hemisphere built on a theta/phi grid; faces falling inside the slit band
# (|y| < R*sin(w), on the +X side and continuing over the zenith) are omitted.
def in_slit(theta, phi):
    y = math.sin(theta) * math.sin(phi)
    x = math.sin(theta) * math.cos(phi)
    return abs(y) < math.sin(SLIT_W) and (x > 0.0 or theta < math.radians(32.0))

def build_dome():
    n_th, n_ph = 30, 96
    th0 = math.radians(1.2)
    bm = bmesh.new()
    grid = []
    for i in range(n_th + 1):
        th = th0 + (math.pi * 0.5 - th0) * i / n_th
        row = []
        for j in range(n_ph):
            ph = TAU * j / n_ph
            row.append(bm.verts.new((R_DOME * math.sin(th) * math.cos(ph),
                                     R_DOME * math.sin(th) * math.sin(ph),
                                     R_DOME * math.cos(th))))
        grid.append(row)
    for i in range(n_th):
        th_a = th0 + (math.pi * 0.5 - th0) * i / n_th
        th_b = th0 + (math.pi * 0.5 - th0) * (i + 1) / n_th
        for j in range(n_ph):
            k = (j + 1) % n_ph
            if in_slit(0.5 * (th_a + th_b), TAU * (j + 0.5) / n_ph):
                continue
            bm.faces.new((grid[i][j], grid[i][k], grid[i + 1][k], grid[i + 1][j]))
    dome = mesh_from_bmesh("ObservatoryDome", bm)
    sol = dome.modifiers.new("Shell", 'SOLIDIFY')
    sol.thickness, sol.offset = 0.22, -1.0
    finish(dome, M_DOME, smooth=True)
    dome.location.z = Z_DOME
    dome.rotation_euler.z = AZ
    return dome

build_dome()

# ----------------------------------------------------------------------------- slit rails & shutters
# Both are swept in constant-|y| planes so they run exactly parallel to the slit.
def zone_patch(name, radius, y0, y1, a0, a1, ny, na, mat, thick=0.0):
    bm = bmesh.new()
    grid = []
    for i in range(ny + 1):
        y = y0 + (y1 - y0) * i / ny
        r = math.sqrt(max(radius * radius - y * y, 1e-6))
        row = [bm.verts.new((r * math.sin(a0 + (a1 - a0) * j / na), y,
                             r * math.cos(a0 + (a1 - a0) * j / na)))
               for j in range(na + 1)]
        grid.append(row)
    for i in range(ny):
        for j in range(na):
            bm.faces.new((grid[i][j], grid[i][j + 1],
                          grid[i + 1][j + 1], grid[i + 1][j]))
    o = mesh_from_bmesh(name, bm)
    if thick:
        s = o.modifiers.new("Thick", 'SOLIDIFY')
        s.thickness, s.offset = thick, 0.0
    finish(o, mat, smooth=True)
    o.location.z = Z_DOME
    o.rotation_euler.z = AZ
    return o

Y_EDGE = R_DOME * math.sin(SLIT_W)
A0, A1 = math.radians(-34.0), math.radians(92.0)

for s in (1.0, -1.0):
    # raised rib framing each side of the aperture
    zone_patch("SlitRail_%s" % ("P" if s > 0 else "N"), R_DOME + 0.13,
               s * (Y_EDGE - 0.06), s * (Y_EDGE + 0.16), A0, A1, 2, 72,
               M_RAIL, thick=0.16)
    # retracted shutter leaf resting alongside the opening
    zone_patch("Shutter_%s" % ("P" if s > 0 else "N"), R_DOME + 0.34,
               s * (Y_EDGE + 0.28), s * (Y_EDGE + 2.55), A0 + math.radians(3.0),
               A1 - math.radians(2.0), 6, 72, M_SHUT, thick=0.14)

# ----------------------------------------------------------------------------- circular base
cyl("Plinth",     7.05, 0.45, 0.00, M_PLINTH)
cyl("WallLower",  6.40, 2.55, 0.45, M_WALL)
cyl("Glazing",    6.26, 1.10, 3.00, M_GLASS, caps='NOTHING')
cyl("GlazingSill", 6.42, 0.14, 2.92, M_DARK)
cyl("GlazingHead", 6.42, 0.14, 4.06, M_DARK)
cyl("WallUpper",  6.40, 2.10, 4.10, M_WALL)
cyl("Cornice",    6.78, 0.42, 6.20, M_PLINTH)
cyl("Collar",     6.22, 0.70, 6.62, M_COLLAR)
cyl("Deck",       6.10, 0.12, 6.55, M_FLOOR)

for i in range(24):
    a = TAU * i / 24
    box("Mullion_%02d" % i, (0.14, 0.22, 1.10),
        (6.32 * math.cos(a), 6.32 * math.sin(a), 3.55), M_DARK, rot=(0, 0, a))

# recessed vertical reveals on the upper wall
for i in range(12):
    a = TAU * i / 12 + math.radians(15.0)
    box("Reveal_%02d" % i, (0.10, 0.30, 1.90),
        (6.40 * math.cos(a), 6.40 * math.sin(a), 5.10), M_DARK, rot=(0, 0, a))

# ----------------------------------------------------------------------------- entrance
box("EntryBlock", (5.20, 2.60, 3.40), (0.0, -6.90, 1.70), M_WALL)
box("EntryCanopy", (6.20, 3.40, 0.28), (0.0, -7.20, 3.52), M_PLINTH)
box("EntryGlass", (3.20, 0.12, 2.70), (0.0, -8.16, 1.45), M_GLASS)
box("EntryJambL", (0.30, 0.30, 2.90), (-1.72, -8.14, 1.45), M_DARK)
box("EntryJambR", (0.30, 0.30, 2.90), (1.72, -8.14, 1.45), M_DARK)
box("Step1", (6.00, 0.90, 0.20), (0.0, -8.60, 0.10), M_PLINTH)
box("Step2", (6.60, 0.90, 0.20), (0.0, -9.45, 0.00), M_PLINTH)

# ----------------------------------------------------------------------------- telescope
PIER_TOP = 6.67 + 2.30
cyl("PierBase", 1.05, 0.28, 6.67, M_FLOOR)
cyl("Pier", 0.58, 2.30, 6.67, M_FLOOR, verts=32)

alt = math.radians(56.0)
d = Vector((math.cos(alt), 0.0, math.sin(alt)))
d.rotate(Euler((0.0, 0.0, AZ)))
h = Vector((-math.sin(AZ), math.cos(AZ), 0.0))          # altitude axis
pivot = Vector((0.0, 0.0, PIER_TOP + 1.65))
rot = d.to_track_quat('Z', 'Y').to_euler()

box("MountHead", (2.90, 1.30, 0.55), (0.0, 0.0, PIER_TOP + 0.28), M_DARK,
    rot=(0.0, 0.0, AZ))
for s in (1.0, -1.0):
    p = pivot + h * (s * 1.30) - Vector((0.0, 0.0, 0.85))
    box("ForkArm_%s" % ("P" if s > 0 else "N"), (0.42, 1.10, 1.90),
        tuple(p), M_DARK, rot=(0.0, 0.0, AZ))

def oriented_cyl(name, r, depth, centre, mat, verts=48):
    bpy.ops.mesh.primitive_cylinder_add(vertices=verts, radius=r, depth=depth,
                                        location=tuple(centre), rotation=rot)
    o = bpy.context.object
    o.name = name
    return finish(o, mat, smooth=True)

oriented_cyl("Tube", 0.86, 5.60, pivot + d * 0.70, M_SCOPE)
oriented_cyl("TubeCollarA", 0.92, 0.22, pivot + d * (0.70 - 1.60), M_DARK)
oriented_cyl("TubeCollarB", 0.92, 0.22, pivot + d * (0.70 + 1.60), M_DARK)
oriented_cyl("ApertureRing", 0.90, 0.30, pivot + d * 3.42, M_DARK)
oriented_cyl("Finder", 0.16, 1.40, pivot + d * 1.90 + h * 1.02, M_DARK, verts=20)
oriented_cyl("Backplate", 0.80, 0.30, pivot + d * (-2.06), M_DARK)

# ----------------------------------------------------------------------------- site
bpy.ops.mesh.primitive_plane_add(size=240.0, location=(0.0, 0.0, 0.0))
bpy.context.object.name = "Terrain"
finish(bpy.context.object, M_GROUND)
cyl("Plaza", 19.0, 0.06, 0.0, M_PLAZA, verts=96)

for i, a in enumerate((math.radians(30.0), math.radians(150.0), math.radians(255.0))):
    x, y = 11.5 * math.cos(a), 11.5 * math.sin(a)
    cyl("BollardPost_%d" % i, 0.16, 1.10, 0.06, M_DARK, verts=16, loc=(x, y))
    cyl("BollardLamp_%d" % i, 0.20, 0.22, 1.16, M_LAMP, verts=16, loc=(x, y))

# ----------------------------------------------------------------------------- world, lights, camera
world = bpy.data.worlds.new("ObservatorySky")
scene.world = world
world.use_nodes = True
nt = world.node_tree
bg = nt.nodes["Background"]
sky = nt.nodes.new("ShaderNodeTexSky")
sky.sky_type = 'NISHITA'
sky.sun_elevation = math.radians(9.0)
sky.sun_rotation = math.radians(200.0)
sky.altitude = 2400.0
nt.links.new(sky.outputs["Color"], bg.inputs["Color"])
bg.inputs["Strength"].default_value = 1.0

sun_data = bpy.data.lights.new("Sun", 'SUN')
sun_data.energy = 3.6
sun_data.angle = math.radians(1.2)
sun_data.color = (1.0, 0.92, 0.80)
sun = link(bpy.data.objects.new("Sun", sun_data))
sun.location = (-24.0, -18.0, 26.0)
sun.rotation_euler = (math.radians(52.0), 0.0, math.radians(-52.0))

fill_data = bpy.data.lights.new("SkyFill", 'AREA')
fill_data.energy = 900.0
fill_data.size = 26.0
fill_data.color = (0.72, 0.82, 1.0)
fill = link(bpy.data.objects.new("SkyFill", fill_data))
fill.location = (22.0, 20.0, 20.0)
fill.rotation_euler = (math.radians(48.0), 0.0, math.radians(132.0))

dome_data = bpy.data.lights.new("DomeInterior", 'AREA')
dome_data.energy = 320.0
dome_data.size = 5.0
dome_data.color = (1.0, 0.80, 0.58)
interior = link(bpy.data.objects.new("DomeInterior", dome_data))
interior.location = (0.0, 0.0, 7.4)
interior.rotation_euler = (0.0, 0.0, 0.0)

cam_data = bpy.data.cameras.new("Camera")
cam_data.lens = 42.0
cam_data.clip_end = 500.0
cam_data.dof.use_dof = True
cam = link(bpy.data.objects.new("Camera", cam_data))
cam.location = (26.0, -22.0, 13.5)
target = Vector((0.0, 0.0, 7.0))
cam.rotation_euler = (target - cam.location).to_track_quat('-Z', 'Y').to_euler()
cam_data.dof.focus_distance = (target - cam.location).length
cam_data.dof.aperture_fstop = 6.0
scene.camera = cam

scene.render.engine = 'CYCLES'
scene.render.resolution_x = 1920
scene.render.resolution_y = 1080
scene.cycles.samples = 128
