import bpy
import math
from mathutils import Vector

# Independent courtyard scene, dimensions in meters.
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)

def material(name, color, metallic=0.0, roughness=0.5):
    m = bpy.data.materials.new(name)
    m.diffuse_color = (*color, 1)
    m.use_nodes = True
    bs = m.node_tree.nodes.get('Principled BSDF')
    bs.inputs['Base Color'].default_value = (*color, 1)
    bs.inputs['Metallic'].default_value = metallic
    bs.inputs['Roughness'].default_value = roughness
    return m

stone = material('Warm limestone', (0.64, 0.57, 0.44))
paving = material('Ivory courtyard pavers', (0.78, 0.74, 0.64))
grout = material('Paving joints', (0.24, 0.26, 0.24))
soil = material('Dark potting soil', (0.095, 0.065, 0.035))
leaves = material('Clipped evergreen', (0.12, 0.28, 0.095))
wood = material('Oiled teak', (0.36, 0.16, 0.065))
metal = material('Dark bronze fittings', (0.09, 0.105, 0.09), 0.65)
water = material('Turquoise water', (0.055, 0.42, 0.47), 0.3, 0.16)
stream = material('Pale fountain streams', (0.40, 0.77, 0.81), 0.25, 0.12)

def finish(obj, name, mat, bevel=0):
    obj.name = name
    obj.data.materials.append(mat)
    if bevel:
        mod = obj.modifiers.new('Soft masonry edges', 'BEVEL')
        mod.width = bevel
        mod.segments = 2
        obj.modifiers.new('Weighted normals', 'WEIGHTED_NORMAL')
    return obj

def box(name, loc, size, mat, bevel=0.025):
    bpy.ops.mesh.primitive_cube_add(size=1, location=loc)
    obj = bpy.context.object
    obj.dimensions = size
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    return finish(obj, name, mat, bevel)

def cylinder(name, loc, radius, depth, mat):
    bpy.ops.mesh.primitive_cylinder_add(vertices=48, radius=radius, depth=depth, location=loc)
    return finish(bpy.context.object, name, mat, 0.025)

def ring(name, z, outer, inner, height, mat):
    verts, faces = [], []
    for radius, level in [(outer, z-height/2), (outer, z+height/2), (inner, z+height/2), (inner, z-height/2)]:
        verts.extend([(radius*math.cos(i*math.tau/64), radius*math.sin(i*math.tau/64), level) for i in range(64)])
    for band in range(4):
        for i in range(64):
            j = (i+1) % 64
            faces.append((band*64+i, band*64+j, ((band+1)%4)*64+j, ((band+1)%4)*64+i))
    mesh = bpy.data.meshes.new(name)
    mesh.from_pydata(verts, [], faces)
    mesh.update()
    obj = bpy.data.objects.new(name, mesh)
    bpy.context.collection.objects.link(obj)
    return finish(obj, name, mat, 0.02)

box('Courtyard foundation', (0, 0, -0.18), (14, 12, 0.36), grout)
for x in range(14):
    for y in range(12):
        box('Limestone paver %02d_%02d' % (x, y), (x-6.5, y-5.5, 0.025), (0.97, 0.97, 0.05), paving, 0.008)
for x in [-6.8, 6.8]:
    box('Side boundary wall', (x, 0, 0.55), (0.32, 12, 1.1), stone)
    box('Side wall coping', (x, 0, 1.13), (0.44, 12, 0.12), paving)
box('Rear boundary wall', (0, 5.8, 0.55), (13.6, 0.32, 1.1), stone)
cylinder('Fountain circular plinth', (0, 0, 0.14), 2.35, 0.22, stone)
cylinder('Watertight basin floor', (0, 0, 0.29), 2.12, 0.14, stone)
ring('Raised basin wall', 0.49, 2.16, 1.92, 0.48, stone)
ring('Wide polished basin coping', 0.76, 2.25, 1.87, 0.15, paving)
cylinder('Lower basin water surface', (0, 0, 0.61), 1.915, 0.025, water)
cylinder('Central pedestal foot', (0, 0, 0.69), 0.49, 0.22, stone)
cylinder('Central fountain column', (0, 0, 1.24), 0.22, 1.1, stone)
cylinder('Upper bowl bottom', (0, 0, 1.76), 0.86, 0.13, stone)
ring('Upper bowl raised rim', 1.91, 0.88, 0.75, 0.28, paving)
cylinder('Upper bowl water', (0, 0, 1.96), 0.75, 0.025, water)
cylinder('Bronze jet nozzle', (0, 0, 2.04), 0.065, 0.18, metal)
for i in range(8):
    a = i*math.tau/8
    curve = bpy.data.curves.new('Overflow arc', 'CURVE')
    curve.dimensions = '3D'
    curve.bevel_depth = 0.022
    curve.bevel_resolution = 2
    spline = curve.splines.new('POLY')
    spline.points.add(20)
    for j, point in enumerate(spline.points):
        t = j/20
        radius = 0.8+0.66*t
        point.co = (radius*math.cos(a), radius*math.sin(a), 1.98+0.18*t-1.53*t*t, 1)
    obj = bpy.data.objects.new('Falling water stream %d' % i, curve)
    bpy.context.collection.objects.link(obj)
    obj.data.materials.append(stream)
for x in [-4.7, 4.7]:
    for y in [-3.6, 3.6]:
        box('Planter base', (x, y, 0.18), (2.35, 1.75, 0.24), stone)
        for dx in [-1.05, 1.05]:
            box('Planter end wall', (x+dx, y, 0.57), (0.2, 1.65, 0.7), stone)
        for dy in [-0.73, 0.73]:
            box('Planter long wall', (x, y+dy, 0.57), (2.15, 0.2, 0.7), stone)
        box('Recessed soil', (x, y, 0.76), (1.94, 1.24, 0.1), soil)
        for dx in [-0.58, 0, 0.58]:
            bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=2, radius=0.64, location=(x+dx, y, 1.13))
            shrub = finish(bpy.context.object, 'Clipped planter shrub', leaves)
            shrub.scale = (0.82, 0.85, 0.86)
for x in [-4.8, 4.8]:
    for y in [-0.78, 0.78]:
        box('Bench bronze trestle', (x, y, 0.3), (0.62, 0.12, 0.5), metal)
    for dx in [-0.24, -0.08, 0.08, 0.24]:
        box('Bench teak seat slat', (x+dx, 0, 0.58), (0.13, 2.0, 0.09), wood)

bpy.ops.object.camera_add(location=(16, -20, 17))
camera = bpy.context.object
camera.name = 'Courtyard overview camera'
camera.rotation_euler = (Vector((0, 0, 0.4))-camera.location).to_track_quat('-Z', 'Y').to_euler()
camera.data.type = 'ORTHO'
camera.data.ortho_scale = 20.8
bpy.context.scene.camera = camera
bpy.ops.object.light_add(type='AREA', location=(1, -3, 12))
bpy.context.object.data.energy = 2200
bpy.context.object.data.shape = 'DISK'
bpy.context.object.data.size = 9
bpy.ops.object.light_add(type='SUN', rotation=(0.45, -0.5, -0.35))
bpy.context.object.data.energy = 2
scene = bpy.context.scene
scene.world = bpy.data.worlds.new('Courtyard sky')
scene.world.use_nodes = True
scene.world.node_tree.nodes['Background'].inputs[0].default_value = (0.55, 0.68, 0.8, 1)
scene.world.node_tree.nodes['Background'].inputs[1].default_value = 0.45
scene.render.resolution_x = 1200
scene.render.resolution_y = 1000
scene.render.resolution_percentage = 100
