import bpy
import math
from mathutils import Vector

bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)

def material(name, color, metallic=0.0):
    m = bpy.data.materials.new(name)
    m.diffuse_color = (*color, 1)
    m.use_nodes = True
    bs = m.node_tree.nodes.get('Principled BSDF')
    bs.inputs['Base Color'].default_value = (*color, 1)
    bs.inputs['Metallic'].default_value = metallic
    bs.inputs['Roughness'].default_value = 0.42
    return m

blue = material('Ocean blue painted steel', (0.035, 0.22, 0.34), 0.5)
frame = material('Frame blue', (0.025, 0.13, 0.20), 0.55)
steel = material('Galvanized door hardware', (0.49, 0.55, 0.58), 0.8)
rubber = material('Dark door seals', (0.018, 0.022, 0.026))
ground = material('Concrete', (0.26, 0.28, 0.29))

def box(name, loc, size, mat, bevel=0.015):
    bpy.ops.mesh.primitive_cube_add(size=1, location=loc)
    o = bpy.context.object
    o.name = name
    o.dimensions = size
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    o.data.materials.append(mat)
    if bevel:
        mod = o.modifiers.new('Soft steel edges', 'BEVEL')
        mod.width = bevel
        mod.segments = 2
    return o

def rod(name, a, b, radius, mat):
    delta = Vector(b) - Vector(a)
    bpy.ops.mesh.primitive_cylinder_add(vertices=12, radius=radius, depth=delta.length, location=(Vector(a)+Vector(b))/2)
    o = bpy.context.object
    o.name = name
    o.rotation_euler = delta.to_track_quat('Z', 'Y').to_euler()
    o.data.materials.append(mat)
    return o

# Folded sheet surface: flat valleys and raised, flat-topped ribs.
def corrugated_side(sign):
    verts, faces = [], []
    count = 30
    pitch = 5.76 / count
    for i in range(count):
        for fraction, depth in [(0, 0), (0.20, 0), (0.36, 0.045), (0.70, 0.045), (0.86, 0), (1, 0)]:
            x = -2.88 + (i + fraction) * pitch
            verts.extend([(x, sign*(1.185+depth), 0.27), (x, sign*(1.185+depth), 2.58)])
    for j in range(len(verts)//2-1):
        face = (2*j, 2*j+2, 2*j+3, 2*j+1)
        faces.append(face if sign < 0 else tuple(reversed(face)))
    mesh = bpy.data.meshes.new('Folded side sheet mesh')
    mesh.from_pydata(verts, [], faces)
    mesh.update()
    o = bpy.data.objects.new('Corrugated side ' + str(sign), mesh)
    bpy.context.collection.objects.link(o)
    o.data.materials.append(blue)
    mod = o.modifiers.new('Sheet gauge', 'SOLIDIFY')
    mod.thickness = 0.008

box('Container floor chassis', (0, 0, 0.19), (6.06, 2.44, 0.18), frame)
box('Roof sheet', (0, 0, 2.66), (5.91, 2.35, 0.055), blue)
for side in [-1, 1]:
    corrugated_side(side)
    for z in [0.27, 2.63]:
        box('Long perimeter rail', (0, side*1.20, z), (6.06, 0.11, 0.14), frame)
for x in [-2.98, 2.98]:
    for y in [-1.17, 1.17]:
        box('Corner post', (x, y, 1.45), (0.13, 0.14, 2.46), frame)
        for z in [0.20, 2.66]:
            box('Corner casting', (x, y, z), (0.18, 0.19, 0.17), steel)
            box('Casting socket inset', (x+math.copysign(0.092, x), y, z), (0.008, 0.085, 0.06), rubber)
    for z in [0.28, 2.61]:
        box('End cross rail', (x, 0, z), (0.13, 2.31, 0.13), frame)
box('Closed rear end sheet', (-2.965, 0, 1.45), (0.055, 2.25, 2.23), blue)
for i in range(12):
    box('Rear vertical pressed rib', (-3.005, -1.04+i*0.189, 1.45), (0.055, 0.07, 2.14), blue)
for i in range(28):
    box('Roof transverse corrugation', (-2.78+i*0.206, 0, 2.703), (0.075, 2.19, 0.034), blue, 0.012)
box('Door perimeter gasket', (3.012, 0, 1.445), (0.035, 2.24, 2.22), rubber)
for side in [-1, 1]:
    yc = side*0.558
    box('Left door' if side < 0 else 'Right door', (3.042, yc, 1.445), (0.045, 1.086, 2.17), blue)
    for offset in [-0.36, -0.12, 0.12, 0.36]:
        box('Door pressed rib', (3.078, yc+offset, 1.49), (0.04, 0.075, 1.82), blue)
    for offset in [-0.29, 0.29]:
        y = yc+offset
        rod('Vertical locking bar', (3.135, y, 0.40), (3.135, y, 2.48), 0.022, steel)
        for z in [0.43, 0.94, 1.95, 2.46]:
            box('Lock bar bracket', (3.145, y, z), (0.07, 0.09, 0.065), steel)
        rod('Locking handle', (3.17, y, 1.05), (3.17, y+0.18, 1.05), 0.017, steel)
    for z in [0.55, 1.43, 2.31]:
        box('Hinge strap', (3.108, side*1.025, z), (0.055, 0.20, 0.065), steel)
        rod('Hinge pin', (3.13, side*1.12, z-0.065), (3.13, side*1.12, z+0.065), 0.028, steel)
box('Concrete apron', (0, 0, -0.06), (11, 8, 0.12), ground)

bpy.ops.object.camera_add(location=(10, -9, 6.5))
cam = bpy.context.object
cam.name = 'Container three quarter camera'
cam.rotation_euler = (Vector((0, 0, 1.3))-cam.location).to_track_quat('-Z', 'Y').to_euler()
cam.data.type = 'ORTHO'
cam.data.ortho_scale = 9.3
bpy.context.scene.camera = cam
bpy.ops.object.light_add(type='AREA', location=(2, -4, 9))
bpy.context.object.data.energy = 1800
bpy.context.object.data.shape = 'DISK'
bpy.context.object.data.size = 7
bpy.context.scene.world.color = (0.3, 0.3, 0.3)
bpy.context.scene.render.resolution_x = 1200
bpy.context.scene.render.resolution_y = 800
bpy.context.scene.render.resolution_percentage = 100
