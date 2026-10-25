import bpy
import math
from mathutils import Vector

# Loading dock dimensions are in metres.
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)

def material(name, color, metallic=0.0, roughness=0.6):
    m = bpy.data.materials.new(name)
    m.diffuse_color = (*color, 1)
    m.use_nodes = True
    bsdf = m.node_tree.nodes.get('Principled BSDF')
    bsdf.inputs['Base Color'].default_value = (*color, 1)
    bsdf.inputs['Metallic'].default_value = metallic
    bsdf.inputs['Roughness'].default_value = roughness
    return m

concrete = material('Cast concrete', (0.43, 0.46, 0.47))
wall = material('Warm industrial masonry', (0.65, 0.62, 0.54))
steel = material('Galvanized steel', (0.42, 0.49, 0.53), 0.7)
door = material('Blue gray door panels', (0.19, 0.29, 0.35), 0.45)
rubber = material('Black rubber', (0.025, 0.03, 0.034))
yellow = material('Safety yellow', (0.95, 0.59, 0.035), 0.15)
asphalt = material('Asphalt apron', (0.105, 0.12, 0.135))
white = material('Painted markings', (0.86, 0.86, 0.76))

def box(name, location, size, mat, bevel=0.025):
    bpy.ops.mesh.primitive_cube_add(size=1, location=location)
    ob = bpy.context.object
    ob.name = name
    ob.dimensions = size
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    ob.data.materials.append(mat)
    if bevel:
        mod = ob.modifiers.new('Soft manufactured edges', 'BEVEL')
        mod.width = bevel
        mod.segments = 2
        ob.modifiers.new('Weighted corner normals', 'WEIGHTED_NORMAL')
    return ob

def tube(name, start, end, radius, mat):
    direction = Vector(end) - Vector(start)
    bpy.ops.mesh.primitive_cylinder_add(vertices=16, radius=radius,
        depth=direction.length, location=(Vector(start) + Vector(end)) / 2)
    ob = bpy.context.object
    ob.name = name
    ob.rotation_euler = direction.to_track_quat('Z', 'Y').to_euler()
    ob.data.materials.append(mat)
    return ob

box('Asphalt service yard', (0, -0.9, -0.13), (15, 14, 0.25), asphalt)
box('Raised concrete loading platform', (0, 1, 0.6), (10, 4, 1.2), concrete)
box('Warehouse wall left of opening', (-3, 2.75, 2.85), (4, 0.4, 3.3), wall)
box('Warehouse wall right of opening', (4, 2.75, 2.85), (2, 0.4, 3.3), wall)
box('Warehouse lintel', (0, 2.75, 5.1), (10, 0.4, 1.2), wall)
box('Roof coping', (0, 2.75, 5.75), (10.3, 0.65, 0.15), steel)
box('Dark door opening backing', (1, 2.87, 2.85), (4, 0.08, 3.3), rubber)
for i in range(8):
    z = 1.23 + (i + 0.5) * 0.4
    box('Overhead door section %02d' % (i + 1), (1, 2.57, z),
        (3.88, 0.15, 0.385), door, 0.018)
    for x in (-0.35, 1, 2.35):
        box('Panel reinforcing rib', (x, 2.481, z), (0.045, 0.028, 0.29), steel, 0.008)
for x in (-1.04, 3.04):
    box('Vertical door guide', (x, 2.47, 2.88), (0.14, 0.24, 3.4), steel)
box('Door header housing', (1, 2.44, 4.58), (4.3, 0.36, 0.22), steel)
box('Bottom weather seal', (1, 2.46, 1.245), (3.9, 0.12, 0.09), rubber)
box('Door lifting handle', (1, 2.35, 1.65), (0.42, 0.09, 0.06), steel)
box('Dock leveler inset', (1, 0.05, 1.205), (2.5, 1.85, 0.035), steel)
box('Dock leveler hinged lip', (1, -0.99, 1.19), (2.5, 0.27, 0.07), steel)
for x in (-1.25, 3.25):
    box('Bumper steel mounting plate', (x, -1.045, 0.69), (0.56, 0.09, 0.91), steel)
    box('Dock impact bumper', (x, -1.17, 0.69), (0.43, 0.23, 0.79), rubber, 0.055)
    for z in (0.38, 0.99):
        tube('Bumper mounting bolt', (x, -1.295, z), (x, -1.32, z), 0.035, steel)

# Solid wedge: the ramp rises from the yard to the left side of the dock.
verts = [(-4.85,-6,0),(-2.65,-6,0),(-2.65,-1,0),(-4.85,-1,0),
         (-4.85,-6,0.04),(-2.65,-6,0.04),(-2.65,-1,1.2),(-4.85,-1,1.2)]
faces = [(0,3,2,1),(4,5,6,7),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7)]
mesh = bpy.data.meshes.new('Ramp wedge mesh')
mesh.from_pydata(verts, [], faces)
mesh.update()
ramp = bpy.data.objects.new('Concrete access ramp', mesh)
bpy.context.collection.objects.link(ramp)
ramp.data.materials.append(concrete)
for x in (-4.78, -2.72):
    for y in (-5.75, -3.5, -1.2):
        z = 0.04 + (y + 6) * 1.16 / 5
        tube('Ramp railing post', (x,y,z), (x,y,z+0.98), 0.035, yellow)
    tube('Sloping handrail', (x,-5.8,1.066), (x,-1.05,2.168), 0.045, yellow)
    tube('Ramp intermediate rail', (x,-5.8,0.62), (x,-1.05,1.722), 0.025, yellow)
for x in (-1.05, 3.05):
    box('Truck alignment stripe', (x,-4,0.004), (0.1,4.8,0.012), white, 0)
for x in (-1.5, 3.5):
    tube('Door protection bollard', (x,2.05,1.2), (x,2.05,2.2), 0.085, yellow)

bpy.ops.object.camera_add(location=(12,-16,11))
camera = bpy.context.object
camera.name = 'Loading dock overview camera'
camera.rotation_euler = (Vector((0,-0.6,2.1)) - camera.location).to_track_quat('-Z','Y').to_euler()
camera.data.type = 'ORTHO'
camera.data.ortho_scale = 17
bpy.context.scene.camera = camera
bpy.ops.object.light_add(type='AREA', location=(1,-5,12))
bpy.context.object.data.energy = 2300
bpy.context.object.data.shape = 'DISK'
bpy.context.object.data.size = 9
bpy.context.scene.world.color = (0.25,0.25,0.25)
bpy.context.scene.render.resolution_x = 1400
bpy.context.scene.render.resolution_y = 1000
bpy.context.scene.render.resolution_percentage = 100
