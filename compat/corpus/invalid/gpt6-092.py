import bpy, math
from mathutils import Vector

bpy.ops.wm.read_factory_settings(use_empty=True)

def material(name, color, metallic=0, roughness=0.45):
    m = bpy.data.materials.new(name)
    m.diffuse_color = (*color, 1)
    m.use_nodes = True
    p = m.node_tree.nodes.get('Principled BSDF')
    p.inputs['Base Color'].default_value = (*color, 1)
    p.inputs['Metallic'].default_value = metallic
    p.inputs['Roughness'].default_value = roughness
    return m

def box(name, loc, dims, mat, bevel=0.015, rotation=None):
    bpy.ops.mesh.primitive_cube_add(size=1, location=loc)
    o = bpy.context.object
    o.name = name
    o.dimensions = dims
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    if rotation:
        o.rotation_euler = rotation
    o.data.materials.append(mat)
    if bevel:
        b = o.modifiers.new('Rounded edges', 'BEVEL')
        b.width = bevel
        b.segments = 3
        o.modifiers.new('Weighted normals', 'WEIGHTED_NORMAL')
    return o

def rod(name, a, b, radius, mat):
    a, b = Vector(a), Vector(b)
    bpy.ops.mesh.primitive_cylinder_add(vertices=32, radius=radius, depth=(b-a).length, location=(a+b)/2)
    o = bpy.context.object
    o.name = name
    o.rotation_euler = (b-a).to_track_quat('Z', 'Y').to_euler()
    o.data.materials.append(mat)
    for p in o.data.polygons:
        p.use_smooth = True
    return o

wood = material('Walnut', (0.20, 0.075, 0.029), roughness=0.38)
# Procedural grain requires no image textures.
nodes = wood.node_tree.nodes
links = wood.node_tree.links
tex = nodes.new('ShaderNodeTexNoise')
tex.inputs['Scale'].default_value = 4
tex.inputs['Detail'].default_value = 3
coord = nodes.new('ShaderNodeTexCoord')
scale = nodes.new('ShaderNodeVectorMath')
scale.operation = 'MULTIPLY'
scale.inputs[1].default_value = (9, 9, 0.7)
links.new(coord.outputs['Generated'], scale.inputs[0])
links.new(scale.outputs['Vector'], tex.inputs['Vector'])
ramp = nodes.new('ShaderNodeValToRGB')
ramp.color_ramp.elements[0].color = (0.055, 0.016, 0.006, 1)
ramp.color_ramp.elements[1].color = (0.30, 0.125, 0.048, 1)
links.new(tex.outputs['Fac'], ramp.inputs[0])
links.new(ramp.outputs[0], nodes.get('Principled BSDF').inputs['Base Color'])
black = material('Satin black metal', (0.019, 0.023, 0.029), 0.7, 0.3)
brass = material('Brushed brass', (0.55, 0.34, 0.10), 0.8, 0.32)
leather = material('Reading mat', (0.035, 0.055, 0.049), roughness=0.75)
paper = material('Ivory paper', (0.88, 0.85, 0.72), roughness=0.9)
ink = material('Printed text', (0.06, 0.075, 0.07), roughness=0.9)
foam = material('Microphone foam', (0.01, 0.012, 0.015), roughness=0.98)
floor = material('Floor', (0.24, 0.27, 0.29), roughness=0.8)
box('Floor', (0, 0, -0.065), (10, 10, 0.12), floor)
box('Weighted base', (0, 0, 0.07), (0.95, 0.76, 0.14), black, 0.045)
box('Walnut base cap', (0, 0, 0.16), (0.86, 0.67, 0.06), wood)
box('Front fascia', (0, -0.24, 0.76), (0.68, 0.075, 1.17), wood)
for x in [-0.325, 0.325]:
    box('Side upright', (x, 0.005, 0.76), (0.06, 0.47, 1.17), wood)
box('Interior shelf', (0, 0.005, 0.77), (0.60, 0.44, 0.045), wood)
box('Lower shelf', (0, 0.005, 0.27), (0.60, 0.44, 0.045), wood)
for x in [-0.265, 0.265]:
    box('Fascia brass inlay', (x, -0.281, 0.77), (0.009, 0.005, 0.94), brass, 0.002)
box('Front emblem plate', (0, -0.286, 0.99), (0.29, 0.012, 0.18), brass)
bpy.ops.object.text_add(location=(0, -0.295, 0.99), rotation=(math.pi/2, 0, 0))
t = bpy.context.object
t.name = 'LECTURE emblem'
t.data.body = 'LECTURE'
t.data.align_x = 'CENTER'
t.data.align_y = 'CENTER'
t.data.size = 0.042
t.data.extrude = 0.0006
t.data.materials.append(black)

# The reader stands on +Y; the reading surface slopes down toward them.
angle = math.radians(-15)
center = Vector((0, 0, 1.40))
from mathutils import Matrix
rot = Matrix.Rotation(angle, 3, 'X')
def on_top(x, y, z):
    return center + rot @ Vector((x, y, z))
box('Sloped reading surface', center, (0.96, 0.73, 0.065), wood, 0.02, (angle, 0, 0))
box('Inset reading mat', on_top(0, 0, 0.037), (0.76, 0.55, 0.007), leather, 0.015, (angle, 0, 0))
box('Raised paper retaining lip', on_top(0, 0.325, 0.068), (0.88, 0.035, 0.073), wood, 0.01, (angle, 0, 0))
box('Lip brass edge', on_top(0, 0.325, 0.106), (0.86, 0.038, 0.006), brass, 0.002, (angle, 0, 0))
box('Lecture notes', on_top(0.06, 0.025, 0.045), (0.31, 0.40, 0.005), paper, 0.002, (angle, 0, 0))
for i in range(12):
    width = 0.245 if i % 4 else 0.17
    box('Printed note line', on_top(0.045, -0.13 + i*0.025, 0.048), (width, 0.002, 0.0008), ink, 0, (angle, 0, 0))
mount = on_top(-0.35, -0.23, 0.04)
rod('Microphone mounting socket', mount, mount + Vector((0, 0, 0.045)), 0.04, black)
points = [mount + Vector((0, 0, 0.035)), Vector((-0.35, -0.23, 1.69)), Vector((-0.30, -0.12, 1.88)), Vector((-0.20, 0.09, 1.94))]
curve = bpy.data.curves.new('Gooseneck curve', 'CURVE')
curve.dimensions = '3D'
curve.resolution_u = 24
curve.bevel_depth = 0.012
curve.bevel_resolution = 4
spline = curve.splines.new('BEZIER')
spline.bezier_points.add(len(points)-1)
for p, co in zip(spline.bezier_points, points):
    p.co = co
    p.handle_left_type = 'AUTO'
    p.handle_right_type = 'AUTO'
o = bpy.data.objects.new('Flexible microphone gooseneck', curve)
bpy.context.collection.objects.link(o)
o.data.materials.append(black)
end = points[-1]
direction = Vector((0.25, 0.93, 0.12)).normalized()
rod('Microphone barrel', end, end + direction*0.11, 0.023, black)
bpy.ops.mesh.primitive_uv_sphere_add(segments=32, ring_count=16, location=end + direction*0.12)
o = bpy.context.object
o.name = 'Foam microphone capsule'
o.scale = (0.032, 0.032, 0.059)
o.rotation_euler = direction.to_track_quat('Z', 'Y').to_euler()
o.data.materials.append(foam)
for p in o.data.polygons:
    p.use_smooth = True

scene = bpy.context.scene
scene.world.color = (0.18, 0.18, 0.18)
for loc, power, size in [((2, -3, 5), 650, 4), ((-3, 1, 3), 450, 3)]:
    bpy.ops.object.light_add(type='AREA', location=loc)
    o = bpy.context.object
    o.data.energy = power
    o.data.size = size
    o.rotation_euler = (Vector((0, 0, 1)) - o.location).to_track_quat('-Z', 'Y').to_euler()
bpy.ops.object.camera_add(location=(2.8, -3.6, 3.0))
camera = bpy.context.object
camera.rotation_euler = (Vector((0, 0, 0.98)) - camera.location).to_track_quat('-Z', 'Y').to_euler()
camera.data.type = 'ORTHO'
camera.data.ortho_scale = 2.8
scene.camera = camera
scene.render.engine = 'CYCLES'
scene.render.resolution_x = 1100
scene.render.resolution_y = 1300
scene.render.resolution_percentage = 100
