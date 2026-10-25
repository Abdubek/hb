import bpy, math
from mathutils import Vector

bpy.ops.wm.read_factory_settings(use_empty=True)
scene = bpy.context.scene
scene.render.engine = 'CYCLES'
scene.cycles.samples = 96
scene.render.resolution_x = 1500
scene.render.resolution_y = 1500
scene.render.resolution_percentage = 100
scene.view_settings.view_transform = 'AgX'
scene.world.color = (0.16, 0.16, 0.16)

def material(name, color, metallic=0, roughness=0.4):
    m = bpy.data.materials.new(name)
    m.diffuse_color = (*color, 1)
    m.use_nodes = True
    p = m.node_tree.nodes.get('Principled BSDF')
    p.inputs['Base Color'].default_value = (*color, 1)
    p.inputs['Metallic'].default_value = metallic
    p.inputs['Roughness'].default_value = roughness
    return m

steel = material('Fine horizontally brushed stainless steel', (0.48, 0.52, 0.56), 1, 0.28)
n = steel.node_tree.nodes
l = steel.node_tree.links
tex = n.new('ShaderNodeTexCoord')
mapn = n.new('ShaderNodeVectorMath')
mapn.operation = 'MULTIPLY'
mapn.inputs[1].default_value = (5, 5, 240)
noise = n.new('ShaderNodeTexNoise')
noise.inputs['Scale'].default_value = 1
noise.inputs['Detail'].default_value = 2
bump = n.new('ShaderNodeBump')
bump.inputs['Strength'].default_value = 0.16
bump.inputs['Distance'].default_value = 0.0015
l.new(tex.outputs['Generated'], mapn.inputs[0])
l.new(mapn.outputs['Vector'], noise.inputs['Vector'])
l.new(noise.outputs['Fac'], bump.inputs['Height'])
l.new(bump.outputs['Normal'], n.get('Principled BSDF').inputs['Normal'])
black = material('Matte charcoal polymer', (0.015, 0.02, 0.025), 0, 0.28)
chrome = material('Polished edge steel', (0.65, 0.69, 0.72), 1, 0.15)
backdrop = material('Warm grey seamless paper', (0.34, 0.32, 0.29), 0, 0.7)
led = material('Amber switch light', (0.9, 0.22, 0.025), 0, 0.2)
p = led.node_tree.nodes.get('Principled BSDF')
p.inputs['Emission Color'].default_value = (1, 0.16, 0.01, 1)
p.inputs['Emission Strength'].default_value = 3

def smooth(obj, mat):
    obj.data.materials.append(mat)
    for poly in obj.data.polygons:
        poly.use_smooth = True
    return obj

def lathe(name, profile, mat, segments=128):
    verts = [(r*math.cos(2*math.pi*j/segments), r*math.sin(2*math.pi*j/segments), z) for r,z in profile for j in range(segments)]
    faces = []
    for i in range(len(profile)-1):
        for j in range(segments):
            a = i*segments+j
            b = i*segments+(j+1)%segments
            faces.append((a,b,b+segments,a+segments))
    mesh = bpy.data.meshes.new(name)
    mesh.from_pydata(verts, [], faces)
    mesh.update()
    obj = bpy.data.objects.new(name, mesh)
    scene.collection.objects.link(obj)
    return smooth(obj, mat)

def cylinder(name, radius, depth, z, mat):
    bpy.ops.mesh.primitive_cylinder_add(vertices=96, radius=radius, depth=depth, location=(0,0,z))
    o = bpy.context.object
    o.name = name
    smooth(o, mat)
    b = o.modifiers.new('Rounded manufactured edges', 'BEVEL')
    b.width = 0.015
    b.segments = 3
    o.modifiers.new('Weighted normals', 'WEIGHTED_NORMAL')
    return o

def tube_curve(name, points, radius, mat):
    c = bpy.data.curves.new(name, 'CURVE')
    c.dimensions = '3D'
    c.resolution_u = 24
    c.bevel_depth = radius
    c.bevel_resolution = 5
    c.use_fill_caps = True
    s = c.splines.new('BEZIER')
    s.bezier_points.add(len(points)-1)
    for p,co in zip(s.bezier_points, points):
        p.co = co
        p.handle_left_type = 'AUTO'
        p.handle_right_type = 'AUTO'
    o = bpy.data.objects.new(name, c)
    scene.collection.objects.link(o)
    o.data.materials.append(mat)
    return o

cylinder('Cordless power base', 0.78, 0.115, 0.0775, black)
cylinder('Base steel reveal', 0.745, 0.032, 0.143, chrome)
lathe('Spun steel kettle body', [(0,0.16),(0.62,0.16),(0.70,0.19),(0.75,0.29),(0.77,0.50),(0.75,0.95),(0.68,1.38),(0.56,1.66),(0.48,1.74),(0.44,1.75),(0.44,1.71),(0.52,1.65),(0.64,1.37),(0.71,0.94),(0.73,0.5),(0.70,0.30),(0.60,0.21),(0,0.21)], steel)
cylinder('Lid gasket', 0.465, 0.035, 1.753, black)
lathe('Domed removable lid', [(0,1.82),(0.20,1.82),(0.39,1.795),(0.465,1.775),(0.477,1.79),(0.44,1.82),(0.32,1.855),(0,1.87)], steel)
cylinder('Lid grip', 0.13, 0.10, 1.90, black)

# Open, double-walled pouring spout. Cross-sections follow its upward axis.
centers = [Vector((-0.57,0,1.29)), Vector((-0.79,0,1.41)), Vector((-1.01,0,1.57)), Vector((-1.23,0,1.77))]
radii = [0.245,0.21,0.165,0.18]
N = 64
verts = []
for inner in (False, True):
    for i,(center,r) in enumerate(zip(centers,radii)):
        tangent = (centers[min(i+1,3)]-centers[max(0,i-1)]).normalized()
        u = Vector((0,1,0))
        v = tangent.cross(u).normalized()
        rr = r-(0.025 if inner else 0)
        for j in range(N):
            a = 2*math.pi*j/N
            verts.append(tuple(center + rr*(math.cos(a)*u + math.sin(a)*v)))
faces = []
for side in range(2):
    offset = side*4*N
    for i in range(3):
        for j in range(N):
            a,b = offset+i*N+j, offset+i*N+(j+1)%N
            face = (a,b,b+N,a+N)
            faces.append(face if side == 0 else tuple(reversed(face)))
for j in range(N):
    a,b = 3*N+j,3*N+(j+1)%N
    faces.append((a,b,b+4*N,a+4*N))
mesh = bpy.data.meshes.new('Hollow pouring spout mesh')
mesh.from_pydata(verts, [], faces)
mesh.update()
o = bpy.data.objects.new('Hollow rolled-lip spout', mesh)
scene.collection.objects.link(o)
smooth(o, steel)
# The dark recessed throat reads as the internal filter, hiding the body intersection.
bpy.ops.mesh.primitive_uv_sphere_add(segments=32, ring_count=16, radius=1, location=(-0.70,0,1.37))
o = bpy.context.object
o.name = 'Recessed dark spout filter'
o.scale = (0.055,0.19,0.19)
smooth(o, black)
tube_curve('Insulated loop handle', [(0.48,0,1.62),(0.93,0,1.68),(1.20,0,1.42),(1.24,0,0.83),(1.02,0,0.48),(0.71,0,0.46)], 0.105, black)
for x,z in [(0.58,1.61),(0.70,0.46)]:
    bpy.ops.mesh.primitive_uv_sphere_add(segments=32, ring_count=16, radius=1, location=(x,0,z))
    o = bpy.context.object
    o.name = 'Steel handle anchor'
    o.scale = (0.17,0.135,0.11)
    smooth(o, chrome)
tube_curve('Power toggle', [(0.73,-0.035,0.31),(0.96,-0.035,0.30)], 0.045, black)
bpy.ops.mesh.primitive_uv_sphere_add(segments=24, ring_count=12, radius=1, location=(0.91,-0.077,0.315))
o = bpy.context.object
o.name = 'Illuminated toggle indicator'
o.scale = (0.040,0.012,0.015)
smooth(o, led)

# Floor rolls continuously up into the background.
profile = [(-8,0),(2.5,0)]
for i in range(1,25):
    a = (math.pi/2)*i/24
    profile.append((2.5+2*math.sin(a),2-2*math.cos(a)))
profile.append((4.5,7))
verts = [(x,y,z) for y,z in profile for x in (-9,9)]
faces = [(2*i,2*i+1,2*i+3,2*i+2) for i in range(len(profile)-1)]
mesh = bpy.data.meshes.new('Cyclorama surface')
mesh.from_pydata(verts, [], faces)
mesh.update()
o = bpy.data.objects.new('Seamless studio cyclorama', mesh)
scene.collection.objects.link(o)
smooth(o, backdrop)

def aim(obj, target):
    obj.rotation_euler = (Vector(target)-obj.location).to_track_quat('-Z','Y').to_euler()
def area(name, pos, target, power, size, size_y):
    d = bpy.data.lights.new(name, 'AREA')
    d.energy = power
    d.shape = 'RECTANGLE'
    d.size = size
    d.size_y = size_y
    o = bpy.data.objects.new(name,d)
    scene.collection.objects.link(o)
    o.location = pos
    aim(o,target)
area('Large left diffusion panel', (-3,-3,4.3), (0,0,1), 650, 2.2, 3.5)
area('Tall right reflection strip', (3,0.5,3), (0,0,1), 800, 0.8, 3.5)
area('Overhead softbox', (0,1,5), (0,0,0.5), 500, 3, 2)
area('Front fill', (0,-4,2), (0,0,1), 120, 3, 3)
bpy.ops.object.camera_add(location=(-3.4,-6.4,3.0))
cam = bpy.context.object
cam.name = 'Product hero camera'
aim(cam, (0,0,1.02))
cam.data.lens = 60
cam.data.dof.use_dof = True
bpy.ops.object.empty_add(location=(0,-0.10,1.0))
cam.data.dof.focus_object = bpy.context.object
cam.data.dof.aperture_fstop = 8
scene.camera = cam
