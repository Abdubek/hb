import bpy
from mathutils import Vector
from math import pi

bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)

def material(name, color, metallic=0.0, roughness=0.4):
    m = bpy.data.materials.new(name)
    m.diffuse_color = (*color, 1)
    m.use_nodes = True
    bs = m.node_tree.nodes.get('Principled BSDF')
    bs.inputs['Base Color'].default_value = (*color, 1)
    bs.inputs['Metallic'].default_value = metallic
    bs.inputs['Roughness'].default_value = roughness
    return m

red = material('Powder coated red', (0.48, 0.025, 0.035), 0.55)
dark = material('Dark drawer recesses', (0.025, 0.03, 0.037), 0.3)
steel = material('Brushed steel', (0.55, 0.61, 0.66), 0.85, 0.27)
rubber = material('Rubber', (0.017, 0.021, 0.025), 0, 0.7)
floor = material('Workshop floor', (0.22, 0.25, 0.28), 0, 0.8)

def box(name, location, scale, mat, bevel=0.025):
    bpy.ops.mesh.primitive_cube_add(size=1, location=location)
    obj = bpy.context.object
    obj.name = name
    obj.dimensions = scale
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    obj.data.materials.append(mat)
    if bevel:
        mod = obj.modifiers.new('Soft manufactured edges', 'BEVEL')
        mod.width = bevel
        mod.segments = 3
        obj.modifiers.new('Weighted normals', 'WEIGHTED_NORMAL')
    return obj

def rod(name, a, b, radius, mat, vertices=24):
    delta = Vector(b) - Vector(a)
    bpy.ops.mesh.primitive_cylinder_add(vertices=vertices, radius=radius,
        depth=delta.length, location=(Vector(a) + Vector(b)) / 2)
    obj = bpy.context.object
    obj.name = name
    obj.rotation_euler = delta.to_track_quat('Z', 'Y').to_euler()
    obj.data.materials.append(mat)
    mod = obj.modifiers.new('Edge easing', 'BEVEL')
    mod.width = 0.008
    mod.segments = 2
    obj.modifiers.new('Weighted normals', 'WEIGHTED_NORMAL')
    return obj

# Front of cabinet faces negative Y.
box('Cabinet carcass', (0, 0, 1.29), (2.25, 1.05, 1.77), red)
box('Drawer opening shadow', (0, -0.536, 1.30), (2.05, 0.025, 1.57), dark, 0.008)
box('Lower reinforced plinth', (0, 0, 0.43), (2.32, 1.10, 0.12), dark)
box('Left front stile', (-1.065, -0.555, 1.30), (0.09, 0.07, 1.64), red)
box('Right front stile', (1.065, -0.555, 1.30), (0.09, 0.07, 1.64), red)

bottom = 0.535
for i, height in enumerate([0.40, 0.32, 0.27, 0.23, 0.23]):
    z = bottom + height / 2
    box('Drawer %d front' % (i + 1), (0, -0.57, z), (1.99, 0.065, height - 0.022), red, 0.013)
    for x in [-0.75, 0.75]:
        box('Drawer %d pull mount' % (i + 1), (x, -0.622, z + 0.05), (0.055, 0.055, 0.055), steel, 0.007)
    rod('Drawer %d horizontal pull' % (i + 1), (-0.78, -0.663, z + 0.05), (0.78, -0.663, z + 0.05), 0.023, steel)
    box('Drawer %d label holder' % (i + 1), (0.86, -0.609, z - 0.06), (0.16, 0.012, 0.045), steel, 0.004)
    bottom += height

box('Top work surface', (0, 0, 2.215), (2.30, 1.10, 0.085), rubber)
for x in [-1.13, 1.13]:
    box('Raised side rim', (x, 0, 2.28), (0.05, 1.10, 0.10), red, 0.012)
box('Raised back rim', (0, 0.53, 2.28), (2.30, 0.05, 0.10), red, 0.012)
rod('Lock escutcheon', (0.94, -0.601, 2.095), (0.94, -0.625, 2.095), 0.036, steel)
box('Lock key slot', (0.94, -0.64, 2.095), (0.005, 0.006, 0.027), dark, 0)

# Four casters with metal forks and visible axle caps.
for x in [-0.87, 0.87]:
    for y in [-0.36, 0.36]:
        tag = 'Caster %.2f %.2f' % (x, y)
        box(tag + ' mounting plate', (x, y, 0.365), (0.27, 0.25, 0.045), steel, 0.01)
        rod(tag + ' swivel', (x, y, 0.29), (x, y, 0.365), 0.07, steel)
        for dx in [-0.091, 0.091]:
            box(tag + ' fork', (x + dx, y, 0.24), (0.035, 0.16, 0.19), steel, 0.012)
        rod(tag + ' rubber wheel', (x - 0.075, y, 0.175), (x + 0.075, y, 0.175), 0.165, rubber, 32)
        rod(tag + ' hub axle', (x - 0.12, y, 0.175), (x + 0.12, y, 0.175), 0.057, steel)

for y in [-0.36, 0.36]:
    rod('Push handle standoff', (1.10, y, 1.91), (1.40, y, 1.91), 0.035, steel)
rod('Side push handle', (1.40, -0.40, 1.91), (1.40, 0.40, 1.91), 0.04, steel)
rod('Push handle rubber grip', (1.40, -0.27, 1.91), (1.40, 0.27, 1.91), 0.052, rubber)
box('Ground', (0, 0, -0.045), (200, 200, 0.08), floor, 0)

bpy.ops.object.camera_add(location=(4.3, -5.8, 3.6))
cam = bpy.context.object
cam.name = 'Toolbox camera'
cam.rotation_euler = (Vector((0.1, 0, 1.13)) - cam.location).to_track_quat('-Z', 'Y').to_euler()
cam.data.type = 'ORTHO'
cam.data.ortho_scale = 4.2
bpy.context.scene.camera = cam
bpy.ops.object.light_add(type='AREA', location=(1, -3, 6))
bpy.context.object.data.energy = 1100
bpy.context.object.data.shape = 'DISK'
bpy.context.object.data.size = 5
bpy.context.scene.world.color = (0.25, 0.25, 0.25)
bpy.context.scene.render.resolution_x = 1000
bpy.context.scene.render.resolution_y = 1000
