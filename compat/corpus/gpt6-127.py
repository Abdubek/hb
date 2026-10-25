import bpy, math, random
from mathutils import Vector
bpy.ops.object.select_all(action='SELECT'); bpy.ops.object.delete(use_global=False)
random.seed(18)
def mat(n,c,metal=0,rough=0.55):
    m=bpy.data.materials.new(n); m.diffuse_color=(*c,1); m.use_nodes=True; p=m.node_tree.nodes.get('Principled BSDF'); p.inputs['Base Color'].default_value=(*c,1); p.inputs['Metallic'].default_value=metal; p.inputs['Roughness'].default_value=rough; return m
def box(n,l,s,m,b=0.025):
    bpy.ops.mesh.primitive_cube_add(size=1,location=l); o=bpy.context.object; o.name=n; o.dimensions=s; bpy.ops.object.transform_apply(location=False,rotation=False,scale=True); o.data.materials.append(m)
    if b:
        mod=o.modifiers.new('Edge radii','BEVEL'); mod.width=b; mod.segments=2; o.modifiers.new('Corner normals','WEIGHTED_NORMAL')
    return o
def rod(n,a,b,r,m,v=16):
    d=Vector(b)-Vector(a); bpy.ops.mesh.primitive_cylinder_add(vertices=v,radius=r,depth=d.length,location=(Vector(a)+Vector(b))/2); o=bpy.context.object; o.name=n; o.rotation_euler=d.to_track_quat('Z','Y').to_euler(); o.data.materials.append(m); return o
def text(t,l,size,m):
    bpy.ops.object.text_add(location=l,rotation=(math.pi/2,0,0)); o=bpy.context.object; o.data.body=t; o.data.size=size; o.data.extrude=0.002; o.data.materials.append(m)
snow=mat('Wind packed snow',(0.78,0.85,0.9)); rock=mat('Slate rock',(0.22,0.26,0.29)); steel=mat('Galvanized structure',(0.3,0.37,0.41),0.7); orange=mat('Rescue orange',(0.88,0.19,0.035),0.3); ivory=mat('Insulated module panels',(0.73,0.77,0.71),0.2); dark=mat('Rubber and dark trim',(0.035,0.055,0.064)); glass=mat('Blue reflective glazing',(0.06,0.23,0.3),0.65,0.17); warm=mat('Interior light',(1,0.68,0.29)); solar=mat('Photovoltaic cells',(0.024,0.085,0.18),0.6,0.23)
p=warm.node_tree.nodes.get('Principled BSDF'); p.inputs['Emission Color'].default_value=(1,0.55,0.19,1); p.inputs['Emission Strength'].default_value=2
# A triangulated snow-covered mountain shoulder.
def height(x,y): return 0.035*x+0.13*y+0.27*math.sin(x*0.5)*math.cos(y*0.4)+max(0,y-5)*0.45
N=35; verts=[]
for j in range(N):
    for i in range(N):
        x=-17+i; y=-16+j; z=height(x,y)+random.uniform(-0.22,0.22); verts.append((x,y,z))
faces=[]
for j in range(N-1):
    for i in range(N-1):
        a=j*N+i; faces.extend([(a,a+1,a+N),(a+1,a+N+1,a+N)])
me=bpy.data.meshes.new('Mountain terrain'); me.from_pydata(verts,[],faces); me.materials.append(snow); me.materials.append(rock); ob=bpy.data.objects.new('Alpine ridge',me); bpy.context.collection.objects.link(ob)
for p in me.polygons: p.material_index=1 if p.normal.z<0.79 or random.random()<0.045 else 0
for x,y,s in [(-9,4,3),(9,6,3.5),(-7,-6,1.7),(8,-6,1.8),(-12,10,4),(3,13,5)]:
    bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=1,radius=1,location=(x,y,height(x,y)-0.25)); o=bpy.context.object; o.name='Exposed angular rock'; o.scale=(s,s*0.8,s*0.75); o.data.materials.append(rock)
# Elevated prefabricated modules, with perimeter frames and insulated wall seams.
def module(n,x,y,L,W):
    z=2.3
    for dx in (-L/2+0.35,L/2-0.35):
        for dy in (-W/2+0.3,W/2-0.3):
            xx=x+dx; yy=y+dy; gz=height(xx,yy)
            box('Concrete foundation',(xx,yy,gz+0.05),(0.85,0.85,0.4),rock)
            rod('Adjustable steel pile',(xx,yy,gz+0.2),(xx,yy,z),0.105,steel)
            box('Pile head',(xx,yy,z-0.08),(0.5,0.42,0.1),steel)
    box(n+' chassis',(x,y,z),(L+0.16,W+0.15,0.22),steel)
    box(n+' insulated shell',(x,y,z+1.36),(L,W,2.6),ivory,0.1)
    for dx in (-L/2,L/2):
        for dy in (-W/2,W/2): box('Orange corner casting',(x+dx,y+dy,z+1.37),(0.16,0.16,2.72),orange)
    for zz in (z+0.22,z+2.64):
        for dy in (-W/2,W/2): box('Perimeter frame',(x,y+dy,zz),(L,0.09,0.14),steel)
    for k in range(1,int(L/0.65)):
        xx=x-L/2+k*0.65
        box('Vertical panel seam',(xx,y-W/2-0.008,z+1.4),(0.017,0.016,2.27),steel,0)
    for xx in (x-L*0.29,x+L*0.28):
        box('Window gasket',(xx,y-W/2-0.045,z+1.54),(1.12,0.13,1.02),dark,0.09)
        box('Thermal window',(xx,y-W/2-0.12,z+1.54),(0.94,0.025,0.83),glass,0.055)
        box('Window mullion',(xx,y-W/2-0.145,z+1.54),(0.045,0.025,0.84),steel,0.008)
    box('Door gasket',(x,y-W/2-0.055,z+1.05),(0.94,0.13,2.12),dark)
    box('Insulated entry door',(x,y-W/2-0.13,z+1.07),(0.82,0.1,2.02),orange)
    box('Door glazing',(x,y-W/2-0.19,z+1.6),(0.5,0.02,0.58),glass)
    rod('Door handle',(x+0.29,y-W/2-0.25,z+0.95),(x+0.29,y-W/2-0.25,z+1.18),0.024,steel)
    box('Door porch lamp',(x,y-W/2-0.13,z+2.36),(0.4,0.15,0.09),warm)
    box('Roof cap',(x,y,z+2.75),(L+0.25,W+0.25,0.18),steel,0.05)
    box('Thin roof snow',(x-0.15,y+0.12,z+2.86),(L-0.1,W-0.15,0.1),snow,0.04)
    box('Ventilator',(x+L*0.3,y+0.3,z+3.04),(0.68,0.68,0.32),steel)
    for k in range(5): box('Vent grille',(x+L*0.3,y-0.046,z+2.94+k*0.05),(0.52,0.022,0.02),dark,0)
    text(n,(x-L/2+0.25,y-W/2-0.105,z+2.27),0.18,dark)
module('01 / HABITAT',-3.6,1.8,5.5,3.1)
module('02 / LAB',3.5,1.8,5.5,3.1)
module('03 / OPERATIONS',0,7,6.4,3.2)
# Deck planking and tubular safety rails, with an access stair opening.
def deck(n,x,y,L,W,rail=True):
    z=2.3; box(n,(x,y,z-0.05),(L,W,0.17),steel)
    for i in range(int(L/0.22)):
        xx=x-L/2+0.11+i*0.22; box('Anti slip deck plank',(xx,y,z+0.06),(0.19,W-0.07,0.045),dark,0.006)
    if rail:
        for yy in (y-W/2,y+W/2):
            rod('Guardrail',(x-L/2,yy,z+1.08),(x+L/2,yy,z+1.08),0.035,orange)
            rod('Mid rail',(x-L/2,yy,z+0.56),(x+L/2,yy,z+0.56),0.025,steel)
            for i in range(math.ceil(L/1.3)+1):
                xx=x-L/2+L*i/math.ceil(L/1.3); rod('Rail post',(xx,yy,z),(xx,yy,z+1.08),0.035,steel)
deck('Front interconnecting deck',0,-0.65,13.5,1.55,False)
for a,b in [(-6.75,-0.8),(0.8,6.75)]:
    for z in (2.87,3.38): rod('Front deck rail',(a,-1.425,z),(b,-1.425,z),0.033,orange if z>3 else steel)
    for i in range(6):
        x=a+(b-a)*i/5; rod('Deck post',(x,-1.425,2.3),(x,-1.425,3.38),0.035,steel)
# Narrow bridge from the central gap to the rear module.
deck('Bridge landing',0,4.7,1.55,1.4,False)
box('Central bridge',(0,2.08,2.27),(1.25,5.9,0.18),steel)
for x in (-0.65,0.65):
    for z in (2.86,3.38): rod('Bridge handrail',(x,0.1,z),(x,5.2,z),0.034,orange)
    for y in (0.2,1.4,2.6,3.8,5.1): rod('Bridge upright',(x,y,2.3),(x,y,3.38),0.032,steel)
for x in (-5.7,5.7):
    rod('Under deck diagonal',(x,-0.65,height(x,-0.65)+0.3),(x+(-1 if x>0 else 1),-0.65,2.25),0.055,steel)
# Stairs descend toward the camera.
steps=10
for i in range(steps):
    y=-1.6-i*0.31; z=2.29-i*0.27; box('Serrated stair tread',(0,y,z),(1.4,0.34,0.09),steel)
for x in (-0.76,0.76):
    rod('Stair stringer',(x,-1.45,2.14),(x,-4.48,-0.44),0.065,steel)
    rod('Stair handrail',(x,-1.45,3.34),(x,-4.48,0.76),0.038,orange)
    for i in (0,3,6,9): rod('Stair baluster',(x,-1.6-i*0.31,2.29-i*0.27),(x,-1.6-i*0.31,3.21-i*0.27),0.03,steel)
# Roof solar rack with discrete cell grid.
for xx in (-4.9,-3.15):
    panel=box('Solar panel frame',(xx,1.8,5.52),(1.5,2,0.08),steel); panel.rotation_euler.x=math.radians(18)
    for i in range(4):
        for j in range(6):
            local=Vector((-0.55+i*0.365,-0.81+j*0.323,0.052)); pos=panel.matrix_world @ local
            cell=box('Individual solar cell',pos,(0.34,0.3,0.017),solar,0.003); cell.rotation_euler=panel.rotation_euler
# Weather instrument mast and guy cables.
rod('Weather mast',(6.9,3.6,height(6.9,3.6)),(6.9,3.6,8.8),0.065,steel)
for dx,dy in ((-1.4,0.8),(1.4,1),(0,-1.7)): rod('Guy wire',(6.9,3.6,7.2),(6.9+dx,3.6+dy,height(6.9+dx,3.6+dy)),0.012,dark,8)
rod('Anemometer crossbar',(6.35,3.6,8.65),(7.45,3.6,8.65),0.025,steel)
for xx in (6.35,7.45):
    bpy.ops.mesh.primitive_uv_sphere_add(segments=16,ring_count=8,radius=0.13,location=(xx,3.6,8.7)); bpy.context.object.data.materials.append(orange)
box('Instrument enclosure',(6.9,3.6,6.7),(0.4,0.4,0.5),ivory)
text('ALPINE RESEARCH / 4080 M',(-2.8,5.375,4.52),0.23,orange)
scene=bpy.context.scene; scene.world.use_nodes=True; scene.world.node_tree.nodes['Background'].inputs[0].default_value=(0.55,0.68,0.85,1); scene.world.node_tree.nodes['Background'].inputs[1].default_value=0.5
bpy.ops.object.light_add(type='SUN',rotation=(math.radians(24),math.radians(-30),math.radians(-35))); bpy.context.object.data.energy=3; bpy.context.object.data.angle=0.14
bpy.ops.object.light_add(type='AREA',location=(0,-8,15)); bpy.context.object.data.energy=1800; bpy.context.object.data.size=12
bpy.ops.object.camera_add(location=(20,-27,20)); cam=bpy.context.object; cam.rotation_euler=(Vector((0,2,2.5))-cam.location).to_track_quat('-Z','Y').to_euler(); cam.data.type='ORTHO'; cam.data.ortho_scale=26; scene.camera=cam
scene.render.engine='CYCLES'; scene.render.resolution_x=1600; scene.render.resolution_y=1200; scene.render.resolution_percentage=100
