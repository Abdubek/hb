import bpy, math
from mathutils import Vector

bpy.ops.wm.read_factory_settings(use_empty=True)

def mat(name, color, metallic=0.0, roughness=0.45):
    m = bpy.data.materials.new(name)
    m.diffuse_color = (*color, 1)
    m.use_nodes = True
    p = m.node_tree.nodes.get('Principled BSDF')
    p.inputs['Base Color'].default_value = (*color, 1)
    p.inputs['Metallic'].default_value = metallic
    p.inputs['Roughness'].default_value = roughness
    return m

def box(name, loc, size, material, bevel=0.0):
    bpy.ops.mesh.primitive_cube_add(size=1, location=loc)
    o = bpy.context.object
    o.name = name
    o.dimensions = size
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    o.data.materials.append(material)
    if bevel:
        mod = o.modifiers.new('Rounded edges', 'BEVEL')
        mod.width = bevel
        mod.segments = 3
        o.modifiers.new('Weighted normals', 'WEIGHTED_NORMAL')
    return o

def rod(name, a, b, radius, material):
    a, b = Vector(a), Vector(b)
    bpy.ops.mesh.primitive_cylinder_add(vertices=24, radius=radius, depth=(b-a).length, location=(a+b)/2)
    o = bpy.context.object
    o.name = name
    o.rotation_euler = (b-a).to_track_quat('Z', 'Y').to_euler()
    o.data.materials.append(material)
    for p in o.data.polygons:
        p.use_smooth = True
    mod = o.modifiers.new('Edge rounding', 'BEVEL')
    mod.width = 0.012
    mod.segments = 2
    o.modifiers.new('Weighted normals', 'WEIGHTED_NORMAL')
    return o

def label(body, loc, size, material):
    bpy.ops.object.text_add(location=loc, rotation=(math.pi/2, 0, 0))
    o = bpy.context.object
    o.name = 'Sign: ' + body
    o.data.body = body
    o.data.align_x = 'CENTER'
    o.data.align_y = 'CENTER'
    o.data.size = size
    o.data.extrude = 0.001
    o.data.materials.append(material)
    return o

def area(name, loc, energy, size, target):
    bpy.ops.object.light_add(type='AREA', location=loc)
    o = bpy.context.object
    o.name = name
    o.data.energy = energy
    o.data.shape = 'DISK'
    o.data.size = size
    o.rotation_euler = (Vector(target)-o.location).to_track_quat('-Z','Y').to_euler()

steel = mat('Powder-coated charcoal steel', (0.055,0.082,0.095), 0.7, 0.29)
teal = mat('Transit teal', (0.025,0.32,0.34), 0.35, 0.3)
wood = mat('Warm bench slats', (0.48,0.22,0.075), 0, 0.42)
concrete = mat('Pale concrete', (0.49,0.52,0.51), 0, 0.85)
road = mat('Asphalt', (0.065,0.078,0.09), 0, 0.92)
white = mat('Warm white lettering', (0.91,0.94,0.91), 0, 0.35)
yellow = mat('Safety yellow', (0.96,0.61,0.08), 0, 0.5)
paper = mat('Timetable paper', (0.86,0.89,0.83), 0, 0.65)
glass = mat('Clear architectural glass', (0.84,0.96,0.95), 0, 0.065)
p = glass.node_tree.nodes.get('Principled BSDF')
p.inputs['Transmission Weight'].default_value = 1.0
p.inputs['IOR'].default_value = 1.46
lamp = mat('Ceiling light diffuser', (0.83,0.95,1.0))
p = lamp.node_tree.nodes.get('Principled BSDF')
p.inputs['Emission Color'].default_value = (0.76,0.91,1.0,1)
p.inputs['Emission Strength'].default_value = 2.5

box('Ground', (0,0,-0.19), (200,200,0.2), road)
box('Raised pavement island', (0,0,-0.015), (6.8,4.2,0.19), concrete, 0.055)
for x in [-2.8,-1.4,0,1.4,2.8]:
    box('Paving joint', (x,0,0.083), (0.012,4.05,0.004), steel)
box('Curb safety strip', (0,-1.97,0.086), (5.7,0.11,0.009), yellow, 0.008)

for x in [-2.45,2.45]:
    for y in [-0.77,0.88]:
        box('Column base plate', (x,y,0.12), (0.29,0.28,0.07), steel, 0.018)
        box('Structural column', (x,y,1.53), (0.105,0.105,2.83), steel, 0.018)
        for dx in [-0.095,0.095]:
            for dy in [-0.09,0.09]:
                rod('Base anchor bolt', (x+dx,y+dy,0.155), (x+dx,y+dy,0.18), 0.019, steel)

for x in [-2.45,2.45]:
    box('Transparent side panel', (x,0.055,1.51), (0.018,1.49,2.47), glass, 0.008)
    for z in [0.28,2.75]:
        box('Side panel rail', (x,0.055,z), (0.065,1.65,0.055), steel, 0.009)
    for y in [-0.65,0.76]:
        for z in [0.43,2.58]:
            box('Glass clamp', (x,y,z), (0.065,0.10,0.065), steel, 0.008)
    for y in [-0.53,-0.25,0.03,0.31,0.59]:
        box('Side visibility marker', (x + (0.013 if x>0 else -0.013),y,1.47), (0.006,0.14,0.045), white, 0.003)
for x in [-1.225,1.225]:
    box('Rear glazing', (x,0.88,1.51), (2.33,0.018,2.47), glass, 0.008)
box('Rear center mullion', (0,0.88,1.52), (0.065,0.065,2.55), steel, 0.009)
for z in [0.28,2.75]:
    box('Rear glazing rail', (0,0.88,z), (4.9,0.065,0.055), steel, 0.009)
for x in [-2,-1.6,-1.2,-0.8,-0.4,0.4,0.8,1.2,1.6,2]:
    box('Rear visibility marker', (x,0.864,1.47), (0.17,0.007,0.045), white, 0.003)

box('Roof structural slab', (0,0.03,2.97), (5.55,2.31,0.16), steel, 0.065)
box('Teal roof cap', (0,0.03,3.075), (5.67,2.43,0.085), teal, 0.04)
box('Front fascia sign', (0,-1.145,2.98), (4.85,0.027,0.22), teal, 0.012)
label('CENTRAL AVENUE  /  24', (0,-1.165,2.978), 0.145, white)
for x in [-1.65,1.65]:
    box('Under-roof light', (x,0.02,2.881), (0.65,0.22,0.025), lamp, 0.015)
    area('Shelter downlight', (x,0.02,2.84), 45, 0.7, (x,0,0))

for x in [-1.42,1.42]:
    box('Bench pedestal', (x,0.36,0.40), (0.11,0.43,0.6), steel, 0.025)
    box('Bench foot', (x,0.32,0.14), (0.28,0.64,0.075), steel, 0.025)
    box('Back support', (x,0.67,0.86), (0.065,0.065,1.02), steel, 0.012)
for y in [0.07,0.24,0.41,0.58]:
    box('Seat timber slat', (0,y,0.72), (3.75,0.145,0.09), wood, 0.025)
for z in [1.01,1.20,1.39]:
    box('Backrest timber slat', (0,0.675,z), (3.75,0.08,0.15), wood, 0.025)
for x in [-1.78,0,1.78]:
    rod('Armrest front riser', (x,0.02,0.72), (x,0.02,0.94), 0.028, steel)
    rod('Armrest top', (x,0.02,0.94), (x,0.58,0.94), 0.032, steel)

box('Timetable frame', (1.96,0.817,1.98), (0.57,0.065,0.88), steel, 0.025)
box('Timetable face', (1.96,0.779,1.98), (0.49,0.015,0.79), paper, 0.009)
label('24', (1.96,0.768,2.22), 0.18, teal)
label('CITY SERVICE', (1.96,0.767,2.07), 0.047, steel)
for i in range(7):
    box('Timetable row', (1.96,0.767,1.97-i*0.055), (0.37,0.004,0.011), teal)

area('Large soft key', (0,-5,8), 1600, 6, (0,0,1))
area('Glass edge light', (3,4,6), 1900, 5, (0,0,1.4))
area('Fill', (-5,-1,4), 850, 4, (0,0,1))
bpy.ops.object.camera_add(location=(7.5,-10.2,5.5))
cam = bpy.context.object
cam.rotation_euler = (Vector((0,0,1.45))-cam.location).to_track_quat('-Z','Y').to_euler()
cam.data.type = 'ORTHO'
cam.data.ortho_scale = 8.7
scene = bpy.context.scene
scene.camera = cam
scene.render.engine = 'CYCLES'
scene.cycles.samples = 64
scene.cycles.max_bounces = 12
scene.cycles.transmission_bounces = 8
scene.world.color = (0.24,0.24,0.24)
scene.render.resolution_x = 1500
scene.render.resolution_y = 1100
scene.render.resolution_percentage = 100
scene.view_settings.view_transform = 'AgX'
