import bpy
from math import pi
from mathutils import Vector

# Toy locomotive: forward is -X, track direction is X.
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)

def material(name, color, metallic=0.0):
    m = bpy.data.materials.new(name)
    m.diffuse_color = (*color, 1)
    m.use_nodes = True
    bs = m.node_tree.nodes.get('Principled BSDF')
    bs.inputs['Base Color'].default_value = (*color, 1)
    bs.inputs['Metallic'].default_value = metallic
    bs.inputs['Roughness'].default_value = 0.32
    return m

red = material('Cherry red enamel', (0.64, 0.035, 0.025))
black = material('Soft black iron', (0.035, 0.044, 0.052), 0.35)
brass = material('Warm brass', (0.86, 0.53, 0.12), 0.65)
blue = material('Cab blue', (0.045, 0.24, 0.46))
cream = material('Warm ivory', (0.92, 0.82, 0.58))
steel = material('Steel rods', (0.42, 0.48, 0.52), 0.7)
wood = material('Sleepers', (0.24, 0.12, 0.055))
ground = material('Display ground', (0.24, 0.31, 0.29))

def finish(obj, name, mat, bevel=0.04):
    obj.name = name
    obj.data.materials.append(mat)
    if bevel:
        mod = obj.modifiers.new('Rounded toy edges', 'BEVEL')
        mod.width = bevel
        mod.segments = 3
        obj.modifiers.new('Weighted normals', 'WEIGHTED_NORMAL')
    return obj

def box(name, loc, size, mat, bevel=0.04):
    bpy.ops.mesh.primitive_cube_add(size=1, location=loc)
    obj = bpy.context.object
    obj.dimensions = size
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    return finish(obj, name, mat, bevel)

def cylinder(name, loc, radius, depth, mat, axis='Z'):
    bpy.ops.mesh.primitive_cylinder_add(vertices=32, radius=radius, depth=depth, location=loc)
    obj = bpy.context.object
    obj.rotation_euler = {'X': (0, pi/2, 0), 'Y': (pi/2, 0, 0), 'Z': (0, 0, 0)}[axis]
    return finish(obj, name, mat, 0.025)

box('Display plinth', (0, 0, -0.14), (8.4, 4.1, 0.25), ground, 0.12)
for i in range(13):
    box('Track sleeper %02d' % i, (-3.6 + i*0.6, 0, 0.045), (0.25, 2.35, 0.13), wood)
for y in (-0.9, 0.9):
    box('Rail', (0, y, 0.17), (8, 0.11, 0.14), steel, 0.02)

box('Main red chassis', (0, 0, 1.04), (5.15, 1.8, 0.3), red)
for axle, x in enumerate((-1.65, -0.25, 1.25)):
    cylinder('Axle %d' % axle, (x, 0, 0.77), 0.1, 2.04, steel, 'Y')
    for side in (-1, 1):
        y = side*0.91
        cylinder('Black wheel tire', (x, y, 0.77), 0.53, 0.23, black, 'Y')
        cylinder('Red wheel face', (x, y + side*0.125, 0.77), 0.425, 0.045, red, 'Y')
        cylinder('Brass wheel hub', (x, y + side*0.17, 0.77), 0.13, 0.10, brass, 'Y')
        for angle in (0, pi/3, 2*pi/3):
            spoke = box('Ivory wheel spoke', (x, y + side*0.153, 0.77), (0.70, 0.035, 0.075), cream, 0.012)
            spoke.rotation_euler.y = angle
for side in (-1, 1):
    box('Side connecting rod', (-0.2, side*1.17, 0.64), (3.12, 0.09, 0.13), steel)
    for x in (-1.65, -0.25, 1.25):
        cylinder('Rod pin', (x, side*1.23, 0.64), 0.08, 0.06, brass, 'Y')

cylinder('Horizontal boiler', (-0.8, 0, 1.82), 0.65, 2.8, black, 'X')
for x in (-1.75, -0.65, 0.3):
    cylinder('Brass boiler band', (x, 0, 1.82), 0.672, 0.075, brass, 'X')
cylinder('Front smokebox door', (-2.23, 0, 1.82), 0.54, 0.10, red, 'X')
cylinder('Smokebox latch', (-2.30, 0, 1.82), 0.12, 0.09, brass, 'X')
cylinder('Chimney base', (-1.55, 0, 2.42), 0.27, 0.16, brass)
cylinder('Chimney stack', (-1.55, 0, 2.80), 0.19, 0.68, black)
cylinder('Chimney flared rim', (-1.55, 0, 3.14), 0.30, 0.17, black)
cylinder('Steam dome', (-0.2, 0, 2.47), 0.24, 0.36, brass)
cylinder('Headlamp housing', (-2.31, 0, 2.40), 0.20, 0.25, brass, 'X')
cylinder('Headlamp lens', (-2.45, 0, 2.40), 0.16, 0.025, cream, 'X')

box('Cab lower body', (1.40, 0, 1.49), (1.75, 1.65, 0.65), blue)
for x in (0.57, 2.23):
    for y in (-0.77, 0.77):
        box('Cab corner pillar', (x, y, 2.20), (0.14, 0.14, 1.0), blue)
for y in (-0.78, 0.78):
    box('Open window sill', (1.40, y, 1.85), (1.8, 0.15, 0.12), brass)
box('Cab roof', (1.40, 0, 2.79), (2.18, 2.07, 0.22), red, 0.10)
box('Driver bench', (1.87, 0, 1.96), (0.38, 1.22, 0.17), black)
box('Front buffer beam', (-2.63, 0, 1.03), (0.18, 2.12, 0.31), red)
for y in (-0.64, 0.64):
    cylinder('Front buffer', (-2.84, y, 1.04), 0.17, 0.31, black, 'X')
box('Rear coupling', (2.77, 0, 0.98), (0.5, 0.25, 0.14), black)

world = bpy.context.scene.world or bpy.data.worlds.new('World')
bpy.context.scene.world = world
world.use_nodes = True
world.node_tree.nodes['Background'].inputs[0].default_value = (0.22, 0.27, 0.34, 1)
world.node_tree.nodes['Background'].inputs[1].default_value = 0.5
bpy.ops.object.light_add(type='AREA', location=(-3, -4, 8))
bpy.context.object.data.energy = 1500
bpy.context.object.data.shape = 'DISK'
bpy.context.object.data.size = 6
bpy.ops.object.camera_add(location=(-8, -10, 6.4))
cam = bpy.context.object
cam.rotation_euler = (Vector((0, 0, 1.35)) - cam.location).to_track_quat('-Z', 'Y').to_euler()
cam.data.type = 'ORTHO'
cam.data.ortho_scale = 9.4
bpy.context.scene.camera = cam
bpy.context.scene.render.resolution_x = 1100
bpy.context.scene.render.resolution_y = 800
bpy.context.scene.render.resolution_percentage = 100
