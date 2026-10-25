"""Greenhouse with aluminium frame, gabled glass roof and wooden planting tables."""
import bpy
import bmesh
from math import atan2, sqrt
from mathutils import Vector

W, L = 6.0, 8.0          # footprint (x, y)
EAVE, RIDGE = 2.4, 3.6   # wall top / ridge height
SLOPE = atan2(RIDGE - EAVE, W * 0.5)
RAFTER = sqrt((W * 0.5) ** 2 + (RIDGE - EAVE) ** 2)
BAYS = [-4.0, -2.0, 0.0, 2.0, 4.0]


def clear_scene():
    for obj in list(bpy.data.objects):
        bpy.data.objects.remove(obj, do_unlink=True)


def make_material(name, color, roughness=0.5, metallic=0.0, alpha=1.0):
    mat = bpy.data.materials.new(name)
    mat.use_nodes = True
    bsdf = mat.node_tree.nodes["Principled BSDF"]
    bsdf.inputs["Base Color"].default_value = (*color, 1.0)
    bsdf.inputs["Roughness"].default_value = roughness
    bsdf.inputs["Metallic"].default_value = metallic
    if alpha < 1.0:
        bsdf.inputs["Alpha"].default_value = alpha
        if hasattr(mat, "surface_render_method"):
            mat.surface_render_method = 'BLENDED'
        elif hasattr(mat, "blend_method"):
            mat.blend_method = 'BLEND'
    return mat


def box(name, size, location, rotation=(0.0, 0.0, 0.0), material=None):
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=location, rotation=rotation)
    obj = bpy.context.active_object
    obj.name = name
    obj.scale = size
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    if material:
        obj.data.materials.append(material)
    return obj


def cylinder(name, radius, depth, location, material=None):
    bpy.ops.mesh.primitive_cylinder_add(radius=radius, depth=depth, vertices=16, location=location)
    obj = bpy.context.active_object
    obj.name = name
    if material:
        obj.data.materials.append(material)
    return obj


def gable_panel(name, y, material):
    """Flat triangular glazing that closes off one end wall above the eave."""
    mesh = bpy.data.meshes.new(name)
    obj = bpy.data.objects.new(name, mesh)
    bpy.context.collection.objects.link(obj)
    bm = bmesh.new()
    verts = [bm.verts.new(v) for v in ((-W * 0.5, y, EAVE), (W * 0.5, y, EAVE), (0.0, y, RIDGE))]
    bm.faces.new(verts)
    bm.to_mesh(mesh)
    bm.free()
    mesh.materials.append(material)
    return obj


def add_camera(location, target, lens=35.0):
    cam_data = bpy.data.cameras.new("GreenhouseCamData")
    cam_data.lens = lens
    cam = bpy.data.objects.new("GreenhouseCamera", cam_data)
    bpy.context.collection.objects.link(cam)
    cam.location = location
    cam.rotation_euler = (Vector(target) - Vector(location)).to_track_quat('-Z', 'Y').to_euler()
    bpy.context.scene.camera = cam


clear_scene()
alu = make_material("AluminiumFrame", (0.72, 0.74, 0.76), roughness=0.35, metallic=0.9)
glass = make_material("Glazing", (0.75, 0.85, 0.85), roughness=0.08, alpha=0.22)
concrete = make_material("Concrete", (0.62, 0.61, 0.58), roughness=0.85)
wood = make_material("TableWood", (0.46, 0.31, 0.17), roughness=0.7)
soil = make_material("Soil", (0.16, 0.11, 0.07), roughness=0.95)
terracotta = make_material("Terracotta", (0.63, 0.29, 0.17), roughness=0.8)
foliage = make_material("Foliage", (0.18, 0.42, 0.14), roughness=0.75)

# ground and foundation
box("Ground", (26.0, 26.0, 0.2), (0.0, 0.0, -0.32), material=concrete)
box("FoundationSlab", (W + 0.5, L + 0.5, 0.25), (0.0, 0.0, -0.1), material=concrete)

# vertical frame
for i, y in enumerate(BAYS):
    for sx in (-1.0, 1.0):
        box("Post_%s%d" % ("R" if sx > 0 else "L", i), (0.12, 0.12, EAVE),
            (sx * W * 0.5, y, EAVE * 0.5), material=alu)
for i, y in enumerate((-L * 0.5, L * 0.5)):
    box("GablePost_%d" % i, (0.12, 0.12, RIDGE), (0.0, y, RIDGE * 0.5), material=alu)

# eave beams, ridge beam and rafters
for sx in (-1.0, 1.0):
    box("EaveBeam_%s" % ("R" if sx > 0 else "L"), (0.14, L + 0.2, 0.14),
        (sx * W * 0.5, 0.0, EAVE), material=alu)
box("RidgeBeam", (0.14, L + 0.2, 0.18), (0.0, 0.0, RIDGE), material=alu)
for i, y in enumerate(BAYS):
    for sx in (-1.0, 1.0):
        box("Rafter_%s%d" % ("R" if sx > 0 else "L", i), (RAFTER, 0.09, 0.12),
            (sx * W * 0.25, y, (EAVE + RIDGE) * 0.5),
            rotation=(0.0, sx * SLOPE, 0.0), material=alu)

# glazing: roof slopes, side walls, end walls and gables
for sx in (-1.0, 1.0):
    box("RoofGlass_%s" % ("R" if sx > 0 else "L"), (RAFTER, L, 0.04),
        (sx * W * 0.25, 0.0, (EAVE + RIDGE) * 0.5),
        rotation=(0.0, sx * SLOPE, 0.0), material=glass)
    box("SideGlass_%s" % ("R" if sx > 0 else "L"), (0.04, L - 0.1, EAVE - 0.1),
        (sx * W * 0.5, 0.0, EAVE * 0.5), material=glass)
for sy, tag in ((-1.0, "Front"), (1.0, "Back")):
    box("EndGlass_%s" % tag, (W - 0.1, 0.04, EAVE - 0.1), (0.0, sy * L * 0.5, EAVE * 0.5),
        material=glass)
    gable_panel("GableGlass_%s" % tag, sy * (L * 0.5 - 0.01), glass)

# entrance door on the front gable end
for sx in (-1.0, 1.0):
    box("DoorJamb_%s" % ("R" if sx > 0 else "L"), (0.08, 0.16, 2.05),
        (sx * 0.55, -L * 0.5, 1.02), material=alu)
box("DoorHeader", (1.18, 0.16, 0.1), (0.0, -L * 0.5, 2.1), material=alu)
box("DoorPanel", (1.0, 0.05, 1.95), (0.0, -L * 0.5 - 0.08, 1.0), material=glass)

# planting tables along both side walls
for sx in (-1.0, 1.0):
    tag = "R" if sx > 0 else "L"
    box("TableTop_%s" % tag, (1.0, 6.0, 0.06), (sx * 1.85, 0.0, 0.85), material=wood)
    box("TableTray_%s" % tag, (0.86, 5.8, 0.05), (sx * 1.85, 0.0, 0.9), material=soil)
    for j, y in enumerate((-2.7, -0.9, 0.9, 2.7)):
        for k, ox in enumerate((-0.42, 0.42)):
            box("TableLeg_%s%d%d" % (tag, j, k), (0.07, 0.07, 0.82),
                (sx * 1.85 + ox, y, 0.41), material=wood)
    for j, y in enumerate((-2.4, -1.2, 0.0, 1.2, 2.4)):
        cylinder("Pot_%s%d" % (tag, j), 0.13, 0.24, (sx * 1.85, y, 1.04), material=terracotta)
        cylinder("PotPlant_%s%d" % (tag, j), 0.09, 0.26, (sx * 1.85, y, 1.28), material=foliage)

sun_data = bpy.data.lights.new("SunLight", type='SUN')
sun_data.energy = 4.0
sun = bpy.data.objects.new("Sun", sun_data)
bpy.context.collection.objects.link(sun)
sun.location = (6.0, -6.0, 10.0)
sun.rotation_euler = (0.7, 0.2, 0.6)

add_camera((10.0, -11.0, 6.0), (0.0, 0.0, 1.5))
