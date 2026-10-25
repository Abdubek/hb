import bpy
import bmesh
import math
from mathutils import Vector


def clear_scene():
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete(use_global=False)
    for block in (bpy.data.meshes, bpy.data.materials, bpy.data.cameras, bpy.data.lights):
        for item in list(block):
            if item.users == 0:
                block.remove(item)


def make_material(name, color, roughness=0.4, metallic=0.0, alpha=1.0, ior=1.45):
    mat = bpy.data.materials.new(name)
    mat.use_nodes = True
    bsdf = mat.node_tree.nodes["Principled BSDF"]
    bsdf.inputs["Base Color"].default_value = (*color, 1.0)
    bsdf.inputs["Roughness"].default_value = roughness
    bsdf.inputs["Metallic"].default_value = metallic
    bsdf.inputs["IOR"].default_value = ior
    if alpha < 1.0:
        bsdf.inputs["Alpha"].default_value = alpha
        mat.blend_method = 'BLEND'
    return mat


def add_object(name, material):
    mesh = bpy.data.meshes.new(name + "Mesh")
    obj = bpy.data.objects.new(name, mesh)
    obj.data.materials.append(material)
    bpy.context.scene.collection.objects.link(obj)
    return obj


def lathe(name, material, profile, segments=48):
    """Solid of revolution around Z from a list of (radius, z) pairs."""
    obj = add_object(name, material)
    bm = bmesh.new()
    verts = [bm.verts.new((r, 0.0, z)) for r, z in profile]
    for a, b in zip(verts, verts[1:]):
        bm.edges.new((a, b))
    bmesh.ops.spin(bm, geom=bm.verts[:] + bm.edges[:], axis=(0, 0, 1), cent=(0, 0, 0),
                   dupli=False, angle=2.0 * math.pi, steps=segments, use_merge=True)
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    for f in bm.faces:
        f.smooth = True
    bm.to_mesh(obj.data)
    bm.free()
    return obj


def add_cylinder(name, material, radius, height, z, segments=48):
    obj = add_object(name, material)
    bm = bmesh.new()
    bmesh.ops.create_cone(bm, cap_ends=True, cap_tris=False, segments=segments,
                          radius1=radius, radius2=radius, depth=height)
    for f in bm.faces:
        if len(f.verts) == 4:
            f.smooth = True
    bm.to_mesh(obj.data)
    bm.free()
    obj.location.z = z
    return obj


def curved_panel(name, material, radius, z0, z1, half_angle, steps=12):
    """Thin shell panel wrapped on a cylinder of given radius, facing -Y."""
    obj = add_object(name, material)
    bm = bmesh.new()
    rows = []
    for z in (z0, z1):
        row = []
        for i in range(steps + 1):
            a = -half_angle + 2.0 * half_angle * i / steps
            row.append(bm.verts.new((radius * math.cos(a), radius * math.sin(a), z)))
        rows.append(row)
    for i in range(steps):
        bm.faces.new((rows[0][i], rows[0][i + 1], rows[1][i + 1], rows[1][i]))
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    bm.to_mesh(obj.data)
    bm.free()
    obj.rotation_euler.z = math.radians(-90.0)
    return obj


def add_light(name, energy, size, location, rotation):
    light = bpy.data.lights.new(name + "Data", 'AREA')
    light.energy = energy
    light.size = size
    obj = bpy.data.objects.new(name, light)
    obj.location = location
    obj.rotation_euler = rotation
    bpy.context.scene.collection.objects.link(obj)
    return obj


clear_scene()
scene = bpy.context.scene
scene.world = bpy.data.worlds.new("PerfumeWorld")
scene.world.use_nodes = True
scene.world.node_tree.nodes["Background"].inputs["Color"].default_value = (0.05, 0.05, 0.06, 1.0)

glass = make_material("GlassBody", (0.82, 0.86, 0.90), roughness=0.05, alpha=0.35, ior=1.5)
juice = make_material("Fragrance", (0.86, 0.62, 0.24), roughness=0.10, alpha=0.75, ior=1.36)
gold = make_material("PolishedGold", (0.86, 0.68, 0.29), roughness=0.18, metallic=1.0)
lacquer = make_material("CapLacquer", (0.09, 0.09, 0.11), roughness=0.25)
paper = make_material("LabelPaper", (0.93, 0.91, 0.85), roughness=0.65)
ink = make_material("LabelInk", (0.15, 0.13, 0.12), roughness=0.50)
stone = make_material("DisplaySurface", (0.20, 0.20, 0.22), roughness=0.55)

R = 0.42
# Bottle: seated base, straight wall, soft shoulder, narrow neck.
lathe("BottleBody", glass, [
    (0.0, 0.0), (R * 0.98, 0.0), (R, 0.03), (R, 1.05),
    (R * 0.92, 1.14), (0.16, 1.22), (0.15, 1.40), (0.0, 1.40),
])
lathe("FragranceVolume", juice, [
    (0.0, 0.02), (R * 0.94, 0.02), (R * 0.94, 0.78), (0.0, 0.78),
])
lathe("CapTopInlay", gold, [
    (0.0, 1.826), (0.190, 1.826), (0.205, 1.848), (0.0, 1.848),
])

add_cylinder("NeckCollar", gold, 0.175, 0.12, 1.36)
add_cylinder("Cap", lacquer, 0.21, 0.46, 1.60)
add_cylinder("CapBand", gold, 0.216, 0.05, 1.40)
add_cylinder("DisplayPlinth", stone, 1.5, 0.06, -0.031, segments=64)

# Front label panel plus two printed bars standing in for type.
curved_panel("LabelPanel", paper, R + 0.006, 0.30, 0.78, math.radians(52.0))
curved_panel("LabelTitleBar", ink, R + 0.011, 0.500, 0.545, math.radians(34.0))
curved_panel("LabelRule", ink, R + 0.011, 0.392, 0.404, math.radians(40.0))

add_light("KeyLight", 320.0, 2.2, (2.0, -2.4, 3.0), (math.radians(48.0), 0.0, math.radians(40.0)))
add_light("RimLight", 140.0, 1.6, (-2.2, 1.8, 1.6), (math.radians(72.0), 0.0, math.radians(-135.0)))

cam = bpy.data.objects.new("Camera", bpy.data.cameras.new("CameraData"))
cam.data.lens = 70.0
cam.location = (2.6, -3.4, 2.0)
scene.collection.objects.link(cam)
scene.camera = cam
cam.rotation_euler = (Vector((0.0, 0.0, 0.95)) - cam.location).to_track_quat('-Z', 'Y').to_euler()

print("Perfume bottle scene built: %d objects" % len(scene.collection.objects))
