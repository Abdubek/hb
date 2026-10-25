import bpy, math
from mathutils import Vector

bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)

def material(name, color, metallic=0.0, roughness=0.45):
    m = bpy.data.materials.new(name)
    m.diffuse_color = (*color, 1)
    m.use_nodes = True
    p = m.node_tree.nodes.get('Principled BSDF')
    p.inputs['Base Color'].default_value = (*color, 1)
    p.inputs['Metallic'].default_value = metallic
    p.inputs['Roughness'].default_value = roughness
    return m

wood = material('Warm oak cabinetry', (0.36, 0.19, 0.085))
stone = material('Ivory quartz', (0.84, 0.81, 0.72))
ceramic = material('Glazed white porcelain', (0.94, 0.96, 0.95), roughness=0.16)
chrome = material('Brushed nickel', (0.65, 0.70, 0.72), 0.9, 0.2)
mirror = material('Silver mirror', (0.92, 0.95, 0.97), 1.0, 0.025)
dark = material('Dark recesses', (0.035, 0.043, 0.044))
wall = material('Sage wall', (0.34, 0.44, 0.39))
floor = material('Warm limestone floor', (0.61, 0.59, 0.53))

def box(name, location, dimensions, mat, bevel=0.015):
    bpy.ops.mesh.primitive_cube_add(size=1, location=location)
    o = bpy.context.object
    o.name = name
    o.dimensions = dimensions
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    o.data.materials.append(mat)
    if bevel:
        mod = o.modifiers.new('Soft manufactured edges', 'BEVEL')
        mod.width = bevel
        mod.segments = 3
        o.modifiers.new('Weighted corner normals', 'WEIGHTED_NORMAL')
    return o

def pipe(name, points, radius, mat):
    curve = bpy.data.curves.new(name, 'CURVE')
    curve.dimensions = '3D'
    curve.bevel_depth = radius
    curve.bevel_resolution = 3
    spline = curve.splines.new('BEZIER')
    spline.bezier_points.add(len(points)-1)
    for p, co in zip(spline.bezier_points, points):
        p.co = co
        p.handle_left_type = 'AUTO'
        p.handle_right_type = 'AUTO'
    o = bpy.data.objects.new(name, curve)
    bpy.context.collection.objects.link(o)
    o.data.materials.append(mat)
    return o

box('Bathroom floor', (0, -0.7, -0.055), (4.6, 3.4, 0.11), floor)
box('Vanity backsplash wall', (0, 0.64, 1.65), (4.6, 0.12, 3.3), wall)
box('Recessed toe kick', (0, 0.03, 0.18), (2.24, 0.73, 0.25), dark)
box('Cabinet carcass', (0, 0, 0.69), (2.4, 0.88, 0.84), wood)
for x in (-0.595, 0.595):
    for z in (0.49, 0.9):
        box('Oak drawer front', (x, -0.463, z), (1.16, 0.045, 0.385), wood)
        box('Nickel drawer pull', (x, -0.517, z+0.09), (0.35, 0.045, 0.025), chrome, 0.009)
# Four quartz pieces form a real opening for the basin.
box('Counter left wing', (-0.945, 0, 1.16), (0.61, 0.98, 0.1), stone)
box('Counter right wing', (0.945, 0, 1.16), (0.61, 0.98, 0.1), stone)
for y in (-0.39, 0.39):
    box('Counter bridge', (0, y, 1.16), (1.28, 0.2, 0.1), stone)
box('Quartz backsplash', (0, 0.51, 1.29), (2.5, 0.055, 0.25), stone)
# Continuous bowl surface: outer rim, inner lip, sloping cavity, flat basin floor.
verts = []
for hx, hy, z in ((0.68, 0.33, 1.22), (0.59, 0.245, 1.22), (0.45, 0.16, 0.99)):
    verts.extend([(-hx,-hy,z), (hx,-hy,z), (hx,hy,z), (-hx,hy,z)])
faces = []
for ring in range(2):
    for i in range(4):
        j = (i+1) % 4
        faces.append((ring*4+i, ring*4+j, (ring+1)*4+j, (ring+1)*4+i))
faces.append((8,9,10,11))
mesh = bpy.data.meshes.new('Open basin mesh')
mesh.from_pydata(verts, [], faces)
mesh.update()
basin = bpy.data.objects.new('Inset porcelain sink bowl', mesh)
bpy.context.collection.objects.link(basin)
basin.data.materials.append(ceramic)
solid = basin.modifiers.new('Porcelain thickness', 'SOLIDIFY')
solid.thickness = 0.018
bev = basin.modifiers.new('Rounded basin edges', 'BEVEL')
bev.width = 0.025
bev.segments = 4
bpy.ops.mesh.primitive_cylinder_add(vertices=32, radius=0.044, depth=0.008, location=(0, 0.035, 0.996))
bpy.context.object.name = 'Sink drain cover'
bpy.context.object.data.materials.append(chrome)
box('Faucet mounting plate', (0, 0.375, 1.225), (0.23, 0.13, 0.026), chrome)
pipe('Arched mixer faucet', [(0,0.375,1.24), (0,0.375,1.57), (0,0.26,1.66), (0,0.04,1.62), (0,0.015,1.55)], 0.027, chrome)
box('Mixer lever', (0.095, 0.375, 1.4), (0.15, 0.035, 0.025), chrome)
box('Mirror nickel frame', (0, 0.553, 2.18), (1.95, 0.06, 1.32), chrome, 0.035)
box('Mirror glass', (0, 0.515, 2.18), (1.86, 0.018, 1.23), mirror, 0.02)
box('Folded hand towel', (-0.95, -0.02, 1.245), (0.35, 0.5, 0.055), ceramic)
box('Soap dispenser', (0.94, 0.24, 1.34), (0.12, 0.12, 0.25), ceramic)
pipe('Soap pump', [(0.94,0.24,1.47), (0.94,0.24,1.51), (0.94,0.15,1.51)], 0.012, chrome)

world = bpy.data.worlds.new('Bathroom ambient')
bpy.context.scene.world = world
world.use_nodes = True
world.node_tree.nodes['Background'].inputs[0].default_value = (0.65, 0.72, 0.8, 1)
world.node_tree.nodes['Background'].inputs[1].default_value = 0.35
for name, loc, power, size in [('Softbox', (1,-3,4.7), 850, 4), ('Fill', (-3,-1,3), 450, 3)]:
    bpy.ops.object.light_add(type='AREA', location=loc)
    o = bpy.context.object
    o.name = name
    o.data.energy = power
    o.data.shape = 'DISK'
    o.data.size = size
    o.rotation_euler = (Vector((0,0,1.3))-o.location).to_track_quat('-Z','Y').to_euler()
bpy.ops.object.camera_add(location=(3.5,-5.2,3.35))
camera = bpy.context.object
camera.name = 'Vanity presentation camera'
camera.rotation_euler = (Vector((0,0,1.45))-camera.location).to_track_quat('-Z','Y').to_euler()
camera.data.lens = 48
bpy.context.scene.camera = camera
