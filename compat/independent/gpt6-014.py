import bpy
import math
import random
from mathutils import Vector

# Independent scene: four-bay modular shelving with offset shelf heights.
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)
random.seed(14)

def material(name, color, metallic=0.0, roughness=0.45):
    m = bpy.data.materials.new(name)
    m.diffuse_color = (*color, 1)
    m.use_nodes = True
    p = m.node_tree.nodes.get('Principled BSDF')
    p.inputs['Base Color'].default_value = (*color, 1)
    p.inputs['Metallic'].default_value = metallic
    p.inputs['Roughness'].default_value = roughness
    return m

oak = material('Natural oak shelves', (0.56, 0.33, 0.15))
steel = material('Graphite steel uprights', (0.045, 0.058, 0.065), 0.65, 0.28)
paper = material('Warm ivory page edges', (0.83, 0.78, 0.65))
gold = material('Muted gold spine lettering', (0.71, 0.52, 0.23), 0.35)
ceramic = material('Cream ceramic', (0.76, 0.72, 0.61), 0.0, 0.27)
book_mats = [material(name, color) for name, color in [
    ('Book navy', (0.045, 0.12, 0.20)), ('Book rust', (0.48, 0.12, 0.055)),
    ('Book sage', (0.23, 0.34, 0.24)), ('Book ochre', (0.69, 0.42, 0.10)),
    ('Book charcoal', (0.085, 0.095, 0.10)), ('Book linen', (0.59, 0.53, 0.42))]]

def box(name, loc, size, mat, bevel=0.008):
    bpy.ops.mesh.primitive_cube_add(size=1, location=loc)
    obj = bpy.context.object
    obj.name = name
    obj.dimensions = size
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    obj.data.materials.append(mat)
    if bevel:
        mod = obj.modifiers.new('Edge easing', 'BEVEL')
        mod.width = bevel
        mod.segments = 2
        obj.modifiers.new('Weighted normals', 'WEIGHTED_NORMAL')
    return obj

def rod(name, a, b, radius, mat):
    a, b = Vector(a), Vector(b)
    bpy.ops.mesh.primitive_cylinder_add(vertices=16, radius=radius, depth=(b-a).length, location=(a+b)/2)
    obj = bpy.context.object
    obj.name = name
    obj.rotation_euler = (b-a).to_track_quat('Z', 'Y').to_euler()
    obj.data.materials.append(mat)
    return obj

def book(name, x, bottom, width, height, depth, cover):
    # Spines face the viewer at negative Y; separate boards frame the page block.
    front = -0.255 + random.uniform(-0.018, 0.018)
    yc = front + depth/2
    box(name + ' page block', (x, yc+0.009, bottom+height/2),
        (width-0.016, depth-0.035, height-0.018), paper, 0.002)
    for dx in (-width/2+0.004, width/2-0.004):
        box(name + ' cover board', (x+dx, yc, bottom+height/2),
            (0.008, depth, height), cover, 0.002)
    box(name + ' spine', (x, front+0.006, bottom+height/2),
        (width, 0.013, height), cover, 0.003)
    for fraction in (0.16, 0.80):
        box(name + ' spine foil band', (x, front-0.001, bottom+height*fraction),
            (width*0.73, 0.002, 0.007), gold, 0.001)
    box(name + ' title panel', (x, front-0.002, bottom+height*0.64),
        (width*0.56, 0.002, height*0.12), paper, 0.001)

# Five paired posts divide four equal bays; all horizontal boards are individual modules.
for i in range(5):
    x = -1.84 + i*0.92
    for y in (-0.27, 0.27):
        box('Upright %d %s' % (i, 'front' if y < 0 else 'rear'),
            (x, y, 1.56), (0.045, 0.045, 2.96), steel, 0.006)
        box('Adjustable foot', (x, y, 0.055), (0.085, 0.085, 0.11), steel)
    box('Top depth tie %d' % i, (x, 0, 3.02), (0.045, 0.58, 0.035), steel)
box('Lower continuous oak deck', (0, 0, 0.16), (3.76, 0.64, 0.075), oak)
box('Upper oak crown', (0, 0, 3.055), (3.76, 0.64, 0.07), oak)
rod('Rear diagonal brace left', (-1.84, 0.295, 0.22), (0, 0.295, 2.98), 0.009, steel)
rod('Rear diagonal brace right', (0, 0.295, 2.98), (1.84, 0.295, 0.22), 0.009, steel)

shelf_levels = [(0.78, 1.51, 2.24), (1.00, 1.73, 2.46),
                (0.78, 1.51, 2.24), (1.00, 1.73, 2.46)]
for bay, levels in enumerate(shelf_levels):
    xc = -1.38 + bay*0.92
    for tier, z in enumerate(levels):
        box('Bay %d staggered shelf %d' % (bay+1, tier+1),
            (xc, 0, z), (0.89, 0.62, 0.055), oak)
        for dx in (-0.398, 0.398):
            box('Shelf support bracket', (xc+dx, 0, z-0.038), (0.035, 0.54, 0.026), steel, 0.003)
    for tier, base in enumerate([0.1975] + [z+0.0275 for z in levels]):
        # Leave one upper compartment open for a ceramic display.
        if bay == 2 and tier == 3:
            continue
        x = xc-0.36
        count = random.randint(4, 6)
        for j in range(count):
            width = random.uniform(0.075, 0.105)
            height = random.uniform(0.31, 0.44)
            book('Bay%d tier%d book%d' % (bay+1, tier, j+1),
                x+width/2, base, width, height, random.uniform(0.36, 0.45),
                book_mats[(bay*3+tier+j) % len(book_mats)])
            x += width+0.009
        box('Bookend foot', (x+0.022, -0.02, base+0.007), (0.095, 0.32, 0.014), steel, 0.003)
        box('Bookend upright', (x+0.059, -0.02, base+0.11), (0.015, 0.32, 0.22), steel, 0.003)

# A hollow low-poly ceramic vessel in the deliberately open display compartment.
profile = [(0.085, 0), (0.12, 0.045), (0.14, 0.16), (0.10, 0.27),
           (0.067, 0.32), (0.052, 0.32), (0.085, 0.265), (0.122, 0.155), (0.067, 0.024)]
verts, faces = [], []
for radius, z in profile:
    for i in range(40):
        angle = i*math.tau/40
        verts.append((0.46+radius*math.cos(angle), radius*math.sin(angle), 2.2675+z))
for ring in range(len(profile)-1):
    for i in range(40):
        a, b = ring*40+i, ring*40+(i+1)%40
        faces.append((a, b, b+40, a+40))
faces.append(tuple(reversed(range(40))))
faces.append(tuple((len(profile)-1)*40+i for i in range(40)))
mesh = bpy.data.meshes.new('Hollow vessel mesh')
mesh.from_pydata(verts, [], faces)
mesh.update()
vase = bpy.data.objects.new('Display ceramic vase', mesh)
bpy.context.collection.objects.link(vase)
vase.data.materials.append(ceramic)
for poly in mesh.polygons:
    poly.use_smooth = len(poly.vertices) == 4

wall = material('Warm plaster wall', (0.68, 0.65, 0.59))
floor = material('Stone floor', (0.31, 0.32, 0.30))
box('Room floor', (0, 0, -0.055), (200, 200, 0.1), floor, 0)
box('Backdrop wall', (0, 0.65, 2.6), (12, 0.12, 5.2), wall, 0)
box('Wall baseboard', (0, 0.555, 0.075), (12, 0.06, 0.15), ceramic, 0.005)
bpy.ops.object.camera_add(location=(4.4, -7.5, 4.0))
camera = bpy.context.object
camera.name = 'Bookshelf overview camera'
camera.rotation_euler = (Vector((0, 0, 1.53))-camera.location).to_track_quat('-Z', 'Y').to_euler()
camera.data.type = 'ORTHO'
camera.data.ortho_scale = 5.25
bpy.context.scene.camera = camera
for loc, energy, size in [((-3, -4, 6), 950, 4), ((4, -2, 4), 500, 3)]:
    bpy.ops.object.light_add(type='AREA', location=loc)
    light = bpy.context.object
    light.name = 'Bookshelf studio softbox'
    light.data.energy = energy
    light.data.size = size
    light.rotation_euler = (Vector((0, 0, 1.5))-light.location).to_track_quat('-Z', 'Y').to_euler()
scene = bpy.context.scene
scene.world.color = (0.22, 0.22, 0.22)
scene.render.resolution_x = 1100
scene.render.resolution_y = 1000
scene.render.resolution_percentage = 100
