import bpy, math
from mathutils import Vector
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)

def material(name, color, metallic=0):
    m = bpy.data.materials.new(name)
    m.diffuse_color = (*color, 1)
    m.use_nodes = True
    p = m.node_tree.nodes.get('Principled BSDF')
    p.inputs['Base Color'].default_value = (*color, 1)
    p.inputs['Metallic'].default_value = metallic
    p.inputs['Roughness'].default_value = .55
    return m

def box(name, loc, size, mat, bevel=0):
    bpy.ops.mesh.primitive_cube_add(size=1, location=loc)
    o = bpy.context.object
    o.name = name
    o.dimensions = size
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    o.data.materials.append(mat)
    if bevel:
        b = o.modifiers.new('Soft edges', 'BEVEL'); b.width = bevel; b.segments = 3
        o.modifiers.new('Weighted normals', 'WEIGHTED_NORMAL')
    return o

wall = material('Warm plaster', (.83, .80, .73))
wood = material('Oak', (.43, .24, .11))
floor = material('Light oak flooring', (.66, .46, .27))
trim = material('Ivory trim', (.95, .93, .85))
fabric = material('Sage upholstery', (.22, .35, .30))
dark = material('Dark metal', (.055, .065, .07), .65)
rug = material('Sand rug', (.68, .61, .49))
glass = material('Pale blue glazing', (.38, .66, .77), .25)
# Interior spans x=-2..2 and y=-2.5..2.5; two walls omitted for viewing.
box('Floor slab 4 by 5 meters', (0, 0, -.12), (4.2, 5.2, .24), floor)
for i in range(1, 16):
    box('Floorboard joint %02d' % i, (-2+i*.25, 0, .003), (.008, 5, .006), wood)
# Back wall has a genuine one-meter doorway from x=-1.55 to -.55.
box('Door wall left pier', (-1.825, 2.6, 1.4), (.55, .2, 2.8), wall)
box('Door wall right pier', (.725, 2.6, 1.4), (2.55, .2, 2.8), wall)
box('Door lintel', (-1.05, 2.6, 2.5), (1, .2, .6), wall)
for x in (-1.58, -.52):
    box('Door jamb', (x, 2.47, 1.1), (.07, .1, 2.2), trim)
box('Door casing header', (-1.05, 2.47, 2.22), (1.13, .1, .08), trim)
box('Door threshold', (-1.05, 2.6, .02), (1, .3, .04), wood)
# Left wall window opening: y=-1.25..1.05, z=.95..2.25.
box('Window wall front pier', (-2.1, -1.875, 1.4), (.2, 1.25, 2.8), wall)
box('Window wall rear pier', (-2.1, 1.775, 1.4), (.2, 1.45, 2.8), wall)
box('Window wall below opening', (-2.1, -.1, .475), (.2, 2.3, .95), wall)
box('Window wall above opening', (-2.1, -.1, 2.525), (.2, 2.3, .55), wall)
box('Window glazing', (-2.105, -.1, 1.6), (.025, 2.22, 1.22), glass)
for y in (-1.25, -.1, 1.05):
    box('Window vertical frame', (-2.04, y, 1.6), (.11, .055, 1.35), trim)
for z in (.95, 2.25):
    box('Window horizontal frame', (-2.04, -.1, z), (.11, 2.38, .07), trim)
box('Projecting window sill', (-1.94, -.1, .94), (.4, 2.5, .07), trim, .015)
box('Area rug', (.35, -.5, .025), (2.6, 2.8, .035), rug, .035)
box('Sofa plinth', (.65, 1.7, .19), (2.05, .85, .24), wood, .025)
box('Sofa back', (.65, 2.04, .74), (2.25, .24, .98), fabric, .08)
for x in (-.4, 1.7):
    box('Sofa arm', (x, 1.7, .59), (.22, .9, .68), fabric, .07)
for x in (.12, 1.16):
    box('Seat cushion', (x, 1.59, .49), (.99, .68, .2), fabric, .06)
box('Coffee table top', (.5, -.1, .49), (1.35, .7, .085), wood, .035)
for x in (-.02, 1.02):
    for y in (-.34, .14):
        box('Coffee table leg', (x, y, .25), (.055, .055, .45), dark)
box('Book cover', (.68, -.05, .552), (.32, .23, .035), trim, .008)
box('Low cabinet', (-1.53, -1.85, .44), (.65, 1, .82), wood, .025)
for y in (-2.1, -1.6):
    box('Cabinet door', (-1.19, y, .46), (.035, .46, .72), trim, .008)
    box('Cabinet handle', (-1.16, y, .61), (.04, .15, .025), dark)
box('Wall artwork frame', (.9, 2.47, 1.94), (.95, .06, .64), wood, .015)
box('Wall artwork inset', (.9, 2.429, 1.94), (.82, .015, .51), fabric)
bpy.ops.object.camera_add(location=(7, -9, 7))
camera = bpy.context.object
camera.rotation_euler = (Vector((0, .2, 1))-camera.location).to_track_quat('-Z', 'Y').to_euler()
camera.data.type = 'ORTHO'; camera.data.ortho_scale = 8.6
bpy.context.scene.camera = camera
bpy.ops.object.light_add(type='AREA', location=(1, -2, 6))
bpy.context.object.data.energy = 1100
bpy.context.object.data.shape = 'DISK'; bpy.context.object.data.size = 5
bpy.context.scene.world.color = (.25, .25, .25)
