import bpy
import math
from mathutils import Vector

bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)

def material(name, color, roughness=0.65):
    mat = bpy.data.materials.new(name)
    mat.diffuse_color = (*color, 1)
    mat.use_nodes = True
    mat.node_tree.nodes['Principled BSDF'].inputs['Base Color'].default_value = (*color, 1)
    mat.node_tree.nodes['Principled BSDF'].inputs['Roughness'].default_value = roughness
    return mat

sand = material('Warm fine sand', (0.72, 0.58, 0.36))
ivory = material('Ivory canvas', (0.94, 0.89, 0.73))
coral = material('Coral canvas', (0.83, 0.18, 0.10))
aqua = material('Aqua canvas', (0.045, 0.49, 0.57))
yellow = material('Golden canvas', (0.97, 0.61, 0.08))
wood = material('Oiled teak', (0.38, 0.20, 0.075))
metal = material('Umbrella hardware', (0.34, 0.37, 0.36), 0.3)


def box(name, location, dimensions, mat, rotation=(0, 0, 0)):
    bpy.ops.mesh.primitive_cube_add(size=1, location=location)
    obj = bpy.context.object
    obj.name = name
    obj.dimensions = dimensions
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    obj.rotation_euler = rotation
    obj.data.materials.append(mat)
    bevel = obj.modifiers.new('Soft manufactured edges', 'BEVEL')
    bevel.width = 0.025
    bevel.segments = 2
    obj.modifiers.new('Weighted corner normals', 'WEIGHTED_NORMAL')
    return obj


def rod(name, start, end, radius, mat):
    delta = Vector(end) - Vector(start)
    bpy.ops.mesh.primitive_cylinder_add(vertices=12, radius=radius, depth=delta.length,
                                      location=(Vector(start) + Vector(end)) / 2)
    obj = bpy.context.object
    obj.name = name
    obj.rotation_euler = delta.to_track_quat('Z', 'Y').to_euler()
    obj.data.materials.append(mat)
    return obj

box('Sand display platform', (0, 0, -0.16), (15.5, 7.5, 0.30), sand)


def umbrella(index, x, accent):
    prefix = 'Umbrella %d ' % index
    rod(prefix + 'central teak pole', (x, 0.65, 0), (x, 0.65, 3.25), 0.045, wood)
    rod(prefix + 'sliding collar', (x, 0.65, 2.0), (x, 0.65, 2.18), 0.075, metal)
    # Each panel has three radial bands and a dipped midpoint at its scalloped edge.
    profile = [(0.0, 3.18), (0.63, 3.08), (1.23, 2.80), (1.85, 2.43)]
    for panel in range(12):
        verts = []
        for ring, (radius, z) in enumerate(profile):
            for k in range(3):
                angle = 2 * math.pi * (panel + k / 2) / 12
                edge_dip = 0.10 if ring == 3 and k == 1 else 0
                verts.append((x + radius * math.cos(angle), 0.65 + radius * math.sin(angle), z - edge_dip))
        faces = [(0, 3, 4), (0, 4, 5)]
        for ring in (1, 2):
            for k in range(2):
                a = ring * 3 + k
                faces.append((a, a + 3, a + 4, a + 1))
        mesh = bpy.data.meshes.new(prefix + 'panel mesh')
        mesh.from_pydata(verts, [], faces)
        mesh.update()
        obj = bpy.data.objects.new(prefix + 'canvas panel %02d' % panel, mesh)
        bpy.context.collection.objects.link(obj)
        obj.data.materials.append(accent if panel % 2 == 0 else ivory)
        solid = obj.modifiers.new('Canvas thickness', 'SOLIDIFY')
        solid.thickness = 0.012
        angle = 2 * math.pi * panel / 12
        points = [(x + r * math.cos(angle), 0.65 + r * math.sin(angle), z - 0.025) for r, z in profile]
        for a, b in zip(points[:-1], points[1:]):
            rod(prefix + 'radial rib', a, b, 0.015, wood)
        rod(prefix + 'support strut', (x, 0.65, 2.10), points[2], 0.012, metal)
    rod(prefix + 'top finial', (x, 0.65, 3.17), (x, 0.65, 3.33), 0.065, wood)


def lounge(index, x, y, accent):
    prefix = 'Lounge %s ' % index
    box(prefix + 'seat cushion', (x, y - 0.23, 0.49), (0.69, 1.39, 0.10), ivory)
    for side in (-0.41, 0.41):
        box(prefix + 'seat side rail', (x + side, y - 0.23, 0.40), (0.07, 1.53, 0.12), wood)
        for offset in (-0.77, 0.35):
            rod(prefix + 'splayed leg', (x + side * 1.08, y + offset + 0.08, 0.02),
                (x + side, y + offset, 0.42), 0.038, wood)
    angle = math.radians(55)
    hinge = Vector((x, y + 0.45, 0.47))
    top = hinge + Vector((0, math.cos(angle), math.sin(angle)))
    box(prefix + 'reclined back cushion', (hinge + top) / 2, (0.69, 1.0, 0.10), accent, (angle, 0, 0))
    for side in (-0.41, 0.41):
        shift = Vector((side, 0, 0))
        rod(prefix + 'back frame', hinge + shift, top + shift, 0.035, wood)
        rod(prefix + 'back support', (x + side, y + 0.32, 0.12), top + shift, 0.025, wood)
    rod(prefix + 'back top crossbar', top + Vector((-0.43, 0, 0)), top + Vector((0.43, 0, 0)), 0.035, wood)

for i, (x, accent) in enumerate(((-4.6, coral), (0, aqua), (4.6, yellow)), 1):
    umbrella(i, x, accent)
    lounge('%d A' % i, x - 0.70, -0.90, accent)
    lounge('%d B' % i, x + 0.70, -0.90, accent)
    rod('Table %d pedestal' % i, (x, -1.65, 0), (x, -1.65, 0.51), 0.065, wood)
    rod('Table %d round top' % i, (x, -1.65, 0.49), (x, -1.65, 0.55), 0.29, wood)
    rod('Table %d broad foot' % i, (x, -1.65, 0.015), (x, -1.65, 0.065), 0.22, wood)

bpy.ops.object.camera_add(location=(12, -19, 12))
camera = bpy.context.object
camera.name = 'Beach furniture overview'
camera.rotation_euler = (Vector((0, 0, 1.1)) - camera.location).to_track_quat('-Z', 'Y').to_euler()
camera.data.type = 'ORTHO'
camera.data.ortho_scale = 18
bpy.context.scene.camera = camera
bpy.ops.object.light_add(type='AREA', location=(-3, -4, 11))
bpy.context.object.data.energy = 2300
bpy.context.object.data.size = 8
bpy.context.scene.world.color = (0.35, 0.40, 0.48)
bpy.context.scene.render.resolution_x = 1400
bpy.context.scene.render.resolution_y = 900
bpy.context.scene.render.resolution_percentage = 100
