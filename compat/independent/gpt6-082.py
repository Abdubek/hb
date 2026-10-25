import bpy
import math
from mathutils import Vector

bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)

def material(name, color, metallic=0, roughness=0.45):
    m = bpy.data.materials.new(name)
    m.diffuse_color = (*color, 1)
    m.use_nodes = True
    bs = m.node_tree.nodes.get('Principled BSDF')
    bs.inputs['Base Color'].default_value = (*color, 1)
    bs.inputs['Metallic'].default_value = metallic
    bs.inputs['Roughness'].default_value = roughness
    return m

roof_mat = material('Pearl aluminum roof', (0.79, 0.84, 0.85), 0.65, 0.3)
wood = material('Honey oak soffit and seating', (0.48, 0.26, 0.105))
steel = material('Graphite column steel', (0.085, 0.115, 0.13), 0.7)
stone = material('Pale limestone platform', (0.71, 0.69, 0.61))
gravel = material('Fine warm gravel', (0.35, 0.36, 0.31))
soil = material('Planter soil', (0.095, 0.065, 0.035))
green = material('Ornamental planting', (0.18, 0.29, 0.12))

def box(name, loc, size, mat, bevel=0):
    bpy.ops.mesh.primitive_cube_add(size=1, location=loc)
    obj = bpy.context.object
    obj.name = name
    obj.dimensions = size
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    obj.data.materials.append(mat)
    if bevel:
        mod = obj.modifiers.new('Rounded edges', 'BEVEL')
        mod.width = bevel
        mod.segments = 2
        obj.modifiers.new('Weighted normals', 'WEIGHTED_NORMAL')
    return obj

def rod(name, a, b, radius, mat):
    d = Vector(b) - Vector(a)
    bpy.ops.mesh.primitive_cylinder_add(vertices=16, radius=radius, depth=d.length,
                                      location=(Vector(a)+Vector(b))/2)
    obj = bpy.context.object
    obj.name = name
    obj.rotation_euler = d.to_track_quat('Z', 'Y').to_euler()
    obj.data.materials.append(mat)
    for p in obj.data.polygons:
        p.use_smooth = True
    return obj

def height(x):
    return 4.65 + 1.15 * math.cos(math.pi*x/12)

def curved_strip(name, y0, y1, thickness, offset, mat):
    verts, faces = [], []
    steps = 48
    for i in range(steps+1):
        x = -6 + 12*i/steps
        z = height(x) + offset
        verts.extend([(x, y0, z), (x, y1, z),
                      (x, y0, z+thickness), (x, y1, z+thickness)])
    for i in range(steps):
        a, b = 4*i, 4*(i+1)
        faces.extend([(a, a+1, b+1, b), (a+2, b+2, b+3, a+3),
                      (a, b, b+2, a+2), (a+1, a+3, b+3, b+1)])
    faces.extend([(0, 2, 3, 1), (4*steps, 4*steps+1, 4*steps+3, 4*steps+2)])
    mesh = bpy.data.meshes.new(name)
    mesh.from_pydata(verts, [], faces)
    mesh.update()
    obj = bpy.data.objects.new(name, mesh)
    bpy.context.collection.objects.link(obj)
    obj.data.materials.append(mat)
    return obj

box('Landscape ground', (0, 0, -0.2), (23, 19, 0.3), gravel, 0.15)
box('Raised pavilion plinth', (0, 0, 0.16), (13.2, 9.2, 0.5), stone, 0.07)
box('Lower entrance step', (0, -5.25, 0.025), (5.6, 1.2, 0.15), stone, 0.03)
box('Upper entrance step', (0, -4.85, 0.16), (5.6, 0.6, 0.15), stone, 0.03)
for x in range(-6, 7, 2):
    box('Platform paving joint', (x, 0, 0.414), (0.018, 9, 0.008), gravel)
for y in (-3, -1, 1, 3):
    box('Platform cross joint', (0, y, 0.414), (13, 0.018, 0.008), gravel)
curved_strip('Continuous barrel canopy shell', -4.2, 4.2, 0.18, 0, roof_mat)
for i in range(34):
    y = -4.08 + i*0.245
    curved_strip('Curved oak soffit slat %02d' % i, y, y+0.18, 0.055, -0.06, wood)
for y in (-3.15, 3.15):
    curved_strip('Exposed curved support beam', y-0.085, y+0.085, 0.22, -0.29, steel)
    for x in (-4.9, 4.9):
        top = height(x)-0.29
        rod('Slim circular column', (x, y, 0.43), (x, y, top), 0.095, steel)
        box('Column base plate', (x, y, 0.445), (0.36, 0.36, 0.06), steel, 0.02)
        for dx in (-0.12, 0.12):
            for dy in (-0.12, 0.12):
                rod('Anchor bolt', (x+dx, y+dy, 0.47), (x+dx, y+dy, 0.51), 0.022, roof_mat)
for y in (-4.23, 4.17):
    curved_strip('Thin curved fascia', y, y+0.06, 0.25, -0.07, roof_mat)
for x in (-5.65, 5.65):
    box('Roof edge drainage channel', (x, 0, height(x)+0.2), (0.1, 8.3, 0.09), steel, 0.015)
for x in (-3.2, 3.2):
    for y in (0.6, 2.1):
        box('Bench steel support', (x, y, 0.64), (0.55, 0.12, 0.44), steel, 0.02)
    for i in range(4):
        box('Oak bench seat slat', (x-0.27+i*0.18, 1.35, 0.91), (0.15, 2.15, 0.12), wood, 0.025)
for x in (-5.5, 5.5):
    box('Rectangular planter', (x, 1.5, 0.75), (0.85, 2.1, 0.68), steel, 0.04)
    box('Recessed soil', (x, 1.5, 1.085), (0.73, 1.98, 0.035), soil)
    for j in range(7):
        y = 0.65+j*0.28
        for k in range(3):
            a = k*2.094+j
            rod('Stylized ornamental grass', (x, y, 1.09),
                (x+0.19*math.cos(a), y+0.18*math.sin(a), 1.55+0.12*(j%3)), 0.027, green)

world = bpy.data.worlds.new('Pavilion sky')
bpy.context.scene.world = world
world.use_nodes = True
world.node_tree.nodes['Background'].inputs[0].default_value = (0.72, 0.81, 0.92, 1)
world.node_tree.nodes['Background'].inputs[1].default_value = 0.6
bpy.ops.object.light_add(type='AREA', location=(1, -5, 12))
bpy.context.object.data.energy = 1800
bpy.context.object.data.size = 9
bpy.ops.object.light_add(type='SUN', location=(0, 0, 10))
bpy.context.object.rotation_euler = (0.45, -0.4, -0.5)
bpy.context.object.data.energy = 2
bpy.ops.object.camera_add(location=(16, -20, 12))
cam = bpy.context.object
cam.name = 'Pavilion architectural camera'
cam.rotation_euler = (Vector((0, 0, 2.5))-cam.location).to_track_quat('-Z', 'Y').to_euler()
cam.data.type = 'ORTHO'
cam.data.ortho_scale = 21
bpy.context.scene.camera = cam
bpy.context.scene.render.resolution_x = 1500
bpy.context.scene.render.resolution_y = 1100
bpy.context.scene.render.resolution_percentage = 100
