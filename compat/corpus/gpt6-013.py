import bpy, math
from mathutils import Vector

bpy.ops.object.select_all(action='SELECT'); bpy.ops.object.delete(use_global=False)

def mat(name,color,metal=0,rough=.4,trans=0):
    m=bpy.data.materials.new(name); m.diffuse_color=(*color,1); m.use_nodes=True
    p=m.node_tree.nodes.get('Principled BSDF'); p.inputs['Base Color'].default_value=(*color,1); p.inputs['Metallic'].default_value=metal; p.inputs['Roughness'].default_value=rough; p.inputs['Transmission Weight'].default_value=trans
    return m

def box(name,loc,dims,m,bevel=.025):
    bpy.ops.mesh.primitive_cube_add(size=1,location=loc); o=bpy.context.object; o.name=name; o.dimensions=dims; bpy.ops.object.transform_apply(location=False,rotation=False,scale=True); o.data.materials.append(m)
    if bevel:
        b=o.modifiers.new('Edge bevel','BEVEL'); b.width=bevel; b.segments=3; o.modifiers.new('Weighted normals','WEIGHTED_NORMAL')
    return o

def cyl(name,loc,r,d,m,n=64):
    bpy.ops.mesh.primitive_cylinder_add(vertices=n,radius=r,depth=d,location=loc); o=bpy.context.object; o.name=name; o.data.materials.append(m); return o

def rod(name,a,b,r,m):
    a=Vector(a); b=Vector(b); o=cyl(name,(a+b)/2,r,(b-a).length,m,24); o.rotation_euler=(b-a).to_track_quat('Z','Y').to_euler(); return o

def ring(name,loc,r,t,m):
    bpy.ops.mesh.primitive_torus_add(major_segments=96,minor_segments=6,major_radius=r,minor_radius=t,location=loc); o=bpy.context.object; o.name=name; o.data.materials.append(m); return o

wood=mat('Walnut plinth',(.2,.075,.025),0,.35); black=mat('Black rubber',(.018,.021,.024),0,.6); silver=mat('Brushed aluminum',(.56,.59,.62),.85,.25)
vinyl=mat('Black vinyl',(.011,.013,.018),.15,.24); groove=mat('Groove highlights',(.022,.025,.03),.25,.33); label=mat('Burnt orange record label',(.63,.14,.045))
cream=mat('Label ink',(.88,.78,.55)); acrylic=mat('Smoked transparent acrylic',(.76,.85,.88),0,.075,1); floor=mat('Backdrop',(.17,.21,.24))
p=wood.node_tree.nodes.get('Principled BSDF'); tex=wood.node_tree.nodes.new('ShaderNodeTexNoise'); tex.inputs['Scale'].default_value=4; tex.inputs['Detail'].default_value=2
coord=wood.node_tree.nodes.new('ShaderNodeTexCoord'); mapping=wood.node_tree.nodes.new('ShaderNodeVectorMath'); mapping.operation='MULTIPLY'; mapping.inputs[1].default_value=(1,30,7)
wood.node_tree.links.new(coord.outputs['Generated'],mapping.inputs[0]); wood.node_tree.links.new(mapping.outputs['Vector'],tex.inputs['Vector'])
ramp=wood.node_tree.nodes.new('ShaderNodeValToRGB'); ramp.color_ramp.elements[0].color=(.045,.013,.004,1); ramp.color_ramp.elements[1].color=(.3,.13,.045,1); wood.node_tree.links.new(tex.outputs['Fac'],ramp.inputs[0]); wood.node_tree.links.new(ramp.outputs[0],p.inputs['Base Color'])

box('Walnut turntable plinth',(0,0,.4),(4.8,3.6,.5),wood,.1)
box('Inset top deck',(0,0,.67),(4.61,3.41,.055),black,.035)
for x in (-1.85,1.85):
    for y in (-1.3,1.3):
        cyl('Isolation foot',(x,y,.12),.24,.22,black,32); cyl('Foot metal band',(x,y,.18),.244,.065,silver,32)
cx=-.58; cy=-.04
cyl('Aluminum platter',(cx,cy,.79),1.48,.18,silver,96)
cyl('Platter mat',(cx,cy,.889),1.435,.025,black,96)
cyl('Vinyl record',(cx,cy,.912),1.415,.022,vinyl,128)
for i in range(37): ring('Concentric record groove',(cx,cy,.925),.47+i*.024,.0025,groove)
cyl('Center record label',(cx,cy,.927),.405,.007,label,64)
for r in (.32,.35): ring('Printed label border',(cx,cy,.933),r,.003,cream)
cyl('Spindle',(cx,cy,.979),.037,.11,silver,24)
cu=bpy.data.curves.new('Record title','FONT'); cu.body='SIDE A'; cu.align_x='CENTER'; cu.size=.09
ob=bpy.data.objects.new('Record title',cu); bpy.context.collection.objects.link(ob); ob.location=(cx,cy+.15,.935); cu.materials.append(cream)
# Small platter edge dots.
for i in range(64):
    a=i*math.tau/64; cyl('Platter strobe mark',(cx+1.461*math.cos(a),cy+1.461*math.sin(a),.887),.011,.006,black,8)
# Pivot, bearings, rear counterweight, bent tonearm and cartridge.
pivot=(1.56,.91)
cyl('Tonearm pedestal',(*pivot,.8),.29,.22,silver,48)
cyl('Pivot housing',(*pivot,1.04),.18,.31,black,32)
rod('Horizontal bearing axle',(1.29,.91,1.14),(1.82,.91,1.14),.075,silver)
rod('Rear arm extension',(1.56,.91,1.16),(1.63,1.48,1.16),.057,silver)
rod('Counterweight',(1.595,1.21,1.16),(1.645,1.6,1.16),.185,black)
rod('Counterweight trim',(1.64,1.54,1.16),(1.65,1.62,1.16),.187,silver)
points=[(1.56,.91,1.16),(1.49,.43,1.16),(1.1,-.43,1.14),(.68,-.89,1.12)]
for a,b in zip(points,points[1:]): rod('Bent polished tonearm',a,b,.048,silver)
head=box('Headshell',(.58,-1.01,1.105),(.22,.43,.055),black,.016); head.rotation_euler[2]=-.62
cart=box('Cartridge',(.58,-1.01,1.023),(.14,.22,.11),label,.013); cart.rotation_euler[2]=-.62
rod('Stylus',(.56,-1.06,.978),(.54,-1.085,.941),.008,silver)
rod('Finger lift',(.67,-.97,1.12),(.85,-1.05,1.25),.019,silver)
cyl('Arm rest post',(1.48,.22,.94),.055,.49,silver,20)
box('Rest fork',(1.48,.22,1.2),(.23,.09,.05),black,.01)
rod('Cue lever',(1.82,.75,.99),(1.98,.44,1.03),.025,silver)
cyl('Start stop button',(-1.99,-1.34,.735),.15,.065,silver,32)
cyl('Speed selector',(-1.51,-1.34,.75),.1,.09,silver,32)
box('Pitch slider recess',(1.92,-.82,.715),(.15,1.06,.02),silver,.01)
box('Pitch slider slot',(1.92,-.82,.731),(.035,.92,.012),black,.005)
box('Pitch slider cap',(1.92,-.67,.77),(.24,.13,.075),black,.02)
# Open five-panel dust cover rotates as a rigid assembly about its rear hinge.
hinge=bpy.data.objects.new('Dust cover hinge axis',None); bpy.context.collection.objects.link(hinge); hinge.location=(0,1.77,.72)
for name,loc,dims in [('Cover roof',(0,-1.77,.74),(4.89,3.58,.045)),('Cover front',(0,-3.535,.37),(4.89,.045,.74)),('Cover rear',(0,0,.37),(4.89,.045,.74)),('Cover left',(-2.422,-1.77,.37),(.045,3.58,.74)),('Cover right',(2.422,-1.77,.37),(.045,3.58,.74))]:
    o=box(name,loc,dims,acrylic,.015); o.parent=hinge
hinge.rotation_euler[0]=math.radians(-63)
for x in (-1.65,1.65):
    box('Cover hinge bracket',(x,1.73,.71),(.42,.19,.17),silver,.025)
    rod('Hinge pin',(x-.22,1.77,.77),(x+.22,1.77,.77),.06,black)
box('Ground',(0,0,-.07),(200,200,.1),floor,0)
world=bpy.context.scene.world; world.use_nodes=True; world.node_tree.nodes['Background'].inputs[1].default_value=.4
for loc,energy,size in [((1,-4,8),1100,5),((-5,1,5),800,4),((3,5,7),1300,4)]:
    bpy.ops.object.light_add(type='AREA',location=loc); o=bpy.context.object; o.data.energy=energy; o.data.size=size; o.rotation_euler=(Vector((0,0,1))-o.location).to_track_quat('-Z','Y').to_euler()
bpy.ops.object.camera_add(location=(6,-8,7)); cam=bpy.context.object; cam.rotation_euler=(Vector((0,.3,1.5))-cam.location).to_track_quat('-Z','Y').to_euler(); cam.data.type='ORTHO'; cam.data.ortho_scale=8.2
scene=bpy.context.scene; scene.camera=cam; scene.render.engine='CYCLES'; scene.cycles.samples=64; scene.render.resolution_x=1200; scene.render.resolution_y=1100; scene.render.resolution_percentage=100
