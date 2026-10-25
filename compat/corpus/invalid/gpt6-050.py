import bpy, math
from mathutils import Vector, Matrix
bpy.ops.wm.read_factory_settings(use_empty=True)

def mat(name,c,metal=0,rough=.45):
    m=bpy.data.materials.new(name); m.diffuse_color=(*c,1); m.use_nodes=True; p=m.node_tree.nodes.get('Principled BSDF'); p.inputs['Base Color'].default_value=(*c,1); p.inputs['Metallic'].default_value=metal; p.inputs['Roughness'].default_value=rough; return m

def box(name,loc,dims,m,bevel=.025):
    bpy.ops.mesh.primitive_cube_add(size=1,location=loc); o=bpy.context.object; o.name=name; o.dimensions=dims; bpy.ops.object.transform_apply(location=False,rotation=False,scale=True); o.data.materials.append(m)
    if bevel:
        b=o.modifiers.new('Rounded edges','BEVEL'); b.width=bevel; b.segments=3; o.modifiers.new('Normals','WEIGHTED_NORMAL')
    return o

def cyl(name,loc,r,depth,m,rot=(0,0,0),vertices=64):
    bpy.ops.mesh.primitive_cylinder_add(vertices=vertices,radius=r,depth=depth,location=loc,rotation=rot); o=bpy.context.object; o.name=name; o.data.materials.append(m); b=o.modifiers.new('Edge radius','BEVEL'); b.width=.012; b.segments=2; o.modifiers.new('Normals','WEIGHTED_NORMAL'); return o

def beam(name,a,b,r,m):
    a=Vector(a); b=Vector(b); o=cyl(name,(a+b)/2,r,(b-a).length,m,vertices=16); o.rotation_euler=(b-a).to_track_quat('Z','Y').to_euler(); return o

def aim(o,p): o.rotation_euler=(Vector(p)-o.location).to_track_quat('-Z','Y').to_euler()
white=mat('Off white turbine coating',(.83,.86,.85),.18,.32); steel=mat('Galvanized metal',(.43,.49,.52),.8,.28); dark=mat('Service details',(.045,.065,.075),.3); concrete=mat('Foundation concrete',(.46,.45,.40)); grass=mat('Meadow ground',(.22,.29,.12)); gravel=mat('Service gravel',(.43,.39,.29)); red=mat('Blade warning red',(.71,.065,.035),.12); yellow=mat('Safety yellow',(.9,.57,.045))
box('Terrain',(0,0,-.22),(200,200,.25),grass,0)
cyl('Gravel maintenance apron',(0,0,-.055),3.6,.12,gravel,vertices=96)
box('Access track',(0,-12,-.05),(2.7,19,.09),gravel,.03)
cyl('Circular foundation',(0,0,.12),1.3,.30,concrete)
cyl('Tower anchor flange',(0,0,.32),.88,.13,steel)
for i in range(20):
    a=i*math.tau/20; cyl('Foundation anchor bolt',(.77*math.cos(a),.77*math.sin(a),.42),.038,.10,steel,vertices=6)
# Tapered, hollow-ended tower shell with a closed base and top.
verts=[]; faces=[]; levels=[(.36,.66),(4.7,.54),(9.1,.415),(13.5,.29)]; n=96
for z,r in levels:
    for i in range(n):
        a=i*math.tau/n; verts.append((r*math.cos(a),r*math.sin(a),z))
for j in range(len(levels)-1):
    for i in range(n): k=(i+1)%n; faces.append((j*n+i,j*n+k,(j+1)*n+k,(j+1)*n+i))
faces.append(tuple(reversed(range(n)))); faces.append(tuple((len(levels)-1)*n+i for i in range(n)))
mesh=bpy.data.meshes.new('Tapered tower mesh'); mesh.from_pydata(verts,[],faces); mesh.update(); tower=bpy.data.objects.new('Tapered tubular tower',mesh); bpy.context.collection.objects.link(tower); tower.data.materials.append(white)
for p in mesh.polygons: p.use_smooth=len(p.vertices)==4
for z,r in levels[1:-1]:
    bpy.ops.mesh.primitive_torus_add(major_radius=r,minor_radius=.009,major_segments=96,minor_segments=8,location=(0,0,z)); bpy.context.object.name='Tower section seam'; bpy.context.object.data.materials.append(steel)
box('Service door dark reveal',(0,-.625,1.07),(.48,.055,1.24),dark,.12)
box('Service door',(0,-.663,1.07),(.425,.035,1.16),white,.10)
box('Door handle',(.14,-.698,1.07),(.025,.04,.16),steel,.01)
box('Warning plaque',(0,-.689,1.39),(.15,.012,.14),yellow,.008)
for i in range(3): box('Access step',(0,-1.14-i*.29,.39-i*.10),(.79,.35,.15),steel,.025)
for side in (-1,1):
    beam('Stair handrail post',(side*.48,-1.75,.12),(side*.48,-1.75,.95),.023,steel)
    beam('Stair upper post',(side*.48,-.87,.32),(side*.48,-.87,1.23),.023,steel)
    beam('Stair handrail',(side*.48,-1.83,.93),(side*.48,-.81,1.26),.025,steel)
cyl('Yaw bearing',(0,0,13.48),.47,.20,steel)
box('Nacelle rounded housing',(0,.31,13.93),(1.02,2.04,.95),white,.24)
box('Nacelle underside',(0,.26,13.50),(.76,1.5,.12),dark,.045)
for side in (-1,1):
    for j in range(8): box('Nacelle ventilation slot',(side*.512,.38+j*.083,13.94),(.012,.033,.29),dark,.009)
box('Top maintenance hatch',(0,.38,14.43),(.60,.76,.055),steel,.045)
beam('Weather sensor mast',(.18,.80,14.4),(.18,.80,14.95),.018,steel)
beam('Anemometer crossbar',(-.02,.80,14.95),(.38,.80,14.95),.012,steel)
for x in (-.02,.38):
    bpy.ops.mesh.primitive_uv_sphere_add(segments=16,ring_count=8,radius=.06,location=(x,.80,14.95)); bpy.context.object.name='Anemometer cup'; bpy.context.object.data.materials.append(dark)
# Rotor shaft points forward along negative Y.
rot=(math.pi/2,0,0)
cyl('Main rotor shaft',(0,-.83,13.98),.22,.53,steel,rot)
cyl('Rotor hub',(0,-1.09,13.98),.44,.43,white,rot)
# Three distinct twisted airfoil blades, rotated by exactly 120 degrees.
# Sections specify radial distance, chord, sweep, thickness ratio and pitch.
sections=[(.28,.28,0,.65,24),(.60,.34,0,.42,21),(.98,.58,.04,.22,17),(1.45,.73,.11,.16,13),(2.15,.66,.19,.13,10),(3.1,.53,.29,.115,7),(4.1,.40,.37,.10,4),(5.0,.26,.43,.09,2),(5.65,.13,.46,.085,0),(5.94,.035,.45,.09,-1)]
for blade_index in range(3):
    azimuth=math.radians(8+blade_index*120); R=Matrix.Rotation(azimuth,4,'Y'); base=Vector((0,-1.09,13.98)); vs=[]; fs=[]; count=32
    for radius,chord,sweep,thick,pitch in sections:
        pitch=math.radians(pitch)
        for k in range(count):
            theta=math.tau*k/count; u=(1-math.cos(theta))/2
            yt=5*thick*chord*(.2969*math.sqrt(max(u,0))-.1260*u-.3516*u*u+.2843*u**3-.1036*u**4)
            if k>count/2: yt=-yt
            chordwise=(u-.32)*chord
            xx=sweep+chordwise*math.cos(pitch)-yt*math.sin(pitch)
            yy=chordwise*math.sin(pitch)+yt*math.cos(pitch)-.035*radius
            vs.append(tuple(base+R@Vector((xx,yy,radius))))
    for j in range(len(sections)-1):
        for k in range(count): fs.append((j*count+k,j*count+(k+1)%count,(j+1)*count+(k+1)%count,(j+1)*count+k))
    fs.append(tuple(reversed(range(count)))); fs.append(tuple((len(sections)-1)*count+k for k in range(count)))
    me=bpy.data.meshes.new('Twisted airfoil mesh'); me.from_pydata(vs,[],fs); me.update(); o=bpy.data.objects.new('Rotor blade '+str(blade_index+1),me); bpy.context.collection.objects.link(o); o.data.materials.append(white); o.data.materials.append(red)
    for p in me.polygons:
        p.use_smooth=True
        if p.index<(len(sections)-1)*count and p.index//count==7: p.material_index=1
    root=base+R@Vector((0,0,.43)); bearing=cyl('Blade pitch bearing',root,.20,.19,steel); bearing.rotation_euler=(R@Vector((0,0,1))).to_track_quat('Z','Y').to_euler()
# Rounded spinner covers the blade roots while leaving pitch collars visible.
bpy.ops.mesh.primitive_uv_sphere_add(segments=48,ring_count=24,radius=1,location=(0,-1.36,13.98)); o=bpy.context.object; o.name='Aerodynamic nose spinner'; o.scale=(.47,.61,.47); o.data.materials.append(white)
for p in o.data.polygons: p.use_smooth=True
box('Transformer concrete pad',(2.2,1.3,.10),(1.55,1.3,.24),concrete)
box('Transformer cabinet',(2.2,1.3,.69),(1.15,.9,.95),dark,.07)
for i in range(8): box('Transformer cooling fins',(1.61,1.02+i*.08,.68),(.07,.035,.69),steel,.007)
box('Transformer warning label',(2.2,.838,.83),(.20,.016,.18),yellow,.005)
bpy.ops.object.light_add(type='SUN',location=(-8,-10,20)); bpy.context.object.data.energy=2.5; bpy.context.object.rotation_euler=(.4,-.5,-.45); bpy.context.object.data.angle=.09
bpy.ops.object.light_add(type='AREA',location=(4,-10,16)); bpy.context.object.data.energy=1800; bpy.context.object.data.size=10; aim(bpy.context.object,(0,0,10))
bpy.ops.object.camera_add(location=(24,-36,20)); camera=bpy.context.object; aim(camera,(0,0,9.8)); camera.data.type='ORTHO'; camera.data.ortho_scale=24
scene=bpy.context.scene; scene.camera=camera; scene.render.engine='CYCLES'; scene.cycles.samples=64; scene.world.color=(.3,.3,.3); scene.render.resolution_x=1200; scene.render.resolution_y=1500; scene.render.resolution_percentage=100
