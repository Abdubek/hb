import bpy
import bmesh
import math
from mathutils import Vector

BAR_L = 2.4          # slat length
SLAT_H = 0.26        # slat height
SLAT_D = 0.05        # slat thickness
STRIPES = 8          # number of hazard stripes per slat
TOP_Z = 1.12         # apex height of the A-frame legs


def clear_scene():
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete(use_global=False)
    for coll in (bpy.data.meshes, bpy.data.materials, bpy.data.cameras, bpy.data.lights):
        for item in list(coll):
            if item.users == 0:
                coll.remove(item)


def make_material(name, color, roughness=0.5, metallic=0.0, emission=0.0):
    mat = bpy.data.materials.new(name)
    mat.use_nodes = True
    bsdf = mat.node_tree.nodes["Principled BSDF"]
    bsdf.inputs["Base Color"].default_value = (*color, 1.0)
    bsdf.inputs["Roughness"].default_value = roughness
    bsdf.inputs["Metallic"].default_value = metallic
    if emission > 0.0:
        bsdf.inputs["Emission Color"].default_value = (*color, 1.0)
        bsdf.inputs["Emission Strength"].default_value = emission
    return mat


def add_box(name, size, location, rotation=(0.0, 0.0, 0.0), mat=None):
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=location, rotation=rotation)
    obj = bpy.context.active_object
    obj.name = name
    obj.scale = size
    if mat:
        obj.data.materials.append(mat)
    return obj


def striped_slat(name, z, mats):
    """One barricade board built from alternating orange / white stripe blocks."""
    mesh = bpy.data.meshes.new(name)
    bm = bmesh.new()
    seg = BAR_L / STRIPES
    for i in range(STRIPES):
        verts = bmesh.ops.create_cube(bm, size=1.0)["verts"]
        bmesh.ops.scale(bm, vec=(seg, SLAT_D, SLAT_H), verts=verts)
        bmesh.ops.translate(bm, vec=(-BAR_L * 0.5 + seg * (i + 0.5), 0.0, 0.0), verts=verts)
        faces = set()
        for v in verts:
            faces.update(v.link_faces)
        for f in faces:
            f.material_index = i % 2
    bm.normal_update()
    bm.to_mesh(mesh)
    bm.free()
    obj = bpy.data.objects.new(name, mesh)
    bpy.context.collection.objects.link(obj)
    obj.location = (0.0, 0.0, z)
    for m in mats:
        obj.data.materials.append(m)
    return obj


def a_frame(x, steel, rubber):
    """Two splayed legs meeting at the apex, sitting on a rubber foot pad."""
    spread = 0.34
    angle = math.atan2(spread, TOP_Z)
    leg_len = math.hypot(spread, TOP_Z)
    for s in (1, -1):
        add_box("Leg_%s" % ("F" if s > 0 else "B"),
                (0.07, 0.05, leg_len),
                (x, s * spread * 0.5, TOP_Z * 0.5),
                (s * angle, 0.0, 0.0), steel)
    add_box("Foot", (0.13, spread * 2.3, 0.06), (x, 0.0, 0.03), mat=rubber)
    add_box("LegBrace", (0.05, spread * 1.6, 0.04), (x, 0.0, 0.32), mat=steel)


def aim(obj, target):
    direction = Vector(target) - obj.location
    obj.rotation_euler = direction.to_track_quat('-Z', 'Y').to_euler()


clear_scene()
orange = make_material("HazardOrange", (0.85, 0.26, 0.03), roughness=0.45)
white = make_material("HazardWhite", (0.88, 0.88, 0.85), roughness=0.45)
steel = make_material("GalvSteel", (0.55, 0.56, 0.58), roughness=0.35, metallic=0.85)
rubber = make_material("FootRubber", (0.06, 0.06, 0.07), roughness=0.85)
amber = make_material("BeaconAmber", (1.0, 0.55, 0.05), roughness=0.25, emission=4.0)
asphalt = make_material("Asphalt", (0.19, 0.19, 0.2), roughness=0.95)

ground = add_box("Ground", (14.0, 14.0, 0.05), (0.0, 0.0, -0.025), mat=asphalt)

striped_slat("SlatUpper", 0.98, (orange, white))
striped_slat("SlatLower", 0.58, (white, orange))

for x in (-0.95, 0.95):
    a_frame(x, steel, rubber)

# amber warning beacon on the apex of the left frame
bpy.ops.mesh.primitive_cylinder_add(radius=0.055, depth=0.07, location=(-0.95, 0.0, 1.16))
base = bpy.context.active_object
base.name = "BeaconBase"
base.data.materials.append(steel)
bpy.ops.mesh.primitive_uv_sphere_add(radius=0.075, segments=20, ring_count=12,
                                     location=(-0.95, 0.0, 1.22))
lens = bpy.context.active_object
lens.name = "BeaconLens"
lens.scale = (1.0, 1.0, 0.8)
lens.data.materials.append(amber)
bpy.ops.object.shade_smooth()

light_data = bpy.data.lights.new("KeySun", type='SUN')
light_data.energy = 4.0
sun = bpy.data.objects.new("KeySun", light_data)
bpy.context.collection.objects.link(sun)
sun.location = (4.0, -5.0, 7.0)
aim(sun, (0.0, 0.0, 0.6))

cam_data = bpy.data.cameras.new("Camera")
cam_data.lens = 45.0
cam = bpy.data.objects.new("Camera", cam_data)
bpy.context.collection.objects.link(cam)
cam.location = (3.6, -3.4, 2.1)
aim(cam, (0.0, 0.0, 0.72))
bpy.context.scene.camera = cam
