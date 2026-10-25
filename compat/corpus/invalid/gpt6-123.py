import bpy, math
from mathutils import Vector
bpy.ops.wm.read_factory_settings(use_empty=True)

def mat(name, rgb, metallic=0, roughness=0.4):
    m = bpy.data.materials.new(name)
    m.diffuse_color = (*rgb, 1)
    m.use_nodes = True
    p = m.node_tree.nodes.get('Principled BSDF')
    p.inputs['Base Color'].default_value = (*rgb, 1)
    p.inputs['Metallic'].default_value = metallic
    p.inputs['Roughness'].default_value = roughness
    return m

def finish(o, name, material, bevel=0.02):
    o.name = name
    o.data.materials.append(material)
    if bevel:
        mod = o.modifiers.new('Fabrication edge bevel', 'BEVEL')
        mod.width, mod.segments = bevel, 2
        o.modifiers.new('Weighted normals', 'WEIGHTED_NORMAL')
    return o

def box(name, loc, size, material, bevel=0.02):
    bpy.ops.mesh.primitive_cube_add(size=1, location=loc)
    o = bpy.context.object
    o.dimensions = size
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    return finish(o, name, material, bevel)

def cyl(name, a, b, radius, material, vertices=32):
    a, b = Vector(a), Vector(b)
    bpy.ops.mesh.primitive_cylinder_add(vertices=vertices, radius=radius, depth=(b-a).length, location=(a+b)/2)
    o = bpy.context.object
    o.rotation_mode = 'QUATERNION'
    o.rotation_quaternion = (b-a).to_track_quat('Z', 'Y')
    finish(o, name, material, 0.008)
    for p in o.data.polygons:
        p.use_smooth = len(p.vertices) == 4
    return o

def sphere(name, loc, scale, material):
    bpy.ops.mesh.primitive_uv_sphere_add(segments=32, ring_count=16, location=loc)
    o = bpy.context.object
    o.scale = scale
    finish(o, name, material, 0)
    for p in o.data.polygons:
        p.use_smooth = True
    return o

def torus(name, loc, major, minor, material, axis=(0,0,1)):
    bpy.ops.mesh.primitive_torus_add(major_radius=major, minor_radius=minor, major_segments=40, minor_segments=10, location=loc)
    o = bpy.context.object
    o.rotation_mode = 'QUATERNION'
    o.rotation_quaternion = Vector(axis).to_track_quat('Z', 'Y')
    finish(o, name, material, 0)
    for p in o.data.polygons:
        p.use_smooth = True
    return o

def pipe(name, points, radius, material):
    c = bpy.data.curves.new(name, 'CURVE')
    c.dimensions, c.bevel_depth, c.bevel_resolution = '3D', radius, 3
    s = c.splines.new('POLY')
    s.points.add(len(points)-1)
    for p, co in zip(s.points, points):
        p.co = (*co, 1)
    o = bpy.data.objects.new(name, c)
    bpy.context.collection.objects.link(o)
    o.data.materials.append(material)

def flange(center, axis, pipe_radius=0.11):
    c, n = Vector(center), Vector(axis).normalized()
    u = n.cross(Vector((0,0,1)))
    if u.length < 0.1:
        u = n.cross(Vector((0,1,0)))
    u.normalize()
    v = n.cross(u)
    for t in (-0.043, 0.043):
        cyl('Mating flange plate', c+n*(t-0.034), c+n*(t+0.034), pipe_radius*2.05, steel)
    cyl('Flange gasket', c-n*0.009, c+n*0.009, pipe_radius*1.94, black)
    for i in range(8):
        angle = i*math.tau/8
        p = c+pipe_radius*1.63*(u*math.cos(angle)+v*math.sin(angle))
        cyl('Flange stud', p-n*0.105, p+n*0.105, 0.018, steel, 12)
        for t in (-0.095, 0.095):
            cyl('Hex flange nut', p+n*(t-0.014), p+n*(t+0.014), 0.031, black, 6)

def valve(x, y, z):
    cyl('Valve inline barrel', (x-0.2,y,z), (x+0.2,y,z), 0.17, teal)
    sphere('Valve body casting', (x,y,z), (0.2,0.17,0.2), teal)
    cyl('Valve bonnet', (x,y,z), (x,y,z+0.31), 0.085, steel)
    cyl('Valve stem', (x,y,z+0.28), (x,y,z+0.52), 0.026, steel)
    torus('Red valve handwheel', (x,y,z+0.51), 0.23, 0.028, red)
    for i in range(4):
        a = i*math.pi/2
        cyl('Handwheel spoke', (x,y,z+0.51), (x+0.21*math.cos(a),y+0.21*math.sin(a),z+0.51), 0.017, red, 12)
    flange((x-0.23,y,z), (1,0,0))
    flange((x+0.23,y,z), (1,0,0))

def label(body, loc, size, material):
    c = bpy.data.curves.new(body, 'FONT')
    c.body, c.size, c.align_x = body, size, 'CENTER'
    o = bpy.data.objects.new(body, c)
    bpy.context.collection.objects.link(o)
    o.location = loc
    o.rotation_euler.x = math.pi/2
    o.data.materials.append(material)

steel = mat('Stainless fittings', (0.5,0.58,0.6), 0.85, 0.26)
blue = mat('Motor blue enamel', (0.025,0.13,0.32), 0.5)
teal = mat('Pump green enamel', (0.035,0.3,0.25), 0.45)
yellow = mat('Skid safety paint', (0.91,0.47,0.035), 0.4)
black = mat('Black rubber and bolts', (0.022,0.028,0.031), 0.3)
red = mat('Valve red', (0.64,0.035,0.018), 0.35)
white = mat('Gauge dial', (0.9,0.91,0.86))
gray = mat('Studio floor', (0.12,0.15,0.18), 0, 0.8)
box('Ground', (0,0,-0.15), (200,200,0.2), gray)
for y in (-1.42,1.42):
    box('Longitudinal skid rail', (0,y,0.22), (6.1,0.2,0.35), yellow)
for x in (-2.95,-1.35,0.5,2.95):
    box('Skid crossmember', (x,0,0.22), (0.18,2.9,0.35), yellow)
    for y in (-1.42,1.42):
        box('Anchor foot', (x,y,0.065), (0.38,0.38,0.09), steel)
        cyl('Anchor bolt', (x,y,0.1), (x,y,0.19), 0.055, black, 6)
box('Perforated deck backing', (0,0,0.415), (5.8,2.67,0.045), black)
for j in range(30):
    box('Deck grating bar', (-2.8+j*0.193,0,0.452), (0.055,2.65,0.05), steel, 0.005)

for row, y in enumerate((-0.79,0.74)):
    for x in (-2.3,-1.27,-0.48):
        box('Equipment mounting foot', (x,y,0.59), (0.42,0.66,0.23), blue if x < -1 else teal)
        for dy in (-0.25,0.25):
            cyl('Hold down bolt', (x,y+dy,0.7), (x,y+dy,0.76), 0.042, steel, 6)
    cyl('Electric motor body', (-2.57,y,1.01), (-1.2,y,1.01), 0.34, blue)
    for i in range(16):
        a = math.tau*i/16
        o = box('Motor longitudinal cooling fin', (-1.94,y+0.354*math.sin(a),1.01+0.354*math.cos(a)), (1.15,0.035,0.095), blue, 0.006)
        o.rotation_euler.x = -a
    cyl('Motor fan shroud', (-2.71,y,1.01), (-2.54,y,1.01), 0.38, black)
    for i in range(5):
        z = 0.79+i*0.105
        box('Fan guard rib', (-2.723,y,z), (0.025,0.48,0.018), steel, 0.003)
    box('Motor terminal box', (-1.83,y,1.45), (0.46,0.4,0.22), blue)
    cyl('Drive coupling', (-1.21,y,1.01), (-0.88,y,1.01), 0.13, steel)
    cyl('Yellow coupling guard', (-1.14,y,1.01), (-0.91,y,1.01), 0.23, yellow)
    cyl('Centrifugal pump casing', (-0.85,y,1.01), (-0.34,y,1.01), 0.38, teal)
    cyl('Pump suction nozzle', (-0.34,y,1.01), (0.0,y,1.01), 0.11, steel)
    flange((-0.12,y,1.01), (1,0,0))
    cyl('Suction line', (0,y,1.01), (2.1,y,1.01), 0.11, steel)
    valve(0.6,y,1.01)
    cyl('Pump discharge riser', (-0.6,y,1.25), (-0.6,y,1.94), 0.095, steel)
    flange((-0.6,y,1.58), (0,0,1), 0.095)
    # Rounded 90-degree elbow into the common discharge header.
    pts = [(-0.6,y,1.88)]
    for k in range(9):
        a = math.pi-(math.pi/2)*k/8
        pts.append((-0.42+0.18*math.cos(a),y,1.88+0.18*math.sin(a)))
    pts.append((1.18,y,2.06))
    pipe('Discharge elbow and branch', pts, 0.095, steel)
    cyl('Gauge takeoff', (0.12,y,2.06), (0.12,y,2.36), 0.025, steel)
    cyl('Pressure gauge housing', (0.12,y+0.045,2.45), (0.12,y-0.065,2.45), 0.14, black)
    cyl('Gauge ivory face', (0.12,y-0.068,2.45), (0.12,y-0.075,2.45), 0.12, white)
    for i in range(9):
        a = math.radians(-35+i*31)
        p = (0.12+0.092*math.cos(a),y-0.08,2.45+0.092*math.sin(a))
        q = (0.12+0.107*math.cos(a),y-0.08,2.45+0.107*math.sin(a))
        cyl('Gauge tick', p,q,0.004,black,8)
    cyl('Gauge pointer', (0.12,y-0.086,2.45), (0.075,y-0.086,2.52), 0.005,red,8)

cyl('Discharge header', (1.18,-1.15,2.06), (1.18,1.15,2.06), 0.13, steel)
flange((1.18,-1.08,2.06), (0,1,0), 0.13)
for y in (-0.72,0.73):
    x = 2.12
    for dx in (-0.31,0.31):
        box('Tank support leg', (x+dx,y,0.68), (0.12,0.24,0.43), teal)
    cyl('Vertical accumulator shell', (x,y,0.94), (x,y,2.43), 0.43, steel, 48)
    sphere('Dished lower tank head', (x,y,0.94), (0.43,0.43,0.22), steel)
    sphere('Dished upper tank head', (x,y,2.43), (0.43,0.43,0.22), steel)
    for z in (1.03,2.34):
        torus('Tank circumferential weld', (x,y,z), 0.432,0.014,steel)
    cyl('Top service neck', (x,y,2.58), (x,y,2.8), 0.09,steel)
    flange((x,y,2.75),(0,0,1),0.09)
    box('Tank identification plate', (x,y-0.435,1.77), (0.39,0.023,0.28),black)
    label('ACC-%02d'%(1 if y<0 else 2),(x,y-0.453,1.76),0.074,white)
    cyl('Tank header connection', (1.18,y,2.06), (x-0.38,y,2.06), 0.095,steel)
    flange((1.53,y,2.06),(1,0,0),0.095)
box('Skid equipment plaque', (0,-1.531,0.23), (1.6,0.028,0.23),black)
label('P-204  /  DUPLEX PUMP',(0,-1.551,0.185),0.095,white)
for name,loc,power,color,size in [('Key',(1,-6,9),1700,(0.8,0.9,1),5),('Fill',(-5,-1,5),1000,(1,0.75,0.5),4),('Rim',(3,5,7),1800,(0.6,0.8,1),4)]:
    d=bpy.data.lights.new(name,'AREA')
    d.energy,d.color,d.size=power,color,size
    o=bpy.data.objects.new(name,d)
    bpy.context.collection.objects.link(o)
    o.location=loc
    o.rotation_euler=(Vector((0,0,1))-o.location).to_track_quat('-Z','Y').to_euler()
bpy.ops.object.camera_add(location=(8,-11,8))
cam=bpy.context.object
cam.rotation_euler=(Vector((0,0,1.25))-cam.location).to_track_quat('-Z','Y').to_euler()
cam.data.type,cam.data.ortho_scale='ORTHO',9
scene=bpy.context.scene
scene.camera=cam
scene.world.color=(0.13,0.13,0.13)
scene.render.engine='CYCLES'
scene.render.resolution_x,scene.render.resolution_y=1500,1100
scene.render.resolution_percentage=100
scene.view_settings.view_transform='AgX'
