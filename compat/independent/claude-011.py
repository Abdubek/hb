import bpy
import math
from mathutils import Vector


def reset_scene():
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete(use_global=False)
    for coll in (bpy.data.meshes, bpy.data.materials, bpy.data.lights, bpy.data.cameras):
        for item in list(coll):
            if item.users == 0:
                coll.remove(item)


def make_material(name, color, rough=0.5, metal=0.0, alpha=1.0, transmission=0.0, emit=0.0):
    m = bpy.data.materials.new(name)
    m.use_nodes = True
    bsdf = m.node_tree.nodes["Principled BSDF"]
    bsdf.inputs["Base Color"].default_value = (*color, 1.0)
    bsdf.inputs["Roughness"].default_value = rough
    bsdf.inputs["Metallic"].default_value = metal
    bsdf.inputs["Alpha"].default_value = alpha
    if transmission > 0.0 and "Transmission Weight" in bsdf.inputs:
        bsdf.inputs["Transmission Weight"].default_value = transmission
    if emit > 0.0:
        bsdf.inputs["Emission Color"].default_value = (*color, 1.0)
        bsdf.inputs["Emission Strength"].default_value = emit
    if alpha < 1.0:
        m.blend_method = 'BLEND'
    return m


def _finish(obj, name, material):
    obj.name = name
    obj.data.name = name + "_mesh"
    obj.data.materials.append(material)
    for poly in obj.data.polygons:
        poly.use_smooth = False
    return obj


def box(name, dims, loc, material, rot=(0.0, 0.0, 0.0)):
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=loc, rotation=rot)
    obj = bpy.context.active_object
    obj.scale = dims
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    return _finish(obj, name, material)


def cyl(name, radius, depth, loc, material, verts=12, rot=(0.0, 0.0, 0.0)):
    bpy.ops.mesh.primitive_cylinder_add(radius=radius, depth=depth, vertices=verts,
                                        location=loc, rotation=rot)
    return _finish(bpy.context.active_object, name, material)


def cone(name, r1, r2, depth, loc, material, verts=12):
    bpy.ops.mesh.primitive_cone_add(radius1=r1, radius2=r2, depth=depth,
                                    vertices=verts, location=loc)
    return _finish(bpy.context.active_object, name, material)


def build_body(shell, dark, chrome):
    box("Base_Housing", (0.26, 0.24, 0.05), (0.0, -0.02, 0.025), shell)
    cyl("Warming_Plate", 0.085, 0.012, (0.0, -0.05, 0.056), chrome, verts=16)
    box("Tower_Body", (0.26, 0.13, 0.40), (0.0, 0.135, 0.20), shell)
    box("Tower_Cap", (0.24, 0.12, 0.02), (0.0, 0.135, 0.41), dark)

    water = make_material("WaterWindow", (0.55, 0.72, 0.80), rough=0.1,
                          alpha=0.35, transmission=0.8)
    box("Reservoir_Window", (0.05, 0.012, 0.24), (0.09, 0.072, 0.24), water)
    for i in range(3):
        box("Reservoir_Tick_%d" % i, (0.03, 0.006, 0.004),
            (0.055, 0.072, 0.16 + i * 0.07), dark)


def build_brew_head(shell, dark):
    box("Brew_Head", (0.24, 0.16, 0.06), (0.0, 0.02, 0.36), shell)
    box("Brew_Head_Hinge", (0.20, 0.03, 0.05), (0.0, 0.085, 0.36), dark)
    cone("Filter_Basket", 0.075, 0.055, 0.07, (0.0, -0.01, 0.295),
         make_material("BasketPlastic", (0.20, 0.21, 0.23), rough=0.6), verts=12)
    cyl("Drip_Nozzle", 0.012, 0.02, (0.0, -0.01, 0.252), dark, verts=8)


def build_controls(dark):
    face_y = 0.068
    panel = make_material("PanelPlastic", (0.10, 0.10, 0.12), rough=0.4)
    box("Control_Panel", (0.10, 0.012, 0.09), (-0.075, face_y, 0.24), panel)

    display = make_material("Display", (0.20, 0.95, 0.75), rough=0.3, emit=3.0)
    box("Display_Screen", (0.07, 0.008, 0.028), (-0.075, face_y + 0.008, 0.265), display)

    colors = ((0.85, 0.15, 0.12), (0.90, 0.72, 0.15), (0.20, 0.55, 0.85))
    labels = ("Brew", "Warm", "Timer")
    for i, (col, label) in enumerate(zip(colors, labels)):
        btn_mat = make_material("Button_%s" % label, col, rough=0.35, emit=1.5)
        cyl("Button_%s" % label, 0.011, 0.012,
            (-0.105 + i * 0.03, face_y + 0.010, 0.222), btn_mat,
            verts=10, rot=(math.pi / 2.0, 0.0, 0.0))

    cyl("Power_Switch", 0.014, 0.014, (0.0, face_y + 0.008, 0.10), dark,
        verts=8, rot=(math.pi / 2.0, 0.0, 0.0))


def build_carafe():
    glass = make_material("CarafeGlass", (0.85, 0.88, 0.90), rough=0.08,
                          alpha=0.3, transmission=0.9)
    coffee = make_material("Coffee", (0.12, 0.05, 0.02), rough=0.2)
    lid = make_material("CarafeLid", (0.13, 0.13, 0.15), rough=0.5)

    cx, cy, base_z = 0.0, -0.05, 0.062
    cone("Carafe_Body", 0.070, 0.078, 0.155, (cx, cy, base_z + 0.0775), glass, verts=12)
    cyl("Carafe_Coffee", 0.066, 0.085, (cx, cy, base_z + 0.045), coffee, verts=12)
    cyl("Carafe_Lid", 0.080, 0.022, (cx, cy, base_z + 0.163), lid, verts=12)
    box("Carafe_Spout", (0.035, 0.030, 0.018), (cx, cy - 0.072, base_z + 0.160), lid,
        rot=(math.radians(-15.0), 0.0, 0.0))

    box("Handle_Upper", (0.020, 0.055, 0.018), (cx, cy + 0.078, base_z + 0.135), lid)
    box("Handle_Spine", (0.020, 0.018, 0.090), (cx, cy + 0.105, base_z + 0.095), lid)
    box("Handle_Lower", (0.020, 0.050, 0.018), (cx, cy + 0.075, base_z + 0.055), lid)


def build_environment():
    box("Counter", (1.2, 1.0, 0.04), (0.0, 0.0, -0.02),
        make_material("CounterTop", (0.78, 0.76, 0.72), rough=0.35))

    bpy.ops.object.light_add(type='AREA', location=(0.45, -0.55, 0.85))
    key = bpy.context.active_object
    key.name = "KeyLight"
    key.data.energy = 120.0
    key.data.size = 0.8
    key.rotation_euler = (math.radians(40.0), 0.0, math.radians(35.0))

    bpy.ops.object.light_add(type='POINT', location=(-0.6, -0.4, 0.5))
    fill = bpy.context.active_object
    fill.name = "FillLight"
    fill.data.energy = 15.0


def add_camera():
    loc = Vector((0.52, -0.62, 0.44))
    target = Vector((0.0, 0.0, 0.20))
    bpy.ops.object.camera_add(location=loc)
    cam = bpy.context.active_object
    cam.name = "SceneCamera"
    cam.data.lens = 50.0
    cam.data.clip_start = 0.01
    cam.rotation_euler = (target - loc).to_track_quat('-Z', 'Y').to_euler()
    bpy.context.scene.camera = cam


reset_scene()
SHELL = make_material("ShellPlastic", (0.88, 0.89, 0.90), rough=0.45)
DARK = make_material("DarkTrim", (0.09, 0.09, 0.11), rough=0.5)
CHROME = make_material("PlateChrome", (0.70, 0.71, 0.73), rough=0.25, metal=1.0)
build_environment()
build_body(SHELL, DARK, CHROME)
build_brew_head(SHELL, DARK)
build_controls(DARK)
build_carafe()
add_camera()
