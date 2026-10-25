import bpy, math, random
from mathutils import Vector
random.seed(136)
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)
for block in list(bpy.data.materials):
    bpy.data.materials.remove(block)

def mat(name, color, metal=0, rough=.5, emission=0):
    m=bpy.data.materials.new(name); m.diffuse_color=(*color,1); m.use_nodes=True
    p=m.node_tree.nodes.get('Principled BSDF'); p.inputs['Base Color'].default_value=(*color,1)
    p.inputs['Metallic'].default_value=metal; p.inputs['Roughness'].default_value=rough
    if emission: p.inputs['Emission Color'].default_value=(*color,1); p.inputs['Emission Strength'].default_value=emission
    return m

def box(name, loc, size, material, bevel=.025):
    bpy.ops.mesh.primitive_cube_add(size=1, location=loc); o=bpy.context.object; o.name=name
    o.dimensions=size; bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    o.data.materials.append(material)
    if bevel:
        m=o.modifiers.new('Soft edges','BEVEL'); m.width=bevel; m.segments=2
        o.modifiers.new('Weighted normals','WEIGHTED_NORMAL')
    return o

def rod(name,a,b,r,material,vertices=16):
    a,b=Vector(a),Vector(b); d=b-a
    bpy.ops.mesh.primitive_cylinder_add(vertices=vertices, radius=r, depth=d.length, location=(a+b)/2)
    o=bpy.context.object; o.name=name; o.rotation_euler=d.to_track_quat('Z','Y').to_euler(); o.data.materials.append(material)
    m=o.modifiers.new('Edge bevel','BEVEL'); m.width=min(.012,r*.18); m.segments=2
    o.modifiers.new('Normals','WEIGHTED_NORMAL'); return o

def light(name,loc,power,color,size,target):
    bpy.ops.object.light_add(type='AREA', location=loc); o=bpy.context.object; o.name=name
    o.data.energy=power; o.data.color=color; o.data.shape='DISK'; o.data.size=size
    o.rotation_euler=(Vector(target)-o.location).to_track_quat('-Z','Y').to_euler()

wood=mat('Honey oak',(.43,.235,.105)); pale=mat('Fresh wood',(.66,.45,.23)); dark=mat('Graphite steel',(.065,.078,.083),.75,.3)
steel=mat('Brushed tool steel',(.43,.48,.50),.85,.25); brick=mat('Warm brick',(.35,.14,.075)); mortar=mat('Mortar',(.40,.35,.28))
wall=mat('Chalk plaster',(.70,.68,.60)); peg=mat('Fiberboard',(.38,.245,.125)); hole=mat('Peg holes',(.065,.045,.022))
green=mat('Machine green',(.105,.24,.20),.35); red=mat('Red tool grips',(.57,.07,.035)); glow=mat('Warm bulbs',(1,.69,.34),emission=5)
blue=mat('Window daylight',(.38,.67,.86),rough=.28,emission=.6)
# Open-front industrial loft shell.
box('Floor foundation',(0,0,-.16),(8,6.4,.28),dark)
for i in range(20):
    x=-3.8+i*.4
    for j in range(4):
        box('Individual floorboard',(x,-2.4+j*1.6,0),(.388,1.585,.065),wood if (i+j)%3 else pale,.008)
box('Rear mortar wall',(0,3.12,2.2),(8,.20,4.4),mortar)
for row in range(15):
    for col in range(13):
        x=-3.9+col*.64+(row%2)*.32
        if x<3.94: box('Exposed brick',(x,2.996,.16+row*.285),(.61,.055,.255),brick,.012)
box('Left plaster wall',(-4,0,2.2),(.16,6.3,4.4),wall)
for y in [-2.85,.0,2.85]:
    box('Roof joist',(0,y,4.32),(8.15,.18,.25),dark)
    box('Joist end plate',(-3.87,y,4.0),(.10,.35,.65),dark)
# Loft window mounted on side wall, with deep reveal and metal mullions.
box('Window recess',(-3.89,.7,2.65),(.055,2.85,2.45),dark)
box('Window blue glass',(-3.85,.7,2.65),(.035,2.64,2.24),blue)
for y in [-.65,.25,1.15,2.05]: box('Window mullion',(-3.79,y,2.65),(.10,.045,2.36),dark,.005)
for z in [1.48,2.65,3.82]: box('Window crossbar',(-3.79,.7,z),(.10,2.78,.055),dark,.005)
box('Window sill',(-3.65,.7,1.43),(.50,3.0,.12),pale)
# Heavy workbench.
box('Laminated workbench top',(.05,1.8,1.30),(5.8,1.12,.18),pale)
for x in [-2.55,2.55]:
    for y in [1.39,2.2]: box('Bench leg',(x,y,.64),(.15,.15,1.24),dark)
    box('Bench lower brace',(x,1.8,.23),(.14,1.02,.12),dark)
box('Lower storage shelf',(0,1.81,.35),(5.25,.86,.09),wood)
box('Bench apron',(0,1.29,1.07),(5.5,.09,.28),wood)
for x in [-1.9,-.65,.6]:
    box('Bench drawer',(x,1.23,1.07),(1.14,.09,.25),green)
    rod('Drawer pull',(x-.18,1.145,1.08),(x+.18,1.145,1.08),.025,steel)
# Pegboard, drilled-hole impression, and metal perimeter.
box('Pegboard',(0,2.80,2.57),(4.9,.10,1.9),peg)
for x in [-2.49,2.49]: box('Pegboard frame',(x,2.72,2.57),(.06,.07,2.0),dark,.008)
for z in [1.59,3.55]: box('Pegboard frame',(0,2.72,z),(5.04,.07,.06),dark,.008)
for i in range(30):
    for j in range(11):
        x=-2.32+i*.16; z=1.76+j*.16
        rod('Peg perforation',(x,2.742,z),(x,2.733,z),.016,hole,8)
# Readable silhouettes of hanging tools.
for x,z in [(-1.96,2.9),(-1.47,2.65)]:
    rod('Hammer handle',(x,2.58,z-.64),(x,2.58,z-.10),.042,wood)
    box('Hammer head',(x,2.58,z),(.40,.14,.15),steel)
for i,x in enumerate([-.86,-.57,-.28]):
    rod('Screwdriver grip',(x,2.59,2.2),(x,2.59,2.52),.055,red if i%2 else green)
    rod('Screwdriver shaft',(x,2.59,2.52),(x,2.59,2.93+i*.08),.017,steel)
for x in [.27,.66,1.05]:
    rod('Spanner stem',(x,2.58,2.14),(x,2.58,2.82),.035,steel)
    rod('Spanner jaw left',(x-.075,2.58,2.92),(x-.075,2.58,2.78),.028,steel)
    rod('Spanner jaw right',(x+.075,2.58,2.92),(x+.075,2.58,2.78),.028,steel)
    rod('Spanner jaw bridge',(x-.075,2.58,2.78),(x+.075,2.58,2.78),.032,steel)
box('Saw blade',(1.72,2.59,2.67),(.37,.035,.72),steel)
for i in range(10):
    tooth=box('Saw tooth',(1.515,2.59,2.36+i*.064),(.085,.033,.045),steel,.003); tooth.rotation_euler.y=.55
box('Saw wooden grip',(1.73,2.58,3.16),(.34,.11,.23),wood)
box('Grip inset',(1.73,2.513,3.16),(.18,.012,.10),hole)
for x in [-1.96,-1.47,-.86,-.57,-.28,.27,.66,1.05,1.73]:
    rod('Peg hook',(x,2.73,3.34),(x,2.52,3.34),.018,steel)
# Drawer chest.
box('Tool chest body',(3.15,1.95,.79),(1.1,1.08,1.48),dark)
for j in range(6):
    z=.24+j*.22; box('Chest drawer',(3.15,1.38,z),(.97,.08,.19),green)
    rod('Chest handle',(2.86,1.30,z),(3.44,1.30,z),.022,steel)
box('Chest wooden top',(3.15,1.95,1.58),(1.2,1.16,.12),wood)
# Bench vise and a small project.
box('Vise base',(-2.06,1.33,1.44),(.52,.45,.11),green)
box('Vise body',(-2.06,1.12,1.58),(.30,.49,.24),green)
for y in [.91,1.22]: box('Vise jaw',(-2.06,y,1.75),(.50,.11,.16),steel)
rod('Vise screw',(-2.06,.65,1.56),(-2.06,1.17,1.56),.045,steel)
rod('Vise sliding handle',(-2.06,.67,1.35),(-2.06,.67,1.78),.025,steel)
for i in range(4): box('Project wood offcut',(.1+i*.18,1.72,1.44+i*.027),(.13,.62,.065),wood)
box('Open sketchbook',(1.15,1.64,1.412),(.65,.47,.028),wall,.008)
for i in range(4): box('Pencil sketch line',(1.13,1.53+i*.055,1.429),(.40,.006,.002),dark,0)
# Two articulated task lamps.
for x in [-2.65,2.30]:
    rod('Lamp foot',(x,2.06,1.4),(x,2.06,1.46),.16,dark,32)
    a=(x,2.06,1.48); b=(x-.18,2.04,2.05); c=(x+.20,1.80,2.35)
    rod('Lamp lower arm',a,b,.034,dark); rod('Lamp upper arm',b,c,.03,dark)
    rod('Lamp pivot',(b[0],1.97,b[2]),(b[0],2.11,b[2]),.067,steel)
    bpy.ops.mesh.primitive_cone_add(vertices=32,radius1=.22,radius2=.09,depth=.22,location=(c[0],c[1],c[2]-.10))
    bpy.context.object.name='Enamel task lamp shade'; bpy.context.object.data.materials.append(green)
    rod('Lamp diffuser',(c[0],c[1],c[2]-.215),(c[0],c[1],c[2]-.225),.19,glow,32)
    light('Task pool',(c[0],c[1],c[2]-.25),65,(1,.73,.43),.35,(x,1.6,1.3))
# Stool and stocked shelf.
rod('Stool seat',(.6,-.05,.81),(.6,-.05,.92),.37,wood,40)
for a in [0,2.094,4.188]: rod('Splayed stool leg',(.6+.29*math.cos(a),-.05+.29*math.sin(a),.83),(.6+.42*math.cos(a),-.05+.42*math.sin(a),.08),.045,dark)
for i in range(4): box('Shelf parts bin',(-1.9+i*.91,1.75,.59),(.72,.63,.39),green)
light('Window soft light',(-3.2,-.2,3.3),650,(.69,.83,1),3,(0,1,1))
light('Front softbox',(2,-4,6),1100,(1,.86,.68),5,(0,1,1))
scene=bpy.context.scene; scene.world.color=(.20,.20,.20)
bpy.ops.object.camera_add(location=(9,-12,8.0)); camera=bpy.context.object
camera.rotation_euler=(Vector((0,.65,1.85))-camera.location).to_track_quat('-Z','Y').to_euler(); camera.data.type='ORTHO'; camera.data.ortho_scale=11.7
scene.camera=camera; scene.render.engine='CYCLES'; scene.cycles.samples=64
scene.render.resolution_x=1500; scene.render.resolution_y=1150; scene.render.resolution_percentage=100
scene.view_settings.view_transform='AgX'
