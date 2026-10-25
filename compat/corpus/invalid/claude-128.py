"""
claude-128 -- Retro computer terminal.

Builds, from Blender's factory startup, a vintage desktop terminal: a beige CRT
housing with a bulged phosphor screen behind glass, a bezel, front control knobs,
rear vent ribs and connector plugs with rubber cables, plus a wedge keyboard with
a full key field and a coiled keyboard cable.

Scene construction only -- nothing is rendered or saved.
"""

import math
import random

import bpy
import bmesh
from mathutils import Vector, Matrix


# ---------------------------------------------------------------------------
# scene bootstrap
# ---------------------------------------------------------------------------

def reset_scene():
    bpy.ops.wm.read_factory_settings(use_empty=True)
    scene = bpy.context.scene
    scene.render.engine = 'CYCLES'
    scene.cycles.samples = 128
    scene.cycles.use_denoising = True
    scene.render.resolution_x = 1600
    scene.render.resolution_y = 1100
    scene.unit_settings.system = 'METRIC'
    scene.unit_settings.length_unit = 'CENTIMETERS'
    return scene


# ---------------------------------------------------------------------------
# small helpers
# ---------------------------------------------------------------------------

def set_input(node, name, value):
    """Assign a socket only if this Blender build exposes it under that name."""
    sock = node.inputs.get(name)
    if sock is not None:
        sock.default_value = value


def make_material(name, base_color, roughness=0.5, metallic=0.0,
                  transmission=0.0, ior=1.45, emission=None, emission_strength=0.0,
                  coat=0.0):
    mat = bpy.data.materials.new(name)
    mat.use_nodes = True
    bsdf = mat.node_tree.nodes.get("Principled BSDF")
    set_input(bsdf, "Base Color", (*base_color, 1.0))
    set_input(bsdf, "Roughness", roughness)
    set_input(bsdf, "Metallic", metallic)
    set_input(bsdf, "IOR", ior)
    set_input(bsdf, "Transmission Weight", transmission)
    set_input(bsdf, "Coat Weight", coat)
    if emission is not None:
        set_input(bsdf, "Emission Color", (*emission, 1.0))
        set_input(bsdf, "Emission Strength", emission_strength)
    if transmission > 0.0:
        mat.use_backface_culling = False
    return mat


def obj_from_bm(name, bm, material=None, smooth_angle=None):
    me = bpy.data.meshes.new(name)
    bm.to_mesh(me)
    bm.free()
    me.validate()
    ob = bpy.data.objects.new(name, me)
    bpy.context.collection.objects.link(ob)
    if material is not None:
        ob.data.materials.append(material)
    if smooth_angle is not None:
        for poly in ob.data.polygons:
            poly.use_smooth = True
        ob.data.set_sharp_from_angle(angle=smooth_angle)
    return ob


def box(bm, center, size):
    """Axis aligned box added into an existing bmesh."""
    mat = Matrix.Translation(Vector(center)) @ Matrix.Diagonal(
        Vector((size[0], size[1], size[2], 1.0)))
    return bmesh.ops.create_cube(bm, size=1.0, matrix=mat)


def bevel_all(bm, offset, segments=2, profile=0.5):
    geom = list(bm.verts) + list(bm.edges) + list(bm.faces)
    bmesh.ops.bevel(bm, geom=geom, offset=offset, offset_type='OFFSET',
                    segments=segments, profile=profile, affect='EDGES',
                    clamp_overlap=True)


# ---------------------------------------------------------------------------
# materials
# ---------------------------------------------------------------------------

MAT = {
    "case":     make_material("CaseBeige", (0.520, 0.470, 0.360), roughness=0.52, coat=0.15),
    "case_dk":  make_material("CaseWarmGrey", (0.330, 0.300, 0.240), roughness=0.60),
    "bezel":    make_material("BezelPlastic", (0.035, 0.036, 0.040), roughness=0.42),
    "rubber":   make_material("CableRubber", (0.018, 0.018, 0.020), roughness=0.66),
    "glass":    make_material("CRTGlass", (0.86, 0.90, 0.88), roughness=0.045,
                              transmission=1.0, ior=1.52),
    "phosphor": make_material("Phosphor", (0.010, 0.030, 0.016), roughness=0.30,
                              emission=(0.05, 0.35, 0.12), emission_strength=0.6),
    "text":     make_material("PhosphorText", (0.02, 0.05, 0.02), roughness=0.4,
                              emission=(0.30, 1.00, 0.42), emission_strength=7.0),
    "led":      make_material("PowerLED", (0.35, 0.05, 0.02), roughness=0.25,
                              emission=(1.0, 0.18, 0.06), emission_strength=14.0),
    "keycap":   make_material("Keycap", (0.430, 0.410, 0.360), roughness=0.58),
    "keycap_d": make_material("KeycapDark", (0.085, 0.082, 0.080), roughness=0.55),
    "metal":    make_material("PlugMetal", (0.62, 0.63, 0.65), roughness=0.28, metallic=1.0),
    "brass":    make_material("PinBrass", (0.72, 0.55, 0.22), roughness=0.32, metallic=1.0),
    "desk":     make_material("DeskWood", (0.115, 0.072, 0.042), roughness=0.42, coat=0.25),
}


# ---------------------------------------------------------------------------
# key dimensions of the terminal
# ---------------------------------------------------------------------------

CASE_W, CASE_D, CASE_H = 0.46, 0.42, 0.38
CASE_CY = 0.06                      # case centre in Y
PED_H = 0.09                        # pedestal height
CASE_CZ = PED_H + CASE_H * 0.5      # case centre in Z
FRONT_Y = CASE_CY - CASE_D * 0.5    # -0.15
BACK_TAPER_X = 0.74
BACK_TAPER_Z = 0.80
BACK_Y = CASE_CY + CASE_D * 0.5     # 0.27

SCREEN_CZ = CASE_CZ + 0.025
OPEN_HW, OPEN_HH = 0.165, 0.113     # bezel opening half sizes


def screen_falloff(u, v):
    """Flat-ish centre, rolled off edges; u, v in [-1, 1]."""
    return max(0.0, (1.0 - u * u)) ** 0.55 * max(0.0, (1.0 - v * v)) ** 0.55


def build_curved_panel(bm, half_w, half_h, base_y, bulge, nx=44, nz=34):
    """Grid in the XZ plane bulging toward -Y, centred on the screen."""
    verts = []
    for iz in range(nz + 1):
        v = -1.0 + 2.0 * iz / nz
        row = []
        for ix in range(nx + 1):
            u = -1.0 + 2.0 * ix / nx
            y = base_y - bulge * screen_falloff(u, v)
            row.append(bm.verts.new((u * half_w, y, SCREEN_CZ + v * half_h)))
        verts.append(row)
    for iz in range(nz):
        for ix in range(nx):
            bm.faces.new((verts[iz][ix], verts[iz][ix + 1],
                          verts[iz + 1][ix + 1], verts[iz + 1][ix]))
    bm.verts.index_update()


# ---------------------------------------------------------------------------
# CRT housing
# ---------------------------------------------------------------------------

def build_housing():
    bm = bmesh.new()
    bmesh.ops.create_cube(
        bm, size=1.0,
        matrix=Matrix.Diagonal(Vector((CASE_W, CASE_D, CASE_H, 1.0))))

    # taper the rear of the shell like a real CRT shroud, keeping the base flat
    bottom = -CASE_H * 0.5
    for v in bm.verts:
        if v.co.y > 0.0:
            v.co.x *= BACK_TAPER_X
            v.co.z = bottom + (v.co.z - bottom) * BACK_TAPER_Z

    bevel_all(bm, offset=0.020, segments=4)
    bmesh.ops.translate(bm, verts=bm.verts, vec=(0.0, CASE_CY, CASE_CZ))
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    return obj_from_bm("CRT_Housing", bm, MAT["case"], smooth_angle=math.radians(34.0))


def build_pedestal():
    bm = bmesh.new()
    box(bm, (0.0, CASE_CY + 0.01, PED_H * 0.5 + 0.012), (0.32, 0.30, PED_H - 0.02))
    bevel_all(bm, offset=0.012, segments=3)
    # swivel disc resting on the desk
    bmesh.ops.create_cone(bm, cap_ends=True, cap_tris=False, segments=48,
                          radius1=0.145, radius2=0.155, depth=0.024,
                          matrix=Matrix.Translation((0.0, CASE_CY + 0.01, 0.012)))
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    return obj_from_bm("Pedestal", bm, MAT["case_dk"], smooth_angle=math.radians(34.0))


def build_bezel():
    """Frame around the tube face: outer rect minus inner opening, solidified."""
    ow, oh = 0.420, 0.290
    iw, ih = OPEN_HW * 2.0, OPEN_HH * 2.0
    y = FRONT_Y - 0.002

    bm = bmesh.new()

    def rect(hw, hh):
        return [bm.verts.new((-hw, y, SCREEN_CZ - hh)),
                bm.verts.new((hw, y, SCREEN_CZ - hh)),
                bm.verts.new((hw, y, SCREEN_CZ + hh)),
                bm.verts.new((-hw, y, SCREEN_CZ + hh))]

    o = rect(ow * 0.5, oh * 0.5)
    i = rect(iw * 0.5, ih * 0.5)
    for k in range(4):
        n = (k + 1) % 4
        bm.faces.new((o[k], o[n], i[n], i[k]))
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    ob = obj_from_bm("Bezel", bm, MAT["bezel"])

    sol = ob.modifiers.new("Solidify", 'SOLIDIFY')
    sol.thickness = 0.045
    sol.offset = 1.0            # extrude back into the housing
    bev = ob.modifiers.new("Bevel", 'BEVEL')
    bev.width = 0.005
    bev.segments = 3
    bev.harden_normals = False
    return ob


def build_glass():
    bm = bmesh.new()
    build_curved_panel(bm, 0.174, 0.122, FRONT_Y + 0.001, 0.030)
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    ob = obj_from_bm("ScreenGlass", bm, MAT["glass"], smooth_angle=math.radians(60.0))
    sol = ob.modifiers.new("Solidify", 'SOLIDIFY')
    sol.thickness = 0.008
    sol.offset = 1.0
    return ob


def build_phosphor():
    bm = bmesh.new()
    build_curved_panel(bm, 0.161, 0.110, FRONT_Y + 0.014, 0.026)
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    return obj_from_bm("Phosphor", bm, MAT["phosphor"], smooth_angle=math.radians(60.0))


def build_screen_text():
    """Glowing bars standing in for lines of monospaced text."""
    rng = random.Random(7)
    bm = bmesh.new()
    hw, hh = 0.161, 0.110
    base_y = FRONT_Y + 0.014
    bulge = 0.026
    left = -0.142
    line_h = 0.0068
    step = 0.0168
    top_z = SCREEN_CZ + 0.082

    for row in range(10):
        z = top_z - row * step
        v = (z - SCREEN_CZ) / hh
        if row == 9:
            segs = [(left, 0.020)]                       # prompt
        else:
            n_chunks = rng.randint(1, 3)
            segs = []
            x = left
            for _ in range(n_chunks):
                w = rng.uniform(0.020, 0.085)
                if x + w > 0.145:
                    break
                segs.append((x, w))
                x += w + rng.uniform(0.008, 0.018)
        for x0, w in segs:
            cx = x0 + w * 0.5
            u = cx / hw
            y = base_y - bulge * screen_falloff(u, v) - 0.0022
            box(bm, (cx, y, z), (w, 0.0025, line_h))

    # blinking cursor block after the prompt
    cz = top_z - 9 * step
    cx = left + 0.028
    cy = base_y - bulge * screen_falloff(cx / hw, (cz - SCREEN_CZ) / hh) - 0.0022
    box(bm, (cx, cy, cz), (0.008, 0.0025, line_h * 1.45))

    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    return obj_from_bm("ScreenText", bm, MAT["text"])


# ---------------------------------------------------------------------------
# front panel: brand plate, knobs, LED
# ---------------------------------------------------------------------------

def build_front_panel():
    bm = bmesh.new()
    # recessed name plate on the lower left
    box(bm, (-0.135, FRONT_Y + 0.004, 0.140), (0.130, 0.014, 0.028))
    # thin ventilation slot under the tube
    for i in range(5):
        box(bm, (-0.02 + i * 0.016, FRONT_Y + 0.003, 0.128), (0.006, 0.012, 0.050))
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    ob = obj_from_bm("FrontPlate", bm, MAT["bezel"])

    # power indicator
    led = bmesh.new()
    bmesh.ops.create_cone(led, cap_ends=True, cap_tris=False, segments=20,
                          radius1=0.006, radius2=0.006, depth=0.010,
                          matrix=Matrix.Translation((-0.185, FRONT_Y - 0.003, 0.163))
                          @ Matrix.Rotation(math.radians(90.0), 4, 'X'))
    bmesh.ops.recalc_face_normals(led, faces=led.faces)
    obj_from_bm("PowerLED", led, MAT["led"], smooth_angle=math.radians(40.0))
    return ob


def build_knobs():
    """Three fluted control knobs (brightness / contrast / vertical hold)."""
    bm = bmesh.new()
    for idx, kx in enumerate((0.085, 0.140, 0.195)):
        radius = 0.021 if idx < 2 else 0.017
        sub = bmesh.new()
        bmesh.ops.create_cone(sub, cap_ends=True, cap_tris=False, segments=64,
                              radius1=radius, radius2=radius * 0.93, depth=0.032)
        # flute the barrel
        for v in sub.verts:
            r = math.hypot(v.co.x, v.co.y)
            if r > 1e-4:
                a = math.atan2(v.co.y, v.co.x)
                f = 1.0 + 0.045 * math.sin(14.0 * a)
                v.co.x *= f
                v.co.y *= f
        geom = list(sub.verts) + list(sub.edges) + list(sub.faces)
        bmesh.ops.bevel(sub, geom=geom, offset=0.0022, offset_type='OFFSET',
                        segments=2, profile=0.5, affect='EDGES', clamp_overlap=True)
        m = (Matrix.Translation((kx, FRONT_Y - 0.011, 0.140))
             @ Matrix.Rotation(math.radians(90.0), 4, 'X')
             @ Matrix.Rotation(math.radians(18.0 * idx), 4, 'Z'))
        bmesh.ops.transform(sub, matrix=m, verts=sub.verts)
        bmesh.ops.recalc_face_normals(sub, faces=sub.faces)
        tmp = bpy.data.meshes.new("knob_tmp")
        sub.to_mesh(tmp)
        sub.free()
        bm.from_mesh(tmp)
        bpy.data.meshes.remove(tmp)
    return obj_from_bm("Knobs", bm, MAT["case_dk"], smooth_angle=math.radians(30.0))


def build_knob_pointers():
    bm = bmesh.new()
    for idx, kx in enumerate((0.085, 0.140, 0.195)):
        radius = 0.021 if idx < 2 else 0.017
        a = math.radians(60.0 + 40.0 * idx)
        box(bm, (kx + math.cos(a) * radius * 0.5,
                 FRONT_Y - 0.028,
                 0.140 + math.sin(a) * radius * 0.5),
            (0.0045, 0.003, radius * 0.85))
        pointer = bm.faces[-6:]
        bmesh.ops.rotate(bm, verts=list({v for f in pointer for v in f.verts}),
                         cent=(kx, FRONT_Y - 0.028, 0.140),
                         matrix=Matrix.Rotation(a - math.pi * 0.5, 3, 'Y'))
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    return obj_from_bm("KnobPointers", bm, MAT["keycap"])


# ---------------------------------------------------------------------------
# rear: vent ribs and connector plugs
# ---------------------------------------------------------------------------

def build_vents():
    bm = bmesh.new()
    y = BACK_Y - 0.004
    for i in range(12):
        z = 0.385 - i * 0.0125
        box(bm, (0.0, y, z), (0.24, 0.014, 0.0062))
    # side vents on both flanks
    for side in (-1.0, 1.0):
        for i in range(8):
            box(bm, (side * (CASE_W * 0.5 - 0.012), CASE_CY + 0.10, 0.20 + i * 0.016),
                (0.016, 0.16, 0.0075))
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    return obj_from_bm("Vents", bm, MAT["case_dk"])


def build_connectors():
    """D-sub shell with thumbscrews, two coax barrels and a power inlet."""
    shells = bmesh.new()
    pins = bmesh.new()
    metal = bmesh.new()

    # --- D-sub style serial connector -------------------------------------
    dx, dz = -0.075, 0.215
    y0 = BACK_Y - 0.006
    box(shells, (dx, y0 + 0.012, dz), (0.096, 0.030, 0.030))
    # trapezoid: pinch the top of the shell
    for v in shells.verts:
        if v.co.z > dz:
            v.co.x = dx + (v.co.x - dx) * 0.86
    box(pins, (dx, y0 + 0.030, dz), (0.072, 0.012, 0.017))
    for k in range(9):
        px = dx - 0.030 + k * 0.0075
        bmesh.ops.create_cone(metal, cap_ends=True, cap_tris=False, segments=10,
                              radius1=0.0016, radius2=0.0016, depth=0.014,
                              matrix=Matrix.Translation((px, y0 + 0.036, dz + 0.004))
                              @ Matrix.Rotation(math.radians(90.0), 4, 'X'))
    for sx in (-0.056, 0.056):
        bmesh.ops.create_cone(metal, cap_ends=True, cap_tris=False, segments=16,
                              radius1=0.0065, radius2=0.0055, depth=0.020,
                              matrix=Matrix.Translation((dx + sx, y0 + 0.020, dz))
                              @ Matrix.Rotation(math.radians(90.0), 4, 'X'))

    # --- coax barrel plugs -------------------------------------------------
    for bx in (0.055, 0.105):
        bmesh.ops.create_cone(metal, cap_ends=True, cap_tris=False, segments=28,
                              radius1=0.0135, radius2=0.0135, depth=0.030,
                              matrix=Matrix.Translation((bx, y0 + 0.014, dz))
                              @ Matrix.Rotation(math.radians(90.0), 4, 'X'))
        bmesh.ops.create_cone(shells, cap_ends=True, cap_tris=False, segments=28,
                              radius1=0.0175, radius2=0.0175, depth=0.022,
                              matrix=Matrix.Translation((bx, y0 + 0.036, dz))
                              @ Matrix.Rotation(math.radians(90.0), 4, 'X'))

    # --- mains inlet -------------------------------------------------------
    box(shells, (0.0, y0 + 0.016, 0.330), (0.060, 0.036, 0.042))
    box(pins, (0.0, y0 + 0.038, 0.330), (0.044, 0.014, 0.028))
    for px, pz in ((-0.012, 0.336), (0.012, 0.336), (0.0, 0.320)):
        bmesh.ops.create_cone(metal, cap_ends=True, cap_tris=False, segments=12,
                              radius1=0.0022, radius2=0.0022, depth=0.016,
                              matrix=Matrix.Translation((px, y0 + 0.044, pz))
                              @ Matrix.Rotation(math.radians(90.0), 4, 'X'))

    for b in (shells, pins, metal):
        bmesh.ops.recalc_face_normals(b, faces=b.faces)
    obj_from_bm("PlugShells", shells, MAT["rubber"], smooth_angle=math.radians(35.0))
    obj_from_bm("PlugBodies", pins, MAT["bezel"])
    return obj_from_bm("PlugMetal", metal, MAT["metal"], smooth_angle=math.radians(35.0))


# ---------------------------------------------------------------------------
# cables
# ---------------------------------------------------------------------------

def make_cable(name, points, radius, material, poly=False, closed_caps=True):
    cu = bpy.data.curves.new(name, 'CURVE')
    cu.dimensions = '3D'
    cu.resolution_u = 12
    cu.bevel_depth = radius
    cu.bevel_resolution = 6
    cu.use_fill_caps = closed_caps

    if poly:
        sp = cu.splines.new('POLY')
        sp.points.add(len(points) - 1)
        for p, co in zip(sp.points, points):
            p.co = (co[0], co[1], co[2], 1.0)
    else:
        sp = cu.splines.new('BEZIER')
        sp.bezier_points.add(len(points) - 1)
        for bp, co in zip(sp.bezier_points, points):
            bp.co = Vector(co)
            bp.handle_left_type = 'AUTO'
            bp.handle_right_type = 'AUTO'

    ob = bpy.data.objects.new(name, cu)
    ob.data.materials.append(material)
    bpy.context.collection.objects.link(ob)
    return ob


def build_rear_cables():
    r = 0.009
    make_cable("Cable_Serial", [
        (-0.075, BACK_Y + 0.030, 0.215),
        (-0.105, BACK_Y + 0.150, 0.140),
        (-0.070, BACK_Y + 0.260, r + 0.002),
        (0.180, BACK_Y + 0.330, r + 0.002),
        (0.520, BACK_Y + 0.230, r + 0.002),
    ], r, MAT["rubber"])

    make_cable("Cable_Coax_A", [
        (0.055, BACK_Y + 0.028, 0.215),
        (0.105, BACK_Y + 0.120, 0.150),
        (0.070, BACK_Y + 0.240, r + 0.002),
        (-0.220, BACK_Y + 0.300, r + 0.002),
        (-0.560, BACK_Y + 0.190, r + 0.002),
    ], r, MAT["rubber"])

    make_cable("Cable_Coax_B", [
        (0.105, BACK_Y + 0.028, 0.215),
        (0.165, BACK_Y + 0.140, 0.120),
        (0.150, BACK_Y + 0.250, r + 0.002),
        (0.330, BACK_Y + 0.380, r + 0.002),
    ], r, MAT["rubber"])

    rp = 0.011
    make_cable("Cable_Mains", [
        (0.0, BACK_Y + 0.042, 0.330),
        (0.045, BACK_Y + 0.170, 0.230),
        (0.030, BACK_Y + 0.300, rp + 0.002),
        (-0.060, BACK_Y + 0.520, rp + 0.002),
        (-0.060, BACK_Y + 0.900, rp + 0.002),
    ], rp, MAT["rubber"])


def build_coiled_cable():
    """Classic coiled keyboard lead from the keyboard back to the case."""
    a = Vector((0.005, -0.298, 0.042))
    b = Vector((-0.140, -0.150, 0.055))
    axis = b - a
    length = axis.length
    d = axis.normalized()
    side = d.cross(Vector((0.0, 0.0, 1.0))).normalized()
    up = side.cross(d).normalized()

    pts = [Vector((0.005, -0.330, 0.038)), a.copy()]
    turns, n = 8, 260
    for i in range(n + 1):
        t = i / n
        r = 0.020 * (math.sin(math.pi * t) ** 0.45)
        ang = 2.0 * math.pi * turns * t
        pts.append(a + d * (length * t)
                   + side * (r * math.cos(ang))
                   + up * (r * math.sin(ang)))
    pts.append(Vector((-0.170, -0.140, 0.050)))
    make_cable("Cable_KeyboardCoil", [tuple(p) for p in pts], 0.0045,
               MAT["rubber"], poly=True)


# ---------------------------------------------------------------------------
# keyboard
# ---------------------------------------------------------------------------

KB_BACK_Y, KB_FRONT_Y = -0.300, -0.552
KB_BACK_H, KB_FRONT_H = 0.055, 0.022
KB_SLOPE = (KB_FRONT_H - KB_BACK_H) / (KB_FRONT_Y - KB_BACK_Y)
KB_TILT = math.atan(KB_SLOPE)


def kb_top_z(y):
    return KB_BACK_H + KB_SLOPE * (y - KB_BACK_Y)


def build_keyboard_case():
    bm = bmesh.new()
    w = 0.60
    cy = (KB_BACK_Y + KB_FRONT_Y) * 0.5
    box(bm, (0.0, cy, 0.03), (w, KB_BACK_Y - KB_FRONT_Y, 0.06))

    # slope the top face and raise the shell off the desk on feet
    for v in bm.verts:
        if v.co.z > 0.03:
            v.co.z = kb_top_z(v.co.y)
        else:
            v.co.z = 0.0
        if v.co.y < cy:                      # slight front narrowing
            v.co.x *= 0.985

    bevel_all(bm, offset=0.008, segments=3)

    # recessed key well lip
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    ob = obj_from_bm("KeyboardCase", bm, MAT["case"], smooth_angle=math.radians(34.0))

    feet = bmesh.new()
    for fx in (-0.255, 0.255):
        for fy in (KB_BACK_Y - 0.022, KB_FRONT_Y + 0.022):
            bmesh.ops.create_cone(feet, cap_ends=True, cap_tris=False, segments=16,
                                  radius1=0.014, radius2=0.014, depth=0.008,
                                  matrix=Matrix.Translation((fx, fy, 0.004)))
    bmesh.ops.recalc_face_normals(feet, faces=feet.faces)
    obj_from_bm("KeyboardFeet", feet, MAT["rubber"], smooth_angle=math.radians(35.0))
    return ob


def add_keycap(bm, cx, cy, width, depth=0.031, height=0.012):
    """Tapered keycap sitting on the sloped keyboard deck."""
    z0 = kb_top_z(cy) + 0.001
    res = box(bm, (0.0, 0.0, height * 0.5), (width, depth, height))
    verts = res["verts"]
    top = [v for v in verts if v.co.z > height * 0.4]
    for v in top:
        v.co.x *= 0.84
        v.co.y *= 0.84
        v.co.z -= 0.0015
    geom = list(verts) + [e for e in bm.edges if all(v in verts for v in e.verts)] \
        + [f for f in bm.faces if all(v in verts for v in f.verts)]
    bmesh.ops.bevel(bm, geom=geom, offset=0.0016, offset_type='OFFSET',
                    segments=2, profile=0.6, affect='EDGES', clamp_overlap=True)
    moved = {v for v in bm.verts if v.tag} if False else None  # placeholder, unused
    m = (Matrix.Translation((cx, cy, z0))
         @ Matrix.Rotation(KB_TILT, 4, 'X'))
    # transform only the verts belonging to this cap: collect by proximity to origin
    fresh = [v for v in bm.verts if abs(v.co.x) < width and abs(v.co.y) < depth
             and -0.001 < v.co.z < height + 0.001]
    bmesh.ops.transform(bm, matrix=m, verts=fresh)
    return moved


def build_keys():
    light = bmesh.new()
    dark = bmesh.new()

    unit = 0.0395
    cap = 0.031
    rows_y = [-0.327, -0.370, -0.412, -0.455, -0.500]
    x0 = -(13 * unit) * 0.5

    # rows 0..3: full alphanumeric field, dark keys at the row extremities
    for r_i, ry in enumerate(rows_y[:4]):
        for c in range(14):
            cx = x0 + c * unit
            edge = (c == 0) or (c >= 12 and r_i in (1, 2, 3))
            width = cap * (1.5 if (edge and c >= 12) else 1.0)
            target = dark if edge else light
            if edge and c >= 12:
                if c == 13:
                    continue
                cx += unit * 0.5
            add_keycap(target, cx, ry, width)

    # bottom row: modifiers plus spacebar
    by = rows_y[4]
    add_keycap(dark, x0 + 0.0 * unit, by, cap * 1.4)
    add_keycap(dark, x0 + 1.6 * unit, by, cap * 1.2)
    add_keycap(light, 0.0, by, cap * 6.2)
    add_keycap(dark, x0 + 11.4 * unit, by, cap * 1.2)
    add_keycap(dark, x0 + 13.0 * unit, by, cap * 1.4)

    for b in (light, dark):
        bmesh.ops.recalc_face_normals(b, faces=b.faces)
    obj_from_bm("Keycaps", light, MAT["keycap"], smooth_angle=math.radians(30.0))
    return obj_from_bm("KeycapsAccent", dark, MAT["keycap_d"], smooth_angle=math.radians(30.0))


# ---------------------------------------------------------------------------
# environment, lights, camera
# ---------------------------------------------------------------------------

def build_desk():
    bm = bmesh.new()
    bmesh.ops.create_grid(bm, x_segments=1, y_segments=1, size=3.0)
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    return obj_from_bm("Desk", bm, MAT["desk"])


def setup_world(scene):
    world = bpy.data.worlds.new("TerminalWorld")
    world.use_nodes = True
    bg = world.node_tree.nodes["Background"]
    bg.inputs["Color"].default_value = (0.035, 0.038, 0.048, 1.0)
    bg.inputs["Strength"].default_value = 0.6
    scene.world = world


def add_area_light(name, location, target, energy, size, color=(1.0, 1.0, 1.0)):
    data = bpy.data.lights.new(name, 'AREA')
    data.energy = energy
    data.size = size
    data.color = color
    ob = bpy.data.objects.new(name, data)
    ob.location = location
    direction = Vector(target) - Vector(location)
    ob.rotation_euler = direction.to_track_quat('-Z', 'Y').to_euler()
    bpy.context.collection.objects.link(ob)
    return ob


def setup_lights():
    focus = (0.0, -0.05, 0.28)
    add_area_light("Key", (-1.05, -1.20, 1.30), focus, 260.0, 1.1,
                   color=(1.0, 0.95, 0.88))
    add_area_light("Fill", (1.30, -0.85, 0.75), focus, 90.0, 1.4,
                   color=(0.72, 0.80, 1.0))
    add_area_light("Rim", (0.55, 1.35, 1.05), focus, 180.0, 0.8,
                   color=(0.85, 0.90, 1.0))
    add_area_light("DeskBounce", (0.0, -0.85, 0.16), (0.0, -0.2, 0.30), 25.0, 0.9,
                   color=(1.0, 0.86, 0.70))


def setup_camera(scene):
    data = bpy.data.cameras.new("Camera")
    data.lens = 62.0
    data.sensor_width = 36.0
    data.dof.use_dof = True
    data.dof.aperture_fstop = 4.0

    cam = bpy.data.objects.new("Camera", data)
    cam.location = (0.82, -1.12, 0.58)
    aim = Vector((-0.01, -0.10, 0.28))
    cam.rotation_euler = (aim - Vector(cam.location)).to_track_quat('-Z', 'Y').to_euler()
    bpy.context.collection.objects.link(cam)

    focus = bpy.data.objects.new("FocusTarget", None)
    focus.empty_display_size = 0.05
    focus.location = (0.0, -0.17, SCREEN_CZ)
    bpy.context.collection.objects.link(focus)
    data.dof.focus_object = focus

    scene.camera = cam
    return cam


# ---------------------------------------------------------------------------
# main
# ---------------------------------------------------------------------------

def main():
    scene = reset_scene()

    build_desk()
    build_pedestal()
    build_housing()
    build_bezel()
    build_phosphor()
    build_screen_text()
    build_glass()
    build_front_panel()
    build_knobs()
    build_knob_pointers()
    build_vents()
    build_connectors()
    build_rear_cables()

    build_keyboard_case()
    build_keys()
    build_coiled_cable()

    setup_world(scene)
    setup_lights()
    setup_camera(scene)


main()
