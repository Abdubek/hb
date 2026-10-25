import bpy
from mathutils import Vector

bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)

def material(name, color, metallic=0.0, roughness=0.4):
    mat = bpy.data.materials.new(name)
    mat.diffuse_color = (*color, 1)
    mat.use_nodes = True
    shader = mat.node_tree.nodes.get('Principled BSDF')
    shader.inputs['Base Color'].default_value = (*color, 1)
    shader.inputs['Metallic'].default_value = metallic
    shader.inputs['Roughness'].default_value = roughness
    return mat

def box(name, location, dimensions, mat, bevel=0.03):
    bpy.ops.mesh.primitive_cube_add(size=1, location=location)
    obj = bpy.context.object
    obj.name = name
    obj.dimensions = dimensions
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    obj.data.materials.append(mat)
    if bevel:
        mod = obj.modifiers.new('Edge radii', 'BEVEL')
        mod.width = bevel
        mod.segments = 3
        obj.modifiers.new('Weighted normals', 'WEIGHTED_NORMAL')
    return obj

def cylinder(name, start, end, radius, mat):
    a, b = Vector(start), Vector(end)
    bpy.ops.mesh.primitive_cylinder_add(vertices=32, radius=radius, depth=(b-a).length, location=(a+b)/2)
    obj = bpy.context.object
    obj.name = name
    obj.rotation_euler = (b-a).to_track_quat('Z', 'Y').to_euler()
    obj.data.materials.append(mat)
    bevel = obj.modifiers.new('Machined rims', 'BEVEL')
    bevel.width = min(radius * 0.15, 0.025)
    bevel.segments = 2
    obj.modifiers.new('Weighted normals', 'WEIGHTED_NORMAL')
    return obj

def beam(name, a, b, width, depth, mat):
    a, b = Vector(a), Vector(b)
    obj = box(name, (a+b)/2, (width, depth, (b-a).length), mat, 0.065)
    obj.rotation_euler = (b-a).to_track_quat('Z', 'Y').to_euler()
    return obj

def cable(name, points, mat):
    curve = bpy.data.curves.new(name, 'CURVE')
    curve.dimensions = '3D'
    curve.bevel_depth = 0.035
    curve.bevel_resolution = 2
    spline = curve.splines.new('BEZIER')
    spline.bezier_points.add(len(points)-1)
    for p, co in zip(spline.bezier_points, points):
        p.co = co
        p.handle_left_type = 'AUTO'
        p.handle_right_type = 'AUTO'
    obj = bpy.data.objects.new(name, curve)
    bpy.context.collection.objects.link(obj)
    curve.materials.append(mat)

metal = material('Mount graphite aluminum', (0.09, 0.11, 0.14), 0.75)
silver = material('Pivot hardware', (0.44, 0.49, 0.55), 0.8)
black = material('Monitor charcoal polymer', (0.018, 0.022, 0.03))
rubber = material('Cable and clamp pads', (0.009, 0.012, 0.015), roughness=0.75)
wood = material('Oak desktop', (0.48, 0.32, 0.19), roughness=0.65)
screen = material('Deep blue display', (0.025, 0.08, 0.15), roughness=0.24)
ui = material('Display blue panels', (0.09, 0.26, 0.40))
cyan = material('Display cyan accents', (0.18, 0.72, 0.82))
white = material('Display pale text strokes', (0.65, 0.81, 0.89))
box('Desk slab', (0, -0.65, -0.18), (11, 4.4, 0.36), wood, 0.08)
box('Clamp top saddle', (3.25, 1.18, 0.10), (0.9, 0.72, 0.16), metal)
box('Clamp protective top pad', (3.25, 1.18, 0.025), (0.78, 0.60, 0.045), rubber)
box('Clamp rear spine', (3.25, 1.69, -0.32), (0.7, 0.20, 1.02), metal)
box('Clamp lower jaw', (3.25, 1.31, -0.76), (0.7, 0.80, 0.16), metal)
cylinder('Clamp tightening screw', (3.25, 1.15, -1.03), (3.25, 1.15, -0.41), 0.085, silver)
cylinder('Under-desk pressure pad', (3.25, 1.15, -0.43), (3.25, 1.15, -0.36), 0.25, rubber)
cylinder('Clamp handle', (2.93, 1.15, -0.96), (3.57, 1.15, -0.96), 0.07, black)
cylinder('Vertical support post', (3.25, 1.18, 0.17), (3.25, 1.18, 2.65), 0.16, silver)
cylinder('Post swivel collar', (3.25, 1.18, 1.95), (3.25, 1.18, 2.42), 0.25, metal)
a, b, c = (3.25, 1.18, 2.23), (3.8, 1.02, 4.35), (0.0, 0.60, 4.8)
beam('Lower articulated lift arm', a, b, 0.34, 0.36, metal)
beam('Upper articulated reach arm', b, c, 0.34, 0.36, metal)
cylinder('Lift assist piston', (3.38, 0.80, 2.50), (3.77, 0.69, 3.80), 0.09, silver)
for name, p in [('Shoulder', a), ('Elbow', b), ('Tilt head', c)]:
    x, y, z = p
    cylinder(name + ' pivot', (x, y-0.29, z), (x, y+0.29, z), 0.26, metal)
    cylinder(name + ' visible axle cap', (x, y-0.32, z), (x, y-0.29, z), 0.13, silver)
box('Rear VESA mounting plate', (0, 0.31, 4.8), (1.08, 0.18, 1.08), metal)
box('Monitor rear shell', (-0.55, 0.015, 4.75), (6.2, 0.34, 3.55), black, 0.12)
box('Inset display glass', (-0.55, -0.168, 4.80), (5.90, 0.025, 3.18), screen, 0.035)
box('Display navigation sidebar', (-3.04, -0.19, 4.80), (0.65, 0.018, 2.95), ui)
box('Display header', (-0.14, -0.19, 6.07), (4.9, 0.018, 0.30), ui)
for i in range(3):
    box('Dashboard card %d' % i, (-1.66+i*1.53, -0.19, 5.40), (1.34, 0.018, 0.67), ui)
for i, h in enumerate([0.35, 0.70, 0.48, 1.0, 0.84, 1.25, 1.10]):
    box('Chart bar %d' % i, (-1.96+i*0.56, -0.20, 3.55+h/2), (0.27, 0.018, h), cyan, 0.015)
for i in range(5):
    box('Sidebar menu stroke %d' % i, (-3.04, -0.21, 5.75-i*0.42), (0.40, 0.015, 0.055), white, 0.01)
box('Power indicator', (2.27, -0.17, 3.10), (0.065, 0.025, 0.025), cyan, 0.008)
cable('Managed display cable', [(0.4,0.25,3.4), (0.5,0.7,4.48), (3.65,1.33,4.2), (3.05,1.46,2.1), (3.02,1.46,0.25), (3.04,1.85,-0.65)], rubber)

scene = bpy.context.scene
scene.world = bpy.data.worlds.new('Soft studio environment')
scene.world.use_nodes = True
scene.world.node_tree.nodes['Background'].inputs[1].default_value = 0.4
for loc, power, size in [((1,-6,10),1400,7), ((-5,3,8),1100,5)]:
    bpy.ops.object.light_add(type='AREA', location=loc)
    light = bpy.context.object
    light.data.energy = power
    light.data.size = size
    light.rotation_euler = (Vector((0,0,3))-light.location).to_track_quat('-Z','Y').to_euler()
bpy.ops.object.camera_add(location=(11,-15,10))
cam = bpy.context.object
cam.name = 'Monitor and articulated mount overview'
cam.rotation_euler = (Vector((0.3,0.2,2.7))-cam.location).to_track_quat('-Z','Y').to_euler()
cam.data.type = 'ORTHO'
cam.data.ortho_scale = 13.5
scene.camera = cam
scene.render.resolution_x = 1400
scene.render.resolution_y = 1100
scene.render.resolution_percentage = 100
