import bpy
import math
from mathutils import Vector

# Watch displayed flat, with its bracelet extended along Y.
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)

def material(name, color, metallic=0, roughness=0.35):
    m = bpy.data.materials.new(name)
    m.diffuse_color = (*color, 1)
    m.use_nodes = True
    bs = m.node_tree.nodes.get('Principled BSDF')
    bs.inputs['Base Color'].default_value = (*color, 1)
    bs.inputs['Metallic'].default_value = metallic
    bs.inputs['Roughness'].default_value = roughness
    return m

steel = material('Brushed stainless steel', (0.48, 0.55, 0.61), 0.85, 0.28)
polish = material('Polished steel', (0.75, 0.8, 0.85), 0.95, 0.16)
dial = material('Midnight blue dial', (0.012, 0.037, 0.065), 0.2, 0.4)
lume = material('Ivory luminous inserts', (0.83, 0.9, 0.78), 0.1)
red = material('Red second hand', (0.8, 0.035, 0.025), 0.3)
dark = material('Dark recessed seams', (0.035, 0.045, 0.052), 0.45)
ground = material('Display surface', (0.11, 0.14, 0.17))

def box(name, loc, dims, mat, bevel=0.025):
    bpy.ops.mesh.primitive_cube_add(size=1, location=loc)
    o = bpy.context.object
    o.name = name
    o.dimensions = dims
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    o.data.materials.append(mat)
    if bevel:
        mod = o.modifiers.new('Rounded edges', 'BEVEL')
        mod.width = bevel
        mod.segments = 3
        o.modifiers.new('Weighted normals', 'WEIGHTED_NORMAL')
    return o

def cylinder(name, loc, radius, depth, mat, vertices=64):
    bpy.ops.mesh.primitive_cylinder_add(vertices=vertices, radius=radius,
                                      depth=depth, location=loc)
    o = bpy.context.object
    o.name = name
    o.data.materials.append(mat)
    mod = o.modifiers.new('Machined edges', 'BEVEL')
    mod.width = 0.018
    mod.segments = 3
    o.modifiers.new('Weighted normals', 'WEIGHTED_NORMAL')
    return o

def ring(name, outer, inner, z, height, mat):
    verts, faces = [], []
    n = 96
    for radius, zz in [(outer, z-height/2), (outer, z+height/2),
                       (inner, z-height/2), (inner, z+height/2)]:
        verts.extend((radius*math.cos(i*2*math.pi/n),
                      radius*math.sin(i*2*math.pi/n), zz) for i in range(n))
    for i in range(n):
        j = (i+1) % n
        faces.extend([(i, j, n+j, n+i), (n+i, n+j, 3*n+j, 3*n+i),
                      (2*n+j, 2*n+i, 3*n+i, 3*n+j), (j, i, 2*n+i, 2*n+j)])
    mesh = bpy.data.meshes.new(name)
    mesh.from_pydata(verts, [], faces)
    mesh.update()
    o = bpy.data.objects.new(name, mesh)
    bpy.context.collection.objects.link(o)
    o.data.materials.append(mat)
    bevel = o.modifiers.new('Bezel edge polish', 'BEVEL')
    bevel.width = 0.012
    bevel.segments = 2
    o.modifiers.new('Weighted normals', 'WEIGHTED_NORMAL')
    return o

cylinder('Round case body', (0, 0, 0.39), 1.04, 0.38, steel)
cylinder('Case back', (0, 0, 0.19), 0.93, 0.07, dark)
ring('Raised polished bezel', 1.045, 0.91, 0.598, 0.11, polish)
cylinder('Recessed blue dial', (0, 0, 0.585), 0.912, 0.032, dial)
for sign in (-1, 1):
    for x in (-0.59, 0.59):
        lug = box('Case lug', (x, sign*1.005, 0.36), (0.24, 0.46, 0.28), steel, 0.06)
    for i in range(8):
        y = sign*(1.26+i*0.285)
        width = 1.13-0.026*i
        box('Bracelet %s link %02d core' % (sign, i), (0, y, 0.285),
            (width-0.04, 0.247, 0.135), dark, 0.035)
        for side in (-1, 1):
            box('Bracelet %s link %02d outer %s' % (sign, i, side),
                (side*(width/2-0.16), y, 0.34), (0.32, 0.261, 0.2), steel, 0.045)
        box('Bracelet %s link %02d polished center' % (sign, i),
            (0, y, 0.355), (width-0.67, 0.249, 0.22), polish, 0.035)
box('Folding clasp cover', (0, -3.62, 0.31), (0.91, 0.4, 0.19), steel, 0.055)
box('Clasp release inset', (0, -3.64, 0.408), (0.38, 0.09, 0.014), dark, 0.012)
crown = cylinder('Winding crown', (1.16, 0, 0.405), 0.17, 0.25, steel, 48)
crown.rotation_euler.y = math.pi/2
for i in range(24):
    a = 2*math.pi*i/24
    ridge = box('Crown grip flute %02d' % i,
        (1.17, 0.168*math.sin(a), 0.405+0.168*math.cos(a)),
        (0.19, 0.021, 0.021), polish, 0.006)
    ridge.rotation_euler.x = -a
for i in range(60):
    a = 2*math.pi*i/60
    major = i % 5 == 0
    marker = box('Dial index %02d' % i,
        (0.818*math.sin(a), 0.818*math.cos(a), 0.614),
        (0.045 if major else 0.014, 0.13 if major else 0.046, 0.016),
        lume if major else steel, 0.004)
    marker.rotation_euler.z = -a

def hand(name, angle, length, width, z, mat):
    a = math.radians(angle)
    o = box(name, (math.sin(a)*(length/2-0.055),
                  math.cos(a)*(length/2-0.055), z), (width, length, 0.024), mat, 0.009)
    o.rotation_euler.z = -a
    return o

hand('Hour hand at ten', 300, 0.57, 0.074, 0.65, lume)
hand('Minute hand at two', 60, 0.77, 0.048, 0.685, lume)
hand('Sweep second hand', 185, 0.85, 0.018, 0.721, red)
cylinder('Hand pivot cap', (0, 0, 0.744), 0.062, 0.027, polish, 32)

def text(name, body, loc, size, mat):
    curve = bpy.data.curves.new(name, 'FONT')
    curve.body = body
    curve.align_x = 'CENTER'
    curve.align_y = 'CENTER'
    curve.size = size
    obj = bpy.data.objects.new(name, curve)
    bpy.context.collection.objects.link(obj)
    obj.location = loc
    obj.data.materials.append(mat)

text('Dial brand', 'MERIDIAN', (0, 0.36, 0.607), 0.105, lume)
text('Dial specification', 'AUTOMATIC', (0, -0.37, 0.607), 0.069, steel)
box('Date aperture surround', (0.61, 0, 0.623), (0.21, 0.17, 0.025), polish, 0.013)
box('Date window', (0.61, 0, 0.638), (0.174, 0.138, 0.007), lume, 0.003)
text('Date numeral', '08', (0.61, 0, 0.644), 0.11, dial)
box('Display plinth', (0, 0, 0.04), (4.4, 8.5, 0.2), ground, 0.1)
bpy.context.scene.world = bpy.data.worlds.new('Watch studio')
bpy.context.scene.world.use_nodes = True
bpy.context.scene.world.node_tree.nodes['Background'].inputs[1].default_value = 0.45
for name, loc, energy, size in [('Key softbox', (-3, -2, 7), 650, 5),
                                ('Rim softbox', (4, 3, 5), 450, 4)]:
    bpy.ops.object.light_add(type='AREA', location=loc)
    light = bpy.context.object
    light.name = name
    light.data.energy = energy
    light.data.size = size
    light.rotation_euler = (Vector((0, 0, 0.3))-light.location).to_track_quat('-Z', 'Y').to_euler()
bpy.ops.object.camera_add(location=(3, -4.5, 11))
cam = bpy.context.object
cam.name = 'Watch product camera'
cam.rotation_euler = (Vector((0, -0.1, 0.3))-cam.location).to_track_quat('-Z', 'Y').to_euler()
cam.data.type = 'ORTHO'
cam.data.ortho_scale = 8.5
bpy.context.scene.camera = cam
bpy.context.scene.render.resolution_x = 1000
bpy.context.scene.render.resolution_y = 1200
bpy.context.scene.render.resolution_percentage = 100
