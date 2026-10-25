import bpy
import math
from mathutils import Vector

# Standalone scene: the fireplace faces negative Y.
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)

def material(name, color, roughness=0.6, metallic=0.0):
    m = bpy.data.materials.new(name)
    m.diffuse_color = (*color, 1)
    m.use_nodes = True
    bs = m.node_tree.nodes.get('Principled BSDF')
    bs.inputs['Base Color'].default_value = (*color, 1)
    bs.inputs['Roughness'].default_value = roughness
    bs.inputs['Metallic'].default_value = metallic
    return m

def box(name, loc, size, mat, bevel=0.0):
    bpy.ops.mesh.primitive_cube_add(size=1, location=loc)
    obj = bpy.context.object
    obj.name = name
    obj.dimensions = size
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    obj.data.materials.append(mat)
    if bevel:
        mod = obj.modifiers.new('Soft edges', 'BEVEL')
        mod.width = bevel
        mod.segments = 3
        obj.modifiers.new('Weighted normals', 'WEIGHTED_NORMAL')
    return obj

def cylinder_between(name, start, end, radius, mat, vertices=16):
    a, b = Vector(start), Vector(end)
    bpy.ops.mesh.primitive_cylinder_add(vertices=vertices, radius=radius,
                                      depth=(b-a).length, location=(a+b)/2)
    obj = bpy.context.object
    obj.name = name
    obj.rotation_euler = (b-a).to_track_quat('Z', 'Y').to_euler()
    obj.data.materials.append(mat)
    return obj

stone = material('Warm limestone', (0.61, 0.56, 0.46))
brick = material('Firebrick', (0.23, 0.105, 0.065))
mortar = material('Recessed dark mortar', (0.085, 0.075, 0.065))
slate = material('Slate hearth', (0.095, 0.115, 0.125))
wood = material('Oak mantel', (0.24, 0.105, 0.038))
bark = material('Dark log bark', (0.12, 0.055, 0.022))
endgrain = material('Cut timber ends', (0.56, 0.32, 0.12))
ringmat = material('Growth rings', (0.29, 0.14, 0.046))
iron = material('Blackened iron grate', (0.035, 0.04, 0.045), 0.4, 0.7)
wall = material('Plaster wall', (0.77, 0.74, 0.67))
floor = material('Neutral floor', (0.32, 0.29, 0.25))

box('Room floor', (0, 0, -0.08), (10, 8, 0.16), floor)
box('Room wall', (0, 1.14, 2.35), (8, 0.2, 4.7), wall)
box('Chimney breast', (0, 0.59, 2.13), (3.05, 0.86, 4.26), wall, 0.025)
box('Raised hearth foundation', (0, -0.3, 0.12), (3.65, 2.0, 0.24), stone, 0.04)
box('Hearth slate cap', (0, -0.3, 0.275), (3.8, 2.12, 0.09), slate, 0.025)
box('Firebox rear mortar', (0, 0.065, 1.2), (2.03, 0.15, 1.77), mortar)
for row in range(7):
    count = 4 if row % 2 == 0 else 5
    width = 2.0 / count
    for col in range(count):
        box(f'Rear firebrick {row}-{col}',
            (-1 + width*(col+0.5), -0.025, 0.44 + row*0.24),
            (width-0.015, 0.065, 0.22), brick, 0.007)
for sign, label in [(-1, 'Left'), (1, 'Right')]:
    box(label+' stone jamb', (sign*1.22, -0.3, 1.21), (0.46, 1.02, 1.78), stone, 0.025)
    box(label+' jamb foot', (sign*1.22, -0.33, 0.44), (0.57, 1.1, 0.24), stone, 0.018)
    box(label+' capital', (sign*1.22, -0.34, 2.02), (0.59, 1.1, 0.18), stone, 0.018)
    box(label+' mantel corbel', (sign*1.2, -0.5, 2.2), (0.25, 0.42, 0.27), wood, 0.02)
box('Stone lintel', (0, -0.3, 2.19), (2.95, 1.02, 0.24), stone, 0.025)
box('Mantel lower molding', (0, -0.31, 2.365), (3.15, 1.15, 0.12), wood, 0.025)
box('Thick overhanging mantel shelf', (0, -0.34, 2.51), (3.55, 1.38, 0.2), wood, 0.035)

for x in [-0.69, 0.69]:
    for y in [-0.72, -0.18]:
        box('Grate foot', (x, y, 0.43), (0.07, 0.07, 0.22), iron, 0.008)
for y in [-0.72, -0.18]:
    box('Grate cross rail', (0, y, 0.55), (1.6, 0.065, 0.07), iron, 0.008)
for i in range(7):
    x = -0.72 + i*0.24
    box(f'Grate support bar {i}', (x, -0.45, 0.59), (0.045, 0.67, 0.055), iron, 0.006)
    cylinder_between(f'Grate front finger {i}', (x, -0.78, 0.57), (x, -0.87, 0.8), 0.023, iron)
# Logs run into the opening, exposing their cut ends to the viewer.
for i, (x, z, r) in enumerate([(-0.43, 0.78, 0.17), (0, 0.78, 0.18),
                               (0.43, 0.78, 0.17), (-0.22, 1.07, 0.17),
                               (0.22, 1.07, 0.17), (0, 1.35, 0.16)]):
    front = -0.77 + (i % 3)*0.035
    cylinder_between(f'Stacked log {i}', (x, front, z), (x, -0.11, z), r, bark)
    cylinder_between(f'Cut end {i}', (x, front-0.012, z), (x, front-0.003, z), r*0.9, endgrain)
    for fraction in [0.36, 0.65]:
        bpy.ops.mesh.primitive_torus_add(major_segments=24, minor_segments=6,
            location=(x, front-0.014, z), rotation=(math.pi/2, 0, 0),
            major_radius=r*fraction, minor_radius=0.004)
        obj = bpy.context.object
        obj.name = f'Log {i} growth ring {fraction}'
        obj.data.materials.append(ringmat)

scene = bpy.context.scene
scene.world.color = (0.25, 0.25, 0.25)
bpy.ops.object.light_add(type='AREA', location=(1, -4, 6))
bpy.context.object.name = 'Large soft key'
bpy.context.object.data.energy = 1100
bpy.context.object.data.shape = 'DISK'
bpy.context.object.data.size = 5
bpy.context.object.rotation_euler = (Vector((0, 0, 1.4))-bpy.context.object.location).to_track_quat('-Z', 'Y').to_euler()
bpy.ops.object.camera_add(location=(5, -7, 4.4))
cam = bpy.context.object
cam.name = 'Fireplace camera'
cam.rotation_euler = (Vector((0, -0.15, 1.8))-cam.location).to_track_quat('-Z', 'Y').to_euler()
cam.data.type = 'ORTHO'
cam.data.ortho_scale = 6.3
scene.camera = cam
scene.render.resolution_x = 1000
scene.render.resolution_y = 1000
scene.render.resolution_percentage = 100
