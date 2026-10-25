import bpy
import math
from mathutils import Vector


def clear_scene():
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete(use_global=False)
    for coll in (bpy.data.meshes, bpy.data.materials):
        for block in list(coll):
            if block.users == 0:
                coll.remove(block)


def make_material(name, color, roughness=0.5, metallic=0.0, emit=0.0):
    mat = bpy.data.materials.new(name)
    mat.use_nodes = True
    bsdf = mat.node_tree.nodes["Principled BSDF"]
    bsdf.inputs["Base Color"].default_value = (color[0], color[1], color[2], 1.0)
    bsdf.inputs["Roughness"].default_value = roughness
    bsdf.inputs["Metallic"].default_value = metallic
    if emit > 0.0:
        bsdf.inputs["Emission Color"].default_value = (color[0], color[1], color[2], 1.0)
        bsdf.inputs["Emission Strength"].default_value = emit
    return mat


def add_box(name, size, location, material, rotation=(0.0, 0.0, 0.0)):
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=location, rotation=rotation)
    obj = bpy.context.object
    obj.name = name
    obj.scale = size
    obj.data.materials.append(material)
    return obj


def add_cylinder(name, radius, depth, location, material, rotation=(0.0, 0.0, 0.0), verts=20):
    bpy.ops.mesh.primitive_cylinder_add(radius=radius, depth=depth, vertices=verts,
                                        location=location, rotation=rotation)
    obj = bpy.context.object
    obj.name = name
    obj.data.materials.append(material)
    return obj


def build_rail(tag, y, length, material):
    """Flat-bottom rail approximated by foot / web / head slabs."""
    add_box("Rail_%s_Foot" % tag, (length, 0.15, 0.03), (0.0, y, 0.175), material)
    add_box("Rail_%s_Web" % tag, (length, 0.035, 0.10), (0.0, y, 0.24), material)
    add_box("Rail_%s_Head" % tag, (length, 0.07, 0.04), (0.0, y, 0.31), material)


def add_lamp(tag, z, color, x_face, backing, hood_mat):
    lens = make_material("MAT_Lens_%s" % tag, color, roughness=0.15, emit=6.0)
    add_cylinder("Lamp_%s_Lens" % tag, 0.13, 0.06, (x_face - 0.04, backing, z), lens,
                 rotation=(0.0, math.pi / 2.0, 0.0), verts=24)
    bpy.ops.mesh.primitive_cone_add(radius1=0.19, radius2=0.15, depth=0.22, vertices=20,
                                    location=(x_face - 0.14, backing, z),
                                    rotation=(0.0, -math.pi / 2.0, 0.0))
    hood = bpy.context.object
    hood.name = "Lamp_%s_Hood" % tag
    hood.data.materials.append(hood_mat)


def aim(obj, target):
    direction = Vector(target) - obj.location
    obj.rotation_euler = direction.to_track_quat('-Z', 'Y').to_euler()


clear_scene()

ballast_mat = make_material("MAT_Ballast", (0.34, 0.32, 0.30), roughness=0.95)
sleeper_mat = make_material("MAT_Sleeper", (0.19, 0.14, 0.10), roughness=0.9)
rail_mat = make_material("MAT_Rail_Steel", (0.48, 0.48, 0.5), roughness=0.35, metallic=1.0)
signal_mat = make_material("MAT_Signal_Grey", (0.16, 0.17, 0.18), roughness=0.6, metallic=0.4)
galv_mat = make_material("MAT_Galvanised", (0.62, 0.63, 0.65), roughness=0.45, metallic=0.9)
concrete_mat = make_material("MAT_Concrete", (0.62, 0.61, 0.58), roughness=0.9)
ground_mat = make_material("MAT_Ground", (0.24, 0.28, 0.16), roughness=1.0)

TRACK_LEN = 14.0
GAUGE = 1.435

add_box("Ground", (26.0, 20.0, 0.08), (0.0, 0.0, -0.04), ground_mat)
add_box("BallastBed", (TRACK_LEN, 3.6, 0.3), (0.0, 0.0, 0.07), ballast_mat)

# --- sleepers and rails ---------------------------------------------------
spacing = 0.7
count = int(TRACK_LEN / spacing)
for i in range(count):
    x = -TRACK_LEN / 2.0 + spacing * (i + 0.5)
    add_box("Sleeper_%02d" % i, (0.26, 2.6, 0.16), (x, 0.0, 0.24), sleeper_mat)

for tag, y in (("L", GAUGE / 2.0), ("R", -GAUGE / 2.0)):
    build_rail(tag, y, TRACK_LEN, rail_mat)

# --- signal structure -----------------------------------------------------
SIG_X = 2.0
SIG_Y = -2.35
MAST_TOP = 4.3

add_box("SignalFoundation", (0.8, 0.8, 0.4), (SIG_X, SIG_Y, 0.18), concrete_mat)
add_cylinder("SignalMast", 0.09, MAST_TOP, (SIG_X, SIG_Y, 0.38 + MAST_TOP / 2.0), signal_mat, verts=16)
add_cylinder("MastCollar", 0.14, 0.12, (SIG_X, SIG_Y, 0.44), galv_mat, verts=16)

# signal head faces -X, toward approaching traffic
head_z = 3.55
add_box("SignalHead_Backplate", (0.06, 0.72, 1.5), (SIG_X + 0.05, SIG_Y, head_z), signal_mat)
add_box("SignalHead_Body", (0.22, 0.42, 1.4), (SIG_X - 0.06, SIG_Y, head_z), signal_mat)
add_box("SignalHead_Cap", (0.3, 0.46, 0.06), (SIG_X - 0.08, SIG_Y, head_z + 0.73), signal_mat)

for tag, dz, colour in (("Red", 0.48, (0.85, 0.05, 0.05)),
                        ("Amber", 0.0, (0.9, 0.45, 0.02)),
                        ("Green", -0.48, (0.05, 0.7, 0.2))):
    add_lamp(tag, head_z + dz, colour, SIG_X - 0.17, SIG_Y, signal_mat)

add_box("SignalIdentPlate", (0.04, 0.3, 0.42), (SIG_X - 0.2, SIG_Y + 0.62, 2.6), concrete_mat)

# --- maintenance ladder ---------------------------------------------------
for tag, dy in (("L", 0.22), ("R", -0.22)):
    add_cylinder("LadderRail_%s" % tag, 0.025, 2.9, (SIG_X + 0.3, SIG_Y + dy, 1.85), galv_mat, verts=10)
rung_z = 0.6
while rung_z < 3.2:
    add_cylinder("LadderRung_%02d" % int(rung_z * 10), 0.018, 0.44,
                 (SIG_X + 0.3, SIG_Y, rung_z), galv_mat,
                 rotation=(math.pi / 2.0, 0.0, 0.0), verts=8)
    rung_z += 0.32

# --- lineside equipment ---------------------------------------------------
add_box("RelayCabinet", (0.7, 0.5, 1.0), (-0.6, -2.6, 0.5), galv_mat)
add_box("RelayCabinet_Roof", (0.8, 0.6, 0.06), (-0.6, -2.6, 1.03), signal_mat)
add_box("CableTrough", (5.0, 0.32, 0.26), (0.4, -2.05, 0.13), concrete_mat)

# --- lighting and camera --------------------------------------------------
bpy.ops.object.light_add(type='SUN', location=(6.0, -8.0, 10.0))
sun = bpy.context.object
sun.name = "KeySun"
sun.data.energy = 3.0
sun.rotation_euler = (math.radians(55.0), 0.0, math.radians(40.0))

bpy.ops.object.light_add(type='AREA', location=(-6.0, 5.0, 6.0))
fill = bpy.context.object
fill.name = "FillArea"
fill.data.energy = 500.0
fill.data.size = 7.0
aim(fill, (0.0, -1.0, 1.5))

bpy.ops.object.camera_add(location=(-6.5, -8.5, 4.6))
cam = bpy.context.object
cam.name = "SceneCamera"
cam.data.lens = 45.0
aim(cam, (1.0, -0.8, 2.1))
bpy.context.scene.camera = cam
