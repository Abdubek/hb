import bpy, math
from mathutils import Vector
bpy.ops.wm.read_factory_settings(use_empty=True)

def material(name, color, roughness=.45, metal=0):
    m=bpy.data.materials.new(name); m.diffuse_color=(*color,1); m.use_nodes=True
    p=m.node_tree.nodes.get('Principled BSDF'); p.inputs['Base Color'].default_value=(*color,1)
    p.inputs['Roughness'].default_value=roughness; p.inputs['Metallic'].default_value=metal
    return m
wood=material('Natural walnut',(.24,.105,.043))
wood_light=material('Walnut alternate boards',(.29,.135,.059))
fabric=material('Oatmeal upholstery',(.67,.61,.49),.9)
floor=material('Muted stone floor',(.32,.35,.34),.8)

def box(name,loc,size,mat,bevel=.015):
    bpy.ops.mesh.primitive_cube_add(size=1,location=loc)
    o=bpy.context.object; o.name=name; o.dimensions=size
    bpy.ops.object.transform_apply(location=False,rotation=False,scale=True)
    o.data.materials.append(mat)
    if bevel:
        m=o.modifiers.new('Rounded joinery','BEVEL'); m.width=bevel; m.segments=3
        o.modifiers.new('Weighted normals','WEIGHTED_NORMAL')
    return o

def beam(name,a,b,width,depth,mat):
    a,b=Vector(a),Vector(b)
    o=box(name,(a+b)/2,(width,depth,(b-a).length),mat,.009)
    o.rotation_euler=(b-a).to_track_quat('Z','Y').to_euler(); return o

# A 1.8 m table, with a five-board top and supporting aprons.
for i in range(5):
    box('Tabletop plank %d'%i,(0,-.44+(i+.5)*.176,.765),(1.8,.174,.065),wood if i%2==0 else wood_light,.008)
for x in (-.76,.76):
    for y in (-.32,.32):
        beam('Table leg',(x*1.06,y*1.08,.045),(x,y,.735),.075,.075,wood)
for y in (-.32,.32): box('Long table apron',(0,y,.665),(1.57,.035,.13),wood,.007)
for x in (-.76,.76): box('End table apron',(x,0,.665),(.035,.65,.13),wood,.007)

# Chair local front is -Y; rotate each pair to face the tabletop.
def chair(index,center,angle):
    c,s=math.cos(angle),math.sin(angle)
    def point(p):
        x,y,z=p; return (center[0]+c*x-s*y,center[1]+s*x+c*y,z)
    def part(name,loc,size,mat,bevel=.012):
        o=box('Chair %d / '%index+name,point(loc),size,mat,bevel); o.rotation_euler.z=angle; return o
    def rail(name,a,b,w=.043,d=.043):
        return beam('Chair %d / '%index+name,point(a),point(b),w,d,wood)
    part('Seat frame',(0,0,.443),(.46,.46,.065),wood)
    part('Upholstered seat',(0,-.01,.487),(.435,.43,.048),fabric,.02)
    for x in (-.18,.18):
        rail('Front leg',(x*1.13,-.205,.025),(x,-.175,.43),.048,.048)
        rail('Rear leg and back post',(x*1.10,.215,.025),(x,.19,.48),.045,.045)
        rail('Back upright',(x,.19,.43),(x,.265,.96),.045,.045)
        rail('Side stretcher',(x,-.19,.21),(x,.205,.21),.027,.027)
    rail('Front stretcher',(-.19,-.19,.23),(.19,-.19,.23),.026,.026)
    for z in (.66,.79,.92):
        y=.19+(z-.43)*(.075/.53)
        o=part('Backrest slat',(0,y,z),(.36,.034,.085),wood,.009)
        o.rotation_euler=( -math.atan(.075/.53),0,angle)

for i,(x,y,a) in enumerate([(-.49,-.85,math.pi),(.49,-.85,math.pi),(-.49,.85,0),(.49,.85,0)],1):
    chair(i,(x,y),a)
box('Floor',(0,0,-.04),(200,200,.08),floor,0)
world=bpy.data.worlds.new('Studio'); bpy.context.scene.world=world; world.use_nodes=True
world.node_tree.nodes['Background'].inputs[0].default_value=(.7,.76,.82,1)
world.node_tree.nodes['Background'].inputs[1].default_value=.3
for loc,energy,size in [((-3,-4,5),850,4),((2,3,4),650,3)]:
    bpy.ops.object.light_add(type='AREA',location=loc); o=bpy.context.object; o.data.energy=energy; o.data.size=size
    o.rotation_euler=(Vector((0,0,.4))-o.location).to_track_quat('-Z','Y').to_euler()
bpy.ops.object.camera_add(location=(3.2,-4.3,3.1)); cam=bpy.context.object
cam.rotation_euler=(Vector((0,0,.48))-cam.location).to_track_quat('-Z','Y').to_euler()
cam.data.type='ORTHO'; cam.data.ortho_scale=3.75
scene=bpy.context.scene; scene.camera=cam; scene.render.engine='CYCLES'
scene.render.resolution_x=1400; scene.render.resolution_y=1100; scene.render.resolution_percentage=100
