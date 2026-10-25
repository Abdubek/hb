import bpy, math
from mathutils import Vector

bpy.ops.wm.read_factory_settings(use_empty=True)

def mat(name, color, metal=0, rough=0.6):
    m = bpy.data.materials.new(name)
    m.diffuse_color = (*color, 1)
    m.use_nodes = True
    p = m.node_tree.nodes.get('Principled BSDF')
    p.inputs['Base Color'].default_value = (*color, 1)
    p.inputs['Metallic'].default_value = metal
    p.inputs['Roughness'].default_value = rough
    return m

wood = mat('Ivory painted timber', (0.80, 0.77, 0.64))
trim = mat('Warm white trim', (0.94, 0.90, 0.77))
deck = mat('Honey colored decking', (0.40, 0.24, 0.115))
roofmat = mat('Patinated green roof', (0.08, 0.22, 0.18), 0.55, 0.48)
seammat = mat('Roof seam highlights', (0.12, 0.28, 0.23), 0.6)
stone = mat('Sandstone foundation', (0.53, 0.49, 0.40), 0, 0.85)
grass = mat('Soft garden lawn', (0.23, 0.32, 0.13), 0, 0.95)
metal = mat('Bronze finial', (0.28, 0.19, 0.07), 0.75, 0.3)

def box(name, loc, dims, material, bevel=0.018):
    bpy.ops.mesh.primitive_cube_add(size=1, location=loc)
    o = bpy.context.object
    o.name = name
    o.dimensions = dims
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    o.data.materials.append(material)
    if bevel:
        b = o.modifiers.new('Soft timber edges', 'BEVEL')
        b.width = bevel
        b.segments = 2
        o.modifiers.new('Weighted normals', 'WEIGHTED_NORMAL')
    return o

def beam(name, a, b, width, depth, material):
    a, b = Vector(a), Vector(b)
    o = box(name, (a+b)/2, (width, depth, (b-a).length), material)
    o.rotation_euler = (b-a).to_track_quat('Z', 'Y').to_euler()
    return o

def cyl(name, loc, radius, depth, material, vertices=64):
    bpy.ops.mesh.primitive_cylinder_add(vertices=vertices, radius=radius, depth=depth, location=loc)
    o = bpy.context.object
    o.name = name
    o.data.materials.append(material)
    b = o.modifiers.new('Rounded rim', 'BEVEL')
    b.width = 0.015
    b.segments = 2
    o.modifiers.new('Weighted normals', 'WEIGHTED_NORMAL')
    return o

def rod(name, a, b, radius, material):
    a, b = Vector(a), Vector(b)
    o = cyl(name, (a+b)/2, radius, (b-a).length, material, 16)
    o.rotation_euler = (b-a).to_track_quat('Z', 'Y').to_euler()
    return o

def tube(name, points, radius, material, cyclic=False):
    c = bpy.data.curves.new(name, 'CURVE')
    c.dimensions = '3D'
    c.bevel_depth = radius
    c.bevel_resolution = 2
    s = c.splines.new('POLY')
    s.points.add(len(points)-1)
    for p, co in zip(s.points, points):
        p.co = (*co, 1)
    s.use_cyclic_u = cyclic
    o = bpy.data.objects.new(name, c)
    bpy.context.collection.objects.link(o)
    o.data.materials.append(material)
    return o

box('Lawn', (0, 0, -0.15), (200, 200, 0.2), grass, 0)
cyl('Circular masonry plinth', (0, 0, 0.15), 3.22, 0.38, stone, 96)
cyl('Circular timber fascia', (0, 0, 0.38), 3.12, 0.16, wood, 96)
# Parallel deck boards trimmed to the circular footprint.
for i in range(31):
    x = (i-15)*0.195
    halfwidth = 0.092
    ymax = math.sqrt(max(0, 3.06**2-(abs(x)+halfwidth)**2))
    box('Clipped deck board', (x, 0, 0.485), (halfwidth*2, ymax*2, 0.065), deck, 0.007)

# Ten evenly spaced posts around the circular plan; front bay stays open.
N = 10
angles = [-math.pi/2-math.pi/N+i*2*math.pi/N for i in range(N)]
points = [Vector((2.73*math.cos(a), 2.73*math.sin(a), 0)) for a in angles]
for p in points:
    x, y = p.x, p.y
    box('Post pedestal', (x, y, 0.64), (0.36, 0.36, 0.26), trim)
    box('Tall gazebo post', (x, y, 1.98), (0.19, 0.19, 2.65), wood)
    box('Post base molding', (x, y, 0.80), (0.27, 0.27, 0.09), trim)
    box('Post capital collar', (x, y, 3.18), (0.29, 0.29, 0.12), trim)
    box('Post capital plate', (x, y, 3.30), (0.37, 0.37, 0.13), trim)

for i in range(N):
    a, b = points[i], points[(i+1)%N]
    beam('Perimeter header', a+Vector((0, 0, 3.37)), b+Vector((0, 0, 3.37)), 0.19, 0.25, wood)
    # Paired diagonal corbels beneath each header.
    for start, end in ((a, b), (b, a)):
        direction = (end-start).normalized()
        beam('Decorative knee brace', start+Vector((0, 0, 2.77)), start+direction*0.48+Vector((0, 0, 3.29)), 0.085, 0.13, trim)
    if i == 0:
        continue
    beam('Railing bottom rail', a+Vector((0, 0, 0.76)), b+Vector((0, 0, 0.76)), 0.10, 0.10, wood)
    beam('Broad handrail', a+Vector((0, 0, 1.48)), b+Vector((0, 0, 1.48)), 0.13, 0.09, trim)
    for j in range(1, 8):
        p = a.lerp(b, j/8)
        box('Railing baluster', (p.x, p.y, 1.10), (0.045, 0.045, 0.65), wood, 0.008)

# Three wide entrance steps align with the open front bay.
for name, y, z, depth, height in [('Bottom entrance step', -3.78, 0.05, 0.48, 0.18), ('Middle entrance step', -3.38, 0.14, 0.44, 0.36), ('Upper entrance step', -2.98, 0.24, 0.45, 0.54)]:
    box(name, (0, y, z), (1.62, depth, height), stone, 0.028)
    box('Step timber nosing', (0, y-0.015, z+height/2+0.015), (1.68, depth+0.05, 0.05), deck, 0.012)

# Shallow bell profile roof, composed of ten tapered facets.
profile = [(3.42, 3.49), (3.30, 3.61), (2.86, 3.79), (2.15, 4.10), (1.38, 4.48), (0.58, 4.88), (0.13, 5.06)]
verts = [(r*math.cos(a), r*math.sin(a), z) for r, z in profile for a in angles]
faces = []
for j in range(len(profile)-1):
    for i in range(N):
        faces.append((j*N+i, j*N+(i+1)%N, (j+1)*N+(i+1)%N, (j+1)*N+i))
faces.append(tuple((len(profile)-1)*N+i for i in range(N)))
mesh = bpy.data.meshes.new('Faceted bell roof mesh')
mesh.from_pydata(verts, [], faces)
mesh.update()
o = bpy.data.objects.new('Ten sided pavilion roof', mesh)
bpy.context.collection.objects.link(o)
o.data.materials.append(roofmat)
s = o.modifiers.new('Roof panel thickness', 'SOLIDIFY')
s.thickness = 0.06
s.offset = -1
for a in angles:
    tube('Raised radial roof seam', [(r*math.cos(a), r*math.sin(a), z+0.025) for r, z in profile], 0.023, seammat)
    beam('Exposed timber roof rafter', (3.24*math.cos(a), 3.24*math.sin(a), 3.45), (0, 0, 4.98), 0.105, 0.15, wood)
for r, z in profile[2:-1]:
    tube('Horizontal roof panel seam', [(r*math.cos(a), r*math.sin(a), z+0.018) for a in angles], 0.013, seammat, True)
for i in range(N):
    a, b = angles[i], angles[(i+1)%N]
    beam('Roof eave fascia', (3.40*math.cos(a), 3.40*math.sin(a), 3.47), (3.40*math.cos(b), 3.40*math.sin(b), 3.47), 0.105, 0.18, trim)
cyl('Roof apex collar', (0, 0, 5.10), 0.16, 0.16, metal, 32)
cyl('Finial stem', (0, 0, 5.30), 0.045, 0.30, metal, 24)
bpy.ops.mesh.primitive_uv_sphere_add(segments=24, ring_count=12, radius=0.12, location=(0, 0, 5.48))
bpy.context.object.name = 'Bronze ball finial'
bpy.context.object.data.materials.append(metal)

# Built-in bench follows three back bays, set inward from the railing.
for i in (4, 5, 6):
    a, b = points[i]*0.86, points[(i+1)%N]*0.86
    direction = (b-a).normalized()
    radial = (a+b).normalized()
    for offset in (-0.15, 0, 0.15):
        beam('Bench seat board', a+radial*offset+Vector((0, 0, 0.97)), b+radial*offset+Vector((0, 0, 0.97)), 0.13, 0.07, deck)
    for t in (0.15, 0.85):
        p = a.lerp(b, t)
        box('Bench leg', (p.x, p.y, 0.72), (0.13, 0.24, 0.42), wood)

world = bpy.data.worlds.new('Garden daylight')
world.use_nodes = True
world.node_tree.nodes['Background'].inputs[0].default_value = (0.69, 0.80, 0.95, 1)
world.node_tree.nodes['Background'].inputs[1].default_value = 0.4
bpy.context.scene.world = world
bpy.ops.object.light_add(type='SUN')
bpy.context.object.rotation_euler = (0.42, -0.48, -0.5)
bpy.context.object.data.energy = 2.2
bpy.context.object.data.angle = 0.12
for loc, power, size in [((-5, -6, 7), 900, 5), ((0, 0, 3.05), 90, 2)]:
    bpy.ops.object.light_add(type='AREA', location=loc)
    o = bpy.context.object
    o.data.energy = power
    o.data.size = size
    o.rotation_euler = (Vector((0, 0, 1))-o.location).to_track_quat('-Z', 'Y').to_euler()
bpy.ops.object.camera_add(location=(9, -13, 8.0))
o = bpy.context.object
o.rotation_euler = (Vector((0, -0.2, 2.35))-o.location).to_track_quat('-Z', 'Y').to_euler()
o.data.type = 'ORTHO'
o.data.ortho_scale = 10
scene = bpy.context.scene
scene.camera = o
scene.render.engine = 'CYCLES'
scene.render.resolution_x = 1400
scene.render.resolution_y = 1200
scene.render.resolution_percentage = 100
