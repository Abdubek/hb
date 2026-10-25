import bpy, math, random
from mathutils import Vector
random.seed(29)
bpy.ops.object.select_all(action='SELECT'); bpy.ops.object.delete(use_global=False)

def mat(name,c,rough=.5,metal=0):
    m=bpy.data.materials.new(name); m.diffuse_color=(*c,1); m.use_nodes=True; p=m.node_tree.nodes.get('Principled BSDF'); p.inputs['Base Color'].default_value=(*c,1); p.inputs['Roughness'].default_value=rough; p.inputs['Metallic'].default_value=metal; return m

def box(name,loc,size,m,bevel=.01):
    bpy.ops.mesh.primitive_cube_add(size=1,location=loc); o=bpy.context.object; o.name=name; o.dimensions=size; bpy.ops.object.transform_apply(location=False,rotation=False,scale=True); o.data.materials.append(m)
    if bevel: b=o.modifiers.new('Edge bevel','BEVEL'); b.width=bevel; b.segments=2; o.modifiers.new('Normals','WEIGHTED_NORMAL')
    return o

def rod(name,a,b,r,m,vertices=24):
    a=Vector(a); b=Vector(b); bpy.ops.mesh.primitive_cylinder_add(vertices=vertices,radius=r,depth=(b-a).length,location=(a+b)/2); o=bpy.context.object; o.name=name; o.rotation_euler=(b-a).to_track_quat('Z','Y').to_euler(); o.data.materials.append(m)
    bevel=o.modifiers.new('Rounded edge','BEVEL'); bevel.width=.005; bevel.segments=2; o.modifiers.new('Normals','WEIGHTED_NORMAL'); return o

def text(body,loc,size,m):
    c=bpy.data.curves.new(body,'FONT'); c.body=body; c.align_x='CENTER'; c.align_y='CENTER'; c.size=size; c.extrude=.0005; o=bpy.data.objects.new(body,c); bpy.context.collection.objects.link(o); o.location=loc; o.rotation_euler=(math.pi/2,0,0); c.materials.append(m)

blue=mat('Rack cobalt powdercoat',(.035,.115,.24),.4,.5); orange=mat('Safety orange beams',(.85,.20,.025),.38,.35); steel=mat('Galvanized shelf panels',(.40,.46,.48),.55,.7); dark=mat('Dark metal and print',(.028,.036,.043),.65); cream=mat('Inventory labels',(.88,.87,.76),.8); tape=mat('Packing tape',(.52,.33,.14),.5)
card=[mat('Kraft carton %d'%i,(.47+.055*i,.29+.04*i,.13+.027*i),.9) for i in range(4)]
red=mat('Red drum enamel',(.43,.045,.025),.35,.55); teal=mat('Teal drum enamel',(.035,.25,.26),.35,.55)
# Two bays with three storage levels and braced end frames.
for x in [-2.5,0,2.5]:
    for y in [-.64,.64]:
        box('Bolted upright',(x,y,1.91),(.115,.115,3.76),blue)
        box('Anchored footplate',(x,y,.035),(.27,.25,.055),blue)
        for dx in [-.09,.09]: rod('Anchor bolt',(x+dx,y,.06),(x+dx,y,.077),.019,steel,6)
        for k in range(23): box('Upright punched slot',(x,y-.060,.23+k*.15),(.026,.004,.062),dark,.007)
    for z in [.22,1.31,2.49,3.65]: box('End-frame cross tie',(x,0,z),(.065,1.23,.065),blue)
    for k in range(3):
        z=.24+k*1.12
        rod('End-frame diagonal',(x,-.60 if k%2==0 else .60,z),(x,.60 if k%2==0 else -.60,z+1.08),.022,blue)
for level,z in enumerate([.22,1.43,2.65]):
    for bay,cx in enumerate([-1.25,1.25]):
        for y in [-.64,.64]:
            box('Orange load beam',(cx,y,z), (2.39,.105,.16),orange)
            for xx in [cx-1.15,cx+1.15]:
                box('Beam connector plate',(xx,y,z+.035),(.15,.13,.25),orange)
                if y<0:
                    for zz in [z-.025,z+.09]: rod('Beam locking bolt',(xx,y-.075,zz),(xx,y-.06,zz),.018,steel,6)
        for k in range(5): box('Shelf galvanized decking',(cx,-.48+k*.24,z+.10),(2.37,.232,.04),steel,.004)
        box('Shelf address label',(cx,-.701,z),(.40,.006,.10),cream,.003); text('%s-%02d'%('A' if bay==0 else 'B',level+1),(cx,-.707,z),.065,dark)

def carton(name,x,y,z,w,d,h,tone=0):
    box(name,(x,y,z+h/2),(w,d,h),card[tone%4],.018)
    box('Top carton seam',(x,y,z+h+.002),(.009,d-.025,.003),dark,0)
    box('Top sealing tape',(x,y,z+h+.005),(.10,d,.005),tape,.001)
    box('Tape folded over front',(x,y-d/2-.003,z+h-.06),(.10,.006,.12),tape,.001)
    box('White carton label',(x,y-d/2-.005,z+h*.48),(w*.55,.007,h*.30),cream,.003)
    text(name,(x,y-d/2-.010,z+h*.52),min(.06,w*.10),dark)
    text('WAREHOUSE',(x,y-d/2-.010,z+h*.41),.026,dark)
    for i in range(15): box('Barcode',(x-w*.17+i*w*.022,y-d/2-.010,z+h*.59),(.005,.002,h*.055),dark,0)

def barrel(name,x,y,z,m):
    # Lathed closed steel drum with softly bulging wall and rolled ends.
    profile=[(0,.28),(.025,.305),(.055,.305),(.08,.29),(.21,.298),(.24,.316),(.28,.316),(.31,.302),(.54,.302),(.57,.316),(.61,.316),(.64,.298),(.78,.29),(.805,.307),(.835,.307),(.845,.28)]
    n=48; verts=[(x+r*math.cos(j*math.tau/n),y+r*math.sin(j*math.tau/n),z+zz) for zz,r in profile for j in range(n)]; faces=[]
    for k in range(len(profile)-1):
        for j in range(n): faces.append((k*n+j,k*n+(j+1)%n,(k+1)*n+(j+1)%n,(k+1)*n+j))
    faces.append(tuple(reversed(range(n)))); faces.append(tuple((len(profile)-1)*n+j for j in range(n)))
    mesh=bpy.data.meshes.new(name); mesh.from_pydata(verts,[],faces); mesh.update(); o=bpy.data.objects.new(name,mesh); bpy.context.collection.objects.link(o); mesh.materials.append(m)
    for p in mesh.polygons: p.use_smooth=len(p.vertices)==4
    for zz in [.035,.82]:
        bpy.ops.mesh.primitive_torus_add(major_segments=48,minor_segments=8,location=(x,y,z+zz),major_radius=.303,minor_radius=.009); bpy.context.object.name='Drum rolled rim'; bpy.context.object.data.materials.append(steel)
    rod('Drum top bung',(x+.13,y,z+.844),(x+.13,y,z+.859),.045,steel)
    rod('Small vent bung',(x-.13,y+.08,z+.844),(x-.13,y+.08,z+.854),.022,steel)
    box('Drum contents label',(x,y-.303,z+.44),(.27,.012,.17),cream,.008); text('OIL / 60 L',(x,y-.311,z+.46),.041,dark); text('SEALED',(x,y-.311,z+.405),.032,dark)

for x in [-2.02,-1.25,-.48]: barrel('Red storage drum',x,0,.34,red)
for i,x in enumerate([.62,1.62]):
    carton('BX-%02d'%(i+1),x,0,.34,.84,.94,.56,i)
    carton('BX-%02d'%(i+3),x,.02,.90,.72,.79,.35,i+1)
for i,x in enumerate([-2.03,-1.25,-.47]):
    carton('PK-%02d'%(i+1),x,0,1.55,.65,.98,.56,i+1)
    if i!=1: carton('PK-%02d'%(i+4),x,.02,2.11,.59,.79,.40,i)
for x in [.63,1.45,2.16]: barrel('Teal storage drum',x,.04,1.55,teal)
for i,x in enumerate([-2.05,-1.20,-.40,.48,1.35,2.15]): carton('ST-%02d'%(i+1),x,.02,2.77,.68,.89,.59+(i%2)*.15,i)
# Header and protective upright guards.
box('Rack header',(0,.64,3.70),(5.1,.09,.19),blue); box('Aisle sign',(0,-.70,3.66),(1.45,.035,.30),cream); text('RACK 04',(0,-.723,3.66),.19,dark)
for x in [-2.5,0,2.5]: box('Upright impact guard',(x,-.68,.25),(.21,.20,.43),orange,.018)
floor=mat('Warehouse concrete',(.25,.27,.28),.92); box('Floor',(0,0,-.04),(200,200,.07),floor,0)
for x in [-2.78,2.78]: box('Safety floor marking',(x,0,.001),(.065,2.1,.002),orange,0)
scene=bpy.context.scene; scene.world.use_nodes=True; scene.world.node_tree.nodes['Background'].inputs[1].default_value=.35
for loc,power,size in [((1,-5,7),1800,5),((-5,-2,4),1000,4),((3,4,6),1600,4)]:
    bpy.ops.object.light_add(type='AREA',location=loc); o=bpy.context.object; o.data.energy=power; o.data.size=size; o.rotation_euler=(Vector((0,0,1.8))-o.location).to_track_quat('-Z','Y').to_euler()
bpy.ops.object.camera_add(location=(7,-10,6)); cam=bpy.context.object; cam.rotation_euler=(Vector((0,0,1.85))-cam.location).to_track_quat('-Z','Y').to_euler(); cam.data.type='ORTHO'; cam.data.ortho_scale=7.3; scene.camera=cam
scene.render.engine='CYCLES'; scene.cycles.samples=64; scene.render.resolution_x=1500; scene.render.resolution_y=1150; scene.render.resolution_percentage=100
