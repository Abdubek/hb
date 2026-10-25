"""Public drinking fountain: concrete pedestal with an adult and a child basin."""
import bpy
import bmesh
from math import radians
from mathutils import Vector

COLUMN_H = 1.05
UPPER_Z = 1.02
LOWER_Z = 0.72


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


def cylinder(name, radius, depth, location, rotation=(0.0, 0.0, 0.0), material=None, verts=24):
    bpy.ops.mesh.primitive_cylinder_add(radius=radius, depth=depth, vertices=verts,
                                        location=location, rotation=rotation)
    obj = bpy.context.active_object
    obj.name = name
    if material:
        obj.data.materials.append(material)
    return obj


def basin(name, location, outer=0.24, depth=0.16, wall=0.03, material=None):
    """Hollowed bowl: a capped cylinder whose top face is inset and pushed down."""
    mesh = bpy.data.meshes.new(name)
    obj = bpy.data.objects.new(name, mesh)
    bpy.context.collection.objects.link(obj)
    bm = bmesh.new()
    bmesh.ops.create_cone(bm, cap_ends=True, cap_tris=False, segments=32,
                          radius1=outer * 0.82, radius2=outer, depth=depth)
    top = max(bm.faces, key=lambda f: f.calc_center_median().z)
    bmesh.ops.inset_individual(bm, faces=[top], thickness=wall, depth=0.0)
    bmesh.ops.translate(bm, verts=list(top.verts), vec=(0.0, 0.0, -(depth - wall)))
    bm.normal_update()
    bm.to_mesh(mesh)
    bm.free()
    for poly in mesh.polygons:
        poly.use_smooth = abs(poly.normal.z) < 0.7
    if material:
        mesh.materials.append(material)
    obj.location = location
    return obj


def spout_and_controls(tag, cx, basin_z, metal, chrome, dark, water):
    """Bubbler nozzle, push button, drain grate and a small arc of water."""
    cylinder("BubblerStem_%s" % tag, 0.022, 0.09, (cx, 0.06, basin_z + 0.08), material=chrome)
    cylinder("BubblerNozzle_%s" % tag, 0.018, 0.09, (cx, 0.02, basin_z + 0.13),
             rotation=(radians(55.0), 0.0, 0.0), material=chrome)
    cylinder("PushButton_%s" % tag, 0.025, 0.03, (cx, -0.19, basin_z + 0.02),
             rotation=(radians(90.0), 0.0, 0.0), material=metal)
    cylinder("DrainGrate_%s" % tag, 0.045, 0.012, (cx, -0.02, basin_z - 0.055), material=dark)
    for i in range(6):
        t = i / 5.0
        y = 0.0 - 0.11 * t
        z = basin_z + 0.17 + 0.05 * t - 0.16 * t * t
        bpy.ops.mesh.primitive_uv_sphere_add(radius=0.014, segments=10, ring_count=6,
                                             location=(cx, y, z))
        drop = bpy.context.active_object
        drop.name = "WaterArc_%s_%d" % (tag, i)
        drop.data.materials.append(water)


def add_camera(location, target, lens=45.0):
    cam_data = bpy.data.cameras.new("FountainCamData")
    cam_data.lens = lens
    cam = bpy.data.objects.new("FountainCamera", cam_data)
    bpy.context.collection.objects.link(cam)
    cam.location = location
    cam.rotation_euler = (Vector(target) - Vector(location)).to_track_quat('-Z', 'Y').to_euler()
    bpy.context.scene.camera = cam


clear_scene()
concrete = make_material("Concrete", (0.60, 0.59, 0.56), roughness=0.85)
paving = make_material("Paving", (0.45, 0.44, 0.42), roughness=0.95)
metal = make_material("StainlessSteel", (0.70, 0.71, 0.73), roughness=0.3, metallic=0.9)
chrome = make_material("Chrome", (0.85, 0.86, 0.88), roughness=0.08, metallic=1.0)
dark = make_material("DarkGrate", (0.09, 0.09, 0.10), roughness=0.6, metallic=0.4)
water = make_material("Water", (0.55, 0.75, 0.85), roughness=0.05, alpha=0.4)

# paving and plinth
box("Paving", (6.0, 6.0, 0.12), (0.0, 0.0, -0.06), material=paving)
cylinder("Plinth", 0.62, 0.1, (0.0, 0.0, 0.05), material=concrete, verts=32)

# main pedestal, with a stepped shoulder under each basin
box("Pedestal", (0.92, 0.34, COLUMN_H), (0.0, 0.0, 0.1 + COLUMN_H * 0.5), material=concrete)
box("PedestalCap", (0.98, 0.40, 0.05), (0.0, 0.0, 0.1 + COLUMN_H + 0.02), material=concrete)
box("ServiceHatch", (0.30, 0.03, 0.36), (0.0, 0.18, 0.42), material=metal)

# adult basin (left, high) and child basin (right, low)
basin("UpperBasin", (-0.30, -0.26, UPPER_Z), outer=0.25, depth=0.17, material=metal)
basin("LowerBasin", (0.30, -0.26, LOWER_Z), outer=0.22, depth=0.15, material=metal)
for tag, cx, bz, w in (("Upper", -0.30, UPPER_Z, 0.30), ("Lower", 0.30, LOWER_Z, 0.26)):
    box("BasinBracket_%s" % tag, (w, 0.22, 0.07), (cx, -0.12, bz - 0.10), material=metal)
    box("Splashback_%s" % tag, (w + 0.06, 0.04, 0.20), (cx, 0.02, bz + 0.09), material=metal)

spout_and_controls("Upper", -0.30, UPPER_Z, metal, chrome, dark, water)
spout_and_controls("Lower", 0.30, LOWER_Z, metal, chrome, dark, water)

# signage plate and floor drain
box("SignPlate", (0.26, 0.02, 0.12), (0.0, -0.18, 0.92), material=metal)
cylinder("FloorDrain", 0.07, 0.02, (0.0, -0.45, 0.105), material=dark)

sun_data = bpy.data.lights.new("SunLight", type='SUN')
sun_data.energy = 4.0
sun = bpy.data.objects.new("Sun", sun_data)
bpy.context.collection.objects.link(sun)
sun.location = (2.0, -2.5, 4.0)
sun.rotation_euler = (radians(45.0), 0.0, radians(30.0))

add_camera((1.9, -2.3, 1.7), (0.0, -0.1, 0.85))
