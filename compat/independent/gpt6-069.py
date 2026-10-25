import bpy
import math
from mathutils import Vector

bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)

def material(name, color, metallic=0.0, roughness=0.4):
    m = bpy.data.materials.new(name)
    m.diffuse_color = (*color, 1)
    m.use_nodes = True
    bs = m.node_tree.nodes.get('Principled BSDF')
    bs.inputs['Base Color'].default_value = (*color, 1)
    bs.inputs['Metallic'].default_value = metallic
    bs.inputs['Roughness'].default_value = roughness
    return m

alloy = material('Satin aluminum', (0.35, 0.39, 0.44), 0.8)
black = material('Black anodized hardware', (0.035, 0.045, 0.055), 0.65)
rubber = material('Rubber grips and feet', (0.018, 0.021, 0.025), 0, 0.8)
orange = material('Orange adjustment accents', (0.85, 0.19, 0.035), 0.45)
ground = material('Studio floor', (0.22, 0.25, 0.28))

def finish(obj, name, mat, bevel=0):
    obj.name = name
    obj.data.materials.append(mat)
    if bevel:
        mod = obj.modifiers.new('Soft manufactured edges', 'BEVEL')
        mod.width = bevel
        mod.segments = 2
        obj.modifiers.new('Weighted corner normals', 'WEIGHTED_NORMAL')
    return obj

def box(name, location, scale, mat, bevel=0.02):
    bpy.ops.mesh.primitive_cube_add(size=1, location=location)
    obj = bpy.context.object
    obj.dimensions = scale
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    return finish(obj, name, mat, bevel)

def rod(name, a, b, radius, mat, radius2=None):
    a, b = Vector(a), Vector(b)
    direction = b - a
    bpy.ops.mesh.primitive_cone_add(vertices=24, radius1=radius,
        radius2=radius if radius2 is None else radius2,
        depth=direction.length, location=(a + b) / 2)
    obj = bpy.context.object
    obj.rotation_euler = direction.to_track_quat('Z', 'Y').to_euler()
    return finish(obj, name, mat, 0.007)

rod('Central telescoping column', (0, 0, 1.18), (0, 0, 3.0), 0.072, alloy)
rod('Three-way leg hub', (0, 0, 2.27), (0, 0, 2.49), 0.24, black)
rod('Column locking collar', (0, 0, 2.49), (0, 0, 2.60), 0.13, black)
rod('Column lock screw', (0.08, 0, 2.55), (0.28, 0, 2.55), 0.035, alloy)
rod('Column lock knob', (0.24, 0, 2.55), (0.32, 0, 2.55), 0.078, orange)
rod('Lower spreader collar', (0, 0, 1.22), (0, 0, 1.34), 0.12, black)
for i in range(3):
    angle = math.radians(30 + 120 * i)
    radial = Vector((math.cos(angle), math.sin(angle), 0))
    top = radial * 0.18 + Vector((0, 0, 2.34))
    foot = radial * 1.20 + Vector((0, 0, 0.10))
    def along(t):
        return top.lerp(foot, t)
    prefix = 'Leg %d ' % (i + 1)
    rod(prefix + 'upper tube', along(0), along(0.56), 0.071, black)
    rod(prefix + 'telescoping lower tube', along(0.50), along(0.99), 0.049, alloy)
    rod(prefix + 'foam hand grip', along(0.10), along(0.32), 0.083, rubber)
    rod(prefix + 'extension clamp', along(0.51), along(0.57), 0.09, black)
    latch = box(prefix + 'orange clamp lever', along(0.54) + radial * 0.085,
                (0.06, 0.16, 0.14), orange, 0.015)
    latch.rotation_euler.z = angle
    rod(prefix + 'rubber foot', along(0.94), foot, 0.076, rubber, 0.095)
    rod(prefix + 'spreader brace', radial * 0.08 + Vector((0, 0, 1.28)),
        along(0.62), 0.024, alloy)
    tangent = Vector((-radial.y, radial.x, 0))
    rod(prefix + 'hinge axle', top - tangent * 0.115, top + tangent * 0.115, 0.045, alloy)

rod('Head rotating base', (0, 0, 2.93), (0, 0, 3.05), 0.18, black)
rod('Orange pan index ring', (0, 0, 3.025), (0, 0, 3.055), 0.184, orange)
box('Tilt head housing', (0, 0, 3.16), (0.28, 0.25, 0.24), black)
rod('Tilt pivot', (-0.22, 0, 3.17), (0.22, 0, 3.17), 0.085, alloy)
rod('Tilt lock dial', (-0.25, 0, 3.17), (-0.20, 0, 3.17), 0.115, black)
box('Quick release mounting plate', (0, 0, 3.32), (0.42, 0.34, 0.065), alloy, 0.012)
box('Plate rubber pad', (0, 0, 3.36), (0.36, 0.28, 0.018), rubber, 0.006)
rod('Camera mounting screw', (0, 0, 3.36), (0, 0, 3.40), 0.026, alloy)
rod('Pan handle shaft', (0, 0.08, 3.13), (0.28, 0.73, 2.89), 0.025, alloy)
rod('Pan handle grip', (0.28, 0.73, 2.89), (0.39, 0.99, 2.79), 0.055, rubber)
box('Floor', (0, 0, -0.065), (200, 200, 0.10), ground, 0)

bpy.ops.object.camera_add(location=(5.0, -7.0, 4.4))
camera = bpy.context.object
camera.name = 'Tripod overview camera'
camera.rotation_euler = (Vector((0, 0, 1.72)) - camera.location).to_track_quat('-Z', 'Y').to_euler()
camera.data.type = 'ORTHO'
camera.data.ortho_scale = 4.5
bpy.context.scene.camera = camera
for name, loc, power, size in [('Key softbox', (3, -4, 6), 1000, 4), ('Rim softbox', (-3, 2, 5), 850, 3)]:
    bpy.ops.object.light_add(type='AREA', location=loc)
    light = bpy.context.object
    light.name = name
    light.data.energy = power
    light.data.shape = 'DISK'
    light.data.size = size
    light.rotation_euler = (Vector((0, 0, 1.6)) - light.location).to_track_quat('-Z', 'Y').to_euler()
bpy.context.scene.world.color = (0.22, 0.22, 0.22)
bpy.context.scene.render.resolution_x = 900
bpy.context.scene.render.resolution_y = 1000
bpy.context.scene.render.resolution_percentage = 100
