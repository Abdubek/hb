"""claude-091 - A row of cinema seats on a stepped platform (Blender 4.5 LTS)."""
import bpy, math
from mathutils import Vector


def reset_scene():
    bpy.ops.wm.read_factory_settings(use_empty=True)
    scene = bpy.context.scene
    scene.render.engine = 'CYCLES'
    if hasattr(scene, "cycles"):
        scene.cycles.samples = 64
    world = bpy.data.worlds.new("World")
    scene.world = world
    world.use_nodes = True
    bg = world.node_tree.nodes["Background"]
    bg.inputs[0].default_value = (0.015, 0.015, 0.025, 1.0)
    bg.inputs[1].default_value = 0.8


def make_material(name, color, roughness=0.5, metallic=0.0,
                  emission=None, emission_strength=0.0):
    mat = bpy.data.materials.new(name)
    mat.use_nodes = True
    bsdf = mat.node_tree.nodes["Principled BSDF"]
    bsdf.inputs["Base Color"].default_value = (*color, 1.0)
    bsdf.inputs["Roughness"].default_value = roughness
    bsdf.inputs["Metallic"].default_value = metallic
    if emission is not None:
        bsdf.inputs["Emission Color"].default_value = (*emission, 1.0)
        bsdf.inputs["Emission Strength"].default_value = emission_strength
    return mat


def shade(obj, angle=30.0):
    """Smooth shading with an angle based edge split (version safe)."""
    for poly in obj.data.polygons:
        poly.use_smooth = True
    mod = obj.modifiers.new("EdgeSplit", 'EDGE_SPLIT')
    mod.split_angle = math.radians(angle)


def add_box(name, size, location, rotation=(0, 0, 0), material=None,
            bevel=0.0, segments=2):
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=location, rotation=rotation)
    obj = bpy.context.active_object
    obj.name = name
    obj.scale = size
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    if material:
        obj.data.materials.append(material)
    if bevel > 0.0:
        mod = obj.modifiers.new("Bevel", 'BEVEL')
        mod.width = bevel
        mod.segments = segments
        mod.limit_method = 'ANGLE'
        mod.angle_limit = math.radians(40)
        mod.use_clamp_overlap = True
    return obj


def add_cylinder(name, radius, depth, location, rotation=(0, 0, 0),
                 material=None, verts=32):
    bpy.ops.mesh.primitive_cylinder_add(radius=radius, depth=depth, vertices=verts,
                                        location=location, rotation=rotation)
    obj = bpy.context.active_object
    obj.name = name
    if material:
        obj.data.materials.append(material)
    shade(obj)
    return obj


def add_camera(location, target, lens=45.0):
    cam_data = bpy.data.cameras.new("Camera")
    cam_data.lens = lens
    cam = bpy.data.objects.new("Camera", cam_data)
    cam.location = location
    bpy.context.collection.objects.link(cam)
    empty = bpy.data.objects.new("CameraTarget", None)
    empty.location = target
    empty.empty_display_size = 0.2
    bpy.context.collection.objects.link(empty)
    con = cam.constraints.new('TRACK_TO')
    con.target = empty
    con.track_axis = 'TRACK_NEGATIVE_Z'
    con.up_axis = 'UP_Y'
    bpy.context.scene.camera = cam
    return cam


def add_light(name, ltype, location, energy, size=1.0, rotation=(0, 0, 0),
              color=(1.0, 1.0, 1.0), spot_size=1.0, spot_blend=0.3):
    data = bpy.data.lights.new(name, ltype)
    data.energy = energy
    data.color = color
    if ltype == 'AREA':
        data.size = size
    elif ltype == 'SPOT':
        data.spot_size = spot_size
        data.spot_blend = spot_blend
        data.shadow_soft_size = size
    else:
        data.shadow_soft_size = size
    obj = bpy.data.objects.new(name, data)
    obj.location = location
    obj.rotation_euler = rotation
    bpy.context.collection.objects.link(obj)
    return obj


# ------------------------------------------------------------------ scene
reset_scene()

carpet_mat = make_material("Carpet", (0.055, 0.045, 0.06), roughness=0.95)
riser_mat = make_material("Riser", (0.03, 0.028, 0.035), roughness=0.9)
nosing_mat = make_material("StepNosing", (0.42, 0.36, 0.20), roughness=0.35, metallic=0.9)
fabric_mat = make_material("SeatFabric", (0.30, 0.028, 0.038), roughness=0.88)
fabric_dark = make_material("SeatFabricDark", (0.20, 0.018, 0.026), roughness=0.9)
shell_mat = make_material("SeatShell", (0.045, 0.04, 0.045), roughness=0.55)
metal_mat = make_material("SeatMetal", (0.14, 0.14, 0.15), roughness=0.42, metallic=0.85)
plate_mat = make_material("NumberPlate", (0.70, 0.60, 0.32), roughness=0.3, metallic=1.0)
floor_mat = make_material("Floor", (0.035, 0.032, 0.04), roughness=0.85)
led_mat = make_material("StepLED", (0.9, 0.75, 0.45), roughness=0.4,
                        emission=(1.0, 0.72, 0.35), emission_strength=6.0)

SEATS = 8
SEAT_W = 0.55
RISER = 0.22
TREAD = 1.15
TIERS = 4
ROW_W = SEATS * SEAT_W + 1.6            # platform width, incl. side aisles
BACK_Y = 1.9                            # rear edge of the platform
TOP_Z = RISER * TIERS                   # deck the seats stand on
TOP_FRONT_Y = -0.55                     # front edge of the top tier

# --- floor of the auditorium
add_box("AuditoriumFloor", (14.0, 16.0, 0.06), (0.0, -3.0, -0.03), material=floor_mat)

# --- stepped platform: nested slabs, each lower one reaching further forward
for tier in range(TIERS):
    height = TOP_Z - tier * RISER
    front = TOP_FRONT_Y - tier * TREAD
    depth = BACK_Y - front
    add_box("Tier_%02d" % tier,
            (ROW_W, depth, height),
            (0.0, front + depth * 0.5, height * 0.5),
            material=carpet_mat if tier == 0 else riser_mat)
    # metal nosing strip along the leading edge of every tread
    add_box("Nosing_%02d" % tier,
            (ROW_W, 0.075, 0.014),
            (0.0, front + 0.037, height - 0.007),
            material=nosing_mat, bevel=0.003)
    # recessed aisle step lights on the two outer ends of each riser
    for side in (-1, 1):
        add_box("StepLED_%02d_%d" % (tier, side),
                (0.10, 0.02, 0.035),
                (side * (ROW_W * 0.5 - 0.22), front - 0.011, height - 0.10),
                material=led_mat)

# --- carpeted deck cap so the seats sit on a slightly different tone
add_box("DeckCap", (ROW_W, BACK_Y - TOP_FRONT_Y, 0.02),
        (0.0, (TOP_FRONT_Y + BACK_Y) * 0.5, TOP_Z + 0.005), material=carpet_mat)

# --- a single row of seats on the top tier
SEAT_FRONT = TOP_FRONT_Y + 0.10         # y of the front of the seat cluster
Z0 = TOP_Z + 0.01


def build_seat(index):
    x = (index - (SEATS - 1) * 0.5) * SEAT_W
    tag = "%02d" % index

    # folding seat pan, sloping down towards the back of the seat
    add_box("SeatPan_" + tag, (SEAT_W - 0.09, 0.52, 0.10),
            (x, SEAT_FRONT + 0.32, Z0 + 0.44),
            rotation=(math.radians(-7.0), 0.0, 0.0),
            material=fabric_mat, bevel=0.028, segments=3)
    # rigid shell under the pan
    add_box("PanShell_" + tag, (SEAT_W - 0.07, 0.50, 0.035),
            (x, SEAT_FRONT + 0.33, Z0 + 0.385),
            rotation=(math.radians(-7.0), 0.0, 0.0),
            material=shell_mat, bevel=0.012)

    # backrest, reclined
    lean = math.radians(-14.0)
    add_box("SeatBack_" + tag, (SEAT_W - 0.09, 0.14, 0.60),
            (x, SEAT_FRONT + 0.60, Z0 + 0.79),
            rotation=(lean, 0.0, 0.0),
            material=fabric_mat, bevel=0.035, segments=3)
    add_box("BackShell_" + tag, (SEAT_W - 0.05, 0.05, 0.64),
            (x, SEAT_FRONT + 0.695, Z0 + 0.79),
            rotation=(lean, 0.0, 0.0),
            material=shell_mat, bevel=0.02, segments=2)
    # headrest roll on top of the backrest
    add_box("Headrest_" + tag, (SEAT_W - 0.13, 0.16, 0.10),
            (x, SEAT_FRONT + 0.525, Z0 + 1.10),
            rotation=(lean, 0.0, 0.0),
            material=fabric_dark, bevel=0.045, segments=4)


def build_standard(index):
    """Armrest standard shared between neighbouring seats."""
    x = (index - SEATS * 0.5) * SEAT_W
    tag = "%02d" % index
    add_box("StandFoot_" + tag, (0.16, 0.24, 0.03),
            (x, SEAT_FRONT + 0.24, Z0 + 0.015), material=metal_mat, bevel=0.006)
    add_box("StandPost_" + tag, (0.075, 0.11, 0.52),
            (x, SEAT_FRONT + 0.24, Z0 + 0.27), material=metal_mat, bevel=0.008)
    add_box("StandBrace_" + tag, (0.06, 0.34, 0.06),
            (x, SEAT_FRONT + 0.56, Z0 + 0.44),
            rotation=(math.radians(20.0), 0.0, 0.0),
            material=metal_mat, bevel=0.008)
    add_box("Armrest_" + tag, (0.09, 0.60, 0.055),
            (x, SEAT_FRONT + 0.32, Z0 + 0.555),
            material=fabric_dark, bevel=0.024, segments=3)
    # cup holder boss at the front of every armrest
    add_cylinder("CupHolder_" + tag, 0.045, 0.05,
                 (x, SEAT_FRONT + 0.045, Z0 + 0.555), material=shell_mat, verts=24)
    add_cylinder("CupRecess_" + tag, 0.036, 0.052,
                 (x, SEAT_FRONT + 0.045, Z0 + 0.548), material=metal_mat, verts=24)


for i in range(SEATS):
    build_seat(i)
for i in range(SEATS + 1):
    build_standard(i)

# --- row letter plates on the aisle-side standards
for side in (-1, 1):
    x = side * (SEATS * 0.5) * SEAT_W
    add_box("RowPlate_%d" % side, (0.012, 0.10, 0.07),
            (x + side * 0.045, SEAT_FRONT + 0.16, Z0 + 0.42),
            material=plate_mat, bevel=0.004)

# --- lighting
key = add_light("KeyArea", 'AREA', (2.6, -4.4, 4.4), 900.0, size=3.5)
key.rotation_euler = (math.radians(52.0), 0.0, math.radians(28.0))
fill = add_light("FillArea", 'AREA', (-4.0, -3.4, 3.0), 300.0, size=4.0)
fill.rotation_euler = (math.radians(62.0), 0.0, math.radians(-45.0))
rim = add_light("RimArea", 'AREA', (0.0, 3.6, 3.2), 420.0, size=3.0,
                color=(0.55, 0.65, 1.0))
rim.rotation_euler = (math.radians(-120.0), 0.0, 0.0)
add_light("ScreenGlow", 'AREA', (0.0, -7.5, 2.2), 260.0, size=6.0,
          rotation=(math.radians(90.0), 0.0, 0.0), color=(0.6, 0.72, 1.0))

# --- camera
add_camera((3.9, -4.6, 2.55), (0.0, -0.05, 1.15), lens=42.0)
