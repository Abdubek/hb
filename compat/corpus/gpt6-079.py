import bpy, math
from mathutils import Vector
bpy.ops.object.select_all(action='SELECT'); bpy.ops.object.delete(use_global=False)

def mat(name,c,metal=0,rough=.5):
    m=bpy.data.materials.new(name); m.diffuse_color=(*c,1); m.use_nodes=True; p=m.node_tree.nodes.get('Principled BSDF'); p.inputs['Base Color'].default_value=(*c,1); p.inputs['Metallic'].default_value=metal; p.inputs['Roughness'].default_value=rough; return m
paint=mat('Ocean blue enamel',(.045,.22,.29),.65,.4); frame=mat('Heavy blue rails',(.025,.13,.18),.7,.36); silver=mat('Galvanized locking hardware',(.55,.61,.62),.8,.28); gasket=mat('Door rubber seals',(.02,.026,.028),0,.8); stencil=mat('Ivory lettering',(.86,.88,.79)); black=mat('Casting socket shadow',(.012,.018,.02)); ground=mat('Concrete yard',(.29,.31,.31),0,.85)

def box(name,loc,dims,m,bevel=0):
    bpy.ops.mesh.primitive_cube_add(size=1,location=loc); o=bpy.context.object; o.name=name; o.dimensions=dims; bpy.ops.object.transform_apply(location=False,rotation=False,scale=True); o.data.materials.append(m)
    if bevel: b=o.modifiers.new('Formed edge radius','BEVEL'); b.width=bevel; b.segments=2; o.modifiers.new('Weighted normals','WEIGHTED_NORMAL')
    return o

def rod(name,a,b,r,m):
    d=Vector(b)-Vector(a); bpy.ops.mesh.primitive_cylinder_add(vertices=16,radius=r,depth=d.length,location=(Vector(a)+Vector(b))/2); o=bpy.context.object; o.name=name; o.rotation_euler=d.to_track_quat('Z','Y').to_euler(); o.data.materials.append(m)

def text(body,loc,size,rot,m=stencil):
    bpy.ops.object.text_add(location=loc,rotation=rot); o=bpy.context.object; o.name=body; o.data.body=body; o.data.size=size; o.data.extrude=.0006; o.data.materials.append(m)
# A nominal twenty-foot container, length on X; closed double doors on +X.
L,W,H=6.06,2.44,2.59; base=.16; top=base+H
box('Container floor',(0,0,base+.09),(L-.12,W-.13,.18),frame,.018)
# Continuous folded sheets with trapezoidal corrugation profiles.
def corrugated_side(y,sign):
    verts=[]; count=30; start=-L/2+.16; span=L-.32
    for i in range(count):
        for t,depth in ((0,0),(.20,0),(.38,.048),(.70,.048),(.88,0)):
            x=start+(i+t)*span/count
            verts.extend([(x,y+sign*depth,base+.21),(x,y+sign*depth,top-.18)])
    verts.extend([(start+span,y,base+.21),(start+span,y,top-.18)])
    faces=[(i,i+2,i+3,i+1) for i in range(0,len(verts)-2,2)]
    me=bpy.data.meshes.new('Folded side sheet'); me.from_pydata(verts,[],faces); me.update(); o=bpy.data.objects.new('Corrugated steel side',me); bpy.context.collection.objects.link(o); o.data.materials.append(paint); s=o.modifiers.new('Steel sheet thickness','SOLIDIFY'); s.thickness=.012; b=o.modifiers.new('Fold radii','BEVEL'); b.width=.006; b.segments=2
corrugated_side(-W/2+.055,-1); corrugated_side(W/2-.055,1)
box('Roof sheet',(0,0,top-.075),(L-.16,W-.16,.055),paint,.015)
for i in range(27): box('Pressed roof rib',(-2.77+i*.213,0,top-.036),(.09,W-.36,.045),paint,.018)
box('Closed end sheet',(-L/2+.08,0,base+H/2),(.07,W-.23,H-.3),paint,.012)
for i in range(10): box('End wall corrugation',(-L/2+.026,-1.02+i*.227,base+H/2),(.09,.10,H-.43),paint,.022)
for y in (-W/2,W/2):
    for z in (base+.08,top-.08): box('Longitudinal structural rail',(0,y,z),(L,.12,.16),frame,.016)
for x in (-L/2,L/2):
    for z in (base+.08,top-.08): box('End header or sill',(x,0,z),(.14,W,.16),frame,.013)
    for y in (-W/2,W/2):
        box('Corner post',(x,y,base+H/2),(.16,.16,H),frame,.014)
        for z in (base+.10,top-.10):
            box('Corner casting',(x,y,z),(.22,.20,.20),silver,.025)
            box('End casting socket',(x+(.112 if x>0 else -.112),y,z),(.004,.095,.067),black,.025)
            box('Side casting socket',(x,y+(.102 if y>0 else -.102),z),(.10,.004,.067),black,.022)
            if z>1: box('Top twistlock socket',(x,y,z+.102),(.10,.073,.004),black,.025)
# Two individually framed doors with perimeter seals and four locking rods.
for side in (-1,1):
    yc=side*.575
    box('Door gasket',(L/2+.014,yc,base+H/2),(.045,1.145,H-.27),gasket,.014)
    box('Door leaf',(L/2+.048,yc,base+H/2),(.045,1.085,H-.33),paint,.012)
    for y in (yc-.52,yc+.52): box('Door vertical edge',(L/2+.082,y,base+H/2),(.04,.055,H-.34),frame,.008)
    for z in (base+.20,top-.20): box('Door horizontal edge',(L/2+.085,yc,z),(.04,1.08,.07),frame,.008)
    for yoff in (-.36,-.12,.12,.36): box('Door pressed rib',(L/2+.09,yc+yoff,base+H/2),(.058,.08,H-.57),paint,.018)
    for y in (yc-.30,yc+.30):
        rod('Vertical locking bar',(L/2+.16,y,base+.22),(L/2+.16,y,top-.22),.026,silver)
        for z in (base+.32,base+.9,top-.8,top-.32): box('Lock rod bearing',(L/2+.16,y,z),(.105,.095,.065),silver,.012)
        for z in (base+.23,top-.23): box('Locking cam',(L/2+.14,y+.045,z),(.11,.16,.06),silver,.012)
        rod('Lock lever',(L/2+.21,y,1.20),(L/2+.21,y+.20,1.20),.018,silver)
        box('Handle keeper',(L/2+.20,y+.17,1.20),(.08,.06,.12),silver,.008)
    for z in (.67,1.43,2.19):
        y=side*1.105; box('Door hinge strap',(L/2+.105,y-side*.075,z),(.075,.20,.08),silver,.01); rod('Hinge pin',(L/2+.105,y,z-.08),(L/2+.105,y,z+.08),.031,silver)
# Door text orientation: local text X is world Y, local Y is world Z.
rot=(math.pi/2,0,math.pi/2)
text('NORTHLINE',(L/2+.125,-1.04,2.31),.12,rot)
text('NCLU 204581 7',(L/2+.127,.07,2.28),.092,rot)
text('22G1',(L/2+.127,.10,2.11),.105,rot)
text('MAX GROSS  30,480 KG\nTARE          2,180 KG\nNET          28,300 KG',(L/2+.127,.05,1.82),.066,rot)
box('CSC plate',(L/2+.13,-.83,.64),(.015,.28,.19),silver,.005)
text('CSC\nAPPROVED',(L/2+.142,-.94,.67),.042,rot,black)
text('NORTHLINE',(-1.85,-W/2-.007,1.53),.35,(math.pi/2,0,0))
box('Container yard',(0,0,-.08),(13,10,.16),ground,.03)
for loc,power,size in [((5,-6,10),1700,7),((-5,-2,6),1100,5),((1,6,7),1000,5)]:
    bpy.ops.object.light_add(type='AREA',location=loc); o=bpy.context.object; o.data.energy=power; o.data.size=size; o.rotation_euler=(Vector((0,0,1))-o.location).to_track_quat('-Z','Y').to_euler()
bpy.ops.object.camera_add(location=(10,-11,7)); cam=bpy.context.object; cam.rotation_euler=(Vector((0,0,1.25))-cam.location).to_track_quat('-Z','Y').to_euler(); cam.data.type='ORTHO'; cam.data.ortho_scale=9
s=bpy.context.scene; s.camera=cam; s.world.color=(.20,.20,.20); s.render.engine='CYCLES'; s.render.resolution_x=1400; s.render.resolution_y=1000; s.render.resolution_percentage=100
