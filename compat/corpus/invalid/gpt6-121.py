import bpy, math
from mathutils import Vector
bpy.ops.wm.read_factory_settings(use_empty=True)

def mat(name, color, metallic=0.0, roughness=0.4, emission=0.0):
    m = bpy.data.materials.new(name)
    m.diffuse_color = (*color, 1)
    m.use_nodes = True
    p = m.node_tree.nodes.get('Principled BSDF')
    p.inputs['Base Color'].default_value = (*color, 1)
    p.inputs['Metallic'].default_value = metallic
    p.inputs['Roughness'].default_value = roughness
    if emission:
        p.inputs['Emission Color'].default_value = (*color, 1)
        p.inputs['Emission Strength'].default_value = emission
    return m

def finish(o, name, material, bevel=0.0):
    o.name = name
    o.data.materials.append(material)
    if bevel:
        m = o.modifiers.new('Machined edge radii', 'BEVEL')
        m.width = bevel
        m.segments = 3
        o.modifiers.new('Weighted corner normals', 'WEIGHTED_NORMAL')
    return o

def box(name, loc, size, material, bevel=0.025):
    bpy.ops.mesh.primitive_cube_add(size=1, location=loc)
    o = bpy.context.object
    o.dimensions = size
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    return finish(o, name, material, bevel)

def cyl(name, a, b, radius, material, vertices=32):
    a, b = Vector(a), Vector(b)
    bpy.ops.mesh.primitive_cylinder_add(vertices=vertices, radius=radius, depth=(b-a).length, location=(a+b)/2)
    o = bpy.context.object
    o.rotation_quaternion = (b-a).to_track_quat('Z', 'Y')
    o.rotation_mode = 'QUATERNION'
    finish(o, name, material, 0.012)
    for p in o.data.polygons:
        p.use_smooth = len(p.vertices) == 4
    return o

def pipe(name, points, radius, material):
    c = bpy.data.curves.new(name, 'CURVE')
    c.dimensions = '3D'
    c.bevel_depth = radius
    c.bevel_resolution = 3
    s = c.splines.new('POLY')
    s.points.add(len(points)-1)
    for p, co in zip(s.points, points):
        p.co = (*co, 1)
    o = bpy.data.objects.new(name, c)
    bpy.context.collection.objects.link(o)
    o.data.materials.append(material)
    return o

def label(body, loc, size, material):
    c = bpy.data.curves.new('Stencil '+body, 'FONT')
    c.body = body
    c.size = size
    c.align_x = 'CENTER'
    c.extrude = 0.001
    o = bpy.data.objects.new('Stencil '+body, c)
    bpy.context.collection.objects.link(o)
    o.location = loc
    o.rotation_euler = (math.pi/2, 0, 0)
    o.data.materials.append(material)

def light(name, loc, energy, color, size, target):
    d = bpy.data.lights.new(name, 'AREA')
    d.energy, d.color, d.shape, d.size = energy, color, 'DISK', size
    o = bpy.data.objects.new(name, d)
    bpy.context.collection.objects.link(o)
    o.location = loc
    o.rotation_euler = (Vector(target)-o.location).to_track_quat('-Z', 'Y').to_euler()

steel = mat('Blue grey armor', (0.16, 0.24, 0.29), 0.75)
dark = mat('Graphite seals', (0.018, 0.027, 0.035), 0.3)
trim = mat('Brushed titanium', (0.47, 0.55, 0.58), 0.85, 0.28)
orange = mat('Safety ochre', (0.95, 0.38, 0.045), 0.35)
white = mat('Stencil ivory', (0.8, 0.88, 0.87))
red = mat('Red warning lenses', (1.0, 0.025, 0.008), 0.15, 0.24, 5)
cyan = mat('Interface cyan', (0.015, 0.72, 1.0), 0.1, 0.25, 3)
ground = mat('Deck concrete', (0.055, 0.07, 0.08), 0.15, 0.8)

box('Display deck', (0, -0.5, -0.18), (10, 7, 0.36), ground, 0.1)
box('Rear pressure bulkhead', (0, 0.8, 3.05), (8.4, 0.5, 6.1), dark, 0.08)
for side in (-1, 1):
    box('Outer wall armor', (side*3.28, 0.36, 3), (1.65, 0.45, 5.95), steel, 0.08)
    for z in (0.65, 2.1, 3.55, 5.0):
        box('Wall inset tile', (side*3.28, 0.1, z), (1.35, 0.09, 1.17), trim, 0.04)
        for x in (side*3.28-0.53, side*3.28+0.53):
            for dz in (-0.45, 0.45):
                cyl('Wall captive screw', (x, 0.025, z+dz), (x, -0.015, z+dz), 0.038, dark, 12)
    box('Door frame upright', (side*2.24, -0.02, 2.82), (0.48, 0.94, 5.62), trim, 0.08)
    box('Frame black reveal', (side*1.98, -0.31, 2.8), (0.08, 0.22, 4.96), dark, 0.012)
    box('Sliding pressure leaf', (side*0.99, 0, 2.79), (1.94, 0.42, 4.93), steel, 0.06)
    box('Inset leaf armor', (side*1.0, -0.24, 3.05), (1.62, 0.12, 3.66), dark, 0.06)
    for z, height in ((1.8, 1.0), (3.07, 1.36), (4.32, 0.8)):
        box('Floating door panel', (side*1.0, -0.32, z), (1.47, 0.12, height), steel, 0.055)
    box('Lock spine', (side*0.17, -0.43, 2.8), (0.16, 0.13, 3.8), trim, 0.025)
    for z in (0.76, 4.88):
        box('Leaf hazard band', (side*1.0, -0.29, z), (1.7, 0.1, 0.2), orange)
    for z in (1.25, 2.8, 4.4):
        box('Frame clamp', (side*2.27, -0.56, z), (0.62, 0.25, 0.3), dark)
        cyl('Clamp pin', (side*2.27, -0.72, z), (side*2.27, -0.77, z), 0.095, trim)
    for i in range(3):
        x = side*(2.82+i*0.25)
        pts = [(x, -0.2, 0.35), (x, -0.2, 4.65-i*0.2), (x+side*0.2, -0.2, 4.86-i*0.2), (side*3.82, -0.2, 4.86-i*0.2), (side*3.82, -0.2, 5.65)]
        pipe('Exposed service conduit', pts, 0.055, trim if i != 1 else orange)
        for z in (1.0, 2.7, 4.1):
            box('Conduit saddle', (x, -0.22, z), (0.17, 0.17, 0.09), dark, 0.012)
    box('Warning beacon mount', (side*2.23, -0.65, 5.17), (0.38, 0.26, 0.46), dark)
    cyl('Red warning lamp', (side*2.23, -0.8, 5.17), (side*2.23, -0.96, 5.17), 0.135, red)
box('Upper armored lintel', (0, -0.02, 5.58), (4.97, 0.94, 0.58), trim, 0.08)
box('Lintel sign backing', (0, -0.51, 5.59), (3.7, 0.07, 0.37), dark)
label('AIRLOCK  //  07', (0, -0.558, 5.47), 0.25, white)
box('Raised threshold', (0, -0.3, 0.18), (4.9, 1.3, 0.36), trim, 0.06)
for x in [i*0.24 for i in range(-8, 9)]:
    box('Threshold grip grooves', (x, -0.51, 0.369), (0.1, 0.78, 0.015), dark, 0.003)
box('Control pedestal', (2.85, -0.48, 2.45), (0.56, 0.31, 0.96), dark, 0.05)
box('Control screen', (2.85, -0.65, 2.61), (0.42, 0.028, 0.39), cyan, 0.015)
for x in (2.7, 2.85, 3.0):
    cyl('Control button', (x, -0.65, 2.19), (x, -0.69, 2.19), 0.04, orange, 16)
label('PRESSURE SEAL', (-1.02, -0.392, 3.1), 0.12, white)
label('07', (1.02, -0.392, 3.0), 0.54, white)
for side in (-1, 1):
    box('Floor approach stripe', (side*2.3, -2.0, 0.012), (0.12, 2.15, 0.018), orange, 0)
for i in range(13):
    o = box('Threshold hazard slash', (-2.1+i*0.35, -1.06, 0.021), (0.17, 0.37, 0.024), orange, 0)
    o.rotation_euler.z = -0.45
light('Large cool key', (1, -7, 9), 1800, (0.72, 0.84, 1), 6, (0, 0, 2.5))
light('Warm side fill', (-6, -2, 5), 1200, (1, 0.52, 0.26), 4, (0, 0, 3))
light('Top rim', (3, 3, 8), 1700, (0.35, 0.68, 1), 4, (0, 0, 3))
bpy.ops.object.camera_add(location=(9, -14, 8))
cam = bpy.context.object
cam.rotation_euler = (Vector((0, 0, 2.65))-cam.location).to_track_quat('-Z', 'Y').to_euler()
cam.data.type = 'ORTHO'
cam.data.ortho_scale = 12.2
scene = bpy.context.scene
scene.camera = cam
scene.world.color = (0.12, 0.12, 0.12)
scene.render.engine = 'CYCLES'
scene.render.resolution_x, scene.render.resolution_y = 1400, 1100
scene.render.resolution_percentage = 100
scene.view_settings.view_transform = 'AgX'
