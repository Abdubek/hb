import bpy, math
from mathutils import Vector

# Freestanding kitchen range, dimensions in metres.
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)

def mat(name, color, metallic=0.0, roughness=0.4):
    m = bpy.data.materials.new(name)
    m.diffuse_color = (*color, 1)
    m.use_nodes = True
    p = m.node_tree.nodes.get('Principled BSDF')
    p.inputs['Base Color'].default_value = (*color, 1)
    p.inputs['Metallic'].default_value = metallic
    p.inputs['Roughness'].default_value = roughness
    return m

def cube(name, loc, scale, material, bevel=0.0):
    bpy.ops.mesh.primitive_cube_add(size=1, location=loc)
    o = bpy.context.object
    o.name = name
    o.dimensions = scale
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    o.data.materials.append(material)
    if bevel:
        b = o.modifiers.new('Soft manufactured edges', 'BEVEL')
        b.width = bevel
        b.segments = 3
        o.modifiers.new('Weighted corner normals', 'WEIGHTED_NORMAL')
    return o

def cyl(name, loc, radius, depth, material, direction=(0,0,1)):
    bpy.ops.mesh.primitive_cylinder_add(vertices=48, radius=radius, depth=depth, location=loc)
    o = bpy.context.object
    o.name = name
    o.rotation_euler = Vector(direction).to_track_quat('Z','Y').to_euler()
    o.data.materials.append(material)
    b = o.modifiers.new('Edge rounding', 'BEVEL')
    b.width = min(0.009, depth * 0.15)
    b.segments = 3
    o.modifiers.new('Weighted normals', 'WEIGHTED_NORMAL')
    for p in o.data.polygons:
        p.use_smooth = True
    return o

def ring(name, loc, major, minor, material, rotation=(0,0,0)):
    bpy.ops.mesh.primitive_torus_add(major_segments=64, minor_segments=12, location=loc, major_radius=major, minor_radius=minor, rotation=rotation)
    o = bpy.context.object
    o.name = name
    o.data.materials.append(material)
    for p in o.data.polygons:
        p.use_smooth = True
    return o

def text(name, body, loc, size, material):
    bpy.ops.object.text_add(location=loc, rotation=(math.pi/2,0,0))
    o = bpy.context.object
    o.name = name
    o.data.body = body
    o.data.size = size
    o.data.align_x = 'CENTER'
    o.data.extrude = 0.0003
    o.data.materials.append(material)
    return o

steel = mat('Brushed stainless steel', (0.48,0.53,0.57), 0.82, 0.28)
enamel = mat('Warm white enamel', (0.86,0.85,0.80), 0.2, 0.25)
black = mat('Black cast iron', (0.018,0.022,0.025), 0.45, 0.6)
glass = mat('Smoked oven glass', (0.023,0.042,0.055), 0.5, 0.16)
chrome = mat('Polished trim', (0.7,0.74,0.77), 0.95, 0.18)
white = mat('Printed markings', (0.94,0.96,0.92), 0.0, 0.4)
led = mat('Mint display', (0.15,0.9,0.62), 0, 0.3)
p = led.node_tree.nodes.get('Principled BSDF')
p.inputs['Emission Color'].default_value = (0.12,0.85,0.55,1)
p.inputs['Emission Strength'].default_value = 1.5
floor = mat('Kitchen floor', (0.22,0.25,0.27), 0, 0.75)

for x in (-0.46,0.46):
    for y in (-0.35,0.35):
        cyl('Adjustable foot', (x,y,0.085), 0.055, 0.15, black)
cube('Range cabinet', (0,0,0.69), (1.12,0.92,1.18), enamel, 0.045)
cube('Recessed toe kick', (0,-0.462,0.17), (1.00,0.035,0.14), black, 0.01)
cube('Lower drawer', (0,-0.482,0.31), (1.04,0.045,0.16), steel, 0.018)
cube('Drawer finger recess', (0,-0.509,0.36), (0.5,0.008,0.018), black, 0.004)
cube('Oven door gasket', (0,-0.478,0.71), (1.025,0.042,0.62), black, 0.025)
cube('Oven door stainless surround', (0,-0.512,0.71), (0.985,0.075,0.59), steel, 0.035)
cube('Glass window rim', (0,-0.555,0.69), (0.825,0.02,0.425), black, 0.035)
cube('Smoked glass window', (0,-0.568,0.69), (0.76,0.012,0.36), glass, 0.028)
for x in (-0.4,0.4):
    cyl('Handle standoff', (x,-0.596,0.973), 0.026, 0.10, chrome, (0,1,0))
cyl('Oven handle', (0,-0.657,0.973), 0.032, 0.86, steel, (1,0,0))
cube('Control fascia', (0,-0.477,1.15), (1.1,0.09,0.20), steel, 0.015)
for i,x in enumerate((-0.43,-0.255,0.255,0.43)):
    cyl('Knob bezel %d'%i, (x,-0.535,1.16), 0.063, 0.015, chrome, (0,-1,0))
    cyl('Control knob %d'%i, (x,-0.57,1.16), 0.049, 0.066, black, (0,-1,0))
    cube('Knob index', (x,-0.605,1.19), (0.007,0.004,0.022), white, 0.002)
    for a in (-55,0,55):
        ang = math.radians(a)
        cyl('Control scale dot', (x+0.073*math.sin(ang),-0.526,1.16+0.073*math.cos(ang)), 0.003, 0.003, black, (0,1,0))
cube('Clock recess', (0,-0.527,1.17), (0.24,0.014,0.09), black, 0.009)
text('Digital time', '12:45', (0,-0.537,1.148), 0.05, led)
text('Range brand', 'N O R D', (0,-0.554,0.428), 0.021, black)
cube('Stainless cooktop lip', (0,0,1.3), (1.17,0.97,0.055), steel, 0.025)
cube('Black enamel hob', (0,-0.015,1.333), (1.10,0.88,0.025), black, 0.02)
for i,(x,y,r) in enumerate(((-0.285,-0.24,0.105),(0.285,-0.24,0.12),(-0.285,0.235,0.09),(0.285,0.235,0.105))):
    cyl('Burner drip bowl %d'%i, (x,y,1.352), r+0.055, 0.018, steel)
    ring('Burner crown', (x,y,1.377), r*0.8, 0.018, chrome)
    cyl('Burner cap', (x,y,1.395), r, 0.028, black)
    for j in range(20):
        a = j*math.tau/20
        cube('Burner gas port', (x+r*0.86*math.cos(a),y+r*0.86*math.sin(a),1.374), (0.012,0.012,0.014), black, 0.002)
    for s in (-1,1):
        cube('Grate side', (x+s*0.215,y,1.405), (0.025,0.40,0.048), black, 0.008)
        cube('Grate cross rail', (x,y+s*0.20,1.405), (0.45,0.025,0.048), black, 0.008)
        cube('Pot support horizontal', (x+s*0.143,y,1.432), (0.145,0.028,0.04), black, 0.008)
        cube('Pot support vertical', (x,y+s*0.135,1.432), (0.028,0.135,0.04), black, 0.008)
cube('Rear splash guard', (0,0.441,1.415), (1.15,0.055,0.20), steel, 0.018)
for x in [i*0.045 for i in range(-10,11)]:
    cube('Rear ventilation slot', (x,0.409,1.43), (0.022,0.006,0.066), black, 0.006)
cube('Floor', (0,0,-0.035), (200,200,0.06), floor)

world = bpy.context.scene.world
world.use_nodes = True
world.node_tree.nodes['Background'].inputs[0].default_value = (0.18,0.21,0.25,1)
world.node_tree.nodes['Background'].inputs[1].default_value = 0.45
for name,loc,power,size in [('Key',(3,-4,6),850,4),('Fill',(-4,-2,3),550,3),('Rim',(1,4,5),1000,3)]:
    bpy.ops.object.light_add(type='AREA', location=loc)
    o=bpy.context.object; o.name=name; o.data.energy=power; o.data.shape='DISK'; o.data.size=size
    o.rotation_euler=(Vector((0,0,0.8))-o.location).to_track_quat('-Z','Y').to_euler()
bpy.ops.object.camera_add(location=(2.5,-3.8,2.8))
cam=bpy.context.object
cam.rotation_euler=(Vector((0,0,0.78))-cam.location).to_track_quat('-Z','Y').to_euler()
cam.data.type='ORTHO'; cam.data.ortho_scale=2.6
scene=bpy.context.scene; scene.camera=cam
scene.render.engine='CYCLES'; scene.cycles.samples=64
scene.render.resolution_x=1100; scene.render.resolution_y=1100; scene.render.resolution_percentage=100
