import bpy, math
from mathutils import Vector
bpy.ops.wm.read_factory_settings(use_empty=True)

def mat(name,color,metal=0,rough=.5):
    m=bpy.data.materials.new(name); m.diffuse_color=(*color,1); m.use_nodes=True; p=m.node_tree.nodes.get('Principled BSDF'); p.inputs['Base Color'].default_value=(*color,1); p.inputs['Metallic'].default_value=metal; p.inputs['Roughness'].default_value=rough; return m

def box(name,loc,size,material,bevel=0):
    bpy.ops.mesh.primitive_cube_add(size=1,location=loc); o=bpy.context.object; o.name=name; o.dimensions=size; bpy.ops.object.transform_apply(location=False,rotation=False,scale=True); o.data.materials.append(material)
    if bevel:
        b=o.modifiers.new('Eased corners','BEVEL'); b.width=bevel; b.segments=2; o.modifiers.new('Weighted normals','WEIGHTED_NORMAL')
    return o

def beam(name,a,b,width,depth,material):
    a,b=Vector(a),Vector(b); o=box(name,(a+b)/2,(width,depth,(b-a).length),material,.012); o.rotation_euler=(b-a).to_track_quat('Z','Y').to_euler(); return o

def bolt(name,loc,axis,material,r=.018):
    bpy.ops.mesh.primitive_cylinder_add(vertices=6,radius=r,depth=.013,location=loc); o=bpy.context.object; o.name=name; o.rotation_euler=Vector(axis).to_track_quat('Z','Y').to_euler(); o.data.materials.append(material)

wood=mat('Warm weathered timber',(.36,.20,.095),0,.72); wood2=mat('Alternate deck boards',(.44,.27,.14),0,.77); endgrain=mat('Dark timber rails',(.25,.13,.055),0,.7); iron=mat('Graphite brackets',(.075,.09,.10),.72,.4); zinc=mat('Zinc bolt heads',(.55,.60,.61),.8,.3); stone=mat('Abutment stone',(.38,.40,.36),0,.95); earth=mat('Earth bank',(.22,.17,.105),0,1); grass=mat('Mossy bank',(.22,.32,.13),0,1); water=mat('Stream blue green',(.045,.23,.24),.3,.19); ripple=mat('Water ripple highlights',(.19,.38,.37),.25,.25)
# The span runs along X: 4.5 m long, 1.6 m deck width.
def height(x): return .66+.19*(1-(x/2.25)**2)
box('Left bank',(-2.92,0,.01),(1.45,3.6,.6),earth,.12)
box('Right bank',(2.92,0,.01),(1.45,3.6,.6),earth,.12)
for x in [-2.92,2.92]: box('Grassy bank top',(x,0,.322),(1.44,3.6,.045),grass,.035)
box('Stream bed',(0,0,-.23),(4.4,3.6,.16),stone,.07)
box('Water surface',(0,0,-.133),(4.38,3.56,.026),water,.025)
for i in range(13):
    x=-1.9+(i%5)*.83; y=-1.5+i*.25
    box('Small stream ripple',(x,y,-.117),(.12+(i%3)*.09,.013,.002),ripple,.006)
# Stone bearing walls built with staggered masonry joints.
for sign in [-1,1]:
    for row in range(2):
        for j in range(5):
            box('Abutment masonry block',(sign*2.15,-.96+j*.48,.12+row*.23),(.40,.468,.218),stone,.018)
    box('Abutment coping',(sign*2.15,0,.46),(.50,2.45,.12),stone,.025)
# Segmented curved timber stringers under the cambered deck.
segments=24
for y in [-.60,.60]:
    for i in range(segments):
        a=-2.25+4.5*i/segments; b=-2.25+4.5*(i+1)/segments
        beam('Structural timber stringer',(a,y,height(a)-.20),(b,y,height(b)-.20),.16,.27,endgrain)
# Individual transverse planks, tangent to the gentle camber.
for i in range(30):
    x=-2.25+(i+.5)*.15; o=box('Deck plank %02d'%(i+1),(x,0,height(x)-.035),(.144,1.65,.07),wood if i%3 else wood2,.008)
    o.rotation_euler.y=-math.atan(-.38*x/(2.25**2))
    for y in [-.60,.60]: bolt('Deck fixing',(x,y,height(x)+.003),(0,0,1),zinc,.009)
# Six posts per side, caps, steel shoes and two continuous rails.
postxs=[-2.18,-1.308,-.436,.436,1.308,2.18]
for y in [-.85,.85]:
    side=1 if y>0 else -1
    for x in postxs:
        z=height(x)
        box('Square timber guard post',(x,y,z+.48),(.105,.105,1.12),wood,.009)
        box('Post cap',(x,y,z+1.055),(.145,.145,.045),endgrain,.014)
        box('Steel post shoe',(x,y,z-.015),(.126,.128,.21),iron,.006)
        for dz in [-.065,.04]: bolt('Post shoe bolt',(x,y+side*.072,z+dz),(0,side,0),zinc)
    for a,b in zip(postxs[:-1],postxs[1:]):
        beam('Upper handrail',(a,y,height(a)+1.005),(b,y,height(b)+1.005),.135,.095,endgrain)
        beam('Lower rail',(a,y,height(a)+.22),(b,y,height(b)+.22),.075,.065,wood)
        for k in range(1,6):
            x=a+(b-a)*k/6; t=(x-a)/(b-a); z=(1-t)*height(a)+t*height(b)
            beam('Vertical guard baluster',(x,y,z+.26),(x,y,z+.97),.035,.035,wood)
# Cross ties and underside diagonal steel bracing.
for x in [-1.74,0,1.74]: beam('Underdeck cross tie',(x,-.75,height(x)-.24),(x,.75,height(x)-.24),.10,.12,endgrain)
for a,b in [(-1.74,0),(0,1.74)]:
    beam('Underdeck diagonal brace',(a,-.59,height(a)-.30),(b,.59,height(b)-.30),.035,.035,iron)
    beam('Underdeck diagonal brace',(a,.59,height(a)-.30),(b,-.59,height(b)-.30),.035,.035,iron)
# Timber approach steps meet the banks at each end.
for sign in [-1,1]:
    box('Approach lower step',(sign*2.79,0,.38),(.38,1.67,.09),wood2,.012)
    box('Approach upper step',(sign*2.44,0,.50),(.35,1.67,.12),wood,.012)
# A handful of low polygon river stones.
for i in range(14):
    sign=-1 if i%2 else 1; x=sign*(1.80+.14*math.sin(i*2)); y=-1.55+(i//2)*.5
    bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=1,radius=1,location=(x,y,-.06)); o=bpy.context.object; o.name='Stream edge stone'; o.scale=(.17,.12,.105); o.rotation_euler.z=i*.72; o.data.materials.append(stone)
scene=bpy.context.scene; scene.world.color=(.22,.25,.28)
for loc,power,size in [((1,-4,7),1100,5),((-4,1,5),650,4),((3,4,6),850,4)]:
    bpy.ops.object.light_add(type='AREA',location=loc); o=bpy.context.object; o.data.energy=power; o.data.size=size; o.rotation_euler=(Vector((0,0,.6))-o.location).to_track_quat('-Z','Y').to_euler()
bpy.ops.object.camera_add(location=(7,-8,5.5)); cam=bpy.context.object; cam.rotation_euler=(Vector((0,0,.60))-cam.location).to_track_quat('-Z','Y').to_euler(); cam.data.type='ORTHO'; cam.data.ortho_scale=8.1; scene.camera=cam
scene.unit_settings.system='METRIC'; scene.render.resolution_x=1500; scene.render.resolution_y=1100; scene.render.resolution_percentage=100
