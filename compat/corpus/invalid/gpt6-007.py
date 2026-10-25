import bpy, math
from mathutils import Vector
bpy.ops.wm.read_factory_settings(use_empty=True)

def mat(name, color, metal=0, rough=.5):
    m=bpy.data.materials.new(name); m.diffuse_color=(*color,1); m.use_nodes=True; p=m.node_tree.nodes.get('Principled BSDF'); p.inputs['Base Color'].default_value=(*color,1); p.inputs['Metallic'].default_value=metal; p.inputs['Roughness'].default_value=rough; return m

def box(name, loc, size, material, bevel=0):
    bpy.ops.mesh.primitive_cube_add(size=1,location=loc); o=bpy.context.object; o.name=name; o.dimensions=size; bpy.ops.object.transform_apply(location=False,rotation=False,scale=True); o.data.materials.append(material)
    if bevel:
        mod=o.modifiers.new('Rounded edges','BEVEL'); mod.width=bevel; mod.segments=3; o.modifiers.new('Weighted normals','WEIGHTED_NORMAL')
    return o

def cyl(name, loc, radius, depth, material, vertices=32):
    bpy.ops.mesh.primitive_cylinder_add(vertices=vertices,radius=radius,depth=depth,location=loc); o=bpy.context.object; o.name=name; o.data.materials.append(material)
    for p in o.data.polygons: p.use_smooth=True
    return o

def tube(name, points, radius, material):
    c=bpy.data.curves.new(name,'CURVE'); c.dimensions='3D'; c.resolution_u=1; c.bevel_depth=radius; c.bevel_resolution=4; c.use_fill_caps=True
    s=c.splines.new('POLY'); s.points.add(len(points)-1)
    for p,co in zip(s.points,points): p.co=(*co,1)
    o=bpy.data.objects.new(name,c); bpy.context.collection.objects.link(o); o.data.materials.append(material); return o

steel=mat('Brushed galvanized steel',(.49,.57,.61),.83,.3); bolts=mat('Stainless fasteners',(.7,.75,.77),.9,.22); rubber=mat('Black end caps',(.025,.032,.035),0,.8); concrete=mat('Concrete paving',(.40,.43,.43),0,.95); joint=mat('Paving joints',(.19,.21,.22),0,.95); yellow=mat('Parking bay paint',(.94,.65,.10),0,.72)
# Five individual upright wheel slots on a shared bolted base.
# Each slot has 110 mm clear spacing between its two vertical rails.
box('Pavement foundation',(0,-.2,-.105),(4.6,3.7,.2),joint,.035)
for i in range(8):
    for j in range(6): box('Paving slab',(-2.0+i*.57,-1.72+j*.60,.003),(.561,.591,.026),concrete,.008)
for y in [-.29,.29]:
    box('Rack crossbar',(0,y,.125),(3.4,.075,.075),steel,.009)
    for x in [-1.709,1.709]: box('Crossbar end cap',(x,y,.125),(.022,.073,.073),rubber,.006)
for x in [-1.46,1.46]:
    for y in [-.29,.29]:
        box('Anchor foot',(x,y,.054),(.26,.20,.06),steel,.012)
        for dx in [-.084,.084]:
            cyl('Anchor washer',(x+dx,y,.091),.025,.008,bolts)
            cyl('Hex anchor head',(x+dx,y,.104),.016,.019,bolts,6)
for i in range(5):
    x=(i-2)*.66
    # Rounded inverted U in the x-z plane, leaned slightly toward the rear.
    r=.075; zc=.69
    points=[(x-r,-.29,.16),(x-r,.16,zc)]
    for k in range(17):
        a=math.pi-k*math.pi/16; z=zc+r*math.sin(a)
        points.append((x+r*math.cos(a),.16+(z-zc)*.5,z))
    points.append((x+r,-.29,.16))
    tube('Wheel cradle %d'%(i+1),points,.020,steel)
    # A rear brace gives each wheel hoop a stable triangular side profile.
    for dx in [-r,r]:
        tube('Cradle rear support',[(x+dx,.29,.16),(x+dx,.18,.61)],.016,steel)
        cyl('Foot weld collar',(x+dx,-.29,.166),.027,.022,steel)
    # Shallow wheel channel with raised sides guides a single bicycle tire.
    box('Wheel guide channel',(x,-.11,.175),(.15,.61,.018),steel,.005)
    for dx in [-.07,.07]: box('Channel lip',(x+dx,-.11,.19),(.015,.61,.035),steel,.005)
    # Five short bay markings and readable numbers on the pavement.
    box('Bay center marker',(x,-1.15,.019),(.045,.56,.003),yellow,.009)
    bpy.ops.object.text_add(location=(x,-1.69,.022)); t=bpy.context.object; t.name='Parking bay number %d'%(i+1); t.data.body=str(i+1); t.data.align_x='CENTER'; t.data.size=.17; t.data.extrude=.0005; t.data.materials.append(yellow)
# Small manufacturer plate.
box('Rack badge',(0,-.337,.13),(.30,.012,.05),rubber,.007)
for x in [-.126,.126]:
    o=cyl('Badge rivet',(x,-.347,.13),.008,.009,bolts,16); o.rotation_euler.x=math.pi/2
world=bpy.context.scene.world; world.color=(.25,.25,.25)
for loc,power,size in [((1,-3,5),800,4),((-3,1,3),550,3),((3,4,4),650,3)]:
    bpy.ops.object.light_add(type='AREA',location=loc); o=bpy.context.object; o.data.energy=power; o.data.shape='DISK'; o.data.size=size; o.rotation_euler=(Vector((0,0,.35))-o.location).to_track_quat('-Z','Y').to_euler()
bpy.ops.object.camera_add(location=(4.4,-6.5,3.5)); cam=bpy.context.object; cam.rotation_euler=(Vector((0,-.35,.30))-cam.location).to_track_quat('-Z','Y').to_euler(); cam.data.type='ORTHO'; cam.data.ortho_scale=5.4
scene=bpy.context.scene; scene.camera=cam; scene.unit_settings.system='METRIC'; scene.render.resolution_x=1500; scene.render.resolution_y=1050; scene.render.resolution_percentage=100
