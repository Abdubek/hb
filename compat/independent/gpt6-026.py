import bpy
import math
from mathutils import Vector

# Six shipping crates stacked in two tiers on a forklift pallet.
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)

def material(name, color, metallic=0.0, roughness=0.6):
    mat = bpy.data.materials.new(name)
    mat.diffuse_color = (*color, 1)
    mat.use_nodes = True
    bsdf = mat.node_tree.nodes.get('Principled BSDF')
    bsdf.inputs['Base Color'].default_value = (*color, 1)
    bsdf.inputs['Metallic'].default_value = metallic
    bsdf.inputs['Roughness'].default_value = roughness
    return mat

pallet_wood = material('Pallet rough oak', (0.36,0.23,0.11))
wood = material('Crate pine', (0.63,0.43,0.22))
light_wood = material('Crate pale boards', (0.73,0.54,0.30))
dark = material('Dark interior', (0.16,0.105,0.055))
steel = material('Galvanized fasteners', (0.30,0.34,0.36), 0.75, 0.3)
label_mat = material('Ivory shipping labels', (0.94,0.91,0.78))
ink = material('Black label ink', (0.025,0.033,0.035))
ground = material('Warehouse floor', (0.26,0.29,0.31))

def box(name, location, dimensions, mat, bevel=0.012):
    bpy.ops.mesh.primitive_cube_add(size=1, location=location)
    obj = bpy.context.object
    obj.name = name
    obj.dimensions = dimensions
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    obj.data.materials.append(mat)
    if bevel:
        mod = obj.modifiers.new('Eased timber edges', 'BEVEL')
        mod.width = bevel
        mod.segments = 2
        obj.modifiers.new('Weighted normals', 'WEIGHTED_NORMAL')
    return obj

def beam(name, start, end, width, depth, mat):
    a, b = Vector(start), Vector(end)
    obj = box(name, (a+b)/2, (width,depth,(b-a).length), mat)
    obj.rotation_euler = (b-a).to_track_quat('Z','Y').to_euler()
    return obj

def text(name, body, location, size):
    curve = bpy.data.curves.new(name, 'FONT')
    curve.body = body
    curve.align_x = 'CENTER'
    curve.align_y = 'CENTER'
    curve.size = size
    curve.extrude = 0.0005
    obj = bpy.data.objects.new(name, curve)
    bpy.context.collection.objects.link(obj)
    obj.location = location
    obj.rotation_euler = (math.pi/2, 0, 0)
    obj.data.materials.append(ink)
    return obj

# Bottom runners, nine spacer blocks, and top boards leave fork openings.
for i, x in enumerate([-1.78, 0, 1.78]):
    box('Pallet bottom runner %d' % i, (x,0,0.06), (0.35,2.3,0.12), pallet_wood)
    for j, y in enumerate([-0.89,0,0.89]):
        box('Pallet spacer block %d-%d' % (i,j), (x,y,0.235), (0.35,0.34,0.23), pallet_wood)
    box('Pallet upper stringer %d' % i, (x,0,0.39), (0.28,2.3,0.08), pallet_wood)
for j in range(7):
    box('Pallet deck board %02d' % j, (0,-0.99+j*0.33,0.485), (4.30,0.29,0.11), light_wood)

cargo_names = ['TOOLS', 'FITTINGS', 'HARDWARE', 'SPARES', 'GAUGES', 'VALVES']
for tier in range(2):
    for column in range(3):
        n = tier*3+column+1
        prefix = 'Crate %02d' % n
        x = (column-1)*1.38
        base = 0.54 + tier*1.05
        z = base+0.50
        # A closed dark inner shell gives narrow plank gaps realistic depth.
        box(prefix+' inner box', (x,0,z), (1.14,1.66,0.91), dark)
        for row in range(4):
            board_z = base+0.135+row*0.243
            mat = wood if (row+n)%2 else light_wood
            for side in [-1,1]:
                box(prefix+' front/back plank %d %d' % (side,row), (x,side*0.87,board_z), (1.22,0.08,0.231), mat)
                box(prefix+' side plank %d %d' % (side,row), (x+side*0.61,0,board_z), (0.08,1.66,0.231), mat)
        for j in range(5):
            box(prefix+' lid board %d' % j, (x-0.488+j*0.244,0,base+0.965), (0.233,1.82,0.07), light_wood)
        for side in [-1,1]:
            for offset in [-0.49,0.49]:
                box(prefix+' vertical face batten', (x+offset,side*0.933,z), (0.10,0.065,0.98), pallet_wood)
                for bolt_z in [base+0.12,base+0.87]:
                    bpy.ops.mesh.primitive_uv_sphere_add(segments=8, ring_count=4, radius=0.023, location=(x+offset,side*0.974,bolt_z))
                    bolt = bpy.context.object
                    bolt.name = prefix+' nail head'
                    bolt.scale = (1,0.3,1)
                    bolt.data.materials.append(steel)
            beam(prefix+' side diagonal brace', (x+side*0.676,-0.74,base+0.12), (x+side*0.676,0.74,base+0.87), 0.075,0.11,pallet_wood)
        # All six individual labels face the front, including the upper tier.
        box(prefix+' label plate', (x,-0.928,z), (0.80,0.022,0.43), label_mat, 0.006)
        text(prefix+' number', 'CRATE %02d' % n, (x,-0.943,z+0.105), 0.12)
        text(prefix+' contents', cargo_names[n-1], (x,-0.943,z-0.015), 0.075)
        text(prefix+' handling mark', 'UP  /  KEEP DRY', (x,-0.943,z-0.14), 0.042)
        for k in range(24):
            width = 0.006 if (k+n)%3 else 0.013
            box(prefix+' barcode %02d' % k, (x-0.25+k*0.021,-0.943,z-0.086), (width,0.002,0.043), ink, 0)

box('Warehouse floor', (0,0,-0.045), (200,200,0.08), ground, 0)
bpy.ops.object.camera_add(location=(6,-10,6))
camera = bpy.context.object
camera.name = 'Pallet and six crates camera'
camera.rotation_euler = (Vector((0,0,1.25))-camera.location).to_track_quat('-Z','Y').to_euler()
camera.data.type = 'ORTHO'
camera.data.ortho_scale = 6.8
scene = bpy.context.scene
scene.camera = camera
bpy.ops.object.light_add(type='AREA', location=(1,-4,8))
bpy.context.object.name = 'Large warehouse soft light'
bpy.context.object.data.energy = 1500
bpy.context.object.data.size = 5
scene.world = bpy.data.worlds.new('Warehouse world')
scene.world.use_nodes = True
scene.world.node_tree.nodes['Background'].inputs[1].default_value = 0.45
scene.render.resolution_x = 1400
scene.render.resolution_y = 1100
scene.render.resolution_percentage = 100
