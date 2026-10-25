import bpy, math
from mathutils import Vector
bpy.ops.object.select_all(action='SELECT'); bpy.ops.object.delete(use_global=False)

def mat(name,c,metal=0,rough=0.5):
    m=bpy.data.materials.new(name); m.diffuse_color=(*c,1); m.use_nodes=True
    p=m.node_tree.nodes.get('Principled BSDF'); p.inputs['Base Color'].default_value=(*c,1); p.inputs['Metallic'].default_value=metal; p.inputs['Roughness'].default_value=rough
    return m
frame=mat('Graphite powder-coated aluminum',(0.065,0.085,0.095),0.65,0.33)
cloth=mat('Forest green woven canvas',(0.11,0.23,0.16),0,0.88)
trim=mat('Dark canvas binding',(0.035,0.075,0.05),0,0.8)
rubber=mat('Rubber feet',(0.025,0.03,0.027),0,0.85)
metal=mat('Zinc hardware',(0.55,0.60,0.63),0.8,0.25)
stitch=mat('Khaki stitching',(0.48,0.53,0.34),0,0.85)
ground=mat('Warm studio',(0.25,0.24,0.20),0,0.85)
p=cloth.node_tree.nodes.get('Principled BSDF'); noise=cloth.node_tree.nodes.new('ShaderNodeTexNoise'); noise.inputs['Scale'].default_value=190; noise.inputs['Detail'].default_value=2
bump=cloth.node_tree.nodes.new('ShaderNodeBump'); bump.inputs['Strength'].default_value=0.22; bump.inputs['Distance'].default_value=0.008; cloth.node_tree.links.new(noise.outputs['Fac'],bump.inputs['Height']); cloth.node_tree.links.new(bump.outputs['Normal'],p.inputs['Normal'])

def box(name,loc,dim,m,b=0.02):
    bpy.ops.mesh.primitive_cube_add(size=1,location=loc); o=bpy.context.object; o.name=name; o.dimensions=dim; bpy.ops.object.transform_apply(location=False,rotation=False,scale=True); o.data.materials.append(m)
    if b:
        q=o.modifiers.new('Rounded edges','BEVEL'); q.width=b; q.segments=3; o.modifiers.new('Weighted normals','WEIGHTED_NORMAL')
    return o

def rod(name,a,b,r,m):
    a,b=Vector(a),Vector(b); bpy.ops.mesh.primitive_cylinder_add(vertices=24,radius=r,depth=(b-a).length,location=(a+b)/2); o=bpy.context.object; o.name=name; o.rotation_euler=(b-a).to_track_quat('Z','Y').to_euler(); o.data.materials.append(m)
    for p in o.data.polygons: p.use_smooth=len(p.vertices)==4
    bevel=o.modifiers.new('Tube end bevel','BEVEL'); bevel.width=0.004; bevel.segments=2
    return o

def tube(name,points,r,m):
    cu=bpy.data.curves.new(name,'CURVE'); cu.dimensions='3D'; cu.resolution_u=12; cu.bevel_depth=r; cu.bevel_resolution=3
    sp=cu.splines.new('POLY'); sp.points.add(len(points)-1)
    for p,v in zip(sp.points,points): p.co=(*v,1)
    o=bpy.data.objects.new(name,cu); bpy.context.collection.objects.link(o); o.data.materials.append(m); return o

def fabric(name,fn,nu,nv,m):
    vs=[fn(i/nu,j/nv) for j in range(nv+1) for i in range(nu+1)]; fs=[]
    for j in range(nv):
        for i in range(nu):
            a=j*(nu+1)+i; fs.append((a,a+1,a+nu+2,a+nu+1))
    me=bpy.data.meshes.new(name); me.from_pydata(vs,[],fs); me.update(); o=bpy.data.objects.new(name,me); bpy.context.collection.objects.link(o); o.data.materials.append(m)
    for p in me.polygons: p.use_smooth=True
    s=o.modifiers.new('Canvas thickness','SOLIDIFY'); s.thickness=0.009
    return o

# Front is negative Y. Each side is a crossed, pivoting pair of tubes.
for side in [-1,1]:
    x=side*0.59
    rod('Front foot to rear seat strut',(x,-0.52,0.08),(x,0.40,0.94),0.025,frame)
    rod('Rear foot to front seat strut',(x,0.53,0.08),(x,-0.43,0.94),0.025,frame)
    rod('Reclined back upright',(x,0.37,0.79),(x,0.66,1.82),0.026,frame)
    rod('Armrest front support',(x,-0.39,0.90),(x,-0.31,1.29),0.022,frame)
    rod('Armrest rail',(x,-0.39,1.29),(x,0.51,1.31),0.022,frame)
    for y in [-0.52,0.53]: box('Broad non-slip foot',(x,y,0.065),(0.14,0.16,0.10),rubber,0.025)
    rod('Main folding pivot',(x-side*0.042,0.005,0.50),(x+side*0.046,0.005,0.50),0.064,rubber)
    rod('Pivot bolt',(x+side*0.044,0.005,0.50),(x+side*0.062,0.005,0.50),0.029,metal)
    for y,z in [(-0.40,0.92),(0.39,0.94),(0.51,1.31)]:
        rod('Hinge pin',(x-side*0.032,y,z),(x+side*0.039,y,z),0.032,metal)
    box('Padded canvas armrest',(x,0.035,1.335),(0.19,0.86,0.055),cloth,0.025)
    for xx in [x-0.073,x+0.073]: tube('Armrest stitched seam',[(xx,-0.35,1.367),(xx,0.42,1.367)],0.0025,stitch)
rod('Front seat crossbar',(-0.59,-0.43,0.94),(0.59,-0.43,0.94),0.026,frame)
rod('Rear seat crossbar',(-0.59,0.40,0.94),(0.59,0.40,0.94),0.026,frame)
rod('Back top crossbar',(-0.59,0.66,1.82),(0.59,0.66,1.82),0.026,frame)
rod('Front folding diagonal A',(-0.56,-0.49,0.15),(0.56,-0.43,0.91),0.019,frame)
rod('Front folding diagonal B',(0.56,-0.52,0.15),(-0.56,-0.46,0.91),0.019,frame)
rod('Front brace pivot',(0,-0.51,0.53),(0,-0.43,0.53),0.032,metal)
rod('Rear folding diagonal A',(-0.56,0.49,0.15),(0.56,0.40,0.91),0.019,frame)
rod('Rear folding diagonal B',(0.56,0.52,0.15),(-0.56,0.43,0.91),0.019,frame)

def seat(u,v):
    return ((u-0.5)*1.14,-0.43+v*0.83,0.965-0.105*math.sin(math.pi*u)*math.sin(math.pi*v))
def back(u,v):
    return ((u-0.5)*1.14,0.41+v*0.25+0.055*math.sin(math.pi*u)*math.sin(math.pi*v),1.00+v*0.79)
fabric('Suspended canvas seat',seat,28,24,cloth); fabric('Flexible canvas backrest',back,28,24,cloth)
for name,fn in [('Seat',seat),('Back',back)]:
    for fixed in [0,1]:
        tube(name+' side binding',[fn(fixed,i/32) for i in range(33)],0.012,trim)
        tube(name+' transverse binding',[fn(i/32,fixed) for i in range(33)],0.012,trim)
    for u in [0.025,0.975]:
        pts=[Vector(fn(u,i/50)) for i in range(51)]
        for i in range(0,50,2):
            a=pts[i]+Vector((0,-0.005,0.008)); b=pts[i+1]+Vector((0,-0.005,0.008)); tube(name+' stitches',[a,b],0.0018,stitch)
box('Backrest logo patch',(0,0.602,1.60),(0.22,0.015,0.10),trim,0.01)
# A hanging fabric pocket on the right side.
fabric('Side storage pocket',lambda u,v:(0.69+0.025*math.sin(math.pi*u)*math.sin(math.pi*v),-0.15+u*0.43,0.78+v*0.40),16,12,cloth)
tube('Pocket opening',[(0.70,-0.15,1.18),(0.70,0.28,1.18)],0.013,trim)
for y in [-0.12,0.25]: box('Pocket suspension webbing',(0.68,y,1.25),(0.025,0.055,0.19),trim,0.005)
box('Ground',(0,0,-0.035),(200,200,0.05),ground)
scene=bpy.context.scene; scene.world.use_nodes=True; scene.world.node_tree.nodes['Background'].inputs[0].default_value=(0.32,0.37,0.42,1); scene.world.node_tree.nodes['Background'].inputs[1].default_value=0.4
for loc,power,size in [((-3,-4,5),650,4),((3,1,4),850,3),((0,4,3),400,2)]:
    bpy.ops.object.light_add(type='AREA',location=loc); o=bpy.context.object; o.data.energy=power; o.data.size=size; o.rotation_euler=(Vector((0,0,0.9))-o.location).to_track_quat('-Z','Y').to_euler()
bpy.ops.object.camera_add(location=(3.2,-4.4,2.8)); cam=bpy.context.object; cam.rotation_euler=(Vector((0,0.08,0.92))-cam.location).to_track_quat('-Z','Y').to_euler(); cam.data.type='ORTHO'; cam.data.ortho_scale=2.9; scene.camera=cam
scene.render.engine='CYCLES'; scene.render.resolution_x=1100; scene.render.resolution_y=1100; scene.render.resolution_percentage=100
