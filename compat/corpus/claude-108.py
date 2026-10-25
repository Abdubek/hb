"""claude-108 - Top down flat lay: pen, notebook, glasses and a small camera on a desktop."""
import bpy, bmesh, math
from mathutils import Vector

R = math.radians

# ------------------------------------------------------------------ helpers
def scene(res=(1600, 1600)):
    bpy.ops.wm.read_factory_settings(use_empty=True)
    sc = bpy.context.scene
    sc.render.resolution_x, sc.render.resolution_y = res
    try:
        sc.render.engine = 'CYCLES'
        sc.cycles.samples = 160
    except Exception:
        pass
    w = bpy.data.worlds.new("World")
    sc.world = w
    w.use_nodes = True
    bg = w.node_tree.nodes["Background"]
    bg.inputs[0].default_value = (0.34, 0.36, 0.40, 1.0)
    bg.inputs[1].default_value = 0.25
    return sc


def mat(name, c, rough=0.5, metal=0.0, trans=0.0, emit=None, es=0.0):
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


def cyl(name, r, d, loc, rot=(0, 0, 0), v=32, m=None, parent=None):
    bpy.ops.mesh.primitive_cylinder_add(radius=r, depth=d, vertices=v, location=loc, rotation=rot)
    ob = bpy.context.active_object
    ob.name = name
    put(ob, m)
    smooth(ob)
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


def torus(name, R1, R2, loc, rot=(0, 0, 0), ms=48, mn=14, m=None, parent=None):
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
    ob.empty_display_size = 0.03
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
    ob = bpy.data.objects.new(name, l)
    ob.location = loc
    bpy.context.collection.objects.link(ob)
    if target is not None:
        aim(ob, target)
    return ob


# ------------------------------------------------------------------ scene
sc = scene()

M = {
    'desk': mat("Walnut", (0.20, 0.115, 0.062), 0.34),
    'cover': mat("NotebookCover", (0.10, 0.13, 0.16), 0.52),
    'paper': mat("Paper", (0.93, 0.92, 0.88), 0.68),
    'elastic': mat("Elastic", (0.06, 0.07, 0.09), 0.80),
    'ribbon': mat("Ribbon", (0.62, 0.18, 0.16), 0.70),
    'penbody': mat("PenBody", (0.08, 0.09, 0.11), 0.28),
    'grip': mat("PenGrip", (0.04, 0.04, 0.05), 0.75),
    'chrome': mat("Chrome", (0.80, 0.81, 0.83), 0.16, 1.0),
    'brass': mat("Brass", (0.74, 0.60, 0.32), 0.24, 1.0),
    'frame': mat("Tortoise", (0.19, 0.10, 0.05), 0.24),
    'lens': mat("Lens", (0.90, 0.94, 0.96), 0.02, trans=1.0),
    'body': mat("CamBody", (0.055, 0.058, 0.062), 0.44),
    'leather': mat("CamLeather", (0.10, 0.10, 0.11), 0.78),
    'silver': mat("CamTop", (0.70, 0.71, 0.73), 0.30, 1.0),
    'glassdark': mat("FrontGlass", (0.02, 0.03, 0.05), 0.05, 0.4),
    'red': mat("RedDot", (0.62, 0.09, 0.08), 0.35),
}

# desktop
box("Desk", (1.30, 1.00, 0.05), (0, 0, -0.025), m=M['desk'])
for i in range(4):
    box("Grain%d" % i, (1.30, 0.004, 0.002), (0, -0.34 + i * 0.23, 0.0005),
        m=mat("Grain%d" % i, (0.15, 0.085, 0.05), 0.42))

# ------------------------------------------------------------- notebook (A5)
NB = empty("Notebook", (-0.135, 0.028, 0.0), (0, 0, R(6)))
nb = box("NbCover", (0.150, 0.212, 0.016), (0, 0, 0.008), m=M['cover'], b=0.004, parent=NB)
box("NbPages", (0.142, 0.204, 0.012), (0.002, 0, 0.007), m=M['paper'], b=0.0012, parent=NB)
box("NbCoverTop", (0.150, 0.212, 0.0022), (0, 0, 0.0161), m=M['cover'], b=0.0008, parent=NB)
box("NbSpine", (0.012, 0.212, 0.017), (-0.069, 0, 0.0085), m=M['cover'], b=0.005, parent=NB)
box("NbElastic", (0.0055, 0.222, 0.018), (0.052, 0, 0.0085), m=M['elastic'], b=0.0015, parent=NB)
box("NbRibbon", (0.008, 0.05, 0.0012), (0.02, -0.128, 0.0012), rot=(0, 0, R(-8)),
    m=M['ribbon'], parent=NB)
box("NbLabel", (0.052, 0.030, 0.0008), (0.0, 0.055, 0.0172), m=M['paper'], b=0.0004, parent=NB)

# ------------------------------------------------------------- pen
PEN = empty("Pen", (0.012, 0.075, 0.0), (0, 0, R(-64)))
PL = 0.140
cyl("PenBarrel", 0.0053, PL * 0.62, (0, 0.018, 0.0053), rot=(R(90), 0, 0), v=28,
    m=M['penbody'], parent=PEN)
cone("PenTaper", 0.0053, 0.0030, 0.024, (0, -0.055, 0.0053), rot=(R(-90), 0, 0), v=28,
     m=M['grip'], parent=PEN)
cone("PenTip", 0.0030, 0.0009, 0.010, (0, -0.072, 0.0053), rot=(R(-90), 0, 0), v=20,
     m=M['chrome'], parent=PEN)
cyl("PenGrip", 0.0056, 0.026, (0, -0.030, 0.0053), rot=(R(90), 0, 0), v=28,
    m=M['grip'], parent=PEN)
for i, yy in enumerate((-0.043, 0.049)):
    cyl("PenRing%d" % i, 0.0058, 0.004, (0, yy, 0.0053), rot=(R(90), 0, 0), v=28,
        m=M['brass'], parent=PEN)
cyl("PenCapEnd", 0.0050, 0.012, (0, 0.062, 0.0053), rot=(R(90), 0, 0), v=28,
    m=M['brass'], parent=PEN)
box("PenClip", (0.0032, 0.034, 0.0020), (0.0, 0.046, 0.0112), m=M['brass'], b=0.0008, parent=PEN)
box("PenClipFoot", (0.0032, 0.006, 0.0055), (0.0, 0.062, 0.0088), m=M['brass'], b=0.0008, parent=PEN)

# ------------------------------------------------------------- glasses (folded)
GL = empty("Glasses", (0.088, -0.085, 0.0), (0, 0, R(-14)))
for sx in (-0.049, 0.049):
    torus("Rim", 0.0245, 0.0032, (sx, 0, 0.0035), m=M['frame'], parent=GL)
    lens = cyl("Lens", 0.0235, 0.0016, (sx, 0, 0.0035), v=40, m=M['lens'], parent=GL)
    lens.scale = (1.0, 0.82, 1.0)
    torus("Rim", 0.0245, 0.0032, (sx, 0, 0.0035), m=M['frame'], parent=GL).scale = (1.0, 0.84, 1.0)
for ob in GL.children:
    if ob.name.startswith("Rim"):
        ob.scale = (1.0, 0.84, 1.0)
box("Bridge", (0.020, 0.0045, 0.0035), (0, 0.013, 0.0035), m=M['frame'], b=0.0012, parent=GL)
box("BridgeBar", (0.022, 0.0035, 0.0030), (0, 0.006, 0.0035), m=M['frame'], b=0.0010, parent=GL)
for sx in (-1, 1):
    box("Hinge", (0.008, 0.0060, 0.0040), (sx * 0.0715, 0.008, 0.0040), m=M['brass'], b=0.0010, parent=GL)
    # temples folded back across the lenses
    t = box("Temple", (0.098, 0.0035, 0.0028), (sx * 0.028, -0.004, 0.0088),
            rot=(0, 0, R(-9 * sx)), m=M['frame'], b=0.0010, parent=GL)
    box("TempleTip", (0.020, 0.0042, 0.0034), (sx * -0.024, -0.012 * sx - 0.004, 0.0088),
        rot=(0, 0, R(-9 * sx)), m=M['elastic'], b=0.0014, parent=GL)
    box("NosePad", (0.0055, 0.010, 0.0025), (sx * 0.026, 0.010, 0.0030),
        rot=(0, 0, R(24 * sx)), m=M['lens'], b=0.0008, parent=GL)

# ------------------------------------------------------------- compact camera
CA = empty("Camera_Prop", (0.098, 0.098, 0.0), (0, 0, R(-26)))
BW, BD, BH = 0.118, 0.064, 0.040
box("CamBody", (BW, BD, BH), (0, 0, BH / 2), m=M['body'], b=0.005, parent=CA)
box("CamLeather", (BW + 0.001, BD - 0.014, BH - 0.014), (0, 0, BH / 2 - 0.002),
    m=M['leather'], b=0.003, parent=CA)
box("CamTopPlate", (BW, BD, 0.008), (0, 0, BH - 0.002), m=M['silver'], b=0.0025, parent=CA)
box("CamBasePlate", (BW, BD, 0.005), (0, 0, 0.0025), m=M['silver'], b=0.002, parent=CA)
grip = box("CamGrip", (0.020, BD, BH - 0.006), (BW / 2 - 0.008, 0, BH / 2 - 0.002),
           m=M['leather'], b=0.008, parent=CA)
# viewfinder hump + hot shoe
box("CamHump", (0.032, 0.030, 0.014), (-0.020, 0.008, BH + 0.006), m=M['silver'], b=0.003, parent=CA)
box("HotShoe", (0.020, 0.017, 0.004), (-0.020, 0.008, BH + 0.014), m=M['silver'], b=0.0008, parent=CA)
box("ShoeRail", (0.024, 0.003, 0.0026), (-0.020, 0.008, BH + 0.0155), m=M['chrome'], parent=CA)
# top controls
cyl("ModeDial", 0.0125, 0.008, (0.030, 0.014, BH + 0.004), v=28, m=M['silver'], parent=CA)
for i in range(10):
    a = R(i * 36)
    box("DialNotch%d" % i, (0.0016, 0.0035, 0.008),
        (0.030 + 0.0122 * math.cos(a), 0.014 + 0.0122 * math.sin(a), BH + 0.004),
        rot=(0, 0, a), m=M['body'], parent=CA)
cyl("Shutter", 0.0058, 0.005, (0.030, -0.014, BH + 0.0035), v=24, m=M['silver'], parent=CA)
cyl("ShutterInner", 0.0032, 0.006, (0.030, -0.014, BH + 0.004), v=20, m=M['chrome'], parent=CA)
cyl("OnOff", 0.0090, 0.004, (0.046, 0.000, BH + 0.002), v=24, m=M['body'], parent=CA)
box("ExpDial", (0.008, 0.008, 0.004), (0.010, -0.020, BH + 0.003), m=M['silver'], b=0.001, parent=CA)
# lens assembly pointing -Y so the barrel reads clearly from above
LY = -BD / 2
cyl("LensMount", 0.0230, 0.008, (-0.004, LY - 0.003, 0.019), rot=(R(90), 0, 0), v=40,
    m=M['silver'], parent=CA)
cyl("LensBarrel", 0.0205, 0.026, (-0.004, LY - 0.018, 0.019), rot=(R(90), 0, 0), v=40,
    m=M['body'], parent=CA)
for i in range(3):
    torus("LensRib%d" % i, 0.0212, 0.0020, (-0.004, LY - 0.010 - i * 0.008, 0.019),
          rot=(R(90), 0, 0), ms=40, mn=10, m=M['chrome'], parent=CA)
cyl("LensFront", 0.0195, 0.006, (-0.004, LY - 0.032, 0.019), rot=(R(90), 0, 0), v=40,
    m=M['silver'], parent=CA)
cyl("FrontGlass", 0.0160, 0.004, (-0.004, LY - 0.034, 0.019), rot=(R(90), 0, 0), v=40,
    m=M['glassdark'], parent=CA)
cyl("RedDot", 0.0040, 0.0035, (0.040, LY + 0.001, 0.030), rot=(R(90), 0, 0), v=20,
    m=M['red'], parent=CA)
for sx in (-1, 1):
    box("StrapLug", (0.006, 0.010, 0.007), (sx * (BW / 2 - 0.004), 0.0, BH - 0.004),
        m=M['chrome'], b=0.0015, parent=CA)
    torus("StrapRing", 0.0045, 0.0011, (sx * (BW / 2 + 0.002), 0.0, BH - 0.004),
          rot=(0, R(90), 0), ms=24, mn=8, m=M['chrome'], parent=CA)

# ------------------------------------------------------------- lighting
light("Softbox", 'AREA', (-0.22, 0.30, 0.90), 240.0, size=1.10, color=(1.0, 0.98, 0.95),
      target=(0.0, 0.0, 0.0))
light("Fill", 'AREA', (0.42, -0.34, 0.52), 45.0, size=0.60, color=(0.92, 0.95, 1.0),
      target=(0.05, 0.02, 0.0))
light("Kicker", 'AREA', (0.34, 0.36, 0.30), 22.0, size=0.30, color=(1.0, 0.92, 0.82),
      target=(0.10, 0.09, 0.02))

# ------------------------------------------------------------- top down camera
cd = bpy.data.cameras.new("FlatLayCam")
cd.lens = 50.0
cd.clip_start = 0.01
cd.clip_end = 20.0
cam = bpy.data.objects.new("FlatLayCam", cd)
cam.location = (0.004, 0.004, 0.86)
cam.rotation_euler = (0.0, 0.0, R(-4.0))       # looking straight down -Z
bpy.context.collection.objects.link(cam)
sc.camera = cam
