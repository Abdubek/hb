import bpy
from mathutils import Vector

POST_X = 1.75
POST_Y = 1.20
POST_H = 2.50
POST_W = 0.14
BEAM_Z = POST_H + 0.15
RAFTER_Z = BEAM_Z + 0.15 + 0.11
SLAT_Z = RAFTER_Z + 0.11 + 0.045


def clear_scene():
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete(use_global=False)


def make_material(name, color, roughness=0.7, metallic=0.0):
    mat = bpy.data.materials.new(name)
    mat.use_nodes = True
    bsdf = mat.node_tree.nodes["Principled BSDF"]
    bsdf.inputs["Base Color"].default_value = (color[0], color[1], color[2], 1.0)
    bsdf.inputs["Roughness"].default_value = roughness
    bsdf.inputs["Metallic"].default_value = metallic
    return mat


def add_beam(name, size, location, mat):
    """Axis-aligned timber member; size is full width/depth/height."""
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=location)
    obj = bpy.context.object
    obj.name = name
    obj.scale = size
    obj.data.materials.append(mat)
    return obj


def add_foliage(name, radius, location, mat):
    bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=2, radius=radius, location=location)
    obj = bpy.context.object
    obj.name = name
    obj.scale = (1.0, 1.0, 0.75)
    obj.data.materials.append(mat)
    bpy.ops.object.shade_smooth()
    return obj


def build_posts(mat_post, mat_stone):
    for ix, xtag in ((1, "E"), (-1, "W")):
        for iy, ytag in ((1, "N"), (-1, "S")):
            x, y = ix * POST_X, iy * POST_Y
            add_beam("Post_%s%s" % (ytag, xtag), (POST_W, POST_W, POST_H),
                     (x, y, POST_H * 0.5), mat_post)
            add_beam("Footing_%s%s" % (ytag, xtag), (0.30, 0.30, 0.18),
                     (x, y, 0.09), mat_stone)
            # diagonal-look corner braces, built as short blocks under the beam
            add_beam("Brace_%s%s" % (ytag, xtag), (0.09, 0.34, 0.34),
                     (x, y - iy * 0.22, POST_H - 0.22), mat_post)


def build_canopy(mat_beam, mat_rafter, mat_slat):
    for ix, xtag in ((1, "E"), (-1, "W")):
        for off, side in ((0.13, "Out"), (-0.13, "In")):
            add_beam("Beam_%s_%s" % (xtag, side), (0.09, 2.95, 0.30),
                     (ix * POST_X + ix * off, 0.0, BEAM_Z), mat_beam)

    n_rafters = 7
    for i in range(n_rafters):
        t = i / (n_rafters - 1.0)
        y = -1.35 + t * 2.70
        add_beam("Rafter_%02d" % i, (4.30, 0.09, 0.22), (0.0, y, RAFTER_Z), mat_rafter)

    n_slats = 15
    for i in range(n_slats):
        t = i / (n_slats - 1.0)
        x = -1.96 + t * 3.92
        add_beam("Slat_%02d" % i, (0.06, 3.05, 0.09), (x, 0.0, SLAT_Z), mat_slat)


def build_furniture(mat_post, mat_slat, mat_terracotta, mat_leaf):
    add_beam("BenchSeat", (2.10, 0.44, 0.07), (0.0, -1.02, 0.46), mat_slat)
    add_beam("BenchBack", (2.10, 0.07, 0.38), (0.0, -1.22, 0.68), mat_slat)
    for ix in (1, -1):
        add_beam("BenchLeg_%s" % ("E" if ix > 0 else "W"), (0.09, 0.40, 0.44),
                 (ix * 0.90, -1.02, 0.22), mat_post)

    for ix, tag in ((1, "E"), (-1, "W")):
        px, py = ix * 1.55, 0.95
        add_beam("Planter_%s" % tag, (0.50, 0.50, 0.42), (px, py, 0.21), mat_terracotta)
        add_beam("PlanterRim_%s" % tag, (0.56, 0.56, 0.06), (px, py, 0.44), mat_terracotta)
        add_foliage("Shrub_%s" % tag, 0.34, (px, py, 0.66), mat_leaf)
        add_foliage("ShrubTop_%s" % tag, 0.22, (px - ix * 0.14, py + 0.10, 0.90), mat_leaf)


clear_scene()

m_post = make_material("TimberDark", (0.32, 0.20, 0.12), roughness=0.75)
m_beam = make_material("TimberBeam", (0.46, 0.30, 0.17), roughness=0.7)
m_rafter = make_material("TimberRafter", (0.52, 0.35, 0.20), roughness=0.68)
m_slat = make_material("TimberSlat", (0.60, 0.43, 0.26), roughness=0.66)
m_stone = make_material("StoneFooting", (0.55, 0.54, 0.51), roughness=0.9)
m_paving = make_material("Paving", (0.68, 0.66, 0.62), roughness=0.88)
m_lawn = make_material("Lawn", (0.22, 0.36, 0.14), roughness=0.95)
m_terracotta = make_material("Terracotta", (0.63, 0.31, 0.19), roughness=0.72)
m_leaf = make_material("Foliage", (0.18, 0.42, 0.16), roughness=0.85)

bpy.ops.mesh.primitive_plane_add(size=14.0, location=(0.0, 0.0, -0.02))
bpy.context.object.name = "Lawn"
bpy.context.object.data.materials.append(m_lawn)

add_beam("PatioSlab", (4.60, 3.50, 0.10), (0.0, 0.0, 0.03), m_paving)

build_posts(m_post, m_stone)
build_canopy(m_beam, m_rafter, m_slat)
build_furniture(m_post, m_slat, m_terracotta, m_leaf)

bpy.ops.object.light_add(type='SUN', location=(5.0, -4.0, 9.0))
sun = bpy.context.object
sun.name = "SunLight"
sun.data.energy = 4.5
sun.data.angle = 0.06
sun.rotation_euler = Vector((-5.0, 4.0, -9.0)).to_track_quat('-Z', 'Y').to_euler()

bpy.ops.object.light_add(type='AREA', location=(-4.5, 3.5, 4.0))
fill = bpy.context.object
fill.name = "SkyFill"
fill.data.energy = 400.0
fill.data.size = 6.0
fill.rotation_euler = Vector((4.5, -3.5, -3.0)).to_track_quat('-Z', 'Y').to_euler()

cam_loc = Vector((6.2, -6.4, 4.1))
target = Vector((0.0, 0.0, 1.55))
cam_data = bpy.data.cameras.new("PergolaCam")
cam_data.lens = 40.0
cam = bpy.data.objects.new("Camera", cam_data)
bpy.context.collection.objects.link(cam)
cam.location = cam_loc
cam.rotation_euler = (target - cam_loc).to_track_quat('-Z', 'Y').to_euler()
bpy.context.scene.camera = cam
