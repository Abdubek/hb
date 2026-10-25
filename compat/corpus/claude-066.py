import bpy
from math import radians, cos, sin
from mathutils import Vector

bpy.ops.wm.read_factory_settings(use_empty=True)
scene = bpy.context.scene
try:
    scene.render.engine = 'BLENDER_EEVEE_NEXT'
except TypeError:
    pass
C = bpy.context


def mat(name, color, rough=0.5, metal=0.0):
    m = bpy.data.materials.new(name)
    m.use_nodes = True
    b = m.node_tree.nodes["Principled BSDF"]
    b.inputs["Base Color"].default_value = (*color, 1.0)
    b.inputs["Roughness"].default_value = rough
    b.inputs["Metallic"].default_value = metal
    return m


def box(name, size, loc, material=None, rot=(0, 0, 0)):
    bpy.ops.mesh.primitive_cube_add(size=1, location=loc, rotation=rot)
    ob = C.object
    ob.name = name
    ob.scale = size
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    if material:
        ob.data.materials.append(material)
    return ob


def cyl(name, r, h, loc, material=None, rot=(0, 0, 0), verts=32):
    bpy.ops.mesh.primitive_cylinder_add(vertices=verts, radius=r, depth=h,
                                        location=loc, rotation=rot)
    ob = C.object
    ob.name = name
    if material:
        ob.data.materials.append(material)
    return ob


def sphere(name, r, loc, material=None, segs=32, rings=16):
    bpy.ops.mesh.primitive_uv_sphere_add(segments=segs, ring_count=rings,
                                         radius=r, location=loc)
    ob = C.object
    ob.name = name
    if material:
        ob.data.materials.append(material)
    return ob


def smooth(ob, angle=40.0):
    for p in ob.data.polygons:
        p.use_smooth = True
    m = ob.modifiers.new("EdgeSplit", 'EDGE_SPLIT')
    m.split_angle = radians(angle)
    return ob


def bevel(ob, width=0.008, segments=3, angle=40.0):
    m = ob.modifiers.new("Bevel", 'BEVEL')
    m.width = width
    m.segments = segments
    m.limit_method = 'ANGLE'
    m.angle_limit = radians(angle)
    return ob


# ---------------------------------------------------------------- materials
M_ASPHALT = mat("Asphalt", (0.045, 0.045, 0.050), rough=0.92)
M_CONCRETE = mat("Concrete", (0.60, 0.585, 0.55), rough=0.88)
M_CURB = mat("CurbConcrete", (0.68, 0.665, 0.63), rough=0.82)
M_PAINT = mat("RoadPaint", (0.82, 0.80, 0.72), rough=0.75)
M_METER = mat("MeterGreen", (0.035, 0.115, 0.075), rough=0.42, metal=0.35)
M_STEEL = mat("Steel", (0.44, 0.45, 0.47), rough=0.35, metal=1.0)
M_CHROME = mat("Chrome", (0.72, 0.73, 0.75), rough=0.15, metal=1.0)
M_GLASS = mat("DarkGlass", (0.015, 0.02, 0.025), rough=0.12)
M_LCD = mat("LCD", (0.35, 0.62, 0.45), rough=0.30)
M_LABEL = mat("Label", (0.86, 0.86, 0.84), rough=0.65)
M_RED = mat("RedFlag", (0.55, 0.05, 0.04), rough=0.55)
M_GRASS = mat("Verge", (0.16, 0.22, 0.10), rough=0.95)

# ---------------------------------------------------------------- ground
SIDEWALK_Z = 0.155

box("Road", (14.0, 8.0, 0.02), (0.0, -3.9, -0.01), M_ASPHALT)
box("Gutter", (14.0, 0.35, 0.024), (0.0, -0.10, 0.004), M_CONCRETE)
box("Sidewalk", (14.0, 4.0, SIDEWALK_Z), (0.0, 2.05, SIDEWALK_Z * 0.5), M_CONCRETE)

curb = box("Curb", (14.0, 0.22, SIDEWALK_Z + 0.01),
           (0.0, -0.04, (SIDEWALK_Z + 0.01) * 0.5), M_CURB)
bevel(curb, width=0.02, segments=2, angle=50)

# expansion joints scored into the sidewalk
for i in range(-4, 5):
    box("Joint%d" % i, (0.012, 3.9, 0.004),
        (i * 1.35, 2.05, SIDEWALK_Z - 0.001), M_ASPHALT)

box("Verge", (14.0, 1.4, 0.14), (0.0, 4.6, 0.07), M_GRASS)

# parking bay markings
for x in (-2.6, 2.6):
    box("Stripe%.1f" % x, (0.10, 2.4, 0.006), (x, -1.45, 0.008), M_PAINT)
box("StripeLong", (5.2, 0.10, 0.006), (0.0, -2.62, 0.008), M_PAINT)


# ---------------------------------------------------------------- meter build
def build_parking_meter(name, x, y, head_yaw=0.0, expired=False):
    base_z = SIDEWALK_Z

    fl = cyl(name + "_Flange", 0.085, 0.028, (x, y, base_z + 0.014), M_STEEL, verts=28)
    bevel(fl, 0.006, 2)
    smooth(fl)
    for i in range(4):
        a = radians(45 + 90 * i)
        smooth(cyl(name + "_Bolt%d" % i, 0.010, 0.012,
                   (x + 0.062 * cos(a), y + 0.062 * sin(a), base_z + 0.032),
                   M_STEEL, verts=12))

    pole = cyl(name + "_Pole", 0.036, 0.90, (x, y, base_z + 0.028 + 0.45), M_STEEL)
    smooth(pole)
    collar = cyl(name + "_Collar", 0.048, 0.045, (x, y, base_z + 0.905), M_STEEL,
                 verts=28)
    bevel(collar, 0.006, 2)
    smooth(collar)

    head_bottom = base_z + 0.925
    hh = 0.34
    head_c = head_bottom + hh * 0.5

    head = box(name + "_Head", (0.205, 0.165, hh), (x, y, head_c), M_METER,
               rot=(0, 0, head_yaw))
    bevel(head, 0.030, 5, angle=55)
    smooth(head, 50)

    cap = sphere(name + "_Dome", 0.098, (x, y, head_bottom + hh - 0.012), M_METER)
    cap.scale = (1.0, 0.82, 0.42)
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    smooth(cap)

    # front bezel, window and readout (the face looks toward -Y, i.e. the street)
    fy = y - 0.084
    bez = box(name + "_Bezel", (0.165, 0.014, 0.185), (x, fy, head_c + 0.045), M_CHROME)
    bevel(bez, 0.006, 3)
    win = box(name + "_Window", (0.140, 0.010, 0.160), (x, fy - 0.006, head_c + 0.045),
              M_GLASS)
    bevel(win, 0.004, 2)
    box(name + "_LCD", (0.105, 0.004, 0.052), (x, fy - 0.010, head_c + 0.070),
        M_RED if expired else M_LCD)
    for i in range(4):
        box(name + "_Digit%d" % i, (0.014, 0.003, 0.030),
            (x - 0.042 + i * 0.028, fy - 0.013, head_c + 0.070), M_GLASS)
    box(name + "_Plate", (0.130, 0.006, 0.052), (x, fy - 0.004, head_c - 0.085),
        M_LABEL)

    slot = box(name + "_CoinSlot", (0.030, 0.020, 0.010),
               (x + 0.055, y - 0.070, head_bottom + hh - 0.030), M_CHROME,
               rot=(radians(-18), 0, 0))
    bevel(slot, 0.003, 2)
    box(name + "_CardSlot", (0.012, 0.030, 0.006),
        (x - 0.100, y - 0.020, head_c + 0.020), M_CHROME)

    cup = cyl(name + "_Return", 0.028, 0.018, (x, y - 0.082, head_bottom + 0.038),
              M_CHROME, rot=(radians(90), 0, 0), verts=20)
    smooth(cup)
    lock = cyl(name + "_Lock", 0.016, 0.020,
               (x + 0.075, y - 0.082, head_bottom + 0.040), M_CHROME,
               rot=(radians(90), 0, 0), verts=20)
    smooth(lock)

    box(name + "_Tag", (0.008, 0.090, 0.055), (x + 0.104, y, head_c - 0.070), M_LABEL)


build_parking_meter("Meter", 0.0, 0.42, head_yaw=radians(4), expired=False)
build_parking_meter("Meter2", 3.15, 0.42, head_yaw=radians(-6), expired=True)

smooth(cyl("Bollard", 0.055, 0.95, (-3.4, 0.55, SIDEWALK_Z + 0.475), M_STEEL))
smooth(sphere("BollardTop", 0.055, (-3.4, 0.55, SIDEWALK_Z + 0.95), M_STEEL))

# ---------------------------------------------------------------- lighting
world = bpy.data.worlds.new("World")
scene.world = world
world.use_nodes = True
world.node_tree.nodes["Background"].inputs[0].default_value = (0.30, 0.40, 0.55, 1.0)
world.node_tree.nodes["Background"].inputs[1].default_value = 1.1

sun_data = bpy.data.lights.new("Sun", 'SUN')
sun_data.energy = 4.0
sun_data.angle = radians(1.5)
sun_data.color = (1.0, 0.95, 0.86)
sun = bpy.data.objects.new("Sun", sun_data)
scene.collection.objects.link(sun)
sun.location = (-3.0, -4.0, 6.0)
sun.rotation_euler = (radians(52), 0.0, radians(-38))

fill_data = bpy.data.lights.new("Fill", 'AREA')
fill_data.energy = 120.0
fill_data.size = 3.0
fill = bpy.data.objects.new("Fill", fill_data)
scene.collection.objects.link(fill)
fill.location = (2.2, -3.2, 2.4)
fill.rotation_euler = (radians(62), 0, radians(28))

# ---------------------------------------------------------------- camera
cam_data = bpy.data.cameras.new("Camera")
cam_data.lens = 62.0
cam = bpy.data.objects.new("Camera", cam_data)
scene.collection.objects.link(cam)
cam.location = (1.05, -1.85, 1.62)
target = Vector((0.0, 0.35, 1.16))
cam.rotation_euler = (target - cam.location).to_track_quat('-Z', 'Y').to_euler()
cam_data.dof.use_dof = True
cam_data.dof.focus_distance = (target - cam.location).length
cam_data.dof.aperture_fstop = 4.0
scene.camera = cam
