import bpy
import math
from mathutils import Vector


def clear_scene():
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete(use_global=False)


def make_material(name, color, roughness=0.5, metallic=0.0, emission=0.0):
    mat = bpy.data.materials.new(name)
    mat.use_nodes = True
    bsdf = mat.node_tree.nodes["Principled BSDF"]
    bsdf.inputs["Base Color"].default_value = (color[0], color[1], color[2], 1.0)
    bsdf.inputs["Roughness"].default_value = roughness
    bsdf.inputs["Metallic"].default_value = metallic
    if emission > 0.0:
        bsdf.inputs["Emission Color"].default_value = (color[0], color[1], color[2], 1.0)
        bsdf.inputs["Emission Strength"].default_value = emission
    return mat


def add_box(name, dims, loc, mat, rot=(0.0, 0.0, 0.0)):
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=loc, rotation=rot)
    ob = bpy.context.active_object
    ob.name = name
    ob.scale = dims
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    ob.data.materials.append(mat)
    return ob


def add_cylinder(name, radius, depth, loc, mat, rot=(0.0, 0.0, 0.0), verts=24):
    bpy.ops.mesh.primitive_cylinder_add(vertices=verts, radius=radius, depth=depth,
                                        location=loc, rotation=rot)
    ob = bpy.context.active_object
    ob.name = name
    ob.data.materials.append(mat)
    return ob


def add_ball(name, radius, loc, mat):
    bpy.ops.mesh.primitive_uv_sphere_add(segments=24, ring_count=12, radius=radius, location=loc)
    ob = bpy.context.active_object
    ob.name = name
    bpy.ops.object.shade_smooth()
    ob.data.materials.append(mat)
    return ob


def look_at(ob, target):
    direction = Vector(target) - ob.location
    ob.rotation_euler = direction.to_track_quat('-Z', 'Y').to_euler()


clear_scene()

m_shell = make_material("CabinetShell", (0.05, 0.06, 0.09), roughness=0.45)
m_art = make_material("SideArt", (0.75, 0.10, 0.16), roughness=0.55)
m_trim = make_material("ChromeTrim", (0.72, 0.73, 0.76), roughness=0.28, metallic=1.0)
m_dark = make_material("MattePlastic", (0.02, 0.02, 0.03), roughness=0.7)
m_screen = make_material("ScreenGlow", (0.15, 0.45, 0.95), roughness=0.15, emission=3.0)
m_marquee = make_material("MarqueeLight", (1.0, 0.72, 0.22), roughness=0.3, emission=2.5)
m_panel = make_material("ControlPanelTop", (0.10, 0.12, 0.18), roughness=0.5)
m_red = make_material("ButtonRed", (0.85, 0.08, 0.08), roughness=0.3)
m_yellow = make_material("ButtonYellow", (0.95, 0.75, 0.05), roughness=0.3)
m_floor = make_material("FloorConcrete", (0.22, 0.22, 0.24), roughness=0.85)

bpy.ops.mesh.primitive_plane_add(size=6.0, location=(0.0, 0.0, 0.0))
floor = bpy.context.active_object
floor.name = "Floor"
floor.data.materials.append(m_floor)

add_box("Cabinet_Plinth", (0.74, 0.86, 0.10), (0.0, 0.0, 0.05), m_dark)
add_box("Cabinet_LowerBody", (0.70, 0.80, 0.85), (0.0, 0.0, 0.525), m_shell)
add_box("Cabinet_UpperBody", (0.70, 0.50, 0.85), (0.0, 0.15, 1.37), m_shell)
for side, x in (("L", -0.356), ("R", 0.356)):
    add_box("SideArt_" + side, (0.012, 0.76, 0.78), (x, 0.0, 0.53), m_art)

# Angled control panel; controls are placed in its local space.
panel_rot = (math.radians(12.0), 0.0, 0.0)
panel = add_box("ControlPanel", (0.68, 0.38, 0.05), (0.0, -0.23, 1.00), m_panel, panel_rot)
add_box("ControlPanel_Lip", (0.70, 0.04, 0.07), (0.0, -0.425, 0.96), m_trim)
P = panel.matrix_world.copy()


def on_panel(lx, ly, lz):
    return P @ Vector((lx, ly, lz))


add_cylinder("Joystick_Base", 0.055, 0.02, on_panel(-0.17, 0.0, 0.030), m_trim, panel_rot)
add_cylinder("Joystick_Shaft", 0.014, 0.09, on_panel(-0.17, 0.0, 0.080), m_trim, panel_rot)
add_ball("Joystick_Ball", 0.032, on_panel(-0.17, 0.0, 0.135), m_red)

for row, ly in enumerate((0.06, -0.045)):
    for col, lx in enumerate((0.02, 0.10, 0.18)):
        mat = m_red if row == 0 else m_yellow
        idx = row * 3 + col + 1
        add_cylinder("Button_Ring_%d" % idx, 0.026, 0.012,
                     on_panel(lx, ly, 0.028), m_trim, panel_rot)
        add_cylinder("Button_Cap_%d" % idx, 0.021, 0.014,
                     on_panel(lx, ly, 0.036), mat, panel_rot)

add_cylinder("StartButton_P1", 0.014, 0.012, on_panel(-0.24, 0.13, 0.030), m_yellow, panel_rot)
add_cylinder("StartButton_P2", 0.014, 0.012, on_panel(-0.11, 0.13, 0.030), m_yellow, panel_rot)

screen_rot = (math.radians(-6.0), 0.0, 0.0)
add_box("Screen_Bezel", (0.62, 0.06, 0.50), (0.0, -0.085, 1.32), m_dark, screen_rot)
add_box("Screen_Display", (0.54, 0.02, 0.42), (0.0, -0.125, 1.32), m_screen, screen_rot)

add_box("Marquee_Housing", (0.70, 0.07, 0.24), (0.0, -0.09, 1.71), m_dark,
        (math.radians(-8.0), 0.0, 0.0))
add_box("Marquee_Graphic", (0.64, 0.02, 0.19), (0.0, -0.125, 1.71), m_marquee,
        (math.radians(-8.0), 0.0, 0.0))
add_box("Cabinet_TopCap", (0.72, 0.52, 0.04), (0.0, 0.15, 1.81), m_trim)

for side, x in (("L", -0.185), ("R", 0.185)):
    add_cylinder("Speaker_" + side, 0.055, 0.03, (x, -0.075, 1.60), m_dark,
                 (math.radians(90.0), 0.0, 0.0), verts=32)

add_box("CoinDoor", (0.30, 0.04, 0.24), (0.0, -0.405, 0.46), m_trim)
add_box("CoinSlot_L", (0.035, 0.02, 0.012), (-0.07, -0.43, 0.53), m_dark)
add_box("CoinSlot_R", (0.035, 0.02, 0.012), (0.07, -0.43, 0.53), m_dark)
add_box("CoinReturn", (0.12, 0.02, 0.05), (0.0, -0.43, 0.38), m_dark)
add_box("KickPlate", (0.68, 0.03, 0.16), (0.0, -0.40, 0.20), m_dark)

bpy.ops.object.light_add(type='AREA', location=(1.0, -1.6, 2.7))
key = bpy.context.active_object
key.name = "KeyLight"
key.data.energy = 450.0
key.data.size = 2.5
look_at(key, (0.0, -0.2, 1.2))

bpy.ops.object.light_add(type='AREA', location=(-1.8, -0.6, 1.8))
fill = bpy.context.active_object
fill.name = "FillLight"
fill.data.energy = 120.0
fill.data.size = 2.0
look_at(fill, (0.0, 0.0, 1.0))

bpy.ops.object.camera_add(location=(1.75, -2.15, 1.65))
cam = bpy.context.active_object
cam.name = "SceneCamera"
cam.data.lens = 42.0
look_at(cam, (0.0, -0.15, 1.05))
bpy.context.scene.camera = cam
