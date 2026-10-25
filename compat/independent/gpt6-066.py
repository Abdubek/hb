import bpy
from mathutils import Vector
from math import pi

# Self-contained curbside parking meter, front facing negative Y.
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)

def material(name, color, metallic=0.0, roughness=0.5):
    mat = bpy.data.materials.new(name)
    mat.diffuse_color = (*color, 1)
    mat.use_nodes = True
    bsdf = mat.node_tree.nodes.get('Principled BSDF')
    bsdf.inputs['Base Color'].default_value = (*color, 1)
    bsdf.inputs['Metallic'].default_value = metallic
    bsdf.inputs['Roughness'].default_value = roughness
    return mat

def box(name, location, dimensions, mat, bevel=0.01):
    bpy.ops.mesh.primitive_cube_add(size=1, location=location)
    obj = bpy.context.object
    obj.name = name
    obj.dimensions = dimensions
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    obj.data.materials.append(mat)
    if bevel:
        edge = obj.modifiers.new('Rounded edges', 'BEVEL')
        edge.width = bevel
        edge.segments = 3
        obj.modifiers.new('Weighted normals', 'WEIGHTED_NORMAL')
    return obj

def cylinder(name, location, radius, depth, mat, rotation=(0, 0, 0)):
    bpy.ops.mesh.primitive_cylinder_add(vertices=32, radius=radius, depth=depth,
                                      location=location, rotation=rotation)
    obj = bpy.context.object
    obj.name = name
    obj.data.materials.append(mat)
    bevel = obj.modifiers.new('Machined edge', 'BEVEL')
    bevel.width = 0.006
    bevel.segments = 2
    obj.modifiers.new('Weighted normals', 'WEIGHTED_NORMAL')
    return obj

def label(name, text, location, size, mat):
    data = bpy.data.curves.new(name, 'FONT')
    data.body = text
    data.align_x = 'CENTER'
    data.align_y = 'CENTER'
    data.size = size
    data.extrude = 0.0004
    obj = bpy.data.objects.new(name, data)
    bpy.context.collection.objects.link(obj)
    obj.location = location
    obj.rotation_euler = (pi / 2, 0, 0)
    obj.data.materials.append(mat)
    return obj

metal = material('Galvanized post', (0.43, 0.47, 0.50), 0.8, 0.33)
green = material('Deep green meter enamel', (0.055, 0.20, 0.16), 0.45, 0.3)
black = material('Dark recesses', (0.012, 0.018, 0.02))
lcd = material('LCD pale green', (0.48, 0.65, 0.47), 0.05)
white = material('White paint', (0.9, 0.91, 0.86))
red = material('Expired indicator', (0.8, 0.055, 0.025))
concrete = material('Sidewalk concrete', (0.48, 0.47, 0.43), roughness=0.85)
curb = material('Curb stone', (0.65, 0.64, 0.58), roughness=0.8)
asphalt = material('Road asphalt', (0.085, 0.095, 0.105), roughness=0.95)
joint = material('Pavement joints', (0.21, 0.22, 0.21))

box('Road section', (0, -1.32, -0.09), (4.4, 2.36, 0.18), asphalt, 0)
box('Raised sidewalk', (0, 0.89, 0.025), (4.4, 1.78, 0.25), concrete, 0.01)
box('Continuous curb', (0, -0.13, 0.035), (4.4, 0.26, 0.23), curb, 0.025)
for x in [-1.45, 0, 1.45]:
    box('Sidewalk expansion joint', (x, 0.95, 0.151), (0.009, 1.65, 0.002), joint, 0)
    box('Curb block joint', (x, -0.13, 0.151), (0.007, 0.20, 0.002), joint, 0)
for x in [-1.65, 1.65]:
    box('Parking bay end stripe', (x, -1.35, 0.003), (0.065, 1.8, 0.006), white, 0)
box('Parking bay outer stripe', (0, -2.22, 0.003), (3.35, 0.065, 0.006), white, 0)

post_y = 0.30
cylinder('Post mounting flange', (0, post_y, 0.177), 0.15, 0.05, metal)
for x in [-0.085, 0.085]:
    for y in [post_y - 0.085, post_y + 0.085]:
        cylinder('Anchor bolt', (x, y, 0.208), 0.016, 0.02, metal)
cylinder('Meter support pole', (0, post_y, 0.80), 0.056, 1.20, metal)
cylinder('Housing support collar', (0, post_y, 1.30), 0.086, 0.14, black)
box('Meter main housing', (0, post_y, 1.58), (0.40, 0.27, 0.59), green, 0.075)
box('Meter rounded crown', (0, post_y, 1.85), (0.39, 0.265, 0.20), green, 0.085)
box('Inset front plate', (0, 0.150, 1.62), (0.337, 0.036, 0.46), metal, 0.035)
box('Display rubber gasket', (0, 0.124, 1.73), (0.287, 0.025, 0.151), black, 0.018)
box('LCD display', (0, 0.109, 1.73), (0.255, 0.007, 0.118), lcd, 0.008)
label('LCD time', '00:00', (0, 0.103, 1.745), 0.055, black)
label('LCD time units', 'HOURS : MIN', (0, 0.103, 1.701), 0.018, black)
label('Meter identification', 'PARK  024', (0, 0.15, 1.885), 0.036, white)
box('Coin slot surround', (-0.072, 0.120, 1.581), (0.084, 0.022, 0.09), black, 0.008)
box('Coin slot trim', (-0.072, 0.105, 1.585), (0.021, 0.01, 0.065), metal, 0.003)
box('Coin insertion slit', (-0.072, 0.098, 1.585), (0.007, 0.006, 0.051), black, 0.001)
cylinder('Time purchase button', (0.077, 0.103, 1.583), 0.04, 0.025, green, (pi / 2, 0, 0))
label('Button plus', '+', (0.077, 0.087, 1.584), 0.046, white)
label('Payment instruction', 'COIN     ADD', (0, 0.124, 1.514), 0.022, black)
box('Coin return recess', (0, 0.119, 1.46), (0.16, 0.016, 0.037), black, 0.006)
box('Coin return lip', (0, 0.104, 1.438), (0.18, 0.05, 0.013), metal, 0.003)
cylinder('Expired status lamp', (0.131, 0.149, 1.874), 0.018, 0.012, red, (pi / 2, 0, 0))
box('Lower cash box door', (0, 0.157, 1.356), (0.245, 0.02, 0.08), green, 0.01)
cylinder('Cash box lock', (0.075, 0.14, 1.359), 0.015, 0.018, metal, (pi / 2, 0, 0))

bpy.ops.object.camera_add(location=(3.2, -4.6, 3.05))
camera = bpy.context.object
camera.name = 'Curbside meter camera'
camera.rotation_euler = (Vector((0, -0.25, 0.95)) - camera.location).to_track_quat('-Z', 'Y').to_euler()
camera.data.type = 'ORTHO'
camera.data.ortho_scale = 3.75
scene = bpy.context.scene
scene.camera = camera
bpy.ops.object.light_add(type='AREA', location=(-2, -3, 5))
bpy.context.object.data.energy = 850
bpy.context.object.data.size = 4
scene.world.color = (0.25, 0.25, 0.25)
scene.render.resolution_x = 900
scene.render.resolution_y = 900
scene.render.resolution_percentage = 100
