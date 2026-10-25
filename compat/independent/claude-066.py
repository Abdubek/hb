import bpy
import math
from mathutils import Vector


def clear_scene():
    if bpy.context.object and bpy.context.object.mode != 'OBJECT':
        bpy.ops.object.mode_set(mode='OBJECT')
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete(use_global=False)
    for coll in (bpy.data.meshes, bpy.data.materials, bpy.data.cameras, bpy.data.lights):
        for block in list(coll):
            if block.users == 0:
                coll.remove(block)


def new_material(name, color, roughness=0.5, metallic=0.0):
    mat = bpy.data.materials.new(name)
    mat.use_nodes = True
    bsdf = mat.node_tree.nodes["Principled BSDF"]
    bsdf.inputs["Base Color"].default_value = (color[0], color[1], color[2], 1.0)
    bsdf.inputs["Roughness"].default_value = roughness
    bsdf.inputs["Metallic"].default_value = metallic
    return mat


def add_box(name, dims, loc, mat=None, rot=(0.0, 0.0, 0.0)):
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=loc, rotation=rot)
    ob = bpy.context.object
    ob.name = name
    ob.scale = dims
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    if mat:
        ob.data.materials.append(mat)
    return ob


def add_cylinder(name, radius, depth, loc, mat=None, rot=(0.0, 0.0, 0.0), verts=28):
    bpy.ops.mesh.primitive_cylinder_add(radius=radius, depth=depth, vertices=verts,
                                        location=loc, rotation=rot)
    ob = bpy.context.object
    ob.name = name
    if mat:
        ob.data.materials.append(mat)
    return ob


def add_dome(name, radius, squash, loc, mat=None):
    bpy.ops.mesh.primitive_uv_sphere_add(radius=radius, segments=24, ring_count=12, location=loc)
    ob = bpy.context.object
    ob.name = name
    ob.scale = squash
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    if mat:
        ob.data.materials.append(mat)
    return ob


def bevel(ob, width=0.008, segments=2):
    mod = ob.modifiers.new("Bevel", 'BEVEL')
    mod.width = width
    mod.segments = segments
    mod.limit_method = 'ANGLE'
    mod.angle_limit = math.radians(40.0)
    return mod


def add_camera(loc, target, lens=48.0):
    cam = bpy.data.cameras.new("MeterCam")
    cam.lens = lens
    ob = bpy.data.objects.new("Camera", cam)
    bpy.context.collection.objects.link(ob)
    ob.location = loc
    direction = Vector(target) - Vector(loc)
    ob.rotation_euler = direction.to_track_quat('-Z', 'Y').to_euler()
    bpy.context.scene.camera = ob
    return ob


clear_scene()

asphalt = new_material("Asphalt", (0.045, 0.045, 0.05), roughness=0.92)
concrete = new_material("Concrete", (0.62, 0.60, 0.56), roughness=0.85)
curb_paint = new_material("CurbPaint_Yellow", (0.72, 0.55, 0.05), roughness=0.6)
steel = new_material("Steel_Housing", (0.20, 0.24, 0.26), roughness=0.38, metallic=0.85)
dark_metal = new_material("Metal_Dark", (0.07, 0.075, 0.08), roughness=0.45, metallic=0.7)
glass = new_material("Display_Glass", (0.02, 0.05, 0.045), roughness=0.12)
lcd = new_material("LCD_Screen", (0.35, 0.72, 0.55), roughness=0.3)
chrome = new_material("Chrome_Trim", (0.78, 0.79, 0.80), roughness=0.15, metallic=1.0)
label = new_material("Label_White", (0.86, 0.86, 0.83), roughness=0.7)

# --- street: road below, curb stone, sidewalk above -------------------------
add_box("Asphalt_Road", (9.0, 3.2, 0.30), (0.0, -1.6, -0.15), asphalt)
add_box("Sidewalk_Slab", (9.0, 3.0, 0.16), (0.0, 1.6, 0.08), concrete)
curb = add_box("Curb_Stone", (9.0, 0.24, 0.50), (0.0, 0.02, -0.09), concrete)
bevel(curb, 0.02, 2)
add_box("Curb_Paint_Stripe", (9.0, 0.012, 0.16), (0.0, -0.106, 0.04), curb_paint)
for i, x in enumerate((-3.0, 0.9, 3.6)):
    add_box("Sidewalk_Joint_%02d" % i, (0.02, 3.0, 0.01), (x, 1.6, 0.161), concrete)

# --- meter post -------------------------------------------------------------
POST_Y = 0.62
base = add_cylinder("Meter_BasePlate", 0.13, 0.06, (0.0, POST_Y, 0.19), dark_metal)
bevel(base, 0.01, 2)
add_cylinder("Meter_Pole", 0.046, 1.02, (0.0, POST_Y, 0.73), steel)
add_cylinder("Pole_Collar", 0.062, 0.05, (0.0, POST_Y, 1.21), chrome)
for i, z in enumerate((0.42, 0.86)):
    add_cylinder("Pole_Rib_%02d" % i, 0.052, 0.018, (0.0, POST_Y, z), dark_metal)

# --- meter head -------------------------------------------------------------
HEAD_Z = 1.44
head = add_box("Meter_Head", (0.25, 0.17, 0.42), (0.0, POST_Y, HEAD_Z), steel)
bevel(head, 0.018, 3)
add_dome("Head_Dome", 0.125, (1.0, 0.70, 0.52), (0.0, POST_Y, HEAD_Z + 0.21), steel)
add_box("Head_Bezel", (0.19, 0.02, 0.15), (0.0, POST_Y - 0.086, HEAD_Z + 0.09), chrome)
add_box("Display_Glass", (0.165, 0.012, 0.125), (0.0, POST_Y - 0.094, HEAD_Z + 0.09), glass)
add_box("Display_LCD", (0.145, 0.006, 0.10), (0.0, POST_Y - 0.098, HEAD_Z + 0.09), lcd)
add_box("Coin_Slot", (0.055, 0.022, 0.014), (0.06, POST_Y - 0.086, HEAD_Z + 0.185), dark_metal)
add_box("Card_Slot", (0.012, 0.05, 0.016), (0.128, POST_Y, HEAD_Z + 0.05), dark_metal)
add_box("Coin_Return_Cup", (0.06, 0.03, 0.03), (-0.06, POST_Y - 0.082, HEAD_Z - 0.16), dark_metal)
add_box("Meter_ID_Plate", (0.14, 0.008, 0.05), (0.0, POST_Y - 0.09, HEAD_Z - 0.08), label)
for i, x in enumerate((-0.055, 0.0, 0.055)):
    add_cylinder("Keypad_Button_%02d" % i, 0.016, 0.014, (x, POST_Y - 0.088, HEAD_Z - 0.015),
                 chrome, rot=(math.pi / 2.0, 0.0, 0.0), verts=16)
add_box("Rate_Decal", (0.11, 0.006, 0.09), (0.0, POST_Y + 0.089, HEAD_Z + 0.06), label)

# --- lighting and camera ----------------------------------------------------
sun_data = bpy.data.lights.new("Sun", type='SUN')
sun_data.energy = 4.0
sun_data.angle = math.radians(3.0)
sun = bpy.data.objects.new("Sun", sun_data)
bpy.context.collection.objects.link(sun)
sun.location = (3.0, -4.0, 6.0)
sun.rotation_euler = (math.radians(52.0), 0.0, math.radians(38.0))

fill_data = bpy.data.lights.new("Fill", type='AREA')
fill_data.energy = 90.0
fill_data.size = 3.0
fill = bpy.data.objects.new("Fill_Light", fill_data)
bpy.context.collection.objects.link(fill)
fill.location = (-2.4, -2.6, 2.6)
fill.rotation_euler = Vector((0.0, 0.5, 1.3) ).to_track_quat('Z', 'Y').to_euler()

world = bpy.data.worlds.new("MeterWorld")
world.use_nodes = True
world.node_tree.nodes["Background"].inputs["Color"].default_value = (0.35, 0.42, 0.52, 1.0)
world.node_tree.nodes["Background"].inputs["Strength"].default_value = 0.7
bpy.context.scene.world = world

add_camera((1.85, -2.35, 1.85), (0.0, 0.45, 1.28), lens=52.0)
