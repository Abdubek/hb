import bpy
from mathutils import Vector
from math import radians

bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)

def material(name, color, metallic=0.0, roughness=0.45):
    m = bpy.data.materials.new(name)
    m.diffuse_color = (*color, 1)
    m.use_nodes = True
    bs = m.node_tree.nodes.get('Principled BSDF')
    bs.inputs['Base Color'].default_value = (*color, 1)
    bs.inputs['Metallic'].default_value = metallic
    bs.inputs['Roughness'].default_value = roughness
    return m

def box(name, loc, size, mat, bevel=0.025):
    bpy.ops.mesh.primitive_cube_add(size=1, location=loc)
    ob = bpy.context.object
    ob.name = name
    ob.dimensions = size
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    ob.data.materials.append(mat)
    if bevel:
        mod = ob.modifiers.new('Soft manufactured edges', 'BEVEL')
        mod.width = bevel
        mod.segments = 3
        ob.modifiers.new('Weighted corner normals', 'WEIGHTED_NORMAL')
    return ob

def beam(name, start, end, width, depth, mat):
    a, b = Vector(start), Vector(end)
    ob = box(name, (a+b)/2, (width, depth, (b-a).length), mat)
    ob.rotation_euler = (b-a).to_track_quat('Z', 'Y').to_euler()
    return ob

wood = material('Warm oiled hardwood', (0.43, 0.19, 0.065))
iron = material('Charcoal powder coated steel', (0.055, 0.075, 0.07), 0.7)
steel = material('Stainless screw heads', (0.48, 0.51, 0.53), 0.85)
ground = material('Paving', (0.34, 0.36, 0.33), roughness=0.85)

# Front is negative Y. Overall width accommodates two adults.
for i in range(5):
    y = -0.265 + i * 0.1325
    box('Seat hardwood slat %02d' % (i+1), (0, y, 0.52), (1.72, 0.112, 0.055), wood, 0.012)
    for x in (-0.64, 0.64):
        bpy.ops.mesh.primitive_uv_sphere_add(segments=12, ring_count=6, radius=1, location=(x, y, 0.55))
        screw = bpy.context.object
        screw.name = 'Seat countersunk fastener'
        screw.scale = (0.012, 0.012, 0.003)
        screw.data.materials.append(steel)

for side, x in [('Left', -0.67), ('Right', 0.67)]:
    box(side+' seat bearer', (x, 0, 0.462), (0.07, 0.70, 0.075), iron)
    for label, y in [('front', -0.24), ('rear', 0.24)]:
        beam(side+' '+label+' leg', (x, y*1.25, 0.07), (x, y, 0.465), 0.065, 0.065, iron)
        box(side+' '+label+' foot', (x, y*1.25, 0.035), (0.15, 0.14, 0.04), iron, 0.015)
    beam(side+' back upright', (x, 0.27, 0.43), (x, 0.435, 1.11), 0.06, 0.055, iron)
    beam(side+' arm front post', (x, -0.22, 0.49), (x, -0.22, 0.755), 0.045, 0.045, iron)
    box(side+' hardwood armrest', (x, 0.025, 0.77), (0.10, 0.64, 0.06), wood, 0.025)

for i in range(4):
    z = 0.675 + i * 0.123
    y = 0.27 + (z-0.43)*0.165/0.68 - 0.039
    slat = box('Backrest slat %02d' % (i+1), (0, y, z), (1.72, 0.048, 0.103), wood, 0.012)
    slat.rotation_euler.x = radians(-13.6)
box('Underseat cross brace', (0, 0.12, 0.24), (1.36, 0.045, 0.06), iron, 0.012)
box('Paved display surface', (0, 0, -0.055), (5, 4, 0.10), ground, 0.03)

bpy.ops.object.camera_add(location=(2.8, -3.4, 2.15))
cam = bpy.context.object
cam.name = 'Bench presentation camera'
cam.rotation_euler = (Vector((0, 0.05, 0.55))-cam.location).to_track_quat('-Z', 'Y').to_euler()
cam.data.type = 'ORTHO'
cam.data.ortho_scale = 2.85
bpy.context.scene.camera = cam
bpy.ops.object.light_add(type='AREA', location=(0, -2, 4))
bpy.context.object.data.energy = 550
bpy.context.object.data.shape = 'DISK'
bpy.context.object.data.size = 4
bpy.context.scene.world.color = (0.22, 0.22, 0.22)
