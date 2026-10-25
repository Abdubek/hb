import bpy, math
from mathutils import Vector
bpy.ops.object.select_all(action='SELECT'); bpy.ops.object.delete(use_global=False)

def mat(name,color,roughness=0.45,metallic=0):
    m=bpy.data.materials.new(name); m.diffuse_color=(*color,1); m.use_nodes=True
    p=m.node_tree.nodes.get('Principled BSDF'); p.inputs['Base Color'].default_value=(*color,1); p.inputs['Roughness'].default_value=roughness; p.inputs['Metallic'].default_value=metallic; return m

def box(name,loc,size,m,bevel=0.012):
    bpy.ops.mesh.primitive_cube_add(size=1,location=loc); o=bpy.context.object; o.name=name; o.dimensions=size
    bpy.ops.object.transform_apply(location=False,rotation=False,scale=True); o.data.materials.append(m)
    if bevel:
        b=o.modifiers.new('Manufactured edges','BEVEL'); b.width=bevel; b.segments=3; o.modifiers.new('Weighted normals','WEIGHTED_NORMAL')
    return o

def cyl(name,loc,radius,depth,m,rotation=(0,0,0),vertices=32):
    bpy.ops.mesh.primitive_cylinder_add(vertices=vertices,radius=radius,depth=depth,location=loc,rotation=rotation)
    o=bpy.context.object; o.name=name; o.data.materials.append(m)
    b=o.modifiers.new('Rim bevel','BEVEL'); b.width=0.005; b.segments=2; o.modifiers.new('Weighted normals','WEIGHTED_NORMAL'); return o

def text(name,body,loc,size,m):
    bpy.ops.object.text_add(location=loc,rotation=(math.pi/2,0,0)); o=bpy.context.object; o.name=name; o.data.body=body
    o.data.align_x='CENTER'; o.data.size=size; o.data.extrude=0.00025; o.data.materials.append(m); return o

def wire(name,points,radius,m):
    c=bpy.data.curves.new(name,'CURVE'); c.dimensions='3D'; c.resolution_u=1; c.bevel_depth=radius; c.bevel_resolution=2
    s=c.splines.new('POLY'); s.points.add(len(points)-1)
    for p,co in zip(s.points,points): p.co=(*co,1)
    o=bpy.data.objects.new(name,c); bpy.context.collection.objects.link(o); o.data.materials.append(m); return o

def area(loc,energy,size,color,target):
    bpy.ops.object.light_add(type='AREA',location=loc); o=bpy.context.object; o.data.energy=energy; o.data.size=size; o.data.color=color
    o.rotation_euler=(Vector(target)-o.location).to_track_quat('-Z','Y').to_euler()

teal=mat('Enamel petrol blue',(0.018,0.22,0.27),0.32,0.35)
black=mat('Rubber and interior',(0.016,0.024,0.031),0.7)
metal=mat('Brushed aluminum',(0.43,0.50,0.55),0.3,0.85)
white=mat('Ivory printing',(0.88,0.92,0.88),0.4)
yellow=mat('Golden yellow',(0.96,0.53,0.035),0.42)
red=mat('Berry packaging',(0.66,0.035,0.08),0.4)
blue=mat('Blue packaging',(0.035,0.23,0.65),0.4)
green=mat('Green packaging',(0.15,0.51,0.20),0.45)
ground=mat('Floor',(0.22,0.27,0.30),0.9)
glow=mat('Cool backlight',(0.62,0.88,1),0.3); p=glow.node_tree.nodes.get('Principled BSDF'); p.inputs['Emission Color'].default_value=(0.48,0.8,1,1); p.inputs['Emission Strength'].default_value=2
screen=mat('LCD',(0.02,0.075,0.065),0.25)
glass=mat('Display glazing',(0.73,0.89,0.93),0.12)
nt=glass.node_tree; nt.nodes.clear(); out=nt.nodes.new('ShaderNodeOutputMaterial'); mix=nt.nodes.new('ShaderNodeMixShader'); mix.inputs[0].default_value=0.075
transparent=nt.nodes.new('ShaderNodeBsdfTransparent'); glossy=nt.nodes.new('ShaderNodeBsdfPrincipled'); glossy.inputs['Base Color'].default_value=(0.6,0.8,0.9,1); glossy.inputs['Metallic'].default_value=0.6; glossy.inputs['Roughness'].default_value=0.16
nt.links.new(transparent.outputs[0],mix.inputs[1]); nt.links.new(glossy.outputs[0],mix.inputs[2]); nt.links.new(mix.outputs[0],out.inputs['Surface'])
box('Ground',(0,0,-0.08),(200,200,0.16),ground)
for x in [-0.65,0.65]:
    for y in [-0.35,0.35]: cyl('Leveling foot',(x,y,0.07),0.07,0.14,black)
# Open-front cabinet avoids hiding the product compartment.
box('Cabinet back',(0,0.45,1.43),(1.62,0.11,2.68),teal,0.035)
for x in [-0.765,0.765]: box('Cabinet side',(x,0,1.43),(0.12,0.98,2.68),teal,0.027)
box('Roof',(0,0,2.74),(1.62,0.98,0.13),teal,0.025)
box('Bottom plinth',(0,-0.01,0.22),(1.62,1.0,0.24),black,0.025)
box('Compartment backing',(-0.23,0.36,1.68),(1.09,0.055,1.71),black)
box('Payment column',(0.575,-0.42,1.51),(0.36,0.17,2.19),teal,0.02)
box('Lit header',(0,-0.495,2.59),(1.47,0.065,0.26),black,0.014)
text('Brand','F R E S H  /  2 4',(0,-0.534,2.55),0.105,white)
box('Header accent',(0,-0.537,2.485),(1.36,0.006,0.014),yellow,0.003)
for x in [-0.725,0.345]:
    box('Window gasket',(x,-0.497,1.67),(0.045,0.06,1.64),black)
    box('Interior light bar',(x+(-0.025 if x>0 else 0.025),-0.35,1.69),(0.018,0.024,1.47),glow,0.005)
# Four shelves, each with three product lanes and visible dispensing coils.
colors=[red,yellow,blue,green]
for row in range(4):
    shelf_z=0.92+row*0.36
    box('Product shelf',(-0.19,-0.025,shelf_z),(1.025,0.69,0.037),metal,0.007)
    box('Shelf front rail',(-0.19,-0.381,shelf_z+0.018),(1.02,0.035,0.062),black,0.005)
    for col in range(3):
        x=-0.52+col*0.33; product_mat=colors[(row+col)%4]
        if row<2:
            for y in [-0.20,0.09]:
                cyl('Beverage can',(x,y,shelf_z+0.154),0.092,0.253,product_mat)
                cyl('Can lid',(x,y,shelf_z+0.284),0.085,0.007,metal)
                cyl('Can bottom rim',(x,y,shelf_z+0.029),0.09,0.008,metal)
                box('Pull tab',(x,y-0.013,shelf_z+0.290),(0.025,0.047,0.006),black,0.009)
            text('Can label','POP',(x,-0.297,shelf_z+0.13),0.052,white)
        else:
            for y in [-0.19,0.09]:
                pack=box('Snack packet',(x,y,shelf_z+0.153),(0.205,0.13,0.26),product_mat,0.032)
                box('Packet top seal',(x,y,shelf_z+0.285),(0.20,0.125,0.018),white,0.003)
            text('Snack label','BITES',(x,-0.26,shelf_z+0.145),0.045,white)
        points=[]
        for k in range(151):
            t=k/150; a=t*math.tau*4
            points.append((x+0.119*math.cos(a),-0.30+t*0.58,shelf_z+0.13+0.105*math.sin(a)))
        wire('Dispensing spiral',points,0.009,metal)
        text('Selection code',str(row+1)+str(col+1),(x,-0.403,shelf_z+0.002),0.040,white)
box('Clear product window',(-0.19,-0.469,1.68),(1.025,0.012,1.565),glass,0.005)
box('Lower fascia',(0,-0.445,0.595),(1.49,0.12,0.53),teal)
box('Collection recess',(-0.15,-0.513,0.575),(0.99,0.017,0.29),black,0.025)
box('Collection flap',(-0.15,-0.525,0.625),(0.90,0.018,0.14),metal,0.012)
text('Collection instruction','PUSH TO COLLECT',(-0.15,-0.539,0.61),0.044,black)
box('Pickup lower lip',(-0.15,-0.553,0.42),(1.0,0.13,0.043),metal,0.008)
box('LCD bezel',(0.571,-0.52,2.21),(0.29,0.055,0.18),black)
box('LCD glass',(0.571,-0.551,2.21),(0.25,0.01,0.133),screen,0.005)
text('LCD message','SELECT',(0.571,-0.559,2.222),0.041,glow)
text('LCD price','$ 2.50',(0.571,-0.559,2.165),0.035,glow)
for r in range(4):
    for c in range(3):
        x=0.489+c*0.082; z=1.972-r*0.09
        box('Keypad button',(x,-0.538,z),(0.065,0.045,0.068),metal,0.008)
        text('Key legend',['1','2','3','4','5','6','7','8','9','*','0','#'][r*3+c],(x,-0.565,z-0.017),0.043,black)
box('Card reader',(0.572,-0.542,1.425),(0.235,0.10,0.24),black,0.022)
box('Card insertion slot',(0.572,-0.599,1.375),(0.18,0.008,0.025),metal,0.003)
text('Reader label','TAP / CARD',(0.572,-0.6,1.46),0.029,white)
cyl('Coin bezel',(0.572,-0.526,1.16),0.066,0.03,metal,(math.pi/2,0,0))
box('Coin slot',(0.572,-0.547,1.16),(0.012,0.007,0.080),black,0.003)
for z in [0.91,2.40]: cyl('Door lock',(0.721,-0.512,z),0.017,0.012,metal,(math.pi/2,0,0))
for i in range(10): box('Side ventilation',(0.829,0.06,0.43+i*0.036),(0.009,0.50,0.014),black,0.004)
area((-3,-4,5),850,3,(0.80,0.9,1),(0,0,1.4)); area((4,-2,4),700,3,(1,0.82,0.64),(0,0,1.5)); area((1,3,5),1000,2,(0.65,0.86,1),(0,0,1.7))
scene=bpy.context.scene; scene.world.color=(0.18,0.18,0.18)
bpy.ops.object.camera_add(location=(4,-6.5,3.7)); cam=bpy.context.object; cam.rotation_euler=(Vector((0,0,1.4))-cam.location).to_track_quat('-Z','Y').to_euler(); cam.data.type='ORTHO'; cam.data.ortho_scale=3.65; scene.camera=cam
scene.render.engine='CYCLES'; scene.cycles.samples=64; scene.render.resolution_x=1200; scene.render.resolution_y=1500; scene.render.resolution_percentage=100; scene.view_settings.view_transform='AgX'
