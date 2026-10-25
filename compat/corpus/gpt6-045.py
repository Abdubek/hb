import bpy, math
from mathutils import Vector

bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)

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
        b = o.modifiers.new('Edge rounding', 'BEVEL')
        b.width = bevel
        b.segments = 3
        o.modifiers.new('Weighted normals', 'WEIGHTED_NORMAL')
    return o

def beam(name, a, b, width, depth, mat):
    d = Vector(b) - Vector(a)
    o = box(name, (Vector(a) + Vector(b)) / 2, (width, depth, d.length), mat, 0.01)
    o.rotation_euler = d.to_track_quat('Z', 'Y').to_euler()
    return o

def rod(name, a, b, radius, mat):
    d = Vector(b) - Vector(a)
    bpy.ops.mesh.primitive_cylinder_add(vertices=20, radius=radius, depth=d.length, location=(Vector(a) + Vector(b)) / 2)
    o = bpy.context.object
    o.name = name
    o.rotation_euler = d.to_track_quat('Z', 'Y').to_euler()
    o.data.materials.append(mat)
    for p in o.data.polygons:
        p.use_smooth = len(p.vertices) == 4
    return o

wood = material('Oiled oak treads and handrails', (0.57, 0.36, 0.17), 0.42)
wood_dark = material('Oak end grain and risers', (0.37, 0.21, 0.095), 0.57)
steel = material('Graphite steel structure', (0.075, 0.10, 0.12), 0.37, 0.7)
metal = material('Stainless fixings', (0.58, 0.63, 0.66), 0.28, 0.85)
floor = material('Warm neutral floor', (0.58, 0.56, 0.50), 0.88)

box('Architectural display floor', (0.6, -0.7, -0.13), (200, 200, 0.20), floor)
# Two perpendicular flights: seven 0.22 m rises each, with a square landing.
rise = 0.22
run = 0.32
count = 7
landing_z = count * rise
upper_z = 2 * landing_z
x_center = -0.90
y_start = -count * run
width = 1.50

# Lower flight, ascending in positive Y.
for i in range(count):
    front = y_start + i * run
    top = (i + 1) * rise
    box('Lower flight oak tread %02d' % (i + 1), (x_center, front + run / 2 - 0.015, top - 0.035), (width, run + 0.035, 0.07), wood, 0.014)
    box('Lower flight riser %02d' % (i + 1), (x_center, front + 0.012, top - rise / 2 - 0.02), (width - 0.07, 0.035, rise - 0.04), wood_dark, 0.006)
    box('Lower tread steel support', (x_center, front + run / 2, top - 0.105), (1.31, 0.22, 0.07), steel, 0.008)
    for x in (x_center - 0.55, x_center + 0.55):
        for dy in (0.075, 0.245):
            bpy.ops.mesh.primitive_cylinder_add(vertices=12, radius=0.012, depth=0.003, location=(x, front + dy, top + 0.001))
            bpy.context.object.name = 'Countersunk tread fixing'
            bpy.context.object.data.materials.append(metal)
for x in (x_center - 0.56, x_center + 0.56):
    beam('Lower flight steel stringer', (x, y_start - 0.06, 0.055), (x, 0.045, landing_z - 0.18), 0.095, 0.19, steel)
    box('Stringer floor anchor', (x, y_start, 0.025), (0.23, 0.24, 0.05), steel, 0.01)

# Intermediate landing: X [-1.65,-0.15], Y [0,1.5].
box('Landing structural tray', (-0.90, 0.75, landing_z - 0.13), (1.50, 1.50, 0.18), steel, 0.02)
for j in range(8):
    box('Landing oak board', (-0.90, (j + 0.5) * 1.50 / 8, landing_z - 0.035), (1.50, 1.50 / 8 - 0.008, 0.07), wood, 0.007)
for x in (-1.56, -0.24):
    for y in (0.10, 1.40):
        box('Landing support column', (x, y, (landing_z - 0.22) / 2), (0.11, 0.11, landing_z - 0.22), steel, 0.01)
        box('Landing base plate', (x, y, 0.025), (0.24, 0.24, 0.05), steel, 0.014)

# Upper flight, ascending in positive X.
x_start = -0.15
for i in range(count):
    front = x_start + i * run
    top = landing_z + (i + 1) * rise
    box('Upper flight oak tread %02d' % (i + 1), (front + run / 2 - 0.015, 0.75, top - 0.035), (run + 0.035, width, 0.07), wood, 0.014)
    box('Upper flight riser %02d' % (i + 1), (front + 0.012, 0.75, top - rise / 2 - 0.02), (0.035, width - 0.07, rise - 0.04), wood_dark, 0.006)
    box('Upper tread steel support', (front + run / 2, 0.75, top - 0.105), (0.22, 1.31, 0.07), steel, 0.008)
    for y in (0.20, 1.30):
        for dx in (0.075, 0.245):
            bpy.ops.mesh.primitive_cylinder_add(vertices=12, radius=0.012, depth=0.003, location=(front + dx, y, top + 0.001))
            bpy.context.object.name = 'Countersunk tread fixing'
            bpy.context.object.data.materials.append(metal)
end_x = x_start + count * run
for y in (0.19, 1.31):
    beam('Upper flight steel stringer', (x_start - 0.06, y, landing_z - 0.10), (end_x + 0.045, y, upper_z - 0.18), 0.095, 0.19, steel)
# Upper platform with visible supporting columns.
box('Upper platform tray', (end_x + 0.65, 0.75, upper_z - 0.13), (1.30, 1.50, 0.18), steel, 0.02)
for j in range(8):
    box('Upper platform board', (end_x + 0.65, (j + 0.5) * 1.5 / 8, upper_z - 0.035), (1.30, 1.5 / 8 - 0.008, 0.07), wood, 0.007)
for x in (end_x + 0.13, end_x + 1.17):
    for y in (0.12, 1.38):
        box('Upper platform support', (x, y, (upper_z - 0.22) / 2), (0.13, 0.13, upper_z - 0.22), steel, 0.012)
        box('Upper platform base plate', (x, y, 0.025), (0.28, 0.28, 0.05), steel, 0.012)
beam('Upper platform diagonal brace', (end_x + 0.13, 1.38, 0.4), (end_x + 1.17, 1.38, upper_z - 0.26), 0.055, 0.055, steel)

# Guardrail system, using vertical pickets and oak handrails.
rail_height = 0.96
def post(x, y, z):
    box('Guardrail mounting shoe', (x, y, z + 0.018), (0.12, 0.12, 0.035), metal, 0.01)
    box('Square guardrail post', (x, y, z + rail_height / 2), (0.052, 0.052, rail_height), steel, 0.006)

def handrail(a, b):
    beam('Oak handrail', a, b, 0.085, 0.07, wood)

for x in (-1.60, -0.20):
    # Rail slope follows the nosing line. Two pickets per tread.
    y0 = y_start + 0.04
    y1 = -0.04
    def lower_line(y):
        return rise + (y - y0) * rise / run
    for i in (0, 3, 6):
        y = y0 + i * run
        post(x, y, lower_line(y))
    for i in range(count):
        for offset in (0.11, 0.25):
            y = y_start + i * run + offset
            base = (i + 1) * rise
            rod('Lower flight vertical baluster', (x, y, base + 0.015), (x, y, lower_line(y) + rail_height - 0.045), 0.012, steel)
    handrail((x, y0 - 0.12, lower_line(y0 - 0.12) + rail_height), (x, y1, lower_line(y1) + rail_height))
    # Join the inclined handrail to the level landing rail height.
    handrail((x, y1, lower_line(y1) + rail_height), (x, 0.08, landing_z + rail_height))

for y in (0.05, 1.45):
    x0 = x_start + 0.04
    x1 = end_x - 0.04
    def upper_line(x):
        return landing_z + rise + (x - x0) * rise / run
    for i in (0, 3, 6):
        x = x0 + i * run
        post(x, y, upper_line(x))
    for i in range(count):
        for offset in (0.11, 0.25):
            x = x_start + i * run + offset
            base = landing_z + (i + 1) * rise
            rod('Upper flight vertical baluster', (x, y, base + 0.015), (x, y, upper_line(x) + rail_height - 0.045), 0.012, steel)
    handrail((x0, y, upper_line(x0) + rail_height), (x1, y, upper_line(x1) + rail_height))
    handrail((x1, y, upper_line(x1) + rail_height), (end_x + 0.08, y, upper_z + rail_height))
    handrail((x_start - 0.05, y, landing_z + rail_height), (x0, y, upper_line(x0) + rail_height))

def level_guard(a, b, z, spacing=0.13):
    av, bv = Vector(a), Vector(b)
    length = (bv - av).length
    post(av.x, av.y, z)
    post(bv.x, bv.y, z)
    handrail((av.x, av.y, z + rail_height), (bv.x, bv.y, z + rail_height))
    beam('Level guard lower rail', (av.x, av.y, z + 0.13), (bv.x, bv.y, z + 0.13), 0.035, 0.035, steel)
    n = max(2, math.ceil(length / spacing))
    for i in range(1, n):
        p = av.lerp(bv, i / n)
        rod('Landing vertical baluster', (p.x, p.y, z + 0.13), (p.x, p.y, z + rail_height - 0.04), 0.012, steel)

# Only exposed landing edges receive guards; both flight openings remain clear.
level_guard((-1.60, 0.08), (-1.60, 1.45), landing_z)
level_guard((-1.60, 1.45), (-0.20, 1.45), landing_z)
for y in (0.05, 1.45):
    level_guard((end_x + 0.08, y), (end_x + 1.25, y), upper_z)
level_guard((end_x + 1.25, 0.05), (end_x + 1.25, 1.45), upper_z)

scene = bpy.context.scene
scene.render.engine = 'CYCLES'
scene.world.use_nodes = True
scene.world.node_tree.nodes['Background'].inputs[0].default_value = (0.76, 0.81, 0.88, 1)
scene.world.node_tree.nodes['Background'].inputs[1].default_value = 0.45
for loc, energy, size in [((0, -4, 8), 1700, 6), ((4, 5, 6), 1300, 5)]:
    bpy.ops.object.light_add(type='AREA', location=loc)
    o = bpy.context.object
    o.data.energy = energy
    o.data.size = size
    o.rotation_euler = (Vector((0.4, 0, 1.5)) - o.location).to_track_quat('-Z', 'Y').to_euler()
bpy.ops.object.camera_add(location=(8, -11, 8))
camera = bpy.context.object
camera.rotation_euler = (Vector((0.6, -0.2, 1.8)) - camera.location).to_track_quat('-Z', 'Y').to_euler()
camera.data.type = 'ORTHO'
camera.data.ortho_scale = 8.7
scene.camera = camera
scene.render.resolution_x = 1400
scene.render.resolution_y = 1400
scene.render.resolution_percentage = 100
