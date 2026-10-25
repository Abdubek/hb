import bpy, bmesh, math
from mathutils import Vector

# ---------------------------------------------------------------- scene reset
def clean_scene():
    bpy.ops.wm.read_factory_settings(use_empty=True)
    for coll in (bpy.data.meshes, bpy.data.materials, bpy.data.objects):
        for item in list(coll):
            coll.remove(item)

clean_scene()
scene = bpy.context.scene
scene.unit_settings.system = 'METRIC'

# ---------------------------------------------------------------- materials
def make_mat(name, color, metallic=0.0, roughness=0.5, spec=0.5):
    mat = bpy.data.materials.new(name)
    mat.use_nodes = True
    bsdf = mat.node_tree.nodes["Principled BSDF"]
    bsdf.inputs["Base Color"].default_value = (*color, 1.0)
    bsdf.inputs["Metallic"].default_value = metallic
    bsdf.inputs["Roughness"].default_value = roughness
    if "Specular IOR Level" in bsdf.inputs:
        bsdf.inputs["Specular IOR Level"].default_value = spec
    return mat

MAT_TRAY   = make_mat("TrayPaint",  (0.05, 0.22, 0.11), 0.75, 0.34)   # green painted steel
MAT_FRAME  = make_mat("FrameSteel", (0.12, 0.13, 0.14), 0.90, 0.42)
MAT_WOOD   = make_mat("Ash",        (0.55, 0.39, 0.21), 0.0,  0.55)
MAT_RUBBER = make_mat("Rubber",     (0.03, 0.03, 0.035), 0.0, 0.75, 0.25)
MAT_HUB    = make_mat("Hub",        (0.45, 0.46, 0.48), 0.95, 0.30)
MAT_GROUND = make_mat("Ground",     (0.28, 0.26, 0.22), 0.0,  0.92)

# ---------------------------------------------------------------- helpers
def link(obj, mat=None):
    scene.collection.objects.link(obj)
    if mat:
        obj.data.materials.append(mat)
    return obj

def mesh_from_bm(name, bm):
    me = bpy.data.meshes.new(name)
    bm.to_mesh(me)
    bm.free()
    return bpy.data.objects.new(name, me)

def add_bevel(obj, width=0.006, segments=2, angle=math.radians(50)):
    m = obj.modifiers.new("Bevel", 'BEVEL')
    m.width = width
    m.segments = segments
    m.limit_method = 'ANGLE'
    m.angle_limit = angle
    return m

def auto_smooth(obj, angle=math.radians(35)):
    for p in obj.data.polygons:
        p.use_smooth = True
    if hasattr(obj.data, "use_auto_smooth"):
        obj.data.use_auto_smooth = True
    if hasattr(obj.data, "auto_smooth_angle"):
        obj.data.auto_smooth_angle = angle

def box(name, size, loc=(0, 0, 0), rot=(0, 0, 0), mat=None, bevel=0.006):
    bm = bmesh.new()
    bmesh.ops.create_cube(bm, size=1.0)
    bmesh.ops.scale(bm, vec=Vector(size), verts=bm.verts)
    obj = link(mesh_from_bm(name, bm), mat)
    obj.location = loc
    obj.rotation_euler = rot
    if bevel:
        add_bevel(obj, bevel)
    return obj

def beam(name, p1, p2, w, h, mat=None, bevel=0.006):
    """Box stretched between two points, cross section w (side) x h (up)."""
    p1, p2 = Vector(p1), Vector(p2)
    d = p2 - p1
    L = d.length
    bm = bmesh.new()
    bmesh.ops.create_cube(bm, size=1.0)
    bmesh.ops.scale(bm, vec=Vector((L, w, h)), verts=bm.verts)
    obj = link(mesh_from_bm(name, bm), mat)
    obj.rotation_mode = 'QUATERNION'
    obj.rotation_quaternion = Vector((1, 0, 0)).rotation_difference(d.normalized())
    obj.location = (p1 + p2) * 0.5
    if bevel:
        add_bevel(obj, bevel)
    return obj

def cylinder(name, radius, depth, loc, rot=(0, 0, 0), mat=None, verts=32, smooth=True):
    bm = bmesh.new()
    bmesh.ops.create_cone(bm, cap_ends=True, cap_tris=False, segments=verts,
                          radius1=radius, radius2=radius, depth=depth)
    obj = link(mesh_from_bm(name, bm), mat)
    obj.location = loc
    obj.rotation_euler = rot
    if smooth:
        for p in obj.data.polygons:
            if len(p.vertices) == 4:
                p.use_smooth = True
    return obj

# ---------------------------------------------------------------- key layout
# +X is forward (wheel end), +Z up. Ground at z = 0.
HANDLE_REAR  = Vector((-1.15, 0.225, 0.52))     # +Y handle, grip end
HANDLE_FRONT = Vector(( 0.86, 0.315, 0.335))    # +Y handle, wheel end
HANDLE_W, HANDLE_H = 0.055, 0.048

def handle_point(t, side):
    """Point along a handle centre line, t=0 rear .. 1 front; side = +1/-1."""
    p = HANDLE_REAR.lerp(HANDLE_FRONT, t)
    return Vector((p.x, p.y * side, p.z))

def t_at_x(x):
    return (x - HANDLE_REAR.x) / (HANDLE_FRONT.x - HANDLE_REAR.x)

WHEEL_R      = 0.205
WHEEL_CENTER = Vector((1.03, 0.0, WHEEL_R))
AXLE_HALF_W  = 0.075

# ---------------------------------------------------------------- handles
for side, tag in ((1, "L"), (-1, "R")):
    beam(f"Handle_{tag}", handle_point(0.0, side), handle_point(1.0, side),
         HANDLE_W, HANDLE_H, MAT_WOOD, bevel=0.008)

    # rubber grip sleeve over the rear stretch of each handle
    g0, g1 = handle_point(0.0, side), handle_point(0.09, side)
    d = (g1 - g0)
    grip = cylinder(f"Grip_{tag}", 0.042, d.length, (0, 0, 0), mat=MAT_RUBBER, verts=24)
    grip.rotation_mode = 'QUATERNION'
    grip.rotation_quaternion = Vector((0, 0, 1)).rotation_difference(d.normalized())
    grip.location = (g0 + g1) * 0.5

# cross braces tying the handles together, under the tray
for t, name in ((0.16, "Brace_Rear"), (0.50, "Brace_Mid"), (0.86, "Brace_Front")):
    a = handle_point(t, -1) + Vector((0, 0, -0.035))
    b = handle_point(t,  1) + Vector((0, 0, -0.035))
    beam(name, a, b, 0.045, 0.022, MAT_FRAME, bevel=0.004)

# ---------------------------------------------------------------- tray
def build_tray():
    b = [Vector(v) for v in ((-0.45, -0.24, 0.0), (0.50, -0.24, 0.0),
                             ( 0.50,  0.24, 0.0), (-0.45,  0.24, 0.0))]
    t = [Vector(v) for v in ((-0.62, -0.45, 0.40), (0.68, -0.45, 0.30),
                             ( 0.68,  0.45, 0.30), (-0.62,  0.45, 0.40))]
    bm = bmesh.new()
    bv = [bm.verts.new(v) for v in b]
    tv = [bm.verts.new(v) for v in t]
    bm.verts.ensure_lookup_table()
    bm.faces.new(bv)                                    # floor
    for i in range(4):
        j = (i + 1) % 4
        bm.faces.new((bv[i], bv[j], tv[j], tv[i]))      # flared walls
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    # horizontal cuts up the walls so they deform/shade as pressed sheet steel
    wall_edges = [e for e in bm.edges if abs(e.verts[0].co.z - e.verts[1].co.z) > 1e-4]
    bmesh.ops.subdivide_edges(bm, edges=wall_edges, cuts=2, use_grid_fill=False)
    obj = link(mesh_from_bm("Tray", bm), MAT_TRAY)
    obj.rotation_euler = (0, math.atan2(HANDLE_REAR.z - HANDLE_FRONT.z,
                                        HANDLE_FRONT.x - HANDLE_REAR.x), 0)
    obj.location = (0.02, 0.0, 0.455)

    sol = obj.modifiers.new("Solidify", 'SOLIDIFY')
    sol.thickness = 0.013
    sol.offset = -1.0
    sol.use_rim = True
    add_bevel(obj, 0.005, segments=2)
    auto_smooth(obj)
    return obj

tray = build_tray()

# ---------------------------------------------------------------- wheel assembly
# fork brackets running from the handle ends down and inward to the axle
for side, tag in ((1, "L"), (-1, "R")):
    top = handle_point(0.97, side) + Vector((0, 0, -0.02))
    bot = Vector((WHEEL_CENTER.x, AXLE_HALF_W * side, WHEEL_CENTER.z))
    beam(f"Fork_{tag}", top, bot, 0.030, 0.075, MAT_FRAME, bevel=0.005)
    # short stay back under the tray front for stiffness
    beam(f"Stay_{tag}", bot, handle_point(0.78, side) + Vector((0, 0, -0.03)),
         0.022, 0.030, MAT_FRAME, bevel=0.004)

axle = cylinder("Axle", 0.019, AXLE_HALF_W * 2 + 0.03, WHEEL_CENTER,
                rot=(math.radians(90), 0, 0), mat=MAT_HUB, verts=20)

# tyre: swept pneumatic profile
bm = bmesh.new()
major, minor, mseg, nseg = WHEEL_R - 0.045, 0.045, 56, 18
for i in range(mseg):
    a = 2 * math.pi * i / mseg
    for j in range(nseg):
        b_ = 2 * math.pi * j / nseg
        r = major + minor * math.cos(b_)
        z = minor * math.sin(b_) * 0.85
        bm.verts.new((r * math.cos(a), r * math.sin(a), z))
bm.verts.ensure_lookup_table()
for i in range(mseg):
    for j in range(nseg):
        v0 = i * nseg + j
        v1 = i * nseg + (j + 1) % nseg
        v2 = ((i + 1) % mseg) * nseg + (j + 1) % nseg
        v3 = ((i + 1) % mseg) * nseg + j
        bm.faces.new((bm.verts[v0], bm.verts[v1], bm.verts[v2], bm.verts[v3]))
bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
tyre = link(mesh_from_bm("Tyre", bm), MAT_RUBBER)
tyre.location = WHEEL_CENTER
tyre.rotation_euler = (math.radians(90), 0, 0)
for p in tyre.data.polygons:
    p.use_smooth = True

# rim disc, hub and spokes
rim = cylinder("Rim", WHEEL_R - 0.055, 0.062, WHEEL_CENTER,
               rot=(math.radians(90), 0, 0), mat=MAT_HUB, verts=48)
hub = cylinder("Hub", 0.052, 0.10, WHEEL_CENTER,
               rot=(math.radians(90), 0, 0), mat=MAT_HUB, verts=24)

for k in range(6):
    a = 2 * math.pi * k / 6
    off = Vector((math.cos(a), 0.0, math.sin(a))) * ((WHEEL_R - 0.055) * 0.5)
    box(f"Spoke_{k}", (WHEEL_R - 0.06, 0.020, 0.020),
        loc=WHEEL_CENTER + off, rot=(0, -a, 0), mat=MAT_HUB, bevel=0.003)

# ---------------------------------------------------------------- legs / supports
LEG_X = -0.60
for side, tag in ((1, "L"), (-1, "R")):
    top = handle_point(t_at_x(LEG_X), side)
    top = Vector((LEG_X, top.y, top.z - 0.02))
    foot = Vector((LEG_X - 0.06, top.y + 0.035 * side, 0.03))
    beam(f"Leg_{tag}", top, foot, 0.038, 0.038, MAT_FRAME, bevel=0.005)
    # skid pad on the ground
    box(f"Foot_{tag}", (0.16, 0.055, 0.030),
        loc=(LEG_X - 0.06, foot.y, 0.016), mat=MAT_FRAME, bevel=0.006)
    # diagonal knee brace from leg back up to the handle
    beam(f"LegBrace_{tag}", foot + Vector((0.0, 0, 0.10)),
         handle_point(t_at_x(-0.92), side) + Vector((0, 0, -0.03)),
         0.022, 0.022, MAT_FRAME, bevel=0.004)

# bar joining the two feet
beam("FootBar",
     (LEG_X - 0.06, -0.29, 0.03), (LEG_X - 0.06, 0.29, 0.03),
     0.032, 0.032, MAT_FRAME, bevel=0.004)

# ---------------------------------------------------------------- ground
bm = bmesh.new()
bmesh.ops.create_grid(bm, x_segments=12, y_segments=12, size=6.0)
ground = link(mesh_from_bm("Ground", bm), MAT_GROUND)
ground.location = (0, 0, 0)

# ---------------------------------------------------------------- lighting
world = bpy.data.worlds.new("World")
world.use_nodes = True
world.node_tree.nodes["Background"].inputs["Color"].default_value = (0.30, 0.38, 0.48, 1.0)
world.node_tree.nodes["Background"].inputs["Strength"].default_value = 0.65
scene.world = world

sun_data = bpy.data.lights.new("Sun", 'SUN')
sun_data.energy = 3.2
sun_data.angle = math.radians(2.5)
sun_data.color = (1.0, 0.96, 0.90)
sun = link(bpy.data.objects.new("Sun", sun_data))
sun.location = (3.0, -3.5, 5.0)
sun.rotation_euler = (math.radians(52), 0, math.radians(38))

fill_data = bpy.data.lights.new("Fill", 'AREA')
fill_data.energy = 180.0
fill_data.size = 3.0
fill = link(bpy.data.objects.new("Fill", fill_data))
fill.location = (-2.6, 2.4, 2.4)
fill.rotation_euler = (math.radians(58), 0, math.radians(-135))

rim_data = bpy.data.lights.new("RimLight", 'AREA')
rim_data.energy = 90.0
rim_data.size = 1.6
rimlight = link(bpy.data.objects.new("RimLight", rim_data))
rimlight.location = (2.6, 2.2, 1.6)
rimlight.rotation_euler = (math.radians(72), 0, math.radians(130))

# ---------------------------------------------------------------- camera
cam_data = bpy.data.cameras.new("Camera")
cam_data.lens = 55.0
cam = link(bpy.data.objects.new("Camera", cam_data))
cam.location = (2.55, -2.65, 1.55)
target = Vector((-0.05, 0.0, 0.45))
cam.rotation_euler = (target - cam.location).to_track_quat('-Z', 'Y').to_euler()
scene.camera = cam

bpy.context.view_layer.update()
