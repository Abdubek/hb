"""claude-094 - A wall-mounted control panel with switches and gauges (Blender 4.5 LTS)."""
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
    bg.inputs[0].default_value = (0.03, 0.032, 0.038, 1.0)
    bg.inputs[1].default_value = 1.0


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


def make_glass(name):
    mat = bpy.data.materials.new(name)
    mat.use_nodes = True
    bsdf = mat.node_tree.nodes["Principled BSDF"]
    bsdf.inputs["Base Color"].default_value = (0.95, 0.97, 0.97, 1.0)
    bsdf.inputs["Roughness"].default_value = 0.04
    bsdf.inputs["Transmission Weight"].default_value = 1.0
    bsdf.inputs["IOR"].default_value = 1.45
    return mat


def shade(obj, angle=30.0):
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


def add_cone(name, r1, r2, depth, location, rotation=(0, 0, 0),
             material=None, verts=24):
    bpy.ops.mesh.primitive_cone_add(radius1=r1, radius2=r2, depth=depth,
                                    vertices=verts, location=location,
                                    rotation=rotation)
    obj = bpy.context.active_object
    obj.name = name
    if material:
        obj.data.materials.append(material)
    shade(obj)
    return obj


def add_sphere(name, radius, location, material=None, segments=20, rings=12):
    bpy.ops.mesh.primitive_uv_sphere_add(radius=radius, segments=segments,
                                         ring_count=rings, location=location)
    obj = bpy.context.active_object
    obj.name = name
    if material:
        obj.data.materials.append(material)
    shade(obj, angle=45.0)
    return obj


def add_camera(location, target, lens=50.0):
    cam_data = bpy.data.cameras.new("Camera")
    cam_data.lens = lens
    cam = bpy.data.objects.new("Camera", cam_data)
    cam.location = location
    bpy.context.collection.objects.link(cam)
    empty = bpy.data.objects.new("CameraTarget", None)
    empty.location = target
    bpy.context.collection.objects.link(empty)
    con = cam.constraints.new('TRACK_TO')
    con.target = empty
    con.track_axis = 'TRACK_NEGATIVE_Z'
    con.up_axis = 'UP_Y'
    bpy.context.scene.camera = cam
    return cam


def add_light(name, ltype, location, energy, size=1.0, rotation=(0, 0, 0),
              color=(1.0, 1.0, 1.0)):
    data = bpy.data.lights.new(name, ltype)
    data.energy = energy
    data.color = color
    if ltype == 'AREA':
        data.size = size
    else:
        data.shadow_soft_size = size
    obj = bpy.data.objects.new(name, data)
    obj.location = location
    obj.rotation_euler = rotation
    bpy.context.collection.objects.link(obj)
    return obj


# ------------------------------------------------------------------ scene
reset_scene()

wall_mat = make_material("Wall", (0.30, 0.30, 0.29), roughness=0.92)
floor_mat = make_material("Floor", (0.12, 0.12, 0.13), roughness=0.75)
case_mat = make_material("PanelCase", (0.13, 0.20, 0.22), roughness=0.42, metallic=0.5)
face_mat = make_material("FacePlate", (0.55, 0.57, 0.58), roughness=0.28, metallic=0.9)
dark_mat = make_material("DarkPlastic", (0.035, 0.036, 0.040), roughness=0.45)
steel_mat = make_material("Steel", (0.66, 0.67, 0.69), roughness=0.22, metallic=1.0)
dial_mat = make_material("DialFace", (0.90, 0.89, 0.85), roughness=0.65)
tick_mat = make_material("DialTick", (0.06, 0.06, 0.07), roughness=0.6)
needle_mat = make_material("Needle", (0.62, 0.07, 0.05), roughness=0.4)
glass_mat = make_glass("GaugeGlass")
label_mat = make_material("LabelPlate", (0.06, 0.07, 0.09), roughness=0.5)
warn_mat = make_material("WarningPlate", (0.72, 0.55, 0.05), roughness=0.6)
copper_mat = make_material("Copper", (0.55, 0.28, 0.14), roughness=0.35, metallic=1.0)
led_red = make_material("LedRed", (0.5, 0.05, 0.04), roughness=0.2,
                        emission=(1.0, 0.10, 0.06), emission_strength=12.0)
led_grn = make_material("LedGreen", (0.06, 0.45, 0.10), roughness=0.2,
                        emission=(0.15, 1.0, 0.25), emission_strength=12.0)
led_amb = make_material("LedAmber", (0.55, 0.32, 0.03), roughness=0.2,
                        emission=(1.0, 0.62, 0.10), emission_strength=12.0)
led_off = make_material("LedOff", (0.10, 0.09, 0.08), roughness=0.3)

# --- room shell (the panel faces -Y, towards the camera)
add_box("Wall", (6.0, 0.20, 3.4), (0.0, 0.20, 1.70), material=wall_mat)
add_box("Floor", (6.0, 6.0, 0.10), (0.0, -2.6, -0.05), material=floor_mat)

# --- panel housing bolted to the wall
CX, CZ = 0.0, 1.50                     # centre of the panel
W, H = 1.30, 0.86                      # faceplate size
FRONT = -0.10                          # y of the exposed faceplate surface
add_box("PanelHousing", (W + 0.08, 0.19, H + 0.08), (CX, 0.005, CZ),
        material=case_mat, bevel=0.010, segments=3)
add_box("FacePlate", (W, 0.024, H), (CX, FRONT + 0.012, CZ),
        material=face_mat, bevel=0.004)
add_box("FaceGroove", (W - 0.05, 0.006, H - 0.05), (CX, FRONT + 0.001, CZ),
        material=case_mat)

# corner fixing screws
for sx in (-1, 1):
    for sz in (-1, 1):
        add_cylinder("Screw_%d_%d" % (sx, sz), 0.010, 0.014,
                     (CX + sx * (W * 0.5 - 0.028), FRONT + 0.006,
                      CZ + sz * (H * 0.5 - 0.028)),
                     rotation=(math.radians(90.0), 0.0, 0.0),
                     material=steel_mat, verts=16)

# hinge knuckles and a latch handle on the enclosure door
for sz in (-1, 1):
    add_cylinder("Hinge_%d" % sz, 0.016, 0.06,
                 (CX + W * 0.5 + 0.045, -0.03, CZ + sz * 0.28),
                 material=case_mat, verts=20)
add_cylinder("LatchBoss", 0.026, 0.05, (CX - W * 0.5 - 0.045, -0.045, CZ),
             rotation=(math.radians(90.0), 0.0, 0.0), material=steel_mat, verts=24)
add_box("LatchHandle", (0.022, 0.10, 0.026), (CX - W * 0.5 - 0.045, -0.09, CZ),
        material=steel_mat, bevel=0.006)


# ------------------------------------------------------------------ gauges
def build_gauge(tag, x, z, radius, value, ticks=11):
    """Analogue gauge; value in 0..1 drives the needle over a 270 deg sweep."""
    add_cylinder("GaugeBezel_" + tag, radius, 0.055, (x, FRONT - 0.010, z),
                 rotation=(math.radians(90.0), 0.0, 0.0),
                 material=steel_mat, verts=48)
    add_cylinder("GaugeWell_" + tag, radius * 0.90, 0.050, (x, FRONT - 0.014, z),
                 rotation=(math.radians(90.0), 0.0, 0.0),
                 material=dark_mat, verts=48)
    add_cylinder("GaugeDial_" + tag, radius * 0.88, 0.005, (x, FRONT - 0.014, z),
                 rotation=(math.radians(90.0), 0.0, 0.0),
                 material=dial_mat, verts=48)

    sweep = math.radians(270.0)
    for i in range(ticks):
        frac = i / float(ticks - 1)
        ang = -sweep * 0.5 + frac * sweep
        major = (i % 2 == 0)
        length = radius * (0.20 if major else 0.12)
        pos = (x + math.sin(ang) * (radius * 0.72),
               FRONT - 0.020,
               z + math.cos(ang) * (radius * 0.72))
        add_box("GaugeTick_%s_%d" % (tag, i),
                (0.006 if major else 0.004, 0.004, length),
                pos, rotation=(0.0, ang, 0.0), material=tick_mat)

    # needle and hub
    ang = -sweep * 0.5 + value * sweep
    length = radius * 0.80
    add_box("GaugeNeedle_" + tag, (0.008, 0.004, length),
            (x + math.sin(ang) * length * 0.42,
             FRONT - 0.024,
             z + math.cos(ang) * length * 0.42),
            rotation=(0.0, ang, 0.0), material=needle_mat)
    add_cylinder("GaugeHub_" + tag, radius * 0.10, 0.016, (x, FRONT - 0.026, z),
                 rotation=(math.radians(90.0), 0.0, 0.0),
                 material=dark_mat, verts=20)
    # red danger marker near the top of the scale
    add_box("GaugeRedline_" + tag, (0.010, 0.004, radius * 0.16),
            (x + math.sin(sweep * 0.42) * (radius * 0.72), FRONT - 0.020,
             z + math.cos(sweep * 0.42) * (radius * 0.72)),
            rotation=(0.0, sweep * 0.42, 0.0), material=needle_mat)
    # cover glass
    add_cylinder("GaugeGlass_" + tag, radius * 0.90, 0.004, (x, FRONT - 0.034, z),
                 rotation=(math.radians(90.0), 0.0, 0.0),
                 material=glass_mat, verts=48)
    # legend plate below the gauge
    add_box("GaugeLabel_" + tag, (radius * 1.5, 0.004, 0.042),
            (x, FRONT - 0.002, z - radius - 0.045), material=label_mat, bevel=0.003)


gauge_top = CZ + 0.20
build_gauge("A", CX - 0.42, gauge_top, 0.135, 0.30)
build_gauge("B", CX - 0.06, gauge_top, 0.135, 0.62)
build_gauge("C", CX + 0.30, gauge_top, 0.100, 0.86, ticks=9)

# small vertical bargraph meter on the right
add_box("BarMeterFrame", (0.10, 0.020, 0.30), (CX + 0.54, FRONT - 0.004, gauge_top),
        material=dark_mat, bevel=0.005)
for i in range(9):
    lit = i < 5
    seg_mat = led_grn if (lit and i < 3) else (led_amb if lit else led_off)
    add_box("BarSeg_%d" % i, (0.070, 0.010, 0.020),
            (CX + 0.54, FRONT - 0.016, gauge_top - 0.125 + i * 0.031),
            material=seg_mat)


# ------------------------------------------------------------------ switches
def build_toggle(tag, x, z, up=True):
    add_cylinder("SwBase_" + tag, 0.019, 0.020, (x, FRONT - 0.006, z),
                 rotation=(math.radians(90.0), 0.0, 0.0),
                 material=steel_mat, verts=24)
    add_cylinder("SwNut_" + tag, 0.014, 0.030, (x, FRONT - 0.014, z),
                 rotation=(math.radians(90.0), 0.0, 0.0),
                 material=steel_mat, verts=6)
    tilt = math.radians(66.0 if up else 114.0)
    direction = Vector((0.0, -math.sin(tilt), math.cos(tilt)))
    origin = Vector((x, FRONT - 0.018, z))
    lever_len = 0.048
    add_cone("SwLever_" + tag, 0.0075, 0.005, lever_len,
             origin + direction * (lever_len * 0.5),
             rotation=(tilt, 0.0, 0.0), material=dark_mat, verts=16)
    add_sphere("SwTip_" + tag, 0.010, origin + direction * lever_len,
               material=dark_mat, segments=18, rings=10)
    add_box("SwLabel_" + tag, (0.058, 0.004, 0.020), (x, FRONT - 0.002, z - 0.048),
            material=label_mat, bevel=0.002)


switch_z = CZ - 0.16
for i in range(6):
    build_toggle("%02d" % i, CX - 0.50 + i * 0.115, switch_z, up=(i in (0, 2, 3, 5)))


# --- rotary knobs
def build_knob(tag, x, z, angle_deg, radius=0.048):
    add_cylinder("KnobCollar_" + tag, radius * 1.15, 0.010, (x, FRONT - 0.004, z),
                 rotation=(math.radians(90.0), 0.0, 0.0),
                 material=steel_mat, verts=36)
    add_cone("KnobBody_" + tag, radius, radius * 0.82, 0.040,
             (x, FRONT - 0.026, z), rotation=(math.radians(90.0), 0.0, 0.0),
             material=dark_mat, verts=32)
    ang = math.radians(angle_deg)
    add_box("KnobPointer_" + tag, (0.008, 0.006, radius * 0.9),
            (x + math.sin(ang) * radius * 0.42, FRONT - 0.047,
             z + math.cos(ang) * radius * 0.42),
            rotation=(0.0, ang, 0.0), material=steel_mat)
    for i in range(9):
        a = math.radians(-120.0 + i * 30.0)
        add_box("KnobTick_%s_%d" % (tag, i), (0.005, 0.004, 0.016),
                (x + math.sin(a) * radius * 1.35, FRONT - 0.004,
                 z + math.cos(a) * radius * 1.35),
                rotation=(0.0, a, 0.0), material=tick_mat)


build_knob("A", CX + 0.10, switch_z, -40.0)
build_knob("B", CX + 0.30, switch_z, 75.0)

# --- indicator lamps in a row
lamp_z = CZ - 0.32
for i, lamp_mat in enumerate((led_grn, led_amb, led_red, led_off, led_grn)):
    x = CX - 0.50 + i * 0.085
    add_cylinder("LampBezel_%d" % i, 0.020, 0.016, (x, FRONT - 0.004, lamp_z),
                 rotation=(math.radians(90.0), 0.0, 0.0),
                 material=steel_mat, verts=24)
    add_sphere("LampDome_%d" % i, 0.0145, (x, FRONT - 0.014, lamp_z),
               material=lamp_mat, segments=20, rings=12)

# --- illuminated push buttons and an emergency stop
for i in range(2):
    x = CX + 0.10 + i * 0.20
    add_box("ButtonWell_%d" % i, (0.062, 0.008, 0.062), (x, FRONT - 0.002, lamp_z),
            material=dark_mat, bevel=0.004)
    add_cylinder("Button_%d" % i, 0.024, 0.020, (x, FRONT - 0.012, lamp_z),
                 rotation=(math.radians(90.0), 0.0, 0.0),
                 material=led_amb if i else led_grn, verts=28)

add_cylinder("EStopBase", 0.055, 0.020, (CX + 0.54, FRONT - 0.008, lamp_z),
             rotation=(math.radians(90.0), 0.0, 0.0), material=warn_mat, verts=32)
add_cone("EStopHead", 0.048, 0.040, 0.036, (CX + 0.54, FRONT - 0.032, lamp_z),
         rotation=(math.radians(90.0), 0.0, 0.0), material=led_red, verts=32)

# --- warning plate and nameplate on the faceplate
add_box("NamePlate", (0.34, 0.005, 0.048), (CX - 0.44, FRONT - 0.002, CZ + 0.385),
        material=label_mat, bevel=0.003)
add_box("WarningPlate", (0.20, 0.005, 0.052), (CX + 0.42, FRONT - 0.002, CZ - 0.385),
        material=warn_mat, bevel=0.003)

# --- conduit runs entering the housing from below
for sx in (-1, 1):
    x = CX + sx * 0.42
    add_cylinder("Conduit_%d" % sx, 0.026, 1.05, (x, -0.045, 0.53),
                 material=steel_mat, verts=24)
    add_cylinder("ConduitGland_%d" % sx, 0.036, 0.06, (x, -0.045, 1.05),
                 material=copper_mat, verts=24)
    add_cylinder("ConduitFloorBoss_%d" % sx, 0.042, 0.05, (x, -0.045, 0.025),
                 material=steel_mat, verts=24)
    for k in range(3):
        add_cylinder("ConduitClip_%d_%d" % (sx, k), 0.034, 0.020,
                     (x, -0.045, 0.20 + k * 0.30), material=case_mat, verts=20)

# --- lighting
key = add_light("Key", 'AREA', (1.5, -2.1, 2.7), 420.0, size=1.6)
key.rotation_euler = (math.radians(52.0), 0.0, math.radians(35.0))
fill = add_light("Fill", 'AREA', (-1.8, -1.8, 1.5), 140.0, size=2.0)
fill.rotation_euler = (math.radians(80.0), 0.0, math.radians(-45.0))
top = add_light("TopStrip", 'AREA', (0.0, -0.55, 2.55), 200.0, size=2.4,
                color=(0.95, 0.97, 1.0))
top.rotation_euler = (math.radians(28.0), 0.0, 0.0)

# --- camera
add_camera((1.05, -1.95, 1.72), (0.0, -0.05, 1.46), lens=55.0)
