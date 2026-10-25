import bpy
import math
from mathutils import Vector

bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)

def material(name, color, metallic=0, roughness=0.4):
    m = bpy.data.materials.new(name)
    m.diffuse_color = (*color, 1)
    m.use_nodes = True
    bs = m.node_tree.nodes.get('Principled BSDF')
    bs.inputs['Base Color'].default_value = (*color, 1)
    bs.inputs['Metallic'].default_value = metallic
    bs.inputs['Roughness'].default_value = roughness
    return m

wood = material('Walnut table frame', (0.14, 0.055, 0.025))
light_tile = material('Maple board squares', (0.72, 0.56, 0.35))
dark_tile = material('Ebony board squares', (0.055, 0.035, 0.025))
ivory = material('Ivory chess pieces', (0.93, 0.86, 0.69))
black = material('Charcoal chess pieces', (0.065, 0.075, 0.085), 0.15)
brass = material('Brass trim', (0.62, 0.37, 0.10), 0.75)
floor_mat = material('Floor stone', (0.25, 0.28, 0.29))

def finish(obj, name, mat, bevel=0):
    obj.name = name
    obj.data.materials.append(mat)
    if bevel:
        mod = obj.modifiers.new('Edge highlights', 'BEVEL')
        mod.width = bevel
        mod.segments = 2
        obj.modifiers.new('Weighted normals', 'WEIGHTED_NORMAL')
    return obj

def box(name, loc, dims, mat, bevel=0.008):
    bpy.ops.mesh.primitive_cube_add(size=1, location=loc)
    obj = bpy.context.object
    obj.dimensions = dims
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    return finish(obj, name, mat, bevel)

def cone(name, x, y, z, r1, r2, height, mat):
    bpy.ops.mesh.primitive_cone_add(vertices=24, radius1=r1, radius2=r2,
                                  depth=height, location=(x, y, z + height / 2))
    return finish(bpy.context.object, name, mat, 0.004)

def ball(name, loc, radius, mat):
    bpy.ops.mesh.primitive_uv_sphere_add(segments=16, ring_count=8, radius=radius, location=loc)
    obj = finish(bpy.context.object, name, mat)
    for polygon in obj.data.polygons:
        polygon.use_smooth = True
    return obj

box('Solid walnut tabletop', (0, 0, 1.80), (2.88, 2.88, 0.16), wood, 0.035)
for x in (-1.17, 1.17):
    for y in (-1.17, 1.17):
        box('Square tapered-style table leg', (x, y, 0.86), (0.17, 0.17, 1.72), wood, 0.016)
        box('Brass foot ferrule', (x, y, 0.07), (0.177, 0.177, 0.14), brass)
for offset in (-1.19, 1.19):
    box('Front or rear apron', (0, offset, 1.60), (2.45, 0.11, 0.27), wood)
    box('Side apron', (offset, 0, 1.60), (0.11, 2.45, 0.27), wood)
box('Brass board surround', (0, 0, 1.889), (2.46, 2.46, 0.018), brass, 0.005)
for row in range(8):
    for col in range(8):
        box('Square %s%d' % (chr(97 + col), row + 1),
            ((col - 3.5) * 0.30, (row - 3.5) * 0.30, 1.905),
            (0.30, 0.30, 0.025), dark_tile if (row + col) % 2 == 0 else light_tile, 0)

surface = 1.9175
def piece(kind, col, row, mat, side):
    x, y = (col - 3.5) * 0.30, (row - 3.5) * 0.30
    name = side + ' ' + kind + ' ' + chr(97 + col) + str(row + 1)
    cone(name + ' base', x, y, surface, 0.107, 0.095, 0.035, mat)
    cone(name + ' plinth', x, y, surface + 0.035, 0.095, 0.068, 0.035, mat)
    stem = 0.10 if kind == 'Pawn' else 0.16
    cone(name + ' tapered body', x, y, surface + 0.07, 0.063, 0.041, stem, mat)
    z = surface + 0.07 + stem
    cone(name + ' collar', x, y, z, 0.067, 0.067, 0.023, mat)
    z += 0.023
    if kind == 'Pawn':
        ball(name + ' head', (x, y, z + 0.050), 0.055, mat)
    elif kind == 'Rook':
        cone(name + ' tower', x, y, z, 0.071, 0.076, 0.065, mat)
        for i in range(4):
            a = i * math.pi / 2
            box(name + ' battlement %d' % i, (x + 0.052 * math.cos(a), y + 0.052 * math.sin(a), z + 0.078), (0.040, 0.040, 0.042), mat, 0.003)
    elif kind == 'Knight':
        # Extruded angular horse silhouette, facing toward the opponent.
        profile = [(-0.065, 0), (0.055, 0), (0.037, 0.095), (0.095, 0.115), (0.097, 0.158), (0.025, 0.197), (0.003, 0.235), (-0.021, 0.193), (-0.057, 0.155)]
        direction = 1 if side == 'White' else -1
        verts = [(x + width, y + direction * py, z + pz) for width in (-0.034, 0.034) for py, pz in profile]
        n = len(profile)
        faces = [tuple(reversed(range(n))), tuple(range(n, 2 * n))]
        faces += [(i, (i + 1) % n, (i + 1) % n + n, i + n) for i in range(n)]
        mesh = bpy.data.meshes.new(name + ' horse mesh')
        mesh.from_pydata(verts, [], faces)
        mesh.update()
        obj = bpy.data.objects.new(name + ' horse head', mesh)
        bpy.context.collection.objects.link(obj)
        finish(obj, obj.name, mat, 0.005)
    elif kind == 'Bishop':
        cone(name + ' pointed mitre', x, y, z, 0.069, 0.009, 0.14, mat)
        ball(name + ' finial', (x, y, z + 0.145), 0.023, mat)
    elif kind == 'Queen':
        cone(name + ' flared crown', x, y, z, 0.045, 0.079, 0.10, mat)
        for i in range(6):
            a = i * math.tau / 6
            ball(name + ' crown pearl %d' % i, (x + 0.065 * math.cos(a), y + 0.065 * math.sin(a), z + 0.112), 0.019, mat)
        ball(name + ' royal finial', (x, y, z + 0.137), 0.030, mat)
    else:
        cone(name + ' royal cap', x, y, z, 0.072, 0.042, 0.09, mat)
        box(name + ' cross upright', (x, y, z + 0.16), (0.032, 0.032, 0.14), mat, 0.003)
        box(name + ' cross arm', (x, y, z + 0.182), (0.104, 0.032, 0.032), mat, 0.003)

order = ['Rook', 'Knight', 'Bishop', 'Queen', 'King', 'Bishop', 'Knight', 'Rook']
for side, mat, back, pawns in [('White', ivory, 0, 1), ('Black', black, 7, 6)]:
    for col, kind in enumerate(order):
        piece(kind, col, back, mat, side)
        piece('Pawn', col, pawns, mat, side)
box('Studio floor', (0, 0, -0.05), (200, 200, 0.10), floor_mat, 0)
bpy.ops.object.camera_add(location=(4.3, -5.6, 6.1))
camera = bpy.context.object
camera.name = 'Chess table overview'
camera.rotation_euler = (Vector((0, 0, 1.20)) - camera.location).to_track_quat('-Z', 'Y').to_euler()
camera.data.type = 'ORTHO'
camera.data.ortho_scale = 4.9
bpy.context.scene.camera = camera
for loc, energy, size in [((1, -3, 7), 1100, 4), ((-4, 2, 5), 950, 3)]:
    bpy.ops.object.light_add(type='AREA', location=loc)
    light = bpy.context.object
    light.data.energy = energy
    light.data.size = size
    light.rotation_euler = (Vector((0, 0, 1.4)) - light.location).to_track_quat('-Z', 'Y').to_euler()
bpy.context.scene.world.color = (0.25, 0.25, 0.25)
bpy.context.scene.render.resolution_x = 1100
bpy.context.scene.render.resolution_y = 1100
bpy.context.scene.render.resolution_percentage = 100
