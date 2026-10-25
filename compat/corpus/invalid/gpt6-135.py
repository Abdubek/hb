import bpy, math, random
from mathutils import Vector
random.seed(135)
bpy.ops.wm.read_factory_settings(use_empty=True)

def mat(name,c,rough=.6,metal=0):
    m=bpy.data.materials.new(name); m.diffuse_color=(*c,1); m.use_nodes=True; p=m.node_tree.nodes.get('Principled BSDF'); p.inputs['Base Color'].default_value=(*c,1); p.inputs['Roughness'].default_value=rough; p.inputs['Metallic'].default_value=metal; return m

def box(name,loc,size,m,b=.025):
    bpy.ops.mesh.primitive_cube_add(size=1,location=loc); o=bpy.context.object; o.name=name; o.dimensions=size; bpy.ops.object.transform_apply(location=False,rotation=False,scale=True); o.data.materials.append(m)
    if b:
        q=o.modifiers.new('Soft edges','BEVEL'); q.width=b; q.segments=3; o.modifiers.new('Weighted normals','WEIGHTED_NORMAL')
    return o

def cyl(name,loc,r,d,m,rot=(0,0,0)):
    bpy.ops.mesh.primitive_cylinder_add(vertices=32,radius=r,depth=d,location=loc,rotation=rot); o=bpy.context.object; o.name=name; o.data.materials.append(m); q=o.modifiers.new('Rim bevel','BEVEL'); q.width=.008; q.segments=2; o.modifiers.new('Weighted normals','WEIGHTED_NORMAL'); return o

def rod(name,a,b,r,m):
    v=Vector(b)-Vector(a); o=cyl(name,(Vector(a)+Vector(b))/2,r,v.length,m); o.rotation_euler=v.to_track_quat('Z','Y').to_euler(); return o

def text(body,loc,size,m):
    bpy.ops.object.text_add(location=loc,rotation=(math.pi/2,0,0)); o=bpy.context.object; o.name=body; o.data.body=body; o.data.align_x='CENTER'; o.data.size=size; o.data.extrude=.001; o.data.materials.append(m)

def area(name,loc,power,color,size,target):
    bpy.ops.object.light_add(type='AREA',location=loc); o=bpy.context.object; o.name=name; o.data.energy=power; o.data.color=color; o.data.shape='DISK'; o.data.size=size; o.rotation_euler=(Vector(target)-o.location).to_track_quat('-Z','Y').to_euler()

wall=mat('Warm white paint',(.84,.85,.79)); floor=mat('Warm grey resilient floor',(.51,.55,.53)); oak=mat('Light oak',(.6,.43,.25)); sage=mat('Sage cleanable upholstery',(.34,.5,.44),.72); blue=mat('Blue cleanable upholstery',(.23,.4,.5),.7); metal=mat('Satin aluminum',(.46,.51,.53),.3,.65); dark=mat('Graphite',(.045,.065,.072)); white=mat('Ceramic white',(.92,.93,.88),.3); leaf=mat('Plant green',(.12,.3,.15),.8); leaf2=mat('Light leaf green',(.25,.42,.19),.85); soil=mat('Potting soil',(.055,.035,.02)); teal=mat('Clinic teal',(.06,.27,.28)); paper=mat('Magazine paper',(.87,.85,.77)); orange=mat('Magazine orange',(.74,.35,.13)); sand=mat('Art sand',(.65,.53,.35)); glass=mat('Frosted glass',(.64,.8,.79),.36)
box('Floor slab',(0,0,-.14),(7.8,6.4,.28),floor)
# Rear partition surrounds a genuine open reception window.
# Window spans x=-2.7 to .6, z=1.06 to 2.35.
box('Reception low partition',(-1.05,2.2,.53),(3.3,.17,1.06),wall)
box('Reception header',(-1.05,2.2,2.82),(3.3,.17,.94),wall)
box('Reception left pier',(-3.3,2.2,1.645),(1.2,.17,3.29),wall)
box('Reception right pier',(2.25,2.2,1.645),(3.3,.17,3.29),wall)
box('Reception counter sill',(-1.05,2.14,1.095),(3.55,.64,.11),oak,.045)
for x in [-2.74,.64]: box('Reception opening jamb',(x,2.2,1.71),(.08,.22,1.3),oak,.012)
box('Reception opening lintel',(-1.05,2.2,2.36),(3.46,.23,.09),oak)
box('Rear office wall',(0,3.14,1.64),(7.8,.14,3.28),wall)
box('Left room wall',(-3.83,0,1.64),(.14,6.3,3.28),wall)
box('Left oak skirting',(-3.73,-.42,.09),(.065,5.3,.16),oak)
box('Reception front wainscot',(-1.05,2.103,.5),(3.25,.035,.9),sage)
text('WILLOW DENTAL',(-1.05,2.097,2.83),.25,teal)
text('RECEPTION',(-1.05,2.095,2.57),.105,teal)
# Visible work surface and storage beyond the window
box('Reception work desk',(-1.07,2.68,.79),(3.17,.66,.075),oak)
for x in [-2.3,.1]: box('Office storage pedestal',(x,2.73,.39),(.48,.52,.74),white)
box('Computer base',(-1.5,2.68,.866),(.35,.24,.055),dark)
rod('Computer support',(-1.5,2.71,.88),(-1.5,2.71,1.14),.032,metal)
box('Computer monitor back',(-1.5,2.69,1.3),(.63,.09,.42),dark,.025)
box('Keyboard',(-1.5,2.39,.856),(.47,.15,.025),dark,.007)
for i in range(4): box('File tray',(-.1,2.7,.88+i*.075),(.39,.28,.045),teal,.008)
box('Tissue box',(-2.12,2.03,1.23),(.24,.17,.16),white,.025)
box('Protruding tissue',(-2.12,2.03,1.34),(.13,.04,.1),paper,.015)
# Door on the solid portion of the rear partition
box('Consultation door frame',(2.37,2.086,1.25),(1.12,.08,2.5),oak)
box('Consultation door',(2.37,2.032,1.22),(.98,.045,2.4),white)
box('Frosted door insert',(2.37,1.997,1.68),(.61,.018,.86),glass)
text('TREATMENT',(2.37,1.981,1.67),.087,teal)
rod('Door lever',(2.72,1.954,1.08),(2.57,1.954,1.08),.017,metal)
# Comfortable individual waiting chairs, connected visually by a shared style

def chair(x,y,angle,color):
    root=bpy.data.objects.new('Waiting chair assembly',None); bpy.context.collection.objects.link(root)
    parts=[box('Rounded upholstered seat',(0,0,.47),(.62,.58,.13),color,.065),box('Upholstered back',(0,.255,.87),(.62,.115,.66),color,.065)]
    for dx in [-.255,.255]:
        for dy in [-.21,.21]: parts.append(rod('Chair leg',(dx,dy,.04),(dx,dy,.43),.022,metal))
    for dx in [-.35,.35]:
        parts.append(rod('Arm upright',(dx,-.12,.42),(dx,-.12,.71),.018,metal)); parts.append(box('Oak arm rest',(dx,0,.735),(.085,.5,.06),oak,.025))
    for o in parts: o.parent=root
    root.location=(x,y,0); root.rotation_euler.z=angle
for y in [-1.93,-.91,.11]: chair(-3.05,y,math.pi/2,sage)
for x in [-1.45,-.42,.61]: chair(x,1.2,0,blue if x<0 else sage)
# Small two-seat bench at right, leaving the path to treatment clear
for y in [-1.6,-.58]: chair(2.88,y,-math.pi/2,sage)
# Rounded magazine table and a lower shelf
box('Magazine table top',(-.45,-.72,.49),(1.58,.92,.085),oak,.14)
box('Magazine table lower shelf',(-.45,-.72,.2),(1.31,.69,.04),oak,.05)
for dx in [-.59,.59]:
    for dy in [-.27,.27]: rod('Coffee table leg',(-.45+dx,-.72+dy,.035),(-.45+dx,-.72+dy,.46),.024,metal)
for i,(x,y,c) in enumerate([(-.88,-.72,blue),(-.44,-.75,orange),(-.03,-.63,teal)]):
    root=bpy.data.objects.new('Magazine',None); bpy.context.collection.objects.link(root)
    objs=[box('Magazine pages',(0,0,0),(.29,.37,.016),paper,.003),box('Magazine cover',(0,0,.01),(.3,.38,.004),c,.002),box('Cover picture',(0,-.015,.013),(.23,.18,.002),sand,.001)]
    for k in range(3): objs.append(box('Cover title line',(0,.115-k*.018,.013),(.22-k*.035,.008,.002),paper,.001))
    for o in objs: o.parent=root
    root.location=(x,y,.545+i*.003); root.rotation_euler.z=[-.12,.15,-.2][i]
# Planters with stems and individually oriented leaves

def plant(x,y,r,height):
    bpy.ops.mesh.primitive_cone_add(vertices=40,radius1=r*.77,radius2=r,depth=.48,location=(x,y,.25)); bpy.context.object.name='Ceramic planter'; bpy.context.object.data.materials.append(white)
    cyl('Planter rim',(x,y,.49),r+.012,.045,white); cyl('Soil',(x,y,.51),r*.91,.015,soil)
    for i in range(11):
        a=i*2.399; top=Vector((x+r*1.3*math.cos(a),y+r*1.3*math.sin(a),.69+height*(.45+.55*random.random()))); base=Vector((x,y,.51)); rod('Plant stem',base,top,.008,leaf)
        for t in [.57,.88]:
            loc=base.lerp(top,t); direction=Vector((math.cos(a),math.sin(a),.7)); bpy.ops.mesh.primitive_uv_sphere_add(segments=12,ring_count=8,location=loc+direction*.07); o=bpy.context.object; o.name='Leaf'; o.scale=(.065,.024,.2); o.rotation_euler=direction.to_track_quat('Z','Y').to_euler(); o.data.materials.append(leaf if i%2 else leaf2)
plant(-3.13,1.27,.25,.9); plant(3.02,-2.73,.31,1.16)
# Water station and wall art
box('Water station cabinet',(3.17,.81,.46),(.59,.58,.9),oak)
box('Water dispenser',(3.17,.81,1.14),(.4,.39,.46),white,.045)
box('Dispenser recess',(3.17,.607,1.13),(.27,.02,.2),dark)
for x in [3.1,3.23]: cyl('Dispenser tap',(x,.572,1.2),.025,.04,teal,(math.pi/2,0,0))
cyl('Water carafe',(3.17,.81,1.51),.135,.29,glass)
# Calm abstract artwork on the left wall, facing into the room
for y in [-1.25,.05]:
    box('Artwork oak frame',(-3.731,y,2.13),(.07,.91,.94),oak)
    box('Artwork paper',(-3.686,y,2.13),(.015,.8,.83),paper,.005)
    cyl('Artwork circle',(-3.673,y-.12,2.27),.19,.008,sand,(0,math.pi/2,0))
    box('Artwork horizon',(-3.663,y,1.99),(.008,.72,.18),sage,.008)
# Reception clock
cyl('Clock frame',(3.28,2.07,2.79),.22,.055,metal,(math.pi/2,0,0)); cyl('Clock face',(3.28,2.036,2.79),.197,.008,white,(math.pi/2,0,0))
for i in range(12):
    a=i*math.tau/12; cyl('Hour mark',(3.28+.167*math.sin(a),2.026,2.79+.167*math.cos(a)),.009,.005,teal,(math.pi/2,0,0))
rod('Minute hand',(3.28,2.014,2.79),(3.28,2.014,2.94),.007,teal); rod('Hour hand',(3.28,2.01,2.79),(3.18,2.01,2.84),.009,teal)
# Roof omitted: soft architectural ceiling panels remain as fixtures
for x in [-1.8,1.65]:
    box('Ceiling light panel',(x,-.5,3.2),(1.25,.62,.055),white)
    area('Ceiling soft light',(x,-.5,3.14),240,(1,.95,.85),1.5,(x,-.5,0))
area('Office light',(-1.05,2.7,3.02),90,(1,.94,.85),1.5,(-1,2.5,.8)); area('Daylight from open facade',(0,-4,5),1050,(.85,.93,1),5,(0,1,0)); area('Room fill',(3,0,4.7),400,(1,.91,.78),3,(0,0,1))
bpy.ops.object.camera_add(location=(9.5,-12.8,8.3)); cam=bpy.context.object; cam.rotation_euler=(Vector((0,.12,1.12))-cam.location).to_track_quat('-Z','Y').to_euler(); cam.data.type='ORTHO'; cam.data.ortho_scale=10.7
s=bpy.context.scene; s.camera=cam; s.render.engine='CYCLES'; s.world.color=(.22,.22,.22); s.render.resolution_x=1500; s.render.resolution_y=1200; s.render.resolution_percentage=100
