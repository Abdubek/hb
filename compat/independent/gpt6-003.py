import bpy
from mathutils import Vector
from math import pi, sin, cos

bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)

def material(name, rgb, metal=0, rough=0.45):
    m = bpy.data.materials.new(name)
    m.diffuse_color = (*rgb, 1)
    m.use_nodes = True
    bs = m.node_tree.nodes.get('Principled BSDF')
    bs.inputs['Base Color'].default_value = (*rgb, 1)
    bs.inputs['Metallic'].default_value = metal
    bs.inputs['Roughness'].default_value = rough
    return m

def box(name, pos, size, mat, bevel=0.025):
    bpy.ops.mesh.primitive_cube_add(size=1, location=pos)
    ob = bpy.context.object
    ob.name = name
    ob.dimensions = size
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    ob.data.materials.append(mat)
    if bevel:
        mod = ob.modifiers.new('Edge bevel', 'BEVEL')
        mod.width = bevel
        mod.segments = 2
        ob.modifiers.new('Weighted normals', 'WEIGHTED_NORMAL')
    return ob

def rod(name, a, b, radius, mat, vertices=24):
    a, b = Vector(a), Vector(b)
    bpy.ops.mesh.primitive_cylinder_add(vertices=vertices, radius=radius, depth=(b-a).length, location=(a+b)/2)
    ob = bpy.context.object
    ob.name = name
    ob.rotation_euler = (b-a).to_track_quat('Z', 'Y').to_euler()
    ob.data.materials.append(mat)
    bevel = ob.modifiers.new('Rim bevel', 'BEVEL')
    bevel.width = min(radius*0.15, 0.015)
    bevel.segments = 2
    ob.modifiers.new('Weighted normals', 'WEIGHTED_NORMAL')
    return ob

shell = material('Expedition orange', (0.75, 0.27, 0.06), 0.25)
metal = material('Aluminum suspension', (0.36, 0.40, 0.44), 0.8)
dark = material('Graphite structural metal', (0.055, 0.07, 0.09), 0.65)
rubber = material('Tire rubber', (0.022, 0.028, 0.032), 0, 0.85)
glass = material('Optical blue glass', (0.02, 0.16, 0.26), 0.65, 0.15)
solar = material('Solar cells', (0.035, 0.075, 0.15), 0.55, 0.25)
ground = material('Sandy ground', (0.40, 0.32, 0.23), 0, 0.95)

box('Main chassis', (0, 0, 0.72), (1.68, 0.94, 0.30), shell, 0.075)
box('Underbody equipment bay', (0, 0, 0.53), (1.25, 0.77, 0.19), dark)
box('Deck perimeter', (0, 0, 0.90), (1.73, 1.01, 0.07), metal)
for i in range(4):
    for j in range(3):
        box('Solar cell %d-%d' % (i, j), (-0.61+i*0.40, -0.32+j*0.32, 0.945), (0.365, 0.29, 0.025), solar, 0.006)

# Six independent wheels, with visible outboard hubs and transverse axles.
for side in (-1, 1):
    y = side*0.72
    rod('Side suspension rocker', (-0.69, side*0.54, 0.49), (0.69, side*0.54, 0.49), 0.045, metal)
    for i, x in enumerate((-0.70, 0, 0.70)):
        label = ('Port' if side == 1 else 'Starboard')+' wheel '+str(i+1)
        rod(label+' suspension link', (x-0.12, side*0.47, 0.65), (x, side*0.62, 0.32), 0.043, metal)
        rod(label+' axle', (x, side*0.47, 0.32), (x, side*0.84, 0.32), 0.065, dark)
        rod(label+' tire', (x, y-0.125, 0.32), (x, y+0.125, 0.32), 0.30, rubber, 32)
        rod(label+' outer rim', (x, side*0.842, 0.32), (x, side*0.863, 0.32), 0.19, metal, 32)
        rod(label+' hub cap', (x, side*0.859, 0.32), (x, side*0.883, 0.32), 0.095, shell)
        for k in range(16):
            angle = k*2*pi/16
            tread = box(label+' tread '+str(k), (x+0.302*sin(angle), y, 0.32+0.302*cos(angle)), (0.082, 0.27, 0.027), rubber, 0.005)
            tread.rotation_euler.y = angle

rod('Sensor mast', (0.46, 0, 0.96), (0.46, 0, 1.60), 0.045, metal)
rod('Mast base collar', (0.46, 0, 0.94), (0.46, 0, 1.04), 0.10, dark)
box('Stereo sensor head', (0.46, 0, 1.65), (0.22, 0.48, 0.19), shell)
for y in (-0.145, 0.145):
    rod('Camera lens housing', (0.57, y, 1.65), (0.625, y, 1.65), 0.065, dark)
    rod('Camera optical face', (0.626, y, 1.65), (0.637, y, 1.65), 0.047, glass)
rod('Rear communications antenna', (-0.65, 0.30, 0.96), (-0.65, 0.30, 1.45), 0.013, dark, 12)
box('Front bumper', (0.91, 0, 0.62), (0.12, 1.01, 0.10), dark)
box('Terrain display slab', (0, 0, -0.07), (5, 4, 0.1), ground)
bpy.ops.object.camera_add(location=(3.2, -3.5, 2.6))
cam = bpy.context.object
cam.name = 'Rover camera'
cam.rotation_euler = (Vector((0, 0, 0.75))-cam.location).to_track_quat('-Z', 'Y').to_euler()
cam.data.type = 'ORTHO'
cam.data.ortho_scale = 3.25
bpy.context.scene.camera = cam
bpy.ops.object.light_add(type='AREA', location=(1, -3, 5))
bpy.context.object.data.energy = 800
bpy.context.object.data.size = 4
bpy.context.scene.world.color = (0.23, 0.23, 0.23)
