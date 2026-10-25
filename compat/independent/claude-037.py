import bpy
import math
from mathutils import Vector, Euler

# ---------------------------------------------------------------- utilities

def reset_scene():
    for obj in list(bpy.data.objects):
        bpy.data.objects.remove(obj, do_unlink=True)
    for coll in (bpy.data.meshes, bpy.data.curves, bpy.data.materials,
                 bpy.data.cameras, bpy.data.lights):
        for item in list(coll):
            if item.users == 0:
                coll.remove(item)


def make_material(name, color, roughness=0.5, metallic=0.0):
    mat = bpy.data.materials.new(name)
    mat.use_nodes = True
    bsdf = mat.node_tree.nodes["Principled BSDF"]
    bsdf.inputs["Base Color"].default_value = (*color, 1.0)
    bsdf.inputs["Roughness"].default_value = roughness
    bsdf.inputs["Metallic"].default_value = metallic
    return mat


def _finish(obj, name, material, bevel=0.0, segments=3):
    obj.name = name
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    if material is not None:
        obj.data.materials.append(material)
    if bevel > 0.0:
        mod = obj.modifiers.new("Bevel", 'BEVEL')
        mod.width = bevel
        mod.segments = segments
        mod.limit_method = 'ANGLE'
    return obj


def box(name, dims, location, rotation=(0.0, 0.0, 0.0), material=None, bevel=0.0, segments=3):
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=location)
    obj = bpy.context.object
    obj.rotation_euler = Euler(rotation)
    obj.scale = dims
    return _finish(obj, name, material, bevel, segments)


def cylinder(name, radius, depth, location, rotation=(0.0, 0.0, 0.0), material=None, verts=28):
    bpy.ops.mesh.primitive_cylinder_add(radius=radius, depth=depth, vertices=verts,
                                        location=location, rotation=rotation)
    return _finish(bpy.context.object, name, material)


def add_camera(location, target, lens=55.0):
    cam_data = bpy.data.cameras.new("ToasterCam")
    cam_data.lens = lens
    cam = bpy.data.objects.new("Camera", cam_data)
    bpy.context.collection.objects.link(cam)
    cam.location = location
    cam.rotation_euler = (Vector(location) - Vector(target)).to_track_quat('Z', 'Y').to_euler()
    bpy.context.scene.camera = cam
    return cam


# ---------------------------------------------------------------- materials

reset_scene()

MAT_COUNTER = make_material("Counter.Stone", (0.72, 0.70, 0.67), roughness=0.4)
MAT_STEEL = make_material("Toaster.Steel", (0.78, 0.79, 0.80), roughness=0.28, metallic=0.95)
MAT_TRIM = make_material("Toaster.Trim", (0.14, 0.14, 0.15), roughness=0.45)
MAT_SLOT = make_material("Toaster.SlotInterior", (0.02, 0.02, 0.02), roughness=0.85)
MAT_CHROME = make_material("Toaster.Chrome", (0.88, 0.88, 0.90), roughness=0.12, metallic=1.0)
MAT_ACCENT = make_material("Toaster.Accent", (0.70, 0.10, 0.08), roughness=0.35)

X_AXIS = (0.0, math.radians(90.0), 0.0)
SIDE_X = 0.150  # right-hand control face

# ---------------------------------------------------------------- body

box("Counter.Top", (1.4, 1.0, 0.02), (0.0, 0.0, -0.01), material=MAT_COUNTER)

box("Toaster.Body", (0.300, 0.180, 0.170), (0.0, 0.0, 0.100), material=MAT_STEEL,
    bevel=0.016, segments=4)
box("Toaster.TopPlate", (0.278, 0.158, 0.014), (0.0, 0.0, 0.186), material=MAT_TRIM,
    bevel=0.005)
box("Toaster.BaseSkirt", (0.292, 0.172, 0.016), (0.0, 0.0, 0.023), material=MAT_TRIM,
    bevel=0.004)

for i, (fx, fy) in enumerate([(0.115, 0.062), (-0.115, 0.062), (0.115, -0.062), (-0.115, -0.062)]):
    cylinder("Toaster.Foot.%d" % (i + 1), 0.014, 0.016, (fx, fy, 0.008),
             material=MAT_TRIM, verts=16)

# ---------------------------------------------------------------- bread slots

for i, sy in enumerate((0.042, -0.042)):
    box("Toaster.SlotRim.%d" % (i + 1), (0.224, 0.040, 0.010), (0.0, sy, 0.188),
        material=MAT_CHROME, bevel=0.003)
    box("Toaster.Slot.%d" % (i + 1), (0.212, 0.026, 0.075), (0.0, sy, 0.150),
        material=MAT_SLOT)
    box("Toaster.SlotWire.%d" % (i + 1), (0.196, 0.004, 0.006), (0.0, sy, 0.152),
        material=MAT_CHROME)

# ---------------------------------------------------------------- side controls

# carriage lever riding in a recessed track
box("Control.LeverTrack", (0.008, 0.016, 0.104), (SIDE_X, -0.048, 0.118),
    material=MAT_SLOT)
box("Control.LeverStem", (0.012, 0.012, 0.026), (SIDE_X + 0.007, -0.048, 0.152),
    material=MAT_CHROME, bevel=0.003)
box("Control.LeverKnob", (0.020, 0.034, 0.024), (SIDE_X + 0.020, -0.048, 0.158),
    material=MAT_TRIM, bevel=0.006, segments=4)

# browning dial with an indicator mark
cylinder("Control.DialBase", 0.032, 0.008, (SIDE_X + 0.004, 0.030, 0.078),
         rotation=X_AXIS, material=MAT_TRIM)
cylinder("Control.Dial", 0.026, 0.016, (SIDE_X + 0.012, 0.030, 0.078),
         rotation=X_AXIS, material=MAT_CHROME)
box("Control.DialMark", (0.006, 0.005, 0.020), (SIDE_X + 0.021, 0.030, 0.089),
    rotation=(math.radians(18.0), 0.0, 0.0), material=MAT_ACCENT)

# function buttons above the dial
for i, by in enumerate((0.056, 0.012)):
    box("Control.Button.%d" % (i + 1), (0.010, 0.028, 0.016), (SIDE_X + 0.003, by, 0.146),
        material=MAT_TRIM, bevel=0.004)
    box("Control.ButtonLed.%d" % (i + 1), (0.004, 0.008, 0.004), (SIDE_X + 0.009, by, 0.146),
        material=MAT_ACCENT)

# ---------------------------------------------------------------- crumb tray + cord

box("Toaster.CrumbTray", (0.262, 0.014, 0.028), (0.0, -0.093, 0.040),
    material=MAT_TRIM, bevel=0.004)
box("Toaster.TrayHandle", (0.070, 0.012, 0.008), (0.0, -0.101, 0.040),
    material=MAT_CHROME, bevel=0.003)

cord_data = bpy.data.curves.new("Toaster.CordCurve", 'CURVE')
cord_data.dimensions = '3D'
cord_data.resolution_u = 8
cord_data.bevel_depth = 0.005
cord_data.bevel_resolution = 3
spline = cord_data.splines.new('BEZIER')
spline.bezier_points.add(2)
for point, co in zip(spline.bezier_points,
                     [(-0.05, 0.092, 0.050), (-0.22, 0.200, 0.014), (-0.42, 0.150, 0.006)]):
    point.co = co
    point.handle_left_type = 'AUTO'
    point.handle_right_type = 'AUTO'
cord = bpy.data.objects.new("Toaster.Cord", cord_data)
bpy.context.collection.objects.link(cord)
cord.data.materials.append(MAT_TRIM)

# ---------------------------------------------------------------- lighting + camera

key = bpy.data.lights.new("Key", 'AREA')
key.energy = 160.0
key.size = 0.9
key_obj = bpy.data.objects.new("Light.Key", key)
bpy.context.collection.objects.link(key_obj)
key_obj.location = (0.5, -0.6, 0.9)
key_obj.rotation_euler = (Vector(key_obj.location) - Vector((0.0, 0.0, 0.1))).to_track_quat('Z', 'Y').to_euler()

fill = bpy.data.lights.new("Fill", 'SUN')
fill.energy = 2.0
fill_obj = bpy.data.objects.new("Light.Fill", fill)
bpy.context.collection.objects.link(fill_obj)
fill_obj.rotation_euler = (math.radians(55.0), 0.0, math.radians(140.0))

add_camera((0.52, -0.56, 0.36), (0.0, 0.0, 0.10), lens=55.0)
