import bpy, math, random
from mathutils import Vector
random.seed(149)
bpy.ops.object.select_all(action='SELECT'); bpy.ops.object.delete(use_global=False)

def mat(name,c,metal=0,rough=.6):
    m=bpy.data.materials.new(name); m.diffuse_color=(*c,1); m.use_nodes=True; p=m.node_tree.nodes['Principled BSDF']; p.inputs['Base Color'].default_value=(*c,1); p.inputs['Metallic'].default_value=metal; p.inputs['Roughness'].default_value=rough; return m
wood=mat('Weathered deck timber',(.46,.35,.23)); timber=mat('Pavilion glulam',(.65,.43,.22)); steel=mat('Dark coastal steel',(.07,.12,.14),.7,.3)
roof=mat('Standing seam zinc',(.28,.37,.39),.7,.34); rock=mat('Coastal sandstone',(.43,.41,.34)); grass=mat('Dune grasses',(.39,.42,.19)); sand=mat('Dune sand',(.62,.57,.43)); water=mat('Sea',(.075,.29,.34),.3,.23)
glass=mat('Pale blue wind screen',(.43,.69,.72),.05,.15); glass.node_tree.nodes['Principled BSDF'].inputs['Transmission Weight'].default_value=.65


def box(name,loc,size,m,bev=0):
    bpy.ops.mesh.primitive_cube_add(size=1,location=loc); o=bpy.context.object; o.name=name; o.dimensions=size; bpy.ops.object.transform_apply(location=False,rotation=False,scale=True); o.data.materials.append(m)
    if bev:
        b=o.modifiers.new('Weathered edges','BEVEL'); b.width=bev; b.segments=2; o.modifiers.new('Normals','WEIGHTED_NORMAL')
    return o

def beam(name,a,b,w,d,m):
    a,b=Vector(a),Vector(b); o=box(name,(a+b)/2,(w,d,(b-a).length),m,.018); o.rotation_euler=(b-a).to_track_quat('Z','Y').to_euler(); return o

def mesh(name,vs,fs,m):
    me=bpy.data.meshes.new(name); me.from_pydata(vs,[],fs); me.update(); o=bpy.data.objects.new(name,me); bpy.context.collection.objects.link(o); o.data.materials.append(m); return o

box('Sea plane',(0,7,-1.2),(75,60,.25),water)
# Low irregular headland rises above the water, with a rocky seaward face.
outline=[(-13,-13),(13,-13),(13,0),(9,4),(4,5),(0,4.3),(-5,5.2),(-10,3),(-13,0)]
vs=[(x,y,-1.3) for x,y in outline]+[(x,y,.15+random.uniform(-.08,.08)) for x,y in outline]; n=len(outline)
fs=[tuple(range(n,2*n)),tuple(reversed(range(n)))]+[(i,(i+1)%n,(i+1)%n+n,i+n) for i in range(n)]
mesh('Rocky headland',vs,fs,sand)
for i in range(28):
    x=random.uniform(-12,12); y=3.1+random.uniform(-.3,1.4)-abs(x)*.10
    bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=1,radius=1,location=(x,y,-.25)); o=bpy.context.object; o.name='Shore rock'; o.scale=(random.uniform(.65,1.5),random.uniform(.65,1.15),random.uniform(.7,1.4)); o.rotation_euler=(random.random(),random.random(),random.random()); o.data.materials.append(rock)
# The deck projects beyond the shoreline on visible piles.
for x in (-4.5,0,4.5):
    for y in (-2,2.5,5):
        box('Concrete pier',(x,y,-.10),(.6,.6,2.1),rock,.05)
        box('Deck pile cap',(x,y,.81),(.78,.78,.18),steel,.025)
for x in (-4.5,0,4.5): box('Longitudinal deck bearer',(x,1.2,.94),(.20,8.4,.28),steel,.02)
for y in (-2.6,-1.3,0,1.3,2.6,3.9,5.2): box('Deck cross joist',(0,y,1.12),(10.4,.16,.24),steel,.018)
for i in range(48):
    y=-2.85+i*.17
    box('Individual deck plank',(0,y,1.29),(10.4,.158,.12),wood,.012)
# Three entry steps on the landward side.
for i in range(4): box('Broad approach step',(0,-4.65+i*.45,.15+i*.30),(3.4,.47,.28),wood,.035)
# Timber columns support a sharply folded, asymmetric roof.
for x in (-4,4):
    for y in (-1.9,3.7):
        z=4.15 if x<0 else 4.55
        box('Column steel shoe',(x,y,1.50),(.28,.28,.42),steel,.025)
        box('Glulam column',(x,y,(1.4+z)/2),(.23,.23,z-1.4),timber,.025)
        beam('Knee brace',(x,y,z-.85),(x+(.8 if x<0 else -.8),y,z+.12),.14,.14,timber)
# Ridge runs fore and aft; unequal eaves make the angular silhouette legible.
roofverts=[(-5,-2.8,4.15),(0,-2.8,5.45),(5,-2.8,4.55),(-5,4.6,4.15),(0,4.6,5.45),(5,4.6,4.55)]
o=mesh('Folded angular pavilion roof',roofverts,[(0,1,4,3),(1,2,5,4)],roof); s=o.modifiers.new('Roof sheet thickness','SOLIDIFY'); s.thickness=.13; b=o.modifiers.new('Roof edge bevel','BEVEL'); b.width=.025; b.segments=2
for y in (-2.65,-1.2,.4,2,3.6,4.45):
    beam('Exposed left roof rafter',(-4.9,y,4.02),(0,y,5.32),.15,.19,timber)
    beam('Exposed right roof rafter',(0,y,5.32),(4.9,y,4.42),.15,.19,timber)
for x in [i*.5 for i in range(-10,11)]:
    z=5.45+(x*.26 if x<0 else -x*.18)
    beam('Raised zinc seam',(x,-2.8,z+.035),(x,4.6,z+.035),.025,.035,roof)
for x,z in ((-5,4.14),(0,5.44),(5,4.54)): beam('Roof longitudinal fascia',(x,-2.8,z),(x,4.6,z),.14,.14,steel)
# Tall wind screens protect both ends; clear front balustrade preserves the view.
for x in (-4.85,4.85):
    for j in range(4):
        y=-1.85+j*1.5
        box('Wind screen glass',(x,y+.71,2.49),(.035,1.38,2.25),glass,.01)
        box('Wind screen upright',(x,y,2.55),(.07,.07,2.4),steel,.01)
    box('Last wind screen upright',(x,4.15,2.55),(.07,.07,2.4),steel,.01)
    for z in (1.45,3.64): box('Wind screen horizontal frame',(x,1.15,z),(.075,6,.075),steel,.01)
for i in range(7):
    x=-5.1+i*1.7
    box('Viewing edge balustrade post',(x,5.2,1.93),(.06,.07,1.2),steel,.01)
    if i<6: box('Viewing edge glass panel',(x+.85,5.2,1.90),(1.59,.025,1.0),glass,.006)
box('Continuous viewing handrail',(0,5.2,2.54),(10.3,.10,.08),timber,.025)
# Rail returns flank the central stair opening.
for x in (-3.4,3.4):
    for xx in (x-1.65,x+1.65): box('Rear railing post',(xx,-2.9,1.94),(.06,.06,1.2),steel)
    box('Rear guard handrail',(x,-2.9,2.54),(3.3,.08,.08),steel,.018)
    box('Rear guard middle rail',(x,-2.9,1.95),(3.3,.06,.06),steel,.01)
for x in (-3.2,3.2):
    for y in (-.6,1.0): box('Bench leg',(x,y,1.55),(.12,.14,.45),steel,.015)
    for j in range(4): box('Viewing bench seat',(x-.27+j*.18,.2,1.82),(.165,2.3,.10),wood,.015)
beam('Interpretive panel pedestal',(0,3.4,1.35),(0,3.4,2.15),.10,.10,steel)
o=box('Angled interpretive map',(0,3.4,2.17),(1.5,.72,.06),steel,.04); o.rotation_euler[0]=math.radians(18)
for i in range(32):
    x=random.uniform(-11,11); y=random.uniform(-10,1)
    if abs(x)<5.6: continue
    for j in range(5):
        a=random.uniform(0,math.tau); h=random.uniform(.25,.65)
        beam('Dune grass blade',(x,y,.15),(x+.22*math.cos(a),y+.22*math.sin(a),h+.15),.018,.026,grass)
scene=bpy.context.scene; scene.render.engine='CYCLES'; scene.cycles.samples=64; scene.world.color=(.40,.47,.52)
bpy.ops.object.light_add(type='AREA',location=(-3,-7,16)); bpy.context.object.data.energy=2000; bpy.context.object.data.size=11
bpy.ops.object.light_add(type='SUN'); bpy.context.object.rotation_euler=(.55,-.45,-.5); bpy.context.object.data.energy=2; bpy.context.object.data.angle=.16
bpy.ops.object.camera_add(location=(19,23,15)); cam=bpy.context.object; cam.rotation_euler=(Vector((0,.5,1.6))-cam.location).to_track_quat('-Z','Y').to_euler(); cam.data.type='ORTHO'; cam.data.ortho_scale=24; scene.camera=cam
scene.render.resolution_x=1500; scene.render.resolution_y=1100; scene.render.resolution_percentage=100
