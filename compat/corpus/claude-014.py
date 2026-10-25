"""claude-014 - Modular bookshelf with staggered shelves and books (Blender 4.5 LTS)."""
import bpy, bmesh, math, random
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


def mat(name, col, rough=0.5, metal=0.0, alpha=1.0, coat=0.0, emit=None, estr=0.0):
    m = bpy.data.materials.new(name)
    m.use_nodes = True
    b = m.node_tree.nodes["Principled BSDF"]
    b.inputs["Base Color"].default_value = (col[0], col[1], col[2], 1.0)
    b.inputs["Roughness"].default_value = rough
    b.inputs["Metallic"].default_value = metal
    if "Coat Weight" in b.inputs:
        b.inputs["Coat Weight"].default_value = coat
    if "Alpha" in b.inputs:
        b.inputs["Alpha"].default_value = alpha
    if emit is not None and "Emission Color" in b.inputs:
        b.inputs["Emission Color"].default_value = (emit[0], emit[1], emit[2], 1.0)
        b.inputs["Emission Strength"].default_value = estr
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


def cyl(r, d, seg=24, loc=(0, 0, 0), rot=(0, 0, 0), r2=None, smooth=True):
    bm = bmesh.new()
    bmesh.ops.create_cone(bm, cap_ends=True, cap_tris=False, segments=seg,
                          radius1=r, radius2=(r if r2 is None else r2), depth=d)
    if smooth:
        for f in bm.faces:
            if abs(f.normal.z) < 0.9:
                f.smooth = True
    return _x(bm, loc, rot)


def ball(r, loc=(0, 0, 0), sub=2, scale=(1, 1, 1)):
    bm = bmesh.new()
    bmesh.ops.create_icosphere(bm, subdivisions=sub, radius=r)
    for f in bm.faces:
        f.smooth = True
    return _x(bm, loc, (0, 0, 0), scale)


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
W, D, H = 2.00, 0.32, 1.90
ST = 0.025                       # shelf board thickness
SD = 0.30                        # shelf depth
Y_FRONT = -SD / 2.0              # front edge of the shelf boards


def make_book(rng, name, w, d, h, cx, base_z, y_front, cover, pages, accent,
              tilt=0.0, flat=False):
    """One book = cover box + inset page block (+ optional spine band)."""
    bm = bmesh.new()
    join(bm, box((w, d, h), (0, 0, 0), bevel=min(0.0025, w * 0.15, h * 0.1)), 0)
    if flat:
        join(bm, box((w - 0.008, d - 0.010, h - 0.006), (0.004, 0.004, 0.0)), 1)
    else:
        join(bm, box((w - 0.006, d - 0.012, h - 0.008), (0, 0.007, 0.0)), 1)
        if rng.random() < 0.55:
            join(bm, box((w + 0.0006, 0.004, h * 0.16),
                         (0, -d / 2 + 0.001, h * (0.22 if rng.random() < 0.5 else -0.26))),
                 2)
    loc = (cx + (h / 2.0) * math.sin(tilt) * 0.6,
           y_front + d / 2.0,
           base_z + (h / 2.0) * math.cos(tilt))
    return obj(name, bm, [cover, pages, accent], loc=loc, rot=(0.0, tilt, 0.0))


def fill_run(rng, x0, x1, floor_z, ceil_z, covers, pages, accents, tag, made):
    clear = ceil_z - floor_z
    if clear < 0.12 or x1 - x0 < 0.06:
        return
    x = x0 + rng.uniform(0.006, 0.022)
    while x < x1 - 0.035:
        roll = rng.random()
        if roll < 0.10:
            x += rng.uniform(0.03, 0.10)
            continue
        cover = rng.choice(covers)
        accent = rng.choice(accents)
        if roll < 0.26 and clear > 0.16:
            run = rng.uniform(0.14, 0.21)
            if x + run > x1 - 0.02:
                break
            z = floor_z
            for i in range(rng.randint(2, 4)):
                th = rng.uniform(0.022, 0.036)
                if z + th > ceil_z - 0.01:
                    break
                d = rng.uniform(0.15, 0.22)
                made[0] += 1
                make_book(rng, "Book_%s_%03d" % (tag, made[0]), run, d, th,
                          x + run / 2.0, z, Y_FRONT + rng.uniform(0.01, 0.04),
                          rng.choice(covers), pages, rng.choice(accents), flat=True)
                z += th
            x += run + rng.uniform(0.008, 0.03)
            continue
        hi = min(0.28, clear - 0.015)
        lo = max(0.13, hi - 0.10)
        h = rng.uniform(lo, hi)
        w = rng.uniform(0.018, 0.050)
        d = rng.uniform(0.15, 0.245)
        tilt = 0.0
        if roll < 0.34 and clear > h + 0.05:
            tilt = rng.choice((-1.0, 1.0)) * rng.uniform(0.12, 0.22)
        made[0] += 1
        make_book(rng, "Book_%s_%03d" % (tag, made[0]), w, d, h,
                  x + w / 2.0, floor_z, Y_FRONT + rng.uniform(0.008, 0.05),
                  cover, pages, accent, tilt=tilt)
        x += w + (0.012 if tilt else 0.002)


def main():
    reset()
    world((0.05, 0.052, 0.058), 0.6)
    rng = random.Random(20260909)

    m_case = mat("OakCase", (0.34, 0.235, 0.145), 0.42, coat=0.12)
    m_back = mat("BackPanel", (0.19, 0.20, 0.22), 0.62)
    m_pages = mat("Pages", (0.86, 0.83, 0.74), 0.75)
    m_floor = mat("Floor", (0.20, 0.17, 0.15), 0.55, coat=0.1)
    m_wall = mat("Wall", (0.44, 0.44, 0.43), 0.75)
    m_metal = mat("Brass", (0.62, 0.48, 0.20), 0.28, metal=1.0)
    m_pot = mat("Pot", (0.55, 0.34, 0.26), 0.55)
    m_leaf = mat("Foliage", (0.10, 0.30, 0.12), 0.62)
    m_vase = mat("Vase", (0.12, 0.28, 0.30), 0.20, coat=0.5)

    covers = [mat("Cover_%02d" % i, c, rng.uniform(0.35, 0.7), coat=rng.uniform(0.0, 0.3))
              for i, c in enumerate([
                  (0.42, 0.09, 0.10), (0.09, 0.19, 0.34), (0.12, 0.28, 0.19),
                  (0.52, 0.34, 0.10), (0.24, 0.10, 0.30), (0.06, 0.07, 0.09),
                  (0.66, 0.60, 0.46), (0.30, 0.32, 0.36), (0.58, 0.22, 0.08),
                  (0.14, 0.32, 0.36), (0.46, 0.44, 0.16), (0.36, 0.16, 0.22)])]
    accents = [mat("Accent_%02d" % i, c, 0.35, metal=(0.9 if i < 2 else 0.0))
               for i, c in enumerate([(0.72, 0.58, 0.24), (0.82, 0.82, 0.84),
                                      (0.90, 0.88, 0.82), (0.10, 0.10, 0.12)])]

    obj("Floor", box((8.0, 8.0, 0.06), (0, 0, -0.03)), m_floor)
    obj("BackWall", box((8.0, 0.10, 4.0), (0, 0.44, 2.0)), m_wall)

    # ------------------------------------------------------------------- case
    bays = [(-0.970, -0.3525), (-0.3275, 0.3075), (0.3325, 0.970)]
    shelves = {0: [0.46, 0.86, 1.18, 1.52],
               1: [0.62, 1.00, 1.40],
               2: [0.40, 0.78, 1.10, 1.46]}
    dividers = [(-0.340, 0.105, 1.885), (0.320, 0.105, 1.885)]
    subdiv = [(-0.660, 0.46, 0.86), (0.660, 1.10, 1.46)]

    bm = bmesh.new()
    for sx in (-1, 1):
        join(bm, box((0.030, D, H - 0.09), (sx * 0.985, 0.0, 0.09 + (H - 0.09) / 2.0)), 0)
    join(bm, box((W, D, ST), (0, 0, 1.885)), 0)
    join(bm, box((W, D, ST), (0, 0, 0.105)), 0)
    join(bm, box((W - 0.06, D - 0.04, 0.075), (0, 0, 0.0375)), 0)
    for x, z0, z1 in dividers:
        join(bm, box((0.025, D, z1 - z0), (x, 0.0, (z0 + z1) / 2.0)), 0)
    for x, z0, z1 in subdiv:
        join(bm, box((0.022, SD, z1 - z0 - ST), (x, 0.0, (z0 + z1) / 2.0)), 0)
    for bi, (bx0, bx1) in enumerate(bays):
        for z in shelves[bi]:
            join(bm, box((bx1 - bx0, SD, ST), ((bx0 + bx1) / 2.0, 0.0, z)), 0)
    obj("Bookshelf_Case", bm, m_case)
    obj("BackPanel", box((W - 0.06, 0.012, H - 0.14), (0, 0.152, 0.99)), m_back)

    # ------------------------------------------------------------------ books
    made = [0]
    for bi, (bx0, bx1) in enumerate(bays):
        levels = [0.105] + shelves[bi] + [1.885]
        for i in range(len(levels) - 1):
            fz = levels[i] + ST / 2.0
            cz = levels[i + 1] - ST / 2.0
            runs = [(bx0, bx1)]
            for x, z0, z1 in subdiv:
                if bx0 < x < bx1 and z0 <= fz + 0.02 and z1 >= cz - 0.02:
                    runs = [(bx0, x - 0.013), (x + 0.013, bx1)]
            for ri, (rx0, rx1) in enumerate(runs):
                if rng.random() < 0.12 and i not in (0, len(levels) - 2):
                    continue                              # leave a compartment open
                fill_run(rng, rx0, rx1, fz, cz, covers, m_pages, accents,
                         "%d%d%d" % (bi, i, ri), made)

    # ---------------------------------------------------------------- objects
    z_top = 1.885 + ST / 2.0
    for i, (th, w) in enumerate(((0.032, 0.20), (0.028, 0.185), (0.035, 0.21))):
        make_book(rng, "TopStack_%d" % i, w, 0.20, th, -0.55, z_top + i * 0.033,
                  Y_FRONT + 0.03, rng.choice(covers), m_pages, rng.choice(accents),
                  flat=True)

    bm = bmesh.new()
    for i, x in enumerate((0.62, 0.735)):
        join(bm, box((0.10, 0.24, 0.26), (x, 0.02, 0.105 + ST / 2.0 + 0.13),
                     bevel=0.006, seg=2), 0)
    obj("MagazineFiles", bm, m_back)

    bm = bmesh.new()
    join(bm, cyl(0.055, 0.075, seg=28, r2=0.075, loc=(-0.75, 0.02, z_top + 0.0375)), 0)
    obj("Pot", bm, m_pot)
    bm = bmesh.new()
    for dx, dy, dz, r in ((0.0, 0.0, 0.075, 0.07), (0.05, 0.02, 0.055, 0.045),
                          (-0.045, -0.02, 0.06, 0.05), (0.01, -0.04, 0.045, 0.038)):
        join(bm, ball(r, (-0.75 + dx, 0.02 + dy, z_top + 0.075 + dz),
                      sub=2, scale=(1.0, 1.0, 0.75)), 0)
    obj("Foliage", bm, m_leaf)

    obj("Vase", cyl(0.045, 0.16, seg=32, r2=0.030, loc=(0.42, 0.02, z_top + 0.08)),
        m_vase)

    bm = bmesh.new()
    join(bm, box((0.20, 0.016, 0.26), (0.10, 0.09, 1.00 + ST / 2.0 + 0.13),
                 rot=(0.20, 0, 0.10)), 0)
    obj("FrameBack", bm, m_case)
    obj("FrameGlass", box((0.17, 0.006, 0.23), (0.10, 0.077, 1.00 + ST / 2.0 + 0.13),
                          rot=(0.20, 0, 0.10)), m_metal)

    # -------------------------------------------------------- camera and lights
    cam((1.55, -2.55, 1.35), (-0.05, 0.0, 0.98), lens=42.0, fstop=6.0)
    area("Key", (2.0, -2.6, 3.0), (0, 0, 1.1), 2.2, 900.0, (1.0, 0.96, 0.90))
    area("Fill", (-2.6, -2.2, 1.5), (0, 0, 1.0), 2.6, 320.0, (0.82, 0.88, 1.0))
    area("Wash", (0.0, -1.4, 2.6), (0, 0.2, 1.2), 0.12, 240.0, (1.0, 0.90, 0.75),
         size_y=2.4)


main()
