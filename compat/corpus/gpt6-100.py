import bpy, math
from mathutils import Vector

bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)

def mat(name,c,metal=0,rough=0.5):
    m=bpy.data.materials.new(name); m.diffuse_color=(*c,1); m.use_nodes=True
    p=m.node_tree.nodes.get('Principled BSDF'); p.inputs['Base Color'].default_value=(*c,1); p.inputs['Metallic'].default_value=metal; p.inputs['Roughness'].default_value=rough
    return m

def box(name,loc,dim,m,b=0):
    bpy.ops.mesh.primitive_cube_add(size=1,location=loc)
    o=bpy.context.object; o.name=name; o.dimensions=dim
    bpy.ops.object.transform_apply(location=False,rotation=False,scale=True); o.data.materials.append(m)
    if b:
        mod=o.modifiers.new('Edge bevel','BEVEL'); mod.width=b; mod.segments=2
        o.modifiers.new('Weighted normals','WEIGHTED_NORMAL')
    return o

def cyl(name,loc,r,d,m,axis=(0,0,1),verts=32):
    bpy.ops.mesh.primitive_cylinder_add(vertices=verts,radius=r,depth=d,location=loc)
    o=bpy.context.object; o.name=name; o.data.materials.append(m)
    o.rotation_euler=Vector(axis).to_track_quat('Z','Y').to_euler()
    mod=o.modifiers.new('Edge rounding','BEVEL'); mod.width=min(0.01,d*0.1); mod.segments=2
    o.modifiers.new('Weighted normals','WEIGHTED_NORMAL')
    for f in o.data.polygons: f.use_smooth=True
    return o

def beam(name,a,b,w,d,m):
    a=Vector(a); b=Vector(b); o=box(name,(a+b)*0.5,(w,d,(b-a).length),m,0.012)
    o.rotation_euler=(b-a).to_track_quat('Z','Y').to_euler(); return o

def text(body,loc,size,m):
    bpy.ops.object.text_add(location=loc,rotation=(math.pi/2,0,0))
    o=bpy.context.object; o.name=body; o.data.body=body; o.data.align_x='CENTER'; o.data.size=size; o.data.extrude=0.001; o.data.materials.append(m)
    return o

concrete=mat('Platform concrete',(0.46,0.47,0.45),0,0.85)
paving=mat('Paving slabs',(0.66,0.65,0.59),0,0.85)
edge=mat('Pale coping',(0.85,0.81,0.67),0,0.75)
yellow=mat('Tactile safety yellow',(0.89,0.61,0.075),0,0.65)
steel=mat('Forest green structure',(0.055,0.19,0.17),0.6,0.4)
roof=mat('Standing seam zinc roof',(0.16,0.23,0.27),0.72,0.35)
wood=mat('Oiled bench timber',(0.45,0.23,0.085),0,0.5)
black=mat('Dark metal',(0.035,0.046,0.05),0.5,0.55)
rail=mat('Rail steel',(0.40,0.43,0.46),0.9,0.3)
sleeper=mat('Weathered sleepers',(0.20,0.17,0.13),0,0.95)
ballast=mat('Ballast',(0.30,0.32,0.31),0,0.95)
ground=mat('Ground',(0.20,0.26,0.17),0,1)
white=mat('Sign lettering',(0.96,0.94,0.85),0,0.4)
blue=mat('Station signs',(0.025,0.13,0.26),0.2,0.4)
light=mat('Lamp diffuser',(0.94,0.90,0.68),0,0.3)
p=light.node_tree.nodes.get('Principled BSDF'); p.inputs['Emission Color'].default_value=(1,0.86,0.59,1); p.inputs['Emission Strength'].default_value=2
# Procedural small-scale ballast texture.
nt=ballast.node_tree; noise=nt.nodes.new('ShaderNodeTexNoise'); noise.inputs['Scale'].default_value=38; noise.inputs['Detail'].default_value=2
bump=nt.nodes.new('ShaderNodeBump'); bump.inputs['Strength'].default_value=0.75; bump.inputs['Distance'].default_value=0.06
nt.links.new(noise.outputs['Fac'],bump.inputs['Height']); nt.links.new(bump.outputs['Normal'],nt.nodes.get('Principled BSDF').inputs['Normal'])

box('Landscape',(0,0,-0.13),(200,200,0.2),ground)
box('Track ballast bed',(0,-3.07,0.015),(17,2.45,0.19),ballast,0.10)
for i in range(29):
    x=-8.12+i*0.58
    box('Timber sleeper',(x,-3.07,0.145),(0.22,2.06,0.15),sleeper,0.018)
    for y in (-3.7875,-2.3525):
        box('Rail chair',(x,y,0.235),(0.27,0.25,0.035),black,0.007)
for y in (-3.7875,-2.3525):
    box('Rail foot',(0,y,0.269),(17,0.14,0.045),rail,0.006)
    box('Rail web',(0,y,0.327),(17,0.042,0.08),rail,0.004)
    box('Polished rail head',(0,y,0.377),(17,0.075,0.045),rail,0.009)
box('Raised platform foundation',(0,0.15,0.35),(12,3.5,0.70),concrete,0.035)
for ix in range(20):
    for iy in range(5):
        box('Paving slab',(-5.7+ix*0.6,-0.94+iy*0.6,0.73),(0.59,0.59,0.06),paving,0.006)
for i in range(24):
    x=-5.75+i*0.5
    box('Platform edge coping',(x,-1.40,0.737),(0.49,0.4,0.075),edge,0.008)
    box('Tactile tile',(x,-1.075,0.77),(0.49,0.22,0.035),yellow,0.004)
    for j in range(5):
        for k in range(2):
            cyl('Tactile raised stud',(x-0.18+j*0.09,-1.13+k*0.10,0.792),0.015,0.01,yellow,verts=8)
# Access steps at the left end.
for i in range(3):
    h=(i+1)*0.19
    box('Access step',(-6.95+i*0.32,0.42,h/2),(0.34,1.35,h),concrete,0.015)
for y in (-0.29,1.13):
    for x,z in ((-7.10,0.18),(-6.1,0.74)):
        cyl('Step handrail post',(x,y,z+0.45),0.027,0.90,steel)
    beam('Sloped handrail',(-7.1,y,1.08),(-6.1,y,1.64),0.045,0.045,steel)
# Canopy frames and visible knee braces.
for x in (-4.8,0,4.8):
    for y in (-0.64,1.29):
        box('Column base plate',(x,y,0.80),(0.31,0.31,0.06),steel,0.015)
        box('Canopy column',(x,y,2.03),(0.14,0.14,2.43),steel,0.012)
        for dx in (-0.10,0.10):
            for dy in (-0.10,0.10): cyl('Anchor bolt',(x+dx,y+dy,0.837),0.018,0.025,rail,verts=12)
        for sign in (-1,1):
            beam('Longitudinal knee brace',(x,y,2.71),(x+sign*0.51,y,3.20),0.075,0.075,steel)
    beam('Canopy tie beam',(x,-1.02,3.24),(x,1.67,3.24),0.12,0.14,steel)
    beam('Front rafter',(x,-1.12,3.30),(x,0.32,3.77),0.11,0.13,steel)
    beam('Rear rafter',(x,0.32,3.77),(x,1.76,3.30),0.11,0.13,steel)
    beam('King post',(x,0.32,3.24),(x,0.32,3.77),0.065,0.065,steel)
for y in (-0.64,1.29): box('Longitudinal canopy beam',(0,y,3.23),(10.65,0.14,0.19),steel,0.012)
# Roof panels rise to a central ridge; separate seams run down each slope.
slope=math.atan2(0.47,1.44)
for sign in (-1,1):
    o=box('Sloping zinc roof',(0,0.32+sign*0.72,3.545),(10.9,math.hypot(1.44,0.47)+0.08,0.065),roof,0.008)
    o.rotation_euler.x=-sign*slope
    for i in range(23):
        x=-5.4+i*0.49
        beam('Standing roof seam',(x,0.32,3.81),(x,0.32+sign*1.48,3.327),0.018,0.025,roof)
box('Ridge cap',(0,0.32,3.811),(10.95,0.12,0.047),roof,0.015)
for y in (-1.14,1.78):
    box('Gutter',(0,y,3.30),(10.98,0.12,0.13),steel,0.02)
cyl('Downpipe',(4.88,1.73,2.02),0.045,2.53,steel)
# Two timber benches facing the track.
for cx in (-2.8,2.8):
    for dx in (-0.70,0.70):
        for y in (0.48,0.94): box('Bench foot',(cx+dx,y,0.99),(0.075,0.075,0.45),black,0.01)
        box('Bench seat bearer',(cx+dx,0.71,1.22),(0.075,0.65,0.075),black,0.008)
        box('Bench back upright',(cx+dx,1.00,1.40),(0.06,0.065,0.88),black,0.008)
        beam('Armrest riser',(cx+dx,0.48,1.23),(cx+dx,0.48,1.48),0.045,0.045,black)
        box('Bench armrest',(cx+dx,0.72,1.49),(0.075,0.60,0.05),wood,0.015)
    for j in range(5): box('Timber seat slat',(cx,0.46+j*0.12,1.275),(1.93,0.10,0.06),wood,0.012)
    for z in (1.48,1.65,1.82): box('Timber back slat',(cx,0.972,z),(1.93,0.055,0.135),wood,0.012)
# Rear safety railing.
for x in (-5.7,-3.8,-1.9,0,1.9,3.8,5.7):
    cyl('Rear railing post',(x,1.78,1.28),0.033,1.04,steel)
for z in (1.1,1.77): cyl('Rear railing rail',(0,1.78,z),0.027,11.4,steel,(1,0,0))
# Hanging station sign and bay indicator.
for x in (-1.30,1.30): cyl('Sign suspension',(x,-0.69,2.97),0.015,0.43,steel)
box('Station name board',(0,-0.69,2.74),(3.15,0.095,0.47),blue,0.035)
text('WILLOW HALT',(0,-0.741,2.665),0.24,white)
box('Platform number board',(-4.80,-0.78,2.43),(0.42,0.08,0.48),blue,0.02)
text('1',(-4.80,-0.828,2.28),0.33,white)
# Analogue station clock at the right hand end.
cyl('Clock housing',(4.8,-0.77,2.65),0.245,0.09,black,(0,1,0))
cyl('Clock dial',(4.8,-0.822,2.65),0.218,0.012,white,(0,1,0))
for i in range(12):
    a=i*math.tau/12
    o=box('Clock hour tick',(4.8+0.187*math.sin(a),-0.832,2.65+0.187*math.cos(a)),(0.012,0.007,0.035),black,0.002)
    o.rotation_euler.y=a
beam('Clock minute hand',(4.8,-0.843,2.65),(4.93,-0.843,2.725),0.012,0.012,black)
beam('Clock hour hand',(4.8,-0.846,2.65),(4.72,-0.846,2.72),0.016,0.012,black)
cyl('Clock spindle',(4.8,-0.85,2.65),0.019,0.012,black,(0,1,0))
# Timetable and litter bin.
box('Timetable backing',(0,1.62,1.91),(0.77,0.09,1.01),steel,0.025)
box('Timetable sheet',(0,1.569,1.91),(0.66,0.013,0.88),white,0.005)
text('DEPARTURES',(0,1.557,2.22),0.073,blue)
for i in range(8): text('%02d:%02d    Local'%(8+i,12 if i%2==0 else 42),(0,1.553,2.10-i*0.071),0.042,black)
cyl('Litter bin',(5.34,0.73,1.07),0.22,0.60,steel)
cyl('Bin lid',(5.34,0.73,1.388),0.24,0.05,black)
cyl('Bin opening',(5.34,0.73,1.416),0.135,0.008,black)
for x in (-2.4,2.4):
    box('Canopy light housing',(x,0.32,3.15),(1.10,0.22,0.08),black,0.015)
    box('Canopy light diffuser',(x,0.32,3.104),(0.97,0.17,0.016),light,0.005)
    bpy.ops.object.light_add(type='AREA',location=(x,0.32,3.08))
    o=bpy.context.object; o.data.energy=45; o.data.shape='RECTANGLE'; o.data.size=1; o.data.size_y=0.2

world=bpy.context.scene.world; world.use_nodes=True
world.node_tree.nodes['Background'].inputs[0].default_value=(0.48,0.62,0.78,1); world.node_tree.nodes['Background'].inputs[1].default_value=0.55
bpy.ops.object.light_add(type='SUN',location=(0,-4,8))
o=bpy.context.object; o.rotation_euler=(math.radians(28),math.radians(-25),math.radians(-35)); o.data.energy=2.5; o.data.angle=0.15
bpy.ops.object.light_add(type='AREA',location=(0,-5,9))
o=bpy.context.object; o.data.energy=1300; o.data.size=8; o.rotation_euler=(Vector((0,0,1.3))-o.location).to_track_quat('-Z','Y').to_euler()
bpy.ops.object.camera_add(location=(13,-18,11))
cam=bpy.context.object; cam.rotation_euler=(Vector((-0.25,-0.5,1.35))-cam.location).to_track_quat('-Z','Y').to_euler()
cam.data.type='ORTHO'; cam.data.ortho_scale=19.3
scene=bpy.context.scene; scene.camera=cam; scene.render.engine='CYCLES'; scene.cycles.samples=64
scene.render.resolution_x=1600; scene.render.resolution_y=1000; scene.render.resolution_percentage=100
