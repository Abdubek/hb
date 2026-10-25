import bpy, math
from mathutils import Vector
bpy.ops.wm.read_factory_settings(use_empty=True)

def mat(name, color, metal=0, rough=.5):
    m=bpy.data.materials.new(name); m.diffuse_color=(*color,1); m.use_nodes=True; p=m.node_tree.nodes.get('Principled BSDF'); p.inputs['Base Color'].default_value=(*color,1); p.inputs['Metallic'].default_value=metal; p.inputs['Roughness'].default_value=rough; return m

def box(name,loc,size,material,bevel=0):
    bpy.ops.mesh.primitive_cube_add(size=1,location=loc); o=bpy.context.object; o.name=name; o.dimensions=size; bpy.ops.object.transform_apply(location=False,rotation=False,scale=True); o.data.materials.append(material)
    if bevel:
        b=o.modifiers.new('Edge radii','BEVEL'); b.width=bevel; b.segments=3; o.modifiers.new('Weighted normals','WEIGHTED_NORMAL')
    return o

def rod(name,a,b,r,material,vertices=32):
    a,b=Vector(a),Vector(b); d=b-a; bpy.ops.mesh.primitive_cylinder_add(vertices=vertices,radius=r,depth=d.length,location=(a+b)/2); o=bpy.context.object; o.name=name; o.rotation_euler=d.to_track_quat('Z','Y').to_euler(); o.data.materials.append(material)
    for p in o.data.polygons: p.use_smooth=True
    return o

metal=mat('Graphite powder coated aluminum',(.065,.085,.105),.7,.31); steel=mat('Galvanized hardware',(.53,.59,.63),.85,.24); pave=mat('Light gray concrete',(.48,.50,.51),0,.9); curb=mat('Perimeter curb',(.30,.33,.35),0,.9); grout=mat('Recessed mortar joints',(.16,.18,.19),0,1); black=mat('Gaskets and seams',(.012,.019,.022),0,.66); lens=mat('Warm opal LED lens',(.94,.89,.71),0,.28)
p=lens.node_tree.nodes.get('Principled BSDF'); p.inputs['Emission Color'].default_value=(1,.83,.54,1); p.inputs['Emission Strength'].default_value=3
# A 2.4 m square pavement plinth with exposed curb thickness.
box('Square pavement base',(0,0,-.16),(2.4,2.4,.32),curb,.025)
box('Mortar bed',(0,0,.008),(2.26,2.26,.025),grout)
for i in range(4):
    for j in range(4): box('Pavement tile',(-.84+i*.56,-.84+j*.56,.032),(.551,.551,.048),pave,.006)
# Service foundation and four visible anchor bolts.
box('Foundation pad',(0,0,.07),(.57,.57,.10),pave,.014)
box('Steel base flange',(0,0,.14),(.40,.40,.055),metal,.02)
for x in [-.145,.145]:
    for y in [-.145,.145]:
        rod('Anchor washer',(x,y,.167),(x,y,.176),.028,steel)
        rod('Hex anchor nut',(x,y,.177),(x,y,.204),.021,steel,6)
        rod('Threaded stud',(x,y,.202),(x,y,.216),.011,steel)
# Tapered five meter pole, smaller toward its top.
bpy.ops.mesh.primitive_cone_add(vertices=64,radius1=.108,radius2=.062,depth=4.8,location=(0,0,2.57)); pole=bpy.context.object; pole.name='Tapered streetlight mast'; pole.data.materials.append(metal)
for p in pole.data.polygons: p.use_smooth=True
rod('Base collar',(0,0,.17),(0,0,.29),.122,metal)
box('Service hatch seal',(0,-.108,.65),(.13,.012,.38),black,.025)
box('Service hatch',(0,-.119,.65),(.114,.014,.357),metal,.022)
for z in [.51,.79]: rod('Hatch screw',(0,-.128,z),(0,-.136,z),.008,steel,12)
rod('Top cap',(0,0,4.953),(0,0,4.995),.07,metal)
# Swept curved arm, tangentially joined to the mast.
points=[(0,0,4.76),(0,0,4.96)]
for i in range(1,17):
    a=math.pi-i*(math.pi/2)/16
    points.append((.27+.27*math.cos(a),0,4.96+.27*math.sin(a)))
points.extend([(.74,0,5.23),(.96,0,5.23)])
c=bpy.data.curves.new('Swept arm','CURVE'); c.dimensions='3D'; c.bevel_depth=.045; c.bevel_resolution=5; c.use_fill_caps=True; s=c.splines.new('POLY'); s.points.add(len(points)-1)
for p,co in zip(s.points,points): p.co=(*co,1)
o=bpy.data.objects.new('Curved luminaire arm',c); bpy.context.collection.objects.link(o); o.data.materials.append(metal)
rod('Arm mounting sleeve',(.79,0,5.23),(.98,0,5.23),.058,steel)
# Flat modern LED head with gasket, recessed optical panel, fins and screws.
box('Slim luminaire housing',(1.12,0,5.205),(.82,.32,.13),metal,.055)
box('Lens perimeter gasket',(1.17,0,5.138),(.62,.255,.012),black,.03)
box('Recessed opal diffuser',(1.17,0,5.13),(.57,.218,.014),lens,.023)
for i in range(7): box('Top cooling rib',(.94+i*.075,0,5.281),(.022,.225,.025),metal,.007)
for x in [.84,1.48]:
    for y in [-.114,.114]: rod('Housing screw',(x,y,5.13),(x,y,5.14),.009,steel,12)
rod('Photocell base',(.84,0,5.27),(.84,0,5.312),.033,black)
# The LED fixture casts a soft pool of warm light.
bpy.ops.object.light_add(type='AREA',location=(1.17,0,5.105)); led=bpy.context.object; led.name='Streetlight LED illumination'; led.data.energy=190; led.data.color=(1,.80,.52); led.data.shape='RECTANGLE'; led.data.size=.5; led.data.size_y=.19
scene=bpy.context.scene; scene.world.color=(.13,.16,.21)
for loc,power,size in [((3,-4,7),850,5),((-4,1,5),650,4),((2,4,6),900,3)]:
    bpy.ops.object.light_add(type='AREA',location=loc); o=bpy.context.object; o.data.energy=power; o.data.size=size; o.rotation_euler=(Vector((0,0,2.5))-o.location).to_track_quat('-Z','Y').to_euler()
bpy.ops.object.camera_add(location=(8,-11,8)); cam=bpy.context.object; cam.rotation_euler=(Vector((.25,0,2.45))-cam.location).to_track_quat('-Z','Y').to_euler(); cam.data.type='ORTHO'; cam.data.ortho_scale=6.7; scene.camera=cam
scene.unit_settings.system='METRIC'; scene.render.resolution_x=1050; scene.render.resolution_y=1500; scene.render.resolution_percentage=100
