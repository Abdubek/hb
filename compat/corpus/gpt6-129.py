import bpy, math
from mathutils import Vector
bpy.ops.object.select_all(action='SELECT'); bpy.ops.object.delete(use_global=False)
def mat(n,c,metal=0,rough=0.45):
    m=bpy.data.materials.new(n); m.diffuse_color=(*c,1); m.use_nodes=True; p=m.node_tree.nodes.get('Principled BSDF'); p.inputs['Base Color'].default_value=(*c,1); p.inputs['Metallic'].default_value=metal; p.inputs['Roughness'].default_value=rough; return m
def box(n,l,s,m,b=0.035):
    bpy.ops.mesh.primitive_cube_add(size=1,location=l); o=bpy.context.object; o.name=n; o.dimensions=s; bpy.ops.object.transform_apply(location=False,rotation=False,scale=True); o.data.materials.append(m)
    if b:
        mod=o.modifiers.new('Fabricated edges','BEVEL'); mod.width=b; mod.segments=3; o.modifiers.new('Weighted normals','WEIGHTED_NORMAL')
    return o
def rod(n,a,b,r,m,v=24):
    d=Vector(b)-Vector(a); bpy.ops.mesh.primitive_cylinder_add(vertices=v,radius=r,depth=d.length,location=(Vector(a)+Vector(b))/2); o=bpy.context.object; o.name=n; o.rotation_euler=d.to_track_quat('Z','Y').to_euler(); o.data.materials.append(m)
    mod=o.modifiers.new('Rim bevel','BEVEL'); mod.width=min(0.018,r*0.2); mod.segments=2; o.modifiers.new('Normals','WEIGHTED_NORMAL'); return o
def beam(n,a,b,width,depth,m):
    d=Vector(b)-Vector(a); o=box(n,(Vector(a)+Vector(b))/2,(width,depth,d.length),m); o.rotation_euler=d.to_track_quat('Z','Y').to_euler(); return o
def plate(n,profile,y,w,m):
    vs=[(x,y+s*w/2,z) for s in (-1,1) for x,z in profile]; N=len(profile); fs=[tuple(range(N-1,-1,-1)),tuple(range(N,2*N))]+[(i,(i+1)%N,(i+1)%N+N,i+N) for i in range(N)]
    me=bpy.data.meshes.new(n); me.from_pydata(vs,[],fs); me.update(); o=bpy.data.objects.new(n,me); bpy.context.collection.objects.link(o); o.data.materials.append(m); b=o.modifiers.new('Welded plate edge','BEVEL'); b.width=0.035; b.segments=2; o.modifiers.new('Normals','WEIGHTED_NORMAL'); return o
def hose(n,pts,r=0.027):
    c=bpy.data.curves.new(n,'CURVE'); c.dimensions='3D'; c.bevel_depth=r; c.bevel_resolution=3; s=c.splines.new('BEZIER'); s.bezier_points.add(len(pts)-1)
    for p,co in zip(s.bezier_points,pts): p.co=co; p.handle_left_type='AUTO'; p.handle_right_type='AUTO'
    o=bpy.data.objects.new(n,c); bpy.context.collection.objects.link(o); o.data.materials.append(rubber)
yellow=mat('Construction yellow',(0.92,0.52,0.035),0.4); dark=mat('Undercarriage',(0.055,0.065,0.07),0.65); steel=mat('Worn track steel',(0.25,0.28,0.29),0.8); chrome=mat('Hydraulic chrome',(0.68,0.73,0.77),0.95,0.18); rubber=mat('Hydraulic hose',(0.014,0.019,0.022)); glass=mat('Cab tinted glazing',(0.07,0.22,0.27),0.5,0.16); seatmat=mat('Seat fabric',(0.09,0.11,0.12)); light=mat('Lamp glass',(0.93,0.94,0.81),0.1,0.15); orange=mat('Amber beacon',(1,0.27,0.015),0.2)
# Long individual track shoes wrap a stadium-shaped path in the XZ plane.
R=0.55; A=1.48; cz=0.72
for y in (-1.12,1.12):
    box('Track frame',(0,y,0.76),(3.05,0.57,0.51),dark,0.1)
    for x in (-1.48,-0.8,0,0.8,1.48):
        rad=0.48 if abs(x)>1.4 else 0.34
        rod('Track wheel',(x,y-0.32,cz),(x,y+0.32,cz),rad,dark,48)
        for side in (-1,1):
            yy=y+side*0.335; rod('Wheel hub',(x,yy,cz),(x,yy+side*0.055,cz),rad*0.56,steel,32)
            if abs(x)>1.4:
                for k in range(10):
                    t=k*math.tau/10; rod('Sprocket bolt',(x+0.25*math.cos(t),yy,cz+0.25*math.sin(t)),(x+0.25*math.cos(t),yy+side*0.065,cz+0.25*math.sin(t)),0.03,chrome,8)
    perimeter=4*A+2*math.pi*R; count=52
    for i in range(count):
        s=i*perimeter/count
        if s<2*A: x=-A+s; z=cz+R; tx,tz=1,0
        elif s<2*A+math.pi*R:
            a=math.pi/2-(s-2*A)/R; x=A+R*math.cos(a); z=cz+R*math.sin(a); tx,tz=math.sin(a),-math.cos(a)
        elif s<4*A+math.pi*R: x=A-(s-2*A-math.pi*R); z=cz-R; tx,tz=-1,0
        else:
            a=-math.pi/2-(s-4*A-math.pi*R)/R; x=-A+R*math.cos(a); z=cz+R*math.sin(a); tx,tz=math.sin(a),-math.cos(a)
        theta=-math.atan2(tz,tx)
        o=box('Individual track shoe',(x,y,z),(perimeter/count*0.9,0.82,0.105),steel,0.015); o.rotation_euler.y=theta
        # Raised grouser on each shoe, following the local outward normal.
        nx,nz=-tz,tx
        o=box('Track grouser',(x+nx*0.075,y,z+nz*0.075),(0.052,0.84,0.055),dark,0.009); o.rotation_euler.y=theta
box('Undercarriage bridge',(0,0,1.04),(2.5,2.15,0.4),dark)
rod('Slew bearing',(0,0,1.23),(0,0,1.48),0.94,dark,64)
rod('Turntable rim',(0,0,1.46),(0,0,1.57),1.04,steel,64)
box('Upper deck',(-0.16,0,1.7),(3.45,2.27,0.35),yellow,0.13)
box('Rear counterweight',(-1.3,0,2.13),(1.12,2.23,0.81),yellow,0.22)
box('Engine hood',(-0.83,0.55,2.48),(1.75,1.03,0.56),yellow,0.1)
for i in range(9): box('Engine air louver',(-1.49+i*0.15,1.079,2.49),(0.075,0.035,0.32),dark,0.014)
rod('Exhaust stack',(-1.18,0.65,2.75),(-1.18,0.65,3.37),0.065,dark)
rod('Exhaust cap',(-1.28,0.65,3.37),(-1.07,0.65,3.37),0.073,dark)
# Operator cab is an open frame with separate windows and an interior.
box('Cab floor',(-0.28,-0.62,1.97),(1.6,1.04,0.17),dark)
box('Seat cushion',(-0.43,-0.64,2.37),(0.56,0.56,0.16),seatmat,0.08)
box('Seat back',(-0.71,-0.64,2.69),(0.14,0.58,0.64),seatmat,0.07)
rod('Seat pedestal',(-0.44,-0.64,2.04),(-0.44,-0.64,2.3),0.13,dark)
for yy in (-1.15,-0.08):
    beam('Rear cab pillar',(-1.04,yy,2.02),(-0.95,yy,3.69),0.085,0.085,dark)
    beam('Front cab pillar',(0.65,yy,2.02),(0.46,yy,3.69),0.085,0.085,dark)
    for zz in (2.18,2.72,3.66): beam('Cab side frame',(-0.98,yy,zz),(0.46 if zz>3 else 0.57,yy,zz),0.07,0.065,dark)
box('Cab roof',(-0.25,-0.615,3.76),(1.7,1.23,0.16),yellow,0.08)
# Near door glazing split around its frame.
for x,w in [(-0.64,0.54),(0.08,0.7)]:
    box('Door upper window',(x,-1.157,3.18),(w,0.018,0.84),glass,0.035)
    box('Door lower panel',(x,-1.155,2.45),(w,0.04,0.4),yellow,0.015)
beam('Door upright',(-0.31,-1.19,2.15),(-0.31,-1.19,3.67),0.048,0.048,dark)
rod('Door handle',(0.31,-1.21,2.77),(0.31,-1.21,2.99),0.023,chrome)
# Front windshield tilts along the front pillars.
o=box('Front windshield',(0.553,-0.615,2.96),(0.02,0.98,1.38),glass,0.028); o.rotation_euler.y=math.radians(-6.5)
beam('Windshield wiper',(0.65,-0.93,2.47),(0.54,-0.42,3.18),0.022,0.023,dark)
box('Far cab glazing',(-0.25,-0.075,3.04),(1.34,0.018,1.2),glass,0.035)
box('Control console',(0.25,-0.6,2.46),(0.35,0.69,0.27),dark)
for yy in (-0.92,-0.31): rod('Joystick',(0,yy,2.45),(0.08,yy,2.76),0.025,dark)
box('Access step',(-0.45,-1.43,1.46),(0.91,0.45,0.09),steel)
for i in range(5): box('Step tread',(-0.78+i*0.17,-1.43,1.515),(0.065,0.36,0.018),dark,0.003)
rod('Beacon base',(-0.72,-0.2,3.85),(-0.72,-0.2,3.94),0.105,dark)
rod('Amber beacon',(-0.72,-0.2,3.94),(-0.72,-0.2,4.11),0.094,orange)
# Articulated boom runs forward along +X, offset from cab.
y=0.46; P=(0.79,y,2.05); Q=(2.68,y,4.63); S=(4.11,y,2.4)
plate('Main curved boom',[(0.56,1.92),(1.12,1.99),(2.91,4.49),(2.73,4.87),(2.39,4.81),(1.65,3.15)],y,0.48,yellow)
plate('Dipper stick',[(2.46,4.66),(2.85,4.83),(3.16,4.14),(4.29,2.34),(3.97,2.23),(3.45,3.24)],y,0.37,yellow)
for x,z,w in [(P[0],P[2],0.76),(Q[0],Q[2],0.72),(S[0],S[2],0.73)]:
    rod('Articulation pin',(x,y-w/2,z),(x,y+w/2,z),0.145,steel)
    for sign in (-1,1): rod('Pivot end cap',(x,y+sign*w/2,z),(x,y+sign*(w/2+0.04),z),0.105,dark)
def hydraulic(n,a,b):
    a=Vector(a); b=Vector(b); d=b-a; mid=a+d*0.6
    rod(n+' barrel',a,mid,0.11,yellow); rod(n+' gland',mid-d.normalized()*0.06,mid+d.normalized()*0.04,0.13,dark); rod(n+' piston',mid,b,0.062,chrome)
    for p in (a,b): rod(n+' clevis',p+Vector((0,-0.12,0)),p+Vector((0,0.12,0)),0.09,steel)
hydraulic('Boom lift',(0.99,0.07,2.04),(2.13,0.07,3.68))
hydraulic('Stick ram',(1.8,0.47,3.89),(3.15,0.47,4.23))
hydraulic('Bucket curl',(3.23,0.45,3.84),(4.33,0.45,2.65))
for yy in (0.22,0.7):
    hose('Boom hydraulic line',[(0.55,yy,2.1),(0.63,yy,2.7),(1.49,yy,3.34),(2.31,yy,4.68),(2.73,yy,4.97),(3.05,yy,4.43)])
    hose('Dipper hydraulic line',[(2.94,yy,4.43),(3.37,yy,3.84),(3.9,yy,2.86),(4.15,yy,2.64)])
# Open steel bucket: curved rear and floor strip plus two cheek plates; mouth faces +X.
profile=[(3.98,2.41),(3.77,2.13),(3.74,1.71),(3.91,1.4),(4.33,1.2),(4.99,1.17)]
vs=[]
for yy in (y-0.61,y+0.61): vs.extend([(x,yy,z) for x,z in profile])
N=len(profile); fs=[(i,i+1,N+i+1,N+i) for i in range(N-1)]
me=bpy.data.meshes.new('Bucket rolled shell'); me.from_pydata(vs,[],fs); me.update(); ob=bpy.data.objects.new('Open bucket shell',me); bpy.context.collection.objects.link(ob); ob.data.materials.append(steel); so=ob.modifiers.new('Steel wall thickness','SOLIDIFY'); so.thickness=0.065; be=ob.modifiers.new('Worn edges','BEVEL'); be.width=0.025; be.segments=2
cheek=profile+[(4.78,1.65),(4.34,2.37)]
for yy in (y-0.64,y+0.64): plate('Bucket cheek plate',cheek,yy,0.075,yellow)
rod('Bucket hinge',(4.08,y-0.77,2.39),(4.08,y+0.77,2.39),0.13,steel)
for yy in (y-0.3,y+0.3):
    beam('Bucket linkage',(4.1,yy,2.38),(4.33,yy,2.65),0.1,0.07,dark)
    beam('Curl link',(4.33,yy,2.65),(4.48,yy,2.19),0.1,0.07,dark)
beam('Bucket cutting lip',(4.99,y-0.68,1.17),(4.99,y+0.68,1.17),0.11,0.11,steel)
for yy in (y-0.5,y-0.25,y,y+0.25,y+0.5):
    plate('Replaceable digging tooth',[(4.87,1.23),(5.28,1.11),(5.34,1.025),(4.9,1.07)],yy,0.15,chrome)
for yy in (-0.99,0.95): box('Work light',(0.47,yy,3.73),(0.19,0.23,0.16),light)
box('Ground',(0,0,-0.03),(200,200,0.12),mat('Compacted earth',(0.23,0.2,0.15)),0)
scene=bpy.context.scene; scene.world.use_nodes=True; scene.world.node_tree.nodes['Background'].inputs[1].default_value=0.45
for loc,power,size in [((2,-5,10),1800,6),((-5,1,6),1400,5),((5,5,8),2000,5)]:
    bpy.ops.object.light_add(type='AREA',location=loc); o=bpy.context.object; o.data.energy=power; o.data.size=size; o.rotation_euler=(Vector((1,0,2))-o.location).to_track_quat('-Z','Y').to_euler()
bpy.ops.object.camera_add(location=(10,-14,8)); cam=bpy.context.object; cam.rotation_euler=(Vector((1.5,0,2.1))-cam.location).to_track_quat('-Z','Y').to_euler(); cam.data.type='ORTHO'; cam.data.ortho_scale=10; scene.camera=cam
scene.render.engine='CYCLES'; scene.render.resolution_x=1600; scene.render.resolution_y=1100; scene.render.resolution_percentage=100
