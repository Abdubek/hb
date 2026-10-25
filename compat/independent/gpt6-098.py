import bpy
import math
from mathutils import Vector

bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)

def material(name, color, metallic=0.0, roughness=0.3):
    m = bpy.data.materials.new(name)
    m.diffuse_color = (*color, 1)
    m.use_nodes = True
    bs = m.node_tree.nodes.get('Principled BSDF')
    bs.inputs['Base Color'].default_value = (*color, 1)
    bs.inputs['Metallic'].default_value = metallic
    bs.inputs['Roughness'].default_value = roughness
    return m

ceramic = material('Glazed porcelain', (0.91, 0.95, 0.94), 0, 0.19)
chrome = material('Polished chrome', (0.66, 0.72, 0.77), 0.95, 0.17)
dark = material('Drain recess and aerator', (0.025, 0.033, 0.036), 0.3)
floor_mat = material('Warm stone floor', (0.38, 0.35, 0.31), 0, 0.75)
wall_mat = material('Sage plaster', (0.36, 0.46, 0.43), 0, 0.85)

def box(name, loc, dimensions, mat, bevel=0.03):
    bpy.ops.mesh.primitive_cube_add(size=1, location=loc)
    o = bpy.context.object
    o.name = name
    o.dimensions = dimensions
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    o.data.materials.append(mat)
    if bevel:
        mod = o.modifiers.new('Rounded edges', 'BEVEL')
        mod.width = bevel
        mod.segments = 3
        o.modifiers.new('Weighted normals', 'WEIGHTED_NORMAL')
    return o

def cylinder(name, loc, radius, depth, mat):
    bpy.ops.mesh.primitive_cylinder_add(vertices=48, radius=radius, depth=depth, location=loc)
    o = bpy.context.object
    o.name = name
    o.data.materials.append(mat)
    mod = o.modifiers.new('Edge highlights', 'BEVEL')
    mod.width = 0.008
    mod.segments = 3
    o.modifiers.new('Weighted normals', 'WEIGHTED_NORMAL')
    return o

def revolve(name, profile, sx, sy, mat, offset_y=0):
    # Closed cross-section swept around Z; profile follows the material boundary.
    n = 64
    verts = [(r*sx*math.cos(2*math.pi*j/n), offset_y+r*sy*math.sin(2*math.pi*j/n), z)
             for r, z in profile for j in range(n)]
    faces = []
    for i in range(len(profile)):
        nxt = (i+1) % len(profile)
        for j in range(n):
            k = (j+1) % n
            faces.append((i*n+j, nxt*n+j, nxt*n+k, i*n+k))
    mesh = bpy.data.meshes.new(name+' mesh')
    mesh.from_pydata(verts, [], faces)
    mesh.update()
    o = bpy.data.objects.new(name, mesh)
    bpy.context.collection.objects.link(o)
    o.data.materials.append(mat)
    for p in mesh.polygons:
        p.use_smooth = True
    return o

# Interior descends to a real central drain opening; the return path forms the underside.
bowl_profile = [(0.09, 2.62), (0.17, 2.63), (0.28, 2.66), (0.42, 2.72),
                (0.58, 2.82), (0.73, 2.96), (0.85, 3.10), (0.91, 3.18),
                (0.95, 3.21), (1.00, 3.21), (1.04, 3.18), (1.045, 3.12),
                (1.01, 3.04), (0.90, 2.88), (0.74, 2.70), (0.54, 2.55),
                (0.32, 2.48), (0.09, 2.48)]
revolve('Oval washbasin with thick rolled rim', bowl_profile, 1.26, 0.84, ceramic)
# Hollow pedestal with a broad foot and a narrower column supporting the basin.
pedestal_profile = [(0.46, 0.04), (0.49, 0.08), (0.49, 0.17), (0.43, 0.25),
                    (0.33, 0.37), (0.29, 0.70), (0.27, 1.45), (0.29, 2.12),
                    (0.38, 2.43), (0.47, 2.56), (0.34, 2.56), (0.20, 2.15),
                    (0.18, 0.37), (0.35, 0.14), (0.35, 0.04)]
revolve('Porcelain pedestal', pedestal_profile, 1, 0.86, ceramic, 0.13)
box('Rear faucet mounting deck', (0, 0.73, 3.125), (1.32, 0.31, 0.15), ceramic, 0.065)
cylinder('Faucet mounting escutcheon', (0, 0.72, 3.22), 0.145, 0.045, chrome)
cylinder('Mixer body', (0, 0.72, 3.39), 0.105, 0.32, chrome)

# A continuous beveled curve gives the faucet a smooth swan-neck silhouette.
curve = bpy.data.curves.new('Curved faucet tube path', 'CURVE')
curve.dimensions = '3D'
curve.resolution_u = 16
curve.bevel_depth = 0.065
curve.bevel_resolution = 4
curve.use_fill_caps = True
spline = curve.splines.new('BEZIER')
points = [(0, 0.72, 3.46), (0, 0.72, 3.86), (0, 0.56, 4.02),
          (0, 0.24, 4.02), (0, 0.06, 3.85), (0, 0.06, 3.72)]
spline.bezier_points.add(len(points)-1)
for bp, co in zip(spline.bezier_points, points):
    bp.co = co
    bp.handle_left_type = 'AUTO'
    bp.handle_right_type = 'AUTO'
faucet = bpy.data.objects.new('Chrome swan-neck faucet', curve)
bpy.context.collection.objects.link(faucet)
faucet.data.materials.append(chrome)
cylinder('Spout aerator collar', (0, 0.06, 3.72), 0.078, 0.085, chrome)
cylinder('Recessed aerator face', (0, 0.06, 3.676), 0.058, 0.006, dark)
box('Mixer lever pivot', (0.13, 0.72, 3.45), (0.13, 0.12, 0.12), chrome)
box('Single mixer lever', (0.23, 0.66, 3.56), (0.07, 0.29, 0.22), chrome, 0.025)

revolve('Circular drain flange', [(0.095, 2.625), (0.145, 2.642),
        (0.151, 2.632), (0.145, 2.613), (0.095, 2.606)], 1, 1, chrome)
cylinder('Dark drain well', (0, 0, 2.604), 0.095, 0.02, dark)
cylinder('Drain strainer', (0, 0, 2.618), 0.084, 0.012, chrome)
for i in range(8):
    a = i*2*math.pi/8
    cylinder('Strainer perforation %02d' % i, (0.055*math.cos(a), 0.055*math.sin(a), 2.625), 0.012, 0.003, dark)
cylinder('Strainer center screw', (0, 0, 2.627), 0.017, 0.008, chrome)
# A dark inset with a chrome surround suggests the rear overflow opening.
overflow = cylinder('Overflow chrome bezel', (0, 0.697, 3.065), 0.062, 0.014, chrome)
overflow.rotation_euler.x = math.radians(90)
inset = cylinder('Overflow dark opening', (0, 0.686, 3.065), 0.043, 0.015, dark)
inset.rotation_euler.x = math.radians(90)
box('Stone floor', (0, 0, -0.06), (200, 200, 0.1), floor_mat, 0)
box('Bathroom wall', (0, 1.18, 2.6), (8, 0.15, 5.3), wall_mat, 0)
box('Porcelain skirting', (0, 1.075, 0.12), (8, 0.065, 0.24), ceramic, 0.01)

bpy.ops.object.camera_add(location=(5.0, -7.3, 6.6))
cam = bpy.context.object
cam.name = 'Washbasin presentation camera'
cam.rotation_euler = (Vector((0, 0.10, 2.10))-cam.location).to_track_quat('-Z', 'Y').to_euler()
cam.data.type = 'ORTHO'
cam.data.ortho_scale = 5.5
bpy.context.scene.camera = cam
for name, loc, power, size in [('Softbox key', (2, -4, 7), 1100, 4), ('Softbox fill', (-4, -2, 5), 850, 3)]:
    bpy.ops.object.light_add(type='AREA', location=loc)
    light = bpy.context.object
    light.name = name
    light.data.energy = power
    light.data.size = size
    light.rotation_euler = (Vector((0, 0, 2))-light.location).to_track_quat('-Z', 'Y').to_euler()
bpy.context.scene.world.color = (0.25, 0.25, 0.25)
bpy.context.scene.render.resolution_x = 1000
bpy.context.scene.render.resolution_y = 1000
bpy.context.scene.render.resolution_percentage = 100
