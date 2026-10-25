"""claude-078: A construction barricade with striped slats and feet (Blender 4.5 LTS)."""
import bpy, bmesh, math
from mathutils import Vector, Matrix


# ------------------------------------------------------------------ helpers
def reset(bg=(0.10, 0.12, 0.15), strength=1.0):
    bpy.ops.wm.read_factory_settings(use_empty=True)
    w = bpy.data.worlds.new("World")
    w.use_nodes = True
    n = w.node_tree.nodes["Background"]
    n.inputs[0].default_value = (bg[0], bg[1], bg[2], 1.0)
    n.inputs[1].default_value = strength
    bpy.context.scene.world = w
    bpy.context.scene.render.resolution_x = 1600
    bpy.context.scene.render.resolution_y = 1100


def mat(name, col, rough=0.5, metal=0.0, emit=None):
    m = bpy.data.materials.new(name)
    m.use_nodes = True
    b = m.node_tree.nodes["Principled BSDF"]
    b.inputs["Base Color"].default_value = (col[0], col[1], col[2], 1.0)
    b.inputs["Roughness"].default_value = rough
    b.inputs["Metallic"].default_value = metal
    if emit:
        b.inputs["Emission Color"].default_value = (emit[0], emit[1], emit[2], 1.0)
        b.inputs["Emission Strength"].default_value = emit[3]
    return m


def to_obj(name, bm, mats=(), recalc=True):
    me = bpy.data.meshes.new(name)
    if recalc:
        bmesh.ops.recalc_face_normals(bm, faces=bm.faces[:])
    bm.to_mesh(me)
    bm.free()
    for m in mats:
        me.materials.append(m)
    ob = bpy.data.objects.new(name, me)
    bpy.context.collection.objects.link(ob)
    return ob


def _nf(res):
    fs = set()
    for v in res.get("verts", ()):
        fs.update(v.link_faces)
    return fs


def bx(bm, size, c, mi=0, basis=None):
    m = Matrix.Translation(Vector(c))
    if basis is not None:
        m = m @ basis
    m = m @ Matrix.Diagonal(Vector((size[0], size[1], size[2], 1.0)))
    for f in _nf(bmesh.ops.create_cube(bm, size=1.0, matrix=m)):
        f.material_index = mi


def cy(bm, r, d, c, mi=0, axis='Z', seg=16, r2=None):
    rot = {'Z': Matrix.Identity(4),
           'X': Matrix.Rotation(math.radians(90.0), 4, 'Y'),
           'Y': Matrix.Rotation(math.radians(-90.0), 4, 'X')}[axis]
    m = Matrix.Translation(Vector(c)) @ rot
    res = bmesh.ops.create_cone(bm, cap_ends=True, cap_tris=False, segments=seg,
                                radius1=r, radius2=(r if r2 is None else r2),
                                depth=d, matrix=m)
    for f in _nf(res):
        f.material_index = mi


def sphere(bm, r, c, mi=0, subdiv=3):
    m = Matrix.Translation(Vector(c)) @ Matrix.Diagonal(Vector((r, r, r, 1.0)))
    res = bmesh.ops.create_icosphere(bm, subdivisions=subdiv, radius=1.0, matrix=m)
    for f in _nf(res):
        f.material_index = mi


def strut(bm, p0, p1, w, h, mi=0, pad=0.0):
    p0, p1 = Vector(p0), Vector(p1)
    d = p1 - p0
    if d.length < 1e-7:
        return
    bx(bm, (d.length + pad, w, h), (p0 + p1) * 0.5, mi,
       d.to_track_quat('X', 'Z').to_matrix().to_4x4())


def plane(name, size, m, loc=(0.0, 0.0, 0.0)):
    bm = bmesh.new()
    bmesh.ops.create_grid(bm, x_segments=8, y_segments=8, size=size * 0.5)
    ob = to_obj(name, bm, (m,))
    ob.location = loc
    return ob


def sun(name, energy, rot, ang=0.02, col=(1.0, 0.97, 0.93)):
    d = bpy.data.lights.new(name, 'SUN')
    d.energy = energy
    d.angle = ang
    d.color = col
    ob = bpy.data.objects.new(name, d)
    ob.rotation_euler = rot
    bpy.context.collection.objects.link(ob)
    return ob


def area(name, energy, loc, target, size=8.0, col=(1.0, 1.0, 1.0)):
    d = bpy.data.lights.new(name, 'AREA')
    d.energy = energy
    d.size = size
    d.color = col
    ob = bpy.data.objects.new(name, d)
    ob.location = loc
    ob.rotation_euler = (Vector(target) - Vector(loc)).to_track_quat('-Z', 'Y').to_euler()
    bpy.context.collection.objects.link(ob)
    return ob


def point(name, energy, loc, radius=0.08, col=(1.0, 0.62, 0.10)):
    d = bpy.data.lights.new(name, 'POINT')
    d.energy = energy
    d.shadow_soft_size = radius
    d.color = col
    ob = bpy.data.objects.new(name, d)
    ob.location = loc
    bpy.context.collection.objects.link(ob)
    return ob


def camera(loc, target, lens=45.0):
    c = bpy.data.cameras.new("Camera")
    c.lens = lens
    ob = bpy.data.objects.new("Camera", c)
    ob.location = loc
    ob.rotation_euler = (Vector(target) - Vector(loc)).to_track_quat('-Z', 'Y').to_euler()
    bpy.context.collection.objects.link(ob)
    bpy.context.scene.camera = ob
    return ob


def bevel(ob, width=0.008, segments=2):
    mo = ob.modifiers.new("Bevel", 'BEVEL')
    mo.width = width
    mo.segments = segments
    mo.limit_method = 'ANGLE'
    mo.angle_limit = math.radians(40.0)
    return mo


# ------------------------------------------------- diagonal stripe geometry
def clip_halfplane(poly, a, b, c):
    """Sutherland-Hodgman clip of a 2D polygon to a*u + b*v + c >= 0."""
    out = []
    n = len(poly)
    for i in range(n):
        p, q = poly[i], poly[(i + 1) % n]
        dp = a * p[0] + b * p[1] + c
        dq = a * q[0] + b * q[1] + c
        if dp >= 0.0:
            out.append(p)
        if (dp > 0.0 > dq) or (dp < 0.0 < dq):
            t = dp / (dp - dq)
            out.append((p[0] + t * (q[0] - p[0]), p[1] + t * (q[1] - p[1])))
    return out


def striped_slat(name, length, height, thickness, stripe_w, mats, slope=-1.0):
    """Rail in the XZ plane whose faces are split into alternating diagonal bands.

    Bands are perpendicular to (1, slope): with slope = -1 the stripes slant down
    toward +X, as on a Type III barricade."""
    bm = bmesh.new()
    hx, hz = length * 0.5, height * 0.5
    rect = [(-hx, -hz), (hx, -hz), (hx, hz), (-hx, hz)]
    inv = 1.0 / math.hypot(1.0, slope)
    ax, az = inv, slope * inv
    svals = [ax * p[0] + az * p[1] for p in rect]
    k0 = int(math.floor(min(svals) / stripe_w))
    k1 = int(math.ceil(max(svals) / stripe_w))
    yf, yb = -thickness * 0.5, thickness * 0.5
    for k in range(k0, k1 + 1):
        poly = clip_halfplane(rect, ax, az, -k * stripe_w)
        if len(poly) < 3:
            continue
        poly = clip_halfplane(poly, -ax, -az, (k + 1) * stripe_w)
        if len(poly) < 3:
            continue
        mi = (k % 2 + 2) % 2
        front = [bm.verts.new((u, yf, v)) for u, v in poly]
        bm.faces.new(front).material_index = mi
        back = [bm.verts.new((u, yb, v)) for u, v in reversed(poly)]
        bm.faces.new(back).material_index = mi
    ring = rect + [rect[0]]
    for i in range(4):
        u0, v0 = ring[i]
        u1, v1 = ring[i + 1]
        vs = [bm.verts.new((u0, yf, v0)), bm.verts.new((u1, yf, v1)),
              bm.verts.new((u1, yb, v1)), bm.verts.new((u0, yb, v0))]
        bm.faces.new(vs).material_index = 2
    bm.normal_update()
    return to_obj(name, bm, mats, recalc=False)


# ---------------------------------------------------------------- barricade
RAIL_L = 2.44
RAIL_H = 0.205
RAIL_T = 0.038
RAIL_Z = (0.78, 1.08, 1.38)
POST_X = 1.02
POST_TOP = 1.56
FRONT_Y = -0.042


def build_rails(orange, white, edge):
    for i, z in enumerate(RAIL_Z):
        ob = striped_slat("Slat_%d" % i, RAIL_L, RAIL_H, RAIL_T, 0.152,
                          (orange, white, edge), slope=-1.0)
        ob.location = (0.0, FRONT_Y, z)


def build_frame(alu, plastic, bolt):
    bm = bmesh.new()
    for sx in (-1.0, 1.0):
        px = sx * POST_X
        bx(bm, (0.085, 0.045, POST_TOP - 0.09), (px, 0.0, (POST_TOP + 0.09) * 0.5), 0)
        bx(bm, (0.10, 0.075, 0.05), (px, 0.0, POST_TOP - 0.02), 0)
        strut(bm, (px, 0.02, 1.30), (px, 0.62, 0.075), 0.055, 0.05, 0)
        strut(bm, (px, 0.03, 0.62), (px, 0.34, 0.60), 0.04, 0.035, 0)
        for z in RAIL_Z:
            bx(bm, (0.095, 0.05, 0.24), (px, -0.012, z), 0)
            for dz in (-0.062, 0.062):
                cy(bm, 0.011, 0.115, (px, -0.045, z + dz), 2, axis='Y', seg=10)
                bx(bm, (0.028, 0.014, 0.028), (px, -0.096, z + dz), 2)
    strut(bm, (-POST_X + 0.04, 0.055, 0.42), (POST_X - 0.04, 0.055, 1.30), 0.05, 0.03, 0)
    strut(bm, (-POST_X + 0.04, 0.055, 1.30), (POST_X - 0.04, 0.055, 0.42), 0.05, 0.03, 0)
    bx(bm, (2.0, 0.05, 0.05), (0.0, 0.055, 0.40), 0)
    bevel(to_obj("Frame", bm, (alu, plastic, bolt)), 0.005, 1)


def build_feet(plastic, bolt, sandbag):
    """Moulded plastic base feet with rounded ends, plus sandbag ballast."""
    bm = bmesh.new()
    for sx in (-1.0, 1.0):
        px = sx * POST_X
        for fy, fl in ((0.02, 0.62), (0.60, 0.34)):
            bx(bm, (0.19, fl, 0.075), (px, fy, 0.0375), 0)
            for dy in (-fl * 0.5, fl * 0.5):
                cy(bm, 0.0375, 0.19, (px, fy + dy, 0.0375), 0, axis='X', seg=14)
            for k in range(3):
                bx(bm, (0.155, 0.03, 0.055), (px, fy - fl * 0.32 + k * fl * 0.32, 0.062), 0)
        bx(bm, (0.135, 0.10, 0.16), (px, 0.0, 0.115), 0)
        cy(bm, 0.012, 0.17, (px, 0.0, 0.135), 1, axis='X', seg=10)
        bx(bm, (0.34, 0.26, 0.10), (px, -0.06, 0.13), 2,
           Matrix.Rotation(math.radians(6.0 * sx), 4, 'Y'))
    bevel(to_obj("Feet", bm, (plastic, bolt, sandbag)), 0.012, 2)


def build_beacon(housing, lens, bolt):
    base = (POST_X, 0.0, POST_TOP + 0.06)
    bm = bmesh.new()
    bx(bm, (0.17, 0.15, 0.11), base, 0)
    bx(bm, (0.10, 0.09, 0.06), (base[0], base[1], base[2] - 0.08), 0)
    cy(bm, 0.012, 0.20, (base[0], base[1], base[2] - 0.08), 1, axis='X', seg=8)
    to_obj("BeaconHousing", bm, (housing, bolt))
    bm = bmesh.new()
    sphere(bm, 0.075, (base[0], base[1], base[2] + 0.075), 0)
    cy(bm, 0.078, 0.035, (base[0], base[1], base[2] + 0.03), 0, seg=20)
    to_obj("BeaconLens", bm, (lens,))
    point("Beacon", 22.0, (base[0], base[1], base[2] + 0.09))


def build_context(asphalt, orange, white, dirt, plastic):
    plane("Road", 60.0, asphalt, (0.0, 0.0, 0.0))
    bm = bmesh.new()
    bx(bm, (3.4, 2.0, 0.24), (0.15, 2.25, -0.10), 0)
    to_obj("Trench", bm, (dirt,))
    bm = bmesh.new()
    for i in range(28):
        a = i * 0.61
        r = 0.7 + 0.55 * ((i * 7) % 5) / 5.0
        bx(bm, (0.16 + 0.06 * (i % 3), 0.14, 0.09 + 0.03 * (i % 4)),
           (0.15 + r * math.cos(a), 3.6 + 0.5 * math.sin(a), 0.05), 0)
    bevel(to_obj("SpoilPile", bm, (dirt,)), 0.02, 1)
    for i, (cx, cyy) in enumerate(((-1.85, -0.35), (1.95, -0.55))):
        bm = bmesh.new()
        res = bmesh.ops.create_cone(bm, cap_ends=True, cap_tris=False, segments=20,
                                    radius1=0.145, radius2=0.028, depth=0.62,
                                    matrix=Matrix.Translation((0.0, 0.0, 0.34)))
        for f in _nf(res):
            f.material_index = 0
        bx(bm, (0.34, 0.34, 0.035), (0.0, 0.0, 0.0175), 0)
        cy(bm, 0.098, 0.10, (0.0, 0.0, 0.44), 1, seg=20)
        cy(bm, 0.072, 0.07, (0.0, 0.0, 0.575), 1, seg=20)
        cone = to_obj("Cone_%d" % i, bm, (orange, white))
        cone.location = (cx, cyy, 0.0)
        cone.rotation_euler = (0.0, 0.0, i * 0.7)


def main():
    reset()
    orange = mat("ReflOrange", (0.78, 0.20, 0.015), 0.34)
    white = mat("ReflWhite", (0.86, 0.86, 0.84), 0.34)
    edge = mat("SlatEdge", (0.42, 0.43, 0.44), 0.45, 0.65)
    alu = mat("Upright", (0.50, 0.51, 0.53), 0.44, 0.80)
    plastic = mat("FootPlastic", (0.055, 0.055, 0.06), 0.62)
    bolt = mat("Bolt", (0.60, 0.60, 0.62), 0.32, 0.95)
    sandbag = mat("Sandbag", (0.30, 0.26, 0.19), 0.90)
    lens = mat("AmberLens", (0.95, 0.42, 0.02), 0.20, 0.0, emit=(1.0, 0.45, 0.03, 12.0))
    asphalt = mat("Asphalt", (0.055, 0.056, 0.06), 0.88)
    dirt = mat("Soil", (0.14, 0.10, 0.07), 0.94)

    build_context(asphalt, orange, white, dirt, plastic)
    build_rails(orange, white, edge)
    build_frame(alu, plastic, bolt)
    build_feet(plastic, bolt, sandbag)
    build_beacon(plastic, lens, bolt)

    sun("Sun", 3.6, (math.radians(48.0), math.radians(10.0), math.radians(-42.0)))
    area("SkyFill", 260.0, (-2.5, -5.0, 5.0), (0.0, 0.4, 0.9), 8.0, (0.62, 0.74, 1.0))
    area("Bounce", 90.0, (2.6, -2.2, 0.9), (0.0, 0.3, 0.9), 4.0, (1.0, 0.90, 0.78))
    camera((-2.35, -3.35, 1.45), (0.05, 0.12, 0.95), lens=48.0)


main()
