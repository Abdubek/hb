import bpy, math
from mathutils import Vector
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)

def mat(name, color, metal=0.0, rough=0.45):
    m=bpy.data.materials.new(name); m.diffuse_color=(*color,1); m.use_nodes=True
    p=m.node_tree.nodes.get('Principled BSDF'); p.inputs['Base Color'].default_value=(*color,1); p.inputs['Metallic'].default_value=metal; p.inputs['Roughness'].default_value=rough
    return m

def finish(o,name,m,bevel=0):
    o.name=name; o.data.materials.append(m)
    if bevel:
        b=o.modifiers.new('Soft manufactured edges','BEVEL'); b.width=bevel; b.segments=3
        o.modifiers.new('Weighted normals','WEIGHTED_NORMAL')
    return o

def box(name,loc,size,m,bevel=0.03):
    bpy.ops.mesh.primitive_cube_add(size=1,location=loc); o=bpy.context.object; o.dimensions=size
    bpy.ops.object.transform_apply(location=False,rotation=False,scale=True)
    return finish(o,name,m,bevel)

def rod(name,a,b,r,m,vertices=24):
    d=Vector(b)-Vector(a); bpy.ops.mesh.primitive_cylinder_add(vertices=vertices,radius=r,depth=d.length,location=(Vector(a)+Vector(b))/2)
    o=bpy.context.object; o.rotation_euler=d.to_track_quat('Z','Y').to_euler(); finish(o,name,m,0.008)
    for p in o.data.polygons: p.use_smooth=len(p.vertices)==4
    return o

def tube(name,points,r,m,closed=False):
    c=bpy.data.curves.new(name,'CURVE'); c.dimensions='3D'; c.bevel_depth=r; c.bevel_resolution=4; c.resolution_u=16
    s=c.splines.new('POLY'); s.points.add(len(points)-1)
    for p,co in zip(s.points,points): p.co=(*co,1)
    s.use_cyclic_u=closed; o=bpy.data.objects.new(name,c); bpy.context.collection.objects.link(o); o.data.materials.append(m); return o

def label(text,loc,size,m):
    bpy.ops.object.text_add(location=loc,rotation=(math.pi/2,0,0)); o=bpy.context.object; o.name=text; o.data.body=text; o.data.size=size; o.data.extrude=0.001; o.data.materials.append(m)

black=mat('Powder coated charcoal',(0.035,0.044,0.05),0.7)
rubber=mat('Rubber',(0.015,0.019,0.022),0,0.85)
red=mat('Safety vermilion',(0.68,0.075,0.027),0.5,0.3)
steel=mat('Cast aluminum',(0.38,0.42,0.45),0.8)
dark=mat('Recesses',(0.025,0.03,0.033),0.25)
white=mat('Warm white lettering',(0.87,0.9,0.83))
yellow=mat('Warning yellow',(0.95,0.63,0.035),0.1)
blue=mat('Display blue',(0.06,0.47,0.63),0.2)
p=blue.node_tree.nodes.get('Principled BSDF'); p.inputs['Emission Color'].default_value=(0.04,0.4,0.65,1); p.inputs['Emission Strength'].default_value=1.5
# Two continuous rounded rectangular cage hoops.
for x in (-1.28,1.28):
    pts=[]
    for cy,cz,start in [(0.59,0.43,-90),(0.59,1.92,0),(-0.59,1.92,90),(-0.59,0.43,180)]:
        for j in range(9):
            a=math.radians(start+j*90/8); pts.append((x,cy+0.18*math.cos(a),cz+0.18*math.sin(a)))
    tube('Bent steel perimeter hoop',pts,0.067,black,True)
for y in (-0.77,0.77):
    for z in (0.43,1.92): rod('Longitudinal cage rail',(-1.28,y,z),(1.28,y,z),0.055,black)
for x in (-1.12,1.12):
    for y in (-0.61,0.61):
        box('Anti vibration foot',(x,y,0.14),(0.35,0.3,0.19),rubber,0.055)
        rod('Mount bolt',(x,y,0.21),(x,y,0.37),0.045,steel)
box('Pressed steel base',(0,0,0.35),(2.4,1.3,0.13),black)
# Engine on left and alternator on right, sharing a horizontal shaft.
box('Engine crankcase',(-0.52,0,0.88),(0.77,0.83,0.69),steel,0.12)
rod('Alternator body',(0.05,0,0.94),(1.06,0,0.94),0.46,steel,64)
rod('Alternator rear cover',(1.04,0,0.94),(1.12,0,0.94),0.43,black,64)
for i in range(18):
    a=i*math.tau/18; y=0.442*math.cos(a); z=0.94+0.442*math.sin(a)
    rod('Alternator cooling rib',(0.19,y,z),(0.93,y,z),0.024,steel,12)
box('Cylinder block',(-0.57,0.08,1.31),(0.63,0.59,0.39),dark)
for z in (1.16,1.23,1.30,1.37,1.44): box('Engine cooling fin',(-0.57,0.08,z),(0.75,0.7,0.028),steel,0.01)
rod('Pull start shroud',(-0.59,-0.4,0.91),(-0.59,-0.62,0.91),0.365,black,64)
rod('Starter hub',(-0.59,-0.615,0.91),(-0.59,-0.65,0.91),0.15,red,48)
for i in range(12):
    a=i*math.tau/12
    o=box('Starter ventilation slot',(-0.59+0.265*math.cos(a),-0.638,0.91+0.265*math.sin(a)),(0.105,0.013,0.038),dark,0.016); o.rotation_euler.y=-a
label('GX',(-0.68,-0.674,0.865),0.095,white)
tube('Starter cord',[(-0.83,-0.63,1.1),(-1.03,-0.66,1.34),(-1.07,-0.66,1.45)],0.014,rubber)
rod('Pull grip',(-1.18,-0.66,1.45),(-0.94,-0.66,1.45),0.046,rubber)
box('Air filter box',(-0.98,0.03,1.2),(0.24,0.5,0.44),black,0.055)
box('Muffler',(-0.39,0.53,1.26),(0.66,0.27,0.42),dark,0.06)
for x in (-0.6,-0.48,-0.36,-0.24): box('Heat shield ribs',(x,0.68,1.26),(0.036,0.025,0.3),steel,0.007)
tube('Exhaust elbow',[(-0.1,0.57,1.28),(0.14,0.57,1.28),(0.21,0.7,1.28),(0.21,0.83,1.28)],0.045,steel)
rod('Dark exhaust mouth',(0.21,0.828,1.28),(0.21,0.839,1.28),0.035,dark)
# Elevated fuel tank, folded seam, cap and warning label.
box('Fuel tank lower seam',(0,0,1.64),(2.23,1.14,0.055),black,0.06)
box('Red steel fuel tank',(0,0,1.76),(2.16,1.08,0.27),red,0.11)
rod('Fuel filler neck',(-0.62,0.12,1.89),(-0.62,0.12,1.94),0.14,steel)
rod('Fuel cap',(-0.62,0.12,1.94),(-0.62,0.12,1.995),0.16,black,48)
for i in range(12):
    a=i*math.tau/12
    box('Cap grip',(-0.62+0.146*math.cos(a),0.12+0.146*math.sin(a),1.97),(0.04,0.04,0.06),black,0.01)
box('Fuel warning sticker',(0.45,0,1.901),(0.48,0.27,0.007),yellow,0.015)
# Front control console, with recessed sockets and tactile controls.
box('Control console',(0.62,-0.59,1.26),(1.05,0.21,0.63),black,0.05)
box('Face plate',(0.62,-0.709,1.26),(0.97,0.028,0.55),steel,0.022)
box('Meter bezel',(0.36,-0.735,1.4),(0.32,0.036,0.17),dark,0.018)
box('Digital meter',(0.36,-0.758,1.405),(0.26,0.012,0.105),blue,0.008)
label('230', (0.255,-0.768,1.372),0.076,white)
for x in (0.37,0.78):
    rod('Outlet flange',(x,-0.73,1.12),(x,-0.768,1.12),0.13,black,48)
    rod('Outlet recess',(x,-0.769,1.12),(x,-0.778,1.12),0.092,rubber,32)
    for dx in (-0.034,0.034): box('Socket aperture',(x+dx,-0.786,1.125),(0.019,0.008,0.045),dark,0.004)
    rod('Socket earth contact',(x,-0.784,1.063),(x,-0.796,1.063),0.014,steel)
box('Rocker switch',(0.85,-0.754,1.42),(0.13,0.052,0.16),dark,0.015)
box('Switch red paddle',(0.85,-0.787,1.43),(0.092,0.024,0.1),red,0.008)
for x in (0.19,1.05):
    for z in (1.04,1.49): rod('Panel screw',(x,-0.725,z),(x,-0.746,z),0.019,steel,12)
label('FIELD / 3500',(-0.99,-0.554,1.745),0.115,white)
tube('Fuel hose',[(-0.84,0.22,1.62),(-0.97,0.28,1.53),(-0.99,0.3,1.1),(-0.75,0.22,0.96)],0.025,rubber)
box('Ground',(0,0,-0.055),(200,200,0.1),mat('Studio floor',(0.16,0.19,0.22)),0)
world=bpy.context.scene.world; world.use_nodes=True; world.node_tree.nodes['Background'].inputs[0].default_value=(0.18,0.22,0.28,1); world.node_tree.nodes['Background'].inputs[1].default_value=0.45
for loc,power,size in [((1,-4,7),1000,5),((-4,-1,4),700,4),((2,4,5),1100,3)]:
    bpy.ops.object.light_add(type='AREA',location=loc); o=bpy.context.object; o.data.energy=power; o.data.shape='DISK'; o.data.size=size; o.rotation_euler=(Vector((0,0,1))-o.location).to_track_quat('-Z','Y').to_euler()
bpy.ops.object.camera_add(location=(4,-6,3.7)); cam=bpy.context.object; cam.rotation_euler=(Vector((0,0,1))-cam.location).to_track_quat('-Z','Y').to_euler(); cam.data.type='ORTHO'; cam.data.ortho_scale=4.5
scene=bpy.context.scene; scene.camera=cam; scene.render.engine='CYCLES'; scene.render.resolution_x=1400; scene.render.resolution_y=1100; scene.render.resolution_percentage=100
