import bpy
import bmesh
import math
from mathutils import Vector


def clear_scene():
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete(use_global=False)
    for mesh in list(bpy.data.meshes):
        if mesh.users == 0:
            bpy.data.meshes.remove(mesh)


def material(name, color, roughness=0.65, metallic=0.0):
    mat = bpy.data.materials.new(name)
    mat.use_nodes = True
    bsdf = mat.node_tree.nodes["Principled BSDF"]
    bsdf.inputs["Base Color"].default_value = (*color, 1.0)
    bsdf.inputs["Roughness"].default_value = roughness
    bsdf.inputs["Metallic"].default_value = metallic
    return mat


def box(name, size, center, mat, rotation=(0.0, 0.0, 0.0)):
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=center, rotation=rotation)
    obj = bpy.context.active_object
    obj.name = name
    obj.scale = size
    bpy.ops.object.transform_apply(scale=True)
    obj.data.materials.append(mat)
    return obj


def cylinder(name, radius, depth, center, mat, rotation=(0.0, 0.0, 0.0), verts=16):
    bpy.ops.mesh.primitive_cylinder_add(radius=radius, depth=depth, vertices=verts,
                                        location=center, rotation=rotation)
    obj = bpy.context.active_object
    obj.name = name
    obj.data.materials.append(mat)
    return obj


def wedge_ramp(name, width, run, height, origin, mat):
    """Triangular-prism approach ramp built with bmesh; rises along +Y."""
    mesh = bpy.data.meshes.new(name)
    obj = bpy.data.objects.new(name, mesh)
    bpy.context.collection.objects.link(obj)
    bm = bmesh.new()
    hw = width * 0.5
    profile = ((0.0, 0.0), (run, 0.0), (run, height))
    for x in (-hw, hw):
        for y, z in profile:
            bm.verts.new((x, y, z))
    bm.verts.ensure_lookup_table()
    v = bm.verts
    bm.faces.new((v[0], v[1], v[2]))
    bm.faces.new((v[5], v[4], v[3]))
    bm.faces.new((v[0], v[3], v[4], v[1]))   # ground side
    bm.faces.new((v[1], v[4], v[5], v[2]))   # vertical face at the dock
    bm.faces.new((v[2], v[5], v[3], v[0]))   # sloped driving surface
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces[:])
    bm.to_mesh(mesh)
    bm.free()
    obj.location = origin
    obj.data.materials.append(mat)
    return obj


clear_scene()

CONCRETE = material("Concrete", (0.58, 0.57, 0.55), roughness=0.95)
ASPHALT = material("Asphalt", (0.11, 0.11, 0.12), roughness=1.0)
WALL = material("WarehouseWall", (0.72, 0.70, 0.66), roughness=0.8)
DOOR = material("DoorPanel", (0.78, 0.79, 0.80), roughness=0.4, metallic=0.7)
STEEL = material("Steel", (0.35, 0.36, 0.38), roughness=0.45, metallic=0.9)
RUBBER = material("DockBumper", (0.05, 0.05, 0.06), roughness=0.95)
STRIPE = material("SafetyYellow", (0.85, 0.63, 0.05), roughness=0.7)

DOCK_H = 1.25          # trailer-bed height
DOCK_W = 12.0
DOCK_D = 6.0
BAY_W = 3.2
DOOR_H = 3.6
WALL_T = 0.3

# --- ground, platform and warehouse shell ---
box("Apron", (24.0, 20.0, 0.2), (0.0, -8.0, -0.1), ASPHALT)
box("DockPlatform", (DOCK_W, DOCK_D, DOCK_H), (0.0, DOCK_D * 0.5, DOCK_H * 0.5), CONCRETE)
box("DockFaceCurb", (DOCK_W, 0.12, 0.35), (0.0, -0.06, DOCK_H - 0.175), STEEL)
box("WarehouseWall", (DOCK_W, WALL_T, 5.4), (0.0, DOCK_D + WALL_T * 0.5, DOCK_H + 2.7), WALL)
box("Parapet", (DOCK_W + 0.4, DOCK_D + 0.6, 0.35),
    (0.0, DOCK_D * 0.5 + 0.3, DOCK_H + 5.55), WALL)


def build_bay(index, x):
    """One dock position: framed opening, sectional door, bumpers, dock light."""
    y_wall = DOCK_D + WALL_T * 0.5
    hw = BAY_W * 0.5
    for sx, tag in ((-1, "L"), (1, "R")):
        box("Jamb_%d_%s" % (index, tag), (0.22, WALL_T + 0.06, DOOR_H),
            (x + sx * (hw + 0.11), y_wall, DOCK_H + DOOR_H * 0.5), STEEL)
    box("Header_%d" % index, (BAY_W + 0.44, WALL_T + 0.06, 0.3),
        (x, y_wall, DOCK_H + DOOR_H + 0.15), STEEL)
    # sectional overhead door, five ribbed panels
    panel_h = DOOR_H / 5.0
    for p in range(5):
        box("DoorPanel_%d_%d" % (index, p), (BAY_W, 0.09, panel_h * 0.94),
            (x, y_wall - 0.12, DOCK_H + panel_h * (p + 0.5)), DOOR)
    for sx, tag in ((-1, "L"), (1, "R")):
        box("DoorTrack_%d_%s" % (index, tag), (0.06, 0.06, DOOR_H + 0.2),
            (x + sx * (hw + 0.02), y_wall - 0.2, DOCK_H + DOOR_H * 0.5), STEEL)
    # laminated rubber bumpers flanking the opening
    for sx, tag in ((-1, "L"), (1, "R")):
        bx = x + sx * (hw - 0.25)
        box("Bumper_%d_%s" % (index, tag), (0.5, 0.24, 0.5),
            (bx, -0.12, DOCK_H - 0.32), RUBBER)
        box("BumperFace_%d_%s" % (index, tag), (0.46, 0.03, 0.44),
            (bx, -0.245, DOCK_H - 0.32), RUBBER)
    # swing-arm dock light
    cylinder("DockLightArm_%d" % index, 0.04, 1.1,
             (x + hw + 0.35, y_wall - 0.55, DOCK_H + DOOR_H + 0.5), STEEL,
             rotation=(math.radians(90), 0.0, 0.0))
    cylinder("DockLightHead_%d" % index, 0.16, 0.2,
             (x + hw + 0.35, y_wall - 1.05, DOCK_H + DOOR_H + 0.5), STEEL,
             rotation=(math.radians(90), 0.0, 0.0))
    # painted approach guide stripes
    for sx in (-1, 1):
        box("GuideStripe_%d_%d" % (index, sx), (0.14, 5.0, 0.02),
            (x + sx * (hw + 0.3), -2.6, 0.015), STRIPE)


for i, cx in enumerate((-3.6, 3.6)):
    build_bay(i, cx)

# --- drive-up ramp to the deck at the near end of the platform ---
ramp_x = DOCK_W * 0.5 + 1.9
wedge_ramp("ApproachRamp", 3.4, 5.0, DOCK_H, Vector((ramp_x, -5.0, 0.0)), CONCRETE)
box("RampDeck", (3.4, 1.4, 0.2), (ramp_x, 0.7, DOCK_H - 0.1), CONCRETE)
for sx in (-1.75, 1.75):
    box("RampCurb_%s" % ("L" if sx < 0 else "R"), (0.16, 5.05, 0.3),
        (ramp_x + sx, -2.5, DOCK_H * 0.5 + 0.15), STRIPE,
        rotation=(math.atan2(DOCK_H, 5.0), 0.0, 0.0))

# guard rail along the open platform edge beside the ramp
rail_x = DOCK_W * 0.5
for i in range(4):
    cylinder("GuardPost_%d" % i, 0.05, 1.1, (rail_x, 1.6 + i * 1.3, DOCK_H + 0.55), STEEL)
cylinder("GuardRail_Top", 0.05, 4.2, (rail_x, 3.55, DOCK_H + 1.05), STEEL,
         rotation=(math.radians(90), 0.0, 0.0))

for bx in (-DOCK_W * 0.5 + 0.4, DOCK_W * 0.5 - 0.4):
    cylinder("Bollard_%s" % ("L" if bx < 0 else "R"), 0.14, 1.1, (bx, -1.2, 0.55), STRIPE)

# --- lighting and camera ---
bpy.ops.object.light_add(type='SUN', location=(-10.0, -14.0, 18.0))
sun = bpy.context.active_object
sun.name = "Sun"
sun.data.energy = 3.5
sun.rotation_euler = (math.radians(50), 0.0, math.radians(-40))

bpy.ops.object.camera_add(location=(13.0, -16.0, 8.5))
cam = bpy.context.active_object
cam.name = "Camera"
cam.data.lens = 40
aim = Vector((0.0, 2.0, 2.0)) - cam.location
cam.rotation_euler = aim.to_track_quat('-Z', 'Y').to_euler()
bpy.context.scene.camera = cam
