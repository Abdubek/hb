import bpy, math
from mathutils import Vector
bpy.ops.object.select_all(action='SELECT'); bpy.ops.object.delete(use_global=False)

def mat(name,c,rough=.45,metal=0):
    m=bpy.data.materials.new(name); m.diffuse_color=(*c,1); m.use_nodes=True; p=m.node_tree.nodes.get('Principled BSDF'); p.inputs['Base Color'].default_value=(*c,1); p.inputs['Roughness'].default_value=rough; p.inputs['Metallic'].default_value=metal; return m

def box(name,loc,size,m,bevel=.015):
    bpy.ops.mesh.primitive_cube_add(size=1,location=loc); o=bpy.context.object; o.name=name; o.dimensions=size; bpy.ops.object.transform_apply(location=False,rotation=False,scale=True); o.data.materials.append(m)
    if bevel: b=o.modifiers.new('Manufactured edge radius','BEVEL'); b.width=bevel; b.segments=3; o.modifiers.new('Normals','WEIGHTED_NORMAL')
    return o

def cyl(name,a,b,r,m,vertices=40):
    a=Vector(a); b=Vector(b); d=b-a; bpy.ops.mesh.primitive_cylinder_add(vertices=vertices,radius=r,depth=d.length,location=(a+b)/2); o=bpy.context.object; o.name=name; o.rotation_euler=d.to_track_quat('Z','Y').to_euler(); o.data.materials.append(m); be=o.modifiers.new('Edge bevel','BEVEL'); be.width=.006; be.segments=2; o.modifiers.new('Normals','WEIGHTED_NORMAL')
    for p in o.data.polygons: p.use_smooth=True
    return o

def tube(name,pts,r,m):
    c=bpy.data.curves.new(name,'CURVE'); c.dimensions='3D'; c.bevel_depth=r; c.bevel_resolution=3; s=c.splines.new('BEZIER'); s.bezier_points.add(len(pts)-1)
    for p,co in zip(s.bezier_points,pts): p.co=co; p.handle_left_type='AUTO'; p.handle_right_type='AUTO'
    o=bpy.data.objects.new(name,c); bpy.context.collection.objects.link(o); c.materials.append(m)

def torus(name,loc,major,minor,m,rotation=(0,0,0)):
    bpy.ops.mesh.primitive_torus_add(major_segments=48,minor_segments=12,location=loc,rotation=rotation,major_radius=major,minor_radius=minor); o=bpy.context.object; o.name=name; o.data.materials.append(m)
    for p in o.data.polygons: p.use_smooth=True
    return o

yellow=mat('Industrial yellow enamel',(.96,.53,.025),.33,.35); charcoal=mat('Graphite chassis',(.045,.057,.063),.45,.6); metal=mat('Machined steel',(.48,.54,.58),.27,.85); rubber=mat('Tire rubber',(.021,.026,.030),.85); seatmat=mat('Black vinyl seat',(.034,.041,.048),.6); white=mat('White markings',(.90,.92,.88),.6); amber=mat('Amber warning lens',(1,.24,.008),.23); red=mat('Rear red lenses',(.55,.012,.008),.22)
# Vehicle front is negative Y.
box('Main chassis',(0,.04,.52),(1.15,1.78,.32),charcoal,.075)
box('Rear rounded counterweight',(0,.71,.85),(1.24,.76,.72),yellow,.16)
box('Engine hood',(0,.51,1.16),(1.12,.73,.17),yellow,.055)
box('Rear bumper',(0,1.12,.48),(1.22,.14,.18),charcoal,.04)
box('Operator floor',(0,-.23,.73),(1.06,1.04,.10),charcoal,.03)
for side in [-1,1]:
    box('Yellow side sill',(side*.57,-.13,.64),(.13,.96,.24),yellow,.025)
    box('Entry step',(side*.69,-.07,.42),(.22,.49,.085),charcoal)
    for j in range(6): box('Step traction ridge',(side*.69,-.25+j*.073,.466),(.19,.013,.01),metal,.003)
# Four wheels: large front drive pair and smaller rear steer pair.
for y,r,width in [(-.65,.36,.25),(.73,.29,.21)]:
    cyl('Axle',(-.72,y,r),(.72,y,r),.075,charcoal)
    for side in [-1,1]:
        x=side*.64
        cyl('Solid industrial tire',(x-width/2,y,r),(x+width/2,y,r),r,rubber,64)
        outer=x+side*(width/2+.006)
        cyl('Painted wheel rim',(outer-side*.018,y,r),(outer,y,r),r*.60,yellow)
        cyl('Hub boss',(outer,y,r),(outer+side*.025,y,r),r*.25,metal)
        for j in range(6):
            a=j*math.tau/6; yy=y+math.sin(a)*r*.40; zz=r+math.cos(a)*r*.40
            cyl('Wheel lug bolt',(outer,yy,zz),(outer+side*.013,yy,zz),.014,charcoal,6)
        for j in range(32):
            a=j*math.tau/32; tread=box('Raised tire tread',(x,y+math.sin(a)*(r-.002),r+math.cos(a)*(r-.002)),(width*.92,.034,.014),rubber,.004); tread.rotation_euler.x=-a
for side in [-1,1]: box('Front wheel fender',(side*.57,-.63,.79),(.29,.77,.085),yellow,.025)
# Open operator station.
box('Seat pedestal',(0,.15,.91),(.45,.43,.29),charcoal,.04)
box('Seat cushion',(0,.10,1.10),(.56,.49,.14),seatmat,.065)
b=box('Seat back',(0,.35,1.37),(.56,.13,.49),seatmat,.06); b.rotation_euler.x=math.radians(8)
for x in [-.23,.23]: box('Seat side bolster',(x,.11,1.16),(.10,.43,.12),seatmat,.045)
box('Seat belt buckle',(.31,.19,1.13),(.065,.08,.05),red,.015)
box('Dashboard',(0,-.53,1.19),(.77,.24,.19),charcoal,.04)
steer0=Vector((-.16,-.57,.82)); steer1=Vector((-.16,-.37,1.39)); cyl('Steering column',steer0,steer1,.028,charcoal)
q=(steer1-steer0).to_track_quat('Z','Y'); torus('Steering wheel',steer1,.16,.016,charcoal,q.to_euler())
for i in range(3):
    a=i*math.tau/3; end=steer1+q@Vector((.145*math.cos(a),.145*math.sin(a),0)); cyl('Steering wheel spoke',steer1,end,.010,metal)
cyl('Steering hub',steer1-(steer1-steer0).normalized()*.015,steer1+(steer1-steer0).normalized()*.018,.038,charcoal)
for i in range(2):
    a=(.26+i*.10,-.31,.92); b=(.26+i*.10,-.25,1.25+i*.025); cyl('Hydraulic control lever',a,b,.010,metal)
    bpy.ops.mesh.primitive_uv_sphere_add(segments=16,ring_count=8,radius=.032,location=b); bpy.context.object.name='Control knob'; bpy.context.object.data.materials.append(charcoal)
for x in [-.15,.13]:
    o=box('Foot pedal',(x,-.51,.81),(.12,.19,.035),rubber,.008); o.rotation_euler.x=.3
# Overhead protective cage, with an open slatted roof.
for x in [-.49,.49]:
    for y in [-.65,.66]: box('Overhead guard upright',(x,y,1.52),(.065,.065,1.67),charcoal,.012)
    box('Roof side rail',(x,.0,2.37),(.075,1.47,.08),charcoal)
for y in [-.70,.70]: box('Roof end rail',(0,y,2.37),(1.05,.075,.08),charcoal)
for y in [-.48,-.24,0,.24,.48]: box('Overhead protective slat',(0,y,2.38),(.96,.055,.04),charcoal,.006)
cyl('Beacon mounting',(0,.47,2.40),(0,.47,2.45),.085,charcoal)
cyl('Amber rotating beacon',(0,.47,2.45),(0,.47,2.58),.069,amber)
# Twin channel mast, nested rails, crossmembers and hydraulic lift.
for x in [-.43,.43]:
    box('Outer mast channel web',(x,-.97,1.42),(.12,.10,2.52),charcoal)
    for y in [-1.045,-.895]: box('Mast channel flange',(x,y,1.42),(.17,.05,2.52),charcoal,.007)
    box('Sliding polished rail',(x,-1.07,1.43),(.068,.055,2.36),metal,.006)
for z in [.22,2.62]: box('Mast crossmember',(0,-.97,z),(.95,.15,.11),charcoal)
cyl('Lift hydraulic cylinder',(0,-.90,.29),(0,-.90,1.50),.067,charcoal)
cyl('Lift piston',(0,-.90,1.45),(0,-.90,2.43),.038,metal)
cyl('Lift chain sheave',(-.07,-.90,2.43),(.07,-.90,2.43),.10,metal)
for x in [-.17,.17]:
    for j in range(37): box('Lift chain link',(x,-1.055,.64+j*.049),(.024,.028,.039),metal,.005)
for side in [-1,1]: cyl('Mast tilt ram',(side*.43,-.35,.49),(side*.43,-.91,.78),.043,metal)
# Fork carriage and load backrest.
for z in [.43,.80]: box('Fork carriage crossbar',(0,-1.17,z),(1.09,.13,.12),charcoal)
for x in [-.51,.51]: box('Load backrest edge',(x,-1.15,1.08),(.055,.06,1.24),charcoal,.006)
for z in [.52,1.69]: box('Load backrest horizontal',(0,-1.15,z),(1.07,.06,.055),charcoal,.006)
for x in [-.34,-.17,0,.17,.34]: box('Load backrest vertical grille',(x,-1.15,1.10),(.027,.045,1.13),charcoal,.005)
# Two L-shaped forks with individually tapered toes.
for x in [-.32,.32]:
    box('Fork upright',(x,-1.28,.60),(.15,.10,.75),metal,.012)
    box('Fork heel',(x,-1.34,.255),(.15,.20,.14),metal,.014)
    verts=[(x-.075,-1.30,.20),(x+.075,-1.30,.20),(x+.065,-2.42,.20),(x-.065,-2.42,.20),(x-.075,-1.30,.30),(x+.075,-1.30,.30),(x+.065,-2.42,.225),(x-.065,-2.42,.225)]
    faces=[(0,3,2,1),(4,5,6,7),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7)]
    mesh=bpy.data.meshes.new('Tapered fork mesh'); mesh.from_pydata(verts,[],faces); mesh.update(); o=bpy.data.objects.new('Tapered load fork',mesh); bpy.context.collection.objects.link(o); mesh.materials.append(metal); b=o.modifiers.new('Fork edge radius','BEVEL'); b.width=.007; b.segments=2; o.modifiers.new('Normals','WEIGHTED_NORMAL')
tube('Hydraulic hose',[(-.14,-.86,.4),(-.21,-.80,1.4),(-.19,-.84,2.42),(0,-.86,2.53),(.19,-.84,2.42),(.21,-.85,1.40)],.012,rubber)
for side in [-1,1]:
    box('Headlamp housing',(side*.48,-.73,1.77),(.17,.10,.13),charcoal,.022); box('Headlamp lens',(side*.48,-.786,1.77),(.13,.012,.09),white,.015)
    box('Rear tail light',(side*.45,1.092,.94),(.15,.018,.09),red,.012)
    for j in range(6): box('Engine cooling vent',(side*.624,.50+j*.065,.91),(.008,.025,.23),charcoal,.009)
# Readable side fleet identification.
c=bpy.data.curves.new('Fleet lettering','FONT'); c.body='F-20'; c.align_x='CENTER'; c.align_y='CENTER'; c.size=.13; c.extrude=.001; c.materials.append(charcoal); o=bpy.data.objects.new('Fleet ID',c); bpy.context.collection.objects.link(o); o.location=(.625,.70,1.13); o.rotation_euler=(math.pi/2,0,math.pi/2)
floor=mat('Concrete floor',(.27,.29,.30),.9); box('Floor',(0,0,-.045),(200,200,.08),floor,0)
scene=bpy.context.scene; scene.world.use_nodes=True; scene.world.node_tree.nodes['Background'].inputs[1].default_value=.35
for loc,energy,size in [((3,-4,6),1400,4),((-4,-2,3),850,3),((2,4,5),1400,3)]:
    bpy.ops.object.light_add(type='AREA',location=loc); o=bpy.context.object; o.data.energy=energy; o.data.size=size; o.rotation_euler=(Vector((0,-.3,1))-o.location).to_track_quat('-Z','Y').to_euler()
bpy.ops.object.camera_add(location=(5,-7,4)); cam=bpy.context.object; cam.rotation_euler=(Vector((0,-.5,1.16))-cam.location).to_track_quat('-Z','Y').to_euler(); cam.data.type='ORTHO'; cam.data.ortho_scale=4.9; scene.camera=cam
scene.render.engine='CYCLES'; scene.cycles.samples=64; scene.render.resolution_x=1400; scene.render.resolution_y=1200; scene.render.resolution_percentage=100
