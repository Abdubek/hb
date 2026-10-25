import bpy, math
from mathutils import Vector

bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)

def mat(name, color, metallic=0, roughness=.45, transmission=0):
    m=bpy.data.materials.new(name); m.diffuse_color=(*color,1); m.use_nodes=True
    p=m.node_tree.nodes.get('Principled BSDF'); p.inputs['Base Color'].default_value=(*color,1)
    p.inputs['Metallic'].default_value=metallic; p.inputs['Roughness'].default_value=roughness
    p.inputs['Transmission Weight'].default_value=transmission
    return m

def cube(name, loc, scale, material, bevel=0):
    bpy.ops.mesh.primitive_cube_add(size=1, location=loc); o=bpy.context.object; o.name=name
    o.dimensions=scale; bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    o.data.materials.append(material)
    if bevel:
        mod=o.modifiers.new('Soft molded edges','BEVEL'); mod.width=bevel; mod.segments=2
        o.modifiers.new('Weighted corner normals','WEIGHTED_NORMAL')
    return o

def cyl(name, loc, radius, depth, material, vertices=32):
    bpy.ops.mesh.primitive_cylinder_add(vertices=vertices, radius=radius, depth=depth, location=loc)
    o=bpy.context.object; o.name=name; o.data.materials.append(material); return o

def lathe(name, profile, center, material, n=32):
    verts=[(center[0]+r*math.cos(2*math.pi*j/n),center[1]+r*math.sin(2*math.pi*j/n),center[2]+z) for r,z in profile for j in range(n)]
    faces=[]
    for i in range(len(profile)-1):
        for j in range(n):
            a=i*n+j; b=i*n+(j+1)%n; faces.append((a,b,b+n,a+n))
    me=bpy.data.meshes.new(name); me.from_pydata(verts,[],faces); me.update()
    o=bpy.data.objects.new(name,me); bpy.context.collection.objects.link(o); o.data.materials.append(material); return o

def tube(name, points, radius, material):
    cu=bpy.data.curves.new(name,'CURVE'); cu.dimensions='3D'; cu.bevel_depth=radius; cu.bevel_resolution=1
    sp=cu.splines.new('POLY'); sp.points.add(len(points)-1)
    for p,co in zip(sp.points,points): p.co=(*co,1)
    o=bpy.data.objects.new(name,cu); bpy.context.collection.objects.link(o); o.data.materials.append(material); return o

cream=mat('Warm ivory polymer',(.78,.72,.59)); dark=mat('Charcoal polymer',(.025,.032,.035))
steel=mat('Brushed stainless',(.48,.53,.55),.8,.28); glass=mat('Clear carafe glass',(.87,.96,1),0,.08,1)
coffee=mat('Dark brewed coffee',(.065,.018,.006),0,.2); red=mat('Power button',(.65,.045,.025))
green=mat('Green indicator',(.12,.8,.22)); floor=mat('Studio sand',(.22,.25,.27))
p=green.node_tree.nodes.get('Principled BSDF'); p.inputs['Emission Color'].default_value=(.1,1,.2,1); p.inputs['Emission Strength'].default_value=2

cube('Broad base',(0,0,.17),(2.35,1.95,.3),dark,.1)
for x in (-.85,.85):
    for y in (-.68,.68): cyl('Rubber foot',(x,y,.055),.13,.1,dark,16)
cube('Rear upright water reservoir',(0,.59,1.53),(2.12,.72,2.6),cream,.12)
cube('Upper brewing head',(0,-.02,2.72),(2.15,1.85,.62),cream,.11)
cube('Front control panel',(0,-.964,2.72),(1.91,.055,.41),dark,.035)
cube('Steel accent strip',(0,-1.002,2.98),(1.78,.02,.045),steel,.008)
for x,material in ((-.58,red),(-.15,dark),(.23,dark)):
    o=cyl('Round front button',(x,-1.02,2.72),.115,.055,material,16); o.rotation_euler[0]=math.pi/2
    if material==dark:
        o=cyl('Button face',(x,-1.055,2.72),.072,.014,steel,16); o.rotation_euler[0]=math.pi/2
led=cyl('Ready light',(.68,-1.014,2.72),.044,.025,green,12); led.rotation_euler[0]=math.pi/2
cyl('Warming plate',(0,-.27,.35),.81,.065,steel)
cyl('Plate dark center',(0,-.27,.388),.72,.014,dark)
cyl('Filter basket',(0,-.25,2.32),.67,.26,dark)
cyl('Drip outlet',(0,-.25,2.14),.1,.14,steel,16)
# A closed wall cross-section forms a hollow glass vessel with a real rim.
profile=[(0,.03),(.57,.03),(.68,.12),(.73,.4),(.72,.77),(.61,1.04),(.48,1.15),(.48,1.24),(.445,1.24),(.445,1.16),(.575,1.02),(.68,.76),(.69,.4),(.64,.14),(.55,.075),(0,.075)]
lathe('Faceted hollow glass carafe',profile,(0,-.27,.4),glass)
lathe('Coffee volume',[(0,.08),(.55,.08),(.635,.15),(.679,.4),(.672,.65),(0,.65)],(0,-.27,.4),coffee)
cyl('Carafe lid',(0,-.27,1.69),.53,.1,dark)
cyl('Lid grip',(0,-.27,1.775),.19,.075,dark,16)
tube('Angular carafe handle',[(.46,-.27,1.58),(.98,-.27,1.57),(1.12,-.27,1.39),(1.12,-.27,.78),(.94,-.27,.62),(.66,-.27,.69)],.09,dark)
cube('Handle upper mount',(.52,-.27,1.55),(.2,.25,.19),dark,.04)
# Short glass pouring lip attached to the opposite side of the neck.
verts=[(-.42,-.43,1.59),(-.42,-.11,1.59),(-.77,-.15,1.71),(-.77,-.39,1.71)]
me=bpy.data.meshes.new('Pour lip'); me.from_pydata(verts,[],[(0,1,2,3)]); me.update()
o=bpy.data.objects.new('Pouring lip',me); bpy.context.collection.objects.link(o); o.data.materials.append(glass)
mod=o.modifiers.new('Lip wall','SOLIDIFY'); mod.thickness=.035
cube('Reservoir lid',(0,.6,3.07),(1.88,.63,.11),dark,.045)
cube('Side water gauge',(1.072,.64,1.72),(.025,.28,1.2),dark,.04)
for i in range(6): cube('Water level mark',(1.091,.59,1.23+i*.19),(.018,.12,.022),steel)
cube('Ground',(0,0,-.09),(200,200,.1),floor)

world=bpy.context.scene.world; world.use_nodes=True; world.node_tree.nodes['Background'].inputs[0].default_value=(.3,.35,.4,1); world.node_tree.nodes['Background'].inputs[1].default_value=.45
for name,loc,power,size in [('Key',(3,-4,7),650,4),('Fill',(-4,-2,4),400,3),('Rim',(1,4,6),800,3)]:
    bpy.ops.object.light_add(type='AREA',location=loc); o=bpy.context.object; o.name=name; o.data.energy=power; o.data.shape='DISK'; o.data.size=size; o.rotation_euler=(Vector((0,0,1.4))-o.location).to_track_quat('-Z','Y').to_euler()
bpy.ops.object.camera_add(location=(5,-7,4.8)); cam=bpy.context.object; cam.rotation_euler=(Vector((0,0,1.5))-cam.location).to_track_quat('-Z','Y').to_euler(); cam.data.type='ORTHO'; cam.data.ortho_scale=5.2
scene=bpy.context.scene; scene.camera=cam; scene.render.engine='CYCLES'; scene.cycles.samples=64; scene.render.resolution_x=1000; scene.render.resolution_y=1000; scene.render.resolution_percentage=100
