import bpy, math, random
from mathutils import Vector
random.seed(146)
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)

def mat(name, color, rough=.65):
    m=bpy.data.materials.new(name); m.diffuse_color=(*color,1); m.use_nodes=True
    m.node_tree.nodes['Principled BSDF'].inputs['Base Color'].default_value=(*color,1)
    m.node_tree.nodes['Principled BSDF'].inputs['Roughness'].default_value=rough
    return m
sand=mat('Warm limestone',(.61,.51,.37)); edge=mat('Cut stone edges',(.78,.70,.55))
wood=mat('Oiled cedar seating',(.30,.14,.065)); grass=mat('Meadow turf',(.22,.32,.105))
soil=mat('Mulched planting beds',(.15,.095,.055)); leaf=mat('Olive foliage',(.19,.29,.11))
trunk=mat('Tree bark',(.22,.13,.075)); metal=mat('Dark bronze rails',(.10,.12,.10),.35)

def cube(name, loc, scale, material, bevel=0):
    bpy.ops.mesh.primitive_cube_add(size=1, location=loc); o=bpy.context.object; o.name=name; o.dimensions=scale
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True); o.data.materials.append(material)
    if bevel:
        m=o.modifiers.new('Soft edges','BEVEL'); m.width=bevel; m.segments=2
        o.modifiers.new('Weighted normals','WEIGHTED_NORMAL')
    return o

def beam(name,a,b,r,material):
    d=Vector(b)-Vector(a); bpy.ops.mesh.primitive_cylinder_add(vertices=12, radius=r, depth=d.length, location=(Vector(a)+Vector(b))/2)
    o=bpy.context.object; o.name=name; o.rotation_euler=d.to_track_quat('Z','Y').to_euler(); o.data.materials.append(material); return o

def sector(name, ri, ro, z0, z1, a0, a1, material):
    n=max(2,int(abs(a1-a0)/2)); verts=[]
    for z in (z0,z1):
        for r in (ri,ro):
            verts.extend([(r*math.cos(math.radians(a0+(a1-a0)*i/n)),r*math.sin(math.radians(a0+(a1-a0)*i/n)),z) for i in range(n+1)])
    k=n+1; faces=[]
    for i in range(n):
        faces.extend([(i,i+1,k+i+1,k+i),(2*k+i,3*k+i,3*k+i+1,2*k+i+1),(i,2*k+i,2*k+i+1,i+1),(k+i,k+i+1,3*k+i+1,3*k+i)])
    faces.extend([(0,k,3*k,2*k),(n,2*k+n,3*k+n,k+n)])
    me=bpy.data.meshes.new(name); me.from_pydata(verts,[],faces); me.update(); o=bpy.data.objects.new(name,me); bpy.context.collection.objects.link(o); o.data.materials.append(material); return o

cube('Landscape plinth',(0,3,-.42),(37,31,.8),grass,.3)
# Bowl opens toward the foreground; broad radial aisles separate the seating banks.
banks=[(0,18),(25,155),(162,180)]
for row in range(7):
    ri=5+row*1.35; ro=ri+1.35; top=.22+row*.53
    for a,b in banks:
        sector('Terrace %02d foundation'%row,ri,ro,-.02,top,a,b,sand)
        sector('Terrace %02d stone nosing'%row,ri,ri+.14,top,top+.07,a,b,edge)
        # Individual curved bench boards with visible joint gaps.
        count=max(1,int((b-a)/7))
        for j in range(count):
            aa=a+(b-a)*j/count+.20; bb=a+(b-a)*(j+1)/count-.20
            sector('Cedar bench board',ri+.22,ri+.68,top+.35,top+.45,aa,bb,wood)
        for angle in range(int(a)+3,int(b),12):
            t=math.radians(angle)
            cube('Bench support',((ri+.44)*math.cos(t),(ri+.44)*math.sin(t),top+.17),(.18,.20,.34),metal)
# Two side-access stair flights, two steps per terrace rise.
for a,b in [(18,25),(155,162)]:
    for i in range(14):
        ri=5+i*.675; top=.22+i*.265
        sector('Side access stair tread',ri,ri+.675,-.02,top,a,b,edge)
    for angle in (a+.6,b-.6):
        t=math.radians(angle); pts=[]
        for i in range(0,15,2):
            r=5+i*.675; z=.22+i*.265+.95
            p=(r*math.cos(t),r*math.sin(t),z); pts.append(p)
            beam('Aisle handrail post',(p[0],p[1],z-.95),p,.035,metal)
        for p,q in zip(pts,pts[1:]): beam('Sloping aisle handrail',p,q,.045,metal)
sector('Upper promenade',14.45,16.05,-.02,3.42,0,180,sand)
sector('Upper planting strip',16.1,17.1,-.02,.13,0,180,soil)
# Low stage and its accessible front apron.
bpy.ops.mesh.primitive_cylinder_add(vertices=96, radius=4.45, depth=.30, location=(0,.55,.12)); bpy.context.object.name='Circular performance stage'; bpy.context.object.data.materials.append(edge)
cube('Stage approach',(0,-4.3,.02),(7,2,.12),sand,.06)
for x in (-3.6,3.6):
    cube('Stage planter',(x,-3.2,.32),(1.1,.8,.65),sand,.08)
    for j in range(5):
        bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=1,radius=.29,location=(x+random.uniform(-.3,.3),-3.2+random.uniform(-.15,.15),.82)); bpy.context.object.data.materials.append(leaf)
for angle in range(8,178,14):
    t=math.radians(angle); x,y=16.6*math.cos(t),16.6*math.sin(t)
    beam('Tree trunk',(x,y,0),(x,y,2.4),.13,trunk)
    for j in range(3):
        bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=2,radius=1.0,location=(x+random.uniform(-.45,.45),y+random.uniform(-.4,.4),2.5+j*.35))
        o=bpy.context.object; o.name='Sculpted olive canopy'; o.scale=(1,.9,.85); o.data.materials.append(leaf)
for x in (-14.5,14.5):
    for y in (-3,-.6):
        cube('Approach bollard',(x,y,.5),(.16,.16,1),metal,.025)
        cube('Bollard light lens',(x,y,.88),(.18,.18,.12),edge,.015)
# Retaining-wall end caps expose the rising profile at either side.
for side in (-1,1):
    for i in range(7):
        cube('Terrace end coping',(side*(5.67+i*1.35),-.08,.28+i*.53),(1.34,.23,.12),edge,.025)
scene=bpy.context.scene; scene.render.engine='CYCLES'; scene.cycles.samples=64
scene.world.color=(.35,.35,.35)
bpy.ops.object.light_add(type='AREA', location=(1,-8,22)); bpy.context.object.data.energy=2600; bpy.context.object.data.shape='DISK'; bpy.context.object.data.size=13
bpy.ops.object.light_add(type='SUN', location=(-10,-10,20)); bpy.context.object.rotation_euler=(.45,-.35,-.5); bpy.context.object.data.energy=2.2; bpy.context.object.data.angle=.18
bpy.ops.object.camera_add(location=(25,-30,25)); cam=bpy.context.object; cam.rotation_euler=(Vector((0,5,1))-cam.location).to_track_quat('-Z','Y').to_euler(); cam.data.type='ORTHO'; cam.data.ortho_scale=43; scene.camera=cam
scene.render.resolution_x=1500; scene.render.resolution_y=1100; scene.render.resolution_percentage=100
