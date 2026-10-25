import bpy, math
from mathutils import Vector

# Architectural cutaway: the near wall and near half of the roof are removed.
bpy.ops.wm.read_factory_settings(use_empty=True)

def mat(name, color, roughness=.6, metallic=0):
    m=bpy.data.materials.new(name); m.diffuse_color=(*color,1)
    m.use_nodes=True; p=m.node_tree.nodes.get('Principled BSDF')
    p.inputs['Base Color'].default_value=(*color,1)
    p.inputs['Roughness'].default_value=roughness; p.inputs['Metallic'].default_value=metallic
    return m

def box(name, loc, scale, material, bevel=0):
    bpy.ops.mesh.primitive_cube_add(size=1, location=loc)
    o=bpy.context.object; o.name=name; o.dimensions=scale
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    o.data.materials.append(material)
    if bevel:
        mod=o.modifiers.new('Soft concrete edges','BEVEL'); mod.width=bevel; mod.segments=2
        o.modifiers.new('Weighted normals','WEIGHTED_NORMAL')
    return o

def rod(name, a, b, radius, material, vertices=12):
    a,b=Vector(a),Vector(b); d=b-a
    bpy.ops.mesh.primitive_cylinder_add(vertices=vertices, radius=radius, depth=d.length, location=(a+b)/2)
    o=bpy.context.object; o.name=name; o.rotation_euler=d.to_track_quat('Z','Y').to_euler()
    o.data.materials.append(material)
    return o

def aim(o, point): o.rotation_euler=(Vector(point)-o.location).to_track_quat('-Z','Y').to_euler()

def area(name, loc, power, size, target, color=(1,1,1)):
    bpy.ops.object.light_add(type='AREA', location=loc); o=bpy.context.object; o.name=name
    o.data.energy=power; o.data.shape='DISK'; o.data.size=size; o.data.color=color; aim(o,target)

concrete=mat('Board formed concrete',(.47,.49,.47))
p=concrete.node_tree.nodes.get('Principled BSDF'); n=concrete.node_tree.nodes.new('ShaderNodeTexNoise')
n.inputs['Scale'].default_value=36; n.inputs['Detail'].default_value=3
b=concrete.node_tree.nodes.new('ShaderNodeBump'); b.inputs['Strength'].default_value=.22; b.inputs['Distance'].default_value=.045
concrete.node_tree.links.new(n.outputs['Fac'],b.inputs['Height']); concrete.node_tree.links.new(b.outputs['Normal'],p.inputs['Normal'])
paving=mat('Pale precast treads',(.66,.67,.63)); steel=mat('Galvanized steel',(.38,.45,.47),.28,.8)
dark=mat('Drain interior',(.045,.058,.06)); road=mat('Asphalt',(.12,.14,.15)); soil=mat('Cut earth',(.25,.22,.17))
yellow=mat('Safety ochre',(.92,.64,.12)); blue=mat('Wayfinding blue',(.035,.17,.28))
white=mat('Lettering',(.9,.94,.91)); lamp=mat('Warm luminaire',(.95,.79,.47))
p=lamp.node_tree.nodes.get('Principled BSDF'); p.inputs['Emission Color'].default_value=(1,.78,.43,1); p.inputs['Emission Strength'].default_value=4

box('Presentation ground',(0,0,-.65),(27,15,.3),soil,.1)
box('Underpass foundation',(0,0,-.3),(21,5.8,.5),concrete,.05)
box('Central walkway',(0,0,-.06),(10,4.25,.12),paving,.025)
box('Back retaining wall',(0,2.67,1.65),(21,.42,3.9),concrete,.035)
box('Near wall cutaway sill',(0,-2.67,.12),(21,.42,.65),concrete,.025)
box('Roof cutaway slab',(0,1.32,3.48),(10.4,3.1,.42),concrete,.04)
box('Road surface above roof',(0,1.32,3.73),(10.4,3.1,.08),road)
for x in (-3,0,3): box('Road lane dash',(x,1.4,3.777),(1.5,.1,.012),white)
for x in (-5.05,5.05):
    box('Tunnel portal beam',(x,0,3.28),(.36,5.55,.38),concrete,.035)
    for y in (-2.48,2.48): box('Portal jamb',(x,y,1.55),(.42,.35,3.1),concrete,.025)

# Two opposing stair flights rise from the tunnel to street level.
steps=12; run=.43; rise=.29
for side in (-1,1):
    for i in range(steps):
        x=side*(5+(i+.5)*run); z=(i+1)*rise
        box('Solid stair %s %02d'%(side,i),(x,0,z/2),(run,4.28,z),paving,.014)
        box('Contrasting stair nosing',(side*(5+i*run+.035),0,z+.009),(.065,4.2,.018),yellow,.004)
    end=5+steps*run; top=steps*rise
    box('Upper landing',(side*(end+.9),0,top-.12),(1.8,5.7,.24),concrete,.025)
    for j in range(7):
        box('Tactile warning rib',(side*(end+.2+j*.09),0,top+.025),(.035,3.65,.05),yellow,.009)
    for y in (-2.18,2.18):
        for i in range(0,steps+1,2):
            x=side*(5+i*run); z=min((i+1)*rise,top)
            rod('Stair baluster',(x,y,z),(x,y,z+1),.032,steel)
            box('Baluster foot',(x,y,z+.02),(.16,.16,.04),steel,.015)
        rod('Sloping handrail',(side*5,y,rise+1),(side*end,y,top+1),.047,steel)
        rod('Mid rail',(side*5,y,rise+.52),(side*end,y,top+.52),.025,steel)
        rod('Landing handrail',(side*end,y,top+1),(side*(end+1.7),y,top+1),.047,steel)
        rod('Landing end post',(side*(end+1.7),y,top),(side*(end+1.7),y,top+1),.032,steel)

# Open trench drains with metal frames and individually modeled grate bars.
for y in (-2.32,2.32):
    box('Drain trench',(0,y,-.025),(10,.25,.19),dark)
    for edge in (-.135,.135): box('Drain frame',(0,y+edge,.027),(10,.025,.035),steel)
    for i in range(126): box('Grate cross bar',(-4.96+i*.079,y,.028),(.025,.24,.026),steel)
    rod('Level wall handrail',(-4.8,y,1.06),(4.8,y,1.06),.043,steel)
    for x in (-4,-2,0,2,4): rod('Handrail bracket',(x,y,1.06),(x,y+(.19 if y>0 else -.19),.96),.022,steel)
for x in (-4.3,4.3):
    box('Sump frame',(x,1.82,.025),(.58,.58,.04),steel,.025)
    box('Sump dark opening',(x,1.82,.05),(.49,.49,.025),dark)
    for j in range(7): box('Sump grate',(x-.21+j*.07,1.82,.07),(.026,.48,.035),steel)

# Formwork joints and tie holes on the exposed back wall.
for x in range(-10,11,2):
    box('Vertical formwork seam',(x,2.451,1.68),(.012,.009,3.65),dark)
    for z in (.6,1.8,2.9):
        o=rod('Recessed form tie',(x+.36,2.439,z),(x+.36,2.449,z),.033,dark)
for z in (.85,1.7,2.55): box('Horizontal formwork seam',(0,2.448,z),(20.7,.01,.009),dark)
for x in (-3.5,0,3.5):
    box('Wall light housing',(x,2.32,2.73),(1.16,.23,.19),steel,.025)
    box('Wall light diffuser',(x,2.185,2.72),(1,.025,.1),lamp,.012)
    area('Tunnel warm light',(x,2.02,2.65),160,1.5,(x,0,.3),(1,.8,.54))
box('Wayfinding panel',(0,2.405,1.94),(2.7,.065,.49),blue,.035)
bpy.ops.object.text_add(location=(0,2.359,1.82), rotation=(math.pi/2,0,0))
t=bpy.context.object; t.name='Pedestrian passage sign'; t.data.body='PEDESTRIAN  /  EXIT'; t.data.align_x='CENTER'; t.data.size=.19; t.data.extrude=.001; t.data.materials.append(white)

area('Large daylight',(0,-7,15),2400,10,(0,0,0))
area('Entrance fill',(12,2,10),1600,7,(4,0,1))
bpy.ops.object.camera_add(location=(19,-23,17)); cam=bpy.context.object; aim(cam,(0,0,1.1)); cam.data.type='ORTHO'; cam.data.ortho_scale=29
scene=bpy.context.scene; scene.camera=cam; scene.render.engine='CYCLES'; scene.cycles.samples=64
scene.world.color=(.28,.28,.28); scene.render.resolution_x=1600; scene.render.resolution_y=1000; scene.render.resolution_percentage=100
scene.view_settings.view_transform='AgX'
