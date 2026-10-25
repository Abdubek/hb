import bpy, math
from mathutils import Vector

# Parking meter; the front of the meter faces -Y.
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)

def material(name, color, metallic=0.0, roughness=0.45):
    m = bpy.data.materials.new(name)
    m.diffuse_color = (*color, 1)
    m.use_nodes = True
    p = m.node_tree.nodes.get('Principled BSDF')
    p.inputs['Base Color'].default_value = (*color, 1)
    p.inputs['Metallic'].default_value = metallic
    p.inputs['Roughness'].default_value = roughness
    return m

def finish(obj, name, mat, bevel=0):
    obj.name = name
    obj.data.materials.append(mat)
    if bevel:
        mod = obj.modifiers.new('Soft manufactured edges', 'BEVEL')
        mod.width = bevel
        mod.segments = 3
        obj.modifiers.new('Weighted normals', 'WEIGHTED_NORMAL')
    return obj

def box(name, loc, size, mat, bevel=0.02):
    bpy.ops.mesh.primitive_cube_add(size=1, location=loc)
    obj = bpy.context.object
    obj.dimensions = size
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    return finish(obj, name, mat, bevel)

def rod(name, a, b, radius, mat, vertices=48):
    a, b = Vector(a), Vector(b)
    bpy.ops.mesh.primitive_cylinder_add(vertices=vertices, radius=radius, depth=(b-a).length, location=(a+b)/2)
    obj = bpy.context.object
    obj.rotation_quaternion = (b-a).to_track_quat('Z', 'Y')
    obj.rotation_mode = 'QUATERNION'
    for p in obj.data.polygons:
        p.use_smooth = len(p.vertices) == 4
    return finish(obj, name, mat, 0.006)

def label(name, body, loc, size, mat):
    curve = bpy.data.curves.new(name, 'FONT')
    curve.body = body
    curve.align_x = 'CENTER'
    curve.align_y = 'CENTER'
    curve.size = size
    curve.extrude = 0.0006
    obj = bpy.data.objects.new(name, curve)
    bpy.context.collection.objects.link(obj)
    obj.location = loc
    obj.rotation_euler = (math.pi/2, 0, 0)
    curve.materials.append(mat)
    return obj

steel = material('Brushed galvanized steel', (0.42, 0.48, 0.51), 0.82, 0.3)
body = material('Blue green enamel', (0.065, 0.23, 0.24), 0.55, 0.27)
black = material('Recesses and rubber', (0.018, 0.025, 0.028), 0.1, 0.55)
screen = material('Muted LCD glass', (0.29, 0.40, 0.34), 0.18, 0.2)
white = material('Cream lettering', (0.88, 0.88, 0.76), 0, 0.55)
red = material('Red indicator', (0.8, 0.065, 0.025), 0.1, 0.28)
concrete = material('Sidewalk concrete', (0.48, 0.47, 0.43), 0, 0.9)
curbmat = material('Pale curb concrete', (0.64, 0.63, 0.58), 0, 0.85)
asphalt = material('Asphalt', (0.095, 0.11, 0.12), 0, 0.96)
yellow = material('Road marking yellow', (0.84, 0.60, 0.09), 0, 0.8)
# Procedural aggregate, without external textures.
nt = asphalt.node_tree
noise = nt.nodes.new('ShaderNodeTexNoise')
noise.inputs['Scale'].default_value = 170
noise.inputs['Detail'].default_value = 2
bump = nt.nodes.new('ShaderNodeBump')
bump.inputs['Strength'].default_value = 0.3
bump.inputs['Distance'].default_value = 0.035
nt.links.new(noise.outputs['Fac'], bump.inputs['Height'])
nt.links.new(bump.outputs['Normal'], nt.nodes.get('Principled BSDF').inputs['Normal'])
box('Road slab', (0, -0.9, -0.13), (8, 6, 0.25), asphalt, 0.04)
box('Raised sidewalk', (0, 1.37, 0.025), (8, 2.7, 0.30), concrete, 0.02)
for i in range(8):
    box('Individual curb stone', (-3.5+i, -0.075, 0.055), (0.985, 0.25, 0.34), curbmat, 0.018)
for x in [-3, -1.5, 0, 1.5, 3]:
    box('Sidewalk expansion joint', (x, 1.42, 0.178), (0.012, 2.55, 0.003), black, 0)
for x in [-2.6, 2.6]:
    box('Parking bay stripe', (x, -1.55, 0.001), (0.085, 2.55, 0.008), yellow, 0.005)

py = 0.49
rod('Foot flange', (0, py, 0.18), (0, py, 0.235), 0.155, steel)
rod('Upright post', (0, py, 0.22), (0, py, 1.87), 0.06, steel)
rod('Lower protective collar', (0, py, 0.23), (0, py, 0.42), 0.073, body)
for x in [-0.082, 0.082]:
    for y in [py-0.082, py+0.082]:
        rod('Flange anchor bolt', (x, y, 0.23), (x, y, 0.254), 0.019, steel, 6)
box('Meter cast housing', (0, py, 2.03), (0.47, 0.31, 0.73), body, 0.105)
box('Front bezel', (0, py-0.163, 2.055), (0.405, 0.047, 0.61), steel, 0.07)
box('Inset face panel', (0, py-0.19, 2.055), (0.352, 0.019, 0.55), black, 0.045)
box('LCD recess', (0, py-0.204, 2.17), (0.296, 0.014, 0.16), steel, 0.016)
box('LCD screen', (0, py-0.214, 2.17), (0.273, 0.009, 0.132), screen, 0.01)
label('Time remaining', '01:24', (0, py-0.221, 2.182), 0.068, black)
label('LCD caption', 'TIME REMAINING', (0, py-0.221, 2.132), 0.018, black)
label('Meter header', 'PARK', (0, py-0.204, 2.292), 0.046, white)
box('Coin slot surround', (-0.075, py-0.209, 2.001), (0.13, 0.027, 0.047), steel, 0.011)
box('Coin slot opening', (-0.075, py-0.225, 2.001), (0.092, 0.008, 0.009), black, 0.003)
label('Coin caption', 'COINS', (-0.075, py-0.207, 2.043), 0.023, white)
rod('Payment knob', (0.086, py-0.201, 1.998), (0.086, py-0.25, 1.998), 0.047, steel)
box('Knob grip', (0.086, py-0.261, 1.998), (0.016, 0.018, 0.073), black, 0.005)
rod('Status lamp bezel', (-0.128, py-0.2, 2.289), (-0.128, py-0.213, 2.289), 0.019, steel)
rod('Status lamp', (-0.128, py-0.211, 2.289), (-0.128, py-0.218, 2.289), 0.013, red)
box('Rate notice plate', (0, py-0.206, 1.888), (0.276, 0.011, 0.094), body, 0.009)
label('Rate notice', '2 HOUR LIMIT\nPAY TO PARK', (0, py-0.214, 1.889), 0.027, white)
for x in [-0.146, 0.146]:
    rod('Face screw', (x, py-0.204, 1.828), (x, py-0.215, 1.828), 0.008, steel, 16)
box('Rear collection door', (0, py+0.16, 1.973), (0.29, 0.018, 0.36), steel, 0.025)
rod('Side lock cylinder', (0.228, py, 1.84), (0.242, py, 1.84), 0.025, steel)
box('Lock keyway', (0.245, py, 1.84), (0.004, 0.006, 0.026), black, 0.001)
label('Post identification', 'P-042', (0, py-0.065, 1.59), 0.031, black)

world = bpy.context.scene.world or bpy.data.worlds.new('World')
bpy.context.scene.world = world
world.use_nodes = True
world.node_tree.nodes['Background'].inputs[0].default_value = (0.23, 0.29, 0.36, 1)
world.node_tree.nodes['Background'].inputs[1].default_value = 0.45

def area(name, loc, power, size, target):
    bpy.ops.object.light_add(type='AREA', location=loc)
    light = bpy.context.object
    light.name = name
    light.data.energy = power
    light.data.shape = 'DISK'
    light.data.size = size
    light.rotation_euler = (Vector(target)-light.location).to_track_quat('-Z', 'Y').to_euler()
area('Large warm key', (3, -4, 6), 850, 4, (0, 0, 1))
area('Sidewalk fill', (-3, 2, 4), 650, 3, (0, 0, 1))
bpy.ops.object.camera_add(location=(4, -6, 3.65))
cam = bpy.context.object
cam.rotation_euler = (Vector((0, 0.25, 1.15))-cam.location).to_track_quat('-Z', 'Y').to_euler()
cam.data.type = 'ORTHO'
cam.data.ortho_scale = 4.2
bpy.context.scene.camera = cam
bpy.context.scene.render.resolution_x = 1200
bpy.context.scene.render.resolution_y = 1200
bpy.context.scene.render.resolution_percentage = 100
