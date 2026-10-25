import bpy, math
from mathutils import Vector
bpy.ops.wm.read_factory_settings(use_empty=True)

def mat(name, color, metallic=0, roughness=.5):
    m=bpy.data.materials.new(name); m.diffuse_color=(*color,1); m.use_nodes=True
    p=m.node_tree.nodes.get('Principled BSDF'); p.inputs['Base Color'].default_value=(*color,1); p.inputs['Metallic'].default_value=metallic; p.inputs['Roughness'].default_value=roughness
    return m

def box(name, loc, size, material, bevel=0):
    bpy.ops.mesh.primitive_cube_add(size=1, location=loc); o=bpy.context.object; o.name=name; o.dimensions=size
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True); o.data.materials.append(material)
    if bevel:
        b=o.modifiers.new('Soft edges','BEVEL'); b.width=bevel; b.segments=3
        o.modifiers.new('Weighted normals','WEIGHTED_NORMAL')
    return o

def rod(name, a, b, radius, material):
    a,b=Vector(a),Vector(b); d=b-a
    bpy.ops.mesh.primitive_cylinder_add(vertices=24, radius=radius, depth=d.length, location=(a+b)/2)
    o=bpy.context.object; o.name=name; o.rotation_euler=d.to_track_quat('Z','Y').to_euler(); o.data.materials.append(material)
    for p in o.data.polygons: p.use_smooth=True
    return o

def light(name, loc, power, size, target):
    bpy.ops.object.light_add(type='AREA', location=loc); o=bpy.context.object; o.name=name; o.data.energy=power; o.data.shape='DISK'; o.data.size=size; o.rotation_euler=(Vector(target)-o.location).to_track_quat('-Z','Y').to_euler()

wall=mat('Warm plaster',(.79,.76,.69)); trim=mat('Ivory woodwork',(.94,.92,.84)); oak=mat('Honey oak',(.43,.24,.105)); dark=mat('Dark bronze',(.085,.065,.045),.65,.3)
fabric=mat('Sage upholstery',(.25,.39,.32),0,.88); cushion=mat('Linen cushions',(.84,.75,.55),0,.95); rug=mat('Terracotta woven rug',(.51,.24,.16),0,1); cream=mat('Ceramic',(.85,.85,.76),0,.26); green=mat('Leaves',(.12,.28,.09),0,.8); soil=mat('Potting soil',(.055,.029,.013)); glass=mat('Window glass',(.68,.86,.95),0,.12)
p=glass.node_tree.nodes.get('Principled BSDF'); p.inputs['Transmission Weight'].default_value=.7; p.inputs['IOR'].default_value=1.45
# The clear internal floor measures exactly 4 m by 5 m; front and right walls
# are intentionally omitted for an architectural cutaway presentation.
box('Floor slab', (0,0,-.12),(4.24,5.24,.24),trim,.025)
for ix in range(16):
    for iy in range(5):
        box('Individual oak floorboard',(-1.875+ix*.25,-2+iy, .014),(.246,.994,.028),oak,.006)
# Back wall: a real 0.9 m wide, 2.15 m high doorway at x=1.25.
box('Back wall left',(-.65,2.6,1.4),(2.9,.2,2.8),wall)
box('Back wall right',(1.91,2.6,1.4),(.42,.2,2.8),wall)
box('Door lintel',(1.25,2.6,2.475),(.9,.2,.65),wall)
for x in [.76,1.74]: box('Door casing',(x,2.465,1.095),(.08,.07,2.19),trim,.008)
box('Door casing header',(1.25,2.465,2.19),(1.06,.07,.08),trim,.008)
# Open door leaf rotates about its hinge into the room.
bpy.ops.object.empty_add(location=(.81,2.46,0)); hinge=bpy.context.object; hinge.name='Open doorway hinge'; hinge.rotation_euler.z=math.radians(-64)
door=box('Oak door leaf',(0,0,0),(.87,.045,2.1),oak,.012); door.parent=hinge; door.location=(.435,0,1.05)
for z in [.56,1.56]:
    panel=box('Inset door panel',(0,0,0),(.65,.014,.76),trim,.008); panel.parent=hinge; panel.location=(.435,-.027,z)
handle=rod('Door lever',(0,0,0),(.13,0,0),.015,dark); handle.parent=hinge; handle.location=(.68,-.075,1.02)
# Left wall: real window opening y=-0.8..1.0, z=1.0..2.25.
box('Wall below window',(-2.1,0,.5),(.2,5,1),wall)
box('Wall above window',(-2.1,0,2.525),(.2,5,.55),wall)
box('Window wall front pier',(-2.1,-1.65,1.625),(.2,1.7,1.25),wall)
box('Window wall rear pier',(-2.1,1.75,1.625),(.2,1.5,1.25),wall)
for y in [-.8,1.0]: box('Window upright',(-2.075,y,1.625),(.13,.065,1.31),trim,.006)
for z in [1.0,2.25]: box('Window horizontal frame',(-2.075,.1,z),(.13,1.86,.065),trim,.006)
box('Window mullion',(-2.055,.1,1.625),(.1,.045,1.2),trim,.004)
for y in [-.35,.55]: box('Glass pane',(-2.09,y,1.625),(.012,.84,1.17),glass)
box('Projecting window sill',(-1.995,.1,.97),(.38,2.0,.07),trim,.012)
box('Left skirting',(-1.976,0,.09),(.035,5,.15),trim,.007)
box('Back skirting',(-.62,2.474,.09),(2.76,.035,.15),trim,.007)
# Sofa against the back-left corner.
for x in [-1.44,.24]:
    for y in [1.40,2.12]: rod('Sofa foot',(x,y,.025),(x,y,.23),.037,dark)
box('Sofa lower body',(-.6,1.78,.32),(2.03,.95,.28),fabric,.1)
box('Sofa back',(-.6,2.14,.77),(2.03,.24,.8),fabric,.09)
for x in [-1.52,.32]: box('Sofa arm',(x,1.77,.62),(.22,.95,.55),fabric,.09)
for x in [-1.02,-.18]:
    box('Seat cushion',(x,1.68,.51),(.82,.73,.2),fabric,.08)
    o=box('Loose linen pillow',(x,1.96,.86),(.53,.19,.48),cushion,.075); o.rotation_euler.x=math.radians(12)
box('Area rug',(-.2,-.30,.043),(2.65,2.4,.022),rug,.045)
for x in [-1.38, .98]: box('Rug border',(x,-.30,.057),(.035,2.25,.003),cushion)
box('Rounded coffee tabletop',(-.35,.0,.47),(1.25,.66,.07),oak,.055)
for x in [-.83,.13]:
    for y in [-.23,.23]: rod('Coffee table leg',(x,y,.055),(x,y,.44),.027,dark)
book=box('Coffee table book',(-.53,.04,.523),(.36,.25,.032),trim,.005)
box('Book cover',(-.53,.04,.543),(.37,.26,.008),fabric,.003)
rod('Ceramic cup',(.03,.02,.507),(.03,.02,.61),.047,cream)
# Low media console at the open right side.
box('Console cabinet',(1.62,-.66,.42),(.57,1.64,.66),oak,.025)
for y in [-1.20,-.66,-.12]:
    box('Console drawer',(1.321,y,.44),(.022,.50,.49),trim,.007)
    rod('Drawer pull',(1.299,y-.08,.48),(1.299,y+.08,.48),.012,dark)
for y in [-1.30,-.02]:
    for x in [1.4,1.83]: rod('Console foot',(x,y,.03),(x,y,.15),.025,dark)
# Framed abstract art above sofa.
box('Picture frame',(-.65,2.471,1.98),(1.12,.06,.70),oak,.014)
box('Picture ground',(-.65,2.434,1.98),(1.01,.012,.59),cream)
box('Abstract ochre block',(-.87,2.424,1.96),(.34,.009,.42),rug)
box('Abstract green block',(-.40,2.423,2.06),(.41,.009,.24),fabric)
# Potted plant and articulated foliage.
bpy.ops.mesh.primitive_cone_add(vertices=40, radius1=.17, radius2=.23, depth=.39, location=(-1.52,-1.86,.225)); bpy.context.object.name='Plant pot'; bpy.context.object.data.materials.append(cream)
rod('Soil',(-1.52,-1.86,.41),(-1.52,-1.86,.425),.211,soil)
for i in range(11):
    ang=i*2.4; h=.62+(i%4)*.14
    end=Vector((-1.52+math.cos(ang)*.28,-1.86+math.sin(ang)*.28,h))
    rod('Plant stem',(-1.52,-1.86,.4),end,.009,green)
    bpy.ops.mesh.primitive_uv_sphere_add(segments=16, ring_count=8, location=end); o=bpy.context.object; o.name='Plant leaf'; o.scale=(.09,.035,.22); o.rotation_euler=(Vector((math.cos(ang),math.sin(ang),.8))).to_track_quat('Z','Y').to_euler(); o.data.materials.append(green)
light('Large soft key',(1,-3,6),750,5,(0,0,0))
light('Window daylight',(-3,.1,2.4),400,2,(0,.3,.4))
light('Warm rear fill',(1.4,3.5,4.0),300,3,(0,0,1))
scene=bpy.context.scene; scene.world.color=(.23,.23,.23)
bpy.ops.object.camera_add(location=(7,-9,7.3)); camera=bpy.context.object; camera.rotation_euler=(Vector((0,.15,1.0))-camera.location).to_track_quat('-Z','Y').to_euler(); camera.data.type='ORTHO'; camera.data.ortho_scale=8.3; scene.camera=camera
scene.unit_settings.system='METRIC'; scene.render.resolution_x=1400; scene.render.resolution_y=1200; scene.render.resolution_percentage=100
