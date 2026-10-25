import bpy
import math
from mathutils import Vector

HOOPS = 5
SPACING = 0.75
HOOP_H = 0.90
HOOP_HALF_W = 0.40
CORNER_R = 0.22
TUBE_R = 0.028


def reset_scene():
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete(use_global=False)
    for m in list(bpy.data.meshes):
        bpy.data.meshes.remove(m)
    for c in list(bpy.data.curves):
        bpy.data.curves.remove(c)
    for m in list(bpy.data.materials):
        bpy.data.materials.remove(m)


def mat(name, color, roughness=0.4, metallic=0.0):
    m = bpy.data.materials.new(name)
    m.use_nodes = True
    bsdf = m.node_tree.nodes['Principled BSDF']
    bsdf.inputs['Base Color'].default_value = (*color, 1.0)
    bsdf.inputs['Roughness'].default_value = roughness
    bsdf.inputs['Metallic'].default_value = metallic
    return m


def box(name, size, center, material):
    bpy.ops.mesh.primitive_cube_add(size=2.0, location=center)
    ob = bpy.context.object
    ob.name = name
    ob.scale = (size[0] / 2.0, size[1] / 2.0, size[2] / 2.0)
    ob.data.materials.append(material)
    return ob


def tube_path(name, points, radius, material, res=5):
    """Round-profile tube swept along a polyline, then converted to mesh."""
    cu = bpy.data.curves.new(name + '_Curve', 'CURVE')
    cu.dimensions = '3D'
    cu.bevel_depth = radius
    cu.bevel_resolution = res
    cu.resolution_u = 2
    spline = cu.splines.new('POLY')
    spline.points.add(len(points) - 1)
    for pt, co in zip(spline.points, points):
        pt.co = (co[0], co[1], co[2], 1.0)
    ob = bpy.data.objects.new(name, cu)
    bpy.context.collection.objects.link(ob)
    ob.data.materials.append(material)
    bpy.ops.object.select_all(action='DESELECT')
    ob.select_set(True)
    bpy.context.view_layer.objects.active = ob
    bpy.ops.object.convert(target='MESH')
    return bpy.context.object


def cyl_between(name, p0, p1, radius, material, verts=16):
    p0, p1 = Vector(p0), Vector(p1)
    d = p1 - p0
    bpy.ops.mesh.primitive_cylinder_add(vertices=verts, radius=radius, depth=d.length,
                                        location=(p0 + p1) / 2.0)
    ob = bpy.context.object
    ob.name = name
    ob.rotation_euler = d.to_track_quat('Z', 'Y').to_euler()
    ob.data.materials.append(material)
    return ob


def hoop_points(x):
    """Inverted-U profile in the YZ plane at station x, with rounded top corners."""
    w, h, r = HOOP_HALF_W, HOOP_H, CORNER_R
    pts = [(x, -w, 0.0), (x, -w, h - r)]
    for i in range(1, 7):
        a = math.pi / 2 * i / 6
        pts.append((x, -w + r - r * math.cos(a), h - r + r * math.sin(a)))
    pts.append((x, w - r, h))
    for i in range(1, 7):
        a = math.pi / 2 * i / 6
        pts.append((x, w - r + r * math.sin(a), h - r + r * math.cos(a)))
    pts.append((x, w, 0.0))
    return pts


def build_rack(steel, concrete):
    xs = [(i - (HOOPS - 1) / 2.0) * SPACING for i in range(HOOPS)]
    box('Concrete_Pad', (HOOPS * SPACING + 1.0, 2.4, 0.08), (0, 0, -0.04), concrete)
    for i, x in enumerate(xs):
        tube_path('Hoop_%d' % (i + 1), hoop_points(x), TUBE_R, steel)
        for j, y in enumerate((-HOOP_HALF_W, HOOP_HALF_W)):
            box('Base_Plate_%d_%d' % (i + 1, j), (0.13, 0.13, 0.02), (x, y, 0.01), steel)
    for j, y in enumerate((-HOOP_HALF_W, HOOP_HALF_W)):
        cyl_between('Base_Rail_%d' % j, (xs[0], y, 0.09), (xs[-1], y, 0.09), 0.022, steel)
    return xs


def build_sign(x, steel, sign_m):
    top = 1.85
    cyl_between('Sign_Post', (x, 1.0, 0.0), (x, 1.0, top), 0.032, steel)
    box('Sign_Plate', (0.34, 0.02, 0.34), (x, 1.0, top - 0.2), sign_m)


def build_bicycle(prefix, x, frame_m, rubber, steel, saddle_m):
    """Simplified diamond-frame bicycle standing in the YZ plane at station x."""
    r_wheel = 0.34
    rear = Vector((x, -0.53, r_wheel))
    front = Vector((x, 0.53, r_wheel))
    bb = Vector((x, 0.0, 0.28))
    seat = Vector((x, -0.18, 0.86))
    head = Vector((x, 0.36, 0.94))

    for name, c in (('Wheel_R', rear), ('Wheel_F', front)):
        bpy.ops.mesh.primitive_torus_add(major_radius=r_wheel, minor_radius=0.028,
                                         major_segments=28, minor_segments=8,
                                         location=c, rotation=(0, math.pi / 2, 0))
        ob = bpy.context.object
        ob.name = '%s_%s' % (prefix, name)
        ob.data.materials.append(rubber)
        cyl_between('%s_%s_Hub' % (prefix, name), c - Vector((0.04, 0, 0)),
                    c + Vector((0.04, 0, 0)), 0.03, steel, verts=12)

    for name, a, b in (('Chainstay', rear, bb), ('Seattube', bb, seat), ('Seatstay', seat, rear),
                       ('Toptube', seat, head), ('Downtube', bb, head), ('Fork', head, front)):
        cyl_between('%s_%s' % (prefix, name), a, b, 0.018, frame_m)

    cyl_between('%s_Handlebar' % prefix, head + Vector((-0.2, 0.02, 0.06)),
                head + Vector((0.2, 0.02, 0.06)), 0.014, steel, verts=12)
    cyl_between('%s_Crank' % prefix, bb - Vector((0.07, 0, 0)), bb + Vector((0.07, 0, 0)),
                0.012, steel, verts=12)
    box('%s_Saddle' % prefix, (0.09, 0.26, 0.045), seat + Vector((0, 0, 0.035)), saddle_m)


def add_camera_and_lights():
    cam_loc = Vector((3.4, -3.6, 2.1))
    target = Vector((0.0, 0.0, 0.55))
    bpy.ops.object.camera_add(location=cam_loc)
    cam = bpy.context.object
    cam.name = 'RackCamera'
    cam.data.lens = 45
    cam.rotation_euler = (target - cam_loc).to_track_quat('-Z', 'Y').to_euler()
    bpy.context.scene.camera = cam

    bpy.ops.object.light_add(type='SUN', location=(3, -3, 6),
                             rotation=(math.radians(52), 0, math.radians(35)))
    sun = bpy.context.object
    sun.name = 'Sun'
    sun.data.energy = 4.0

    bpy.ops.object.light_add(type='AREA', location=(-2.5, -3.0, 2.5),
                             rotation=(math.radians(70), 0, math.radians(-40)))
    fill = bpy.context.object
    fill.name = 'FillLight'
    fill.data.energy = 200
    fill.data.size = 3.0


reset_scene()
steel = mat('Galvanized_Steel', (0.70, 0.71, 0.73), 0.32, 0.9)
concrete = mat('Concrete_Pad_Mat', (0.62, 0.61, 0.58), 0.85)
asphalt = mat('Asphalt', (0.22, 0.22, 0.23), 0.9)
sign_m = mat('Sign_Blue', (0.10, 0.28, 0.62), 0.35)
frame_red = mat('Bike_Frame_Red', (0.62, 0.10, 0.10), 0.28)
frame_teal = mat('Bike_Frame_Teal', (0.08, 0.42, 0.42), 0.28)
rubber = mat('Tire_Rubber', (0.05, 0.05, 0.05), 0.75)
saddle_m = mat('Saddle_Leather', (0.12, 0.09, 0.07), 0.55)

box('Ground', (14.0, 14.0, 0.06), (0, 0, -0.11), asphalt)
stations = build_rack(steel, concrete)
build_sign(stations[0] - 0.7, steel, sign_m)
build_bicycle('Bike_A', stations[1] + 0.07, frame_red, rubber, steel, saddle_m)
build_bicycle('Bike_B', stations[3] - 0.07, frame_teal, rubber, steel, saddle_m)
add_camera_and_lights()
