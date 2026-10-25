"""claude-093 - A museum display case with pedestal and glass enclosure (Blender 4.5 LTS)."""
import bpy, bmesh, math
from mathutils import Vector


def reset_scene():
    bpy.ops.wm.read_factory_settings(use_empty=True)
    scene = bpy.context.scene
    scene.render.engine = 'CYCLES'
    if hasattr(scene, "cycles"):
        scene.cycles.samples = 96
        scene.cycles.transparent_max_bounces = 24
        scene.cycles.transmission_bounces = 16
    world = bpy.data.worlds.new("World")
    scene.world = world
    world.use_nodes = True
    bg = world.node_tree.nodes["Background"]
    bg.inputs[0].default_value = (0.025, 0.026, 0.032, 1.0)
    bg.inputs[1].default_value = 0.9


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


def make_glass(name):
    mat = bpy.data.materials.new(name)
    mat.use_nodes = True
    bsdf = mat.node_tree.nodes["Principled BSDF"]
    bsdf.inputs["Base Color"].default_value = (0.92, 0.97, 0.95, 1.0)
    bsdf.inputs["Roughness"].default_value = 0.02
    bsdf.inputs["Metallic"].default_value = 0.0
    bsdf.inputs["Transmission Weight"].default_value = 1.0
    bsdf.inputs["IOR"].default_value = 1.46
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


def add_tube_curve(name, points, radius, material=None, location=(0, 0, 0),
                   rotation=(0, 0, 0)):
    curve = bpy.data.curves.new(name, 'CURVE')
    curve.dimensions = '3D'
    curve.resolution_u = 14
    curve.bevel_depth = radius
    curve.bevel_resolution = 5
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


def add_lathed(name, profile, location, material, steps=64):
    """Revolve a 2D profile (x = radius, z = height) around the Z axis."""
    mesh = bpy.data.meshes.new(name)
    bm = bmesh.new()
    verts = [bm.verts.new((x, 0.0, z)) for x, z in profile]
    edges = [bm.edges.new((verts[i], verts[i + 1])) for i in range(len(verts) - 1)]
    bmesh.ops.spin(bm, geom=verts + edges, cent=(0.0, 0.0, 0.0),
                   axis=(0.0, 0.0, 1.0), dvec=(0.0, 0.0, 0.0),
                   angle=math.tau, steps=steps, use_merge=False)
    bmesh.ops.remove_doubles(bm, verts=bm.verts[:], dist=1e-5)
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces[:])
    bm.to_mesh(mesh)
    bm.free()
    obj = bpy.data.objects.new(name, mesh)
    obj.location = location
    bpy.context.collection.objects.link(obj)
    obj.data.materials.append(material)
    shade(obj, angle=50.0)
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
              color=(1.0, 1.0, 1.0), spot_size=0.8, spot_blend=0.4):
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

stone_mat = make_material("PedestalStone", (0.80, 0.79, 0.75), roughness=0.42)
stone_dark = make_material("PedestalBase", (0.16, 0.16, 0.17), roughness=0.55)
chrome_mat = make_material("CaseChrome", (0.72, 0.73, 0.75), roughness=0.15, metallic=1.0)
glass_mat = make_glass("VitrineGlass")
velvet_mat = make_material("DeckVelvet", (0.10, 0.045, 0.055), roughness=0.95)
clay_mat = make_material("Terracotta", (0.36, 0.145, 0.075), roughness=0.55)
clay_dark = make_material("TerracottaSlip", (0.075, 0.055, 0.048), roughness=0.5)
plaque_mat = make_material("Plaque", (0.16, 0.17, 0.18), roughness=0.35, metallic=0.4)
label_mat = make_material("LabelCard", (0.90, 0.89, 0.85), roughness=0.8)
floor_mat = make_material("GalleryFloor", (0.30, 0.29, 0.28), roughness=0.28)
wall_mat = make_material("GalleryWall", (0.13, 0.135, 0.15), roughness=0.9)
strip_mat = make_material("CaseLightStrip", (0.9, 0.85, 0.75), roughness=0.4,
                          emission=(1.0, 0.94, 0.82), emission_strength=14.0)

# --- gallery shell
add_box("GalleryFloor", (10.0, 10.0, 0.10), (0.0, 0.0, -0.05), material=floor_mat)
add_box("GalleryWallBack", (10.0, 0.15, 4.0), (0.0, 2.2, 2.0), material=wall_mat)
add_box("GalleryWallSide", (0.15, 10.0, 4.0), (-2.6, 0.0, 2.0), material=wall_mat)

# --- pedestal
PED = 0.62            # pedestal footprint (square)
PED_H = 0.94          # height of the pedestal top deck
add_box("PedestalPlinth", (PED + 0.10, PED + 0.10, 0.045),
        (0.0, 0.0, 0.0225), material=stone_dark, bevel=0.008)
add_box("PedestalShaft", (PED, PED, PED_H - 0.10),
        (0.0, 0.0, 0.045 + (PED_H - 0.10) * 0.5), material=stone_mat, bevel=0.006)
add_box("PedestalCap", (PED + 0.07, PED + 0.07, 0.055),
        (0.0, 0.0, PED_H - 0.0275), material=stone_mat, bevel=0.010, segments=3)
# shallow reveal groove near the top of the shaft
add_box("PedestalReveal", (PED + 0.012, PED + 0.012, 0.012),
        (0.0, 0.0, PED_H - 0.09), material=stone_dark)

# --- vitrine base frame sitting on the pedestal cap
CASE = 0.52           # glass enclosure footprint
CASE_H = 0.66         # glass height
BASE_H = 0.045
base_z = PED_H + BASE_H * 0.5
add_box("VitrineBase", (CASE + 0.06, CASE + 0.06, BASE_H),
        (0.0, 0.0, base_z), material=chrome_mat, bevel=0.006)
deck_z = PED_H + BASE_H
add_box("VitrineDeck", (CASE - 0.02, CASE - 0.02, 0.008),
        (0.0, 0.0, deck_z + 0.004), material=velvet_mat)

# --- corner posts and glass panes
half = CASE * 0.5
for i, (sx, sy) in enumerate(((-1, -1), (1, -1), (1, 1), (-1, 1))):
    add_box("CornerPost_%d" % i, (0.020, 0.020, CASE_H),
            (sx * half, sy * half, deck_z + CASE_H * 0.5),
            material=chrome_mat, bevel=0.004)

pane_t = 0.006
for i, (axis, sign) in enumerate((("y", -1), ("y", 1), ("x", -1), ("x", 1))):
    if axis == "y":
        size = (CASE - 0.012, pane_t, CASE_H - 0.012)
        loc = (0.0, sign * half, deck_z + CASE_H * 0.5)
    else:
        size = (pane_t, CASE - 0.012, CASE_H - 0.012)
        loc = (sign * half, 0.0, deck_z + CASE_H * 0.5)
    add_box("GlassPane_%d" % i, size, loc, material=glass_mat)

add_box("GlassTop", (CASE - 0.010, CASE - 0.010, pane_t),
        (0.0, 0.0, deck_z + CASE_H - 0.004), material=glass_mat)

# --- crown frame with a concealed light strip on the inside
add_box("CrownFrame", (CASE + 0.05, CASE + 0.05, 0.038),
        (0.0, 0.0, deck_z + CASE_H + 0.019), material=chrome_mat, bevel=0.006)
add_box("LightStrip", (CASE - 0.10, CASE - 0.10, 0.006),
        (0.0, 0.0, deck_z + CASE_H - 0.016), material=strip_mat)

# --- the artefact: a lathed amphora with two handles
PROFILE = [
    (0.000, 0.000), (0.060, 0.000), (0.068, 0.012), (0.052, 0.034),
    (0.070, 0.072), (0.100, 0.128), (0.116, 0.192), (0.112, 0.240),
    (0.090, 0.286), (0.060, 0.322), (0.046, 0.348), (0.050, 0.366),
    (0.070, 0.384), (0.066, 0.396), (0.046, 0.390), (0.041, 0.372),
]
vase_origin = Vector((0.0, 0.0, deck_z + 0.008))
add_lathed("Amphora", PROFILE, vase_origin, clay_mat, steps=72)

for i, ang in enumerate((0.0, math.pi)):
    add_tube_curve("AmphoraHandle_%d" % i,
                   [(0.098, 0.0, 0.238),
                    (0.172, 0.0, 0.292),
                    (0.140, 0.0, 0.348),
                    (0.054, 0.0, 0.356)],
                   0.012, material=clay_mat,
                   location=vase_origin, rotation=(0.0, 0.0, ang))

# painted band details around the belly of the vessel
add_lathed("AmphoraBandA",
           [(0.1175, 0.176), (0.1175, 0.206)], vase_origin, clay_dark, steps=72)
add_lathed("AmphoraBandB",
           [(0.0525, 0.336), (0.0525, 0.352)], vase_origin, clay_dark, steps=72)
add_lathed("AmphoraRim",
           [(0.0705, 0.384), (0.0665, 0.396)], vase_origin, clay_dark, steps=72)

# --- interpretive label, angled on the pedestal front face
add_box("LabelPlaque", (0.28, 0.10, 0.012),
        (0.0, -PED * 0.5 - 0.055, PED_H - 0.20),
        rotation=(math.radians(-58.0), 0.0, 0.0), material=plaque_mat, bevel=0.004)
add_box("LabelCard", (0.24, 0.075, 0.002),
        (0.0, -PED * 0.5 - 0.062, PED_H - 0.197),
        rotation=(math.radians(-58.0), 0.0, 0.0), material=label_mat)

# --- floor stanchion posts marking the viewing distance
for i, (px, py) in enumerate(((-0.85, -0.85), (0.85, -0.85), (0.85, 0.85))):
    add_cylinder("StanchionBase_%d" % i, 0.10, 0.026, (px, py, 0.013),
                 material=stone_dark, verts=28)
    add_cylinder("StanchionPost_%d" % i, 0.020, 0.90, (px, py, 0.46),
                 material=chrome_mat, verts=24)
    add_cylinder("StanchionCap_%d" % i, 0.030, 0.05, (px, py, 0.93),
                 material=chrome_mat, verts=24)

# --- lighting: gallery spots focused on the case
spot_a = add_light("SpotKey", 'SPOT', (0.9, -1.5, 3.1), 420.0, size=0.05,
                   spot_size=math.radians(34.0), color=(1.0, 0.95, 0.88))
spot_a.rotation_euler = (math.radians(32.0), 0.0, math.radians(30.0))
spot_b = add_light("SpotFill", 'SPOT', (-1.4, -0.9, 3.0), 240.0, size=0.05,
                   spot_size=math.radians(42.0), color=(0.9, 0.94, 1.0))
spot_b.rotation_euler = (math.radians(26.0), 0.0, math.radians(-56.0))
rim = add_light("RimArea", 'AREA', (-0.5, 1.6, 2.0), 90.0, size=1.5,
                color=(0.72, 0.80, 1.0))
rim.rotation_euler = (math.radians(-118.0), 0.0, 0.0)
add_light("Ambient", 'AREA', (0.0, -0.4, 3.6), 60.0, size=5.0)

# --- camera
add_camera((1.25, -1.55, 1.55), (0.0, 0.0, 1.16), lens=60.0)
