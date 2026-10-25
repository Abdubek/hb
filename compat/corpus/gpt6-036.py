import bpy, math
from mathutils import Vector
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)

def mat(name, color, metal=0, rough=.4):
    m=bpy.data.materials.new(name); m.diffuse_color=(*color,1); m.use_nodes=True
    p=m.node_tree.nodes.get('Principled BSDF'); p.inputs['Base Color'].default_value=(*color,1); p.inputs['Metallic'].default_value=metal; p.inputs['Roughness'].default_value=rough
    return m

def finish(o,name,m,bevel=0):
    o.name=name; o.data.materials.append(m)
    if bevel:
        mod=o.modifiers.new('Soft manufactured edges','BEVEL'); mod.width=bevel; mod.segments=3
        o.modifiers.new('Weighted normals','WEIGHTED_NORMAL')
    return o

def box(name,loc,size,m,bevel=.03):
    bpy.ops.mesh.primitive_cube_add(size=1,location=loc); o=bpy.context.object; o.dimensions=size
    bpy.ops.object.transform_apply(location=False,rotation=False,scale=True)
    return finish(o,name,m,bevel)

def rod(name,a,b,r,m,vertices=48):
    a,b=Vector(a),Vector(b); d=b-a
    bpy.ops.mesh.primitive_cylinder_add(vertices=vertices,radius=r,depth=d.length,location=(a+b)/2)
    o=bpy.context.object; o.rotation_euler=d.to_track_quat('Z','Y').to_euler()
    finish(o,name,m,.012)
    for f in o.data.polygons: f.use_smooth=len(f.vertices)==4
    return o

def beam(name,a,b,w,h,m):
    a,b=Vector(a),Vector(b); d=b-a
    o=box(name,(a+b)/2,(w,h,d.length),m,.05); o.rotation_euler=d.to_track_quat('Z','Y').to_euler(); return o

def cable(name,points,r,m):
    c=bpy.data.curves.new(name,'CURVE'); c.dimensions='3D'; c.bevel_depth=r; c.bevel_resolution=3
    s=c.splines.new('BEZIER'); s.bezier_points.add(len(points)-1)
    for p,co in zip(s.bezier_points,points): p.co=co; p.handle_left_type='AUTO'; p.handle_right_type='AUTO'
    o=bpy.data.objects.new(name,c); bpy.context.collection.objects.link(o); o.data.materials.append(m)

black=mat('Graphite powder coat',(.045,.052,.064),.65,.28)
rubber=mat('Soft black rubber',(.012,.016,.021),0,.7)
silver=mat('Brushed aluminum',(.48,.54,.59),.85,.24)
wood=mat('Warm oak desktop',(.40,.235,.115),0,.48)
glass=mat('Dark blue display glass',(.012,.045,.082),.25,.2)
blue=mat('Interface blue',(.035,.32,.53),.15,.3)
white=mat('Interface pale gray',(.43,.62,.70),.1,.4)
led=mat('Power light',(.1,.65,.8),0,.25)
led.node_tree.nodes.get('Principled BSDF').inputs['Emission Color'].default_value=(.05,.7,1,1)
led.node_tree.nodes.get('Principled BSDF').inputs['Emission Strength'].default_value=2

box('Desktop',(0,.1,.91),(6.2,3.1,.20),wood,.065)
for x in (-2.65,2.65):
    for y in (-1.05,1.2): box('Desk leg',(x,y,.4),(.12,.12,.82),black,.02)
# Rear-edge C clamp: top jaw, outside spine, underside jaw and screw.
box('Clamp top jaw',(1.75,1.32,1.06),(.64,.60,.10),black)
box('Clamp protective pad',(1.75,1.28,1.016),(.53,.40,.025),rubber,.008)
box('Clamp outside spine',(1.75,1.76,.80),(.48,.15,.59),black)
box('Clamp bottom jaw',(1.75,1.43,.54),(.48,.71,.11),black)
rod('Clamp screw',(1.75,1.26,.36),(1.75,1.26,.77),.045,silver)
rod('Clamp pressure foot',(1.75,1.26,.75),(1.75,1.26,.81),.145,black)
rod('Clamp T bar',(1.51,1.26,.38),(1.99,1.26,.38),.025,silver)
rod('Mount upright',(1.75,1.30,1.10),(1.75,1.30,2.64),.105,black)
rod('Height adjustment collar',(1.75,1.30,2.29),(1.75,1.30,2.48),.16,silver)
rod('Collar lock',(1.87,1.30,2.39),(2.03,1.30,2.39),.057,black)
a=(1.75,1.30,2.53); b=(2.13,.64,3.20); c=(.40,.49,3.55)
beam('Lower articulated link',a,b,.22,.27,black)
beam('Upper articulated link',b,c,.24,.30,black)
beam('Upper aluminum inset',(2.03,.455,3.22),(.48,.335,3.54),.075,.035,silver)
rod('Gas spring piston',(1.83,1.16,2.62),(2.06,.73,3.06),.066,silver)
for i,p in enumerate((a,b,c)):
    rod('Hinge body '+str(i),(p[0],p[1]-.20,p[2]),(p[0],p[1]+.20,p[2]),.17,black)
    rod('Hinge bolt '+str(i),(p[0],p[1]-.225,p[2]),(p[0],p[1]-.203,p[2]),.07,silver,6)
rod('Tilt coupling',(.40,.49,3.55),(.40,.22,3.55),.11,silver)
box('VESA mounting plate',(.40,.235,3.55),(.68,.075,.68),black,.055)
for x in (.15,.65):
    for z in (3.30,3.80): rod('VESA screw',(x,.27,z),(x,.30,z),.035,silver,6)
# Screen faces the negative Y direction.
box('Monitor rear housing',(-.10,.04,3.58),(3.36,.32,2.02),black,.12)
box('Front bezel',(-.10,-.147,3.58),(3.32,.10,1.99),rubber,.07)
box('Glass screen',(-.10,-.202,3.62),(3.13,.018,1.75),glass,.018)
# A restrained graphic desktop made entirely from geometry.
box('Sidebar',(-1.43,-.215,3.62),(.25,.007,1.64),black,.01)
for z in (4.21,4.04,3.87,3.70): box('Sidebar icon',(-1.43,-.223,z),(.085,.006,.06),white,.01)
box('Application card',(-.15,-.218,3.72),(2.13,.008,1.20),blue,.045)
for i,w in enumerate((1.44,1.12,1.53,.84)):
    box('Text line',(-.27,-.226,4.09-i*.13),(w,.006,.033),white,.008)
for i,h in enumerate((.14,.22,.29,.18,.36,.43)):
    box('Chart bar',(-.86+i*.28,-.23,3.20+h/2),(.16,.006,h),white,.008)
rod('Power indicator',(1.34,-.208,2.65),(1.34,-.22,2.65),.018,led,24)
for x in (-.18,-.08,.02): box('Underside control',(x,-.015,2.558),(.046,.08,.014),black,.005)
for x in [-1.25+i*.14 for i in range(17)]: box('Rear vent slot',(x,.207,4.30),(.065,.006,.13),rubber,.018)
cable('Routed display cable',[(.43,.24,3.18),(.64,.56,3.11),(1.94,.77,3.04),(1.81,1.43,2.49),(1.84,1.42,1.35),(1.84,1.79,.78),(1.45,1.95,.34)],.029,rubber)
for z in (1.55,2.07): rod('Cable retaining collar',(1.75,1.30,z),(1.75,1.30,z+.065),.12,rubber)

floor=mat('Studio floor',(.18,.21,.25),0,.8)
box('Ground',(0,0,-.075),(200,200,.1),floor,0)
world=bpy.context.scene.world; world.use_nodes=True; world.node_tree.nodes['Background'].inputs[0].default_value=(.22,.25,.30,1); world.node_tree.nodes['Background'].inputs[1].default_value=.4
for name,loc,power,size in [('Key',(-4,-5,8),1100,5),('Fill',(5,-2,6),800,4),('Rim',(1,5,7),1200,3)]:
    bpy.ops.object.light_add(type='AREA',location=loc); o=bpy.context.object; o.name=name; o.data.energy=power; o.data.shape='DISK'; o.data.size=size; o.rotation_euler=(Vector((0,0,2.4))-o.location).to_track_quat('-Z','Y').to_euler()
bpy.ops.object.camera_add(location=(7,-9,6.1)); cam=bpy.context.object; cam.rotation_euler=(Vector((0,.3,2.25))-cam.location).to_track_quat('-Z','Y').to_euler(); cam.data.type='ORTHO'; cam.data.ortho_scale=8.3
scene=bpy.context.scene; scene.camera=cam; scene.render.engine='CYCLES'; scene.render.resolution_x=1400; scene.render.resolution_y=1100; scene.render.resolution_percentage=100
