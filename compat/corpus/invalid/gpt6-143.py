import bpy, math
from mathutils import Vector
bpy.ops.wm.read_factory_settings(use_empty=True)

def mat(name,c,rough=.5,metal=0):
    m=bpy.data.materials.new(name); m.diffuse_color=(*c,1); m.use_nodes=True
    p=m.node_tree.nodes.get('Principled BSDF'); p.inputs['Base Color'].default_value=(*c,1); p.inputs['Roughness'].default_value=rough; p.inputs['Metallic'].default_value=metal
    return m

def box(name,loc,size,m,bevel=0):
    bpy.ops.mesh.primitive_cube_add(size=1,location=loc); o=bpy.context.object; o.name=name; o.dimensions=size
    bpy.ops.object.transform_apply(location=False,rotation=False,scale=True); o.data.materials.append(m)
    if bevel:
        mod=o.modifiers.new('Dressed edges','BEVEL'); mod.width=bevel; mod.segments=2; o.modifiers.new('Weighted normals','WEIGHTED_NORMAL')
    return o

def beam(name,a,b,width,depth,m):
    a,b=Vector(a),Vector(b); d=b-a
    o=box(name,(a+b)/2,(width,depth,d.length),m,.012); o.rotation_euler=d.to_track_quat('Z','Y').to_euler(); return o

def rod(name,a,b,r,m):
    a,b=Vector(a),Vector(b); d=b-a
    bpy.ops.mesh.primitive_cylinder_add(vertices=12,radius=r,depth=d.length,location=(a+b)/2)
    o=bpy.context.object; o.name=name; o.rotation_euler=d.to_track_quat('Z','Y').to_euler(); o.data.materials.append(m); return o

def aim(o,p): o.rotation_euler=(Vector(p)-o.location).to_track_quat('-Z','Y').to_euler()
def area(name,loc,power,size,target):
    bpy.ops.object.light_add(type='AREA',location=loc); o=bpy.context.object; o.name=name; o.data.energy=power; o.data.size=size; aim(o,target)

timber=mat('Honey glulam',(.56,.32,.13)); darkwood=mat('Bench hardwood',(.32,.15,.06)); steel=mat('Charcoal connection steel',(.12,.16,.17),.3,.75)
boltmat=mat('Zinc bolts',(.54,.59,.61),.23,.85); concrete=mat('Platform concrete',(.55,.56,.53)); yellow=mat('Tactile safety strip',(.86,.62,.12))
ballast=mat('Rail ballast',(.22,.24,.23)); railmat=mat('Polished rails',(.35,.39,.4),.25,.85); white=mat('Sign lettering',(.94,.94,.83)); blue=mat('Station blue',(.035,.13,.2))
glass=mat('Clear blue roof glass',(.72,.87,.9),.08)
p=glass.node_tree.nodes.get('Principled BSDF'); p.inputs['Transmission Weight'].default_value=.94; p.inputs['IOR'].default_value=1.45
lamp=mat('Linear warm LEDs',(.98,.86,.65)); p=lamp.node_tree.nodes.get('Principled BSDF'); p.inputs['Emission Color'].default_value=(1,.82,.56,1); p.inputs['Emission Strength'].default_value=4
# Procedural grain requires no image textures.
n=timber.node_tree.nodes.new('ShaderNodeTexNoise'); n.inputs['Scale'].default_value=4; n.inputs['Detail'].default_value=2
tex=timber.node_tree.nodes.new('ShaderNodeTexCoord'); mapping=timber.node_tree.nodes.new('ShaderNodeVectorMath'); mapping.operation='MULTIPLY'; mapping.inputs[1].default_value=(3,3,.22)
timber.node_tree.links.new(tex.outputs['Generated'],mapping.inputs[0]); timber.node_tree.links.new(mapping.outputs['Vector'],n.inputs['Vector'])
ramp=timber.node_tree.nodes.new('ShaderNodeValToRGB'); ramp.color_ramp.elements[0].color=(.24,.095,.025,1); ramp.color_ramp.elements[1].color=(.66,.41,.18,1)
timber.node_tree.links.new(n.outputs['Fac'],ramp.inputs[0]); timber.node_tree.links.new(ramp.outputs['Color'],timber.node_tree.nodes.get('Principled BSDF').inputs['Base Color'])

box('Site',(0,1,-.38),(29,15,.45),ballast,.08)
box('Raised station platform',(0,0,.04),(26,8.8,.7),concrete,.06)
for y in (-4.07,4.07):
    box('Platform edge coping',(0,y,.43),(26,.62,.13),concrete,.025)
    box('Yellow safety band',(0,y-.27*(1 if y>0 else -1),.507),(25.8,.13,.018),yellow)
    for i in range(104): box('Tactile raised rib',(-12.85+i*.25,y,.515),(.04,.34,.022),yellow,.006)
for x in range(-12,13,2): box('Paving expansion joint',(x,0,.396),(.013,7.35,.008),steel)

# Seven king-post trusses on paired timber columns.
trusses=[-10.8,-7.2,-3.6,0,3.6,7.2,10.8]
for index,x in enumerate(trusses):
    for y in (-3.2,3.2):
        box('Concrete column footing',(x,y,.58),(.7,.7,.35),concrete,.04)
        box('Steel column shoe',(x,y,.81),(.43,.43,.2),steel,.02)
        box('Timber column',(x,y,2.66),(.3,.34,3.66),timber,.02)
        for dx in (-.2,.2): box('Shoe side plate',(x+dx,y,1.01),(.045,.38,.6),steel,.009)
        for z in (.87,1.13): rod('Shoe through bolt',(x-.25,y,z),(x+.25,y,z),.04,boltmat)
        beam('Longitudinal knee brace',(x,y,3.35),(x+(.85 if index<6 else -.85),y,4.36),.16,.18,timber)
        beam('Transverse knee brace',(x,y,3.35),(x,y-math.copysign(.85,y),4.36),.17,.18,timber)
    beam('Truss tie beam',(x,-3.48,4.4),(x,3.48,4.4),.24,.28,timber)
    beam('Left principal rafter',(x,-3.8,4.44),(x,0,6.05),.22,.25,timber)
    beam('Right principal rafter',(x,0,6.05),(x,3.8,4.44),.22,.25,timber)
    beam('King post',(x,0,4.4),(x,0,6.03),.2,.2,timber)
    for side in (-1,1): beam('Truss diagonal strut',(x,0,4.46),(x,side*1.95,5.18),.16,.17,timber)
    for y,z in ((0,5.88),(0,4.46),(-3.15,4.46),(3.15,4.46)):
        for dx in (-.145,.145): box('Truss connection plate',(x+dx,y,z),(.035,.43,.35),steel,.015)
        for dy in (-.13,.13): rod('Truss connection bolt',(x-.18,y+dy,z),(x+.18,y+dy,z),.035,boltmat)

for y in (-3.2,3.2): beam('Continuous eaves beam',(-11.6,y,4.38),(11.6,y,4.38),.27,.3,timber)
for y in (-3.8,-2.55,-1.28,0,1.28,2.55,3.8):
    z=6.12-abs(y)*1.61/3.8
    beam('Roof longitudinal purlin',(-11.6,y,z),(11.6,y,z),.13,.16,timber)

# Separate glazing panes leave narrow joints for pressure-cap glazing bars.
slope=1.61/3.8
for side in (-1,1):
    for ix in range(18):
        x=-11.7+(ix+.5)*1.3
        for row in range(3):
            y=side*(row+.5)*(3.9/3); z=6.24-abs(y)*slope
            o=box('Glazed roof pane',(x,y,z),(1.265,1.275*math.sqrt(1+slope*slope),.035),glass,.006)
            o.rotation_euler.x=-side*math.atan(slope)
    for ix in range(19):
        x=-11.7+ix*1.3
        beam('Glazing pressure cap',(x,0,6.275),(x,side*3.9,6.275-3.9*slope),.055,.06,steel)
    for row in range(4):
        y=side*row*1.3; z=6.275-abs(y)*slope
        beam('Longitudinal glazing bar',(-11.75,y,z),(11.75,y,z),.045,.045,steel)
beam('Ridge weather cap',(-11.85,0,6.31),(11.85,0,6.31),.14,.085,steel)
for y in (-3.97,3.97):
    box('Gutter base',(0,y,4.52),(23.8,.23,.055),steel)
    for dy in (-.115,.115): box('Gutter lip',(0,y+dy,4.59),(23.8,.03,.17),steel)
    for x in (-10.8,10.8):
        rod('Rainwater downpipe',(x,y,4.52),(x,y,.48),.065,steel)
        for z in (1.1,2.5,4): rod('Pipe wall bracket',(x,y,z),(x,y-math.copysign(.62,y),z),.023,steel)

for x in (-7.2,0,7.2):
    for j in range(5): box('Bench seat slat',(x,-.3+j*.115,.92),(2.5,.09,.09),darkwood,.015)
    for z in (1.22,1.42): box('Bench back slat',(x,.29,z),(2.5,.08,.16),darkwood,.015)
    for dx in (-.92,.92):
        box('Bench foot',(x+dx,0,.66),(.12,.6,.5),steel,.02)
        beam('Backrest support',(x+dx,.29,.8),(x+dx,.29,1.52),.065,.065,steel)
for x in (-5.4,5.4):
    for y in (-1,1): rod('Sign suspension',(x,y,4.42),(x,y,3.73),.017,steel)
    box('Station name board',(x,0,3.5),(.12,2.8,.52),blue,.025)
    bpy.ops.object.text_add(location=(x+.071,0,3.38))
    o=bpy.context.object; o.name='Station lettering'; o.rotation_euler=(math.pi/2,0,math.pi/2); o.data.body='WOODLAND'; o.data.align_x='CENTER'; o.data.size=.27; o.data.extrude=.001; o.data.materials.append(white)
for x in (-9,-1.8,5.4):
    box('Suspended LED housing',(x,0,4.17),(2.1,.14,.11),steel,.015)
    box('LED diffuser',(x,0,4.108),(1.95,.11,.025),lamp)
    area('Canopy downlight',(x,0,4.02),100,2,(x,0,0))

# A short adjacent railway establishes the station context.
for x in range(-14,15): box('Railway sleeper',(x,6.25,-.06),(.2,2.5,.17),darkwood,.015)
for y in (5.53,6.97):
    box('Rail foot',(0,y,.06),(28,.16,.055),railmat)
    box('Rail web',(0,y,.14),(28,.055,.14),railmat)
    box('Rail head',(0,y,.225),(28,.095,.065),railmat,.015)
area('Soft daylight',(-5,-9,15),2600,10,(0,0,2)); area('Glazing highlights',(6,7,13),2000,8,(0,0,4))
bpy.ops.object.camera_add(location=(23,-22,14)); cam=bpy.context.object; aim(cam,(0,0,2.2)); cam.data.type='ORTHO'; cam.data.ortho_scale=29
scene=bpy.context.scene; scene.camera=cam; scene.render.engine='CYCLES'; scene.cycles.samples=64; scene.world.color=(.3,.3,.3)
scene.render.resolution_x=1600; scene.render.resolution_y=1000; scene.render.resolution_percentage=100; scene.view_settings.view_transform='AgX'
