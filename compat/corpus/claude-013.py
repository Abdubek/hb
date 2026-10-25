"""claude-013 - Record player with platter, tonearm and dust cover (Blender 4.5 LTS)."""
import bpy, bmesh, math
from mathutils import Vector, Matrix, Euler

TAU = 2.0 * math.pi


# --------------------------------------------------------------------- helpers
def reset():
    bpy.ops.wm.read_factory_settings(use_empty=True)
    s = bpy.context.scene
    s.render.engine = 'CYCLES'
    try:
        s.cycles.samples = 128
    except Exception:
        pass
    s.render.resolution_x, s.render.resolution_y = 1600, 1200
    return s


def world(col, strength):
    w = bpy.data.worlds.new("World")
    w.use_nodes = True
    bg = w.node_tree.nodes["Background"]
    bg.inputs[0].default_value = (col[0], col[1], col[2], 1.0)
    bg.inputs[1].default_value = strength
    bpy.context.scene.world = w


def mat(name, col, rough=0.5, metal=0.0, alpha=1.0, ior=1.45, trans=0.0, coat=0.0,
        emit=None, estr=0.0):
    m = bpy.data.materials.new(name)
    m.use_nodes = True
    b = m.node_tree.nodes["Principled BSDF"]
    b.inputs["Base Color"].default_value = (col[0], col[1], col[2], 1.0)
    b.inputs["Roughness"].default_value = rough
    b.inputs["Metallic"].default_value = metal
    for k, v in (("IOR", ior), ("Alpha", alpha), ("Transmission Weight", trans),
                 ("Coat Weight", coat)):
        if k in b.inputs:
            b.inputs[k].default_value = v
    if emit is not None and "Emission Color" in b.inputs:
        b.inputs["Emission Color"].default_value = (emit[0], emit[1], emit[2], 1.0)
        b.inputs["Emission Strength"].default_value = estr
    if alpha < 1.0 or trans > 0.0:
        for attr, val in (("blend_method", 'BLEND'), ("surface_render_method", 'BLENDED')):
            try:
                setattr(m, attr, val)
            except Exception:
                pass
    return m


def _x(bm, loc=(0, 0, 0), rot=(0, 0, 0), scale=(1, 1, 1)):
    M = (Matrix.Translation(Vector(loc))
         @ Euler(rot, 'XYZ').to_matrix().to_4x4()
         @ Matrix.Diagonal(Vector(scale)).to_4x4())
    for v in bm.verts:
        v.co = M @ v.co
    return bm


def box(size, loc=(0, 0, 0), rot=(0, 0, 0), bevel=0.0, seg=1):
    bm = bmesh.new()
    bmesh.ops.create_cube(bm, size=1.0)
    for v in bm.verts:
        v.co.x *= size[0]
        v.co.y *= size[1]
        v.co.z *= size[2]
    if bevel > 0.0:
        bmesh.ops.bevel(bm, geom=list(bm.verts) + list(bm.edges) + list(bm.faces),
                        offset=bevel, segments=seg, affect='EDGES', profile=0.5,
                        clamp_overlap=True)
    return _x(bm, loc, rot)


def cyl(r, d, seg=32, loc=(0, 0, 0), rot=(0, 0, 0), r2=None, smooth=True, caps=True):
    bm = bmesh.new()
    bmesh.ops.create_cone(bm, cap_ends=caps, cap_tris=False, segments=seg,
                          radius1=r, radius2=(r if r2 is None else r2), depth=d)
    if smooth:
        for f in bm.faces:
            if abs(f.normal.z) < 0.9:
                f.smooth = True
    return _x(bm, loc, rot)


def tube(pts, r, seg=12, closed=False, smooth=True):
    P = [Vector(p) for p in pts]
    n = len(P)
    T = []
    for i in range(n):
        if closed:
            t = P[(i + 1) % n] - P[(i - 1) % n]
        elif i == 0:
            t = P[1] - P[0]
        elif i == n - 1:
            t = P[-1] - P[-2]
        else:
            t = P[i + 1] - P[i - 1]
        T.append(t.normalized() if t.length > 1e-9 else Vector((0, 0, 1)))
    ref = Vector((0, 0, 1))
    if abs(T[0].dot(ref)) > 0.9:
        ref = Vector((1, 0, 0))
    nr = (ref - T[0] * T[0].dot(ref)).normalized()
    R = r if hasattr(r, '__len__') else [r] * n
    bm = bmesh.new()
    rings = []
    for i in range(n):
        t = T[i]
        nr = nr - t * t.dot(nr)
        if nr.length < 1e-7:
            ref = Vector((1, 0, 0)) if abs(t.x) < 0.9 else Vector((0, 1, 0))
            nr = ref - t * t.dot(ref)
        nr.normalize()
        bi = t.cross(nr).normalized()
        rings.append([bm.verts.new(P[i] + nr * (math.cos(TAU * k / seg) * R[i])
                                   + bi * (math.sin(TAU * k / seg) * R[i]))
                      for k in range(seg)])
    for i in range(n if closed else n - 1):
        a, b2 = rings[i], rings[(i + 1) % n]
        for k in range(seg):
            k2 = (k + 1) % seg
            f = bm.faces.new([a[k], a[k2], b2[k2], b2[k]])
            f.smooth = smooth
    if not closed:
        bm.faces.new(rings[0])
        bm.faces.new(rings[-1])
    bmesh.ops.recalc_face_normals(bm, faces=list(bm.faces))
    return bm


def aim(direction):
    """Euler that points a Z-aligned primitive along `direction`."""
    return Vector(direction).to_track_quat('Z', 'Y').to_euler()


def join(bm, tmp, mi=0):
    tmp.verts.index_update()
    vs = [bm.verts.new(v.co) for v in tmp.verts]
    for f in tmp.faces:
        try:
            nf = bm.faces.new([vs[v.index] for v in f.verts])
        except ValueError:
            continue
        nf.smooth = f.smooth
        nf.material_index = mi
    tmp.free()


def obj(name, bm, mats, loc=(0, 0, 0), rot=(0, 0, 0)):
    me = bpy.data.meshes.new(name)
    bm.normal_update()
    bm.to_mesh(me)
    bm.free()
    me.validate()
    for m in (mats if isinstance(mats, (list, tuple)) else [mats]):
        me.materials.append(m)
    o = bpy.data.objects.new(name, me)
    o.location = loc
    o.rotation_euler = rot
    bpy.context.scene.collection.objects.link(o)
    return o


def cam(loc, tgt, lens=50.0, fstop=None):
    cd = bpy.data.cameras.new("Camera")
    cd.lens = lens
    c = bpy.data.objects.new("Camera", cd)
    c.location = loc
    d = Vector(tgt) - Vector(loc)
    c.rotation_euler = d.to_track_quat('-Z', 'Y').to_euler()
    if fstop:
        cd.dof.use_dof = True
        cd.dof.focus_distance = d.length
        cd.dof.aperture_fstop = fstop
    bpy.context.scene.collection.objects.link(c)
    bpy.context.scene.camera = c
    return c


def area(name, loc, tgt, size, energy, col=(1, 1, 1), size_y=None):
    ld = bpy.data.lights.new(name, 'AREA')
    ld.energy = energy
    ld.size = size
    ld.color = col
    if size_y:
        ld.shape = 'RECTANGLE'
        ld.size_y = size_y
    o = bpy.data.objects.new(name, ld)
    o.location = loc
    o.rotation_euler = (Vector(tgt) - Vector(loc)).to_track_quat('-Z', 'Y').to_euler()
    bpy.context.scene.collection.objects.link(o)
    return o


# ----------------------------------------------------------------------- scene
def main():
    reset()
    world((0.035, 0.038, 0.045), 0.7)

    m_wood = mat("Walnut", (0.115, 0.055, 0.028), 0.35, coat=0.3)
    m_black = mat("BlackPlastic", (0.030, 0.030, 0.033), 0.40)
    m_alu = mat("Aluminium", (0.70, 0.71, 0.72), 0.22, metal=1.0)
    m_chrome = mat("Chrome", (0.88, 0.89, 0.90), 0.07, metal=1.0)
    m_felt = mat("Slipmat", (0.055, 0.055, 0.06), 0.85)
    m_vinyl = mat("Vinyl", (0.014, 0.014, 0.016), 0.22, coat=0.25)
    m_groove = mat("Grooves", (0.020, 0.020, 0.023), 0.38)
    m_label = mat("Label", (0.72, 0.20, 0.12), 0.55)
    m_glass = mat("SmokeAcrylic", (0.30, 0.30, 0.34), 0.05, alpha=0.18, trans=0.9,
                  ior=1.49)
    m_red = mat("LedRed", (0.3, 0.02, 0.02), 0.3, emit=(1.0, 0.10, 0.06), estr=7.0)
    m_green = mat("LedGreen", (0.02, 0.3, 0.1), 0.3, emit=(0.2, 1.0, 0.35), estr=5.0)
    m_floor = mat("Shelf", (0.13, 0.13, 0.14), 0.5)

    obj("Shelf", box((4.0, 4.0, 0.04), (0, 0, -0.02)), m_floor)

    PT = 0.075                      # plinth top

    # ------------------------------------------------------------------ plinth
    bm = bmesh.new()
    join(bm, box((0.46, 0.37, 0.055), (0, 0, 0.0475), bevel=0.006, seg=2), 0)
    obj("Plinth", bm, m_wood)

    bm = bmesh.new()
    for sx in (-1, 1):
        for sy in (-1, 1):
            join(bm, cyl(0.019, 0.020, seg=20, loc=(sx * 0.19, sy * 0.145, 0.010)), 0)
    for sx in (-1, 1):
        join(bm, box((0.032, 0.022, 0.014), (sx * 0.14, 0.176, 0.080), bevel=0.003), 0)
    obj("Feet_Hinges", bm, m_black)

    # --------------------------------------------------------- platter + record
    bm = bmesh.new()
    join(bm, cyl(0.152, 0.020, seg=64, loc=(0, 0, PT + 0.010)), 0)
    join(bm, cyl(0.140, 0.006, seg=64, loc=(0, 0, PT - 0.003)), 0)
    obj("Platter", bm, m_alu)
    obj("Slipmat", cyl(0.1485, 0.0022, seg=64, loc=(0, 0, PT + 0.0211)), m_felt)

    obj("Record", cyl(0.1495, 0.0030, seg=64, loc=(0, 0, PT + 0.0237)), m_vinyl)
    obj("RecordGrooves", cyl(0.1425, 0.0034, seg=64, loc=(0, 0, PT + 0.0237)), m_groove)
    obj("RecordLabel", cyl(0.0500, 0.0038, seg=48, loc=(0, 0, PT + 0.0238)), m_label)
    obj("Spindle", cyl(0.0036, 0.034, seg=16, loc=(0, 0, PT + 0.036)), m_chrome)

    REC_TOP = PT + 0.0252           # playing surface

    # ---------------------------------------------------------------- tonearm
    PIV = Vector((0.175, 0.125, 0.132))
    bm = bmesh.new()
    join(bm, cyl(0.046, 0.006, seg=40, loc=(0.175, 0.125, PT + 0.003)), 0)
    join(bm, cyl(0.019, 0.048, seg=28, loc=(0.175, 0.125, PT + 0.024)), 0)
    join(bm, cyl(0.014, 0.016, seg=24, loc=(0.175, 0.125, PT + 0.052)), 0)
    join(bm, box((0.026, 0.030, 0.020), (0.175, 0.125, 0.132), rot=(0, 0, -0.68),
                 bevel=0.003), 0)
    obj("TonearmBase", bm, m_black)

    arm_pts = [(0.175, 0.125, 0.130), (0.140, 0.083, 0.1288), (0.108, 0.041, 0.1272),
               (0.082, -0.002, 0.1250), (0.066, -0.032, 0.1222),
               (0.058, -0.050, 0.1195)]
    obj("ArmTube", tube(arm_pts, 0.0048, seg=14), m_chrome)

    cw_dir = Vector((0.032, 0.040, 0.002))
    bm = bmesh.new()
    join(bm, tube([(0.175, 0.125, 0.130), (0.213, 0.172, 0.132)], 0.0038, seg=12), 0)
    obj("CounterStub", bm, m_chrome)
    obj("Counterweight", cyl(0.0175, 0.030, seg=28, loc=(0.212, 0.171, 0.132)),
        m_black, rot=tuple(aim(cw_dir)))

    bm = bmesh.new()
    join(bm, box((0.024, 0.032, 0.013), (0.056, -0.055, 0.1145), rot=(0, 0, -0.68),
                 bevel=0.002), 0)
    join(bm, box((0.017, 0.024, 0.011), (0.052, -0.062, 0.1055), rot=(0, 0, -0.68),
                 bevel=0.002), 0)
    join(bm, box((0.004, 0.016, 0.010), (0.070, -0.048, 0.1195), rot=(0, 0, -0.68)), 0)
    obj("Headshell", bm, m_black)
    obj("Stylus", cyl(0.0010, 0.007, seg=10, r2=0.0002,
                      loc=(0.050, -0.066, REC_TOP + 0.0035)), m_chrome)

    bm = bmesh.new()
    join(bm, cyl(0.0065, 0.026, seg=18, loc=(0.203, 0.058, PT + 0.013)), 0)
    join(bm, box((0.016, 0.014, 0.008), (0.203, 0.058, PT + 0.030), bevel=0.002), 0)
    join(bm, cyl(0.010, 0.012, seg=20, loc=(0.148, 0.168, PT + 0.006)), 0)
    obj("ArmRest_AntiSkate", bm, m_black)

    # --------------------------------------------------------------- controls
    bm = bmesh.new()
    join(bm, cyl(0.017, 0.007, seg=28, loc=(-0.175, -0.122, PT + 0.002)), 0)
    join(bm, cyl(0.013, 0.006, seg=24, loc=(-0.178, -0.058, PT + 0.002)), 0)
    join(bm, cyl(0.013, 0.006, seg=24, loc=(-0.140, -0.058, PT + 0.002)), 0)
    join(bm, box((0.024, 0.120, 0.006), (0.192, -0.045, PT - 0.001)), 0)
    join(bm, box((0.030, 0.018, 0.010), (0.192, -0.020, PT + 0.004), bevel=0.002), 0)
    join(bm, box((0.034, 0.014, 0.012), (-0.205, -0.176, 0.050), bevel=0.002), 0)
    obj("Controls", bm, m_black)

    obj("StartLed", cyl(0.0075, 0.005, seg=20, loc=(-0.175, -0.122, PT + 0.004)), m_green)
    bm = bmesh.new()
    join(bm, cyl(0.0055, 0.005, seg=16, loc=(-0.178, -0.058, PT + 0.004)), 0)
    join(bm, cyl(0.0055, 0.005, seg=16, loc=(-0.140, -0.058, PT + 0.004)), 0)
    for i in range(5):
        join(bm, box((0.004, 0.004, 0.003), (-0.100 + i * 0.014, -0.150, PT + 0.001)), 0)
    obj("Indicators", bm, m_red)

    # -------------------------------------------------------------- dust cover
    bm = bmesh.new()
    join(bm, box((0.470, 0.400, 0.006), (0, -0.200, 0.0), bevel=0.002), 0)
    join(bm, box((0.470, 0.006, 0.115), (0, -0.397, -0.0565), bevel=0.002), 0)
    for sx in (-1, 1):
        join(bm, box((0.006, 0.400, 0.115), (sx * 0.232, -0.200, -0.0565), bevel=0.002), 0)
    obj("DustCover", bm, m_glass, loc=(0, 0.180, 0.086),
        rot=(math.radians(-56.0), 0.0, 0.0))

    # -------------------------------------------------------- camera and lights
    cam((0.52, -0.66, 0.42), (0.0, -0.01, 0.115), lens=52.0, fstop=4.0)
    area("Key", (0.60, -0.70, 0.95), (0, 0, 0.12), 1.10, 220.0, (1.0, 0.97, 0.92))
    area("Fill", (-0.85, -0.50, 0.40), (0, 0, 0.10), 1.40, 60.0, (0.80, 0.86, 1.0))
    area("Rim", (-0.20, 0.85, 0.70), (0, 0.06, 0.14), 0.70, 110.0, (0.95, 0.96, 1.0))


main()
