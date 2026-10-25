import bpy, math
from mathutils import Vector
bpy.ops.object.select_all(action='SELECT'); bpy.ops.object.delete(use_global=False)

def mat(name,c,metal=0,rough=.45):
    m=bpy.data.materials.new(name); m.diffuse_color=(*c,1); m.use_nodes=True; p=m.node_tree.nodes.get('Principled BSDF'); p.inputs['Base Color'].default_value=(*c,1); p.inputs['Metallic'].default_value=metal; p.inputs['Roughness'].default_value=rough; return m
paint=mat('Industrial golden yellow',(.96,.52,.035),.5,.35); edge=mat('Dark steel',(.055,.075,.085),.8,.33); steel=mat('Machined steel',(.43,.48,.51),.85,.26); cable=mat('Wire rope',(.055,.06,.065),.8,.38); ground=mat('Concrete floor',(.30,.32,.33),0,.88); red=mat('Motor red',(.48,.045,.028),.5); white=mat('Lettering',(.91,.91,.82))

def box(name,loc,dims,m,bevel=0):
    bpy.ops.mesh.primitive_cube_add(size=1,location=loc); o=bpy.context.object; o.name=name; o.dimensions=dims; bpy.ops.object.transform_apply(location=False,rotation=False,scale=True); o.data.materials.append(m)
    if bevel: b=o.modifiers.new('Edge radii','BEVEL'); b.width=bevel; b.segments=2; o.modifiers.new('Weighted normals','WEIGHTED_NORMAL')
    return o

def rod(name,a,b,r,m,verts=24):
    d=Vector(b)-Vector(a); bpy.ops.mesh.primitive_cylinder_add(vertices=verts,radius=r,depth=d.length,location=(Vector(a)+Vector(b))/2); o=bpy.context.object; o.name=name; o.rotation_euler=d.to_track_quat('Z','Y').to_euler(); o.data.materials.append(m); return o

def beam(name,a,b,w,h,m=paint):
    d=Vector(b)-Vector(a); o=box(name,(Vector(a)+Vector(b))/2,(w,h,d.length),m,.02); o.rotation_euler=d.to_track_quat('Z','Y').to_euler()

def path(name,coords,r,m):
    c=bpy.data.curves.new(name,'CURVE'); c.dimensions='3D'; c.resolution_u=12; c.bevel_depth=r; c.bevel_resolution=4; p=c.splines.new('BEZIER'); p.bezier_points.add(len(coords)-1)
    for b,co in zip(p.bezier_points,coords): b.co=co; b.handle_left_type='AUTO'; b.handle_right_type='AUTO'
    o=bpy.data.objects.new(name,c); bpy.context.collection.objects.link(o); o.data.materials.append(m); return o
box('Factory apron',(0,0,-.13),(16,13,.26),ground,.04)
# Traveling gantry runs along Y on two ground rails.
for x in (-4.25,4.25):
    box('Rail footing',(x,0,.025),(.48,10,.05),edge,.006)
    box('Crane runway rail',(x,0,.095),(.10,10,.14),steel,.008)
    for y in (-4,-3,-2,-1,0,1,2,3,4):
        box('Rail anchor tie',(x,y,.065),(.43,.16,.035),steel,.006)
    box('Travel end carriage',(x,0,.64),(.65,4.6,.37),paint,.05)
    for y in (-1.85,1.85):
        rod('Rail wheel',(x-.21,y,.34),(x+.21,y,.34),.25,steel,40)
        rod('Wheel flange',(x-.24,y,.34),(x-.18,y,.34),.29,edge,40)
        for xx in (x-.28,x+.28): box('Axle bearing housing',(xx,y,.39),(.12,.27,.27),edge,.03)
    rod('Travel motor',(x+.37,-1.72,.65),(x+.8,-1.72,.65),.19,red)
    for y in (-2.38,2.38): box('End carriage bumper',(x,y,.63),(.44,.16,.25),edge,.025)
    # A-frame legs splay in the travel direction.
    for y in (-1.75,1.75):
        beam('Splayed portal leg',(x,y,.78),(x,y*.29,6.42),.31,.38)
        box('Leg foot plate',(x,y,.85),(.55,.62,.12),edge,.018)
        for dx in (-.18,.18):
            for dy in (-.19,.19): rod('Foot anchor bolt',(x+dx,y+dy,.88),(x+dx,y+dy,.96),.035,steel,6)
    beam('Portal cross tie',(x,-1.24,2.5),(x,1.24,2.5),.17,.19)
    beam('Portal diagonal brace',(x,-1.65,1.12),(x,.72,5.3),.10,.12,edge)
    beam('Portal diagonal brace',(x,1.65,1.12),(x,-.72,5.3),.10,.12,edge)
# Twin bridge girders carry the trolley wheels.
for y in (-.62,.62):
    box('Main girder web',(0,y,6.53),(9.3,.20,.74),paint,.018)
    for z in (6.16,6.90): box('Girder flange',(0,y,z),(9.55,.42,.09),paint,.014)
    box('Trolley running rail',(0,y,6.98),(9.0,.085,.09),steel,.008)
    for x in (-4,-3,-2,-1,0,1,2,3,4): box('Girder web stiffener',(x,y-.115,6.53),(.06,.075,.66),paint,.008)
    for x in (-4.35,4.35): box('Trolley end stop',(x,y,7.12),(.16,.25,.23),edge,.012)
for x in (-4.25,4.25): box('Bridge end tie',(x,0,6.65),(.38,1.7,.40),paint,.018)
# Hoist trolley is offset along the span, with visible wheels, gearbox and drum.
tx=.9
for x in (tx-.65,tx+.65):
    for y in (-.62,.62): rod('Trolley wheel',(x,y-.085,7.16),(x,y+.085,7.16),.15,steel,32)
box('Trolley chassis',(tx,0,7.30),(1.7,1.7,.18),edge,.025)
for x in (tx-.58,tx+.58): box('Drum bearing pedestal',(x,0,7.55),(.16,.56,.43),paint,.025)
rod('Hoist drum',(tx-.53,0,7.63),(tx+.53,0,7.63),.25,steel,48)
for x in (tx-.51,tx+.51): rod('Drum flange',(x-.035,0,7.63),(x+.035,0,7.63),.32,edge,40)
for i in range(25):
    bpy.ops.mesh.primitive_torus_add(major_radius=.253,minor_radius=.009,major_segments=32,minor_segments=6,location=(tx-.47+i*.039,0,7.63),rotation=(0,math.pi/2,0)); bpy.context.object.name='Drum cable winding'; bpy.context.object.data.materials.append(cable)
rod('Hoist drive motor',(tx+.7,0,7.63),(tx+1.22,0,7.63),.22,red)
box('Hoist reduction gearbox',(tx+.64,0,7.57),(.25,.49,.45),paint,.025)
# Four-part reeving through an open center in the trolley chassis.
# Slots visually expose the ropes below the winding drum.
for xx in (tx-.32,tx+.32):
    for yy in (-.23,.23): rod('Vertical hoist rope',(xx,yy,7.37),(xx,yy,3.74),.014,cable,12)
for y in (-.31,.31): box('Lower pulley cheek plate',(tx,y,3.64),(.98,.09,.60),paint,.075)
for xx in (tx-.32,tx+.32):
    rod('Lower sheave',(xx,-.245,3.76),(xx,.245,3.76),.24,edge,40)
    rod('Sheave axle',(xx,-.38,3.76),(xx,.38,3.76),.065,steel)
box('Hook block lower crosshead',(tx,0,3.38),(.75,.58,.16),edge,.035)
rod('Swivel stem',(tx,0,3.36),(tx,0,3.10),.11,steel)
rod('Swivel collar',(tx,0,3.26),(tx,0,3.15),.16,edge)
# Forged open J-hook with a tapered tip and a separate spring safety latch.
coords=[(tx,0,3.15),(tx-.04,0,2.91),(tx-.22,0,2.71),(tx-.24,0,2.43),(tx-.03,0,2.27),(tx+.23,0,2.30),(tx+.39,0,2.49),(tx+.37,0,2.69)]
hook=path('Forged lifting hook',coords,.10,steel)
for point,r in zip(hook.data.splines[0].bezier_points,(1,1.1,1.25,1.35,1.3,1.05,.7,.25)): point.radius=r
beam('Hook safety latch',(tx+.025,-.015,2.98),(tx+.37,-.015,2.68),.032,.065,edge)
rod('Latch pivot',(tx+.02,-.10,2.98),(tx+.02,.10,2.98),.035,steel)
# Access ladder on the left portal.
for x in (-4.53,-4.01): rod('Ladder stile',(x,-1.95,.45),(x,-1.95,6.88),.032,edge)
for i in range(21): rod('Ladder rung',(-4.53,-1.95,.60+i*.30),(-4.01,-1.95,.60+i*.30),.024,steel)
for z in (1.1,2.6,4.1,5.6): beam('Ladder standoff',(-4.25,-1.95,z),(-4.25,-1.75+(z-.78)/5.64*1.24,z),.05,.06,edge)
box('Electrical control cabinet',(-4.25,-1.42,1.73),(.60,.32,.75),edge,.035)
box('Control panel face',(-4.25,-1.59,1.73),(.48,.035,.61),steel,.014)
for x,m in ((-4.39,red),(-4.13,paint)): rod('Control button',(x,-1.62,1.86),(x,-1.66,1.86),.045,m)
bpy.ops.object.text_add(location=(-1.2,-.735,6.42),rotation=(math.pi/2,0,0)); o=bpy.context.object; o.name='Rated capacity'; o.data.body='SWL  10 TONNES'; o.data.size=.24; o.data.extrude=.001; o.data.materials.append(edge)
for loc,power,size in [((3,-8,13),2300,8),((-7,-1,9),1700,6),((2,6,11),1900,6)]:
    bpy.ops.object.light_add(type='AREA',location=loc); o=bpy.context.object; o.data.energy=power; o.data.size=size; o.rotation_euler=(Vector((0,0,3.5))-o.location).to_track_quat('-Z','Y').to_euler()
bpy.ops.object.camera_add(location=(13,-18,12)); cam=bpy.context.object; cam.rotation_euler=(Vector((0,0,3.6))-cam.location).to_track_quat('-Z','Y').to_euler(); cam.data.type='ORTHO'; cam.data.ortho_scale=14.8
s=bpy.context.scene; s.camera=cam; s.world.color=(.20,.20,.20); s.render.engine='CYCLES'; s.render.resolution_x=1300; s.render.resolution_y=1100; s.render.resolution_percentage=100
