"""
claude-055 : A toy locomotive with wheels, chimney and cab
Blender 4.5 LTS -- builds the scene only (no render, no file output).
"""

import bpy
import bmesh
from math import pi, sin, cos, radians
from mathutils import Matrix, Vector, Euler

# ----------------------------------------------------------------------------
# scene reset
# ----------------------------------------------------------------------------
bpy.ops.wm.read_factory_settings(use_empty=True)

scene = bpy.context.scene
try:
    scene.render.engine = 'BLENDER_EEVEE_NEXT'
except TypeError:
    pass
scene.render.resolution_x = 1600
scene.render.resolution_y = 1000
scene.unit_settings.system = 'METRIC'

SC = scene.collection


# ----------------------------------------------------------------------------
# helpers
# ----------------------------------------------------------------------------
def make_material(name, color, roughness=0.45, metallic=0.0, emission=None,
                  emission_strength=1.0):
    mat = bpy.data.materials.new(name)
    mat.use_nodes = True
    bsdf = mat.node_tree.nodes["Principled BSDF"]
    bsdf.inputs["Base Color"].default_value = (*color, 1.0)
    bsdf.inputs["Roughness"].default_value = roughness
    bsdf.inputs["Metallic"].default_value = metallic
    if emission is not None:
        bsdf.inputs["Emission Color"].default_value = (*emission, 1.0)
        bsdf.inputs["Emission Strength"].default_value = emission_strength
    return mat


def placement(loc=(0.0, 0.0, 0.0), rot=(0.0, 0.0, 0.0), scale=(1.0, 1.0, 1.0)):
    return (Matrix.Translation(loc)
            @ Euler(rot, 'XYZ').to_matrix().to_4x4()
            @ Matrix.Diagonal((*scale, 1.0)))


def finish(name, bm, mat=None, parent=None, matrix=None):
    """Turn a bmesh into a linked object (bmesh is consumed)."""
    if matrix is not None:
        bmesh.ops.transform(bm, matrix=matrix, verts=bm.verts)
    bm.normal_update()
    me = bpy.data.meshes.new(name)
    bm.to_mesh(me)
    bm.free()
    me.validate()
    obj = bpy.data.objects.new(name, me)
    SC.objects.link(obj)
    if mat is not None:
        obj.data.materials.append(mat)
    if parent is not None:
        obj.parent = parent
    return obj


def box_into(bm, center, size):
    """Axis aligned box added into an existing bmesh."""
    bmesh.ops.create_cube(
        bm, size=1.0,
        matrix=Matrix.Translation(center) @ Matrix.Diagonal((*size, 1.0)))


def add_box(name, center, size, mat=None, parent=None, rot=(0, 0, 0)):
    bm = bmesh.new()
    bmesh.ops.create_cube(bm, size=1.0, matrix=Matrix.Diagonal((*size, 1.0)))
    return finish(name, bm, mat, parent, placement(center, rot))


def add_cylinder(name, radius, depth, loc=(0, 0, 0), rot=(0, 0, 0),
                 segments=32, mat=None, parent=None, radius_top=None,
                 caps=True, scale=(1, 1, 1)):
    """Cylinder / truncated cone along local +Z, sides shaded smooth."""
    r_top = radius if radius_top is None else radius_top
    bm = bmesh.new()
    bmesh.ops.create_cone(bm, cap_ends=caps, cap_tris=False,
                          segments=segments, radius1=radius, radius2=r_top,
                          depth=depth, matrix=Matrix.Identity(4),
                          calc_uvs=True)
    bm.normal_update()
    for f in bm.faces:
        if abs(f.normal.z) < 0.5:
            f.smooth = True
    return finish(name, bm, mat, parent, placement(loc, rot, scale))


def add_sphere(name, radius, loc=(0, 0, 0), scale=(1, 1, 1), rot=(0, 0, 0),
               mat=None, parent=None, u=24, v=12):
    bm = bmesh.new()
    bmesh.ops.create_uvsphere(bm, u_segments=u, v_segments=v, radius=radius,
                              matrix=Matrix.Identity(4), calc_uvs=True)
    for f in bm.faces:
        f.smooth = True
    return finish(name, bm, mat, parent, placement(loc, rot, scale))


def add_window_panel(name, width, height, thickness, win_w, win_h, win_z,
                     loc, rot=(0, 0, 0), mat=None, parent=None):
    """Flat panel in the local XZ plane (thickness along Y) with a window hole."""
    bm = bmesh.new()
    hw, hh, ht = width * 0.5, height * 0.5, thickness * 0.5
    wl, wr = -win_w * 0.5, win_w * 0.5
    wb, wt = win_z - win_h * 0.5, win_z + win_h * 0.5
    # below / above the opening
    box_into(bm, (0.0, 0.0, (-hh + wb) * 0.5), (width, thickness, wb + hh))
    box_into(bm, (0.0, 0.0, (hh + wt) * 0.5), (width, thickness, hh - wt))
    # left / right pillars
    box_into(bm, ((-hw + wl) * 0.5, 0.0, (wb + wt) * 0.5),
             (wl + hw, thickness, win_h))
    box_into(bm, ((hw + wr) * 0.5, 0.0, (wb + wt) * 0.5),
             (hw - wr, thickness, win_h))
    del ht
    return finish(name, bm, mat, parent, placement(loc, rot))


def add_arch_roof(name, x0, x1, half_w, height, base_z, mat=None, parent=None,
                  segments=22, thickness=0.035):
    """Half tube roof shell, thickened with a solidify modifier."""
    bm = bmesh.new()
    rows = []
    for x in (x0, x1):
        row = [bm.verts.new((x, cos(pi * i / segments) * half_w,
                             base_z + sin(pi * i / segments) * height))
               for i in range(segments + 1)]
        rows.append(row)
    bm.verts.ensure_lookup_table()
    for i in range(segments):
        f = bm.faces.new((rows[0][i], rows[0][i + 1],
                          rows[1][i + 1], rows[1][i]))
        f.smooth = True
    obj = finish(name, bm, mat, parent)
    mod = obj.modifiers.new("Solidify", 'SOLIDIFY')
    mod.thickness = thickness
    mod.offset = 1.0
    return obj


# ----------------------------------------------------------------------------
# materials
# ----------------------------------------------------------------------------
MAT_RED     = make_material("ToyRed",      (0.560, 0.045, 0.040), 0.32)
MAT_GREEN   = make_material("ToyGreen",    (0.035, 0.190, 0.105), 0.34)
MAT_BLACK   = make_material("ToyBlack",    (0.022, 0.022, 0.026), 0.42)
MAT_GREY    = make_material("DarkSteel",   (0.075, 0.078, 0.085), 0.38, 0.85)
MAT_YELLOW  = make_material("ToyYellow",   (0.780, 0.520, 0.045), 0.35)
MAT_BRASS   = make_material("Brass",       (0.720, 0.480, 0.130), 0.22, 1.0)
MAT_LENS    = make_material("LampLens",    (1.000, 0.900, 0.640), 0.12,
                            emission=(1.0, 0.86, 0.55), emission_strength=6.0)
MAT_GROUND  = make_material("Ground",      (0.300, 0.300, 0.310), 0.90)
MAT_RAIL    = make_material("Rail",        (0.320, 0.300, 0.290), 0.35, 1.0)
MAT_SLEEPER = make_material("Sleeper",     (0.150, 0.100, 0.065), 0.85)

# ----------------------------------------------------------------------------
# key dimensions
# ----------------------------------------------------------------------------
GAUGE       = 0.42          # wheel centre plane offset in Y
DRIVE_R     = 0.26
DRIVE_W     = 0.09
LEAD_R      = 0.15
LEAD_W      = 0.075
DRIVE_X     = (-0.55, 0.05)
LEAD_X      = 0.75
DECK_TOP    = 0.36
BOILER_R    = 0.30
BOILER_Z    = 0.66
CAB_X0, CAB_X1 = -0.98, -0.30
CAB_TOP     = 1.16
CAB_HALF_W  = 0.37

loco = bpy.data.objects.new("Locomotive", None)
loco.empty_display_type = 'PLAIN_AXES'
loco.empty_display_size = 0.4
SC.objects.link(loco)


# ----------------------------------------------------------------------------
# chassis
# ----------------------------------------------------------------------------
add_box("Footplate", (0.0, 0.0, 0.33), (2.06, 0.74, 0.06), MAT_RED, loco)
add_box("DeckTrim", (0.0, 0.0, 0.295), (2.02, 0.78, 0.02), MAT_YELLOW, loco)

for s in (1, -1):
    add_box("Frame_%d" % s, (-0.05, s * 0.30, 0.215), (1.86, 0.05, 0.20),
            MAT_GREY, loco)
add_box("FrameCross", (-0.05, 0.0, 0.155), (1.60, 0.58, 0.07), MAT_GREY, loco)

# buffer beam, buffers and coupling hook
add_box("BufferBeam", (1.03, 0.0, 0.39), (0.09, 0.90, 0.20), MAT_RED, loco)
for s in (1, -1):
    add_cylinder("BufferStem_%d" % s, 0.045, 0.14, (1.11, s * 0.30, 0.39),
                 rot=(0, pi / 2, 0), segments=16, mat=MAT_GREY, parent=loco)
    add_cylinder("BufferHead_%d" % s, 0.075, 0.04, (1.185, s * 0.30, 0.39),
                 rot=(0, pi / 2, 0), segments=20, mat=MAT_BLACK, parent=loco)
add_cylinder("CouplingHook", 0.035, 0.16, (1.12, 0.0, 0.33),
             rot=(0, pi / 2, 0), segments=12, mat=MAT_BRASS, parent=loco)

# rear beam
add_box("RearBeam", (-1.06, 0.0, 0.39), (0.08, 0.86, 0.20), MAT_RED, loco)

# cow catcher slats
for i in range(5):
    off = (i - 2) * 0.115
    add_box("Catcher_%d" % i, (1.19, off, 0.17),
            (0.24, 0.035, 0.30), MAT_YELLOW, loco, rot=(0.0, radians(38), 0.0))
add_box("CatcherRail", (1.29, 0.0, 0.055), (0.06, 0.72, 0.05), MAT_YELLOW, loco)


# ----------------------------------------------------------------------------
# wheels
# ----------------------------------------------------------------------------
def make_wheel(name, x, side, radius, width, spokes=8, phase=0.0):
    y = side * GAUGE
    z = radius
    axis_rot = (pi / 2, 0.0, 0.0)
    add_cylinder(name + "_Tyre", radius, width, (x, y, z), axis_rot,
                 segments=40, mat=MAT_BLACK, parent=loco)
    add_cylinder(name + "_Web", radius * 0.84, width * 0.75, (x, y, z),
                 axis_rot, segments=36, mat=MAT_RED, parent=loco)
    add_cylinder(name + "_Hub", radius * 0.20, width * 1.5, (x, y, z),
                 axis_rot, segments=20, mat=MAT_BRASS, parent=loco)
    y_out = y + side * (width * 0.5 + 0.012)
    for i in range(spokes):
        a = pi * i / spokes + phase
        add_box("%s_Spoke_%d" % (name, i), (x, y_out, z),
                (0.045, 0.028, radius * 1.62), MAT_YELLOW, loco,
                rot=(0.0, a, 0.0))
    return y_out


CRANK_R = DRIVE_R * 0.58
CRANK_A = radians(-38.0)

for side in (1, -1):
    for i, dx in enumerate(DRIVE_X):
        y_face = make_wheel("Drive_%d_%d" % (i, side), dx, side,
                            DRIVE_R, DRIVE_W, spokes=8, phase=radians(11))
        cx = dx + cos(CRANK_A) * CRANK_R
        cz = DRIVE_R + sin(CRANK_A) * CRANK_R
        add_cylinder("Crank_%d_%d" % (i, side), 0.035, 0.10,
                     (cx, y_face + side * 0.04, cz), (pi / 2, 0, 0),
                     segments=14, mat=MAT_BRASS, parent=loco)
    # coupling rod linking both drivers
    x_a = DRIVE_X[0] + cos(CRANK_A) * CRANK_R
    x_b = DRIVE_X[1] + cos(CRANK_A) * CRANK_R
    rod_z = DRIVE_R + sin(CRANK_A) * CRANK_R
    add_box("CouplingRod_%d" % side,
            ((x_a + x_b) * 0.5, side * (GAUGE + DRIVE_W * 0.5 + 0.075), rod_z),
            (abs(x_b - x_a) + 0.11, 0.030, 0.070), MAT_GREY, loco)

    make_wheel("Lead_%d" % side, LEAD_X, side, LEAD_R, LEAD_W, spokes=6)

for dx in DRIVE_X:
    add_cylinder("Axle_%.2f" % dx, 0.038, GAUGE * 2.0, (dx, 0.0, DRIVE_R),
                 (pi / 2, 0, 0), segments=16, mat=MAT_GREY, parent=loco)
add_cylinder("AxleLead", 0.032, GAUGE * 2.0, (LEAD_X, 0.0, LEAD_R),
             (pi / 2, 0, 0), segments=16, mat=MAT_GREY, parent=loco)

# cylinder blocks / steam chests
for s in (1, -1):
    add_box("CylBlock_%d" % s, (0.58, s * 0.42, 0.44), (0.38, 0.19, 0.24),
            MAT_GREY, loco)
    add_cylinder("CylCap_%d" % s, 0.105, 0.05, (0.77, s * 0.42, 0.44),
                 (0, pi / 2, 0), segments=20, mat=MAT_BRASS, parent=loco)
    add_cylinder("PistonRod_%d" % s, 0.022, 0.34,
                 (0.22, s * 0.42, 0.44), (0, pi / 2, 0), segments=12,
                 mat=MAT_BRASS, parent=loco)


# ----------------------------------------------------------------------------
# boiler, smokebox, domes, chimney
# ----------------------------------------------------------------------------
add_cylinder("Boiler", BOILER_R, 1.20, (0.15, 0.0, BOILER_Z), (0, pi / 2, 0),
             segments=48, mat=MAT_RED, parent=loco)
for bx in (-0.15, 0.20, 0.55):
    add_cylinder("BoilerBand_%.2f" % bx, BOILER_R + 0.012, 0.045,
                 (bx, 0.0, BOILER_Z), (0, pi / 2, 0), segments=48,
                 mat=MAT_YELLOW, parent=loco)

add_cylinder("Smokebox", 0.32, 0.24, (0.87, 0.0, BOILER_Z), (0, pi / 2, 0),
             segments=48, mat=MAT_BLACK, parent=loco)
add_cylinder("SmokeboxDoor", 0.30, 0.05, (1.00, 0.0, BOILER_Z),
             (0, pi / 2, 0), segments=48, mat=MAT_BLACK, parent=loco)
add_sphere("DoorDish", 0.29, (0.99, 0.0, BOILER_Z), scale=(0.28, 1.0, 1.0),
           mat=MAT_BLACK, parent=loco)
add_cylinder("DoorRing", 0.30, 0.02, (1.015, 0.0, BOILER_Z), (0, pi / 2, 0),
             segments=48, mat=MAT_BRASS, parent=loco)
add_cylinder("DoorHandle", 0.022, 0.24, (1.07, 0.0, BOILER_Z), (pi / 2, 0, 0),
             segments=12, mat=MAT_BRASS, parent=loco)

# chimney
add_cylinder("ChimneyBase", 0.115, 0.08, (0.86, 0.0, 0.97), segments=28,
             mat=MAT_BLACK, parent=loco)
add_cylinder("Chimney", 0.088, 0.24, (0.86, 0.0, 1.11), segments=28,
             radius_top=0.078, mat=MAT_BLACK, parent=loco)
add_cylinder("ChimneyBand", 0.094, 0.04, (0.86, 0.0, 1.11), segments=28,
             mat=MAT_YELLOW, parent=loco)
add_cylinder("ChimneyCap", 0.086, 0.09, (0.86, 0.0, 1.26), segments=28,
             radius_top=0.122, mat=MAT_BRASS, parent=loco)

# steam dome + sand dome
add_cylinder("DomeBase", 0.170, 0.11, (0.24, 0.0, 0.945), segments=32,
             mat=MAT_YELLOW, parent=loco)
add_sphere("DomeTop", 0.170, (0.24, 0.0, 1.00), scale=(1.0, 1.0, 0.72),
           mat=MAT_YELLOW, parent=loco)
add_cylinder("SandDome", 0.120, 0.09, (0.56, 0.0, 0.945), segments=26,
             mat=MAT_RED, parent=loco)
add_sphere("SandDomeTop", 0.120, (0.56, 0.0, 0.99), scale=(1.0, 1.0, 0.70),
           mat=MAT_RED, parent=loco)

# safety valves and whistle
for vx in (-0.06, 0.04):
    add_cylinder("SafetyValve_%.2f" % vx, 0.035, 0.13, (vx, 0.0, 0.99),
                 segments=14, mat=MAT_BRASS, parent=loco)
add_cylinder("WhistleStem", 0.030, 0.14, (-0.36, 0.0, 1.00), segments=14,
             mat=MAT_BRASS, parent=loco)
add_sphere("WhistleBell", 0.055, (-0.36, 0.0, 1.09), scale=(1.0, 1.0, 1.25),
           mat=MAT_BRASS, parent=loco)

# handrails along the boiler
for s in (1, -1):
    add_cylinder("Handrail_%d" % s, 0.013, 1.30, (0.30, s * 0.305, 0.83),
                 (0, pi / 2, 0), segments=10, mat=MAT_BRASS, parent=loco)
    for hx in (-0.28, 0.30, 0.90):
        add_cylinder("RailPost_%d_%.2f" % (s, hx), 0.012, 0.075,
                     (hx, s * 0.285, 0.83), (pi / 2, 0, 0), segments=8,
                     mat=MAT_BRASS, parent=loco)

# headlamp on the smokebox front
add_box("Headlamp", (1.11, 0.0, 0.86), (0.16, 0.17, 0.17), MAT_YELLOW, loco)
add_cylinder("LampLens", 0.062, 0.05, (1.20, 0.0, 0.86), (0, pi / 2, 0),
             segments=20, mat=MAT_LENS, parent=loco)
add_box("LampBracket", (1.05, 0.0, 0.79), (0.10, 0.10, 0.06), MAT_BLACK, loco)


# ----------------------------------------------------------------------------
# cab
# ----------------------------------------------------------------------------
cab_len = CAB_X1 - CAB_X0
cab_h = CAB_TOP - DECK_TOP
cab_mid_x = (CAB_X0 + CAB_X1) * 0.5
cab_mid_z = (DECK_TOP + CAB_TOP) * 0.5

for s in (1, -1):
    add_window_panel("CabSide_%d" % s, cab_len, cab_h, 0.04,
                     0.34, 0.34, 0.13,
                     (cab_mid_x, s * (CAB_HALF_W - 0.02), cab_mid_z),
                     mat=MAT_GREEN, parent=loco)

# rear wall (rotated so its local X runs along world Y)
add_window_panel("CabRear", CAB_HALF_W * 2.0, cab_h, 0.05,
                 0.40, 0.32, 0.14,
                 (CAB_X0 + 0.025, 0.0, cab_mid_z), rot=(0.0, 0.0, pi / 2),
                 mat=MAT_GREEN, parent=loco)

# front wall with a large opening for the boiler backhead
add_window_panel("CabFront", CAB_HALF_W * 2.0, cab_h, 0.05,
                 0.52, 0.56, 0.10,
                 (CAB_X1 - 0.025, 0.0, cab_mid_z), rot=(0.0, 0.0, pi / 2),
                 mat=MAT_GREEN, parent=loco)

add_arch_roof("CabRoof", CAB_X0 - 0.07, CAB_X1 + 0.07, CAB_HALF_W + 0.06,
              0.20, CAB_TOP - 0.02, MAT_RED, loco, segments=24, thickness=0.035)

# cab waist trim and floor
add_box("CabTrim", (cab_mid_x, 0.0, DECK_TOP + 0.02),
        (cab_len + 0.03, CAB_HALF_W * 2.0 + 0.03, 0.035), MAT_YELLOW, loco)
add_box("CabFloor", (cab_mid_x, 0.0, DECK_TOP + 0.015),
        (cab_len - 0.06, CAB_HALF_W * 1.9, 0.02), MAT_BLACK, loco)

# boiler backhead inside the cab
add_sphere("Backhead", BOILER_R, (-0.45, 0.0, BOILER_Z),
           scale=(0.55, 1.0, 1.0), mat=MAT_GREY, parent=loco)
add_cylinder("FireboxDoor", 0.11, 0.05, (-0.58, 0.0, BOILER_Z),
             (0, pi / 2, 0), segments=24, mat=MAT_BRASS, parent=loco)
for gy in (-0.11, 0.11):
    add_cylinder("Gauge_%.2f" % gy, 0.045, 0.04, (-0.58, gy, BOILER_Z + 0.20),
                 (0, pi / 2, 0), segments=16, mat=MAT_BRASS, parent=loco)
add_cylinder("ThrottleLever", 0.018, 0.30, (-0.62, 0.14, 0.86),
             (radians(25), 0, 0), segments=10, mat=MAT_BRASS, parent=loco)


# ----------------------------------------------------------------------------
# ground and track
# ----------------------------------------------------------------------------
bm = bmesh.new()
bmesh.ops.create_grid(bm, x_segments=1, y_segments=1, size=14.0,
                      matrix=Matrix.Identity(4), calc_uvs=True)
ground = finish("Ground", bm, MAT_GROUND, matrix=Matrix.Translation((0, 0, -0.12)))

for s in (1, -1):
    add_box("Rail_%d" % s, (0.0, s * GAUGE, -0.03), (14.0, 0.075, 0.06), MAT_RAIL)
for i in range(-11, 12):
    add_box("Sleeper_%d" % i, (i * 0.56, 0.0, -0.09), (0.18, 1.45, 0.06),
            MAT_SLEEPER)


# ----------------------------------------------------------------------------
# lighting
# ----------------------------------------------------------------------------
world = bpy.data.worlds.new("World")
world.use_nodes = True
world.node_tree.nodes["Background"].inputs[0].default_value = (0.05, 0.06, 0.08, 1.0)
world.node_tree.nodes["Background"].inputs[1].default_value = 0.6
scene.world = world


def add_light(name, ltype, loc, target, energy, size=1.0, color=(1, 1, 1)):
    data = bpy.data.lights.new(name, ltype)
    data.energy = energy
    data.color = color
    if ltype == 'AREA':
        data.shape = 'SQUARE'
        data.size = size
    elif ltype == 'SUN':
        data.angle = radians(2.5)
    obj = bpy.data.objects.new(name, data)
    obj.location = loc
    obj.rotation_euler = (Vector(target) - Vector(loc)).to_track_quat(
        '-Z', 'Y').to_euler()
    SC.objects.link(obj)
    return obj


aim = (0.0, 0.0, 0.65)
add_light("KeyArea", 'AREA', (2.8, -3.2, 3.4), aim, 900.0, size=2.6,
          color=(1.0, 0.96, 0.90))
add_light("FillArea", 'AREA', (-3.4, -2.4, 1.7), aim, 260.0, size=3.0,
          color=(0.80, 0.87, 1.0))
add_light("RimArea", 'AREA', (-2.2, 3.0, 2.6), aim, 420.0, size=2.0,
          color=(1.0, 0.92, 0.82))
add_light("Sun", 'SUN', (4.0, 4.0, 6.0), (0, 0, 0), 1.6,
          color=(1.0, 0.97, 0.92))


# ----------------------------------------------------------------------------
# camera
# ----------------------------------------------------------------------------
cam_data = bpy.data.cameras.new("Camera")
cam_data.lens = 52.0
cam_data.clip_start = 0.05
cam_data.clip_end = 200.0
cam_data.dof.use_dof = True
cam = bpy.data.objects.new("Camera", cam_data)
cam.location = (3.55, -4.05, 2.35)
look_at = Vector((-0.05, 0.0, 0.68))
cam.rotation_euler = (look_at - Vector(cam.location)).to_track_quat(
    '-Z', 'Y').to_euler()
cam_data.dof.focus_distance = (look_at - Vector(cam.location)).length
cam_data.dof.aperture_fstop = 5.6
SC.objects.link(cam)
scene.camera = cam

print("Toy locomotive scene built: %d objects" % len(SC.all_objects))
