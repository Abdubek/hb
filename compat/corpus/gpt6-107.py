import bpy, math, random
from mathutils import Vector
random.seed(107)
bpy.ops.object.select_all(action='SELECT'); bpy.ops.object.delete(use_global=False)

def mat(name,color,metal=0,rough=.5):
    m=bpy.data.materials.new(name); m.diffuse_color=(*color,1); m.use_nodes=True; p=m.node_tree.nodes.get('Principled BSDF'); p.inputs['Base Color'].default_value=(*color,1); p.inputs['Metallic'].default_value=metal; p.inputs['Roughness'].default_value=rough; return m

def box(name,loc,size,material,bevel=0):
    bpy.ops.mesh.primitive_cube_add(size=1,location=loc); o=bpy.context.object; o.name=name; o.dimensions=size; bpy.ops.object.transform_apply(location=False,rotation=False,scale=True); o.data.materials.append(material)
    if bevel:
        b=o.modifiers.new('Edge highlights','BEVEL'); b.width=bevel; b.segments=2; o.modifiers.new('Weighted normals','WEIGHTED_NORMAL')
    return o

def rod(name,a,b,r,material):
    a,b=Vector(a),Vector(b); bpy.ops.mesh.primitive_cylinder_add(vertices=16,radius=r,depth=(b-a).length,location=(a+b)/2); o=bpy.context.object; o.name=name; o.rotation_euler=(b-a).to_track_quat('Z','Y').to_euler(); o.data.materials.append(material); return o

def area(name,loc,power,size,target):
    bpy.ops.object.light_add(type='AREA',location=loc); o=bpy.context.object; o.name=name; o.data.energy=power; o.data.size=size; o.rotation_euler=(Vector(target)-o.location).to_track_quat('-Z','Y').to_euler()

concrete=mat('Warm limestone',(.56,.54,.47)); paving=mat('Pale plaza stone',(.65,.65,.6)); joint=mat('Paving joint',(.33,.35,.34)); bronze=mat('Champagne anodized fins',(.49,.38,.23),.75,.29); frame=mat('Dark mullions',(.075,.095,.105),.75,.3); wood=mat('Bench timber',(.34,.18,.08)); foliage=mat('Tree canopy',(.19,.3,.12)); trunk=mat('Tree bark',(.2,.13,.07)); soil=mat('Planting soil',(.12,.095,.06)); black=mat('Dark metal',(.04,.05,.05),.65,.34)
glazing=[mat('Glass tone %02d'%i,(.10+i*.014,.19+i*.017,.23+i*.019),.62,.19) for i in range(5)]
# Urban base with a precisely jointed pedestrian plaza.
box('City ground',(0,0,-.25),(220,220,.4),joint)
box('Plaza foundation',(0,0,-.015),(35,29,.3),concrete,.1)
for ix in range(23):
    for iy in range(19):
        x=-16.5+ix*1.5; y=-13.5+iy*1.5
        box('Plaza paving slab',(x,y,.156),(1.476,1.476,.055),paving)
# Tower: 22 levels over a two-story glazed lobby.
box('Tower structural core',(0,0,38),(10.9,8.9,68),frame)
box('Lobby interior',(0,0,2.95),(10.6,8.6,5.6),concrete)
for face in [-1,1]:
    for i in range(10):
        x=-5.4+i*1.2
        box('Lobby glass front and rear',(x,face*4.82,2.85),(1.15,.08,5.35),glazing[3])
        box('Lobby vertical mullion',(x-.59,face*4.88,2.85),(.055,.12,5.5),frame)
    for i in range(8):
        y=-4.2+i*1.2
        box('Lobby side glazing',(face*6.02,y,2.85),(.08,1.15,5.35),glazing[3])
for floor in range(22):
    z=5.7+floor*3.05
    box('Continuous floor edge',(0,0,z),(12.35,9.95,.2),bronze,.025)
    for face in [-1,1]:
        for bay in range(10):
            x=-5.4+bay*1.2; material=glazing[random.randrange(len(glazing))]
            box('Front rear curtain wall pane',(x,face*4.82,z+1.56),(1.15,.09,2.84),material)
            box('Front rear spandrel',(x,face*4.89,z+.38),(1.15,.055,.5),glazing[0])
        for bay in range(8):
            y=-4.2+bay*1.2
            box('Side curtain wall pane',(face*6.02,y,z+1.56),(.09,1.15,2.84),glazing[random.randrange(len(glazing))])
            box('Side spandrel',(face*6.09,y,z+.38),(.055,1.15,.5),glazing[0])
# Fins span several floors; visible joints make their construction credible.
for side in [-1,1]:
    for bay in range(11):
        x=-6+bay*1.2
        for segment in range(4):
            box('Tall front facade fin',(x,side*5.16,14.07+segment*16.775),(.105,.72,16.71),bronze,.018)
    for bay in range(9):
        y=-4.8+bay*1.2
        for segment in range(4):
            box('Tall side facade fin',(side*6.35,y,14.07+segment*16.775),(.72,.105,16.71),bronze,.018)
box('Crown cap',(0,0,72.97),(12.65,10.25,.38),bronze,.04)
box('Roof slab',(0,0,73.12),(11.9,9.5,.2),concrete)
for x in [-5.9,5.9]: box('Roof side parapet',(x,0,73.63),(.16,9.55,.96),bronze)
for y in [-4.7,4.7]: box('Roof end parapet',(0,y,73.63),(11.9,.16,.96),bronze)
box('Screened mechanical penthouse',(0,1,74.05),(5.5,4.1,1.8),frame)
for i in range(10): box('Penthouse louver',(0,-1.08,73.25+i*.17),(5.6,.12,.065),bronze)
# Entrance canopy, door leaves and monumental lobby columns.
box('Entrance canopy',(0,-6.15,4.3),(7.1,3.2,.23),bronze,.045)
box('Canopy soffit',(0,-6.15,4.15),(6.8,3,.05),wood)
for x in [-3,3]: rod('Canopy slender column',(x,-7.35,.18),(x,-7.35,4.15),.075,bronze)
for x in [-.72,.72]:
    box('Entrance door',(x,-4.98,1.62),(1.38,.09,2.88),glazing[4])
    for dx in [-.68,.68]: box('Door stile',(x+dx,-5.05,1.62),(.055,.1,2.9),bronze)
    rod('Door pull',(x+(-.48 if x>0 else .48),-5.17,1.1),(x+(-.48 if x>0 else .48),-5.17,1.85),.023,bronze)
for x in [-4.8,4.8]: box('Lobby stone column',(x,-4.3,2.88),(.55,.55,5.4),concrete,.035)
# Landscape islands, slatted benches and human scale fixtures.
for x,y in [(-11,-6),(11,-5),(-11,4),(11,5)]:
    box('Raised planter',(x,y,.49),(3.3,3.3,.64),concrete,.12)
    box('Exposed planter soil',(x,y,.823),(2.97,2.97,.04),soil,.06)
    rod('Tree trunk',(x,y,.83),(x,y,4.8),.17,trunk)
    for j in range(5):
        a=j*math.tau/5; tip=(x+.9*math.cos(a),y+.9*math.sin(a),4.6+(j%2)*.5)
        rod('Tree branch',(x,y,3.1),tip,.065,trunk)
        bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=2,radius=1,location=tip); o=bpy.context.object; o.name='Sculpted tree canopy'; o.scale=(1.35,1.25,1.6); o.data.materials.append(foliage)
for x in [-9,9]:
    for y in [-10,0,9]:
        for dx in [-1,1]: box('Bench support',(x+dx,y,.45),(.16,.61,.52),black,.025)
        for j in range(5): box('Bench seat slat',(x,y-.3+j*.15,.74),(2.65,.115,.095),wood,.015)
for x in [-5,5]:
    for y in [-11,-8]:
        rod('Bollard',(x,y,.17),(x,y,.94),.09,black)
        rod('Bollard light collar',(x,y,.81),(x,y,.86),.095,paving)
for x,y in [(-14,-10),(14,-10),(-14,10),(14,10)]:
    rod('Plaza light mast',(x,y,.18),(x,y,5.8),.065,black)
    box('Plaza light head',(x,y,5.82),(.72,.32,.1),black,.04)
# A few abstract pedestrians establish the tower's scale.
for x,y in [(-2,-9),(3,-10),(8,-1),(-8,8)]:
    coat=mat('Pedestrian coat '+str(x),(.12+random.random()*.15,.13+random.random()*.12,.16+random.random()*.15))
    for dx in [-.12,.12]: rod('Pedestrian leg',(x+dx,y,.2),(x+dx,y,.94),.075,black)
    box('Pedestrian torso',(x,y,1.21),(.43,.25,.61),coat,.09)
    bpy.ops.mesh.primitive_uv_sphere_add(segments=16,ring_count=8,radius=.15,location=(x,y,1.68)); bpy.context.object.data.materials.append(concrete)
# Compressed perspective from a distant, elevated architectural viewpoint.
bpy.ops.object.camera_add(location=(125,-165,104)); cam=bpy.context.object; cam.name='Telephoto architectural camera'; cam.data.lens=100; cam.data.clip_end=1000; cam.rotation_euler=(Vector((0,0,35))-cam.location).to_track_quat('-Z','Y').to_euler(); bpy.context.scene.camera=cam
bpy.ops.object.light_add(type='SUN',location=(50,-70,100)); sun=bpy.context.object; sun.name='Afternoon sun'; sun.data.energy=3; sun.data.angle=math.radians(12); sun.rotation_euler=(math.radians(28),math.radians(-24),math.radians(-32))
area('Broad sky reflection',(-35,-25,70),10000,45,(0,0,35)); area('Warm facade rim',(20,30,90),7000,35,(0,0,40))
scene=bpy.context.scene; scene.world.color=(.36,.43,.52); scene.render.engine='CYCLES'; scene.cycles.samples=64; scene.render.resolution_x=1200; scene.render.resolution_y=1500; scene.render.resolution_percentage=100; scene.view_settings.view_transform='AgX'
