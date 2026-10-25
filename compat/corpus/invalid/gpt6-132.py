import bpy, math, random
from mathutils import Vector
random.seed(132)
bpy.ops.wm.read_factory_settings(use_empty=True)

def mat(name,c,rough=.55,metal=0):
    m=bpy.data.materials.new(name); m.diffuse_color=(*c,1); m.use_nodes=True; p=m.node_tree.nodes.get('Principled BSDF'); p.inputs['Base Color'].default_value=(*c,1); p.inputs['Roughness'].default_value=rough; p.inputs['Metallic'].default_value=metal; return m

def box(name,loc,size,m,b=.025):
    bpy.ops.mesh.primitive_cube_add(size=1,location=loc); o=bpy.context.object; o.name=name; o.dimensions=size; bpy.ops.object.transform_apply(location=False,rotation=False,scale=True); o.data.materials.append(m)
    if b:
        q=o.modifiers.new('Rounded edges','BEVEL'); q.width=b; q.segments=3; o.modifiers.new('Weighted normals','WEIGHTED_NORMAL')
    return o

def cyl(name,loc,r,d,m,rot=(0,0,0)):
    bpy.ops.mesh.primitive_cylinder_add(vertices=40,radius=r,depth=d,location=loc,rotation=rot); o=bpy.context.object; o.name=name; o.data.materials.append(m); q=o.modifiers.new('Rounded rim','BEVEL'); q.width=.01; q.segments=3; o.modifiers.new('Weighted normals','WEIGHTED_NORMAL'); return o

def rod(name,a,b,r,m):
    v=Vector(b)-Vector(a); o=cyl(name,(Vector(a)+Vector(b))/2,r,v.length,m); o.rotation_euler=v.to_track_quat('Z','Y').to_euler(); return o

def text(body,loc,size,m):
    bpy.ops.object.text_add(location=loc,rotation=(math.pi/2,0,0)); o=bpy.context.object; o.name=body; o.data.body=body; o.data.align_x='CENTER'; o.data.size=size; o.data.extrude=.001; o.data.materials.append(m)

def area(name,loc,power,color,size,target):
    bpy.ops.object.light_add(type='AREA',location=loc); o=bpy.context.object; o.name=name; o.data.energy=power; o.data.color=color; o.data.shape='DISK'; o.data.size=size; o.rotation_euler=(Vector(target)-o.location).to_track_quat('-Z','Y').to_euler()

plaster=mat('Warm plaster',(.79,.72,.61)); green=mat('Sage upholstery',(.18,.29,.23),.86); oak=mat('Honey oak',(.43,.25,.11)); dark=mat('Dark metal',(.035,.045,.041),.35,.65); brass=mat('Brass',(.58,.35,.1),.3,.75); stone=mat('Cream terrazzo',(.77,.73,.64)); white=mat('Glazed porcelain',(.93,.9,.8),.22); terracotta=mat('Terracotta',(.51,.22,.12)); leaf=mat('Leaves',(.12,.27,.12),.8); soil=mat('Soil',(.07,.038,.019)); coffee=mat('Coffee',(.07,.025,.01)); chalk=mat('Chalkboard',(.035,.08,.067)); steel=mat('Espresso machine steel',(.48,.52,.5),.23,.8)
box('Floor foundation',(0,0,-.14),(7.1,6.2,.28),terracotta)
for i in range(14):
    for j in range(12): box('Checker floor tile',(-3.25+i*.5,-2.75+j*.5,.015),(.487,.487,.035),stone if (i+j)%2 else plaster,.004)
box('Back wall',(0,3.03,1.7),(7.1,.15,3.4),plaster)
# Left wall with a large open window bay
box('Window wall sill',(-3.48,0,.49),(.15,6,.98),plaster)
box('Window wall header',(-3.48,0,3.17),(.15,6,.46),plaster)
for y in [-2.94,2.94]: box('Window wall pier',(-3.48,y,1.95),(.15,.17,2),plaster)
for y in [-2.8,-1.4,0,1.4,2.8]: box('Window mullion',(-3.46,y,1.96),(.12,.075,2),dark,.006)
for z in [1,2.94]: box('Window horizontal frame',(-3.46,0,z),(.15,5.7,.075),dark,.005)
box('Deep window ledge',(-3.35,0,1.0),(.42,5.8,.07),oak)
# Corner banquette: back wall and window wall
box('Back banquette plinth',(-1.43,2.49,.25),(3.65,.8,.5),oak)
box('Back banquette seat',(-1.43,2.44,.54),(3.7,.79,.17),green,.075)
box('Back banquette back',(-1.43,2.8,1.0),(3.7,.15,.9),green,.065)
box('Window banquette plinth',(-2.98,.15,.25),(.7,3.85,.5),oak)
box('Window banquette seat',(-2.95,.15,.54),(.77,3.88,.17),green,.075)
box('Window banquette back',(-3.28,.15,1.0),(.15,3.88,.9),green,.055)
for x in [-2.9,-2.3,-1.7,-1.1,-.5,.1]: box('Back upholstery seam',(x,2.716,1),(.009,.006,.74),oak,.002)
for y in [-1.5,-.8,-.1,.6,1.3]: box('Side upholstery seam',(-3.197,y,1),(.006,.009,.74),oak,.002)

def cup(x,y,z):
    cyl('Saucer',(x,y,z),.105,.017,white)
    cyl('Cup',(x,y,z+.057),.063,.095,white)
    cyl('Coffee surface',(x,y,z+.107),.052,.003,coffee)
    bpy.ops.mesh.primitive_torus_add(major_segments=20,minor_segments=8,location=(x+.069,y,z+.061),major_radius=.033,minor_radius=.009,rotation=(math.pi/2,0,0)); bpy.context.object.data.materials.append(white)

def table(x,y):
    cyl('Cafe table foot',(x,y,.065),.32,.07,dark); cyl('Cafe table pedestal',(x,y,.43),.042,.72,dark); cyl('Round oak table',(x,y,.83),.56,.075,oak)
    cup(x-.18,y,.876); cup(x+.21,y+.12,.876)
    cyl('Bud vase',(x+.06,y-.21,.97),.045,.17,terracotta); rod('Flower stem',(x+.06,y-.21,1.04),(x+.09,y-.2,1.22),.008,leaf)

def chair(x,y,angle):
    root=bpy.data.objects.new('Chair assembly',None); bpy.context.collection.objects.link(root)
    parts=[box('Chair seat',(0,0,.48),(.46,.46,.065),oak,.045),box('Chair curved style back',(0,.2,.81),(.46,.065,.43),oak,.055)]
    for dx in [-.17,.17]:
        for dy in [-.17,.17]: parts.append(rod('Chair leg',(dx*1.22,dy*1.22,.05),(dx,dy,.46),.022,dark))
    for o in parts: o.parent=root
    root.location=(x,y,0); root.rotation_euler.z=angle
for x,y in [(-1.88,1.52),(-1.96,-.3),(-1.96,-1.78)]: table(x,y)
chair(-.96,1.5,-math.pi/2); chair(-1.0,-.35,-math.pi/2); chair(-1.0,-1.86,-math.pi/2)
# Service counter on the right
box('Counter body',(1.94,.65,.54),(2.08,3.48,1.08),oak,.045)
for y in [i*.12-.98 for i in range(28)]: box('Counter vertical fluting',(.875,y,.53),(.045,.045,.91),terracotta,.012)
box('Stone counter top',(1.94,.65,1.115),(2.22,3.6,.12),stone,.045)
box('Back worktop',(2.12,2.55,.92),(2.43,.61,.11),oak)
for x in [1.35,2.1,2.85]:
    box('Under counter cabinet',(x,2.62,.46),(.7,.55,.85),green)
    box('Cabinet handle',(x,2.322,.72),(.24,.025,.025),brass,.01)
box('Espresso machine',(2.25,1.5,1.42),(1.03,.64,.49),steel,.06)
box('Machine black front',(2.25,1.17,1.43),(.91,.035,.27),dark)
box('Drip tray',(2.25,1.03,1.2),(.92,.3,.045),steel)
for x in [2.0,2.45]:
    rod('Group head',(x,1.14,1.46),(x,1.03,1.39),.043,steel); rod('Portafilter handle',(x,1.02,1.4),(x,.83,1.4),.025,dark); cup(x,1.03,1.23)
for x in [1.98,2.2,2.42]: cyl('Cup on machine',(x,1.5,1.73),.06,.1,white)
box('POS base',(1.75,-.72,1.23),(.3,.25,.1),dark)
box('POS screen',(1.75,-.71,1.45),(.43,.08,.3),dark).rotation_euler.x=math.radians(18)
cyl('Pastry platter',(2.5,-.15,1.19),.32,.025,white)
for i in range(5):
    a=i*math.tau/5; bpy.ops.mesh.primitive_uv_sphere_add(segments=16,ring_count=8,location=(2.5+.18*math.cos(a),-.15+.18*math.sin(a),1.25)); o=bpy.context.object; o.name='Fresh bread roll'; o.scale=(.1,.065,.05); o.data.materials.append(oak)
box('Menu frame',(1.65,2.91,2.31),(2.25,.07,1.12),oak)
box('Menu board',(1.65,2.865,2.31),(2.13,.02,1.0),chalk)
text('CORNER & CUP',(1.65,2.845,2.56),.21,white)
text('ESPRESSO   3     LATTE   4',(1.65,2.843,2.29),.12,white)
text('BAKED DAILY  /  SLOW MORNINGS',(1.65,2.843,2.05),.085,white)
# Three warm pendant lamps
for x,y in [(-1.88,1.5),(-1.96,-1.4),(1.95,.1)]:
    cyl('Ceiling rose',(x,y,3.36),.09,.055,dark); rod('Pendant cable',(x,y,3.33),(x,y,2.62),.009,dark)
    bpy.ops.mesh.primitive_cone_add(vertices=48,radius1=.3,radius2=.105,depth=.23,location=(x,y,2.53)); bpy.context.object.name='Brass pendant shade'; bpy.context.object.data.materials.append(brass)
    cyl('Opal diffuser',(x,y,2.408),.27,.015,white); area('Pendant warm pool',(x,y,2.38),85,(1,.72,.43),.5,(x,y,0))
cyl('Floor planter',(.12,2.26,.27),.26,.5,terracotta); cyl('Pot soil',(.12,2.26,.526),.23,.015,soil)
for i in range(12):
    a=i*2.4; top=(.12+.3*math.cos(a),2.26+.3*math.sin(a),.9+random.random()*.6); rod('Plant stem',(.12,2.26,.5),top,.009,leaf)
    bpy.ops.mesh.primitive_uv_sphere_add(segments=12,ring_count=8,location=top); o=bpy.context.object; o.name='Plant leaf'; o.scale=(.085,.035,.22); o.rotation_euler=(.4*math.cos(a),.6*math.sin(a),a); o.data.materials.append(leaf)
area('Window daylight',(-5,-1,4),1000,(.77,.86,1),4,(0,0,0)); area('Front fill',(3,-4,5),750,(1,.89,.74),5,(0,1,0))
bpy.ops.object.camera_add(location=(8.7,-11,8)); cam=bpy.context.object; cam.rotation_euler=(Vector((0,.1,1.15))-cam.location).to_track_quat('-Z','Y').to_euler(); cam.data.type='ORTHO'; cam.data.ortho_scale=10.1
s=bpy.context.scene; s.camera=cam; s.render.engine='CYCLES'; s.world.color=(.2,.2,.2); s.render.resolution_x=1500; s.render.resolution_y=1200; s.render.resolution_percentage=100
