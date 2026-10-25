import bpy
import math
from mathutils import Vector

# ---------------------------------------------------------------- utilities

def clear_scene():
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete(use_global=False)
    for coll in (bpy.data.meshes, bpy.data.materials, bpy.data.cameras, bpy.data.lights):
        for item in list(coll):
            if item.users == 0:
                coll.remove(item)


def make_material(name, color, roughness=0.5, metallic=0.0):
    mat = bpy.data.materials.new(name)
    mat.use_nodes = True
    bsdf = mat.node_tree.nodes.get("Principled BSDF")
    if bsdf:
        bsdf.inputs["Base Color"].default_value = (color[0], color[1], color[2], 1.0)
        bsdf.inputs["Roughness"].default_value = roughness
        bsdf.inputs["Metallic"].default_value = metallic
    return mat


def finish(obj, name, material, parent=None, smooth=False):
    obj.name = name
    obj.data.name = name + "_mesh"
    obj.data.materials.append(material)
    if smooth:
        for poly in obj.data.polygons:
            poly.use_smooth = True
    if parent is not None:
        obj.parent = parent
    return obj


def add_cylinder(name, radius, depth, location, material, rotation=(0, 0, 0),
                 verts=48, parent=None, smooth=False):
    bpy.ops.mesh.primitive_cylinder_add(vertices=verts, radius=radius, depth=depth,
                                        location=location, rotation=rotation)
    return finish(bpy.context.active_object, name, material, parent, smooth)


def add_box(name, size, location, material, rotation=(0, 0, 0), parent=None):
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=location, rotation=rotation)
    obj = bpy.context.active_object
    obj.scale = size
    return finish(obj, name, material, parent)


def add_torus(name, major, minor, location, material, parent=None):
    bpy.ops.mesh.primitive_torus_add(major_radius=major, minor_radius=minor,
                                     major_segments=48, minor_segments=8,
                                     location=location)
    return finish(bpy.context.active_object, name, material, parent, smooth=True)


# ---------------------------------------------------------------- dimensions

SKIRT_H = 0.40
BODY_R = 2.20
BODY_H = 5.00
BODY_TOP = SKIRT_H + BODY_H          # 5.40
DOME_H = 1.00
RAIL_R = 1.85
RAIL_TOP = BODY_TOP + 1.60
LADDER_X = BODY_R + 0.34

clear_scene()

steel = make_material("MAT_TankSteel", (0.72, 0.74, 0.76), roughness=0.35, metallic=0.9)
dark_steel = make_material("MAT_DarkSteel", (0.28, 0.30, 0.33), roughness=0.45, metallic=0.8)
yellow = make_material("MAT_SafetyYellow", (0.85, 0.62, 0.06), roughness=0.55)
concrete = make_material("MAT_Concrete", (0.52, 0.51, 0.48), roughness=0.9)
grating = make_material("MAT_Grating", (0.40, 0.42, 0.44), roughness=0.6, metallic=0.7)

root = bpy.data.objects.new("StorageTankAssembly", None)
bpy.context.collection.objects.link(root)

# ---------------------------------------------------------------- ground + tank

bpy.ops.mesh.primitive_plane_add(size=24.0, location=(0, 0, 0))
finish(bpy.context.active_object, "GroundPad", concrete)

add_cylinder("TankSkirt", BODY_R + 0.15, SKIRT_H, (0, 0, SKIRT_H / 2), dark_steel, parent=root)
add_cylinder("TankShell", BODY_R, BODY_H, (0, 0, SKIRT_H + BODY_H / 2), steel,
             parent=root, smooth=True)

# two weld/stiffener rings around the shell
for i, z in enumerate((SKIRT_H + BODY_H * 0.35, SKIRT_H + BODY_H * 0.7)):
    add_torus("ShellRing_%02d" % (i + 1), BODY_R + 0.02, 0.05, (0, 0, z), dark_steel, root)

# dished roof: squashed sphere, its lower half is hidden inside the shell
bpy.ops.mesh.primitive_uv_sphere_add(segments=48, ring_count=16, radius=BODY_R,
                                     location=(0, 0, BODY_TOP))
dome = bpy.context.active_object
dome.scale = (1.0, 1.0, DOME_H / BODY_R)
finish(dome, "TankRoofDome", steel, root, smooth=True)

# roof fittings
add_cylinder("RoofVentStack", 0.16, 0.70, (0, 0, BODY_TOP + DOME_H + 0.25), dark_steel,
             parent=root, verts=24, smooth=True)
add_cylinder("RoofManway", 0.40, 0.16, (0.85, 0.0, BODY_TOP + DOME_H * 0.9), dark_steel,
             parent=root, verts=32)

# outlet nozzle + short pipe run at grade
add_cylinder("OutletNozzle", 0.18, 0.9, (BODY_R + 0.25, 0, SKIRT_H + 0.55), dark_steel,
             rotation=(0, math.pi / 2, 0), parent=root, verts=24, smooth=True)
add_cylinder("OutletFlange", 0.28, 0.08, (BODY_R + 0.66, 0, SKIRT_H + 0.55), dark_steel,
             rotation=(0, math.pi / 2, 0), parent=root, verts=24)

# ---------------------------------------------------------------- access ladder

ladder = bpy.data.objects.new("AccessLadder", None)
bpy.context.collection.objects.link(ladder)
ladder.parent = root

ladder_h = BODY_TOP + 0.55
for side, y in (("L", 0.26), ("R", -0.26)):
    add_cylinder("LadderStringer_%s" % side, 0.045, ladder_h,
                 (LADDER_X, y, ladder_h / 2), yellow, verts=12, parent=ladder, smooth=True)

rung_count = int((ladder_h - 0.5) / 0.32)
for i in range(rung_count):
    z = 0.35 + i * 0.32
    add_cylinder("LadderRung_%02d" % (i + 1), 0.028, 0.52, (LADDER_X, 0, z), yellow,
                 rotation=(math.pi / 2, 0, 0), verts=10, parent=ladder, smooth=True)

# safety cage hoops on the upper part of the climb
for i in range(4):
    z = 2.6 + i * 0.8
    hoop = add_torus("LadderCageHoop_%02d" % (i + 1), 0.42, 0.025,
                     (LADDER_X + 0.20, 0, z), yellow, ladder)
    hoop.rotation_euler = (0, math.pi / 2, 0)

# ---------------------------------------------------------------- roof platform + rail

rail = bpy.data.objects.new("RoofSafetyRail", None)
bpy.context.collection.objects.link(rail)
rail.parent = root

# walkway ring on the roof, near the rail line
walk = add_torus("RoofWalkwayRing", RAIL_R, 0.06, (0, 0, BODY_TOP + 0.60), grating, rail)
walk.scale = (1.0, 1.0, 0.35)

post_count = 12
for i in range(post_count):
    ang = 2.0 * math.pi * i / post_count
    x, y = RAIL_R * math.cos(ang), RAIL_R * math.sin(ang)
    base_z = BODY_TOP + DOME_H * math.sqrt(max(0.0, 1.0 - (RAIL_R / BODY_R) ** 2))
    height = RAIL_TOP - base_z
    add_cylinder("RailPost_%02d" % (i + 1), 0.035, height, (x, y, base_z + height / 2),
                 yellow, verts=10, parent=rail, smooth=True)

add_torus("RailTopHoop", RAIL_R, 0.04, (0, 0, RAIL_TOP - 0.05), yellow, rail)
add_torus("RailMidHoop", RAIL_R, 0.032, (0, 0, RAIL_TOP - 0.60), yellow, rail)
add_torus("RailToeBoard", RAIL_R, 0.05, (0, 0, BODY_TOP + 0.72), dark_steel, rail)

# small landing platform where the ladder meets the roof
add_box("LadderLanding", (0.85, 0.75, 0.06), (LADDER_X - 0.15, 0, BODY_TOP + 0.58),
        grating, parent=rail)

# ---------------------------------------------------------------- camera + light

bpy.ops.object.camera_add(location=(10.5, -11.0, 7.6))
cam = bpy.context.active_object
cam.name = "SceneCamera"
cam.data.lens = 45.0
target = Vector((0.0, 0.0, 3.4))
cam.rotation_euler = (target - cam.location).to_track_quat('-Z', 'Y').to_euler()
bpy.context.scene.camera = cam

bpy.ops.object.light_add(type='SUN', location=(6, -8, 14))
sun = bpy.context.active_object
sun.name = "SunLight"
sun.data.energy = 4.0
sun.rotation_euler = (math.radians(52), 0.0, math.radians(35))

bpy.ops.object.light_add(type='AREA', location=(-9, 6, 9))
fill = bpy.context.active_object
fill.name = "FillLight"
fill.data.energy = 900.0
fill.data.size = 8.0
fill.rotation_euler = (Vector((0, 0, 3)) - fill.location).to_track_quat('-Z', 'Y').to_euler()

print("Storage tank scene built: %d objects" % len(bpy.context.scene.objects))
