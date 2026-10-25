import bpy
import math
from mathutils import Vector

# A five-star rolling task chair, dimensions in meters.
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)

def material(name, color, metallic=0.0, roughness=0.45):
    m = bpy.data.materials.new(name)
    m.diffuse_color = (*color, 1)
    m.use_nodes = True
    bsdf = m.node_tree.nodes.get('Principled BSDF')
    bsdf.inputs['Base Color'].default_value = (*color, 1)
    bsdf.inputs['Metallic'].default_value = metallic
    bsdf.inputs['Roughness'].default_value = roughness
    return m

fabric = material('Ocean blue upholstery', (0.045, 0.19, 0.25), roughness=0.8)
plastic = material('Graphite molded polymer', (0.045, 0.052, 0.061))
metal = material('Satin aluminum', (0.46, 0.5, 0.54), 0.8, 0.28)
rubber = material('Caster rubber', (0.018, 0.022, 0.026), roughness=0.85)
floor_mat = material('Warm gray floor', (0.36, 0.34, 0.31), roughness=0.85)

def finish(obj, name, mat, bevel=0):
    obj.name = name
    obj.data.materials.append(mat)
    if bevel:
        mod = obj.modifiers.new('Rounded manufactured edges', 'BEVEL')
        mod.width = bevel
        mod.segments = 3
        obj.modifiers.new('Weighted corner normals', 'WEIGHTED_NORMAL')
    return obj

def box(name, location, dimensions, mat, bevel=0.025):
    bpy.ops.mesh.primitive_cube_add(size=1, location=location)
    obj = bpy.context.object
    obj.dimensions = dimensions
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    return finish(obj, name, mat, bevel)

def rod(name, start, end, radius, mat, bevel=0.006):
    a, b = Vector(start), Vector(end)
    bpy.ops.mesh.primitive_cylinder_add(vertices=24, radius=radius,
                                      depth=(b-a).length, location=(a+b)/2)
    obj = bpy.context.object
    obj.rotation_euler = (b-a).to_track_quat('Z', 'Y').to_euler()
    finish(obj, name, mat, bevel)
    for polygon in obj.data.polygons:
        polygon.use_smooth = len(polygon.vertices) == 4
    return obj

rod('Five-star central hub', (0, 0, 0.34), (0, 0, 0.51), 0.12, plastic)
for i in range(5):
    angle = math.radians(18 + 72*i)
    radial = Vector((math.cos(angle), math.sin(angle), 0))
    tangent = Vector((-math.sin(angle), math.cos(angle), 0))
    tip = radial * 0.57
    rod(f'Base spoke {i+1}', radial*0.075 + Vector((0, 0, 0.43)),
        tip + Vector((0, 0, 0.32)), 0.044, metal)
    rod(f'Caster swivel stem {i+1}', tip + Vector((0, 0, 0.22)),
        tip + Vector((0, 0, 0.35)), 0.035, plastic)
    center = tip - radial*0.035 + Vector((0, 0, 0.135))
    rod(f'Caster axle {i+1}', center-tangent*0.10, center+tangent*0.10, 0.026, metal)
    box(f'Caster fork {i+1}', tip + Vector((0, 0, 0.23)),
        (0.095, 0.095, 0.10), plastic, 0.015)
    for side in (-1, 1):
        wheel = center + tangent*(side*0.071)
        rod(f'Caster {i+1} wheel {side}', wheel-tangent*0.027,
            wheel+tangent*0.027, 0.13, rubber)
        outer = wheel + tangent*(side*0.029)
        rod(f'Caster {i+1} hubcap {side}', outer-tangent*0.005,
            outer+tangent*0.005, 0.05, plastic, 0.003)

rod('Gas lift housing', (0, 0, 0.44), (0, 0, 0.72), 0.065, plastic)
rod('Chrome lift piston', (0, 0, 0.69), (0, 0, 0.91), 0.04, metal)
box('Under-seat tilt mechanism', (0, 0, 0.88), (0.34, 0.35, 0.10), plastic)
box('Seat structural shell', (0, 0, 0.965), (0.70, 0.67, 0.10), plastic, 0.045)
box('Contoured seat cushion', (0, -0.025, 1.045), (0.69, 0.66, 0.14), fabric, 0.065)
rod('Backrest spine', (0, 0.25, 0.90), (0, 0.40, 1.53), 0.045, metal)
back = box('Backrest outer shell', (0, 0.36, 1.47), (0.64, 0.12, 0.74), plastic, 0.055)
back.rotation_euler.x = math.radians(-9)
pad = box('Upholstered backrest', (0, 0.285, 1.47), (0.60, 0.13, 0.69), fabric, 0.06)
pad.rotation_euler.x = math.radians(-9)
for side in (-1, 1):
    x = side*0.40
    rod(f'Armrest lower bracket {side}', (side*0.29, 0.10, 0.95),
        (x, 0.10, 1.03), 0.029, metal)
    rod(f'Armrest upright {side}', (x, 0.10, 1.01), (x, 0.10, 1.31), 0.029, metal)
    box(f'Padded armrest {side}', (x, -0.035, 1.33), (0.115, 0.43, 0.075), plastic, 0.035)
rod('Height adjustment lever', (0.12, -0.08, 0.89), (0.41, -0.12, 0.86), 0.012, metal)
box('Adjustment lever grip', (0.42, -0.12, 0.86), (0.11, 0.06, 0.04), plastic, 0.018)
box('Floor', (0, 0, -0.055), (200, 200, 0.10), floor_mat, 0)

bpy.ops.object.camera_add(location=(2.7, -3.6, 2.4))
camera = bpy.context.object
camera.name = 'Chair presentation camera'
camera.rotation_euler = (Vector((0, 0, 0.95))-camera.location).to_track_quat('-Z', 'Y').to_euler()
camera.data.type = 'ORTHO'
camera.data.ortho_scale = 2.7
bpy.context.scene.camera = camera
bpy.ops.object.light_add(type='AREA', location=(1.5, -2.5, 4))
bpy.context.object.name = 'Large softbox'
bpy.context.object.data.energy = 450
bpy.context.object.data.shape = 'DISK'
bpy.context.object.data.size = 4
bpy.context.scene.world.color = (0.22, 0.22, 0.22)
bpy.context.scene.render.resolution_x = 900
bpy.context.scene.render.resolution_y = 900
bpy.context.scene.render.resolution_percentage = 100
