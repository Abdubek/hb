import bpy, math, random
from mathutils import Vector
bpy.ops.wm.read_factory_settings(use_empty=True)
random.seed(8)

def mat(name,c,metal=0,rough=0.45):
    m=bpy.data.materials.new(name); m.diffuse_color=(*c,1); m.use_nodes=True; p=m.node_tree.nodes.get('Principled BSDF'); p.inputs['Base Color'].default_value=(*c,1); p.inputs['Metallic'].default_value=metal; p.inputs['Roughness'].default_value=rough; return m

def box(name,loc,size,m,bevel=0.025):
    bpy.ops.mesh.primitive_cube_add(size=1,location=loc); o=bpy.context.object; o.name=name; o.dimensions=size; bpy.ops.object.transform_apply(location=False,rotation=False,scale=True); o.data.materials.append(m)
    if bevel:
        b=o.modifiers.new('Soft edges','BEVEL'); b.width=bevel; b.segments=4; o.modifiers.new('Weighted normals','WEIGHTED_NORMAL')
    return o

def rod(name,a,b,r,m,vertices=32):
    d=Vector(b)-Vector(a); bpy.ops.mesh.primitive_cylinder_add(vertices=vertices,radius=r,depth=d.length,location=(Vector(a)+Vector(b))/2); o=bpy.context.object; o.name=name; o.rotation_euler=d.to_track_quat('Z','Y').to_euler(); o.data.materials.append(m)
    for p in o.data.polygons: p.use_smooth=True
    return o

def text(body,loc,size,m):
    cu=bpy.data.curves.new(body,'FONT'); cu.body=body; cu.align_x='CENTER'; cu.align_y='CENTER'; cu.size=size; cu.extrude=0.009; cu.bevel_depth=0.002
    o=bpy.data.objects.new(body,cu); bpy.context.collection.objects.link(o); o.location=loc; o.rotation_euler=(math.pi/2,0,0); o.data.materials.append(m); return o

walnut=mat('Walnut',(0.24,0.115,0.055)); stone=mat('Ivory travertine',(0.78,0.72,0.60),rough=0.40); brass=mat('Champagne brass',(0.63,0.46,0.24),0.78,0.27); wall=mat('Plaster',(0.74,0.72,0.65),rough=0.85); green=mat('Deep green upholstery',(0.09,0.23,0.19),rough=0.88); black=mat('Dark hardware',(0.023,0.028,0.027),0.3); rug=mat('Oatmeal rug',(0.54,0.48,0.37),rough=0.96); paper=mat('Cream paper',(0.91,0.86,0.73)); foliage=mat('Leaves',(0.11,0.27,0.085),rough=0.7); soil=mat('Soil',(0.055,0.032,0.017)); screen=mat('Screen glass',(0.025,0.055,0.065),0.25,0.15)
# Stone with subtle procedural variation.
ns=stone.node_tree.nodes; links=stone.node_tree.links; n=ns.new('ShaderNodeTexNoise'); n.inputs['Scale'].default_value=6; n.inputs['Detail'].default_value=3
r=ns.new('ShaderNodeValToRGB'); r.color_ramp.elements[0].color=(0.52,0.46,0.35,1); r.color_ramp.elements[1].color=(0.85,0.80,0.69,1); links.new(n.outputs['Fac'],r.inputs[0]); links.new(r.outputs[0],ns['Principled BSDF'].inputs['Base Color'])
box('Lobby floor',(0,0,-0.075),(12,10,0.15),stone,0)
box('Rear wall',(0,2.1,1.9),(10,0.16,3.8),wall,0)
box('Left return wall',(-5,0.2,1.9),(0.14,4,3.8),wall,0)
box('Wall skirting',(0,1.994,0.085),(10,0.045,0.17),walnut,0.006)
# Feature panel and repeated vertical battens.
box('Reception feature panel',(-1.05,1.985,2.05),(4.7,0.065,3.23),walnut,0.014)
for i in range(48): box('Feature wall slat',(-3.34+i*0.098,1.925,2.05),(0.042,0.065,3.18),walnut,0.008)
box('Sign backing',(-1.05,1.852,2.62),(3.20,0.055,1.12),green,0.04)
text('THE  ALDER',(-1.05,1.809,2.74),0.37,brass)
text('H O T E L   &   S U I T E S',(-1.05,1.807,2.39),0.104,paper)
# Guest-facing desk with raised counter and lower staff work surface.
box('Desk recessed plinth',(-1.05,0,0.105),(3.40,1.03,0.21),black,0.05)
box('Desk body',(-1.05,0,0.65),(3.62,1.13,1.04),walnut,0.075)
for i in range(47): box('Desk front flute',(-2.80+i*0.075,-0.580,0.66),(0.035,0.045,0.92),walnut,0.015)
box('Desk brass toe trim',(-1.05,-0.587,0.19),(3.44,0.026,0.044),brass,0.01)
box('Reception countertop',(-1.05,-0.10,1.21),(3.83,1.12,0.12),stone,0.055)
box('Staff worktop',(-1.05,0.73,0.82),(3.31,0.59,0.07),walnut)
for x in [-2.52,0.42]: box('Staff support cabinet',(x,0.73,0.44),(0.43,0.53,0.71),walnut)
text('RECEPTION',(-1.05,-0.622,0.76),0.19,brass)
# Monitor faces staff, its narrow back visible from the guest side.
box('Monitor foot',(-1.50,0.71,0.877),(0.32,0.20,0.035),black)
rod('Monitor stand',(-1.50,0.71,0.89),(-1.50,0.71,1.12),0.035,black)
box('Monitor',(-1.50,0.73,1.28),(0.65,0.065,0.40),black,0.02)
box('Monitor display',(-1.50,0.768,1.28),(0.60,0.008,0.35),screen,0.006)
box('Keyboard',(-1.50,1.0,0.869),(0.52,0.18,0.025),black,0.008)
for row in range(4):
    for col in range(12): box('Keyboard key',(-1.735+col*0.042,0.943+row*0.037,0.886),(0.032,0.027,0.009),wall,0.003)
# Bell, brochure holder and a small guest sign.
rod('Bell base',(-0.26,-0.31,1.276),(-0.26,-0.31,1.30),0.092,black)
bpy.ops.mesh.primitive_uv_sphere_add(segments=32,ring_count=16,radius=1,location=(-0.26,-0.31,1.30)); bell=bpy.context.object; bell.name='Service bell dome'; bell.scale=(0.079,0.079,0.057); bell.data.materials.append(brass)
for p in bell.data.polygons: p.use_smooth=True
rod('Bell button',(-0.26,-0.31,1.346),(-0.26,-0.31,1.375),0.018,brass)
box('Guest sign frame',(-2.40,-0.15,1.43),(0.40,0.065,0.30),brass,0.012)
box('Guest sign face',(-2.40,-0.19,1.43),(0.365,0.012,0.264),green,0.008)
text('WELCOME',(-2.40,-0.2,1.44),0.064,paper)
box('Brochure holder',(0.28,0.02,1.34),(0.25,0.18,0.14),brass,0.012)
for i in range(4): box('Brochure',(0.28,0.025+i*0.023,1.46),(0.21,0.014,0.29),paper,0.003)
# Lounge grouping on a woven rug.
box('Lounge rug',(2.65,-0.30,0.014),(3.35,3.05,0.028),rug,0.06)
for x in [1.12,4.18]: box('Rug border',(x,-0.30,0.031),(0.024,2.81,0.004),paper,0.001)
# Chair local coordinates let both chairs angle toward the coffee table.
def chair(name,cx,cy,angle):
    a=math.radians(angle)
    def point(x,y,z): return (cx+x*math.cos(a)-y*math.sin(a),cy+x*math.sin(a)+y*math.cos(a),z)
    def part(label,loc,size,m,b):
        ob=box(name+' '+label,point(*loc),size,m,b); ob.rotation_euler.z=a; return ob
    for x in [-0.34,0.34]:
        for y in [-0.33,0.33]: rod(name+' tapered-look leg',point(x*1.12,y*1.12,0.05),point(x,y,0.37),0.026,brass)
    part('base',(0,0,0.37),(0.87,0.87,0.16),green,0.08)
    part('seat cushion',(0,-0.045,0.49),(0.69,0.69,0.17),green,0.075)
    back=part('back cushion',(0,0.34,0.78),(0.87,0.20,0.66),green,0.095); back.rotation_euler.x=math.radians(-7)
    for x in [-0.40,0.40]: part('arm',(x,0.015,0.65),(0.17,0.80,0.36),green,0.08)
chair('Lounge chair A',2.04,0.60,16)
chair('Lounge chair B',3.76,-0.20,72)
rod('Coffee table pedestal',(2.60,-0.64,0.08),(2.60,-0.64,0.47),0.073,brass)
rod('Coffee table base',(2.60,-0.64,0.04),(2.60,-0.64,0.085),0.31,black)
rod('Round stone coffee table',(2.60,-0.64,0.46),(2.60,-0.64,0.52),0.52,stone,64)
book=box('Travel book',(2.55,-0.69,0.542),(0.34,0.24,0.037),green,0.005); book.rotation_euler.z=0.20
box('Book pages',(2.55,-0.69,0.544),(0.315,0.223,0.022),paper,0.002).rotation_euler.z=0.20
# Tall potted plant occupies the rear lounge corner.
rod('Planter foot',(3.80,1.40,0.03),(3.80,1.40,0.10),0.24,brass)
bpy.ops.mesh.primitive_cone_add(vertices=48,radius1=0.23,radius2=0.32,depth=0.55,location=(3.80,1.40,0.36)); bpy.context.object.name='Ceramic planter'; bpy.context.object.data.materials.append(stone)
rod('Visible pot soil',(3.80,1.40,0.63),(3.80,1.40,0.642),0.294,soil)
for i in range(14):
    a=i*2.399; h=1.10+random.random()*1.10; reach=0.25+random.random()*0.35
    start=Vector((3.80,1.40,0.63)); end=Vector((3.80+math.cos(a)*reach,1.40+math.sin(a)*reach,h))
    rod('Plant stem',start,end,0.012,walnut,12)
    direction=Vector((math.cos(a)*0.28,math.sin(a)*0.28,0.19)); center=end+direction*0.4
    bpy.ops.mesh.primitive_uv_sphere_add(segments=16,ring_count=8,radius=1,location=center); leaf=bpy.context.object; leaf.name='Leaf'; leaf.scale=(0.13,0.025,0.32); leaf.rotation_euler=direction.to_track_quat('Z','Y').to_euler(); leaf.data.materials.append(foliage)
    for p in leaf.data.polygons: p.use_smooth=True
# Suspended warm pendants above the desk.
glow=mat('Pendant diffuser',(0.98,0.85,0.60)); p=glow.node_tree.nodes['Principled BSDF']; p.inputs['Emission Color'].default_value=(1,0.78,0.48,1); p.inputs['Emission Strength'].default_value=3
for x in [-2.30,0.20]:
    rod('Pendant suspension',(x,-0.05,2.80),(x,-0.05,3.75),0.012,black)
    bpy.ops.mesh.primitive_cone_add(vertices=48,radius1=0.28,radius2=0.10,depth=0.20,location=(x,-0.05,2.73)); bpy.context.object.name='Brass pendant shade'; bpy.context.object.data.materials.append(brass)
    rod('Pendant diffuser',(x,-0.05,2.625),(x,-0.05,2.639),0.25,glow)
    bpy.ops.object.light_add(type='AREA',location=(x,-0.05,2.61)); bpy.context.object.data.energy=110; bpy.context.object.data.color=(1,0.81,0.58); bpy.context.object.data.shape='DISK'; bpy.context.object.data.size=0.45
world=bpy.data.worlds.new('Lobby ambient'); bpy.context.scene.world=world; world.use_nodes=True; world.node_tree.nodes['Background'].inputs[1].default_value=0.35
for loc,power,size in [((-2,-4,6),1400,5),((4,-2,5),900,4)]:
    bpy.ops.object.light_add(type='AREA',location=loc); o=bpy.context.object; o.data.energy=power; o.data.size=size; o.rotation_euler=(Vector((0,0,1))-o.location).to_track_quat('-Z','Y').to_euler()
bpy.ops.object.camera_add(location=(8,-12,7)); cam=bpy.context.object; cam.rotation_euler=(Vector((0.4,0.25,1.50))-cam.location).to_track_quat('-Z','Y').to_euler(); cam.data.type='ORTHO'; cam.data.ortho_scale=10.2
scene=bpy.context.scene; scene.camera=cam; scene.render.engine='CYCLES'; scene.cycles.samples=64; scene.render.resolution_x=1400; scene.render.resolution_y=1050; scene.render.resolution_percentage=100
