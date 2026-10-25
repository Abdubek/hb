import bpy, math
from mathutils import Vector
bpy.ops.wm.read_factory_settings(use_empty=True)

def mat(name,color,metallic=0,roughness=0.65):
    m = bpy.data.materials.new(name)
    m.diffuse_color = (*color,1)
    m.use_nodes = True
    p = m.node_tree.nodes.get('Principled BSDF')
    p.inputs['Base Color'].default_value = (*color,1)
    p.inputs['Metallic'].default_value = metallic
    p.inputs['Roughness'].default_value = roughness
    return m

def box(name,loc,size,material,bevel=0):
    bpy.ops.mesh.primitive_cube_add(size=1,location=loc)
    o = bpy.context.object
    o.name = name
    o.dimensions = size
    bpy.ops.object.transform_apply(location=False,rotation=False,scale=True)
    o.data.materials.append(material)
    if bevel:
        b = o.modifiers.new('Edge rounding','BEVEL')
        b.width = bevel
        b.segments = 2
        o.modifiers.new('Weighted normals','WEIGHTED_NORMAL')
    return o

def paths(name,lines,radius,material):
    c = bpy.data.curves.new(name,'CURVE')
    c.dimensions = '3D'
    c.bevel_depth = radius
    c.bevel_resolution = 1
    for points in lines:
        s = c.splines.new('POLY')
        s.points.add(len(points)-1)
        for p,co in zip(s.points,points):
            p.co = (*co,1)
    o = bpy.data.objects.new(name,c)
    bpy.context.collection.objects.link(o)
    c.materials.append(material)
    return o

def pole(name,a,b,radius,material,vertices=20):
    a,b = Vector(a),Vector(b)
    bpy.ops.mesh.primitive_cylinder_add(vertices=vertices,radius=radius,depth=(b-a).length,location=(a+b)/2)
    o = bpy.context.object
    o.name = name
    o.rotation_euler = (b-a).to_track_quat('Z','Y').to_euler()
    o.data.materials.append(material)
    for p in o.data.polygons:
        p.use_smooth = True
    return o

blue = mat('Acrylic blue playing surface',(0.055,0.24,0.40),roughness=0.94)
green = mat('Green court runoffs',(0.095,0.28,0.205),roughness=0.95)
white = mat('White line paint and net tape',(0.93,0.93,0.84),roughness=0.83)
netmat = mat('Charcoal tennis mesh',(0.014,0.02,0.021),roughness=0.9)
steel = mat('Forest green coated posts',(0.035,0.10,0.075),0.6,0.43)
wire = mat('Fence wire',(0.14,0.20,0.17),0.65,0.5)
concrete = mat('Concrete curb',(0.43,0.44,0.40),roughness=0.9)
grass = mat('Surrounding landscape',(0.19,0.25,0.12),roughness=1)
brass = mat('Net tension hardware',(0.45,0.39,0.24),0.8,0.3)
box('Ground',(0,0,-0.22),(150,150,0.15),grass)
box('Court slab',(0,0,-0.10),(18.6,36.6,0.20),concrete,0.05)
box('Green runoff surface',(0,0,0.009),(18.3,36.3,0.018),green)
box('Doubles playing rectangle',(0,0,0.021),(10.97,23.77,0.014),blue)
# Regulation doubles, singles and service lines; length runs along Y.
line_z = 0.031
for x in (-5.485,5.485,-4.115,4.115):
    box('Doubles sideline' if abs(x)>5 else 'Singles sideline',(x,0,line_z),(0.05,23.77,0.004),white)
for y in (-11.885,11.885):
    box('Baseline',(0,y,line_z),(11.02,0.10,0.004),white)
    box('Baseline center mark',(0,y-math.copysign(0.10,y),line_z),(0.05,0.20,0.004),white)
for y in (-6.4,6.4):
    box('Service line',(0,y,line_z),(8.23,0.05,0.004),white)
box('Center service line',(0,0,line_z),(0.05,12.8,0.004),white)

net_half = 6.399
for x in (-net_half,net_half):
    pole('Tennis net post',(x,0,0.025),(x,0,1.15),0.055,steel)
    pole('Post socket flange',(x,0,0.02),(x,0,0.06),0.115,steel)
    bpy.ops.mesh.primitive_uv_sphere_add(segments=20,ring_count=10,radius=0.059,location=(x,0,1.15))
    bpy.context.object.name = 'Net post rounded cap'
    bpy.context.object.data.materials.append(steel)

def top(x):
    return 0.914+0.156*(abs(x)/net_half)**2

# The top tape follows a shallow sag; mesh is one efficient curve object.
lines = []
columns = 256
for i in range(columns+1):
    x = -net_half+2*net_half*i/columns
    lines.append([(x,0,0.06),(x,0,top(x)-0.025)])
for j in range(19):
    f = j/18
    lines.append([(-net_half+2*net_half*i/128,0,0.06+f*(top(-net_half+2*net_half*i/128)-0.085)) for i in range(129)])
paths('Fine tennis net mesh',lines,0.0015,netmat)
verts,faces = [],[]
for i in range(129):
    x = -net_half+2*net_half*i/128
    z = top(x)
    verts.extend([(x,-0.009,z),(x,-0.009,z-0.05)])
    if i:
        a = 2*(i-1)
        faces.append((a,a+2,a+3,a+1))
mesh = bpy.data.meshes.new('Sagging top band mesh')
mesh.from_pydata(verts,[],faces)
mesh.update()
o = bpy.data.objects.new('White woven top tape',mesh)
bpy.context.collection.objects.link(o)
o.data.materials.append(white)
s = o.modifiers.new('Tape thickness','SOLIDIFY')
s.thickness = 0.018
paths('Bottom net binding',[[(-net_half,0,0.06),(net_half,0,0.06)]],0.006,netmat)
box('Center hold-down strap',(0,-0.014,0.482),(0.045,0.032,0.914),white,0.003)
box('Center strap ground anchor',(0,0,0.043),(0.13,0.13,0.024),steel,0.01)
for x in (-net_half,net_half):
    paths('Net side binding',[[(x,0,0.06),(x,0,1.07)]],0.012,netmat)
pole('Tension winch spindle',(net_half,0,0.81),(net_half,0.15,0.81),0.025,brass)
paths('Winch crank',[[(net_half,0.16,0.81),(net_half,0.16,0.67),(net_half,0.24,0.67)]],0.012,brass)

# A 3 m high enclosure with regularly spaced perimeter posts and welded wire.
xedge,yedge,height = 8.9,17.9,3.0
segments = []
for side in (-1,1):
    for i in range(12):
        ya = -yedge + 2*yedge*i/12
        yb = -yedge + 2*yedge*(i+1)/12
        # Entry opening on the near long side.
        if side == 1 and i == 5:
            continue
        segments.append(((side*xedge,ya),(side*xedge,yb)))
    for i in range(6):
        xa = -xedge+2*xedge*i/6
        xb = -xedge+2*xedge*(i+1)/6
        segments.append(((xa,side*yedge),(xb,side*yedge)))
post_coords = set()
fence_lines = []
for a,b in segments:
    post_coords.add(a)
    post_coords.add(b)
    pole('Fence top rail',(*a,height),(*b,height),0.023,steel)
    pole('Fence lower rail',(*a,0.12),(*b,0.12),0.018,steel)
    length = math.dist(a,b)
    count = max(1,round(length/0.18))
    for i in range(1,count):
        f = i/count
        x,y = a[0]+(b[0]-a[0])*f,a[1]+(b[1]-a[1])*f
        fence_lines.append([(x,y,0.12),(x,y,height)])
    for j in range(1,17):
        z = 0.12+(height-0.12)*j/17
        fence_lines.append([(*a,z),(*b,z)])
for x,y in sorted(post_coords):
    pole('Perimeter fence post',(x,y,0.03),(x,y,height+0.055),0.047,steel)
    pole('Post cap',(x,y,height+0.025),(x,y,height+0.075),0.053,steel)
paths('Perimeter welded wire mesh',fence_lines,0.003,wire)
for x in (-9.2,9.2):
    box('Long perimeter curb',(x,0,0.025),(0.17,36.5,0.07),concrete,0.02)
for y in (-18.2,18.2):
    box('End perimeter curb',(0,y,0.025),(18.5,0.17,0.07),concrete,0.02)

world = bpy.data.worlds.new('Tennis court daylight')
world.use_nodes = True
world.node_tree.nodes['Background'].inputs[0].default_value = (0.64,0.76,0.93,1)
world.node_tree.nodes['Background'].inputs[1].default_value = 0.55
bpy.context.scene.world = world
bpy.ops.object.light_add(type='SUN',location=(0,0,20))
bpy.context.object.rotation_euler = (0.5,-0.4,-0.5)
bpy.context.object.data.energy = 2.3
bpy.context.object.data.angle = 0.15
bpy.ops.object.light_add(type='AREA',location=(0,-3,20))
bpy.context.object.data.energy = 2200
bpy.context.object.data.size = 15
bpy.ops.object.camera_add(location=(30,-39,37))
cam = bpy.context.object
cam.rotation_euler = (Vector((0,0,0))-cam.location).to_track_quat('-Z','Y').to_euler()
cam.data.type = 'ORTHO'
cam.data.ortho_scale = 48
scene = bpy.context.scene
scene.camera = cam
scene.render.engine = 'CYCLES'
scene.render.resolution_x = 1500
scene.render.resolution_y = 1500
scene.render.resolution_percentage = 100
scene.view_settings.view_transform = 'AgX'
