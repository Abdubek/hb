import bpy, math
from mathutils import Vector
bpy.ops.wm.read_factory_settings(use_empty=True)

def mat(name, color, metal=0, rough=.4):
    m=bpy.data.materials.new(name); m.diffuse_color=(*color,1); m.use_nodes=True
    s=m.node_tree.nodes.get('Principled BSDF'); s.inputs['Base Color'].default_value=(*color,1); s.inputs['Metallic'].default_value=metal; s.inputs['Roughness'].default_value=rough
    return m
steel=mat('Galvanized steel',(.36,.43,.46),.8)
blue=mat('Blue enamel',(.035,.19,.29),.55)
red=mat('Valve wheel red',(.62,.045,.025),.4)
dark=mat('Dark iron',(.055,.065,.072),.7)
concrete=mat('Concrete',(.24,.27,.28),0,.85)
yellow=mat('Safety yellow',(.95,.57,.035),.25)
white=mat('Gauge porcelain',(.88,.88,.79))

def cube(name,loc,scale,material,bevel=.04):
    bpy.ops.mesh.primitive_cube_add(size=1,location=loc); o=bpy.context.object; o.name=name; o.dimensions=scale; bpy.ops.object.transform_apply(location=False,rotation=False,scale=True); o.data.materials.append(material)
    if bevel:
        m=o.modifiers.new('Soft edges','BEVEL'); m.width=bevel; m.segments=3
        o.modifiers.new('Weighted normals','WEIGHTED_NORMAL')
    return o

def cyl(name,a,b,r,material,vertices=40):
    a,b=Vector(a),Vector(b); d=b-a
    bpy.ops.mesh.primitive_cylinder_add(vertices=vertices,radius=r,depth=d.length,location=(a+b)/2); o=bpy.context.object; o.name=name; o.rotation_quaternion=d.to_track_quat('Z','Y'); o.rotation_mode='QUATERNION'; o.rotation_quaternion=d.to_track_quat('Z','Y'); o.data.materials.append(material)
    for p in o.data.polygons: p.use_smooth=len(p.vertices)==4
    return o

def tube(name,pts,r,material):
    c=bpy.data.curves.new(name,'CURVE'); c.dimensions='3D'; c.bevel_depth=r; c.bevel_resolution=4; c.use_fill_caps=True
    s=c.splines.new('POLY'); s.points.add(len(pts)-1)
    for p,co in zip(s.points,pts): p.co=(*co,1)
    o=bpy.data.objects.new(name,c); bpy.context.collection.objects.link(o); o.data.materials.append(material); return o

def rounded_pipe(name,points):
    v=list(map(Vector,points)); out=[v[0]]
    for i in range(1,len(v)-1):
        a=v[i]+(v[i-1]-v[i]).normalized()*.52; b=v[i]+(v[i+1]-v[i]).normalized()*.52
        out.append(a)
        for j in range(1,17):
            t=j/16; out.append((1-t)**2*a+2*(1-t)*t*v[i]+t*t*b)
    out.append(v[-1]); tube(name,out,.18,blue)

def flange(x,y,z):
    cyl('Flange gasket',(x-.025,y,z),(x+.025,y,z),.305,dark)
    for sign in (-1,1):
        xx=x+sign*.075; cyl('Bolted flange',(xx-.045,y,z),(xx+.045,y,z),.32,steel)
    for k in range(8):
        a=k*math.tau/8; yy=y+.255*math.cos(a); zz=z+.255*math.sin(a)
        cyl('Flange stud',(x-.15,yy,zz),(x+.15,yy,zz),.027,dark,12)
        for xx in (x-.14,x+.14): cyl('Hex nut',(xx-.028,yy,zz),(xx+.028,yy,zz),.047,steel,6)

def valve(x,y,z):
    cyl('Valve barrel',(x-.28,y,z),(x+.28,y,z),.25,steel)
    cube('Gate valve housing',(x,y,z+.10),(.43,.43,.43),blue)
    cyl('Bonnet',(x,y,z+.18),(x,y,z+.43),.17,steel)
    cyl('Exposed valve stem',(x,y,z+.4),(x,y,z+.86),.046,steel)
    for k in range(8):
        zz=z+.47+k*.034
        bpy.ops.mesh.primitive_torus_add(major_radius=.047,minor_radius=.009,major_segments=20,minor_segments=6,location=(x,y,zz)); bpy.context.object.data.materials.append(dark)
    zz=z+.9
    tube('Cast handwheel rim',[(x+.36*math.cos(a*math.tau/64),y+.36*math.sin(a*math.tau/64),zz) for a in range(65)],.035,red)
    cyl('Wheel hub',(x,y,zz-.055),(x,y,zz+.055),.075,red)
    for k in range(5):
        a=k*math.tau/5; cyl('Wheel spoke',(x,y,zz),(x+.34*math.cos(a),y+.34*math.sin(a),zz),.025,red,16)
    flange(x-.46,y,z); flange(x+.46,y,z)

cube('Concrete equipment plinth',(0,0,.08),(8.3,4.6,.22),concrete)
rounded_pipe('Main line with four elbows',[(-3.6,0,.6),(-3.6,0,2),(1.6,0,2),(1.6,0,3.45),(3.5,0,3.45),(3.5,0,.6)])
rounded_pipe('Return line',[(-3.4,-1.25,.65),(-3.4,-1.25,1.25),(2.65,-1.25,1.25),(2.65,-1.25,.6)])
valve(-.9,0,2); valve(.7,-1.25,1.25)
flange(2.5,0,3.45)
for x,y,z in [(-2.45,0,2),(.55,0,2),(-2.25,-1.25,1.25),(2,-1.25,1.25)]:
    cube('Support foot',(x,y,.25),(.64,.6,.12),dark)
    cube('Pipe support',(x,y,(z-.2+.3)/2),(.13,.16,z-.5),yellow)
    tube('Saddle strap',[(x,y+.205*math.cos(t*math.pi/24),z+.205*math.sin(t*math.pi/24)) for t in range(49)],.024,steel)
    for dx in (-.22,.22): cyl('Anchor bolt',(x+dx,y,.29),(x+dx,y,.36),.045,steel,6)
# Pressure gauge mounted on the main pipe and facing the viewer.
cyl('Gauge riser',(.15,0,2.1),(.15,0,2.6),.045,steel)
cyl('Gauge casing',(.15,.04,2.7),(.15,-.12,2.7),.18,steel)
cyl('Gauge dial',(.15,-.125,2.7),(.15,-.137,2.7),.153,white)
for k in range(11):
    a=math.radians(-40+26*k)
    cyl('Dial tick',(.15+.12*math.cos(a),-.15,2.7+.12*math.sin(a)),(.15+.14*math.cos(a),-.15,2.7+.14*math.sin(a)),.006,dark,8)
cyl('Gauge needle',(.15,-.155,2.7),(.07,-.155,2.79),.009,red,8)
cube('Ground',(0,0,-.13),(200,200,.15),mat('Floor',(.12,.15,.17),0,.8))
scene=bpy.context.scene; scene.world.color=(.2,.2,.2)
for loc,power,size in [((1,-4,8),1600,6),((-5,1,5),1100,5),((4,5,7),1900,4)]:
    bpy.ops.object.light_add(type='AREA',location=loc); o=bpy.context.object; o.data.energy=power; o.data.shape='DISK'; o.data.size=size; o.rotation_euler=(Vector((0,0,1.6))-o.location).to_track_quat('-Z','Y').to_euler()
bpy.ops.object.camera_add(location=(8,-11,7)); camera=bpy.context.object; camera.rotation_euler=(Vector((0,-.2,1.8))-camera.location).to_track_quat('-Z','Y').to_euler(); camera.data.type='ORTHO'; camera.data.ortho_scale=10.8; scene.camera=camera
scene.render.engine='CYCLES'; scene.render.resolution_x=1500; scene.render.resolution_y=1100; scene.render.resolution_percentage=100
