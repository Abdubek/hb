import bpy, math
from mathutils import Vector
bpy.ops.wm.read_factory_settings(use_empty=True)

def mat(name,c,metal=0,rough=.4):
    m=bpy.data.materials.new(name); m.diffuse_color=(*c,1); m.use_nodes=True; s=m.node_tree.nodes.get('Principled BSDF'); s.inputs['Base Color'].default_value=(*c,1); s.inputs['Metallic'].default_value=metal; s.inputs['Roughness'].default_value=rough; return m
ivory=mat('Warm white enamel',(.79,.83,.8),.15)
teal=mat('Cabinet teal',(.12,.36,.4),.25)
black=mat('Black polymer',(.025,.04,.05),0,.38)
stone=mat('Epoxy worktop',(.10,.15,.18),.1,.25)
steel=mat('Stainless steel',(.55,.62,.65),.85,.23)
blue=mat('Blue liquid',(.025,.34,.68),.1,.2)
orange=mat('Amber reagent',(.7,.22,.035),.15,.28)
glass=mat('Borosilicate glass',(.8,.95,.98),0,.12); bs=glass.node_tree.nodes.get('Principled BSDF'); bs.inputs['Transmission Weight'].default_value=1; bs.inputs['IOR'].default_value=1.45
screen=mat('Screen blue',(.025,.2,.3)); bs=screen.node_tree.nodes.get('Principled BSDF'); bs.inputs['Emission Color'].default_value=(.03,.5,.8,1); bs.inputs['Emission Strength'].default_value=.6

def box(name,p,d,m,bevel=.025):
    bpy.ops.mesh.primitive_cube_add(size=1,location=p); o=bpy.context.object; o.name=name; o.dimensions=d; bpy.ops.object.transform_apply(location=False,rotation=False,scale=True); o.data.materials.append(m)
    if bevel:
        b=o.modifiers.new('Rounded edges','BEVEL'); b.width=bevel; b.segments=3; o.modifiers.new('Normals','WEIGHTED_NORMAL')
    return o

def rod(name,a,b,r,m,n=32):
    a,b=Vector(a),Vector(b); d=b-a; bpy.ops.mesh.primitive_cylinder_add(vertices=n,radius=r,depth=d.length,location=(a+b)/2); o=bpy.context.object; o.name=name; o.rotation_mode='QUATERNION'; o.rotation_quaternion=d.to_track_quat('Z','Y'); o.data.materials.append(m)
    for f in o.data.polygons: f.use_smooth=len(f.vertices)==4
    return o

def path(name,pts,r,m):
    c=bpy.data.curves.new(name,'CURVE'); c.dimensions='3D'; c.bevel_depth=r; c.bevel_resolution=3; c.use_fill_caps=True; s=c.splines.new('POLY'); s.points.add(len(pts)-1)
    for p,v in zip(s.points,pts): p.co=(*v,1)
    o=bpy.data.objects.new(name,c); bpy.context.collection.objects.link(o); o.data.materials.append(m)

def label(body,p,size,m):
    c=bpy.data.curves.new('Label','FONT'); c.body=body; c.size=size; c.extrude=.0005; o=bpy.data.objects.new(body,c); bpy.context.collection.objects.link(o); o.location=p; o.rotation_euler=(math.pi/2,0,0); o.data.materials.append(m)

box('Lab floor',(0,0,-.08),(9,6,.16),mat('Floor',(.34,.4,.42),0,.8))
box('Back wall',(0,1.05,1.8),(6.8,.14,3.6),mat('Wall',(.66,.72,.7),0,.85))
box('Cabinet carcass',(0,.15,.88),(6,1.4,1.7),ivory)
box('Recessed toe kick',(0,.1,.14),(5.8,1.2,.22),black)
box('Continuous worktop',(0,.1,1.79),(6.2,1.62,.14),stone)
box('Back splash',(0,.85,1.95),(6.2,.06,.28),stone)
for x in (-2.48,-1.48,1.48,2.48):
    box('Lower cabinet door',(x,-.573,.97),(.94,.055,1.35),teal)
    path('Brushed pull',[(x+.25,-.61,1.37),(x+.25,-.69,1.37),(x+.25,-.69,1.12),(x+.25,-.61,1.12)],.017,steel)
for x in (-.5,.5):
    for z in (.49,.94,1.39):
        box('Drawer front',(x,-.58,z),(.94,.07,.4),teal)
        path('Drawer pull',[(x-.22,-.64,z+.06),(x-.22,-.71,z+.06),(x+.22,-.71,z+.06),(x+.22,-.64,z+.06)],.017,steel)
for x in (-2.05,0,2.05):
    box('Wall cabinet',(x,.72,2.96),(1.95,.52,.9),ivory)
    for dx in (-.48,.48):
        box('Upper door',(x+dx,.437,2.96),(.92,.045,.82),teal)
        rod('Upper handle',(x+dx,.375,2.77),(x+dx,.375,2.98),.017,steel)
# Microscope, with stage, objectives and an inclined eyepiece.
box('Microscope foot',(-1.95,-.04,1.94),(.58,.5,.16),ivory,.07)
path('Microscope curved arm',[(-1.76,.1,1.99),(-1.65,.13,2.18),(-1.65,.13,2.54),(-1.9,.06,2.64)],.065,ivory)
box('Microscope stage',(-1.98,-.06,2.24),(.43,.35,.045),black)
box('Glass slide',(-2,-.1,2.268),(.24,.085,.006),glass,.001)
rod('Objective turret',(-1.98,-.02,2.47),(-1.98,-.02,2.54),.12,steel)
for dx,dy in [(-.065,-.03),(.06,-.03),(0,.065)]: rod('Objective',(-1.98+dx,-.02+dy,2.48),(-1.98+dx,-.02+dy,2.34),.035,black)
rod('Optical head',(-1.97,0,2.53),(-1.97,-.16,2.82),.073,ivory)
rod('Eyepiece',(-1.97,-.15,2.8),(-1.97,-.22,2.91),.057,black)
rod('Focus knob',(-1.57,.1,2.38),(-1.72,.1,2.38),.075,black)
# Digital analytical instrument.
box('Spectrometer',(.05,.05,2.09),(1.05,.72,.47),ivory,.065)
box('Sample chamber lid',(.3,.03,2.339),(.4,.52,.045),stone)
box('Instrument display',(-.17,-.318,2.16),(.38,.015,.16),black,.009)
box('LCD',(-.17,-.328,2.16),(.32,.006,.115),screen,.004)
label('0.248',(-.30,-.334,2.13),.065,ivory)
for x in (.13,.27,.41): rod('Control button',(x,-.325,2.04),(x,-.346,2.04),.025,teal,24)
label('SPECTRA  UV',(-.43,-.329,1.96),.052,black)
# Small hotplate and an open, hollow beaker.
box('Hotplate',(1.29,-.12,1.98),(.58,.56,.24),ivory)
rod('Heating surface',(1.29,-.12,2.1),(1.29,-.12,2.13),.235,black,48)
rod('Hotplate dial',(1.44,-.41,1.99),(1.44,-.45,1.99),.045,black)
def beaker(x,y,z,r,h):
    verts=[]; faces=[]; n=48
    for radius,zz in [(r,z),(r,z+h),(r-.014,z+h),(r-.014,z+.018)]:
        verts.extend([(x+radius*math.cos(i*math.tau/n),y+radius*math.sin(i*math.tau/n),zz) for i in range(n)])
    for j in range(3):
        for i in range(n):
            k=(i+1)%n; faces.append((j*n+i,j*n+k,(j+1)*n+k,(j+1)*n+i))
    faces.extend([tuple(reversed(range(n))),tuple(range(3*n,4*n))]); me=bpy.data.meshes.new('Beaker mesh'); me.from_pydata(verts,[],faces); me.update(); o=bpy.data.objects.new('Open glass beaker',me); bpy.context.collection.objects.link(o); o.data.materials.append(glass)
    for f in me.polygons: f.use_smooth=len(f.vertices)==4
    rod('Liquid',(x,y,z+.022),(x,y,z+h*.52),r-.02,blue,48)
    for i in range(4): box('Graduation',(x+.04,y-r-.003,z+.08+i*.055),(.055,.005,.007),ivory,.001)
beaker(1.29,-.12,2.13,.165,.39)
# Test tube rack and reagent bottles.
for x in (2,2.63): box('Rack upright',(x,-.16,2),(.045,.34,.28),steel)
for y in (-.29,-.03): rod('Rack upper rail',(1.98,y,2.1),(2.65,y,2.1),.018,steel)
box('Rack bottom',(2.315,-.16,1.886),(.72,.36,.04),teal)
for i in range(5):
    x=2.07+i*.12; rod('Test tube',(x,-.16,1.93),(x,-.16,2.27),.043,glass)
    rod('Sample',(x,-.16,1.95),(x,-.16,2.08),.03,orange)
    rod('Tube cap',(x,-.16,2.26),(x,-.16,2.3),.046,teal)
for x in (-.95,-.65):
    rod('Reagent bottle',(x,.5,1.86),(x,.5,2.17),.09,orange)
    rod('Bottle cap',(x,.5,2.17),(x,.5,2.23),.065,black)
    box('Bottle label',(x,.409,2.02),(.105,.012,.12),ivory,.004)
# Adjustable laboratory stool in front of the bench.
rod('Stool cushion',(.3,-1.65,.99),(.3,-1.65,1.12),.37,black,64)
rod('Stool column',(.3,-1.65,.22),(.3,-1.65,1),.065,steel)
for i in range(5):
    a=i*math.tau/5; p=(.3+.43*math.cos(a),-1.65+.43*math.sin(a),.14); rod('Stool leg',(.3,-1.65,.3),p,.035,steel); rod('Caster',(p[0]-.055,p[1],.09),(p[0]+.055,p[1],.09),.075,black,24)
scene=bpy.context.scene; scene.world.color=(.3,.3,.3)
for loc,power,size in [((1,-4,7),1400,5),((-4,-1,5),1000,4),((3,2,6),1200,3)]:
    bpy.ops.object.light_add(type='AREA',location=loc); o=bpy.context.object; o.data.energy=power; o.data.size=size; o.rotation_euler=(Vector((0,0,1.5))-o.location).to_track_quat('-Z','Y').to_euler()
bpy.ops.object.camera_add(location=(7,-10,6.3)); o=bpy.context.object; o.rotation_euler=(Vector((0,0,1.6))-o.location).to_track_quat('-Z','Y').to_euler(); o.data.type='ORTHO'; o.data.ortho_scale=8.4; scene.camera=o
scene.render.engine='CYCLES'; scene.render.resolution_x=1500; scene.render.resolution_y=1100; scene.render.resolution_percentage=100
