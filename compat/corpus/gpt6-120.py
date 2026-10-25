import bpy, math, random
from mathutils import Vector
bpy.ops.object.select_all(action='SELECT'); bpy.ops.object.delete(use_global=False)
random.seed(120)
def mat(name,c,rough=.55):
    m=bpy.data.materials.new(name); m.diffuse_color=(*c,1); m.use_nodes=True; p=m.node_tree.nodes.get('Principled BSDF'); p.inputs['Base Color'].default_value=(*c,1); p.inputs['Roughness'].default_value=rough; return m
willow=[mat('Willow tone %d'%i,(.48+i*.035,.265+i*.024,.105+i*.013)) for i in range(5)]; rim_mat=mat('Honey colored rim',(.43,.23,.085)); floor=mat('Warm studio',(.29,.265,.22))
def strip(name,v,f,m,thickness=.035):
    me=bpy.data.meshes.new(name); me.from_pydata(v,[],f); me.update(); o=bpy.data.objects.new(name,me); bpy.context.collection.objects.link(o); o.data.materials.append(m)
    s=o.modifiers.new('Wicker thickness','SOLIDIFY'); s.thickness=thickness; s.offset=0
    b=o.modifiers.new('Rounded strip edges','BEVEL'); b.width=.012; b.segments=2
    for p in me.polygons: p.use_smooth=True
    return o

def tube(name,pts,r,m,closed=False):
    cu=bpy.data.curves.new(name,'CURVE'); cu.dimensions='3D'; cu.bevel_depth=r; cu.bevel_resolution=3; sp=cu.splines.new('POLY'); sp.points.add(len(pts)-1)
    for p,co in zip(sp.points,pts): p.co=(*co,1)
    sp.use_cyclic_u=closed; ob=bpy.data.objects.new(name,cu); bpy.context.collection.objects.link(ob); ob.data.materials.append(m); return ob
N=48; rows=13; z0=.27; step=.22; top=z0+(rows-1)*step; bottom_r=1.68; top_r=2.23; amp=.044

def radius(z):
    t=(z-z0)/(top-z0); return bottom_r+(top_r-bottom_r)*t+.10*math.sin(math.pi*t)
# Upright stakes and horizontal bands alternate above and below at every crossing.
for i in range(N):
    theta=2*math.pi*i/N; v=[]; seg=144
    for k in range(seg+1):
        z=z0+(top-z0)*k/seg; rr=radius(z)+amp*math.cos(math.pi*(z-z0)/step+math.pi*i)
        for side in [-1,1]:
            a=theta+side*.067/radius(z); v.append((rr*math.cos(a),rr*math.sin(a),z))
    f=[(2*k,2*k+1,2*k+3,2*k+2) for k in range(seg)]
    strip('Vertical woven stake %02d'%i,v,f,willow[i%5])
for j in range(rows):
    zc=z0+j*step; v=[]; seg=N*8
    for k in range(seg):
        a=2*math.pi*k/seg
        for side in [-1,1]:
            z=zc+side*.078; rr=radius(z)-amp*math.cos(N*a/2+math.pi*j); v.append((rr*math.cos(a),rr*math.sin(a),z))
    f=[(2*k,2*k+1,2*((k+1)%seg)+1,2*((k+1)%seg)) for k in range(seg)]
    strip('Horizontal over under band %02d'%j,v,f,willow[(j+2)%5])
# Crossing flat strips form a visible woven floor, clipped to a circular footprint.
spacing=.19; base_radius=1.69
for axis in range(2):
    for idx in range(-8,9):
        c=idx*spacing; halfwidth=.074; extent=math.sqrt(max(0,base_radius**2-(abs(c)+halfwidth)**2)); v=[]; seg=80
        for k in range(seg+1):
            t=-extent+2*extent*k/seg
            zz=.245+(1 if axis==0 else -1)*.034*math.cos(math.pi*t/spacing+math.pi*idx)
            for side in [-1,1]:
                cross=c+side*halfwidth; x,y=(t,cross) if axis==0 else (cross,t); v.append((x,y,zz))
        f=[(2*k,2*k+1,2*k+3,2*k+2) for k in range(seg)]
        strip('Crosswoven basket base',v,f,willow[(idx+axis)%5],.028)
# Stacked rim cores are bound with a tightly winding slender cane.
for z,r,thick in [(top+.035,top_r,.085),(top+.16,top_r,.082),(.20,bottom_r,.065)]:
    tube('Reinforced continuous rim',[(r*math.cos(2*math.pi*k/256),r*math.sin(2*math.pi*k/256),z) for k in range(256)],thick,rim_mat,True)
pts=[]
for k in range(4608):
    a=2*math.pi*k/4608; winding=192*a; rr=top_r+.095*math.cos(winding); pts.append((rr*math.cos(a),rr*math.sin(a),top+.10+.13*math.sin(winding)))
tube('Cane rim lashing',pts,.022,willow[3],True)
# Two opposite arched strap handles rise from pairs of rim attachments.
for side in [-1,1]:
    anchor_x=side*math.sqrt(top_r**2-.72**2); v=[]; seg=96
    for k in range(seg+1):
        t=math.pi*k/seg; center=Vector((anchor_x+side*.27*math.sin(t),.72*math.cos(t),top+.13+1.12*math.sin(t)))
        tangent=Vector((side*.27*math.cos(t),-.72*math.sin(t),1.12*math.cos(t))).normalized(); width=Vector((1,0,0)); width=(width-tangent*width.dot(tangent)).normalized()
        for s in [-1,1]: v.append(tuple(center+width*s*.105))
    strip('Arched wicker handle',v,[(2*k,2*k+1,2*k+3,2*k+2) for k in range(seg)],rim_mat,.075)
    for edge in [-1,1]:
        tube('Handle edge reinforcement',[v[2*k+(1 if edge>0 else 0)] for k in range(seg+1)],.028,willow[3])
    for yy in [-.72,.72]:
        a=math.atan2(yy,anchor_x)
        for k in range(6):
            aa=a+(k-2.5)*.024; pts=[]
            for q in range(24):
                b=2*math.pi*q/24; rr=top_r+.12*math.cos(b); pts.append((rr*math.cos(aa),rr*math.sin(aa),top+.1+.18*math.sin(b)))
            tube('Handle attachment binding',pts,.019,willow[4],True)
bpy.ops.mesh.primitive_plane_add(size=200,location=(0,0,.08)); bpy.context.object.name='Studio ground'; bpy.context.object.data.materials.append(floor)
world=bpy.context.scene.world; world.use_nodes=True; world.node_tree.nodes['Background'].inputs[0].default_value=(.7,.76,.82,1); world.node_tree.nodes['Background'].inputs[1].default_value=.35
for loc,power,size in [((1,-4,9),1100,5),((-5,-1,5),750,4),((2,5,7),1200,4)]:
    bpy.ops.object.light_add(type='AREA',location=loc); ob=bpy.context.object; ob.data.energy=power; ob.data.size=size; ob.rotation_euler=(Vector((0,0,1.8))-ob.location).to_track_quat('-Z','Y').to_euler()
bpy.ops.object.camera_add(location=(7,-10,8)); cam=bpy.context.object; cam.rotation_euler=(Vector((0,0,1.9))-cam.location).to_track_quat('-Z','Y').to_euler(); cam.data.type='ORTHO'; cam.data.ortho_scale=7.5; bpy.context.scene.camera=cam
bpy.context.scene.render.engine='CYCLES'; bpy.context.scene.render.resolution_x=1400; bpy.context.scene.render.resolution_y=1400; bpy.context.scene.render.resolution_percentage=100
