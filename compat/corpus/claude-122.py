import bpy, bmesh, math
from mathutils import Vector, Matrix

# ----------------------------------------------------------------------------
# Modular space-station corridor: swept hull shell, repeating structural ribs,
# raised floor panels with a central grating, ceiling pipe runs and end bulkheads.
# ----------------------------------------------------------------------------

MODULES   = 8
MODULE_L  = 2.4
LENGTH    = MODULES * MODULE_L
X0        = -LENGTH * 0.5
X1        =  LENGTH * 0.5

# Corridor cross-section, given as an open polyline in the YZ plane, running
# from the left ceiling edge, down the left wall, across the floor and back up.
PROFILE = [
    (-1.00, 2.60), (-1.35, 2.35), (-1.50, 2.00),
    (-1.50, 0.35), (-1.35, 0.10), (-1.10, 0.00),
    ( 1.10, 0.00), ( 1.35, 0.10), ( 1.50, 0.35),
    ( 1.50, 2.00), ( 1.35, 2.35), ( 1.00, 2.60),
]


# --------------------------------------------------------------------- helpers
def reset_scene():
    bpy.ops.wm.read_factory_settings(use_empty=True)
    scene = bpy.context.scene
    scene.unit_settings.system = 'METRIC'
    world = bpy.data.worlds.new("Station_World")
    world.use_nodes = True
    bg = world.node_tree.nodes["Background"]
    bg.inputs["Color"].default_value = (0.012, 0.016, 0.024, 1.0)
    bg.inputs["Strength"].default_value = 1.0
    scene.world = world


def make_material(name, color, metallic=0.0, roughness=0.5,
                  emission=None, emission_strength=0.0):
    mat = bpy.data.materials.new(name)
    mat.use_nodes = True
    bsdf = mat.node_tree.nodes["Principled BSDF"]
    bsdf.inputs["Base Color"].default_value = (*color, 1.0)
    bsdf.inputs["Metallic"].default_value = metallic
    bsdf.inputs["Roughness"].default_value = roughness
    if emission is not None:
        bsdf.inputs["Emission Color"].default_value = (*emission, 1.0)
        bsdf.inputs["Emission Strength"].default_value = emission_strength
    return mat


def new_object(name, bm, material=None):
    """Consume a bmesh into a fresh object linked to the scene collection."""
    me = bpy.data.meshes.new(name)
    bm.normal_update()
    bm.to_mesh(me)
    bm.free()
    obj = bpy.data.objects.new(name, me)
    if material is not None:
        me.materials.append(material)
    bpy.context.scene.collection.objects.link(obj)
    return obj


def add_box(bm, center, size):
    mat = (Matrix.Translation(Vector(center)) @
           Matrix.Diagonal(Vector(size)).to_4x4())
    bmesh.ops.create_cube(bm, size=1.0, matrix=mat)


def add_tube(bm, center, radius, length, segments=20, axis='X'):
    """Capped cylinder; default axis runs along the corridor (+X)."""
    rot = {'X': Matrix.Rotation(math.radians(90.0), 4, 'Y'),
           'Y': Matrix.Rotation(math.radians(90.0), 4, 'X'),
           'Z': Matrix.Identity(4)}[axis]
    mat = Matrix.Translation(Vector(center)) @ rot
    bmesh.ops.create_cone(bm, cap_ends=True, cap_tris=False,
                          segments=segments, radius1=radius, radius2=radius,
                          depth=length, matrix=mat)


def sweep_profile(bm, profile, xs):
    """Sweep an open YZ polyline along a list of X stations, quad by quad."""
    rings = []
    for x in xs:
        rings.append([bm.verts.new((x, y, z)) for (y, z) in profile])
    bm.verts.ensure_lookup_table()
    for i in range(len(rings) - 1):
        a, b = rings[i], rings[i + 1]
        for j in range(len(profile) - 1):
            bm.faces.new((a[j], a[j + 1], b[j + 1], b[j]))
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces[:])


def smooth_sides(obj):
    """Smooth cylinder walls, keep n-gon caps flat."""
    for poly in obj.data.polygons:
        poly.use_smooth = len(poly.vertices) == 4


def add_solidify(obj, thickness, offset=0.0):
    m = obj.modifiers.new("Solidify", 'SOLIDIFY')
    m.thickness = thickness
    m.offset = offset
    return m


def add_bevel(obj, width=0.008, segments=2, angle=40.0):
    m = obj.modifiers.new("Bevel", 'BEVEL')
    m.width = width
    m.segments = segments
    m.limit_method = 'ANGLE'
    m.angle_limit = math.radians(angle)
    return m


def module_center(i):
    return X0 + (i + 0.5) * MODULE_L


# ------------------------------------------------------------------ materials
reset_scene()

MAT_HULL    = make_material("Hull_Plating",   (0.34, 0.36, 0.40), 0.85, 0.42)
MAT_RIB     = make_material("Rib_Structure",  (0.17, 0.19, 0.23), 0.90, 0.33)
MAT_PANEL   = make_material("Wall_Panel",     (0.52, 0.54, 0.57), 0.70, 0.38)
MAT_FLOOR   = make_material("Floor_Plate",    (0.28, 0.30, 0.33), 0.80, 0.45)
MAT_GRATE   = make_material("Floor_Grating",  (0.09, 0.10, 0.11), 0.85, 0.55)
MAT_PIPE    = make_material("Pipe_Steel",     (0.60, 0.62, 0.66), 1.00, 0.28)
MAT_CONDUIT = make_material("Conduit_Dark",   (0.13, 0.14, 0.17), 0.60, 0.50)
MAT_ACCENT  = make_material("Hazard_Accent",  (0.78, 0.52, 0.06), 0.35, 0.40)
MAT_DOOR    = make_material("Bulkhead_Door",  (0.42, 0.45, 0.50), 0.90, 0.30)
MAT_LIGHT   = make_material("Light_Strip",    (0.85, 0.92, 1.00), 0.0, 0.20,
                            emission=(0.72, 0.84, 1.00), emission_strength=9.0)
MAT_SIGNAL  = make_material("Signal_Lamp",    (1.00, 0.55, 0.20), 0.0, 0.30,
                            emission=(1.00, 0.45, 0.12), emission_strength=14.0)


# ------------------------------------------------------------------ hull shell
bm = bmesh.new()
station_xs = [X0 + i * 0.6 for i in range(int(LENGTH / 0.6) + 1)]
sweep_profile(bm, PROFILE, station_xs)
shell = new_object("Corridor_Shell", bm, MAT_HULL)
add_solidify(shell, 0.12, offset=0.0)


# ---------------------------------------------------------------------- ribs
def scaled_profile(points, factor, center=(0.0, 1.30)):
    cy, cz = center
    return [(cy + (y - cy) * factor, cz + (z - cz) * factor) for (y, z) in points]


bm = bmesh.new()
rib_profile = scaled_profile(PROFILE, 0.965)
left_arc, right_arc = rib_profile[:6], rib_profile[6:]
for i in range(1, MODULES):
    x = X0 + i * MODULE_L
    xs = [x - 0.09, x, x + 0.09]
    sweep_profile(bm, left_arc, xs)
    sweep_profile(bm, right_arc, xs)
ribs = new_object("Structural_Ribs", bm, MAT_RIB)
add_solidify(ribs, 0.16, offset=0.0)
add_bevel(ribs, width=0.012)


# -------------------------------------------------------------- floor panels
bm = bmesh.new()
gap = 0.03
panel_y = [(-1.16, -0.42), (0.42, 1.16)]
for i in range(MODULES):
    xc = module_center(i)
    for k in (-1, 1):
        px = xc + k * MODULE_L * 0.25
        for (ya, yb) in panel_y:
            add_box(bm,
                    (px, (ya + yb) * 0.5, 0.025),
                    (MODULE_L * 0.5 - gap, (yb - ya) - gap, 0.05))
floor = new_object("Floor_Panels", bm, MAT_FLOOR)
add_bevel(floor, width=0.006)

# central grating strip: rails plus closely spaced cross slats
bm = bmesh.new()
for k in (-1, 1):
    add_box(bm, (0.0, k * 0.375, 0.022), (LENGTH - 0.1, 0.05, 0.044))
slat_step = 0.12
n_slats = int(LENGTH / slat_step)
for s in range(n_slats):
    x = X0 + 0.06 + s * slat_step
    add_box(bm, (x, 0.0, 0.034), (0.05, 0.72, 0.020))
add_box(bm, (0.0, 0.0, 0.008), (LENGTH - 0.1, 0.76, 0.016))
grate = new_object("Floor_Grating", bm, MAT_GRATE)


# ------------------------------------------------------- wall panels & rails
bm = bmesh.new()
for i in range(MODULES):
    xc = module_center(i)
    for k in (-1, 1):
        # two recessed wall plates per module side
        add_box(bm, (xc, k * 1.425, 1.42), (MODULE_L - 0.32, 0.035, 0.86))
        add_box(bm, (xc, k * 1.425, 0.52), (MODULE_L - 0.32, 0.035, 0.62))
        # kick plate along the base of each wall
        add_box(bm, (xc, k * 1.408, 0.16), (MODULE_L - 0.12, 0.05, 0.22))
wall_panels = new_object("Wall_Panels", bm, MAT_PANEL)
add_bevel(wall_panels, width=0.01)

# handrails with bracket stubs at every rib station
bm = bmesh.new()
for k in (-1, 1):
    add_tube(bm, (0.0, k * 1.33, 1.05), 0.035, LENGTH - 0.4, segments=14)
    for i in range(MODULES + 1):
        x = X0 + i * MODULE_L
        if x <= X0 + 0.2 or x >= X1 - 0.2:
            continue
        add_box(bm, (x, k * 1.40, 1.05), (0.07, 0.13, 0.07))
rails = new_object("Handrails", bm, MAT_PIPE)
smooth_sides(rails)


# ------------------------------------------------------------- ceiling pipes
PIPE_RUNS = [(-0.78, 2.40, 0.095), (-0.55, 2.50, 0.060),
             ( 0.60, 2.44, 0.110), ( 0.86, 2.36, 0.055),
             (-0.30, 2.53, 0.045)]
bm = bmesh.new()
for (y, z, r) in PIPE_RUNS:
    add_tube(bm, (0.0, y, z), r, LENGTH - 0.16, segments=20)
    for i in range(MODULES + 1):
        x = X0 + i * MODULE_L
        add_tube(bm, (x, y, z), r + 0.028, 0.13, segments=20)
# hanger straps dropping each pipe from the ceiling shell
for (y, z, r) in PIPE_RUNS:
    for i in range(MODULES):
        x = module_center(i)
        add_box(bm, (x, y, z + r + 0.07), (0.05, r * 2.2, 0.16))
pipes = new_object("Ceiling_Pipes", bm, MAT_PIPE)
smooth_sides(pipes)

# boxed cable conduit tray running the ceiling centre line
bm = bmesh.new()
add_box(bm, (0.0, 0.15, 2.50), (LENGTH - 0.16, 0.30, 0.14))
for i in range(MODULES + 1):
    x = X0 + i * MODULE_L
    add_box(bm, (x, 0.15, 2.50), (0.10, 0.34, 0.18))
# wall-run conduits either side
for k in (-1, 1):
    add_tube(bm, (0.0, k * 1.40, 1.95), 0.05, LENGTH - 0.2, segments=12)
    add_tube(bm, (0.0, k * 1.40, 1.82), 0.035, LENGTH - 0.2, segments=12)
conduit = new_object("Conduits", bm, MAT_CONDUIT)
smooth_sides(conduit)


# -------------------------------------------------------------- light strips
bm = bmesh.new()
for i in range(MODULES):
    xc = module_center(i)
    for k in (-1, 1):
        add_box(bm, (xc, k * 1.16, 2.44), (MODULE_L - 0.28, 0.16, 0.05))
strips = new_object("Light_Strips", bm, MAT_LIGHT)

# small orange signal lamps beside each rib
bm = bmesh.new()
for i in range(1, MODULES):
    x = X0 + i * MODULE_L
    for k in (-1, 1):
        add_box(bm, (x, k * 1.40, 2.02), (0.10, 0.05, 0.10))
signals = new_object("Signal_Lamps", bm, MAT_SIGNAL)


# ----------------------------------------------------------------- bulkheads
DOOR_W, DOOR_H = 1.20, 2.10


def build_bulkhead(x, flip):
    bm = bmesh.new()
    t = 0.30
    # wall built from four slabs framing the doorway (no booleans needed)
    add_box(bm, (x, 0.0, DOOR_H + (2.60 - DOOR_H) * 0.5),
            (t, 3.0, 2.60 - DOOR_H))
    for k in (-1, 1):
        span = 1.5 - DOOR_W * 0.5
        add_box(bm, (x, k * (DOOR_W * 0.5 + span * 0.5), DOOR_H * 0.5),
                (t, span, DOOR_H))
    # raised frame ring around the opening
    add_box(bm, (x - flip * (t * 0.5 + 0.04), 0.0, DOOR_H + 0.09),
            (0.08, DOOR_W + 0.34, 0.18))
    for k in (-1, 1):
        add_box(bm, (x - flip * (t * 0.5 + 0.04),
                     k * (DOOR_W * 0.5 + 0.09), DOOR_H * 0.5),
                (0.08, 0.18, DOOR_H + 0.18))
    obj = new_object("Bulkhead_%s" % ("Fore" if flip > 0 else "Aft"),
                     bm, MAT_RIB)
    add_bevel(obj, width=0.012)

    # twin sliding door leaves, parted slightly
    bm = bmesh.new()
    for k in (-1, 1):
        add_box(bm, (x, k * (DOOR_W * 0.25 + 0.03), DOOR_H * 0.5 - 0.02),
                (0.10, DOOR_W * 0.5 - 0.06, DOOR_H - 0.04))
    leaves = new_object("Door_Leaves_%d" % (1 if flip > 0 else 0), bm, MAT_DOOR)
    add_bevel(leaves, width=0.01)

    # hazard stripe on the deck in front of the bulkhead
    bm = bmesh.new()
    add_box(bm, (x - flip * 0.42, 0.0, 0.055), (0.16, 2.6, 0.02))
    new_object("Hazard_Stripe_%d" % (1 if flip > 0 else 0), bm, MAT_ACCENT)


build_bulkhead(X0 - 0.15, flip=-1)
build_bulkhead(X1 + 0.15, flip=1)


# -------------------------------------------------------------------- lights
def add_area_light(name, location, size, size_y, energy, color=(0.8, 0.88, 1.0)):
    data = bpy.data.lights.new(name, 'AREA')
    data.shape = 'RECTANGLE'
    data.size = size
    data.size_y = size_y
    data.energy = energy
    data.color = color
    obj = bpy.data.objects.new(name, data)
    obj.location = location
    bpy.context.scene.collection.objects.link(obj)
    return obj


for i in range(0, MODULES, 2):
    xc = module_center(i)
    add_area_light("Ceiling_Light_%d" % i, (xc, 0.0, 2.42), 1.6, 1.2, 90.0)

warm = add_area_light("End_Glow", (X1 - 0.6, 0.0, 1.30), 1.2, 2.0, 120.0,
                      color=(1.0, 0.62, 0.35))
warm.rotation_euler = (0.0, math.radians(-90.0), 0.0)

fill = bpy.data.lights.new("Fill", 'POINT')
fill.energy = 40.0
fill.shadow_soft_size = 0.8
fill.color = (0.55, 0.65, 0.9)
fill_obj = bpy.data.objects.new("Fill", fill)
fill_obj.location = (X0 + 1.5, 0.0, 1.7)
bpy.context.scene.collection.objects.link(fill_obj)


# -------------------------------------------------------------------- camera
cam_data = bpy.data.cameras.new("Corridor_Camera")
cam_data.lens = 26.0
cam_data.clip_start = 0.05
cam_data.clip_end = 200.0
cam_data.dof.use_dof = True
cam_data.dof.focus_distance = 9.0
cam_data.dof.aperture_fstop = 3.2
cam = bpy.data.objects.new("Corridor_Camera", cam_data)
cam.location = (X0 + 0.9, 0.10, 1.62)
# default camera looks down -Z; rotate to sight straight down the corridor (+X)
cam.rotation_euler = (math.radians(90.0), 0.0, math.radians(-90.0))
bpy.context.scene.collection.objects.link(cam)
bpy.context.scene.camera = cam
