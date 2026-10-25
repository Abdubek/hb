"""claude-109 - Low angle hero view of a cordless power drill with battery pack and chuck."""
import bpy, bmesh, math
from mathutils import Vector, Matrix

R = math.radians

# ------------------------------------------------------------------ helpers
def scene(res=(1800, 1200)):
    bpy.ops.wm.read_factory_settings(use_empty=True)
    sc = bpy.context.scene
    sc.render.resolution_x, sc.render.resolution_y = res
    try:
        sc.render.engine = 'CYCLES'
        sc.cycles.samples = 192
    except Exception:
        pass
    w = bpy.data.worlds.new("World")
    sc.world = w
    w.use_nodes = True
    bg = w.node_tree.nodes["Background"]
    bg.inputs[0].default_value = (0.035, 0.038, 0.045, 1.0)
    bg.inputs[1].default_value = 0.6
    return sc


def mat(name, c, rough=0.5, metal=0.0, emit=None, es=0.0, trans=0.0):
    m = bpy.data.materials.new(name)
    m.use_nodes = True
    b = m.node_tree.nodes["Principled BSDF"]

    def s(keys, v):
        for k in keys:
            if k in b.inputs:
                b.inputs[k].default_value = v
                return
    s(["Base Color"], (c[0], c[1], c[2], 1.0))
    s(["Roughness"], rough)
    s(["Metallic"], metal)
    if trans:
        s(["Transmission Weight", "Transmission"], trans)
    if emit is not None:
        s(["Emission Color", "Emission"], (emit[0], emit[1], emit[2], 1.0))
        s(["Emission Strength"], es)
    return m


def put(ob, m):
    if m is not None:
        ob.data.materials.clear()
        ob.data.materials.append(m)
    return ob


def smooth(ob, ang=35):
    for p in ob.data.polygons:
        p.use_smooth = True
    md = ob.modifiers.new("ES", 'EDGE_SPLIT')
    md.split_angle = R(ang)
    md.use_edge_sharp = False


def bev(ob, w, seg=3):
    b = ob.modifiers.new("Bevel", 'BEVEL')
    b.width = w
    b.segments = seg
    b.limit_method = 'ANGLE'
    b.angle_limit = R(50)
    return b


def box(name, size, loc, rot=(0, 0, 0), m=None, b=0.0, seg=3, parent=None):
    me = bpy.data.meshes.new(name)
    bm = bmesh.new()
    bmesh.ops.create_cube(bm, size=1.0)
    bmesh.ops.scale(bm, vec=Vector(size), verts=bm.verts)
    bm.to_mesh(me)
    bm.free()
    ob = bpy.data.objects.new(name, me)
    ob.location = loc
    ob.rotation_euler = rot
    bpy.context.collection.objects.link(ob)
    put(ob, m)
    if b > 0:
        bev(ob, b, seg)
    if parent:
        ob.parent = parent
    return ob


def cyl(name, r, d, loc, rot=(0, 0, 0), v=32, m=None, parent=None, b=0.0):
    bpy.ops.mesh.primitive_cylinder_add(radius=r, depth=d, vertices=v, location=loc, rotation=rot)
    ob = bpy.context.active_object
    ob.name = name
    put(ob, m)
    smooth(ob)
    if b > 0:
        bev(ob, b, 2)
    if parent:
        ob.parent = parent
    return ob


def cone(name, r1, r2, d, loc, rot=(0, 0, 0), v=32, m=None, parent=None):
    bpy.ops.mesh.primitive_cone_add(radius1=r1, radius2=r2, depth=d, vertices=v,
                                    location=loc, rotation=rot)
    ob = bpy.context.active_object
    ob.name = name
    put(ob, m)
    smooth(ob)
    if parent:
        ob.parent = parent
    return ob


def torus(name, R1, R2, loc, rot=(0, 0, 0), ms=40, mn=12, m=None, parent=None):
    bpy.ops.mesh.primitive_torus_add(major_radius=R1, minor_radius=R2, major_segments=ms,
                                     minor_segments=mn, location=loc, rotation=rot)
    ob = bpy.context.active_object
    ob.name = name
    put(ob, m)
    smooth(ob, 80)
    if parent:
        ob.parent = parent
    return ob


def empty(name, loc=(0, 0, 0), rot=(0, 0, 0)):
    ob = bpy.data.objects.new(name, None)
    ob.location = loc
    ob.rotation_euler = rot
    ob.empty_display_size = 0.02
    bpy.context.collection.objects.link(ob)
    return ob


def aim(ob, t):
    d = Vector(t) - ob.location
    ob.rotation_euler = d.to_track_quat('-Z', 'Y').to_euler()


def light(name, kind, loc, energy, size=1.0, color=(1, 1, 1), target=None, shape=None, sy=None):
    l = bpy.data.lights.new(name, kind)
    l.energy = energy
    l.color = color
    if kind == 'AREA':
        l.size = size
        if shape:
            l.shape = shape
            l.size_y = sy or size
    else:
        l.shadow_soft_size = size
    ob = bpy.data.objects.new(name, l)
    ob.location = loc
    bpy.context.collection.objects.link(ob)
    if target is not None:
        aim(ob, target)
    return ob


# ------------------------------------------------------------------ scene
sc = scene()

M = {
    'shell': mat("Shell", (0.055, 0.058, 0.062), 0.38),
    'accent': mat("Accent", (0.85, 0.62, 0.04), 0.34),
    'rubber': mat("Overmould", (0.030, 0.032, 0.036), 0.82),
    'grey': mat("GreyPlastic", (0.24, 0.25, 0.27), 0.48),
    'steel': mat("Steel", (0.66, 0.67, 0.70), 0.24, 1.0),
    'darksteel': mat("DarkSteel", (0.30, 0.31, 0.33), 0.34, 1.0),
    'chrome': mat("Chrome", (0.82, 0.83, 0.85), 0.10, 1.0),
    'batt': mat("Battery", (0.10, 0.105, 0.115), 0.44),
    'green': mat("Gauge", (0.2, 1.0, 0.35), 0.3, emit=(0.25, 1.0, 0.40), es=6.0),
    'led': mat("LED", (1.0, 0.97, 0.90), 0.2, emit=(1.0, 0.96, 0.86), es=40.0),
    'floor': mat("Floor", (0.022, 0.024, 0.028), 0.12),
    'label': mat("Label", (0.88, 0.88, 0.86), 0.55),
}

DR = empty("Drill", (0.0, 0.0, 0.0), (0, 0, R(-10)))

BZ = 0.062          # battery height
AX = 0.176          # motor axis height

# ------------------------------------------------------------- battery pack
batt = box("BatteryBody", (0.086, 0.094, BZ - 0.004), (-0.028, 0, (BZ - 0.004) / 2 + 0.001),
           m=M['batt'], b=0.006, parent=DR)
box("BatteryFoot", (0.090, 0.098, 0.006), (-0.028, 0, 0.003), m=M['rubber'], b=0.002, parent=DR)
box("BatteryCollar", (0.070, 0.082, 0.016), (-0.022, 0, BZ + 0.004), m=M['shell'], b=0.004, parent=DR)
for sy in (-1, 1):
    box("Latch", (0.020, 0.008, 0.014), (-0.062, sy * 0.045, BZ - 0.016),
        m=M['grey'], b=0.003, parent=DR)
    box("Rail", (0.056, 0.006, 0.008), (-0.020, sy * 0.041, BZ - 0.002),
        m=M['grey'], b=0.002, parent=DR)
for i in range(3):
    box("Gauge%d" % i, (0.009, 0.0035, 0.0035), (-0.058 + i * 0.012, -0.048, 0.040),
        m=M['green'], parent=DR)
box("GaugeFace", (0.040, 0.002, 0.012), (-0.046, -0.0475, 0.040), m=M['shell'], parent=DR)
box("BattLabel", (0.044, 0.001, 0.016), (-0.024, 0.0475, 0.026), m=M['accent'], parent=DR)

# ------------------------------------------------------------- handle
HT = R(9)
handle = box("Handle", (0.040, 0.052, 0.116), (-0.014, 0, BZ + 0.058), rot=(0, HT, 0),
             m=M['shell'], b=0.014, seg=4, parent=DR)
for sy in (-1, 1):
    box("GripPad", (0.030, 0.006, 0.086), (-0.014, sy * 0.0262, BZ + 0.052), rot=(0, HT, 0),
        m=M['rubber'], b=0.005, parent=DR)
box("GripFront", (0.008, 0.040, 0.080), (-0.033, 0, BZ + 0.052), rot=(0, HT, 0),
    m=M['rubber'], b=0.006, parent=DR)
box("GripBack", (0.008, 0.040, 0.086), (0.006, 0, BZ + 0.056), rot=(0, HT, 0),
    m=M['rubber'], b=0.006, parent=DR)

# ------------------------------------------------------------- motor housing
body = cyl("MotorHousing", 0.0355, 0.150, (-0.028, 0, AX), rot=(0, R(90), 0), v=40,
           m=M['shell'], parent=DR)
cyl("HousingCap", 0.0330, 0.016, (-0.106, 0, AX), rot=(0, R(90), 0), v=40, m=M['grey'], parent=DR)
box("HousingSpine", (0.120, 0.030, 0.020), (-0.030, 0, AX + 0.026), m=M['shell'], b=0.008, parent=DR)
box("SpineGrip", (0.086, 0.020, 0.008), (-0.030, 0, AX + 0.036), m=M['rubber'], b=0.003, parent=DR)
# cooling vents around the rear of the housing
for i in range(10):
    a = R(-70 + i * 15.5)
    for xx in (-0.086, -0.070, -0.054):
        box("Vent", (0.008, 0.0030, 0.014),
            (xx, 0.0355 * math.cos(a) * 0.0 + 0.0, AX),
            rot=(a, 0, 0), m=M['grey'], parent=DR).location = (
                xx, 0.0350 * math.sin(a), AX + 0.0350 * math.cos(a))
box("HousingJoint", (0.148, 0.0016, 0.070), (-0.028, 0.0, AX), m=M['grey'], parent=DR)
box("NameBadge", (0.044, 0.001, 0.014), (-0.052, -0.0356, AX - 0.004), m=M['accent'], parent=DR)

# trigger + switches
box("Trigger", (0.016, 0.030, 0.034), (-0.040, 0, BZ + 0.088), rot=(0, R(6), 0),
    m=M['grey'], b=0.006, parent=DR)
box("TriggerFace", (0.005, 0.026, 0.030), (-0.048, 0, BZ + 0.088), rot=(0, R(6), 0),
    m=M['rubber'], b=0.004, parent=DR)
box("RevSwitch", (0.014, 0.062, 0.014), (-0.012, 0, AX - 0.020), m=M['grey'], b=0.004, parent=DR)
box("SpeedSwitch", (0.024, 0.020, 0.008), (-0.046, 0, AX + 0.038), m=M['accent'], b=0.003, parent=DR)
box("BeltHook", (0.006, 0.004, 0.034), (-0.050, 0.050, BZ + 0.030), rot=(0, R(-14), 0),
    m=M['darksteel'], b=0.002, parent=DR)
box("BeltHookLip", (0.014, 0.004, 0.006), (-0.056, 0.050, BZ + 0.048), m=M['darksteel'],
    b=0.002, parent=DR)

# ------------------------------------------------------------- gearbox + clutch collar
cyl("Gearbox", 0.0335, 0.044, (0.070, 0, AX), rot=(0, R(90), 0), v=40, m=M['grey'], parent=DR)
cyl("ClutchRing", 0.0345, 0.024, (0.086, 0, AX), rot=(0, R(90), 0), v=40, m=M['accent'], parent=DR)
for i in range(24):
    a = R(i * 15)
    box("ClutchRib", (0.020, 0.0030, 0.0040),
        (0.086, 0.0348 * math.sin(a), AX + 0.0348 * math.cos(a)), rot=(a, 0, 0),
        m=M['shell'], parent=DR)
torus("CollarEdge", 0.0336, 0.0022, (0.100, 0, AX), rot=(0, R(90), 0), m=M['darksteel'], parent=DR)
cyl("Spindle", 0.0210, 0.014, (0.106, 0, AX), rot=(0, R(90), 0), v=32, m=M['darksteel'], parent=DR)

# LED work light under the spindle
cyl("LEDHousing", 0.0075, 0.008, (0.086, 0, AX - 0.032), rot=(0, R(90), 0), v=20,
    m=M['grey'], parent=DR)
cyl("LED", 0.0050, 0.003, (0.091, 0, AX - 0.032), rot=(0, R(90), 0), v=18, m=M['led'], parent=DR)
light("WorkLight", 'SPOT', (0.20, 0.0, AX - 0.030), 3.0, size=0.004, color=(1.0, 0.96, 0.86),
      target=(0.42, 0.0, AX - 0.02))

# ------------------------------------------------------------- keyless chuck
CH = 0.113
cyl("ChuckBase", 0.0245, 0.012, (CH + 0.004, 0, AX), rot=(0, R(90), 0), v=36,
    m=M['darksteel'], parent=DR)
sleeve = cyl("ChuckSleeve", 0.0235, 0.034, (CH + 0.026, 0, AX), rot=(0, R(90), 0), v=36,
             m=M['steel'], parent=DR)
for i in range(20):
    a = R(i * 18)
    box("Knurl", (0.030, 0.0028, 0.0035),
        (CH + 0.026, 0.0238 * math.sin(a), AX + 0.0238 * math.cos(a)), rot=(a, 0, 0),
        m=M['darksteel'], parent=DR)
cone("ChuckNose", 0.0225, 0.0135, 0.016, (CH + 0.051, 0, AX), rot=(0, R(90), 0), v=36,
     m=M['steel'], parent=DR)
torus("ChuckBand", 0.0240, 0.0020, (CH + 0.010, 0, AX), rot=(0, R(90), 0), m=M['darksteel'], parent=DR)
# three jaws visible in the chuck mouth
for i in range(3):
    a = R(i * 120)
    box("Jaw%d" % i, (0.022, 0.0060, 0.0130),
        (CH + 0.055, 0.0080 * math.sin(a), AX + 0.0080 * math.cos(a)),
        rot=(a, R(4), 0), m=M['chrome'], b=0.001, parent=DR)

# ------------------------------------------------------------- twist drill bit
def twist_bit(name, r, length, twists=2.6, rings=18, seg=16, m=None):
    """Loft a two lobed cross-section along Z with progressive rotation."""
    me = bpy.data.meshes.new(name)
    bm = bmesh.new()
    vr = []
    for i in range(rings):
        t = i / (rings - 1.0)
        z = t * length
        phi = t * twists * 2.0 * math.pi
        ring = []
        for j in range(seg):
            a = 2.0 * math.pi * j / seg
            rr = r * (0.70 + 0.30 * math.cos(2.0 * (a - phi)))
            ring.append(bm.verts.new((rr * math.cos(a), rr * math.sin(a), z)))
        vr.append(ring)
    for i in range(rings - 1):
        a, b = vr[i], vr[i + 1]
        for j in range(seg):
            k = (j + 1) % seg
            bm.faces.new((a[j], a[k], b[k], b[j]))
    bm.faces.new(list(reversed(vr[0])))
    bm.faces.new(vr[-1])
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces[:])
    bm.to_mesh(me)
    bm.free()
    ob = bpy.data.objects.new(name, me)
    bpy.context.collection.objects.link(ob)
    put(ob, m)
    smooth(ob, 45)
    return ob


bit = twist_bit("BitFlutes", 0.0042, 0.062, m=M['chrome'])
bit.location = (CH + 0.062, 0, AX)
bit.rotation_euler = (0, R(90), 0)
bit.parent = DR
cyl("BitShank", 0.0042, 0.030, (CH + 0.050, 0, AX), rot=(0, R(90), 0), v=20,
    m=M['darksteel'], parent=DR)
cone("BitTip", 0.0042, 0.0002, 0.008, (CH + 0.128, 0, AX), rot=(0, R(90), 0), v=20,
     m=M['chrome'], parent=DR)

# ------------------------------------------------------------- stage
bpy.ops.mesh.primitive_plane_add(size=6.0, location=(0, 0, 0))
floor = bpy.context.active_object
floor.name = "Floor"
put(floor, M['floor'])
box("Sweep", (6.0, 0.05, 3.0), (0, 1.4, 1.5), m=mat("Sweep", (0.06, 0.065, 0.075), 0.9))

# ------------------------------------------------------------- lighting
light("Key", 'AREA', (-0.34, -0.42, 0.52), 90.0, size=0.55, color=(1.0, 0.98, 0.95),
      target=(0.02, 0.0, 0.13))
light("Rim", 'AREA', (0.46, 0.40, 0.30), 60.0, size=0.35, color=(0.72, 0.84, 1.0),
      target=(0.02, 0.0, 0.14), shape='RECTANGLE', sy=0.10)
light("Kick", 'AREA', (0.10, -0.55, 0.06), 26.0, size=0.40, color=(1.0, 0.88, 0.72),
      target=(0.03, 0.0, 0.10))
light("TopStrip", 'AREA', (-0.02, 0.05, 0.62), 40.0, size=0.80, color=(0.9, 0.93, 1.0),
      target=(0.0, 0.0, 0.12), shape='RECTANGLE', sy=0.08)

# ------------------------------------------------------------- low hero camera
cd = bpy.data.cameras.new("HeroCam")
cd.lens = 50.0
cd.clip_start = 0.01
cd.clip_end = 40.0
cd.dof.use_dof = True
cd.dof.aperture_fstop = 3.2
cd.dof.focus_distance = 0.46
cam = bpy.data.objects.new("HeroCam", cd)
cam.location = (0.30, -0.40, 0.034)
bpy.context.collection.objects.link(cam)
aim(cam, (-0.005, 0.0, 0.118))
cam.rotation_euler.rotate_axis('Z', R(1.5))
sc.camera = cam
