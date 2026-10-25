import bpy
import math
from mathutils import Vector

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

steel = material('Brushed stainless steel', (0.48, 0.53, 0.56), 0.8)
liner = material('Ivory interior plastic', (0.85, 0.88, 0.86))
white = material('White shelf trim', (0.96, 0.97, 0.94))
gray = material('Dark rubber gasket', (0.065, 0.075, 0.08))
shelfmat = material('Pale blue shelf panels', (0.52, 0.72, 0.76), 0.15, 0.22)
red = material('Tomato red', (0.65, 0.08, 0.035))
green = material('Bottle green', (0.09, 0.32, 0.13))
floor_mat = material('Warm studio floor', (0.24, 0.25, 0.27))

def box(name, location, scale, mat, bevel=0.025, parent=None):
    bpy.ops.mesh.primitive_cube_add(size=1, location=location)
    o = bpy.context.object
    o.name = name
    o.dimensions = scale
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    o.data.materials.append(mat)
    if bevel:
        mod = o.modifiers.new('Soft manufactured edges', 'BEVEL')
        mod.width = bevel
        mod.segments = 3
        o.modifiers.new('Weighted corner normals', 'WEIGHTED_NORMAL')
    if parent:
        o.parent = parent
    return o

def cylinder(name, location, radius, depth, mat):
    bpy.ops.mesh.primitive_cylinder_add(vertices=32, radius=radius, depth=depth, location=location)
    o = bpy.context.object
    o.name = name
    o.data.materials.append(mat)
    mod = o.modifiers.new('Rounded edges', 'BEVEL')
    mod.width = 0.015
    mod.segments = 2
    o.modifiers.new('Weighted normals', 'WEIGHTED_NORMAL')
    return o

# Open-front insulated cabinet: individual walls leave the cavity unobstructed.
box('Cabinet left wall', (-1.12, 0, 2.35), (0.20, 1.92, 4.30), steel)
box('Cabinet right wall', (1.12, 0, 2.35), (0.20, 1.92, 4.30), steel)
box('Cabinet roof', (0, 0, 4.43), (2.24, 1.92, 0.16), steel)
box('Cabinet base', (0, 0, 0.28), (2.24, 1.92, 0.16), steel)
box('Rear insulated wall', (0, 0.89, 2.35), (2.12, 0.18, 4.12), steel)
box('Interior rear liner', (0, 0.785, 2.35), (2.04, 0.04, 4.00), liner)
for x in (-1.005, 1.005):
    box('Interior side liner', (x, -0.04, 2.35), (0.035, 1.64, 4.00), liner)
box('Interior ceiling', (0, -0.04, 4.30), (2.02, 1.65, 0.06), liner)
box('Interior floor', (0, -0.04, 0.40), (2.02, 1.65, 0.10), liner)
for z in (1.28, 2.12, 2.96, 3.75):
    box('Removable shelf panel', (0, -0.04, z), (1.97, 1.52, 0.055), shelfmat, 0.012)
    box('Shelf front lip', (0, -0.79, z), (1.98, 0.07, 0.09), white, 0.012)
    for x in (-0.965, 0.965):
        box('Shelf support rail', (x, -0.02, z-0.07), (0.07, 1.43, 0.08), liner)
box('Crisper drawer base', (0, -0.05, 0.55), (1.85, 1.38, 0.10), liner)
box('Crisper drawer front', (0, -0.77, 0.86), (1.85, 0.08, 0.57), shelfmat)
for x in (-0.89, 0.89):
    box('Crisper drawer side', (x, -0.04, 0.86), (0.07, 1.40, 0.57), liner)
box('Crisper pull', (0, -0.835, 1.03), (0.65, 0.07, 0.065), white)
for x in (-0.58, -0.20, 0.18):
    cylinder('Stored food tin', (x, 0.15, 2.37), 0.14, 0.44, red)
for x in (0.46, 0.78):
    cylinder('Juice bottle body', (x, 0.30, 1.61), 0.12, 0.59, green)
    cylinder('Juice bottle cap', (x, 0.30, 1.94), 0.075, 0.09, white)
box('Interior lamp housing', (0, 0.735, 4.02), (0.65, 0.08, 0.16), white)
for x in (-0.94, 0.94):
    for y in (-0.69, 0.69):
        cylinder('Adjustable foot', (x, y, 0.12), 0.10, 0.24, gray)

# All door components use hinge-local coordinates before the hinge is positioned.
bpy.ops.object.empty_add(type='PLAIN_AXES')
hinge = bpy.context.object
hinge.name = 'Door hinge assembly - open 108 degrees'
box('Door outer shell', (1.12, 0, 2.35), (2.24, 0.18, 4.28), steel, parent=hinge)
box('Door perimeter gasket', (1.12, 0.11, 2.35), (2.12, 0.06, 4.12), gray, parent=hinge)
box('Door inner liner', (1.12, 0.15, 2.35), (1.98, 0.06, 3.98), liner, parent=hinge)
for z in (0.87, 1.88, 3.03):
    box('Door bin bottom', (1.12, 0.35, z), (1.79, 0.40, 0.07), white, parent=hinge)
    box('Door bin retaining wall', (1.12, 0.55, z+0.19), (1.79, 0.065, 0.38), shelfmat, parent=hinge)
    for x in (0.25, 1.99):
        box('Door bin end', (x, 0.35, z+0.19), (0.065, 0.40, 0.38), white, parent=hinge)
for z in (2.09, 3.23):
    box('Handle standoff', (2.01, -0.18, z), (0.09, 0.22, 0.10), steel, parent=hinge)
box('Vertical door handle', (2.01, -0.29, 2.66), (0.10, 0.10, 1.26), steel, 0.045, hinge)
hinge.location = (-1.12, -1.01, 0)
hinge.rotation_euler.z = math.radians(-108)
box('Studio ground', (0, 0, -0.085), (200, 200, 0.10), floor_mat, 0)

bpy.ops.object.camera_add(location=(7.3, -10.8, 6.8))
cam = bpy.context.object
cam.name = 'Refrigerator presentation camera'
cam.rotation_euler = (Vector((-0.40, -0.55, 2.20))-cam.location).to_track_quat('-Z', 'Y').to_euler()
cam.data.type = 'ORTHO'
cam.data.ortho_scale = 7.7
bpy.context.scene.camera = cam
for name, loc, power, size in [('Key', (2, -6, 8), 1400, 5), ('Fill', (-5, -3, 5), 1000, 4), ('Rim', (2, 4, 7), 1100, 3)]:
    bpy.ops.object.light_add(type='AREA', location=loc)
    light = bpy.context.object
    light.name = name
    light.data.energy = power
    light.data.shape = 'DISK'
    light.data.size = size
    light.rotation_euler = (Vector((0, 0, 2))-light.location).to_track_quat('-Z', 'Y').to_euler()
bpy.context.scene.world.color = (0.22, 0.22, 0.22)
bpy.context.scene.render.resolution_x = 1000
bpy.context.scene.render.resolution_y = 1000
bpy.context.scene.render.resolution_percentage = 100
