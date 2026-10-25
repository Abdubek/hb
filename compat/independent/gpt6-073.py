import bpy
import math
from mathutils import Vector

# Dimensions are in meters; the net crosses the center along X.
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)

def material(name, color, roughness=0.7):
    mat = bpy.data.materials.new(name)
    mat.diffuse_color = (*color, 1)
    mat.use_nodes = True
    mat.node_tree.nodes['Principled BSDF'].inputs['Base Color'].default_value = (*color, 1)
    mat.node_tree.nodes['Principled BSDF'].inputs['Roughness'].default_value = roughness
    return mat

blue = material('Court blue', (0.045, 0.24, 0.43))
green = material('Green runoff', (0.07, 0.27, 0.18))
white = material('Paint and net binding', (0.93, 0.95, 0.91))
steel = material('Dark coated steel', (0.055, 0.075, 0.075), 0.35)
mesh_mat = material('Black net cord', (0.018, 0.024, 0.026))
concrete = material('Concrete foundation', (0.38, 0.40, 0.38))

def box(name, location, dimensions, mat):
    bpy.ops.mesh.primitive_cube_add(size=1, location=location)
    obj = bpy.context.object
    obj.name = name
    obj.dimensions = dimensions
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    obj.data.materials.append(mat)
    return obj

def rod(name, start, end, radius, mat, sides=10):
    direction = Vector(end) - Vector(start)
    bpy.ops.mesh.primitive_cylinder_add(vertices=sides, radius=radius, depth=direction.length,
                                      location=(Vector(start) + Vector(end)) / 2)
    obj = bpy.context.object
    obj.name = name
    obj.rotation_euler = direction.to_track_quat('Z', 'Y').to_euler()
    obj.data.materials.append(mat)
    return obj

box('Raised court foundation', (0, 0, -0.18), (18.5, 36.5, 0.36), concrete)
box('Runoff playing surface', (0, 0, 0.012), (18, 36, 0.024), green)
box('Doubles court surface', (0, 0, 0.03), (10.97, 23.77, 0.02), blue)
# Regulation doubles/singles sidelines, baselines, service boxes, and center marks.
for x in (-5.485, -4.115, 4.115, 5.485):
    box('Sideline X %.3f' % x, (x, 0, 0.044), (0.05, 23.77, 0.008), white)
for y in (-11.885, 11.885):
    box('Baseline Y %.3f' % y, (0, y, 0.045), (11.02, 0.1, 0.01), white)
    inward = -1 if y > 0 else 1
    box('Baseline center mark', (0, y + inward * 0.14, 0.05), (0.05, 0.18, 0.01), white)
for y in (-6.40, 6.40):
    box('Service line', (0, y, 0.046), (8.23, 0.05, 0.008), white)
box('Center service line', (0, 0, 0.046), (0.05, 12.8, 0.008), white)

# Slightly sagging net: 1.07 m at posts, 0.914 m at center, above the surface.
span = 6.40
surface = 0.05
def net_top(x):
    return surface + 0.914 + 0.156 * (abs(x) / span) ** 2
for x in (-span, span):
    box('Net post foot', (x, 0, 0.09), (0.27, 0.27, 0.08), steel)
    rod('Net support post', (x, 0, 0.1), (x, 0, 1.23), 0.065, steel)
    rod('Post cap', (x, 0, 1.23), (x, 0, 1.26), 0.082, steel)
for i in range(81):
    x = -span + 2 * span * i / 80
    rod('Net vertical cord %02d' % i, (x, 0, 0.10), (x, 0, net_top(x)), 0.006, mesh_mat, 6)
for i in range(40):
    x0 = -span + 2 * span * i / 40
    x1 = -span + 2 * span * (i + 1) / 40
    rod('White net headband', (x0, 0, net_top(x0)), (x1, 0, net_top(x1)), 0.023, white)
    for j in range(9):
        fraction = j / 9
        z0 = 0.10 + fraction * (net_top(x0) - 0.10)
        z1 = 0.10 + fraction * (net_top(x1) - 0.10)
        rod('Net horizontal cord', (x0, 0, z0), (x1, 0, z1), 0.005, mesh_mat, 6)
box('Center net strap', (0, -0.023, 0.52), (0.05, 0.016, 0.94), white)
rod('Net tension crank', (span, 0, 0.65), (span + 0.20, 0, 0.65), 0.025, steel)

# Open perimeter with evenly spaced posts and two horizontal safety rails.
perimeter = [(x, y) for y in (-17, 17) for x in (-8, -4, 0, 4, 8)]
perimeter += [(x, y) for x in (-8, 8) for y in (-12, -6, 0, 6, 12)]
for i, (x, y) in enumerate(perimeter):
    box('Perimeter footing %02d' % i, (x, y, 0.08), (0.30, 0.30, 0.12), concrete)
    rod('Perimeter post %02d' % i, (x, y, 0.10), (x, y, 2.35), 0.055, steel)
for z in (0.55, 2.25):
    for y in (-17, 17):
        rod('End perimeter rail', (-8, y, z), (8, y, z), 0.03, steel)
    for x in (-8, 8):
        rod('Side perimeter rail', (x, -17, z), (x, 17, z), 0.03, steel)

bpy.ops.object.camera_add(location=(29, -36, 31))
camera = bpy.context.object
camera.name = 'Court overview camera'
camera.rotation_euler = (Vector((0, 0, 0)) - camera.location).to_track_quat('-Z', 'Y').to_euler()
camera.data.type = 'ORTHO'
camera.data.ortho_scale = 47
bpy.context.scene.camera = camera
bpy.ops.object.light_add(type='AREA', location=(0, -6, 22))
bpy.context.object.data.energy = 3600
bpy.context.object.data.shape = 'DISK'
bpy.context.object.data.size = 20
bpy.context.scene.world.color = (0.35, 0.35, 0.35)
bpy.context.scene.render.resolution_x = 1200
bpy.context.scene.render.resolution_y = 1000
bpy.context.scene.render.resolution_percentage = 100
