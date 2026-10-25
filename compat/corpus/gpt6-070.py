import bpy, math
from mathutils import Vector

bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)

def mat(name, color, metal=0, rough=0.45):
    m = bpy.data.materials.new(name)
    m.diffuse_color = (*color, 1)
    m.use_nodes = True
    p = m.node_tree.nodes.get('Principled BSDF')
    p.inputs['Base Color'].default_value = (*color, 1)
    p.inputs['Metallic'].default_value = metal
    p.inputs['Roughness'].default_value = rough
    return m

def finish(o, name, m, bevel=0):
    o.name = name
    o.data.materials.append(m)
    if bevel:
        mod = o.modifiers.new('Small edge bevel', 'BEVEL')
        mod.width = bevel
        mod.segments = 3
        o.modifiers.new('Weighted normals', 'WEIGHTED_NORMAL')
    return o

def box(name, loc, dim, m, bevel=0.01):
    bpy.ops.mesh.primitive_cube_add(size=1, location=loc)
    o = bpy.context.object
    o.dimensions = dim
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    return finish(o, name, m, bevel)

def rod(name, a, b, radius, m, vertices=32):
    a, b = Vector(a), Vector(b)
    bpy.ops.mesh.primitive_cylinder_add(vertices=vertices, radius=radius, depth=(b-a).length, location=(a+b)/2)
    o = bpy.context.object
    o.rotation_euler = (b-a).to_track_quat('Z', 'Y').to_euler()
    for p in o.data.polygons:
        p.use_smooth = len(p.vertices) == 4
    return finish(o, name, m, 0.004)

def ball(name, loc, r, m):
    bpy.ops.mesh.primitive_uv_sphere_add(segments=24, ring_count=12, radius=r, location=loc)
    o = bpy.context.object
    for p in o.data.polygons:
        p.use_smooth = True
    return finish(o, name, m)

def lathe(name, x, y, z, profile, m, sides=40):
    verts = []
    for radius, height in profile:
        for j in range(sides):
            a = j*2*math.pi/sides
            verts.append((radius*math.cos(a), radius*math.sin(a), height))
    faces = [tuple(reversed(range(sides)))]
    for i in range(len(profile)-1):
        for j in range(sides):
            nj = (j+1)%sides
            faces.append((i*sides+j, i*sides+nj, (i+1)*sides+nj, (i+1)*sides+j))
    faces.append(tuple((len(profile)-1)*sides+j for j in range(sides)))
    mesh = bpy.data.meshes.new(name)
    mesh.from_pydata(verts, [], faces)
    mesh.update()
    o = bpy.data.objects.new(name, mesh)
    bpy.context.collection.objects.link(o)
    o.location = (x, y, z)
    for p in mesh.polygons:
        p.use_smooth = len(p.vertices) == 4
    return finish(o, name, m, 0.003)

walnut = mat('Walnut table frame', (0.18, 0.073, 0.028), 0, 0.36)
darkwood = mat('Dark stained apron', (0.078, 0.032, 0.017), 0, 0.42)
maple = mat('Maple light squares', (0.72, 0.56, 0.35), 0, 0.43)
ebony = mat('Ebony dark squares', (0.08, 0.12, 0.12), 0, 0.4)
ivory = mat('Ivory chess pieces', (0.88, 0.83, 0.68), 0.06, 0.28)
black = mat('Black chess pieces', (0.026, 0.036, 0.044), 0.15, 0.27)
brass = mat('Brass inlay and feet', (0.59, 0.37, 0.11), 0.8, 0.28)
felt = mat('Green felt piece bases', (0.022, 0.09, 0.05), 0, 0.9)
floor = mat('Warm studio floor', (0.28, 0.25, 0.22), 0, 0.82)
box('Floor', (0, 0, -0.075), (200, 200, 0.1), floor, 0)
# Wood grain generated entirely with shader nodes.
for m in [walnut, maple]:
    nt = m.node_tree
    tex = nt.nodes.new('ShaderNodeTexNoise')
    tex.inputs['Scale'].default_value = 5
    tex.inputs['Detail'].default_value = 2
    coord = nt.nodes.new('ShaderNodeTexCoord')
    mapping = nt.nodes.new('ShaderNodeVectorMath')
    mapping.operation = 'MULTIPLY'
    mapping.inputs[1].default_value = (3, 65, 8)
    nt.links.new(coord.outputs['Generated'], mapping.inputs[0])
    nt.links.new(mapping.outputs['Vector'], tex.inputs['Vector'])
    bump = nt.nodes.new('ShaderNodeBump')
    bump.inputs['Strength'].default_value = 0.14
    bump.inputs['Distance'].default_value = 0.014
    nt.links.new(tex.outputs['Fac'], bump.inputs['Height'])
    nt.links.new(bump.outputs['Normal'], nt.nodes.get('Principled BSDF').inputs['Normal'])

box('Thick square tabletop', (0, 0, 2.105), (3.62, 3.62, 0.20), walnut, 0.055)
box('Under top molding', (0, 0, 1.99), (3.49, 3.49, 0.07), darkwood, 0.025)
for y in [-1.46, 1.46]:
    box('Long table apron', (0, y, 1.81), (3.06, 0.12, 0.32), darkwood, 0.015)
for x in [-1.46, 1.46]:
    box('Side table apron', (x, 0, 1.81), (0.12, 3.06, 0.32), darkwood, 0.015)
# Square tapered legs with small brass ferrules.
for x in [-1.45, 1.45]:
    for y in [-1.45, 1.45]:
        verts = []
        for z, half in [(0.055, 0.070), (1.99, 0.125)]:
            verts.extend([(x-half, y-half, z), (x+half, y-half, z), (x+half, y+half, z), (x-half, y+half, z)])
        mesh = bpy.data.meshes.new('Tapered leg mesh')
        mesh.from_pydata(verts, [], [(3,2,1,0), (4,5,6,7), (0,1,5,4), (1,2,6,5), (2,3,7,6), (3,0,4,7)])
        mesh.update()
        o = bpy.data.objects.new('Tapered walnut table leg', mesh)
        bpy.context.collection.objects.link(o)
        finish(o, o.name, walnut, 0.012)
        box('Brass leg ferrule', (x, y, 0.11), (0.151, 0.151, 0.17), brass, 0.012)
# Flush inset 8x8 board. a1 is dark and h1 is light.
square = 0.375
board_top = 2.218
for rank in range(8):
    for file in range(8):
        x = (file-3.5)*square
        y = (rank-3.5)*square
        box('Square '+chr(97+file)+str(rank+1), (x, y, 2.211), (square, square, 0.014), ebony if (file+rank)%2 == 0 else maple, 0.001)
for v in [-1.513, 1.513]:
    box('Board brass border horizontal', (0, v, 2.214), (3.05, 0.018, 0.009), brass, 0.002)
    box('Board brass border vertical', (v, 0, 2.214), (0.018, 3.05, 0.009), brass, 0.002)

def flat_text(body, loc, rotation=0):
    c = bpy.data.curves.new('Board coordinate '+body, 'FONT')
    c.body = body
    c.size = 0.085
    c.align_x = 'CENTER'
    c.align_y = 'CENTER'
    o = bpy.data.objects.new('Inlaid coordinate '+body, c)
    bpy.context.collection.objects.link(o)
    o.location = loc
    o.rotation_euler.z = rotation
    c.materials.append(brass)
for i in range(8):
    p = (i-3.5)*square
    flat_text(chr(65+i), (p, -1.635, 2.209))
    flat_text(chr(65+i), (p, 1.635, 2.209), math.pi)
    flat_text(str(i+1), (-1.635, p, 2.209), -math.pi/2)
    flat_text(str(i+1), (1.635, p, 2.209), math.pi/2)

# Thirty-two complete geometric pieces in the standard starting position.
def piece(kind, file, rank, m, side):
    x, y, z = (file-3.5)*square, (rank-3.5)*square, board_top
    name = side+' '+kind+' '+chr(97+file)+str(rank+1)
    radius = 0.112 if kind == 'Pawn' else 0.133
    rod(name+' felt sole', (x, y, z+0.002), (x, y, z+0.009), radius*0.94, felt)
    profile = [(radius*0.90, 0.009), (radius, 0.022), (radius, 0.047), (radius*0.88, 0.063), (radius*0.85, 0.079), (radius*0.61, 0.098)]
    if kind == 'Pawn':
        profile += [(0.043, 0.18), (0.067, 0.195), (0.067, 0.215), (0.048, 0.223)]
        lathe(name+' body', x, y, z, profile, m)
        ball(name+' head', (x, y, z+0.275), 0.064, m)
    elif kind == 'Rook':
        profile += [(0.064, 0.16), (0.070, 0.295), (0.101, 0.307), (0.101, 0.344)]
        lathe(name+' tower', x, y, z, profile, m)
        for j in range(6):
            a = j*math.tau/6
            o = box(name+' battlement', (x+0.077*math.cos(a), y+0.077*math.sin(a), z+0.37), (0.049, 0.045, 0.066), m, 0.004)
            o.rotation_euler.z = a
    elif kind == 'Knight':
        profile += [(0.075, 0.128), (0.080, 0.148)]
        lathe(name+' plinth', x, y, z, profile, m)
        # Extruded angular horse silhouette: mane, ears, brow and muzzle.
        outline = [(-0.085,0.15), (0.065,0.15), (0.043,0.255), (0.107,0.273), (0.132,0.307), (0.103,0.354), (0.044,0.395), (0.024,0.452), (-0.007,0.414), (-0.043,0.438), (-0.041,0.383), (-0.085,0.304)]
        verts = []
        direction = 1 if side == 'White' else -1
        for thickness in [-0.045, 0.045]:
            for forward, h in outline:
                verts.append((x+thickness, y+direction*forward, z+h))
        n = len(outline)
        faces = [tuple(reversed(range(n))), tuple(range(n, 2*n))]
        for j in range(n):
            k = (j+1)%n
            faces.append((j,k,n+k,n+j))
        mesh = bpy.data.meshes.new(name+' horse mesh')
        mesh.from_pydata(verts, [], faces)
        mesh.update()
        o = bpy.data.objects.new(name+' horse head', mesh)
        bpy.context.collection.objects.link(o)
        finish(o, o.name, m, 0.009)
        for s in [-1, 1]:
            ball(name+' eye', (x+s*0.047, y+direction*0.050, z+0.362), 0.009, brass)
    elif kind == 'Bishop':
        profile += [(0.044,0.25), (0.076,0.271), (0.076,0.294), (0.040,0.307), (0.064,0.345), (0.069,0.37), (0.045,0.41), (0.009,0.453)]
        head = lathe(name+' mitre body', x, y, z, profile, m)
        # A true diagonal mitre slit, cut through the upper head.
        cutter = box('Temporary bishop slit cutter', (x, y, z+0.426), (0.025, 0.22, 0.13), m, 0)
        cutter.rotation_euler.y = -0.48
        boolean = head.modifiers.new('Mitre diagonal slit', 'BOOLEAN')
        boolean.operation = 'DIFFERENCE'
        boolean.solver = 'EXACT'
        boolean.object = cutter
        bpy.context.view_layer.objects.active = head
        bpy.ops.object.select_all(action='DESELECT')
        head.select_set(True)
        bpy.ops.object.modifier_apply(modifier=boolean.name)
        bpy.data.objects.remove(cutter, do_unlink=True)
        ball(name+' finial', (x, y, z+0.47), 0.021, m)
    else:
        profile += [(0.046,0.28), (0.080,0.307), (0.080,0.329), (0.052,0.342), (0.064,0.395), (0.096,0.443), (0.096,0.462)]
        lathe(name+' royal body', x, y, z, profile, m)
        if kind == 'Queen':
            for j in range(8):
                a = j*math.tau/8
                ball(name+' crown point', (x+0.077*math.cos(a), y+0.077*math.sin(a), z+0.476), 0.021, m)
            ball(name+' crown center', (x, y, z+0.485), 0.034, m)
        else:
            rod(name+' crown neck', (x, y, z+0.46), (x, y, z+0.493), 0.039, m)
            box(name+' cross upright', (x, y, z+0.548), (0.034, 0.035, 0.14), m, 0.004)
            box(name+' cross arm', (x, y, z+0.567), (0.105, 0.035, 0.032), m, 0.004)

back = ['Rook', 'Knight', 'Bishop', 'Queen', 'King', 'Bishop', 'Knight', 'Rook']
for file, kind in enumerate(back):
    piece(kind, file, 0, ivory, 'White')
    piece('Pawn', file, 1, ivory, 'White')
    piece('Pawn', file, 6, black, 'Black')
    piece(kind, file, 7, black, 'Black')

scene = bpy.context.scene
scene.world = scene.world or bpy.data.worlds.new('World')
scene.world.use_nodes = True
scene.world.node_tree.nodes['Background'].inputs[0].default_value = (0.28, 0.31, 0.36, 1)
scene.world.node_tree.nodes['Background'].inputs[1].default_value = 0.4
for loc, energy, size in [((2, -4, 8), 1500, 5), ((-5, -1, 5), 1000, 4), ((2, 5, 6), 1500, 4)]:
    bpy.ops.object.light_add(type='AREA', location=loc)
    o = bpy.context.object
    o.data.energy = energy
    o.data.size = size
    o.rotation_euler = (Vector((0, 0, 1.7))-o.location).to_track_quat('-Z', 'Y').to_euler()
bpy.ops.object.camera_add(location=(5.8, -7.8, 7.2))
cam = bpy.context.object
cam.rotation_euler = (Vector((0, 0, 1.45))-cam.location).to_track_quat('-Z', 'Y').to_euler()
cam.data.type = 'ORTHO'
cam.data.ortho_scale = 6.1
scene.camera = cam
scene.render.resolution_x = 1400
scene.render.resolution_y = 1200
scene.render.resolution_percentage = 100
