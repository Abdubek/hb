# claude-051 : Industrial pipe assembly with elbows and valve wheels  (Blender 4.5 LTS)
import bpy, bmesh, math
from mathutils import Vector, Matrix, Quaternion

TAU = math.tau

# ----------------------------------------------------------------------------- scene
def reset():
    bpy.ops.wm.read_factory_settings(use_empty=True)
    sc = bpy.context.scene
    sc.unit_settings.system = 'METRIC'
    try:
        sc.render.engine = 'BLENDER_EEVEE_NEXT'
    except Exception:
        pass

def link(ob):
    bpy.context.scene.collection.objects.link(ob)
    return ob

def auto_smooth(ob, angle=math.radians(35.0)):
    for o in bpy.context.selected_objects:
        o.select_set(False)
    bpy.context.view_layer.objects.active = ob
    ob.select_set(True)
    try:
        bpy.ops.object.shade_auto_smooth(angle=angle)
    except Exception:
        try:
            bpy.ops.object.shade_smooth()
        except Exception:
            pass
    ob.select_set(False)

# ----------------------------------------------------------------------------- materials
def pbr(name, base, metallic=0.0, rough=0.5, spec=0.5, emit=None):
    m = bpy.data.materials.new(name)
    m.use_nodes = True
    b = m.node_tree.nodes["Principled BSDF"]
    b.inputs["Base Color"].default_value = (base[0], base[1], base[2], 1.0)
    b.inputs["Metallic"].default_value = metallic
    b.inputs["Roughness"].default_value = rough
    if "Specular IOR Level" in b.inputs:
        b.inputs["Specular IOR Level"].default_value = spec
    if emit is not None and "Emission Color" in b.inputs:
        b.inputs["Emission Color"].default_value = (emit[0], emit[1], emit[2], 1.0)
        b.inputs["Emission Strength"].default_value = emit[3]
    return m

def make_materials():
    return {
        'steel'   : pbr("Steel_Pipe",    (0.42, 0.44, 0.47), 1.0, 0.38),
        'darksteel': pbr("Steel_Dark",   (0.20, 0.21, 0.23), 1.0, 0.52),
        'valve'   : pbr("Valve_Body",    (0.045, 0.10, 0.26), 0.25, 0.42),
        'wheel'   : pbr("Wheel_Red",     (0.46, 0.045, 0.035), 0.15, 0.40),
        'brass'   : pbr("Brass_Stem",    (0.72, 0.52, 0.20), 1.0, 0.26),
        'paintyel': pbr("Paint_Yellow",  (0.62, 0.44, 0.05), 0.20, 0.45),
        'concrete': pbr("Concrete",      (0.30, 0.30, 0.29), 0.0, 0.88),
        'wall'    : pbr("Wall_Panel",    (0.36, 0.37, 0.36), 0.10, 0.72),
        'face'    : pbr("Gauge_Face",    (0.88, 0.88, 0.85), 0.0, 0.35),
        'glass'   : pbr("Gauge_Rim",     (0.15, 0.15, 0.16), 0.8, 0.30),
    }

# ----------------------------------------------------------------------------- math helpers
def axis_matrix(loc, axis):
    """Matrix placing a primitive (built along +Z) at loc, aligned to axis."""
    a = Vector(axis)
    if a.length < 1e-9:
        a = Vector((0.0, 0.0, 1.0))
    q = a.normalized().to_track_quat('Z', 'Y')
    return Matrix.Translation(Vector(loc)) @ q.to_matrix().to_4x4()

def basis_matrix(origin, x_dir, z_hint):
    """Orthonormal frame: local +X along x_dir, local +Z as close to z_hint as possible."""
    x = Vector(x_dir).normalized()
    z = Vector(z_hint)
    z = z - x * z.dot(x)
    if z.length < 1e-6:
        z = Vector((0.0, 0.0, 1.0)) if abs(x.z) < 0.9 else Vector((0.0, 1.0, 0.0))
        z = z - x * z.dot(x)
    z.normalize()
    y = z.cross(x)
    o = Vector(origin)
    return Matrix(((x.x, y.x, z.x, o.x),
                   (x.y, y.y, z.y, o.y),
                   (x.z, y.z, z.z, o.z),
                   (0.0, 0.0, 0.0, 1.0)))

def rounded_path(points, bend_radius, segments=10):
    """Insert circular arcs (the elbows) at every corner of a polyline."""
    pts = [Vector(p) for p in points]
    out = [pts[0].copy()]
    for i in range(1, len(pts) - 1):
        p0, p1, p2 = pts[i - 1], pts[i], pts[i + 1]
        d1 = p0 - p1
        d2 = p2 - p1
        if d1.length < 1e-8 or d2.length < 1e-8:
            continue
        u1, u2 = d1.normalized(), d2.normalized()
        ang = u1.angle(u2)
        if ang < 1e-4 or abs(ang - math.pi) < 1e-4:
            out.append(p1.copy())
            continue
        tan_len = bend_radius / math.tan(ang * 0.5)
        tan_len = min(tan_len, d1.length * 0.49, d2.length * 0.49)
        rr = tan_len * math.tan(ang * 0.5)
        a = p1 + u1 * tan_len
        b = p1 + u2 * tan_len
        bis = (u1 + u2)
        if bis.length < 1e-8:
            out.append(p1.copy())
            continue
        centre = p1 + bis.normalized() * (rr / math.sin(ang * 0.5))
        va, vb = a - centre, b - centre
        n = va.cross(vb)
        if n.length < 1e-9:
            out.append(p1.copy())
            continue
        n.normalize()
        total = va.angle(vb)
        for k in range(segments + 1):
            q = Quaternion(n, total * k / segments)
            out.append(centre + (q @ va))
    out.append(pts[-1].copy())
    # strip duplicates
    clean = [out[0]]
    for p in out[1:]:
        if (p - clean[-1]).length > 1e-6:
            clean.append(p)
    return clean

def path_tangent(p_from, p_to):
    return (Vector(p_to) - Vector(p_from)).normalized()

# ----------------------------------------------------------------------------- mesh builder
class MeshBuilder:
    def __init__(self, name):
        self.name = name
        self.bm = bmesh.new()
        self.mats = []

    def _mi(self, mat):
        for i, m in enumerate(self.mats):
            if m is mat:
                return i
        self.mats.append(mat)
        return len(self.mats) - 1

    def _assign(self, before, mat, smooth):
        idx = self._mi(mat)
        for f in self.bm.faces:
            if f not in before:
                f.material_index = idx
                f.smooth = smooth

    def cylinder(self, radius, depth, matrix, mat, segs=32, r2=None, caps=True, smooth=True):
        before = set(self.bm.faces)
        bmesh.ops.create_cone(self.bm, cap_ends=caps, cap_tris=False, segments=segs,
                              radius1=radius, radius2=(radius if r2 is None else r2),
                              depth=depth, matrix=matrix, calc_uvs=True)
        self._assign(before, mat, smooth)

    def box(self, size, matrix, mat, smooth=False):
        before = set(self.bm.faces)
        m = matrix @ Matrix.Diagonal(Vector(size)).to_4x4()
        bmesh.ops.create_cube(self.bm, size=1.0, matrix=m, calc_uvs=True)
        self._assign(before, mat, smooth)

    def torus(self, major, minor, matrix, mat, mseg=40, nseg=14, smooth=True):
        before = set(self.bm.faces)
        rings = []
        for i in range(mseg):
            a = TAU * i / mseg
            ca, sa = math.cos(a), math.sin(a)
            ring = []
            for j in range(nseg):
                b = TAU * j / nseg
                rr = major + minor * math.cos(b)
                co = Vector((rr * ca, rr * sa, minor * math.sin(b)))
                ring.append(self.bm.verts.new(matrix @ co))
            rings.append(ring)
        for i in range(mseg):
            r0, r1 = rings[i], rings[(i + 1) % mseg]
            for j in range(nseg):
                k = (j + 1) % nseg
                try:
                    self.bm.faces.new((r0[j], r1[j], r1[k], r0[k]))
                except ValueError:
                    pass
        self.bm.verts.index_update()
        self._assign(before, mat, smooth)

    def build(self, smooth_angle=math.radians(35.0)):
        me = bpy.data.meshes.new(self.name)
        self.bm.normal_update()
        self.bm.to_mesh(me)
        self.bm.free()
        for m in self.mats:
            me.materials.append(m)
        ob = link(bpy.data.objects.new(self.name, me))
        auto_smooth(ob, smooth_angle)
        return ob

# ----------------------------------------------------------------------------- pipe runs
def make_pipe(name, points, radius, mat, bend, bevel_res=8, arc_segs=10, caps=True):
    pts = rounded_path(points, bend, arc_segs)
    cu = bpy.data.curves.new(name + "_crv", 'CURVE')
    cu.dimensions = '3D'
    cu.resolution_u = 2
    cu.bevel_depth = radius
    cu.bevel_resolution = bevel_res
    cu.use_fill_caps = caps
    sp = cu.splines.new('POLY')
    sp.points.add(len(pts) - 1)
    for i, p in enumerate(pts):
        sp.points[i].co = (p.x, p.y, p.z, 1.0)
    sp.use_smooth = True
    ob = link(bpy.data.objects.new(name, cu))
    cu.materials.append(mat)
    return ob

# ----------------------------------------------------------------------------- parts
def add_flange(b, centre, axis, r, mats, bolts=8):
    c = Vector(centre)
    a = Vector(axis).normalized()
    Rf, t = 2.05 * r, 0.36 * r
    b.cylinder(Rf, t, axis_matrix(c, a), mats['steel'], segs=32)
    b.cylinder(1.30 * r, t * 1.9, axis_matrix(c, a), mats['steel'], segs=28)
    q = a.to_track_quat('Z', 'Y')
    ring, br = 1.58 * r, 0.115 * r
    for i in range(bolts):
        ang = TAU * i / bolts + math.pi / bolts
        off = q @ Vector((math.cos(ang) * ring, math.sin(ang) * ring, 0.0))
        b.cylinder(br, t * 2.1, axis_matrix(c + off, a), mats['darksteel'], segs=6, smooth=False)

def add_valve(name, r, origin, flow_dir, stem_dir, mats, wheel_scale=1.0, hand_turn=0.0):
    """Flanged gate valve with a spoked hand wheel. Local frame: +X = flow, +Z = stem."""
    b = MeshBuilder(name)
    R = r
    X = Vector((1.0, 0.0, 0.0))
    Z = Vector((0.0, 0.0, 1.0))
    steel, body, wheel, brass = mats['steel'], mats['valve'], mats['wheel'], mats['brass']

    # --- pipe stubs and end flanges
    for s in (1.0, -1.0):
        b.cylinder(R * 1.02, R * 2.4, axis_matrix((s * 2.0 * R, 0, 0), X), steel, segs=28)
        add_flange(b, (s * 3.0 * R, 0, 0), X, R, mats)

    # --- body
    b.cylinder(R * 1.55, R * 1.75, axis_matrix((0, 0, 0), X), body, segs=32)
    b.torus(R * 1.55, R * 0.20, axis_matrix((0, 0, 0), X), body, mseg=32, nseg=12)
    b.cylinder(R * 1.50, R * 0.65, axis_matrix((0, 0, -R * 1.15), Z), body, segs=32, r2=R * 1.12)
    b.cylinder(R * 1.10, R * 0.22, axis_matrix((0, 0, -R * 1.55), Z), body, segs=32)

    # --- neck / bonnet
    b.cylinder(R * 1.36, R * 0.95, axis_matrix((0, 0, R * 1.05), Z), body, segs=32, r2=R * 0.92)
    b.cylinder(R * 1.42, R * 0.22, axis_matrix((0, 0, R * 1.62), Z), steel, segs=32)
    q = Z.to_track_quat('Z', 'Y')
    for i in range(6):
        ang = TAU * i / 6.0
        off = q @ Vector((math.cos(ang) * R * 1.12, math.sin(ang) * R * 1.12, 0.0))
        b.cylinder(R * 0.10, R * 0.46, axis_matrix(Vector((0, 0, R * 1.62)) + off, Z),
                   mats['darksteel'], segs=6, smooth=False)
    b.cylinder(R * 0.82, R * 0.70, axis_matrix((0, 0, R * 2.08), Z), body, segs=28, r2=R * 0.60)
    b.cylinder(R * 0.62, R * 0.24, axis_matrix((0, 0, R * 2.52), Z), mats['darksteel'],
               segs=6, smooth=False)

    # --- stem
    b.cylinder(R * 0.14, R * 2.70, axis_matrix((0, 0, R * 2.15), Z), brass, segs=16)

    # --- hand wheel
    wz = R * 3.40
    wr = R * 2.05 * wheel_scale
    b.torus(wr, R * 0.17, axis_matrix((0, 0, wz), Z), wheel, mseg=44, nseg=12)
    b.cylinder(R * 0.46, R * 0.34, axis_matrix((0, 0, wz), Z), wheel, segs=24)
    spokes = 5
    for i in range(spokes):
        ang = TAU * i / spokes + hand_turn
        d = Vector((math.cos(ang), math.sin(ang), 0.0))
        length = wr - R * 0.22
        centre = d * (length * 0.5 + R * 0.20) + Vector((0, 0, wz))
        b.cylinder(R * 0.085, length, axis_matrix(centre, d), wheel, segs=12)
    b.cylinder(R * 0.26, R * 0.20, axis_matrix((0, 0, wz + R * 0.26), Z), brass,
               segs=6, smooth=False)

    ob = b.build()
    ob.matrix_world = basis_matrix(origin, flow_dir, stem_dir)
    return ob

def add_tee(name, r, origin, run_dir, branch_dir, mats):
    b = MeshBuilder(name)
    X = Vector((1.0, 0.0, 0.0))
    Z = Vector((0.0, 0.0, 1.0))
    b.cylinder(r * 1.28, r * 3.2, axis_matrix((0, 0, 0), X), mats['steel'], segs=30)
    b.cylinder(r * 1.10, r * 1.5, axis_matrix((0, 0, r * 0.9), Z), mats['steel'], segs=28)
    add_flange(b, (0, 0, r * 1.7), Z, r, mats, bolts=6)
    ob = b.build()
    ob.matrix_world = basis_matrix(origin, run_dir, branch_dir)
    return ob

def add_gauge(name, origin, up_dir, face_dir, s, mats):
    b = MeshBuilder(name)
    Z = Vector((0.0, 0.0, 1.0))
    Y = Vector((0.0, 1.0, 0.0))
    b.cylinder(s * 0.16, s * 0.55, axis_matrix((0, 0, s * 0.27), Z), mats['brass'], segs=6, smooth=False)
    b.cylinder(s * 0.12, s * 0.45, axis_matrix((0, 0, s * 0.72), Z), mats['brass'], segs=14)
    b.cylinder(s * 0.55, s * 0.24, axis_matrix((0, s * 0.02, s * 1.10), Y), mats['glass'], segs=32)
    b.cylinder(s * 0.47, s * 0.06, axis_matrix((0, s * 0.15, s * 1.10), Y), mats['face'], segs=32)
    b.box((s * 0.05, s * 0.04, s * 0.34),
          Matrix.Translation(Vector((s * 0.10, s * 0.19, s * 1.22))) @
          Matrix.Rotation(math.radians(-32.0), 4, 'Y'), mats['wheel'])
    ob = b.build()
    ob.matrix_world = basis_matrix(origin, face_dir, up_dir)
    return ob

# ----------------------------------------------------------------------------- assembly
def main():
    reset()
    mats = make_materials()

    # ---------------- ground, wall, plinths
    env = MeshBuilder("Environment")
    env.box((30.0, 30.0, 0.30), Matrix.Translation((0.0, 0.0, -0.15)), mats['concrete'])
    env.box((22.0, 0.35, 6.5), Matrix.Translation((0.0, 5.2, 3.25)), mats['wall'])
    for x in (-9.0, -3.0, 3.0, 9.0):
        env.box((0.45, 0.45, 6.5), Matrix.Translation((x, 4.95, 3.25)), mats['darksteel'])
    env.box((7.0, 4.0, 0.22), Matrix.Translation((-3.2, -1.2, 0.11)), mats['concrete'])
    env.build()

    # ---------------- pipe runs
    r1, r2, r3 = 0.26, 0.17, 0.13

    line1_pts = [(-6.4, 0.0, 1.35), (-3.2, 0.0, 1.35), (-3.2, 0.0, 3.05),
                 ( 1.9, 0.0, 3.05), ( 1.9, 0.0, 1.10), ( 5.6, 0.0, 1.10)]
    line2_pts = [(-1.2, 0.0, 3.05), (-1.2, -2.30, 3.05),
                 (-1.2, -2.30, 0.62), ( 3.6, -2.30, 0.62)]
    line3_pts = [(-5.6, 1.70, 2.45), ( 0.9, 1.70, 2.45),
                 ( 0.9, 1.70, 0.75), ( 4.8, 1.70, 0.75)]

    make_pipe("Pipe_Header", line1_pts, r1, mats['steel'], bend=0.62, bevel_res=10, arc_segs=12)
    make_pipe("Pipe_Branch", line2_pts, r2, mats['paintyel'], bend=0.46, bevel_res=8, arc_segs=10)
    make_pipe("Pipe_Utility", line3_pts, r3, mats['steel'], bend=0.36, bevel_res=8, arc_segs=10)

    # end flanges / blind caps on the open pipe ends
    ends = MeshBuilder("Pipe_Terminations")
    for pts, rr in ((line1_pts, r1), (line2_pts, r2), (line3_pts, r3)):
        a0 = path_tangent(pts[1], pts[0])
        a1 = path_tangent(pts[-2], pts[-1])
        add_flange(ends, Vector(pts[0]) + a0 * 0.10, a0, rr, mats)
        add_flange(ends, Vector(pts[-1]) - a1 * 0.10, a1, rr, mats)
    # a couple of mid-run bolted joints
    add_flange(ends, (-2.05, 0.0, 3.05), (1, 0, 0), r1, mats)
    add_flange(ends, ( 3.90, 0.0, 1.10), (1, 0, 0), r1, mats)
    add_flange(ends, (-1.20, -2.30, 1.55), (0, 0, 1), r2, mats)
    add_flange(ends, ( 1.60, 1.70, 0.75), (1, 0, 0), r3, mats)
    ends.build()

    # branch tee off the header
    add_tee("Tee_Branch", r1, (-1.2, 0.0, 3.05), (1, 0, 0), (0, -1, 0), mats)

    # ---------------- valves
    add_valve("Valve_Header_A", r1, (-4.90, 0.0, 1.35), (1, 0, 0), (0, 0, 1),
              mats, wheel_scale=1.15, hand_turn=0.20)
    add_valve("Valve_Header_B", r1, ( 0.40, 0.0, 3.05), (1, 0, 0), (0, 0, 1),
              mats, wheel_scale=1.00, hand_turn=0.55)
    add_valve("Valve_Header_C", r1, ( 4.75, 0.0, 1.10), (1, 0, 0), (0, 0, 1),
              mats, wheel_scale=1.10, hand_turn=0.90)
    add_valve("Valve_Branch_Riser", r2, (-1.20, -2.30, 1.95), (0, 0, -1), (0, -1, 0),
              mats, wheel_scale=1.25, hand_turn=0.35)
    add_valve("Valve_Branch_Low", r2, ( 2.25, -2.30, 0.62), (1, 0, 0), (0, 0, 1),
              mats, wheel_scale=1.20, hand_turn=1.10)
    add_valve("Valve_Utility_A", r3, (-3.60, 1.70, 2.45), (1, 0, 0), (0, 0, 1),
              mats, wheel_scale=1.35, hand_turn=0.15)
    add_valve("Valve_Utility_B", r3, ( 3.30, 1.70, 0.75), (1, 0, 0), (0, 0, 1),
              mats, wheel_scale=1.30, hand_turn=0.75)

    # ---------------- gauges
    add_gauge("Gauge_Header", (-2.55, 0.0, 3.05 + r1 * 0.6), (0, 0, 1), (0, -1, 0), 0.62, mats)
    add_gauge("Gauge_Branch", (0.55, -2.30, 0.62 + r2 * 0.6), (0, 0, 1), (0, -1, 0), 0.48, mats)

    # ---------------- pipe supports
    sup = MeshBuilder("Supports")
    Z = Vector((0.0, 0.0, 1.0))

    def stanchion(x, y, top_z, rr, axis=(1, 0, 0), width=0.17):
        h = top_z - rr - 0.10
        if h <= 0.1:
            return
        sup.box((0.62, 0.62, 0.07), Matrix.Translation((x, y, 0.035)), mats['darksteel'])
        sup.box((width, width, h), Matrix.Translation((x, y, h * 0.5 + 0.06)), mats['darksteel'])
        sup.box((0.46, 0.30, 0.06), Matrix.Translation((x, y, h + 0.09)), mats['darksteel'])
        sup.torus(rr + 0.055, 0.055, axis_matrix((x, y, top_z), axis), mats['darksteel'],
                  mseg=28, nseg=10)

    stanchion(-5.70, 0.0, 1.35, r1)
    stanchion(-4.00, 0.0, 1.35, r1)
    stanchion( 5.25, 0.0, 1.10, r1)
    stanchion(-2.00, 0.0, 3.05, r1, width=0.20)
    stanchion( 1.05, 0.0, 3.05, r1, width=0.20)
    stanchion( 1.00, -2.30, 0.62, r2)
    stanchion( 3.30, -2.30, 0.62, r2)
    stanchion(-4.60, 1.70, 2.45, r3, width=0.14)
    stanchion( 4.30, 1.70, 0.75, r3, width=0.14)

    # cross braces tying the two tall header stanchions together
    sup.box((3.15, 0.13, 0.13), Matrix.Translation((-0.475, 0.0, 1.55)), mats['darksteel'])
    sup.box((0.13, 0.13, 1.45), Matrix.Translation((-0.475, 0.0, 2.28)), mats['darksteel'])

    # hanger rods for the utility line where it crosses the header bay
    for x in (-1.90, 0.90):
        sup.cylinder(0.035, 1.9, axis_matrix((x, 1.70, 2.45 + 0.95), Z), mats['darksteel'], segs=10)
        sup.box((0.30, 0.30, 0.08), Matrix.Translation((x, 1.70, 2.45 + 1.90)), mats['darksteel'])
        sup.torus(r3 + 0.045, 0.045, axis_matrix((x, 1.70, 2.45), (1, 0, 0)),
                  mats['darksteel'], mseg=24, nseg=10)
    sup.build()

    # ---------------- lighting
    key = bpy.data.lights.new("Key", 'AREA')
    key.energy = 900.0
    key.size = 6.0
    key.color = (1.0, 0.96, 0.90)
    key_ob = link(bpy.data.objects.new("Key", key))
    key_ob.location = (-4.5, -7.0, 8.0)
    key_ob.rotation_euler = (math.radians(48.0), 0.0, math.radians(-32.0))

    fill = bpy.data.lights.new("Fill", 'AREA')
    fill.energy = 320.0
    fill.size = 8.0
    fill.color = (0.70, 0.80, 1.0)
    fill_ob = link(bpy.data.objects.new("Fill", fill))
    fill_ob.location = (7.5, -6.0, 4.0)
    fill_ob.rotation_euler = (math.radians(72.0), 0.0, math.radians(52.0))

    rim = bpy.data.lights.new("Rim", 'AREA')
    rim.energy = 260.0
    rim.size = 5.0
    rim_ob = link(bpy.data.objects.new("Rim", rim))
    rim_ob.location = (2.0, 4.4, 5.4)
    rim_ob.rotation_euler = (math.radians(-58.0), 0.0, math.radians(10.0))

    sun = bpy.data.lights.new("Sun", 'SUN')
    sun.energy = 1.6
    sun.angle = math.radians(3.0)
    sun_ob = link(bpy.data.objects.new("Sun", sun))
    sun_ob.rotation_euler = (math.radians(52.0), math.radians(6.0), math.radians(-40.0))

    world = bpy.data.worlds.new("World")
    world.use_nodes = True
    bg = world.node_tree.nodes["Background"]
    bg.inputs["Color"].default_value = (0.045, 0.050, 0.058, 1.0)
    bg.inputs["Strength"].default_value = 1.0
    bpy.context.scene.world = world

    # ---------------- camera
    cam = bpy.data.cameras.new("Camera")
    cam.lens = 40.0
    cam.clip_end = 200.0
    cam.dof.use_dof = True
    cam.dof.focus_distance = 12.5
    cam.dof.aperture_fsize = 4.0
    cam_ob = link(bpy.data.objects.new("Camera", cam))
    cam_ob.location = (9.6, -10.8, 5.4)
    target = Vector((-0.4, -0.6, 1.85))
    cam_ob.rotation_mode = 'QUATERNION'
    cam_ob.rotation_quaternion = (cam_ob.location - target).to_track_quat('Z', 'Y')
    bpy.context.scene.camera = cam_ob

    bpy.context.view_layer.update()

main()
