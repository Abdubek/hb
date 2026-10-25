import bpy
import math
from mathutils import Vector

# Recessed tiled pool, coping, paved deck and stainless entry ladder.
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)

def material(name, color, metallic=0, roughness=0.45):
    m = bpy.data.materials.new(name)
    m.diffuse_color = (*color,1)
    m.use_nodes = True
    bs = m.node_tree.nodes.get('Principled BSDF')
    bs.inputs['Base Color'].default_value = (*color,1)
    bs.inputs['Metallic'].default_value = metallic
    bs.inputs['Roughness'].default_value = roughness
    return m

grout = material('Pale waterproof grout', (0.58,0.7,0.72))
tiles = [material('Ceramic aqua', (0.09,0.48,0.59), roughness=0.25),
         material('Ceramic sky', (0.23,0.65,0.73), roughness=0.25),
         material('Ceramic pale blue', (0.43,0.76,0.79), roughness=0.25)]
navy = material('Lane marking navy', (0.025,0.10,0.19))
stone = material('Cream limestone coping', (0.77,0.74,0.64), roughness=0.75)
deck = material('Warm gray deck pavers', (0.49,0.47,0.42), roughness=0.9)
joint = material('Paver joints', (0.23,0.24,0.22), roughness=0.9)
steel = material('Polished ladder steel', (0.65,0.72,0.75), 0.9, 0.2)
rubber = material('Black step grip', (0.025,0.03,0.035))

def box(name, loc, dimensions, mat, bevel=0):
    bpy.ops.mesh.primitive_cube_add(size=1, location=loc)
    ob = bpy.context.object
    ob.name = name
    ob.dimensions = dimensions
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    ob.data.materials.append(mat)
    if bevel:
        mod = ob.modifiers.new('Rounded edges', 'BEVEL')
        mod.width = bevel
        mod.segments = 2
        ob.modifiers.new('Weighted normals', 'WEIGHTED_NORMAL')
    return ob

def pipe(name, points, radius, mat):
    curve = bpy.data.curves.new(name,'CURVE')
    curve.dimensions = '3D'
    curve.bevel_depth = radius
    curve.bevel_resolution = 3
    spline = curve.splines.new('POLY')
    spline.points.add(len(points)-1)
    for p,co in zip(spline.points,points):
        p.co = (*co,1)
    ob = bpy.data.objects.new(name,curve)
    bpy.context.collection.objects.link(ob)
    ob.data.materials.append(mat)

# Interior opening: 8 by 4 m. Deck surface is z=0; floor is z=-1.6.
box('Pool foundation', (0,0,-1.78), (8.5,4.5,0.36), grout)
for y in (-2.12,2.12):
    box('Long concrete pool wall', (0,y,-0.8), (8.48,0.24,1.6), grout)
for x in (-4.12,4.12):
    box('End concrete pool wall', (x,0,-0.8), (0.24,4,1.6), grout)
for i in range(20):
    for j in range(10):
        mat = navy if j in (3,6) and 2 <= i <= 17 else tiles[(i+2*j)%3]
        box('Floor tile %02d %02d'%(i,j), (-3.8+i*0.4,-1.8+j*0.4,-1.59),
            (0.39,0.39,0.02), mat)
for side in (-1,1):
    for row in range(4):
        z = -1.4+row*0.4
        for i in range(20):
            box('Long wall tile', (-3.8+i*0.4,side*1.989,z),
                (0.39,0.02,0.39), tiles[(i+row)%3])
        for j in range(10):
            box('End wall tile', (side*3.989,-1.8+j*0.4,z),
                (0.02,0.39,0.39), tiles[(j+row)%3])

# Deck built around an open center; individual pavers expose narrow joints.
for y in (-3,3):
    box('Long deck substrate', (0,y,-0.18), (11.2,1.8,0.32), joint)
for x in (-4.9,4.9):
    box('End deck substrate', (x,0,-0.18), (1.4,4.2,0.32), joint)
for ix in range(14):
    for iy in range(10):
        x,y = -5.2+ix*0.8,-3.6+iy*0.8
        if abs(x)>4.05 or abs(y)>2.05:
            box('Deck paving slab', (x,y,-0.035), (0.785,0.785,0.07), deck,0.009)
for side in (-1,1):
    for i in range(16):
        box('Long edge coping', (-3.75+i*0.5,side*2.15,0.04), (0.49,0.34,0.12), stone,0.02)
    for j in range(9):
        box('End edge coping', (side*4.15,-2+j*0.5,0.04), (0.34,0.49,0.12), stone,0.02)

# A lightly tinted transparent surface keeps the tile pattern visible.
water = bpy.data.materials.new('Clear cyan pool water')
water.use_nodes = True
nodes = water.node_tree.nodes
nodes.clear()
out = nodes.new('ShaderNodeOutputMaterial')
transparent = nodes.new('ShaderNodeBsdfTransparent')
transparent.inputs[0].default_value = (0.7,0.94,0.98,1)
gloss = nodes.new('ShaderNodeBsdfPrincipled')
gloss.inputs['Base Color'].default_value = (0.07,0.5,0.62,1)
gloss.inputs['Roughness'].default_value = 0.16
mix = nodes.new('ShaderNodeMixShader')
mix.inputs[0].default_value = 0.18
water.node_tree.links.new(transparent.outputs[0],mix.inputs[1])
water.node_tree.links.new(gloss.outputs[0],mix.inputs[2])
water.node_tree.links.new(mix.outputs[0],out.inputs['Surface'])
bpy.ops.mesh.primitive_plane_add(size=2, location=(0,0,-0.28))
ob = bpy.context.object
ob.name = 'Still water surface'
ob.scale = (3.98,1.98,1)
ob.data.materials.append(water)

for x in (2.45,3.15):
    points = [(x,2.55,0.04),(x,2.55,0.6)]
    points += [(x,2.15+0.4*math.cos(t*math.pi/20),0.6+0.4*math.sin(t*math.pi/20)) for t in range(21)]
    points += [(x,1.75,-1.2),(x,1.87,-1.35),(x,1.97,-1.35)]
    pipe('Ladder continuous handrail',points,0.043,steel)
    box('Ladder deck mounting plate',(x,2.55,0.035),(0.2,0.22,0.055),steel,0.025)
for z in (-0.15,-0.48,-0.81,-1.14):
    box('Ladder stainless tread',(2.8,1.75,z),(0.75,0.18,0.055),steel,0.015)
    box('Ladder nonslip tread insert',(2.8,1.75,z+0.03),(0.59,0.13,0.012),rubber,0.006)

bpy.ops.object.camera_add(location=(11,-14,13))
camera = bpy.context.object
camera.name = 'Pool overview camera'
camera.rotation_euler = (Vector((0,0,-0.3))-camera.location).to_track_quat('-Z','Y').to_euler()
camera.data.type = 'ORTHO'
camera.data.ortho_scale = 15.6
bpy.context.scene.camera = camera
bpy.ops.object.light_add(type='AREA',location=(0,-3,10))
bpy.context.object.data.energy = 2200
bpy.context.object.data.size = 8
bpy.context.scene.world.color = (0.3,0.3,0.3)
