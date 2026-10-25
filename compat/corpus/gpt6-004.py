import bpy, math
from mathutils import Vector
bpy.ops.wm.read_factory_settings(use_empty=True)

def mat(name,c,metal=0,rough=.4,emission=0):
    m=bpy.data.materials.new(name); m.diffuse_color=(*c,1); m.use_nodes=True
    p=m.node_tree.nodes.get('Principled BSDF'); p.inputs['Base Color'].default_value=(*c,1)
    p.inputs['Metallic'].default_value=metal; p.inputs['Roughness'].default_value=rough
    if emission:
        p.inputs['Emission Color'].default_value=(*c,1); p.inputs['Emission Strength'].default_value=emission
    return m
body=mat('Muted blue housing',(.10,.23,.30),.15)
back=mat('Rear housing',(.055,.11,.145))
dark=mat('Buttons and bezel',(.016,.023,.03),0,.48)
screen=mat('Screen navy',(.014,.033,.063),.15,.2,.18)
white=mat('Warm white print',(.8,.9,.91))
teal=mat('Mint controls',(.19,.73,.60))
coral=mat('Coral controls',(.92,.25,.16))
led=mat('Power indicator',(.25,1,.5),0,.25,3)
ui=mat('Screen cyan',(.14,.75,.91),0,.5,.65)
ground=mat('Studio backdrop',(.14,.17,.20),0,.8)

def box(name,loc,size,ma,bevel=.02):
    bpy.ops.mesh.primitive_cube_add(size=1,location=loc); o=bpy.context.object; o.name=name; o.dimensions=size
    bpy.ops.object.transform_apply(location=False,rotation=False,scale=True); o.data.materials.append(ma)
    if bevel:
        b=o.modifiers.new('Rounded edges','BEVEL'); b.width=bevel; b.segments=5
        o.modifiers.new('Weighted normals','WEIGHTED_NORMAL')
    return o

def disc(name,x,y,z,r,d,ma):
    bpy.ops.mesh.primitive_cylinder_add(vertices=48,radius=r,depth=d,location=(x,y,z))
    o=bpy.context.object; o.name=name; o.data.materials.append(ma)
    b=o.modifiers.new('Button lip','BEVEL'); b.width=.007; b.segments=3
    o.modifiers.new('Weighted normals','WEIGHTED_NORMAL'); return o

def text(name,string,loc,size,ma):
    cu=bpy.data.curves.new(name,'FONT'); cu.body=string; cu.size=size; cu.align_x='CENTER'; cu.align_y='CENTER'; cu.extrude=.0004
    ob=bpy.data.objects.new(name,cu); bpy.context.collection.objects.link(ob); ob.location=loc; cu.materials.append(ma); return ob

# Display-up landscape console; scene dimensions use a tenfold product scale.
box('Rear shell',(0,0,.115),(2.3,1.08,.20),back,.098)
box('Case seam',(0,0,.207),(2.298,1.078,.026),dark,.012)
box('Front shell',(0,0,.264),(2.3,1.08,.105),body,.051)
box('Display bezel',(0,.035,.32),(1.30,.88,.038),dark,.018)
box('Display glass',(0,.035,.341),(1.16,.73,.012),screen,.006)
# A fully modeled little pixel-game screen.
text('Game title','ORBIT', (0,.27,.351),.085,white)
text('Status','03   /   1200', (0,-.265,.351),.037,ui)
for x,y in [(-.46,.15),(-.24,.04),(.43,.19),(.34,-.09),(-.39,-.13),(.16,.10)]:
    box('Pixel star',(x,y,.351),(.016,.016,.002),white,.001)
for row,pattern in enumerate(['00100','01110','11111','10101']):
    for col,v in enumerate(pattern):
        if v=='1': box('Player ship',((col-2)*.024,-.07-row*.024,.353),(.022,.022,.004),ui,.001)
for x in (-.28,0,.28):
    for row,pattern in enumerate(['01110','11011','11111','01010']):
        for col,v in enumerate(pattern):
            if v=='1': box('Enemy pixel',(x+(col-2)*.018,.17-row*.018,.353),(.016,.016,.003),coral,.001)
# Cross-shaped D-pad built as a single manifold extruded outline.
cx,cy=-.89,.06; a,b=.17,.059
outline=[(-b,a),(b,a),(b,b),(a,b),(a,-b),(b,-b),(b,-a),(-b,-a),(-b,-b),(-a,-b),(-a,b),(-b,b)]
verts=[(cx+x,cy+y,z) for z in (.318,.373) for x,y in outline]; n=len(outline)
faces=[tuple(range(n)),tuple(range(2*n-1,n-1,-1))]+[(i,i+n,(i+1)%n+n,(i+1)%n) for i in range(n)]
mesh=bpy.data.meshes.new('D-pad mesh'); mesh.from_pydata(verts,[],faces); mesh.update()
o=bpy.data.objects.new('Directional cross',mesh); bpy.context.collection.objects.link(o); o.data.materials.append(dark)
b=o.modifiers.new('Soft control edges','BEVEL'); b.width=.012; b.segments=3; o.modifiers.new('Weighted normals','WEIGHTED_NORMAL')
for label,x,y,ma in [('A',1.015,.055,coral),('B',.87,-.09,teal),('X',.87,.20,teal),('Y',.725,.055,teal)]:
    disc('Button socket',x,y,.321,.087,.019,dark)
    disc('Action '+label,x,y,.354,.067,.057,ma)
    text('Button legend '+label,label,(x,y,.385),.042,dark)
for x,label in [(-.22,'SELECT'),(.22,'START')]:
    box(label+' button',(x,-.427,.334),(.14,.039,.025),dark,.012)
    text(label+' label',label,(x,-.48,.322),.024,white)
for x in (-.92,.92):
    for j in range(4): box('Speaker slot',(x+(j-1.5)*.043,-.345,.318),(.017,.105,.008),dark,.004)
for x in (-.83,.83): box('Shoulder trigger',(x,.51,.239),(.40,.10,.12),dark,.035)
disc('Power LED',.57,.458,.32,.013,.008,led)
box('USB port surround',(0,-.544,.125),(.17,.013,.063),dark,.006)
box('USB inner tongue',(0,-.553,.125),(.113,.007,.017),back,.002)
box('Ground',(0,0,-.042),(200,200,.08),ground,0)
world=bpy.data.worlds.new('World'); bpy.context.scene.world=world; world.use_nodes=True; world.node_tree.nodes['Background'].inputs[1].default_value=.3
for loc,power,size in [((-3,-4,5),700,4),((3,2,4),600,3)]:
    bpy.ops.object.light_add(type='AREA',location=loc); o=bpy.context.object; o.data.energy=power; o.data.size=size
    o.rotation_euler=(Vector((0,0,.2))-o.location).to_track_quat('-Z','Y').to_euler()
bpy.ops.object.camera_add(location=(1.6,-2.6,4.5)); cam=bpy.context.object
cam.rotation_euler=(Vector((0,0,.15))-cam.location).to_track_quat('-Z','Y').to_euler(); cam.data.type='ORTHO'; cam.data.ortho_scale=3.0
scene=bpy.context.scene; scene.camera=cam; scene.render.engine='CYCLES'
scene.render.resolution_x=1400; scene.render.resolution_y=1000; scene.render.resolution_percentage=100
