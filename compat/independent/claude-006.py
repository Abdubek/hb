import bpy
import math
from mathutils import Vector

WALL_H = 2.6
T = 0.1              # wall thickness
IX, IY = 2.0, 2.5    # interior half extents -> 4 m x 5 m room


def reset_scene():
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete(use_global=False)
    for block in list(bpy.data.meshes):
        bpy.data.meshes.remove(block)
    for block in list(bpy.data.materials):
        bpy.data.materials.remove(block)


def mat(name, color, roughness=0.6, metallic=0.0, alpha=1.0):
    m = bpy.data.materials.new(name)
    m.use_nodes = True
    bsdf = m.node_tree.nodes['Principled BSDF']
    bsdf.inputs['Base Color'].default_value = (*color, 1.0)
    bsdf.inputs['Roughness'].default_value = roughness
    bsdf.inputs['Metallic'].default_value = metallic
    if alpha < 1.0:
        bsdf.inputs['Alpha'].default_value = alpha
        m.blend_method = 'BLEND'
    return m


def box(name, size, center, material, rot_z=0.0):
    bpy.ops.mesh.primitive_cube_add(size=2.0, location=center)
    ob = bpy.context.object
    ob.name = name
    ob.scale = (size[0] / 2.0, size[1] / 2.0, size[2] / 2.0)
    ob.rotation_euler.z = rot_z
    ob.data.materials.append(material)
    return ob


def cyl(name, radius, depth, center, material, verts=20):
    bpy.ops.mesh.primitive_cylinder_add(vertices=verts, radius=radius, depth=depth,
                                        location=center)
    ob = bpy.context.object
    ob.name = name
    ob.data.materials.append(material)
    return ob


def wall_panels(name, axis, plane, segments, material):
    """segments: (u0, u1, z0, z1) rectangles measured in the wall plane."""
    for i, (u0, u1, z0, z1) in enumerate(segments):
        du, dz = u1 - u0, z1 - z0
        uc, zc = (u0 + u1) / 2.0, (z0 + z1) / 2.0
        if axis == 'x':      # wall runs along X, faces +/-Y
            box('%s_%d' % (name, i), (du, T, dz), (uc, plane, zc), material)
        else:                # wall runs along Y, faces +/-X
            box('%s_%d' % (name, i), (T, du, dz), (plane, uc, zc), material)


def build_shell(wall_m, floor_m, ceil_m, glass_m, trim_m):
    box('Floor', (2 * IX, 2 * IY, 0.08), (0, 0, -0.04), floor_m)
    box('Ceiling', (2 * IX + T, 2 * IY + T, 0.08), (0, 0, WALL_H + 0.04), ceil_m)

    # South wall, pierced by a 0.9 x 2.05 doorway
    d0, d1, dh = -0.95, -0.05, 2.05
    wall_panels('Wall_South', 'x', -IY - T / 2, [
        (-IX - T, d0, 0, WALL_H),
        (d1, IX + T, 0, WALL_H),
        (d0, d1, dh, WALL_H)], wall_m)

    # North wall, pierced by a 1.6 x 1.2 window on a 0.9 m sill
    w0, w1, s0, s1 = -0.8, 0.8, 0.9, 2.1
    wall_panels('Wall_North', 'x', IY + T / 2, [
        (-IX - T, w0, 0, WALL_H),
        (w1, IX + T, 0, WALL_H),
        (w0, w1, 0, s0),
        (w0, w1, s1, WALL_H)], wall_m)

    wall_panels('Wall_West', 'y', -IX - T / 2, [(-IY, IY, 0, WALL_H)], wall_m)
    wall_panels('Wall_East', 'y', IX + T / 2, [(-IY, IY, 0, WALL_H)], wall_m)

    box('WindowGlass', (w1 - w0, 0.015, s1 - s0), (0, IY + T / 2, (s0 + s1) / 2), glass_m)
    box('WindowSill', (w1 - w0 + 0.2, 0.24, 0.04), (0, IY - 0.04, s0), trim_m)
    for i, x in enumerate((w0, 0.0, w1)):
        box('WindowMullion_%d' % i, (0.05, 0.1, s1 - s0), (x, IY + 0.02, (s0 + s1) / 2), trim_m)

    # Door leaf hinged at x = d0 and swung 65 degrees into the room
    a = math.radians(-65.0)
    box('DoorLeaf', (0.9, 0.045, dh),
        (d0 + 0.45 * math.cos(a), -IY + 0.45 * math.sin(a), dh / 2), trim_m, rot_z=a)
    box('DoorFrame_Head', (1.02, 0.14, 0.06), (-0.5, -IY, dh + 0.03), trim_m)
    for i, x in enumerate((d0 - 0.03, d1 + 0.03)):
        box('DoorFrame_Jamb_%d' % i, (0.06, 0.14, dh), (x, -IY, dh / 2), trim_m)


def build_sofa(fabric, wood):
    x = -IX + 0.55
    box('Sofa_Base', (0.95, 2.0, 0.32), (x, -0.3, 0.28), fabric)
    box('Sofa_Back', (0.2, 2.0, 0.55), (x - 0.38, -0.3, 0.7), fabric)
    for i, y in enumerate((-1.2, 0.6)):
        box('Sofa_Arm_%d' % i, (0.95, 0.2, 0.24), (x, y, 0.56), fabric)
    for i, y in enumerate((-0.75, -0.3, 0.15)):
        box('Sofa_Cushion_%d' % i, (0.8, 0.42, 0.12), (x + 0.04, y, 0.5), fabric)
    for i, (dx, dy) in enumerate(((-0.35, -0.85), (-0.35, 0.85), (0.35, -0.85), (0.35, 0.85))):
        cyl('Sofa_Foot_%d' % i, 0.035, 0.12, (x + dx, -0.3 + dy, 0.06), wood)


def build_table(wood, metal, book_m):
    cx, cy = -0.35, -0.3
    box('Table_Top', (0.62, 1.1, 0.05), (cx, cy, 0.42), wood)
    for i, (dx, dy) in enumerate(((-0.24, -0.46), (0.24, -0.46), (-0.24, 0.46), (0.24, 0.46))):
        cyl('Table_Leg_%d' % i, 0.025, 0.4, (cx + dx, cy + dy, 0.2), metal)
    box('Table_Book', (0.22, 0.3, 0.045), (cx + 0.03, cy - 0.15, 0.467), book_m)


def build_shelf(wood, book_m):
    x = IX - 0.18
    for i, dy in enumerate((-0.6, 0.6)):
        box('Shelf_Side_%d' % i, (0.32, 0.03, 1.8), (x, 1.0 + dy, 0.9), wood)
    for i in range(5):
        box('Shelf_Board_%d' % i, (0.32, 1.2, 0.03), (x, 1.0, 0.06 + i * 0.42), wood)
    for i in range(7):
        box('Shelf_Book_%d' % i, (0.2, 0.05, 0.26), (x, 0.52 + i * 0.07, 0.635), book_m)


def build_lamp(metal, shade):
    px, py = IX - 0.6, -1.85
    cyl('Lamp_Base', 0.16, 0.03, (px, py, 0.015), metal)
    cyl('Lamp_Pole', 0.02, 1.45, (px, py, 0.74), metal)
    bpy.ops.mesh.primitive_cone_add(vertices=24, radius1=0.2, radius2=0.13, depth=0.26,
                                    location=(px, py, 1.56))
    ob = bpy.context.object
    ob.name = 'Lamp_Shade'
    ob.data.materials.append(shade)


def build_plant(pot_m, leaf_m):
    px, py = -IX + 0.5, 1.95
    bpy.ops.mesh.primitive_cone_add(vertices=20, radius1=0.14, radius2=0.19, depth=0.34,
                                    location=(px, py, 0.17))
    bpy.context.object.name = 'Plant_Pot'
    bpy.context.object.data.materials.append(pot_m)
    for i, (dx, dy, z, r) in enumerate(((0.0, 0.0, 0.55, 0.22), (0.14, 0.07, 0.42, 0.15),
                                        (-0.11, -0.09, 0.46, 0.14))):
        bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=2, radius=r,
                                              location=(px + dx, py + dy, z))
        bpy.context.object.name = 'Plant_Foliage_%d' % i
        bpy.context.object.data.materials.append(leaf_m)


def add_camera_and_lights():
    cam_loc = Vector((1.6, -2.0, 2.1))
    target = Vector((-0.7, 0.9, 0.85))
    bpy.ops.object.camera_add(location=cam_loc)
    cam = bpy.context.object
    cam.name = 'RoomCamera'
    cam.data.lens = 20
    cam.rotation_euler = (target - cam_loc).to_track_quat('-Z', 'Y').to_euler()
    bpy.context.scene.camera = cam

    bpy.ops.object.light_add(type='AREA', location=(0, 0, WALL_H - 0.12))
    ceiling = bpy.context.object
    ceiling.name = 'CeilingLight'
    ceiling.data.energy = 240
    ceiling.data.size = 1.6

    bpy.ops.object.light_add(type='AREA', location=(0, IY - 0.25, 1.5),
                             rotation=(math.radians(90), 0, 0))
    daylight = bpy.context.object
    daylight.name = 'WindowLight'
    daylight.data.energy = 320
    daylight.data.size = 1.6


reset_scene()
wall_m = mat('Wall_Paint', (0.88, 0.87, 0.83), 0.85)
floor_m = mat('Floor_Oak', (0.45, 0.29, 0.16), 0.45)
ceil_m = mat('Ceiling_Paint', (0.95, 0.95, 0.95), 0.9)
trim_m = mat('Wood_Trim', (0.35, 0.22, 0.13), 0.5)
metal_m = mat('Steel', (0.65, 0.66, 0.68), 0.35, 0.9)
fabric_m = mat('Sofa_Fabric', (0.24, 0.33, 0.42), 0.8)
glass_m = mat('Glass', (0.75, 0.85, 0.92), 0.08, 0.0, 0.25)
shade_m = mat('Shade_Linen', (0.95, 0.9, 0.78), 0.7)
book_m = mat('Book_Cloth', (0.55, 0.13, 0.12), 0.5)
pot_m = mat('Terracotta', (0.6, 0.3, 0.2), 0.7)
leaf_m = mat('Foliage', (0.16, 0.36, 0.16), 0.65)
rug_m = mat('Rug_Wool', (0.7, 0.6, 0.48), 0.9)

build_shell(wall_m, floor_m, ceil_m, glass_m, trim_m)
box('Rug', (2.3, 1.9, 0.02), (-0.3, -0.35, 0.05), rug_m)
build_sofa(fabric_m, trim_m)
build_table(trim_m, metal_m, book_m)
build_shelf(trim_m, book_m)
build_lamp(metal_m, shade_m)
build_plant(pot_m, leaf_m)
add_camera_and_lights()
