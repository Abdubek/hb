import bpy, math
from mathutils import Vector
bpy.ops.object.select_all(action='SELECT'); bpy.ops.object.delete(use_global=False)

def mat(n,c,metal=0,rough=.5,emit=0):
    m=bpy.data.materials.new(n); m.diffuse_color=(*c,1); m.use_nodes=True; p=m.node_tree.nodes.get('Principled BSDF')
    p.inputs['Base Color'].default_value=(*c,1); p.inputs['Metallic'].default_value=metal; p.inputs['Roughness'].default_value=rough
    if emit: p.inputs['Emission Color'].default_value=(*c,1); p.inputs['Emission Strength'].default_value=emit
    return m

def box(n,p,s,m,b=.025):
    bpy.ops.mesh.primitive_cube_add(size=1,location=p); o=bpy.context.object; o.name=n; o.dimensions=s; bpy.ops.object.transform_apply(location=False,rotation=False,scale=True); o.data.materials.append(m)
    if b:
        q=o.modifiers.new('Soft corners','BEVEL'); q.width=b; q.segments=3; o.modifiers.new('Weighted normals','WEIGHTED_NORMAL')
    return o

def rod(n,a,b,r,m,v=24):
    a,b=Vector(a),Vector(b); d=b-a; bpy.ops.mesh.primitive_cylinder_add(vertices=v,radius=r,depth=d.length,location=(a+b)/2)
    o=bpy.context.object; o.name=n; o.rotation_euler=d.to_track_quat('Z','Y').to_euler(); o.data.materials.append(m)
    q=o.modifiers.new('Edge bevel','BEVEL'); q.width=min(.012,r*.2); q.segments=2; o.modifiers.new('Normals','WEIGHTED_NORMAL'); return o

def ellipsoid(n,p,s,m):
    bpy.ops.mesh.primitive_uv_sphere_add(segments=32,ring_count=20,location=p); o=bpy.context.object; o.name=n; o.scale=s; o.data.materials.append(m)
    for f in o.data.polygons: f.use_smooth=True
    return o

def oval(n,p,radii,depth,m):
    bpy.ops.mesh.primitive_cylinder_add(vertices=96,radius=1,depth=depth,location=p); o=bpy.context.object; o.name=n; o.scale=(radii[0],radii[1],1)
    bpy.ops.object.transform_apply(location=False,rotation=False,scale=True); o.data.materials.append(m)
    q=o.modifiers.new('Rounded perimeter','BEVEL'); q.width=.035; q.segments=3; o.modifiers.new('Normals','WEIGHTED_NORMAL'); return o

def curve(n,points,r,m):
    c=bpy.data.curves.new(n,'CURVE'); c.dimensions='3D'; c.bevel_depth=r; c.bevel_resolution=4
    s=c.splines.new('BEZIER'); s.bezier_points.add(len(points)-1)
    for p,co in zip(s.bezier_points,points): p.co=co; p.handle_left_type='AUTO'; p.handle_right_type='AUTO'
    o=bpy.data.objects.new(n,c); bpy.context.collection.objects.link(o); o.data.materials.append(m); return o

def area(n,p,target,power,size,c):
    bpy.ops.object.light_add(type='AREA',location=p); o=bpy.context.object; o.name=n; o.data.energy=power; o.data.size=size; o.data.color=c
    o.rotation_euler=(Vector(target)-o.location).to_track_quat('-Z','Y').to_euler()

plaster=mat('Warm mineral plaster',(.70,.65,.54)); wood=mat('Smoked oak',(.22,.105,.046)); floorwood=mat('Natural oak floor',(.46,.30,.16)); walnut=mat('Walnut table',(.26,.12,.057))
fabric=mat('Sage boucle upholstery',(.32,.40,.31),rough=.92); piping=mat('Upholstery welting',(.22,.29,.22)); brass=mat('Champagne brass',(.60,.43,.20),.78,.27)
black=mat('Dark bronze',(.07,.055,.034),.75,.3); rug=mat('Wool rug',(.62,.56,.44),rough=1); ceramic=mat('Ivory ceramic',(.87,.82,.68),rough=.24)
glow=mat('Opal globes',(1,.86,.65),rough=.3,emit=3); olive=mat('Olive foliage',(.15,.22,.085)); terracotta=mat('Terracotta artwork',(.58,.23,.12)); artcream=mat('Artwork linen',(.83,.75,.60))
# Architectural room, with open front and right sides.
box('Floor slab',(0,0,-.16),(10,8,.28),wood)
for i in range(25):
    for j in range(4): box('Oak floor plank',(-4.8+i*.4,-3+j*2,.015),(.388,1.986,.065),floorwood,.006)
box('Rear plaster wall',(0,4.0,2.4),(10,.18,4.8),plaster)
box('Left plaster wall',(-5,0,2.4),(.18,8.0,4.8),plaster)
box('Rear baseboard',(0,3.87,.16),(9.95,.08,.25),wood)
box('Left baseboard',(-4.87,0,.16),(.08,7.9,.25),wood)
# Tall decorative wall battens.
for x in [-4.5,-3,-1.5,0,1.5,3,4.5]: box('Wall batten',(x,3.875,2.43),(.045,.05,4.15),wood,.008)
for z in [.38,4.48]: box('Wall horizontal molding',(0,3.875,z),(9.4,.05,.045),wood,.008)
box('Large woven rug',(0,-.25,.077),(7.9,5.35,.035),rug,.10)
for y in [-2.77,2.27]: box('Rug woven border',(0,y,.099),(7.55,.06,.008),wood,.003)
# Oval table with twin fluted pedestal bases.
oval('Oval walnut dining top',(0,0,1.29),(2.65,1.28),.15,walnut)
oval('Recessed table apron',(0,0,1.17),(2.43,1.09),.13,wood)
for x in [-1.42,1.42]:
    oval('Pedestal foot',(x,0,.16),(.57,.67),.13,wood)
    oval('Pedestal core',(x,0,.66),(.38,.49),.96,walnut)
    for i in range(24):
        a=math.tau*i/24; rod('Pedestal flute',(x+.38*math.cos(a),.49*math.sin(a),.23),(x+.38*math.cos(a),.49*math.sin(a),1.12),.038,wood,12)
# Local chair coordinates: front is -Y; rotate each chair to face the table.
def chair(cx,cy,theta):
    def pos(x,y,z): return (cx+x*math.cos(theta)-y*math.sin(theta),cy+x*math.sin(theta)+y*math.cos(theta),z)
    def cb(n,p,s,m,b):
        o=box(n,pos(*p),s,m,b); o.rotation_euler.z=theta; return o
    cb('Chair wood seat frame',(0,0,.60),(.81,.82,.12),wood,.065)
    cb('Chair upholstered seat',(0,-.025,.70),(.86,.86,.18),fabric,.085)
    for x in [-.30,.30]:
        for y in [-.29,.29]: rod('Tapered-looking splayed chair leg',pos(x,y,.61),pos(x*1.24,y*1.24,.10),.037,wood)
        rod('Rear back support',pos(x,.30,.58),pos(x,.40,1.38),.030,wood)
    # Upholstered curved back, built as a shallow annular strip.
    verts=[]; N=24
    for z in [.96,1.56]:
        for radius in [.56,.68]:
            for i in range(N+1):
                a=math.radians(43+94*i/N); verts.append(pos(radius*math.cos(a),-.10+radius*math.sin(a),z))
    stride=N+1; faces=[]
    for i in range(N):
        faces.extend([(i,i+1,2*stride+i+1,2*stride+i),(stride+i,3*stride+i,3*stride+i+1,stride+i+1),(i,stride+i,stride+i+1,i+1),(2*stride+i,2*stride+i+1,3*stride+i+1,3*stride+i)])
    faces.extend([(0,2*stride,3*stride,stride),(N,stride+N,3*stride+N,2*stride+N)])
    me=bpy.data.meshes.new('Curved upholstered chair back'); me.from_pydata(verts,[],faces); me.update(); o=bpy.data.objects.new('Wraparound upholstered back',me); bpy.context.collection.objects.link(o); o.data.materials.append(fabric)
    q=o.modifiers.new('Cushioned back edges','BEVEL'); q.width=.045; q.segments=3; o.modifiers.new('Normals','WEIGHTED_NORMAL')
    points=[pos(.625*math.cos(math.radians(43+94*i/24)),-.10+.625*math.sin(math.radians(43+94*i/24)),1.56) for i in range(25)]
    curve('Backrest piping',points,.011,piping)
for x in [-1.65,0,1.65]:
    chair(x,1.83,0); chair(x,-1.83,math.pi)
chair(-3.17,0,math.pi/2); chair(3.17,0,-math.pi/2)
# Table settings: shallow dishes, folded napkins, and brass cutlery.
for x in [-1.65,0,1.65]:
    for y in [-.84,.84]:
        oval('Dinner plate',(x,y,1.385),(.255,.255),.033,ceramic)
        oval('Plate well',(x,y,1.405),(.19,.19),.012,artcream)
        box('Folded linen napkin',(x,y,1.427),(.25,.14,.023),rug,.008)
        for dx in [-.34,.34]: rod('Cutlery',(x+dx,y-.15,1.39),(x+dx,y+.14,1.39),.012,brass,12)
# Central sculptural ceramic vase and branches.
ellipsoid('Ceramic centerpiece',(0,0,1.60),(.22,.22,.25),ceramic)
rod('Vase neck',(0,0,1.65),(0,0,1.88),.075,ceramic,32)
rod('Dark vase opening',(0,0,1.88),(0,0,1.884),.056,wood,32)
for i in range(5):
    a=i*2.4; end=(.40*math.cos(a),.32*math.sin(a),2.10+.12*(i%3))
    curve('Olive branch',[(0,0,1.82),(end[0]*.4,end[1]*.4,2.02),end],.009,wood)
    for t in [.6,.85,1.0]:
        p=(end[0]*t,end[1]*t,1.86+(end[2]-1.86)*t); o=ellipsoid('Olive leaf',p,(.10,.028,.018),olive); o.rotation_euler.z=a+.5
# Sculptural chandelier: looping brass arms with opal pearls.
rod('Ceiling canopy',(0,0,4.58),(0,0,4.68),.24,black,48)
rod('Chandelier stem',(0,0,3.33),(0,0,4.60),.033,brass)
ellipsoid('Central chandelier hub',(0,0,3.34),(.16,.16,.16),brass)
for i in range(9):
    a=math.tau*i/9; reach=1.35+.27*(i%2); z=3.22+.23*math.sin(a*2)
    p=(reach*math.cos(a),reach*.68*math.sin(a),z)
    curve('Sweeping chandelier arm',[(0,0,3.34),(.48*math.cos(a-.4),.42*math.sin(a-.4),3.12),(p[0]*.86,p[1]*.86,z+.18),p],.023,brass)
    ellipsoid('Opal chandelier globe',p,(.17,.17,.17),glow)
    bpy.ops.object.light_add(type='POINT',location=p); bpy.context.object.name='Globe illumination'; bpy.context.object.data.energy=13; bpy.context.object.data.color=(1,.79,.53); bpy.context.object.data.shadow_soft_size=.19
# Sideboard and abstract framed art.
box('Sideboard carcass',(.3,3.25,.73),(4.3,.72,1.08),wood,.045)
for x in [-1.28,-.23,.82,1.87]:
    box('Sideboard door',(x,2.862,.76),(1.01,.05,.94),walnut)
    rod('Door pull',(x+.33,2.81,.69),(x+.33,2.81,.90),.012,brass)
for x in [-1.55,2.15]:
    for y in [3.00,3.5]: rod('Sideboard foot',(x,y,.1),(x,y,.26),.035,brass)
box('Sideboard stone top',(.3,3.25,1.31),(4.4,.78,.09),ceramic)
box('Artwork outer frame',(.3,3.77,2.96),(2.85,.11,1.94),black)
box('Artwork canvas',(.3,3.697,2.96),(2.69,.025,1.78),artcream)
for x,z,sx,sz,m in [(-.35,3.15,.60,.55,terracotta),(.85,2.80,.48,.61,wood),(.28,3.25,.25,.25,plaster)]: ellipsoid('Abstract relief shape',(x,3.67,z),(sx,.025,sz),m)
area('Warm chandelier pool',(0,0,3.05),(0,0,0),220,2.4,(1,.80,.56))
area('Daylight key',(2,-4,6),(0,0,1),1400,5,(1,.91,.78))
area('Soft side fill',(-3,-1,4),(0,1,1),650,4,(.76,.84,1))
scene=bpy.context.scene; scene.world.color=(.20,.20,.20)
bpy.ops.object.camera_add(location=(10,-13,10)); cam=bpy.context.object; cam.rotation_euler=(Vector((0,.4,1.8))-cam.location).to_track_quat('-Z','Y').to_euler(); cam.data.type='ORTHO'; cam.data.ortho_scale=13.9; scene.camera=cam
scene.render.engine='CYCLES'; scene.cycles.samples=64; scene.render.resolution_x=1500; scene.render.resolution_y=1200; scene.render.resolution_percentage=100; scene.view_settings.view_transform='AgX'
