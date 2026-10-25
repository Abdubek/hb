import bpy, math
from mathutils import Vector

bpy.ops.wm.read_factory_settings(use_empty=True)

def mat(name,color,metallic=0.0,roughness=0.4):
    m=bpy.data.materials.new(name)
    m.diffuse_color=(*color,1)
    m.use_nodes=True
    p=m.node_tree.nodes.get('Principled BSDF')
    p.inputs['Base Color'].default_value=(*color,1)
    p.inputs['Metallic'].default_value=metallic
    p.inputs['Roughness'].default_value=roughness
    return m

def box(name,loc,size,material,bevel=0.0,parent=None):
    bpy.ops.mesh.primitive_cube_add(size=1)
    o=bpy.context.object
    o.name=name
    o.dimensions=size
    bpy.ops.object.transform_apply(location=False,rotation=False,scale=True)
    o.data.materials.append(material)
    if bevel:
        b=o.modifiers.new('Precision rounded edges','BEVEL')
        b.width=bevel
        b.segments=4
        o.modifiers.new('Weighted normals','WEIGHTED_NORMAL')
    if parent:
        o.parent=parent
    o.location=loc
    return o

def cylinder(name,loc,radius,depth,material,rotation=(0,0,0),parent=None):
    bpy.ops.mesh.primitive_cylinder_add(vertices=48,radius=radius,depth=depth)
    o=bpy.context.object
    o.name=name
    o.data.materials.append(material)
    if parent:
        o.parent=parent
    o.location=loc
    o.rotation_euler=rotation
    for p in o.data.polygons:
        p.use_smooth=True
    b=o.modifiers.new('Edge chamfer','BEVEL')
    b.width=min(0.012,depth*0.18)
    b.segments=3
    o.modifiers.new('Weighted normals','WEIGHTED_NORMAL')
    return o

def lettering(body,loc,size,material,parent=None,vertical=False):
    bpy.ops.object.text_add()
    o=bpy.context.object
    o.name='Legend '+body
    if parent:
        o.parent=parent
    o.location=loc
    if vertical:
        o.rotation_euler=(math.pi/2,0,0)
    o.data.body=body
    o.data.size=size
    o.data.align_x='CENTER'
    o.data.align_y='CENTER'
    o.data.materials.append(material)
    return o

def area(loc,energy,size,target):
    bpy.ops.object.light_add(type='AREA',location=loc)
    o=bpy.context.object
    o.data.energy=energy
    o.data.size=size
    o.rotation_euler=(Vector(target)-o.location).to_track_quat('-Z','Y').to_euler()

silver=mat('Bead-blasted aluminum',(0.48,0.53,0.59),0.83,0.29)
edge=mat('Polished aluminum accents',(0.67,0.73,0.8),0.85,0.2)
black=mat('Black keyboard polymer',(0.018,0.022,0.03),0.05,0.39)
bezel=mat('Screen bezel',(0.008,0.012,0.018),0.1,0.24)
white=mat('Key legends',(0.72,0.79,0.85),0,0.45)
track=mat('Trackpad glass',(0.35,0.40,0.47),0.4,0.32)
blue=mat('Interface blue',(0.04,0.35,0.64),0,0.4)
cyan=mat('Interface mint',(0.15,0.74,0.70),0,0.4)
navy=mat('Interface panel',(0.035,0.065,0.13),0,0.45)
floor=mat('Studio surface',(0.14,0.18,0.23),0,0.7)
screen=mat('Illuminated screen',(0.035,0.07,0.16),0,0.22)
p=screen.node_tree.nodes.get('Principled BSDF')
p.inputs['Emission Color'].default_value=(0.035,0.09,0.22,1)
p.inputs['Emission Strength'].default_value=0.65

box('Studio floor',(0,0,-0.08),(200,200,0.1),floor)
for x in [-1.35,1.35]:
    for y in [-0.69,0.69]:
        box('Rubber foot',(x,y,0.015),(0.34,0.15,0.055),black,0.04)
box('Lower unibody shell',(0,0,0.13),(3.5,2.18,0.20),silver,0.085)
box('Bottom assembly seam',(0,0,0.067),(3.42,2.10,0.012),black,0.035)
box('Keyboard deck',(0,0,0.227),(3.43,2.11,0.045),silver,0.043)
box('Keyboard recessed well',(0,0.30,0.251),(2.85,1.04,0.016),black,0.045)

# Full key rows with deliberate widths, gaps and readable built-in-font legends.
rows=[
    [('ESC',1),('F1',1),('F2',1),('F3',1),('F4',1),('F5',1),('F6',1),('F7',1),('F8',1),('F9',1),('F10',1),('F11',1),('F12',1),('PWR',1)],
    [('1',1),('2',1),('3',1),('4',1),('5',1),('6',1),('7',1),('8',1),('9',1),('0',1),('-',1),('=',1),('DEL',2)],
    [('TAB',1.5),('Q',1),('W',1),('E',1),('R',1),('T',1),('Y',1),('U',1),('I',1),('O',1),('P',1),('[',1),(']',1.5)],
    [('CAPS',1.75),('A',1),('S',1),('D',1),('F',1),('G',1),('H',1),('J',1),('K',1),('L',1),(';',1),('ENTER',2.25)],
    [('SHIFT',2.25),('Z',1),('X',1),('C',1),('V',1),('B',1),('N',1),('M',1),(',',1),('.',1),('/',1),('SHIFT',1.75)],
    [('CTRL',1.5),('FN',1),('ALT',1.25),('',6.5),('ALT',1.25),('<',1),('>',1),('^',1.5)]
]
for r,row in enumerate(rows):
    total=sum(w for _,w in row)
    pitch=2.73/total
    x=-1.365
    y=0.715-r*0.166
    for legend,units in row:
        width=units*pitch-0.022
        center=x+units*pitch/2
        box('Key '+(legend or 'SPACE'),(center,y,0.276),(width,0.139,0.038),black,0.018)
        if legend:
            lettering(legend,(center,y,0.297),0.036 if len(legend)>1 else 0.058,white)
        x+=units*pitch

box('Trackpad machined border',(0,-0.634,0.253),(1.30,0.59,0.013),edge,0.045)
box('Trackpad',(0,-0.634,0.262),(1.266,0.556,0.013),track,0.037)
box('Front opening recess',(0,-1.092,0.195),(0.58,0.012,0.033),black,0.014)
for x in [-1.55,1.55]:
    for col in range(3):
        for row in range(23):
            cylinder('Speaker perforation',(x+(col-1)*0.038,-0.02+row*0.034,0.253),0.009,0.004,black)
for y in [-0.44,-0.06]:
    box('Left USB-C port',(-1.752,y,0.135),(0.008,0.21,0.06),black,0.016)
    box('USB-C internal tongue',(-1.757,y,0.135),(0.004,0.135,0.012),edge,0.003)
box('Right USB port',(1.752,0.20,0.135),(0.009,0.24,0.068),black,0.012)
cylinder('Headphone socket',(1.752,-0.38,0.13),0.033,0.01,black,(0,math.pi/2,0))
for x in [-1.13,1.13]:
    cylinder('Display hinge barrel',(x,0.943,0.285),0.10,0.63,edge,(0,math.pi/2,0))

bpy.ops.object.empty_add(type='PLAIN_AXES',location=(0,0.946,0.29))
hinge=bpy.context.object
hinge.name='Display hinge - open 105 degrees'
hinge.rotation_euler.x=math.radians(-15)
box('Display aluminum housing',(0,0.013,1.02),(3.48,0.112,2.04),silver,0.065,hinge)
box('Inset black display bezel',(0,-0.049,1.035),(3.37,0.022,1.94),bezel,0.045,hinge)
box('Active display glass',(0,-0.063,1.035),(3.14,0.012,1.70),screen,0.021,hinge)
cylinder('Webcam lens',(0,-0.072,1.954),0.025,0.01,black,(math.pi/2,0,0),hinge)
cylinder('Webcam lens glint',(0,-0.079,1.954),0.012,0.004,blue,(math.pi/2,0,0),hinge)
lettering('N O V A',(0,-0.064,0.104),0.045,white,hinge,True)

# A modeled screen interface; all graphics are local geometry, no textures.
box('Application sidebar',(-1.22,-0.072,1.035),(0.59,0.005,1.59),navy,0.015,hinge)
lettering('STUDIO',(-1.22,-0.079,1.69),0.095,white,hinge,True)
for i,name in enumerate(['Overview','Projects','Library','Settings']):
    lettering(name,(-1.22,-0.079,1.41-i*0.18),0.059,white,hinge,True)
lettering('Make something great.',(0.29,-0.079,1.67),0.107,white,hinge,True)
lettering('Your workspace, ready.',(0.22,-0.079,1.48),0.065,white,hinge,True)
for i in range(3):
    box('Dashboard card',(-0.50+i*0.70,-0.075,1.15),(0.62,0.008,0.39),blue if i==0 else navy,0.025,hinge)
    lettering(['12','08','94%'][i],(-0.50+i*0.70,-0.084,1.18),0.14,white,hinge,True)
    lettering(['PROJECTS','DRAFTS','COMPLETE'][i],(-0.50+i*0.70,-0.084,1.02),0.041,white,hinge,True)
box('Activity chart background',(0.20,-0.074,0.62),(2.07,0.006,0.50),navy,0.022,hinge)
for i,h in enumerate([0.10,0.17,0.14,0.23,0.20,0.29,0.27,0.34,0.32,0.39]):
    box('Chart bar',(-0.68+i*0.19,-0.081,0.395+h/2),(0.11,0.006,h),cyan,0.008,hinge)

area((-3,-4,7),1000,5,(0,0,0.8))
area((4,2,5),1250,4,(0,0.4,1))
area((-4,3,3),700,3,(0,0,1))
bpy.ops.object.camera_add(location=(5.0,-7.0,5.2))
cam=bpy.context.object
cam.rotation_euler=(Vector((0,0.20,1.0))-cam.location).to_track_quat('-Z','Y').to_euler()
cam.data.type='ORTHO'
cam.data.ortho_scale=5.8
scene=bpy.context.scene
scene.camera=cam
scene.render.engine='CYCLES'
scene.cycles.samples=64
scene.world.color=(0.2,0.2,0.2)
scene.render.resolution_x=1500
scene.render.resolution_y=1200
scene.render.resolution_percentage=100
scene.view_settings.view_transform='AgX'
