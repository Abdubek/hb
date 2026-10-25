import bpy, math
from mathutils import Vector
bpy.ops.object.select_all(action='SELECT'); bpy.ops.object.delete(use_global=False)
def mat(n,c,metal=0,rough=.35):
 m=bpy.data.materials.new(n); m.diffuse_color=(*c,1); m.use_nodes=True; p=m.node_tree.nodes.get('Principled BSDF'); p.inputs['Base Color'].default_value=(*c,1); p.inputs['Metallic'].default_value=metal; p.inputs['Roughness'].default_value=rough; return m
def rod(n,a,b,r,m,vertices=40):
 a,b=Vector(a),Vector(b); d=b-a; bpy.ops.mesh.primitive_cylinder_add(vertices=vertices,radius=r,depth=d.length,location=(a+b)/2); o=bpy.context.object; o.name=n; o.rotation_euler=d.to_track_quat('Z','Y').to_euler(); o.data.materials.append(m); bevel=o.modifiers.new('Machined edges','BEVEL'); bevel.width=min(.018,r*.15); bevel.segments=2; o.modifiers.new('Weighted normals','WEIGHTED_NORMAL'); return o
def box(n,p,s,m,b=.03):
 bpy.ops.mesh.primitive_cube_add(size=1,location=p); o=bpy.context.object; o.name=n; o.dimensions=s; bpy.ops.object.transform_apply(location=False,rotation=False,scale=True); o.data.materials.append(m); mod=o.modifiers.new('Rounded edges','BEVEL'); mod.width=b; mod.segments=3; o.modifiers.new('Weighted normals','WEIGHTED_NORMAL'); return o
ivory=mat('Optical tube ivory',(.87,.84,.73),.15); black=mat('Black anodized',(.028,.035,.045),.55); silver=mat('Brushed aluminum',(.48,.54,.58),.8); blue=mat('Blue hardware',(.045,.19,.34),.65); rubber=mat('Rubber feet',(.025,.028,.032),0,.8); lens=mat('Coated objective',(.025,.14,.20),.7,.13); floor=mat('Backdrop',(.18,.205,.24))
rod('Tripod center hub',(0,0,1.75),(0,0,2.13),.23,black)
for i in range(3):
 a=math.radians(30)+i*math.tau/3; radial=Vector((math.cos(a),math.sin(a),0)); top=radial*.17+Vector((0,0,1.91)); foot=radial*1.16+Vector((0,0,.12)); mid=top.lerp(foot,.59)
 rod('Upper tripod leg',top,mid,.082,silver); rod('Telescopic lower leg',mid,foot,.060,silver); rod('Leg locking collar',mid.lerp(top,.07),mid.lerp(foot,.10),.105,black); rod('Rubber foot',foot+Vector((0,0,.06)),foot-Vector((0,0,.075)),.09,rubber)
 brace=top.lerp(foot,.58); rod('Spreader brace',(0,0,.88),brace,.025,black); rod('Leg clamp screw',mid,mid+Vector((0,-.15,0)),.038,blue)
rod('Spreader hub',(0,0,.80),(0,0,.94),.12,black); rod('Azimuth bearing',(0,0,2.10),(0,0,2.28),.29,blue); rod('Mount column',(0,0,2.25),(0,0,2.64),.15,black)
center=Vector((0,0,2.83)); axis=Vector((0,.93,.367)).normalized(); side=Vector((1,0,0)); up=axis.cross(side).normalized()
rod('Altitude axle',(-.49,0,2.83),(.49,0,2.83),.13,silver)
for x in [-.43,.43]: box('Fork arm',(x,0,2.61),(.13,.25,.68),black)
rod('Optical tube',center-axis*.93,center+axis*.95,.32,ivory)
for t in [-.52,.50]:
 p=center+axis*t; rod('Tube mounting band',p-axis*.055,p+axis*.055,.342,black)
rod('Rear cell',center-axis*1.01,center-axis*.87,.338,blue)
front=center+axis*1.08
# Open annular dew shield with visible inner wall.
verts=[]; N=64
for t,r in [(.85,.365),(1.27,.365),(.85,.329),(1.27,.329)]:
 for j in range(N):
  a=j*math.tau/N; p=center+axis*t+r*(side*math.cos(a)+up*math.sin(a)); verts.append(tuple(p))
faces=[]
for j in range(N):
 k=(j+1)%N; faces.extend([(j,k,N+k,N+j),(2*N+j,3*N+j,3*N+k,2*N+k),(N+j,N+k,3*N+k,3*N+j),(j,2*N+j,2*N+k,k)])
me=bpy.data.meshes.new('Dew shield mesh'); me.from_pydata(verts,[],faces); me.update(); ob=bpy.data.objects.new('Open dew shield',me); bpy.context.collection.objects.link(ob); ob.data.materials.append(black)
rod('Objective glass',front-axis*.024,front,.325,lens)
rear=center-axis*1.0; rod('Focuser drawtube',rear-axis*.36,rear,.12,silver); rod('Eyepiece barrel',rear-axis*.53,rear-axis*.32,.15,black); rod('Eyepiece glass',rear-axis*.54,rear-axis*.532,.105,lens)
def knob(n,p,d,r):
 p,d=Vector(p),Vector(d).normalized(); rod(n,p,p+d*.12,r,black,32); u=d.cross(Vector((0,0,1)))
 if u.length<.01: u=d.cross(Vector((0,1,0)))
 u.normalize(); v=d.cross(u)
 for j in range(20):
  a=j*math.tau/20; q=p+r*(u*math.cos(a)+v*math.sin(a)); rod('Knurl ridge',q,q+d*.12,.009,silver,8)
knob('Altitude tension knob',(.49,0,2.83),(1,0,0),.17); knob('Azimuth lock knob',(0,-.24,2.18),(0,-1,0),.11)
for s in [-1,1]:
 p=rear-axis*.17+side*s*.11; rod('Focus spindle',p,p+side*s*.13,.035,silver); knob('Focus adjustment',p+side*s*.13,side*s,.105)
for t in [-.25,.35]:
 p=center+axis*t+up*.30; rod('Finder support',p,p+up*.22,.032,black)
fc=center+up*.53+side*.045; rod('Finder scope',fc-axis*.37,fc+axis*.39,.079,ivory); rod('Finder front rim',fc+axis*.35,fc+axis*.44,.095,black); rod('Finder lens',fc+axis*.442,fc+axis*.45,.074,lens)
box('Ground',(0,0,-.075),(200,200,.1),floor)
bpy.context.scene.world.color=(.22,.22,.22)
for loc,e in [((4,4,7),1000),((-4,-3,5),800)]:
 bpy.ops.object.light_add(type='AREA',location=loc); o=bpy.context.object; o.data.energy=e; o.data.size=5; o.rotation_euler=(Vector((0,0,2))-o.location).to_track_quat('-Z','Y').to_euler()
bpy.ops.object.camera_add(location=(6,8,5)); cam=bpy.context.object; cam.rotation_euler=(Vector((0,0,1.8))-cam.location).to_track_quat('-Z','Y').to_euler(); cam.data.type='ORTHO'; cam.data.ortho_scale=5.6; bpy.context.scene.camera=cam
s=bpy.context.scene; s.render.engine='CYCLES'; s.render.resolution_x=1100; s.render.resolution_y=1300; s.render.resolution_percentage=100
