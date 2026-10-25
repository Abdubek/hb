import bpy
import math
from mathutils import Vector

# Freestanding coat rack, in meters.
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)

def material(name, color, metallic=0.0, roughness=0.4):
    mat = bpy.data.materials.new(name)
    mat.diffuse_color = (*color, 1)
    mat.use_nodes = True
    bsdf = mat.node_tree.nodes.get('Principled BSDF')
    bsdf.inputs['Base Color'].default_value = (*color, 1)
    bsdf.inputs['Metallic'].default_value = metallic
    bsdf.inputs['Roughness'].default_value = roughness
    return mat

wood = material('Warm walnut', (0.24, 0.095, 0.038), roughness=0.32)
steel = material('Graphite powder coated steel', (0.045, 0.055, 0.065), 0.7)
brass = material('Satin brass trim', (0.58, 0.36, 0.12), 0.75)
rubber = material('Rubber underside', (0.018, 0.018, 0.022), roughness=0.8)
floor_mat = material('Warm studio floor', (0.64, 0.61, 0.56), roughness=0.8)

def finish(obj, name, mat, bevel=0):
    obj.name = name
    obj.data.materials.append(mat)
    if bevel:
        mod = obj.modifiers.new('Soft manufactured edges', 'BEVEL')
        mod.width = bevel
        mod.segments = 3
        obj.modifiers.new('Weighted corner normals', 'WEIGHTED_NORMAL')
    return obj

def cylinder(name, radius, depth, location, mat, bevel=0.008):
    bpy.ops.mesh.primitive_cylinder_add(vertices=48, radius=radius, depth=depth, location=location)
    return finish(bpy.context.object, name, mat, bevel)

def ball(name, location, radius, mat):
    bpy.ops.mesh.primitive_uv_sphere_add(segments=20, ring_count=12, radius=radius, location=location)
    obj = finish(bpy.context.object, name, mat)
    for poly in obj.data.polygons:
        poly.use_smooth = True
    return obj

def hook(name, angle, height, reach):
    # Rising outer tips retain coats without sharp exposed ends.
    profile = [(0.075, height), (0.20, height - 0.045),
               (reach * 0.83, height + 0.045), (reach, height + 0.19),
               (reach * 0.98, height + 0.29)]
    points = [(r * math.cos(angle), r * math.sin(angle), z) for r, z in profile]
    curve = bpy.data.curves.new(name + ' path', 'CURVE')
    curve.dimensions = '3D'
    curve.resolution_u = 12
    curve.bevel_depth = 0.017
    curve.bevel_resolution = 3
    curve.use_fill_caps = True
    spline = curve.splines.new('BEZIER')
    spline.bezier_points.add(len(points) - 1)
    for point, co in zip(spline.bezier_points, points):
        point.co = co
        point.handle_left_type = 'AUTO'
        point.handle_right_type = 'AUTO'
    obj = bpy.data.objects.new(name, curve)
    bpy.context.collection.objects.link(obj)
    obj.data.materials.append(steel)
    ball(name + ' rounded walnut tip', points[-1], 0.033, wood)

cylinder('Non slip base pad', 0.385, 0.018, (0, 0, 0.019), rubber)
cylinder('Weighted circular base', 0.43, 0.075, (0, 0, 0.064), steel, 0.022)
cylinder('Brass base inset', 0.27, 0.012, (0, 0, 0.106), brass, 0.004)
cylinder('Central support socket', 0.105, 0.15, (0, 0, 0.17), steel)
cylinder('Solid walnut upright', 0.061, 2.03, (0, 0, 1.255), wood)
cylinder('Upper hook mounting collar', 0.086, 0.085, (0, 0, 1.98), brass)
cylinder('Lower hook mounting collar', 0.082, 0.075, (0, 0, 1.34), brass)
for index in range(6):
    hook('Upper coat hook %02d' % (index + 1), index * math.tau / 6, 1.98, 0.43)
for index in range(3):
    hook('Lower bag hook %02d' % (index + 1), index * math.tau / 3 + math.pi / 6, 1.34, 0.29)
ball('Walnut crown finial', (0, 0, 2.30), 0.082, wood)

bpy.ops.mesh.primitive_plane_add(size=200)
finish(bpy.context.object, 'Ground', floor_mat)
bpy.ops.object.camera_add(location=(3.5, -4.8, 3.0))
camera = bpy.context.object
camera.name = 'Coat rack presentation camera'
camera.rotation_euler = (Vector((0, 0, 1.18)) - camera.location).to_track_quat('-Z', 'Y').to_euler()
camera.data.type = 'ORTHO'
camera.data.ortho_scale = 3.05
scene = bpy.context.scene
scene.camera = camera
for name, location, energy, size in [('Key softbox', (3, -4, 5), 650, 4), ('Rim softbox', (-3, 2, 4), 450, 3)]:
    bpy.ops.object.light_add(type='AREA', location=location)
    light = bpy.context.object
    light.name = name
    light.data.energy = energy
    light.data.shape = 'DISK'
    light.data.size = size
    light.rotation_euler = (Vector((0, 0, 1.2)) - light.location).to_track_quat('-Z', 'Y').to_euler()
scene.world.color = (0.22, 0.22, 0.22)
scene.render.resolution_x = 800
scene.render.resolution_y = 1000
scene.render.resolution_percentage = 100
