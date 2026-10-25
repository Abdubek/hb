import bpy, math
from mathutils import Vector

bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)
for d in list(bpy.data.materials): bpy.data.materials.remove(d)

def mat(name, color, rough=.5, metal=0):
    m=bpy.data.materials.new(name); m.diffuse_color=(*color,1); m.use_nodes=True
    p=m.node_tree.nodes.get('Principled BSDF'); p.inputs['Base Color'].default_value=(*color,1); p.inputs['Roughness'].default_value=rough; p.inputs['Metallic'].default_value=metal
    return m

def box(name, loc, size, material, bevel=.025):
    bpy.ops.mesh.primitive_cube_add(size=1, location=loc); o=bpy.context.object; o.name=name; o.dimensions=size
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    if material: o.data.materials.append(material)
    if bevel:
        b=o.modifiers.new('Soft edges','BEVEL'); b.width=bevel; b.segments=3
        o.modifiers.new('Weighted normals','WEIGHTED_NORMAL')
    return o

def cyl(name, loc, radius, depth, material, vertices=40):
    bpy.ops.mesh.primitive_cylinder_add(vertices=vertices, radius=radius, depth=depth, location=loc); o=bpy.context.object; o.name=name; o.data.materials.append(material)
    b=o.modifiers.new('Edge rounding','BEVEL'); b.width=.012; b.segments=3
    o.modifiers.new('Weighted normals','WEIGHTED_NORMAL'); return o

def sphere(name, loc, scale, material):
    bpy.ops.mesh.primitive_uv_sphere_add(segments=24, ring_count=12, location=loc); o=bpy.context.object; o.name=name; o.scale=scale; o.data.materials.append(material)
    for p in o.data.polygons: p.use_smooth=True
    return o

def rod(name, a, b, radius, material):
    a,b=Vector(a),Vector(b); o=cyl(name,(a+b)/2,radius,(b-a).length,material,20); o.rotation_euler=(b-a).to_track_quat('Z','Y').to_euler(); return o

def light(name, loc, energy, size, target):
    bpy.ops.object.light_add(type='AREA',location=loc); o=bpy.context.object; o.name=name; o.data.energy=energy; o.data.shape='DISK'; o.data.size=size; o.rotation_euler=(Vector(target)-o.location).to_track_quat('-Z','Y').to_euler()

wall=mat('Warm plaster',(.79,.76,.67)); oak=mat('Honey oak',(.49,.28,.12)); seam=mat('Floor joints',(.18,.12,.075)); white=mat('Ivory enamel',(.86,.87,.79)); green=mat('Sage cabinets',(.26,.39,.31)); stone=mat('Pale worktop',(.72,.74,.68)); dark=mat('Graphite',(.035,.045,.045)); steel=mat('Brushed steel',(.38,.43,.44),.26,.8); blue=mat('Indigo linen',(.15,.25,.36)); linen=mat('Cream bedding',(.9,.83,.67)); clay=mat('Terracotta',(.56,.22,.12)); leaf=mat('Leaves',(.15,.3,.12)); rug=mat('Woven oatmeal',(.63,.52,.37)); art=mat('Ochre print',(.8,.43,.12)); glass=mat('Pale blue window',(.48,.68,.73),.22)
box('Raised cutaway foundation',(0,0,-.18),(7.4,6.1,.36),white)
box('Dark floor underlay',(0,0,.015),(7.1,5.8,.05),seam,0)
for row in range(15):
    y=-2.71+row*.387
    for col in range(5):
        x=-3.54+col*1.42
        box('Individual oak floorboard',(x+.704,y,.062),(1.398,.376,.055),oak,.006)
box('Rear wall',(0,2.95,1.6),(7.4,.16,3.2),wall)
# Left wall is built around a real window opening.
box('Left wall lower',(-3.62,0,.55),(.16,5.8,1.1),wall)
box('Left wall upper',(-3.62,0,2.91),(.16,5.8,.58),wall)
box('Left wall front pier',(-3.62,-2.43,1.86),(.16,.94,1.52),wall)
box('Left wall rear pier',(-3.62,1.53,1.86),(.16,2.74,1.52),wall)
box('Window pane',(-3.625,-.94,1.86),(.045,2.04,1.5),glass,.005)
for y in [-1.97,.09,-.94]: box('Window mullion',(-3.52,y,1.86),(.14,.065,1.6),white,.008)
for z in [1.08,2.64]: box('Window frame',(-3.52,-.94,z),(.18,2.2,.09),white,.008)
box('Window sill',(-3.4,-.94,1.07),(.43,2.25,.09),oak)
box('Rear skirting',(0,2.83,.18),(7.15,.06,.22),white,.01)
box('Left skirting',(-3.49,0,.18),(.06,5.8,.22),white,.01)
# Kitchen run, with articulated doors and a contrasting backsplash.
box('Kitchen toe kick',(-1.57,2.3,.18),(3.6,.85,.2),dark)
for i in range(4):
    x=-2.92+i*.9
    box('Base cabinet',(x,2.3,.58),(.88,.91,.78),green)
    box('Cabinet door',(x,1.828,.59),(.83,.035,.71),green,.015)
    box('Brass pull',(x,1.79,.85),(.28,.035,.027),steel,.008)
box('Continuous worktop',(-1.57,2.28,1.015),(3.7,1.03,.095),stone)
box('Tiled backsplash',(-1.57,2.845,1.35),(3.72,.045,.58),white,.005)
for x in [-3.2+i*.3 for i in range(12)]: box('Tile grout',(x,2.816,1.35),(.012,.007,.55),stone,0)
box('Horizontal tile grout',(-1.57,2.812,1.35),(3.7,.008,.012),stone,0)
box('Sink steel rim',(-2.65,2.22,1.071),(.72,.62,.035),steel,.09)
box('Sink dark basin',(-2.65,2.22,1.092),(.59,.49,.02),dark,.085)
rod('Faucet upright',(-2.65,2.62,1.05),(-2.65,2.62,1.43),.027,steel)
rod('Faucet spout',(-2.65,2.62,1.43),(-2.65,2.33,1.43),.027,steel)
rod('Faucet nozzle',(-2.65,2.33,1.43),(-2.65,2.33,1.35),.027,steel)
box('Black induction hob',(-.83,2.24,1.074),(1.04,.69,.025),dark,.04)
for x in [-1.08,-.58]:
    for y in [2.05,2.43]:
        cyl('Burner steel circle',(x,y,1.094),.153,.009,steel)
        cyl('Burner dark center',(x,y,1.1),.135,.009,dark)
for x in [-2.85,-1.88]:
    box('Wall cabinet',(x,2.62,2.29),(.92,.48,.8),green)
    box('Upper door',(x,2.365,2.29),(.86,.035,.74),green)
    box('Upper handle',(x+.28,2.332,2.13),(.025,.025,.2),steel,.006)
box('Extractor hood',(-.83,2.56,1.99),(1.12,.66,.14),steel)
box('Extractor chimney',(-.83,2.73,2.5),(.46,.31,.95),white)
box('Compact refrigerator',(.74,2.35,.97),(.82,.97,1.76),white,.055)
box('Freezer separation',(.74,1.85,1.41),(.74,.018,.018),stone,.003)
box('Fridge handle',(1.02,1.81,1.01),(.04,.05,.46),steel)
box('Cutting board',(-1.82,2.13,1.09),(.46,.35,.04),oak)
# Sleeping area.
box('Bed platform',(2.36,1.09,.3),(1.94,2.92,.4),oak,.055)
box('Upholstered headboard',(2.36,2.6,.91),(2.02,.15,1.32),blue,.075)
box('Mattress',(2.36,1.08,.61),(1.8,2.76,.3),linen,.13)
box('Duvet',(2.36,.64,.83),(1.84,1.9,.2),blue,.12)
box('Folded bed runner',(2.36,-.04,.945),(1.88,.45,.045),linen,.035)
for x in [1.91,2.81]: box('Pillow',(x,2.08,.86),(.73,.53,.2),linen,.12)
box('Bedside table',(1.09,1.96,.45),(.47,.61,.71),oak)
cyl('Bedside lamp base',(1.09,1.96,.85),.13,.05,steel)
rod('Bedside lamp stem',(1.09,1.96,.85),(1.09,1.96,1.12),.025,steel)
bpy.ops.mesh.primitive_cone_add(vertices=40,radius1=.2,radius2=.12,depth=.24,location=(1.09,1.96,1.19)); bpy.context.object.data.materials.append(linen)
# Living and dining furniture leaves a readable central circulation route.
box('Area rug',(-.55,-1.4,.105),(3.95,2.18,.035),rug,.07)
box('Sofa base',(-2.75,-.72,.44),(.98,2.05,.46),linen,.11)
box('Sofa back',(-3.13,-.72,.85),(.26,2.1,.97),linen,.11)
for y in [-1.37,-.69,-.01]: box('Seat cushion',(-2.66,y,.72),(.71,.62,.19),linen,.08)
for y in [-1.79,.35]: box('Sofa arm',(-2.75,y,.75),(1.02,.19,.57),linen,.07)
box('Sofa accent pillow',(-2.89,-1.13,1.03),(.23,.46,.46),blue,.09)
cyl('Round coffee table',(-1.08,-.95,.63),.58,.08,oak)
for a in [0,2.094,4.189]: rod('Coffee table leg',(-1.08+.4*math.cos(a),-.95+.4*math.sin(a),.13),(-1.08+.3*math.cos(a),-.95+.3*math.sin(a),.6),.04,dark)
box('Coffee table book',(-1.07,-.96,.695),(.34,.25,.045),blue,.008)
cyl('Ceramic cup',(-.81,-.75,.75),.063,.13,white)
cyl('Coffee surface',(-.81,-.75,.819),.052,.006,dark)
box('Dining table',(.66,-1.83,.85),(1.15,.86,.09),oak,.07)
for x in [.21,1.11]:
    for y in [-2.15,-1.51]: rod('Dining table leg',(x,y,.12),(x,y,.81),.035,dark)
for x in [-.17,1.49]:
    box('Dining chair seat',(x,-1.83,.52),(.5,.56,.09),green,.07)
    box('Dining chair back',(x+(-.2 if x<0 else .2),-1.83,.89),(.075,.54,.55),green,.05)
    for dx in [-.18,.18]:
        for dy in [-.2,.2]: rod('Chair leg',(x+dx,-1.83+dy,.12),(x+dx,-1.83+dy,.49),.025,oak)
# Simple wall art and a houseplant.
box('Art frame',(2.32,2.833,2.26),(1.2,.06,.85),oak)
box('Art paper',(2.32,2.793,2.26),(1.08,.012,.73),linen,.002)
box('Abstract color block',(2.14,2.783,2.21),(.38,.01,.5),art,.005)
box('Abstract blue block',(2.54,2.779,2.38),(.32,.012,.24),blue,.005)
cyl('Plant pot',(2.91,-2.13,.34),.24,.46,clay)
cyl('Pot soil',(2.91,-2.13,.575),.216,.018,seam)
for i in range(8):
    a=i*2.4; end=Vector((2.91+.3*math.cos(a),-2.13+.3*math.sin(a),.92+(i%3)*.17))
    rod('Plant stem',(2.91,-2.13,.57),end,.012,leaf)
    o=sphere('Plant leaf',end,(.105,.06,.27),leaf); o.rotation_euler=(Vector((math.cos(a),math.sin(a),.7))).to_track_quat('Z','Y').to_euler()
box('Backdrop',(0,0,-.43),(200,200,.12),mat('Backdrop',(.72,.76,.75)),0)
light('Large warm key',(1,-5,10),1400,7,(0,0,0)); light('Window fill',(-5,-2,6),800,5,(0,0,1)); light('Rear rim',(3,5,7),1000,4,(0,0,1))
bpy.ops.object.camera_add(location=(10,-13,11)); cam=bpy.context.object; cam.name='Isometric apartment camera'; cam.rotation_euler=(Vector((0,0,1))-cam.location).to_track_quat('-Z','Y').to_euler(); cam.data.type='ORTHO'; cam.data.ortho_scale=11.8; bpy.context.scene.camera=cam
scene=bpy.context.scene; scene.render.engine='CYCLES'; scene.cycles.samples=64; scene.world.color=(.3,.3,.3); scene.render.resolution_x=1400; scene.render.resolution_y=1200; scene.render.resolution_percentage=100; scene.view_settings.view_transform='AgX'
