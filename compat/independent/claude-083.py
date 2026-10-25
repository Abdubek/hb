import bpy
import math
from mathutils import Vector

SHELVES = 7
MAST_R, MAST_H = 0.085, 2.25
STEP_Z = 0.27
STEP_ANGLE = math.radians(52.0)


def reset_scene():
    if bpy.context.scene.objects:
        bpy.ops.object.select_all(action='SELECT')
        bpy.ops.object.delete(use_global=False)
    for coll in (bpy.data.meshes, bpy.data.materials, bpy.data.cameras, bpy.data.lights):
        for block in list(coll):
            coll.remove(block)


def make_material(name, color, roughness=0.5, metallic=0.0):
    mat = bpy.data.materials.new(name)
    mat.use_nodes = True
    bsdf = mat.node_tree.nodes["Principled BSDF"]
    bsdf.inputs["Base Color"].default_value = (color[0], color[1], color[2], 1.0)
    bsdf.inputs["Roughness"].default_value = roughness
    bsdf.inputs["Metallic"].default_value = metallic
    return mat


def finish(ob, name, material):
    ob.name = name
    ob.data.materials.append(material)
    return ob


def add_disc(name, radius, thickness, location, material, verts=48):
    bpy.ops.mesh.primitive_cylinder_add(vertices=verts, radius=radius,
                                        depth=thickness, location=location)
    return finish(bpy.context.active_object, name, material)


def add_rim(name, radius, location, material):
    bpy.ops.mesh.primitive_torus_add(major_radius=radius, minor_radius=0.014,
                                     major_segments=40, minor_segments=8,
                                     location=location)
    return finish(bpy.context.active_object, name, material)


def add_arm(name, from_xy, to_xy, z, material):
    start, end = Vector(from_xy), Vector(to_xy)
    span = (end - start).length
    mid = (start + end) / 2.0
    angle = math.atan2(end.y - start.y, end.x - start.x)
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(mid.x, mid.y, z),
                                    rotation=(0.0, 0.0, angle))
    ob = bpy.context.active_object
    ob.scale = (span + 0.1, 0.09, 0.05)
    return finish(ob, name, material)


def add_item(name, kind, location, material):
    if kind == 0:
        bpy.ops.mesh.primitive_cylinder_add(vertices=24, radius=0.075, depth=0.22,
                                            location=(location[0], location[1],
                                                      location[2] + 0.11))
    elif kind == 1:
        bpy.ops.mesh.primitive_cube_add(size=0.17,
                                        location=(location[0], location[1],
                                                  location[2] + 0.085),
                                        rotation=(0.0, 0.0, math.radians(22)))
    else:
        bpy.ops.mesh.primitive_uv_sphere_add(segments=20, ring_count=12, radius=0.09,
                                             location=(location[0], location[1],
                                                       location[2] + 0.09))
        bpy.ops.object.shade_smooth()
    return finish(bpy.context.active_object, name, material)


def add_camera(location, target, lens=50.0):
    cam_data = bpy.data.cameras.new("Camera")
    cam_data.lens = lens
    cam = bpy.data.objects.new("Camera", cam_data)
    bpy.context.collection.objects.link(cam)
    cam.location = location
    cam.rotation_euler = (Vector(target) - Vector(location)).to_track_quat('-Z', 'Y').to_euler()
    bpy.context.scene.camera = cam
    return cam


reset_scene()

m_base = make_material("BaseGraphite", (0.13, 0.13, 0.15), roughness=0.45)
m_mast = make_material("MastChrome", (0.82, 0.83, 0.85), roughness=0.18, metallic=1.0)
m_shelf = make_material("ShelfWhite", (0.90, 0.89, 0.86), roughness=0.35)
m_rim = make_material("RimBrass", (0.72, 0.55, 0.24), roughness=0.3, metallic=1.0)
m_floor = make_material("Floor", (0.42, 0.43, 0.46), roughness=0.8)
item_mats = [make_material("ItemRed", (0.62, 0.14, 0.14), roughness=0.4),
             make_material("ItemTeal", (0.11, 0.45, 0.46), roughness=0.4),
             make_material("ItemSand", (0.78, 0.68, 0.45), roughness=0.5)]

bpy.ops.mesh.primitive_plane_add(size=14.0, location=(0, 0, 0))
finish(bpy.context.active_object, "Floor", m_floor)

add_disc("BasePlate", 0.62, 0.09, (0, 0, 0.045), m_base)
add_disc("BaseCollar", 0.22, 0.10, (0, 0, 0.14), m_base, verts=32)
mast = add_disc("CentralMast", MAST_R, MAST_H, (0, 0, 0.14 + MAST_H / 2.0), m_mast, verts=24)
add_disc("MastCap", 0.11, 0.05, (0, 0, 0.14 + MAST_H + 0.02), m_rim, verts=24)

for i in range(SHELVES):
    angle = i * STEP_ANGLE
    z = 0.34 + i * STEP_Z
    shelf_r = 0.42 - 0.022 * i
    reach = 0.30 + 0.012 * i
    cx, cy = reach * math.cos(angle), reach * math.sin(angle)

    add_arm("ShelfArm_%d" % i, (0.0, 0.0), (cx, cy), z, m_mast)
    add_disc("Shelf_%d" % i, shelf_r, 0.035, (cx, cy, z + 0.045), m_shelf)
    add_rim("ShelfRim_%d" % i, shelf_r, (cx, cy, z + 0.062), m_rim)

    item_dir = angle + math.radians(18)
    ix = cx + 0.13 * math.cos(item_dir)
    iy = cy + 0.13 * math.sin(item_dir)
    add_item("Product_%d" % i, i % 3, (ix, iy, z + 0.062), item_mats[i % 3])

key_data = bpy.data.lights.new("KeyLight", type='AREA')
key_data.energy = 320.0
key_data.size = 2.5
key = bpy.data.objects.new("KeyLight", key_data)
bpy.context.collection.objects.link(key)
key.location = (2.4, -2.6, 3.6)
key.rotation_euler = (math.radians(42), 0.0, math.radians(42))

fill_data = bpy.data.lights.new("FillLight", type='POINT')
fill_data.energy = 90.0
fill = bpy.data.objects.new("FillLight", fill_data)
bpy.context.collection.objects.link(fill)
fill.location = (-2.2, 1.8, 1.8)

add_camera((3.1, -3.4, 2.5), (0.0, 0.0, 1.25))
