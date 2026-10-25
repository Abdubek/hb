import bpy
import math


def reset_scene():
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete(use_global=False)
    for coll in (bpy.data.meshes, bpy.data.materials, bpy.data.lights, bpy.data.cameras):
        for item in list(coll):
            if item.users == 0:
                coll.remove(item)


MATS = {}


def mat(name, color, rough=0.5, metal=0.0, emit=0.0):
    if name in MATS:
        return MATS[name]
    m = bpy.data.materials.new(name)
    m.use_nodes = True
    bsdf = m.node_tree.nodes["Principled BSDF"]
    bsdf.inputs["Base Color"].default_value = (*color, 1.0)
    bsdf.inputs["Roughness"].default_value = rough
    bsdf.inputs["Metallic"].default_value = metal
    if emit > 0.0:
        bsdf.inputs["Emission Color"].default_value = (*color, 1.0)
        bsdf.inputs["Emission Strength"].default_value = emit
    MATS[name] = m
    return m


def _finish(obj, name, material):
    obj.name = name
    obj.data.name = name + "_mesh"
    obj.data.materials.append(material)
    return obj


def box(name, dims, loc, material):
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=loc)
    obj = bpy.context.active_object
    obj.scale = dims
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    return _finish(obj, name, material)


def cyl(name, radius, depth, loc, material, verts=24, rot=(0.0, 0.0, 0.0)):
    bpy.ops.mesh.primitive_cylinder_add(radius=radius, depth=depth, vertices=verts,
                                        location=loc, rotation=rot)
    return _finish(bpy.context.active_object, name, material)


def build_island():
    wood = mat("IslandWood", (0.22, 0.13, 0.08), rough=0.55)
    stone = mat("CounterStone", (0.86, 0.85, 0.82), rough=0.25)
    steel = mat("BrushedSteel", (0.72, 0.73, 0.75), rough=0.35, metal=1.0)

    box("Island_Cabinet", (2.10, 0.86, 0.84), (0.0, 0.06, 0.52), wood)
    box("Island_ToeKick", (2.00, 0.76, 0.10), (0.0, 0.06, 0.05),
        mat("ToeKick", (0.05, 0.05, 0.06), 0.8))
    box("Island_Countertop", (2.45, 1.15, 0.06), (0.0, 0.0, 0.97), stone)

    for i, x in enumerate((-0.65, 0.0, 0.65)):
        box("Island_DrawerFront_%d" % i, (0.60, 0.03, 0.24), (x, 0.50, 0.76), wood)
        cyl("Island_DrawerHandle_%d" % i, 0.012, 0.30, (x, 0.525, 0.76), steel,
            verts=12, rot=(0.0, math.pi / 2.0, 0.0))
        box("Island_DoorFront_%d" % i, (0.60, 0.03, 0.42), (x, 0.50, 0.40), wood)


def build_stool(index, x):
    seat_mat = mat("StoolSeat", (0.12, 0.30, 0.34), rough=0.6)
    frame = mat("StoolFrame", (0.55, 0.56, 0.58), rough=0.3, metal=1.0)
    y = -0.95

    cyl("Stool%d_Seat" % index, 0.18, 0.06, (x, y, 0.66), seat_mat, verts=20)
    cyl("Stool%d_Cushion" % index, 0.165, 0.04, (x, y, 0.70), seat_mat, verts=20)

    for leg, (sx, sy) in enumerate(((1, 1), (1, -1), (-1, 1), (-1, -1))):
        splay = 0.10
        cyl("Stool%d_Leg%d" % (index, leg), 0.018, 0.66,
            (x + sx * 0.13, y + sy * 0.13, 0.33), frame, verts=10,
            rot=(-sy * splay, sx * splay, 0.0))

    bpy.ops.mesh.primitive_torus_add(location=(x, y, 0.24), major_radius=0.16,
                                     minor_radius=0.012, major_segments=20,
                                     minor_segments=8)
    _finish(bpy.context.active_object, "Stool%d_Footrest" % index, frame)


def build_pendant(index, x):
    shade = mat("PendantShade", (0.08, 0.09, 0.10), rough=0.4)
    brass = mat("PendantBrass", (0.72, 0.55, 0.24), rough=0.3, metal=1.0)
    glow = mat("PendantBulb", (1.0, 0.92, 0.72), rough=0.4, emit=6.0)

    cyl("Pendant%d_Cord" % index, 0.008, 0.72, (x, 0.0, 2.24), brass, verts=8)
    cyl("Pendant%d_Canopy" % index, 0.05, 0.03, (x, 0.0, 2.58), brass, verts=16)
    bpy.ops.mesh.primitive_cone_add(radius1=0.17, radius2=0.055, depth=0.22,
                                    vertices=24, location=(x, 0.0, 1.79))
    _finish(bpy.context.active_object, "Pendant%d_Shade" % index, shade)
    bpy.ops.mesh.primitive_uv_sphere_add(radius=0.055, segments=16, ring_count=8,
                                         location=(x, 0.0, 1.70))
    _finish(bpy.context.active_object, "Pendant%d_Bulb" % index, glow)


def build_environment():
    box("Floor", (9.0, 9.0, 0.05), (0.0, 0.0, -0.025),
        mat("FloorOak", (0.42, 0.31, 0.20), rough=0.6))
    box("BackWall", (9.0, 0.1, 3.0), (0.0, 2.6, 1.5),
        mat("Wall", (0.88, 0.87, 0.84), rough=0.9))

    bpy.ops.object.light_add(type='AREA', location=(2.0, -3.0, 3.2))
    key = bpy.context.active_object
    key.name = "KeyLight"
    key.data.energy = 400.0
    key.data.size = 3.0
    key.rotation_euler = (math.radians(45.0), 0.0, math.radians(30.0))

    bpy.ops.object.light_add(type='POINT', location=(-2.5, -1.5, 2.2))
    fill = bpy.context.active_object
    fill.name = "FillLight"
    fill.data.energy = 120.0


def add_camera():
    from mathutils import Vector
    loc = Vector((3.6, -4.3, 2.5))
    target = Vector((0.0, -0.1, 1.05))
    bpy.ops.object.camera_add(location=loc)
    cam = bpy.context.active_object
    cam.name = "SceneCamera"
    cam.data.lens = 40.0
    cam.rotation_euler = (target - loc).to_track_quat('-Z', 'Y').to_euler()
    bpy.context.scene.camera = cam


reset_scene()
build_environment()
build_island()
for i, x in enumerate((-0.7, 0.0, 0.7)):
    build_stool(i, x)
for i, x in enumerate((-0.75, 0.0, 0.75)):
    build_pendant(i, x)
add_camera()
