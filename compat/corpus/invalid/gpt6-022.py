import bpy, math
from mathutils import Vector

bpy.ops.wm.read_factory_settings(use_empty=True)

def mat(name, color, metal=0, rough=0.4):
    m = bpy.data.materials.new(name)
    m.diffuse_color = (*color, 1)
    m.use_nodes = True
    p = m.node_tree.nodes.get('Principled BSDF')
    p.inputs['Base Color'].default_value = (*color, 1)
    p.inputs['Metallic'].default_value = metal
    p.inputs['Roughness'].default_value = rough
    return m

enamel = mat('Forest green enamel', (0.025, 0.105, 0.075), 0.65, 0.28)
steel = mat('Dark steel', (0.055, 0.065, 0.06), 0.85, 0.3)
brass = mat('Aged brass', (0.42, 0.24, 0.065), 0.8, 0.3)
rubber = mat('Black rubber', (0.018, 0.021, 0.018), 0, 0.85)
wick = mat('Charred wick', (0.045, 0.025, 0.013), 0, 1)
ground = mat('Warm studio floor', (0.20, 0.18, 0.145), 0, 0.9)
glass = mat('Clear chimney glass', (0.92, 0.97, 0.94), 0, 0.08)
p = glass.node_tree.nodes.get('Principled BSDF')
p.inputs['Transmission Weight'].default_value = 1
p.inputs['IOR'].default_value = 1.46
flame = mat('Warm glowing mantle', (1, 0.57, 0.16))
p = flame.node_tree.nodes.get('Principled BSDF')
p.inputs['Emission Color'].default_value = (1, 0.39, 0.055, 1)
p.inputs['Emission Strength'].default_value = 5

def finish(o, name, material, bevel=0):
    o.name = name
    o.data.materials.append(material)
    for f in o.data.polygons:
        f.use_smooth = True
    if bevel:
        m = o.modifiers.new('Rounded manufactured edges', 'BEVEL')
        m.width = bevel
        m.segments = 3
        o.modifiers.new('Weighted normals', 'WEIGHTED_NORMAL')
    return o

def cyl(name, loc, radius, depth, material, vertices=64):
    bpy.ops.mesh.primitive_cylinder_add(vertices=vertices, radius=radius, depth=depth, location=loc)
    return finish(bpy.context.object, name, material, 0.012)

def torus(name, z, radius, thickness, material):
    bpy.ops.mesh.primitive_torus_add(major_radius=radius, minor_radius=thickness, major_segments=64, minor_segments=12, location=(0, 0, z))
    return finish(bpy.context.object, name, material)

def lathe(name, profile, material, segments=64, thickness=0):
    vertices = [(r*math.cos(2*math.pi*i/segments), r*math.sin(2*math.pi*i/segments), z) for r, z in profile for i in range(segments)]
    faces = []
    for j in range(len(profile)-1):
        for i in range(segments):
            a = j*segments+i
            b = j*segments+(i+1)%segments
            faces.append((a, b, b+segments, a+segments))
    mesh = bpy.data.meshes.new(name)
    mesh.from_pydata(vertices, [], faces)
    mesh.update()
    o = bpy.data.objects.new(name, mesh)
    bpy.context.collection.objects.link(o)
    finish(o, name, material)
    if thickness:
        s = o.modifiers.new('Wall thickness', 'SOLIDIFY')
        s.thickness = thickness
        s.offset = -1
    return o

def tube(name, points, radius, material):
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

cyl('Rubber base pad', (0, 0, 0.075), 0.55, 0.10, rubber)
lathe('Pressed fuel reservoir', [(0.01, 0.10), (0.52, 0.10), (0.57, 0.15), (0.57, 0.28), (0.53, 0.40), (0.43, 0.46), (0.20, 0.48), (0.01, 0.48)], enamel, thickness=0.025)
torus('Reservoir rolled seam', 0.17, 0.565, 0.025, steel)
cyl('Brass burner assembly', (0, 0, 0.54), 0.24, 0.14, brass)
cyl('Wick holder', (0, 0, 0.635), 0.095, 0.075, steel)
cyl('Wick', (0, 0, 0.69), 0.06, 0.045, wick)
for i in range(16):
    a = i*2*math.pi/16
    cyl('Burner ventilation recess', (0.185*math.cos(a), 0.185*math.sin(a), 0.615), 0.022, 0.012, rubber, 12)

lathe('Bulbous glass chimney', [(0.285, 0.59), (0.35, 0.65), (0.40, 0.81), (0.405, 1.03), (0.37, 1.23), (0.285, 1.47), (0.28, 1.64)], glass, thickness=0.012)
torus('Lower glass retaining ring', 0.625, 0.315, 0.035, brass)
torus('Upper glass retaining ring', 1.61, 0.287, 0.027, brass)
# A small luminous flame inside the transparent globe.
lathe('Flame', [(0.008, 0.70), (0.065, 0.74), (0.082, 0.82), (0.062, 0.91), (0.031, 1.02), (0.003, 1.12)], flame, 40)

# Four bowed guards and two encircling protection hoops.
for i in range(4):
    a = math.pi/4+i*math.pi/2
    profile = [(0.42, 0.40), (0.49, 0.52), (0.52, 0.80), (0.52, 1.22), (0.46, 1.55), (0.34, 1.75)]
    tube('Protective frame upright', [(r*math.cos(a), r*math.sin(a), z) for r, z in profile], 0.036, steel)
torus('Lower protective hoop', 0.77, 0.515, 0.024, steel)
torus('Upper protective hoop', 1.31, 0.５０ if False else 0.50, 0.024, steel)

cyl('Ventilator dark interior', (0, 0, 1.75), 0.265, 0.24, steel)
for i in range(12):
    a = 2*math.pi*i/12
    tube('Ventilator vertical bridge', [(0.285*math.cos(a), 0.285*math.sin(a), 1.66), (0.285*math.cos(a), 0.285*math.sin(a), 1.88)], 0.022, enamel)
lathe('Broad enamel rain hood', [(0.45, 1.62), (0.47, 1.66), (0.40, 1.73), (0.32, 1.77)], enamel, thickness=0.025)
lathe('Upper ventilator cap', [(0.35, 1.86), (0.36, 1.90), (0.27, 1.99), (0.11, 2.045), (0.01, 2.045)], enamel, thickness=0.025)
torus('Hood rolled lip', 1.655, 0.455, 0.022, steel)
cyl('Top finial', (0, 0, 2.075), 0.085, 0.075, brass)

for x in (-0.49, 0.49):
    o = cyl('Handle pivot boss', (x, 0, 1.64), 0.085, 0.09, brass, 32)
    o.rotation_euler[1] = math.pi/2
# Raised bail in the XZ plane, joined to the two pivot bosses.
points = [(-0.51, 0, 1.64), (-0.62, 0, 1.87), (-0.65, 0, 2.26)]
points += [(0.65*math.cos(t), 0, 2.26+0.65*math.sin(t)) for t in [math.pi-i*math.pi/48 for i in range(49)]]
points += [(0.62, 0, 1.87), (0.51, 0, 1.64)]
tube('Arched carrying handle', points, 0.029, steel)
tube('Leather grip on bail', [(0.65*math.cos(t), 0, 2.26+0.65*math.sin(t)) for t in [1.18+i*0.78/24 for i in range(25)]], 0.053, rubber)
cap = cyl('Fuel filler cap', (0.35, -0.16, 0.465), 0.115, 0.08, brass, 40)
for i in range(20):
    a = 2*math.pi*i/20
    cyl('Cap knurl', (0.35+0.11*math.cos(a), -0.16+0.11*math.sin(a), 0.47), 0.012, 0.055, brass, 8)
knob = cyl('Wick adjustment wheel', (0, -0.39, 0.54), 0.085, 0.06, brass, 24)
knob.rotation_euler[0] = math.pi/2
tube('Adjustment shaft', [(0, -0.18, 0.54), (0, -0.39, 0.54)], 0.024, steel)

bpy.ops.mesh.primitive_plane_add(size=200)
bpy.context.object.data.materials.append(ground)
world = bpy.data.worlds.new('Studio environment')
world.use_nodes = True
world.node_tree.nodes['Background'].inputs[1].default_value = 0.22
bpy.context.scene.world = world
for name, loc, power, size, color in [('Large softbox', (3, -4, 5), 500, 3, (1, 0.84, 0.67)), ('Glass rim light', (-2, 2, 4), 650, 2.5, (0.67, 0.81, 1)), ('Front fill', (-3, -2, 2), 180, 2, (1, 1, 1))]:
    bpy.ops.object.light_add(type='AREA', location=loc)
    o = bpy.context.object
    o.name = name
    o.data.energy = power
    o.data.size = size
    o.data.color = color
    o.rotation_euler = (Vector((0, 0, 1.3))-o.location).to_track_quat('-Z', 'Y').to_euler()
bpy.ops.object.light_add(type='POINT', location=(0, 0, 0.9))
bpy.context.object.data.energy = 8
bpy.context.object.data.color = (1, 0.38, 0.08)
bpy.context.object.data.shadow_soft_size = 0.08
bpy.ops.object.camera_add(location=(4, -6, 3.6))
camera = bpy.context.object
camera.rotation_euler = (Vector((0, 0, 1.42))-camera.location).to_track_quat('-Z', 'Y').to_euler()
camera.data.type = 'ORTHO'
camera.data.ortho_scale = 3.8
scene = bpy.context.scene
scene.camera = camera
scene.render.engine = 'CYCLES'
scene.cycles.max_bounces = 12
scene.cycles.transmission_bounces = 8
scene.render.resolution_x = 1100
scene.render.resolution_y = 1400
scene.render.resolution_percentage = 100
