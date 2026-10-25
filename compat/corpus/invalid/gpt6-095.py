import bpy, math
from mathutils import Vector

bpy.ops.wm.read_factory_settings(use_empty=True)

def material(name, color, metallic=0, roughness=0.4):
    m = bpy.data.materials.new(name)
    m.diffuse_color = (*color,1)
    m.use_nodes = True
    p = m.node_tree.nodes.get('Principled BSDF')
    p.inputs['Base Color'].default_value = (*color,1)
    p.inputs['Metallic'].default_value = metallic
    p.inputs['Roughness'].default_value = roughness
    return m

def rod(name,a,b,radius,mat):
    a,b = Vector(a),Vector(b)
    bpy.ops.mesh.primitive_cylinder_add(vertices=40,radius=radius,depth=(b-a).length,location=(a+b)/2)
    o = bpy.context.object
    o.name = name
    o.rotation_euler = (b-a).to_track_quat('Z','Y').to_euler()
    o.data.materials.append(mat)
    bevel = o.modifiers.new('Soft edges','BEVEL')
    bevel.width = min(0.012,radius*0.2)
    bevel.segments = 3
    o.modifiers.new('Weighted normals','WEIGHTED_NORMAL')
    return o

def ball(name,loc,radius,mat):
    bpy.ops.mesh.primitive_uv_sphere_add(segments=24,ring_count=16,radius=radius,location=loc)
    o = bpy.context.object
    o.name = name
    o.data.materials.append(mat)
    for p in o.data.polygons:
        p.use_smooth = True
    return o

def bent_wood(name,points,radius,mat):
    curve = bpy.data.curves.new(name,'CURVE')
    curve.dimensions = '3D'
    curve.resolution_u = 24
    curve.bevel_depth = radius
    curve.bevel_resolution = 5
    curve.use_fill_caps = True
    s = curve.splines.new('BEZIER')
    s.bezier_points.add(len(points)-1)
    for p,co in zip(s.bezier_points,points):
        p.co = co
        p.handle_left_type = 'AUTO'
        p.handle_right_type = 'AUTO'
    o = bpy.data.objects.new(name,curve)
    bpy.context.collection.objects.link(o)
    o.data.materials.append(mat)
    return o

wood = material('Honey walnut', (0.27,0.115,0.045), roughness=0.33)
brass = material('Antique brass collars', (0.46,0.29,0.09), 0.8, 0.3)
rubber = material('Protective foot pads', (0.023,0.022,0.019), roughness=0.85)
floor = material('Warm studio floor', (0.34,0.32,0.28), roughness=0.8)
# Subtle procedural grain on all wooden parts.
nodes, links = wood.node_tree.nodes, wood.node_tree.links
coord = nodes.new('ShaderNodeTexCoord')
scale = nodes.new('ShaderNodeVectorMath')
scale.operation = 'MULTIPLY'
scale.inputs[1].default_value = (7,7,0.65)
noise = nodes.new('ShaderNodeTexNoise')
noise.inputs['Scale'].default_value = 4
noise.inputs['Detail'].default_value = 2
ramp = nodes.new('ShaderNodeValToRGB')
ramp.color_ramp.elements[0].color = (0.105,0.034,0.009,1)
ramp.color_ramp.elements[1].color = (0.36,0.17,0.065,1)
links.new(coord.outputs['Generated'],scale.inputs[0])
links.new(scale.outputs['Vector'],noise.inputs['Vector'])
links.new(noise.outputs['Fac'],ramp.inputs[0])
links.new(ramp.outputs[0],nodes.get('Principled BSDF').inputs['Base Color'])

bpy.ops.mesh.primitive_plane_add(size=200)
bpy.context.object.name = 'Studio floor'
bpy.context.object.data.materials.append(floor)
rod('Central walnut mast',(0,0,0.19),(0,0,1.97),0.044,wood)
rod('Lower turned pedestal',(0,0,0.14),(0,0,0.38),0.071,wood)
for z, r, h in [(0.20,0.078,0.032),(0.37,0.065,0.025),(1.27,0.06,0.072),(1.73,0.063,0.11),(1.94,0.056,0.025)]:
    rod('Brass binding collar',(0,0,z-h/2),(0,0,z+h/2),r,brass)
ball('Turned top finial',(0,0,2.015),0.075,wood)
rod('Finial neck',(0,0,1.95),(0,0,2.00),0.035,brass)

# Four broad swept feet provide a stable footprint.
for i in range(4):
    a = math.radians(45+i*90)
    def footpoint(r,z):
        return (r*math.cos(a),r*math.sin(a),z)
    points = [footpoint(0.035,0.31),footpoint(0.16,0.23),footpoint(0.33,0.105),footpoint(0.49,0.064)]
    bent_wood('Swept walnut foot',points,0.038,wood)
    ball('Rounded foot end',points[-1],0.039,wood)
    x,y,z = points[-1]
    rod('Rubber floor pad',(x,y,0.009),(x,y,0.033),0.042,rubber)

# Six high hooks bend outward, dip and turn upward to retain coats.
for i in range(6):
    a = math.radians(i*60)
    def point(r,z):
        return (r*math.cos(a),r*math.sin(a),z)
    points = [point(0.042,1.74),point(0.17,1.81),point(0.32,1.83),point(0.39,1.91),point(0.375,2.025)]
    bent_wood('Upper curved coat hook %02d' % (i+1),points,0.023,wood)
    ball('Upper hook rounded tip',points[-1],0.036,wood)
    rod('Upper hook ferrule',point(0.048,1.744),point(0.094,1.77),0.028,brass)

# Three staggered lower hooks accommodate bags and shorter garments.
for i in range(3):
    a = math.radians(30+i*120)
    def point(r,z):
        return (r*math.cos(a),r*math.sin(a),z)
    points = [point(0.045,1.28),point(0.14,1.22),point(0.245,1.24),point(0.27,1.34)]
    bent_wood('Lower bag hook %02d' % (i+1),points,0.021,wood)
    ball('Lower hook rounded tip',points[-1],0.032,wood)
    rod('Lower hook ferrule',point(0.045,1.28),point(0.087,1.253),0.026,brass)

scene = bpy.context.scene
scene.world.color = (0.23,0.23,0.23)
for loc,energy,size in [((3,-4,5),700,4),((-3,-1,3),450,3),((1,3,4),550,3)]:
    bpy.ops.object.light_add(type='AREA',location=loc)
    o = bpy.context.object
    o.data.energy = energy
    o.data.size = size
    o.rotation_euler = (Vector((0,0,1))-o.location).to_track_quat('-Z','Y').to_euler()
bpy.ops.object.camera_add(location=(3.1,-4.7,2.8))
camera = bpy.context.object
camera.rotation_euler = (Vector((0,0,1.05))-camera.location).to_track_quat('-Z','Y').to_euler()
camera.data.type = 'ORTHO'
camera.data.ortho_scale = 2.65
scene.camera = camera
scene.render.engine = 'CYCLES'
scene.render.resolution_x = 1000
scene.render.resolution_y = 1400
scene.render.resolution_percentage = 100
