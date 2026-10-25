import bpy, math
from mathutils import Vector
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)

def mat(name,c,metal=0,rough=.4):
    m=bpy.data.materials.new(name); m.diffuse_color=(*c,1); m.use_nodes=True; p=m.node_tree.nodes.get('Principled BSDF'); p.inputs['Base Color'].default_value=(*c,1); p.inputs['Metallic'].default_value=metal; p.inputs['Roughness'].default_value=rough; return m

def box(name,loc,size,m,bevel=.04):
    bpy.ops.mesh.primitive_cube_add(size=1,location=loc); o=bpy.context.object; o.name=name; o.dimensions=size; bpy.ops.object.transform_apply(location=False,rotation=False,scale=True)
    if m: o.data.materials.append(m)
    if bevel:
        q=o.modifiers.new('Rounded edges','BEVEL'); q.width=bevel; q.segments=5
        o.modifiers.new('Weighted normals','WEIGHTED_NORMAL')
    return o

def cyl(name,a,b,r,m,vertices=64):
    a,b=Vector(a),Vector(b); d=b-a; bpy.ops.mesh.primitive_cylinder_add(vertices=vertices,radius=r,depth=d.length,location=(a+b)/2); o=bpy.context.object; o.name=name; o.rotation_euler=d.to_track_quat('Z','Y').to_euler(); o.data.materials.append(m)
    q=o.modifiers.new('Edge radius','BEVEL'); q.width=.012; q.segments=3; o.modifiers.new('Weighted normals','WEIGHTED_NORMAL')
    for p in o.data.polygons: p.use_smooth=len(p.vertices)==4
    return o

def apply_all(o):
    bpy.context.view_layer.objects.active=o
    for q in list(o.modifiers): bpy.ops.object.modifier_apply(modifier=q.name)

def cut(o,tool):
    bpy.context.view_layer.objects.active=o; q=o.modifiers.new('Open slot','BOOLEAN'); q.operation='DIFFERENCE'; q.solver='EXACT'; q.object=tool; bpy.ops.object.modifier_apply(modifier=q.name); bpy.data.objects.remove(tool,do_unlink=True)

def path(name,pts,r,m):
    c=bpy.data.curves.new(name,'CURVE'); c.dimensions='3D'; c.bevel_depth=r; c.bevel_resolution=4; s=c.splines.new('BEZIER'); s.bezier_points.add(len(pts)-1)
    for p,co in zip(s.bezier_points,pts): p.co=co; p.handle_left_type='AUTO'; p.handle_right_type='AUTO'
    o=bpy.data.objects.new(name,c); bpy.context.collection.objects.link(o); o.data.materials.append(m)

def text_side(body,loc,size,m):
    c=bpy.data.curves.new(body,'FONT'); c.body=body; c.align_x='CENTER'; c.size=size; c.extrude=.0005
    o=bpy.data.objects.new(body,c); bpy.context.collection.objects.link(o); o.location=loc; o.rotation_euler=(math.pi/2,0,math.pi/2); o.data.materials.append(m)

steel=mat('Satin stainless steel',(.62,.67,.70),.87,.3)
chrome=mat('Polished trim',(.76,.8,.84),.95,.17)
dark=mat('Black polymer',(.023,.029,.034),.05,.42)
inside=mat('Dark slot interior',(.018,.015,.014),.25,.65)
wire=mat('Nichrome',(.23,.18,.15),.7,.48)
cream=mat('Warm ivory enamel',(.79,.75,.63),.25,.28)
blue=mat('Button light',(.10,.55,.75),.15,.22)
box('Lower plinth',(0,0,.22),(3.24,1.96,.26),dark,.13)
for x in (-1.14,1.14):
    for y in (-.66,.66): cyl('Rubber foot',(x,y,.03),(x,y,.14),.13,dark)
body=box('Rounded toaster shell',(0,0,1.13),(3.32,2.02,1.72),cream,.28); apply_all(body)
top=box('Stainless top cap',(0,0,1.98),(3.15,1.91,.13),steel,.10); apply_all(top)
# Real deep openings cut through the top and shell; each contains a recessed carriage.
for y in (-.47,.47):
    tool=box('Slot cutting solid',(0,y,1.77),(2.55,.40,1.10),None,.16); apply_all(tool); cut(body,tool)
    tool=box('Top aperture cutting solid',(0,y,2.01),(2.55,.40,.5),None,.16); apply_all(tool); cut(top,tool)
    rim=box('Raised slot rim',(0,y,2.06),(2.71,.56,.055),chrome,.20); apply_all(rim)
    tool=box('Rim aperture cutting solid',(0,y,2.06),(2.55,.40,.35),None,.16); apply_all(tool); cut(rim,tool)
    box('Slot well floor',(0,y,1.26),(2.43,.35,.06),inside,.03)
    for side in (-1,1):
        box('Inner mica wall',(0,y+side*.184,1.64),(2.32,.015,.69),inside,.01)
        # Fine serpentine heater, recessed below the top edge.
        pts=[]
        for j in range(27): pts.append((-1.07+j*.082,y+side*.171,1.40+(.42 if j%2 else 0)))
        path('Recessed heater wire',pts,.006,wire)
        cyl('Bread guide rail',(-1.11,y+side*.126,1.86),(1.11,y+side*.126,1.86),.014,steel)
        for x in (-.93,-.62,-.31,0,.31,.62,.93): cyl('Bread cage upright',(x,y+side*.13,1.37),(x,y+side*.13,1.87),.009,steel,16)
    box('Bread lifting carriage',(0,y,1.39),(2.20,.25,.035),steel,.015)
# Controls occupy the positive X end, visible from the camera.
box('Control panel',(1.658,0,1.14),(.035,1.49,1.30),steel,.09)
box('Lever travel recess',(1.686,.37,1.40),(.022,.10,.74),dark,.045)
cyl('Lever stem',(1.69,.37,1.67),(1.87,.37,1.67),.034,chrome)
box('Lever paddle',(1.93,.37,1.67),(.22,.39,.12),dark,.055)
cyl('Browning dial bezel',(1.68,-.21,.93),(1.75,-.21,.93),.28,chrome)
cyl('Browning dial',(1.75,-.21,.93),(1.87,-.21,.93),.231,dark)
for i in range(32):
    a=2*math.pi*i/32; cyl('Dial grip flute',(1.77,-.21+.231*math.sin(a),.93+.231*math.cos(a)),(1.855,-.21+.231*math.sin(a),.93+.231*math.cos(a)),.008,steel,12)
box('Dial pointer',(1.883,-.21,1.089),(.009,.022,.065),cream,.005)
for i in range(6):
    a=math.radians(-125+i*50); y=-.21+.34*math.sin(a); z=.93+.34*math.cos(a)
    text_side(str(i+1),(1.69,y,z-.026),.064,dark)
for y,label in [(-.48,'DEFROST'),(.13,'CANCEL')]:
    cyl(label+' button bezel',(1.68,y,.49),(1.71,y,.49),.106,chrome)
    cyl(label+' button',(1.71,y,.49),(1.755,y,.49),.082,dark)
    cyl(label+' indicator',(1.758,y,.50),(1.762,y,.50),.020,blue,24)
    text_side(label,(1.691,y,.31),.049,dark)
# Front crumb tray seam and a shallow pull.
box('Crumb tray front',(0,-1.004,.39),(2.73,.026,.17),steel,.028)
box('Crumb tray pull',(0,-1.048,.38),(.60,.085,.07),dark,.027)
for x in (-1.3,1.3): cyl('Shell fastener',(x,-1.01,.57),(x,-1.025,.57),.026,chrome,24)
path('Power cord',[(-1.46,.88,.35),(-1.96,1.14,.16),(-2.29,1.44,.065),(-1.85,1.90,.065),(-.81,1.86,.065)],.033,dark)
box('Power plug',(-.67,1.86,.075),(.29,.19,.13),dark,.05)
for y in (1.81,1.91): cyl('Plug prong',(-.52,y,.075),(-.36,y,.075),.016,chrome,16)

floor=mat('Warm studio surface',(.30,.32,.34),0,.8); box('Ground',(0,0,-.055),(200,200,.1),floor,0)
scene=bpy.context.scene; scene.world.use_nodes=True; scene.world.node_tree.nodes['Background'].inputs[0].default_value=(.28,.32,.38,1); scene.world.node_tree.nodes['Background'].inputs[1].default_value=.4
for loc,power,size in [((1,-4,7),850,5),((-4,0,5),700,4),((3,4,5),1000,3)]:
    bpy.ops.object.light_add(type='AREA',location=loc); o=bpy.context.object; o.data.energy=power; o.data.size=size; o.rotation_euler=(Vector((0,0,1))-o.location).to_track_quat('-Z','Y').to_euler()
bpy.ops.object.camera_add(location=(6,-7,5.4)); cam=bpy.context.object; cam.rotation_euler=(Vector((-.1,.15,1.02))-cam.location).to_track_quat('-Z','Y').to_euler(); cam.data.type='ORTHO'; cam.data.ortho_scale=5.7; scene.camera=cam
scene.render.engine='CYCLES'; scene.render.resolution_x=1400; scene.render.resolution_y=1100; scene.render.resolution_percentage=100
