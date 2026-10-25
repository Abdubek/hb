import bpy, math
from mathutils import Vector
bpy.ops.object.select_all(action='SELECT'); bpy.ops.object.delete(use_global=False)

def mat(name,c,metal=0,rough=.6):
    m=bpy.data.materials.new(name); m.diffuse_color=(*c,1); m.use_nodes=True; p=m.node_tree.nodes['Principled BSDF']; p.inputs['Base Color'].default_value=(*c,1); p.inputs['Metallic'].default_value=metal; p.inputs['Roughness'].default_value=rough; return m
concrete=mat('Pale cast concrete',(.58,.59,.57)); dark=mat('Asphalt',(.09,.105,.11)); steel=mat('Galvanized horizontal barriers',(.43,.49,.51),.75,.28)
yellow=mat('Safety ochre',(.96,.58,.07)); white=mat('Road markings',(.90,.9,.84)); blue=mat('Wayfinding blue',(.035,.20,.36)); glass=mat('Car glazing',(.04,.10,.14),.35,.2)
red=mat('Terracotta vehicle',(.55,.12,.07),.4,.3); teal=mat('Teal vehicle',(.025,.31,.33),.45,.28); tire=mat('Tires',(.025,.03,.032)); ground=mat('Site paving',(.28,.30,.29))

def box(name,loc,size,m,bev=0):
    bpy.ops.mesh.primitive_cube_add(size=1,location=loc); o=bpy.context.object; o.name=name; o.dimensions=size; bpy.ops.object.transform_apply(location=False,rotation=False,scale=True); o.data.materials.append(m)
    if bev:
        b=o.modifiers.new('Edge chamfer','BEVEL'); b.width=bev; b.segments=2; o.modifiers.new('Normals','WEIGHTED_NORMAL')
    return o

def beam(name,a,b,width,depth,m):
    a,b=Vector(a),Vector(b); o=box(name,(a+b)/2,(width,depth,(b-a).length),m,.018); o.rotation_euler=(b-a).to_track_quat('Z','Y').to_euler(); return o

def text(name,body,loc,size,m):
    c=bpy.data.curves.new(name,'FONT'); c.body=body; c.align_x='CENTER'; c.size=size; c.extrude=.004; o=bpy.data.objects.new(name,c); bpy.context.collection.objects.link(o); o.location=loc; o.rotation_euler=(math.pi/2,0,0); o.data.materials.append(m)

box('Urban site',(0,1,-.3),(39,26,.5),ground,.15)
# Four parking decks; rear lane is reserved for alternating ramps.
for level in range(4):
    z=level*3.3
    box('Main floor slab %d'%level,(0,-1,z-.18),(27,9,.36),concrete,.045)
    box('Parking surface %d'%level,(0,-1,z+.012),(26.7,8.7,.025),dark)
    # Ramp landings at either end connect to the main deck.
    for x in (-11.9,11.9): box('Rear ramp landing',(x,5.5,z-.18),(3.2,4,.36),concrete,.025)
    for x in (-12,-6,0,6,12):
        for y in (-5,3):
            if level<3:
                box('Rectangular structural column',(x,y,z+1.47),(.55,.55,3.3),concrete,.045)
                box('Yellow column foot',(x,y,z+.34),(.58,.58,.65),yellow,.025)
        box('Facade barrier post',(x,-5.46,z+.7),(.105,.13,1.4),steel,.012)
    box('Front structural spandrel',(0,-5.05,z-.08),(27,.4,.52),concrete,.025)
    for rail_z in (.45,.85,1.23):
        box('Continuous horizontal safety rail',(0,-5.47,z+rail_z),(27,.13,.16),steel,.022)
    for side in (-13.35,13.35):
        for y in (-4,-1,2,5,7): box('End barrier post',(side,y,z+.66),(.12,.12,1.32),steel)
        for rz in (.45,.85,1.23): box('End horizontal safety rail',(side,1,z+rz),(.13,13,.16),steel,.015)
    for x in (-10.6,-7.8,-5,-2.2,.6,3.4,6.2,9):
        box('Parking bay line',(x,-2.15,z+.033),(.075,4.5,.015),white)
    box('Drive lane dashed marking',(0,1.1,z+.035),(2,.08,.018),white)
    for x in (-9,-6,-3,3,6,9): box('Drive lane dash',(x,1.1,z+.035),(1.25,.08,.018),white)
    box('Level number panel',(-12,-5.58,z+1.35),(.9,.10,.75),blue,.04)
    text('Level number',str(level+1),(-12,-5.645,z+1.10),.56,white)
# Alternating full-length rear ramps connect consecutive floors.
for level in range(3):
    z=level*3.3; direction=1 if level%2==0 else -1
    a=Vector((-10.3*direction,5.5,z)); b=Vector((10.3*direction,5.5,z+3.3)); mid=(a+b)/2
    run=b-a; ramp=box('Inclined concrete ramp',mid-Vector((0,0,.13)),(run.length,4,.26),concrete,.025); ramp.rotation_euler[1]=-math.atan2(run.z,run.x) if direction==1 else math.atan2(run.z,-run.x)
    # Surface and rails are defined from endpoints to retain exact slope.
    for side in (-1,1):
        aa=a+Vector((0,side*1.93,.65)); bb=b+Vector((0,side*1.93,.65))
        beam('Ramp crash barrier',aa,bb,.16,.48,steel)
        beam('Ramp handrail',aa+Vector((0,0,.55)),bb+Vector((0,0,.55)),.08,.08,steel)
        for j in range(9):
            p=a.lerp(b,j/8)+Vector((0,side*1.93,0)); beam('Ramp railing upright',p,p+Vector((0,0,1.25)),.09,.09,steel)
    for j in range(10):
        p=a.lerp(b,(j+.5)/10)+Vector((0,0,.015)); o=box('Ramp center dash',p,(1,.09,.02),yellow); o.rotation_euler[1]=-direction*math.atan(3.3/20.6)
# Compact stylized parked cars establish scale and depth.
def car(x,y,z,m):
    box('Car body',(x,y,z+.57),(1.75,3.65,.70),m,.20)
    box('Dark cabin glass',(x,y-.15,z+1.12),(1.50,1.92,.65),glass,.18)
    box('Car roof',(x,y-.13,z+1.46),(1.43,1.60,.08),m,.05)
    for sx in (-.86,.86):
        for dy in (-1.13,1.13):
            bpy.ops.mesh.primitive_cylinder_add(vertices=20,radius=.34,depth=.19,location=(x+sx,y+dy,z+.35),rotation=(0,math.pi/2,0)); bpy.context.object.data.materials.append(tire)
    for sx in (-.58,.58): box('Headlight',(x+sx,y-1.83,z+.63),(.38,.035,.17),white,.035)
for level in range(4):
    for j,x in enumerate((-9.2,-3.6,4.8,10.4)):
        if (level+j)%3!=0: car(x,-2.1,level*3.3+.035,teal if j%2 else red)
box('Parking entrance sign',(0,-5.65,11.27),(8,.20,.82),blue,.05); text('Parking title','P  /  CITY PARK',(0,-5.77,11.02),.51,white)
for x in (-15.5,15.5):
    box('Entry bollard',(x,-7,.55),(.18,.18,1.1),yellow,.025)
scene=bpy.context.scene; scene.render.engine='CYCLES'; scene.cycles.samples=64; scene.world.color=(.3,.3,.3)
bpy.ops.object.light_add(type='AREA',location=(0,-12,22)); bpy.context.object.data.energy=3000; bpy.context.object.data.size=14
bpy.ops.object.light_add(type='SUN'); bpy.context.object.rotation_euler=(.45,-.4,-.35); bpy.context.object.data.energy=2.5; bpy.context.object.data.angle=.15
bpy.ops.object.camera_add(location=(32,-35,25)); cam=bpy.context.object; cam.rotation_euler=(Vector((0,1,4))-cam.location).to_track_quat('-Z','Y').to_euler(); cam.data.type='ORTHO'; cam.data.ortho_scale=43; scene.camera=cam
scene.render.resolution_x=1500; scene.render.resolution_y=1100; scene.render.resolution_percentage=100
