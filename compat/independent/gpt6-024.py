import bpy
import bmesh
import math
from mathutils import Vector

bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)

def material(name, color, metal=0.0):
    m = bpy.data.materials.new(name)
    m.diffuse_color = (*color,1)
    m.use_nodes = True
    bs = m.node_tree.nodes.get('Principled BSDF')
    bs.inputs['Base Color'].default_value = (*color,1)
    bs.inputs['Metallic'].default_value = metal
    bs.inputs['Roughness'].default_value = 0.36
    return m

blue = material('Blue powder-coated frame', (0.035,0.25,0.48), 0.45)
yellow = material('Yellow slide shell', (0.98,0.58,0.035), 0.1)
red = material('Coral safety rails', (0.8,0.12,0.065), 0.3)
deck = material('Textured dark platform', (0.11,0.14,0.17))
silver = material('Steel hardware', (0.55,0.62,0.67), 0.8)
rubber = material('Rubber play surface', (0.24,0.36,0.30))

def finish(obj, name, mat):
    obj.name = name
    obj.data.materials.append(mat)
    return obj

def box(name, center, size, mat, bevel=0.03):
    bpy.ops.mesh.primitive_cube_add(size=1, location=center)
    obj = finish(bpy.context.object, name, mat)
    obj.dimensions = size
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    if bevel:
        mod = obj.modifiers.new('Soft manufactured edges','BEVEL')
        mod.width = bevel
        mod.segments = 2
    return obj

def tube(name, a, b, radius, mat):
    a, b = Vector(a), Vector(b)
    bpy.ops.mesh.primitive_cylinder_add(vertices=16, radius=radius, depth=(b-a).length, location=(a+b)/2)
    obj = finish(bpy.context.object, name, mat)
    obj.rotation_euler = (b-a).to_track_quat('Z','Y').to_euler()
    for face in obj.data.polygons:
        face.use_smooth = len(face.vertices) == 4
    return obj

box('Playground safety pad', (1.5,0,-0.12), (10,6,0.24), rubber, 0.12)
box('Elevated landing platform', (0,0,2.66), (2,1.65,0.18), deck)
for x in (-0.86,0.86):
    for y in (-0.68,0.68):
        tube('Platform support post', (x,y,0.08), (x,y,3.7), 0.065, blue)
        box('Ground mounting plate', (x,y,0.055), (0.27,0.27,0.11), silver)
        for dx in (-0.085,0.085):
            tube('Anchor bolt', (x+dx,y,0.1), (x+dx,y,0.14), 0.024, silver)
for y in (-0.68,0.68):
    tube('Under-deck longitudinal beam', (-0.9,y,2.51), (0.9,y,2.51), 0.085, blue)
    tube('Diagonal platform brace', (-0.86,y,0.6), (0.86,y,2.45), 0.035, blue)
    tube('Side guardrail', (-0.86,y,3.7), (0.86,y,3.7), 0.045, red)
    for x in (-0.6,-0.3,0,0.3,0.6):
        tube('Vertical safety baluster', (x,y,2.75), (x,y,3.67), 0.024, blue)
# Short rear rails leave the ladder entrance open.
for sign in (-1,1):
    tube('Rear entrance rail', (-0.86,sign*0.48,3.7), (-0.86,sign*0.68,3.7), 0.045, red)
    tube('Slide entrance handhold', (0.86,sign*0.68,3.7), (1.28,sign*0.59,3.08), 0.045, red)

# Inclined access ladder with broad, level treads.
for y in (-0.48,0.48):
    tube('Ladder stringer', (-2.5,y,0.08), (-0.96,y,2.76), 0.055, blue)
    tube('Ladder handrail', (-2.5,y,0.88), (-0.96,y,3.65), 0.04, red)
    for t in (0.05,0.5,0.95):
        x, z = -2.5+1.54*t, 0.08+2.68*t
        tube('Handrail riser', (x,y,z), (x,y,z+0.8), 0.03, red)
for i in range(1,10):
    t = i/10
    box('Ladder tread %02d' % i, (-2.5+1.54*t,0,0.08+2.68*t), (0.25,0.94,0.065), deck, 0.015)

# An extruded U-shaped section forms a continuous solid slide and sidewalls.
profile = [(-0.65,0.32),(-0.58,0.32),(-0.58,0),(0.58,0),(0.58,0.32),(0.65,0.32),(0.65,-0.08),(-0.65,-0.08)]
vertices, faces = [], []
segments = 36
for i in range(segments+1):
    t = i/segments
    x = 1 + 4.4*t
    z = 0.35 + 2.4*(1-3*t*t+2*t*t*t)
    vertices.extend((x,y,z+offset) for y,offset in profile)
for i in range(segments):
    for j in range(8):
        k = (j+1)%8
        faces.append((i*8+j,i*8+k,(i+1)*8+k,(i+1)*8+j))
faces.extend([tuple(reversed(range(8))), tuple(segments*8+j for j in range(8))])
mesh = bpy.data.meshes.new('Solid curved slide mesh')
mesh.from_pydata(vertices, [], faces)
mesh.update()
bm = bmesh.new()
bm.from_mesh(mesh)
bmesh.ops.recalc_face_normals(bm, faces=list(bm.faces))
bm.to_mesh(mesh)
bm.free()
slide = bpy.data.objects.new('Sweeping yellow slide with raised sidewalls', mesh)
bpy.context.collection.objects.link(slide)
slide.data.materials.append(yellow)
mod = slide.modifiers.new('Rounded slide edges','BEVEL')
mod.width = 0.025
mod.segments = 3
for t in (0.38,0.78,0.97):
    x = 1+4.4*t
    z = 0.35+2.4*(1-3*t*t+2*t*t*t)-0.1
    tube('Slide underside crossbar', (x,-0.56,z), (x,0.56,z), 0.04, blue)
    for y in (-0.47,0.47):
        tube('Slide support leg', (x,y,0.05), (x,y,z), 0.045, blue)

world = bpy.context.scene.world or bpy.data.worlds.new('World')
bpy.context.scene.world = world
world.use_nodes = True
world.node_tree.nodes['Background'].inputs[0].default_value = (0.72,0.81,0.9,1)
world.node_tree.nodes['Background'].inputs[1].default_value = 0.6
bpy.ops.object.light_add(type='AREA', location=(1,-4,9))
bpy.context.object.data.energy = 1500
bpy.context.object.data.size = 6
bpy.ops.object.camera_add(location=(9,-12,8))
camera = bpy.context.object
camera.rotation_euler = (Vector((1.4,0,1.6))-camera.location).to_track_quat('-Z','Y').to_euler()
camera.data.type = 'ORTHO'
camera.data.ortho_scale = 11
bpy.context.scene.camera = camera
