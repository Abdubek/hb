import bpy
from mathutils import Vector

# Desk organizer, dimensions in meters.
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

walnut = material('Warm walnut', (0.24, 0.105, 0.045))
navy = material('Blue powder coat', (0.035, 0.105, 0.16), 0.35)
brass = material('Brass details', (0.65, 0.40, 0.12), 0.7)
paper = material('Ivory paper', (0.88, 0.85, 0.74))
red = material('Terracotta pencil', (0.65, 0.13, 0.065))
wood = material('Pencil wood', (0.70, 0.47, 0.24))
black = material('Graphite and rubber', (0.025, 0.03, 0.035))
desk = material('Desk surface', (0.38, 0.42, 0.43))

def box(name, loc, size, mat, bevel=0.002):
    bpy.ops.mesh.primitive_cube_add(size=1, location=loc)
    o = bpy.context.object
    o.name = name
    o.dimensions = size
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    o.data.materials.append(mat)
    if bevel:
        mod = o.modifiers.new('Soft manufactured edges', 'BEVEL')
        mod.width = bevel
        mod.segments = 3
        o.modifiers.new('Weighted normals', 'WEIGHTED_NORMAL')
    return o

def cylinder(name, loc, radius, depth, mat, vertices=32):
    bpy.ops.mesh.primitive_cylinder_add(vertices=vertices, radius=radius,
                                      depth=depth, location=loc)
    o = bpy.context.object
    o.name = name
    o.data.materials.append(mat)
    bevel = o.modifiers.new('Edge highlight', 'BEVEL')
    bevel.width = 0.0007
    bevel.segments = 2
    o.modifiers.new('Weighted normals', 'WEIGHTED_NORMAL')
    return o

def cup(name, x, y, width, depth, height):
    bottom = 0.022
    t = 0.004
    box(name + ' floor', (x, y, bottom + t/2), (width, depth, t), navy)
    for sign in (-1, 1):
        box(name + (' left wall' if sign < 0 else ' right wall'),
            (x + sign*(width-t)/2, y, bottom+height/2), (t, depth, height), navy)
        box(name + (' front wall' if sign < 0 else ' back wall'),
            (x, y + sign*(depth-t)/2, bottom+height/2),
            (width-2*t, t, height), navy)
    box(name + ' label', (x, y-depth/2-0.001, bottom+height*0.58),
        (width*0.45, 0.0015, 0.012), brass, 0.0005)

box('Organizer walnut plinth', (0, 0, 0.012), (0.48, 0.32, 0.02), walnut, 0.007)
for x in (-0.205, 0.205):
    for y in (-0.125, 0.125):
        cylinder('Non-slip foot', (x, y, 0), 0.012, 0.006, black)

# Two open cups occupy the left column.
cup('Tall pencil cup', -0.166, 0.078, 0.105, 0.112, 0.125)
cup('Short pen cup', -0.166, -0.072, 0.105, 0.108, 0.082)
for i, (x, y) in enumerate([(-0.191, 0.057), (-0.168, 0.09),
                             (-0.139, 0.066), (-0.190, 0.108)]):
    length = 0.172 + 0.008*(i % 2)
    cylinder('Pencil %d lacquer barrel' % i, (x, y, 0.026+length/2),
             0.0037, length, red if i % 2 else navy, 6)
    bpy.ops.mesh.primitive_cone_add(vertices=6, radius1=0.0037,
        radius2=0.0008, depth=0.013, location=(x, y, 0.026+length+0.0065))
    bpy.context.object.name = 'Pencil %d sharpened wood' % i
    bpy.context.object.data.materials.append(wood)
    bpy.ops.mesh.primitive_cone_add(vertices=6, radius1=0.0008,
        radius2=0, depth=0.004, location=(x, y, 0.026+length+0.015))
    bpy.context.object.name = 'Pencil %d graphite tip' % i
    bpy.context.object.data.materials.append(black)
for i in range(3):
    x, y = -0.19+i*0.024, -0.074+(i % 2)*0.019
    cylinder('Pen %d body' % i, (x, y, 0.094), 0.0045, 0.136, navy)
    cylinder('Pen %d cap' % i, (x, y, 0.15), 0.005, 0.03, brass)
    box('Pen %d pocket clip' % i, (x+0.005, y, 0.147),
        (0.002, 0.003, 0.023), brass, 0.0006)

# Low open-front paper tray sized for small correspondence.
box('Paper tray bottom', (0.07, 0, 0.028), (0.286, 0.275, 0.012), navy)
for x in (-0.069, 0.209):
    box('Paper tray side rail', (x, 0, 0.05), (0.008, 0.275, 0.048), navy)
box('Paper tray rear wall', (0.07, 0.1335, 0.05), (0.27, 0.008, 0.048), navy)
# Two short front lips leave a convenient finger opening.
for x in (-0.024, 0.164):
    box('Tray front retaining lip', (x, -0.133, 0.04), (0.09, 0.008, 0.027), navy)
for i in range(7):
    sheet = box('Correspondence sheet %02d' % i,
                (0.069+(i % 3)*0.0008, -0.003, 0.035+i*0.001),
                (0.25, 0.239, 0.0007), paper, 0.0002)
    sheet.rotation_euler.z = (i % 3-1)*0.004
box('Desktop', (0, 0, -0.023), (1.2, 0.95, 0.035), desk, 0.015)

world = bpy.data.worlds.new('Studio world')
bpy.context.scene.world = world
world.use_nodes = True
world.node_tree.nodes['Background'].inputs[0].default_value = (0.7, 0.75, 0.8, 1)
world.node_tree.nodes['Background'].inputs[1].default_value = 0.45
bpy.ops.object.light_add(type='AREA', location=(-0.35, -0.35, 0.9))
bpy.context.object.name = 'Large softbox'
bpy.context.object.data.energy = 70
bpy.context.object.data.shape = 'DISK'
bpy.context.object.data.size = 0.7
bpy.ops.object.camera_add(location=(0.64, -0.8, 0.69))
cam = bpy.context.object
cam.name = 'Organizer overview'
cam.rotation_euler = (Vector((0, 0, 0.065))-cam.location).to_track_quat('-Z', 'Y').to_euler()
cam.data.type = 'ORTHO'
cam.data.ortho_scale = 0.71
bpy.context.scene.camera = cam
bpy.context.scene.render.resolution_x = 1200
bpy.context.scene.render.resolution_y = 1000
bpy.context.scene.render.resolution_percentage = 100
