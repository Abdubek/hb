import bpy, math, random
from mathutils import Vector

bpy.ops.wm.read_factory_settings(use_empty=True)
random.seed(17)

def mat(name, color, metallic=0.0, roughness=0.45):
    m = bpy.data.materials.new(name)
    m.diffuse_color = (*color,1)
    m.use_nodes = True
    p = m.node_tree.nodes.get('Principled BSDF')
    p.inputs['Base Color'].default_value = (*color,1)
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
        b = o.modifiers.new('Soft manufactured edges','BEVEL')
        b.width = bevel
        b.segments = 3
        o.modifiers.new('Weighted normals','WEIGHTED_NORMAL')
    return o

def cyl(name, loc, radius, depth, material):
    bpy.ops.mesh.primitive_cylinder_add(vertices=32, radius=radius, depth=depth, location=loc)
    o = bpy.context.object
    o.name = name
    o.data.materials.append(material)
    for p in o.data.polygons:
        p.use_smooth = True
    b = o.modifiers.new('Rim bevel','BEVEL')
    b.width = min(0.014,depth*0.15)
    b.segments = 3
    o.modifiers.new('Weighted normals','WEIGHTED_NORMAL')
    return o

def text(body, loc, size, material):
    bpy.ops.object.text_add(location=loc, rotation=(math.pi/2,0,0))
    o = bpy.context.object
    o.name = 'Lettering ' + body
    o.data.body = body
    o.data.align_x = 'CENTER'
    o.data.align_y = 'CENTER'
    o.data.size = size
    o.data.extrude = 0.001
    o.data.materials.append(material)
    return o

def area(name, loc, power, size, target):
    bpy.ops.object.light_add(type='AREA', location=loc)
    o = bpy.context.object
    o.name = name
    o.data.energy = power
    o.data.size = size
    o.rotation_euler = (Vector(target)-o.location).to_track_quat('-Z','Y').to_euler()

def package(x,y,bottom,w,d,h,material,word):
    box('Packaged ' + word, (x,y,bottom+h/2), (w,d,h), material, 0.018)
    box('Paper product label', (x,y-d/2-0.004,bottom+h*0.55), (w*0.77,0.009,h*0.43), cream, 0.006)
    text(word, (x,y-d/2-0.010,bottom+h*0.58), w*0.17, dark)
    box('Label accent', (x,y-d/2-0.011,bottom+h*0.44), (w*0.48,0.003,0.012), gold)

def jar(x,y,bottom,material):
    cyl('Preserve jar body', (x,y,bottom+0.17), 0.115,0.34,material)
    cyl('Wraparound jar label', (x,y,bottom+0.18), 0.117,0.15,cream)
    cyl('Metal screw lid', (x,y,bottom+0.355), 0.122,0.045,gold)
    text('PANTRY', (x,y-0.12,bottom+0.18), 0.035,dark)

def bottle(x,y,bottom):
    cyl('Bottle body', (x,y,bottom+0.19),0.086,0.38,green)
    bpy.ops.mesh.primitive_cone_add(vertices=32,radius1=0.086,radius2=0.037,depth=0.095,location=(x,y,bottom+0.4275))
    o=bpy.context.object
    o.name='Bottle shoulder'
    o.data.materials.append(green)
    for p in o.data.polygons:
        p.use_smooth=True
    cyl('Bottle neck', (x,y,bottom+0.50),0.037,0.06,green)
    cyl('Bottle cap', (x,y,bottom+0.547),0.041,0.034,gold)
    cyl('Bottle paper band', (x,y,bottom+0.20),0.0875,0.18,cream)
    text('OIL', (x,y-0.090,bottom+0.20),0.047,dark)

oak=mat('Honey oak',(0.42,0.23,0.11))
walnut=mat('Dark end grain',(0.20,0.095,0.045))
cream=mat('Cream paper',(0.91,0.86,0.72))
stone=mat('Warm pale countertop',(0.75,0.72,0.64),0,0.29)
teal=mat('Deep teal cabinetry',(0.025,0.19,0.18),0,0.37)
dark=mat('Dark metal and ink',(0.035,0.049,0.047),0.35,0.3)
gold=mat('Brushed brass',(0.60,0.39,0.14),0.75,0.3)
red=mat('Berry preserves',(0.37,0.065,0.055),0,0.28)
green=mat('Olive green bottles',(0.14,0.24,0.08),0,0.21)
blue=mat('Blue tea cartons',(0.19,0.37,0.48))
terracotta=mat('Terracotta coffee bags',(0.62,0.24,0.12))
wall=mat('Plaster',(0.72,0.76,0.70),0,0.95)
floor=mat('Floor',(0.31,0.34,0.31),0,0.85)
screen=mat('Terminal display',(0.06,0.25,0.24),0.1,0.24)

box('Studio floor',(0,0,-0.13),(200,200,0.2),floor)
box('Shop floor platform',(0,0,0),(6.2,5.4,0.12),stone,0.035)
box('Back wall',(0,2.05,1.86),(5.7,0.15,3.6),wall,0.02)
box('Back wall skirting',(0,1.95,0.17),(5.7,0.05,0.18),teal,0.01)

box('Counter plinth',(0,-0.92,0.17),(4.5,1.02,0.22),dark,0.025)
box('Counter cabinet',(0,-0.92,0.70),(4.65,1.14,0.96),teal,0.035)
for i in range(35):
    x=-2.24+i*0.132
    box('Vertical oak front batten',(x,-1.515,0.71),(0.076,0.055,0.86),oak,0.012)
box('Counter brass toe trim',(0,-1.525,0.25),(4.5,0.024,0.035),gold,0.007)
box('Thick stone countertop',(0,-0.92,1.25),(4.86,1.34,0.15),stone,0.045)
box('Front name plaque',(-0.43,-1.565,0.79),(1.9,0.036,0.40),teal,0.035)
text('THE DAILY PANTRY',(-0.43,-1.587,0.79),0.13,cream)

box('Display backing',(0,1.81,1.62),(4.88,0.10,2.87),teal,0.02)
for x in [-2.44,0,2.44]:
    box('Shelf upright',(x,1.54,1.61),(0.09,0.62,2.9),oak,0.012)
for z in [0.40,1.12,1.84,2.56]:
    box('Display shelf',(0,1.50,z),(4.95,0.76,0.075),oak,0.016)
    box('Brass shelf lip',(0,1.112,z-0.004),(4.86,0.025,0.035),gold,0.005)
    for x in [-1.7,-0.65,0.65,1.7]:
        box('Shelf price card',(x,1.088,z),(0.30,0.012,0.075),cream,0.004)
        text('4.50',(x,1.080,z),0.039,dark)

for x in [-2.13,-1.77,-1.41,-1.05,-0.69,-0.33]:
    jar(x,1.43,0.438,red)
for x in [0.35,0.72,1.09,1.46,1.83,2.20]:
    package(x,1.46,0.438,0.27,0.32,random.uniform(0.43,0.52),terracotta,'COFFEE')
for x in [-2.13,-1.80,-1.47,-1.14,-0.81,-0.48]:
    package(x,1.47,1.158,0.255,0.30,0.46,blue,'TEA')
for x in [0.35,0.72,1.09,1.46,1.83,2.20]:
    bottle(x,1.43,1.158)
for x in [-2.10,-1.69,-1.28,-0.87,-0.46]:
    package(x,1.48,1.878,0.31,0.32,0.49,cream,'OATS')
for x in [0.36,0.73,1.10,1.47,1.84,2.21]:
    jar(x,1.43,1.878,terracotta)
box('Shop header',(0,1.77,2.99),(3.9,0.12,0.48),oak,0.025)
text('GOOD FOOD. EVERY DAY.',(0,1.698,2.99),0.19,cream)

box('Counter product tray',(-1.42,-0.87,1.365),(1.13,0.67,0.08),walnut,0.025)
for x in [-1.76,-1.42,-1.08]:
    package(x,-0.87,1.405,0.25,0.29,0.39,terracotta,'COFFEE')
box('Register base',(1.54,-0.86,1.365),(0.58,0.43,0.08),dark,0.025)
box('Register pedestal',(1.54,-0.77,1.57),(0.095,0.095,0.36),gold,0.015)
terminal=box('POS terminal',(1.54,-0.79,1.79),(0.68,0.10,0.45),dark,0.035)
display=box('POS screen',(1.54,-0.848,1.79),(0.60,0.012,0.36),screen,0.015)
text('WELCOME',(1.54,-0.858,1.84),0.065,cream)
text('12.50',(1.54,-0.858,1.72),0.09,cream)
box('Card reader',(1.45,-1.30,1.37),(0.22,0.28,0.085),dark,0.02)
box('Card reader display',(1.45,-1.26,1.416),(0.15,0.09,0.008),screen,0.008)
for i in range(3):
    for j in range(3):
        box('Card reader key',(1.4+i*0.05,-1.32-j*0.035,1.417),(0.032,0.021,0.007),cream,0.003)

area('Front softbox',(-3,-5,7),1450,5,(0,0,1))
area('Shelf fill',(2,-1,5),850,3,(0,1.4,1.5))
area('Warm rim',(-4,3,5),1000,3,(0,0,1))
bpy.ops.object.camera_add(location=(7,-10,6.5))
cam=bpy.context.object
cam.rotation_euler=(Vector((0,0.05,1.45))-cam.location).to_track_quat('-Z','Y').to_euler()
cam.data.type='ORTHO'
cam.data.ortho_scale=8.5
scene=bpy.context.scene
scene.camera=cam
scene.render.engine='CYCLES'
scene.cycles.samples=64
scene.world.color=(0.22,0.22,0.22)
scene.render.resolution_x=1500
scene.render.resolution_y=1200
scene.render.resolution_percentage=100
scene.view_settings.view_transform='AgX'
