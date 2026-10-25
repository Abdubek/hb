import bpy, math
from mathutils import Vector

bpy.ops.wm.read_factory_settings(use_empty=True)

def mat(name,color,metallic=0.0,roughness=0.4):
    m=bpy.data.materials.new(name)
    m.diffuse_color=(*color,1)
    m.use_nodes=True
    p=m.node_tree.nodes.get('Principled BSDF')
    p.inputs['Base Color'].default_value=(*color,1)
    p.inputs['Metallic'].default_value=metallic
    p.inputs['Roughness'].default_value=roughness
    return m

def box(name,loc,size,material,bevel=0.0):
    bpy.ops.mesh.primitive_cube_add(size=1,location=loc)
    o=bpy.context.object
    o.name=name
    o.dimensions=size
    bpy.ops.object.transform_apply(location=False,rotation=False,scale=True)
    o.data.materials.append(material)
    if bevel:
        b=o.modifiers.new('Soft edges','BEVEL')
        b.width=bevel
        b.segments=4
        o.modifiers.new('Weighted normals','WEIGHTED_NORMAL')
    return o

def rod(name,a,b,radius,material):
    a,b=Vector(a),Vector(b)
    bpy.ops.mesh.primitive_cylinder_add(vertices=40,radius=radius,depth=(b-a).length,location=(a+b)/2)
    o=bpy.context.object
    o.name=name
    o.rotation_euler=(b-a).to_track_quat('Z','Y').to_euler()
    o.data.materials.append(material)
    for p in o.data.polygons:
        p.use_smooth=True
    bevel=o.modifiers.new('Machined edge','BEVEL')
    bevel.width=0.012
    bevel.segments=3
    o.modifiers.new('Weighted normals','WEIGHTED_NORMAL')
    return o

def oval_cylinder(name,x,y,z,depth,ry,rz,material):
    bpy.ops.mesh.primitive_cylinder_add(vertices=64,radius=1,depth=depth,location=(x,y,z),rotation=(0,math.pi/2,0))
    o=bpy.context.object
    o.name=name
    o.scale=(rz,ry,1)
    bpy.ops.object.transform_apply(location=False,rotation=False,scale=True)
    o.data.materials.append(material)
    b=o.modifiers.new('Rounded cup edges','BEVEL')
    b.width=0.045
    b.segments=4
    o.modifiers.new('Weighted normals','WEIGHTED_NORMAL')
    for p in o.data.polygons:
        p.use_smooth=True
    return o

def oval_ring(name,x,y,z,ry,rz,tube_x,tube_rad,material):
    verts=[]
    faces=[]
    n,m=72,16
    for i in range(n):
        t=2*math.pi*i/n
        for j in range(m):
            p=2*math.pi*j/m
            verts.append((x+tube_x*math.sin(p),y+(ry+tube_rad*math.cos(p))*math.cos(t),z+(rz+tube_rad*math.cos(p))*math.sin(t)))
    for i in range(n):
        for j in range(m):
            faces.append((i*m+j,((i+1)%n)*m+j,((i+1)%n)*m+(j+1)%m,i*m+(j+1)%m))
    mesh=bpy.data.meshes.new(name)
    mesh.from_pydata(verts,[],faces)
    mesh.update()
    o=bpy.data.objects.new(name,mesh)
    bpy.context.collection.objects.link(o)
    o.data.materials.append(material)
    for p in mesh.polygons:
        p.use_smooth=True
    return o

def band(name,rx,rz,zc,t0,t1,width,thickness,material):
    verts=[]
    faces=[]
    segments=80
    for i in range(segments+1):
        t=t0+(t1-t0)*i/segments
        for radial,y in [(-thickness/2,-width/2),(-thickness/2,width/2),(thickness/2,width/2),(thickness/2,-width/2)]:
            verts.append(((rx+radial)*math.cos(t),y,zc+(rz+radial)*math.sin(t)))
    for i in range(segments):
        for j in range(4):
            faces.append((4*i+j,4*i+(j+1)%4,4*(i+1)+(j+1)%4,4*(i+1)+j))
    faces.extend([(3,2,1,0),(4*segments,4*segments+1,4*segments+2,4*segments+3)])
    mesh=bpy.data.meshes.new(name)
    mesh.from_pydata(verts,[],faces)
    mesh.update()
    o=bpy.data.objects.new(name,mesh)
    bpy.context.collection.objects.link(o)
    o.data.materials.append(material)
    bevel=o.modifiers.new('Comfort edge rounding','BEVEL')
    bevel.width=0.028
    bevel.segments=3
    o.modifiers.new('Weighted normals','WEIGHTED_NORMAL')
    for p in mesh.polygons:
        p.use_smooth=True
    return o

def curve(name,points,radius,material):
    data=bpy.data.curves.new(name,'CURVE')
    data.dimensions='3D'
    data.resolution_u=20
    data.bevel_depth=radius
    data.bevel_resolution=4
    spline=data.splines.new('BEZIER')
    spline.bezier_points.add(len(points)-1)
    for p,co in zip(spline.bezier_points,points):
        p.co=co
        p.handle_left_type='AUTO'
        p.handle_right_type='AUTO'
    o=bpy.data.objects.new(name,data)
    bpy.context.collection.objects.link(o)
    o.data.materials.append(material)
    return o

def area(loc,power,size,target):
    bpy.ops.object.light_add(type='AREA',location=loc)
    o=bpy.context.object
    o.data.energy=power
    o.data.size=size
    o.rotation_euler=(Vector(target)-o.location).to_track_quat('-Z','Y').to_euler()

shell=mat('Midnight blue earcup shells',(0.045,0.105,0.15),0.55,0.28)
leather=mat('Soft charcoal cushions',(0.025,0.029,0.035),0,0.7)
metal=mat('Satin titanium',(0.42,0.49,0.55),0.85,0.27)
accent=mat('Copper trim',(0.71,0.35,0.15),0.78,0.27)
black=mat('Recesses and cable',(0.009,0.012,0.018),0,0.5)
meshmat=mat('Inner acoustic fabric',(0.065,0.075,0.085),0,0.95)
standmat=mat('Warm graphite stand',(0.10,0.12,0.14),0.7,0.31)
floor=mat('Studio floor',(0.28,0.32,0.35),0,0.75)

box('Ground',(0,0,-0.10),(200,200,0.16),floor)
box('Weighted stand base',(0,0.24,0.13),(2.05,1.5,0.26),standmat,0.12)
box('Base top insert',(0,0.24,0.269),(1.83,1.28,0.025),leather,0.10)
for x in [-0.72,0.72]:
    for y in [-0.22,0.72]:
        box('Stand rubber foot',(x,y,-0.005),(0.24,0.19,0.035),black,0.035)
rod('Stand vertical column',(0,0.31,0.27),(0,0.31,3.57),0.095,metal)
box('Top saddle',(0,0.05,3.66),(0.73,0.68,0.17),standmat,0.08)
box('Saddle soft pad',(0,0.02,3.758),(0.70,0.59,0.075),leather,0.036)

band('Continuous sprung metal headband',1.35,1.47,2.52,0,math.pi,0.44,0.085,metal)
band('Headband outer blue wrap',1.365,1.49,2.52,0.28,math.pi-0.28,0.46,0.095,shell)
band('Underside padded headband',1.29,1.37,2.52,0.40,math.pi-0.40,0.41,0.15,leather)
for side in [-1,1]:
    x=side*1.35
    box('Telescoping adjustment slider',(x,0,2.62),(0.095,0.27,0.47),metal,0.035)
    box('Slider collar',(x,0,2.80),(0.13,0.32,0.12),shell,0.03)
    for z in [2.49,2.56,2.63]:
        box('Slider index mark',(x,-0.142,z),(0.055,0.004,0.012),black,0.002)
    # A fork supports each cup at its front and rear swivel points.
    for y in [-0.43,0.43]:
        rod('Yoke diagonal',(x,0,2.48),(side*1.43,y,2.30),0.043,metal)
        rod('Yoke fork',(side*1.43,y,2.30),(side*1.43,y,1.99),0.043,metal)
        rod('Yoke pivot bolt',(side*1.38,y,1.99),(side*1.51,y,1.99),0.075,accent)
    oval_cylinder('Over-ear shell',side*1.39,0,1.98,0.34,0.47,0.66,shell)
    oval_cylinder('Outer copper rim',side*1.572,0,1.98,0.025,0.426,0.606,accent)
    oval_cylinder('Outer cover',side*1.594,0,1.98,0.045,0.405,0.583,shell)
    oval_cylinder('Recessed driver fabric',side*1.175,0,1.98,0.045,0.35,0.53,meshmat)
    oval_ring('Plush oval ear cushion',side*1.15,0,1.98,0.335,0.505,0.135,0.105,leather)
    oval_ring('Cushion stitched seam',side*1.065,0,1.98,0.354,0.527,0.008,0.008,meshmat)
    rod('Circular brand medallion',(side*1.621,0,1.98),(side*1.63,0,1.98),0.13,metal)
    rod('Medallion inset',(side*1.632,0,1.98),(side*1.636,0,1.98),0.082,shell)
    for i in range(6):
        box('Cup ventilation slot',(side*1.61,-0.15+i*0.06,1.57),(0.017,0.018,0.10),black,0.008)

for z in [1.86,2.08]:
    box('Left cup control',(-1.43,-0.48,z),(0.10,0.028,0.12),metal,0.012)
rod('Audio cable socket',(-1.38,-0.08,1.34),(-1.38,-0.08,1.21),0.052,metal)
curve('Hanging audio cable',[(-1.38,-0.08,1.22),(-1.49,-0.13,0.65),(-1.37,-0.33,0.13),(-0.88,-0.85,0.05),(-0.16,-0.99,0.045),(0.55,-0.81,0.045),(0.67,-0.36,0.046),(0.24,-0.26,0.05),(-0.06,-0.62,0.045),(0.51,-1.13,0.05),(1.05,-1.17,0.05)],0.022,black)
rod('Cable plug body',(1.04,-1.17,0.05),(1.30,-1.17,0.05),0.048,black)
rod('Audio jack',(1.30,-1.17,0.05),(1.53,-1.17,0.05),0.025,accent)
for x in [1.37,1.43]:
    rod('Jack insulating ring',(x,-1.17,0.05),(x+0.012,-1.17,0.05),0.026,black)

area((-4,-5,7),1200,4,(0,0,2))
area((4,2,6),1600,3,(0,0,2.3))
area((1,-4,3),400,3,(0,0,2))
bpy.ops.object.camera_add(location=(6,-8,4.9))
cam=bpy.context.object
cam.rotation_euler=(Vector((0,-0.05,2.03))-cam.location).to_track_quat('-Z','Y').to_euler()
cam.data.type='ORTHO'
cam.data.ortho_scale=5.8
scene=bpy.context.scene
scene.camera=cam
scene.render.engine='CYCLES'
scene.cycles.samples=64
scene.world.color=(0.20,0.20,0.20)
scene.render.resolution_x=1200
scene.render.resolution_y=1400
scene.render.resolution_percentage=100
scene.view_settings.view_transform='AgX'
