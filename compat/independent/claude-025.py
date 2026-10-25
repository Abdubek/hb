import bpy
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


def add_cylinder(name, radius, depth, location, verts=20,
                 rotation=(0.0, 0.0, 0.0), material=None):
    bpy.ops.mesh.primitive_cylinder_add(radius=radius, depth=depth,
                                        vertices=verts, location=location,
                                        rotation=rotation)
    obj = bpy.context.object
    obj.name = name
    if material:
        obj.data.materials.append(material)
    return obj


def aim_camera(location, target, lens=40.0):
    cam_data = bpy.data.cameras.new("GazeboCam")
    cam_data.lens = lens
    cam = bpy.data.objects.new("Camera", cam_data)
    bpy.context.collection.objects.link(cam)
    cam.location = location
    direction = Vector(target) - Vector(location)
    cam.rotation_euler = direction.to_track_quat('-Z', 'Y').to_euler()
    bpy.context.scene.camera = cam
    return cam


def ring_point(radius, angle, z):
    return Vector((radius * math.cos(angle), radius * math.sin(angle), z))


def build_bay(index, p1, p2, post_r, material):
    """Top rail, bottom rail and balusters spanning the chord p1 -> p2."""
    chord = p2 - p1
    span = chord.length - 2.0 * post_r
    yaw = math.atan2(chord.y, chord.x)
    mid = (p1 + p2) * 0.5
    for z, thick in ((1.02, 0.07), (0.34, 0.06)):
        add_box("Gazebo_Rail_%d" % index, (span, thick, thick),
                (mid.x, mid.y, z), rotation=(0.0, 0.0, yaw), material=material)
    unit = chord.normalized()
    count = 5
    for k in range(count):
        f = (k + 0.5) / count
        base = p1 + unit * (post_r + span * f)
        add_box("Gazebo_Baluster_%d_%d" % (index, k), (0.05, 0.05, 0.66),
                (base.x, base.y, 0.68), rotation=(0.0, 0.0, yaw), material=material)


# ---------------------------------------------------------------- build

clear_scene()

LAWN = make_material("Lawn", (0.20, 0.34, 0.15), 0.9)
STONE = make_material("StoneBase", (0.55, 0.53, 0.49), 0.8)
DECK = make_material("DeckTimber", (0.52, 0.36, 0.21), 0.65)
PAINT = make_material("PaintedTrim", (0.90, 0.89, 0.85), 0.45)
SHINGLE = make_material("RoofShingle", (0.28, 0.24, 0.26), 0.55)
BRASS = make_material("Finial", (0.72, 0.55, 0.20), 0.3, 1.0)

SIDES = 8
POST_R_RING = 2.15
POST_RADIUS = 0.09
DECK_TOP = 0.0
POST_H = 2.5
ROOF_BASE = DECK_TOP + POST_H
ROOF_RISE = 1.15
EAVE_R = 2.75

bpy.ops.mesh.primitive_plane_add(size=18.0, location=(0.0, 0.0, -0.38))
lawn = bpy.context.object
lawn.name = "Lawn"
lawn.data.materials.append(LAWN)

add_cylinder("Gazebo_StoneFooting", 2.62, 0.3, (0.0, 0.0, -0.23), verts=48,
             material=STONE)
add_cylinder("Gazebo_Deck", 2.45, 0.16, (0.0, 0.0, -0.08), verts=48,
             material=DECK)

angles = [i * 2.0 * math.pi / SIDES for i in range(SIDES)]
posts = [ring_point(POST_R_RING, a, 0.0) for a in angles]

for i, p in enumerate(posts):
    add_cylinder("Gazebo_Post_%d" % i, POST_RADIUS, POST_H,
                 (p.x, p.y, DECK_TOP + POST_H * 0.5), verts=12, material=PAINT)
    add_box("Gazebo_PostCap_%d" % i, (0.26, 0.26, 0.08),
            (p.x, p.y, ROOF_BASE - 0.04), rotation=(0.0, 0.0, angles[i]),
            material=PAINT)

# leave bay 0 open as the entrance
for i in range(1, SIDES):
    build_bay(i, posts[i], posts[(i + 1) % SIDES], POST_RADIUS, PAINT)

# ring beam carrying the roof
bpy.ops.mesh.primitive_torus_add(major_radius=POST_R_RING, minor_radius=0.08,
                                 major_segments=48, minor_segments=8,
                                 location=(0.0, 0.0, ROOF_BASE - 0.16))
beam = bpy.context.object
beam.name = "Gazebo_RingBeam"
beam.data.materials.append(PAINT)

bpy.ops.mesh.primitive_cone_add(radius1=EAVE_R, radius2=0.06, depth=ROOF_RISE,
                                vertices=48,
                                location=(0.0, 0.0, ROOF_BASE + ROOF_RISE * 0.5))
roof = bpy.context.object
roof.name = "Gazebo_Roof"
roof.data.materials.append(SHINGLE)
shell = roof.modifiers.new("Shell", 'SOLIDIFY')
shell.thickness = 0.06

bpy.ops.mesh.primitive_torus_add(major_radius=EAVE_R, minor_radius=0.07,
                                 major_segments=48, minor_segments=8,
                                 location=(0.0, 0.0, ROOF_BASE))
fascia = bpy.context.object
fascia.name = "Gazebo_Fascia"
fascia.data.materials.append(PAINT)

# hip ribs lying on the cone surface
pitch = math.atan2(ROOF_RISE, EAVE_R)
rib_len = math.hypot(ROOF_RISE, EAVE_R)
for i, a in enumerate(angles):
    mid = ring_point(EAVE_R * 0.5, a, ROOF_BASE + ROOF_RISE * 0.5)
    add_box("Gazebo_Rib_%d" % i, (rib_len, 0.10, 0.05),
            (mid.x, mid.y, mid.z + 0.03),
            rotation=(0.0, -pitch, a), material=PAINT)

add_cylinder("Gazebo_FinialStem", 0.06, 0.32,
             (0.0, 0.0, ROOF_BASE + ROOF_RISE + 0.12), verts=12, material=BRASS)
bpy.ops.mesh.primitive_uv_sphere_add(radius=0.16, segments=20, ring_count=10,
                                     location=(0.0, 0.0, ROOF_BASE + ROOF_RISE + 0.4))
ball = bpy.context.object
ball.name = "Gazebo_FinialBall"
ball.data.materials.append(BRASS)

# entrance steps on the +X side
for k, (width, z) in enumerate(((1.5, -0.22), (1.7, -0.36))):
    add_box("Gazebo_Step_%d" % k, (0.42, width, 0.14),
            (2.62 + 0.42 * k, 0.0, z), material=STONE)

aim_camera((7.4, -7.2, 4.6), (0.0, 0.0, 1.5))

sun_data = bpy.data.lights.new("Sun", 'SUN')
sun_data.energy = 3.5
sun = bpy.data.objects.new("Sun", sun_data)
bpy.context.collection.objects.link(sun)
sun.location = (5.0, -5.0, 9.0)
sun.rotation_euler = (math.radians(50.0), 0.0, math.radians(40.0))
