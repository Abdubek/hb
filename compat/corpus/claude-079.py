"""claude-079: A shipping container with corrugated sides and doors (Blender 4.5 LTS)."""
import bpy, bmesh, math
from mathutils import Vector, Matrix


# ------------------------------------------------------------------ helpers
def reset(bg=(0.07, 0.085, 0.105), strength=1.0):
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


def cy(bm, r, d, c, mi=0, axis='Z', seg=14):
    rot = {'Z': Matrix.Identity(4),
           'X': Matrix.Rotation(math.radians(90.0), 4, 'Y'),
           'Y': Matrix.Rotation(math.radians(-90.0), 4, 'X')}[axis]
    m = Matrix.Translation(Vector(c)) @ rot
    res = bmesh.ops.create_cone(bm, cap_ends=True, cap_tris=False, segments=seg,
                                radius1=r, radius2=r, depth=d, matrix=m)
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


def area(name, energy, loc, target, size=10.0, col=(1.0, 1.0, 1.0)):
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


def bevel(ob, width=0.01, segments=2):
    mo = ob.modifiers.new("Bevel", 'BEVEL')
    mo.width = width
    mo.segments = segments
    mo.limit_method = 'ANGLE'
    mo.angle_limit = math.radians(40.0)
    return mo


def basis_from_axes(xa, ya, za, translation=(0.0, 0.0, 0.0)):
    xa, ya, za = Vector(xa), Vector(ya), Vector(za)
    return Matrix(((xa.x, ya.x, za.x, translation[0]),
                   (xa.y, ya.y, za.y, translation[1]),
                   (xa.z, ya.z, za.z, translation[2]),
                   (0.0, 0.0, 0.0, 1.0)))


# ------------------------------------------------------ corrugated sheeting
def corrugation(bm, length, height, depth=0.042, pitch=0.30, rib=0.10, ramp=0.045,
                basis=None, mi=0):
    """Trapezoidal corrugated sheet: profile along local X, ribs along local Z,
    corrugation depth toward local +Y; local -Y is the outward face normal."""
    n = max(1, int(round(length / pitch)))
    p = length / n
    inner = p - 2.0 * ramp - rib
    if inner <= 0.01:
        rib, ramp = p * 0.32, p * 0.10
        inner = p - 2.0 * ramp - rib
    prof = []
    for i in range(n):
        x0 = -length * 0.5 + i * p
        prof.append((x0, 0.0))
        prof.append((x0 + rib, 0.0))
        prof.append((x0 + rib + ramp, -depth))
        prof.append((x0 + rib + ramp + inner, -depth))
    prof.append((length * 0.5, 0.0))

    def place(v):
        v = Vector(v)
        return (basis @ v) if basis is not None else v

    lo = [bm.verts.new(place((u, w, -height * 0.5))) for u, w in prof]
    hi = [bm.verts.new(place((u, w, height * 0.5))) for u, w in prof]
    for i in range(len(prof) - 1):
        bm.faces.new((lo[i], lo[i + 1], hi[i + 1], hi[i])).material_index = mi


def corrugated_object(name, length, height, m, loc, basis=None, depth=0.042,
                      pitch=0.30, thickness=0.012):
    bm = bmesh.new()
    corrugation(bm, length, height, depth=depth, pitch=pitch, basis=basis)
    bm.normal_update()
    ob = to_obj(name, bm, (m,), recalc=False)
    ob.location = loc
    mo = ob.modifiers.new("Solidify", 'SOLIDIFY')
    mo.thickness = thickness
    mo.offset = 1.0
    return ob


# ---------------------------------------------------------------- container
L, W, H = 6.06, 2.438, 2.591
HX, HY = L * 0.5, W * 0.5
POST_T = 0.15
RAIL_T = 0.14
PANEL_H = H - 2.0 * RAIL_T - 0.10
PANEL_Z = RAIL_T + 0.10 + PANEL_H * 0.5
DOOR_H = PANEL_H
DOOR_W = 1.06


def build_shell(paint, hardware, plywood, dark):
    bm = bmesh.new()
    for sx in (-1.0, 1.0):
        for sy in (-1.0, 1.0):
            bx(bm, (POST_T, 0.16, H - 0.30),
               (sx * (HX - POST_T * 0.5), sy * (HY - 0.08), H * 0.5), 0)
    for sy in (-1.0, 1.0):
        bx(bm, (L, 0.13, RAIL_T), (0.0, sy * (HY - 0.065), H - RAIL_T * 0.5), 0)
        bx(bm, (L, 0.15, 0.16), (0.0, sy * (HY - 0.075), 0.19), 0)
    for sx in (-1.0, 1.0):
        bx(bm, (0.13, W - 0.28, RAIL_T), (sx * (HX - 0.065), 0.0, H - RAIL_T * 0.5), 0)
        bx(bm, (0.15, W - 0.28, 0.18), (sx * (HX - 0.075), 0.0, 0.20), 0)
    bevel(to_obj("Frame", bm, (paint,)), 0.012, 2)

    bm = bmesh.new()
    for sx in (-1.0, 1.0):
        for sy in (-1.0, 1.0):
            for z in (0.06, H - 0.06):
                bx(bm, (0.178, 0.162, 0.118),
                   (sx * (HX - 0.089), sy * (HY - 0.081), z), 0)
    bevel(to_obj("CornerCastings", bm, (hardware,)), 0.016, 2)

    bm = bmesh.new()
    n = 13
    for i in range(n):
        bx(bm, (0.075, W - 0.30, 0.115),
           (-HX + 0.32 + i * (L - 0.64) / (n - 1), 0.0, 0.165), 0)
    for sx in (-1.0, 1.0):
        bx(bm, (0.30, W - 0.30, 0.14), (sx * 1.05, 0.0, 0.155), 0)
    bevel(to_obj("Underframe", bm, (hardware,)), 0.008, 1)

    bm = bmesh.new()
    bx(bm, (L - 0.32, W - 0.30, 0.045), (0.0, 0.0, 0.245), 0)
    to_obj("Floor", bm, (plywood,))

    bm = bmesh.new()
    for sy in (-1.0, 1.0):
        bx(bm, (L - 0.34, 0.02, PANEL_H), (0.0, sy * (HY - 0.19), PANEL_Z), 0)
    bx(bm, (0.02, W - 0.34, PANEL_H), (HX - 0.19, 0.0, PANEL_Z), 0)
    bx(bm, (L - 0.34, W - 0.34, 0.02), (0.0, 0.0, H - 0.19), 0)
    to_obj("InteriorLining", bm, (dark,))

    corrugated_object("SideWall_L", L - 2.0 * POST_T, PANEL_H, paint,
                      (0.0, -(HY - 0.055), PANEL_Z))
    corrugated_object("SideWall_R", L - 2.0 * POST_T, PANEL_H, paint,
                      (0.0, HY - 0.055, PANEL_Z),
                      basis=Matrix.Rotation(math.pi, 4, 'Z'))
    corrugated_object("EndWall", W - 0.32, PANEL_H, paint,
                      (HX - 0.065, 0.0, PANEL_Z),
                      basis=basis_from_axes((0, 1, 0), (-1, 0, 0), (0, 0, 1)))
    corrugated_object("Roof", W - 0.30, L - 0.32, paint,
                      (0.0, 0.0, H - RAIL_T - 0.01),
                      basis=basis_from_axes((0, 1, 0), (0, 0, -1), (-1, 0, 0)),
                      depth=0.030, pitch=0.26)

    bm = bmesh.new()
    for sy in (-1.0, 1.0):
        for x in (-2.0, 2.0):
            bx(bm, (0.30, 0.06, 0.16), (x, sy * (HY - 0.07), H - 0.34), 0)
            for k in range(4):
                bx(bm, (0.26, 0.03, 0.02),
                   (x, sy * (HY - 0.105), H - 0.40 + k * 0.04), 0)
    to_obj("Vents", bm, (hardware,))


def build_door_leaf(sign, paint, hardware, seal):
    """Door leaf in leaf-local space: hinge line at the origin, local -X outboard,
    leaf extending along local sign*Y."""
    bm = bmesh.new()
    inner = sign * (DOOR_W - 0.02)
    basis = basis_from_axes((0.0, sign, 0.0), (1.0, 0.0, 0.0), (0.0, 0.0, -sign),
                            translation=(0.0, sign * DOOR_W * 0.5, 0.0))
    corrugation(bm, DOOR_W - 0.14, DOOR_H - 0.13, depth=0.030, pitch=0.24,
                basis=basis, mi=0)
    bx(bm, (0.055, DOOR_W, 0.075), (-0.012, sign * DOOR_W * 0.5, DOOR_H * 0.5 - 0.03), 0)
    bx(bm, (0.055, DOOR_W, 0.075), (-0.012, sign * DOOR_W * 0.5, -DOOR_H * 0.5 + 0.03), 0)
    bx(bm, (0.055, 0.085, DOOR_H), (-0.012, sign * 0.042, 0.0), 0)
    bx(bm, (0.055, 0.085, DOOR_H), (-0.012, inner, 0.0), 0)
    bx(bm, (0.03, 0.035, DOOR_H - 0.05), (0.012, inner + sign * 0.05, 0.0), 2)
    for t in (0.30, 0.78):
        ry = sign * DOOR_W * t
        cy(bm, 0.021, DOOR_H - 0.06, (-0.055, ry, 0.0), 1, seg=12)
        for z in (DOOR_H * 0.5 - 0.06, -DOOR_H * 0.5 + 0.06):
            bx(bm, (0.075, 0.075, 0.10), (-0.055, ry, z), 1)
            bx(bm, (0.085, 0.10, 0.055), (-0.055, ry, z + (0.09 if z > 0 else -0.09)), 1)
        for z in (0.55, -0.55):
            bx(bm, (0.065, 0.085, 0.075), (-0.045, ry, z), 1)
        bx(bm, (0.06, 0.055, 0.30), (-0.075, ry, 0.02), 1)
        cy(bm, 0.018, 0.34, (-0.115, ry, -0.10), 1, seg=10)
        bx(bm, (0.075, 0.12, 0.09), (-0.075, ry + sign * 0.09, -0.22), 1)
    for z in (DOOR_H * 0.5 - 0.22, 0.0, -DOOR_H * 0.5 + 0.22):
        bx(bm, (0.10, 0.11, 0.085), (-0.03, sign * 0.05, z), 1)
        cy(bm, 0.026, 0.16, (-0.075, -sign * 0.02, z), 1, seg=10)
        bx(bm, (0.09, 0.09, 0.075), (-0.085, -sign * 0.02, z), 1)
    bm.normal_update()
    ob = to_obj("DoorLeaf_%s" % ("A" if sign > 0 else "B"), bm,
                (paint, hardware, seal), recalc=False)
    bevel(ob, 0.006, 1)
    return ob


def build_doors(paint, hardware, seal):
    x_hinge = -(HX - 0.075)
    leaf_a = build_door_leaf(1.0, paint, hardware, seal)
    leaf_a.location = (x_hinge, -(HY - 0.10), PANEL_Z)
    leaf_a.rotation_euler = (0.0, 0.0, math.radians(88.0))   # swung open
    leaf_b = build_door_leaf(-1.0, paint, hardware, seal)
    leaf_b.location = (x_hinge, HY - 0.10, PANEL_Z)
    bm = bmesh.new()
    bx(bm, (0.10, W - 0.30, 0.10), (x_hinge - 0.01, 0.0, PANEL_Z + DOOR_H * 0.5 + 0.06), 0)
    bx(bm, (0.10, W - 0.30, 0.10), (x_hinge - 0.01, 0.0, PANEL_Z - DOOR_H * 0.5 - 0.06), 0)
    to_obj("DoorSurround", bm, (hardware,))


def main():
    reset()
    paint = mat("ContainerPaint", (0.46, 0.145, 0.075), 0.62, 0.35)
    hardware = mat("Hardware", (0.14, 0.145, 0.15), 0.55, 0.70)
    seal = mat("Gasket", (0.03, 0.03, 0.032), 0.85)
    plywood = mat("Plywood", (0.22, 0.16, 0.10), 0.85)
    dark = mat("Interior", (0.045, 0.042, 0.04), 0.90)
    gravel = mat("Gravel", (0.16, 0.155, 0.15), 0.92)
    concrete = mat("Concrete", (0.34, 0.335, 0.32), 0.85)

    plane("Yard", 80.0, gravel, (0.0, 0.0, 0.0))
    build_shell(paint, hardware, plywood, dark)
    build_doors(paint, hardware, seal)
    for sx in (-1.0, 1.0):
        for sy in (-1.0, 1.0):
            box_obj("Pad", (0.55, 0.55, 0.12),
                    (sx * (HX - 0.30), sy * (HY - 0.30), 0.03), concrete)

    sun("Sun", 3.5, (math.radians(54.0), math.radians(8.0), math.radians(-124.0)))
    area("SkyFill", 420.0, (-9.0, -10.0, 9.0), (-0.5, 0.0, 1.4), 14.0, (0.58, 0.70, 1.0))
    area("Rim", 160.0, (7.0, 8.0, 5.0), (0.5, 0.0, 1.6), 8.0, (1.0, 0.93, 0.80))
    camera((-8.6, -7.8, 3.7), (-0.7, 0.05, 1.35), lens=42.0)


main()
