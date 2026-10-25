import bpy, math
from mathutils import Vector
bpy.ops.object.select_all(action='SELECT'); bpy.ops.object.delete(use_global=False)

def mat(name,c,rough=.55,metal=0):
    m=bpy.data.materials.new(name); m.diffuse_color=(*c,1); m.use_nodes=True; p=m.node_tree.nodes.get('Principled BSDF'); p.inputs['Base Color'].default_value=(*c,1); p.inputs['Roughness'].default_value=rough; p.inputs['Metallic'].default_value=metal; return m

def box(name,loc,size,m,bevel=.02,parent=None):
    bpy.ops.mesh.primitive_cube_add(size=1,location=loc); o=bpy.context.object; o.name=name; o.dimensions=size; bpy.ops.object.transform_apply(location=False,rotation=False,scale=True); o.data.materials.append(m)
    if bevel:
        b=o.modifiers.new('Soft edges','BEVEL'); b.width=bevel; b.segments=3; o.modifiers.new('Weighted normals','WEIGHTED_NORMAL')
    if parent: o.parent=parent
    return o

def cyl(name,loc,r,depth,m):
    bpy.ops.mesh.primitive_cylinder_add(vertices=128,radius=r,depth=depth,location=loc); o=bpy.context.object; o.name=name; o.data.materials.append(m); b=o.modifiers.new('Edge radius','BEVEL'); b.width=.025; b.segments=3; o.modifiers.new('Weighted normals','WEIGHTED_NORMAL'); return o

def mesh_obj(name,verts,faces,m,parent):
    mesh=bpy.data.meshes.new(name); mesh.from_pydata(verts,[],faces); mesh.update(); o=bpy.data.objects.new(name,mesh); bpy.context.collection.objects.link(o); o.data.materials.append(m); o.parent=parent; return o

def curve(name,points,r,m,parent=None,closed=False):
    c=bpy.data.curves.new(name,'CURVE'); c.dimensions='3D'; c.bevel_depth=r; c.bevel_resolution=3; s=c.splines.new('POLY'); s.points.add(len(points)-1)
    for p,co in zip(s.points,points): p.co=(*co,1)
    s.use_cyclic_u=closed; o=bpy.data.objects.new(name,c); bpy.context.collection.objects.link(o); o.data.materials.append(m); o.parent=parent; return o

def area(name,loc,power,size,target,color=(1,1,1)):
    bpy.ops.object.light_add(type='AREA',location=loc); o=bpy.context.object; o.name=name; o.data.energy=power; o.data.size=size; o.data.color=color; o.rotation_euler=(Vector(target)-o.location).to_track_quat('-Z','Y').to_euler()

cream=mat('Warm white foam',(.86,.83,.73),.65); gum=mat('Gum rubber tread',(.42,.25,.115),.85); fabric=mat('Stone knit upper',(.61,.66,.64),.9); suede=mat('Sand suede overlays',(.48,.46,.39),.85); teal=mat('Deep teal leather',(.055,.23,.23),.5); laces=mat('Cotton laces',(.92,.89,.8),.86); dark=mat('Dark padded lining',(.04,.065,.065),.95); metal=mat('Eyelet metal',(.34,.39,.38),.3,.65); stage=mat('Display warm gray',(.4,.44,.43),.4); base=mat('Turntable graphite',(.045,.06,.062),.35,.4)
# Fine procedural knit gives simple forms a soft textile finish.
n=fabric.node_tree.nodes; links=fabric.node_tree.links; noise=n.new('ShaderNodeTexNoise'); noise.inputs['Scale'].default_value=145; noise.inputs['Detail'].default_value=2; bump=n.new('ShaderNodeBump'); bump.inputs['Strength'].default_value=.19; bump.inputs['Distance'].default_value=.017; links.new(noise.outputs['Fac'],bump.inputs['Height']); links.new(bump.outputs['Normal'],n.get('Principled BSDF').inputs['Normal'])
turn=bpy.data.objects.new('Turntable rotating display',None); bpy.context.collection.objects.link(turn)
cyl('Turntable stationary base',(0,0,.12),2.9,.24,base)
platter=cyl('Rotating presentation platter',(0,0,.32),2.83,.2,stage); platter.parent=turn
ringpts=[(2.865*math.cos(i*math.tau/160),2.865*math.sin(i*math.tau/160),.23) for i in range(160)]; curve('Platter perimeter accent',ringpts,.012,cream,None,True)
# Sole outline is a rounded, asymmetric footprint, built in stacked rings.
def sole(name,zs,scales,m,parent):
    count=64; verts=[]
    for z,s in zip(zs,scales):
        for i in range(count):
            a=math.tau*i/count; x=-.12+1.56*math.cos(a); width=.48+.105*(1-math.cos(a))/2
            verts.append((-.12+(x+.12)*s,width*math.sin(a)*s,z+.05*max(0,-math.cos(a))**4))
    faces=[tuple(reversed(range(count)))]
    for j in range(len(zs)-1):
        for i in range(count): faces.append((j*count+i,j*count+(i+1)%count,(j+1)*count+(i+1)%count,(j+1)*count+i))
    faces.append(tuple((len(zs)-1)*count+i for i in range(count)))
    o=mesh_obj(name,verts,faces,m,parent)
    for p in o.data.polygons: p.use_smooth=len(p.vertices)==4
    return o

def shoe(name,loc,angle):
    root=bpy.data.objects.new(name,None); bpy.context.collection.objects.link(root); root.parent=turn; root.location=loc; root.rotation_euler.z=angle
    sole(name+' gum outsole',[.025,.085,.12],[.97,1,1],gum,root)
    sole(name+' foam midsole',[.12,.17,.29,.32],[1,1.015,.985,.945],cream,root)
    # Longitudinal upper sections: rounded toe, broad vamp, taller heel.
    sections=[(-1.61,.075,.085),(-1.48,.32,.22),(-1.22,.47,.34),(-.85,.5,.43),(-.42,.46,.61),(.02,.415,.8),(.43,.4,.86),(.87,.4,.88),(1.2,.31,.8),(1.31,.12,.6)]
    verts=[]; N=32
    for x,w,h in sections:
        for i in range(N):
            a=math.tau*i/N; verts.append((x,w*math.cos(a),.3+h*(math.sin(a)+1)/2))
    faces=[tuple(reversed(range(N)))]
    for j in range(len(sections)-1):
        for i in range(N): faces.append((j*N+i,j*N+(i+1)%N,(j+1)*N+(i+1)%N,(j+1)*N+i))
    faces.append(tuple((len(sections)-1)*N+i for i in range(N)))
    o=mesh_obj(name+' knit upper',verts,faces,fabric,root)
    for p in o.data.polygons: p.use_smooth=True
    sub=o.modifiers.new('Soft upper surface','SUBSURF'); sub.levels=1; sub.render_levels=1
    # Toe overlay wraps both visible sides and crosses the toe crest.
    for side in [-1,1]:
        curve('Toe overlay seam',[(-1.49,side*.18,.46),(-1.3,side*.36,.51),(-1.08,side*.46,.54),(-.91,side*.49,.57)],.035,suede,root)
        curve('Toe cap stitching',[(-1.48,side*.2,.49),(-1.29,side*.38,.54),(-1.07,side*.478,.57),(-.92,side*.5,.59)],.008,laces,root)
        # Applied quarter panels follow the side of the upper.
        vs=[(-.58,side*.447,.48),(.71,side*.396,.46),(1.14,side*.29,.63),(.95,side*.32,.94),(.39,side*.38,.92),(-.4,side*.46,.69)]
        panel=mesh_obj('Suede quarter overlay',vs,[(0,1,2,3,4,5)],suede,root); sol=panel.modifiers.new('Overlay thickness','SOLIDIFY'); sol.thickness=.023; b=panel.modifiers.new('Panel edge softness','BEVEL'); b.width=.017; b.segments=3
        curve('Quarter panel stitching',[(x,y*1.015,z) for x,y,z in vs],.007,laces,root,True)
        stripe=mesh_obj('Teal side ribbon',[(-.38,side*.478,.53),(-.18,side*.457,.48),(.51,side*.423,.87),(.33,side*.429,.91)],[(0,1,2,3)],teal,root); stripe.modifiers.new('Leather thickness','SOLIDIFY').thickness=.022
        curve('Midsole molded groove',[(-1.37,side*.37,.207),(-1.05,side*.49,.188),(-.5,side*.555,.185),(.15,side*.505,.185),(.8,side*.414,.185),(1.18,side*.29,.19)],.008,suede,root)
    # A dark inset and padded elliptical collar read as the ankle opening.
    bpy.ops.mesh.primitive_uv_sphere_add(segments=48,ring_count=16,location=(.75,0,1.107)); opening=bpy.context.object; opening.name='Recessed dark ankle opening'; opening.scale=(.395,.265,.035); opening.data.materials.append(dark); opening.parent=root
    pts=[(.75+.41*math.cos(i*math.tau/80),.285*math.sin(i*math.tau/80),1.13+.035*math.cos(i*math.tau/80)) for i in range(80)]
    curve('Padded ankle collar',pts,.063,teal,root,True)
    curve('Inner collar piping',[(x,y*.86,z-.016) for x,y,z in pts],.019,dark,root,True)
    # Tongue leans upward from the vamp toward the collar.
    tongue=box('Padded tongue',(-.09,0,.98),(.86,.48,.12),teal,.055,root); tongue.rotation_euler.y=math.radians(-18)
    tag=box('Tongue woven label',(.18,0,1.131),(.23,.29,.012),cream,.018,root); tag.rotation_euler.y=math.radians(-18)
    for yy in [-.07,0,.07]: box('Tongue label stripe',(.18,yy,1.15),(.12,.018,.009),teal,.004,root)
    # Paired eyelets and five crossed lace runs.
    for i in range(5):
        x=-.7+i*.19; z=.765+i*.079; w=.26-i*.009
        for side in [-1,1]:
            box('Lace eyestay',(x,side*w,z-.008),(.15,.12,.055),suede,.035,root)
            pts=[(x+.039*math.cos(j*math.tau/24),side*w+.039*math.sin(j*math.tau/24),z+.025) for j in range(24)]
            curve('Metal lace eyelet',pts,.008,metal,root,True)
        if i<4:
            for side in [-1,1]:
                curve('Crossed cotton lace',[(x,side*w,z+.04),(x+.095,0,z+.105),(x+.19,-side*(w-.009),z+.12)],.023,laces,root)
    # Tied bow and lace tips sit above the top eyelets.
    for side in [-1,1]:
        curve('Lace bow loop',[(.11,0,1.15),(.24,side*.17,1.23),(.13,side*.34,1.24),(-.04,side*.24,1.2),(.11,0,1.15)],.022,laces,root)
        curve('Loose lace end',[(.11,0,1.15),(-.1,side*.2,1.16),(-.3,side*.33,1.04)],.021,laces,root)
        curve('Lace aglet',[(-.3,side*.33,1.04),(-.36,side*.35,1.0)],.022,cream,root)
    box('Heel counter',(1.252,0,.67),(.15,.5,.43),teal,.065,root)
    curve('Heel pull loop',[(1.2,-.105,.98),(1.39,-.105,1.23),(1.39,.105,1.23),(1.2,.105,.98)],.035,teal,root)
    # Chunky outsole lugs remain visible around the perimeter.
    for x in [-1.15,-.87,-.59,-.31,-.03,.25,.53,.81,1.06]:
        for side in [-1,1]:
            width=.49*math.sqrt(max(.05,1-((x+.12)/1.57)**2))
            o=box('Outsole traction lug',(x,side*width,.067),(.17,.15,.086),gum,.018,root); o.rotation_euler.z=side*.16
    return root

shoe('Left sneaker',(-.08,-.86,.43),math.radians(-9))
shoe('Right sneaker',(.12,.86,.43),math.radians(13))
# Optional animation is prepared as a complete, smooth turntable revolution.
turn.rotation_euler.z=0; turn.keyframe_insert(data_path='rotation_euler',frame=1)
turn.rotation_euler.z=math.tau; turn.keyframe_insert(data_path='rotation_euler',frame=121)
if turn.animation_data and turn.animation_data.action:
    action=turn.animation_data.action
    if hasattr(action,'fcurves'):
        for fc in action.fcurves:
            for kp in fc.keyframe_points: kp.interpolation='LINEAR'
scene=bpy.context.scene; scene.frame_start=1; scene.frame_end=120; scene.frame_set(1)
box('Studio floor',(0,0,-.07),(200,200,.1),mat('Muted sage backdrop',(.25,.33,.31),.7),0)
area('Large product key',(-4,-5,7),800,4,(0,0,.8)); area('Soft overhead',(1,1,8),650,4,(0,0,0)); area('Cool edge light',(3,4,4),800,3,(0,0,1),(.72,.88,1)); area('Front fill',(-4,1,3),200,3,(0,0,.8))
bpy.ops.object.camera_add(location=(-7.7,-9,6.4)); camera=bpy.context.object; camera.name='Sneaker pair display camera'; camera.data.lens=55; camera.rotation_euler=(Vector((0,0,.6))-camera.location).to_track_quat('-Z','Y').to_euler(); scene.camera=camera
scene.world.color=(.23,.27,.26); scene.render.engine='CYCLES'; scene.cycles.samples=64; scene.render.resolution_x=1400; scene.render.resolution_y=1200; scene.render.resolution_percentage=100; scene.view_settings.view_transform='AgX'
