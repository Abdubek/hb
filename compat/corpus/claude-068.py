import bpy
from math import radians
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


def cyl(name, r, h, loc, material=None, rot=(0, 0, 0), verts=24):
    bpy.ops.mesh.primitive_cylinder_add(vertices=verts, radius=r, depth=h,
                                        location=loc, rotation=rot)
    ob = C.object
    ob.name = name
    if material:
        ob.data.materials.append(material)
    return ob


def torus(name, R, r, loc, material=None, rot=(0, 0, 0)):
    bpy.ops.mesh.primitive_torus_add(major_radius=R, minor_radius=r,
                                     major_segments=32, minor_segments=12,
                                     location=loc, rotation=rot)
    ob = C.object
    ob.name = name
    if material:
        ob.data.materials.append(material)
    for p in ob.data.polygons:
        p.use_smooth = True
    return ob


def smooth(ob, angle=40.0):
    for p in ob.data.polygons:
        p.use_smooth = True
    m = ob.modifiers.new("EdgeSplit", 'EDGE_SPLIT')
    m.split_angle = radians(angle)
    return ob


def bevel(ob, width=0.006, segments=3, angle=40.0):
    m = ob.modifiers.new("Bevel", 'BEVEL')
    m.width = width
    m.segments = segments
    m.limit_method = 'ANGLE'
    m.angle_limit = radians(angle)
    return ob


# ---------------------------------------------------------------- materials
M_FLOOR = mat("Floor", (0.30, 0.28, 0.26), rough=0.42)
M_SHELL = mat("Shell", (0.075, 0.115, 0.22), rough=0.32)
M_SHELL2 = mat("ShellBack", (0.060, 0.095, 0.185), rough=0.34)
M_TRIM = mat("Trim", (0.045, 0.045, 0.050), rough=0.58)
M_RUBBER = mat("Rubber", (0.028, 0.028, 0.030), rough=0.86)
M_CHROME = mat("Chrome", (0.76, 0.77, 0.79), rough=0.18, metal=1.0)
M_ZIP = mat("Zipper", (0.62, 0.55, 0.32), rough=0.30, metal=0.95)
M_TAG = mat("Tag", (0.85, 0.83, 0.76), rough=0.72)
M_ACCENT = mat("Accent", (0.62, 0.42, 0.10), rough=0.45, metal=0.3)

box("Floor", (10.0, 10.0, 0.08), (0, 0, -0.04), M_FLOOR)

# ---------------------------------------------------------------- dimensions
W, D, H = 0.44, 0.26, 0.64          # shell width (x), depth (y), height (z)
WHEEL_R = 0.036
BASE_Z = WHEEL_R * 2.0 - 0.010      # shell bottom sits just above the wheels
CZ = BASE_Z + H * 0.5
SPLIT = 0.020                       # front/back shell join plane offset in y

# ---------------------------------------------------------------- shells
back_d = D * 0.5 + SPLIT
front_d = D * 0.5 - SPLIT

back = box("ShellBack", (W, back_d, H), (0, -(D * 0.5) + back_d * 0.5, CZ), M_SHELL2)
bevel(back, 0.048, 6, angle=55)
smooth(back, 50)

front = box("ShellFront", (W, front_d, H), (0, (D * 0.5) - front_d * 0.5, CZ), M_SHELL)
bevel(front, 0.044, 6, angle=55)
smooth(front, 50)

band = box("ZipBand", (W + 0.008, 0.016, H + 0.008), (0, SPLIT, CZ), M_ZIP)
bevel(band, 0.006, 3)
smooth(band, 50)
for sx in (-1, 1):
    p = box("ZipPull%d" % sx, (0.018, 0.028, 0.030),
            (sx * (W * 0.5 - 0.02), SPLIT, CZ + H * 0.5 - 0.05), M_CHROME)
    bevel(p, 0.006, 2)

# ---------------------------------------------------------------- shell detail
for i in range(-3, 4):
    r = box("RibFront%d" % i, (0.016, 0.012, H - 0.10),
            (i * (W * 0.135), D * 0.5 - 0.004, CZ), M_SHELL)
    bevel(r, 0.005, 3)
    smooth(r, 50)
box("BrandPlate", (0.10, 0.008, 0.030), (0.0, D * 0.5 + 0.004, CZ + H * 0.30), M_ACCENT)

# ---------------------------------------------------------------- corner bumpers
for sx in (-1, 1):
    for sy in (-1, 1):
        for sz in (-1, 1):
            b = box("Bumper%d%d%d" % (sx, sy, sz), (0.075, 0.070, 0.075),
                    (sx * (W * 0.5 - 0.018), sy * (D * 0.5 - 0.016),
                     CZ + sz * (H * 0.5 - 0.018)), M_TRIM)
            bevel(b, 0.030, 5, angle=60)
            smooth(b, 55)

for sy in (-1, 1):
    r = box("BottomRail%d" % sy, (W - 0.08, 0.030, 0.026),
            (0, sy * (D * 0.5 - 0.018), BASE_Z + 0.010), M_TRIM)
    bevel(r, 0.010, 3)

# ---------------------------------------------------------------- spinner wheels
for sx in (-1, 1):
    for sy in (-1, 1):
        px = sx * (W * 0.5 - 0.062)
        py = sy * (D * 0.5 - 0.052)
        hs = box("WheelHouse%d%d" % (sx, sy), (0.072, 0.070, 0.036),
                 (px, py, BASE_Z + 0.006), M_TRIM)
        bevel(hs, 0.012, 3)
        smooth(cyl("Swivel%d%d" % (sx, sy), 0.014, 0.030, (px, py, BASE_Z - 0.010),
                   M_CHROME, verts=16))
        for fy in (-1, 1):
            box("Fork%d%d%d" % (sx, sy, fy), (0.052, 0.010, 0.052),
                (px, py + fy * 0.026, WHEEL_R + 0.006), M_TRIM)
        w = cyl("Wheel%d%d" % (sx, sy), WHEEL_R, 0.030, (px, py, WHEEL_R), M_RUBBER,
                rot=(radians(90), 0, 0), verts=32)
        smooth(w)
        bevel(w, 0.006, 2)
        smooth(cyl("WheelHub%d%d" % (sx, sy), 0.014, 0.032, (px, py, WHEEL_R),
                   M_CHROME, rot=(radians(90), 0, 0), verts=16))

# ---------------------------------------------------------------- telescopic handle
TOP = BASE_Z + H
EXT = 0.34
for sx in (-1, 1):
    px = sx * 0.105
    smooth(cyl("TeleOuter%d" % sx, 0.0155, 0.10, (px, -D * 0.5 + 0.045, TOP - 0.02),
               M_TRIM, verts=20))
    smooth(cyl("TeleInner%d" % sx, 0.0125, EXT,
               (px, -D * 0.5 + 0.045, TOP + EXT * 0.5 - 0.01), M_CHROME, verts=20))

grip = box("HandleGrip", (0.26, 0.042, 0.038), (0, -D * 0.5 + 0.045, TOP + EXT + 0.005),
           M_TRIM)
bevel(grip, 0.016, 4, angle=60)
smooth(grip, 55)
smooth(cyl("ReleaseButton", 0.014, 0.010, (0, -D * 0.5 + 0.028, TOP + EXT + 0.010),
           M_ACCENT, rot=(radians(90), 0, 0), verts=16))
for sx in (-1, 1):
    smooth(cyl("GripCap%d" % sx, 0.019, 0.014,
               (sx * 0.13, -D * 0.5 + 0.045, TOP + EXT + 0.005), M_RUBBER,
               rot=(0, radians(90), 0), verts=18))

# ---------------------------------------------------------------- carry handles
top_h = box("TopHandle", (0.16, 0.034, 0.026), (0, D * 0.5 - 0.075, TOP + 0.020), M_TRIM)
bevel(top_h, 0.011, 3)
for sx in (-1, 1):
    box("TopHandleMount%d" % sx, (0.034, 0.042, 0.026),
        (sx * 0.066, D * 0.5 - 0.075, TOP + 0.002), M_TRIM)

side_h = box("SideHandle", (0.026, 0.034, 0.15), (W * 0.5 + 0.016, 0.0, CZ + 0.06),
             M_TRIM)
bevel(side_h, 0.010, 3)
for sz in (-1, 1):
    box("SideHandleMount%d" % sz, (0.026, 0.044, 0.032),
        (W * 0.5 + 0.006, 0.0, CZ + 0.06 + sz * 0.062), M_TRIM)

# ---------------------------------------------------------------- lock, feet, tag
lock = box("TSALock", (0.052, 0.026, 0.038), (0.0, SPLIT + 0.006, CZ + H * 0.5 - 0.10),
           M_CHROME)
bevel(lock, 0.008, 3)
for i in range(3):
    smooth(cyl("Dial%d" % i, 0.008, 0.014,
               (-0.014 + i * 0.014, SPLIT + 0.020, CZ + H * 0.5 - 0.10), M_TRIM,
               rot=(0, radians(90), 0), verts=14))

for sx in (-1, 1):
    f = box("Foot%d" % sx, (0.045, 0.035, 0.014),
            (sx * 0.13, -D * 0.5 + 0.03, BASE_Z + 0.004), M_RUBBER)
    bevel(f, 0.005, 2)

torus("TagLoop", 0.020, 0.0035, (0.055, D * 0.5 - 0.075, TOP + 0.012), M_TRIM,
      rot=(radians(90), 0, 0))
smooth(cyl("TagStrap", 0.004, 0.075, (0.055, D * 0.5 - 0.072, TOP - 0.030), M_TRIM,
           verts=10))
tag = box("Tag", (0.062, 0.006, 0.042), (0.055, D * 0.5 - 0.070, TOP - 0.078), M_TAG,
          rot=(0, 0, radians(6)))
bevel(tag, 0.005, 2)

for i, (x, z, s) in enumerate(((-0.12, 0.16, 0.055), (0.10, -0.06, 0.045))):
    smooth(cyl("Sticker%d" % i, s, 0.004, (x, -D * 0.5 - 0.001, CZ + z), M_TAG,
               rot=(radians(90), 0, 0), verts=20))

# ---------------------------------------------------------------- lighting
world = bpy.data.worlds.new("World")
scene.world = world
world.use_nodes = True
world.node_tree.nodes["Background"].inputs[0].default_value = (0.35, 0.38, 0.44, 1.0)
world.node_tree.nodes["Background"].inputs[1].default_value = 0.65

key = bpy.data.lights.new("Key", 'AREA')
key.energy = 320.0
key.size = 1.8
ko = bpy.data.objects.new("Key", key)
scene.collection.objects.link(ko)
ko.location = (1.3, -1.4, 2.0)
ko.rotation_euler = (radians(42), 0, radians(44))

fill = bpy.data.lights.new("Fill", 'AREA')
fill.energy = 110.0
fill.size = 2.5
fo = bpy.data.objects.new("Fill", fill)
scene.collection.objects.link(fo)
fo.location = (-1.6, -1.1, 1.3)
fo.rotation_euler = (radians(66), 0, radians(-56))

rim = bpy.data.lights.new("Rim", 'AREA')
rim.energy = 160.0
rim.size = 1.2
ro = bpy.data.objects.new("Rim", rim)
scene.collection.objects.link(ro)
ro.location = (-0.6, 1.7, 1.5)
ro.rotation_euler = (radians(62), 0, radians(196))

# ---------------------------------------------------------------- camera
cam_data = bpy.data.cameras.new("Camera")
cam_data.lens = 65.0
cam = bpy.data.objects.new("Camera", cam_data)
scene.collection.objects.link(cam)
cam.location = (1.15, -1.35, 0.98)
target = Vector((0.0, 0.0, 0.52))
cam.rotation_euler = (target - cam.location).to_track_quat('-Z', 'Y').to_euler()
cam_data.dof.use_dof = True
cam_data.dof.focus_distance = (target - cam.location).length
cam_data.dof.aperture_fstop = 5.0
scene.camera = cam
