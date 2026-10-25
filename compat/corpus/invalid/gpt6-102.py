import bpy, math
from mathutils import Vector

bpy.ops.wm.read_factory_settings(use_empty=True)
scene = bpy.context.scene
scene.render.engine = 'CYCLES'
scene.cycles.samples = 128
scene.cycles.transmission_bounces = 12
scene.render.resolution_x = 1200
scene.render.resolution_y = 1600
scene.render.resolution_percentage = 100
scene.view_settings.view_transform = 'AgX'
scene.world.color = (0.07,0.07,0.07)

def mat(name, color, metallic=0, roughness=0.3):
    m = bpy.data.materials.new(name)
    m.diffuse_color = (*color,1)
    m.use_nodes = True
    p = m.node_tree.nodes.get('Principled BSDF')
    p.inputs['Base Color'].default_value = (*color,1)
    p.inputs['Metallic'].default_value = metallic
    p.inputs['Roughness'].default_value = roughness
    return m

glass = mat('Clear thick crystal glass', (0.97,0.99,1), 0, 0.065)
p = glass.node_tree.nodes.get('Principled BSDF')
p.inputs['Transmission Weight'].default_value = 1
p.inputs['IOR'].default_value = 1.46
liquid = mat('Pale amber eau de parfum', (1,0.82,0.48), 0, 0.08)
p = liquid.node_tree.nodes.get('Principled BSDF')
p.inputs['Transmission Weight'].default_value = 1
p.inputs['IOR'].default_value = 1.34
v = liquid.node_tree.nodes.new('ShaderNodeVolumeAbsorption')
v.inputs['Color'].default_value = (0.88,0.46,0.10,1)
v.inputs['Density'].default_value = 0.5
liquid.node_tree.links.new(v.outputs['Volume'], liquid.node_tree.nodes.get('Material Output').inputs['Volume'])
gold = mat('Champagne gold', (0.68,0.48,0.22), 0.85, 0.2)
capmat = mat('Obsidian lacquer', (0.018,0.012,0.018), 0.12, 0.17)
label = mat('Ivory cotton paper', (0.89,0.85,0.73), 0, 0.7)
ink = mat('Warm black lettering', (0.035,0.025,0.02), 0, 0.6)
stone = mat('Plum satin pedestal', (0.115,0.055,0.082), 0.1, 0.28)
bg = mat('Rose-grey backdrop', (0.23,0.15,0.18), 0, 0.65)

def assign(o,m):
    o.data.materials.append(m)
    return o

def box(name, location, scale, material, bevel=0):
    bpy.ops.mesh.primitive_cube_add(size=1, location=location)
    o = bpy.context.object
    o.name = name
    o.dimensions = scale
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    assign(o,material)
    if bevel:
        mod = o.modifiers.new('Soft machined edges','BEVEL')
        mod.width = bevel
        mod.segments = 5
        o.modifiers.new('Weighted normals','WEIGHTED_NORMAL')
    return o

def cyl(name, radius, depth, loc, material):
    bpy.ops.mesh.primitive_cylinder_add(vertices=96, radius=radius, depth=depth, location=loc)
    o = bpy.context.object
    o.name = name
    assign(o,material)
    for f in o.data.polygons:
        f.use_smooth = True
    b = o.modifiers.new('Edge highlights','BEVEL')
    b.width = 0.008
    b.segments = 3
    o.modifiers.new('Weighted normals','WEIGHTED_NORMAL')
    return o

box('Low presentation plinth', (0,0,0.12), (2.1,1.65,0.24), stone, 0.065)
# A continuous vessel mesh follows outer wall, neck opening and inner cavity.
def rounded_ring(hx,hy,r,z):
    pts = []
    for cx,cy,start in [(hx-r,hy-r,0),(-hx+r,hy-r,90),(-hx+r,-hy+r,180),(hx-r,-hy+r,270)]:
        for j in range(12):
            a = math.radians(start+90*j/12)
            pts.append((cx+r*math.cos(a),cy+r*math.sin(a),z))
    return pts
rings = [
    (0.54,0.285,0.10,0.25),(0.59,0.33,0.12,0.31),
    (0.59,0.33,0.12,1.64),(0.55,0.30,0.12,1.76),
    (0.22,0.20,0.18,1.89),(0.19,0.19,0.185,2.03),
    (0.135,0.135,0.13,2.03),(0.135,0.135,0.13,1.91),
    (0.49,0.245,0.10,1.70),(0.525,0.265,0.105,1.60),
    (0.525,0.265,0.105,0.43),(0.49,0.235,0.09,0.38)]
verts = [p for ring in rings for p in rounded_ring(*ring)]
N = 48
faces = [tuple(reversed(range(N)))]
for k in range(len(rings)-1):
    for j in range(N):
        a,b = k*N+j,k*N+(j+1)%N
        faces.append((a,b,b+N,a+N))
faces.append(tuple((len(rings)-1)*N+j for j in range(N)))
mesh = bpy.data.meshes.new('Closed thick-walled bottle mesh')
mesh.from_pydata(verts,[],faces)
mesh.update()
o = bpy.data.objects.new('Crystal bottle with real internal cavity',mesh)
scene.collection.objects.link(o)
assign(o,glass)
for p in mesh.polygons:
    p.use_smooth = len(p.vertices) == 4
box('Perfume fill with visible upper surface', (0,0,0.995), (1.038,0.518,1.19), liquid, 0.08)
cyl('Gold neck collar', 0.205, 0.16, (0,0,1.995), gold)
box('Heavy lacquer cap', (0,0,2.235), (0.64,0.56,0.39), capmat, 0.065)
box('Cap gold lower accent', (0,0,2.065), (0.605,0.525,0.025), gold, 0.016)
box('Paper front label', (0,-0.334,1.03), (0.80,0.009,0.80), label, 0.012)

def text(name, body, size, loc, material):
    c = bpy.data.curves.new(name,'FONT')
    c.body = body
    c.align_x = 'CENTER'
    c.align_y = 'CENTER'
    c.size = size
    c.extrude = 0.0003
    o = bpy.data.objects.new(name,c)
    scene.collection.objects.link(o)
    o.location = loc
    o.rotation_euler = (math.pi/2,0,0)
    assign(o,material)
text('House name', 'A U R E', 0.115, (0,-0.341,1.24), ink)
text('Fragrance name', 'No. 08', 0.105, (0,-0.341,1.045), ink)
text('Label description', 'EAU DE PARFUM', 0.042, (0,-0.341,0.865), ink)
text('Volume mark', '50 ml', 0.042, (0,-0.341,0.74), ink)
box('Label gold rule', (0,-0.342,1.135), (0.44,0.002,0.006), gold)

profile = [(-7,0),(2,0)]
for i in range(1,25):
    a = math.pi*0.5*i/24
    profile.append((2+1.5*math.sin(a),1.5-1.5*math.cos(a)))
profile.append((3.5,7))
verts = [(x,y,z) for y,z in profile for x in (-7,7)]
faces = [(2*i,2*i+1,2*i+3,2*i+2) for i in range(len(profile)-1)]
mesh = bpy.data.meshes.new('Seamless background')
mesh.from_pydata(verts,[],faces)
mesh.update()
o = bpy.data.objects.new('Rose-grey cyclorama',mesh)
scene.collection.objects.link(o)
assign(o,bg)
for p in mesh.polygons:
    p.use_smooth = True

def aim(o,target):
    o.rotation_euler = (Vector(target)-o.location).to_track_quat('-Z','Y').to_euler()
def area(name,loc,power,width,height,target,color):
    d = bpy.data.lights.new(name,'AREA')
    d.energy = power
    d.shape = 'RECTANGLE'
    d.size = width
    d.size_y = height
    d.color = color
    o = bpy.data.objects.new(name,d)
    scene.collection.objects.link(o)
    o.location = loc
    aim(o,target)
area('Softbox 01 - tall key', (-2.4,-2.6,3.4), 500, 1.5, 3.2, (0,0,1.25), (1,0.9,0.78))
area('Softbox 02 - gentle fill', (2.5,-1.0,2.6), 280, 1.3, 2.8, (0,0,1.2), (0.80,0.9,1))
area('Rear narrow rim light', (0.7,2.0,3.0), 650, 0.45, 2.6, (0,0,1.2), (1,0.78,0.55))
bpy.ops.object.camera_add(location=(2.7,-7.2,3.1))
cam = bpy.context.object
cam.name = 'Portrait perfume hero - 85mm'
cam.data.lens = 85
cam.data.sensor_fit = 'HORIZONTAL'
aim(cam,(0,0,1.28))
bpy.ops.object.empty_add(location=(0,-0.33,1.15))
focus = bpy.context.object
focus.name = 'Label focus'
cam.data.dof.use_dof = True
cam.data.dof.focus_object = focus
cam.data.dof.aperture_fstop = 8
scene.camera = cam
