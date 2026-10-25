import bpy, math, random
from mathutils import Vector
bpy.ops.wm.read_factory_settings(use_empty=True)
random.seed(12)

def mat(name,c,metal=0,rough=0.5):
    m=bpy.data.materials.new(name); m.diffuse_color=(*c,1); m.use_nodes=True
    p=m.node_tree.nodes.get('Principled BSDF'); p.inputs['Base Color'].default_value=(*c,1); p.inputs['Metallic'].default_value=metal; p.inputs['Roughness'].default_value=rough; return m

def box(name,loc,size,m,bevel=0.025):
    bpy.ops.mesh.primitive_cube_add(size=1,location=loc); o=bpy.context.object; o.name=name; o.dimensions=size; bpy.ops.object.transform_apply(location=False,rotation=False,scale=True); o.data.materials.append(m)
    if bevel:
        b=o.modifiers.new('Edge rounding','BEVEL'); b.width=bevel; b.segments=2; o.modifiers.new('Normals','WEIGHTED_NORMAL')
    return o

def rod(name,a,b,r,m):
    d=Vector(b)-Vector(a); bpy.ops.mesh.primitive_cylinder_add(vertices=20,radius=r,depth=d.length,location=(Vector(a)+Vector(b))/2); o=bpy.context.object; o.name=name; o.rotation_euler=d.to_track_quat('Z','Y').to_euler(); o.data.materials.append(m); return o

def text(name,body,loc,size,m):
    cu=bpy.data.curves.new(name,'FONT'); cu.body=body; cu.align_x='CENTER'; cu.align_y='CENTER'; cu.size=size; cu.extrude=0.002
    o=bpy.data.objects.new(name,cu); bpy.context.collection.objects.link(o); o.location=loc; o.rotation_euler=(math.pi/2,0,0); o.data.materials.append(m); return o

wood=mat('Honey pine',(0.49,0.29,0.12)); edge=mat('Dark timber',(0.26,0.13,0.055)); cream=mat('Canvas cream',(0.96,0.89,0.69)); green=mat('Canvas forest',(0.13,0.32,0.20)); iron=mat('Black iron',(0.045,0.055,0.05),0.7); chalk=mat('Chalk',(0.94,0.92,0.79)); board=mat('Chalkboard',(0.027,0.065,0.049)); red=mat('Tomato red',(0.68,0.045,0.019),rough=0.32); yellow=mat('Golden pears',(0.83,0.57,0.08)); apple=mat('Green apples',(0.34,0.57,0.055)); stem=mat('Stems',(0.18,0.10,0.035)); ground=mat('Paving',(0.43,0.42,0.37))
box('Street foundation',(0,0,-0.13),(200,200,0.20),ground,0)
for ix in range(-5,6):
    for iy in range(-4,5): box('Paving stone',(ix*0.69+(iy%2)*0.345,iy*0.52,-0.015),(0.67,0.50,0.045),ground,0.012)
for x in [-1.70,1.70]:
    for y in [-0.80,0.80]:
        box('Canopy post',(x,y,1.40),(0.09,0.09,2.80),edge)
        box('Post foot',(x,y,0.09),(0.16,0.16,0.16),iron)
        rod('Diagonal brace',(x,y,2.27),(x-math.copysign(0.35,x),y,2.66),0.035,wood)
rod('Ridge pole',(-1.85,0,3.20),(1.85,0,3.20),0.04,iron)
for y in [-0.94,0.94]: rod('Eave pole',(-1.87,y,2.73),(1.87,y,2.73),0.035,iron)
# Alternating fabric strips across a pitched roof, with a soft sag between supports.
for i in range(12):
    x0=-1.92+i*0.32; x1=x0+0.32; verts=[]
    for x in [x0,x1]:
        for j in range(17):
            y=-1.04+j*2.08/16; z=3.22-0.49*abs(y)-0.045*math.sin(math.pi*abs(y)/1.04)
            verts.append((x,y,z))
    faces=[(j,j+1,17+j+1,17+j) for j in range(16)]
    me=bpy.data.meshes.new('Canvas strip'); me.from_pydata(verts,[],faces); me.update(); o=bpy.data.objects.new('Striped canopy',me); bpy.context.collection.objects.link(o); o.data.materials.append(green if i%2==0 else cream)
    s=o.modifiers.new('Fabric thickness','SOLIDIFY'); s.thickness=0.012
    for y in [-1.04,1.04]:
        vv=[(x0,y,2.71),(x1,y,2.71)]+[(x1-k*0.32/8,y,2.51-0.065*math.sin(math.pi*k/8)) for k in range(9)]
        mm=bpy.data.meshes.new('Scallop'); mm.from_pydata(vv,[],[tuple(range(len(vv)))]); mm.update(); ob=bpy.data.objects.new('Scalloped valance',mm); bpy.context.collection.objects.link(ob); ob.data.materials.append(green if i%2==0 else cream); so=ob.modifiers.new('Hem thickness','SOLIDIFY'); so.thickness=0.01
# Counter with visible plank frontage.
for x in [-1.48,1.48]:
    for y in [-0.52,0.52]: box('Counter leg',(x,y,0.53),(0.12,0.12,1.04),edge)
box('Counter top',(0,0,1.06),(3.30,1.36,0.13),wood)
for i in range(15): box('Front plank',(-1.54+i*0.22,-0.585,0.62),(0.207,0.07,0.76),wood,0.008)
for z in [0.30,0.93]: box('Front rail',(0,-0.632,z),(3.24,0.06,0.095),edge)

def crate(name,cx,cy,z,w=0.91,d=0.88):
    box(name+' floor',(cx,cy,z+0.025),(w,d,0.05),wood,0.008)
    for sx in [-1,1]:
        for sy in [-1,1]: box(name+' corner',(cx+sx*(w/2-0.04),cy+sy*(d/2-0.04),z+0.20),(0.065,0.065,0.39),edge,0.008)
    for k in range(3):
        zz=z+0.09+k*0.12
        for sy in [-1,1]: box(name+' long slat',(cx,cy+sy*d/2,zz),(w,0.045,0.083),wood,0.008)
        for sx in [-1,1]: box(name+' end slat',(cx+sx*w/2,cy,zz),(0.045,d,0.083),wood,0.008)

def fruit(kind,loc,m):
    bpy.ops.mesh.primitive_uv_sphere_add(segments=16,ring_count=10,radius=0.105,location=loc); o=bpy.context.object; o.name=kind
    o.scale=(1,0.95,0.88) if kind=='Tomato' else ((0.90,0.90,1.25) if kind=='Pear' else (1,1,1))
    o.data.materials.append(m)
    for p in o.data.polygons: p.use_smooth=True
    top=loc[2]+(0.125 if kind=='Pear' else 0.095)
    rod('Fruit stem',(loc[0],loc[1],top-0.01),(loc[0]+0.013,loc[1],top+0.045),0.009,stem)
    if kind=='Tomato':
        for a in range(5):
            ang=a*math.tau/5; rod('Tomato calyx',(loc[0],loc[1],top),(loc[0]+0.05*math.cos(ang),loc[1]+0.05*math.sin(ang),top-0.014),0.009,green)
for index,(cx,kind,m) in enumerate([(-1.06,'Tomato',red),(0,'Pear',yellow),(1.06,'Apple',apple)]):
    crate('Produce crate',cx,0,1.135)
    for row in range(3):
        for col in range(4): fruit(kind,(cx-0.32+col*0.21+random.uniform(-0.018,0.018),-0.27+row*0.25,1.37+random.uniform(-0.012,0.02)),m)
    for col in range(3): fruit(kind,(cx-0.22+col*0.22,0.02,1.53),m)
    box('Price placard',(cx,-0.485,1.45),(0.51,0.025,0.22),board,0.012)
    text('Produce label',kind.upper()+'  $3',(cx,-0.503,1.45),0.075,chalk)
crate('Spare crate',2.18,0.25,0.03,0.76,0.75)
crate('Stacked spare crate',2.18,0.25,0.43,0.76,0.75)
box('Market sign',(0,-0.88,2.27),(1.90,0.07,0.33),edge)
text('Market name','FARM & FIELD',(0,-0.924,2.27),0.21,cream)
for x in [-0.72,0.72]: rod('Sign hanger',(x,-0.85,2.70),(x,-0.85,2.43),0.011,iron)
box('Sidewalk sign',(2.04,-1.15,0.65),(0.69,0.085,0.98),wood)
box('Sign blackboard',(2.04,-1.201,0.67),(0.59,0.025,0.80),board)
text('Sidewalk lettering','FRESH\nLOCAL\nDAILY',(2.04,-1.222,0.69),0.13,chalk)
for x in [1.78,2.30]: rod('Sign rear leg',(x,-1.10,1.07),(x,-0.57,0.04),0.033,edge)
world=bpy.data.worlds.new('Daylight'); bpy.context.scene.world=world; world.use_nodes=True; world.node_tree.nodes['Background'].inputs[0].default_value=(0.75,0.82,0.90,1); world.node_tree.nodes['Background'].inputs[1].default_value=0.65
bpy.ops.object.light_add(type='AREA',location=(-3,-4,7)); bpy.context.object.data.energy=1300; bpy.context.object.data.size=5
bpy.ops.object.camera_add(location=(6,-8,5.2)); cam=bpy.context.object; cam.rotation_euler=(Vector((0.25,0,1.4))-cam.location).to_track_quat('-Z','Y').to_euler(); cam.data.type='ORTHO'; cam.data.ortho_scale=6.9
scene=bpy.context.scene; scene.camera=cam; scene.render.engine='CYCLES'; scene.cycles.samples=64; scene.render.resolution_x=1200; scene.render.resolution_y=1050; scene.render.resolution_percentage=100
