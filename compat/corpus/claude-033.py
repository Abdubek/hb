"""claude-033 - Quadcopter with four propellers.

Carbon-plate frame with X arms, four motors carrying twisted two-blade
propellers, battery, FPV camera, antenna, GPS mast, LEDs and landing legs.
"""

import bpy
import bmesh
import math
from mathutils import Vector, Matrix, Euler


# ----------------------------------------------------------------- utilities
def setup(bg=(0.05, 0.06, 0.08), s=1.0):
    bpy.ops.wm.read_factory_settings(use_empty=True)
    sc = bpy.context.scene
    try:
        sc.render.engine = 'BLENDER_EEVEE_NEXT'
    except Exception:
        pass
    sc.render.resolution_x, sc.render.resolution_y = 1920, 1080
    w = bpy.data.worlds.new("World")
    sc.world = w
    w.use_nodes = True
    n = w.node_tree.nodes["Background"]
    n.inputs[0].default_value = (bg[0], bg[1], bg[2], 1.0)
    n.inputs[1].default_value = s
    return sc


def mat(name, col, rough=0.5, metal=0.0, emis=None, es=4.0):
    m = bpy.data.materials.new(name)
    m.use_nodes = True
    b = m.node_tree.nodes["Principled BSDF"]
    b.inputs["Base Color"].default_value = (col[0], col[1], col[2], 1.0)
    b.inputs["Roughness"].default_value = rough
    b.inputs["Metallic"].default_value = metal
    if emis is not None:
        b.inputs["Emission Color"].default_value = (emis[0], emis[1], emis[2], 1.0)
        b.inputs["Emission Strength"].default_value = es
    return m


def MX(loc=(0, 0, 0), rot=(0, 0, 0), scl=(1, 1, 1)):
    return (Matrix.Translation(loc)
            @ Euler(rot, 'XYZ').to_matrix().to_4x4()
            @ Matrix.Diagonal(Vector((scl[0], scl[1], scl[2], 1.0))))


def bbox(bm, size, loc=(0, 0, 0), rot=(0, 0, 0)):
    bmesh.ops.create_cube(bm, size=1.0, matrix=MX(loc, rot, size))


def bcyl(bm, r, d, loc=(0, 0, 0), rot=(0, 0, 0), seg=16, r2=None, cap=True):
    bmesh.ops.create_cone(bm, cap_ends=cap, cap_tris=False, segments=seg,
                          radius1=r, radius2=(r if r2 is None else r2),
                          depth=d, matrix=MX(loc, rot))


def bsph(bm, r, loc=(0, 0, 0), u=16, v=8):
    bmesh.ops.create_uvsphere(bm, u_segments=u, v_segments=v, radius=r,
                              matrix=MX(loc))


def shade(ob, angle=35.0):
    for p in ob.data.polygons:
        p.use_smooth = True
    try:
        bpy.context.view_layer.objects.active = ob
        ob.select_set(True)
        bpy.ops.object.shade_smooth_by_angle(angle=math.radians(angle))
        ob.select_set(False)
    except Exception:
        pass


def finish(name, bm, m=None, smooth=None, loc=(0, 0, 0), rot=(0, 0, 0), parent=None):
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    me = bpy.data.meshes.new(name)
    bm.to_mesh(me)
    bm.free()
    me.validate()
    ob = bpy.data.objects.new(name, me)
    bpy.context.scene.collection.objects.link(ob)
    ob.location = loc
    ob.rotation_euler = rot
    if m:
        me.materials.append(m)
    if smooth:
        shade(ob, smooth)
    if parent:
        ob.parent = parent
    return ob


def cyl(name, r, d, loc=(0, 0, 0), rot=(0, 0, 0), seg=24, r2=None, m=None,
        smooth=35.0, cap=True, parent=None):
    bm = bmesh.new()
    bcyl(bm, r, d, seg=seg, r2=r2, cap=cap)
    return finish(name, bm, m, smooth, loc, rot, parent)


def box(name, size, loc=(0, 0, 0), rot=(0, 0, 0), m=None, bev=0.0, seg=2, parent=None):
    bm = bmesh.new()
    bbox(bm, size)
    if bev > 0.0:
        bmesh.ops.bevel(bm, geom=list(bm.verts) + list(bm.edges) + list(bm.faces),
                        offset=bev, segments=seg, profile=0.5, affect='EDGES',
                        clamp_overlap=True)
    return finish(name, bm, m, None, loc, rot, parent)


def between(name, p1, p2, r, m=None, seg=12, r2=None, parent=None, smooth=40.0):
    p1, p2 = Vector(p1), Vector(p2)
    d = p2 - p1
    return cyl(name, r, d.length, (p1 + p2) / 2.0,
               d.to_track_quat('Z', 'Y').to_euler(), seg=seg, r2=r2, m=m,
               smooth=smooth, parent=parent)


def cam(loc, tgt, lens=50.0):
    c = bpy.data.cameras.new("Camera")
    c.lens = lens
    ob = bpy.data.objects.new("Camera", c)
    bpy.context.scene.collection.objects.link(ob)
    ob.location = loc
    ob.rotation_euler = (Vector(tgt) - Vector(loc)).to_track_quat('-Z', 'Y').to_euler()
    bpy.context.scene.camera = ob
    return ob


def light(kind, name, loc, energy, col=(1, 1, 1), size=1.0, tgt=None, angle=0.05):
    l = bpy.data.lights.new(name, kind)
    l.energy = energy
    l.color = col
    if kind == 'AREA':
        l.size = size
    elif kind == 'SUN':
        l.angle = angle
    elif kind == 'POINT':
        l.shadow_soft_size = size
    ob = bpy.data.objects.new(name, l)
    bpy.context.scene.collection.objects.link(ob)
    ob.location = loc
    if tgt is not None:
        ob.rotation_euler = (Vector(tgt) - Vector(loc)).to_track_quat('-Z', 'Y').to_euler()
    return ob


def empty(name, loc=(0, 0, 0), rot=(0, 0, 0), parent=None):
    e = bpy.data.objects.new(name, None)
    bpy.context.scene.collection.objects.link(e)
    e.location = loc
    e.rotation_euler = rot
    e.empty_display_size = 0.03
    if parent:
        e.parent = parent
    return e


# ----------------------------------------------------------------- materials
setup((0.035, 0.040, 0.050), 1.0)

M_CARBON = mat("Carbon", (0.020, 0.021, 0.024), 0.30, 0.25)
M_PLASTIC = mat("Plastic", (0.055, 0.058, 0.065), 0.45)
M_ORANGE = mat("Accent", (0.85, 0.28, 0.03), 0.35)
M_ALU = mat("Aluminium", (0.72, 0.73, 0.75), 0.22, 1.0)
M_MOTOR = mat("MotorBell", (0.30, 0.31, 0.34), 0.28, 1.0)
M_COPPER = mat("Windings", (0.60, 0.31, 0.12), 0.45, 0.9)
M_PROP = mat("Propeller", (0.10, 0.11, 0.13), 0.30)
M_PROPTIP = mat("PropTip", (0.90, 0.62, 0.08), 0.30)
M_BATT = mat("Battery", (0.12, 0.13, 0.30), 0.55)
M_LENS = mat("CameraLens", (0.02, 0.03, 0.06), 0.08)
M_LED_R = mat("LedRed", (0.4, 0.02, 0.02), 0.2, emis=(1.0, 0.05, 0.05), es=25.0)
M_LED_G = mat("LedGreen", (0.02, 0.4, 0.08), 0.2, emis=(0.1, 1.0, 0.2), es=25.0)
M_PAD = mat("LandingPad", (0.10, 0.10, 0.11), 0.85)
M_PADMARK = mat("PadMark", (0.80, 0.80, 0.78), 0.7)
M_FLOOR = mat("Floor", (0.045, 0.047, 0.052), 0.75)

root = empty("Quadcopter", loc=(0.0, 0.0, 0.0))

# ----------------------------------------------------------------- frame
BODY_Z = 0.075          # height of the frame plates above the ground
ARM_R = 0.185           # motor distance from centre

# bottom and top carbon plates (hex-ish beveled slabs)
box("BottomPlate", (0.115, 0.155, 0.004), loc=(0.0, 0.0, BODY_Z),
    m=M_CARBON, bev=0.010, seg=3, parent=root)
box("MidPlate", (0.100, 0.130, 0.003), loc=(0.0, 0.0, BODY_Z + 0.024),
    m=M_CARBON, bev=0.008, seg=3, parent=root)
box("TopPlate", (0.108, 0.140, 0.004), loc=(0.0, 0.0, BODY_Z + 0.050),
    m=M_CARBON, bev=0.010, seg=3, parent=root)

# standoffs between plates
bm = bmesh.new()
for sx in (-1.0, 1.0):
    for sy in (-1.0, 1.0):
        bcyl(bm, 0.0045, 0.046, loc=(sx * 0.042, sy * 0.058, BODY_Z + 0.025), seg=10)
finish("Standoffs", bm, M_ORANGE, smooth=40.0, parent=root)

# flight controller stack + ESC
box("FlightController", (0.036, 0.036, 0.006), loc=(0.0, 0.0, BODY_Z + 0.011),
    m=M_PLASTIC, bev=0.001, parent=root)
box("ESC", (0.040, 0.040, 0.005), loc=(0.0, -0.002, BODY_Z + 0.033),
    m=M_PLASTIC, bev=0.001, parent=root)

# battery strapped on top
box("Battery", (0.070, 0.108, 0.030), loc=(0.0, -0.006, BODY_Z + 0.068),
    m=M_BATT, bev=0.004, parent=root)
bm = bmesh.new()
for y in (-0.035, 0.035):
    bbox(bm, (0.078, 0.016, 0.036), loc=(0.0, y - 0.006, BODY_Z + 0.068))
finish("BatteryStraps", bm, M_PLASTIC, parent=root)

# ----------------------------------------------------------------- arms and motors
def motor(name, parent, loc):
    cyl(name + "_Base", 0.016, 0.006, (loc[0], loc[1], loc[2] + 0.003), seg=20,
        m=M_PLASTIC, parent=parent)
    cyl(name + "_Stator", 0.0135, 0.012, (loc[0], loc[1], loc[2] + 0.012), seg=20,
        m=M_COPPER, parent=parent)
    cyl(name + "_Bell", 0.0155, 0.014, (loc[0], loc[1], loc[2] + 0.017), seg=24,
        m=M_MOTOR, parent=parent)
    cyl(name + "_BellTop", 0.0155, 0.003, (loc[0], loc[1], loc[2] + 0.0255), seg=24,
        r2=0.012, m=M_MOTOR, parent=parent)
    cyl(name + "_Shaft", 0.0025, 0.020, (loc[0], loc[1], loc[2] + 0.032), seg=10,
        m=M_ALU, parent=parent)


def prop_blade(name, parent, R, hub_r, pitch, nspan=16, ncho=6):
    bm = bmesh.new()
    grid = []
    for i in range(nspan + 1):
        t = i / nspan
        r = hub_r + (R - hub_r) * t
        chord = 0.026 * (0.45 + 0.9 * math.sin(math.pi * min(1.0, 0.18 + 0.88 * t)))
        if t > 0.90:
            chord *= max(0.18, (1.0 - t) / 0.10)
        tw = math.radians(pitch * (1.0 - 0.62 * t))
        row = []
        for j in range(ncho + 1):
            s = j / ncho - 0.5
            y = chord * s
            z = 0.13 * chord * (1.0 - 4.0 * s * s)
            yy = y * math.cos(tw) - z * math.sin(tw)
            zz = y * math.sin(tw) + z * math.cos(tw)
            row.append(bm.verts.new((r, yy, zz)))
        grid.append(row)
    for i in range(nspan):
        for j in range(ncho):
            bm.faces.new((grid[i][j], grid[i][j + 1],
                          grid[i + 1][j + 1], grid[i + 1][j]))
    ob = finish(name, bm, M_PROP, 55.0, parent=parent)
    sol = ob.modifiers.new("Solidify", 'SOLIDIFY')
    sol.thickness = 0.0016
    sol.offset = 0.0
    return ob


def propeller(index, parent, loc, cw, phase):
    hub = empty("Prop_%d" % index, loc=loc, rot=(0.0, 0.0, phase), parent=parent)
    cyl("PropHub_%d" % index, 0.011, 0.008, (0.0, 0.0, 0.0), seg=20,
        m=M_PROP, parent=hub)
    cyl("PropNut_%d" % index, 0.006, 0.006, (0.0, 0.0, 0.007), seg=12,
        r2=0.0045, m=M_ORANGE, parent=hub)
    for k in range(2):
        b = prop_blade("Blade_%d_%d" % (index, k), hub, 0.118, 0.010,
                       22.0 if cw else -22.0)
        b.rotation_euler = (0.0, 0.0, math.pi * k)
        if cw:
            b.scale = (1.0, -1.0, 1.0)
    return hub


for i in range(4):
    a = math.pi / 4.0 + i * math.pi / 2.0
    mx, my = math.cos(a) * ARM_R, math.sin(a) * ARM_R
    inner = Vector((math.cos(a) * 0.045, math.sin(a) * 0.045, BODY_Z))
    outer = Vector((mx, my, BODY_Z))
    # tapered arm plate
    bm = bmesh.new()
    bbox(bm, (ARM_R - 0.030, 0.026, 0.006),
         loc=((0.045 + ARM_R) / 2.0, 0.0, 0.0))
    bbox(bm, (0.055, 0.034, 0.010), loc=(ARM_R - 0.006, 0.0, 0.0))
    arm = finish("Arm_%d" % i, bm, M_CARBON, loc=(0.0, 0.0, BODY_Z),
                 rot=(0.0, 0.0, a), parent=root)
    # motor mount ring
    cyl("MotorMount_%d" % i, 0.021, 0.008, (mx, my, BODY_Z + 0.006), seg=20,
        m=M_ORANGE, parent=root)
    motor("Motor_%d" % i, root, (mx, my, BODY_Z + 0.010))
    propeller(i, root, (mx, my, BODY_Z + 0.046),
              cw=(i % 2 == 0), phase=i * 0.6)
    # navigation LED at the arm end
    ledm = M_LED_G if my > 0.0 else M_LED_R
    cyl("Led_%d" % i, 0.005, 0.003, (mx * 0.86, my * 0.86, BODY_Z - 0.004),
        seg=10, m=ledm, parent=root)

# ----------------------------------------------------------------- payload
# FPV camera pod at the front (+Y)
cam_root = empty("CameraPod", loc=(0.0, 0.088, BODY_Z + 0.028),
                 rot=(math.radians(-22.0), 0.0, 0.0), parent=root)
box("CamBody", (0.030, 0.026, 0.026), loc=(0.0, 0.0, 0.0), m=M_PLASTIC,
    bev=0.003, parent=cam_root)
cyl("CamBarrel", 0.010, 0.018, (0.0, 0.017, 0.0), rot=(math.pi / 2.0, 0.0, 0.0),
    seg=20, m=M_PLASTIC, parent=cam_root)
cyl("CamLens", 0.0082, 0.004, (0.0, 0.027, 0.0), rot=(math.pi / 2.0, 0.0, 0.0),
    seg=20, m=M_LENS, parent=cam_root)

# GPS mast and antenna
cyl("GpsMast", 0.003, 0.055, (0.0, -0.050, BODY_Z + 0.095), seg=10,
    m=M_ALU, parent=root)
box("GpsPuck", (0.030, 0.030, 0.008), loc=(0.0, -0.050, BODY_Z + 0.126),
    m=M_PLASTIC, bev=0.002, parent=root)
ant = empty("AntennaRoot", loc=(0.0, -0.070, BODY_Z + 0.010),
            rot=(math.radians(35.0), 0.0, 0.0), parent=root)
cyl("AntennaCable", 0.0022, 0.045, (0.0, 0.0, -0.022), seg=8, m=M_PLASTIC,
    parent=ant)
cyl("AntennaTube", 0.008, 0.038, (0.0, 0.0, -0.062), seg=14, m=M_ORANGE,
    parent=ant)

# ----------------------------------------------------------------- landing gear
for i in range(4):
    a = math.pi / 4.0 + i * math.pi / 2.0
    ux, uy = math.cos(a), math.sin(a)
    top = (ux * 0.055, uy * 0.055, BODY_Z - 0.002)
    knee = (ux * 0.088, uy * 0.088, 0.030)
    foot = (ux * 0.094, uy * 0.094, 0.010)
    between("LegUpper_%d" % i, top, knee, 0.0035, m=M_CARBON, parent=root)
    between("LegLower_%d" % i, knee, foot, 0.0035, m=M_CARBON, parent=root)
    bm = bmesh.new()
    bsph(bm, 0.008, loc=foot, u=14, v=8)
    finish("Foot_%d" % i, bm, M_PLASTIC, smooth=45.0, parent=root)

# ----------------------------------------------------------------- environment
bm = bmesh.new()
bbox(bm, (12.0, 12.0, 0.2), loc=(0.0, 0.0, -0.1))
finish("Floor", bm, M_FLOOR)
cyl("LandingPad", 0.60, 0.006, (0.0, 0.0, 0.003), seg=48, m=M_PAD)
bm = bmesh.new()
bcyl(bm, 0.30, 0.002, loc=(0.0, 0.0, 0.0072), seg=48)
bcyl(bm, 0.26, 0.004, loc=(0.0, 0.0, 0.0072), seg=48)
bmesh.ops.delete(bm, geom=[f for f in bm.faces if f.calc_center_median().length < 0.27],
                 context='FACES')
bbox(bm, (0.055, 0.30, 0.002), loc=(-0.075, 0.0, 0.0072))
bbox(bm, (0.055, 0.30, 0.002), loc=(0.075, 0.0, 0.0072))
bbox(bm, (0.150, 0.045, 0.002), loc=(0.0, 0.0, 0.0072))
finish("PadMarking", bm, M_PADMARK)

# ----------------------------------------------------------------- lighting
light('AREA', "Key", (0.55, -0.45, 0.75), 220.0, (1.0, 0.96, 0.90),
      size=0.9, tgt=(0.0, 0.0, 0.10))
light('AREA', "Fill", (-0.70, -0.30, 0.35), 60.0, (0.62, 0.74, 1.0),
      size=1.4, tgt=(0.0, 0.0, 0.10))
light('AREA', "Rim", (-0.30, 0.75, 0.45), 120.0, (0.85, 0.92, 1.0),
      size=0.7, tgt=(0.0, 0.0, 0.12))
light('SUN', "Ambient", (0.0, 0.0, 3.0), 0.6, (0.8, 0.86, 1.0),
      tgt=(0.0, 0.0, 0.0), angle=0.4)

# ----------------------------------------------------------------- camera
cam((0.52, -0.58, 0.32), (0.0, 0.0, 0.105), lens=60.0)
