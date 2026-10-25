import bpy
from mathutils import Vector
from math import pi, sin, cos

# Independent outdoor basketball goal with a regulation-height rim.
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)

def material(name, color, metallic=0.0, roughness=0.45):
    mat = bpy.data.materials.new(name)
    mat.diffuse_color = (*color, 1)
    mat.use_nodes = True
    node = mat.node_tree.nodes.get('Principled BSDF')
    node.inputs['Base Color'].default_value = (*color, 1)
    node.inputs['Metallic'].default_value = metallic
    node.inputs['Roughness'].default_value = roughness
    return mat

steel = material('Graphite powder-coated steel', (0.055, 0.075, 0.095), 0.65)
boardmat = material('Ivory composite backboard', (0.86, 0.89, 0.88))
orange = material('Orange enamel rim', (0.95, 0.19, 0.025), 0.35)
white = material('White nylon net and court paint', (0.93, 0.94, 0.9))
black = material('Backboard target markings', (0.035, 0.045, 0.055))
concrete = material('Concrete footing', (0.43, 0.44, 0.42))
court = material('Blue green court surface', (0.08, 0.23, 0.27))

 def_placeholder = None

def box(name, location, dimensions, mat, bevel=0.01):
    bpy.ops.mesh.primitive_cube_add(size=1, location=location)
    obj = bpy.context.object
    obj.name = name
    obj.dimensions = dimensions
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    obj.data.materials.append(mat)
    if bevel:
        mod = obj.modifiers.new('Rounded manufactured edges', 'BEVEL')
        mod.width = bevel
        mod.segments = 2
        obj.modifiers.new('Weighted normals', 'WEIGHTED_NORMAL')
    return obj

def beam(name, a, b, width, depth, mat):
    delta = Vector(b) - Vector(a)
    obj = box(name, (Vector(a) + Vector(b)) / 2, (width, depth, delta.length), mat)
    obj.rotation_mode = 'QUATERNION'
    obj.rotation_quaternion = delta.to_track_quat('Z', 'Y')
    return obj

def cord(name, points, radius, mat, cyclic=False):
    data = bpy.data.curves.new(name, 'CURVE')
    data.dimensions = '3D'
    data.bevel_depth = radius
    data.bevel_resolution = 2
    spline = data.splines.new('POLY')
    spline.points.add(len(points) - 1)
    for point, xyz in zip(spline.points, points):
        point.co = (*xyz, 1)
    spline.use_cyclic_u = cyclic
    obj = bpy.data.objects.new(name, data)
    bpy.context.collection.objects.link(obj)
    obj.data.materials.append(mat)
    return obj

box('Court slab', (0, -1.7, -0.06), (6, 7, 0.12), court)
box('Raised concrete footing', (0, 0.95, 0.09), (0.7, 0.7, 0.18), concrete)
box('Steel base plate', (0, 0.95, 0.205), (0.46, 0.46, 0.05), steel)
box('Square support pole', (0, 0.95, 1.91), (0.18, 0.18, 3.4), steel)
for x in (-0.17, 0.17):
    for y in (0.78, 1.12):
        bpy.ops.mesh.primitive_cylinder_add(vertices=6, radius=0.027, depth=0.03, location=(x, y, 0.245))
        bpy.context.object.name = 'Foundation anchor nut'
        bpy.context.object.data.materials.append(steel)
beam('Top cantilever arm', (0, 0.95, 3.58), (0, 0.08, 3.58), 0.13, 0.13, steel)
beam('Cantilever diagonal brace', (0, 0.95, 2.68), (0, 0.12, 3.45), 0.085, 0.085, steel)
box('Backboard rear cross rail', (0, 0.10, 3.56), (1.5, 0.10, 0.09), steel)
box('Backboard', (0, 0, 3.565), (1.8, 0.10, 1.05), boardmat, 0.018)
for x in (-0.88, 0.88):
    box('Backboard vertical border', (x, -0.057, 3.565), (0.035, 0.012, 1.01), black, 0)
for z in (3.06, 4.07):
    box('Backboard horizontal border', (0, -0.057, z), (1.79, 0.012, 0.035), black, 0)
for x in (-0.295, 0.295):
    box('Target rectangle side', (x, -0.065, 3.30), (0.025, 0.014, 0.45), black, 0)
for z in (3.0875, 3.5125):
    box('Target rectangle horizontal', (0, -0.065, z), (0.615, 0.014, 0.025), black, 0)
box('Rim mounting plate', (0, -0.085, 3.10), (0.18, 0.055, 0.18), orange)
box('Rim mounting arm', (0, -0.215, 3.05), (0.12, 0.25, 0.045), orange)
bpy.ops.mesh.primitive_torus_add(major_segments=64, minor_segments=10, location=(0, -0.55, 3.05), major_radius=0.23, minor_radius=0.009)
bpy.context.object.name = 'Basketball rim'
bpy.context.object.data.materials.append(orange)
for polygon in bpy.context.object.data.polygons:
    polygon.use_smooth = True

# Two families of opposing diagonal cords form an open diamond net.
for family in (-1, 1):
    for i in range(12):
        points = []
        for level in range(6):
            t = level / 5
            angle = 2 * pi * i / 12 + family * level * pi / 12
            radius = 0.23 - 0.075 * min(t * 1.6, 1)
            points.append((radius * cos(angle), -0.55 + radius * sin(angle), 3.04 - 0.43 * t))
        cord('Net diagonal %d %02d' % (family, i), points, 0.0025, white)
cord('Net bottom binding', [(0.155 * cos(i * 2 * pi / 48), -0.55 + 0.155 * sin(i * 2 * pi / 48), 2.61) for i in range(48)], 0.003, white, True)
for x in (-1.8, 1.8):
    box('Painted lane edge', (x, -1.9, 0.003), (0.045, 4.8, 0.006), white, 0)
box('Painted baseline', (0, 0.5, 0.003), (5.8, 0.045, 0.006), white, 0)
box('Painted free throw line', (0, -4.3, 0.003), (3.6, 0.045, 0.006), white, 0)

bpy.context.scene.world = bpy.data.worlds.new('Outdoor ambient')
bpy.context.scene.world.use_nodes = True
bpy.context.scene.world.node_tree.nodes['Background'].inputs[1].default_value = 0.65
bpy.ops.object.light_add(type='AREA', location=(1, -3, 7))
bpy.context.object.data.energy = 1400
bpy.context.object.data.size = 5
bpy.ops.object.camera_add(location=(6, -9, 5.7))
camera = bpy.context.object
camera.name = 'Basketball goal overview'
camera.rotation_euler = (Vector((0, -1, 2)) - camera.location).to_track_quat('-Z', 'Y').to_euler()
camera.data.type = 'ORTHO'
camera.data.ortho_scale = 7.8
bpy.context.scene.camera = camera
bpy.context.scene.render.resolution_x = 1100
bpy.context.scene.render.resolution_y = 1100
bpy.context.scene.render.resolution_percentage = 100
