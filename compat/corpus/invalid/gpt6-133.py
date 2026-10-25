import bpy, math, random
from mathutils import Vector
random.seed(133)
bpy.ops.wm.read_factory_settings(use_empty=True)

def mat(name,c,rough=.6,metal=0):
    m=bpy.data.materials.new(name); m.diffuse_color=(*c,1); m.use_nodes=True; p=m.node_tree.nodes.get('Principled BSDF'); p.inputs['Base Color'].default_value=(*c,1); p.inputs['Roughness'].default_value=rough; p.inputs['Metallic'].default_value=metal; return m

def box(name,loc,size,m,b=.018):
    bpy.ops.mesh.primitive_cube_add(size=1,location=loc); o=bpy.context.object; o.name=name; o.dimensions=size; bpy.ops.object.transform_apply(location=False,rotation=False,scale=True); o.data.materials.append(m)
    if b:
        q=o.modifiers.new('Edge bevel','BEVEL'); q.width=b; q.segments=2; o.modifiers.new('Weighted normals','WEIGHTED_NORMAL')
    return o

def cyl(name,loc,r,d,m):
    bpy.ops.mesh.primitive_cylinder_add(vertices=24,radius=r,depth=d,location=loc); o=bpy.context.object; o.name=name; o.data.materials.append(m); q=o.modifiers.new('Rim bevel','BEVEL'); q.width=.008; q.segments=2; o.modifiers.new('Weighted normals','WEIGHTED_NORMAL'); return o

def rod(name,a,b,r,m):
    v=Vector(b)-Vector(a); o=cyl(name,(Vector(a)+Vector(b))/2,r,v.length,m); o.rotation_euler=v.to_track_quat('Z','Y').to_euler(); return o

def text(body,loc,size,m):
    bpy.ops.object.text_add(location=loc,rotation=(math.pi/2,0,0)); o=bpy.context.object; o.name=body; o.data.body=body; o.data.align_x='CENTER'; o.data.size=size; o.data.extrude=.001; o.data.materials.append(m)

def area(name,loc,power,color,size,target):
    bpy.ops.object.light_add(type='AREA',location=loc); o=bpy.context.object; o.name=name; o.data.energy=power; o.data.color=color; o.data.shape='DISK'; o.data.size=size; o.rotation_euler=(Vector(target)-o.location).to_track_quat('-Z','Y').to_euler()

wall=mat('Ivory plaster',(.84,.82,.74)); oak=mat('Birch shelving',(.56,.38,.2)); pale=mat('Pale wood tabletops',(.7,.55,.34)); floor=mat('Stone flooring',(.48,.5,.47)); grout=mat('Grout',(.29,.32,.3)); metal=mat('Bronze frames',(.14,.18,.16),.35,.6); green=mat('Moss chair fabric',(.23,.34,.25),.9); paper=mat('Book paper',(.84,.8,.66)); ink=mat('Sign lettering',(.09,.15,.14)); blue=mat('Skylight glazing',(.61,.8,.88),.19)
bookm=[mat('Book cloth '+str(i),c,.85) for i,c in enumerate([(.35,.13,.09),(.12,.24,.31),(.26,.34,.2),(.61,.41,.14),(.36,.23,.34),(.7,.58,.39)])]
box('Library foundation',(0,0,-.16),(9,7.6,.32),grout)
for i in range(15):
    for j in range(12): box('Stone tile',(-4.2+i*.6,-3.45+j*.63,.015),(.588,.618,.03),floor,.003)
box('Rear wall',(0,3.75,1.95),(9,.16,3.9),wall)
box('West wall',(-4.42,0,1.95),(.16,7.5,3.9),wall)
box('Rear baseboard',(0,3.64,.13),(8.8,.06,.24),oak)
box('West baseboard',(-4.31,0,.13),(.06,7.4,.24),oak)
# Back wall bookcases with individually bound volumes

def book(x,y,z,w,h,d):
    m=random.choice(bookm)
    box('Book pages',(x,y,z+h/2),(w-.012,d-.025,h-.025),paper,.002)
    for dx in [-w/2+.004,w/2-.004]: box('Cloth cover',(x+dx,y,z+h/2),(.008,d,h),m,.002)
    box('Book spine',(x,y-d/2,z+h/2),(w,.025,h),m,.004)
    for f in [.17,.8]: box('Spine foil band',(x,y-d/2-.014,z+h*f),(w*.65,.003,.007),paper,.001)

def case(x,y,width=1.7,height=2.5,depth=.38,double=False):
    box('Bookcase back',(x,y+depth/2-.025,height/2),(width,.05,height),oak)
    for dx in [-width/2,width/2]: box('Bookcase upright',(x+dx,y,height/2),(.065,depth,height),oak)
    levels=[.13,.6,1.07,1.54,2.01,2.48]
    for z in levels:
        box('Book shelf',(x,y,z),(width,depth,.045),oak)
        if z>height-.3: continue
        xx=x-width/2+.09
        while xx<x+width/2-.12:
            w=random.uniform(.045,.085); h=random.uniform(.26,.4); book(xx+w/2,y-.01,z+.025,w,h,depth-.08); xx+=w+.013
for x in [-3.34,-1.5,.34,2.18]: case(x,3.39)
text('NEIGHBOURHOOD LIBRARY',(-.5,3.652,3.24),.3,ink)
for x,t in [(-3.34,'ART'),(-1.5,'FICTION'),(.34,'HISTORY'),(2.18,'SCIENCE')]: text(t,(x,3.15,2.68),.11,ink)
# Two low, freestanding, double-sided stacks in the west aisle
for yc in [-1.8,.5]:
    root=bpy.data.objects.new('Double sided stack',None); bpy.context.collection.objects.link(root)
    # Built as two bookcases back to back, then turned to run north-south.
    before=set(bpy.context.scene.objects)
    case(0,-.19,1.75,2.5,.38)
    first=set(bpy.context.scene.objects)-before
    before=set(bpy.context.scene.objects)
    case(0,-.19,1.75,2.5,.38)
    second=set(bpy.context.scene.objects)-before
    for o in first: o.parent=root
    backroot=bpy.data.objects.new('Reverse shelf face',None); bpy.context.collection.objects.link(backroot); backroot.parent=root; backroot.rotation_euler.z=math.pi
    for o in second: o.parent=backroot
    root.location=(-2.77,yc,0); root.rotation_euler.z=math.pi/2
# Reading tables and chairs

def chair(x,y,angle):
    root=bpy.data.objects.new('Reading chair',None); bpy.context.collection.objects.link(root)
    parts=[box('Chair seat',(0,0,.46),(.5,.49,.09),green,.055),box('Chair back',(0,.225,.81),(.5,.065,.49),oak,.045)]
    for dx in [-.19,.19]:
        for dy in [-.18,.18]: parts.append(rod('Chair leg',(dx*1.13,dy*1.13,.04),(dx,dy,.44),.026,oak))
    for o in parts: o.parent=root
    root.location=(x,y,0); root.rotation_euler.z=angle
for y in [-1.95,.55]:
    box('Reading table',(1.25,y,.8),(3.05,1.17,.095),pale,.045)
    for dx in [-1.31,1.31]:
        for dy in [-.43,.43]: box('Table leg',(1.25+dx,y+dy,.39),(.085,.085,.75),metal,.01)
    for x in [.35,1.25,2.15]: chair(x,y-.97,math.pi); chair(x,y+.97,0)
    # Shared reading light along the table center
    for x in [.35,2.15]: rod('Task light upright',(x,y,.85),(x,y,1.28),.018,metal)
    box('Linear reading lamp',(1.25,y,1.31),(2.22,.15,.075),metal)
    area('Table task lighting',(1.25,y,1.26),45,(1,.87,.62),1.5,(1.25,y,.8))
    for x in [.35,1.25,2.15]:
        o=box('Closed reading book',(x,y-.29,.869),(.29,.38,.045),random.choice(bookm),.008); o.rotation_euler.z=random.uniform(-.2,.2)
    # Open volume with two page blocks and a visible gutter
    for dx in [-.115,.115]:
        o=box('Open book pages',(2.14+dx,y+.3,.875),(.22,.29,.027),paper,.004); o.rotation_euler.y=-.05 if dx<0 else .05
        for j in range(7): box('Printed lines',(2.14+dx,y+.21+j*.026,.892),(.16,.003,.0015),floor,.0005)
# Low new-arrivals display near front-left
box('New arrivals bench',(-.95,-3.19,.48),(1.1,.56,.88),oak)
for i in range(5): book(-1.33+i*.18,-3.2,.93,.075,.27,.23)
text('NEW',(-.95,-3.482,.55),.14,ink)
# Roof is cut away; two framed skylight modules remain above the rear zone.
# Open centers and translucent glazing allow the room to remain legible.
p=blue.node_tree.nodes.get('Principled BSDF'); p.inputs['Transmission Weight'].default_value=.75; p.inputs['IOR'].default_value=1.45
for x in [-2.25,1.65]:
    for xx in [x-1.15,x+1.15]: box('Skylight raised curb',(xx,2.05,3.91),(.13,1.9,.25),wall)
    for yy in [1.1,3.0]: box('Skylight raised curb',(x,yy,3.91),(2.43,.13,.25),wall)
    box('Skylight glass',(x,2.05,4.045),(2.2,1.78,.025),blue,.005)
    box('Skylight central mullion',(x,2.05,4.08),(.055,1.8,.055),metal,.005)
    for yy in [1.15,2.95]: box('Skylight frame',(x,yy,4.08),(2.32,.055,.055),metal,.005)
    area('Skylight daylight',(x,2.05,3.76),450,(.8,.9,1),2,(x,1,0))
area('Open facade daylight',(2,-4,6),1300,(1,.93,.82),5,(0,1,0)); area('West fill',(-3,-2,5),650,(.82,.9,1),4,(0,0,1))
bpy.ops.object.camera_add(location=(11,-14,10)); cam=bpy.context.object; cam.rotation_euler=(Vector((0,.15,1.25))-cam.location).to_track_quat('-Z','Y').to_euler(); cam.data.type='ORTHO'; cam.data.ortho_scale=12.4
s=bpy.context.scene; s.camera=cam; s.render.engine='CYCLES'; s.world.color=(.22,.22,.22); s.render.resolution_x=1600; s.render.resolution_y=1250; s.render.resolution_percentage=100
