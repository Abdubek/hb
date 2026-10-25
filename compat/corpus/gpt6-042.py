import bpy, math, random
from mathutils import Vector

bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)
random.seed(42)

def material(name, color, roughness=0.6, metallic=0):
    m = bpy.data.materials.new(name)
    m.diffuse_color = (*color, 1)
    m.use_nodes = True
    p = m.node_tree.nodes.get('Principled BSDF')
    p.inputs['Base Color'].default_value = (*color, 1)
    p.inputs['Roughness'].default_value = roughness
    p.inputs['Metallic'].default_value = metallic
    return m

def box(name, loc, size, mat, bevel=0):
    bpy.ops.mesh.primitive_cube_add(size=1, location=loc)
    o = bpy.context.object
    o.name = name
    o.dimensions = size
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    o.data.materials.append(mat)
    if bevel:
        b = o.modifiers.new('Edge highlights', 'BEVEL')
        b.width = bevel
        b.segments = 2
        o.modifiers.new('Weighted normals', 'WEIGHTED_NORMAL')
    return o

def beam(name, a, b, width, mat):
    d = Vector(b) - Vector(a)
    o = box(name, (Vector(a) + Vector(b)) / 2, (width, width, d.length), mat, 0.006)
    o.rotation_euler = d.to_track_quat('Z', 'Y').to_euler()
    return o

def panel(name, verts, mat):
    mesh = bpy.data.meshes.new(name)
    mesh.from_pydata(verts, [], [tuple(range(len(verts)))])
    mesh.update()
    o = bpy.data.objects.new(name, mesh)
    bpy.context.collection.objects.link(o)
    o.data.materials.append(mat)
    return o

def cylinder(name, loc, radius, depth, mat, vertices=24):
    bpy.ops.mesh.primitive_cylinder_add(vertices=vertices, radius=radius, depth=depth, location=loc)
    o = bpy.context.object
    o.name = name
    o.data.materials.append(mat)
    bevel = o.modifiers.new('Rounded lip', 'BEVEL')
    bevel.width = 0.012
    bevel.segments = 2
    o.modifiers.new('Weighted normals', 'WEIGHTED_NORMAL')
    return o

frame = material('Forest green metal frame', (0.055, 0.17, 0.13), 0.35, 0.6)
wood = material('Cedar bench slats', (0.49, 0.30, 0.15))
concrete = material('Foundation curb', (0.47, 0.46, 0.39))
gravel = material('Gravel floor', (0.39, 0.36, 0.28))
soil = material('Dark potting soil', (0.075, 0.044, 0.023))
terra = material('Terracotta pots', (0.57, 0.24, 0.12))
leaf_mats = [material('Leaf green ' + str(i), c) for i, c in enumerate([(0.14, 0.35, 0.065), (0.26, 0.45, 0.10), (0.055, 0.24, 0.09)])]
red = material('Ripe tomatoes', (0.65, 0.045, 0.025), 0.35)
ground = material('Garden earth', (0.22, 0.27, 0.17))
# A thin-sheet glass shader gives an unobstructed view of the planting benches.
glass = bpy.data.materials.new('Clear horticultural glass')
glass.use_nodes = True
n = glass.node_tree.nodes
n.clear()
out = n.new('ShaderNodeOutputMaterial')
transparent = n.new('ShaderNodeBsdfTransparent')
reflect = n.new('ShaderNodeBsdfPrincipled')
reflect.inputs['Base Color'].default_value = (0.72, 0.90, 0.83, 1)
reflect.inputs['Metallic'].default_value = 0.8
reflect.inputs['Roughness'].default_value = 0.09
fresnel = n.new('ShaderNodeFresnel')
fresnel.inputs['IOR'].default_value = 1.45
mix = n.new('ShaderNodeMixShader')
glass.node_tree.links.new(fresnel.outputs[0], mix.inputs[0])
glass.node_tree.links.new(transparent.outputs[0], mix.inputs[1])
glass.node_tree.links.new(reflect.outputs[0], mix.inputs[2])
glass.node_tree.links.new(mix.outputs[0], out.inputs[0])
glass.diffuse_color = (0.72, 0.9, 0.83, 0.15)

box('Ground', (0, 0, -0.18), (200, 200, 0.2), ground)
box('Greenhouse gravel pad', (0, 0, -0.015), (4.25, 6.25, 0.17), gravel, 0.04)
for x in (-2, 2):
    box('Foundation side curb', (x, 0, 0.12), (0.18, 6.18, 0.24), concrete, 0.025)
for y in (-3, 3):
    box('Foundation end curb', (0, y, 0.12), (4, 0.18, 0.24), concrete, 0.025)
for i in range(10):
    box('Central aisle paver', (0, -2.72 + i * 0.60, 0.095), (0.89, 0.55, 0.08), concrete, 0.025)

# Repeated structural bays with a pitched glass roof.
for y in (-3, -2, -1, 0, 1, 2, 3):
    for x in (-2, 2):
        beam('Wall upright', (x, y, 0.22), (x, y, 2.65), 0.075, frame)
        beam('Roof rafter', (x, y, 2.65), (0, y, 3.85), 0.085, frame)
for x in (-2, 2):
    for z in (0.25, 1.42, 2.65):
        beam('Side horizontal rail', (x, -3.04, z), (x, 3.04, z), 0.07, frame)
for x in (-1, 0, 1):
    z = 3.85 - abs(x) * 0.60
    beam('Roof longitudinal purlin', (x, -3.08, z), (x, 3.08, z), 0.07, frame)
for y in (-3, 3):
    beam('End eave rail', (-2, y, 2.65), (2, y, 2.65), 0.075, frame)
    beam('End foundation rail', (-2, y, 0.25), (2, y, 0.25), 0.075, frame)
    for x in (-1, 0, 1):
        beam('Gable upright', (x, y, 2.65), (x, y, 3.85 - abs(x) * 0.6), 0.06, frame)
    panel('Gable glazing', [(-1.96, y, 2.69), (1.96, y, 2.69), (0, y, 3.81)], glass)
for i in range(6):
    a, b = -2.96 + i, -2.04 + i
    for x in (-2, 2):
        for lo, hi in ((0.29, 1.38), (1.46, 2.61)):
            panel('Side glass pane', [(x, a, lo), (x, b, lo), (x, b, hi), (x, a, hi)], glass)
    for side in (-1, 1):
        for j in range(2):
            x1, x2 = side * (0.04 + j), side * (0.96 + j)
            z1, z2 = 3.85 - abs(x1) * 0.6, 3.85 - abs(x2) * 0.6
            panel('Roof glass pane', [(x1, a, z1), (x2, a, z2), (x2, b, z2), (x1, b, z1)], glass)
# Rear glazing and front panels leave a real open doorway.
for x in (-1, 0, 1):
    beam('Rear wall mullion', (x, 3, 0.25), (x, 3, 2.65), 0.07, frame)
for i in range(4):
    x = -1.96 + i
    panel('Rear glass', [(x, 3, 0.29), (x + 0.92, 3, 0.29), (x + 0.92, 3, 2.61), (x, 3, 2.61)], glass)
for side in (-1, 1):
    x = side * 0.56
    beam('Door jamb', (x, -3, 0.25), (x, -3, 2.65), 0.085, frame)
    panel('Front fixed glass', [(side * 0.61, -3, 0.29), (side * 1.96, -3, 0.29), (side * 1.96, -3, 2.61), (side * 0.61, -3, 2.61)], glass)
beam('Door lintel', (-0.56, -3, 2.35), (0.56, -3, 2.35), 0.075, frame)
panel('Door transom', [(-0.52, -3, 2.40), (0.52, -3, 2.40), (0.52, -3, 2.61), (-0.52, -3, 2.61)], glass)
# Door swung outward around its left hinge.
hinge = Vector((-0.56, -3.025, 0))
a = math.radians(-58)
def door_point(x, z):
    return hinge + Vector((x * math.cos(a), x * math.sin(a), z))
for x in (0, 1.10):
    beam('Open door stile', door_point(x, 0.26), door_point(x, 2.32), 0.065, frame)
for z in (0.26, 1.28, 2.32):
    beam('Open door rail', door_point(0, z), door_point(1.10, z), 0.065, frame)
panel('Door glass', [door_point(0.04, 0.30), door_point(1.06, 0.30), door_point(1.06, 2.28), door_point(0.04, 2.28)], glass)
beam('Door handle', door_point(0.95, 1.14) + Vector((0, -0.06, 0)), door_point(0.95, 1.42) + Vector((0, -0.06, 0)), 0.035, frame)

# Slatted planting tables along both sides, with lower shelves.
for x in (-1.27, 1.27):
    for y in (-2.23, 0, 2.23):
        for dx in (-0.40, 0.40):
            box('Bench leg', (x + dx, y, 0.54), (0.085, 0.085, 0.98), frame, 0.009)
    for dx in (-0.42, 0.42):
        box('Bench apron', (x + dx, 0, 0.92), (0.08, 5.1, 0.15), wood, 0.01)
    for j in range(5):
        for z in (1.03, 0.35):
            box('Bench slat', (x - 0.38 + j * 0.19, 0, z), (0.17, 5.14, 0.065), wood, 0.007)
    for y in (-1.5, 1.4):
        box('Lower shelf soil bag', (x, y, 0.48), (0.66, 0.48, 0.20), soil, 0.09)

def plant(x, y, scale, variant):
    base = 1.065
    bpy.ops.mesh.primitive_cone_add(vertices=24, radius1=0.13 * scale, radius2=0.19 * scale, depth=0.26 * scale, location=(x, y, base + 0.13 * scale))
    bpy.context.object.name = 'Tapered terracotta plant pot'
    bpy.context.object.data.materials.append(terra)
    cylinder('Pot rolled rim', (x, y, base + 0.25 * scale), 0.201 * scale, 0.045 * scale, terra)
    cylinder('Visible pot soil', (x, y, base + 0.275 * scale), 0.169 * scale, 0.012, soil)
    z0 = base + 0.28 * scale
    beam('Plant stem', (x, y, z0), (x, y, z0 + 0.59 * scale), 0.018 * scale, leaf_mats[2])
    for k in range(7):
        angle = k * 2.4 + variant
        h = (0.11 + k * 0.064) * scale
        start = Vector((x, y, z0 + h))
        end = start + Vector((math.cos(angle) * 0.22, math.sin(angle) * 0.22, 0.10)) * scale
        beam('Leaf stalk', start, end, 0.010 * scale, leaf_mats[2])
        bpy.ops.mesh.primitive_uv_sphere_add(segments=12, ring_count=8, radius=1, location=end)
        leaf = bpy.context.object
        leaf.name = 'Pointed oval leaf'
        leaf.scale = (0.085 * scale, 0.025 * scale, 0.19 * scale)
        leaf.rotation_euler = Vector((math.cos(angle), math.sin(angle), 0.45)).to_track_quat('Z', 'Y').to_euler()
        leaf.data.materials.append(leaf_mats[variant % 3])
        for polygon in leaf.data.polygons:
            polygon.use_smooth = True
    if variant % 3 == 0:
        for k in range(3):
            angle = k * 2.1
            bpy.ops.mesh.primitive_uv_sphere_add(segments=16, ring_count=8, radius=0.057 * scale, location=(x + 0.12 * math.cos(angle) * scale, y + 0.12 * math.sin(angle) * scale, z0 + 0.3 * scale))
            bpy.context.object.name = 'Tomato fruit'
            bpy.context.object.data.materials.append(red)
for side in (-1, 1):
    for i in range(7):
        plant(side * 1.27 + random.uniform(-0.10, 0.10), -2.25 + i * 0.74, random.uniform(0.78, 1.12), i)
# Seed tray on the front corner of a bench.
box('Seed tray', (1.32, -2.69, 1.11), (0.70, 0.30, 0.075), frame, 0.025)
for i in range(5):
    cylinder('Seedling soil plug', (1.06 + i * 0.13, -2.69, 1.16), 0.049, 0.035, soil, 12)

scene = bpy.context.scene
scene.render.engine = 'CYCLES'
scene.cycles.transparent_max_bounces = 16
scene.world.use_nodes = True
scene.world.node_tree.nodes['Background'].inputs[0].default_value = (0.68, 0.79, 0.90, 1)
scene.world.node_tree.nodes['Background'].inputs[1].default_value = 0.5
bpy.ops.object.light_add(type='AREA', location=(1, -4, 9))
bpy.context.object.data.energy = 1800
bpy.context.object.data.size = 7
bpy.context.object.rotation_euler = (Vector((0, 0, 1)) - bpy.context.object.location).to_track_quat('-Z', 'Y').to_euler()
bpy.ops.object.light_add(type='SUN')
bpy.context.object.rotation_euler = (0.35, -0.5, -0.5)
bpy.context.object.data.energy = 2
bpy.context.object.data.angle = 0.15
bpy.ops.object.camera_add(location=(9, -12, 8))
camera = bpy.context.object
camera.rotation_euler = (Vector((0, -0.2, 1.6)) - camera.location).to_track_quat('-Z', 'Y').to_euler()
camera.data.type = 'ORTHO'
camera.data.ortho_scale = 10.9
scene.camera = camera
scene.render.resolution_x = 1400
scene.render.resolution_y = 1200
scene.render.resolution_percentage = 100
