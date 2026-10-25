import bpy, math
from mathutils import Vector
bpy.ops.object.select_all(action='SELECT'); bpy.ops.object.delete(use_global=False)
def mat(name,c,metal=0):
    m=bpy.data.materials.new(name); m.diffuse_color=(*c,1); m.use_nodes=True; p=m.node_tree.nodes.get('Principled BSDF'); p.inputs['Base Color'].default_value=(*c,1); p.inputs['Metallic'].default_value=metal; p.inputs['Roughness'].default_value=.55; return m
concrete=mat('Warm structural concrete',(.49,.47,.42)); asphalt=mat('Asphalt wearing course',(.085,.095,.105)); steel=mat('Galvanized guard rails',(.58,.64,.68),.75); yellow=mat('Traffic yellow',(.95,.64,.045)); white=mat('White markings',(.85,.85,.78)); ground=mat('Site paving',(.23,.26,.27))
def mesh(name,v,f,m):
    me=bpy.data.meshes.new(name); me.from_pydata(v,[],f); me.update(); o=bpy.data.objects.new(name,me); bpy.context.collection.objects.link(o); o.data.materials.append(m); return o
def box(name,loc,size,m):
    bpy.ops.mesh.primitive_cube_add(size=1,location=loc); o=bpy.context.object; o.name=name; o.dimensions=size; bpy.ops.object.transform_apply(location=False,rotation=False,scale=True); o.data.materials.append(m); return o
def rod(name,a,b,r,m):
    a,b=Vector(a),Vector(b); d=b-a; bpy.ops.mesh.primitive_cylinder_add(vertices=12,radius=r,depth=d.length,location=(a+b)/2); o=bpy.context.object; o.name=name; o.rotation_euler=d.to_track_quat('Z','Y').to_euler(); o.data.materials.append(m)
def curve(name,pts,r,m):
    cu=bpy.data.curves.new(name,'CURVE'); cu.dimensions='3D'; cu.resolution_u=1; cu.bevel_depth=r; cu.bevel_resolution=3; sp=cu.splines.new('POLY'); sp.points.add(len(pts)-1)
    for p,co in zip(sp.points,pts): p.co=(*co,1)
    o=bpy.data.objects.new(name,cu); bpy.context.collection.objects.link(o); o.data.materials.append(m)
turns=2.25; end=turns*2*math.pi; pitch=3.5; base=.4; inner=4.5; outer=9; steps=540

def z(t): return base+pitch*t/(2*math.pi)
def point(r,t,dz=0): return (r*math.cos(t),r*math.sin(t),z(t)+dz)
def ribbon(name,r0,r1,t0,t1,n,offset,thickness,m):
    v=[]
    for i in range(n+1):
        t=t0+(t1-t0)*i/n
        for dz in [offset,offset-thickness]:
            for r in [r0,r1]: v.append(point(r,t,dz))
    f=[]
    for i in range(n):
        k=4*i; f.extend([(k,k+1,k+5,k+4),(k+2,k+6,k+7,k+3),(k,k+4,k+6,k+2),(k+1,k+3,k+7,k+5)])
    f.extend([(0,2,3,1),(4*n,4*n+1,4*n+3,4*n+2)]); return mesh(name,v,f,m)
ribbon('Continuous helical concrete deck',inner,outer,0,end,steps,0,.32,concrete)
ribbon('Asphalt surface',inner+.12,outer-.12,0,end,steps,.026,.026,asphalt)
for r in [inner+.14,outer-.14]:
    ribbon('Raised protective curb',r-.12,r+.12,0,end,steps,.18,.2,concrete)
    for h in [.57,1.02]: curve('Continuous tubular guardrail',[point(r,end*i/steps,h) for i in range(steps+1)],.057,steel)
    for i in range(114):
        t=end*i/113; rod('Guardrail upright',point(r,t,.16),point(r,t,1.07),.045,steel)
# Two-way lane division and edge lines.
for r in [inner+.45,outer-.45]: ribbon('Continuous white edge stripe',r-.035,r+.035,0,end,steps,.033,.003,white)
for i in range(60):
    t=i*end/60; ribbon('Dashed center marking',6.71,6.79,t,min(t+.115,end),5,.034,.003,yellow)
# Columns sit inside the central void, with radial cantilever beams under each lap.
for i in range(8):
    t=i*2*math.pi/8; r=3.75; maxz=0
    for lap in range(3):
        a=t+lap*2*math.pi
        if a>end: continue
        zz=z(a)-.45; maxz=max(maxz,zz)
        ob=box('Radial concrete support beam',(6.15*math.cos(t),6.15*math.sin(t),zz),(5.1,.38,.48),concrete); ob.rotation_euler.z=t
    rod('Central support column',(r*math.cos(t),r*math.sin(t),0),(r*math.cos(t),r*math.sin(t),maxz+.24),.26,concrete)
    box('Column footing',(r*math.cos(t),r*math.sin(t),.04),(1,1,.18),concrete)
# Tangential approach slabs meet both open ends of the helix.
def landing(t,length,before):
    tangent=Vector((-math.sin(t),math.cos(t),0)); radial=Vector((math.cos(t),math.sin(t),0)); c=radial*6.75+tangent*((-1 if before else 1)*length/2); c.z=z(t)-.16
    o=box('Tangent entry' if before else 'Upper exit landing',c,(4.5,length,.32),concrete); o.rotation_euler.z=t
    c.z=z(t)+.012; o=box('Landing asphalt',c,(4.24,length,.025),asphalt); o.rotation_euler.z=t
    for r in [inner+.14,outer-.14]:
        a=Vector(point(r,t,1.02)); b=a+tangent*((-1 if before else 1)*length); curve('Landing rail',[a,b],.057,steel)
        for k in range(5):
            p=a+(b-a)*k/4; rod('Landing rail post',p-Vector((0,0,.86)),p,.045,steel)
    if not before:
        for r in [5,8.5]:
            p=radial*r+tangent*(length-.4); rod('Exit landing column',(p.x,p.y,0),(p.x,p.y,z(t)-.32),.25,concrete)
landing(0,4,True); landing(end,4,False)
box('Ground',(0,0,-.2),(29,29,.3),ground)
world=bpy.context.scene.world; world.use_nodes=True; world.node_tree.nodes['Background'].inputs[0].default_value=(.65,.73,.82,1); world.node_tree.nodes['Background'].inputs[1].default_value=.45
bpy.ops.object.light_add(type='AREA',location=(0,-8,22)); bpy.context.object.data.energy=2600; bpy.context.object.data.size=15
bpy.ops.object.light_add(type='SUN'); bpy.context.object.rotation_euler=(.4,-.5,-.4); bpy.context.object.data.energy=2
bpy.ops.object.camera_add(location=(24,-29,23)); cam=bpy.context.object; cam.rotation_euler=(Vector((0,0,3.7))-cam.location).to_track_quat('-Z','Y').to_euler(); cam.data.type='ORTHO'; cam.data.ortho_scale=30; bpy.context.scene.camera=cam
bpy.context.scene.render.engine='CYCLES'; bpy.context.scene.render.resolution_x=1500; bpy.context.scene.render.resolution_y=1300; bpy.context.scene.render.resolution_percentage=100
