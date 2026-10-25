import bpy
import math
from mathutils import Vector

# Four burner kitchen range; front faces negative Y. Units are meters.
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)

def material(name, color, metallic=0.0, roughness=0.4):
    mat = bpy.data.materials.new(name)
    mat.diffuse_color = (*color, 1)
    mat.use_nodes = True
    shader = mat.node_tree.nodes.get('Principled BSDF')
    shader.inputs['Base Color'].default_value = (*color, 1)
    shader.inputs['Metallic'].default_value = metallic
    shader.inputs['Roughness'].default_value = roughness
    return mat

steel = material('Brushed stainless steel', (0.48, 0.52, 0.55), 0.85, 0.3)
enamel = material('Ivory enamel', (0.8, 0.78, 0.7), 0.15, 0.26)
iron = material('Cast iron grates', (0.033, 0.039, 0.045), 0.6, 0.65)
black = material('Black seals and recesses', (0.013, 0.018, 0.023), 0.1, 0.55)
glass = material('Smoked oven glass', (0.025, 0.05, 0.065), 0.35, 0.12)
white = material('Control markings', (0.87, 0.88, 0.83), roughness=0.45)
ground = material('Floor', (0.35, 0.39, 0.42), roughness=0.8)

def finish(obj, name, mat, bevel=0):
    obj.name = name
    obj.data.materials.append(mat)
    if bevel:
        modifier = obj.modifiers.new('Rounded fabrication edges', 'BEVEL')
        modifier.width = bevel
        modifier.segments = 3
        obj.modifiers.new('Weighted normals', 'WEIGHTED_NORMAL')
    return obj

def box(name, location, dimensions, mat, bevel=0.006):
    bpy.ops.mesh.primitive_cube_add(size=1, location=location)
    obj = bpy.context.object
    obj.dimensions = dimensions
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    return finish(obj, name, mat, bevel)

def cylinder(name, location, radius, depth, mat, axis=(0, 0, 1)):
    bpy.ops.mesh.primitive_cylinder_add(vertices=40, radius=radius, depth=depth, location=location)
    obj = bpy.context.object
    obj.rotation_euler = Vector(axis).to_track_quat('Z', 'Y').to_euler()
    return finish(obj, name, mat, 0.002)

def ring(name, location, radius, thickness, mat):
    bpy.ops.mesh.primitive_torus_add(major_segments=40, minor_segments=10, location=location,
                                   major_radius=radius, minor_radius=thickness)
    obj = finish(bpy.context.object, name, mat)
    for polygon in obj.data.polygons:
        polygon.use_smooth = True

for x in (-0.35, 0.35):
    for y in (-0.25, 0.25):
        cylinder('Adjustable leveling foot', (x, y, 0.05), 0.035, 0.09, black)
box('Enamel range cabinet', (0, 0, 0.48), (0.9, 0.7, 0.8), enamel, 0.018)
box('Recessed toe kick', (0, -0.342, 0.13), (0.79, 0.024, 0.08), black)
box('Lower storage drawer', (0, -0.36, 0.23), (0.85, 0.03, 0.115), steel)
box('Drawer finger recess', (0, -0.378, 0.269), (0.35, 0.01, 0.017), black, 0.004)
box('Oven door perimeter gasket', (0, -0.36, 0.525), (0.85, 0.027, 0.46), black)
box('Stainless oven door', (0, -0.383, 0.525), (0.82, 0.045, 0.435), steel, 0.012)
box('Window black surround', (0, -0.408, 0.5), (0.68, 0.012, 0.29), black, 0.015)
box('Smoked glass oven window', (0, -0.417, 0.5), (0.615, 0.008, 0.236), glass, 0.012)
for x in (-0.3, 0.3):
    box('Oven handle standoff', (x, -0.443, 0.69), (0.035, 0.075, 0.035), steel)
cylinder('Horizontal oven pull handle', (0, -0.485, 0.69), 0.018, 0.68, steel, (1, 0, 0))
box('Front control fascia', (0, -0.368, 0.815), (0.87, 0.05, 0.11), steel)
for i, x in enumerate((-0.33, -0.165, 0, 0.165, 0.33)):
    cylinder('Control bezel %d' % (i + 1), (x, -0.4, 0.815), 0.034, 0.01, black, (0, 1, 0))
    cylinder('Burner knob %d' % (i + 1) if i < 4 else 'Oven temperature knob',
             (x, -0.421, 0.815), 0.027, 0.033, steel, (0, 1, 0))
    box('Knob pointer %d' % (i + 1), (x, -0.439, 0.83), (0.003, 0.002, 0.014), black, 0.0005)
    box('Off index %d' % (i + 1), (x, -0.397, 0.859), (0.006, 0.003, 0.008), white, 0.001)
box('Stainless cooktop rim', (0, 0, 0.894), (0.92, 0.72, 0.033), steel)
box('Recessed black cooktop', (0, -0.005, 0.912), (0.855, 0.65, 0.013), black)
box('Rear splash lip', (0, 0.335, 0.946), (0.9, 0.035, 0.095), steel)
for i, (x, y) in enumerate(((-0.23, -0.175), (0.23, -0.175), (-0.23, 0.155), (0.23, 0.155))):
    prefix = 'Burner %d ' % (i + 1)
    radius = 0.074 if i in (0, 3) else 0.057
    cylinder(prefix + 'drip well', (x, y, 0.924), 0.123, 0.011, steel)
    ring(prefix + 'gas ring', (x, y, 0.94), radius, 0.009, steel)
    cylinder(prefix + 'black cap', (x, y, 0.952), radius + 0.003, 0.014, iron)
    for side in (-1, 1):
        box(prefix + 'grate side rail', (x + side * 0.15, y, 0.981), (0.016, 0.274, 0.023), iron, 0.003)
        box(prefix + 'grate end rail', (x, y + side * 0.129, 0.981), (0.3, 0.016, 0.023), iron, 0.003)
        box(prefix + 'pot support X', (x + side * 0.1, y, 0.981), (0.116, 0.018, 0.023), iron, 0.003)
        box(prefix + 'pot support Y', (x, y + side * 0.094, 0.981), (0.018, 0.09, 0.023), iron, 0.003)

box('Studio floor', (0, 0, -0.025), (200, 200, 0.05), ground, 0)
bpy.ops.object.camera_add(location=(1.65, -2.25, 1.75))
camera = bpy.context.object
camera.name = 'Range three quarter camera'
camera.rotation_euler = (Vector((0, 0, 0.52)) - camera.location).to_track_quat('-Z', 'Y').to_euler()
camera.data.type = 'ORTHO'
camera.data.ortho_scale = 1.65
scene = bpy.context.scene
scene.camera = camera
for location, power, size in [((1, -3, 4), 450, 3), ((-2, 1, 3), 350, 2)]:
    bpy.ops.object.light_add(type='AREA', location=location)
    light = bpy.context.object
    light.data.energy = power
    light.data.size = size
    light.rotation_euler = (Vector((0, 0, 0.5)) - light.location).to_track_quat('-Z', 'Y').to_euler()
scene.world.color = (0.2, 0.2, 0.2)
scene.render.resolution_x = 1000
scene.render.resolution_y = 1000
scene.render.resolution_percentage = 100
