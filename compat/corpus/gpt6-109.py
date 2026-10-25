import bpy, math
from mathutils import Vector
bpy.ops.object.select_all(action='SELECT'); bpy.ops.object.delete(use_global=False)

def mat(name,c,rough=.4,metal=0):
    m=bpy.data.materials.new(name); m.diffuse_color=(*c,1); m.use_nodes=True; p=m.node_tree.nodes.get('Principled BSDF'); p.inputs['Base Color'].default_value=(*c,1); p.inputs['Roughness'].default_value=rough; p.inputs['Metallic'].default_value=metal; return m

def box(name,loc,size,m,bevel=.04):
    bpy.ops.mesh.primitive_cube_add(size=1,location=loc); o=bpy.context.object; o.name=name; o.dimensions=size; bpy.ops.object.transform_apply(location=False,rotation=False,scale=True); o.data.materials.append(m)
    if bevel:
        b=o.modifiers.new('Molded edge radii','BEVEL'); b.width=bevel; b.segments=4; o.modifiers.new('Weighted normals','WEIGHTED_NORMAL')
    return o

def cyl(name,loc,r,depth,m,axis='X',vertices=64):
    bpy.ops.mesh.primitive_cylinder_add(vertices=vertices,radius=r,depth=depth,location=loc); o=bpy.context.object; o.name=name
    if axis=='X': o.rotation_euler.y=math.pi/2
    elif axis=='Y': o.rotation_euler.x=math.pi/2
    o.data.materials.append(m); b=o.modifiers.new('Machined edge','BEVEL'); b.width=.012; b.segments=3; o.modifiers.new('Weighted normals','WEIGHTED_NORMAL'); return o

def profile(name,rings,m,n=64):
    verts=[]
    for x,r,z in rings:
        for i in range(n):
            a=math.tau*i/n; verts.append((x,r*math.cos(a),z+r*math.sin(a)))
    faces=[tuple(reversed(range(n)))]
    for j in range(len(rings)-1):
        for i in range(n):
            q=j*n+i; qn=j*n+(i+1)%n; faces.append((q,qn,qn+n,q+n))
    faces.append(tuple((len(rings)-1)*n+i for i in range(n)))
    mesh=bpy.data.meshes.new(name); mesh.from_pydata(verts,[],faces); mesh.update(); o=bpy.data.objects.new(name,mesh); bpy.context.collection.objects.link(o); o.data.materials.append(m)
    for p in mesh.polygons: p.use_smooth=len(p.vertices)==4
    return o

def tube(name,points,r,m):
    c=bpy.data.curves.new(name,'CURVE'); c.dimensions='3D'; c.bevel_depth=r; c.bevel_resolution=3; s=c.splines.new('POLY'); s.points.add(len(points)-1)
    for p,co in zip(s.points,points): p.co=(*co,1)
    o=bpy.data.objects.new(name,c); bpy.context.collection.objects.link(o); o.data.materials.append(m); return o

def area(name,loc,power,size,target,color=(1,1,1)):
    bpy.ops.object.light_add(type='AREA',location=loc); o=bpy.context.object; o.name=name; o.data.energy=power; o.data.shape='DISK'; o.data.size=size; o.data.color=color; o.rotation_euler=(Vector(target)-o.location).to_track_quat('-Z','Y').to_euler()

yellow=mat('Safety ochre housing',(.93,.48,.035),.32); rubber=mat('Graphite overmold',(.026,.033,.037),.72); black=mat('Black hard polymer',(.055,.068,.074),.35); steel=mat('Machined stainless steel',(.5,.56,.6),.23,.9); darksteel=mat('Dark chuck steel',(.12,.15,.17),.29,.8); white=mat('Printed markings',(.84,.88,.86),.45); orange=mat('Battery release orange',(.94,.25,.025),.36)
# Stable battery foot supports the angled ergonomic grip.
box('Battery rubber bumper',(.5,0,.17),(1.76,1.16,.3),rubber,.105)
box('Battery pack main case',(.5,0,.42),(1.69,1.1,.43),black,.11)
box('Battery upper shell',(.5,0,.68),(1.53,1.02,.18),yellow,.07)
box('Battery slide rail',(.52,0,.8),(1.02,.74,.15),black,.035)
for y in [-.558,.558]:
    box('Battery release button',(.16,y,.55),(.46,.048,.21),orange,.035)
    box('Battery label',(.66,y,.34),(.73,.012,.19),rubber,.012)
    for x in [.25,.47,.69,.91,1.13]: box('Battery cooling slot',(x,y,.17),(.1,.025,.1),black,.008)
# Grip is a tapered, leaning solid loft with rectangular rounded edges.
verts=[]
for z,x,w,d in [(.79,.52,.66,.67),(1.05,.46,.58,.64),(1.7,.27,.54,.59),(2.25,.11,.68,.68),(2.43,.05,.87,.76)]:
    verts.extend([(x-w/2,-d/2,z),(x+w/2,-d/2,z),(x+w/2,d/2,z),(x-w/2,d/2,z)])
faces=[(3,2,1,0)]
for j in range(4):
    for i in range(4): faces.append((j*4+i,j*4+(i+1)%4,(j+1)*4+(i+1)%4,(j+1)*4+i))
faces.append((16,17,18,19)); mesh=bpy.data.meshes.new('Grip mesh'); mesh.from_pydata(verts,[],faces); mesh.update(); grip=bpy.data.objects.new('Ergonomic grip',mesh); bpy.context.collection.objects.link(grip); grip.data.materials.append(yellow); b=grip.modifiers.new('Rounded grip','BEVEL'); b.width=.095; b.segments=4; grip.modifiers.new('Grip normals','WEIGHTED_NORMAL')
for y in [-.325,.325]:
    o=box('Rubber grip side panel',(.38,y,1.48),(.4,.065,1.08),rubber,.09); o.rotation_euler.y=math.radians(-15)
    for i in range(6):
        z=1.03+i*.145; x=.48-(z-1.03)*.27
        o=box('Raised grip traction rib',(x,y*1.105,z),(.32,.024,.048),black,.015); o.rotation_euler.y=math.radians(-15)
# Main motor pod points toward negative X.
profile('Motor housing', [(-.86,.37,2.7),(-.64,.49,2.7),(.52,.51,2.7),(1.02,.44,2.7),(1.18,.32,2.7)],yellow)
profile('Rear rubber bumper',[(.93,.447,2.7),(1.13,.4,2.7),(1.24,.3,2.7)],rubber)
cyl('Rear end cap',(1.245,0,2.7),.28,.035,black)
for y in [-.46,.46]:
    box('Motor side inset',(.28,y,2.76),(.85,.052,.34),black,.1)
    for i in range(6):
        o=box('Motor ventilation opening',(.54+i*.082,y,2.64),(.038,.05,.25),rubber,.012); o.rotation_euler.y=math.radians(-16)
    box('Housing seam',(-.39,y,2.7),(.014,.04,.33),rubber,.004)
    for x,z in [(-.48,2.91),(.4,2.46),(.8,2.88)]:
        cyl('Recessed assembly screw',(x,y*1.025,z),.042,.025,darksteel,'Y',24)
        box('Screw slot',(x,y*1.058,z),(.042,.005,.009),rubber,.002)
box('Forward reverse switch',(-.12,0,2.29),(.3,.92,.15),black,.04)
o=box('Trigger',(-.34,-.015,2.06),(.23,.51,.38),rubber,.065); o.rotation_euler.y=math.radians(-12)
box('Top speed selector',(.12,0,3.207),(.48,.27,.095),black,.03)
for x in [-.03,.07,.17,.27]: box('Selector traction rib',(x,0,3.261),(.025,.21,.018),rubber,.006)
# Gearbox, torque collar, knurled keyless chuck and three jaws.
cyl('Gearbox shoulder',(-.92,0,2.7),.395,.3,darksteel)
cyl('Torque selector ring',(-1.17,0,2.7),.39,.28,black)
for i in range(24):
    a=math.tau*i/24
    o=box('Torque ring ridge',(-1.17,.393*math.cos(a),2.7+.393*math.sin(a)),(.2,.043,.045),rubber,.009); o.rotation_euler.x=a
cyl('Torque index band',(-1.345,0,2.7),.365,.07,silver if False else steel)
for i in range(16):
    a=math.tau*i/16
    o=box('Torque index tick',(-1.39,.365*math.cos(a),2.7+.365*math.sin(a)),(.028,.024,.014),white,.003); o.rotation_euler.x=a
profile('Chuck body',[(-1.41,.325,2.7),(-1.55,.35,2.7),(-1.92,.32,2.7),(-2.13,.235,2.7)],darksteel)
for i in range(40):
    a=math.tau*i/40
    o=box('Chuck knurl rib',(-1.73,.339*math.cos(a),2.7+.339*math.sin(a)),(.28,.018,.02),black,.005); o.rotation_euler.x=a
cyl('Chuck polished nose',(-2.13,0,2.7),.233,.12,steel)
cyl('Chuck dark bore',(-2.197,0,2.7),.136,.02,rubber)
for i in range(3):
    a=math.tau*i/3
    o=box('Chuck clamping jaw',(-2.225,.071*math.cos(a),2.7+.071*math.sin(a)),(.14,.07,.075),steel,.012); o.rotation_euler.x=a
cyl('Hex driver shank',(-2.49,0,2.7),.052,.49,steel,vertices=6)
profile('Driver tip',[(-2.735,.044,2.7),(-2.89,.04,2.7),(-2.96,.011,2.7)],darksteel,n=6)
# Side lettering sits flush on the visible side of the tool.
def label(body,loc,size,material):
    c=bpy.data.curves.new(body,'FONT'); c.body=body; c.align_x='CENTER'; c.size=size; c.extrude=.0005; o=bpy.data.objects.new(body,c); bpy.context.collection.objects.link(o); o.location=loc; o.rotation_euler=(math.pi/2,0,0); o.data.materials.append(material)
label('VOLT',(.2,-.491,2.76),.14,white); label('18V',(.72,-.569,.3),.14,white)
led=mat('Work light',(.9,.95,1),.2); p=led.node_tree.nodes.get('Principled BSDF'); p.inputs['Emission Color'].default_value=(.7,.85,1,1); p.inputs['Emission Strength'].default_value=2
box('LED work light bezel',(-.18,-.34,2.4),(.22,.09,.12),black,.035); box('LED work light lens',(-.18,-.391,2.4),(.14,.013,.055),led,.012)
tube('Belt clip',[(.82,.42,.9),(.92,.67,.83),(1.1,.67,.43),(1.29,.67,.45),(1.3,.67,.63)],.036,steel)
box('Studio ground',(0,0,-.085),(200,200,.12),mat('Slate backdrop',(.11,.145,.17),.58),.01)
area('Key softbox',(-4,-5,7),850,4,(-.5,0,1.6)); area('Warm rim',(3,3,5),1100,3,(0,0,2),(1,.77,.51)); area('Chuck strip',(-5,2,3.8),700,2,(-1,0,2.6),(.65,.8,1)); area('Front fill',(1,-5,2),180,3,(0,0,1.5))
bpy.ops.object.camera_add(location=(-7.8,-10,2.45)); camera=bpy.context.object; camera.name='Low angle drill hero'; camera.data.lens=54; camera.rotation_euler=(Vector((-.65,0,1.58))-camera.location).to_track_quat('-Z','Y').to_euler(); bpy.context.scene.camera=camera
scene=bpy.context.scene; scene.world.color=(.17,.2,.24); scene.render.engine='CYCLES'; scene.cycles.samples=64; scene.render.resolution_x=1500; scene.render.resolution_y=1100; scene.render.resolution_percentage=100; scene.view_settings.view_transform='AgX'
