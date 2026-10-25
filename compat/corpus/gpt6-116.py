import bpy, math, random
from mathutils import Vector
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)
random.seed(16)

def mat(name, color, metallic=0, rough=.5):
    m=bpy.data.materials.new(name); m.diffuse_color=(*color,1); m.use_nodes=True
    p=m.node_tree.nodes.get('Principled BSDF'); p.inputs['Base Color'].default_value=(*color,1); p.inputs['Metallic'].default_value=metallic; p.inputs['Roughness'].default_value=rough
    return m
soil=mat('Dry meadow',(.24,.30,.12)); gravel=mat('Service road gravel',(.48,.43,.33)); steel=mat('Galvanized steel',(.48,.55,.59),.8,.3); blue=mat('Photovoltaic cells',(.014,.045,.115),.55,.22); silver=mat('Cell conductors',(.34,.53,.67),.7,.3); concrete=mat('Concrete foundations',(.53,.52,.46)); white=mat('Electrical cabinets',(.76,.8,.77),.3)

def height(x,y): return .045*x+.025*y+.23*math.sin(x*.18)*math.cos(y*.15)
def mesh(name,v,f,m):
    me=bpy.data.meshes.new(name); me.from_pydata(v,[],f); me.update(); ob=bpy.data.objects.new(name,me); bpy.context.collection.objects.link(ob); ob.data.materials.append(m); return ob

def box(name,loc,scale,m,rot=None):
    bpy.ops.mesh.primitive_cube_add(size=1,location=loc); o=bpy.context.object; o.name=name; o.dimensions=scale
    if rot: o.rotation_euler=rot
    bpy.ops.object.transform_apply(location=False,rotation=False,scale=True); o.data.materials.append(m); return o

def rod(name,a,b,r,m):
    d=Vector(b)-Vector(a); bpy.ops.mesh.primitive_cylinder_add(vertices=10,radius=r,depth=d.length,location=(Vector(a)+Vector(b))/2); o=bpy.context.object; o.name=name; o.rotation_euler=d.to_track_quat('Z','Y').to_euler(); o.data.materials.append(m)
# A continuous, gently undulating terrain mesh.
nx,ny=80,66
v=[(x,y,height(x,y)) for y in [-20+40*j/ny for j in range(ny+1)] for x in [-25+50*i/nx for i in range(nx+1)]]
f=[]
for j in range(ny):
    for i in range(nx):
        k=j*(nx+1)+i; f.append((k,k+1,k+nx+2,k+nx+1))
mesh('Sloping meadow',v,f,soil)
def road(name,x0,x1,y0,y1):
    nx=max(2,int((x1-x0)*3)); ny=max(2,int((y1-y0)*3)); v=[]; f=[]
    for j in range(ny+1):
        y=y0+(y1-y0)*j/ny
        for i in range(nx+1):
            x=x0+(x1-x0)*i/nx; v.append((x,y,height(x,y)+.025))
    for j in range(ny):
        for i in range(nx):
            k=j*(nx+1)+i; f.append((k,k+1,k+nx+2,k+nx+1))
    mesh(name,v,f,gravel)
road('Central maintenance avenue',-1.35,1.35,-18,18)
road('South access road',-23,23,-18,-15)
road('North service road',-23,23,15,18)
for yy in [-9,-3,3,9]: road('Cross aisle',-22,22,yy-.48,yy+.48)
# Each table follows its local terrain grade; individual cell tiles remain planar.
for yy in [-12,-6,0,6,12]:
    for xx in [-18,-12,-6,6,12,18]:
        eps=.1; sx=(height(xx+eps,yy)-height(xx-eps,yy))/(2*eps)
        u=Vector((1,0,sx)).normalized(); vv=Vector((0,1,.48)); vv=(vv-u*vv.dot(u)).normalized(); normal=u.cross(vv).normalized()
        from mathutils import Matrix
        rot=Matrix((u,vv,normal)).transposed().to_euler(); center=Vector((xx,yy,height(xx,yy)+1.65))
        def local(a,b,c=0): return center+u*a+vv*b+normal*c
        box('Aluminum table frame',local(0,0), (4.95,2.85,.12),steel,rot)
        for pi in range(4):
            for pj in range(2):
                a=(pi-1.5)*1.21; b=(pj-.5)*1.37
                box('Dark panel backing',local(a,b,.075),(1.15,1.31,.045),blue,rot)
                for ci in range(6):
                    for cj in range(6):
                        ca=a+(ci-2.5)*.183; cb=b+(cj-2.5)*.207
                        box('Silicon cell',local(ca,cb,.102),(.171,.195,.008),blue,rot)
                for ci in range(6): box('Fine bus line',local(a+(ci-2.5)*.183,b,.108),(.006,1.23,.003),silver,rot)
        for a in [-1.85,1.85]:
            for b in [-.92,.92]:
                top=local(a,b,-.09); ground=Vector((top.x,top.y,height(top.x,top.y)))
                box('Footing',ground+Vector((0,0,.08)),(.42,.42,.18),concrete)
                rod('Support post',ground,top,.055,steel)
            rod('Diagonal brace',local(a,-.9,-.2),local(a,.9,-.7),.034,steel)
# A small inverter station beside the access road.
for x in [3,4.5,6]:
    z=height(x,-14)
    box('Inverter pad',(x,-14,z+.12),(1.25,1.1,.24),concrete)
    box('Inverter cabinet',(x,-14,z+.85),(.85,.7,1.35),white)
    for k in range(6): box('Vent slot',(x,-14.356,z+.6+k*.09),(.58,.013,.028),steel)
world=bpy.context.scene.world; world.use_nodes=True; world.node_tree.nodes['Background'].inputs[0].default_value=(.57,.72,.88,1); world.node_tree.nodes['Background'].inputs[1].default_value=.4
bpy.ops.object.light_add(type='SUN',location=(0,0,20)); bpy.context.object.rotation_euler=(.45,-.5,-.4); bpy.context.object.data.energy=3
bpy.ops.object.light_add(type='AREA',location=(-10,-8,24)); bpy.context.object.data.energy=1800; bpy.context.object.data.shape='DISK'; bpy.context.object.data.size=20
bpy.ops.object.camera_add(location=(39,-46,35)); cam=bpy.context.object; cam.rotation_euler=(Vector((0,0,0))-cam.location).to_track_quat('-Z','Y').to_euler(); cam.data.type='ORTHO'; cam.data.ortho_scale= sixty=60; bpy.context.scene.camera=cam
bpy.context.scene.render.engine='CYCLES'
bpy.context.scene.render.resolution_x=1600; bpy.context.scene.render.resolution_y=1100; bpy.context.scene.render.resolution_percentage=100
