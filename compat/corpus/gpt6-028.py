import bpy, math
from mathutils import Vector
bpy.ops.object.select_all(action='SELECT'); bpy.ops.object.delete(use_global=False)

def mat(name,c,rough=.4,metal=0):
    m=bpy.data.materials.new(name); m.diffuse_color=(*c,1); m.use_nodes=True; p=m.node_tree.nodes.get('Principled BSDF'); p.inputs['Base Color'].default_value=(*c,1); p.inputs['Roughness'].default_value=rough; p.inputs['Metallic'].default_value=metal; return m

def cylinder(name,a,b,r,m,r2=None):
    a=Vector(a); b=Vector(b); d=b-a
    if r2 is None: bpy.ops.mesh.primitive_cylinder_add(vertices=48,radius=r,depth=d.length,location=(a+b)/2)
    else: bpy.ops.mesh.primitive_cone_add(vertices=48,radius1=r,radius2=r2,depth=d.length,location=(a+b)/2)
    o=bpy.context.object; o.name=name; o.rotation_euler=d.to_track_quat('Z','Y').to_euler(); o.data.materials.append(m); be=o.modifiers.new('Soft metal edges','BEVEL'); be.width=.005; be.segments=3; o.modifiers.new('Normals','WEIGHTED_NORMAL')
    for p in o.data.polygons: p.use_smooth=True
    return o

def curve(name,pts,r,m):
    c=bpy.data.curves.new(name,'CURVE'); c.dimensions='3D'; c.bevel_depth=r; c.bevel_resolution=3; s=c.splines.new('BEZIER'); s.bezier_points.add(len(pts)-1)
    for p,co in zip(s.bezier_points,pts): p.co=co; p.handle_left_type='AUTO'; p.handle_right_type='AUTO'
    o=bpy.data.objects.new(name,c); bpy.context.collection.objects.link(o); c.materials.append(m); return o

def cube(name,loc,size,m,bevel=.01):
    bpy.ops.mesh.primitive_cube_add(size=1,location=loc); o=bpy.context.object; o.name=name; o.dimensions=size; bpy.ops.object.transform_apply(location=False,rotation=False,scale=True); o.data.materials.append(m)
    if bevel: b=o.modifiers.new('Rounded edges','BEVEL'); b.width=bevel; b.segments=3; o.modifiers.new('Normals','WEIGHTED_NORMAL')
    return o

paint=mat('Satin forest green enamel',(.065,.15,.115),.32,.45); brass=mat('Brushed brass fittings',(.58,.36,.12),.28,.8); dark=mat('Black rubber',(.017,.022,.021),.7); white=mat('Warm porcelain reflector',(.86,.84,.73),.32); bulbmat=mat('Glowing frosted bulb',(1,.8,.43),.3)
p=bulbmat.node_tree.nodes.get('Principled BSDF'); p.inputs['Emission Color'].default_value=(1,.70,.30,1); p.inputs['Emission Strength'].default_value=3
cylinder('Non-slip underside',(0,0,.012),(0,0,.035),.29,dark)
cylinder('Heavy circular base',(0,0,.035),(0,0,.10),.31,paint,r2=.285)
cylinder('Brass base inset',(0,0,.10),(0,0,.111),.20,brass)
cylinder('Stem socket',(0,0,.10),(0,0,.22),.06,paint)
cylinder('Lower upright',(0,0,.18),(0,0,1.12),.026,paint)
cylinder('Telescoping collar',(0,0,1.04),(0,0,1.12),.039,brass)
cylinder('Collar lock screw',(0,-.03,1.075),(0,-.075,1.075),.013,brass)
cylinder('Collar thumb wheel',(0,-.075,1.075),(0,-.09,1.075),.027,dark)
cylinder('Polished upper upright',(0,0,1.10),(0,0,1.50),.019,brass)
A=Vector((0,0,1.50)); B=Vector((.42,0,1.94)); C=Vector((.92,0,1.75))
# Paired parallel rails and visible locking pivots make the arm adjustable.
for start,end,name in [(A,B,'Lower arm'),(B,C,'Upper arm')]:
    for y in [-.038,.038]: cylinder(name+' rail',start+Vector((0,y,0)),end+Vector((0,y,0)),.014,paint)
for i,pivot in enumerate([A,B,C]):
    cylinder('Pivot %d brass axle'%i,pivot+Vector((0,-.073,0)),pivot+Vector((0,.073,0)),.026,brass)
    cylinder('Pivot %d circular housing'%i,pivot+Vector((0,-.050,0)),pivot+Vector((0,.050,0)),.052,paint)
    cylinder('Front locking wheel',pivot+Vector((0,-.086,0)),pivot+Vector((0,-.055,0)),.037,brass)
    cylinder('Lock screw',pivot+Vector((0,-.091,0)),pivot+Vector((0,-.086,0)),.012,dark)
# Exposed tension spring alongside lower arm.
u=(B-A).normalized(); e=Vector((0,1,0)); f=u.cross(e).normalized(); start=A+(B-A)*.18+Vector((0,-.078,0)); length=(B-A).length*.56
pts=[]
for j in range(241):
    t=j/240; pts.append(start+u*(t*length)+.020*(math.cos(t*math.tau*17)*e+math.sin(t*math.tau*17)*f))
c= bpy.data.curves.new('Helical balance spring','CURVE'); c.dimensions='3D'; c.bevel_depth=.0035; c.bevel_resolution=2; s=c.splines.new('POLY'); s.points.add(len(pts)-1)
for p,co in zip(s.points,pts): p.co=(*co,1)
o=bpy.data.objects.new('Helical balance spring',c); bpy.context.collection.objects.link(o); c.materials.append(brass)
for t in [.18,.74]: cylinder('Spring anchor',A+(B-A)*t,A+(B-A)*t+Vector((0,-.10,0)),.008,brass)
# Open bell shade with explicit outer wall, inner wall and rolled rim.
axis=Vector((.22,-.12,-1)).normalized(); top=C+axis*.09; cylinder('Shade swivel neck',C,top,.025,brass)
q=axis.to_track_quat('Z','Y'); rings=[(0,.058),(.04,.067),(.15,.132),(.25,.195),(.26,.195),(.26,.186),(.15,.123),(.04,.058),(0,.049)]; verts=[]; faces=[]; count=64
for z,r in rings:
    for j in range(count): verts.append(top+q@Vector((r*math.cos(j*math.tau/count),r*math.sin(j*math.tau/count),z)))
for k in range(len(rings)):
    nk=(k+1)%len(rings)
    for j in range(count): faces.append((k*count+j,k*count+(j+1)%count,nk*count+(j+1)%count,nk*count+j))
mesh=bpy.data.meshes.new('Hollow spun shade mesh'); mesh.from_pydata(verts,[],faces); mesh.update(); shade=bpy.data.objects.new('Open enamel bell shade',mesh); bpy.context.collection.objects.link(shade); mesh.materials.append(paint); mesh.materials.append(white); mesh.materials.append(brass)
for poly in mesh.polygons:
    band=poly.index//count; poly.material_index=1 if band>=5 else (2 if band in [3,4] else 0); poly.use_smooth=True
cylinder('Bulb socket',top+axis*.02,top+axis*.105,.033,white)
bpy.ops.mesh.primitive_uv_sphere_add(segments=32,ring_count=16,radius=.054,location=top+axis*.16); o=bpy.context.object; o.name='Frosted bulb'; o.data.materials.append(bulbmat)
for p in o.data.polygons: p.use_smooth=True
bpy.ops.object.light_add(type='POINT',location=top+axis*.23); bpy.context.object.name='Warm bulb light'; bpy.context.object.data.energy=18; bpy.context.object.data.color=(1,.73,.43); bpy.context.object.data.shadow_soft_size=.06
curve('Arm electrical flex',[(0,.038,.22),(0,.038,1.40),(-.025,.07,1.51),(.40,.07,1.97),(.91,.07,1.80),tuple(top)],.006,dark)
curve('Floor power cord',[(0,.05,.07),(-.24,.18,.018),(-.55,.30,.013),(-.75,.10,.013),(-.94,.21,.013),(-1.07,.37,.013)],.008,dark)
cube('Inline foot switch',(-.60,.245,.032),(.12,.08,.044),dark,.018)
cube('Power plug',(-1.10,.40,.026),(.08,.07,.045),dark,.012)
for x in [-1.12,-1.08]: cylinder('Plug pin',(x,.43,.027),(x,.47,.027),.006,brass)
floor=mat('Studio warm gray',(.30,.29,.26),.9); cube('Floor',(0,0,-.045),(200,200,.08),floor,0)
scene=bpy.context.scene; scene.world.use_nodes=True; scene.world.node_tree.nodes['Background'].inputs[1].default_value=.25
for loc,energy,size in [((1,-3,4),500,3),((-3,-1,3),350,2),((2,3,4),650,3)]:
    bpy.ops.object.light_add(type='AREA',location=loc); o=bpy.context.object; o.data.energy=energy; o.data.size=size; o.rotation_euler=(Vector((.3,0,1))-o.location).to_track_quat('-Z','Y').to_euler()
bpy.ops.object.camera_add(location=(3,-5,3)); cam=bpy.context.object; cam.rotation_euler=(Vector((.15,0,1))-cam.location).to_track_quat('-Z','Y').to_euler(); cam.data.type='ORTHO'; cam.data.ortho_scale=2.8; scene.camera=cam
scene.render.engine='CYCLES'; scene.cycles.samples=64; scene.render.resolution_x=1100; scene.render.resolution_y=1400; scene.render.resolution_percentage=100
