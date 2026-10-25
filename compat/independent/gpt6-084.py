import bpy
import math
from mathutils import Vector

# Cylindrical perfume bottle with a shaped shoulder, fitted cap and curved label.
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)

def material(name, color, metallic=0.0, roughness=0.35):
    mat = bpy.data.materials.new(name)
    mat.diffuse_color = (*color, 1)
    mat.use_nodes = True
    shader = mat.node_tree.nodes.get('Principled BSDF')
    shader.inputs['Base Color'].default_value = (*color, 1)
    shader.inputs['Metallic'].default_value = metallic
    shader.inputs['Roughness'].default_value = roughness
    return mat

bottle_mat = material('Opaque amber lacquered glass', (0.24, 0.068, 0.018), 0.15, 0.16)
cap_mat = material('Satin charcoal cap', (0.025, 0.03, 0.035), 0.45, 0.25)
gold = material('Champagne gold metal', (0.72, 0.51, 0.24), 0.8, 0.23)
paper = material('Ivory label paper', (0.91, 0.86, 0.73), 0, 0.65)
ink = material('Dark label lettering', (0.045, 0.031, 0.022), 0, 0.6)
ground = material('Studio stone', (0.23, 0.25, 0.27), 0, 0.6)

def cylinder(name, radius, depth, z, mat, bevel=0.02):
    bpy.ops.mesh.primitive_cylinder_add(vertices=96, radius=radius, depth=depth, location=(0, 0, z))
    obj = bpy.context.object
    obj.name = name
    obj.data.materials.append(mat)
    edge = obj.modifiers.new('Rounded edges', 'BEVEL')
    edge.width = bevel
    edge.segments = 3
    obj.modifiers.new('Weighted normals', 'WEIGHTED_NORMAL')
    return obj

# Revolved cross-section gives the bottle a heavy heel and soft shoulder.
profile = [(0.60, 0.06), (0.67, 0.08), (0.71, 0.15), (0.72, 0.24),
           (0.72, 1.98), (0.71, 2.10), (0.67, 2.20), (0.58, 2.28),
           (0.38, 2.35), (0.30, 2.39), (0.30, 2.52)]
segments = 96
verts = [(r * math.cos(i * math.tau / segments), r * math.sin(i * math.tau / segments), z)
         for r, z in profile for i in range(segments)]
faces = []
for j in range(len(profile) - 1):
    for i in range(segments):
        a = j * segments + i
        b = j * segments + (i + 1) % segments
        faces.append((a, b, b + segments, a + segments))
faces.append(tuple(reversed(range(segments))))
faces.append(tuple((len(profile) - 1) * segments + i for i in range(segments)))
mesh = bpy.data.meshes.new('Revolved bottle mesh')
mesh.from_pydata(verts, [], faces)
mesh.update()
body = bpy.data.objects.new('Amber cylindrical perfume bottle', mesh)
bpy.context.collection.objects.link(body)
body.data.materials.append(bottle_mat)
for polygon in mesh.polygons:
    polygon.use_smooth = len(polygon.vertices) == 4

cylinder('Gold neck collar', 0.325, 0.13, 2.45, gold, 0.015)
cylinder('Cap lower gold band', 0.407, 0.065, 2.54, gold, 0.01)
cylinder('Fitted cylindrical charcoal cap', 0.415, 0.58, 2.85, cap_mat, 0.045)
cylinder('Cap crown inset', 0.32, 0.012, 3.143, gold, 0.006)
cylinder('Bottle heel accent ring', 0.719, 0.028, 0.245, gold, 0.007)

# A thin curved patch hugs the front of the cylindrical wall.
def label_patch(name, radius, half_angle, bottom, top, mat):
    steps = 32
    vertices = []
    for z in (bottom, top):
        for i in range(steps + 1):
            angle = -half_angle + 2 * half_angle * i / steps
            vertices.append((radius * math.sin(angle), -radius * math.cos(angle), z))
    quads = [(i, i + 1, i + steps + 2, i + steps + 1) for i in range(steps)]
    data = bpy.data.meshes.new(name + ' mesh')
    data.from_pydata(vertices, [], quads)
    data.update()
    obj = bpy.data.objects.new(name, data)
    bpy.context.collection.objects.link(obj)
    obj.data.materials.append(mat)
    for polygon in data.polygons:
        polygon.use_smooth = True
    solid = obj.modifiers.new('Label thickness', 'SOLIDIFY')
    solid.thickness = 0.003
    return obj

label_patch('Gold bordered label panel', 0.725, 0.70, 0.68, 1.83, gold)
label_patch('Ivory label inset', 0.730, 0.655, 0.72, 1.79, paper)

def text(name, content, z, size, mat):
    bpy.ops.object.text_add(location=(0, -0.747, z), rotation=(math.pi / 2, 0, 0))
    obj = bpy.context.object
    obj.name = name
    obj.data.body = content
    obj.data.align_x = 'CENTER'
    obj.data.align_y = 'CENTER'
    obj.data.size = size
    obj.data.extrude = 0.0005
    obj.data.materials.append(mat)

text('House name', 'ATELIER', 1.59, 0.11, ink)
text('Fragrance name', 'AMBRE', 1.30, 0.155, ink)
text('Concentration', 'EAU DE PARFUM', 1.04, 0.065, ink)
text('Bottle volume', '50 ml', 0.86, 0.075, ink)

bpy.ops.mesh.primitive_plane_add(size=200, location=(0, 0, 0.055))
bpy.context.object.name = 'Studio surface'
bpy.context.object.data.materials.append(ground)
bpy.ops.object.camera_add(location=(3.1, -8.5, 4.0))
camera = bpy.context.object
camera.name = 'Perfume product camera'
camera.rotation_euler = (Vector((0, 0, 1.60)) - camera.location).to_track_quat('-Z', 'Y').to_euler()
camera.data.type = 'ORTHO'
camera.data.ortho_scale = 4.15
bpy.context.scene.camera = camera
for location, power, size in [((3, -4, 6), 850, 4), ((-3, -2, 4), 600, 3), ((1, 3, 5), 1000, 3)]:
    bpy.ops.object.light_add(type='AREA', location=location)
    light = bpy.context.object
    light.name = 'Product softbox'
    light.data.energy = power
    light.data.size = size
    light.rotation_euler = (Vector((0, 0, 1.5)) - light.location).to_track_quat('-Z', 'Y').to_euler()
scene = bpy.context.scene
scene.world = scene.world or bpy.data.worlds.new('Studio world')
scene.world.use_nodes = True
scene.world.node_tree.nodes['Background'].inputs[0].default_value = (0.18, 0.18, 0.18, 1)
scene.render.resolution_x = 900
scene.render.resolution_y = 1100
scene.render.resolution_percentage = 100
