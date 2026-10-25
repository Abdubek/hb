import bpy
import math
from mathutils import Vector

# Traditional rural mailbox, with its front facing negative Y.
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)

def material(name, color, metallic=0.0, roughness=0.45):
    m = bpy.data.materials.new(name)
    m.diffuse_color = (*color, 1)
    m.use_nodes = True
    bs = m.node_tree.nodes.get('Principled BSDF')
    bs.inputs['Base Color'].default_value = (*color, 1)
    bs.inputs['Metallic'].default_value = metallic
    bs.inputs['Roughness'].default_value = roughness
    return m

blue = material('Enamel - midnight blue', (0.035, 0.12, 0.22), 0.55)
steel = material('Galvanized trim', (0.55, 0.61, 0.65), 0.8)
red = material('Signal red enamel', (0.8, 0.035, 0.025), 0.3)
wood = material('Warm painted timber', (0.34, 0.20, 0.105))
black = material('Door reveal', (0.018, 0.024, 0.03))
white = material('Ivory lettering', (0.92, 0.87, 0.72))
ground = material('Ground', (0.22, 0.28, 0.18), roughness=0.9)

def finish(obj, name, mat, bevel=0.0):
    obj.name = name
    obj.data.materials.append(mat)
    if bevel:
        mod = obj.modifiers.new('Soft manufactured edges', 'BEVEL')
        mod.width = bevel
        mod.segments = 3
        obj.modifiers.new('Weighted corner normals', 'WEIGHTED_NORMAL')
    return obj

def box(name, location, scale, mat, bevel=0.015):
    bpy.ops.mesh.primitive_cube_add(size=1, location=location)
    o = bpy.context.object
    o.dimensions = scale
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    return finish(o, name, mat, bevel)

def cylinder(name, location, radius, depth, mat, rotation=(0, 0, 0)):
    bpy.ops.mesh.primitive_cylinder_add(vertices=32, radius=radius, depth=depth,
                                      location=location, rotation=rotation)
    return finish(bpy.context.object, name, mat, 0.006)

# Extruded arch section: straight sides with a semicircular crown.
def arched_body(name, radius, bottom, spring, front, back, mat):
    section = [(-radius, bottom), (radius, bottom)]
    section += [(radius * math.cos(math.pi * i / 24),
                 spring + radius * math.sin(math.pi * i / 24)) for i in range(25)]
    n = len(section)
    verts = [(x, y, z) for y in (front, back) for x, z in section]
    faces = [tuple(range(n)), tuple(range(2*n-1, n-1, -1))]
    faces += [(i, n+i, n+(i+1) % n, (i+1) % n) for i in range(n)]
    mesh = bpy.data.meshes.new(name + ' mesh')
    mesh.from_pydata(verts, [], faces)
    mesh.update()
    obj = bpy.data.objects.new(name, mesh)
    bpy.context.collection.objects.link(obj)
    return finish(obj, name, mat, 0.008)

box('Ground patch', (0, 0, -0.075), (4, 4, 0.15), ground, 0.12)
box('Timber post', (0, 0.18, 0.91), (0.22, 0.22, 1.82), wood, 0.025)
box('Post foot collar', (0, 0.18, 0.12), (0.28, 0.28, 0.18), steel)
box('Horizontal mounting beam', (0, 0, 1.77), (0.20, 1.65, 0.16), wood)
a, b = Vector((0, 0.18, 1.13)), Vector((0, -0.59, 1.72))
brace = box('Diagonal timber brace', (a+b)/2, (0.13, 0.13, (b-a).length), wood)
brace.rotation_euler = (b-a).to_track_quat('Z', 'Y').to_euler()
box('Mailbox mounting plate', (0, 0, 1.885), (0.78, 1.65, 0.07), steel)
arched_body('Rounded mailbox shell', 0.43, 1.92, 2.31, -0.83, 0.83, blue)
arched_body('Front perimeter trim', 0.445, 1.915, 2.31, -0.855, -0.82, steel)
arched_body('Door gasket', 0.423, 1.935, 2.31, -0.872, -0.85, black)
arched_body('Closed arched front door', 0.403, 1.95, 2.31, -0.891, -0.87, blue)
cylinder('Bottom door hinge barrel', (0, -0.91, 1.97), 0.025, 0.64, steel,
         (0, math.pi/2, 0))
box('Latch bracket', (0, -0.916, 2.52), (0.10, 0.05, 0.10), steel)
box('Door pull', (0, -0.96, 2.50), (0.18, 0.07, 0.045), steel)
# Flag stands upright on the visible right side.
cylinder('Flag pivot washer', (0.45, 0.25, 2.20), 0.065, 0.025, steel,
         (0, math.pi/2, 0))
box('Raised flag stem', (0.482, 0.25, 2.56), (0.028, 0.055, 0.73), red, 0.008)
box('Rectangular signal flag', (0.482, 0.09, 2.88), (0.03, 0.37, 0.20), red, 0.01)
cylinder('Flag pivot bolt', (0.505, 0.25, 2.20), 0.023, 0.025, steel,
         (0, math.pi/2, 0))
box('Address plaque', (0, -0.905, 2.20), (0.43, 0.018, 0.19), white)
bpy.ops.object.text_add(location=(0, -0.918, 2.20), rotation=(math.pi/2, 0, 0))
text = bpy.context.object
text.name = 'Address number 24'
text.data.body = '24'
text.data.align_x = 'CENTER'
text.data.align_y = 'CENTER'
text.data.size = 0.15
text.data.extrude = 0.001
text.data.materials.append(blue)

scene = bpy.context.scene
scene.world.color = (0.22, 0.22, 0.22)
bpy.ops.object.light_add(type='AREA', location=(3, -4, 6))
bpy.context.object.data.energy = 800
bpy.context.object.data.shape = 'DISK'
bpy.context.object.data.size = 4
bpy.ops.object.camera_add(location=(4.2, -6.2, 3.7))
camera = bpy.context.object
camera.name = 'Mailbox presentation camera'
camera.rotation_euler = (Vector((0, 0, 1.5))-camera.location).to_track_quat('-Z', 'Y').to_euler()
camera.data.type = 'ORTHO'
camera.data.ortho_scale = 4.3
scene.camera = camera
scene.render.resolution_x = 900
scene.render.resolution_y = 900
scene.render.resolution_percentage = 100
