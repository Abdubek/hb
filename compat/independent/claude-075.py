import bpy
import math
from mathutils import Vector

# ---------------------------------------------------------------- utilities

def reset_scene():
    for ob in list(bpy.data.objects):
        bpy.data.objects.remove(ob, do_unlink=True)
    for me in list(bpy.data.meshes):
        bpy.data.meshes.remove(me)


def make_mat(name, color, rough=0.5, metal=0.0):
    mat = bpy.data.materials.new(name)
    mat.use_nodes = True
    bsdf = mat.node_tree.nodes["Principled BSDF"]
    bsdf.inputs["Base Color"].default_value = (color[0], color[1], color[2], 1.0)
    bsdf.inputs["Roughness"].default_value = rough
    bsdf.inputs["Metallic"].default_value = metal
    return mat


def _finish(ob, name, mat, parent):
    ob.name = name
    ob.data.name = name
    if mat:
        ob.data.materials.append(mat)
    if parent:
        ob.parent = parent
        ob.matrix_parent_inverse = parent.matrix_world.inverted()
    return ob


def box(name, dims, loc, rot=(0, 0, 0), mat=None, parent=None):
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=loc, rotation=rot)
    ob = bpy.context.object
    ob.scale = dims
    return _finish(ob, name, mat, parent)


def cyl(name, r, h, loc, rot=(0, 0, 0), verts=20, mat=None, parent=None):
    bpy.ops.mesh.primitive_cylinder_add(radius=r, depth=h, vertices=verts,
                                        location=loc, rotation=rot)
    return _finish(bpy.context.object, name, mat, parent)


def bevel(ob, width=0.02, segments=2):
    bpy.ops.object.select_all(action='DESELECT')
    ob.select_set(True)
    bpy.context.view_layer.objects.active = ob
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    mod = ob.modifiers.new("Bevel", 'BEVEL')
    mod.width = width
    mod.segments = segments
    mod.limit_method = 'ANGLE'
    mod.angle_limit = math.radians(40.0)
    bpy.ops.object.modifier_apply(modifier=mod.name)
    return ob


def empty(name, loc=(0, 0, 0)):
    ob = bpy.data.objects.new(name, None)
    ob.empty_display_size = 0.5
    ob.location = loc
    bpy.context.scene.collection.objects.link(ob)
    return ob

# ---------------------------------------------------------------- materials

ROOF = make_mat("RoofMembrane", (0.30, 0.30, 0.31), rough=0.95)
CURB = make_mat("MountCurb", (0.18, 0.18, 0.19), rough=0.8)
SHELL = make_mat("CabinetShell", (0.70, 0.71, 0.72), rough=0.42, metal=0.85)
PANEL = make_mat("AccessPanel", (0.62, 0.63, 0.65), rough=0.5, metal=0.8)
GRILLE = make_mat("GrilleSteel", (0.30, 0.31, 0.33), rough=0.55, metal=0.9)
DUCT = make_mat("DuctGalv", (0.78, 0.79, 0.80), rough=0.3, metal=1.0)
ACCENT = make_mat("AccentBlue", (0.10, 0.28, 0.55), rough=0.4)

# ---------------------------------------------------------------- assemblies

TOP_Z = 1.70   # top face of the cabinet


def build_cabinet(parent):
    box("RoofCurb", (4.40, 2.80, 0.30), (0, 0, 0.15), mat=CURB, parent=parent)
    box("CurbGasket", (4.10, 2.50, 0.06), (0, 0, 0.32), mat=ACCENT, parent=parent)
    shell = box("MainCabinet", (4.00, 2.40, 1.35), (0, 0, 1.025),
                mat=SHELL, parent=parent)
    bevel(shell, 0.035, 2)
    box("TopCapRail", (4.06, 2.46, 0.06), (0, 0, TOP_Z - 0.01),
        mat=PANEL, parent=parent)
    return shell


def build_fan_grille(name, x, y, parent):
    cyl(name + "_Shroud", 0.62, 0.20, (x, y, TOP_Z + 0.06), verts=24,
        mat=PANEL, parent=parent)
    cyl(name + "_Throat", 0.52, 0.22, (x, y, TOP_Z + 0.04), verts=24,
        mat=GRILLE, parent=parent)
    cyl(name + "_Hub", 0.13, 0.08, (x, y, TOP_Z + 0.17), verts=16,
        mat=GRILLE, parent=parent)
    for i in range(12):
        a = math.pi * i / 12.0
        box("%s_Bar%02d" % (name, i), (1.12, 0.035, 0.028),
            (x, y, TOP_Z + 0.16), (0, 0, a), GRILLE, parent)
    for j, r in enumerate((0.28, 0.50)):
        bpy.ops.mesh.primitive_torus_add(major_radius=r, minor_radius=0.018,
                                         major_segments=24, minor_segments=6,
                                         location=(x, y, TOP_Z + 0.16))
        _finish(bpy.context.object, "%s_Ring%d" % (name, j), GRILLE, parent)


def build_louvers(name, y_face, parent):
    sign = 1.0 if y_face > 0 else -1.0
    box(name + "_Frame", (2.30, 0.06, 1.00), (0.75, y_face, 1.02),
        mat=PANEL, parent=parent)
    for i in range(9):
        z = 0.60 + i * 0.105
        box("%s_Slat%02d" % (name, i), (2.20, 0.10, 0.05),
            (0.75, y_face + sign * 0.03, z), (math.radians(-28.0 * sign), 0, 0),
            GRILLE, parent)


def build_duct(name, y, parent):
    box(name + "_Collar", (0.16, 0.92, 0.82), (-1.96, y, 0.95),
        mat=DUCT, parent=parent)
    box(name + "_Run", (1.25, 0.80, 0.70), (-2.60, y, 0.95),
        mat=DUCT, parent=parent)
    box(name + "_Flange", (0.08, 0.92, 0.82), (-3.20, y, 0.95),
        mat=PANEL, parent=parent)
    box(name + "_Elbow", (0.80, 0.80, 0.80), (-3.62, y, 0.95),
        mat=DUCT, parent=parent)
    box(name + "_Drop", (0.72, 0.72, 0.60), (-3.62, y, 0.28),
        mat=DUCT, parent=parent)
    box(name + "_Boot", (0.92, 0.92, 0.10), (-3.62, y, 0.05),
        mat=CURB, parent=parent)


def build_service_side(parent):
    panel = box("AccessPanel", (0.07, 1.70, 1.05), (2.02, 0.30, 1.02),
                mat=PANEL, parent=parent)
    bevel(panel, 0.02, 1)
    for i, y in enumerate((-0.42, 1.02)):
        cyl("PanelHinge%d" % i, 0.045, 0.16, (2.04, y, 1.02),
            (0, math.radians(90), 0), verts=10, mat=GRILLE, parent=parent)
    cyl("PanelHandle", 0.035, 0.34, (2.10, 0.30, 1.02),
        (math.radians(90), 0, 0), verts=10, mat=GRILLE, parent=parent)
    box("ControlBox", (0.30, 0.55, 0.65), (2.05, -1.55, 1.05),
        mat=ACCENT, parent=parent)
    box("NamePlate", (0.03, 0.42, 0.16), (2.21, -1.55, 1.28),
        mat=PANEL, parent=parent)
    cyl("Conduit", 0.05, 1.05, (2.12, -1.55, 0.35),
        (0, 0, 0), verts=12, mat=GRILLE, parent=parent)
    cyl("ConduitElbow", 0.05, 0.30, (2.12, -1.42, 0.12),
        (math.radians(90), 0, 0), verts=12, mat=GRILLE, parent=parent)


def add_camera(loc, target, lens=42.0):
    cam_data = bpy.data.cameras.new("Camera")
    cam_data.lens = lens
    cam = bpy.data.objects.new("Camera", cam_data)
    bpy.context.scene.collection.objects.link(cam)
    cam.location = loc
    cam.rotation_euler = (Vector(target) - Vector(loc)).to_track_quat('-Z', 'Y').to_euler()
    bpy.context.scene.camera = cam
    return cam

# ---------------------------------------------------------------- scene

reset_scene()

bpy.ops.mesh.primitive_plane_add(size=18.0, location=(0, 0, 0))
_finish(bpy.context.object, "RoofDeck", ROOF, None)

unit = empty("RTU_Assembly", (0, 0, 0))
build_cabinet(unit)
build_fan_grille("SupplyFan", -0.95, 0.0, unit)
build_fan_grille("ExhaustFan", 0.95, 0.0, unit)
build_louvers("CoilLouverN", 1.21, unit)
build_louvers("CoilLouverS", -1.21, unit)
build_duct("SupplyDuct", -0.52, unit)
build_duct("ReturnDuct", 0.52, unit)
build_service_side(unit)

sun_data = bpy.data.lights.new("Sun", type='SUN')
sun_data.energy = 3.5
sun = bpy.data.objects.new("Sun", sun_data)
sun.rotation_euler = (math.radians(52), 0.0, math.radians(-35))
sun.location = (5.0, -5.0, 10.0)
bpy.context.scene.collection.objects.link(sun)

world = bpy.data.worlds.new("SkyWorld")
world.use_nodes = True
world.node_tree.nodes["Background"].inputs[0].default_value = (0.32, 0.45, 0.60, 1.0)
bpy.context.scene.world = world

add_camera((6.8, -7.6, 4.9), (-0.4, 0.0, 1.10))
