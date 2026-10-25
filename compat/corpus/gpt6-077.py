import bpy, math
from mathutils import Vector
bpy.ops.object.select_all(action='SELECT'); bpy.ops.object.delete(use_global=False)

def mat(name,c,metal=0,rough=.5):
    m=bpy.data.materials.new(name); m.diffuse_color=(*c,1); m.use_nodes=True; p=m.node_tree.nodes.get('Principled BSDF'); p.inputs['Base Color'].default_value=(*c,1); p.inputs['Metallic'].default_value=metal; p.inputs['Roughness'].default_value=rough; return m
concrete=mat('Cast concrete',(.43,.45,.43)); wall=mat('Warehouse blue gray',(.24,.31,.34),.25); zinc=mat('Galvanized door',(.63,.67,.66),.65,.35); dark=mat('Door recess',(.025,.035,.04)); rubber=mat('Black laminated rubber',(.025,.029,.03),0,.85); yellow=mat('Safety yellow',(.98,.57,.025),.25); steel=mat('Rail metal',(.14,.17,.18),.75); asphalt=mat('Asphalt',(.105,.12,.13),0,.95); white=mat('Paint markings',(.86,.84,.7)); red=mat('Red sign',(.58,.045,.028))

def box(name,loc,dims,m,bevel=0):
    bpy.ops.mesh.primitive_cube_add(size=1,location=loc); o=bpy.context.object; o.name=name; o.dimensions=dims; bpy.ops.object.transform_apply(location=False,rotation=False,scale=True); o.data.materials.append(m)
    if bevel: b=o.modifiers.new('Rounded edges','BEVEL'); b.width=bevel; b.segments=3; o.modifiers.new('Weighted normals','WEIGHTED_NORMAL')
    return o

def rod(name,a,b,r,m):
    d=Vector(b)-Vector(a); bpy.ops.mesh.primitive_cylinder_add(vertices=20,radius=r,depth=d.length,location=(Vector(a)+Vector(b))/2); o=bpy.context.object; o.name=name; o.rotation_euler=d.to_track_quat('Z','Y').to_euler(); o.data.materials.append(m)

def text(body,loc,size,m):
    bpy.ops.object.text_add(location=loc,rotation=(math.pi/2,0,0)); o=bpy.context.object; o.name=body; o.data.body=body; o.data.align_x='CENTER'; o.data.size=size; o.data.extrude=.001; o.data.materials.append(m)
box('Yard',(0,-2,-.12),(18,17,.24),asphalt,.025)
box('Warehouse mass',(0,3.7,3.65),(12,4,7.3),wall,.025)
for x in range(-6,7): box('Facade rib',(x,1.675,4.3),(.05,.065,5.8),zinc,.01)
box('Raised loading platform',(-.5,.05,.65),(9,3.3,1.3),concrete,.055)
box('Dock edge curb',(-.5,-1.59,1.27),(9,.12,.10),yellow,.01)
box('Door dark recess',(-1,1.60,3.25),(4.25,.18,4.0),dark,.015)
for x in (-3.18,1.18): box('Door jamb',(x,1.46,3.27),(.16,.22,4.15),zinc,.025)
box('Door lintel',(-1,1.46,5.32),(4.5,.24,.20),zinc,.02)
for i in range(8):
    z=1.56+i*.48
    box('Overhead door sectional panel',(-1,1.435,z),(4.05,.10,.455),zinc,.018)
    for x in (-2.5,-1.5,-.5,.5): box('Panel pressed recess',(x,1.377,z),(.86,.022,.30),wall,.022)
    for x in (-2.86,.86): box('Section hinge',(x,1.352,z+.22),(.09,.035,.13),steel,.009)
box('Bottom door weather seal',(-1,1.36,1.335),(4.1,.13,.07),rubber,.01)
rod('Door pull',(-1.3,1.23,1.85),(-.7,1.23,1.85),.025,steel)
for x in (-1.3,-.7): rod('Pull bracket',(x,1.23,1.85),(x,1.37,1.85),.025,steel)
box('Steel dock leveler',(-1,-.74,1.325),(2.45,1.5,.055),steel,.012)
box('Leveler hinged lip',(-1,-1.62,1.26),(2.45,.25,.12),steel,.01)
for x in (-2.7,.7):
    box('Bumper steel backing',(x,-1.67,.80),(.47,.16,.89),steel,.025)
    for i in range(11): box('Laminated bumper rubber',(x,-1.81,.43+i*.068),(.42,.24,.055),rubber,.01)
    for z in (.48,1.05): rod('Bumper mounting bolt',(x,-1.93,z),(x,-1.975,z),.035,zinc)
# A solid wedge ramp reaches the dock at its right-hand side.
x0,x1=4.0,5.9; ya,yb=-7.0,1.5; h=1.3
verts=[(x0,ya,0),(x1,ya,0),(x1,yb,0),(x0,yb,0),(x0,ya,.04),(x1,ya,.04),(x1,yb,h),(x0,yb,h)]
faces=[(0,3,2,1),(4,5,6,7),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7)]
mesh=bpy.data.meshes.new('Ramp wedge mesh'); mesh.from_pydata(verts,[],faces); mesh.update(); o=bpy.data.objects.new('Concrete access ramp',mesh); bpy.context.collection.objects.link(o); o.data.materials.append(concrete)
for y in (-6,-5,-4,-3,-2,-1,0,1):
    z=.04+(y-ya)/(yb-ya)*(h-.04)
    box('Ramp traction groove',(4.95,y,z+.003),(1.73,.025,.008),steel)
for x in (4.06,5.84):
    for i in range(7):
        t=i/6; y=ya+.3+t*(yb-ya-.5); z=.04+(y-ya)/(yb-ya)*(h-.04)
        rod('Ramp guard post',(x,y,z),(x,y,z+1.0),.035,yellow)
    for height in (.5,1.0): rod('Ramp sloping guard',(x,ya+.3,.04+.3/(yb-ya)*(h-.04)+height),(x,yb-.2,h-.2/(yb-ya)*(h-.04)+height),.035,yellow)
# Dock safety bollards and loading bay markings.
for x in (-3.6,1.6):
    rod('Safety bollard',(x,1.05,1.3),(x,1.05,2.45),.115,yellow)
    rod('Black bollard band',(x,1.05,2.1),(x,1.05,2.25),.117,rubber)
    box('Bollard mounting foot',(x,1.05,1.33),(.35,.35,.06),steel,.015)
for x in (-3.3,1.3): box('Truck bay stripe',(x,-5,.012),(.10,6,.015),white)
box('Dock identification plaque',(-1,1.38,5.95),(1.25,.10,.65),dark,.03); text('DOCK 02',(-1,1.318,5.83),.23,white)
box('Caution sign',(2.7,1.54,3.1),(.8,.07,.6),yellow,.018); text('CAUTION',(2.7,1.49,3.13),.14,dark); text('LOADING',(2.7,1.49,2.93),.12,dark)
box('Lamp hood',(-1,1.1,6.48),(1.5,.7,.15),steel,.035)
bpy.ops.object.light_add(type='AREA',location=(-1,1.05,6.36)); bpy.context.object.data.energy=80; bpy.context.object.data.size=1.1
for loc,power,size in [((1,-8,13),2300,8),((-8,-1,7),1200,6)]:
    bpy.ops.object.light_add(type='AREA',location=loc); o=bpy.context.object; o.data.energy=power; o.data.size=size; o.rotation_euler=(Vector((0,0,2))-o.location).to_track_quat('-Z','Y').to_euler()
bpy.ops.object.camera_add(location=(14,-20,13)); cam=bpy.context.object; cam.rotation_euler=(Vector((.3,-1.8,2.3))-cam.location).to_track_quat('-Z','Y').to_euler(); cam.data.type='ORTHO'; cam.data.ortho_scale=19
s=bpy.context.scene; s.camera=cam; s.world.color=(.2,.2,.2); s.render.engine='CYCLES'; s.render.resolution_x=1400; s.render.resolution_y=1000; s.render.resolution_percentage=100
