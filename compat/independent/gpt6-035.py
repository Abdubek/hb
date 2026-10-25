import bpy
from math import radians
from mathutils import Vector

# Compact mechanical keyboard; one scene unit is one key pitch.
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)

def material(name, color, metallic=0.0, roughness=0.4):
    m = bpy.data.materials.new(name)
    m.diffuse_color = (*color, 1)
    m.use_nodes = True
    bsdf = m.node_tree.nodes.get('Principled BSDF')
    bsdf.inputs['Base Color'].default_value = (*color, 1)
    bsdf.inputs['Metallic'].default_value = metallic
    bsdf.inputs['Roughness'].default_value = roughness
    return m

def box(name, location, scale, mat, bevel=0.0):
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
        obj.modifiers.new('Weighted corner normals', 'WEIGHTED_NORMAL')
    return obj

def label(text, location, size, mat, name):
    curve = bpy.data.curves.new(name, 'FONT')
    curve.body = text
    curve.align_x = 'CENTER'
    curve.align_y = 'CENTER'
    curve.size = size
    curve.extrude = 0.001
    obj = bpy.data.objects.new(name, curve)
    bpy.context.collection.objects.link(obj)
    obj.location = location
    curve.materials.append(mat)
    return obj

case = material('Anodized midnight aluminum', (0.055, 0.075, 0.11), 0.65)
plate = material('Dark switch plate', (0.017, 0.023, 0.034), 0.3)
rubber = material('Black rubber', (0.015, 0.017, 0.02), roughness=0.8)
ink = material('Warm white legends', (0.92, 0.96, 1.0))
row_mats = [material('Coral keys', (0.8, 0.20, 0.17)),
            material('Ochre keys', (0.80, 0.46, 0.13)),
            material('Teal keys', (0.09, 0.47, 0.43)),
            material('Blue keys', (0.12, 0.33, 0.64)),
            material('Lavender keys', (0.40, 0.28, 0.59))]
desk = material('Warm desktop', (0.28, 0.22, 0.17), roughness=0.7)
box('Desktop', (0, 0, -0.23), (23, 13, 0.3), desk, 0.12)
box('Lower keyboard enclosure', (0, 0, 0.30), (15.65, 5.85, 0.58), case, 0.20)
box('Recessed switch plate', (0, 0, 0.60), (15.18, 5.38, 0.10), plate, 0.10)
for x in (-5.8, 5.8):
    for y in (-1.9, 1.9):
        box('Non-slip foot', (x, y, 0.015), (1.1, 0.55, 0.18), rubber, 0.07)

rows = [
    [('Esc',1)] + [(s,1) for s in '1234567890'] + [('-',1), ('=',1), ('Back',2)],
    [('Tab',1.5)] + [(s,1) for s in 'QWERTYUIOP'] + [('[',1), (']',1), ('\\',1.5)],
    [('Caps',1.75)] + [(s,1) for s in 'ASDFGHJKL'] + [(';',1), ("'",1), ('Enter',2.25)],
    [('Shift',2.25)] + [(s,1) for s in 'ZXCVBNM'] + [(',',1), ('.',1), ('/',1), ('Shift',2.75)],
    [('Ctrl',1.25), ('Win',1.25), ('Alt',1.25), ('',6.25), ('Alt',1.25), ('Fn',1.25), ('Ctrl',1.25), ('Menu',1.25)]
]
for r, row in enumerate(rows):
    cursor = -sum(width for _, width in row) / 2
    y = 2.0 - r
    for k, (legend, width) in enumerate(row):
        x = cursor + width / 2
        name = 'Row %d key %02d %s' % (r + 1, k + 1, legend or 'Spacebar')
        box(name + ' switch housing', (x, y, 0.71), (width - 0.20, 0.72, 0.20), rubber, 0.045)
        box(name, (x, y, 0.94), (width - 0.10, 0.88, 0.42), row_mats[r], 0.09)
        if legend:
            label(legend, (x, y + 0.08, 1.153), 0.19 if len(legend) > 1 else 0.25, ink, name + ' legend')
        cursor += width

box('USB-C port surround', (0, 2.934, 0.31), (0.95, 0.035, 0.29), rubber, 0.07)
box('USB-C inner tongue', (0, 2.955, 0.31), (0.59, 0.018, 0.08), plate, 0.02)
for x in (6.7, 6.95, 7.2):
    box('Status indicator', (x, 2.66, 0.659), (0.09, 0.09, 0.025), ink, 0.025)

world = bpy.data.worlds.new('Studio world')
bpy.context.scene.world = world
world.use_nodes = True
world.node_tree.nodes['Background'].inputs[0].default_value = (0.18, 0.22, 0.30, 1)
world.node_tree.nodes['Background'].inputs[1].default_value = 0.5
for name, loc, energy, size in [('Large softbox', (0, -3, 11), 1800, 9), ('Rim light', (3, 6, 7), 1200, 7)]:
    bpy.ops.object.light_add(type='AREA', location=loc)
    light = bpy.context.object
    light.name = name
    light.data.energy = energy
    light.data.shape = 'DISK'
    light.data.size = size
    light.rotation_euler = (Vector((0, 0, 0.5)) - light.location).to_track_quat('-Z', 'Y').to_euler()
bpy.ops.object.camera_add(location=(10, -13, 17))
camera = bpy.context.object
camera.name = 'Keyboard overview camera'
camera.rotation_euler = (Vector((0, 0, 0.45)) - camera.location).to_track_quat('-Z', 'Y').to_euler()
camera.data.type = 'ORTHO'
camera.data.ortho_scale = 19
bpy.context.scene.camera = camera
bpy.context.scene.render.resolution_x = 1400
bpy.context.scene.render.resolution_y = 950
bpy.context.scene.render.resolution_percentage = 100
