import bpy
import math
from mathutils import Vector

bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)

def material(name, color, metallic=0, roughness=0.55):
    m = bpy.data.materials.new(name)
    m.diffuse_color = (*color,1)
    m.use_nodes = True
    bs = m.node_tree.nodes.get('Principled BSDF')
    bs.inputs['Base Color'].default_value = (*color,1)
    bs.inputs['Metallic'].default_value = metallic
    bs.inputs['Roughness'].default_value = roughness
    return m

frame = material('Powder coated sage frame',(0.24,0.38,0.32),0.5,0.3)
concrete = material('Concrete curb',(0.48,0.49,0.43))
wood = material('Cedar table slats',(0.48,0.30,0.15))
soil = material('Potting soil',(0.075,0.043,0.018))
potmat = material('Terracotta pots',(0.57,0.24,0.12))
leafmat = material('Vegetable leaves',(0.17,0.38,0.07))
gravel = material('Fine gravel floor',(0.46,0.42,0.32))
metal = material('Galvanized hardware',(0.47,0.53,0.52),0.8,0.28)
glass = material('Clear greenhouse glazing',(0.84,0.95,0.94),0,0.08)
bs = glass.node_tree.nodes.get('Principled BSDF')
bs.inputs['Transmission Weight'].default_value = 1.0
bs.inputs['IOR'].default_value = 1.45
bs.inputs['Alpha'].default_value = 0.22
glass.diffuse_color = (0.72,0.90,0.88,0.22)
glass.surface_render_method = 'DITHERED'

def box(name, loc, size, mat):
    bpy.ops.mesh.primitive_cube_add(size=1, location=loc)
    o = bpy.context.object
    o.name = name
    o.dimensions = size
    bpy.ops.object.transform_apply(location=False,rotation=False,scale=True)
    o.data.materials.append(mat)
    return o

def beam(name, a, b, width=0.065, mat=frame):
    d = Vector(b)-Vector(a)
    o = box(name,(Vector(a)+Vector(b))/2,(width,width,d.length),mat)
    o.rotation_mode = 'QUATERNION'
    o.rotation_quaternion = d.to_track_quat('Z','Y')
    return o

def pane(name, points):
    mesh = bpy.data.meshes.new(name+' mesh')
    mesh.from_pydata(points,[],[tuple(range(len(points)))])
    mesh.update()
    o = bpy.data.objects.new(name,mesh)
    bpy.context.collection.objects.link(o)
    o.data.materials.append(glass)
    mod = o.modifiers.new('Glass thickness','SOLIDIFY')
    mod.thickness = 0.008
    return o

box('Garden base',(0,0,-0.13),(7,9,0.24),gravel)
box('Greenhouse gravel floor',(0,0,0.01),(4.1,6.1,0.10),gravel)
for x in (-2,2):
    box('Side foundation curb',(x,0,0.12),(0.20,6.2,0.24),concrete)
    for z in (0.26,1.30,2.65):
        beam('Longitudinal wall rail',(x,-3,z),(x,3,z),0.075)
for y in (-3,3):
    box('End foundation curb',(0,y,0.12),(4.2,0.20,0.24),concrete)
    beam('Gable tie',( -2,y,2.65),(2,y,2.65),0.08)
beam('Roof ridge',(0,-3.10,3.8),(0,3.10,3.8),0.10)
# Repeated structural bays and individually glazed wall/roof panels.
for y in (-3,-1.5,0,1.5,3):
    for x in (-2,2):
        beam('Wall upright',(x,y,0.23),(x,y,2.65),0.08)
        beam('Pitched roof rafter',(x,y,2.65),(0,y,3.8),0.08)
for y0 in (-3,-1.5,0,1.5):
    y1 = y0+1.5
    for x in (-2,2):
        for z0,z1 in ((0.29,1.27),(1.34,2.61)):
            pane('Side wall glass',[(x,y0+0.04,z0),(x,y1-0.04,z0),
                                   (x,y1-0.04,z1),(x,y0+0.04,z1)])
        pane('Sloped roof glass',[(x,y0+0.04,2.65),(x,y1-0.04,2.65),
                                 (0,y1-0.04,3.8),(0,y0+0.04,3.8)])
for y in (-3,3):
    pane('Triangular gable glazing',[(-1.94,y,2.69),(1.94,y,2.69),(0,y,3.75)])
    beam('Gable king post',(0,y,2.65),(0,y,3.8))
    for x in (-0.65,0.65):
        beam('End mullion',(x,y,0.25),(x,y,2.65),0.08)
    for x0,x1 in ((-1.95,-0.69),(0.69,1.95)):
        pane('End side glazing',[(x0,y,0.29),(x1,y,0.29),(x1,y,2.60),(x0,y,2.60)])
pane('Rear center glazing',[(-0.61,3,0.29),(0.61,3,0.29),(0.61,3,2.60),(-0.61,3,2.60)])
beam('Door header',(-0.65,-3,2.35),(0.65,-3,2.35),0.085)
pane('Door transom',[(-0.61,-3,2.40),(0.61,-3,2.40),(0.61,-3,2.61),(-0.61,-3,2.61)])
# A slightly open glazed door makes the central aisle welcoming.
door = bpy.data.objects.new('Open hinged entrance door',None)
bpy.context.collection.objects.link(door)
door.location = (-0.61,-3.04,0.27)
for name,a,b in [('Left stile',(0,0,0),(0,0,2.03)),('Right stile',(1.22,0,0),(1.22,0,2.03)),
                 ('Top rail',(0,0,2.03),(1.22,0,2.03)),('Bottom rail',(0,0,0),(1.22,0,0)),
                 ('Door crossbar',(0,0,0.96),(1.22,0,0.96))]:
    o = beam(name,a,b,0.065)
    o.parent = door
p = pane('Door glass',[(0.04,0,0.04),(1.18,0,0.04),(1.18,0,1.99),(0.04,0,1.99)])
p.parent = door
handle = box('Door pull',(1.10,-0.06,1.02),(0.035,0.09,0.20),metal)
handle.parent = door
door.rotation_euler.z = math.radians(-32)
# Two planting benches flank an unobstructed center aisle.
for x in (-1.32,1.32):
    for y in (-1.75,0,1.75):
        for dx in (-0.38,0.38):
            box('Bench leg',(x+dx,y,0.59),(0.07,0.07,1.08),frame)
    for dx in (-0.40,0.40):
        box('Bench support rail',(x+dx,0,1.06),(0.075,4.9,0.13),frame)
    for i in range(6):
        box('Planting table slat',(x-0.40+i*0.16,0,1.16),(0.14,4.9,0.08),wood)
    for j in range(6):
        y = -2.05+j*0.80
        bpy.ops.mesh.primitive_cone_add(vertices=16,radius1=0.17,radius2=0.23,depth=0.30,location=(x,y,1.35))
        bpy.context.object.name = 'Terracotta planting pot'
        bpy.context.object.data.materials.append(potmat)
        bpy.ops.mesh.primitive_torus_add(major_segments=20,minor_segments=6,location=(x,y,1.50),major_radius=0.218,minor_radius=0.022)
        bpy.context.object.name = 'Rolled pot rim'
        bpy.context.object.data.materials.append(potmat)
        bpy.ops.mesh.primitive_cylinder_add(vertices=16,radius=0.205,depth=0.018,location=(x,y,1.488))
        bpy.context.object.name = 'Visible potting soil'
        bpy.context.object.data.materials.append(soil)
        beam('Plant stem',(x,y,1.50),(x,y,1.88),0.025,leafmat)
        for k in range(5):
            a = k*2*math.pi/5+j*0.7
            bpy.ops.mesh.primitive_uv_sphere_add(segments=10,ring_count=6,location=(x+0.12*math.cos(a),y+0.12*math.sin(a),1.72+0.035*(k%2)))
            leaf = bpy.context.object
            leaf.name = 'Broad vegetable leaf'
            leaf.scale = (0.22,0.075,0.035)
            leaf.rotation_euler = (0,-0.40,a)
            leaf.data.materials.append(leafmat)
for y in (-2,-1,0,1,2):
    box('Aisle paving slab',(0,y,0.085),(0.90,0.83,0.07),concrete)
bpy.ops.object.camera_add(location=(8,-11,7))
cam = bpy.context.object
cam.name = 'Greenhouse presentation camera'
cam.rotation_euler = (Vector((0,0,1.5))-cam.location).to_track_quat('-Z','Y').to_euler()
cam.data.type = 'ORTHO'
cam.data.ortho_scale = 10.4
bpy.context.scene.camera = cam
bpy.ops.object.light_add(type='AREA',location=(1,-4,8))
bpy.context.object.data.energy = 1800
bpy.context.object.data.size = 6
bpy.context.scene.world.color = (0.4,0.4,0.4)
