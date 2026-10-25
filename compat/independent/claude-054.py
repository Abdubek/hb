import bpy
import bmesh
import math
from mathutils import Vector

# --------------------------------------------------------------- utilities


def clear_scene():
    for obj in list(bpy.data.objects):
        bpy.data.objects.remove(obj, do_unlink=True)
    for coll in (bpy.data.meshes, bpy.data.materials, bpy.data.cameras,
                 bpy.data.lights):
        for item in list(coll):
            coll.remove(item)


def material(name, color, metallic=0.0, roughness=0.5):
    mat = bpy.data.materials.new(name)
    mat.use_nodes = True
    bsdf = next(n for n in mat.node_tree.nodes if n.type == 'BSDF_PRINCIPLED')
    bsdf.inputs['Base Color'].default_value = (*color, 1.0)
    bsdf.inputs['Metallic'].default_value = metallic
    bsdf.inputs['Roughness'].default_value = roughness
    return mat


def register(obj, name, mat, parent):
    obj.name = name
    obj.data.name = name
    obj.data.materials.clear()
    obj.data.materials.append(mat)
    obj.parent = parent
    return obj


def box(name, size, loc, mat, parent, rot=(0, 0, 0)):
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=loc, rotation=rot)
    obj = bpy.context.object
    obj.scale = size
    return register(obj, name, mat, parent)


def tube(name, radius, depth, loc, mat, parent, rot=(0, 0, 0), verts=24):
    bpy.ops.mesh.primitive_cylinder_add(radius=radius, depth=depth,
                                        vertices=verts, location=loc,
                                        rotation=rot)
    return register(bpy.context.object, name, mat, parent)


def nozzle(name, r1, r2, depth, loc, mat, parent, rot=(0, 0, 0)):
    bpy.ops.mesh.primitive_cone_add(radius1=r1, radius2=r2, depth=depth,
                                    vertices=16, location=loc, rotation=rot)
    return register(bpy.context.object, name, mat, parent)


def parabolic_dish(name, radius, depth, mat, parent, loc, rings=6, segs=28):
    """Lathe a parabolic profile that opens towards local +Z."""
    verts = [Vector((0.0, 0.0, 0.0))]
    for i in range(1, rings + 1):
        r = radius * i / rings
        z = depth * (r / radius) ** 2
        for j in range(segs):
            a = 2.0 * math.pi * j / segs
            verts.append(Vector((r * math.cos(a), r * math.sin(a), z)))

    def idx(ring, seg):
        return 1 + (ring - 1) * segs + (seg % segs)

    faces = [(0, idx(1, j), idx(1, j + 1)) for j in range(segs)]
    for i in range(1, rings):
        for j in range(segs):
            faces.append((idx(i, j), idx(i, j + 1),
                          idx(i + 1, j + 1), idx(i + 1, j)))

    mesh = bpy.data.meshes.new(name)
    mesh.from_pydata([tuple(v) for v in verts], [], faces)
    mesh.validate()
    obj = bpy.data.objects.new(name, mesh)
    bpy.context.collection.objects.link(obj)
    obj.location = loc
    obj.rotation_euler = (0.0, math.radians(90.0), 0.0)  # face +X
    solid = obj.modifiers.new('Shell', 'SOLIDIFY')
    solid.thickness = 0.025
    solid.offset = 0.0
    return register(obj, name, mat, parent)


def aim_camera(cam, target):
    direction = Vector(target) - cam.location
    cam.rotation_euler = direction.to_track_quat('-Z', 'Y').to_euler()


# --------------------------------------------------------------- the build
clear_scene()

mli = material('MAT_GoldFoil', (0.72, 0.52, 0.12), metallic=1.0, roughness=0.35)
metal = material('MAT_Aluminium', (0.66, 0.68, 0.70), metallic=1.0, roughness=0.3)
cells = material('MAT_SolarCell', (0.05, 0.09, 0.30), metallic=0.6, roughness=0.2)
white = material('MAT_WhitePaint', (0.86, 0.87, 0.88), roughness=0.55)
dark = material('MAT_DarkComposite', (0.06, 0.06, 0.07), roughness=0.7)

bpy.ops.object.empty_add(type='PLAIN_AXES', location=(0, 0, 0))
root = bpy.context.object
root.name = 'Satellite'

# spacecraft bus
box('Bus_Body', (1.20, 1.00, 1.40), (0, 0, 0), mli, root)
box('Bus_TopDeck', (1.26, 1.06, 0.06), (0, 0, 0.72), white, root)
box('Bus_BottomDeck', (1.26, 1.06, 0.06), (0, 0, -0.72), white, root)
for sign in (1, -1):
    box('Bus_Rib_%s' % ('PY' if sign > 0 else 'NY'),
        (1.24, 0.05, 1.38), (0, sign * 0.51, 0), metal, root)

# solar wings: hinge, boom and panel with cell strips
for sign, tag in ((1, 'Port'), (-1, 'Starboard')):
    tube('Wing_%s_Hinge' % tag, 0.10, 0.24, (0, sign * 0.62, 0), metal, root,
         rot=(math.radians(90), 0, 0))
    tube('Wing_%s_Boom' % tag, 0.06, 0.90, (0, sign * 1.15, 0), metal, root,
         rot=(math.radians(90), 0, 0))
    box('Wing_%s_Panel' % tag, (1.20, 2.40, 0.05),
        (0, sign * 2.80, 0), dark, root)
    for k in range(3):
        y = sign * (1.70 + k * 0.80)
        box('Wing_%s_Cells_%d' % (tag, k + 1), (1.10, 0.72, 0.03),
            (0, y, 0.04), cells, root)
    for edge in (0.58, -0.58):
        box('Wing_%s_Rail_%s' % (tag, 'A' if edge > 0 else 'B'),
            (0.05, 2.42, 0.09), (edge, sign * 2.80, 0), metal, root)

# high gain dish antenna on a short mast
tube('Antenna_Mast', 0.07, 0.55, (0.85, 0, 0), metal, root,
     rot=(0, math.radians(90), 0))
parabolic_dish('Antenna_Dish', 0.78, 0.30, white, root, (1.20, 0, 0))
tube('Antenna_FeedBoom', 0.025, 0.55, (1.62, 0, 0), metal, root,
     rot=(0, math.radians(90), 0))
nozzle('Antenna_FeedHorn', 0.13, 0.05, 0.20, (1.98, 0, 0), metal, root,
       rot=(0, math.radians(-90), 0))

# omni whips, downlink horn and thrusters
for sign in (1, -1):
    tube('Whip_Antenna_%s' % ('A' if sign > 0 else 'B'), 0.018, 1.10,
         (sign * 0.35, 0.30, 1.30), metal, root)
    tube('Whip_Tip_%s' % ('A' if sign > 0 else 'B'), 0.05, 0.05,
         (sign * 0.35, 0.30, 1.87), white, root)
nozzle('Downlink_Horn', 0.22, 0.09, 0.30, (0, -0.25, -0.92), white, root,
       rot=(math.radians(180), 0, 0))
for dx in (0.38, -0.38):
    for dy in (0.30, -0.30):
        nozzle('Thruster_%s%s' % ('P' if dx > 0 else 'N',
                                  'P' if dy > 0 else 'N'),
               0.05, 0.11, 0.16, (dx, dy, -0.83), dark, root,
               rot=(math.radians(180), 0, 0))
box('StarTracker', (0.18, 0.18, 0.22), (0.40, -0.30, 0.84), dark, root)

# --------------------------------------------------------------- staging
bpy.ops.object.light_add(type='SUN', location=(6, -5, 8))
sun = bpy.context.object
sun.name = 'KeyLight_Sun'
sun.data.energy = 4.0
sun.rotation_euler = (math.radians(50), math.radians(15), math.radians(35))

bpy.ops.object.light_add(type='AREA', location=(-5, -4, 2))
fill = bpy.context.object
fill.name = 'FillLight'
fill.data.energy = 300.0
fill.data.size = 6.0
fill.rotation_euler = (math.radians(80), 0, math.radians(-60))

bpy.ops.object.camera_add(location=(5.4, -6.2, 3.0))
cam = bpy.context.object
cam.name = 'SceneCamera'
cam.data.lens = 50.0
aim_camera(cam, (0.2, 0.0, 0.1))
bpy.context.scene.camera = cam

for obj in bpy.data.objects:
    if obj.type == 'MESH':
        obj.data.polygons.foreach_set('use_smooth',
                                      [False] * len(obj.data.polygons))
        obj.data.update()
