import bpy
import bmesh
from mathutils import Vector

# ---------------------------------------------------------------- helpers

def clear_scene():
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete(use_global=False)
    for block in (bpy.data.meshes, bpy.data.materials, bpy.data.cameras):
        for item in list(block):
            if item.users == 0:
                block.remove(item)


def make_material(name, color, roughness=0.5, metallic=0.0, alpha=1.0):
    mat = bpy.data.materials.new(name)
    mat.use_nodes = True
    bsdf = mat.node_tree.nodes["Principled BSDF"]
    bsdf.inputs["Base Color"].default_value = (*color, alpha)
    bsdf.inputs["Roughness"].default_value = roughness
    bsdf.inputs["Metallic"].default_value = metallic
    bsdf.inputs["Alpha"].default_value = alpha
    if alpha < 1.0:
        # glass-like panels: transmissive and blended in the viewport
        bsdf.inputs["Transmission Weight"].default_value = 0.9
        if hasattr(mat, "surface_render_method"):
            mat.surface_render_method = 'BLENDED'
        if hasattr(mat, "blend_method"):
            mat.blend_method = 'BLEND'
        mat.use_backface_culling = False
    return mat


def add_box(name, size, location, material, rotation=(0.0, 0.0, 0.0)):
    """Axis-aligned box of full dimensions `size` centred on `location`."""
    mesh = bpy.data.meshes.new(name)
    bm = bmesh.new()
    bmesh.ops.create_cube(bm, size=1.0)
    bmesh.ops.scale(bm, vec=Vector(size), verts=bm.verts)
    bm.to_mesh(mesh)
    bm.free()
    obj = bpy.data.objects.new(name, mesh)
    obj.location = location
    obj.rotation_euler = rotation
    obj.data.materials.append(material)
    bpy.context.collection.objects.link(obj)
    return obj


def add_tube(name, radius, height, location, material, segments=16):
    mesh = bpy.data.meshes.new(name)
    bm = bmesh.new()
    bmesh.ops.create_cone(bm, cap_ends=True, cap_tris=False, segments=segments,
                          radius1=radius, radius2=radius, depth=height)
    bm.to_mesh(mesh)
    bm.free()
    obj = bpy.data.objects.new(name, mesh)
    obj.location = location
    obj.data.materials.append(material)
    bpy.context.collection.objects.link(obj)
    return obj


def aim_camera(camera, target):
    direction = Vector(target) - camera.location
    camera.rotation_euler = direction.to_track_quat('-Z', 'Y').to_euler()


# ---------------------------------------------------------------- materials

clear_scene()

mat_frame = make_material("MAT_Frame_Steel", (0.28, 0.30, 0.33), roughness=0.35, metallic=0.9)
mat_glass = make_material("MAT_Panel_Glass", (0.72, 0.82, 0.85), roughness=0.05, alpha=0.18)
mat_roof = make_material("MAT_Roof_Panel", (0.13, 0.14, 0.16), roughness=0.4, metallic=0.6)
mat_bench = make_material("MAT_Bench_Slat", (0.45, 0.28, 0.13), roughness=0.65)
mat_ground = make_material("MAT_Pavement", (0.52, 0.52, 0.50), roughness=0.9)
mat_sign = make_material("MAT_Sign_Red", (0.62, 0.08, 0.09), roughness=0.4)

# ---------------------------------------------------------------- dimensions

W, D, H = 4.0, 1.6, 2.5          # shelter width, depth, post height
POST = 0.09                       # square post section

add_box("Pavement", (9.0, 6.0, 0.12), (0.0, 0.0, -0.06), mat_ground)

# ---------------------------------------------------------------- frame

for i, x in enumerate((-W / 2 + POST / 2, W / 2 - POST / 2)):
    for j, y in enumerate((-D / 2 + POST / 2, D / 2 - POST / 2)):
        add_box("Post_%d%d" % (i, j), (POST, POST, H), (x, y, H / 2), mat_frame)

# top rails tying the posts together, front and back
for tag, y in (("Back", D / 2 - POST / 2), ("Front", -D / 2 + POST / 2)):
    add_box("TopRail_" + tag, (W, POST, POST), (0.0, y, H - POST / 2), mat_frame)
for tag, x in (("Left", -W / 2 + POST / 2), ("Right", W / 2 - POST / 2)):
    add_box("SideRail_" + tag, (POST, D, POST), (x, 0.0, H - POST / 2), mat_frame)

# ---------------------------------------------------------------- roof

roof = add_box("Roof_Panel", (W + 0.5, D + 0.7, 0.10),
               (0.0, -0.12, H + 0.13), mat_roof, rotation=(-0.06, 0.0, 0.0))
add_box("Roof_Fascia", (W + 0.5, 0.06, 0.16), (0.0, -(D + 0.7) / 2 - 0.10, H + 0.16), mat_roof)

# ---------------------------------------------------------------- glazing

GLASS_T = 0.02
glass_h = H - 0.35
add_box("Panel_Back", (W - 2 * POST, GLASS_T, glass_h),
        (0.0, D / 2 - POST, 0.2 + glass_h / 2), mat_glass)
for tag, x in (("Left", -W / 2 + POST), ("Right", W / 2 - POST)):
    add_box("Panel_Side_" + tag, (GLASS_T, D - 2 * POST, glass_h),
            (x, 0.0, 0.2 + glass_h / 2), mat_glass)
# short entry wing on the open front, right hand side
add_box("Panel_Front_Wing", (0.9, GLASS_T, glass_h),
        (W / 2 - 0.55, -D / 2 + POST, 0.2 + glass_h / 2), mat_glass)

# ---------------------------------------------------------------- bench

bench_z = 0.46
bench_y = D / 2 - 0.32
for i in range(3):
    add_box("Bench_Slat_%d" % i, (W - 0.9, 0.14, 0.045),
            (0.0, bench_y - i * 0.18, bench_z), mat_bench)
for i, x in enumerate((-W / 2 + 0.7, 0.0, W / 2 - 0.7)):
    add_box("Bench_Bracket_%d" % i, (0.06, 0.5, 0.05), (x, bench_y - 0.18, bench_z - 0.05), mat_frame)
    add_tube("Bench_Leg_%d" % i, 0.035, bench_z - 0.05, (x, bench_y - 0.10, (bench_z - 0.05) / 2), mat_frame)
add_box("Bench_Backrest", (W - 0.9, 0.05, 0.20), (0.0, D / 2 - 0.15, 0.95),
        mat_bench, rotation=(0.18, 0.0, 0.0))

# ---------------------------------------------------------------- signage

add_box("Sign_Board", (0.85, 0.05, 0.45), (-W / 2 + 0.55, -D / 2 + POST - 0.05, H - 0.55), mat_sign)
add_tube("Sign_Post", 0.05, 3.1, (W / 2 + 0.6, -D / 2 - 0.3, 1.55), mat_frame)
add_box("Sign_Flag", (0.5, 0.04, 0.5), (W / 2 + 0.6, -D / 2 - 0.34, 2.85), mat_sign)
add_tube("Litter_Bin", 0.20, 0.72, (W / 2 - 0.45, -D / 2 + 0.45, 0.36), mat_frame, segments=20)

# ---------------------------------------------------------------- lighting

sun_data = bpy.data.lights.new("Sun", type='SUN')
sun_data.energy = 3.5
sun = bpy.data.objects.new("Key_Sun", sun_data)
sun.location = (5.0, -6.0, 8.0)
sun.rotation_euler = (0.9, 0.15, 0.7)
bpy.context.collection.objects.link(sun)

fill_data = bpy.data.lights.new("Fill", type='AREA')
fill_data.energy = 220.0
fill_data.size = 5.0
fill = bpy.data.objects.new("Fill_Area", fill_data)
fill.location = (-4.5, -5.0, 3.2)
bpy.context.collection.objects.link(fill)
aim_camera(fill, (0.0, 0.0, 1.2))

# ---------------------------------------------------------------- camera

cam_data = bpy.data.cameras.new("ShelterCam")
cam_data.lens = 35.0
cam = bpy.data.objects.new("Camera", cam_data)
cam.location = (6.2, -6.8, 3.4)
bpy.context.collection.objects.link(cam)
aim_camera(cam, (0.0, 0.0, 1.15))
bpy.context.scene.camera = cam
