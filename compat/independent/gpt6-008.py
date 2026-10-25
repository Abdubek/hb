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
    p.inputs['Roughness'].default_value = .4 if metal else .75
    return m

def box(name, loc, size, mat, bevel=0):
    bpy.ops.mesh.primitive_cube_add(size=1, location=loc)
    o = bpy.context.object; o.name = name; o.dimensions = size
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    o.data.materials.append(mat)
    if bevel:
        b = o.modifiers.new('Edge radii', 'BEVEL'); b.width = bevel; b.segments = 3
        o.modifiers.new('Weighted normals', 'WEIGHTED_NORMAL')
    return o

def cylinder(name, loc, radius, depth, mat, vertices=32):
    bpy.ops.mesh.primitive_cylinder_add(vertices=vertices, radius=radius, depth=depth, location=loc)
    o = bpy.context.object; o.name = name; o.data.materials.append(mat)
    return o

metal = material('Graphite aluminum', (.07, .085, .10), .75)
steel = material('Stainless fasteners', (.48, .51, .54), .9)
stone = material('Pale concrete pavers', (.57, .57, .53))
edge = material('Dark curb stone', (.29, .31, .32))
grout = material('Paver joints', (.16, .17, .17))
lens = material('LED diffuser', (.91, .96, 1))
p = lens.node_tree.nodes.get('Principled BSDF')
p.inputs['Emission Color'].default_value = (.78, .89, 1, 1)
p.inputs['Emission Strength'].default_value = 2
box('Square pavement foundation', (0, 0, -.14), (3, 3, .28), edge, .025)
box('Mortar bed', (0, 0, -.025), (2.83, 2.83, .07), grout)
for i in range(5):
    for j in range(5):
        box('Paving slab %d %d' % (i, j), ((i-2)*.55, (j-2)*.55, .012), (.536, .536, .065), stone, .008)
box('Pole anchor plate', (0, 0, .085), (.43, .43, .075), metal, .025)
for x in (-.145, .145):
    for y in (-.145, .145):
        cylinder('Anchor washer', (x, y, .131), .032, .012, steel)
        cylinder('Hex anchor nut', (x, y, .149), .024, .025, steel, 6)
# Slender tapered five-meter pole.
bpy.ops.mesh.primitive_cone_add(vertices=40, radius1=.115, radius2=.065, depth=4.85, location=(0, 0, 2.545))
pole = bpy.context.object; pole.name = 'Tapered streetlight mast'; pole.data.materials.append(metal)
for f in pole.data.polygons: f.use_smooth = len(f.vertices) == 4
cylinder('Base collar', (0, 0, .245), .135, .25, metal)
box('Service access hatch', (0, -.112, .68), (.115, .018, .3), metal, .015)
for z in (.57, .79):
    screw = cylinder('Hatch screw', (0, -.126, z), .009, .009, steel, 12)
    screw.rotation_euler.x = math.pi/2
box('Cantilever arm', (.52, 0, 4.94), (1.14, .12, .12), metal, .035)
box('Luminaire upper housing', (1.16, 0, 4.925), (.88, .34, .13), metal, .055)
box('Recessed lens bezel', (1.19, 0, 4.854), (.71, .28, .035), steel, .016)
box('LED optical diffuser', (1.19, 0, 4.832), (.65, .23, .019), lens, .012)
for i in range(7):
    box('Top cooling fin %02d' % i, (.87+i*.09, 0, 5.008), (.023, .25, .055), metal, .006)
bpy.ops.object.light_add(type='AREA', location=(1.19, 0, 4.81))
l = bpy.context.object; l.name = 'Downward streetlight illumination'
l.data.energy = 70; l.data.shape = 'RECTANGLE'; l.data.size = .6; l.data.size_y = .2
bpy.ops.object.camera_add(location=(8, -10, 7))
cam = bpy.context.object
cam.rotation_euler = (Vector((.3, 0, 2.35))-cam.location).to_track_quat('-Z', 'Y').to_euler()
cam.data.type = 'ORTHO'; cam.data.ortho_scale = 7.2
bpy.context.scene.camera = cam
bpy.ops.object.light_add(type='AREA', location=(2, -4, 8))
bpy.context.object.data.energy = 1700; bpy.context.object.data.size = 5
bpy.context.scene.world.color = (.3, .3, .3)
