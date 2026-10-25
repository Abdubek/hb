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
        mod=o.modifiers.new('Edge fillets','BEVEL'); mod.width=bevel; mod.segments=3; o.modifiers.new('Weighted normals','WEIGHTED_NORMAL')
    return o

def mesh(name,verts,faces,m):
    data=bpy.data.meshes.new(name); data.from_pydata(verts,[],faces); data.update(); o=bpy.data.objects.new(name,data); bpy.context.collection.objects.link(o); o.data.materials.append(m); return o

def cyl(name,loc,r,depth,m,vertices=96):
    bpy.ops.mesh.primitive_cylinder_add(vertices=vertices,radius=r,depth=depth,location=loc); o=bpy.context.object; o.name=name; o.data.materials.append(m)
    mod=o.modifiers.new('Machined edge','BEVEL'); mod.width=.025; mod.segments=2; o.modifiers.new('Weighted normals','WEIGHTED_NORMAL'); return o

def rod(name,a,b,r,m,vertices=20):
    a,b=Vector(a),Vector(b); d=b-a
    o=cyl(name,(a+b)/2,r,d.length,m,vertices); o.rotation_euler=d.to_track_quat('Z','Y').to_euler(); return o

def curve(name,points,r,m):
    data=bpy.data.curves.new(name,'CURVE'); data.dimensions='3D'; data.resolution_u=1; data.bevel_depth=r; data.bevel_resolution=3
    s=data.splines.new('POLY'); s.points.add(len(points)-1)
    for p,co in zip(s.points,points): p.co=(*co,1)
    o=bpy.data.objects.new(name,data); bpy.context.collection.objects.link(o); o.data.materials.append(m); return o

def aim(o,p): o.rotation_euler=(Vector(p)-o.location).to_track_quat('-Z','Y').to_euler()
def area(name,loc,power,size,target,color=(1,1,1)):
    bpy.ops.object.light_add(type='AREA',location=loc); o=bpy.context.object; o.name=name; o.data.energy=power; o.data.size=size; o.data.color=color; aim(o,target)

white=mat('Pearl white dome panels',(.79,.83,.84),.3,.42); concrete=mat('Circular board formed concrete',(.43,.47,.47)); metal=mat('Dark anodized aluminum',(.065,.1,.12),.28,.8)
steel=mat('Stainless tracks',(.48,.56,.59),.22,.85); glass=mat('Blue observation glazing',(.09,.24,.3),.17,.4); ground=mat('Rocky landscape',(.23,.27,.24))
paving=mat('Terrace stone',(.52,.56,.54)); blue=mat('Telescope enamel',(.055,.22,.32),.25,.5); black=mat('Optical interior',(.012,.019,.024),.3)
optic=mat('Objective glass',(.12,.36,.43),.08,.65); brass=mat('Instrument brass',(.63,.41,.14),.26,.75)
glow=mat('Recessed warm lights',(.95,.78,.48)); p=glow.node_tree.nodes.get('Principled BSDF'); p.inputs['Emission Color'].default_value=(1,.7,.35,1); p.inputs['Emission Strength'].default_value=3

cyl('Landscape plinth',(0,0,-.32),9.2,.55,ground,128)
cyl('Circular terrace',(0,0,.015),6.55,.18,paving,128)
cyl('Foundation ring',(0,0,.28),4.75,.4,concrete,128)
cyl('Observatory floor',(0,0,.5),4.46,.15,metal,128)
# Ring wall assembled as arc solids leaves an actual entrance facing -Y.
def arcwall(name,r1,r2,z1,z2,a1,a2,m,n=64):
    verts=[]
    for z in (z1,z2):
        for r in (r1,r2):
            for i in range(n+1):
                a=a1+(a2-a1)*i/n; verts.append((r*math.cos(a),r*math.sin(a),z))
    q=n+1; faces=[]
    for i in range(n):
        faces.extend([(i,i+1,q+i+1,q+i),(2*q+i,3*q+i,3*q+i+1,2*q+i+1),(i,2*q+i,2*q+i+1,i+1),(q+i,q+i+1,3*q+i+1,3*q+i)])
    faces.extend([(0,q,3*q,2*q),(n,2*q+n,3*q+n,q+n)])
    return mesh(name,verts,faces,m)
entry=math.radians(14); start=-math.pi/2+entry; end=3*math.pi/2-entry
arcwall('Circular concrete base wall',4.18,4.5,.48,2.25,start,end,concrete,112)
arcwall('Continuous head ring',4.18,4.5,2.25,2.92,0,math.tau,concrete,128)
# A narrow ribbon of inset facade glazing sits above the main wall.
arcwall('Dark ribbon window backing',4.49,4.515,2.34,2.65,0,math.tau,metal,128)
for i in range(48):
    a=i*math.tau/48
    arcwall('Ribbon glazing panel',4.516,4.54,2.37,2.62,a+.012,a+math.tau/48-.012,glass,3)
    if i%2==0:
        x,y=4.505*math.cos(a),4.505*math.sin(a)
        rod('Concrete facade joint',(x,y,.58),(x,y,2.23),.009,metal,8)
for x in (-1.05,1.05): box('Entrance jamb',(x,-4.27,1.4),(.11,.22,1.82),metal,.015)
box('Entrance lintel',(0,-4.27,2.26),(2.2,.24,.13),metal,.015)
for x in (-.51,.51):
    box('Entry door glazing',(x,-4.24,1.41),(.97,.07,1.68),glass,.015)
    for dx in (-.49,.49): box('Entry door frame',(x+dx,-4.29,1.41),(.045,.08,1.75),metal)
    rod('Entry pull handle',(x*.35,-4.35,1.15),(x*.35,-4.35,1.65),.018,steel)
for i in range(3): box('Approach step',(0,-5.55+i*.4,.08*(i+1)),(2.8,.42,.16*(i+1)),paving,.025)
box('Door landing',(0,-4.49,.26),(2.8,.55,.52),paving,.025)

# A true hemispherical shell with a constant-width meridional observing slot.
# The missing strip |Y| < slot is open from +X over the crown to -X.
# Parametrizing each half by Y produces smooth, parallel slit edges.
R=4.43; base=2.95; thickness=.105; slot=.47
for side in (-1,1):
    # Surface bands run from each slit lip toward the corresponding hemisphere side.
    verts=[]; bands=40; around=96
    for inner in (False,True):
        r=R-thickness if inner else R
        tmax=math.acos(slot/r)
        for j in range(bands+1):
            t=tmax*(1-j/bands)
            y=side*r*math.cos(t); rr=r*math.sin(t)
            for k in range(around+1):
                a=math.pi*k/around
                verts.append((rr*math.cos(a),y,base+rr*math.sin(a)))
    stride=around+1; layer=(bands+1)*stride; faces=[]
    for inside in range(2):
        off=inside*layer
        for j in range(bands):
            for k in range(around):
                ids=(off+j*stride+k,off+j*stride+k+1,off+(j+1)*stride+k+1,off+(j+1)*stride+k)
                faces.append(ids if (side==1)==(inside==0) else ids[::-1])
    # Thickness returns around the slot and both equatorial edges.
    for k in range(around): faces.append((k,layer+k,layer+k+1,k+1))
    for j in range(bands):
        for k in (0,around):
            a=j*stride+k; b=(j+1)*stride+k; faces.append((a,b,layer+b,layer+a))
    o=mesh('Hemisphere shell '+str(side),verts,faces,white)
    for p in o.data.polygons: p.use_smooth=True
    edge_r=math.sqrt(R*R-slot*slot)
    points=[(edge_r*math.cos(math.pi*i/96),side*slot,base+edge_r*math.sin(math.pi*i/96)) for i in range(97)]
    curve('Raised slit edge weather seal',points,.043,metal)
    points=[((edge_r+.035)*math.cos(math.pi*i/96),side*(slot+.11),base+(edge_r+.035)*math.sin(math.pi*i/96)) for i in range(97)]
    curve('Shutter guide rail',points,.033,steel)
    # Subtle longitudinal panel seams following the shell geometry.
    for j in range(1,10):
        y=side*(slot+(R-slot)*j/10); rr=math.sqrt(R*R-y*y)+.014
        curve('Dome panel seam',[(rr*math.cos(math.pi*i/64),y,base+rr*math.sin(math.pi*i/64)) for i in range(65)],.009,steel)

# Full annular rotation bearing does not obstruct the open sky slit.
arcwall('Dome rotation bearing',4.22,4.55,2.83,2.99,0,math.tau,metal,128)
for z,r in ((2.88,4.56),(3.0,4.45)):
    curve('Circular bearing rail',[(r*math.cos(i*math.tau/128),r*math.sin(i*math.tau/128),z) for i in range(129)],.025,steel)
# Retracted curved shutter parks immediately beside the slot on the far shell.
verts=[]; cols=8; rows=64
for i in range(rows+1):
    a=math.pi*i/rows
    for j in range(cols+1):
        y=.64+j*.115; rr=math.sqrt((R+.10)**2-y*y)
        verts.append((rr*math.cos(a),y,base+rr*math.sin(a)))
faces=[]
for i in range(rows):
    for j in range(cols):
        a=i*(cols+1)+j; faces.append((a,a+1,a+cols+2,a+cols+1))
o=mesh('Retracted curved observing shutter',verts,faces,white)
mod=o.modifiers.new('Shutter panel thickness','SOLIDIFY'); mod.thickness=.045
for p in o.data.polygons: p.use_smooth=True

# Telescope on an independent pier, aligned with the open +X side of the slit.
cyl('Isolated telescope pier',(0,0,1.35),.5,1.55,concrete,48)
cyl('Pier top flange',(0,0,2.16),.62,.16,steel,48)
cyl('Azimuth mount',(0,0,2.42),.4,.42,blue,48)
for y in (-.52,.52): box('Telescope fork arm',(.1,y,2.96),(.28,.2,1.1),blue,.07)
rod('Altitude bearing',(.1,-.72,3.24),(.1,.72,3.24),.19,steel,32)
direction=Vector((math.cos(math.radians(38)),0,math.sin(math.radians(38))))
center=Vector((.2,0,3.4)); rear=center-direction*1.05; front=center+direction*1.7
rod('Optical tube',rear,front,.35,blue,64)
for dist in (-.7,.5,1.65):
    c=center+direction*dist; rod('Telescope tube collar',c-direction*.055,c+direction*.055,.385,steel,64)
rod('Open dew shield',front-direction*.1,front+direction*.3,.4,blue,64)
rod('Dark aperture',front+direction*.305,front+direction*.317,.355,black,64)
rod('Recessed objective',front+direction*.32,front+direction*.327,.31,optic,64)
rod('Rear focuser',rear-direction*.22,rear,.105,metal,32)
rod('Eyepiece',rear-direction*.4,rear-direction*.22,.06,brass,24)
rod('Finder scope',center+Vector((0,-.43,.23)),center+Vector((0,-.43,.23))+direction*.7,.068,metal,24)

for i in range(12):
    a=i*math.tau/12; x,y=5.9*math.cos(a),5.9*math.sin(a)
    if y< -4.8 and abs(x)<2: continue
    cyl('Terrace bollard',(x,y,.42),.075,.7,metal,16)
    cyl('Bollard light cap',(x,y,.78),.082,.12,glow,16)
area('Interior service light',(-1.5,0,2.65),100,1.5,(0,0,1),(1,.76,.48))
area('Soft evening key',(5,-9,13),2300,8,(0,0,3),(.84,.91,1))
area('Dome rim light',(-7,5,12),1800,7,(0,0,4),(1,.83,.63))
bpy.ops.object.camera_add(location=(16,-19,13)); cam=bpy.context.object; aim(cam,(0,0,3)); cam.data.type='ORTHO'; cam.data.ortho_scale=19
scene=bpy.context.scene; scene.camera=cam; scene.render.engine='CYCLES'; scene.cycles.samples=64; scene.world.color=(.22,.25,.3)
scene.render.resolution_x=1400; scene.render.resolution_y=1400; scene.render.resolution_percentage=100; scene.view_settings.view_transform='AgX'
