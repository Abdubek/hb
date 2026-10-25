import bpy, math
from mathutils import Vector

bpy.ops.wm.read_factory_settings(use_empty=True)
scene = bpy.context.scene
scene.render.engine = 'CYCLES'
scene.cycles.samples = 128
scene.render.resolution_x = 1600
scene.render.resolution_y = 1200
scene.render.resolution_percentage = 100
scene.unit_settings.system = 'METRIC'
scene.view_settings.view_transform = 'AgX'
scene.world.color = (0.10,0.10,0.10)

def mat(name,color,metal=0,rough=0.3):
    m = bpy.data.materials.new(name)
    m.diffuse_color = (*color,1)
    m.use_nodes = True
    p = m.node_tree.nodes.get('Principled BSDF')
    p.inputs['Base Color'].default_value = (*color,1)
    p.inputs['Metallic'].default_value = metal
    p.inputs['Roughness'].default_value = rough
    return m
steel = mat('Satin stainless steel',(0.48,0.53,0.59),1,0.23)
polish = mat('Polished steel bevels',(0.68,0.73,0.8),1,0.13)
dial = mat('Midnight blue dial',(0.014,0.055,0.09),0.45,0.3)
leather = mat('Dark brown leather',(0.035,0.013,0.008),0,0.52)
stitch = mat('Linen stitching',(0.49,0.34,0.17),0,0.65)
lume = mat('Ivory indices',(0.84,0.88,0.75),0.15,0.26)
red = mat('Orange seconds hand',(0.95,0.17,0.025),0.3,0.25)
blockmat = mat('Graphite display suede',(0.035,0.045,0.052),0,0.85)
floor = mat('Neutral studio floor',(0.16,0.18,0.2),0,0.75)
crystal = mat('Sapphire crystal',(0.98,0.99,1),0,0.025)
p = crystal.node_tree.nodes.get('Principled BSDF')
p.inputs['Transmission Weight'].default_value = 1
p.inputs['IOR'].default_value = 1.76
# Fine leather grain in physical coordinates.
n = leather.node_tree.nodes
l = leather.node_tree.links
noise = n.new('ShaderNodeTexNoise')
noise.inputs['Scale'].default_value = 1700
coord = n.new('ShaderNodeTexCoord')
bump = n.new('ShaderNodeBump')
bump.inputs['Strength'].default_value = 0.22
bump.inputs['Distance'].default_value = 0.00010
l.new(coord.outputs['Object'],noise.inputs['Vector'])
l.new(noise.outputs['Fac'],bump.inputs['Height'])
l.new(bump.outputs['Normal'],n.get('Principled BSDF').inputs['Normal'])

bpy.ops.object.empty_add()
rig = bpy.context.object
rig.name = 'Tilted watch and display assembly'
rig.rotation_euler = (math.radians(12),math.radians(-9),math.radians(-18))

def finish(o,name,m,parent=True):
    o.name = name
    o.data.materials.append(m)
    if parent:
        o.parent = rig
    return o

def box(name,loc,dims,m,bevel=0,parent=True):
    bpy.ops.mesh.primitive_cube_add(size=1,location=loc)
    o = finish(bpy.context.object,name,m,parent)
    o.dimensions = dims
    bpy.ops.object.transform_apply(location=False,rotation=False,scale=True)
    if bevel:
        b = o.modifiers.new('Edge radius','BEVEL')
        b.width = bevel
        b.segments = 3
        o.modifiers.new('Weighted normals','WEIGHTED_NORMAL')
    return o

def cyl(name,radius,depth,z,m,xy=(0,0)):
    bpy.ops.mesh.primitive_cylinder_add(vertices=96,radius=radius,depth=depth,location=(*xy,z))
    o = finish(bpy.context.object,name,m)
    for f in o.data.polygons:
        f.use_smooth = True
    b = o.modifiers.new('Edge radius','BEVEL')
    b.width = min(depth*0.15,0.0005)
    b.segments = 3
    o.modifiers.new('Weighted normals','WEIGHTED_NORMAL')
    return o

def ring(name,r1,r2,z1,z2,m):
    N = 128
    verts = [(r*math.cos(2*math.pi*j/N),r*math.sin(2*math.pi*j/N),z) for r,z in [(r1,z1),(r1,z2),(r2,z2),(r2,z1)] for j in range(N)]
    faces = []
    for k in range(4):
        for j in range(N):
            faces.append((k*N+j,k*N+(j+1)%N,((k+1)%4)*N+(j+1)%N,((k+1)%4)*N+j))
    me = bpy.data.meshes.new(name)
    me.from_pydata(verts,[],faces)
    me.update()
    o = bpy.data.objects.new(name,me)
    scene.collection.objects.link(o)
    finish(o,name,m)
    for f in me.polygons:
        f.use_smooth = True
    b = o.modifiers.new('Bezel edge glints','BEVEL')
    b.width = 0.00022
    b.segments = 3
    return o

block = box('Tilted beveled display block',(0,0,0),(0.072,0.15,0.027),blockmat,0.004)
# Lift the rotated block so its lowest bounding corner rests on the floor.
rotation = rig.rotation_euler.to_matrix()
rig.location.z = -min((rotation @ Vector((x,y,z))).z for x in (-0.036,0.036) for y in (-0.075,0.075) for z in (-0.0135,0.0135)) + 0.0003
for sign in (-1,1):
    box('Leather strap', (0,sign*0.043,0.0152), (0.0195,0.056,0.003), leather,0.0012)
    for x in (-0.008,0.008):
        for j in range(24):
            box('Individual strap stitch',(x,sign*(0.023+j*0.0019),0.01676),(0.00028,0.0010,0.00014),stitch,0.00005)
    for x in (-0.0082,0.0082):
        box('Case lug',(x,sign*0.020,0.0195),(0.005,0.009,0.006),steel,0.0013)
for j in range(5):
    cyl('Dark recessed strap hole',0.0007,0.00015,0.0168,blockmat,(0,-0.043-j*0.004))
for x in (-0.0105,0.0105):
    box('Buckle side rail',(x,0.064,0.018),(0.0018,0.013,0.002),polish,0.0005)
for y in (0.058,0.070):
    box('Buckle crossbar',(0,y,0.018),(0.021,0.0018,0.002),polish,0.0005)
box('Buckle tongue',(0,0.064,0.019),(0.0012,0.012,0.001),polish,0.0003)
cyl('Case body - 42mm',0.021,0.008,0.0205,steel)
ring('Polished bezel',0.0213,0.0187,0.024,0.0265,polish)
cyl('Blue dial',0.01865,0.0007,0.0242,dial)
ring('Inner chapter ring',0.0186,0.0179,0.02455,0.0251,steel)
for i in range(60):
    a = 2*math.pi*i/60
    major = i%5 == 0
    r = 0.01625 if major else 0.01715
    o = box('Applied hour index' if major else 'Minute marker',(r*math.sin(a),r*math.cos(a),0.0248),(0.00085 if major else 0.00022,0.0025 if major else 0.0007,0.0003),lume if major else polish,0.00007)
    o.rotation_euler.z = -a

def hand(name,angle,length,width,z,m,tail=0.0025):
    a = math.radians(angle)
    mid = (length-tail)*0.5
    o = box(name,(mid*math.sin(a),mid*math.cos(a),z),(width,length+tail,0.0003),m,0.00012)
    o.rotation_euler.z = -a
hand('Hour hand at ten',-60,0.0105,0.0012,0.02535,lume)
hand('Minute hand at two',60,0.0143,0.0008,0.02575,lume)
hand('Fine seconds hand',176,0.016,0.00022,0.02608,red,0.004)
cyl('Hand pinion',0.0011,0.0005,0.0261,polish)
cyl('Thin sapphire cover',0.01865,0.0006,0.0269,crystal)
# Crown axis points out of the case along X.
crown = cyl('Knurled winding crown',0.0027,0.0035,0.021,steel,(0.022,0))
crown.rotation_euler.y = math.pi/2
for i in range(32):
    a = 2*math.pi*i/32
    o = box('Crown knurl',(0.022,0.0027*math.cos(a),0.021+0.0027*math.sin(a)),(0.0030,0.00035,0.00035),polish,0.00008)
    o.rotation_euler.x = a

def label(name,body,size,loc,m):
    c = bpy.data.curves.new(name,'FONT')
    c.body = body
    c.size = size
    c.align_x = 'CENTER'
    c.align_y = 'CENTER'
    o = bpy.data.objects.new(name,c)
    scene.collection.objects.link(o)
    o.location = loc
    finish(o,name,m)
label('Dial signature','MERIDIAN',0.0022,(0,0.0078,0.0247),lume)
label('Dial small print','AUTOMATIC',0.0013,(0,-0.007,0.0247),lume)
box('Date aperture surround',(0.0109,0,0.02475),(0.0045,0.0035,0.0003),polish,0.00025)
box('Date wheel visible',(0.0109,0,0.02494),(0.0039,0.0029,0.00012),lume,0.0001)
label('Date numeral','18',0.0022,(0.0109,0,0.02502),dial)
box('Studio floor',(0,0,-0.004),(2,2,0.008),floor,0,False)
bpy.context.view_layer.update()
focus_pos = rig.matrix_world @ Vector((0,0,0.0255))

def aim(o,target):
    o.rotation_euler = (Vector(target)-o.location).to_track_quat('-Z','Y').to_euler()
def area(name,loc,energy,size,target):
    d = bpy.data.lights.new(name,'AREA')
    d.energy = energy
    d.shape = 'DISK'
    d.size = size
    o = bpy.data.objects.new(name,d)
    scene.collection.objects.link(o)
    o.location = loc
    aim(o,target)
area('Macro diffusion key',(-0.15,-0.12,0.28),9,0.22,focus_pos)
area('Bezel rim strip',(0.13,0.10,0.19),7,0.12,focus_pos)
area('Low fill',(-0.06,0.20,0.12),2,0.18,focus_pos)
bpy.ops.object.empty_add(location=focus_pos)
focus = bpy.context.object
focus.name = 'Focus on watch hands'
bpy.ops.object.camera_add(location=focus_pos+Vector((0.095,-0.16,0.24)))
cam = bpy.context.object
cam.name = '100mm macro camera'
cam.data.lens = 100
cam.data.clip_start = 0.005
cam.data.clip_end = 10
cam.data.dof.use_dof = True
cam.data.dof.focus_object = focus
cam.data.dof.aperture_fstop = 4
cam.data.dof.aperture_blades = 9
aim(cam,focus_pos)
scene.camera = cam
