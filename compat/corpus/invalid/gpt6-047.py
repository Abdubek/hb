import bpy, math, random
from mathutils import Vector
bpy.ops.wm.read_factory_settings(use_empty=True)
random.seed(47)

def mat(name,c,metal=0,rough=.5):
    m=bpy.data.materials.new(name); m.diffuse_color=(*c,1); m.use_nodes=True; p=m.node_tree.nodes.get('Principled BSDF'); p.inputs['Base Color'].default_value=(*c,1); p.inputs['Metallic'].default_value=metal; p.inputs['Roughness'].default_value=rough; return m

def box(name,loc,dims,m,bevel=.04):
    bpy.ops.mesh.primitive_cube_add(size=1,location=loc); o=bpy.context.object; o.name=name; o.dimensions=dims; bpy.ops.object.transform_apply(location=False,rotation=False,scale=True); o.data.materials.append(m)
    if bevel:
        b=o.modifiers.new('Rounded edges','BEVEL'); b.width=bevel; b.segments=3; o.modifiers.new('Normals','WEIGHTED_NORMAL')
    return o

def cyl(name,loc,r,depth,m):
    bpy.ops.mesh.primitive_cylinder_add(vertices=64,radius=r,depth=depth,location=loc); o=bpy.context.object; o.name=name; o.data.materials.append(m); b=o.modifiers.new('Edge dressing','BEVEL'); b.width=.025; b.segments=3; o.modifiers.new('Normals','WEIGHTED_NORMAL'); return o

def ring(name,rout,rin,z0,z1,m,n=96):
    verts=[]
    for r,z in [(rout,z0),(rout,z1),(rin,z1),(rin,z0)]:
        verts.extend([(r*math.cos(i*math.tau/n),r*math.sin(i*math.tau/n),z) for i in range(n)])
    faces=[]
    for j in range(4):
        for i in range(n):
            k=(i+1)%n; a=j*n; b=((j+1)%4)*n; faces.append((a+i,a+k,b+k,b+i))
    mesh=bpy.data.meshes.new(name); mesh.from_pydata(verts,[],faces); mesh.update(); o=bpy.data.objects.new(name,mesh); bpy.context.collection.objects.link(o); o.data.materials.append(m); b=o.modifiers.new('Stone edge radius','BEVEL'); b.width=.025; b.segments=2; o.modifiers.new('Normals','WEIGHTED_NORMAL'); return o

def tube(name,points,r,m):
    cu=bpy.data.curves.new(name,'CURVE'); cu.dimensions='3D'; cu.resolution_u=2; cu.bevel_depth=r; cu.bevel_resolution=3; sp=cu.splines.new('POLY'); sp.points.add(len(points)-1)
    for p,co in zip(sp.points,points): p.co=(*co,1)
    o=bpy.data.objects.new(name,cu); bpy.context.collection.objects.link(o); o.data.materials.append(m)

def aim(o,p): o.rotation_euler=(Vector(p)-o.location).to_track_quat('-Z','Y').to_euler()
stone=mat('Limestone',(.66,.61,.49)); coping=mat('Pale coping',(.85,.79,.65)); mortar=mat('Paving joints',(.29,.30,.27)); soil=mat('Dark soil',(.09,.055,.028)); plaster=mat('Warm courtyard plaster',(.75,.68,.54)); metal=mat('Dark bronze',(.10,.13,.115),.65); wood=mat('Bench cedar',(.38,.18,.065)); leaves=[mat('Leaf '+str(i),c) for i,c in enumerate([(.14,.30,.09),(.23,.39,.12),(.07,.20,.105)])]; water=mat('Fountain water',(.055,.27,.28),.12,.12)
p=water.node_tree.nodes.get('Principled BSDF'); p.inputs['Transmission Weight'].default_value=.55; p.inputs['IOR'].default_value=1.333
noise=water.node_tree.nodes.new('ShaderNodeTexNoise'); noise.inputs['Scale'].default_value=28; bump=water.node_tree.nodes.new('ShaderNodeBump'); bump.inputs['Strength'].default_value=.16; bump.inputs['Distance'].default_value=.025; water.node_tree.links.new(noise.outputs['Fac'],bump.inputs['Height']); water.node_tree.links.new(bump.outputs['Normal'],p.inputs['Normal'])
box('Courtyard foundation',(0,0,-.16),(13,13,.3),mortar)
pavers=[mat('Paver tone '+str(i),(.51+i*.018,.49+i*.017,.43+i*.014)) for i in range(4)]
for ix in range(16):
    for iy in range(16): box('Square paving slab',((ix-7.5)*.78,(iy-7.5)*.78,.025),(.755,.755,.07),random.choice(pavers),.012)
for x in (-6.4,6.4):
    box('Courtyard side wall',(x,0,1.0),(.22,13,2),plaster); box('Side wall cap',(x,0,2.04),(.34,13.1,.13),coping)
box('Rear courtyard wall',(0,6.4,1),(13,.22,2),plaster); box('Rear cap',(0,6.4,2.04),(13.1,.34,.13),coping)
for x in (-6.4,-3.2,0,3.2,6.4): box('Rear wall pier',(x,6.3,1.15),(.45,.45,2.3),stone)
cyl('Fountain circular foundation',(0,0,.15),2.35,.20,stone)
cyl('Basin floor',(0,0,.27),2.05,.18,stone)
ring('Thick basin wall',2.14,1.89,.22,.77,stone)
ring('Wide basin coping',2.23,1.84,.74,.89,coping)
cyl('Pool water',(0,0,.625),1.895,.045,water)
cyl('Central pedestal foot',(0,0,.72),.54,.28,coping)
cyl('Central column',(0,0,1.17),.23,.8,stone)
cyl('Upper bowl base',(0,0,1.57),.80,.14,stone)
ring('Upper bowl curved rim',.83,.71,1.57,1.86,coping)
cyl('Upper bowl water',(0,0,1.78),.71,.035,water)
cyl('Fountain nozzle',(0,0,1.88),.075,.22,metal)
for i in range(8):
    a=i*math.tau/8
    points=[]
    for j in range(25):
        t=j/24; r=.055+.48*t; z=1.99+1.25*t-1.45*t*t; points.append((r*math.cos(a),r*math.sin(a),z))
    tube('Crown water jet',points,.018,water)
    points=[]
    for j in range(25):
        t=j/24; r=.77+.68*t; z=1.79+.12*t-1.28*t*t; points.append((r*math.cos(a),r*math.sin(a),z))
    tube('Overflow water stream',points,.023,water)
    for radius in (.12,.22,.34):
        bpy.ops.mesh.primitive_torus_add(major_radius=radius,minor_radius=.007,major_segments=40,minor_segments=6,location=(1.42*math.cos(a),1.42*math.sin(a),.653)); bpy.context.object.name='Splash ripple'; bpy.context.object.data.materials.append(water)
for px,py,sx,sy in [(-4.7,-3,1.65,2.5),(4.7,-3,1.65,2.5),(-4.7,2.2,1.65,2.7),(4.7,2.2,1.65,2.7),(-1.6,4.9,2.4,1.3),(1.6,4.9,2.4,1.3)]:
    box('Planter base',(px,py,.21),(sx,sy,.25),stone)
    for dx in (-1,1): box('Planter side',(px+dx*(sx/2-.09),py,.52),(.18,sy,.65),stone)
    for dy in (-1,1): box('Planter end',(px,py+dy*(sy/2-.09),.52),(sx-.3,.18,.65),stone)
    box('Exposed soil',(px,py,.75),(sx-.34,sy-.34,.12),soil,.015)
    for dx in (-1,1): box('Planter coping',(px+dx*(sx/2-.09),py,.86),(.24,sy+.08,.12),coping,.025)
    for dy in (-1,1): box('Planter coping',(px,py+dy*(sy/2-.09),.86),(sx-.3,.24,.12),coping,.025)
    for j in range(15):
        x=px+random.uniform(-sx*.32,sx*.32); y=py+random.uniform(-sy*.32,sy*.32)
        bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=2,radius=1,location=(x,y,1.0+random.uniform(0,.25))); o=bpy.context.object; o.name='Dense shrub foliage'; o.scale=(random.uniform(.23,.38),random.uniform(.23,.38),random.uniform(.3,.6)); o.data.materials.append(random.choice(leaves))
for x in (-2.4,2.4):
    for dx in (-.66,.66): box('Bench leg',(x+dx,-3.65,.32),(.10,.56,.55),metal,.02)
    for j in range(4): box('Bench seat slat',(x,-3.9+j*.16,.63),(1.85,.135,.09),wood,.025)
    for dx in (-.78,.78): box('Back support',(x+dx,-3.93,.96),(.055,.055,.75),metal,.01)
    for z in (.96,1.16): box('Bench back slat',(x,-3.94,z),(1.85,.08,.16),wood,.025)
bpy.ops.object.light_add(type='SUN',location=(3,-4,10)); bpy.context.object.data.energy=2.3; bpy.context.object.rotation_euler=(.48,-.35,-.4); bpy.context.object.data.angle=.12
bpy.ops.object.light_add(type='AREA',location=(0,-2,10)); bpy.context.object.data.energy=1200; bpy.context.object.data.size=9
bpy.ops.object.camera_add(location=(15,-19,15)); camera=bpy.context.object; aim(camera,(0,0,.6)); camera.data.type='ORTHO'; camera.data.ortho_scale=19
scene=bpy.context.scene; scene.camera=camera; scene.render.engine='CYCLES'; scene.cycles.samples=64; scene.world.color=(.28,.28,.28); scene.render.resolution_x=1600; scene.render.resolution_y=1200; scene.render.resolution_percentage=100
