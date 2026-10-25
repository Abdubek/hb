import bpy, bmesh, math
from mathutils import Vector, Matrix, Quaternion

# ----------------------------------------------------------------------------
# scene reset
# ----------------------------------------------------------------------------
bpy.ops.wm.read_factory_settings(use_empty=True)
scene = bpy.context.scene
scene.unit_settings.system = 'METRIC'
scene.unit_settings.length_unit = 'CENTIMETERS'

TAU = math.tau
SEGS = 96

# pan dimensions (metres)
R = 0.090          # outer body radius
H = 0.115          # body height
T = 0.0040         # wall thickness
TB = 0.0060        # base thickness (thick sandwich base)

LID_R = R + 0.0022
LID_T = 0.0035
LID_DOME = 0.030
LID_SKIRT = 0.007


# ----------------------------------------------------------------------------
# helpers
# ----------------------------------------------------------------------------
def link(obj):
    bpy.context.collection.objects.link(obj)
    return obj


def material(name, color, metallic=0.0, roughness=0.5, ior=1.45,
             coat=0.0, aniso=0.0):
    mat = bpy.data.materials.new(name)
    mat.use_nodes = True
    bsdf = mat.node_tree.nodes.get("Principled BSDF")
    if bsdf:
        def put(key, value):
            if key in bsdf.inputs:
                bsdf.inputs[key].default_value = value
        put("Base Color", (*color, 1.0))
        put("Metallic", metallic)
        put("Roughness", roughness)
        put("IOR", ior)
        put("Coat Weight", coat)
        put("Coat Roughness", 0.12)
        put("Anisotropic", aniso)
    return mat


def assign(obj, mat):
    obj.data.materials.append(mat)
    return obj


def smooth(obj, angle_deg=32.0):
    """Smooth shading limited by angle (4.1+ 'Smooth by Angle' node group)."""
    prev = bpy.context.view_layer.objects.active
    for o in bpy.context.selected_objects:
        o.select_set(False)
    obj.select_set(True)
    bpy.context.view_layer.objects.active = obj
    try:
        bpy.ops.object.shade_auto_smooth(angle=math.radians(angle_deg))
    except Exception:
        bpy.ops.object.shade_smooth()
    obj.select_set(False)
    if prev:
        bpy.context.view_layer.objects.active = prev


def revolve(name, profile, segments=SEGS, close_profile=False):
    """Lathe a list of (radius, z) points around the global Z axis."""
    bm = bmesh.new()
    verts = [bm.verts.new((p[0], 0.0, p[1])) for p in profile]
    edges = []
    for a, b in zip(verts, verts[1:]):
        edges.append(bm.edges.new((a, b)))
    if close_profile:
        edges.append(bm.edges.new((verts[-1], verts[0])))

    bmesh.ops.spin(bm, geom=verts + edges, axis=(0.0, 0.0, 1.0),
                   cent=(0.0, 0.0, 0.0), dvec=(0.0, 0.0, 0.0),
                   angle=TAU, steps=segments, use_merge=True)
    bmesh.ops.remove_doubles(bm, verts=bm.verts, dist=1.0e-5)
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)

    me = bpy.data.meshes.new(name)
    bm.to_mesh(me)
    bm.free()
    return link(bpy.data.objects.new(name, me))


def tube(name, points, radii, bevel_res=8, flatten=1.0, flatten_pivot=0.0):
    """Round-section swept tube along a NURBS path; returns a mesh object."""
    cu = bpy.data.curves.new(name + "_curve", 'CURVE')
    cu.dimensions = '3D'
    cu.resolution_u = 14
    cu.bevel_depth = 1.0            # radius comes from per-point radius
    cu.bevel_resolution = bevel_res
    cu.use_fill_caps = True

    sp = cu.splines.new('NURBS')
    sp.points.add(len(points) - 1)
    for pt, co, rad in zip(sp.points, points, radii):
        pt.co = (co[0], co[1], co[2], 1.0)
        pt.radius = rad
    sp.order_u = 3
    sp.use_endpoint_u = True

    obj = link(bpy.data.objects.new(name, cu))
    for o in bpy.context.selected_objects:
        o.select_set(False)
    obj.select_set(True)
    bpy.context.view_layer.objects.active = obj
    bpy.ops.object.convert(target='MESH')
    obj.select_set(False)

    if flatten != 1.0:
        m = (Matrix.Translation((0.0, 0.0, flatten_pivot))
             @ Matrix.Diagonal((1.0, 1.0, flatten, 1.0)).to_4x4()
             @ Matrix.Translation((0.0, 0.0, -flatten_pivot)))
        obj.data.transform(m)
    obj.data.update()
    return obj


def cylinder(name, radius, depth, location, rotation=(0.0, 0.0, 0.0),
             verts=48, scale=(1.0, 1.0, 1.0)):
    bm = bmesh.new()
    bmesh.ops.create_cone(bm, cap_ends=True, cap_tris=False, segments=verts,
                          radius1=radius, radius2=radius, depth=depth)
    bmesh.ops.scale(bm, verts=bm.verts, vec=Vector(scale))
    me = bpy.data.meshes.new(name)
    bm.to_mesh(me)
    bm.free()
    obj = link(bpy.data.objects.new(name, me))
    obj.location = location
    obj.rotation_euler = rotation
    return obj


# ----------------------------------------------------------------------------
# materials
# ----------------------------------------------------------------------------
mat_steel = material("Stainless Steel", (0.760, 0.775, 0.790),
                     metallic=1.0, roughness=0.19, aniso=0.35)
mat_steel_dull = material("Steel Base", (0.560, 0.575, 0.590),
                          metallic=1.0, roughness=0.42)
mat_bakelite = material("Handle Phenolic", (0.032, 0.033, 0.036),
                        metallic=0.0, roughness=0.38, coat=0.25)
mat_floor = material("Worktop", (0.215, 0.205, 0.196),
                     metallic=0.0, roughness=0.55)


# ----------------------------------------------------------------------------
# pan body: closed lathe profile (outer wall -> rolled rim -> inner wall -> base)
# ----------------------------------------------------------------------------
body_profile = [
    (0.0000, 0.0000),                 # base, outside centre
    (R - 0.020, 0.0000),
    (R - 0.009, 0.0012),
    (R - 0.0025, 0.0075),             # base-to-wall radius (outside)
    (R - 0.0004, 0.0160),
    (R, 0.0280),
    (R, H - 0.0130),
    (R + 0.0012, H - 0.0055),         # slight flare below the rim
    (R + 0.0034, H - 0.0012),         # rolled pouring rim
    (R + 0.0030, H),
    (R + 0.0002, H - 0.0004),
    (R - 0.0016, H - 0.0035),
    (R - T, H - 0.0135),              # inner wall
    (R - T, 0.0300),
    (R - T - 0.0010, 0.0195),
    (R - T - 0.0075, TB + 0.0016),    # inner base fillet
    (R - T - 0.0165, TB),
    (0.0000, TB),                     # base, inside centre
]
pan = revolve("Saucepan_Body", body_profile)
assign(pan, mat_steel)
smooth(pan, 34.0)

# encapsulated heat-diffusing disc under the base
disc = revolve("Base_Disc", [
    (0.0000, -0.0038),
    (R - 0.026, -0.0038),
    (R - 0.019, -0.0030),
    (R - 0.017, -0.0006),
    (R - 0.0175, 0.0004),
    (0.0000, 0.0004),
], segments=SEGS)
assign(disc, mat_steel_dull)
smooth(disc, 30.0)

# measuring graduations inside the pan (thin embossed rings)
for i, zz in enumerate((0.040, 0.062, 0.084)):
    ring = revolve("Grad_Ring_%d" % i, [
        (R - T - 0.0002, zz - 0.0009),
        (R - T - 0.0013, zz),
        (R - T - 0.0002, zz + 0.0009),
    ], segments=SEGS)
    assign(ring, mat_steel_dull)
    smooth(ring, 40.0)


# ----------------------------------------------------------------------------
# lid: domed lathe profile with skirt, plus knob
# ----------------------------------------------------------------------------
LID_Z = H - 0.0024          # skirt drops over the rim
ARC = 22

lid_profile = []
for i in range(ARC + 1):                       # outer dome, apex -> rim
    a = (i / ARC) * (math.pi * 0.5)
    lid_profile.append((LID_R * math.sin(a),
                        LID_SKIRT + LID_DOME * math.cos(a)))
lid_profile += [
    (LID_R, LID_SKIRT * 0.45),
    (LID_R, 0.0006),
    (LID_R - 0.0009, -0.0004),                 # rounded skirt edge
    (LID_R - LID_T, 0.0004),
    (LID_R - LID_T, LID_SKIRT * 0.55),
]
for i in range(ARC, -1, -1):                   # inner dome, rim -> apex
    a = (i / ARC) * (math.pi * 0.5)
    lid_profile.append(((LID_R - LID_T) * math.sin(a),
                        LID_SKIRT + (LID_DOME - LID_T) * math.cos(a)))

lid = revolve("Lid", lid_profile)
lid.location.z = LID_Z
assign(lid, mat_steel)
smooth(lid, 34.0)

# knob mounting washer + mushroom knob on the lid apex
KNOB_Z = LID_Z + LID_SKIRT + LID_DOME - 0.0012

washer = revolve("Knob_Washer", [
    (0.0000, 0.0000),
    (0.0175, 0.0000),
    (0.0180, 0.0011),
    (0.0168, 0.0022),
    (0.0000, 0.0022),
])
washer.location.z = KNOB_Z
assign(washer, mat_steel)
smooth(washer, 30.0)

knob_profile = [
    (0.0000, 0.0000),
    (0.0150, 0.0000),
    (0.0158, 0.0022),                # flared base skirt
    (0.0128, 0.0046),
    (0.0086, 0.0062),
    (0.0074, 0.0100),                # waist
    (0.0092, 0.0142),
    (0.0140, 0.0186),
    (0.0158, 0.0242),                # cap swell
    (0.0143, 0.0294),
    (0.0098, 0.0326),
    (0.0044, 0.0342),
    (0.0000, 0.0345),
]
knob = revolve("Lid_Knob", knob_profile)
knob.location.z = KNOB_Z + 0.0020
assign(knob, mat_bakelite)
smooth(knob, 40.0)


# ----------------------------------------------------------------------------
# main handle: mounting plate, rivets and phenolic grip
# ----------------------------------------------------------------------------
PLATE_Z = 0.0790

plate = cylinder("Handle_Plate", 0.0195, 0.0075,
                 location=(R - 0.0012, 0.0, PLATE_Z),
                 rotation=(0.0, math.pi * 0.5, 0.0),
                 scale=(1.0, 1.0, 1.0))
assign(plate, mat_steel)
smooth(plate, 30.0)

for dz in (-0.0105, 0.0105):
    rivet = revolve("Rivet", [
        (0.0000, 0.0000),
        (0.0042, 0.0002),
        (0.0046, 0.0014),
        (0.0034, 0.0026),
        (0.0000, 0.0030),
    ], segments=32)
    rivet.rotation_euler = (0.0, math.pi * 0.5, 0.0)
    rivet.location = (R + 0.0026, 0.0, PLATE_Z + dz)
    assign(rivet, mat_steel)
    smooth(rivet, 34.0)

HL = 0.205
hpts, hrad = [], []
N = 20
for i in range(N):
    t = i / (N - 1)
    x = R - 0.010 + HL * t
    z = PLATE_Z + 0.052 * (t ** 1.45) - 0.006 * math.sin(math.pi * t)
    r = 0.0092 + 0.0040 * math.sin(math.pi * min(1.0, t * 1.05)) ** 0.7
    if t < 0.10:
        r *= 0.80 + 2.0 * t
    if t > 0.90:
        r *= max(0.18, 1.0 - (t - 0.90) * 7.2)
    hpts.append((x, 0.0, z))
    hrad.append(r)

handle = tube("Handle_Grip", hpts, hrad, bevel_res=10,
              flatten=0.86, flatten_pivot=PLATE_Z + 0.020)
assign(handle, mat_bakelite)
smooth(handle, 40.0)

# hanging eyelet at the handle tip
tip = Vector(hpts[-1])
eyelet = revolve("Handle_Eyelet", [
    (0.0060, 0.0000),
    (0.0092, 0.0016),
    (0.0122, 0.0000),
    (0.0092, -0.0016),
], segments=40, close_profile=True)
eyelet.rotation_euler = (math.pi * 0.5, 0.0, 0.0)
eyelet.location = (tip.x - 0.004, 0.0, tip.z + 0.001)
assign(eyelet, mat_steel)
smooth(eyelet, 40.0)


# ----------------------------------------------------------------------------
# opposite helper (loop) handle
# ----------------------------------------------------------------------------
hp_plate = cylinder("Helper_Plate", 0.0150, 0.0065,
                    location=(-(R - 0.0014), 0.0, PLATE_Z),
                    rotation=(0.0, math.pi * 0.5, 0.0))
assign(hp_plate, mat_steel)
smooth(hp_plate, 30.0)

for dz in (-0.0075, 0.0075):
    rv = revolve("Helper_Rivet", [
        (0.0000, 0.0000),
        (0.0038, 0.0002),
        (0.0042, 0.0013),
        (0.0030, 0.0024),
        (0.0000, 0.0027),
    ], segments=32)
    rv.rotation_euler = (0.0, -math.pi * 0.5, 0.0)
    rv.location = (-(R + 0.0024), 0.0, PLATE_Z + dz)
    assign(rv, mat_steel)
    smooth(rv, 34.0)

loop_pts, loop_rad = [], []
M = 16
for i in range(M):
    t = i / (M - 1)
    a = math.pi * (t - 0.5)                 # -90deg .. +90deg sweep
    x = -(R - 0.006) - 0.052 * math.cos(a)
    z = PLATE_Z + 0.021 * math.sin(a)
    r = 0.0082 + 0.0016 * math.sin(math.pi * t)
    if t < 0.08 or t > 0.92:
        r *= 0.90
    loop_pts.append((x, 0.0, z))
    loop_rad.append(r)

loop = tube("Helper_Handle", loop_pts, loop_rad, bevel_res=10,
            flatten=0.90, flatten_pivot=PLATE_Z)
assign(loop, mat_bakelite)
smooth(loop, 40.0)


# ----------------------------------------------------------------------------
# worktop
# ----------------------------------------------------------------------------
bm = bmesh.new()
bmesh.ops.create_grid(bm, x_segments=1, y_segments=1, size=1.2)
me = bpy.data.meshes.new("Worktop")
bm.to_mesh(me)
bm.free()
floor = link(bpy.data.objects.new("Worktop", me))
floor.location.z = -0.0038
assign(floor, mat_floor)


# ----------------------------------------------------------------------------
# lighting
# ----------------------------------------------------------------------------
world = bpy.data.worlds.new("World")
world.use_nodes = True
bg = world.node_tree.nodes.get("Background")
if bg:
    bg.inputs["Color"].default_value = (0.045, 0.048, 0.055, 1.0)
    bg.inputs["Strength"].default_value = 1.0
scene.world = world


def area_light(name, energy, size, location, target=(0.0, 0.0, 0.06),
               shape='RECTANGLE', size_y=None, color=(1.0, 1.0, 1.0)):
    data = bpy.data.lights.new(name, 'AREA')
    data.energy = energy
    data.shape = shape
    data.size = size
    if size_y is not None:
        data.size_y = size_y
    data.color = color
    obj = link(bpy.data.objects.new(name, data))
    obj.location = location
    d = Vector(target) - Vector(location)
    obj.rotation_euler = d.to_track_quat('-Z', 'Y').to_euler()
    return obj


# broad key softbox (gives the long highlight down the steel wall)
area_light("Key", 180.0, 1.10, (0.62, -0.85, 1.05), size_y=0.55)
# cool fill from the left
area_light("Fill", 55.0, 1.40, (-1.00, -0.45, 0.60),
           color=(0.82, 0.88, 1.0), size_y=1.0)
# narrow strip rim light behind, sharpens rim and lid dome
area_light("Rim", 110.0, 1.60, (-0.35, 1.05, 0.70), size_y=0.12,
           target=(0.0, 0.0, 0.10))
# small top light to read the knob
area_light("Top", 30.0, 0.45, (0.05, -0.10, 0.95),
           target=(0.0, 0.0, 0.15), shape='SQUARE')


# ----------------------------------------------------------------------------
# camera
# ----------------------------------------------------------------------------
cam_data = bpy.data.cameras.new("Camera")
cam_data.lens = 68.0
cam_data.sensor_width = 36.0
cam_data.clip_start = 0.01
cam_data.clip_end = 50.0
cam_data.dof.use_dof = True
cam_data.dof.aperture_fstop = 4.0

cam = link(bpy.data.objects.new("Camera", cam_data))
cam.location = (0.62, -0.72, 0.34)
look_at = Vector((0.030, 0.0, 0.070))
cam.rotation_euler = (look_at - cam.location).to_track_quat('-Z', 'Y').to_euler()
cam_data.dof.focus_distance = (look_at - cam.location).length
scene.camera = cam

scene.render.resolution_x = 1600
scene.render.resolution_y = 1200
scene.render.film_transparent = False
try:
    scene.render.engine = 'CYCLES'
    scene.cycles.samples = 128
    scene.cycles.use_denoising = True
except Exception:
    pass

bpy.context.view_layer.update()
