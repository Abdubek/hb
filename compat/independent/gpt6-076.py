import bpy
from mathutils import Vector

# Three alternating steel flights with rear balconies and end landings.
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)

def material(name, color, metallic=0.0, roughness=0.5):
    m = bpy.data.materials.new(name)
    m.diffuse_color = (*color, 1)
    m.use_nodes = True
    p = m.node_tree.nodes.get('Principled BSDF')
    p.inputs['Base Color'].default_value = (*color, 1)
    p.inputs['Metallic'].default_value = metallic
    p.inputs['Roughness'].default_value = roughness
    return m

metal = material('Painted charcoal escape steel', (0.085, 0.105, 0.115), 0.7)
treads = material('Worn galvanized tread edges', (0.36, 0.40, 0.41), 0.75)
brick = material('Terracotta masonry', (0.43, 0.20, 0.135))
stone = material('Window stone trim', (0.65, 0.60, 0.49))
glass = material('Blue gray window glass', (0.095, 0.19, 0.24), 0.35, 0.22)
ground = material('Pavement', (0.29, 0.30, 0.29))
mortar = material('Mortar joints', (0.34, 0.27, 0.23))

def box(name, loc, dims, mat, bevel=0.0):
    bpy.ops.mesh.primitive_cube_add(size=1, location=loc)
    o = bpy.context.object
    o.name = name
    o.dimensions = dims
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    o.data.materials.append(mat)
    if bevel:
        mod = o.modifiers.new('Soft metal edges', 'BEVEL')
        mod.width = bevel
        mod.segments = 2
    return o

def beam(name, a, b, width, depth, mat=metal):
    a, b = Vector(a), Vector(b)
    o = box(name, (a+b)/2, (width, depth, (b-a).length), mat)
    o.rotation_euler = (b-a).to_track_quat('Z', 'Y').to_euler()
    return o

def rail(name, a, b, radius=0.025):
    a, b = Vector(a), Vector(b)
    bpy.ops.mesh.primitive_cylinder_add(vertices=10, radius=radius, depth=(b-a).length, location=(a+b)/2)
    o = bpy.context.object
    o.name = name
    o.data.materials.append(metal)
    o.rotation_euler = (b-a).to_track_quat('Z', 'Y').to_euler()
    return o

def railing(name, a, b, height=1.05, divisions=8):
    a, b = Vector(a), Vector(b)
    rail(name+' handrail', a+Vector((0, 0, height)), b+Vector((0, 0, height)), 0.034)
    rail(name+' midrail', a+Vector((0, 0, 0.51)), b+Vector((0, 0, 0.51)), 0.021)
    for i in range(divisions+1):
        p = a.lerp(b, i/divisions)
        rail(name+' upright %02d' % i, p, p+Vector((0, 0, height)), 0.022)

def deck(name, cx, cy, z, sx, sy):
    # Open steel slats, boxed perimeter and transverse underside support.
    for yy in (cy-sy/2, cy+sy/2):
        box(name+' perimeter', (cx, yy, z-0.075), (sx, 0.065, 0.15), metal)
    for xx in (cx-sx/2, cx+sx/2):
        box(name+' end frame', (xx, cy, z-0.075), (0.065, sy, 0.15), metal)
    count = max(2, int(sx/0.105))
    for i in range(count):
        xx = cx-sx/2+(i+0.5)*sx/count
        box(name+' grating slat %02d' % i, (xx, cy, z-0.025), (0.045, sy, 0.05), treads)
    box(name+' underside crossbar', (cx, cy, z-0.12), (sx, 0.06, 0.09), metal)

box('Pavement slab', (0, -0.8, -0.16), (11, 8, 0.3), ground, 0.04)
box('Building masonry wall', (0, 1.5, 4.7), (8.3, 3, 9.4), brick, 0.02)
box('Roof cornice', (0, 1.42, 9.42), (8.65, 3.25, 0.24), stone, 0.025)
# Shallow mortar lines add architectural scale without a dense brick mesh.
for i in range(46):
    box('Horizontal masonry joint %02d' % i, (0, -0.012, 0.12+i*0.20), (8.3, 0.015, 0.012), mortar)
for level in (2.7, 5.3, 7.9):
    for x in (-1.45, 1.45):
        z = level+0.62
        box('Window stone surround', (x, -0.065, z), (1.24, 0.14, 1.62), stone, 0.018)
        box('Recessed window frame', (x, -0.148, z), (1.04, 0.05, 1.43), metal)
        box('Window glazing', (x, -0.18, z), (0.93, 0.025, 1.30), glass)
        box('Window vertical mullion', (x, -0.204, z), (0.035, 0.03, 1.30), metal)
        box('Window sash rail', (x, -0.205, z), (0.96, 0.03, 0.045), metal)
        box('Projecting window sill', (x, -0.20, z-0.81), (1.37, 0.40, 0.10), stone)
    deck('Level %.1f rear balcony' % level, 0, -0.82, level, 5.4, 1.05)
    for x in (-2.25, 2.25):
        deck('End landing', x, -1.91, level, 0.9, 1.13)
        railing('Landing outer side', (x+(-0.45 if x < 0 else 0.45), -0.3, level),
            (x+(-0.45 if x < 0 else 0.45), -2.475, level), divisions=5)
        railing('Landing front edge', (x-0.45, -2.475, level), (x+0.45, -2.475, level), divisions=3)
        box('Wall anchor plate', (x, -0.055, level-0.50), (0.3, 0.10, 1.1), metal)
        beam('Balcony cantilever', (x, -0.07, level-0.16), (x, -2.46, level-0.16), 0.13, 0.13)
        beam('Diagonal balcony bracket', (x, -0.08, level-1.05), (x, -2.2, level-0.18), 0.09, 0.09)
    railing('Rear balcony front guard', (-1.8, -1.345, level), (1.8, -1.345, level), divisions=12)

for flight in range(3):
    bottom = 0.1+flight*2.6
    top = bottom+2.6
    xa, xb = (-1.8, 1.8) if flight % 2 == 0 else (1.8, -1.8)
    count = 13
    for i in range(count):
        x = xa+(xb-xa)*(i+0.5)/count
        z = bottom+(top-bottom)*(i+1)/count
        box('Flight %d open tread %02d' % (flight+1, i+1), (x, -1.91, z-0.025),
            (3.6/count+0.025, 1.02, 0.05), treads, 0.007)
    for y in (-1.385, -2.435):
        beam('Flight %d diagonal stringer' % (flight+1), (xa, y, bottom-0.12),
            (xb, y, top-0.12), 0.085, 0.16)
        railing('Flight %d stair guard' % (flight+1), (xa, y, bottom+0.10),
            (xb, y, top+0.10), divisions=9)
box('Ground entry pad', (-2.22, -1.91, 0.035), (1.0, 1.32, 0.10), stone, 0.02)
for y in (-1.39, -2.43):
    box('Bottom stringer foot plate', (-1.8, y, 0.025), (0.32, 0.26, 0.05), metal)

scene = bpy.context.scene
scene.world.color = (0.26, 0.26, 0.26)
bpy.ops.object.light_add(type='AREA', location=(-5, -8, 13))
bpy.context.object.name = 'Facade softbox'
bpy.context.object.data.energy = 2300
bpy.context.object.data.size = 8
bpy.ops.object.camera_add(location=(12, -19, 12))
cam = bpy.context.object
cam.name = 'Fire escape overview camera'
cam.rotation_euler = (Vector((0, -0.6, 4.4))-cam.location).to_track_quat('-Z', 'Y').to_euler()
cam.data.type = 'ORTHO'
cam.data.ortho_scale = 14
scene.camera = cam
scene.render.resolution_x = 1000
scene.render.resolution_y = 1100
scene.render.resolution_percentage = 100
