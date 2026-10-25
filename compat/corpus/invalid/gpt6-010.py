import bpy, math
from mathutils import Vector
bpy.ops.wm.read_factory_settings(use_empty=True)

def mat(name,color,metal=0,rough=.5):
    m=bpy.data.materials.new(name); m.diffuse_color=(*color,1); m.use_nodes=True; p=m.node_tree.nodes.get('Principled BSDF'); p.inputs['Base Color'].default_value=(*color,1); p.inputs['Metallic'].default_value=metal; p.inputs['Roughness'].default_value=rough; return m

def box(name,loc,size,material,bevel=0):
    bpy.ops.mesh.primitive_cube_add(size=1,location=loc); o=bpy.context.object; o.name=name; o.dimensions=size; bpy.ops.object.transform_apply(location=False,rotation=False,scale=True); o.data.materials.append(material)
    if bevel:
        b=o.modifiers.new('Soft edges','BEVEL'); b.width=bevel; b.segments=3; o.modifiers.new('Weighted normals','WEIGHTED_NORMAL')
    return o

def rod(name,a,b,r,material,vertices=32):
    a,b=Vector(a),Vector(b); d=b-a; bpy.ops.mesh.primitive_cylinder_add(vertices=vertices,radius=r,depth=d.length,location=(a+b)/2); o=bpy.context.object; o.name=name; o.rotation_euler=d.to_track_quat('Z','Y').to_euler(); o.data.materials.append(material)
    for p in o.data.polygons: p.use_smooth=True
    return o

def lathe(name,profile,material,n=64):
    verts=[]; faces=[]
    for r,z in profile:
        for j in range(n):
            a=2*math.pi*j/n; verts.append((r*math.cos(a),r*math.sin(a),z))
    for i in range(len(profile)-1):
        for j in range(n):
            k=(j+1)%n; faces.append((i*n+j,i*n+k,(i+1)*n+k,(i+1)*n+j))
    mesh=bpy.data.meshes.new(name); mesh.from_pydata(verts,[],faces); mesh.update(); o=bpy.data.objects.new(name,mesh); bpy.context.collection.objects.link(o); mesh.materials.append(material)
    for f in mesh.polygons: f.use_smooth=True
    return o

navy=mat('Midnight blue cabinetry',(.055,.115,.14),0,.43); oak=mat('Natural oak',(.48,.30,.15),0,.52); brass=mat('Brushed brass',(.60,.39,.14),.78,.3); black=mat('Black pendant cords',(.02,.025,.028),.15,.7); stone=mat('Ivory quartz',(.88,.86,.80),0,.26); floor=mat('Warm limestone floor',(.58,.55,.49),0,.88); grout=mat('Tile joints',(.36,.34,.3),0,.95); leather=mat('Saddle leather seats',(.43,.19,.075),0,.57); ceramic=mat('Glazed warm white ceramic',(.89,.86,.77),0,.25); red=mat('Red apples',(.48,.035,.025),0,.28); green=mat('Green apples',(.39,.52,.09),0,.32)
# Quiet procedural variation in the quartz, generated without image textures.
nt=stone.node_tree; p=nt.nodes.get('Principled BSDF'); noise=nt.nodes.new('ShaderNodeTexNoise'); noise.inputs['Scale'].default_value=95; noise.inputs['Detail'].default_value=2; bump=nt.nodes.new('ShaderNodeBump'); bump.inputs['Strength'].default_value=.10; bump.inputs['Distance'].default_value=.008; nt.links.new(noise.outputs['Fac'],bump.inputs['Height']); nt.links.new(bump.outputs['Normal'],p.inputs['Normal'])
box('Floor platform',(0,0,-.095),(4.5,3.7,.18),grout,.025)
for i in range(6):
    for j in range(5): box('Limestone tile',(-1.875+i*.75,-1.48+j*.74,.005),(.742,.732,.025),floor,.004)
# 2.6 x 1.1 m island, with 30 cm knee overhang on the stool side.
box('Recessed toe kick',(0,.13,.075),(2.32,.66,.15),black,.012)
box('Cabinet carcass',(0,.13,.51),(2.43,.72,.78),navy,.015)
box('Quartz countertop',(0,0,.94),(2.64,1.10,.08),stone,.018)
# Waterfall end panels down to the floor.
for x in [-1.285,1.285]: box('Quartz waterfall end',(x,0,.49),(.07,1.10,.90),stone,.012)
# Three framed cabinet fronts face the working side (positive Y).
for x in [-.79,0,.79]:
    box('Drawer face',(x,.504,.785),(.762,.045,.19),navy,.008)
    box('Cupboard door',(x,.504,.42),(.762,.045,.52),navy,.008)
    box('Recessed door center',(x,.531,.42),(. sixty if False else .60,.008,.36),navy,.004)
    rod('Drawer brass handle',(x-.135,.566,.79),(x+.135,.566,.79),.013,brass)
    for dx in [-.135,.135]: rod('Handle standoff',(x+dx,.524,.79),(x+dx,.566,.79),.010,brass)
    rod('Door pull',(x+.24,.565,.49),(x+.24,.565,.63),.011,brass)
    for z in [.49,.63]: rod('Door pull mount',(x+.24,.527,z),(x+.24,.565,z),.009,brass)
# Oak slats on the seating face below the overhang.
box('Seating face shadow backing',(0,-.244,.52),(2.43,.025,.73),black)
for i in range(36): box('Oak vertical fluting',(-1.17+i*.067,-.268,.52),(.047,.035,.73),oak,.009)
# Three counter-height stools with splayed legs and rounded upholstered seats.
for x in [-.85,0,.85]:
    y=-1.00
    rod('Oak seat rim',(x,y,.62),(x,y,.672),.225,oak,48)
    o=rod('Leather seat cushion',(x,y,.674),(x,y,.715),.215,leather,48)
    b=o.modifiers.new('Cushion rounding','BEVEL'); b.width=.018; b.segments=3; o.modifiers.new('Weighted normals','WEIGHTED_NORMAL')
    for dx in [-1,1]:
        for dy in [-1,1]:
            rod('Splayed stool leg',(x+dx*.215,y+dy*.215,.035),(x+dx*.14,y+dy*.14,.64),.022,oak)
            rod('Brass foot sleeve',(x+dx*.215,y+dy*.215,.025),(x+dx*.208,y+dy*.208,.095),.023,brass)
    for dy in [-1,1]: rod('Stool footrest',(x-.19,y+dy*.19,.25),(x+.19,y+dy*.19,.25),.012,brass)
    for dx in [-1,1]: rod('Stool side stretcher',(x+dx*.19,y-.19,.25),(x+dx*.19,y+.19,.25),.012,brass)
    # Low curved back in a horizontal arc, upholstered over a timber shell.
    verts=[]; faces=[]; n=24
    for z,r in [(.77,.225),(.94,.225),(.77,.245),(.94,.245)]:
        for j in range(n+1):
            a=math.radians(205+130*j/n); verts.append((x+r*math.cos(a),y+r*math.sin(a),z))
    stride=n+1
    for j in range(n):
        faces.extend([(j,j+1,stride+j+1,stride+j),(2*stride+j,3*stride+j,3*stride+j+1,2*stride+j+1),(stride+j,stride+j+1,3*stride+j+1,3*stride+j),(j,2*stride+j,2*stride+j+1,j+1)])
    faces.extend([(0,stride,3*stride,2*stride),(n,2*stride+n,3*stride+n,stride+n)])
    mesh=bpy.data.meshes.new('Curved stool back'); mesh.from_pydata(verts,[],faces); mesh.update(); o=bpy.data.objects.new('Upholstered curved backrest',mesh); bpy.context.collection.objects.link(o); o.data.materials.append(leather)
    b=o.modifiers.new('Backrest edge rounding','BEVEL'); b.width=.012; b.segments=3; o.modifiers.new('Weighted normals','WEIGHTED_NORMAL')
    for dx in [-.15,.15]: rod('Backrest support',(x+dx,y-.14,.63),(x+dx,y-.17,.82),.012,brass)
# Three pendant shades modeled as hollow spun-metal shells with inner surfaces.
for x in [-.84,0,.84]:
    rod('Ceiling canopy',(x,0,2.88),(x,0,2.93),.085,brass)
    rod('Pendant suspension cable',(x,0,2.37),(x,0,2.88),.008,black,16)
    rod('Pendant neck',(x,0,2.32),(x,0,2.40),.027,brass)
    profile=[(.026,.25),(.075,.238),(.135,.19),(.19,.12),(.245,.025),(.245,0),(.235,0),(.235,.02),(.181,.112),(.126,.181),(.069,.226),(.026,.238),(.026,.25)]
    shade=lathe('Hollow brass pendant shade',profile,brass); shade.location=(x,0,2.08)
    rod('Bulb socket',(x,0,2.20),(x,0,2.29),.035,ceramic)
    bpy.ops.mesh.primitive_uv_sphere_add(segments=24,ring_count=12,radius=.057,location=(x,0,2.15)); o=bpy.context.object; o.name='Frosted pendant bulb'; o.data.materials.append(ceramic)
    bpy.ops.object.light_add(type='AREA',location=(x,0,2.085)); o=bpy.context.object; o.name='Pendant warm light'; o.data.energy=65; o.data.color=(1,.76,.46); o.data.shape='DISK'; o.data.size=.20
# Countertop accessories: cutting board, shallow bowl and fruit.
board=box('Oak chopping board',(-.74,.04,.994),(.48,.36,.028),oak,.045)
box('Board handle',(-1.02,.04,.994),(.18,.11,.026),oak,.04)
bowl=lathe('Ceramic fruit bowl',[(0,0),(.11,0),(.19,.065),(.215,.12),(.204,.126),(.18,.074),(.103,.014),(0,.014)],ceramic); bowl.location=(.49,.03,.984)
for i in range(4):
    a=i*2.4; x=.49+.09*math.cos(a); y=.03+.08*math.sin(a); z=1.09+(i//3)*.055
    bpy.ops.mesh.primitive_uv_sphere_add(segments=24,ring_count=16,radius=.065,location=(x,y,z)); o=bpy.context.object; o.name='Bowl apple'; o.scale=(1,1,.9); o.data.materials.append(red if i%2 else green)
    rod('Apple stem',(x,y,z+.047),(x+.004,y,z+.074),.005,oak,12)
scene=bpy.context.scene; scene.world.color=(.25,.25,.25)
for loc,power,size in [((1,-4,5),700,4),((-3,1,4),550,3),((2,3,5),700,3)]:
    bpy.ops.object.light_add(type='AREA',location=loc); o=bpy.context.object; o.data.energy=power; o.data.size=size; o.rotation_euler=(Vector((0,0,1))-o.location).to_track_quat('-Z','Y').to_euler()
bpy.ops.object.camera_add(location=(5,-6,4.3)); cam=bpy.context.object; cam.rotation_euler=(Vector((0,-.12,1.25))-cam.location).to_track_quat('-Z','Y').to_euler(); cam.data.type='ORTHO'; cam.data.ortho_scale=5.3; scene.camera=cam
scene.unit_settings.system='METRIC'; scene.render.resolution_x=1400; scene.render.resolution_y=1400; scene.render.resolution_percentage=100
