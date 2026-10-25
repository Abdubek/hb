import bpy
import math
from mathutils import Vector

# Independent scene: a compact camping lantern with a hinged carry handle.
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)

def material(name, color, metallic=0.0, roughness=0.4):
    mat = bpy.data.materials.new(name)
    mat.diffuse_color = (*color, 1)
    mat.use_nodes = True
    shader = mat.node_tree.nodes.get('Principled BSDF')
    shader.inputs['Base Color'].default_value = (*color, 1)
    shader.inputs['Metallic'].default_value = metallic
    shader.inputs['Roughness'].default_value = roughness
    return mat

paint = material('Forest green enamel', (0.045, 0.18, 0.12), 0.55, 0.3)
metal = material('Brushed steel protective cage', (0.28, 0.32, 0.34), 0.85, 0.25)
rubber = material('Black rubber grip and feet', (0.018, 0.023, 0.025), 0.0, 0.75)
glass = material('Clear glass chimney', (0.86, 0.96, 1.0), 0.0, 0.08)
shader = glass.node_tree.nodes.get('Principled BSDF')
shader.inputs['Transmission Weight'].default_value = 1.0
shader.inputs['IOR'].default_value = 1.45
emitter = material('Warm luminous diffuser', (1.0, 0.77, 0.36), 0.0, 0.45)
shader = emitter.node_tree.nodes.get('Principled BSDF')
shader.inputs['Emission Color'].default_value = (1.0, 0.63, 0.22, 1)
shader.inputs['Emission Strength'].default_value = 2.5
ground = material('Neutral display surface', (0.22, 0.25, 0.27), 0.0, 0.85)

def finish(obj, name, mat, bevel=0.0):
    obj.name = name
    obj.data.materials.append(mat)
    if bevel:
        mod = obj.modifiers.new('Rounded manufactured edges', 'BEVEL')
        mod.width = bevel
        mod.segments = 3
        obj.modifiers.new('Weighted normals', 'WEIGHTED_NORMAL')
    for poly in obj.data.polygons:
        poly.use_smooth = len(poly.vertices) == 4
    return obj

def cylinder(name, radius, depth, z, mat, xy=(0, 0), bevel=0.015):
    bpy.ops.mesh.primitive_cylinder_add(vertices=48, radius=radius, depth=depth,
                                      location=(xy[0], xy[1], z))
    return finish(bpy.context.object, name, mat, bevel)

def ring(name, radius, tube, z, mat):
    bpy.ops.mesh.primitive_torus_add(major_segments=48, minor_segments=10,
                                   major_radius=radius, minor_radius=tube, location=(0, 0, z))
    return finish(bpy.context.object, name, mat)

def tube_path(name, points, radius, mat):
    curve = bpy.data.curves.new(name, 'CURVE')
    curve.dimensions = '3D'
    curve.bevel_depth = radius
    curve.bevel_resolution = 3
    curve.use_fill_caps = True
    spline = curve.splines.new('POLY')
    spline.points.add(len(points) - 1)
    for p, co in zip(spline.points, points):
        p.co = (*co, 1)
    obj = bpy.data.objects.new(name, curve)
    bpy.context.collection.objects.link(obj)
    curve.materials.append(mat)
    return obj

cylinder('Rubber non-slip foot', 0.52, 0.09, 0.045, rubber)
cylinder('Enamel battery housing', 0.55, 0.26, 0.205, paint, bevel=0.04)
cylinder('Lower steel rim', 0.565, 0.065, 0.345, metal)
cylinder('Lower chimney seat', 0.45, 0.065, 0.40, rubber)
cylinder('Interior reflector base', 0.395, 0.05, 0.455, metal)
cylinder('Warm LED diffuser column', 0.16, 0.86, 0.91, emitter, bevel=0.035)
cylinder('Diffuser top cap', 0.18, 0.05, 1.355, metal)

# Open-ended glass cylinder, with actual wall thickness.
verts = []
for z in (0.425, 1.43):
    for i in range(48):
        a = 2 * math.pi * i / 48
        verts.append((0.405 * math.cos(a), 0.405 * math.sin(a), z))
faces = [(i, (i + 1) % 48, (i + 1) % 48 + 48, i + 48) for i in range(48)]
mesh = bpy.data.meshes.new('Glass chimney mesh')
mesh.from_pydata(verts, [], faces)
mesh.update()
chimney = bpy.data.objects.new('Transparent protective glass chimney', mesh)
bpy.context.collection.objects.link(chimney)
finish(chimney, chimney.name, glass)
chimney.modifiers.new('Glass wall thickness', 'SOLIDIFY').thickness = 0.012

for i in range(6):
    a = 2 * math.pi * i / 6
    x, y = 0.485 * math.cos(a), 0.485 * math.sin(a)
    cylinder('Protective cage upright %02d' % (i + 1), 0.026, 1.08, 0.94, metal, (x, y), 0.005)
for z in (0.46, 0.96, 1.43):
    ring('Cage hoop %.2f' % z, 0.485, 0.023, z, metal)
cylinder('Upper chimney gasket', 0.43, 0.045, 1.445, rubber)
cylinder('Enamel upper housing', 0.55, 0.16, 1.54, paint, bevel=0.025)
bpy.ops.mesh.primitive_cone_add(vertices=48, radius1=0.58, radius2=0.36, depth=0.16, location=(0, 0, 1.69))
finish(bpy.context.object, 'Sloped rain hood', paint, 0.015)
cylinder('Rain hood crown', 0.36, 0.055, 1.785, paint)

for x in (-0.55, 0.55):
    pivot = cylinder('Handle hinge pin', 0.065, 0.10, 1.57, metal, (x, 0))
    pivot.rotation_euler[1] = math.pi / 2
handle = [(0.62 * math.cos(math.pi * i / 48), 0,
           1.57 + 0.98 * math.sin(math.pi * i / 48)) for i in range(49)]
tube_path('Arched steel carry handle', handle, 0.032, metal)
tube_path('Rubber handle grip', handle[17:32], 0.053, rubber)
knob = cylinder('Front brightness control dial', 0.10, 0.09, 0.21, rubber, (0, -0.56))
knob.rotation_euler[0] = math.pi / 2
indicator = cylinder('Dial indicator dot', 0.014, 0.008, 0.255, metal, (0, -0.609), 0)
indicator.rotation_euler[0] = math.pi / 2

cylinder('Circular display plinth', 1.4, 0.08, -0.045, ground, bevel=0.025)
scene = bpy.context.scene
scene.world.color = (0.25, 0.25, 0.25)
for name, location, energy, size in [('Key softbox', (3, -4, 5), 650, 4), ('Rim softbox', (-3, 2, 4), 800, 3)]:
    bpy.ops.object.light_add(type='AREA', location=location)
    lamp = bpy.context.object
    lamp.name = name
    lamp.data.energy = energy
    lamp.data.size = size
    lamp.rotation_euler = (Vector((0, 0, 1.1)) - lamp.location).to_track_quat('-Z', 'Y').to_euler()
bpy.ops.object.camera_add(location=(3.3, -5.8, 3.1))
camera = bpy.context.object
camera.name = 'Lantern product camera'
camera.rotation_euler = (Vector((0, 0, 1.23)) - camera.location).to_track_quat('-Z', 'Y').to_euler()
camera.data.type = 'ORTHO'
camera.data.ortho_scale = 3.6
scene.camera = camera
scene.render.resolution_x = 1000
scene.render.resolution_y = 1100
scene.render.resolution_percentage = 100
