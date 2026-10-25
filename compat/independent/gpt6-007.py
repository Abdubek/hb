import bpy, math
from mathutils import Vector
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)

def material(name, color, metal=0):
    m = bpy.data.materials.new(name)
    m.diffuse_color = (*color, 1)
    m.use_nodes = True
    p = m.node_tree.nodes.get('Principled BSDF')
    p.inputs['Base Color'].default_value = (*color, 1)
    p.inputs['Metallic'].default_value = metal
    p.inputs['Roughness'].default_value = .35 if metal else .8
    return m

def box(name, loc, size, mat, bevel=0):
    bpy.ops.mesh.primitive_cube_add(size=1, location=loc)
    o = bpy.context.object; o.name = name; o.dimensions = size
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    o.data.materials.append(mat)
    if bevel:
        mod = o.modifiers.new('Rounded edges', 'BEVEL'); mod.width = bevel; mod.segments = 3
        o.modifiers.new('Weighted normals', 'WEIGHTED_NORMAL')
    return o

def cylinder(name, loc, radius, depth, mat, vertices=24):
    bpy.ops.mesh.primitive_cylinder_add(vertices=vertices, radius=radius, depth=depth, location=loc)
    o = bpy.context.object; o.name = name; o.data.materials.append(mat)
    return o

def tube(name, points, radius, mat):
    c = bpy.data.curves.new(name, 'CURVE'); c.dimensions = '3D'
    c.bevel_depth = radius; c.bevel_resolution = 3; c.use_fill_caps = True
    s = c.splines.new('POLY'); s.points.add(len(points)-1)
    for p, co in zip(s.points, points): p.co = (*co, 1)
    o = bpy.data.objects.new(name, c); bpy.context.collection.objects.link(o)
    o.data.materials.append(mat)
    return o

steel = material('Brushed stainless steel', (.48, .55, .59), .85)
base = material('Charcoal powder coating', (.065, .085, .10), .6)
concrete = material('Concrete', (.48, .47, .43))
paint = material('Bay marking cream', (.88, .82, .55))
# Five spaced inverted-U locking stands, one for each designated bicycle bay.
box('Concrete parking pad', (0, 0, -.09), (5.7, 3.5, .18), concrete, .04)
for y in (-.45, .45):
    box('Shared mounting rail', (0, y, .055), (4.7, .15, .11), base, .02)
for i in range(5):
    x = (i-2)*1.0
    pts = [(x, -.45, .11), (x, -.45, .85)]
    # Quarter circles connect vertical legs to the horizontal crown.
    for j in range(9):
        a = math.pi-j*math.pi/16
        pts.append((x, -.3+.15*math.cos(a), .85+.15*math.sin(a)))
    pts.append((x, .3, 1.0))
    for j in range(1, 9):
        a = math.pi/2-j*math.pi/16
        pts.append((x, .3+.15*math.cos(a), .85+.15*math.sin(a)))
    pts.append((x, .45, .11))
    tube('Bicycle bay %d locking hoop' % (i+1), pts, .032, steel)
    for y in (-.45, .45):
        box('Bay %d footplate' % (i+1), (x, y, .125), (.23, .23, .03), steel, .015)
        for dx in (-.075, .075):
            cylinder('Anchor bolt', (x+dx, y, .154), .021, .026, base, 6)
    # Ground stripes define a bicycle-sized space alongside each stand.
    for dx in (-.42, .42):
        box('Bay %d painted boundary' % (i+1), (x+dx, 0, .003), (.035, 2.8, .006), paint)
    bpy.ops.object.text_add(location=(x, -1.4, .009))
    t = bpy.context.object; t.name = 'Ground bay number %d' % (i+1)
    t.data.body = str(i+1); t.data.align_x = 'CENTER'; t.data.size = .23
    t.data.extrude = .001; t.data.materials.append(paint)
# End caps make the shared structural rails visibly closed.
for x in (-2.36, 2.36):
    for y in (-.45, .45):
        box('Rail end cap', (x, y, .055), (.025, .16, .12), steel, .006)
bpy.ops.object.camera_add(location=(7, -7, 5))
cam = bpy.context.object
cam.rotation_euler = (Vector((0, 0, .3))-cam.location).to_track_quat('-Z', 'Y').to_euler()
cam.data.type = 'ORTHO'; cam.data.ortho_scale = 7.5
bpy.context.scene.camera = cam
bpy.ops.object.light_add(type='AREA', location=(1, -3, 6))
bpy.context.object.data.energy = 1400; bpy.context.object.data.size = 5
bpy.context.scene.world.color = (.25, .25, .25)
