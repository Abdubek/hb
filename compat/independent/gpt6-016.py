import bpy
from mathutils import Vector

bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)

def material(name, color, metallic=0.0, roughness=0.5):
    mat = bpy.data.materials.new(name)
    mat.diffuse_color = (*color, 1)
    mat.use_nodes = True
    shader = mat.node_tree.nodes.get('Principled BSDF')
    shader.inputs['Base Color'].default_value = (*color, 1)
    shader.inputs['Metallic'].default_value = metallic
    shader.inputs['Roughness'].default_value = roughness
    return mat

steel = material('Dark teal coated steel', (0.035, 0.13, 0.15), 0.65, 0.30)
roof_mat = material('Silver roof skin', (0.54, 0.61, 0.64), 0.65, 0.28)
wood = material('Warm timber bench slats', (0.49, 0.24, 0.085), 0.0, 0.42)
concrete = material('Concrete platform', (0.48, 0.49, 0.46))
asphalt = material('Road asphalt', (0.09, 0.10, 0.11), 0, 0.95)
white = material('Warm white markings', (0.9, 0.93, 0.90))
blue = material('Transit blue', (0.02, 0.15, 0.45), 0.15)
rubber = material('Panel gaskets', (0.025, 0.03, 0.035))
glass = material('Transparent safety glass', (0.79, 0.94, 0.96), 0, 0.075)
shader = glass.node_tree.nodes.get('Principled BSDF')
shader.inputs['Transmission Weight'].default_value = 1.0
shader.inputs['IOR'].default_value = 1.45

def box(name, location, size, mat, bevel=0.02):
    bpy.ops.mesh.primitive_cube_add(size=1, location=location)
    obj = bpy.context.object
    obj.name = name
    obj.dimensions = size
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    obj.data.materials.append(mat)
    if bevel:
        mod = obj.modifiers.new('Soft manufactured edges', 'BEVEL')
        mod.width = bevel
        mod.segments = 2
        obj.modifiers.new('Weighted normals', 'WEIGHTED_NORMAL')
    return obj

def cylinder(name, location, radius, depth, mat):
    bpy.ops.mesh.primitive_cylinder_add(vertices=16, radius=radius, depth=depth, location=location)
    obj = bpy.context.object
    obj.name = name
    obj.data.materials.append(mat)
    return obj

def text(name, body, location, size, mat):
    curve = bpy.data.curves.new(name, type='FONT')
    curve.body = body
    curve.align_x = 'CENTER'
    curve.align_y = 'CENTER'
    curve.size = size
    curve.extrude = 0.001
    obj = bpy.data.objects.new(name, curve)
    bpy.context.collection.objects.link(obj)
    obj.location = location
    obj.rotation_euler = (1.57079632679, 0, 0)
    curve.materials.append(mat)
    return obj

# Negative Y is the open, curb-facing entrance.
box('Ground', (0, 0, -0.23), (10, 7.5, 0.20), asphalt)
box('Raised shelter platform', (0, 0.25, -0.065), (7.7, 4.2, 0.25), concrete, 0.05)
box('Front curb edge', (0, -1.83, -0.015), (7.7, 0.15, 0.35), white)
box('Road stop marking', (0, -2.75, -0.121), (5.8, 0.12, 0.014), white, 0)
for x in (-2.7, 2.7):
    for y in (-0.90, 1.10):
        box('Post base plate', (x, y, 0.095), (0.29, 0.29, 0.07), steel)
        box('Structural corner post', (x, y, 1.48), (0.12, 0.12, 2.77), steel)
        for dx in (-0.095, 0.095):
            cylinder('Anchor bolt', (x + dx, y, 0.145), 0.025, 0.025, roof_mat)
    box('Side lower glazing rail', (x, 0.10, 0.30), (0.09, 2.0, 0.10), steel)
    box('Side upper glazing rail', (x, 0.10, 2.61), (0.09, 2.0, 0.10), steel)
    box('Transparent side safety panel', (x, 0.10, 1.46), (0.022, 1.86, 2.19), glass, 0.005)
    for y in (-0.83, 1.03):
        box('Side vertical gasket', (x, y, 1.46), (0.035, 0.026, 2.19), rubber, 0.004)
    for j in range(7):
        box('Side visibility marker', (x, -0.68 + j * 0.25, 1.43), (0.028, 0.105, 0.05), white, 0.003)
for x in (-0.90, 0.90):
    box('Rear glazing mullion', (x, 1.10, 1.46), (0.075, 0.09, 2.35), steel)
for x in (-1.80, 0, 1.80):
    box('Transparent rear panel', (x, 1.10, 1.46), (1.70, 0.022, 2.19), glass, 0.005)
box('Rear lower frame', (0, 1.10, 0.30), (5.4, 0.10, 0.10), steel)
box('Rear roof beam', (0, 1.10, 2.76), (5.60, 0.16, 0.20), steel)
box('Front roof beam', (0, -0.90, 2.76), (5.60, 0.16, 0.20), steel)
box('Overhanging metal roof', (0, 0.05, 2.94), (6.10, 2.75, 0.16), roof_mat, 0.055)
box('Front fascia', (0, -1.32, 2.90), (6.10, 0.085, 0.25), steel)
box('Rear rain gutter', (0, 1.44, 2.88), (6.10, 0.13, 0.13), steel)
cylinder('Rain downpipe', (2.85, 1.43, 1.48), 0.045, 2.75, steel)
for x in (-1.65, 1.65):
    box('Bench leg', (x, 0.40, 0.34), (0.12, 0.53, 0.54), steel)
    box('Bench back support', (x, 0.73, 0.72), (0.085, 0.08, 1.10), steel)
for y in (0.18, 0.38, 0.58):
    box('Timber seat slat', (0, y, 0.64), (4.25, 0.17, 0.085), wood)
for z in (0.89, 1.09, 1.29):
    box('Timber backrest slat', (0, 0.76, z), (4.25, 0.085, 0.16), wood)
for x in (-2.08, 0, 2.08):
    box('Bench armrest support', (x, 0.34, 0.79), (0.045, 0.045, 0.29), steel)
    box('Bench armrest', (x, 0.40, 0.95), (0.065, 0.53, 0.06), steel)
box('Bus stop fascia sign', (0, -1.38, 2.90), (2.90, 0.035, 0.28), blue, 0.01)
text('Stop name lettering', 'BUS  /  CENTRAL', (0, -1.404, 2.90), 0.18, white)
box('Timetable frame', (1.85, 1.045, 1.94), (0.58, 0.075, 0.85), steel)
box('Timetable white face', (1.85, 0.997, 1.94), (0.50, 0.016, 0.77), white)
text('Timetable heading', 'ROUTES', (1.85, 0.984, 2.21), 0.075, blue)
text('Route numbers', '12   24   38', (1.85, 0.983, 2.07), 0.065, blue)
for z in (1.91, 1.83, 1.75, 1.67):
    box('Timetable printed rule', (1.85, 0.984, z), (0.37, 0.005, 0.012), blue, 0)

scene = bpy.context.scene
scene.render.engine = 'CYCLES'
scene.cycles.samples = 32
scene.world.color = (0.35, 0.35, 0.35)
bpy.ops.object.light_add(type='AREA', location=(-3, -4, 8))
bpy.context.object.data.energy = 1500
bpy.context.object.data.size = 6
bpy.ops.object.camera_add(location=(8.5, -11, 6.3))
camera = bpy.context.object
camera.name = 'Shelter overview camera'
camera.rotation_euler = (Vector((0, 0, 1.30)) - camera.location).to_track_quat('-Z', 'Y').to_euler()
camera.data.type = 'ORTHO'
camera.data.ortho_scale = 9.5
scene.camera = camera
scene.render.resolution_x = 1400
scene.render.resolution_y = 1000
scene.render.resolution_percentage = 100
