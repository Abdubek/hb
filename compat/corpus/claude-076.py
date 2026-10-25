"""claude-076: A fire escape staircase on a building wall (Blender 4.5 LTS)."""
import bpy, bmesh, math
from mathutils import Vector, Matrix


# ------------------------------------------------------------------ helpers
def reset(bg=(0.035, 0.045, 0.065), strength=1.0):
    bpy.ops.wm.read_factory_settings(use_empty=True)
    w = bpy.data.worlds.new("World")
    w.use_nodes = True
    n = w.node_tree.nodes["Background"]
    n.inputs[0].default_value = (bg[0], bg[1], bg[2], 1.0)
    n.inputs[1].default_value = strength
    bpy.context.scene.world = w
    bpy.context.scene.render.resolution_x = 1500
    bpy.context.scene.render.resolution_y = 1150


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


def cy(bm, r, d, c, mi=0, axis='Z', seg=16):
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


def sun(name, energy, rot, ang=0.02, col=(1.0, 0.97, 0.92)):
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


def point(name, energy, loc, radius=0.15, col=(1.0, 0.85, 0.62)):
    d = bpy.data.lights.new(name, 'POINT')
    d.energy = energy
    d.shadow_soft_size = radius
    d.color = col
    ob = bpy.data.objects.new(name, d)
    ob.location = loc
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


def bevel(ob, width=0.008, segments=2):
    mo = ob.modifiers.new("Bevel", 'BEVEL')
    mo.width = width
    mo.segments = segments
    mo.limit_method = 'ANGLE'
    mo.angle_limit = math.radians(40.0)
    return mo


# ------------------------------------------------------------------ layout
Y0, Y1 = -1.40, 0.0                      # landing outer edge / wall face
LEV = [3.60, 7.10, 10.60]                # landing levels
LAND = [(0.0, 2.50), (5.30, 7.80), (0.0, 2.50)]
FLIGHTS = [(2.50, 5.30), (5.30, 2.50)]   # x-run of each flight (alternating)
RAIL_H = 1.06


def grating(bm, x0, x1, y0, y1, z, mi=0, bar_w=0.022, gap=0.055, th=0.05):
    """Bar-grating landing deck inside a perimeter channel frame."""
    span = y1 - y0
    n = max(2, int(span / (bar_w + gap)))
    step = span / n
    for i in range(n + 1):
        bx(bm, (x1 - x0, bar_w, th), ((x0 + x1) * 0.5, y0 + i * step, z - th * 0.5), mi)
    for t in (0.25, 0.75):
        bx(bm, (0.02, span, 0.018), (x0 + (x1 - x0) * t, (y0 + y1) * 0.5, z - th + 0.01), mi)
    bx(bm, (x1 - x0 + 0.10, 0.05, 0.11), ((x0 + x1) * 0.5, y0 - 0.025, z - 0.055), mi)
    bx(bm, (x1 - x0 + 0.10, 0.05, 0.11), ((x0 + x1) * 0.5, y1 + 0.025, z - 0.055), mi)
    for x in (x0 - 0.025, x1 + 0.025):
        bx(bm, (0.05, span + 0.10, 0.11), (x, (y0 + y1) * 0.5, z - 0.055), mi)


def rail_level(bm, p0, p1, mi=0, h=RAIL_H, post_step=1.15, balu_step=0.19):
    a, b = Vector(p0), Vector(p1)
    d = b - a
    length = d.length
    if length < 1e-6:
        return
    u = d.normalized()
    n = max(1, int(round(length / post_step)))
    for i in range(n + 1):
        p = a + u * (length * i / n)
        bx(bm, (0.05, 0.05, h), (p.x, p.y, p.z + h * 0.5), mi)
    pipe(bm, a + Vector((0, 0, h)), b + Vector((0, 0, h)), 0.026, mi)
    pipe(bm, a + Vector((0, 0, h * 0.52)), b + Vector((0, 0, h * 0.52)), 0.020, mi)
    nb = max(1, int(length / balu_step))
    for i in range(1, nb):
        p = a + u * (length * i / nb)
        bx(bm, (0.014, 0.014, h * 0.5), (p.x, p.y, p.z + h * 0.26), mi)
    kx = abs(d.x) + 0.05 if abs(d.x) > 1e-6 else 0.03
    ky = abs(d.y) + 0.05 if abs(d.y) > 1e-6 else 0.03
    bx(bm, (kx, ky, 0.10), ((a.x + b.x) * 0.5, (a.y + b.y) * 0.5, a.z + 0.05), mi)


def rail_slope(bm, x0, z0, x1, z1, y, mi=0, h=RAIL_H):
    ang = math.atan2(z1 - z0, x1 - x0)
    basis = Matrix.Rotation(-ang, 4, 'Y')
    length = math.hypot(x1 - x0, z1 - z0)
    for lift, r in ((h, 0.026), (h * 0.52, 0.020)):
        bx(bm, (length, 2 * r, 2 * r),
           ((x0 + x1) * 0.5, y, (z0 + z1) * 0.5 + lift), mi, basis)
    n = max(2, int(length / 0.95))
    for i in range(n + 1):
        t = i / n
        bx(bm, (0.05, 0.05, h), (x0 + (x1 - x0) * t, y, z0 + (z1 - z0) * t + h * 0.5), mi)
    nb = max(2, int(length / 0.21))
    for i in range(1, nb):
        t = i / nb
        bx(bm, (0.014, 0.014, h * 0.5),
           (x0 + (x1 - x0) * t, y, z0 + (z1 - z0) * t + h * 0.27), mi)


def flight(bm, x0, x1, z0, z1, y0, y1, mi=0, steps=12):
    """Open-riser stair flight with channel stringers and grated treads."""
    ang = math.atan2(z1 - z0, x1 - x0)
    basis = Matrix.Rotation(-ang, 4, 'Y')
    length = math.hypot(x1 - x0, z1 - z0)
    run = (x1 - x0) / steps
    rise = (z1 - z0) / steps
    for y in (y0 + 0.07, y1 - 0.07):
        bx(bm, (length + 0.30, 0.05, 0.30),
           ((x0 + x1) * 0.5, y, (z0 + z1) * 0.5 - 0.20), mi, basis)
    tw = (y1 - y0) - 0.22
    for i in range(steps):
        cx = x0 + run * (i + 0.5)
        cz = z0 + rise * (i + 1) - 0.025
        w = abs(run) * 0.96
        bx(bm, (w, tw, 0.035), (cx, (y0 + y1) * 0.5, cz), mi)
        bx(bm, (w, 0.035, 0.055), (cx, (y0 + y1) * 0.5 - tw * 0.5, cz - 0.01), mi)
        for t in (-0.22, 0.22):
            bx(bm, (w, 0.016, 0.05), (cx, (y0 + y1) * 0.5 + t * tw, cz - 0.04), mi)
    rail_slope(bm, x0, z0, x1, z1, y0 + 0.05, mi)


def ladder(bm, x_lo, x_hi, z_top, z_bot, y, mi=0):
    for x in (x_lo, x_hi):
        bx(bm, (0.05, 0.09, z_top - z_bot), (x, y, (z_top + z_bot) * 0.5), mi)
        bx(bm, (0.10, 0.14, 0.06), (x, y, z_bot - 0.02), mi)
    n = int((z_top - z_bot) / 0.30)
    for i in range(1, n):
        z = z_bot + i * (z_top - z_bot) / n
        pipe(bm, (x_lo, y, z), (x_hi, y, z), 0.018, mi, seg=8)


def build_fire_escape(steel, rust):
    bm = bmesh.new()
    for (lx0, lx1), z in zip(LAND, LEV):
        grating(bm, lx0, lx1, Y0, Y1, z)
        rail_level(bm, (lx0, Y0, z), (lx1, Y0, z))
        for lx in (lx0, lx1):
            served = any(abs(lx - fx) < 0.05 for f in FLIGHTS for fx in f)
            if not served:
                rail_level(bm, (lx, Y0, z), (lx, Y1 - 0.10, z), post_step=0.7)
        for lx in (lx0 + 0.25, (lx0 + lx1) * 0.5, lx1 - 0.25):
            strut(bm, (lx, Y1 - 0.02, z - 1.10), (lx, Y0 + 0.10, z - 0.14), 0.05, 0.10, 1)
            bx(bm, (0.24, 0.10, 0.30), (lx, Y1 - 0.03, z - 0.90), 1)
        bx(bm, (lx1 - lx0 + 0.40, 0.10, 0.20), ((lx0 + lx1) * 0.5, Y1 - 0.06, z - 0.12), 1)
    for (fx0, fx1), z0, z1 in zip(FLIGHTS, LEV[:-1], LEV[1:]):
        flight(bm, fx0, fx1, z0, z1, Y0, Y1)
    ladder(bm, 0.45, 1.55, LEV[0] - 0.05, 0.35, Y0 + 0.28)
    bx(bm, (1.35, 0.06, 0.06), (1.0, Y0 + 0.28, LEV[0] + 0.95))
    ob = to_obj("FireEscape", bm, (steel, rust))
    bevel(ob, 0.006, 1)
    return ob


def build_building(brick, concrete, glass, trim, stone):
    bevel(box_obj("Facade", (16.0, 0.60, 15.0), (4.0, 0.30, 7.5), brick), 0.02, 1)
    for z in (0.45, 5.35, 8.85, 12.35, 14.60):
        box_obj("Course", (16.2, 0.16, 0.22), (4.0, -0.02, z), stone)
    box_obj("Cornice", (16.6, 0.45, 0.50), (4.0, -0.12, 14.95), stone)
    box_obj("Parapet", (16.2, 0.30, 0.90), (4.0, 0.15, 15.40), brick)
    for z in (1.85, 5.35, 8.85, 12.35):
        for x in (-2.45, 1.20, 6.55, 10.30):
            box_obj("Glass", (1.15, 0.05, 1.62), (x, 0.14, z), glass)
            box_obj("Sash", (1.18, 0.05, 0.05), (x, 0.10, z), trim)
            box_obj("Mullion", (0.05, 0.05, 1.62), (x, 0.10, z), trim)
            for dx in (-0.63, 0.63):
                box_obj("Jamb", (0.09, 0.22, 1.80), (x + dx, 0.02, z), trim)
            box_obj("Head", (1.44, 0.22, 0.10), (x, 0.02, z + 0.90), stone)
            box_obj("Sill", (1.55, 0.28, 0.09), (x, -0.02, z - 0.88), stone)
    box_obj("FireDoor", (1.05, 0.10, 2.05), (3.90, 0.06, LEV[0] + 1.05), trim)
    box_obj("DoorFrame", (1.25, 0.16, 2.25), (3.90, 0.14, LEV[0] + 1.10), stone)
    box_obj("DoorBar", (0.75, 0.07, 0.07), (3.90, -0.03, LEV[0] + 1.02), concrete)
    plane("Sidewalk", 60.0, concrete, (2.0, -8.0, 0.0))
    box_obj("Curb", (40.0, 0.35, 0.30), (2.0, -6.2, 0.06), stone)
    box_obj("Street", (40.0, 14.0, 0.02), (2.0, -13.3, -0.02), concrete)
    box_obj("BasementVent", (2.2, 0.12, 0.90), (8.6, -0.05, 0.50), trim)


def main():
    reset()
    brick = mat("Brick", (0.30, 0.115, 0.085), 0.85)
    concrete = mat("Concrete", (0.35, 0.34, 0.33), 0.90)
    stone = mat("CastStone", (0.52, 0.50, 0.46), 0.75)
    glass = mat("WindowGlass", (0.035, 0.05, 0.065), 0.12, 0.15)
    trim = mat("Trim", (0.10, 0.12, 0.11), 0.55)
    steel = mat("PaintedSteel", (0.075, 0.082, 0.085), 0.52, 0.35)
    rust = mat("RustySteel", (0.24, 0.115, 0.055), 0.85, 0.25)
    build_building(brick, concrete, glass, trim, stone)
    build_fire_escape(steel, rust)
    sun("Sun", 3.4, (math.radians(56.0), math.radians(6.0), math.radians(-38.0)))
    area("SkyFill", 320.0, (-4.0, -22.0, 12.0), (4.0, 0.0, 7.0), 16.0, (0.55, 0.68, 1.0))
    point("StairLamp", 40.0, (3.90, -0.55, LEV[0] + 2.35), 0.12)
    camera((-8.5, -15.0, 4.2), (3.6, -0.9, 7.2), lens=35.0)


main()
