import bpy, math
from mathutils import Vector

bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)

def mat(name, color, metal=0, rough=0.45):
    m = bpy.data.materials.new(name)
    m.diffuse_color = (*color, 1)
    m.use_nodes = True
    p = m.node_tree.nodes.get('Principled BSDF')
    p.inputs['Base Color'].default_value = (*color, 1)
    p.inputs['Metallic'].default_value = metal
    p.inputs['Roughness'].default_value = rough
    return m

def finish(o, name, m, bevel=0):
    o.name = name
    o.data.materials.append(m)
    if bevel:
        mod = o.modifiers.new('Machined edge bevels', 'BEVEL')
        mod.width = bevel
        mod.segments = 3
        o.modifiers.new('Weighted normals', 'WEIGHTED_NORMAL')
    return o

def box(name, loc, dim, m, bevel=0.01):
    bpy.ops.mesh.primitive_cube_add(size=1, location=loc)
    o = bpy.context.object
    o.dimensions = dim
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    return finish(o, name, m, bevel)

def rod(name, a, b, radius, m, vertices=32):
    a, b = Vector(a), Vector(b)
    bpy.ops.mesh.primitive_cylinder_add(vertices=vertices, radius=radius, depth=(b-a).length, location=(a+b)/2)
    o = bpy.context.object
    o.rotation_euler = (b-a).to_track_quat('Z', 'Y').to_euler()
    for p in o.data.polygons:
        p.use_smooth = len(p.vertices) == 4
    return finish(o, name, m, 0.004)

def sphere(name, loc, scale, m):
    bpy.ops.mesh.primitive_uv_sphere_add(segments=32, ring_count=16, location=loc)
    o = bpy.context.object
    o.scale = scale
    for p in o.data.polygons:
        p.use_smooth = True
    return finish(o, name, m)

def tube(name, points, radius, m):
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
    c.materials.append(m)

alloy = mat('Black anodized alloy', (0.065, 0.079, 0.091), 0.78, 0.3)
silver = mat('Exposed aluminum', (0.52, 0.58, 0.63), 0.88, 0.24)
rubber = mat('Rubber feet and grips', (0.018, 0.021, 0.025), 0, 0.8)
red = mat('Red anodized accents', (0.55, 0.025, 0.018), 0.65, 0.3)
white = mat('Scale markings', (0.72, 0.76, 0.77), 0.15, 0.6)
level = mat('Spirit level green', (0.32, 0.73, 0.095), 0.1, 0.22)
floormat = mat('Matte studio floor', (0.23, 0.26, 0.29), 0, 0.8)
box('Floor', (0, 0, -0.065), (200, 200, 0.1), floormat, 0)
# Three distinct legs with telescoping stages, clamps, pivots and feet.
for index in range(3):
    a = math.radians(-90+120*index)
    outward = Vector((math.cos(a), math.sin(a), 0))
    tangent = Vector((-math.sin(a), math.cos(a), 0))
    top = outward*0.155+Vector((0, 0, 1.69))
    bottom = outward*0.89+Vector((0, 0, 0.075))
    axis = (bottom-top).normalized()
    point = lambda t: top.lerp(bottom, t)
    rod('Leg %d upper tube'%index, point(0), point(0.43), 0.049, alloy)
    rod('Leg %d middle tube'%index, point(0.40), point(0.75), 0.040, silver)
    rod('Leg %d lower tube'%index, point(0.72), point(1), 0.031, alloy)
    rod('Foam upper leg grip', point(0.07), point(0.29), 0.058, rubber)
    for t in [0.415, 0.735]:
        p = point(t)
        rod('Leg clamp sleeve', p-axis*0.037, p+axis*0.037, 0.057 if t < 0.5 else 0.048, alloy)
        rod('Red clamp collar', p-axis*0.031, p-axis*0.015, 0.059 if t < 0.5 else 0.050, red)
        lever = box('Flip lock lever', p+outward*0.052, (0.044, 0.033, 0.092), rubber, 0.012)
        lever.rotation_euler = axis.to_track_quat('Z', 'Y').to_euler()
        rod('Clamp hinge pin', p+outward*0.042-tangent*0.035, p+outward*0.042+tangent*0.035, 0.012, silver)
    sphere('Anti slip rubber foot', bottom-Vector((0, 0, 0.015)), (0.072, 0.072, 0.060), rubber)
    rod('Leg pivot axle', top-tangent*0.071, top+tangent*0.071, 0.035, silver)
    for s in [-1, 1]:
        rod('Pivot end cap', top+tangent*(s*0.071), top+tangent*(s*0.083), 0.040, alloy)
    rod('Shoulder connection', outward*0.07+Vector((0, 0, 1.69)), top, 0.068, alloy)
    # Spreader links connect the legs to a sliding central hub.
    link_start = outward*0.065+Vector((0, 0, 0.91))
    link_end = point(0.52)
    rod('Leg spreader brace', link_start, link_end, 0.016, alloy, 20)
    rod('Spreader outer pivot', link_end-tangent*0.045, link_end+tangent*0.045, 0.019, silver, 20)

rod('Central lower column', (0, 0, 0.74), (0, 0, 1.68), 0.040, alloy)
rod('Spreader sliding hub', (0, 0, 0.855), (0, 0, 0.965), 0.079, alloy)
rod('Hub lock knob shaft', (0, -0.06, 0.91), (0, -0.12, 0.91), 0.018, silver)
rod('Hub lock knob', (0, -0.11, 0.91), (0, -0.145, 0.91), 0.033, rubber)
rod('Tripod shoulder casting', (0, 0, 1.62), (0, 0, 1.78), 0.148, alloy)
rod('Shoulder accent ring', (0, 0, 1.755), (0, 0, 1.78), 0.15, red)
rod('Column collar', (0, 0, 1.775), (0, 0, 1.835), 0.077, rubber)
rod('Extended central elevator column', (0, 0, 1.79), (0, 0, 2.19), 0.043, silver)
for z in [1.87+i*0.035 for i in range(8)]:
    box('Column height graduation', (0.018, -0.040, z), (0.019, 0.003, 0.004), alloy, 0)
rod('Column locking screw', (0.12, 0, 1.715), (0.225, 0, 1.715), 0.019, silver)
rod('Column locking knob', (0.205, 0, 1.715), (0.255, 0, 1.715), 0.045, rubber)
# A compact ball head and empty quick release platform make the tripod functional.
rod('Head panning base', (0, 0, 2.16), (0, 0, 2.225), 0.105, alloy)
rod('Pan scale ring', (0, 0, 2.175), (0, 0, 2.194), 0.108, silver)
for i in range(24):
    a = 2*math.pi*i/24
    o = box('Pan scale tick', (0.109*math.cos(a), 0.109*math.sin(a), 2.184), (0.008, 0.003, 0.014 if i%3 == 0 else 0.008), alloy, 0)
    o.rotation_euler.z = a+math.pi/2
rod('Ball socket housing', (0, 0, 2.22), (0, 0, 2.34), 0.087, alloy)
sphere('Exposed ball joint', (0, 0, 2.345), (0.072, 0.072, 0.072), silver)
rod('Ball platform stem', (0, 0, 2.365), (0, 0, 2.425), 0.030, silver)
rod('Ball tension spindle', (0.07, 0, 2.28), (0.16, 0, 2.28), 0.020, silver)
rod('Ball tension knob', (0.14, 0, 2.28), (0.20, 0, 2.28), 0.052, rubber)
box('Quick release clamp', (0, 0, 2.437), (0.24, 0.19, 0.055), alloy, 0.014)
box('Camera mounting plate', (0, 0, 2.474), (0.205, 0.16, 0.032), silver, 0.012)
for x in [-0.06, 0.06]:
    box('Plate rubber pad', (x, 0, 2.495), (0.063, 0.133, 0.012), rubber, 0.007)
rod('Quarter inch camera screw', (0, 0, 2.489), (0, 0, 2.519), 0.012, silver, 24)
rod('Release clamp screw', (-0.10, 0, 2.436), (-0.17, 0, 2.436), 0.015, silver)
rod('Release clamp knob', (-0.19, 0, 2.436), (-0.15, 0, 2.436), 0.030, red)
rod('Level bezel', (0.077, -0.054, 2.501), (0.077, -0.054, 2.508), 0.021, alloy)
rod('Bubble level window', (0.077, -0.054, 2.508), (0.077, -0.054, 2.511), 0.016, level)
sphere('Spirit level bubble', (0.077, -0.054, 2.513), (0.005, 0.005, 0.002), white)
# Bent ballast hook below the column.
pts = [(0, 0, 0.76), (0, 0, 0.65)]
for i in range(17):
    a = math.pi+math.pi*i/16
    pts.append((0.042+0.042*math.cos(a), 0, 0.65+0.042*math.sin(a)))
tube('Ballast hook', pts, 0.011, silver)

scene = bpy.context.scene
scene.world = scene.world or bpy.data.worlds.new('World')
scene.world.use_nodes = True
scene.world.node_tree.nodes['Background'].inputs[0].default_value = (0.28, 0.32, 0.38, 1)
scene.world.node_tree.nodes['Background'].inputs[1].default_value = 0.5
for loc, energy, size in [((3, -4, 5), 1000, 4), ((-3, -2, 3), 700, 3), ((1, 3, 4), 1200, 3)]:
    bpy.ops.object.light_add(type='AREA', location=loc)
    o = bpy.context.object
    o.data.energy = energy
    o.data.size = size
    o.rotation_euler = (Vector((0, 0, 1.3))-o.location).to_track_quat('-Z', 'Y').to_euler()
bpy.ops.object.camera_add(location=(3.5, -6, 3.2))
cam = bpy.context.object
cam.rotation_euler = (Vector((0, 0, 1.25))-cam.location).to_track_quat('-Z', 'Y').to_euler()
cam.data.type = 'ORTHO'
cam.data.ortho_scale = 3.25
scene.camera = cam
scene.render.resolution_x = 1100
scene.render.resolution_y = 1200
scene.render.resolution_percentage = 100
