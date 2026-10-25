import bpy
from math import radians
from mathutils import Vector

# Overall body proportions of a mirrorless-style camera, in metres.
BODY_W, BODY_D, BODY_H = 0.132, 0.052, 0.090
FRONT = -BODY_D / 2.0
BACK = BODY_D / 2.0
TOP = BODY_H / 2.0


def reset_scene():
    if bpy.context.object and bpy.context.object.mode != 'OBJECT':
        bpy.ops.object.mode_set(mode='OBJECT')
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete(use_global=False)
    for mesh in list(bpy.data.meshes):
        if mesh.users == 0:
            bpy.data.meshes.remove(mesh)


def material(name, color, roughness=0.5, metallic=0.0):
    mat = bpy.data.materials.get(name)
    if mat is not None:
        return mat
    mat = bpy.data.materials.new(name)
    mat.use_nodes = True
    bsdf = mat.node_tree.nodes["Principled BSDF"]
    bsdf.inputs["Base Color"].default_value = (color[0], color[1], color[2], 1.0)
    bsdf.inputs["Roughness"].default_value = roughness
    bsdf.inputs["Metallic"].default_value = metallic
    return mat


def finish(obj, name, mat, bevel=0.0, segments=2):
    obj.name = name
    obj.data.name = name
    obj.data.materials.append(mat)
    if bevel > 0.0:
        mod = obj.modifiers.new("Bevel", 'BEVEL')
        mod.width = bevel
        mod.segments = segments
        mod.limit_method = 'ANGLE'
        mod.angle_limit = radians(40.0)
    return obj


def box(name, size, location, mat, bevel=0.0, rotation=(0.0, 0.0, 0.0)):
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=location, rotation=rotation)
    obj = bpy.context.active_object
    obj.scale = size
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    return finish(obj, name, mat, bevel)


def cyl(name, radius, depth, location, mat, rotation=(0.0, 0.0, 0.0), verts=32, bevel=0.0):
    bpy.ops.mesh.primitive_cylinder_add(vertices=verts, radius=radius, depth=depth,
                                        location=location, rotation=rotation)
    return finish(bpy.context.active_object, name, mat, bevel)


def build_body(mats):
    box("Body_Shell", (BODY_W, BODY_D, BODY_H), (0.0, 0.0, 0.0), mats['body'], bevel=0.006)
    # Right-hand grip bulge, generously beveled so it reads as a moulded handle.
    box("Hand_Grip", (0.028, 0.062, 0.086), (BODY_W / 2.0 - 0.004, -0.006, -0.002),
        mats['rubber'], bevel=0.012)
    box("Thumb_Rest", (0.016, 0.012, 0.030), (BODY_W / 2.0 - 0.010, BACK + 0.002, 0.014),
        mats['rubber'], bevel=0.005)
    box("Prism_Hump", (0.046, 0.042, 0.026), (0.0, 0.002, TOP + 0.012), mats['body'], bevel=0.007)
    box("Viewfinder_Eyepiece", (0.030, 0.012, 0.020), (0.0, BACK + 0.005, TOP - 0.002),
        mats['rubber'], bevel=0.004)
    box("Rear_Screen", (0.072, 0.004, 0.048), (-0.014, BACK + 0.002, -0.006), mats['glass'])
    box("Name_Plate", (0.030, 0.003, 0.008), (-0.040, FRONT - 0.001, TOP - 0.014), mats['chrome'])
    for side, x in (("L", -BODY_W / 2.0 - 0.002), ("R", BODY_W / 2.0 + 0.002)):
        box("Strap_Lug_" + side, (0.006, 0.014, 0.010), (x, -0.004, TOP - 0.010),
            mats['chrome'], bevel=0.002)


def build_lens(mats):
    y = FRONT
    cyl("Lens_Mount", 0.031, 0.010, (0.0, y - 0.005, 0.0), mats['chrome'],
        rotation=(radians(90), 0, 0))
    cyl("Lens_Barrel", 0.027, 0.030, (0.0, y - 0.025, 0.0), mats['body'],
        rotation=(radians(90), 0, 0))
    cyl("Zoom_Ring", 0.029, 0.018, (0.0, y - 0.049, 0.0), mats['rubber'],
        rotation=(radians(90), 0, 0), verts=48, bevel=0.002)
    cyl("Focus_Ring", 0.028, 0.012, (0.0, y - 0.064, 0.0), mats['rubber'],
        rotation=(radians(90), 0, 0), verts=48, bevel=0.002)
    cyl("Lens_Front_Ring", 0.030, 0.008, (0.0, y - 0.074, 0.0), mats['chrome'],
        rotation=(radians(90), 0, 0))
    cyl("Lens_Glass", 0.024, 0.004, (0.0, y - 0.076, 0.0), mats['glass'],
        rotation=(radians(90), 0, 0), verts=48)


def build_top_controls(mats):
    z = TOP
    cyl("Mode_Dial", 0.014, 0.009, (0.040, 0.012, z + 0.004), mats['dial'], verts=24, bevel=0.001)
    cyl("Exposure_Dial", 0.012, 0.008, (-0.040, 0.012, z + 0.003), mats['dial'], verts=24, bevel=0.001)
    cyl("Shutter_Collar", 0.009, 0.005, (0.040, -0.016, z + 0.002), mats['chrome'], verts=24)
    cyl("Shutter_Button", 0.006, 0.005, (0.040, -0.016, z + 0.006), mats['accent'], verts=24,
        bevel=0.001)
    cyl("Front_Command_Dial", 0.010, 0.006, (0.058, -0.024, z - 0.006), mats['dial'],
        rotation=(0, radians(90), 0), verts=24)
    box("Power_Lever", (0.018, 0.006, 0.004), (0.019, -0.012, z + 0.003), mats['dial'], bevel=0.001)
    box("Hotshoe_Base", (0.022, 0.018, 0.004), (0.0, 0.002, z + 0.027), mats['chrome'])
    for side, x in (("L", -0.011), ("R", 0.011)):
        box("Hotshoe_Rail_" + side, (0.003, 0.018, 0.004), (x, 0.002, z + 0.030), mats['chrome'])
    cyl("Movie_Button", 0.004, 0.004, (0.062, 0.004, z + 0.001), mats['accent'], verts=16)


def add_lighting():
    sun_data = bpy.data.lights.new("Key_Sun", type='SUN')
    sun_data.energy = 3.5
    sun = bpy.data.objects.new("Key_Sun", sun_data)
    sun.rotation_euler = (radians(55), radians(12), radians(-40))
    bpy.context.collection.objects.link(sun)

    fill_data = bpy.data.lights.new("Fill_Area", type='AREA')
    fill_data.energy = 60.0
    fill_data.size = 0.8
    fill = bpy.data.objects.new("Fill_Area", fill_data)
    fill.location = (-0.45, -0.40, 0.30)
    fill.rotation_euler = (radians(60), 0.0, radians(-50))
    bpy.context.collection.objects.link(fill)


def add_camera(location, target, lens=55.0):
    cam_data = bpy.data.cameras.new("Scene_Camera")
    cam_data.lens = lens
    cam = bpy.data.objects.new("Scene_Camera", cam_data)
    cam.location = location
    direction = Vector(target) - Vector(location)
    cam.rotation_euler = direction.to_track_quat('-Z', 'Y').to_euler()
    bpy.context.collection.objects.link(cam)
    bpy.context.scene.camera = cam
    return cam


def main():
    reset_scene()
    mats = {
        'body': material("Camera_Body", (0.045, 0.047, 0.050), roughness=0.45),
        'rubber': material("Grip_Rubber", (0.020, 0.020, 0.022), roughness=0.85),
        'chrome': material("Chrome_Trim", (0.72, 0.73, 0.75), roughness=0.25, metallic=1.0),
        'dial': material("Dial_Metal", (0.30, 0.31, 0.33), roughness=0.35, metallic=0.9),
        'glass': material("Optical_Glass", (0.02, 0.05, 0.09), roughness=0.08),
        'accent': material("Accent_Red", (0.55, 0.05, 0.05), roughness=0.4),
    }
    build_body(mats)
    build_lens(mats)
    build_top_controls(mats)

    box("Studio_Backdrop", (1.2, 1.2, 0.006), (0.0, 0.10, -BODY_H / 2.0 - 0.003),
        material("Backdrop_Grey", (0.32, 0.33, 0.34), roughness=0.7))

    add_lighting()
    add_camera((0.30, -0.32, 0.17), (0.0, -0.030, 0.005))


main()
