import bpy, math
from mathutils import Vector
bpy.ops.object.select_all(action='SELECT'); bpy.ops.object.delete(use_global=False)

def mat(name,c,metal=0,rough=.5):
    m=bpy.data.materials.new(name); m.diffuse_color=(*c,1); m.use_nodes=True; p=m.node_tree.nodes['Principled BSDF']; p.inputs['Base Color'].default_value=(*c,1); p.inputs['Metallic'].default_value=metal; p.inputs['Roughness'].default_value=rough; return m
concrete=mat('Warm ivory concrete',(.66,.67,.63)); steel=mat('Graphite structure',(.07,.10,.12),.65,.3); silver=mat('Platform galvanized steel',(.45,.52,.55),.7,.32)
glass=mat('Blue cab glazing',(.12,.34,.42),.20,.17); glass.node_tree.nodes['Principled BSDF'].inputs['Transmission Weight'].default_value=.38
roof=mat('Roof enamel',(.75,.77,.72),.45,.3); yellow=mat('Safety yellow',(.95,.58,.06)); asphalt=mat('Apron',(.18,.21,.22)); grass=mat('Airfield grass',(.28,.36,.17)); red=mat('Beacon red',(.7,.015,.01))
red.node_tree.nodes['Principled BSDF'].inputs['Emission Color'].default_value=(1,.025,.01,1); red.node_tree.nodes['Principled BSDF'].inputs['Emission Strength'].default_value=3

def box(name,loc,size,m,bev=0):
    bpy.ops.mesh.primitive_cube_add(size=1,location=loc); o=bpy.context.object; o.name=name; o.dimensions=size; bpy.ops.object.transform_apply(location=False,rotation=False,scale=True); o.data.materials.append(m)
    if bev:
        b=o.modifiers.new('Edge bevel','BEVEL'); b.width=bev; b.segments=2; o.modifiers.new('Weighted normals','WEIGHTED_NORMAL')
    return o

def cyl(name,loc,r,depth,m,n=48,r2=None):
    bpy.ops.mesh.primitive_cone_add(vertices=n,radius1=r,radius2=r if r2 is None else r2,depth=depth,location=loc); o=bpy.context.object; o.name=name; o.data.materials.append(m); return o

def beam(name,a,b,r,m):
    a,b=Vector(a),Vector(b); o=cyl(name,(a+b)/2,r,(b-a).length,m,12); o.rotation_euler=(b-a).to_track_quat('Z','Y').to_euler(); return o

def ring(name,ri,ro,z,thick,m,n=64):
    vs=[]
    for zz in (z-thick,z):
        for r in (ri,ro): vs.extend([(r*math.cos(i*math.tau/n),r*math.sin(i*math.tau/n),zz) for i in range(n)])
    fs=[]
    for i in range(n):
        j=(i+1)%n; fs.extend([(i,j,n+j,n+i),(2*n+i,3*n+i,3*n+j,2*n+j),(i,2*n+i,2*n+j,j),(n+i,n+j,3*n+j,3*n+i)])
    me=bpy.data.meshes.new(name); me.from_pydata(vs,[],fs); me.update(); o=bpy.data.objects.new(name,me); bpy.context.collection.objects.link(o); o.data.materials.append(m)

def rail(radius,z):
    for i in range(24):
        t=i*math.tau/24; x,y=radius*math.cos(t),radius*math.sin(t); beam('Platform railing post',(x,y,z),(x,y,z+1.05),.035,silver)
        t2=(i+1)*math.tau/24
        for dz in (.5,1.05): beam('Platform perimeter rail',(x,y,z+dz),(radius*math.cos(t2),radius*math.sin(t2),z+dz),.028,silver)

box('Airfield base',(0,0,-.32),(28,26,.6),grass,.2); box('Service apron',(0,0,.015),(17,17,.08),asphalt,.15)
box('Tower foundation',(0,0,.22),(5.6,5.6,.4),concrete,.10)
cyl('Tapered octagonal tower shaft',(0,0,6.05),2.15,11.7,concrete,8,1.70)
# Narrow service windows on the front shaft face, set outward from the octagonal skin.
for z in (3.0,5.7,8.4):
    box('Window surround',(0,-1.94+(z-3)*.035,z),(.7,.14,1.30),steel,.045)
    box('Shaft window',(0,-2.02+(z-3)*.035,z),(.51,.05,1.08),glass,.025)
box('Ground service annex',(3.2,1.25,1.5),(3.6,4.7,3),concrete,.10); box('Annex roof coping',(3.2,1.25,3.06),(3.85,4.95,.18),roof,.055)
box('Entry door',(3.3,-1.12,1.15),(1.15,.11,2.3),steel,.025)
box('Door vision panel',(3.3,-1.19,1.52),(.72,.04,.69),glass,.015)
for i in range(9): box('Annex ventilation louver',(5.025,.8,1+i*.115),(.08,1.5,.045),silver)
# Lower mechanical service platform and upper cab catwalk.
ring('Mechanical service platform',1.65,2.85,8.7,.20,silver); rail(2.8,8.7)
ring('Cab exterior catwalk',1.55,3.72,11.6,.24,silver); rail(3.65,11.6)
for i in range(8):
    t=i*math.tau/8
    beam('Catwalk diagonal support',(1.6*math.cos(t),1.6*math.sin(t),10.15),(3.35*math.cos(t),3.35*math.sin(t),11.38),.075,steel)
cyl('Cab lower solid drum',(0,0,11.95),2.67,.70,steel,8,2.79)
# Splayed panoramic glazing, each pane is a solid mesh panel.
n=8; offset=math.pi/8
for i in range(n):
    a=offset+i*math.tau/n; b=offset+(i+1)*math.tau/n
    vs=[(2.79*math.cos(a),2.79*math.sin(a),12.3),(2.79*math.cos(b),2.79*math.sin(b),12.3),(3.13*math.cos(b),3.13*math.sin(b),14.45),(3.13*math.cos(a),3.13*math.sin(a),14.45)]
    me=bpy.data.meshes.new('Cab pane'); me.from_pydata(vs,[],[(0,1,2,3)]); me.update(); o=bpy.data.objects.new('Panoramic glazed cab panel',me); bpy.context.collection.objects.link(o); o.data.materials.append(glass); s=o.modifiers.new('Glazing thickness','SOLIDIFY'); s.thickness=.035
    beam('Sloping cab mullion',vs[0],vs[3],.065,steel)
    beam('Window lower frame',vs[0],vs[1],.06,steel); beam('Window upper frame',vs[3],vs[2],.06,steel)
    p=Vector(vs[0]).lerp(Vector(vs[1]),.5); q=Vector(vs[3]).lerp(Vector(vs[2]),.5); beam('Fine intermediate mullion',p,q,.025,silver)
cyl('Broad octagonal roof',(0,0,14.57),3.58,.25,roof,8,3.58)
cyl('Roof raised cap',(0,0,14.80),2.6,.22,steel,8,2.5)
# Interior consoles and operator seats are visible through the glazing.
for x in (-1.2,0,1.2):
    box('Control console',(x,-1.25,12.65),(.95,.65,.7),steel,.07)
    o=box('Radar display',(x,-1.35,13.13),(.68,.12,.43),glass,.025); o.rotation_euler[0]=-.25
    cyl('Operator stool',(x,-.3,12.8),.28,.12,steel,24); beam('Stool stem',(x,-.3,12.2),(x,-.3,12.75),.05,silver)
# Ladder on the rear of the shaft, connecting service levels.
for x in (-.35,.35): beam('Service ladder rail',(x,2.05,3.2),(x,2.05,11.7),.045,steel)
for i in range(28): beam('Ladder rung',(-.35,2.05,3.3+i*.3),(.35,2.05,3.3+i*.3),.03,silver)
beam('Roof antenna mast',(0,0,14.9),(0,0,18),.065,silver)
for z in (16.1,16.5,16.9): beam('Radio antenna cross element',(-.65,0,z),(.65,0,z),.022,silver)
cyl('Obstruction beacon',(0,0,18.08),.13,.22,red,24)
beam('Secondary aerial',(1.35,.5,14.85),(1.35,.5,16.6),.035,silver)
for x in (-5.8,5.8):
    for y in (-5,-3,-1): cyl('Safety bollard',(x,y,.5),.10,1,yellow,16)
scene=bpy.context.scene; scene.render.engine='CYCLES'; scene.cycles.samples=64; scene.world.color=(.34,.38,.42)
bpy.ops.object.light_add(type='AREA',location=(5,-10,22)); bpy.context.object.data.energy=2400; bpy.context.object.data.size=10
bpy.ops.object.light_add(type='SUN'); bpy.context.object.rotation_euler=(.4,-.5,-.4); bpy.context.object.data.energy=2.3; bpy.context.object.data.angle=.12
bpy.ops.object.camera_add(location=(24,-31,22)); cam=bpy.context.object; cam.rotation_euler=(Vector((0,0,8.2))-cam.location).to_track_quat('-Z','Y').to_euler(); cam.data.type='ORTHO'; cam.data.ortho_scale=26; scene.camera=cam
scene.render.resolution_x=1200; scene.render.resolution_y=1500; scene.render.resolution_percentage=100
