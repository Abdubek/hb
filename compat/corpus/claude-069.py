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


def smooth(ob, angle=40.0):
    for p in ob.data.polygons:
        p.use_smooth = True
    m = ob.modifiers.new("EdgeSplit", 'EDGE_SPLIT')
    m.split_angle = radians(angle)
    return ob


def bevel(ob, width=0.004, segments=3, angle=40.0):
    m = ob.modifiers.new("Bevel", 'BEVEL')
    m.width = width
    m.segments = segments
    m.limit_method = 'ANGLE'
    m.angle_limit = radians(angle)
    return ob


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


def cone(name, r1, r2, h, loc, material=None, rot=(0, 0, 0), verts=24):
    bpy.ops.mesh.primitive_cone_add(vertices=verts, radius1=r1, radius2=r2, depth=h,
                                    location=loc, rotation=rot)
    ob = C.object
    ob.name = name
    if material:
        ob.data.materials.append(material)
    return ob


def sphere(name, r, loc, material=None, segs=28, rings=16):
    bpy.ops.mesh.primitive_uv_sphere_add(segments=segs, ring_count=rings, radius=r,
                                         location=loc)
    ob = C.object
    ob.name = name
    if material:
        ob.data.materials.append(material)
    return ob


def _orient(ob, d):
    ob.rotation_mode = 'QUATERNION'
    ob.rotation_quaternion = d.to_track_quat('Z', 'Y')
    bpy.ops.object.transform_apply(location=False, rotation=True, scale=False)


def cyl_between(name, p1, p2, r, material=None, verts=24, shade=True):
    p1, p2 = Vector(p1), Vector(p2)
    d = p2 - p1
    ob = cyl(name, r, d.length, (p1 + p2) * 0.5, material, verts=verts)
    _orient(ob, d)
    if shade:
        smooth(ob)
    return ob


def bar_between(name, p1, p2, w, h, material=None, bev=0.004):
    p1, p2 = Vector(p1), Vector(p2)
    d = p2 - p1
    bpy.ops.mesh.primitive_cube_add(size=1, location=(p1 + p2) * 0.5)
    ob = C.object
    ob.name = name
    ob.scale = (w, h, d.length)
    ob.rotation_mode = 'QUATERNION'
    ob.rotation_quaternion = d.to_track_quat('Z', 'Y')
    bpy.ops.object.transform_apply(location=False, rotation=True, scale=True)
    if material:
        ob.data.materials.append(material)
    if bev:
        bevel(ob, bev, 3)
    return ob


def lerp(a, b, t):
    return Vector(a).lerp(Vector(b), t)


# ---------------------------------------------------------------- materials
M_FLOOR = mat("Floor", (0.19, 0.19, 0.20), rough=0.55)
M_ALU = mat("Aluminium", (0.60, 0.61, 0.63), rough=0.28, metal=1.0)
M_ANOD = mat("BlackAnodised", (0.055, 0.055, 0.060), rough=0.38, metal=0.85)
M_CARBON = mat("CarbonTube", (0.085, 0.085, 0.092), rough=0.30, metal=0.15)
M_RUBBER = mat("Rubber", (0.030, 0.030, 0.032), rough=0.88)
M_KNOB = mat("Knob", (0.10, 0.10, 0.11), rough=0.62)
M_ACCENT = mat("Accent", (0.55, 0.36, 0.06), rough=0.32, metal=0.9)
M_LEVEL = mat("Level", (0.35, 0.72, 0.45), rough=0.20)

box("Floor", (12.0, 12.0, 0.08), (0, 0, -0.04), M_FLOOR)

# ---------------------------------------------------------------- key dimensions
APEX_Z = 1.02           # leg hinge / spider height
FOOT_R = 0.62           # radius of the spread feet
HUB_R = 0.058
COL_R = 0.019

# ---------------------------------------------------------------- spider hub
hub = cyl("Hub", HUB_R, 0.055, (0, 0, APEX_Z - 0.010), M_ANOD, verts=36)
bevel(hub, 0.006, 3)
smooth(hub)
smooth(cone("HubTop", HUB_R, HUB_R * 0.72, 0.028, (0, 0, APEX_Z + 0.031), M_ANOD,
            verts=36))
smooth(cone("HubBottom", HUB_R * 0.70, HUB_R, 0.026, (0, 0, APEX_Z - 0.050), M_ANOD,
            verts=36))

# ---------------------------------------------------------------- legs
LEG_ANGLES = (90.0, 210.0, 330.0)
for li, adeg in enumerate(LEG_ANGLES):
    a = radians(adeg)
    ux, uy = cos(a), sin(a)
    top = Vector((ux * (HUB_R + 0.010), uy * (HUB_R + 0.010), APEX_Z - 0.010))
    foot = Vector((ux * FOOT_R, uy * FOOT_R, 0.030))
    axis = (foot - top).normalized()

    bar_between("Yoke%d" % li, top - axis * 0.01, lerp(top, foot, 0.055),
                0.046, 0.030, M_ANOD, bev=0.005)
    smooth(sphere("HingeBolt%d" % li, 0.014, top, M_ALU, segs=18, rings=10))

    # upper section: square-shouldered tube with a raised spine
    up_a = lerp(top, foot, 0.045)
    up_b = lerp(top, foot, 0.560)
    smooth(bar_between("LegUpper%d" % li, up_a, up_b, 0.036, 0.026, M_CARBON,
                       bev=0.008), 50)
    bar_between("LegSpine%d" % li, up_a, up_b, 0.012, 0.032, M_ANOD, bev=0.003)

    # twist-lock collar between the sections
    lock = cyl_between("LegLock%d" % li, lerp(top, foot, 0.545),
                       lerp(top, foot, 0.615), 0.026, M_KNOB, verts=24)
    bevel(lock, 0.004, 2)
    for k in range(8):
        t = 0.552 + k * 0.008
        cyl_between("Knurl%d_%d" % (li, k), lerp(top, foot, t),
                    lerp(top, foot, t + 0.004), 0.0275, M_ANOD, verts=16)

    # lower section: thinner round tube
    cyl_between("LegLower%d" % li, lerp(top, foot, 0.545), lerp(top, foot, 0.965),
                0.0155, M_CARBON, verts=24)

    # rubber foot
    foot_cup = cone("Foot%d" % li, 0.030, 0.024, 0.038,
                    tuple(lerp(top, foot, 0.985) + Vector((0, 0, -0.004))),
                    M_RUBBER, verts=24)
    _orient(foot_cup, axis)
    smooth(foot_cup)
    pad = cyl("FootPad%d" % li, 0.030, 0.014, (foot.x * 1.005, foot.y * 1.005, 0.008),
              M_RUBBER, verts=24)
    smooth(pad)
    bevel(pad, 0.004, 2)

    # leg-angle selector tab near the hinge
    tab = box("AngleTab%d" % li, (0.026, 0.018, 0.030),
              tuple(lerp(top, foot, 0.075) + Vector((ux * 0.030, uy * 0.030, 0.012))),
              M_ACCENT)
    bevel(tab, 0.004, 2)

    # brace strut linking the leg to the centre-column collar
    brace_leg = lerp(top, foot, 0.335)
    brace_hub = Vector((ux * 0.052, uy * 0.052, 0.700))
    cyl_between("Brace%d" % li, brace_hub, brace_leg, 0.0075, M_ALU, verts=16)
    smooth(sphere("BraceJoint%d" % li, 0.011, brace_leg, M_ANOD, segs=14, rings=8))

collar = cyl("BraceCollar", 0.040, 0.045, (0, 0, 0.700), M_ANOD, verts=28)
bevel(collar, 0.005, 3)
smooth(collar)

# ---------------------------------------------------------------- centre column
COL_TOP = 1.33
smooth(cyl("CentreColumn", COL_R, COL_TOP - 0.52, (0, 0, (COL_TOP + 0.52) * 0.5),
           M_ALU, verts=28))
for i in range(10):
    z = 0.60 + i * 0.028
    if z < APEX_Z - 0.06:
        smooth(cyl("Rack%d" % i, COL_R + 0.004, 0.010, (0, 0, z), M_ANOD, verts=20))

knob = cyl("ColumnKnob", 0.024, 0.036, (HUB_R + 0.020, 0.0, APEX_Z - 0.008), M_KNOB,
           rot=(0, radians(90), 0), verts=24)
bevel(knob, 0.004, 2)
smooth(knob)
smooth(cyl("KnobStem", 0.010, 0.030, (HUB_R + 0.002, 0, APEX_Z - 0.008), M_ALU,
           rot=(0, radians(90), 0), verts=14))

smooth(cyl("ColumnBottom", COL_R * 0.8, 0.030, (0, 0, 0.520), M_ANOD, verts=20))
bpy.ops.mesh.primitive_torus_add(major_radius=0.016, minor_radius=0.0035,
                                 major_segments=24, minor_segments=10,
                                 location=(0, 0, 0.492), rotation=(radians(90), 0, 0))
hook = C.object
hook.name = "WeightHook"
hook.data.materials.append(M_ALU)
for p in hook.data.polygons:
    p.use_smooth = True

smooth(cyl("BubbleLevel", 0.012, 0.010, (0.0, HUB_R - 0.014, APEX_Z + 0.045), M_LEVEL,
           verts=18))

# ---------------------------------------------------------------- ball head
BASE_Z = COL_TOP
head_base = cyl("HeadBase", 0.046, 0.030, (0, 0, BASE_Z + 0.015), M_ANOD, verts=32)
bevel(head_base, 0.005, 3)
smooth(head_base)
smooth(cone("HeadBody", 0.046, 0.038, 0.055, (0, 0, BASE_Z + 0.057), M_ANOD, verts=32))
smooth(sphere("Ball", 0.041, (0, 0, BASE_Z + 0.108), M_ALU))
smooth(cone("Socket", 0.040, 0.030, 0.030, (0, 0, BASE_Z + 0.092), M_ANOD, verts=32))

TILT = radians(7)
stem_top = Vector((0.0, -0.012, BASE_Z + 0.152))
smooth(cyl("BallStem", 0.015, 0.040, (0, -0.005, BASE_Z + 0.136), M_ALU,
           rot=(TILT, 0, 0), verts=20))
clamp = box("QRClamp", (0.075, 0.058, 0.024), tuple(stem_top), M_ANOD, rot=(TILT, 0, 0))
bevel(clamp, 0.006, 3)
plate_qr = box("QRPlate", (0.060, 0.050, 0.012),
               (stem_top.x, stem_top.y - 0.002, stem_top.z + 0.018), M_ACCENT,
               rot=(TILT, 0, 0))
bevel(plate_qr, 0.004, 2)
smooth(cyl("QRScrew", 0.008, 0.014,
           (stem_top.x, stem_top.y - 0.002, stem_top.z + 0.028), M_ALU, verts=14))

for name, ang in (("PanLock", radians(-90)), ("BallLock", radians(20))):
    kx, ky = 0.046 * cos(ang), 0.046 * sin(ang)
    k = cyl(name, 0.019, 0.030, (kx, ky, BASE_Z + 0.052), M_KNOB,
            rot=(0, radians(90), ang), verts=22)
    bevel(k, 0.003, 2)
    smooth(k)

ring = cyl("FrictionRing", 0.048, 0.012, (0, 0, BASE_Z + 0.034), M_ACCENT, verts=32)
smooth(ring)
bevel(ring, 0.003, 2)

# pan handle angling down and back from the head
h_start = Vector((0.040, 0.030, BASE_Z + 0.075))
h_end = h_start + Vector((0.14, 0.15, -0.09))
cyl_between("PanHandle", h_start, h_end, 0.010, M_ANOD, verts=20)
cyl_between("PanGrip", h_start.lerp(h_end, 0.45), h_end, 0.014, M_RUBBER, verts=20)
smooth(sphere("PanHandleTip", 0.014, h_end, M_RUBBER, segs=18, rings=10))

# ---------------------------------------------------------------- lighting
world = bpy.data.worlds.new("World")
scene.world = world
world.use_nodes = True
world.node_tree.nodes["Background"].inputs[0].default_value = (0.30, 0.33, 0.38, 1.0)
world.node_tree.nodes["Background"].inputs[1].default_value = 0.6

key = bpy.data.lights.new("Key", 'AREA')
key.energy = 400.0
key.size = 2.0
ko = bpy.data.objects.new("Key", key)
scene.collection.objects.link(ko)
ko.location = (1.6, -1.9, 2.6)
ko.rotation_euler = (radians(38), 0, radians(40))

fill = bpy.data.lights.new("Fill", 'AREA')
fill.energy = 140.0
fill.size = 3.0
fo = bpy.data.objects.new("Fill", fill)
scene.collection.objects.link(fo)
fo.location = (-2.0, -1.4, 1.6)
fo.rotation_euler = (radians(65), 0, radians(-54))

rim = bpy.data.lights.new("Rim", 'AREA')
rim.energy = 260.0
rim.size = 1.5
ro = bpy.data.objects.new("Rim", rim)
scene.collection.objects.link(ro)
ro.location = (-0.4, 2.2, 2.0)
ro.rotation_euler = (radians(58), 0, radians(192))

# ---------------------------------------------------------------- camera
cam_data = bpy.data.cameras.new("Camera")
cam_data.lens = 58.0
cam = bpy.data.objects.new("Camera", cam_data)
scene.collection.objects.link(cam)
cam.location = (1.55, -1.95, 1.35)
target = Vector((0.0, 0.0, 0.80))
cam.rotation_euler = (target - cam.location).to_track_quat('-Z', 'Y').to_euler()
cam_data.dof.use_dof = True
cam_data.dof.focus_distance = (target - cam.location).length
cam_data.dof.aperture_fstop = 5.6
scene.camera = cam
