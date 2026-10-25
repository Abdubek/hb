import bpy, math
from mathutils import Vector
bpy.ops.object.select_all(action='SELECT'); bpy.ops.object.delete(use_global=False)

def mat(n,c,metal=0,rough=.5,emit=0):
    m=bpy.data.materials.new(n); m.diffuse_color=(*c,1); m.use_nodes=True; p=m.node_tree.nodes.get('Principled BSDF')
    p.inputs['Base Color'].default_value=(*c,1); p.inputs['Metallic'].default_value=metal; p.inputs['Roughness'].default_value=rough
    if emit: p.inputs['Emission Color'].default_value=(*c,1); p.inputs['Emission Strength'].default_value=emit
    return m

def box(n,p,s,m,b=.025):
    bpy.ops.mesh.primitive_cube_add(size=1,location=p); o=bpy.context.object; o.name=n; o.dimensions=s
    bpy.ops.object.transform_apply(location=False,rotation=False,scale=True); o.data.materials.append(m)
    if b:
        q=o.modifiers.new('Soft edges','BEVEL'); q.width=b; q.segments=3; o.modifiers.new('Weighted normals','WEIGHTED_NORMAL')
    return o

def rod(n,a,b,r,m,v=24):
    a,b=Vector(a),Vector(b); d=b-a; bpy.ops.mesh.primitive_cylinder_add(vertices=v,radius=r,depth=d.length,location=(a+b)/2)
    o=bpy.context.object; o.name=n; o.rotation_euler=d.to_track_quat('Z','Y').to_euler(); o.data.materials.append(m)
    q=o.modifiers.new('Edge bevel','BEVEL'); q.width=min(.012,r*.18); q.segments=2; o.modifiers.new('Normals','WEIGHTED_NORMAL'); return o

def curve(n,points,r,m):
    c=bpy.data.curves.new(n,'CURVE'); c.dimensions='3D'; c.resolution_u=1; c.bevel_depth=r; c.bevel_resolution=3
    s=c.splines.new('POLY'); s.points.add(len(points)-1)
    for p,co in zip(s.points,points): p.co=(*co,1)
    o=bpy.data.objects.new(n,c); bpy.context.collection.objects.link(o); o.data.materials.append(m); return o

def ring(n,p,major,minor,m,rotation=(0,0,0)):
    bpy.ops.mesh.primitive_torus_add(major_radius=major,minor_radius=minor,major_segments=64,minor_segments=12,location=p,rotation=rotation)
    o=bpy.context.object; o.name=n; o.data.materials.append(m)
    for f in o.data.polygons: f.use_smooth=True
    return o

def area(n,p,target,power,size,c):
    bpy.ops.object.light_add(type='AREA',location=p); o=bpy.context.object; o.name=n; o.data.energy=power; o.data.size=size; o.data.color=c
    o.rotation_euler=(Vector(target)-o.location).to_track_quat('-Z','Y').to_euler()

teak=mat('Oiled teak',(.34,.16,.065)); trim=mat('Golden end grain',(.56,.31,.12)); cream=mat('Painted cream lining',(.79,.78,.65)); seam=mat('Deck caulking',(.065,.045,.027))
brass=mat('Aged brass',(.58,.39,.12),.8,.27); navy=mat('Navy canvas',(.045,.11,.19),rough=.9); linen=mat('Ecru linen',(.81,.79,.67),rough=.95)
stripe=mat('Blue blanket stripes',(.20,.36,.42),rough=.9); glass=mat('Sea blue glazing',(.13,.48,.62),rough=.21,emit=.6); bulb=mat('Warm lamp glass',(1,.72,.38),emit=4)
# Cabin coordinates: bow is +Y, front and starboard are cut away.
box('Hull floor base',(0,0,-.13),(4.15,6.3,.24),teak,.12)
for i in range(17): box('Teak sole plank',(-1.92+i*.24,0,.02),(.226,6.13,.065),trim if i%4==0 else teak,.007)
for x in [-1.92,1.92]: box('Sole perimeter margin',(x,0,.07),(.11,6.2,.08),trim)
box('Port hull lining',(-2.02,0,1.18),(.16,6.3,2.36),cream)
box('Starboard cutaway coaming',(2.02,0,.33),(.16,6.3,.66),teak)
# Rear bulkhead with a genuine round opening made with a boolean cutter.
wall=box('Bow bulkhead',(0,3.13,1.33),(4.1,.18,2.66),cream,0)
bpy.ops.mesh.primitive_cylinder_add(vertices=64,radius=.46,depth=.7,location=(0,3.13,1.95),rotation=(math.pi/2,0,0))
cutter=bpy.context.object; mod=wall.modifiers.new('Porthole aperture','BOOLEAN'); mod.operation='DIFFERENCE'; mod.object=cutter
bpy.context.view_layer.objects.active=wall; bpy.ops.object.modifier_apply(modifier=mod.name); bpy.data.objects.remove(cutter,do_unlink=True)
ring('Bow porthole flange',(0,3.005,1.95),.49,.065,brass,(math.pi/2,0,0))
ring('Bow inner seal',(0,2.986,1.95),.418,.018,seam,(math.pi/2,0,0))
rod('Bow porthole glass',(0,3.07,1.95),(0,3.09,1.95),.435,glass,64)
for i in range(10):
    a=2*math.pi*i/10; x=.49*math.cos(a); z=1.95+.49*math.sin(a)
    rod('Flange bolt',(x,2.944,z),(x,2.921,z),.018,brass,12)
# Two port-side portholes with matching circular apertures.
port=bpy.data.objects.get('Port hull lining')
for yy in [-1.65,.8]:
    bpy.ops.mesh.primitive_cylinder_add(vertices=64,radius=.35,depth=.7,location=(-2.02,yy,1.77),rotation=(0,math.pi/2,0))
    cutter=bpy.context.object; mod=port.modifiers.new('Side aperture','BOOLEAN'); mod.operation='DIFFERENCE'; mod.object=cutter
    bpy.context.view_layer.objects.active=port; bpy.ops.object.modifier_apply(modifier=mod.name); bpy.data.objects.remove(cutter,do_unlink=True)
    ring('Port brass frame',(-1.913,yy,1.77),.38,.055,brass,(0,math.pi/2,0))
    rod('Port blue glass',(-2.045,yy,1.77),(-2.025,yy,1.77),.346,glass,64)
    for i in range(8):
        a=i*math.tau/8; y=yy+.38*math.cos(a); z=1.77+.38*math.sin(a)
        rod('Porthole screw',(-1.865,y,z),(-1.85,y,z),.015,brass,12)
# Curved barrel ceiling: rear third is solid, forward portion exposes curved ribs.
# Arch rises from z=2.25 at the sides to z=3.3 at its crown.
N=40; verts=[]
for y in [1.55,3.22]:
    for i in range(N+1):
        a=math.pi*i/N; verts.append((2.05*math.cos(a),y,2.25+1.05*math.sin(a)))
faces=[(i,i+1,N+2+i,N+1+i) for i in range(N)]
mesh=bpy.data.meshes.new('Barrel ceiling mesh'); mesh.from_pydata(verts,[],faces); mesh.update()
o=bpy.data.objects.new('Curved cream ceiling',mesh); bpy.context.collection.objects.link(o); o.data.materials.append(cream)
q=o.modifiers.new('Ceiling thickness','SOLIDIFY'); q.thickness=.075
for f in mesh.polygons: f.use_smooth=True
for y in [-2.9,-1.5,0,1.55,3.12]:
    points=[(2.01*math.cos(math.pi*i/48),y,2.245+1.025*math.sin(math.pi*i/48)) for i in range(49)]
    curve('Laminated curved roof rib',points,.047,trim)
for i in range(1,12):
    a=math.pi*i/12
    curve('Ceiling plank seam',[(2.05*math.cos(a),1.57,2.25+1.05*math.sin(a)-.014),(2.05*math.cos(a),3.18,2.25+1.05*math.sin(a)-.014)],.006,teak)
# Port and starboard bunks with drawers below and soft bedding.
for x in [-1.37,1.37]:
    box('Bunk base',(x,-.60,.38),(1.16,3.55,.65),teak,.06)
    box('Bunk mattress',(x,-.60,.84),(1.10,3.40,.25),linen,.12)
    box('Navy blanket',(x,-1.14,.988),(1.08,2.20,.065),navy,.035)
    for yy in [-1.93,-1.78,-1.63]: box('Woven blanket stripe',(x,yy,1.025),(1.075,.055,.012),stripe,.005)
    pillow=box('Rounded linen pillow',(x,.57,1.025),(.84,.59,.18),linen,.09); pillow.rotation_euler.z=.045 if x<0 else -.06
    inner=x+(.59 if x<0 else -.59)
    box('Bunk retaining fiddle',(inner,-.65,.87),(.075,3.4,.19),trim,.03)
    for yy in [-1.73,-.60,.53]:
        box('Under bunk drawer',(inner,yy,.41),(.038,1.0,.43),trim,.015)
        rod('Drawer recessed pull',(inner-.024,yy,.44),(inner+.024,yy,.44),.057,brass,24)
# Rear storage cabinetry and the deployed fold-down table.
for x in [-1.45,1.45]:
    box('Bow locker',(x,2.56,.65),(1.00,.83,1.20),teak,.045)
    box('Locker door',(x,2.115,.64),(.87,.055,.98),trim)
    rod('Locker knob',(x+.27,2.07,.68),(x+.27,2.02,.68),.035,brass)
    box('Locker top',(x,2.54,1.28),(1.07,.90,.075),trim)
box('Table wall mounting cleat',(0,2.99,1.14),(1.55,.14,.16),teak)
box('Fold down tabletop deployed',(0,2.34,1.15),(1.52,1.28,.09),trim,.055)
for xx in [-.50,.50]:
    rod('Table brass hinge',(xx-.13,2.93,1.15),(xx+.13,2.93,1.15),.03,brass)
    rod('Folding support bracket',(xx,2.96,.47),(xx,1.92,1.095),.025,brass)
for x in [-.73,.73]: box('Table raised fiddle',(x,2.35,1.22),(.035,1.16,.075),teak,.01)
box('Nautical chart',(0,2.32,1.201),(.86,.68,.008),linen,.006)
for i in range(5): curve('Chart contour',[(-.35+j*.075,2.12+i*.09+.025*math.sin(j+i),1.208) for j in range(10)],.0025,stripe)
rod('Enamel mug',(.50,2.52,1.20),(.50,2.52,1.39),.07,cream)
ring('Mug handle',(.59,2.52,1.30),.052,.013,cream,(math.pi/2,0,0))
# Small reading lamps on rear posts.
for x in [-1.73,1.73]:
    box('Reading lamp mount',(x,1.03,1.58),(.10,.16,.24),brass)
    rod('Reading lamp arm',(x,1.03,1.63),(x*.86,.84,1.78),.022,brass)
    rod('Lamp shade',(x*.86,.84,1.73),(x*.86,.84,1.86),.095,brass)
    rod('Lamp lens',(x*.86,.84,1.714),(x*.86,.84,1.731),.076,bulb)
    area('Bunk reading light',(x*.86,.84,1.69),(x,0,.8),35,.25,(1,.69,.37))
rod('Ceiling lamp housing',(0,2.1,3.16),(0,2.1,3.23),.20,brass,48)
rod('Ceiling opal glass',(0,2.1,3.13),(0,2.1,3.16),.165,bulb,48)
area('Cabin ceiling light',(0,2.1,3.08),(0,1,0),110,1,(1,.77,.48))
area('Hatch daylight',(1,-3,5),(0,0,1),850,4,(.75,.86,1))
area('Open cabin fill',(4,-1,4),(0,1,1),500,4,(1,.86,.68))
scene=bpy.context.scene; scene.world.color=(.18,.18,.18)
bpy.ops.object.camera_add(location=(8,-11,8)); cam=bpy.context.object; cam.rotation_euler=(Vector((0,.15,1.35))-cam.location).to_track_quat('-Z','Y').to_euler(); cam.data.type='ORTHO'; cam.data.ortho_scale=9.9; scene.camera=cam
scene.render.engine='CYCLES'; scene.cycles.samples=64; scene.render.resolution_x=1300; scene.render.resolution_y=1300; scene.render.resolution_percentage=100; scene.view_settings.view_transform='AgX'
