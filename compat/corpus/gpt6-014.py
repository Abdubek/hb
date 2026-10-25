import bpy, math, random
from mathutils import Vector

bpy.ops.object.select_all(action='SELECT'); bpy.ops.object.delete(use_global=False)
random.seed(14)

def mat(name,color,rough=.5,metal=0):
    m=bpy.data.materials.new(name); m.diffuse_color=(*color,1); m.use_nodes=True
    p=m.node_tree.nodes.get('Principled BSDF'); p.inputs['Base Color'].default_value=(*color,1); p.inputs['Roughness'].default_value=rough; p.inputs['Metallic'].default_value=metal; return m

def box(name,loc,dims,m,bevel=.012):
    bpy.ops.mesh.primitive_cube_add(size=1,location=loc); o=bpy.context.object; o.name=name; o.dimensions=dims
    bpy.ops.object.transform_apply(location=False,rotation=False,scale=True); o.data.materials.append(m)
    if bevel:
        b=o.modifiers.new('Furniture edge','BEVEL'); b.width=bevel; b.segments=2; o.modifiers.new('Weighted normals','WEIGHTED_NORMAL')
    return o

def cylinder(name,loc,r,d,m):
    bpy.ops.mesh.primitive_cylinder_add(vertices=24,radius=r,depth=d,location=loc); o=bpy.context.object; o.name=name; o.data.materials.append(m); return o

oak=mat('Natural pale oak',(.61,.41,.22)); edge=mat('End grain and edge band',(.72,.53,.3)); back=mat('Warm gray backing',(.28,.31,.3)); pages=mat('Cream paper',(.8,.76,.63),.85)
gold=mat('Spine foil',(.69,.5,.21),.3,.65); steel=mat('Dark steel fasteners',(.09,.11,.115),.35,.65); pottery=mat('Matte clay',(.63,.25,.13),.8)
colors=[('Ocean',(.055,.2,.24)),('Terracotta',(.55,.16,.09)),('Mustard',(.61,.4,.07)),('Ink',(.035,.065,.11)),('Sage',(.29,.4,.3)),('Linen',(.64,.59,.46)),('Plum',(.29,.1,.19))]
covers=[mat('Book cloth '+n,c,.75) for n,c in colors]; floor=mat('Warm studio floor',(.35,.33,.29))
# Four interchangeable bays share full-height uprights; shelf heights alternate.
width=6.6; height=5.4; depth=.96
box('Back panel',(0,.45,2.88),(width,.075,height),back)
box('Base plinth',(0,0,.2),(6.73,1.03,.28),oak,.04)
box('Bottom shelf',(0,-.015,.39),(6.73,1.02,.15),oak,.025)
box('Crown shelf',(0,-.015,5.65),(6.73,1.02,.15),oak,.025)
uprights=[-3.24,-1.62,0,1.62,3.24]
for x in uprights:
    box('Modular vertical panel',(x,0,3.0),(.13,.98,5.24),oak,.018)
    box('Front edge band',(x,-.496,3.0),(.132,.018,5.23),edge,.005)
    for z in [1.02+i*.22 for i in range(19)]:
        # Visible shelf-pin sockets on the front edge make the modular construction legible.
        o=cylinder('Shelf adjustment socket',(x,-.51,z),.012,.009,steel); o.rotation_euler[0]=math.pi/2
for x in (-2.7,2.7):
    for y in (-.31,.31): cylinder('Recessed furniture foot',(x,y,.065),.075,.12,steel)

shelf_levels=[[.465,1.72,3.1,4.43,5.575],[.465,2.1,3.65,5.575],[.465,1.57,2.92,4.27,5.575],[.465,2.02,3.51,4.7,5.575]]

def book(name,x,y,z,w,d,h,material,lean=0):
    root=bpy.data.objects.new(name,None); bpy.context.collection.objects.link(root); root.location=(x,y,z); root.rotation_euler[1]=lean
    parts=[('Paper block',(0,.016,h/2),(w-.035,d-.048,h-.044),pages),('Left cover',(-w/2+.009,0,h/2),(.018,d,h),material),('Right cover',(w/2-.009,0,h/2),(.018,d,h),material),('Rounded spine',(0,-d/2+.012,h/2),(w,.035,h),material)]
    for suffix,loc,dims,m in parts:
        o=box(name+' '+suffix,loc,dims,m,.005); o.parent=root
    for zz in (.13,h-.14):
        o=box('Spine foil rule',(0,-d/2-.008,zz),(w*.75,.009,.016),gold,.002); o.parent=root
    o=box('Spine title plaque',(0,-d/2-.008,h*.62),(w*.56,.009,min(.18,h*.2)),pages,.002); o.parent=root
    return root

def stack_book(x,y,z,w,d,h,m):
    box('Stacked paper',(x,y,z+h/2),(w-.035,d-.035,h-.025),pages,.006)
    for zz in (z+.008,z+h-.008): box('Stacked cover',(x,y,zz),(w,d,.016),m,.006)
    box('Stacked spine',(x,y-d/2,z+h/2),(w,.028,h),m,.006)

def vase(x,y,z):
    profile=[(0,0),(.17,0),(.25,.08),(.27,.32),(.2,.48),(.12,.55),(.12,.69),(.09,.69),(.09,.55),(.17,.46),(.23,.3),(.21,.09),(.14,.035),(0,.035)]
    n=32; vs=[(x+r*math.cos(j*math.tau/n),y+r*math.sin(j*math.tau/n),z+zz) for r,zz in profile for j in range(n)]
    fs=[(i*n+j,i*n+(j+1)%n,(i+1)*n+(j+1)%n,(i+1)*n+j) for i in range(len(profile)-1) for j in range(n)]
    me=bpy.data.meshes.new('Vase mesh'); me.from_pydata(vs,[],fs); me.update(); ob=bpy.data.objects.new('Ceramic display vase',me); bpy.context.collection.objects.link(ob); me.materials.append(pottery)

for bay,levels in enumerate(shelf_levels):
    left=uprights[bay]+.075; right=uprights[bay+1]-.075; center=(left+right)/2
    for level in levels[1:-1]:
        box('Staggered adjustable shelf',(center,0,level-.06),(right-left,.96,.12),oak,.016)
        box('Shelf front edge',(center,-.488,level-.06),(right-left,.018,.122),edge,.004)
    for row,(bottom,top) in enumerate(zip(levels,levels[1:])):
        clearance=top-bottom-.14
        if (bay,row) in [(1,1),(3,2)]:
            vase(center+.25,-.05,bottom)
            z=bottom
            for k in range(3):
                stack_book(center-.35,-.08,z,.66,.58,.12,covers[(k+bay)%len(covers)]); z+=.125
        elif (bay,row)==(2,2):
            for k in range(4): stack_book(center-.15,-.08,bottom+k*.14,.92,.64,.135,covers[k])
            book('Single tall volume',right-.21,-.1,bottom,.19,.6,clearance*.81,covers[4])
        else:
            x=left+.1
            count=random.randint(4,6)
            for k in range(count):
                w=random.uniform(.14,.22); h=random.uniform(clearance*.62,clearance*.88); d=random.uniform(.56,.76)
                if x+w>right-.08: break
                book('Bay %d row %d volume %d'%(bay+1,row+1,k+1),x+w/2,-.09,bottom,w,d,h,random.choice(covers)); x+=w+.023
            if right-x>.3:
                # A steel bookend with horizontal foot and vertical support.
                box('Bookend foot',(x+.05,-.07,bottom+.014),(.24,.6,.025),steel,.006)
                box('Bookend upright',(x+.13,-.07,bottom+.21),(.025,.6,.4),steel,.008)
box('Ground',(0,0,-.07),(200,200,.1),floor,0)
world=bpy.context.scene.world; world.use_nodes=True; world.node_tree.nodes['Background'].inputs[1].default_value=.45
for loc,energy,size in [((0,-5,9),1300,6),((-6,-3,4),800,5),((5,3,8),1100,4)]:
    bpy.ops.object.light_add(type='AREA',location=loc); o=bpy.context.object; o.data.energy=energy; o.data.size=size; o.rotation_euler=(Vector((0,0,2.5))-o.location).to_track_quat('-Z','Y').to_euler()
bpy.ops.object.camera_add(location=(8,-13,8)); cam=bpy.context.object; cam.rotation_euler=(Vector((0,0,2.85))-cam.location).to_track_quat('-Z','Y').to_euler(); cam.data.type='ORTHO'; cam.data.ortho_scale=9.2
scene=bpy.context.scene; scene.camera=cam; scene.render.engine='CYCLES'; scene.cycles.samples=64; scene.render.resolution_x=1200; scene.render.resolution_y=1100; scene.render.resolution_percentage=100
