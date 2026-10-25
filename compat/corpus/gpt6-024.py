import bpy, math
from mathutils import Vector

bpy.ops.wm.read_factory_settings(use_empty=True)

def mat(name, color, metal=0, rough=0.45):
    m = bpy.data.materials.new(name)
    m.diffuse_color = (*color, 1)
    m.use_nodes = True
    p = m.node_tree.nodes.get('Principled BSDF')
    p.inputs['Base Color'].default_value = (*color, 1)
    p.inputs['Metallic'].default_value = metal
    p.inputs['Roughness'].default_value = rough
    return m

blue = mat('Blue powder coated frame', (0.025, 0.22, 0.46), 0.4)
yellow = mat('Golden yellow molded slide', (0.96, 0.52, 0.025), 0.05, 0.3)
red = mat('Coral safety rails', (0.80, 0.10, 0.045), 0.3)
steel = mat('Stainless fasteners', (0.55, 0.60, 0.63), 0.8, 0.25)
deck = mat('Dark non slip decking', (0.075, 0.10, 0.12), 0, 0.9)
rubber = mat('Muted teal safety tiles', (0.14, 0.29, 0.27), 0, 0.95)
rubber2 = mat('Alternate safety tiles', (0.18, 0.34, 0.30), 0, 0.95)
grass = mat('Surrounding lawn', (0.27, 0.34, 0.13), 0, 0.95)

def box(name, loc, dims, material, bevel=0.025):
    bpy.ops.mesh.primitive_cube_add(size=1, location=loc)
    o = bpy.context.object
    o.name = name
    o.dimensions = dims
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    o.data.materials.append(material)
    if bevel:
        b = o.modifiers.new('Rounded edges', 'BEVEL')
        b.width = bevel
        b.segments = 3
        o.modifiers.new('Weighted normals', 'WEIGHTED_NORMAL')
    return o

def rod(name, a, b, radius, material):
    a, b = Vector(a), Vector(b)
    bpy.ops.mesh.primitive_cylinder_add(vertices=24, radius=radius, depth=(b-a).length, location=(a+b)/2)
    o = bpy.context.object
    o.name = name
    o.rotation_euler = (b-a).to_track_quat('Z', 'Y').to_euler()
    o.data.materials.append(material)
    for p in o.data.polygons:
        p.use_smooth = len(p.vertices) == 4
    bevel = o.modifiers.new('End rounding', 'BEVEL')
    bevel.width = 0.012
    bevel.segments = 2
    o.modifiers.new('Weighted normals', 'WEIGHTED_NORMAL')
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

box('Ground', (0, 0, -0.16), (200, 200, 0.2), grass, 0)
for x in range(6):
    for y in range(10):
        box('Impact absorbing tile', (x-2.5, y-4.0, 0), (0.985, 0.985, 0.12), rubber if (x+y)%2 else rubber2, 0.016)

# Elevated landing, front at y=0.8, rear at y=2.0.
for x in (-0.75, 0.75):
    for y in (0.80, 2.00):
        box('Post anchor foot', (x, y, 0.11), (0.31, 0.31, 0.09), steel)
        rod('Platform support post', (x, y, 0.13), (x, y, 3.55), 0.065, blue)
        bpy.ops.mesh.primitive_uv_sphere_add(segments=16, ring_count=8, radius=0.073, location=(x, y, 3.55))
        bpy.context.object.name = 'Rounded post cap'
        bpy.context.object.data.materials.append(red)
        for dx in (-0.10, 0.10):
            rod('Anchor bolt', (x+dx, y, 0.15), (x+dx, y, 0.18), 0.028, steel)
box('Platform frame', (0, 1.4, 2.53), (1.6, 1.35, 0.16), blue)
for i in range(8):
    box('Landing deck plank', (-0.665+i*0.19, 1.4, 2.64), (0.18, 1.30, 0.07), deck, 0.008)
for x in (-0.75, 0.75):
    rod('Side guard top rail', (x, 0.8, 3.49), (x, 2.0, 3.49), 0.05, red)
    rod('Side guard lower rail', (x, 0.8, 2.82), (x, 2.0, 2.82), 0.035, red)
    for i in range(1, 8):
        y = 0.8+i*0.15
        rod('Vertical guard infill', (x, y, 2.83), (x, y, 3.48), 0.021, red)
    rod('Under platform diagonal brace', (x, 0.8, 1.18), (x, 2.0, 2.50), 0.04, blue)
# Rear guard wings leave a central ladder entrance.
for s in (-1, 1):
    rod('Rear entry guard wing', (s*0.75, 2, 3.49), (s*0.49, 2, 3.49), 0.05, red)
    rod('Rear entry upright', (s*0.49, 2, 2.70), (s*0.49, 2, 3.49), 0.04, red)

# Smooth slide profile: nearly level entry and a flattened runout.
def center(t):
    y = 0.80-4.60*t
    z = 2.675-2.34*(3*t*t-2*t*t*t)
    return y, z
# Open U-shaped cross section with tall molded side walls and rounded lip tubes.
section = [(-0.66, 0.25), (-0.66, 0.11), (-0.60, 0.025), (-0.52, 0), (0.52, 0), (0.60, 0.025), (0.66, 0.11), (0.66, 0.25)]
N = 65
verts = []
for i in range(N):
    t = i/(N-1)
    y, z = center(t)
    for x, rise in section:
        verts.append((x, y, z+rise))
faces = []
K = len(section)
for i in range(N-1):
    for j in range(K-1):
        a = i*K+j
        faces.append((a, a+1, a+1+K, a+K))
mesh = bpy.data.meshes.new('Continuous slide chute mesh')
mesh.from_pydata(verts, [], faces)
mesh.update()
o = bpy.data.objects.new('Sculpted yellow slide chute', mesh)
bpy.context.collection.objects.link(o)
o.data.materials.append(yellow)
for p in mesh.polygons:
    p.use_smooth = True
s = o.modifiers.new('Molded shell thickness', 'SOLIDIFY')
s.thickness = 0.055
s.offset = -1
b = o.modifiers.new('Soft shell edges', 'BEVEL')
b.width = 0.018
b.segments = 3
for x in (-0.66, 0.66):
    tube('Rounded slide rim', [(x, center(i/64)[0], center(i/64)[1]+0.25) for i in range(65)], 0.043, yellow)
# Flat terminal landing with a rounded leading edge.
box('Slide runout extension', (0, -3.98, 0.308), (1.16, 0.39, 0.055), yellow, 0.024)
for x in (-0.66, 0.66):
    tube('Runout side lip', [(x, -3.80, 0.585), (x, -4.04, 0.54), (x, -4.17, 0.40)], 0.045, yellow)
for t in (0.43, 0.82):
    y, z = center(t)
    rod('Chute underside crossbar', (-0.59, y, z-0.10), (0.59, y, z-0.10), 0.045, blue)
    for x in (-0.48, 0.48):
        rod('Chute support leg', (x, y, 0.09), (x, y, z-0.1), 0.055, blue)
        box('Chute support foot', (x, y, 0.12), (0.22, 0.24, 0.10), steel)
# Grab rails flank the entrance without crossing the slide opening.
for x in (-0.64, 0.64):
    tube('Slide entry hand grip', [(x, 1.20, 2.72), (x, 1.20, 3.17), (x, 1.05, 3.30), (x, 0.68, 3.22), (x, 0.35, 2.93)], 0.04, red)

# Inclined ladder at the back, with level anti-slip treads.
for x in (-0.48, 0.48):
    rod('Ladder stringer', (x, 3.63, 0.15), (x, 2.02, 2.67), 0.055, blue)
    tube('Ladder handrail', [(x, 3.58, 0.72), (x, 2.13, 3.16), (x, 1.99, 3.44), (x, 1.80, 3.49)], 0.043, red)
    for t in (0.14, 0.55):
        y = 3.63-1.61*t
        z = 0.15+2.52*t
        rod('Handrail support', (x, y, z), (x, y, z+0.56), 0.035, red)
for i in range(1, 9):
    t = i/9
    y, z = 3.63-1.61*t, 0.15+2.52*t
    box('Ladder stair tread', (0, y, z), (0.93, 0.24, 0.065), blue, 0.018)
    box('Non slip tread insert', (0, y, z+0.037), (0.78, 0.18, 0.013), deck, 0.005)

world = bpy.data.worlds.new('Playground sky')
world.use_nodes = True
world.node_tree.nodes['Background'].inputs[0].default_value = (0.72, 0.82, 1, 1)
world.node_tree.nodes['Background'].inputs[1].default_value = 0.4
bpy.context.scene.world = world
bpy.ops.object.light_add(type='SUN')
bpy.context.object.rotation_euler = (0.48, -0.5, -0.35)
bpy.context.object.data.energy = 2.3
bpy.context.object.data.angle = 0.12
bpy.ops.object.light_add(type='AREA', location=(-4, -4, 7))
o = bpy.context.object
o.data.energy = 650
o.data.size = 5
o.rotation_euler = (Vector((0, 0, 1.3))-o.location).to_track_quat('-Z', 'Y').to_euler()
bpy.ops.object.camera_add(location=(10, -8, 7.2))
o = bpy.context.object
o.rotation_euler = (Vector((0, -0.15, 1.45))-o.location).to_track_quat('-Z', 'Y').to_euler()
o.data.type = 'ORTHO'
o.data.ortho_scale = 10.7
scene = bpy.context.scene
scene.camera = o
scene.render.engine = 'CYCLES'
scene.render.resolution_x = 1400
scene.render.resolution_y = 1100
scene.render.resolution_percentage = 100
