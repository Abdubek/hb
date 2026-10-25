import bpy, math
from mathutils import Vector
bpy.ops.wm.read_factory_settings(use_empty=True)

def material(name, color, metallic=0.0, roughness=0.5):
    m = bpy.data.materials.new(name)
    m.diffuse_color = (*color, 1)
    m.use_nodes = True
    p = m.node_tree.nodes.get('Principled BSDF')
    p.inputs['Base Color'].default_value = (*color, 1)
    p.inputs['Metallic'].default_value = metallic
    p.inputs['Roughness'].default_value = roughness
    return m

def wood(name, color):
    m = material(name, color, roughness=0.57)
    n, l = m.node_tree.nodes, m.node_tree.links
    tex = n.new('ShaderNodeTexNoise')
    tex.inputs['Scale'].default_value = 4
    tex.inputs['Detail'].default_value = 3
    coord = n.new('ShaderNodeTexCoord')
    mapping = n.new('ShaderNodeVectorMath')
    mapping.operation = 'MULTIPLY'
    mapping.inputs[1].default_value = (1.8, 65, 65)
    l.new(coord.outputs['Generated'], mapping.inputs[0])
    l.new(mapping.outputs['Vector'], tex.inputs['Vector'])
    ramp = n.new('ShaderNodeValToRGB')
    ramp.color_ramp.elements[0].position = 0.18
    ramp.color_ramp.elements[0].color = (*[c * 0.65 for c in color], 1)
    ramp.color_ramp.elements[1].position = 0.85
    ramp.color_ramp.elements[1].color = (*[min(c * 1.25, 1) for c in color], 1)
    l.new(tex.outputs['Fac'], ramp.inputs[0])
    l.new(ramp.outputs['Color'], n.get('Principled BSDF').inputs['Base Color'])
    bump = n.new('ShaderNodeBump')
    bump.inputs['Strength'].default_value = 0.13
    bump.inputs['Distance'].default_value = 0.002
    l.new(tex.outputs['Fac'], bump.inputs['Height'])
    l.new(bump.outputs['Normal'], n.get('Principled BSDF').inputs['Normal'])
    return m

def box(name, loc, size, mat, bevel=0.008):
    bpy.ops.mesh.primitive_cube_add(size=1, location=loc)
    o = bpy.context.object
    o.name = name
    o.dimensions = size
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    o.data.materials.append(mat)
    if bevel:
        b = o.modifiers.new('Soft manufactured edges', 'BEVEL')
        b.width = bevel
        b.segments = 3
        o.modifiers.new('Weighted corner normals', 'WEIGHTED_NORMAL')
    return o

def beam(name, a, b, width, depth, mat):
    a, b = Vector(a), Vector(b)
    o = box(name, (a + b) / 2, (width, depth, (b-a).length), mat)
    o.rotation_euler = (b-a).to_track_quat('Z', 'Y').to_euler()
    return o

def cylinder(name, loc, radius, depth, mat, axis=(0,0,1), vertices=32):
    bpy.ops.mesh.primitive_cylinder_add(vertices=vertices, radius=radius, depth=depth, location=loc)
    o = bpy.context.object
    o.name = name
    o.rotation_euler = Vector(axis).to_track_quat('Z', 'Y').to_euler()
    o.data.materials.append(mat)
    bevel = o.modifiers.new('Edge glint', 'BEVEL')
    bevel.width = 0.0015
    bevel.segments = 2
    o.modifiers.new('Weighted normals', 'WEIGHTED_NORMAL')
    return o

cedar = [wood('Honey cedar ' + str(i), (0.39+i*0.022, 0.19+i*0.013, 0.065+i*0.008)) for i in range(5)]
steel = material('Galvanized fasteners', (0.43,0.47,0.49), 0.82, 0.28)
feet = material('Black protective feet', (0.035,0.042,0.037), roughness=0.8)
ground = material('Warm gravel', (0.23,0.25,0.20), roughness=0.92)

# Full-size timber table: tabletop 2.2 m long and 0.78 m high.
for i in range(5):
    box('Tabletop plank %02d' % (i+1), (0,(i-2)*0.187,0.755), (2.2,0.177,0.05), cedar[i])
for side in (-1,1):
    for i in range(2):
        box('Bench seat plank', (0,side*(0.69+i*0.184),0.438), (2.2,0.174,0.046), cedar[(i+2)%5])

for x in (-0.76,0.76):
    box('Underside tabletop bearer', (x,0,0.68), (0.115,0.94,0.10), cedar[2])
    box('Attached bench cross bearer', (x,0,0.36), (0.12,1.98,0.11), cedar[1])
    for side in (-1,1):
        beam('Splayed A-frame leg', (x,side*0.77,0.06), (x,side*0.30,0.68), 0.115,0.105,cedar[3])
        box('Rubber foot', (x,side*0.77,0.035), (0.13,0.15,0.038), feet)
        for y,z in ((side*0.34,0.625),(side*0.53,0.36)):
            for face in (-1,1):
                cylinder('Bolt washer', (x+face*0.063,y,z), 0.024,0.004,steel,(1,0,0))
                cylinder('Hex carriage bolt', (x+face*0.068,y,z), 0.014,0.008,steel,(1,0,0),6)
    for i in range(5):
        for dx in (-0.027,0.027):
            cylinder('Recessed tabletop screw', (x+dx,(i-2)*0.187,0.7805), 0.005,0.002,steel,vertices=16)
    for side in (-1,1):
        for i in range(2):
            cylinder('Bench screw', (x,side*(0.69+i*0.184),0.4615), 0.006,0.002,steel,vertices=16)
box('Longitudinal lower stretcher', (0,0,0.34), (1.61,0.085,0.10), cedar[0])
for side in (-1,1):
    beam('Diagonal anti-racking brace', (side*0.72,0,0.38), (side*0.18,0,0.681), 0.065,0.072,cedar[1])

box('Ground', (0,0,-0.08), (200,200,0.12), ground, 0)
world = bpy.data.worlds.new('Soft blue daylight')
world.use_nodes = True
world.node_tree.nodes['Background'].inputs[0].default_value = (0.63,0.74,0.88,1)
world.node_tree.nodes['Background'].inputs[1].default_value = 0.45
bpy.context.scene.world = world
bpy.ops.object.light_add(type='AREA', location=(1.5,-3.5,5))
bpy.context.object.data.energy = 650
bpy.context.object.data.shape = 'DISK'
bpy.context.object.data.size = 4
bpy.ops.object.light_add(type='SUN', location=(0,0,5))
bpy.context.object.rotation_euler = (0.45,-0.5,-0.5)
bpy.context.object.data.energy = 1.5
bpy.context.object.data.angle = math.radians(12)
bpy.ops.object.camera_add(location=(3.4,-3.5,2.5))
cam = bpy.context.object
cam.rotation_euler = (Vector((0,0,0.4))-cam.location).to_track_quat('-Z','Y').to_euler()
cam.data.type = 'ORTHO'
cam.data.ortho_scale = 3.75
scene = bpy.context.scene
scene.camera = cam
scene.render.engine = 'CYCLES'
scene.render.resolution_x = 1400
scene.render.resolution_y = 1100
scene.render.resolution_percentage = 100
scene.view_settings.view_transform = 'AgX'
