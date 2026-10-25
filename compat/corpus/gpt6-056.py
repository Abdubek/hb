import bpy, math
from mathutils import Vector
bpy.ops.wm.read_factory_settings(use_empty=True)

def mat(name, color, metal=0.0, rough=0.45):
    m=bpy.data.materials.new(name); m.diffuse_color=(*color,1); m.use_nodes=True
    p=m.node_tree.nodes.get('Principled BSDF'); p.inputs['Base Color'].default_value=(*color,1); p.inputs['Metallic'].default_value=metal; p.inputs['Roughness'].default_value=rough
    return m

def mesh(name, verts, faces, material):
    me=bpy.data.meshes.new(name); me.from_pydata(verts,[],faces); me.update()
    ob=bpy.data.objects.new(name,me); bpy.context.collection.objects.link(ob); ob.data.materials.append(material); return ob

def box(name, loc, size, material, bevel=0.03):
    bpy.ops.mesh.primitive_cube_add(size=1,location=loc); o=bpy.context.object; o.name=name; o.dimensions=size
    bpy.ops.object.transform_apply(location=False,rotation=False,scale=True); o.data.materials.append(material)
    if bevel:
        m=o.modifiers.new('Soft edges','BEVEL'); m.width=bevel; m.segments=3
        o.modifiers.new('Weighted normals','WEIGHTED_NORMAL')
    return o

def rod(name, a, b, radius, material, vertices=24):
    d=Vector(b)-Vector(a); bpy.ops.mesh.primitive_cylinder_add(vertices=vertices,radius=radius,depth=d.length,location=(Vector(a)+Vector(b))/2)
    o=bpy.context.object; o.name=name; o.rotation_euler=d.to_track_quat('Z','Y').to_euler(); o.data.materials.append(material)
    for p in o.data.polygons: p.use_smooth=True
    return o

def rope(name, points, radius, material):
    cu=bpy.data.curves.new(name,'CURVE'); cu.dimensions='3D'; cu.bevel_depth=radius; cu.bevel_resolution=3
    s=cu.splines.new('POLY'); s.points.add(len(points)-1)
    for p,co in zip(s.points,points): p.co=(*co,1)
    o=bpy.data.objects.new(name,cu); bpy.context.collection.objects.link(o); o.data.materials.append(material)

navy=mat('Deep marine blue',(0.025,0.10,0.17)); wood=mat('Teak',(0.48,0.25,0.10)); pale=mat('Ivory trim',(0.88,0.85,0.72)); cloth=mat('Warm sailcloth',(0.94,0.92,0.80),rough=0.85)
metal=mat('Brushed aluminum',(0.52,0.60,0.64),0.8); dark=mat('Cockpit shadow',(0.035,0.05,0.055)); line=mat('Rigging',(0.24,0.22,0.18)); sea=mat('Blue water',(0.045,0.26,0.34),0.2,0.23)
# Closed hull: longitudinal stations and a six-point cross section.
stations=[(-2.35,0.025),(-1.90,0.48),(-1.1,0.79),(0.0,0.88),(1.05,0.73),(1.90,0.50),(2.05,0.42)]
verts=[]
for x,w in stations:
    bottom=-0.38+0.38*(abs(x)/2.4)**2
    verts.extend([(x,-w,0.64),(x,w,0.64),(x,w*0.93,0.28),(x,w*0.48,bottom),(x,-w*0.48,bottom),(x,-w*0.93,0.28)])
faces=[]
for i in range(len(stations)-1):
    for j in range(6): faces.append((i*6+j,i*6+(j+1)%6,(i+1)*6+(j+1)%6,(i+1)*6+j))
faces.extend([tuple(reversed(range(6))),tuple(range((len(stations)-1)*6,len(stations)*6))])
hull=mesh('Hull',verts,faces,navy)
# Recalculate the hull normals for the station winding.
bpy.context.view_layer.objects.active=hull; hull.select_set(True)
import bmesh
bm=bmesh.new(); bm.from_mesh(hull.data); bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces)); bm.to_mesh(hull.data); bm.free(); hull.select_set(False)
bev=hull.modifiers.new('Rounded chines','BEVEL'); bev.width=0.055; bev.segments=3; hull.modifiers.new('Hull normals','WEIGHTED_NORMAL')
deckverts=[(x,-w*0.96,0.665) for x,w in stations]+[(x,w*0.96,0.665) for x,w in reversed(stations)]
mesh('Teak deck',deckverts,[tuple(range(len(deckverts)))],wood)
for side in [-1,1]:
    rope('Ivory gunwale',[(x,side*w,0.70) for x,w in stations],0.038,pale)
    rope('Hull accent stripe',[(x,side*w*0.99,0.49) for x,w in stations],0.014,pale)
box('Cockpit inset',(0.98,0,0.69),(1.45,0.91,0.035),dark,0.09)
for y in [-0.43,0.43]: box('Cockpit seat',(1.0,y,0.77),(1.43,0.20,0.14),wood)
box('Cockpit aft coaming',(1.72,0,0.79),(0.14,0.93,0.19),pale)
box('Forward hatch',(-1.40,0,0.70),(0.48,0.48,0.06),pale)
box('Hatch glass',(-1.40,0,0.735),(0.38,0.38,0.02),navy)
rod('Mast',(-0.48,0,0.67),(-0.48,0,4.9),0.052,metal)
rod('Boom',(-0.48,0,1.32),(1.78,0,1.32),0.046,metal)
# Slightly billowed main and jib sails; solidify makes both sides visible.
def sail(name, corners, bulge):
    c=sum((Vector(v) for v in corners),Vector())/3; c.y+=bulge
    o=mesh(name,corners+[tuple(c)],[(0,1,3),(1,2,3),(2,0,3)],cloth)
    s=o.modifiers.new('Cloth thickness','SOLIDIFY'); s.thickness=0.009
    rope(name+' perimeter',corners+[corners[0]],0.012,pale)
    return o
sail('Mainsail',[(-0.40,0.035,4.72),(-0.40,0.035,1.43),(1.66,0.035,1.43)],0.20)
sail('Jib',[(-0.58,-0.035,4.57),(-2.19,-0.035,0.91),(-0.67,-0.035,1.45)],-0.13)
for z in [2.05,2.72,3.40]:
    endx=-0.40+2.06*(4.72-z)/(4.72-1.43)
    rope('Sail seam',[(-0.40,0.045,z),((endx-0.4)/2,0.13,z),(endx,0.045,z)],0.005,wood)
rope('Forestay',[(-2.25,0,0.72),(-0.48,0,4.86)],0.012,line)
for y in [-0.71,0.71]: rope('Shroud',[(-0.17,y,0.72),(-0.48,0,4.67)],0.011,line)
rope('Mainsheet',[(1.60,0,1.30),(1.33,-0.25,0.81),(1.63,0.02,1.28)],0.015,line)
for x in [-1.82,1.66]:
    for y in [-0.30,0.30]:
        rod('Cleat base',(x,y,0.69),(x,y,0.76),0.025,metal)
        rod('Cleat',(x-0.10,y,0.77),(x+0.10,y,0.77),0.021,metal)
box('Rudder',(2.10,0,-0.10),(0.27,0.10,0.85),wood)
rod('Tiller',(2.08,0,0.75),(1.25,0.08,0.92),0.035,wood)
box('Water',(0,0,-0.31),(200,200,0.10),sea,0)
# Small quiet ripples around the hull.
for side in [-1,1]:
    for i in range(3):
        points=[(-2.5+j*0.20,side*(0.80+i*0.19+0.08*math.sin(j*0.4)),-0.253) for j in range(28)]
        rope('Water ripple',points,0.007,mat('Ripple '+str(side)+' '+str(i),(0.14,0.39,0.43),rough=0.35))
world=bpy.data.worlds.new('Sky'); bpy.context.scene.world=world; world.use_nodes=True; world.node_tree.nodes['Background'].inputs[0].default_value=(0.65,0.77,0.86,1); world.node_tree.nodes['Background'].inputs[1].default_value=0.65
bpy.ops.object.light_add(type='AREA',location=(-3,-4,8)); bpy.context.object.data.energy=1600; bpy.context.object.data.shape='DISK'; bpy.context.object.data.size=6
bpy.ops.object.camera_add(location=(7,-10,6.5)); cam=bpy.context.object; cam.rotation_euler=(Vector((0,0,2.0))-cam.location).to_track_quat('-Z','Y').to_euler(); cam.data.type='ORTHO'; cam.data.ortho_scale=8.5
scene=bpy.context.scene; scene.camera=cam; scene.render.engine='CYCLES'; scene.cycles.samples=64; scene.render.resolution_x=1100; scene.render.resolution_y=1100; scene.render.resolution_percentage=100
