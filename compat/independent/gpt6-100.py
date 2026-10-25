import bpy
import math
from mathutils import Vector

bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)

def material(name, color, metallic=0.0, roughness=0.55):
    m = bpy.data.materials.new(name)
    m.diffuse_color = (*color, 1)
    m.use_nodes = True
    bs = m.node_tree.nodes.get('Principled BSDF')
    bs.inputs['Base Color'].default_value = (*color, 1)
    bs.inputs['Metallic'].default_value = metallic
    bs.inputs['Roughness'].default_value = roughness
    return m

concrete = material('Platform concrete', (0.48, 0.49, 0.47))
paving = material('Pale paving slabs', (0.67, 0.66, 0.60))
steel = material('Dark teal painted steel', (0.055, 0.18, 0.19), 0.55)
roof = material('Canopy metal', (0.24, 0.32, 0.34), 0.7)
wood = material('Bench timber', (0.48, 0.23, 0.085))
yellow = material('Safety yellow', (0.95, 0.65, 0.08))
white = material('Sign lettering', (0.93, 0.94, 0.88))
rail = material('Rail steel', (0.32, 0.34, 0.35), 0.85)
ballast = material('Ballast bed', (0.23, 0.24, 0.23), roughness=0.95)
soil = material('Surrounding ground', (0.30, 0.34, 0.27), roughness=1)

def box(name, location, dimensions, mat, bevel=0.025):
    bpy.ops.mesh.primitive_cube_add(size=1, location=location)
    o = bpy.context.object
    o.name = name
    o.dimensions = dimensions
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    o.data.materials.append(mat)
    if bevel:
        mod = o.modifiers.new('Edge softening', 'BEVEL')
        mod.width = bevel
        mod.segments = 2
        o.modifiers.new('Weighted normals', 'WEIGHTED_NORMAL')
    return o

def beam(name, start, end, width, mat):
    a, b = Vector(start), Vector(end)
    obj = box(name, (a+b)/2, (width, width, (b-a).length), mat, 0.012)
    obj.rotation_euler = (b-a).to_track_quat('Z', 'Y').to_euler()
    return obj

def label(name, body, location, size):
    bpy.ops.object.text_add(location=location, rotation=(math.pi/2, 0, 0))
    o = bpy.context.object
    o.name = name
    o.data.body = body
    o.data.align_x = 'CENTER'
    o.data.align_y = 'CENTER'
    o.data.size = size
    o.data.extrude = 0.002
    o.data.materials.append(white)

box('Ground', (0, -0.8, -0.14), (14, 8.5, 0.25), soil)
box('Raised station platform', (0, 0, 0.34), (10, 3.6, 0.68), concrete)
for i in range(20):
    for j in range(6):
        box('Paving slab %02d-%d' % (i, j), (-4.75+i*0.5, -1.25+j*0.5, 0.705),
            (0.488, 0.488, 0.05), paving, 0.006)
for i in range(20):
    box('Track edge coping %02d' % i, (-4.75+i*0.5, -1.64, 0.715),
        (0.488, 0.30, 0.07), paving, 0.008)
box('Continuous yellow safety strip', (0, -1.43, 0.738), (9.96, 0.09, 0.014), yellow, 0.003)
for i in range(50):
    box('Tactile warning rib %02d' % i, (-4.9+i*0.2, -1.62, 0.758),
        (0.035, 0.18, 0.015), yellow, 0.004)
# Three ascending steps at the platform's left end.
for i in range(3):
    box('Access step %d' % (i+1), (-6.05+i*0.35, 0.35, (i+1)*0.115),
        (0.35, 1.6, (i+1)*0.23), concrete)
# Compact pitched canopy supported by two rows of columns.
for x in (-3.7, 0, 3.7):
    for y in (-0.65, 1.25):
        box('Column foot', (x, y, 0.77), (0.32, 0.32, 0.08), steel)
        box('Canopy column', (x, y, 2.04), (0.13, 0.13, 2.55), steel)
        beam('Column knee brace', (x, y, 2.75), (x+0.4, y, 3.30), 0.075, steel)
    beam('Transverse roof tie', (x, -0.95, 3.30), (x, 1.55, 3.30), 0.13, steel)
for y in (-0.75, 1.35):
    box('Longitudinal eave beam', (0, y, 3.30), (8.5, 0.14, 0.18), steel)
for sign in (-1, 1):
    panel = box('Pitched canopy roof', (0, 0.30+sign*0.77, 3.57),
                (8.8, math.sqrt(1.54**2+0.44**2), 0.085), roof)
    panel.rotation_euler.x = -sign*math.atan2(0.44, 1.54)
box('Roof ridge cap', (0, 0.30, 3.80), (8.9, 0.14, 0.10), steel)
# Two slatted benches face the track.
for index, x in enumerate((-2.15, 2.15)):
    for dx in (-0.74, 0.74):
        box('Bench %d leg' % index, (x+dx, 0.64, 0.94), (0.09, 0.48, 0.42), steel)
        box('Bench %d back support' % index, (x+dx, 0.90, 1.34), (0.075, 0.075, 0.85), steel)
        box('Bench armrest', (x+dx, 0.63, 1.39), (0.07, 0.56, 0.065), steel)
    for j in range(4):
        box('Bench seat slat', (x, 0.42+j*0.14, 1.18), (1.9, 0.115, 0.07), wood, 0.012)
    for j in range(3):
        box('Bench back slat', (x, 0.90, 1.39+j*0.14), (1.9, 0.065, 0.115), wood, 0.012)
box('Station name board', (0, 0.32, 2.89), (2.8, 0.10, 0.46), steel)
label('Station name', 'WILLOW HALT', (0, 0.258, 2.89), 0.255)
for x in (-1.1, 1.1):
    beam('Sign suspension', (x, 0.32, 3.30), (x, 0.32, 3.08), 0.035, steel)
box('Track ballast', (0, -3.10, 0.035), (13, 2.10, 0.13), ballast)
for i in range(23):
    box('Track sleeper %02d' % i, (-6.05+i*0.55, -3.10, 0.14), (0.18, 1.95, 0.13), wood)
for y in (-3.82, -2.38):
    box('Rail foot', (0, y, 0.225), (13, 0.15, 0.04), rail, 0.008)
    box('Rail web', (0, y, 0.29), (13, 0.045, 0.12), rail, 0.005)
    box('Rail head', (0, y, 0.365), (13, 0.08, 0.05), rail, 0.012)

scene = bpy.context.scene
scene.world.color = (0.25, 0.25, 0.25)
bpy.ops.object.light_add(type='AREA', location=(0, -4, 10))
bpy.context.object.data.energy = 1800
bpy.context.object.data.size = 8
bpy.ops.object.camera_add(location=(12, -16, 10))
camera = bpy.context.object
camera.name = 'Platform overview camera'
camera.rotation_euler = (Vector((0, -0.6, 1.3))-camera.location).to_track_quat('-Z', 'Y').to_euler()
camera.data.type = 'ORTHO'
camera.data.ortho_scale = 17
scene.camera = camera
scene.render.resolution_x = 1200
scene.render.resolution_y = 800
scene.render.resolution_percentage = 100
