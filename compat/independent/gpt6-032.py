import bpy
import math
from mathutils import Vector

# Four-way urban junction with pedestrian crossings and protective bollards.
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)

def material(name, color, metallic=0.0, emission=0.0):
    m = bpy.data.materials.new(name)
    m.diffuse_color = (*color, 1)
    m.use_nodes = True
    bs = m.node_tree.nodes.get('Principled BSDF')
    bs.inputs['Base Color'].default_value = (*color, 1)
    bs.inputs['Metallic'].default_value = metallic
    bs.inputs['Roughness'].default_value = 0.48
    if emission:
        bs.inputs['Emission Color'].default_value = (*color, 1)
        bs.inputs['Emission Strength'].default_value = emission
    return m

def box(name, loc, size, mat, bevel=0.0, angle=0.0):
    bpy.ops.mesh.primitive_cube_add(size=1, location=loc)
    obj = bpy.context.object
    obj.name = name
    obj.dimensions = size
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    obj.rotation_euler.z = angle
    obj.data.materials.append(mat)
    if bevel:
        mod = obj.modifiers.new('Rounded edges', 'BEVEL')
        mod.width, mod.segments = bevel, 2
        obj.modifiers.new('Weighted normals', 'WEIGHTED_NORMAL')
    return obj

def rod(name, a, b, radius, mat, vertices=16):
    d = Vector(b) - Vector(a)
    bpy.ops.mesh.primitive_cylinder_add(vertices=vertices, radius=radius, depth=d.length,
        location=(Vector(a) + Vector(b)) / 2)
    obj = bpy.context.object
    obj.name = name
    obj.rotation_euler = d.to_track_quat('Z', 'Y').to_euler()
    obj.data.materials.append(mat)
    return obj

asphalt = material('Charcoal asphalt', (0.075, 0.085, 0.10))
concrete = material('Sidewalk concrete', (0.59, 0.60, 0.56))
curb = material('Pale curb stone', (0.77, 0.77, 0.70))
white = material('White road paint', (0.94, 0.93, 0.83))
yellow = material('Yellow road paint', (0.98, 0.64, 0.045))
black = material('Signal and bollard enamel', (0.025, 0.033, 0.041), 0.3)
steel = material('Galvanized poles', (0.47, 0.52, 0.56), 0.75)
tactile = material('Tactile paving ochre', (0.82, 0.48, 0.12))
red_on = material('Red illuminated', (1.0, 0.018, 0.009), emission=2.5)
red_off = material('Red dormant', (0.17, 0.009, 0.007))
amber = material('Amber dormant', (0.22, 0.09, 0.004))
green_on = material('Green illuminated', (0.02, 0.85, 0.17), emission=2.5)
green_off = material('Green dormant', (0.008, 0.13, 0.025))
box('Intersection asphalt foundation', (0, 0, -0.17), (20, 20, 0.34), asphalt, 0.12)
for sx in (-1, 1):
    for sy in (-1, 1):
        box('Corner sidewalk', (sx * 7.05, sy * 7.05, 0.10), (5.9, 5.9, 0.20), concrete, 0.06)
        box('North south curb', (sx * 4.18, sy * 7.1, 0.13), (0.22, 5.8, 0.26), curb, 0.035)
        box('East west curb', (sx * 7.1, sy * 4.18, 0.13), (5.8, 0.22, 0.26), curb, 0.035)
        box('Crossing tactile pad A', (sx * 4.65, sy * 5.0, 0.215), (0.65, 1.45, 0.03), tactile)
        box('Crossing tactile pad B', (sx * 5.0, sy * 4.65, 0.215), (1.45, 0.65, 0.03), tactile)
        for offset in (6.25, 7.65, 9.05):
            for x, y in ((sx * 4.65, sy * offset), (sx * offset, sy * 4.65)):
                rod('Bollard socket', (x, y, 0.2), (x, y, 0.29), 0.19, steel)
                rod('Protective bollard', (x, y, 0.28), (x, y, 1.13), 0.105, black)
                rod('Bollard reflective band', (x, y, 0.88), (x, y, 1.02), 0.11, white)

# Rotate one approach marking layout around the center of the junction.
for k in range(4):
    angle = k * math.pi / 2
    c, s = math.cos(angle), math.sin(angle)
    def p(x, y, z):
        return (c * x - s * y, s * x + c * y, z)
    for x in (-3.3, -2.2, -1.1, 0, 1.1, 2.2, 3.3):
        box('Zebra crossing stripe', p(x, -5.0, 0.014), (0.55, 1.7, 0.028), white, angle=angle)
    box('Incoming lane stop line', p(2.05, -6.3, 0.015), (3.55, 0.26, 0.03), white, angle=angle)
    for x in (-0.10, 0.10):
        box('Double yellow center line', p(x, -8.15, 0.015), (0.09, 3.7, 0.03), yellow, angle=angle)
    box('Straight arrow shaft', p(2, -8.1, 0.018), (0.16, 1.3, 0.035), white, angle=angle)
    verts = [p(1.57, -7.65, 0.037), p(2.43, -7.65, 0.037), p(2, -7.05, 0.037)]
    mesh = bpy.data.meshes.new('Arrowhead mesh')
    mesh.from_pydata(verts, [], [(0, 1, 2)])
    mesh.update()
    obj = bpy.data.objects.new('Straight ahead arrowhead', mesh)
    bpy.context.collection.objects.link(obj)
    obj.data.materials.append(white)

    # Each near-side signal faces approaching traffic on the right-hand lane.
    rod('Signal pole %d' % k, p(4.65, -6.15, 0.2), p(4.65, -6.15, 4.5), 0.085, steel)
    rod('Overhead signal arm %d' % k, p(4.65, -6.15, 4.4), p(2.1, -6.15, 4.4), 0.07, steel)
    box('Signal pole base', p(4.65, -6.15, 0.32), (0.35, 0.35, 0.24), black, 0.035, angle)
    box('Signal backboard %d' % k, p(2.1, -6.15, 3.85), (0.75, 0.15, 1.65), yellow, 0.055, angle)
    box('Three aspect housing %d' % k, p(2.1, -6.28, 3.85), (0.59, 0.24, 1.49), black, 0.055, angle)
    mats = [red_on if k % 2 else red_off, amber, green_off if k % 2 else green_on]
    for j, mat in enumerate(mats):
        z = 4.33 - j * 0.48
        rod('Signal lens %d %d' % (k, j), p(2.1, -6.4, z), p(2.1, -6.445, z), 0.176, mat, 24)
        box('Lens weather visor', p(2.1, -6.52, z + 0.20), (0.43, 0.38, 0.045), black, 0.015, angle)

scene = bpy.context.scene
scene.world.color = (0.28, 0.28, 0.28)
bpy.ops.object.light_add(type='AREA', location=(0, -3, 17))
bpy.context.object.data.energy, bpy.context.object.data.size = 3200, 12
bpy.ops.object.camera_add(location=(23, -29, 26))
camera = bpy.context.object
camera.rotation_euler = (Vector((0, 0, 0.6)) - camera.location).to_track_quat('-Z', 'Y').to_euler()
camera.data.type, camera.data.ortho_scale = 'ORTHO', 30
scene.camera = camera
scene.render.resolution_x, scene.render.resolution_y, scene.render.resolution_percentage = 1200, 1000, 100
