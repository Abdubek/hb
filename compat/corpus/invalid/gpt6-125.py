import bpy, math
from mathutils import Vector
bpy.ops.wm.read_factory_settings(use_empty=True)

def mat(name,rgb,metal=0,roughness=0.4,glow=0):
    m=bpy.data.materials.new(name)
    m.diffuse_color=(*rgb,1)
    m.use_nodes=True
    p=m.node_tree.nodes.get('Principled BSDF')
    p.inputs['Base Color'].default_value=(*rgb,1)
    p.inputs['Metallic'].default_value=metal
    p.inputs['Roughness'].default_value=roughness
    if glow:
        p.inputs['Emission Color'].default_value=(*rgb,1)
        p.inputs['Emission Strength'].default_value=glow
    return m

def finish(o,name,m,bevel=0):
    o.name=name
    o.data.materials.append(m)
    if bevel:
        b=o.modifiers.new('Edge treatment','BEVEL')
        b.width,b.segments=bevel,3
        o.modifiers.new('Weighted normals','WEIGHTED_NORMAL')
    return o

def box(name,loc,size,m,bevel=0.025):
    bpy.ops.mesh.primitive_cube_add(size=1,location=loc)
    o=bpy.context.object
    o.dimensions=size
    bpy.ops.object.transform_apply(location=False,rotation=False,scale=True)
    return finish(o,name,m,bevel)

def cyl(name,a,b,r,m,verts=40):
    a,b=Vector(a),Vector(b)
    bpy.ops.mesh.primitive_cylinder_add(vertices=verts,radius=r,depth=(b-a).length,location=(a+b)/2)
    o=bpy.context.object
    o.rotation_mode='QUATERNION'
    o.rotation_quaternion=(b-a).to_track_quat('Z','Y')
    finish(o,name,m,0.012)
    for p in o.data.polygons:
        p.use_smooth=len(p.vertices)==4
    return o

def sphere(name,loc,scale,m):
    bpy.ops.mesh.primitive_uv_sphere_add(segments=40,ring_count=20,location=loc)
    o=bpy.context.object
    o.scale=scale
    finish(o,name,m)
    for p in o.data.polygons:
        p.use_smooth=True
    return o

def torus(name,loc,r,t,m,axis=(0,0,1)):
    bpy.ops.mesh.primitive_torus_add(major_radius=r,minor_radius=t,major_segments=64,minor_segments=12,location=loc)
    o=bpy.context.object
    o.rotation_mode='QUATERNION'
    o.rotation_quaternion=Vector(axis).to_track_quat('Z','Y')
    finish(o,name,m)
    for p in o.data.polygons:
        p.use_smooth=True
    return o

def lathe(name,profile,m,loc=(0,0,0),segments=64):
    verts,faces=[],[]
    for r,z in profile:
        for i in range(segments):
            a=i*math.tau/segments
            verts.append((loc[0]+r*math.cos(a),loc[1]+r*math.sin(a),loc[2]+z))
    for j in range(len(profile)-1):
        for i in range(segments):
            a=j*segments+i
            b=j*segments+(i+1)%segments
            faces.append((a,b,b+segments,a+segments))
    mesh=bpy.data.meshes.new(name)
    mesh.from_pydata(verts,[],faces)
    mesh.update()
    o=bpy.data.objects.new(name,mesh)
    bpy.context.collection.objects.link(o)
    finish(o,name,m)
    for p in mesh.polygons:
        p.use_smooth=True
    return o

def cable(name,points,r,m):
    c=bpy.data.curves.new(name,'CURVE')
    c.dimensions,c.bevel_depth,c.bevel_resolution='3D',r,3
    s=c.splines.new('BEZIER')
    s.bezier_points.add(len(points)-1)
    for p,co in zip(s.bezier_points,points):
        p.co=co
        p.handle_left_type=p.handle_right_type='AUTO'
    o=bpy.data.objects.new(name,c)
    bpy.context.collection.objects.link(o)
    o.data.materials.append(m)

def label(body,loc,size,m):
    c=bpy.data.curves.new(body,'FONT')
    c.body,c.size,c.align_x=body,size,'CENTER'
    c.extrude=0.001
    o=bpy.data.objects.new(body,c)
    bpy.context.collection.objects.link(o)
    o.location=loc
    o.rotation_euler.x=math.pi/2
    o.data.materials.append(m)

ivory=mat('Thermal ceramic ivory',(0.73,0.78,0.77),0.35)
steel=mat('Titanium structures',(0.32,0.4,0.45),0.85,0.29)
dark=mat('Heat shield graphite',(0.025,0.033,0.042),0.45)
gold=mat('Tank bronze insulation',(0.66,0.37,0.09),0.72,0.33)
blue=mat('Mission blue',(0.025,0.15,0.28),0.55)
glass=mat('Dark cockpit glazing',(0.012,0.085,0.14),0.65,0.13)
orange=mat('Dock safety orange',(0.96,0.37,0.035),0.35)
cyan=mat('Dock lamps',(0.025,0.63,1),0.1,0.3,4)
red=mat('Navigation red',(1,0.018,0.007),0.1,0.3,3)
ground=mat('Hangar floor',(0.065,0.085,0.11),0.2,0.7)
box('Hangar foundation',(0,0,-0.35),(200,200,0.3),ground)
cyl('Circular docking pad',(0,0,-0.18),(0,0,0.06),5.2,dark,96)
cyl('Pad upper deck',(0,0,0.05),(0,0,0.13),4.96,steel,96)
torus('Pad outer warning ring',(0,0,0.146),4.55,0.045,orange)
for i in range(16):
    a=i*math.tau/16
    o=box('Radial deck seam',(3.5*math.cos(a),3.5*math.sin(a),0.137),(2.3,0.025,0.012),dark,0)
    o.rotation_euler.z=a
    cyl('Pad inset light',(4.83*math.cos(a),4.83*math.sin(a),0.13),(4.83*math.cos(a),4.83*math.sin(a),0.165),0.07,cyan,20)

# Revolved pressure capsule: flat service base, cylindrical waist, tapered crew cabin.
lathe('Main crew capsule',[(0,1.87),(1.28,1.87),(1.52,2.1),(1.55,3.43),(1.46,3.8),(1.12,4.8),(0.71,5.44),(0.4,5.7),(0,5.76)],ivory)
cyl('Lower service module',(0,0,1.42),(0,0,2.23),1.3,blue,64)
torus('Lower structural ring',(0,0,1.54),1.32,0.085,steel)
torus('Capsule base heat shield',(0,0,2.15),1.51,0.09,dark)
torus('Waist separation seam',(0,0,3.43),1.553,0.021,dark)
torus('Upper cabin seam',(0,0,3.81),1.458,0.016,steel)
for i in range(16):
    a=i*math.tau/16
    x,y=1.322*math.cos(a),1.322*math.sin(a)
    o=box('Service module rib',(x,y,1.85),(0.055,0.075,0.52),steel,0.012)
    o.rotation_euler.z=a

# Windows are mounted normal to the sloping cabin surface.
for i,a in enumerate((math.radians(-125),math.radians(-90),math.radians(-55))):
    outward=Vector((math.cos(a),math.sin(a),0.34)).normalized()
    center=Vector((1.32*math.cos(a),1.32*math.sin(a),4.12))
    o=box('Cockpit window metal bezel',center,(0.6,0.47,0.09),dark,0.075)
    o.rotation_mode='QUATERNION'
    o.rotation_quaternion=outward.to_track_quat('Z','Y')
    o=box('Cockpit glazing',center+outward*0.052,(0.49,0.36,0.033),glass,0.06)
    o.rotation_mode='QUATERNION'
    o.rotation_quaternion=outward.to_track_quat('Z','Y')
label('KESTREL', (0,-1.558,2.99),0.22,blue)
label('EXPLORER  12',(0,-1.56,2.72),0.1,dark)

for i,a in enumerate((0,math.pi/2,math.pi,3*math.pi/2)):
    u=Vector((math.cos(a),math.sin(a),0))
    t=Vector((-math.sin(a),math.cos(a),0))
    p=u*1.98
    for z in (2.05,3.4):
        cyl('Tank mounting outrigger',u*1.31+Vector((0,0,z)),p+Vector((0,0,z)),0.09,steel)
    cyl('External fuel tank barrel',(p.x,p.y,2.13),(p.x,p.y,3.45),0.39,gold)
    sphere('Fuel tank lower dome',(p.x,p.y,2.13),(0.39,0.39,0.32),gold)
    sphere('Fuel tank upper dome',(p.x,p.y,3.45),(0.39,0.39,0.32),gold)
    for z in (2.3,3.25):
        cyl('Tank retaining strap',(p.x,p.y,z-0.055),(p.x,p.y,z+0.055),0.408,steel)
        box('Strap tension block',(p.x+u.x*0.4,p.y+u.y*0.4,z),(0.11,0.11,0.15),dark)
    cyl('Tank feed neck',(p.x,p.y,1.78),(p.x,p.y,1.98),0.085,steel)
    cable('Fuel delivery hose',[(p.x,p.y,1.81),(p.x*0.9,p.y*0.9,1.58),(u.x*1.28,u.y*1.28,1.77)],0.047,dark)

# Four thruster pods occupy the spaces between the fuel tanks.
for i in range(4):
    a=math.pi/4+i*math.pi/2
    u=Vector((math.cos(a),math.sin(a),0))
    t=Vector((-math.sin(a),math.cos(a),0))
    p=u*1.95
    cyl('Thruster pod support',u*1.2+Vector((0,0,1.95)),p+Vector((0,0,1.95)),0.12,steel)
    cyl('Thruster pod housing',(p.x,p.y,1.77),(p.x,p.y,2.42),0.28,blue)
    sphere('Pod upper cap',(p.x,p.y,2.41),(0.28,0.28,0.15),ivory)
    # Double-wall bell profile remains visibly open underneath.
    lathe('Open thruster bell',[(0.13,1.89),(0.16,1.7),(0.27,1.46),(0.3,1.34),(0.255,1.34),(0.23,1.46),(0.12,1.7),(0.095,1.87)],dark,(p.x,p.y,0),40)
    torus('Thruster bell rim',(p.x,p.y,1.35),0.28,0.025,steel)
    for sign in (-1,1):
        q=p+t*sign*0.24+Vector((0,0,2.15))
        cyl('Attitude control nozzle housing',q,q+t*sign*0.16,0.09,steel)
        cyl('Attitude nozzle dark aperture',q+t*sign*0.165,q+t*sign*0.174,0.067,dark)

for i in range(4):
    a=math.pi/4+i*math.pi/2
    u=Vector((math.cos(a),math.sin(a),0))
    t=Vector((-math.sin(a),math.cos(a),0))
    top=u*1.37+Vector((0,0,2.38))
    knee=u*2.6+Vector((0,0,0.8))
    foot=u*3.16+Vector((0,0,0.3))
    cyl('Landing leg main strut',top,knee,0.13,ivory)
    cyl('Landing leg exposed piston',knee,foot,0.08,steel)
    cyl('Landing brace',u*1.22+Vector((0,0,1.55)),knee,0.075,steel)
    for p in (top,knee):
        cyl('Landing leg hinge',p-t*0.19,p+t*0.19,0.16,dark)
        cyl('Hinge cap',p-t*0.21,p-t*0.19,0.09,orange)
    o=box('Landing footpad',(foot.x,foot.y,0.23),(0.87,0.62,0.18),dark,0.09)
    o.rotation_euler.z=a
    cyl('Foot swivel',(foot.x,foot.y,0.25),foot+Vector((0,0,0.15)),0.13,steel)
    for offset in (-0.23,0,0.23):
        pos=Vector((foot.x,foot.y,0.328))+u*offset
        o=box('Footpad traction rib',pos,(0.035,0.48,0.02),steel,0.005)
        o.rotation_euler.z=a

# The landed craft is physically docked to a rear service tower by a sealed collar.
box('Dock tower base',(0,4.28,0.37),(2.9,1.6,0.48),dark,0.08)
for x in (-1.07,1.07):
    box('Dock tower upright',(x,4.56,2.88),(0.2,0.24,5.05),steel)
    for z in (1.0,2.3,3.6,4.9):
        box('Tower cross tie',(0,4.56,z),(2.23,0.14,0.15),steel)
    for z in (1.0,2.3,3.6):
        cyl('Tower diagonal brace',(-1.05,4.57,z),(1.05,4.57,z+1.3),0.055,steel)
    cyl('Tower beacon',(x,4.56,5.39),(x,4.56,5.58),0.09,cyan)
box('Dock machinery cabinet',(0,4.22,3.1),(1.73,0.9,1.8),blue,0.08)
cyl('Dock transfer tunnel',(0,1.4,3.04),(0,4.2,3.04),0.62,steel,48)
for y in (1.49,1.67,1.87,2.07,2.27,2.47):
    torus('Flexible docking bellows',(0,y,3.04),0.63,0.06,dark,(0,1,0))
torus('Dock mating collar',(0,1.44,3.04),0.71,0.08,ivory,(0,1,0))
for i in range(8):
    a=i*math.tau/8
    box('Dock latch',(0.73*math.cos(a),1.54,3.04+0.73*math.sin(a)),(0.13,0.23,0.13),orange)
box('Service catwalk',(0,3.22,2.26),(1.9,2.35,0.13),dark)
for x in (-0.89,0.89):
    for y in (2.5,3.3,4.15):
        cyl('Catwalk handrail post',(x,y,2.28),(x,y,3.05),0.028,orange,16)
    cyl('Catwalk handrail',(x,2.5,3.05),(x,4.15,3.05),0.035,orange,16)
cable('Dock utility umbilical',[(0.8,4.08,3.6),(1.35,3.2,2.45),(1.15,1.8,2.65),(0.92,1.12,2.82)],0.055,orange)
cyl('Communications aerial',(0,0,5.68),(0,0,6.28),0.027,steel)
sphere('Aerial tip',(0,0,6.3),(0.065,0.065,0.065),red)
for name,loc,power,color,size in [('Key',(1,-8,11),2400,(0.8,0.9,1),6),('Warm fill',(-7,-2,6),1700,(1,0.67,0.35),5),('Rim',(4,7,10),2600,(0.3,0.65,1),5)]:
    d=bpy.data.lights.new(name,'AREA')
    d.energy,d.color,d.size=power,color,size
    o=bpy.data.objects.new(name,d)
    bpy.context.collection.objects.link(o)
    o.location=loc
    o.rotation_euler=(Vector((0,0,2.6))-o.location).to_track_quat('-Z','Y').to_euler()
bpy.ops.object.camera_add(location=(11,-14,10))
cam=bpy.context.object
cam.rotation_euler=(Vector((0,0.65,2.6))-cam.location).to_track_quat('-Z','Y').to_euler()
cam.data.type,cam.data.ortho_scale='ORTHO',13.8
scene=bpy.context.scene
scene.camera=cam
scene.world.color=(0.07,0.09,0.13)
scene.render.engine='CYCLES'
scene.render.resolution_x,scene.render.resolution_y=1400,1200
scene.render.resolution_percentage=100
scene.view_settings.view_transform='AgX'
