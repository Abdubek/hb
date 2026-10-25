import bpy
import bmesh
import math
from mathutils import Vector, Matrix


def reset_scene():
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete(use_global=False)
    for mesh in list(bpy.data.meshes):
        if mesh.users == 0:
            bpy.data.meshes.remove(mesh)


def material(name, color, roughness=0.5, metallic=0.0):
    mat = bpy.data.materials.new(name)
    mat.use_nodes = True
    bsdf = mat.node_tree.nodes["Principled BSDF"]
    bsdf.inputs["Base Color"].default_value = (*color, 1.0)
    bsdf.inputs["Roughness"].default_value = roughness
    bsdf.inputs["Metallic"].default_value = metallic
    return mat


def cylinder(name, radius, depth, location, mat, rotation=(0, 0, 0), verts=20):
    bpy.ops.mesh.primitive_cylinder_add(vertices=verts, radius=radius, depth=depth,
                                        location=location, rotation=rotation)
    obj = bpy.context.active_object
    obj.name = name
    obj.data.materials.append(mat)
    return obj


def cone(name, r1, r2, depth, location, mat, verts=20):
    bpy.ops.mesh.primitive_cone_add(vertices=verts, radius1=r1, radius2=r2,
                                    depth=depth, location=location)
    obj = bpy.context.active_object
    obj.name = name
    obj.data.materials.append(mat)
    return obj


def sphere(name, radius, location, mat, segments=16):
    bpy.ops.mesh.primitive_uv_sphere_add(radius=radius, segments=segments,
                                         ring_count=max(4, segments // 2), location=location)
    obj = bpy.context.active_object
    obj.name = name
    obj.data.materials.append(mat)
    return obj


def build_hook_arm(name, angle, height, length, mat):
    """Tapered arm swept outward from the post, curling up and tipped with a ball."""
    direction = Vector((math.cos(angle), math.sin(angle), 0.0))
    base = direction * 0.050 + Vector((0, 0, height))
    rot = Matrix.Rotation(angle, 3, 'Z')

    mesh = bpy.data.meshes.new(name)
    bm = bmesh.new()
    segments = 8
    sides = 10
    rings = []
    for i in range(segments + 1):
        t = i / segments
        pos = base + direction * (length * t) + Vector((0, 0, 0.045 * t * t))
        radius = 0.020 * (1.0 - 0.45 * t)
        ring = []
        for k in range(sides):
            a = 2 * math.pi * k / sides
            offset = rot @ (Vector((0.0, math.cos(a), math.sin(a))) * radius)
            ring.append(bm.verts.new(pos + offset))
        rings.append(ring)

    for i in range(segments):
        for k in range(sides):
            bm.faces.new((rings[i][k], rings[i][(k + 1) % sides],
                          rings[i + 1][(k + 1) % sides], rings[i + 1][k]))
    bm.faces.new(list(reversed(rings[0])))
    bm.faces.new(rings[-1])
    bm.normal_update()
    bm.to_mesh(mesh)
    bm.free()

    obj = bpy.data.objects.new(name, mesh)
    bpy.context.collection.objects.link(obj)
    obj.data.materials.append(mat)

    tip = base + direction * length + Vector((0, 0, 0.045))
    sphere(name + "_Ball", 0.022, tip, mat, segments=14)
    return obj


reset_scene()

wood = material("WalnutWood", (0.29, 0.16, 0.09), roughness=0.45)
wood_dark = material("WalnutDark", (0.19, 0.10, 0.05), roughness=0.5)
brass = material("Brass", (0.72, 0.55, 0.20), roughness=0.28, metallic=1.0)
floor_mat = material("FloorConcrete", (0.52, 0.51, 0.49), roughness=0.85)

bpy.ops.mesh.primitive_plane_add(size=6.0, location=(0, 0, 0))
floor_obj = bpy.context.active_object
floor_obj.name = "Floor"
floor_obj.data.materials.append(floor_mat)

# Central post, slightly tapered, on a turned foot.
cone("CenterPost", 0.055, 0.042, 1.72, (0, 0, 0.90), wood, verts=24)
cylinder("PostCollarLower", 0.070, 0.05, (0, 0, 0.12), wood_dark, verts=24)
cylinder("PostCollarUpper", 0.062, 0.04, (0, 0, 1.55), wood_dark, verts=24)
cylinder("BaseHub", 0.13, 0.09, (0, 0, 0.055), wood_dark, verts=24)
cylinder("FinialNeck", 0.030, 0.09, (0, 0, 1.74), brass, verts=16)
sphere("FinialBall", 0.070, (0, 0, 1.82), brass, segments=20)

# Three splayed feet with contact pads.
for i in range(3):
    a = 2 * math.pi * i / 3 + math.radians(20)
    leg = cylinder("Leg_%d" % i, 0.030, 0.58, (0, 0, 0), wood, verts=14)
    leg.rotation_euler = (0, math.radians(58), a)
    leg.location = Vector((math.cos(a), math.sin(a), 0)) * 0.24 + Vector((0, 0, 0.10))
    cylinder("FootPad_%d" % i, 0.038, 0.022,
             (math.cos(a) * 0.47, math.sin(a) * 0.47, 0.011), wood_dark, verts=14)

# Two tiers of hooks, offset so they interleave when seen from above.
upper_count = 4
for i in range(upper_count):
    a = 2 * math.pi * i / upper_count
    build_hook_arm("HookUpper_%d" % i, a, 1.44, 0.20, brass)
    cylinder("HookUpperMount_%d" % i, 0.028, 0.03,
             (math.cos(a) * 0.050, math.sin(a) * 0.050, 1.44), brass,
             rotation=(0, math.pi / 2, a), verts=14)

lower_count = 4
for i in range(lower_count):
    a = 2 * math.pi * i / lower_count + math.pi / lower_count
    build_hook_arm("HookLower_%d" % i, a, 1.18, 0.23, brass)
    cylinder("HookLowerMount_%d" % i, 0.028, 0.03,
             (math.cos(a) * 0.050, math.sin(a) * 0.050, 1.18), brass,
             rotation=(0, math.pi / 2, a), verts=14)

# Umbrella ring near the base, braced back to the post.
bpy.ops.mesh.primitive_torus_add(major_radius=0.16, minor_radius=0.014,
                                 major_segments=28, minor_segments=8,
                                 location=(0, 0, 0.36))
ring = bpy.context.active_object
ring.name = "UmbrellaRing"
ring.data.materials.append(brass)
for i in range(3):
    a = 2 * math.pi * i / 3
    cylinder("RingStay_%d" % i, 0.012, 0.115,
             (math.cos(a) * 0.105, math.sin(a) * 0.105, 0.36), brass,
             rotation=(0, math.pi / 2, a), verts=10)

bpy.ops.object.light_add(type='AREA', location=(2.0, -2.4, 3.4))
key = bpy.context.active_object
key.name = "KeyLight"
key.data.energy = 600
key.data.size = 3.5
key.rotation_euler = (math.radians(42), 0, math.radians(40))

bpy.ops.object.light_add(type='AREA', location=(-2.6, -1.4, 1.8))
fill = bpy.context.active_object
fill.name = "FillLight"
fill.data.energy = 160
fill.data.size = 3.0
fill.rotation_euler = (math.radians(70), 0, math.radians(-60))

bpy.ops.object.camera_add(location=(2.5, -3.0, 1.95))
cam = bpy.context.active_object
cam.name = "Camera"
cam.data.lens = 50
direction = Vector((0.0, 0.0, 1.05)) - cam.location
cam.rotation_euler = direction.to_track_quat('-Z', 'Y').to_euler()
bpy.context.scene.camera = cam
