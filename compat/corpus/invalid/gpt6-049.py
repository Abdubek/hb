import bpy, math
from mathutils import Vector
bpy.ops.wm.read_factory_settings(use_empty=True)

def mat(name,c,metal=0,rough=.45):
    m=bpy.data.materials.new(name); m.diffuse_color=(*c,1); m.use_nodes=True; p=m.node_tree.nodes.get('Principled BSDF'); p.inputs['Base Color'].default_value=(*c,1); p.inputs['Metallic'].default_value=metal; p.inputs['Roughness'].default_value=rough; return m

def box(name,loc,dims,m,bevel=.015,rotation=0):
    bpy.ops.mesh.primitive_cube_add(size=1,location=loc); o=bpy.context.object; o.name=name; o.dimensions=dims; bpy.ops.object.transform_apply(location=False,rotation=False,scale=True); o.rotation_euler.x=rotation; o.data.materials.append(m)
    if bevel:
        b=o.modifiers.new('Edge radius','BEVEL'); b.width=bevel; b.segments=2; o.modifiers.new('Normals','WEIGHTED_NORMAL')
    return o

def beam(name,a,b,width,depth,m):
    a=Vector(a); b=Vector(b); o=box(name,(a+b)/2,(width,depth,(b-a).length),m,.012); o.rotation_euler=(b-a).to_track_quat('Z','Y').to_euler(); return o

def cable(name,points,m,r=.014):
    cu=bpy.data.curves.new(name,'CURVE'); cu.dimensions='3D'; cu.bevel_depth=r; cu.bevel_resolution=3; s=cu.splines.new('POLY'); s.points.add(len(points)-1)
    for p,co in zip(s.points,points): p.co=(*co,1)
    o=bpy.data.objects.new(name,cu); bpy.context.collection.objects.link(o); o.data.materials.append(m)

def aim(o,p): o.rotation_euler=(Vector(p)-o.location).to_track_quat('-Z','Y').to_euler()
steel=mat('Galvanized steel',(.50,.55,.58),.78,.3); frame=mat('Anodized aluminum',(.67,.71,.75),.8,.24); black=mat('Black seals and cables',(.014,.019,.025)); backing=mat('Panel backsheet',(.19,.22,.25),.15); cell=mat('Monocrystalline silicon',(.012,.044,.105),.48,.20); traces=mat('Silver cell conductors',(.30,.43,.57),.72,.28); concrete=mat('Concrete footings',(.48,.47,.42)); ground=mat('Gravel ground',(.25,.24,.20)); green=mat('Equipment green',(.14,.31,.27)); white=mat('Lettering',(.88,.90,.86))
box('Ground',(0,0,-.16),(100,100,.2),ground,.0)
box('Array gravel pad',(0,0,-.015),(9,7,.12),concrete,.06)
# Local panel coordinates: X across array, Y uphill along the tilted surface.
angle=math.radians(27); origin=Vector((0,0,1.85)); c=math.cos(angle); s=math.sin(angle)
def world(x,y,z=0): return origin+Vector((x,c*y-s*z,s*y+c*z))
def panelbox(name,x,y,z,dims,m,bevel=.008): return box(name,world(x,y,z),dims,m,bevel,angle)
# Two rows by four columns, with framed modules and individually separated cells.
w=1.12; h=2.02
for row in range(2):
    for col in range(4):
        px=(col-1.5)*1.18; py=(row-.5)*2.10
        panelbox('Module backsheet',px,py,0,(w,h,.05),backing)
        panelbox('Dark cell bed',px,py,.03,(w-.045,h-.045,.015),black)
        for sign in (-1,1):
            panelbox('Long aluminum frame',px+sign*(w/2-.014),py,.018,(.028,h,.075),frame)
            panelbox('Short aluminum frame',px,py+sign*(h/2-.014),.018,(w-.04,.028,.075),frame)
        for ix in range(6):
            for iy in range(10):
                xx=px+(ix-2.5)*.174; yy=py+(iy-4.5)*.193
                panelbox('Photovoltaic cell',xx,yy,.043,(.167,.186,.006),cell,.008)
                for off in (-.044,.044): panelbox('Cell busbar',xx+off,yy,.047,(.002,.177,.001),traces,0)
        # Fine conductor lines across the complete cell field.
        for k in range(49): panelbox('Fine silver fingers',px,py+(k-24)*.038,.047,(1.038,.0009,.0007),traces,0)
        panelbox('Rear junction box',px,py+.38,-.075,(.23,.16,.09),black,.012)
        cable('Module wiring',[world(px,py+.38,-.13),world(px+.30,py+.38,-.21),world(px+.47,py,-.20),world(px+.59,py,-.18)],black)
# Long rails support both rows below their cells.
for y in (-1.73,-.40,.40,1.73): panelbox('Continuous mounting rail',0,y,-.13,(4.88,.065,.105),steel)
for x in (-1.87,0,1.87):
    front=world(x,-1.8,-.23); rear=world(x,1.8,-.23)
    for p in (front,rear):
        box('Concrete footing',(p.x,p.y,.12),(.65,.65,.30),concrete,.04)
        box('Base plate',(p.x,p.y,.29),(.32,.30,.035),steel,.008)
        beam('Vertical support',(p.x,p.y,.31),p,.10,.10,steel)
        for dx in (-.115,.115):
            for dy in (-.105,.105):
                bpy.ops.mesh.primitive_cylinder_add(vertices=6,radius=.025,depth=.025,location=(p.x+dx,p.y+dy,.322)); bpy.context.object.name='Anchor nut'; bpy.context.object.data.materials.append(frame)
    beam('Inclined rafter',world(x,-2.05,-.22),world(x,2.05,-.22),.11,.13,steel)
    beam('Triangular diagonal',(front.x,front.y,.43),rear,.06,.06,steel)
    beam('Lower longitudinal tie',(front.x,front.y,.47),(rear.x,rear.y,.47),.07,.07,steel)
rear_y=world(0,1.8,-.23).y
beam('Rear lateral cross brace',(-1.87,rear_y,.48),world(1.87,1.8,-.25),.045,.045,steel)
beam('Rear opposite cross brace',(1.87,rear_y,.48),world(-1.87,1.8,-.25),.045,.045,steel)
for x in (-2.33,-1.77,-.59,.59,1.77,2.33):
    for y in (-1.73,1.73): panelbox('Rail clamp',x,y,.075,(.06,.075,.025),frame,.005)
box('Inverter mounting post',(3.15,.8,.8),(.10,.10,1.5),steel)
box('Inverter footing',(3.15,.8,.1),(.55,.55,.23),concrete)
box('Weatherproof inverter',(3.15,.72,1.16),(.62,.30,.82),white,.065)
box('Inverter face',(3.15,.555,1.16),(.49,.03,.65),green,.03)
box('Inverter indicator',(3.15,.531,1.34),(.19,.012,.06),black,.006)
for i in range(6): box('Cooling fin',(2.84,.65,.89+i*.09),(.045,.25,.025),steel,.005)
cable('DC conduit',[world(2.25,.45,-.20),(2.6,.7,.75),(2.6,.7,.38),(3.15,.7,.38),(3.15,.7,.75)],black,.025)
bpy.ops.object.text_add(location=(2.96,.532,1.1),rotation=(math.pi/2,0,0)); bpy.context.object.data.body='SOLAR\nDC / AC'; bpy.context.object.data.size=.078; bpy.context.object.data.materials.append(white)
bpy.ops.object.light_add(type='SUN',location=(-4,-5,9)); bpy.context.object.data.energy=2.5; bpy.context.object.rotation_euler=(.4,-.5,-.4); bpy.context.object.data.angle=.10
bpy.ops.object.light_add(type='AREA',location=(1,-4,8)); bpy.context.object.data.energy=900; bpy.context.object.data.size=7; aim(bpy.context.object,(0,0,1))
bpy.ops.object.camera_add(location=(8,-10,6)); camera=bpy.context.object; aim(camera,(.2,0,1.25)); camera.data.type='ORTHO'; camera.data.ortho_scale=10.3
scene=bpy.context.scene; scene.camera=camera; scene.render.engine='CYCLES'; scene.cycles.samples=64; scene.world.color=(.25,.25,.25); scene.render.resolution_x=1600; scene.render.resolution_y=1200; scene.render.resolution_percentage=100
