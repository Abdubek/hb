import bpy, math
from mathutils import Vector
bpy.ops.wm.read_factory_settings(use_empty=True)

def mat(name,c,metal=0,rough=.45):
    m=bpy.data.materials.new(name); m.diffuse_color=(*c,1); m.use_nodes=True
    p=m.node_tree.nodes.get('Principled BSDF'); p.inputs['Base Color'].default_value=(*c,1)
    p.inputs['Metallic'].default_value=metal; p.inputs['Roughness'].default_value=rough
    return m
wood=mat('Walnut cabinet',(.21,.085,.035),0,.4)
baffle=mat('Charcoal front baffle',(.042,.05,.055),0,.63)
rubber=mat('Rubber surrounds',(.014,.018,.022),0,.83)
cone=mat('Graphite paper cones',(.09,.105,.115),.1,.7)
metal=mat('Brushed aluminum trim',(.34,.38,.41),.8,.3)
black=mat('Black fasteners',(.018,.022,.025),.65)
label=mat('Brand plate',(.67,.64,.54),.65)
floor=mat('Desktop',(.29,.32,.34),0,.75)

def box(name,loc,size,ma,bevel=.015):
    bpy.ops.mesh.primitive_cube_add(size=1,location=loc); o=bpy.context.object; o.name=name; o.dimensions=size
    bpy.ops.object.transform_apply(location=False,rotation=False,scale=True); o.data.materials.append(ma)
    if bevel:
        b=o.modifiers.new('Edge bevel','BEVEL'); b.width=bevel; b.segments=3
        o.modifiers.new('Weighted normals','WEIGHTED_NORMAL')
    return o

def disc(name,x,y,z,r,depth,ma):
    bpy.ops.mesh.primitive_cylinder_add(vertices=64,radius=r,depth=depth,location=(x,y,z),rotation=(math.pi/2,0,0))
    o=bpy.context.object; o.name=name; o.data.materials.append(ma)
    b=o.modifiers.new('Fine edge bevel','BEVEL'); b.width=.003; b.segments=2
    o.modifiers.new('Weighted normals','WEIGHTED_NORMAL'); return o

def ring(name,z,r,tube,y,ma):
    bpy.ops.mesh.primitive_torus_add(major_segments=64,minor_segments=12,location=(0,y,z),rotation=(math.pi/2,0,0),major_radius=r,minor_radius=tube)
    o=bpy.context.object; o.name=name; o.data.materials.append(ma)
    for p in o.data.polygons: p.use_smooth=True

# Cabinet front faces -Y. Use separate enclosure walls and a thick inset baffle.
box('Left walnut wall',(-.345,0,.62),(.05,.56,1.14),wood)
box('Right walnut wall',(.345,0,.62),(.05,.56,1.14),wood)
box('Walnut top',(0,0,1.165),(.69,.56,.05),wood)
box('Walnut bottom',(0,0,.075),(.69,.56,.05),wood)
box('Rear panel',(0,.257,.62),(.64,.045,1.05),baffle,.009)
box('Inset front baffle',(0,-.24,.62),(.64,.065,1.05),baffle,.014)
for x in (-.255,.255):
    for y in (-.19,.19): box('Isolation foot',(x,y,.032),(.12,.12,.055),rubber,.018)

# Drivers are lathed radial profiles, with visible cone slope, surrounds and domes.
def driver(name,z,r):
    disc(name+' mounting flange',0,-.288,z,r,.033,black)
    ring(name+' trim',z,r*.945,r*.027,-.311,metal)
    # Cone remains in front of the baffle, recessed behind its projecting surround.
    profile=[(r*.12,-.303),(r*.23,-.307),(r*.37,-.319),(r*.64,-.342),(r*.77,-.358)]
    seg=64; verts=[]
    for radius,y in profile:
        for i in range(seg):
            a=2*math.pi*i/seg; verts.append((radius*math.cos(a),y,z+radius*math.sin(a)))
    faces=[]
    for j in range(len(profile)-1):
        for i in range(seg):
            ni=(i+1)%seg; faces.append((j*seg+i,j*seg+ni,(j+1)*seg+ni,(j+1)*seg+i))
    mesh=bpy.data.meshes.new(name+' cone mesh'); mesh.from_pydata(verts,[],faces); mesh.update()
    o=bpy.data.objects.new(name+' cone',mesh); bpy.context.collection.objects.link(o); o.data.materials.append(cone)
    for p in mesh.polygons:p.use_smooth=True
    ring(name+' rolled surround',z,r*.81,r*.074,-.347,rubber)
    bpy.ops.mesh.primitive_uv_sphere_add(segments=40,ring_count=20,radius=1,location=(0,-.316,z))
    o=bpy.context.object; o.name=name+' dust dome'; o.scale=(r*.285,r*.17,r*.285); o.data.materials.append(rubber)
    for p in o.data.polygons:p.use_smooth=True
    for k in range(4):
        a=math.pi/4+k*math.pi/2; x=r*.89*math.cos(a); zz=z+r*.89*math.sin(a)
        disc(name+' mounting screw',x,-.327,zz,r*.037,.009,metal)
        box(name+' screw slot',(x,-.333,zz),(r*.042,.003,r*.009),black,.0005)

driver('Woofer',.43,.257)
driver('Tweeter',.935,.137)
box('Small maker badge',(0,-.28,.754),(.15,.01,.037),label,.006)
cu=bpy.data.curves.new('Badge lettering','FONT'); cu.body='SONA'; cu.align_x='CENTER'; cu.align_y='CENTER'; cu.size=.023; cu.extrude=.0002
ob=bpy.data.objects.new('Badge lettering',cu); bpy.context.collection.objects.link(ob); ob.location=(0,-.287,.754); ob.rotation_euler=(math.pi/2,0,0); cu.materials.append(black)
# Rear connector plate and terminals complete the enclosure.
box('Rear connector plate',(0,.285,.30),(.25,.018,.19),black,.012)
for x in (-.065,.065): disc('Binding post',x,.31,.30,.022,.045,metal)
box('Desktop',(0,0,-.026),(200,200,.05),floor,0)
world=bpy.data.worlds.new('World'); bpy.context.scene.world=world; world.use_nodes=True; world.node_tree.nodes['Background'].inputs[1].default_value=.3
for loc,power,size in [((-2,-3,4),500,3),((2,1,3),450,2)]:
    bpy.ops.object.light_add(type='AREA',location=loc); o=bpy.context.object; o.data.energy=power; o.data.size=size
    o.rotation_euler=(Vector((0,0,.6))-o.location).to_track_quat('-Z','Y').to_euler()
bpy.ops.object.camera_add(location=(1.65,-2.9,1.6)); cam=bpy.context.object
cam.rotation_euler=(Vector((0,0,.60))-cam.location).to_track_quat('-Z','Y').to_euler(); cam.data.type='ORTHO'; cam.data.ortho_scale=1.75
scene=bpy.context.scene; scene.camera=cam; scene.render.engine='CYCLES'
scene.render.resolution_x=1100; scene.render.resolution_y=1400; scene.render.resolution_percentage=100
