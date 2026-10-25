"""
claude-131 - A compact recording studio control room.

Builds, from factory startup:
  * a shell room (floor, ceiling, four walls) with a window into the live room
  * acoustic treatment: fabric first-reflection panels, ceiling cloud,
    corner bass traps and a skyline diffuser on the rear wall
  * a mixing desk with an angled console (faders + knobs), rack gear,
    dual displays and a MIDI controller on a keyboard tray
  * a pair of ported nearfield monitors on the desk bridge
  * operator chair, boom mic stand with pop filter, rug
  * practical + area lighting and a framed camera

Scene construction only: nothing is rendered or saved.
"""

import math
import random

import bmesh
import bpy
from mathutils import Euler, Matrix, Vector

random.seed(7)

TAU = math.tau
D = math.radians


# ----------------------------------------------------------------------------
# scene bootstrap
# ----------------------------------------------------------------------------

def reset_scene():
    bpy.ops.wm.read_factory_settings(use_empty=True)
    scene = bpy.context.scene
    scene.unit_settings.system = 'METRIC'
    scene.unit_settings.length_unit = 'METERS'

    world = bpy.data.worlds.new("StudioWorld")
    world.use_nodes = True
    bg = world.node_tree.nodes["Background"]
    bg.inputs["Color"].default_value = (0.020, 0.021, 0.025, 1.0)
    bg.inputs["Strength"].default_value = 1.0
    scene.world = world
    return scene


# ----------------------------------------------------------------------------
# material helpers
# ----------------------------------------------------------------------------

def _set(node, key, value):
    if key in node.inputs:
        node.inputs[key].default_value = value


def make_material(name, base=(0.5, 0.5, 0.5), roughness=0.5, metallic=0.0,
                  emission=None, emission_strength=0.0, alpha=1.0,
                  transmission=0.0, ior=1.45, sheen=0.0):
    mat = bpy.data.materials.new(name)
    mat.use_nodes = True
    bsdf = mat.node_tree.nodes.get("Principled BSDF")
    _set(bsdf, "Base Color", (*base, 1.0))
    _set(bsdf, "Roughness", roughness)
    _set(bsdf, "Metallic", metallic)
    _set(bsdf, "IOR", ior)
    _set(bsdf, "Alpha", alpha)
    _set(bsdf, "Transmission Weight", transmission)
    _set(bsdf, "Sheen Weight", sheen)
    if emission is not None:
        _set(bsdf, "Emission Color", (*emission, 1.0))
        _set(bsdf, "Emission Strength", emission_strength)
    if alpha < 1.0 or transmission > 0.0:
        mat.blend_method = 'BLEND'
    return mat


MATS = {}


def build_materials():
    M = MATS
    M['floor'] = make_material("WoodFloor", (0.146, 0.086, 0.048), 0.42)
    M['wall'] = make_material("WallPaint", (0.128, 0.130, 0.138), 0.86)
    M['ceiling'] = make_material("Ceiling", (0.180, 0.182, 0.188), 0.92)
    M['fabric_dark'] = make_material("PanelFabricCharcoal", (0.052, 0.055, 0.062),
                                     0.95, sheen=0.35)
    M['fabric_accent'] = make_material("PanelFabricRust", (0.212, 0.072, 0.038),
                                       0.94, sheen=0.4)
    M['frame_wood'] = make_material("PanelFrame", (0.238, 0.152, 0.088), 0.55)
    M['diffuser'] = make_material("DiffuserPine", (0.316, 0.222, 0.128), 0.62)
    M['desk'] = make_material("DeskWalnut", (0.086, 0.052, 0.033), 0.36)
    M['desk_top'] = make_material("DeskSurface", (0.128, 0.082, 0.052), 0.28)
    M['metal'] = make_material("BrushedMetal", (0.62, 0.63, 0.65), 0.32, 1.0)
    M['dark_metal'] = make_material("DarkMetal", (0.070, 0.072, 0.078), 0.38, 1.0)
    M['plastic_black'] = make_material("BlackPlastic", (0.026, 0.027, 0.030), 0.44)
    M['plastic_grey'] = make_material("GreyPlastic", (0.155, 0.158, 0.165), 0.52)
    M['cabinet'] = make_material("SpeakerCabinet", (0.030, 0.031, 0.034), 0.36)
    M['baffle'] = make_material("SpeakerBaffle", (0.055, 0.056, 0.060), 0.55)
    M['cone'] = make_material("DriverCone", (0.118, 0.120, 0.126), 0.68)
    M['dome'] = make_material("TweeterDome", (0.72, 0.70, 0.66), 0.22, 1.0)
    M['screen'] = make_material("ScreenGlow", (0.02, 0.02, 0.02), 0.20,
                                emission=(0.240, 0.330, 0.470),
                                emission_strength=4.5)
    M['led_green'] = make_material("LEDGreen", (0.02, 0.05, 0.02), 0.3,
                                   emission=(0.15, 1.0, 0.28),
                                   emission_strength=12.0)
    M['led_amber'] = make_material("LEDAmber", (0.05, 0.03, 0.01), 0.3,
                                   emission=(1.0, 0.55, 0.10),
                                   emission_strength=10.0)
    M['led_strip'] = make_material("LEDStrip", (0.02, 0.02, 0.02), 0.4,
                                   emission=(1.0, 0.72, 0.42),
                                   emission_strength=6.0)
    M['fader_cap'] = make_material("FaderCap", (0.085, 0.088, 0.094), 0.60)
    M['knob'] = make_material("Knob", (0.055, 0.057, 0.062), 0.48)
    M['chair'] = make_material("ChairFabric", (0.052, 0.058, 0.070), 0.90, sheen=0.3)
    M['rug'] = make_material("Rug", (0.098, 0.086, 0.078), 0.95, sheen=0.25)
    M['glass'] = make_material("WindowGlass", (0.86, 0.90, 0.92), 0.03, 0.0,
                               alpha=0.18, transmission=0.92, ior=1.5)
    M['live_room'] = make_material("LiveRoomBackdrop", (0.045, 0.042, 0.040), 0.85)
    M['mic'] = make_material("MicBody", (0.140, 0.142, 0.150), 0.30, 1.0)
    M['mesh'] = make_material("PopMesh", (0.030, 0.030, 0.032), 0.70)
    return M


# ----------------------------------------------------------------------------
# primitive helpers
# ----------------------------------------------------------------------------

def _finish(name, bm, loc, rot, mat, parent):
    me = bpy.data.meshes.new(name)
    bm.to_mesh(me)
    bm.free()
    me.validate()
    obj = bpy.data.objects.new(name, me)
    bpy.context.collection.objects.link(obj)
    obj.location = loc
    obj.rotation_euler = Euler(rot, 'XYZ')
    if mat is not None:
        obj.data.materials.append(mat)
    if parent is not None:
        obj.parent = parent  # parent inverse stays identity -> pure local coords
    return obj


def box(name, size, loc=(0, 0, 0), rot=(0, 0, 0), mat=None, parent=None,
        bevel=0.0):
    bm = bmesh.new()
    bmesh.ops.create_cube(bm, size=1.0)
    bmesh.ops.scale(bm, vec=Vector(size), verts=bm.verts)
    if bevel > 0.0:
        bmesh.ops.bevel(bm, geom=bm.verts[:] + bm.edges[:] + bm.faces[:],
                        offset=bevel, segments=2, profile=0.5,
                        affect='EDGES', clamp_overlap=True)
    return _finish(name, bm, loc, rot, mat, parent)


def cylinder(name, radius, depth, loc=(0, 0, 0), rot=(0, 0, 0), mat=None,
             parent=None, segments=28, radius_top=None, caps=True):
    r_top = radius if radius_top is None else radius_top
    bm = bmesh.new()
    bmesh.ops.create_cone(bm, cap_ends=caps, cap_tris=False, segments=segments,
                          radius1=radius, radius2=r_top, depth=depth)
    return _finish(name, bm, loc, rot, mat, parent)


def sphere(name, radius, loc=(0, 0, 0), rot=(0, 0, 0), mat=None, parent=None,
           segments=24, rings=12):
    bm = bmesh.new()
    bmesh.ops.create_uvsphere(bm, u_segments=segments, v_segments=rings,
                              radius=radius)
    return _finish(name, bm, loc, rot, mat, parent)


def plane(name, size, loc=(0, 0, 0), rot=(0, 0, 0), mat=None, parent=None):
    bm = bmesh.new()
    bmesh.ops.create_grid(bm, x_segments=1, y_segments=1, size=0.5)
    bmesh.ops.scale(bm, vec=Vector((size[0], size[1], 1.0)), verts=bm.verts)
    return _finish(name, bm, loc, rot, mat, parent)


def empty(name, loc=(0, 0, 0), rot=(0, 0, 0), parent=None):
    obj = bpy.data.objects.new(name, None)
    obj.empty_display_size = 0.15
    bpy.context.collection.objects.link(obj)
    obj.location = loc
    obj.rotation_euler = Euler(rot, 'XYZ')
    if parent is not None:
        obj.parent = parent
    return obj


def shade_smooth(obj, angle=D(35)):
    for poly in obj.data.polygons:
        poly.use_smooth = True
    mod = obj.modifiers.new("EdgeSplit", 'EDGE_SPLIT')
    mod.split_angle = angle
    mod.use_edge_angle = True
    mod.use_edge_sharp = False
    return obj


# ----------------------------------------------------------------------------
# room shell
# ----------------------------------------------------------------------------

RX, RY, RZ = 3.0, 2.25, 2.80        # interior half-width, half-depth, height
WT = 0.15                            # wall thickness


def build_room():
    M = MATS
    root = empty("Room")

    box("Floor", (2 * RX + 2 * WT, 2 * RY + 2 * WT, WT),
        loc=(0, 0, -WT / 2), mat=M['floor'], parent=root)
    box("Ceiling", (2 * RX + 2 * WT, 2 * RY + 2 * WT, WT),
        loc=(0, 0, RZ + WT / 2), mat=M['ceiling'], parent=root)

    # left / right / rear walls
    box("WallLeft", (WT, 2 * RY, RZ), loc=(-RX - WT / 2, 0, RZ / 2),
        mat=M['wall'], parent=root)
    box("WallRight", (WT, 2 * RY, RZ), loc=(RX + WT / 2, 0, RZ / 2),
        mat=M['wall'], parent=root)
    box("WallRear", (2 * RX + 2 * WT, WT, RZ), loc=(0, -RY - WT / 2, RZ / 2),
        mat=M['wall'], parent=root)

    # front wall built around a control-room window
    ow, oz0, oz1 = 1.15, 1.05, 1.98       # opening half width / bottom / top
    fy = RY + WT / 2
    box("WallFrontLeft", (RX - ow, WT, RZ),
        loc=(-(ow + (RX - ow) / 2), fy, RZ / 2), mat=M['wall'], parent=root)
    box("WallFrontRight", (RX - ow, WT, RZ),
        loc=(ow + (RX - ow) / 2, fy, RZ / 2), mat=M['wall'], parent=root)
    box("WallFrontSill", (2 * ow, WT, oz0),
        loc=(0, fy, oz0 / 2), mat=M['wall'], parent=root)
    box("WallFrontHead", (2 * ow, WT, RZ - oz1),
        loc=(0, fy, oz1 + (RZ - oz1) / 2), mat=M['wall'], parent=root)

    # window reveal frame + slightly splayed double glazing
    frame = M['dark_metal']
    box("WinFrameBottom", (2 * ow + 0.08, WT + 0.02, 0.05),
        loc=(0, fy, oz0 + 0.02), mat=frame, parent=root)
    box("WinFrameTop", (2 * ow + 0.08, WT + 0.02, 0.05),
        loc=(0, fy, oz1 - 0.02), mat=frame, parent=root)
    box("WinFrameL", (0.06, WT + 0.02, oz1 - oz0),
        loc=(-ow, fy, (oz0 + oz1) / 2), mat=frame, parent=root)
    box("WinFrameR", (0.06, WT + 0.02, oz1 - oz0),
        loc=(ow, fy, (oz0 + oz1) / 2), mat=frame, parent=root)

    box("GlassInner", (2 * ow - 0.06, 0.014, oz1 - oz0 - 0.06),
        loc=(0, RY + 0.03, (oz0 + oz1) / 2), rot=(D(2.5), 0, 0),
        mat=M['glass'], parent=root)
    box("GlassOuter", (2 * ow - 0.06, 0.014, oz1 - oz0 - 0.06),
        loc=(0, RY + 0.12, (oz0 + oz1) / 2), rot=(D(-2.5), 0, 0),
        mat=M['glass'], parent=root)

    # suggestion of the live room beyond the glass
    box("LiveRoomBackdrop", (3.4, 0.10, 1.6),
        loc=(0, RY + 1.25, 1.45), mat=M['live_room'], parent=root)
    box("LiveRoomFloor", (3.4, 1.4, 0.05),
        loc=(0, RY + 0.75, 0.02), mat=M['live_room'], parent=root)
    cylinder("LiveRoomStand", 0.03, 1.3, loc=(0.9, RY + 0.6, 0.68),
             mat=M['dark_metal'], parent=root, segments=12)

    # skirting
    for x, y, sx, sy in ((0, -RY + 0.01, 2 * RX, 0.02),
                         (-RX + 0.01, 0, 0.02, 2 * RY),
                         (RX - 0.01, 0, 0.02, 2 * RY)):
        box("Skirting", (sx, sy, 0.09), loc=(x, y, 0.045),
            mat=M['frame_wood'], parent=root)

    return root


# ----------------------------------------------------------------------------
# acoustic treatment
# ----------------------------------------------------------------------------

def acoustic_panel(name, w, h, thickness=0.09, loc=(0, 0, 0), rot=(0, 0, 0),
                   parent=None, fabric=None):
    """Fabric wrapped absorber with a slim wooden frame (local +Z is face-out)."""
    fab = fabric or MATS['fabric_dark']
    piv = empty(name, loc=loc, rot=rot, parent=parent)
    box(name + "_Core", (w, h, thickness), loc=(0, 0, 0), mat=fab,
        parent=piv, bevel=0.012)
    fr = 0.03
    box(name + "_FrameT", (w + fr, fr, thickness * 0.96),
        loc=(0, h / 2 + fr / 2 - 0.004, 0), mat=MATS['frame_wood'], parent=piv)
    box(name + "_FrameB", (w + fr, fr, thickness * 0.96),
        loc=(0, -h / 2 - fr / 2 + 0.004, 0), mat=MATS['frame_wood'], parent=piv)
    box(name + "_FrameL", (fr, h, thickness * 0.96),
        loc=(-w / 2 - fr / 2 + 0.004, 0, 0), mat=MATS['frame_wood'], parent=piv)
    box(name + "_FrameR", (fr, h, thickness * 0.96),
        loc=(w / 2 + fr / 2 - 0.004, 0, 0), mat=MATS['frame_wood'], parent=piv)
    return piv


def build_treatment():
    M = MATS
    root = empty("AcousticTreatment")

    # ---- side wall first-reflection panels (panel plane is local XY) ----
    side_y = (-0.55, 0.55, 1.65)
    for sx, sign in ((-1, 1), (1, -1)):
        for i, y in enumerate(side_y):
            fab = M['fabric_accent'] if i == 1 else M['fabric_dark']
            acoustic_panel("SidePanel_%s%d" % ("L" if sx < 0 else "R", i),
                           0.95, 1.35, 0.10,
                           loc=(sx * (RX - 0.05), y, 1.45),
                           rot=(D(90), 0, sign * D(90)),
                           parent=root, fabric=fab)

    # ---- front wall panels either side of the window ----
    for sx in (-1, 1):
        acoustic_panel("FrontPanel_%s" % ("L" if sx < 0 else "R"),
                       0.75, 1.9, 0.10,
                       loc=(sx * 2.05, RY - 0.05, 1.30),
                       rot=(D(90), 0, D(180)), parent=root,
                       fabric=M['fabric_dark'])
    acoustic_panel("FrontPanel_Head", 2.2, 0.55, 0.10,
                   loc=(0, RY - 0.05, 2.42), rot=(D(90), 0, D(180)),
                   parent=root, fabric=M['fabric_dark'])

    # ---- ceiling cloud (two tilted panels above the desk) ----
    for i, y in enumerate((0.35, 1.45)):
        cloud = acoustic_panel("Cloud_%d" % i, 1.9, 0.85, 0.11,
                               loc=(0, y, 2.50 - i * 0.03),
                               rot=(D(6) if i else D(-6), 0, 0),
                               parent=root, fabric=M['fabric_dark'])
        # suspension wires
        for sx in (-1, 1):
            for sy in (-1, 1):
                cylinder("CloudWire", 0.004, 0.30,
                         loc=(sx * 0.85, sy * 0.36, 0.16), mat=M['metal'],
                         parent=cloud, segments=6)

    # ---- corner bass traps ----
    for sx in (-1, 1):
        for sy in (-1, 1):
            trap = cylinder("BassTrap", 0.32, RZ - 0.06,
                            loc=(sx * (RX - 0.22), sy * (RY - 0.22),
                                 (RZ - 0.06) / 2),
                            mat=M['fabric_dark'], parent=root, segments=24)
            shade_smooth(trap)
            cylinder("BassTrapCapT", 0.335, 0.03,
                     loc=(sx * (RX - 0.22), sy * (RY - 0.22), RZ - 0.05),
                     mat=M['frame_wood'], parent=root, segments=24)
            cylinder("BassTrapCapB", 0.335, 0.03,
                     loc=(sx * (RX - 0.22), sy * (RY - 0.22), 0.02),
                     mat=M['frame_wood'], parent=root, segments=24)

    # ---- rear wall skyline diffuser ----
    diff = empty("Diffuser", loc=(0, -RY + 0.02, 1.55), parent=root)
    cols, rows, cell = 14, 8, 0.145
    box("DiffuserBacker", (cols * cell + 0.06, rows * cell + 0.06, 0.03),
        loc=(0, 0, 0.015), rot=(D(90), 0, 0), mat=M['frame_wood'], parent=diff)
    for i in range(cols):
        for j in range(rows):
            depth = 0.03 + random.random() ** 1.3 * 0.20
            x = (i - (cols - 1) / 2.0) * cell
            z = (j - (rows - 1) / 2.0) * cell
            box("DiffuserWell", (cell * 0.9, cell * 0.9, depth),
                loc=(x, z, 0.03 + depth / 2),
                rot=(D(90), 0, 0), mat=M['diffuser'], parent=diff)

    return root


# ----------------------------------------------------------------------------
# mixing desk + console surface
# ----------------------------------------------------------------------------

def build_console(parent):
    """Angled control surface: channel strips of faders, knobs and buttons."""
    M = MATS
    piv = empty("Console", loc=(0, 0.02, 0.80), rot=(D(-14), 0, 0), parent=parent)

    body = box("ConsoleBody", (1.42, 0.52, 0.075), loc=(0, 0, 0.035),
               mat=M['plastic_grey'], parent=piv, bevel=0.008)
    box("ConsoleFace", (1.38, 0.48, 0.012), loc=(0, 0, 0.078),
        mat=M['plastic_black'], parent=piv)

    n = 12
    span = 1.22
    for i in range(n):
        x = -span / 2 + span * i / (n - 1)
        # fader slot + cap
        box("FaderSlot", (0.014, 0.16, 0.004), loc=(x, -0.115, 0.086),
            mat=M['plastic_black'], parent=piv)
        travel = -0.115 + (random.random() - 0.35) * 0.09
        box("FaderCap", (0.026, 0.036, 0.020), loc=(x, travel, 0.096),
            mat=M['fader_cap'], parent=piv, bevel=0.004)
        # knob column
        for k in range(3):
            y = 0.045 + k * 0.072
            kn = cylinder("Knob", 0.017, 0.024, loc=(x, y, 0.094),
                          mat=M['knob'], parent=piv, segments=16)
            shade_smooth(kn)
            box("KnobPointer", (0.004, 0.016, 0.004),
                loc=(x, y + 0.006, 0.107), rot=(0, 0, D(random.uniform(-50, 50))),
                mat=M['plastic_grey'], parent=piv)
        # channel buttons with status LEDs
        for b in range(2):
            box("ChanButton", (0.026, 0.020, 0.010),
                loc=(x, -0.02 + b * 0.028, 0.089),
                mat=M['plastic_black'], parent=piv)
        if i % 3 == 0:
            box("ChanLED", (0.010, 0.006, 0.004), loc=(x, -0.212, 0.088),
                mat=M['led_green'], parent=piv)
        else:
            box("ChanLED", (0.010, 0.006, 0.004), loc=(x, -0.212, 0.088),
                mat=M['led_amber'], parent=piv)

    # transport / master section on the right cheek
    box("MasterPad", (0.16, 0.20, 0.010), loc=(0.60, -0.12, 0.089),
        mat=M['plastic_grey'], parent=piv)
    jog = cylinder("JogWheel", 0.055, 0.020, loc=(0.60, -0.14, 0.098),
                   mat=M['dark_metal'], parent=piv, segments=24)
    shade_smooth(jog)
    box("MeterBridge", (0.34, 0.05, 0.012), loc=(-0.52, 0.20, 0.090),
        mat=M['led_green'], parent=piv)
    return piv


def build_desk():
    M = MATS
    root = empty("MixDesk", loc=(0, 1.32, 0))

    top_z = 0.735
    box("DeskTop", (2.60, 0.88, 0.05), loc=(0, 0, top_z),
        mat=M['desk_top'], parent=root, bevel=0.008)
    box("DeskEdge", (2.62, 0.03, 0.055), loc=(0, -0.445, top_z),
        mat=M['desk'], parent=root)

    # pedestals
    for sx in (-1, 1):
        box("DeskPedestal", (0.46, 0.82, top_z - 0.06),
            loc=(sx * 1.02, 0.01, (top_z - 0.06) / 2 + 0.03),
            mat=M['desk'], parent=root)
        box("PedestalPlinth", (0.44, 0.78, 0.03), loc=(sx * 1.02, 0.01, 0.015),
            mat=M['dark_metal'], parent=root)

    # rack gear in the right pedestal (front faces -Y)
    for u in range(4):
        z = 0.16 + u * 0.135
        box("RackUnit", (0.42, 0.42, 0.115), loc=(1.02, 0.10, z),
            mat=M['plastic_black'], parent=root)
        box("RackFace", (0.43, 0.012, 0.120), loc=(1.02, -0.115, z),
            mat=M['dark_metal'], parent=root, bevel=0.004)
        for i in range(4):
            kn = cylinder("RackKnob", 0.014, 0.018,
                          loc=(0.88 + i * 0.075, -0.128, z),
                          rot=(D(90), 0, 0), mat=M['knob'], parent=root,
                          segments=14)
            shade_smooth(kn)
        box("RackLED", (0.012, 0.006, 0.006), loc=(1.20, -0.126, z + 0.035),
            mat=M['led_green'] if u % 2 else M['led_amber'], parent=root)
        box("RackDisplay", (0.11, 0.006, 0.030), loc=(0.71, -0.126, z),
            mat=M['led_amber'], parent=root)

    # left pedestal: drawers
    for d in range(3):
        z = 0.18 + d * 0.19
        box("Drawer", (0.40, 0.014, 0.165), loc=(-1.02, -0.395, z),
            mat=M['desk_top'], parent=root, bevel=0.005)
        cylinder("DrawerPull", 0.008, 0.16, loc=(-1.02, -0.408, z),
                 rot=(0, D(90), 0), mat=M['metal'], parent=root, segments=10)

    # rear bridge carrying the monitors
    bz = 1.02
    for sx in (-1, 1):
        box("BridgeLeg", (0.05, 0.34, bz - top_z - 0.025),
            loc=(sx * 1.24, 0.24, top_z + 0.025 + (bz - top_z - 0.025) / 2),
            mat=M['desk'], parent=root)
    box("BridgeTop", (2.58, 0.38, 0.05), loc=(0, 0.24, bz),
        mat=M['desk_top'], parent=root, bevel=0.008)
    box("BridgeUnderGlow", (2.30, 0.05, 0.012), loc=(0, 0.07, bz - 0.033),
        mat=M['led_strip'], parent=root)

    # pull-out keyboard tray
    box("KeyTray", (1.30, 0.36, 0.025), loc=(0, -0.36, 0.615),
        mat=M['desk_top'], parent=root, bevel=0.005)
    for sx in (-1, 1):
        box("TraySlide", (0.03, 0.42, 0.02), loc=(sx * 0.66, -0.20, 0.615),
            mat=M['metal'], parent=root)

    build_console(root)
    build_midi_controller(root)
    build_displays(root, top_z)
    build_desk_props(root, top_z)
    return root


def build_midi_controller(parent):
    M = MATS
    piv = empty("MidiController", loc=(0, -0.36, 0.630), rot=(0, 0, 0),
                parent=parent)
    box("MidiBody", (1.02, 0.28, 0.045), loc=(0, 0, 0.022),
        mat=M['plastic_black'], parent=piv, bevel=0.006)
    # 49 keys: white naturals with black sharps sitting on top
    n_white = 29
    kw = 0.0295
    start = -n_white * kw / 2 + kw / 2
    pattern = [0, 1, 0, 1, 0, 0, 1, 0, 1, 0, 1, 0]   # sharp follows this natural
    for i in range(n_white):
        x = start + i * kw
        box("WhiteKey", (kw * 0.88, 0.145, 0.014),
            loc=(x, -0.055, 0.050), mat=M['baffle'], parent=piv)
        if pattern[i % 12] and i < n_white - 1:
            box("BlackKey", (kw * 0.55, 0.092, 0.016),
                loc=(x + kw / 2, -0.030, 0.063), mat=M['plastic_black'],
                parent=piv)
    for i in range(8):
        kn = cylinder("MidiKnob", 0.011, 0.014,
                      loc=(-0.40 + i * 0.058, 0.095, 0.052),
                      mat=M['knob'], parent=piv, segments=12)
        shade_smooth(kn)
    for w in range(2):
        wh = cylinder("PitchWheel", 0.024, 0.014,
                      loc=(-0.455 + w * 0.055, 0.045, 0.050),
                      rot=(0, D(90), 0), mat=M['plastic_grey'], parent=piv,
                      segments=16)
        shade_smooth(wh)
    return piv


def build_displays(parent, top_z):
    M = MATS
    for sx, tilt in ((-1, D(9)), (1, D(-9))):
        piv = empty("Display_%s" % ("L" if sx < 0 else "R"),
                    loc=(sx * 0.40, 0.28, top_z + 0.025), rot=(0, 0, tilt),
                    parent=parent)
        cylinder("MonBase", 0.10, 0.018, loc=(0, 0, 0.009),
                 mat=M['dark_metal'], parent=piv, segments=24)
        box("MonStem", (0.05, 0.03, 0.20), loc=(0, 0.01, 0.11),
            mat=M['dark_metal'], parent=piv)
        head = empty("MonHead", loc=(0, 0.01, 0.21), rot=(D(-8), 0, 0),
                     parent=piv)
        box("MonShell", (0.63, 0.028, 0.38), loc=(0, 0.012, 0.19),
            mat=M['plastic_black'], parent=head, bevel=0.006)
        box("MonPanel", (0.605, 0.006, 0.352), loc=(0, -0.006, 0.195),
            mat=M['screen'], parent=head)


def build_desk_props(parent, top_z):
    M = MATS
    # headphones resting on a hook under the bridge
    hp = empty("Headphones", loc=(-0.95, 0.20, 0.86), rot=(D(90), 0, D(20)),
               parent=parent)
    band = cylinder("HPBand", 0.085, 0.022, loc=(0, 0, 0), rot=(0, D(90), 0),
                    mat=M['plastic_black'], parent=hp, segments=20)
    shade_smooth(band)
    for sx in (-1, 1):
        cup = cylinder("HPCup", 0.045, 0.032, loc=(sx * 0.075, -0.055, 0),
                       rot=(0, D(90), 0), mat=M['plastic_black'], parent=hp,
                       segments=20)
        shade_smooth(cup)

    # coffee mug
    mug = cylinder("Mug", 0.042, 0.10, loc=(-1.02, -0.20, top_z + 0.075),
                   mat=M['baffle'], parent=parent, segments=24)
    shade_smooth(mug)
    cylinder("MugHandle", 0.028, 0.010, loc=(-1.07, -0.20, top_z + 0.08),
             rot=(D(90), 0, 0), mat=M['baffle'], parent=parent, segments=16)

    # notepad and pen
    box("Notepad", (0.20, 0.26, 0.010), loc=(0.90, -0.25, top_z + 0.03),
        rot=(0, 0, D(-12)), mat=M['plastic_grey'], parent=parent)
    cylinder("Pen", 0.005, 0.14, loc=(0.90, -0.30, top_z + 0.04),
             rot=(0, D(90), D(-30)), mat=M['dark_metal'], parent=parent,
             segments=8)


# ----------------------------------------------------------------------------
# nearfield monitors
# ----------------------------------------------------------------------------

def build_monitor(name, loc, toe_in, parent=None):
    """Two-way ported nearfield; local -Y is the listening direction."""
    M = MATS
    piv = empty(name, loc=loc, rot=(0, 0, toe_in), parent=parent)

    # isolation pad + slight upward tilt
    box(name + "_Pad", (0.24, 0.30, 0.035), loc=(0, 0, 0.017),
        mat=M['fabric_dark'], parent=piv, bevel=0.006)
    body = empty(name + "_Body", loc=(0, 0, 0.035), rot=(D(-5), 0, 0),
                 parent=piv)

    w, d, h = 0.235, 0.29, 0.375
    box(name + "_Cabinet", (w, d, h), loc=(0, 0, h / 2), mat=M['cabinet'],
        parent=body, bevel=0.012)
    box(name + "_Baffle", (w - 0.012, 0.014, h - 0.012),
        loc=(0, -d / 2 - 0.004, h / 2), mat=M['baffle'], parent=body,
        bevel=0.006)

    fy = -d / 2 - 0.012
    # woofer: surround ring + cone + dust cap
    ring = cylinder(name + "_WooferRing", 0.078, 0.012, loc=(0, fy, 0.115),
                    rot=(D(90), 0, 0), mat=M['plastic_black'], parent=body,
                    segments=28)
    shade_smooth(ring)
    cone = cylinder(name + "_WooferCone", 0.068, 0.045, loc=(0, fy + 0.024, 0.115),
                    rot=(D(90), 0, 0), mat=M['cone'], parent=body,
                    segments=28, radius_top=0.018)
    shade_smooth(cone)
    cap = sphere(name + "_DustCap", 0.020, loc=(0, fy - 0.002, 0.115),
                 mat=M['dome'], parent=body, segments=18, rings=9)
    shade_smooth(cap)

    # tweeter waveguide + dome
    wg = cylinder(name + "_Waveguide", 0.052, 0.030, loc=(0, fy + 0.014, 0.285),
                  rot=(D(90), 0, 0), mat=M['plastic_black'], parent=body,
                  segments=28, radius_top=0.030)
    shade_smooth(wg)
    tw = sphere(name + "_Tweeter", 0.016, loc=(0, fy - 0.004, 0.285),
                mat=M['dome'], parent=body, segments=18, rings=9)
    shade_smooth(tw)

    # front port + power LED
    port = cylinder(name + "_Port", 0.030, 0.05, loc=(0, fy + 0.020, 0.205),
                    rot=(D(90), 0, 0), mat=M['plastic_black'], parent=body,
                    segments=20)
    shade_smooth(port)
    sphere(name + "_LED", 0.006, loc=(0.085, fy - 0.004, 0.035),
           mat=M['led_green'], parent=body, segments=10, rings=6)

    # rear amplifier plate and cable stub
    box(name + "_AmpPlate", (0.16, 0.012, 0.22), loc=(0, d / 2 + 0.004, 0.18),
        mat=M['dark_metal'], parent=body, bevel=0.004)
    for i in range(3):
        kn = cylinder(name + "_AmpKnob", 0.012, 0.016,
                      loc=(-0.045 + i * 0.045, d / 2 + 0.014, 0.24),
                      rot=(D(90), 0, 0), mat=M['knob'], parent=body,
                      segments=12)
        shade_smooth(kn)
    cylinder(name + "_Cable", 0.008, 0.16, loc=(0.0, d / 2 + 0.05, 0.06),
             rot=(D(70), 0, 0), mat=M['plastic_black'], parent=body,
             segments=10)
    return piv


# ----------------------------------------------------------------------------
# chair
# ----------------------------------------------------------------------------

def build_chair(loc=(0.0, 0.30, 0.0), yaw=D(4)):
    M = MATS
    piv = empty("Chair", loc=loc, rot=(0, 0, yaw))

    hub = cylinder("ChairHub", 0.055, 0.06, loc=(0, 0, 0.09),
                   mat=M['dark_metal'], parent=piv, segments=20)
    shade_smooth(hub)
    for i in range(5):
        a = TAU * i / 5.0
        leg = box("ChairLeg", (0.30, 0.045, 0.028),
                  loc=(math.cos(a) * 0.16, math.sin(a) * 0.16, 0.085),
                  rot=(0, D(-3), a), mat=M['dark_metal'], parent=piv,
                  bevel=0.008)
        caster = cylinder("Caster", 0.030, 0.020,
                          loc=(math.cos(a) * 0.30, math.sin(a) * 0.30, 0.030),
                          rot=(D(90), 0, a), mat=M['plastic_black'],
                          parent=piv, segments=16)
        shade_smooth(caster)

    col = cylinder("ChairColumn", 0.032, 0.30, loc=(0, 0, 0.26),
                   mat=M['metal'], parent=piv, segments=20)
    shade_smooth(col)
    cylinder("ChairColumnShroud", 0.045, 0.14, loc=(0, 0, 0.20),
             mat=M['plastic_black'], parent=piv, segments=20)

    box("ChairMech", (0.20, 0.22, 0.05), loc=(0, 0, 0.425),
        mat=M['plastic_black'], parent=piv, bevel=0.008)
    box("ChairSeat", (0.50, 0.48, 0.09), loc=(0, 0, 0.495),
        mat=M['chair'], parent=piv, bevel=0.035)

    back = empty("ChairBackPivot", loc=(0, 0.235, 0.52), rot=(D(-12), 0, 0),
                 parent=piv)
    box("ChairBack", (0.46, 0.07, 0.52), loc=(0, 0.02, 0.28),
        mat=M['chair'], parent=back, bevel=0.030)
    box("ChairLumbar", (0.38, 0.05, 0.12), loc=(0, -0.03, 0.12),
        mat=M['chair'], parent=back, bevel=0.020)

    for sx in (-1, 1):
        box("Armrest", (0.07, 0.28, 0.045), loc=(sx * 0.27, 0.03, 0.66),
            mat=M['plastic_black'], parent=piv, bevel=0.015)
        box("ArmPost", (0.04, 0.05, 0.17), loc=(sx * 0.27, 0.10, 0.565),
            mat=M['plastic_black'], parent=piv)
    return piv


# ----------------------------------------------------------------------------
# boom mic stand
# ----------------------------------------------------------------------------

def build_mic_stand(loc=(-2.05, -0.15, 0.0), yaw=D(35)):
    M = MATS
    piv = empty("MicStand", loc=loc, rot=(0, 0, yaw))

    for i in range(3):
        a = TAU * i / 3.0 + D(20)
        box("TripodLeg", (0.36, 0.03, 0.022),
            loc=(math.cos(a) * 0.17, math.sin(a) * 0.17, 0.06),
            rot=(0, D(-9), a), mat=M['dark_metal'], parent=piv, bevel=0.005)
    cylinder("TripodHub", 0.045, 0.09, loc=(0, 0, 0.10),
             mat=M['dark_metal'], parent=piv, segments=18)
    lower = cylinder("StandLower", 0.020, 1.00, loc=(0, 0, 0.60),
                     mat=M['dark_metal'], parent=piv, segments=18)
    shade_smooth(lower)
    upper = cylinder("StandUpper", 0.015, 0.55, loc=(0, 0, 1.28),
                     mat=M['metal'], parent=piv, segments=18)
    shade_smooth(upper)
    cylinder("StandCollar", 0.026, 0.05, loc=(0, 0, 1.08),
             mat=M['plastic_black'], parent=piv, segments=16)

    boom = empty("BoomPivot", loc=(0, 0, 1.52), rot=(D(64), 0, 0), parent=piv)
    arm = cylinder("BoomArm", 0.013, 0.90, loc=(0, 0, 0.30),
                   mat=M['dark_metal'], parent=boom, segments=16)
    shade_smooth(arm)
    cylinder("BoomCounterweight", 0.045, 0.10, loc=(0, 0, -0.22),
             mat=M['dark_metal'], parent=boom, segments=18)
    cylinder("BoomClamp", 0.028, 0.06, loc=(0, 0, 0.0), rot=(D(90), 0, 0),
             mat=M['plastic_black'], parent=boom, segments=16)

    head = empty("MicHead", loc=(0, 0, 0.74), rot=(D(-64) - D(90), 0, 0),
                 parent=boom)
    # shockmount ring + elastics
    bpy.ops.mesh.primitive_torus_add(major_radius=0.055, minor_radius=0.007,
                                     major_segments=28, minor_segments=10,
                                     location=(0, 0, 0))
    ring = bpy.context.object
    ring.name = "ShockMountRing"
    ring.data.materials.append(M['dark_metal'])
    ring.parent = head
    ring.location = (0, 0, 0.0)
    ring.rotation_euler = Euler((D(90), 0, 0), 'XYZ')
    shade_smooth(ring)
    for i in range(6):
        a = TAU * i / 6.0
        cylinder("ShockElastic", 0.002, 0.055,
                 loc=(math.cos(a) * 0.030, 0, math.sin(a) * 0.030),
                 rot=(D(90), 0, 0), mat=M['baffle'], parent=head, segments=6)

    mic = cylinder("MicBody", 0.024, 0.16, loc=(0, 0, 0), rot=(D(90), 0, 0),
                   mat=M['mic'], parent=head, segments=24)
    shade_smooth(mic)
    grille = sphere("MicGrille", 0.028, loc=(0, -0.085, 0), mat=M['mesh'],
                    parent=head, segments=22, rings=12)
    shade_smooth(grille)

    # pop filter on a gooseneck
    goose = empty("PopGooseneck", loc=(0, -0.10, -0.02), rot=(0, 0, 0),
                  parent=head)
    cylinder("GooseneckArm", 0.006, 0.13, loc=(0, -0.05, -0.04),
             rot=(D(70), 0, 0), mat=M['dark_metal'], parent=goose, segments=8)
    bpy.ops.mesh.primitive_torus_add(major_radius=0.075, minor_radius=0.006,
                                     major_segments=28, minor_segments=8,
                                     location=(0, 0, 0))
    pop_ring = bpy.context.object
    pop_ring.name = "PopFilterRing"
    pop_ring.data.materials.append(M['plastic_black'])
    pop_ring.parent = goose
    pop_ring.location = (0, -0.10, -0.02)
    pop_ring.rotation_euler = Euler((D(90), 0, 0), 'XYZ')
    shade_smooth(pop_ring)
    plane("PopFilterMesh", (0.145, 0.145), loc=(0, -0.10, -0.02),
          rot=(D(90), 0, 0), mat=M['mesh'], parent=goose)

    # cable loop back down the stand
    cylinder("MicCable", 0.005, 0.55, loc=(0, -0.02, 1.28), rot=(D(12), 0, 0),
             mat=M['plastic_black'], parent=piv, segments=8)
    return piv


# ----------------------------------------------------------------------------
# soft furnishing + misc
# ----------------------------------------------------------------------------

def build_extras():
    M = MATS
    box("Rug", (2.80, 2.10, 0.014), loc=(0, 0.35, 0.007), mat=M['rug'])
    box("RugBorder", (2.86, 2.16, 0.008), loc=(0, 0.35, 0.004),
        mat=M['fabric_dark'])

    # gear shelf on the rear-left wall with a couple of outboard units
    shelf = empty("GearShelf", loc=(-2.35, -1.55, 0.0))
    box("ShelfBoard", (0.42, 1.10, 0.04), loc=(0, 0, 1.05),
        mat=M['frame_wood'], parent=shelf)
    for sx in (-1, 1):
        box("ShelfBracket", (0.36, 0.04, 0.30), loc=(0.02, sx * 0.45, 0.88),
            mat=M['dark_metal'], parent=shelf)
    for i in range(2):
        box("OutboardUnit", (0.36, 0.44, 0.10),
            loc=(0, -0.26 + i * 0.52, 1.12), mat=M['plastic_black'],
            parent=shelf)
        box("OutboardDisplay", (0.010, 0.14, 0.03),
            loc=(-0.185, -0.26 + i * 0.52, 1.13),
            mat=M['led_amber'], parent=shelf)

    # a couple of stacked flight cases in the rear corner
    for i, (sz, z) in enumerate(((0.52, 0.26), (0.44, 0.66))):
        box("FlightCase", (0.62, 0.46, sz), loc=(2.35, -1.62, z),
            rot=(0, 0, D(-8) if i else D(4)), mat=M['plastic_black'],
            bevel=0.012)


# ----------------------------------------------------------------------------
# lighting
# ----------------------------------------------------------------------------

def add_area_light(name, energy, size, loc, rot, color=(1.0, 0.92, 0.82),
                   size_y=None, shape='RECTANGLE'):
    data = bpy.data.lights.new(name, 'AREA')
    data.energy = energy
    data.color = color
    data.shape = shape
    data.size = size
    if size_y is not None:
        data.size_y = size_y
    obj = bpy.data.objects.new(name, data)
    bpy.context.collection.objects.link(obj)
    obj.location = loc
    obj.rotation_euler = Euler(rot, 'XYZ')
    return obj


def add_spot(name, energy, loc, target, color=(1.0, 0.86, 0.70),
             spot_size=D(60), blend=0.45, radius=0.06):
    data = bpy.data.lights.new(name, 'SPOT')
    data.energy = energy
    data.color = color
    data.spot_size = spot_size
    data.spot_blend = blend
    data.shadow_soft_size = radius
    obj = bpy.data.objects.new(name, data)
    bpy.context.collection.objects.link(obj)
    obj.location = loc
    direction = Vector(target) - Vector(loc)
    obj.rotation_euler = direction.to_track_quat('-Z', 'Y').to_euler()
    return obj


def build_lighting():
    M = MATS

    # main soft key over the mix position
    add_area_light("KeyOverhead", 140.0, 2.6, (0.0, 0.80, 2.62),
                   (0, 0, 0), color=(1.0, 0.90, 0.78), size_y=1.2)

    # gentle wash on the front wall / window area
    add_area_light("FrontWash", 45.0, 3.2, (0.0, 1.95, 2.40),
                   (D(52), 0, 0), color=(0.80, 0.86, 1.0), size_y=0.5)

    # rear bounce so the diffuser reads
    add_area_light("RearFill", 30.0, 2.4, (0.0, -1.70, 2.35),
                   (D(-58), 0, 0), color=(0.75, 0.82, 1.0), size_y=0.6)

    # accent spots grazing the side panels
    add_spot("AccentLeft", 90.0, (-2.30, 0.95, 2.62), (-2.95, 0.60, 1.45),
             color=(1.0, 0.80, 0.62), spot_size=D(55))
    add_spot("AccentRight", 90.0, (2.30, 0.95, 2.62), (2.95, 0.60, 1.45),
             color=(1.0, 0.80, 0.62), spot_size=D(55))

    # practical: recessed ceiling cans (visible fixtures)
    for sx in (-1.6, 1.6):
        for sy in (-1.4, 0.9):
            can = cylinder("CeilingCan", 0.075, 0.05, loc=(sx, sy, RZ - 0.02),
                           mat=M['dark_metal'], segments=20)
            shade_smooth(can)
            cylinder("CeilingCanLens", 0.058, 0.012, loc=(sx, sy, RZ - 0.048),
                     mat=M['led_strip'], segments=20)


# ----------------------------------------------------------------------------
# camera
# ----------------------------------------------------------------------------

def build_camera(scene):
    cam_data = bpy.data.cameras.new("StudioCam")
    cam_data.lens = 26.0
    cam_data.sensor_width = 36.0
    cam_data.clip_start = 0.02
    cam_data.clip_end = 100.0
    cam_data.dof.use_dof = True
    cam_data.dof.focus_distance = 3.3
    cam_data.dof.aperture_fstop = 3.2

    cam = bpy.data.objects.new("StudioCam", cam_data)
    bpy.context.collection.objects.link(cam)

    loc = Vector((-2.42, -1.86, 1.70))
    target = Vector((0.10, 1.15, 1.05))
    cam.location = loc
    cam.rotation_euler = (target - loc).to_track_quat('-Z', 'Y').to_euler()

    scene.camera = cam
    scene.render.resolution_x = 1920
    scene.render.resolution_y = 1080
    return cam


# ----------------------------------------------------------------------------
# assembly
# ----------------------------------------------------------------------------

def main():
    scene = reset_scene()
    build_materials()

    build_room()
    build_treatment()
    desk = build_desk()

    # nearfields on the bridge, toed in toward the mix position
    bridge_top = 1.045
    build_monitor("MonitorL", (-0.95, 1.56, bridge_top), D(-22))
    build_monitor("MonitorR", (0.95, 1.56, bridge_top), D(22))

    build_chair()
    build_mic_stand()
    build_extras()
    build_lighting()
    build_camera(scene)

    bpy.context.view_layer.update()
    print("Recording studio built: %d objects" % len(bpy.data.objects))
    return desk


if __name__ == "__main__":
    main()
