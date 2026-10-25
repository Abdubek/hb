import bpy, math
from mathutils import Vector
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)

def mat(name,c,metal=0,rough=.35):
    m=bpy.data.materials.new(name); m.diffuse_color=(*c,1); m.use_nodes=True; p=m.node_tree.nodes.get('Principled BSDF'); p.inputs['Base Color'].default_value=(*c,1); p.inputs['Metallic'].default_value=metal; p.inputs['Roughness'].default_value=rough; return m

def lathe(name,profile,m,n=128):
    verts=[(r*math.cos(2*math.pi*j/n),r*math.sin(2*math.pi*j/n),z) for r,z in profile for j in range(n)]
    faces=[]
    for k in range(len(profile)-1):
        for j in range(n):
            a=k*n+j; b=k*n+(j+1)%n; faces.append((a,b,b+n,a+n))
    mesh=bpy.data.meshes.new(name); mesh.from_pydata(verts,[],faces); mesh.update(); o=bpy.data.objects.new(name,mesh); bpy.context.collection.objects.link(o); o.data.materials.append(m)
    for p in mesh.polygons: p.use_smooth=True
    return o

def box(name,loc,size,m,bevel=.04):
    bpy.ops.mesh.primitive_cube_add(size=1,location=loc); o=bpy.context.object; o.name=name; o.dimensions=size; bpy.ops.object.transform_apply(location=False,rotation=False,scale=True); o.data.materials.append(m)
    if bevel:
        q=o.modifiers.new('Edge radius','BEVEL'); q.width=bevel; q.segments=4; o.modifiers.new('Weighted normals','WEIGHTED_NORMAL')
    return o

def rod(name,a,b,r,m):
    a,b=Vector(a),Vector(b); d=b-a; bpy.ops.mesh.primitive_cylinder_add(vertices=64,radius=r,depth=d.length,location=(a+b)/2); o=bpy.context.object; o.name=name; o.rotation_euler=d.to_track_quat('Z','Y').to_euler(); o.data.materials.append(m)
    q=o.modifiers.new('Machined edges','BEVEL'); q.width=.014; q.segments=3; o.modifiers.new('Weighted normals','WEIGHTED_NORMAL')
    for p in o.data.polygons: p.use_smooth=len(p.vertices)==4
    return o

def torus(name,loc,major,minor,m,rotation=(0,0,0)):
    bpy.ops.mesh.primitive_torus_add(major_segments=112,minor_segments=16,location=loc,major_radius=major,minor_radius=minor,rotation=rotation); o=bpy.context.object; o.name=name; o.data.materials.append(m)
    for p in o.data.polygons: p.use_smooth=True
    return o

steel=mat('Brushed stainless steel',(.57,.62,.65),.90,.27)
polish=mat('Polished rolled edges',(.8,.83,.86),.95,.15)
base=mat('Sandwich base aluminum',(.35,.39,.42),.82,.37)
black=mat('Heat resistant black polymer',(.024,.028,.03),0,.33)
recess=mat('Dark recess',(.009,.012,.014),.15,.48)
# One continuous cross-section: underside, rounded exterior, rolled mouth,
# inner wall and cooking floor. Tiny center rings are closed with disks.
profile=[(.001,.16),(.95,.16),(1.15,.18),(1.25,.23),(1.30,.32),(1.32,.55),(1.35,1.53),(1.38,1.60),(1.40,1.63),(1.39,1.67),(1.35,1.69),(1.31,1.65),(1.30,1.57),(1.27,.54),(1.24,.36),(1.17,.29),(.001,.29)]
lathe('Saucepan hollow body',profile,steel)
rod('Cooking floor center seal',(0,0,.17),(0,0,.289),.015,steel)
lathe('Encapsulated thick base',[(.001,.07),(1.12,.07),(1.22,.10),(1.25,.15),(1.24,.21),(1.15,.23),(.001,.23)],base)
rod('Base center seal',(0,0,.071),(0,0,.22),.015,base)
torus('Base polished seam',(0,0,.18),1.235,.018,polish)
torus('Rolled saucepan lip',(0,0,1.644),1.359,.037,polish)
# Seated domed lid with a downward locating flange and modeled underside.
lid_profile=[(.001,1.79),(.36,1.78),(.79,1.735),(1.21,1.665),(1.285,1.635),(1.285,1.565),(1.316,1.565),(1.316,1.66),(1.40,1.68),(1.43,1.71),(1.41,1.75),(1.31,1.77),(1.09,1.83),(.79,1.91),(.43,1.96),(.001,1.97)]
lid=lathe('Domed stainless lid',lid_profile,steel)
rod('Lid center seal',(0,0,1.79),(0,0,1.971),.015,steel)
torus('Lid edge bead',(0,0,1.715),1.408,.026,polish)
# A true steam vent cut through the lid dome.
bpy.ops.mesh.primitive_cylinder_add(vertices=40,radius=.048,depth=.55,location=(-.79,-.25,1.86)); cutter=bpy.context.object
bpy.context.view_layer.objects.active=lid; q=lid.modifiers.new('Steam vent bore','BOOLEAN'); q.operation='DIFFERENCE'; q.solver='EXACT'; q.object=cutter; bpy.ops.object.modifier_apply(modifier=q.name); bpy.data.objects.remove(cutter,do_unlink=True)
torus('Steam vent ferrule',(-.79,-.25,1.898),.05,.009,polish)
rod('Knob mounting washer',(0,0,1.957),(0,0,1.991),.24,polish)
lathe('Sculpted lid knob',[(.001,1.98),(.13,1.98),(.145,2.04),(.16,2.16),(.28,2.20),(.34,2.27),(.34,2.34),(.30,2.39),(.18,2.41),(.001,2.41)],black,96)
rod('Knob crown',(0,0,2.386),(0,0,2.414),.18,black)
# Twin stamped tangs anchor the long side handle to the pot wall.
for y in (-.21,.21):
    tang=box('Stainless handle tang',(1.52,y,1.28),(.66,.105,.19),steel,.04); tang.rotation_euler[1]=-.13
    rod('Handle mounting rivet',(1.23,y,1.27),(1.365,y,1.27),.067,polish)
box('Heat break collar',(1.82,0,1.34),(.22,.49,.27),black,.08)
# Rounded tapered grip built from elliptical rings along its length.
rings=[(1.79,.00,1.35,.22,.13),(1.96,.00,1.38,.27,.17),(2.35,.00,1.44,.28,.18),(3.16,.00,1.57,.24,.16),(3.63,.00,1.64,.205,.15),(3.77,.00,1.66,.11,.105)]
verts=[]; n=32
for x,y,z,ry,rz in rings:
    for j in range(n):
        a=2*math.pi*j/n; verts.append((x,y+ry*math.cos(a),z+rz*math.sin(a)))
faces=[tuple(reversed(range(n)))]
for k in range(len(rings)-1):
    for j in range(n): faces.append((k*n+j,k*n+(j+1)%n,(k+1)*n+(j+1)%n,(k+1)*n+j))
faces.append(tuple((len(rings)-1)*n+j for j in range(n)))
mesh=bpy.data.meshes.new('Grip mesh'); mesh.from_pydata(verts,[],faces); mesh.update(); grip=bpy.data.objects.new('Tapered saucepan handle',mesh); bpy.context.collection.objects.link(grip); grip.data.materials.append(black)
for p in mesh.polygons: p.use_smooth=len(p.vertices)==4
bpy.ops.mesh.primitive_cylinder_add(vertices=48,radius=.087,depth=.7,location=(3.48,0,1.63)); cutter=bpy.context.object
bpy.context.view_layer.objects.active=grip; q=grip.modifiers.new('Hanging hole','BOOLEAN'); q.operation='DIFFERENCE'; q.solver='EXACT'; q.object=cutter; bpy.ops.object.modifier_apply(modifier=q.name); bpy.data.objects.remove(cutter,do_unlink=True)
q=grip.modifiers.new('Grip edge finish','BEVEL'); q.width=.012; q.segments=3; grip.modifiers.new('Grip normals','WEIGHTED_NORMAL')
for x in (2.10,2.25,2.40): box('Underside grip rib',(x,0,1.29+(x-2.10)*.16),(.034,.36,.028),recess,.01)

floor=mat('Slate studio surface',(.15,.18,.21),0,.78); box('Ground',(0,0,.015),(200,200,.1),floor,0)
scene=bpy.context.scene; scene.world.use_nodes=True; scene.world.node_tree.nodes['Background'].inputs[0].default_value=(.32,.36,.42,1); scene.world.node_tree.nodes['Background'].inputs[1].default_value=.45
for loc,power,size in [((-3,-4,7),1000,5),((5,-1,5),800,4),((0,5,6),1200,3)]:
    bpy.ops.object.light_add(type='AREA',location=loc); o=bpy.context.object; o.data.energy=power; o.data.size=size; o.rotation_euler=(Vector((.6,0,1))-o.location).to_track_quat('-Z','Y').to_euler()
bpy.ops.object.camera_add(location=(6,-8,6)); cam=bpy.context.object; cam.rotation_euler=(Vector((.95,0,1.15))-cam.location).to_track_quat('-Z','Y').to_euler(); cam.data.type='ORTHO'; cam.data.ortho_scale=6.5; scene.camera=cam
scene.render.engine='CYCLES'; scene.render.resolution_x=1400; scene.render.resolution_y=1100; scene.render.resolution_percentage=100
