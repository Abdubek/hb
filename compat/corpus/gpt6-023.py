import bpy, math
from mathutils import Vector

bpy.ops.wm.read_factory_settings(use_empty=True)

def mat(name, color, metal=0, rough=0.5):
    m = bpy.data.materials.new(name)
    m.diffuse_color = (*color, 1)
    m.use_nodes = True
    p = m.node_tree.nodes.get('Principled BSDF')
    p.inputs['Base Color'].default_value = (*color, 1)
    p.inputs['Metallic'].default_value = metal
    p.inputs['Roughness'].default_value = rough
    return m

tankmat = mat('Faded blue tank paint', (0.19, 0.37, 0.43), 0.55, 0.4)
steel = mat('Galvanized structural steel', (0.24, 0.29, 0.30), 0.8, 0.4)
dark = mat('Dark steel joints', (0.075, 0.095, 0.10), 0.75)
concrete = mat('Concrete footings', (0.46, 0.45, 0.40), 0, 0.9)
earth = mat('Dry grass ground', (0.28, 0.30, 0.18), 0, 0.95)
white = mat('Painted lettering', (0.87, 0.88, 0.78), 0.1)

def box(name, loc, dimensions, material, bevel=0.025):
    bpy.ops.mesh.primitive_cube_add(size=1, location=loc)
    o = bpy.context.object
    o.name = name
    o.dimensions = dimensions
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    o.data.materials.append(material)
    if bevel:
        m = o.modifiers.new('Edge bevel', 'BEVEL')
        m.width = bevel
        m.segments = 2
        o.modifiers.new('Weighted normals', 'WEIGHTED_NORMAL')
    return o

def beam(name, a, b, width, material, depth=None):
    a, b = Vector(a), Vector(b)
    o = box(name, (a+b)/2, (width, depth or width, (b-a).length), material, 0.012)
    o.rotation_euler = (b-a).to_track_quat('Z', 'Y').to_euler()
    return o

def cyl(name, loc, radius, depth, material, vertices=64):
    bpy.ops.mesh.primitive_cylinder_add(vertices=vertices, radius=radius, depth=depth, location=loc)
    o = bpy.context.object
    o.name = name
    o.data.materials.append(material)
    for p in o.data.polygons:
        p.use_smooth = len(p.vertices) == 4
    m = o.modifiers.new('Small rim bevel', 'BEVEL')
    m.width = 0.018
    m.segments = 2
    o.modifiers.new('Weighted normals', 'WEIGHTED_NORMAL')
    return o

def rod(name, a, b, radius, material):
    a, b = Vector(a), Vector(b)
    o = cyl(name, (a+b)/2, radius, (b-a).length, material, 16)
    o.rotation_euler = (b-a).to_track_quat('Z', 'Y').to_euler()
    return o

def ring(name, z, radius, thickness, material):
    bpy.ops.mesh.primitive_torus_add(major_radius=radius, minor_radius=thickness, major_segments=96, minor_segments=10, location=(0, 0, z))
    o = bpy.context.object
    o.name = name
    o.data.materials.append(material)
    for f in o.data.polygons:
        f.use_smooth = True
    return o

box('Ground', (0, 0, -0.14), (200, 200, 0.2), earth, 0)
# Four splayed legs, each with bolted base and concrete footing.
signs = [(-1, -1), (1, -1), (1, 1), (-1, 1)]
def legpoint(s, z):
    t = (z-0.45)/(6.65-0.45)
    r = 2.08*(1-t)+1.34*t
    return (s[0]*r, s[1]*r, z)
for sx, sy in signs:
    x, y = sx*2.08, sy*2.08
    box('Concrete pier', (x, y, 0.17), (0.85, 0.85, 0.46), concrete)
    box('Base plate', (x, y, 0.425), (0.60, 0.60, 0.075), dark)
    beam('Splayed square steel leg', (x, y, 0.46), (sx*1.34, sy*1.34, 6.65), 0.22, steel)
    for dx in (-0.23, 0.23):
        for dy in (-0.23, 0.23):
            cyl('Anchor nut', (x+dx, y+dy, 0.485), 0.045, 0.055, dark, 6)
levels = [0.72, 2.68, 4.64, 6.48]
for i in range(4):
    a, b = signs[i], signs[(i+1)%4]
    for z in levels:
        beam('Horizontal frame tie', legpoint(a, z), legpoint(b, z), 0.12, steel)
    for z0, z1 in zip(levels[:-1], levels[1:]):
        beam('Cross bracing diagonal', legpoint(a, z0), legpoint(b, z1), 0.075, steel, 0.055)
        beam('Cross bracing diagonal', legpoint(b, z0), legpoint(a, z1), 0.075, steel, 0.055)

# Tank shell, shallow hopper underside, and conical roof.
bpy.ops.mesh.primitive_cone_add(vertices=96, radius1=0.53, radius2=1.88, depth=0.68, location=(0, 0, 6.67))
bpy.context.object.name = 'Conical tank sump'
bpy.context.object.data.materials.append(tankmat)
cyl('Cylindrical water tank', (0, 0, 8.20), 1.88, 2.40, tankmat, 96)
for z in (7.01, 7.78, 8.57, 9.39):
    ring('Tank reinforcing band', z, 1.89, 0.045, dark)
for z in (7.07, 9.32):
    for i in range(40):
        a = i*2*math.pi/40
        bpy.ops.mesh.primitive_uv_sphere_add(segments=8, ring_count=4, radius=0.028, location=(1.888*math.cos(a), 1.888*math.sin(a), z))
        bpy.context.object.name = 'Tank band rivet'
        bpy.context.object.data.materials.append(steel)
bpy.ops.mesh.primitive_cone_add(vertices=96, radius1=2.04, radius2=0.22, depth=0.70, location=(0, 0, 9.74))
bpy.context.object.name = 'Conical weather roof'
bpy.context.object.data.materials.append(tankmat)
ring('Roof drip edge', 9.40, 2.02, 0.045, steel)
cyl('Roof vent neck', (0, 0, 10.16), 0.18, 0.28, dark)
bpy.ops.mesh.primitive_cone_add(vertices=48, radius1=0.32, radius2=0.07, depth=0.13, location=(0, 0, 10.34))
bpy.context.object.name = 'Vent rain cap'
bpy.context.object.data.materials.append(steel)

# Annular maintenance catwalk, leaving the tank underside visible.
N = 96
verts = [(r*math.cos(2*math.pi*i/N), r*math.sin(2*math.pi*i/N), 6.96) for r in (1.90, 2.30) for i in range(N)]
faces = [(i, (i+1)%N, N+(i+1)%N, N+i) for i in range(N)]
mesh = bpy.data.meshes.new('Annular catwalk mesh')
mesh.from_pydata(verts, [], faces)
mesh.update()
o = bpy.data.objects.new('Maintenance catwalk', mesh)
bpy.context.collection.objects.link(o)
o.data.materials.append(steel)
s = o.modifiers.new('Deck thickness', 'SOLIDIFY')
s.thickness = 0.07
# Rail arcs leave an opening at the ladder on the front side.
def arc_rail(z):
    c = bpy.data.curves.new('Catwalk railing', 'CURVE')
    c.dimensions = '3D'
    c.bevel_depth = 0.028
    c.bevel_resolution = 2
    sp = c.splines.new('POLY')
    pts = [(2.27*math.cos(a), 2.27*math.sin(a), z) for a in [-math.pi/2+0.20+i*(2*math.pi-0.40)/96 for i in range(97)]]
    sp.points.add(len(pts)-1)
    for p, co in zip(sp.points, pts):
        p.co = (*co, 1)
    obj = bpy.data.objects.new('Continuous safety rail', c)
    bpy.context.collection.objects.link(obj)
    obj.data.materials.append(steel)
for z in (7.48, 7.98):
    arc_rail(z)
for i in range(20):
    a = -math.pi/2+0.21+i*(2*math.pi-0.42)/19
    x, y = 2.27*math.cos(a), 2.27*math.sin(a)
    rod('Catwalk railing stanchion', (x, y, 6.96), (x, y, 8.0), 0.03, steel)

for x in (-0.32, 0.32):
    rod('Ladder side rail', (x, -2.36, 0.18), (x, -2.36, 8.02), 0.043, steel)
for i in range(23):
    z = 0.36+i*0.29
    rod('Ladder rung', (-0.32, -2.36, z), (0.32, -2.36, z), 0.027, steel)
for z in (2.68, 4.64, 6.48):
    for x in (-0.32, 0.32):
        rod('Ladder fixing bracket', (x, -2.36, z), (x, legpoint((1, -1), z)[1], z), 0.035, dark)
rod('Downpipe', (0.48, 0.45, 0.42), (0.48, 0.45, 6.7), 0.105, tankmat)
rod('Sump outlet elbow', (0, 0, 6.38), (0.48, 0.45, 6.38), 0.105, tankmat)
rod('Ground outlet pipe', (0.48, 0.45, 0.48), (1.3, 0.45, 0.48), 0.105, tankmat)
cyl('Pipe flange', (0.48, 0.45, 1.1), 0.17, 0.08, dark, 32)

bpy.ops.object.text_add(location=(0, -1.899, 8.35), rotation=(math.pi/2, 0, 0))
o = bpy.context.object
o.name = 'Tank identification'
o.data.body = 'WATER'
o.data.align_x = 'CENTER'
o.data.size = 0.34
o.data.extrude = 0.002
o.data.materials.append(white)
world = bpy.data.worlds.new('Overcast sky')
world.use_nodes = True
world.node_tree.nodes['Background'].inputs[0].default_value = (0.66, 0.77, 0.91, 1)
world.node_tree.nodes['Background'].inputs[1].default_value = 0.4
bpy.context.scene.world = world
bpy.ops.object.light_add(type='SUN')
bpy.context.object.rotation_euler = (0.42, -0.52, -0.4)
bpy.context.object.data.energy = 2.4
bpy.context.object.data.angle = 0.12
bpy.ops.object.light_add(type='AREA', location=(-6, -8, 11))
o = bpy.context.object
o.data.energy = 1100
o.data.size = 7
o.rotation_euler = (Vector((0, 0, 5))-o.location).to_track_quat('-Z', 'Y').to_euler()
bpy.ops.object.camera_add(location=(13, -19, 12))
o = bpy.context.object
o.rotation_euler = (Vector((0, 0, 5.1))-o.location).to_track_quat('-Z', 'Y').to_euler()
o.data.type = 'ORTHO'
o.data.ortho_scale = 13
scene = bpy.context.scene
scene.camera = o
scene.render.engine = 'CYCLES'
scene.render.resolution_x = 1100
scene.render.resolution_y = 1400
scene.render.resolution_percentage = 100
