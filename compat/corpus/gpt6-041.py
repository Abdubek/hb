import bpy, math
from mathutils import Vector

# Tiny cottage, with the entrance facing negative Y.
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)

def material(name, color, roughness=0.65, metallic=0.0):
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
        mod = o.modifiers.new('Soft edges', 'BEVEL')
        mod.width = bevel
        mod.segments = 2
        o.modifiers.new('Weighted normals', 'WEIGHTED_NORMAL')
    return o

def beam(name, a, b, width, mat):
    d = Vector(b) - Vector(a)
    o = box(name, (Vector(a) + Vector(b)) / 2, (width, width, d.length), mat, 0.012)
    o.rotation_euler = d.to_track_quat('Z', 'Y').to_euler()
    return o

def mesh(name, vertices, faces, mat):
    data = bpy.data.meshes.new(name)
    data.from_pydata(vertices, [], faces)
    data.update()
    o = bpy.data.objects.new(name, data)
    bpy.context.collection.objects.link(o)
    o.data.materials.append(mat)
    return o

sage = material('Sage painted siding', (0.30, 0.43, 0.34))
trim = material('Warm ivory trim', (0.87, 0.82, 0.67))
roof = material('Charcoal standing seam roof', (0.095, 0.13, 0.15), 0.38, 0.55)
wood = material('Honey colored porch timber', (0.43, 0.24, 0.105))
door_mat = material('Burnt red front door', (0.40, 0.105, 0.075))
stone = material('Foundation stone', (0.37, 0.38, 0.35))
brick = material('Terracotta brick', (0.43, 0.18, 0.105))
mortar = material('Chimney mortar', (0.62, 0.57, 0.48))
black = material('Chimney opening', (0.025, 0.025, 0.024))
glass = material('Blue reflective windows', (0.16, 0.34, 0.42), 0.13, 0.35)
brass = material('Door hardware', (0.58, 0.38, 0.12), 0.25, 0.75)
grass = material('Muted green ground', (0.23, 0.30, 0.18))

box('Ground', (0, 0, -0.14), (200, 200, 0.2), grass)
box('Stone foundation', (0, 0, 0.23), (4.12, 4.72, 0.54), stone, 0.055)
box('House walls', (0, 0, 1.84), (4, 4.6, 2.72), sage)
for y in (-2.3, 2.3):
    mesh('Triangular gable', [(-2, y, 3.20), (2, y, 3.20), (0, y, 4.45)], [(0, 1, 2)], sage)
# Raised horizontal clapboard edges.
for i in range(15):
    z = 0.58 + i * 0.177
    for y in (-2.314, 2.314):
        box('Clapboard front or rear seam', (0, y, z), (4, 0.024, 0.025), sage)
    for x in (-2.014, 2.014):
        box('Clapboard side seam', (x, 0, z), (0.024, 4.6, 0.025), sage)
for x in (-2.025, 2.025):
    for y in (-2.32, 2.32):
        box('Corner board', (x, y, 1.86), (0.13, 0.10, 2.78), trim, 0.012)

rise, run = 1.43, 2.30
angle = math.atan2(rise, run)
for side in (-1, 1):
    o = box('Sloped metal roof', (side * run / 2, 0, 4.47 - rise / 2), (math.hypot(run, rise), 5.18, 0.115), roof, 0.025)
    o.rotation_euler[1] = side * angle
    for i in range(14):
        y = -2.50 + i * 5.0 / 13
        beam('Standing seam', (0, y, 4.56), (side * 2.3, y, 3.13), 0.028, roof)
    for y in (-2.60, 2.60):
        beam('Gable fascia', (0, y, 4.49), (side * 2.33, y, 3.04), 0.14, trim)
    box('Eave fascia', (side * 2.30, 0, 3.075), (0.12, 5.26, 0.18), trim)
beam('Roof ridge cap', (0, -2.63, 4.55), (0, 2.63, 4.55), 0.13, roof)

# Porch deck, steps, posts and a separate sloping canopy.
box('Porch front rim', (0, -3.67, 0.37), (4.3, 0.16, 0.30), wood, 0.02)
for i in range(24):
    box('Porch deck board', (-2.075 + i * 0.18, -3.00, 0.50), (0.17, 1.45, 0.12), wood, 0.008)
for x in (-1.92, 1.92):
    box('Porch footing', (x, -3.48, 0.18), (0.38, 0.38, 0.36), stone, 0.03)
    box('Porch post', (x, -3.48, 1.58), (0.17, 0.17, 2.16), trim, 0.012)
    beam('Post diagonal brace', (x, -3.48, 2.10), (x * 0.68, -3.48, 2.57), 0.10, trim)
box('Porch header', (0, -3.48, 2.62), (4.25, 0.20, 0.19), trim, 0.012)
canopy = box('Porch canopy', (0, -2.98, 2.86), (4.65, 1.65, 0.11), roof, 0.02)
canopy.rotation_euler[0] = math.radians(13)
for side in (-1, 1):
    x = side * 1.43
    for z in (0.75, 1.38):
        box('Porch front rail', (x, -3.48, z), (0.86, 0.10, 0.10), trim, 0.01)
    for j in range(5):
        box('Porch baluster', (side * (1.05 + j * 0.18), -3.48, 1.06), (0.045, 0.045, 0.60), trim)
    for z in (0.75, 1.38):
        box('Porch side rail', (side * 1.92, -2.92, z), (0.10, 1.12, 0.10), trim, 0.01)
    for j in range(6):
        box('Side baluster', (side * 1.92, -3.36 + j * 0.18, 1.06), (0.045, 0.045, 0.60), trim)
for i in range(3):
    box('Porch stair', (0, -4.15 + i * 0.28, 0.08 + i * 0.085), (1.70, 0.55, 0.16 + i * 0.17), wood, 0.018)

box('Front door', (-0.45, -2.344, 1.52), (0.88, 0.085, 1.95), door_mat, 0.018)
for x in (-0.95, 0.05):
    box('Door casing', (x, -2.405, 1.56), (0.10, 0.09, 2.08), trim, 0.01)
box('Door lintel', (-0.45, -2.405, 2.60), (1.10, 0.09, 0.12), trim, 0.01)
for z in (0.95, 1.58):
    box('Recessed door panel', (-0.45, -2.396, z), (0.64, 0.025, 0.45), wood, 0.015)
box('Door upper glass', (-0.45, -2.398, 2.18), (0.58, 0.028, 0.38), glass, 0.01)
bpy.ops.mesh.primitive_uv_sphere_add(segments=16, ring_count=8, radius=0.045, location=(-0.12, -2.465, 1.51))
bpy.context.object.name = 'Brass door knob'
bpy.context.object.data.materials.append(brass)

def front_window(x, z):
    box('Front window glass', (x, -2.355, z), (0.84, 0.04, 0.92), glass)
    for dx in (-0.47, 0.47):
        box('Window jamb', (x + dx, -2.405, z), (0.10, 0.11, 1.12), trim)
    for dz in (-0.51, 0.51):
        box('Window horizontal frame', (x, -2.405, z + dz), (1.04, 0.11, 0.10), trim)
    box('Window mullion', (x, -2.42, z), (0.045, 0.08, 0.95), trim)
    box('Window crossbar', (x, -2.42, z), (0.90, 0.08, 0.045), trim)
    box('Window sill', (x, -2.46, z - 0.56), (1.13, 0.25, 0.09), trim, 0.012)
front_window(1.15, 1.95)
for y in (-0.9, 1.0):
    box('Side window glass', (2.038, y, 1.97), (0.045, 1.03, 1.11), glass)
    for dy in (-0.57, 0.57):
        box('Side window jamb', (2.08, y + dy, 1.97), (0.12, 0.11, 1.31), trim)
    for dz in (-0.61, 0.61, 0):
        box('Side window cross frame', (2.08, y, 1.97 + dz), (0.12, 1.23, 0.085), trim)
    box('Side window mullion', (2.09, y, 1.97), (0.13, 0.05, 1.18), trim)

# Brick chimney extends through the rear roof plane.
box('Chimney mortar core', (1.13, 1.22, 4.25), (0.61, 0.65, 1.55), mortar)
for row in range(10):
    z = 3.54 + row * 0.155
    for side in (-1, 1):
        for j in range(3):
            box('Chimney face brick', (1.13 - 0.20 + j * 0.20, 1.22 + side * 0.335, z), (0.188, 0.04, 0.139), brick, 0.008)
        for j in range(3):
            box('Chimney side brick', (1.13 + side * 0.315, 1.22 - 0.21 + j * 0.21, z), (0.04, 0.199, 0.139), brick, 0.008)
box('Chimney crown', (1.13, 1.22, 5.07), (0.80, 0.84, 0.14), stone, 0.025)
box('Dark flue inset', (1.13, 1.22, 5.145), (0.42, 0.45, 0.012), black)
for x in (0.885, 1.375):
    box('Flue lip', (x, 1.22, 5.18), (0.07, 0.58, 0.11), brick)
for y in (0.965, 1.475):
    box('Flue lip', (1.13, y, 5.18), (0.56, 0.07, 0.11), brick)
for i in range(5):
    box('Garden stepping stone', (0.08 * math.sin(i), -4.8 - i * 0.72, 0.015), (0.95, 0.50, 0.08), stone, 0.08)

scene = bpy.context.scene
scene.render.engine = 'CYCLES'
scene.world.use_nodes = True
scene.world.node_tree.nodes['Background'].inputs[0].default_value = (0.64, 0.76, 0.89, 1)
scene.world.node_tree.nodes['Background'].inputs[1].default_value = 0.4
bpy.ops.object.light_add(type='AREA', location=(2, -5, 9))
bpy.context.object.data.energy = 1500
bpy.context.object.data.shape = 'DISK'
bpy.context.object.data.size = 7
bpy.context.object.rotation_euler = (Vector((0, 0, 1.8)) - bpy.context.object.location).to_track_quat('-Z', 'Y').to_euler()
bpy.ops.object.light_add(type='SUN', location=(0, 0, 8))
bpy.context.object.rotation_euler = (0.45, -0.5, -0.4)
bpy.context.object.data.energy = 2
bpy.context.object.data.angle = 0.12
bpy.ops.object.camera_add(location=(9, -12, 7.8))
camera = bpy.context.object
camera.rotation_euler = (Vector((0, -0.65, 2.1)) - camera.location).to_track_quat('-Z', 'Y').to_euler()
camera.data.type = 'ORTHO'
camera.data.ortho_scale = 11.8
scene.camera = camera
scene.render.resolution_x = 1400
scene.render.resolution_y = 1200
scene.render.resolution_percentage = 100
