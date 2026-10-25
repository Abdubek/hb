import bpy
from mathutils import Vector
from math import radians

# Independent scene: a rounded two-slot toaster with front-facing controls.
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)

def material(name, color, metallic=0.0, roughness=0.4):
    m = bpy.data.materials.new(name)
    m.diffuse_color = (*color, 1)
    m.use_nodes = True
    p = m.node_tree.nodes.get('Principled BSDF')
    p.inputs['Base Color'].default_value = (*color, 1)
    p.inputs['Metallic'].default_value = metallic
    p.inputs['Roughness'].default_value = roughness
    return m

cream = material('Warm ivory enamel', (0.78, 0.69, 0.51), 0.25)
steel = material('Brushed stainless steel', (0.55, 0.59, 0.63), 0.8, 0.28)
black = material('Charcoal polymer', (0.025, 0.031, 0.038))
dark = material('Dark slot interiors', (0.008, 0.009, 0.011), 0.1, 0.65)
red = material('Red cancel button', (0.62, 0.025, 0.018))
floor = material('Countertop', (0.24, 0.29, 0.32))

def box(name, location, scale, mat=None, bevel=0.0, apply=False):
    bpy.ops.mesh.primitive_cube_add(size=1, location=location)
    o = bpy.context.object
    o.name = name
    o.dimensions = scale
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    if mat:
        o.data.materials.append(mat)
    if bevel:
        b = o.modifiers.new('Soft manufactured edges', 'BEVEL')
        b.width = bevel
        b.segments = 5
        if apply:
            bpy.ops.object.modifier_apply(modifier=b.name)
    return o

def cylinder(name, location, radius, depth, mat):
    bpy.ops.mesh.primitive_cylinder_add(vertices=48, radius=radius, depth=depth,
                                      location=location, rotation=(radians(90), 0, 0))
    o = bpy.context.object
    o.name = name
    o.data.materials.append(mat)
    b = o.modifiers.new('Rounded rim', 'BEVEL')
    b.width = 0.025
    b.segments = 3
    o.modifiers.new('Weighted normals', 'WEIGHTED_NORMAL')
    return o

body = box('Enamel toaster housing', (0, 0, 1.08), (3.3, 1.85, 1.86), cream, 0.26, True)
top = box('Stainless top deck', (0, 0, 1.99), (2.98, 1.61, 0.12), steel, 0.09, True)
for index, y in enumerate((-0.40, 0.40), 1):
    cutter = box('Temporary slot cutter', (0, y, 1.94), (2.46, 0.36, 1.04), None, 0.15, True)
    for target in (body, top):
        bpy.context.view_layer.objects.active = target
        mod = target.modifiers.new('Rounded bread opening', 'BOOLEAN')
        mod.operation = 'DIFFERENCE'
        mod.solver = 'EXACT'
        mod.object = cutter
        bpy.ops.object.modifier_apply(modifier=mod.name)
    bpy.data.objects.remove(cutter, do_unlink=True)
    box('Slot %d dark bottom' % index, (0, y, 1.44), (2.38, 0.30, 0.04), dark, 0.02)
    for side in (-1, 1):
        box('Slot %d bread guide %d' % (index, side), (0, y + side * 0.125, 1.80),
            (2.17, 0.024, 0.027), steel, 0.01)
for o in (body, top):
    o.modifiers.new('Weighted surface normals', 'WEIGHTED_NORMAL')
box('Lower black plinth', (0, 0, 0.22), (3.13, 1.74, 0.20), black, 0.09)
for x in (-1.12, 1.12):
    for y in (-0.56, 0.56):
        box('Rubber foot', (x, y, 0.085), (0.35, 0.30, 0.15), black, 0.05)
box('Side control inset', (0.90, -0.915, 1.07), (0.93, 0.09, 1.30), black, 0.12)
box('Lever travel groove', (0.77, -0.975, 1.38), (0.075, 0.025, 0.54), dark, 0.03)
box('Lever steel stem', (0.77, -1.06, 1.43), (0.08, 0.22, 0.07), steel, 0.015)
box('Toast lowering lever', (0.77, -1.17, 1.43), (0.38, 0.19, 0.13), black, 0.05)
cylinder('Browning adjustment dial', (0.78, -1.01, 0.81), 0.24, 0.15, steel)
cylinder('Dial black face', (0.78, -1.095, 0.81), 0.185, 0.025, black)
box('Dial indicator', (0.78, -1.116, 0.94), (0.025, 0.012, 0.07), cream, 0.006)
cylinder('Cancel button', (1.14, -0.99, 1.10), 0.09, 0.09, red)
box('Removable crumb tray seam', (-0.43, -0.926, 0.40), (1.88, 0.018, 0.045), dark, 0.012)
box('Crumb tray pull', (-0.43, -0.97, 0.39), (0.52, 0.10, 0.085), steel, 0.025)
box('Counter surface', (0, 0, -0.09), (200, 200, 0.16), floor)

scene = bpy.context.scene
scene.world.color = (0.20, 0.20, 0.20)
bpy.ops.object.camera_add(location=(4.4, -6.5, 5.0))
camera = bpy.context.object
camera.name = 'Toaster product camera'
camera.rotation_euler = (Vector((0, 0, 1.0)) - camera.location).to_track_quat('-Z', 'Y').to_euler()
camera.data.type = 'ORTHO'
camera.data.ortho_scale = 5.5
scene.camera = camera
for name, location, power, size in [('Key softbox', (0, -4, 7), 950, 5), ('Rim softbox', (3, 4, 5), 800, 4)]:
    bpy.ops.object.light_add(type='AREA', location=location)
    light = bpy.context.object
    light.name = name
    light.data.energy = power
    light.data.shape = 'DISK'
    light.data.size = size
    light.rotation_euler = (Vector((0, 0, 1)) - light.location).to_track_quat('-Z', 'Y').to_euler()
scene.render.resolution_x = 1000
scene.render.resolution_y = 800
scene.render.resolution_percentage = 100
