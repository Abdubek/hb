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
    p.inputs['Roughness'].default_value = .38 if metal else .6
    return m

def box(name, loc, size, mat, bevel=0):
    bpy.ops.mesh.primitive_cube_add(size=1, location=loc)
    o = bpy.context.object; o.name = name; o.dimensions = size
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    o.data.materials.append(mat)
    if bevel:
        b = o.modifiers.new('Soft edges', 'BEVEL'); b.width = bevel; b.segments = 3
        o.modifiers.new('Weighted normals', 'WEIGHTED_NORMAL')
    return o

def cylinder(name, loc, radius, depth, mat):
    bpy.ops.mesh.primitive_cylinder_add(vertices=32, radius=radius, depth=depth, location=loc)
    o = bpy.context.object; o.name = name; o.data.materials.append(mat)
    b = o.modifiers.new('Rim bevel', 'BEVEL'); b.width = .008; b.segments = 2
    o.modifiers.new('Weighted normals', 'WEIGHTED_NORMAL')
    return o

def rod(name, a, b, radius, mat):
    a, b = Vector(a), Vector(b)
    o = cylinder(name, (a+b)/2, radius, (b-a).length, mat)
    o.rotation_euler = (b-a).to_track_quat('Z', 'Y').to_euler()
    return o

navy = material('Deep blue cabinetry', (.065, .13, .18))
quartz = material('Warm white quartz', (.89, .87, .81))
wood = material('Oak stool seats', (.48, .28, .13))
metal = material('Blackened steel', (.045, .05, .055), .7)
brass = material('Satin brass', (.58, .38, .14), .75)
floor = material('Warm concrete floor', (.52, .49, .44))
ceramic = material('Cream ceramic', (.82, .78, .66))
glow = material('Pendant diffuser', (1, .87, .64))
p = glow.node_tree.nodes.get('Principled BSDF')
p.inputs['Emission Color'].default_value = (1, .78, .45, 1)
p.inputs['Emission Strength'].default_value = 2
box('Kitchen floor display platform', (0, 0, -.09), (5, 4.3, .18), floor, .035)
box('Recessed island toe kick', (0, .18, .085), (2.7, .79, .17), metal, .012)
box('Island cabinet carcass', (0, .18, .51), (2.9, .94, .78), navy, .015)
box('Quartz island countertop', (0, -.04, .95), (3.12, 1.46, .10), quartz, .025)
# Storage faces the rear working aisle; the front has a knee-space overhang.
for i in range(3):
    x = (i-1)*.96
    for z, h in ((.745, .25), (.38, .45)):
        box('Cabinet drawer %d %.2f' % (i, z), (x, .668, z), (.92, .035, h), navy, .01)
        rod('Brass drawer pull', (x-.16, .71, z+.045), (x+.16, .71, z+.045), .012, brass)
        for dx in (-.14, .14):
            rod('Handle standoff', (x+dx, .68, z+.045), (x+dx, .71, z+.045), .01, brass)
for x in (-1.46, 1.46):
    box('Island end panel', (x, .18, .51), (.035, .95, .78), navy, .012)
for i in range(15):
    box('Front decorative oak slat', (-1.34+i*.192, -.304, .51), (.055, .022, .72), wood, .006)
for index, x in enumerate((-1, 0, 1)):
    y = -1.26
    cylinder('Stool %d round oak seat' % (index+1), (x, y, .665), .275, .075, wood)
    for sx in (-1, 1):
        for sy in (-1, 1):
            rod('Stool %d splayed leg' % (index+1), (x+sx*.23, y+sy*.23, .025), (x+sx*.15, y+sy*.15, .63), .023, metal)
    for sy in (-1, 1):
        rod('Stool footrest', (x-.205, y+sy*.205, .25), (x+.205, y+sy*.205, .25), .016, brass)
    for sx in (-1, 1):
        rod('Stool side stretcher', (x+sx*.205, y-.205, .25), (x+sx*.205, y+.205, .25), .014, metal)
# A ceiling canopy supports three suspended modern pendants.
box('Pendant ceiling canopy', (0, 0, 2.85), (2.6, .23, .065), metal, .025)
for i, x in enumerate((-1, 0, 1)):
    rod('Pendant %d suspension cable' % (i+1), (x, 0, 2.81), (x, 0, 2.16), .008, metal)
    cylinder('Pendant brass neck', (x, 0, 2.16), .044, .11, brass)
    bpy.ops.mesh.primitive_cone_add(vertices=48, radius1=.235, radius2=.095, depth=.25, location=(x, 0, 1.995))
    o = bpy.context.object; o.name = 'Pendant %d shade' % (i+1); o.data.materials.append(metal)
    cylinder('Pendant luminous underside', (x, 0, 1.868), .212, .016, glow)
    bpy.ops.object.light_add(type='AREA', location=(x, 0, 1.85))
    l = bpy.context.object; l.name = 'Pendant downlight'; l.data.energy = 35; l.data.size = .35
box('Oak cutting board', (.91, .22, 1.02), (.49, .35, .035), wood, .025)
cylinder('Ceramic fruit platter', (-.6, .12, 1.025), .24, .045, ceramic)
for x, y in ((-.69, .08), (-.48, .1), (-.59, .24)):
    bpy.ops.mesh.primitive_uv_sphere_add(segments=16, ring_count=8, radius=.065, location=(x, y, 1.09))
    bpy.context.object.name = 'Decorative fruit'; bpy.context.object.data.materials.append(brass)
bpy.ops.object.camera_add(location=(6, -7, 5))
cam = bpy.context.object
cam.rotation_euler = (Vector((0, -.1, 1.15))-cam.location).to_track_quat('-Z', 'Y').to_euler()
cam.data.type = 'ORTHO'; cam.data.ortho_scale = 6.7
bpy.context.scene.camera = cam
bpy.ops.object.light_add(type='AREA', location=(1, -3, 6))
bpy.context.object.data.energy = 1100; bpy.context.object.data.size = 4
bpy.context.scene.world.color = (.25, .25, .25)
