import bpy, math, random
from mathutils import Vector
bpy.ops.wm.read_factory_settings(use_empty=True)
random.seed(9)

def mat(name,c,rough=.65,metal=0):
    m=bpy.data.materials.new(name); m.diffuse_color=(*c,1); m.use_nodes=True
    p=m.node_tree.nodes.get('Principled BSDF'); p.inputs['Base Color'].default_value=(*c,1); p.inputs['Roughness'].default_value=rough; p.inputs['Metallic'].default_value=metal
    return m

def box(name,loc,size,m,bevel=0):
    bpy.ops.mesh.primitive_cube_add(size=1,location=loc); o=bpy.context.object; o.name=name; o.dimensions=size
    bpy.ops.object.transform_apply(location=False,rotation=False,scale=True); o.data.materials.append(m)
    if bevel:
        mod=o.modifiers.new('Worn edges','BEVEL'); mod.width=bevel; mod.segments=2; o.modifiers.new('Weighted normals','WEIGHTED_NORMAL')
    return o

def mesh(name,verts,faces,m):
    data=bpy.data.meshes.new(name); data.from_pydata(verts,[],faces); data.update(); o=bpy.data.objects.new(name,data); bpy.context.collection.objects.link(o); o.data.materials.append(m); return o

def rod(name,a,b,r,m):
    a,b=Vector(a),Vector(b); d=b-a
    bpy.ops.mesh.primitive_cylinder_add(vertices=16,radius=r,depth=d.length,location=(a+b)/2)
    o=bpy.context.object; o.name=name; o.rotation_euler=d.to_track_quat('Z','Y').to_euler(); o.data.materials.append(m); return o

def aim(o,p): o.rotation_euler=(Vector(p)-o.location).to_track_quat('-Z','Y').to_euler()
def area(name,loc,power,size,target):
    bpy.ops.object.light_add(type='AREA',location=loc); o=bpy.context.object; o.name=name; o.data.energy=power; o.data.size=size; aim(o,target)

plaster=mat('Lime plaster',(.81,.77,.65)); stone=mat('Cut limestone',(.57,.55,.46)); roof=mat('Slate roof',(.16,.21,.25)); roof2=mat('Slate variation',(.21,.27,.3))
wood=mat('Oak doors and pews',(.29,.135,.055)); metal=mat('Dark iron',(.075,.085,.08),.4,.65); bronze=mat('Bell bronze',(.49,.29,.09),.3,.7)
glass=mat('Amber leaded glass',(.43,.28,.095),.24,.2); p=glass.node_tree.nodes.get('Principled BSDF'); p.inputs['Emission Color'].default_value=(.3,.14,.025,1); p.inputs['Emission Strength'].default_value=.35
lawn=mat('Muted grass',(.27,.34,.19)); gravel=mat('Gravel path',(.56,.51,.41)); dark=mat('Interior shadow',(.1,.09,.07)); foliage=mat('Shrub foliage',(.17,.26,.1))

box('Landscape base',(0,0,-.22),(19,23,.4),lawn,.15)
box('Approach path',(0,-7.7,.015),(3.1,7,.1),gravel,.025)
box('Chapel stone foundation',(0,0,.28),(6.8,10.8,.55),stone,.07)
box('Interior stone floor',(0,0,.6),(6.15,10.2,.15),stone)
# Side walls are assembled around actual narrow openings, without boolean cuts.
centers=(-3.35,-1.1,1.15,3.4); opening=.68; bottom=1.75; top=3.85; walltop=4.7
for side in (-1,1):
    x=side*3.15
    box('Side wall below windows',(x,0,(.55+bottom)/2),(.3,10.3,bottom-.55),plaster)
    box('Side wall above windows',(x,0,(top+walltop)/2),(.3,10.3,walltop-top),plaster)
    ends=[-5.15]+[v for c in centers for v in (c-opening/2,c+opening/2)]+[5.15]
    for i in range(0,len(ends)-1,2):
        a,b=ends[i:i+2]; box('Wall pier',(x,(a+b)/2,(bottom+top)/2),(.3,b-a,top-bottom),plaster)
    for y in centers:
        box('Recessed narrow glazing',(x,y,(bottom+top)/2),(.055,.61,top-bottom-.08),glass)
        for dy in (-.4,.4): box('Window stone jamb',(x+side*.18,y+dy,(bottom+top)/2),(.18,.14,2.34),stone,.02)
        for z in (bottom-.08,top+.08): box('Window lintel and sill',(x+side*.19,y,z),(.24,.94,.16),stone,.02)
        for dy in (-.29,0,.29): box('Leaded vertical window bar',(x+side*.045,y+dy,2.8),(.06,.022,2.04),metal)
        for z in (2.28,2.8,3.32): box('Leaded cross bar',(x+side*.05,y,z),(.065,.61,.022),metal)
    for y in (-4.9,-2.25,2.25,4.9):
        box('Shallow stone buttress',(side*3.44,y,1.75),(.5,.46,2.6),stone,.035)
        box('Buttress cap',(side*3.44,y,3.1),(.57,.53,.14),stone,.025)

# Entrance wall has a real doorway; triangular masonry closes both gables.
for x in (-2.16,2.16): box('Front wall beside door',(x,-5,2.62),(1.98,.3,4.15),plaster)
box('Front door lintel wall',(0,-5,4.02),(2.34,.3,1.36),plaster)
box('Rear wall',(0,5,2.62),(6.3,.3,4.15),plaster)
for y in (-5,5):
    verts=[(-3.3,y-.15,4.7),(3.3,y-.15,4.7),(0,y-.15,6.7),(-3.3,y+.15,4.7),(3.3,y+.15,4.7),(0,y+.15,6.7)]
    mesh('Solid plaster gable',verts,[(0,2,1),(3,4,5),(0,1,4,3),(1,2,5,4),(2,0,3,5)],plaster)
for x in (-1.22,1.22): box('Entrance stone surround',(x,-5.2,1.98),(.22,.24,2.87),stone,.025)
box('Entrance lintel',(0,-5.2,3.48),(2.67,.28,.24),stone,.025)
for x in (-.55,.55):
    box('Oak entrance door',(x,-5.035,1.96),(1.065,.15,2.62),wood,.018)
    for i in range(5): box('Door plank joint',(x-.43+i*.215,-5.117,1.96),(.012,.014,2.5),dark)
    for z in (1.12,2.65): box('Iron strap hinge',(x,-5.135,z),(.86,.035,.075),metal,.01)
    rod('Door handle',(x+(.3 if x<0 else -.3),-5.17,1.77),(x+(.3 if x<0 else -.3),-5.17,2.03),.027,bronze)
for i in range(4):
    h=(i+1)*.15
    box('Entrance step',(0,-6.5+i*.34,h/2),(3.35,.36,h),stone,.025)
box('Entrance landing',(0,-5.36,.3),(3.35,.8,.6),stone,.025)

# Individually coursed slate roof over solid roof decks.
slope=2/3.3; angle=math.atan(slope)
for side in (-1,1):
    o=box('Pitched roof deck',(side*1.79,0,6.72-1.79*slope),(3.58*math.sqrt(1+slope*slope),11,.14),roof)
    o.rotation_euler.y=side*angle
    for row in range(10):
        x=side*(row+.5)*.358; z=6.83-abs(x)*slope
        for col in range(22):
            y=-5.25+col*.5
            o=box('Slate roof tile',(x,y,z),(.385*math.sqrt(1+slope*slope),.484,.04),roof2 if random.random()<.22 else roof)
            o.rotation_euler.y=side*angle
    box('Eaves fascia',(side*3.58,0,4.55),(.11,11.15,.23),wood,.015)
for i in range(23): rod('Ridge cap',(0,-5.5+i*.48,6.83),(0,-5.5+(i+1)*.48,6.83),.115,roof)

# Bell tower rises through the front roof; four open belfry bays expose the bell.
box('Tower lower shaft',(0,-3.75,5.63),(1.95,1.95,2.5),plaster,.025)
box('Tower lower cornice',(0,-3.75,6.81),(2.22,2.22,.22),stone,.025)
for x in (-.83,.83):
    for y in (-4.58,-2.92): box('Belfry corner pier',(x,y,7.64),(.3,.3,1.56),stone,.02)
box('Belfry upper cornice',(0,-3.75,8.47),(2.25,2.25,.22),stone,.035)
beam_y=-3.75
box('Bell hanging beam',(0,beam_y,8.2),(1.68,.22,.2),wood,.02)
rod('Bell hanger',(0,beam_y,8.17),(0,beam_y,7.86),.055,metal)
# Lathed bell profile includes an inner surface and open mouth.
profile=[(.11,7.95),(.2,7.87),(.23,7.67),(.29,7.42),(.43,7.22),(.49,7.17),(.48,7.1),(.41,7.1),(.36,7.22),(.23,7.43),(.17,7.67),(.13,7.82),(.07,7.86)]
verts=[]; seg=48
for r,z in profile:
    for j in range(seg):
        a=j*math.tau/seg; verts.append((r*math.cos(a),beam_y+r*math.sin(a),z))
faces=[]
for i in range(len(profile)-1):
    for j in range(seg): faces.append((i*seg+j,i*seg+(j+1)%seg,(i+1)*seg+(j+1)%seg,(i+1)*seg+j))
bell=mesh('Hollow bronze bell',verts,faces,bronze)
for p in bell.data.polygons: p.use_smooth=True
rod('Bell clapper',(0,beam_y,7.67),(0,beam_y,7.04),.035,metal)
bpy.ops.mesh.primitive_uv_sphere_add(segments=16,ring_count=8,radius=.095,location=(0,beam_y,7.08)); bpy.context.object.data.materials.append(bronze)
verts=[(-1.27,-5.02,8.58),(1.27,-5.02,8.58),(1.27,-2.48,8.58),(-1.27,-2.48,8.58),(0,-3.75,10.03)]
mesh('Tower pyramidal slate roof',verts,[(0,1,4),(1,2,4),(2,3,4),(3,0,4),(3,2,1,0)],roof)
rod('Tower cross upright',(0,-3.75,9.96),(0,-3.75,10.95),.038,bronze)
rod('Tower cross arms',(-.28,-3.75,10.63),(.28,-3.75,10.63),.038,bronze)

for y in (-2.8,-1.5,-.2,1.1,2.4):
    for x in (-1.65,1.65):
        box('Interior pew seat',(x,y,1.13),(1.95,.45,.1),wood,.02)
        box('Interior pew back',(x,y+.21,1.48),(1.95,.09,.62),wood,.02)
        for dx in (-.72,.72): box('Pew leg',(x+dx,y,.9),(.1,.35,.5),wood)
box('Altar',(0,3.8,1.12),(1.8,.8,.85),stone,.04)
for x in (-5,5):
    for y in (-3,1.5,4):
        bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=2,radius=.7,location=(x,y,.5)); o=bpy.context.object; o.name='Chapel garden shrub'; o.scale=(1,.9,.85); o.data.materials.append(foliage)
area('Warm afternoon',(-8,-10,16),2200,8,(0,0,3)); area('Cool sky fill',(8,4,12),1500,9,(0,0,4))
bpy.ops.object.camera_add(location=(16,-22,14)); cam=bpy.context.object; aim(cam,(0,-.3,4)); cam.data.type='ORTHO'; cam.data.ortho_scale=21
scene=bpy.context.scene; scene.camera=cam; scene.render.engine='CYCLES'; scene.cycles.samples=64; scene.world.color=(.3,.3,.3)
scene.render.resolution_x=1300; scene.render.resolution_y=1500; scene.render.resolution_percentage=100; scene.view_settings.view_transform='AgX'
