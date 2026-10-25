import bpy, math, random
from mathutils import Vector
random.seed(131)
bpy.ops.wm.read_factory_settings(use_empty=True)

def mat(name, color, rough=.5, metal=0):
    m=bpy.data.materials.new(name); m.diffuse_color=(*color,1); m.use_nodes=True
    p=m.node_tree.nodes.get('Principled BSDF'); p.inputs['Base Color'].default_value=(*color,1); p.inputs['Roughness'].default_value=rough; p.inputs['Metallic'].default_value=metal
    return m

def box(name, loc, size, material, bevel=.025):
    bpy.ops.mesh.primitive_cube_add(size=1, location=loc); o=bpy.context.object; o.name=name; o.dimensions=size
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    o.data.materials.append(material)
    if bevel:
        m=o.modifiers.new('Soft edges','BEVEL'); m.width=bevel; m.segments=3
        o.modifiers.new('Weighted normals','WEIGHTED_NORMAL')
    return o

def cyl(name, loc, radius, depth, material, rotation=(0,0,0)):
    bpy.ops.mesh.primitive_cylinder_add(vertices=32, radius=radius, depth=depth, location=loc, rotation=rotation); o=bpy.context.object; o.name=name; o.data.materials.append(material)
    b=o.modifiers.new('Edge rounding','BEVEL'); b.width=.008; b.segments=2; o.modifiers.new('Weighted normals','WEIGHTED_NORMAL'); return o

def rod(name, a, b, radius, material):
    d=Vector(b)-Vector(a); o=cyl(name,(Vector(a)+Vector(b))/2,radius,d.length,material); o.rotation_euler=d.to_track_quat('Z','Y').to_euler(); return o

def label(body, loc, size, material):
    bpy.ops.object.text_add(location=loc, rotation=(math.pi/2,0,0)); o=bpy.context.object; o.name=body; o.data.body=body; o.data.align_x='CENTER'; o.data.size=size; o.data.extrude=.001; o.data.materials.append(material)

def light(name, loc, power, color, size, target):
    bpy.ops.object.light_add(type='AREA', location=loc); o=bpy.context.object; o.name=name; o.data.energy=power; o.data.color=color; o.data.shape='DISK'; o.data.size=size; o.rotation_euler=(Vector(target)-o.location).to_track_quat('-Z','Y').to_euler()

wood=mat('Smoked oak',(.24,.12,.055)); floor=mat('Floor oak',(.34,.22,.12)); wall=mat('Warm charcoal walls',(.12,.14,.155)); black=mat('Black powder coat',(.022,.026,.03)); fabric=mat('Graphite acoustic fabric',(.055,.07,.085),.95); felt=mat('Blue grey rug',(.09,.16,.20),1); cream=mat('Ivory details',(.82,.8,.72)); silver=mat('Brushed aluminum',(.38,.43,.46),.3,.7); blue=mat('Blue controls',(.08,.45,.65)); red=mat('Record buttons',(.65,.08,.05)); screen=mat('Screen glow',(.015,.13,.18),.25)
p=screen.node_tree.nodes.get('Principled BSDF'); p.inputs['Emission Color'].default_value=(.015,.32,.48,1); p.inputs['Emission Strength'].default_value=1.2
box('Room foundation',(0,0,-.15),(6.6,5.8,.3),black)
for i in range(22):
    x=-3.15+i*.3
    for j in range(4): box('Oak floor board',(x,-2.15+j*1.43,0),(.294,1.419,.055),floor,.006)
box('Rear wall',(0,2.85,1.65),(6.6,.16,3.3),wall)
box('Left wall',(-3.25,0,1.65),(.16,5.7,3.3),wall)
box('Rear skirting',(0,2.73,.1),(6.4,.06,.18),wood)
box('Left skirting',(-3.13,0,.1),(.06,5.55,.18),wood)
box('Rug',(0,-.55,.045),(3.6,2.7,.025),felt,.015)
for x in [-2.25,-1.1,1.1,2.25]:
    box('Acoustic panel timber frame',(x,2.69,1.94),(.88,.17,1.5),wood)
    box('Fabric absorber',(x,2.58,1.94),(.81,.08,1.42),fabric,.045)
for y in [-1.65,-.35,1.0]:
    box('Side absorber frame',(-3.1,y,1.95),(.18,.95,1.55),wood)
    box('Side absorber fabric',(-2.98,y,1.95),(.08,.87,1.47),fabric)
for x in [-3.0,3.0]:
    box('Corner bass trap',(x,2.53,1.55),(.35,.42,3.0),fabric,.07)
for i in range(9):
    for j in range(6):
        depth=random.choice([.08,.15,.23,.3]); box('Quadratic diffuser block',(-.43+i*.108,2.72-depth/2,1.28+j*.14),(.098,depth,.13),wood,.004)
label('STUDIO  /  01',(0,2.735,2.87),.19,cream)
box('Suspended acoustic cloud',(0,.45,3.03),(3.4,1.8,.14),fabric,.055)
for x in [-1.45,1.45]:
    for y in [-.3,1.2]: rod('Cloud suspension',(x,y,3.08),(x,y,3.3),.009,silver)
# Desk and integrated mixer
for x in [-1.42,1.42]: box('Desk pedestal',(x,.95,.45),(.38,.94,.86),wood)
box('Mixing desktop',(0,.86,.94),(3.5,1.4,.12),wood,.065)
box('Console chassis',(0,.65,1.055),(2.16,.88,.14),black,.05)
box('Console face',(0,.65,1.133),(2.06,.8,.018),silver,.015)
for i in range(14):
    x=-.94+i*.144
    box('Fader slot',(x,.47,1.147),(.014,.3,.006),black,.003)
    box('Fader cap',(x,.39+random.random()*.17,1.163),(.073,.044,.025),cream,.006)
    for y in [.77,.9]: cyl('Rotary knob',(x,y,1.17),.026,.041,black)
    box('Channel select',(x,.66,1.16),(.043,.035,.02),blue if i%3 else red,.004)
    box('Channel meter',(x,1.0,1.15),(.035,.065,.009),screen,.003)
for x in [-.67,.67]:
    cyl('Screen stand',(x,1.38,1.22),.035,.42,black)
    box('Display housing',(x,1.4,1.58),(1.08,.075,.62),black)
    box('DAW screen',(x,1.355,1.58),(.98,.012,.52),screen,.009)
    for j in range(6):
        box('Track lane',(x,1.345,1.39+j*.067),(.89,.007,.002),silver,.001)
        for k in range(4): box('Audio clip',(x-.38+k*.21,1.337,1.41+j*.067),(.13+random.random()*.06,.008,.027),blue if j%2 else cream,.002)
# Nearfield speakers, front faces toward the open room
for x in [-2.12,2.12]:
    box('Speaker stand foot',(x,1.48,.075),(.58,.54,.09),black)
    cyl('Speaker stand column',(x,1.48,.72),.055,1.25,black)
    box('Speaker cabinet',(x,1.47,1.63),(.58,.43,.82),black,.06)
    for z,r in [(1.5,.185),(1.87,.075)]:
        cyl('Driver surround',(x,1.241,z),r,.035,fabric,(math.pi/2,0,0))
        cyl('Driver cone',(x,1.215,z),r*.78,.015,silver if r<.1 else black,(math.pi/2,0,0))
        cyl('Dust cap',(x,1.20,z),r*.34,.025,black,(math.pi/2,0,0))
# Rolling chair
cyl('Chair lift',(0,-.92,.32),.055,.5,silver)
for i in range(5):
    a=i*math.tau/5; end=(.45*math.cos(a),-.92+.45*math.sin(a),.1); rod('Chair star base',(0,-.92,.15),end,.035,black); cyl('Caster',end,.06,.07,black,(math.pi/2,0,0))
box('Padded chair seat',(0,-.92,.57),(.69,.65,.16),fabric,.09)
box('Chair back',(0,-1.22,1.04),(.68,.15,.78),fabric,.09)
for x in [-.39,.39]:
    rod('Arm support',(x,-.9,.54),(x,-.9,.84),.025,silver); box('Arm rest',(x,-.9,.87),(.1,.43,.065),black)
# Equipment rack and microphone
box('Rack cabinet',(2.35,-.3,.47),(.67,.67,.9),wood)
for z in [.22,.4,.58,.76]:
    box('Rack unit',(2.35,-.652,z),(.58,.04,.145),black,.009)
    for x in [2.12,2.25,2.38]: cyl('Rack knob',(x,-.684,z),.022,.025,silver,(math.pi/2,0,0))
    box('Rack meter',(2.53,-.677,z),(.11,.015,.065),screen,.003)
rod('Mic stand',(-2,-1.7,.08),(-2,-1.7,1.65),.019,black)
for a in [0,2.094,4.189]: rod('Tripod leg',(-2,-1.7,.25),(-2+.4*math.cos(a),-1.7+.4*math.sin(a),.055),.016,black)
rod('Mic boom',(-2,-1.7,1.55),(-1.45,-1.65,1.86),.018,silver)
cyl('Microphone',(-1.45,-1.65,1.9),.055,.23,black)
light('Soft ceiling light',(0,-.7,4.6),850,(1,.84,.66),4,(0,.5,0))
light('Open front fill',(3,-4,3.8),650,(.68,.82,1),4,(0,1,1))
light('Rear warm accent',(-1,2.2,2.9),120,(1,.49,.22),1.5,(0,1,1))
bpy.ops.object.camera_add(location=(7.8,-10.3,7.0)); camera=bpy.context.object; camera.rotation_euler=(Vector((0,.25,1.25))-camera.location).to_track_quat('-Z','Y').to_euler(); camera.data.type='ORTHO'; camera.data.ortho_scale=9.3
scene=bpy.context.scene; scene.camera=camera; scene.render.engine='CYCLES'; scene.world.color=(.18,.18,.18); scene.render.resolution_x=1500; scene.render.resolution_y=1200; scene.render.resolution_percentage=100
