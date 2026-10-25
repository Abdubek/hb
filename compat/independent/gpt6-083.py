import bpy
import math
from mathutils import Vector

# Spiral display stand with eight staggered round display platforms.
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)

def material(name, color, metallic=0.0, roughness=0.4):
    mat = bpy.data.materials.new(name)
    mat.diffuse_color = (*color, 1)
    mat.use_nodes = True
    shader = mat.node_tree.nodes.get('Principled BSDF')
    shader.inputs['Base Color'].default_value = (*color, 1)
    shader.inputs['Metallic'].default_value = metallic
    shader.inputs['Roughness'].default_value = roughness
    return mat

steel = material('Graphite powder-coated steel', (0.065, 0.085, 0.095), 0.65)
wood = material('Warm maple shelves', (0.62, 0.35, 0.14), 0.0, 0.32)
brass = material('Brass shelf edge and fittings', (0.64, 0.43, 0.16), 0.75, 0.26)
floor_mat = material('Warm grey floor', (0.25, 0.27, 0.28))

def cylinder(name, location, radius, depth, mat, bevel=0.025):
    bpy.ops.mesh.primitive_cylinder_add(vertices=64, radius=radius, depth=depth, location=location)
    obj = bpy.context.object
    obj.name = name
    obj.data.materials.append(mat)
    if bevel:
        modifier = obj.modifiers.new('Soft manufactured edges', 'BEVEL')
        modifier.width = bevel
        modifier.segments = 3
    obj.modifiers.new('Weighted corner normals', 'WEIGHTED_NORMAL')
    return obj

def rod(name, start, end, radius, mat):
    start, end = Vector(start), Vector(end)
    obj = cylinder(name, (start + end) / 2, radius, (end - start).length, mat, 0.012)
    obj.rotation_euler = (end - start).to_track_quat('Z', 'Y').to_euler()
    return obj

cylinder('Heavy circular pedestal', (0, 0, 0.13), 1.02, 0.26, steel, 0.07)
cylinder('Pedestal brass reveal', (0, 0, 0.275), 0.82, 0.035, brass, 0.012)
cylinder('Pedestal upper boss', (0, 0, 0.33), 0.36, 0.11, steel)
cylinder('Continuous central mast', (0, 0, 2.22), 0.105, 3.9, steel)
cylinder('Mast crown', (0, 0, 4.19), 0.145, 0.08, brass)

for i in range(8):
    angle = math.radians(-110 + i * 48)
    z = 0.72 + i * 0.46
    direction = Vector((math.cos(angle), math.sin(angle), 0))
    center = direction * 0.82
    tag = 'Shelf %02d' % (i + 1)
    cylinder(tag + ' mast collar', (0, 0, z - 0.10), 0.15, 0.17, brass, 0.012)
    rod(tag + ' horizontal support', (0, 0, z - 0.10),
        (center.x, center.y, z - 0.10), 0.052, steel)
    brace_end = direction * 0.65
    rod(tag + ' diagonal brace', (0, 0, z - 0.37),
        (brace_end.x, brace_end.y, z - 0.11), 0.034, steel)
    cylinder(tag + ' underside mounting plate', (center.x, center.y, z - 0.085),
             0.17, 0.05, steel, 0.012)
    cylinder(tag + ' circular brass edge', (center.x, center.y, z),
             0.49, 0.12, brass, 0.018)
    cylinder(tag + ' maple display surface', (center.x, center.y, z + 0.018),
             0.468, 0.095, wood, 0.015)

# Three small feet lift the pedestal just above the ground.
for i in range(3):
    angle = i * math.tau / 3
    cylinder('Rubber foot %d' % (i + 1),
             (0.68 * math.cos(angle), 0.68 * math.sin(angle), -0.025),
             0.12, 0.05, steel, 0.015)

bpy.ops.mesh.primitive_plane_add(size=200, location=(0, 0, -0.055))
bpy.context.object.name = 'Studio ground'
bpy.context.object.data.materials.append(floor_mat)

bpy.ops.object.camera_add(location=(6.8, -9.4, 6.0))
camera = bpy.context.object
camera.name = 'Stand overview camera'
camera.rotation_euler = (Vector((0, 0, 2.0)) - camera.location).to_track_quat('-Z', 'Y').to_euler()
camera.data.type = 'ORTHO'
camera.data.ortho_scale = 5.9
bpy.context.scene.camera = camera

for name, location, energy, size in [
    ('Large key softbox', (4, -5, 8), 1200, 5),
    ('Fill softbox', (-4, -2, 5), 800, 4),
    ('Upper rim light', (1, 4, 7), 1100, 3)]:
    bpy.ops.object.light_add(type='AREA', location=location)
    light = bpy.context.object
    light.name = name
    light.data.energy = energy
    light.data.shape = 'DISK'
    light.data.size = size
    light.rotation_euler = (Vector((0, 0, 2)) - light.location).to_track_quat('-Z', 'Y').to_euler()

scene = bpy.context.scene
scene.world = scene.world or bpy.data.worlds.new('Studio world')
scene.world.use_nodes = True
scene.world.node_tree.nodes['Background'].inputs[0].default_value = (0.15, 0.15, 0.15, 1)
scene.render.resolution_x = 900
scene.render.resolution_y = 1100
scene.render.resolution_percentage = 100
