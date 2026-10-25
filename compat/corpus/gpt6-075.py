import bpy, math
from mathutils import Vector
bpy.ops.wm.read_factory_settings(use_empty=True)

def mat(name,color,metallic=0,roughness=0.5):
    m = bpy.data.materials.new(name)
    m.diffuse_color = (*color,1)
    m.use_nodes = True
    p = m.node_tree.nodes.get('Principled BSDF')
    p.inputs['Base Color'].default_value = (*color,1)
    p.inputs['Metallic'].default_value = metallic
    p.inputs['Roughness'].default_value = roughness
    return m

def box(name,loc,size,material,bevel=0.012):
    bpy.ops.mesh.primitive_cube_add(size=1,location=loc)
    o = bpy.context.object
    o.name = name
    o.dimensions = size
    bpy.ops.object.transform_apply(location=False,rotation=False,scale=True)
    o.data.materials.append(material)
    if bevel:
        b = o.modifiers.new('Sheet metal edge radius','BEVEL')
        b.width = bevel
        b.segments = 2
        o.modifiers.new('Weighted normals','WEIGHTED_NORMAL')
    return o

def cyl(name,loc,radius,depth,material,vertices=48,axis=(0,0,1)):
    bpy.ops.mesh.primitive_cylinder_add(vertices=vertices,radius=radius,depth=depth,location=loc)
    o = bpy.context.object
    o.name = name
    o.rotation_euler = Vector(axis).to_track_quat('Z','Y').to_euler()
    o.data.materials.append(material)
    b = o.modifiers.new('Machined edge','BEVEL')
    b.width = 0.003
    b.segments = 2
    o.modifiers.new('Weighted normals','WEIGHTED_NORMAL')
    return o

def tube(name,points,radius,material,cyclic=False):
    c = bpy.data.curves.new(name,'CURVE')
    c.dimensions = '3D'
    c.bevel_depth = radius
    c.bevel_resolution = 2
    s = c.splines.new('POLY')
    s.points.add(len(points)-1)
    for p,co in zip(s.points,points):
        p.co = (*co,1)
    s.use_cyclic_u = cyclic
    o = bpy.data.objects.new(name,c)
    bpy.context.collection.objects.link(o)
    c.materials.append(material)
    return o

def label(text,loc,size,material,rotation=(math.pi/2,0,0)):
    c = bpy.data.curves.new(text,'FONT')
    c.body = text
    c.size = size
    c.extrude = 0.0003
    c.align_x = 'CENTER'
    o = bpy.data.objects.new(text,c)
    bpy.context.collection.objects.link(o)
    o.location = loc
    o.rotation_euler = rotation
    c.materials.append(material)
    return o

body = mat('Warm gray powder coated casing',(0.56,0.59,0.56),0.45,0.43)
panel = mat('Access panel enamel',(0.66,0.68,0.64),0.35,0.46)
steel = mat('Galvanized ducts',(0.53,0.61,0.65),0.8,0.36)
dark = mat('Dark recess and gaskets',(0.018,0.027,0.029),0.12,0.78)
grille = mat('Graphite fan guards',(0.11,0.14,0.15),0.75,0.35)
blade = mat('Aluminum fan blades',(0.38,0.44,0.46),0.8,0.32)
bolt = mat('Zinc fasteners',(0.65,0.69,0.70),0.85,0.27)
yellow = mat('Warning label yellow',(0.93,0.65,0.06),roughness=0.56)
roof = mat('Charcoal roof membrane',(0.16,0.18,0.19),roughness=0.96)
curb = mat('Concrete parapet',(0.46,0.45,0.41),roughness=0.91)
# Low-amplitude procedural galvanized mottling.
n,l = steel.node_tree.nodes,steel.node_tree.links
noise = n.new('ShaderNodeTexNoise')
noise.inputs['Scale'].default_value = 95
noise.inputs['Detail'].default_value = 2
ramp = n.new('ShaderNodeValToRGB')
ramp.color_ramp.elements[0].color = (0.32,0.39,0.42,1)
ramp.color_ramp.elements[1].color = (0.65,0.71,0.73,1)
l.new(noise.outputs['Fac'],ramp.inputs[0])
l.new(ramp.outputs['Color'],n.get('Principled BSDF').inputs['Base Color'])
box('Rooftop slab',(0,0,-0.15),(12,10,0.28),curb,0.03)
box('Roof membrane',(0,0,0.001),(11.9,9.9,0.035),roof,0)
for x in range(-5,6,2):
    box('Roof membrane overlap',(x,0,0.022),(0.027,9.8,0.008),roof,0)
for y in (-4.9,4.9):
    box('Parapet wall',(0,y,0.24),(12,0.20,0.55),curb)
    box('Parapet metal coping',(0,y,0.53),(12.04,0.27,0.045),steel)
for x in (-5.9,5.9):
    box('Parapet wall',(x,0,0.24),(0.20,9.8,0.55),curb)
    box('Parapet metal coping',(x,0,0.53),(0.27,9.82,0.045),steel)

box('Raised equipment curb',(-0.6,0,0.24),(3.38,2.0,0.44),steel)
box('Curb weather flashing',(-0.6,0,0.085),(3.60,2.22,0.09),steel)
box('Black vibration isolation',(-0.6,0,0.47),(3.40,2.02,0.08),dark)
box('Packaged HVAC cabinet',(-0.6,0,1.16),(3.60,2.12,1.32),body,0.025)
box('Bottom cabinet rail',(-0.6,0,0.54),(3.68,2.20,0.10),grille)
# Three inset service bays on the camera-facing side.
for i,x in enumerate((-1.80,-0.62,0.56)):
    box('Service panel dark gasket',(x,-1.069,1.17),(1.12,0.018,1.13),dark,0.008)
    box('Removable service door',(x,-1.085,1.17),(1.085,0.023,1.095),panel,0.01)
    for dx in (-0.475,0.475):
        for z in (0.70,1.64):
            cyl('Service door captive screw',(x+dx,-1.103,z),0.012,0.008,bolt,12,(0,1,0))
    box('Recessed door latch',(x+0.36,-1.108,1.20),(0.063,0.015,0.14),dark,0.006)
    box('Latch pull',(x+0.36,-1.127,1.20),(0.021,0.025,0.082),bolt,0.005)
    if i == 0:
        box('Intake louver recess',(x,-1.108,1.19),(0.79,0.01,0.64),dark,0)
        for j in range(10):
            o = box('Angled weather louver',(x,-1.142,0.90+j*0.061),(0.80,0.075,0.033),body,0.004)
            o.rotation_euler.x = math.radians(-24)
box('Equipment identification plate',(-0.62,-1.111,1.48),(0.64,0.009,0.13),grille,0.005)
label('RTU - 075',(-0.62,-1.119,1.45),0.067,panel)
box('Electrical warning sticker',(0.36,-1.11,1.48),(0.22,0.007,0.15),yellow,0.002)
label('!',(0.36,-1.12,1.435),0.11,dark)

# A rectangular finned condenser coil on the left end.
box('Condenser coil recess',(-2.411,0,1.16),(0.018,1.84,0.99),dark,0)
for i in range(66):
    box('Condenser aluminum fin',(-2.428,-0.87+i*1.74/65,1.16),(0.025,0.010,0.91),blade,0)
for z in (0.72,1.16,1.60):
    box('Coil protective cross rail',(-2.449,0,z),(0.029,1.85,0.028),grille,0.004)

# Build real circular openings in the roof using an exact Boolean before fans.
lid = box('Overhanging top sheet',(-0.6,0,1.84),(3.70,2.22,0.07),body,0)
fan_centers = (-1.48,0.27)
for x in fan_centers:
    bpy.ops.mesh.primitive_cylinder_add(vertices=64,radius=0.65,depth=0.30,location=(x,0,1.84))
    cutter = bpy.context.object
    mod = lid.modifiers.new('Fan aperture','BOOLEAN')
    mod.operation = 'DIFFERENCE'
    mod.solver = 'EXACT'
    mod.object = cutter
    bpy.context.view_layer.objects.active = lid
    lid.select_set(True)
    cutter.select_set(False)
    bpy.ops.object.modifier_apply(modifier=mod.name)
    bpy.data.objects.remove(cutter,do_unlink=True)
for x in fan_centers:
    cyl('Dark fan well',(x,0,1.813),0.645,0.013,dark)
    # Ring shroud is an annular mesh, leaving the fan visible.
    verts,faces = [],[]
    for z,r in ((1.84,0.65),(1.97,0.65),(1.97,0.69),(1.84,0.69)):
        verts.extend([(x+r*math.cos(i*math.tau/64),r*math.sin(i*math.tau/64),z) for i in range(64)])
    for j in range(4):
        for i in range(64):
            faces.append((j*64+i,j*64+(i+1)%64,((j+1)%4)*64+(i+1)%64,((j+1)%4)*64+i))
    mesh = bpy.data.meshes.new('Annular fan shroud')
    mesh.from_pydata(verts,[],faces)
    mesh.update()
    o = bpy.data.objects.new('Raised circular fan shroud',mesh)
    bpy.context.collection.objects.link(o)
    o.data.materials.append(grille)
    for f in mesh.polygons:
        f.use_smooth = True
    cyl('Fan motor hub',(x,0,1.89),0.13,0.10,blade)
    for k in range(7):
        a = k*math.tau/7
        points = [(0.11,-0.035,1.867),(0.49,-0.13,1.84),(0.59,-0.005,1.867),(0.48,0.17,1.92),(0.16,0.08,1.91)]
        v = [(x+px*math.cos(a)-py*math.sin(a),px*math.sin(a)+py*math.cos(a),pz) for px,py,pz in points]
        mesh = bpy.data.meshes.new('Swept fan blade')
        mesh.from_pydata(v,[],[(0,1,2,3,4)])
        mesh.update()
        o = bpy.data.objects.new('Seven-blade axial fan',mesh)
        bpy.context.collection.objects.link(o)
        o.data.materials.append(blade)
        s = o.modifiers.new('Blade gauge','SOLIDIFY')
        s.thickness = 0.006
    for j in range(1,11):
        r = 0.062*j
        tube('Concentric fan guard ring',[(x+r*math.cos(i*math.tau/80),r*math.sin(i*math.tau/80),1.985+0.025*(1-r/0.69)) for i in range(80)],0.005,grille,True)
    for k in range(12):
        a = k*math.tau/12
        tube('Radial grille spoke',[(x,0,2.014),(x+0.69*math.cos(a),0.69*math.sin(a),1.985)],0.006,grille)
    for k in range(4):
        a = math.pi/4+k*math.pi/2
        cyl('Fan guard fixing screw',(x+0.671*math.cos(a),0.671*math.sin(a),1.979),0.013,0.014,bolt,12)

# Two galvanized rectangular ducts leave the right end and turn into the roof.
def duct(y,width,index):
    box('Duct connection gasket',(1.222,y,1.16),(0.09,width+0.12,0.84),dark)
    box('Horizontal galvanized duct',(2.18,y,1.16),(1.91,width,0.70),steel)
    box('Downturned duct riser',(3.02,y,0.79),(0.72,width,1.42),steel)
    box('Riser roof boot',(3.02,y,0.10),(0.94,width+0.23,0.14),steel)
    for x in (1.30,2.05,2.80):
        for z in (0.805,1.515):
            box('Duct flange horizontal',(x,y,z),(0.042,width+0.075,0.035),steel,0.003)
        for yy in (y-width/2-0.018,y+width/2+0.018):
            box('Duct flange vertical',(x,yy,1.16),(0.042,0.035,0.74),steel,0.003)
    for z in (0.38,0.85):
        for yy in (y-width/2-0.014,y+width/2+0.014):
            box('Riser standing seam',(3.02,yy,z),(0.77,0.028,0.027),steel,0.002)
    # Shallow diagonal embossing across the top sheet.
    tube('Duct stiffening cross',[(1.38,y-width*0.43,1.513),(2.30,y+width*0.43,1.513)],0.003,bolt)
    tube('Duct stiffening cross',[(1.38,y+width*0.43,1.513),(2.30,y-width*0.43,1.513)],0.003,bolt)
    for xx in (2.02,3.03):
        box('Duct support sleeper',(xx,y,0.10),(0.20,width+0.24,0.15),curb)
        for yy in (y-width/2-0.07,y+width/2+0.07):
            box('Duct support upright',(xx,yy,0.46),(0.045,0.045,0.68),grille,0.004)
duct(-0.52,0.70,0)
duct(0.53,0.67,1)
box('Electrical disconnect enclosure',(0.75,-1.20,0.83),(0.30,0.17,0.39),body,0.018)
box('Disconnect switch handle',(0.82,-1.303,0.86),(0.045,0.045,0.16),dark,0.008)
tube('Electrical conduit',[(0.75,-1.20,0.63),(0.75,-1.20,0.33),(0.80,-1.25,0.19),(1.50,-1.25,0.19),(1.50,-1.25,0.06)],0.018,steel)
tube('Condensate drain',[(-1.85,-1.1,0.65),(-1.85,-1.31,0.65),(-1.85,-1.31,0.29),(-1.65,-1.31,0.29),(-1.65,-1.31,0.44),(-1.40,-1.31,0.44),(-1.40,-1.31,0.09)],0.018,panel)

world = bpy.data.worlds.new('Rooftop daylight')
world.use_nodes = True
world.node_tree.nodes['Background'].inputs[0].default_value = (0.68,0.78,0.92,1)
world.node_tree.nodes['Background'].inputs[1].default_value = 0.5
bpy.context.scene.world = world
bpy.ops.object.light_add(type='SUN',location=(0,0,10))
bpy.context.object.rotation_euler = (0.4,-0.55,-0.3)
bpy.context.object.data.energy = 2.0
bpy.context.object.data.angle = 0.15
bpy.ops.object.light_add(type='AREA',location=(1,-5,8))
bpy.context.object.data.energy = 1500
bpy.context.object.data.size = 6
bpy.ops.object.camera_add(location=(8,-10,8))
cam = bpy.context.object
cam.rotation_euler = (Vector((0.4,0,0.9))-cam.location).to_track_quat('-Z','Y').to_euler()
cam.data.type = 'ORTHO'
cam.data.ortho_scale = 8.4
scene = bpy.context.scene
scene.camera = cam
scene.render.engine = 'CYCLES'
scene.render.resolution_x = 1500
scene.render.resolution_y = 1150
scene.render.resolution_percentage = 100
scene.view_settings.view_transform = 'AgX'
