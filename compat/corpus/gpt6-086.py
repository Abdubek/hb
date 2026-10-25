import bpy, math
from mathutils import Vector
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)

def mat(name, color, metal=0.0, rough=0.4):
    m=bpy.data.materials.new(name); m.diffuse_color=(*color,1); m.use_nodes=True
    p=m.node_tree.nodes.get('Principled BSDF'); p.inputs['Base Color'].default_value=(*color,1); p.inputs['Metallic'].default_value=metal; p.inputs['Roughness'].default_value=rough
    return m
steel=mat('Brushed stainless steel',(0.48,0.55,0.61),0.88,0.25)
polish=mat('Polished edges',(0.72,0.79,0.85),0.95,0.14)
black=mat('Midnight blue dial',(0.012,0.032,0.055),0.3,0.3)
lume=mat('Ivory luminous indices',(0.85,0.92,0.84),0.1,0.25)
red=mat('Orange seconds hand',(1.0,0.17,0.035),0.4,0.25)
dark=mat('Dark joints',(0.045,0.052,0.06),0.7,0.4)
backdrop=mat('Backdrop',(0.10,0.14,0.18),0,0.75)

def finish(o,name,m,bevel=0):
    o.name=name; o.data.materials.append(m)
    if bevel:
        mod=o.modifiers.new('Machined edge radii','BEVEL'); mod.width=bevel; mod.segments=3
        o.modifiers.new('Weighted normals','WEIGHTED_NORMAL')
    return o

def box(name,loc,scale,m,bevel=0):
    bpy.ops.mesh.primitive_cube_add(size=1,location=loc); o=bpy.context.object; o.dimensions=scale
    bpy.ops.object.transform_apply(location=False,rotation=False,scale=True)
    return finish(o,name,m,bevel)

def cyl(name,loc,r,depth,m,verts=96):
    bpy.ops.mesh.primitive_cylinder_add(vertices=verts,radius=r,depth=depth,location=loc)
    o=finish(bpy.context.object,name,m,0.025)
    for p in o.data.polygons: p.use_smooth=len(p.vertices)==4
    return o

def rod(name,a,b,r,m):
    a,b=Vector(a),Vector(b); o=cyl(name,(a+b)/2,r,(b-a).length,m,32)
    o.rotation_euler=(b-a).to_track_quat('Z','Y').to_euler(); return o

def ring(name,outer,inner,z,depth,m):
    n=128; vs=[]
    for zz,rr in [(z-depth/2,outer),(z+depth/2,outer),(z-depth/2,inner),(z+depth/2,inner)]:
        vs.extend([(rr*math.cos(i*2*math.pi/n),rr*math.sin(i*2*math.pi/n),zz) for i in range(n)])
    fs=[]
    for i in range(n):
        j=(i+1)%n
        fs.extend([(i,j,n+j,n+i),(2*n+j,2*n+i,3*n+i,3*n+j),(n+i,n+j,3*n+j,3*n+i),(j,i,2*n+i,2*n+j)])
    me=bpy.data.meshes.new(name); me.from_pydata(vs,[],fs); me.update()
    o=bpy.data.objects.new(name,me); bpy.context.collection.objects.link(o); finish(o,name,m,0.012)
    return o

def lettering(name,body,loc,size,m):
    cu=bpy.data.curves.new(name,'FONT'); cu.body=body; cu.align_x='CENTER'; cu.align_y='CENTER'; cu.size=size; cu.extrude=0.001
    ob=bpy.data.objects.new(name,cu); bpy.context.collection.objects.link(ob); ob.location=loc; ob.data.materials.append(m)

cyl('Screw-down case back',(0,0,0.32),1.14,0.15,steel)
cyl('Round brushed case',(0,0,0.52),1.25,0.40,steel)
ring('Polished bezel',1.28,1.095,0.77,0.14,polish)
ring('Inner bezel shadow',1.105,1.045,0.773,0.07,dark)
cyl('Recessed dial',(0,0,0.735),1.047,0.06,black)
for i in range(60):
    a=i*math.tau/60; major=i%5==0; rr=0.935 if major else 0.982
    o=box('Hour index' if major else 'Minute tick',(rr*math.sin(a),rr*math.cos(a),0.785),(0.047 if major else 0.015,0.16 if major else 0.063,0.016),lume,0.006)
    o.rotation_euler.z=-a
lettering('Brand','MERIDIAN',(0,0.40,0.78),0.135,lume)
lettering('Movement label','AUTOMATIC',(0,-0.40,0.78),0.083,lume)
lettering('Dial subtitle','100 m',(0,-0.55,0.78),0.073,lume)
box('Date surround',(0.69,0,0.787),(0.255,0.20,0.025),polish,0.015)
box('Date paper',(0.69,0,0.805),(0.21,0.155,0.01),lume,0.004)
lettering('Date','18',(0.69,0,0.815),0.115,black)

def hand(name,length,width,angle,z,m):
    vs=[(-width/2,-0.13,0),(width/2,-0.13,0),(width/2,length-0.14,0),(0,length,0),(-width/2,length-0.14,0)]
    me=bpy.data.meshes.new(name); me.from_pydata(vs,[],[(0,1,2,3,4)]); me.update()
    o=bpy.data.objects.new(name,me); bpy.context.collection.objects.link(o); o.location.z=z; o.rotation_euler.z=math.radians(-angle); o.data.materials.append(m)
    s=o.modifiers.new('Hand thickness','SOLIDIFY'); s.thickness=0.018
    b=o.modifiers.new('Fine edges','BEVEL'); b.width=0.008; b.segments=2
hand('Hour hand at ten',0.64,0.10,305,0.825,polish)
hand('Hour luminous insert',0.52,0.042,305,0.848,lume)
hand('Minute hand at two',0.87,0.078,60,0.866,polish)
hand('Minute luminous insert',0.74,0.03,60,0.888,lume)
hand('Seconds sweep',0.94,0.023,192,0.906,red)
cyl('Hand axle',(0,0,0.926),0.078,0.04,polish,48)
cyl('Axle cap',(0,0,0.951),0.037,0.015,red,32)
for sy in [-1,1]:
    for sx in [-1,1]:
        lug=box('Integral lug',(sx*0.55,sy*1.18,0.49),(0.24,0.54,0.30),steel,0.075)
        lug.rotation_euler.x=sy*0.10
    rod('Spring bar',(-0.61,sy*1.39,0.44),(0.61,sy*1.39,0.44),0.065,dark)
    for i in range(8):
        y=sy*(1.52+i*0.345); z=0.40-0.11*min(i/3,1)
        for x,w in [(-0.40,0.29),(0,0.46),(0.40,0.29)]:
            box('Articulated bracelet link',(x,y,z),(w,0.318,0.20),polish if x==0 else steel,0.055)
        rod('Bracelet hinge',(-0.52,y+sy*0.155,z),(0.52,y+sy*0.155,z),0.038,dark)
        for sx in [-1,1]:
            rod('Link pin end',(sx*0.543,y,z),(sx*0.558,y,z),0.032,polish)
box('Folding clasp',(0,4.25,0.29),(1.03,0.65,0.22),steel,0.065)
box('Clasp inset',(0,4.25,0.41),(0.70,0.46,0.025),polish,0.025)
rod('Crown stem',(1.16,0,0.53),(1.42,0,0.53),0.10,dark)
rod('Winding crown',(1.35,0,0.53),(1.60,0,0.53),0.205,steel)
for i in range(28):
    a=i*math.tau/28
    rod('Crown knurl',(1.38,0.20*math.cos(a),0.53+0.20*math.sin(a)),(1.57,0.20*math.cos(a),0.53+0.20*math.sin(a)),0.012,polish)
box('Studio floor',(0,0,-0.04),(200,200,0.1),backdrop)
world=bpy.context.scene.world; world.use_nodes=True; world.node_tree.nodes['Background'].inputs[0].default_value=(0.17,0.20,0.25,1); world.node_tree.nodes['Background'].inputs[1].default_value=0.45
for name,loc,power,size in [('Large softbox',(-4,-2,8),1000,5),('Rim strip',(4,3,6),1300,4),('Fill',(1,-5,4),500,3)]:
    bpy.ops.object.light_add(type='AREA',location=loc); o=bpy.context.object; o.name=name; o.data.energy=power; o.data.shape='DISK'; o.data.size=size; o.rotation_euler=(Vector((0,0,0.3))-o.location).to_track_quat('-Z','Y').to_euler()
bpy.ops.object.camera_add(location=(5,-7,12)); cam=bpy.context.object; cam.rotation_euler=(Vector((0,0.25,0.4))-cam.location).to_track_quat('-Z','Y').to_euler(); cam.data.type='ORTHO'; cam.data.ortho_scale=10.6
scene=bpy.context.scene; scene.camera=cam; scene.render.engine='CYCLES'; scene.render.resolution_x=1000; scene.render.resolution_y=1200; scene.render.resolution_percentage=100
