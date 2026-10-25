import bpy, math
from mathutils import Vector
bpy.ops.object.select_all(action='SELECT'); bpy.ops.object.delete(use_global=False)

def mat(name,color,roughness=0.45,metallic=0,emission=0):
    m=bpy.data.materials.new(name); m.diffuse_color=(*color,1); m.use_nodes=True
    p=m.node_tree.nodes.get('Principled BSDF'); p.inputs['Base Color'].default_value=(*color,1); p.inputs['Roughness'].default_value=roughness; p.inputs['Metallic'].default_value=metallic
    p.inputs['Emission Color'].default_value=(*color,1); p.inputs['Emission Strength'].default_value=emission; return m

def box(name,loc,size,m,bevel=0.012,parent=None):
    bpy.ops.mesh.primitive_cube_add(size=1,location=loc); o=bpy.context.object; o.name=name; o.dimensions=size
    bpy.ops.object.transform_apply(location=False,rotation=False,scale=True); o.data.materials.append(m)
    if bevel:
        b=o.modifiers.new('Soft manufactured edges','BEVEL'); b.width=bevel; b.segments=3; o.modifiers.new('Weighted normals','WEIGHTED_NORMAL')
    if parent: o.parent=parent; o.location=loc
    return o

def cyl(name,loc,r,depth,m,rotation=(0,0,0),parent=None):
    bpy.ops.mesh.primitive_cylinder_add(vertices=32,radius=r,depth=depth,location=loc,rotation=rotation); o=bpy.context.object; o.name=name; o.data.materials.append(m)
    b=o.modifiers.new('Small edge bevel','BEVEL'); b.width=0.003; b.segments=2; o.modifiers.new('Weighted normals','WEIGHTED_NORMAL')
    if parent: o.parent=parent; o.location=loc
    return o

def text(name,body,loc,size,m,parent=None):
    bpy.ops.object.text_add(location=loc,rotation=(math.pi/2,0,0)); o=bpy.context.object; o.name=name; o.data.body=body; o.data.align_x='CENTER'; o.data.size=size; o.data.extrude=0.00015; o.data.materials.append(m)
    if parent: o.parent=parent; o.location=loc
    return o

def wire(name,points,r,m,parent=None):
    c=bpy.data.curves.new(name,'CURVE'); c.dimensions='3D'; c.bevel_depth=r; c.bevel_resolution=3
    s=c.splines.new('POLY'); s.points.add(len(points)-1)
    for p,co in zip(s.points,points): p.co=(*co,1)
    o=bpy.data.objects.new(name,c); bpy.context.collection.objects.link(o); o.data.materials.append(m)
    if parent: o.parent=parent
    return o

def area(loc,energy,size,color,target):
    bpy.ops.object.light_add(type='AREA',location=loc); o=bpy.context.object; o.data.energy=energy; o.data.size=size; o.data.color=color
    o.rotation_euler=(Vector(target)-o.location).to_track_quat('-Z','Y').to_euler()

ivory=mat('Powder coated shell',(0.76,0.80,0.79),0.38,0.22)
navy=mat('Deep navy panels',(0.018,0.06,0.095),0.4,0.3)
black=mat('Recess rubber',(0.009,0.015,0.021),0.6)
metal=mat('Brushed stainless steel',(0.46,0.52,0.55),0.32,0.8)
teal=mat('Transit teal',(0.015,0.46,0.49),0.35)
white=mat('White lettering',(0.9,0.97,0.98),0.4,0,0.35)
ui=mat('Screen background',(0.025,0.08,0.115),0.28,0,0.35)
button=mat('Touch target teal',(0.02,0.37,0.40),0.4,0,0.6)
muted=mat('Secondary interface',(0.15,0.25,0.30),0.5,0,0.25)
led=mat('Ready light',(0.08,0.85,0.44),0.3,0,2)
paper=mat('Ticket paper',(0.91,0.86,0.70),0.88)
ground=mat('Station floor',(0.28,0.33,0.35),0.87)
box('Ground',(0,0,-0.08),(200,200,0.16),ground)
box('Stable floor base',(0,0,0.07),(0.99,0.81,0.14),navy,0.065)
box('Base metal trim',(0,0,0.149),(0.87,0.68,0.026),metal,0.013)
box('Pedestal cabinet',(0,0.045,0.83),(0.73,0.56,1.34),ivory,0.065)
box('Front service door',(0,-0.248,0.65),(0.61,0.025,0.85),navy,0.028)
box('Vertical teal accent',(-0.294,-0.266,0.65),(0.029,0.006,0.74),teal,0.006)
cyl('Service lock',(0.235,-0.273,0.78),0.025,0.015,metal,(math.pi/2,0,0))
box('Lock keyway',(0.235,-0.283,0.78),(0.006,0.004,0.024),black,0.001)
for i in range(9): box('Pedestal side vent',(0.369,0.065,0.31+i*0.035),(0.008,0.30,0.012),black,0.004)
# Tilt the complete interaction head backward for a standing user.
bpy.ops.object.empty_add(type='PLAIN_AXES',location=(0,-0.01,1.66)); head=bpy.context.object; head.name='Angled kiosk head'; head.rotation_euler.x=math.radians(-13)
box('Head enclosure',(0,0,0),(1.05,0.31,1.12),ivory,0.062,head)
box('Head front fascia',(0,-0.168,0),(0.965,0.043,1.025),navy,0.035,head)
text('Kiosk heading','CITYLINE',(0,-0.195,0.411),0.09,white,head)
text('Kiosk subtitle','TICKETS & PASSES',(0,-0.195,0.354),0.034,white,head)
box('Touch screen gasket',(0,-0.201,0.063),(0.84,0.023,0.526),black,0.026,head)
box('Touch screen glass',(0,-0.216,0.063),(0.792,0.015,0.479),ui,0.018,head)
text('Screen greeting','Where are you going?',(0,-0.227,0.234),0.045,white,head)
text('Screen instruction','Choose your ticket',(0,-0.227,0.179),0.027,white,head)
for x,title,price in [(-0.192,'SINGLE','$2.50'),(0.192,'DAY PASS','$6.00')]:
    box('Large touch button',(x,-0.230,0.057),(0.343,0.007,0.159),button,0.016,head)
    text('Ticket type',title,(x,-0.237,0.079),0.036,white,head)
    text('Fare',price,(x,-0.237,0.021),0.045,white,head)
box('Language touch target',(-0.19,-0.230,-0.10),(0.32,0.007,0.068),muted,0.01,head)
box('Help touch target',(0.19,-0.230,-0.10),(0.32,0.007,0.068),muted,0.01,head)
text('Language label','ENGLISH',(-0.19,-0.237,-0.112),0.026,white,head)
text('Help label','HELP',(0.19,-0.237,-0.112),0.026,white,head)
# Integrated payment reader beneath the screen.
box('Card reader surround',(0.245,-0.22,-0.347),(0.30,0.065,0.245),metal,0.026,head)
box('Contactless reader body',(0.245,-0.268,-0.338),(0.255,0.07,0.203),black,0.027,head)
text('Payment label','TAP CARD',(0.245,-0.307,-0.289),0.031,white,head)
for r in [0.021,0.037,0.053]:
    pts=[]
    for i in range(25):
        a=-1.0+i*2.0/24; pts.append((0.224+r*math.cos(a),-0.31,-0.35+r*math.sin(a)))
    wire('Contactless signal arc',pts,0.0028,white,head)
box('Card slot silver lip',(0.245,-0.309,-0.411),(0.209,0.017,0.028),metal,0.006,head)
box('Card insertion opening',(0.245,-0.32,-0.411),(0.171,0.005,0.009),black,0.002,head)
box('Reader status light',(0.331,-0.309,-0.289),(0.022,0.006,0.008),led,0.003,head)
text('Receipt instructions','1  CHOOSE\n2  PAY\n3  COLLECT',(-0.222,-0.195,-0.29),0.038,white,head)
for x in [-0.427,0.427]:
    for z in [-0.448,0.448]:
        cyl('Fascia screw',(x,-0.195,z),0.009,0.009,metal,(math.pi/2,0,0),head)
# Recessed ticket printer with a projecting printed ticket and tray.
box('Printer mounting plate',(0,-0.263,1.00),(0.54,0.035,0.22),metal,0.021)
box('Printer dark recess',(0,-0.286,1.014),(0.445,0.015,0.10),black,0.013)
box('Printer exit slit',(0,-0.298,1.025),(0.367,0.012,0.022),black,0.003)
box('Printer hood',(0,-0.319,1.074),(0.47,0.095,0.032),navy,0.01)
box('Ticket catch tray',(0,-0.34,0.921),(0.49,0.19,0.035),navy,0.012)
box('Tray front lip',(0,-0.43,0.94),(0.49,0.02,0.054),navy,0.008)
# Paper descends in front of the slit; printing is visible from the camera.
ticket=box('Dispensed ticket',(0,-0.328,0.967),(0.27,0.008,0.14),paper,0.002)
text('Printed transit ticket','CITYLINE',(0,-0.334,0.993),0.027,navy)
text('Ticket fare label','SINGLE  $2.50',(0,-0.334,0.961),0.017,navy)
for i in range(31):
    w=0.002 if i%3 else 0.004
    box('Ticket barcode bar',(-0.102+i*0.0068,-0.334,0.935),(w,0.001,0.019),black,0)
text('Pickup label','COLLECT TICKET',(0,-0.274,0.83),0.037,white)
# Accessibility call button and speaker on the service panel.
cyl('Assistance button bezel',(-0.16,-0.279,0.51),0.044,0.021,metal,(math.pi/2,0,0))
cyl('Assistance button',(-0.16,-0.293,0.51),0.033,0.012,teal,(math.pi/2,0,0))
text('Assistance symbol','i',(-0.16,-0.301,0.492),0.049,white)
for r in range(4):
    for c in range(6): cyl('Speaker perforation',(0.055+c*0.023,-0.266,0.478+r*0.023),0.005,0.007,black,(math.pi/2,0,0))
area((-3,-4,5),800,3,(0.8,0.91,1),(0,0,1.2)); area((4,-1,3.5),650,3,(1,0.83,0.67),(0,0,1.3)); area((0,3,4),950,2.5,(0.63,0.86,1),(0,0,1.5))
scene=bpy.context.scene; scene.world.color=(0.18,0.18,0.18)
bpy.ops.object.camera_add(location=(3.2,-5.4,3.0)); cam=bpy.context.object; cam.rotation_euler=(Vector((0,-0.04,1.16))-cam.location).to_track_quat('-Z','Y').to_euler(); cam.data.type='ORTHO'; cam.data.ortho_scale=2.95; scene.camera=cam
scene.render.engine='CYCLES'; scene.cycles.samples=48; scene.render.resolution_x=1200; scene.render.resolution_y=1500; scene.render.resolution_percentage=100; scene.view_settings.view_transform='AgX'
