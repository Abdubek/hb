import bpy, math
from mathutils import Vector
bpy.ops.object.select_all(action='SELECT'); bpy.ops.object.delete(use_global=False)

def mat(name,c,rough=.5,metal=0):
    m=bpy.data.materials.new(name); m.diffuse_color=(*c,1); m.use_nodes=True; p=m.node_tree.nodes.get('Principled BSDF'); p.inputs['Base Color'].default_value=(*c,1); p.inputs['Roughness'].default_value=rough; p.inputs['Metallic'].default_value=metal; return m

def box(name,loc,size,m,bevel=.02,parent=None):
    bpy.ops.mesh.primitive_cube_add(size=1,location=loc); o=bpy.context.object; o.name=name; o.dimensions=size; bpy.ops.object.transform_apply(location=False,rotation=False,scale=True); o.data.materials.append(m)
    if bevel:
        b=o.modifiers.new('Rounded edges','BEVEL'); b.width=bevel; b.segments=4; o.modifiers.new('Weighted normals','WEIGHTED_NORMAL')
    if parent: o.parent=parent
    return o

def cyl(name,loc,r,depth,m,parent=None):
    bpy.ops.mesh.primitive_cylinder_add(vertices=64,radius=r,depth=depth,location=loc); o=bpy.context.object; o.name=name; o.data.materials.append(m)
    b=o.modifiers.new('Machined edge','BEVEL'); b.width=.008; b.segments=3; o.modifiers.new('Weighted normals','WEIGHTED_NORMAL')
    if parent: o.parent=parent
    return o

def curve(name,points,r,m,parent=None,closed=False):
    c=bpy.data.curves.new(name,'CURVE'); c.dimensions='3D'; c.resolution_u=16; c.bevel_depth=r; c.bevel_resolution=3; s=c.splines.new('POLY'); s.points.add(len(points)-1)
    for p,co in zip(s.points,points): p.co=(*co,1)
    s.use_cyclic_u=closed; o=bpy.data.objects.new(name,c); bpy.context.collection.objects.link(o); o.data.materials.append(m)
    if parent: o.parent=parent
    return o

def root(name,loc,angle):
    o=bpy.data.objects.new(name,None); bpy.context.collection.objects.link(o); o.location=loc; o.rotation_euler.z=angle; return o

def area(name,loc,power,size,target):
    bpy.ops.object.light_add(type='AREA',location=loc); o=bpy.context.object; o.name=name; o.data.energy=power; o.data.size=size; o.rotation_euler=(Vector(target)-o.location).to_track_quat('-Z','Y').to_euler()

wood=mat('Natural desktop',(.52,.35,.2),.6); paper=mat('Warm page edges',(.85,.82,.7),.85); cover=mat('Forest green book cloth',(.075,.17,.13),.85); gold=mat('Gold foil and brass',(.61,.43,.16),.3,.75); black=mat('Black polymer',(.025,.031,.032),.4); silver=mat('Satin aluminum',(.48,.52,.53),.28,.85); rubber=mat('Camera leatherette',(.045,.05,.047),.83); optic=mat('Blue coated lens',(.035,.115,.16),.13,.62); coffee=mat('Amber spectacle frames',(.18,.07,.025),.26); ribbon=mat('Rust bookmark',(.5,.15,.055),.8)
# Procedural wood is generated entirely within the blend scene.
p=wood.node_tree.nodes.get('Principled BSDF'); nodes=wood.node_tree.nodes; links=wood.node_tree.links
tex=nodes.new('ShaderNodeTexNoise'); tex.inputs['Scale'].default_value=3; tex.inputs['Detail'].default_value=2
coord=nodes.new('ShaderNodeTexCoord'); mapping=nodes.new('ShaderNodeVectorMath'); mapping.operation='MULTIPLY'; mapping.inputs[1].default_value=(2,95,4); links.new(coord.outputs['Generated'],mapping.inputs[0]); links.new(mapping.outputs[0],tex.inputs['Vector'])
ramp=nodes.new('ShaderNodeValToRGB'); ramp.color_ramp.elements[0].position=.2; ramp.color_ramp.elements[0].color=(.28,.16,.075,1); ramp.color_ramp.elements[1].position=.8; ramp.color_ramp.elements[1].color=(.6,.43,.27,1); links.new(tex.outputs['Fac'],ramp.inputs[0]); links.new(ramp.outputs[0],p.inputs['Base Color'])
box('Solid wood desktop',(0,0,-.13),(12,10,.25),wood,.06)
# Notebook, subtly rotated, with individual page-edge lines and foil lettering.
book=root('Notebook assembly',(-1.28,.15,0),math.radians(-9))
box('Bottom hard cover',(0,0,.065),(2.55,3.62,.09),cover,.065,book)
box('Page block',(.035,0,.22),(2.43,3.48,.25),paper,.045,book)
for i in range(11):
    z=.115+i*.021
    box('Fore edge page line',(1.254,0,z),(.006,3.35,.003),gold,0,book)
    box('Foot page line',(.04,-1.744,z),(2.33,.004,.003),gold,0,book)
box('Top hard cover',(0,0,.39),(2.55,3.62,.1),cover,.065,book)
box('Rounded notebook spine',(-1.25,0,.25),(.15,3.58,.38),cover,.06,book)
box('Elastic closure',(1.01,0,.452),(.115,3.51,.025),black,.014,book)
box('Bookmark ribbon',(-.62,-1.94,.09),(.14,.48,.014),ribbon,.006,book)
for text,y,size in [('FIELD NOTES',.47,.225),('IDEAS / SKETCHES',.05,.095),('VOL. 01',-1.14,.09)]:
    c=bpy.data.curves.new(text,'FONT'); c.body=text; c.align_x='CENTER'; c.size=size; c.extrude=.0007; o=bpy.data.objects.new(text,c); bpy.context.collection.objects.link(o); o.parent=book; o.location=(0,y,.449); o.data.materials.append(gold)
# Pen lies in the gap between notebook and camera.
pen=root('Pen assembly',(.62,-.62,.105),math.radians(-13))
o=cyl('Pen barrel',(0,0,0),.072,2.12,black,pen); o.rotation_euler.x=math.pi/2
for y in [-.75,.73,.9]:
    o=cyl('Pen metal band',(0,y,0),.076,.035,gold,pen); o.rotation_euler.x=math.pi/2
bpy.ops.mesh.primitive_cone_add(vertices=48,radius1=.005,radius2=.071,depth=.32,location=(0,-1.22,0)); o=bpy.context.object; o.name='Pen conical nib'; o.rotation_euler.x=-math.pi/2; o.data.materials.append(silver); o.parent=pen
box('Pen pocket clip',(0,.52,.082),(.038,.65,.025),gold,.015,pen)
o=cyl('Pen click button',(0,1.12,0),.047,.12,silver,pen); o.rotation_euler.x=math.pi/2
# Eyeglasses with transparent lenses, rims, bridge, hinges and folded temples.
glass=mat('Clear optical glass',(.94,.98,1),.075); gp=glass.node_tree.nodes.get('Principled BSDF'); gp.inputs['Transmission Weight'].default_value=1; gp.inputs['IOR'].default_value=1.45
spec=root('Eyeglasses assembly',(1.22,1.78,.15),math.radians(8))
for x in [-.64,.64]:
    points=[]
    for i in range(96):
        a=math.tau*i/96; points.append((x+.53*math.cos(a),.4*math.sin(a),.1+.035*math.cos(a)))
    curve('Rounded acetate lens rim',points,.038,coffee,spec,True)
    o=cyl('Transparent spectacle lens',(x,0,.1),1,.024,glass,spec); o.scale=(.505,.375,1)
    outer=x+(-.55 if x<0 else .55)
    box('Metal hinge',(outer,0,.09),(.1,.085,.065),gold,.012,spec)
    sign=-1 if x<0 else 1
    curve('Folded spectacle temple',[(outer,0,.08),(outer,-.38,.015),(sign*.8,-.54,-.06),(-sign*.45,-.55,-.065),(-sign*.65,-.46,-.06)],.027,coffee,spec)
    box('Nose pad',(x+(.43 if x<0 else -.43),-.08,.05),(.055,.13,.07),coffee,.025,spec)
curve('Arched nose bridge',[(-.13,.07,.11),(-.08,.16,.13),(0,.185,.14),(.08,.16,.13),(.13,.07,.11)],.027,gold,spec)
# Compact camera rests on its back, so the lens faces the flat-lay camera.
camroot=root('Compact camera assembly',(2.35,-.72,0),math.radians(-12))
box('Camera metal body',(0,0,.38),(1.97,1.22,.65),silver,.14,camroot)
box('Camera leather front',(0,-.025,.72),(1.88,1.03,.075),rubber,.1,camroot)
box('Raised right hand grip',(.73,-.04,.79),(.35,.98,.23),black,.1,camroot)
for z,r,d,m in [(.79,.54,.1,silver),(.92,.49,.2,black),(1.06,.455,.1,silver),(1.16,.42,.16,black),(1.255,.365,.025,silver),(1.272,.325,.018,optic)]: cyl('Concentric camera lens',(-.16,-.06,z),r,d,m,camroot)
for i in range(48):
    a=math.tau*i/48
    o=box('Lens focus grip rib',(-.16+.492*math.cos(a),-.06+.492*math.sin(a),.94),(.022,.032,.13),black,.004,camroot); o.rotation_euler.z=a
cyl('Lens inner aperture',(-.16,-.06,1.284),.15,.008,black,camroot)
cyl('Lens central glass',(-.16,-.06,1.291),.105,.006,optic,camroot)
box('Viewfinder silver surround',(-.68,.36,.78),(.36,.23,.08),silver,.035,camroot)
box('Viewfinder glass',(-.68,.36,.827),(.27,.14,.025),optic,.022,camroot)
box('Flash window',(.32,.38,.78),(.35,.16,.04),paper,.02,camroot)
cyl('Shutter button',(.64,.54,.78),.095,.055,silver,camroot)
for x in [-.96,.96]:
    curve('Camera strap eyelet',[(x,-.32,.52),(x*1.08,-.32,.52),(x*1.08,-.1,.52),(x,-.1,.52)],.025,silver,camroot)
curve('Short wrist strap',[(.99,-.28,.45),(1.3,-.52,.13),(1.5,-1.15,.06),(1.2,-1.47,.045),(.84,-1.42,.045),(.87,-1.1,.05),(1.13,-.62,.11),(.99,-.15,.45)],.032,black,camroot)
area('Large window softbox',(-3,4,7),650,5,(0,0,0)); area('Soft fill',(4,-2,5),220,4,(0,0,0))
bpy.ops.object.camera_add(location=(0,0,12)); camera=bpy.context.object; camera.name='Exact top down flat lay'; camera.rotation_euler=(0,0,0); camera.data.type='ORTHO'; camera.data.ortho_scale=8.9; bpy.context.scene.camera=camera
scene=bpy.context.scene; scene.world.color=(.25,.25,.25); scene.render.engine='CYCLES'; scene.cycles.samples=96; scene.render.resolution_x=1500; scene.render.resolution_y=1200; scene.render.resolution_percentage=100; scene.view_settings.view_transform='AgX'
