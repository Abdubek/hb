import bpy, math
from mathutils import Vector
bpy.ops.object.select_all(action='SELECT'); bpy.ops.object.delete(use_global=False)
def mat(n,c,metal=0,glow=0):
 m=bpy.data.materials.new(n); m.diffuse_color=(*c,1); m.use_nodes=True; p=m.node_tree.nodes.get('Principled BSDF'); p.inputs['Base Color'].default_value=(*c,1); p.inputs['Metallic'].default_value=metal; p.inputs['Roughness'].default_value=.5
 if glow: p.inputs['Emission Color'].default_value=(*c,1); p.inputs['Emission Strength'].default_value=glow
 return m
def box(n,p,s,m,b=0):
 bpy.ops.mesh.primitive_cube_add(size=1,location=p); o=bpy.context.object; o.name=n; o.dimensions=s; bpy.ops.object.transform_apply(location=False,rotation=False,scale=True); o.data.materials.append(m)
 if b: mod=o.modifiers.new('Rounded edges','BEVEL'); mod.width=b; mod.segments=3; o.modifiers.new('Normals','WEIGHTED_NORMAL')
 return o
def cyl(n,p,r,d,m):
 bpy.ops.mesh.primitive_cylinder_add(vertices=24,radius=r,depth=d,location=p); o=bpy.context.object; o.name=n; o.data.materials.append(m); return o
asphalt=mat('Asphalt',(.075,.09,.105)); paving=mat('Sidewalk',(.57,.57,.52)); curb=mat('Concrete curb',(.73,.73,.68)); white=mat('Road white',(.92,.91,.8)); yellow=mat('Road yellow',(1,.65,.055)); metal=mat('Signal poles',(.21,.25,.27),.75); black=mat('Dark housing',(.018,.023,.026)); red=mat('Lit red',(.95,.015,.009),glow=3); green=mat('Lit green',(.025,.9,.18),glow=3); offred=mat('Unlit red',(.16,.012,.01)); offgreen=mat('Unlit green',(.008,.12,.04)); amber=mat('Unlit amber',(.23,.095,.006)); tactile=mat('Tactile paving',(.82,.48,.09))
box('Street base',(0,0,-.16),(18,18,.32),asphalt,.12)
for sx in [-1,1]:
 for sy in [-1,1]:
  box('Raised corner sidewalk',(sx*6.3,sy*6.3,.10),(5.4,5.4,.2),paving,.07)
  box('Curb along street',(sx*3.68,sy*6.3,.12),(.16,5.4,.24),curb,.035); box('Curb return',(sx*6.3,sy*3.68,.12),(5.4,.16,.24),curb,.035)
  for v in [4.4,5.6,6.8,8]:
   box('Paving joint',(sx*v,sy*6.3,.205),(.016,5.25,.009),curb); box('Paving joint',(sx*6.3,sy*v,.205),(5.25,.016,.009),curb)
# Approach markings and four zebra crossings.
for angle in [0,math.pi/2,math.pi,3*math.pi/2]:
 def place(n,x,y,z,s,m,b=0):
  X=x*math.cos(angle)-y*math.sin(angle); Y=x*math.sin(angle)+y*math.cos(angle); o=box(n,(X,Y,z),s,m,b); o.rotation_euler.z=angle; return o
 for x in [-.12,.12]: place('Double center line',x,6.8,.012,(.075,4.1,.022),yellow)
 for x in [-2.85,-1.9,-.95,0,.95,1.9,2.85]: place('Zebra stripe',x,4.25,.014,(.55,1.25,.025),white)
 place('Stop line',1.78,5.25,.014,(3.2,.16,.025),white)
 place('Tactile pad',3.98,4.25,.216,(.55,1.25,.025),tactile,.025)
 for yy in [6.3,8]: place('Lane edge',3.3,yy,.014,(.09,1,.025),white)
 # Pole and signal face oriented toward each approaching lane.
 px,py=3.99,3.28
 X=px*math.cos(angle)-py*math.sin(angle); Y=px*math.sin(angle)+py*math.cos(angle)
 cyl('Pole plinth',(X,Y,.30),.22,.23,metal); cyl('Signal pole',(X,Y,2.02),.08,3.6,metal)
 place('Yellow signal shell',px,py,3.5,(.57,.35,1.35),yellow,.085); place('Black signal face',px,py+.188,3.5,(.48,.055,1.24),black,.04)
 active_green=angle in [0,math.pi]
 for z,ma in [(3.91,offred if active_green else red),(3.5,amber),(3.09,green if active_green else offgreen)]:
  lx=px*math.cos(angle)-(py+.24)*math.sin(angle); ly=px*math.sin(angle)+(py+.24)*math.cos(angle)
  o=cyl('Circular lens',(lx,ly,z),.155,.035,ma); o.rotation_euler=(math.pi/2,0,angle)
  place('Lens rain visor',px,py+.31,z+.18,(.38,.29,.045),black,.02)
 place('Pedestrian button box',px,py+.13,1.25,(.19,.16,.28),yellow,.025)
for sx in [-1,1]:
 for sy in [-1,1]:
  for x,y in [(4.2,5.5),(4.2,7),(5.5,4.2),(7,4.2)]:
   X,Y=sx*x,sy*y; cyl('Bollard base',(X,Y,.24),.18,.09,metal); cyl('Bollard',(X,Y,.75),.095,1.0,black); cyl('Reflective bollard band',(X,Y,1.02),.099,.15,yellow)
   bpy.ops.mesh.primitive_uv_sphere_add(segments=16,ring_count=8,radius=.096,location=(X,Y,1.25)); bpy.context.object.data.materials.append(black)
bpy.context.scene.world.color=(.28,.28,.28)
bpy.ops.object.light_add(type='AREA',location=(0,-4,14)); bpy.context.object.data.energy=2500; bpy.context.object.data.size=10
bpy.ops.object.light_add(type='SUN',rotation=(.5,-.3,-.4)); bpy.context.object.data.energy=2
bpy.ops.object.camera_add(location=(18,-23,23)); cam=bpy.context.object; cam.rotation_euler=(Vector((0,0,.5))-cam.location).to_track_quat('-Z','Y').to_euler(); cam.data.type='ORTHO'; cam.data.ortho_scale=26; bpy.context.scene.camera=cam
s=bpy.context.scene; s.render.engine='CYCLES'; s.render.resolution_x=1400; s.render.resolution_y=1200; s.render.resolution_percentage=100
