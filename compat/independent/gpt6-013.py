import bpy
import math
from mathutils import Vector

# Independent scene: belt-drive record player with raised dust cover.
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

walnut = material('Warm walnut plinth', (0.21, 0.085, 0.035))
black = material('Satin black components', (0.014, 0.019, 0.024))
vinyl = material('Black vinyl', (0.008, 0.01, 0.014), 0.15, 0.23)
groove = material('Groove highlights', (0.035, 0.041, 0.047), 0.25, 0.32)
metal = material('Brushed aluminum', (0.57, 0.61, 0.65), 0.8, 0.25)
label = material('Terracotta record label', (0.66, 0.16, 0.075))
glass = material('Clear smoked acrylic', (0.66, 0.79, 0.83), 0.0, 0.1)
p = glass.node_tree.nodes.get('Principled BSDF')
p.inputs['Transmission Weight'].default_value = 0.92
p.inputs['IOR'].default_value = 1.46

def finish(obj, name, mat, bevel=0):
    obj.name = name
    obj.data.materials.append(mat)
    if bevel:
        mod = obj.modifiers.new('Soft machined edges', 'BEVEL')
        mod.width = bevel
        mod.segments = 3
        obj.modifiers.new('Weighted corner normals', 'WEIGHTED_NORMAL')
    return obj

def box(name, loc, size, mat, bevel=0.015, parent=None):
    bpy.ops.mesh.primitive_cube_add(size=1, location=loc)
    obj = bpy.context.object
    obj.dimensions = size
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    finish(obj, name, mat, bevel)
    if parent:
        obj.parent = parent
        obj.location = loc
    return obj

def cylinder(name, loc, radius, depth, mat):
    bpy.ops.mesh.primitive_cylinder_add(vertices=64, radius=radius, depth=depth, location=loc)
    obj = finish(bpy.context.object, name, mat, 0.004)
    for face in obj.data.polygons:
        face.use_smooth = len(face.vertices) == 4
    return obj

def rod(name, a, b, radius, mat):
    a, b = Vector(a), Vector(b)
    obj = cylinder(name, (a + b) / 2, radius, (b - a).length, mat)
    obj.rotation_euler = (b - a).to_track_quat('Z', 'Y').to_euler()
    return obj

box('Walnut main chassis', (0, 0, 0.25), (2.5, 1.85, 0.3), walnut, 0.045)
box('Inset black top deck', (0, 0, 0.409), (2.38, 1.73, 0.025), black)
for x in (-0.96, 0.96):
    for y in (-0.65, 0.65):
        cylinder('Isolation foot', (x, y, 0.075), 0.12, 0.15, black)
cylinder('Aluminum platter rim', (-0.32, 0, 0.458), 0.77, 0.072, metal)
cylinder('Rubber platter mat', (-0.32, 0, 0.499), 0.745, 0.015, black)
cylinder('Twelve inch record', (-0.32, 0, 0.511), 0.72, 0.009, vinyl)
for i in range(16):
    bpy.ops.mesh.primitive_torus_add(major_radius=0.27 + i * 0.027,
        minor_radius=0.0011, major_segments=96, minor_segments=4,
        location=(-0.32, 0, 0.516))
    finish(bpy.context.object, 'Pressed concentric groove %02d' % i, groove)
cylinder('Record center label', (-0.32, 0, 0.518), 0.215, 0.003, label)
cylinder('Label center ring', (-0.32, 0, 0.521), 0.055, 0.003, black)
cylinder('Polished spindle', (-0.32, 0, 0.546), 0.019, 0.06, metal)

cylinder('Tonearm bearing base', (0.86, 0.56, 0.46), 0.135, 0.08, black)
cylinder('Tonearm pivot tower', (0.86, 0.56, 0.555), 0.073, 0.16, metal)
rod('Pivot cross bearing', (0.76, 0.56, 0.63), (0.96, 0.56, 0.63), 0.044, black)
rod('Rear arm shaft', (0.86, 0.56, 0.64), (0.91, 0.79, 0.64), 0.021, metal)
rod('Counterweight', (0.89, 0.69, 0.64), (0.915, 0.81, 0.64), 0.078, metal)
rod('Main tonearm tube', (0.86, 0.56, 0.64), (0.70, -0.31, 0.60), 0.023, metal)
rod('Angled tonearm end', (0.70, -0.31, 0.60), (0.43, -0.43, 0.585), 0.023, metal)
head = box('Headshell', (0.40, -0.44, 0.578), (0.19, 0.082, 0.026), black, 0.006)
head.rotation_euler.z = math.radians(24)
box('Cartridge', (0.38, -0.445, 0.548), (0.075, 0.052, 0.035), label, 0.004)
rod('Stylus', (0.37, -0.445, 0.532), (0.355, -0.447, 0.517), 0.003, metal)
rod('Arm rest post', (0.87, 0.10, 0.425), (0.87, 0.10, 0.62), 0.018, metal)
box('Arm rest cradle', (0.87, 0.10, 0.62), (0.075, 0.045, 0.025), black, 0.004)
cylinder('Start stop button', (-0.99, -0.70, 0.438), 0.055, 0.025, metal)
cylinder('Speed selector dial', (0.96, -0.65, 0.447), 0.082, 0.04, metal)
box('Speed dial index', (0.96, -0.685, 0.47), (0.009, 0.034, 0.003), black, 0.001)

hinge = bpy.data.objects.new('Dust cover hinge axis', None)
bpy.context.collection.objects.link(hinge)
hinge.location = (0, 0.87, 0.43)
hinge.rotation_euler.x = math.radians(-66)
box('Transparent dust cover roof', (0, -0.87, 0.30), (2.46, 1.78, 0.025), glass, 0.008, hinge)
for x in (-1.218, 1.218):
    box('Dust cover side wall', (x, -0.87, 0.15), (0.024, 1.78, 0.30), glass, 0.006, hinge)
for y in (-1.748, 0.008):
    box('Dust cover end wall', (0, y, 0.15), (2.46, 0.024, 0.30), glass, 0.006, hinge)
for x in (-0.82, 0.82):
    rod('Rear cover hinge barrel', (x-0.10, 0.87, 0.43), (x+0.10, 0.87, 0.43), 0.038, metal)

floor = material('Studio surface', (0.19, 0.22, 0.25))
box('Display surface', (0, 0, -0.045), (200, 200, 0.08), floor, 0)
bpy.ops.object.camera_add(location=(3.3, -4.5, 3.2))
camera = bpy.context.object
camera.name = 'Record player camera'
camera.rotation_euler = (Vector((0, 0.05, 0.80)) - camera.location).to_track_quat('-Z', 'Y').to_euler()
camera.data.type = 'ORTHO'
camera.data.ortho_scale = 4.4
bpy.context.scene.camera = camera
for name, loc, power, size in [('Key softbox', (0, -3, 5), 650, 4), ('Rim softbox', (2, 3, 4), 850, 3)]:
    bpy.ops.object.light_add(type='AREA', location=loc)
    light = bpy.context.object
    light.name = name
    light.data.energy = power
    light.data.shape = 'DISK'
    light.data.size = size
    light.rotation_euler = (Vector((0, 0, 0.5)) - light.location).to_track_quat('-Z', 'Y').to_euler()
scene = bpy.context.scene
scene.world.color = (0.22, 0.22, 0.22)
scene.render.resolution_x = 1000
scene.render.resolution_y = 850
scene.render.resolution_percentage = 100
