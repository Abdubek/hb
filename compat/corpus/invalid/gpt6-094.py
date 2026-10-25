import bpy, math
from mathutils import Vector

bpy.ops.wm.read_factory_settings(use_empty=True)

def material(name, color, metallic=0, roughness=0.45, emission=0):
    m = bpy.data.materials.new(name)
    m.diffuse_color = (*color, 1)
    m.use_nodes = True
    p = m.node_tree.nodes.get('Principled BSDF')
    p.inputs['Base Color'].default_value = (*color, 1)
    p.inputs['Metallic'].default_value = metallic
    p.inputs['Roughness'].default_value = roughness
    if emission:
        p.inputs['Emission Color'].default_value = (*color, 1)
        p.inputs['Emission Strength'].default_value = emission
    return m

def box(name, loc, dims, mat, bevel=0.01):
    bpy.ops.mesh.primitive_cube_add(size=1, location=loc)
    o = bpy.context.object
    o.name = name
    o.dimensions = dims
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    o.data.materials.append(mat)
    if bevel:
        b = o.modifiers.new('Machined edges', 'BEVEL')
        b.width = bevel
        b.segments = 3
        o.modifiers.new('Weighted normals', 'WEIGHTED_NORMAL')
    return o

def rod(name, a, b, radius, mat, vertices=32):
    a, b = Vector(a), Vector(b)
    bpy.ops.mesh.primitive_cylinder_add(vertices=vertices, radius=radius, depth=(b-a).length, location=(a+b)/2)
    o = bpy.context.object
    o.name = name
    o.rotation_euler = (b-a).to_track_quat('Z', 'Y').to_euler()
    o.data.materials.append(mat)
    bevel = o.modifiers.new('Rim bevel', 'BEVEL')
    bevel.width = min(radius*0.15, 0.006)
    bevel.segments = 2
    o.modifiers.new('Weighted normals', 'WEIGHTED_NORMAL')
    return o

def disk(name, x, y, z, radius, depth, mat):
    return rod(name, (x,y-depth/2,z), (x,y+depth/2,z), radius, mat, 64)

def text(body, x, y, z, size, mat):
    bpy.ops.object.text_add(location=(x,y,z), rotation=(math.pi/2,0,0))
    o = bpy.context.object
    o.name = 'Legend ' + body
    o.data.body = body
    o.data.align_x = 'CENTER'
    o.data.align_y = 'CENTER'
    o.data.size = size
    o.data.extrude = 0.0003
    o.data.materials.append(mat)
    return o

paint = material('Blue gray enamel', (0.12,0.21,0.26), 0.45, 0.34)
edge = material('Housing dark metal', (0.055,0.075,0.084), 0.6, 0.4)
chrome = material('Brushed steel', (0.52,0.58,0.60), 0.85, 0.25)
black = material('Black polymer', (0.012,0.017,0.019), roughness=0.38)
ivory = material('Gauge dial ivory', (0.85,0.86,0.76), roughness=0.65)
red = material('Safety red', (0.66,0.018,0.009), roughness=0.35)
yellow = material('Safety yellow', (0.94,0.58,0.012), roughness=0.4)
green = material('Green pilot lamp', (0.025,0.8,0.16), roughness=0.25, emission=2)
amber = material('Amber pilot lamp', (1,0.28,0.01), roughness=0.25, emission=1.3)
wall = material('Concrete wall', (0.37,0.39,0.38), roughness=0.95)
box('Wall', (0,0.23,1.8), (5,0.22,3.6), wall, 0.02)
box('Control cabinet', (0,-0.05,1.72), (1.66,0.36,1.88), edge, 0.045)
box('Door gasket', (0,-0.242,1.72), (1.58,0.025,1.80), black, 0.025)
box('Front panel', (0,-0.267,1.72), (1.54,0.035,1.76), paint, 0.023)
for x in [-0.70,0.70]:
    for z in [0.91,2.53]:
        disk('Panel screw', x,-0.293,z,0.023,0.012,chrome)
        box('Screw slot', (x,-0.300,z), (0.027,0.002,0.004), black, 0.001)
for z in [1.14,2.29]:
    box('Cabinet hinge', (-0.80,-0.18,z), (0.055,0.11,0.18), chrome, 0.014)
text('PROCESS CONTROL',0,-0.294,2.43,0.082,ivory)
text('UNIT 04  /  AUXILIARY SYSTEM',0,-0.295,2.32,0.028,ivory)

for gx, title, unit, value in [(-0.39,'PRESSURE','bar',0.62),(0.39,'TEMPERATURE','C',0.43)]:
    gz = 2.02
    disk('Gauge body',gx,-0.32,gz,0.269,0.08,black)
    disk('Gauge polished bezel',gx,-0.37,gz,0.248,0.025,chrome)
    disk('Inset gauge face',gx,-0.386,gz,0.224,0.007,ivory)
    for i in range(41):
        a = math.radians(225-i*6.75)
        outer = 0.204
        inner = 0.175 if i%5==0 else 0.188
        rod('Dial graduation', (gx+inner*math.cos(a),-0.394,gz+inner*math.sin(a)), (gx+outer*math.cos(a),-0.394,gz+outer*math.sin(a)), 0.0025 if i%5==0 else 0.0013, black, 8)
        if i%10==0:
            text(str(i//4),gx+0.145*math.cos(a),-0.397,gz+0.145*math.sin(a),0.026,black)
    a = math.radians(225-value*270)
    rod('Red gauge needle', (gx-0.03*math.cos(a),-0.407,gz-0.03*math.sin(a)), (gx+0.177*math.cos(a),-0.407,gz+0.177*math.sin(a)), 0.0045, red, 12)
    disk('Needle hub',gx,-0.41,gz,0.019,0.011,black)
    text(unit,gx,-0.398,gz-0.07,0.032,black)
    text(title,gx,-0.297,1.69,0.043,ivory)

for i, x in enumerate([-0.49,-0.17,0.17]):
    disk('Toggle mounting washer',x,-0.311,1.42,0.059,0.025,chrome)
    disk('Toggle pivot',x,-0.334,1.42,0.032,0.034,black)
    dz = 0.074 if i != 1 else -0.074
    start, end = (x,-0.35,1.42),(x,-0.455,1.42+dz)
    rod('Toggle lever',start,end,0.012,chrome)
    bpy.ops.mesh.primitive_uv_sphere_add(segments=20,ring_count=12,radius=0.024,location=end)
    bpy.context.object.name = 'Toggle grip'
    bpy.context.object.data.materials.append(black)
    text(['POWER','PUMP','FAN'][i],x,-0.295,1.25,0.035,ivory)
    text('ON',x,-0.295,1.56,0.022,ivory)
    text('OFF',x,-0.295,1.32,0.020,ivory)
for x, mat, title in [(-0.48,green,'RUN'),(-0.17,amber,'READY')]:
    disk('Pilot bezel',x,-0.31,1.07,0.053,0.028,chrome)
    disk('Pilot lens',x,-0.335,1.07,0.038,0.033,mat)
    text(title,x,-0.295,0.965,0.027,ivory)
disk('Emergency stop backing',0.49,-0.313,1.34,0.144,0.029,yellow)
disk('Stop button neck',0.49,-0.36,1.34,0.068,0.075,black)
disk('Mushroom emergency stop',0.49,-0.42,1.34,0.105,0.075,red)
text('STOP',0.49,-0.462,1.34,0.032,ivory)
text('EMERGENCY',0.49,-0.295,1.12,0.031,ivory)
for i in range(5):
    box('Vent slot', (0.21+i*0.087,-0.289,0.98), (0.045,0.01,0.055), black, 0.008)
for x in [-0.50,0.50]:
    rod('Cable gland',(x,-0.035,0.74),(x,-0.035,0.82),0.064,black)
    rod('Conduit',(x,-0.035,0.12),(x,-0.035,0.75),0.032,chrome)
    for z in [0.25,0.58]:
        box('Conduit wall clamp',(x,0.028,z),(0.12,0.13,0.035),edge,0.008)

scene = bpy.context.scene
scene.world.color = (0.2,0.2,0.2)
for loc, energy, size in [((-2,-4,5),800,4),((3,-2,3),450,3)]:
    bpy.ops.object.light_add(type='AREA',location=loc)
    o = bpy.context.object
    o.data.energy = energy
    o.data.size = size
    o.rotation_euler = (Vector((0,-0.2,1.6))-o.location).to_track_quat('-Z','Y').to_euler()
bpy.ops.object.camera_add(location=(2.4,-6,3.0))
camera = bpy.context.object
camera.rotation_euler = (Vector((0,-0.1,1.45))-camera.location).to_track_quat('-Z','Y').to_euler()
camera.data.type = 'ORTHO'
camera.data.ortho_scale = 3.3
scene.camera = camera
scene.render.engine = 'CYCLES'
scene.render.resolution_x = 1100
scene.render.resolution_y = 1400
scene.render.resolution_percentage = 100
