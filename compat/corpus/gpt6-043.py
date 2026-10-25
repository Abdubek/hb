import bpy, math
from mathutils import Vector

bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)

def material(name, color, roughness=0.45, metallic=0):
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
        b = o.modifiers.new('Rounded manufactured edges', 'BEVEL')
        b.width = bevel
        b.segments = 3
        o.modifiers.new('Weighted normals', 'WEIGHTED_NORMAL')
    return o

def cylinder(name, loc, radius, depth, mat, rotation=None):
    bpy.ops.mesh.primitive_cylinder_add(vertices=48, radius=radius, depth=depth, location=loc)
    o = bpy.context.object
    o.name = name
    if rotation:
        o.rotation_euler = rotation
    o.data.materials.append(mat)
    b = o.modifiers.new('Edge radius', 'BEVEL')
    b.width = 0.006
    b.segments = 3
    o.modifiers.new('Weighted normals', 'WEIGHTED_NORMAL')
    return o

def tube(name, points, radius, mat):
    c = bpy.data.curves.new(name, 'CURVE')
    c.dimensions = '3D'
    c.resolution_u = 12
    c.bevel_depth = radius
    c.bevel_resolution = 4
    c.use_fill_caps = True
    s = c.splines.new('POLY')
    s.points.add(len(points) - 1)
    for p, co in zip(s.points, points):
        p.co = (*co, 1)
    o = bpy.data.objects.new(name, c)
    bpy.context.collection.objects.link(o)
    o.data.materials.append(mat)
    return o

paint = material('Deep teal powder coated steel', (0.035, 0.20, 0.20), 0.34, 0.50)
steel = material('Brushed stainless steel', (0.64, 0.69, 0.72), 0.24, 0.90)
dark = material('Drain slots and seams', (0.022, 0.03, 0.032), 0.7)
concrete = material('Warm concrete', (0.55, 0.53, 0.47), 0.82)
paving = material('Paving stones', (0.40, 0.43, 0.42), 0.8)
white = material('Sign lettering', (0.91, 0.94, 0.90))
water = material('Clear water stream', (0.55, 0.84, 0.95), 0.08)
p = water.node_tree.nodes.get('Principled BSDF')
p.inputs['Transmission Weight'].default_value = 0.85
p.inputs['IOR'].default_value = 1.333

box('Ground', (0, 0, -0.15), (200, 200, 0.20), concrete)
for i in range(9):
    for j in range(7):
        box('Plaza paver', ((i - 4) * 0.50, (j - 3) * 0.50, -0.025), (0.484, 0.484, 0.065), paving, 0.012)
box('Anchor plinth', (0, 0.10, 0.085), (0.76, 0.66, 0.16), concrete, 0.065)
box('Column foot flange', (0, 0.10, 0.18), (0.57, 0.48, 0.055), steel, 0.055)
box('Main fountain pedestal', (0, 0.10, 0.91), (0.43, 0.39, 1.43), paint, 0.085)
box('Top column cap', (0, 0.10, 1.64), (0.45, 0.41, 0.08), steel, 0.07)
for x in (-0.22, 0.22):
    for y in (-0.06, 0.26):
        cylinder('Anchor bolt', (x, y, 0.218), 0.027, 0.024, steel)
box('Service panel dark reveal', (0, -0.103, 0.69), (0.30, 0.012, 0.64), dark, 0.025)
box('Service access panel', (0, -0.114, 0.69), (0.28, 0.013, 0.62), paint, 0.022)
for x in (-0.112, 0.112):
    for z in (0.43, 0.95):
        cylinder('Panel screw', (x, -0.124, z), 0.010, 0.007, steel, (math.pi / 2, 0, 0))

# Closed revolved bowl cross-section: underside, rolled lip, concave interior, drain hole.
def basin(name, cx, cy, z):
    profile = [(0.055, -0.18), (0.16, -0.18), (0.29, -0.145), (0.39, -0.075), (0.445, 0.005), (0.446, 0.026), (0.437, 0.041), (0.420, 0.044), (0.407, 0.033), (0.391, 0.0), (0.34, -0.057), (0.26, -0.107), (0.16, -0.134), (0.055, -0.139)]
    segments = 96
    verts = []
    for r, dz in profile:
        for i in range(segments):
            a = i * 2 * math.pi / segments
            verts.append((cx + r * math.cos(a), cy + r * 0.83 * math.sin(a), z + dz))
    faces = []
    for j in range(len(profile)):
        nxt = (j + 1) % len(profile)
        for i in range(segments):
            k = (i + 1) % segments
            faces.append((j * segments + i, j * segments + k, nxt * segments + k, nxt * segments + i))
    mesh = bpy.data.meshes.new(name)
    mesh.from_pydata(verts, [], faces)
    mesh.update()
    o = bpy.data.objects.new(name, mesh)
    bpy.context.collection.objects.link(o)
    o.data.materials.append(steel)
    for poly in mesh.polygons:
        poly.use_smooth = True
    cylinder('Drain dark recess', (cx, cy, z - 0.146), 0.052, 0.025, dark)
    cylinder('Drain strainer', (cx, cy, z - 0.132), 0.046, 0.011, steel)
    for i in range(8):
        a = i * math.pi / 4
        cylinder('Drain perforation', (cx + 0.028 * math.cos(a), cy + 0.028 * math.sin(a), z - 0.1258), 0.006, 0.0015, dark)
    cylinder('Drain center hole', (cx, cy, z - 0.1258), 0.007, 0.0015, dark)

for cx, z in ((-0.67, 1.32), (0.67, 0.97)):
    cy = -0.08
    box('Cantilever support arm', (cx / 2, 0.075, z - 0.215), (abs(cx) + 0.18, 0.22, 0.16), paint, 0.055)
    cylinder('Bowl underside collar', (cx, cy, z - 0.195), 0.13, 0.105, paint)
    basin('High basin' if cx < 0 else 'Low accessible basin', cx, cy, z)
    # Valve is positioned on the rear rim and directs water into the bowl.
    fy = cy + 0.25
    cylinder('Bubbler mounting boss', (cx, fy, z + 0.035), 0.073, 0.06, steel)
    tube('Curved bubbler faucet', [(cx, fy, z + 0.055), (cx, fy, z + 0.13), (cx, fy - 0.025, z + 0.17), (cx, fy - 0.07, z + 0.18)], 0.031, steel)
    cylinder('Bubbler nozzle aperture', (cx, fy - 0.072, z + 0.188), 0.014, 0.014, dark)
    # Protective side lobes around the bubbler head.
    for dx in (-0.048, 0.048):
        tube('Bubbler sanitary guard', [(cx + dx, fy, z + 0.05), (cx + dx, fy - 0.005, z + 0.15), (cx + dx, fy - 0.065, z + 0.20)], 0.013, steel)
    box('Push button housing', (cx, cy - 0.307, z - 0.07), (0.19, 0.09, 0.105), paint, 0.035)
    cylinder('Round push button', (cx, cy - 0.36, z - 0.065), 0.037, 0.019, steel, (math.pi / 2, 0, 0))
    if cx < 0:
        points = []
        for i in range(41):
            t = i / 40
            points.append((cx, fy - 0.072 - 0.23 * t, z + 0.198 + 0.58 * t - 0.905 * t * t))
        tube('Arching drinking water stream', points, 0.008, water)
        for r in (0.060, 0.087):
            bpy.ops.mesh.primitive_torus_add(major_radius=r, minor_radius=0.003, major_segments=48, minor_segments=8, location=(cx, cy - 0.025, z - 0.126))
            bpy.context.object.name = 'Small splash ripple'
            bpy.context.object.scale.y = 0.7
            bpy.context.object.data.materials.append(water)

box('Water sign plaque', (0, -0.112, 1.48), (0.32, 0.025, 0.19), paint, 0.02)
bpy.ops.object.text_add(location=(0, -0.13, 1.48), rotation=(math.pi / 2, 0, 0))
t = bpy.context.object
t.name = 'Drinking water label'
t.data.body = 'WATER'
t.data.align_x = 'CENTER'
t.data.align_y = 'CENTER'
t.data.size = 0.064
t.data.extrude = 0.001
t.data.materials.append(white)

scene = bpy.context.scene
scene.render.engine = 'CYCLES'
scene.world.use_nodes = True
scene.world.node_tree.nodes['Background'].inputs[0].default_value = (0.72, 0.79, 0.85, 1)
scene.world.node_tree.nodes['Background'].inputs[1].default_value = 0.4
for loc, energy, size in [((1, -3, 5), 650, 4), ((-3, 1, 3), 450, 3)]:
    bpy.ops.object.light_add(type='AREA', location=loc)
    o = bpy.context.object
    o.data.energy = energy
    o.data.size = size
    o.rotation_euler = (Vector((0, 0, 0.8)) - o.location).to_track_quat('-Z', 'Y').to_euler()
bpy.ops.object.camera_add(location=(3.1, -4.5, 3.0))
camera = bpy.context.object
camera.rotation_euler = (Vector((0, -0.03, 0.88)) - camera.location).to_track_quat('-Z', 'Y').to_euler()
camera.data.type = 'ORTHO'
camera.data.ortho_scale = 3.5
scene.camera = camera
scene.render.resolution_x = 1400
scene.render.resolution_y = 1400
scene.render.resolution_percentage = 100
