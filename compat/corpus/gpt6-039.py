import bpy, math
from mathutils import Vector
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)

def mat(name,c,metal=0,rough=.4):
    m=bpy.data.materials.new(name); m.diffuse_color=(*c,1); m.use_nodes=True; p=m.node_tree.nodes.get('Principled BSDF'); p.inputs['Base Color'].default_value=(*c,1); p.inputs['Metallic'].default_value=metal; p.inputs['Roughness'].default_value=rough; return m

def box(name,loc,size,m,bevel=.025):
    bpy.ops.mesh.primitive_cube_add(size=1,location=loc); o=bpy.context.object; o.name=name; o.dimensions=size; bpy.ops.object.transform_apply(location=False,rotation=False,scale=True); o.data.materials.append(m)
    if bevel:
        q=o.modifiers.new('Folded edge radius','BEVEL'); q.width=bevel; q.segments=3; o.modifiers.new('Weighted normals','WEIGHTED_NORMAL')
    return o

def rod(name,a,b,r,m,n=48):
    a,b=Vector(a),Vector(b); d=b-a; bpy.ops.mesh.primitive_cylinder_add(vertices=n,radius=r,depth=d.length,location=(a+b)/2); o=bpy.context.object; o.name=name; o.rotation_euler=d.to_track_quat('Z','Y').to_euler(); o.data.materials.append(m)
    q=o.modifiers.new('Edge bevel','BEVEL'); q.width=.008; q.segments=3; o.modifiers.new('Weighted normals','WEIGHTED_NORMAL')
    for p in o.data.polygons: p.use_smooth=len(p.vertices)==4
    return o

def tube(name,pts,r,m):
    c=bpy.data.curves.new(name,'CURVE'); c.dimensions='3D'; c.bevel_depth=r; c.bevel_resolution=4; s=c.splines.new('BEZIER'); s.bezier_points.add(len(pts)-1)
    for p,co in zip(s.bezier_points,pts): p.co=co; p.handle_left_type='AUTO'; p.handle_right_type='AUTO'
    o=bpy.data.objects.new(name,c); bpy.context.collection.objects.link(o); o.data.materials.append(m)

def label(body,loc,size,m):
    c=bpy.data.curves.new(body,'FONT'); c.body=body; c.size=size; c.align_x='CENTER'; c.extrude=.0005; o=bpy.data.objects.new(body,c); bpy.context.collection.objects.link(o); o.location=loc; o.rotation_euler=(math.pi/2,0,0); o.data.materials.append(m)

red=mat('Deep red baked enamel',(.48,.018,.028),.48,.3)
redinner=mat('Drawer interior red',(.26,.012,.021),.4,.4)
black=mat('Black rubber',(.018,.023,.027),0,.72)
dark=mat('Black powder coated steel',(.037,.045,.053),.65,.34)
steel=mat('Zinc plated hardware',(.55,.62,.67),.85,.24)
white=mat('Label lettering',(.77,.81,.80),.05,.4)
# Four separate caster assemblies, with axles and swivel bearings.
for x in (-1.26,1.26):
    for y in (-.68,.68):
        rod('Swivel bearing',(x,y,.57),(x,y,.70),.145,steel)
        box('Caster mounting plate',(x,y,.72),(.39,.34,.07),steel,.025)
        cy=y-.07
        rod('Rubber caster wheel',(x-.105,cy,.31),(x+.105,cy,.31),.29,black,64)
        for side in (-1,1):
            rod('Pressed wheel hub',(x+side*.109,cy,.31),(x+side*.122,cy,.31),.155,steel)
            box('Caster fork',(x+side*.15,y-.025,.45),(.065,.22,.35),steel,.045)
            rod('Axle bolt',(x+side*.177,cy,.31),(x+side*.19,cy,.31),.055,dark,6)
        rod('Caster axle',(x-.21,cy,.31),(x+.21,cy,.31),.043,steel)
        if y<0: box('Foot brake pedal',(x,cy-.18,.46),(.18,.28,.055),dark,.025)
        for dx in (-.12,.12):
            for dy in (-.095,.095): rod('Caster fixing bolt',(x+dx,y+dy,.757),(x+dx,y+dy,.78),.027,dark,6)
box('Cabinet base',(0,0,.84),(3.08,1.86,.18),dark,.045)
box('Left cabinet wall',(-1.48,0,1.99),(.14,1.79,2.20),red,.055)
box('Right cabinet wall',(1.48,0,1.99),(.14,1.79,2.20),red,.055)
box('Back panel',(0,.84,1.99),(2.86,.12,2.20),red,.045)
box('Dark drawer cavity',(0,.73,1.98),(2.77,.08,2.08),dark,.01)
box('Cabinet top',(0,0,3.13),(3.12,1.91,.15),red,.045)
box('Recessed rubber work mat',(0,-.01,3.221),(2.94,1.72,.043),black,.035)
for x in (-1.49,1.49): box('Raised worktop side lip',(x,0,3.255),(.065,1.84,.12),dark,.022)
box('Raised worktop rear lip',(0,.89,3.255),(3.0,.055,.12),dark,.018)
# Drawers stack upward; the upper drawer is pulled forward to reveal its tray.
drawers=[(.96,.47),(1.47,.38),(1.89,.32),(2.25,.29),(2.58,.26)]
for i,(bottom,height) in enumerate(drawers):
    offset=-.44 if i==4 else 0
    front_y=-.93+offset
    box('Drawer %d front'%(i+1),(0,front_y,bottom+height/2),(2.76,.105,height),red,.023)
    box('Drawer %d floor'%(i+1),(0,-.04+offset,bottom+.044),(2.63,1.66,.055),redinner,.015)
    for x in (-1.31,1.31): box('Drawer tray side',(x,-.05+offset,bottom+height/2),(.045,1.68,height-.03),redinner,.012)
    box('Drawer tray back',(0,.765+offset,bottom+height/2),(2.63,.045,height-.03),redinner,.012)
    box('Drawer pull shadow',(0,front_y-.06,bottom+height-.092),(2.43,.025,.095),dark,.018)
    box('Continuous aluminum drawer pull',(0,front_y-.112,bottom+height-.055),(2.46,.12,.06),steel,.018)
    box('Inventory label holder',(-.98,front_y-.059,bottom+.082),(.30,.015,.065),dark,.009)
    label('%02d'%(i+1),(-.98,front_y-.071,bottom+.062),.044,white)
    for x in (-1.37,1.37): box('Telescopic drawer runner',(x,-.025+offset/2,bottom+.10),(.055,1.65-offset,.06),steel,.009)
    if i==4:
        box('Drawer rubber liner',(0,-.05+offset,bottom+.08),(2.54,1.56,.016),black,.01)
        for x in (-.70,0,.70): box('Tray divider',(x,-.05+offset,bottom+.145),(.025,1.53,.13),redinner,.008)
# Upper fixed fascia and working key cylinder.
box('Lock fascia',(0,-.925,2.993),(2.77,.105,.19),red,.022)
rod('Lock cylinder',(1.13,-.984,3.0),(1.13,-1.018,3.0),.069,steel)
box('Key slot',(1.13,-1.025,3.0),(.014,.006,.075),dark,.004)
box('Brand badge',(-.90,-.984,3.0),(.74,.018,.112),dark,.015)
label('WORKSHOP',(-.90,-.998,2.976),.063,white)
# Rounded push handle on the right side, anchored at both ends.
for y in (-.60,.60):
    box('Handle mount plate',(1.564,y,2.69),(.04,.21,.30),steel,.022)
    for z in (2.60,2.78): rod('Handle mounting screw',(1.589,y,z),(1.609,y,z),.028,dark,6)
tube('Side push handle',[(1.60,-.60,2.70),(1.87,-.60,2.70),(1.96,-.47,2.70),(1.96,.47,2.70),(1.87,.60,2.70),(1.60,.60,2.70)],.058,steel)
rod('Push handle rubber grip',(1.96,-.37,2.70),(1.96,.37,2.70),.078,black)
for y in [-.56+i*.16 for i in range(8)]: box('Side ventilation slot',(1.554,y,1.24),(.012,.083,.29),dark,.023)
for x in (-1.53,1.53): box('Front corner bumper',(x,-.90,1.88),(.105,.105,1.94),dark,.03)

floor=mat('Workshop floor',(.19,.22,.25),0,.8); box('Ground',(0,0,-.045),(200,200,.1),floor,0)
scene=bpy.context.scene; scene.world.use_nodes=True; scene.world.node_tree.nodes['Background'].inputs[0].default_value=(.26,.30,.37,1); scene.world.node_tree.nodes['Background'].inputs[1].default_value=.4
for loc,power,size in [((-4,-5,7),1100,5),((5,-2,5),800,4),((1,4,7),1300,3)]:
    bpy.ops.object.light_add(type='AREA',location=loc); o=bpy.context.object; o.data.energy=power; o.data.size=size; o.rotation_euler=(Vector((0,0,1.8))-o.location).to_track_quat('-Z','Y').to_euler()
bpy.ops.object.camera_add(location=(6,-8,5.6)); cam=bpy.context.object; cam.rotation_euler=(Vector((.15,-.08,1.67))-cam.location).to_track_quat('-Z','Y').to_euler(); cam.data.type='ORTHO'; cam.data.ortho_scale=5.5; scene.camera=cam
scene.render.engine='CYCLES'; scene.render.resolution_x=1300; scene.render.resolution_y=1400; scene.render.resolution_percentage=100
