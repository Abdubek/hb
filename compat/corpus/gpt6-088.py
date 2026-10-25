import bpy, math
from mathutils import Vector
bpy.ops.object.select_all(action='SELECT'); bpy.ops.object.delete(use_global=False)

def mat(name,c,metal=0,rough=0.5):
    m=bpy.data.materials.new(name); m.diffuse_color=(*c,1); m.use_nodes=True; p=m.node_tree.nodes.get('Principled BSDF'); p.inputs['Base Color'].default_value=(*c,1); p.inputs['Metallic'].default_value=metal; p.inputs['Roughness'].default_value=rough; return m
steel=mat('Galvanized frame',(0.37,0.44,0.48),0.8,0.36)
edge=mat('Bright hardware',(0.65,0.69,0.70),0.85,0.25)
dark=mat('Axle and springs',(0.055,0.065,0.07),0.6,0.48)
rubber=mat('Tire rubber',(0.025,0.03,0.032),0,0.85)
tread=mat('Tread blocks',(0.04,0.045,0.048),0,0.9)
red=mat('Red tail lenses',(0.60,0.015,0.012),0.1,0.24)
amber=mat('Amber reflectors',(1,0.31,0.025),0.1,0.22)
white=mat('Plate lettering',(0.84,0.86,0.80),0,0.5)
wood=[mat('Weathered plank '+str(i),(0.29+i*0.017,0.20+i*0.012,0.105+i*0.009),0,0.82) for i in range(5)]
ground=mat('Ground',(0.18,0.22,0.24),0,0.9)

def box(name,loc,dim,m,b=0.015):
    bpy.ops.mesh.primitive_cube_add(size=1,location=loc); o=bpy.context.object; o.name=name; o.dimensions=dim; bpy.ops.object.transform_apply(location=False,rotation=False,scale=True); o.data.materials.append(m)
    if b:
        mod=o.modifiers.new('Soft edges','BEVEL'); mod.width=b; mod.segments=2; o.modifiers.new('Weighted normals','WEIGHTED_NORMAL')
    return o

def beam(name,a,b,width,height,m):
    a,b=Vector(a),Vector(b); o=box(name,(a+b)/2,(width,height,(b-a).length),m,0.012); o.rotation_euler=(b-a).to_track_quat('Z','Y').to_euler(); return o

def rod(name,a,b,r,m,n=32):
    a,b=Vector(a),Vector(b); bpy.ops.mesh.primitive_cylinder_add(vertices=n,radius=r,depth=(b-a).length,location=(a+b)/2); o=bpy.context.object; o.name=name; o.rotation_euler=(b-a).to_track_quat('Z','Y').to_euler(); o.data.materials.append(m)
    for p in o.data.polygons: p.use_smooth=len(p.vertices)==4
    return o

def tube(name,pts,r,m):
    cu=bpy.data.curves.new(name,'CURVE'); cu.dimensions='3D'; cu.bevel_depth=r; cu.bevel_resolution=3; sp=cu.splines.new('POLY'); sp.points.add(len(pts)-1)
    for p,v in zip(sp.points,pts): p.co=(*v,1)
    o=bpy.data.objects.new(name,cu); bpy.context.collection.objects.link(o); o.data.materials.append(m)

# The tongue extends toward positive X; rear gate is at negative X.
for y in [-0.86,0.86]: box('Main chassis rail',(0,y,0.71),(3.3,0.10,0.16),steel)
for x in [-1.60,-0.8,0,0.8,1.60]: box('Bed crossmember',(x,0,0.70),(0.09,1.65,0.12),steel)
for j in range(9):
    y=-0.76+j*0.19; box('Timber deck board',(0,y,0.815),(3.18,0.18,0.075),wood[j%5],0.008)
    for x in [-1.48,-0.04,1.48]:
        rod('Deck carriage bolt',(x,y,0.853),(x,y,0.859),0.021,edge,12)
for sy in [-1,1]:
    y=sy*0.86
    for z in [0.91,1.38]: box('Side perimeter rail',(0,y,z),(3.30,0.06,0.065),steel)
    for x in [-1.61,-0.55,0.55,1.61]:
        box('Side stake',(x,y,1.14),(0.055,0.065,0.53),steel)
        for z in [1.04,1.26]: rod('Stake bolt',(x,y,z),(x,y+sy*0.042,z),0.019,edge,12)
    for z in [1.035,1.25]: box('Side timber slat',(0,y, z),(3.19,0.037,0.17),wood[2],0.006)
for x in [-1.62,1.62]:
    for z in [0.91,1.38]: box('End rail',(x,0,z),(0.06,1.77,0.065),steel)
    for z in [1.035,1.25]: box('End timber slat',(x,0,z),(0.04,1.66,0.17),wood[3],0.006)
    for y in [-0.82,0,0.82]: box('End upright',(x,y,1.14),(0.064,0.055,0.5),steel)
for y in [-0.57,0.57]:
    box('Tailgate hinge leaf',(-1.665,y,0.94),(0.027,0.17,0.16),edge)
    rod('Tailgate hinge barrel',(-1.70,y-0.12,0.875),(-1.70,y+0.12,0.875),0.03,edge)
for y in [-0.78,0.78]: box('Gate latch',(-1.68,y,1.32),(0.045,0.18,0.055),dark)
ax=-0.25; wz=0.49
rod('Continuous axle',(ax,-1.13,wz),(ax,1.13,wz),0.065,dark)
for sy in [-1,1]:
    y=sy*1.05
    # Closed tire profile revolved around the axle.
    profile=[(-0.16,0.29),(-0.17,0.38),(-0.13,0.47),(-0.085,0.49),(0.085,0.49),(0.13,0.47),(0.17,0.38),(0.16,0.29)]
    vs=[]; fs=[]; n=64
    for yy,rr in profile:
        vs.extend([(ax+rr*math.sin(i*math.tau/n),y+yy,wz+rr*math.cos(i*math.tau/n)) for i in range(n)])
    for j in range(len(profile)):
        for i in range(n): fs.append((j*n+i,j*n+(i+1)%n,((j+1)%len(profile))*n+(i+1)%n,((j+1)%len(profile))*n+i))
    me=bpy.data.meshes.new('Tire'); me.from_pydata(vs,[],fs); me.update(); ob=bpy.data.objects.new('Pneumatic tire',me); bpy.context.collection.objects.link(ob); ob.data.materials.append(rubber)
    for p in me.polygons: p.use_smooth=True
    rod('Steel wheel rim',(ax,y-0.135,wz),(ax,y+0.135,wz),0.302,edge,64)
    out=y+sy*0.15
    rod('Recessed rim dish',(ax,out-sy*0.02,wz),(ax,out,wz),0.235,steel,64)
    rod('Hub cap',(ax,out,wz),(ax,out+sy*0.065,wz),0.095,edge)
    for k in range(5):
        a=k*math.tau/5; xx=ax+0.145*math.sin(a); zz=wz+0.145*math.cos(a)
        rod('Wheel ventilation inset',(xx,out,zz),(xx,out+sy*0.004,zz),0.044,dark,24)
        xx=ax+0.11*math.sin(a); zz=wz+0.11*math.cos(a)
        rod('Lug nut',(xx,out,zz),(xx,out+sy*0.035,zz),0.019,edge,6)
    for i in range(44):
        a=i*math.tau/44
        for row in [-1,1]:
            o=box('Tire tread',(ax+0.489*math.sin(a),y+row*0.062,wz+0.489*math.cos(a)),(0.047,0.095,0.015),tread,0.004); o.rotation_euler.y=a
    # Folded sheet fender with a broad top and angled ends.
    pts=[(ax-0.68,y,0.68),(ax-0.51,y,1.03),(ax-0.34,y,1.08),(ax+0.34,y,1.08),(ax+0.51,y,1.03),(ax+0.68,y,0.68)]
    vs=[(x,yy+d,z) for x,yy,z in pts for d in [-0.235,0.235]]; fs=[(i*2,i*2+1,i*2+3,i*2+2) for i in range(len(pts)-1)]
    me=bpy.data.meshes.new('Fender sheet'); me.from_pydata(vs,[],fs); me.update(); o=bpy.data.objects.new('Folded galvanized fender',me); bpy.context.collection.objects.link(o); o.data.materials.append(steel); mod=o.modifiers.new('Sheet gauge','SOLIDIFY'); mod.thickness=0.022
    for dy in [-0.235,0.235]: tube('Rolled fender edge',[(x,yy+dy,z) for x,yy,z in pts],0.015,edge)
    box('Rear mudflap',(ax-0.65,y,0.51),(0.028,0.40,0.33),rubber)
    for layer in range(4):
        span=0.60-layer*0.085
        pts=[(ax-span+2*span*i/20,sy*0.67,0.48+0.14*((i/10)-1)**2-layer*0.018) for i in range(21)]
        for a,b in zip(pts[:-1],pts[1:]): beam('Leaf spring',a,b,0.065,0.012,dark)
    for xx in [ax-0.60,ax+0.60]: box('Spring hanger',(xx,sy*0.67,0.635),(0.09,0.09,0.19),steel)
    for xx in [ax-0.095,ax+0.095]: rod('Axle U-bolt',(xx,sy*0.67,0.42),(xx,sy*0.67,0.62),0.014,edge)
    box('Amber side reflector',(1.32,sy*0.903,1.05),(0.15,0.017,0.07),amber)
    box('Rear lamp housing',(-1.70,sy*0.68,0.75),(0.12,0.25,0.14),dark)
    box('Red rear lamp',(-1.767,sy*0.68,0.76),(0.022,0.20,0.10),red)
for y in [-0.80,0.80]: beam('A-frame tongue',(1.38,y,0.69),(3.02,0,0.69),0.11,0.13,steel)
box('Tongue cross tie',(2.02,0,0.69),(0.10,0.96,0.09),steel)
box('Hitch coupler body',(3.16,0,0.70),(0.58,0.21,0.18),edge,0.07)
bpy.ops.mesh.primitive_uv_sphere_add(segments=32,ring_count=16,location=(3.43,0,0.675)); o=bpy.context.object; o.name='Rounded ball socket nose'; o.scale=(0.15,0.12,0.105); o.data.materials.append(edge)
box('Coupler latch base',(3.17,0,0.815),(0.25,0.10,0.045),dark)
beam('Locking latch handle',(3.08,0,0.83),(3.33,0,0.90),0.09,0.04,edge)
rod('Jack outer sleeve',(2.60,0.25,0.40),(2.60,0.25,0.93),0.053,steel)
rod('Jack telescoping leg',(2.60,0.25,0.10),(2.60,0.25,0.50),0.035,edge)
box('Jack foot',(2.60,0.25,0.07),(0.26,0.20,0.055),steel)
rod('Jack crank',(2.60,0.25,0.96),(2.60,0.45,0.96),0.018,edge)
rod('Crank grip',(2.60,0.45,0.96),(2.60,0.45,1.07),0.027,rubber)
for sy in [-1,1]:
    for i in range(14):
        t=i/13; loc=(2.75+0.60*t,sy*(0.11+0.13*math.sin(math.pi*t)),0.61-0.22*math.sin(math.pi*t))
        bpy.ops.mesh.primitive_torus_add(major_segments=12,minor_segments=6,location=loc,major_radius=0.035,minor_radius=0.009,rotation=(math.pi/2 if i%2 else 0,0,0)); o=bpy.context.object; o.name='Safety chain link'; o.scale.x=1.4; o.data.materials.append(dark)
box('Rear number plate',(-1.775,0,0.70),(0.02,0.46,0.14),white)
box('Ground',(0,0,-0.035),(200,200,0.05),ground)
scene=bpy.context.scene; scene.world.use_nodes=True; scene.world.node_tree.nodes['Background'].inputs[1].default_value=0.45
for loc,power,size in [((2,-4,7),1300,5),((-4,2,5),1000,4),((5,4,3),700,3)]:
    bpy.ops.object.light_add(type='AREA',location=loc); o=bpy.context.object; o.data.energy=power; o.data.size=size; o.rotation_euler=(Vector((0.6,0,0.7))-o.location).to_track_quat('-Z','Y').to_euler()
bpy.ops.object.camera_add(location=(7,-7,5)); cam=bpy.context.object; cam.rotation_euler=(Vector((0.75,0,0.65))-cam.location).to_track_quat('-Z','Y').to_euler(); cam.data.type='ORTHO'; cam.data.ortho_scale=6.7; scene.camera=cam
scene.render.engine='CYCLES'; scene.render.resolution_x=1400; scene.render.resolution_y=1000; scene.render.resolution_percentage=100
