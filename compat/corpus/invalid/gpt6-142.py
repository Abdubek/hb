import bpy, math, random
from mathutils import Vector
bpy.ops.wm.read_factory_settings(use_empty=True)
random.seed(12)

def mat(name,c,rough=.6,metal=0):
    m=bpy.data.materials.new(name); m.diffuse_color=(*c,1); m.use_nodes=True
    p=m.node_tree.nodes.get('Principled BSDF'); p.inputs['Base Color'].default_value=(*c,1); p.inputs['Roughness'].default_value=rough; p.inputs['Metallic'].default_value=metal
    return m

def box(name,loc,size,m,bevel=0):
    bpy.ops.mesh.primitive_cube_add(size=1,location=loc); o=bpy.context.object; o.name=name; o.dimensions=size
    bpy.ops.object.transform_apply(location=False,rotation=False,scale=True); o.data.materials.append(m)
    if bevel:
        mod=o.modifiers.new('Edge softness','BEVEL'); mod.width=bevel; mod.segments=2
        o.modifiers.new('Weighted normals','WEIGHTED_NORMAL')
    return o

def rod(name,a,b,r,m):
    a,b=Vector(a),Vector(b); d=b-a
    bpy.ops.mesh.primitive_cylinder_add(vertices=10,radius=r,depth=d.length,location=(a+b)/2)
    o=bpy.context.object; o.name=name; o.rotation_euler=d.to_track_quat('Z','Y').to_euler(); o.data.materials.append(m); return o

def aim(o,p): o.rotation_euler=(Vector(p)-o.location).to_track_quat('-Z','Y').to_euler()
def area(name,loc,power,size,target):
    bpy.ops.object.light_add(type='AREA',location=loc); o=bpy.context.object; o.name=name; o.data.energy=power; o.data.size=size; aim(o,target)

stucco=mat('Warm cream render',(.77,.72,.61)); brick=mat('Terracotta brick',(.48,.22,.14)); concrete=mat('Pale balcony concrete',(.62,.64,.61))
metal=mat('Dark olive metalwork',(.13,.19,.16),.35,.65); glass=mat('Blue grey glazing',(.12,.26,.3),.19,.35)
wood=mat('Oiled cedar',(.46,.26,.105)); path=mat('Limestone paving',(.63,.61,.52)); earth=mat('Garden soil',(.16,.105,.065))
grass=mat('Lawn',(.25,.37,.13)); leaves=[mat('Leaves '+str(i),c) for i,c in enumerate(((.2,.36,.1),(.32,.44,.14),(.13,.29,.13)))]
flower=mat('Flowers',(.76,.39,.56)); dark=mat('Roof membrane',(.15,.18,.17)); glow=mat('Garden light glass',(.95,.81,.52))
p=glow.node_tree.nodes.get('Principled BSDF'); p.inputs['Emission Color'].default_value=(1,.73,.35,1); p.inputs['Emission Strength'].default_value=2

box('Site plinth',(0,0,-.33),(23,24,.65),concrete,.16)
box('Courtyard paving',(0,-.1,.025),(20,21,.12),path,.035)
# A three-storey U-shaped perimeter block opens toward the camera.
box('Rear residential wing',(0,7.6,4.65),(20,4.8,9.3),stucco,.045)
for x in (-8.1,8.1): box('Side residential wing',(x,-1.3,4.65),(3.8,13,9.3),stucco,.045)
box('Rear brick plinth',(0,5.16,.4),(20,.09,.8),brick)
for x in (-6.16,6.16): box('Side brick plinth',(x,-1.3,.4),(.09,13,.8),brick)
for z in (3.1,6.2,9.3):
    box('Rear floor band',(0,5.08,z),(20,.24,.16),concrete)
    for x in (-6.09,6.09): box('Side floor band',(x,-1.3,z),(.24,13,.16),concrete)
box('Rear flat roof',(0,7.6,9.34),(20,4.8,.12),dark)
for x in (-8.1,8.1): box('Side flat roof',(x,-1.3,9.34),(3.8,13,.12),dark)
for y in (5.12,10.03): box('Rear parapet',(0,y,9.59),(20.2,.18,.55),stucco,.025)
for x in (-10.04,10.04,-6.12,6.12): box('Side parapet',(x,-1.3,9.59),(.18,13,.55),stucco,.025)

# Facade coordinates allow the same detailed balcony to face into each wing.
def point(origin,u,v,z):
    x,y,angle=origin
    return (x+u*math.cos(angle)-v*math.sin(angle),y+u*math.sin(angle)+v*math.cos(angle),z)
def localbox(name,origin,u,v,z,size,m,bevel=0):
    o=box(name,point(origin,u,v,z),size,m,bevel); o.rotation_euler.z=origin[2]; return o

def apartment(origin,z,balcony=True):
    localbox('Window recess',origin,0,0,z+1.42,(2.25,.1,2.24),metal)
    localbox('Glazed living room doors',origin,0,-.065,z+1.42,(2.05,.055,2.06),glass)
    for u in (-1.04,0,1.04): localbox('Door mullion',origin,u,-.11,z+1.42,(.065,.065,2.12),metal)
    localbox('Door transom',origin,0,-.11,z+2.05,(2.12,.065,.055),metal)
    localbox('Window sill',origin,0,-.12,z+.3,(2.35,.28,.1),concrete)
    if balcony:
        localbox('Projecting balcony slab',origin,0,-.69,z+.13,(2.95,1.55,.22),concrete,.025)
        for u in (-1.39,1.39):
            rod('Balcony side top rail',point(origin,u,-.08,z+1.25),point(origin,u,-1.38,z+1.25),.035,metal)
        rod('Balcony front top rail',point(origin,-1.39,-1.38,z+1.25),point(origin,1.39,-1.38,z+1.25),.035,metal)
        for j in range(15):
            u=-1.38+j*2.76/14
            rod('Balcony front baluster',point(origin,u,-1.38,z+.25),point(origin,u,-1.38,z+1.25),.018,metal)
        for u in (-1.39,1.39):
            for v in (-.1,-.4,-.7,-1,-1.3): rod('Balcony return baluster',point(origin,u,v,z+.25),point(origin,u,v,z+1.25),.018,metal)
        localbox('Balcony planter',origin,.63,-1.12,z+.47,(.85,.36,.42),brick,.035)
        for j in range(3):
            bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=1,radius=.23,location=point(origin,.35+j*.26,-1.12,z+.75))
            bpy.context.object.data.materials.append(leaves[j]); bpy.context.object.name='Balcony planting'

for floor in range(3):
    z=floor*3.1
    for x in (-7.7,-3.85,0,3.85,7.7): apartment((x,5.12,0),z,floor>0)
    for y in (-5.5,-1.5,2.5):
        apartment((-6.15,y,math.pi/2),z,floor>0)
        apartment((6.15,y,-math.pi/2),z,floor>0)

# Open steel access stair at the front of the right wing, with two switchback storeys.
for base in (0,3.1):
    for flight in range(2):
        x=3.7 if flight==0 else 5.05; y0=-7.8 if flight==0 else -5.0; direction=1 if flight==0 else -1
        z0=base+flight*1.55
        for i in range(10):
            y=y0+direction*(i+.5)*.28; z=z0+(i+1)*.155
            box('External stair tread',(x,y,z-.045),(1.2,.29,.09),metal,.01)
        for dx in (-.56,.56):
            rod('Stair stringer',(x+dx,y0,z0-.05),(x+dx,y0+direction*2.8,z0+1.5),.065,metal)
            rod('Stair handrail',(x+dx,y0,z0+1.02),(x+dx,y0+direction*2.8,z0+2.57),.03,metal)
            for i in range(0,11,2):
                y=y0+direction*i*.28; z=z0+i*.155
                rod('Stair railing upright',(x+dx,y,z),(x+dx,y,z+1.02),.022,metal)
    box('Stair intermediate landing',(4.38,-4.62,base+1.49),(2.57,.8,.12),metal)
    box('Stair floor landing',(4.95,-8.15,base+3.04),(2.4,.8,.12),metal)
    rod('Landing guard',(3.75,-8.52,base+4.12),(6.12,-8.52,base+4.12),.032,metal)
    for x in (3.78,4.55,5.3,6.1): rod('Landing post',(x,-8.52,base+3.1),(x,-8.52,base+4.12),.024,metal)
for x in (3.1,5.65):
    for y in (-8.5,-4.25): rod('Stair support column',(x,y,.1),(x,y,6.2),.07,metal)

# Shared central garden with crossing paths, seating and trees.
for x in (-2.4,2.4):
    for y in (-2.4,1.3):
        box('Raised garden border',(x,y,.22),(3.55,2.7,.38),concrete,.065)
        box('Garden soil',(x,y,.425),(3.32,2.47,.08),earth,.025)
        box('Lawn inset',(x,y,.48),(3.16,2.32,.035),grass,.025)

def tree(x,y,height):
    rod('Tree trunk',(x,y,.45),(x,y,height),.12,wood)
    for j in range(5):
        a=j*math.tau/5; end=(x+.65*math.cos(a),y+.65*math.sin(a),height+.25)
        rod('Tree branch',(x,y,height-.65),end,.055,wood)
        bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=2,radius=.92,location=end)
        o=bpy.context.object; o.name='Garden tree crown'; o.scale=(1,1,.95); o.data.materials.append(leaves[j%3])
for x,y,h in ((-2.4,1.3,2.5),(2.4,1.3,2.8),(-2.6,-2.4,2.2)): tree(x,y,h)
for i in range(24):
    x=random.uniform(1,3.8); y=random.uniform(-3.4,-1.4)
    bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=1,radius=.16,location=(x,y,.64)); bpy.context.object.data.materials.append(leaves[i%3])
    if i%3==0:
        bpy.ops.mesh.primitive_uv_sphere_add(segments=8,ring_count=4,radius=.065,location=(x,y,.81)); bpy.context.object.data.materials.append(flower)
for x in (-2.4,2.4):
    for j in range(4): box('Bench seat slat',(x,-4.4+j*.105,.62),(2,.082,.09),wood,.015)
    for z in (.91,1.1): box('Bench back slat',(x,-4.45,z),(2,.09,.14),wood,.015)
    for dx in (-.75,.75):
        box('Bench leg',(x+dx,-4.2,.34),(.09,.42,.55),metal)
        rod('Bench back support',(x+dx,-4.46,.3),(x+dx,-4.46,1.2),.03,metal)
for x,y in ((-4.6,-5),(0,-5),(4.6,3),(-4.6,3)):
    box('Garden bollard',(x,y,.5),(.13,.13,.9),metal,.025)
    box('Bollard diffuser',(x,y,.89),(.15,.15,.16),glow,.02)

area('Courtyard daylight',(-9,-10,20),3300,12,(0,0,2)); area('Roof rim',(7,8,17),2200,9,(0,0,3))
bpy.ops.object.camera_add(location=(25,-34,26)); cam=bpy.context.object; aim(cam,(0,1,3)); cam.data.type='ORTHO'; cam.data.ortho_scale=32
scene=bpy.context.scene; scene.camera=cam; scene.render.engine='CYCLES'; scene.cycles.samples=64; scene.world.color=(.32,.32,.32)
scene.render.resolution_x=1500; scene.render.resolution_y=1250; scene.render.resolution_percentage=100; scene.view_settings.view_transform='AgX'
