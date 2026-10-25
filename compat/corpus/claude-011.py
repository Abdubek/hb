"""claude-011 - Low-poly coffee maker with carafe and buttons (Blender 4.5 LTS)."""
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


def cyl(r, d, seg=24, loc=(0, 0, 0), rot=(0, 0, 0), r2=None, smooth=True, caps=True):
    bm = bmesh.new()
    bmesh.ops.create_cone(bm, cap_ends=caps, cap_tris=False, segments=seg,
                          radius1=r, radius2=(r if r2 is None else r2), depth=d)
    if smooth:
        for f in bm.faces:
            if abs(f.normal.z) < 0.9:
                f.smooth = True
    return _x(bm, loc, rot)


def tube(pts, r, seg=10, closed=False, smooth=True):
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
    world((0.05, 0.055, 0.07), 0.7)

    m_body = mat("BodyRed", (0.40, 0.045, 0.045), 0.34, coat=0.35)
    m_dark = mat("Graphite", (0.045, 0.045, 0.05), 0.42)
    m_panel = mat("PanelInset", (0.02, 0.02, 0.024), 0.30)
    m_steel = mat("Steel", (0.72, 0.73, 0.75), 0.22, metal=1.0)
    m_chrome = mat("Chrome", (0.88, 0.89, 0.9), 0.08, metal=1.0)
    m_glass = mat("CarafeGlass", (0.86, 0.9, 0.92), 0.06, alpha=0.22, trans=0.92)
    m_coffee = mat("Coffee", (0.085, 0.032, 0.014), 0.22)
    m_water = mat("Water", (0.36, 0.58, 0.72), 0.08, alpha=0.4, trans=0.85)
    m_led_r = mat("LedRed", (0.35, 0.02, 0.02), 0.3, emit=(1.0, 0.10, 0.05), estr=8.0)
    m_led_g = mat("LedGreen", (0.02, 0.3, 0.12), 0.3, emit=(0.15, 1.0, 0.35), estr=6.0)
    m_led_b = mat("LedBlue", (0.02, 0.1, 0.35), 0.3, emit=(0.15, 0.5, 1.0), estr=6.0)
    m_disp = mat("Display", (0.015, 0.03, 0.025), 0.15, emit=(0.15, 1.0, 0.6), estr=4.0)
    m_floor = mat("Counter", (0.15, 0.145, 0.15), 0.55)

    obj("Counter", box((4.0, 4.0, 0.04), (0, 0, -0.02)), m_floor)

    LP = dict(seg=12, smooth=False)          # low-poly, flat-shaded cylinders

    # ---------------------------------------------------------------- housing
    bm = bmesh.new()
    join(bm, box((0.22, 0.26, 0.030), (0, 0.0, 0.015), bevel=0.006, seg=1), 0)
    join(bm, box((0.22, 0.11, 0.280), (0, 0.075, 0.170), bevel=0.008, seg=2), 0)
    join(bm, box((0.22, 0.20, 0.045), (0, 0.030, 0.3325), bevel=0.008, seg=2), 0)
    join(bm, box((0.13, 0.11, 0.040), (-0.02, -0.020, 0.290), bevel=0.006, seg=1), 0)
    # recessed control panel and water-gauge housing on the front face
    join(bm, box((0.075, 0.010, 0.235), (0.085, 0.017, 0.165)), 1)
    join(bm, box((0.034, 0.014, 0.160), (-0.088, 0.014, 0.150), bevel=0.003), 1)
    for sx in (-1, 1):
        for sy in (-1, 1):
            join(bm, cyl(0.013, 0.008, seg=8, loc=(sx * 0.085, sy * 0.10, 0.002),
                         smooth=False), 1)
    housing = obj("CoffeeMaker_Body", bm, [m_body, m_dark])

    # water level behind the translucent gauge
    obj("WaterLevel", box((0.026, 0.006, 0.095), (-0.088, 0.014, 0.118)), m_water)

    # ------------------------------------------------------- brew group / plate
    bm = bmesh.new()
    join(bm, cyl(0.042, 0.008, loc=(-0.02, -0.020, 0.266), **LP), 0)
    join(bm, cyl(0.050, 0.046, r2=0.060, loc=(-0.02, -0.020, 0.243), **LP), 0)
    join(bm, cyl(0.060, 0.006, loc=(-0.02, -0.020, 0.222), **LP), 0)
    obj("BrewGroup", bm, m_dark)
    obj("WarmingPlate", cyl(0.078, 0.008, loc=(-0.02, -0.035, 0.034), **LP), m_steel)
    obj("PlateRing", cyl(0.086, 0.004, loc=(-0.02, -0.035, 0.031), **LP), m_dark)

    # -------------------------------------------------------------- controls
    bm = bmesh.new()
    for z in (0.100, 0.155, 0.210):
        join(bm, cyl(0.013, 0.010, seg=10, loc=(0.085, 0.016, z),
                     rot=(math.pi / 2, 0, 0), smooth=False), 0)
    obj("ButtonBodies", bm, m_dark)
    for z, m, nm in ((0.100, m_led_r, "Led_Power"), (0.155, m_led_g, "Led_Brew"),
                     (0.210, m_led_b, "Led_Strength")):
        obj(nm, cyl(0.0062, 0.004, seg=10, loc=(0.085, 0.0105, z),
                    rot=(math.pi / 2, 0, 0), smooth=False), m)
    obj("Display", box((0.055, 0.008, 0.026), (0.085, 0.0135, 0.278)), m_disp)
    obj("DisplayBezel", box((0.066, 0.010, 0.036), (0.085, 0.016, 0.278), bevel=0.003),
        m_dark)
    obj("PowerRocker", box((0.030, 0.012, 0.014), (0.070, -0.128, 0.018)), m_led_r)

    # ---------------------------------------------------------------- carafe
    bm = bmesh.new()
    join(bm, cyl(0.058, 0.132, r2=0.068, loc=(-0.02, -0.035, 0.104), **LP), 0)
    obj("Carafe_Glass", bm, m_glass)
    obj("Carafe_Coffee", cyl(0.054, 0.072, r2=0.061, loc=(-0.02, -0.035, 0.075), **LP),
        m_coffee)

    bm = bmesh.new()
    join(bm, cyl(0.071, 0.014, loc=(-0.02, -0.035, 0.168), **LP), 0)   # collar
    join(bm, cyl(0.066, 0.012, loc=(-0.02, -0.035, 0.181), **LP), 0)   # lid
    join(bm, cyl(0.016, 0.010, seg=8, loc=(-0.02, -0.035, 0.191), smooth=False), 0)
    join(bm, box((0.030, 0.034, 0.014), (-0.055, -0.085, 0.170), rot=(0.35, 0, -0.5)), 0)
    join(bm, tube([(0.010, -0.035, 0.163), (0.075, -0.035, 0.152),
                   (0.104, -0.035, 0.118), (0.100, -0.035, 0.082),
                   (0.058, -0.035, 0.062), (0.020, -0.035, 0.060)],
                  0.0075, seg=8, smooth=False), 0)
    obj("Carafe_Fittings", bm, m_dark)
    obj("LidHinge", cyl(0.006, 0.030, seg=8, loc=(0.028, 0.010, 0.176),
                        rot=(0, math.pi / 2, 0.5), smooth=False), m_chrome)

    # -------------------------------------------------------- camera and lights
    cam((0.44, -0.56, 0.34), (-0.015, -0.02, 0.165), lens=58.0, fstop=5.6)
    area("Key", (0.50, -0.62, 0.72), (0, 0, 0.18), 0.85, 150.0, (1.0, 0.97, 0.93))
    area("Fill", (-0.72, -0.42, 0.30), (0, 0, 0.15), 1.10, 45.0, (0.82, 0.88, 1.0))
    area("Rim", (-0.18, 0.70, 0.62), (0, 0.05, 0.22), 0.60, 80.0, (0.95, 0.95, 1.0))


main()
