import bpy, math, random
from mathutils import Vector
random.seed(140)
bpy.ops.object.select_all(action='SELECT'); bpy.ops.object.delete(use_global=False)

def mat(n,c,metal=0,rough=.5,emit=0):
    m=bpy.data.materials.new(n); m.diffuse_color=(*c,1); m.use_nodes=True; p=m.node_tree.nodes.get('Principled BSDF')
    p.inputs['Base Color'].default_value=(*c,1); p.inputs['Metallic'].default_value=metal; p.inputs['Roughness'].default_value=rough
    if emit: p.inputs['Emission Color'].default_value=(*c,1); p.inputs['Emission Strength'].default_value=emit
    return m

def box(n,p,s,m,b=.012):
    bpy.ops.mesh.primitive_cube_add(size=1,location=p); o=bpy.context.object; o.name=n; o.dimensions=s; bpy.ops.object.transform_apply(location=False,rotation=False,scale=True); o.data.materials.append(m)
    if b:
        q=o.modifiers.new('Edge bevel','BEVEL'); q.width=b; q.segments=2; o.modifiers.new('Weighted normals','WEIGHTED_NORMAL')
    return o

def rod(n,a,b,r,m,v=24):
    a,b=Vector(a),Vector(b); d=b-a; bpy.ops.mesh.primitive_cylinder_add(vertices=v,radius=r,depth=d.length,location=(a+b)/2)
    o=bpy.context.object; o.name=n; o.rotation_euler=d.to_track_quat('Z','Y').to_euler(); o.data.materials.append(m)
    q=o.modifiers.new('Edge bevel','BEVEL'); q.width=min(.009,r*.2); q.segments=2; o.modifiers.new('Normals','WEIGHTED_NORMAL'); return o

def ellipse(n,p,rx,rz,m):
    bpy.ops.mesh.primitive_cylinder_add(vertices=64,radius=1,depth=.008,location=p,rotation=(math.pi/2,0,0))
    o=bpy.context.object; o.name=n; o.scale=(rx,rz,1); o.data.materials.append(m); return o

def text(body,p,size,m):
    bpy.ops.object.text_add(location=p,rotation=(math.pi/2,0,0)); o=bpy.context.object; o.name='Typography '+body; o.data.body=body; o.data.size=size; o.data.extrude=.0004; o.data.materials.append(m); return o

def area(n,p,target,power,size,c=(1,.93,.83)):
    bpy.ops.object.light_add(type='AREA',location=p); o=bpy.context.object; o.name=n; o.data.energy=power; o.data.size=size; o.data.color=c
    o.rotation_euler=(Vector(target)-o.location).to_track_quat('-Z','Y').to_euler()

white=mat('Gallery warm white',(.84,.83,.79)); floor=mat('Pale polished concrete',(.52,.53,.50),rough=.34); joint=mat('Concrete joints',(.25,.27,.26))
black=mat('Matte black fixtures',(.025,.029,.029),.45,.32); oak=mat('Natural oak frames',(.42,.26,.13)); paper=mat('Cotton paper',(.91,.87,.77),rough=.9)
rust=mat('Oxide red pigment',(.59,.16,.075),rough=.88); blue=mat('Ultramarine pigment',(.045,.13,.43),rough=.85); yellow=mat('Ochre pigment',(.79,.50,.11),rough=.85)
sage=mat('Sage pigment',(.29,.40,.31),rough=.85); charcoal=mat('Charcoal pigment',(.065,.07,.065),rough=.9); pink=mat('Rose pigment',(.66,.37,.31),rough=.9)
bronze=mat('Patinated bronze',(.20,.25,.19),.8,.32); seat=mat('Bench leather',(.18,.10,.055),rough=.62); luminous=mat('Track lamp lens',(1,.89,.71),emit=3)
# Open-front, roofless gallery with tall rear wall and offset partitions.
box('Gallery foundation',(0,.3,-.17),(12.6,10.4,.30),joint)
box('Polished concrete floor',(0,.3,.005),(12.4,10.2,.08),floor)
for x in [-4,-2,0,2,4]: box('Floor expansion seam',(x,.3,.048),(.012,10.1,.003),joint,0)
for y in [-3.6,-1.6,.4,2.4,4.4]: box('Floor expansion seam',(0,y,.048),(12.3,.012,.003),joint,0)
box('Rear gallery wall',(0,5.40,2.25),(12.6,.20,4.5),white)
box('West gallery wall',(-6.20,.3,2.25),(.20,10.4,4.5),white)
box('Rear recessed skirting',(0,5.282,.10),(12.3,.035,.10),joint,.002)
# Independently standing partition walls maintain clear circulation routes.
box('West freestanding partition',(-3.1,.90,1.70),(3.50,.22,3.40),white)
box('East freestanding partition',(2.8,2.00,1.70),(3.25,.22,3.40),white)
for x,y,w in [(-3.1,.90,3.50),(2.8,2.00,3.25)]: box('Partition shadow plinth',(x,y,.095),(w-.10,.16,.10),joint)
# Every work has a separate frame, mount board and original geometric composition.
def artwork(cx,y,cz,w,h,style,number):
    # y is the painted surface; artwork faces toward negative Y.
    frame=oak if number%2 else black
    box('Artwork backing',(cx,y+.045,cz),(w,.055,h),frame)
    box('Paper mat',(cx,y+.009,cz),(w-.09,.018,h-.09),paper,.002)
    for xx in [cx-w/2+.022,cx+w/2-.022]: box('Vertical frame rail',(xx,y-.02,cz),(.044,.10,h),frame,.005)
    for zz in [cz-h/2+.022,cz+h/2-.022]: box('Horizontal frame rail',(cx,y-.02,zz),(w,.10,.044),frame,.005)
    iw=w-.30; ih=h-.30
    box('Artwork painted field',(cx,y-.008,cz),(iw,.010,ih),white if style==1 else paper,.001)
    if style==0:
        ellipse('Composition sun',(cx-iw*.17,y-.022,cz+ih*.18),iw*.24,ih*.24,rust)
        box('Composition dark block',(cx+iw*.19,y-.033,cz-ih*.12),(iw*.30,.009,ih*.58),blue,.002)
        box('Composition ochre bar',(cx-iw*.12,y-.046,cz-ih*.29),(iw*.67,.009,ih*.08),yellow,.002)
        ellipse('Composition pale circle',(cx+iw*.16,y-.048,cz+ih*.13),iw*.12,ih*.13,pink)
    elif style==1:
        for i in range(7):
            xx=cx-iw*.42+i*iw*.14; height=ih*(.35+.48*(.5+.5*math.sin(i*.9+number)))
            box('Color study vertical',(xx,y-.025,cz-ih*.4+height/2),(iw*.095,.013,height),[blue,sage,rust,yellow,pink,charcoal,sage][i],.002)
        box('Color study baseline',(cx,y-.041,cz-ih*.39),(iw*.90,.009,.018),charcoal,.001)
    else:
        for i in range(5):
            zz=cz-ih*.36+i*ih*.175
            box('Abstract landscape stratum',(cx,y-.020-i*.002,zz),(iw*.92,.009,ih*.13),[blue,sage,pink,yellow,paper][i],.001)
        ellipse('Landscape sun',(cx+iw*.24,y-.047,cz+ih*.25),iw*.12,iw*.12,rust)
        box('Landscape foreground',(cx-iw*.20,y-.05,cz-ih*.27),(iw*.45,.008,ih*.10),charcoal,.001)
    lx=cx+w/2+.10
    box('Artwork caption card',(lx+.115,y+.01,cz-h/2+.095),(.25,.018,.16),paper,.002)
    text('%02d'%number,(lx+.014,y-.007,cz-h/2+.11),.047,charcoal)
    for j in range(3): box('Caption text line',(lx+.125,y-.006,cz-h/2+.08-j*.022),(.19-j*.024,.003,.005),joint,0)

artwork(-4.25,5.265,2.42,1.65,2.05,0,1)
artwork(-1.32,5.265,2.42,1.85,1.50,2,2)
artwork(1.60,5.265,2.42,1.48,1.93,1,3)
artwork(4.35,5.265,2.42,1.43,1.80,0,4)
artwork(-3.10,.762,1.98,1.80,2.15,1,5)
artwork(2.80,1.862,1.98,1.86,1.85,2,6)
# Exhibition title on a short entrance wall.
box('Entrance title wall',(-5.1,-3.35,1.47),(2.05,.19,2.94),white)
text('FORM',(-5.95,-3.46,2.33),.30,charcoal)
text('& FIELD',(-5.95,-3.46,1.95),.24,charcoal)
text('STUDIES IN COLOR',(-5.95,-3.46,1.55),.10,charcoal)
text('01 / 06',(-5.95,-3.46,.84),.11,charcoal)
# Gallery benches.
for x,y in [(-1.65,-1.7),(2.95,-1.1)]:
    box('Bench upholstered cushion',(x,y,.57),(2.25,.67,.15),seat,.07)
    box('Bench oak rail',(x,y,.46),(2.13,.55,.08),oak)
    for xx in [x-.83,x+.83]:
        for yy in [y-.20,y+.20]: rod('Bench slender leg',(xx,yy,.08),(xx,yy,.43),.028,black)
# Sculptural focal point on a white plinth.
box('Sculpture pedestal',(.30,-3.10,.61),(1.15,1.05,1.12),white)
# Twisted elliptical bronze ribbon, a closed strip with real thickness.
verts=[]; faces=[]; N=112
for i in range(N):
    t=math.tau*i/N
    center=Vector((.30+.53*math.cos(t),-3.10+.17*math.sin(2*t),1.94+.72*math.sin(t)))
    width=Vector((math.cos(t)*math.cos(t/2),math.sin(t/2),math.sin(t)*math.cos(t/2)))
    for sign in [-1,1]: verts.append(tuple(center+width*.15*sign))
for i in range(N):
    j=(i+1)%N
    if j: faces.append((2*i,2*j,2*j+1,2*i+1))
    else: faces.append((2*i,1,0,2*i+1))
me=bpy.data.meshes.new('Twisted ribbon surface'); me.from_pydata(verts,[],faces); me.update(); o=bpy.data.objects.new('Bronze continuous ribbon sculpture',me); bpy.context.collection.objects.link(o); o.data.materials.append(bronze)
q=o.modifiers.new('Cast bronze thickness','SOLIDIFY'); q.thickness=.035
q=o.modifiers.new('Polished ribbon edges','BEVEL'); q.width=.012; q.segments=3
for p in me.polygons: p.use_smooth=True
rod('Sculpture mounting pin',(.3,-3.1,1.17),(.3,-3.1,1.31),.035,bronze)
box('Sculpture caption',(.3,-3.636,.91),(.38,.014,.17),paper,.002)
text('07  /  CONTINUUM',(.135,-3.647,.91),.031,charcoal)
# Ceiling tracks float at the omitted ceiling plane, with suspension rods.
for y in [-2.6,.15,4.10]:
    box('Ceiling lighting track',(0,y,4.38),(11.65,.07,.085),black,.009)
    for x in [-5,0,5]: rod('Track suspension',(x,y,4.41),(x,y,4.83),.012,black,12)

def spotlight(x,y,target):
    anchor=Vector((x,y,4.34)); aim=Vector(target); direction=(aim-anchor).normalized()
    rod('Track swivel stem',anchor,anchor+Vector((0,0,-.15)),.026,black)
    start=anchor+Vector((0,0,-.16)); end=start+direction*.25
    rod('Adjustable spotlight housing',start,end,.085,black,32)
    rod('Spotlight luminous lens',end,end+direction*.008,.067,luminous,32)
    bpy.ops.object.light_add(type='SPOT',location=end+direction*.015); o=bpy.context.object; o.name='Artwork spotlight'
    o.rotation_euler=direction.to_track_quat('-Z','Y').to_euler(); o.data.energy=160; o.data.color=(1,.91,.78); o.data.spot_size=math.radians(62); o.data.spot_blend=.65; o.data.shadow_soft_size=.065
for x in [-4.25,-1.32,1.60,4.35]: spotlight(x,4.10,(x,5.23,2.35))
for x,y,target in [(-3.1,-2.6,(-3.1,.75,1.9)),(2.8,.15,(2.8,1.85,1.9)),(.3,-2.6,(.3,-3.1,1.9)),(-5.1,-2.6,(-5.1,-3.46,1.8))]: spotlight(x,y,target)
area('Broad skylight',(0,1,7),(0,1,0),1700,8,(.88,.93,1))
area('Open facade fill',(3,-7,5),(0,1,1.5),1200,7,(1,.93,.82))
scene=bpy.context.scene; scene.world.color=(.22,.22,.22)
bpy.ops.object.camera_add(location=(13,-18,13)); cam=bpy.context.object; cam.rotation_euler=(Vector((0,.65,1.65))-cam.location).to_track_quat('-Z','Y').to_euler(); cam.data.type='ORTHO'; cam.data.ortho_scale=18.5; scene.camera=cam
scene.render.engine='CYCLES'; scene.cycles.samples=64; scene.render.resolution_x=1600; scene.render.resolution_y=1200; scene.render.resolution_percentage=100; scene.view_settings.view_transform='AgX'
