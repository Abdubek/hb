import bpy
from mathutils import Vector

# Small sailing dinghy. Bow is +X; sails lie approximately in the XZ plane.
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)

def material(name, rgb, metallic=0.0):
    m = bpy.data.materials.new(name)
    m.diffuse_color = (*rgb, 1)
    m.use_nodes = True
    bs = m.node_tree.nodes.get('Principled BSDF')
    bs.inputs['Base Color'].default_value = (*rgb, 1)
    bs.inputs['Metallic'].default_value = metallic
    bs.inputs['Roughness'].default_value = 0.43
    return m

navy = material('Navy blue hull', (0.025, 0.12, 0.24))
teak = material('Honey teak', (0.51, 0.27, 0.095))
ivory = material('Ivory sailcloth', (0.95, 0.91, 0.76))
red = material('Red sail stripe', (0.75, 0.12, 0.07))
aluminum = material('Anodized aluminum', (0.57, 0.63, 0.67), 0.7)
rope = material('Rigging rope', (0.28, 0.24, 0.18))
water = material('Blue display base', (0.08, 0.32, 0.40))

def mesh(name, verts, faces, mat):
    data = bpy.data.meshes.new(name + ' mesh')
    data.from_pydata(verts, [], faces)
    data.update()
    obj = bpy.data.objects.new(name, data)
    bpy.context.collection.objects.link(obj)
    obj.data.materials.append(mat)
    return obj

def box(name, loc, size, mat, bevel=0.025):
    bpy.ops.mesh.primitive_cube_add(size=1, location=loc)
    obj = bpy.context.object
    obj.name = name
    obj.dimensions = size
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    obj.data.materials.append(mat)
    if bevel:
        mod = obj.modifiers.new('Soft edges', 'BEVEL')
        mod.width = bevel
        mod.segments = 2
        obj.modifiers.new('Weighted normals', 'WEIGHTED_NORMAL')
    return obj

def rod(name, a, b, radius, mat, vertices=16):
    a, b = Vector(a), Vector(b)
    delta = b - a
    bpy.ops.mesh.primitive_cylinder_add(vertices=vertices, radius=radius, depth=delta.length, location=(a+b)/2)
    obj = bpy.context.object
    obj.name = name
    obj.rotation_euler = delta.to_track_quat('Z', 'Y').to_euler()
    obj.data.materials.append(mat)
    return obj

# Three nested polygon rings form the bottom, topsides and inward-facing lip.
outline = [(-2.5, -0.68), (-1.5, -1.02), (0.25, -1.08),
           (1.65, -0.65), (2.65, 0), (1.65, 0.65),
           (0.25, 1.08), (-1.5, 1.02), (-2.5, 0.68)]
n = len(outline)
verts = [(x*0.84, y*0.55, 0.18) for x, y in outline]
verts += [(x, y, 0.98) for x, y in outline]
verts += [(x*0.94, y*0.88, 0.90) for x, y in outline]
faces = [tuple(reversed(range(n)))]
for i in range(n):
    j = (i+1) % n
    faces.append((i, j, n+j, n+i))
    faces.append((n+i, n+j, 2*n+j, 2*n+i))
faces.append(tuple(range(2*n, 3*n)))
hull = mesh('Closed faceted hull with recessed deck', verts, faces, navy)
hull.data.materials.append(teak)
hull.data.polygons[-1].material_index = 1
for i, (x, y) in enumerate(outline):
    nx, ny = outline[(i+1) % n]
    rod('Teak gunwale %02d' % i, (x, y, 1.0), (nx, ny, 1.0), 0.045, teak)

# A dark inset with a wooden rim suggests the small open cockpit.
box('Cockpit recess', (-0.92, 0, 0.912), (1.72, 1.20, 0.025), navy)
for y in (-0.64, 0.64):
    box('Cockpit side coaming', (-0.92, y, 0.98), (1.86, 0.10, 0.16), teak)
for x in (-1.82, -0.02):
    box('Cockpit end coaming', (x, 0, 0.98), (0.10, 1.30, 0.16), teak)
box('Crosswise cockpit bench', (-1.05, 0, 1.08), (0.34, 1.29, 0.12), teak)
box('Mast step', (0.48, 0, 0.99), (0.36, 0.34, 0.18), aluminum)
rod('Main mast', (0.48, 0, 0.96), (0.48, 0, 5.7), 0.065, aluminum, 24)
rod('Horizontal boom', (0.48, 0, 1.64), (-2.06, 0, 1.64), 0.052, aluminum, 24)

# Slightly billowed cloth panels, with solidify for visible sail edges.
def sail(name, corners, mat):
    center = sum((Vector(p) for p in corners), Vector()) / len(corners)
    center.y += 0.17
    vertices = list(corners) + [tuple(center)]
    obj = mesh(name, vertices, [(i, (i+1) % len(corners), len(corners)) for i in range(len(corners))], mat)
    mod = obj.modifiers.new('Sailcloth thickness', 'SOLIDIFY')
    mod.thickness = 0.012
    for i, a in enumerate(corners):
        rod(name + ' edge seam', a, corners[(i+1) % len(corners)], 0.012, rope, 8)
    return obj

sail('Triangular mainsail', [(0.39, 0.035, 5.43), (0.39, 0.035, 1.78), (-1.97, 0.035, 1.78)], ivory)
sail('Forward jib', [(0.62, 0.015, 5.14), (2.36, 0.015, 1.15), (0.70, 0.015, 1.82)], ivory)
# Small colored pennant provides a readable masthead detail.
sail('Masthead red pennant', [(0.48, 0, 5.69), (0.48, 0, 5.39), (-0.12, 0, 5.55)], red)
rod('Forestay', (0.48, 0, 5.56), (2.51, 0, 1.04), 0.014, rope, 8)
for y in (-0.91, 0.91):
    rod('Side shroud', (0.48, 0, 5.43), (-0.20, y, 1.03), 0.012, rope, 8)
rod('Boom mainsheet', (-1.85, 0, 1.63), (-1.8, 0.30, 1.03), 0.018, rope, 8)
box('Stern rudder blade', (-2.58, 0, 0.35), (0.32, 0.10, 1.0), teak)
rod('Rudder stock', (-2.52, 0, 0.7), (-2.52, 0, 1.22), 0.055, aluminum)
rod('Wooden tiller', (-2.52, 0, 1.22), (-1.39, 0, 1.30), 0.045, teak)
box('Water display slab', (0, 0, -0.27), (7.5, 4.8, 0.18), water, 0.12)

scene = bpy.context.scene
scene.world = scene.world or bpy.data.worlds.new('World')
scene.world.use_nodes = True
scene.world.node_tree.nodes['Background'].inputs[0].default_value = (0.30, 0.39, 0.48, 1)
scene.world.node_tree.nodes['Background'].inputs[1].default_value = 0.6
bpy.ops.object.light_add(type='AREA', location=(1, -4, 8))
bpy.context.object.data.energy = 1400
bpy.context.object.data.size = 5
bpy.ops.object.camera_add(location=(8, -13, 7.0))
cam = bpy.context.object
cam.rotation_euler = (Vector((0, 0, 2.5)) - cam.location).to_track_quat('-Z', 'Y').to_euler()
cam.data.type = 'ORTHO'
cam.data.ortho_scale = 9.2
scene.camera = cam
scene.render.resolution_x = 1000
scene.render.resolution_y = 1000
scene.render.resolution_percentage = 100
