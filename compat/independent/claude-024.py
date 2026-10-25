import bpy
import bmesh
import math
from mathutils import Vector

# ---------------------------------------------------------------- helpers


def clear_scene():
    for obj in list(bpy.data.objects):
        bpy.data.objects.remove(obj, do_unlink=True)


def make_material(name, color, roughness=0.5, metallic=0.0):
    mat = bpy.data.materials.new(name)
    mat.use_nodes = True
    bsdf = mat.node_tree.nodes["Principled BSDF"]
    bsdf.inputs["Base Color"].default_value = (*color, 1.0)
    bsdf.inputs["Roughness"].default_value = roughness
    bsdf.inputs["Metallic"].default_value = metallic
    return mat


def add_box(name, size, location, rotation=(0.0, 0.0, 0.0), material=None):
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=location)
    obj = bpy.context.object
    obj.name = name
    obj.scale = size
    obj.rotation_euler = rotation
    if material:
        obj.data.materials.append(material)
    return obj


def add_cylinder(name, radius, depth, location, rotation=(0.0, 0.0, 0.0),
                 verts=16, material=None):
    bpy.ops.mesh.primitive_cylinder_add(radius=radius, depth=depth,
                                        vertices=verts, location=location,
                                        rotation=rotation)
    obj = bpy.context.object
    obj.name = name
    if material:
        obj.data.materials.append(material)
    return obj


def aim_camera(location, target, lens=42.0):
    cam_data = bpy.data.cameras.new("SlideCam")
    cam_data.lens = lens
    cam = bpy.data.objects.new("Camera", cam_data)
    bpy.context.collection.objects.link(cam)
    cam.location = location
    direction = Vector(target) - Vector(location)
    cam.rotation_euler = direction.to_track_quat('-Z', 'Y').to_euler()
    bpy.context.scene.camera = cam
    return cam


def build_chute(name, width, wall_h, length, drop, segments, material):
    """Sweep a U shaped profile along a smooth S curve falling in +Y."""
    path = []
    for i in range(segments + 1):
        t = i / segments
        path.append(Vector((0.0, t * length, drop * 0.5 * (1.0 + math.cos(math.pi * t)))))

    across = Vector((1.0, 0.0, 0.0))
    profile = [(-width * 0.5, wall_h), (-width * 0.5, 0.0),
               (width * 0.5, 0.0), (width * 0.5, wall_h)]

    bm = bmesh.new()
    rows = []
    for i, point in enumerate(path):
        nxt = path[min(i + 1, segments)]
        prv = path[max(i - 1, 0)]
        tangent = (nxt - prv).normalized()
        up = across.cross(tangent).normalized()
        rows.append([bm.verts.new(point + across * dx + up * du) for dx, du in profile])

    for i in range(segments):
        for j in range(len(profile) - 1):
            bm.faces.new((rows[i][j], rows[i][j + 1], rows[i + 1][j + 1], rows[i + 1][j]))
    bm.normal_update()

    mesh = bpy.data.meshes.new(name)
    bm.to_mesh(mesh)
    bm.free()
    obj = bpy.data.objects.new(name, mesh)
    bpy.context.collection.objects.link(obj)
    obj.data.materials.append(material)
    solid = obj.modifiers.new("Shell", 'SOLIDIFY')
    solid.thickness = 0.05
    solid.offset = -1.0
    return obj


# ---------------------------------------------------------------- build

clear_scene()

GRASS = make_material("Grass", (0.22, 0.38, 0.16), 0.9)
STEEL = make_material("GalvanisedSteel", (0.62, 0.64, 0.66), 0.35, 1.0)
DECK = make_material("DeckPlastic", (0.15, 0.35, 0.62), 0.55)
SLIDE = make_material("SlideYellow", (0.86, 0.62, 0.08), 0.3)
RAIL = make_material("RailRed", (0.68, 0.14, 0.12), 0.4)

DECK_Z = 1.8
DECK_HALF = 0.6

bpy.ops.mesh.primitive_plane_add(size=16.0, location=(0.0, 1.0, 0.0))
ground = bpy.context.object
ground.name = "Ground"
ground.data.materials.append(GRASS)

add_box("Platform_Deck", (2 * DECK_HALF, 2 * DECK_HALF, 0.09),
        (0.0, 0.0, DECK_Z - 0.045), material=DECK)

for sx in (-1, 1):
    for sy in (-1, 1):
        add_cylinder("Platform_Leg", 0.055, DECK_Z,
                     (sx * (DECK_HALF - 0.09), sy * (DECK_HALF - 0.09), DECK_Z * 0.5),
                     material=STEEL)

# platform side railings (left/right), entry rails at the slide mouth
for sx in (-1, 1):
    add_box("Platform_TopRail", (0.06, 2 * DECK_HALF, 0.06),
            (sx * DECK_HALF, 0.0, DECK_Z + 0.9), material=RAIL)
    for sy in (-1, 1):
        add_cylinder("Platform_RailPost", 0.04, 0.9,
                     (sx * DECK_HALF, sy * (DECK_HALF - 0.06), DECK_Z + 0.45),
                     material=RAIL)
    for k in range(3):
        y = -DECK_HALF + 0.3 * (k + 1)
        add_box("Platform_Baluster", (0.04, 0.04, 0.85),
                (sx * DECK_HALF, y, DECK_Z + 0.42), material=RAIL)

for sx in (-1, 1):
    add_cylinder("Slide_GrabPost", 0.035, 0.8,
                 (sx * 0.36, DECK_HALF, DECK_Z + 0.4), material=STEEL)
add_cylinder("Slide_GrabBar", 0.035, 0.72, (0.0, DECK_HALF, DECK_Z + 0.8),
             rotation=(0.0, math.pi * 0.5, 0.0), material=STEEL)

chute = build_chute("Slide_Chute", 0.62, 0.24, 3.3, DECK_Z - 0.2, 24, SLIDE)
chute.location = (0.0, DECK_HALF, 0.2)

add_box("Slide_Runout", (0.72, 0.5, 0.08), (0.0, DECK_HALF + 3.45, 0.2), material=SLIDE)

# ladder: rails from the ground up to the deck on the -Y side
foot_y, top_y = -1.55, -DECK_HALF
rise = DECK_Z
span = top_y - foot_y
rail_len = math.hypot(span, rise) + 0.25
tilt = math.atan2(span, rise)
for sx in (-1, 1):
    add_box("Ladder_Rail", (0.07, 0.07, rail_len),
            (sx * 0.44, (foot_y + top_y) * 0.5, rise * 0.5),
            rotation=(tilt, 0.0, 0.0), material=STEEL)

for k in range(6):
    f = (k + 0.5) / 6.0
    add_cylinder("Ladder_Rung", 0.032, 0.88,
                 (0.0, foot_y + span * f, rise * f),
                 rotation=(0.0, math.pi * 0.5, 0.0), material=RAIL)

aim_camera((6.2, -5.6, 4.2), (0.0, 0.9, 1.3))

sun_data = bpy.data.lights.new("Sun", 'SUN')
sun_data.energy = 4.0
sun = bpy.data.objects.new("Sun", sun_data)
bpy.context.collection.objects.link(sun)
sun.location = (4.0, -4.0, 8.0)
sun.rotation_euler = (math.radians(48.0), 0.0, math.radians(35.0))
