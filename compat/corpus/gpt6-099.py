import bpy, math
from mathutils import Vector

bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)

def mat(name,c,metal=0,rough=0.4):
    m=bpy.data.materials.new(name); m.diffuse_color=(*c,1); m.use_nodes=True
    p=m.node_tree.nodes.get('Principled BSDF'); p.inputs['Base Color'].default_value=(*c,1)
    p.inputs['Metallic'].default_value=metal; p.inputs['Roughness'].default_value=rough
    return m

def box(name,loc,dim,m,b=0.01):
    bpy.ops.mesh.primitive_cube_add(size=1,location=loc)
    o=bpy.context.object; o.name=name; o.dimensions=dim
    bpy.ops.object.transform_apply(location=False,rotation=False,scale=True)
    o.data.materials.append(m)
    if b:
        mod=o.modifiers.new('Soft edges','BEVEL'); mod.width=b; mod.segments=3
        o.modifiers.new('Weighted normals','WEIGHTED_NORMAL')
    return o

def cyl(name,loc,r,d,m,axis=(0,0,1)):
    bpy.ops.mesh.primitive_cylinder_add(vertices=40,radius=r,depth=d,location=loc)
    o=bpy.context.object; o.name=name; o.data.materials.append(m)
    o.rotation_euler=Vector(axis).to_track_quat('Z','Y').to_euler()
    mod=o.modifiers.new('Edge bevel','BEVEL'); mod.width=min(0.004,d*0.15); mod.segments=3
    o.modifiers.new('Weighted normals','WEIGHTED_NORMAL')
    for p in o.data.polygons: p.use_smooth=True
    return o

def beam(name,a,b,width,m):
    a=Vector(a); b=Vector(b)
    o=box(name,(a+b)/2,(width,width,(b-a).length),m,0.006)
    o.rotation_euler=(b-a).to_track_quat('Z','Y').to_euler()
    return o

def curve(name,pts,r,m):
    c=bpy.data.curves.new(name,'CURVE'); c.dimensions='3D'; c.bevel_depth=r; c.bevel_resolution=3
    s=c.splines.new('POLY'); s.points.add(len(pts)-1)
    for p,co in zip(s.points,pts): p.co=(*co,1)
    o=bpy.data.objects.new(name,c); bpy.context.collection.objects.link(o); o.data.materials.append(m)
    return o

def profile(r,bottom,shoulder):
    pts=[(-r,bottom),(r,bottom),(r,shoulder)]
    for i in range(1,41):
        a=math.pi*i/40
        pts.append((r*math.cos(a),shoulder+r*math.sin(a)))
    return pts

def extruded_profile(name,pts,y1,y2,m):
    n=len(pts); verts=[(x,y,z) for y in (y1,y2) for x,z in pts]
    faces=[tuple(range(n)),tuple(range(2*n-1,n-1,-1))]
    for i in range(n):
        j=(i+1)%n; faces.append((i,i+n,j+n,j))
    mesh=bpy.data.meshes.new(name); mesh.from_pydata(verts,[],faces); mesh.update()
    o=bpy.data.objects.new(name,mesh); bpy.context.collection.objects.link(o); o.data.materials.append(m)
    mod=o.modifiers.new('Rolled edge','BEVEL'); mod.width=0.004; mod.segments=3
    o.modifiers.new('Weighted normals','WEIGHTED_NORMAL')
    return o

navy=mat('Blue enamel',(0.035,0.11,0.19),0.55,0.3)
red=mat('Signal red flag',(0.77,0.035,0.027),0.35,0.28)
steel=mat('Galvanized metal',(0.48,0.55,0.60),0.85,0.32)
black=mat('Shadow seams',(0.018,0.025,0.03),0,0.65)
wood=mat('Warm cedar',(0.35,0.18,0.075),0,0.72)
white=mat('Ivory lettering',(0.93,0.9,0.75),0,0.45)
soil=mat('Earth',(0.17,0.13,0.075),0,0.95)
grass=mat('Grass',(0.19,0.27,0.095),0,0.9)
# Procedural wood grain needs no image assets.
nt=wood.node_tree; p=nt.nodes.get('Principled BSDF')
tex=nt.nodes.new('ShaderNodeTexNoise'); tex.inputs['Scale'].default_value=4; tex.inputs['Detail'].default_value=3
coord=nt.nodes.new('ShaderNodeTexCoord'); mapping=nt.nodes.new('ShaderNodeVectorMath'); mapping.operation='MULTIPLY'; mapping.inputs[1].default_value=(7,7,0.45)
nt.links.new(coord.outputs['Generated'],mapping.inputs[0]); nt.links.new(mapping.outputs['Vector'],tex.inputs['Vector'])
ramp=nt.nodes.new('ShaderNodeValToRGB'); ramp.color_ramp.elements[0].color=(0.13,0.055,0.02,1); ramp.color_ramp.elements[1].color=(0.48,0.28,0.12,1)
nt.links.new(tex.outputs['Fac'],ramp.inputs[0]); nt.links.new(ramp.outputs[0],p.inputs['Base Color'])

box('Cedar post',(0,0.19,0.66),(0.145,0.145,1.32),wood,0.008)
box('Mailbox support arm',(0,0.01,1.25),(0.18,1.04,0.105),wood,0.008)
beam('Diagonal timber brace',(0,0.18,0.88),(0,-0.31,1.20),0.08,wood)
box('Mounting plate',(0,0,1.32),(0.43,0.82,0.025),steel,0.005)
for y in (-0.28,0.28):
    for x in (-0.16,0.16): cyl('Mounting bolt',(x,y,1.337),0.014,0.012,steel)
# Hollow arched shell with rolled front and rear edges.
outer=profile(0.245,1.34,1.58)
inner=profile(0.232,1.353,1.58)
n=len(outer); verts=[]
for y in (-0.46,0.46):
    for pts in (outer,inner): verts.extend((x,y,z) for x,z in pts)
faces=[]
for i in range(n):
    j=(i+1)%n
    faces.extend([(i,i+2*n,j+2*n,j),(i+n,j+n,j+3*n,i+3*n),(i,j,j+n,i+n),(i+2*n,i+3*n,j+3*n,j+2*n)])
mesh=bpy.data.meshes.new('Arched sheet metal mesh'); mesh.from_pydata(verts,[],faces); mesh.update()
o=bpy.data.objects.new('Hollow mailbox body',mesh); bpy.context.collection.objects.link(o); o.data.materials.append(navy)
for f in mesh.polygons: f.use_smooth=(f.index%4 in (0,1) and f.index//4>1)
o.modifiers.new('Weighted normals','WEIGHTED_NORMAL')
extruded_profile('Sealed rear panel',inner,0.443,0.461,navy)
extruded_profile('Door perimeter gasket',profile(0.246,1.338,1.58),-0.477,-0.465,black)
extruded_profile('Front drop-down door',profile(0.239,1.345,1.579),-0.493,-0.476,navy)
for y in (-0.458,0.452):
    pts=[(x,y,z) for x,z in outer]; pts.append(pts[0])
    curve('Rolled body seam',pts,0.005,steel)
pts=[(x,-0.496,z) for x,z in profile(0.221,1.362,1.579)]; pts.append(pts[0])
curve('Embossed door border',pts,0.003,steel)
for x in (-0.15,0.15):
    cyl('Door hinge barrel',(x,-0.482,1.346),0.017,0.093,steel,(1,0,0))
    box('Hinge leaf',(x,-0.501,1.372),(0.071,0.008,0.033),steel,0.004)
box('Top latch clip',(0,-0.468,1.83),(0.05,0.08,0.018),steel,0.004)
box('Door pull tab',(0,-0.523,1.782),(0.072,0.066,0.025),steel,0.007)
# Upright flag mounted on the right side, visible from the camera.
cyl('Flag pivot washer',(0.256,0.08,1.51),0.041,0.02,steel,(1,0,0))
box('Raised flag arm',(0.274,0.08,1.78),(0.021,0.035,0.54),red,0.007)
box('Rectangular signal flag',(0.274,-0.025,2.013),(0.023,0.24,0.15),red,0.009)
cyl('Flag pivot bolt',(0.291,0.08,1.51),0.017,0.025,steel,(1,0,0))
for y in (-0.34,0.34): cyl('Body rivet',(0.249,y,1.43),0.009,0.008,steel,(1,0,0))
box('Address plaque',(0,-0.505,1.555),(0.30,0.012,0.10),white,0.008)
bpy.ops.object.text_add(location=(0,-0.513,1.526),rotation=(math.pi/2,0,0))
o=bpy.context.object; o.name='House number 248'; o.data.body='248'; o.data.align_x='CENTER'; o.data.size=0.083; o.data.extrude=0.0005; o.data.materials.append(navy)
bpy.ops.object.text_add(location=(0,-0.503,1.663),rotation=(math.pi/2,0,0))
o=bpy.context.object; o.name='Mail lettering'; o.data.body='U.S. MAIL'; o.data.align_x='CENTER'; o.data.size=0.033; o.data.extrude=0.0003; o.data.materials.append(white)
cyl('Soil at post base',(0,0.19,0.005),0.28,0.025,soil)
box('Ground',(0,0,-0.033),(200,200,0.06),grass,0)

world=bpy.context.scene.world; world.use_nodes=True
world.node_tree.nodes['Background'].inputs[0].default_value=(0.45,0.58,0.72,1); world.node_tree.nodes['Background'].inputs[1].default_value=0.5
bpy.ops.object.light_add(type='SUN',location=(0,0,5))
o=bpy.context.object; o.rotation_euler=(0.45,-0.5,-0.5); o.data.energy=2; o.data.angle=0.15
bpy.ops.object.light_add(type='AREA',location=(2,-4,5))
o=bpy.context.object; o.data.energy=350; o.data.size=4; o.rotation_euler=(Vector((0,0,1))-o.location).to_track_quat('-Z','Y').to_euler()
bpy.ops.object.camera_add(location=(3,-4.5,2.8))
cam=bpy.context.object; cam.rotation_euler=(Vector((0,0,1.05))-cam.location).to_track_quat('-Z','Y').to_euler()
cam.data.type='ORTHO'; cam.data.ortho_scale=2.65
scene=bpy.context.scene; scene.camera=cam; scene.render.engine='CYCLES'; scene.cycles.samples=64
scene.render.resolution_x=1100; scene.render.resolution_y=1200; scene.render.resolution_percentage=100
