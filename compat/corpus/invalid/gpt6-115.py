import bpy, math
from mathutils import Vector

bpy.ops.wm.read_factory_settings(use_empty=True)

TRAY_Z = 2.95
TRAY_WIDTH = 0.68
RAIL_HEIGHT = 0.20
HALF = TRAY_WIDTH/2

def material(name, color, metallic=0, roughness=0.45):
    m = bpy.data.materials.new(name)
    m.diffuse_color = (*color, 1)
    m.use_nodes = True
    p = m.node_tree.nodes.get('Principled BSDF')
    p.inputs['Base Color'].default_value = (*color, 1)
    p.inputs['Metallic'].default_value = metallic
    p.inputs['Roughness'].default_value = roughness
    return m

steel = material('Galvanized steel', (0.50, 0.58, 0.63), 0.82, 0.32)
dark_steel = material('Bracket steel', (0.18, 0.23, 0.27), 0.8, 0.34)
hardware = material('Zinc bolt heads', (0.70, 0.74, 0.76), 0.9, 0.24)
black = material('Black power cable jacket', (0.016, 0.022, 0.027), 0.05, 0.46)
blue = material('Blue data cable jacket', (0.035, 0.23, 0.58), 0.08, 0.42)
orange = material('Orange control cable jacket', (0.95, 0.24, 0.035), 0.05, 0.44)
wall_mat = material('Concrete service wall', (0.40, 0.43, 0.44), roughness=0.84)
floor_mat = material('Industrial floor', (0.18, 0.21, 0.24), roughness=0.72)

# Reusable fabrication helpers.
def box(name, loc, dims, mat, bevel=0.008):
    bpy.ops.mesh.primitive_cube_add(size=1, location=loc)
    o = bpy.context.object
    o.name = name
    o.dimensions = dims
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    o.data.materials.append(mat)
    if bevel:
        mod = o.modifiers.new('Fabricated edge rounding', 'BEVEL')
        mod.width = bevel
        mod.segments = 2
        o.modifiers.new('Weighted normals', 'WEIGHTED_NORMAL')
    return o

def beam(name, a, b, width, height, mat):
    a, b = Vector(a), Vector(b)
    o = box(name, (a+b)/2, ((b-a).length, width, height), mat)
    o.rotation_euler = (b-a).to_track_quat('X', 'Z').to_euler()
    return o

def bolt(name, loc, axis=(0, 0, 1), radius=0.029):
    bpy.ops.mesh.primitive_cylinder_add(vertices=6, radius=radius, depth=0.025, location=loc)
    o = bpy.context.object
    o.name = name
    o.rotation_euler = Vector(axis).to_track_quat('Z', 'Y').to_euler()
    o.data.materials.append(hardware)
    return o

def tube(name, points, radius, mat):
    curve = bpy.data.curves.new(name, 'CURVE')
    curve.dimensions = '3D'
    curve.resolution_u = 12
    curve.bevel_depth = radius
    curve.bevel_resolution = 3
    curve.use_fill_caps = True
    spline = curve.splines.new('POLY')
    spline.points.add(len(points)-1)
    for p, co in zip(spline.points, points):
        p.co = (*co, 1)
    obj = bpy.data.objects.new(name, curve)
    bpy.context.collection.objects.link(obj)
    obj.data.materials.append(mat)
    return obj

def rail(a, b, name='Tray side channel'):
    beam(name, (a[0], a[1], TRAY_Z+RAIL_HEIGHT/2), (b[0], b[1], TRAY_Z+RAIL_HEIGHT/2), 0.036, RAIL_HEIGHT, steel)
    beam('Folded top lip', (a[0], a[1], TRAY_Z+RAIL_HEIGHT), (b[0], b[1], TRAY_Z+RAIL_HEIGHT), 0.066, 0.023, steel)
    beam('Folded lower lip', (a[0], a[1], TRAY_Z+0.018), (b[0], b[1], TRAY_Z+0.018), 0.075, 0.026, steel)

def straight(name, start, end, pitch=0.27):
    a, b = Vector((*start, 0)), Vector((*end, 0))
    d = (b-a).normalized()
    n = Vector((-d.y, d.x, 0))
    length = (b-a).length
    for side in (-1, 1):
        p, q = a+n*HALF*side, b+n*HALF*side
        rail(p, q, name+' side rail')
    count = max(2, math.ceil(length/pitch))
    for i in range(count):
        c = a+d*((i+0.5)*length/count)
        p, q = c-n*(HALF-0.015), c+n*(HALF-0.015)
        beam(name+' ladder rung', (p.x,p.y,TRAY_Z+0.036), (q.x,q.y,TRAY_Z+0.036), 0.065, 0.035, steel)

def splice(center, direction):
    c = Vector((*center, 0))
    d = Vector((*direction, 0)).normalized()
    n = Vector((-d.y, d.x, 0))
    for side in (-1, 1):
        p = c+n*(HALF+0.027)*side
        beam('Bolted modular splice plate', (p.x-d.x*0.16,p.y-d.y*0.16,TRAY_Z+0.11), (p.x+d.x*0.16,p.y+d.y*0.16,TRAY_Z+0.11), 0.022, 0.13, dark_steel)
        for shift in (-0.10, 0.10):
            v = p+d*shift+n*side*0.021
            bolt('Splice hex fastener', (v.x,v.y,TRAY_Z+0.11), (n.x*side,n.y*side,0))

# Main run, open T junction, branch run and a swept 90-degree elbow.
straight('Module A', (-5.1, 0), (-3.1, 0))
straight('Module B', (-3.1, 0), (-1.36, 0))
straight('Module C', (-0.64, 0), (1.65, 0))
straight('Module D', (1.65, 0), (3.7, 0))
for x in (-3.1, 1.65):
    splice((x, 0), (1, 0))
# The north rail is omitted across the branch mouth.
rail((-1.36, -HALF), (-0.64, -HALF), 'T junction continuous back rail')
for x in (-1.26, -1.0, -0.74):
    beam('T junction cross rung', (x,-HALF,TRAY_Z+0.036), (x,HALF,TRAY_Z+0.036), 0.065, 0.035, steel)
straight('Branch module E', (-1.0, HALF), (-1.0, 1.75))
straight('Branch module F', (-1.0, 1.75), (-1.0, 3.8))
splice((-1, 1.75), (0, 1))
for x in (-1.36, -0.64):
    splice((x, 0), (1, 0))

elbow_center = (3.7, 0.9)
RADIUS = 0.9

def curved_strip(name, radius, width, z0, z1):
    n = 32
    verts, faces = [], []
    for z, r in [(z0,radius-width/2),(z0,radius+width/2),(z1,radius-width/2),(z1,radius+width/2)]:
        for i in range(n+1):
            a = -math.pi/2+(math.pi/2)*i/n
            verts.append((elbow_center[0]+r*math.cos(a), elbow_center[1]+r*math.sin(a), z))
    s = n+1
    for i in range(n):
        j = i+1
        faces.extend([(i,j,s+j,s+i),(2*s+i,3*s+i,3*s+j,2*s+j),(i,2*s+i,2*s+j,j),(s+i,s+j,3*s+j,3*s+i)])
    faces.extend([(0,s,3*s,2*s),(n,2*s+n,3*s+n,s+n)])
    mesh = bpy.data.meshes.new(name)
    mesh.from_pydata(verts, [], faces)
    mesh.materials.append(steel)
    mesh.update()
    o = bpy.data.objects.new(name, mesh)
    bpy.context.collection.objects.link(o)
    mod = o.modifiers.new('Bend edge rounding', 'BEVEL')
    mod.width = 0.006
    mod.segments = 2
    o.modifiers.new('Weighted normals', 'WEIGHTED_NORMAL')
for r in (RADIUS-HALF, RADIUS+HALF):
    curved_strip('Elbow rolled side rail', r, 0.036, TRAY_Z, TRAY_Z+RAIL_HEIGHT)
    curved_strip('Elbow top lip', r, 0.066, TRAY_Z+RAIL_HEIGHT-0.01, TRAY_Z+RAIL_HEIGHT+0.013)
    curved_strip('Elbow bottom lip', r, 0.075, TRAY_Z+0.005, TRAY_Z+0.031)
for i in range(7):
    a = -math.pi/2+(i+0.5)*math.pi/14
    p = (elbow_center[0]+(RADIUS-HALF)*math.cos(a), elbow_center[1]+(RADIUS-HALF)*math.sin(a), TRAY_Z+0.036)
    q = (elbow_center[0]+(RADIUS+HALF)*math.cos(a), elbow_center[1]+(RADIUS+HALF)*math.sin(a), TRAY_Z+0.036)
    beam('Elbow radial rung', p, q, 0.065, 0.035, steel)
straight('Module G after elbow', (4.6, 0.9), (4.6, 3.8))
splice((3.7, 0), (1, 0))
splice((4.6, 0.9), (0, 1))

# Structural wall brackets have a backplate, arm, diagonal brace and anchors.
box('Service wall', (0, -1.1, 2.35), (12.1, 0.20, 4.7), wall_mat, 0.025)
for x in (-4.55, -2.25, 0.7, 2.95):
    box('Wall bracket backplate', (x, -0.967, 2.62), (0.17, 0.065, 0.79), dark_steel)
    beam('Cantilever tray support', (x,-0.95,TRAY_Z-0.075), (x,0.50,TRAY_Z-0.075), 0.10, 0.10, dark_steel)
    beam('Diagonal bracket gusset', (x,-0.93,2.30), (x,0.28,TRAY_Z-0.13), 0.065, 0.065, dark_steel)
    for z in (2.33, 2.89):
        bolt('Wall expansion anchor', (x,-0.922,z), (0,-1,0), 0.042)
    for y in (-HALF, HALF):
        box('Tray hold down clip', (x,y,TRAY_Z+0.022), (0.15,0.13,0.035), dark_steel)
        bolt('Hold down bolt', (x,y,TRAY_Z+0.052))

# Free branches use floor stands, keeping their support path explicit.
for x in (-1.0, 4.6):
    for y in (1.65, 3.35):
        for dx in (-0.46, 0.46):
            box('Support stand upright', (x+dx,y,(TRAY_Z-0.10)/2), (0.065,0.065,TRAY_Z-0.10), dark_steel)
            box('Stand anchor foot', (x+dx,y,0.035), (0.24,0.24,0.07), dark_steel)
            for dy in (-0.075,0.075):
                bolt('Floor anchor bolt', (x+dx,y+dy,0.083), radius=0.024)
        beam('Stand crossbar', (x-0.53,y,TRAY_Z-0.07), (x+0.53,y,TRAY_Z-0.07), 0.09, 0.09, dark_steel)

# Smoothly sampled cable centerlines follow the available bend radius.
for index, offset in enumerate((-0.20,-0.105,0.0,0.105,0.20)):
    radius = 0.033 if index < 3 else 0.026
    z = TRAY_Z+0.054+radius
    points = [(-5.12,offset,z),(3.7,offset,z)]
    bend_radius = RADIUS-offset
    for k in range(1, 41):
        a = -math.pi/2+(math.pi/2)*k/40
        points.append((3.7+bend_radius*math.cos(a),0.9+bend_radius*math.sin(a),z))
    points.append((4.6-offset,3.85,z))
    tube('Continuous cable through elbow %02d' % index, points, radius, black if index < 3 else blue)
for index, offset in enumerate((-0.13,-0.045,0.045,0.13)):
    z = TRAY_Z+0.16
    turn_radius = 0.57+offset
    cx, cy = -1.60, turn_radius
    points = [(-5.12,0,z),(cx,0,z)]
    for k in range(1, 33):
        a = -math.pi/2+(math.pi/2)*k/32
        points.append((cx+turn_radius*math.cos(a),cy+turn_radius*math.sin(a),z))
    points.append((cx+turn_radius,3.85,z))
    tube('Branch control cable %02d' % index, points, 0.023, orange if index%2 else blue)
# Thin straps pass over and around the cable bundle.
for x in (-4.2,-2.8,0.2,2.7):
    tube('Main run cable retaining strap', [(x,-0.26,TRAY_Z+0.035),(x,-0.26,TRAY_Z+0.205),(x,0.26,TRAY_Z+0.205),(x,0.26,TRAY_Z+0.035)], 0.010, black)
box('Industrial slab', (0,1,-0.13), (200,200,0.20), floor_mat, 0)

def light(loc, energy, size):
    bpy.ops.object.light_add(type='AREA', location=loc)
    o = bpy.context.object
    o.data.energy = energy
    o.data.size = size
    o.rotation_euler = (Vector((0,1,2))-o.location).to_track_quat('-Z','Y').to_euler()
light((-3,5,10), 2500, 7)
light((7,2,8), 2100, 5)
light((-6,-0.3,6), 1200, 4)
bpy.ops.object.camera_add(location=(11,14,11))
cam = bpy.context.object
cam.rotation_euler = (Vector((0,1.1,2.0))-cam.location).to_track_quat('-Z','Y').to_euler()
cam.data.type = 'ORTHO'
cam.data.ortho_scale = 15.2
scene = bpy.context.scene
scene.camera = cam
scene.render.engine = 'CYCLES'
scene.render.resolution_x = 1600
scene.render.resolution_y = 1150
scene.render.resolution_percentage = 100
scene.world.color = (0.26,0.26,0.26)
