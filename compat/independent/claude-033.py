import bpy
import bmesh
import math
from mathutils import Vector

ARM_LEN = 0.46          # hub centre -> motor centre
PROP_R = 0.15
BODY_Z = 0.30           # cruise height above the pad


def clear_scene():
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete(use_global=False)
    for coll in (bpy.data.meshes, bpy.data.materials, bpy.data.cameras, bpy.data.lights):
        for item in list(coll):
            if item.users == 0:
                coll.remove(item)


def material(name, color, rough=0.5, metallic=0.0, emit=None):
    mat = bpy.data.materials.new(name)
    mat.use_nodes = True
    bsdf = mat.node_tree.nodes["Principled BSDF"]
    bsdf.inputs["Base Color"].default_value = (*color, 1.0)
    bsdf.inputs["Roughness"].default_value = rough
    bsdf.inputs["Metallic"].default_value = metallic
    if emit is not None:
        bsdf.inputs["Emission Color"].default_value = (*emit, 1.0)
        bsdf.inputs["Emission Strength"].default_value = 6.0
    return mat


def box(name, size, loc, mat, rot=(0, 0, 0), bevel=0.0):
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=loc, rotation=rot)
    ob = bpy.context.active_object
    ob.name = name
    ob.scale = size
    ob.data.materials.append(mat)
    if bevel > 0.0:
        bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
        mod = ob.modifiers.new("Bevel", 'BEVEL')
        mod.width = bevel
        mod.segments = 2
    return ob


def cyl(name, radius, depth, loc, mat, rot=(0, 0, 0), verts=20):
    bpy.ops.mesh.primitive_cylinder_add(vertices=verts, radius=radius, depth=depth,
                                        location=loc, rotation=rot)
    ob = bpy.context.active_object
    ob.name = name
    ob.data.materials.append(mat)
    return ob


def sphere(name, radius, loc, mat, segs=20):
    bpy.ops.mesh.primitive_uv_sphere_add(segments=segs, ring_count=segs // 2,
                                         radius=radius, location=loc)
    ob = bpy.context.active_object
    ob.name = name
    ob.data.materials.append(mat)
    return ob


def blade_mesh(name, length):
    """Tapered flat blade whose root sits at the local origin, tip along +X."""
    mesh = bpy.data.meshes.new(name)
    bm = bmesh.new()
    bmesh.ops.create_cube(bm, size=1.0)
    for v in bm.verts:
        t = v.co.x + 0.5                      # 0 at root, 1 at tip
        v.co.x = t * length
        v.co.y *= 0.075 * (1.0 - 0.5 * t)     # chord narrows toward the tip
        v.co.z *= 0.012
    bm.to_mesh(mesh)
    bm.free()
    return mesh


def propeller(index, centre, spin_ccw, mat_blade, mat_hub):
    cx, cy, cz = centre
    cyl("Prop%d_Hub" % index, 0.026, 0.03, (cx, cy, cz + 0.012), mat_hub, verts=14)
    pitch = math.radians(14.0) * (1.0 if spin_ccw else -1.0)
    phase = math.radians(25.0 * index)
    for b in range(2):
        yaw = phase + b * math.pi
        ob = bpy.data.objects.new("Prop%d_Blade%d" % (index, b),
                                  blade_mesh("Prop%d_Blade%d_Mesh" % (index, b), PROP_R))
        ob.location = (cx + math.cos(yaw) * 0.022, cy + math.sin(yaw) * 0.022, cz + 0.012)
        ob.rotation_euler = (pitch, 0.0, yaw)
        ob.data.materials.append(mat_blade)
        bpy.context.collection.objects.link(ob)


def motor_stack(index, x, y, mat_metal, mat_dark):
    cyl("Motor%d_Can" % index, 0.036, 0.05, (x, y, BODY_Z + 0.025), mat_metal, verts=18)
    cyl("Motor%d_Mount" % index, 0.045, 0.012, (x, y, BODY_Z - 0.004), mat_dark, verts=18)


def add_camera(loc, target, lens=50):
    cam = bpy.data.objects.new("Camera", bpy.data.cameras.new("CameraData"))
    cam.data.lens = lens
    cam.location = loc
    cam.rotation_euler = (Vector(target) - Vector(loc)).to_track_quat('-Z', 'Y').to_euler()
    bpy.context.collection.objects.link(cam)
    bpy.context.scene.camera = cam


clear_scene()

MAT_SHELL = material("Shell_Grey", (0.28, 0.29, 0.32), rough=0.35)
MAT_DARK = material("Plastic_Dark", (0.045, 0.045, 0.05), rough=0.45)
MAT_CARBON = material("Carbon_Arm", (0.09, 0.09, 0.1), rough=0.28, metallic=0.35)
MAT_METAL = material("Motor_Alu", (0.66, 0.67, 0.7), rough=0.3, metallic=1.0)
MAT_BLADE = material("Prop_Blade", (0.12, 0.12, 0.14), rough=0.4)
MAT_GLASS = material("Lens_Glass", (0.02, 0.03, 0.05), rough=0.08, metallic=0.4)
MAT_BATT = material("Battery_Pack", (0.16, 0.13, 0.09), rough=0.6)
MAT_LED_G = material("Led_Green", (0.05, 0.5, 0.1), emit=(0.15, 1.0, 0.25))
MAT_LED_R = material("Led_Red", (0.5, 0.03, 0.03), emit=(1.0, 0.08, 0.05))
MAT_PAD = material("Landing_Pad", (0.34, 0.34, 0.36), rough=0.85)

box("Landing_Pad", (3.2, 3.2, 0.04), (0, 0, -0.02), MAT_PAD)
cyl("Pad_Ring", 0.62, 0.006, (0, 0, 0.004), MAT_DARK, verts=48)

box("Body_Core", (0.30, 0.22, 0.075), (0, 0, BODY_Z), MAT_SHELL, bevel=0.014)
box("Body_Canopy", (0.20, 0.16, 0.05), (0.01, 0, BODY_Z + 0.055), MAT_DARK, bevel=0.012)
box("Battery", (0.17, 0.13, 0.045), (-0.02, 0, BODY_Z - 0.055), MAT_BATT, bevel=0.006)
cyl("GPS_Puck", 0.035, 0.014, (-0.06, 0, BODY_Z + 0.088), MAT_SHELL, verts=18)
cyl("Antenna_Mast", 0.004, 0.09, (-0.12, 0, BODY_Z + 0.02), MAT_DARK,
    rot=(math.radians(35), 0, 0), verts=8)

sphere("Gimbal_Ball", 0.045, (0.15, 0.0, BODY_Z - 0.055), MAT_DARK)
cyl("Gimbal_Lens", 0.026, 0.03, (0.185, 0.0, BODY_Z - 0.058), MAT_GLASS,
    rot=(0, math.pi / 2, 0), verts=20)

for i, ang_deg in enumerate((45, 135, 225, 315)):
    a = math.radians(ang_deg)
    mx, my = math.cos(a) * ARM_LEN, math.sin(a) * ARM_LEN
    cyl("Arm%d" % i, 0.020, ARM_LEN - 0.06,
        (mx * 0.52, my * 0.52, BODY_Z),
        MAT_CARBON, rot=(0, math.pi / 2, a), verts=14)
    motor_stack(i, mx, my, MAT_METAL, MAT_DARK)
    propeller(i, (mx, my, BODY_Z + 0.055), spin_ccw=(i % 2 == 0),
              mat_blade=MAT_BLADE, mat_hub=MAT_METAL)
    led_mat = MAT_LED_G if ang_deg in (45, 315) else MAT_LED_R
    sphere("Nav_Led%d" % i, 0.011, (mx * 0.86, my * 0.86, BODY_Z - 0.028), led_mat, segs=12)
    # skid leg dropping from each arm to the pad
    cyl("Leg%d_Strut" % i, 0.009, 0.24,
        (mx * 0.72, my * 0.72, BODY_Z - 0.13), MAT_SHELL,
        rot=(math.radians(12) * math.sin(a), -math.radians(12) * math.cos(a), 0), verts=10)
    sphere("Leg%d_Foot" % i, 0.018, (mx * 0.78, my * 0.78, BODY_Z - 0.25), MAT_DARK, segs=12)

sun = bpy.data.objects.new("Sun", bpy.data.lights.new("SunData", type='SUN'))
sun.data.energy = 3.5
sun.location = (1.2, -1.6, 3.0)
sun.rotation_euler = (math.radians(42), math.radians(8), math.radians(30))
bpy.context.collection.objects.link(sun)

fill = bpy.data.objects.new("Fill_Light", bpy.data.lights.new("FillData", type='AREA'))
fill.data.energy = 90.0
fill.data.size = 2.0
fill.location = (-1.4, 1.2, 1.6)
fill.rotation_euler = (math.radians(-50), 0, math.radians(-40))
bpy.context.collection.objects.link(fill)

add_camera((1.05, -1.35, 0.85), (0.0, 0.0, 0.30), lens=55)
