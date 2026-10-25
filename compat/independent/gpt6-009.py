import bpy, math
from mathutils import Vector
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)

def material(name, color, metal=0):
    m = bpy.data.materials.new(name); m.diffuse_color = (*color, 1)
    m.use_nodes = True
    p = m.node_tree.nodes.get('Principled BSDF')
    p.inputs['Base Color'].default_value = (*color, 1)
    p.inputs['Metallic'].default_value = metal
    p.inputs['Roughness'].default_value = .65
    return m

def box(name, loc, size, mat, bevel=0):
    bpy.ops.mesh.primitive_cube_add(size=1, location=loc)
    o = bpy.context.object; o.name = name; o.dimensions = size
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    o.data.materials.append(mat)
    if bevel:
        b = o.modifiers.new('Eased edges', 'BEVEL'); b.width = bevel; b.segments = 2
        o.modifiers.new('Weighted normals', 'WEIGHTED_NORMAL')
    return o

def beam(name, a, b, width, depth, mat):
    a, b = Vector(a), Vector(b)
    o = box(name, (a+b)/2, (width, depth, (b-a).length), mat, .008)
    o.rotation_euler = (b-a).to_track_quat('Z', 'Y').to_euler()
    return o

wood = material('Cedar decking', (.46, .25, .115))
wood2 = material('Alternate cedar boards', (.55, .32, .16))
steel = material('Charcoal steel', (.075, .1, .105), .7)
boltmat = material('Galvanized bolts', (.52, .57, .58), .8)
stone = material('Concrete abutments', (.48, .47, .42))
earth = material('River banks', (.28, .33, .19))
water = material('Stream blue green', (.10, .28, .30), .25)
# Compact landscape section with a 4.6-meter clear stream crossing.
box('Stream surface', (0, 0, -.38), (4.6, 5, .08), water, .03)
for x in (-3.05, 3.05):
    box('Approach bank', (x, 0, -.18), (1.5, 5, .44), earth, .07)
for x in (-2.35, 2.35):
    box('Concrete abutment', (x, 0, -.03), (.5, 2.3, .5), stone, .025)
for y in (-.70, .70):
    box('Longitudinal steel deck girder', (0, y, .24), (5.1, .13, .25), steel, .012)
for x in (-2.25, -1.125, 0, 1.125, 2.25):
    box('Underdeck crossmember', (x, 0, .25), (.1, 1.8, .16), steel, .008)
for i in range(25):
    x = -2.4+i*.2
    box('Deck plank %02d' % (i+1), (x, 0, .415), (.188, 1.9, .1), wood if i%3 else wood2, .008)
    for y in (-.7, .7):
        bpy.ops.mesh.primitive_cylinder_add(vertices=12, radius=.014, depth=.004, location=(x, y, .467))
        o = bpy.context.object; o.name = 'Deck screw'; o.data.materials.append(boltmat)
for side in (-1, 1):
    y = side*.99
    for i, x in enumerate((-2.4, -1.2, 0, 1.2, 2.4)):
        box('Railing post %s %d' % (side, i), (x, y, .99), (.085, .085, 1.18), steel, .009)
        box('Post mounting shoe', (x, y, .43), (.18, .16, .06), steel, .01)
        box('Post cap', (x, y, 1.595), (.105, .105, .025), boltmat, .007)
    box('Cedar handrail side %s' % side, (0, y, 1.64), (5.08, .135, .09), wood, .025)
    for z in (.61, 1.43):
        box('Horizontal guard rail', (0, y, z), (4.8, .045, .045), steel, .006)
    for i in range(40):
        x = -2.34+i*.12
        box('Vertical guard infill', (x, y, 1.02), (.022, .022, .8), steel, .003)
# Short sloped timber approaches meet the raised bridge deck.
for side in (-1, 1):
    beam('Approach ramp stringer', (side*2.5, -.7, .34), (side*3.55, -.7, .07), .09, .14, steel)
    beam('Approach ramp stringer', (side*2.5, .7, .34), (side*3.55, .7, .07), .09, .14, steel)
    for i in range(6):
        d = (i+.5)*1.05/6
        o = box('Approach ramp plank', (side*(2.5+d), 0, .415-d*.27/1.05), (.18, 1.9, .08), wood, .007)
        o.rotation_euler.y = side*math.atan(.27/1.05)
bpy.ops.object.camera_add(location=(8, -10, 6.5))
cam = bpy.context.object
cam.rotation_euler = (Vector((0, 0, .55))-cam.location).to_track_quat('-Z', 'Y').to_euler()
cam.data.type = 'ORTHO'; cam.data.ortho_scale = 10
bpy.context.scene.camera = cam
bpy.ops.object.light_add(type='AREA', location=(1, -3, 7))
bpy.context.object.data.energy = 1600; bpy.context.object.data.size = 5
bpy.context.scene.world.color = (.28, .28, .28)
