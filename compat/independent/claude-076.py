import bpy
import math
from mathutils import Vector

def reset_scene():
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete(use_global=False)
    for block in (bpy.data.meshes, bpy.data.materials):
        for item in block:
            if item.users == 0:
                block.remove(item)

def make_material(name, color, roughness=0.6, metallic=0.0):
    mat = bpy.data.materials.new(name)
    mat.use_nodes = True
    bsdf = mat.node_tree.nodes["Principled BSDF"]
    bsdf.inputs["Base Color"].default_value = (*color, 1.0)
    bsdf.inputs["Roughness"].default_value = roughness
    bsdf.inputs["Metallic"].default_value = metallic
    return mat

def add_box(name, size, location, material, rotation=(0, 0, 0)):
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=location, rotation=rotation)
    obj = bpy.context.active_object
    obj.name = name
    obj.scale = Vector(size) * 0.5
    bpy.ops.object.transform_apply(scale=True)
    obj.data.materials.append(material)
    return obj

def add_pipe(name, radius, length, location, material, rotation=(0, 0, 0)):
    bpy.ops.mesh.primitive_cylinder_add(radius=radius, depth=length, vertices=12,
                                        location=location, rotation=rotation)
    obj = bpy.context.active_object
    obj.name = name
    obj.data.materials.append(material)
    return obj

reset_scene()

BRICK = make_material("Brick", (0.42, 0.20, 0.16), roughness=0.9)
STEEL = make_material("PaintedSteel", (0.16, 0.17, 0.18), roughness=0.5, metallic=0.85)
GRATE = make_material("Grating", (0.30, 0.31, 0.32), roughness=0.7, metallic=0.8)
GLASS = make_material("WindowGlass", (0.05, 0.08, 0.10), roughness=0.15)

LANDING_H = 3.0        # floor-to-floor height
LANDING_W = 2.4        # along the wall
LANDING_D = 1.2        # out from the wall
FLIGHTS = 3
STEPS = 10
RAIL_H = 1.05

# --- building wall with recessed windows ---
add_box("BuildingWall", (10.0, 0.6, 13.0), (0.0, 0.3, 5.5), BRICK)
for level in range(4):
    z = 1.4 + level * LANDING_H
    for side in (-3.4, 2.6):
        add_box("Window_%d_%s" % (level, "L" if side < 0 else "R"),
                (1.3, 0.12, 1.6), (side, -0.02, z), GLASS)

def build_railing(prefix, length, origin, axis, height=RAIL_H, posts=5):
    """Vertical posts plus mid and top rail running along +axis from origin."""
    for i in range(posts):
        t = i / (posts - 1)
        p = origin + axis * (length * t)
        add_pipe("%s_Post%d" % (prefix, i), 0.025, height,
                 (p.x, p.y, p.z + height * 0.5), STEEL)
    mid = origin + axis * (length * 0.5)
    angle = math.atan2(axis.y, axis.x)
    for j, frac in enumerate((0.55, 1.0)):
        add_pipe("%s_Rail%d" % (prefix, j), 0.03, length,
                 (mid.x, mid.y, mid.z + height * frac), STEEL,
                 rotation=(0.0, math.radians(90), angle))

def build_landing(index):
    z = LANDING_H * (index + 1)
    add_box("Landing_%d" % index, (LANDING_W, LANDING_D, 0.06),
            (0.0, -LANDING_D * 0.5, z), GRATE)
    for sx in (-LANDING_W * 0.5, LANDING_W * 0.5):
        add_pipe("LandingLeg_%d_%s" % (index, "L" if sx < 0 else "R"), 0.04, LANDING_H,
                 (sx, -LANDING_D + 0.15, z - LANDING_H * 0.5), STEEL)
    # outer edge plus one side rail; the wall side stays open
    build_railing("LandingRailOuter_%d" % index, LANDING_W,
                  Vector((-LANDING_W * 0.5, -LANDING_D, z)), Vector((1, 0, 0)))
    build_railing("LandingRailSide_%d" % index, LANDING_D,
                  Vector((-LANDING_W * 0.5, -LANDING_D, z)), Vector((0, 1, 0)), posts=3)

def build_flight(index):
    """Stair flight climbing one storey up to landing `index`."""
    bottom_z = LANDING_H * index
    rise = LANDING_H / STEPS
    run = 0.24
    direction = -1.0 if index % 2 else 1.0
    start = Vector(((LANDING_W * 0.5 - 0.25) * direction, -LANDING_D * 0.5, bottom_z))
    for s in range(STEPS):
        add_box("Tread_%d_%d" % (index, s), (0.85, run, 0.05),
                (start.x, start.y - run * s, bottom_z + rise * (s + 1)), GRATE)
    length = math.hypot(run * STEPS, LANDING_H)
    pitch = math.atan2(LANDING_H, run * STEPS)
    mid_y = start.y - run * STEPS * 0.5
    mid_z = bottom_z + LANDING_H * 0.5
    for sx in (-0.44, 0.44):
        tag = "A" if sx < 0 else "B"
        add_box("Stringer_%d_%s" % (index, tag), (0.06, length, 0.3),
                (start.x + sx, mid_y, mid_z), STEEL, rotation=(pitch, 0.0, 0.0))
        add_pipe("Handrail_%d_%s" % (index, tag), 0.03, length,
                 (start.x + sx, mid_y, mid_z + RAIL_H), STEEL,
                 rotation=(math.pi * 0.5 - pitch, 0.0, math.pi * 0.5))

for i in range(FLIGHTS):
    build_landing(i)
    build_flight(i)

# drop ladder hanging below the lowest landing
for sx in (-0.5, 0.5):
    add_box("DropLadderRail_%s" % ("L" if sx < 0 else "R"), (0.05, 0.05, 2.4),
            (sx, -LANDING_D + 0.2, 1.8), STEEL)
for r in range(7):
    add_pipe("DropLadderRung_%d" % r, 0.02, 1.0,
             (0.0, -LANDING_D + 0.2, 0.8 + r * 0.32), STEEL,
             rotation=(0.0, math.radians(90), 0.0))

add_box("Sidewalk", (16.0, 10.0, 0.15), (0.0, -4.0, -0.075),
        make_material("Concrete", (0.55, 0.54, 0.52), roughness=0.95))

# --- lighting and camera ---
bpy.ops.object.light_add(type='SUN', location=(-8.0, -10.0, 16.0))
sun = bpy.context.active_object
sun.name = "KeySun"
sun.data.energy = 4.0
sun.rotation_euler = (math.radians(52), 0.0, math.radians(-35))

bpy.ops.object.camera_add(location=(9.5, -13.0, 8.0))
cam = bpy.context.active_object
cam.name = "MainCamera"
cam.data.lens = 42
aim = Vector((0.0, -0.8, 5.5)) - cam.location
cam.rotation_euler = aim.to_track_quat('-Z', 'Y').to_euler()
bpy.context.scene.camera = cam
