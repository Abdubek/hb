import bpy, math, random
from mathutils import Vector

bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)
random.seed(44)

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
        b = o.modifiers.new('Soft edges', 'BEVEL')
        b.width = bevel
        b.segments = 2
        o.modifiers.new('Weighted normals', 'WEIGHTED_NORMAL')
    return o

def tube(name, points, radius, mat):
    curve = bpy.data.curves.new(name, 'CURVE')
    curve.dimensions = '3D'
    curve.bevel_depth = radius
    curve.bevel_resolution = 4
    curve.use_fill_caps = True
    spline = curve.splines.new('POLY')
    spline.points.add(len(points) - 1)
    for p, co in zip(spline.points, points):
        p.co = (*co, 1)
    o = bpy.data.objects.new(name, curve)
    bpy.context.collection.objects.link(o)
    o.data.materials.append(mat)
    return o

sand = material('Limestone pool deck', (0.71, 0.64, 0.50), 0.8)
coping = material('Pale coping stones', (0.87, 0.82, 0.68), 0.65)
grout = material('Light blue waterproof grout', (0.47, 0.66, 0.70), 0.85)
tiles = [material('Ceramic aqua tile ' + str(i), c, 0.24) for i, c in enumerate([(0.15, 0.54, 0.66), (0.22, 0.62, 0.72), (0.30, 0.66, 0.73), (0.12, 0.47, 0.62)])]
navy = material('Deep blue lane tile', (0.025, 0.12, 0.22), 0.25)
steel = material('Polished stainless ladder', (0.67, 0.73, 0.77), 0.17, 0.93)
rubber = material('Black anti slip step inserts', (0.025, 0.035, 0.04), 0.8)
dark = material('Drain openings', (0.055, 0.07, 0.065), 0.85)
grass = material('Surrounding lawn', (0.23, 0.32, 0.16), 0.9)
wood = material('Teak loungers', (0.49, 0.29, 0.13), 0.65)
fabric = material('Cream lounger fabric', (0.88, 0.85, 0.72), 0.9)

# Pool opening is 8 by 4.5 meters; waterline is just below the coping.
box('Landscape beneath pool', (0, 0, -1.94), (200, 200, 0.4), grass)
box('Pool foundation slab', (0, 0, -1.76), (8.5, 5.0, 0.24), grout)
box('Pool floor grout bed', (0, 0, -1.625), (8, 4.5, 0.05), grout)
for y in (-2.38, 2.38):
    box('Long pool wall', (0, y, -0.73), (8.5, 0.26, 1.82), grout)
for x in (-4.13, 4.13):
    box('Short pool wall', (x, 0, -0.73), (0.26, 4.5, 1.82), grout)
# Individual tiles, combined into one mesh per material for efficient scene geometry.
batches = {m.name: [[], []] for m in tiles + [navy]}
def tile_quad(vertices, mat):
    vv, ff = batches[mat.name]
    start = len(vv)
    vv.extend(vertices)
    ff.append(tuple(start + i for i in range(4)))
for i in range(32):
    for j in range(18):
        x, y = -4 + i * 0.25, -2.25 + j * 0.25
        m = random.choice(tiles)
        if (j in (5, 12) and 3 <= i <= 28) or (i in (3, 28) and j in (4, 5, 6, 11, 12, 13)):
            m = navy
        g = 0.007
        tile_quad([(x + g, y + g, -1.594), (x + 0.25 - g, y + g, -1.594), (x + 0.25 - g, y + 0.25 - g, -1.594), (x + g, y + 0.25 - g, -1.594)], m)
for side in (-1, 1):
    y = side * 2.246
    for i in range(32):
        for j in range(7):
            x, z = -4 + i * 0.25, -1.6 + j * 0.25
            m = navy if j == 6 else random.choice(tiles)
            v = [(x + 0.007, y, z + 0.007), (x + 0.243, y, z + 0.007), (x + 0.243, y, z + 0.243), (x + 0.007, y, z + 0.243)]
            tile_quad(v if side == 1 else list(reversed(v)), m)
    x = side * 3.996
    for i in range(18):
        for j in range(7):
            y0, z = -2.25 + i * 0.25, -1.6 + j * 0.25
            m = navy if j == 6 else random.choice(tiles)
            v = [(x, y0 + 0.007, z + 0.007), (x, y0 + 0.243, z + 0.007), (x, y0 + 0.243, z + 0.243), (x, y0 + 0.007, z + 0.243)]
            tile_quad(v if side == -1 else list(reversed(v)), m)
for name, (verts, faces) in batches.items():
    mesh = bpy.data.meshes.new(name + ' mesh')
    mesh.from_pydata(verts, [], faces)
    mesh.update()
    o = bpy.data.objects.new(name + ' mosaic', mesh)
    bpy.context.collection.objects.link(o)
    o.data.materials.append(bpy.data.materials[name])

# Deck built as four solid strips around the open basin.
for y in (-3.40, 3.40):
    box('Long deck foundation', (0, y, -0.70), (12, 2.0, 1.6), sand)
for x in (-5.2, 5.2):
    box('End deck foundation', (x, 0, -0.70), (1.6, 4.8, 1.6), sand)
for y in (-3.45, 3.45):
    for i in range(15):
        for j in range(2):
            box('Deck paving slab', (-5.6 + i * 0.8, y - 0.45 + j * 0.9, 0.12), (0.785, 0.885, 0.055), sand, 0.012)
for x in (-5.20, 5.20):
    for i in range(2):
        for j in range(6):
            box('End deck paving slab', (x - 0.40 + i * 0.80, -2 + j * 0.8, 0.12), (0.785, 0.785, 0.055), sand, 0.012)
for y in (-2.42, 2.42):
    for i in range(16):
        box('Long coping tile', (-3.75 + i * 0.5, y, 0.18), (0.491, 0.40, 0.14), coping, 0.025)
for x in (-4.18, 4.18):
    for i in range(10):
        box('End coping tile', (x, -2.25 + i * 0.5, 0.18), (0.36, 0.491, 0.14), coping, 0.022)

# Closed transparent water volume, with a subtly rippled top surface.
water = material('Pool water', (0.83, 0.96, 0.98), 0.09)
p = water.node_tree.nodes.get('Principled BSDF')
p.inputs['Transmission Weight'].default_value = 1.0
p.inputs['IOR'].default_value = 1.333
tex = water.node_tree.nodes.new('ShaderNodeTexNoise')
tex.inputs['Scale'].default_value = 7
tex.inputs['Detail'].default_value = 2
bump = water.node_tree.nodes.new('ShaderNodeBump')
bump.inputs['Strength'].default_value = 0.13
bump.inputs['Distance'].default_value = 0.035
water.node_tree.links.new(tex.outputs['Fac'], bump.inputs['Height'])
water.node_tree.links.new(bump.outputs['Normal'], p.inputs['Normal'])
absorb = water.node_tree.nodes.new('ShaderNodeVolumeAbsorption')
absorb.inputs['Color'].default_value = (0.26, 0.73, 0.86, 1)
absorb.inputs['Density'].default_value = 0.055
water.node_tree.links.new(absorb.outputs[0], water.node_tree.nodes.get('Material Output').inputs['Volume'])
box('Water volume', (0, 0, -0.81), (7.976, 4.476, 1.54), water)

# Ladder sits at the near long edge, with curved rails over the coping.
for x in (2.48, 3.10):
    points = [(x, -2.95, 0.18), (x, -2.95, 0.83)]
    for i in range(25):
        a = math.pi - i * math.pi / 24
        points.append((x, -2.52 + 0.43 * math.cos(a), 0.83 + 0.43 * math.sin(a)))
    points.extend([(x, -2.09, 0.45), (x, -2.09, -1.22), (x, -2.17, -1.35)])
    tube('Curved stainless ladder rail', points, 0.037, steel)
    bpy.ops.mesh.primitive_cylinder_add(vertices=32, radius=0.10, depth=0.035, location=(x, -2.95, 0.175))
    bpy.context.object.name = 'Ladder anchor escutcheon'
    bpy.context.object.data.materials.append(steel)
    box('Ladder wall bumper', (x, -2.205, -1.35), (0.11, 0.08, 0.10), rubber, 0.02)
for z in (-0.10, -0.43, -0.76, -1.09):
    box('Ladder tread', (2.79, -2.07, z), (0.66, 0.19, 0.055), steel, 0.018)
    box('Anti slip tread pad', (2.79, -2.07, z + 0.032), (0.51, 0.14, 0.014), rubber, 0.008)
    for j in range(5):
        box('Tread grip rib', (2.59 + j * 0.10, -2.07, z + 0.043), (0.014, 0.13, 0.008), rubber)
# Linear deck drains.
for y in (-2.79, 2.79):
    box('Drain channel', (-0.8, y, 0.155), (5.0, 0.10, 0.016), dark, 0.01)
    for i in range(65):
        box('Drain grate bar', (-3.26 + i * 0.077, y, 0.17), (0.026, 0.10, 0.015), steel)
# Two simple slatted loungers furnish the far deck.
for cx in (-2.3, 0.5):
    for dx in (-0.73, 0.73):
        for dy in (-0.30, 0.30):
            box('Lounger leg', (cx + dx, 3.45 + dy, 0.34), (0.075, 0.075, 0.39), wood, 0.012)
    for dy in (-0.34, 0.34):
        box('Lounger side frame', (cx, 3.45 + dy, 0.48), (1.9, 0.08, 0.12), wood, 0.02)
    for i in range(11):
        box('Lounger seat slat', (cx - 0.85 + i * 0.13, 3.45, 0.55), (0.115, 0.70, 0.055), wood, 0.008)
    back = box('Raised lounger back', (cx + 0.68, 3.45, 0.77), (0.70, 0.69, 0.075), fabric, 0.035)
    back.rotation_euler[1] = -math.radians(35)

scene = bpy.context.scene
scene.render.engine = 'CYCLES'
scene.cycles.max_bounces = 12
scene.cycles.transmission_bounces = 8
scene.world.use_nodes = True
scene.world.node_tree.nodes['Background'].inputs[0].default_value = (0.66, 0.79, 0.92, 1)
scene.world.node_tree.nodes['Background'].inputs[1].default_value = 0.55
bpy.ops.object.light_add(type='SUN')
bpy.context.object.rotation_euler = (0.45, -0.4, -0.6)
bpy.context.object.data.energy = 2.5
bpy.context.object.data.angle = 0.08
bpy.ops.object.light_add(type='AREA', location=(-2, -3, 10))
bpy.context.object.data.energy = 1800
bpy.context.object.data.size = 8
bpy.context.object.rotation_euler = (Vector((0, 0, 0)) - bpy.context.object.location).to_track_quat('-Z', 'Y').to_euler()
bpy.ops.object.camera_add(location=(12, -15, 13))
camera = bpy.context.object
camera.rotation_euler = (Vector((0, 0, -0.3)) - camera.location).to_track_quat('-Z', 'Y').to_euler()
camera.data.type = 'ORTHO'
camera.data.ortho_scale = 16.5
scene.camera = camera
scene.render.resolution_x = 1600
scene.render.resolution_y = 1200
scene.render.resolution_percentage = 100
