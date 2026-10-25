import bpy, math, random
from mathutils import Vector
random.seed(61)
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)

def material(name, color, roughness=0.5, metallic=0.0):
    m=bpy.data.materials.new(name); m.diffuse_color=(*color,1); m.use_nodes=True
    p=m.node_tree.nodes.get('Principled BSDF'); p.inputs['Base Color'].default_value=(*color,1)
    p.inputs['Roughness'].default_value=roughness; p.inputs['Metallic'].default_value=metallic
    return m

def box(name, loc, size, mat, bevel=0.025):
    bpy.ops.mesh.primitive_cube_add(size=1, location=loc); o=bpy.context.object; o.name=name
    o.dimensions=size; bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    o.data.materials.append(mat)
    if bevel:
        mod=o.modifiers.new('Soft edges','BEVEL'); mod.width=bevel; mod.segments=3
        o.modifiers.new('Weighted normals','WEIGHTED_NORMAL')
    return o

def cylinder(name, a, b, radius, mat, vertices=24):
    a,b=Vector(a),Vector(b); d=b-a
    bpy.ops.mesh.primitive_cylinder_add(vertices=vertices, radius=radius, depth=d.length, location=(a+b)/2)
    o=bpy.context.object; o.name=name; o.rotation_euler=d.to_track_quat('Z','Y').to_euler(); o.data.materials.append(mat)
    mod=o.modifiers.new('Edge bevel','BEVEL'); mod.width=0.007; mod.segments=2
    o.modifiers.new('Weighted normals','WEIGHTED_NORMAL'); return o

def area(name, loc, energy, color, size, target):
    bpy.ops.object.light_add(type='AREA', location=loc); o=bpy.context.object; o.name=name
    o.data.energy=energy; o.data.color=color; o.data.shape='DISK'; o.data.size=size
    o.rotation_euler=(Vector(target)-o.location).to_track_quat('-Z','Y').to_euler()

stone=material('Warm limestone',(0.57,0.51,0.41),0.82)
trim=material('Honed limestone',(0.76,0.69,0.57),0.65)
brick=material('Soot darkened firebrick',(0.19,0.105,0.065),0.95)
mortar=material('Mortar shadow',(0.065,0.052,0.043),0.95)
iron=material('Blackened wrought iron',(0.035,0.041,0.044),0.4,0.7)
wall=material('Plaster',(0.69,0.65,0.57),0.95)
floor=material('Floor stone',(0.29,0.27,0.235),0.85)
bark=material('Rough bark',(0.13,0.062,0.024),0.95)
wood=material('Cut end grain',(0.56,0.32,0.13),0.87)
ring=material('Growth rings',(0.29,0.14,0.055),0.9)
# Procedural mineral grain and bark relief, entirely internal to the file.
for m,scale,strength in [(stone,24,0.16),(brick,35,0.2),(bark,13,0.5)]:
    nt=m.node_tree; p=nt.nodes.get('Principled BSDF'); n=nt.nodes.new('ShaderNodeTexNoise')
    n.inputs['Scale'].default_value=scale; n.inputs['Detail'].default_value=3
    bump=nt.nodes.new('ShaderNodeBump'); bump.inputs['Strength'].default_value=strength; bump.inputs['Distance'].default_value=0.055
    nt.links.new(n.outputs['Fac'],bump.inputs['Height']); nt.links.new(bump.outputs['Normal'],p.inputs['Normal'])
box('Room floor',(0,0,-0.10),(200,200,0.2),floor)
box('Chimney breast',(0,0.70,2.35),(4.3,0.38,4.7),wall)
box('Hearth bottom plinth',(0,-0.34,0.11),(3.6,1.85,0.22),stone,0.04)
box('Overhanging hearth slab',(0,-0.40,0.265),(3.8,2.0,0.13),trim,0.035)
box('Firebox back mortar',(0,0.465,1.13),(2.12,0.10,1.62),mortar,0)
for row in range(7):
    z=0.43+row*0.225
    for col in range(6):
        x=-1.08+col*0.43+(0.215 if row%2 else 0)
        left=max(-1.055,x); right=min(1.055,x+0.412)
        if right>left:
            box('Back firebrick',((left+right)/2,0.39,z),(right-left,0.10,0.205),brick,0.007)
for side in [-1,1]:
    box('Inner firebox cheek',(side*1.065,0.05,1.13),(0.10,0.80,1.61),brick,0.008)
    box('Pier footing',(side*1.35,-0.20,0.43),(0.67,0.92,0.20),trim)
    for row in range(5):
        box('Dressed stone jamb',(side*1.35,-0.12,0.68+row*0.27),(0.55,0.72,0.255),stone,0.012)
    box('Pier capital',(side*1.35,-0.15,1.95),(0.68,0.83,0.16),trim)
box('Stone lintel',(0,-0.12,2.14),(3.27,0.78,0.26),stone,0.022)
box('Mantel lower molding',(0,-0.15,2.32),(3.48,0.89,0.12),trim)
box('Mantel shelf',(0,-0.21,2.45),(3.77,1.04,0.16),trim,0.035)
box('Firebox floor',(0,-0.02,0.355),(2.13,1.05,0.055),iron,0.008)
# Raised grate and turned-up front retaining bars.
for x in [-0.77,0.77]:
    for y in [-0.43,0.25]:
        cylinder('Grate foot',(x,y,0.38),(x,y,0.56),0.026,iron)
for y in [-0.43,0.27]:
    cylinder('Grate cross rail',(-0.90,y,0.56),(0.90,y,0.56),0.027,iron)
for i in range(9):
    x=-0.83+i*0.2075
    cylinder('Grate slat',(x,-0.43,0.56),(x,0.29,0.56),0.022,iron)
    cylinder('Grate front tooth',(x,-0.43,0.55),(x,-0.49,0.79),0.019,iron)
# Logs run into the firebox, exposing detailed end grain toward the viewer.
for i,(x,z,r) in enumerate([(-0.55,0.73,0.16),(-0.19,0.73,0.17),(0.19,0.73,0.17),(0.55,0.73,0.15),(-0.36,1.00,0.17),(0.02,1.02,0.18),(0.39,0.99,0.16),(-0.16,1.28,0.16),(0.20,1.27,0.15)]):
    front=-0.40+random.uniform(-0.04,0.03); end=0.30+random.uniform(-0.05,0.02)
    cylinder('Stacked split firewood', (x,front,z),(x,end,z),r,bark,14)
    cylinder('Exposed cut end',(x,front-0.009,z),(x,front-0.016,z),r*0.90,wood,24)
    for fraction in [0.30,0.55,0.78]:
        bpy.ops.mesh.primitive_torus_add(major_radius=r*fraction,minor_radius=0.0025,major_segments=32,minor_segments=6,location=(x,front-0.021,z),rotation=(math.pi/2,0,0))
        bpy.context.object.name='Annual growth ring'; bpy.context.object.data.materials.append(ring)
    for j in range(7):
        a=j*math.tau/7+0.1*i
        xx=x+math.cos(a)*r*0.96; zz=z+math.sin(a)*r*0.96
        cylinder('Bark ridge',(xx,front+0.02,zz),(xx,end-0.02,zz),0.009,bark,8)
# Small companion tool stand on the hearth.
box('Tool stand base',(1.48,-0.83,0.37),(0.24,0.27,0.06),iron)
cylinder('Tool stand mast',(1.48,-0.83,0.4),(1.48,-0.83,1.27),0.022,iron)
cylinder('Tool stand hook rail',(1.32,-0.83,1.24),(1.64,-0.83,1.24),0.018,iron)
for x in [1.34,1.61]:
    cylinder('Fire tool shaft',(x,-0.84,0.49),(x,-0.84,1.30),0.012,iron)
    cylinder('Tool handle',(x,-0.84,1.19),(x,-0.84,1.32),0.025,iron)
box('Ash shovel blade',(1.61,-0.84,0.52),(0.13,0.035,0.17),iron,0.012)
cylinder('Poker tip',(1.34,-0.84,0.5),(1.25,-0.84,0.46),0.013,iron)
area('Large warm window',(-3,-4,6),950,(1.0,0.85,0.67),4,(0,0,1.3))
area('Soft fill',(4,-1,4),600,(0.76,0.84,1.0),3,(0,0,1.4))
scene=bpy.context.scene; scene.world.color=(0.22,0.22,0.22)
bpy.ops.object.camera_add(location=(5.2,-7.5,4.2)); camera=bpy.context.object
camera.rotation_euler=(Vector((0,-0.1,1.4))-camera.location).to_track_quat('-Z','Y').to_euler()
camera.data.type='ORTHO'; camera.data.ortho_scale=5.7; scene.camera=camera
scene.render.engine='CYCLES'; scene.cycles.samples=48
scene.render.resolution_x=1400; scene.render.resolution_y=1400; scene.render.resolution_percentage=100
scene.view_settings.view_transform='AgX'
