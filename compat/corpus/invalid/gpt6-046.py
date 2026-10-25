import bpy, math
from mathutils import Vector
bpy.ops.wm.read_factory_settings(use_empty=True)

def mat(name, color, metallic=0, roughness=.45):
    m=bpy.data.materials.new(name); m.diffuse_color=(*color,1); m.use_nodes=True
    p=m.node_tree.nodes.get('Principled BSDF'); p.inputs['Base Color'].default_value=(*color,1); p.inputs['Metallic'].default_value=metallic; p.inputs['Roughness'].default_value=roughness
    return m

def box(name, loc, scale, material, bevel=.025):
    bpy.ops.mesh.primitive_cube_add(size=1, location=loc); o=bpy.context.object; o.name=name; o.dimensions=scale
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True); o.data.materials.append(material)
    if bevel:
        b=o.modifiers.new('Soft manufactured edges','BEVEL'); b.width=bevel; b.segments=3
        o.modifiers.new('Weighted corner normals','WEIGHTED_NORMAL')
    return o

def cylinder(name, loc, radius, depth, material):
    bpy.ops.mesh.primitive_cylinder_add(vertices=48, radius=radius, depth=depth, location=loc); o=bpy.context.object; o.name=name; o.data.materials.append(material)
    b=o.modifiers.new('Edge radius','BEVEL'); b.width=.015; b.segments=3; o.modifiers.new('Normals','WEIGHTED_NORMAL'); return o

def text(body, loc, size, material):
    bpy.ops.object.text_add(location=loc, rotation=(math.pi/2,0,0)); o=bpy.context.object; o.name=body; o.data.body=body; o.data.size=size; o.data.extrude=.0015; o.data.materials.append(material); return o

def aim(o, point): o.rotation_euler=(Vector(point)-o.location).to_track_quat('-Z','Y').to_euler()
def area(name, loc, power, size, target):
    bpy.ops.object.light_add(type='AREA', location=loc); o=bpy.context.object; o.name=name; o.data.energy=power; o.data.shape='DISK'; o.data.size=size; aim(o,target)

white=mat('Warm white laminate',(.84,.83,.78)); dark=mat('Graphite',(.035,.05,.065)); teal=mat('Brand teal',(.02,.34,.33)); aluminum=mat('Brushed aluminum',(.55,.59,.62),.8,.28); wood=mat('Oak platform',(.43,.25,.12)); floor=mat('Hall floor',(.19,.21,.23)); glass=mat('Smoky acrylic',(.075,.18,.22),.35,.16); gold=mat('Sculpture brass',(.7,.39,.10),.75,.25)
box('Exhibition hall ground',(0,0,-.15),(200,200,.2),floor)
box('Raised modular deck',(0,0,.09),(8,6,.28),wood,.05)
box('Inset booth flooring',(0,0,.24),(7.9,5.9,.035),white,.01)
for x in (-3,-1,1,3):
    box('Rear interchangeable wall panel',(x,2.88,1.88),(1.96,.12,3.24),white)
for x in (-4,-2,0,2,4):
    box('Rear aluminum upright',(x,2.85,1.94),(.075,.15,3.4),aluminum,.008)
for y in (-1.95,0,1.95):
    box('Side interchangeable wall panel',(-3.96,y,1.88),(.12,1.9,3.24),white)
for y in (-2.94,-.98,.98,2.94):
    box('Side aluminum upright',(-3.98,y,1.94),(.15,.075,3.4),aluminum,.008)
box('Rear top rail',(0,2.85,3.6),(8.12,.17,.12),aluminum,.008)
box('Side top rail',(-3.96,0,3.6),(.17,6,.12),aluminum,.008)
box('Brand feature panel',(.4,2.785,2.12),(3.65,.035,2.55),teal,.005)
text('FORM / LAB',(-1.15,2.75,2.68),.40,white)
text('MODULAR IDEAS',(-1.12,2.747,2.25),.155,white)
for i in range(4):
    box('Brand relief line',(.37,2.746,1.35+i*.13),(2.95,.025,.025),white,.006)
box('Open entrance header',(0,-2.8,3.72),(8.1,.23,.48),dark)
for x in (-3.95,3.95): box('Entrance support',(x,-2.8,1.91),(.10,.10,3.52),aluminum,.01)
text('FORM / LAB',(-3.45,-2.925,3.58),.27,white)
text('EXHIBITION  /  01',(1.5,-2.925,3.60),.16,white)
for idx,(x,y,h) in enumerate([(-2.5,.8,1.0),(-.7,.5,.8),(1.2,.75,1.2)]):
    box('Plinth recessed foot',(x,y,.31),(.72,.72,.12),dark)
    box('Display plinth',(x,y,.36+h/2),(.92,.92,h),white,.035)
    box('Plinth top',(x,y,.37+h),(.96,.96,.055),aluminum,.012)
    text('0'+str(idx+1),(x-.36,y-.47,.55),.12,teal)
    if idx==0:
        bpy.ops.mesh.primitive_torus_add(major_radius=.27, minor_radius=.07, major_segments=48, minor_segments=12, location=(x,y,h+.73), rotation=(math.pi/2,0,0)); bpy.context.object.data.materials.append(gold)
    elif idx==1:
        bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=2, radius=.32, location=(x,y,h+.72)); bpy.context.object.data.materials.append(teal)
    else:
        cylinder('Exhibit base',(x,y,h+.43),.24,.06,dark)
        for j in range(5):
            o=box('Stacked concept model',(x,y,h+.51+j*.105),(.39,.39,.075),gold,.01); o.rotation_euler.z=j*.23
box('Reception counter foot',(2.65,-1.7,.34),(1.7,.68,.16),dark)
box('Reception counter',(2.65,-1.7,.84),(1.85,.8,1.0),teal,.06)
box('Reception worktop',(2.65,-1.7,1.37),(1.98,.93,.09),white,.035)
text('WELCOME',(1.96,-2.108,.89),.20,white)
box('Tablet stand',(2.8,-1.63,1.46),(.26,.22,.08),aluminum)
o=box('Information tablet',(2.8,-1.63,1.64),(.40,.055,.30),dark); o.rotation_euler.x=math.radians(15)
box('Wall display screen',(-2.5,2.77,2.35),(1.22,.065,.78),dark)
box('Screen graphic',(-2.5,2.729,2.35),(1.09,.015,.65),glass,.005)
text('DESIGN',(-2.94,2.715,2.39),.18,white)
text('BUILD / REPEAT',(-2.94,2.715,2.2),.09,white)
for x in (-2.7,0,2.7):
    box('Ceiling light housing',(x,1.9,3.49),(.32,.25,.13),dark)
    area('Exhibit downlight',(x,1.85,3.39),90,.45,(x,.5,.8))
area('Large front softbox',(2,-6,8),1500,7,(0,0,1)); area('Side fill',(-6,-1,5),900,5,(0,0,1.5))
bpy.ops.object.camera_add(location=(11,-14,9)); camera=bpy.context.object; aim(camera,(0,0,1.5)); camera.data.type='ORTHO'; camera.data.ortho_scale=12.5
scene=bpy.context.scene; scene.camera=camera; scene.render.engine='CYCLES'; scene.cycles.samples=64; scene.world.color=(.22,.22,.22); scene.render.resolution_x=1600; scene.render.resolution_y=1200; scene.render.resolution_percentage=100
