import bpy, math
from mathutils import Vector

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

walnut = material('Walnut joinery', (0.22, 0.105, 0.052))
stone = material('Cream countertop stone', (0.82, 0.78, 0.66))
brass = material('Satin brass', (0.64, 0.43, 0.17), 0.8, 0.27)
plaster = material('Warm plaster', (0.68, 0.64, 0.55))
floor = material('Travertine floor', (0.46, 0.44, 0.38))
teal = material('Teal upholstery', (0.055, 0.22, 0.23))
dark = material('Charcoal metal', (0.035, 0.045, 0.048), 0.5)
screen = material('Monitor glass', (0.045, 0.12, 0.15), 0.2, 0.2)
leaf = material('Plant leaves', (0.08, 0.24, 0.1))
soil = material('Potting soil', (0.055, 0.035, 0.02))

def box(name, loc, dims, mat, bevel=0.02):
    bpy.ops.mesh.primitive_cube_add(size=1, location=loc)
    o = bpy.context.object
    o.name = name
    o.dimensions = dims
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    o.data.materials.append(mat)
    if bevel:
        b = o.modifiers.new('Rounded edges', 'BEVEL')
        b.width = bevel
        b.segments = 3
        o.modifiers.new('Weighted normals', 'WEIGHTED_NORMAL')
    return o

def cylinder(name, loc, radius, depth, mat):
    bpy.ops.mesh.primitive_cylinder_add(vertices=32, radius=radius, depth=depth, location=loc)
    o = bpy.context.object
    o.name = name
    o.data.materials.append(mat)
    b = o.modifiers.new('Edge easing', 'BEVEL')
    b.width = 0.012
    b.segments = 2
    o.modifiers.new('Weighted normals', 'WEIGHTED_NORMAL')
    return o

def text(name, body, loc, size, mat):
    curve = bpy.data.curves.new(name, 'FONT')
    curve.body = body
    curve.align_x = 'CENTER'
    curve.size = size
    curve.extrude = 0.007
    curve.bevel_depth = 0.001
    o = bpy.data.objects.new(name, curve)
    bpy.context.collection.objects.link(o)
    o.location = loc
    o.rotation_euler = (math.pi/2, 0, 0)
    o.data.materials.append(mat)
    return o

box('Lobby floor', (0,0,-0.08), (8,6,0.16), floor)
box('Reception back wall', (0,2.35,1.9), (8,0.18,3.8), plaster)
box('Wall skirting', (0,2.235,0.09), (8,0.05,0.18), walnut)
box('Walnut sign panel', (-1.15,2.225,2.3), (3.8,0.08,2.1), walnut)
text('Hotel wall name', 'THE ATRIUM', (-1.15,2.17,2.55), 0.37, brass)
text('Hotel wall subtitle', 'H O T E L   &   S U I T E S', (-1.15,2.17,2.13), 0.13, stone)
box('Sign underline', (-1.15,2.16,1.99), (1.8,0.018,0.014), brass, 0.003)
# Guest-facing desk with a lower worktop behind its raised transaction ledge.
box('Desk recessed plinth', (-1.15,0.35,0.1), (3.3,0.96,0.2), dark)
box('Desk front structure', (-1.15,-0.13,0.65), (3.5,0.18,1.12), walnut)
for i in range(28):
    box('Front walnut flute %02d' % (i+1), (-2.84+i*0.125,-0.238,0.66), (0.063,0.075,1.04), walnut, 0.009)
for x in (-2.85,0.55):
    box('Desk end panel', (x,0.4,0.65), (0.1,1.15,1.1), walnut)
box('Raised stone transaction ledge', (-1.15,-0.1,1.24), (3.68,0.56,0.11), stone)
box('Staff work surface', (-1.15,0.57,0.83), (3.32,0.73,0.065), stone)
box('Desk brass base trim', (-1.15,-0.283,0.16), (3.48,0.025,0.035), brass, 0.004)
box('Monitor foot', (-1.1,0.58,0.882), (0.36,0.24,0.04), dark)
box('Monitor stand', (-1.1,0.56,1.06), (0.045,0.055,0.33), dark)
box('Reception monitor', (-1.1,0.52,1.22), (0.65,0.06,0.4), dark)
box('Staff-facing screen', (-1.1,0.555,1.22), (0.6,0.008,0.35), screen, 0.005)
box('Keyboard', (-1.1,0.8,0.875), (0.46,0.16,0.025), dark, 0.005)
cylinder('Service bell base', (-2.3,-0.12,1.315), 0.095, 0.025, dark)
bpy.ops.mesh.primitive_uv_sphere_add(segments=24, ring_count=12, radius=1, location=(-2.3,-0.12,1.335))
bell = bpy.context.object
bell.name = 'Brass service bell dome'
bell.scale = (0.075,0.075,0.045)
bell.data.materials.append(brass)
cylinder('Service bell button', (-2.3,-0.12,1.39), 0.018, 0.025, brass)

def chair(name, x, y):
    for dx in (-0.3,0.3):
        for dy in (-0.29,0.29):
            box(name+' leg', (x+dx,y+dy,0.22), (0.045,0.045,0.44), brass, 0.008)
    box(name+' seat', (x,y,0.48), (0.78,0.76,0.18), teal, 0.08)
    box(name+' backrest', (x,y+0.32,0.87), (0.8,0.18,0.72), teal, 0.075)
    for dx in (-0.39,0.39):
        box(name+' armrest', (x+dx,y,0.69), (0.13,0.78,0.27), teal, 0.055)

chair('Lounge chair A', 1.7,0.9)
chair('Lounge chair B', 3.0,0.9)
cylinder('Side table pedestal', (2.35,-0.15,0.28), 0.055, 0.52, brass)
cylinder('Side table base', (2.35,-0.15,0.035), 0.24, 0.05, dark)
cylinder('Round stone side table', (2.35,-0.15,0.56), 0.37, 0.06, stone)
box('Guest information booklet', (2.34,-0.15,0.6), (0.24,0.18,0.02), walnut, 0.004)
cylinder('Lobby planter', (-3.35,1.5,0.31), 0.29, 0.62, stone)
cylinder('Visible soil', (-3.35,1.5,0.623), 0.26, 0.018, soil)
for i in range(9):
    a = i*2.4
    cylinder('Plant stem', (-3.35,1.5,0.97), 0.012, 0.7, walnut)
    bpy.ops.mesh.primitive_uv_sphere_add(segments=12, ring_count=8, radius=1, location=(-3.35+0.2*math.cos(a),1.5+0.2*math.sin(a),1.12+(i%3)*0.18))
    o = bpy.context.object
    o.name = 'Decorative plant leaf %02d' % i
    o.scale = (0.1,0.12,0.38)
    o.rotation_euler = (0.55*math.sin(a),0.55*math.cos(a),a)
    o.data.materials.append(leaf)

bpy.context.scene.world = bpy.data.worlds.new('Lobby ambient')
bpy.context.scene.world.use_nodes = True
bpy.context.scene.world.node_tree.nodes['Background'].inputs[1].default_value = 0.35
for loc, energy, size in [((0,-3,5.5),1400,5), ((-3,1,4.6),650,3), ((3,0,4.7),650,3)]:
    bpy.ops.object.light_add(type='AREA', location=loc)
    o = bpy.context.object
    o.name = 'Lobby soft lighting'
    o.data.energy = energy
    o.data.size = size
    o.rotation_euler = (Vector((0,0.5,1))-o.location).to_track_quat('-Z','Y').to_euler()
bpy.ops.object.camera_add(location=(7,-10,6))
camera = bpy.context.object
camera.name = 'Reception overview camera'
camera.rotation_euler = (Vector((0,0.65,1.55))-camera.location).to_track_quat('-Z','Y').to_euler()
camera.data.lens = 46
bpy.context.scene.camera = camera
