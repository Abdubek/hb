import bpy, math, random
from mathutils import Vector

bpy.ops.object.select_all(action='SELECT'); bpy.ops.object.delete(use_global=False)
random.seed(15)

def mat(name,color,rough=.5,metal=0):
    m=bpy.data.materials.new(name); m.diffuse_color=(*color,1); m.use_nodes=True
    p=m.node_tree.nodes.get('Principled BSDF'); p.inputs['Base Color'].default_value=(*color,1); p.inputs['Roughness'].default_value=rough; p.inputs['Metallic'].default_value=metal; return m

def box(name,loc,dims,m,bevel=.025):
    bpy.ops.mesh.primitive_cube_add(size=1,location=loc); o=bpy.context.object; o.name=name; o.dimensions=dims; bpy.ops.object.transform_apply(location=False,rotation=False,scale=True); o.data.materials.append(m)
    if bevel:
        b=o.modifiers.new('Architectural edge','BEVEL'); b.width=bevel; b.segments=2; o.modifiers.new('Weighted normals','WEIGHTED_NORMAL')
    return o

def rod(name,a,b,r,m,n=12):
    a=Vector(a); b=Vector(b); bpy.ops.mesh.primitive_cylinder_add(vertices=n,radius=r,depth=(b-a).length,location=(a+b)/2)
    o=bpy.context.object; o.name=name; o.rotation_euler=(b-a).to_track_quat('Z','Y').to_euler(); o.data.materials.append(m); return o

def text(name,body,loc,size,m):
    cu=bpy.data.curves.new(name,'FONT'); cu.body=body; cu.align_x='CENTER'; cu.size=size; cu.extrude=.002
    o=bpy.data.objects.new(name,cu); bpy.context.collection.objects.link(o); o.location=loc; o.rotation_euler=(math.pi/2,0,0); cu.materials.append(m); return o

stucco=mat('Warm ochre stucco',(.67,.43,.25),.85); stone=mat('Limestone trim',(.77,.72,.61),.75); base=mat('Ground floor rustication',(.48,.43,.35),.85)
frame=mat('Painted window frames',(.12,.19,.18),.5); iron=mat('Balcony iron',(.035,.052,.055),.36,.65); glass=mat('Blue gray glazing',(.08,.17,.22),.16,.45)
shadow=mat('Dark recess',(.02,.026,.027),.9); wood=mat('Entrance oak',(.18,.075,.026),.6); brass=mat('Door brass',(.58,.39,.12),.3,.7)
terracotta=mat('Terracotta planters',(.49,.18,.085),.85); soil=mat('Potting soil',(.06,.035,.015),1); foliage=[mat('Leaf '+str(i),c,.8) for i,c in enumerate([(.16,.29,.08),(.23,.38,.11),(.085,.2,.1)])]
paving=mat('Sidewalk stone',(.43,.44,.42),.85); ground=mat('Ground',(.24,.27,.28),.9)
# Building mass is recessed behind a front wall assembled around actual openings.
box('Building rear volume',(0,1.62,4.84),(10.5,3.3,9.2),stucco,.045)
box('Foundation',(0,.8,.28),(10.9,5,.4),base,.05)
centers=[-3.35,0,3.35]; opening_width=1.72; floor_z=[.48,3.48,6.48]
# Front plane is Y=-.25. Each floor has continuous spandrels and separate piers.
for story,z0 in enumerate(floor_z):
    sill=z0+.48 if story==0 else z0+.23
    head=z0+2.6
    wallmat=base if story==0 else stucco
    ranges=[(x-opening_width/2,x+opening_width/2) for x in centers]
    cursor=-5.25
    for lo,hi in ranges:
        box('Facade pier',((cursor+lo)/2,-.26,z0+1.5),(lo-cursor,.5,3),wallmat,.008); cursor=hi
    box('Facade end pier',((cursor+5.25)/2,-.26,z0+1.5),(5.25-cursor,.5,3),wallmat,.008)
    box('Floor header',(0,-.26,(head+z0+3)/2),(10.5,.5,z0+3-head),wallmat,.008)
    for col,x in enumerate(centers):
        low=z0 if story==0 and col==1 else sill
        if low>z0: box('Wall under opening',(x,-.26,(z0+low)/2),(opening_width,.5,low-z0),wallmat,.008)
        h=head-low; mid=(head+low)/2
        box('Shadow inside opening',(x,-.005,mid),(1.72,.035,h),shadow,.005)
        if story==0 and col==1:
            box('Entrance door',(x,-.11,mid),(1.53,.12,h-.08),wood,.018)
            for sx in (-.39,.39):
                box('Door inset lower panel',(x+sx,-.184,low+.48),(.61,.04,.71),base,.015)
                box('Door upper glass',(x+sx,-.184,low+1.58),(.61,.04,1.12),glass,.012)
                rod('Door pull',(x+sx*.35,-.25,low+.96),(x+sx*.35,-.25,low+1.3),.027,brass)
            box('Door center stile',(x,-.2,mid),(.065,.08,h),wood,.01)
            text('Address','18',(x,-.552,head+.13),.19,iron)
        else:
            box('Recessed glazing',(x,-.13,mid),(1.52,.05,h-.12),glass,.009)
            for xx in (x-.79,x+.79): box('Window jamb',(xx,-.23,mid),(.09,.15,h),frame,.009)
            for zz in (low+.045,head-.045): box('Window horizontal frame',(x,-.23,zz),(1.65,.15,.09),frame,.009)
            box('Center mullion',(x,-.23,mid),(.065,.15,h),frame,.008)
            box('Transom',(x,-.23,head-.53),(1.58,.15,.065),frame,.008)
            for sx in (-.08,.08): rod('Window handle',(x+sx,-.335,mid-.12),(x+sx,-.335,mid+.03),.015,brass)
        for xx in (x-.96,x+.96): box('Stone opening surround',(xx,-.55,mid),(.17,.18,h+.22),stone,.016)
        box('Stone lintel',(x,-.57,head+.1),(2.1,.24,.2),stone,.02)
        box('Projecting sill',(x,-.61,low-.06),(2.15,.38,.14),stone,.025)
    box('Floor belt course',(0,-.56,z0+2.97),(10.8,.3,.16),stone,.018)
# Ground-level horizontal block joints terminate at the opening surrounds.
for z in (1.15,1.65,2.15,2.65):
    for left,right in [(-5.25,-4.34),(-2.36,-.99),(.99,2.36),(4.34,5.25)]:
        box('Rustication recessed joint',((left+right)/2,-.516,z),(right-left,.018,.022),shadow,.002)
# Six balconies, each with a slab, brackets, balusters and returned side rails.
for story in (1,2):
    z=floor_z[story]+.17
    for col,x in enumerate(centers):
        box('Balcony slab',(x,-1.08,z),(2.54,1.54,.2),stone,.035)
        box('Balcony slab edge',(x,-1.83,z+.015),(2.61,.105,.15),base,.02)
        for sx in (-.83,.83):
            rod('Diagonal balcony bracket',(x+sx,-.52,z-.64),(x+sx,-1.46,z-.11),.055,iron)
        for railz,r in ((z+.28,.022),(z+1.14,.035)):
            rod('Front balcony rail',(x-1.18,-1.78,railz),(x+1.18,-1.78,railz),r,iron)
            for sx in (-1.18,1.18): rod('Returned side rail',(x+sx,-1.78,railz),(x+sx,-.51,railz),r,iron)
        for i in range(13):
            xx=x-1.18+i*2.36/12; rod('Front baluster',(xx,-1.78,z+.12),(xx,-1.78,z+1.14),.019,iron)
        for sx in (-1.18,1.18):
            for i in range(5):
                y=-1.53+i*.25; rod('Side baluster',(x+sx,y,z+.12),(x+sx,y,z+1.14),.019,iron)
        if (story+col)%2==0:
            px=x-.54; py=-1.52
            box('Balcony planter',(px,py,z+.33),(.8,.34,.35),terracotta,.035)
            box('Planter rim',(px,py,z+.51),(.86,.4,.07),terracotta,.015)
            box('Planter soil',(px,py,z+.551),(.72,.28,.016),soil,.004)
            for k in range(9):
                xx=px+random.uniform(-.31,.31); yy=py+random.uniform(-.1,.1); zz=z+random.uniform(.65,.82)
                rod('Plant stem',(xx,yy,z+.55),(xx,yy,zz),.012,foliage[0],6)
                bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=1,radius=random.uniform(.11,.17),location=(xx,yy,zz))
                o=bpy.context.object; o.name='Low poly foliage'; o.scale=(1,.8,1.15); o.data.materials.append(random.choice(foliage))
# Cornice and roof parapet finish the three-story silhouette.
for z,w,d,h in [(9.47,10.8,4,.16),(9.64,11.05,4.18,.2),(9.79,11.2,4.3,.11)]: box('Stepped cornice',(0,1.12,z),(w,d,h),stone,.025)
box('Flat roof',(0,1.45,9.85),(10.7,3.5,.1),base,.02)
for x in (-5.2,5.2): box('Side parapet',(x,1.37,10.08),(.22,3.7,.48),stucco,.02)
box('Front parapet',(0,-.39,10.08),(10.5,.24,.48),stucco,.02)
box('Parapet coping',(0,-.39,10.34),(10.75,.4,.12),stone,.025)
for x in (-5.07,5.07):
    rod('Rain downpipe',(x,-.64,.58),(x,-.64,9.35),.052,iron)
    for z in (1,3,5,7,9): box('Downpipe wall strap',(x,-.65,z),(.16,.16,.07),iron,.01)
box('Entrance lower step',(0,-1.23,.25),(2.75,1.35,.17),stone,.025)
box('Entrance upper step',(0,-.93,.39),(2.35,.76,.12),stone,.018)
for x in (-1.31,1.31):
    box('Entrance light backplate',(x,-.57,2.23),(.18,.08,.37),iron,.015)
    box('Entrance lantern',(x,-.73,2.25),(.2,.23,.29),stone,.02)
box('Sidewalk',(0,-.25,.04),(13.5,7.5,.2),paving,.025)
for x in range(-6,7): box('Paving joint',(x,-2.55,.143),(.015,2.7,.006),base,.001)
box('Front paving seam',(0,-2.65,.143),(13.3,.015,.006),base,.001)
box('Ground',(0,0,-.12),(200,200,.1),ground,0)
world=bpy.context.scene.world; world.use_nodes=True; world.node_tree.nodes['Background'].inputs[0].default_value=(.55,.68,.85,1); world.node_tree.nodes['Background'].inputs[1].default_value=.55
bpy.ops.object.light_add(type='SUN',location=(5,-8,15)); sun=bpy.context.object; sun.name='Afternoon sunlight'; sun.data.energy=2.4; sun.data.angle=math.radians(12); sun.rotation_euler=(math.radians(28),math.radians(-24),math.radians(-28))
bpy.ops.object.light_add(type='AREA',location=(-7,-10,10)); light=bpy.context.object; light.data.energy=1600; light.data.size=9; light.rotation_euler=(Vector((0,0,5))-light.location).to_track_quat('-Z','Y').to_euler()
bpy.ops.object.camera_add(location=(14,-23,14)); cam=bpy.context.object; cam.rotation_euler=(Vector((0,-.15,4.9))-cam.location).to_track_quat('-Z','Y').to_euler(); cam.data.type='ORTHO'; cam.data.ortho_scale=17.6
scene=bpy.context.scene; scene.camera=cam; scene.render.engine='CYCLES'; scene.cycles.samples=64; scene.render.resolution_x=1200; scene.render.resolution_y=1200; scene.render.resolution_percentage=100
