"""claude-077: A loading dock with ramp, bumpers and overhead door (Blender 4.5 LTS)."""
import bpy, bmesh, math
from mathutils import Vector, Matrix


# ------------------------------------------------------------------ helpers
def reset(bg=(0.05, 0.06, 0.08), strength=1.0):
    bpy.ops.wm.read_factory_settings(use_empty=True)
    w = bpy.data.worlds.new("World")
    w.use_nodes = True
    n = w.node_tree.nodes["Background"]
    n.inputs[0].default_value = (bg[0], bg[1], bg[2], 1.0)
    n.inputs[1].default_value = strength
    bpy.context.scene.world = w
    bpy.context.scene.render.resolution_x = 1600
    bpy.context.scene.render.resolution_y = 1000


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


def prism(name, profile, y0, y1, m):
    """Closed prism from a convex XZ profile extruded between two Y planes."""
    bm = bmesh.new()
    lo = [bm.verts.new((x, y0, z)) for x, z in profile]
    hi = [bm.verts.new((x, y1, z)) for x, z in profile]
    n = len(profile)
    for i in range(n):
        j = (i + 1) % n
        bm.faces.new((lo[i], lo[j], hi[j], hi[i]))
    bm.faces.new(tuple(lo))
    bm.faces.new(tuple(reversed(hi)))
    return to_obj(name, bm, (m,))


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


def point(name, energy, loc, radius=0.2, col=(1.0, 0.88, 0.70)):
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


def bevel(ob, width=0.012, segments=2):
    mo = ob.modifiers.new("Bevel", 'BEVEL')
    mo.width = width
    mo.segments = segments
    mo.limit_method = 'ANGLE'
    mo.angle_limit = math.radians(40.0)
    return mo


# --------------------------------------------------------------- dimensions
DOCK_Z = 1.25
OPEN_W, OPEN_H = 3.60, 3.35
OPEN_X0, OPEN_X1 = -1.80, 1.80
OPEN_TOP = DOCK_Z + OPEN_H
WALL_T = 0.40                 # interior is +Y
FRONT = -1.85                 # outer face of the dock platform


def build_building(block, panel, steel, dark, glass):
    for cx in (-5.55, 5.55):
        bevel(box_obj("Wall", (7.50, WALL_T, 7.0), (cx, WALL_T * 0.5, 3.5), block), 0.02, 1)
    box_obj("Header", (OPEN_W, WALL_T, 7.0 - OPEN_TOP),
            (0.0, WALL_T * 0.5, (OPEN_TOP + 7.0) * 0.5), block)
    box_obj("PanelBand", (18.6, 0.10, 2.1), (0.0, -0.05, 5.9), panel)
    box_obj("Coping", (18.9, 0.62, 0.30), (0.0, 0.16, 7.1), steel)
    for i in range(-9, 10):
        box_obj("PanelRib", (0.05, 0.05, 2.1), (i + 0.5, -0.12, 5.9), panel)
    for x in (OPEN_X0, OPEN_X1):
        box_obj("Jamb", (0.14, WALL_T, OPEN_H), (x, WALL_T * 0.5, DOCK_Z + OPEN_H * 0.5), steel)
    box_obj("Lintel", (OPEN_W + 0.3, WALL_T + 0.06, 0.20),
            (0.0, WALL_T * 0.5, OPEN_TOP), steel)
    box_obj("InteriorBack", (16.0, 0.30, 6.0), (0.0, 9.0, 3.2), dark)
    box_obj("InteriorFloor", (16.0, 9.0, 0.24), (0.0, 4.7, DOCK_Z - 0.12), dark)
    box_obj("InteriorCeil", (16.0, 9.0, 0.24), (0.0, 4.7, 5.0), dark)
    box_obj("InteriorSideL", (0.30, 9.0, 6.0), (-7.0, 4.7, 3.2), dark)
    box_obj("InteriorSideR", (0.30, 9.0, 6.0), (7.0, 4.7, 3.2), dark)
    box_obj("ManDoorGlass", (0.90, 0.08, 2.05), (7.60, -0.02, DOCK_Z - 0.20), glass)
    box_obj("ManDoorFrame", (1.05, 0.16, 2.20), (7.60, 0.08, DOCK_Z - 0.13), steel)


def build_platform(concrete, steel, rubber, yellow):
    bevel(box_obj("DockSlab", (18.0, 2.10, DOCK_Z), (0.0, FRONT + 1.05, DOCK_Z * 0.5),
                  concrete), 0.03, 2)
    box_obj("EdgeAngle", (18.0, 0.10, 0.14), (0.0, FRONT + 0.05, DOCK_Z - 0.07), steel)
    box_obj("FaceCurb", (18.0, 0.06, 0.20), (0.0, FRONT - 0.03, 0.10), steel)
    box_obj("SafetyStripe", (18.0, 0.16, 0.012), (0.0, FRONT + 0.30, DOCK_Z + 0.006), yellow)

    # laminated rubber dock bumpers flanking the opening
    bm = bmesh.new()
    for bxp in (OPEN_X0 - 0.35, OPEN_X1 + 0.35):
        for i in range(5):
            bx(bm, (0.34, 0.26, 0.088), (bxp, FRONT - 0.13, 0.72 + i * 0.10), 0)
        bx(bm, (0.40, 0.05, 0.60), (bxp, FRONT + 0.01, 0.96), 1)
        for dz in (-0.24, 0.24):
            cy(bm, 0.022, 0.30, (bxp, FRONT - 0.02, 0.96 + dz), 1, axis='Y', seg=10)
    bevel(to_obj("DockBumpers", bm, (rubber, steel)), 0.008, 1)

    # dock leveler plate tipped slightly toward the truck
    bevel(box_obj("LevelerPlate", (3.30, 1.55, 0.06), (0.0, FRONT + 0.80, DOCK_Z + 0.01),
                  steel, rot=(math.radians(-3.0), 0.0, 0.0)), 0.01, 1)
    box_obj("LevelerHinge", (3.30, 0.10, 0.10), (0.0, FRONT + 1.56, DOCK_Z - 0.03), steel)

    bm = bmesh.new()
    for bxp in (-4.2, 4.2, -7.4, 7.4):
        cy(bm, 0.115, 1.05, (bxp, FRONT - 0.55, 0.52), 0)
        cy(bm, 0.125, 0.10, (bxp, FRONT - 0.55, 1.05), 0)
    to_obj("Bollards", bm, (yellow,))

    bm = bmesh.new()
    for bxp in (5.4, 7.2, 8.9):
        bx(bm, (0.07, 0.07, 1.05), (bxp, FRONT + 0.18, DOCK_Z + 0.52), 0)
    for h in (0.55, 1.02):
        pipe(bm, (5.4, FRONT + 0.18, DOCK_Z + h), (8.9, FRONT + 0.18, DOCK_Z + h), 0.026)
    to_obj("EdgeRail", bm, (yellow,))


def build_ramp(concrete, yellow):
    x_top, x_bot = -9.0, -16.5
    bevel(prism("Ramp", [(x_top, DOCK_Z), (x_bot, 0.015), (x_bot, -0.20), (x_top, -0.20)],
                FRONT, 0.25, concrete), 0.02, 1)
    for y in (FRONT + 0.14, 0.11):
        bevel(prism("RampCurb", [(x_top, DOCK_Z + 0.24), (x_bot, 0.26),
                                 (x_bot, 0.015), (x_top, DOCK_Z)],
                    y - 0.07, y + 0.07, concrete), 0.015, 1)
    bm = bmesh.new()
    ry = FRONT + 0.10
    n = 7
    for i in range(n + 1):
        t = i / n
        x = x_top + (x_bot - x_top) * t
        z = DOCK_Z + (0.015 - DOCK_Z) * t + 0.24
        bx(bm, (0.06, 0.06, 1.05), (x, ry, z + 0.52), 0)
    for h in (0.55, 1.02):
        pipe(bm, (x_top, ry, DOCK_Z + 0.24 + h), (x_bot, ry, 0.255 + h), 0.028)
    to_obj("RampRail", bm, (yellow,))
    bm = bmesh.new()
    for i in range(1, 22):
        t = i / 22.0
        x = x_top + (x_bot - x_top) * t
        z = DOCK_Z + (0.015 - DOCK_Z) * t
        bx(bm, (0.05, 1.85, 0.02), (x, FRONT + 1.05, z + 0.01), 0)
    to_obj("RampGrip", bm, (concrete,))
    box_obj("RampApron", (4.0, 2.4, 0.05), (x_bot - 1.9, FRONT + 1.05, 0.02), concrete)


def build_overhead_door(door_mat, steel, glass, dark):
    """Sectional door: leaves in the vertical track, on the radius, and stowed flat."""
    ph = OPEN_H / 5.0
    yl = 0.16
    bm = bmesh.new()

    def leaf(center, basis=None, glazed=False):
        bx(bm, (OPEN_W - 0.10, 0.055, ph - 0.015), center, 0, basis)
        rot3 = basis.to_3x3() if basis is not None else Matrix.Identity(3)
        for dz in (-ph * 0.28, ph * 0.28):
            bx(bm, (OPEN_W - 0.32, 0.02, ph * 0.30),
               Vector(center) + rot3 @ Vector((0.0, -0.035, dz)), 0, basis)
        if glazed:
            for i in range(4):
                bx(bm, (0.58, 0.02, ph * 0.44),
                   Vector(center) + rot3 @ Vector((-1.20 + i * 0.80, -0.04, 0.0)), 1, basis)

    z_bottom = DOCK_Z + 1.35
    for i in range(3):
        leaf((0.0, yl, z_bottom + ph * (i + 0.5)), glazed=(i == 1))
    leaf((0.0, yl + 0.30, OPEN_TOP - 0.22), Matrix.Rotation(math.radians(-46.0), 4, 'X'))
    leaf((0.0, yl + 0.75, OPEN_TOP + 0.10), Matrix.Rotation(math.radians(-90.0), 4, 'X'))
    for i in range(4):
        z = z_bottom + ph * i
        for hx in (-1.55, 0.0, 1.55):
            bx(bm, (0.14, 0.06, 0.10), (hx, yl + 0.05, z), 2)
        for rx in (OPEN_X0 + 0.12, OPEN_X1 - 0.12):
            cy(bm, 0.035, 0.10, (rx, yl + 0.14, z), 2, axis='X', seg=10)
    bevel(to_obj("OverheadDoor", bm, (door_mat, glass, steel)), 0.006, 1)

    bm = bmesh.new()
    for x in (OPEN_X0 + 0.10, OPEN_X1 - 0.10):
        bx(bm, (0.07, 0.26, OPEN_H - 0.40), (x, yl + 0.14, DOCK_Z + OPEN_H * 0.5 - 0.20), 0)
        for k in range(6):
            a = math.radians(90.0 * k / 5.0)
            r = 0.62
            bx(bm, (0.07, 0.20, 0.20),
               (x, yl + 0.14 + r * (1.0 - math.cos(a)), OPEN_TOP - 0.22 + r * math.sin(a)),
               0, Matrix.Rotation(-a, 4, 'X'))
        bx(bm, (0.07, 3.0, 0.22), (x, yl + 2.30, OPEN_TOP + 0.32), 0)
        pipe(bm, (x, yl + 3.60, OPEN_TOP + 0.32), (x, yl + 3.40, 4.95), 0.022, 0, seg=8)
        bx(bm, (0.10, 0.10, 0.30), (x, yl + 0.20, OPEN_TOP + 0.55), 0)
    cy(bm, 0.028, OPEN_W + 0.50, (0.0, yl + 0.30, OPEN_TOP + 0.42), 0, axis='X', seg=12)
    for sx in (-0.95, 0.95):
        cy(bm, 0.075, 1.55, (sx, yl + 0.30, OPEN_TOP + 0.42), 0, axis='X', seg=14)
    for dx in (OPEN_X0 + 0.18, OPEN_X1 - 0.18):
        cy(bm, 0.11, 0.13, (dx, yl + 0.30, OPEN_TOP + 0.42), 0, axis='X', seg=14)
    bx(bm, (0.34, 0.30, 0.34), (0.0, yl + 0.30, OPEN_TOP + 0.42), 0)
    to_obj("DoorTrack", bm, (steel,))
    box_obj("OpeningBackdrop", (OPEN_W, 0.05, OPEN_H), (0.0, 6.2, DOCK_Z + OPEN_H * 0.5), dark)


def build_details(steel, yellow, wood, dark, lamp):
    bm = bmesh.new()
    bx(bm, (0.16, 0.16, 0.30), (OPEN_X1 + 0.55, 0.02, OPEN_TOP - 0.30), 0)
    pipe(bm, (OPEN_X1 + 0.55, 0.02, OPEN_TOP - 0.30),
         (OPEN_X1 + 0.10, -1.05, OPEN_TOP - 0.75), 0.035)
    pipe(bm, (OPEN_X1 + 0.10, -1.05, OPEN_TOP - 0.75),
         (OPEN_X1 - 0.35, -1.65, OPEN_TOP - 1.15), 0.032)
    cy(bm, 0.20, 0.22, (OPEN_X1 - 0.35, -1.65, OPEN_TOP - 1.15), 0, seg=20)
    to_obj("DockLight", bm, (steel,))
    box_obj("LampLens", (0.30, 0.30, 0.03), (OPEN_X1 - 0.35, -1.65, OPEN_TOP - 1.28), lamp)
    box_obj("Controls", (0.34, 0.16, 0.46), (OPEN_X0 - 0.62, -0.06, DOCK_Z + 1.35), dark)
    box_obj("ControlPlate", (0.26, 0.03, 0.34), (OPEN_X0 - 0.62, -0.15, DOCK_Z + 1.35), yellow)
    box_obj("DockSign", (0.70, 0.04, 0.70), (0.0, -0.03, OPEN_TOP + 0.85), yellow)
    for i, (px, py, rz) in enumerate(((2.9, -0.85, 0.15), (4.1, -1.15, -0.4),
                                      (-3.4, -0.95, 0.6))):
        bm = bmesh.new()
        for k in range(3):
            bx(bm, (1.15, 0.13, 0.023), (0.0, -0.36 + k * 0.36, 0.125), 0)
            bx(bm, (1.15, 0.13, 0.023), (0.0, -0.36 + k * 0.36, 0.012), 0)
            bx(bm, (0.10, 0.80, 0.09), (-0.48 + k * 0.48, 0.0, 0.058), 0)
        pal = to_obj("Pallet_%d" % i, bm, (wood,))
        pal.location = (px, py, DOCK_Z)
        pal.rotation_euler = (0.0, 0.0, rz)
        if i < 2:
            bevel(box_obj("Crate_%d" % i, (1.0, 0.72, 0.85),
                          (px, py, DOCK_Z + 0.58), wood, rot=(0.0, 0.0, rz)), 0.01, 1)


def main():
    reset()
    block = mat("ConcreteBlock", (0.46, 0.45, 0.42), 0.88)
    concrete = mat("Concrete", (0.40, 0.395, 0.38), 0.85)
    panel = mat("WallPanel", (0.30, 0.34, 0.36), 0.60, 0.30)
    steel = mat("GalvSteel", (0.52, 0.54, 0.56), 0.40, 0.85)
    door_mat = mat("DoorSteel", (0.62, 0.63, 0.60), 0.42, 0.55)
    rubber = mat("BumperRubber", (0.035, 0.035, 0.038), 0.92)
    yellow = mat("SafetyYellow", (0.72, 0.50, 0.03), 0.55)
    dark = mat("Interior", (0.045, 0.045, 0.05), 0.85)
    wood = mat("Pallet", (0.36, 0.26, 0.15), 0.85)
    glass = mat("DoorGlass", (0.06, 0.075, 0.08), 0.18, 0.20)
    lamp = mat("LampLens", (0.90, 0.85, 0.70), 0.25, 0.0, emit=(1.0, 0.86, 0.62, 14.0))
    asphalt = mat("Asphalt", (0.075, 0.075, 0.08), 0.90)

    plane("Yard", 90.0, asphalt, (-3.0, -14.0, 0.0))
    build_building(block, panel, steel, dark, glass)
    build_platform(concrete, steel, rubber, yellow)
    build_ramp(concrete, yellow)
    build_overhead_door(door_mat, steel, glass, dark)
    build_details(steel, yellow, wood, dark, lamp)
    for x in (OPEN_X0 - 1.6, OPEN_X1 + 1.6):
        box_obj("BayLine", (0.14, 14.0, 0.01), (x, FRONT - 7.1, 0.006), yellow)

    sun("Sun", 3.0, (math.radians(52.0), math.radians(-8.0), math.radians(-56.0)))
    area("SkyFill", 500.0, (-6.0, -20.0, 14.0), (0.0, 0.0, 3.0), 22.0, (0.60, 0.72, 1.0))
    point("DoorGlow", 90.0, (OPEN_X1 - 0.35, -1.60, OPEN_TOP - 1.35), 0.18)
    point("InteriorGlow", 200.0, (0.0, 2.6, 3.6), 1.2, (0.85, 0.90, 1.0))
    camera((-12.5, -14.5, 5.2), (-0.6, -0.7, 2.3), lens=34.0)


main()
