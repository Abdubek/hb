import bpy
import math
from mathutils import Vector

# Folding camping chair, dimensions in meters.
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)

def material(name, color, metallic=0.0, roughness=0.5):
    m = bpy.data.materials.new(name)
    m.diffuse_color = (*color, 1)
    m.use_nodes = True
    bs = m.node_tree.nodes.get('Principled BSDF')
    bs.inputs['Base Color'].default_value = (*color, 1)
    bs.inputs['Metallic'].default_value = metallic
    bs.inputs['Roughness'].default_value = roughness
    return m

frame = material('Powder-coated graphite tubing', (0.085, 0.10, 0.115), 0.65, 0.32)
fabric = material('Forest green woven canvas', (0.055, 0.20, 0.13), 0, 0.88)
trim = material('Dark reinforced canvas edging', (0.025, 0.075, 0.05), 0, 0.85)
rubber = material('Rubber feet and arm pads', (0.025, 0.03, 0.035), 0, 0.8)
steel = material('Stainless pivot hardware', (0.55, 0.59, 0.62), 0.85, 0.24)
ground = material('Warm studio floor', (0.33, 0.32, 0.29))

def tube(name, a, b, radius, mat, vertices=16):
    direction = Vector(b) - Vector(a)
    bpy.ops.mesh.primitive_cylinder_add(vertices=vertices, radius=radius, depth=direction.length, location=(Vector(a)+Vector(b))/2)
    obj = bpy.context.object
    obj.name = name
    obj.rotation_euler = direction.to_track_quat('Z', 'Y').to_euler()
    obj.data.materials.append(mat)
    for face in obj.data.polygons:
        face.use_smooth = len(face.vertices) == 4
    bevel = obj.modifiers.new('Soft manufactured edges', 'BEVEL')
    bevel.width = 0.004
    bevel.segments = 2
    obj.modifiers.new('Weighted normals', 'WEIGHTED_NORMAL')
    return obj

def box(name, location, scale, mat, bevel=0.02):
    bpy.ops.mesh.primitive_cube_add(size=1, location=location)
    obj = bpy.context.object
    obj.name = name
    obj.dimensions = scale
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    obj.data.materials.append(mat)
    mod = obj.modifiers.new('Rounded corners', 'BEVEL')
    mod.width = bevel
    mod.segments = 3
    obj.modifiers.new('Weighted normals', 'WEIGHTED_NORMAL')
    return obj

def cloth(name, vertices, faces):
    mesh = bpy.data.meshes.new(name + ' mesh')
    mesh.from_pydata(vertices, [], faces)
    mesh.update()
    obj = bpy.data.objects.new(name, mesh)
    bpy.context.collection.objects.link(obj)
    obj.data.materials.append(fabric)
    solid = obj.modifiers.new('Canvas thickness', 'SOLIDIFY')
    solid.thickness = 0.008
    return obj

# Two crossed leg pairs with visible hinge hardware and four feet.
for side, x in [('Left', -0.49), ('Right', 0.49)]:
    tube(side + ' front foot to rear seat leg', (x,-0.48,0.09), (x,0.36,0.88), 0.026, frame)
    tube(side + ' rear foot to front seat leg', (x+0.018,0.48,0.09), (x+0.018,-0.39,0.88), 0.026, frame)
    tube(side + ' backrest upright', (x,0.34,0.76), (x,0.61,1.72), 0.025, frame)
    tube(side + ' armrest front support', (x,-0.30,0.79), (x,-0.30,1.16), 0.020, frame)
    tube(side + ' armrest rail', (x,-0.40,1.16), (x,0.455,1.16), 0.022, frame)
    box(side + ' padded armrest', (x,-0.04,1.19), (0.115,0.70,0.065), rubber)
    tube(side + ' main folding pivot', (x-0.047,0,0.51), (x+0.068,0,0.51), 0.044, steel)
    tube(side + ' pivot center cap', (x-0.053,0,0.51), (x-0.047,0,0.51), 0.017, frame)
    for y in [-0.48,0.48]:
        box(side + ' rubber foot ' + str(y), (x,y,0.055), (0.11,0.13,0.10), rubber)
    tube(side + ' seat side rail', (x,-0.39,0.88), (x,0.36,0.88), 0.023, frame)
    tube(side + ' folding lock link', (x+0.025,-0.27,0.69), (x+0.025,0.25,0.69), 0.012, steel)

for label, y in [('Front', -0.39), ('Rear', 0.36)]:
    tube(label + ' seat crossbar', (-0.49,y,0.88), (0.508,y,0.88), 0.023, frame)
tube('Backrest top crossbar', (-0.49,0.61,1.72), (0.49,0.61,1.72), 0.025, frame)
tube('Front transverse folding brace A', (-0.47,-0.445,0.18), (0.47,-0.395,0.82), 0.014, frame)
tube('Front transverse folding brace B', (0.47,-0.465,0.18), (-0.47,-0.415,0.82), 0.014, frame)
tube('Front brace rivet', (0,-0.465,0.50), (0,-0.425,0.50), 0.025, steel)
cloth('Gently sagging canvas seat', [(-0.46,-0.38,0.90),(0,-0.38,0.865),(0.46,-0.38,0.90),(-0.46,0.35,0.90),(0,0.35,0.865),(0.46,0.35,0.90)], [(0,1,4,3),(1,2,5,4)])
cloth('Canvas backrest sling', [(-0.46,0.405,0.96),(0,0.44,0.96),(0.46,0.405,0.96),(-0.46,0.595,1.68),(0,0.62,1.68),(0.46,0.595,1.68)], [(0,1,4,3),(1,2,5,4)])
for x in [-0.46,0.46]:
    tube('Backrest reinforced side seam', (x,0.405,0.96), (x,0.595,1.68), 0.013, trim)
    tube('Seat reinforced side seam', (x,-0.38,0.90), (x,0.35,0.90), 0.012, trim)
tube('Backrest top binding', (-0.46,0.595,1.68), (0.46,0.595,1.68), 0.013, trim)
box('Small stitched backrest label', (0,0.606,1.57), (0.14,0.012,0.055), trim, 0.004)
box('Studio floor', (0,0,-0.055), (200,200,0.1), ground, 0)
bpy.ops.object.camera_add(location=(3,-4,2.65))
camera = bpy.context.object
camera.name = 'Chair presentation camera'
camera.rotation_euler = (Vector((0,0.05,0.85))-camera.location).to_track_quat('-Z','Y').to_euler()
camera.data.type = 'ORTHO'
camera.data.ortho_scale = 2.65
bpy.context.scene.camera = camera
bpy.ops.object.light_add(type='AREA', location=(1,-3,5))
bpy.context.object.data.energy = 650
bpy.context.object.data.shape = 'DISK'
bpy.context.object.data.size = 4
bpy.context.scene.world.color = (0.25,0.25,0.25)
bpy.context.scene.render.resolution_x = 900
bpy.context.scene.render.resolution_y = 1000
bpy.context.scene.render.resolution_percentage = 100
