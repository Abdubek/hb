import bpy
from math import sin, cos, pi
from mathutils import Vector

# Independent scene: stainless saucepan, fitted domed lid and insulated handle.
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)

def material(name, color, metallic=0.0, roughness=0.4):
    m = bpy.data.materials.new(name)
    m.diffuse_color = (*color, 1)
    m.use_nodes = True
    p = m.node_tree.nodes.get('Principled BSDF')
    p.inputs['Base Color'].default_value = (*color, 1)
    p.inputs['Metallic'].default_value = metallic
    p.inputs['Roughness'].default_value = roughness
    return m

steel = material('Satin stainless steel', (0.53, 0.59, 0.64), 0.85, 0.28)
polished = material('Polished rim and hardware', (0.72, 0.77, 0.81), 0.92, 0.19)
black = material('Heat resistant black grip', (0.023, 0.029, 0.036), 0.05, 0.40)
base_mat = material('Encapsulated base metal', (0.25, 0.29, 0.33), 0.8, 0.32)
floor = material('Warm countertop', (0.29, 0.26, 0.23))

def lathe(name, profile, mat, segments=64):
    # Ordered radial cross-section; axis endpoints become single pole vertices.
    vertices, rings, faces = [], [], []
    for radius, z in profile:
        ring = []
        for i in range(1 if radius == 0 else segments):
            angle = 2 * pi * i / segments
            ring.append(len(vertices))
            vertices.append((radius * cos(angle), radius * sin(angle), z))
        rings.append(ring)
    for a, b in zip(rings, rings[1:]):
        for i in range(segments):
            j = (i + 1) % segments
            if len(a) == 1:
                faces.append((a[0], b[j], b[i]))
            elif len(b) == 1:
                faces.append((a[i], a[j], b[0]))
            else:
                faces.append((a[i], a[j], b[j], b[i]))
    mesh = bpy.data.meshes.new(name + ' mesh')
    mesh.from_pydata(vertices, [], faces)
    mesh.update()
    obj = bpy.data.objects.new(name, mesh)
    bpy.context.collection.objects.link(obj)
    obj.data.materials.append(mat)
    for polygon in mesh.polygons:
        polygon.use_smooth = True
    return obj

def box(name, location, dimensions, mat, bevel=0.06):
    bpy.ops.mesh.primitive_cube_add(size=1, location=location)
    obj = bpy.context.object
    obj.name = name
    obj.dimensions = dimensions
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    obj.data.materials.append(mat)
    mod = obj.modifiers.new('Rounded edges', 'BEVEL')
    mod.width = bevel
    mod.segments = 4
    obj.modifiers.new('Weighted normals', 'WEIGHTED_NORMAL')
    return obj

lathe('Solid base and hollow saucepan wall', [
    (0, 0.16), (1.02, 0.16), (1.13, 0.20), (1.20, 0.30),
    (1.27, 1.37), (1.28, 1.46), (1.26, 1.50), (1.21, 1.50),
    (1.19, 1.44), (1.12, 0.34), (1.04, 0.28), (0, 0.28)], steel)
lathe('Thick induction base', [(0, 0.055), (1.02, 0.055), (1.09, 0.085),
    (1.10, 0.15), (1.05, 0.19), (0, 0.19)], base_mat)
lathe('Rolled polished pot rim', [(1.21, 1.43), (1.28, 1.43), (1.31, 1.47),
    (1.30, 1.51), (1.26, 1.53), (1.21, 1.50), (1.21, 1.43)], polished)
lathe('Fitted domed steel lid', [(0, 1.72), (0.36, 1.70), (0.79, 1.62),
    (1.12, 1.48), (1.22, 1.48), (1.23, 1.53), (1.14, 1.55),
    (0.81, 1.69), (0.39, 1.77), (0, 1.79)], steel)
lathe('Lid edge bead', [(1.15, 1.50), (1.24, 1.50), (1.26, 1.53),
    (1.24, 1.56), (1.15, 1.55), (1.15, 1.50)], polished)
lathe('Knob metal washer', [(0, 1.77), (0.19, 1.77), (0.21, 1.80),
    (0.19, 1.83), (0, 1.83)], polished)
lathe('Insulated lid knob', [(0, 1.81), (0.12, 1.81), (0.13, 1.96),
    (0.25, 2.00), (0.28, 2.06), (0.25, 2.15), (0.18, 2.18), (0, 2.18)], black)
box('Handle mounting shoe', (1.23, 0, 1.12), (0.18, 0.48, 0.37), polished)
box('Steel handle tang', (1.58, 0, 1.16), (0.73, 0.29, 0.17), steel)
grip = box('Long insulated saucepan handle', (2.62, 0, 1.24), (1.89, 0.43, 0.30), black, 0.13)
grip.rotation_euler.y = -0.065
for x in (1.91, 3.27):
    bpy.ops.mesh.primitive_uv_sphere_add(segments=20, ring_count=12, radius=1,
                                      location=(x, 0, 1.40 + (x - 2.62) * 0.065))
    rivet = bpy.context.object
    rivet.name = 'Flush handle fastening rivet'
    rivet.scale = (0.055, 0.055, 0.015)
    rivet.data.materials.append(polished)
box('Counter surface', (0, 0, -0.035), (200, 200, 0.16), floor, 0.02)

scene = bpy.context.scene
scene.world.color = (0.22, 0.22, 0.22)
bpy.ops.object.camera_add(location=(5.2, -7.5, 5.5))
camera = bpy.context.object
camera.name = 'Saucepan product camera'
target = Vector((0.9, 0, 1.0))
camera.rotation_euler = (target - camera.location).to_track_quat('-Z', 'Y').to_euler()
camera.data.type = 'ORTHO'
camera.data.ortho_scale = 6.2
scene.camera = camera
for name, location, energy, size in [('Large key', (0, -4, 7), 1100, 5), ('Metal rim light', (2, 4, 6), 1000, 4)]:
    bpy.ops.object.light_add(type='AREA', location=location)
    light = bpy.context.object
    light.name = name
    light.data.energy = energy
    light.data.size = size
    light.rotation_euler = (target - light.location).to_track_quat('-Z', 'Y').to_euler()
scene.render.resolution_x = 1100
scene.render.resolution_y = 800
scene.render.resolution_percentage = 100
