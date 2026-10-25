import bpy, math, random
from mathutils import Vector

bpy.ops.wm.read_factory_settings(use_empty=True)
random.seed(12)

def mat(name, color, metallic=0, roughness=0.5):
    m = bpy.data.materials.new(name)
    m.diffuse_color = (*color, 1)
    m.use_nodes = True
    p = m.node_tree.nodes.get('Principled BSDF')
    p.inputs['Base Color'].default_value = (*color, 1)
    p.inputs['Metallic'].default_value = metallic
    p.inputs['Roughness'].default_value = roughness
    return m

def box(name, loc, size, material, bevel=0.025):
    bpy.ops.mesh.primitive_cube_add(size=1, location=loc)
    o = bpy.context.object
    o.name = name
    o.dimensions = size
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    o.data.materials.append(material)
    if bevel:
        b = o.modifiers.new('Rounded edges', 'BEVEL')
        b.width = bevel
        b.segments = 4
        o.modifiers.new('Weighted normals', 'WEIGHTED_NORMAL')
    return o

def cylinder(name, loc, radius, depth, material, vertices=48, bevel=0.012):
    bpy.ops.mesh.primitive_cylinder_add(vertices=vertices, radius=radius, depth=depth, location=loc)
    o = bpy.context.object
    o.name = name
    o.data.materials.append(material)
    for p in o.data.polygons:
        p.use_smooth = len(p.vertices) == 4
    if bevel:
        b = o.modifiers.new('Edge bevel', 'BEVEL')
        b.width = bevel
        b.segments = 3
        o.modifiers.new('Weighted normals', 'WEIGHTED_NORMAL')
    return o

def rod(name, a, b, radius, material, vertices=24):
    a, b = Vector(a), Vector(b)
    o = cylinder(name, (a+b)/2, radius, (b-a).length, material, vertices, 0.004)
    o.rotation_euler = (b-a).to_track_quat('Z', 'Y').to_euler()
    return o

def cup(name, x, y, bottom, radius, height, material):
    n = 72
    # Closed cross-section creates floor, exterior, lip and interior cavity.
    profile = [(0, bottom), (radius-0.025, bottom), (radius, bottom+0.025),
               (radius, bottom+height-0.025), (radius-0.015, bottom+height),
               (radius-0.085, bottom+height), (radius-0.1, bottom+height-0.025),
               (radius-0.1, bottom+0.12), (0, bottom+0.12)]
    verts, rings, faces = [], [], []
    for r, z in profile:
        if r == 0:
            rings.append([len(verts)])
            verts.append((x, y, z))
        else:
            ring = []
            for j in range(n):
                a = j*2*math.pi/n
                ring.append(len(verts))
                verts.append((x+r*math.cos(a), y+r*math.sin(a), z))
            rings.append(ring)
    for a, b in zip(rings[:-1], rings[1:]):
        for j in range(n):
            k = (j+1)%n
            if len(a) == 1:
                faces.append((a[0], b[k], b[j]))
            elif len(b) == 1:
                faces.append((a[j], a[k], b[0]))
            else:
                faces.append((a[j], a[k], b[k], b[j]))
    mesh = bpy.data.meshes.new(name)
    mesh.from_pydata(verts, [], faces)
    mesh.update()
    o = bpy.data.objects.new(name, mesh)
    bpy.context.collection.objects.link(o)
    o.data.materials.append(material)
    for p in mesh.polygons:
        p.use_smooth = abs(p.normal.z) < 0.95
    return o

walnut = mat('Oiled walnut', (0.28, 0.13, 0.055), 0, 0.4)
# Procedural elongated grain uses no image assets.
nt = walnut.node_tree
tex = nt.nodes.new('ShaderNodeTexNoise')
tex.inputs['Scale'].default_value = 4
tex.inputs['Detail'].default_value = 3
coord = nt.nodes.new('ShaderNodeTexCoord')
mapping = nt.nodes.new('ShaderNodeVectorMath')
mapping.operation = 'MULTIPLY'
mapping.inputs[1].default_value = (1.2, 32, 8)
nt.links.new(coord.outputs['Generated'], mapping.inputs[0])
nt.links.new(mapping.outputs['Vector'], tex.inputs['Vector'])
ramp = nt.nodes.new('ShaderNodeValToRGB')
ramp.color_ramp.elements[0].position = 0.2
ramp.color_ramp.elements[0].color = (0.095, 0.036, 0.012, 1)
ramp.color_ramp.elements[1].position = 0.8
ramp.color_ramp.elements[1].color = (0.38, 0.2, 0.085, 1)
nt.links.new(tex.outputs['Fac'], ramp.inputs[0])
nt.links.new(ramp.outputs['Color'], nt.nodes.get('Principled BSDF').inputs['Base Color'])
teal = mat('Muted teal powder coat', (0.08, 0.25, 0.26), 0.25, 0.46)
brass = mat('Brass accents', (0.58, 0.39, 0.15), 0.8, 0.28)
felt = mat('Charcoal felt', (0.045, 0.055, 0.053), 0, 0.96)
paper = mat('Warm white paper', (0.88, 0.86, 0.78), 0, 0.83)
blue = mat('Blue stationery', (0.035, 0.1, 0.22), 0.1, 0.33)
yellow = mat('Yellow pencil lacquer', (0.82, 0.48, 0.065), 0, 0.42)
pencilwood = mat('Exposed pencil wood', (0.64, 0.4, 0.18), 0, 0.72)
graphite = mat('Graphite', (0.03, 0.032, 0.035), 0.2, 0.36)
eraser = mat('Pencil eraser', (0.62, 0.27, 0.22), 0, 0.75)
desk = mat('Warm gray desktop', (0.42, 0.43, 0.4), 0, 0.75)

box('Walnut organizer base', (0, 0, 0.17), (7.0, 4.25, 0.28), walnut, 0.13)
for x in (-2.8, 2.8):
    for y in (-1.55, 1.55):
        cylinder('Nonslip foot', (x, y, 0.035), 0.17, 0.07, felt)

# Open-front paper tray, sized for a portrait stack of stationery.
box('Paper tray floor', (1.18, 0.1, 0.39), (3.95, 3.65, 0.14), walnut, 0.06)
box('Tray felt liner', (1.18, 0.08, 0.47), (3.65, 3.3, 0.025), felt, 0.012)
for x in (-0.75, 3.11):
    box('Paper tray side', (x, 0.13, 0.71), (0.12, 3.62, 0.55), walnut, 0.04)
box('Paper tray back', (1.18, 1.9, 0.71), (3.96, 0.12, 0.55), walnut, 0.04)
# Two short front lips leave a useful finger opening.
for x in (-0.21, 2.57):
    box('Tray front retaining lip', (x, -1.65, 0.56), (1.12, 0.12, 0.22), walnut, 0.035)
for i in range(15):
    o = box('Individual sheet %02d' % i, (1.18+random.uniform(-0.025, 0.025), 0.12+random.uniform(-0.018, 0.018), 0.495+i*0.014), (3.18, 2.91, 0.011), paper, 0.003)
    o.rotation_euler.z = random.uniform(-0.008, 0.008)
for j in range(6):
    box('Printed note line', (1.08, 0.75-j*0.22, 0.7), (2.12 if j else 1.25, 0.012, 0.002), blue, 0)

cup('Tall open pen cup', -2.12, 1.05, 0.31, 0.71, 1.85, teal)
cup('Short open pencil cup', -2.2, -0.65, 0.31, 0.6, 1.25, teal)
for x, y, r in [(-2.12, 1.05, 0.71), (-2.2, -0.65, 0.6)]:
    cylinder('Cup brass foot ring', (x, y, 0.355), r+0.015, 0.065, brass)

for i in range(5):
    a = i*2*math.pi/5
    start = Vector((-2.12+0.29*math.cos(a), 1.05+0.29*math.sin(a), 0.44))
    direction = Vector((0.055*math.cos(a), 0.055*math.sin(a), 1)).normalized()
    length = 2.26+0.14*(i%3)
    tip = start+direction*length
    rod('Pen barrel', start, tip, 0.065, blue if i%2 else felt)
    rod('Pen cap', tip-direction*0.43, tip+direction*0.06, 0.075, teal)
    rod('Pen cap band', tip-direction*0.44, tip-direction*0.395, 0.077, brass)
    side = Vector((0.08, -0.025, 0))
    rod('Pen pocket clip', tip-direction*0.32+side, tip-direction*0.02+side, 0.013, brass)

for i in range(4):
    a = 0.5+i*1.6
    start = Vector((-2.2+0.23*math.cos(a), -0.65+0.23*math.sin(a), 0.44))
    direction = Vector((0.065*math.cos(a), 0.065*math.sin(a), 1)).normalized()
    length = 1.82+0.11*(i%3)
    end = start+direction*length
    rod('Hexagonal pencil', start, end, 0.062, yellow, 6)
    bpy.ops.mesh.primitive_cone_add(vertices=24, radius1=0.062, radius2=0.012, depth=0.21, location=end+direction*0.105)
    o = bpy.context.object
    o.name = 'Sharpened pencil wood'
    o.rotation_euler = direction.to_track_quat('Z', 'Y').to_euler()
    o.data.materials.append(pencilwood)
    bpy.ops.mesh.primitive_cone_add(vertices=16, radius1=0.014, radius2=0, depth=0.06, location=end+direction*0.24)
    o = bpy.context.object
    o.name = 'Graphite pencil point'
    o.rotation_euler = direction.to_track_quat('Z', 'Y').to_euler()
    o.data.materials.append(graphite)

# Small front catchall for clips, built with a visible recessed floor.
box('Accessory tray floor', (-2.16, -1.63, 0.36), (1.67, 0.63, 0.08), teal, 0.035)
for y in (-1.94, -1.32):
    box('Accessory tray long rim', (-2.16, y, 0.46), (1.67, 0.055, 0.2), teal, 0.022)
for x in (-2.97, -1.35):
    box('Accessory tray end rim', (x, -1.63, 0.46), (0.055, 0.62, 0.2), teal, 0.022)
for i in range(3):
    data = bpy.data.curves.new('Paperclip wire', 'CURVE')
    data.dimensions = '3D'
    data.bevel_depth = 0.013
    data.bevel_resolution = 3
    pts = []
    for j in range(65):
        a = -math.pi/2 + j*math.pi*3.5/64
        r = 0.11-0.035*j/64
        pts.append((r*math.cos(a)*1.8, r*math.sin(a), 0))
    sp = data.splines.new('POLY')
    sp.points.add(len(pts)-1)
    for p, co in zip(sp.points, pts):
        p.co = (*co, 1)
    o = bpy.data.objects.new('Brass paperclip', data)
    bpy.context.collection.objects.link(o)
    o.location = (-2.65+i*0.48, -1.63, 0.42+i*0.008)
    o.rotation_euler.z = -0.25+i*0.32
    o.data.materials.append(brass)

box('Desktop', (0, 0, -0.16), (200, 200, 0.25), desk, 0.04)
world = bpy.data.worlds.new('Desk studio')
bpy.context.scene.world = world
world.use_nodes = True
world.node_tree.nodes['Background'].inputs[1].default_value = 0.35
for name, loc, power, size in [('Window key', (-3, -4, 9), 1100, 6), ('Soft fill', (6, -1, 5), 700, 5), ('Back highlight', (-1, 6, 7), 950, 4)]:
    bpy.ops.object.light_add(type='AREA', location=loc)
    o = bpy.context.object
    o.name = name
    o.data.energy = power
    o.data.size = size
    o.rotation_euler = (Vector((0, 0, 0.8))-o.location).to_track_quat('-Z', 'Y').to_euler()
bpy.ops.object.camera_add(location=(9, -12, 12))
cam = bpy.context.object
cam.rotation_euler = (Vector((0, 0, 0.85))-cam.location).to_track_quat('-Z', 'Y').to_euler()
cam.data.type = 'ORTHO'
cam.data.ortho_scale = 10.3
scene = bpy.context.scene
scene.camera = cam
scene.render.engine = 'CYCLES'
scene.cycles.samples = 64
scene.render.resolution_x = 1500
scene.render.resolution_y = 1150
scene.render.resolution_percentage = 100
scene.view_settings.view_transform = 'AgX'
