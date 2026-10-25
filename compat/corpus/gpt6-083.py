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

def cylinder(name, loc, radius, depth, material, bevel=0.025, vertices=64):
    bpy.ops.mesh.primitive_cylinder_add(vertices=vertices, radius=radius, depth=depth, location=loc)
    o = bpy.context.object
    o.name = name
    o.data.materials.append(material)
    for p in o.data.polygons:
        p.use_smooth = len(p.vertices) == 4
    if bevel:
        b = o.modifiers.new('Machined edge', 'BEVEL')
        b.width = bevel
        b.segments = 3
        o.modifiers.new('Weighted normals', 'WEIGHTED_NORMAL')
    return o

def rod(name, a, b, radius, material):
    a, b = Vector(a), Vector(b)
    o = cylinder(name, (a+b)/2, radius, (b-a).length, material, 0.01, 24)
    o.rotation_euler = (b-a).to_track_quat('Z', 'Y').to_euler()
    return o

def curve(name, coords, radius, material):
    data = bpy.data.curves.new(name, 'CURVE')
    data.dimensions = '3D'
    data.bevel_depth = radius
    data.bevel_resolution = 4
    sp = data.splines.new('POLY')
    sp.points.add(len(coords)-1)
    for p, co in zip(sp.points, coords):
        p.co = (*co, 1)
    ob = bpy.data.objects.new(name, data)
    bpy.context.collection.objects.link(ob)
    ob.data.materials.append(material)

bronze = mat('Satin champagne bronze', (0.43, 0.29, 0.13), 0.8, 0.28)
wood = mat('Smoked walnut shelves', (0.22, 0.105, 0.044), 0, 0.38)
base = mat('Dark mineral base', (0.07, 0.085, 0.08), 0.12, 0.6)
ceramic = mat('Ivory ceramic', (0.87, 0.83, 0.72), 0, 0.28)
teal = mat('Teal ceramic', (0.055, 0.25, 0.25), 0.15, 0.27)
ground = mat('Warm studio ground', (0.37, 0.35, 0.31), 0, 0.85)

cylinder('Heavy circular plinth', (0, 0, 0.17), 1.48, 0.3, base, 0.08, 96)
cylinder('Base bronze reveal', (0, 0, 0.335), 1.36, 0.055, bronze, 0.014)
cylinder('Central structural mast', (0, 0, 2.69), 0.14, 4.68, bronze, 0.025)
cylinder('Mast foot collar', (0, 0, 0.46), 0.27, 0.2, bronze)
cylinder('Mast top finial', (0, 0, 5.06), 0.2, 0.15, bronze, 0.05)

# Nine radial shelves climb through one and a half revolutions.
count = 9
start = math.radians(-110)
step = math.radians(67.5)
for i in range(count):
    angle = start + step*i
    z = 0.84 + 0.49*i
    d = Vector((math.cos(angle), math.sin(angle), 0))
    center = d*0.91
    cylinder('Shelf %02d walnut disk' % (i+1), (center.x, center.y, z), 0.62, 0.105, wood, 0.026)
    cylinder('Shelf %02d bronze underside' % (i+1), (center.x, center.y, z-0.062), 0.58, 0.026, bronze, 0.01)
    cylinder('Shelf mast collar', (0, 0, z-0.13), 0.205, 0.18, bronze, 0.014)
    rod('Radial support arm', (0, 0, z-0.105), (center.x, center.y, z-0.105), 0.055, bronze)
    rod('Diagonal shelf brace', (d.x*0.17, d.y*0.17, z-0.35), (center.x, center.y, z-0.1), 0.035, bronze)
    cylinder('Undershelf support boss', (center.x, center.y, z-0.12), 0.14, 0.13, bronze)
    # Small display objects leave the circular shelf outlines visible.
    if i in (0, 3, 6):
        cylinder('Ceramic display pedestal', (center.x, center.y, z+0.14), 0.19, 0.17, ceramic, 0.035)
        bpy.ops.mesh.primitive_uv_sphere_add(segments=32, ring_count=16, radius=0.15, location=(center.x, center.y, z+0.37))
        o = bpy.context.object
        o.name = 'Spherical display sculpture'
        o.data.materials.append(teal)
        for p in o.data.polygons:
            p.use_smooth = True
    elif i in (2, 5, 8):
        cylinder('Display sample vessel', (center.x, center.y, z+0.19), 0.16, 0.27, teal, 0.04)
        cylinder('Display sample lid', (center.x, center.y, z+0.34), 0.17, 0.04, bronze, 0.012)

coords = []
for k in range(361):
    f = k/360
    a = start + step*(count-1)*f
    coords.append((0.32*math.cos(a), 0.32*math.sin(a), 0.64+0.49*(count-1)*f))
curve('Ascending helical accent ribbon', coords, 0.035, bronze)
for k in range(4):
    a = k*math.pi/2 + math.pi/4
    cylinder('Recessed rubber foot', (1.02*math.cos(a), 1.02*math.sin(a), 0.045), 0.12, 0.07, base, 0.015)

bpy.ops.mesh.primitive_plane_add(size=200)
bpy.context.object.name = 'Studio floor'
bpy.context.object.data.materials.append(ground)
world = bpy.data.worlds.new('Soft studio')
bpy.context.scene.world = world
world.use_nodes = True
world.node_tree.nodes['Background'].inputs[1].default_value = 0.3
for name, loc, power, size in [('Key', (4, -6, 8), 950, 5), ('Fill', (-4, -2, 5), 650, 4), ('Rim', (2, 4, 7), 1100, 3)]:
    bpy.ops.object.light_add(type='AREA', location=loc)
    o = bpy.context.object
    o.name = name
    o.data.energy = power
    o.data.shape = 'DISK'
    o.data.size = size
    o.rotation_euler = (Vector((0, 0, 2.5))-o.location).to_track_quat('-Z', 'Y').to_euler()
bpy.ops.object.camera_add(location=(8, -11, 8))
cam = bpy.context.object
cam.rotation_euler = (Vector((0, 0, 2.55))-cam.location).to_track_quat('-Z', 'Y').to_euler()
cam.data.type = 'ORTHO'
cam.data.ortho_scale = 7.25
scene = bpy.context.scene
scene.camera = cam
scene.render.engine = 'CYCLES'
scene.cycles.samples = 64
scene.render.resolution_x = 1100
scene.render.resolution_y = 1400
scene.render.resolution_percentage = 100
scene.view_settings.view_transform = 'AgX'
