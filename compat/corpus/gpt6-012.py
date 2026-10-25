import bpy, math
from mathutils import Vector

bpy.ops.object.select_all(action='SELECT'); bpy.ops.object.delete(use_global=False)

def mat(name,color,metal=0,rough=.4):
    m=bpy.data.materials.new(name); m.diffuse_color=(*color,1); m.use_nodes=True
    p=m.node_tree.nodes.get('Principled BSDF'); p.inputs['Base Color'].default_value=(*color,1); p.inputs['Metallic'].default_value=metal; p.inputs['Roughness'].default_value=rough
    return m

def box(name,loc,dims,m,bevel=.03):
    bpy.ops.mesh.primitive_cube_add(size=1,location=loc); o=bpy.context.object; o.name=name; o.dimensions=dims
    bpy.ops.object.transform_apply(location=False,rotation=False,scale=True); o.data.materials.append(m)
    if bevel:
        b=o.modifiers.new('Machined edge','BEVEL'); b.width=bevel; b.segments=3; o.modifiers.new('Weighted normals','WEIGHTED_NORMAL')
    return o

def cylinder(name,loc,r,d,m,front=False,n=64):
    bpy.ops.mesh.primitive_cylinder_add(vertices=n,radius=r,depth=d,location=loc); o=bpy.context.object; o.name=name; o.data.materials.append(m)
    if front: o.rotation_euler[0]=math.pi/2
    b=o.modifiers.new('Edge highlights','BEVEL'); b.width=.012; b.segments=2; o.modifiers.new('Weighted normals','WEIGHTED_NORMAL'); return o

def ring(name,loc,r,t,m,front=False):
    bpy.ops.mesh.primitive_torus_add(major_segments=64,minor_segments=8,location=loc,major_radius=r,minor_radius=t)
    o=bpy.context.object; o.name=name; o.data.materials.append(m)
    if front: o.rotation_euler[0]=math.pi/2
    return o

def label(name,text,loc,size,m,rot=(math.pi/2,0,0)):
    cu=bpy.data.curves.new(name,'FONT'); cu.body=text; cu.size=size; cu.align_x='CENTER'; cu.extrude=.0007
    o=bpy.data.objects.new(name,cu); bpy.context.collection.objects.link(o); o.location=loc; o.rotation_euler=rot; cu.materials.append(m)
    return o

black=mat('Black anodized alloy',(.027,.031,.036),.55,.32); rubber=mat('Grip rubber',(.016,.018,.019),0,.8)
silver=mat('Satin titanium',(.5,.53,.55),.82,.27); white=mat('Ivory engraving',(.85,.87,.82)); red=mat('Mount index red',(.8,.035,.012))
blue=mat('Coated optical glass',(.014,.09,.15),.5,.09); screen=mat('LCD glass',(.012,.026,.034),.35,.14); floor=mat('Studio surface',(.16,.19,.23))
# Fine procedural grain remains asset-free.
p=rubber.node_tree.nodes.get('Principled BSDF'); noise=rubber.node_tree.nodes.new('ShaderNodeTexNoise'); noise.inputs['Scale'].default_value=150
bump=rubber.node_tree.nodes.new('ShaderNodeBump'); bump.inputs['Strength'].default_value=.22; bump.inputs['Distance'].default_value=.025
rubber.node_tree.links.new(noise.outputs['Fac'],bump.inputs['Height']); rubber.node_tree.links.new(bump.outputs['Normal'],p.inputs['Normal'])
box('Camera chassis',(0,0,1.17),(3.4,1.22,1.96),black,.15)
box('Front leather wrap',(-.05,-.62,1.12),(3.1,.1,1.49),rubber,.07)
box('Deep right hand grip',(1.28,-.58,1.12),(.68,.7,1.82),rubber,.17)
box('Top plate',(0,0,2.13),(3.25,1.17,.18),silver,.06)
box('Bottom plate',(0,0,.21),(3.23,1.16,.13),silver,.045)
box('Viewfinder hump',(-.22,.05,2.32),(.92,.89,.47),black,.09)
box('Hot shoe plate',(-.22,.02,2.58),(.55,.56,.035),silver,.01)
for x in (-.45,.01): box('Hot shoe rail',(x,.02,2.62),(.06,.56,.08),black,.01)
box('Hot shoe contact',(-.22,.08,2.61),(.08,.09,.025),silver,.005)
box('Viewfinder eyecup',(-.22,.675,2.26),(.73,.18,.4),rubber,.07)
box('Viewfinder rear glass',(-.22,.776,2.26),(.51,.025,.25),blue,.025)
# Lens points toward negative Y.
cx=-.35; cz=1.16
for name,y,r,d,m in [('Mount flange',-.72,.85,.18,silver),('Mount collar',-.86,.79,.16,black),('Lens barrel',-1.25,.73,.66,black),('Zoom ring',-1.12,.758,.28,rubber),('Focus ring',-1.55,.716,.25,rubber),('Front barrel',-1.79,.7,.24,black)]:
    cylinder(name,(cx,y,cz),r,d,m,True)
for y,r in [(-.93,.758),(-1.31,.739),(-1.68,.701),(-1.915,.661)]: ring('Lens trim ring',(cx,y,cz),r,.018,silver,True)
for y,r in [(-1.12,.765),(-1.55,.724)]:
    for i in range(48):
        a=2*math.pi*i/48
        o=box('Raised focus grip',(cx+r*math.cos(a),y,cz+r*math.sin(a)),(.025,.22,.025),rubber,.005)
        o.rotation_euler[1]=-a
cylinder('Recessed optical element',(cx,-1.915,cz),.595,.025,blue,True)
ring('Inner optical retaining ring',(cx,-1.942,cz),.6,.032,black,True)
ring('Optical coating reflection',(cx,-1.934,cz),.43,.009,blue,True)
cylinder('Red lens alignment dot',(cx+.5,-.963,cz+.58),.039,.016,red,True,16)
label('Lens specification','35 / 1.8',(cx,-1.955,cz-.51),.09,white)
label('Body brand','NOVA',(-.22,-.409,2.31),.16,white)
for x,r in [(-1.18,.32),(.79,.27)]:
    cylinder('Top control dial',(x,.03,2.31),r,.22,black)
    cylinder('Dial top',(x,.03,2.429),r*.86,.02,silver)
    for i in range(24):
        a=i*2*math.pi/24
        box('Dial knurl',(x+r*math.cos(a),.03+r*math.sin(a),2.32),(.025,.025,.15),black,.004)
    for i in range(8):
        a=i*math.pi/4; o=box('Dial engraved tick',(x+r*.64*math.cos(a),.03+r*.64*math.sin(a),2.445),(.055,.013,.005),black,.002); o.rotation_euler[2]=a
cylinder('Shutter collar',(1.26,-.33,2.275),.195,.13,black)
cylinder('Shutter release',(1.26,-.33,2.355),.137,.045,silver)
cylinder('Record button',(1.31,.31,2.26),.09,.055,red)
box('Rear display surround',(-.32,.64,1.19),(2.08,.14,1.36),rubber,.06)
box('Rear display',(-.32,.72,1.19),(1.86,.023,1.14),screen,.025)
for z in (.78,1.14,1.51):
    o=cylinder('Rear function button',(1.05,.67,z),.087,.06,black,True,24)
for x in (-1.77,1.77):
    ring('Strap lug',(x,0,1.83),.105,.035,silver,True)
box('Ground',(0,0,.055),(200,200,.1),floor,0)
world=bpy.context.scene.world; world.use_nodes=True; world.node_tree.nodes['Background'].inputs[1].default_value=.35
for loc,energy,size in [((1,-5,7),850,4),((-4,-2,4),550,3),((3,4,5),900,3)]:
    bpy.ops.object.light_add(type='AREA',location=loc); o=bpy.context.object; o.data.energy=energy; o.data.size=size; o.rotation_euler=(Vector((0,-.3,1))-o.location).to_track_quat('-Z','Y').to_euler()
bpy.ops.object.camera_add(location=(5,-7,4.7)); cam=bpy.context.object; cam.rotation_euler=(Vector((0,-.4,1.3))-cam.location).to_track_quat('-Z','Y').to_euler(); cam.data.type='ORTHO'; cam.data.ortho_scale=5.9
scene=bpy.context.scene; scene.camera=cam; scene.render.engine='CYCLES'; scene.cycles.samples=64; scene.render.resolution_x=1200; scene.render.resolution_y=1000; scene.render.resolution_percentage=100
