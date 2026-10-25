import bpy, math, random
from mathutils import Vector
random.seed(134)
bpy.ops.wm.read_factory_settings(use_empty=True)

def mat(name,c,rough=.5,metal=0):
    m=bpy.data.materials.new(name); m.diffuse_color=(*c,1); m.use_nodes=True; p=m.node_tree.nodes.get('Principled BSDF'); p.inputs['Base Color'].default_value=(*c,1); p.inputs['Roughness'].default_value=rough; p.inputs['Metallic'].default_value=metal; return m

def box(name,loc,size,m,b=.025):
    bpy.ops.mesh.primitive_cube_add(size=1,location=loc); o=bpy.context.object; o.name=name; o.dimensions=size; bpy.ops.object.transform_apply(location=False,rotation=False,scale=True); o.data.materials.append(m)
    if b:
        q=o.modifiers.new('Edge softening','BEVEL'); q.width=b; q.segments=3; o.modifiers.new('Weighted normals','WEIGHTED_NORMAL')
    return o

def cyl(name,loc,r,d,m):
    bpy.ops.mesh.primitive_cylinder_add(vertices=32,radius=r,depth=d,location=loc); o=bpy.context.object; o.name=name; o.data.materials.append(m); q=o.modifiers.new('Bevel','BEVEL'); q.width=.009; q.segments=2; o.modifiers.new('Weighted normals','WEIGHTED_NORMAL'); return o

def ellipsoid(name,loc,scale,m):
    bpy.ops.mesh.primitive_uv_sphere_add(segments=24,ring_count=12,location=loc); o=bpy.context.object; o.name=name; o.scale=scale; o.data.materials.append(m)
    for p in o.data.polygons: p.use_smooth=True
    return o

def rod(name,a,b,r,m):
    d=Vector(b)-Vector(a); o=cyl(name,(Vector(a)+Vector(b))/2,r,d.length,m); o.rotation_euler=d.to_track_quat('Z','Y').to_euler(); return o

def text(body,loc,size,m):
    bpy.ops.object.text_add(location=loc,rotation=(math.pi/2,0,0)); o=bpy.context.object; o.name=body; o.data.body=body; o.data.align_x='CENTER'; o.data.size=size; o.data.extrude=.002; o.data.materials.append(m)

def area(name,loc,power,color,size,target):
    bpy.ops.object.light_add(type='AREA',location=loc); o=bpy.context.object; o.name=name; o.data.energy=power; o.data.color=color; o.data.shape='DISK'; o.data.size=size; o.rotation_euler=(Vector(target)-o.location).to_track_quat('-Z','Y').to_euler()

wall=mat('Bone plaster',(.81,.79,.73)); concrete=mat('Polished concrete',(.43,.45,.44),.4); oak=mat('Natural oak',(.54,.36,.19)); dark=mat('Charcoal metal',(.025,.036,.042),.35,.65); cream=mat('Rubber sole',(.88,.86,.77),.7); black=mat('Black outsole',(.025,.03,.032),.85); suede=mat('Tan suede',(.48,.27,.13),.93); navy=mat('Navy textile',(.055,.13,.19),.9); coral=mat('Terracotta leather',(.55,.19,.115),.52); white=mat('White leather',(.82,.83,.79),.4); lining=mat('Dark shoe lining',(.035,.04,.045),1); brass=mat('Brushed brass',(.57,.39,.16),.26,.8); sage=mat('Bench upholstery',(.3,.4,.33),.92); mirror=mat('Silver mirror',(.94,.97,1),.015,1)
box('Shop floor',(0,0,-.13),(8,6.8,.26),concrete)
for x in [-2,0,2]: box('Floor expansion joint',(x,0,.003),(.012,6.7,.006),dark,.001)
box('Rear wall',(0,3.34,1.8),(8,.16,3.6),wall)
box('Left wall',(-3.94,0,1.8),(.16,6.7,3.6),wall)
box('Rear skirting',(0,3.23,.09),(7.85,.065,.16),oak)
# Sculpted, layered sneakers in local coordinates; toes point forward (-Y).
def shoe(x,y,z,material,angle=0,scale=1):
    root=bpy.data.objects.new('Sneaker display',None); bpy.context.collection.objects.link(root); before=set(bpy.context.scene.objects)
    # Custom lofted outsole gives a flattened footprint rather than a sphere.
    rings=[(.005,.9),(.024,1),(.055,.99),(.073,.94)]; verts=[]; faces=[]; n=32
    for zz,f in rings:
        for i in range(n):
            a=i*math.tau/n; yy=.22*math.cos(a); width=.085 if yy>0 else .105; verts.append((math.sin(a)*width*f,yy*f,zz))
    for j in range(len(rings)-1):
        for i in range(n): k=j*n+i; kn=j*n+(i+1)%n; faces.append((k,kn,kn+n,k+n))
    faces.append(tuple(reversed(range(n)))); faces.append(tuple((len(rings)-1)*n+i for i in range(n)))
    mesh=bpy.data.meshes.new('Sole loft'); mesh.from_pydata(verts,[],faces); mesh.update(); o=bpy.data.objects.new('Layered rubber sole',mesh); bpy.context.collection.objects.link(o); o.data.materials.append(cream); q=o.modifiers.new('Sole bevel','BEVEL'); q.width=.004; q.segments=2; o.modifiers.new('Sole normals','WEIGHTED_NORMAL')
    ellipsoid('Toe upper',(0,-.09,.094),(.094,.125,.06),material)
    ellipsoid('Heel upper',(0,.102,.127),(.079,.098,.099),material)
    ellipsoid('Vamp',(0,-.003,.135),(.079,.135,.07),material)
    ellipsoid('Ankle opening',(0,.12,.204),(.051,.056,.009),lining)
    box('Tongue',(0,.015,.199),(.077,.105,.018),material,.014)
    for i in range(4):
        yy=-.05+i*.027; zz=.172+i*.008
        rod('Lace',(-.037,yy,zz),(.037,yy+.018,zz+.003),.0038,cream)
        rod('Lace',(.037,yy,zz),(-.037,yy+.018,zz+.003),.0038,cream)
    for xx in [-.087,.087]:
        for i in range(3): rod('Side stripe',(xx,-.04+i*.027,.09),(xx,.001+i*.027,.155),.006,cream)
    for yy in [-.15,-.08,0,.08,.15]: box('Sole tread',(0,yy,.006),(.13,.018,.012),black,.003)
    box('Heel pull tab',(0,.187,.213),(.025,.018,.045),material,.005)
    for o in set(bpy.context.scene.objects)-before: o.parent=root
    root.location=(x,y,z); root.rotation_euler.z=angle; root.scale=(scale,scale,scale)
# Rear shelving: metal standards and oak planks
for x in [-3.35,-1.85,-.35,1.15]: box('Shelf standard',(x,3.19,1.6),(.045,.06,2.65),dark,.008)
for z in [.65,1.2,1.75,2.3]:
    box('Floating display shelf',(-1.1,2.99,z),(4.8,.48,.055),oak,.014)
    for x in [-3.35,-1.85,-.35,1.15]: box('Shelf bracket',(x,3.015,z-.085),(.03,.35,.12),dark,.006)
    for i,x in enumerate([-3.0,-2.2,-1.4,-.6,.2,.9]):
        shoe(x,2.96,z+.03,[white,navy,suede,coral][(i+int(z*10))%4],-.25)
        box('Shelf price card',(x,2.735,z+.057),(.15,.015,.068),cream,.004)
text('STRIDE',(-1.15,3.245,2.95),.43,dark)
text('EVERYDAY / WELL MADE',(-1.15,3.243,2.69),.095,dark)
# Left wall short display shelves, with shoes turned into the room
for y in [-1.9,-.65,.6,1.85]:
    box('Side display backing',(-3.82,y,1.67),(.06,.94,2.3),oak)
    for z in [.85,1.5,2.15]:
        box('Side floating shelf',(-3.64,y,z),(.4,.86,.05),wall)
        shoe(-3.6,y,z+.027,random.choice([navy,suede,coral,white]),math.pi/2)
# Full height mirror beside checkout
box('Mirror brass frame',(2.65,3.205,1.67),(1.38,.1,2.8),brass,.035)
box('Full length mirror',(2.65,3.14,1.67),(1.26,.025,2.68),mirror,.012)
# Display islands, staggered heights
for x,y,w,d,h in [(-.9,-.4,1.7,1.02,.64),(1.2,-.6,1.48,1.02,.85)]:
    box('Island recessed toe kick',(x,y,.075),(w-.17,d-.17,.15),dark)
    box('Display island',(x,y,h/2+.1),(w,d,h),wall,.055)
    box('Island oak top',(x,y,h+.13),(w+.03,d+.03,.07),oak,.026)
    for dx in [-.38,.34]:
        shoe(x+dx,y,h+.167,coral if x<0 else white,.22,1.12)
        shoe(x+dx+.2,y,h+.167,coral if x<0 else white,.22,1.12)
# Fitting bench with metal base
box('Fitting bench cushion',(-1.65,-2.5,.51),(2.0,.65,.17),sage,.09)
for x in [-2.43,-.87]:
    box('Bench leg',(x,-2.5,.24),(.055,.49,.44),dark)
box('Bench underframe',(-1.65,-2.5,.38),(1.75,.06,.08),dark)
# Checkout desk on right, keeping an approach aisle clear
box('Checkout desk',(2.76,1.22,.54),(1.72,1.0,1.08),oak,.055)
box('Checkout stone top',(2.76,1.22,1.12),(1.8,1.08,.1),wall)
box('Checkout accent panel',(2.76,.706,.63),(1.38,.025,.62),sage)
text('STRIDE',(2.76,.681,.58),.17,cream)
cyl('POS stand',(2.72,1.18,1.27),.045,.23,dark)
box('POS monitor',(2.72,1.2,1.47),(.48,.07,.32),dark)
box('POS screen',(2.72,1.156,1.47),(.42,.012,.26),navy,.006)
for i in range(3):
    box('Shoe box',(3.2,1.36,1.23+i*.125),(.42,.29,.115),cream,.009)
    box('Shoe box label',(3.2,1.21,1.23+i*.125),(.16,.008,.043),sage,.002)
# Track lighting, roof omitted for cutaway view
for x in [-2.4,1.4]:
    box('Ceiling lighting track',(x,0,3.52),(.065,5.6,.065),dark,.008)
    for y in [-2,0,2]:
        cyl('Track spotlight housing',(x,y,3.4),.085,.2,dark)
        area('Display downlight',(x,y,3.28),110,(1,.87,.7),.65,(x,y,.6))
area('Shopfront daylight',(1,-4,5),1100,(.84,.91,1),5,(0,.5,0)); area('Ceiling fill',(-1,1,5),650,(1,.92,.79),4,(0,0,0))
bpy.ops.object.camera_add(location=(10,-12,8.7)); cam=bpy.context.object; cam.rotation_euler=(Vector((0,.25,1.2))-cam.location).to_track_quat('-Z','Y').to_euler(); cam.data.type='ORTHO'; cam.data.ortho_scale=11.2
s=bpy.context.scene; s.camera=cam; s.render.engine='CYCLES'; s.world.color=(.22,.22,.22); s.render.resolution_x=1500; s.render.resolution_y=1200; s.render.resolution_percentage=100
