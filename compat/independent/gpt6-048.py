import bpy
import math
from mathutils import Vector

# Independent three-bay electric vehicle charging forecourt.
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)

def material(name, color, metallic=0, roughness=0.45, emission=0):
    m = bpy.data.materials.new(name)
    m.diffuse_color = (*color, 1)
    m.use_nodes = True
    bs = m.node_tree.nodes.get('Principled BSDF')
    bs.inputs['Base Color'].default_value = (*color, 1)
    bs.inputs['Metallic'].default_value = metallic
    bs.inputs['Roughness'].default_value = roughness
    if emission:
        bs.inputs['Emission Color'].default_value = (*color, 1)
        bs.inputs['Emission Strength'].default_value = emission
    return m

asphalt = material('Fine charcoal asphalt', (0.085, 0.105, 0.12), roughness=0.9)
concrete = material('Concrete curb', (0.55, 0.59, 0.59))
white = material('White enamel and markings', (0.88, 0.93, 0.94), 0.15)
green = material('EV green', (0.10, 0.62, 0.29), 0.15)
dark = material('Graphite equipment trim', (0.035, 0.05, 0.065), 0.35)
rubber = material('Rubber tires and charging cable', (0.012, 0.018, 0.022), roughness=0.8)
steel = material('Brushed aluminum', (0.48, 0.56, 0.62), 0.8, 0.25)
screen = material('Display glass', (0.015, 0.06, 0.08), 0.3, 0.17)
glow = material('Mint status light', (0.2, 0.95, 0.61), emission=2)
solar = material('Blue photovoltaic cells', (0.018, 0.065, 0.15), 0.5, 0.22)
paint = material('Car electric blue paint', (0.025, 0.27, 0.59), 0.6, 0.22)
glass = material('Car tinted glazing', (0.025, 0.07, 0.1), 0.4, 0.14)
red = material('Red tail lamps', (0.65, 0.025, 0.018), emission=0.3)

def box(name, loc, size, mat, bevel=0.025):
    bpy.ops.mesh.primitive_cube_add(size=1, location=loc)
    obj = bpy.context.object
    obj.name = name
    obj.dimensions = size
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    obj.data.materials.append(mat)
    if bevel:
        mod = obj.modifiers.new('Rounded manufacturing edges', 'BEVEL')
        mod.width = bevel
        mod.segments = 3
        obj.modifiers.new('Weighted normals', 'WEIGHTED_NORMAL')
    return obj

def cylinder(name, loc, radius, depth, mat, rotation=(0, 0, 0)):
    bpy.ops.mesh.primitive_cylinder_add(vertices=24, radius=radius, depth=depth, location=loc, rotation=rotation)
    obj = bpy.context.object
    obj.name = name
    obj.data.materials.append(mat)
    bevel = obj.modifiers.new('Rounded rim', 'BEVEL')
    bevel.width = 0.015
    bevel.segments = 2
    obj.modifiers.new('Weighted normals', 'WEIGHTED_NORMAL')
    return obj

def label(name, body, loc, size, mat, rotation=(math.pi/2, 0, 0)):
    curve = bpy.data.curves.new(name, 'FONT')
    curve.body = body
    curve.align_x = 'CENTER'
    curve.align_y = 'CENTER'
    curve.size = size
    curve.extrude = 0.001
    obj = bpy.data.objects.new(name, curve)
    bpy.context.collection.objects.link(obj)
    obj.location = loc
    obj.rotation_euler = rotation
    obj.data.materials.append(mat)
    return obj

def cable(name, points):
    curve = bpy.data.curves.new(name, 'CURVE')
    curve.dimensions = '3D'
    curve.bevel_depth = 0.035
    curve.bevel_resolution = 3
    spline = curve.splines.new('BEZIER')
    spline.bezier_points.add(len(points)-1)
    for p, co in zip(spline.bezier_points, points):
        p.co = co
        p.handle_left_type = 'AUTO'
        p.handle_right_type = 'AUTO'
    obj = bpy.data.objects.new(name, curve)
    bpy.context.collection.objects.link(obj)
    obj.data.materials.append(rubber)

box('Forecourt asphalt slab', (0, -0.7, -0.15), (12.6, 10.6, 0.3), asphalt)
box('Raised charging island', (0, 3.1, 0.13), (11.7, 1.9, 0.26), concrete)
for x in [-5.25, -1.75, 1.75, 5.25]:
    box('Parking bay separator', (x, -0.75, 0.012), (0.09, 5.4, 0.022), white, 0)
for index, x in enumerate([-3.5, 0, 3.5], start=1):
    box('Green EV bay threshold', (x, -3.5, 0.014), (3.3, 0.85, 0.025), green, 0)
    label('Ground EV marking', 'EV', (x, -3.5, 0.033), 0.58, white, (0, 0, 0))
    box('Wheel stop', (x, 1.42, 0.11), (1.75, 0.22, 0.2), concrete)
    box('Charger %d pedestal' % index, (x, 2.8, 0.38), (0.95, 0.78, 0.24), dark)
    box('Charger %d enclosure' % index, (x, 2.8, 1.43), (0.87, 0.64, 1.94), white, 0.12)
    box('Charger green top', (x, 2.8, 2.39), (0.88, 0.65, 0.2), green, 0.06)
    box('Front graphite fascia', (x, 2.466, 1.66), (0.68, 0.035, 1.08), dark)
    box('Touch display', (x, 2.441, 1.85), (0.49, 0.018, 0.36), screen)
    label('Display power rating', '150 kW', (x, 2.428, 1.89), 0.105, glow)
    label('Display status', 'READY', (x, 2.427, 1.76), 0.065, white)
    label('Bay identifier', '%02d' % index, (x, 2.442, 1.35), 0.17, white)
    box('Contactless payment reader', (x, 2.435, 1.1), (0.16, 0.04, 0.12), screen)
    box('Status indicator', (x, 2.434, 2.14), (0.48, 0.02, 0.035), glow)
    cable('Docked charging cable %d' % index, [(x+0.43, 2.78, 1.9), (x+0.78, 2.49, 1.55), (x+0.82, 2.29, 0.55), (x+0.52, 2.17, 0.49), (x+0.4, 2.32, 1.22)])
    handle = box('Docked charging connector', (x+0.4, 2.31, 1.27), (0.115, 0.17, 0.3), dark, 0.04)
    handle.rotation_euler.y = -0.22
    for dx in [-0.95, 0.95]:
        cylinder('Protective bollard', (x+dx, 2.15, 0.61), 0.085, 1.18, steel)
        cylinder('Bollard green visibility band', (x+dx, 2.15, 0.97), 0.089, 0.15, green)
for x in [-5.6, 5.6]:
    box('Canopy column footing', (x, 3.2, 0.33), (0.7, 0.7, 0.16), concrete)
    box('Canopy steel column', (x, 3.2, 2.22), (0.22, 0.3, 3.85), steel)
box('Canopy rear support beam', (0, 3.2, 4.06), (12.0, 0.26, 0.3), steel)
box('Solar canopy roof', (0, 2.05, 4.27), (12.2, 3.5, 0.22), dark)
box('Green canopy front fascia', (0, 0.28, 4.24), (12.2, 0.12, 0.4), green)
label('Station name', 'EV CHARGE  /  FAST ELECTRIC', (0, 0.209, 4.24), 0.27, white)
for x in range(10):
    for y in range(3):
        box('Solar panel aluminum frame', (-5.4+x*1.2, 0.95+y*1.04, 4.411), (1.12, 0.97, 0.055), steel, 0.008)
        box('Photovoltaic module', (-5.4+x*1.2, 0.95+y*1.04, 4.444), (1.05, 0.9, 0.018), solar, 0.004)
# Compact parked electric hatchback, nose facing the charger.
box('EV lower body', (-3.5, -0.65, 0.68), (1.78, 3.95, 0.63), paint, 0.23)
box('EV glazed passenger cabin', (-3.5, -0.92, 1.23), (1.53, 2.15, 0.78), glass, 0.22)
box('EV painted roof', (-3.5, -0.94, 1.64), (1.34, 1.69, 0.08), paint, 0.06)
for side in [-1, 1]:
    box('Window center pillar', (-3.5+side*0.77, -0.92, 1.27), (0.045, 0.11, 0.59), dark)
    box('Door handle', (-3.5+side*0.894, -0.59, 0.96), (0.025, 0.22, 0.04), steel)
    box('Side mirror', (-3.5+side*0.97, -0.03, 1.12), (0.21, 0.24, 0.13), paint, 0.05)
    for y in [-1.92, 0.59]:
        cylinder('EV tire', (-3.5+side*0.86, y, 0.43), 0.37, 0.23, rubber, (0, math.pi/2, 0))
        cylinder('EV alloy wheel', (-3.5+side*0.985, y, 0.43), 0.245, 0.025, steel, (0, math.pi/2, 0))
    box('Front LED headlight', (-3.5+side*0.58, 1.324, 0.81), (0.4, 0.03, 0.12), white)
    box('Rear tail light', (-3.5+side*0.59, -2.627, 0.83), (0.36, 0.03, 0.13), red)
box('EV front lower intake', (-3.5, 1.329, 0.53), (0.85, 0.035, 0.14), dark)

bpy.ops.object.camera_add(location=(13, -18, 12))
camera = bpy.context.object
camera.name = 'Charging forecourt overview'
camera.rotation_euler = (Vector((0, 0.2, 1.4))-camera.location).to_track_quat('-Z', 'Y').to_euler()
camera.data.type = 'ORTHO'
camera.data.ortho_scale = 18.5
bpy.context.scene.camera = camera
bpy.ops.object.light_add(type='AREA', location=(1, -5, 11))
bpy.context.object.data.energy = 2200
bpy.context.object.data.size = 8
bpy.ops.object.light_add(type='SUN', rotation=(0.35, -0.5, -0.5))
bpy.context.object.data.energy = 2
scene = bpy.context.scene
scene.world = bpy.data.worlds.new('Forecourt daylight')
scene.world.use_nodes = True
scene.world.node_tree.nodes['Background'].inputs[0].default_value = (0.58, 0.7, 0.85, 1)
scene.world.node_tree.nodes['Background'].inputs[1].default_value = 0.5
scene.render.resolution_x = 1400
scene.render.resolution_y = 1000
scene.render.resolution_percentage = 100
