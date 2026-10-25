import bpy, math
from mathutils import Vector
bpy.ops.wm.read_factory_settings(use_empty=True)

def mat(name,c,metal=0,rough=0.45):
    m=bpy.data.materials.new(name); m.diffuse_color=(*c,1); m.use_nodes=True; p=m.node_tree.nodes.get('Principled BSDF'); p.inputs['Base Color'].default_value=(*c,1); p.inputs['Metallic'].default_value=metal; p.inputs['Roughness'].default_value=rough; return m

def box(name,loc,size,m,bevel=0.025):
    bpy.ops.mesh.primitive_cube_add(size=1,location=loc); o=bpy.context.object; o.name=name; o.dimensions=size; bpy.ops.object.transform_apply(location=False,rotation=False,scale=True); o.data.materials.append(m)
    if bevel:
        b=o.modifiers.new('Rounded edges','BEVEL'); b.width=bevel; b.segments=3; o.modifiers.new('Weighted normals','WEIGHTED_NORMAL')
    return o

def rod(name,a,b,r,m,vertices=32):
    d=Vector(b)-Vector(a); bpy.ops.mesh.primitive_cylinder_add(vertices=vertices,radius=r,depth=d.length,location=(Vector(a)+Vector(b))/2); o=bpy.context.object; o.name=name; o.rotation_euler=d.to_track_quat('Z','Y').to_euler(); o.data.materials.append(m)
    for p in o.data.polygons: p.use_smooth=True
    return o

def tube(name,points,r,m):
    cu=bpy.data.curves.new(name,'CURVE'); cu.dimensions='3D'; cu.bevel_depth=r; cu.bevel_resolution=4; s=cu.splines.new('BEZIER'); s.bezier_points.add(len(points)-1)
    for p,co in zip(s.bezier_points,points): p.co=co; p.handle_left_type='AUTO'; p.handle_right_type='AUTO'
    o=bpy.data.objects.new(name,cu); bpy.context.collection.objects.link(o); o.data.materials.append(m); return o

def text(body,loc,size,m):
    cu=bpy.data.curves.new(body,'FONT'); cu.body=body; cu.align_x='CENTER'; cu.align_y='CENTER'; cu.size=size; cu.extrude=0.001
    o=bpy.data.objects.new(body,cu); bpy.context.collection.objects.link(o); o.location=loc; o.rotation_euler=(math.pi/2,0,0); o.data.materials.append(m)

sage=mat('Sage enamel',(0.19,0.34,0.29),0.12); walnut=mat('Walnut',(0.25,0.12,0.06)); chrome=mat('Stainless steel',(0.60,0.65,0.66),0.85,0.23); black=mat('Rubber and handles',(0.025,0.03,0.028),rough=0.70); cream=mat('Porcelain',(0.92,0.86,0.72),rough=0.24); brass=mat('Brass logo',(0.70,0.46,0.16),0.72); coffee=mat('Coffee',(0.065,0.025,0.009),rough=0.32); beanmat=mat('Roasted beans',(0.13,0.055,0.018)); floor=mat('Studio floor',(0.65,0.65,0.59)); screen=mat('Display',(0.035,0.11,0.12),0.2)
box('Floor',(0,0,-0.055),(200,200,0.1),floor,0)
# Four separate casters, each with tire, fork, swivel and hub.
for x in [-0.91,0.91]:
    for y in [-0.41,0.41]:
        rod('Caster swivel',(x,y,0.33),(x,y,0.44),0.061,chrome)
        box('Caster mounting plate',(x,y,0.425),(0.20,0.16,0.025),chrome,0.01)
        rod('Tire',(x,y-0.058,0.17),(x,y+0.058,0.17),0.165,black,40)
        rod('Wheel hub',(x,y-0.065,0.17),(x,y+0.065,0.17),0.073,chrome)
        for side in [-1,1]: box('Caster fork',(x,y+side*0.075,0.26),(0.085,0.025,0.20),chrome,0.012)
        rod('Axle',(x,y-0.098,0.17),(x,y+0.098,0.17),0.025,brass)
box('Chassis',(0,0,0.44),(2.14,1.07,0.13),black)
box('Cart cabinet',(0,0,0.92),(2.08,1.00,0.88),sage,0.055)
box('Walnut counter',(0,0,1.405),(2.30,1.16,0.13),walnut,0.045)
box('Metal work surface',(0,0,1.479),(2.21,1.07,0.025),chrome,0.018)
for x in [-0.98,0.98]: box('Front brass edge',(x,-0.512,0.94),(0.016,0.016,0.75),brass,0.004)
text('DAILY PRESS',(0,-0.517,1.02),0.205,cream)
text('ESPRESSO  /  COFFEE',(0,-0.518,0.78),0.079,cream)
# Right-side service door with ventilation and handle.
box('Service door',(1.047,0,0.92),(0.018,0.82,0.68),sage,0.018)
for i in range(7): box('Vent slot',(1.060,0,0.68+i*0.045),(0.008,0.46,0.013),black,0.005)
rod('Door handle',(1.085,-0.26,1.12),(1.085,-0.06,1.12),0.018,chrome)
for y in [-0.39,0.39]: rod('Push handle mount',(-1.04,y,1.25),(-1.37,y,1.25),0.028,chrome)
rod('Push handle',(-1.37,-0.39,1.25),(-1.37,0.39,1.25),0.038,walnut)
# Espresso machine: stepped body, group heads, drip tray and controls.
box('Espresso machine base',(-0.22,0.12,1.55),(1.12,0.67,0.10),black)
box('Espresso machine',(-0.22,0.28,1.91),(1.08,0.41,0.65),chrome,0.065)
box('Machine top',(-0.22,0.24,2.255),(1.16,0.51,0.065),sage)
box('Control fascia',(-0.22,0.056,2.06),(0.95,0.045,0.19),black)
box('Drip tray',(-0.22,-0.13,1.61),(1.09,0.40,0.055),chrome,0.012)
for i in range(19): box('Drip tray slot',(-0.71+i*0.054,-0.14,1.64),(0.013,0.31,0.007),black,0.004)
for x in [-0.49,0.04]:
    rod('Group head',(x,-0.005,1.86),(x,-0.005,1.97),0.09,chrome)
    rod('Portafilter basket',(x,-0.05,1.81),(x,-0.05,1.86),0.067,chrome)
    rod('Portafilter handle',(x,-0.07,1.835),(x,-0.37,1.835),0.028,black)
    rod('Coffee spout',(x,-0.05,1.78),(x,-0.05,1.81),0.016,chrome)
    for dx in [-0.09,0,0.09]: rod('Brew button',(x+dx,0.026,2.06),(x+dx,0.010,2.06),0.018,cream)
rod('Pressure gauge bezel',(-0.22,0.026,2.16),(-0.22,0.004,2.16),0.045,brass)
rod('Pressure gauge face',(-0.22,0.003,2.16),(-0.22,-0.001,2.16),0.037,cream)
rod('Gauge needle',(-0.22,-0.005,2.16),(-0.239,-0.005,2.18),0.003,black)
tube('Steam wand',[(0.29,0.08,1.98),(0.40,-0.03,1.95),(0.41,-0.20,1.72)],0.012,chrome)
rod('Steam knob',(0.29,0.02,2.12),(0.29,-0.045,2.12),0.04,black)
# Open porcelain cups made as continuous outer/inner radial profiles.
def cup(name,x,y,z):
    profile=[(0.047,0),(0.050,0.018),(0.061,0.11),(0.053,0.11),(0.042,0.02),(0,0.02)]
    verts=[(x+r*math.cos(i*math.tau/32),y+r*math.sin(i*math.tau/32),z+h) for r,h in profile for i in range(32)]
    faces=[(j*32+i,j*32+(i+1)%32,(j+1)*32+(i+1)%32,(j+1)*32+i) for j in range(len(profile)-1) for i in range(32)]
    me=bpy.data.meshes.new(name); me.from_pydata(verts,[],faces); me.update(); o=bpy.data.objects.new(name,me); bpy.context.collection.objects.link(o); o.data.materials.append(cream)
    for p in me.polygons: p.use_smooth=True
    tube('Cup handle',[(x+0.053,y,z+0.085),(x+0.092,y,z+0.086),(x+0.096,y,z+0.04),(x+0.049,y,z+0.03)],0.009,cream)
for x in [-0.49,0.04]:
    rod('Saucer',(x,-0.11,1.646),(x,-0.11,1.66),0.088,cream)
    cup('Espresso cup',x,-0.11,1.661)
for x in [-0.58,-0.30,-0.02]: cup('Warming cup',x,0.23,2.288)
# Compact grinder and a translucent hopper filled with beans.
box('Grinder base',(0.80,0.20,1.53),(0.35,0.39,0.075),black)
box('Grinder motor',(0.80,0.29,1.77),(0.27,0.27,0.43),sage,0.055)
box('Grinder spout',(0.80,0.095,1.87),(0.12,0.16,0.09),chrome)
rod('Hopper collar',(0.80,0.29,1.96),(0.80,0.29,2.05),0.09,black)
glass=mat('Hopper glass',(0.72,0.80,0.76),rough=0.12); glass.node_tree.nodes['Principled BSDF'].inputs['Transmission Weight'].default_value=0.85
bpy.ops.mesh.primitive_cone_add(vertices=40,radius1=0.09,radius2=0.16,depth=0.27,location=(0.80,0.29,2.16)); bpy.context.object.name='Glass bean hopper'; bpy.context.object.data.materials.append(glass)
rod('Beans inside hopper',(0.80,0.29,2.075),(0.80,0.29,2.23),0.115,beanmat)
rod('Hopper lid',(0.80,0.29,2.298),(0.80,0.29,2.326),0.168,black)
box('Menu stand',(-0.91,-0.10,1.68),(0.23,0.05,0.35),walnut)
box('Menu face',(-0.91,-0.132,1.68),(0.205,0.012,0.32),black,0.005)
text('MENU\nESPRESSO\nLATTE\nFILTER',(-0.91,-0.141,1.68),0.034,cream)
world=bpy.data.worlds.new('Studio'); bpy.context.scene.world=world; world.use_nodes=True; world.node_tree.nodes['Background'].inputs[1].default_value=0.45
for loc,power,size in [((-3,-4,6),1000,4),((3,2,5),800,3)]:
    bpy.ops.object.light_add(type='AREA',location=loc); o=bpy.context.object; o.data.energy=power; o.data.size=size; o.rotation_euler=(Vector((0,0,1))-o.location).to_track_quat('-Z','Y').to_euler()
bpy.ops.object.camera_add(location=(4,-6,3.8)); cam=bpy.context.object; cam.rotation_euler=(Vector((0,0,1.15))-cam.location).to_track_quat('-Z','Y').to_euler(); cam.data.type='ORTHO'; cam.data.ortho_scale=4.2
scene=bpy.context.scene; scene.camera=cam; scene.render.engine='CYCLES'; scene.cycles.samples=64; scene.render.resolution_x=1100; scene.render.resolution_y=1100; scene.render.resolution_percentage=100
