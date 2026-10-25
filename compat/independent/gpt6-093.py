import bpy
import math
from mathutils import Vector

bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)

def material(name, color, metallic=0.0, roughness=0.4):
    m = bpy.data.materials.new(name)
    m.diffuse_color = (*color, 1)
    m.use_nodes = True
    p = m.node_tree.nodes.get('Principled BSDF')
    p.inputs['Base Color'].default_value = (*color, 1)
    p.inputs['Metallic'].default_value = metallic
    p.inputs['Roughness'].default_value = roughness
    return m

stone = material('Warm limestone pedestal', (0.52, 0.49, 0.43))
bronze = material('Brushed bronze trim', (0.27, 0.16, 0.065), 0.8, 0.28)
velvet = material('Charcoal exhibit liner', (0.025, 0.035, 0.04), 0, 0.85)
ceramic = material('Terracotta artifact', (0.43, 0.13, 0.055), 0.12, 0.38)
ink = material('Ivory lettering', (0.88, 0.84, 0.69))
floor = material('Gallery floor', (0.16, 0.18, 0.20), 0, 0.65)
glass = material('Optical display glass', (0.91, 0.98, 0.97), 0, 0.055)
glass.node_tree.nodes.get('Principled BSDF').inputs['Transmission Weight'].default_value = 1.0
glass.node_tree.nodes.get('Principled BSDF').inputs['IOR'].default_value = 1.45

def box(name, loc, dims, mat, bevel=0.0):
    bpy.ops.mesh.primitive_cube_add(size=1, location=loc)
    o = bpy.context.object
    o.name = name
    o.dimensions = dims
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    o.data.materials.append(mat)
    if bevel:
        mod = o.modifiers.new('Soft manufactured edges', 'BEVEL')
        mod.width = bevel
        mod.segments = 3
        o.modifiers.new('Weighted corner normals', 'WEIGHTED_NORMAL')
    return o

def text(name, body, loc, size, mat):
    bpy.ops.object.text_add(location=loc, rotation=(math.pi / 2, 0, 0))
    o = bpy.context.object
    o.name = name
    o.data.body = body
    o.data.align_x = 'CENTER'
    o.data.size = size
    o.data.extrude = 0.0005
    o.data.materials.append(mat)

box('Gallery floor slab', (0, 0, -0.10), (12, 12, 0.2), floor, 0.03)
box('Recessed pedestal foot', (0, 0, 0.075), (1.60, 1.30, 0.15), velvet, 0.025)
box('Solid stone pedestal', (0, 0, 0.67), (1.85, 1.55, 1.12), stone, 0.035)
box('Bronze display sill', (0, 0, 1.25), (1.96, 1.66, 0.08), bronze, 0.015)
box('Dark inset display surface', (0, 0, 1.302), (1.78, 1.48, 0.025), velvet, 0.008)
box('Front glass pane', (0, -0.769, 2.07), (1.80, 0.012, 1.51), glass)
box('Rear glass pane', (0, 0.769, 2.07), (1.80, 0.012, 1.51), glass)
for x in (-0.914, 0.914):
    box('Side glass pane', (x, 0, 2.07), (0.012, 1.53, 1.51), glass)
    for y in (-0.785, 0.785):
        box('Slim bronze corner upright', (x, y, 2.075), (0.025, 0.025, 1.59), bronze, 0.003)
box('Glass enclosure roof', (0, 0, 2.838), (1.85, 1.58, 0.014), glass)
for y in (-0.80, 0.80):
    box('Upper perimeter rail', (0, y, 2.86), (1.88, 0.025, 0.035), bronze, 0.004)
for x in (-0.928, 0.928):
    box('Upper side rail', (x, 0, 2.86), (0.025, 1.60, 0.035), bronze, 0.004)
box('Artifact support block', (0, 0, 1.365), (0.72, 0.66, 0.10), stone, 0.012)

# Revolved vessel profile returns down the inside to form a visible hollow mouth.
profile = [(0, 0), (0.19, 0), (0.21, 0.06), (0.22, 0.12),
           (0.34, 0.29), (0.36, 0.48), (0.29, 0.67), (0.15, 0.80),
           (0.145, 0.93), (0.19, 0.96), (0.19, 1.00), (0.155, 1.00),
           (0.115, 0.94), (0.12, 0.81), (0.255, 0.65), (0.32, 0.47),
           (0.30, 0.30), (0.17, 0.13), (0, 0.10)]
segments = 48
verts = [(r * math.cos(i * math.tau / segments), r * math.sin(i * math.tau / segments), z + 1.42)
         for r, z in profile for i in range(segments)]
faces = []
for j in range(len(profile) - 1):
    for i in range(segments):
        a = j * segments + i
        b = j * segments + (i + 1) % segments
        faces.append((a, b, b + segments, a + segments))
mesh = bpy.data.meshes.new('Hollow ceramic vessel mesh')
mesh.from_pydata(verts, [], faces)
mesh.update()
vessel = bpy.data.objects.new('Exhibit - ceremonial terracotta vessel', mesh)
bpy.context.collection.objects.link(vessel)
vessel.data.materials.append(ceramic)
for p in mesh.polygons:
    p.use_smooth = True
box('Museum identification plaque', (0, -0.785, 0.89), (1.15, 0.025, 0.28), bronze, 0.015)
text('Plaque title', 'CEREMONIAL VESSEL', (0, -0.801, 0.93), 0.069, ink)
text('Plaque accession', 'COLLECTION 07  /  STUDY REPLICA', (0, -0.801, 0.835), 0.032, ink)

def aim(obj, point):
    obj.rotation_euler = (Vector(point) - obj.location).to_track_quat('-Z', 'Y').to_euler()

for name, loc, power, size in [('Gallery key', (3, -4, 6), 650, 4), ('Gallery fill', (-3, -1, 4), 400, 3), ('Rim light', (1, 3, 5), 550, 3)]:
    bpy.ops.object.light_add(type='AREA', location=loc)
    light = bpy.context.object
    light.name = name
    light.data.energy = power
    light.data.shape = 'DISK'
    light.data.size = size
    aim(light, (0, 0, 1.6))
bpy.ops.object.camera_add(location=(4.1, -6.2, 3.8))
camera = bpy.context.object
camera.name = 'Museum display camera'
aim(camera, (0, 0, 1.43))
camera.data.type = 'ORTHO'
camera.data.ortho_scale = 4.25
scene = bpy.context.scene
scene.camera = camera
scene.render.engine = 'CYCLES'
scene.world.color = (0.18, 0.18, 0.18)
scene.render.resolution_x = 1000
scene.render.resolution_y = 1000
scene.render.resolution_percentage = 100
