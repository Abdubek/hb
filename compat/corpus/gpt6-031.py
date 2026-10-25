import bpy, math
from mathutils import Vector
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)
def mat(n,c,metal=0,rough=.45,glow=0):
 m=bpy.data.materials.new(n); m.diffuse_color=(*c,1); m.use_nodes=True; p=m.node_tree.nodes.get('Principled BSDF'); p.inputs['Base Color'].default_value=(*c,1); p.inputs['Metallic'].default_value=metal; p.inputs['Roughness'].default_value=rough
 if glow: p.inputs['Emission Color'].default_value=(*c,1); p.inputs['Emission Strength'].default_value=glow
 return m
def cube(n,loc,scale,m,b=.0):
 bpy.ops.mesh.primitive_cube_add(size=1,location=loc); o=bpy.context.object; o.name=n; o.dimensions=scale; bpy.ops.object.transform_apply(location=False,rotation=False,scale=True); o.data.materials.append(m)
 if b: mod=o.modifiers.new('Soft edges','BEVEL'); mod.width=b; mod.segments=2; o.modifiers.new('Normals','WEIGHTED_NORMAL')
 return o
def rod(n,a,b,r,m):
 d=Vector(b)-Vector(a); bpy.ops.mesh.primitive_cylinder_add(vertices=24,radius=r,depth=d.length,location=(Vector(a)+Vector(b))/2); o=bpy.context.object; o.name=n; o.rotation_euler=d.to_track_quat('Z','Y').to_euler(); o.data.materials.append(m); return o
steel=mat('Rail steel',(.31,.35,.38),.85); wood=mat('Weathered sleepers',(.16,.095,.055)); gravel=mat('Ballast',(.25,.27,.28)); ground=mat('Ground',(.15,.20,.13)); black=mat('Signal enamel',(.024,.03,.035),.4); silver=mat('Galvanized metal',(.52,.56,.57),.75); red=mat('Red lens',(.22,.009,.008)); amber=mat('Amber lens',(.28,.12,.008)); green=mat('Active green',(.03,1,.19),glow=4); white=mat('Sign white',(.85,.86,.77))
cube('Ground',(0,0,-.22),(13,8,.3),ground,.08)
cube('Ballast bed',(0,0,-.025),(11,3.1,.3),gravel,.16)
for i in range(17):
 x=-5+i*.625; cube('Timber sleeper',(x,0,.15),(.24,2.65,.19),wood,.025)
 for y in [-.78,.78]:
  cube('Tie plate',(x,y,.267),(.34,.34,.05),steel,.012)
  for yy in [y-.12,y+.12]: rod('Fastening bolt',(x,yy,.29),(x,yy,.335),.032,steel)
for y in [-.78,.78]:
 cube('Rail foot',(0,y,.31),(11,.19,.06),steel,.012); cube('Rail web',(0,y,.405),(11,.07,.15),steel,.008); cube('Polished rail head',(0,y,.50),(11,.125,.075),steel,.024)
cube('Concrete signal footing',(2,2,.16),(.85,.8,.48),gravel,.08)
cube('Anchor plate',(2,2,.43),(.55,.5,.06),steel,.02)
for x in [1.8,2.2]:
 for y in [1.83,2.17]: rod('Anchor bolt',(x,y,.45),(x,y,.52),.035,silver)
rod('Signal mast',(2,2,.45),(2,2,4.55),.105,silver)
cube('Signal backboard',(2,1.94,4.28),(.88,.23,2.05),black,.16)
for z,lens in [(4.88,red),(4.28,amber),(3.68,green)]:
 rod('Lens bezel',(2,1.79,z),(2,1.68,z),.245,silver); rod('Dark lens surround',(2,1.67,z),(2,1.61,z),.225,black); rod('Signal glass',(2,1.60,z),(2,1.575,z),.177,lens)
 # Half-cylinder hood, open downward and toward the track.
 verts=[]
 for yy in [1.72,1.23]:
  for j in range(17):
   t=j*math.pi/16; verts.append((2+.255*math.cos(t),yy,z+.255*math.sin(t)))
 faces=[(j,j+1,j+18,j+17) for j in range(16)]; me=bpy.data.meshes.new('Hood mesh'); me.from_pydata(verts,[],faces); me.update(); ob=bpy.data.objects.new('Signal visor',me); bpy.context.collection.objects.link(ob); ob.data.materials.append(black); ob.modifiers.new('Metal thickness','SOLIDIFY').thickness=.025
for x in [1.76,2.24]: rod('Ladder upright',(x,2.3,.6),(x,2.3,4.2),.025,silver)
for i in range(12): rod('Ladder rung',(1.76,2.3,.65+i*.29),(2.24,2.3,.65+i*.29),.022,silver)
cube('Equipment cabinet',(3,2,.72),(.65,.55,1.1),silver,.055); cube('Cabinet door',(3,1.71,.72),(.55,.035,.95),black,.015)
cube('Signal identification plate',(2,1.84,2.6),(.49,.045,.36),white,.015)
bpy.ops.object.text_add(location=(1.815,1.806,2.49),rotation=(math.pi/2,0,0)); text=bpy.context.object; text.name='Signal number'; text.data.body='S 12'; text.data.size=.20; text.data.extrude=.001; text.data.materials.append(black)
world=bpy.context.scene.world; world.color=(.22,.22,.22)
bpy.ops.object.light_add(type='AREA',location=(1,-3,9)); bpy.context.object.data.energy=1700; bpy.context.object.data.shape='DISK'; bpy.context.object.data.size=7
bpy.ops.object.light_add(type='AREA',location=(-5,4,6)); bpy.context.object.data.energy=1000; bpy.context.object.data.size=6
bpy.ops.object.camera_add(location=(11,-13,9)); cam=bpy.context.object; cam.rotation_euler=(Vector((0,0,1.6))-cam.location).to_track_quat('-Z','Y').to_euler(); cam.data.type='ORTHO'; cam.data.ortho_scale=15; bpy.context.scene.camera=cam
scene=bpy.context.scene; scene.render.engine='CYCLES'; scene.render.resolution_x=1400; scene.render.resolution_y=1000; scene.render.resolution_percentage=100
