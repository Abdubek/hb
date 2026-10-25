"""claude-092 - A lecture podium with microphone and reading surface (Blender 4.5 LTS)."""
import bpy, bmesh, math
from mathutils import Vector, Euler


def reset_scene():
    bpy.ops.wm.read_factory_settings(use_empty=True)
    scene = bpy.context.scene
    scene.render.engine = 'CYCLES'
    if hasattr(scene, "cycles"):
        scene.cycles.samples = 64
    world = bpy.data.worlds.new("World")
    scene.world = world
    world.use_nodes = True
    bg = world.node_tree.nodes["Background"]
    bg.inputs[0].default_value = (0.035, 0.036, 0.045, 1.0)
    bg.inputs[1].default_value = 1.0


def make_material(name, color, roughness=0.5, metallic=0.0,
                  emission=None, emission_strength=0.0):
    mat = bpy.data.materials.new(name)
    mat.use_nodes = True
    bsdf = mat.node_tree.nodes["Principled BSDF"]
    bsdf.inputs["Base Color"].default_value = (*color, 1.0)
    bsdf.inputs["Roughness"].default_value = roughness
    bsdf.inputs["Metallic"].default_value = metallic
    if emission is not None:
        bsdf.inputs["Emission Color"].default_value = (*emission, 1.0)
        bsdf.inputs["Emission Strength"].default_value = emission_strength
    return mat


def shade(obj, angle=30.0):
    for poly in obj.data.polygons:
        poly.use_smooth = True
    mod = obj.modifiers.new("EdgeSplit", 'EDGE_SPLIT')
    mod.split_angle = math.radians(angle)


def add_box(name, size, location, rotation=(0, 0, 0), material=None,
            bevel=0.0, segments=2):
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=location, rotation=rotation)
    obj = bpy.context.active_object
    obj.name = name
    obj.scale = size
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    if material:
        obj.data.materials.append(material)
    if bevel > 0.0:
        mod = obj.modifiers.new("Bevel", 'BEVEL')
        mod.width = bevel
        mod.segments = segments
        mod.limit_method = 'ANGLE'
        mod.angle_limit = math.radians(40)
        mod.use_clamp_overlap = True
    return obj


def add_cylinder(name, radius, depth, location, rotation=(0, 0, 0),
                 material=None, verts=32):
    bpy.ops.mesh.primitive_cylinder_add(radius=radius, depth=depth, vertices=verts,
                                        location=location, rotation=rotation)
    obj = bpy.context.active_object
    obj.name = name
    if material:
        obj.data.materials.append(material)
    shade(obj)
    return obj


def add_sphere(name, radius, location, material=None, segments=24, rings=12,
               scale=(1.0, 1.0, 1.0), rotation=(0, 0, 0)):
    bpy.ops.mesh.primitive_uv_sphere_add(radius=radius, segments=segments,
                                         ring_count=rings, location=location,
                                         rotation=rotation)
    obj = bpy.context.active_object
    obj.name = name
    obj.scale = scale
    if material:
        obj.data.materials.append(material)
    shade(obj, angle=45.0)
    return obj


def add_tube_curve(name, points, radius, material=None, location=(0, 0, 0),
                   rotation=(0, 0, 0)):
    curve = bpy.data.curves.new(name, 'CURVE')
    curve.dimensions = '3D'
    curve.resolution_u = 16
    curve.bevel_depth = radius
    curve.bevel_resolution = 6
    spline = curve.splines.new('BEZIER')
    spline.bezier_points.add(len(points) - 1)
    for bp, co in zip(spline.bezier_points, points):
        bp.co = Vector(co)
        bp.handle_left_type = 'AUTO'
        bp.handle_right_type = 'AUTO'
    spline.use_smooth = True
    obj = bpy.data.objects.new(name, curve)
    obj.location = location
    obj.rotation_euler = rotation
    bpy.context.collection.objects.link(obj)
    if material:
        curve.materials.append(material)
    return obj


def add_camera(location, target, lens=50.0):
    cam_data = bpy.data.cameras.new("Camera")
    cam_data.lens = lens
    cam = bpy.data.objects.new("Camera", cam_data)
    cam.location = location
    bpy.context.collection.objects.link(cam)
    empty = bpy.data.objects.new("CameraTarget", None)
    empty.location = target
    bpy.context.collection.objects.link(empty)
    con = cam.constraints.new('TRACK_TO')
    con.target = empty
    con.track_axis = 'TRACK_NEGATIVE_Z'
    con.up_axis = 'UP_Y'
    bpy.context.scene.camera = cam
    return cam


def add_light(name, ltype, location, energy, size=1.0, rotation=(0, 0, 0),
              color=(1.0, 1.0, 1.0), spot_size=0.9, spot_blend=0.35):
    data = bpy.data.lights.new(name, ltype)
    data.energy = energy
    data.color = color
    if ltype == 'AREA':
        data.size = size
    elif ltype == 'SPOT':
        data.spot_size = spot_size
        data.spot_blend = spot_blend
        data.shadow_soft_size = size
    else:
        data.shadow_soft_size = size
    obj = bpy.data.objects.new(name, data)
    obj.location = location
    obj.rotation_euler = rotation
    bpy.context.collection.objects.link(obj)
    return obj


# ------------------------------------------------------------------ scene
reset_scene()

wood_mat = make_material("PodiumWood", (0.135, 0.062, 0.030), roughness=0.32)
wood_light = make_material("PodiumWoodLight", (0.32, 0.17, 0.085), roughness=0.38)
trim_mat = make_material("PodiumTrim", (0.055, 0.03, 0.018), roughness=0.28)
brass_mat = make_material("Brass", (0.72, 0.55, 0.24), roughness=0.24, metallic=1.0)
steel_mat = make_material("Steel", (0.55, 0.56, 0.58), roughness=0.30, metallic=1.0)
black_mat = make_material("MicBlack", (0.020, 0.020, 0.022), roughness=0.45)
mesh_mat = make_material("MicMesh", (0.10, 0.10, 0.11), roughness=0.35, metallic=0.9)
paper_mat = make_material("Paper", (0.88, 0.87, 0.83), roughness=0.75)
felt_mat = make_material("DeskFelt", (0.055, 0.075, 0.10), roughness=0.95)
floor_mat = make_material("StageFloor", (0.055, 0.05, 0.05), roughness=0.55)
back_mat = make_material("Backdrop", (0.075, 0.085, 0.11), roughness=0.9)
led_mat = make_material("StatusLED", (0.1, 0.5, 0.15), roughness=0.3,
                        emission=(0.15, 1.0, 0.25), emission_strength=8.0)

# --- stage floor and backdrop
add_box("StageFloor", (8.0, 8.0, 0.08), (0.0, 0.6, -0.04), material=floor_mat)
add_box("Backdrop", (8.0, 0.12, 3.6), (0.0, 2.4, 1.8), material=back_mat)


# --- lectern body: lofted shell, narrow at the foot and wider at the top
def build_body(name, rings, material):
    mesh = bpy.data.meshes.new(name)
    bm = bmesh.new()
    loops = []
    for hx, hy, z in rings:
        loops.append([bm.verts.new(v) for v in ((-hx, -hy, z), (hx, -hy, z),
                                                (hx, hy, z), (-hx, hy, z))])
    for lower, upper in zip(loops, loops[1:]):
        for i in range(4):
            j = (i + 1) % 4
            bm.faces.new((lower[i], lower[j], upper[j], upper[i]))
    bm.faces.new(loops[0])
    bm.faces.new(loops[-1])
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces[:])
    bm.to_mesh(mesh)
    bm.free()
    obj = bpy.data.objects.new(name, mesh)
    bpy.context.collection.objects.link(obj)
    obj.data.materials.append(material)
    mod = obj.modifiers.new("Bevel", 'BEVEL')
    mod.width = 0.010
    mod.segments = 3
    mod.limit_method = 'ANGLE'
    mod.angle_limit = math.radians(35)
    mod.use_clamp_overlap = True
    return obj


build_body("LecternBody",
           [(0.255, 0.205, 0.00),
            (0.255, 0.205, 0.055),
            (0.215, 0.175, 0.115),
            (0.240, 0.185, 0.520),
            (0.300, 0.225, 1.015)],
           wood_mat)

# plinth under the body
add_box("Plinth", (0.60, 0.50, 0.045), (0.0, 0.0, 0.0225), material=trim_mat, bevel=0.008)

# --- decorative front panel and emblem (audience side is -Y)
add_box("FrontPanel", (0.40, 0.014, 0.62), (0.0, -0.222, 0.62),
        material=wood_light, bevel=0.006)
add_cylinder("EmblemDisc", 0.105, 0.014, (0.0, -0.232, 0.62),
             rotation=(math.radians(90.0), 0.0, 0.0), material=brass_mat, verts=48)
add_cylinder("EmblemInner", 0.078, 0.016, (0.0, -0.236, 0.62),
             rotation=(math.radians(90.0), 0.0, 0.0), material=wood_light, verts=48)
for i in range(8):
    a = i * math.tau / 8.0
    add_box("EmblemRay_%d" % i, (0.012, 0.010, 0.030),
            (0.092 * math.sin(a), -0.239, 0.62 + 0.092 * math.cos(a)),
            rotation=(0.0, a, 0.0), material=brass_mat)

# --- side rails
for side in (-1, 1):
    add_box("SideRail_%d" % side, (0.014, 0.34, 0.70),
            (side * 0.272, 0.0, 0.63), material=trim_mat, bevel=0.005)

# --- reading surface: slanted top, high edge towards the audience
TILT = math.radians(-12.0)
TOP_CENTER = Vector((0.0, 0.02, 1.055))
tilt_mat = Euler((TILT, 0.0, 0.0), 'XYZ').to_matrix()


def on_surface(local):
    """Map a point given in reading-surface space into world space."""
    return TOP_CENTER + tilt_mat @ Vector(local)


add_box("ReadingSurface", (0.70, 0.52, 0.034), TOP_CENTER,
        rotation=(TILT, 0.0, 0.0), material=wood_mat, bevel=0.008, segments=3)
add_box("SurfaceFelt", (0.66, 0.48, 0.004), on_surface((0.0, 0.0, 0.019)),
        rotation=(TILT, 0.0, 0.0), material=felt_mat)
# book lip along the low (audience) edge
add_box("BookLip", (0.70, 0.030, 0.050), on_surface((0.0, -0.252, 0.030)),
        rotation=(TILT, 0.0, 0.0), material=trim_mat, bevel=0.008)
# thin trim strip along the reader's edge
add_box("RearTrim", (0.70, 0.024, 0.016), on_surface((0.0, 0.252, 0.020)),
        rotation=(TILT, 0.0, 0.0), material=trim_mat, bevel=0.005)

# --- speaking notes lying on the reading surface
for i, (dx, dy, rot_z, h) in enumerate(((-0.055, 0.015, 2.5, 0.023),
                                        (0.070, -0.030, -4.0, 0.024))):
    add_box("Notes_%d" % i, (0.210, 0.297, 0.003),
            on_surface((dx, dy, h)),
            rotation=(TILT, 0.0, math.radians(rot_z)), material=paper_mat)

# --- interior shelf, visible from the reader's side
add_box("InnerShelf", (0.46, 0.32, 0.020), (0.0, 0.02, 0.70), material=wood_light)

# --- gooseneck microphone rising from the left of the reading surface
mic_base = on_surface((-0.215, 0.075, 0.020))
add_cylinder("MicBaseDisc", 0.048, 0.026, mic_base + Vector((0.0, 0.0, 0.012)),
             material=black_mat, verts=40)
add_cylinder("MicCollar", 0.020, 0.045, mic_base + Vector((0.0, 0.0, 0.045)),
             material=steel_mat, verts=28)

neck_root = mic_base + Vector((0.0, 0.0, 0.062))
neck_points = [
    (neck_root.x, neck_root.y, neck_root.z),
    (neck_root.x, neck_root.y + 0.005, neck_root.z + 0.16),
    (neck_root.x + 0.015, neck_root.y - 0.055, neck_root.z + 0.30),
    (neck_root.x + 0.030, neck_root.y - 0.175, neck_root.z + 0.335),
]
add_tube_curve("Gooseneck", neck_points, 0.0075, material=black_mat)

# microphone capsule at the tip, angled towards the speaker
tip = Vector(neck_points[-1])
cap_rot = (math.radians(72.0), 0.0, math.radians(-8.0))
add_cylinder("MicBody", 0.019, 0.070, tip + Vector((0.006, -0.030, -0.008)),
             rotation=cap_rot, material=black_mat, verts=28)
add_sphere("MicHead", 0.021, tip + Vector((0.010, -0.062, -0.018)),
           material=mesh_mat, segments=28, rings=16)
add_cylinder("MicLED", 0.005, 0.004, tip + Vector((0.0, 0.002, 0.012)),
             rotation=cap_rot, material=led_mat, verts=16)

# --- small control plate with a mute button on the reading surface
plate = on_surface((0.24, 0.150, 0.020))
add_box("ControlPlate", (0.10, 0.06, 0.008), plate,
        rotation=(TILT, 0.0, 0.0), material=steel_mat, bevel=0.003)
add_cylinder("MuteButton", 0.016, 0.012, on_surface((0.24, 0.150, 0.030)),
             rotation=(TILT, 0.0, 0.0), material=black_mat, verts=24)

# --- lighting
key = add_light("Key", 'AREA', (1.9, -2.3, 3.0), 500.0, size=1.8)
key.rotation_euler = (math.radians(45.0), 0.0, math.radians(38.0))
fill = add_light("Fill", 'AREA', (-2.2, -1.9, 1.9), 150.0, size=2.4)
fill.rotation_euler = (math.radians(70.0), 0.0, math.radians(-48.0))
rim = add_light("Rim", 'AREA', (-0.6, 2.0, 2.6), 220.0, size=1.4,
                color=(0.7, 0.8, 1.0))
rim.rotation_euler = (math.radians(-125.0), 0.0, math.radians(-10.0))
spot = add_light("PodiumSpot", 'SPOT', (0.0, -1.1, 3.3), 260.0, size=0.08,
                 spot_size=math.radians(48.0), color=(1.0, 0.95, 0.86))
spot.rotation_euler = (math.radians(20.0), 0.0, 0.0)

# --- camera
add_camera((1.35, -1.85, 1.62), (0.0, -0.02, 0.92), lens=55.0)
