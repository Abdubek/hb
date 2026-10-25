import bpy, math
from mathutils import Vector

bpy.ops.wm.read_factory_settings(use_empty=True)

def mat(name, color, metallic=0, roughness=.45):
    m = bpy.data.materials.new(name)
    m.diffuse_color = (*color, 1)
    m.use_nodes = True
    p = m.node_tree.nodes.get('Principled BSDF')
    p.inputs['Base Color'].default_value = (*color, 1)
    p.inputs['Metallic'].default_value = metallic
    p.inputs['Roughness'].default_value = roughness
    return m

wood = mat('Honey oak', (.43,.20,.065))
steel = mat('Forest green powder coat', (.035,.095,.064), .65)
bolt = mat('Stainless fasteners', (.48,.51,.52), .85)
ground = mat('Warm paving', (.28,.29,.26))

def box(name, loc, size, material, bevel=.02):
    bpy.ops.mesh.primitive_cube_add(size=1, location=loc)
    o = bpy.context.object
    o.name = name
    o.dimensions = size
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    o.data.materials.append(material)
    if bevel:
        b = o.modifiers.new('Soft edges', 'BEVEL'); b.width=bevel; b.segments=3
        o.modifiers.new('Weighted normals', 'WEIGHTED_NORMAL')
    return o

def bar(name, a, b, width, depth, material):
    a,b = Vector(a),Vector(b)
    o = box(name, (a+b)/2, (width,depth,(b-a).length),material,.012)
    o.rotation_euler = (b-a).to_track_quat('Z','Y').to_euler()
    return o

def screw(loc, axis):
    bpy.ops.mesh.primitive_uv_sphere_add(segments=12, ring_count=6, radius=1, location=loc)
    o=bpy.context.object; o.name='Slat carriage bolt'; o.scale=(.013,.013,.006)
    o.rotation_euler=Vector(axis).to_track_quat('Z','Y').to_euler()
    o.data.materials.append(bolt)

# Two-person seat, five independent timber slats.
for i in range(5):
    y=-.255+i*.124
    box('Seat slat %02d'%i,(0,y,.505),(1.65,.108,.055),wood,.012)
    for x in (-.65,.65): screw((x,y,.535),(0,0,1))

# Lean the back uprights and slats together.
angle=math.radians(11)
for i in range(4):
    z=.70+i*.125
    y=.28+(z-.55)*math.tan(angle)
    o=box('Backrest slat %02d'%i,(0,y,z),(1.65,.045,.105),wood,.012)
    o.rotation_euler.x=-angle
    for x in (-.65,.65): screw((x,y-.026,z),(0,-math.cos(angle),math.sin(angle)))

for x in (-.65,.65):
    box('Seat support rail',(x,0,.447),(.065,.66,.065),steel,.012)
    bar('Front splayed leg',(x,-.32,.06),(x,-.23,.45),.065,.065,steel)
    bar('Rear splayed leg',(x,.35,.06),(x,.24,.45),.065,.065,steel)
    bar('Back upright',(x,.245,.42),(x,.39,1.145),.055,.055,steel)
    bar('Arm front support',(x,-.21,.45),(x,-.21,.755),.045,.045,steel)
    box('Timber arm cap',(x,.015,.78),(.115,.60,.05),wood,.02)
    for y in (-.32,.35):
        box('Anchor foot',(x,y,.035),(.16,.13,.045),steel,.015)
bar('Lower cross brace',(-.65,.18,.255),(.65,.18,.255),.045,.045,steel)
box('Ground',(0,0,-.065),(200,200,.1),ground,.0)

world=bpy.data.worlds.new('World'); bpy.context.scene.world=world
world.use_nodes=True; world.node_tree.nodes['Background'].inputs[0].default_value=(.55,.65,.75,1)
world.node_tree.nodes['Background'].inputs[1].default_value=.35
for name,loc,power,size in [('Key',(-3,-4,6),700,4),('Fill',(4,1,4),450,3)]:
    bpy.ops.object.light_add(type='AREA', location=loc)
    o=bpy.context.object; o.name=name; o.data.energy=power; o.data.shape='DISK'; o.data.size=size
    o.rotation_euler=(Vector((0,0,.5))-o.location).to_track_quat('-Z','Y').to_euler()
bpy.ops.object.camera_add(location=(2.65,-3.5,2.05))
camera=bpy.context.object; camera.rotation_euler=(Vector((0,0,.59))-camera.location).to_track_quat('-Z','Y').to_euler()
camera.data.type='ORTHO'; camera.data.ortho_scale=2.65
scene=bpy.context.scene; scene.camera=camera
scene.render.engine='CYCLES'; scene.render.resolution_x=1400; scene.render.resolution_y=1000; scene.render.resolution_percentage=100
