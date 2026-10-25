"""claude-080: A gantry crane with trolley and hook (Blender 4.5 LTS)."""
import bpy, bmesh, math
from mathutils import Vector, Matrix


# ------------------------------------------------------------------ helpers
def reset(bg=(0.06, 0.075, 0.10), strength=1.0):
    bpy.ops.wm.read_factory_settings(use_empty=True)
    w = bpy.data.worlds.new("World")
    w.use_nodes = True
    n = w.node_tree.nodes["Background"]
    n.inputs[0].default_value = (bg[0], bg[1], bg[2], 1.0)
    n.inputs[1].default_value = strength
    bpy.context.scene.world = w
    bpy.context.scene.render.resolution_x = 1600
    bpy.context.scene.render.resolution_y = 1050


def mat(name, col, rough=0.5, metal=0.0):
    m = bpy.data.materials.new(name)
    m.use_nodes = True
    b = m.node_tree.nodes["Principled BSDF"]
    b.inputs["Base Color"].default_value = (col[0], col[1], col[2], 1.0)
    b.inputs["Roughness"].default_value = rough
    b.inputs["Metallic"].default_value = metal
    return m


def to_obj(name, bm, mats=()):
    me = bpy.data.meshes.new(name)
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


def cy(bm, r, d, c, mi=0, axis='Z', seg=18):
    rot = {'Z': Matrix.Identity(4),
           'X': Matrix.Rotation(math.radians(90.0), 4, 'Y'),
           'Y': Matrix.Rotation(math.radians(-90.0), 4, 'X')}[axis]
    m = Matrix.Translation(Vector(c)) @ rot
    res = bmesh.ops.create_cone(bm, cap_ends=True, cap_tris=False, segments=seg,
                                radius1=r, radius2=r, depth=d, matrix=m)
    for f in _nf(res):
        f.material_index = mi


def strut(bm, p0, p1, w, h, mi=0, pad=0.0):
    p0, p1 = Vector(p0), Vector(p1)
    d = p1 - p0
    if d.length < 1e-7:
        return
    bx(bm, (d.length + pad, w, h), (p0 + p1) * 0.5, mi,
       d.to_track_quat('X', 'Z').to_matrix().to_4x4())


def pipe(bm, p0, p1, r, mi=0, seg=12):
    p0, p1 = Vector(p0), Vector(p1)
    d = p1 - p0
    if d.length < 1e-7:
        return
    m = Matrix.Translation((p0 + p1) * 0.5) @ d.to_track_quat('Z', 'Y').to_matrix().to_4x4()
    res = bmesh.ops.create_cone(bm, cap_ends=True, cap_tris=False, segments=seg,
                                radius1=r, radius2=r, depth=d.length, matrix=m)
    for f in _nf(res):
        f.material_index = mi


def box_obj(name, size, loc, m, rot=(0.0, 0.0, 0.0)):
    bm = bmesh.new()
    bx(bm, size, (0.0, 0.0, 0.0))
    ob = to_obj(name, bm, (m,))
    ob.location = loc
    ob.rotation_euler = rot
    return ob


def plane(name, size, m, loc=(0.0, 0.0, 0.0)):
    bm = bmesh.new()
    bmesh.ops.create_grid(bm, x_segments=8, y_segments=8, size=size * 0.5)
    ob = to_obj(name, bm, (m,))
    ob.location = loc
    return ob


def sun(name, energy, rot, ang=0.02, col=(1.0, 0.96, 0.90)):
    d = bpy.data.lights.new(name, 'SUN')
    d.energy = energy
    d.angle = ang
    d.color = col
    ob = bpy.data.objects.new(name, d)
    ob.rotation_euler = rot
    bpy.context.collection.objects.link(ob)
    return ob


def area(name, energy, loc, target, size=12.0, col=(1.0, 1.0, 1.0)):
    d = bpy.data.lights.new(name, 'AREA')
    d.energy = energy
    d.size = size
    d.color = col
    ob = bpy.data.objects.new(name, d)
    ob.location = loc
    ob.rotation_euler = (Vector(target) - Vector(loc)).to_track_quat('-Z', 'Y').to_euler()
    bpy.context.collection.objects.link(ob)
    return ob


def camera(loc, target, lens=40.0):
    c = bpy.data.cameras.new("Camera")
    c.lens = lens
    ob = bpy.data.objects.new("Camera", c)
    ob.location = loc
    ob.rotation_euler = (Vector(target) - Vector(loc)).to_track_quat('-Z', 'Y').to_euler()
    bpy.context.collection.objects.link(ob)
    bpy.context.scene.camera = ob
    return ob


def bevel(ob, width=0.02, segments=2):
    mo = ob.modifiers.new("Bevel", 'BEVEL')
    mo.width = width
    mo.segments = segments
    mo.limit_method = 'ANGLE'
    mo.angle_limit = math.radians(40.0)
    return mo


# ------------------------------------------------------------------ layout
LEG_X = 8.0          # rails run along Y at x = +/- LEG_X
GY = 1.40            # girder / column offset in Y
TOP = 9.00           # top of the girders
GD = 1.10            # girder depth
GIRDER_L = 18.40
TROLLEY_X = 2.60
HOOK_Z = 4.05
RAIL_Z = 0.16


def build_ground(concrete, steel, rail_mat):
    plane("Slab", 90.0, concrete, (0.0, 0.0, 0.0))
    bm = bmesh.new()
    for sx in (-1.0, 1.0):
        x = sx * LEG_X
        bx(bm, (1.10, 30.0, 0.10), (x, 0.0, 0.05), 0)        # rail plinth
        for sy in (-1.0, 1.0):
            bx(bm, (0.34, 30.0, 0.12), (x + sy * 0.0, 0.0, RAIL_Z), 1)
            break
        bx(bm, (0.16, 30.0, 0.08), (x, 0.0, RAIL_Z + 0.10), 1)   # rail head
        for i in range(-14, 15):
            bx(bm, (0.60, 0.16, 0.05), (x, i * 1.0, 0.115), 0)   # sole plates
    to_obj("Runway", bm, (concrete, rail_mat))
    # painted travel-limit markings
    for sx in (-1.0, 1.0):
        for sy in (-1.0, 1.0):
            box_obj("LimitMark", (1.6, 0.18, 0.01),
                    (sx * LEG_X, sy * 12.0, 0.11), steel)


def build_leg(bm, x, mi_paint=0, mi_steel=1):
    z0, z1 = 1.05, TOP - GD
    for sy in (-1.0, 1.0):
        bx(bm, (0.50, 0.50, z1 - z0), (x, sy * GY, (z0 + z1) * 0.5), mi_paint)
    # lattice bracing between the two columns of the portal leg
    n = 7
    for i in range(n):
        za = z0 + (z1 - z0) * i / n
        zb = z0 + (z1 - z0) * (i + 1) / n
        y0 = -GY + 0.25 if i % 2 == 0 else GY - 0.25
        y1 = GY - 0.25 if i % 2 == 0 else -GY + 0.25
        strut(bm, (x, y0, za), (x, y1, zb), 0.22, 0.16, mi_paint)
        bx(bm, (0.30, 2.0 * GY - 0.5, 0.26), (x, 0.0, za), mi_paint)
    bx(bm, (0.30, 2.0 * GY - 0.5, 0.26), (x, 0.0, z1 - 0.15), mi_paint)
    # knee braces up into the girders
    for sy in (-1.0, 1.0):
        strut(bm, (x, sy * GY, z1 - 1.6), (x + 1.9, sy * GY, z1 + 0.05), 0.24, 0.18, mi_paint)
        strut(bm, (x, sy * GY, z1 - 1.6), (x - 1.9, sy * GY, z1 + 0.05), 0.24, 0.18, mi_paint)
    # equalizer beam and bogies on the rail
    bx(bm, (0.55, 2.0 * GY + 1.5, 0.45), (x, 0.0, 0.85), mi_paint)
    for sy in (-1.0, 1.0):
        bx(bm, (0.50, 1.55, 0.36), (x, sy * (GY + 0.35), 0.52), mi_steel)
        for dy in (-0.52, 0.52):
            cy(bm, 0.34, 0.16, (x, sy * (GY + 0.35) + dy, 0.36), mi_steel, axis='X', seg=20)
            cy(bm, 0.09, 0.60, (x, sy * (GY + 0.35) + dy, 0.36), mi_steel, axis='X', seg=10)
        # rail sweeps and buffers
        bx(bm, (0.30, 0.10, 0.30), (x, sy * (GY + 1.30), 0.32), mi_steel)
        cy(bm, 0.16, 0.30, (x, sy * (GY + 1.55), 0.85), mi_steel, axis='Y', seg=14)


def build_bridge(paint, steel, grate):
    bm = bmesh.new()
    for x in (-LEG_X, LEG_X):
        build_leg(bm, x)
    for sy in (-1.0, 1.0):
        bx(bm, (GIRDER_L, 0.60, GD), (0.0, sy * GY, TOP - GD * 0.5), 0)
        bx(bm, (GIRDER_L, 0.90, 0.10), (0.0, sy * GY, TOP - 0.05), 0)   # top flange
        bx(bm, (GIRDER_L, 0.90, 0.10), (0.0, sy * GY, TOP - GD + 0.05), 0)
        for i in range(-9, 10):
            bx(bm, (0.06, 0.86, GD - 0.2), (i * 1.0, sy * (GY + 0.32), TOP - GD * 0.5), 0)
    # cross beams and top-flange diagonal bracing
    for x in (-9.0, -LEG_X, -4.0, 0.0, 4.0, LEG_X, 9.0):
        bx(bm, (0.42, 2.0 * GY - 0.6, 0.42), (x, 0.0, TOP - GD + 0.35), 0)
    for i in range(-8, 8, 2):
        strut(bm, (i * 1.0, -GY + 0.3, TOP - 0.10), ((i + 2) * 1.0, GY - 0.3, TOP - 0.10),
              0.18, 0.10, 0)
        strut(bm, (i * 1.0, GY - 0.3, TOP - 0.10), ((i + 2) * 1.0, -GY + 0.3, TOP - 0.10),
              0.18, 0.10, 0)
    # crane rails on the girder top flanges for the trolley
    for sy in (-1.0, 1.0):
        bx(bm, (GIRDER_L, 0.14, 0.10), (0.0, sy * GY, TOP + 0.05), 1)
    bevel(to_obj("Bridge", bm, (paint, steel)), 0.012, 1)

    # maintenance walkway with handrail and toe board, outboard of one girder
    bm = bmesh.new()
    wy = GY + 0.95
    n = int(GIRDER_L / 0.14)
    for i in range(n):
        bx(bm, (0.05, 1.10, 0.05), (-GIRDER_L * 0.5 + 0.07 + i * 0.14, wy, TOP - GD + 0.62), 0)
    for dy in (-0.55, 0.55):
        bx(bm, (GIRDER_L, 0.06, 0.14), (0.0, wy + dy, TOP - GD + 0.58), 1)
    for i in range(-9, 10, 2):
        bx(bm, (0.07, 0.07, 1.05), (i * 1.0, wy + 0.55, TOP - GD + 1.15), 1)
        strut(bm, (i * 1.0, wy + 0.5, TOP - GD + 0.55), (i * 1.0, GY + 0.30, TOP - GD + 0.15),
              0.10, 0.08, 1)
    for h in (0.60, 1.10):
        pipe(bm, (-GIRDER_L * 0.5, wy + 0.55, TOP - GD + 0.62 + h),
             (GIRDER_L * 0.5, wy + 0.55, TOP - GD + 0.62 + h), 0.03, 1)
    bx(bm, (GIRDER_L, 0.04, 0.16), (0.0, wy + 0.56, TOP - GD + 0.70), 1)
    to_obj("Walkway", bm, (grate, paint))

    # access ladder with safety cage on the far leg
    bm = bmesh.new()
    lx = -LEG_X
    ly = GY + 1.05
    for dx in (-0.28, 0.28):
        bx(bm, (0.06, 0.10, TOP - GD + 0.9), (lx + dx, ly, (TOP - GD + 0.9) * 0.5), 0)
    k = int((TOP - GD + 0.5) / 0.32)
    for i in range(1, k):
        pipe(bm, (lx - 0.28, ly, i * 0.32), (lx + 0.28, ly, i * 0.32), 0.018, 0, seg=8)
    for i in range(3, k, 4):
        for a in range(7):
            ang = math.radians(180.0 * a / 6.0)
            bx(bm, (0.09, 0.09, 0.09),
               (lx + 0.42 * math.cos(ang), ly + 0.42 * math.sin(ang), i * 0.32), 0)
    to_obj("Ladder", bm, (paint,))


def build_machinery(paint, steel, glass, dark):
    # machinery house sitting over one leg, clear of the trolley travel
    bm = bmesh.new()
    bx(bm, (2.60, 2.90, 1.60), (LEG_X, 0.0, TOP + 0.90), 0)
    bx(bm, (2.80, 3.10, 0.10), (LEG_X, 0.0, TOP + 1.75), 1)
    for sy in (-1.0, 1.0):
        for dx in (-0.65, 0.65):
            bx(bm, (0.60, 0.05, 0.45), (LEG_X + dx, sy * 1.46, TOP + 1.10), 2)
    bx(bm, (0.05, 0.90, 1.40), (LEG_X - 1.31, 0.0, TOP + 0.85), 1)
    for i in range(4):
        bx(bm, (2.40, 0.06, 0.06), (LEG_X, -1.05 + i * 0.70, TOP + 1.68), 1)
    to_obj("MachineryHouse", bm, (paint, steel, glass))

    # operator cab hung under the bridge
    bm = bmesh.new()
    cx, cyy, cz = -5.20, GY + 1.05, TOP - GD - 1.05
    bx(bm, (1.90, 1.70, 2.00), (cx, cyy, cz), 0)
    bx(bm, (2.05, 1.85, 0.10), (cx, cyy, cz + 1.05), 1)
    bx(bm, (1.70, 0.05, 1.10), (cx, cyy - 0.86, cz + 0.30), 2)
    bx(bm, (0.05, 1.50, 1.10), (cx - 0.96, cyy, cz + 0.30), 2)
    bx(bm, (1.70, 1.50, 0.05), (cx, cyy, cz - 0.85), 1)
    for dx in (-0.75, 0.75):
        strut(bm, (cx + dx, cyy - 0.4, cz + 1.05), (cx + dx, GY + 0.30, TOP - GD + 0.10),
              0.12, 0.10, 1)
    bx(bm, (1.60, 0.30, 0.06), (cx, cyy - 0.60, cz - 0.55), 1)
    to_obj("OperatorCab", bm, (paint, steel, glass))

    # festoon cable track along the bridge
    bm = bmesh.new()
    bx(bm, (GIRDER_L - 1.0, 0.08, 0.08), (0.0, -GY - 0.55, TOP - GD + 0.45), 0)
    for i in range(-8, 9):
        bx(bm, (0.10, 0.16, 0.22), (i * 1.05, -GY - 0.55, TOP - GD + 0.32), 0)
        pipe(bm, (i * 1.05, -GY - 0.55, TOP - GD + 0.22),
             ((i + 0.5) * 1.05, -GY - 0.62, TOP - GD - 0.05), 0.022, 0, seg=6)
    to_obj("Festoon", bm, (dark,))


def build_trolley(paint, steel, dark, rope_mat):
    bm = bmesh.new()
    tz = TOP + 0.10
    # wheels riding the girder rails, then the trolley frame above them
    for dx in (-1.15, 1.15):
        for sy in (-1.0, 1.0):
            cy(bm, 0.30, 0.18, (TROLLEY_X + dx, sy * GY, tz + 0.30), 1, axis='Y', seg=20)
            cy(bm, 0.09, 0.46, (TROLLEY_X + dx, sy * GY, tz + 0.30), 1, axis='Y', seg=10)
    for sy in (-1.0, 1.0):
        bx(bm, (3.20, 0.14, 0.55), (TROLLEY_X, sy * (GY + 0.18), tz + 0.42), 0)
    bx(bm, (3.30, 2.0 * GY + 0.50, 0.32), (TROLLEY_X, 0.0, tz + 0.82), 0)
    for i in range(-3, 4):
        bx(bm, (0.16, 2.0 * GY + 0.30, 0.16), (TROLLEY_X + i * 0.55, 0.0, tz + 1.02), 0)
    # hoist drum, gearbox and motor
    cy(bm, 0.42, 2.10, (TROLLEY_X - 0.75, 0.0, tz + 1.50), 1, axis='Y', seg=24)
    for i in range(9):
        cy(bm, 0.45, 0.05, (TROLLEY_X - 0.75, -0.95 + i * 0.24, tz + 1.50), 1, axis='Y', seg=20)
    for sy in (-1.0, 1.0):
        bx(bm, (0.70, 0.16, 0.70), (TROLLEY_X - 0.75, sy * 1.12, tz + 1.50), 0)
    bx(bm, (0.85, 0.80, 0.80), (TROLLEY_X + 0.55, 0.55, tz + 1.45), 0)
    cy(bm, 0.30, 0.95, (TROLLEY_X + 1.35, 0.55, tz + 1.45), 1, axis='X', seg=18)
    bx(bm, (0.60, 0.60, 0.55), (TROLLEY_X + 0.60, -0.75, tz + 1.40), 0)
    # travel drive on one wheel axle
    cy(bm, 0.22, 0.70, (TROLLEY_X + 1.15, GY - 0.70, tz + 0.30), 1, axis='Y', seg=14)
    # rope sheaves under the frame
    for dx in (-0.42, 0.42):
        for sy in (-1.0, 1.0):
            cy(bm, 0.20, 0.09, (TROLLEY_X + dx, sy * 0.22, tz + 0.60), 1, axis='Y', seg=18)
    bevel(to_obj("Trolley", bm, (paint, steel)), 0.01, 1)

    # four rope falls down to the hook block
    bm = bmesh.new()
    for dx in (-0.42, 0.42):
        for sy in (-1.0, 1.0):
            pipe(bm, (TROLLEY_X + dx, sy * 0.22, tz + 0.60),
                 (TROLLEY_X + dx, sy * 0.22, HOOK_Z + 0.28), 0.025, 0, seg=8)
    pipe(bm, (TROLLEY_X - 0.75, 0.98, tz + 1.50),
         (TROLLEY_X - 0.42, 0.22, tz + 0.75), 0.025, 0, seg=8)
    to_obj("Ropes", bm, (rope_mat,))

    # hook block: shell, sheaves, thrust bearing and swivel
    bm = bmesh.new()
    bx(bm, (1.10, 0.62, 0.62), (TROLLEY_X, 0.0, HOOK_Z), 0)
    for dx in (-0.30, 0.30):
        cy(bm, 0.24, 0.34, (TROLLEY_X + dx, 0.0, HOOK_Z + 0.14), 1, axis='Y', seg=20)
    for sy in (-1.0, 1.0):
        bx(bm, (1.20, 0.06, 0.70), (TROLLEY_X, sy * 0.33, HOOK_Z), 1)
    cy(bm, 0.16, 0.22, (TROLLEY_X, 0.0, HOOK_Z - 0.40), 1, seg=18)
    cy(bm, 0.10, 0.26, (TROLLEY_X, 0.0, HOOK_Z - 0.55), 1, seg=14)
    bevel(to_obj("HookBlock", bm, (dark, steel)), 0.012, 2)
    return tz


def build_hook(name, loc, m):
    """Hook shank plus a tapered J-curve, swept with a bevelled poly curve."""
    cu = bpy.data.curves.new(name, 'CURVE')
    cu.dimensions = '3D'
    cu.bevel_depth = 0.075
    cu.bevel_resolution = 5
    cu.resolution_u = 8
    cu.use_fill_caps = True
    pts = [(0.0, 0.0, 0.0), (0.0, 0.0, -0.16), (0.0, 0.0, -0.30)]
    seg = 26
    for i in range(1, seg + 1):
        a = math.radians(90.0 + 250.0 * i / seg)
        pts.append((0.30 * math.cos(a), 0.0, -0.60 + 0.30 * math.sin(a)))
    sp = cu.splines.new('POLY')
    sp.points.add(len(pts) - 1)
    taper_from = len(pts) - 8
    for i, p in enumerate(pts):
        sp.points[i].co = (p[0], p[1], p[2], 1.0)
        if i < taper_from:
            sp.points[i].radius = 1.0 if i > 1 else 0.75
        else:
            sp.points[i].radius = max(0.22, 1.0 - (i - taper_from) * 0.12)
    ob = bpy.data.objects.new(name, cu)
    ob.location = loc
    cu.materials.append(m)
    bpy.context.collection.objects.link(ob)
    return ob


def main():
    reset()
    paint = mat("CranePaint", (0.72, 0.46, 0.03), 0.48, 0.25)
    steel = mat("Steel", (0.30, 0.31, 0.33), 0.42, 0.85)
    rail_mat = mat("RailSteel", (0.42, 0.42, 0.44), 0.30, 0.95)
    dark = mat("DarkSteel", (0.09, 0.09, 0.10), 0.55, 0.70)
    grate = mat("Grating", (0.36, 0.37, 0.38), 0.55, 0.60)
    glass = mat("CabGlass", (0.05, 0.07, 0.09), 0.15, 0.20)
    concrete = mat("Concrete", (0.36, 0.355, 0.34), 0.88)
    rope_mat = mat("WireRope", (0.22, 0.22, 0.235), 0.45, 0.90)

    build_ground(concrete, steel, rail_mat)
    build_bridge(paint, steel, grate)
    build_machinery(paint, steel, glass, dark)
    build_trolley(paint, steel, dark, rope_mat)
    build_hook("Hook", (TROLLEY_X, 0.0, HOOK_Z - 0.62), steel)

    # a load parked under the hook for scale
    bevel(box_obj("Load", (2.60, 1.60, 1.20), (TROLLEY_X, 0.0, 0.60), dark), 0.02, 2)
    bm = bmesh.new()
    for sx in (-1.0, 1.0):
        for sy in (-1.0, 1.0):
            pipe(bm, (TROLLEY_X + sx * 1.20, sy * 0.70, 1.20),
                 (TROLLEY_X, 0.0, HOOK_Z - 1.05), 0.02, 0, seg=6)
    to_obj("Slings", bm, (rope_mat,))

    sun("Sun", 3.2, (math.radians(50.0), math.radians(-6.0), math.radians(-48.0)))
    area("SkyFill", 900.0, (-18.0, -22.0, 18.0), (0.0, 0.0, 5.0), 30.0, (0.58, 0.70, 1.0))
    area("Rim", 350.0, (16.0, 14.0, 10.0), (2.0, 0.0, 6.0), 16.0, (1.0, 0.92, 0.80))
    camera((-17.5, -21.0, 9.5), (0.5, 0.0, 5.2), lens=40.0)


main()
