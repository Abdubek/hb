import bpy, math
from mathutils import Vector
bpy.ops.object.select_all(action='SELECT'); bpy.ops.object.delete(use_global=False)

def material(name,color,roughness=0.5,metallic=0):
    m=bpy.data.materials.new(name); m.diffuse_color=(*color,1); m.use_nodes=True
    p=m.node_tree.nodes.get('Principled BSDF'); p.inputs['Base Color'].default_value=(*color,1)
    p.inputs['Roughness'].default_value=roughness; p.inputs['Metallic'].default_value=metallic; return m

def box(name,loc,size,mat,bevel=0.015):
    bpy.ops.mesh.primitive_cube_add(size=1,location=loc); o=bpy.context.object; o.name=name; o.dimensions=size
    bpy.ops.object.transform_apply(location=False,rotation=False,scale=True); o.data.materials.append(mat)
    if bevel:
        b=o.modifiers.new('Edge rounding','BEVEL'); b.width=bevel; b.segments=3
        o.modifiers.new('Weighted normals','WEIGHTED_NORMAL')
    return o

def rod(name,a,b,r,mat):
    a,b=Vector(a),Vector(b); d=b-a
    bpy.ops.mesh.primitive_cylinder_add(vertices=24,radius=r,depth=d.length,location=(a+b)/2)
    o=bpy.context.object; o.name=name; o.rotation_euler=d.to_track_quat('Z','Y').to_euler(); o.data.materials.append(mat)
    m=o.modifiers.new('Rounded ends','BEVEL'); m.width=0.006; m.segments=3; o.modifiers.new('Normals','WEIGHTED_NORMAL'); return o

def text(name,body,loc,size,mat):
    bpy.ops.object.text_add(location=loc,rotation=(math.pi/2,0,0)); o=bpy.context.object; o.name=name
    o.data.body=body; o.data.align_x='CENTER'; o.data.size=size; o.data.extrude=0.0003; o.data.materials.append(mat); return o

def area(loc,power,size,color,target):
    bpy.ops.object.light_add(type='AREA',location=loc); o=bpy.context.object; o.data.energy=power; o.data.shape='DISK'; o.data.size=size; o.data.color=color
    o.rotation_euler=(Vector(target)-o.location).to_track_quat('-Z','Y').to_euler()

walnut=material('Walnut veneer',(0.26,0.105,0.040),0.42)
nt=walnut.node_tree; p=nt.nodes.get('Principled BSDF'); tex=nt.nodes.new('ShaderNodeTexNoise'); tex.inputs['Scale'].default_value=3; tex.inputs['Detail'].default_value=2
coord=nt.nodes.new('ShaderNodeTexCoord'); mapping=nt.nodes.new('ShaderNodeVectorMath'); mapping.operation='MULTIPLY'; mapping.inputs[1].default_value=(1.3,32,25)
nt.links.new(coord.outputs['Generated'],mapping.inputs[0]); nt.links.new(mapping.outputs['Vector'],tex.inputs['Vector'])
ramp=nt.nodes.new('ShaderNodeValToRGB'); ramp.color_ramp.elements[0].position=0.2; ramp.color_ramp.elements[0].color=(0.065,0.025,0.012,1)
ramp.color_ramp.elements[1].position=0.8; ramp.color_ramp.elements[1].color=(0.39,0.19,0.072,1)
nt.links.new(tex.outputs['Fac'],ramp.inputs[0]); nt.links.new(ramp.outputs['Color'],p.inputs['Base Color'])
black=material('Satin graphite',(0.019,0.023,0.028),0.3,0.25)
inside=material('Dark cabinet interior',(0.072,0.038,0.019),0.8)
brass=material('Brushed champagne metal',(0.52,0.36,0.16),0.3,0.8)
white=material('Warm lettering',(0.8,0.83,0.82),0.4)
ground=material('Studio floor',(0.38,0.40,0.39),0.85)
blue=material('Book blue',(0.055,0.16,0.23),0.75)
cream=material('Book cream',(0.67,0.58,0.43),0.85)
red=material('Book terracotta',(0.43,0.13,0.07),0.8)
box('Ground',(0,0,-0.10),(200,200,0.2),ground)
# Cabinet carcass: four closed drawers and an open media bay.
for x in [-1.43,1.43]:
    for y in [-0.30,0.30]:
        rod('Taper styled metal leg',(x*1.035,y*1.13,0.04),(x,y,0.31),0.033,black)
box('Cabinet bottom',(0,0,0.33),(3.25,0.85,0.10),walnut)
box('Continuous walnut top',(0,0,1.02),(3.35,0.92,0.12),walnut,0.025)
box('Back panel',(0,0.394,0.67),(3.15,0.05,0.59),inside)
for x in [-1.58,-0.56,0.56,1.58]:
    box('Vertical cabinet panel',(x,0,0.67),(0.075,0.85,0.59),walnut)
for x in [-1.07,1.07]:
    for z in [0.525,0.823]:
        box('Drawer body',(x,-0.035,z),(0.91,0.68,0.253),inside)
        box('Walnut drawer front',(x,-0.451,z),(0.96,0.063,0.28),walnut,0.012)
        for dx in [-0.17,0.17]:
            rod('Pull standoff',(x+dx,-0.49,z+0.035),(x+dx,-0.524,z+0.035),0.009,brass)
        rod('Drawer pull',(x-0.19,-0.528,z+0.035),(x+0.19,-0.528,z+0.035),0.013,brass)
box('Media shelf',(0,0,0.675),(1.045,0.81,0.045),walnut)
box('Streaming receiver',(0,-0.105,0.76),(0.83,0.48,0.105),black,0.017)
box('Receiver display',(-0.10,-0.351,0.765),(0.30,0.008,0.039),blue,0.004)
text('Receiver readout','12:45',(-0.10,-0.357,0.752),0.028,white)
rod('Receiver control',(0.31,-0.35,0.765),(0.31,-0.366,0.765),0.028,brass)
for z,w,m in [(0.41,0.72,cream),(0.468,0.64,red),(0.526,0.69,blue)]:
    box('Art book',(0,-0.07,z),(w,0.53,0.05),m,0.005)
    box('Book spine rule',(-w/2+0.07,-0.339,z),(0.012,0.004,0.035),brass,0.001)
# Television with narrow bezel, rear chassis, V feet, and procedural display.
box('TV rear housing',(0,0.075,2.06),(2.51,0.15,1.39),black,0.045)
box('TV bezel',(0,-0.024,2.06),(2.60,0.065,1.49),black,0.026)
screen=material('Abstract blue display',(0.02,0.08,0.15),0.19,0.15)
nt=screen.node_tree; p=nt.nodes.get('Principled BSDF'); coord=nt.nodes.new('ShaderNodeTexCoord'); sep=nt.nodes.new('ShaderNodeSeparateXYZ')
nt.links.new(coord.outputs['Generated'],sep.inputs[0]); ramp=nt.nodes.new('ShaderNodeValToRGB')
ramp.color_ramp.elements.remove(ramp.color_ramp.elements[1])
for idx,(pos,col) in enumerate([(0,(0.005,0.018,0.06,1)),(0.36,(0.012,0.12,0.21,1)),(0.62,(0.10,0.33,0.39,1)),(0.84,(0.018,0.055,0.15,1)),(1,(0.035,0.09,0.21,1))]):
    e=ramp.color_ramp.elements[0] if idx==0 else ramp.color_ramp.elements.new(pos); e.position=pos; e.color=col
nt.links.new(sep.outputs['Z'],ramp.inputs[0]); nt.links.new(ramp.outputs['Color'],p.inputs['Base Color']); nt.links.new(ramp.outputs['Color'],p.inputs['Emission Color']); p.inputs['Emission Strength'].default_value=0.35
box('Television glass screen',(0,-0.064,2.075),(2.475,0.012,1.352),screen,0.013)
text('Small television branding','A U R A',(0,-0.064,1.348),0.021,white)
led=material('Standby LED',(0.06,0.52,0.76),0.3); led.node_tree.nodes.get('Principled BSDF').inputs['Emission Color'].default_value=(0.08,0.6,1,1)
rod('TV status light',(1.12,-0.06,1.347),(1.12,-0.07,1.347),0.006,led)
for x in [-0.87,0.87]:
    for y,dx in [(-0.27,0.14),(0.25,-0.08)]:
        rod('TV V stand',(x,0.025,1.40),(x+math.copysign(dx,x),y,1.10),0.025,black)
        box('TV foot pad',(x+math.copysign(dx,x),y,1.091),(0.17,0.08,0.018),black,0.008)
# Remote placed on the free strip of the console top.
remote=box('Remote control',(1.39,-0.22,1.102),(0.14,0.31,0.039),black,0.018)
for i in range(4):
    for j in range(2):
        box('Remote key',(1.357+j*0.066,-0.29+i*0.049,1.126),(0.029,0.025,0.009),white,0.006)
area((-3,-4,6),1050,4,(1,0.84,0.69),(0,0,1.1)); area((4,-1,4.5),750,3,(0.72,0.84,1),(0,0,1.5)); area((0,3,5),900,3,(1,1,1),(0,0,1.5))
scene=bpy.context.scene; scene.world.color=(0.20,0.20,0.20)
bpy.ops.object.camera_add(location=(4.4,-6.6,3.7)); cam=bpy.context.object
cam.rotation_euler=(Vector((0,0,1.45))-cam.location).to_track_quat('-Z','Y').to_euler(); cam.data.type='ORTHO'; cam.data.ortho_scale=4.8; scene.camera=cam
scene.render.engine='CYCLES'; scene.cycles.samples=48; scene.render.resolution_x=1500; scene.render.resolution_y=1200; scene.render.resolution_percentage=100
scene.view_settings.view_transform='AgX'
