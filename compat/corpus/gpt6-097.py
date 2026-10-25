import bpy, math
from mathutils import Vector

bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)

def mat(name,c,metal=0,rough=0.4):
    m=bpy.data.materials.new(name); m.diffuse_color=(*c,1); m.use_nodes=True
    p=m.node_tree.nodes.get('Principled BSDF')
    p.inputs['Base Color'].default_value=(*c,1); p.inputs['Metallic'].default_value=metal; p.inputs['Roughness'].default_value=rough
    return m

def box(name,loc,dim,m,b=0.02,parent=None):
    bpy.ops.mesh.primitive_cube_add(size=1,location=loc)
    o=bpy.context.object; o.name=name; o.dimensions=dim
    bpy.ops.object.transform_apply(location=False,rotation=False,scale=True)
    o.data.materials.append(m)
    if b:
        mod=o.modifiers.new('Rounded edges','BEVEL'); mod.width=b; mod.segments=3
        o.modifiers.new('Weighted normals','WEIGHTED_NORMAL')
    if parent: o.parent=parent
    return o

def cyl(name,loc,r,d,m,parent=None):
    bpy.ops.mesh.primitive_cylinder_add(vertices=40,radius=r,depth=d,location=loc)
    o=bpy.context.object; o.name=name; o.data.materials.append(m)
    mod=o.modifiers.new('Rounded rim','BEVEL'); mod.width=min(0.012,d/6); mod.segments=3
    o.modifiers.new('Weighted normals','WEIGHTED_NORMAL')
    for p in o.data.polygons: p.use_smooth=True
    if parent: o.parent=parent
    return o

def label(body,loc,size,m,parent=None):
    bpy.ops.object.text_add(location=loc,rotation=(math.pi/2,0,0))
    o=bpy.context.object; o.name=body; o.data.body=body; o.data.align_x='CENTER'; o.data.size=size; o.data.extrude=0.0004; o.data.materials.append(m)
    if parent: o.parent=parent
    return o

shell=mat('Satin seafoam enamel',(0.30,0.53,0.51),0.3,0.28)
liner=mat('Ivory interior plastic',(0.91,0.94,0.88),0,0.3)
steel=mat('Brushed aluminium',(0.58,0.64,0.66),0.8,0.25)
dark=mat('Dark seals',(0.04,0.065,0.065),0,0.6)
clear=mat('Pale blue shelf glass',(0.64,0.85,0.89),0,0.13)
p=clear.node_tree.nodes.get('Principled BSDF'); p.inputs['Transmission Weight'].default_value=0.65; p.inputs['IOR'].default_value=1.46
red=mat('Tomato red',(0.65,0.045,0.025),0,0.35)
green=mat('Produce green',(0.22,0.40,0.055),0,0.45)
cream=mat('Milk carton',(0.90,0.83,0.61),0,0.6)
blue=mat('Milk label',(0.06,0.28,0.45),0,0.5)
amber=mat('Jar contents',(0.7,0.32,0.06),0,0.28)
ground=mat('Floor',(0.23,0.26,0.28),0,0.8)
lamp=mat('Interior diffuser',(0.85,0.97,1.0),0,0.25)
p=lamp.node_tree.nodes.get('Principled BSDF'); p.inputs['Emission Color'].default_value=(0.72,0.89,1,1); p.inputs['Emission Strength'].default_value=2

# Open-front insulated cabinet built from separate walls.
for x in (-0.51,0.51):
    for y in (-0.36,0.36): cyl('Levelling foot',(x,y,0.075),0.055,0.15,dark)
box('Left insulated wall',(-0.59,0,1.23),(0.14,1.02,2.24),shell,0.045)
box('Right insulated wall',(0.59,0,1.23),(0.14,1.02,2.24),shell,0.045)
box('Cabinet back',(0,0.46,1.23),(1.08,0.13,2.24),shell,0.035)
box('Top insulation',(0,0,2.31),(1.22,1.02,0.15),shell,0.04)
box('Bottom insulation',(0,0,0.18),(1.22,1.02,0.14),shell,0.03)
box('Interior back liner',(0,0.382,1.26),(1.05,0.03,2.04),liner,0.018)
for x in (-0.513,0.513): box('Inner side liner',(x,-0.025,1.25),(0.025,0.84,2.02),liner,0.012)
box('Ceiling liner',(0,-0.035,2.221),(1.04,0.84,0.03),liner,0.012)
box('Interior floor',(0,-0.02,0.266),(1.04,0.85,0.045),liner,0.01)
box('Toe ventilation panel',(0,-0.518,0.17),(1.07,0.02,0.10),dark,0.01)
for i in range(16): box('Toe grille',(i*0.061-0.458,-0.535,0.17),(0.013,0.013,0.073),steel,0.003)
for z in (0.75,1.17,1.59,1.97):
    box('Glass shelf',(0,-0.02,z),(0.985,0.78,0.022),clear,0.009)
    box('Shelf front edging',(0,-0.405,z),(1.0,0.025,0.032),steel,0.006)
    for x in (-0.486,0.486): box('Shelf support',(x,0.00,z-0.027),(0.035,0.71,0.025),liner,0.005)
# Crisper is a genuine open container, not a solid block.
box('Crisper base',(0,-0.03,0.33),(0.94,0.72,0.035),clear,0.012)
box('Crisper front',(0,-0.398,0.49),(0.94,0.025,0.32),clear,0.012)
box('Crisper back',(0,0.327,0.49),(0.94,0.025,0.32),clear,0.012)
for x in (-0.46,0.46): box('Crisper side',(x,-0.03,0.49),(0.025,0.73,0.32),clear,0.009)
box('Crisper handle',(0,-0.425,0.60),(0.38,0.045,0.035),liner,0.012)
for i in range(5):
    bpy.ops.mesh.primitive_uv_sphere_add(segments=24,ring_count=12,radius=0.10,location=(-0.32+i*0.15,-0.11+(i%2)*0.21,0.43))
    o=bpy.context.object; o.name='Fresh produce'; o.data.materials.append(green if i%2 else red)
    for p in o.data.polygons: p.use_smooth=True
for x in (-0.30,-0.05):
    box('Milk carton',(x,0.04,0.94),(0.18,0.21,0.35),cream,0.009)
    box('Blue carton label',(x,-0.071,0.94),(0.16,0.004,0.16),blue,0.001)
    label('MILK',(x,-0.075,0.943),0.033,liner)
    cyl('Carton cap',(x,0.04,1.127),0.029,0.024,blue)
for x in (0.16,0.35):
    cyl('Preserve jar',(x,0.12,1.29),0.075,0.21,amber)
    cyl('Jar lid',(x,0.12,1.405),0.08,0.026,steel)
box('Covered food box',(-0.19,0.06,1.68),(0.42,0.39,0.15),liner,0.025)
box('Food box lid',(-0.19,0.06,1.763),(0.44,0.41,0.027),blue,0.012)
box('Interior light',(0,-0.1,2.196),(0.38,0.23,0.015),lamp,0.012)
for i in range(9): box('Cooling vent',(-0.24+i*0.06,0.363,2.07),(0.025,0.007,0.09),dark,0.004)

# Coordinates below are local to the left door hinge.
pivot=bpy.data.objects.new('Door hinge - open 108 degrees',None)
bpy.context.collection.objects.link(pivot)
pivot.location=(-0.615,-0.53,0)
pivot.rotation_euler.z=math.radians(-108)
box('Open insulated door',(0.615,-0.045,1.255),(1.24,0.13,2.25),shell,0.05,pivot)
box('Door inner liner',(0.615,0.035,1.255),(1.11,0.045,2.08),liner,0.03,pivot)
for x in (0.065,1.165): box('Vertical magnetic gasket',(x,0.067,1.255),(0.026,0.019,2.10),dark,0.008,pivot)
for z in (0.21,2.30): box('Horizontal magnetic gasket',(0.615,0.067,z),(1.12,0.019,0.026),dark,0.007,pivot)
for z in (0.48,1.02,1.57):
    box('Door bin base',(0.615,0.18,z),(0.99,0.25,0.035),liner,0.012,pivot)
    box('Door bin retaining rail',(0.615,0.302,z+0.13),(0.99,0.027,0.19),clear,0.015,pivot)
    for x in (0.13,1.1): box('Door bin end',(x,0.18,z+0.10),(0.026,0.25,0.20),liner,0.012,pivot)
for x in (0.39,0.63,0.87):
    cyl('Door bottle',(x,0.18,0.68),0.074,0.35,green,pivot)
    cyl('Bottle shoulder',(x,0.18,0.86),0.052,0.05,green,pivot)
    cyl('Bottle neck',(x,0.18,0.915),0.028,0.07,green,pivot)
    cyl('Bottle cap',(x,0.18,0.954),0.032,0.025,cream,pivot)
for z in (0.94,1.69): box('Exterior handle mount',(1.06,-0.142,z),(0.055,0.095,0.065),steel,0.018,pivot)
box('Exterior vertical handle',(1.06,-0.196,1.315),(0.049,0.055,0.81),steel,0.022,pivot)
for z in (0.24,2.22): cyl('Hinge pin',(-0.615,-0.53,z),0.03,0.13,steel)
box('Floor',(0,0,-0.04),(200,200,0.06),ground,0)

world=bpy.context.scene.world; world.use_nodes=True
world.node_tree.nodes['Background'].inputs[0].default_value=(0.21,0.24,0.29,1)
world.node_tree.nodes['Background'].inputs[1].default_value=0.5
for loc,power,size in [((1,-4,6),950,4),((-4,-2,3),700,3),((3,3,5),1100,3)]:
    bpy.ops.object.light_add(type='AREA',location=loc)
    o=bpy.context.object; o.data.energy=power; o.data.size=size
    o.rotation_euler=(Vector((0,0,1.1))-o.location).to_track_quat('-Z','Y').to_euler()
bpy.ops.object.light_add(type='AREA',location=(0,-0.05,2.15))
o=bpy.context.object; o.name='Interior lamp'; o.data.energy=12; o.data.size=0.35
bpy.ops.object.camera_add(location=(4,-7,3.9))
cam=bpy.context.object; cam.rotation_euler=(Vector((-0.35,-0.28,1.18))-cam.location).to_track_quat('-Z','Y').to_euler()
cam.data.type='ORTHO'; cam.data.ortho_scale=3.7
scene=bpy.context.scene; scene.camera=cam; scene.render.engine='CYCLES'; scene.cycles.samples=64
scene.render.resolution_x=1200; scene.render.resolution_y=1200; scene.render.resolution_percentage=100
