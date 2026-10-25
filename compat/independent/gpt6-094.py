import bpy
import math
from mathutils import Vector

bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)

def material(name, color, metal=0.0, rough=0.4):
    m = bpy.data.materials.new(name)
    m.diffuse_color = (*color, 1)
    m.use_nodes = True
    p = m.node_tree.nodes.get('Principled BSDF')
    p.inputs['Base Color'].default_value = (*color, 1)
    p.inputs['Metallic'].default_value = metal
    p.inputs['Roughness'].default_value = rough
    return m

paint = material('Blue gray enamel', (0.12, 0.20, 0.25), 0.35)
steel = material('Brushed hardware', (0.48, 0.53, 0.56), 0.8, 0.26)
black = material('Black rubber and markings', (0.012, 0.018, 0.023), 0, 0.6)
ivory = material('Warm white dial faces', (0.86, 0.85, 0.75), 0, 0.65)
red = material('Safety red', (0.66, 0.025, 0.018), 0.15)
green = material('Green status lens', (0.04, 0.65, 0.15), 0.15, 0.22)
yellow = material('Safety yellow', (0.95, 0.61, 0.035), 0.1)
wall = material('Concrete wall', (0.36, 0.39, 0.40), 0, 0.9)

def box(name, loc, dims, mat, bevel=0.0):
    bpy.ops.mesh.primitive_cube_add(size=1, location=loc)
    o = bpy.context.object
    o.name = name
    o.dimensions = dims
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    o.data.materials.append(mat)
    if bevel:
        b = o.modifiers.new('Rounded edges', 'BEVEL')
        b.width = bevel
        b.segments = 3
        o.modifiers.new('Weighted normals', 'WEIGHTED_NORMAL')
    return o

def cylinder(name, loc, radius, depth, mat):
    bpy.ops.mesh.primitive_cylinder_add(vertices=40, radius=radius, depth=depth, location=loc, rotation=(math.pi / 2, 0, 0))
    o = bpy.context.object
    o.name = name
    o.data.materials.append(mat)
    b = o.modifiers.new('Machined edge', 'BEVEL')
    b.width = min(0.009, depth / 5)
    b.segments = 2
    o.modifiers.new('Weighted normals', 'WEIGHTED_NORMAL')
    return o

def label(name, body, loc, size, mat=ivory):
    bpy.ops.object.text_add(location=loc, rotation=(math.pi / 2, 0, 0))
    o = bpy.context.object
    o.name = name
    o.data.body = body
    o.data.size = size
    o.data.align_x = 'CENTER'
    o.data.materials.append(mat)

box('Concrete mounting wall', (0, 0.37, 1.9), (6, 0.25, 4.4), wall, 0.025)
box('Cabinet rear mounting plate', (0, 0.20, 1.95), (2.52, 0.08, 2.42), steel, 0.03)
box('Control cabinet enclosure', (0, -0.03, 1.95), (2.40, 0.42, 2.30), paint, 0.055)
box('Door gasket seam', (0, -0.248, 1.95), (2.31, 0.024, 2.21), black, 0.03)
box('Control panel front door', (0, -0.28, 1.95), (2.26, 0.045, 2.16), paint, 0.028)
for x in (-1.04, 1.04):
    for z in (0.99, 2.91):
        cylinder('Captive door screw', (x, -0.313, z), 0.031, 0.021, steel)
        box('Screwdriver slot', (x, -0.325, z), (0.038, 0.003, 0.006), black)
for z in (1.35, 2.55):
    box('Left door hinge', (-1.17, -0.24, z), (0.10, 0.12, 0.25), steel, 0.018)
box('Station header plate', (0, -0.315, 2.80), (1.71, 0.024, 0.21), black, 0.012)
label('Station title', 'PUMP CONTROL / 02', (0, -0.331, 2.755), 0.105)

for gx, title, unit, angle in [(-0.55, 'PRESSURE', 'bar', 62), (0.55, 'FLOW', 'L/min', 115)]:
    gz = 2.30
    cylinder(title + ' outer bezel', (gx, -0.341, gz), 0.365, 0.073, steel)
    cylinder(title + ' black rim', (gx, -0.385, gz), 0.326, 0.027, black)
    cylinder(title + ' recessed dial', (gx, -0.404, gz), 0.300, 0.014, ivory)
    for i in range(21):
        a = math.radians(225 - i * 13.5)
        major = i % 5 == 0
        r = 0.260 if major else 0.268
        tick = box(title + ' scale tick', (gx + r * math.cos(a), -0.416, gz + r * math.sin(a)), (0.010 if major else 0.005, 0.006, 0.046 if major else 0.025), black)
        tick.rotation_euler[1] = math.pi / 2 - a
        if major:
            label(title + ' scale number', str(i // 5 * 25), (gx + 0.205 * math.cos(a), -0.422, gz + 0.205 * math.sin(a) - 0.018), 0.039, black)
    a = math.radians(angle)
    needle = box(title + ' needle', (gx + 0.103 * math.cos(a), -0.434, gz + 0.103 * math.sin(a)), (0.014, 0.012, 0.235), red, 0.003)
    needle.rotation_euler[1] = math.pi / 2 - a
    cylinder(title + ' needle pivot', (gx, -0.446, gz), 0.033, 0.021, black)
    label(title + ' dial units', unit, (gx, -0.423, gz - 0.12), 0.047, black)
    label(title + ' caption', title, (gx, -0.322, 1.845), 0.074)

for i, x in enumerate((-0.72, -0.24, 0.24)):
    cylinder('Toggle mounting washer', (x, -0.33, 1.55), 0.09, 0.036, steel)
    cylinder('Toggle pivot boot', (x, -0.366, 1.55), 0.052, 0.055, black)
    lever = cylinder('Toggle lever ' + str(i + 1), (x, -0.438, 1.58 if i != 1 else 1.52), 0.024, 0.15, steel)
    lever.rotation_euler[0] += 0.38 if i != 1 else -0.38
    label('Toggle legend', ['POWER', 'AUTO', 'AUX'][i], (x, -0.324, 1.32), 0.062)
    cylinder('Status lamp socket', (x, -0.331, 1.14), 0.048, 0.036, black)
    cylinder('Status indicator lens', (x, -0.357, 1.14), 0.034, 0.023, green if i != 1 else yellow)
cylinder('Emergency stop yellow collar', (0.77, -0.335, 1.49), 0.20, 0.045, yellow)
cylinder('Emergency stop neck', (0.77, -0.395, 1.49), 0.11, 0.11, black)
cylinder('Emergency stop mushroom button', (0.77, -0.473, 1.49), 0.155, 0.085, red)
label('Emergency legend', 'E-STOP', (0.77, -0.324, 1.19), 0.075)
for x in (-0.75, 0.75):
    conduit = cylinder('Supply conduit', (x, 0.10, 0.36), 0.05, 0.83, steel)
    conduit.rotation_euler = (0, 0, 0)
    gland = cylinder('Cable entry gland', (x, 0.10, 0.79), 0.085, 0.12, black)
    gland.rotation_euler = (0, 0, 0)

def aim(obj, target):
    obj.rotation_euler = (Vector(target) - obj.location).to_track_quat('-Z', 'Y').to_euler()

for loc, energy, size in [((1, -4, 5), 650, 4), ((-4, -2, 3), 350, 3)]:
    bpy.ops.object.light_add(type='AREA', location=loc)
    bpy.context.object.data.energy = energy
    bpy.context.object.data.size = size
    aim(bpy.context.object, (0, 0, 1.9))
bpy.ops.object.camera_add(location=(3.1, -7, 3.3))
camera = bpy.context.object
camera.name = 'Control station camera'
aim(camera, (0, -0.1, 1.77))
camera.data.type = 'ORTHO'
camera.data.ortho_scale = 4.15
scene = bpy.context.scene
scene.camera = camera
scene.world.color = (0.2, 0.2, 0.2)
scene.render.resolution_x = 1000
scene.render.resolution_y = 1100
scene.render.resolution_percentage = 100
