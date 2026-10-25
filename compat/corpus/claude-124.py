import bpy, bmesh, math
from mathutils import Vector

# ---------------------------------------------------------------- infrastructure
def reset_scene():
    bpy.ops.wm.read_factory_settings(use_empty=True)
    bpy.context.scene.unit_settings.system = 'METRIC'

def coll(name):
    c = bpy.data.collections.get(name)
    if c is None:
        c = bpy.data.collections.new(name)
        bpy.context.scene.collection.children.link(c)
    return c

def make_mat(name, base, metallic=0.0, rough=0.5, emit=None, emit_str=0.0, alpha=1.0):
    m = bpy.data.materials.get(name)
    if m:
        return m
    m = bpy.data.materials.new(name)
    m.use_nodes = True
    n = m.node_tree.nodes.get("Principled BSDF")
    n.inputs["Base Color"].default_value = (base[0], base[1], base[2], 1.0)
    n.inputs["Metallic"].default_value = metallic
    n.inputs["Roughness"].default_value = rough
    if emit is not None:
        n.inputs["Emission Color"].default_value = (emit[0], emit[1], emit[2], 1.0)
        n.inputs["Emission Strength"].default_value = emit_str
    if alpha < 1.0:
        n.inputs["Alpha"].default_value = alpha
        try:
            m.blend_method = 'BLEND'
        except Exception:
            pass
    return m

def _finish(name, bm, c, mat, loc=(0, 0, 0), rot=(0, 0, 0), smooth=False):
    me = bpy.data.meshes.new(name)
    bm.to_mesh(me)
    bm.free()
    if smooth:
        for p in me.polygons:
            if abs(p.normal.z) < 0.7:
                p.use_smooth = True
    ob = bpy.data.objects.new(name, me)
    ob.location = loc
    ob.rotation_euler = rot
    (c if c else bpy.context.scene.collection).objects.link(ob)
    if mat:
        me.materials.append(mat)
    return ob

def add_box(name, size, loc, rot=(0, 0, 0), c=None, mat=None, bevel=0.0):
    bm = bmesh.new()
    bmesh.ops.create_cube(bm, size=1.0)
    bmesh.ops.scale(bm, vec=Vector(size), verts=bm.verts)
    if bevel > 0.0:
        bmesh.ops.bevel(bm, geom=list(bm.verts) + list(bm.edges), offset=bevel,
                        segments=2, affect='EDGES', profile=0.5)
    return _finish(name, bm, c, mat, loc, rot)

def add_cyl(name, r, depth, loc, rot=(0, 0, 0), seg=20, c=None, mat=None, r2=None):
    bm = bmesh.new()
    bmesh.ops.create_cone(bm, cap_ends=True, cap_tris=False, segments=seg,
                          radius1=r, radius2=(r if r2 is None else r2), depth=depth)
    return _finish(name, bm, c, mat, loc, rot, smooth=True)

def add_sphere(name, r, loc, c=None, mat=None, sub=2):
    bm = bmesh.new()
    bmesh.ops.create_icosphere(bm, subdivisions=sub, radius=r)
    ob = _finish(name, bm, c, mat, loc)
    for p in ob.data.polygons:
        p.use_smooth = True
    return ob

def add_link(name, p1, p2, r, seg=14, c=None, mat=None):
    """Tube spanning two points (arm links, rails, tubing)."""
    a, b = Vector(p1), Vector(p2)
    v = b - a
    rot = v.to_track_quat('Z', 'Y').to_euler()
    return add_cyl(name, r, v.length, (a + b) * 0.5, rot, seg=seg, c=c, mat=mat)

def add_plane(name, sx, sy, loc, rot=(0, 0, 0), c=None, mat=None):
    bm = bmesh.new()
    bmesh.ops.create_grid(bm, x_segments=1, y_segments=1, size=1.0)
    bmesh.ops.scale(bm, vec=(sx * 0.5, sy * 0.5, 1.0), verts=bm.verts)
    return _finish(name, bm, c, mat, loc, rot)

# ---------------------------------------------------------------- materials
reset_scene()

MAT = {
    "floor":    make_mat("Concrete", (0.20, 0.20, 0.21), 0.0, 0.85),
    "stripe":   make_mat("HazardYellow", (0.72, 0.52, 0.05), 0.0, 0.6),
    "frame":    make_mat("SteelFrame", (0.42, 0.44, 0.47), 0.9, 0.35),
    "paint":    make_mat("MachineBlue", (0.08, 0.16, 0.30), 0.3, 0.35),
    "roller":   make_mat("RollerSteel", (0.55, 0.57, 0.60), 1.0, 0.22),
    "rubber":   make_mat("Rubber", (0.05, 0.05, 0.055), 0.0, 0.75),
    "arch":     make_mat("ArchAlu", (0.62, 0.63, 0.66), 0.95, 0.28),
    "sensor":   make_mat("SensorBody", (0.09, 0.09, 0.10), 0.25, 0.4),
    "lens":     make_mat("Lens", (0.05, 0.09, 0.12), 0.1, 0.08),
    "led":      make_mat("LedBar", (0.6, 0.85, 1.0), 0.0, 0.4, emit=(0.55, 0.8, 1.0), emit_str=14.0),
    "laser":    make_mat("LaserRed", (1.0, 0.15, 0.1), 0.0, 0.4, emit=(1.0, 0.12, 0.06), emit_str=22.0),
    "beacon":   make_mat("Beacon", (1.0, 0.55, 0.05), 0.0, 0.35, emit=(1.0, 0.45, 0.05), emit_str=18.0),
    "screen":   make_mat("Screen", (0.05, 0.1, 0.12), 0.0, 0.25, emit=(0.25, 0.6, 0.65), emit_str=6.0),
    "robot":    make_mat("RobotWhite", (0.80, 0.80, 0.78), 0.15, 0.35),
    "robotJnt": make_mat("RobotGrey", (0.25, 0.26, 0.28), 0.6, 0.4),
    "fence":    make_mat("FenceYellow", (0.62, 0.45, 0.04), 0.5, 0.45),
    "mesh":     make_mat("WireMesh", (0.30, 0.31, 0.33), 0.85, 0.5),
    "cabinet":  make_mat("Cabinet", (0.30, 0.32, 0.34), 0.5, 0.4),
    "partA":    make_mat("PartAlu", (0.68, 0.69, 0.72), 1.0, 0.3),
    "partB":    make_mat("PartRed", (0.35, 0.06, 0.05), 0.2, 0.45),
    "cable":    make_mat("Cable", (0.04, 0.04, 0.05), 0.1, 0.6),
}

C_STAGE = coll("Stage")
C_CONV = coll("Conveyor")
C_ARCH = coll("SensorArches")
C_ROBOT = coll("Robot")
C_FENCE = coll("Fencing")
C_PROPS = coll("Props")

# ---------------------------------------------------------------- key dimensions
CONV_X0, CONV_X1 = -6.4, 6.4          # conveyor run along +X
BED_HW = 0.60                         # half width of roller bed
DECK_Z = 0.95                         # roller top height
RAIL_HW = BED_HW + 0.09
CELL_X = 7.6                          # fence half length
CELL_Y = 3.4                          # fence half depth

# ---------------------------------------------------------------- floor & markings
add_plane("Floor", 34, 26, (0, 0, 0), c=C_STAGE, mat=MAT["floor"])

for sy in (-1, 1):
    add_plane("HazardStripe", 15.2, 0.22, (0, sy * (CELL_Y - 0.55), 0.004),
              c=C_STAGE, mat=MAT["stripe"])
for i in range(9):                    # hatched walk-off zone near the gate
    add_plane("HatchMark", 0.9, 0.12, (-1.9 + i * 0.42, -CELL_Y - 0.75, 0.004),
              rot=(0, 0, math.radians(35)), c=C_STAGE, mat=MAT["stripe"])

# ---------------------------------------------------------------- conveyor frame
for sy in (-1, 1):
    add_box("SideRail", (CONV_X1 - CONV_X0 + 0.5, 0.09, 0.22),
            ((CONV_X0 + CONV_X1) * 0.5, sy * RAIL_HW, DECK_Z + 0.02),
            c=C_CONV, mat=MAT["paint"], bevel=0.012)
    add_box("ToeRail", (CONV_X1 - CONV_X0 + 0.5, 0.06, 0.10),
            ((CONV_X0 + CONV_X1) * 0.5, sy * RAIL_HW, DECK_Z - 0.30),
            c=C_CONV, mat=MAT["frame"])
    # low product guide above the rollers
    add_box("ProductGuide", (CONV_X1 - CONV_X0, 0.035, 0.10),
            ((CONV_X0 + CONV_X1) * 0.5, sy * (BED_HW - 0.02), DECK_Z + 0.10),
            c=C_CONV, mat=MAT["frame"])

leg_x = [CONV_X0 + 0.5 + i * 1.9 for i in range(7)]
for lx in leg_x:
    for sy in (-1, 1):
        add_box("Leg", (0.09, 0.09, DECK_Z - 0.08),
                (lx, sy * RAIL_HW, (DECK_Z - 0.08) * 0.5), c=C_CONV, mat=MAT["frame"])
        add_cyl("FootPad", 0.09, 0.03, (lx, sy * RAIL_HW, 0.015), seg=14,
                c=C_CONV, mat=MAT["rubber"])
    add_box("CrossMember", (0.08, RAIL_HW * 2, 0.08), (lx, 0, 0.30),
            c=C_CONV, mat=MAT["frame"])
    # diagonal brace
    add_link("Brace", (lx, -RAIL_HW, 0.10), (lx, RAIL_HW, 0.62), 0.022,
             seg=8, c=C_CONV, mat=MAT["frame"])

# rollers
n_roll = 27
for i in range(n_roll):
    rx = CONV_X0 + 0.35 + i * ((CONV_X1 - CONV_X0 - 0.7) / (n_roll - 1))
    add_cyl("Roller", 0.055, BED_HW * 2 - 0.02, (rx, 0, DECK_Z - 0.055),
            rot=(math.radians(90), 0, 0), seg=18, c=C_CONV, mat=MAT["roller"])
    for sy in (-1, 1):
        add_cyl("RollerHub", 0.032, 0.05, (rx, sy * (BED_HW + 0.03), DECK_Z - 0.055),
                rot=(math.radians(90), 0, 0), seg=12, c=C_CONV, mat=MAT["frame"])

# drive ends: motor, gearbox, chain guard
for sx in (-1, 1):
    ex = sx * (CONV_X1 + 0.18)
    add_cyl("DriveRoller", 0.075, BED_HW * 2, (ex, 0, DECK_Z - 0.055),
            rot=(math.radians(90), 0, 0), seg=20, c=C_CONV, mat=MAT["rubber"])
    add_box("ChainGuard", (0.34, 0.10, 0.34), (ex, RAIL_HW + 0.10, DECK_Z - 0.06),
            c=C_CONV, mat=MAT["paint"], bevel=0.02)
    add_cyl("Gearmotor", 0.11, 0.34, (ex - sx * 0.10, RAIL_HW + 0.34, DECK_Z - 0.20),
            rot=(math.radians(90), 0, 0), seg=16, c=C_CONV, mat=MAT["frame"])
    add_box("MotorTerm", (0.10, 0.10, 0.10), (ex - sx * 0.10, RAIL_HW + 0.34, DECK_Z - 0.05),
            c=C_CONV, mat=MAT["sensor"])
    add_link("MotorCable", (ex - sx * 0.10, RAIL_HW + 0.34, DECK_Z - 0.05),
             (ex - sx * 0.10, RAIL_HW + 0.36, 0.05), 0.018, seg=8,
             c=C_CONV, mat=MAT["cable"])

# cable tray slung under the bed
add_box("CableTray", (CONV_X1 - CONV_X0, 0.16, 0.05), (0, RAIL_HW + 0.13, 0.42),
        c=C_CONV, mat=MAT["frame"])
for i in range(5):
    add_link("TrayLoom", (CONV_X0 + 0.4, RAIL_HW + 0.09 + i * 0.015, 0.46),
             (CONV_X1 - 0.4, RAIL_HW + 0.09 + i * 0.015, 0.46), 0.014, seg=8,
             c=C_CONV, mat=MAT["cable"])

# ---------------------------------------------------------------- sensor arches
def build_arch(ax, r=0.86, leg_h=1.55, name="Arch"):
    """Portal arch made from a poly curve with a round bevel, plus sensor heads."""
    pts = [(ax, -r, 0.0), (ax, -r, leg_h * 0.5), (ax, -r, leg_h)]
    seg = 18
    for i in range(seg + 1):
        a = math.pi * i / seg
        pts.append((ax, -r * math.cos(a), leg_h + r * math.sin(a)))
    pts += [(ax, r, leg_h * 0.5), (ax, r, 0.0)]

    cu = bpy.data.curves.new(name + "Curve", 'CURVE')
    cu.dimensions = '3D'
    cu.bevel_depth = 0.065
    cu.bevel_resolution = 4
    cu.use_fill_caps = True
    sp = cu.splines.new('POLY')
    sp.points.add(len(pts) - 1)
    for p, co in zip(sp.points, pts):
        p.co = (co[0], co[1], co[2], 1.0)
    ob = bpy.data.objects.new(name, cu)
    C_ARCH.objects.link(ob)
    cu.materials.append(MAT["arch"])

    # base plates
    for sy in (-1, 1):
        add_box("ArchBase", (0.26, 0.26, 0.03), (ax, sy * r, 0.015),
                c=C_ARCH, mat=MAT["frame"])
        for dx, dy in ((-0.09, -0.09), (0.09, -0.09), (-0.09, 0.09), (0.09, 0.09)):
            add_cyl("AnchorBolt", 0.016, 0.05, (ax + dx, sy * r + dy, 0.04), seg=8,
                    c=C_ARCH, mat=MAT["frame"])

    apex = leg_h + r
    target = Vector((ax, 0.0, DECK_Z + 0.05))

    # top-down camera head with ring illuminator
    add_box("HeadTop", (0.24, 0.30, 0.22), (ax, 0.0, apex - 0.18),
            c=C_ARCH, mat=MAT["sensor"], bevel=0.02)
    add_cyl("LensTop", 0.075, 0.10, (ax, 0.0, apex - 0.33), seg=20,
            c=C_ARCH, mat=MAT["lens"])
    add_cyl("RingLight", 0.15, 0.045, (ax, 0.0, apex - 0.36), seg=28,
            c=C_ARCH, mat=MAT["led"], r2=0.15)
    add_link("HeadCable", (ax, 0.10, apex - 0.08), (ax, r * 0.55, apex - 0.02),
             0.016, seg=8, c=C_ARCH, mat=MAT["cable"])

    # oblique heads clamped to the arc
    for ang in (math.radians(40), math.radians(140), math.radians(65), math.radians(115)):
        base = Vector((ax, -r * math.cos(ang), leg_h + r * math.sin(ang)))
        d = (target - base)
        d.normalize()
        add_box("Clamp", (0.13, 0.13, 0.10), base, c=C_ARCH, mat=MAT["frame"])
        body_a = base + d * 0.10
        body_b = base + d * 0.34
        add_link("HeadOblique", body_a, body_b, 0.055, seg=16, c=C_ARCH, mat=MAT["sensor"])
        add_sphere("LensOblique", 0.048, body_b + d * 0.02, c=C_ARCH, mat=MAT["lens"], sub=2)

    # laser profile line emitters near the apex
    for sy in (-1, 1):
        add_box("LaserStrip", (0.05, 0.05, 0.34),
                (ax, sy * 0.42, apex - 0.30), rot=(math.radians(sy * 12), 0, 0),
                c=C_ARCH, mat=MAT["laser"])

    # side plates carrying the sensor bus along the legs
    for sy in (-1, 1):
        add_box("LegPlate", (0.06, 0.10, 0.9), (ax + 0.09, sy * r, leg_h * 0.6),
                c=C_ARCH, mat=MAT["frame"])
    return ob

for ax in (-3.4, -0.2, 3.0):
    build_arch(ax)

# ---------------------------------------------------------------- light curtains
for sx in (-1, 1):
    for sy in (-1, 1):
        px = sx * (CONV_X1 - 0.9)
        add_box("CurtainPost", (0.09, 0.09, 1.5), (px, sy * (BED_HW + 0.30), 0.75 + 0.02),
                c=C_ARCH, mat=MAT["sensor"], bevel=0.01)
        add_box("CurtainWindow", (0.03, 0.045, 1.15),
                (px - sx * 0.05, sy * (BED_HW + 0.30), 0.95),
                c=C_ARCH, mat=MAT["led"])
        add_box("CurtainFoot", (0.2, 0.2, 0.03), (px, sy * (BED_HW + 0.30), 0.015),
                c=C_ARCH, mat=MAT["frame"])

# ---------------------------------------------------------------- robot arm
RB = Vector((-1.6, 2.05, 0.0))          # pedestal centre

add_box("RobotPedestal", (0.9, 0.9, 0.55), RB + Vector((0, 0, 0.275)),
        c=C_ROBOT, mat=MAT["cabinet"], bevel=0.02)
add_box("PedestalPlate", (1.05, 1.05, 0.04), RB + Vector((0, 0, 0.57)),
        c=C_ROBOT, mat=MAT["frame"])
add_cyl("RobotBase", 0.34, 0.16, RB + Vector((0, 0, 0.67)), seg=28,
        c=C_ROBOT, mat=MAT["robotJnt"])
add_cyl("Waist", 0.26, 0.30, RB + Vector((0, 0, 0.90)), seg=26,
        c=C_ROBOT, mat=MAT["robot"])

# posed kinematic chain: shoulder -> elbow -> wrist -> tool
J0 = RB + Vector((0.0, 0.0, 1.06))
J1 = RB + Vector((0.18, -0.62, 1.86))
J2 = RB + Vector((0.30, -1.28, 1.42))
J3 = RB + Vector((0.34, -1.55, 1.24))

add_cyl("ShoulderYoke", 0.19, 0.40, J0, rot=(math.radians(90), 0, math.radians(-16)),
        seg=22, c=C_ROBOT, mat=MAT["robotJnt"])
add_link("UpperArm", J0, J1, 0.145, seg=20, c=C_ROBOT, mat=MAT["robot"])
add_sphere("ElbowCap", 0.165, J1, c=C_ROBOT, mat=MAT["robotJnt"], sub=2)
add_cyl("ElbowAxle", 0.15, 0.36, J1, rot=(math.radians(90), 0, math.radians(-16)),
        seg=20, c=C_ROBOT, mat=MAT["robotJnt"])
add_link("Forearm", J1, J2, 0.105, seg=18, c=C_ROBOT, mat=MAT["robot"])
add_sphere("WristJoint", 0.11, J2, c=C_ROBOT, mat=MAT["robotJnt"], sub=2)
add_link("Wrist", J2, J3, 0.075, seg=16, c=C_ROBOT, mat=MAT["robot"])

# end effector: inspection camera with its own ring light
tool_dir = (J3 - J2).normalized()
tool_rot = tool_dir.to_track_quat('Z', 'Y').to_euler()
add_cyl("ToolFlange", 0.095, 0.05, J3, rot=tool_rot, seg=18, c=C_ROBOT, mat=MAT["robotJnt"])
tip = J3 + tool_dir * 0.16
add_box("ToolCamera", (0.13, 0.13, 0.20), J3 + tool_dir * 0.12,
        rot=tool_rot, c=C_ROBOT, mat=MAT["sensor"], bevel=0.012)
add_cyl("ToolLens", 0.05, 0.06, tip + tool_dir * 0.06, rot=tool_rot, seg=18,
        c=C_ROBOT, mat=MAT["lens"])
add_cyl("ToolRing", 0.095, 0.03, tip + tool_dir * 0.09, rot=tool_rot, seg=24,
        c=C_ROBOT, mat=MAT["led"])

# dress pack looping along the arm
add_link("DressPackA", J0 + Vector((-0.14, -0.05, 0.05)), J1 + Vector((-0.16, 0.06, -0.02)),
         0.028, seg=10, c=C_ROBOT, mat=MAT["cable"])
add_link("DressPackB", J1 + Vector((-0.16, 0.06, -0.02)), J2 + Vector((-0.12, 0.05, 0.06)),
         0.028, seg=10, c=C_ROBOT, mat=MAT["cable"])
add_link("DressPackC", RB + Vector((-0.2, 0.28, 0.72)), J0 + Vector((-0.14, -0.05, 0.02)),
         0.03, seg=10, c=C_ROBOT, mat=MAT["cable"])

# ---------------------------------------------------------------- control cabinet
CAB = Vector((2.6, 2.45, 0.0))
add_box("Cabinet", (1.1, 0.55, 1.85), CAB + Vector((0, 0, 0.93)),
        c=C_ROBOT, mat=MAT["cabinet"], bevel=0.02)
add_box("CabinetDoor", (1.02, 0.03, 1.6), CAB + Vector((0, -0.29, 0.95)),
        c=C_ROBOT, mat=MAT["paint"])
add_box("HMIScreen", (0.42, 0.03, 0.30), CAB + Vector((-0.2, -0.32, 1.32)),
        c=C_ROBOT, mat=MAT["screen"])
add_cyl("EStop", 0.055, 0.05, CAB + Vector((0.34, -0.31, 1.32)),
        rot=(math.radians(90), 0, 0), seg=16, c=C_ROBOT, mat=MAT["laser"])
for i in range(3):
    add_cyl("StatusLamp", 0.03, 0.04, CAB + Vector((0.34, -0.31, 1.10 - i * 0.11)),
            rot=(math.radians(90), 0, 0), seg=12, c=C_ROBOT, mat=MAT["beacon"])
add_cyl("BeaconPost", 0.035, 0.22, CAB + Vector((0, 0, 1.96)), seg=12,
        c=C_ROBOT, mat=MAT["sensor"])
add_cyl("Beacon", 0.11, 0.16, CAB + Vector((0, 0, 2.15)), seg=20,
        c=C_ROBOT, mat=MAT["beacon"])
add_sphere("BeaconCap", 0.11, CAB + Vector((0, 0, 2.23)), c=C_ROBOT, mat=MAT["beacon"], sub=2)
add_box("CabinetFan", (0.24, 0.02, 0.24), CAB + Vector((0.32, 0.28, 1.5)),
        c=C_ROBOT, mat=MAT["frame"])

# ---------------------------------------------------------------- fencing
FENCE_H = 2.1

def fence_panel(mid, length, angle, c, height=FENCE_H):
    """Framed wire-mesh panel standing in the plane rotated by `angle` about Z."""
    cx, cy = mid
    rot = (math.radians(90), 0.0, angle)
    grid = bmesh.new()
    bmesh.ops.create_grid(grid, x_segments=max(4, int(length * 5)),
                          y_segments=max(4, int(height * 5)), size=1.0)
    bmesh.ops.scale(grid, vec=((length - 0.12) * 0.5, (height - 0.16) * 0.5, 1.0),
                    verts=grid.verts)
    ob = _finish("MeshPanel", grid, c, MAT["mesh"], (cx, cy, height * 0.5 + 0.06), rot)
    wf = ob.modifiers.new("Wire", 'WIREFRAME')
    wf.thickness = 0.016
    wf.use_replace = True
    wf.use_even_offset = False

    ax, ay = math.cos(angle), math.sin(angle)
    for z in (0.10, height * 0.5 + 0.06, height + 0.02):
        add_link("PanelRail", (cx - ax * length * 0.5, cy - ay * length * 0.5, z),
                 (cx + ax * length * 0.5, cy + ay * length * 0.5, z),
                 0.026, seg=10, c=c, mat=MAT["fence"])
    for s in (-1, 1):
        add_box("PanelStile", (0.05, 0.05, height),
                (cx + ax * s * length * 0.5, cy + ay * s * length * 0.5, height * 0.5 + 0.02),
                rot=(0, 0, angle), c=c, mat=MAT["fence"])
    return ob

def fence_post(p, height=FENCE_H + 0.14):
    add_box("FencePost", (0.11, 0.11, height), (p[0], p[1], height * 0.5),
            c=C_FENCE, mat=MAT["fence"], bevel=0.008)
    add_box("PostBasePlate", (0.24, 0.24, 0.03), (p[0], p[1], 0.015),
            c=C_FENCE, mat=MAT["frame"])
    add_cyl("PostCap", 0.06, 0.03, (p[0], p[1], height + 0.02), seg=10,
            c=C_FENCE, mat=MAT["frame"])

def fence_run(a, b, n):
    a, b = Vector(a), Vector(b)
    d = b - a
    ang = math.atan2(d.y, d.x)
    seg_len = d.length / n
    for i in range(n):
        mid = a + d * ((i + 0.5) / n)
        fence_panel((mid.x, mid.y), seg_len, ang, C_FENCE)
    for i in range(n + 1):
        p = a + d * (i / n)
        fence_post((p.x, p.y))

# long rear side, continuous
fence_run((-CELL_X, CELL_Y), (CELL_X, CELL_Y), 6)
# front side, split around the personnel gate
fence_run((-CELL_X, -CELL_Y), (-1.35, -CELL_Y), 3)
fence_run((1.35, -CELL_Y), (CELL_X, -CELL_Y), 3)
# end walls, split around the conveyor throat
for sx in (-1, 1):
    fence_run((sx * CELL_X, -CELL_Y), (sx * CELL_X, -1.0), 1)
    fence_run((sx * CELL_X, 1.0), (sx * CELL_X, CELL_Y), 1)

# gate leaves swung open
for s, ang in ((-1, math.radians(-52)), (1, math.radians(180 + 52))):
    hinge = Vector((s * 1.35, -CELL_Y, 0.0))
    leaf = 1.25
    mid = hinge + Vector((math.cos(ang), math.sin(ang), 0)) * (leaf * 0.5)
    fence_panel((mid.x, mid.y), leaf, ang, C_FENCE, height=1.95)
    add_cyl("GateHinge", 0.045, 1.95, (hinge.x, hinge.y, 1.0), seg=12,
            c=C_FENCE, mat=MAT["fence"])
add_box("GateSwitch", (0.09, 0.09, 0.26), (1.35, -CELL_Y + 0.14, 1.15),
        c=C_FENCE, mat=MAT["sensor"])
add_box("GateSwitchLed", (0.03, 0.03, 0.06), (1.29, -CELL_Y + 0.14, 1.24),
        c=C_FENCE, mat=MAT["led"])

# conveyor throat hoods with rubber curtains
for sx in (-1, 1):
    hx = sx * CELL_X
    add_box("ThroatHood", (0.22, 2.1, 0.5), (hx, 0, FENCE_H - 0.15),
            c=C_FENCE, mat=MAT["fence"], bevel=0.01)
    for sy in (-1, 1):
        add_box("ThroatJamb", (0.16, 0.12, FENCE_H - 0.4), (hx, sy * 1.0, (FENCE_H - 0.4) * 0.5),
                c=C_FENCE, mat=MAT["fence"])
    for i in range(9):
        add_box("Curtain", (0.02, 0.19, 0.62),
                (hx, -0.85 + i * 0.21, DECK_Z + 0.50), c=C_FENCE, mat=MAT["rubber"])

# warning signage on the front fence
add_box("SignPlate", (0.5, 0.02, 0.36), (-3.6, -CELL_Y - 0.06, 1.5),
        c=C_FENCE, mat=MAT["stripe"])
add_box("SignGlyph", (0.16, 0.01, 0.16), (-3.6, -CELL_Y - 0.08, 1.5),
        rot=(0, math.radians(45), 0), c=C_FENCE, mat=MAT["sensor"])

# ---------------------------------------------------------------- work-in-process
parts = [
    (-5.2, "box"), (-2.0, "cyl"), (1.4, "box"), (4.6, "cyl"),
]
for i, (px, kind) in enumerate(parts):
    m = MAT["partA"] if i % 2 == 0 else MAT["partB"]
    if kind == "box":
        add_box("PartHousing", (0.42, 0.36, 0.2), (px, 0.02, DECK_Z + 0.10),
                rot=(0, 0, math.radians(6 * (1 if i % 2 else -1))),
                c=C_PROPS, mat=m, bevel=0.015)
        add_box("PartBoss", (0.14, 0.14, 0.07), (px, 0.02, DECK_Z + 0.235),
                c=C_PROPS, mat=MAT["frame"])
    else:
        add_cyl("PartFlange", 0.19, 0.16, (px, 0.0, DECK_Z + 0.08), seg=24,
                c=C_PROPS, mat=m)
        add_cyl("PartBore", 0.075, 0.18, (px, 0.0, DECK_Z + 0.09), seg=18,
                c=C_PROPS, mat=MAT["sensor"])

# reject chute and bin beside the last arch
add_box("RejectChute", (0.7, 0.9, 0.05), (4.9, -1.05, DECK_Z - 0.12),
        rot=(math.radians(-22), 0, 0), c=C_PROPS, mat=MAT["frame"])
for sx in (-1, 1):
    add_box("ChuteWall", (0.04, 0.9, 0.18), (4.9 + sx * 0.35, -1.05, DECK_Z - 0.05),
            rot=(math.radians(-22), 0, 0), c=C_PROPS, mat=MAT["frame"])
add_box("RejectBin", (0.8, 0.8, 0.6), (4.9, -1.75, 0.30),
        c=C_PROPS, mat=MAT["partB"], bevel=0.02)
add_box("BinLip", (0.86, 0.86, 0.05), (4.9, -1.75, 0.62), c=C_PROPS, mat=MAT["frame"])

# pallet of inspected parts in the corner
add_box("Pallet", (1.2, 1.0, 0.12), (-5.6, 2.3, 0.06), c=C_PROPS, mat=MAT["stripe"])
for i in range(2):
    for j in range(2):
        add_box("Tote", (0.5, 0.42, 0.3), (-5.9 + i * 0.6, 2.08 + j * 0.45, 0.27),
                c=C_PROPS, mat=MAT["partA"], bevel=0.015)

# ---------------------------------------------------------------- lighting
def add_light(name, ltype, loc, energy, color=(1, 1, 1), size=1.0, rot=(0, 0, 0), angle=None):
    ld = bpy.data.lights.new(name, ltype)
    ld.energy = energy
    ld.color = color
    if ltype == 'AREA':
        ld.shape = 'RECTANGLE'
        ld.size = size
        ld.size_y = size * 0.35
    if ltype == 'SUN' and angle is not None:
        ld.angle = angle
    ob = bpy.data.objects.new(name, ld)
    ob.location = loc
    ob.rotation_euler = rot
    C_STAGE.objects.link(ob)
    return ob

# ceiling luminaires over the cell
for i, lx in enumerate((-4.5, 0.0, 4.5)):
    add_light("BayLight%d" % i, 'AREA', (lx, 0.4, 6.2), 900,
              color=(1.0, 0.97, 0.92), size=3.2, rot=(0, 0, 0))
add_light("FillLight", 'AREA', (-8.5, -8.0, 4.6), 500, color=(0.85, 0.9, 1.0),
          size=6.0, rot=(math.radians(58), 0, math.radians(-42)))
add_light("RimLight", 'AREA', (9.5, 7.0, 4.0), 400, color=(0.8, 0.88, 1.0),
          size=5.0, rot=(math.radians(66), 0, math.radians(140)))
add_light("SunShaft", 'SUN', (0, 0, 9), 1.6, color=(1.0, 0.95, 0.88),
          rot=(math.radians(38), math.radians(12), math.radians(-58)), angle=0.08)

world = bpy.data.worlds.new("StationWorld")
world.use_nodes = True
bg = world.node_tree.nodes["Background"]
bg.inputs["Color"].default_value = (0.035, 0.04, 0.05, 1.0)
bg.inputs["Strength"].default_value = 0.6
bpy.context.scene.world = world

# ---------------------------------------------------------------- camera
cam_data = bpy.data.cameras.new("StationCam")
cam_data.lens = 32.0
cam_data.sensor_width = 36.0
cam_data.dof.use_dof = True
cam_data.dof.focus_distance = 13.0
cam_data.dof.aperture_fstop = 4.0
cam = bpy.data.objects.new("StationCam", cam_data)
cam.location = (10.8, -10.4, 5.4)
target = Vector((-0.4, 0.2, 1.35))
cam.rotation_euler = (target - Vector(cam.location)).to_track_quat('-Z', 'Y').to_euler()
C_STAGE.objects.link(cam)
bpy.context.scene.camera = cam

# output settings only (nothing is rendered or saved)
sc = bpy.context.scene
sc.render.resolution_x = 1920
sc.render.resolution_y = 1080
sc.frame_start = 1
sc.frame_end = 1

print("Robotic inspection station built: %d objects" % len(bpy.data.objects))
