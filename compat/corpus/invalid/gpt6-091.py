import bpy, math
from mathutils import Vector

bpy.ops.wm.read_factory_settings(use_empty=True)

def material(name, color, metallic=0.0, roughness=0.5):
    m = bpy.data.materials.new(name)
    m.diffuse_color = (*color, 1)
    m.use_nodes = True
    p = m.node_tree.nodes.get('Principled BSDF')
    p.inputs['Base Color'].default_value = (*color, 1)
    p.inputs['Metallic'].default_value = metallic
    p.inputs['Roughness'].default_value = roughness
    return m

def box(name, loc, scale, mat, bevel=0.03):
    bpy.ops.mesh.primitive_cube_add(size=1, location=loc)
    o = bpy.context.object
    o.name = name
    o.dimensions = scale
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    o.data.materials.append(mat)
    if bevel:
        b = o.modifiers.new('Soft edges', 'BEVEL')
        b.width = bevel
        b.segments = 3
        o.modifiers.new('Weighted normals', 'WEIGHTED_NORMAL')
    return o

def cylinder(name, loc, radius, depth, mat):
    bpy.ops.mesh.primitive_cylinder_add(vertices=32, radius=radius, depth=depth, location=loc)
    o = bpy.context.object
    o.name = name
    o.data.materials.append(mat)
    b = o.modifiers.new('Edge rounding', 'BEVEL')
    b.width = 0.012
    b.segments = 2
    o.modifiers.new('Weighted normals', 'WEIGHTED_NORMAL')
    return o

def label(body, loc, size, mat):
    bpy.ops.object.text_add(location=loc, rotation=(math.pi / 2, 0, 0))
    o = bpy.context.object
    o.name = 'Seat number ' + body
    o.data.body = body
    o.data.align_x = 'CENTER'
    o.data.align_y = 'CENTER'
    o.data.size = size
    o.data.extrude = 0.001
    o.data.materials.append(mat)

velvet = material('Burgundy upholstery', (0.32, 0.012, 0.035), roughness=0.86)
piping = material('Upholstery piping', (0.12, 0.004, 0.013), roughness=0.7)
steel = material('Black powder coated steel', (0.022, 0.027, 0.035), 0.65, 0.3)
plastic = material('Armrest polymer', (0.013, 0.017, 0.024), roughness=0.4)
carpet = material('Charcoal carpet', (0.055, 0.066, 0.082), roughness=0.97)
brass = material('Warm brass', (0.72, 0.45, 0.14), 0.75, 0.3)
ground = material('Surrounding floor', (0.12, 0.14, 0.17), roughness=0.8)
lightstrip = material('Amber aisle lighting', (0.9, 0.29, 0.035))
p = lightstrip.node_tree.nodes.get('Principled BSDF')
p.inputs['Emission Color'].default_value = (1, 0.24, 0.025, 1)
p.inputs['Emission Strength'].default_value = 3

box('Floor', (0, 0, -0.09), (16, 13, 0.18), ground)
box('Lower step', (0, -0.35, 0.10), (7.8, 3.6, 0.20), carpet)
box('Middle step', (0, -0.10, 0.30), (7.8, 3.1, 0.20), carpet)
box('Seating platform', (0, 0.15, 0.50), (7.8, 2.6, 0.20), carpet)
for y, z in [(-2.13, 0.18), (-1.63, 0.38), (-1.13, 0.58)]:
    box('Brass step nosing', (0, y, z), (7.68, 0.035, 0.022), brass, 0.006)
    for x in [-3.45, 3.45]:
        box('Recessed aisle marker', (x, y - 0.015, z - 0.075), (0.25, 0.014, 0.04), lightstrip, 0.006)

for i in range(6):
    x = (i - 2.5) * 1.12
    box('Seat mounting plate', (x, 0.3, 0.625), (0.62, 0.6, 0.05), steel)
    for dx in [-0.23, 0.23]:
        box('Pedestal leg', (x + dx, 0.30, 0.87), (0.065, 0.31, 0.47), steel, 0.015)
        for dy in [-0.22, 0.22]:
            cylinder('Anchor bolt', (x + dx, 0.30 + dy, 0.66), 0.025, 0.018, brass)
    box('Seat pan', (x, 0.14, 1.085), (0.90, 0.79, 0.12), steel, 0.07)
    box('Cushion piping', (x, 0.11, 1.16), (0.88, 0.78, 0.16), piping, 0.075)
    box('Seat cushion', (x, 0.10, 1.195), (0.85, 0.76, 0.17), velvet, 0.08)
    back = box('Rear seat shell', (x, 0.64, 1.69), (0.96, 0.19, 1.23), steel, 0.10)
    back.rotation_euler.x = math.radians(9)
    trim = box('Backrest piping', (x, 0.515, 1.71), (0.90, 0.22, 1.15), piping, 0.105)
    trim.rotation_euler.x = math.radians(9)
    back = box('Padded backrest', (x, 0.49, 1.72), (0.86, 0.23, 1.10), velvet, 0.10)
    back.rotation_euler.x = math.radians(9)
    head = box('Headrest', (x, 0.37, 2.04), (0.67, 0.11, 0.28), velvet, 0.055)
    head.rotation_euler.x = math.radians(9)
    label(str(i + 1).zfill(2), (x, -0.302, 1.08), 0.08, brass)

for i in range(7):
    x = (i - 3) * 1.12
    box('Arm support', (x, 0.22, 1.13), (0.08, 0.12, 0.94), steel, 0.02)
    box('Shared armrest', (x, 0.15, 1.54), (0.19, 0.77, 0.12), plastic, 0.055)
    cylinder('Cup holder dark well', (x, -0.12, 1.607), 0.069, 0.012, steel)
    bpy.ops.mesh.primitive_torus_add(major_radius=0.070, minor_radius=0.009, major_segments=32, minor_segments=10, location=(x, -0.12, 1.618))
    bpy.context.object.name = 'Cup holder rim'
    bpy.context.object.data.materials.append(plastic)

scene = bpy.context.scene
scene.world.color = (0.14, 0.14, 0.14)
for loc, energy, size in [((1, -5, 8), 1700, 7), ((-5, 1, 5), 1100, 5), ((4, 4, 6), 1500, 4)]:
    bpy.ops.object.light_add(type='AREA', location=loc)
    o = bpy.context.object
    o.data.energy = energy
    o.data.shape = 'DISK'
    o.data.size = size
    o.rotation_euler = (Vector((0, 0, 1)) - o.location).to_track_quat('-Z', 'Y').to_euler()
bpy.ops.object.camera_add(location=(8.4, -11, 7.0))
camera = bpy.context.object
camera.rotation_euler = (Vector((0, -0.15, 1.0)) - camera.location).to_track_quat('-Z', 'Y').to_euler()
camera.data.type = 'ORTHO'
camera.data.ortho_scale = 10.7
scene.camera = camera
scene.render.engine = 'CYCLES'
scene.render.resolution_x = 1500
scene.render.resolution_y = 1000
scene.render.resolution_percentage = 100
