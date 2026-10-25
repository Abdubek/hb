import bpy, math
from mathutils import Vector
bpy.ops.object.select_all(action='SELECT'); bpy.ops.object.delete(use_global=False)

def mat(name,c,metal=0,rough=.55):
    m=bpy.data.materials.new(name); m.diffuse_color=(*c,1); m.use_nodes=True; p=m.node_tree.nodes['Principled BSDF']; p.inputs['Base Color'].default_value=(*c,1); p.inputs['Metallic'].default_value=metal; p.inputs['Roughness'].default_value=rough; return m
steel=mat('Deep teal bridge steel',(.035,.21,.23),.7,.3); silver=mat('Stainless hardware',(.52,.58,.58),.8,.25); deck=mat('Warm timber decking',(.43,.29,.16)); concrete=mat('Abutment concrete',(.57,.56,.49)); roof=mat('Portal folded metal roof',(.71,.39,.13),.6,.34)
land=mat('Grassed banks',(.28,.36,.16)); water=mat('River water',(.08,.27,.29),.3,.22); path=mat('Approach gravel',(.52,.48,.38)); dark=mat('Portal sign background',(.055,.10,.11)); white=mat('Sign lettering',(.87,.88,.77))

def box(name,loc,size,m,bev=0):
    bpy.ops.mesh.primitive_cube_add(size=1,location=loc); o=bpy.context.object; o.name=name; o.dimensions=size; bpy.ops.object.transform_apply(location=False,rotation=False,scale=True); o.data.materials.append(m)
    if bev:
        b=o.modifiers.new('Fabrication edge radius','BEVEL'); b.width=bev; b.segments=2; o.modifiers.new('Weighted normals','WEIGHTED_NORMAL')
    return o

def beam(name,a,b,w,d,m):
    a,b=Vector(a),Vector(b); o=box(name,(a+b)/2,(w,d,(b-a).length),m,.012); o.rotation_euler=(b-a).to_track_quat('Z','Y').to_euler(); return o

def bolt(name,loc,axis='Y'):
    rot=(math.pi/2,0,0) if axis=='Y' else (0,0,0)
    bpy.ops.mesh.primitive_cylinder_add(vertices=6,radius=.049,depth=.045,location=loc,rotation=rot); o=bpy.context.object; o.name=name; o.data.materials.append(silver)

def panel(name,verts,faces,m,thickness=.06):
    me=bpy.data.meshes.new(name); me.from_pydata(verts,[],faces); me.update(); o=bpy.data.objects.new(name,me); bpy.context.collection.objects.link(o); o.data.materials.append(m); s=o.modifiers.new('Sheet thickness','SOLIDIFY'); s.thickness=thickness; return o

box('River bed',(0,0,-1.1),(38,26,.4),concrete)
box('River surface',(0,0,-.65),(20.7,26,.08),water)
for side in (-1,1):
    box('Raised landscaped bank',(side*15.8,0,-.17),(10.7,26,1.55),land,.25)
    box('Approach path',(side*16.2,0,.64),(10,3.4,.08),path,.03)
    box('Concrete bridge abutment',(side*10.5,0,.35),(1.7,5.6,1.75),concrete,.09)
    box('Abutment bearing ledge',(side*10.35,0,1.16),(1.9,5.8,.22),concrete,.045)
    for y in (-1.9,1.9):
        box('Elastomer bearing pad',(side*10.4,y,1.33),(.52,.44,.14),dark,.025)
        box('Steel bearing plate',(side*10.4,y,1.43),(.68,.55,.06),silver,.012)
# Six repeating 3.5 m truss modules over a clear river span.
for y in (-1.92,1.92):
    for j in range(6):
        xa=-10.5+j*3.5; xb=xa+3.5
        beam('Module lower chord',(xa,y,1.59),(xb,y,1.59),.20,.23,steel)
        beam('Module upper chord',(xa,y,4.29),(xb,y,4.29),.18,.20,steel)
        beam('Warren truss rising diagonal',(xa,y,1.59),((xa+xb)/2,y,4.29),.15,.17,steel)
        beam('Warren truss falling diagonal',((xa+xb)/2,y,4.29),(xb,y,1.59),.15,.17,steel)
        # Bolted gusset plates explicitly mark the modular connections.
        for x,z in ((xa,1.59),((xa+xb)/2,4.29)):
            outward=y+(.135 if y>0 else -.135)
            panel('Triangular connection gusset',[(x-.24,outward,z-.15),(x+.24,outward,z-.15),(x,outward,z+.27)],[(0,1,2)],steel,.035)
            for dx,dz in ((-.11,-.065),(.11,-.065),(0,.13)): bolt('Gusset hex bolt',(x+dx,outward+(.04 if y>0 else -.04),z+dz))
    for j in range(7):
        x=-10.5+j*3.5
        beam('Module boundary upright',(x,y,1.59),(x,y,4.29),.13,.15,steel)
        box('Chord splice plate',(x,y+(.145 if y>0 else -.145),4.29),(.55,.05,.28),silver,.015)
        for dx in (-.19,.19): bolt('Splice bolt',(x+dx,y+(.18 if y>0 else -.18),4.29))
# Cross girders and bracing below the pedestrian deck.
for j in range(13):
    x=-10.5+j*1.75
    beam('Deck transverse floor beam',(x,-2.02,1.49),(x,2.02,1.49),.14,.23,steel)
for j in range(6):
    x=-10.5+j*3.5
    beam('Under deck cross brace A',(x,-1.85,1.34),(x+3.5,1.85,1.34),.055,.065,silver)
    beam('Under deck cross brace B',(x,1.85,1.34),(x+3.5,-1.85,1.34),.055,.065,silver)
for i in range(120): box('Deck transverse timber board',(-10.42+i*.175,0,1.77),(.163,3.6,.15),deck,.009)
# Closely spaced pedestrian balusters inside the structural trusses.
for y in (-1.72,1.72):
    beam('Continuous pedestrian handrail',(-10.5,y,2.95),(10.5,y,2.95),.075,.075,silver)
    beam('Guard lower rail',(-10.5,y,1.96),(10.5,y,1.96),.055,.055,steel)
    for i in range(151):
        x=-10.5+i*.14; beam('Slender guard baluster',(x,y,1.96),(x,y,2.91),.025,.025,steel)
# Covered entry portals stand on both abutments, with pitched angular roofs.
for side in (-1,1):
    cx=side*11.45
    box('Portal entry landing',(cx,0,1.69),(2.0,3.7,.30),deck,.025)
    for x in (cx-1,cx+1):
        for y in (-2.22,2.22):
            box('Portal column',(x,y,3.1),(.19,.19,3.4),steel,.02)
            box('Portal base plate',(x,y,1.45),(.40,.40,.08),silver,.018)
            for dx in (-.13,.13):
                for dy in (-.13,.13): bolt('Anchor bolt',(x+dx,y+dy,1.51),'Z')
        beam('Portal left roof rafter',(x,-2.65,4.65),(x,0,5.48),.16,.20,steel)
        beam('Portal right roof rafter',(x,0,5.48),(x,2.65,4.65),.16,.20,steel)
        for y in (-2.22,2.22): beam('Portal knee brace',(x,y,3.95),(x,y*.64,4.87),.10,.12,steel)
    verts=[(cx-1.35,-2.75,4.70),(cx+1.35,-2.75,4.70),(cx+1.35,0,5.55),(cx-1.35,0,5.55),(cx-1.35,2.75,4.70),(cx+1.35,2.75,4.70)]
    panel('Portal folded canopy',verts,[(0,1,2,3),(3,2,5,4)],roof,.09)
    for y in (-2.65,0,2.65):
        z=5.55-abs(y)*(.85/2.75); beam('Portal canopy seam',(cx-1.35,y,z+.04),(cx+1.35,y,z+.04),.035,.035,roof)
    # Broad shallow approach ramp aligns the bank path and elevated bridge deck.
    inner=side*12.45; outer=side*18.45
    vertices=[(inner,-1.8,1.84),(inner,1.8,1.84),(outer,1.8,.69),(outer,-1.8,.69)]
    panel('Accessible approach ramp',vertices,[(0,1,2,3)],concrete,.2)
    for y in (-1.87,1.87):
        beam('Approach ramp handrail',(inner,y,2.9),(outer,y,1.75),.065,.065,silver)
        for i in range(5):
            t=i/4; x=inner+(outer-inner)*t; z=1.84-1.15*t
            beam('Approach railing post',(x,y,z),(x,y,z+1.06),.055,.055,steel)
    # Side-facing identification plaque reads clearly from the presentation camera.
    box('Portal name plaque',(cx,-2.35,4.10),(1.75,.09,.42),dark,.025)
    c=bpy.data.curves.new('Bridge lettering','FONT'); c.body='RIVER WALK'; c.align_x='CENTER'; c.size=.19; c.extrude=.002
    o=bpy.data.objects.new('Portal lettering',c); bpy.context.collection.objects.link(o); o.location=(cx,-2.405,4.025); o.rotation_euler=(math.pi/2,0,0); o.data.materials.append(white)
scene=bpy.context.scene; scene.render.engine='CYCLES'; scene.cycles.samples=64; scene.world.color=(.36,.40,.42)
bpy.ops.object.light_add(type='AREA',location=(0,-10,18)); bpy.context.object.data.energy=2600; bpy.context.object.data.size=12
bpy.ops.object.light_add(type='SUN'); bpy.context.object.rotation_euler=(.5,-.4,-.5); bpy.context.object.data.energy=2.3; bpy.context.object.data.angle=.16
bpy.ops.object.camera_add(location=(27,-34,22)); cam=bpy.context.object; cam.rotation_euler=(Vector((0,0,1.8))-cam.location).to_track_quat('-Z','Y').to_euler(); cam.data.type='ORTHO'; cam.data.ortho_scale=43; scene.camera=cam
scene.render.resolution_x=1600; scene.render.resolution_y=1000; scene.render.resolution_percentage=100
