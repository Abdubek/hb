"""claude-012 - Camera body with lens and top controls (Blender 4.5 LTS)."""
import bpy, bmesh, math
from mathutils import Vector, Matrix, Euler

TAU = 2.0 * math.pi
RX = (math.pi / 2, 0.0, 0.0)          # rotate a Z-cylinder onto the -Y lens axis


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


def ball(r, loc=(0, 0, 0), sub=3, scale=(1, 1, 1)):
    bm = bmesh.new()
    bmesh.ops.create_icosphere(bm, subdivisions=sub, radius=r)
    for f in bm.faces:
        f.smooth = True
    return _x(bm, loc, (0, 0, 0), scale)


def prism(bw, bd, tw, td, h, loc=(0, 0, 0), rot=(0, 0, 0)):
    bm = bmesh.new()
    q = ((-1, -1), (1, -1), (1, 1), (-1, 1))
    b = [bm.verts.new((x * bw / 2, y * bd / 2, -h / 2)) for x, y in q]
    t = [bm.verts.new((x * tw / 2, y * td / 2, h / 2)) for x, y in q]
    bm.faces.new(b)
    bm.faces.new(t)
    for i in range(4):
        j = (i + 1) % 4
        bm.faces.new([b[i], b[j], t[j], t[i]])
    bmesh.ops.recalc_face_normals(bm, faces=list(bm.faces))
    return _x(bm, loc, rot)


def knurl(r, d, seg=72, bump=0.0012, loc=(0, 0, 0), rot=(0, 0, 0)):
    """Cylinder with alternating radii - a ribbed grip ring."""
    bm = bmesh.new()
    lo, hi = [], []
    for k in range(seg):
        a = TAU * k / seg
        rr = r + (bump if k % 2 else 0.0)
        lo.append(bm.verts.new((math.cos(a) * rr, math.sin(a) * rr, -d / 2)))
        hi.append(bm.verts.new((math.cos(a) * rr, math.sin(a) * rr, d / 2)))
    for k in range(seg):
        k2 = (k + 1) % seg
        bm.faces.new([lo[k], lo[k2], hi[k2], hi[k]])
    bm.faces.new(lo)
    bm.faces.new(hi)
    bmesh.ops.recalc_face_normals(bm, faces=list(bm.faces))
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
        rings.append([bm.verts.new(P[i] + nr * (math.cos(TAU * k / seg) * r)
                                   + bi * (math.sin(TAU * k / seg) * r))
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


def arc(center, radius, a0, a1, n, plane='XZ'):
    c = Vector(center)
    out = []
    for i in range(n):
        a = a0 + (a1 - a0) * i / (n - 1)
        if plane == 'XZ':
            out.append(c + Vector((math.cos(a) * radius, 0.0, math.sin(a) * radius)))
        elif plane == 'YZ':
            out.append(c + Vector((0.0, math.cos(a) * radius, math.sin(a) * radius)))
        else:
            out.append(c + Vector((math.cos(a) * radius, math.sin(a) * radius, 0.0)))
    return out


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
    world((0.03, 0.033, 0.04), 0.6)

    m_body = mat("Magnesium", (0.055, 0.056, 0.06), 0.38, coat=0.15)
    m_rub = mat("Leatherette", (0.022, 0.022, 0.025), 0.72)
    m_barrel = mat("LensBarrel", (0.04, 0.04, 0.043), 0.32, coat=0.2)
    m_metal = mat("Chrome", (0.86, 0.87, 0.89), 0.10, metal=1.0)
    m_dark = mat("DarkMetal", (0.10, 0.10, 0.11), 0.28, metal=1.0)
    m_glass = mat("FrontGlass", (0.55, 0.72, 0.85), 0.02, alpha=0.35, trans=0.9, ior=1.55)
    m_cav = mat("LensCavity", (0.005, 0.005, 0.006), 0.6)
    m_red = mat("RedRing", (0.55, 0.03, 0.03), 0.30, coat=0.4)
    m_lcd = mat("LCD", (0.01, 0.012, 0.016), 0.08, emit=(0.10, 0.16, 0.30), estr=1.4)
    m_top = mat("TopLCD", (0.35, 0.38, 0.34), 0.25, emit=(0.5, 0.55, 0.45), estr=0.6)
    m_floor = mat("Sweep", (0.10, 0.10, 0.115), 0.45)

    obj("Sweep", box((3.0, 3.0, 0.04), (0, 0, -0.02)), m_floor)

    ZC = 0.050                       # optical axis height

    # ------------------------------------------------------------------- body
    bm = bmesh.new()
    join(bm, box((0.130, 0.052, 0.082), (0, 0, 0.045), bevel=0.009, seg=3), 0)
    join(bm, box((0.132, 0.054, 0.014), (0, 0, 0.089), bevel=0.004, seg=2), 0)
    join(bm, prism(0.042, 0.046, 0.030, 0.040, 0.022, (0, 0.004, 0.106)), 0)
    join(bm, box((0.030, 0.056, 0.076), (0.072, -0.002, 0.044), bevel=0.013, seg=3), 1)
    join(bm, box((0.134, 0.0555, 0.038), (0, 0, 0.043), bevel=0.004, seg=2), 1)
    join(bm, box((0.026, 0.012, 0.020), (0, 0.031, 0.104), bevel=0.005, seg=2), 1)
    join(bm, box((0.120, 0.048, 0.005), (0, 0, 0.0035), bevel=0.002), 0)
    body = obj("CameraBody", bm, [m_body, m_rub])

    # ------------------------------------------------------- mount + lens stack
    bm = bmesh.new()
    join(bm, cyl(0.031, 0.010, loc=(0, -0.029, ZC), rot=RX, seg=48), 0)
    join(bm, cyl(0.024, 0.020, loc=(0, -0.044, ZC), rot=RX, seg=48), 0)
    join(bm, cyl(0.0245, 0.012, loc=(0, -0.084, ZC), rot=RX, seg=48), 0)
    join(bm, cyl(0.0272, 0.010, loc=(0, -0.121, ZC), rot=RX, seg=48), 0)
    join(bm, knurl(0.0265, 0.024, loc=(0, -0.066, ZC), rot=RX), 0)
    join(bm, knurl(0.0270, 0.026, loc=(0, -0.103, ZC), rot=RX), 0)
    obj("LensBarrel", bm, m_barrel)

    bm = bmesh.new()
    join(bm, cyl(0.0265, 0.005, loc=(0, -0.0345, ZC), rot=RX, seg=48), 0)
    join(bm, cyl(0.0292, 0.0035, loc=(0, -0.1275, ZC), rot=RX, seg=48), 0)
    obj("LensMountRing", bm, m_metal)
    obj("LensAccentRing", cyl(0.0288, 0.0028, loc=(0, -0.1130, ZC), rot=RX, seg=48), m_red)
    obj("LensCavity", cyl(0.0235, 0.024, loc=(0, -0.116, ZC), rot=RX, seg=48), m_cav)
    obj("FrontElement", ball(0.0255, (0, -0.1265, ZC), sub=3, scale=(1.0, 0.42, 1.0)),
        m_glass)

    # --------------------------------------------------------- top controls
    bm = bmesh.new()
    join(bm, knurl(0.0140, 0.0095, loc=(0.045, 0.013, 0.1005)), 0)
    join(bm, knurl(0.0125, 0.0085, loc=(-0.046, 0.011, 0.1005)), 0)
    join(bm, cyl(0.0115, 0.0045, loc=(0.045, -0.016, 0.0975), seg=32), 0)
    join(bm, box((0.010, 0.004, 0.004), (0.045, 0.013, 0.1055)), 0)
    join(bm, box((0.014, 0.006, 0.005), (0.020, 0.0225, 0.0965), rot=(0, 0, 0.35)), 0)
    obj("TopDials", bm, m_dark)

    bm = bmesh.new()
    join(bm, cyl(0.0145, 0.0022, loc=(0.045, 0.013, 0.1058), seg=32), 0)
    join(bm, cyl(0.0075, 0.0055, loc=(0.045, -0.016, 0.0995), seg=24), 0)
    join(bm, cyl(0.0050, 0.0035, loc=(-0.014, -0.017, 0.0975), seg=20), 0)
    join(bm, cyl(0.0050, 0.0035, loc=(-0.001, -0.017, 0.0975), seg=20), 0)
    obj("TopButtons", bm, m_metal)

    bm = bmesh.new()
    join(bm, box((0.028, 0.024, 0.003), (0, 0.004, 0.1185)), 0)
    for sx in (-1, 1):
        join(bm, box((0.0035, 0.024, 0.005), (sx * 0.0128, 0.004, 0.1205)), 0)
    join(bm, box((0.014, 0.008, 0.002), (0, -0.002, 0.1205)), 0)
    obj("HotShoe", bm, m_dark)

    obj("TopLCD", box((0.028, 0.017, 0.0015), (-0.020, -0.018, 0.0965)), m_top)

    # ----------------------------------------------------------- back details
    obj("RearLCD", box((0.076, 0.0035, 0.052), (-0.010, 0.0275, 0.048)), m_lcd)
    obj("RearLCDBezel", box((0.084, 0.006, 0.060), (-0.010, 0.0265, 0.048), bevel=0.002),
        m_body)

    bm = bmesh.new()
    for sx in (-1, 1):
        join(bm, box((0.008, 0.010, 0.006), (sx * 0.0665, 0.006, 0.078)), 0)
        pts = arc((sx * 0.072, 0.006, 0.083), 0.007, -0.6, math.pi + 0.6, 10, 'XZ')
        join(bm, tube(pts, 0.0018, seg=8), 0)
    join(bm, cyl(0.006, 0.005, loc=(0.038, -0.030, 0.058), rot=RX, seg=20), 0)
    join(bm, cyl(0.0055, 0.005, loc=(0, 0, 0.0035), seg=20), 0)
    obj("BodyFittings", bm, m_dark)

    # -------------------------------------------------------- camera and lights
    cam((0.30, -0.34, 0.20), (-0.005, -0.045, 0.058), lens=70.0, fstop=3.5)
    area("Key", (0.34, -0.40, 0.55), (0, -0.03, 0.06), 0.55, 90.0, (1.0, 0.98, 0.95))
    area("Fill", (-0.45, -0.30, 0.20), (0, -0.02, 0.05), 0.80, 30.0, (0.80, 0.86, 1.0))
    area("Rim", (-0.12, 0.45, 0.42), (0, 0.02, 0.07), 0.45, 55.0, (0.92, 0.94, 1.0))
    area("Strip", (0.05, -0.55, 0.06), (0, -0.06, 0.05), 0.05, 25.0, (1.0, 1.0, 1.0),
         size_y=0.5)


main()
