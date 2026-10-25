import bpy, math
from mathutils import Vector
bpy.ops.object.select_all(action='SELECT'); bpy.ops.object.delete(use_global=False)

def mat(name,color,roughness=0.4,metallic=0,emission=0):
    m=bpy.data.materials.new(name); m.diffuse_color=(*color,1); m.use_nodes=True
    p=m.node_tree.nodes.get('Principled BSDF'); p.inputs['Base Color'].default_value=(*color,1); p.inputs['Roughness'].default_value=roughness; p.inputs['Metallic'].default_value=metallic
    p.inputs['Emission Color'].default_value=(*color,1); p.inputs['Emission Strength'].default_value=emission; return m

def box(name,loc,size,m,bevel=0.012,parent=None):
    bpy.ops.mesh.primitive_cube_add(size=1,location=loc); o=bpy.context.object; o.name=name; o.dimensions=size
    bpy.ops.object.transform_apply(location=False,rotation=False,scale=True); o.data.materials.append(m)
    if bevel:
        b=o.modifiers.new('Rounded edges','BEVEL'); b.width=bevel; b.segments=3; o.modifiers.new('Weighted normals','WEIGHTED_NORMAL')
    if parent: o.parent=parent; o.location=loc
    return o

def cyl(name,loc,r,depth,m,parent=None,rotation=(0,0,0)):
    bpy.ops.mesh.primitive_cylinder_add(vertices=32,radius=r,depth=depth,location=loc,rotation=rotation); o=bpy.context.object; o.name=name; o.data.materials.append(m)
    b=o.modifiers.new('Rounded rim','BEVEL'); b.width=0.005; b.segments=3; o.modifiers.new('Weighted normals','WEIGHTED_NORMAL')
    if parent: o.parent=parent; o.location=loc
    return o

def text(name,body,loc,size,m,parent=None,flat=False):
    bpy.ops.object.text_add(location=loc,rotation=(0,0,0) if flat else (math.pi/2,0,0)); o=bpy.context.object; o.name=name; o.data.body=body; o.data.align_x='CENTER'; o.data.size=size; o.data.extrude=0.0003; o.data.materials.append(m)
    if parent: o.parent=parent; o.location=loc
    return o

def line(name,points,r,m):
    c=bpy.data.curves.new(name,'CURVE'); c.dimensions='3D'; c.bevel_depth=r; c.bevel_resolution=3
    s=c.splines.new('POLY'); s.points.add(len(points)-1)
    for p,co in zip(s.points,points): p.co=(*co,1)
    o=bpy.data.objects.new(name,c); bpy.context.collection.objects.link(o); o.data.materials.append(m); return o

def area(loc,power,size,color,target):
    bpy.ops.object.light_add(type='AREA',location=loc); o=bpy.context.object; o.data.energy=power; o.data.size=size; o.data.color=color
    o.rotation_euler=(Vector(target)-o.location).to_track_quat('-Z','Y').to_euler()

purple=mat('Midnight purple enamel',(0.07,0.025,0.16),0.34,0.25)
black=mat('Black textured laminate',(0.012,0.016,0.025),0.62)
cyan=mat('Cyan T molding',(0.015,0.7,0.86),0.28,0.25)
pink=mat('Hot pink',(0.94,0.025,0.28),0.3)
chrome=mat('Steel',(0.48,0.56,0.63),0.23,0.85)
white=mat('White graphics',(0.86,0.94,1),0.4,0,0.4)
screen=mat('Deep blue screen',(0.006,0.012,0.05),0.26,0,0.18)
pixel=mat('Game cyan',(0.07,0.8,1),0.4,0,2.0)
gold=mat('Game gold',(1,0.61,0.03),0.4,0,1.5)
marquee=mat('Backlit marquee',(0.19,0.025,0.36),0.4,0,0.65)
floor=mat('Floor',(0.09,0.12,0.17),0.82)
box('Ground',(0,0,-0.09),(200,200,0.18),floor)
# Extruded shaped side panels: pronounced control deck and projecting marquee.
profile=[(-0.48,0.12),(0.48,0.12),(0.48,2.38),(-0.43,2.38),(-0.54,2.08),(-0.23,1.99),(-0.43,1.39),(-0.64,1.27),(-0.65,1.12),(-0.47,1.02)]
for side in [-1,1]:
    center=side*0.575; half=0.04; n=len(profile)
    verts=[(x,y,z) for x in [center-half,center+half] for y,z in profile]
    faces=[tuple(reversed(range(n))),tuple(range(n,2*n))]
    faces += [(i,(i+1)%n,(i+1)%n+n,i+n) for i in range(n)]
    mesh=bpy.data.meshes.new('Side silhouette'); mesh.from_pydata(verts,[],faces); mesh.update()
    o=bpy.data.objects.new('Shaped arcade side',mesh); bpy.context.collection.objects.link(o); o.data.materials.append(purple)
    mod=o.modifiers.new('Panel bevel','BEVEL'); mod.width=0.015; mod.segments=3; o.modifiers.new('Panel normals','WEIGHTED_NORMAL')
    x=side*0.619
    line('Continuous cyan edge trim',[(x,y,z) for y,z in profile+[profile[0]]],0.011,cyan)
    # Layered lightning motif attached to the exterior side.
    for offset,m in [(0,cyan),(0.11,pink)]:
        yz=[(0.25+offset,1.86),(-0.21+offset,1.44),(0.02+offset,1.44),(-0.25+offset,0.58),(0.28+offset,1.22),(0.06+offset,1.22)]
        me=bpy.data.meshes.new('Lightning graphic'); me.from_pydata([(side*0.622,y,z) for y,z in yz],[],[tuple(range(6))]); me.update()
        obj=bpy.data.objects.new('Side lightning artwork',me); bpy.context.collection.objects.link(obj); obj.data.materials.append(m)
box('Rear enclosure',(0,0.439,1.23),(1.09,0.075,2.2),black)
box('Base plinth',(0,0,0.14),(1.20,0.99,0.19),black)
for x in [-0.47,0.47]:
    for y in [-0.35,0.35]: cyl('Cabinet foot',(x,y,0.05),0.052,0.10,black)
box('Lower front',(0,-0.454,0.64),(1.08,0.065,0.92),purple)
box('Coin door frame',(0,-0.498,0.70),(0.48,0.035,0.52),chrome,0.023)
box('Coin access door',(0,-0.522,0.70),(0.43,0.025,0.47),black,0.018)
for x in [-0.10,0.10]:
    box('Coin acceptor',(x,-0.544,0.80),(0.12,0.03,0.15),chrome)
    box('Coin opening',(x,-0.563,0.825),(0.013,0.01,0.074),black,0.002)
    box('Coin return button',(x,-0.565,0.753),(0.073,0.017,0.030),pink,0.005)
text('Coin instruction','INSERT COIN',(0,-0.54,0.53),0.047,white)
cyl('Coin door lock',(0.155,-0.541,0.57),0.021,0.015,chrome,rotation=(math.pi/2,0,0))
# Sloped control deck, with all controls in its local coordinates.
bpy.ops.object.empty_add(type='PLAIN_AXES',location=(0,-0.38,1.24)); deck=bpy.context.object; deck.name='Sloping control assembly'; deck.rotation_euler.x=math.radians(10)
box('Control deck',(0,0,0),(1.10,0.58,0.09),black,0.02,deck)
box('Pink deck front stripe',(0,-0.278,0.048),(1.04,0.016,0.007),pink,0.003,deck)
cyl('Joystick mounting ring',(-0.30,-0.025,0.056),0.105,0.016,chrome,deck)
cyl('Joystick dust cover',(-0.30,-0.025,0.071),0.082,0.023,black,deck)
cyl('Joystick shaft',(-0.30,-0.025,0.145),0.018,0.15,chrome,deck)
bpy.ops.mesh.primitive_uv_sphere_add(segments=24,ring_count=16,radius=0.064); ball=bpy.context.object; ball.name='Red joystick ball'; ball.parent=deck; ball.location=(-0.30,-0.025,0.24); ball.data.materials.append(pink)
for p in ball.data.polygons: p.use_smooth=True
for row in range(2):
    for col in range(3):
        x=0.08+col*0.14; y=-0.10+row*0.16+col*0.025
        cyl('Action button bezel',(x,y,0.057),0.058,0.022,chrome,deck)
        cyl('Action button cap',(x,y,0.076),0.048,0.033,pink if row==0 else cyan,deck)
for x,label in [(-0.13,'1P'),(0.03,'2P')]:
    cyl('Start button',(x,0.197,0.067),0.03,0.027,white,deck)
    text('Player marking',label,(x,0.13,0.05),0.032,white,deck,True)
# Recessed tilted screen with an original geometry-built pixel shooter.
bpy.ops.object.empty_add(type='PLAIN_AXES',location=(0,-0.28,1.73)); display=bpy.context.object; display.name='Tilted display assembly'; display.rotation_euler.x=math.radians(-17)
box('Screen surround',(0,0,0),(1.09,0.13,0.72),black,0.035,display)
box('CRT outer rim',(0,-0.078,0),(0.95,0.05,0.63),chrome,0.03,display)
box('CRT dark glass',(0,-0.11,0),(0.90,0.025,0.58),screen,0.045,display)
text('Game score','SCORE 02480   HI 09800',(0,-0.128,0.222),0.039,white,display)
pattern=['0011100','0111110','1101011','1111111','0100010','1010101']
for row in range(2):
    for col in range(4):
        cx=-0.30+col*0.20; cz=0.13-row*0.135
        for iz,bits in enumerate(pattern):
            for ix,bit in enumerate(bits):
                if bit=='1': box('Alien pixel',(cx+(ix-3)*0.016,-0.13,cz-iz*0.014),(0.014,0.003,0.012),gold if row==0 else pixel,0,display)
for x in [-0.25,0,0.25]: box('Shield',(x,-0.13,-0.19),(0.09,0.003,0.025),pixel,0.002,display)
box('Player ship',(0,-0.132,-0.248),(0.09,0.004,0.022),white,0.002,display)
box('Player turret',(0,-0.132,-0.228),(0.025,0.004,0.027),white,0.001,display)
box('Laser shot',(0.02,-0.132,-0.12),(0.008,0.004,0.040),pink,0,display)
box('Marquee housing',(0,-0.055,2.225),(1.10,0.85,0.29),black,0.023)
box('Illuminated marquee',(0,-0.493,2.245),(1.045,0.026,0.217),marquee,0.012)
text('Arcade title','N E O N  R A I D',(0,-0.514,2.225),0.106,white)
box('Marquee cyan line',(0,-0.513,2.159),(0.94,0.005,0.011),cyan,0.003)
for x in [-0.39,0.39]:
    for i in range(5): box('Speaker grille',(x+(i-2)*0.025,-0.505,2.057),(0.01,0.014,0.054),chrome,0.004)
area((-3,-4,5),850,3,(0.7,0.88,1),(0,0,1.2)); area((3,-1,4),650,2.5,(1,0.65,0.8),(0,0,1.4)); area((1,3,4),1000,2,(0.4,0.7,1),(0,0,1.6))
scene=bpy.context.scene; scene.world.color=(0.12,0.12,0.16)
bpy.ops.object.camera_add(location=(3.7,-5.5,3.1)); cam=bpy.context.object; cam.rotation_euler=(Vector((0,-0.03,1.24))-cam.location).to_track_quat('-Z','Y').to_euler(); cam.data.type='ORTHO'; cam.data.ortho_scale=3.25; scene.camera=cam
scene.render.engine='CYCLES'; scene.cycles.samples=48; scene.render.resolution_x=1200; scene.render.resolution_y=1500; scene.render.resolution_percentage=100; scene.view_settings.view_transform='AgX'
