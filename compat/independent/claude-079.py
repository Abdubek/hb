import bpy
import bmesh
import math
from mathutils import Vector, Matrix

L = 6.06   # 20 ft container length
W = 2.44   # width
H = 2.59   # height
PITCH = 0.22
DEPTH = 0.025


def clear_scene():
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete(use_global=False)
    for coll in (bpy.data.meshes, bpy.data.materials, bpy.data.cameras, bpy.data.lights):
        for item in list(coll):
            if item.users == 0:
                coll.remove(item)


def make_material(name, color, roughness=0.6, metallic=0.0):
    mat = bpy.data.materials.new(name)
    mat.use_nodes = True
    bsdf = mat.node_tree.nodes["Principled BSDF"]
    bsdf.inputs["Base Color"].default_value = (*color, 1.0)
    bsdf.inputs["Roughness"].default_value = roughness
    bsdf.inputs["Metallic"].default_value = metallic
    return mat


def add_box(name, size, location, mat=None, rotation=(0.0, 0.0, 0.0)):
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=location, rotation=rotation)
    obj = bpy.context.active_object
    obj.name = name
    obj.scale = size
    if mat:
        obj.data.materials.append(mat)
    return obj


def corrugated_panel(name, length, height, location, rot_z, mat, thickness=0.04):
    """Zig-zag profile swept vertically, thickened with a solidify modifier."""
    n = max(2, int(round(length / PITCH)))
    n += n % 2
    step = length / n
    mesh = bpy.data.meshes.new(name)
    bm = bmesh.new()
    cols = []
    for i in range(n + 1):
        x = -length * 0.5 + i * step
        y = DEPTH if i % 2 else -DEPTH
        cols.append((bm.verts.new((x, y, 0.0)), bm.verts.new((x, y, height))))
    for i in range(n):
        bm.faces.new((cols[i][0], cols[i + 1][0], cols[i + 1][1], cols[i][1]))
    bm.normal_update()
    bm.to_mesh(mesh)
    bm.free()
    obj = bpy.data.objects.new(name, mesh)
    bpy.context.collection.objects.link(obj)
    obj.location = location
    obj.rotation_euler = (0.0, 0.0, rot_z)
    obj.data.materials.append(mat)
    solid = obj.modifiers.new("Skin", 'SOLIDIFY')
    solid.thickness = thickness
    solid.offset = 0.0
    return obj


def add_cylinder(name, radius, depth, location, mat, rotation=(0.0, 0.0, 0.0)):
    bpy.ops.mesh.primitive_cylinder_add(radius=radius, depth=depth, vertices=16,
                                        location=location, rotation=rotation)
    obj = bpy.context.active_object
    obj.name = name
    obj.data.materials.append(mat)
    return obj


def door_leaf(side, swing, paint, metal):
    """Hinged door half; `side` is +1 (left) or -1 (right), `swing` in radians."""
    hinge = Vector((L * 0.5, side * W * 0.5, 0.0))
    angle = side * swing
    M = Matrix.Translation(hinge) @ Matrix.Rotation(angle, 4, 'Z')
    dw = W * 0.5 - 0.04
    tag = "L" if side > 0 else "R"
    corrugated_panel("Door_" + tag, dw, H - 0.22,
                     M @ Vector((0.0, -side * dw * 0.5, 0.16)),
                     math.pi * 0.5 + angle, paint, thickness=0.05)
    for frac, label in ((0.22, "a"), (0.72, "b")):
        local = Vector((0.09, -side * dw * frac, (H - 0.22) * 0.5 + 0.16))
        add_cylinder("LockBar_%s%s" % (tag, label), 0.026, H - 0.4, M @ local, metal)
        handle = Vector((0.17, -side * dw * frac, 1.05))
        add_box("Handle_%s%s" % (tag, label), (0.16, 0.05, 0.06), M @ handle, metal,
                rotation=(0.0, 0.0, angle))


def aim(obj, target):
    obj.rotation_euler = (Vector(target) - obj.location).to_track_quat('-Z', 'Y').to_euler()


clear_scene()
paint = make_material("ContainerPaint", (0.52, 0.15, 0.09), roughness=0.62, metallic=0.25)
metal = make_material("DarkSteel", (0.11, 0.11, 0.12), roughness=0.45, metallic=0.9)
casting = make_material("CornerCasting", (0.3, 0.3, 0.32), roughness=0.5, metallic=0.8)
plank = make_material("FloorPlywood", (0.33, 0.24, 0.14), roughness=0.9)
concrete = make_material("Concrete", (0.42, 0.42, 0.41), roughness=0.95)

add_box("Ground", (24.0, 24.0, 0.1), (0.0, 0.0, -0.05), concrete)

# corrugated shell: two long sides + rear end wall
for s in (1, -1):
    corrugated_panel("SideWall_%s" % ("L" if s > 0 else "R"), L - 0.24, H - 0.22,
                     (0.0, s * (W * 0.5 - 0.03), 0.16), 0.0, paint)
corrugated_panel("RearWall", W - 0.24, H - 0.22,
                 (-L * 0.5 + 0.03, 0.0, 0.16), math.pi * 0.5, paint)

add_box("Roof", (L, W, 0.06), (0.0, 0.0, H - 0.03), paint)
add_box("Floor", (L - 0.28, W - 0.2, 0.1), (0.0, 0.0, 0.15), plank)

# corner posts, rails and ISO corner castings
for sx in (1, -1):
    for sy in (1, -1):
        add_box("CornerPost", (0.12, 0.12, H), (sx * (L * 0.5 - 0.06), sy * (W * 0.5 - 0.06), H * 0.5), metal)
        for z in (0.09, H - 0.09):
            add_box("Casting", (0.18, 0.18, 0.18),
                    (sx * (L * 0.5 - 0.09), sy * (W * 0.5 - 0.09), z), casting)
for sy in (1, -1):
    for z in (0.06, H - 0.09):
        add_box("SideRail", (L, 0.11, 0.12), (0.0, sy * (W * 0.5 - 0.055), z), metal)
for z in (0.06, H - 0.09):
    add_box("EndRail", (0.11, W, 0.12), (-L * 0.5 + 0.055, 0.0, z), metal)
    add_box("DoorHeaderSill", (0.11, W, 0.14), (L * 0.5 - 0.055, 0.0, z), metal)

door_leaf(1, math.radians(38.0), paint, metal)
door_leaf(-1, 0.0, paint, metal)

light_data = bpy.data.lights.new("KeySun", type='SUN')
light_data.energy = 4.5
sun = bpy.data.objects.new("KeySun", light_data)
bpy.context.collection.objects.link(sun)
sun.location = (6.0, -8.0, 10.0)
aim(sun, (0.0, 0.0, 1.0))

cam_data = bpy.data.cameras.new("Camera")
cam_data.lens = 45.0
cam = bpy.data.objects.new("Camera", cam_data)
bpy.context.collection.objects.link(cam)
cam.location = (9.5, -8.5, 5.2)
aim(cam, (0.0, 0.0, 1.3))
bpy.context.scene.camera = cam
