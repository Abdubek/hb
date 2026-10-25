import bpy, math, random
from mathutils import Vector
bpy.ops.wm.read_factory_settings(use_empty=True)
random.seed(54)

def mat(name,c,metal=0,rough=.4):
    m=bpy.data.materials.new(name); m.diffuse_color=(*c,1); m.use_nodes=True; s=m.node_tree.nodes.get('Principled BSDF'); s.inputs['Base Color'].default_value=(*c,1); s.inputs['Metallic'].default_value=metal; s.inputs['Roughness'].default_value=rough; return m
gold=mat('Gold thermal blanket',(.64,.37,.055),.8,.32)
silver=mat('Machined aluminum',(.57,.64,.71),.85,.25)
dark=mat('Graphite',(.03,.04,.055),.5)
white=mat('Ceramic white',(.81,.85,.87),.2)
cells=[mat('Photovoltaic '+str(i),(.015+.004*i,.035+.008*i,.14+.025*i),.65,.24) for i in range(4)]
# Procedural foil detail uses only Blender nodes.
nt=gold.node_tree; noise=nt.nodes.new('ShaderNodeTexNoise'); noise.inputs['Scale'].default_value=24; noise.inputs['Detail'].default_value=3; bump=nt.nodes.new('ShaderNodeBump'); bump.inputs['Strength'].default_value=.22; bump.inputs['Distance'].default_value=.055; nt.links.new(noise.outputs['Fac'],bump.inputs['Height']); nt.links.new(bump.outputs['Normal'],nt.nodes.get('Principled BSDF').inputs['Normal'])

def box(name,p,d,m,bevel=.025):
    bpy.ops.mesh.primitive_cube_add(size=1,location=p); o=bpy.context.object; o.name=name; o.dimensions=d; bpy.ops.object.transform_apply(location=False,rotation=False,scale=True); o.data.materials.append(m)
    if bevel:
        b=o.modifiers.new('Edge bevel','BEVEL'); b.width=bevel; b.segments=2; o.modifiers.new('Weighted normals','WEIGHTED_NORMAL')
    return o

def rod(name,a,b,r,m,n=32):
    a,b=Vector(a),Vector(b); d=b-a; bpy.ops.mesh.primitive_cylinder_add(vertices=n,radius=r,depth=d.length,location=(a+b)/2); o=bpy.context.object; o.name=name; o.rotation_mode='QUATERNION'; o.rotation_quaternion=d.to_track_quat('Z','Y'); o.data.materials.append(m)
    for f in o.data.polygons: f.use_smooth=len(f.vertices)==4
    return o

def path(name,pts,r,m):
    c=bpy.data.curves.new(name,'CURVE'); c.dimensions='3D'; c.bevel_depth=r; c.bevel_resolution=3; s=c.splines.new('POLY'); s.points.add(len(pts)-1)
    for p,v in zip(s.points,pts): p.co=(*v,1)
    o=bpy.data.objects.new(name,c); bpy.context.collection.objects.link(o); o.data.materials.append(m)

box('Satellite bus',(0,0,0),(1.65,1.45,1.85),gold,.09)
for x in (-.84,.84):
    for y in (-.74,.74): box('Structural corner rail',(x,y,0),(.065,.065,1.96),silver,.012)
for z in (-.96,.96): box('Equipment deck',(0,0,z),(1.8,1.6,.09),silver)
box('Front radiator',(0,-.754,.05),(1.25,.045,1.3),white)
for x in [-.52+i*.13 for i in range(9)]: box('Radiator channel',(x,-.785,.05),(.024,.015,1.18),silver,.004)
for x in (-.69,.69):
    for z in (-.73,.73): rod('Panel fastener',(x,-.75,z),(x,-.795,z),.035,silver,6)
# Two articulated wings, each divided into three framed modules.
for side in (-1,1):
    rod('Array deployment axle',(side*.83,0,.05),(side*1.58,0,.05),.09,silver)
    rod('Rotary hinge',(side*1.2,-.16,.05),(side*1.2,.16,.05),.16,dark)
    for module in range(3):
        cx=side*(2.3+module*1.52)
        box('Solar panel substrate',(cx,0,.05),(1.44,2.7,.065),dark,.012)
        for dx in (-.72,.72): box('Array side frame',(cx+dx,0,.083),(.035,2.74,.075),silver,.005)
        for y in (-1.35,1.35): box('Array end frame',(cx,y,.083),(1.46,.035,.075),silver,.005)
        for ix in range(6):
            for iy in range(10):
                x=cx-.585+ix*.234; y=-1.18+iy*.262
                box('Individual solar cell',(x,y,.092),(.219,.246,.012),random.choice(cells),.006)
                for dx in (-.05,.05): box('Cell busbar',(x+dx,y,.100),(.004,.238,.003),silver,0)
        if module<2:
            xx=side*(3.06+module*1.52)
            for y in (-.95,.95): rod('Interpanel hinge',(xx,y-.1,.06),(xx,y+.1,.06),.06,silver)
    rod('Wing diagonal brace',(side*.85,.58,-.5),(side*1.6,.6,.035),.035,silver)
# Parabolic dish in local coordinates, tilted toward the camera.
center=Vector((0,-.1,1.35)); axis=Vector((0,-.48,.88)).normalized(); q=axis.to_track_quat('Z','Y')
def world(v): return center+q@Vector(v)
rod('Dish support mast',(0,0,.97),center,.12,silver)
R=.95; depth=.30; segments=96; rings=16
verts=[world((0,0,0))]; faces=[]
for j in range(1,rings+1):
    r=R*j/rings
    for i in range(segments):
        a=i*math.tau/segments; verts.append(world((r*math.cos(a),r*math.sin(a),depth*(r/R)**2)))
for i in range(segments): faces.append((0,1+i,1+(i+1)%segments))
for j in range(rings-1):
    a=1+j*segments; b=a+segments
    for i in range(segments): k=(i+1)%segments; faces.append((a+i,b+i,b+k,a+k))
me=bpy.data.meshes.new('Parabolic reflector mesh'); me.from_pydata(verts,[],faces); me.update(); o=bpy.data.objects.new('High gain antenna reflector',me); bpy.context.collection.objects.link(o); o.data.materials.append(white)
for p in me.polygons: p.use_smooth=True
s=o.modifiers.new('Reflector shell thickness','SOLIDIFY'); s.thickness=.025
path('Reflector rolled rim',[world((R*math.cos(i*math.tau/96),R*math.sin(i*math.tau/96),depth)) for i in range(97)],.025,silver)
focal=R*R/(4*depth)
for i in range(3):
    a=i*math.tau/3; rod('Feed support strut',world((.88*math.cos(a),.88*math.sin(a),.26)),world((0,0,focal+.07)),.018,silver)
rod('Antenna feed',world((0,0,focal-.055)),world((0,0,focal+.16)),.085,gold)
for i in range(8):
    a=i*math.tau/8; path('Reflector back rib',[world((R*j/16*math.cos(a),R*j/16*math.sin(a),depth*(j/16)**2-.034)) for j in range(17)],.012,silver)
# Thrusters, optical sensor and telemetry antenna.
for x in (-.67,.67):
    for y in (-.52,.52):
        rod('Thruster mount',(x,y,-.92),(x,y,-1.1),.115,silver)
        bpy.ops.mesh.primitive_cone_add(vertices=40,radius1=.17,radius2=.075,depth=.24,location=(x,y,-1.2)); bpy.context.object.name='Thruster bell'; bpy.context.object.data.materials.append(dark)
        rod('Thruster outlet',(x,y,-1.325),(x,y,-1.334),.135,black if 'black' in globals() else dark)
rod('Star tracker housing',(.46,.74,.52),(.46,1.02,.52),.16,dark)
rod('Star tracker lens',(.46,1.025,.52),(.46,1.034,.52),.125,cells[2])
rod('Telemetry mast',(.67,.5,.98),(.67,.5,2.65),.018,silver)
for z in (2.25,2.55): rod('Telemetry cross element',(.4,.5,z),(.94,.5,z),.012,silver)
scene=bpy.context.scene; scene.world.use_nodes=True; scene.world.node_tree.nodes.get('Background').inputs['Color'].default_value=(.012,.02,.045,1); scene.world.node_tree.nodes.get('Background').inputs['Strength'].default_value=.3
for loc,power,size in [((1,-5,8),1900,5),((-5,-1,3),1400,4),((3,5,5),2300,4)]:
    bpy.ops.object.light_add(type='AREA',location=loc); o=bpy.context.object; o.data.energy=power; o.data.size=size; o.rotation_euler=(-o.location).to_track_quat('-Z','Y').to_euler()
bpy.ops.object.camera_add(location=(7,-11,8)); o=bpy.context.object; o.rotation_euler=(Vector((0,0,.4))-o.location).to_track_quat('-Z','Y').to_euler(); o.data.type='ORTHO'; o.data.ortho_scale=13.6; scene.camera=o
scene.render.engine='CYCLES'; scene.render.resolution_x=1600; scene.render.resolution_y=1000; scene.render.resolution_percentage=100
