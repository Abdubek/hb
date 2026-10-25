import bpy, math
from mathutils import Vector
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)

def mat(name, color, metallic=0, roughness=.5):
    m=bpy.data.materials.new(name); m.diffuse_color=(*color,1); m.use_nodes=True
    p=m.node_tree.nodes.get('Principled BSDF'); p.inputs['Base Color'].default_value=(*color,1); p.inputs['Metallic'].default_value=metallic; p.inputs['Roughness'].default_value=roughness
    return m
brick=mat('Warm brick',(.32,.115,.065)); mortar=mat('Mortar',(.34,.30,.25)); steel=mat('Painted iron',(.035,.055,.065),.75,.32); glass=mat('Blue window glass',(.055,.13,.18),.4,.2); trim=mat('Window stone',(.53,.48,.4)); ground=mat('Pavement',(.16,.18,.19))

def box(name,loc,scale,material,bevel=0):
    bpy.ops.mesh.primitive_cube_add(size=1,location=loc); o=bpy.context.object; o.name=name; o.dimensions=scale; bpy.ops.object.transform_apply(location=False,rotation=False,scale=True); o.data.materials.append(material)
    if bevel: m=o.modifiers.new('Edge highlights','BEVEL'); m.width=bevel; m.segments=2; o.modifiers.new('Weighted normals','WEIGHTED_NORMAL')
    return o

def rod(name,a,b,r=.025,material=steel):
    d=Vector(b)-Vector(a); bpy.ops.mesh.primitive_cylinder_add(vertices=12,radius=r,depth=d.length,location=(Vector(a)+Vector(b))/2); o=bpy.context.object; o.name=name; o.rotation_euler=d.to_track_quat('Z','Y').to_euler(); o.data.materials.append(material); return o

def beam(name,a,b,width=.1,height=.14):
    d=Vector(b)-Vector(a); o=box(name,(Vector(a)+Vector(b))/2,(width,height,d.length),steel,.015); o.rotation_euler=d.to_track_quat('Z','Y').to_euler(); return o

box('Sidewalk',(0,-1.4,-.18),(11,8,.35),ground,.06)
box('Building',(0,2,5.7),(8.5,3,11.4),brick,.025)
# Shallow mortar courses and staggered joints on the street-facing wall.
for row in range(42):
    z=.13+row*.27; box('Horizontal mortar',(0,.493,z),(8.5,.014,.018),mortar)
    for j in range(15):
        x=-4.2+j*.6+(row%2)*.3
        if x<4.25: box('Staggered joint',(x,.49,z+.135),(.018,.014,.25),mortar)
for z in (3,6,9):
    for x in (-2.65,0,2.65):
        box('Stone window surround',(x,.425,z+1.0),(1.35,.18,2.15),trim,.025)
        box('Recessed dark window',(x,.315,z+1.04),(1.12,.08,1.88),glass,.015)
        box('Window vertical mullion',(x,.255,z+1.04),(.045,.06,1.88),steel)
        box('Window crossbar',(x,.25,z+1.04),(1.12,.06,.045),steel)
        box('Projecting sill',(x,.28,z+.015),(1.52,.48,.12),trim,.02)
box('Cornice',(0,.3,11.32),(8.8,.65,.22),trim,.025)

# Balconies connect each flight to all three windows.
for z in (3,6,9):
    for y in (-.05,-.88): box('Balcony rim',(0,y,z-.10),(6.7,.10,.2),steel,.012)
    for i in range(68): box('Open balcony grating',(-3.3+i*.098,-.46,z),(.035,.83,.055),steel)
    for x in (-3.3,3.3):
        box('Landing frame',(x,-1.43,z-.09),(.12,2.0,.18),steel)
        for i in range(15): box('Landing open grating',(x+(.48 if x<0 else -.48),-.9-i*.10,z),(.95,.035,.055),steel)
        beam('Triangular wall bracket',(x,.4,z-1),(x,-2.38,z-.15),.085,.11)
        box('Wall anchor plate',(x,.365,z-.85),(.24,.1,.5),steel,.015)
        for zz in (z-.99,z-.71): rod('Anchor bolt',(x,.28,zz),(x,.20,zz),.045)
    # End rails leave the stair mouths open toward the flight.
    for x in (-3.36,3.36):
        for y in (-.05,-.8,-1.55,-2.4): rod('Landing post',(x,y,z),(x,y,z+1.05))
        rod('Landing top rail',(x,.05,z+1.05),(x,-2.4,z+1.05),.036)
        rod('Landing middle rail',(x,.05,z+.52),(x,-2.4,z+.52),.02)
    for x in (-1.8,-.9,0,.9,1.8): rod('Balcony guard post',(x,-.94,z),(x,-.94,z+1.05))
    rod('Balcony handrail',(-2.35,-.94,z+1.05),(2.35,-.94,z+1.05),.034)
    rod('Balcony midrail',(-2.35,-.94,z+.52),(2.35,-.94,z+.52),.022)

# Alternating flights: solid nosings with open-bar treads and twin stringers.
for floor in range(3):
    z0=floor*3; direction=1 if floor%2==0 else -1; x0=-2.85*direction; x1=2.85*direction
    for y in (-1.20,-2.32): beam('Diagonal channel stringer',(x0,y,z0-.10),(x1,y,z0+2.90),.12,.18)
    for i in range(18):
        t=(i+.5)/18; x=x0+(x1-x0)*t; z=z0+(i+1)/18*3
        box('Tread nosing',(x-direction*.135,-1.76,z),(.045,1.18,.07),steel,.006)
        for k in range(4): box('Open tread bar',(x-.105+k*.07,-1.76,z),(.027,1.16,.055),steel)
    for y in (-1.16,-2.38):
        for i in range(7):
            t=i/6; x=x0+(x1-x0)*t; z=z0+3*t
            rod('Stair baluster',(x,y,z),(x,y,z+1.02),.025)
        rod('Sloping handrail',(x0,y,z0+1.02),(x1,y,z0+4.02),.037)
        rod('Sloping intermediate rail',(x0,y,z0+.5),(x1,y,z0+3.5),.022)
for x in (-3.3,3.3):
    beam('Front support column',(x,-2.4,0),(x,-2.4,9),.13,.13)
    box('Column base plate',(x,-2.4,.035),(.36,.36,.07),steel,.01)

def area(loc,power,size):
    bpy.ops.object.light_add(type='AREA',location=loc); o=bpy.context.object; o.data.energy=power; o.data.shape='DISK'; o.data.size=size; o.rotation_euler=(Vector((0,0,5))-o.location).to_track_quat('-Z','Y').to_euler()
area((2,-9,15),2200,8); area((-8,-2,9),1300,7)
bpy.ops.object.camera_add(location=(14,-20,14)); cam=bpy.context.object; cam.rotation_euler=(Vector((0,-.4,5.3))-cam.location).to_track_quat('-Z','Y').to_euler(); cam.data.type='ORTHO'; cam.data.ortho_scale=17
scene=bpy.context.scene; scene.camera=cam; scene.world.color=(.22,.22,.22); scene.render.engine='CYCLES'; scene.render.resolution_x=1100; scene.render.resolution_y=1100; scene.render.resolution_percentage=100
