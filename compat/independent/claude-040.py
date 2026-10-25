import bpy
import bmesh
from mathutils import Vector


def clear_scene():
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete(use_global=False)
    for block in (bpy.data.meshes, bpy.data.materials):
        for item in block:
            if item.users == 0:
                block.remove(item)


def make_material(name, color, rough=0.5, metal=0.0):
    mat = bpy.data.materials.new(name)
    mat.use_nodes = True
    bsdf = mat.node_tree.nodes['Principled BSDF']
    bsdf.inputs['Base Color'].default_value = (*color, 1.0)
    bsdf.inputs['Roughness'].default_value = rough
    bsdf.inputs['Metallic'].default_value = metal
    return mat


def add_box(name, center, size, mat, rot=(0.0, 0.0, 0.0)):
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=center, rotation=rot)
    obj = bpy.context.object
    obj.name = name
    obj.scale = Vector(size) * 0.5
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    obj.data.materials.append(mat)
    return obj


def add_cylinder(name, center, radius, depth, mat, rot=(0.0, 0.0, 0.0), verts=24):
    bpy.ops.mesh.primitive_cylinder_add(vertices=verts, radius=radius, depth=depth,
                                        location=center, rotation=rot)
    obj = bpy.context.object
    obj.name = name
    obj.data.materials.append(mat)
    return obj


def build_tray(mat):
    """Open, outward-flaring hopper made from an 8 vertex shell + solidify."""
    bot = [(-0.50, -0.22, 0.46), (0.52, -0.22, 0.46), (0.52, 0.22, 0.46), (-0.50, 0.22, 0.46)]
    top = [(-0.66, -0.40, 0.82), (0.62, -0.34, 0.86), (0.62, 0.34, 0.86), (-0.66, 0.40, 0.82)]
    bm = bmesh.new()
    bv = [bm.verts.new(p) for p in bot]
    tv = [bm.verts.new(p) for p in top]
    bm.faces.new(bv[::-1])
    for i in range(4):
        j = (i + 1) % 4
        bm.faces.new((bv[i], bv[j], tv[j], tv[i]))
    bm.normal_update()
    me = bpy.data.meshes.new('WheelbarrowTray')
    bm.to_mesh(me)
    bm.free()
    obj = bpy.data.objects.new('Tray', me)
    bpy.context.collection.objects.link(obj)
    obj.data.materials.append(mat)
    solid = obj.modifiers.new('Shell', 'SOLIDIFY')
    solid.thickness = 0.03
    solid.offset = -1.0
    bpy.context.view_layer.objects.active = obj
    bpy.ops.object.modifier_apply(modifier=solid.name)
    return obj


def build_wheel(mat_tyre, mat_hub):
    tyre = add_cylinder('WheelTyre', (0.92, 0.0, 0.20), 0.20, 0.09, mat_tyre,
                        rot=(1.5708, 0.0, 0.0), verts=32)
    bpy.ops.object.shade_smooth()
    hub = add_cylinder('WheelHub', (0.92, 0.0, 0.20), 0.07, 0.11, mat_hub,
                       rot=(1.5708, 0.0, 0.0), verts=16)
    axle = add_cylinder('Axle', (0.92, 0.0, 0.20), 0.018, 0.44, mat_hub,
                        rot=(1.5708, 0.0, 0.0), verts=12)
    return tyre, hub, axle


def setup_camera(target):
    bpy.ops.object.camera_add(location=(2.6, -2.6, 1.7))
    cam = bpy.context.object
    cam.name = 'SceneCamera'
    direction = Vector(target) - cam.location
    cam.rotation_euler = direction.to_track_quat('-Z', 'Y').to_euler()
    cam.data.lens = 50
    bpy.context.scene.camera = cam
    return cam


clear_scene()

steel = make_material('Steel', (0.62, 0.63, 0.66), rough=0.35, metal=1.0)
paint = make_material('TrayPaint', (0.10, 0.32, 0.58), rough=0.4, metal=0.6)
wood = make_material('HandleWood', (0.55, 0.36, 0.18), rough=0.7)
rubber = make_material('Rubber', (0.05, 0.05, 0.06), rough=0.9)
grass = make_material('Ground', (0.28, 0.34, 0.20), rough=1.0)

build_tray(paint)

# Two wooden handles/rails running the length of the barrow, tilted nose-down.
for side, y in (('L', -0.30), ('R', 0.30)):
    add_box('Handle_' + side, (-0.05, y, 0.415), (1.95, 0.055, 0.07), wood,
            rot=(0.0, 0.06, 0.0))

# Cross braces tying the rails together.
add_box('CrossBrace_Front', (0.66, 0.0, 0.40), (0.07, 0.62, 0.05), steel)
add_box('CrossBrace_Rear', (-0.62, 0.0, 0.45), (0.07, 0.62, 0.05), steel)

# Wheel fork legs reaching down to the axle.
for side, y in (('L', -0.20), ('R', 0.20)):
    add_box('Fork_' + side, (0.90, y, 0.31), (0.06, 0.05, 0.30), steel,
            rot=(0.0, -0.22, 0.0))

build_wheel(rubber, steel)

# Rear support legs plus feet.
for side, y in (('L', -0.30), ('R', 0.30)):
    add_box('Leg_' + side, (-0.50, y, 0.21), (0.05, 0.05, 0.42), steel)
    add_box('Foot_' + side, (-0.50, y, 0.02), (0.22, 0.09, 0.04), steel)

# Grips at the far end of the rails.
for side, y in (('L', -0.30), ('R', 0.30)):
    add_cylinder('Grip_' + side, (-0.93, y, 0.36), 0.045, 0.16, rubber,
                 rot=(0.0, 1.5708, 0.0), verts=16)

ground = add_box('Ground', (0.0, 0.0, -0.02), (8.0, 8.0, 0.04), grass)
ground.select_set(False)

bpy.ops.object.light_add(type='SUN', location=(3.0, -3.0, 5.0))
sun = bpy.context.object
sun.name = 'KeyLight'
sun.data.energy = 4.0
sun.rotation_euler = (0.7, 0.2, -0.9)

setup_camera((0.0, 0.0, 0.5))
bpy.context.scene.world = bpy.data.worlds.new('World')
bpy.context.scene.world.use_nodes = True
bpy.context.scene.world.node_tree.nodes['Background'].inputs[0].default_value = (0.55, 0.62, 0.72, 1.0)
