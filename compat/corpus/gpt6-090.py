import bpy, math
from mathutils import Vector
bpy.ops.object.select_all(action='SELECT'); bpy.ops.object.delete(use_global=False)

def mat(name,c,metal=0,rough=0.45):
    m=bpy.data.materials.new(name); m.diffuse_color=(*c,1); m.use_nodes=True; p=m.node_tree.nodes.get('Principled BSDF'); p.inputs['Base Color'].default_value=(*c,1); p.inputs['Metallic'].default_value=metal; p.inputs['Roughness'].default_value=rough; return m
paint=mat('Tractor green enamel',(0.13,0.33,0.065),0.4,0.31)
yellow=mat('Warm yellow wheel rims',(0.92,0.61,0.08),0.45,0.32)
rubber=mat('Agricultural tire rubber',(0.023,0.028,0.024),0,0.86)
tread=mat('Raised rubber lugs',(0.037,0.045,0.037),0,0.82)
black=mat('Chassis iron',(0.045,0.06,0.045),0.55,0.55)
seatmat=mat('Black vinyl seat',(0.035,0.036,0.029),0,0.57)
steel=mat('Steel hardware',(0.48,0.54,0.53),0.85,0.27)
lamp=mat('Headlight glass',(0.86,0.93,0.79),0.2,0.18)
red=mat('Rear reflectors',(0.70,0.012,0.008),0.15,0.25)
amber=mat('Amber beacon',(1,0.31,0.015),0.15,0.22)
ground=mat('Earth-colored studio',(0.24,0.22,0.17),0,0.92)

def box(name,loc,dim,m,b=0.02):
    bpy.ops.mesh.primitive_cube_add(size=1,location=loc); o=bpy.context.object; o.name=name; o.dimensions=dim; bpy.ops.object.transform_apply(location=False,rotation=False,scale=True); o.data.materials.append(m)
    if b:
        q=o.modifiers.new('Rounded edges','BEVEL'); q.width=b; q.segments=3; o.modifiers.new('Weighted normals','WEIGHTED_NORMAL')
    return o

def rod(name,a,b,r,m,n=32):
    a,b=Vector(a),Vector(b); bpy.ops.mesh.primitive_cylinder_add(vertices=n,radius=r,depth=(b-a).length,location=(a+b)/2); o=bpy.context.object; o.name=name; o.rotation_euler=(b-a).to_track_quat('Z','Y').to_euler(); o.data.materials.append(m)
    for p in o.data.polygons: p.use_smooth=len(p.vertices)==4
    return o

def beam(name,a,b,w,d,m):
    a,b=Vector(a),Vector(b); o=box(name,(a+b)/2,(w,d,(b-a).length),m,0.014); o.rotation_euler=(b-a).to_track_quat('Z','Y').to_euler(); return o

def tube(name,pts,r,m):
    cu=bpy.data.curves.new(name,'CURVE'); cu.dimensions='3D'; cu.bevel_depth=r; cu.bevel_resolution=3; s=cu.splines.new('POLY'); s.points.add(len(pts)-1)
    for p,v in zip(s.points,pts): p.co=(*v,1)
    o=bpy.data.objects.new(name,cu); bpy.context.collection.objects.link(o); o.data.materials.append(m); return o

def torus(name,loc,major,minor,m,rotation=(math.pi/2,0,0)):
    bpy.ops.mesh.primitive_torus_add(major_segments=64,minor_segments=20,major_radius=major,minor_radius=minor,location=loc,rotation=rotation); o=bpy.context.object; o.name=name; o.data.materials.append(m)
    for p in o.data.polygons: p.use_smooth=True
    return o

# Tractor points toward +X; rear tires dominate the silhouette.
rearx=-0.95; frontx=1.28
box('Main chassis',(0.08,0,0.64),(2.82,0.57,0.25),black,0.045)
box('Transmission housing',(-0.68,0,0.86),(0.88,0.64,0.59),paint,0.12)
rod('Rear axle',(rearx,-1.0,0.86),(rearx,1.0,0.86),0.125,black)
rod('Front axle',(frontx,-0.85,0.52),(frontx,0.85,0.52),0.073,black)
for x,r,width,track in [(rearx,0.86,0.43,0.91),(frontx,0.52,0.28,0.79)]:
    z=r+0.025
    for sy in [-1,1]:
        y=sy*track
        # Revolved sidewalls with a relatively flat tread crown.
        prof=[(-width*0.46,r*0.49),(-width*0.55,r*0.67),(-width*0.49,r*0.90),(-width*0.32,r*0.97),(width*0.32,r*0.97),(width*0.49,r*0.90),(width*0.55,r*0.67),(width*0.46,r*0.49)]
        n=64; vs=[]; fs=[]
        for yy,rr in prof: vs.extend([(x+rr*math.sin(i*math.tau/n),y+yy,z+rr*math.cos(i*math.tau/n)) for i in range(n)])
        for j in range(len(prof)):
            for i in range(n): fs.append((j*n+i,j*n+(i+1)%n,((j+1)%len(prof))*n+(i+1)%n,((j+1)%len(prof))*n+i))
        me=bpy.data.meshes.new('Tire casing'); me.from_pydata(vs,[],fs); me.update(); o=bpy.data.objects.new('Rear agricultural tire' if x==rearx else 'Front agricultural tire',me); bpy.context.collection.objects.link(o); o.data.materials.append(rubber)
        for p in me.polygons: p.use_smooth=True
        # Paired diagonal lugs form a directional chevron pattern.
        for i in range(24 if x==rearx else 20):
            a=i*math.tau/(24 if x==rearx else 20)
            for half in [-1,1]:
                pts=[]
                for j in range(5):
                    t=j/4; aa=a-0.16*t; rr=r*(0.988-0.045*t*t)
                    pts.append((x+rr*math.sin(aa),y+half*width*0.47*t,z+rr*math.cos(aa)))
                for p1,p2 in zip(pts[:-1],pts[1:]):
                    mid=(Vector(p1)+Vector(p2))/2; direction=(Vector(p2)-Vector(p1)).normalized(); normal=Vector((mid.x-x,0,mid.z-z)).normalized(); side=direction.cross(normal).normalized(); normal=side.cross(direction).normalized()
                    from mathutils import Matrix
                    o=box('Chevron tread lug',mid,(r*0.105,(Vector(p2)-Vector(p1)).length+0.012,r*0.065),tread,0.008)
                    o.rotation_euler=Matrix((side,direction,normal)).transposed().to_euler()
        rod('Rim barrel',(x,y-width*0.44,z),(x,y+width*0.44,z),r*0.515,yellow,64)
        out=y+sy*width*0.46
        rod('Inset rim dish',(x,out-sy*0.035,z),(x,out,z),r*0.415,yellow,64)
        torus('Rim lip',(x,out,z),r*0.485,r*0.025,yellow)
        rod('Axle hub',(x,out,z),(x,out+sy*0.09,z),r*0.16,paint,32)
        for k in range(8 if x==rearx else 6):
            a=k*math.tau/(8 if x==rearx else 6); xx=x+r*0.23*math.sin(a); zz=z+r*0.23*math.cos(a)
            rod('Wheel lug bolt',(xx,out,zz),(xx,out+sy*0.027,zz),r*0.025,steel,6)
box('Simple rounded engine hood',(0.69,0,1.24),(1.93,0.82,0.80),paint,0.12)
box('Hood top ridge',(0.66,0,1.658),(1.54,0.11,0.025),paint,0.012)
box('Front grille gasket',(1.675,0,1.23),(0.04,0.69,0.59),black,0.045)
for i in range(13): box('Vertical grille bar',(1.705,-0.285+i*0.0475,1.24),(0.025,0.018,0.48),steel,0.005)
box('Grille lower frame',(1.72,0,0.97),(0.035,0.65,0.035),paint,0.01)
for sy in [-1,1]:
    rod('Headlight housing',(1.58,sy*0.37,1.52),(1.75,sy*0.37,1.52),0.105,black)
    rod('Headlight lens',(1.752,sy*0.37,1.52),(1.765,sy*0.37,1.52),0.084,lamp,48)
    for i in range(7):
        o=box('Hood ventilation slot',(0.85+i*0.075,sy*0.415,1.31),(0.025,0.014,0.29),black,0.009); o.rotation_euler.y=0.18
    box('Hood side stripe',(0.62,sy*0.421,1.53),(1.36,0.012,0.035),yellow,0.005)
    box('Hood latch',(-0.12,sy*0.434,1.07),(0.06,0.035,0.16),steel,0.009)
box('Front ballast bracket',(1.88,0,0.65),(0.50,0.76,0.16),black,0.035)
for y in [-0.27,-0.135,0,0.135,0.27]: box('Front counterweight',(1.97,y,0.75),(0.28,0.115,0.36),black,0.025)
# Vertical exhaust with muffler and a rain cap.
rod('Exhaust riser',(0.72,0.22,1.62),(0.72,0.22,2.10),0.043,black)
rod('Exhaust muffler',(0.72,0.22,1.89),(0.72,0.22,2.26),0.079,black)
rod('Exhaust tip',(0.72,0.22,2.23),(0.72,0.22,2.51),0.037,black)
cap=box('Exhaust rain flap',(0.72,0.22,2.525),(0.10,0.095,0.016),steel,0.008); cap.rotation_euler.y=0.12
rod('Air intake',(0.22,-0.22,1.64),(0.22,-0.22,1.92),0.043,black)
rod('Intake mushroom cap',(0.22,-0.22,1.90),(0.22,-0.22,1.96),0.086,black)
# Open driving station and sheet-metal rear fenders.
box('Operator platform',(-0.79,0,0.90),(1.23,1.24,0.075),paint,0.025)
for sy in [-1,1]:
    box('Rear fender crown',(rearx,sy*0.82,1.81),(1.50,0.51,0.08),paint,0.07)
    box('Rear fender inner wall',(rearx,sy*0.60,1.46),(1.30,0.035,0.69),paint,0.035)
    box('Fender rear reflector',(-1.72,sy*0.83,1.79),(0.026,0.18,0.08),red,0.015)
    box('Fender grab handle',(-1.02,sy*0.59,1.93),(0.30,0.035,0.035),black,0.015)
    for xx in [-1.15,-0.89]: rod('Handle standoff',(xx,sy*0.59,1.82),(xx,sy*0.59,1.93),0.015,black)
    for j in range(2):
        zz=0.48+j*0.21; yy=sy*(0.80-j*0.10)
        box('Access step',(-0.26,yy,zz),(0.45,0.24,0.047),black,0.012)
        for k in range(5): box('Step traction ridge',(-0.43+k*0.082,yy,zz+0.028),(0.024,0.20,0.013),steel,0.003)
    beam('Step support',(-0.42,sy*0.71,0.48),(-0.42,sy*0.53,0.91),0.035,0.035,black)
rod('Seat pedestal',(-0.99,0,0.95),(-0.99,0,1.22),0.08,black)
box('Driver seat cushion',(-1.00,0,1.27),(0.55,0.55,0.14),seatmat,0.075)
o=box('Driver seat back',(-1.27,0,1.53),(0.12,0.55,0.49),seatmat,0.075); o.rotation_euler.y=-0.13
box('Dashboard',(-0.35,0,1.44),(0.15,0.61,0.32),paint,0.035)
for y in [-0.15,0.02,0.17]:
    rod('Gauge bezel',(-0.441,y,1.50),(-0.458,y,1.50),0.062 if y==-0.15 else 0.045,steel)
    rod('Gauge black face',(-0.459,y,1.50),(-0.464,y,1.50),0.051 if y==-0.15 else 0.034,black)
    tube('Gauge needle',[(-0.47,y,1.50),(-0.47,y+0.021,1.52)],0.003,lamp)
a=Vector((-0.36,0,1.12)); b=Vector((-0.69,0,1.68)); rod('Steering column',a,b,0.032,black)
wheel=torus('Steering wheel',b,0.225,0.021,seatmat,(0,0,0)); q=(b-a).to_track_quat('Z','Y'); wheel.rotation_euler=q.to_euler()
for i in range(3):
    v=q@Vector((0.21*math.cos(i*math.tau/3),0.21*math.sin(i*math.tau/3),0)); rod('Steering spoke',b,b+v,0.012,steel)
for y in [-0.23,0.24]:
    rod('Control lever',(-0.70,y,0.96),(-0.59,y,1.30),0.012,steel)
    bpy.ops.mesh.primitive_uv_sphere_add(segments=16,ring_count=8,radius=0.036,location=(-0.59,y,1.30)); bpy.context.object.name='Control knob'; bpy.context.object.data.materials.append(black)
for sy in [-1,1]: beam('Rollover protection upright',(-1.45,sy*0.49,1.08),(-1.53,sy*0.49,2.53),0.075,0.075,black)
box('Rollover top bar',(-1.53,0,2.53),(0.085,1.07,0.08),black)
rod('Beacon base',(-1.53,0.49,2.56),(-1.53,0.49,2.61),0.07,black)
rod('Amber warning beacon',(-1.53,0.49,2.61),(-1.53,0.49,2.76),0.06,amber)
for sy in [-1,1]:
    beam('Rear three-point lower link',(-1.35,sy*0.33,0.57),(-1.98,sy*0.43,0.43),0.045,0.055,steel)
    rod('Lift link',(-1.52,sy*0.34,0.92),(-1.78,sy*0.40,0.48),0.023,steel)
rod('Rear PTO stub',(-1.39,0,0.67),(-1.68,0,0.67),0.055,steel)
box('Drawbar',(-1.86,0,0.40),(0.53,0.13,0.055),black)
box('Ground',(0,0,-0.04),(200,200,0.05),ground)
scene=bpy.context.scene; scene.world.use_nodes=True; scene.world.node_tree.nodes['Background'].inputs[1].default_value=0.45
for loc,power,size in [((4,-5,7),1500,5),((-4,-1,5),1000,4),((1,4,6),1300,4)]:
    bpy.ops.object.light_add(type='AREA',location=loc); o=bpy.context.object; o.data.energy=power; o.data.size=size; o.rotation_euler=(Vector((0,0,1))-o.location).to_track_quat('-Z','Y').to_euler()
bpy.ops.object.camera_add(location=(6,-7,4.3)); cam=bpy.context.object; cam.rotation_euler=(Vector((0,0,1.23))-cam.location).to_track_quat('-Z','Y').to_euler(); cam.data.type='ORTHO'; cam.data.ortho_scale=5.6; scene.camera=cam
scene.render.engine='CYCLES'; scene.render.resolution_x=1300; scene.render.resolution_y=1100; scene.render.resolution_percentage=100
