import bpy, math
from mathutils import Vector
bpy.ops.wm.read_factory_settings(use_empty=True)

def mat(name,c,metal=0,rough=.4):
    m=bpy.data.materials.new(name); m.diffuse_color=(*c,1); m.use_nodes=True; s=m.node_tree.nodes.get('Principled BSDF'); s.inputs['Base Color'].default_value=(*c,1); s.inputs['Metallic'].default_value=metal; s.inputs['Roughness'].default_value=rough; return m
shell=mat('Painted pale steel',(.63,.72,.72),.5)
steel=mat('Rail galvanized metal',(.38,.44,.46),.8)
dark=mat('Gaskets',(.04,.055,.065),.2)
yellow=mat('Ladder yellow',(.95,.56,.035),.35)
base=mat('Concrete',(.3,.32,.32),0,.85)

def cube(name,p,d,m):
    bpy.ops.mesh.primitive_cube_add(size=1,location=p); o=bpy.context.object; o.name=name; o.dimensions=d; bpy.ops.object.transform_apply(location=False,rotation=False,scale=True); o.data.materials.append(m); b=o.modifiers.new('Edge rounding','BEVEL'); b.width=.025; b.segments=3; o.modifiers.new('Normals','WEIGHTED_NORMAL'); return o

def rod(name,a,b,r,m,n=32):
    a,b=Vector(a),Vector(b); d=b-a; bpy.ops.mesh.primitive_cylinder_add(vertices=n,radius=r,depth=d.length,location=(a+b)/2); o=bpy.context.object; o.name=name; o.rotation_mode='QUATERNION'; o.rotation_quaternion=d.to_track_quat('Z','Y'); o.data.materials.append(m)
    for f in o.data.polygons: f.use_smooth=len(f.vertices)==4
    return o

def line(name,pts,r,m):
    c=bpy.data.curves.new(name,'CURVE'); c.dimensions='3D'; c.bevel_depth=r; c.bevel_resolution=3; c.use_fill_caps=True; s=c.splines.new('POLY'); s.points.add(len(pts)-1)
    for p,v in zip(s.points,pts): p.co=(*v,1)
    o=bpy.data.objects.new(name,c); bpy.context.collection.objects.link(o); o.data.materials.append(m)

def ring(name,r,z,thickness,m):
    line(name,[(r*math.cos(k*math.tau/128),r*math.sin(k*math.tau/128),z) for k in range(129)],thickness,m)

rod('Circular foundation',(0,0,0),(0,0,.3),2.65,base,128)
rod('Tank bottom flange',(0,0,.3),(0,0,.43),2.18,steel,128)
rod('Cylindrical tank shell',(0,0,.4),(0,0,4.25),2.05,shell,128)
for z in (.47,1.65,2.9,4.22): ring('Circumferential welded seam',2.054,z,.014,steel)
# Shallow conical roof rises to its central vent.
bpy.ops.mesh.primitive_cone_add(vertices=128,radius1=2.08,radius2=.18,depth=.3,location=(0,0,4.4)); bpy.context.object.name='Sloped roof'; bpy.context.object.data.materials.append(shell)
for p in bpy.context.object.data.polygons: p.use_smooth=len(p.vertices)==4
ring('Roof edge',2.08,4.25,.05,steel)
rod('Roof vent',(0,0,4.53),(0,0,4.85),.13,steel)
bpy.ops.mesh.primitive_cone_add(vertices=48,radius1=.26,radius2=.06,depth=.12,location=(0,0,4.9)); bpy.context.object.name='Vent rain cap'; bpy.context.object.data.materials.append(steel)
# Access hatch and handle.
rod('Hatch neck',(.85,-.4,4.3),(.85,-.4,4.56),.4,steel,64)
rod('Hatch gasket',(.85,-.4,4.55),(.85,-.4,4.59),.43,dark,64)
rod('Hatch lid',(.85,-.4,4.59),(.85,-.4,4.64),.46,shell,64)
line('Hatch handle',[(.72,-.4,4.65),(.72,-.4,4.77),(.98,-.4,4.77),(.98,-.4,4.65)],.025,steel)
for k in range(8):
    a=k*math.tau/8; x=.85+.37*math.cos(a); y=-.4+.37*math.sin(a); rod('Hatch bolt',(x,y,4.63),(x,y,4.68),.035,steel,6)
# Guardrails have a ladder opening at the front.
start=-math.pi/2+.23; end=3*math.pi/2-.23
for z in (4.78,5.3): line('Roof safety rail',[(2.01*math.cos(start+(end-start)*i/120),2.01*math.sin(start+(end-start)*i/120),z) for i in range(121)],.028,steel)
for i in range(17):
    a=start+(end-start)*i/16; x=2.01*math.cos(a); y=2.01*math.sin(a); rod('Rail post',(x,y,4.25),(x,y,5.3),.032,steel)
for z in (4.34,4.4): line('Toe guard',[(2.015*math.cos(start+(end-start)*i/120),2.015*math.sin(start+(end-start)*i/120),z) for i in range(121)],.03,steel)
# Ladder climbs the near wall and extends into the roof opening.
for x in (-.37,.37):
    line('Ladder stile',[(x,-2.33,.32),(x,-2.33,4.85),(x,-2.25,5.25),(x,-1.98,5.3)],.045,yellow)
    for z in (.65,1.85,3.05,4.15): rod('Ladder wall bracket',(x,-2.32,z),(x,-1.99,z),.035,steel)
for i in range(15):
    z=.5+i*.275; rod('Non slip rung',(-.37,-2.33,z),(.37,-2.33,z),.028,steel)
# Protective ladder cage wraps around the outward side.
for z in (2.05,2.8,3.55,4.3):
    line('Ladder cage hoop',[(.62*math.cos(math.pi+i*math.pi/40),-2.22+.62*math.sin(math.pi+i*math.pi/40),z) for i in range(41)],.026,yellow)
for i in range(7):
    a=math.pi+i*math.pi/6; x=.62*math.cos(a); y=-2.22+.62*math.sin(a); rod('Cage vertical',(x,y,2.05),(x,y,4.3),.018,yellow)
rod('Drain nozzle',(1.2,-1.55,.85),(1.65,-2.17,.85),.12,steel)
rod('Drain flange',(1.59,-2.09,.85),(1.7,-2.24,.85),.22,steel)
for k in range(12):
    a=k*math.tau/12; x=2.22*math.cos(a); y=2.22*math.sin(a); cube('Anchor lug',(x,y,.43),(.22,.22,.13),steel); rod('Foundation anchor',(x,y,.45),(x,y,.59),.045,dark,6)
cube('Ground',(0,0,-.12),(200,200,.2),mat('Ground',(.12,.16,.19),0,.9))
scene=bpy.context.scene; scene.world.color=(.2,.2,.2)
for loc,power,size in [((4,-6,9),1900,5),((-5,-1,6),1400,5),((2,4,8),2000,4)]:
    bpy.ops.object.light_add(type='AREA',location=loc); o=bpy.context.object; o.data.energy=power; o.data.size=size; o.rotation_euler=(Vector((0,0,2.5))-o.location).to_track_quat('-Z','Y').to_euler()
bpy.ops.object.camera_add(location=(8,-11,8)); o=bpy.context.object; o.rotation_euler=(Vector((0,-.3,2.6))-o.location).to_track_quat('-Z','Y').to_euler(); o.data.type='ORTHO'; o.data.ortho_scale=8.4; scene.camera=o
scene.render.engine='CYCLES'; scene.render.resolution_x=1200; scene.render.resolution_y=1400; scene.render.resolution_percentage=100
