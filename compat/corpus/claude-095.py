"""claude-095 - A freestanding coat rack with multiple hooks (Blender 4.5 LTS)."""
import bpy, math
from mathutils import Vector


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
    bg.inputs[0].default_value = (0.05, 0.05, 0.055, 1.0)
    bg.inputs[1].default_value = 1.0


def make_material(name, color, roughness=0.5, metallic=0.0):
    mat = bpy.data.materials.new(name)
    mat.use_nodes = True
    bsdf = mat.node_tree.nodes["Principled BSDF"]
    bsdf.inputs["Base Color"].default_value = (*color, 1.0)
    bsdf.inputs["Roughness"].default_value = roughness
    bsdf.inputs["Metallic"].default_value = metallic
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


def add_cone(name, r1, r2, depth, location, rotation=(0, 0, 0),
             material=None, verts=32):
    bpy.ops.mesh.primitive_cone_add(radius1=r1, radius2=r2, depth=depth,
                                    vertices=verts, location=location,
                                    rotation=rotation)
    obj = bpy.context.active_object
    obj.name = name
    if material:
        obj.data.materials.append(material)
    shade(obj)
    return obj


def add_sphere(name, radius, location, material=None, segments=24, rings=14,
               scale=(1.0, 1.0, 1.0)):
    bpy.ops.mesh.primitive_uv_sphere_add(radius=radius, segments=segments,
                                         ring_count=rings, location=location)
    obj = bpy.context.active_object
    obj.name = name
    obj.scale = scale
    if material:
        obj.data.materials.append(material)
    shade(obj, angle=45.0)
    return obj


def add_torus(name, major, minor, location, rotation=(0, 0, 0), material=None,
              major_seg=48, minor_seg=12):
    bpy.ops.mesh.primitive_torus_add(major_radius=major, minor_radius=minor,
                                     major_segments=major_seg,
                                     minor_segments=minor_seg,
                                     location=location, rotation=rotation)
    obj = bpy.context.active_object
    obj.name = name
    if material:
        obj.data.materials.append(material)
    shade(obj, angle=50.0)
    return obj


def add_tube_curve(name, points, radius, material=None, location=(0, 0, 0),
                   rotation=(0, 0, 0), taper_end=None):
    curve = bpy.data.curves.new(name, 'CURVE')
    curve.dimensions = '3D'
    curve.resolution_u = 16
    curve.bevel_depth = radius
    curve.bevel_resolution = 6
    spline = curve.splines.new('BEZIER')
    spline.bezier_points.add(len(points) - 1)
    for i, (bp, co) in enumerate(zip(spline.bezier_points, points)):
        bp.co = Vector(co)
        bp.handle_left_type = 'AUTO'
        bp.handle_right_type = 'AUTO'
        if taper_end is not None:
            frac = i / float(len(points) - 1)
            bp.radius = 1.0 + (taper_end - 1.0) * frac
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
              color=(1.0, 1.0, 1.0)):
    data = bpy.data.lights.new(name, ltype)
    data.energy = energy
    data.color = color
    if ltype == 'AREA':
        data.size = size
    else:
        data.shadow_soft_size = size
    obj = bpy.data.objects.new(name, data)
    obj.location = location
    obj.rotation_euler = rotation
    bpy.context.collection.objects.link(obj)
    return obj


# ------------------------------------------------------------------ scene
reset_scene()

wood_mat = make_material("Walnut", (0.115, 0.055, 0.030), roughness=0.38)
wood_dark = make_material("WalnutDark", (0.055, 0.026, 0.014), roughness=0.34)
brass_mat = make_material("Brass", (0.72, 0.54, 0.22), roughness=0.26, metallic=1.0)
brass_dark = make_material("BrassAged", (0.42, 0.31, 0.13), roughness=0.40, metallic=1.0)
felt_mat = make_material("FootFelt", (0.10, 0.10, 0.11), roughness=0.95)
floor_mat = make_material("OakFloor", (0.30, 0.19, 0.11), roughness=0.35)
wall_mat = make_material("Wall", (0.60, 0.58, 0.55), roughness=0.92)
rug_mat = make_material("Rug", (0.16, 0.13, 0.15), roughness=0.95)

# --- room
add_box("Floor", (8.0, 8.0, 0.08), (0.0, 0.0, -0.04), material=floor_mat)
add_box("WallBack", (8.0, 0.12, 3.2), (0.0, 1.15, 1.60), material=wall_mat)
add_box("Skirting", (8.0, 0.03, 0.12), (0.0, 1.075, 0.06), material=wood_dark)
add_box("Rug", (2.2, 1.6, 0.012), (0.0, -0.15, 0.006), material=rug_mat)

# --- proportions
POLE_R = 0.042
POLE_TOP = 1.76
LEG_HUB_Z = 0.30
FOOT_R = 0.36

# central turned pole, gently tapered
add_cone("Pole", 0.052, 0.036, POLE_TOP, (0.0, 0.0, POLE_TOP * 0.5),
         material=wood_mat, verts=40)

# turned rings and collars along the shaft
for name, z, r, h in (("CollarLow", 0.34, 0.070, 0.045),
                      ("BeadLow", 0.40, 0.058, 0.018),
                      ("BeadMid", 0.92, 0.055, 0.022),
                      ("CollarHooksB", 1.34, 0.066, 0.040),
                      ("CollarHooksA", 1.585, 0.062, 0.040),
                      ("BeadTop", 1.71, 0.052, 0.020)):
    add_cone(name, r, r * 0.94, h, (0.0, 0.0, z), material=wood_dark, verts=40)

# finial on top
add_sphere("Finial", 0.062, (0.0, 0.0, POLE_TOP + 0.045), material=wood_mat,
           scale=(1.0, 1.0, 1.10))
add_sphere("FinialTip", 0.020, (0.0, 0.0, POLE_TOP + 0.125), material=brass_mat)

# --- splayed legs from the hub down to the floor
LEGS = 4
for i in range(LEGS):
    ang = i * math.tau / LEGS + math.radians(45.0)
    top = Vector((0.0, 0.0, LEG_HUB_Z))
    foot = Vector((math.cos(ang) * FOOT_R, math.sin(ang) * FOOT_R, 0.035))
    direction = foot - top
    length = direction.length
    rot = direction.to_track_quat('Z', 'Y').to_euler()
    add_cone("Leg_%d" % i, 0.048, 0.026, length,
             top + direction * 0.5, rotation=rot, material=wood_mat, verts=28)
    add_sphere("LegKnuckle_%d" % i, 0.036, foot, material=wood_dark)
    add_cylinder("LegPad_%d" % i, 0.030, 0.014,
                 (foot.x, foot.y, 0.007), material=felt_mat, verts=20)
    # brass strap where the leg meets the shaft
    add_sphere("LegStrap_%d" % i, 0.026,
               top + direction.normalized() * 0.085,
               material=brass_dark, scale=(1.0, 1.0, 0.6))

add_sphere("LegHub", 0.078, (0.0, 0.0, LEG_HUB_Z), material=wood_dark,
           scale=(1.0, 1.0, 0.72))

# --- umbrella ring near the base, carried on three brass stays
add_torus("UmbrellaRing", 0.215, 0.011, (0.0, 0.0, 0.50), material=brass_mat)
for i in range(3):
    ang = i * math.tau / 3.0
    outer = Vector((math.cos(ang) * 0.215, math.sin(ang) * 0.215, 0.50))
    inner = Vector((math.cos(ang) * 0.055, math.sin(ang) * 0.055, 0.455))
    direction = outer - inner
    rot = direction.to_track_quat('Z', 'Y').to_euler()
    add_cylinder("RingStay_%d" % i, 0.008, direction.length,
                 inner + direction * 0.5, rotation=rot, material=brass_mat, verts=16)


# --- hooks: two whorls of four, offset from one another
def build_hook(tag, z, angle, scale=1.0, material=None):
    pts = [(POLE_R * 0.9, 0.0, 0.0),
           (0.105 * scale, 0.0, -0.030 * scale),
           (0.165 * scale, 0.0, -0.012 * scale),
           (0.185 * scale, 0.0, 0.055 * scale)]
    add_tube_curve("Hook_" + tag, pts, 0.0125 * scale, material=material,
                   location=(0.0, 0.0, z), rotation=(0.0, 0.0, angle))
    tip = Vector(pts[-1])
    tip_world = Vector((math.cos(angle) * tip.x, math.sin(angle) * tip.x, z + tip.z))
    add_sphere("HookTip_" + tag, 0.021 * scale, tip_world, material=material)
    # escutcheon plate where the hook enters the pole
    root = Vector((math.cos(angle) * POLE_R, math.sin(angle) * POLE_R, z))
    add_cylinder("HookRose_" + tag, 0.030 * scale, 0.012,
                 root, rotation=(math.radians(90.0), 0.0, angle),
                 material=material, verts=24)


for i in range(4):
    build_hook("Top_%d" % i, 1.615, i * math.tau / 4.0,
               scale=1.0, material=brass_mat)
for i in range(4):
    build_hook("Mid_%d" % i, 1.365, i * math.tau / 4.0 + math.radians(45.0),
               scale=1.15, material=brass_mat)

# a lower pair of stouter hooks for bags
for i in range(2):
    build_hook("Low_%d" % i, 1.055, i * math.pi + math.radians(22.5),
               scale=1.25, material=brass_dark)

# --- maker's plate on the shaft
add_box("MakerPlate", (0.052, 0.006, 0.026), (0.0, -0.041, 0.72),
        material=brass_dark, bevel=0.002)

# --- lighting
key = add_light("Key", 'AREA', (1.9, -2.0, 2.9), 400.0, size=1.8,
                color=(1.0, 0.96, 0.90))
key.rotation_euler = (math.radians(48.0), 0.0, math.radians(40.0))
fill = add_light("Fill", 'AREA', (-2.1, -1.6, 1.7), 120.0, size=2.2,
                 color=(0.85, 0.90, 1.0))
fill.rotation_euler = (math.radians(75.0), 0.0, math.radians(-52.0))
rim = add_light("Rim", 'AREA', (-0.9, 1.0, 2.4), 180.0, size=1.2)
rim.rotation_euler = (math.radians(-125.0), 0.0, math.radians(-20.0))
add_light("Ambient", 'AREA', (0.0, -1.0, 3.2), 70.0, size=5.0)

# --- camera
add_camera((1.85, -2.35, 1.45), (0.0, 0.0, 1.05), lens=50.0)
