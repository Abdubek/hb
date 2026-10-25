import bpy, math
from mathutils import Vector
bpy.ops.object.select_all(action='SELECT'); bpy.ops.object.delete(use_global=False)
def mat(n,c,metal=0):
 m=bpy.data.materials.new(n); m.diffuse_color=(*c,1); m.use_nodes=True; p=m.node_tree.nodes.get('Principled BSDF'); p.inputs['Base Color'].default_value=(*c,1); p.inputs['Metallic'].default_value=metal; p.inputs['Roughness'].default_value=.33; return m
def box(n,p,s,m,b=.04):
 bpy.ops.mesh.primitive_cube_add(size=1,location=p); o=bpy.context.object; o.name=n; o.dimensions=s; bpy.ops.object.transform_apply(location=False,rotation=False,scale=True); o.data.materials.append(m)
 if b: mod=o.modifiers.new('Edge radii','BEVEL'); mod.width=b; mod.segments=3; o.modifiers.new('Weighted normals','WEIGHTED_NORMAL')
 return o
def rod(n,a,b,r,m):
 d=Vector(b)-Vector(a); bpy.ops.mesh.primitive_cylinder_add(vertices=32,radius=r,depth=d.length,location=(Vector(a)+Vector(b))/2); o=bpy.context.object; o.name=n; o.rotation_euler=d.to_track_quat('Z','Y').to_euler(); o.data.materials.append(m); return o
shell=mat('Ivory polymer',(.82,.85,.84)); carbon=mat('Graphite composite',(.035,.045,.055)); orange=mat('Orange accents',(1,.20,.025)); metal=mat('Motor aluminum',(.32,.37,.40),.8); dark=mat('Propeller graphite',(.055,.065,.075),.25); glass=mat('Camera glass',(.015,.09,.14),.65); floor=mat('Studio floor',(.18,.22,.27))
box('Lower fuselage',(0,0,.88),(1.5,1.85,.32),carbon,.16); box('Upper aerodynamic body',(0,0,1.12),(1.43,1.75,.40),shell,.19); box('Battery hatch',(0,.18,1.335),(.87,1.04,.05),carbon,.09); box('Battery latch',(0,.72,1.36),(.3,.09,.045),orange,.018)
for x in [-.49,.49]:
 for y in [-.43,-.26,-.09,.08]: box('Cooling slot',(x,y,1.323),(.085,.095,.026),carbon,.016)
for sx in [-1,1]:
 for sy in [-1,1]:
  end=Vector((sx*1.75,sy*1.65,1.03)); start=Vector((sx*.53,sy*.53,.96)); d=end-start
  arm=box('Diagonal structural arm',(start+end)/2,(.27,.24,d.length),carbon,.055); arm.rotation_euler=d.to_track_quat('Z','Y').to_euler()
  rod('Motor mounting plate',(end.x,end.y,.96),(end.x,end.y,1.08),.25,carbon); rod('Brushless motor',(end.x,end.y,1.08),(end.x,end.y,1.37),.195,metal); rod('Motor top bell',(end.x,end.y,1.32),(end.x,end.y,1.4),.20,orange if sy<0 else carbon)
  for j in range(12):
   a=j*math.tau/12; xx=end.x+.196*math.cos(a); yy=end.y+.196*math.sin(a); rod('Motor cooling groove',(xx,yy,1.13),(xx,yy,1.29),.011,carbon)
  theta=(sx*sy)*.32
  # Two swept, tapered blades; each mesh is closed with slight pitch.
  outline=[(.10,-.065),(.35,-.12),(.88,-.06),(1.12,.015),(1.16,.08),(.99,.16),(.38,.14),(.10,.065)]
  for k in [0,1]:
   a=theta+k*math.pi; verts=[]
   for dz in [-.018,.018]:
    for u,v in outline: verts.append((end.x+u*math.cos(a)-v*math.sin(a),end.y+u*math.sin(a)+v*math.cos(a),1.45+dz+v*.22))
   N=len(outline); faces=[tuple(range(N-1,-1,-1)),tuple(range(N,2*N))]+[(j,(j+1)%N,(j+1)%N+N,j+N) for j in range(N)]
   me=bpy.data.meshes.new('Blade mesh'); me.from_pydata(verts,[],faces); me.update(); ob=bpy.data.objects.new('Swept propeller blade',me); bpy.context.collection.objects.link(ob); ob.data.materials.append(dark); bevel=ob.modifiers.new('Blade edge','BEVEL'); bevel.width=.012; bevel.segments=2; ob.modifiers.new('Blade normals','WEIGHTED_NORMAL')
  rod('Propeller hub',(end.x,end.y,1.40),(end.x,end.y,1.51),.115,carbon); rod('Retaining nut',(end.x,end.y,1.51),(end.x,end.y,1.57),.058,metal)
for x in [-.66,.66]:
 for y in [-.55,.55]: rod('Landing strut',(x*.78,y,.78),(x,y,.17),.045,metal)
 rod('Landing skid',(x,-.91,.13),(x,.91,.13),.065,carbon)
rod('Camera suspension',(0,-.54,.78),(0,-.54,.55),.07,metal); box('Camera gimbal',(0,-.64,.46),(.53,.40,.35),carbon,.075); rod('Camera lens rim',(0,-.83,.46),(0,-.98,.46),.15,metal); rod('Camera front glass',(0,-.985,.46),(0,-1.005,.46),.119,glass)
for x in [-.49,.49]: box('Front orange marker',(x,-.885,1.11),(.24,.035,.11),orange,.025)
box('Ground',(0,0,-.09),(200,200,.1),floor,0)
bpy.context.scene.world.color=(.22,.22,.22)
for loc,energy,size in [((2,-4,8),1100,5),((-5,2,5),900,4)]:
 bpy.ops.object.light_add(type='AREA',location=loc); o=bpy.context.object; o.data.energy=energy; o.data.size=size; o.rotation_euler=(Vector((0,0,1))-o.location).to_track_quat('-Z','Y').to_euler()
bpy.ops.object.camera_add(location=(7,-9,8)); cam=bpy.context.object; cam.rotation_euler=(Vector((0,0,.8))-cam.location).to_track_quat('-Z','Y').to_euler(); cam.data.type='ORTHO'; cam.data.ortho_scale=8.4; bpy.context.scene.camera=cam
s=bpy.context.scene; s.render.engine='CYCLES'; s.render.resolution_x=1400; s.render.resolution_y=1100; s.render.resolution_percentage=100
