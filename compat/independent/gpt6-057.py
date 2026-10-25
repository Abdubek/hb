import bpy
import math
import random
from mathutils import Vector

bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)
random.seed(57)

def material(name, color, metallic=0.0):
    m = bpy.data.materials.new(name)
    m.diffuse_color = (*color, 1)
    m.use_nodes = True
    bs = m.node_tree.nodes.get('Principled BSDF')
    bs.inputs['Base Color'].default_value = (*color, 1)
    bs.inputs['Metallic'].default_value = metallic
    bs.inputs['Roughness'].default_value = 0.48
    return m

wood = material('Honey colored timber', (0.43, 0.23, 0.09))
cratewood = material('Fresh crate wood', (0.64, 0.43, 0.22))
metal = material('Dark steel hardware', (0.11, 0.14, 0.13), 0.65)
cream = material('Canvas cream', (0.95, 0.87, 0.64))
green = material('Canvas forest green', (0.08, 0.32, 0.18))
red = material('Red tomatoes', (0.75, 0.055, 0.025))
apple = material('Green apples', (0.39, 0.64, 0.06))
orange = material('Oranges', (1.0, 0.34, 0.015))
chalk = material('Chalkboard', (0.025, 0.07, 0.055))
paving = material('Warm pavement', (0.32, 0.30, 0.26))

def box(name, loc, size, mat, bevel=0.0):
    bpy.ops.mesh.primitive_cube_add(size=1, location=loc)
    o = bpy.context.object
    o.name = name
    o.dimensions = size
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    o.data.materials.append(mat)
    if bevel:
        mod = o.modifiers.new('Soft edges', 'BEVEL')
        mod.width = bevel
        mod.segments = 2
        o.modifiers.new('Corner normals', 'WEIGHTED_NORMAL')
    return o

def label(name, body, loc, size, mat):
    curve = bpy.data.curves.new(name, 'FONT')
    curve.body = body
    curve.align_x = 'CENTER'
    curve.align_y = 'CENTER'
    curve.size = size
    curve.extrude = 0.001
    o = bpy.data.objects.new(name, curve)
    bpy.context.collection.objects.link(o)
    o.location = loc
    o.rotation_euler = (math.pi / 2, 0, 0)
    o.data.materials.append(mat)
    return o

box('Pavement display base', (0, 0, -0.10), (5.4, 4.2, 0.20), paving, 0.06)
for x in (-1.75, 1.75):
    for y in (-0.87, 0.87):
        box('Canopy upright', (x, y, 1.43), (0.10, 0.10, 2.86), wood, 0.012)
        box('Steel post foot', (x, y, 0.07), (0.18, 0.18, 0.14), metal, 0.015)
box('Rear canopy rail', (0, 0.87, 2.74), (3.62, 0.09, 0.12), wood)
box('Front canopy rail', (0, -0.87, 2.74), (3.62, 0.09, 0.12), wood)
box('Roof ridge', (0, 0, 3.24), (3.85, 0.08, 0.08), wood)
for i in range(12):
    x0 = -2.04 + i * 0.34
    x1 = x0 + 0.34
    verts = [(x0,-1.15,2.78),(x1,-1.15,2.78),(x1,0,3.29),(x0,0,3.29),
             (x0,1.15,2.78),(x1,1.15,2.78)]
    mesh = bpy.data.meshes.new('Canvas stripe mesh')
    mesh.from_pydata(verts, [], [(0,1,2,3),(3,2,5,4)])
    mesh.update()
    roof = bpy.data.objects.new('Canopy stripe %02d' % i, mesh)
    bpy.context.collection.objects.link(roof)
    mat = cream if i % 2 == 0 else green
    roof.data.materials.append(mat)
    roof.modifiers.new('Canvas thickness', 'SOLIDIFY').thickness = 0.012
    for y in (-1.15, 1.15):
        box('Striped hanging valance', ((x0+x1)/2,y,2.66), (0.34,0.025,0.24), mat)

box('Countertop', (0, 0, 1.03), (3.65, 1.65, 0.13), wood, 0.025)
for x in (-1.5, 1.5):
    for y in (-0.62, 0.62):
        box('Counter leg', (x,y,0.48), (0.12,0.12,0.96), wood)
box('Lower storage shelf', (0,0.1,0.28), (3.25,1.30,0.09), wood)
for i in range(12):
    box('Counter front board', (-1.65+i*0.30,-0.73,0.66), (0.28,0.055,0.62), cratewood, 0.008)

def crate(name, x, y, z, produce=None):
    box(name+' floor', (x,y,z+0.035), (0.96,0.94,0.07), cratewood)
    for dx in (-0.44,0.44):
        for dy in (-0.43,0.43):
            box(name+' corner block', (x+dx,y+dy,z+0.22), (0.07,0.07,0.44), wood)
    for h in (0.13,0.29):
        for dy in (-0.46,0.46):
            box(name+' long slat', (x,y+dy,z+h), (0.96,0.045,0.12), cratewood, 0.006)
        for dx in (-0.46,0.46):
            box(name+' end slat', (x+dx,y,z+h), (0.045,0.92,0.12), cratewood, 0.006)
    if produce:
        for row in range(3):
            for col in range(3):
                p = (x+(col-1)*0.265+random.uniform(-0.025,0.025), y+(row-1)*0.265, z+0.24+random.uniform(0,0.035))
                bpy.ops.mesh.primitive_uv_sphere_add(segments=12, ring_count=8, radius=0.14, location=p)
                o = bpy.context.object
                o.name = name+' fruit'
                o.scale.z = 0.9
                o.data.materials.append(produce)
                for face in o.data.polygons:
                    face.use_smooth = True
                box(name+' fruit stem', (p[0],p[1],p[2]+0.13), (0.018,0.018,0.05), green)

for x, name, mat in [(-1.13,'Tomatoes',red),(0,'Apples',apple),(1.13,'Oranges',orange)]:
    crate(name, x, 0, 1.095, mat)
    box(name+' price board', (x,-0.80,1.02), (0.64,0.035,0.22), chalk, 0.01)
    label(name+' price', name.upper()+'  $3', (x,-0.823,1.02), 0.075, cream)
crate('Spare crate', -0.9, 0.12, 0.325)
box('Market sign frame', (0,-0.92,2.28), (1.86,0.10,0.37), wood, 0.02)
box('Market sign face', (0,-0.978,2.28), (1.74,0.025,0.27), chalk)
label('Market lettering', 'FARM FRESH', (0,-0.997,2.28), 0.20, cream)

world = bpy.context.scene.world or bpy.data.worlds.new('Market world')
bpy.context.scene.world = world
world.use_nodes = True
world.node_tree.nodes['Background'].inputs[0].default_value = (0.65,0.73,0.82,1)
world.node_tree.nodes['Background'].inputs[1].default_value = 0.5
bpy.ops.object.light_add(type='AREA', location=(1,-4,7))
bpy.context.object.data.energy = 1100
bpy.context.object.data.shape = 'DISK'
bpy.context.object.data.size = 5
bpy.ops.object.camera_add(location=(5.7,-7.6,4.8))
camera = bpy.context.object
camera.name = 'Market presentation camera'
camera.rotation_euler = (Vector((0,0,1.5))-camera.location).to_track_quat('-Z','Y').to_euler()
camera.data.type = 'ORTHO'
camera.data.ortho_scale = 6.4
bpy.context.scene.camera = camera
bpy.context.scene.render.resolution_x = 1100
bpy.context.scene.render.resolution_y = 900
