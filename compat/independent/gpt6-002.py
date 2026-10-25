import bpy
from mathutils import Vector
from math import sin, cos, pi

bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)

def material(name, rgb, roughness=0.45):
    m = bpy.data.materials.new(name)
    m.diffuse_color = (*rgb, 1)
    m.use_nodes = True
    bs = m.node_tree.nodes.get('Principled BSDF')
    bs.inputs['Base Color'].default_value = (*rgb, 1)
    bs.inputs['Roughness'].default_value = roughness
    return m

def box(name, pos, size, mat, bevel=0.02, angle=0):
    bpy.ops.mesh.primitive_cube_add(size=1, location=pos)
    ob = bpy.context.object
    ob.name = name
    ob.dimensions = size
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    ob.rotation_euler.z = angle
    ob.data.materials.append(mat)
    mod = ob.modifiers.new('Rounded joinery edges', 'BEVEL')
    mod.width = bevel
    mod.segments = 3
    ob.modifiers.new('Weighted normals', 'WEIGHTED_NORMAL')
    return ob

oak = material('Natural oak', (0.57, 0.34, 0.15))
endwood = material('Oak frame', (0.36, 0.19, 0.075))
fabric = material('Sage seat upholstery', (0.23, 0.34, 0.28), 0.9)
floor = material('Warm pale floor', (0.66, 0.62, 0.55), 0.8)
ceramic = material('Ivory ceramic', (0.85, 0.84, 0.75), 0.24)

box('Dining tabletop', (0, 0, 0.77), (1.75, 1.02, 0.075), oak, 0.035)
for x in (-0.73, 0.73):
    for y in (-0.365, 0.365):
        box('Table leg', (x, y, 0.355), (0.085, 0.085, 0.71), endwood, 0.012)
for y in (-0.365, 0.365):
    box('Table long apron', (0, y, 0.66), (1.48, 0.045, 0.14), endwood, 0.008)
for x in (-0.73, 0.73):
    box('Table end apron', (x, 0, 0.66), (0.045, 0.74, 0.14), endwood, 0.008)

# Each chair's back is local +Y; rotate the pair across the table.
def chair(name, cx, cy, angle):
    def part(label, p, size, mat, bevel=0.012):
        x, y, z = p
        pos = (cx+x*cos(angle)-y*sin(angle), cy+x*sin(angle)+y*cos(angle), z)
        return box(name+' | '+label, pos, size, mat, bevel, angle)
    part('seat frame', (0, 0, 0.43), (0.47, 0.47, 0.075), endwood)
    part('upholstered cushion', (0, -0.01, 0.484), (0.445, 0.425, 0.065), fabric, 0.03)
    for x in (-0.185, 0.185):
        part('front leg', (x, -0.18, 0.21), (0.052, 0.052, 0.42), endwood)
        part('rear leg and back post', (x, 0.19, 0.475), (0.052, 0.055, 0.95), endwood)
        part('side stretcher', (x, 0, 0.19), (0.031, 0.38, 0.038), endwood, 0.006)
    part('front stretcher', (0, -0.18, 0.19), (0.38, 0.032, 0.038), endwood, 0.006)
    part('back top rail', (0, 0.19, 0.93), (0.43, 0.065, 0.09), oak)
    part('back lower rail', (0, 0.19, 0.60), (0.38, 0.045, 0.055), endwood)
    for i in range(3):
        part('back slat '+str(i+1), ((i-1)*0.105, 0.19, 0.755), (0.063, 0.034, 0.26), oak, 0.009)

for i, x in enumerate((-0.47, 0.47)):
    chair('North chair '+str(i+1), x, 0.91, 0)
    chair('South chair '+str(i+1), x, -0.91, pi)

# A restrained centerpiece provides scale without hiding the furniture.
bpy.ops.mesh.primitive_uv_sphere_add(segments=24, ring_count=12, radius=1, location=(0, 0, 0.865))
bowl = bpy.context.object
bowl.name = 'Low ceramic centerpiece'
bowl.scale = (0.145, 0.145, 0.055)
bowl.data.materials.append(ceramic)
for poly in bowl.data.polygons:
    poly.use_smooth = True
box('Floor', (0, 0, -0.055), (6, 6, 0.1), floor, 0.02)
bpy.ops.object.camera_add(location=(3.5, -4.0, 3.2))
cam = bpy.context.object
cam.name = 'Dining set camera'
cam.rotation_euler = (Vector((0, 0, 0.43))-cam.location).to_track_quat('-Z', 'Y').to_euler()
cam.data.type = 'ORTHO'
cam.data.ortho_scale = 3.7
bpy.context.scene.camera = cam
bpy.ops.object.light_add(type='AREA', location=(-2, -2, 5))
bpy.context.object.data.energy = 700
bpy.context.object.data.size = 4
bpy.context.scene.world.color = (0.25, 0.25, 0.25)
