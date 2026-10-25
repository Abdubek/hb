import bpy, math
from mathutils import Vector
bpy.ops.wm.read_factory_settings(use_empty=True)

def mat(name,c,metal=0,rough=.45,glow=0):
    m=bpy.data.materials.new(name); m.diffuse_color=(*c,1); m.use_nodes=True; p=m.node_tree.nodes.get('Principled BSDF'); p.inputs['Base Color'].default_value=(*c,1); p.inputs['Metallic'].default_value=metal; p.inputs['Roughness'].default_value=rough
    if glow: p.inputs['Emission Color'].default_value=(*c,1); p.inputs['Emission Strength'].default_value=glow
    return m

def box(name,loc,dims,m,bevel=.025):
    bpy.ops.mesh.primitive_cube_add(size=1,location=loc); o=bpy.context.object; o.name=name; o.dimensions=dims; bpy.ops.object.transform_apply(location=False,rotation=False,scale=True); o.data.materials.append(m)
    if bevel:
        b=o.modifiers.new('Manufactured edge radius','BEVEL'); b.width=bevel; b.segments=3; o.modifiers.new('Normals','WEIGHTED_NORMAL')
    return o

def cyl(name,loc,r,depth,m,rot=(0,0,0)):
    bpy.ops.mesh.primitive_cylinder_add(vertices=40,radius=r,depth=depth,location=loc,rotation=rot); o=bpy.context.object; o.name=name; o.data.materials.append(m); b=o.modifiers.new('Edge radius','BEVEL'); b.width=.012; b.segments=2; o.modifiers.new('Normals','WEIGHTED_NORMAL'); return o

def label(body,loc,size,m):
    bpy.ops.object.text_add(location=loc,rotation=(math.pi/2,0,0)); o=bpy.context.object; o.name=body; o.data.body=body; o.data.size=size; o.data.extrude=.001; o.data.materials.append(m)

def cable(name,points,r,m):
    cu=bpy.data.curves.new(name,'CURVE'); cu.dimensions='3D'; cu.resolution_u=20; cu.bevel_depth=r; cu.bevel_resolution=4; sp=cu.splines.new('BEZIER'); sp.bezier_points.add(len(points)-1)
    for b,p in zip(sp.bezier_points,points): b.co=p; b.handle_left_type='AUTO'; b.handle_right_type='AUTO'
    o=bpy.data.objects.new(name,cu); bpy.context.collection.objects.link(o); o.data.materials.append(m)

def aim(o,p): o.rotation_euler=(Vector(p)-o.location).to_track_quat('-Z','Y').to_euler()
asphalt=mat('Asphalt',(.075,.085,.10)); concrete=mat('Concrete',(.47,.49,.47)); white=mat('Warm white',(.86,.88,.86)); dark=mat('Graphite housing',(.027,.04,.048),.25); green=mat('Charging green',(.045,.62,.30)); led=mat('Status LED',(.10,1,.45),0,.25,3); black=mat('Cable rubber',(.009,.013,.018)); screen=mat('Screen glass',(.015,.075,.095),.2,.18); steel=mat('Stainless steel',(.48,.53,.56),.8,.25); yellow=mat('Safety yellow',(.95,.62,.045)); blue=mat('Car blue',(.035,.22,.42),.6,.24); glass=mat('Car tinted glass',(.025,.07,.095),.45,.16)
box('Site ground',(0,0,-.19),(100,100,.2),concrete)
box('Charging forecourt',(0,-1,-.04),(12,13,.18),asphalt)
box('Raised equipment island',(0,3.45,.16),(10,2,.35),concrete,.1)
for x in (-4.5,-1.5,1.5,4.5): box('Bay stripe',(x,-.95,.06),(.085,6.1,.012),white,.002)
for x in (-3,0,3):
    box('Bay entrance stripe',(x,-4,.065),(2.9,.085,.012),white,.002)
    box('Wheel stop',(x,1.64,.16),(1.65,.22,.20),concrete,.055)
    for dx in (-.55,.55): box('Wheel stop reflector',(x+dx,1.515,.18),(.24,.015,.08),yellow,.003)
    bpy.ops.object.text_add(location=(x,-3.65,.07)); o=bpy.context.object; o.name='EV bay stencil'; o.data.body='EV'; o.data.align_x='CENTER'; o.data.size=.6; o.data.materials.append(green)
for idx,x in enumerate((-3,0,3)):
    box('Charger base',(x,3,.40),(.95,.72,.18),steel,.05)
    box('Fast charging cabinet',(x,3,1.43),(.82,.62,1.92),white,.11)
    box('Dark front fascia',(x,2.675,1.48),(.68,.065,1.66),dark,.06)
    box('Illuminated status bar',(x,2.629,2.18),(.49,.018,.045),led,.015)
    box('Touchscreen',(x,2.626,1.77),(.46,.018,.38),screen,.02)
    label('READY' if idx else 'CHARGING',(x-.20,2.607,1.83),.066,led)
    label('150 kW',(x-.19,2.607,1.66),.074,white)
    box('Payment reader',(x+.12,2.623,1.35),(.16,.025,.19),black,.015)
    label('TAP',(x+.075,2.605,1.35),.035,white)
    label('0'+str(idx+1),(x-.24,2.624,.83),.17,white)
    for z in (.58,.64,.70): box('Vent slot',(x,2.625,z),(.4,.018,.015),steel,.005)
    cyl('Emergency stop bezel',(x-.19,2.608,1.3),.051,.025,yellow,(math.pi/2,0,0))
    red= bpy.data.materials.get('Emergency red') or mat('Emergency red',(.65,.025,.015))
    cyl('Emergency stop',(x-.19,2.585,1.3),.035,.025,red,(math.pi/2,0,0))
    if idx==0:
        cable('Connected charging cable',[(x+.43,2.95,1.95),(x+.91,2.5,1.2),(x+1.15,1.8,.38),(x+1.05,.55,.32),(x+.88,.2,.95)],.033,black)
        box('Connected plug',(x+.91,.2,.97),(.23,.13,.13),dark,.035)
    else:
        cable('Parked cable loop',[(x+.43,3,1.94),(x+.73,2.83,1.56),(x+.76,2.57,.57),(x+.49,2.45,.46),(x+.33,2.50,1.26)],.032,black)
        box('Holstered connector',(x+.32,2.5,1.34),(.12,.16,.29),dark,.045)
    for dx in (-.84,.84):
        cyl('Protective bollard',(x+dx,2.29,.61),.073,1.08,steel)
        cyl('Bollard reflective band',(x+dx,2.29,.98),.077,.15,yellow)
for x in (-5,5): box('Canopy column',(x,3.8,2.1),(.20,.20,3.9),steel,.025)
box('Canopy main beam',(0,3.8,4.03),(10.5,.3,.24),steel)
box('Canopy roof',(0,1.3,4.25),(11,6.3,.22),dark,.09)
box('Green canopy fascia',(0,-1.87,4.23),(11,.10,.32),green)
label('VOLT / ELECTRIC',( -4.65,-1.934,4.13),.22,white)
label('FAST CHARGING',(1.93,-1.934,4.13),.18,white)
for x in (-3,0,3):
    box('Under canopy light',(x,1.3,4.12),(1.3,.22,.035),led,.015)
    bpy.ops.object.light_add(type='AREA',location=(x,1.2,4.05)); bpy.context.object.data.energy=65; bpy.context.object.data.size=2
# Compact electric car, nose facing the chargers.
cx=-3; cy=-.65
box('EV lower body',(cx,cy,.69),(1.77,3.75,.63),blue,.23)
box('EV hood',(cx,cy+1.12,.99),(1.65,1.08,.22),blue,.12)
box('EV cabin',(cx,cy-.30,1.25),(1.48,1.98,.79),glass,.25)
box('EV roof',(cx,cy-.37,1.65),(1.28,1.36,.075),blue,.06)
for side in (-1,1):
    box('Door window pillar',(cx+side*.744,cy-.37,1.35),(.05,.09,.46),blue,.015)
    for y in (cy-.65,cy+.2): box('Door handle',(cx+side*.886,y,.99),(.028,.16,.035),steel,.01)
    for y in (cy-1.2,cy+1.18):
        cyl('Tire',(cx+side*.86,y,.48),.37,.23,black,(0,math.pi/2,0))
        cyl('Alloy wheel',(cx+side*.991,y,.48),.25,.024,steel,(0,math.pi/2,0))
        cyl('Wheel center',(cx+side*1.007,y,.48),.095,.025,dark,(0,math.pi/2,0))
    box('Headlight',(cx+side*.59,cy+1.855,.9),(.38,.045,.12),white,.04)
    box('Rear lamp',(cx+side*.60,cy-1.855,.91),(.36,.045,.10),red,.03)
box('Front lower grille',(cx,cy+1.872,.58),(.83,.035,.13),dark,.035)
box('Charge port',(cx+.89,.2,.97),(.025,.21,.21),black,.04)
bpy.ops.object.light_add(type='SUN',location=(0,-5,10)); bpy.context.object.data.energy=2; bpy.context.object.rotation_euler=(.45,-.4,-.4); bpy.context.object.data.angle=.1
bpy.ops.object.light_add(type='AREA',location=(3,-8,8)); bpy.context.object.data.energy=1100; bpy.context.object.data.size=8; aim(bpy.context.object,(0,1,1))
bpy.ops.object.camera_add(location=(14,-19,10)); camera=bpy.context.object; aim(camera,(0,.1,1.4)); camera.data.type='ORTHO'; camera.data.ortho_scale=17
scene=bpy.context.scene; scene.camera=camera; scene.render.engine='CYCLES'; scene.cycles.samples=64; scene.world.color=(.25,.25,.25); scene.render.resolution_x=1600; scene.render.resolution_y=1100; scene.render.resolution_percentage=100
