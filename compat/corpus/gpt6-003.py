import bpy, math
from mathutils import Vector
bpy.ops.wm.read_factory_settings(use_empty=True)

def mat(name,c,metal=0,rough=.45):
    m=bpy.data.materials.new(name); m.diffuse_color=(*c,1); m.use_nodes=True
    p=m.node_tree.nodes.get('Principled BSDF'); p.inputs['Base Color'].default_value=(*c,1)
    p.inputs['Metallic'].default_value=metal; p.inputs['Roughness'].default_value=rough
    return m
shell=mat('Ivory ceramic armor',(.67,.69,.62),.35)
metal=mat('Dark titanium',(.14,.17,.19),.8)
rubber=mat('Graphite tires',(.028,.035,.041),0,.8)
orange=mat('Safety orange',(.9,.20,.025),.25)
blue=mat('Sensor glass',(.018,.10,.17),.7,.15)
solar=mat('Solar cells',(.025,.07,.16),.5,.22)
sand=mat('Ochre terrain',(.34,.24,.15),0,.95)

def box(name,loc,size,ma,bevel=.025):
    bpy.ops.mesh.primitive_cube_add(size=1,location=loc); o=bpy.context.object; o.name=name; o.dimensions=size
    bpy.ops.object.transform_apply(location=False,rotation=False,scale=True); o.data.materials.append(ma)
    if bevel:
        b=o.modifiers.new('Edge radii','BEVEL'); b.width=bevel; b.segments=3
        o.modifiers.new('Weighted normals','WEIGHTED_NORMAL')
    return o

def cylinder(name,loc,radius,depth,ma,axis=(0,0,1),vertices=48):
    bpy.ops.mesh.primitive_cylinder_add(vertices=vertices,radius=radius,depth=depth,location=loc)
    o=bpy.context.object; o.name=name; o.rotation_euler=Vector(axis).to_track_quat('Z','Y').to_euler(); o.data.materials.append(ma)
    b=o.modifiers.new('Machined edges','BEVEL'); b.width=.008; b.segments=2
    o.modifiers.new('Weighted normals','WEIGHTED_NORMAL'); return o

def rod(name,a,b,r,ma):
    a,b=Vector(a),Vector(b); return cylinder(name,(a+b)/2,r,(b-a).length,ma,b-a,24)

# Longitudinal direction is X, with the rover front at +X.
box('Lower chassis',(0,0,.76),(1.95,.97,.27),metal,.08)
box('Upper armor',(0,0,.985),(1.84,1.05,.23),shell,.085)
box('Front bumper',(1.05,0,.75),(.12,1.08,.12),orange)
box('Rear bumper',(-1.05,0,.75),(.12,1.08,.12),metal)
for side in (-1,1):
    y=side*.76
    # Visible articulated suspension arms and six complete wheels.
    for x in (-.82,0,.82):
        rod('Suspension wishbone',(x*.8,side*.44,.79),(x,y,.39),.043,metal)
        rod('Axle',(x,side*.46,.37),(x,y,.37),.06,metal)
        cylinder('Tire',(x,y,.37),.345,.25,rubber,(0,1,0),64)
        cylinder('Wheel rim',(x,y+side*.132,.37),.231,.027,shell,(0,1,0))
        cylinder('Hub',(x,y+side*.16,.37),.095,.075,orange,(0,1,0))
        for k in range(24):
            t=2*math.pi*k/24
            o=box('Tread cleat',(x+.342*math.sin(t),y,.37+.342*math.cos(t)),(.058,.267,.028),rubber,.006)
            o.rotation_euler.y=t
        for k in range(6):
            t=2*math.pi*k/6
            cylinder('Rim bolt',(x+.155*math.sin(t),y+side*.155,.37+.155*math.cos(t)),.019,.019,metal,(0,1,0),12)
    rod('Suspension rocker',(-.82,side*.59,.57),(0,side*.59,.73),.035,metal)
    rod('Suspension bogie',(0,side*.59,.73),(.82,side*.59,.57),.035,metal)
    box('Side equipment panel',(-.2,side*.538,.965),(.8,.026,.14),orange,.014)
    for i in range(8): box('Cooling slot',(-.51+i*.087,side*.556,.965),(.038,.012,.075),metal,.005)

box('Solar panel frame',(-.32,0,1.14),(1.04,.92,.065),metal,.014)
for i in range(5):
    for j in range(4): box('Photovoltaic cell',(-.73+i*.205,-.337+j*.225,1.177),(.191,.208,.009),solar,.003)
cylinder('Mast turntable',(.59,0,1.145),.16,.1,metal)
rod('Sensor mast',(.59,0,1.19),(.59,0,1.92),.055,shell)
cylinder('Mast collar',(.59,0,1.56),.075,.09,orange)
box('Stereo sensor head',(.62,0,1.94),(.24,.58,.22),shell,.055)
for y in (-.185,.185):
    cylinder('Camera housing',(.76,y,1.95),.082,.085,metal,(1,0,0))
    cylinder('Camera lens',(.806,y,1.95),.06,.009,blue,(1,0,0))
cylinder('Lidar base',(.6,0,2.09),.10,.06,metal)
cylinder('Lidar optical band',(.6,0,2.145),.087,.06,blue)
cylinder('Lidar cap',(.6,0,2.185),.102,.025,shell)
rod('Radio antenna',(-.84,.34,1.1),(-.84,.34,1.77),.013,metal)
for y in (-.34,.34):
    cylinder('Front inspection lamp',(1.0,y,1.0),.064,.045,blue,(1,0,0))
box('Terrain',(0,0,-.035),(200,200,.07),sand,0)
world=bpy.data.worlds.new('World'); bpy.context.scene.world=world; world.use_nodes=True
world.node_tree.nodes['Background'].inputs[1].default_value=.3
for loc,power,size in [((3,-4,6),1100,4),((-3,2,4),800,3)]:
    bpy.ops.object.light_add(type='AREA',location=loc); o=bpy.context.object; o.data.energy=power; o.data.size=size
    o.rotation_euler=(Vector((0,0,.8))-o.location).to_track_quat('-Z','Y').to_euler()
bpy.ops.object.camera_add(location=(3.8,-4.8,3.05)); cam=bpy.context.object
cam.rotation_euler=(Vector((0,0,1))-cam.location).to_track_quat('-Z','Y').to_euler()
cam.data.type='ORTHO'; cam.data.ortho_scale=3.6
scene=bpy.context.scene; scene.camera=cam; scene.render.engine='CYCLES'
scene.render.resolution_x=1400; scene.render.resolution_y=1100; scene.render.resolution_percentage=100
