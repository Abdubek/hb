"""
claude-123 : Compact industrial pump skid
Blender 4.5 LTS - headless scene construction only (no render, no file output).

Builds a bolted-frame skid carrying two motor/pump trains, a stainless buffer
tank, suction & discharge headers with flanged elbows, gate valves, pressure
gauges, a control cabinet and conduit, plus lighting and a camera.
"""

import math
import bpy
import bmesh
from mathutils import Vector, Quaternion

# ----------------------------------------------------------------------------
# scene reset
# ----------------------------------------------------------------------------
bpy.ops.wm.read_factory_settings(use_empty=True)

scene = bpy.context.scene
scene.unit_settings.system = 'METRIC'
try:
    scene.render.engine = 'BLENDER_EEVEE_NEXT'
except TypeError:
    scene.render.engine = 'CYCLES'

COLL = bpy.data.collections.new("PumpSkid")
scene.collection.children.link(COLL)
vl = bpy.context.view_layer
vl.active_layer_collection = vl.layer_collection.children["PumpSkid"]


# ----------------------------------------------------------------------------
# materials
# ----------------------------------------------------------------------------
def make_mat(name, color, metallic=0.0, roughness=0.5, spec=0.5):
    mat = bpy.data.materials.new(name)
    mat.use_nodes = True
    bsdf = mat.node_tree.nodes["Principled BSDF"]
    bsdf.inputs["Base Color"].default_value = (color[0], color[1], color[2], 1.0)
    bsdf.inputs["Metallic"].default_value = metallic
    bsdf.inputs["Roughness"].default_value = roughness
    if "Specular IOR Level" in bsdf.inputs:
        bsdf.inputs["Specular IOR Level"].default_value = spec
    return mat


M = {
    "steel":     make_mat("Steel_Galv",   (0.60, 0.62, 0.65), 1.0, 0.40),
    "steel_br":  make_mat("Steel_Bright", (0.78, 0.79, 0.80), 1.0, 0.18),
    "steel_dk":  make_mat("Steel_Dark",   (0.13, 0.14, 0.16), 1.0, 0.50),
    "frame":     make_mat("Paint_Frame",  (0.20, 0.22, 0.25), 0.0, 0.48),
    "deck":      make_mat("Deck_Plate",   (0.34, 0.35, 0.37), 0.8, 0.55),
    "pump":      make_mat("Paint_Blue",   (0.05, 0.17, 0.40), 0.0, 0.34),
    "motor":     make_mat("Paint_Motor",  (0.22, 0.28, 0.31), 0.0, 0.42),
    "guard":     make_mat("Paint_Yellow", (0.83, 0.60, 0.05), 0.0, 0.40),
    "valve":     make_mat("Paint_Valve",  (0.10, 0.24, 0.20), 0.0, 0.38),
    "wheel":     make_mat("Paint_Red",    (0.52, 0.06, 0.05), 0.0, 0.38),
    "tank":      make_mat("Tank_Steel",   (0.72, 0.74, 0.76), 1.0, 0.24),
    "cab":       make_mat("Cabinet_Gray", (0.55, 0.56, 0.55), 0.0, 0.40),
    "rubber":    make_mat("Rubber",       (0.04, 0.04, 0.045), 0.0, 0.75),
    "white":     make_mat("Dial_White",   (0.88, 0.88, 0.86), 0.0, 0.35),
    "glass":     make_mat("Sight_Glass",  (0.55, 0.68, 0.72), 0.0, 0.10),
    "concrete":  make_mat("Concrete",     (0.30, 0.29, 0.28), 0.0, 0.92),
}


# ----------------------------------------------------------------------------
# low level helpers
# ----------------------------------------------------------------------------
def finish(ob, mat=None, smooth=True, name=None):
    """Assign material and smooth quad faces only (keeps caps flat)."""
    if name:
        ob.name = name
    if mat is not None:
        ob.data.materials.append(mat)
    if smooth:
        for p in ob.data.polygons:
            p.use_smooth = (len(p.vertices) == 4)
    return ob


def mesh_from_data(name, verts, faces, mat=None, smooth=True):
    me = bpy.data.meshes.new(name)
    me.from_pydata([tuple(v) for v in verts], [], faces)
    me.validate()
    me.update()
    ob = bpy.data.objects.new(name, me)
    COLL.objects.link(ob)
    return finish(ob, mat, smooth)


def cyl(r, depth, loc, rot=(0, 0, 0), verts=24, mat=None, name="Cyl"):
    bpy.ops.mesh.primitive_cylinder_add(vertices=verts, radius=r, depth=depth,
                                        location=tuple(loc), rotation=tuple(rot))
    return finish(bpy.context.object, mat, True, name)


def cone(r1, r2, depth, loc, rot=(0, 0, 0), verts=24, mat=None, name="Cone"):
    bpy.ops.mesh.primitive_cone_add(vertices=verts, radius1=r1, radius2=r2,
                                    depth=depth, location=tuple(loc),
                                    rotation=tuple(rot))
    return finish(bpy.context.object, mat, True, name)


def box(dims, loc, mat=None, name="Box", rot=(0, 0, 0)):
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=tuple(loc),
                                    rotation=tuple(rot))
    ob = bpy.context.object
    ob.scale = tuple(dims)
    return finish(ob, mat, False, name)


def sphere(r, loc, scale=(1, 1, 1), segs=32, rings=16, mat=None, name="Sphere"):
    bpy.ops.mesh.primitive_uv_sphere_add(segments=segs, ring_count=rings,
                                         radius=r, location=tuple(loc))
    ob = bpy.context.object
    ob.scale = tuple(scale)
    return finish(ob, mat, True, name)


def torus(major, minor, loc, axis=(0, 0, 1), maj_seg=32, min_seg=12,
          mat=None, name="Torus"):
    rot = Vector((0, 0, 1)).rotation_difference(Vector(axis).normalized()).to_euler()
    bpy.ops.mesh.primitive_torus_add(major_radius=major, minor_radius=minor,
                                     major_segments=maj_seg,
                                     minor_segments=min_seg,
                                     location=tuple(loc), rotation=tuple(rot))
    return finish(bpy.context.object, mat, True, name)


def basis_for(direction):
    """Return (quaternion, e1, e2) for a +Z aligned primitive pointing 'direction'."""
    d = Vector(direction).normalized()
    q = Vector((0, 0, 1)).rotation_difference(d)
    return q, (q @ Vector((1, 0, 0))), (q @ Vector((0, 1, 0)))


# ----------------------------------------------------------------------------
# swept tube along a polyline with rounded (elbow) corners
# ----------------------------------------------------------------------------
def path_frames(points, bend_r, arc_steps):
    P = [Vector(p) for p in points]
    frames = [(P[0].copy(), (P[1] - P[0]).normalized())]
    for i in range(1, len(P) - 1):
        a = (P[i] - P[i - 1]).normalized()
        b = (P[i + 1] - P[i]).normalized()
        ang = a.angle(b)
        if ang < 1e-4:
            continue
        t = bend_r * math.tan(min(ang, math.radians(160)) * 0.5)
        start = P[i] - a * t
        n = (b - a * a.dot(b))
        if n.length < 1e-6:
            continue
        n.normalize()
        center = start + n * bend_r
        axis = a.cross(b).normalized()
        v0 = start - center
        frames.append((start, a))
        for s in range(1, arc_steps + 1):
            q = Quaternion(axis, ang * s / arc_steps)
            frames.append((center + (q @ v0), (q @ a).normalized()))
    frames.append((P[-1].copy(), (P[-1] - P[-2]).normalized()))
    return frames


def tube(points, r, bend_r=0.12, seg=16, arc_steps=6, mat=None, name="Pipe"):
    frames = path_frames(points, bend_r, arc_steps)
    verts, faces = [], []
    ref, prev_t = None, None
    for pos, tan in frames:
        if ref is None:
            up = Vector((0, 0, 1))
            if abs(tan.dot(up)) > 0.95:
                up = Vector((1, 0, 0))
            ref = (up - tan * tan.dot(up)).normalized()
        else:
            ref = (prev_t.rotation_difference(tan) @ ref).normalized()
        bin_ = tan.cross(ref).normalized()
        for k in range(seg):
            phi = 2.0 * math.pi * k / seg
            verts.append(pos + ref * (r * math.cos(phi)) + bin_ * (r * math.sin(phi)))
        prev_t = tan
    n = len(frames)
    for i in range(n - 1):
        for k in range(seg):
            a0 = i * seg + k
            a1 = i * seg + (k + 1) % seg
            faces.append((a0, a1, a1 + seg, a0 + seg))
    faces.append(tuple(range(seg - 1, -1, -1)))
    faces.append(tuple(range((n - 1) * seg, n * seg)))
    return mesh_from_data(name, verts, faces, mat, True)


# ----------------------------------------------------------------------------
# fittings
# ----------------------------------------------------------------------------
def flange(loc, normal, r_out, thick=0.024, n_bolts=8, mat=None, name="Flange"):
    mat = mat or M["steel"]
    q, e1, e2 = basis_for(normal)
    rot = q.to_euler()
    loc = Vector(loc)
    cyl(r_out, thick, loc, rot, 28, mat, name)
    rb = r_out * 0.76
    for i in range(n_bolts):
        a = 2.0 * math.pi * i / n_bolts
        p = loc + e1 * (rb * math.cos(a)) + e2 * (rb * math.sin(a))
        cyl(r_out * 0.10, thick * 2.1, p, rot, 8, M["steel_dk"], "Bolt")


def flanged_spool(p0, p1, r, r_flange, n_bolts=8, mat=None, name="Spool"):
    p0, p1 = Vector(p0), Vector(p1)
    d = (p1 - p0).normalized()
    tube([p0, p1], r, 0.05, 16, 2, mat or M["steel"], name)
    flange(p0, -d, r_flange, 0.024, n_bolts)
    flange(p1, d, r_flange, 0.024, n_bolts)


def gate_valve(loc, axis, up, s=1.0, name="Valve"):
    loc = Vector(loc)
    ax = Vector(axis).normalized()
    up = Vector(up).normalized()
    up = (up - ax * ax.dot(up)).normalized()

    rot_ax = Vector((0, 0, 1)).rotation_difference(ax).to_euler()
    q_up, e1, e2 = basis_for(up)
    rot_up = q_up.to_euler()

    # body + end connections
    cyl(0.125 * s, 0.30 * s, loc, rot_ax, 20, M["valve"], name + "_Body")
    sphere(0.14 * s, loc, (1, 1, 0.75), 24, 12, M["valve"], name + "_Bowl")
    flange(loc + ax * (0.16 * s), ax, 0.165 * s, 0.026 * s, 8)
    flange(loc - ax * (0.16 * s), -ax, 0.165 * s, 0.026 * s, 8)

    # bonnet / yoke / stem
    cyl(0.085 * s, 0.22 * s, loc + up * (0.19 * s), rot_up, 16, M["valve"], name + "_Bonnet")
    flange(loc + up * (0.30 * s), up, 0.115 * s, 0.022 * s, 6)
    cyl(0.052 * s, 0.24 * s, loc + up * (0.42 * s), rot_up, 12, M["valve"], name + "_Yoke")
    cyl(0.017 * s, 0.42 * s, loc + up * (0.40 * s), rot_up, 8, M["steel_br"], name + "_Stem")

    # handwheel
    wc = loc + up * (0.58 * s)
    torus(0.135 * s, 0.017 * s, wc, up, 28, 10, M["wheel"], name + "_Wheel")
    cyl(0.034 * s, 0.045 * s, wc, rot_up, 12, M["wheel"], name + "_Hub")
    for i in range(3):
        a = 2.0 * math.pi * i / 3.0
        d = (e1 * math.cos(a) + e2 * math.sin(a)).normalized()
        rot_sp = Vector((0, 0, 1)).rotation_difference(d).to_euler()
        cyl(0.011 * s, 0.14 * s, wc + d * (0.068 * s), rot_sp, 8,
            M["wheel"], name + "_Spoke")
    cyl(0.020 * s, 0.05 * s, loc + up * (0.66 * s), rot_up, 8,
        M["steel_br"], name + "_StemTop")


def pressure_gauge(loc, direction, s=1.0):
    d = Vector(direction).normalized()
    rot = Vector((0, 0, 1)).rotation_difference(d).to_euler()
    loc = Vector(loc)
    cyl(0.014 * s, 0.10 * s, loc + d * (0.05 * s), rot, 10, M["steel"], "GaugeStem")
    cyl(0.055 * s, 0.048 * s, loc + d * (0.124 * s), rot, 20, M["steel_dk"], "GaugeCase")
    cyl(0.047 * s, 0.010 * s, loc + d * (0.152 * s), rot, 20, M["white"], "GaugeDial")


# ----------------------------------------------------------------------------
# skid base frame
# ----------------------------------------------------------------------------
FX, FY = 1.50, 0.90          # frame half extents
BEAM_H, DECK_Z = 0.16, 0.18  # beam height, deck top

def build_frame():
    zc = BEAM_H * 0.5
    # longitudinal rails
    for y in (-FY + 0.05, FY - 0.05):
        box((2 * FX, 0.10, BEAM_H), (0, y, zc), M["frame"], "Rail")
        box((2 * FX, 0.14, 0.022), (0, y, BEAM_H - 0.011), M["frame"], "RailTopFlange")
        box((2 * FX, 0.14, 0.022), (0, y, 0.011), M["frame"], "RailBotFlange")
    # cross members
    for x in (-FX + 0.05, -0.55, 0.35, FX - 0.05):
        box((0.10, 2 * FY - 0.10, BEAM_H), (x, 0, zc), M["frame"], "CrossBeam")
    # deck plate
    box((2 * FX - 0.02, 2 * FY - 0.02, 0.022), (0, 0, DECK_Z - 0.011),
        M["deck"], "DeckPlate")
    # anti-slip bars on the deck
    for i in range(11):
        x = -FX + 0.20 + i * 0.26
        box((0.035, 2 * FY - 0.16, 0.014), (x, 0, DECK_Z + 0.006),
            M["deck"], "DeckBar")
    # feet pads and lifting lugs
    for sx in (-1, 1):
        for sy in (-1, 1):
            box((0.24, 0.22, 0.026), (sx * (FX - 0.18), sy * (FY - 0.12), 0.013),
                M["steel_dk"], "FootPad")
            for k in (-1, 1):
                cyl(0.016, 0.09, (sx * (FX - 0.18) + k * 0.07,
                                  sy * (FY - 0.12), 0.045),
                    (0, 0, 0), 8, M["steel_dk"], "AnchorBolt")
            lug = (sx * (FX - 0.06), sy * (FY - 0.05), DECK_Z + 0.06)
            box((0.16, 0.026, 0.16), lug, M["frame"], "LiftLug")
            torus(0.042, 0.011, (lug[0], lug[1], lug[2] + 0.03), (0, 1, 0),
                  20, 8, M["steel_dk"], "LiftEye")


# ----------------------------------------------------------------------------
# motor + centrifugal pump train
# ----------------------------------------------------------------------------
SHAFT_Z = 0.58
PED_TOP = 0.32

def build_train(y, tag):
    # grouted pedestal / common baseplate
    box((1.78, 0.54, 0.14), (-0.50, y, PED_TOP - 0.07), M["frame"], "Pedestal_" + tag)
    box((1.84, 0.60, 0.02), (-0.50, y, DECK_Z + 0.01), M["steel_dk"], "Shim_" + tag)

    # ---- motor -------------------------------------------------------------
    mx = -0.95
    rot_x = (0, math.radians(90), 0)
    cyl(0.20, 0.66, (mx, y, SHAFT_Z), rot_x, 32, M["motor"], "MotorBody_" + tag)
    for i in range(12):
        fx = mx - 0.30 + 0.028 + i * 0.049
        cyl(0.215, 0.020, (fx, y, SHAFT_Z), rot_x, 32, M["motor"], "MotorFin_" + tag)
    # end bells
    cyl(0.205, 0.06, (mx - 0.34, y, SHAFT_Z), rot_x, 32, M["motor"], "MotorEndB_" + tag)
    cyl(0.205, 0.06, (mx + 0.34, y, SHAFT_Z), rot_x, 32, M["motor"], "MotorEndF_" + tag)
    # fan cowl
    cyl(0.19, 0.13, (mx - 0.43, y, SHAFT_Z), rot_x, 28, M["motor"], "FanCowl_" + tag)
    cone(0.19, 0.115, 0.10, (mx - 0.545, y, SHAFT_Z), (0, math.radians(-90), 0),
         28, M["motor"], "FanCap_" + tag)
    # feet
    for fx in (mx - 0.21, mx + 0.21):
        box((0.15, 0.46, 0.10), (fx, y, PED_TOP + 0.05), M["motor"], "MotorFoot_" + tag)
        for sy in (-1, 1):
            cyl(0.014, 0.07, (fx, y + sy * 0.20, PED_TOP + 0.10), (0, 0, 0), 8,
                M["steel_dk"], "HoldDown_" + tag)
    # terminal box + eyebolt + nameplate
    box((0.26, 0.28, 0.15), (mx, y, SHAFT_Z + 0.27), M["motor"], "TermBox_" + tag)
    box((0.28, 0.30, 0.016), (mx, y, SHAFT_Z + 0.352), M["steel_dk"], "TermLid_" + tag)
    torus(0.030, 0.010, (mx + 0.16, y, SHAFT_Z + 0.22), (0, 1, 0), 20, 8,
          M["steel_dk"], "MotorEye_" + tag)
    box((0.11, 0.005, 0.07), (mx - 0.05, y - 0.205, SHAFT_Z + 0.06),
        M["steel_br"], "Nameplate_" + tag)

    # ---- coupling guard ----------------------------------------------------
    cyl(0.035, 0.30, (-0.46, y, SHAFT_Z), rot_x, 12, M["steel_br"], "Shaft_" + tag)
    cyl(0.135, 0.26, (-0.44, y, SHAFT_Z), rot_x, 20, M["guard"], "CouplingGuard_" + tag)
    box((0.26, 0.30, 0.014), (-0.44, y, SHAFT_Z - 0.135), M["guard"], "GuardBase_" + tag)

    # ---- pump --------------------------------------------------------------
    cyl(0.115, 0.28, (-0.16, y, SHAFT_Z), rot_x, 24, M["pump"], "BearingHouse_" + tag)
    for i in range(4):
        cyl(0.128, 0.016, (-0.26 + i * 0.055, y, SHAFT_Z), rot_x, 24,
            M["pump"], "BearingRib_" + tag)
    box((0.30, 0.24, 0.26), (-0.16, y, PED_TOP + 0.13), M["pump"], "PumpPed_" + tag)

    # volute casing
    vx = 0.10
    torus(0.185, 0.105, (vx, y, SHAFT_Z), (1, 0, 0), 32, 16, M["pump"],
          "Volute_" + tag)
    cyl(0.255, 0.05, (vx + 0.11, y, SHAFT_Z), rot_x, 32, M["pump"], "VoluteCover_" + tag)
    cyl(0.275, 0.04, (vx - 0.10, y, SHAFT_Z), rot_x, 32, M["pump"], "VolutePlate_" + tag)
    for i in range(10):                             # casing bolts
        a = 2.0 * math.pi * i / 10.0
        cyl(0.014, 0.05, (vx + 0.135, y + 0.235 * math.cos(a),
                          SHAFT_Z + 0.235 * math.sin(a)),
            rot_x, 8, M["steel_dk"], "CaseBolt_" + tag)

    # suction (axial, facing +X) and discharge (radial, up)
    flanged_spool((vx + 0.135, y, SHAFT_Z), (0.42, y, SHAFT_Z),
                  0.085, 0.155, 8, M["pump"], "Suction_" + tag)
    flanged_spool((vx, y, SHAFT_Z + 0.16), (vx, y, 0.96),
                  0.075, 0.140, 8, M["pump"], "Discharge_" + tag)
    # casing drain
    tube([(vx - 0.02, y, SHAFT_Z - 0.16), (vx - 0.02, y, PED_TOP + 0.10),
          (vx + 0.18, y, PED_TOP + 0.10)], 0.018, 0.05, 10, 4,
         M["steel"], "Drain_" + tag)


# ----------------------------------------------------------------------------
# buffer / seal-flush tank
# ----------------------------------------------------------------------------
TX, TR = 1.02, 0.40
T_BOT, T_TOP = 0.55, 1.60

def build_tank():
    cyl(TR, T_TOP - T_BOT, (TX, 0, (T_TOP + T_BOT) * 0.5), (0, 0, 0), 40,
        M["tank"], "TankShell")
    sphere(TR, (TX, 0, T_TOP), (1, 1, 0.55), 40, 20, M["tank"], "TankTopDome")
    sphere(TR, (TX, 0, T_BOT), (1, 1, 0.55), 40, 20, M["tank"], "TankBotDome")
    # weld seams
    for z in (0.90, 1.25):
        torus(TR, 0.010, (TX, 0, z), (0, 0, 1), 40, 8, M["tank"], "TankSeam")

    # legs with gussets
    for i in range(4):
        a = math.pi * 0.25 + i * math.pi * 0.5
        px, py = TX + 0.31 * math.cos(a), 0.31 * math.sin(a)
        cyl(0.045, T_BOT - DECK_Z + 0.12, (px, py, (DECK_Z + T_BOT + 0.12) * 0.5),
            (0, 0, 0), 12, M["frame"], "TankLeg")
        box((0.14, 0.14, 0.020), (px, py, DECK_Z + 0.01), M["steel_dk"], "LegPad")
    torus(TR * 0.86, 0.024, (TX, 0, T_BOT + 0.02), (0, 0, 1), 32, 8,
          M["frame"], "TankLegRing")

    # top nozzles: vent + level transmitter
    flanged_spool((TX - 0.12, 0, T_TOP + 0.18), (TX - 0.12, 0, T_TOP + 0.34),
                  0.045, 0.095, 6, M["tank"], "VentNozzle")
    cone(0.075, 0.03, 0.11, (TX - 0.12, 0, T_TOP + 0.40), (0, 0, 0), 16,
         M["steel"], "VentCap")
    flanged_spool((TX + 0.16, 0.06, T_TOP + 0.16), (TX + 0.16, 0.06, T_TOP + 0.30),
                  0.038, 0.085, 4, M["tank"], "LTNozzle")
    box((0.13, 0.13, 0.16), (TX + 0.16, 0.06, T_TOP + 0.40), M["cab"], "LevelXmtr")

    # side manway facing the camera
    mw = Vector((TX - 0.10, -TR + 0.02, 1.15))
    flanged_spool((mw.x, mw.y, mw.z), (mw.x, mw.y - 0.10, mw.z),
                  0.16, 0.235, 10, M["tank"], "Manway")
    cyl(0.235, 0.030, (mw.x, mw.y - 0.125, mw.z), (math.radians(90), 0, 0), 28,
        M["tank"], "ManwayCover")

    # tank side nozzles: discharge inlet (upper, -X) and suction outlet (bottom)
    flanged_spool((TX - TR + 0.01, 0, 1.50), (TX - TR - 0.09, 0, 1.50),
                  0.100, 0.175, 8, M["tank"], "TankInletNozzle")
    flanged_spool((TX, 0, T_BOT - 0.16), (TX, 0, T_BOT - 0.28),
                  0.100, 0.175, 8, M["tank"], "TankOutletNozzle")

    # sight glass with isolation cocks
    gx, gy = TX + 0.10, -TR - 0.06
    cyl(0.020, 0.62, (gx, gy, 1.02), (0, 0, 0), 12, M["glass"], "SightGlass")
    for z in (0.71, 1.33):
        tube([(TX - 0.02, gy + 0.10, z), (gx, gy + 0.10, z), (gx, gy, z)],
             0.014, 0.05, 10, 4, M["steel"], "GaugeLine")
        cyl(0.030, 0.05, (gx, gy + 0.05, z), (math.radians(90), 0, 0), 10,
            M["wheel"], "GaugeCock")
    box((0.06, 0.010, 0.66), (gx + 0.03, gy - 0.02, 1.02), M["white"], "GaugeScale")

    # nameplate
    box((0.14, 0.006, 0.09), (TX + 0.22, -TR - 0.005, 1.42),
        M["steel_br"], "TankPlate")


# ----------------------------------------------------------------------------
# process piping
# ----------------------------------------------------------------------------
SUC_R, DIS_R = 0.105, 0.105
SUC_X, SUC_Z = 0.90, 0.36
DIS_X, DIS_Z = 0.40, 1.32

def build_piping(train_ys):
    # ---- suction header under the tank -------------------------------------
    tube([(SUC_X, -0.68, SUC_Z), (SUC_X, 0.68, SUC_Z)], SUC_R, 0.10, 20, 2,
         M["steel"], "SuctionHeader")
    for sy in (-1, 1):
        flange((SUC_X, sy * 0.68, SUC_Z), (0, sy, 0), 0.175, 0.026, 8)
    # header supports
    for sy in (-1, 1):
        box((0.12, 0.12, SUC_Z - DECK_Z), (SUC_X, sy * 0.56, (SUC_Z + DECK_Z) * 0.5),
            M["frame"], "SucSupport")
        box((0.20, 0.20, 0.020), (SUC_X, sy * 0.56, SUC_Z - 0.10),
            M["frame"], "SucSaddle")

    # riser from header to tank bottom nozzle
    tube([(SUC_X, 0, SUC_Z), (SUC_X + 0.12, 0, SUC_Z), (SUC_X + 0.12, 0, T_BOT - 0.28)],
         SUC_R, 0.08, 20, 6, M["steel"], "SuctionRiser")

    # ---- discharge header ---------------------------------------------------
    tube([(DIS_X, -0.68, DIS_Z), (DIS_X, 0.68, DIS_Z)], DIS_R, 0.10, 20, 2,
         M["steel"], "DischargeHeader")
    for sy in (-1, 1):
        flange((DIS_X, sy * 0.68, DIS_Z), (0, sy, 0), 0.175, 0.026, 8)
    # header pipe rack
    for sy in (-1, 1):
        cyl(0.045, DIS_Z - DECK_Z, (DIS_X, sy * 0.80, (DIS_Z + DECK_Z) * 0.5),
            (0, 0, 0), 12, M["frame"], "RackPost")
        box((0.12, 0.12, 0.020), (DIS_X, sy * 0.80, DECK_Z + 0.01),
            M["steel_dk"], "RackBase")
    box((0.10, 1.72, 0.08), (DIS_X, 0, DIS_Z - 0.14), M["frame"], "RackBeam")
    for sy in (-1, 1):
        torus(DIS_R + 0.02, 0.014, (DIS_X, sy * 0.58, DIS_Z), (0, 1, 0), 20, 8,
              M["steel_dk"], "UBoltClamp")

    # header to tank inlet
    tube([(DIS_X, 0, DIS_Z), (DIS_X, 0, 1.50), (TX - TR - 0.09, 0, 1.50)],
         DIS_R, 0.14, 20, 8, M["steel"], "HeaderToTank")

    # ---- per pump branches --------------------------------------------------
    for y in train_ys:
        s = 1.0 if y > 0 else -1.0
        # suction branch: pump inlet -> down -> into header
        tube([(0.42, y, SHAFT_Z), (SUC_X, y, SHAFT_Z), (SUC_X, y, SUC_Z)],
             0.085, 0.14, 16, 7, M["steel"], "SuctionBranch")
        flange((0.42, y, SHAFT_Z), (-1, 0, 0), 0.155, 0.024, 8)
        gate_valve((0.62, y, SHAFT_Z), (1, 0, 0), (0, 0, 1), 0.85, "SucValve")

        # discharge branch: riser -> over to header
        tube([(0.10, y, 0.96), (0.10, y, DIS_Z), (DIS_X, y, DIS_Z)],
             0.075, 0.13, 16, 7, M["steel"], "DischargeBranch")
        # check valve then isolation gate valve on the riser
        cyl(0.105, 0.16, (0.10, y, 1.06), (0, 0, 0), 20, M["valve"], "CheckValve")
        flange((0.10, y, 1.14), (0, 0, 1), 0.145, 0.024, 8)
        flange((0.10, y, 0.985), (0, 0, -1), 0.145, 0.024, 8)
        gate_valve((0.10, y, 1.26), (0, 0, 1), (-1, 0, 0), 0.78, "DisValve")
        pressure_gauge((0.10 + 0.075, y - 0.02, 1.02), (0.4, -0.9, 0.2), 0.9)

        # seal flush line: tank down to pump gland
        tube([(TX - 0.34, s * 0.22, T_TOP - 0.10), (TX - 0.34, s * 0.22, 0.86),
              (0.02, s * 0.22, 0.86), (0.02, y - s * 0.10, 0.86),
              (0.02, y - s * 0.10, SHAFT_Z + 0.20)],
             0.016, 0.06, 10, 4, M["steel_br"], "SealFlush")


# ----------------------------------------------------------------------------
# local control cabinet + conduit
# ----------------------------------------------------------------------------
def build_cabinet(train_ys):
    cx, cz0, ch = -1.00, DECK_Z, 0.86
    box((0.30, 0.36, ch), (cx, 0, cz0 + ch * 0.5), M["cab"], "Cabinet")
    box((0.02, 0.32, ch - 0.06), (cx - 0.155, 0, cz0 + ch * 0.5),
        M["cab"], "CabinetDoor")
    box((0.34, 0.40, 0.030), (cx, 0, cz0 + ch + 0.015), M["cab"], "CabinetRoof")
    box((0.34, 0.40, 0.020), (cx, 0, cz0 + 0.01), M["steel_dk"], "CabinetBase")
    # door furniture
    cyl(0.022, 0.06, (cx - 0.18, -0.12, cz0 + ch * 0.5), (0, math.radians(90), 0),
        10, M["steel_dk"], "Handle")
    for i, col in enumerate((M["wheel"], M["white"], M["guard"])):
        cyl(0.020, 0.016, (cx - 0.168, -0.02 + i * 0.075, cz0 + ch - 0.14),
            (0, math.radians(90), 0), 12, col, "PilotLight")
    box((0.008, 0.16, 0.10), (cx - 0.162, 0.06, cz0 + 0.30), M["steel_dk"], "HMIPanel")

    # conduit runs to each motor terminal box
    for y in train_ys:
        s = 1.0 if y > 0 else -1.0
        tube([(cx, s * 0.19, cz0 + ch - 0.10),
              (cx + 0.09, s * 0.19, cz0 + ch - 0.10),
              (cx + 0.09, y - s * 0.15, cz0 + ch - 0.10),
              (cx + 0.09, y - s * 0.15, SHAFT_Z + 0.27)],
             0.022, 0.06, 10, 4, M["steel"], "Conduit")
        cyl(0.030, 0.05, (cx + 0.09, y - s * 0.15, SHAFT_Z + 0.27), (0, 0, 0), 10,
            M["rubber"], "ConduitGland")


# ----------------------------------------------------------------------------
# build the scene
# ----------------------------------------------------------------------------
TRAIN_Y = (-0.45, 0.45)

build_frame()
for yy, tag in zip(TRAIN_Y, ("A", "B")):
    build_train(yy, tag)
build_tank()
build_piping(TRAIN_Y)
build_cabinet(TRAIN_Y)

# ground slab
bpy.ops.mesh.primitive_plane_add(size=16.0, location=(0, 0, 0))
finish(bpy.context.object, M["concrete"], False, "GroundSlab")


# ----------------------------------------------------------------------------
# lighting
# ----------------------------------------------------------------------------
def add_area(name, loc, target, energy, size, shape='SQUARE', size_y=None):
    ld = bpy.data.lights.new(name, 'AREA')
    ld.energy = energy
    ld.shape = shape
    ld.size = size
    if size_y is not None:
        ld.size_y = size_y
    ob = bpy.data.objects.new(name, ld)
    COLL.objects.link(ob)
    ob.location = loc
    d = (Vector(target) - Vector(loc)).normalized()
    ob.rotation_euler = d.to_track_quat('-Z', 'Y').to_euler()
    return ob


add_area("KeyLight", (4.2, -4.0, 4.6), (0.1, 0.0, 0.85), 2200, 4.0)
add_area("FillLight", (-4.6, -2.6, 2.6), (-0.6, 0.0, 0.70), 700, 5.0)
add_area("RimLight", (-1.2, 4.6, 3.8), (0.3, 0.0, 1.10), 1100, 3.5)

sun_data = bpy.data.lights.new("SkyFill", 'SUN')
sun_data.energy = 1.6
sun_data.angle = math.radians(6.0)
sun = bpy.data.objects.new("SkyFill", sun_data)
COLL.objects.link(sun)
sun.rotation_euler = Vector((0.55, 0.25, -1.0)).normalized().to_track_quat('-Z', 'Y').to_euler()

# world
world = bpy.data.worlds.new("SkidWorld")
world.use_nodes = True
bg = world.node_tree.nodes["Background"]
bg.inputs["Color"].default_value = (0.045, 0.050, 0.058, 1.0)
bg.inputs["Strength"].default_value = 1.0
scene.world = world


# ----------------------------------------------------------------------------
# camera
# ----------------------------------------------------------------------------
cam_data = bpy.data.cameras.new("SkidCam")
cam_data.lens = 44.0
cam_data.clip_start = 0.05
cam_data.clip_end = 200.0
cam = bpy.data.objects.new("SkidCam", cam_data)
COLL.objects.link(cam)
cam.location = (4.55, -4.35, 2.75)
look_at = Vector((0.05, 0.0, 0.88))
cam.rotation_euler = (look_at - Vector(cam.location)).to_track_quat('-Z', 'Y').to_euler()
scene.camera = cam

print("Pump skid built: %d objects" % len(COLL.objects))
