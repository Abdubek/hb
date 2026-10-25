import bpy, math
from mathutils import Vector
bpy.ops.object.select_all(action='SELECT'); bpy.ops.object.delete(use_global=False)
def mat(n,c,metal=0,rough=0.45):
    m=bpy.data.materials.new(n); m.diffuse_color=(*c,1); m.use_nodes=True; p=m.node_tree.nodes.get('Principled BSDF'); p.inputs['Base Color'].default_value=(*c,1); p.inputs['Metallic'].default_value=metal; p.inputs['Roughness'].default_value=rough; return m
def box(n,l,s,m,b=0.025):
    bpy.ops.mesh.primitive_cube_add(size=1,location=l); o=bpy.context.object; o.name=n; o.dimensions=s; bpy.ops.object.transform_apply(location=False,rotation=False,scale=True); o.data.materials.append(m)
    if b:
        mod=o.modifiers.new('Fabrication bevel','BEVEL'); mod.width=b; mod.segments=2; o.modifiers.new('Weighted normals','WEIGHTED_NORMAL')
    return o
def rod(n,a,b,r,m,v=16):
    d=Vector(b)-Vector(a); bpy.ops.mesh.primitive_cylinder_add(vertices=v,radius=r,depth=d.length,location=(Vector(a)+Vector(b))/2); o=bpy.context.object; o.name=n; o.rotation_euler=d.to_track_quat('Z','Y').to_euler(); o.data.materials.append(m); return o
def wire(n,pts,r,m):
    c=bpy.data.curves.new(n,'CURVE'); c.dimensions='3D'; c.bevel_depth=r; c.bevel_resolution=3; c.resolution_u=16; s=c.splines.new('BEZIER'); s.bezier_points.add(len(pts)-1)
    for p,co in zip(s.bezier_points,pts): p.co=co; p.handle_left_type='AUTO'; p.handle_right_type='AUTO'
    ob=bpy.data.objects.new(n,c); bpy.context.collection.objects.link(ob); ob.data.materials.append(m)
def label(t,l,size,m):
    bpy.ops.object.text_add(location=l,rotation=(math.pi/2,0,0)); o=bpy.context.object; o.data.body=t; o.data.size=size; o.data.extrude=0.001; o.data.materials.append(m)
steel=mat('Galvanized steel',(0.47,0.53,0.56),0.8); red=mat('Aviation red',(0.66,0.055,0.035),0.45); white=mat('Off white coated steel',(0.82,0.83,0.79),0.35); dark=mat('Cables',(0.025,0.03,0.035)); concrete=mat('Concrete',(0.42,0.43,0.41)); yellow=mat('Safety yellow',(0.95,0.62,0.035),0.3); panelmat=mat('Antenna radome',(0.78,0.81,0.77),0.08); lamp=mat('Red beacon',(0.9,0.015,0.008)); p=lamp.node_tree.nodes.get('Principled BSDF'); p.inputs['Emission Color'].default_value=(1,0.008,0.002,1); p.inputs['Emission Strength'].default_value=3
# Four modular square lattice bays, with bolted flange joints.
base=0.65; bay=2.75; corners=[(-1,-1),(1,-1),(1,1),(-1,1)]
for x,y in corners:
    box('Concrete footing',(x,y,0.2),(1.07,1.07,0.4),concrete,0.06)
    box('Base plate',(x,y,0.44),(0.6,0.6,0.075),steel)
    rod('Column shoe',(x,y,0.46),(x,y,base),0.14,steel)
    for dx in (-0.21,0.21):
        for dy in (-0.21,0.21): rod('Anchor bolt',(x+dx,y+dy,0.46),(x+dx,y+dy,0.56),0.035,steel,6)
for k in range(4):
    z0=base+k*bay; z1=z0+bay; m=red if k%2 else white
    for x,y in corners:
        rod('Modular vertical chord',(x,y,z0),(x,y,z1),0.085,m)
        for z in (z0+0.055,z1-0.055):
            box('Bolted chord flange',(x,y,z),(0.34,0.34,0.065),steel,0.009)
            for dx in (-0.115,0.115):
                for dy in (-0.115,0.115): rod('Flange fastener',(x+dx,y+dy,z-0.055),(x+dx,y+dy,z+0.055),0.023,dark,6)
    for i,(x,y) in enumerate(corners):
        xx,yy=corners[(i+1)%4]
        for z in (z0+0.15,z0+bay/2,z1-0.15): rod('Horizontal lattice tie',(x,y,z),(xx,yy,z),0.043,m)
        # Half-bay X bracing has alternating slight offsets at crossing points.
        for h in range(2):
            za=z0+h*bay/2+0.15; zb=z0+(h+1)*bay/2-0.15
            rod('Diagonal cross brace',(x,y,za),(xx,yy,zb),0.032,m)
            rod('Diagonal cross brace',(x,y,zb),(xx,yy,za),0.032,m)
# Walkable grated platforms with a rectangular opening around the access ladder.
def platform(z):
    for y in (-1.53,1.53): box('Platform perimeter beam',(0,y,z),(3.18,0.12,0.17),steel)
    for x in (-1.53,1.53): box('Platform perimeter beam',(x,0,z),(0.12,3.18,0.17),steel)
    for i in range(32):
        x=-1.49+i*0.096
        # Hatch opening at the front left corner.
        if -0.94<x<-0.25:
            box('Grating bearer',(x,0.32,z+0.08),(0.033,2.4,0.045),steel,0.004)
        else: box('Grating bearer',(x,0,z+0.08),(0.033,3.02,0.045),steel,0.004)
    for j in range(16):
        y=-1.45+j*0.193
        if y<-0.87:
            for x,L in [(-1.23,0.48),(0.64,1.72)]: box('Grating cross strip',(x,y,z+0.055),(L,0.025,0.03),steel,0)
        else: box('Grating cross strip',(0,y,z+0.055),(3,0.025,0.03),steel,0)
    for i in range(4):
        a=Vector((corners[i][0]*1.53,corners[i][1]*1.53,z)); b=Vector((corners[(i+1)%4][0]*1.53,corners[(i+1)%4][1]*1.53,z))
        for zz in (0.56,1.05): rod('Platform guardrail',a+Vector((0,0,zz)),b+Vector((0,0,zz)),0.032,yellow)
        for t in (0,0.5,1):
            q=a.lerp(b,t); rod('Railing post',q,q+Vector((0,0,1.07)),0.034,steel)
        mid=(a+b)/2
        o=box('Platform toe board',mid+Vector((0,0,0.16)),(3.03,0.035,0.14),yellow,0.006); o.rotation_euler.z=math.atan2((b-a).y,(b-a).x)
        rod('Platform support diagonal',(corners[i][0],corners[i][1],z-0.75),a,0.05,steel)
for z in (3.4,8.9,11.65): platform(z)
# Climbing ladder at front left with safety hoops above the first landing.
for x in (-0.94,-0.28): rod('Access ladder rail',(x,-1.27,0.45),(x,-1.27,12.65),0.032,steel)
for i in range(42):
    z=0.6+i*0.285; rod('Ladder rung',(-0.94,-1.27,z),(-0.28,-1.27,z),0.023,steel)
for z in (4.2,5.25,6.3,7.35,8.4,9.6,10.65):
    pts=[]
    for j in range(25):
        a=j*math.pi/24; pts.append((-0.61+0.48*math.cos(a),-1.27-0.58*math.sin(a),z))
    wire('Ladder safety hoop',pts,0.022,steel)
for a in (math.pi*0.25,math.pi*0.5,math.pi*0.75):
    x=-0.61+0.48*math.cos(a); y=-1.27-0.58*math.sin(a); rod('Safety cage vertical',(x,y,4.2),(x,y,10.65),0.021,steel)
# Separate cable ladder on right, including multiple feeder bundles and clamps.
for y in (-0.36,0.36): rod('Cable tray spine',(1.12,y,0.6),(1.12,y,11.45),0.031,steel)
for i in range(35):
    z=0.7+i*0.31; rod('Cable tray rung',(1.12,-0.36,z),(1.12,0.36,z),0.018,steel)
for j in range(6):
    y=-0.26+j*0.103; wire('Vertical RF feeder',[(1.19,y,0.54),(1.2,y,1.2),(1.2,y,8.5),(1.2,y,10.9)],0.026,dark)
    for z in (1.6,3.9,6.2,8.5,10.5): rod('Cable clamp',(1.2,y-0.041,z),(1.2,y+0.041,z),0.032,steel,12)
# Three sectors of tall antenna panels around the upper mast.
rod('Upper antenna support mast',(0,0,10.8),(0,0,14.7),0.11,steel)
for sector in range(3):
    a=sector*math.tau/3-math.pi/2; outward=Vector((math.cos(a),math.sin(a),0)); tangent=Vector((-math.sin(a),math.cos(a),0))
    for offset in (-0.42,0.42):
        center=outward*1.32+tangent*offset+Vector((0,0,12.91))
        for z in (12.17,13.65):
            q=Vector((center.x,center.y,z)); rod('Antenna standoff',(0,0,z),q-outward*0.13,0.045,steel)
            rod('Antenna mounting pole',q-Vector((0,0,0.19)),q+Vector((0,0,0.19)),0.045,steel)
        o=box('Sector antenna radome',center,(0.49,0.23,2.05),panelmat,0.1); o.rotation_euler.z=a-math.pi/2
        q=center-outward*0.14
        o=box('Antenna rear spine',q,(0.18,0.06,1.65),steel,0.016); o.rotation_euler.z=a-math.pi/2
        start=center-Vector((0,0,1.04)); rod('RF connector',start,start-Vector((0,0,0.13)),0.045,steel)
        wire('Antenna jumper',[tuple(start-Vector((0,0,0.1))),tuple(start-Vector((0,0,0.42))),tuple(outward*0.7+Vector((0,0,11.5))),(1.2,offset*0.4,10.9)],0.023,dark)
# Parabolic microwave dish on the left of the middle platform.
center=Vector((-1.47,-0.1,9.83)); axis=Vector((-0.86,-0.5,0.07)).normalized(); u=Vector((0,0,1)).cross(axis).normalized(); v=axis.cross(u); radius=0.73; rings=12; segments=48
verts=[tuple(center)]
for j in range(1,rings+1):
    r=radius*j/rings
    for i in range(segments):
        a=i*math.tau/segments; q=center+u*(r*math.cos(a))+v*(r*math.sin(a))+axis*(0.3*(r/radius)**2); verts.append(tuple(q))
faces=[(0,1+i,1+(i+1)%segments) for i in range(segments)]
for j in range(rings-1):
    a=1+j*segments; b=a+segments
    for i in range(segments): faces.append((a+i,b+i,b+(i+1)%segments,a+(i+1)%segments))
me=bpy.data.meshes.new('Parabolic reflector'); me.from_pydata(verts,[],faces); me.update(); ob=bpy.data.objects.new('Microwave dish',me); bpy.context.collection.objects.link(ob); ob.data.materials.append(white); so=ob.modifiers.new('Dish thickness','SOLIDIFY'); so.thickness=0.035
for p in me.polygons: p.use_smooth=True
focus=center+axis*0.55
for a in (0,math.tau/3,2*math.tau/3):
    rim=center+u*(radius*math.cos(a))+v*(radius*math.sin(a))+axis*0.3; rod('Dish feed support',rim,focus,0.016,steel)
rod('Microwave feed',focus-axis*0.07,focus+axis*0.1,0.085,dark)
rod('Dish mounting bracket',(-1,0,9.6),center-axis*0.15,0.08,steel)
rod('Lightning finial',(0,0,14.5),(0,0,15.7),0.025,steel)
rod('Beacon base',(0,0,14.65),(0,0,14.78),0.14,dark)
rod('Obstruction beacon',(0,0,14.78),(0,0,15.04),0.12,lamp)
# Ground communications cabinet and incoming conduit.
box('Equipment plinth',(2.55,0.8,0.14),(1.52,1.47,0.28),concrete)
box('Outdoor radio cabinet',(2.55,0.8,1.15),(1.18,1.08,1.75),white,0.07)
box('Cabinet door',(2.55,0.245,1.17),(1.04,0.05,1.58),steel,0.02)
rod('Cabinet latch',(2.93,0.205,1.03),(2.93,0.205,1.3),0.023,dark)
for i in range(7): box('Cabinet cooling louver',(2.54,0.21,0.65+i*0.075),(0.77,0.03,0.029),dark,0.006)
wire('Feeder conduit',[(1.19,0.1,1),(1.28,0.1,0.4),(1.9,0.6,0.32),(2.05,0.8,0.5),(2.05,0.8,0.9)],0.095,dark)
label('RF / 04',(2.2,0.207,1.65),0.15,dark)
box('Warning placard',(0.43,-1.045,1.95),(0.57,0.035,0.43),yellow,0.016)
label('DANGER',(0.19,-1.07,1.99),0.105,dark); label('RF AREA',(0.2,-1.07,1.83),0.09,dark)
box('Site ground',(0,0,-0.08),(200,200,0.12),mat('Gravel ground',(0.2,0.24,0.23)),0)
scene=bpy.context.scene; scene.world.use_nodes=True; scene.world.node_tree.nodes['Background'].inputs[0].default_value=(0.43,0.56,0.7,1); scene.world.node_tree.nodes['Background'].inputs[1].default_value=0.5
bpy.ops.object.light_add(type='SUN',rotation=(math.radians(25),math.radians(-30),math.radians(-25))); bpy.context.object.data.energy=2.5; bpy.context.object.data.angle=0.12
for loc,power,size in [((5,-8,13),2300,8),((-6,2,12),1800,7)]:
    bpy.ops.object.light_add(type='AREA',location=loc); o=bpy.context.object; o.data.energy=power; o.data.size=size; o.rotation_euler=(Vector((0,0,7))-o.location).to_track_quat('-Z','Y').to_euler()
bpy.ops.object.camera_add(location=(19,-27,19)); cam=bpy.context.object; cam.rotation_euler=(Vector((0,0,7.5))-cam.location).to_track_quat('-Z','Y').to_euler(); cam.data.type='ORTHO'; cam.data.ortho_scale=19; scene.camera=cam
scene.render.engine='CYCLES'; scene.render.resolution_x=1100; scene.render.resolution_y=1600; scene.render.resolution_percentage=100
