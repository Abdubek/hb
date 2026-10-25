import bpy
import math
from mathutils import Vector

bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)

def material(name, color, metallic=0.0, roughness=0.4):
    m = bpy.data.materials.new(name)
    m.diffuse_color = (*color,1)
    m.use_nodes = True
    bs = m.node_tree.nodes.get('Principled BSDF')
    bs.inputs['Base Color'].default_value = (*color,1)
    bs.inputs['Metallic'].default_value = metallic
    bs.inputs['Roughness'].default_value = roughness
    return m

paint = material('Deep teal enamel', (0.025,0.22,0.23), 0.25)
steel = material('Brushed stainless steel', (0.58,0.64,0.66), 0.85, 0.28)
black = material('Rubber and black handles', (0.025,0.03,0.032))
wood = material('Oak countertop', (0.53,0.30,0.13))
white = material('Ivory ceramic', (0.94,0.91,0.82))
coffee = material('Coffee beans', (0.11,0.045,0.018))
glass = material('Smoked hopper shell', (0.19,0.24,0.25), 0.25)
ground = material('Studio ground', (0.29,0.32,0.33))

def box(name, loc, size, mat, bevel=0.02):
    bpy.ops.mesh.primitive_cube_add(size=1, location=loc)
    o = bpy.context.object
    o.name = name
    o.dimensions = size
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    o.data.materials.append(mat)
    if bevel:
        mod = o.modifiers.new('Rounded manufactured edges', 'BEVEL')
        mod.width = bevel
        mod.segments = 3
        o.modifiers.new('Weighted corner normals', 'WEIGHTED_NORMAL')
    return o

def cylinder(name, loc, radius, depth, mat, axis='Z'):
    rotation = {'Z':(0,0,0),'X':(0,math.pi/2,0),'Y':(math.pi/2,0,0)}[axis]
    bpy.ops.mesh.primitive_cylinder_add(vertices=32, radius=radius, depth=depth, location=loc, rotation=rotation)
    o = bpy.context.object
    o.name = name
    o.data.materials.append(mat)
    bevel = o.modifiers.new('Machined edge', 'BEVEL')
    bevel.width = min(0.008, depth*0.12)
    bevel.segments = 2
    o.modifiers.new('Weighted normals', 'WEIGHTED_NORMAL')
    return o

def rod(name, a, b, radius, mat):
    a, b = Vector(a), Vector(b)
    o = cylinder(name, (a+b)/2, radius, (b-a).length, mat)
    o.rotation_euler = (b-a).to_track_quat('Z','Y').to_euler()
    return o

def cup(name, x, y, z):
    n = 32
    verts = []
    for radius, height in [(0.060,0),(0.078,0.13),(0.066,0.13),(0.050,0.018)]:
        verts.extend([(x+radius*math.cos(i*2*math.pi/n),y+radius*math.sin(i*2*math.pi/n),z+height) for i in range(n)])
    faces = []
    for ring in range(3):
        for i in range(n):
            j = (i+1)%n
            faces.append((ring*n+i,ring*n+j,(ring+1)*n+j,(ring+1)*n+i))
    faces.extend([tuple(reversed(range(n))),tuple(range(3*n,4*n))])
    mesh = bpy.data.meshes.new(name+' mesh')
    mesh.from_pydata(verts, [], faces)
    mesh.update()
    o = bpy.data.objects.new(name, mesh)
    bpy.context.collection.objects.link(o)
    o.data.materials.append(white)
    bpy.ops.mesh.primitive_torus_add(major_segments=24, minor_segments=8, location=(x+0.085,y,z+0.072), major_radius=0.043, minor_radius=0.012, rotation=(math.pi/2,0,0))
    bpy.context.object.name = name+' handle'
    bpy.context.object.data.materials.append(white)

box('Display plinth', (0,0,-0.065), (3.7,2.7,0.13), ground, 0.05)
for x in (-0.82,0.82):
    for y in (-0.43,0.43):
        cylinder('Caster tire', (x,y,0.18), 0.18, 0.12, black, 'X')
        cylinder('Wheel hub', (x,y,0.18), 0.085, 0.13, steel, 'X')
        for dx in (-0.085,0.085):
            box('Caster fork plate', (x+dx,y,0.265), (0.035,0.085,0.21), steel, 0.009)
        cylinder('Caster swivel bearing', (x,y,0.385), 0.085, 0.06, steel)
box('Cart chassis', (0,0,0.435), (1.94,1.13,0.10), steel)
box('Cart cabinet body', (0,0,0.85), (1.90,1.08,0.76), paint, 0.055)
for x in (-0.46,0.46):
    box('Front cabinet door', (x,-0.554,0.835), (0.88,0.04,0.62), paint, 0.015)
    rod('Door pull', (x-0.13,-0.607,1.04), (x+0.13,-0.607,1.04), 0.019, steel)
box('Oak worktop', (0,0,1.28), (2.07,1.24,0.12), wood, 0.035)
box('Stainless work surface', (0,0,1.348), (1.97,1.15,0.018), steel, 0.015)
for y in (-0.40,0.40):
    rod('Push handle bracket', (0.94,y,1.10), (1.23,y,1.10), 0.025, steel)
rod('Cart push handle', (1.23,-0.40,1.10), (1.23,0.40,1.10), 0.038, black)

box('Espresso machine body', (-0.28,0.19,1.72), (1.03,0.59,0.69), steel, 0.055)
box('Espresso machine top cover', (-0.28,0.19,2.075), (1.08,0.62,0.05), paint)
box('Dark recessed brewing bay', (-0.28,-0.119,1.62), (0.90,0.03,0.36), black, 0.01)
box('Control fascia', (-0.28,-0.145,1.96), (0.95,0.07,0.17), paint)
box('Drip tray', (-0.28,-0.27,1.405), (1.05,0.43,0.07), black, 0.018)
for i in range(13):
    box('Drip tray grate bar', (-0.75+i*0.078,-0.27,1.448), (0.018,0.38,0.014), steel, 0.004)
for x in (-0.53,-0.05):
    cylinder('Brew group', (x,-0.20,1.79), 0.092, 0.095, steel)
    rod('Portafilter handle', (x,-0.22,1.77), (x,-0.48,1.77), 0.031, black)
    cylinder('Coffee outlet', (x,-0.22,1.71), 0.022, 0.06, steel)
    cup('Serving espresso cup', x, -0.25, 1.456)
    cylinder('Brew button', (x,-0.19,1.96), 0.031, 0.018, white, 'Y')
cylinder('Pressure gauge bezel', (-0.28,-0.19,1.96), 0.060, 0.018, steel, 'Y')
cylinder('Pressure gauge face', (-0.28,-0.203,1.96), 0.049, 0.006, white, 'Y')
rod('Gauge needle', (-0.28,-0.21,1.96), (-0.303,-0.21,1.985), 0.003, black)
rod('Steam wand upper', (0.20,-0.12,1.83), (0.31,-0.27,1.68), 0.012, steel)
rod('Steam wand lower', (0.31,-0.27,1.68), (0.31,-0.30,1.52), 0.012, steel)
box('Grinder base', (0.69,0.13,1.40), (0.38,0.44,0.08), black)
cylinder('Grinder motor', (0.69,0.20,1.64), 0.145, 0.43, paint)
cylinder('Hopper collar', (0.69,0.20,1.89), 0.10, 0.08, steel)
cylinder('Smoked bean hopper', (0.69,0.20,2.055), 0.18, 0.25, glass)
cylinder('Beans visible at hopper top', (0.69,0.20,2.184), 0.165, 0.008, coffee)
cylinder('Hopper lid', (0.69,0.20,2.215), 0.19, 0.04, black)
box('Grinder dispensing chute', (0.69,0.015,1.72), (0.12,0.20,0.10), steel)
cup('Grinder dosing cup', 0.69, -0.07, 1.445)
for x in (-0.55,-0.27,0.01):
    cup('Cup warming rack cup', x, 0.20, 2.105)

curve = bpy.data.curves.new('Cart branding', 'FONT')
curve.body = 'ESPRESSO'
curve.align_x = 'CENTER'
curve.size = 0.115
curve.extrude = 0.001
sign = bpy.data.objects.new('Espresso cart lettering', curve)
bpy.context.collection.objects.link(sign)
sign.location = (0,-0.582,0.76)
sign.rotation_euler = (math.pi/2,0,0)
sign.data.materials.append(white)
world = bpy.context.scene.world or bpy.data.worlds.new('Studio world')
bpy.context.scene.world = world
world.use_nodes = True
world.node_tree.nodes['Background'].inputs[1].default_value = 0.45
bpy.ops.object.light_add(type='AREA', location=(0,-3,6))
bpy.context.object.data.energy = 850
bpy.context.object.data.size = 4
bpy.ops.object.camera_add(location=(3.7,-5.2,3.45))
camera = bpy.context.object
camera.name = 'Espresso cart presentation camera'
camera.rotation_euler = (Vector((0,0,1.12))-camera.location).to_track_quat('-Z','Y').to_euler()
camera.data.type = 'ORTHO'
camera.data.ortho_scale = 3.7
bpy.context.scene.camera = camera
bpy.context.scene.render.resolution_x = 1000
bpy.context.scene.render.resolution_y = 1000
