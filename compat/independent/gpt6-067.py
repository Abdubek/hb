import bpy
import math
from mathutils import Vector

bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)

def material(name, color, metallic=0.0, roughness=0.45):
    m = bpy.data.materials.new(name)
    m.diffuse_color = (*color, 1)
    m.use_nodes = True
    bs = m.node_tree.nodes.get('Principled BSDF')
    bs.inputs['Base Color'].default_value = (*color, 1)
    bs.inputs['Metallic'].default_value = metallic
    bs.inputs['Roughness'].default_value = roughness
    return m

steel = material('Brushed stainless steel', (0.48, 0.55, 0.59), 0.8, 0.26)
rubber = material('Rubber tires and grips', (0.025, 0.032, 0.038))
deck = material('Charcoal platform', (0.10, 0.13, 0.15))
navy = material('Navy suitcase', (0.035, 0.12, 0.23))
rust = material('Terracotta suitcase', (0.58, 0.17, 0.065))
sand = material('Sand suitcase', (0.70, 0.52, 0.30))
trim = material('Leather trim', (0.12, 0.075, 0.04))
floor = material('Floor', (0.32, 0.36, 0.40))

def box(name, location, scale, mat, bevel=0.04):
    bpy.ops.mesh.primitive_cube_add(size=1, location=location)
    o = bpy.context.object
    o.name = name
    o.dimensions = scale
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    o.data.materials.append(mat)
    if bevel:
        mod = o.modifiers.new('Soft manufactured edges', 'BEVEL')
        mod.width = bevel
        mod.segments = 3
        o.modifiers.new('Weighted normals', 'WEIGHTED_NORMAL')
    return o

def rod(name, a, b, radius, mat):
    a, b = Vector(a), Vector(b)
    bpy.ops.mesh.primitive_cylinder_add(vertices=20, radius=radius,
                                      depth=(b-a).length, location=(a+b)/2)
    o = bpy.context.object
    o.name = name
    o.rotation_euler = (b-a).to_track_quat('Z', 'Y').to_euler()
    o.data.materials.append(mat)
    mod = o.modifiers.new('Edge rounding', 'BEVEL')
    mod.width = min(radius * 0.2, 0.025)
    mod.segments = 2
    o.modifiers.new('Weighted normals', 'WEIGHTED_NORMAL')
    return o

box('Low luggage platform', (0, 0, 0.63), (2.9, 1.85, 0.18), deck, 0.10)
for y in (-0.86, 0.86):
    rod('Platform perimeter rail', (-1.4, y, 0.75), (1.4, y, 0.75), 0.055, steel)
for x in (-1.2, 1.2):
    for y in (-0.64, 0.64):
        rod('Caster swivel stem', (x, y, 0.4), (x, y, 0.57), 0.065, steel)
        for dx in (-0.135, 0.135):
            box('Caster fork', (x+dx, y, 0.34), (0.05, 0.16, 0.27), steel, 0.025)
        rod('Rubber caster wheel', (x-0.11, y, 0.23), (x+0.11, y, 0.23), 0.23, rubber)
        rod('Caster axle cap', (x-0.17, y, 0.23), (x+0.17, y, 0.23), 0.075, steel)

for x in (-1.31, 1.31):
    rod('Rear handle upright', (x, 0.78, 0.72), (x, 0.78, 3.25), 0.065, steel)
    rod('Angled handle shoulder', (x, 0.78, 3.25), (x*0.80, 0.78, 3.50), 0.065, steel)
    rod('Side platform guard', (x, -0.73, 0.87), (x, 0.78, 0.87), 0.05, steel)
rod('Upper push handle', (-1.048, 0.78, 3.50), (1.048, 0.78, 3.50), 0.065, steel)
for x in (-0.67, 0.67):
    rod('Push handle rubber grip', (x-0.24, 0.78, 3.50), (x+0.24, 0.78, 3.50), 0.085, rubber)
rod('Rear support crossbar', (-1.31, 0.78, 1.35), (1.31, 0.78, 1.35), 0.05, steel)

def suitcase(name, x, y, z, w, d, h, mat):
    box(name + ' body', (x, y, z), (w, d, h), mat, 0.11)
    box(name + ' zipper seam', (x, y, z), (w+0.008, d+0.008, 0.035), rubber, 0.014)
    for dx in (-w*0.32, w*0.32):
        box(name + ' wrap strap', (x+dx, y, z), (0.085, d+0.025, h+0.012), trim, 0.018)
    for dx in (-0.23, 0.23):
        box(name + ' handle mount', (x+dx, y-d/2-0.035, z), (0.09, 0.12, 0.12), steel)
    rod(name + ' carry handle', (x-0.23, y-d/2-0.11, z),
        (x+0.23, y-d/2-0.11, z), 0.045, trim)
    box(name + ' luggage tag', (x+0.4, y-d/2-0.035, z-0.08), (0.17, 0.025, 0.23), sand, 0.02)

suitcase('Large navy case', 0, -0.06, 1.11, 2.38, 1.42, 0.76, navy)
suitcase('Middle terracotta case', -0.12, -0.04, 1.81, 2.03, 1.28, 0.64, rust)
suitcase('Top sand case', 0.14, 0.0, 2.405, 1.65, 1.05, 0.55, sand)
box('Ground', (0, 0, -0.075), (200, 200, 0.15), floor, 0)

bpy.ops.object.camera_add(location=(5.3, -7.5, 4.8))
camera = bpy.context.object
camera.name = 'Cart presentation camera'
camera.rotation_euler = (Vector((0, 0, 1.75))-camera.location).to_track_quat('-Z', 'Y').to_euler()
camera.data.type = 'ORTHO'
camera.data.ortho_scale = 5.4
bpy.context.scene.camera = camera
for name, position, power, size in [('Key', (1, -4, 7), 1100, 5), ('Fill', (-4, 1, 5), 850, 4)]:
    bpy.ops.object.light_add(type='AREA', location=position)
    light = bpy.context.object
    light.name = name
    light.data.energy = power
    light.data.shape = 'DISK'
    light.data.size = size
    light.rotation_euler = (Vector((0, 0, 1.5))-light.location).to_track_quat('-Z', 'Y').to_euler()
scene = bpy.context.scene
scene.world = bpy.data.worlds.new('Studio world')
scene.world.use_nodes = True
scene.world.node_tree.nodes['Background'].inputs[0].default_value = (0.3, 0.3, 0.3, 1)
scene.world.node_tree.nodes['Background'].inputs[1].default_value = 0.5
scene.render.resolution_x = 1000
scene.render.resolution_y = 1000
scene.render.resolution_percentage = 100
