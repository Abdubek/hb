# claude-039 : A wheeled toolbox with drawers and handle
# Blender 4.5 LTS - headless scene construction only (no render, no file output).

import bpy
import bmesh
import math
from mathutils import Vector, Matrix


# ----------------------------------------------------------------------------
# scene bootstrap
# ----------------------------------------------------------------------------
def reset_scene():
    bpy.ops.wm.read_factory_settings(use_empty=True)
    scene = bpy.context.scene
    scene.unit_settings.system = 'METRIC'
    scene.unit_settings.length_unit = 'METERS'
    return scene


def setup_world(scene, color=(0.045, 0.048, 0.055), strength=1.0):
    world = bpy.data.worlds.new("ToolboxWorld")
    world.use_nodes = True
    bg = world.node_tree.nodes["Background"]
    bg.inputs["Color"].default_value = (*color, 1.0)
    bg.inputs["Strength"].default_value = strength
    scene.world = world
    return world


def make_material(name, base, metallic=0.0, roughness=0.5, coat=0.0):
    mat = bpy.data.materials.new(name)
    mat.use_nodes = True
    bsdf = mat.node_tree.nodes.get("Principled BSDF")
    bsdf.inputs["Base Color"].default_value = (base[0], base[1], base[2], 1.0)
    bsdf.inputs["Metallic"].default_value = metallic
    bsdf.inputs["Roughness"].default_value = roughness
    if coat and "Coat Weight" in bsdf.inputs:
        bsdf.inputs["Coat Weight"].default_value = coat
        bsdf.inputs["Coat Roughness"].default_value = 0.08
    return mat


# ----------------------------------------------------------------------------
# part accumulation : one bmesh per named part, one material each
# ----------------------------------------------------------------------------
PARTS = {}


def part(name, material):
    """Return the bmesh that accumulates geometry for the named part."""
    if name not in PARTS:
        PARTS[name] = [bmesh.new(), material]
    return PARTS[name][0]


def finalise_parts():
    objects = []
    for name, (bm, mat) in PARTS.items():
        bmesh.ops.remove_doubles(bm, verts=bm.verts, dist=1e-5)
        bm.normal_update()
        me = bpy.data.meshes.new(name)
        bm.to_mesh(me)
        bm.free()
        me.materials.append(mat)
        ob = bpy.data.objects.new(name, me)
        bpy.context.collection.objects.link(ob)
        objects.append(ob)
    PARTS.clear()
    return objects


# ----------------------------------------------------------------------------
# primitive helpers (bmesh ops, world-space matrices)
# ----------------------------------------------------------------------------
def xform(loc=(0.0, 0.0, 0.0), rot=None):
    m = Matrix.Translation(Vector(loc))
    if rot:
        angle, axis = rot
        m = m @ Matrix.Rotation(angle, 4, axis)
    return m


def add_box(bm, size, loc=(0.0, 0.0, 0.0), rot=None, base=None, bevel=0.004, segments=2):
    """Axis aligned (then transformed) beveled box."""
    before = set(bm.verts)
    scale = Matrix.Diagonal(Vector((size[0], size[1], size[2], 1.0)))
    mat = xform(loc, rot)
    if base is not None:
        mat = base @ mat
    bmesh.ops.create_cube(bm, size=1.0, matrix=mat @ scale, calc_uvs=True)
    verts = [v for v in bm.verts if v not in before]
    if bevel > 0.0:
        edges = list({e for v in verts for e in v.link_edges})
        bmesh.ops.bevel(bm, geom=edges, offset=bevel, offset_type='OFFSET',
                        segments=segments, profile=0.5, affect='EDGES',
                        clamp_overlap=True)
        verts = [v for v in bm.verts if v not in before]
    return verts


def add_cylinder(bm, radius, depth, loc=(0.0, 0.0, 0.0), axis='Z', base=None,
                 segments=28, caps=True, smooth=True):
    """Cylinder whose local Z is remapped to the requested axis."""
    before = set(bm.verts)
    mat = Matrix.Translation(Vector(loc))
    if axis == 'X':
        mat = mat @ Matrix.Rotation(math.radians(90.0), 4, 'Y')
    elif axis == 'Y':
        mat = mat @ Matrix.Rotation(math.radians(-90.0), 4, 'X')
    if base is not None:
        mat = base @ mat
    bmesh.ops.create_cone(bm, cap_ends=caps, cap_tris=False, segments=segments,
                          radius1=radius, radius2=radius, depth=depth,
                          matrix=mat, calc_uvs=True)
    verts = [v for v in bm.verts if v not in before]
    if smooth:
        for f in {f for v in verts for f in v.link_faces}:
            if len(f.verts) == 4:
                f.smooth = True
    return verts


def rounded_path(points, radius, seg=10):
    """Quadratic-bezier corner rounding for a polyline."""
    pts = [Vector(p) for p in points]
    out = [pts[0]]
    for i in range(1, len(pts) - 1):
        prev, cur, nxt = pts[i - 1], pts[i], pts[i + 1]
        d0 = cur - prev
        d1 = nxt - cur
        r = min(radius, d0.length * 0.48, d1.length * 0.48)
        a = cur - d0.normalized() * r
        b = cur + d1.normalized() * r
        for j in range(seg + 1):
            t = j / seg
            out.append(((1.0 - t) ** 2) * a + (2.0 * (1.0 - t) * t) * cur + (t * t) * b)
    out.append(pts[-1])
    return out


def make_swept_curve(name, points, radius, material, resolution=6):
    cu = bpy.data.curves.new(name, 'CURVE')
    cu.dimensions = '3D'
    cu.resolution_u = 4
    cu.bevel_depth = radius
    cu.bevel_resolution = resolution
    cu.use_fill_caps = True
    spline = cu.splines.new('POLY')
    spline.points.add(len(points) - 1)
    for p, co in zip(spline.points, points):
        p.co = (co[0], co[1], co[2], 1.0)
    spline.use_smooth = True
    ob = bpy.data.objects.new(name, cu)
    ob.data.materials.append(material)
    bpy.context.collection.objects.link(ob)
    return ob


# ----------------------------------------------------------------------------
# toolbox dimensions (metres)
# ----------------------------------------------------------------------------
W = 0.70            # cabinet width  (X)
D = 0.45            # cabinet depth  (Y)
H = 0.85            # carcass height (Z)
T = 0.014           # sheet thickness
Z0 = 0.13           # underside of the carcass (top of the caster mount plates)
ZT = Z0 + H         # top of the carcass
FRONT = -D / 2.0    # front face plane
FT = 0.018          # drawer front thickness

DRAWERS = [0.26, 0.20, 0.14, 0.10, 0.10]   # bottom -> top
GAP = 0.005
OPEN_INDEX = 1
OPEN_AMOUNT = 0.26


# ----------------------------------------------------------------------------
# geometry builders
# ----------------------------------------------------------------------------
def build_carcass(mat_body, mat_steel, mat_rubber):
    bm = part("Toolbox_Carcass", mat_body)

    # side panels
    for sx in (-1.0, 1.0):
        add_box(bm, (T, D, H), (sx * (W / 2.0 - T / 2.0), 0.0, Z0 + H / 2.0), bevel=0.003)
    # back panel
    add_box(bm, (W - 2.0 * T, T, H), (0.0, D / 2.0 - T / 2.0, Z0 + H / 2.0), bevel=0.003)
    # floor and ceiling of the carcass
    add_box(bm, (W - 2.0 * T, D, T), (0.0, 0.0, Z0 + T / 2.0), bevel=0.003)
    add_box(bm, (W - 2.0 * T, D, T), (0.0, 0.0, ZT - T / 2.0), bevel=0.003)
    # plinth / base frame the casters bolt through
    add_box(bm, (W - 0.02, D - 0.02, 0.028), (0.0, 0.0, Z0 - 0.014), bevel=0.004)
    # rear stiffening ribs
    for zr in (Z0 + 0.28, Z0 + 0.58):
        add_box(bm, (W - 2.0 * T - 0.01, 0.02, 0.03), (0.0, D / 2.0 - T - 0.01, zr), bevel=0.003)

    # stainless worktop + rubber mat
    steel = part("Toolbox_Worktop", mat_steel)
    add_box(steel, (W + 0.04, D + 0.04, 0.028), (0.0, 0.0, ZT + 0.014), bevel=0.005, segments=3)
    rub = part("Worktop_Mat", mat_rubber)
    add_box(rub, (W - 0.01, D - 0.02, 0.006), (0.0, 0.0, ZT + 0.028 + 0.003), bevel=0.002)


def build_drawer(index, z_bottom, height, mat_body, mat_steel, mat_chrome, mat_rubber):
    oa = OPEN_AMOUNT if index == OPEN_INDEX else 0.0
    zc = z_bottom + height / 2.0

    # ---- overlay front -----------------------------------------------------
    front = part("Drawer_Fronts", mat_body)
    fy = FRONT - FT / 2.0 - oa
    add_box(front, (W - 0.006, FT, height - 0.002), (0.0, fy, zc), bevel=0.005, segments=3)

    # ---- bar pull ----------------------------------------------------------
    pull = part("Drawer_Pulls", mat_chrome)
    bar_len = W - 0.24
    stand_len = 0.035
    stand_y = FRONT - FT - stand_len / 2.0 - oa
    bar_y = FRONT - FT - stand_len - 0.013 - oa
    add_cylinder(pull, 0.013, bar_len, (0.0, bar_y, zc), axis='X', segments=20)
    for sx in (-1.0, 1.0):
        add_cylinder(pull, 0.0095, stand_len,
                     (sx * (bar_len / 2.0 - 0.025), stand_y, zc), axis='Y', segments=16)

    # a lock barrel on the top drawer
    if index == len(DRAWERS) - 1:
        add_cylinder(pull, 0.013, 0.026, (W / 2.0 - 0.075, FRONT - FT - 0.013 - oa, zc),
                     axis='Y', segments=20)

    # ---- drawer box behind the front --------------------------------------
    box = part("Drawer_Boxes", mat_steel)
    bw = W - 0.05
    bd = 0.40
    bh = max(0.05, height - 0.03)
    wt = 0.010
    y_near = FRONT + 0.006 - oa
    y_far = y_near + bd
    zb = z_bottom + 0.013
    add_box(box, (bw, bd, wt), (0.0, (y_near + y_far) / 2.0, zb + wt / 2.0), bevel=0.002)
    for sx in (-1.0, 1.0):
        add_box(box, (wt, bd, bh), (sx * (bw / 2.0 - wt / 2.0),
                                    (y_near + y_far) / 2.0, zb + bh / 2.0), bevel=0.002)
    add_box(box, (bw - 2.0 * wt, wt, bh), (0.0, y_far - wt / 2.0, zb + bh / 2.0), bevel=0.002)
    add_box(box, (bw - 2.0 * wt, wt, bh), (0.0, y_near + wt / 2.0, zb + bh / 2.0), bevel=0.002)

    # slide rails on the flanks
    rail = part("Drawer_Slides", mat_steel)
    for sx in (-1.0, 1.0):
        add_box(rail, (0.012, bd, 0.024), (sx * (bw / 2.0 + 0.008),
                                           (y_near + y_far) / 2.0, zb + bh * 0.55), bevel=0.002)

    # ---- contents of the open drawer --------------------------------------
    if index == OPEN_INDEX:
        liner = part("Drawer_Liner", mat_rubber)
        add_box(liner, (bw - 2.0 * wt - 0.004, bd - 2.0 * wt - 0.004, 0.004),
                (0.0, (y_near + y_far) / 2.0, zb + wt + 0.002), bevel=0.001)
        # divider strip
        div = part("Drawer_Boxes", mat_steel)
        add_box(div, (bw - 2.0 * wt, 0.008, 0.045),
                (0.0, y_near + 0.17, zb + wt + 0.023), bevel=0.002)
        # sockets standing in a row
        tools = part("Tools_Chrome", mat_chrome)
        for i in range(6):
            r = 0.014 + 0.002 * (i % 3)
            add_cylinder(tools, r, 0.048,
                         (-0.20 + i * 0.081, y_near + 0.085, zb + wt + 0.026),
                         axis='Z', segments=20)
        # a couple of spanners lying flat
        for i, ox in enumerate((-0.16, -0.10)):
            add_box(tools, (0.022, 0.20, 0.008),
                    (ox, y_near + 0.28, zb + wt + 0.006),
                    rot=(math.radians(6.0 * (i + 1)), 'Z'), bevel=0.003)
        # a screwdriver: shaft + handle
        add_cylinder(tools, 0.005, 0.17, (0.10, y_near + 0.27, zb + wt + 0.006),
                     axis='Y', segments=14)
        grip = part("Tools_Grip", mat_rubber)
        add_cylinder(grip, 0.013, 0.09, (0.10, y_near + 0.135, zb + wt + 0.006),
                     axis='Y', segments=18)


def build_drawer_stack(mat_body, mat_steel, mat_chrome, mat_rubber):
    z = Z0 + T + 0.002
    for i, h in enumerate(DRAWERS):
        build_drawer(i, z, h, mat_body, mat_steel, mat_chrome, mat_rubber)
        z += h + GAP


def build_caster(x, y, angle, mat_dark, mat_chrome, mat_rubber):
    base = xform((x, y, 0.0), (angle, 'Z'))
    metal = part("Casters_Metal", mat_dark)
    chrome = part("Casters_Chrome", mat_chrome)
    tyre = part("Casters_Tyres", mat_rubber)

    trail = -0.022                      # swivel offset of the wheel axle
    # mounting plate + bolts
    add_box(metal, (0.098, 0.098, 0.012), (0.0, 0.0, Z0 - 0.034), base=base, bevel=0.003)
    for bx in (-1.0, 1.0):
        for by in (-1.0, 1.0):
            add_cylinder(chrome, 0.005, 0.014,
                         (bx * 0.036, by * 0.036, Z0 - 0.030), axis='Z', base=base, segments=10)
    # kingpin / swivel race
    add_cylinder(metal, 0.026, 0.014, (0.0, 0.0, Z0 - 0.047), axis='Z', base=base, segments=24)
    add_cylinder(chrome, 0.019, 0.030, (0.0, 0.0, Z0 - 0.066), axis='Z', base=base, segments=20)
    # fork
    add_box(metal, (0.078, 0.062, 0.014), (0.0, trail, 0.112), base=base, bevel=0.003)
    for sx in (-1.0, 1.0):
        add_box(metal, (0.011, 0.052, 0.086), (sx * 0.033, trail, 0.069), base=base, bevel=0.003)
    # axle, hub and tyre
    add_cylinder(chrome, 0.0075, 0.086, (0.0, trail, 0.05), axis='X', base=base, segments=14)
    add_cylinder(chrome, 0.020, 0.052, (0.0, trail, 0.05), axis='X', base=base, segments=24)
    add_cylinder(tyre, 0.050, 0.048, (0.0, trail, 0.05), axis='X', base=base, segments=40)


def build_casters(mat_dark, mat_chrome, mat_rubber):
    cx = W / 2.0 - 0.072
    cy = D / 2.0 - 0.075
    layout = ((-cx, -cy, math.radians(28.0)),
              (cx, -cy, math.radians(-34.0)),
              (-cx, cy, math.radians(4.0)),
              (cx, cy, math.radians(-6.0)))
    for x, y, a in layout:
        build_caster(x, y, a, mat_dark, mat_chrome, mat_rubber)


def build_push_handle(mat_chrome, mat_dark, mat_rubber):
    hx = W / 2.0 + 0.030
    hy = 0.152
    z_low = 0.55
    z_top = 1.16
    path = rounded_path([(hx, -hy, z_low), (hx, -hy, z_top),
                         (hx, hy, z_top), (hx, hy, z_low)], 0.10, seg=10)
    make_curve_obj = make_swept_curve("Push_Handle", path, 0.017, mat_chrome)
    make_curve_obj.data.bevel_resolution = 8

    # rubber grip sleeve across the top run
    grip = part("Handle_Grip", mat_rubber)
    add_cylinder(grip, 0.024, 0.20, (hx, 0.0, z_top), axis='Y', segments=32)
    for sy in (-1.0, 1.0):
        add_cylinder(grip, 0.028, 0.010, (hx, sy * 0.105, z_top), axis='Y', segments=32)

    # brackets tying the uprights to the cabinet flank
    brk = part("Handle_Brackets", mat_dark)
    for sy in (-1.0, 1.0):
        for zb in (0.585, 0.86):
            add_box(brk, (0.040, 0.052, 0.048),
                    ((W / 2.0 + hx) / 2.0, sy * hy, zb), bevel=0.004)
        # end cap plate where the tube meets the bracket
        add_box(brk, (0.010, 0.060, 0.060), (W / 2.0 + 0.004, sy * hy, 0.585), bevel=0.004)


def build_side_details(mat_dark, mat_chrome):
    """Bumper corners and a small hook rail on the left flank."""
    bump = part("Corner_Bumpers", mat_dark)
    for sx in (-1.0, 1.0):
        for sy in (-1.0, 1.0):
            add_box(bump, (0.03, 0.03, H - 0.04),
                    (sx * (W / 2.0 - 0.012), sy * (D / 2.0 - 0.012), Z0 + H / 2.0),
                    bevel=0.008, segments=3)

    rail = part("Hook_Rail", mat_chrome)
    rx = -W / 2.0 - 0.014
    add_cylinder(rail, 0.008, 0.30, (rx, 0.0, 0.80), axis='Y', segments=14)
    for sy in (-1.0, 1.0):
        add_box(rail, (0.028, 0.016, 0.016), (rx + 0.007, sy * 0.14, 0.80), bevel=0.003)
    for oy in (-0.09, 0.0, 0.09):
        add_cylinder(rail, 0.005, 0.05, (rx - 0.012, oy, 0.784), axis='Z', segments=10)


def build_floor(mat_floor):
    bm = part("Floor", mat_floor)
    add_box(bm, (14.0, 14.0, 0.2), (0.0, 0.0, -0.1), bevel=0.0)


# ----------------------------------------------------------------------------
# camera and lighting
# ----------------------------------------------------------------------------
def aim(obj, target):
    direction = Vector(target) - obj.location
    obj.rotation_euler = direction.to_track_quat('-Z', 'Y').to_euler()


def build_camera(scene):
    cam_data = bpy.data.cameras.new("Camera")
    cam_data.lens = 52.0
    cam_data.clip_start = 0.05
    cam_data.clip_end = 100.0
    cam = bpy.data.objects.new("Camera", cam_data)
    cam.location = Vector((1.95, -2.15, 1.62))
    bpy.context.collection.objects.link(cam)
    aim(cam, (-0.02, -0.02, 0.66))
    scene.camera = cam
    return cam


def build_lights():
    def area(name, loc, target, energy, size, color=(1.0, 1.0, 1.0)):
        data = bpy.data.lights.new(name, 'AREA')
        data.energy = energy
        data.shape = 'RECTANGLE'
        data.size = size[0]
        data.size_y = size[1]
        data.color = color
        ob = bpy.data.objects.new(name, data)
        ob.location = Vector(loc)
        bpy.context.collection.objects.link(ob)
        aim(ob, target)
        return ob

    area("Key", (2.3, -2.6, 3.1), (0.0, -0.1, 0.8), 900.0, (2.0, 1.6))
    area("Fill", (-2.7, -1.8, 1.5), (0.0, 0.0, 0.6), 260.0, (2.4, 2.0), (0.86, 0.90, 1.0))
    area("Rim", (-0.7, 2.7, 2.3), (0.0, 0.15, 0.9), 500.0, (1.6, 1.6), (0.95, 0.97, 1.0))


# ----------------------------------------------------------------------------
# main
# ----------------------------------------------------------------------------
def main():
    scene = reset_scene()
    setup_world(scene)

    mat_body = make_material("PaintedSteel_Red", (0.42, 0.035, 0.028), 0.55, 0.30, coat=0.6)
    mat_steel = make_material("BrushedSteel", (0.62, 0.63, 0.65), 1.0, 0.30)
    mat_chrome = make_material("Chrome", (0.84, 0.86, 0.88), 1.0, 0.14)
    mat_dark = make_material("CharcoalMetal", (0.045, 0.046, 0.052), 0.5, 0.45)
    mat_rubber = make_material("Rubber", (0.025, 0.025, 0.027), 0.0, 0.82)
    mat_floor = make_material("ShopFloor", (0.16, 0.165, 0.175), 0.0, 0.55)

    build_floor(mat_floor)
    build_carcass(mat_body, mat_steel, mat_rubber)
    build_drawer_stack(mat_body, mat_steel, mat_chrome, mat_rubber)
    build_side_details(mat_dark, mat_chrome)
    build_casters(mat_dark, mat_chrome, mat_rubber)
    build_push_handle(mat_chrome, mat_dark, mat_rubber)

    finalise_parts()

    build_camera(scene)
    build_lights()


if __name__ == "__main__":
    main()
