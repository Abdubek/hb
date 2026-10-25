import bpy
from mathutils import Vector
from math import pi, sin, cos

bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)

def material(name, rgb, metal=0, rough=0.45):
    m = bpy.data.materials.new(name)
    m.diffuse_color = (*rgb, 1)
    m.use_nodes = True
    bs = m.node_tree.nodes.get('Principled BSDF')
    bs.inputs['Base Color'].default_value = (*rgb, 1)
    bs.inputs['Metallic'].default_value = metal
    bs.inputs['Roughness'].default_value = rough
    return m

def box(name, pos, size, mat, bevel=0.02):
    bpy.ops.mesh.primitive_cube_add(size=1, location=pos)
    ob = bpy.context.object
    ob.name = name
    ob.dimensions = size
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    ob.data.materials.append(mat)
    mod = ob.modifiers.new('Cabinet edge radius', 'BEVEL')
    mod.width = bevel
    mod.segments = 3
    ob.modifiers.new('Weighted normals', 'WEIGHTED_NORMAL')
    return ob

def disc(name, x, y, z, radius, depth, mat):
    bpy.ops.mesh.primitive_cylinder_add(vertices=48, radius=radius, depth=depth, location=(x, y, z), rotation=(pi/2, 0, 0))
    ob = bpy.context.object
    ob.name = name
    ob.data.materials.append(mat)
    mod = ob.modifiers.new('Machined rim edges', 'BEVEL')
    mod.width = min(0.006, depth/3)
    mod.segments = 2
    ob.modifiers.new('Weighted normals', 'WEIGHTED_NORMAL')
    return ob

def ring(name, z, y, major, minor, mat):
    bpy.ops.mesh.primitive_torus_add(major_segments=48, minor_segments=10, location=(0, y, z), rotation=(pi/2, 0, 0), major_radius=major, minor_radius=minor)
    ob = bpy.context.object
    ob.name = name
    ob.data.materials.append(mat)
    for p in ob.data.polygons:
        p.use_smooth = True

def diaphragm(name, z, outer_radius, inner_radius, outer_y, inner_y, mat):
    verts, faces = [], []
    count = 48
    for radius, y in [(outer_radius, outer_y), (inner_radius, inner_y)]:
        for i in range(count):
            a = 2*pi*i/count
            verts.append((radius*cos(a), y, z+radius*sin(a)))
    for i in range(count):
        j = (i+1)%count
        faces.append((i, j, count+j, count+i))
    mesh = bpy.data.meshes.new(name+' mesh')
    mesh.from_pydata(verts, [], faces)
    mesh.update()
    ob = bpy.data.objects.new(name, mesh)
    bpy.context.collection.objects.link(ob)
    ob.data.materials.append(mat)
    for p in mesh.polygons:
        p.use_smooth = True

walnut = material('Walnut cabinet', (0.25, 0.115, 0.048))
baffle = material('Graphite front baffle', (0.048, 0.055, 0.065))
rubber = material('Soft driver surrounds', (0.016, 0.019, 0.024), rough=0.8)
cone = material('Woven charcoal cones', (0.095, 0.105, 0.12), rough=0.7)
metal = material('Brushed aluminum trim', (0.39, 0.43, 0.47), 0.85, 0.3)
black = material('Recess black', (0.008, 0.01, 0.014))
led = material('Green power indicator', (0.16, 0.75, 0.35), rough=0.22)
desk = material('Desk surface', (0.46, 0.48, 0.49), rough=0.8)

box('Walnut speaker enclosure', (0, 0, 0.68), (0.76, 0.59, 1.25), walnut, 0.045)
box('Inset front baffle', (0, -0.304, 0.69), (0.69, 0.038, 1.15), baffle, 0.026)
for x in (-0.26, 0.26):
    for y in (-0.19, 0.19):
        box('Isolation foot', (x, y, 0.032), (0.12, 0.12, 0.054), rubber, 0.018)

# Front faces negative Y. Driver cones recess behind their rolled surrounds.
for name, z, radius in [('Woofer', 0.48, 0.265), ('Tweeter', 1.015, 0.155)]:
    disc(name+' mounting plate', 0, -0.337, z, radius, 0.035, black)
    ring(name+' trim ring', z, -0.360, radius-0.011, 0.010, metal)
    ring(name+' compliant surround', z, -0.367, radius*0.79, radius*0.10, rubber)
    diaphragm(name+' recessed cone', z, radius*0.77, radius*0.27, -0.370, -0.357, cone)
    bpy.ops.mesh.primitive_uv_sphere_add(segments=32, ring_count=16, radius=1, location=(0, -0.36, z))
    cap = bpy.context.object
    cap.name = name+' dust dome'
    cap.scale = (radius*0.30, radius*0.18, radius*0.30)
    cap.data.materials.append(cone if name == 'Woofer' else black)
    for p in cap.data.polygons:
        p.use_smooth = True
    for i in range(4):
        a = pi/4+i*pi/2
        x, zz = radius*0.91*cos(a), z+radius*0.91*sin(a)
        disc(name+' mounting screw '+str(i+1), x, -0.363, zz, 0.009, 0.009, metal)
        box(name+' screw slot '+str(i+1), (x, -0.369, zz), (0.011, 0.003, 0.002), black, 0.0005)

box('Brand badge', (-0.18, -0.329, 0.16), (0.16, 0.012, 0.035), metal, 0.005)
disc('Volume knob base', 0.22, -0.335, 0.15, 0.047, 0.018, black)
disc('Volume knob', 0.22, -0.359, 0.15, 0.035, 0.04, metal)
box('Volume position mark', (0.22, -0.382, 0.171), (0.005, 0.003, 0.012), black, 0.001)
disc('Power LED', 0.105, -0.331, 0.15, 0.009, 0.01, led)
box('Desktop', (0, 0, -0.04), (4, 3, 0.08), desk, 0.025)
bpy.ops.object.camera_add(location=(2.1, -3.4, 1.9))
cam = bpy.context.object
cam.name = 'Speaker product camera'
cam.rotation_euler = (Vector((0, -0.03, 0.66))-cam.location).to_track_quat('-Z', 'Y').to_euler()
cam.data.type = 'ORTHO'
cam.data.ortho_scale = 1.95
bpy.context.scene.camera = cam
bpy.ops.object.light_add(type='AREA', location=(-2, -3, 4))
bpy.context.object.data.energy = 450
bpy.context.object.data.size = 3
bpy.context.scene.world.color = (0.22, 0.22, 0.22)
