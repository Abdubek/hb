import bpy, math
from mathutils import Vector
bpy.ops.object.select_all(action='SELECT'); bpy.ops.object.delete(use_global=False)

def mat(name,c,metal=0,rough=.45):
    m=bpy.data.materials.new(name); m.diffuse_color=(*c,1); m.use_nodes=True; p=m.node_tree.nodes.get('Principled BSDF'); p.inputs['Base Color'].default_value=(*c,1); p.inputs['Metallic'].default_value=metal; p.inputs['Roughness'].default_value=rough; return m
white=mat('Reflective warm white',(.91,.91,.83),.1,.29); orange=mat('Safety orange',(.98,.20,.025),.1,.3); zinc=mat('Galvanized frame',(.4,.46,.49),.8,.3); dark=mat('Rubber foot caps',(.027,.032,.037),0,.8); asphalt=mat('Road',(.12,.135,.15),0,.95); amber=mat('Amber warning lens',(1,.33,.015),.1,.23)
p=amber.node_tree.nodes.get('Principled BSDF'); p.inputs['Emission Color'].default_value=(1,.16,.003,1); p.inputs['Emission Strength'].default_value=.7

def box(name,loc,dims,m,bevel=0):
    bpy.ops.mesh.primitive_cube_add(size=1,location=loc); o=bpy.context.object; o.name=name; o.dimensions=dims; bpy.ops.object.transform_apply(location=False,rotation=False,scale=True); o.data.materials.append(m)
    if bevel: b=o.modifiers.new('Soft manufactured edges','BEVEL'); b.width=bevel; b.segments=3; o.modifiers.new('Weighted normals','WEIGHTED_NORMAL')
    return o

def rod(name,a,b,r,m,verts=20):
    d=Vector(b)-Vector(a); bpy.ops.mesh.primitive_cylinder_add(vertices=verts,radius=r,depth=d.length,location=(Vector(a)+Vector(b))/2); o=bpy.context.object; o.name=name; o.rotation_euler=d.to_track_quat('Z','Y').to_euler(); o.data.materials.append(m); return o

def beam(name,a,b,w,m):
    d=Vector(b)-Vector(a); o=box(name,(Vector(a)+Vector(b))/2,(w,w,d.length),m,.009); o.rotation_euler=d.to_track_quat('Z','Y').to_euler()
box('Road surface',(0,0,-.10),(9,7,.2),asphalt,.04)
for x in (-1.55,1.55):
    box('Wide stabilizing foot',(x,.13,.105),(.20,1.65,.18),zinc,.018)
    for y in (-.66,.92): box('Rubber end cap',(x,y,.11),(.24,.22,.22),dark,.023)
    box('Upright square tube',(x,0,1.12),(.11,.12,2.08),zinc,.013)
    beam('Rear diagonal brace',(x,.82,.20),(x,.06,1.43),.07,zinc)
    box('Foot gusset',(x,.04,.23),(.19,.32,.10),zinc,.01)
    for z in (.51,1.16,1.82):
        box('Slat attachment bracket',(x,-.04,z),(.22,.1,.23),zinc,.01)
# Stripe polygons are clipped to each slat rectangle, avoiding overhanging ends.
def clip(poly,axis,limit,keep_above):
    out=[]
    for i,a in enumerate(poly):
        b=poly[(i+1)%len(poly)]; ia=(a[axis]>=limit) if keep_above else (a[axis]<=limit); ib=(b[axis]>=limit) if keep_above else (b[axis]<=limit)
        if ia: out.append(a)
        if ia!=ib:
            t=(limit-a[axis])/(b[axis]-a[axis]); out.append((a[0]+t*(b[0]-a[0]),a[1]+t*(b[1]-a[1])))
    return out
for z in (.51,1.16,1.82):
    width,height=3.9,.36
    box('Striped reflective slat',(0,-.125,z),(width,.09,height),white,.012)
    for k in range(-7,8):
        a=k*.60; poly=[(a,-height/2),(a+.30,-height/2),(a+.30+height,height/2),(a+height,height/2)]
        poly=clip(poly,0,-width/2,True)
        if poly: poly=clip(poly,0,width/2,False)
        if len(poly)>=3:
            for y in (-.171,-.079):
                mesh=bpy.data.meshes.new('Clipped diagonal stripe'); mesh.from_pydata([(x,y,z+zz) for x,zz in poly],[],[tuple(range(len(poly)))]); mesh.update(); o=bpy.data.objects.new('Orange diagonal reflective band',mesh); bpy.context.collection.objects.link(o); o.data.materials.append(orange)
    for x in (-1.55,1.55):
        for zz in (z-.105,z+.105):
            rod('Bolt washer',(x,-.173,zz),(x,-.183,zz),.030,zinc)
            rod('Hex bolt',(x,-.185,zz),(x,-.201,zz),.021,zinc,6)
# Small battery warning lamp mounted above the right upright.
box('Warning lamp battery housing',(1.55,0,2.23),(.30,.25,.31),orange,.045)
rod('Lens black bezel',(1.55,-.12,2.48),(1.55,-.23,2.48),.175,dark,48)
rod('Amber circular lens',(1.55,-.23,2.48),(1.55,-.258,2.48),.146,amber,48)
for r in (.065,.103,.136):
    bpy.ops.mesh.primitive_torus_add(major_radius=r,minor_radius=.005,major_segments=48,minor_segments=8,location=(1.55,-.26,2.48),rotation=(math.pi/2,0,0)); bpy.context.object.name='Concentric lens prism'; bpy.context.object.data.materials.append(amber)
box('Ground lane dash',(-2.8,-1.6,.007),(.13,1.5,.014),white)
for loc,power,size in [((1,-5,7),1100,5),((-4,2,5),850,4)]:
    bpy.ops.object.light_add(type='AREA',location=loc); o=bpy.context.object; o.data.energy=power; o.data.size=size; o.rotation_euler=(Vector((0,0,1))-o.location).to_track_quat('-Z','Y').to_euler()
bpy.ops.object.camera_add(location=(5,-8,4)); cam=bpy.context.object; cam.rotation_euler=(Vector((0,0,1.2))-cam.location).to_track_quat('-Z','Y').to_euler(); cam.data.type='ORTHO'; cam.data.ortho_scale=5.7
s=bpy.context.scene; s.camera=cam; s.world.color=(.22,.22,.22); s.render.engine='CYCLES'; s.render.resolution_x=1400; s.render.resolution_y=1000; s.render.resolution_percentage=100
